"""
Nano Desktop OS - 应用管理器
管理应用的安装、卸载、列表、启动
"""

import json
import os
import shutil

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Data")
APP_DATA_DIR = os.path.join(DATA_DIR, "AppData")


def _get_apps_index_path():
    d = os.path.join(DATA_DIR, "System")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "apps_index.json")


def _load_apps_index():
    path = _get_apps_index_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_apps_index(apps):
    path = _get_apps_index_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(apps, f, ensure_ascii=False, indent=2)


def get_app_type(app_dir_name):
    """判断应用类型：
    - .py 结尾：脚本类型，目录下有一个同名 .py 文件
    - .App 结尾：应用类型，目录下有一个 main.py 文件
    """
    name = app_dir_name
    if name.endswith(".py"):
        return "script"
    elif name.endswith(".App"):
        return "app"
    return "unknown"


def get_executive_file(app_dir_name):
    """获取应用的 Executive 文件路径"""
    app_path = os.path.join(APP_DATA_DIR, app_dir_name)
    app_type = get_app_type(app_dir_name)
    if app_type == "script":
        exec_file = os.path.join(app_path, app_dir_name)  # 同名 .py 文件
        if os.path.isfile(exec_file):
            return exec_file
        return None
    elif app_type == "app":
        exec_file = os.path.join(app_path, "main.py")
        if os.path.isfile(exec_file):
            return exec_file
        return None
    return None


def list_apps():
    """列出所有已安装的应用"""
    apps = []
    if not os.path.exists(APP_DATA_DIR):
        return apps

    for entry in os.listdir(APP_DATA_DIR):
        entry_path = os.path.join(APP_DATA_DIR, entry)
        if not os.path.isdir(entry_path):
            continue
        app_type = get_app_type(entry)
        if app_type == "unknown":
            continue

        exec_file = get_executive_file(entry)
        if not exec_file:
            continue

        apps.append({
            "name": entry,
            "display_name": entry.replace(".App", "").replace(".py", ""),
            "type": app_type,
            "path": entry_path,
            "executive": exec_file,
            "icon": entry[0].upper() if entry else "?"
        })
    return apps


def install_app(source_path):
    """安装应用。source_path 可以是文件、文件夹或压缩包。"""
    if not os.path.exists(source_path):
        return {"success": False, "error": "源路径不存在"}

    # 获取安装包名
    basename = os.path.basename(source_path)

    # 处理压缩包
    if basename.endswith((".zip", ".tar.gz", ".tgz", ".rar")):
        import tempfile
        import zipfile

        # 去掉压缩后缀得到真实名称（仅取第一个后缀前的部分）
        for ext in [".zip", ".tar.gz", ".tgz", ".rar"]:
            if basename.endswith(ext):
                real_name = basename[:-len(ext)]
                break
        else:
            real_name = basename

        dest = os.path.join(APP_DATA_DIR, real_name)

        if os.path.exists(dest):
            return {"success": False, "error": f"应用 '{real_name}' 已存在，请先卸载"}

        if basename.endswith(".zip"):
            with zipfile.ZipFile(source_path, 'r') as zf:
                zf.extractall(dest)
        else:
            return {"success": False, "error": "不支持的压缩格式"}

    elif os.path.isdir(source_path):
        # 文件夹：直接复制
        real_name = basename
        dest = os.path.join(APP_DATA_DIR, real_name)
        if os.path.exists(dest):
            return {"success": False, "error": f"应用 '{real_name}' 已存在，请先卸载"}
        shutil.copytree(source_path, dest)

    elif os.path.isfile(source_path):
        # 单个文件：复制到以文件名命名的目录
        real_name = basename
        dest = os.path.join(APP_DATA_DIR, real_name)
        if os.path.exists(dest):
            return {"success": False, "error": f"应用 '{real_name}' 已存在，请先卸载"}
        os.makedirs(dest, exist_ok=True)
        shutil.copy2(source_path, os.path.join(dest, basename))
    else:
        return {"success": False, "error": "不支持的安装包格式"}

    # 验证安装结果
    exec_file = get_executive_file(real_name)
    if not exec_file:
        # 安装失败，清理
        if os.path.exists(dest):
            shutil.rmtree(dest)
        return {"success": False, "error": f"安装包 '{real_name}' 缺少有效的 Executive 文件"}

    return {"success": True, "name": real_name, "type": get_app_type(real_name), "path": dest}


def uninstall_app(app_name):
    """卸载应用"""
    app_path = os.path.join(APP_DATA_DIR, app_name)
    if not os.path.exists(app_path):
        return {"success": False, "error": "应用不存在"}
    shutil.rmtree(app_path)
    return {"success": True}


def force_install_app(source_path):
    """强制安装（覆盖已存在的应用）"""
    basename = os.path.basename(source_path)

    # 去掉压缩后缀
    for ext in [".zip", ".tar.gz", ".tgz", ".rar"]:
        if basename.endswith(ext):
            real_name = basename[:-len(ext)]
            break
    else:
        real_name = basename

    # 先卸载
    dest = os.path.join(APP_DATA_DIR, real_name)
    if os.path.exists(dest):
        shutil.rmtree(dest)

    return install_app(source_path)
