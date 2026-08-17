import { defaultTheme } from '@vuepress/theme-default'
import { viteBundler } from '@vuepress/bundler-vite'
import { searchPlugin } from '@vuepress/plugin-search'

export default {
  title: 'Nano Desktop OS Resources',
  description: 'Nano Desktop OS 文档',
  base: '/nano-desktop-os/',
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }]
  ],
  bundler: viteBundler(),
  theme: defaultTheme({
    repo: 'https://github.com/ltaoist/nano-desktop-os',
    repoLabel: 'GitHub',
    navbar: [],
    sidebar: [
      {
        text: '关于 Nano Desktop OS',
        link: '/'
      },
      {
        text: '操作指南',
        link: '/guide/'
      },
      {
        text: '应用开发',
        link: '/dev/',
        collapsible: true,
        children: [
          '/dev/logic-thread',
          '/dev/app-basics',
          '/dev/debug-install'
        ]
      },
      {
        text: 'TOB 编程',
        link: '/tob/',
        collapsible: true,
        children: [
          '/tob/concept',
          '/tob/primitives',
          '/tob/python-tob',
          '/tob/js-tob'
        ]
      },
      {
        text: 'calc.App 例程',
        link: '/calc/'
      },
      {
        text: 'snake.App 例程',
        link: '/snake/'
      },
      {
        text: '分支开发',
        link: '/branch/'
      },
      {
        text: '最小系统开发',
        link: '/minimal/',
        collapsible: true,
        children: [
          '/minimal/tob-server',
          '/minimal/thread-manager',
          '/minimal/app-filesystem',
          '/minimal/system-services'
        ]
      }
    ],
    lastUpdated: true,
    lastUpdatedText: '📅 更新时间',
    docsRepo: 'https://github.com/ltaoist/nano-desktop-os',
    docsBranch: 'master',
    docsDir: 'docssrc/docs',
    editLink: true,
    editLinkText: '在 GitHub 上编辑此页'
  }),
  plugins: [
    searchPlugin({
      locales: {
        '/': {
          placeholder: '搜索文档'
        }
      },
      hotKeys: ['s', '/'],
      maxSuggestions: 10
    })
  ]
}
