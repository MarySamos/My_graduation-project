<template>
  <div class="page">
    <!-- 页面头部 -->
    <header class="page-header">
      <div>
        <p class="page-breadcrumb">系统管理 / 用户</p>
        <h1 class="page-title">用户管理</h1>
        <p class="page-subtitle">管理系统用户和权限</p>
      </div>
      <div class="header-actions">
        <button class="btn-minimal" @click="loadUsers" :disabled="loading">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M1 8a7 7 0 1 1 14 0A7 7 0 0 1 1 8z" />
            <path d="M8 4v4l3 3" />
          </svg>
          刷新
        </button>
      </div>
    </header>

    <!-- 统计卡片 -->
    <section class="stats-row">
      <div class="stat-card-mini animate-in">
        <span class="stat-label">总用户数</span>
        <span class="stat-value">{{ stats.total }}</span>
      </div>
      <div class="stat-card-mini animate-in">
        <span class="stat-label">活跃用户</span>
        <span class="stat-value">{{ stats.active }}</span>
      </div>
      <div class="stat-card-mini animate-in">
        <span class="stat-label">管理员</span>
        <span class="stat-value">{{ stats.admins }}</span>
      </div>
      <div class="stat-card-mini animate-in">
        <span class="stat-label">本周新增</span>
        <span class="stat-value">{{ stats.newThisWeek }}</span>
      </div>
    </section>

    <!-- 用户表格 -->
    <section class="table-section">
      <div class="table-card">
        <el-table :data="users" v-loading="loading" class="minimal-table">
          <el-table-column prop="id" label="ID" width="60" align="center" />
          <el-table-column prop="employee_id" label="工号" width="140" />
          <el-table-column prop="name" label="姓名" width="140" />
          <el-table-column prop="department" label="部门">
            <template #default="{ row }">
              <span class="department-tag">{{ row.department || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="role" label="角色" width="120">
            <template #default="{ row }">
              <span :class="['role-badge', `role-${row.role}`]">
                {{ getRoleName(row.role) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-switch
                v-model="row.is_active"
                @change="toggleStatus(row)"
                :active-color="getCssVar('--accent')"
              />
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" align="center" fixed="right">
            <template #default="{ row }">
              <button class="action-btn" @click="deleteUser(row)">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M2 5h12M5 5V3a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2M6 9v4M10 9v4M3 5h10v11a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V5z" />
                </svg>
              </button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const loading = ref(false)
const users = ref([])

const stats = computed(() => {
  const total = users.value.length
  const active = users.value.filter(u => u.is_active).length
  const admins = users.value.filter(u => u.role === 'admin').length
  const oneWeekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
  const newThisWeek = users.value.filter(u => new Date(u.created_at) > oneWeekAgo).length
  return { total, active, admins, newThisWeek }
})

const loadUsers = async () => {
  loading.value = true
  try {
    const res = await api.get('/api/v1/admin/users')
    users.value = res.data.users || res.data || []
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const toggleStatus = async (user) => {
  try {
    await api.put(`/api/v1/admin/users/${user.id}/status`, { is_active: user.is_active })
    ElMessage.success(user.is_active ? '已启用' : '已禁用')
  } catch (e) {
    ElMessage.error('操作失败')
    user.is_active = !user.is_active
  }
}

const deleteUser = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.name}" 吗？此操作不可撤销。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    await api.delete(`/api/v1/admin/users/${user.id}`)
    ElMessage.success('删除成功')
    loadUsers()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const getRoleName = (role) => {
  const names = {
    admin: '管理员',
    analyst: '分析师',
    user: '用户'
  }
  return names[role] || role
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getCssVar = (name) => {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}

onMounted(() => {
  loadUsers()
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

.header-actions {
  display: flex;
  gap: 12px;
}

/* 统计卡片 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card-mini {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 20px;
  border: 1px solid rgba(196, 164, 132, 0.08);
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}

.stat-value {
  display: block;
  font-size: 1.75rem;
  font-weight: 500;
  font-family: 'Playfair Display', Georgia, serif;
  color: var(--text-primary);
}

/* 表格区域 */
.table-section {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 24px;
  border: 1px solid rgba(196, 164, 132, 0.08);
}

.table-card {
  width: 100%;
}

.department-tag {
  display: inline-block;
  padding: 4px 10px;
  background: var(--bg-secondary);
  border-radius: 12px;
  font-size: 13px;
  color: var(--text-secondary);
}

.role-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.role-admin {
  background: rgba(196, 120, 106, 0.15);
  color: var(--error);
}

.role-analyst {
  background: rgba(196, 164, 132, 0.15);
  color: var(--accent);
}

.role-user {
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-btn:hover {
  color: var(--error);
  background: rgba(196, 120, 106, 0.1);
}

/* Element Plus 表格样式覆盖 */
:deep(.minimal-table) {
  font-family: 'DM Sans', sans-serif;
  color: var(--text-primary);
}

:deep(.minimal-table .el-table__header-wrapper) {
  border-radius: var(--radius-md) var(--radius-md) 0 0;
}

:deep(.minimal-table th.el-table__cell) {
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--bg-secondary);
}

:deep(.minimal-table td.el-table__cell) {
  border-bottom: 1px solid var(--bg-secondary);
}

:deep(.minimal-table tr:hover > td) {
  background: var(--bg-secondary) !important;
}

:deep(.minimal-table .el-table__empty-block) {
  background: var(--bg-card);
}

/* 响应式 */
@media (max-width: 1024px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .stats-row {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }
}
</style>
