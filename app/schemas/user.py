"""
模块名称：user.py
主要功能：定义用户相关的Pydantic模式
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模式

    Attributes:
        email (EmailStr): 用户邮箱。
        username (str): 用户名。
        nickname (Optional[str]): 用户昵称。
    """
    email: EmailStr
    username: str
    nickname: Optional[str] = None


class UserCreate(UserBase):
    """用户创建模式

    Attributes:
        password (str): 用户密码。
        username (str): 用户名。
        nickname (Optional[str]): 用户昵称。
        github_id (Optional[str]): GitHub 用户ID。
        github_username (Optional[str]): GitHub 用户名。
    """
    password: str
    username: str
    nickname: Optional[str] = None
    github_id: Optional[str] = None
    github_username: Optional[str] = None


class UserUpdate(UserBase):
    """用户更新模式

    Attributes:
        email (Optional[EmailStr]): 用户邮箱。
        username (Optional[str]): 用户名。
        nickname (Optional[str]): 用户昵称。
        password (Optional[str]): 用户密码。
        github_id (Optional[str]): GitHub 用户ID。
        github_username (Optional[str]): GitHub 用户名。
        avatar (Optional[str]): 用户头像 (Base64)。
    """
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    nickname: Optional[str] = None
    password: Optional[str] = None
    github_id: Optional[str] = None
    github_username: Optional[str] = None
    avatar: Optional[str] = None


class UserInDBBase(UserBase):
    """数据库中的用户基础模式

    Attributes:
        id (int): 用户ID。
        uuid (str): 用户UUID。
        username (str): 用户名。
        nickname (Optional[str]): 用户昵称。
        github_id (Optional[str]): GitHub 用户ID。
        github_username (Optional[str]): GitHub 用户名。
        created_at (datetime): 创建时间。
        updated_at (Optional[datetime]): 更新时间。
        avatar (Optional[str]): 用户头像 (Base64)。
    """
    id: int
    uuid: str
    username: str
    nickname: Optional[str] = None
    github_id: Optional[str] = None
    github_username: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class User(UserInDBBase):
    """用户响应模式
    """
    pass


class UserInDB(UserInDBBase):
    """数据库中的用户模式（包含哈希密码）

    Attributes:
        hashed_password (str): 哈希密码。
    """
    hashed_password: str


class Token(BaseModel):
    """认证令牌模式

    Attributes:
        access_token (str): 访问令牌。
        token_type (str): 令牌类型。
    """
    access_token: str
    token_type: str