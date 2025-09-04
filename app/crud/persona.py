"""
模块名称：persona.py
主要功能：Persona的CRUD操作实现
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from app.db.models.persona import Persona, PersonaAvatar
from app.db.models.user import User
from app.schemas.persona import PersonaCreate, PersonaUpdate, PersonaSearch


class CRUDPersona:
    """
    Persona的CRUD操作类
    
    提供对Persona数据表的基本操作：创建、读取、更新、删除
    """
    
    def create(self, db: Session, *, obj_in: PersonaCreate) -> Persona:
        """
        创建新的人设记录
        
        Args:
            db: 数据库会话
            obj_in: 创建数据
            
        Returns:
            Persona: 创建的记录对象
        """
        import re
        obj_in_data = obj_in.model_dump(exclude_unset=True)
        avatar_str = obj_in_data.pop('avatar', None)

        # 创建 Persona 对象，但不包括 avatar
        db_obj = Persona(**obj_in_data)

        # 如果 avatar 是 URL，则直接赋值
        if avatar_str and re.match(r'^https?://', avatar_str):
            db_obj.avatar = avatar_str
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # 如果 avatar 是 base64，则创建 PersonaAvatar 记录
        if avatar_str and not re.match(r'^https?://', avatar_str):
            avatar = PersonaAvatar(persona_uuid=db_obj.uuid, base64=avatar_str)
            db.add(avatar)
            db.commit()
            db.refresh(db_obj)
            
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Persona]:
        """
        根据ID获取人设记录
        
        Args:
            db: 数据库会话
            id: 记录ID
            
        Returns:
            Optional[Persona]: 记录对象或None
        """
        return db.query(Persona).options(joinedload(Persona.author)).filter(Persona.id == id).first()
    
    def get_multi(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Persona]:
        """
        获取多个人设记录（分页）
        
        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 限制记录数
            
        Returns:
            List[Persona]: 记录列表
        """
        return db.query(Persona).options(joinedload(Persona.author)).offset(skip).limit(limit).all()
    
    def search(
        self,
        db: Session,
        *,
        search_params: PersonaSearch
    ) -> tuple[List[Persona], int]:
        """
        搜索人设记录
        
        Args:
            db: 数据库会话
            search_params: 搜索参数
            
        Returns:
            tuple[List[Persona], int]: 记录列表和总数
        """
        query = db.query(Persona)
        
        # 关键词搜索
        if search_params.keyword:
            keyword_filter = f"%{search_params.keyword}%"
            query = query.filter(
                or_(
                    Persona.name.like(keyword_filter),
                    Persona.description.like(keyword_filter),
                    Persona.content.like(keyword_filter)
                )
            )
        
        # 标签筛选
        if search_params.tags:
            tags = [tag.strip() for tag in search_params.tags.split(',') if tag.strip()]
            for tag in tags:
                query = query.filter(Persona.tags.like(f"%{tag}%"))
        
        # 作者筛选
        if search_params.author_uuid:
            query = query.filter(Persona.author_uuid == search_params.author_uuid)
        
        # 添加作者信息关联
        query = query.options(joinedload(Persona.author))
        
        # 计算总数
        total = query.count()
        
        # 分页
        records = query.offset(search_params.skip).limit(search_params.limit).all()
        
        return records, total
    
    def get_by_author_uuid(
        self, 
        db: Session, 
        *, 
        author_uuid: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Persona]:
        """
        根据作者UUID获取人设记录
        
        Args:
            db: 数据库会话
            author_uuid: 作者UUID
            skip: 跳过记录数
            limit: 限制记录数
            
        Returns:
            List[Persona]: 记录列表
        """
        return db.query(Persona).options(joinedload(Persona.author)).filter(
            Persona.author_uuid == author_uuid
        ).offset(skip).limit(limit).all()
    
    def get_by_tags(
        self, 
        db: Session, 
        *, 
        tags: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Persona]:
        """
        根据标签获取人设记录
        
        Args:
            db: 数据库会话
            tags: 标签字符串（逗号分隔）
            skip: 跳过记录数
            limit: 限制记录数
            
        Returns:
            List[Persona]: 记录列表
        """
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        query = db.query(Persona)
        
        for tag in tag_list:
            query = query.filter(Persona.tags.like(f"%{tag}%"))
        
        return query.options(joinedload(Persona.author)).offset(skip).limit(limit).all()
    
    def update(
        self,
        db: Session,
        *,
        db_obj: Persona,
        obj_in: PersonaUpdate
    ) -> Persona:
        """
        更新人设记录
        
        Args:
            db: 数据库会话
            db_obj: 数据库中的记录对象
            obj_in: 更新数据
            
        Returns:
            Persona: 更新后的记录对象
        """
        import re
        update_data = obj_in.model_dump(exclude_unset=True)

        if 'avatar' in update_data:
            avatar_str = update_data.pop('avatar')
            
            # 如果是 base64 编码
            if avatar_str and not re.match(r'^https?://', avatar_str):
                db_obj.avatar = None  # 清空旧的 URL
                if db_obj.avatar_rel:
                    db_obj.avatar_rel.base64 = avatar_str
                else:
                    new_avatar = PersonaAvatar(persona_uuid=db_obj.uuid, base64=avatar_str)
                    db.add(new_avatar)
            # 如果是 URL
            else:
                db_obj.avatar = avatar_str
                # 如果存在旧的 base64 头像，则删除
                if db_obj.avatar_rel:
                    db.delete(db_obj.avatar_rel)

        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, *, id: int) -> Optional[Persona]:
        """
        删除人设记录
        
        Args:
            db: 数据库会话
            id: 记录ID
            
        Returns:
            Optional[Persona]: 被删除的记录对象或None
        """
        obj = db.query(Persona).filter(Persona.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj
    
    def get_authors(self, db: Session) -> List[dict]:
        """
        获取所有不重复的作者列表（包含UUID和昵称）
        
        Args:
            db: 数据库会话
            
        Returns:
            List[dict]: 作者列表，包含uuid和nickname
        """
        authors = db.query(Persona.author_uuid, User.nickname).join(
            User, Persona.author_uuid == User.uuid
        ).filter(
            Persona.author_uuid.isnot(None)
        ).distinct().all()
        return [{'uuid': author[0], 'nickname': author[1]} for author in authors if author[0]]
    
    def get_all_tags(self, db: Session) -> List[str]:
        """
        获取所有不重复的标签列表
        
        Args:
            db: 数据库会话
            
        Returns:
            List[str]: 标签列表
        """
        tags = db.query(Persona.tags).filter(
            Persona.tags.isnot(None)
        ).all()
        
        all_tags = set()
        for tag_str in tags:
            if tag_str[0]:
                tag_list = [t.strip() for t in tag_str[0].split(',') if t.strip()]
                all_tags.update(tag_list)
        
        return sorted(list(all_tags))


# 创建全局CRUD实例
persona = CRUDPersona()