<template>
  <div class="page">
    <header class="page-header">
      <div>
        <p class="page-breadcrumb">智能助手 / 对话</p>
        <h1 class="page-title">AI 智能助手</h1>
        <p class="page-subtitle">数据分析与知识查询</p>
      </div>
    </header>

    <!-- 聊天容器 -->
    <section class="chat-container">
      <!-- 模式切换 -->
      <div class="mode-toggle">
        <button
          :class="['mode-btn', { active: chatMode === 'data' }]"
          @click="chatMode = 'data'"
        >
          数据查询
        </button>
        <button
          :class="['mode-btn', { active: chatMode === 'knowledge' }]"
          @click="chatMode = 'knowledge'"
        >
          知识库
        </button>
      </div>

      <!-- 消息列表 -->
      <div class="messages-list" ref="messagesRef">
        <div v-if="messages.length === 0" class="welcome-state">
          <h3>你好，我是 BankAgent 智能助手</h3>
          <p>我可以帮你分析数据或查询知识库，试试问我：</p>
          <div class="suggestions">
            <span class="suggestion-chip" @click="sendSuggestion('查询30岁以下的客户有哪些？')">
              查询30岁以下客户
            </span>
            <span class="suggestion-chip" @click="sendSuggestion('各职业的转化率是多少？')">
              职业转化率
            </span>
            <span class="suggestion-chip" @click="sendSuggestion('银行的定期存款产品有哪些特点？')">
              查询知识库
            </span>
          </div>
        </div>

        <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.role]">
          <div v-if="msg.role === 'assistant'" class="message-content">
            <div class="message-text">{{ msg.content }}</div>
            <div v-if="msg.sources && msg.sources.length > 0" class="sources-box">
              <div class="sources-title">知识来源 ({{ msg.sources.length }})</div>
              <div v-for="(source, idx) in msg.sources" :key="idx" class="source-item">
                <span class="source-index">{{ idx + 1 }}</span>
                <div class="source-content">{{ source.content }}</div>
              </div>
            </div>
            <div v-if="msg.chart" class="chart-box" v-html="msg.chart"></div>
            <div v-if="msg.sql" class="sql-box">
              <div class="sql-title">已执行 SQL</div>
              <pre>{{ msg.sql }}</pre>
            </div>
          </div>
          <div v-else class="message-content user-content">
            <div class="message-text">{{ msg.content }}</div>
          </div>
        </div>

        <div v-if="loading" class="message assistant">
          <div class="message-content">
            <div class="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入框 -->
      <div class="input-area">
        <input
          v-model="inputMessage"
          @keyup.enter="sendMessage"
          type="text"
          placeholder="输入问题..."
          :disabled="loading"
          class="chat-input"
        />
        <button
          class="send-btn"
          @click="sendMessage"
          :disabled="!inputMessage.trim() || loading"
        >
          发送
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import api from '../../api'

const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const messagesRef = ref(null)
const chatMode = ref('data')

const scrollToBottom = async () => {
  await nextTick()
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value) return

  const userMsg = inputMessage.value
  messages.value.push({ role: 'user', content: userMsg })
  inputMessage.value = ''
  loading.value = true
  await scrollToBottom()

  const assistantMsg = { role: 'assistant', content: '', chart: null, sql: null, sources: null }
  messages.value.push(assistantMsg)

  try {
    const response = await fetch('/api/v1/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userMsg, user_id: localStorage.getItem('userId') || 'default', history: [] })
    })

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop()

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.type === 'text') assistantMsg.content += data.content
            else if (data.type === 'answer') assistantMsg.content = data.content
            else if (data.type === 'sql') assistantMsg.sql = data.sql
            else if (data.type === 'visualization') assistantMsg.chart = data.chart
            else if (data.type === 'sources') assistantMsg.sources = data.sources
            else if (data.type === 'error') assistantMsg.content = data.message
            else if (data.type === 'done') { loading.value = false; await scrollToBottom(); return }
            await scrollToBottom()
          } catch (e) {}
        }
      }
    }
  } catch (error) {
    console.error('Chat error:', error)
    assistantMsg.content = '抱歉，遇到了一些问题。'
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

const sendSuggestion = (text) => {
  inputMessage.value = text
  sendMessage()
}
</script>

<style scoped>
/* ============================================================
   整体页面结构
   ============================================================ */
.page {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.page-header {
  margin-bottom: 24px;
}

.page-breadcrumb {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
  font-weight: 500;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--color-text-primary);
  margin: 0;
}

.page-subtitle {
  font-size: 15px;
  color: var(--color-text-regular);
  margin-top: 8px;
}

/* ============================================================
   聊天主容器
   ============================================================ */
.chat-container {
  background: var(--color-bg-container);
  border-radius: var(--radius-large);
  padding: 24px;
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 500px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border-light);
}

/* ============================================================
   分段控件 (模式切换)
   ============================================================ */
.mode-toggle {
  display: inline-flex;
  background: var(--color-bg-page);
  padding: 4px;
  border-radius: 12px;
  margin-bottom: 24px;
  align-self: flex-start;
}

.mode-btn {
  padding: 8px 24px;
  background: transparent;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.mode-btn.active {
  background: var(--color-bg-container);
  color: var(--color-text-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* ============================================================
   消息列表区域
   ============================================================ */
.messages-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px 8px;
}

/* 自定义滚动条 */
.messages-list::-webkit-scrollbar {
  width: 6px;
}
.messages-list::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 3px;
}

.welcome-state {
  text-align: center;
  padding: 80px 20px;
  color: var(--color-text-secondary);
}

.welcome-state h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 12px;
}

.suggestions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 32px;
  flex-wrap: wrap;
}

.suggestion-chip {
  padding: 10px 20px;
  background: var(--color-bg-page);
  border-radius: 24px;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-regular);
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.suggestion-chip:hover {
  background: var(--color-bg-container);
  color: var(--color-primary);
  border-color: var(--color-primary-light);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

/* ============================================================
   聊天气泡 (iMessage Style)
   ============================================================ */
.message {
  margin-bottom: 24px;
  display: flex;
}

.message.assistant {
  justify-content: flex-start;
}

.message.user {
  justify-content: flex-end;
}

.message-content {
  max-width: 75%;
  padding: 12px 18px;
  font-size: 15px;
  line-height: 1.5;
  word-wrap: break-word;
}

.message.assistant .message-content {
  background: var(--color-bg-page);
  color: var(--color-text-primary);
  border-radius: 20px 20px 20px 4px;
}

.message.user .message-content {
  background: var(--color-primary);
  color: #ffffff;
  border-radius: 20px 20px 4px 20px;
}

/* ============================================================
   附加内容 (提示来源、SQL渲染框等)
   ============================================================ */
.sources-box,
.sql-box {
  margin-top: 12px;
  padding: 16px;
  background: #ffffff;
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
}

.sources-title,
.sql-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.source-item {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  font-size: 14px;
}
.source-item:last-child {
  margin-bottom: 0;
}

.source-index {
  width: 24px;
  height: 24px;
  background: var(--color-bg-page);
  color: var(--color-text-regular);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.sql-box pre {
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
  font-size: 13px;
  color: var(--color-primary);
  white-space: pre-wrap;
  margin: 0;
}

/* ============================================================
   输入框区域
   ============================================================ */
.input-area {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border-light);
}

.chat-input {
  flex: 1;
  padding: 16px 24px;
  background: var(--color-bg-page);
  border: 1px solid transparent;
  border-radius: var(--radius-xl);
  font-size: 16px;
  font-family: inherit;
  color: var(--color-text-primary);
  transition: all 0.3s ease;
}

.chat-input:focus {
  outline: none;
  background: var(--color-bg-container);
  border-color: var(--color-primary-light);
  box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.15);
}

.send-btn {
  padding: 14px 28px;
  background: var(--color-primary);
  color: #ffffff;
  font-weight: 600;
  font-size: 15px;
  border: none;
  border-radius: var(--radius-xl);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.send-btn:hover:not(:disabled) {
  background: var(--color-primary-dark);
  transform: scale(0.96);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Typing Indicator (iOS Style) */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 4px 8px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: var(--color-text-secondary);
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
.typing-indicator span:nth-child(3) { animation-delay: 0s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}
</style>
