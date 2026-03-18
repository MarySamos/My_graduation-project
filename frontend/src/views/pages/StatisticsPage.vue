<template>
  <div class="page">
    <!-- 页面头部 -->
    <header class="page-header">
      <div>
        <p class="page-breadcrumb">数据分析 / 统计分析</p>
        <h1 class="page-title">描述性统计</h1>
        <p class="page-subtitle">查看所有数值列的统计指标</p>
      </div>
      <button class="btn-primary" @click="loadData" :disabled="loading">
        <span v-if="!loading">刷新数据</span>
        <span v-else>加载中...</span>
      </button>
    </header>

    <!-- 统计卡片网格 -->
    <section v-if="statistics" class="stats-grid">
      <div v-for="(stat, col) in statistics.statistics" :key="col" class="stat-card animate-in">
        <div class="card-header">
          <h3 class="card-title">{{ col }}</h3>
          <span class="card-badge">{{ stat.count }} 个数据点</span>
        </div>
        <div class="stat-metrics">
          <div class="metric-row">
            <span class="metric-label">均值</span>
            <span class="metric-value">{{ stat.mean }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">中位数</span>
            <span class="metric-value">{{ stat.median }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">标准差</span>
            <span class="metric-value">{{ stat.std }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">范围</span>
            <span class="metric-value">{{ stat.min }} ~ {{ stat.max }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">偏度</span>
            <span class="metric-value">{{ stat.skewness }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 加载状态 -->
    <div v-else-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>正在加载统计数据...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const loading = ref(false)
const statistics = ref(null)

const loadData = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/v1/analysis/statistics')
    statistics.value = response.data
  } catch (error) {
    console.error('Failed to load statistics:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 32px;
  padding-bottom: 40px;
}

.page-breadcrumb {
  font-size: 12px;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 8px;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 400;
  font-family: 'Playfair Display', Georgia, serif;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 0.875rem;
  color: var(--text-tertiary);
  margin: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.btn-primary {
  padding: 12px 24px;
  font-family: 'DM Sans', sans-serif;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-inverse);
  background: var(--text-primary);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-base);
}

.btn-primary:hover:not(:disabled) {
  background: var(--accent);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.stat-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 24px;
  border: 1px solid rgba(196, 164, 132, 0.08);
  transition: all var(--transition-base);
}

.stat-card:hover {
  box-shadow: var(--shadow-soft);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--bg-secondary);
}

.card-title {
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-primary);
  margin: 0;
}

.card-badge {
  font-size: 12px;
  padding: 4px 10px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  border-radius: 12px;
}

.stat-metrics {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px dashed var(--bg-secondary);
}

.metric-row:last-child {
  border-bottom: none;
}

.metric-label {
  font-size: 13px;
  color: var(--text-tertiary);
}

.metric-value {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  font-family: 'DM Sans', monospace;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: var(--text-tertiary);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 2px solid var(--bg-secondary);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
