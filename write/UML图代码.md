# BankAgent-Pro 论文UML图代码

> 以下代码可以复制到 https://mermaid.live/ 或 https://plantuml.com/ 在线渲染

---

## 1. 系统总体架构图

```mermaid
graph TB
    subgraph "表现层 Presentation Layer"
        A1[Vue3 前端应用]
        A2[Element Plus UI组件]
        A3[ECharts 图表渲染]
    end

    subgraph "API网关层 API Gateway"
        B1[FastAPI 路由]
        B2[JWT 认证中间件]
        B3[请求日志]
    end

    subgraph "业务逻辑层 Business Logic Layer"
        C1[用户认证服务]
        C2[LangGraph 智能体工作流]
        C3[数据分析服务]
        C4[RAG 知识库服务]
        C5[可视化服务]
    end

    subgraph "AI智能体层 AI Agent Layer"
        D1[意图识别节点]
        D2[Text-to-SQL节点]
        D3[SQL执行节点]
        D4[数据分析节点]
        D5[RAG检索节点]
        D6[答案生成节点]
    end

    subgraph "数据层 Data Layer"
        E1[(PostgreSQL 数据库)]
        E2[(pgvector 向量库)]
        E3[GLM-4 API]
        E4[Scikit-learn 模型]
    end

    A1 --> B1
    A2 --> B1
    A3 --> B1
    B1 --> B2
    B2 --> C1
    B2 --> C2
    B2 --> C3
    B2 --> C4
    B2 --> C5

    C2 --> D1
    D1 --> D2
    D1 --> D4
    D1 --> D5
    D2 --> D3
    D3 --> D6
    D4 --> D6
    D5 --> D6

    D2 --> E1
    D3 --> E1
    D4 --> E4
    D5 --> E2
    D2 --> E3
    D6 --> E3
    C1 --> E1
    C4 --> E2
```

---

## 2. LangGraph智能体工作流图

```mermaid
stateDiagram-v2
    [*] --> 用户输入

    用户输入 --> 意图识别节点

    意图识别节点 --> 数据查询: query类型
    意图识别节点 --> 统计分析: stats类型
    意图识别节点 --> 知识问答: chat类型
    意图识别节点 --> 可视化展示: viz类型

    state 数据查询 {
        [*] --> Text_to_SQL
        Text_to_SQL --> SQL执行
        SQL执行 --> 结果返回
    }

    state 统计分析 {
        [*] --> 选择分析类型
        选择分析类型 --> 聚类分析
        选择分析类型 --> 相关性分析
        选择分析类型 --> 描述性统计
        聚类分析 --> 结果返回
        相关性分析 --> 结果返回
        描述性统计 --> 结果返回
    }

    state 知识问答 {
        [*] --> 向量检索
        向量检索 --> RAG生成
        RAG生成 --> 结果返回
    }

    state 可视化展示 {
        [*] --> 选择图表类型
        选择图表类型 --> 生成图表
        生成图表 --> 结果返回
    }

    数据查询 --> 答案生成
    统计分析 --> 答案生成
    知识问答 --> 答案生成
    可视化展示 --> 答案生成

    答案生成 --> [*]
```

---

## 3. 系统用例图

```mermaid
graph TB
    subgraph "普通用户 User"
        U1(登录/注册)
        U2(智能对话查询)
        U3(数据查询)
        U4(统计分析)
        U5(可视化查看)
        U6(知识库问答)
    end

    subgraph "管理员 Admin"
        A1(用户管理)
        A2(知识库管理)
        A3(数据管理)
        A4(日志查看)
    end

    subgraph "系统功能"
        S1[用户认证模块]
        S2[智能对话模块]
        S3[Text-to-SQL模块]
        S4[数据分析模块]
        S5[可视化模块]
        S6[RAG知识库模块]
    end

    U1 --> S1
    U2 --> S2
    U3 --> S3
    U4 --> S4
    U5 --> S5
    U6 --> S6

    A1 --> S1
    A2 --> S6
    A3 --> S3
    A4 --> S2
```

---

## 4. 数据库E-R图

```mermaid
erDiagram
    USERS ||--o{ MARKETING_DATA : owns
    USERS ||--o{ KNOWLEDGE_DOCS : uploads
    USERS ||--o{ OPERATION_LOGS : generates

    USERS {
        int id PK
        string employee_id UK
        string name
        string department
        string hashed_password
        string role
        boolean is_active
        datetime created_at
    }

    MARKETING_DATA {
        int id PK
        int age
        string job
        string marital
        string education
        float balance
        boolean housing
        boolean loan
        string contact
        int duration
        int campaign
        int pdays
        string poutcome
        boolean y
    }

    KNOWLEDGE_DOCS {
        int id PK
        string title
        text content
        string file_path
        string file_type
        vector embedding
        json meta_data
        int uploaded_by FK
        datetime created_at
    }

    OPERATION_LOGS {
        int id PK
        int user_id FK
        string action
        string resource
        string ip_address
        json details
        datetime created_at
    }
```

---

## 5. 核心类图

```mermaid
classDiagram
    class User {
        +int id
        +str employee_id
        +str name
        +str department
        +str hashed_password
        +str role
        +bool is_active
        +verify_password() bool
    }

    class LangGraphAgent {
        +State state
        +Graph workflow
        +create_graph() void
        +invoke(message) Response
        +stream(message) Iterator
    }

    class IntentParser {
        +llm: BaseLanguageModel
        +parse_intent(query) str
        +extract_entities(query) dict
    }

    class TextToSQL {
        +llm: BaseLanguageModel
        +schema: dict
        +generate_sql(query, schema) str
        +validate_sql(sql) bool
    }

    class RAGService {
        +vector_store: PGVector
        +embeddings: Embeddings
        +upload_doc(file) void
        +search(query, k) list
        +generate_answer(query, context) str
    }

    class AnalysisService {
        +df: DataFrame
        +descriptive_stats() dict
        +cluster(data, k) dict
        +correlation(data) dict
    }

    class VisualizationService {
        +generate_chart(data, type) str
        +to_html(chart) str
    }

    User --> LangGraphAgent : 使用
    LangGraphAgent --> IntentParser : 包含
    LangGraphAgent --> TextToSQL : 包含
    LangGraphAgent --> RAGService : 包含
    LangGraphAgent --> AnalysisService : 包含
    LangGraphAgent --> VisualizationService : 包含
```

---

## 6. 数据处理流程图

```mermaid
flowchart TD
    A[原始银行营销数据] --> B[数据加载]
    B --> C{缺失值检查}
    C -->|有缺失| D[均值/众数填充]
    C -->|无缺失| E[异常值检测]
    D --> E
    E -->|有异常| F[剔除/修正]
    E -->|无异常| G[数据类型转换]
    F --> G
    G --> H[特征工程]
    H --> I[数据存储]
    I --> J[分析建模]
```

---

## 7. Text-to-SQL处理流程图

```mermaid
flowchart TD
    A[用户自然语言输入] --> B[意图识别]
    B --> C{是否为数据查询}
    C -->|否| Z[其他处理流程]
    C -->|是| D[提取查询要素]
    D --> E[加载数据库Schema]
    E --> F[构建Few-Shot提示]
    F --> G[调用LLM生成SQL]
    G --> H[SQL安全校验]
    H -->|不安全| I[拒绝执行]
    H -->|安全| J[执行SQL查询]
    J --> K[格式化结果]
    K --> L[生成自然语言回答]
    I --> L
```

---

## 8. RAG检索增强生成流程图

```mermaid
flowchart LR
    subgraph "文档处理阶段"
        A[上传PDF/TXT文档] --> B[文档分块]
        B --> C[文本向量化]
        C --> D[存储到pgvector]
    end

    subgraph "查询阶段"
        E[用户问题] --> F[问题向量化]
        F --> G[相似度检索]
        G --> H[获取Top-K相关片段]
    end

    subgraph "生成阶段"
        H --> I[构建提示词]
        I --> J[调用LLM生成回答]
        J --> K[返回最终答案]
    end
```

---

## 9. 系统部署架构图

```mermaid
graph TB
    subgraph "客户端层"
        U[浏览器]
    end

    subgraph "Web服务器层"
        N[Nginx 反向代理]
    end

    subgraph "应用服务器层"
        A1[FastAPI 应用1]
        A2[FastAPI 应用2]
        A3[FastAPI 应用3]
    end

    subgraph "数据层"
        D1[(PostgreSQL 主库)]
        D2[(PostgreSQL 从库)]
        R[Redis 缓存]
    end

    subgraph "外部服务"
        E[GLM-4 API]
    end

    U --> N
    N --> A1
    N --> A2
    N --> A3
    A1 --> D1
    A2 --> D1
    A3 --> D1
    A1 --> D2
    A2 --> D2
    A3 --> D2
    A1 --> R
    A2 --> R
    A3 --> R
    A1 --> E
    A2 --> E
    A3 --> E
    D1 --> D2
```

---

## 使用说明

### Mermaid在线渲染
1. 访问 https://mermaid.live/
2. 将代码复制到左侧编辑框
3. 右侧实时预览效果
4. 点击 Download PNG 下载图片

### PlantUML在线渲染
1. 访问 http://www.plantuml.com/plantuml/uml/
2. 将代码复制到输入框
3. 点击 Submit 生成图片

### 论文中插入图片
1. 生成PNG格式图片
2. 在Word中使用"插入 -> 图片"
3. 添加图注，如"图4-1 系统总体架构图"
