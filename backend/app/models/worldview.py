"""
世界观设定数据模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class WorldviewSetting(Base):
    """世界观设定模型"""
    __tablename__ = "worldview_settings"

    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, ForeignKey("novels.id"), nullable=False)
    
    # 设定分类
    category = Column(String(50), nullable=False, index=True)  # geography, culture, magic, technology, etc.
    name = Column(String(200), nullable=False, index=True)
    
    # 设定内容
    description = Column(Text, nullable=False)
    details = Column(JSON, default=dict)  # 详细设定数据
    
    # 设定属性
    importance_level = Column(String(20), default="medium")  # high, medium, low
    consistency_rules = Column(JSON, default=list)  # 一致性规则
    
    # 关联信息
    related_characters = Column(JSON, default=list)  # 相关角色ID列表
    related_chapters = Column(JSON, default=list)   # 相关章节ID列表
    
    # AI分析
    ai_analysis = Column(JSON, default=dict)
    
    # 状态
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    
    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    novel = relationship("Novel", back_populates="worldview_settings")

    def __repr__(self):
        return f"<WorldviewSetting {self.category}:{self.name}>"


class PlotElement(Base):
    """情节元素模型"""
    __tablename__ = "plot_elements"

    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, ForeignKey("novels.id"), nullable=False)
    
    # 情节信息
    element_type = Column(String(50), nullable=False)  # conflict, twist, climax, resolution, etc.
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # 情节位置
    chapter_start = Column(Integer)
    chapter_end = Column(Integer)
    position_in_story = Column(String(50))  # beginning, middle, end
    
    # 情节属性
    importance_score = Column(Integer, default=5)  # 1-10
    emotional_impact = Column(String(50))  # high, medium, low
    plot_function = Column(String(100))  # 情节功能
    
    # 关联信息
    involved_characters = Column(JSON, default=list)
    affected_settings = Column(JSON, default=list)
    prerequisites = Column(JSON, default=list)  # 前置条件
    consequences = Column(JSON, default=list)   # 后果影响
    
    # 发展状态
    development_stage = Column(String(50), default="planned")  # planned, developing, resolved
    
    # AI分析
    ai_analysis = Column(JSON, default=dict)
    
    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    novel = relationship("Novel", back_populates="plot_elements")

    def __repr__(self):
        return f"<PlotElement {self.element_type}:{self.title}>"


class StoryTimeline(Base):
    """故事时间线模型"""
    __tablename__ = "story_timelines"

    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, ForeignKey("novels.id"), nullable=False)
    
    # 时间点信息
    timeline_point = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # 时间属性
    story_day = Column(Integer, default=1)  # 故事内时间
    real_time_reference = Column(String(100))  # 现实时间参考
    duration = Column(String(100))  # 持续时间
    
    # 关联信息
    involved_chapters = Column(JSON, default=list)
    involved_characters = Column(JSON, default=list)
    key_events = Column(JSON, default=list)
    
    # 时间线类型
    timeline_type = Column(String(50), default="main")  # main, flashback, parallel
    
    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    novel = relationship("Novel", back_populates="story_timelines")

    def __repr__(self):
        return f"<StoryTimeline Day {self.story_day}: {self.timeline_point}>"


class NovelOutline(Base):
    """小说大纲模型"""
    __tablename__ = "novel_outlines"

    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, ForeignKey("novels.id"), nullable=False)
    
    # 大纲层级
    level = Column(Integer, nullable=False)  # 1=部分, 2=章节, 3=小节
    parent_id = Column(Integer, ForeignKey("novel_outlines.id"))
    
    # 大纲内容
    title = Column(String(200), nullable=False)
    summary = Column(Text, nullable=False)
    detailed_description = Column(Text)
    
    # 大纲属性
    order_index = Column(Integer, nullable=False)
    estimated_word_count = Column(Integer, default=0)
    actual_word_count = Column(Integer, default=0)
    
    # 状态
    completion_status = Column(String(50), default="planned")  # planned, writing, completed
    
    # 关联信息
    related_characters = Column(JSON, default=list)
    key_plot_points = Column(JSON, default=list)
    
    # AI生成信息
    ai_generated = Column(Boolean, default=False)
    ai_analysis = Column(JSON, default=dict)
    
    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    novel = relationship("Novel", back_populates="novel_outlines")
    children = relationship("NovelOutline", backref="parent", remote_side=[id])

    def __repr__(self):
        return f"<NovelOutline L{self.level}: {self.title}>"


class StyleGuide(Base):
    """文风指南模型"""
    __tablename__ = "style_guides"

    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, ForeignKey("novels.id"), nullable=False)
    
    # 文风分类
    style_category = Column(String(50), nullable=False)  # narrative, dialogue, description, etc.
    
    # 文风规则
    rules = Column(JSON, nullable=False)  # 具体的文风规则
    examples = Column(JSON, default=list)  # 示例文本
    
    # 文风特征
    tone = Column(String(50))  # 语调
    pace = Column(String(50))  # 节奏
    perspective = Column(String(50))  # 视角
    
    # 应用范围
    applicable_scenes = Column(JSON, default=list)  # 适用场景
    character_specific = Column(JSON, default=dict)  # 角色特定文风
    
    # AI分析
    ai_analysis = Column(JSON, default=dict)
    
    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    novel = relationship("Novel", back_populates="style_guides")

    def __repr__(self):
        return f"<StyleGuide {self.style_category}>"
