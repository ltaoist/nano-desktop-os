# System Services

## Auth (auth.py)

Auth uses a minimal single-user model, suitable for a local desktop scenario:

- Credentials are stored as plaintext JSON in `Data/System/auth.json`, in the format `{"username": "...", "password": "..."}`
- On first run the file does not exist, and the default account is `admin`/`admin`
- `verify_login()` does a plaintext string comparison — no hashing, no salt, no session/token
- `check_auth_header()` parses HTTP Basic Auth, but in the current version it is **not actually used in any route** — API endpoints are not protected by auth middleware

Frontend login flow: user enters credentials → `POST /api/auth/login` → on success the frontend sets `loggedIn = true` → establishes an SSE connection. Auth is purely frontend state control; the backend API itself is open. This is sufficient for a local app, but an auth middleware should be added for network deployment.

## SSE event bus (sse_bus.py)

SSE (Server-Sent Events) is the mechanism for the backend to push state changes one-way to the frontend SPA, solving the problem of "how does the frontend know the thread/app list changed".

**Why SSE instead of WebSocket**: the system already has the TOB WebSocket for app frontend-backend communication, but system-level UI updates (thread list, app list, notifications) are one-way server→client pushes. SSE is simpler than WebSocket — HTTP-based, auto-reconnect, no heartbeat protocol needed.

**SSEBus implementation**:

- On connection, `subscribe()` creates an `asyncio.Queue` and adds it to the `_queues` list
- `publish(event, data)` iterates all queues and `put_nowait()` messages, formatted as `event: xxx\ndata: {...}\n\n`
- Connections whose queues are full (slow clients) are marked stale and cleaned up with `unsubscribe()`
- The SSE endpoint (`/api/events`) first sends three kinds of full data (threads, apps, notifications), then loops waiting for queue messages
- If there is no message for 15 seconds, it sends `: keepalive\n\n` (an SSE comment frame) to prevent proxies from timing out the connection

**Full-broadcast mode**: after every state change it broadcasts the complete list rather than incremental diffs. The frontend directly replaces the array with no merging logic. For desktop-scale data (thread counts typically no more than a few dozen) this is fully sufficient and avoids incremental-sync complexity.

**Three event kinds**:

| Event | Trigger | Frontend response |
|------|----------|----------|
| `threads` | create/delete/update thread, status refresh | ThreadListPanel re-renders the thread list |
| `apps` | install/uninstall app | LauncherPanel updates the app list |
| `notifications` | delete/clear notifications | NotificationPanel updates the notification badge |

Note: `notify_event()` and `notify_error()` do **not automatically trigger SSE broadcast** when creating a notification — currently only the explicit `_broadcast_notifications()` call in REST API routes pushes. Notifications created by background tasks (such as subprocesses) are not seen by the frontend immediately and require the next poll or a page refresh.

## Notification bus (notification_bus.py)

Notifications are persisted in `Data/System/notifications.json` as a JSON array; each notification contains an auto-increment ID, a type (`"event"`/`"error"`), a source, message content, and an ISO timestamp. Notifications are system-level and do not belong to any specific thread or app.

## Frontend architecture highlights

The frontend is a Vue 3 SPA; core state is centralized in `App.vue`:

- `loggedIn`: login state
- `threads`: thread list (full update from SSE)
- `apps`: app list (full update from SSE)
- `notifications`: notification list (full update from SSE)
- `eventSource`: the EventSource instance
- `backendDown`: backend connection status flag (set false on any SSE event, true on error)

**Window model**: each thread window is an iframe; `WindowContent.vue` sets the iframe src based on app type:

- app type: `/app-content/{app}/?thread_id={thread_id}`
- script type: `/html/scriptContentWindow.html?thread_id={thread_id}`

The iframe uses `sandbox="allow-scripts allow-same-origin allow-forms"` for isolation, allowing script execution, same-origin access (needed for TOB communication), and form submission, but blocking popups and top-level navigation.

## Static file serving directory mapping

Understanding request routing in development mode is important for debugging:

```
Browser request            Development (5173)         Backend direct (8000)
─────────────────────────────────────────────────────────────────────
/                           Vite (index.html)            none (needs frontend build)
/api/*                      Vite proxy → 8000            FastAPI routes
/ws                         Vite proxy → ws://8000/ws    TOB WebSocket
/api/events                 Vite proxy → 8000            SSE endpoint
/app-content/{app}/*        Vite proxy → 8000            FastAPI routes
/nano_tob.js                Vite public/ direct          none (needs frontend build)
/html/*                     Vite public/html/            none
```
