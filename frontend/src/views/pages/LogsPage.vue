<template>
  <div class="page">
    <header class="page-header">
      <div>
        <p class="page-breadcrumb">系统管理 / 操作日志</p>
        <h1 class="page-title">操作日志</h1>
        <p class="page-subtitle">系统操作记录</p>
      </div>
      <button class="btn-primary" @click="loadData" :disabled="loading">
        刷新
      </button>
    </header>

    <section class="logs-section">
      <div v-if="logs.length === 0 && !loading" class="empty-state">
        <p>暂无日志记录</p>
      </div>

      <div v-else class="logs-list">
        <div v-for="log in logs" :key="log.id" class="log-item animate-in">
          <div class="log-time">{{ formatTime(log.created_at) }}</div>
          <div class="log-content">
            <div class="log-action">{{ log.action }}</div>
            <div class="log-user">用户: {{ log.user_name || '未知' }}</div>
          </div>
          <div class="log-ip">{{ log.ip_address || '-' }}</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const loading = ref(false)
const logs = ref([])

const loadData = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/v1/admin/logs')
    logs.value = response.data.logs || []
  } catch (error) {
    console.error('Failed to load logs:', error)
  } finally {
    loading.value = false
  }
}

const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.logs-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: var(--text-tertiary);
  background: var(--bg-card);
  border-radius: var(--radius-lg);
}

.logs-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.log-item {
  display: grid;
  grid-template-columns: 150px 1fr 120px;
  gap: 16px;
  background: var(--bg-card);
  border-radius: var(--radius-md);
  padding: 12px 16px;
  align-items: center;
  border: 1px solid rgba(196, 164, 132, 0.08);
}

.log-time {
  font-size: 12px;
  color: var(--text-tertiary);
  font-family: 'DM Sans', monospace;
}

.log-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.log-action {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.log-user {
  font-size: 12px;
  color: var(--text-tertiary);
}

.log-ip {
  font-size: 12px;
  color: var(--text-tertiary);
  text-align: right;
  font-family: 'DM Sans', monospace;
}
</style>
