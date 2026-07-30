"""
聊天路由 - 核心对话 API
"""
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel, Field
from loguru import logger

from app.database import get_db
from app.models.conversation import Message
from app.models.session import ChatSession
from app.services.chat_manager import chat_manager

router = APIRouter()


# ============ 请求/响应模型 ============

class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="会话ID，不传则创建新会话")
    message: str = Field(..., min_length=1, max_length=2000, description="用户消息")


class ChatResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    intent: Optional[str] = None
    confidence: Optional[str] = None
    created_at: str


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: list


# ============ API 端点 ============

@router.post("/send", response_model=ChatResponse)
async def send_message(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    发送消息并获取回复
    - 如果未提供 session_id，自动创建新会话
    - 支持多轮对话上下文
    """
    # 1. 获取或创建会话
    session_id = request.session_id
    if not session_id:
        session_id = str(uuid.uuid4())
        new_session = ChatSession(id=session_id, title=request.message[:30])
        db.add(new_session)
        await db.commit()
        logger.info(f"创建新会话: {session_id}")

    # 2. 保存用户消息
    user_msg = Message(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role="user",
        content=request.message,
    )
    db.add(user_msg)

    # 3. 获取对话上下文
    context = await chat_manager.get_context(session_id)

    # 4. 处理消息
    result = await chat_manager.process_message(session_id, request.message, context)

    # 5. 保存助手回复
    assistant_msg = Message(
        id=result["id"],
        session_id=session_id,
        role="assistant",
        content=result["content"],
        intent=result["intent"],
        confidence=result["confidence"],
    )
    db.add(assistant_msg)

    # 6. 更新会话
    await db.execute(
        select(ChatSession).where(ChatSession.id == session_id)
    )
    session_result = await db.execute(
        select(ChatSession).where(ChatSession.id == session_id)
    )
    session = session_result.scalar_one_or_none()
    if session:
        session.message_count += 2
        session.updated_at = datetime.now()

    # 7. 更新上下文缓存
    await chat_manager.add_to_context(session_id, {"role": "user", "content": request.message})
    await chat_manager.add_to_context(session_id, {"role": "assistant", "content": result["content"], "intent": result["intent"]})

    await db.commit()

    return ChatResponse(
        id=result["id"],
        session_id=session_id,
        role="assistant",
        content=result["content"],
        intent=result["intent"],
        confidence=result["confidence"],
        created_at=result["created_at"],
    )


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_history(session_id: str, db: AsyncSession = Depends(get_db)):
    """获取会话历史消息"""
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
    )
    messages = result.scalars().all()

    return ChatHistoryResponse(
        session_id=session_id,
        messages=[
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "intent": m.intent,
                "confidence": m.confidence,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ],
    )


@router.delete("/history/{session_id}")
async def clear_history(session_id: str, db: AsyncSession = Depends(get_db)):
    """清除会话历史"""
    result = await db.execute(
        select(Message).where(Message.session_id == session_id)
    )
    messages = result.scalars().all()
    for msg in messages:
        await db.delete(msg)
    await db.commit()

    # 清除上下文缓存
    await chat_manager.clear_context(session_id)

    return {"detail": "历史记录已清除", "session_id": session_id}
