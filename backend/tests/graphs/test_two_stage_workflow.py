"""测试两阶段工作流"""
import pytest
from app.graphs.two_stage_workflow import TwoStageWorkflow


@pytest.mark.asyncio
async def test_chat_route():
    """测试闲聊路由"""
    workflow = TwoStageWorkflow()

    responses = []
    async for chunk in workflow.process(
        message="你好",
        session_id="test_session",
        user_id="test_user"
    ):
        responses.append(chunk)

    # route_type 是小写 "chat"
    assert any('"route_type": "chat"' in r for r in responses)
    assert any("answer" in r for r in responses)


@pytest.mark.asyncio
async def test_query_route():
    """测试查询路由"""
    workflow = TwoStageWorkflow()

    responses = []
    async for chunk in workflow.process(
        message="查询30岁以下的客户",
        session_id="test_session2",
        user_id="test_user"
    ):
        responses.append(str(chunk))

    # 应该包含 QUERY 意图（小写）
    assert any("query" in r for r in responses)


@pytest.mark.asyncio
async def test_followup_route():
    """测试追问路由"""
    workflow = TwoStageWorkflow()

    # 直接设置记忆，模拟已有查询历史
    memory = await workflow.memory_manager.get_or_create("test_session3", "test_user")
    memory.update_after_query(
        query="查询30岁以下的客户",
        sql="SELECT * FROM marketing_data WHERE age < 30",
        result=[{"age": 25}, {"age": 28}],
        intent="query"
    )

    # 追问 - 使用更明确的追问消息，包含上下文
    responses = []
    async for chunk in workflow.process(
        message="分析一下这些客户的转化率",
        session_id="test_session3",  # 同一个 session
        user_id="test_user"
    ):
        responses.append(str(chunk))

    assert any("followup" in r for r in responses)
