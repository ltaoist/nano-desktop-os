# 系统服务

## 认证（auth.py）

认证采用极简的单用户模型，适合本地桌面场景：

- 凭据以明文 JSON 存储在 `Data/System/auth.json`，格式 `{"username": "...", "password": "..."}`
- 首次运行时文件不存在，默认账号 `admin`/`admin`
- `verify_login()` 做明文字符串比较，无哈希、无盐值、无 Session/Token
- `check_auth_header()` 解析 HTTP Basic Auth，但当前版本**未在任何路由中实际使用**——API 接口没有认证中间件保护

前端登录流程：用户输入凭据 → `POST /api/auth/login` → 验证成功后前端设 `loggedIn = true` → 建立 SSE 连接。认证是纯前端状态控制，后端 API 本身是开放的。这对于本地应用足够，如需网络部署应添加认证中间件。

## SSE 事件总线（sse_bus.py）

SSE（Server-Sent Events）是后端向前端 SPA 单向推送状态变更的机制，解决"前端如何知道线程/应用列表变化了"的问题。

**为什么用 SSE 而非 WebSocket**：系统已有 TOB WebSocket 用于应用前后端通信，但系统级 UI 更新（线程列表、应用列表、通知）是单向的服务端→客户端推送，SSE 比 WebSocket 更简单——基于 HTTP、自动重连、无需心跳协议。

**SSEBus 实现**：
- 每个客户端连接时 `subscribe()` 创建一个 `asyncio.Queue`，加入 `_queues` 列表
- `publish(event, data)` 遍历所有队列 `put_nowait()` 消息，格式为 `event: xxx\ndata: {...}\n\n`
- 队列满（慢客户端）的连接被标记为 stale 并 `unsubscribe()` 清理
- SSE 端点 (`/api/events`) 先发送三类全量数据（threads、apps、notifications），然后进入循环等待队列消息
- 15 秒无消息则发送 `: keepalive\n\n`（SSE 注释帧）防止代理超时断开连接

**全量广播模式**：每次状态变更后广播完整列表而非增量差异。前端直接替换数组，无需合并逻辑。这对于桌面应用的数据规模（线程数通常不超过几十个）完全足够，且避免了增量同步的复杂性。

**三类事件**：

| 事件 | 触发时机 | 前端响应 |
|------|----------|----------|
| `threads` | 创建/删除/更新线程、状态刷新 | ThreadListPanel 重新渲染线程列表 |
| `apps` | 安装/卸载应用 | LauncherPanel 更新应用列表 |
| `notifications` | 删除/清空通知 | NotificationPanel 更新通知红点 |

注意：`notify_event()` 和 `notify_error()` 创建通知时**不自动触发 SSE 广播**——当前只有 REST API 路由中的显式 `_broadcast_notifications()` 调用才会推送。后台任务（如子进程）创建通知后前端不会立即看到，需要下次轮询或页面刷新。

## 通知总线（notification_bus.py）

通知持久化在 `Data/System/notifications.json`，以 JSON 数组存储，每条通知包含自增 ID、类型（`"event"`/`"error"`）、来源、消息内容、ISO 时间戳。通知是系统级的，不属于任何特定线程或应用。

## 前端架构要点

前端是 Vue 3 SPA，核心状态集中在 `App.vue`：
- `loggedIn`：登录状态
- `threads`：线程列表（从 SSE 全量更新）
- `apps`：应用列表（从 SSE 全量更新）
- `notifications`：通知列表（从 SSE 全量更新）
- `eventSource`：EventSource 实例
- `backendDown`：后端连接状态标志（收到任何 SSE 事件置 false，onerror 置 true）

**窗口模型**：每个线程窗口是一个 iframe，`WindowContent.vue` 根据应用类型设置 iframe src：
- app 类型：`/app-content/{app}/?thread_id={thread_id}`
- script 类型：`/html/scriptContentWindow.html?thread_id={thread_id}`

iframe 使用 `sandbox="allow-scripts allow-same-origin allow-forms"` 进行隔离，允许脚本执行、同源访问（TOB 通信需要）和表单提交，但禁止弹出窗口和顶层导航。

## 静态文件服务的目录映射

理解开发模式下的请求路由对调试很重要：

```
浏览器请求                    开发模式(5173)              后端直连(8000)
─────────────────────────────────────────────────────────────────────
/                           Vite (index.html)            无（需前端构建）
/api/*                      Vite 代理 → 8000            FastAPI 路由
/ws                         Vite 代理 → ws://8000/ws    TOB WebSocket
/api/events                 Vite 代理 → 8000            SSE 端点
/app-content/{app}/*        Vite 代理 → 8000            FastAPI 路由
/nano_tob.js                Vite public/ 直接提供        无（需前端构建）
/html/*                     Vite public/html/           无
```
