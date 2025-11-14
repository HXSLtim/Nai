"""
用户认证路由
提供注册、登录、获取当前用户等接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.schemas import UserCreate, UserLogin, UserResponse, Token
from app.crud.user import (
    get_user_by_username,
    get_user_by_email,
    create_user,
    authenticate_user
)
from app.core.security import create_access_token
from app.api.dependencies import get_current_user
from app.models.user import User
from loguru import logger

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册

    创建新用户账号

    Args:
        user: 用户注册信息
        db: 数据库会话

    Returns:
        Token响应（包含access_token和用户信息）

    Raises:
        HTTPException: 用户名或邮箱已存在
    """
    # 检查用户名是否已存在
    if get_user_by_username(db, username=user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 检查邮箱是否已存在
    if get_user_by_email(db, email=user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )

    # 创建用户
    db_user = create_user(db, user)

    # 生成Token
    access_token = create_access_token(data={"sub": str(db_user.id)})

    logger.info(f"新用户注册：{db_user.username}（{db_user.email}）")

    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(db_user)
    )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录

    使用用户名和密码登录，返回JWT Token

    Args:
        credentials: 登录凭证（用户名 + 密码）
        db: 数据库会话

    Returns:
        Token响应（包含access_token和用户信息）

    Raises:
        HTTPException: 用户名或密码错误，或用户已被禁用
    """
    user = authenticate_user(db, credentials.username, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )

    # 生成Token
    access_token = create_access_token(data={"sub": str(user.id)})

    logger.info(f"用户登录：{user.username}")

    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    获取当前用户信息

    需要认证（提供有效的Bearer Token）

    Args:
        current_user: 当前登录用户（通过依赖注入自动获取）

    Returns:
        当前用户信息
    """
    return UserResponse.model_validate(current_user)
