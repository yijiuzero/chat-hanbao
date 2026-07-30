"""
消息模型
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True)
    role = Column(String(20), nullable=False)  # user / assistant / system
    content = Column(Text, nullable=False)
    intent = Column(String(50), nullable=True)  # 意图分类
    confidence = Column(String(10), nullable=True)  # 置信度
    created_at = Column(DateTime(timezone=True), server_default=func.now())
