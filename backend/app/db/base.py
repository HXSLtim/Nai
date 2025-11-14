"""
数据库基础配置
使用SQLite简化开发
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 使用SQLite（简化，生产环境建议PostgreSQL）
SQLALCHEMY_DATABASE_URL = "sqlite:///./novel.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite需要此参数
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    获取数据库会话

    用于FastAPI依赖注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
