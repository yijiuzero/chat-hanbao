"""
应用配置
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # 应用信息
    APP_NAME: str = "Chat Hanbao"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库
    DATABASE_URL: str = "postgresql+asyncpg://chatuser:chatpass@postgres:5432/chatdb"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    SESSION_TTL: int = 3600  # 会话过期时间（秒）

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # NLP 配置
    NLP_ENGINE: str = "rule"  # rule / llm_api
    LLM_API_URL: str = ""
    LLM_API_KEY: str = ""

    # 日志
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
