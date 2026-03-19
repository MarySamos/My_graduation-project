"""测试语气适配器"""
import pytest
from app.graphs.tone import ToneAdapter
from app.graphs.enums import RouteType


def test_adapt_chat_tone():
    """测试闲聊语气"""
    adapter = ToneAdapter()
    result = adapter.adapt("你好，我是AI助手", RouteType.CHAT)

    assert "😊" in result or len(result) > 10


def test_adapt_query_tone():
    """测试查询语气"""
    adapter = ToneAdapter()
    result = adapter.adapt("查询到2534条记录", RouteType.QUERY, has_data=True)

    assert "查询到" in result or "找到" in result
    # 应该比较正式


def test_adapt_error_tone():
    """测试错误语气"""
    adapter = ToneAdapter()
    result = adapter.adapt("SQL错误", RouteType.QUERY, is_error=True)

    assert "抱歉" in result or "无法" in result
