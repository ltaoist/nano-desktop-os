import { defaultTheme } from '@vuepress/theme-default'
import { viteBundler } from '@vuepress/bundler-vite'
import { searchPlugin } from '@vuepress/plugin-search'

const zhSidebar = [
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
]

const enSidebar = [
  {
    text: 'About Nano Desktop OS',
    link: '/en/'
  },
  {
    text: 'Usage Guide',
    link: '/en/guide/'
  },
  {
    text: 'App Development',
    link: '/en/dev/',
    collapsible: true,
    children: [
      '/en/dev/logic-thread',
      '/en/dev/app-basics',
      '/en/dev/debug-install'
    ]
  },
  {
    text: 'TOB Programming',
    link: '/en/tob/',
    collapsible: true,
    children: [
      '/en/tob/concept',
      '/en/tob/primitives',
      '/en/tob/python-tob',
      '/en/tob/js-tob'
    ]
  },
  {
    text: 'calc.App Example',
    link: '/en/calc/'
  },
  {
    text: 'snake.App Example',
    link: '/en/snake/'
  },
  {
    text: 'Branch Development',
    link: '/en/branch/'
  },
  {
    text: 'Minimal System',
    link: '/en/minimal/',
    collapsible: true,
    children: [
      '/en/minimal/tob-server',
      '/en/minimal/thread-manager',
      '/en/minimal/app-filesystem',
      '/en/minimal/system-services'
    ]
  }
]

export default {
  title: 'Nano Desktop OS Resources',
  description: 'Nano Desktop OS 文档',
  base: '/nano-desktop-os/',
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }]
  ],
  locales: {
    '/': {
      lang: 'zh-CN',
      title: 'Nano Desktop OS 文档',
      description: 'Nano Desktop OS 文档'
    },
    '/en/': {
      lang: 'en-US',
      title: 'Nano Desktop OS Docs',
      description: 'Nano Desktop OS documentation'
    }
  },
  bundler: viteBundler(),
  theme: defaultTheme({
    repo: 'https://github.com/ltaoist/nano-desktop-os',
    repoLabel: 'GitHub',
    navbar: [],
    locales: {
      '/': {
        selectLanguageName: '简体中文',
        sidebar: zhSidebar,
        lastUpdatedText: '📅 更新时间',
        editLinkText: '在 GitHub 上编辑此页'
      },
      '/en/': {
        selectLanguageName: 'English',
        sidebar: enSidebar,
        lastUpdatedText: '📅 Last Updated',
        editLinkText: 'Edit this page on GitHub'
      }
    },
    lastUpdated: true,
    docsRepo: 'https://github.com/ltaoist/nano-desktop-os',
    docsBranch: 'main',
    docsDir: 'docssrc/docs',
    editLink: true,
    editLinkPattern: ':repo/blob/:branch/:path'
  }),
  plugins: [
    searchPlugin({
      locales: {
        '/': {
          placeholder: '搜索文档'
        },
        '/en/': {
          placeholder: 'Search the docs'
        }
      },
      hotKeys: ['s', '/'],
      maxSuggestions: 10
    })
  ]
}
