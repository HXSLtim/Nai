# AI写小说软件技术方案 - 执行摘要

**生成时间**: 2025-11-14
**完整文档**: [ai-novel-writing-system-analysis.md](./ai-novel-writing-system-analysis.md)

---

## 一、推荐技术栈（一句话总结）

```
LangGraph（多Agent编排） + LlamaIndex（RAG检索） + Qdrant（向量数据库）
+ FastAPI（后端） + Next.js（前端） + PostgreSQL（关系数据库）
```

---

## 二、核心架构（3分钟理解）

### 2.1 系统分层

```
┌─────────────────────────────────────────┐
│  前端层: Next.js                         │
│  - 小说编辑器                            │
│  - 世界观/角色/大纲管理界面              │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│  API层: FastAPI                          │
│  - 内容生成API                           │
│  - 检索API                               │
│  - 管理API                               │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│  多Agent层: LangGraph                    │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │Agent A:  │→ │Agent B:  │→ │Agent C:││
│  │世界观描写│  │角色对话  │  │剧情控制││
│  └──────────┘  └──────────┘  └────────┘│
└───────┬───────────────┬─────────────────┘
        │               │
┌───────▼──────┐  ┌────▼─────────────────┐
│  RAG检索层    │  │  LLM推理层           │
│  LlamaIndex   │  │  GPT-4o / 本地模型   │
└───────┬──────┘  └──────────────────────┘
        │
┌───────▼──────────────────────────────────┐
│  数据存储层                               │
│  Qdrant（向量） + PostgreSQL（结构化）    │
└──────────────────────────────────────────┘
```

### 2.2 数据流

```
用户输入剧情指令
    ↓
RAG检索（世界观 + 角色 + 大纲）
    ↓
Agent A: 世界观描写（环境、氛围）
    ↓
Agent B: 角色对话（对话、心理）
    ↓
Agent C: 剧情控制（整合、推进）
    ↓
一致性检查（规则引擎 + 知识图谱）
    ↓
输出最终章节内容
```

---

## 三、技术选型理由（为什么选这些技术）

| 技术 | 选择理由 | 替代方案 |
|-----|---------|---------|
| **LangGraph** | ✅ 图结构控制，适合"世界观→角色→剧情"层级依赖<br>✅ 状态管理，支持长篇连续性<br>✅ 确定性工作流，避免剧情失控 | AutoGen（对话式，易发散）<br>CrewAI（原型快但控制弱） |
| **LlamaIndex** | ✅ 2025年检索准确率提升35%<br>✅ 内置Query Engines/Routers/Fusers<br>✅ 学习曲线友好，适合快速构建 | LangChain（更适合复杂工作流） |
| **Qdrant** | ✅ 开源，无使用费用<br>✅ 强大元数据过滤（按章节/时间线/角色）<br>✅ Rust高性能，内存占用小 | Pinecone（贵）<br>Milvus（运维复杂）<br>ChromaDB（功能有限） |

---

## 四、核心技术亮点

### 4.1 分层记忆系统（解决一致性问题）

```python
class NovelAgentMemory:
    # 核心记忆（永久，不遗忘）
    core_memory = {
        "worldview_rules": {},    # 世界观硬规则（如魔法设定）
        "character_profiles": {}, # 角色核心性格
        "plot_constraints": {}    # 剧情约束（如已死亡角色）
    }

    # 工作记忆（当前章节上下文）
    working_memory = {
        "current_chapter": None,
        "active_characters": [],
        "recent_events": []  # 最近5个事件
    }

    # 语义记忆（可检索知识库）
    semantic_memory = {
        "worldview_index": None,  # LlamaIndex索引
        "character_index": None,
        "plot_index": None
    }
```

### 4.2 混合检索策略（提升召回率）

```
向量检索（语义相似）
    +
BM25关键词检索（精确匹配）
    +
元数据过滤（章节范围/角色筛选）
    ↓
倒数排序融合（Reciprocal Rank Fusion）
    ↓
输出Top 5相关内容
```

### 4.3 三Agent协作机制

| Agent | 职责 | 输入 | 输出 |
|-------|-----|------|------|
| **Agent A<br>世界观描写** | 环境渲染<br>氛围营造 | 剧情指令 + 世界观库 | 200-300字环境描写 |
| **Agent B<br>角色对话** | 角色对话<br>心理描写 | Agent A输出 + 角色性格库 | 符合性格的对话和心理 |
| **Agent C<br>剧情控制** | 整合内容<br>推进剧情 | Agent A+B输出 + 大纲库 | 完整段落 + 剧情决策 |

### 4.4 一致性保障机制

```
┌─────────────────────────────────────────┐
│  1. 规则引擎                             │
│     - 魔法等级限制                       │
│     - 角色能力边界                       │
│     - 物理规则约束                       │
└─────────────────────────────────────────┘
         +
┌─────────────────────────────────────────┐
│  2. 知识图谱                             │
│     - 地理关系验证                       │
│     - 角色关系网                         │
│     - 历史事件时间线                     │
└─────────────────────────────────────────┘
         +
┌─────────────────────────────────────────┐
│  3. 情绪状态机                           │
│     - 追踪角色情绪变化                   │
│     - 验证情绪转换合理性                 │
└─────────────────────────────────────────┘
```

---

## 五、数据模型（核心表结构）

### 5.1 PostgreSQL（结构化数据）

```sql
novels（小说元数据）
├── chapters（章节）
├── worldview_elements（世界观元素）
│   ├── category: geography, history, magic_system
│   └── timeline_position
├── characters（角色）
│   ├── personality_traits（性格特质）
│   └── character_arc（成长轨迹）
├── character_relationships（角色关系）
└── plot_points（剧情点/伏笔）
```

### 5.2 Qdrant（向量集合）

```
worldview（世界观向量）
├── payload: category, timeline_position, chapter_range
│
characters（角色向量）
├── payload: personality_summary, dialogue_style, emotional_state
│
plot_outline（大纲向量）
├── payload: plot_type, tension_level, foreshadowing_ids
│
generated_content（已生成内容向量）
└── payload: chapter_number, involved_characters, worldview_tags
```

---

## 六、关键挑战与解决方案

### 挑战1: 长文本连贯性（百万字级别小说）

**解决方案**:
- ✅ 分层摘要压缩（最近3章用详细摘要，更早章节用单段摘要）
- ✅ 关键事件索引（向量化重要剧情点）
- ✅ 滑动窗口上下文管理（保留高优先级内容）

### 挑战2: 角色一致性

**解决方案**:
- ✅ 角色Persona固化（核心性格 + 禁忌行为 + 历史对话示例）
- ✅ 情绪状态机（追踪情绪转换）
- ✅ OOC检测（验证对话是否Out of Character）

### 挑战3: 剧情逻辑性

**解决方案**:
- ✅ 剧情图谱（Plot Graph，DAG结构管理事件依赖）
- ✅ 时间线管理器（防止时间线矛盾）
- ✅ 伏笔追踪（确保伏笔被解决）

### 挑战4: 成本控制

**解决方案**:
- ✅ 响应缓存（相同prompt零成本）
- ✅ 模型分级（简单任务用gpt-4o-mini，复杂任务用gpt-4o）
- ✅ 本地模型混合（超预算时切换本地模型）

---

## 七、开发路线图（MVP到Production）

### 阶段1: MVP（2周）- 验证可行性

**目标**: 证明技术可行
**功能**: 基础RAG + 单Agent + 命令行界面
**技术**: LlamaIndex + ChromaDB + GPT-4o-mini
**验收**: 输入指令，输出500字段落

### 阶段2: Alpha（4周）- 多Agent系统

**目标**: 完整协作流程
**功能**: 三Agent + LangGraph + Qdrant + 基础Web界面
**验收**: 生成完整章节（3000字），角色风格初步一致

### 阶段3: Beta（6周）- 一致性保障

**目标**: 长篇支持
**功能**: 剧情图谱 + 时间线 + 知识图谱 + 章节摘要
**验收**: 生成10章连续小说（3万字），零矛盾

### 阶段4: Production（8周）- 完整产品

**目标**: 用户就绪
**功能**: 用户管理 + 可视化 + 导出 + 性能优化
**技术**: 缓存 + 本地模型 + 流式生成

---

## 八、成本估算（参考）

### 开发成本
- MVP: 1人 × 2周 = 80小时
- Alpha: 2人 × 4周 = 320小时
- Beta: 3人 × 6周 = 720小时
- Production: 4人 × 8周 = 1280小时

### 运营成本（月）
- GPT-4o API: ~$500-2000（取决于用户量和缓存命中率）
- 服务器: ~$100-300（Qdrant + PostgreSQL + Redis）
- 总计: ~$600-2300/月

### 成本优化建议
- ✅ 使用响应缓存（可节省50-70% API成本）
- ✅ 简单任务用gpt-4o-mini（成本降低10倍）
- ✅ 考虑本地模型（如Llama 3或Qwen）作为备选

---

## 九、风险提示

| 风险 | 等级 | 缓解措施 |
|-----|------|---------|
| LLM幻觉导致内容错误 | 🔴 高 | 多层验证 + 人工审核接口 |
| API成本超预算 | 🔴 高 | 缓存 + 模型分级 + 本地模型 |
| 用户对生成质量不满意 | 🔴 高 | 多方案生成 + 人工编辑接口 |
| 向量检索召回率低 | 🟡 中 | 混合检索 + 重排序 |
| 长文本生成速度慢 | 🟡 中 | 流式输出 + 异步处理 |

---

## 十、下一步行动（立即开始）

### Week 1: 基础RAG系统
```bash
# 安装依赖
pip install llama-index chromadb openai

# 创建世界观索引
from llama_index import VectorStoreIndex, Document
docs = [Document(text="魔法塔位于北方雪山...")]
index = VectorStoreIndex.from_documents(docs)

# 测试检索
query_engine = index.as_query_engine()
response = query_engine.query("魔法塔的位置？")
print(response)
```

### Week 2: 单Agent生成测试
```python
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

# 创建剧情Agent
prompt = PromptTemplate(...)
agent = OpenAI(temperature=0.7)

# 生成段落
paragraph = agent(prompt.format(instruction="主角进入魔法塔"))
print(paragraph)
```

### Week 3-4: 集成LangGraph多Agent
```python
from langgraph.graph import StateGraph

# 定义工作流
workflow = StateGraph(NovelState)
workflow.add_node("worldbuilder", worldbuilder_agent)
workflow.add_node("character", character_agent)
workflow.add_node("plot", plot_controller_agent)

# 运行工作流
result = workflow.run({"instruction": "主角与导师决裂"})
```

---

## 附录：参考资源

### 官方文档
- LangGraph: https://langchain-ai.github.io/langgraph/
- LlamaIndex: https://docs.llamaindex.ai/
- Qdrant: https://qdrant.tech/documentation/

### 关键技术论文
- SCORE: Story Coherence and Retrieval Enhancement (2025)
- Memory Blocks: The Key to Agentic Context Management (2025)
- Agent Communication Protocols Survey (2025)

### 完整方案文档
📄 [ai-novel-writing-system-analysis.md](./ai-novel-writing-system-analysis.md)（15000+字详细方案）

---

**文档版本**: v1.0
**最后更新**: 2025-11-14
**联系人**: 技术负责人
