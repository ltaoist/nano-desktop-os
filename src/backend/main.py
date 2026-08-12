"""
Nano Desktop OS - 后端主服务
整合 TOB 通信链路、系统接口、静态资源服务
"""

import asyncio
import json
import os
import sys
import secrets
import string

# ── Windows 终端启用 ANSI 颜色 ─────────────────────────────────────────

if sys.platform == "win32":
    import ctypes
    kernel32 = ctypes.windll.kernel32
    # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
    # -11 = stdout, -12 = stderr，都启用 ANSI 支持
    for handle_id in (-11, -12):
        handle = kernel32.GetStdHandle(handle_id)
        mode = ctypes.c_uint32()
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from . import auth
from . import app_manager
from . import thread_manager
from . import data_storage
from . import notification_bus
from . import sse_bus

# ── 中文化 uvicorn 日志 ───────────────────────────────────────────────

import copy
from uvicorn.logging import DefaultFormatter as _UvDefaultFormatter
import uvicorn.config as _uv_config

class _NanoDefaultFormatter(_UvDefaultFormatter):
    """在 uvicorn DefaultFormatter 基础上将英文日志翻译为中文"""
    _MAP = {
        "Started server process": "服务进程已启动",
        "Waiting for application startup.": "正在等待应用启动...",
        "Application startup complete.": "应用启动完成。",
        "Uvicorn running on ": "服务已就绪，监听地址 ",
        "(Press CTRL+C to quit)": "（按 CTRL+C 退出）",
        "Shutting down": "正在关闭...",
        "Waiting for application shutdown.": "正在等待应用关闭...",
        "Application shutdown complete.": "应用已关闭。",
        "Finished server process": "服务进程已结束",
    }

    def format(self, record):
        # uvicorn access log 使用位置参数传递，需要提取为命名属性
        if record.name == "uvicorn.access" and record.args:
            args = record.args
            if len(args) >= 5:
                record.__dict__.setdefault("client_addr", str(args[0]))
                record.__dict__.setdefault("request_line", f"{args[1]} {args[2]} HTTP/{args[3]}")
                record.__dict__.setdefault("status_code", str(args[4]))
        result = super().format(record)
        for en, zh in self._MAP.items():
            result = result.replace(en, zh)
        return result

_CHINESE_LOG_CONFIG = copy.deepcopy(_uv_config.LOGGING_CONFIG)
_CHINESE_LOG_CONFIG["formatters"]["default"] = {
    "()": "src.backend.main._NanoDefaultFormatter",
    "fmt": "%(levelprefix)s %(message)s",
    "use_colors": None,
}
_CHINESE_LOG_CONFIG["formatters"]["access"] = {
    "()": "src.backend.main._NanoDefaultFormatter",
    "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
    "use_colors": None,
}

app = FastAPI(title="Nano Desktop OS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── nanoid ────────────────────────────────────────────────────────────

def _nanoid(size=21):
    alphabet = string.ascii_letters + string.digits + "_-"
    return ''.join(secrets.choice(alphabet) for _ in range(size))


def _make_ins_id():
    return f"Ins-{_nanoid()}"


def _make_tob_id():
    return f"Tob-{_nanoid()}"


# ── TOB 服务端（内嵌）─────────────────────────────────────────────────

class TOBServer:
    def __init__(self):
        self._tobs = {}          # tob_id -> {"ws": ws, "thread_id": str, "name": str|None}
        self._names = {}         # (thread_id, name) -> tob_id
        self._pending_calls = {} # proxy_id -> (caller_ws, caller_thread_id, caller_ins_id)
        self._tob_waiters = {}   # tob_id -> [(ws, thread_id, ins_id)]
        self._named_waiters = {} # (thread_id, name) -> [(ws, thread_id, ins_id)]

    async def handle(self, websocket: WebSocket):
        await websocket.accept()
        thread_id = None
        try:
            while True:
                try:
                    raw = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                except asyncio.TimeoutError:
                    try:
                        await websocket.send_json({})
                    except Exception:
                        break
                    continue
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if thread_id is None:
                    thread_id = data.get("thread_id", "")
                asyncio.create_task(self._dispatch(websocket, data, thread_id))
        except (WebSocketDisconnect, Exception):
            pass
        finally:
            await self._cleanup(websocket)

    async def _cleanup(self, ws):
        """清理连接的所有 TOB 和等待条目"""
        to_delete = [tid for tid, t in self._tobs.items() if t["ws"] is ws]
        for tid in to_delete:
            tob = self._tobs.pop(tid)
            name = tob.get("name")
            tid_str = tob.get("thread_id", "?")
            if name:
                self._names.pop((tid_str, name), None)
            print(f"[TOB] 清理 TOB {tid} (name={name}, thread={tid_str})")
        if to_delete:
            print(f"[TOB] 连接断开，清理了 {len(to_delete)} 个 TOB")
        to_remove = [
            pid for pid, (cws, _, _) in self._pending_calls.items()
            if cws is ws
        ]
        for pid in to_remove:
            del self._pending_calls[pid]
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
                await self._send(ws, thread_id, ins_id, f"{ins_type}Return", {"error": str(e)})

    async def _send(self, ws, thread_id, ins_id, msg_type, params):
        try:
            await ws.send_text(json.dumps({
                "thread_id": thread_id,
                "id": ins_id,
                "type": msg_type,
                "params": params
            }, ensure_ascii=False))
        except Exception:
            pass

    async def _handle_create(self, ws, thread_id, ins_id, params):
        tob_id = _make_tob_id()
        self._tobs[tob_id] = {"ws": ws, "thread_id": thread_id, "name": None}
        await self._send(ws, thread_id, ins_id, "createTOBReturn", {"tob_id": tob_id})
        waiters = self._tob_waiters.pop(tob_id, [])
        for waiter_ws, waiter_tid, waiter_ins_id in waiters:
            if waiter_tid == thread_id:
                await self._send(waiter_ws, waiter_tid, waiter_ins_id, "waitTOBReturn", {"tob_id": tob_id})
            else:
                self._tob_waiters.setdefault(tob_id, []).append((waiter_ws, waiter_tid, waiter_ins_id))

    async def _handle_name(self, ws, thread_id, ins_id, params):
        tob_id = params.get("tob_id", "")
        name = params.get("name", "")
        tob = self._tobs.get(tob_id)
        if not tob:
            await self._send(ws, thread_id, ins_id, "nameTOBReturn", {"error": "TOB 未找到"})
            return
        if tob["thread_id"] != thread_id:
            await self._send(ws, thread_id, ins_id, "nameTOBReturn", {"error": "TOB 不属于此线程"})
            return
        if tob["name"]:
            old_key = (tob["thread_id"], tob["name"])
            self._names.pop(old_key, None)
        tob["name"] = name
        name_key = (thread_id, name)
        self._names[name_key] = tob_id
        await self._send(ws, thread_id, ins_id, "nameTOBReturn", {"success": True})
        waiters = self._named_waiters.pop(name_key, [])
        for waiter_ws, waiter_tid, waiter_ins_id in waiters:
            await self._send(waiter_ws, waiter_tid, waiter_ins_id, "waitNamedTOBReturn", {"tob_id": tob_id})

    async def _handle_get(self, ws, thread_id, ins_id, params):
        tob_id = params.get("tob_id", "")
        tob = self._tobs.get(tob_id)
        if tob and tob["thread_id"] == thread_id:
            await self._send(ws, thread_id, ins_id, "getTOBReturn", {"tob_id": tob_id})
        else:
            await self._send(ws, thread_id, ins_id, "getTOBReturn", {"tob_id": None})

    async def _handle_wait_tob(self, ws, thread_id, ins_id, params):
        tob_id = params.get("tob_id", "")
        timeout = params.get("timeout", 0)
        tob = self._tobs.get(tob_id)
        if tob and tob["thread_id"] == thread_id:
            await self._send(ws, thread_id, ins_id, "waitTOBReturn", {"tob_id": tob_id})
            return
        entry = (ws, thread_id, ins_id)
        self._tob_waiters.setdefault(tob_id, []).append(entry)
        tob = self._tobs.get(tob_id)
        if tob and tob["thread_id"] == thread_id:
            waiters = self._tob_waiters.get(tob_id, [])
            if entry in waiters:
                waiters.remove(entry)
            await self._send(ws, thread_id, ins_id, "waitTOBReturn", {"tob_id": tob_id})
            return
        if timeout > 0:
            await asyncio.sleep(timeout / 1000.0)
            waiters = self._tob_waiters.get(tob_id, [])
            if entry in waiters:
                waiters.remove(entry)
                await self._send(ws, thread_id, ins_id, "waitTOBReturn", {"tob_id": None})

    async def _handle_wait_named(self, ws, thread_id, ins_id, params):
        name = params.get("name", "")
        timeout = params.get("timeout", 0)
        name_key = (thread_id, name)
        if name_key in self._names:
            await self._send(ws, thread_id, ins_id, "waitNamedTOBReturn", {"tob_id": self._names[name_key]})
            return
        entry = (ws, thread_id, ins_id)
        self._named_waiters.setdefault(name_key, []).append(entry)
        if name_key in self._names:
            waiters = self._named_waiters.get(name_key, [])
            if entry in waiters:
                waiters.remove(entry)
            await self._send(ws, thread_id, ins_id, "waitNamedTOBReturn", {"tob_id": self._names[name_key]})
            return
        if timeout > 0:
            await asyncio.sleep(timeout / 1000.0)
            waiters = self._named_waiters.get(name_key, [])
            if entry in waiters:
                waiters.remove(entry)
                await self._send(ws, thread_id, ins_id, "waitNamedTOBReturn", {"tob_id": None})

    async def _handle_call_method(self, ws, thread_id, ins_id, params):
        tob_id = params.get("tob_id", "")
        method = params.get("method", "")
        method_params = params.get("params", [])
        tob = self._tobs.get(tob_id)
        if not tob or tob["thread_id"] != thread_id:
            await self._send(ws, thread_id, ins_id, "callTOBMethodReturn", {"error": "TOB 未找到"})
            return
        proxy_id = _make_ins_id()
        self._pending_calls[proxy_id] = (ws, thread_id, ins_id)
        owner_ws = tob["ws"]
        try:
            await owner_ws.send_text(json.dumps({
                "thread_id": tob["thread_id"],
                "id": proxy_id,
                "type": "callTOBMethod",
                "params": {
                    "tob_id": tob_id,
                    "method": method,
                    "params": method_params
                }
            }, ensure_ascii=False))
        except Exception:
            self._pending_calls.pop(proxy_id, None)
            print(f"[TOB] callTOBMethod 失败: TOB {tob_id} 所有者不可达，清理连接")
            await self._cleanup(owner_ws)
            await self._send(ws, thread_id, ins_id, "callTOBMethodReturn", {"error": "TOB 所有者不可达"})

    async def _handle_call_return(self, ws, thread_id, ins_id, params):
        pending = self._pending_calls.pop(ins_id, None)
        if pending:
            caller_ws, caller_thread_id, caller_ins_id = pending
            await self._send(caller_ws, caller_thread_id, caller_ins_id, "callTOBMethodReturn", {
                "result": params.get("result"),
                "error": params.get("error")
            })

    async def _handle_forget(self, ws, thread_id, ins_id, params):
        tob_id = params.get("tob_id", "")
        tob = self._tobs.get(tob_id)
        if not tob or tob["thread_id"] != thread_id:
            await self._send(ws, thread_id, ins_id, "forgetTOBReturn", {"tob_id": None})
            return
        self._tobs.pop(tob_id)
        if tob["name"]:
            self._names.pop((tob["thread_id"], tob["name"]), None)
        await self._send(ws, thread_id, ins_id, "forgetTOBReturn", {"success": True})


tob_server = TOBServer()


# ── TOB 通信端点 ──────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await tob_server.handle(websocket)


# ── 认证 API ──────────────────────────────────────────────────────────

@app.post("/api/auth/login")
async def login(data: dict):
    username = data.get("username", "")
    password = data.get("password", "")
    if auth.verify_login(username, password):
        return {"success": True, "username": username}
    return JSONResponse({"success": False, "error": "用户名或密码错误"}, status_code=401)


@app.post("/api/auth/credentials")
async def update_credentials(data: dict):
    username = data.get("username", "")
    password = data.get("password", "")
    if username and password:
        auth.update_credentials(username, password)
        return {"success": True}
    return JSONResponse({"success": False, "error": "无效的凭据"}, status_code=400)


# ── 应用管理 API ──────────────────────────────────────────────────────

@app.get("/api/apps")
async def list_apps():
    return {"apps": app_manager.list_apps()}


@app.post("/api/apps/install")
async def install_app(data: dict):
    source = data.get("source", "")
    force = data.get("force", False)
    if not source:
        return JSONResponse({"success": False, "error": "缺少源路径"}, status_code=400)
    if force:
        result = app_manager.force_install_app(source)
    else:
        result = app_manager.install_app(source)
    if result.get("success"):
        print(f"[App] 安装成功: {result.get('name', '')}")
        _broadcast_apps()
    return result


@app.delete("/api/apps/{app_name}")
async def uninstall_app(app_name: str):
    result = app_manager.uninstall_app(app_name)
    if result.get("success"):
        print(f"[App] 卸载: {app_name}")
        _broadcast_apps()
    return result


# ── 线程管理 API ──────────────────────────────────────────────────────

@app.get("/api/threads")
async def list_threads():
    thread_manager.refresh_thread_statuses()
    return {"threads": thread_manager.list_threads()}


@app.post("/api/threads")
async def create_thread(data: dict):
    app_name = data.get("app_name", "")
    thread_id = data.get("thread_id", None)  # 前端可指定线程 ID
    if not app_name:
        return JSONResponse({"success": False, "error": "缺少应用名称"}, status_code=400)

    apps = app_manager.list_apps()
    target_app = None
    for a in apps:
        if a["name"] == app_name:
            target_app = a
            break

    if not target_app:
        return JSONResponse({"success": False, "error": f"应用 '{app_name}' 未安装"}, status_code=404)

    thread_id = thread_manager.create_thread(app_name, target_app["executive"], target_app["type"],
                                              thread_id=thread_id, display_name=target_app.get("display_name"))
    pid = thread_manager.start_thread_process(thread_id, target_app["executive"])
    _broadcast_threads()
    return {"success": True, "thread_id": thread_id, "pid": pid}


@app.put("/api/threads/{thread_id}/title")
async def update_thread_title(thread_id: str, data: dict):
    title = data.get("title", "")
    thread_manager.update_thread_title(thread_id, title)
    _broadcast_threads()
    return {"success": True}


@app.put("/api/threads/{thread_id}/label")
async def update_thread_label(thread_id: str, data: dict):
    label = data.get("label", "")
    thread_manager.update_thread_label(thread_id, label)
    _broadcast_threads()
    return {"success": True}


@app.put("/api/threads/{thread_id}/status")
async def update_thread_status(thread_id: str, data: dict):
    status = data.get("status", "")
    thread_manager.update_thread_status(thread_id, status)
    _broadcast_threads()
    return {"success": True}


@app.delete("/api/threads/{thread_id}")
async def delete_thread(thread_id: str):
    thread_manager.delete_thread(thread_id)
    _broadcast_threads()
    return {"success": True}


@app.get("/api/threads/{thread_id}/history")
async def get_thread_history(thread_id: str):
    history = thread_manager.get_thread_history(thread_id)
    return {"history": history}


# ── 数据存储 API ──────────────────────────────────────────────────────

@app.get("/api/storage/{app_name}/path")
async def list_path_entries(app_name: str, path: str = ""):
    entries = data_storage.listAppPathEntries(app_name, path)
    return {"entries": entries}


@app.get("/api/storage/{app_name}/path/data")
async def get_path_data(app_name: str, path: str):
    data = data_storage.getAppPathData(app_name, path)
    return {"data": data}


@app.put("/api/storage/{app_name}/path/data")
async def set_path_data(app_name: str, path: str, value: dict):
    data = value.get("data", "")
    data_storage.setAppPathData(app_name, path, data)
    return {"success": True}


@app.delete("/api/storage/{app_name}/path/data")
async def delete_path_data(app_name: str, path: str):
    data_storage.deleteAppPathData(app_name, path)
    return {"success": True}


@app.delete("/api/storage/{app_name}")
async def delete_app_store(app_name: str):
    data_storage.deleteAppDataStore(app_name)
    return {"success": True}


# ── 通知 API ──────────────────────────────────────────────────────────

@app.get("/api/notifications")
async def get_notifications():
    return {"notifications": notification_bus.get_notifications()}


@app.delete("/api/notifications/{notif_id}")
async def delete_notification(notif_id: int):
    notification_bus.delete_notification(notif_id)
    _broadcast_notifications()
    return {"success": True}


@app.delete("/api/notifications")
async def clear_notifications():
    notification_bus.clear_notifications()
    _broadcast_notifications()
    return {"success": True}


# ── App 静态内容服务 ──────────────────────────────────────────────────

@app.get("/app-content/{app_name}")
async def serve_app_index(app_name: str, thread_id: str = ""):
    """重定向到 /app-content/{app_name}/ 确保相对路径正确"""
    qs = f"?thread_id={thread_id}" if thread_id else ""
    return RedirectResponse(f"/app-content/{app_name}/{qs}")


@app.get("/app-content/{app_name}/")
async def serve_app_content(app_name: str, thread_id: str = ""):
    """为 App 类型应用提供 index.html"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Data")
    app_dir = os.path.join(data_dir, "AppData", app_name)
    index_html = os.path.join(app_dir, "index.html")

    if not os.path.isdir(app_dir):
        return JSONResponse({"error": "App not found"}, status_code=404)

    if os.path.isfile(index_html):
        with open(index_html, "r", encoding="utf-8") as f:
            html = f.read()
        html = html.replace("</head>", f'<script>window.THREAD_ID="{thread_id}";</script>\n</head>')
        return HTMLResponse(html)

    return JSONResponse({"error": "No index.html"}, status_code=404)


@app.get("/app-content/{app_name}/{path:path}")
async def serve_app_static(app_name: str, path: str):
    """为 App 类型应用提供静态文件 (js/css/img 等)"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Data")
    file_path = os.path.join(data_dir, "AppData", app_name, "static", path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return JSONResponse({"error": "File not found"}, status_code=404)


# ── SSE 广播辅助 ──────────────────────────────────────────────────────

def _broadcast_threads():
    thread_manager.refresh_thread_statuses()
    sse_bus.sse_bus.publish("threads", {"threads": thread_manager.list_threads()})

def _broadcast_apps():
    sse_bus.sse_bus.publish("apps", {"apps": app_manager.list_apps()})

def _broadcast_notifications():
    sse_bus.sse_bus.publish("notifications", {"notifications": notification_bus.get_notifications()})


# ── SSE 事件推送 ──────────────────────────────────────────────────────

@app.get("/api/events")
async def sse_events(request: Request):
    """SSE 端点：推送 threads / apps / notifications 变更事件"""
    async def event_stream():
        q = sse_bus.sse_bus.subscribe()
        try:
            # 发送初始数据
            thread_manager.refresh_thread_statuses()
            threads = thread_manager.list_threads()
            apps = app_manager.list_apps()
            notifications = notification_bus.get_notifications()
            import json as _json
            yield f"event: threads\ndata: {_json.dumps({'threads': threads}, ensure_ascii=False)}\n\n"
            yield f"event: apps\ndata: {_json.dumps({'apps': apps}, ensure_ascii=False)}\n\n"
            yield f"event: notifications\ndata: {_json.dumps({'notifications': notifications}, ensure_ascii=False)}\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    data = await asyncio.wait_for(q.get(), timeout=15)
                    yield data
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            sse_bus.sse_bus.unsubscribe(q)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ── 健康检查 ──────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok"}


# ── 启动 ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_config=_CHINESE_LOG_CONFIG)
