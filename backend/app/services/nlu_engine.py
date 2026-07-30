"""
自然语言理解引擎 - 插件化设计
支持规则匹配和 LLM API 两种模式，可扩展
"""
import re
from typing import Dict, Tuple, Optional
from loguru import logger


# 意图规则库 - 可轻松扩展
INTENT_RULES = {
    "greeting": {
        "patterns": [r"你好", r"嗨", r"hello", r"hi", r"hey", r"早上好", r"下午好", r"晚上好"],
        "responses": [
            "你好呀！有什么我可以帮助你的吗？😊",
            "嗨！很高兴见到你！",
            "你好！我是 Hanbao，有什么想聊的吗？",
        ],
    },
    "farewell": {
        "patterns": [r"再见", r"拜拜", r"bye", r"goodbye", r"下次见", r"走了"],
        "responses": ["再见！祝你今天愉快！👋", "拜拜！有需要随时找我~", "下次见！"],
    },
    "help": {
        "patterns": [r"帮助", r"help", r"怎么用", r"能做什么", r"功能", r"做什么"],
        "responses": [
            "我是 Hanbao 聊天机器人！我可以：\n- 陪你聊天\n- 回答简单问题\n- 记录对话历史\n- 多轮上下文对话\n试试跟我聊聊吧！",
        ],
    },
    "weather": {
        "patterns": [r"天气", r"weather", r"下雨", r"气温", r"温度", r"刮风"],
        "responses": [
            "我目前还没有接入天气查询API，不过你可以告诉我你在哪个城市，我帮你记下来，以后接入天气服务时就能提醒你啦！",
            "天气功能正在开发中...你可以先聊聊别的 🌤️",
        ],
    },
    "time": {
        "patterns": [r"时间", r"几点", r"日期", r"今天", r"time", r"day"],
        "responses": [
            "你可以看看你的设备时钟哦～不过我可以帮你记录重要的事情！",
        ],
    },
    "thanks": {
        "patterns": [r"谢谢", r"感谢", r"thanks", r"thank you", r"谢了"],
        "responses": ["不客气！能帮到你我很开心~ 😊", "不用谢！有需要随时找我~", "这是我应该做的！"],
    },
    "joke": {
        "patterns": [r"笑话", r"joke", r"搞笑", r"开心", r"无聊"],
        "responses": [
            "来一个：为什么程序员总是分不清万圣节和圣诞节？因为 Oct 31 = Dec 25 🎃",
            "知道为什么Python程序员戴眼镜吗？因为他们看不清C！😄",
            "一个SQL语句走进酒吧，看到两张桌子（tables），于是问：我可以JOIN你们吗？",
        ],
    },
    "name": {
        "patterns": [r"你叫什么", r"你是谁", r"名字", r"your name", r"who are you"],
        "responses": [
            "我是 Hanbao！一个住在 Docker 容器里的聊天机器人 🐳",
            "我叫 Hanbao，是你的 AI 聊天伙伴！",
        ],
    },
}


class NLUEngine:
    """NLU 引擎 - 支持规则匹配，预留 LLM API 扩展"""

    def __init__(self, engine_type: str = "rule"):
        self.engine_type = engine_type
        logger.info(f"NLU 引擎初始化: {engine_type}")

    async def understand(self, text: str) -> Dict:
        """
        理解用户输入
        返回: {"intent": str, "confidence": float, "entities": list}
        """
        if self.engine_type == "rule":
            return self._rule_match(text)
        return self._default_understand(text)

    def _rule_match(self, text: str) -> Dict:
        """规则匹配"""
        text_lower = text.lower().strip()
        best_intent = "chat"
        best_confidence = 0.5

        for intent, data in INTENT_RULES.items():
            for pattern in data["patterns"]:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    best_intent = intent
                    best_confidence = 0.85
                    break

        return {
            "intent": best_intent,
            "confidence": best_confidence,
            "entities": [],
        }

    def _default_understand(self, text: str) -> Dict:
        """默认理解（fallback）"""
        return {
            "intent": "chat",
            "confidence": 0.5,
            "entities": [],
        }

    def get_response(self, intent: str) -> str:
        """获取意图对应的回复"""
        import random
        if intent in INTENT_RULES:
            responses = INTENT_RULES[intent]["responses"]
            return random.choice(responses)
        return ""


# 全局 NLU 实例
nlu_engine = NLUEngine(engine_type="rule")
