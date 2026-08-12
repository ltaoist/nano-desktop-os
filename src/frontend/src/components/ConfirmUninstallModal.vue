<template>
  <div class="modal-overlay" @click.self="cancel">
    <div class="confirm-modal">
      <h3>确认卸载</h3>
      <p>此操作不可恢复。请输入 <strong>{{ appName }}</strong> 以确认：</p>
      <input
        ref="input"
        v-model="typed"
        :class="['confirm-input', { error: typed && typed !== appName }]"
        :placeholder="appName"
        @keydown.enter="confirmIfMatch"
        @keydown.escape="cancel"
      />
      <div class="confirm-actions">
        <button class="btn-cancel" @click="cancel">取消</button>
        <button class="btn-danger" :disabled="typed !== appName" @click="confirmIfMatch">确认卸载</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConfirmUninstallModal',
  props: { appName: { type: String, required: true } },
  emits: ['confirm', 'cancel'],
  data() {
    return { typed: '' }
  },
  mounted() {
    this.$nextTick(() => this.$refs.input.focus())
  },
  methods: {
    confirmIfMatch() {
      if (this.typed === this.appName) {
        this.$emit('confirm')
      }
    },
    cancel() {
      this.$emit('cancel')
    }
  }
}
</script>

<style scoped>
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.confirm-modal { background: #1e1e36; border: 1px solid #444; border-radius: 12px; padding: 24px; width: 400px; }
.confirm-modal h3 { font-size: 18px; color: #e0e0e0; margin-bottom: 12px; }
.confirm-modal p { font-size: 13px; color: #aaa; margin-bottom: 12px; line-height: 1.5; }
.confirm-modal strong { color: #ff6b6b; }
.confirm-input { width: 100%; box-sizing: border-box; padding: 8px 12px; background: #2a2a42; border: 1px solid #555; border-radius: 6px; color: #e0e0e0; font-size: 14px; outline: none; }
.confirm-input:focus { border-color: #ff6b6b; }
.confirm-input.error { border-color: #e44; }
.confirm-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 16px; }
.btn-cancel { padding: 6px 16px; background: transparent; border: 1px solid #555; color: #aaa; border-radius: 6px; cursor: pointer; font-size: 13px; }
.btn-cancel:hover { background: #333; color: #e0e0e0; }
.btn-danger { padding: 6px 16px; background: #e44; border: none; color: #fff; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 600; }
.btn-danger:hover:not(:disabled) { background: #d33; }
.btn-danger:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
