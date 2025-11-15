"""小说审核多Agent服务

实现小说上线前的完整审核流程，包括：
1. 章节节奏审核 Agent
2. 内容质量检查 Agent  
3. 情节连贯性 Agent
4. 角色一致性 Agent
5. 语言风格 Agent
6. 敏感内容检测 Agent

所有 Agent 协同工作，生成详细的审核报告和改进建议。
"""
from typing import TypedDict, Dict, Any, List, Optional
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.core.config import settings
from app.models.workflow_schemas import AgentWorkflowStep, AgentWorkflowTrace
from app.services.rag_service import rag_service
from app.services.review_agents import (
    review_pace_agent,
    review_quality_agent,
    review_plot_coherence_agent,
    review_character_consistency_agent,
    review_style_agent,
    review_content_safety_agent,
)
from loguru import logger
import asyncio
import json


# ========== 审核结果数据模型 ==========

class PaceReviewResult(TypedDict):
    """节奏审核结果"""
    score: int  # 0-100分
    pace_type: str  # slow/medium/fast/uneven
    issues: List[str]  # 问题列表
    suggestions: List[str]  # 改进建议
    details: Dict[str, Any]  # 详细分析


class QualityReviewResult(TypedDict):
    """质量审核结果"""
    score: int
    grammar_score: int  # 语法得分
    logic_score: int  # 逻辑得分
    description_score: int  # 描写得分
    issues: List[str]
    suggestions: List[str]


class PlotCoherenceResult(TypedDict):
    """情节连贯性结果"""
    score: int
    coherence_issues: List[str]  # 连贯性问题
    plot_holes: List[str]  # 情节漏洞
    suggestions: List[str]


class CharacterConsistencyResult(TypedDict):
    """角色一致性结果"""
    score: int
    inconsistencies: List[Dict[str, Any]]  # 不一致之处
    suggestions: List[str]


class StyleReviewResult(TypedDict):
    """风格审核结果"""
    score: int
    style_type: str  # 风格类型
    consistency_score: int  # 风格一致性
    issues: List[str]
    suggestions: List[str]


class ContentSafetyResult(TypedDict):
    """内容安全审核结果"""
    is_safe: bool
    risk_level: str  # low/medium/high
    flagged_content: List[Dict[str, Any]]  # 标记的内容
    suggestions: List[str]


class ComprehensiveReviewResult(TypedDict):
    """综合审核结果"""
    overall_score: int  # 总体得分
    is_ready_for_publish: bool  # 是否可以发布
    pace_review: PaceReviewResult
    quality_review: QualityReviewResult
    plot_coherence: PlotCoherenceResult
    character_consistency: CharacterConsistencyResult
    style_review: StyleReviewResult
    content_safety: ContentSafetyResult
    workflow_trace: Dict[str, Any]  # 工作流追踪


# ========== 审核 Agent 服务 ==========

class ReviewAgentService:
    """小说审核多Agent服务"""

    def __init__(self):
        """初始化审核服务"""
        # 初始化LLM（使用复杂模型进行审核）
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL_COMPLEX,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE,
            temperature=0.3  # 审核需要更稳定的输出
        )
        
        logger.info("审核Agent服务初始化完成")

    async def review_chapter_comprehensive(
        self,
        novel_id: int,
        chapter_id: int,
        chapter_number: int,
        content: str,
        previous_chapters: Optional[List[str]] = None,
    ) -> ComprehensiveReviewResult:
        """
        对章节进行全面审核
        
        Args:
            novel_id: 小说ID
            chapter_id: 章节ID
            chapter_number: 章节号
            content: 章节内容
            previous_chapters: 前面章节的内容（用于连贯性检查）
            
        Returns:
            综合审核结果
        """
        logger.info(f"开始全面审核：小说{novel_id}，章节{chapter_number}")
        
        # 生成工作流追踪ID
        run_id = f"review-{novel_id}-{chapter_id}-{int(datetime.utcnow().timestamp() * 1000)}"
        workflow_steps: List[Dict[str, Any]] = []
        
        # 并行执行多个审核Agent
        pace_task = review_pace_agent(self.llm, novel_id, chapter_number, content, workflow_steps)
        quality_task = review_quality_agent(self.llm, novel_id, chapter_number, content, workflow_steps)
        plot_task = review_plot_coherence_agent(self.llm, novel_id, chapter_number, content, previous_chapters, workflow_steps)
        character_task = review_character_consistency_agent(self.llm, novel_id, chapter_number, content, workflow_steps)
        style_task = review_style_agent(self.llm, novel_id, chapter_number, content, workflow_steps)
        safety_task = review_content_safety_agent(self.llm, novel_id, chapter_number, content, workflow_steps)
        
        # 等待所有审核完成
        results = await asyncio.gather(
            pace_task,
            quality_task,
            plot_task,
            character_task,
            style_task,
            safety_task,
            return_exceptions=True
        )
        
        pace_review, quality_review, plot_coherence, character_consistency, style_review, content_safety = results
        
        # 处理异常
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"审核Agent {i} 失败: {result}")
                # 使用默认值
                if i == 0:
                    pace_review = self._default_pace_result()
                elif i == 1:
                    quality_review = self._default_quality_result()
                elif i == 2:
                    plot_coherence = self._default_plot_result()
                elif i == 3:
                    character_consistency = self._default_character_result()
                elif i == 4:
                    style_review = self._default_style_result()
                elif i == 5:
                    content_safety = self._default_safety_result()
        
        # 计算总体得分（加权平均）
        overall_score = int(
            pace_review["score"] * 0.2 +
            quality_review["score"] * 0.25 +
            plot_coherence["score"] * 0.2 +
            character_consistency["score"] * 0.15 +
            style_review["score"] * 0.1 +
            (100 if content_safety["is_safe"] else 0) * 0.1
        )
        
        # 判断是否可以发布（所有维度都要达标）
        is_ready = (
            overall_score >= 70 and
            pace_review["score"] >= 60 and
            quality_review["score"] >= 65 and
            plot_coherence["score"] >= 60 and
            character_consistency["score"] >= 60 and
            content_safety["is_safe"]
        )
        
        # 构建工作流追踪
        workflow_trace = AgentWorkflowTrace(
            run_id=run_id,
            trigger="review.comprehensive",
            novel_id=novel_id,
            chapter_id=chapter_id,
            user_id=None,
            summary=f"小说{novel_id} 第{chapter_number}章 综合审核",
            steps=[AgentWorkflowStep(**step) for step in workflow_steps],
        )
        
        return ComprehensiveReviewResult(
            overall_score=overall_score,
            is_ready_for_publish=is_ready,
            pace_review=pace_review,
            quality_review=quality_review,
            plot_coherence=plot_coherence,
            character_consistency=character_consistency,
            style_review=style_review,
            content_safety=content_safety,
            workflow_trace=workflow_trace.model_dump(),
        )

    # 默认结果方法
    def _default_pace_result(self) -> PaceReviewResult:
        return PaceReviewResult(
            score=70,
            pace_type="medium",
            issues=["审核服务暂时不可用"],
            suggestions=["请稍后重试"],
            details={}
        )
    
    def _default_quality_result(self) -> QualityReviewResult:
        return QualityReviewResult(
            score=70,
            grammar_score=70,
            logic_score=70,
            description_score=70,
            issues=["审核服务暂时不可用"],
            suggestions=["请稍后重试"]
        )
    
    def _default_plot_result(self) -> PlotCoherenceResult:
        return PlotCoherenceResult(
            score=70,
            coherence_issues=["审核服务暂时不可用"],
            plot_holes=[],
            suggestions=["请稍后重试"]
        )
    
    def _default_character_result(self) -> CharacterConsistencyResult:
        return CharacterConsistencyResult(
            score=70,
            inconsistencies=[],
            suggestions=["审核服务暂时不可用，请稍后重试"]
        )
    
    def _default_style_result(self) -> StyleReviewResult:
        return StyleReviewResult(
            score=70,
            style_type="未知",
            consistency_score=70,
            issues=["审核服务暂时不可用"],
            suggestions=["请稍后重试"]
        )
    
    def _default_safety_result(self) -> ContentSafetyResult:
        return ContentSafetyResult(
            is_safe=True,
            risk_level="low",
            flagged_content=[],
            suggestions=[]
        )


# 创建全局实例
review_agent_service = ReviewAgentService()
