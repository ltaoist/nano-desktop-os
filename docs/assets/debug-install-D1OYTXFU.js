import{a as e,c as t,i as n,l as r,n as i,o as a,r as o,s,t as c}from"./app-Duc5LDOZ.js";var l=JSON.parse(`{"path":"/en/dev/debug-install.html","title":"Install & Distribute","lang":"en-US","frontmatter":{},"git":{},"filePathRelative":"en/dev/debug-install.md"}`),u={name:`debug-install.md`};function d(c,l,u,d,f,p){let m=t(`RouteLink`);return s(),o(`div`,null,[l[6]||=n(`<h1 id="install-distribute" tabindex="-1"><a class="header-anchor" href="#install-distribute"><span>Install &amp; Distribute</span></a></h1><p>Copy an application directory (<code>.App</code> or <code>.py</code>) into <code>Data/AppData/</code> to install it. After restarting the service or refreshing the page, the app appears in the launcher. Multiple applications can be placed under <code>Data/AppData/</code>:</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text"><pre><code class="language-text"><span class="line">Data/</span>
<span class="line">└── AppData/</span>
<span class="line">    ├── calc.App/</span>
<span class="line">    │   ├── main.py</span>
<span class="line">    │   ├── index.html</span>
<span class="line">    │   └── static/</span>
<span class="line">    ├── snake.App/</span>
<span class="line">    │   ├── main.py</span>
<span class="line">    │   ├── index.html</span>
<span class="line">    │   └── static/</span>
<span class="line">    ├── myscript.py/</span>
<span class="line">    │   └── myscript.py</span>
<span class="line">    └── ...</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>You can also upload a ZIP package through the installer (📦) in the UI; the installer extracts it into <code>Data/AppData/</code>. Uninstalling deletes the corresponding directory, and clearing app data deletes the corresponding directory under <code>Data/AppDataStore/</code>.</p><p>To distribute an app, package the app directory as a ZIP file. The ZIP&#39;s root must be the app directory name (<code>.App</code> or <code>.py</code> directory):</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text"><pre><code class="language-text"><span class="line">myapp.App.zip</span>
<span class="line">└── myapp.App/</span>
<span class="line">    ├── main.py</span>
<span class="line">    ├── index.html</span>
<span class="line">    └── static/</span>
<span class="line">        └── ...</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text"><pre><code class="language-text"><span class="line">myscript.py.zip</span>
<span class="line">└── myscript.py/</span>
<span class="line">    └── myscript.py</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><hr>`,8),i(`ul`,null,[i(`li`,null,[a(m,{to:`/en/tob/`},{default:r(()=>[...l[0]||=[e(`TOB Programming`,-1)]]),_:1}),l[1]||=e(` — complete API reference for frontend-backend interop`,-1)]),i(`li`,null,[a(m,{to:`/en/calc/`},{default:r(()=>[...l[2]||=[e(`calc.App Example`,-1)]]),_:1}),l[4]||=e(` · `,-1),a(m,{to:`/en/snake/`},{default:r(()=>[...l[3]||=[e(`snake.App Example`,-1)]]),_:1}),l[5]||=e(` — learn through code`,-1)])])])}var f=c(u,[[`render`,d]]);export{l as _pageData,f as default};