"""
模块名称：main.py
主要功能：FastAPI应用入口文件，负责应用的初始化和配置
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.db.session import engine
from app.db.base import Base
from app.api.endpoints import personas, tags, authors, auth
from app.core.config import settings

# 加载环境变量
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    Args:
        app: FastAPI应用实例
    
    Yields:
        None
    """
    # 启动时创建数据库表
    Base.metadata.create_all(bind=engine)
    yield
    # 关闭时的清理操作


# 创建FastAPI应用实例
app = FastAPI(
    title="DreamShell API",
    description="人设市场管理系统后端API",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(personas.router, prefix="/api/personas", tags=["personas"])
app.include_router(tags.router, prefix="/api/tags", tags=["tags"])
app.include_router(authors.router, prefix="/api/authors", tags=["authors"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])


@app.get("/")
async def root():
    """
    根路由
    
    Returns:
        dict: 欢迎信息
    """
    return {
        "message": "欢迎使用DreamShell API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """
    健康检查接口
    
    Returns:
        dict: 健康状态信息
    """
    return {"status": "healthy", "service": "DreamShell API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )