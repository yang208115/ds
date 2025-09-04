"""
模块名称：deps.py
主要功能：定义API依赖项，例如数据库会话和当前用户获取
"""

from typing import Generator, Optional

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.config import settings
from app.crud.user import user as crud_user
from app.schemas.user import User


# OAuth2 方案，用于从请求头中提取令牌
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def get_db() -> Generator:
    """获取数据库会话

    Yields:
        Session: 数据库会话。
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """获取当前认证用户

    Args:
        db (Session): 数据库会话。
        token (str): 认证令牌。

    Raises:
        HTTPException: 凭证无效或用户不存在。

    Returns:
        User: 当前用户对象。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud_user.get_by_email(db, email=user_email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_user_optional(
    db: Session = Depends(get_db),
    authorization: str = Header(None)
) -> Optional[User]:
    """获取可选的当前认证用户，允许匿名访问

    Args:
        db (Session): 数据库会话。
        authorization (str): 认证头，可选。

    Returns:
        Optional[User]: 当前用户对象或None（匿名访问）。
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_email: str = payload.get("sub")
        if user_email is None:
            return None
    except JWTError:
        return None
    
    user = crud_user.get_by_email(db, email=user_email)
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户

    Args:
        current_user (User): 当前认证用户。

    Raises:
        HTTPException: 用户不活跃。

    Returns:
        User: 当前活跃用户对象。
    """
    # 这里可以添加用户活跃状态的检查，例如用户是否被禁用
    # if not crud_user.is_active(current_user):
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user