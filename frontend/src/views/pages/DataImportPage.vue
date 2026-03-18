<template>
  <div class="page">
    <header class="page-header">
      <div>
        <p class="page-breadcrumb">数据管理 / 数据导入</p>
        <h1 class="page-title">导入数据</h1>
        <p class="page-subtitle">上传 CSV 或 Excel 文件</p>
      </div>
    </header>

    <section class="import-section">
      <div class="upload-area" :class="{ 'drag-over': isDragOver }"
           @dragover.prevent="isDragOver = true"
           @dragleave.prevent="isDragOver = false"
           @drop.prevent="handleDrop">
        <div class="upload-icon">📁</div>
        <h3>拖放文件到这里</h3>
        <p>或点击选择文件</p>
        <input type="file" ref="fileInput" @change="handleFileSelect" accept=".csv,.xlsx,.xls" class="hidden" />
        <button class="btn-primary" @click="$refs.fileInput.click()">选择文件</button>
      </div>

      <div v-if="selectedFile" class="file-info">
        <div class="file-name">{{ selectedFile.name }}</div>
        <div class="file-size">{{ (selectedFile.size / 1024).toFixed(2) }} KB</div>
      </div>

      <div v-if="uploadStatus" class="upload-status" :class="uploadStatus.type">
        {{ uploadStatus.message }}
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../../api'

const isDragOver = ref(false)
const selectedFile = ref(null)
const fileInput = ref(null)
const uploadStatus = ref(null)

const handleDrop = (e) => {
  isDragOver.value = false
  const files = e.dataTransfer.files
  if (files.length > 0) {
    selectedFile.value = files[0]
    uploadFile()
  }
}

const handleFileSelect = (e) => {
  const files = e.target.files
  if (files.length > 0) {
    selectedFile.value = files[0]
    uploadFile()
  }
}

const uploadFile = async () => {
  if (!selectedFile.value) return

  const formData = new FormData()
  formData.append('file', selectedFile.value)

  uploadStatus.value = { type: 'info', message: '正在上传...' }

  try {
    const response = await api.post('/api/v1/data/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    uploadStatus.value = { type: 'success', message: '导入成功！' }
  } catch (error) {
    uploadStatus.value = { type: 'error', message: '导入失败：' + (error.response?.data?.detail || error.message) }
  }
}
</script>

<style scoped>
.import-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.upload-area {
  background: var(--bg-card);
  border: 2px dashed var(--bg-secondary);
  border-radius: var(--radius-xl);
  padding: 60px;
  text-align: center;
  transition: all var(--transition-base);
}

.upload-area.drag-over {
  border-color: var(--accent);
  background: var(--accent-subtle);
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.upload-area h3 {
  font-size: 1.25rem;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.upload-area p {
  color: var(--text-tertiary);
  margin-bottom: 20px;
}

.hidden {
  display: none;
}

.file-info {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid rgba(196, 164, 132, 0.08);
}

.file-name {
  font-weight: 500;
  color: var(--text-primary);
}

.file-size {
  font-size: 13px;
  color: var(--text-tertiary);
}

.upload-status {
  padding: 16px 20px;
  border-radius: var(--radius-lg);
  text-align: center;
}

.upload-status.info {
  background: var(--info);
  color: var(--text-inverse);
}

.upload-status.success {
  background: var(--success);
  color: var(--text-inverse);
}

.upload-status.error {
  background: var(--error);
  color: var(--text-inverse);
}
</style>
