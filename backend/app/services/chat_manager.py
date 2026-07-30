"""
对话管理器 - 处理多轮对话上下文
"""
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from loguru import logger

from app.services.nlu_engine import nlu_engine


class ChatManager:
    """对话管理器 - 管理会话状态和上下文"""

    def __init__(self, redis_client=None):
        self.redis = redis_client
        # 内存缓存（Redis 不可用时的 fallback）
        self._context_cache: Dict[str, List[Dict]] = {}

    async def process_message(
        self, session_id: str, user_message: str, context: List[Dict] = None
    ) -> Dict:
        """
        处理用户消息并生成回复
        """
        # 1. NLU 理解
        nlu_result = await nlu_engine.understand(user_message)
        intent = nlu_result["intent"]
        confidence = nlu_result["confidence"]

        # 2. 生成回复
        reply = await self._generate_response(
            session_id, user_message, intent, confidence, context
        )

        # 3. 构建响应
        result = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "role": "assistant",
            "content": reply,
            "intent": intent,
            "confidence": str(confidence),
            "created_at": datetime.now().isoformat(),
        }

        logger.info(f"对话处理完成 | session={session_id} | intent={intent}")
        return result

    async def _generate_response(
        self, session_id: str, message: str, intent: str, confidence: float, context: List[Dict]
    ) -> str:
        """
        生成回复 - 基于意图和上下文
        可扩展为调用 LLM API
        """
        # 高置信度：直接使用规则回复
        if confidence >= 0.8:
            return nlu_engine.get_response(intent)

        # 中置信度：结合上下文回复
        if confidence >= 0.5:
            # 检查是否有上下文
            if context and len(context) > 0:
                last_topic = context[-1].get("intent", "")
                if last_topic == intent:
                    return f"你似乎对「{intent}」很感兴趣！能告诉我更多吗？{nlu_engine.get_response(intent)}"
            return nlu_engine.get_response(intent) or self._smart_reply(message, context)

        # 低置信度：智能兜底
        return self._smart_reply(message, context)

    def _smart_reply(self, message: str, context: List[Dict] = None) -> str:
        """智能兜底回复"""
        if "?" in message or "？" in message or "吗" in message:
            return "这是个好问题！让我想想... 🤔 目前我还在学习中，不过我会尽力帮你解答的！"
        
        if len(message) > 100:
            return "你说得很详细！我理解你想要表达更多内容。能总结一下重点吗？这样我能更好地帮助你 📝"
        
        fallbacks = [
            "嗯嗯，我在听！能再详细说说吗？😊",
            "有意思！继续说~",
            "我明白了，还有别的想聊的吗？",
            "收到！有什么具体的方面想深入了解的吗？",
        ]
        import random
        return random.choice(fallbacks)

    async def get_context(self, session_id: str, limit: int = 10) -> List[Dict]:
        """获取会话上下文"""
        # 先尝试 Redis
        if self.redis:
            try:
                key = f"chat:context:{session_id}"
                data = await self.redis.lrange(key, 0, limit - 1)
                if data:
                    return [json.loads(d) for d in data]
            except Exception as e:
                logger.warning(f"Redis 读取失败: {e}")

        # Fallback 到内存
        return self._context_cache.get(session_id, [])[-limit:]

    async def add_to_context(self, session_id: str, message: Dict, max_history: int = 20):
        """添加消息到上下文"""
        # 尝试 Redis
        if self.redis:
            try:
                key = f"chat:context:{session_id}"
                await self.redis.rpush(key, json.dumps(message, ensure_ascii=False))
                await self.redis.ltrim(key, -max_history, -1)
                await self.redis.expire(key, 3600)
                return
            except Exception as e:
                logger.warning(f"Redis 写入失败: {e}")

        # Fallback 到内存
        if session_id not in self._context_cache:
            self._context_cache[session_id] = []
        self._context_cache[session_id].append(message)
        # 限制上下文长度
        if len(self._context_cache[session_id]) > max_history:
            self._context_cache[session_id] = self._context_cache[session_id][-max_history:]

    async def clear_context(self, session_id: str):
        """清除会话上下文"""
        if self.redis:
            try:
                await self.redis.delete(f"chat:context:{session_id}")
            except Exception:
                pass
        self._context_cache.pop(session_id, None)


# 全局对话管理器
chat_manager = ChatManager()
