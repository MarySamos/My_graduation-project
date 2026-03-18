<template>
  <div class="page">
    <!-- 页面头部 -->
    <header class="page-header">
      <div>
        <p class="page-breadcrumb">数据分析 / 客户聚类</p>
        <h1 class="page-title">客户画像分析</h1>
        <p class="page-subtitle">基于 K-Means 算法的客户分群</p>
      </div>
    </header>

    <!-- 控制栏 -->
    <section class="control-bar">
      <div class="control-group">
        <label>聚类数量</label>
        <select v-model="clusterCount" class="control-select">
          <option :value="null">自动推荐</option>
          <option v-for="n in 8" :key="n" :value="n + 1">{{ n + 1 }} 类</option>
        </select>
      </div>
      <button class="btn-primary" @click="runClustering" :disabled="loading">
        {{ loading ? '分析中...' : '开始聚类' }}
      </button>
    </section>

    <!-- 聚类结果 -->
    <section v-if="clustering" class="results-section">
      <!-- 指标 -->
      <div class="metrics-row">
        <div class="metric-card">
          <span class="metric-value">{{ clustering.n_clusters }}</span>
          <span class="metric-label">聚类数量</span>
        </div>
        <div class="metric-card">
          <span class="metric-value">{{ clustering.silhouette_score }}</span>
          <span class="metric-label">轮廓系数</span>
        </div>
      </div>

      <!-- 客户画像卡片 -->
      <div class="profiles-grid">
        <div v-for="profile in clustering.cluster_profiles" :key="profile.cluster_id" class="profile-card animate-in">
          <div class="profile-header" :style="{ background: getProfileColor(profile.cluster_id) }">
            <span class="profile-id">群体 {{ profile.cluster_id + 1 }}</span>
            <span class="profile-label">{{ profile.label }}</span>
          </div>
          <div class="profile-body">
            <div class="profile-stat">
              <span>规模</span>
              <strong>{{ profile.size }} ({{ profile.percentage }}%)</strong>
            </div>
            <div class="profile-stat">
              <span>转化率</span>
              <strong>{{ profile.conversion_rate }}%</strong>
            </div>
            <div class="profile-stat">
              <span>主要职业</span>
              <strong>{{ profile.dominant_job }}</strong>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../../api'

const loading = ref(false)
const clusterCount = ref(null)
const clustering = ref(null)

const runClustering = async () => {
  loading.value = true
  try {
    const response = await api.post('/api/v1/analysis/clustering', {
      n_clusters: clusterCount.value,
      max_k: 10
    })
    clustering.value = response.data
  } catch (error) {
    console.error('Clustering failed:', error)
  } finally {
    loading.value = false
  }
}

const getProfileColor = (id) => {
  const colors = [
    'linear-gradient(135deg, #C4A484 0%, #A68A6E 100%)',
    'linear-gradient(135deg, #7A9B6A 0%, #5A7B4A 100%)',
    'linear-gradient(135deg, #7A9CB8 0%, #5A7B88 100%)',
    'linear-gradient(135deg, #D4A85A 0%, #B48A3A 100%)',
    'linear-gradient(135deg, #C4786A 0%, #94664A 100%)',
    'linear-gradient(135deg, #8B7BA8 0%, #6B5B78 100%)',
    'linear-gradient(135deg, #9BA68A 0%, #7B8646 100%)',
    'linear-gradient(135deg, #A68A7A 0%, #866A6A 100%)'
  ]
  return colors[id % colors.length]
}
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

.control-bar {
  display: flex;
  gap: 16px;
  align-items: center;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.control-group label {
  font-size: 14px;
  color: var(--text-secondary);
}

.control-select {
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

/* 结果展示 */
.metrics-row {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.metric-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 20px 24px;
  border: 1px solid rgba(196, 164, 132, 0.08);
  text-align: center;
}

.metric-value {
  display: block;
  font-size: 1.5rem;
  font-family: 'Playfair Display', Georgia, serif;
  font-weight: 500;
  color: var(--text-primary);
}

.metric-label {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 4px;
}

.profiles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}

.profile-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid rgba(196, 164, 132, 0.08);
  transition: all var(--transition-base);
}

.profile-card:hover {
  box-shadow: var(--shadow-soft);
  transform: translateY(-2px);
}

.profile-header {
  padding: 20px 24px;
  color: white;
}

.profile-id {
  font-size: 13px;
  opacity: 0.9;
}

.profile-label {
  font-size: 16px;
  font-weight: 500;
  margin-top: 4px;
}

.profile-body {
  padding: 20px 24px;
}

.profile-stat {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid var(--bg-primary);
}

.profile-stat:last-child {
  border-bottom: none;
}

.profile-stat span {
  font-size: 13px;
  color: var(--text-tertiary);
}

.profile-stat strong {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}
</style>
