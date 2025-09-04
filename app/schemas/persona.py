"""
模块名称：persona.py
主要功能：Persona相关的Pydantic模式定义，用于数据验证和序列化
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator


class PersonaBase(BaseModel):
    """
    Persona基础模式
    
    Attributes:
        uuid: 人设UUID
        view_count: 浏览量
        name: 人设名称
        title: 人设标题
        avatar: 头像URL
        content: 人设内容
        description: 人设描述
        tags: 标签列表（逗号分隔）
        ext_data: 扩展数据（JSON格式）
        author: 作者
    """
    
    uuid: Optional[str] = Field(None, max_length=36, description="人设UUID")
    view_count: int = Field(0, ge=0, description="浏览量")
    name: str = Field(..., min_length=1, max_length=255, description="人设名称")
    title: str = Field(..., min_length=1, max_length=255, description="人设标题")
    avatar: Optional[str] = Field(None, description="头像 (Base64或URL)")
    content: Optional[str] = Field(None, description="人设内容")
    description: Optional[str] = Field(None, description="人设描述")
    tags: Optional[str] = Field(None, max_length=255, description="标签列表，逗号分隔")
    ext_data: Optional[dict] = Field(None, description="扩展数据（JSON格式）")
    author_uuid: Optional[str] = Field(None, max_length=36, description="作者UUID")
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        """验证名称不能为空"""
        if not v or not v.strip():
            raise ValueError('人设名称不能为空')
        return v.strip()
    
    @validator('content')
    def content_must_not_be_empty(cls, v):
        """验证内容不能为空"""
        if not v or not v.strip():
            raise ValueError('人设内容不能为空')
        return v.strip()
    
    @validator('tags')
    def format_tags(cls, v):
        """格式化标签"""
        if v:
            # 移除多余空格，确保逗号分隔
            tags = [tag.strip() for tag in v.split(',') if tag.strip()]
            return ','.join(tags) if tags else None
        return None


class PersonaCreate(PersonaBase):
    """创建Persona时的请求模式"""
    pass


class PersonaUpdate(BaseModel):
    """
    更新Persona时的请求模式
    
    所有字段都是可选的，允许部分更新
    """
    
    uuid: Optional[str] = Field(None, max_length=36, description="人设UUID")
    view_count: Optional[int] = Field(None, ge=0, description="浏览量")
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="人设名称")
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="人设标题")
    avatar: Optional[str] = Field(None, description="头像 (Base64或URL)")
    content: Optional[str] = Field(None, description="人设内容")
    description: Optional[str] = Field(None, description="人设描述")
    tags: Optional[str] = Field(None, max_length=255, description="标签列表，逗号分隔")
    ext_data: Optional[dict] = Field(None, description="扩展数据（JSON格式）")
    author_uuid: Optional[str] = Field(None, max_length=36, description="作者UUID")
    
    @validator('name')
    def name_must_not_be_empty_if_provided(cls, v):
        """如果提供名称，验证不能为空"""
        if v is not None and not v.strip():
            raise ValueError('人设名称不能为空')
        return v.strip() if v else None
    
    @validator('content')
    def content_must_not_be_empty_if_provided(cls, v):
        """如果提供内容，验证不能为空"""
        if v is not None and not v.strip():
            raise ValueError('人设内容不能为空')
        return v.strip() if v else None
    
    @validator('tags')
    def format_tags(cls, v):
        """格式化标签"""
        if v:
            tags = [tag.strip() for tag in v.split(',') if tag.strip()]
            return ','.join(tags) if tags else None
        return None


class PersonaInDB(PersonaBase):
    """
    数据库中的Persona模式
    
    Attributes:
        id: 主键ID
        author_nickname: 作者昵称（从关联的User获取）
        author_username: 作者用户名（从关联的User获取）
        create_time: 创建时间
        update_time: 更新时间
    """
    
    id: int = Field(..., description="主键ID")
    author_nickname: Optional[str] = Field(None, description="作者昵称")
    author_username: Optional[str] = Field(None, description="作者用户名")
    create_time: datetime = Field(..., description="创建时间")
    update_time: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        """Pydantic配置"""
        from_attributes = True
        
    @classmethod
    def from_db(cls, persona_obj):
        """从数据库对象创建实例"""
        data = {
            'id': persona_obj.id,
            'uuid': persona_obj.uuid,
            'view_count': persona_obj.view_count,
            'name': persona_obj.name,
            'title': persona_obj.title,
            'avatar': persona_obj.avatar_rel.base64 if persona_obj.avatar_rel else persona_obj.avatar,
            'content': persona_obj.content,
            'description': persona_obj.description,
            'tags': persona_obj.tags,
            'ext_data': persona_obj.ext_data,
            'author_uuid': persona_obj.author_uuid,
            'author_nickname': persona_obj.author.nickname if persona_obj.author else None,
            'author_username': persona_obj.author.username if persona_obj.author else None,
            'create_time': persona_obj.create_time,
            'update_time': persona_obj.update_time
        }
        return cls(**data)


class PersonaResponse(PersonaInDB):
    """API响应的Persona模式"""
    pass


class PersonaSearch(BaseModel):
    """
    搜索Persona时的请求模式
    
    Attributes:
        keyword: 搜索关键词（名称、描述、内容）
        tags: 标签筛选
        author_uuid: 作者UUID筛选
        skip: 分页偏移量
        limit: 分页限制
    """
    
    keyword: Optional[str] = Field(None, description="搜索关键词")
    tags: Optional[str] = Field(None, description="标签筛选，逗号分隔")
    author_uuid: Optional[str] = Field(None, description="作者UUID筛选")
    skip: int = Field(0, ge=0, description="分页偏移量")
    limit: int = Field(10, ge=1, le=100, description="分页限制，最大100")


class PersonaListResponse(BaseModel):
    """
    Persona列表响应模式
    
    Attributes:
        items: Persona列表
        total: 总记录数
        skip: 当前偏移量
        limit: 当前限制数
    """
    
    items: list[PersonaResponse] = Field(..., description="Persona列表")
    total: int = Field(..., description="总记录数")
    skip: int = Field(..., description="当前偏移量")
    limit: int = Field(..., description="当前限制数")