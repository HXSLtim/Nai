# AI写小说软件 - 快速参考指南

**生成时间**: 2025-11-14

---

## 一、技术决策树（30秒快速决策）

```
开始构建AI写小说系统
    │
    ├─ 需要多Agent协作？
    │   └─ 是 → 使用 LangGraph（图结构控制）
    │
    ├─ 需要RAG检索知识库？
    │   └─ 是 → 使用 LlamaIndex（检索性能最优）
    │
    ├─ 需要向量数据库？
    │   ├─ 预算充足，需要托管 → Pinecone
    │   ├─ 开源，高性能，强过滤 → Qdrant ⭐
    │   ├─ 亿级数据，分布式 → Milvus
    │   └─ 快速原型，小数据集 → ChromaDB
    │
    ├─ 需要结构化数据存储？
    │   └─ 是 → PostgreSQL + JSONB
    │
    ├─ 需要实时流式输出？
    │   └─ 是 → FastAPI（WebSocket）
    │
    └─ 需要前端界面？
        └─ 是 → Next.js 14（Server Components）
```

---

## 二、关键代码片段（复制即用）

### 2.1 LlamaIndex基础RAG（5分钟搭建）

```python
# 安装依赖
# pip install llama-index qdrant-client openai

from llama_index import VectorStoreIndex, Document, ServiceContext
from llama_index.vector_stores import QdrantVectorStore
from qdrant_client import QdrantClient
import os

# 配置
os.environ["OPENAI_API_KEY"] = "your-key"

# 初始化Qdrant
qdrant_client = QdrantClient(host="localhost", port=6333)

# 创建文档
docs = [
    Document(text="魔法塔位于北方雪山之巅，终年冰雪覆盖..."),
    Document(text="主角李明，性格勇敢但冲动，擅长火系魔法..."),
]

# 创建向量索引
vector_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name="novel_context"
)

service_context = ServiceContext.from_defaults(
    chunk_size=512,
    chunk_overlap=50
)

index = VectorStoreIndex.from_documents(
    docs,
    vector_store=vector_store,
    service_context=service_context
)

# 检索查询
query_engine = index.as_query_engine(similarity_top_k=3)
response = query_engine.query("魔法塔在哪里？")
print(response)
```

---

### 2.2 LangGraph三Agent工作流（核心框架）

```python
# pip install langgraph langchain openai

from langgraph.graph import StateGraph, END
from typing import TypedDict
from langchain.chat_models import ChatOpenAI

# 定义状态
class NovelState(TypedDict):
    user_instruction: str
    worldview_desc: str
    character_dialogue: str
    final_paragraph: str
    revision_count: int

# 初始化LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

# Agent A: 世界观描写
def worldbuilder_agent(state: NovelState):
    prompt = f"""
你是世界观描写专家。

【用户指令】
{state['user_instruction']}

【任务】
生成200-300字的环境描写和氛围渲染。

【输出】
"""
    response = llm.invoke(prompt)

    return {
        **state,
        "worldview_desc": response.content
    }

# Agent B: 角色对话
def character_agent(state: NovelState):
    prompt = f"""
你是角色塑造专家。

【环境上下文】
{state['worldview_desc']}

【用户指令】
{state['user_instruction']}

【任务】
创作符合角色性格的对话和心理描写。

【输出】
"""
    response = llm.invoke(prompt)

    return {
        **state,
        "character_dialogue": response.content
    }

# Agent C: 剧情控制
def plot_controller_agent(state: NovelState):
    prompt = f"""
你是剧情控制专家。

【环境描写】
{state['worldview_desc']}

【角色对话】
{state['character_dialogue']}

【任务】
整合以上内容，生成完整段落（500-800字）。

【输出】
"""
    response = llm.invoke(prompt)

    return {
        **state,
        "final_paragraph": response.content
    }

# 构建工作流
workflow = StateGraph(NovelState)

# 添加节点
workflow.add_node("worldbuilder", worldbuilder_agent)
workflow.add_node("character", character_agent)
workflow.add_node("plot_controller", plot_controller_agent)

# 定义边
workflow.set_entry_point("worldbuilder")
workflow.add_edge("worldbuilder", "character")
workflow.add_edge("character", "plot_controller")
workflow.add_edge("plot_controller", END)

# 编译并运行
app = workflow.compile()

result = app.invoke({
    "user_instruction": "主角在魔法塔顶与导师决裂",
    "worldview_desc": "",
    "character_dialogue": "",
    "final_paragraph": "",
    "revision_count": 0
})

print(result["final_paragraph"])
```

---

### 2.3 Qdrant向量检索（元数据过滤）

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, Filter, FieldCondition, Range

# 初始化客户端
client = QdrantClient(host="localhost", port=6333)

# 创建集合
client.create_collection(
    collection_name="worldview",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
)

# 插入向量（带元数据）
from openai import OpenAI
openai_client = OpenAI()

texts = [
    "魔法塔位于北方雪山，终年冰雪覆盖",
    "主角李明擅长火系魔法，性格冲动"
]

for i, text in enumerate(texts):
    # 生成嵌入
    embedding = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    ).data[0].embedding

    # 插入Qdrant
    client.upsert(
        collection_name="worldview",
        points=[{
            "id": i,
            "vector": embedding,
            "payload": {
                "text": text,
                "category": "geography" if i == 0 else "character",
                "chapter_range": [1, 5]
            }
        }]
    )

# 检索（带过滤）
query_text = "魔法塔的位置"
query_embedding = openai_client.embeddings.create(
    model="text-embedding-3-small",
    input=query_text
).data[0].embedding

results = client.search(
    collection_name="worldview",
    query_vector=query_embedding,
    query_filter=Filter(
        must=[
            FieldCondition(
                key="chapter_range",
                range=Range(gte=1, lte=10)
            )
        ]
    ),
    limit=3
)

for result in results:
    print(f"Score: {result.score}, Text: {result.payload['text']}")
```

---

### 2.4 FastAPI流式输出（实时生成）

```python
# pip install fastapi uvicorn

from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()

# HTTP流式接口
@app.get("/generate")
async def generate_chapter():
    async def stream_generator():
        # 模拟分段生成
        paragraphs = [
            "第一段：环境描写...",
            "第二段：角色对话...",
            "第三段：剧情推进..."
        ]

        for para in paragraphs:
            yield f"{para}\n\n"
            await asyncio.sleep(1)  # 模拟生成延迟

    return StreamingResponse(
        stream_generator(),
        media_type="text/plain"
    )

# WebSocket实时通信
@app.websocket("/ws/generate")
async def websocket_generate(websocket: WebSocket):
    await websocket.accept()

    try:
        # 接收指令
        instruction = await websocket.receive_text()

        # 逐段发送生成内容
        for i in range(3):
            paragraph = f"段落{i+1}：基于指令'{instruction}'生成的内容..."
            await websocket.send_text(paragraph)
            await asyncio.sleep(2)

        await websocket.close()
    except Exception as e:
        print(f"WebSocket错误: {e}")

# 运行：uvicorn main:app --reload
```

---

### 2.5 角色一致性检查（Persona验证）

```python
from langchain.chat_models import ChatOpenAI

class CharacterPersona:
    def __init__(self, character_profile):
        self.profile = character_profile
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    def validate_dialogue(self, dialogue):
        """验证对话是否符合角色性格"""
        validation_prompt = f"""
【角色档案】
姓名: {self.profile['name']}
性格: {', '.join(self.profile['personality'])}
说话风格: {self.profile['speaking_style']}
禁忌行为: {', '.join(self.profile['taboos'])}

【待验证对话】
{dialogue}

【任务】
判断该对话是否OOC（Out of Character，角色崩坏）。

【输出格式（JSON）】
{{
    "is_valid": true/false,
    "issues": ["问题1", "问题2"],
    "suggestions": ["改进建议"]
}}
"""
        response = self.llm.invoke(validation_prompt)

        # 解析JSON响应
        import json
        result = json.loads(response.content)

        return result

# 示例使用
character_profile = {
    "name": "李明",
    "personality": ["勇敢", "冲动", "正义感强"],
    "speaking_style": "直率，少用客套话",
    "taboos": ["背叛朋友", "伤害无辜"]
}

persona = CharacterPersona(character_profile)

dialogue = '"师父，虽然您救过我，但如果您要伤害无辜村民，我也不会手软！"李明咬牙道。'

validation = persona.validate_dialogue(dialogue)

if validation["is_valid"]:
    print("对话符合角色性格")
else:
    print(f"OOC问题: {validation['issues']}")
    print(f"建议: {validation['suggestions']}")
```

---

### 2.6 成本优化：响应缓存

```python
import hashlib
import json
from langchain.chat_models import ChatOpenAI

class CachedLLM:
    def __init__(self, model="gpt-4o-mini"):
        self.llm = ChatOpenAI(model=model, temperature=0.7)
        self.cache = {}  # 简单内存缓存（生产环境用Redis）

    def generate(self, prompt, use_cache=True):
        # 生成缓存键
        cache_key = hashlib.md5(
            f"{prompt}_{self.llm.model_name}_{self.llm.temperature}".encode()
        ).hexdigest()

        # 尝试从缓存获取
        if use_cache and cache_key in self.cache:
            print("✅ 缓存命中，零成本")
            return self.cache[cache_key]

        # 调用LLM
        print("⚠️ 调用LLM API，产生费用")
        response = self.llm.invoke(prompt)
        content = response.content

        # 存入缓存
        self.cache[cache_key] = content

        return content

# 示例使用
cached_llm = CachedLLM(model="gpt-4o-mini")

# 第一次调用（产生费用）
result1 = cached_llm.generate("描写魔法塔外观")

# 第二次相同调用（缓存命中，零成本）
result2 = cached_llm.generate("描写魔法塔外观")
```

---

## 三、常见问题速查

### Q1: 如何控制生成内容的长度？

**方法1**: 在Prompt中明确要求
```python
prompt = f"""
生成500-800字的段落（严格控制字数）。

【输出】
"""
```

**方法2**: 使用`max_tokens`参数
```python
llm = ChatOpenAI(model="gpt-4o", max_tokens=1000)
```

---

### Q2: 如何避免角色性格前后矛盾？

**核心方法**: Memory Blocks + Persona固化

```python
# 1. 定义不可变的核心性格
core_persona = {
    "name": "李明",
    "core_traits": ["勇敢", "冲动"],  # 永远不变
    "taboos": ["背叛朋友"]            # 绝不会做的事
}

# 2. 每次生成前注入Persona
prompt = f"""
【角色核心性格（不可违反）】
{json.dumps(core_persona, ensure_ascii=False)}

【生成对话】
...
"""

# 3. 生成后验证
validation = persona_validator.check(generated_dialogue, core_persona)
if not validation["is_valid"]:
    # 重新生成或修正
    ...
```

---

### Q3: 如何处理长篇小说的上下文窗口限制？

**策略组合**:

1. **分层摘要**（最近章节详细，早期章节简化）
```python
context = ""

# 最近3章：详细摘要
for i in range(current_chapter - 3, current_chapter):
    context += chapter_summaries[i]["detailed"]

# 更早章节：一句话摘要
for i in range(0, current_chapter - 3):
    context += chapter_summaries[i]["one_sentence"]
```

2. **关键事件索引**（向量化重要剧情点）
```python
# 检索相关历史事件
relevant_events = event_vector_store.search(
    query=f"与{current_plot}相关的历史事件",
    top_k=5
)
```

3. **滑动窗口**（保留高优先级内容）
```python
# 优先级：核心剧情 > 角色对话 > 环境描写
context_window.add(paragraph, priority="high")
```

---

### Q4: 如何降低LLM API成本？

**三大策略**:

1. **响应缓存**（节省50-70%）
```python
# 相同prompt直接返回缓存
if prompt_hash in cache:
    return cache[prompt_hash]  # 零成本
```

2. **模型分级**（简单任务用便宜模型）
```python
if task_complexity == "simple":
    model = "gpt-4o-mini"  # 成本降低10倍
else:
    model = "gpt-4o"
```

3. **本地模型混合**（超预算时切换）
```python
if daily_budget_exceeded():
    response = local_llama_model.generate(prompt)  # 零API成本
else:
    response = openai_api.generate(prompt)
```

**预期节省**: 从$2000/月降至$500-800/月

---

### Q5: 如何确保世界观不矛盾？

**核心机制**: 规则引擎 + 知识图谱

```python
# 1. 定义硬规则
world_rules = {
    "magic_level_limit": lambda caster, spell: (
        db.get_magic_level(caster) >= db.get_required_level(spell)
    ),
    "character_alive": lambda char_id: (
        char_id not in dead_characters
    )
}

# 2. 验证生成内容
violations = []
for rule_name, rule_checker in world_rules.items():
    if not rule_checker(generated_content):
        violations.append(f"违反规则: {rule_name}")

# 3. 有违规则拒绝内容
if violations:
    return {"status": "rejected", "reasons": violations}
```

---

### Q6: 如何实现实时流式输出？

**WebSocket方案**（推荐）:

```python
# 后端（FastAPI）
@app.websocket("/ws/generate")
async def generate(websocket: WebSocket):
    await websocket.accept()

    async for chunk in llm.stream_generate(prompt):
        await websocket.send_text(chunk)

# 前端（Next.js）
const ws = new WebSocket("ws://localhost:8000/ws/generate");

ws.onmessage = (event) => {
    setContent(prev => prev + event.data);  // 逐字追加
};
```

---

## 四、开发检查清单

### MVP阶段（第1-2周）
- [ ] 安装依赖：`llama-index`, `qdrant-client`, `openai`
- [ ] 启动Qdrant：`docker run -p 6333:6333 qdrant/qdrant`
- [ ] 创建基础RAG索引（世界观/角色）
- [ ] 实现单Agent生成（命令行测试）
- [ ] 验收：输入指令，输出500字段落

### Alpha阶段（第3-6周）
- [ ] 集成LangGraph三Agent工作流
- [ ] 实现Memory Blocks记忆系统
- [ ] 迁移到生产级Qdrant部署
- [ ] 开发FastAPI后端API
- [ ] 创建Next.js基础界面
- [ ] 验收：生成完整章节（3000字）

### Beta阶段（第7-12周）
- [ ] 实现剧情图谱（Plot Graph）
- [ ] 实现时间线验证器
- [ ] 实现角色情绪状态机
- [ ] 实现一致性检查系统
- [ ] 实现章节摘要压缩
- [ ] 验收：生成10章小说，零矛盾

### Production阶段（第13-20周）
- [ ] 用户管理系统
- [ ] 多小说项目管理
- [ ] 角色关系图谱可视化
- [ ] 导出功能（EPUB/PDF）
- [ ] 性能优化（缓存、并发）
- [ ] 部署上线

---

## 五、故障排查速查

### 问题1: Qdrant连接失败

**症状**: `ConnectionRefusedError: [Errno 61] Connection refused`

**解决**:
```bash
# 检查Qdrant是否运行
docker ps | grep qdrant

# 如果没运行，启动Qdrant
docker run -d -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```

---

### 问题2: LlamaIndex检索结果为空

**症状**: `query_engine.query()` 返回空结果

**排查步骤**:
```python
# 1. 检查索引是否有数据
print(f"文档数量: {len(index.docstore.docs)}")

# 2. 检查嵌入模型是否一致
print(f"嵌入模型: {service_context.embed_model}")

# 3. 降低相似度阈值
query_engine = index.as_query_engine(
    similarity_top_k=10,  # 增加返回数量
    similarity_cutoff=0.3  # 降低阈值（默认0.7）
)
```

---

### 问题3: LangGraph工作流卡住

**症状**: `app.invoke()` 无响应

**排查**:
```python
# 1. 启用调试模式
import logging
logging.basicConfig(level=logging.DEBUG)

# 2. 检查是否有无限循环边
# 确保条件边最终会到达END

# 3. 添加超时
from asyncio import timeout

async with timeout(60):  # 60秒超时
    result = await app.ainvoke(input_state)
```

---

### 问题4: OpenAI API Rate Limit

**症状**: `RateLimitError: Rate limit reached`

**解决**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def generate_with_retry(prompt):
    return llm.invoke(prompt)
```

---

## 六、资源链接

### 官方文档
- LangGraph: https://langchain-ai.github.io/langgraph/
- LlamaIndex: https://docs.llamaindex.ai/
- Qdrant: https://qdrant.tech/documentation/
- FastAPI: https://fastapi.tiangolo.com/

### 教程资源
- LangGraph教程: https://github.com/langchain-ai/langgraph/tree/main/examples
- LlamaIndex示例: https://docs.llamaindex.ai/en/stable/examples/
- Qdrant快速开始: https://qdrant.tech/documentation/quick-start/

### 社区支持
- LangChain Discord: https://discord.gg/langchain
- LlamaIndex Discord: https://discord.gg/llamaindex
- Qdrant Discord: https://discord.gg/qdrant

---

**文档版本**: v1.0
**最后更新**: 2025-11-14
