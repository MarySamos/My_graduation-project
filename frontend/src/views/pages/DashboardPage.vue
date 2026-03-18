<template>
  <div class="page">
    <header class="page-header">
      <div>
        <p class="page-breadcrumb">数据概览</p>
        <h1 class="page-title">数据仪表盘</h1>
        <p class="page-subtitle">银行营销数据总览</p>
      </div>
      <button class="btn-primary" @click="loadData" :disabled="loading">
        刷新
      </button>
    </header>

    <!-- 统计卡片 -->
    <section class="stats-overview">
      <div class="stat-card-mini animate-in">
        <div class="stat-label">总客户数</div>
        <div class="stat-value">{{ stats.total_customers || '-' }}</div>
        <div class="stat-change positive">+12.5%</div>
      </div>
      <div class="stat-card-mini animate-in">
        <div class="stat-label">已转化</div>
        <div class="stat-value">{{ stats.converted || '-' }}</div>
        <div class="stat-change positive">转化率 {{ stats.conversion_rate || '-' }}%</div>
      </div>
      <div class="stat-card-mini animate-in">
        <div class="stat-label">平均余额</div>
        <div class="stat-value">{{ stats.avg_balance || '-' }}</div>
        <div class="stat-change">欧元</div>
      </div>
      <div class="stat-card-mini animate-in">
        <div class="stat-label">平均年龄</div>
        <div class="stat-value">{{ stats.avg_age || '-' }}</div>
        <div class="stat-change">岁</div>
      </div>
    </section>

    <!-- 图表区域 -->
    <section class="charts-section">
      <div class="chart-card animate-in">
        <h3>职业分布</h3>
        <div ref="jobChartRef" class="chart-container"></div>
      </div>
      <div class="chart-card animate-in">
        <h3>婚姻状况</h3>
        <div ref="maritalChartRef" class="chart-container"></div>
      </div>
      <div class="chart-card animate-in">
        <h3>教育水平</h3>
        <div ref="eduChartRef" class="chart-container"></div>
      </div>
      <div class="chart-card animate-in">
        <h3>联系结果</h3>
        <div ref="outcomeChartRef" class="chart-container"></div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import api from '../../api'
import * as echarts from 'echarts'

const loading = ref(false)
const stats = ref({})

const jobChartRef = ref(null)
const maritalChartRef = ref(null)
const eduChartRef = ref(null)
const outcomeChartRef = ref(null)

const loadData = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/v1/dashboard/stats')
    stats.value = response.data
  } catch (error) {
    console.error('Failed to load stats:', error)
  } finally {
    loading.value = false
  }
}

const renderCharts = () => {
  // 简化版图表，实际数据需要从 API 获取
  if (jobChartRef.value) {
    const chart = echarts.init(jobChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        data: [
          { value: 1048, name: '管理员' },
          { value: 1921, name: '技术人员' },
          { value: 2678, name: '蓝领' }
        ]
      }]
    })
  }
}

onMounted(async () => {
  await loadData()
  await nextTick()
  renderCharts()
})
</script>

<style scoped>
.stats-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card-mini {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 24px;
  border: 1px solid rgba(196, 164, 132, 0.08);
  text-align: center;
}

.stat-label {
  font-size: 12px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 12px;
}

.stat-value {
  font-size: 2rem;
  font-weight: 600;
  font-family: 'Playfair Display', serif;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.stat-change {
  font-size: 13px;
  color: var(--text-tertiary);
}

.stat-change.positive {
  color: var(--success);
}

.charts-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.chart-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 24px;
  border: 1px solid rgba(196, 164, 132, 0.08);
}

.chart-card h3 {
  font-size: 1rem;
  font-weight: 500;
  margin-bottom: 20px;
  color: var(--text-primary);
}

.chart-container {
  height: 200px;
}
</style>
