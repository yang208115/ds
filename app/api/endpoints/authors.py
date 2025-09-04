"""
模块名称：authors.py
主要功能：作者相关的API路由端点
"""

from typing import List, Dict
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.crud.persona import persona as crud_persona
from app.crud.user import user as crud_user

# 创建路由
router = APIRouter()


@router.get("/", response_model=List[Dict[str, str]])
def get_all_authors(
    *,
    db: Session = Depends(get_db)
) -> List[Dict[str, str]]:
    """
    获取所有不重复的作者列表（包含UUID和昵称）
    
    Args:
        db: 数据库会话
        
    Returns:
        List[Dict[str, str]]: 作者列表，包含uuid和nickname
    """
    return crud_persona.get_authors(db=db)


@router.get("/stats", response_model=Dict[str, Dict[str, str]])
def get_author_stats(
    *,
    db: Session = Depends(get_db)
) -> Dict[str, Dict[str, str]]:
    """
    获取作者统计信息
    
    Args:
        db: 数据库会话
        
    Returns:
        Dict[str, Dict[str, str]]: 作者统计信息，包含每个作者的人设数量和昵称
    """
    from sqlalchemy import func
    from app.db.models.persona import Persona
    from app.db.models.user import User
    
    # 获取每个作者的人设数量
    stats = db.query(
        Persona.author_uuid,
        User.nickname,
        func.count(Persona.id).label('count')
    ).join(
        User, Persona.author_uuid == User.uuid
    ).filter(
        Persona.author_uuid.isnot(None)
    ).group_by(
        Persona.author_uuid, User.nickname
    ).all()
    
    # 转换为字典格式
    author_stats = {
        author_uuid: {
            'nickname': nickname or 'Unknown',
            'count': str(count)
        }
        for author_uuid, nickname, count in stats if author_uuid
    }
    
    return author_stats

@router.get("/avatar/{user_uuid}", response_model=str)
def get_user_avatar(
    *,
    db: Session = Depends(get_db),
    user_uuid: str
) -> str:
    """获取用户的头像

    Args:
        db: 数据库会话
        user_uuid: 用户UUID

    Returns:
        str: 头像的Base64编码

    Raises:
        HTTPException: 头像不存在
    """
    avatar = crud_user.get_avatar(db, user_uuid=user_uuid)
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    return avatar

@router.get("/top", response_model=List[Dict[str, str]])
def get_top_authors(
    *,
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50, description="返回作者数量限制")
) -> List[Dict[str, str]]:
    """
    获取创作数量最多的作者列表
    
    Args:
        db: 数据库会话
        limit: 返回作者数量限制
        
    Returns:
        List[Dict[str, str]]: 作者列表，包含uuid、nickname和人设数量
    """
    from sqlalchemy import func
    from app.db.models.persona import Persona
    from app.db.models.user import User
    
    # 获取每个作者的人设数量并排序
    stats = db.query(
        Persona.author_uuid,
        User.nickname,
        func.count(Persona.id).label('count')
    ).join(
        User, Persona.author_uuid == User.uuid
    ).filter(
        Persona.author_uuid.isnot(None)
    ).group_by(
        Persona.author_uuid, User.nickname
    ).order_by(
        func.count(Persona.id).desc()
    ).limit(limit).all()
    
    # 转换为字典格式
    result = [
        {
            "uuid": author_uuid,
            "nickname": nickname or 'Unknown',
            "count": str(count)
        }
        for author_uuid, nickname, count in stats
    ]
    
    return result


@router.get("/user/{user_uuid}", response_model=Dict[str, str])
def get_user_by_uuid(
    *,
    db: Session = Depends(get_db),
    user_uuid: str
) -> Dict[str, str]:
    """
    根据UUID获取用户信息
    
    Args:
        db: 数据库会话
        user_uuid: 用户UUID
        
    Returns:
        Dict[str, str]: 用户信息，包含uuid、username和nickname
        
    Raises:
        HTTPException: 用户不存在时抛出404错误
    """
    user = crud_user.get_by_uuid(db=db, uuid=user_uuid)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"UUID为 {user_uuid} 的用户不存在"
        )
    
    return {
        "uuid": user.uuid,
        "username": user.username,
        "nickname": user.nickname or user.username
    }