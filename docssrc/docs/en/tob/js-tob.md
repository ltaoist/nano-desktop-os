# JavaScript TOB API

After including `/nano_tob.js` in HTML, all TOB functions are mounted on `window` as global variables, and async functions return Promises.

```html
<script src="/nano_tob.js"></script>
```

## Function reference

```javascript
async function initializeTOBM(url?)              // url optional; auto-built when omitted
async function closeTOBM()

async function createTOB()                       // returns a TOB object { tob_id: string }
async function forgetTOB(tob_id)                 // returns boolean
function getTOB(tob_id)                          // synchronous, returns a TOB or null

async function nameTOB(tob, name)                // returns boolean
async function waitNamedTOB(name, timeout?)      // timeout in ms, 0 = wait forever, returns a TOB or null
async function waitTOB(tob_id, timeout?)         // returns a TOB or null

function mountTOBMethod(tob, method, delegate)   // synchronous
async function callTOBMethod(tob, method, params)// params is an array
```

See [TOB Primitives](./primitives) for the semantics of each function.

---

- [TOB Programming](./)
- [What Is a Thread Object Proxy](./concept)
- [TOB Primitives](./primitives)
- [Python TOB API](./python-tob)
