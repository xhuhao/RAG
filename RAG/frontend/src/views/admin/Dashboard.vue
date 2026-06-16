<!--
  文件：Dashboard.vue
  功能：数据统计页面
  说明：展示问答总量、趋势图、热门问题等统计数据
-->

<template>
  <div class="dashboard-container">
    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-card class="stat-card">
        <div class="stat-value">{{ stats.totalQuestions }}</div>
        <div class="stat-label">问答总量</div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-value">{{ stats.todayQuestions }}</div>
        <div class="stat-label">今日问答</div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-value">{{ stats.totalUsers }}</div>
        <div class="stat-label">用户总数</div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-value">{{ stats.totalDocuments }}</div>
        <div class="stat-label">文档总数</div>
      </el-card>
    </div>

    <!-- 图表区域 -->
    <div class="charts-area">
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>问答趋势（近7天）</span>
          </div>
        </template>
        <div class="chart-placeholder">
          <p>📊 问答趋势折线图</p>
          <p>（ECharts图表将在阶段3实现）</p>
        </div>
      </el-card>

      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>热门问题Top10</span>
          </div>
        </template>
        <div class="chart-placeholder">
          <p>📈 热门问题柱状图</p>
          <p>（ECharts图表将在阶段3实现）</p>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
/**
 * 数据统计页面组件
 * 功能：展示系统统计数据和图表
 */

import { ref, onMounted } from 'vue'
import { getStatsOverview } from '../../api/admin.js'

// 统计数据
const stats = ref({
  totalQuestions: 0,
  todayQuestions: 0,
  totalUsers: 0,
  totalDocuments: 0
})

/**
 * 加载统计数据
 */
const loadStats = async () => {
  try {
    const res = await getStatsOverview()
    const data = res.data

    stats.value = {
      totalQuestions: data.questions?.total || 0,
      todayQuestions: data.questions?.today || 0,
      totalUsers: data.users?.total || 0,
      totalDocuments: data.documents?.total || 0
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #999;
}

.charts-area {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.card-header {
  font-weight: bold;
}

.chart-placeholder {
  height: 300px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #999;
}

.chart-placeholder p {
  margin: 8px 0;
}
</style>
