<template>
  <div class="title-bar">
    <div class="app-icon">{{ appName ? appName[0].toUpperCase() : '?' }}</div>
    <div class="title-info">
      <input
        v-if="editing"
        ref="editInput"
        v-model="editValue"
        class="title-edit-input"
        @blur="saveTitle"
        @keydown.enter="saveTitle"
        @keydown.escape="cancelEdit"
      />
      <template v-else>
        <span class="title-text" @dblclick="startEdit" title="双击编辑标题">{{ title }}</span>
        <span class="thread-id-badge">#{{ threadId }}</span>
        <span class="title-label">{{ label }}</span>
      </template>
    </div>
    <div class="title-actions">
      <button class="tb-action tb-close" title="关闭" @click="$emit('close')">&times;</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WindowTitleBar',
  props: { title: String, label: String, appName: String, status: String, threadId: String },
  emits: ['close', 'suspend', 'update-title'],
  data() {
    return { editing: false, editValue: '' }
  },
  methods: {
    startEdit() {
      this.editValue = this.title
      this.editing = true
      this.$nextTick(() => this.$refs.editInput && this.$refs.editInput.focus())
    },
    saveTitle() {
      if (!this.editing) return
      this.editing = false
      if (this.editValue.trim() && this.editValue.trim() !== this.title) {
        this.$emit('update-title', this.editValue.trim())
      }
    },
    cancelEdit() {
      this.editing = false
    }
  }
}
</script>

<style scoped>
.title-bar { display: flex; align-items: center; padding: 8px 12px; background: #1a1a32; border-bottom: 1px solid #2a2a44; gap: 10px; }
.app-icon { width: 28px; height: 28px; border-radius: 6px; background: #33335a; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: bold; color: #ccc; flex-shrink: 0; }
.title-info { flex: 1; min-width: 0; display: flex; align-items: center; }
.thread-id-badge { font-size: 11px; color: #5a9ef0; background: #1e1e3a; padding: 1px 6px; border-radius: 4px; font-weight: 600; margin-right: 6px; flex-shrink: 0; }
.title-text { font-size: 14px; font-weight: 600; color: #e0e0e0; cursor: default; user-select: none; }
.title-text:hover { color: #fff; }
.title-edit-input { font-size: 14px; font-weight: 600; background: #2a2a42; border: 1px solid #5a9ef0; border-radius: 4px; color: #e0e0e0; padding: 2px 6px; outline: none; width: 200px; }
.title-label { font-size: 11px; color: #777; margin-left: 8px; }
.title-actions { display: flex; gap: 4px; }
.tb-action { width: 28px; height: 28px; border: none; background: transparent; color: #888; font-size: 14px; cursor: pointer; border-radius: 4px; display: flex; align-items: center; justify-content: center; }
.tb-action:hover { background: #33335a; color: #e0e0e0; }
.tb-close:hover { background: #e4434b; color: #fff; }
</style>
