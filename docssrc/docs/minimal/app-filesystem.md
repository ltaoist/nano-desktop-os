# 应用与数据

## 应用类型识别

应用管理器通过目录名后缀识别两种应用类型，逻辑在 `get_app_type()` 和 `get_executive_file()` 中：

| 后缀 | 类型 | 入口文件 | 说明 |
|------|------|----------|------|
| `.App` | `"app"` | `{name}.App/main.py` | 完整应用，包含前端页面（index.html） |
| `.py` | `"script"` | `{name}.py/{name}.py` | 脚本应用，无独立前端页面 |

应用列表通过每次调用 `list_apps()` 时实时扫描 `Data/AppData/` 目录生成，不维护持久化索引。`Data/System/apps_index.json` 相关函数已定义但当前未使用。

**icon 字段**：应用图标取目录名首字母大写（如 calc.App → "C"），这是一个极简的图标方案。

## App 内容服务

`.App` 类型应用的前端通过三个路由服务：

**`GET /app-content/{app_name}`**：重定向到 `/app-content/{app_name}/`，确保浏览器以目录形式解析相对路径。

**`GET /app-content/{app_name}/`**：核心路由，做了一件关键的事——注入 THREAD_ID：

```python
with open(index_html, "r", encoding="utf-8") as f:
    html = f.read()
html = html.replace("</head>", f'<script>window.THREAD_ID="{thread_id}";</script>\n</head>')
return HTMLResponse(html)
```

读取应用目录下的 `index.html`，在 `</head>` 闭合标签前插入一段 `<script>` 设置 `window.THREAD_ID`。这是一种 HTML 字符串级别的注入，不需要应用代码做任何配合。`nano_tob.js` 加载后读取此全局变量。

**`GET /app-content/{app_name}/{path:path}`**：从应用的 `static/` 子目录服务静态资源（CSS、JS、图片等）。注意静态文件路径是 `{app_dir}/static/{path}`，应用的图片、额外脚本等资源需要放在 `static/` 目录下。

### nano_tob.js 的服务位置

`<script src="/nano_tob.js">` 这个脚本不在后端路由中，而是由前端 Vite 开发服务器从 `src/frontend/public/nano_tob.js` 提供。在开发模式下（端口 5173），iframe 的 `/nano_tob.js` 请求被 Vite 拦截并返回 public 目录中的文件。在生产构建后，需要将前端 dist 目录挂载到后端（当前版本依赖 Vite dev server）。

## 安装机制

`install_app(source_path)` 支持三种来源：

1. **.zip 文件**：`zipfile.ZipFile` 解压到 `Data/AppData/{real_name}/`。要求 ZIP 包根目录直接包含入口文件（不多套一层目录）。仅支持 zip 格式，不支持 rar/tar.gz。
2. **目录**：`shutil.copytree()` 复制整个目录到 `Data/AppData/`。
3. **单文件**：创建 `Data/AppData/{filename}/` 目录，`shutil.copy2()` 复制文件进去。

安装后调用 `get_executive_file()` 验证入口文件存在，验证失败则删除已复制的目录并返回错误。`force_install_app()` 先删除同名目录再安装，实现覆盖安装。

## 数据存储框架

`data_storage.py` 实现应用私有存储，核心设计是**按应用名隔离的文件系统路径存储**：

```
Data/AppDataStore/{app_name}/
└── _pathstore/           # 路径数据存储根
    ├── config.json       # /config.json → _pathstore/config.json
    ├── leaderboard.json  # /leaderboard.json
    └── subdir/           # /subdir/ → _pathstore/subdir/
        └── data.txt
```

路径以 `/` 开头，`_sanitize_path()` 去掉前导 `/` 后映射到 `_pathstore/` 下的文件系统路径。`os.makedirs(os.path.dirname(target), exist_ok=True)` 自动创建父目录。

**路径 vs 文件**：`listAppPathEntries` 可列出目录内容；`getAppPathData` 对目录返回 None 只读取文件；`deleteAppPathData` 对目录递归删除（`shutil.rmtree`）对文件删除文件。

**API 设计原则**：
- 全部同步函数——文件 I/O 在桌面场景下足够快，不需要异步封装
- 无内置锁——`data_storage` 不提供跨进程锁，应用需要自行处理并发写入（如 snake.App 的文件锁实现）
- 无版本管理——覆盖式写入，应用自行管理数据格式迁移
- `deleteAppDataStore(app_name)` 删除整个应用数据目录，用于"清空数据"功能

**系统特殊应用名**：线程历史数据使用应用名 `"_system"` 存储在 `Data/AppDataStore/_system/thread_history/{thread_id}.json`，与用户应用数据完全隔离。
