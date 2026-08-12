<template>
  <div class="thread-window">
    <WindowTitleBar
      :title="thread.title"
      :label="thread.label"
      :appName="thread.app"
      :status="thread.status"
      :threadId="threadId"
      @close="$emit('close')"
      @update-title="title => $emit('update-title', title)"
    />
    <div class="window-content">
      <WindowContent ref="content" :threadId="threadId" :thread="thread" />
    </div>
  </div>
</template>

<script>
import WindowTitleBar from './WindowTitleBar.vue'
import WindowContent from './WindowContent.vue'

export default {
  name: 'ThreadWindow',
  components: { WindowTitleBar, WindowContent },
  props: { thread: Object, threadId: String },
  emits: ['close', 'update-title'],
  methods: {
    reload() {
      this.$refs.content.reload()
    }
  }
}
</script>

<style scoped>
.thread-window { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.window-content { flex: 1; position: relative; overflow: hidden; }
</style>
