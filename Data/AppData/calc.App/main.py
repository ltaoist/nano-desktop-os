"""
Nano Desktop OS - 计算器
通过系统通信总线与桌面交互的可视化计算器
"""

import asyncio
import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "src", "backend")
sys.path.insert(0, backend_dir)

import nano_tob


_history = []


def calc_eval(expr):
    """对表达式求值，返回计算结果字符串；出错或无效时返回 None"""
    allowed = set("0123456789+-*/.()% ")
    cleaned = ''.join(c for c in expr if c in allowed)
    if not cleaned:
        return None
    try:
        result = eval(cleaned, {"__builtins__": {}})
        return str(result)
    except Exception:
        return None


def calc_history_push(expr, result):
    """记录一条历史"""
    _history.append(f"{expr} = {result}")
    if len(_history) > 100:
        _history[:] = _history[-50:]


def calc_history_list():
    """返回历史列表的副本"""
    return list(_history)


async def __nanoAppMain():
    await nano_tob.initializeTOBM()

    tob = await nano_tob.createTOB()
    await nano_tob.nameTOB(tob, "app")

    def get_ui():
        """返回 UI 定义"""
        return {"type": "calculator"}

    def calculate(expr):
        """计算表达式"""
        result = calc_eval(expr)
        if result is None:
            return {"error": "无效表达式"}
        calc_history_push(expr, result)
        return {"result": result, "history": calc_history_list()[-10:]}

    def get_history():
        return calc_history_list()

    nano_tob.mountTOBMethod(tob, "get_ui", get_ui)
    nano_tob.mountTOBMethod(tob, "calculate", calculate)
    nano_tob.mountTOBMethod(tob, "get_history", get_history)

    print(f"[calc.App] 计算器已就绪 (thread: {os.environ.get('THREAD_ID', '?')})")

    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        pass
    finally:
        await nano_tob.closeTOBM()
