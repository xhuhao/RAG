<!--
  文件：Settings.vue
  功能：系统设置页面
  说明：管理员配置定时同步任务、查看同步历史
-->

<template>
  <div class="settings-container">
    <!-- 定时同步设置 -->
    <el-card class="setting-card">
      <template #header>
        <div class="card-header">
          <span>定时同步设置</span>
        </div>
      </template>

      <el-form :model="syncSettings" label-width="120px">
        <el-form-item label="同步频率">
          <el-select v-model="syncSettings.frequency" style="width: 200px">
            <el-option label="每天" value="daily" />
            <el-option label="每小时" value="hourly" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>

        <el-form-item label="执行时间" v-if="syncSettings.frequency === 'daily'">
          <el-time-picker v-model="syncSettings.time" format="HH:mm" />
        </el-form-item>

        <el-form-item label="Cron表达式" v-if="syncSettings.frequency === 'custom'">
          <el-input v-model="syncSettings.cron" placeholder="例：0 2 * * *" style="width: 200px" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSaveSettings">保存设置</el-button>
          <el-button type="success" @click="handleSyncNow">立即同步</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 同步历史 -->
    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <span>同步历史记录</span>
        </div>
      </template>

      <el-table :data="syncHistory" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="created_at" label="同步时间" width="180" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'">
              {{ row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="added" label="新增" width="80" />
        <el-table-column prop="updated" label="更新" width="80" />
        <el-table-column prop="removed" label="删除" width="80" />
        <el-table-column prop="failed" label="失败" width="80" />
        <el-table-column prop="message" label="备注" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
/**
 * 系统设置页面组件
 * 功能：管理员配置定时同步任务、查看同步历史
 */

import { ref } from 'vue'
import { ElMessage } from 'element-plus'

// 同步设置
const syncSettings = ref({
  frequency: 'daily',
  time: new Date(2025, 0, 1, 2, 0),  // 凌晨2点
  cron: '0 2 * * *'
})

// 同步历史（模拟数据）
const syncHistory = ref([
  { id: 1, created_at: '2025-06-08 02:00:00', status: 'success', added: 3, updated: 1, removed: 0, failed: 0, message: '同步完成' },
  { id: 2, created_at: '2025-06-07 02:00:00', status: 'success', added: 0, updated: 0, removed: 0, failed: 0, message: '无新增文档' }
])

/**
 * 保存设置
 */
const handleSaveSettings = () => {
  // TODO: 调用后端接口保存设置
  ElMessage.success('设置已保存')
}

/**
 * 立即同步
 */
const handleSyncNow = async () => {
  // TODO: 调用后端接口触发同步
  ElMessage.success('同步任务已触发')
}
</script>

<style scoped>
.settings-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.card-header {
  font-weight: bold;
}
</style>
