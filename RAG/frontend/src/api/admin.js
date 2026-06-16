/**
 * 文件：admin.js
 * 功能：管理员相关API
 * 说明：封装用户管理、统计等接口
 */

import api from './index.js'

/**
 * 获取用户列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.per_page - 每页数量
 * @param {string} params.keyword - 搜索关键词
 * @returns {Promise} 用户列表
 */
export function getUserList(params) {
  return api.get('/users', { params })
}

/**
 * 获取用户详情
 * @param {number} userId - 用户ID
 * @returns {Promise} 用户详情
 */
export function getUser(userId) {
  return api.get(`/users/${userId}`)
}

/**
 * 更新用户
 * @param {number} userId - 用户ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新结果
 */
export function updateUser(userId, data) {
  return api.put(`/users/${userId}`, data)
}

/**
 * 删除用户
 * @param {number} userId - 用户ID
 * @returns {Promise} 删除结果
 */
export function deleteUser(userId) {
  return api.delete(`/users/${userId}`)
}

/**
 * 重置用户密码
 * @param {number} userId - 用户ID
 * @returns {Promise} 重置结果
 */
export function resetPassword(userId) {
  return api.put(`/users/${userId}/reset-password`)
}

/**
 * 获取统计数据
 * @returns {Promise} 统计数据
 */
export function getStatsOverview() {
  return api.get('/stats/overview')
}

/**
 * 获取问答趋势
 * @param {number} days - 统计天数
 * @returns {Promise} 趋势数据
 */
export function getStatsTrends(days = 7) {
  return api.get('/stats/trends', { params: { days } })
}

/**
 * 获取热门问题
 * @param {number} top - 返回数量
 * @returns {Promise} 热门问题列表
 */
export function getHotQuestions(top = 10) {
  return api.get('/stats/hot-questions', { params: { top } })
}
