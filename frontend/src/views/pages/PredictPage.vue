<template>
  <div class="page">
    <header class="page-header">
      <div>
        <p class="page-breadcrumb">智能预测</p>
        <h1 class="page-title">客户转化预测</h1>
        <p class="page-subtitle">基于机器学习模型</p>
      </div>
    </header>

    <section class="predict-section">
      <div class="predict-card">
        <h3>输入客户信息</h3>

        <div class="form-grid">
          <div class="form-group">
            <label>年龄</label>
            <input v-model="form.age" type="number" placeholder="30-60" />
          </div>

          <div class="form-group">
            <label>职业</label>
            <select v-model="form.job">
              <option value="">请选择</option>
              <option value="admin">管理员</option>
              <option value="technician">技术人员</option>
              <option value="blue-collar">蓝领</option>
              <option value="retired">退休</option>
              <option value="student">学生</option>
            </select>
          </div>

          <div class="form-group">
            <label>婚姻状况</label>
            <select v-model="form.marital">
              <option value="">请选择</option>
              <option value="married">已婚</option>
              <option value="single">单身</option>
              <option value="divorced">离异</option>
            </select>
          </div>

          <div class="form-group">
            <label>教育水平</label>
            <select v-model="form.education">
              <option value="">请选择</option>
              <option value="primary">小学</option>
              <option value="secondary">中学</option>
              <option value="tertiary">大学</option>
            </select>
          </div>

          <div class="form-group">
            <label>账户余额</label>
            <input v-model="form.balance" type="number" placeholder="0-100000" />
          </div>

          <div class="form-group">
            <label>是否有房贷</label>
            <select v-model="form.housing">
              <option value="yes">是</option>
              <option value="no">否</option>
            </select>
          </div>
        </div>

        <button class="btn-primary btn-full" @click="predict" :disabled="loading">
          {{ loading ? '预测中...' : '开始预测' }}
        </button>
      </div>

        <div v-if="result" class="result-card animate-in">
          <h3>预测结果</h3>
          <div class="result-score">
            <div class="score-label">转化概率</div>
          <div class="score-value">{{ result.probability.toFixed(1) }}%</div>
          <div class="score-bar">
            <div class="score-fill" :style="{ width: result.probability + '%' }"></div>
          </div>
        </div>
        <div class="result-prediction">
          <span>预测结果：</span>
          <strong :class="result.prediction === 1 ? 'positive' : 'negative'">
            {{ result.prediction === 1 ? '可能转化' : '不太可能转化' }}
          </strong>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import api from '../../api'

const loading = ref(false)
const result = ref(null)

const form = reactive({
  age: '',
  job: '',
  marital: '',
  education: '',
  balance: '',
  housing: 'no'
})

const predict = async () => {
  loading.value = true
  result.value = null
  try {
    const payload = {
      age: Number(form.age) || 35,
      job: form.job || 'management',
      marital: form.marital || 'married',
      education: form.education || 'secondary',
      default_credit: 'no',
      balance: Number(form.balance) || 1000,
      housing: form.housing || 'no',
      loan: 'no',
      contact: 'cellular',
      day: 15,
      month: 'may',
      duration: 300,
      campaign: 2,
      pdays: -1,
      previous: 0,
      poutcome: 'unknown'
    }
    const response = await api.post('/api/v1/predict/single', payload)
    result.value = response.data
  } catch (error) {
    console.error('Predict failed:', error)
    alert('预测失败，请检查输入')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.predict-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.predict-card, .result-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 24px;
  border: 1px solid rgba(196, 164, 132, 0.08);
}

.predict-card h3, .result-card h3 {
  font-size: 1.25rem;
  margin-bottom: 20px;
  color: var(--text-primary);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 13px;
  color: var(--text-tertiary);
}

.form-group input,
.form-group select {
  padding: 12px 16px;
  background: var(--bg-primary);
  border: 1px solid var(--bg-secondary);
  border-radius: var(--radius-md);
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--accent);
}

.btn-full {
  width: 100%;
  padding: 14px;
}

.result-score {
  text-align: center;
  margin-bottom: 24px;
}

.score-label {
  font-size: 13px;
  color: var(--text-tertiary);
  margin-bottom: 12px;
}

.score-value {
  font-size: 3rem;
  font-weight: 600;
  font-family: 'Playfair Display', serif;
  color: var(--accent);
  margin-bottom: 16px;
}

.score-bar {
  height: 8px;
  background: var(--bg-secondary);
  border-radius: 4px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: var(--accent);
  transition: width 0.5s ease;
}

.result-prediction {
  text-align: center;
  font-size: 16px;
}

.result-predication strong.positive {
  color: var(--success);
}

.result-prediction strong.positive {
  color: var(--success);
}

.result-prediction strong.negative {
  color: var(--text-tertiary);
}
</style>
