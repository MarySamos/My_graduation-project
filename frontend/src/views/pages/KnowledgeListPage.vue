<template>
  <div class="page">
    <header class="page-header">
      <div>
        <p class="page-breadcrumb">知识库 / 文档列表</p>
        <h1 class="page-title">知识文档</h1>
        <p class="page-subtitle">已上传的文档列表</p>
      </div>
      <button class="btn-primary" @click="loadData" :disabled="loading">
        刷新
      </button>
    </header>

    <section class="docs-section">
      <div v-if="docs.length === 0 && !loading" class="empty-state">
        <p>还没有上传任何文档</p>
      </div>

      <div v-else class="docs-list">
        <div v-for="doc in docs" :key="doc.id" class="doc-card animate-in">
          <div class="doc-icon">📄</div>
            <div class="doc-info">
              <div class="doc-title">{{ doc.title }}</div>
              <div class="doc-meta">
                <span>{{ (doc.meta_data && doc.meta_data.chunk_count) || 1 }} 个片段</span>
                <span>{{ (doc.file_type || '').toUpperCase() }}</span>
                <span>{{ doc.has_embedding ? '已向量化' : '未向量化' }}</span>
              </div>
            </div>
            <button class="doc-delete" @click="deleteDoc(doc.id)">删除</button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const loading = ref(false)
const docs = ref([])

const loadData = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/v1/knowledge/list')
    docs.value = response.data.data || []
  } catch (error) {
    console.error('Failed to load docs:', error)
  } finally {
    loading.value = false
  }
}

const deleteDoc = async (id) => {
  if (!confirm('确定要删除这个文档吗？')) return
  try {
    await api.delete(`/api/v1/knowledge/${id}`)
    loadData()
  } catch (error) {
    console.error('Failed to delete doc:', error)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.docs-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: var(--text-tertiary);
  background: var(--bg-card);
  border-radius: var(--radius-lg);
}

.docs-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.doc-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
  border: 1px solid rgba(196, 164, 132, 0.08);
}

.doc-icon {
  font-size: 24px;
}

.doc-info {
  flex: 1;
}

.doc-title {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.doc-meta {
  font-size: 12px;
  color: var(--text-tertiary);
}

.doc-meta span {
  margin-right: 16px;
}

.doc-delete {
  padding: 8px 16px;
  background: transparent;
  border: 1px solid var(--bg-secondary);
  border-radius: var(--radius-md);
  color: var(--text-tertiary);
  cursor: pointer;
  transition: all var(--transition-base);
}

.doc-delete:hover {
  border-color: var(--error);
  color: var(--error);
}
</style>
