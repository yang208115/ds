"""
模块名称：security.py
主要功能：提供密码哈希、JWT生成与验证等安全相关功能
"""

from datetime import datetime, timedelta
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any],
    expires_delta: timedelta = None
) -> str:
    """创建访问令牌

    Args:
        subject (Union[str, Any]): 令牌的主题，通常是用户ID。
        expires_delta (timedelta, optional): 令牌过期时间。默认为None。

    Returns:
        str: 生成的访问令牌。
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码

    Args:
        plain_password (str): 明文密码。
        hashed_password (str): 哈希密码。

    Returns:
        bool: 密码是否匹配。
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希

    Args:
        password (str): 明文密码。

    Returns:
        str: 密码的哈希值。
    """
    return pwd_context.hash(password)