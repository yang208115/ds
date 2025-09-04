"""
模块名称：tags.py
主要功能：标签相关的API路由端点
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.crud.persona import persona as crud_persona

# 创建路由
router = APIRouter()


@router.get("/", response_model=List[str])
def get_all_tags(
    *,
    db: Session = Depends(get_db)
) -> List[str]:
    """
    获取所有不重复的标签列表
    
    Args:
        db: 数据库会话
        
    Returns:
        List[str]: 标签列表（按字母排序）
    """
    return crud_persona.get_all_tags(db=db)


@router.get("/stats", response_model=dict)
def get_tag_stats(
    *,
    db: Session = Depends(get_db)
) -> dict:
    """
    获取标签统计信息
    
    Args:
        db: 数据库会话
        
    Returns:
        dict: 标签统计信息，包含标签使用次数
    """
    from sqlalchemy import func
    from app.db.models.persona import Persona
    
    # 获取所有记录的标签
    records = db.query(Persona.tags).filter(Persona.tags.isnot(None)).all()
    
    tag_counts = {}
    for tag_str in records:
        if tag_str[0]:
            tags = [t.strip() for t in tag_str[0].split(',') if t.strip()]
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    # 按使用次数排序
    sorted_tags = dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True))
    
    return {
        "total_tags": len(sorted_tags),
        "tag_counts": sorted_tags
    }