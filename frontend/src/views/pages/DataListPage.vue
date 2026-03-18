<template>
  <div class="page">
    <header class="page-header">
      <div>
        <p class="page-breadcrumb">数据管理 / 数据列表</p>
        <h1 class="page-title">客户数据</h1>
        <p class="page-subtitle">浏览和管理客户信息</p>
      </div>
      <button class="btn-primary" @click="loadData" :disabled="loading">
        刷新
      </button>
    </header>

    <section class="data-section">
      <div class="table-controls">
        <input v-model="searchQuery" type="text" placeholder="搜索客户..." class="search-input" />
        <select v-model="pageSize" @change="loadData" class="page-select">
          <option :value="10">10 条/页</option>
          <option :value="20">20 条/页</option>
          <option :value="50">50 条/页</option>
        </select>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>工号</th>
              <th>年龄</th>
              <th>职业</th>
              <th>婚姻</th>
              <th>教育</th>
              <th>余额</th>
              <th>是否贷款</th>
              <th>结果</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredData" :key="item.id">
              <td>{{ item.id }}</td>
              <td>{{ item.age }}</td>
              <td>{{ item.job }}</td>
              <td>{{ item.marital }}</td>
              <td>{{ item.education }}</td>
              <td>{{ item.balance }}</td>
              <td>{{ item.housing === 'yes' ? '是' : '否' }}</td>
              <td>
                <span :class="['status-badge', item.y === 'yes' ? 'success' : 'neutral']">
                  {{ item.y === 'yes' ? '已转化' : '未转化' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination">
        <button @click="prevPage" :disabled="page === 1">上一页</button>
        <span>第 {{ page }} 页</span>
        <button @click="nextPage" :disabled="!hasMore">下一页</button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'

const loading = ref(false)
const data = ref([])
const page = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const hasMore = ref(true)

const filteredData = computed(() => {
  if (!searchQuery.value) return data.value
  const query = searchQuery.value.toLowerCase()
  return data.value.filter(item =>
    item.job?.toLowerCase().includes(query) ||
    item.marital?.toLowerCase().includes(query) ||
    item.id?.toString().includes(query)
  )
})

const loadData = async () => {
  loading.value = true
  try {
    const response = await api.get(`/api/v1/data/table/marketing_data?page=${page.value}&page_size=${pageSize.value}`)
    data.value = response.data.data || []
    hasMore.value = data.value.length === pageSize.value
  } catch (error) {
    console.error('Failed to load data:', error)
  } finally {
    loading.value = false
  }
}

const prevPage = () => {
  if (page.value > 1) {
    page.value--
    loadData()
  }
}

const nextPage = () => {
  if (hasMore.value) {
    page.value++
    loadData()
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.data-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.table-controls {
  display: flex;
  gap: 16px;
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  background: var(--bg-card);
  border: 1px solid var(--bg-secondary);
  border-radius: var(--radius-md);
  font-size: 14px;
}

.search-input:focus {
  outline: none;
  border-color: var(--accent);
}

.page-select {
  padding: 12px 16px;
  background: var(--bg-card);
  border: 1px solid var(--bg-secondary);
  border-radius: var(--radius-md);
  font-size: 14px;
}

.table-container {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid rgba(196, 164, 132, 0.08);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  padding: 16px;
  text-align: left;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-tertiary);
  background: var(--bg-secondary);
}

.data-table td {
  padding: 14px 16px;
  border-bottom: 1px solid var(--bg-secondary);
  font-size: 14px;
  color: var(--text-primary);
}

.data-table tr:hover {
  background: var(--bg-primary);
}

.status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.status-badge.success {
  background: rgba(122, 155, 106, 0.2);
  color: var(--success);
}

.status-badge.neutral {
  background: var(--bg-secondary);
  color: var(--text-tertiary);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
}

.pagination button {
  padding: 10px 20px;
  background: var(--bg-card);
  border: 1px solid var(--bg-secondary);
  border-radius: var(--radius-md);
  cursor: pointer;
}

.pagination button:hover:not(:disabled) {
  border-color: var(--accent);
  color: var(--accent);
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
