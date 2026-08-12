<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="installer-panel">
      <div class="panel-header">
        <h3>应用中心</h3>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>

      <div class="install-section">
        <h4>安装应用</h4>
        <div class="install-form">
          <input v-model="sourcePath" type="text" placeholder="安装包路径 (文件/文件夹/压缩包)" />
          <button @click="install">安装</button>
        </div>
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
  emits: ['install', 'uninstall', 'clear-data', 'close'],
  data() {
    return { sourcePath: '' }
  },
  methods: {
    install() {
      if (this.sourcePath.trim()) {
        this.$emit('install', this.sourcePath.trim())
        this.sourcePath = ''
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
.install-form { display: flex; gap: 8px; }
.install-form input { flex: 1; padding: 8px 12px; background: #2a2a42; border: 1px solid #444; border-radius: 6px; color: #e0e0e0; font-size: 13px; outline: none; }
.install-form input:focus { border-color: #5a9ef0; }
.install-form button { padding: 8px 16px; background: #3a6fc5; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; }
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
