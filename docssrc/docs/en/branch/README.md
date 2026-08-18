# Branch Development

This chapter is for developers who need to modify the system source or do custom development. It introduces the project structure, dev environment setup, and the Fork workflow.

## Project structure

```
Nano Desktop/
├── src/
│   ├── backend/          # Python backend (FastAPI + uvicorn)
│   │   ├── main.py       # server entry: HTTP API, WebSocket, SSE, static files
│   │   ├── launch.py     # one-click startup: launches backend + frontend dev server
│   │   ├── tob_server.py # TOB WebSocket service (reserved for standalone deployment; core logic embedded in main.py)
│   │   ├── thread_manager.py  # thread lifecycle management (create/start/delete/history)
│   │   ├── app_manager.py     # app scanning/install/uninstall, app index maintenance
│   │   ├── auth.py            # single-user auth, credentials in Data/System/auth.json
│   │   ├── data_storage.py    # app private file storage + cross-process file lock
│   │   ├── nano_tob.py        # Python TOB client
│   │   ├── notification_bus.py # system notification persistence and query
│   │   └── sse_bus.py         # SSE event push (thread/app/notification changes)
│   └── frontend/         # Vue 3 frontend (built with Vite)
│       ├── public/
│       │   ├── nano_tob.js          # JS TOB client (app frontends include this script)
│       │   ├── nano_script_app.js   # runtime for .py script apps
│       │   └── html/scriptContentWindow.html
│       └── src/
│           ├── main.js
│           ├── App.vue              # desktop root layout
│           └── components/
│               ├── LoginModal.vue
│               ├── LauncherPanel.vue        # launcher
│               ├── AppInstallerPanel.vue    # installer
│               ├── ThreadListPanel.vue      # thread sidebar
│               ├── ThreadWindow.vue         # thread window
│               ├── WindowContent.vue        # iframe content area
│               ├── WindowTitleBar.vue
│               └── NotificationPanel.vue
├── Data/
│   ├── AppData/          # app install directory (calc.App, snake.App, etc.)
│   └── System/           # system data (auth.json, apps_index.json)
├── docssrc/              # docs source (VuePress 2)
└── requirements.txt      # Python dependencies: fastapi, uvicorn, websockets
```

**Key backend routes** (`main.py`):

| Route | Purpose |
|------|------|
| `WebSocket /ws` | TOB communication endpoint |
| `SSE /api/events` | server-side event push |
| `POST /api/auth/login` | login authentication |
| `GET/POST /api/apps` | list and install apps |
| `DELETE /api/apps/{name}` | uninstall an app |
| `GET/POST /api/threads` | list and create threads |
| `DELETE /api/threads/{id}` | delete a thread |
| `PUT /api/threads/{id}/title|label|status` | modify thread attributes |
| `/app-content/{app_name}/*` | app frontend static resources |
| `/nano_tob.js` | TOB JS client script |

## Dev environment setup

**Prerequisites**: Python 3.8+, Node.js 18+, Git.

```bash
# 1. Clone the repository
git clone https://github.com/ltaoist/nano-desktop-os
cd nano-desktop-os

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install frontend dependencies
cd src/frontend
npm install
cd ../..
```

**Start in development mode** (recommended):

```bash
python -m src.backend.launch
```

`launch.py` starts both the backend (`http://127.0.0.1:8000`) and the frontend Vite dev server (`http://localhost:5173`). Vite proxies `/api`, `/ws`, and `/app-content` to the backend. Open `http://localhost:5173` in a browser; the default account is `admin`/`admin`.

**Start independently** (when debugging frontend and backend separately):

```bash
# Terminal 1: backend
python -m src.backend.main
# Terminal 2: frontend
cd src/frontend && npm run dev
```

**Frontend production build**:

```bash
cd src/frontend
npm run build    # output goes to src/frontend/dist/, served by the backend as static files
```

**Docs development**:

```bash
cd docssrc
npm install
npm run docs:dev    # http://localhost:8080
```

## Process management

`launch.py` registers SIGINT/SIGTERM handlers and gracefully shuts down child processes on Ctrl+C:

- Windows: `taskkill /F /T /PID` terminates the process tree
- macOS/Linux: SIGTERM first, then SIGKILL after 3 seconds

Default credentials are stored in `Data/System/auth.json`; you can edit that file directly or change them through the settings UI after login.

## Fork and customization

Fork the repository on GitHub, then clone it locally:

```bash
git clone https://github.com/ltaoist/nano-desktop-os
cd nano-desktop-os
```

The project uses the MIT license and may be freely used, modified, sold, and redistributed; the only requirement is to keep the original copyright notice. Common customization directions:

- **Replace built-in apps**: delete or add `.App` directories under `Data/AppData/`
- **Modify the UI**: edit the Vue components and styles under `src/frontend/src/components/`
- **Integrate external auth**: replace the auth logic in `auth.py`
- **Add system services**: register new routes or background tasks in `main.py`
- **Trim features**: remove unneeded routes, components, or modules

When customizing, keep the TOB communication layer and the core thread/app manager logic, as these are the foundation for running applications. See [⚙️ Minimal System](../minimal/) for the design and implementation of each core component.
