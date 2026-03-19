"""语气适配器

根据内容类型调整回答语气
"""
from app.graphs.enums import RouteType


class ToneAdapter:
    """语气适配器

    根据路由类型和内容调整回答语气
    """

    # 闲聊用 emoji
    CHAT_EMOJIS = ["😊", "👋", "✨", "💪", "🎉"]

    # 数据洞察词
    INSIGHT_PHRASES = [
        "从数据来看",
        "值得注意的是",
        "这说明",
        "数据显示",
        "整体而言"
    ]

    def adapt(
        self,
        content: str,
        route_type: RouteType,
        has_data: bool = False,
        is_error: bool = False
    ) -> str:
        """适配语气

        Args:
            content: 原始内容
            route_type: 路由类型
            has_data: 是否有数据
            is_error: 是否是错误

        Returns:
            适配后的内容
        """
        if is_error:
            return self._error_tone(content)

        if route_type == RouteType.CHAT:
            return self._friendly_tone(content)

        if has_data:
            return self._professional_insight_tone(content)

        return self._neutral_tone(content)

    def _friendly_tone(self, content: str) -> str:
        """友好语气（闲聊）"""
        # 如果没有 emoji，添加一个
        if not any(emoji in content for emoji in self.CHAT_EMOJIS):
            import random
            emoji = random.choice(self.CHAT_EMOJIS)
            # 只在结尾添加，且原句不长
            if len(content) < 100:
                return f"{content} {emoji}"

        return content

    def _professional_insight_tone(self, content: str) -> str:
        """专业且有洞察力的语气"""
        # 如果太短，不需要添加洞察
        if len(content) < 50:
            return content

        # 如果已经包含洞察词，不重复
        if any(phrase in content for phrase in self.INSIGHT_PHRASES):
            return content

        # 在开头添加一个洞察词
        import random
        phrase = random.choice(self.INSIGHT_PHRASES)
        return f"{phrase}，{content[0].lower()}{content[1:]}"

    def _neutral_tone(self, content: str) -> str:
        """中性语气"""
        return content

    def _error_tone(self, content: str) -> str:
        """错误提示语气"""
        error_prefixes = [
            "抱歉，",
            "不好意思，",
            "遇到了问题："
        ]

        # 如果没有前缀，添加一个
        if not any(content.startswith(p) for p in error_prefixes):
            return f"抱歉，{content}"

        return content
