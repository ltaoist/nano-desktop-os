<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="launcher-panel">
      <div class="panel-header">
        <h3>启动器</h3>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>
      <div class="app-grid">
        <div v-for="app in apps" :key="app.name" class="app-card" @click="$emit('launch', app.name)">
          <div class="app-card-icon">{{ app.icon }}</div>
          <div class="app-card-name">{{ app.display_name }}</div>
          <div class="app-card-type">{{ app.type }}</div>
        </div>
        <div v-if="!apps.length" class="empty-hint">暂无已安装应用</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LauncherPanel',
  props: { apps: { type: Array, default: () => [] } },
  emits: ['launch', 'close']
}
</script>

<style scoped>
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 900; }
.launcher-panel { background: #1e1e36; border: 1px solid #333; border-radius: 12px; width: 480px; max-height: 70vh; overflow-y: auto; padding: 20px; }
.panel-header { display: flex; align-items: center; margin-bottom: 16px; }
.panel-header h3 { flex: 1; font-size: 18px; color: #e0e0e0; }
.close-btn { width: 28px; height: 28px; border: none; background: transparent; color: #888; font-size: 18px; cursor: pointer; border-radius: 4px; }
.close-btn:hover { background: #e4434b; color: #fff; }
.app-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.app-card { background: #2a2a42; border: 1px solid #333; border-radius: 8px; padding: 16px 8px; text-align: center; cursor: pointer; transition: background 0.15s; }
.app-card:hover { background: #33335a; }
.app-card-icon { width: 48px; height: 48px; border-radius: 10px; background: #3a3a5a; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: bold; color: #ccc; margin: 0 auto 8px; }
.app-card-name { font-size: 12px; color: #e0e0e0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.app-card-type { font-size: 10px; color: #777; margin-top: 2px; }
.empty-hint { grid-column: 1 / -1; text-align: center; color: #555; padding: 20px; }
</style>
