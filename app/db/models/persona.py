"""
模块名称：persona.py
主要功能：Persona数据模型定义
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, func, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func as sql_func
from sqlalchemy.dialects.mysql import CHAR, MEDIUMTEXT
import uuid as uuid_lib
from app.db.base import Base


class Persona(Base):
    """
    Persona数据模型
    
    Attributes:
        id: 主键ID
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
        create_time: 创建时间
        update_time: 更新时间
    """
    
    __tablename__ = "personas"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    uuid = Column(CHAR(36), unique=True, nullable=False, default=lambda: str(uuid_lib.uuid4()), comment="人设UUID")
    view_count = Column(Integer, default=0, comment="浏览量")
    name = Column(String(255), nullable=False, comment="人设名称")
    title = Column(String(255), nullable=True, comment="人设标题")
    avatar = Column(Text, nullable=True, comment="头像URL")
    content = Column(Text, nullable=True, comment="人设内容")
    description = Column(Text, nullable=True, comment="人设描述")
    tags = Column(String(255), nullable=True, comment="标签列表，逗号分隔")
    ext_data = Column(JSON, nullable=True, comment="扩展数据（JSON格式）")
    author_uuid = Column(CHAR(36), ForeignKey('users.uuid'), nullable=False, comment="作者UUID")
    
    # 关系定义
    author = relationship("User", back_populates="personas")
    avatar_rel = relationship("PersonaAvatar", back_populates="persona", uselist=False, cascade="all, delete-orphan")
    create_time = Column(
        DateTime(timezone=True),
        server_default=sql_func.now(),
        comment="创建时间"
    )
    update_time = Column(
        DateTime(timezone=True),
        server_default=sql_func.now(),
        onupdate=sql_func.now(),
        comment="更新时间"
    )
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"<Persona(id={self.id}, name='{self.name}', author_uuid='{self.author_uuid}')>"
    
    def to_dict(self) -> dict:
        """
        转换为字典格式
        
        Returns:
            dict: 包含所有字段的字典
        """
        return {
            "id": self.id,
            "uuid": self.uuid,
            "view_count": self.view_count,
            "name": self.name,
            "title": self.title,
            "avatar": self.avatar_rel.base64 if self.avatar_rel else self.avatar,
            "content": self.content,
            "description": self.description,
            "tags": self.tags,
            "ext_data": self.ext_data,
            "author_uuid": self.author_uuid,
            "author_nickname": self.author.nickname if self.author else None,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "update_time": self.update_time.isoformat() if self.update_time else None
        }

class PersonaAvatar(Base):
    """
    PersonaAvatar数据模型, 存储Base64编码的头像

    Attributes:
        id: 主键ID
        persona_uuid: 人设UUID (外键)
        base64: Base64编码的头像字符串
    """
    __tablename__ = "persona_avatars"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    persona_uuid = Column(CHAR(36), ForeignKey("personas.uuid"), unique=True, nullable=False, comment="人设UUID")
    base64 = Column(MEDIUMTEXT, nullable=False, comment="Base64编码的头像")

    persona = relationship("Persona", back_populates="avatar_rel")

    def __repr__(self) -> str:
        return f"<PersonaAvatar(id={self.id}, persona_uuid='{self.persona_uuid}')>"

