# calc.App — Calculator

## App description

calc.App is a calculator. When opened, the window shows a dark-themed calculator panel in the center: at the top is a display area split into two rows — the upper row shows the currently entered expression in a smaller font, and the lower row shows the result in a larger font, initially `0`. Below the display is a 4×5 key grid: C (clear), parentheses, division; 7, 8, 9, multiplication; 4, 5, 6, subtraction; 1, 2, 3, addition; 0 (two cells wide), decimal point, equals (green). Below the key grid is a history area that can scroll to show the most recent calculation history, each entry formatted as "expression = result".

The user clicks number and operator buttons to enter an expression character by character, and the display area updates in real time as keys are pressed. Clicking "C" clears the current input and resets the display to 0. Clicking "=" evaluates the expression; the result appears in the result row, the expression row appends an "=" marker, and the new record appears at the top of the history area. If the expression has a syntax error, the result row shows "Error". History accumulates during the current session and is cleared when the window closes.

![Calculator](/assets/calc.png)

## Design

The backend mounts two synchronous methods. `calculate` receives an expression string, evaluates it, appends the record to an in-memory history list, and returns the result plus the 10 most recent history entries; `get_history` returns the current history list. Expression evaluation uses `eval`, with whitelist character filtering before evaluation and `__builtins__` cleared to prevent accidental access.

The frontend builds the calculator UI after connecting to TOB. Number, operator, parenthesis, and decimal point keys: on press, append the character to a local expression variable and update the display directly, without calling the backend. "C" key: clears the local expression and display. "=" key: sends the current expression to the backend `calculate` and updates the result row and history area after the response.

## Backend implementation

```python
import asyncio, os, sys

#
# Import the SDK
#
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "src", "backend")
sys.path.insert(0, backend_dir)
import nano_tob

_history = []

def calc_eval(expr):
    # Whitelist: allow only digits, operators, parentheses, decimal point, percent, space
    allowed = set("0123456789+-*/.()% ")
    cleaned = ''.join(c for c in expr if c in allowed)
    if not cleaned:
        return None
    try:
        # Clear __builtins__ to block access to dangerous objects like __import__
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
            return {"error": "Invalid expression"}
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

The backend mounts two synchronous methods: `calculate` receives an expression, evaluates it, records the history, and returns the result plus the 10 most recent history entries; `get_history` returns the history list. `calculate` returns the result and history in one call so the frontend does not need multiple round trips. The expression is filtered through a whitelist before `eval`, and `__builtins__` is cleared in the `eval` namespace.

## Frontend implementation

After connecting to TOB, the frontend builds the calculator UI and handles keys through global functions:

```javascript
await initializeTOBM();
const tob = await waitNamedTOB('app');

let expr = '';

window._calcSend = function(key) {
  if (key === 'C') {
    // Clear: local operation, no backend call
    expr = '';
    elDisplay.textContent = '';
    elResult.textContent = '0';
    return;
  }
  if (key === '=') {
    // Evaluate: call the backend
    callTOBMethod(tob, 'calculate', [expr]).then(r => {
      if (r.error) { elResult.textContent = r.error; return; }
      elResult.textContent = r.result;
      elHistory.innerHTML = (r.history||[]).map(h =>
        '<div class="h-item">'+h+'</div>').join('');
      expr = '';
    });
    return;
  }
  // Digits and operators: append to the local expression and update the display
  expr += key;
  elDisplay.textContent = expr;
};
```

Key handling has three cases: "C" clears local state, digits and operators append to the local expression, and "=" calls the backend to evaluate. Clearing and input happen entirely in the frontend, while only "=" produces one cross-end call.

## Design review

Compared with the generic app entry template, calc.App introduces these practices: the backend mounts synchronous methods, keeps state in process memory (a module-level list), and returns all the data the UI needs (result + history) in one call to avoid multiple round trips. The frontend keeps immediate-feedback input operations local and only calls the backend when computation is required.

The next example, [snake.App](../snake/), introduces data persistence and multi-process concurrency control.
