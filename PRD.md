# RAG校园知识库问答系统 - PRD文档

## 1. 项目概述

### 1.1 项目名称
广西师范大学RAG校园知识库问答Agent系统

### 1.2 项目简介
开发一个基于LangChain的RAG校园内部知识库问答Agent系统，复杂度适中，适合入门学习用。

### 1.3 技术栈
- **后端**：Python + Flask
- **前端**：Vue3 + Element Plus
- **数据库**：MySQL8 + Chroma向量数据库（Server模式）
- **LLM**：Deepseek-v4-pro
- **嵌入模型**：Ollama Qwen3-Embedding:4B
- **部署**：Docker Compose

---

## 2. 功能需求

### 2.1 用户角色

#### 普通用户
- 注册、登录
- 知识库问答（仅此功能）

#### 管理员
- 所有普通用户功能
- 文档管理（上传、删除、编辑）
- 用户管理（查看、禁用、重置密码）
- 数据统计（问答次数、热门问题、用户活跃度）
- 系统设置（定时任务配置、模型参数调整）

### 2.2 用户系统

#### 注册
- 用户名（必填，唯一）
- 密码（必填，MD5加密）
- 确认密码（必填）

#### 登录
- 用户名 + 密码
- 登录后根据角色跳转：
  - 管理员 → /admin/dashboard
  - 普通用户 → /chat

#### 登录状态
- 不保持登录状态
- 刷新页面需要重新登录

#### 默认账号
```
管理员：admin / 123456
测试用户：student1 / 123456
测试用户：student2 / 123456
```

### 2.3 知识库问答

#### 功能描述
- 用户输入问题，系统检索知识库并返回答案
- 支持多轮对话（保留最近20轮上下文）
- 回答时展示参考来源（网页链接）
- 参考来源链接点击后新窗口打开

#### 无答案处理
- 知识库无匹配内容时，直接回复："抱歉，未找到相关信息"

#### 问答页面交互
- **发送方式**：Enter发送 + Shift+Enter换行 + 点击按钮发送
- **等待回答**：显示"正在思考中..." + 加载动画
- **参考来源**：显示在答案下方，点击新窗口打开
- **界面布局**：单栏（简洁为主，不保存历史）

### 2.4 文档管理

#### 文档来源
- 广西师范大学官网PDF文档
- 纯文本PDF（无需OCR）

#### 文档分类
- **院系维度**：计算机学院、教务处、图书馆、研究生院等（10-20个）
- **文档类型**：通知公告、规章制度、课程信息、常见问题（4-6个）

#### 文档版本管理
- 新文档自动替换旧文档（同标题/同类别）
- 旧文档标记为`is_active=False`归档
- 检索时只查询生效文档
- 管理员可手动恢复旧文档

#### 文档同步
- **定时同步**：管理员可配置（默认每天凌晨2点）
- **手动同步**：管理员点击"立即同步"按钮
- **同步策略**：增量更新（只处理新增/修改的文档）
- **同步判断**：对比URL列表 + 检查Last-Modified时间
- **失败处理**：静默跳过，记录日志
- **同步历史**：记录每次同步的时间、状态、成功/失败数量

#### 分块策略
- **chunk_size**：1000字符
- **chunk_overlap**：200字符
- **分块方式**：按段落优先，段落太长再按字符切分

### 2.5 数据统计（管理员后台首页）

#### 统计指标
| 指标 | 展示形式 | 说明 |
|------|----------|------|
| 问答总量 | 数字卡片 | 今日/本周/总计 |
| 问答趋势 | 折线图 | 近7天每日问答量 |
| 热门问题 | 柱状图 | Top10被问最多的问题 |
| 文档统计 | 数字卡片 | 文档总数/最近更新时间 |

#### 技术实现
- 图表库：ECharts
- 刷新方式：定时刷新（每30秒或1分钟）

### 2.6 系统设置（管理员）

#### 功能列表
- 定时同步配置（同步频率、执行时间）
- 手动触发同步按钮
- 同步历史记录表格

---

## 3. API接口设计

### 3.1 用户认证模块 `/api/auth`
```
POST /api/auth/register    用户注册
POST /api/auth/login       用户登录
GET  /api/auth/logout      用户登出
GET  /api/auth/info        获取当前用户信息
```

### 3.2 问答模块 `/api/chat`
```
POST /api/chat/ask         提问（发送问题，返回答案+参考来源）
```

### 3.3 文档管理模块 `/api/documents`（管理员）
```
GET    /api/documents      获取文档列表
POST   /api/documents      上传文档
DELETE /api/documents/:id  删除文档
PUT    /api/documents/:id  更新文档元数据
```

### 3.4 用户管理模块 `/api/users`（管理员）
```
GET    /api/users          获取用户列表
PUT    /api/users/:id      修改用户信息（角色、状态）
DELETE /api/users/:id      删除用户
PUT    /api/users/:id/reset-password  重置密码
```

### 3.5 统计模块 `/api/stats`（管理员）
```
GET /api/stats/overview    总览数据（用户数、文档数、问答数）
GET /api/stats/trends      问答趋势（近7天）
GET /api/stats/hot-questions  热门问题Top10
```

### 3.6 系统设置模块 `/api/settings`（管理员）
```
GET  /api/settings          获取配置
PUT  /api/settings          更新配置（同步频率等）
POST /api/settings/sync    手动触发同步
GET  /api/settings/sync-history  同步历史记录
```

### 3.7 返回格式
```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

### 3.8 错误码
```
200 - 成功
400 - 请求参数错误
401 - 未登录/登录过期
403 - 无权限（普通用户访问管理员接口）
404 - 资源不存在
500 - 服务器内部错误
```

---

## 4. 数据库设计

### 4.1 用户表 `users`
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    password VARCHAR(32) NOT NULL COMMENT '密码（MD5加密）',
    role ENUM('user', 'admin') DEFAULT 'user' COMMENT '角色',
    status TINYINT DEFAULT 1 COMMENT '状态：1正常 0禁用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间'
);
```

### 4.2 文档表 `documents`
```sql
CREATE TABLE documents (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL COMMENT '文档标题',
    category VARCHAR(50) COMMENT '分类（院系）',
    doc_type VARCHAR(50) COMMENT '文档类型',
    url VARCHAR(500) COMMENT '文档URL',
    version INT DEFAULT 1 COMMENT '版本号',
    is_active TINYINT DEFAULT 1 COMMENT '是否生效',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
);
```

### 4.3 同步日志表 `sync_logs`
```sql
CREATE TABLE sync_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    status ENUM('success', 'failed') COMMENT '同步状态',
    added INT DEFAULT 0 COMMENT '新增数量',
    updated INT DEFAULT 0 COMMENT '更新数量',
    removed INT DEFAULT 0 COMMENT '删除数量',
    failed INT DEFAULT 0 COMMENT '失败数量',
    message TEXT COMMENT '备注信息',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '同步时间'
);
```

### 4.4 初始化数据
```sql
-- 管理员账号
INSERT INTO users (username, password, role) 
VALUES ('admin', MD5('123456'), 'admin');

-- 测试用户
INSERT INTO users (username, password, role) VALUES 
('student1', MD5('123456'), 'user'),
('student2', MD5('123456'), 'user');
```

---

## 5. 前端设计

### 5.1 路由结构
```
公共页面（无需登录）
├── /login      登录
├── /register   注册

普通用户页面
└── /chat       问答主页面

管理员页面（侧边栏布局）
├── /admin/dashboard   数据统计
├── /admin/documents   文档管理
├── /admin/users       用户管理
└── /admin/settings    系统设置
```

### 5.2 页面设计

#### 问答页面（Chat.vue）
- 单栏布局，简洁为主
- 聊天风格界面
- 底部输入框 + 发送按钮
- 消息气泡展示（用户问题右侧，AI回答左侧）
- 参考来源链接显示在答案下方

#### 管理后台布局
- 左侧边栏：菜单导航
- 顶部：Logo + 用户名 + 登出按钮
- 右侧内容区：页面内容

### 5.3 公共组件
```
components/
├── layout/
│   ├── Layout.vue          # 管理后台布局
│   ├── Header.vue          # 顶部导航栏
│   └── Sidebar.vue         # 侧边栏菜单
├── common/
│   ├── Loading.vue         # 加载动画
│   ├── Pagination.vue      # 分页组件
│   └── ConfirmDialog.vue   # 确认弹窗
└── chat/
    ├── ChatContainer.vue   # 聊天容器
    ├── ChatMessage.vue     # 单条消息
    ├── ChatInput.vue       # 输入框+发送按钮
    └── ReferenceLink.vue   # 参考来源链接
```

---

## 6. 后端设计

### 6.1 目录结构
```
backend/
├── app/
│   ├── __init__.py        # Flask应用初始化
│   ├── config/            # 配置文件
│   │   ├── default.py     # 默认配置
│   │   ├── development.py # 开发环境
│   │   └── production.py  # 生产环境
│   ├── models/            # 数据库模型
│   │   ├── user.py
│   │   └── document.py
│   ├── routes/            # API路由
│   │   ├── auth.py        # 登录注册
│   │   ├── chat.py        # 问答接口
│   │   ├── admin.py       # 管理员接口
│   │   └── document.py    # 文档管理
│   ├── services/          # 业务逻辑
│   │   ├── rag_service.py # RAG检索问答
│   │   └── sync_service.py# 文档同步
│   └── utils/             # 工具函数
│       └── md5.py
├── logs/                  # 日志文件
│   ├── app.log
│   └── error.log
├── chroma_data/           # Chroma数据（本地开发用）
├── requirements.txt
├── init.sql
└── run.py
```

### 6.2 模型配置

#### Deepseek LLM
```python
DEEPSEEK_API_KEY = 'your-api-key'
DEEPSEEK_MODEL = 'deepseek-v4-pro'
DEEPSEEK_TEMPERATURE = 0.2
DEEPSEEK_MAX_TOKENS = 1024
DEEPSEEK_TOP_P = 0.9
```

#### Ollama嵌入模型
```python
OLLAMA_HOST = 'ollama'
OLLAMA_PORT = 11434
OLLAMA_MODEL = 'qwen3-embedding:4b'
```

#### 多轮对话
```python
MAX_HISTORY_TURNS = 20  # 保留最近20轮对话
```

### 6.3 日志配置
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.FileHandler('logs/error.log', level=logging.ERROR),
        logging.StreamHandler()
    ]
)
```

### 6.4 跨域配置（开发环境）
```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})
```

---

## 7. 部署方案

### 7.1 服务器配置
- 阿里云/腾讯云学生机（¥9.9/月）
- 2核2G内存
- Docker + Docker Compose

### 7.2 Docker Compose配置
```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./frontend/dist:/usr/share/nginx/html
    depends_on:
      - flask

  flask:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    depends_on:
      mysql:
        condition: service_healthy
      chroma-server:
        condition: service_started
      ollama:
        condition: service_started
    volumes:
      - ./backend/logs:/app/logs

  chroma-server:
    image: chromadb/chroma
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/chroma/chroma

  mysql:
    image: mysql:8
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: 123456
      MYSQL_DATABASE: db_enterprise_ga
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  chroma_data:
  mysql_data:
  ollama_data:
```

### 7.3 启动顺序
```
1. MySQL（等待健康检查通过）
2. Chroma Server
3. Ollama
4. Flask后端
5. Nginx前端
```

### 7.4 访问方式
- 服务器IP直接访问：`http://123.45.67.89`
- 或绑定域名（可选）

---

## 8. 安全设计

### 8.1 密码安全
- MD5加盐加密
- 盐值：`guangxi_rag_2025`

### 8.2 接口安全
- 管理员接口验证role是否为admin
- 未登录访问需要登录的接口 → 返回401

### 8.3 文件上传安全
- 只允许上传PDF文件
- 限制文件大小（最大10MB）

### 8.4 SQL注入防护
- 使用SQLAlchemy ORM，自动防注入

### 8.5 XSS防护
- 前端对用户输入做转义

---

## 9. 开发计划

### 9.1 开发阶段

#### 阶段1：基础框架搭建（1-2天）
- 后端：Flask项目骨架、数据库连接、用户表
- 前端：Vue3项目骨架、登录页面、路由配置
- 完成：能注册、能登录、能跳转页面

#### 阶段2：核心功能开发（3-5天）
- 后端：文档上传、RAG检索、问答接口
- 前端：问答聊天界面、多轮对话
- 完成：能上传PDF、能问答、能显示参考来源

#### 阶段3：管理功能开发（2-3天）
- 后端：用户管理、文档管理、统计接口
- 前端：管理后台页面、图表展示
- 完成：管理员能管理用户和文档、能看到统计图表

#### 阶段4：部署和优化（1-2天）
- Docker打包、服务器部署
- 测试、修复bug、优化体验
- 完成：项目可访问、可演示

### 9.2 总工期
约10-12天完成

---

## 10. 测试方案

### 10.1 功能测试

#### 用户测试
```
1. 注册新用户 student3/123456
2. 用 student1/123456 登录
3. 提问："图书馆借书规则是什么？"
4. 验证：返回答案 + 参考来源链接
```

#### 管理员测试
```
1. 用 admin/123456 登录后台
2. 查看用户列表、文档列表
3. 上传一篇测试PDF
4. 查看统计图表是否有数据
```

### 10.2 边界测试
```
- 输入空问题 → 提示"请输入问题"
- 输入超长问题 → 正常处理或提示长度限制
- 未登录访问问答页 → 跳转登录页
- 普通用户访问管理后台 → 提示无权限
```

### 10.3 演示脚本（约5分钟）
```
1. 打开登录页面，用 admin/123456 登录
2. 展示管理后台：用户管理、文档管理、统计图表
3. 登出，用 student1/123456 登录
4. 演示问答功能：提问3个问题，展示答案和参考来源
5. 展示多轮对话：追问一个问题
6. 结束
```

---

## 11. 附录

### 11.1 完整目录结构
```
RAG-Campus-KB/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config/
│   │   │   ├── default.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   └── document.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── chat.py
│   │   │   ├── admin.py
│   │   │   └── document.py
│   │   ├── services/
│   │   │   ├── rag_service.py
│   │   │   └── sync_service.py
│   │   └── utils/
│   │       └── md5.py
│   ├── logs/
│   ├── requirements.txt
│   ├── init.sql
│   └── run.py
│
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── views/
│   │   │   ├── Login.vue
│   │   │   ├── Register.vue
│   │   │   ├── Chat.vue
│   │   │   └── admin/
│   │   │       ├── Dashboard.vue
│   │   │       ├── Users.vue
│   │   │       ├── Documents.vue
│   │   │       └── Settings.vue
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   ├── common/
│   │   │   └── chat/
│   │   ├── router/
│   │   ├── stores/
│   │   └── api/
│   └── package.json
│
├── docker-compose.yml
├── nginx.conf
├── PRD.md                      # 本文件
└── README.md
```

---

**文档版本**：v1.0  
**创建日期**：2025-06-08  
**作者**：琉璃子 & 主人
