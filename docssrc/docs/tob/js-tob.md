# JavaScript TOB API

在 HTML 中引入 `/nano_tob.js` 后，所有 TOB 函数挂载在 `window` 上作为全局变量，异步函数返回 Promise。

```html
<script src="/nano_tob.js"></script>
```

## 函数参考

```javascript
async function initializeTOBM(url?)              // url 可选，不传则自动构建
async function closeTOBM()

async function createTOB()                       // 返回 TOB 对象 { tob_id: string }
async function forgetTOB(tob_id)                 // 返回 boolean
function getTOB(tob_id)                          // 同步，返回 TOB 或 null

async function nameTOB(tob, name)                // 返回 boolean
async function waitNamedTOB(name, timeout?)      // timeout 毫秒，0=无限等待，返回 TOB 或 null
async function waitTOB(tob_id, timeout?)         // 返回 TOB 或 null

function mountTOBMethod(tob, method, delegate)   // 同步
async function callTOBMethod(tob, method, params)// params 为数组
```

各函数语义见 [TOB 原语](/tob/primitives)。

---

- [TOB 编程](/tob)
- [什么是线程代理对象](/tob/concept)
- [TOB 原语](/tob/primitives)
- [Python TOB API](/tob/python-tob)
