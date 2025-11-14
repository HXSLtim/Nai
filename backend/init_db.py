"""
数据库初始化脚本

创建所有数据表
"""
from app.db.base import Base, engine
from app.models.user import User  # 导入所有模型，确保被SQLAlchemy发现
from app.models.novel import Novel, Chapter, StyleSample

print("正在创建数据库表...")
Base.metadata.create_all(bind=engine)
print("[SUCCESS] 数据库初始化完成！")
print(f"[INFO] 创建的表：{', '.join(Base.metadata.tables.keys())}")
