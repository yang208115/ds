"""
模块名称：personas.py
主要功能：Persona相关的API路由端点
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, get_current_user_optional
from app.crud.persona import persona as crud_persona
from app.db.models.persona import Persona
from app.schemas.user import User
from app.schemas.persona import (
    PersonaCreate,
    PersonaUpdate,
    PersonaResponse,
    PersonaSearch,
    PersonaListResponse
)

# 创建路由
router = APIRouter()


@router.post("/", response_model=PersonaResponse)
def create_persona(
    *,
    db: Session = Depends(get_db),
    persona_in: PersonaCreate,
    current_user: User = Depends(get_current_user)
) -> PersonaResponse:
    """
    创建新的人设记录
    
    Args:
        db: 数据库会话
        persona_in: 创建数据
        
    Returns:
        PersonaResponse: 创建的人设记录
    """

    # 检查名称是否已存在
    existing = db.query(Persona).filter(
        Persona.name == persona_in.name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"人设名称 '{persona_in.name}' 已存在"
        )
    
    persona_in.author_uuid = current_user.uuid
    persona = crud_persona.create(db=db, obj_in=persona_in)
    return PersonaResponse.from_db(persona)


@router.get("/{persona_id}", response_model=PersonaResponse)
def read_persona(
    *,
    db: Session = Depends(get_db),
    persona_id: int
) -> PersonaResponse:
    """
    根据ID获取人设记录
    
    Args:
        db: 数据库会话
        persona_id: 人设ID
        
    Returns:
        PersonaResponse: 人设记录
        
    Raises:
        HTTPException: 记录不存在时抛出404错误
    """
    persona = crud_persona.get(db=db, id=persona_id)
    if not persona:
        raise HTTPException(
            status_code=404,
            detail=f"ID为 {persona_id} 的人设记录不存在"
        )
    return PersonaResponse.from_db(persona)


@router.get("/", response_model=PersonaListResponse)
def read_personas(
    *,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数限制")
) -> PersonaListResponse:
    """
    获取人设列表（分页）
    
    Args:
        db: 数据库会话
        skip: 跳过记录数
        limit: 返回记录数限制
        
    Returns:
        PersonaListResponse: 人设列表和总数
    """
    personas = crud_persona.get_multi(db=db, skip=skip, limit=limit)
    total = db.query(Persona).count()
    
    # 转换为PersonaResponse对象，确保包含author_nickname
    persona_responses = [PersonaResponse.from_db(persona) for persona in personas]
    
    return PersonaListResponse(
        items=persona_responses,
        total=total,
        skip=skip,
        limit=limit
    )


@router.put("/{persona_id}", response_model=PersonaResponse)
def update_persona(
    *,
    db: Session = Depends(get_db),
    persona_id: int,
    persona_in: PersonaUpdate
) -> PersonaResponse:
    """
    更新人设记录
    
    Args:
        db: 数据库会话
        persona_id: 人设ID
        persona_in: 更新数据
        
    Returns:
        PersonaResponse: 更新后的人设记录
        
    Raises:
        HTTPException: 记录不存在时抛出404错误
    """
    persona = crud_persona.get(db=db, id=persona_id)
    if not persona:
        raise HTTPException(
            status_code=404,
            detail=f"ID为 {persona_id} 的人设记录不存在"
        )
    
    # 如果更新名称，检查名称是否已存在
    if persona_in.name and persona_in.name != persona.name:
        existing = db.query(Persona).filter(
            Persona.name == persona_in.name,
            Persona.id != persona_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"人设名称 '{persona_in.name}' 已存在"
            )
    
    persona = crud_persona.update(db=db, db_obj=persona, obj_in=persona_in)
    return PersonaResponse.from_db(persona)


@router.delete("/{persona_id}", response_model=PersonaResponse)
def delete_persona(
    *,
    db: Session = Depends(get_db),
    persona_id: int
) -> PersonaResponse:
    """
    删除人设记录
    
    Args:
        db: 数据库会话
        persona_id: 人设ID
        
    Returns:
        PersonaResponse: 被删除的人设记录
        
    Raises:
        HTTPException: 记录不存在时抛出404错误
    """
    persona = crud_persona.get(db=db, id=persona_id)
    if not persona:
        raise HTTPException(
            status_code=404,
            detail=f"ID为 {persona_id} 的人设记录不存在"
        )
    
    persona = crud_persona.remove(db=db, id=persona_id)
    return PersonaResponse.from_db(persona)


@router.post("/search", response_model=PersonaListResponse)
def search_personas(
    *,
    db: Session = Depends(get_db),
    search_params: PersonaSearch
) -> PersonaListResponse:
    """
    搜索人设记录
    
    Args:
        db: 数据库会话
        search_params: 搜索参数
        
    Returns:
        PersonaListResponse: 搜索结果列表和总数
    """
    personas, total = crud_persona.search(db=db, search_params=search_params)
    
    # 转换为PersonaResponse对象，确保包含author_nickname
    persona_responses = [PersonaResponse.from_db(persona) for persona in personas]
    
    return PersonaListResponse(
        items=persona_responses,
        total=total,
        skip=search_params.skip,
        limit=search_params.limit
    )


@router.get("/author/{author_uuid}", response_model=PersonaListResponse)
def get_personas_by_author_uuid(
    *,
    db: Session = Depends(get_db),
    author_uuid: str,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数限制")
) -> PersonaListResponse:
    """
    根据作者UUID获取人设记录
    
    Args:
        db: 数据库会话
        author_uuid: 作者UUID
        skip: 跳过记录数
        limit: 返回记录数限制
        
    Returns:
        PersonaListResponse: 人设列表和总数
    """
    personas = crud_persona.get_by_author_uuid(
        db=db,
        author_uuid=author_uuid,
        skip=skip,
        limit=limit
    )
    
    # 计算总数
    total = db.query(Persona).filter(Persona.author_uuid == author_uuid).count()
    
    # 转换为PersonaResponse对象
    persona_responses = [PersonaResponse.from_db(p) for p in personas]
    
    return PersonaListResponse(
        items=persona_responses,
        total=total,
        skip=skip,
        limit=limit
    )


@router.post("/{persona_id}/view", response_model=PersonaResponse)
def increment_persona_view(
    *,
    db: Session = Depends(get_db),
    persona_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> PersonaResponse:
    """
    增加人设浏览量（仅当访问者不是作者时）
    
    Args:
        db: 数据库会话
        persona_id: 人设ID
        current_user: 当前用户（可选）
        
    Returns:
        PersonaResponse: 更新后的人设记录
        
    Raises:
        HTTPException: 记录不存在时抛出404错误
    """
    persona = crud_persona.get(db=db, id=persona_id)
    if not persona:
        raise HTTPException(
            status_code=404,
            detail=f"ID为 {persona_id} 的人设记录不存在"
        )
    
    # 检查是否是作者本人访问
    is_author = (
        current_user and 
        persona.author_uuid and 
        current_user.uuid == persona.author_uuid
    )
    
    if not is_author:
        # 仅当访问者不是作者时才增加浏览量
        persona.view_count = (persona.view_count or 0) + 1
        db.commit()
        db.refresh(persona)
        print(f"人设 ID {persona_id} 浏览量已增加至 {persona.view_count}")
    else:
        print(f"作者访问自己的人设 ID {persona_id}，不增加浏览量")
    
    return PersonaResponse.from_db(persona)


@router.get("/tags/{tags}", response_model=List[PersonaResponse])
def get_personas_by_tags(
    *,
    db: Session = Depends(get_db),
    tags: str,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数限制")
) -> List[PersonaResponse]:
    """
    根据标签获取人设记录
    
    Args:
        db: 数据库会话
        tags: 标签字符串（逗号分隔）
        skip: 跳过记录数
        limit: 返回记录数限制
        
    Returns:
        List[PersonaResponse]: 人设列表
    """
    personas = crud_persona.get_by_tags(
        db=db, 
        tags=tags, 
        skip=skip, 
        limit=limit
    )
    # 转换为PersonaResponse对象，确保包含author_nickname
    return [PersonaResponse.from_db(persona) for persona in personas]