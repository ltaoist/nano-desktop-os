# Python TOB API

The Python-side TOB module is `nano_tob`, built on asyncio. All async functions are provided as coroutines and must be awaited. See [Writing an App - Importing the SDK](../dev/app-basics#importing-the-sdk) for how to import it.

## Function reference

```python
async def initializeTOBM(url: str = None) -> None: ...
async def closeTOBM() -> None: ...

async def createTOB() -> object: ...              # returns a TOB object (with a .id attribute)
async def forgetTOB(tob_id: str) -> bool: ...
def getTOB(tob_id: str) -> object | None: ...     # synchronous

async def nameTOB(tob: object, name: str) -> bool: ...
async def waitNamedTOB(name: str, timeout: int = 0) -> object | None: ...
async def waitTOB(tob_id: str, timeout: int = 0) -> object | None: ...

def mountTOBMethod(tob: object, method: str, delegate: Callable) -> None: ...  # synchronous
async def callTOBMethod(tob: object, method: str, params: list) -> Any: ...
```

See [TOB Primitives](./primitives) for the semantics of each function.

---

- [TOB Programming](./)
- [What Is a Thread Object Proxy](./concept)
- [TOB Primitives](./primitives)
- [JavaScript TOB API](./js-tob)
