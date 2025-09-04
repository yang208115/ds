"""
模块名称：user.py
主要功能：定义用户数据库模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import CHAR, MEDIUMTEXT
from sqlalchemy.orm import relationship
from app.db.base import Base
import uuid


class User(Base):
    """用户数据库模型

    Attributes:
        id (int): 用户唯一标识。
        uuid (str): 用户UUID，全局唯一标识符。
        email (str): 用户邮箱，唯一。
        username (str): 用户名，唯一。
        hashed_password (str): 哈希密码，用于邮箱登录。
        github_id (str): GitHub 用户ID，唯一。
        github_username (str): GitHub 用户名。
        created_at (datetime): 创建时间。
        updated_at (datetime): 更新时间。
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(CHAR(36), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    nickname = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=True)
    github_id = Column(String(255), unique=True, index=True, nullable=True)
    github_username = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系定义
    personas = relationship("Persona", back_populates="author")
    avatar_rel = relationship("AuthorAvatar", back_populates="user", uselist=False, cascade="all, delete-orphan")


class AuthorAvatar(Base):
    """
    AuthorAvatar数据模型, 存储Base64编码的头像

    Attributes:
        id: 主键ID
        user_uuid: 用户UUID (外键)
        base64: Base64编码的头像字符串
    """
    __tablename__ = "author_avatars"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    user_uuid = Column(CHAR(36), ForeignKey("users.uuid"), unique=True, nullable=False, comment="用户UUID")
    base64 = Column(MEDIUMTEXT, nullable=False, comment="Base64编码的头像")

    user = relationship("User", back_populates="avatar_rel")

    def __repr__(self) -> str:
        return f"<AuthorAvatar(id={self.id}, user_uuid='{self.user_uuid}')>"
