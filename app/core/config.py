"""
模块名称：config.py
主要功能：应用配置管理，使用Pydantic的BaseSettings进行配置管理
"""

from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator
import json
import os


class Settings(BaseSettings):
    """
    应用配置类
    
    Attributes:
        DATABASE_URL: 数据库连接字符串
        SECRET_KEY: 应用密钥
        DEBUG: 调试模式开关
        CORS_ORIGINS: 允许的CORS源列表
        HOST: 服务器主机地址
        PORT: 服务器端口
        LOG_LEVEL: 日志级别
    """
    
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://NAP:Lyf652717@8.134.161.25:3306/nap"
    
    # 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 100))
    
    # GitHub OAuth配置
    GITHUB_CLIENT_ID: str = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET: str = os.getenv("GITHUB_CLIENT_SECRET", "")
    GITHUB_REDIRECT_URI: str = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8000/api/v1/auth/github/callback")
    
    # 应用配置
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # CORS配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000"
    ]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    class Config:
        """配置类设置"""
        env_file = ".env"
        case_sensitive = True
    
    @field_validator("CORS_ORIGINS", mode='before')
    def parse_cors_origins(cls, v):
        """
        解析CORS_ORIGINS配置
        
        Args:
            v: 原始配置值
            
        Returns:
            List[str]: 解析后的CORS源列表
        """
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [item.strip() for item in v.split(",")]
        return v
    
    @field_validator("DATABASE_URL")
    def validate_database_url(cls, v):
        """
        验证数据库连接字符串格式
        
        Args:
            v: 数据库连接字符串
            
        Returns:
            str: 验证通过的数据库连接字符串
        """
        if not v.startswith(("mysql+pymysql://", "sqlite:///", "postgresql://")):
            raise ValueError("不支持的数据库类型")
        return v


# 创建全局配置实例
settings = Settings()