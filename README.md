# 🐳 Chat Hanbao - 智能聊天机器人

基于 Docker 的全栈聊天机器人应用，支持自然语言理解、多轮对话、会话管理。

## ✨ 功能特性

- 🤖 **智能对话** - 内置 NLU 引擎，支持意图识别和多轮上下文对话
- 💬 **实时聊天** - Web 前端界面，支持浏览器实时交互
- 📦 **会话管理** - 创建、查看、删除会话，对话历史持久化
- 🔌 **插件化 NLP** - 支持规则匹配和 LLM API 双引擎，易于扩展
- 📊 **数据持久化** - PostgreSQL 存储对话历史，Redis 缓存会话上下文
- 🐳 **一键部署** - Docker Compose 编排，一键启动所有服务
- 📝 **日志记录** - 结构化日志，支持文件轮转和分级输出

## 🏗️ 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python + FastAPI + SQLAlchemy (异步) |
| 前端 | React + Vite + Axios |
| 数据库 | PostgreSQL 16 |
| 缓存 | Redis 7 |
| 编排 | Docker Compose |

## 🚀 快速开始

### 前置条件

- Docker Desktop 或 Docker Engine 20.10+
- Docker Compose v2.0+

### 一键启动

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd chat-hanbao

# 2. 启动所有服务
docker compose up -d

# 3. 查看日志
docker compose logs -f
```

### 访问应用

| 服务 | 地址 | 端口 |
|------|------|------|
| 🌐 Web 前端 | http://localhost:8373 | 8373 |
| 📚 API 文档 | http://localhost:8399/docs | 8399 |
| 🔧 后端 API | http://localhost:8399 | 8399 |
| 🗄️ PostgreSQL | localhost:5632 | 5632 |
| ⚡ Redis | localhost:6399 | 6399 |

> 端口映射已设置为冷门端口，避免与飞牛 NAS 已有服务冲突。如需修改，编辑 `docker-compose.yml` 中 `services.xxx.ports` 的左侧宿主机端口。

### 停止服务

```bash
docker compose down

# 同时删除数据卷（清空数据库）
docker compose down -v
```

## 📁 项目结构

```
chat-hanbao/
├── docker-compose.yml          # Docker 编排文件
├── .env                        # 环境变量
├── README.md                   # 项目文档
│
├── backend/                    # 后端服务
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── main.py             # FastAPI 入口
│       ├── config.py           # 配置管理
│       ├── database.py         # 数据库连接
│       ├── models/             # 数据模型
│       │   ├── session.py      # 会话模型
│       │   └── conversation.py # 消息模型
│       ├── routers/            # API 路由
│       │   ├── chat.py         # 聊天接口
│       │   ├── sessions.py     # 会话管理接口
│       │   └── health.py       # 健康检查
│       ├── services/           # 业务逻辑
│       │   ├── nlu_engine.py   # NLU 引擎
│       │   ├── chat_manager.py # 对话管理器
│       │   └── redis_client.py# Redis 客户端
│       └── utils/
│           └── logger.py       # 日志配置
│
└── frontend/                   # 前端服务
    ├── Dockerfile
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.jsx            # React 入口
        ├── App.jsx             # 主应用
        ├── components/
        │   ├── ChatWindow.jsx  # 聊天窗口
        │   └── Sidebar.jsx     # 侧边栏
        ├── services/
        │   └── api.js          # API 客户端
        └── styles/             # 样式文件
```

## 📡 API 接口

### 聊天接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/chat/send` | 发送消息获取回复 |
| GET | `/api/chat/history/{session_id}` | 获取会话历史 |
| DELETE | `/api/chat/history/{session_id}` | 清除会话历史 |

### 会话管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/sessions/create` | 创建新会话 |
| GET | `/api/sessions/list` | 获取会话列表 |
| GET | `/api/sessions/{id}` | 获取会话详情 |
| DELETE | `/api/sessions/{id}` | 删除会话 |

### 健康检查

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 基础健康检查 |
| GET | `/health/db` | 数据库健康检查 |

## 🔧 配置说明

通过 `.env` 文件或环境变量配置：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DATABASE_URL` | `postgresql+asyncpg://chatuser:chatpass@postgres:5432/chatdb` | 数据库连接 |
| `REDIS_URL` | `redis://redis:6379/0` | Redis 连接 |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | 跨域白名单 |
| `NLP_ENGINE` | `rule` | NLU 引擎类型 (rule/llm_api) |
| `LLM_API_URL` | - | LLM API 地址 |
| `LLM_API_KEY` | - | LLM API 密钥 |
| `LOG_LEVEL` | `INFO` | 日志级别 |

## 🧩 扩展指南

### 接入 LLM API

修改 `.env` 配置：

```env
NLP_ENGINE=llm_api
LLM_API_URL=https://api.openai.com/v1/chat/completions
LLM_API_KEY=sk-your-api-key
```

然后在 `nlu_engine.py` 中扩展 `LLMEngine` 类。

### 添加新意图

在 `nlu_engine.py` 的 `INTENT_RULES` 字典中添加：

```python
"new_intent": {
    "patterns": [r"关键词1", r"关键词2"],
    "responses": ["回复1", "回复2"],
},
```

### 添加新 API 端点

1. 在 `app/routers/` 下创建新路由文件
2. 在 `app/main.py` 中注册路由

## 📝 日志

日志文件位于 `logs/` 目录：

- `app.log` - 应用日志（INFO 级别）
- `error.log` - 错误日志（ERROR 级别）

## 📄 协议

MIT License
