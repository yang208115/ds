"""
模块名称：base.py
主要功能：数据库基础类，为所有模型提供基础
"""

from sqlalchemy.ext.declarative import declarative_base

# Import all the models here so that Base.metadata
# has them registered for Alembic autogenerate


# 创建基础类
Base = declarative_base()