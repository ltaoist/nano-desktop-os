"""
Snake Game - 贪吃蛇
带持久化排行榜（使用 System 数据存储 + 跨进程文件锁）
"""
import asyncio
import json
import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "src", "backend")
sys.path.insert(0, backend_dir)
import nano_tob
from data_storage import getAppPathData, setAppPathData

APP_NAME = "snake.App"
LEADERBOARD_PATH = "/leaderboard.json"

# 跨进程文件锁路径（与 data_storage 共享同一目录）
_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "Data")
_LOCK_PATH = os.path.join(_DATA_DIR, "AppDataStore", APP_NAME, ".leaderboard.lock")

_leaderboard = []


def _load():
    """从 data_storage 读取排行榜"""
    global _leaderboard
    try:
        raw = getAppPathData(APP_NAME, LEADERBOARD_PATH)
        _leaderboard = json.loads(raw) if raw else []
    except Exception:
        _leaderboard = []


def _save():
    """写入排行榜到 data_storage"""
    try:
        setAppPathData(APP_NAME, LEADERBOARD_PATH,
                       json.dumps(_leaderboard, ensure_ascii=False))
    except Exception:
        pass


async def _acquire_file_lock():
    """
    跨进程文件锁：使用 os.O_CREAT | os.O_EXCL 原子创建锁文件。
    文件已存在时等待重试（async sleep，不阻塞事件循环）。
    """
    os.makedirs(os.path.dirname(_LOCK_PATH), exist_ok=True)
    while True:
        try:
            fd = os.open(_LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            os.close(fd)
            return
        except FileExistsError:
            await asyncio.sleep(0.05)


def _release_file_lock():
    """释放跨进程文件锁"""
    try:
        os.remove(_LOCK_PATH)
    except Exception:
        pass


async def submit_score(name, score):
    """
    提交分数到排行榜。
    文件锁保证跨进程互斥，防止多线程同时写导致数据丢失。
    """
    await _acquire_file_lock()
    try:
        # 重新从磁盘加载，获取其他进程可能已写入的最新数据
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
    """返回排行榜（每次从磁盘加载，确保拿到最新数据）"""
    _load()
    return list(_leaderboard[:10])


async def __nanoAppMain():
    # 启动时加载已有数据
    _load()

    await nano_tob.initializeTOBM()

    tob = await nano_tob.createTOB()
    await nano_tob.nameTOB(tob, "app")

    nano_tob.mountTOBMethod(tob, "submit_score", submit_score)
    nano_tob.mountTOBMethod(tob, "get_leaderboard", get_leaderboard)

    print(f"[snake.App] 贪吃蛇已就绪 (thread: {os.environ.get('THREAD_ID', '?')})")

    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        pass
    finally:
        await nano_tob.closeTOBM()
