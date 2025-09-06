"""
模块名称：user.py
主要功能：提供用户相关的CRUD操作
"""

from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.db.models.user import User, AuthorAvatar
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


class CRUDUser:
    """用户CRUD操作类
    """
    def get_avatar(self, db: Session, user_uuid: str) -> str | None:
        """获取用户的头像的Base64编码

        Args:
            db: 数据库会话
            user_uuid: 用户UUID

        Returns:
            str | None: 头像的Base64编码或None
        """
        avatar_obj = db.query(AuthorAvatar).filter(AuthorAvatar.user_uuid == user_uuid).first()
        return avatar_obj.base64 if avatar_obj else None
    
    def get_by_email(self, db: Session, email: str) -> User | None:
        """根据邮箱获取用户

        Args:
            db (Session): 数据库会话。
            email (str): 用户邮箱。

        Returns:
            User | None: 用户对象或None。
        """
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, username: str) -> User | None:
        """根据用户名获取用户

        Args:
            db (Session): 数据库会话。
            username (str): 用户名。

        Returns:
            User | None: 用户对象或None。
        """
        return db.query(User).filter(User.username == username).first()

    def get_by_github_id(self, db: Session, github_id: str) -> User | None:
        """根据GitHub ID获取用户

        Args:
            db (Session): 数据库会话。
            github_id (str): GitHub 用户ID。

        Returns:
            User | None: 用户对象或None。
        """
        return db.query(User).filter(User.github_id == github_id).first()
    
    def get_by_github_id_or_username(self, db: Session, *, github_id: str, username: str) -> User | None:
        """根据 GitHub ID 或用户名获取用户

        优先匹配 GitHub ID；若 GitHub ID 不存在，再匹配用户名。

        Args:
            db (Session): 数据库会话。
            github_id (str): GitHub 用户 ID。
            username (str): 用户名。

        Returns:
            User | None: 用户对象或 None。
        """
        return (
            db.query(User)
            .filter(
                or_(
                    User.github_id == github_id,          # 主匹配
                    User.username == username             # 后备匹配
                )
            )
            .first()
        )

    def get_by_uuid(self, db: Session, uuid: str) -> User | None:
        """根据UUID获取用户

        Args:
            db (Session): 数据库会话。
            uuid (str): 用户UUID。

        Returns:
            User | None: 用户对象或None。
        """
        return db.query(User).filter(User.uuid == uuid).first()

    def create(self, db: Session, obj_in: UserCreate) -> User:
        """创建新用户

        Args:
            db (Session): 数据库会话。
            obj_in (UserCreate): 用户创建模式。

        Returns:
            User: 新创建的用户对象。
        """
        hashed_password = get_password_hash(obj_in.password) if obj_in.password else None
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            nickname=obj_in.nickname,
            hashed_password=hashed_password,
            github_id=obj_in.github_id,
            github_username=obj_in.github_username,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: User, obj_in: UserUpdate) -> User:
        """更新用户

        Args:
            db (Session): 数据库会话。
            db_obj (User): 数据库中的用户对象。
            obj_in (UserUpdate): 用户更新模式。

        Returns:
            User: 更新后的用户对象。
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = get_password_hash(update_data["password"])
            del update_data["password"]

        if "avatar" in update_data:
            avatar_base64 = update_data.pop("avatar")
            if avatar_base64:
                # 查找或创建头像记录
                avatar_obj = db.query(AuthorAvatar).filter(AuthorAvatar.user_uuid == db_obj.uuid).first()
                if not avatar_obj:
                    avatar_obj = AuthorAvatar(user_uuid=db_obj.uuid, base64=avatar_base64)
                    db.add(avatar_obj)
                else:
                    avatar_obj.base64 = avatar_base64



        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


user = CRUDUser()