"""
包名称：crud
功能说明：数据库CRUD操作包，提供对数据表的基本操作
"""

from app.crud.persona import persona
from app.crud.user import user

__all__ = ["persona", "user"]