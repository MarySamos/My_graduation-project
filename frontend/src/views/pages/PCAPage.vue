<template>
  <div class="page">
    <header class="page-header">
      <div>
        <p class="page-breadcrumb">数据分析 / PCA 降维</p>
        <h1 class="page-title">PCA 降维可视化</h1>
        <p class="page-subtitle">主成分分析</p>
      </div>
      <button class="btn-primary" @click="loadData" :disabled="loading">
        运行 PCA
      </button>
    </header>

    <section v-if="pca" class="pca-section">
      <div class="components-summary">
        <div v-for="comp in pca.components" :key="comp.component" class="component-card">
          <div class="component-label">{{ comp.component }}</div>
          <div class="component-value">{{ (comp.variance_ratio * 100).toFixed(1) }}%</div>
          <div class="component-desc">方差解释率</div>
        </div>
        <div class="component-card">
          <div class="component-label">总计</div>
          <div class="component-value">{{ (pca.total_variance_explained * 100).toFixed(1) }}%</div>
          <div class="component-desc">总方差解释率</div>
        </div>
      </div>

      <div ref="chartRef" class="chart-area"></div>
    </section>

    <div v-else-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>正在计算 PCA...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import api from '../../api'
import * as echarts from 'echarts'

const loading = ref(false)
const pca = ref(null)
const chartRef = ref(null)

const loadData = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/v1/analysis/pca')
    pca.value = response.data
    await nextTick()
    renderChart()
  } catch (error) {
    console.error('Failed to load PCA:', error)
  } finally {
    loading.value = false
  }
}

const renderChart = () => {
  if (!chartRef.value || !pca.value) return
  const chart = echarts.init(chartRef.value)
  const yesData = pca.value.scatter_data.filter(p => p.label === 'yes').map(p => [p.x, p.y])
  const noData = pca.value.scatter_data.filter(p => p.label === 'no').map(p => [p.x, p.y])

  chart.setOption({
    tooltip: {
      formatter: (p) => {
        const label = p.seriesName.includes('已转化') ? '已转化' : '未转化'
        return `${label}<br/>PC1: ${p.data[0].toFixed(3)}<br/>PC2: ${p.data[1].toFixed(3)}`
      }
    },
    legend: {
      data: ['已转化', '未转化'],
      top: 0
    },
    grid: { top: 40, right: 20, bottom: 50, left: 60 },
    xAxis: {
      name: `PC1 (${(pca.value.components[0]?.variance_ratio * 100).toFixed(1)}%)`,
      type: 'value'
    },
    yAxis: {
      name: `PC2 (${(pca.value.components[1]?.variance_ratio * 100).toFixed(1)}%)`,
      type: 'value'
    },
    series: [
      {
        name: '已转化',
        type: 'scatter',
        data: yesData,
        symbolSize: 8,
        itemStyle: { color: '#7A9B6A' }
      },
      {
        name: '未转化',
        type: 'scatter',
        data: noData,
        symbolSize: 6,
        itemStyle: { color: '#C4A484' }
      }
    ]
  })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.pca-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.components-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.component-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 20px;
  text-align: center;
  border: 1px solid rgba(196, 164, 132, 0.08);
}

.component-label {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-bottom: 8px;
}

.component-value {
  font-size: 1.5rem;
  font-weight: 600;
  font-family: 'Playfair Display', serif;
  color: var(--accent);
  margin-bottom: 4px;
}

.component-desc {
  font-size: 12px;
  color: var(--text-tertiary);
}

.chart-area {
  height: 400px;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 20px;
  border: 1px solid rgba(196, 164, 132, 0.08);
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
