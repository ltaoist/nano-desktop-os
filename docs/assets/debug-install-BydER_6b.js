import{i as e,r as t,s as n,t as r}from"./app-BBqylZP6.js";var i=JSON.parse(`{"path":"/dev/debug-install.html","title":"安装与分发","lang":"en-US","frontmatter":{},"git":{"updatedTime":1786726823000,"contributors":[{"name":"Norman Mo","username":"","email":"ltaoist6@gmail.com","commits":1}],"changelog":[{"hash":"99910ee9697c4385f739104f0d98eddebdc0bc83","time":1786726823000,"email":"ltaoist6@gmail.com","author":"Norman Mo","message":"add docs"}]},"filePathRelative":"dev/debug-install.md"}`),a={name:`debug-install.md`};function o(r,i,a,o,s,c){return n(),t(`div`,null,[...i[0]||=[e(`<h1 id="安装与分发" tabindex="-1"><a class="header-anchor" href="#安装与分发"><span>安装与分发</span></a></h1><p>将应用目录（<code>.App</code> 或 <code>.py</code>）复制到 <code>Data/AppData/</code> 下即完成安装，重启服务或刷新页面后应用出现在启动器中。<code>Data/AppData/</code> 目录下可同时放置多个应用：</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text"><pre><code class="language-text"><span class="line">Data/</span>
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
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>也可以通过界面上的安装器（📦）上传 ZIP 包，安装器自动解压到 <code>Data/AppData/</code>。卸载即删除对应目录，清空应用数据即删除 <code>Data/AppDataStore/</code> 下对应数据目录。</p><p>分发应用时将应用目录打包为 ZIP 文件即可，ZIP 内根目录为应用目录名（<code>.App</code> 或 <code>.py</code> 目录）：</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text"><pre><code class="language-text"><span class="line">myapp.App.zip</span>
<span class="line">└── myapp.App/</span>
<span class="line">    ├── main.py</span>
<span class="line">    ├── index.html</span>
<span class="line">    └── static/</span>
<span class="line">        └── ...</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text"><pre><code class="language-text"><span class="line">myscript.py.zip</span>
<span class="line">└── myscript.py/</span>
<span class="line">    └── myscript.py</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><hr><ul><li><a href="/tob/" target="_blank" rel="noopener noreferrer">TOB 编程</a> — 前后端互操作的完整 API 参考</li><li><a href="/calc/" target="_blank" rel="noopener noreferrer">calc.App 例程</a> · <a href="/snake/" target="_blank" rel="noopener noreferrer">snake.App 例程</a> — 通过代码学习</li></ul>`,9)]])}var s=r(a,[[`render`,o]]);export{i as _pageData,s as default};