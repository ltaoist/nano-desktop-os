export const redirects = JSON.parse("{}")

export const routes = Object.fromEntries([
  ["/", { loader: () => import(/* webpackChunkName: "index.html" */"D:/repo/OO/Nano Desktop/docssrc/docs/README.md"), meta: {"title":"关于 Nano Desktop OS"} }],
  ["/branch/", { loader: () => import(/* webpackChunkName: "branch_index.html" */"D:/repo/OO/Nano Desktop/docssrc/docs/branch/README.md"), meta: {"title":"分支开发"} }],
  ["/calc/", { loader: () => import(/* webpackChunkName: "calc_index.html" */"D:/repo/OO/Nano Desktop/docssrc/docs/calc/README.md"), meta: {"title":"calc.App — 计算器"} }],
  ["/dev/app-basics.html", { loader: () => import(/* webpackChunkName: "dev_app-basics.html" */"D:/repo/OO/Nano Desktop/docssrc/docs/dev/app-basics.md"), meta: {"title":"编写应用"} }],
  ["/dev/debug-install.html", { loader: () => import(/* webpackChunkName: "dev_debug-install.html" */"D:/repo/OO/Nano Desktop/docssrc/docs/dev/debug-install.md"), meta: {"title":"安装与分发"} }],
  ["/dev/logic-thread.html", { loader: () => import(/* webpackChunkName: "dev_logic-thread.html" */"D:/repo/OO/Nano Desktop/docssrc/docs/dev/logic-thread.md"), meta: {"title":"逻辑线程编程"} }],
  ["/dev/", { loader: () => import(/* webpackChunkName: "dev_index.html" */"D:/repo/OO/Nano Desktop/docssrc/docs/dev/README.md"), meta: {"title":"应用开发"} }],
  ["/guide/", { loader: () => import(/* webpackChunkName: "guide_index.html" */"D:/repo/OO/Nano Desktop/docssrc/docs/guide/README.md"), meta: {"title":"操作指南"} }],
  ["/minimal/app-filesystem.html", { loader: () => import(/* webpackChunkName: "minimal_app-filesystem.html" */"D:/repo/OO/Nano Desktop/docssrc/docs/minimal/app-filesystem.md"), meta: {"title":"应用与数据"} }],
  ["/minimal/", { loader: () => import(/* webpackChunkName: "minimal_index.html" */"D:/repo/OO/Nano Desktop/docssrc/docs/minimal/README.md"), meta: {"title":"最小系统开发"} }],
  ["/minimal/system-services.html", { loader: () => import(/* webpackChunkName: "minimal_system-services.html" */"D:/repo/OO/Nano Desktop/docssrc/docs/minimal/system-services.md"), meta: {"title":"系统服务"} }],
  ["/minimal/thread-manager.html", { loader: () => import(/* webpackChunkName: "minimal_thread-manager.html" */"D:/repo/OO/Nano Desktop/docssrc/docs/minimal/thread-manager.md"), meta: {"title":"线程生命周期"} }],
  ["/minimal/tob-server.html", { loader: () => import(/* webpackChunkName: "minimal_tob-server.html" */"D:/repo/OO/Nano Desktop/docssrc/docs/minimal/tob-server.md"), meta: {"title":"TOB 服务器实现"} }],
  ["/snake/", { loader: () => import(/* webpackChunkName: "snake_index.html" */"D:/repo/OO/Nano Desktop/docssrc/docs/snake/README.md"), meta: {"title":"snake.App — 贪吃蛇"} }],
  ["/tob/concept.html", { loader: () => import(/* webpackChunkName: "tob_concept.html" */"D:/repo/OO/Nano Desktop/docssrc/docs/tob/concept.md"), meta: {"title":"什么是线程代理对象"} }],
  ["/tob/js-tob.html", { loader: () => import(/* webpackChunkName: "tob_js-tob.html" */"D:/repo/OO/Nano Desktop/docssrc/docs/tob/js-tob.md"), meta: {"title":"JavaScript TOB API"} }],
  ["/tob/primitives.html", { loader: () => import(/* webpackChunkName: "tob_primitives.html" */"D:/repo/OO/Nano Desktop/docssrc/docs/tob/primitives.md"), meta: {"title":"TOB 原语"} }],
  ["/tob/python-tob.html", { loader: () => import(/* webpackChunkName: "tob_python-tob.html" */"D:/repo/OO/Nano Desktop/docssrc/docs/tob/python-tob.md"), meta: {"title":"Python TOB API"} }],
  ["/tob/", { loader: () => import(/* webpackChunkName: "tob_index.html" */"D:/repo/OO/Nano Desktop/docssrc/docs/tob/README.md"), meta: {"title":"TOB 编程"} }],
  ["/404.html", { loader: () => import(/* webpackChunkName: "404.html" */"D:/repo/OO/Nano Desktop/docssrc/docs/.vuepress/.temp/pages/404.html.vue"), meta: {"title":""} }],
]);
