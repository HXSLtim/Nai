"""章节审核API路由"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from loguru import logger
from app.services.review_agent_service import review_agent_service
import json
import asyncio


router = APIRouter()


class ChapterReviewRequest(BaseModel):
    """章节审核请求"""
    novel_id: int
    chapter_id: int
    chapter_number: int
    content: str
    previous_chapters: Optional[List[str]] = None  # 前面章节内容（用于连贯性检查）


@router.post("/chapter")
async def review_chapter(request: ChapterReviewRequest):
    """
    对章节进行全面审核
    
    返回综合审核结果，包括：
    - 节奏审核
    - 质量检查
    - 情节连贯性
    - 角色一致性
    - 语言风格
    - 内容安全
    """
    logger.info(f"收到章节审核请求: novel_id={request.novel_id}, chapter={request.chapter_number}")
    
    try:
        result = await review_agent_service.review_chapter_comprehensive(
            novel_id=request.novel_id,
            chapter_id=request.chapter_id,
            chapter_number=request.chapter_number,
            content=request.content,
            previous_chapters=request.previous_chapters,
        )
        
        logger.info(f"审核完成: 总分={result['overall_score']}, 可发布={result['is_ready_for_publish']}")
        return result
        
    except Exception as e:
        logger.error(f"章节审核失败: {e}")
        raise HTTPException(status_code=500, detail=f"审核失败: {str(e)}")


@router.post("/chapter-stream")
async def review_chapter_stream(request: ChapterReviewRequest):
    """
    流式章节审核
    
    实时返回各个Agent的审核进度和结果
    """
    logger.info(f"收到流式章节审核请求: novel_id={request.novel_id}, chapter={request.chapter_number}")
    
    async def event_generator():
        try:
            # 发送开始事件
            yield f"data: {json.dumps({'type': 'start', 'message': '开始审核'}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0)
            
            # 创建工作流步骤列表
            workflow_steps: List[dict] = []
            
            # 依次执行各个Agent并流式返回结果
            from app.services.review_agents import (
                review_pace_agent,
                review_quality_agent,
                review_plot_coherence_agent,
                review_character_consistency_agent,
                review_style_agent,
                review_content_safety_agent,
            )
            
            # 1. 节奏审核
            yield f"data: {json.dumps({'type': 'agent_start', 'agent': 'pace', 'message': '正在审核节奏...'}, ensure_ascii=False)}\n\n"
            pace_result = await review_pace_agent(
                review_agent_service.llm,
                request.novel_id,
                request.chapter_number,
                request.content,
                workflow_steps
            )
            yield f"data: {json.dumps({'type': 'agent_result', 'agent': 'pace', 'result': pace_result}, ensure_ascii=False, default=str)}\n\n"
            await asyncio.sleep(0)
            
            # 2. 质量检查
            yield f"data: {json.dumps({'type': 'agent_start', 'agent': 'quality', 'message': '正在检查质量...'}, ensure_ascii=False)}\n\n"
            quality_result = await review_quality_agent(
                review_agent_service.llm,
                request.novel_id,
                request.chapter_number,
                request.content,
                workflow_steps
            )
            yield f"data: {json.dumps({'type': 'agent_result', 'agent': 'quality', 'result': quality_result}, ensure_ascii=False, default=str)}\n\n"
            await asyncio.sleep(0)
            
            # 3. 情节连贯性
            yield f"data: {json.dumps({'type': 'agent_start', 'agent': 'plot', 'message': '正在检查情节连贯性...'}, ensure_ascii=False)}\n\n"
            plot_result = await review_plot_coherence_agent(
                review_agent_service.llm,
                request.novel_id,
                request.chapter_number,
                request.content,
                request.previous_chapters,
                workflow_steps
            )
            yield f"data: {json.dumps({'type': 'agent_result', 'agent': 'plot', 'result': plot_result}, ensure_ascii=False, default=str)}\n\n"
            await asyncio.sleep(0)
            
            # 4. 角色一致性
            yield f"data: {json.dumps({'type': 'agent_start', 'agent': 'character', 'message': '正在检查角色一致性...'}, ensure_ascii=False)}\n\n"
            character_result = await review_character_consistency_agent(
                review_agent_service.llm,
                request.novel_id,
                request.chapter_number,
                request.content,
                workflow_steps
            )
            yield f"data: {json.dumps({'type': 'agent_result', 'agent': 'character', 'result': character_result}, ensure_ascii=False, default=str)}\n\n"
            await asyncio.sleep(0)
            
            # 5. 语言风格
            yield f"data: {json.dumps({'type': 'agent_start', 'agent': 'style', 'message': '正在审核语言风格...'}, ensure_ascii=False)}\n\n"
            style_result = await review_style_agent(
                review_agent_service.llm,
                request.novel_id,
                request.chapter_number,
                request.content,
                workflow_steps
            )
            yield f"data: {json.dumps({'type': 'agent_result', 'agent': 'style', 'result': style_result}, ensure_ascii=False, default=str)}\n\n"
            await asyncio.sleep(0)
            
            # 6. 内容安全
            yield f"data: {json.dumps({'type': 'agent_start', 'agent': 'safety', 'message': '正在检测内容安全...'}, ensure_ascii=False)}\n\n"
            safety_result = await review_content_safety_agent(
                review_agent_service.llm,
                request.novel_id,
                request.chapter_number,
                request.content,
                workflow_steps
            )
            yield f"data: {json.dumps({'type': 'agent_result', 'agent': 'safety', 'result': safety_result}, ensure_ascii=False, default=str)}\n\n"
            await asyncio.sleep(0)
            
            # 计算总体得分
            overall_score = int(
                pace_result["score"] * 0.2 +
                quality_result["score"] * 0.25 +
                plot_result["score"] * 0.2 +
                character_result["score"] * 0.15 +
                style_result["score"] * 0.1 +
                (100 if safety_result["is_safe"] else 0) * 0.1
            )
            
            is_ready = (
                overall_score >= 70 and
                pace_result["score"] >= 60 and
                quality_result["score"] >= 65 and
                plot_result["score"] >= 60 and
                character_result["score"] >= 60 and
                safety_result["is_safe"]
            )
            
            # 发送汇总结果
            summary = {
                "type": "summary",
                "overall_score": overall_score,
                "is_ready_for_publish": is_ready,
                "pace_review": pace_result,
                "quality_review": quality_result,
                "plot_coherence": plot_result,
                "character_consistency": character_result,
                "style_review": style_result,
                "content_safety": safety_result,
            }
            yield f"data: {json.dumps(summary, ensure_ascii=False, default=str)}\n\n"
            
            logger.info(f"流式审核完成: 总分={overall_score}, 可发布={is_ready}")
            
        except Exception as e:
            logger.error(f"流式审核失败: {e}")
            error_payload = {"type": "error", "message": str(e)}
            yield f"data: {json.dumps(error_payload, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/test")
async def test_review_route():
    """测试审核路由是否正常工作"""
    logger.info("审核路由测试被调用")
    return {"status": "ok", "message": "审核路由工作正常"}
