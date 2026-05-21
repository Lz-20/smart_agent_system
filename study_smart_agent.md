# Smart Agent System 项目学习指南（宏观篇）

> 这份文档帮你**从用户视角 → 系统架构 → 数据流转 → 关键技术**逐层吃透项目，等你看完这一份再深入读代码会顺很多。
>
> 阅读顺序建议：
> 1. **第一章** 一句话定位项目（明白做的是什么生意）
> 2. **第二章** 用户操作链路（明白用户怎么用）
> 3. **第三章** 系统架构总览（明白有哪些组件）
> 4. **第四章 + 第五章** 两条主流程详解（明白数据怎么流）
> 5. **第六章** 关键技术 6 个亮点
> 6. **第七章** 学习路径推荐（按文件读代码）

---

## 目录

- [一、项目定位：一句话讲清楚](#一项目定位一句话讲清楚)
- [二、用户视角：两条操作链路](#二用户视角两条操作链路)
- [三、系统架构总览](#三系统架构总览)
- [四、导入流程详解（让知识库有内容）](#四导入流程详解让知识库有内容)
- [五、查询流程详解（让用户拿到答案）](#五查询流程详解让用户拿到答案)
- [六、关键技术亮点](#六关键技术亮点)
- [七、推荐学习路径（按文件顺序）](#七推荐学习路径按文件顺序)
- [八、术语对照表](#八术语对照表)

---

## 一、项目定位：一句话讲清楚

> **掌柜智库**：一个专门"看产品手册→回答用户问题"的 RAG 智能客服系统。

具体来说就是：

1. **客服侧拿一堆 PDF 产品手册**（如《HAK 180 烫金机说明书.pdf》《万用表 RS-12 使用手册.pdf`）→ 系统把它们变成可被 AI 理解的"知识库"。
2. **用户在网页上问问题**（如"HAK 180 烫金机怎么调温度？"）→ 系统从知识库找出最相关的几段文字，连同图片一起，给出**带出处的中文回答**。

跟普通 ChatGPT 的区别在于：
- 普通 LLM 凭训练记忆瞎说，掌柜智库 **只基于私有手册回答**，引用切片可以追溯。
- 普通搜索是关键字匹配，掌柜智库做了 **4 路并发检索 + 重排**，召回质量更高。
- 用户问"它是多少钱"时，系统会**结合上下文消解代词**，识别"它"是指上一轮的"HAK 180 烫金机"。

---

## 二、用户视角：两条操作链路

整个系统分**两套界面**，对应两类用户角色。

### 2.1 知识库管理员（B 端）— 灌数据

**入口**：<http://localhost:8000/import.html>

**操作流程**：

```
┌──────────────────────────────────────────────────────────┐
│ 1. 拖拽/选择 PDF 或 MD 文件 → 点【上传】按钮             │
│ 2. 系统返回 task_id，前端开始轮询 /status/{task_id}     │
│ 3. 进度条依次亮起：                                      │
│    ✅ upload_file (本地保存 + MinIO 持久化)              │
│    ✅ node_pdf_to_md (MinerU 解析 PDF → Markdown)        │
│    ✅ node_md_img (修复 markdown 中的图片路径)           │
│    ✅ node_document_split (按标题切分成 Chunks)          │
│    ✅ node_item_name_recognition (LLM 识别商品型号)      │
│    ✅ node_bge_embedding (BGE-M3 文本→向量)              │
│    ✅ node_import_milvus (Chunks 向量入库 Milvus)        │
│ 4. status = completed，知识库就有这本手册的数据了        │
└──────────────────────────────────────────────────────────┘
```

> 💡 **管理员无需懂 AI**：拖文件 + 点按钮即可，剩下的自动化。

### 2.2 普通客服/客户（C 端）— 问问题

**入口**：<http://localhost:8001/chat.html>

**操作流程**：

```
┌──────────────────────────────────────────────────────────┐
│ 1. 在输入框敲问题 → 回车                                 │
│ 2. 前端 POST /query (是流式就走 SSE，否则同步)           │
│ 3. 后端 LangGraph 7 节点协作：                           │
│    🟦 商品名确认 (识别说的是哪个产品)                    │
│    🟨 4 路并发召回 (向量+HyDE+图谱+网络搜索)             │
│    🟧 RRF 融合 (4 路结果合并排序)                        │
│    🟧 BGE Rerank (相关性二次精排)                        │
│    🟩 LLM 生成最终答案 (qwen-flash + 上下文)             │
│ 4. 答案逐字符流式推送到聊天气泡                          │
│ 5. 引用了图片就额外渲染图片块                            │
└──────────────────────────────────────────────────────────┘
```

> 💡 **客服侧的痛点解决**：用户问"HAK 180 多少钱"，模型不会瞎编一个数字，会从手册中找出对应章节回答。

---

## 三、系统架构总览

### 3.1 高层组件图

```
┌─────────────────────────────────────────────────────────────────┐
│                          用户浏览器                              │
│   [chat.html: 8001]          [import.html: 8000]                │
└──────────┬──────────────────────────┬───────────────────────────┘
           │ HTTP/SSE                 │ multipart upload
           ↓                          ↓
┌──────────────────────┐    ┌──────────────────────┐
│  query_service       │    │  file_import_service │  ← 两个 FastAPI 进程
│  (LangGraph: 7 节点) │    │  (LangGraph: 7 节点) │
└──────┬────────────┬──┘    └──┬────────────────┬──┘
       │ ↑          │ ↑        │ ↑              │
       │ │ 检索    │ │生成     │ │              │
       ↓ │          ↓ │        ↓ │              ↓
┌──────────┐  ┌─────────┐  ┌──────────┐   ┌──────────┐
│  Milvus  │  │  LLM    │  │  Milvus  │   │  MinerU  │  ← 内部依赖
│ (向量库) │  │(qwen-fl)│  │ (向量库) │   │ (PDF解析)│
└──────────┘  └─────────┘  └──────────┘   └──────────┘
       ↑           ↑              ↑              ↑
       │           │              │              │
┌──────┴───────────┴──────────────┴──────────────┴────┐
│         共享基础设施（Docker / 远程服务）            │
│  • Milvus + etcd + minio (向量+元数据+存储)         │
│  • Neo4j (知识图谱-已落地最小演示)                  │
│  • MongoDB (聊天历史 / 任务状态)                    │
│  • MinIO 远程 (上传文件原档持久化)                  │
│  • DashScope (LLM API + MCP 网络搜索)               │
└─────────────────────────────────────────────────────┘
```

### 3.2 进程模型

| 进程 | 端口 | 入口模块 | 主要职责 |
|------|------|---------|----------|
| **query_service** | 8001 | `@d:/windsuf project/smart_agent_system/app/query_process/api/query_service.py:18-19` | 提供问答 API、SSE 流式推送、聊天历史接口 |
| **file_import_service** | 8000 | `@d:/windsuf project/smart_agent_system/app/import_process/api/file_import_service.py:28-31` | 接收文件上传、触发 LangGraph 后台导入任务 |
| **Docker: milvus 栈** | 19530 / 9091 | `docker-compose.yml` | Milvus 单机版（含 etcd + 内部 minio） |
| **Docker: neo4j** | 7474 / 7687 | `docker-compose.yml` | Neo4j 5.26 社区版，存放商品-规格/特性/组件/操作/故障关系图（示例数据见 `@d:/windsuf project/smart_agent_system/scripts/init_neo4j_kg.py`） |

### 3.3 LangGraph 在哪儿？

**LangGraph 是核心编排框架**，两个服务各有一张图：

| 服务 | LangGraph 编译入口 | 触发时机 |
|------|------|----------|
| 查询 | `@d:/windsuf project/smart_agent_system/app/query_process/agent/main_graph.py:14-82` `query_app = builder.compile()` | 收到 `/query` 请求时 `query_app.invoke(state)` |
| 导入 | `@d:/windsuf project/smart_agent_system/app/import_process/agent/main_graph.py:26-92` `kb_import_app = workflow.compile()` | 收到文件上传后 `kb_import_app.stream(state)` |

**LangGraph 干什么的？** 把一个复杂任务拆成多个**节点函数**（每个节点接收 state、返回 state 的部分字段），用**有向图**串起来。每个节点只关心自己输入输出，框架负责按图遍历、合并状态、并发执行、流式输出。

---

## 四、导入流程详解（让知识库有内容）

### 4.1 状态对象 ImportGraphState

整个导入流程，所有节点共享一个状态字典 `@d:/windsuf project/smart_agent_system/app/import_process/agent/state.py:5-39`：

```python
class ImportGraphState(TypedDict):
    task_id: str              # 任务唯一ID（追踪日志/进度用）
    is_md_read_enabled: bool  # 直接走 MD 路径
    is_pdf_read_enabled: bool # 走 PDF 路径
    local_dir: str            # 任务工作目录 output/YYYYMMDD/<task_id>/
    local_file_path: str      # 上传文件本地路径
    pdf_path / md_path: str   # PDF/MD 文件路径
    md_content: str           # MD 全文（PDF 解析得来或直接读入）
    chunks: list              # 切分后的 Chunk 列表（含 metadata）
    item_name: str            # LLM 识别的产品名（如 "HAK 180 烫金机"）
    embeddings_content: list  # 向量化后的 Chunk（含 dense + sparse）
```

### 4.2 节点流转图

```
                ┌──────────────┐
                │ node_entry   │  ← 入口：参数校验、判断走 PDF 还是 MD
                └──────┬───────┘
              is_pdf?  │  is_md?
              ↓        ↓
       ┌──────────────┐ │
       │node_pdf_to_md│ │  ← 上传 PDF 给 MinerU 云端解析，下载 MD 包
       │  (~30-60秒)  │ │
       └──────┬───────┘ │
              └────┬────┘
                   ↓
           ┌──────────────┐
           │ node_md_img  │  ← 扫描 MD 中的图片引用，下载到本地 / 上传 MinIO
           └──────┬───────┘  ← 替换图片路径为公网可访问 URL
                  ↓
       ┌──────────────────┐
       │node_document_    │  ← 按 # / ## / ### 标题层级切分
       │     split        │  ← 控制单 Chunk ≤ 2000 字符，> 时二次切分
       └──────┬───────────┘  ← 短 Chunk 同标题合并
              ↓
   ┌──────────────────────┐
   │node_item_name_       │  ← LLM 阅读全文，识别核心商品名
   │   recognition        │  ← 写入 chunks[*].item_name 字段
   └──────┬───────────────┘
          ↓
  ┌──────────────────────┐
  │ node_bge_embedding   │  ← BGE-M3 同时生成稠密(1024d) + 稀疏向量
  │                      │  ← 写入 chunks[*].dense_vector / sparse_vector
  └──────┬───────────────┘
         ↓
 ┌──────────────────────┐
 │ node_import_milvus   │  ← 删除该 item_name 的旧数据(幂等)
 │                      │  ← 批量写入 Milvus kb_chunks 集合
 └──────┬───────────────┘  ← 回填 Milvus 自增 chunk_id
        ↓
       END
```

### 4.3 一个具体例子

假设管理员上传了 `HAK180说明书.pdf`：

| 步骤 | 输入 | 输出 |
|------|------|------|
| `node_entry` | `local_file_path="HAK180说明书.pdf"` | 设置 `pdf_path`、`is_pdf_read_enabled=True` |
| `node_pdf_to_md` | PDF 文件 | `md_content="# HAK 180 烫金机...\n## 操作说明\n开机后..."` |
| `node_md_img` | MD 含 `![](./img/panel.jpg)` | 替换为 `![](http://minio.../panel.jpg)` |
| `node_document_split` | 长 MD 文本 | `chunks=[{title, content, h1, h2}, ...]` 共 N 段 |
| `node_item_name_recognition` | chunks + LLM | 给每个 chunk 加 `item_name="HAK 180 烫金机"` |
| `node_bge_embedding` | chunks 文本 | 给每个 chunk 加 `dense_vector(1024维)` + `sparse_vector(字典)` |
| `node_import_milvus` | 完整 chunks | 写入 Milvus，每条返回主键 `chunk_id=1001`、`1002`... |

至此，PDF 在 Milvus 里就是 N 条**可被语义检索**的记录了。

---

## 五、查询流程详解（让用户拿到答案）

### 5.1 状态对象 QueryGraphState

`@d:/windsuf project/smart_agent_system/app/query_process/agent/state.py:5-30`：

```python
class QueryGraphState(TypedDict):
    session_id: str              # 会话ID（多轮对话用）
    original_query: str          # 用户原始问题
    rewritten_query: str         # LLM 改写后的独立完整问题
    item_names: List[str]        # 识别确认的商品名（用于过滤检索）
    history: list                # 近期对话历史

    # 4 路检索结果
    embedding_chunks: list       # 普通向量检索
    hyde_embedding_chunks: list  # HyDE 检索
    kg_chunks: list              # 知识图谱检索
    web_search_docs: list        # 网络搜索

    # 排序结果
    rrf_chunks: list             # 4 路 RRF 融合
    reranked_docs: list          # BGE 重排后的 TopK

    # 输出
    prompt: str
    answer: str
    is_stream: bool
```

### 5.2 节点流转图

```
                 ┌───────────────────────────┐
                 │ node_item_name_confirm    │
                 │ ─────────────────────     │
                 │ Step 3: LLM 提取商品名 +  │
                 │         改写问题           │
                 │ Step 4: Milvus 混合检索   │
                 │         item_names 集合   │
                 │ Step 5: 三档置信度对齐    │
                 │         (高/中/低)         │
                 │ Step 6: 三分支决策        │
                 └────┬──────────────────────┘
                      │
       ┌──────────────┴───────────────┐
   有answer                       无answer
   (反问/拒答)                  (确认了商品)
       │                              │
       ↓                              ↓
 ┌───────────────┐         ┌────────────────────┐
 │ 直接跳到生成  │         │ node_multi_search  │  ← 虚拟节点：分叉点
 │   节点输出    │         │  (lambda x: x)     │
 └───────────────┘         └─────────┬──────────┘
       │                             │
       │             ┌───────────────┼───────────────┬──────────────────┐
       │             ↓               ↓               ↓                  ↓
       │   ┌──────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐
       │   │node_search_  │  │node_search_ │  │node_query_  │  │node_web_     │
       │   │  embedding   │  │embedding_   │  │     kg      │  │  search_mcp  │
       │   │              │  │  hyde       │  │ (Neo4j图谱) │  │  (DashScope  │
       │   │ ① 改写后的Q  │  │① LLM 写一段 │  │ ① 用商品名 │  │   MCP搜索)   │
       │   │   →BGE 向量  │  │  假设答案   │  │   过滤      │  │              │
       │   │ ② Milvus     │  │② 假答案→向量│  │ ② Cypher   │  │              │
       │   │  混合检索    │  │③ 检索       │  │   关系召回  │  │              │
       │   └──────┬───────┘  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘
       │          │                  │                │                │
       │          └──────┬───────────┴────────┬───────┘                │
       │                 │                    │                        │
       │                 ↓                    ↓                        ↓
       │          ┌──────────────────────────────────────────────────────┐
       │          │              node_join (虚拟合并节点)                │
       │          └──────┬───────────────────────────────────────────────┘
       │                 ↓
       │          ┌──────────────────┐
       │          │   node_rrf       │  ← Reciprocal Rank Fusion
       │          │                  │  ← 三路本地结果加权融合
       │          └──────┬───────────┘  ← (web_search_docs 单独保留)
       │                 ↓
       │          ┌──────────────────┐
       │          │  node_rerank     │  ← BGE Reranker Large
       │          │                  │  ← (rrf_chunks + web_search_docs)
       │          │                  │  ← 重排后取 TopK（断崖检测动态截断）
       │          └──────┬───────────┘
       │                 ↓
       └──────────→┌──────────────────┐
                   │node_answer_output│  ← 拼 Prompt: question + reranked_docs
                   │                  │  ← + history + item_names
                   │                  │  ← LLM 流式生成 → SSE 推送给前端
                   │                  │  ← MongoDB 保存助手回答
                   └──────┬───────────┘
                          ↓
                         END
```

### 5.3 一个具体例子（多轮对话）

**Round 1**：
- 用户问："HAK 180 怎么调温度？"
- `node_item_name_confirm` Step 3 → `item_names=["HAK 180 烫金机"]`, `rewritten_query="HAK 180 烫金机如何调节温度？"`
- 4 路并发检索 → 总共拿回 ~30 个相关 chunk
- RRF 融合 → 取前 10
- BGE rerank → 取前 5
- LLM 生成 → "HAK 180 烫金机的温度调节按钮位于操作面板上方，开机后..."

**Round 2**：
- 用户问："**它**多少钱？"（用了代词）
- `node_item_name_confirm` 读取上一轮 history → 识别到"它"= "HAK 180 烫金机"
- LLM 改写问题 → `rewritten_query="HAK 180 烫金机的价格是多少？"`
- 后续流程不变

**Round 3（异常情况）**：
- 用户问："小米 15 怎么使用？"
- `node_item_name_confirm` 在 Milvus 检索 "小米 15" → 置信度低
- 直接 `state["answer"] = "抱歉，未找到相关产品..."`
- LangGraph 路由发现 `state["answer"]` 不为空 → 跳过 4 路检索 → 直接到 `node_answer_output` 输出兜底回复

### 5.4 SSE 流式推送机制

`@d:/windsuf project/smart_agent_system/app/utils/sse_utils.py:8-14` 定义了 5 类事件：

| 事件 | 时机 | 内容 |
|------|------|------|
| `READY` | SSE 连接建立 | `{}` |
| `PROGRESS` | 每个节点 add_running/add_done | `{"node": "node_rrf", "status": "done"}` |
| `DELTA` | LLM 流式吐字 | `{"delta": "HAK 180"}` |
| `FINAL` | 完整答案 | `{"answer": "...完整内容..."}` |
| `ERROR` | 异常 | `{"error": "..."}` |

前端 `chat.html` 用 EventSource 订阅 `/stream/{session_id}`，实时收到这些事件，渲染进度条 + 流式打字效果。

---

## 六、关键技术亮点

理解这 6 点，就能跟同行讲清楚项目了。

### 6.1 BGE-M3 稠密 + 稀疏混合向量

`@d:/windsuf project/smart_agent_system/app/lm/embedding_utils.py:36-44`

BGE-M3 同时输出：
- **稠密向量** (1024 维 float)：捕捉语义近义（"温度调节" ≈ "调温"）
- **稀疏向量** (字典 `{token_id: weight}`)：捕捉精确词命中（"HAK 180" 必须出现）

两者一起喂给 Milvus 做 `WeightedRanker(0.7, 0.3)` 加权混合检索 → 既精准又能近义召回。

### 6.2 LLM 改写问题 + 商品名识别

`@d:/windsuf project/smart_agent_system/app/query_process/agent/nodes/node_item_name_confirm.py:21-78` Step 3

直接让 LLM 阅读"历史对话 + 当前问题"，输出 JSON：
```json
{ "item_names": ["HAK 180 烫金机"], "rewritten_query": "..." }
```

**两个作用**：
1. **代词消解**："它多少钱" → "HAK 180 烫金机多少钱"，让向量检索能命中。
2. **过滤范围**：拿到 `item_names` 后，Milvus 检索时加 `item_name in ["HAK 180 烫金机"]` 过滤条件 → 不被其他产品干扰。

### 6.3 三档置信度对齐（鲁棒性兜底）

`@d:/windsuf project/smart_agent_system/app/query_process/agent/nodes/node_item_name_confirm.py:200-225` Step 5

LLM 提取的 `item_names` **不一定准**（可能是"HAK 180" 但库里只有 "HAK 180 烫金机"）。流程：

| 置信度档位 | 评分阈值 | 处理 |
|------|------|------|
| 高 | score > 0.85 | 自动确认，进入检索 |
| 中 | 0.6 ≤ score ≤ 0.85 | 加入 options，反问用户："您是问 A、B、C 中哪个？" |
| 低 | score < 0.6 | 兜底回复："抱歉，未找到相关产品" |

→ **这就是 LangGraph 中 "答案提前出现就跳过检索" 这条路由的设计原因**。

### 6.4 HyDE 假设性文档检索

`@d:/windsuf project/smart_agent_system/app/query_process/agent/nodes/node_search_embedding_hyde.py:14-47` Step 1

**问题**：用户问 "怎么开机？" 是短查询（5 字），手册里"开机说明"段落是长文本（500 字），向量空间不在一个区域，召回率低。

**解法**：先让 LLM 写一段假答案（"开机方法：按住电源键 3 秒..."），用这段**长假答案**去检索 → 长 vs 长，向量空间匹配度高，召回质量大幅提升。

→ 这就是为什么有 `node_search_embedding` (普通) 和 `node_search_embedding_hyde` (HyDE) 两个并行节点。

### 6.5 RRF Reciprocal Rank Fusion

`@d:/windsuf project/smart_agent_system/app/query_process/agent/nodes/node_rrf.py:79`

4 路检索结果分数标准不一样（向量距离、TF-IDF、知识图谱关联度），无法直接合并。RRF 公式只看排名：

$$
\text{RRF\_score}(d) = \sum_{i \in \text{路数}} \frac{w_i}{k + \text{rank}_i(d)}, \quad k=60
$$

→ 不管原始分数怎么算，**只要在每路里排得靠前，最终就排得靠前**，干净简洁、抗噪能力强。

### 6.6 BGE Reranker 二次精排

`@d:/windsuf project/smart_agent_system/app/query_process/agent/nodes/node_rerank.py:1-16`

向量检索是"双塔模型"（query 和 doc 分别编码后比距离），**忽略了细粒度交互**。Reranker 是"交叉编码器"（query+doc 一起喂模型），效果好但慢。

策略：先用向量召回 30 条（粗筛），再用 Reranker 重排 → 取 TopK（精筛）。

**断崖检测**（`@d:/windsuf project/smart_agent_system/app/query_process/agent/nodes/node_rerank.py:8-16`）：
- 默认最多取前 10 条，但如果第 5 条到第 6 条分数突然掉 50%+，自动只取前 5 条 → 避免低相关性 chunk 干扰 LLM。

---

## 七、推荐学习路径（按文件顺序）

下面是吃透代码的最佳顺序，预计 2-3 小时能精读一遍核心。

### 阶段 1：架构骨架（30 分钟）

| 顺序 | 文件 | 看什么 |
|------|------|--------|
| 1 | `@d:/windsuf project/smart_agent_system/pyproject.toml` | 依赖清单 |
| 2 | `@d:/windsuf project/smart_agent_system/.env` | 全部配置项 |
| 3 | `@d:/windsuf project/smart_agent_system/docker-compose.yml` | 外部服务依赖 |
| 4 | `@d:/windsuf project/smart_agent_system/app/core/logger.py` | 日志规范 |
| 5 | `@d:/windsuf project/smart_agent_system/app/utils/path_util.py` | 项目根目录定位 |

### 阶段 2：查询服务（45 分钟）

| 顺序 | 文件 | 看什么 |
|------|------|--------|
| 1 | `@d:/windsuf project/smart_agent_system/app/query_process/api/query_service.py` | FastAPI 入口、`/query` `/stream` `/history` 接口 |
| 2 | `@d:/windsuf project/smart_agent_system/app/query_process/agent/state.py` | QueryGraphState 全字段 |
| 3 | `@d:/windsuf project/smart_agent_system/app/query_process/agent/main_graph.py` | LangGraph 编排（**最重要**） |
| 4 | `@d:/windsuf project/smart_agent_system/app/query_process/agent/nodes/node_item_name_confirm.py` | 7 个 step 的商品名确认 |
| 5 | `@d:/windsuf project/smart_agent_system/app/query_process/agent/nodes/node_search_embedding.py` | 向量检索 |
| 6 | `@d:/windsuf project/smart_agent_system/app/query_process/agent/nodes/node_search_embedding_hyde.py` | HyDE 检索 |
| 7 | `@d:/windsuf project/smart_agent_system/app/query_process/agent/nodes/node_web_search_mcp.py` | MCP 网络搜索 |
| 8 | `@d:/windsuf project/smart_agent_system/app/query_process/agent/nodes/node_rrf.py` | RRF 融合算法 |
| 9 | `@d:/windsuf project/smart_agent_system/app/query_process/agent/nodes/node_rerank.py` | BGE 重排 |
| 10 | `@d:/windsuf project/smart_agent_system/app/query_process/agent/nodes/node_answer_output.py` | LLM 生成 + SSE 推送 |

### 阶段 3：导入服务（45 分钟）

| 顺序 | 文件 | 看什么 |
|------|------|--------|
| 1 | `@d:/windsuf project/smart_agent_system/app/import_process/api/file_import_service.py` | 上传接口、后台任务调度 |
| 2 | `@d:/windsuf project/smart_agent_system/app/import_process/agent/state.py` | ImportGraphState 全字段 |
| 3 | `@d:/windsuf project/smart_agent_system/app/import_process/agent/main_graph.py` | 导入图（**条件路由典型例子**） |
| 4 | `@d:/windsuf project/smart_agent_system/app/import_process/agent/nodes/node_pdf_to_md.py` | MinerU 云解析（轮询 API） |
| 5 | `@d:/windsuf project/smart_agent_system/app/import_process/agent/nodes/node_md_img.py` | 图片下载/上传/路径替换 |
| 6 | `@d:/windsuf project/smart_agent_system/app/import_process/agent/nodes/node_document_split.py` | 标题层级切分 + 长度控制 |
| 7 | `@d:/windsuf project/smart_agent_system/app/import_process/agent/nodes/node_item_name_recognition.py` | LLM 提取商品名 |
| 8 | `@d:/windsuf project/smart_agent_system/app/import_process/agent/nodes/node_bge_embedding.py` | 批量向量化 |
| 9 | `@d:/windsuf project/smart_agent_system/app/import_process/agent/nodes/node_import_milvus.py` | 自动建表+幂等写入 |

### 阶段 4：基础工具（30 分钟）

| 顺序 | 文件 | 看什么 |
|------|------|--------|
| 1 | `@d:/windsuf project/smart_agent_system/app/lm/lm_utils.py` | LangChain 包装 OpenAI 兼容客户端 |
| 2 | `@d:/windsuf project/smart_agent_system/app/lm/embedding_utils.py` | BGE-M3 单例 + 编码 |
| 3 | `@d:/windsuf project/smart_agent_system/app/lm/reranker_utils.py` | Reranker 单例 |
| 4 | `@d:/windsuf project/smart_agent_system/app/clients/milvus_utils.py` | 混合检索请求构造 |
| 5 | `@d:/windsuf project/smart_agent_system/app/clients/mongo_history_utils.py` | 聊天历史 CRUD |
| 6 | `@d:/windsuf project/smart_agent_system/app/clients/minio_utils.py` | 图片/文件上传 |
| 7 | `@d:/windsuf project/smart_agent_system/app/utils/sse_utils.py` | SSE 队列 + 事件常量 |
| 8 | `@d:/windsuf project/smart_agent_system/app/utils/task_utils.py` | 任务状态字典（前端轮询用） |
| 9 | `@d:/windsuf project/smart_agent_system/app/core/load_prompt.py` | 提示词模板加载 |
| 10 | `@d:/windsuf project/smart_agent_system/prompts/*.prompt` | 6 个核心提示词文本 |

### 阶段 5：前端（可选，15 分钟）

| 顺序 | 文件 | 看什么 |
|------|------|--------|
| 1 | `@d:/windsuf project/smart_agent_system/app/query_process/page/chat.html` | 单文件聊天 UI（含 EventSource SSE） |
| 2 | `@d:/windsuf project/smart_agent_system/app/import_process/page/import.html` | 文件上传 UI（含轮询） |

---

## 八、术语对照表

| 术语 | 全称 | 项目里的体现 |
|------|------|-------------|
| **RAG** | Retrieval-Augmented Generation | 整套系统的总称 |
| **LangGraph** | LangChain 的状态图编排库 | 两个 main_graph.py |
| **State** | LangGraph 流转的状态对象 | `QueryGraphState` / `ImportGraphState` |
| **Node** | LangGraph 节点 | `app/query_process/agent/nodes/*.py` |
| **HyDE** | Hypothetical Document Embeddings | `node_search_embedding_hyde.py` |
| **RRF** | Reciprocal Rank Fusion | `node_rrf.py` |
| **Rerank** | 检索重排 | `node_rerank.py`（BGE-Reranker-Large） |
| **Embedding** | 文本向量化 | BGE-M3 模型 |
| **Dense Vector** | 稠密向量 | BGE-M3 输出 1024 维 float |
| **Sparse Vector** | 稀疏向量 | BGE-M3 输出 token-weight 字典 |
| **Hybrid Search** | 稠密+稀疏混合检索 | `milvus_utils.create_hybrid_search_requests` |
| **Chunk** | 文档切片 | `node_document_split.py` 的输出 |
| **Item Name** | 商品名/型号 | "HAK 180 烫金机"，用于过滤检索 |
| **MCP** | Model Context Protocol | `node_web_search_mcp.py` 调阿里 MCP |
| **MinerU** | OpenXLab 的 PDF 解析云服务 | `node_pdf_to_md.py` |
| **SSE** | Server-Sent Events | `sse_utils.py` |
| **MongoDB History** | 聊天历史持久化 | `mongo_history_utils.py` |
| **Idempotent** | 幂等 | `node_import_milvus.py` 同 item_name 先删后插 |

---

## 九、写在最后

掌握**两张图**（导入图 + 查询图）+ **一个状态对象**（LangGraph TypedDict）+ **6 个亮点**（BGE-M3、问题改写、置信度对齐、HyDE、RRF、Rerank），就能在面试和代码评审里顺畅讲清整个项目了。

读代码遇到不懂的，按 [第七章学习路径](#七推荐学习路径按文件顺序) 的顺序定位文件，再回头查这份文档对应的小节。

接下来想深入哪一块就喊我，可以再分别写：

- 📘 **细节篇**：每个节点的完整 step-by-step 实现解析
- 📗 **算法篇**：BGE-M3 / RRF / Reranker 的数学原理与源码对照
- 📕 **改造篇**：你想替换 LLM、加新检索路、改 prompt 的实战指南
- 📙 **运维篇**：Milvus 集合表结构、Neo4j Cypher 查询、MongoDB 索引设计
