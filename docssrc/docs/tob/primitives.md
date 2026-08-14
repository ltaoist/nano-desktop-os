# TOB 原语

TOB 共提供 10 个原语，按类别给出每个原语的语义、参数和行为。

## 环境初始化与关闭

### initializeTOBM(url?)

初始化 TOB 运行环境。必须在所有其他 TOB 操作之前调用，且只需调用一次。

- **参数**：`url`（可选）—— 服务器地址。不传时使用默认地址。
- **返回**：初始化完成后返回。
- **异常**：初始化失败时抛出异常。

### closeTOBM()

关闭 TOB 环境。所有待处理的调用被拒绝。调用后可重新调用 `initializeTOBM`。

- **参数**：无。
- **返回**：关闭完成后返回。

## 对象生命周期

### createTOB()

创建一个新的 TOB 对象，获得唯一 ID。新创建的 TOB 方法表为空，没有绑定名称。

- **参数**：无。
- **返回**：TOB 对象，包含唯一标识符属性。
- **权限**：只能操作本端创建的 TOB。

### forgetTOB(tob_id)

销毁指定 ID 的 TOB 对象，清除其方法挂载和名称绑定。销毁后，对该 TOB 的远程调用会失败。

- **参数**：`tob_id`（string）—— 要销毁的 TOB 的 ID。
- **返回**：`true`/`True` 表示成功，`false`/`False` 表示 TOB 不存在或不属于本端。

### getTOB(tob_id)

按 ID 查找本线程内的 TOB 对象，立即返回，不等待。

- **参数**：`tob_id`（string）—— TOB 的 ID。
- **返回**：TOB 对象或 `null`/`None`（不存在时）。

## 命名与发现

### nameTOB(tob, name)

给 TOB 对象绑定一个字符串名称。名称在线程命名空间内唯一，重复命名会覆盖旧名称。命名后，等待该名称的其他端会收到通知。

- **参数**：`tob`（TOB 对象），`name`（string）。
- **返回**：`true`/`True` 成功，`false`/`False` 失败。
- **权限**：只能命名本端创建的 TOB。

### waitNamedTOB(name, timeout?)

等待指定名称的 TOB 被命名。如果该名称的 TOB 已存在，立即返回；否则等待直到被命名或超时。

- **参数**：`name`（string），`timeout`（number，可选）—— 超时毫秒数，0 或不传表示无限等待。
- **返回**：TOB 对象；超时返回 `null`/`None`。
- **线程隔离**：只能等待同一线程内的命名 TOB。

### waitTOB(tob_id, timeout?)

等待指定 ID 的 TOB 被创建。语义与 `waitNamedTOB` 类似，但按 ID 而非名称查找。

- **参数**：`tob_id`（string），`timeout`（number，可选）—— 超时毫秒数。
- **返回**：TOB 对象；超时返回 `null`/`None`。

## 方法挂载与调用

### mountTOBMethod(tob, method, delegate)

在 TOB 对象上挂载一个函数到指定方法名，使其可被远程调用。这是一个同步操作。

- **参数**：
  - `tob`：TOB 对象。
  - `method`（string）：方法名称。
  - `delegate`（function）：本地函数，支持普通函数和 `async`/协程函数。
- **参数传递**：远程调用时，`params` 数组元素按顺序作为函数的位置参数传入。
- **返回值**：函数的返回值会被传回调用方。
- **异常**：函数抛出的异常会被转发给调用方。
- **示例**：
  ```python
  mountTOBMethod(tob, "add", lambda a, b: a + b)
  mountTOBMethod(tob, "fetch", fetch_data)  # async 函数也可以
  ```

### callTOBMethod(tob, method, params)

调用指定 TOB 上的方法，等待结果返回。

- **参数**：
  - `tob`：目标 TOB 对象。
  - `method`（string）：方法名称。
  - `params`（Array/list）：参数数组，按顺序传给目标函数。
- **返回**：返回目标方法的返回值。
- **异常**：目标方法抛出异常时，调用方也会收到异常；TOB 不存在时抛出异常。
- **示例**：
  ```javascript
  const sum = await callTOBMethod(app, 'add', [1, 2]);  // sum === 3
  ```

## 数据类型

方法的参数和返回值必须是 JSON 可序列化类型：string、number、boolean、null、数组、普通对象（无循环引用）。不支持函数、Symbol、undefined、Class 实例。Python 端的 `datetime` 等非 JSON 类型需自行转换。

---

- [TOB 编程](/tob)
- [什么是线程代理对象](/tob/concept)
- [Python TOB API](/tob/python-tob)
- [JavaScript TOB API](/tob/js-tob)
