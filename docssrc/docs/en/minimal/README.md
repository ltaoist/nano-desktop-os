# Minimal System

This chapter is for developers who want to understand the system's internal mechanisms or do deep customization. It explains the design principles and key implementation details of Nano Desktop OS's core components.

## System overview

The Nano Desktop OS backend is a FastAPI application (`src/backend/main.py`), and the frontend is a Vue 3 SPA (`src/frontend/`). The whole system works around one core runtime model: **each application instance is an independent Python subprocess that connects to the TOB server over WebSocket and communicates bidirectionally with the frontend page in the browser**.

```
Browser (Vue SPA, port 5173/8000)
  ├── SSE (/api/events)       ← real-time thread/app/notification list updates
  ├── REST API (/api/*)       → thread CRUD, app management, auth, data storage
  └── iframe (/app-content/{app}/?thread_id=xxx)
        └── WebSocket (/ws)   ← TOB bidirectional communication (frontend page side)

Backend subprocess (python -c "...", one process per thread)
  └── WebSocket (/ws)         ← TOB bidirectional communication (backend process side)
        env: THREAD_ID=xxx
```

There are three kinds of HTTP communication channels:

1. **REST API**: frontend management operations (create/delete threads, install apps, auth)
2. **SSE**: server-to-frontend one-way push of list changes (full broadcast)
3. **WebSocket `/ws`**: TOB bidirectional communication; both the frontend iframe and backend subprocess connect to this endpoint

## The full thread creation chain

Understanding the whole process from clicking an icon to frontend-backend connectivity is key to understanding the system:

1. **Frontend initiates**: the user clicks an app icon; LauncherPanel pre-generates a `thread_id` (nanoid, 16 chars) and sends `POST /api/threads`
2. **Backend creates the record**: the `POST /api/threads` route calls `app_manager.list_apps()` to find the app and `thread_manager.create_thread()` to write `Data/System/threads.json`
3. **Starts the subprocess**: calls `thread_manager.start_thread_process()`, launching a Python subprocess with `subprocess.Popen`:
   ```python
   code = f"import sys; sys.path.insert(0, r'{app_dir}'); " \
          f"from {module_name} import __nanoAppMain; " \
          f"import asyncio; asyncio.run(__nanoAppMain())"
   subprocess.Popen([sys.executable, "-c", code], env={**os.environ, "THREAD_ID": thread_id})
   ```
   Note that this uses inline `python -c` code rather than executing a file directly — `sys.path.insert(0, app_dir)` adds the app directory to the module search path, then imports the app's `main` module and calls `__nanoAppMain()`. This lets app code be unaware of where it is on the filesystem.
4. **SSE broadcast**: the route calls `_broadcast_threads()`; the frontend ThreadListPanel receives the new thread list and creates a ThreadWindow
5. **iframe loads**: ThreadWindow embeds an iframe pointing to `/app-content/{app}/?thread_id=xxx`
6. **Backend injects THREAD_ID**: the `/app-content/{app}/` route reads the app's `index.html` and injects `<script>window.THREAD_ID="{thread_id}"</script>` before `</head>`, returning the modified HTML
7. **Frontend TOB connection**: the page's `<script src="/nano_tob.js">` loads the JS TOB client; `nano_tob.js` reads the thread ID from the `thread_id` URL parameter and connects to the `/ws` WebSocket
8. **Backend TOB connection**: in the subprocess, `__nanoAppMain()` calls `initializeTOBM()`, reads the thread ID from the `THREAD_ID` environment variable, and connects to the `/ws` WebSocket
9. **TOB naming and discovery**: the backend calls `createTOB()` + `nameTOB(tob, "app")`; the frontend's `waitNamedTOB("app")` returns a proxy object, and bidirectional communication is established

## ID system

All IDs in the system use the same nanoid algorithm (`secrets.choice` randomly selecting from `[A-Za-z0-9_-]`), guaranteeing URL safety without a centralized ID generator:

| ID type | Prefix | Length | Generated at |
|---------|------|------|----------|
| Thread ID | none | 16 chars | generated in the frontend or by the backend `thread_manager._nanoid(16)` |
| TOB ID | `Tob-` | 21 random chars | TOB server `_make_tob_id()` |
| Instruction ID | `Ins-` | 21 random chars | each end's `_make_ins_id()`, used for request-response matching |

## Component navigation

- [TOB Server Implementation](./tob-server) — internal data structures, message protocol, call routing and proxy mechanism
- [Thread Lifecycle](./thread-manager) — subprocess startup, THREAD_ID propagation, process liveness detection, graceful shutdown
- [Apps and Data](./app-filesystem) — app type detection, index.html injection, static file serving, data storage
- [System Services](./system-services) — auth, notifications, and the SSE bus implementation details
