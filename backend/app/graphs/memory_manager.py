"""记忆管理器

管理多个会话的记忆存储
"""
from typing import Dict
from app.graphs.memory import ConversationMemory


class MemoryManager:
    """记忆管理器

    管理多个 session 的记忆
    """

    def __init__(self):
        self._memories: Dict[str, ConversationMemory] = {}

    async def get_or_create(
        self,
        session_id: str,
        user_id: str = "default"
    ) -> ConversationMemory:
        """获取或创建记忆"""
        if session_id not in self._memories:
            self._memories[session_id] = ConversationMemory(
                session_id=session_id,
                user_id=user_id
            )
        return self._memories[session_id]

    async def update(self, memory: ConversationMemory):
        """更新记忆（已保存在内存中）"""
        # 实际持久化可以在这里添加
        pass

    async def clear(self, session_id: str):
        """清除指定会话的记忆"""
        if session_id in self._memories:
            del self._memories[session_id]
