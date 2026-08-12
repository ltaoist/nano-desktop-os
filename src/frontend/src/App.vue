<template>
  <div class="app-root">
    <LoginModal v-if="!loggedIn" @login="onLogin" />
    <template v-else>
      <div class="desktop">
        <ThreadListPanel
          :threads="threads"
          :selectedId="selectedThreadId"
          :notifications="notifications"
          :backendDown="backendDown"
          :collapsed="panelCollapsed"
          @select="selectThread"
          @close="closeThread"
          @open-launcher="showLauncher = true"
          @open-installer="showInstaller = true"
          @open-notifications="showNotifications = !showNotifications"
          @toggle="panelCollapsed = !panelCollapsed"
        />
        <div v-if="panelCollapsed" class="panel-pull-tab" @click="panelCollapsed = false" title="展开线程面板">
          <span class="pull-arrow">&#x25B6;</span>
        </div>
        <div class="main-area">
          <ThreadWindow
            v-if="selectedThread"
            ref="threadWindow"
            :thread="selectedThread"
            :threadId="selectedThreadId"
            @close="closeThread(selectedThreadId)"
            @update-title="title => updateThreadTitle(selectedThreadId, title)"
          />
          <div v-else class="welcome">
            <div class="welcome-icon">N</div>
            <h1>Nano Desktop OS</h1>
            <p>选择左侧线程或通过启动器创建新线程</p>
          </div>
        </div>
      </div>

      <LauncherPanel
        v-if="showLauncher"
        :apps="apps"
        @launch="launchApp"
        @close="showLauncher = false"
      />
      <AppInstallerPanel
        v-if="showInstaller"
        :apps="apps"
        @install="installApp"
        @uninstall="uninstallApp"
        @clear-data="clearAppData"
        @close="showInstaller = false"
      />
      <NotificationPanel
        v-if="showNotifications"
        :notifications="notifications"
        @delete="deleteNotification"
        @clear="clearNotifications"
        @close="showNotifications = false"
      />
      <ConfirmUninstallModal
        v-if="uninstallTarget"
        :appName="uninstallTarget"
        @confirm="confirmUninstall"
        @cancel="cancelUninstall"
      />
    </template>
  </div>
</template>

<script>
import LoginModal from './components/LoginModal.vue'
import ThreadListPanel from './components/ThreadListPanel.vue'
import ThreadWindow from './components/ThreadWindow.vue'
import LauncherPanel from './components/LauncherPanel.vue'
import AppInstallerPanel from './components/AppInstallerPanel.vue'
import NotificationPanel from './components/NotificationPanel.vue'
import ConfirmUninstallModal from './components/ConfirmUninstallModal.vue'

export default {
  name: 'App',
  components: { LoginModal, ThreadListPanel, ThreadWindow, LauncherPanel, AppInstallerPanel, NotificationPanel, ConfirmUninstallModal },
  data() {
    return {
      loggedIn: false,
      threads: [],
      apps: [],
      notifications: [],
      selectedThreadId: null,
      showLauncher: false,
      showInstaller: false,
      showNotifications: false,
      eventSource: null,
      backendDown: false,
      uninstallTarget: null,
      panelCollapsed: false
    }
  },
  computed: {
    selectedThread() {
      return this.threads.find(t => t.id === this.selectedThreadId) || null
    }
  },
  methods: {
    async onLogin({ username, password }) {
      try {
        const ctrl = new AbortController()
        const timer = setTimeout(() => ctrl.abort(), 10000)
        const resp = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password }),
          signal: ctrl.signal
        })
        clearTimeout(timer)
        const data = await resp.json()
        if (data.success) {
          this.loggedIn = true
          this.connectSSE()
        } else {
          alert(data.error || '登录失败')
        }
      } catch (e) {
        alert('登录失败: ' + (e.name === 'AbortError' ? '后端无响应' : (e.message || '通信错误')))
      }
    },
    selectThread(thread) {
      this.selectedThreadId = thread.id
    },
    async closeThread(threadId) {
      try {
        await fetch(`/api/threads/${threadId}`, { method: 'DELETE' })
      } catch (e) { /* ignore */ }
      if (this.selectedThreadId === threadId) {
        this.selectedThreadId = null
      }
    },
    async launchApp(appName) {
      try {
        const threadId = this.nanoid(16)
        const ctrl = new AbortController()
        const timer = setTimeout(() => ctrl.abort(), 10000)
        const resp = await fetch('/api/threads', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ app_name: appName, thread_id: threadId }),
          signal: ctrl.signal
        })
        clearTimeout(timer)
        const data = await resp.json()
        if (data.success) {
          this.showLauncher = false
          this.selectedThreadId = data.thread_id
        } else {
          alert(data.error || '启动失败')
        }
      } catch (e) {
        alert('启动失败: ' + (e.message || '通信错误'))
      }
    },
    toggleSuspend(threadId) {
      const thread = this.threads.find(t => t.id === threadId)
      if (thread) {
        const newStatus = thread.status === 'suspended' ? 'running' : 'suspended'
        fetch(`/api/threads/${threadId}/status`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: newStatus })
        })
      }
    },
    async updateThreadTitle(threadId, title) {
      try {
        await fetch(`/api/threads/${threadId}/title`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title })
        })
      } catch (e) { /* ignore */ }
    },
    async installApp(source) {
      try {
        const resp = await fetch('/api/apps/install', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ source })
        })
        const data = await resp.json()
        if (!data.success) {
          alert(data.error || '安装失败')
        }
      } catch (e) { alert('安装失败: ' + e.message) }
    },
    async uninstallApp(appName) {
      this.uninstallTarget = appName
    },
    async confirmUninstall() {
      const appName = this.uninstallTarget
      this.uninstallTarget = null
      try {
        await fetch(`/api/apps/${appName}`, { method: 'DELETE' })
        this.reloadCurrentWindowIfApp(appName)
      } catch (e) { /* ignore */ }
    },
    cancelUninstall() {
      this.uninstallTarget = null
    },
    async clearAppData(appName) {
      if (!confirm(`确定要清空 "${appName}" 的所有数据吗？此操作不可恢复。`)) return
      try {
        const resp = await fetch(`/api/storage/${appName}`, { method: 'DELETE' })
        const data = await resp.json()
        if (data.success) {
          this.reloadCurrentWindowIfApp(appName)
          alert(`"${appName}" 的数据已清空`)
        } else {
          alert('清空失败')
        }
      } catch (e) {
        alert('清空失败，请确认后端已重启: ' + (e.message || '通信错误'))
      }
    },
    reloadCurrentWindowIfApp(appName) {
      const t = this.selectedThread
      if (t && t.app === appName && this.$refs.threadWindow) {
        this.$refs.threadWindow.reload()
      }
    },
    async deleteNotification(id) {
      try {
        await fetch(`/api/notifications/${id}`, { method: 'DELETE' })
      } catch (e) { /* ignore */ }
    },
    async clearNotifications() {
      try {
        await fetch('/api/notifications', { method: 'DELETE' })
      } catch (e) { /* ignore */ }
    },
    nanoid(size = 16) {
      const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-'
      const bytes = new Uint8Array(size)
      crypto.getRandomValues(bytes)
      let id = ''
      for (let i = 0; i < size; i++) id += alphabet[bytes[i] % alphabet.length]
      return id
    },
    connectSSE() {
      const es = new EventSource('/api/events')
      this.eventSource = es

      es.addEventListener('threads', (e) => {
        try {
          const data = JSON.parse(e.data)
          this.threads = data.threads || []
          this.backendDown = false
        } catch (_) {}
      })
      es.addEventListener('apps', (e) => {
        try {
          const data = JSON.parse(e.data)
          this.apps = data.apps || []
          this.backendDown = false
        } catch (_) {}
      })
      es.addEventListener('notifications', (e) => {
        try {
          const data = JSON.parse(e.data)
          this.notifications = data.notifications || []
          this.backendDown = false
        } catch (_) {}
      })
      es.onerror = () => {
        this.backendDown = true
      }
    }
  },
  beforeUnmount() {
    if (this.eventSource) this.eventSource.close()
  }
}
</script>

<style>
.app-root { width: 100vw; height: 100vh; overflow: hidden; }
.desktop { display: flex; width: 100%; height: 100%; }
.panel-pull-tab {
  width: 28px;
  height: 100%;
  background: #16162a;
  border-right: 1px solid #2a2a44;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  flex-shrink: 0;
  user-select: none;
  transition: background 0.15s;
}
.panel-pull-tab:hover { background: #222240; }
.pull-arrow { color: #888; font-size: 12px; }
.main-area { flex: 1; overflow: hidden; display: flex; flex-direction: column; }
.welcome { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #555; }
.welcome-icon { font-size: 80px; font-weight: bold; color: #333; margin-bottom: 16px; }
.welcome h1 { font-size: 28px; margin-bottom: 8px; color: #777; }
.welcome p { font-size: 14px; }
</style>
