<template>
  <div class="login-page">
    <!-- 纯净背景层 -->
    <div class="background-glass"></div>

    <!-- 左侧：品牌区域 -->
    <div class="brand-section">
      <div class="brand-content animate-in">
        <div class="brand-mark">
          <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="20" cy="20" r="18" stroke="currentColor" stroke-width="1.5" opacity="0.3"/>
            <circle cx="20" cy="20" r="12" stroke="currentColor" stroke-width="1.5" opacity="0.5"/>
            <circle cx="20" cy="20" r="6" fill="currentColor" opacity="0.8"/>
          </svg>
        </div>
        <h1 class="brand-title">BankAgent</h1>
        <p class="brand-tagline">智能银行数据分析平台</p>

        <div class="brand-features">
          <div class="feature-item">
            <span class="feature-icon">—</span>
            <span>智能对话分析</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">—</span>
            <span>数据可视化洞察</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">—</span>
            <span>知识库智能检索</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧：登录表单 -->
    <div class="form-section">
      <div class="form-container animate-in">
        <div class="form-header">
          <p class="form-greeting">欢迎回来</p>
          <h2 class="form-title">登录您的账户</h2>
        </div>

        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label class="form-label">工号</label>
            <input
              v-model="form.employee_id"
              type="text"
              class="form-input"
              placeholder="请输入工号"
              autocomplete="username"
            />
          </div>

          <div class="form-group">
            <label class="form-label">密码</label>
            <input
              v-model="form.password"
              type="password"
              class="form-input"
              placeholder="请输入密码"
              autocomplete="current-password"
            />
          </div>

          <button type="submit" class="btn-submit" :disabled="loading">
            <span v-if="!loading">登录</span>
            <span v-else class="loading-text">
              <span class="loading-dot"></span>
              <span class="loading-dot"></span>
              <span class="loading-dot"></span>
            </span>
          </button>
        </form>

        <div class="form-footer">
          <p class="register-link">
            还没有账户？
            <router-link to="/register" class="link">立即注册</router-link>
          </p>
        </div>
      </div>
    </div>

    <!-- 通知提示 -->
    <div v-if="notification.show" :class="['notification', notification.type]">
      <span>{{ notification.message }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()

const form = reactive({
  employee_id: '',
  password: ''
})

const loading = ref(false)
const notification = reactive({ show: false, message: '', type: '' })

const showNotification = (message, type = 'error') => {
  notification.message = message
  notification.type = type
  notification.show = true
  setTimeout(() => { notification.show = false }, 3000)
}

const handleLogin = async () => {
  if (!form.employee_id.trim()) {
    showNotification('请输入工号')
    return
  }
  if (!form.password) {
    showNotification('请输入密码')
    return
  }

  loading.value = true

  try {
    const response = await api.post('/api/v1/auth/login', {
      employee_id: form.employee_id,
      password: form.password
    })

    localStorage.setItem('token', response.data.access_token)
    localStorage.setItem('user', JSON.stringify(response.data.user))
    localStorage.setItem('userId', response.data.user.id)

    router.push('/chat')
  } catch (error) {
    showNotification(error.response?.data?.detail || '登录失败，请检查工号和密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ============================================================
   Apple Style Layout
   ============================================================ */

.login-page {
  min-height: 100vh;
  display: flex;
  background: var(--color-bg-page);
  position: relative;
  overflow: hidden;
}

.background-glass {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 15% 50%, rgba(0, 113, 227, 0.04), transparent 40%),
              radial-gradient(circle at 85% 30%, rgba(0, 113, 227, 0.03), transparent 40%);
  pointer-events: none;
}

/* ============================================================
   左侧品牌区
   ============================================================ */

.brand-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px;
  position: relative;
  z-index: 1;
}

.brand-content {
  max-width: 440px;
}

.brand-mark {
  width: 56px;
  height: 56px;
  color: var(--color-primary);
  margin-bottom: 32px;
}

.brand-title {
  font-size: 3.5rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  color: var(--color-text-primary);
  margin-bottom: 16px;
  line-height: 1.1;
}

.brand-tagline {
  font-size: 1.25rem;
  color: var(--color-text-secondary);
  margin-bottom: 56px;
  font-weight: 500;
  letter-spacing: -0.01em;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 16px;
  font-weight: 500;
  color: var(--color-text-regular);
}

.feature-icon {
  font-size: 24px;
  color: var(--color-primary);
}

/* ============================================================
   右侧表单区
   ============================================================ */

.form-section {
  flex: 0 0 520px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  background: var(--color-bg-container);
  border-left: 1px solid var(--color-border-light);
  box-shadow: -20px 0 40px rgba(0, 0, 0, 0.02);
  position: relative;
  z-index: 1;
}

.form-container {
  width: 100%;
  max-width: 380px;
}

.form-header {
  margin-bottom: 48px;
}

.form-greeting {
  font-size: 14px;
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.15em;
  margin-bottom: 12px;
  font-weight: 600;
}

.form-title {
  font-size: 2.25rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--color-text-primary);
}

/* ============================================================
   表单样式
   ============================================================ */

.login-form {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-regular);
}

.form-input {
  width: 100%;
  padding: 16px 20px;
  font-family: inherit;
  font-size: 16px;
  color: var(--color-text-primary);
  background: var(--color-bg-page);
  border: 1px solid transparent;
  border-radius: var(--radius-base);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.form-input::placeholder {
  color: var(--color-text-placeholder);
}

.form-input:focus {
  outline: none;
  background: var(--color-bg-container);
  border-color: var(--color-primary-light);
  box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.15);
}

.btn-submit {
  width: 100%;
  padding: 18px;
  font-family: inherit;
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
  background: var(--color-text-primary);
  border: none;
  border-radius: var(--radius-large);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  margin-top: 12px;
  letter-spacing: 0.02em;
}

.btn-submit:hover:not(:disabled) {
  background: #000000;
  transform: scale(0.98);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.btn-submit:active:not(:disabled) {
  transform: scale(0.96);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 加载动画 */
.loading-text {
  display: flex;
  gap: 6px;
  justify-content: center;
  align-items: center;
  height: 24px;
}

.loading-dot {
  width: 6px;
  height: 6px;
  background: currentColor;
  border-radius: 50%;
  animation: pulse 1.4s infinite;
}

.loading-dot:nth-child(2) { animation-delay: 0.2s; }
.loading-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes pulse {
  0%, 60%, 100% { transform: scale(0.8); opacity: 0.4; }
  30% { transform: scale(1.2); opacity: 1; }
}

/* ============================================================
   表单底部
   ============================================================ */

.form-footer {
  margin-top: 32px;
  text-align: center;
}

.register-link {
  font-size: 15px;
  color: var(--color-text-secondary);
}

.register-link .link {
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: none;
  transition: opacity 0.2s ease;
  margin-left: 4px;
}

.register-link .link:hover {
  opacity: 0.8;
}

/* ============================================================
   通知提示
   ============================================================ */

.notification {
  position: fixed;
  top: 32px;
  left: 50%;
  transform: translateX(-50%) translateY(-20px);
  padding: 16px 32px;
  background: var(--color-text-primary);
  color: var(--color-bg-container);
  border-radius: var(--radius-xl);
  font-size: 15px;
  font-weight: 500;
  opacity: 0;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  z-index: 1000;
  box-shadow: var(--shadow-dark);
}

.notification.show {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

.notification.error {
  background: var(--color-danger);
}

.notification.success {
  background: var(--color-success);
}

/* ============================================================
   响应式
   ============================================================ */

@media (max-width: 968px) {
  .login-page {
    flex-direction: column;
  }

  .brand-section {
    flex: 0 1 auto;
    padding: 60px 32px;
  }

  .brand-title {
    font-size: 2.5rem;
  }

  .form-section {
    flex: 1;
    padding: 60px 32px;
    border-left: none;
    border-top: 1px solid var(--color-border-light);
  }

  .form-container {
    max-width: 100%;
  }
}

/* 入场动画 */
.animate-in {
  animation: fadeUpIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  opacity: 0;
  transform: translateY(20px);
}

.form-container.animate-in {
  animation-delay: 0.2s;
}

@keyframes fadeUpIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
