"""
小说和章节管理API路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User
from app.models.schemas import (
    NovelCreate,
    NovelUpdate,
    NovelResponse,
    ChapterCreate,
    ChapterUpdate,
    ChapterResponse,
    ChapterWithReviewResponse,
    ConsistencySummary,
)
from app.crud import novel as novel_crud
from app.api.dependencies import get_current_user
from app.services.rag_service import rag_service
from app.services.editor_service import editor_service
from app.services.consistency_service import consistency_service
from loguru import logger

router = APIRouter()


# ========== Novel 路由 ==========

@router.post("/", response_model=NovelResponse, status_code=status.HTTP_201_CREATED)
async def create_novel(
    novel: NovelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建小说

    需要认证
    """
    db_novel = novel_crud.create_novel(db, novel, user_id=current_user.id)
    return db_novel


@router.get("/", response_model=List[NovelResponse])
async def list_my_novels(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的所有小说

    需要认证
    """
    novels = novel_crud.get_novels_by_user(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return novels


@router.get("/{novel_id}", response_model=NovelResponse)
async def get_novel(
    novel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取小说详情

    需要认证，只能查看自己的小说
    """
    db_novel = novel_crud.get_novel_by_id(db, novel_id)
    if not db_novel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="小说不存在"
        )

    # 验证权限：只能查看自己的小说
    if db_novel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此小说"
        )

    return db_novel


@router.put("/{novel_id}", response_model=NovelResponse)
async def update_novel(
    novel_id: int,
    novel_update: NovelUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新小说信息

    需要认证，只能更新自己的小说
    """
    db_novel = novel_crud.get_novel_by_id(db, novel_id)
    if not db_novel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="小说不存在"
        )

    # 验证权限
    if db_novel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此小说"
        )

    updated_novel = novel_crud.update_novel(db, novel_id, novel_update)

    # 若本次更新包含世界观设定，则将其索引到RAG（忽略失败）
    if novel_update.worldview is not None:
        try:
            await rag_service.index_content(
                novel_id=updated_novel.id,
                chapter=0,
                content=updated_novel.worldview or "",
                metadata={"source": "worldview"},
            )
            logger.info(f"已将小说{updated_novel.id}的世界观设定索引到RAG")
        except Exception as e:  # noqa: BLE001
            logger.warning(f"索引小说{updated_novel.id}世界观到RAG失败: {e}")

    return updated_novel


@router.delete("/{novel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_novel(
    novel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除小说（级联删除所有章节）

    需要认证，只能删除自己的小说
    """
    db_novel = novel_crud.get_novel_by_id(db, novel_id)
    if not db_novel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="小说不存在"
        )

    # 验证权限
    if db_novel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此小说"
        )

    novel_crud.delete_novel(db, novel_id)
    return None


# ========== Chapter 路由 ==========

@router.post("/{novel_id}/chapters", response_model=ChapterResponse, status_code=status.HTTP_201_CREATED)
async def create_chapter(
    novel_id: int,
    chapter: ChapterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建章节

    需要认证，只能为自己的小说创建章节
    """
    # 验证小说存在且有权限
    db_novel = novel_crud.get_novel_by_id(db, novel_id)
    if not db_novel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="小说不存在"
        )

    if db_novel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权为此小说添加章节"
        )

    # 检查章节号是否已存在
    existing_chapter = novel_crud.get_chapter_by_number(
        db,
        novel_id,
        chapter.chapter_number
    )
    if existing_chapter:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"章节 {chapter.chapter_number} 已存在"
        )

    db_chapter = novel_crud.create_chapter(db, novel_id, chapter)

    # 将章节内容索引到RAG（忽略失败）
    try:
        await rag_service.index_content(
            novel_id=novel_id,
            chapter=db_chapter.chapter_number,
            content=db_chapter.content,
            metadata={"source": "chapter", "chapter_id": db_chapter.id},
        )
        logger.info(f"已将小说{novel_id}第{db_chapter.chapter_number}章内容索引到RAG")
    except Exception as e:
        logger.warning(f"索引章节内容到RAG失败（novel_id={novel_id}, chapter={db_chapter.chapter_number}）: {e}")

    return db_chapter


@router.get("/{novel_id}/chapters", response_model=List[ChapterResponse])
async def list_chapters(
    novel_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取小说的所有章节

    需要认证，只能查看自己小说的章节
    """
    # 验证小说存在且有权限
    db_novel = novel_crud.get_novel_by_id(db, novel_id)
    if not db_novel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="小说不存在"
        )

    if db_novel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此小说的章节"
        )

    chapters = novel_crud.get_chapters_by_novel(
        db,
        novel_id,
        skip=skip,
        limit=limit
    )
    return chapters


@router.get("/{novel_id}/chapters/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(
    novel_id: int,
    chapter_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取章节详情

    需要认证，只能查看自己小说的章节
    """
    # 验证小说存在且有权限
    db_novel = novel_crud.get_novel_by_id(db, novel_id)
    if not db_novel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="小说不存在"
        )

    if db_novel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此小说的章节"
        )

    db_chapter = novel_crud.get_chapter_by_id(db, chapter_id)
    if not db_chapter or db_chapter.novel_id != novel_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不存在"
        )

    return db_chapter


@router.put("/{novel_id}/chapters/{chapter_id}", response_model=ChapterWithReviewResponse)
async def update_chapter(
    novel_id: int,
    chapter_id: int,
    chapter_update: ChapterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新章节

    需要认证，只能更新自己小说的章节
    """
    # 验证小说存在且有权限
    db_novel = novel_crud.get_novel_by_id(db, novel_id)
    if not db_novel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="小说不存在"
        )

    if db_novel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此小说的章节"
        )

    db_chapter = novel_crud.get_chapter_by_id(db, chapter_id)
    if not db_chapter or db_chapter.novel_id != novel_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不存在"
        )

    updated_chapter = novel_crud.update_chapter(db, chapter_id, chapter_update)

    # 更新章节后重新索引内容到RAG（忽略失败）
    try:
        await rag_service.index_content(
            novel_id=novel_id,
            chapter=updated_chapter.chapter_number,
            content=updated_chapter.content,
            metadata={"source": "chapter", "chapter_id": updated_chapter.id},
        )
        logger.info(f"已重新索引小说{novel_id}第{updated_chapter.chapter_number}章内容到RAG")
    except Exception as e:
        logger.warning(
            f"重新索引章节内容到RAG失败（novel_id={novel_id}, chapter={updated_chapter.chapter_number}）: {e}"
        )

    # 一致性检查（规则引擎 + 知识图谱 + 时间线），失败不影响保存
    consistency_summary: ConsistencySummary | None = None
    try:
        consistency_result = await consistency_service.check_content(
            novel_id=novel_id,
            content=updated_chapter.content or "",
            chapter=updated_chapter.chapter_number,
            current_day=1,
        )
        consistency_summary = ConsistencySummary(
            has_conflict=consistency_result.get("has_conflict", False),
            violations=consistency_result.get("violations", []),
            checks_performed=consistency_result.get("checks_performed", []),
        )
    except Exception as e:  # noqa: BLE001
        logger.warning(
            f"一致性检查失败（novel_id={novel_id}, chapter={updated_chapter.chapter_number}）: {e}"
        )

    # 手动保存时触发轻量编辑审核（失败不影响保存）
    editor_review = await editor_service.review_chapter(
        novel=db_novel,
        chapter=updated_chapter,
    )

    # 显式构造响应，避免ORM内部字段干扰
    return ChapterWithReviewResponse(
        id=updated_chapter.id,
        novel_id=updated_chapter.novel_id,
        chapter_number=updated_chapter.chapter_number,
        title=updated_chapter.title,
        content=updated_chapter.content,
        word_count=updated_chapter.word_count,
        created_at=updated_chapter.created_at,
        updated_at=updated_chapter.updated_at,
        editor_review=editor_review,
        consistency_summary=consistency_summary,
    )


@router.delete("/{novel_id}/chapters/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chapter(
    novel_id: int,
    chapter_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除章节

    需要认证，只能删除自己小说的章节
    """
    # 验证小说存在且有权限
    db_novel = novel_crud.get_novel_by_id(db, novel_id)
    if not db_novel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="小说不存在"
        )

    if db_novel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此小说的章节"
        )

    db_chapter = novel_crud.get_chapter_by_id(db, chapter_id)
    if not db_chapter or db_chapter.novel_id != novel_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不存在"
        )

    success = await novel_crud.delete_chapter(db, chapter_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除章节失败"
        )
    return None
