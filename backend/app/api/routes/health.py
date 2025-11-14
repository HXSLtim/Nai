"""
健康检查路由
"""
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@router.get("/ping")
async def ping():
    """简单ping接口"""
    return {"message": "pong"}
