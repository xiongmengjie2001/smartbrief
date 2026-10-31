# SmartBrief · 多智能体报告生成平台

基于 **LangGraph + LangChain 1.0** 构建的多智能体协作系统：输入一个研究主题，自动完成「拆计划 → 联网检索 → 撰写草稿 → 多轮审核返工 → 输出报告」全流程，并内置**自动化评测体系**量化报告质量。

## 核心能力

- **Plan-and-Execute 编排**：Planner 自动拆解研究步骤，Scheduler 按依赖派发任务
- **ReAct Researcher**：多轮联网检索，自动调整搜索策略直到拿到可用数据
- **A2A 审核循环**：Reviewer 按质量标准审核草稿，不通过则 Rewriter 按意见返工，最多 3 轮后强制通过
- **RAG 知识库**：ChromaDB 向量库 + bge-m3 嵌入，Writer 撰写时自动注入相关术语
- **长期记忆**：历史报告自动入库，下次相似任务 Planner 自动召回做 Few-shot
- **短期记忆（断点续跑）**：LangGraph Checkpointer + SqliteSaver，服务中断后任务自动暂停，可一键从断点恢复
- **自动化评测体系**：固定用例批量执行，五维指标（成功率 / 平均耗时 / P95 / ReAct 循环次数 / 关键词覆盖率 / 记忆命中率）目标值判定，ECharts 雷达图 + Markdown 评测报告，结果落库支持历史对比；评测中断自动标记失败，可重新触发
- **报告中心**：已生成报告列表（主题搜索 / 时间排序 / 分页），报告展示页 Markdown 渲染 + 执行摘要（总耗时 / ReAct 次数 / 记忆命中），支持导出 Word / PDF
- **MCP 工具协议**：内置 web_search MCP Server（stdio 传输），支持自定义 MCP Server（Streamable HTTP / SSE）
- **技能池**：BaseSkill 抽象层，支持内置技能 + 自定义技能（表单创建 / .zip 导入 / 试运行）
- **全栈界面**：Vue 3 + Element Plus + Vite，含任务提交、任务列表、任务详情（Plan 看板 + ReAct 日志 + 审核过程可视化）、评测中心、报告中心、知识库管理、AI 对话、工具监控、技能中心

## 技术栈

| 层 | 技术 |
| ---- | ---- |
| 后端 | Python 3.10+ / FastAPI / LangChain 1.0 / LangGraph 1.0 / sqlite3 |
| 向量库 | ChromaDB + SiliconFlow bge-m3 |
| 记忆 | langgraph-checkpoint-sqlite（短期）+ ChromaDB memory_collection（长期） |
| 工具协议 | MCP（FastMCP Server + ClientSession） |
| 前端 | Vue 3 + TypeScript + Vite + Element Plus + Axios + Vue Router + ECharts |
| 部署 | Docker Compose（前后端镜像 + nginx 反向代理） |

## 架构图

```
用户输入主题
    ↓
Planner（拆计划，召回长期记忆做 Few-shot）
    ↓
Scheduler（按依赖派发步骤）
    ├── ReAct Researcher（联网检索，最多 3 轮 Thought→Action→Observation）
    └── ReAct Writer（基于检索数据撰写草稿，RAG 术语注入）
    ↓
Reviewer（按 3 条标准审核：≥2 数据点 / 引用来源 / ≥1000 字）
    ├── passed → END
    └── not passed → Rewriter（按意见返工）→ 回到 Reviewer（最多 3 轮）
    ↓
输出报告（导出 Word / PDF）+ 长期记忆入库

评测引擎（独立入口）：批量执行固定用例 → 五维指标计算 → 雷达图 + 报告落库
```

## 快速启动

### 1. 配置环境变量

```bash
cd backend
cp .env.example .env
```

编辑 `.env`，填入 OpenAI 兼容接口的 API Key（支持 DeepSeek / Kimi / Ollama 等）：

```ini
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_API_KEY=sk-你的key
OPENAI_MODEL=deepseek-flash

# 可选：RAG 嵌入模型（不配置则知识库为空但不影响主流程）
EMBEDDING_BASE_URL=https://api.siliconflow.cn/v1
EMBEDDING_API_KEY=sk-你的key
EMBEDDING_MODEL=BAAI/bge-m3
```

### 2. 启动后端（端口 8002）

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
```

验证：访问 <http://localhost:8002/api/v1/health> 返回 `{"status":"ok"}`

### 3. 启动前端（端口 5174）

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 <http://localhost:5174>

### 4. 一键启动（可选）

Windows 双击 `start.bat`，Linux / Mac 执行 `start.sh`，同时拉起前后端。

## Docker 部署

`deploy/` 目录提供完整的容器化方案：前后端 Dockerfile、`docker-compose.yml`（本地）与 `docker-compose.prod.yml`（生产）、nginx 配置与部署脚本。

```bash
cd deploy
cp .env.example .env   # 填入 API Key
docker compose up -d --build
```

## 目录结构

```
smartbrief/
├── backend/
│   ├── agents/             # Planner / Scheduler / ReAct Researcher / ReAct Writer / Reviewer / Rewriter
│   ├── graph/              # LangGraph 状态图（state.py + workflow.py）
│   ├── evaluation/         # 自动化评测引擎（runner 批量执行 + metrics 五维指标）
│   ├── memory/             # Checkpointer（短期）+ long_term_memory（长期）
│   ├── rag/                # embeddings / loaders / chunkers / vectorstores / store
│   ├── mcp_client/         # MCP 客户端（stdio / HTTP / SSE）
│   ├── skills/             # 技能池（BaseSkill 抽象层 + Registry + Manager）
│   ├── tools/              # 内置工具（current_time / calculator）
│   ├── api/                # FastAPI 路由
│   ├── db/                 # SQLite 业务库（tasks / task_logs / evaluation_reports）
│   ├── llm/                # OpenAI 兼容客户端
│   ├── tests/              # pytest 测试
│   └── main.py             # FastAPI 入口
├── mcp_servers/
│   └── web_search_server.py    # 内置 MCP Server（web_search）
├── frontend/
│   ├── src/
│   │   ├── views/          # Home / Tasks / TaskDetail / Evaluation / Reports / ReportView
│   │   │                   # KnowledgeBase / Chat / ToolMonitor / SkillCenter
│   │   ├── api/            # Axios 封装
│   │   └── router/
│   └── package.json
├── deploy/                 # Docker Compose 部署（前后端 Dockerfile + nginx）
└── README.md
```

## API 概览

| 方法 | 路径 | 功能 |
| ---- | ---- | ---- |
| POST | /api/v1/generate | 提交研究任务 |
| GET | /api/v1/tasks | 任务列表（分页 + 状态过滤 + 主题搜索 + 时间排序） |
| GET | /api/v1/tasks/{id}/status | 任务详情（含 Plan / ReAct 日志 / 审核结果 / 记忆命中） |
| POST | /api/v1/tasks/{id}/resume | 断点续跑 |
| GET | /api/v1/tasks/{id}/report | 任务报告（Markdown + 执行摘要） |
| POST | /api/v1/evaluation/run | 触发自动化评测（后台执行，并发保护） |
| GET | /api/v1/evaluation/reports | 历史评测报告列表 |
| GET | /api/v1/evaluation/reports/{id} | 评测进度 / 完整结果（指标 + Markdown 报告） |
| POST | /api/v1/chat | 单智能体对话（工具调用闭环） |
| GET | /api/v1/knowledge/documents | RAG 知识库文档列表 |
| POST | /api/v1/knowledge/documents | 上传文档入库 |
| POST | /api/v1/knowledge/search | RAG 语义检索 |
| GET | /api/v1/memory/search | 长期记忆检索 |
| GET | /api/v1/memory/status | 长期记忆开关状态 |
| POST | /api/v1/memory/toggle | 开关长期记忆 |

## 许可

MIT
