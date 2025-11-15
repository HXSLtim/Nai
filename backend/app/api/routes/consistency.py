from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from loguru import logger
from app.services.consistency_service import consistency_service
import json
import asyncio

logger.info("一致性检查路由模块正在加载...")

router = APIRouter()

logger.info("一致性检查路由器已创建")


class ConsistencyCheckRequest(BaseModel):
    novel_id: int
    chapter: int
    content: str
    current_day: int = 1


@router.get("/test")
async def test_consistency_route():
    """测试路由是否正常工作"""
    logger.info("一致性检查测试路由被调用")
    return {"status": "ok", "message": "一致性检查路由工作正常"}


@router.post("/check-stream")
async def check_consistency_stream(request: ConsistencyCheckRequest):
    logger.info(f"收到一致性检查请求: novel_id={request.novel_id}, chapter={request.chapter}")
    async def event_generator():
        try:
            async for event in consistency_service.check_content_stream(
                novel_id=request.novel_id,
                content=request.content,
                chapter=request.chapter,
                current_day=request.current_day,
            ):
                yield f"data: {json.dumps(event, ensure_ascii=False, default=str)}\n\n"
                await asyncio.sleep(0)
        except Exception as e:  # noqa: BLE001
            logger.error(f"一致性检查流式接口失败: {e}")
            error_payload = {"type": "error", "message": str(e)}
            yield f"data: {json.dumps(error_payload, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
