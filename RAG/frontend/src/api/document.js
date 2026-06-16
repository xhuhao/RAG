/**
 * 文件：document.js
 * 功能：文档管理相关API
 * 说明：封装文档上传、查询、更新、删除等接口
 */

import api from './index.js'

/**
 * 获取文档列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.per_page - 每页数量
 * @param {string} params.keyword - 搜索关键词
 * @returns {Promise} 文档列表
 */
export function getDocumentList(params) {
  return api.get('/documents', { params })
}

/**
 * 上传文档
 * @param {FormData} formData - 包含文件和元数据的FormData
 * @returns {Promise} 上传结果
 */
export function uploadDocument(formData) {
  return api.post('/documents', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 获取文档详情
 * @param {number} docId - 文档ID
 * @returns {Promise} 文档详情
 */
export function getDocument(docId) {
  return api.get(`/documents/${docId}`)
}

/**
 * 更新文档
 * @param {number} docId - 文档ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新结果
 */
export function updateDocument(docId, data) {
  return api.put(`/documents/${docId}`, data)
}

/**
 * 删除文档
 * @param {number} docId - 文档ID
 * @returns {Promise} 删除结果
 */
export function deleteDocument(docId) {
  return api.delete(`/documents/${docId}`)
}
