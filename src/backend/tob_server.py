"""
TOB（Thread Object Broker）服务端
基于系统通信链路的分布式对象代理服务器

管理 TOB 的创建、命名、查找、等待、远程方法调用和销毁。
"""

import asyncio
import json
import secrets
import string

import websockets


def _nanoid(size=21):
    """生成类似 nanoid 的唯一标识符"""
    alphabet = string.ascii_letters + string.digits + "_-"
    return ''.join(secrets.choice(alphabet) for _ in range(size))


def _make_ins_id():
    return f"Ins-{_nanoid()}"


def _make_tob_id():
    return f"Tob-{_nanoid()}"


class TOBServer:
    def __init__(self, host="127.0.0.1", port=8765):
        self.host = host
        self.port = port
        # tob_id -> {"ws": ws, "thread_id": str, "name": str|None}
        self._tobs = {}
        # (thread_id, name) -> tob_id
        self._names = {}
        # proxy_id -> (caller_ws, caller_thread_id, caller_ins_id)
        self._pending_calls = {}
        # tob_id -> [(ws, thread_id, ins_id)]
        self._tob_waiters = {}
        # (thread_id, name) -> [(ws, thread_id, ins_id)]
        self._named_waiters = {}

    # ── 连接处理 ──────────────────────────────────────────────────────

    async def handle(self, websocket):
        """处理单个系统通信连接"""
        thread_id = None
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    continue
                if thread_id is None:
                    thread_id = data.get("thread_id", "")
                asyncio.create_task(self._dispatch(websocket, data, thread_id))
        finally:
            await self._cleanup_connection(websocket)

    async def _cleanup_connection(self, ws):
        """连接关闭时清理该连接关联的所有 TOB"""
        to_delete = [tid for tid, t in self._tobs.items() if t["ws"] is ws]
        for tid in to_delete:
            tob = self._tobs.pop(tid)
            if tob["name"]:
                self._names.pop((tob["thread_id"], tob["name"]), None)
        # 清理该连接作为调用方的待处理调用
        to_remove = [
            pid for pid, (caller_ws, _, _) in self._pending_calls.items()
            if caller_ws is ws
        ]
        for pid in to_remove:
            del self._pending_calls[pid]
        # 清理该连接的等待者
        for waiters in self._tob_waiters.values():
            waiters[:] = [w for w in waiters if w[0] is not ws]
        for waiters in self._named_waiters.values():
            waiters[:] = [w for w in waiters if w[0] is not ws]

    async def _dispatch(self, ws, data, thread_id):
        ins_type = data.get("type", "")
        ins_id = data.get("id", "")
        params = data.get("params", {})

        handler = {
            "createTOB": self._handle_create,
            "nameTOB": self._handle_name,
            "getTOB": self._handle_get,
            "waitTOB": self._handle_wait_tob,
            "waitNamedTOB": self._handle_wait_named,
            "callTOBMethod": self._handle_call_method,
            "callTOBMethodReturn": self._handle_call_return,
            "forgetTOB": self._handle_forget,
        }.get(ins_type)

        if handler:
            try:
                await handler(ws, thread_id, ins_id, params)
            except Exception as e:
                await self._send(ws, thread_id, ins_id, f"{ins_type}Return",
                                 {"error": str(e)})

    # ── 工具方法 ──────────────────────────────────────────────────────

    async def _send(self, ws, thread_id, ins_id, msg_type, params):
        await ws.send(json.dumps({
            "thread_id": thread_id,
            "id": ins_id,
            "type": msg_type,
            "params": params
        }, ensure_ascii=False))

    # ── createTOB ────────────────────────────────────────────────────

    async def _handle_create(self, ws, thread_id, ins_id, params):
        tob_id = _make_tob_id()
        self._tobs[tob_id] = {"ws": ws, "thread_id": thread_id, "name": None}
        await self._send(ws, thread_id, ins_id, "createTOBReturn",
                         {"tob_id": tob_id})
        # 通知等待该 TOB 的等待者（仅同线程）
        waiters = self._tob_waiters.pop(tob_id, [])
        for waiter_ws, waiter_tid, waiter_ins_id in waiters:
            if waiter_tid == thread_id:
                await self._send(waiter_ws, waiter_tid, waiter_ins_id,
                                 "waitTOBReturn", {"tob_id": tob_id})
            else:
                # 非同线程等待者放回等待队列
                self._tob_waiters.setdefault(tob_id, []).append(
                    (waiter_ws, waiter_tid, waiter_ins_id))

    # ── nameTOB ──────────────────────────────────────────────────────

    async def _handle_name(self, ws, thread_id, ins_id, params):
        tob_id = params.get("tob_id", "")
        name = params.get("name", "")
        tob = self._tobs.get(tob_id)
        if not tob:
            await self._send(ws, thread_id, ins_id, "nameTOBReturn",
                             {"error": "TOB 未找到"})
            return
        # 只能给本线程的 TOB 命名
        if tob["thread_id"] != thread_id:
            await self._send(ws, thread_id, ins_id, "nameTOBReturn",
                             {"error": "TOB 不属于此线程"})
            return
        # 移除旧名称
        if tob["name"]:
            old_key = (tob["thread_id"], tob["name"])
            self._names.pop(old_key, None)
        tob["name"] = name
        name_key = (thread_id, name)
        self._names[name_key] = tob_id
        await self._send(ws, thread_id, ins_id, "nameTOBReturn",
                         {"success": True})
        # 通知等待该名称的等待者（仅同线程）
        waiters = self._named_waiters.pop(name_key, [])
        for waiter_ws, waiter_tid, waiter_ins_id in waiters:
            await self._send(waiter_ws, waiter_tid, waiter_ins_id,
                             "waitNamedTOBReturn", {"tob_id": tob_id})

    # ── getTOB ───────────────────────────────────────────────────────

    async def _handle_get(self, ws, thread_id, ins_id, params):
        tob_id = params.get("tob_id", "")
        tob = self._tobs.get(tob_id)
        # 只搜索同一线程的 TOB
        if tob and tob["thread_id"] == thread_id:
            await self._send(ws, thread_id, ins_id, "getTOBReturn",
                             {"tob_id": tob_id})
        else:
            await self._send(ws, thread_id, ins_id, "getTOBReturn",
                             {"tob_id": None})

    # ── waitTOB ──────────────────────────────────────────────────────

    async def _handle_wait_tob(self, ws, thread_id, ins_id, params):
        tob_id = params.get("tob_id", "")
        timeout = params.get("timeout", 0)

        # 只搜索同一线程的 TOB
        tob = self._tobs.get(tob_id)
        if tob and tob["thread_id"] == thread_id:
            await self._send(ws, thread_id, ins_id, "waitTOBReturn",
                             {"tob_id": tob_id})
            return

        # 注册等待者
        entry = (ws, thread_id, ins_id)
        self._tob_waiters.setdefault(tob_id, []).append(entry)

        # 双重检查：可能在注册期间被创建（同线程）
        tob = self._tobs.get(tob_id)
        if tob and tob["thread_id"] == thread_id:
            waiters = self._tob_waiters.get(tob_id, [])
            if entry in waiters:
                waiters.remove(entry)
            await self._send(ws, thread_id, ins_id, "waitTOBReturn",
                             {"tob_id": tob_id})
            return

        # timeout == 0 表示无限等待
        if timeout > 0:
            await asyncio.sleep(timeout / 1000.0)
            waiters = self._tob_waiters.get(tob_id, [])
            if entry in waiters:
                waiters.remove(entry)
                await self._send(ws, thread_id, ins_id, "waitTOBReturn",
                                 {"tob_id": None})

    # ── waitNamedTOB ─────────────────────────────────────────────────

    async def _handle_wait_named(self, ws, thread_id, ins_id, params):
        name = params.get("name", "")
        timeout = params.get("timeout", 0)
        name_key = (thread_id, name)

        # 同线程命名 TOB 已存在，立即返回
        if name_key in self._names:
            await self._send(ws, thread_id, ins_id, "waitNamedTOBReturn",
                             {"tob_id": self._names[name_key]})
            return

        # 注册等待者
        entry = (ws, thread_id, ins_id)
        self._named_waiters.setdefault(name_key, []).append(entry)

        # 双重检查
        if name_key in self._names:
            waiters = self._named_waiters.get(name_key, [])
            if entry in waiters:
                waiters.remove(entry)
            await self._send(ws, thread_id, ins_id, "waitNamedTOBReturn",
                             {"tob_id": self._names[name_key]})
            return

        if timeout > 0:
            await asyncio.sleep(timeout / 1000.0)
            waiters = self._named_waiters.get(name_key, [])
            if entry in waiters:
                waiters.remove(entry)
                await self._send(ws, thread_id, ins_id, "waitNamedTOBReturn",
                                 {"tob_id": None})

    # ── callTOBMethod ────────────────────────────────────────────────

    async def _handle_call_method(self, ws, thread_id, ins_id, params):
        tob_id = params.get("tob_id", "")
        method = params.get("method", "")
        method_params = params.get("params", [])

        tob = self._tobs.get(tob_id)
        # 只搜索同一线程的 TOB
        if not tob or tob["thread_id"] != thread_id:
            await self._send(ws, thread_id, ins_id, "callTOBMethodReturn",
                             {"error": "TOB 未找到"})
            return

        # 生成代理指令 ID，转发给 TOB 所有者
        proxy_id = _make_ins_id()
        self._pending_calls[proxy_id] = (ws, thread_id, ins_id)

        await tob["ws"].send(json.dumps({
            "thread_id": tob["thread_id"],
            "id": proxy_id,
            "type": "callTOBMethod",
            "params": {
                "tob_id": tob_id,
                "method": method,
                "params": method_params
            }
        }, ensure_ascii=False))

    # ── callTOBMethodReturn ──────────────────────────────────────────

    async def _handle_call_return(self, ws, thread_id, ins_id, params):
        pending = self._pending_calls.pop(ins_id, None)
        if pending:
            caller_ws, caller_thread_id, caller_ins_id = pending
            await self._send(caller_ws, caller_thread_id, caller_ins_id,
                             "callTOBMethodReturn", {
                                 "result": params.get("result"),
                                 "error": params.get("error")
                             })

    # ── forgetTOB ────────────────────────────────────────────────────

    async def _handle_forget(self, ws, thread_id, ins_id, params):
        tob_id = params.get("tob_id", "")
        tob = self._tobs.get(tob_id)
        # 只能删除本线程的 TOB
        if not tob or tob["thread_id"] != thread_id:
            await self._send(ws, thread_id, ins_id, "forgetTOBReturn",
                             {"tob_id": None})
            return
        self._tobs.pop(tob_id)
        if tob["name"]:
            self._names.pop((tob["thread_id"], tob["name"]), None)
        await self._send(ws, thread_id, ins_id, "forgetTOBReturn",
                         {"success": True})

    # ── start ────────────────────────────────────────────────────────

    async def start(self):
        async with websockets.serve(self.handle, self.host, self.port):
            print(f"TOB Server 已启动 — 通信地址: {self.host}:{self.port}")
            await asyncio.Future()  # 永久运行


if __name__ == "__main__":
    server = TOBServer()
    asyncio.run(server.start())
