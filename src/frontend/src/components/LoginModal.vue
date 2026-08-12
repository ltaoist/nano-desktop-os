<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="login-modal">
      <h2>Nano Desktop OS</h2>
      <p>请登录以继续</p>
      <form @submit.prevent="handleLogin">
        <input v-model="username" type="text" placeholder="用户名" autofocus />
        <input v-model="password" type="password" placeholder="密码" />
        <button type="submit">登录</button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginModal',
  emits: ['login', 'close'],
  data() {
    return { username: '', password: '' }
  },
  methods: {
    handleLogin() {
      this.$emit('login', { username: this.username, password: this.password })
    }
  }
}
</script>

<style scoped>
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.login-modal { background: #1e1e36; border: 1px solid #333; border-radius: 12px; padding: 32px; width: 360px; text-align: center; }
.login-modal h2 { font-size: 24px; margin-bottom: 8px; color: #e0e0e0; }
.login-modal p { font-size: 13px; color: #888; margin-bottom: 20px; }
.login-modal input { width: 100%; padding: 10px 14px; margin-bottom: 12px; background: #2a2a42; border: 1px solid #444; border-radius: 6px; color: #e0e0e0; font-size: 14px; outline: none; }
.login-modal input:focus { border-color: #5a9ef0; }
.login-modal button { width: 100%; padding: 10px; background: #3a6fc5; color: #fff; border: none; border-radius: 6px; font-size: 15px; cursor: pointer; }
.login-modal button:hover { background: #4a7fd5; }
</style>
