# AI写小说软件技术方案 - 文档索引

**生成时间**: 2025-11-14
**项目**: AI驱动的多Agent协作小说创作系统
**技术栈**: LangGraph + LlamaIndex + Qdrant + FastAPI + Next.js

---

## 📚 文档导航

### 🚀 快速开始（3分钟）
**阅读**: [executive-summary.md](./executive-summary.md)

**你会了解**:
- 推荐技术栈是什么
- 系统架构长什么样
- 核心技术亮点有哪些
- 开发路线图（MVP到Production）
- 成本估算（$580-880/月）

---

### 🔍 技术选型对比（10分钟）
**阅读**: [technology-comparison.md](./technology-comparison.md)

**你会了解**:
- 为什么选LangGraph而不是AutoGen或CrewAI？
- 为什么选LlamaIndex而不是LangChain？
- 为什么选Qdrant而不是Pinecone、Milvus或ChromaDB？
- LLM模型成本对比（GPT-4o vs GPT-4o-mini vs Claude vs Gemini）
- 向量数据库性能对比表

---

### 📖 完整技术方案（60分钟深度阅读）
**阅读**: [ai-novel-writing-system-analysis.md](./ai-novel-writing-system-analysis.md)

**你会了解**:
- 详细的系统架构设计（前端→后端→Agent→RAG→存储）
- 数据模型设计（PostgreSQL表结构 + Qdrant向量集合）
- RAG实现策略（分层Chunking + 混合检索 + 上下文管理）
- 多Agent协作机制（LangGraph工作流 + 通信协议 + 冲突解决）
- 关键技术挑战与解决方案（长文本连贯性、角色一致性、剧情逻辑性、世界观一致性）
- 风险点与缓解措施（LLM幻觉、成本控制、性能优化）
- 开发优先级建议（4个阶段，共20周）

**核心章节**:
- 第二章：推荐技术栈（含详细理由）
- 第三章：系统架构设计（架构图 + 数据流）
- 第五章：RAG实现策略（Chunking + 检索 + 一致性保障）
- 第六章：多Agent协作机制（Agent定义 + 通信协议 + 冲突解决）
- 第七章：关键技术挑战与解决方案

---

### 💻 快速参考（开发必备）
**阅读**: [quick-reference.md](./quick-reference.md)

**你会获得**:
- 技术决策树（30秒快速决策）
- 可复制的代码示例：
  - LlamaIndex基础RAG（5分钟搭建）
  - LangGraph三Agent工作流（核心框架）
  - Qdrant向量检索（元数据过滤）
  - FastAPI流式输出（WebSocket实时生成）
  - 角色一致性检查（Persona验证）
  - 成本优化：响应缓存
- 常见问题速查（6个FAQ）
- 故障排查速查（4个常见问题）
- 开发检查清单（MVP→Production）

---

### 📝 操作日志
**阅读**: [operations-log.md](./operations-log.md)

**内容**:
- 信息检索过程记录
- 技术决策理由
- 完成的输出清单

---

## 🎯 核心技术方案速览

### 推荐技术栈

```
┌─────────────────────────────────────────┐
│  前端: Next.js 14 + TailwindCSS          │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│  后端: FastAPI + PostgreSQL + Redis      │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│  多Agent编排: LangGraph                  │
│  RAG检索: LlamaIndex                     │
└────┬─────────────────────┬──────────────┘
     │                     │
┌────▼────────┐   ┌────────▼──────────────┐
│ 向量数据库   │   │ LLM推理               │
│ Qdrant      │   │ GPT-4o + GPT-4o-mini  │
└─────────────┘   └───────────────────────┘
```

### 核心技术亮点

1. **分层记忆系统**
   - Core Memory（世界观规则）
   - Working Memory（当前章节上下文）
   - Semantic Memory（可检索知识库）

2. **混合检索策略**
   - 向量检索（语义相似）
   - BM25关键词检索（精确匹配）
   - 元数据过滤（章节范围/角色筛选）

3. **三Agent协作**
   - Agent A: 世界观描写（环境、氛围）
   - Agent B: 角色对话（对话、心理）
   - Agent C: 剧情控制（整合、推进）

4. **一致性保障**
   - 规则引擎（世界观硬规则）
   - 知识图谱（地理/角色关系验证）
   - 情绪状态机（角色情绪追踪）

---

## 💰 成本与开发周期

### 运营成本（中等规模，100用户同时在线）

| 项目 | 选型 | 月成本 |
|-----|-----|--------|
| 服务器 | 8核16GB VPS | $80 |
| 向量数据库 | Qdrant自托管 | $0（包含在服务器） |
| 关系数据库 | PostgreSQL自托管 | $0（包含在服务器） |
| LLM API | GPT-4o-mini（70%）+ GPT-4o（30%） | $500-800 |
| **总计** | - | **$580-880** |

### 开发路线图

| 阶段 | 周期 | 目标 | 验收标准 |
|-----|-----|------|---------|
| **MVP** | 2周 | 验证可行性 | 输入指令，输出500字段落 |
| **Alpha** | 4周 | 多Agent系统 | 生成完整章节（3000字） |
| **Beta** | 6周 | 一致性保障 | 生成10章小说，零矛盾 |
| **Production** | 8周 | 完整产品 | 用户就绪，可上线 |

**总计**: 20周（约5个月）

---

## 🚀 立即开始（30分钟搭建MVP原型）

### 步骤1: 安装依赖（5分钟）

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install llama-index qdrant-client openai langchain langgraph fastapi uvicorn
```

### 步骤2: 启动Qdrant（2分钟）

```bash
docker run -d -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```

### 步骤3: 创建基础RAG系统（10分钟）

参考 [quick-reference.md](./quick-reference.md) 中的"2.1 LlamaIndex基础RAG"代码示例。

### 步骤4: 测试生成（5分钟）

```bash
python main.py
# 输入：主角在魔法塔顶与导师决裂
# 输出：500字段落
```

### 步骤5: 集成LangGraph多Agent（10分钟）

参考 [quick-reference.md](./quick-reference.md) 中的"2.2 LangGraph三Agent工作流"代码示例。

---

## 📞 技术支持

### 官方文档
- LangGraph: https://langchain-ai.github.io/langgraph/
- LlamaIndex: https://docs.llamaindex.ai/
- Qdrant: https://qdrant.tech/documentation/

### 遇到问题？
参考 [quick-reference.md](./quick-reference.md) 中的"五、故障排查速查"章节。

---

## 📋 文档清单

| 文件名 | 大小 | 描述 | 阅读时间 |
|-------|-----|------|---------|
| [executive-summary.md](./executive-summary.md) | 13KB | 执行摘要 | 3分钟 |
| [technology-comparison.md](./technology-comparison.md) | 15KB | 技术选型对比 | 10分钟 |
| [ai-novel-writing-system-analysis.md](./ai-novel-writing-system-analysis.md) | 55KB | 完整技术方案 | 60分钟 |
| [quick-reference.md](./quick-reference.md) | 17KB | 快速参考指南 | 20分钟 |
| [operations-log.md](./operations-log.md) | 2.6KB | 操作日志 | 5分钟 |

**总计**: 6个文件，150KB文档

---

## ✅ 推荐阅读路径

### 路径1: 决策者（15分钟）
1. [executive-summary.md](./executive-summary.md) - 了解方案概览
2. [technology-comparison.md](./technology-comparison.md) - 理解技术选型

### 路径2: 架构师（90分钟）
1. [executive-summary.md](./executive-summary.md) - 快速了解
2. [ai-novel-writing-system-analysis.md](./ai-novel-writing-system-analysis.md) - 深度阅读
3. [technology-comparison.md](./technology-comparison.md) - 技术对比

### 路径3: 开发者（60分钟）
1. [executive-summary.md](./executive-summary.md) - 快速了解
2. [quick-reference.md](./quick-reference.md) - 代码示例和FAQ
3. [ai-novel-writing-system-analysis.md](./ai-novel-writing-system-analysis.md)（第五、六章）- RAG和多Agent实现细节

---

## 🎓 关键学习要点

阅读完所有文档后，你将掌握：

✅ 如何选择适合AI小说创作的技术栈
✅ 如何设计多Agent协作系统（LangGraph）
✅ 如何实现高性能RAG检索（LlamaIndex + Qdrant）
✅ 如何保障长篇小说的一致性（记忆系统 + 规则引擎）
✅ 如何控制LLM API成本（缓存 + 模型分级 + 本地模型）
✅ 如何实现实时流式生成（WebSocket）
✅ 如何处理长文本生成的连贯性问题
✅ 如何确保角色性格不崩坏（Persona固化 + 情绪状态机）

---

**文档版本**: v1.0
**最后更新**: 2025-11-14
**作者**: Claude (Anthropic)
**联系方式**: 查看项目仓库README
