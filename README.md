# AI小说创作系统

一个基于多Agent协作的智能小说创作平台，支持世界观管理、角色管理、大纲管理和一致性保障。

## 🚀 核心功能

- **多Agent协作写作**：三个专业Agent分工协作
  - Agent A：世界观描写（环境、氛围、魔法体系）
  - Agent B：角色对话（性格、心理、动作描写）
  - Agent C：剧情控制（整合、推进、伏笔）

- **RAG检索增强**：混合检索策略
  - 向量检索（语义相似度）
  - BM25关键词检索（精确匹配）
  - 元数据过滤（章节、时间线、角色）

- **一致性保障**：四层防护机制
  - 规则引擎（硬规则验证）
  - 知识图谱（关系验证）
  - 时间线管理（时间验证）
  - 情绪状态机（行为验证）

## 🏗️ 技术栈

**后端**
- FastAPI - 高性能API框架
- LangGraph - 多Agent编排
- LlamaIndex - RAG检索
- Qdrant - 向量数据库
- PostgreSQL - 关系数据库
- Redis - 缓存
- Neo4j - 知识图谱

**前端**
- Next.js 14 - React框架
- TailwindCSS - UI样式
- D3.js - 关系图谱可视化

**LLM**
- GPT-4o（复杂任务）
- GPT-4o-mini（简单任务）

## 📂 项目结构

```
Nai/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── main.py            # FastAPI入口
│   │   ├── api/               # API路由
│   │   ├── services/          # 业务逻辑
│   │   │   ├── agent_service.py        # 多Agent服务
│   │   │   ├── rag_service.py          # RAG检索服务
│   │   │   ├── consistency_service.py  # 一致性检查服务
│   │   ├── models/            # 数据模型
│   │   └── core/              # 核心配置
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # 前端界面
│   ├── app/                   # Next.js页面
│   ├── components/            # React组件
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml         # 容器编排
├── .env.example              # 环境变量模板
└── README.md                 # 本文件
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
cd Nai

# 复制环境变量
cp .env.example .env

# 编辑.env，填入OpenAI API密钥
# OPENAI_API_KEY=your_api_key_here
```

### 2. 启动服务

```bash
# 启动数据库（Qdrant + PostgreSQL + Redis）
docker-compose up -d

# 安装后端依赖
cd backend
pip install -r requirements.txt

# 启动后端
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端（新终端）
cd frontend
npm install
npm run dev
```

### 3. 访问系统

- 前端界面：http://localhost:3000
- 后端API文档：http://localhost:8000/docs
- Qdrant管理界面：http://localhost:6333/dashboard

## 📖 使用指南

### 创建小说项目

1. 在前端创建新小说项目
2. 定义世界观规则（魔法体系、地理等）
3. 创建角色（性格、关系、背景）
4. 规划大纲（章节、剧情点）

### 生成内容

1. 输入剧情提示词（如"主角在魔法塔顶与导师决裂"）
2. 系统自动执行三Agent工作流：
   - Agent A生成世界观描写
   - Agent B生成角色对话
   - Agent C整合并推进剧情
3. 一致性检查
4. 输出最终段落

### 管理内容

- **世界观管理**：编辑魔法规则、地理设定、历史事件
- **角色管理**：更新角色性格、关系网、情绪状态
- **大纲管理**：调整章节结构、剧情走向、伏笔

## 🔧 配置说明

### 环境变量（.env）

```env
# OpenAI API
OPENAI_API_KEY=your_key

# 数据库
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=novel_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Neo4j（知识图谱）
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

## 📊 开发路线图

- [x] 技术方案设计
- [x] 项目结构初始化
- [ ] 后端核心模块开发
  - [ ] FastAPI基础框架
  - [ ] Qdrant集成
  - [ ] LangGraph三Agent工作流
  - [ ] LlamaIndex RAG检索
  - [ ] 一致性检查系统
- [ ] 前端界面开发
  - [ ] 小说管理界面
  - [ ] 世界观管理界面
  - [ ] 角色管理界面
  - [ ] 大纲管理界面
  - [ ] 实时生成界面
- [ ] 测试与优化
- [ ] 部署上线

## 📚 文档

详细技术文档请查看 `.claude/` 目录：
- `executive-summary.md` - 执行摘要
- `technology-comparison.md` - 技术选型对比
- `ai-novel-writing-system-analysis.md` - 完整技术方案
- `quick-reference.md` - 快速参考

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📞 联系方式

如有问题，请提交Issue或联系开发者。

---

**开发时间**：2025-11-14
**版本**：Alpha 0.1.0
**状态**：开发中
