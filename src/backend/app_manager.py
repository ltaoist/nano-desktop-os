"""
Nano Desktop OS - 应用管理器
管理应用的安装、卸载、列表、启动
"""

import json
import os
import shutil
import tarfile
import tempfile
import zipfile

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Data")
APP_DATA_DIR = os.path.join(DATA_DIR, "AppData")

# 支持的压缩包后缀（按长度从长到短排序，优先匹配复合后缀）
_COMPRESSION_EXTS = [".tar.gz", ".tgz", ".zip", ".7z"]


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


def _strip_compression_ext(name):
    """去掉压缩包后缀，返回裸名"""
    lower = name.lower()
    for ext in _COMPRESSION_EXTS:
        if lower.endswith(ext):
            return name[:-len(ext)]
    return name


def _extract_archive(archive_path, dest_dir):
    """解压压缩包到目标目录。返回 (success, error_msg)"""
    lower = archive_path.lower()
    os.makedirs(dest_dir, exist_ok=True)

    if lower.endswith(".zip"):
        try:
            with zipfile.ZipFile(archive_path, 'r') as zf:
                zf.extractall(dest_dir)
            return True, None
        except Exception as e:
            return False, f"ZIP 解压失败: {e}"

    elif lower.endswith((".tar.gz", ".tgz")):
        try:
            with tarfile.open(archive_path, 'r:gz') as tf:
                tf.extractall(dest_dir)
            return True, None
        except Exception as e:
            return False, f"tar.gz 解压失败: {e}"

    elif lower.endswith(".7z"):
        try:
            import py7zr
        except ImportError:
            return False, "7z 解压需要安装 py7zr 库，请运行: pip install py7zr"
        try:
            with py7zr.SevenZipFile(archive_path, 'r') as sz:
                sz.extractall(dest_dir)
            return True, None
        except Exception as e:
            return False, f"7z 解压失败: {e}"

    return False, f"不支持的压缩格式: {os.path.splitext(archive_path)[1]}"


def _find_app_contents(src_dir):
    """
    分析解压/复制后的目录结构，自动处理以下情况：
    1. 正常结构：目录下直接有 main.py → 返回 src_dir
    2. 套了一层外层文件夹：顶层只有一个子目录，子目录里才有 main.py → 向内剥一层
    3. 缺少 .App 后缀：目录名不以 .App 结尾但包含 main.py → 返回该目录
    4. 单个 .py 脚本文件在目录中（脚本应用）
    返回包含有效应用内容的目录路径，找不到返回 None
    """
    # 先检查当前目录是否直接包含 main.py
    if os.path.isfile(os.path.join(src_dir, "main.py")):
        return src_dir

    # 检查是否是脚本应用（目录下有同名 .py 文件）
    dir_name = os.path.basename(src_dir)
    if dir_name.endswith(".py") and os.path.isfile(os.path.join(src_dir, dir_name)):
        return src_dir

    # 检查是否只有一个 .py 文件（脚本应用场景：单个文件上传）
    entries = os.listdir(src_dir)
    py_files = [e for e in entries if e.endswith(".py") and os.path.isfile(os.path.join(src_dir, e))]
    if len(py_files) == 1 and len(entries) == 1:
        return src_dir

    # 检查是否套了一层文件夹：顶层只有一个子目录
    sub_dirs = [e for e in entries if os.path.isdir(os.path.join(src_dir, e))]
    if len(sub_dirs) == 1 and len(entries) == 1:
        # 递归向内查找
        inner = os.path.join(src_dir, sub_dirs[0])
        found = _find_app_contents(inner)
        if found:
            return found

    # 多文件但没有 main.py，检查是否所有内容都在一个子目录里
    #（Windows 右键压缩常见情况：选了多个文件，但压缩工具自动创建了外层目录）
    if len(sub_dirs) == 1:
        inner = os.path.join(src_dir, sub_dirs[0])
        found = _find_app_contents(inner)
        if found:
            return found

    # 检查当前目录是否有 .py 文件（可能是散装 py 脚本，没有放入同名目录）
    if len(py_files) == 1:
        return src_dir

    return None


def install_app(source_path):
    """安装应用。source_path 可以是文件、文件夹或压缩包。"""
    if not os.path.exists(source_path):
        return {"success": False, "error": "源路径不存在"}

    basename = os.path.basename(source_path)
    lower_name = basename.lower()

    # 明确提示不支持的格式
    if lower_name.endswith(".rar"):
        return {"success": False, "error": "暂不支持 RAR 格式，请先解压为 ZIP 或直接拖拽文件夹安装"}

    is_compressed = any(lower_name.endswith(ext) for ext in _COMPRESSION_EXTS)

    # 初始名称猜测：压缩包去掉后缀，文件夹/文件直接用原名
    if is_compressed:
        initial_name = _strip_compression_ext(basename)
    else:
        initial_name = basename

    # ── 第一步：准备工作目录 ──────────────────────────────────
    tmp_extract_dir = None
    work_dir = None
    cleanup_dirs = []

    try:
        if is_compressed:
            tmp_extract_dir = tempfile.mkdtemp(prefix="nano_app_")
            cleanup_dirs.append(tmp_extract_dir)
            ok, err = _extract_archive(source_path, tmp_extract_dir)
            if not ok:
                return {"success": False, "error": err}
            work_dir = tmp_extract_dir
        elif os.path.isdir(source_path):
            work_dir = source_path
        elif os.path.isfile(source_path):
            tmp_extract_dir = tempfile.mkdtemp(prefix="nano_app_")
            cleanup_dirs.append(tmp_extract_dir)
            shutil.copy2(source_path, os.path.join(tmp_extract_dir, basename))
            work_dir = tmp_extract_dir
        else:
            return {"success": False, "error": "不支持的安装包格式"}

        # ── 第二步：分析目录结构，自动解包外层 ────────────────────
        effective_dir = _find_app_contents(work_dir)
        if not effective_dir:
            return {"success": False, "error": "安装包缺少有效的 main.py 入口文件或脚本文件"}

        # ── 第三步：确定应用名称 ────────────────────────────────
        # effective_dir 是包含 main.py 或脚本的目录
        inner_name = os.path.basename(effective_dir)

        # 判断内层目录名是否是有意义的应用名（不是临时目录）
        def _is_meaningful_name(name):
            """判断目录名是否像一个真正的应用名（非临时目录）"""
            if name.endswith(".App") or name.endswith(".py"):
                return True
            # 临时目录特征：以 nano_app_ 开头，或者全是随机字符
            if name.startswith("nano_app_") or name.startswith("tmp"):
                return False
            # 空名称或纯数字/特殊字符不算
            if not name or len(name) < 2:
                return False
            return True

        # 优先使用内层目录名（如果有意义），否则用初始名称
        if _is_meaningful_name(inner_name):
            real_name = inner_name
        else:
            real_name = initial_name

        # 自动补全后缀：不以 .App/.py 结尾的，根据内容补 .App
        if not real_name.endswith(".App") and not real_name.endswith(".py"):
            if os.path.isfile(os.path.join(effective_dir, "main.py")):
                real_name = real_name + ".App"
            else:
                py_files = [f for f in os.listdir(effective_dir)
                            if f.endswith(".py") and os.path.isfile(os.path.join(effective_dir, f))]
                if len(py_files) == 1:
                    real_name = py_files[0]
                else:
                    real_name = real_name + ".App"

        dest = os.path.join(APP_DATA_DIR, real_name)

        if os.path.exists(dest):
            return {"success": False, "error": f"应用 '{real_name}' 已存在，请先卸载"}

        # ── 第四步：安装到目标目录 ──────────────────────────────
        os.makedirs(os.path.dirname(dest), exist_ok=True)

        # 判断是否需要复制（源目录就是目标目录的直接来源）
        if effective_dir == source_path and os.path.isdir(source_path):
            shutil.copytree(source_path, dest)
        else:
            shutil.copytree(effective_dir, dest)

        # 对于脚本应用：验证同名 .py 文件存在
        if real_name.endswith(".py"):
            script_path = os.path.join(dest, real_name)
            if not os.path.isfile(script_path):
                py_in_dest = [f for f in os.listdir(dest)
                              if f.endswith(".py") and os.path.isfile(os.path.join(dest, f))]
                if len(py_in_dest) == 1:
                    new_name = py_in_dest[0]
                    new_dest = os.path.join(APP_DATA_DIR, new_name)
                    if not os.path.exists(new_dest):
                        os.rename(dest, new_dest)
                        dest = new_dest
                        real_name = new_name
                    else:
                        shutil.rmtree(dest)
                        return {"success": False, "error": f"脚本 '{new_name}' 已存在，请先卸载"}
                else:
                    shutil.rmtree(dest)
                    return {"success": False, "error": "脚本应用缺少同名入口文件"}

        # ── 第五步：验证安装结果 ────────────────────────────────
        exec_file = get_executive_file(real_name)
        if not exec_file:
            if os.path.exists(dest):
                shutil.rmtree(dest)
            return {"success": False, "error": f"安装包 '{real_name}' 缺少有效的 Executive 文件"}

        return {"success": True, "name": real_name, "type": get_app_type(real_name), "path": dest}

    finally:
        for d in cleanup_dirs:
            try:
                shutil.rmtree(d, ignore_errors=True)
            except Exception:
                pass


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
    lower_name = basename.lower()

    # 计算可能的应用名称，用于在安装前删除已有应用
    if any(lower_name.endswith(ext) for ext in _COMPRESSION_EXTS):
        stripped = _strip_compression_ext(basename)
        tmp_dir = tempfile.mkdtemp(prefix="nano_app_force_")
        try:
            ok, err = _extract_archive(source_path, tmp_dir)
            if not ok:
                return {"success": False, "error": err}
            effective_dir = _find_app_contents(tmp_dir)
            if effective_dir:
                inner_name = os.path.basename(effective_dir)
                # 使用与 install_app 相同的命名逻辑推导候选名称
                candidates = []
                if inner_name.endswith(".App") or inner_name.endswith(".py"):
                    candidates.append(inner_name)
                candidates.append(stripped)
                candidates.append(stripped + ".App")
                for candidate in candidates:
                    candidate_path = os.path.join(APP_DATA_DIR, candidate)
                    if os.path.exists(candidate_path):
                        shutil.rmtree(candidate_path)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
    else:
        real_name = basename
        candidate_path = os.path.join(APP_DATA_DIR, real_name)
        if os.path.exists(candidate_path):
            shutil.rmtree(candidate_path)
        # 也尝试加 .App 后缀的情况
        if not real_name.endswith(".App") and not real_name.endswith(".py"):
            candidate_path2 = os.path.join(APP_DATA_DIR, real_name + ".App")
            if os.path.exists(candidate_path2):
                shutil.rmtree(candidate_path2)

    return install_app(source_path)
