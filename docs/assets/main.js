/* Nano Desktop OS Docs — 主题切换 / 侧栏 / 平台选项卡 */
(function () {
  // 主题初始化（尽早执行避免闪烁）
  var saved = null;
  try { saved = localStorage.getItem('nano-docs-theme'); } catch (e) {}
  var theme = saved || (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  document.documentElement.setAttribute('data-theme', theme);

  function setTheme(t) {
    document.documentElement.setAttribute('data-theme', t);
    try { localStorage.setItem('nano-docs-theme', t); } catch (e) {}
    document.querySelectorAll('[data-theme-icon]').forEach(function (el) {
      el.textContent = t === 'dark' ? '☀' : '☾';
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    setTheme(document.documentElement.getAttribute('data-theme'));

    // 主题切换按钮
    document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var cur = document.documentElement.getAttribute('data-theme');
        setTheme(cur === 'dark' ? 'light' : 'dark');
      });
    });

    // 移动端侧栏
    var toggle = document.querySelector('[data-side-toggle]');
    var sidebar = document.querySelector('.sidebar');
    if (toggle && sidebar) {
      toggle.addEventListener('click', function () {
        sidebar.classList.toggle('open');
      });
      sidebar.querySelectorAll('a').forEach(function (a) {
        a.addEventListener('click', function () { sidebar.classList.remove('open'); });
      });
    }

    // 当前页导航高亮
    var path = location.pathname.replace(/\\/g, '/');
    document.querySelectorAll('.sidebar a, .nav-links a').forEach(function (a) {
      var href = a.getAttribute('href');
      if (!href) return;
      var file = href.split('/').pop();
      if (file && path.endsWith(file) && file !== 'index.html') a.classList.add('active');
      if (file === 'index.html' && /index\.html$/.test(path) && href.indexOf('guide') >= 0 && path.indexOf('guide') >= 0) a.classList.add('active');
    });

    // Windows / macOS 平台选项卡
    document.querySelectorAll('.os-tabs').forEach(function (tabs) {
      var btns = tabs.querySelectorAll('.os-tab-bar button');
      var panes = tabs.querySelectorAll('.os-pane');
      btns.forEach(function (btn, i) {
        btn.addEventListener('click', function () {
          btns.forEach(function (b) { b.classList.remove('active'); });
          panes.forEach(function (p) { p.classList.remove('active'); });
          btn.classList.add('active');
          if (panes[i]) panes[i].classList.add('active');
        });
      });
    });

    // 代码块复制按钮
    document.querySelectorAll('pre').forEach(function (pre) {
      var btn = document.createElement('button');
      btn.textContent = '复制';
      btn.style.cssText = 'position:absolute;top:8px;right:10px;font-size:11px;padding:2px 10px;border-radius:6px;border:1px solid var(--border);background:var(--panel);color:var(--text-3);cursor:pointer;font-family:var(--font);';
      btn.addEventListener('click', function () {
        var code = pre.querySelector('code');
        var text = code ? code.innerText : pre.innerText;
        navigator.clipboard && navigator.clipboard.writeText(text).then(function () {
          btn.textContent = '已复制';
          setTimeout(function () { btn.textContent = '复制'; }, 1500);
        });
      });
      pre.appendChild(btn);
    });
  });
})();
