<!--
  文件：Chat.vue
  功能：问答主页面
  说明：用户输入问题，系统检索知识库并返回答案
-->

<template>
  <div class="chat-container">
    <!-- 顶部导航栏 -->
    <div class="chat-header">
      <div class="header-left">
        <h2>RAG校园知识库</h2>
      </div>
      <div class="header-right">
        <span class="username">{{ userInfo?.username }}</span>
        <el-button type="danger" text @click="handleLogout">退出登录</el-button>
      </div>
    </div>

    <!-- 聊天区域 -->
    <div class="chat-messages" ref="messagesRef">
      <!-- 欢迎消息 -->
      <div class="message-item assistant">
        <div class="message-avatar">
          <el-icon><Monitor /></el-icon>
        </div>
        <div class="message-content">
          <div class="message-text">
            你好！我是广西师范大学智能问答助手，请问有什么可以帮您？
          </div>
        </div>
      </div>

      <!-- 消息列表 -->
      <div
        v-for="(msg, index) in messages"
        :key="index"
        class="message-item"
        :class="msg.role"
      >
        <!-- 用户头像 -->
        <div class="message-avatar" v-if="msg.role === 'user'">
          <el-icon><User /></el-icon>
        </div>

        <!-- AI头像 -->
        <div class="message-avatar" v-if="msg.role === 'assistant'">
          <el-icon><Monitor /></el-icon>
        </div>

        <!-- 消息内容 -->
        <div class="message-content">
          <div class="message-text">{{ msg.content }}</div>

          <!-- 参考来源 -->
          <div class="message-references" v-if="msg.references && msg.references.length > 0">
            <div class="references-title">参考来源：</div>
            <div
              v-for="(ref, refIndex) in msg.references"
              :key="refIndex"
              class="reference-item"
            >
              <a :href="ref.url" target="_blank">{{ ref.title }}</a>
            </div>
          </div>
        </div>
      </div>

      <!-- 加载中提示 -->
      <div class="message-item assistant" v-if="loading">
        <div class="message-avatar">
          <el-icon><Monitor /></el-icon>
        </div>
        <div class="message-content">
          <div class="message-text loading-text">
            <span>正在思考中</span>
            <span class="loading-dots">...</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="chat-input">
      <el-input
        v-model="inputMessage"
        type="textarea"
        :rows="2"
        placeholder="请输入您的问题，按Enter发送，Shift+Enter换行"
        resize="none"
        @keydown="handleKeydown"
      />
      <el-button
        type="primary"
        :loading="loading"
        :disabled="!inputMessage.trim()"
        @click="sendMessage"
      >
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup>
/**
 * 问答主页面组件
 * 功能：用户输入问题，系统检索知识库并返回答案
 */

import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Monitor } from '@element-plus/icons-vue'
import { askQuestion } from '../api/chat.js'

const router = useRouter()

// 用户信息
const userInfo = ref(JSON.parse(sessionStorage.getItem('userInfo') || 'null'))

// 消息列表
const messages = ref([])

// 输入框内容
const inputMessage = ref('')

// 加载状态
const loading = ref(false)

// 消息区域引用
const messagesRef = ref(null)

/**
 * 滚动到底部
 */
const scrollToBottom = async () => {
  await nextTick()
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

/**
 * 处理键盘事件
 */
const handleKeydown = (e) => {
  // Enter发送，Shift+Enter换行
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

/**
 * 发送消息
 */
const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message) return

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: message
  })

  // 清空输入框
  inputMessage.value = ''

  // 滚动到底部
  await scrollToBottom()

  // 显示加载状态
  loading.value = true

  try {
    // 调用后端问答接口
    const res = await askQuestion({
      question: message,
      session_id: userInfo.value?.username || 'default'
    })

    // 添加AI回复
    messages.value.push({
      role: 'assistant',
      content: res.data.answer,
      references: res.data.references || []
    })
  } catch (error) {
    console.error('问答失败:', error)
    messages.value.push({
      role: 'assistant',
      content: '抱歉，回答出现问题，请稍后重试。',
      references: []
    })
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

/**
 * 退出登录
 */
const handleLogout = () => {
  sessionStorage.removeItem('userInfo')
  ElMessage.success('已退出登录')
  router.push('/login')
}

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.chat-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.chat-header h2 {
  font-size: 18px;
  color: #333;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.username {
  font-size: 14px;
  color: #666;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.message-item {
  display: flex;
  margin-bottom: 20px;
  gap: 12px;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-shrink: 0;
}

.message-item.user .message-avatar {
  background: #409eff;
  color: #fff;
}

.message-item.assistant .message-avatar {
  background: #67c23a;
  color: #fff;
}

.message-content {
  max-width: 70%;
}

.message-text {
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.message-item.user .message-text {
  background: #409eff;
  color: #fff;
}

.message-item.assistant .message-text {
  background: #fff;
  color: #333;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message-references {
  margin-top: 8px;
  padding: 8px 12px;
  background: #f0f9ff;
  border-radius: 6px;
  font-size: 12px;
}

.references-title {
  color: #999;
  margin-bottom: 4px;
}

.reference-item a {
  color: #409eff;
  text-decoration: none;
}

.reference-item a:hover {
  text-decoration: underline;
}

.loading-text {
  display: flex;
  align-items: center;
}

.loading-dots {
  display: inline-block;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.chat-input {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  background: #fff;
  border-top: 1px solid #e4e7ed;
}

.chat-input .el-input {
  flex: 1;
}

.chat-input .el-button {
  height: auto;
}
</style>
