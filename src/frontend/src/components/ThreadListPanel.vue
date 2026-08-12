<template>
  <div class="thread-list-panel" :class="{ collapsed }">
    <div class="panel-toolbar">
      <span class="os-title">NanoOS</span>
      <button class="tb-btn" title="启动器" @click="$emit('open-launcher')">+</button>
      <button class="tb-btn" title="应用中心" @click="$emit('open-installer')">&#x1F4E6;</button>
    </div>
    <div class="panel-meta">
      <div class="notif-badge" @click="$emit('open-notifications')" title="通知">
        &#x1F514; <span v-if="notifications.length" class="badge-count">{{ notifications.length }}</span>
      </div>
      <span v-if="backendDown" class="backend-warning" title="后端无法连接">&#x26A0;</span>
      <span class="username">admin</span>
    </div>
    <div class="thread-list">
      <ThreadListItem
        v-for="thread in threads"
        :key="thread.id"
        :thread="thread"
        :selected="thread.id === selectedId"
        @click="$emit('select', thread)"
        @close="$emit('close', thread.id)"
      />
      <div v-if="!threads.length" class="empty-hint">暂无运行线程</div>
    </div>
    <div class="panel-collapse-bar" @click="$emit('toggle')" :title="collapsed ? '展开面板' : '折叠面板'">
      <span class="collapse-arrow">{{ collapsed ? '\u25B6' : '\u25C0' }}</span>
    </div>
  </div>
</template>

<script>
import ThreadListItem from './ThreadListItem.vue'

export default {
  name: 'ThreadListPanel',
  components: { ThreadListItem },
  props: {
    threads: { type: Array, default: () => [] },
    selectedId: { type: String, default: null },
    notifications: { type: Array, default: () => [] },
    backendDown: { type: Boolean, default: false },
    collapsed: { type: Boolean, default: false }
  },
  emits: ['select', 'close', 'open-launcher', 'open-installer', 'open-notifications', 'toggle']
}
</script>

<style scoped>
.thread-list-panel {
  width: 260px;
  min-width: 260px;
  height: 100%;
  background: #16162a;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #2a2a44;
  flex-shrink: 0;
  transition: width 0.25s ease, min-width 0.25s ease;
}

.thread-list-panel.collapsed {
  width: 0;
  min-width: 0;
  overflow: hidden;
  border-right: none;
}

.panel-toolbar {
  display: flex;
  align-items: center;
  padding: 12px;
  gap: 8px;
  border-bottom: 1px solid #2a2a44;
}

.os-title {
  font-size: 16px;
  font-weight: 700;
  color: #e0e0e0;
  flex: 1;
  white-space: nowrap;
}

.tb-btn {
  width: 32px;
  height: 32px;
  border: 1px solid #444;
  background: #22223a;
  color: #ccc;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.tb-btn:hover { background: #33335a; }

.panel-collapse-bar {
  height: 20px;
  border-top: 1px solid #2a2a44;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.15s;
}
.panel-collapse-bar:hover { background: #222240; }
.collapse-arrow { color: #666; font-size: 10px; line-height: 1; }

.panel-meta {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid #2a2a44;
  gap: 8px;
}

.notif-badge { cursor: pointer; font-size: 16px; position: relative; }
.badge-count {
  position: absolute;
  top: -6px;
  right: -10px;
  background: #e44;
  color: #fff;
  font-size: 10px;
  border-radius: 10px;
  padding: 1px 5px;
  min-width: 16px;
  text-align: center;
}

.username { font-size: 13px; color: #888; flex: 1; text-align: right; }
.backend-warning { color: #f0a030; font-size: 16px; flex-shrink: 0; }

.thread-list { flex: 1; overflow-y: auto; padding: 8px; }
.empty-hint { text-align: center; color: #555; font-size: 13px; padding: 20px; }
</style>
