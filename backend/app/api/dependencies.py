"""
API依赖注入
提供常用的依赖函数，如认证、权限验证等
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.core.security import verify_token
from app.crud.user import get_user_by_id
from app.models.user import User

# HTTP Bearer认证方案
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前登录用户

    从JWT Token中解析用户信息并验证

    Args:
        credentials: HTTP Authorization头中的Bearer Token
        db: 数据库会话

    Returns:
        当前用户对象

    Raises:
        HTTPException: Token无效或用户不存在
    """
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_id(db, user_id=int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )

    return user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前超级管理员

    验证当前用户是否为超级管理员

    Args:
        current_user: 当前用户

    Returns:
        当前用户对象（超级管理员）

    Raises:
        HTTPException: 权限不足
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user
