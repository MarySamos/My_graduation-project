<template>
  <div class="page">
    <!-- 页面头部 -->
    <header class="page-header">
      <div>
        <p class="page-breadcrumb">数据分析 / 时间趋势</p>
        <h1 class="page-title">时间序列分析</h1>
        <p class="page-subtitle">营销数据的月度趋势与预测</p>
      </div>
      <button class="btn-primary" @click="loadData" :disabled="loading">
        {{ loading ? '加载中...' : '刷新数据' }}
      </button>
    </header>

    <!-- 统计摘要 -->
    <section v-if="timeSeries?.summary" class="summary-cards">
      <div class="summary-card">
        <span class="summary-icon">📊</span>
        <div class="summary-content">
          <span class="summary-value">{{ timeSeries.summary.peak_month }}</span>
          <span class="summary-label">营销高峰月</span>
        </div>
      </div>
      <div class="summary-card">
        <span class="summary-icon">📈</span>
        <div class="summary-content">
          <span class="summary-value">{{ timeSeries.summary.peak_count?.toLocaleString() }}</span>
          <span class="summary-label">高峰客户数</span>
        </div>
      </div>
      <div class="summary-card">
        <span class="summary-icon">🎯</span>
        <div class="summary-content">
          <span class="summary-value">{{ timeSeries.summary.best_conversion_month }}</span>
          <span class="summary-label">最佳转化月</span>
        </div>
      </div>
      <div class="summary-card">
        <span class="summary-icon">💰</span>
        <div class="summary-content">
          <span class="summary-value">{{ timeSeries.summary.best_conversion_rate }}%</span>
          <span class="summary-label">最高转化率</span>
        </div>
      </div>
    </section>

    <!-- 图表区域 -->
    <section class="charts-row">
      <div class="chart-card">
        <h3 class="chart-title">客户数量趋势</h3>
        <div ref="trendChartRef" class="chart-container"></div>
      </div>
      <div class="chart-card">
        <h3 class="chart-title">转化率趋势</h3>
        <div ref="conversionChartRef" class="chart-container"></div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import api from '../../api'
import * as echarts from 'echarts'

const loading = ref(false)
const timeSeries = ref(null)
const trendChartRef = ref(null)
const conversionChartRef = ref(null)
let trendChart = null
let conversionChart = null

const loadData = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/v1/analysis/time-series')
    timeSeries.value = response.data
    await nextTick()
    renderCharts()
  } catch (error) {
    console.error('Failed to load time series:', error)
  } finally {
    loading.value = false
  }
}

const renderCharts = () => {
  if (!timeSeries.value) return

  // 趋势图
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
      grid: { top: 30, right: 30, bottom: 40, left: 60 },
      xAxis: {
        type: 'category',
        data: timeSeries.value.months,
        axisLine: { lineStyle: { color: '#EDE8DC' } },
        axisLabel: { color: '#A39E95' }
      },
      yAxis: {
        type: 'value',
        name: '客户数',
        axisLine: { lineStyle: { color: '#EDE8DC' } },
        splitLine: { lineStyle: { color: '#F5F2EB' } }
      },
      series: [
        {
          name: '客户数',
          type: 'bar',
          data: timeSeries.value.customer_count.values,
          itemStyle: { color: '#C4A484', borderRadius: [6, 6, 0, 0] }
        },
        {
          name: '移动平均',
          type: 'line',
          data: timeSeries.value.customer_count.moving_avg,
          smooth: true,
          lineStyle: { color: '#7A9CB8', width: 3 },
          itemStyle: { color: '#7A9CB8' }
        }
      ]
    })
  }

  // 转化率图
  if (conversionChartRef.value) {
    conversionChart = echarts.init(conversionChartRef.value)
    conversionChart.setOption({
      grid: { top: 30, right: 30, bottom: 40, left: 60 },
      xAxis: {
        type: 'category',
        data: timeSeries.value.months,
        axisLine: { lineStyle: { color: '#EDE8DC' } },
        axisLabel: { color: '#A39E95' }
      },
      yAxis: {
        type: 'value',
        name: '转化率 (%)',
        axisLine: { lineStyle: { color: '#EDE8DC' } },
        splitLine: { lineStyle: { color: '#F5F2EB' } },
        axisLabel: { formatter: '{value}%' }
      },
      series: [
        {
          name: '转化率',
          type: 'line',
          data: timeSeries.value.conversion_rate.values,
          smooth: true,
          areaStyle: { color: 'rgba(122, 155, 106, 0.15)' },
          lineStyle: { color: '#7A9B6A', width: 3 },
          itemStyle: { color: '#7A9B6A' }
        }
      ]
    })
  }
}

onMounted(() => {
  loadData()
})

onUnmounted(() => {
  trendChart?.dispose()
  conversionChart?.dispose()
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

.summary-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.summary-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  border: 1px solid rgba(196, 164, 132, 0.08);
}

.summary-icon {
  font-size: 24px;
}

.summary-value {
  display: block;
  font-size: 1.25rem;
  font-family: 'Playfair Display', Georgia, serif;
  font-weight: 500;
  color: var(--text-primary);
}

.summary-label {
  font-size: 12px;
  color: var(--text-tertiary);
}

.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.chart-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 24px;
  border: 1px solid rgba(196, 164, 132, 0.08);
}

.chart-title {
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.chart-container {
  height: 280px;
}

@media (max-width: 768px) {
  .summary-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-row {
    grid-template-columns: 1fr;
  }
}
</style>
