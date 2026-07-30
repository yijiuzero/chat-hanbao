"""
会话管理路由
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel, Field
from loguru import logger

from app.database import get_db
from app.models.session import ChatSession
from app.models.conversation import Message

router = APIRouter()


# ============ 请求/响应模型 ============

class CreateSessionRequest(BaseModel):
    user_id: Optional[str] = Field(None, description="用户ID")
    title: str = Field("新对话", max_length=255, description="会话标题")


class SessionResponse(BaseModel):
    id: str
    user_id: Optional[str]
    title: str
    message_count: int
    created_at: Optional[str]
    updated_at: Optional[str]


class SessionListResponse(BaseModel):
    sessions: list
    total: int


# ============ API 端点 ============

@router.post("/create", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest, db: AsyncSession = Depends(get_db)):
    """创建新会话"""
    session = ChatSession(
        id=str(uuid.uuid4()),
        user_id=request.user_id,
        title=request.title,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    logger.info(f"新会话已创建: {session.id}")
    return SessionResponse(
        id=session.id,
        user_id=session.user_id,
        title=session.title,
        message_count=session.message_count,
        created_at=session.created_at.isoformat() if session.created_at else None,
        updated_at=session.updated_at.isoformat() if session.updated_at else None,
    )


@router.get("/list", response_model=SessionListResponse)
async def list_sessions(
    user_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """获取会话列表"""
    query = select(ChatSession).order_by(desc(ChatSession.updated_at))
    if user_id:
        query = query.where(ChatSession.user_id == user_id)

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    sessions = result.scalars().all()

    return SessionListResponse(
        sessions=[
            {
                "id": s.id,
                "user_id": s.user_id,
                "title": s.title,
                "message_count": s.message_count,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            }
            for s in sessions
        ],
        total=len(sessions),
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """获取单个会话信息"""
    result = await db.execute(
        select(ChatSession).where(ChatSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    return SessionResponse(
        id=session.id,
        user_id=session.user_id,
        title=session.title,
        message_count=session.message_count,
        created_at=session.created_at.isoformat() if session.created_at else None,
        updated_at=session.updated_at.isoformat() if session.updated_at else None,
    )


@router.delete("/{session_id}")
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """删除会话及其所有消息"""
    result = await db.execute(
        select(ChatSession).where(ChatSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 删除关联消息
    messages_result = await db.execute(
        select(Message).where(Message.session_id == session_id)
    )
    messages = messages_result.scalars().all()
    for msg in messages:
        await db.delete(msg)

    await db.delete(session)
    await db.commit()

    logger.info(f"会话已删除: {session_id}")
    return {"detail": "会话已删除", "session_id": session_id}
