<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="notification-panel">
      <div class="panel-header">
        <h3>通知</h3>
        <button class="clear-btn" @click="$emit('clear')" v-if="notifications.length">清空</button>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>
      <div class="notif-list">
        <div v-for="n in reversedNotifications" :key="n.id" class="notif-item" :class="n.type">
          <div class="notif-source">{{ n.source }}</div>
          <div class="notif-message">{{ n.message }}</div>
          <div class="notif-time">{{ formatTime(n.time) }}</div>
          <button class="del-btn" @click="$emit('delete', n.id)">&times;</button>
        </div>
        <div v-if="!notifications.length" class="empty-hint">暂无通知</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotificationPanel',
  props: { notifications: { type: Array, default: () => [] } },
  emits: ['delete', 'clear', 'close'],
  computed: {
    reversedNotifications() {
      return [...this.notifications].reverse()
    }
  },
  methods: {
    formatTime(iso) {
      if (!iso) return ''
      const d = new Date(iso)
      return d.toLocaleTimeString()
    }
  }
}
</script>

<style scoped>
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 900; }
.notification-panel { background: #1e1e36; border: 1px solid #333; border-radius: 12px; width: 85vw; height: 85vh; display: flex; flex-direction: column; }
.panel-header { display: flex; align-items: center; padding: 16px; border-bottom: 1px solid #2a2a44; }
.panel-header h3 { flex: 1; font-size: 16px; color: #e0e0e0; }
.clear-btn { padding: 4px 10px; background: transparent; border: 1px solid #666; color: #aaa; border-radius: 4px; cursor: pointer; font-size: 12px; margin-right: 8px; }
.clear-btn:hover { background: #333; }
.close-btn { width: 28px; height: 28px; border: none; background: transparent; color: #888; font-size: 18px; cursor: pointer; border-radius: 4px; }
.close-btn:hover { background: #e4434b; color: #fff; }
.notif-list { padding: 8px; flex: 1; overflow-y: auto; }
.notif-item { padding: 10px; border-radius: 6px; margin-bottom: 4px; position: relative; background: #2a2a42; }
.notif-item.event { border-left: 3px solid #4caf50; }
.notif-item.error { border-left: 3px solid #f44336; }
.notif-source { font-size: 11px; color: #888; }
.notif-message { font-size: 13px; color: #e0e0e0; margin-top: 2px; }
.notif-time { font-size: 10px; color: #666; margin-top: 4px; }
.del-btn { position: absolute; top: 8px; right: 8px; width: 20px; height: 20px; border: none; background: transparent; color: #666; font-size: 14px; cursor: pointer; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.del-btn:hover { background: #e44; color: #fff; }
.empty-hint { text-align: center; color: #555; padding: 20px; }
</style>
