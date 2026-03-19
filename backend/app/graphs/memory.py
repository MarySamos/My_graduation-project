"""对话记忆管理器

负责维护会话状态和上下文记忆
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import re


@dataclass
class ConversationMemory:
    """对话记忆

    维护会话的所有状态信息，包括对话历史、查询记录、实体条件等
    """
    session_id: str
    user_id: str

    # 对话历史
    messages: List[Dict[str, str]] = field(default_factory=list)

    # 查询相关记忆
    current_topic: Optional[str] = None  # 当前讨论主题
    last_query: Optional[str] = None     # 上一次查询
    last_sql: Optional[str] = None       # 上一次 SQL
    last_result: Optional[List[Dict]] = None  # 上一次结果
    last_intent: Optional[str] = None    # 上一次意图

    # 提及的筛选条件
    mentioned_filters: Dict[str, Any] = field(default_factory=dict)

    # 统计
    query_count: int = 0

    # 缓存阈值
    _cache_threshold: int = 1000

    def add_message(self, role: str, content: str):
        """添加对话消息"""
        self.messages.append({
            "role": role,
            "content": content
        })

    def update_after_query(
        self,
        query: str,
        sql: str,
        result: List[Dict],
        intent: str = "query"
    ):
        """查询后更新记忆"""
        self.last_query = query
        self.last_sql = sql
        self.last_intent = intent
        self.query_count += 1

        # 提取主题（简化处理：取前10个字）
        self.current_topic = query[:20] if len(query) > 20 else query

        # 缓存结果（如果不太大）
        if self.should_cache_result(len(result)):
            self.last_result = result
        else:
            self.last_result = None

    def extract_filters(self, text: str) -> Dict[str, Any]:
        """从文本中提取筛选条件（简化版）"""
        filters = {}

        # 年龄条件
        age_pattern = r'(\d+)\s*岁'
        age_match = re.search(age_pattern, text)
        if age_match:
            age = int(age_match.group(1))
            # 判断是小于还是大于
            if any(word in text for word in ["以下", "小于", "不到", "不满"]):
                filters["age"] = {"op": "<", "value": age}
            elif any(word in text for word in ["以上", "大于", "超过", "满"]):
                filters["age"] = {"op": ">", "value": age}

        # 职业条件
        jobs = ["admin", "technician", "services", "management", "retired",
                "student", "blue-collar", "self-employed", "unemployed",
                "housemaid", "entrepreneur", "管理员", "技术员", "学生", "退休"]
        for job in jobs:
            if job in text:
                filters["job"] = job
                break

        # 婚姻状况
        if "已婚" in text or "married" in text.lower():
            filters["marital"] = "married"
        elif "未婚" in text or "single" in text.lower():
            filters["marital"] = "single"
        elif "离异" in text or "divorced" in text.lower():
            filters["marital"] = "divorced"

        return filters

    def add_filters(self, filters: Dict[str, Any]):
        """合并新的筛选条件"""
        self.mentioned_filters.update(filters)

    def should_cache_result(self, result_size: int) -> bool:
        """判断是否缓存结果"""
        return result_size <= self._cache_threshold

    def clear_results(self):
        """清除结果缓存（但保留筛选条件）"""
        self.last_result = None
        self.last_sql = None
        self.current_topic = None

    def has_query_history(self) -> bool:
        """是否有查询历史"""
        return self.last_query is not None

    def get_last_query_summary(self) -> str:
        """获取上一次查询的摘要"""
        if not self.last_query:
            return "（无历史查询）"
        return self.last_query
