"""
角色管理API路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User
from app.models.character_schemas import (
    CharacterCreate, CharacterUpdate, CharacterResponse,
    CharacterRelationshipCreate, CharacterRelationshipUpdate, CharacterRelationshipResponse,
    CharacterAppearanceCreate, CharacterAppearanceResponse,
    CharacterAnalysisRequest, CharacterAnalysisResponse,
    CharacterOptimizationRequest, CharacterOptimizationResponse,
    MCPCharacterAction, MCPCharacterResponse,
    CharacterNetworkResponse, CharacterTimelineResponse
)
from app.crud import character as character_crud
from app.crud import novel as novel_crud
from app.api.dependencies import get_current_user
from app.services.character_mcp_service import character_mcp_service
from loguru import logger

router = APIRouter()


# ========== 角色CRUD操作 ==========

@router.post("/", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_character(
    character: CharacterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建角色"""
    # 验证小说权限
    novel = novel_crud.get_novel_by_id(db, character.novel_id)
    if not novel or novel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="小说不存在或无权访问"
        )
    
    # 检查角色名称是否重复
    existing_character = character_crud.get_character_by_name(
        db, character.novel_id, character.name
    )
    if existing_character:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"角色名称 '{character.name}' 已存在"
        )
    
    db_character = character_crud.create_character(db, character)
    logger.info(f"创建角色: {db_character.name} (ID: {db_character.id})")
    
    return db_character


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取角色详情"""
    character = character_crud.get_character(db, character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 验证权限
    novel = novel_crud.get_novel_by_id(db, character.novel_id)
    if not novel or novel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="无权访问该角色"
        )
    
    return character


@router.get("/novel/{novel_id}", response_model=List[CharacterResponse])
async def list_characters(
    novel_id: int,
    skip: int = 0,
    limit: int = 100,
    importance_level: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取小说的角色列表"""
    # 验证小说权限
    novel = novel_crud.get_novel_by_id(db, novel_id)
    if not novel or novel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="小说不存在或无权访问"
        )
    
    characters = character_crud.get_characters_by_novel(
        db, novel_id, skip, limit, importance_level
    )
    
    return characters


@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: int,
    character_update: CharacterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新角色"""
    character = character_crud.get_character(db, character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 验证权限
    novel = novel_crud.get_novel_by_id(db, character.novel_id)
    if not novel or novel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="无权访问该角色"
        )
    
    # 检查名称冲突
    if character_update.name and character_update.name != character.name:
        existing_character = character_crud.get_character_by_name(
            db, character.novel_id, character_update.name
        )
        if existing_character:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"角色名称 '{character_update.name}' 已存在"
            )
    
    updated_character = character_crud.update_character(db, character_id, character_update)
    logger.info(f"更新角色: {updated_character.name} (ID: {character_id})")
    
    return updated_character


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(
    character_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除角色"""
    character = character_crud.get_character(db, character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 验证权限
    novel = novel_crud.get_novel_by_id(db, character.novel_id)
    if not novel or novel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="无权访问该角色"
        )
    
    success = character_crud.delete_character(db, character_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除角色失败"
        )
    
    logger.info(f"删除角色: {character.name} (ID: {character_id})")


# ========== 角色关系管理 ==========

@router.post("/relationships", response_model=CharacterRelationshipResponse, status_code=status.HTTP_201_CREATED)
async def create_character_relationship(
    relationship: CharacterRelationshipCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建角色关系"""
    # 验证小说权限
    novel = novel_crud.get_novel_by_id(db, relationship.novel_id)
    if not novel or novel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="小说不存在或无权访问"
        )
    
    # 验证角色存在
    char_a = character_crud.get_character(db, relationship.character_a_id)
    char_b = character_crud.get_character(db, relationship.character_b_id)
    
    if not char_a or not char_b:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    if char_a.novel_id != relationship.novel_id or char_b.novel_id != relationship.novel_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色不属于指定小说"
        )
    
    db_relationship = character_crud.create_character_relationship(db, relationship)
    
    # 添加角色名称到响应
    response_data = db_relationship.__dict__.copy()
    response_data["character_a_name"] = char_a.name
    response_data["character_b_name"] = char_b.name
    
    logger.info(f"创建角色关系: {char_a.name} - {char_b.name} ({relationship.relationship_type})")
    
    return CharacterRelationshipResponse(**response_data)


@router.get("/{character_id}/relationships", response_model=List[CharacterRelationshipResponse])
async def get_character_relationships(
    character_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取角色的所有关系"""
    character = character_crud.get_character(db, character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 验证权限
    novel = novel_crud.get_novel_by_id(db, character.novel_id)
    if not novel or novel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="无权访问该角色"
        )
    
    relationships = character_crud.get_character_relationships(db, character_id)
    
    # 添加角色名称
    response_relationships = []
    for rel in relationships:
        response_data = rel.__dict__.copy()
        response_data["character_a_name"] = rel.character_a.name
        response_data["character_b_name"] = rel.character_b.name
        response_relationships.append(CharacterRelationshipResponse(**response_data))
    
    return response_relationships


@router.get("/novel/{novel_id}/network", response_model=CharacterNetworkResponse)
async def get_character_network(
    novel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取小说的角色关系网络"""
    # 验证小说权限
    novel = novel_crud.get_novel_by_id(db, novel_id)
    if not novel or novel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="小说不存在或无权访问"
        )
    
    characters = character_crud.get_characters_by_novel(db, novel_id)
    relationships = character_crud.get_novel_relationships(db, novel_id)
    network_analysis = character_crud.get_character_network(db, novel_id)
    
    # 构建关系响应
    relationship_responses = []
    for rel in relationships:
        response_data = rel.__dict__.copy()
        response_data["character_a_name"] = rel.character_a.name
        response_data["character_b_name"] = rel.character_b.name
        relationship_responses.append(CharacterRelationshipResponse(**response_data))
    
    return CharacterNetworkResponse(
        novel_id=novel_id,
        characters=characters,
        relationships=relationship_responses,
        network_analysis=network_analysis
    )


# ========== 角色出场管理 ==========

@router.post("/appearances", response_model=CharacterAppearanceResponse, status_code=status.HTTP_201_CREATED)
async def create_character_appearance(
    appearance: CharacterAppearanceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建角色出场记录"""
    character = character_crud.get_character(db, appearance.character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 验证权限
    novel = novel_crud.get_novel_by_id(db, character.novel_id)
    if not novel or novel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="无权访问该角色"
        )
    
    # 验证章节存在
    chapter = novel_crud.get_chapter_by_id(db, appearance.chapter_id)
    if not chapter or chapter.novel_id != character.novel_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不存在或不属于同一小说"
        )
    
    db_appearance = character_crud.create_character_appearance(db, appearance)
    
    # 更新角色最后出现章节
    character_crud.update_character_last_appearance(
        db, character.id, chapter.chapter_number
    )
    
    # 构建响应
    response_data = db_appearance.__dict__.copy()
    response_data["character_name"] = character.name
    response_data["chapter_number"] = chapter.chapter_number
    
    return CharacterAppearanceResponse(**response_data)


@router.get("/{character_id}/timeline", response_model=CharacterTimelineResponse)
async def get_character_timeline(
    character_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取角色时间线"""
    character = character_crud.get_character(db, character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 验证权限
    novel = novel_crud.get_novel_by_id(db, character.novel_id)
    if not novel or novel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="无权访问该角色"
        )
    
    appearances = character_crud.get_character_appearances(db, character_id)
    
    # 构建出场记录响应
    appearance_responses = []
    for app in appearances:
        response_data = app.__dict__.copy()
        response_data["character_name"] = character.name
        response_data["chapter_number"] = app.chapter.chapter_number
        appearance_responses.append(CharacterAppearanceResponse(**response_data))
    
    return CharacterTimelineResponse(
        character_id=character_id,
        character_name=character.name,
        appearances=appearance_responses
    )


# ========== MCP功能 ==========

@router.post("/mcp/execute", response_model=MCPCharacterResponse)
async def execute_mcp_action(
    action: MCPCharacterAction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """执行MCP角色操作"""
    try:
        # 如果有novel_id，验证权限
        if action.novel_id:
            novel = novel_crud.get_novel_by_id(db, action.novel_id)
            if not novel or novel.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="小说不存在或无权访问"
                )
        
        # 如果有character_id，验证权限
        if action.character_id:
            character = character_crud.get_character(db, action.character_id)
            if not character:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="角色不存在"
                )
            
            novel = novel_crud.get_novel_by_id(db, character.novel_id)
            if not novel or novel.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="无权访问该角色"
                )
        
        # 执行MCP操作
        result = await character_mcp_service.execute_action(db, action, current_user.id)
        
        logger.info(f"MCP操作执行: {action.action} - 用户: {current_user.username}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MCP操作失败: {action.action} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"操作执行失败: {str(e)}"
        )


@router.get("/novel/{novel_id}/search")
async def search_characters(
    novel_id: int,
    q: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """搜索角色"""
    # 验证小说权限
    novel = novel_crud.get_novel_by_id(db, novel_id)
    if not novel or novel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="小说不存在或无权访问"
        )
    
    characters = character_crud.search_characters(db, novel_id, q)
    
    return {
        "novel_id": novel_id,
        "search_term": q,
        "characters": characters,
        "count": len(characters)
    }
