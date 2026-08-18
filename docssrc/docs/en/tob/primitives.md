# TOB Primitives

TOB provides 10 primitives in total, grouped by category, with the semantics, parameters, and behavior of each.

## Environment initialization and shutdown

### initializeTOBM(url?)

Initializes the TOB runtime environment. Must be called before all other TOB operations, and only once.

- **Parameter**: `url` (optional) — server address. When omitted, the default address is used.
- **Returns**: resolves after initialization completes.
- **Exception**: throws if initialization fails.

### closeTOBM()

Closes the TOB environment. All pending calls are rejected. You can call `initializeTOBM` again afterwards.

- **Parameters**: none.
- **Returns**: resolves after closing completes.

## Object lifecycle

### createTOB()

Creates a new TOB object with a unique ID. A newly created TOB has an empty method table and no bound name.

- **Parameters**: none.
- **Returns**: a TOB object containing a unique identifier property.
- **Permission**: you can only operate on TOBs created by the local end.

### forgetTOB(tob_id)

Destroys the TOB with the given ID, clearing its mounted methods and name binding. After destruction, remote calls to that TOB fail.

- **Parameter**: `tob_id` (string) — the ID of the TOB to destroy.
- **Returns**: `true`/`True` on success, `false`/`False` if the TOB does not exist or does not belong to the local end.

### getTOB(tob_id)

Looks up a TOB object in this thread by ID and returns immediately, without waiting.

- **Parameter**: `tob_id` (string) — the TOB's ID.
- **Returns**: the TOB object, or `null`/`None` if it does not exist.

## Naming and discovery

### nameTOB(tob, name)

Binds a string name to a TOB object. Names are unique within a thread's namespace; naming again overwrites the old name. After naming, other ends waiting on that name are notified.

- **Parameters**: `tob` (TOB object), `name` (string).
- **Returns**: `true`/`True` on success, `false`/`False` on failure.
- **Permission**: you can only name TOBs created by the local end.

### waitNamedTOB(name, timeout?)

Waits for a TOB with the given name to be named. If a TOB with that name already exists, returns immediately; otherwise waits until it is named or times out.

- **Parameters**: `name` (string), `timeout` (number, optional) — timeout in milliseconds; `0` or omitted means wait indefinitely.
- **Returns**: the TOB object; `null`/`None` on timeout.
- **Thread isolation**: you can only wait for named TOBs within the same thread.

### waitTOB(tob_id, timeout?)

Waits for a TOB with the given ID to be created. Semantics are similar to `waitNamedTOB`, but lookup is by ID rather than name.

- **Parameters**: `tob_id` (string), `timeout` (number, optional) — timeout in milliseconds.
- **Returns**: the TOB object; `null`/`None` on timeout.

## Method mounting and invocation

### mountTOBMethod(tob, method, delegate)

Mounts a function onto a TOB object under the given method name so it can be called remotely. This is a synchronous operation.

- **Parameters**:
  - `tob`: the TOB object.
  - `method` (string): the method name.
  - `delegate` (function): a local function; supports both plain and `async`/coroutine functions.
- **Argument passing**: on a remote call, elements of the `params` array are passed in order as positional arguments to the function.
- **Return value**: the function's return value is sent back to the caller.
- **Exceptions**: exceptions thrown by the function are forwarded to the caller.
- **Examples**:
  ```python
  mountTOBMethod(tob, "add", lambda a, b: a + b)
  mountTOBMethod(tob, "fetch", fetch_data)  # async functions work too
  ```

### callTOBMethod(tob, method, params)

Calls a method on the given TOB and waits for the result.

- **Parameters**:
  - `tob`: the target TOB object.
  - `method` (string): the method name.
  - `params` (Array/list): the argument array, passed in order to the target function.
- **Returns**: the target method's return value.
- **Exceptions**: if the target method throws, the caller also receives the exception; if the TOB does not exist, an exception is thrown.
- **Example**:
  ```javascript
  const sum = await callTOBMethod(app, 'add', [1, 2]);  // sum === 3
  ```

## Data types

Method parameters and return values must be JSON-serializable types: string, number, boolean, null, arrays, plain objects (no circular references). Functions, Symbols, `undefined`, and class instances are not supported. Non-JSON types on the Python side, such as `datetime`, must be converted manually.

---

- [TOB Programming](./)
- [What Is a Thread Object Proxy](./concept)
- [Python TOB API](./python-tob)
- [JavaScript TOB API](./js-tob)
