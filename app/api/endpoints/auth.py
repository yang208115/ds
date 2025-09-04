"""
模块名称：auth.py
主要功能：提供用户认证相关的API端点，包括邮箱登录/注册和GitHub OAuth认证
"""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from requests_oauthlib import OAuth2Session
import os
import jose.jwt as jwt
from jose import JWTError

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.crud.user import user as crud_user
from app.db.session import get_db
from app.schemas.user import UserCreate, User, Token, UserUpdate
from pydantic import BaseModel


class TokenData(BaseModel):
    username: str = None

router = APIRouter()


# 依赖项：获取当前用户
async def get_current_user(db: Session = Depends(get_db), token: str = Depends(OAuth2PasswordBearer(tokenUrl="token"))):
    """获取当前认证用户

    Args:
        db (Session): 数据库会话。
        token (str): 认证令牌。

    Raises:
        HTTPException: 凭证无效或用户不存在。

    Returns:
        User: 当前用户对象。
    """
    print("Token received:", token)  # 调试输出
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud_user.get_by_email(db, email=username)
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=User)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate
) -> Any:
    """注册新用户

    Args:
        db (Session): 数据库会话。
        user_in (UserCreate): 用户创建模式。

    Raises:
        HTTPException: 邮箱已注册。

    Returns:
        Any: 新创建的用户对象。
    """
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud_user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    user = crud_user.create(db, obj_in=user_in)
    return user


@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """用户登录并获取访问令牌

    Args:
        db (Session): 数据库会话。
        form_data (OAuth2PasswordRequestForm): OAuth2密码请求表单。

    Raises:
        HTTPException: 邮箱或密码不正确。

    Returns:
        Any: 访问令牌。
    """
    user = crud_user.get_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {"access_token": create_access_token(user.email, expires_delta=access_token_expires), "token_type": "bearer"}


@router.get("/github/login")
def github_login():
    """重定向到GitHub OAuth授权页面
    """
    github = OAuth2Session(settings.GITHUB_CLIENT_ID, redirect_uri=settings.GITHUB_REDIRECT_URI)
    authorization_url, state = github.authorization_url("https://github.com/login/oauth/authorize")
    return Response(headers={"Location": authorization_url}, status_code=status.HTTP_302_FOUND)


@router.get("/github/callback", response_model=Token)
def github_callback(
    code: str,
    db: Session = Depends(get_db)
) -> Any:
    """GitHub OAuth回调，处理授权码并完成登录/注册

    Args:
        code (str): GitHub授权码。
        db (Session): 数据库会话。

    Raises:
        HTTPException: 无法获取GitHub访问令牌或用户信息。

    Returns:
        Any: 访问令牌。
    """
    github = OAuth2Session(settings.GITHUB_CLIENT_ID, redirect_uri=settings.GITHUB_REDIRECT_URI)
    try:
        token = github.fetch_token(
            "https://github.com/login/oauth/access_token",
            client_secret=settings.GITHUB_CLIENT_SECRET,
            code=code
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Could not get GitHub access token: {e}")

    github_user_response = github.get("https://api.github.com/user")
    if github_user_response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not get GitHub user info")

    github_user_data = github_user_response.json()
    github_id = str(github_user_data["id"])
    github_username = github_user_data["login"]
    email = github_user_data.get("email", f"{github_username}@github.com") # GitHub可能不返回email

    user = crud_user.get_by_github_id(db, github_id=github_id)
    if not user:
        # 如果用户不存在，则创建新用户
        user_in = UserCreate(
            email=email,
            username=github_username, # 使用github_username作为用户名
            password=os.urandom(16).hex(), # 随机生成密码，因为GitHub登录不需要密码
            github_id=github_id,
            github_username=github_username
        )
        user = crud_user.create(db, obj_in=user_in)
    else:
        # 如果用户存在，更新其信息（例如邮箱可能在GitHub上更新了）
        user_update_data = {"email": email, "github_username": github_username}
        user = crud_user.update(db, db_obj=user, obj_in=user_update_data)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {"access_token": create_access_token(user.email, expires_delta=access_token_expires), "token_type": "bearer"}


@router.get("/me", response_model=User)
def read_users_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    """获取当前用户信息

    Args:
        current_user (User): 当前认证用户。

    Returns:
        Any: 当前用户对象。
    """
    return current_user

@router.put("/profile", response_model=User)
def update_user_profile(
    *,
    db: Session = Depends(get_db),
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """更新当前用户个人信息

    Args:
        db (Session): 数据库会话。
        user_update (UserUpdate): 用户更新数据。
        current_user (User): 当前认证用户。

    Raises:
        HTTPException: 邮箱或用户名已存在。

    Returns:
        Any: 更新后的用户对象。
    """
    # 检查邮箱是否已被其他用户使用
    if user_update.email and user_update.email != current_user.email:
        existing_user = crud_user.get_by_email(db, email=user_update.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # 检查用户名是否已被其他用户使用
    if user_update.username and user_update.username != current_user.username:
        existing_user = crud_user.get_by_username(db, username=user_update.username)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Username already registered")
    
    # 更新用户信息
    user = crud_user.update(db, db_obj=current_user, obj_in=user_update)
    return user