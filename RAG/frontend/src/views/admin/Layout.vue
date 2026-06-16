<!--
  文件：Layout.vue
  功能：管理后台布局
  说明：侧边栏 + 顶栏 + 内容区
-->

<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <div class="admin-sidebar">
      <div class="sidebar-header">
        <h2>管理后台</h2>
      </div>
      <el-menu
        :default-active="currentRoute"
        router
        class="sidebar-menu"
      >
        <el-menu-item index="/admin/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据统计</span>
        </el-menu-item>
        <el-menu-item index="/admin/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/documents">
          <el-icon><Document /></el-icon>
          <span>文档管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </div>

    <!-- 右侧内容区 -->
    <div class="admin-main">
      <!-- 顶栏 -->
      <div class="admin-header">
        <div class="header-left">
          <h3>{{ currentTitle }}</h3>
        </div>
        <div class="header-right">
          <span class="username">{{ userInfo?.username }}</span>
          <el-button type="danger" text @click="handleLogout">退出登录</el-button>
        </div>
      </div>

      <!-- 内容区 -->
      <div class="admin-content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 管理后台布局组件
 * 功能：提供管理后台的整体布局结构
 */

import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { DataAnalysis, User, Document, Setting } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

// 用户信息
const userInfo = ref(JSON.parse(sessionStorage.getItem('userInfo') || 'null'))

// 当前路由路径
const currentRoute = computed(() => route.path)

// 当前页面标题
const currentTitle = computed(() => {
  const titleMap = {
    '/admin/dashboard': '数据统计',
    '/admin/users': '用户管理',
    '/admin/documents': '文档管理',
    '/admin/settings': '系统设置'
  }
  return titleMap[route.path] || '管理后台'
})

/**
 * 退出登录
 */
const handleLogout = () => {
  sessionStorage.removeItem('userInfo')
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  width: 100%;
  height: 100vh;
}

.admin-sidebar {
  width: 220px;
  background: #304156;
  flex-shrink: 0;
}

.sidebar-header {
  height: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #263445;
}

.sidebar-header h2 {
  color: #fff;
  font-size: 16px;
}

.sidebar-menu {
  border-right: none;
  background: #304156;
}

.sidebar-menu .el-menu-item {
  color: #bfcbd9;
}

.sidebar-menu .el-menu-item:hover {
  background: #263445;
}

.sidebar-menu .el-menu-item.is-active {
  color: #409eff;
  background: #263445;
}

.admin-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.admin-header {
  height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.admin-header h3 {
  font-size: 16px;
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

.admin-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: #f5f5f5;
}
</style>
