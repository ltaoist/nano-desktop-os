# Thread Lifecycle

The thread manager (`thread_manager.py`) turns application code into a running process and maintains the correspondence between processes and frontend windows.

## Why subprocesses

Each application instance runs in an independent Python subprocess, rather than a thread or coroutine. This is a key design decision:

- **Isolation**: a crash in one app does not affect other apps or system services
- **Independence**: each process has its own event loop, memory space, and import state
- **Clean termination**: closing a thread only requires killing the process; no resource cleanup is needed
- **Security boundary**: app code cannot directly access the memory of the system service process

The cost is process startup overhead and TOB serialization/deserialization, but for a desktop scenario these costs are negligible.

## Subprocess startup mechanism

`start_thread_process()` does not run `python main.py` directly; it uses `python -c` to run a piece of inline code:

```python
code = (
    f"import sys; sys.path.insert(0, r'{app_dir}'); "
    f"from {module_name} import __nanoAppMain; "
    f"import asyncio; asyncio.run(__nanoAppMain())"
)
subprocess.Popen([python, "-c", code], env={**os.environ, "THREAD_ID": thread_id})
```

Reasons:

1. **`sys.path.insert(0, app_dir)`** adds the app directory to the module search path so `import` statements in app code can reference other modules in the same directory
2. **`from {module_name} import __nanoAppMain`** imports the entry coroutine by convention — the entry function must be named `__nanoAppMain`, which is the only contract between the app and the system
3. **`asyncio.run()`** starts the event loop to run the entry coroutine
4. **`THREAD_ID` environment variable** is the only way the subprocess learns its own thread identifier; the TOB client reads it from `os.environ["THREAD_ID"]` during initialization

App contract summary: must define `async def __nanoAppMain()`; no need to care about paths or startup.

## Bidirectional propagation of THREAD_ID

THREAD_ID is the link between frontend and backend, propagated along two branches:

**Backend side**: `subprocess.Popen`'s `env` parameter injects `THREAD_ID` → `nano_tob.py`'s `_TOBNode.__init__` reads it from `os.environ.get("THREAD_ID", "")` → all TOB messages carry this ID.

**Frontend side**: the iframe src is `/app-content/{app}/?thread_id=xxx` → the `/app-content/{app}/` route reads index.html and injects `<script>window.THREAD_ID="{thread_id}"</script>` before `</head>` → after the page loads, `nano_tob.js`'s `getThreadId()` reads it from the URL parameter in `window.location.search` (as a fallback it also checks `window.THREAD_ID`) → all TOB messages carry this ID.

Thus, the frontend and backend connections of the same thread have the same `thread_id` in the TOB server's view, so they can interoperate in the same namespace.

## Process liveness detection

`refresh_thread_statuses()` is called before each thread-list fetch (`GET /api/threads`) and each SSE broadcast to detect processes that have died but whose status has not been updated:

```python
kernel32 = ctypes.windll.kernel32
handle = kernel32.OpenProcess(0x0400, False, pid)
if handle:
    kernel32.CloseHandle(handle)       # process exists, close the handle
else:
    tinfo["status"] = "dead"           # process does not exist, mark as dead
```

On Windows, process liveness is checked with the `OpenProcess` system call: pass the PID to try to open a process handle; if NULL (handle 0) is returned, the process has exited. `0x0400` is the `PROCESS_QUERY_INFORMATION` permission, only needed for querying, not full access. After detection it immediately calls `CloseHandle` to avoid handle leaks.

This detection is necessary because a subprocess may exit abnormally (crash, killed in Task Manager) and the thread manager receives no notification.

## Process termination

`kill_thread_process()` is worth noting:

```python
proc.terminate()   # SIGTERM
proc.kill()        # SIGKILL
# does not call proc.wait()
```

It first sends terminate (SIGTERM; on Windows this is TerminateProcess), then immediately kills. It does not call `proc.wait()` for the reason stated explicitly in the code comment: on Windows `proc.wait()` may block the asyncio event loop forever.

This is a pragmatic choice: in a desktop scenario, "kill the process quickly" matters more than "graceful shutdown". An app's `__nanoAppMain` should do necessary cleanup in its `finally` block (such as `closeTOBM()`), but should not depend on any shutdown signal other than `CancelledError`.

## Thread data persistence

Thread metadata (ID, app name, title, label, status, PID, creation time) is serialized to JSON and stored in `Data/System/threads.json`. This lets the backend restore the thread list after a restart (although the processes themselves do not auto-restart and are marked as dead).

Thread history data (such as conversation history) is stored by the `data_storage` module under the special app name `"_system"` at `Data/AppDataStore/_system/thread_history/{thread_id}.json`, using the same storage mechanism as app data.
