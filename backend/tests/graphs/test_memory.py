"""测试对话记忆管理器"""
import pytest
from app.graphs.memory import ConversationMemory


def test_create_memory():
    """测试创建记忆"""
    memory = ConversationMemory(
        session_id="test_session",
        user_id="user123"
    )
    assert memory.session_id == "test_session"
    assert memory.user_id == "user123"
    assert memory.messages == []
    assert memory.current_topic is None


def test_add_message():
    """测试添加消息"""
    memory = ConversationMemory(session_id="s1", user_id="u1")
    memory.add_message("user", "你好")
    memory.add_message("assistant", "你好呀！")

    assert len(memory.messages) == 2
    assert memory.messages[0]["role"] == "user"
    assert memory.messages[0]["content"] == "你好"


def test_update_after_query():
    """测试查询后更新记忆"""
    memory = ConversationMemory(session_id="s1", user_id="u1")
    result = [{"age": 25, "name": "Tom"}]

    memory.update_after_query(
        query="查询30岁以下客户",
        sql="SELECT * FROM marketing_data WHERE age < 30",
        result=result
    )

    assert memory.last_query == "查询30岁以下客户"
    assert memory.last_sql == "SELECT * FROM marketing_data WHERE age < 30"
    assert memory.last_result == result
    assert memory.current_topic == "查询30岁以下客户"


def test_extract_filters():
    """测试提取筛选条件"""
    memory = ConversationMemory(session_id="s1", user_id="u1")
    filters = memory.extract_filters("查询年龄小于30岁的学生")

    assert "age" in filters
    assert filters["age"]["op"] == "<"
    assert filters["age"]["value"] == 30
    assert "job" in filters


def test_merge_filters():
    """测试合并筛选条件"""
    memory = ConversationMemory(session_id="s1", user_id="u1")
    memory.mentioned_filters = {"age": {"op": "<", "value": 30}}

    new_filters = {"marital": "married"}
    memory.add_filters(new_filters)

    assert "age" in memory.mentioned_filters
    assert "marital" in memory.mentioned_filters


def test_should_cache_result():
    """测试缓存判断"""
    memory = ConversationMemory(session_id="s1", user_id="u1")

    # 小结果应该缓存
    assert memory.should_cache_result(100) is True
    assert memory.should_cache_result(999) is True
    assert memory.should_cache_result(1000) is True  # 边界值

    # 大结果不缓存
    assert memory.should_cache_result(1001) is False


def test_clear_results():
    """测试清除结果缓存"""
    memory = ConversationMemory(session_id="s1", user_id="u1")
    memory.last_result = [{"a": 1}]
    memory.last_sql = "SELECT 1"

    memory.clear_results()

    assert memory.last_result is None
    assert memory.last_sql is None
    assert memory.current_topic is None
