export const themeData = JSON.parse("{\"navbar\":[],\"sidebar\":[{\"text\":\"关于 Nano Desktop OS\",\"link\":\"/\"},{\"text\":\"操作指南\",\"link\":\"/guide/\"},{\"text\":\"应用开发\",\"link\":\"/dev/\",\"collapsible\":true,\"children\":[\"/dev/logic-thread\",\"/dev/app-basics\",\"/dev/debug-install\"]},{\"text\":\"TOB 编程\",\"link\":\"/tob/\",\"collapsible\":true,\"children\":[\"/tob/concept\",\"/tob/primitives\",\"/tob/python-tob\",\"/tob/js-tob\"]},{\"text\":\"calc.App 例程\",\"link\":\"/calc/\"},{\"text\":\"snake.App 例程\",\"link\":\"/snake/\"},{\"text\":\"分支开发\",\"link\":\"/branch/\"},{\"text\":\"最小系统开发\",\"link\":\"/minimal/\",\"collapsible\":true,\"children\":[\"/minimal/tob-server\",\"/minimal/thread-manager\",\"/minimal/app-filesystem\",\"/minimal/system-services\"]}],\"lastUpdated\":true,\"lastUpdatedText\":\"📅 更新时间\",\"docsRepo\":\"\",\"docsBranch\":\"main\",\"editLink\":false,\"locales\":{\"/\":{\"selectLanguageName\":\"English\"}},\"colorMode\":\"auto\",\"colorModeSwitch\":true,\"logo\":null,\"repo\":null,\"selectLanguageText\":\"Languages\",\"selectLanguageAriaLabel\":\"Select language\",\"sidebarDepth\":2,\"editLinkText\":\"Edit this page\",\"contributors\":true,\"contributorsText\":\"Contributors\",\"notFound\":[\"There's nothing here.\",\"How did we get here?\",\"That's a Four-Oh-Four.\",\"Looks like we've got some broken links.\"],\"backToHome\":\"Take me home\",\"openInNewWindow\":\"open in new window\",\"toggleColorMode\":\"toggle color mode\",\"toggleSidebar\":\"toggle sidebar\"}")

if (import.meta.webpackHot) {
  import.meta.webpackHot.accept()
  if (__VUE_HMR_RUNTIME__.updateThemeData) {
    __VUE_HMR_RUNTIME__.updateThemeData(themeData)
  }
}

if (import.meta.hot) {
  import.meta.hot.accept(({ themeData }) => {
    __VUE_HMR_RUNTIME__.updateThemeData(themeData)
  })
}
