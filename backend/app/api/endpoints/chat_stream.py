"""Chat API with Streaming Support（增强版）.

支持流式输出的智能对话端点

增强功能：
- 查询重写
- 查询类型检测
- 更丰富的流式事件
"""
import json
import traceback
from collections.abc import AsyncGenerator
from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.graphs.query_rewrite import rewrite_query, detect_query_type, expand_query
from app.graphs.stream_event import StreamEvent
from app.graphs.two_stage_workflow import two_stage_workflow
from app.schemas.chat import ChatStreamRequest, ChatResponse

router = APIRouter()

# SSE headers
_SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}

# Default values
_DEFAULT_SESSION_SUFFIX = "_default"
_DEFAULT_USER_ID = "default"


# ========== 增强的流式响应生成器 ==========
async def stream_chat_response_two_stage(
    message: str,
    session_id: str,
    user_id: str = _DEFAULT_USER_ID,
    chat_history: List[Dict] = None,
) -> AsyncGenerator[str, None]:
    """两阶段工作流流式生成聊天响应（使用两阶段工作流）.

    Args:
        message: 用户消息
        session_id: 会话ID
        user_id: 用户ID
        chat_history: 对话历史（当前版本未使用，保留兼容）

    Yields:
        Server-Sent Events 格式的数据
    """
    # 直接使用两阶段工作流
    async for event in two_stage_workflow.process(
        message=message,
        session_id=session_id,
        user_id=user_id
    ):
        yield event


async def stream_chat_response_enhanced(
    message: str,
    session_id: str,
    user_id: str = _DEFAULT_USER_ID,
    chat_history: List[Dict] = None,
) -> AsyncGenerator[str, None]:
    """增强的流式生成聊天响应（使用两阶段工作流）.

    增强功能：
    - 两阶段路由（闲聊/查询/追问）
    - 语气适配
    - 更丰富的流式事件

    Args:
        message: 用户消息
        session_id: 会话ID
        user_id: 用户ID
        chat_history: 对话历史（当前版本未使用，保留兼容）

    Yields:
        Server-Sent Events 格式的数据
    """
    # 使用两阶段工作流
    async for event in two_stage_workflow.process(
        message=message,
        session_id=session_id,
        user_id=user_id
    ):
        yield event


# ========== API 端点 ==========
@router.post("/stream")
async def chat_stream(request: ChatStreamRequest):
    """流式聊天端点（增强版）.

    使用 Server-Sent Events (SSE) 实现实时流式输出

    请求示例：
    ```json
    {
        "message": "查询余额大于5000的客户",
        "session_id": "user123_session456",
        "user_id": "user123",
        "history": []
    }
    ```

    响应事件类型：
    - thinking: 正在处理（包含 step 信息）
    - rewritten: 查询重写结果
    - query_info: 查询类型信息
    - intent: 意图识别结果
    - sql: 生成的 SQL 语句
    - query_result: 查询结果（row_count + preview）
    - stats: 统计分析结果
    - visualization: 可视化图表
    - text: 文本内容（逐字符输出）
    - answer: 最终回答
    - error: 错误信息
    - done: 流结束

    Returns:
        StreamingResponse: SSE 流式响应
    """
    session_id = request.session_id or f"{request.user_id}{_DEFAULT_SESSION_SUFFIX}"

    return StreamingResponse(
        stream_chat_response_enhanced(
            message=request.message,
            session_id=session_id,
            user_id=request.user_id,
            chat_history=request.history,
        ),
        media_type="text/event-stream",
        headers=_SSE_HEADERS,
    )


@router.post("/smart")
async def chat_smart(request: ChatStreamRequest) -> ChatResponse:
    """智能聊天端点（带查询重写和类型检测）.

    这是一个非流式的端点，返回完整的响应，包含：
    - 查询重写信息
    - 查询类型检测
    - 意图识别
    - 建议的可视化类型

    适用于需要快速获取查询元信息的场景
    """
    try:
        # 查询重写
        rewrite_result = rewrite_query(request.message, request.history)

        # 查询类型检测
        query_info = detect_query_type(request.message)

        # 构建响应
        answer_parts = []

        if rewrite_result["changed"]:
            answer_parts.append(f"📝 **查询已优化**：{rewrite_result['rewritten']}")

        answer_parts.extend([
            f"🎯 **意图类型**：{query_info['type']}",
            f"📊 **复杂度**：{query_info['complexity']}",
        ])

        if query_info.get("has_aggregation"):
            answer_parts.append("📈 **包含聚合**：是")
        if query_info.get("has_grouping"):
            answer_parts.append("📋 **包含分组**：是")
        if query_info.get("suggested_visualization"):
            answer_parts.append(f"📈 **建议图表**：{query_info['suggested_visualization']}")

        return ChatResponse(
            answer="\n\n".join(answer_parts),
            chart=None,
            sql=None,
            intent=query_info["type"],
            session_id=request.session_id,
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_query(request: ChatStreamRequest):
    """查询分析端点.

    返回对用户查询的详细分析，不执行实际查询
    """
    try:
        # 查询重写
        rewrite_result = rewrite_query(request.message, request.history)

        # 查询类型检测
        query_info = detect_query_type(request.message)

        # 查询扩展
        expansions = expand_query(request.message)

        return {
            "original_query": request.message,
            "rewritten_query": rewrite_result.get("rewritten"),
            "was_rewritten": rewrite_result.get("changed", False),
            "rewrite_reason": rewrite_result.get("reason"),
            "query_info": query_info,
            "expanded_queries": expansions,
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
