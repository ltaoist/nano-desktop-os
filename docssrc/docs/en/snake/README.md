# snake.App — Snake

## App description

snake.App is a Snake game. When opened, the window is split into two columns: on the left is the game area, titled "Snake", with a dark Canvas below it, the current score under the canvas, and operation hints below that (arrow keys to control, space to pause). On the right is a leaderboard panel, titled "Leaderboard", showing the top 10 entries as a table with rank, player name, and score.

At the start of a game the snake is in the center of the canvas, 3 segments long, moving right, and a piece of food (a green square) appears at a random position. The player changes the snake's direction with the arrow keys, but cannot reverse direction (for example, while moving right it cannot turn directly left). Each time the snake eats food it grows one segment and the score increases by 1, and the food reappears at a new random position. The game ends when the snake's head hits a wall or its own body, and a prompt asks the player for a name. After the name is entered, the score is submitted to the leaderboard, which is sorted from high to low and keeps only the top 10 entries. Leaderboard data is persisted to disk and remains visible after the window closes. Press an arrow key or space to start a new game.

![Snake](/assets/snake.png)

## Design

All game logic runs in the frontend: Canvas rendering, a `requestAnimationFrame`-driven loop, arrow-key direction control, collision detection, and scoring all happen locally in the browser. No cross-end calls occur during gameplay.

The backend mounts two async methods. `get_leaderboard` reads and returns the top 10 leaderboard entries; `submit_score` receives a name and score, appends them to the leaderboard, sorts, truncates, and persists to disk. The leaderboard is written to a JSON file using `data_storage`. Multiple windows may submit scores at the same time, so writes use a file lock for concurrency safety; after acquiring the lock the backend reloads the latest data from disk before writing.

## Data persistence

When an app needs to persist data, it uses the `data_storage` module. Data is isolated by app name, and paths start with `/`.

```python
from data_storage import getAppPathData, setAppPathData

# Read text data, returns a string or None
raw = getAppPathData("myapp.App", "/config.json")

# Write text data (overwrite)
setAppPathData("myapp.App", "/config.json", '{"theme":"dark"}')
```

| Function | Description |
|------|------|
| `getAppPathData(app_name, path)` | Read text data, returns a string or None |
| `setAppPathData(app_name, path, data)` | Write text data (overwrite) |
| `deleteAppPathData(app_name, path)` | Delete a file or directory (recursive) |
| `listAppPathEntries(app_name, path)` | List directory entries, returns `[{"name","type"}]` |
| `deleteAppDataStore(app_name)` | Delete the entire app data directory |

Data files are stored under `Data/AppDataStore/{app_name}/` and remain after the app closes.

## Backend implementation

```python
import asyncio, json, os, sys

#
# Import the SDK
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
    # O_CREAT | O_EXCL atomically creates the lock file; if it exists, wait and retry
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
        # Reload from disk after acquiring the lock to get data other processes may have written
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

Both methods are async coroutines. The core of `submit_score` is the file lock: `os.O_CREAT | os.O_EXCL` is an atomic operation guaranteed by the OS — creation fails if the file already exists, so two processes cannot both acquire the lock. After acquiring the lock it reloads the leaderboard from disk (other processes may have written new scores while we waited), appends the new score, sorts, truncates to the top 10, writes back to disk, and finally releases the lock. While waiting for the lock it uses `await asyncio.sleep(0.05)` instead of `time.sleep`, so the event loop is not blocked.

`get_leaderboard` does not involve concurrent writes; it reads the in-memory cache and returns it directly (`_load()` is called to pick up data other processes just wrote).

## Frontend implementation

The frontend uses `<canvas>` to draw the game and `requestAnimationFrame` to drive the game loop.

```javascript
await initializeTOBM();
const tob = await waitNamedTOB('app');

// Load the leaderboard
let leaderboard = await callTOBMethod(tob, 'get_leaderboard', []);

// Game loop (pure frontend, no TOB calls)
function tick() {
  // Move the snake, detect collisions, eat food, score, draw...
  if (headHitWall || headHitBody) {
    const name = prompt("Game over! Enter your name:");
    if (name) {
      // Submit the score and get the updated leaderboard
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

There are no cross-end calls in the game loop `tick`; moving the snake, collision detection, and Canvas rendering all happen locally in the browser. TOB is used only at two moments: when the page loads to fetch the leaderboard, and when the game ends to submit the score.

## Design review

On top of the basic TOB call pattern, snake.App introduces these practices: using `data_storage` to persist data to disk, making methods async coroutines so waiting for the lock does not block the event loop, using `O_CREAT | O_EXCL` to atomically create a file lock for multi-process concurrent writes, and reloading from disk after acquiring the lock to keep data consistent. The game's high-frequency interactions all happen in the frontend, and TOB calls occur only at the boundary moments of loading and submitting data.
