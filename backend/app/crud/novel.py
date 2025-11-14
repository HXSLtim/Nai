"""
小说CRUD操作
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.novel import Novel, Chapter, StyleSample
from app.models.schemas import NovelCreate, NovelUpdate, ChapterCreate, ChapterUpdate, StyleSampleCreate


# ========== Novel CRUD ==========

def get_novel_by_id(db: Session, novel_id: int) -> Optional[Novel]:
    """根据ID获取小说"""
    return db.query(Novel).filter(Novel.id == novel_id).first()


def get_novels_by_user(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Novel]:
    """
    获取用户的所有小说

    Args:
        db: 数据库会话
        user_id: 用户ID
        skip: 跳过条数
        limit: 返回条数限制

    Returns:
        小说列表
    """
    return db.query(Novel).filter(
        Novel.user_id == user_id
    ).offset(skip).limit(limit).all()


def create_novel(db: Session, novel: NovelCreate, user_id: int) -> Novel:
    """
    创建小说

    Args:
        db: 数据库会话
        novel: 小说创建Schema
        user_id: 作者用户ID

    Returns:
        创建的小说对象
    """
    db_novel = Novel(
        title=novel.title,
        genre=novel.genre,
        description=novel.description,
        worldview=novel.worldview,
        user_id=user_id
    )
    db.add(db_novel)
    db.commit()
    db.refresh(db_novel)
    return db_novel


def update_novel(
    db: Session,
    novel_id: int,
    novel_update: NovelUpdate
) -> Optional[Novel]:
    """
    更新小说

    Args:
        db: 数据库会话
        novel_id: 小说ID
        novel_update: 小说更新Schema

    Returns:
        更新后的小说对象，如果不存在返回None
    """
    db_novel = get_novel_by_id(db, novel_id)
    if not db_novel:
        return None

    # 只更新提供的字段
    update_data = novel_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_novel, field, value)

    db.commit()
    db.refresh(db_novel)
    return db_novel


def delete_novel(db: Session, novel_id: int) -> bool:
    """
    删除小说（级联删除所有章节）

    Args:
        db: 数据库会话
        novel_id: 小说ID

    Returns:
        删除成功返回True，小说不存在返回False
    """
    db_novel = get_novel_by_id(db, novel_id)
    if not db_novel:
        return False

    db.delete(db_novel)
    db.commit()
    return True


# ========== Chapter CRUD ==========

def get_chapter_by_id(db: Session, chapter_id: int) -> Optional[Chapter]:
    """根据ID获取章节"""
    return db.query(Chapter).filter(Chapter.id == chapter_id).first()


def get_chapter_by_number(
    db: Session,
    novel_id: int,
    chapter_number: int
) -> Optional[Chapter]:
    """根据章节号获取章节"""
    return db.query(Chapter).filter(
        Chapter.novel_id == novel_id,
        Chapter.chapter_number == chapter_number
    ).first()


def get_chapters_by_novel(
    db: Session,
    novel_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Chapter]:
    """
    获取小说的所有章节

    Args:
        db: 数据库会话
        novel_id: 小说ID
        skip: 跳过条数
        limit: 返回条数限制

    Returns:
        章节列表（按章节号排序）
    """
    return db.query(Chapter).filter(
        Chapter.novel_id == novel_id
    ).order_by(Chapter.chapter_number).offset(skip).limit(limit).all()


def create_chapter(
    db: Session,
    novel_id: int,
    chapter: ChapterCreate
) -> Chapter:
    """
    创建章节

    Args:
        db: 数据库会话
        novel_id: 小说ID
        chapter: 章节创建Schema

    Returns:
        创建的章节对象
    """
    # 计算字数
    word_count = len(chapter.content)

    db_chapter = Chapter(
        novel_id=novel_id,
        chapter_number=chapter.chapter_number,
        title=chapter.title,
        content=chapter.content,
        word_count=word_count
    )
    db.add(db_chapter)
    db.commit()
    db.refresh(db_chapter)
    return db_chapter


def update_chapter(
    db: Session,
    chapter_id: int,
    chapter_update: ChapterUpdate
) -> Optional[Chapter]:
    """
    更新章节

    Args:
        db: 数据库会话
        chapter_id: 章节ID
        chapter_update: 章节更新Schema

    Returns:
        更新后的章节对象，如果不存在返回None
    """
    db_chapter = get_chapter_by_id(db, chapter_id)
    if not db_chapter:
        return None

    # 只更新提供的字段
    update_data = chapter_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_chapter, field, value)

    # 如果更新了内容，重新计算字数
    if "content" in update_data:
        db_chapter.word_count = len(db_chapter.content)

    db.commit()
    db.refresh(db_chapter)
    return db_chapter


async def delete_chapter(db: Session, chapter_id: int) -> bool:
    """
    删除章节（同时清理RAG数据）

    Args:
        db: 数据库会话
        chapter_id: 章节ID

    Returns:
        删除成功返回True，章节不存在返回False
    """
    from app.services.rag_service import rag_service
    from loguru import logger
    
    db_chapter = get_chapter_by_id(db, chapter_id)
    if not db_chapter:
        return False

    novel_id = db_chapter.novel_id
    chapter_number = db_chapter.chapter_number
    
    try:
        # 先清理RAG数据
        await rag_service.cleanup_chapter_data(novel_id, chapter_number)
        logger.info(f"已清理章节{chapter_id}的RAG数据")
        
        # 删除数据库记录
        db.delete(db_chapter)
        db.commit()
        
        logger.info(f"成功删除章节{chapter_id}")
        return True
        
    except Exception as e:
        logger.error(f"删除章节{chapter_id}失败: {e}")
        db.rollback()
        return False


# ========== StyleSample CRUD ==========

def get_style_sample_by_id(db: Session, sample_id: int) -> Optional[StyleSample]:
    """根据ID获取文风样本"""
    return db.query(StyleSample).filter(StyleSample.id == sample_id).first()


def get_style_samples_by_novel(
    db: Session,
    novel_id: int
) -> List[StyleSample]:
    """获取小说下的所有文风样本"""
    return db.query(StyleSample).filter(StyleSample.novel_id == novel_id).order_by(StyleSample.id.desc()).all()


def create_style_sample(
    db: Session,
    style_sample: StyleSampleCreate
) -> StyleSample:
    """创建文风样本"""
    db_sample = StyleSample(
        novel_id=style_sample.novel_id,
        name=style_sample.name,
        sample_text=style_sample.sample_text,
        style_features=None,
    )
    db.add(db_sample)
    db.commit()
    db.refresh(db_sample)
    return db_sample
