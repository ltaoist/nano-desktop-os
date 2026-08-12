"""
Nano Desktop OS - 线程管理器
管理逻辑线程的生命周期
"""

import json
import os
import subprocess
import sys
from datetime import datetime
import secrets
import string

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Data")


def _nanoid(size=21):
    alphabet = string.ascii_letters + string.digits + "_-"
    return ''.join(secrets.choice(alphabet) for _ in range(size))


def _get_threads_path():
    d = os.path.join(DATA_DIR, "System")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "threads.json")


def _load_threads():
    path = _get_threads_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_threads(threads):
    path = _get_threads_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(threads, f, ensure_ascii=False, indent=2)


# 保存活跃的后端进程引用
_active_processes = {}


def list_threads():
    """列出所有线程"""
    threads = _load_threads()
    return list(threads.values())


def get_thread(thread_id):
    """获取指定线程信息"""
    threads = _load_threads()
    return threads.get(thread_id)


def create_thread(app_name, app_executive, app_type, thread_id=None, display_name=None):
    """创建新线程。thread_id 可由前端指定，未指定则后端生成。"""
    if thread_id is None:
        thread_id = _nanoid(16)
    if display_name is None:
        display_name = app_name.replace(".App", "").replace(".py", "")
    threads = _load_threads()

    threads[thread_id] = {
        "id": thread_id,
        "app": app_name,
        "title": display_name,
        "label": "运行中",
        "status": "running",
        "type": app_type,
        "created_at": datetime.now().isoformat(),
        "pid": None
    }
    _save_threads(threads)
    return thread_id


def update_thread_title(thread_id, title):
    """更新线程标题"""
    threads = _load_threads()
    if thread_id in threads:
        threads[thread_id]["title"] = title
        _save_threads(threads)
    return True


def update_thread_label(thread_id, label):
    """更新线程标签"""
    threads = _load_threads()
    if thread_id in threads:
        threads[thread_id]["label"] = label
        _save_threads(threads)
    return True


def update_thread_status(thread_id, status):
    """更新线程状态：running, dead, suspended, closed"""
    threads = _load_threads()
    if thread_id in threads:
        threads[thread_id]["status"] = status
        _save_threads(threads)
    return True


def start_thread_process(thread_id, app_executive):
    """启动线程对应的执行进程——import 模块后调用 __nanoAppMain()"""
    python = sys.executable
    app_dir = os.path.dirname(app_executive)
    module_name = os.path.splitext(os.path.basename(app_executive))[0]

    code = (
        f"import sys; sys.path.insert(0, r'{app_dir}'); "
        f"from {module_name} import __nanoAppMain; "
        f"import asyncio; asyncio.run(__nanoAppMain())"
    )
    kwargs = dict(
        env={**os.environ, "THREAD_ID": thread_id},
    )
    proc = subprocess.Popen([python, "-c", code], **kwargs)
    _active_processes[thread_id] = proc

    print(f"[{module_name}] 已启动")

    threads = _load_threads()
    if thread_id in threads:
        threads[thread_id]["pid"] = proc.pid
        _save_threads(threads)

    return proc.pid


def kill_thread_process(thread_id):
    """终止线程后端进程"""
    proc = _active_processes.pop(thread_id, None)
    if proc is None:
        return
    try:
        proc.terminate()
    except Exception:
        pass
    # 不调用 wait()——Windows 上可能永远阻塞事件循环
    try:
        proc.kill()
    except Exception:
        pass

    threads = _load_threads()
    if thread_id in threads and proc:
        threads[thread_id]["status"] = "dead" if proc.poll() is not None else "closed"
        threads[thread_id]["pid"] = None
        _save_threads(threads)

    return True


def delete_thread(thread_id):
    """删除线程记录"""
    kill_thread_process(thread_id)
    threads = _load_threads()
    if thread_id in threads:
        del threads[thread_id]
        _save_threads(threads)
    return True


def refresh_thread_statuses():
    """刷新所有线程状态，检测已死亡但未标记为关闭的线程"""
    threads = _load_threads()
    changed = False
    for tid, tinfo in threads.items():
        if tinfo["status"] == "running":
            pid = tinfo.get("pid")
            if pid:
                try:
                    import ctypes
                    kernel32 = ctypes.windll.kernel32
                    handle = kernel32.OpenProcess(0x0400, False, pid)
                    if handle:
                        kernel32.CloseHandle(handle)
                    else:
                        tinfo["status"] = "dead"
                        changed = True
                except Exception:
                    pass
            elif tid not in _active_processes:
                tinfo["status"] = "dead"
                changed = True
    if changed:
        _save_threads(threads)
    return threads


def get_thread_history(thread_id):
    """获取线程历史数据（从应用存储中读取）"""
    # 从路径存储读取线程历史
    from . import data_storage
    history = data_storage.getAppPathData("_system", f"thread_history/{thread_id}.json")
    if history:
        return json.loads(history)
    return None


def save_thread_history(thread_id, data):
    """保存线程历史数据"""
    from . import data_storage
    return data_storage.setAppPathData("_system", f"thread_history/{thread_id}.json", json.dumps(data, ensure_ascii=False))
