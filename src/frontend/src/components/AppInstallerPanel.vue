<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="installer-panel">
      <div class="panel-header">
        <h3>应用中心</h3>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>

      <div class="install-section">
        <h4>安装应用</h4>
        <div
          class="drop-zone"
          :class="{ 'is-dragover': isDragOver, 'is-uploading': isUploading }"
          @dragover.prevent="onDragOver"
          @dragleave.prevent="onDragLeave"
          @drop.prevent="onDrop"
          @click="openFilePicker"
        >
          <input
            ref="fileInput"
            type="file"
            hidden
            multiple
            accept=".zip,.7z,.tar.gz,.tgz,.py"
            @change="onFileInputChange"
          />
          <template v-if="isUploading">
            <div class="drop-icon">⏳</div>
            <div class="drop-text">正在安装...</div>
          </template>
          <template v-else-if="lastFileName">
            <div class="drop-icon">✅</div>
            <div class="drop-text">已安装: {{ lastFileName }}</div>
            <div class="drop-hint">继续拖拽或点击安装其他应用</div>
          </template>
          <template v-else>
            <div class="drop-icon">📦</div>
            <div class="drop-text">拖拽文件/文件夹到这里</div>
            <div class="drop-hint">支持 .zip/.7z 压缩包、.App 文件夹、.py 脚本</div>
            <div class="drop-hint">自动识别外层包裹文件夹，自动补全 .App 后缀</div>
            <div class="drop-hint click-hint">或点击选择文件</div>
          </template>
        </div>
        <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>
      </div>

      <div class="app-list-section">
        <h4>已安装应用 ({{ apps.length }})</h4>
        <div class="app-table">
          <div v-for="app in apps" :key="app.name" class="app-row">
            <div class="app-row-icon">{{ app.icon }}</div>
            <div class="app-row-name">{{ app.display_name }}</div>
            <div class="app-row-type">{{ app.type }}</div>
            <button class="clear-data-btn" @click="$emit('clear-data', app.name)">清空数据</button>
            <button class="uninstall-btn" @click="$emit('uninstall', app.name)">卸载</button>
          </div>
          <div v-if="!apps.length" class="empty-hint">暂无已安装应用</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AppInstallerPanel',
  props: { apps: { type: Array, default: () => [] } },
  emits: ['uninstall', 'clear-data', 'close'],
  data() {
    return {
      isDragOver: false,
      isUploading: false,
      lastFileName: '',
      errorMsg: ''
    }
  },
  methods: {
    onDragOver(e) {
      e.dataTransfer.dropEffect = 'copy'
      this.isDragOver = true
      this.errorMsg = ''
    },
    onDragLeave() {
      this.isDragOver = false
    },
    openFilePicker() {
      if (this.isUploading) return
      this.errorMsg = ''
      this.$refs.fileInput.click()
    },
    onFileInputChange(e) {
      const files = Array.from(e.target.files || [])
      if (files.length > 0) {
        this.uploadFiles(files)
      }
      e.target.value = ''
    },
    async onDrop(e) {
      this.isDragOver = false
      if (this.isUploading) return
      this.errorMsg = ''

      const items = e.dataTransfer.items
      const files = []

      if (items && items.length > 0 && items[0].webkitGetAsEntry) {
        // 使用 webkitGetAsEntry 递归读取文件夹
        const entries = []
        for (let i = 0; i < items.length; i++) {
          const entry = items[i].webkitGetAsEntry()
          if (entry) entries.push(entry)
        }
        const allFiles = await this._readEntries(entries)
        files.push(...allFiles)
      } else {
        // 回退：直接用 dataTransfer.files
        for (let i = 0; i < e.dataTransfer.files.length; i++) {
          files.push(e.dataTransfer.files[i])
        }
      }

      if (files.length > 0) {
        this.uploadFiles(files)
      }
    },
    _readEntries(entries) {
      return new Promise((resolve) => {
        const files = []
        let pending = 0

        const processEntry = (entry, path) => {
          pending++
          if (entry.isFile) {
            entry.file((file) => {
              // 给 File 对象附加相对路径
              Object.defineProperty(file, '_relativePath', {
                value: path + file.name,
                writable: false
              })
              files.push(file)
              pending--
              if (pending === 0) resolve(files)
            }, () => {
              pending--
              if (pending === 0) resolve(files)
            })
          } else if (entry.isDirectory) {
            const reader = entry.createReader()
            const readAll = () => {
              reader.readEntries((subEntries) => {
                if (subEntries.length === 0) {
                  pending--
                  if (pending === 0) resolve(files)
                } else {
                  for (const se of subEntries) {
                    processEntry(se, path + entry.name + '/')
                  }
                  readAll()
                }
              }, () => {
                pending--
                if (pending === 0) resolve(files)
              })
            }
            readAll()
          } else {
            pending--
            if (pending === 0) resolve(files)
          }
        }

        if (entries.length === 0) {
          resolve(files)
          return
        }
        for (const entry of entries) {
          processEntry(entry, '')
        }
      })
    },
    async uploadFiles(files) {
      if (files.length === 0) return
      this.isUploading = true
      this.lastFileName = ''
      this.errorMsg = ''

      const formData = new FormData()
      for (const f of files) {
        // 使用 _relativePath（拖拽文件夹）或 webkitRelativePath（input 选择文件夹）或 name
        let relPath = f._relativePath || f.webkitRelativePath || f.name
        // 确保路径使用 /
        relPath = relPath.replace(/\\/g, '/')
        formData.append('files', f, relPath)
      }

      try {
        const resp = await fetch('/api/apps/upload', {
          method: 'POST',
          body: formData
        })
        const data = await resp.json()
        if (data.success) {
          // 显示安装的文件名
          const firstFile = files[0]
          const name = firstFile._relativePath || firstFile.webkitRelativePath || firstFile.name
          this.lastFileName = name.split('/')[0]
        } else {
          this.errorMsg = data.error || '安装失败'
        }
      } catch (e) {
        this.errorMsg = '安装失败: ' + (e.message || '通信错误')
      } finally {
        this.isUploading = false
      }
    }
  }
}
</script>

<style scoped>
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 900; }
.installer-panel { background: #1e1e36; border: 1px solid #333; border-radius: 12px; width: 520px; max-height: 75vh; overflow-y: auto; padding: 20px; }
.panel-header { display: flex; align-items: center; margin-bottom: 16px; }
.panel-header h3 { flex: 1; font-size: 18px; color: #e0e0e0; }
.close-btn { width: 28px; height: 28px; border: none; background: transparent; color: #888; font-size: 18px; cursor: pointer; border-radius: 4px; }
.close-btn:hover { background: #e4434b; color: #fff; }
.install-section { margin-bottom: 20px; }
.install-section h4, .app-list-section h4 { font-size: 14px; color: #aaa; margin-bottom: 8px; }

.drop-zone {
  border: 2px dashed #444;
  border-radius: 10px;
  padding: 28px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #1a1a30;
  user-select: none;
}
.drop-zone:hover {
  border-color: #5a9ef0;
  background: #1e1e3a;
}
.drop-zone.is-dragover {
  border-color: #5a9ef0;
  background: #252550;
  transform: scale(1.02);
}
.drop-zone.is-uploading {
  cursor: wait;
  border-color: #5a9ef0;
}
.drop-icon {
  font-size: 40px;
  margin-bottom: 10px;
}
.drop-text {
  font-size: 15px;
  color: #ccc;
  margin-bottom: 6px;
}
.drop-hint {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}
.click-hint {
  color: #5a9ef0;
  margin-top: 10px;
}
.error-msg {
  margin-top: 10px;
  padding: 8px 12px;
  background: rgba(228, 68, 68, 0.15);
  border: 1px solid rgba(228, 68, 68, 0.3);
  border-radius: 6px;
  color: #e44;
  font-size: 12px;
  text-align: center;
}

.app-table { max-height: 300px; overflow-y: auto; }
.app-row { display: flex; align-items: center; padding: 8px; gap: 10px; border-bottom: 1px solid #2a2a44; }
.app-row-icon { width: 32px; height: 32px; border-radius: 6px; background: #33335a; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: bold; color: #ccc; flex-shrink: 0; }
.app-row-name { flex: 1; font-size: 13px; color: #e0e0e0; }
.app-row-type { font-size: 11px; color: #777; }
.clear-data-btn { padding: 4px 12px; background: transparent; border: 1px solid #f0a040; color: #f0a040; border-radius: 4px; cursor: pointer; font-size: 12px; }
.clear-data-btn:hover { background: #f0a040; color: #fff; }
.uninstall-btn { padding: 4px 12px; background: transparent; border: 1px solid #e44; color: #e44; border-radius: 4px; cursor: pointer; font-size: 12px; }
.uninstall-btn:hover { background: #e44; color: #fff; }
.empty-hint { text-align: center; color: #555; padding: 20px; }
</style>
