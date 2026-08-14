# 最小系统开发

本章面向希望理解系统内部机制或进行深度定制的开发者，讲解 Nano Desktop OS 核心组件的设计原理与关键实现细节。

## 系统全景

Nano Desktop OS 的后端是一个 FastAPI 应用（`src/backend/main.py`），前端是 Vue 3 SPA（`src/frontend/`）。整个系统围绕一个核心运行模型工作：**每个应用实例是一个独立的 Python 子进程，通过 WebSocket 连接到 TOB 服务器，与浏览器中的前端页面双向通信**。

```
浏览器 (Vue SPA, port 5173/8000)
  ├── SSE (/api/events)       ← 线程/应用/通知列表实时更新
  ├── REST API (/api/*)       → 线程CRUD、应用管理、认证、数据存储
  └── iframe (/app-content/{app}/?thread_id=xxx)
        └── WebSocket (/ws)   ← TOB 双向通信（前端页面侧）

后端子进程 (python -c "...", 每个线程一个进程)
  └── WebSocket (/ws)         ← TOB 双向通信（后端进程侧）
        env: THREAD_ID=xxx
```

系统中有三类 HTTP 通信通道：
1. **REST API**：前端管理操作（创建/删除线程、安装应用、认证）
2. **SSE**：服务端向前端单向推送列表变更（全量广播）
3. **WebSocket `/ws`**：TOB 双向通信，前端 iframe 和后端子进程都连接到此端点

## 线程创建的完整链路

理解一个线程从点击图标到前后端连通的全过程，是理解整个系统的关键：

1. **前端发起**：用户点击应用图标，LauncherPanel 预生成 `thread_id`（nanoid 16位），发送 `POST /api/threads`
2. **后端创建记录**：`POST /api/threads` 路由调用 `app_manager.list_apps()` 找到应用，调用 `thread_manager.create_thread()` 写入 `Data/System/threads.json`
3. **启动子进程**：调用 `thread_manager.start_thread_process()`，用 `subprocess.Popen` 启动 Python 子进程：
   ```python
   code = f"import sys; sys.path.insert(0, r'{app_dir}'); " \
          f"from {module_name} import __nanoAppMain; " \
          f"import asyncio; asyncio.run(__nanoAppMain())"
   subprocess.Popen([sys.executable, "-c", code], env={**os.environ, "THREAD_ID": thread_id})
   ```
   注意这里用 `python -c` 内联代码而非直接执行文件——通过 `sys.path.insert(0, app_dir)` 将应用目录加入模块搜索路径，然后 import 应用的 `main` 模块并调用 `__nanoAppMain()`。这使应用代码无需关心自己在文件系统中的位置。
4. **SSE 广播**：路由调用 `_broadcast_threads()`，前端 ThreadListPanel 收到新线程列表，创建 ThreadWindow
5. **iframe 加载**：ThreadWindow 内嵌 iframe 指向 `/app-content/{app}/?thread_id=xxx`
6. **后端注入 THREAD_ID**：`/app-content/{app}/` 路由读取应用的 `index.html`，在 `</head>` 前注入 `<script>window.THREAD_ID="{thread_id}"</script>`，返回修改后的 HTML
7. **前端 TOB 连接**：页面中 `<script src="/nano_tob.js">` 加载 JS TOB 客户端，`nano_tob.js` 从 URL 参数 `thread_id` 读取线程 ID，连接 `/ws` WebSocket
8. **后端 TOB 连接**：子进程中 `__nanoAppMain()` 调用 `initializeTOBM()`，从环境变量 `THREAD_ID` 读取线程 ID，连接 `/ws` WebSocket
9. **TOB 命名发现**：后端 `createTOB()` + `nameTOB(tob, "app")`，前端 `waitNamedTOB("app")` 返回代理对象，双向通信建立

## ID 体系

系统中所有 ID 使用同一套 nanoid 算法生成（`secrets.choice` 从 `[A-Za-z0-9_-]` 中随机选取），保证 URL 安全且无需中心化发号：

| ID 类型 | 前缀 | 长度 | 生成位置 |
|---------|------|------|----------|
| 线程 ID | 无 | 16 位 | 前端预生成或后端 `thread_manager._nanoid(16)` |
| TOB ID | `Tob-` | 21 位随机串 | TOB 服务器 `_make_tob_id()` |
| 指令 ID | `Ins-` | 21 位随机串 | 各端 `_make_ins_id()`，用于请求-响应匹配 |

## 组件导航

- [TOB 服务器实现](/minimal/tob-server) — 内部数据结构、消息协议、调用路由与代理机制
- [线程生命周期](/minimal/thread-manager) — 子进程启动、THREAD_ID 传播、进程存活检测、优雅关闭
- [应用与数据](/minimal/app-filesystem) — 应用类型识别、index.html 注入、静态文件服务、数据存储
- [系统服务](/minimal/system-services) — 认证、通知、SSE 总线的实现细节
