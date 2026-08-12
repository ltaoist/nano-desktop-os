"""
Nano Desktop OS - 认证模块（单用户）
"""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Data")


def _get_auth_path():
    d = os.path.join(DATA_DIR, "System")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "auth.json")


def _load_auth():
    path = _get_auth_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    # 默认用户
    return {"username": "admin", "password": "admin"}


def _save_auth(data):
    path = _get_auth_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def verify_login(username, password):
    """验证登录"""
    auth = _load_auth()
    return auth.get("username") == username and auth.get("password") == password


def update_credentials(username, password):
    """更新凭据"""
    _save_auth({"username": username, "password": password})
    return True


def check_auth_header(auth_header):
    """检查认证头"""
    if not auth_header:
        return False
    try:
        import base64
        encoded = auth_header.replace("Basic ", "")
        decoded = base64.b64decode(encoded).decode("utf-8")
        username, password = decoded.split(":", 1)
        return verify_login(username, password)
    except Exception:
        return False
