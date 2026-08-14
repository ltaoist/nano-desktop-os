# TOB 服务器实现

TOB 服务器内嵌在 `main.py` 的 `TOBServer` 类中，挂载在 `/ws` WebSocket 端点。前端 iframe 和每个后端子进程都作为 WebSocket 客户端连接到这里，服务器在它们之间路由方法调用。

## 连接模型

TOB 服务器不区分"前端连接"和"后端连接"——所有连接都是平等的 WebSocket 客户端。服务器通过消息中的 `thread_id` 字段实现线程隔离。每条消息的统一格式：

```json
{
  "thread_id": "abc123...",
  "id": "Ins-xyz...",
  "type": "messageType",
  "params": { ... }
}
```

- `thread_id`：逻辑线程标识，服务器据此隔离不同线程的 TOB 命名空间
- `id`：指令 ID（Ins- 前缀），由请求方生成，用于将响应匹配回原请求
- `type`：消息类型，决定 `_dispatch` 路由到哪个处理函数
- `params`：消息参数，结构因 type 而异

连接建立后的第一条消息必须携带 `thread_id`（TOB 客户端在连接后首次发送请求时自动带上），服务器从第一条消息中提取 `thread_id` 并绑定到该连接。

## 五个核心数据结构

```python
self._tobs = {}          # tob_id → {"ws", "thread_id", "name"}
self._names = {}         # (thread_id, name) → tob_id
self._pending_calls = {} # proxy_id → (caller_ws, caller_tid, caller_ins_id)
self._tob_waiters = {}   # tob_id → [(ws, tid, ins_id)]
self._named_waiters = {} # (thread_id, name) → [(ws, tid, ins_id)]
```

**`_tobs`** 是 TOB 对象注册表。每个 TOB 对象归属于一个 WebSocket 连接（`ws` 字段），即该 TOB 的创建者/持有者。服务器不存储方法列表——`mountTOBMethod` 是纯本地操作，方法表存在各端的 `TOB._methods` 字典中，服务器不知道哪些方法被挂载了。

**`_names`** 实现按名称查找。键是 `(thread_id, name)` 元组而非单纯的 `name`，确保线程隔离——线程 A 的 `"app"` 和线程 B 的 `"app"` 不冲突。

**`_pending_calls`** 是路由表。当调用方发起 `callTOBMethod` 时，服务器生成一个新的 `proxy_id`（即 Ins- 前缀的新指令 ID），记录"谁发的、原始指令 ID 是什么"，然后用 `proxy_id` 作为 `id` 转发给目标方。目标方返回结果时携带这个 `proxy_id`，服务器查找 `_pending_calls` 找到原始调用方，再用原始指令 ID 回传结果。这使得调用方和被调用方互不感知对方的存在。

**`_tob_waiters`** 和 **`_named_waiters`** 是等待队列。`waitTOB`/`waitNamedTOB` 在目标 TOB 不存在时，将等待者加入队列；当 `createTOB`/`nameTOB` 发生时，服务器遍历队列通知等待者。超时机制通过 `asyncio.sleep(timeout/1000)` 实现——到期后从队列中移除等待者并发送 `null` 结果。

## 远程调用的完整路由过程

以"前端调用后端 calculate 方法"为例，消息流转如下：

```
前端 (JS)                          TOB 服务器                         后端 (Python)
   │                                  │                                   │
   │──callTOBMethod─────────────────→│                                   │
   │  id: Ins-A                       │                                   │
   │  params: {tob_id: Tob-X,         │                                   │
   │          method: "calculate",    │                                   │
   │          params: ["1+2"]}        │                                   │
   │                                  │  1. 生成 proxy_id = Ins-B         │
   │                                  │  2. _pending_calls[Ins-B] =       │
   │                                  │     (前端ws, tid, Ins-A)           │
   │                                  │──callTOBMethod─────────────────→│
   │                                  │  id: Ins-B                        │
   │                                  │  params: {tob_id: Tob-X,         │
   │                                  │          method: "calculate",    │
   │                                  │          params: ["1+2"]}        │
   │                                  │                                   │ 3. 查找 _methods["calculate"]
   │                                  │                                   │ 4. 执行函数，得到结果
   │                                  │←─callTOBMethodReturn────────────│
   │                                  │  id: Ins-B                        │
   │                                  │  params: {result: "3"}            │
   │                                  │                                   │
   │                                  │ 5. _pending_calls.pop(Ins-B)     │
   │                                  │    → (前端ws, tid, Ins-A)         │
   │←─callTOBMethodReturn────────────│                                   │
   │  id: Ins-A                       │                                   │
   │  params: {result: "3"}            │                                   │
```

关键点：
- 服务器为每次跨端调用生成新的指令 ID（proxy_id），隔离两端的指令命名空间
- 方法查找和执行完全在接收方本地进行，服务器只做转发不做方法校验
- 如果接收方的 TOB 不存在或未挂载该方法，接收方返回错误，服务器原样转发

## 连接清理

WebSocket 断开时（页面关闭、子进程退出），`_cleanup` 方法执行：
1. 遍历 `_tobs`，找出该连接持有的所有 TOB，删除并清除名称绑定
2. 遍历 `_pending_calls`，删除该连接作为调用方的待返回条目（被调用方的返回将无人接收，但不影响正确性）
3. 从两个等待队列中移除该连接的等待条目

注意：如果断开的是被调用方，调用方不会收到错误通知——它只会永远等待。应用层应通过超时处理这种情况。

## 心跳保活

服务器在 `handle` 方法中设置 30 秒接收超时：30 秒内没收到消息则发送一个空 JSON `{}` 作为心跳 ping。这防止 WebSocket 连接因长时间无数据被中间代理（如 Nginx）断开。Python 客户端（`nano_tob.py`）使用 `websockets` 库的默认心跳机制；JS 客户端依赖浏览器 WebSocket 实现。

## 两端客户端的对称设计

Python 客户端（`nano_tob.py`）和 JS 客户端（`nano_tob.js`）结构完全对称：
- 都有 `TOB` 类持有 `id` 和 `_methods` 字典
- 都有 `_TOBNode`/`TOBNode` 类管理 WebSocket 连接、`_pending` Future/Promise 映射、`_tobs` 本地缓存
- 都用 `_request()` 方法发送请求并创建 Future/Promise 等待响应
- 收到 `callTOBMethod` 消息时都查本地 `_methods` 字典执行方法，用 `callTOBMethodReturn` 返回结果
- 区别仅在于 Python 用 asyncio Future，JS 用 Promise；Python 用 `websockets` 库，JS 用浏览器原生 WebSocket
