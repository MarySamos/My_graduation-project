<template>
  <div class="page">
    <header class="page-header">
      <div>
        <p class="page-breadcrumb">数据分析 / 关联规则</p>
        <h1 class="page-title">关联规则发现</h1>
        <p class="page-subtitle">Apriori 算法挖掘</p>
      </div>
      <button class="btn-primary" @click="loadData" :disabled="loading">
        运行分析
      </button>
    </header>

    <section v-if="association?.rules" class="rules-list">
      <div v-for="(rule, idx) in association.rules" :key="idx" class="rule-card animate-in">
        <div class="rule-content">
          <span class="rule-antecedents">{{ rule.antecedents.join(' + ') }}</span>
          <span class="rule-arrow">→</span>
          <span class="rule-consequents">{{ rule.consequents.join(' + ') }}</span>
        </div>
        <div class="rule-metrics">
          <span>支持度: {{ (rule.support * 100).toFixed(1) }}%</span>
          <span>置信度: {{ (rule.confidence * 100).toFixed(1) }}%</span>
          <span class="rule-lift">提升度: {{ rule.lift.toFixed(2) }}</span>
        </div>
      </div>
    </section>

    <div v-else-if="association?.error" class="error-state">
      <p>{{ association.error }}</p>
    </div>

    <div v-else-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>正在挖掘关联规则...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const loading = ref(false)
const association = ref(null)

const loadData = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/v1/analysis/association?min_support=0.05&min_confidence=0.3')
    association.value = response.data
  } catch (error) {
    console.error('Failed to load association:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.rules-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.rule-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 20px;
  border: 1px solid rgba(196, 164, 132, 0.08);
}

.rule-content {
  font-size: 15px;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.rule-antecedents {
  color: var(--accent);
  font-weight: 500;
}

.rule-arrow {
  color: var(--text-tertiary);
}

.rule-consequents {
  color: var(--success);
  font-weight: 600;
}

.rule-metrics {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--text-tertiary);
}

.rule-lift {
  color: var(--warning);
  font-weight: 600;
}

.error-state {
  padding: 40px;
  text-align: center;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  color: var(--error);
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
