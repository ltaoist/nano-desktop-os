# 分支开发

本章面向需要修改系统源码或进行定制开发的开发者，介绍项目结构、开发环境搭建和 Fork 方式。

## 项目结构

```
Nano Desktop/
├── src/
│   ├── backend/          # Python 后端（FastAPI + uvicorn）
│   │   ├── main.py       # 服务器入口：HTTP API、WebSocket、SSE、静态文件
│   │   ├── launch.py     # 一键启动脚本：拉起后端 + 前端 dev server
│   │   ├── tob_server.py # TOB WebSocket 服务（独立部署预留，核心逻辑内嵌 main.py）
│   │   ├── thread_manager.py  # 线程生命周期管理（创建/启动/删除/历史）
│   │   ├── app_manager.py     # 应用扫描/安装/卸载，应用索引维护
│   │   ├── auth.py            # 单用户认证，凭据存 Data/System/auth.json
│   │   ├── data_storage.py    # 应用私有文件存储 + 跨进程文件锁
│   │   ├── nano_tob.py        # Python TOB 客户端
│   │   ├── notification_bus.py # 系统通知持久化与查询
│   │   └── sse_bus.py         # SSE 事件推送（线程/应用/通知变更）
│   └── frontend/         # Vue 3 前端（Vite 构建）
│       ├── public/
│       │   ├── nano_tob.js          # JS TOB 客户端（应用前端引入此脚本）
│       │   ├── nano_script_app.js   # .py 脚本应用运行时
│       │   └── html/scriptContentWindow.html
│       └── src/
│           ├── main.js
│           ├── App.vue              # 桌面根布局
│           └── components/
│               ├── LoginModal.vue
│               ├── LauncherPanel.vue        # 启动器
│               ├── AppInstallerPanel.vue    # 安装器
│               ├── ThreadListPanel.vue      # 线程侧边栏
│               ├── ThreadWindow.vue         # 线程窗口
│               ├── WindowContent.vue        # iframe 内容区
│               ├── WindowTitleBar.vue
│               └── NotificationPanel.vue
├── Data/
│   ├── AppData/          # 应用安装目录（calc.App、snake.App 等）
│   └── System/           # 系统数据（auth.json、apps_index.json）
├── docssrc/              # 文档源码（VuePress 2）
└── requirements.txt      # Python 依赖：fastapi、uvicorn、websockets
```

**后端关键路由**（`main.py`）：

| 路由 | 用途 |
|------|------|
| `WebSocket /ws` | TOB 通信端点 |
| `SSE /api/events` | 服务端事件推送 |
| `POST /api/auth/login` | 登录认证 |
| `GET/POST /api/apps` | 应用列表与安装 |
| `DELETE /api/apps/{name}` | 卸载应用 |
| `GET/POST /api/threads` | 线程列表与创建 |
| `DELETE /api/threads/{id}` | 删除线程 |
| `PUT /api/threads/{id}/title|label|status` | 修改线程属性 |
| `/app-content/{app_name}/*` | 应用前端静态资源 |
| `/nano_tob.js` | TOB JS 客户端脚本 |

## 开发环境搭建

**前置条件**：Python 3.8+、Node.js 18+、Git。

```bash
# 1. 克隆仓库
git clone https://github.com/ltaoist/nano-desktop-os
cd nano-desktop-os

# 2. 安装 Python 依赖
pip install -r requirements.txt

# 3. 安装前端依赖
cd src/frontend
npm install
cd ../..
```

**开发模式启动**（推荐）：

```bash
python -m src.backend.launch
```

`launch.py` 会同时启动后端（`http://127.0.0.1:8000`）和前端 Vite dev server（`http://localhost:5173`），Vite 自动代理 `/api`、`/ws`、`/app-content` 到后端。浏览器打开 `http://localhost:5173`，默认账号 `admin`/`admin`。

**独立启动**（前后端分别调试时）：

```bash
# 终端 1：后端
python -m src.backend.main
# 终端 2：前端
cd src/frontend && npm run dev
```

**前端生产构建**：

```bash
cd src/frontend
npm run build    # 产物输出到 src/frontend/dist/，后端自动提供静态文件
```

**文档开发**：

```bash
cd docssrc
npm install
npm run docs:dev    # http://localhost:8080
```

## 进程管理

`launch.py` 注册了 SIGINT/SIGTERM 处理器，Ctrl+C 时优雅关闭子进程：
- Windows：`taskkill /F /T /PID` 终止进程树
- macOS/Linux：先 SIGTERM，3 秒后 SIGKILL

默认凭据存在 `Data/System/auth.json`，可直接修改或通过登录后设置界面更改。

## Fork 与定制

在 GitHub 上 Fork 仓库后克隆到本地：

```bash
git clone https://github.com/ltaoist/nano-desktop-os
cd nano-desktop-os
```

项目采用 MIT 许可证，可自由使用、修改、商用、再分发，唯一要求是保留原始版权声明。常见的定制方向：

- **替换内置应用**：删除或添加 `Data/AppData/` 下的 `.App` 目录
- **修改 UI**：编辑 `src/frontend/src/components/` 下的 Vue 组件和样式
- **集成外部认证**：替换 `auth.py` 的认证逻辑
- **添加系统服务**：在 `main.py` 中注册新的路由或后台任务
- **裁剪功能**：移除不需要的路由、组件或模块

定制开发时建议保留 TOB 通信层和线程/应用管理器的核心逻辑，这些是应用运行的基础。各核心组件的设计与实现原理见 [⚙️ 最小系统开发](/minimal/)。
