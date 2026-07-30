"""
健康检查路由
"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter()


@router.get("/health")
async def health_check():
    """基础健康检查"""
    return {"status": "healthy", "service": "chat-hanbao"}


@router.get("/health/db")
async def db_health_check(db: AsyncSession = Depends(get_db)):
    """数据库健康检查"""
    try:
        result = await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}
