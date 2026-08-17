# 什么是线程代理对象

一个线程对象代理（Thread Objects Broker，TOB）是一个实体，具有两个属性：
- **唯一 id**：由系统分配，在整个线程内唯一标识这个 TOB
- **方法表**：一组名称到函数的映射，可以通过挂载操作动态增删

调用 TOB 的方法，就是在它的方法表中查找对应名称的函数并执行。

TOB 存在于两端：Python 后端和 JavaScript 前端。两端各自创建自己的 TOB、挂载自己的方法实现。对于远端的TOB，本地只持有它的 id，不持有方法表。在调用方法时，远端 TOB 会在方法表中查找并执行对应函数，返回值被传回来。

Python 后端和 JavaScript 前端都可以创建多个TOB。不同的逻辑线程（即使是同一个应用）的TOB是隔离的，他们不会因为同名而冲突。

---

- [TOB 编程](./)
- [TOB 原语](./primitives)
- [Python TOB API](./python-tob)
- [JavaScript TOB API](./js-tob)
