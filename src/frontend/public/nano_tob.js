/**
 * nano_tob.js — Thread Object Broker 前端客户端
 * 供前端节点使用的 TOB API。
 *
 * 使用前需先调用 initializeTOBM() 初始化 Thread Object Broker 机制。
 * 线程 ID 通过 URL query string 的 thread_id 参数获取。
 */

// ── nanoid 实现 ──────────────────────────────────────────────────────

function nanoid(size = 21) {
    const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-';
    const bytes = new Uint8Array(size);
    crypto.getRandomValues(bytes);
    let id = '';
    for (let i = 0; i < size; i++) {
        id += alphabet[bytes[i] % alphabet.length];
    }
    return id;
}

function makeInsId() {
    return 'Ins-' + nanoid();
}

// ── TOB 对象 ─────────────────────────────────────────────────────────

class TOB {
    constructor(tobId) {
        /** @type {string} */
        this.id = tobId;
        /** @type {Object<string, Function>} */
        this._methods = {};
    }
}

// ── 客户端 ───────────────────────────────────────────────────────────

class TOBNode {
    constructor() {
        /** @type {WebSocket|null} */
        this.ws = null;
        this.threadId = getThreadId();
        /** @type {Object<string, {resolve: Function, reject: Function}>} */
        this._pending = {};
        /** @type {Object<string, TOB>} */
        this._tobs = {};
    }

    /**
     * 连接到系统通信服务
     * @param {string} url
     * @returns {Promise<void>}
     */
    connect(url) {
        return new Promise((resolve, reject) => {
            this.ws = new WebSocket(url);
            this.ws.onopen = () => resolve();
            this.ws.onerror = (err) => reject(err);
            this.ws.onclose = () => {
                for (const id of Object.keys(this._pending)) {
                    this._pending[id].reject(new Error('连接已关闭'));
                }
                this._pending = {};
            };
            this.ws.onmessage = (event) => this._onMessage(JSON.parse(event.data));
        });
    }

    /** 关闭连接并清理本地状态 */
    close() {
        this._tobs = {};
        for (const id of Object.keys(this._pending)) {
            this._pending[id].reject(new Error('连接已关闭'));
        }
        this._pending = {};
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    /**
     * 处理服务器消息
     * @param {{type: string, id: string, params: Object}} data
     */
    _onMessage(data) {
        const { type, id, params } = data;

        if (type === 'callTOBMethod') {
            this._handleIncomingCall(id, params);
        } else {
            const pending = this._pending[id];
            if (pending) {
                delete this._pending[id];
                pending.resolve(params);
            }
        }
    }

    /**
     * 处理服务器转发来的方法调用
     * @param {string} insId
     * @param {{tob_id: string, method: string, params: Array}} params
     */
    async _handleIncomingCall(insId, params) {
        const { tob_id, method, params: methodParams } = params;
        const tob = this._tobs[tob_id];

        if (!tob || !tob._methods[method]) {
            this._sendReturn(insId, null, `TOB ${tob_id} 上未挂载方法 '${method}'`);
            return;
        }

        try {
            const result = await tob._methods[method](...(methodParams || []));
            this._sendReturn(insId, result, null);
        } catch (e) {
            this._sendReturn(insId, null, e.message || String(e));
        }
    }

    /**
     * 发送方法调用结果回服务器
     * @param {string} insId
     * @param {*} result
     * @param {string|null} error
     */
    _sendReturn(insId, result, error) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;
        this.ws.send(JSON.stringify({
            thread_id: this.threadId,
            id: insId,
            type: 'callTOBMethodReturn',
            params: { result: result, error: error }
        }));
    }

    /**
     * 发送请求并返回 Promise
     * @param {string} type
     * @param {Object} params
     * @returns {Promise<Object>}
     */
    _request(type, params) {
        return new Promise((resolve, reject) => {
            if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
                reject(new Error('系统通信未连接'));
                return;
            }
            const insId = makeInsId();
            this._pending[insId] = { resolve, reject };
            this.ws.send(JSON.stringify({
                thread_id: this.threadId,
                id: insId,
                type: type,
                params: params
            }));
        });
    }
}

// ── 模块级单例 ────────────────────────────────────────────────────────

/** @type {TOBNode|null} */
let _client = null;

/**
 * 初始化 Thread Object Broker 机制。必须先调用此函数。
 * @param {string} url
 * @returns {Promise<void>}
 */
async function initializeTOBM(url = 'ws://127.0.0.1:8000/ws') {
    _client = new TOBNode();
    await _client.connect(url);
}

async function closeTOBM() {
    if (_client) {
        try {
            await _client.close();
        } finally {
            _client = null;
        }
    }
}

/**
 * 获取当前线程 ID
 * @returns {string}
 */
function getThreadId() {
    return new URLSearchParams(window.location.search).get('thread_id') || '';
}

function _ensureClient() {
    if (!_client) {
        throw new Error('Thread Object Broker 未初始化。请先调用 initializeTOBM(url)。');
    }
}

// ── 公开 API ─────────────────────────────────────────────────────────

/**
 * 创建一个 TOB，返回 TOB 对象
 * @returns {Promise<TOB>}
 */
async function createTOB() {
    _ensureClient();
    const result = await _client._request('createTOB', {});
    const tob = new TOB(result.tob_id);
    _client._tobs[result.tob_id] = tob;
    return tob;
}

/**
 * 给 TOB 命名
 * @param {TOB} tob
 * @param {string} name
 * @returns {Promise<boolean>}
 */
async function nameTOB(tob, name) {
    _ensureClient();
    const result = await _client._request('nameTOB', { tob_id: tob.id, name: name });
    return result.success || false;
}

/**
 * 通过 ID 获取 TOB，不存在返回 null
 * @param {string} tobId
 * @returns {Promise<TOB|null>}
 */
async function getTOB(tobId) {
    _ensureClient();
    const result = await _client._request('getTOB', { tob_id: tobId });
    if (result.tob_id) {
        let tob = _client._tobs[result.tob_id];
        if (!tob) {
            tob = new TOB(result.tob_id);
            _client._tobs[result.tob_id] = tob;
        }
        return tob;
    }
    return null;
}

/**
 * 等待指定 ID 的 TOB 被创建。
 * @param {string} tobId
 * @param {number} timeout 毫秒，0 表示无限等待
 * @returns {Promise<TOB|null>}
 */
async function waitTOB(tobId, timeout = 0) {
    _ensureClient();
    const result = await _client._request('waitTOB', { tob_id: tobId, timeout: timeout });
    if (result.tob_id) {
        let tob = _client._tobs[result.tob_id];
        if (!tob) {
            tob = new TOB(result.tob_id);
            _client._tobs[result.tob_id] = tob;
        }
        return tob;
    }
    return null;
}

/**
 * 等待指定名称的 TOB 被创建。
 * @param {string} name
 * @param {number} timeout 毫秒，0 表示无限等待
 * @returns {Promise<TOB|null>}
 */
async function waitNamedTOB(name, timeout = 0) {
    _ensureClient();
    const result = await _client._request('waitNamedTOB', { name: name, timeout: timeout });
    if (result.tob_id) {
        let tob = _client._tobs[result.tob_id];
        if (!tob) {
            tob = new TOB(result.tob_id);
            _client._tobs[result.tob_id] = tob;
        }
        return tob;
    }
    return null;
}

/**
 * 调用 TOB 上的远程方法
 * @param {TOB} tob
 * @param {string} method
 * @param {Array} params
 * @returns {Promise<*>}
 */
async function callTOBMethod(tob, method, params) {
    _ensureClient();
    const result = await _client._request('callTOBMethod', {
        tob_id: tob.id,
        method: method,
        params: params
    });
    if (result.error) {
        throw new Error(result.error);
    }
    return result.result;
}

/**
 * 在 TOB 上挂载本地方法。纯本地操作，不通知服务器。
 * @param {TOB} tob
 * @param {string} method
 * @param {Function} delegate
 */
function mountTOBMethod(tob, method, delegate) {
    tob._methods[method] = delegate;
}

/**
 * 删除指定 ID 的 TOB
 * @param {string} tobId
 * @returns {Promise<boolean>}
 */
async function forgetTOB(tobId) {
    _ensureClient();
    const result = await _client._request('forgetTOB', { tob_id: tobId });
    if (result.success) {
        delete _client._tobs[tobId];
        return true;
    }
    return false;
}
