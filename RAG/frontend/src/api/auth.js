/**
 * 文件：auth.js
 * 功能：用户认证相关API
 * 说明：封装登录、注册、登出等接口
 */

import api from './index.js'

/**
 * 用户注册
 * @param {Object} data - 注册信息
 * @param {string} data.username - 用户名
 * @param {string} data.password - 密码
 * @param {string} data.confirm_password - 确认密码
 * @returns {Promise} 注册结果
 */
export function register(data) {
  return api.post('/auth/register', data)
}

/**
 * 用户登录
 * @param {Object} data - 登录信息
 * @param {string} data.username - 用户名
 * @param {string} data.password - 密码
 * @returns {Promise} 登录结果
 */
export function login(data) {
  return api.post('/auth/login', data)
}

/**
 * 用户登出
 * @returns {Promise} 登出结果
 */
export function logout() {
  return api.get('/auth/logout')
}
