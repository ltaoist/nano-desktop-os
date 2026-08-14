# snake.App — 贪吃蛇

## 应用描述

snake.App 是一个贪吃蛇游戏。打开应用后，窗口分为左右两栏：左侧是游戏区域，标题为"贪吃蛇"，下方是一块深色背景的 Canvas 画布，画布下方显示当前分数，再下方是操作提示（方向键控制，空格暂停）。右侧是排行榜面板，标题为"排行榜"，以表格形式显示 Top 10 的排名、玩家名字和分数。

游戏开局时蛇位于画布中央，长度为 3 节，向右移动，画布上随机出现一个食物（绿色方块）。玩家按方向键改变蛇头方向，但不能反向掉头（例如正在向右时不能直接转向左）。蛇每吃到一个食物身体增长一节，分数加 1，食物在新的随机位置重新出现。蛇头撞到画布墙壁或自己的身体时游戏结束，弹出输入框请玩家输入名字。输入名字后分数提交到排行榜，排行榜按分数从高到低排序，只保留前 10 名。排行榜数据持久保存在磁盘上，关闭窗口后下次打开仍然可见。按方向键或空格可以开始新一局。

![贪吃蛇](/assets/snake.png)

## 设计

游戏逻辑全部在前端运行：Canvas 绘制，`requestAnimationFrame` 驱动循环，方向键控制蛇头方向，碰撞检测和计分均在浏览器本地完成，游戏运行期间不产生跨端调用。

后端挂载两个 async 方法。`get_leaderboard` 读取并返回排行榜前10条；`submit_score` 接收名字和分数，追加到排行榜后排序截断，持久化到磁盘。排行榜用 `data_storage` 写入 JSON 文件。多个窗口可能同时提交分数，因此写入时使用文件锁保证并发安全，获得锁后从磁盘重新读取最新数据再写入。

## 数据持久化

应用需要持久化数据时，使用 `data_storage` 模块。数据按应用名隔离存储，路径以 `/` 开头。

```python
from data_storage import getAppPathData, setAppPathData

# 读取文本数据，返回字符串或 None
raw = getAppPathData("myapp.App", "/config.json")

# 写入文本数据（覆盖式）
setAppPathData("myapp.App", "/config.json", '{"theme":"dark"}')
```

| 函数 | 说明 |
|------|------|
| `getAppPathData(app_name, path)` | 读取文本数据，返回字符串或 None |
| `setAppPathData(app_name, path, data)` | 写入文本数据（覆盖式） |
| `deleteAppPathData(app_name, path)` | 删除文件或目录（递归） |
| `listAppPathEntries(app_name, path)` | 列出目录条目，返回 `[{"name","type"}]` |
| `deleteAppDataStore(app_name)` | 删除整个应用数据目录 |

数据文件存储在 `Data/AppDataStore/{app_name}/` 目录下，应用关闭后仍然存在。

## 后端实现

```python
import asyncio, json, os, sys

#
# 导入 SDK
#
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "src", "backend")
sys.path.insert(0, backend_dir)
import nano_tob
from data_storage import getAppPathData, setAppPathData

APP_NAME = "snake.App"
LEADERBOARD_PATH = "/leaderboard.json"
_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "Data")
_LOCK_PATH = os.path.join(_DATA_DIR, "AppDataStore", APP_NAME, ".leaderboard.lock")

_leaderboard = []

def _load():
    global _leaderboard
    try:
        raw = getAppPathData(APP_NAME, LEADERBOARD_PATH)
        _leaderboard = json.loads(raw) if raw else []
    except Exception:
        _leaderboard = []

def _save():
    try:
        setAppPathData(APP_NAME, LEADERBOARD_PATH,
                       json.dumps(_leaderboard, ensure_ascii=False))
    except Exception:
        pass

async def _acquire_file_lock():
    # O_CREAT | O_EXCL 原子创建锁文件，已存在则等待重试
    os.makedirs(os.path.dirname(_LOCK_PATH), exist_ok=True)
    while True:
        try:
            fd = os.open(_LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            os.close(fd)
            return
        except FileExistsError:
            await asyncio.sleep(0.05)

def _release_file_lock():
    try:
        os.remove(_LOCK_PATH)
    except Exception:
        pass

async def submit_score(name, score):
    await _acquire_file_lock()
    try:
        # 获得锁后重新从磁盘加载，拿到其他进程可能已写入的最新数据
        _load()
        _leaderboard.append({"name": str(name), "score": int(score)})
        _leaderboard.sort(key=lambda x: x["score"], reverse=True)
        if len(_leaderboard) > 10:
            _leaderboard[:] = _leaderboard[:10]
        _save()
    finally:
        _release_file_lock()
    return list(_leaderboard[:10])

async def get_leaderboard():
    _load()
    return list(_leaderboard[:10])

async def __nanoAppMain():
    _load()
    await nano_tob.initializeTOBM()
    tob = await nano_tob.createTOB()
    nano_tob.mountTOBMethod(tob, "submit_score", submit_score)
    nano_tob.mountTOBMethod(tob, "get_leaderboard", get_leaderboard)
    await nano_tob.nameTOB(tob, "app")

    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        pass
    finally:
        await nano_tob.closeTOBM()
```

两个方法都是 async 协程。`submit_score` 的核心是文件锁：`os.O_CREAT | os.O_EXCL` 是操作系统保证的原子操作——文件已存在时创建失败，不会出现两个进程同时获得锁的情况。获得锁后重新从磁盘加载排行榜（其他进程可能在我们等待锁期间写入了新分数），追加新分数、排序、截断到Top 10、写回磁盘，最后释放锁。等待锁时用 `await asyncio.sleep(0.05)` 而非 `time.sleep`，不阻塞事件循环。

`get_leaderboard` 不涉及并发写入，直接读取内存缓存返回即可（调用 `_load()` 刷新是为了拿到其他进程刚写入的数据）。

## 前端实现

前端使用 `<canvas>` 绘制游戏画面，`requestAnimationFrame` 驱动游戏循环。

```javascript
await initializeTOBM();
const tob = await waitNamedTOB('app');

// 加载排行榜
let leaderboard = await callTOBMethod(tob, 'get_leaderboard', []);

// 游戏循环（纯前端，无 TOB 调用）
function tick() {
  // 移动蛇、检测碰撞、吃食物、计分、绘制...
  if (headHitWall || headHitBody) {
    const name = prompt("游戏结束！输入你的名字：");
    if (name) {
      // 提交分数，获取更新后的排行榜
      callTOBMethod(tob, 'submit_score', [name, score]).then(lb => {
        leaderboard = lb;
        renderLeaderboard(leaderboard);
      });
    }
    return;
  }
  requestAnimationFrame(tick);
}
```

游戏循环 `tick` 中没有任何跨端调用，蛇的移动、碰撞检测、Canvas 渲染全部在浏览器本地完成。TOB 只在两个时刻使用：页面加载时获取排行榜，游戏结束时提交分数。

## 设计回顾

snake.App 在基础 TOB 调用模式之上引入了这些做法：使用 `data_storage` 将数据持久化到磁盘，方法为 async 协程以便在等待锁时不阻塞事件循环，用 `O_CREAT | O_EXCL` 原子创建文件锁解决多进程并发写入问题，获得锁后重新从磁盘读取以保证数据一致。游戏的高频交互全部在前端完成，TOB 调用仅发生在加载和提交数据的边界时刻。
