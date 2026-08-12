<template>
  <div class="window-content-inner">
    <template v-if="thread.type === 'script'">
      <iframe
        ref="appFrame"
        :key="threadId"
        :src="scriptUrl"
        class="app-iframe"
        sandbox="allow-scripts allow-same-origin allow-forms"
      ></iframe>
    </template>
    <template v-else-if="thread.type === 'app'">
      <iframe
        ref="appFrame"
        :key="threadId"
        :src="appUrl"
        class="app-iframe"
        sandbox="allow-scripts allow-same-origin allow-forms"
      ></iframe>
    </template>
    <div v-else class="loading-hint">未知应用类型</div>
  </div>
</template>

<script>
export default {
  name: 'WindowContent',
  props: { threadId: String, thread: Object },
  computed: {
    scriptUrl() {
      if (this.thread.type !== 'script') return ''
      return `/html/scriptContentWindow.html?thread_id=${this.threadId}`
    },
    appUrl() {
      if (this.thread.type !== 'app') return ''
      return `/app-content/${this.thread.app}/?thread_id=${this.threadId}`
    }
  },
  methods: {
    reload() {
      const frame = this.$refs.appFrame
      if (frame) frame.src = frame.src
    }
  }
}
</script>

<style scoped>
.window-content-inner { width: 100%; height: 100%; }
.app-iframe { width: 100%; height: 100%; border: none; }
.loading-hint { display: flex; align-items: center; justify-content: center; height: 100%; color: #666; font-size: 14px; }
</style>
