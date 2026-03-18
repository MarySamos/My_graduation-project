<template>
  <router-view v-slot="{ Component }">
    <transition name="page" mode="out-in">
      <component :is="Component" />
    </transition>
  </router-view>
</template>

<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  // 检查系统暗色模式偏好
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    // 如果需要暗色模式支持，可以在这里添加
    document.documentElement.classList.add('light')
  } else {
    document.documentElement.classList.add('light')
  }
})
</script>

<style>
/* 全局页面过渡动画 */
.page-enter-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.page-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 选择文本样式 */
::selection {
  background: var(--accent);
  color: var(--text-inverse);
}

::-moz-selection {
  background: var(--accent);
  color: var(--text-inverse);
}

/* 焦点样式 */
:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

/* 链接样式 */
a {
  color: var(--accent);
  text-decoration: none;
  transition: color var(--transition-fast);
}

a:hover {
  color: var(--accent-hover);
}

/* 禁用状态 */
[disabled] {
  cursor: not-allowed;
  opacity: 0.6;
}

/* 图片样式 */
img {
  max-width: 100%;
  height: auto;
}

/* 代码样式 */
code {
  font-family: 'DM Sans Mono', 'Consolas', monospace;
  font-size: 0.9em;
  background: var(--bg-secondary);
  padding: 2px 6px;
  border-radius: 4px;
}

pre {
  font-family: 'DM Sans Mono', 'Consolas', monospace;
  background: var(--bg-card);
  padding: 16px;
  border-radius: var(--radius-md);
  overflow-x: auto;
  border: 1px solid var(--bg-secondary);
}

pre code {
  background: none;
  padding: 0;
}

/* 全局 Toast 容器 */
.el-message-container {
  z-index: 9999 !important;
}

/* 全局 Dialog 容器 */
.el-overlay {
  z-index: 2000 !important;
}

/* 隐藏元素辅助类 */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* 文本截断 */
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 无滚动条但可滚动 */
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.no-scrollbar::-webkit-scrollbar {
  display: none;
}
</style>
