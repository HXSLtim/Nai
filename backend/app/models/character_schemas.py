"""
角色管理相关的Pydantic Schema
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ========== 角色基础Schema ==========

class CharacterBase(BaseModel):
    """角色基础信息"""
    name: str = Field(..., min_length=1, max_length=100, description="角色姓名")
    age: Optional[int] = Field(None, ge=0, le=1000, description="角色年龄")
    gender: Optional[str] = Field(None, max_length=20, description="角色性别")
    occupation: Optional[str] = Field(None, max_length=100, description="角色职业")
    appearance: Optional[str] = Field(None, description="外貌描述")
    personality: Optional[str] = Field(None, description="性格特征")
    background: Optional[str] = Field(None, description="背景故事")
    skills: Optional[List[str]] = Field(default_factory=list, description="技能列表")
    relationships: Optional[Dict[str, Any]] = Field(default_factory=dict, description="关系网络")
    character_arc: Optional[str] = Field(None, description="角色弧线")
    importance_level: str = Field(default="secondary", description="重要性级别")
    first_appearance_chapter: Optional[int] = Field(None, description="首次出现章节")


class CharacterCreate(CharacterBase):
    """创建角色请求"""
    novel_id: int = Field(..., description="所属小说ID")


class CharacterUpdate(BaseModel):
    """更新角色请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=1000)
    gender: Optional[str] = Field(None, max_length=20)
    occupation: Optional[str] = Field(None, max_length=100)
    appearance: Optional[str] = None
    personality: Optional[str] = None
    background: Optional[str] = None
    skills: Optional[List[str]] = None
    relationships: Optional[Dict[str, Any]] = None
    character_arc: Optional[str] = None
    importance_level: Optional[str] = None
    first_appearance_chapter: Optional[int] = None
    last_appearance_chapter: Optional[int] = None


class CharacterResponse(CharacterBase):
    """角色响应"""
    id: int
    novel_id: int
    last_appearance_chapter: Optional[int] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 角色关系Schema ==========

class CharacterRelationshipBase(BaseModel):
    """角色关系基础信息"""
    relationship_type: str = Field(..., max_length=50, description="关系类型")
    description: Optional[str] = Field(None, description="关系描述")
    strength: int = Field(default=5, ge=1, le=10, description="关系强度")
    development_stage: Optional[str] = Field(None, description="发展阶段")
    established_in_chapter: Optional[int] = Field(None, description="建立关系的章节")


class CharacterRelationshipCreate(CharacterRelationshipBase):
    """创建角色关系请求"""
    novel_id: int = Field(..., description="所属小说ID")
    character_a_id: int = Field(..., description="角色A的ID")
    character_b_id: int = Field(..., description="角色B的ID")


class CharacterRelationshipUpdate(BaseModel):
    """更新角色关系请求"""
    relationship_type: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    strength: Optional[int] = Field(None, ge=1, le=10)
    development_stage: Optional[str] = None


class CharacterRelationshipResponse(CharacterRelationshipBase):
    """角色关系响应"""
    id: int
    novel_id: int
    character_a_id: int
    character_b_id: int
    character_a_name: str
    character_b_name: str
    change_history: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 角色出场记录Schema ==========

class CharacterAppearanceBase(BaseModel):
    """角色出场基础信息"""
    appearance_type: str = Field(default="supporting", description="出场类型")
    description: Optional[str] = Field(None, description="出场描述")
    importance_in_chapter: int = Field(default=5, ge=1, le=10, description="在章节中的重要性")
    status_changes: Optional[Dict[str, Any]] = Field(default_factory=dict, description="状态变化")


class CharacterAppearanceCreate(CharacterAppearanceBase):
    """创建角色出场记录请求"""
    character_id: int = Field(..., description="角色ID")
    chapter_id: int = Field(..., description="章节ID")


class CharacterAppearanceResponse(CharacterAppearanceBase):
    """角色出场记录响应"""
    id: int
    character_id: int
    chapter_id: int
    character_name: str
    chapter_number: int
    created_at: datetime

    class Config:
        from_attributes = True


# ========== AI分析相关Schema ==========

class CharacterAnalysisRequest(BaseModel):
    """角色分析请求"""
    character_id: int = Field(..., description="角色ID")
    analysis_type: str = Field(default="comprehensive", description="分析类型")
    include_relationships: bool = Field(default=True, description="是否包含关系分析")
    include_development: bool = Field(default=True, description="是否包含发展分析")


class CharacterAnalysisResponse(BaseModel):
    """角色分析响应"""
    character_id: int
    character_name: str
    analysis_type: str
    
    # 分析结果
    personality_analysis: Optional[Dict[str, Any]] = None
    development_analysis: Optional[Dict[str, Any]] = None
    relationship_analysis: Optional[Dict[str, Any]] = None
    consistency_check: Optional[Dict[str, Any]] = None
    improvement_suggestions: Optional[List[str]] = None
    
    # 元数据
    analysis_timestamp: datetime
    confidence_score: Optional[float] = None


class CharacterOptimizationRequest(BaseModel):
    """角色优化请求"""
    character_id: int = Field(..., description="角色ID")
    optimization_goals: List[str] = Field(..., description="优化目标")
    preserve_traits: Optional[List[str]] = Field(default_factory=list, description="保持的特征")


class CharacterOptimizationResponse(BaseModel):
    """角色优化响应"""
    character_id: int
    original_character: CharacterResponse
    optimized_suggestions: Dict[str, Any]
    reasoning: str
    confidence_score: float


# ========== MCP相关Schema ==========

class MCPCharacterAction(BaseModel):
    """MCP角色操作"""
    action: str = Field(..., description="操作类型: create, update, delete, analyze, optimize")
    character_id: Optional[int] = Field(None, description="角色ID")
    novel_id: Optional[int] = Field(None, description="小说ID")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="操作参数")
    context: Optional[str] = Field(None, description="操作上下文")


class MCPCharacterResponse(BaseModel):
    """MCP角色操作响应"""
    success: bool
    action: str
    character_id: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    message: str
    timestamp: datetime


class CharacterNetworkResponse(BaseModel):
    """角色关系网络响应"""
    novel_id: int
    characters: List[CharacterResponse]
    relationships: List[CharacterRelationshipResponse]
    network_analysis: Optional[Dict[str, Any]] = None


class CharacterTimelineResponse(BaseModel):
    """角色时间线响应"""
    character_id: int
    character_name: str
    appearances: List[CharacterAppearanceResponse]
    development_milestones: Optional[List[Dict[str, Any]]] = None
    relationship_changes: Optional[List[Dict[str, Any]]] = None
