# 编写应用

应用应正确导入 SDK，并编写入口函数。

## 导入 SDK

后端通过 `sys.path` 引入 `src/backend/` 目录，然后导入需要的 SDK 模块：

```python
# 导入路径处理、系统模块
import os, sys

# 从当前文件向上四层找到项目根，拼接 src/backend/ 路径
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "src", "backend")

# 将 SDK 目录插入模块搜索路径最前面，确保能找到 nano_tob 等模块
sys.path.insert(0, backend_dir)

# 导入 TOB 客户端，用于前后端通信
import nano_tob

# 其他 SDK 模块按需导入，例如：
# from data_storage import getAppPathData, setAppPathData
```

前端通过 `<script>` 标签引入 `nano_tob.js`，TOB 函数即作为全局变量可用：

```html
<script src="/nano_tob.js"></script>
```

TOB 的具体用法见 [TOB 编程](../tob/) 章节。

## App 模式

App 模式适合有复杂逻辑和界面的应用。应用应分别提供后端 Python 文件和前端 HTML 文件，前端可使用任意技术栈。系统预装的 calc.App 和 snake.App 都是 App 模式。

App 模式的应用应放在同名 `.App` 目录下：

```
myapp.App/
├── main.py         # 后端
├── index.html      # 前端
└── static/         # 静态资源（JS、CSS、图片等，可选）
```

后端应实现 `__nanoAppMain` 函数。

```python
# 导入异步事件循环、路径处理、系统模块
import asyncio, os, sys

# 从当前文件向上四层找到项目根，拼接 src/backend/ 路径
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "src", "backend")

# 将 SDK 目录插入模块搜索路径最前面
sys.path.insert(0, backend_dir)

# 导入需要的 SDK 模块
# import nano_tob
# from data_storage import ...

async def __nanoAppMain():
    #
    # 应用后端入口。
    # 系统启动线程时在独立 Python 进程中调用此函数。
    #

    # 保持事件循环运行
    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        pass
    finally:
        pass
```

前端应提供 `index.html`。

```html
<!DOCTYPE html>
<html><body>
<div id="app"></div>
<script src="/nano_tob.js"></script>
<script>
//
// 应用前端入口。
//
//
//
</script>
</body></html>
```

前端通过 `/app-content/{app_name}/` 下的 URL 访问应用资源，该路径下的请求由后端从 `static/` 目录返回。例如 `<script src="/app-content/myapp.App/game.js"></script>` 返回 `myapp.App/static/game.js`。以 `/nano_tob.js` 等 `/` 开头的 SDK 路径由前端服务直接提供。

通常，后端可以在入口函数中初始化 TOB，创建一个 TOB 对象并命名（例如 `"app"`），将业务逻辑作为方法挂载上去，前端即可通过 TOB 远程调用这些方法；前端可以在页面中初始化 TOB，等待该命名 TOB 就绪后调用其方法、渲染界面、处理交互。前端也可以创建自己的 TOB 并挂载方法，供后端反向调用——例如推送进度更新或通知。

## 单脚本模式

单脚本模式适合界面简单、以逻辑为主的工具型应用。应用只需提供 Python 文件，不需要独立的前端 HTML 文件。

单脚本模式的应用应放在同名 `.py` 目录下，目录中包含同名的 `.py` 文件：

```
myscript.py/
└── myscript.py
```

单脚本模式的应用打开内容窗口时，Nano Desktop OS 会自动加载一个默认的 HTML 页面（`/html/scriptContentWindow.html`），该页面自动引入 `nano_tob.js` 和 `nano_script_app.js`，连接 TOB 后等待名为 `"scriptAppBackendPublic"` 的 TOB 就绪，调用其 `get_html()` 方法获取 HTML 字符串并渲染。

为此，后端应在 `__nanoAppMain` 中初始化 TOB，创建一个 TOB 命名为 `"scriptAppBackendPublic"`，并挂载 `get_html` 方法：

```python
# 导入异步事件循环、路径处理、系统模块
import asyncio, os, sys

# 从当前文件向上四层找到项目根，拼接 src/backend/ 路径
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "src", "backend")

# 将 SDK 目录插入模块搜索路径最前面
sys.path.insert(0, backend_dir)

# 导入 TOB 客户端
import nano_tob

# 定义返回前端 HTML 内容的函数
def get_html():
    return """<!DOCTYPE html>
<html><body>
<h1>Hello</h1>
<script src="/nano_tob.js"></script>
<script>
//
// get_html 返回的 HTML 被渲染后，nano_tob.js 已加载。
// 可在此初始化 TOB，调用后端方法、处理交互。
//
</script>
</body></html>"""

async def __nanoAppMain():
    #
    # 应用后端入口。
    # 系统启动线程时在独立 Python 进程中调用此函数。
    #

    # 建立与 TOB 消息总线的连接
    await nano_tob.initializeTOBM()

    # 创建一个 TOB 对象，用于通信和方法挂载
    tob = await nano_tob.createTOB()

    # 将 get_html 函数挂载到 TOB 上，供前端调用
    nano_tob.mountTOBMethod(tob, "get_html", get_html)

    # 使用系统约定的名称命名 TOB，前端默认页会找这个名字
    await nano_tob.nameTOB(tob, "scriptAppBackendPublic")

    #
    # 至此初始化完成。系统默认页面会自动连接到 scriptAppBackendPublic，
    # 调用 get_html 获取页面内容并渲染，渲染后的页面即可通过 TOB 调用后端方法。
    #

    # 保持事件循环运行，等待前端调用
    try:
        # 永久等待，直到协程被取消
        await asyncio.Future()

    # 线程关闭时，事件循环会抛出 CancelledError
    except asyncio.CancelledError:
        # 正常退出，无需额外处理
        pass

    # 无论正常退出还是异常，都清理连接
    finally:
        # 关闭 TOB 连接，释放资源
        await nano_tob.closeTOBM()
```

---

- [安装与分发](./debug-install)
