/**
 * 文件：chat.js
 * 功能：问答相关API
 * 说明：封装提问、清空历史等接口
 */

import api from './index.js'

/**
 * 提问
 * @param {Object} data - 提问信息
 * @param {string} data.question - 用户问题
 * @param {string} data.session_id - 会话ID
 * @returns {Promise} 问答结果
 */
export function askQuestion(data) {
  return api.post('/chat/ask', data)
}

/**
 * 清空会话历史
 * @param {Object} data - 清空信息
 * @param {string} data.session_id - 会话ID
 * @returns {Promise} 清空结果
 */
export function clearHistory(data) {
  return api.post('/chat/clear', data)
}
