# Python TOB API

Python 端 TOB 模块为 `nano_tob`，基于 asyncio 实现。所有异步函数以 `coroutine` 形式提供，必须 `await`。导入方式见 [编写应用 - 导入 SDK](/dev/app-basics#导入-sdk)。

## 函数参考

```python
async def initializeTOBM(url: str = None) -> None: ...
async def closeTOBM() -> None: ...

async def createTOB() -> object: ...              # 返回 TOB 对象（有 .id 属性）
async def forgetTOB(tob_id: str) -> bool: ...
def getTOB(tob_id: str) -> object | None: ...     # 同步

async def nameTOB(tob: object, name: str) -> bool: ...
async def waitNamedTOB(name: str, timeout: int = 0) -> object | None: ...
async def waitTOB(tob_id: str, timeout: int = 0) -> object | None: ...

def mountTOBMethod(tob: object, method: str, delegate: Callable) -> None: ...  # 同步
async def callTOBMethod(tob: object, method: str, params: list) -> Any: ...
```

各函数语义见 [TOB 原语](/tob/primitives)。

---

- [TOB 编程](/tob)
- [什么是线程代理对象](/tob/concept)
- [TOB 原语](/tob/primitives)
- [JavaScript TOB API](/tob/js-tob)
