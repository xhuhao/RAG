<!--
  文件：Users.vue
  功能：用户管理页面
  说明：管理员查看、编辑、禁用、删除用户
-->

<template>
  <div class="users-container">
    <!-- 搜索区域 -->
    <el-card class="search-card">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索用户名"
        :prefix-icon="Search"
        style="width: 300px"
        clearable
      />
    </el-card>

    <!-- 用户表格 -->
    <el-card class="table-card">
      <el-table :data="userList" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="180" />
        <el-table-column label="操作" width="300">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button
              size="small"
              :type="row.status === 1 ? 'warning' : 'success'"
              @click="handleToggleStatus(row)"
            >
              {{ row.status === 1 ? '禁用' : '启用' }}
            </el-button>
            <el-button size="small" @click="handleResetPassword(row)">重置密码</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)" v-if="row.role !== 'admin'">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
/**
 * 用户管理页面组件
 * 功能：管理员查看、编辑、禁用、删除用户
 */

import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUserList, updateUser, deleteUser, resetPassword } from '../../api/admin.js'

// 搜索关键词
const searchKeyword = ref('')

// 用户列表
const userList = ref([])

// 加载状态
const loading = ref(false)

/**
 * 加载用户列表
 */
const loadUserList = async () => {
  loading.value = true
  try {
    const res = await getUserList({
      page: 1,
      per_page: 100,
      keyword: searchKeyword.value || undefined
    })
    userList.value = res.data.items || []
  } catch (error) {
    console.error('加载用户列表失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 编辑用户
 */
const handleEdit = async (row) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入新用户名', '编辑用户', {
      inputValue: row.username,
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })

    if (value && value !== row.username) {
      await updateUser(row.id, { username: value })
      ElMessage.success('更新成功')
      loadUserList()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '更新失败')
    }
  }
}

/**
 * 切换用户状态
 */
const handleToggleStatus = async (row) => {
  try {
    const newStatus = row.status === 1 ? 0 : 1
    const action = newStatus === 1 ? '启用' : '禁用'

    await ElMessageBox.confirm(`确定要${action}用户 ${row.username} 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await updateUser(row.id, { status: newStatus })
    ElMessage.success(`${action}成功`)
    loadUserList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '操作失败')
    }
  }
}

/**
 * 删除用户
 */
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户 ${row.username} 吗？此操作不可恢复！`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteUser(row.id)
    ElMessage.success('删除成功')
    loadUserList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

/**
 * 重置密码
 */
const handleResetPassword = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要重置用户 ${row.username} 的密码为123456吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await resetPassword(row.id)
    ElMessage.success('密码重置成功，新密码为：123456')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '重置失败')
    }
  }
}

onMounted(() => {
  loadUserList()
})
</script>

<style scoped>
.users-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
