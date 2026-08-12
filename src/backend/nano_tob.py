"""
nano_tob.py — Thread Object Broker 后端客户端
供后端节点使用的 TOB API。

使用前需先调用 initializeTOBM() 初始化 Thread Object Broker 机制。
线程 ID 通过环境变量 THREAD_ID 获取。
"""

import asyncio
import json
import os
import secrets
import string

import websockets


# ── nanoid 实现 ──────────────────────────────────────────────────────

def _nanoid(size=21):
    alphabet = string.ascii_letters + string.digits + "_-"
    return ''.join(secrets.choice(alphabet) for _ in range(size))


def _make_ins_id():
    return f"Ins-{_nanoid()}"


# ── TOB 对象 ─────────────────────────────────────────────────────────

class TOB:
    """TOB 本地代理对象"""
    def __init__(self, tob_id):
        self.id = tob_id
        self._methods = {}


# ── 客户端 ───────────────────────────────────────────────────────────

class _TOBNode:
    def __init__(self):
        self.ws = None
        self.thread_id = os.environ.get("THREAD_ID", "")
        self._pending = {}   # ins_id -> asyncio.Future
        self._tobs = {}      # tob_id -> TOB

    async def connect(self, url):
        self.ws = await websockets.connect(url)
        asyncio.create_task(self._listen())

    async def close(self):
        """关闭连接并清理本地状态"""
        self._tobs.clear()
        for future in self._pending.values():
            if not future.done():
                future.set_exception(RuntimeError("连接已关闭"))
        self._pending.clear()
        if self.ws is not None:
            try:
                await self.ws.close()
            except Exception:
                pass
            self.ws = None

    async def _listen(self):
        """持续监听服务器消息"""
        try:
            async for message in self.ws:
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    continue
                ins_type = data.get("type", "")
                ins_id = data.get("id", "")
                params = data.get("params", {})

                if ins_type == "callTOBMethod":
                    # 服务器要求我们执行本地方的方法
                    asyncio.create_task(self._handle_incoming_call(ins_id, params))
                else:
                    # 响应我们发出的请求
                    future = self._pending.pop(ins_id, None)
                    if future and not future.done():
                        future.set_result(params)
        except websockets.ConnectionClosed:
            pass

    async def _handle_incoming_call(self, ins_id, params):
        tob_id = params.get("tob_id", "")
        method = params.get("method", "")
        method_params = params.get("params", [])

        tob = self._tobs.get(tob_id)
        if not tob:
            await self._send_return(ins_id, error=f"TOB {tob_id} 在本地未找到")
            return

        delegate = tob._methods.get(method)
        if not delegate:
            await self._send_return(ins_id, error=f"TOB {tob_id} 上未挂载方法 '{method}'")
            return

        try:
            if asyncio.iscoroutinefunction(delegate):
                result = await delegate(*method_params)
            else:
                result = delegate(*method_params)
            await self._send_return(ins_id, result=result)
        except Exception as e:
            await self._send_return(ins_id, error=str(e))

    async def _send_return(self, ins_id, result=None, error=None):
        await self.ws.send(json.dumps({
            "thread_id": self.thread_id,
            "id": ins_id,
            "type": "callTOBMethodReturn",
            "params": {"result": result, "error": error}
        }, ensure_ascii=False))

    async def _request(self, msg_type, params):
        ins_id = _make_ins_id()
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self._pending[ins_id] = future

        await self.ws.send(json.dumps({
            "thread_id": self.thread_id,
            "id": ins_id,
            "type": msg_type,
            "params": params
        }, ensure_ascii=False))

        return await future


# ── 模块级单例 ────────────────────────────────────────────────────────

_client = None


async def initializeTOBM(url="ws://127.0.0.1:8000/ws"):
    """初始化 Thread Object Broker 机制。必须先调用此函数。"""
    global _client
    _client = _TOBNode()
    await _client.connect(url)


async def closeTOBM():
    """关闭 Thread Object Broker 机制。关闭后可通过 initializeTOBM 重新初始化。"""
    global _client
    if _client is not None:
        try:
            await _client.close()
        finally:
            _client = None


def _ensure_client():
    if _client is None:
        raise RuntimeError("Thread Object Broker 未初始化。请先调用 initializeTOBM(url)。")


# ── 公开 API ─────────────────────────────────────────────────────────

async def createTOB():
    """创建一个 TOB，返回 TOB 对象"""
    _ensure_client()
    result = await _client._request("createTOB", {})
    tob_id = result["tob_id"]
    tob = TOB(tob_id)
    _client._tobs[tob_id] = tob
    return tob


async def nameTOB(tob, name):
    """给 TOB 命名"""
    _ensure_client()
    result = await _client._request("nameTOB", {"tob_id": tob.id, "name": name})
    return result.get("success", False)


async def getTOB(tob_id):
    """通过 ID 获取 TOB，不存在返回 None"""
    _ensure_client()
    result = await _client._request("getTOB", {"tob_id": tob_id})
    if result.get("tob_id"):
        tid = result["tob_id"]
        tob = _client._tobs.get(tid)
        if tob is None:
            tob = TOB(tid)
            _client._tobs[tid] = tob
        return tob
    return None


async def waitTOB(tob_id, timeout=0):
    """
    等待指定 ID 的 TOB 被创建。
    timeout 为毫秒，0 表示无限等待。超时返回 None。
    """
    _ensure_client()
    result = await _client._request("waitTOB", {"tob_id": tob_id, "timeout": timeout})
    if result.get("tob_id"):
        tid = result["tob_id"]
        tob = _client._tobs.get(tid)
        if tob is None:
            tob = TOB(tid)
            _client._tobs[tid] = tob
        return tob
    return None


async def waitNamedTOB(name, timeout=0):
    """
    等待指定名称的 TOB 被创建。
    timeout 为毫秒，0 表示无限等待。超时返回 None。
    """
    _ensure_client()
    result = await _client._request("waitNamedTOB", {"name": name, "timeout": timeout})
    if result.get("tob_id"):
        tid = result["tob_id"]
        tob = _client._tobs.get(tid)
        if tob is None:
            tob = TOB(tid)
            _client._tobs[tid] = tob
        return tob
    return None


async def callTOBMethod(tob, method, params):
    """调用 TOB 上的远程方法"""
    _ensure_client()
    result = await _client._request("callTOBMethod", {
        "tob_id": tob.id,
        "method": method,
        "params": params
    })
    if result.get("error"):
        raise Exception(result["error"])
    return result.get("result")


def mountTOBMethod(tob, method, delegate):
    """
    在 TOB 上挂载本地方法。纯本地操作，不通知服务器。
    当服务器转发 callTOBMethod 到此节点时，会调用该方法。
    """
    tob._methods[method] = delegate


async def forgetTOB(tob_id):
    """删除指定 ID 的 TOB"""
    _ensure_client()
    result = await _client._request("forgetTOB", {"tob_id": tob_id})
    if result.get("success"):
        _client._tobs.pop(tob_id, None)
        return True
    return False
