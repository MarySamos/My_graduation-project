<template>
  <div class="page">
    <header class="page-header">
      <div>
        <p class="page-breadcrumb">数据分析 / 漏斗分析</p>
        <h1 class="page-title">营销漏斗</h1>
        <p class="page-subtitle">客户转化流程分析</p>
      </div>
      <button class="btn-primary" @click="loadData" :disabled="loading">
        加载数据
      </button>
    </header>

    <section v-if="funnel" class="funnel-section">
      <div class="funnel-summary">
        <div class="summary-card">
          <div class="summary-label">总客户数</div>
          <div class="summary-value">{{ funnel.total_customers }}</div>
        </div>
        <div class="summary-card">
          <div class="summary-label">转化客户</div>
          <div class="summary-value">{{ funnel.total_converted }}</div>
        </div>
        <div class="summary-card">
          <div class="summary-label">总转化率</div>
          <div class="summary-value">{{ funnel.overall_conversion_rate }}%</div>
        </div>
      </div>

      <div class="funnel-stages">
        <div v-for="(stage, idx) in funnel.stages" :key="idx" class="funnel-stage">
          <div class="stage-bar-wrap">
            <div class="stage-bar" :style="{ width: stage.rate + '%', background: funnelColors[idx] }"></div>
          </div>
          <div class="stage-info">
            <span class="stage-name">{{ stage.name }}</span>
            <span class="stage-count">{{ stage.count }} 人</span>
            <span class="stage-rate">{{ stage.rate }}%</span>
          </div>
          <div v-if="idx > 0" class="drop-badge">流失 {{ stage.drop_rate }}%</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const loading = ref(false)
const funnel = ref(null)
const funnelColors = ['#C4A484', '#7A9B6A', '#D4A85A', '#C4786A', '#7A9CB8']

const loadData = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/v1/analysis/funnel')
    funnel.value = response.data
  } catch (error) {
    console.error('Failed to load funnel data:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.funnel-section {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.funnel-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.summary-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 24px;
  text-align: center;
  border: 1px solid rgba(196, 164, 132, 0.08);
}

.summary-label {
  font-size: 12px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  margin-bottom: 12px;
}

.summary-value {
  font-size: 2rem;
  font-weight: 600;
  font-family: 'Playfair Display', serif;
  color: var(--text-primary);
}

.funnel-stages {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.funnel-stage {
  position: relative;
}

.stage-bar-wrap {
  height: 48px;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.stage-bar {
  height: 100%;
  border-radius: var(--radius-md);
  transition: width 0.8s ease;
}

.stage-info {
  position: absolute;
  top: 0;
  left: 16px;
  right: 16px;
  height: 48px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stage-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-inverse);
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
  min-width: 120px;
}

.stage-count {
  font-size: 13px;
  color: rgba(255,255,255,0.9);
}

.stage-rate {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-inverse);
  margin-left: auto;
}

.drop-badge {
  position: absolute;
  right: -8px;
  top: -8px;
  background: var(--error);
  color: var(--text-inverse);
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
}
</style>
