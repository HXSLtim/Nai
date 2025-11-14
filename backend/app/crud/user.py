"""
用户CRUD操作
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.schemas import UserCreate
from app.core.security import get_password_hash, verify_password


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """根据ID获取用户"""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user: UserCreate) -> User:
    """
    创建用户

    Args:
        db: 数据库会话
        user: 用户创建Schema

    Returns:
        创建的用户对象
    """
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    验证用户身份

    Args:
        db: 数据库会话
        username: 用户名
        password: 明文密码

    Returns:
        验证成功返回用户对象，失败返回None
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
