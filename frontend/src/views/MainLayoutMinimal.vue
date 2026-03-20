<template>
  <div class="main-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-icon">
          <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="20" cy="20" r="18" stroke="currentColor" stroke-width="1.5" opacity="0.4"/>
            <circle cx="20" cy="20" r="12" stroke="currentColor" stroke-width="1.5" opacity="0.6"/>
            <circle cx="20" cy="20" r="6" fill="currentColor" opacity="0.9"/>
          </svg>
        </div>
        <span class="brand-name">BankAgent</span>
      </div>

      <nav class="sidebar-nav">
        <!-- 主菜单 -->
        <template v-for="item in navItems" :key="item.path">
          <!-- 有子菜单的项 -->
          <div v-if="item.children" class="nav-group">
            <div class="nav-item nav-group-header" @click="toggleGroup(item.path)">
              <component :is="item.icon" class="nav-icon" />
              <span class="nav-label">{{ item.label }}</span>
              <svg class="nav-arrow" :class="{ expanded: expandedGroups[item.path] }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </div>
            <div v-show="expandedGroups[item.path]" class="nav-submenu">
              <router-link
                v-for="child in item.children"
                :key="child.path"
                :to="child.path"
                class="nav-item nav-child"
                :class="{ active: isActive(child.path) }"
              >
                <span class="nav-label">{{ child.label }}</span>
              </router-link>
            </div>
          </div>
          <!-- 普通菜单项 -->
          <router-link
            v-else
            :to="item.path"
            class="nav-item"
            :class="{ active: isActive(item.path) }"
          >
            <component :is="item.icon" class="nav-icon" />
            <span class="nav-label">{{ item.label }}</span>
          </router-link>
        </template>

        <!-- 管理功能菜单 - 仅管理员可见 -->
        <template v-if="isAdmin" v-for="item in adminNavItems" :key="item.path">
          <div class="nav-group">
            <div class="nav-item nav-group-header" @click="toggleGroup(item.path)">
              <component :is="item.icon" class="nav-icon" />
              <span class="nav-label">{{ item.label }}</span>
              <svg class="nav-arrow" :class="{ expanded: expandedGroups[item.path] }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </div>
            <div v-show="expandedGroups[item.path]" class="nav-submenu">
              <router-link
                v-for="child in item.children"
                :key="child.path"
                :to="child.path"
                class="nav-item nav-child"
                :class="{ active: isActive(child.path) }"
              >
                <span class="nav-label">{{ child.label }}</span>
              </router-link>
            </div>
          </div>
        </template>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">{{ userName?.charAt(0) || 'U' }}</div>
          <div class="user-details">
            <p class="user-name">{{ userName || '用户' }}</p>
            <p class="user-role">{{ userRole || '普通用户' }}</p>
          </div>
        </div>
        <button class="logout-btn" @click="handleLogout" title="退出登录">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12h-9"/>
          </svg>
        </button>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
      <div class="content-wrapper">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ChatDotRound,
  DataAnalysis,
  Document,
  FolderOpened,
  TrendCharts,
  Histogram,
  Connection,
  Grid,
  Promotion,
  Setting,
  User,
  Notebook,
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const userName = ref('')
const userRole = ref('')
const isAdmin = ref(false)

const expandedGroups = ref({
  '/analysis': true,
  '/data': false,
  '/knowledge': false,
  '/admin': false,
})

const navItems = ref([
  {
    path: '/dashboard',
    label: '仪表盘',
    icon: TrendCharts,
  },
  {
    path: '/chat',
    label: '智能对话',
    icon: ChatDotRound,
  },
  {
    path: '/analysis',
    label: '数据分析',
    icon: DataAnalysis,
    children: [
      { path: '/analysis/statistics', label: '描述性统计' },
      { path: '/analysis/correlation', label: '相关性分析' },
      { path: '/analysis/clustering', label: '客户聚类' },
      { path: '/analysis/features', label: '特征重要性' },
      { path: '/analysis/association', label: '关联规则' },
      { path: '/analysis/pca', label: 'PCA 降维' },
      { path: '/analysis/timeseries', label: '时间趋势' },
      { path: '/analysis/funnel', label: '漏斗分析' },
    ]
  },
  {
    path: '/data',
    label: '数据管理',
    icon: FolderOpened,
    children: [
      { path: '/data/list', label: '数据列表' },
      { path: '/data/import', label: '数据导入' },
    ]
  },
  {
    path: '/knowledge',
    label: '知识库',
    icon: Document,
    children: [
      { path: '/knowledge/list', label: '文档列表' },
      { path: '/knowledge/upload', label: '上传文档' },
    ]
  },
  {
    path: '/predict',
    label: '智能预测',
    icon: TrendCharts,
  },
])

// 管理功能菜单
const adminNavItems = [
  {
    path: '/admin',
    label: '系统管理',
    icon: Setting,
    children: [
      { path: '/admin/users', label: '用户管理' },
      { path: '/logs', label: '操作日志' },
    ]
  }
]

const isActive = (path) => route.path === path || route.path.startsWith(path + '/')

const toggleGroup = (path) => {
  expandedGroups.value[path] = !expandedGroups.value[path]
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  localStorage.removeItem('userId')
  router.push('/login')
  ElMessage.success('已退出登录')
}

onMounted(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    const user = JSON.parse(userStr)
    userName.value = user.name
    userRole.value = user.role === 'admin' ? '管理员' : user.role === 'analyst' ? '分析师' : '普通用户'
    isAdmin.value = user.role === 'admin'
  }
})
</script>

<style scoped>
/* ============================================================
   布局结构
   ============================================================ */

.main-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: var(--color-bg-page);
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
}

/* ============================================================
   侧边栏
   ============================================================ */

.sidebar {
  width: 280px;
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-right: 1px solid var(--color-border-light);
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 10;
  overflow-y: auto;
}

.sidebar-brand {
  padding: 36px 24px 24px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-icon {
  width: 32px;
  height: 32px;
  color: var(--color-primary);
}

.brand-name {
  font-size: 1.35rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--color-text-primary);
}

/* 导航 */
.sidebar-nav {
  flex: 1;
  padding: 8px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.nav-group {
  display: flex;
  flex-direction: column;
}

.nav-group-header {
  cursor: pointer;
}

.nav-submenu {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-left: 36px;
  margin-top: 4px;
  margin-bottom: 8px;
}

.nav-child {
  padding: 8px 16px;
  font-size: 14px;
  border-radius: 8px;
}

.nav-arrow {
  width: 16px;
  height: 16px;
  margin-left: auto;
  transition: transform 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.nav-arrow.expanded {
  transform: rotate(180deg);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 10px;
  color: var(--color-text-regular);
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background: rgba(0, 0, 0, 0.04);
  color: var(--color-text-primary);
}

.nav-item.active {
  background: rgba(0, 113, 227, 0.1);
  color: var(--color-primary-dark);
  font-weight: 600;
}

.nav-icon {
  width: 20px;
  height: 20px;
  font-size: 20px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-icon svg {
  width: 100%;
  height: 100%;
}

.nav-label {
  flex: 1;
}

/* 侧边栏底部 */
.sidebar-footer {
  padding: 24px;
  border-top: 1px solid var(--color-border-light);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--color-bg-page);
  border: 1px solid var(--color-border);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 16px;
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 4px 0;
}

.user-role {
  font-size: 12px;
  color: var(--color-text-secondary);
  font-weight: 500;
  margin: 0;
}

.logout-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  color: var(--color-text-regular);
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.logout-btn:hover {
  color: #ffffff;
  border-color: var(--color-danger);
  background: var(--color-danger);
  box-shadow: 0 4px 12px rgba(255, 59, 48, 0.2);
}

/* ============================================================
   主内容区
   ============================================================ */

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-wrapper {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 40px;
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
}

/* 自定义滚动条样式 */
.content-wrapper::-webkit-scrollbar {
  width: 8px;
}

.content-wrapper::-webkit-scrollbar-track {
  background: transparent;
}

.content-wrapper::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
}

.content-wrapper::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.2);
}

/* ============================================================
   页面切换动画
   ============================================================ */

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s cubic-bezier(0.16, 1, 0.3, 1), transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(12px) scale(0.99);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-12px) scale(0.99);
}

/* ============================================================
   响应式
   ============================================================ */

@media (max-width: 768px) {
  .main-layout {
    flex-direction: column;
  }

  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 100;
    transform: translateX(-100%);
    transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  }

  .sidebar.open {
    transform: translateX(0);
    box-shadow: 0 0 0 100vw rgba(0, 0, 0, 0.2);
  }

  .main-content {
    height: 100vh;
  }

  .content-wrapper {
    padding: 24px;
  }
}
</style>
