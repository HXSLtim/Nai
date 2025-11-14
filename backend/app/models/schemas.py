"""
Pydantic数据模型
定义API请求和响应的数据结构
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ========== 用户认证相关模型 ==========

class UserBase(BaseModel):
    """用户基础Schema"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")


class UserCreate(UserBase):
    """用户注册Schema"""
    password: str = Field(..., min_length=6, max_length=50, description="密码")


class UserLogin(BaseModel):
    """用户登录Schema"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(UserBase):
    """用户响应Schema"""
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class StyleSampleCreate(BaseModel):
    """文风样本创建请求"""
    novel_id: int = Field(..., description="小说ID")
    name: str = Field(..., min_length=1, max_length=100, description="文风名称")
    sample_text: str = Field(..., min_length=1, description="文风样本文本")


class StyleSampleResponse(BaseModel):
    """文风样本响应"""
    id: int
    novel_id: int
    name: str
    sample_preview: str
    style_features: List[str] = Field(default_factory=list)
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token响应Schema"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ========== 枚举类型 ==========

class AgentType(str, Enum):
    """Agent类型枚举"""
    WORLDVIEW = "worldview"  # 世界观Agent
    CHARACTER = "character"  # 角色Agent
    PLOT = "plot"  # 剧情Agent


class ConsistencyCheckType(str, Enum):
    """一致性检查类型枚举"""
    RULE_ENGINE = "rule_engine"  # 规则引擎
    KNOWLEDGE_GRAPH = "knowledge_graph"  # 知识图谱
    TIMELINE = "timeline"  # 时间线
    EMOTION = "emotion"  # 情绪状态机


# ========== 小说相关模型 ==========

class NovelCreate(BaseModel):
    """创建小说请求"""
    title: str = Field(..., min_length=1, max_length=200, description="小说标题")
    genre: Optional[str] = Field(None, max_length=50, description="小说类型（如玄幻、科幻等）")
    description: Optional[str] = Field(None, description="小说简介")
    worldview: Optional[str] = Field(None, description="世界观设定")


class NovelUpdate(BaseModel):
    """更新小说请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="小说标题")
    genre: Optional[str] = Field(None, max_length=50, description="小说类型")
    description: Optional[str] = Field(None, description="小说简介")
    worldview: Optional[str] = Field(None, description="世界观设定")


class NovelResponse(BaseModel):
    """小说响应"""
    id: int
    title: str
    genre: Optional[str]
    description: Optional[str]
    worldview: Optional[str]
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ========== 章节相关模型 ==========

class ChapterCreate(BaseModel):
    """创建章节请求"""
    chapter_number: int = Field(..., gt=0, description="章节号")
    title: str = Field(..., min_length=1, max_length=200, description="章节标题")
    content: str = Field(..., min_length=1, description="章节内容")


class ChapterUpdate(BaseModel):
    """更新章节请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="章节标题")
    content: Optional[str] = Field(None, min_length=1, description="章节内容")


class ChapterResponse(BaseModel):
    """章节响应"""
    id: int
    novel_id: int
    chapter_number: int
    title: str
    content: str
    word_count: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class EditorIssue(BaseModel):
    """网文编辑问题项（轻量审核用）"""
    type: str = Field(..., description="问题类型，如节奏/爽点/信息量/重复度/人物等")
    level: str = Field("info", description="严重程度：info/warn")
    message: str = Field(..., description="问题描述")
    suggestion: Optional[str] = Field(None, description="一句话修改建议")


class EditorReview(BaseModel):
    """网文编辑Agent整体审核结果"""
    score: int = Field(0, ge=0, le=100, description="整体评分（0-100，仅作参考）")
    summary: str = Field(..., description="编辑总体评价")
    issues: List[EditorIssue] = Field(default_factory=list, description="问题列表")
    suggested_tags: List[str] = Field(default_factory=list, description="建议标签，如爽文/慢热等")
    created_at: datetime


class ConsistencySummary(BaseModel):
    """一致性检查摘要"""
    has_conflict: bool = Field(..., description="是否存在一致性冲突")
    violations: List[str] = Field(default_factory=list, description="违规说明列表")
    checks_performed: List[str] = Field(default_factory=list, description="执行过的检查类型")


class ChapterWithReviewResponse(ChapterResponse):
    """带有编辑审核结果的章节响应，用于手动保存后返回"""
    editor_review: Optional[EditorReview] = Field(
        None,
        description="网文编辑Agent的轻量审核结果，为空表示本次未生成或解析失败",
    )
    consistency_summary: Optional[ConsistencySummary] = Field(
        None,
        description="章节内容一致性检查摘要（规则引擎、知识图谱、时间线等）",
    )


# ========== 世界观相关模型 ==========

class WorldviewRule(BaseModel):
    """世界观规则"""
    name: str = Field(..., description="规则名称（如魔法等级上限）")
    value: Any = Field(..., description="规则值（如9）")
    description: Optional[str] = Field(None, description="规则说明")


class WorldviewCreate(BaseModel):
    """创建世界观请求"""
    novel_id: int = Field(..., description="小说ID")
    name: str = Field(..., description="世界观名称（如魔法体系）")
    content: str = Field(..., description="世界观内容描述")
    rules: List[WorldviewRule] = Field(default_factory=list, description="硬规则列表")


class WorldviewResponse(BaseModel):
    """世界观响应"""
    id: int
    novel_id: int
    name: str
    content: str
    rules: List[WorldviewRule]
    created_at: datetime


# ========== 角色相关模型 ==========

class CharacterRelationship(BaseModel):
    """角色关系"""
    target_character_id: int = Field(..., description="目标角色ID")
    relationship_type: str = Field(..., description="关系类型（如朋友、敌人）")


class CharacterCreate(BaseModel):
    """创建角色请求"""
    novel_id: int = Field(..., description="小说ID")
    name: str = Field(..., description="角色名称")
    personality: str = Field(..., description="性格描述")
    appearance: Optional[str] = Field(None, description="外貌描述")
    background: Optional[str] = Field(None, description="背景故事")
    relationships: List[CharacterRelationship] = Field(default_factory=list, description="角色关系")


class CharacterResponse(BaseModel):
    """角色响应"""
    id: int
    novel_id: int
    name: str
    personality: str
    appearance: Optional[str]
    background: Optional[str]
    relationships: List[CharacterRelationship]
    current_emotion: str = "平静"
    created_at: datetime


# ========== 大纲相关模型 ==========

class OutlineNode(BaseModel):
    """大纲节点"""
    chapter: int = Field(..., description="章节号")
    title: str = Field(..., description="章节标题")
    plot_points: List[str] = Field(..., description="剧情点列表")
    foreshadowing: List[str] = Field(default_factory=list, description="伏笔列表")


class OutlineCreate(BaseModel):
    """创建大纲请求"""
    novel_id: int = Field(..., description="小说ID")
    nodes: List[OutlineNode] = Field(..., description="大纲节点列表")


class OutlineResponse(BaseModel):
    """大纲响应"""
    id: int
    novel_id: int
    nodes: List[OutlineNode]
    created_at: datetime


# ========== 内容生成相关模型 ==========

class GenerationRequest(BaseModel):
    """内容生成请求"""
    novel_id: int = Field(..., description="小说ID")
    prompt: str = Field(..., description="剧情提示词")
    chapter: int = Field(..., description="当前章节号")
    current_day: int = Field(1, description="故事当前天数")
    target_length: int = Field(500, description="目标字数")


class InitNovelRequest(BaseModel):
    """AI初始化小说设定请求"""
    novel_id: int = Field(..., description="小说ID")
    target_chapters: int = Field(10, description="规划的章节数量")
    theme: Optional[str] = Field(None, description="故事主题或补充设定提示")


class AgentOutput(BaseModel):
    """单个Agent的输出"""
    agent_type: AgentType
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConsistencyCheckResult(BaseModel):
    """一致性检查结果"""
    check_type: ConsistencyCheckType
    is_valid: bool
    violations: List[str] = Field(default_factory=list)


class GenerationResponse(BaseModel):
    """内容生成响应"""
    novel_id: int
    chapter: int
    final_content: str
    agent_outputs: List[AgentOutput]
    consistency_checks: List[ConsistencyCheckResult]
    retry_count: int = 0
    generated_at: datetime
    worldview_context: List[str] = Field(default_factory=list)
    character_context: List[str] = Field(default_factory=list)
    rag_results: List[Dict[str, Any]] = Field(default_factory=list)


class InitNovelResponse(BaseModel):
    """AI初始化小说设定响应"""
    novel_id: int
    worldview: str
    main_characters: List[str]
    outline: str
    plot_hooks: List[str]


class PlotOption(BaseModel):
    """剧情走向选项"""
    id: int
    title: str
    summary: str
    impact: Optional[str] = None
    risk: Optional[str] = None


class PlotOptionsRequest(BaseModel):
    """剧情走向选项请求"""
    novel_id: int = Field(..., description="小说ID")
    chapter_id: int = Field(..., description="当前章节ID")
    current_content: str = Field(..., description="用于判断下一步剧情走向的文本（通常是当前章节或上一章节的结尾")
    num_options: int = Field(3, ge=1, le=6, description="需要返回的剧情走向数量")


class PlotOptionsResponse(BaseModel):
    """剧情走向选项响应"""
    novel_id: int
    chapter_id: int
    options: List[PlotOption]


class AutoChapterRequest(BaseModel):
    """AI自动生成章节请求"""
    novel_id: int = Field(..., description="小说ID")
    base_chapter_id: Optional[int] = Field(
        None,
        description="作为生成参考的基础章节ID，不传则使用最后一章",
    )
    target_length: int = Field(500, ge=100, le=3000, description="AI生成章节的目标字数")
    theme: Optional[str] = Field(
        None,
        description="本章剧情重点或风格提示，如'推进主线冲突'、'日常轻松番外'等",
    )


class RewriteRequest(BaseModel):
    """局部文本改写请求"""
    novel_id: int = Field(..., description="小说ID")
    chapter_id: Optional[int] = Field(None, description="当前章节ID（可选，用于权限校验")
    original_text: str = Field(..., min_length=1, description="需要改写的原始文本")
    rewrite_type: str = Field(
        "polish",
        description="改写类型：polish（润色）/rewrite（重写）/shorten（压缩）/extend（扩写）",
    )
    style_hint: Optional[str] = Field(
        None,
        description="额外风格提示，例如保持文风不变、偏古风、偏轻松等",
    )
    target_length: Optional[int] = Field(
        None,
        ge=10,
        le=5000,
        description="目标字数（可选，不指定则由模型自动控制长度）",
    )


class RewriteResponse(BaseModel):
    """局部文本改写响应"""
    rewritten_text: str = Field(..., description="改写后的文本")


class ResearchRequest(BaseModel):
    """资料检索请求"""
    novel_id: Optional[int] = Field(None, description="小说ID（可选，用于后续扩展上下文绑定）")
    query: str = Field(..., description="检索问题或关键词")
    category: Optional[str] = Field(None, description="检索类别，如history/geography/technology")


class ResearchResult(BaseModel):
    """资料检索结果"""
    title: str
    summary: str
    source: str
    url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ResearchResponse(BaseModel):
    """资料检索响应"""
    query: str
    results: List[ResearchResult]


# ========== RAG检索相关模型 ==========

class RAGQuery(BaseModel):
    """RAG检索请求"""
    novel_id: int = Field(..., description="小说ID")
    query: str = Field(..., description="检索查询")
    max_chapter: Optional[int] = Field(None, description="最大章节号（用于过滤）")
    top_k: int = Field(3, description="返回Top K结果")


class RAGResult(BaseModel):
    """RAG检索结果"""
    content: str
    metadata: Dict[str, Any]
    score: float


class RAGResponse(BaseModel):
    """RAG检索响应"""
    query: str
    results: List[RAGResult]
    retrieval_method: str  # "hybrid", "vector", "bm25"
