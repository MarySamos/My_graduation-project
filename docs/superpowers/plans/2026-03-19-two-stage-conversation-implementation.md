# 两阶段对话架构实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建两阶段路由的智能对话系统，实现自然的闲聊、精准的数据查询、灵活的追问处理。

**架构:** 第一阶段用轻量级路由器判断意图（闲聊/查询/追问），第二阶段分发到对应处理器。闲聊用高温 LLM，查询复用现有 SQL 工作流，追问用专门的分析器。

**Tech Stack:** LangGraph, LangChain, FastAPI, PostgreSQL, Pytest

---

## 文件结构

### 新增文件
```
backend/app/graphs/
├── router.py              # 对话路由器
├── memory.py              # 对话记忆管理
├── chat_handler.py        # 闲聊处理器
├── followup.py            # 追问分析器
├── tone.py                # 语气适配器
├── two_stage_workflow.py  # 两阶段工作流入口
└── agents/
    ├── __init__.py
    ├── router_agent.py    # 路由 LLM Agent
    └── chat_agent.py      # 闲聊 LLM Agent

backend/tests/graphs/
├── __init__.py
├── test_router.py
├── test_memory.py
├── test_chat_handler.py
├── test_followup.py
└── test_two_stage_workflow.py
```

### 修改文件
```
backend/app/api/endpoints/chat.py         # 使用 two_stage_workflow
backend/app/api/endpoints/chat_stream.py  # 使用 two_stage_workflow
backend/app/graphs/prompts.py             # 添加新 Prompt
```

---

## Task 1: 创建基础枚举和数据结构

**Files:**
- Create: `backend/app/graphs/route_types.py`
- Modify: `backend/app/graphs/enums.py`

- [ ] **Step 1: 添加路由类型枚举到 enums.py**

在 `backend/app/graphs/enums.py` 末尾添加：

```python
class RouteType(str, Enum):
    """路由类型"""
    CHAT = "chat"            # 闲聊
    QUERY = "query"          # 数据查询
    FOLLOWUP = "followup"    # 追问
    CORRECTION = "correction"  # 修正


class FollowupType(str, Enum):
    """追问类型"""
    EXPLAIN = "explain"      # 解释原因
    DETAIL = "detail"        # 展开细节
    DRILLDOWN = "drilldown"  # 下钻细分
    COMPARE = "compare"      # 对比
    TREND = "trend"          # 趋势
```

- [ ] **Step 2: 创建路由决策数据类**

创建 `backend/app/graphs/route_types.py`：

```python
"""路由相关数据结构"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from app.graphs.enums import RouteType, FollowupType


@dataclass
class RouteDecision:
    """路由决策结果"""
    route_type: RouteType
    confidence: float
    reasoning: str = ""

    # 提取的实体（用于查询）
    extracted_entities: Dict[str, Any] = field(default_factory=dict)

    # 追问相关
    followup_type: Optional[FollowupType] = None
    drilldown_dimension: Optional[str] = None  # 下钻维度

    def is_query_type(self) -> bool:
        """是否是查询类型（包括修正）"""
        return self.route_type in (RouteType.QUERY, RouteType.CORRECTION)

    def is_followup(self) -> bool:
        """是否是追问"""
        return self.route_type == RouteType.FOLLOWUP
```

- [ ] **Step 3: 验证语法**

运行:
```bash
cd backend && python -c "from app.graphs.enums import RouteType, FollowupType; from app.graphs.route_types import RouteDecision; print('OK')"
```
预期: 输出 `OK`

- [ ] **Step 4: Commit**

```bash
git add backend/app/graphs/enums.py backend/app/graphs/route_types.py
git commit -m "feat: 添加路由类型枚举和路由决策数据类"
```

---

## Task 2: 实现对话记忆管理器

**Files:**
- Create: `backend/app/graphs/memory.py`
- Test: `backend/tests/graphs/test_memory.py`

- [ ] **Step 1: 写记忆管理器的测试**

创建 `backend/tests/graphs/test_memory.py`：

```python
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
    assert memory.current_topic == "30岁以下客户"


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
```

- [ ] **Step 2: 运行测试验证失败**

运行:
```bash
cd backend && python -m pytest tests/graphs/test_memory.py -v
```
预期: FAIL - "ModuleNotFoundError: No module named 'app.graphs.memory'"

- [ ] **Step 3: 实现 ConversationMemory**

创建 `backend/app/graphs/memory.py`：

```python
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
```

- [ ] **Step 4: 运行测试验证通过**

运行:
```bash
cd backend && python -m pytest tests/graphs/test_memory.py -v
```
预期: PASS (7 passed)

- [ ] **Step 5: Commit**

```bash
git add backend/app/graphs/memory.py backend/tests/graphs/test_memory.py
git commit -m "feat: 实现对话记忆管理器"
```

---

## Task 3: 实现对话路由器

**Files:**
- Create: `backend/app/graphs/router.py`
- Create: `backend/app/graphs/agents/router_agent.py`
- Test: `backend/tests/graphs/test_router.py`

- [ ] **Step 1: 写路由器测试**

创建 `backend/tests/graphs/test_router.py`：

```python
"""测试对话路由器"""
import pytest
from app.graphs.router import ConversationRouter
from app.graphs.memory import ConversationMemory
from app.graphs.enums import RouteType


@pytest.mark.asyncio
async def test_route_chat_greeting():
    """测试问候路由到闲聊"""
    router = ConversationRouter()
    memory = ConversationMemory(session_id="s1", user_id="u1")

    decision = await router.route("你好", memory)

    assert decision.route_type == RouteType.CHAT
    assert decision.confidence > 0.7


@pytest.mark.asyncio
async def test_route_chat_thanks():
    """测试感谢路由到闲聊"""
    router = ConversationRouter()
    memory = ConversationMemory(session_id="s1", user_id="u1")

    decision = await router.route("谢谢你的帮助", memory)

    assert decision.route_type == RouteType.CHAT


@pytest.mark.asyncio
async def test_route_query():
    """测试查询路由"""
    router = ConversationRouter()
    memory = ConversationMemory(session_id="s1", user_id="u1")

    decision = await router.route("查询30岁以下的客户", memory)

    assert decision.route_type == RouteType.QUERY
    assert "age" in decision.extracted_entities


@pytest.mark.asyncio
async def test_route_followup_explain():
    """测试解释型追问"""
    router = ConversationRouter()
    memory = ConversationMemory(session_id="s1", user_id="u1")
    memory.last_query = "查询30岁以下的客户"
    memory.current_topic = "30岁以下客户"

    decision = await router.route("为什么转化率这么低？", memory)

    assert decision.route_type == RouteType.FOLLOWUP
    assert decision.followup_type is not None


@pytest.mark.asyncio
async def test_route_correction():
    """测试修正路由"""
    router = ConversationRouter()
    memory = ConversationMemory(session_id="s1", user_id="u1")
    memory.last_query = "查询30岁以下的客户"

    decision = await router.route("不是30岁，是40岁以上的", memory)

    assert decision.route_type == RouteType.CORRECTION
```

- [ ] **Step 2: 运行测试验证失败**

运行:
```bash
cd backend && python -m pytest tests/graphs/test_router.py -v
```
预期: FAIL - "ModuleNotFoundError"

- [ ] **Step 3: 实现路由器 Agent**

创建 `backend/app/graphs/agents/__init__.py`：
```python
"""LLM Agents"""
```

创建 `backend/app/graphs/agents/router_agent.py`：

```python
"""路由 LLM Agent

使用 LLM 进行智能路由决策
"""
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.core.config import settings


class RouterAgent:
    """路由 LLM Agent"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0.1,  # 低温度，确保稳定
            openai_api_key=settings.ZHIPU_API_KEY,
            openai_api_base=settings.LLM_API_BASE
        )
        self.parser = JsonOutputParser()
        self._build_chain()

    def _build_chain(self):
        """构建路由链"""
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是对话路由器。根据用户输入判断路由类型。

## 路由类型

1. **CHAT** - 闲聊、问候、感谢、告别
   - 问候：你好、嗨、在吗
   - 感谢：谢谢、感谢、多谢
   - 告别：再见、拜拜
   - 能力询问：你能做什么、你会什么

2. **QUERY** - 数据查询请求
   - 包含"查询"、"显示"、"列出"、"有多少"、"统计"
   - 包含具体条件（年龄、职业等）

3. **FOLLOWUP** - 追问之前的结果
   - 追问词：为什么、怎么样、分析一下、详细说、展开
   - 代词：它、它们、那些、这个
   - 要求：需要有查询历史

4. **CORRECTION** - 修正之前的查询
   - 修正词：不是、错了、重新、换、除了
   - 要求是针对上一次查询的修正

## 判断逻辑

1. 先判断是否是问候/感谢/告别 → CHAT
2. 判断是否是修正（"不是X，是Y"）→ CORRECTION
3. 判断是否是追问（有历史 + 追问词）→ FOLLOWUP
4. 判断是否是数据查询 → QUERY
5. 默认 → CHAT

## 输出格式

返回 JSON：
```json
{{
  "route_type": "CHAT|QUERY|FOLLOWUP|CORRECTION",
  "confidence": 0.9,
  "reasoning": "判断理由"
}}
```

注意：
- confidence 是 0-1 的置信度
- reasoning 简要说明判断依据（中文）"""),
            ("user", """## 用户输入
{message}

## 对话上下文
{context}

## 查询历史
{query_history}

请返回路由决策：""")
        ])

        self.chain = self.prompt | self.llm | self.parser

    async def route(
        self,
        message: str,
        context: str,
        query_history: str
    ) -> Dict[str, Any]:
        """执行路由

        Args:
            message: 用户消息
            context: 对话上下文
            query_history: 查询历史

        Returns:
            路由决策字典
        """
        try:
            result = await self.chain.ainvoke({
                "message": message,
                "context": context or "（无）",
                "query_history": query_history or "（无）"
            })
            return result
        except Exception as e:
            # 降级：基于规则的简单路由
            return self._fallback_route(message)

    def _fallback_route(self, message: str) -> Dict[str, Any]:
        """降级路由（基于规则）"""
        message_lower = message.lower()

        # 问候/感谢/告别
        if any(word in message for word in ["你好", "嗨", "在吗", "谢谢", "感谢", "再见", "拜拜"]):
            return {"route_type": "CHAT", "confidence": 0.8, "reasoning": "匹配问候词"}

        # 修正
        if any(word in message for word in ["不是", "错了", "重新", "换"]):
            return {"route_type": "CORRECTION", "confidence": 0.7, "reasoning": "匹配修正词"}

        # 追问
        if any(word in message for word in ["为什么", "怎么样", "分析", "详细", "展开"]):
            return {"route_type": "FOLLOWUP", "confidence": 0.6, "reasoning": "匹配追问词"}

        # 数据查询关键词
        if any(word in message for word in ["查询", "显示", "统计", "多少", "列表"]):
            return {"route_type": "QUERY", "confidence": 0.7, "reasoning": "匹配查询词"}

        # 默认闲聊
        return {"route_type": "CHAT", "confidence": 0.5, "reasoning": "默认分类"}
```

- [ ] **Step 4: 实现路由器**

创建 `backend/app/graphs/router.py`：

```python
"""对话路由器

根据用户输入判断路由到哪个处理器
"""
from typing import Optional
from app.graphs.route_types import RouteDecision
from app.graphs.enums import RouteType, FollowupType
from app.graphs.memory import ConversationMemory
from app.graphs.agents.router_agent import RouterAgent


class ConversationRouter:
    """对话路由器

    判断用户意图，分发到对应处理器
    """

    def __init__(self):
        self.agent = RouterAgent()

    async def route(
        self,
        message: str,
        memory: ConversationMemory
    ) -> RouteDecision:
        """路由决策

        Args:
            message: 用户消息
            memory: 对话记忆

        Returns:
            路由决策
        """
        # 构建上下文
        context = self._format_context(memory)
        query_history = memory.get_last_query_summary()

        # 调用 LLM Agent
        agent_result = await self.agent.route(message, context, query_history)

        # 解析结果
        route_type = RouteType(agent_result.get("route_type", "CHAT"))
        confidence = agent_result.get("confidence", 0.5)
        reasoning = agent_result.get("reasoning", "")

        # 提取实体（如果是查询类型）
        extracted_entities = {}
        if route_type in (RouteType.QUERY, RouteType.CORRECTION):
            extracted_entities = memory.extract_filters(message)

        # 判断追问类型
        followup_type = None
        drilldown_dimension = None
        if route_type == RouteType.FOLLOWUP:
            followup_type = self._detect_followup_type(message)
            if followup_type == FollowupType.DRILLDOWN:
                drilldown_dimension = self._extract_drilldown_dimension(message)

        return RouteDecision(
            route_type=route_type,
            confidence=confidence,
            reasoning=reasoning,
            extracted_entities=extracted_entities,
            followup_type=followup_type,
            drilldown_dimension=drilldown_dimension
        )

    def _format_context(self, memory: ConversationMemory) -> str:
        """格式化上下文"""
        if not memory.messages:
            return "（无对话历史）"

        # 只取最近3轮
        recent = memory.messages[-6:]  # 6条 = 3轮
        parts = []
        for msg in recent:
            role = "用户" if msg["role"] == "user" else "助手"
            parts.append(f"{role}: {msg['content']}")

        return "\n".join(parts)

    def _detect_followup_type(self, message: str) -> Optional[FollowupType]:
        """检测追问类型"""
        # 解释型
        if any(word in message for word in ["为什么", "什么意思", "解释"]):
            return FollowupType.EXPLAIN

        # 展开型
        if any(word in message for word in ["详细", "展开", "多说", "更多"]):
            return FollowupType.DETAIL

        # 下钻型
        if any(word in message for word in ["按", "细分", "分组", "分别"]):
            return FollowupType.DRILLDOWN

        # 对比型
        if any(word in message for word in ["对比", "比较", "相差"]):
            return FollowupType.COMPARE

        # 趋势型
        if any(word in message for word in ["趋势", "变化", "增长"]):
            return FollowupType.TREND

        return None

    def _extract_drilldown_dimension(self, message: str) -> Optional[str]:
        """提取下钻维度"""
        # 检测常见维度
        dimensions = {
            "职业": "job",
            "job": "job",
            "教育": "education",
            "education": "education",
            "婚姻": "marital",
            "marital": "marital",
            "年龄": "age",
        }

        for key, value in dimensions.items():
            if key in message:
                return value

        return None
```

- [ ] **Step 5: 运行测试验证通过**

运行:
```bash
cd backend && python -m pytest tests/graphs/test_router.py -v
```
预期: PASS (6 passed)

- [ ] **Step 6: Commit**

```bash
git add backend/app/graphs/router.py backend/app/graphs/agents/ backend/tests/graphs/test_router.py
git commit -m "feat: 实现对话路由器"
```

---

## Task 4: 实现闲聊处理器

**Files:**
- Create: `backend/app/graphs/chat_handler.py`
- Create: `backend/app/graphs/agents/chat_agent.py`
- Test: `backend/tests/graphs/test_chat_handler.py`

- [ ] **Step 1: 写闲聊处理器测试**

创建 `backend/tests/graphs/test_chat_handler.py`：

```python
"""测试闲聊处理器"""
import pytest
from app.graphs.chat_handler import ChatHandler
from app.graphs.memory import ConversationMemory


@pytest.mark.asyncio
async def test_greeting():
    """测试问候响应"""
    handler = ChatHandler()
    memory = ConversationMemory(session_id="s1", user_id="u1")

    response = await handler.chat("你好", memory)

    assert response
    assert len(response) > 5
    # 应该比较友好
    assert any(word in response for word in ["你好", "嗨", "😊", "助手"])


@pytest.mark.asyncio
async def test_with_context():
    """测试带上下文的闲聊"""
    handler = ChatHandler()
    memory = ConversationMemory(session_id="s1", user_id="u1")
    memory.messages = [
        {"role": "user", "content": "我叫小明"},
        {"role": "assistant", "content": "你好小明！"}
    ]

    response = await handler.chat("我刚才说我叫什么？", memory)

    assert "小明" in response
```

- [ ] **Step 2: 运行测试验证失败**

运行:
```bash
cd backend && python -m pytest tests/graphs/test_chat_handler.py -v
```
预期: FAIL - "ModuleNotFoundError"

- [ ] **Step 3: 实现闲聊 Agent**

创建 `backend/app/graphs/agents/chat_agent.py`：

```python
"""闲聊 LLM Agent"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.config import settings


class ChatAgent:
    """闲聊 LLM Agent

    使用高温度 LLM 进行自然对话
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0.8,  # 高温度，更自然
            openai_api_key=settings.ZHIPU_API_KEY,
            openai_api_base=settings.LLM_API_BASE
        )
        self.parser = StrOutputParser()
        self._build_chain()

    def _build_chain(self):
        """构建闲聊链"""
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是 BankAgent，一个亲切友好的银行数据分析助手。

## 你的特点
- 专业但不刻板，可以适当使用 😊 等表情
- 热情帮助用户了解数据
- 如果用户问银行业务知识，尽力回答
- 记住用户之前说过的内容

## 你的能力
- 帮助查询和分析银行营销数据
- 解读数据趋势和洞察
- 回答银行业务相关问题
- 进行友好的对话交流

回答风格：
- 简洁自然，不要太啰嗦
- 适当使用 emoji 增加亲和力
- 如果不知道，诚实地说不知道"""),
            ("user", """## 对话历史
{history}

## 用户说
{message}

请回复：""")
        ])

        self.chain = self.prompt | self.llm | self.parser

    async def chat(self, message: str, history: str) -> str:
        """进行闲聊

        Args:
            message: 用户消息
            history: 对话历史

        Returns:
            回复内容
        """
        return await self.chain.ainvoke({
            "message": message,
            "history": history or "（这是我们对话的开始）"
        })
```

- [ ] **Step 4: 实现闲聊处理器**

创建 `backend/app/graphs/chat_handler.py`：

```python
"""闲聊处理器

处理非数据查询的对话
"""
from app.graphs.memory import ConversationMemory
from app.graphs.agents.chat_agent import ChatAgent


class ChatHandler:
    """闲聊处理器

    处理问候、闲聊、感谢等非数据查询对话
    """

    def __init__(self):
        self.agent = ChatAgent()

    async def chat(
        self,
        message: str,
        memory: ConversationMemory
    ) -> str:
        """处理闲聊

        Args:
            message: 用户消息
            memory: 对话记忆

        Returns:
            回复内容
        """
        # 格式化历史
        history = self._format_history(memory)

        # 调用 Agent
        response = await self.agent.chat(message, history)

        # 更新记忆
        memory.add_message("user", message)
        memory.add_message("assistant", response)

        return response

    def _format_history(self, memory: ConversationMemory) -> str:
        """格式化对话历史"""
        if not memory.messages:
            return "（这是我们对话的开始）"

        # 只取最近5轮
        recent = memory.messages[-10:]
        parts = []
        for msg in recent:
            role = "用户" if msg["role"] == "user" else "我"
            parts.append(f"{role}: {msg['content']}")

        return "\n".join(parts)
```

- [ ] **Step 5: 运行测试验证通过**

运行:
```bash
cd backend && python -m pytest tests/graphs/test_chat_handler.py -v
```
预期: PASS (2 passed)

- [ ] **Step 6: Commit**

```bash
git add backend/app/graphs/chat_handler.py backend/app/graphs/agents/chat_agent.py backend/tests/graphs/test_chat_handler.py
git commit -m "feat: 实现闲聊处理器"
```

---

## Task 5: 实现追问分析器

**Files:**
- Create: `backend/app/graphs/followup.py`
- Create: `backend/app/graphs/agents/followup_agent.py`
- Test: `backend/tests/graphs/test_followup.py`

- [ ] **Step 1: 写追问分析器测试**

创建 `backend/tests/graphs/test_followup.py`：

```python
"""测试追问分析器"""
import pytest
from app.graphs.followup import FollowupAnalyzer, FollowupAction
from app.graphs.memory import ConversationMemory
from app.graphs.enums import FollowupType


@pytest.mark.asyncio
async def test_explain_followup():
    """测试解释型追问"""
    analyzer = FollowupAnalyzer()
    memory = ConversationMemory(session_id="s1", user_id="u1")
    memory.last_query = "查询30岁以下的客户"
    memory.last_result = [
        {"age": 25, "job": "student", "y": "no"},
        {"age": 28, "job": "student", "y": "no"},
    ]

    action = FollowupAction(
        type=FollowupType.EXPLAIN,
        data=memory.last_result,
        context=memory.current_topic
    )

    response = await analyzer.handle(action, memory)

    assert response
    assert len(response) > 10


@pytest.mark.asyncio
async def test_drilldown_followup():
    """测试下钻型追问"""
    analyzer = FollowupAnalyzer()
    memory = ConversationMemory(session_id="s1", user_id="u1")
    memory.last_query = "查询30岁以下的客户"
    memory.last_sql = "SELECT * FROM marketing_data WHERE age < 30"

    action = FollowupAction(
        type=FollowupType.DRILLDOWN,
        dimension="job",
        context="30岁以下客户"
    )

    sql = await analyzer.generate_drilldown_sql(action, memory)

    assert "job" in sql.lower()
    assert "group by" in sql.lower()


@pytest.mark.asyncio
async def test_no_history_followup():
    """测试无历史时的追问"""
    analyzer = FollowupAnalyzer()
    memory = ConversationMemory(session_id="s1", user_id="u1")
    # 没有查询历史

    action = await analyzer.analyze("为什么转化率低？", memory)

    assert action.type == "NEW_QUERY"
```

- [ ] **Step 2: 运行测试验证失败**

运行:
```bash
cd backend && python -m pytest tests/graphs/test_followup.py -v
```
预期: FAIL - "ModuleNotFoundError"

- [ ] **Step 3: 实现追问分析器**

首先在 `backend/app/graphs/route_types.py` 末尾添加：

```python
@dataclass
class FollowupAction:
    """追问动作"""
    type: str  # EXPLAIN, DETAIL, DRILLDOWN, COMPARE, TREND, NEW_QUERY
    data: Optional[List[Dict]] = None
    context: Optional[str] = None
    dimension: Optional[str] = None  # 下钻维度
    reason: str = ""
```

创建 `backend/app/graphs/agents/followup_agent.py`：

```python
"""追问分析 LLM Agent"""
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.config import settings


class FollowupAgent:
    """追问分析 LLM Agent"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0.3,
            openai_api_key=settings.ZHIPU_API_KEY,
            openai_api_base=settings.LLM_API_BASE
        )
        self.parser = StrOutputParser()
        self._build_chain()

    def _build_chain(self):
        """构建追问分析链"""
        self.explain_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是数据分析专家。请分析用户对查询结果的追问。

## 你的任务
用户问"为什么"或"什么意思"，你需要：
1. 分析数据特点
2. 给出合理的业务解释
3. 保持专业但易懂

## 分析角度
- 数据分布（集中/分散）
- 数值大小（高/低/平均）
- 比例关系（占比、转化率）
- 业务含义（可能的原因）

注意：如果数据不足以得出结论，诚实说明。"""),
            ("user", """## 上一次查询
{last_query}

## 数据结果
{data_preview}

## 用户追问
{message}

请分析：""")
        ])

        self.explain_chain = self.explain_prompt | self.llm | self.parser

    async def explain(
        self,
        message: str,
        last_query: str,
        data_preview: str
    ) -> str:
        """解释型追问"""
        return await self.explain_chain.ainvoke({
            "message": message,
            "last_query": last_query,
            "data_preview": data_preview
        })
```

创建 `backend/app/graphs/followup.py`：

```python
"""追问分析器

处理用户对之前结果的追问
"""
from typing import Optional
import json

from app.graphs.memory import ConversationMemory
from app.graphs.enums import FollowupType
from app.graphs.route_types import FollowupAction
from app.graphs.agents.followup_agent import FollowupAgent


class FollowupAnalyzer:
    """追问分析器

    分析和处理用户的追问
    """

    def __init__(self):
        self.agent = FollowupAgent()

    async def analyze(
        self,
        message: str,
        memory: ConversationMemory
    ) -> FollowupAction:
        """分析追问类型并生成动作

        Args:
            message: 用户消息
            memory: 对话记忆

        Returns:
            追问动作
        """
        # 检查是否有历史结果
        if not memory.has_query_history():
            return FollowupAction(
                type="NEW_QUERY",
                reason="没有查询历史，按新查询处理"
            )

        # 检测追问类型
        followup_type = self._detect_followup_type(message)

        if followup_type == FollowupType.EXPLAIN:
            return FollowupAction(
                type="EXPLAIN",
                data=memory.last_result,
                context=memory.current_topic,
                last_query=memory.last_query
            )

        elif followup_type == FollowupType.DRILLDOWN:
            dimension = self._extract_dimension(message)
            return FollowupAction(
                type="DRILLDOWN",
                dimension=dimension,
                context=memory.current_topic,
                last_sql=memory.last_sql
            )

        elif followup_type == FollowupType.DETAIL:
            return FollowupAction(
                type="DETAIL",
                data=memory.last_result,
                context=memory.current_topic
            )

        # 默认按新查询处理
        return FollowupAction(
            type="NEW_QUERY",
            reason="无法识别为追问类型"
        )

    async def handle(self, action: FollowupAction, memory: ConversationMemory) -> str:
        """处理追问

        Args:
            action: 追问动作
            memory: 对话记忆

        Returns:
            回复内容
        """
        if action.type == "EXPLAIN":
            return await self.handle_explain(action, memory)
        elif action.type == "DETAIL":
            return self.handle_detail(action)
        elif action.type == "DRILLDOWN":
            return await self.handle_drilldown(action, memory)

        return "抱歉，我不太理解你的问题。"

    async def handle_explain(self, action: FollowupAction, memory: ConversationMemory) -> str:
        """处理解释型追问"""
        if not action.data:
            return "抱歉，没有可以分析的数据。"

        # 准备数据预览
        preview = self._prepare_data_preview(action.data)

        response = await self.agent.explain(
            message="为什么？",
            last_query=action.last_query or memory.last_query,
            data_preview=preview
        )

        memory.add_message("user", "为什么？")
        memory.add_message("assistant", response)

        return response

    def handle_detail(self, action: FollowupAction) -> str:
        """处理展开型追问"""
        if not action.data:
            return "抱歉，没有可以展开的数据。"

        # 展示更多数据
        lines = [f"以下是 **{action.context}** 的详细信息：\n"]

        # 只显示前20条
        for i, row in enumerate(action.data[:20], 1):
            lines.append(f"{i}. {row}")

        if len(action.data) > 20:
            lines.append(f"\n（还有 {len(action.data) - 20} 条数据未展示）")

        return "\n".join(lines)

    async def handle_drilldown(self, action: FollowupAction, memory: ConversationMemory) -> str:
        """处理下钻型追问"""
        if not action.dimension:
            return "请问要按哪个维度细分？（如：职业、教育程度、婚姻状况）"

        # 这里应该生成新的 SQL 并执行
        # 简化处理：返回提示信息
        return f"好的，我来按 **{action.dimension}** 细分分析 {action.context}。"

    def generate_drilldown_sql(self, action: FollowupAction, memory: ConversationMemory) -> str:
        """生成下钻 SQL"""
        dimension = action.dimension or "job"

        # 简化：在原 SQL 基础上添加 GROUP BY
        base_sql = memory.last_sql or "SELECT * FROM marketing_data"

        # 简单处理：生成新的统计 SQL
        sql = f"""
        SELECT {dimension}, COUNT(*) as count
        FROM marketing_data
        GROUP BY {dimension}
        ORDER BY count DESC
        LIMIT 20
        """.strip()

        return sql

    def _detect_followup_type(self, message: str) -> Optional[FollowupType]:
        """检测追问类型"""
        if any(word in message for word in ["为什么", "什么意思", "解释"]):
            return FollowupType.EXPLAIN

        if any(word in message for word in ["详细", "展开", "多说", "更多"]):
            return FollowupType.DETAIL

        if any(word in message for word in ["按", "细分", "分组"]):
            return FollowupType.DRILLDOWN

        return None

    def _extract_dimension(self, message: str) -> Optional[str]:
        """提取下钻维度"""
        dimensions = {
            "职业": "job",
            "job": "job",
            "教育": "education",
            "学历": "education",
            "婚姻": "marital",
            "年龄": "age",
        }

        for key, value in dimensions.items():
            if key in message:
                return value

        return None

    def _prepare_data_preview(self, data: list) -> str:
        """准备数据预览"""
        if not data:
            return "（无数据）"

        preview = json.dumps(data[:5], ensure_ascii=False, indent=2, default=str)

        if len(data) > 5:
            preview += f"\n...（还有 {len(data) - 5} 条）"

        return preview
```

- [ ] **Step 4: 运行测试验证通过**

运行:
```bash
cd backend && python -m pytest tests/graphs/test_followup.py -v
```
预期: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add backend/app/graphs/followup.py backend/app/graphs/agents/followup_agent.py backend/app/graphs/route_types.py backend/tests/graphs/test_followup.py
git commit -m "feat: 实现追问分析器"
```

---

## Task 6: 实现语气适配器

**Files:**
- Create: `backend/app/graphs/tone.py`
- Test: `backend/tests/graphs/test_tone.py`

- [ ] **Step 1: 写语气适配器测试**

创建 `backend/tests/graphs/test_tone.py`：

```python
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
```

- [ ] **Step 2: 运行测试验证失败**

运行:
```bash
cd backend && python -m pytest tests/graphs/test_tone.py -v
```
预期: FAIL - "ModuleNotFoundError"

- [ ] **Step 3: 实现语气适配器**

创建 `backend/app/graphs/tone.py`：

```python
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
```

- [ ] **Step 4: 运行测试验证通过**

运行:
```bash
cd backend && python -m pytest tests/graphs/test_tone.py -v
```
预期: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add backend/app/graphs/tone.py backend/tests/graphs/test_tone.py
git commit -m "feat: 实现语气适配器"
```

---

## Task 7: 实现两阶段工作流入口

**Files:**
- Create: `backend/app/graphs/two_stage_workflow.py`
- Create: `backend/app/graphs/memory_manager.py`
- Test: `backend/tests/graphs/test_two_stage_workflow.py`
- Modify: `backend/app/api/endpoints/chat_stream.py`

- [ ] **Step 1: 写工作流测试**

创建 `backend/tests/graphs/test_two_stage_workflow.py`：

```python
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

    assert any("CHAT" in str(r) for r in responses)
    assert any("answer" in str(r) for r in responses)


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

    # 应该包含 QUERY 意图
    assert any("QUERY" in r for r in responses)


@pytest.mark.asyncio
async def test_followup_route():
    """测试追问路由"""
    workflow = TwoStageWorkflow()

    # 先执行查询
    async for _ in workflow.process(
        message="查询30岁以下的客户",
        session_id="test_session3",
        user_id="test_user"
    ):
        pass

    # 再追问
    responses = []
    async for chunk in workflow.process(
        message="为什么？",
        session_id="test_session3",  # 同一个 session
        user_id="test_user"
    ):
        responses.append(str(chunk))

    assert any("FOLLOWUP" in r for r in responses)
```

- [ ] **Step 2: 运行测试验证失败**

运行:
```bash
cd backend && python -m pytest tests/graphs/test_two_stage_workflow.py -v
```
预期: FAIL - "ModuleNotFoundError"

- [ ] **Step 3: 实现记忆管理器**

创建 `backend/app/graphs/memory_manager.py`：

```python
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
```

- [ ] **Step 4: 实现两阶段工作流**

创建 `backend/app/graphs/two_stage_workflow.py`：

```python
"""两阶段对话工作流

第一阶段路由，第二阶段分发处理
"""
import json
from typing import AsyncGenerator

from app.graphs.router import ConversationRouter
from app.graphs.memory import ConversationMemory
from app.graphs.memory_manager import MemoryManager
from app.graphs.chat_handler import ChatHandler
from app.graphs.followup import FollowupAnalyzer
from app.graphs.tone import ToneAdapter
from app.graphs.workflow import agent_app  # 现有工作流
from app.graphs.state import create_initial_state


class StreamEvent:
    """流式事件（复用现有定义）"""

    @staticmethod
    def intent(route_type: str) -> str:
        return f"data: {json.dumps({'type': 'intent', 'route_type': route_type}, ensure_ascii=False)}\n\n"

    @staticmethod
    def thinking(message: str) -> str:
        return f"data: {json.dumps({'type': 'thinking', 'message': message}, ensure_ascii=False)}\n\n"

    @staticmethod
    def text(content: str) -> str:
        return f"data: {json.dumps({'type': 'text', 'content': content}, ensure_ascii=False)}\n\n"

    @staticmethod
    def answer(content: str) -> str:
        return f"data: {json.dumps({'type': 'answer', 'content': content}, ensure_ascii=False)}\n\n"

    @staticmethod
    def error(message: str) -> str:
        return f"data: {json.dumps({'type': 'error', 'message': message}, ensure_ascii=False)}\n\n"

    @staticmethod
    def done() -> str:
        return f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"


class TwoStageWorkflow:
    """两阶段对话工作流

    流程：
    1. 路由决策
    2. 分发处理（闲聊/查询/追问）
    3. 语气适配
    4. 返回结果
    """

    def __init__(self):
        self.router = ConversationRouter()
        self.chat_handler = ChatHandler()
        self.followup_analyzer = FollowupAnalyzer()
        self.tone_adapter = ToneAdapter()
        self.memory_manager = MemoryManager()

    async def process(
        self,
        message: str,
        session_id: str,
        user_id: str = "default"
    ) -> AsyncGenerator[str, None]:
        """处理用户消息

        Args:
            message: 用户消息
            session_id: 会话 ID
            user_id: 用户 ID

        Yields:
            SSE 格式的事件字符串
        """
        try:
            # 1. 加载记忆
            memory = await self.memory_manager.get_or_create(session_id, user_id)

            # 2. 路由决策
            decision = await self.router.route(message, memory)
            yield StreamEvent.intent(decision.route_type.value)

            # 3. 分发处理
            if decision.route_type.value == "chat":
                async for chunk in self._handle_chat(message, memory):
                    yield chunk

            elif decision.route_type.value == "followup":
                async for chunk in self._handle_followup(message, memory):
                    yield chunk

            else:  # query or correction
                async for chunk in self._handle_query(message, memory, decision):
                    yield chunk

            # 4. 更新记忆
            await self.memory_manager.update(memory)

            yield StreamEvent.done()

        except Exception as e:
            yield StreamEvent.error(f"处理出错: {str(e)}")
            yield StreamEvent.done()

    async def _handle_chat(
        self,
        message: str,
        memory: ConversationMemory
    ) -> AsyncGenerator[str, None]:
        """处理闲聊"""
        yield StreamEvent.thinking("正在回复...")

        response = await self.chat_handler.chat(message, memory)
        adapted = self.tone_adapter.adapt(response, memory.last_intent or "chat")

        yield StreamEvent.answer(adapted)

    async def _handle_followup(
        self,
        message: str,
        memory: ConversationMemory
    ) -> AsyncGenerator[str, None]:
        """处理追问"""
        yield StreamEvent.thinking("正在分析...")

        action = await self.followup_analyzer.analyze(message, memory)

        if action.type == "NEW_QUERY":
            # 当新查询处理
            async for chunk in self._handle_query(message, memory, None):
                yield chunk
        else:
            response = await self.followup_analyzer.handle(action, memory)
            adapted = self.tone_adapter.adapt(response, memory.last_intent or "followup")

            yield StreamEvent.answer(adapted)

    async def _handle_query(
        self,
        message: str,
        memory: ConversationMemory,
        decision
    ) -> AsyncGenerator[str, None]:
        """处理数据查询"""
        yield StreamEvent.thinking("正在查询...")

        # 构建初始状态
        initial_state = create_initial_state(
            user_input=message,
            chat_history=memory.messages
        )

        config = {
            "configurable": {
                "thread_id": memory.session_id,
                "user_id": memory.user_id,
            }
        }

        # 执行现有工作流
        final_state = await agent_app.ainvoke(initial_state, config=config)

        # 更新记忆
        if final_state.get("sql_result"):
            memory.update_after_query(
                query=message,
                sql=final_state.get("generated_sql", ""),
                result=final_state["sql_result"],
                intent=final_state.get("intent", "query")
            )

        # 适配语气
        answer = final_state.get("final_answer", "抱歉，没有生成回答。")
        adapted = self.tone_adapter.adapt(
            answer,
            final_state.get("intent", "query"),
            has_data=bool(final_state.get("sql_result"))
        )

        yield StreamEvent.answer(adapted)


# 全局实例
two_stage_workflow = TwoStageWorkflow()
```

- [ ] **Step 5: 修改 chat_stream.py 使用新工作流**

修改 `backend/app/api/endpoints/chat_stream.py`，在 imports 后添加：

```python
from app.graphs.two_stage_workflow import two_stage_workflow
```

然后修改 `stream_chat_response_enhanced` 函数（约第95行）：

```python
async def stream_chat_response_enhanced(
    message: str,
    session_id: str,
    user_id: str = _DEFAULT_USER_ID,
    chat_history: List[Dict] = None,
) -> AsyncGenerator[str, None]:
    """增强的流式生成聊天响应（使用两阶段工作流）"""
    # 直接使用两阶段工作流
    async for event in two_stage_workflow.process(
        message=message,
        session_id=session_id,
        user_id=user_id
    ):
        yield event
```

- [ ] **Step 6: 运行测试验证通过**

运行:
```bash
cd backend && python -m pytest tests/graphs/test_two_stage_workflow.py -v
```
预期: PASS (3 passed)

- [ ] **Step 7: Commit**

```bash
git add backend/app/graphs/two_stage_workflow.py backend/app/graphs/memory_manager.py backend/app/api/endpoints/chat_stream.py backend/tests/graphs/test_two_stage_workflow.py
git commit -m "feat: 实现两阶段工作流入口并集成到 API"
```

---

## Task 8: 端到端测试和文档

**Files:**
- Create: `backend/tests/integration/test_conversation_e2e.py`
- Modify: `docs/superpowers/specs/2026-03-19-two-stage-conversation-design.md`

- [ ] **Step 1: 创建端到端测试**

创建 `backend/tests/integration/test_conversation_e2e.py`：

```python
"""端到端对话测试"""
import pytest
from app.graphs.two_stage_workflow import two_stage_workflow


@pytest.mark.asyncio
async def test_full_conversation_flow():
    """测试完整对话流程"""
    session_id = "e2e_test_session"

    # 1. 问候
    responses = []
    async for chunk in two_stage_workflow.process(
        message="你好",
        session_id=session_id,
        user_id="test_user"
    ):
        responses.append(chunk)

    assert any("你好" in r or "嗨" in r for r in responses)

    # 2. 查询
    responses = []
    async for chunk in two_stage_workflow.process(
        message="查询30岁以下的客户",
        session_id=session_id,
        user_id="test_user"
    ):
        responses.append(chunk)

    assert any("QUERY" in r for r in responses)

    # 3. 追问
    responses = []
    async for chunk in two_stage_workflow.process(
        message="为什么？",
        session_id=session_id,
        user_id="test_user"
    ):
        responses.append(chunk)

    assert any("FOLLOWUP" in r or "answer" in r for r in responses)
```

- [ ] **Step 2: 运行端到端测试**

运行:
```bash
cd backend && python -m pytest tests/integration/test_conversation_e2e.py -v
```
预期: PASS (1 passed)

- [ ] **Step 3: 更新设计文档状态**

在 `docs/superpowers/specs/2026-03-19-two-stage-conversation-design.md` 开头修改状态：

```markdown
**日期**: 2026-03-19
**作者**: Claude
**状态**: ✅ 已实现
```

- [ ] **Step 4: Commit**

```bash
git add backend/tests/integration/test_conversation_e2e.py docs/superpowers/specs/2026-03-19-two-stage-conversation-design.md
git commit -m "test: 添加端到端测试并更新设计文档状态"
```

---

## 测试检查清单

实现完成后，运行全部测试：

```bash
cd backend && python -m pytest tests/graphs/ tests/integration/test_conversation_e2e.py -v
```

预期：所有测试通过

---

## 使用示例

实现后可以这样测试：

```python
from app.graphs.two_stage_workflow import two_stage_workflow

# 闲聊
async for chunk in two_stage_workflow.process("你好", "session1", "user1"):
    print(chunk)

# 查询
async for chunk in two_stage_workflow.process("查询30岁以下客户", "session1", "user1"):
    print(chunk)

# 追问
async for chunk in two_stage_workflow.process("为什么转化率低？", "session1", "user1"):
    print(chunk)
```

---

**总任务数**: 8
**预计时间**: 2-3 小时
**文件变更**: 15 个新增，2 个修改
