<template>
  <div class="page">
    <!-- 页面头部 -->
    <header class="page-header">
      <div>
        <p class="page-breadcrumb">数据分析 / 相关性分析</p>
        <h1 class="page-title">相关性热力图</h1>
        <p class="page-subtitle">探索变量之间的关联关系</p>
      </div>
      <div class="header-controls">
        <select v-model="method" @change="loadData" class="method-select">
          <option value="pearson">Pearson</option>
          <option value="spearman">Spearman</option>
          <option value="kendall">Kendall</option>
        </select>
        <button class="btn-primary" @click="loadData" :disabled="loading">
          {{ loading ? '分析中...' : '开始分析' }}
        </button>
      </div>
    </header>

    <!-- 热力图 -->
    <section v-if="correlation" class="chart-section">
      <div ref="heatmapRef" class="heatmap-chart"></div>
    </section>

    <!-- Top 相关性 -->
    <section v-if="correlation?.top_correlations" class="top-list">
      <h3 class="section-title">Top 相关性排序</h3>
      <div class="correlation-list">
        <div v-for="(c, i) in correlation.top_correlations.slice(0, 10)" :key="i" class="corr-item">
          <span class="corr-pair">{{ c.var1 }} ↔ {{ c.var2 }}</span>
          <div class="corr-bar-wrap">
            <div class="corr-bar" :style="{ width: Math.abs(c.correlation) * 100 + '%', background: c.correlation > 0 ? '#7A9B6A' : '#C4786A' }"></div>
          </div>
          <span class="corr-val" :style="{ color: c.correlation > 0 ? '#7A9B6A' : '#C4786A' }">{{ c.correlation }}</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import api from '../../api'
import * as echarts from 'echarts'

const loading = ref(false)
const method = ref('pearson')
const correlation = ref(null)
const heatmapRef = ref(null)
let chart = null

const loadData = async () => {
  loading.value = true
  try {
    const response = await api.get(`/api/v1/analysis/correlation?method=${method.value}`)
    correlation.value = response.data
    await nextTick()
    renderChart()
  } catch (error) {
    console.error('Failed to load correlation:', error)
  } finally {
    loading.value = false
  }
}

const renderChart = () => {
  if (!heatmapRef.value || !correlation.value) return
  chart = echarts.init(heatmapRef.value)
  const columns = correlation.value.columns

  chart.setOption({
    tooltip: {
      formatter: (p) => `${columns[p.value[0]]} ↔ ${columns[p.value[1]]}<br/>相关系数: <b>${p.value[2]}</b>`
    },
    grid: { top: 20, right: 60, bottom: 60, left: 100 },
    xAxis: {
      type: 'category',
      data: columns,
      axisLine: { lineStyle: { color: '#EDE8DC' } },
      axisLabel: { rotate: 45, fontSize: 11, color: '#A39E95' }
    },
    yAxis: {
      type: 'category',
      data: columns,
      axisLine: { lineStyle: { color: '#EDE8DC' } },
      axisLabel: { fontSize: 11, color: '#A39E95' }
    },
    visualMap: {
      min: -1, max: 1, calculable: true,
      orient: 'vertical', right: 20, top: 'center',
      inRange: { color: ['#C4786A', '#E8DCCA', '#FFFFFF', '#D4E8D4', '#7A9B6A'] },
      textStyle: { color: '#6B6560' }
    },
    series: [{
      type: 'heatmap',
      data: correlation.value.heatmap_data,
      label: { show: columns.length <= 8, fontSize: 10 },
      itemStyle: {
        borderColor: '#FFFEFA',
        borderWidth: 1
      }
    }]
  })
}

onMounted(() => {
  loadData()
})

onUnmounted(() => {
  chart?.dispose()
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

.header-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.method-select {
  padding: 10px 16px;
  font-family: 'DM Sans', sans-serif;
  font-size: 14px;
  color: var(--text-primary);
  background: var(--bg-card);
  border: 1px solid var(--bg-secondary);
  border-radius: var(--radius-md);
  cursor: pointer;
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

.chart-section {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 24px;
  border: 1px solid rgba(196, 164, 132, 0.08);
}

.heatmap-chart {
  height: 500px;
}

.top-list {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 24px;
  border: 1px solid rgba(196, 164, 132, 0.08);
}

.section-title {
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-primary);
  margin: 0 0 20px 0;
}

.correlation-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.corr-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  border-bottom: 1px solid var(--bg-primary);
}

.corr-item:last-child {
  border-bottom: none;
}

.corr-pair {
  width: 180px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.corr-bar-wrap {
  flex: 1;
  height: 6px;
  background: var(--bg-secondary);
  border-radius: 3px;
  overflow: hidden;
}

.corr-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.corr-val {
  width: 60px;
  text-align: right;
  font-size: 14px;
  font-weight: 600;
}
</style>
