"""
Nano Desktop OS - 数据存储框架
提供路径数据存储
"""

import json
import os
import shutil

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Data")


def _get_app_data_dir(app_name):
    """获取应用数据目录"""
    d = os.path.join(DATA_DIR, "AppDataStore", app_name)
    os.makedirs(d, exist_ok=True)
    return d


def _get_path_store_dir(app_name):
    """获取路径存储目录"""
    d = os.path.join(DATA_DIR, "AppDataStore", app_name, "_pathstore")
    os.makedirs(d, exist_ok=True)
    return d


def _sanitize_path(path):
    """清理路径，移除开头的 /"""
    return path.lstrip("/").replace("\\", "/")


# ── 路径数据存储 ──────────────────────────────────────────────────────

def listAppPathEntries(app_name, path=""):
    """列出路径下的所有条目"""
    base = _get_path_store_dir(app_name)
    target = os.path.join(base, _sanitize_path(path))
    if not os.path.exists(target):
        return []
    entries = []
    for name in os.listdir(target):
        full = os.path.join(target, name)
        entries.append({
            "name": name,
            "type": "directory" if os.path.isdir(full) else "file"
        })
    return entries


def getAppPathData(app_name, path):
    """读取路径数据"""
    base = _get_path_store_dir(app_name)
    target = os.path.join(base, _sanitize_path(path))
    if not os.path.exists(target):
        return None
    if os.path.isdir(target):
        return None
    with open(target, "r", encoding="utf-8") as f:
        return f.read()


def setAppPathData(app_name, path, data):
    """写入路径数据"""
    base = _get_path_store_dir(app_name)
    target = os.path.join(base, _sanitize_path(path))
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(data)
    return True


def deleteAppPathData(app_name, path):
    """删除路径数据"""
    base = _get_path_store_dir(app_name)
    target = os.path.join(base, _sanitize_path(path))
    if os.path.exists(target):
        if os.path.isdir(target):
            shutil.rmtree(target)
        else:
            os.remove(target)
    return True


# ── 应用数据存储管理 ──────────────────────────────────────────────────

def deleteAppDataStore(app_name):
    """删除整个应用的数据存储"""
    app_dir = _get_app_data_dir(app_name)
    if os.path.exists(app_dir):
        shutil.rmtree(app_dir)
    return True

