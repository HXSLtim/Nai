"""资料检索相关路由

提供统一的资料检索接口，当前使用维基百科作为默认数据源，后续可替换为 MCP 搜索。
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from httpx import AsyncClient
from loguru import logger

from app.api.routes.auth import get_current_user
from app.db.base import get_db
from app.models.schemas import ResearchRequest, ResearchResponse, ResearchResult
from app.models.user import User

router = APIRouter()


@router.post("/search", response_model=ResearchResponse)
async def research_search(
    request: ResearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),  # 保留以便后续扩展与小说/章节绑定
):
    """资料检索

    目前使用中文维基百科作为公共资料来源，用于历史/地理/现实背景等信息检索。
    后续可以在不改动前端的前提下，将内部实现替换为 MCP 搜索。
    """
    query = (request.query or "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="检索问题不能为空")

    try:
        # 使用中文维基百科开放API进行简单检索
        async with AsyncClient(timeout=10.0) as client:
            params = {
                "action": "query",
                "list": "search",
                "format": "json",
                "srsearch": query,
                "srlimit": 5,
            }
            resp = await client.get("https://zh.wikipedia.org/w/api.php", params=params)
            if resp.status_code != 200:
                logger.warning(
                    f"维基百科检索失败，status={resp.status_code}, body={resp.text[:200]}"
                )
                return ResearchResponse(query=query, results=[])

            data = resp.json()
            search_results = data.get("query", {}).get("search", [])

        results: list[ResearchResult] = []
        for item in search_results:
            title = str(item.get("title") or "").strip()
            page_id = item.get("pageid")
            snippet = str(item.get("snippet") or "")

            # 去掉 HTML 高亮标签
            summary = (
                snippet.replace("<span class=\"searchmatch\">", "")
                .replace("</span>", "")
                .replace("<span class=\"searchmatch\">", "")
            )

            url = f"https://zh.wikipedia.org/?curid={page_id}" if page_id else None

            results.append(
                ResearchResult(
                    title=title or "未命名条目",
                    summary=summary,
                    source="zh.wikipedia.org",
                    url=url,
                    metadata={"page_id": page_id},
                )
            )

        return ResearchResponse(query=query, results=results)

    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001
        logger.error(f"资料检索失败: {e}")
        raise HTTPException(status_code=500, detail=f"资料检索失败: {str(e)}")
