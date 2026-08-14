# 线程生命周期

线程管理器（`thread_manager.py`）负责将应用代码转化为运行中的进程，并维护进程与前端窗口的对应关系。

## 为什么用子进程

每个应用实例运行在独立的 Python 子进程中，而非线程或协程。这是关键设计决策：

- **隔离性**：一个应用崩溃不会影响其他应用或系统服务
- **独立性**：每个进程有独立的事件循环、内存空间、import 状态
- **干净终止**：关闭线程只需杀死进程，无需考虑资源清理
- **安全边界**：应用代码无法直接访问系统服务进程的内存

代价是进程启动开销和 TOB 通信的序列化/反序列化，但对于桌面应用场景，这些开销可忽略。

## 子进程启动机制

`start_thread_process()` 不直接执行 `python main.py`，而是用 `python -c` 执行一段内联代码：

```python
code = (
    f"import sys; sys.path.insert(0, r'{app_dir}'); "
    f"from {module_name} import __nanoAppMain; "
    f"import asyncio; asyncio.run(__nanoAppMain())"
)
subprocess.Popen([python, "-c", code], env={**os.environ, "THREAD_ID": thread_id})
```

这样做的原因：
1. **`sys.path.insert(0, app_dir)`** 将应用目录加入模块搜索路径，应用代码中的 `import` 语句可以引用同目录下的其他模块
2. **`from {module_name} import __nanoAppMain`** 按约定导入入口协程——入口函数必须叫 `__nanoAppMain`，这是应用与系统之间的唯一契约
3. **`asyncio.run()`** 启动事件循环运行入口协程
4. **`THREAD_ID` 环境变量**是子进程获取自身线程标识的唯一途径，TOB 客户端在初始化时从 `os.environ["THREAD_ID"]` 读取

应用约定总结：必须定义 `async def __nanoAppMain()`，无需关心路径和启动方式。

## THREAD_ID 的双向传播

THREAD_ID 是连接前后端的纽带，传播路径分两支：

**后端侧**：`subprocess.Popen` 的 `env` 参数注入 `THREAD_ID` 环境变量 → `nano_tob.py` 的 `_TOBNode.__init__` 从 `os.environ.get("THREAD_ID", "")` 读取 → 所有 TOB 消息携带此 ID。

**前端侧**：iframe 的 src 是 `/app-content/{app}/?thread_id=xxx` → `/app-content/{app}/` 路由读取 index.html，在 `</head>` 前注入 `<script>window.THREAD_ID="{thread_id}"</script>` → 页面加载后 `nano_tob.js` 的 `getThreadId()` 从 `window.location.search` 的 URL 参数中读取（作为后备，也检查 `window.THREAD_ID`） → 所有 TOB 消息携带此 ID。

这样，同一个线程的前端连接和后端连接在 TOB 服务器看来拥有相同的 `thread_id`，从而能在同一个命名空间中互操作。

## 进程状态检测

`refresh_thread_statuses()` 在每次获取线程列表（`GET /api/threads`）和 SSE 广播前被调用，用于检测"已死亡但状态未更新"的进程：

```python
kernel32 = ctypes.windll.kernel32
handle = kernel32.OpenProcess(0x0400, False, pid)
if handle:
    kernel32.CloseHandle(handle)       # 进程存在，关闭句柄
else:
    tinfo["status"] = "dead"           # 进程不存在，标记为死亡
```

Windows 上用 `OpenProcess` 系统调用检测进程存活：传入 PID 尝试打开进程句柄，如果返回 NULL（句柄为 0）说明进程已退出。`0x0400` 是 `PROCESS_QUERY_INFORMATION` 权限，仅用于查询不需要完全访问。检测后立即调用 `CloseHandle` 避免句柄泄漏。

这个检测是必要的，因为子进程可能非正常退出（如崩溃、被任务管理器杀死），线程管理器不会收到通知。

## 进程终止

`kill_thread_process()` 的处理方式值得注意：

```python
proc.terminate()   # SIGTERM
proc.kill()        # SIGKILL
# 不调用 proc.wait()
```

先发送 terminate（SIGTERM，Windows 上是 TerminateProcess），再立即 kill。不调用 `proc.wait()` 的原因是代码注释中明确说明的：在 Windows 上 `proc.wait()` 可能永远阻塞 asyncio 事件循环。

这是一个务实的选择：桌面应用场景下，"快速杀死进程"比"优雅关闭"更重要。应用的 `__nanoAppMain` 应在 `finally` 块中做必要清理（如 `closeTOBM()`），但不应依赖 `CancelledError` 之外的关闭信号。

## 线程数据持久化

线程元数据（ID、应用名、标题、标签、状态、PID、创建时间）序列化为 JSON 存储在 `Data/System/threads.json`。这使得后端重启后能恢复线程列表（虽然进程本身不会自动重启，状态会被标记为 dead）。

线程历史数据（如对话历史）通过 `data_storage` 模块以特殊应用名 `"_system"` 存储在 `Data/AppDataStore/_system/thread_history/{thread_id}.json`，与应用数据使用同一套存储机制。
