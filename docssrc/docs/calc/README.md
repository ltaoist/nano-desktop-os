# calc.App — 计算器

## 应用描述

calc.App 是一个计算器。打开应用后，窗口中央显示一个深色主题的计算器面板：上方是显示区，分为上下两行——上行以较小字号显示当前输入的表达式，下行以较大字号显示计算结果，初始值为 0。显示区下方是 4×5 的按键网格：C（清除）、括号、除号；7、8、9、乘号；4、5、6、减号；1、2、3、加号；0（占两格）、小数点、等号（绿色）。按键网格下方是历史记录区，最多可滚动显示最近的计算历史，每条格式为"表达式 = 结果"。

用户点击数字和运算符按钮逐字符输入表达式，输入过程中显示区实时更新所按键的内容。点击"C"清空当前输入，显示重置为 0。点击"="时，表达式被求值，结果显示在结果行，表达式行追加"="标记，新的计算记录出现在历史区顶部。表达式语法错误时结果行显示 Error。历史记录在本次会话期间持续累积，关闭窗口后清空。

![计算器](/assets/calc.png)

## 设计

后端挂载两个同步方法。`calculate` 接收表达式字符串，求值后将记录追加到内存中的历史列表，返回结果和最近10条历史；`get_history` 返回当前历史列表。表达式求值用 `eval` 完成，求值前做白名单字符过滤，并清空 `__builtins__` 防止意外访问。

前端在连接 TOB 后构建计算器界面。数字键、运算符键、括号键和小数点：按下时追加字符到本地表达式变量，直接更新显示区，不调用后端。"C"键：清空本地表达式和显示。"="键：将当前表达式发送给后端 `calculate`，收到返回后更新结果行和历史区。

## 后端实现

```python
import asyncio, os, sys

#
# 导入 SDK
#
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "src", "backend")
sys.path.insert(0, backend_dir)
import nano_tob

_history = []

def calc_eval(expr):
    # 白名单：只允许数字、运算符、括号、小数点、百分号、空格
    allowed = set("0123456789+-*/.()% ")
    cleaned = ''.join(c for c in expr if c in allowed)
    if not cleaned:
        return None
    try:
        # __builtins__ 置空，阻止访问 __import__ 等危险对象
        result = eval(cleaned, {"__builtins__": {}})
        return str(result)
    except Exception:
        return None

def calc_history_push(expr, result):
    _history.append(f"{expr} = {result}")
    if len(_history) > 100:
        _history[:] = _history[-50:]

def calc_history_list():
    return list(_history)

async def __nanoAppMain():
    await nano_tob.initializeTOBM()
    tob = await nano_tob.createTOB()

    def calculate(expr):
        result = calc_eval(expr)
        if result is None:
            return {"error": "无效表达式"}
        calc_history_push(expr, result)
        return {"result": result, "history": calc_history_list()[-10:]}

    def get_history():
        return calc_history_list()

    nano_tob.mountTOBMethod(tob, "calculate", calculate)
    nano_tob.mountTOBMethod(tob, "get_history", get_history)
    await nano_tob.nameTOB(tob, "app")

    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        pass
    finally:
        await nano_tob.closeTOBM()
```

后端挂载了两个同步方法：`calculate` 接收表达式、求值、记录历史、返回结果和最近10条历史；`get_history` 返回历史列表。`calculate` 一次返回结果和历史，前端不需要多次调用。表达式在 `eval` 前做白名单字符过滤，`eval` 的命名空间中将 `__builtins__` 置空。

## 前端实现

前端在连接 TOB 后构建计算器界面，按键通过全局函数处理：

```javascript
await initializeTOBM();
const tob = await waitNamedTOB('app');

let expr = '';

window._calcSend = function(key) {
  if (key === 'C') {
    // 清除：本地操作，不调用后端
    expr = '';
    elDisplay.textContent = '';
    elResult.textContent = '0';
    return;
  }
  if (key === '=') {
    // 求值：调用后端
    callTOBMethod(tob, 'calculate', [expr]).then(r => {
      if (r.error) { elResult.textContent = r.error; return; }
      elResult.textContent = r.result;
      elHistory.innerHTML = (r.history||[]).map(h =>
        '<div class="h-item">'+h+'</div>').join('');
      expr = '';
    });
    return;
  }
  // 数字和运算符：追加到本地表达式，直接更新显示
  expr += key;
  elDisplay.textContent = expr;
};
```

按键处理分三种情况："C" 清除本地状态、数字和运算符追加到本地表达式、"=" 调用后端求值。其中清除和输入都在前端本地完成，只有"="产生一次跨端调用。

## 设计回顾

相对于通用的应用入口模板，calc.App 引入了这些做法：后端挂载同步方法，状态保存在进程内存中（模块级列表），一次方法调用返回界面更新所需的全部数据（结果+历史），避免多次往返；前端将即时反馈的输入操作留在本地处理，只在需要后端计算时发起调用。

下一例程 [snake.App](../snake/) 引入数据持久化和多进程并发控制。
