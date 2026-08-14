// 将 docssrc/assets/ 下的文件复制到 docs/.vuepress/public/assets/
// VuePress 构建时会自动将 public 目录下的文件复制到输出目录
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const sourceDir = path.resolve(__dirname, '../assets')
const targetDir = path.resolve(__dirname, '../docs/.vuepress/public/assets')

fs.mkdirSync(targetDir, { recursive: true })

if (fs.existsSync(sourceDir)) {
  const files = fs.readdirSync(sourceDir)
  for (const file of files) {
    const src = path.join(sourceDir, file)
    const dest = path.join(targetDir, file)
    if (fs.statSync(src).isFile()) {
      fs.copyFileSync(src, dest)
    }
  }
  console.log(`[assets] 已复制 ${files.length} 个文件到 public/assets/`)
} else {
  console.log('[assets] 源目录不存在，跳过复制')
}
