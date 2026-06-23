# 基于LangChain的RAG校园内部知识库问答系统与优化构建

## 📋 项目概述

本项目是一个基于RAG（Retrieval Augmented Generation）架构的校园内部知识库问答系统，针对广西师范大学的校园信息进行智能问答。系统通过检索增强生成技术，将大语言模型与学校知识库结合，提供准确、可追溯的问答服务。

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                      用户浏览器                          │
└────────────────────────────┬────────────────────────────┘
                             │ HTTP
                             ▼
┌─────────────────────────────────────────────────────────┐
│                  前端层 (Vue3 + Element Plus)            │
│    登录页面 │ 注册页面 │ 问答页面 │ 管理后台              │
└────────────────────────────┬────────────────────────────┘
                             │ RESTful API
                             ▼
┌─────────────────────────────────────────────────────────┐
│                  后端层 (Python + Flask)                 │
│    认证服务 │ 问答服务 │ 文档服务 │ 统计服务              │
└────────────────────────────┬────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│    MySQL     │    │    Chroma    │    │    Ollama    │
│   (元数据)   │    │   (向量库)   │    │  (嵌入模型)  │
└──────────────┘    └──────────────┘    └──────────────┘
                             │
                             ▼
                    ┌──────────────┐
                    │   Deepseek   │
                    │   (LLM)     │
                    └──────────────┘
```

## 🛠️ 技术栈

### 前端
- **Vue3** - 渐进式JavaScript框架
- **Element Plus** - Vue3 UI组件库
- **Vite** - 下一代前端构建工具
- **Axios** - HTTP客户端

### 后端
- **Python 3.x** - 编程语言
- **Flask** - 轻量级Web框架
- **SQLAlchemy** - Python SQL工具包和ORM
- **PyMySQL** - MySQL驱动

### 数据库
- **MySQL 8.0** - 关系型数据库（存储用户、文档元数据）
- **Chroma** - 向量数据库（存储文档向量）

### AI模型
- **Ollama** - 本地大模型运行框架
- **qwen3-embedding:4b** - 嵌入模型（文本向量化）
- **Deepseek** - 大语言模型（答案生成）

### 评估框架
- **RAGas** - RAG系统评估框架
- **Datasets** - 数据集处理库

## ✨ 功能特性

### 用户功能
- ✅ 用户注册与登录
- ✅ 智能问答（基于RAG）
- ✅ 多轮对话（保留最近20轮上下文）
- ✅ 参考来源展示
- ✅ 参考来源链接点击跳转

### 管理员功能
- ✅ 数据统计看板
- ✅ 文档管理（上传、删除、编辑）
- ✅ 用户管理（查看、禁用、重置密码）
- ✅ 系统设置（定时同步配置）

### 数据采集
- ✅ 广西师范大学官网全站采集（48个栏目）
- ✅ 22个院系网站深度采集
- ✅ 国际文化教育学院深度采集（25个栏目）
- ✅ 19个党政群团部门深度采集
- ✅ 公共服务、后勤服务集团采集
- ✅ 支持PDF、HTM、网页等多种格式

### 评估系统
- ✅ RAGas自动化评估
- ✅ 四项核心指标：Faithfulness、Answer Relevancy、Context Precision、Context Recall
- ✅ 自定义评估脚本

## 📁 项目结构

```
RAG/
├── RAG/
│   ├── backend/                    # 后端代码
│   │   ├── app/
│   │   │   ├── __init__.py        # Flask应用初始化
│   │   │   ├── config/            # 配置文件
│   │   │   │   ├── default.py     # 默认配置
│   │   │   │   ├── development.py # 开发环境
│   │   │   │   └── production.py  # 生产环境
│   │   │   ├── models/            # 数据库模型
│   │   │   │   ├── user.py        # 用户模型
│   │   │   │   └── document.py    # 文档模型
│   │   │   ├── routes/            # API路由
│   │   │   │   ├── auth.py        # 认证接口
│   │   │   │   ├── chat.py        # 问答接口
│   │   │   │   ├── admin.py       # 管理接口
│   │   │   │   └── document.py    # 文档接口
│   │   │   └── services/          # 业务逻辑
│   │   │       ├── chat_service.py    # 问答服务
│   │   │       ├── rag_service.py     # RAG检索服务
│   │   │       ├── document_service.py # 文档服务
│   │   │       ├── embedding_service.py # 嵌入服务
│   │   │       └── sync_service.py    # 同步服务
│   │   ├── crawlers/              # 爬虫模块
│   │   ├── logs/                  # 日志文件
│   │   ├── crawl_*.py             # 各种爬虫脚本
│   │   ├── evaluate_rag.py        # RAG评估脚本
│   │   ├── evaluate_with_ragas.py # RAGas评估脚本
│   │   ├── requirements.txt       # 依赖包
│   │   └── run.py                 # 启动文件
│   ├── frontend/                  # 前端代码
│   │   ├── src/
│   │   │   ├── views/             # 页面组件
│   │   │   ├── api/               # API接口
│   │   │   ├── router/            # 路由配置
│   │   │   └── main.js            # 入口文件
│   │   └── package.json
│   └── chroma/                    # Chroma数据
├── uploads/                       # 上传文件
├── PRD.md                         # 产品需求文档
├── docker-compose.yml             # Docker配置
└── README.md                      # 项目说明
```

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Node.js 16+
- MySQL 8.0
- Ollama

### 1. 克隆项目

```bash
git clone https://github.com/xhuhao/RAG.git
cd RAG
```

### 2. 安装后端依赖

```bash
cd RAG/backend
pip install -r requirements.txt
```

### 3. 配置数据库

```sql
-- 创建数据库
CREATE DATABASE db_enterprise_ga CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 导入初始化数据
mysql -u root -p db_enterprise_ga < init.sql
```

### 4. 配置环境变量

编辑 `RAG/backend/app/config/default.py`：

```python
# MySQL配置
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3308
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'your_password'
MYSQL_DB = 'db_enterprise_ga'

# Chroma配置
CHROMA_HOST = 'localhost'
CHROMA_PORT = 8000

# Ollama配置
OLLAMA_HOST = 'localhost'
OLLAMA_PORT = 11434
OLLAMA_MODEL = 'qwen3-embedding:4b'

# Deepseek配置
DEEPSEEK_API_KEY = 'your_api_key'
DEEPSEEK_MODEL = 'deepseek-v4-pro'
```

### 5. 启动服务

```bash
# 启动MySQL
net start MySQL80

# 启动Chroma
cd RAG
chroma run --host localhost --port 8000

# 启动Ollama
ollama serve

# 拉取嵌入模型
ollama pull qwen3-embedding:4b

# 启动后端
cd RAG/backend
python run.py
```

### 6. 安装前端依赖并启动

```bash
cd RAG/frontend
npm install
npm run dev
```

### 7. 访问系统

- 前端地址：http://localhost:5173
- 后端API：http://localhost:5000

### 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | 123456 |
| 测试用户 | student1 | 123456 |
| 测试用户 | student2 | 123456 |

## 📊 数据采集

### 采集脚本

项目提供多个爬虫脚本用于数据采集：

```bash
cd RAG/backend

# 批量采集所有栏目
python crawl_all_v2.py

# 深度采集22个院系
python crawl_colleges_deep.py

# 深度采集国际文化教育学院
python crawl_cice_deep.py

# 深度采集党政群团部门
python crawl_departments_all.py

# 深度采集部门和服务网站
python crawl_departments_deep.py
```

### 数据统计

| 类别 | 文档数量 |
|------|----------|
| 学校概况 | 40+ |
| 机构设置 | 60+ |
| 22个院系 | 600+ |
| 新闻资讯 | 200+ |
| 党政群团部门 | 400+ |
| 国际交流 | 300+ |
| 公共服务 | 100+ |
| **总计** | **1906篇** |

## 📈 评估系统

### 使用RAGas评估

```bash
cd RAG/backend
python evaluate_with_ragas.py
```

### 评估指标

| 指标 | 说明 | 当前分数 |
|------|------|----------|
| Faithfulness | 回答是否基于文档 | 51.51% |
| Answer Relevancy | 回答与问题相关性 | 86.27% |
| Context Precision | 检索文档精确度 | 78.33% |
| Context Recall | 检索文档召回率 | 52.50% |
| **综合评分** | - | **67.50%** |

### 优化方案

| 优化项 | 当前值 | 建议值 | 预期提升 |
|--------|--------|--------|----------|
| LLM提示词 | 通用约束 | 严格约束 | +15-20% |
| Temperature | 0.2 | 0.1 | +5-10% |
| Top K | 3 | 5 | +10-15% |
| Chunk Size | 1000 | 800 | +5-10% |
| Chunk Overlap | 200 | 300 | +5-10% |

## 🔧 API接口

### 认证模块 `/api/auth`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 用户注册 |
| POST | /api/auth/login | 用户登录 |
| GET | /api/auth/logout | 用户登出 |
| GET | /api/auth/info | 获取用户信息 |

### 问答模块 `/api/chat`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/chat/ask | 提问 |

### 文档模块 `/api/documents`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/documents | 获取文档列表 |
| POST | /api/documents | 上传文档 |
| DELETE | /api/documents/:id | 删除文档 |
| PUT | /api/documents/:id | 更新文档 |

### 统计模块 `/api/stats`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/stats/overview | 总览数据 |
| GET | /api/stats/trends | 问答趋势 |
| GET | /api/stats/hot-questions | 热门问题 |

## 🐳 Docker部署

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 📝 开发说明

### 目录说明

- `RAG/backend/app/config/` - 配置文件，包含数据库、模型等配置
- `RAG/backend/app/services/` - 业务逻辑层，包含问答、检索、文档等服务
- `RAG/backend/crawlers/` - 爬虫模块，用于数据采集
- `RAG/frontend/src/views/` - 前端页面组件

### 添加新的数据源

1. 在 `crawlers/` 目录下创建新的爬虫
2. 在 `sync_service.py` 中添加同步逻辑
3. 运行爬虫采集数据

### 修改嵌入模型

编辑 `RAG/backend/app/config/default.py`：

```python
OLLAMA_MODEL = 'your_model_name'
```

### 修改LLM模型

编辑 `RAG/backend/app/config/default.py`：

```python
DEEPSEEK_API_KEY = 'your_api_key'
DEEPSEEK_MODEL = 'your_model_name'
```

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 👥 作者

- **许昊** - [GitHub](https://github.com/xhuhao)

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - RAG框架
- [Chroma](https://github.com/chroma-core/chroma) - 向量数据库
- [Ollama](https://github.com/ollama/ollama) - 本地大模型框架
- [RAGas](https://github.com/explodinggradients/ragas) - RAG评估框架
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [Vue3](https://vuejs.org/) - 前端框架
- [Element Plus](https://element-plus.org/) - UI组件库

---

**广西师范大学** | **基于LangChain的RAG校园内部知识库问答系统与优化构建**
