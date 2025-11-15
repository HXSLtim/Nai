# 小说审核多Agent系统

## 📋 概述

审核 Agent 系统是小说上线流程的核心组件，通过 6 个专业 Agent 协同工作，对章节内容进行全方位审核，确保内容质量达到发布标准。

## 🤖 Agent 架构

### 1. 章节节奏审核 Agent (`PaceReviewAgent`)

**职责**：分析章节的叙事节奏

**审核维度**：
- 情节推进速度（是否过快或过慢）
- 描写与对话平衡（环境描写、心理描写、对话的比例）
- 高潮与平缓分布（节奏起伏）
- 节奏变化合理性（转折是否自然）

**输出**：
```json
{
  "score": 85,
  "pace_type": "medium",
  "issues": ["第3段节奏过快，缺少铺垫"],
  "suggestions": ["建议在高潮前增加环境描写"],
  "details": {
    "plot_speed": "整体节奏适中",
    "balance": "对话占比60%，描写40%，比例合理",
    "rhythm": "有明显的起承转合"
  }
}
```

### 2. 内容质量检查 Agent (`QualityReviewAgent`)

**职责**：检查内容的整体质量

**审核维度**：
- 语法和用词（grammar_score）
- 逻辑合理性（logic_score）
- 描写质量（description_score）

**输出**：
```json
{
  "score": 82,
  "grammar_score": 90,
  "logic_score": 80,
  "description_score": 75,
  "issues": ["第5段存在逻辑跳跃"],
  "suggestions": ["补充角色动机说明"]
}
```

### 3. 情节连贯性 Agent (`PlotCoherenceAgent`)

**职责**：检查章节间的情节连贯性

**审核维度**：
- 情节衔接（与前文的自然衔接）
- 伏笔呼应（未解决的伏笔或矛盾）
- 时间线一致（时间顺序合理性）
- 因果关系（事件发展的合理性）

**输出**：
```json
{
  "score": 78,
  "coherence_issues": ["与第2章的时间线不一致"],
  "plot_holes": ["角色突然出现在另一个城市"],
  "suggestions": ["补充角色移动的过程"]
}
```

### 4. 角色一致性 Agent (`CharacterConsistencyAgent`)

**职责**：检查角色表现的一致性

**审核维度**：
- 性格一致性（行为是否符合角色性格）
- 说话风格（对话是否符合角色特点）
- 能力水平（是否突然变强或变弱）
- 关系变化（人物关系变化是否合理）

**特点**：
- 从 RAG 检索角色历史信息
- 对比当前表现与历史设定

**输出**：
```json
{
  "score": 88,
  "inconsistencies": [
    {
      "type": "对话",
      "description": "主角突然使用了不符合其性格的粗俗语言"
    }
  ],
  "suggestions": ["调整对话风格以符合角色设定"]
}
```

### 5. 语言风格 Agent (`StyleReviewAgent`)

**职责**：评估语言风格的一致性和质量

**审核维度**：
- 风格类型识别（现代/古典/诗意/简洁等）
- 风格一致性（整章风格是否统一）
- 语言质量（用词精准度、表达优美度）
- 可读性（流畅度）

**输出**：
```json
{
  "score": 80,
  "style_type": "现代简洁",
  "consistency_score": 85,
  "issues": ["第7段突然出现古典用语"],
  "suggestions": ["统一为现代表达方式"]
}
```

### 6. 内容安全检测 Agent (`ContentSafetyAgent`)

**职责**：检测敏感和不适当内容

**审核维度**：
- 暴力血腥
- 色情低俗
- 政治敏感
- 违法犯罪

**输出**：
```json
{
  "is_safe": true,
  "risk_level": "low",
  "flagged_content": [],
  "suggestions": []
}
```

## 🔄 工作流程

### 并行审核流程

```
开始审核
    ├─ 节奏审核 Agent      ─┐
    ├─ 质量检查 Agent      ─┤
    ├─ 情节连贯性 Agent    ─┤ 并行执行
    ├─ 角色一致性 Agent    ─┤
    ├─ 语言风格 Agent      ─┤
    └─ 内容安全 Agent      ─┘
            ↓
    汇总结果 & 计算总分
            ↓
    生成审核报告
```

### 评分机制

**总体得分计算**（加权平均）：
```
总分 = 节奏(20%) + 质量(25%) + 连贯性(20%) + 
       角色(15%) + 风格(10%) + 安全(10%)
```

**发布标准**：
- 总体得分 ≥ 70
- 节奏得分 ≥ 60
- 质量得分 ≥ 65
- 连贯性得分 ≥ 60
- 角色得分 ≥ 60
- 内容安全通过

## 📡 API 接口

### 1. 完整审核接口

```http
POST /api/review/chapter
Content-Type: application/json

{
  "novel_id": 1,
  "chapter_id": 5,
  "chapter_number": 5,
  "content": "章节内容...",
  "previous_chapters": ["第1章内容...", "第2章内容..."]
}
```

**响应**：
```json
{
  "overall_score": 82,
  "is_ready_for_publish": true,
  "pace_review": { ... },
  "quality_review": { ... },
  "plot_coherence": { ... },
  "character_consistency": { ... },
  "style_review": { ... },
  "content_safety": { ... },
  "workflow_trace": {
    "run_id": "review-1-5-1699999999999",
    "steps": [ ... ]
  }
}
```

### 2. 流式审核接口

```http
POST /api/review/chapter-stream
Content-Type: application/json

{
  "novel_id": 1,
  "chapter_id": 5,
  "chapter_number": 5,
  "content": "章节内容..."
}
```

**SSE 事件流**：
```
data: {"type": "start", "message": "开始审核"}

data: {"type": "agent_start", "agent": "pace", "message": "正在审核节奏..."}
data: {"type": "agent_result", "agent": "pace", "result": {...}}

data: {"type": "agent_start", "agent": "quality", "message": "正在检查质量..."}
data: {"type": "agent_result", "agent": "quality", "result": {...}}

...

data: {"type": "summary", "overall_score": 82, ...}
```

## 🎯 使用场景

### 1. 章节完成后的质量检查

```python
# 作者完成章节后，系统自动触发审核
result = await review_agent_service.review_chapter_comprehensive(
    novel_id=1,
    chapter_id=5,
    chapter_number=5,
    content=chapter_content,
    previous_chapters=previous_chapters
)

if result["is_ready_for_publish"]:
    print("✓ 章节质量达标，可以发布")
else:
    print("✗ 需要改进：")
    for issue in result["pace_review"]["issues"]:
        print(f"  - {issue}")
```

### 2. 小说上线前的全书审核

```python
# 审核所有章节
for chapter in novel.chapters:
    result = await review_agent_service.review_chapter_comprehensive(
        novel_id=novel.id,
        chapter_id=chapter.id,
        chapter_number=chapter.chapter_number,
        content=chapter.content,
        previous_chapters=get_previous_chapters(chapter)
    )
    
    if not result["is_ready_for_publish"]:
        print(f"第{chapter.chapter_number}章需要修改")
        generate_improvement_suggestions(result)
```

### 3. 实时审核反馈

```python
# 使用流式接口提供实时反馈
async for event in review_chapter_stream(request):
    if event["type"] == "agent_result":
        agent = event["agent"]
        score = event["result"]["score"]
        print(f"{agent} 审核完成，得分：{score}")
```

## 🔧 配置与扩展

### 添加新的审核维度

1. 在 `review_agents.py` 中创建新的 Agent 函数
2. 在 `review_agent_service.py` 中调用新 Agent
3. 更新评分权重配置

### 自定义评分标准

修改 `review_agent_service.py` 中的评分计算逻辑：

```python
# 自定义权重
overall_score = int(
    pace_review["score"] * 0.25 +      # 提高节奏权重
    quality_review["score"] * 0.30 +   # 提高质量权重
    plot_coherence["score"] * 0.15 +
    character_consistency["score"] * 0.15 +
    style_review["score"] * 0.10 +
    (100 if content_safety["is_safe"] else 0) * 0.05
)
```

### 集成外部审核服务

```python
# 例如：集成专业的内容安全API
async def review_content_safety_agent(...):
    # 调用第三方API
    result = await external_safety_api.check(content)
    return result
```

## 📊 工作流追踪

每次审核都会生成详细的工作流追踪信息，包括：

- 每个 Agent 的执行时间
- 输入输出数据
- 使用的 LLM 模型和参数
- 数据来源（如 RAG 检索结果）

这些信息可用于：
- 前端可视化展示审核过程
- 性能分析和优化
- 审核结果的可解释性

## 🚀 性能优化

### 并行执行

所有 Agent 并行执行，大大缩短审核时间：

```python
# 6个Agent并行执行，总耗时约等于最慢的Agent
results = await asyncio.gather(
    pace_task,
    quality_task,
    plot_task,
    character_task,
    style_task,
    safety_task,
    return_exceptions=True
)
```

### 缓存机制

对于不变的历史章节，可以缓存审核结果：

```python
# TODO: 实现缓存
cached_result = cache.get(f"review:{chapter_id}")
if cached_result:
    return cached_result
```

## 📝 最佳实践

1. **定期审核**：建议每完成3-5章进行一次审核
2. **重点关注**：特别注意连贯性和角色一致性
3. **迭代改进**：根据审核建议逐步优化
4. **全书审核**：上线前进行完整的全书审核
5. **保存记录**：保存审核历史，追踪改进过程

## 🔮 未来扩展

- [ ] 添加读者偏好分析 Agent
- [ ] 添加市场竞争力评估 Agent
- [ ] 支持自定义审核规则
- [ ] 集成专业编辑建议
- [ ] 多语言支持
- [ ] 审核报告可视化
