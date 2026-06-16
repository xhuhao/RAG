/**
 * 文件：index.js
 * 功能：路由配置
 * 说明：定义页面路由规则
 */

import { createRouter, createWebHistory } from 'vue-router'

// 路由配置
const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { title: '注册' }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('../views/Chat.vue'),
    meta: { title: '问答', requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/admin/Layout.vue'),
    meta: { title: '管理后台', requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',
        redirect: '/admin/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/admin/Dashboard.vue'),
        meta: { title: '数据统计' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/admin/Users.vue'),
        meta: { title: '用户管理' }
      },
      {
        path: 'documents',
        name: 'Documents',
        component: () => import('../views/admin/Documents.vue'),
        meta: { title: '文档管理' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('../views/admin/Settings.vue'),
        meta: { title: '系统设置' }
      }
    ]
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - RAG知识库` : 'RAG知识库'

  // 获取用户信息
  const userInfo = JSON.parse(sessionStorage.getItem('userInfo') || 'null')

  // 需要登录的页面
  if (to.meta.requiresAuth && !userInfo) {
    next('/login')
    return
  }

  // 需要管理员权限的页面
  if (to.meta.requiresAdmin && userInfo?.role !== 'admin') {
    next('/chat')
    return
  }

  // 已登录用户访问登录/注册页面
  if ((to.path === '/login' || to.path === '/register') && userInfo) {
    if (userInfo.role === 'admin') {
      next('/admin/dashboard')
    } else {
      next('/chat')
    }
    return
  }

  next()
})

export default router
