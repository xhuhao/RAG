<!--
  文件：Documents.vue
  功能：文档管理页面
  说明：管理员上传、编辑、删除文档
-->

<template>
  <div class="documents-container">
    <!-- 操作栏 -->
    <el-card class="action-card">
      <el-button type="primary" @click="handleUpload">
        <el-icon><Upload /></el-icon>
        上传文档
      </el-button>
    </el-card>

    <!-- 文档表格 -->
    <el-card class="table-card">
      <el-table :data="documentList" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="doc_type" label="类型" width="120" />
        <el-table-column prop="version" label="版本" width="80" />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active === 1 ? 'success' : 'info'">
              {{ row.is_active === 1 ? '生效' : '归档' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 上传对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="上传文档" width="500px">
      <el-form :model="uploadForm" label-width="100px">
        <el-form-item label="文档标题" required>
          <el-input v-model="uploadForm.title" placeholder="请输入文档标题" />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="uploadForm.category" placeholder="请输入分类（如：教务处）" />
        </el-form-item>
        <el-form-item label="文档类型">
          <el-input v-model="uploadForm.doc_type" placeholder="请输入类型（如：规章制度）" />
        </el-form-item>
        <el-form-item label="文档URL">
          <el-input v-model="uploadForm.url" placeholder="请输入文档URL" />
        </el-form-item>
        <el-form-item label="PDF文件" required>
          <el-upload
            :auto-upload="false"
            :limit="1"
            accept=".pdf"
            :on-change="handleFileChange"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">只能上传PDF文件</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUploadSubmit">上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 文档管理页面组件
 * 功能：管理员上传、编辑、删除文档
 */

import { ref, onMounted } from 'vue'
import { Upload } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDocumentList, uploadDocument, deleteDocument } from '../../api/document.js'

// 文档列表
const documentList = ref([])

// 加载状态
const loading = ref(false)

// 上传对话框
const uploadDialogVisible = ref(false)
const uploadForm = ref({
  title: '',
  category: '',
  doc_type: '',
  url: '',
  file: null
})

/**
 * 加载文档列表
 */
const loadDocumentList = async () => {
  loading.value = true
  try {
    const res = await getDocumentList({
      page: 1,
      per_page: 100
    })
    documentList.value = res.data.items || []
  } catch (error) {
    console.error('加载文档列表失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 上传文档
 */
const handleUpload = () => {
  uploadDialogVisible.value = true
}

/**
 * 提交上传
 */
const handleUploadSubmit = async () => {
  if (!uploadForm.value.title) {
    ElMessage.error('请输入文档标题')
    return
  }

  if (!uploadForm.value.file) {
    ElMessage.error('请选择PDF文件')
    return
  }

  try {
    const formData = new FormData()
    formData.append('file', uploadForm.value.file)
    formData.append('title', uploadForm.value.title)
    formData.append('category', uploadForm.value.category)
    formData.append('doc_type', uploadForm.value.doc_type)
    formData.append('url', uploadForm.value.url)

    await uploadDocument(formData)
    ElMessage.success('上传成功')
    uploadDialogVisible.value = false
    uploadForm.value = { title: '', category: '', doc_type: '', url: '', file: null }
    loadDocumentList()
  } catch (error) {
    ElMessage.error(error.message || '上传失败')
  }
}

/**
 * 文件选择
 */
const handleFileChange = (file) => {
  uploadForm.value.file = file.raw
}

/**
 * 编辑文档
 */
const handleEdit = (row) => {
  // TODO: 实现编辑功能
  console.log('编辑文档:', row)
}

/**
 * 删除文档
 */
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除文档 "${row.title}" 吗？`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteDocument(row.id)
    ElMessage.success('删除成功')
    loadDocumentList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

onMounted(() => {
  loadDocumentList()
})
</script>

<style scoped>
.documents-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
