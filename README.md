# 掌柜智库 Smart Agent System

基于 **FastAPI + LangGraph + Milvus + Neo4j + MongoDB + DashScope LLM** 的智能问答与知识库导入系统。

本项目面向 **B 端产品客服 / 产品知识库问答** 场景：

- **文件导入服务**：上传 PDF/Markdown 文档，解析、切片、识别产品名、向量化后写入 Milvus。
- **智能问答服务**：识别用户问题中的产品型号，结合向量检索、HyDE、知识图谱、网络搜索、RRF 融合、Rerank 和 LLM 生成回答。
- **数据管理工具**：使用 Attu 管理 Milvus，使用 MongoDB Compass 查看聊天历史。

> **安全提醒**：`docker-compose.yml` 中使用的是本地开发默认密码，例如 Neo4j `neo4j/123123123`、MongoDB `kbadmin/kbadmin123`。这些密码仅适合本地开发环境。部署到服务器或公网环境前，请务必修改密码并限制端口访问。

---

## 目录

- [一、项目能力](#一项目能力)
- [二、技术架构](#二技术架构)
- [三、环境要求](#三环境要求)
- [四、首次部署](#四首次部署)
- [五、日常启动](#五日常启动)
- [六、访问入口](#六访问入口)
- [七、MongoDB Compass 使用指南](#七mongodb-compass-使用指南)
- [八、常用运维命令](#八常用运维命令)
- [九、目录结构](#九目录结构)
- [十、常见问题](#十常见问题)
- [十一、技术栈速查](#十一技术栈速查)
- [十二、当前部署状态记录](#十二当前部署状态记录)

---

## 一、项目能力

### 1.1 文件导入

导入链路：

```text
上传 PDF / Markdown
  → 本地保存
  → 上传到 MinIO
  → PDF 转 Markdown
  → 图片摘要
  → 文档切片
  → 产品名识别
  → BGE-M3 向量化
  → 写入 Milvus
```

对应入口：

- 页面：<http://localhost:8000/import.html>
- API 文档：<http://localhost:8000/docs>
- 入口文件：`app/import_process/api/file_import_service.py`
- 编排文件：`app/import_process/agent/main_graph.py`

### 1.2 智能问答

问答链路：

```text
用户提问
  → 识别产品型号
  → 确认 / 对齐产品名
  → Milvus 混合检索
  → HyDE 检索
  → Neo4j 图谱查询
  → DashScope MCP 网络搜索
  → RRF 多路融合
  → BGE Reranker 重排
  → LLM 生成答案
  → MongoDB 保存聊天记录
```

对应入口：

- 页面：<http://localhost:8001/chat.html>
- API 文档：<http://localhost:8001/docs>
- 入口文件：`app/query_process/api/query_service.py`
- 编排文件：`app/query_process/agent/main_graph.py`

### 1.3 问答系统的限制

本系统不是通用聊天机器人，而是产品知识库问答系统。

如果用户输入：

```text
你好
```

系统可能返回：

```text
抱歉，未找到相关产品，请提供准确型号以便我为您查询。
```

这是当前设计行为。原因是 `node_item_name_confirm` 节点要求先识别产品型号。如果没有识别到产品名，就不会进入完整 RAG 流程，也不会调用 LLM 做闲聊。

推荐提问方式：

```text
RS-12数字万用表怎么使用？
RS-12数字万用表的测量范围是多少？
```

---

## 二、技术架构

### 2.1 总体架构

```text
浏览器页面
  ├── import.html  → import_service:8000
  └── chat.html    → query_service:8001

FastAPI 服务
  ├── 导入流程：LangGraph ImportGraph
  └── 查询流程：LangGraph QueryGraph

本地 Docker 依赖
  ├── Milvus      向量数据库
  ├── etcd        Milvus 元数据
  ├── MinIO       Milvus 内部对象存储
  ├── Neo4j       图数据库
  ├── MongoDB     聊天历史
  └── Attu        Milvus Web 管理工具

远程服务
  ├── DashScope LLM
  ├── DashScope MCP WebSearch
  └── 业务 MinIO：47.94.86.115:9000
```

### 2.2 本地服务端口

| 端口 | 服务 | 说明 |
|------|------|------|
| `8000` | import_service | 文件导入服务 |
| `8001` | query_service | 智能问答服务 |
| `8002` | Attu | Milvus Web 管理工具 |
| `19530` | Milvus | Milvus gRPC |
| `9091` | Milvus HTTP | Milvus 健康检查 / Metrics |
| `7474` | Neo4j Browser | Neo4j Web 控制台 |
| `7687` | Neo4j Bolt | Neo4j 驱动连接端口 |
| `27017` | MongoDB | 本地聊天历史数据库 |

---

## 三、环境要求

| 组件 | 要求 | 说明 |
|------|------|------|
| Windows | Windows 10 / 11 x64 | 当前项目在 Windows 环境验证 |
| Python | 3.11+ | 推荐 Python 3.11 |
| uv | 0.11+ | Python 包管理工具 |
| Docker Desktop | 4.x+ | 用于运行 Milvus、Neo4j、MongoDB、Attu |
| 磁盘空间 | 15GB+ | 模型、镜像、依赖和数据 |
| 内存 | 16GB+ | Milvus + 本地模型推荐配置 |

### 3.1 推荐模型路径

| 模型 | 路径 |
|------|------|
| BGE-M3 | `D:\ai_models\modelscope_cache\models\BAAI\bge-m3` |
| BGE Reranker Large | `D:\ai_models\modelscope_cache\models\rerank\BAAI\bge-reranker-large` |

---

## 四、首次部署

### 4.1 进入项目目录

```powershell
Set-Location "D:\windsuf project\smart_agent_system"
```

### 4.2 安装 Python 依赖

```powershell
uv sync
```

如果国内网络下载慢，可以使用镜像源：

```powershell
uv sync --default-index https://mirrors.aliyun.com/pypi/simple/ --index-strategy unsafe-best-match
```

### 4.3 配置环境变量

复制模板：

```powershell
Copy-Item .env.example .env
```

重点检查 `.env` 中这些配置：

```ini
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_DEFAULT_MODEL=qwen-flash

BGE_M3_PATH=D:\ai_models\modelscope_cache\models\BAAI\bge-m3
BGE_RERANKER_LARGE=D:\ai_models\modelscope_cache\models\rerank\BAAI\bge-reranker-large

MILVUS_URL=http://localhost:19530

NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=123123123

MONGO_URL=mongodb://kbadmin:kbadmin123@localhost:27017/?authSource=admin
MONGO_DB_NAME=kb002

MINIO_ENDPOINT=47.94.86.115:9000
```

> `OPENAI_API_KEY`、`DASHSCOPE_API_KEY`、MinIO 账号密码请使用你自己的有效配置，不要把真实密钥提交到 GitHub。

### 4.4 启动 Docker Desktop

手动打开 Docker Desktop，等待右下角小鲸鱼图标稳定。

也可以用命令：

```powershell
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

### 4.5 启动本地依赖容器

```powershell
docker compose up -d
```

查看状态：

```powershell
docker compose ps
```

期望看到 6 个容器运行：

```text
smart-agent-etcd
smart-agent-milvus-minio
smart-agent-milvus
smart-agent-neo4j
smart-agent-mongo
smart-agent-attu
```

Milvus 首次启动可能需要 30-60 秒健康检查。Attu 依赖 Milvus 健康后再启动，如果短时间内处于 `Created` 或 `Waiting` 属于正常情况。

### 4.6 启动查询服务

新开一个 PowerShell 窗口：

```powershell
Set-Location "D:\windsuf project\smart_agent_system"
uv run uvicorn app.query_process.api.query_service:app --host 0.0.0.0 --port 8001
```

### 4.7 启动文件导入服务

再开一个 PowerShell 窗口：

```powershell
Set-Location "D:\windsuf project\smart_agent_system"
uv run uvicorn app.import_process.api.file_import_service:app --host 0.0.0.0 --port 8000
```

---

## 五、日常启动

每次开机后按顺序执行：

### 5.1 启动 Docker Desktop

确保 Docker Desktop 已运行。

### 5.2 启动容器

```powershell
Set-Location "D:\windsuf project\smart_agent_system"
docker compose up -d
docker compose ps
```

### 5.3 启动 query_service

```powershell
Set-Location "D:\windsuf project\smart_agent_system"
uv run uvicorn app.query_process.api.query_service:app --host 0.0.0.0 --port 8001
```

### 5.4 启动 import_service

```powershell
Set-Location "D:\windsuf project\smart_agent_system"
uv run uvicorn app.import_process.api.file_import_service:app --host 0.0.0.0 --port 8000
```

> 运行 FastAPI 的两个 PowerShell 窗口不能关闭，关闭窗口服务就会停止。

---

## 六、访问入口

### 6.1 业务页面

| 用途 | 地址 | 说明 |
|------|------|------|
| 智能问答页 | <http://localhost:8001/chat.html> | 用户提问入口 |
| 文件导入页 | <http://localhost:8000/import.html> | 上传 PDF / Markdown |
| Query API 文档 | <http://localhost:8001/docs> | FastAPI Swagger |
| Import API 文档 | <http://localhost:8000/docs> | FastAPI Swagger |
| Query 健康检查 | <http://localhost:8001/health> | 返回服务健康状态 |

### 6.2 数据库管理工具

| 数据库 | 工具 | 入口 / 连接串 | 账密 |
|--------|------|----------------|------|
| Milvus | Attu | <http://localhost:8002> | 无，连接 `smart-agent-milvus:19530` |
| Neo4j | Neo4j Browser | <http://localhost:7474> | `neo4j` / `123123123` |
| MongoDB | MongoDB Compass | `mongodb://kbadmin:kbadmin123@localhost:27017/?authSource=admin` | `kbadmin` / `kbadmin123` |
| 业务 MinIO | MinIO Console | <http://47.94.86.115:9001> | 见 `.env` |

### 6.3 健康检查

| 服务 | 地址 |
|------|------|
| Milvus | <http://localhost:9091/healthz> |
| Attu | <http://localhost:8002> |
| Query Service | <http://localhost:8001/health> |

---

## 七、MongoDB Compass 使用指南

### 7.1 下载安装

官方下载地址：<https://www.mongodb.com/try/download/compass>

Windows 选择 `.exe` 安装版即可。

### 7.2 首次连接

打开 Compass，点击 `New Connection`，URI 填：

```text
mongodb://kbadmin:kbadmin123@localhost:27017/?authSource=admin
```

然后点击 `Connect`。

URI 含义：

| 片段 | 含义 |
|------|------|
| `kbadmin` | MongoDB 用户名 |
| `kbadmin123` | MongoDB 密码 |
| `localhost:27017` | 本地 Docker 暴露的 MongoDB 地址 |
| `authSource=admin` | 到 `admin` 库验证用户，必须保留 |

### 7.3 查看聊天记录

连接成功后进入：

```text
kb002 → chat_message → Documents
```

常见字段：

| 字段 | 含义 |
|------|------|
| `_id` | MongoDB 文档 ID |
| `session_id` | 当前浏览器会话 ID |
| `role` | `user` 或 `assistant` |
| `text` | 消息内容 |
| `rewritten_query` | 改写后的问题 |
| `item_names` | 识别到的产品名 |
| `image_urls` | 引用图片地址 |
| `ts` | 时间戳 |

### 7.4 常用 Filter

只看用户提问：

```json
{ "role": "user" }
```

只看助手回答：

```json
{ "role": "assistant" }
```

按产品名查询：

```json
{ "item_names": "RS-12数字万用表" }
```

按时间倒序需要填在 Compass 的 `Sort` 框：

```json
{ "ts": -1 }
```

### 7.5 Filter 没结果怎么办

如果 `{ "role": "user" }` 没有结果：

1. 先确认 `kb002.chat_message` 集合里是否有数据。
2. 去 <http://localhost:8001/chat.html> 提问一句。
3. 等回答完成后，回到 Compass 点击刷新。
4. 再搜索 `{ "role": "user" }`。

---

## 八、常用运维命令

### 8.1 查看容器状态

```powershell
docker compose ps
```

### 8.2 启动容器

```powershell
docker compose up -d
```

### 8.3 停止容器

```powershell
docker compose stop
```

### 8.4 查看日志

```powershell
docker compose logs -f
```

查看单个服务日志：

```powershell
docker compose logs -f mongo
docker compose logs -f milvus
docker compose logs -f neo4j
```

### 8.5 检查端口占用

```powershell
Get-NetTCPConnection -LocalPort 8000,8001,8002,19530,27017,7474,7687 -State Listen
```

### 8.6 停止占用端口的 Python 进程

先查 PID：

```powershell
Get-NetTCPConnection -LocalPort 8001 -State Listen | Select-Object OwningProcess
```

再停止：

```powershell
Stop-Process -Id <PID> -Force
```

### 8.7 检查 MongoDB 数据

```powershell
docker exec smart-agent-mongo mongosh -u kbadmin -p kbadmin123 --authenticationDatabase admin --quiet --eval "print(db.getSiblingDB('kb002').chat_message.countDocuments({}))"
```

### 8.8 备份 MongoDB 命名卷

```powershell
docker run --rm -v smart_agent_system_mongo_data:/data -v ${PWD}:/backup alpine tar czf /backup/mongo-backup.tar.gz /data
```

---

## 九、目录结构

```text
smart_agent_system/
├── .env
├── .env.example
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
├── README.md
├── HANDOFF.md
├── study_smart_agent.md
├── app/
│   ├── clients/
│   ├── conf/
│   ├── core/
│   ├── import_process/
│   │   ├── api/file_import_service.py
│   │   ├── agent/main_graph.py
│   │   └── page/import.html
│   └── query_process/
│       ├── api/query_service.py
│       ├── agent/main_graph.py
│       ├── agent/nodes/
│       └── page/chat.html
├── doc/
├── prompts/
├── scripts/
├── test/
├── output/
├── logs/
└── volumes/
```

---

## 十、常见问题

### Q1：`docker compose up -d` 一直卡住怎么办？

先查看状态：

```powershell
docker compose ps
docker ps -a
```

如果 Milvus 处于健康检查中，请等待 30-60 秒。

如果容器退出，查看日志：

```powershell
docker compose logs mongo
docker compose logs milvus
docker compose logs neo4j
```

### Q2：MongoDB 容器启动失败怎么办？

本项目使用 Docker 命名卷：

```yaml
volumes:
  - mongo_data:/data/db
```

不要改成 Windows 本地目录挂载，例如：

```yaml
./volumes/mongo:/data/db
```

原因是 Windows + Docker Desktop + WSL2 下，MongoDB 对 `/data/db` 的权限操作可能在 bind mount 上失败。

### Q3：Compass 连接失败怎么办？

检查 URI 是否完整：

```text
mongodb://kbadmin:kbadmin123@localhost:27017/?authSource=admin
```

必须带 `?authSource=admin`，否则会认证失败。

### Q4：`chat.html` 能打开，但提问后卡住怎么办？

常见原因：

- 第一次请求需要加载 BGE-M3 模型，可能需要 30-60 秒。
- Milvus 里没有数据，先通过 `import.html` 上传文档。
- DashScope API Key 无效或过期。
- Docker 容器没有启动。

### Q5：为什么问“你好”不走 LLM？

这是设计行为。

当前系统要求先识别产品型号。没有产品型号时，`node_item_name_confirm.py` 会直接返回：

```text
抱歉，未找到相关产品，请提供准确型号以便我为您查询。
```

如果希望支持闲聊，需要修改 `app/query_process/agent/nodes/node_item_name_confirm.py` 中无产品名分支的逻辑，让它转给 LLM 做通用回复。

### Q6：修改 `.env` 后为什么不生效？

FastAPI 服务启动时只读取一次 `.env`。修改 `.env` 后需要重启 query_service 或 import_service。

### Q7：Docker 数据存在哪里？

| 组件 | 存储位置 |
|------|----------|
| Milvus | `./volumes/milvus/` |
| etcd | `./volumes/etcd/` |
| Milvus 内部 MinIO | `./volumes/milvus-minio/` |
| Neo4j | `./volumes/neo4j/` |
| MongoDB | Docker 命名卷 `smart_agent_system_mongo_data` |

不要执行：

```powershell
docker compose down -v
```

除非你确认要删除命名卷数据。

### Q8：如何验证完整 RAG 是否跑通？

先确保已经导入 RS-12 相关文档，然后访问：

<http://localhost:8001/chat.html>

提问：

```text
RS-12数字万用表怎么使用？
```

如果系统返回基于文档的具体答案，说明导入、检索、重排、LLM 生成链路基本正常。

---

## 十一、技术栈速查

| 类别 | 组件 | 说明 |
|------|------|------|
| Web 框架 | FastAPI + Uvicorn | 提供导入和查询接口 |
| Agent 编排 | LangGraph | 导入流程和查询流程编排 |
| 大模型 | DashScope OpenAI 兼容接口 | 默认 `qwen-flash` |
| Embedding | BGE-M3 | 本地向量化 |
| Rerank | BGE Reranker Large | 本地重排 |
| 向量库 | Milvus Standalone v2.5.10 | 本地 Docker |
| 向量库 UI | Attu v2.5 | 本地 Docker，端口 8002 |
| 图数据库 | Neo4j Community v5.26 | 本地 Docker |
| 文档库 | MongoDB v6.0 | 本地 Docker，端口 27017 |
| 文档库 UI | MongoDB Compass | 桌面客户端 |
| 对象存储 | MinIO | 业务 MinIO 仍使用远程 `47.94.86.115:9000` |
| 包管理 | uv | Python 依赖管理 |
| 日志 | loguru | 日志输出 |

---

## 十二、当前部署状态记录

当前已完成：

- 本地 Docker Compose 已包含 Milvus、Neo4j、MongoDB、Attu。
- MongoDB 已切换为本地 Docker：`mongodb://kbadmin:kbadmin123@localhost:27017/?authSource=admin`。
- Attu 通过 <http://localhost:8002> 管理 Milvus。
- MongoDB Compass 可连接本地 MongoDB 查看 `kb002.chat_message`。
- 远程 MinIO 仍保留为业务对象存储。

后续待办：

- 完整验证 `RS-12数字万用表怎么使用？` 的端到端 RAG 问答。
- 将 Neo4j 知识图谱查询从占位逻辑完善为真实查询。
- 根据需要完善一键启动 / 停止脚本。
