"""
包名称：models
功能说明：数据库模型包，包含所有数据表对应的SQLAlchemy模型
"""

from app.db.models.persona import Persona
from app.db.models.user import User

# 导出所有模型
__all__ = ["Persona", "User"]