<template>
  <div class="thread-item" :class="{ selected, suspended: thread.status === 'suspended', dead: thread.status === 'dead' || thread.status === 'closed' }" @click="handleClick">
    <div class="thread-status" :class="thread.status"></div>
    <div class="thread-icon">{{ thread.app ? thread.app[0].toUpperCase() : '?' }}</div>
    <div class="thread-info">
      <div class="thread-title">{{ thread.title }}</div>
      <div class="thread-label">{{ thread.label }}</div>
    </div>
    <button class="close-btn" @click.stop="$emit('close')" title="关闭">&times;</button>
  </div>
</template>

<script>
export default {
  name: 'ThreadListItem',
  props: { thread: Object, selected: Boolean },
  emits: ['click', 'close'],
  methods: {
    handleClick() {
      if (this.thread.status !== 'dead' && this.thread.status !== 'closed') {
        this.$emit('click')
      }
    }
  }
}
</script>

<style scoped>
.thread-item { display: flex; align-items: center; padding: 10px 8px; gap: 8px; border-radius: 8px; cursor: pointer; margin-bottom: 4px; }
.thread-item:hover { background: #222240; }
.thread-item.selected { background: #2a2a55; }
.thread-item.suspended { opacity: 0.6; }
.thread-item.dead { opacity: 0.4; }
.thread-status { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.thread-status.running { background: #4caf50; }
.thread-status.suspended { background: #ff9800; }
.thread-status.dead, .thread-status.closed { background: #f44336; }
.thread-icon { width: 28px; height: 28px; border-radius: 6px; background: #33335a; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: bold; color: #ccc; flex-shrink: 0; }
.thread-info { flex: 1; min-width: 0; }
.thread-title { font-size: 13px; color: #e0e0e0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.thread-label { font-size: 11px; color: #888; margin-top: 2px; }
.close-btn { width: 22px; height: 22px; border: none; background: transparent; color: #666; font-size: 16px; cursor: pointer; border-radius: 4px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.close-btn:hover { background: #e4434b; color: #fff; }
</style>
