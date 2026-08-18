# What Is a Thread Object Proxy

A Thread Objects Broker (TOB) is an entity with two properties:

- **Unique id**: assigned by the system, uniquely identifying this TOB within a thread
- **Method table**: a mapping of names to functions, which can be dynamically added or removed via mounting operations

Calling a method on a TOB means looking up the function with the corresponding name in its method table and executing it.

A TOB exists on both ends: the Python backend and the JavaScript frontend. Each end creates its own TOBs and mounts its own method implementations. For a remote TOB, the local side holds only its id, not its method table. When a method is called, the remote TOB looks up and executes the corresponding function in its method table, and the return value is sent back.

Both the Python backend and the JavaScript frontend can create multiple TOBs. TOBs of different logical threads (even for the same application) are isolated, so they do not conflict because of identical names.

---

- [TOB Programming](./)
- [TOB Primitives](./primitives)
- [Python TOB API](./python-tob)
- [JavaScript TOB API](./js-tob)
