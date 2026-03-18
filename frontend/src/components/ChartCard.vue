<template>
  <div class="chart-card">
    <div v-if="title || $slots.header" class="chart-header">
      <div class="header-left">
        <h3 v-if="title" class="chart-title">{{ title }}</h3>
        <p v-if="subtitle" class="chart-subtitle">{{ subtitle }}</p>
      </div>
      <div v-if="$slots.actions" class="header-actions">
        <slot name="actions"></slot>
      </div>
    </div>
    <div class="chart-body">
      <div ref="chartRef" class="chart-container" :style="{ height: computedHeight }"></div>
      <div v-if="loading" class="chart-loading">
        <div class="spinner"></div>
      </div>
      <EmptyState v-if="error" :title="error" />
      <EmptyState v-if="!loading && !error && isEmpty" title="暂无图表数据" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import EmptyState from './EmptyState.vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  option: {
    type: Object,
    required: true
  },
  height: {
    type: String,
    default: '300px'
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  isEmpty: {
    type: Boolean,
    default: false
  }
})

const chartRef = ref(null)
const computedHeight = computed(() => props.height)
let chartInstance = null

const initChart = () => {
  if (!chartRef.value) return

  // 销毁旧实例
  if (chartInstance) {
    chartInstance.dispose()
  }

  // 创建新实例
  chartInstance = echarts.init(chartRef.value)
  chartInstance.setOption(props.option, true)

  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
}

const handleResize = () => {
  chartInstance?.resize()
}

// 监听配置变化
watch(() => props.option, (newOption) => {
  if (chartInstance && newOption) {
    chartInstance.setOption(newOption, true)
  }
}, { deep: true })

onMounted(() => {
  nextTick(() => {
    initChart()
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})

defineExpose({
  resize: handleResize,
  getInstance: () => chartInstance
})
</script>

<style scoped>
.chart-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 24px;
  border: 1px solid rgba(196, 164, 132, 0.08);
  transition: all var(--transition-base);
}

.chart-card:hover {
  box-shadow: var(--shadow-soft);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  gap: 16px;
}

.header-left {
  flex: 1;
  min-width: 0;
}

.chart-title {
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-primary);
  margin: 0 0 4px 0;
  font-family: 'Playfair Display', Georgia, serif;
}

.chart-subtitle {
  font-size: 13px;
  color: var(--text-tertiary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.chart-body {
  position: relative;
}

.chart-container {
  width: 100%;
}

.chart-loading {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-card);
  border-radius: var(--radius-md);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 2px solid var(--bg-secondary);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
