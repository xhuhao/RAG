/**
 * 文件：index.js
 * 功能：Axios配置
 * 说明：创建axios实例，配置请求拦截器和响应拦截器
 */

import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 可以在这里添加token等认证信息
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    const data = response.data

    // 根据状态码处理
    if (data.code === 200) {
      return data
    } else if (data.code === 401) {
      // 未登录或登录过期
      sessionStorage.removeItem('userInfo')
      window.location.href = '/login'
      return Promise.reject(new Error(data.message))
    } else {
      // 其他错误
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message))
    }
  },
  error => {
    // 网络错误
    if (!error.response) {
      ElMessage.error('网络连接失败，请检查网络')
    } else {
      ElMessage.error(error.response.data?.message || '服务器错误')
    }
    return Promise.reject(error)
  }
)

export default api
