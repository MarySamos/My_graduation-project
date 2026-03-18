<template>
  <div class="page">
    <header class="page-header">
      <div>
        <p class="page-breadcrumb">数据分析 / 特征分析</p>
        <h1 class="page-title">特征重要性</h1>
        <p class="page-subtitle">影响转化的关键因素</p>
      </div>
      <button class="btn-primary" @click="loadData" :disabled="loading">
        分析
      </button>
    </header>

    <section v-if="features" class="features-list">
      <div v-for="f in features.features" :key="f.name" class="feature-item animate-in">
        <span class="feature-name">{{ f.name }}</span>
        <div class="feature-bar-wrap">
          <div class="feature-bar" :style="{ width: (f.importance * 100) + '%' }"></div>
        </div>
        <span class="feature-value">{{ (f.importance * 100).toFixed(1) }}%</span>
      </div>
    </section>

    <div v-else-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>正在分析特征重要性...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const loading = ref(false)
const features = ref(null)

const loadData = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/v1/analysis/feature-importance')
    features.value = response.data
  } catch (error) {
    console.error('Failed to load features:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.features-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
  border: 1px solid rgba(196, 164, 132, 0.08);
}

.feature-name {
  width: 120px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.feature-bar-wrap {
  flex: 1;
  height: 8px;
  background: var(--bg-secondary);
  border-radius: 4px;
  overflow: hidden;
}

.feature-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--success));
  border-radius: 4px;
  transition: width 0.5s ease;
}

.feature-value {
  width: 60px;
  text-align: right;
  font-size: 14px;
  font-weight: 600;
  color: var(--accent);
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
