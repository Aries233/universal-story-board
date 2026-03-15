# Universal Story Board (USB)

> 一站式网文转分镜/漫剧脚本平台 —— 从文字到视觉的 AI 协作流水线

## 项目简介

Universal Story Board 是一个面向创作者的 **零门槛、全自动化** 网文视觉化翻译平台。通过多模态 AI 协作流水线，将长达数万字的长篇网文，在保持剧情连贯性的前提下，转换为可用于动画、漫剧、短视频制作的分镜脚本及视觉资产库。

## 核心特性

- 🎯 **双轨制作模式**: 改编编剧模式（AI 改写 + 审核流程）与原文模式（直接拆解）并行
- 🔗 **长文本连贯性**: 全局项目状态管理，自动继承角色和场景设定
- 🤖 **多 Agent 协作**: 编剧 → 剧本医生 → 角色设计师 → 场景设计师 → 分镜导演
- 🏷️ **实体链接可视化**: 角色和场景转化为可交互的 Tag，点击查看详情
- 📊 **进度管理大盘**: 实时追踪剧本拆解及生成进度
- 🔌 **多模型动态配置**: 支持智谱、千问、Gemini、OpenAI 等多服务商切换
- 🔐 **API Key 加密存储**: AES-256 加密存储，保障安全

## 项目状态

- 🎬 **当前阶段**: Step 4 - 基础业务 API 开发
- 📄 **文档**: [PRD.md](./docs/PRD.md) | [Architecture.md](./docs/Architecture.md)
- ✅ **完成**: Step 1（PRD）→ Step 2（架构设计）→ Step 3（后端初始化）→ Step 4-A（基础 API）

## 目录结构

```
universal-story-board/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/v1/            # API 路由
│   │   │   ├── system.py       # 系统配置 API
│   │   │   ├── projects.py     # 项目管理 API
│   │   │   ├── chapters.py     # 章节管理 API
│   │   │   └── assets.py      # 资产管理 API
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # Pydantic Schemas
│   │   ├── services/          # 业务逻辑层
│   │   ├── utils/             # 工具函数
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 数据库连接
│   │   └── main.py            # FastAPI 入口
│   ├── requirements.txt        # Python 依赖
│   ├── .env.example           # 环境变量示例
│   └── test_api.py            # API 测试脚本
│
├── docs/                       # 项目文档
│   ├── PRD.md                 # 产品需求文档
│   └── Architecture.md         # 架构设计文档
│
├── STEP3_VERIFICATION_REPORT.md  # Step 3 验证报告
├── STEP4A_API_REPORT.md         # Step 4-A API 开发报告
├── README.md                    # 项目说明
└── .gitignore                   # Git 忽略规则
```

## 技术栈

### 后端技术栈

| 组件 | 技术选型 | 版本 | 说明 |
|------|----------|------|------|
| **语言** | Python | 3.11+ | AI 原生、类型注解强 |
| **Web 框架** | FastAPI | 0.109+ | 高性能、异步支持、自动生成 OpenAPI |
| **数据验证** | Pydantic | 2.5+ | 严格约束大模型 JSON 输出 |
| **ORM** | SQLModel | 0.0.14+ | SQLAlchemy + Pydantic 完美结合 |
| **数据库** | SQLite | 3.40+ | 轻量级、单文件、MVP 首选 |
| **异步框架** | asyncio + uvicorn | - | Python 原生异步 |
| **加密工具** | cryptography | 42.0.5+ | AES-256 加密存储 |
| **HTTP 客户端** | httpx | 0.26.0+ | 异步 HTTP 请求 |

### AI 模型支持

- **文本大模型**: GLM-4-Plus/Long、千问 Max、Gemini Pro、GPT-4 Turbo
- **文生图模型**: CogView-3、SD3、DALL-E 3
- **文生视频模型**: Sora2、Runway Gen-2

## 本地部署指南

### 1. 环境要求

- Python 3.11+
- pip 或 virtualenv

### 2. 安装依赖

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件
vim .env
```

**重要配置项**:

```bash
# 加密密钥（首次运行时会自动生成，建议复制到 .env 文件）
ENCRYPTION_KEY=your_generated_key_here

# 其他配置项（可选）
DATABASE_URL=sqlite:///./usb.db
DEBUG=True
LOG_LEVEL=INFO
```

### 4. 启动服务

```bash
# 启动 FastAPI 服务
python -m app.main

# 或使用 uvicorn 直接启动
uvicorn app.main:app --reload --port 8000
```

**预期输出**:
```
✅ Universal Story Board v1.0.0 启动成功
📦 数据库: sqlite:///./usb.db
🔌 支持的多模型路由: 文本/图片/视频
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 5. 访问 API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

### 6. 测试 API

```bash
# 运行 API 测试脚本
python test_api.py
```

## 云服务器部署指南

### 1. 服务器环境要求

- Ubuntu 20.04+ / CentOS 8+
- Python 3.11+
- 至少 1GB 内存

### 2. 安装 Python 依赖

```bash
# 安装 Python 3.11（如果系统版本较低）
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# 创建虚拟环境
cd /path/to/universal-story-board/backend
python3.11 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 生成加密密钥（如果首次运行）
# 启动服务后会自动生成，复制到 .env 文件
```

### 5. 启动服务

```bash
# 启动服务
python -m app.main

# 或使用 nohup 后台运行
nohup python -m app.main > app.log 2>&1 &
```

### 6. 验证服务

```bash
# 健康检查
curl http://localhost:8000/health

# 查看日志
tail -f app.log
```

### 7. 配置防火墙（可选）

```bash
# 开放 8000 端口
sudo ufw allow 8000/tcp
```

### 8. 使用 Systemd 管理服务（生产环境推荐）

创建 `/etc/systemd/system/usb.service`:

```ini
[Unit]
Description=Universal Story Board API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/universal-story-board/backend
Environment="PATH=/path/to/universal-story-board/backend/venv/bin"
ExecStart=/path/to/universal-story-board/backend/venv/bin/python -m app.main
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务:

```bash
sudo systemctl daemon-reload
sudo systemctl enable usb
sudo systemctl start usb
sudo systemctl status usb
```

## API 文档

### 系统配置 API

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 获取凭证列表 | GET | `/api/v1/system/credentials` | - |
| 创建凭证 | POST | `/api/v1/system/credentials` | API Key 自动加密 |
| 更新凭证 | PUT | `/api/v1/system/credentials/{id}` | - |
| 删除凭证 | DELETE | `/api/v1/system/credentials/{id}` | - |
| 获取路由配置 | GET | `/api/v1/system/route-configs` | - |
| 更新路由配置 | PUT | `/api/v1/system/route-configs/{id}` | - |
| 获取系统配置 | GET | `/api/v1/system/config` | 汇总配置 |

### 项目管理 API

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 获取项目列表 | GET | `/api/v1/projects` | 支持分页 |
| 获取项目详情 | GET | `/api/v1/projects/{id}` | - |
| 创建项目 | POST | `/api/v1/projects` | - |
| 更新项目 | PUT | `/api/v1/projects/{id}` | - |
| 删除项目 | DELETE | `/api/v1/projects/{id}` | - |

## 开发指南

### 运行测试

```bash
cd backend
python test_api.py
```

### 代码规范

- 使用 `black` 格式化代码
- 使用 `isort` 排序导入
- 添加类型注解
- 编写中文注释

### 提交代码

```bash
git add .
git commit -m "feat: 添加新功能"
git push
```

## 产品愿景

> 「网文的视觉化翻译引擎」 — 不是简单的文本生成工具，而是具备工业级工作流的 AI 协作平台，支持长篇项目的资产沉淀与版本管理。

## 联系方式

- **产品架构师**: 虎斑 🐯
- **创建日期**: 2026-03-15
- **GitHub**: https://github.com/Aries233/universal-story-board

## License

MIT License

---

**Universal Story Board** - 让网文创作更简单！ 🚀
