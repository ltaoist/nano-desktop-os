"""
Nano Desktop OS - 通知总线
"""

import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Data")


def _get_notifications_path():
    d = os.path.join(DATA_DIR, "System")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "notifications.json")


def _load_notifications():
    path = _get_notifications_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_notifications(notifications):
    path = _get_notifications_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(notifications, f, ensure_ascii=False, indent=2)


def notify_event(message, source="system"):
    """发送事件通知"""
    notifications = _load_notifications()
    notifications.append({
        "id": len(notifications) + 1,
        "type": "event",
        "source": source,
        "message": message,
        "time": datetime.now().isoformat()
    })
    _save_notifications(notifications)
    return True


def notify_error(message, source="system"):
    """发送异常通知"""
    notifications = _load_notifications()
    notifications.append({
        "id": len(notifications) + 1,
        "type": "error",
        "source": source,
        "message": message,
        "time": datetime.now().isoformat()
    })
    _save_notifications(notifications)
    return True


def get_notifications():
    """获取所有通知"""
    return _load_notifications()


def delete_notification(notif_id):
    """删除指定通知"""
    notifications = _load_notifications()
    notifications = [n for n in notifications if n["id"] != notif_id]
    _save_notifications(notifications)
    return True


def clear_notifications():
    """清除所有通知"""
    _save_notifications([])
    return True
