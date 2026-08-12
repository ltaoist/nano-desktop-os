/**
 * nano_script_app.js — 脚本类型应用通用库
 * 与 nano_tob.js 配合使用，封装脚本类型应用的初始化流程
 */

async function nanoScriptInit() {
    await initializeTOBM('ws://127.0.0.1:8000/ws');
    var app = await waitNamedTOB('scriptAppBackendPublic', 10000);
    if (!app) throw new Error('应用未响应');
    var html = await callTOBMethod(app, 'get_html', []);
    if (!html) throw new Error('应用未返回内容');
    document.open();
    document.write(html);
    document.close();
}

async function nanoScriptGetApp() {
    await initializeTOBM('ws://127.0.0.1:8000/ws');
    var app = await waitNamedTOB('scriptAppBackendPublic', 10000);
    if (!app) throw new Error('应用未响应');
    return app;
}
