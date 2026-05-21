# 鎺屾煖鏅哄簱 Smart Agent System

鍩轰簬 FastAPI + LangGraph + Milvus + Neo4j 鐨勬櫤鑳介棶绛斾笌鐭ヨ瘑搴撳鍏ョ郴缁熴€?
- **鏌ヨ鏈嶅姟**锛氬璺贩鍚堟绱紙鍚戦噺 + HyDE + 鐭ヨ瘑鍥捐氨 + 缃戠粶鎼滅储锛夆啋 RRF 铻嶅悎 鈫?BGE 閲嶆帓 鈫?LLM 鐢熸垚绛旀
- **瀵煎叆鏈嶅姟**锛氫笂浼?PDF/MD 鈫?MinerU 瑙ｆ瀽 鈫?鍒囩墖 鈫?BGE-M3 鍚戦噺鍖?鈫?Milvus / Neo4j 鍏ュ簱

> 鈿狅笍 **瀹夊叏璀﹀憡**锛歚docker-compose.yml` 浣跨敤鐨勬槸**寮€鍙戦粯璁ゅ急瀵嗙爜**锛圢eo4j `neo4j/123123123`銆丮ongoDB `kbadmin/kbadmin123`銆丮inIO `minioadmin/minioadmin`锛夛紝**浠呴檺鏈湴寮€鍙戜娇鐢?*銆傞儴缃插埌浠讳綍鍙闂幆澧冨墠鍔″繀淇敼瀵嗙爜锛屽苟纭繚绔彛锛?687 / 27017 / 9000 / 19530 绛夛級**涓嶆毚闇插叕缃?*銆傚鍒?`.env.example` 涓?`.env` 鍚庡～鍏ヨ嚜宸辩殑瀵嗛挜銆?
---

## 鐩綍

- [涓€銆佺幆澧冭姹俔(#涓€鐜瑕佹眰)
- [浜屻€侀娆￠儴缃诧紙涓€娆℃€э級](#浜岄娆￠儴缃蹭竴娆℃€?
- [涓夈€佹棩甯稿惎鍔紙姣忔寮€鏈猴級](#涓夋棩甯稿惎鍔ㄦ瘡娆″紑鏈?
- [鍥涖€佸仠姝㈡湇鍔(#鍥涘仠姝㈡湇鍔?
- [浜斻€佷竴閿惎鍔ㄨ剼鏈琞(#浜斾竴閿惎鍔ㄨ剼鏈?
- [鍏€佽闂叆鍙(#鍏闂叆鍙?
- [涓冦€佺洰褰曠粨鏋刔(#涓冪洰褰曠粨鏋?
- [鍏€佸父瑙侀棶棰樻帓鏌(#鍏父瑙侀棶棰樻帓鏌?

---

## 涓€銆佺幆澧冭姹?
| 缁勪欢 | 鐗堟湰瑕佹眰 | 璇存槑 |
|------|---------|------|
| Windows 10/11 | x64 | 宸查獙璇?|
| Python | 3.11+ | 鎺ㄨ崘 3.11.9 |
| uv | 0.11+ | Python 鍖呯鐞嗗櫒锛孾瀹夎鎸囧崡](https://docs.astral.sh/uv/) |
| Docker Desktop | 4.x+ | 鐢ㄤ簬璺?Milvus / Neo4j |
| 纾佺洏绌洪棿 | 鈮?15 GB | 妯″瀷 3.6GB + Docker 闀滃儚 3GB + 渚濊禆 4GB + Milvus/MongoDB 鏁版嵁 |
| 鍐呭瓨 | 鈮?8 GB | Milvus 鍗曟満鐗堢害 2GB锛孨eo4j 1GB锛孎astAPI + 妯″瀷 2GB |
| 缃戠粶 | 鍥藉唴鍙揪 | 闃块噷 ModelScope / DashScope / 鍥藉唴 Docker 闀滃儚鍔犻€?|

> **涓嶉渶瑕?GPU**锛氬綋鍓?`.env` 榛樿 `BGE_DEVICE=cpu`銆傛湁 NVIDIA 鏄惧崱鍙敼鎴?`cuda:0` 鍔犻€熴€?
---

## 浜屻€侀娆￠儴缃诧紙涓€娆℃€э級

> 鍚庣画姣忔寮€鏈哄彧闇€璧?[绗笁绔燷(#涓夋棩甯稿惎鍔ㄦ瘡娆″紑鏈?銆?
### 2.1 瀹夎 Python 渚濊禆

椤圭洰鏍圭洰褰曟墦寮€ PowerShell锛?
```powershell
Set-Location "D:\windsuf project\smart_agent_system"
uv sync
```

> 鑻ユ竻鍗庢簮瓒呮椂锛岀敤闃块噷婧愰噸璇曪細
> ```powershell
> uv sync --default-index https://mirrors.aliyun.com/pypi/simple/ --index-strategy unsafe-best-match
> ```

瀹屾垚鍚庝細鍦ㄩ」鐩牴鐩綍鐢熸垚 `.venv/` 鏂囦欢澶广€?
### 2.2 閰嶇疆 Docker 闀滃儚鍔犻€燂紙鍥藉唴蹇呭仛锛?
缂栬緫 `C:\Users\<浣犵殑鐢ㄦ埛鍚?\.docker\daemon.json`锛屽姞鍏?`registry-mirrors` 瀛楁锛?
```json
{
  "builder": {
    "gc": { "defaultKeepStorage": "20GB", "enabled": true }
  },
  "experimental": false,
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live",
    "https://dockerpull.org",
    "https://docker.nju.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
```

淇濆瓨鍚?*閲嶅惎 Docker Desktop** 璁╁姞閫熺敓鏁堛€?
### 2.3 涓嬭浇 BGE 妯″瀷锛堢害 3.6 GB锛?
```powershell
Set-Location "D:\windsuf project\smart_agent_system"
$env:MODELSCOPE_OFFLINE='0'
uv run python app/tool/download_bgem3.py
uv run python app/tool/download_reranker.py
```

涓嬭浇鍒?`D:\ai_models\modelscope_cache\models\` 涓嬨€傜害 5鈥?0 鍒嗛挓銆?
### 2.4 妫€鏌?`.env` 閰嶇疆

鎵撳紑椤圭洰鏍圭洰褰?`.env`锛岀‘璁や互涓嬪叧閿」涓庝綘鐨勭幆澧冧竴鑷达細

| 閰嶇疆 | 榛樿鍊?| 璇存槑 |
|------|--------|------|
| `OPENAI_API_KEY` | `<your-dashscope-api-key>` | 闃块噷鐧剧偧 DashScope API Key |
| `OPENAI_BASE_URL` | `https://dashscope.aliyuncs.com/compatible-mode/v1` | LLM 鍏ュ彛 |
| `LLM_DEFAULT_MODEL` | `qwen-flash` | 涓诲璇濇ā鍨?|
| `BGE_M3_PATH` | `D:\ai_models\modelscope_cache\models\BAAI\bge-m3` | 鏈湴 embedding 妯″瀷 |
| `BGE_RERANKER_LARGE` | `D:\ai_models\modelscope_cache\models\rerank\BAAI\bge-reranker-large` | 鏈湴 rerank 妯″瀷 |
| `MILVUS_URL` | `http://localhost:19530` | 鏈湴 Milvus |
| `NEO4J_URI` | `bolt://localhost:7687` | 鏈湴 Neo4j |
| `NEO4J_PASSWORD` | `<your-neo4j-password>` | 涓?docker-compose.yml 淇濇寔涓€鑷达紙**鐢熶骇閮ㄧ讲鍔″繀淇敼**锛?|
| `MONGO_URL` | `mongodb://<user>:<password>@localhost:27017/?authSource=admin` | MongoDB锛堟湰鍦?Docker锛岃处瀵嗚 docker-compose.yml锛?|
| `MONGO_DB_NAME` | `kb002` | 涓氬姟搴撳悕 |
| `MINIO_ENDPOINT` | `<your-minio-host>:9000` | MinIO 瀵硅薄瀛樺偍锛堣嚜寤?鑷€夊疄渚嬶紝瀛樹笂浼?PDF/鍥剧墖锛?|

---

## 涓夈€佹棩甯稿惎鍔紙姣忔寮€鏈猴級

### 姝ラ 1锛氬惎鍔?Docker Desktop

寮€濮嬭彍鍗?鈫?鎼?`Docker Desktop` 鈫?鍙屽嚮銆傜瓑鍙充笅瑙掑皬椴搁奔 馃悑 鍥炬爣绋冲畾锛堢害 30 绉掞級銆?
鎴栧懡浠よ锛?
```powershell
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

### 姝ラ 2锛氭媺璧锋墍鏈変緷璧栧鍣紙Milvus / Neo4j / MongoDB / Attu锛?
```powershell
Set-Location "D:\windsuf project\smart_agent_system"
docker compose up -d
```

楠岃瘉 6 涓鍣ㄩ兘 `Up`锛?
```powershell
docker compose ps
```

鏈熸湜杈撳嚭锛?
```
NAME                       STATUS
smart-agent-etcd           Up X minutes (healthy)
smart-agent-milvus         Up X minutes (healthy)
smart-agent-milvus-minio   Up X minutes (healthy)
smart-agent-neo4j          Up X minutes
smart-agent-mongo          Up X minutes (healthy)
smart-agent-attu           Up X minutes
```

> 绗竴娆″惎鍔?Milvus 闇€瑕佺害 60 绉掑仛鍋ュ悍妫€鏌ワ紱鍚庣画鍑犱箮绉掕捣銆?> Attu 渚濊禆 Milvus 鍋ュ悍鍚庢墠浼氬惎鍔紝鎵€浠ュ湪 Milvus 鍋ュ悍鍓嶄綘鐪嬪埌 Attu 澶勪簬 `Created/Waiting` 鏄甯哥殑銆?
### 姝ラ 3锛氬惎鍔ㄦ煡璇㈡湇鍔★紙绔彛 8001锛?
**鏂板紑 PowerShell 绐楀彛 A**锛岃繍琛岋細

```powershell
Set-Location "D:\windsuf project\smart_agent_system"
uv run uvicorn app.query_process.api.query_service:app --host 0.0.0.0 --port 8001
```

鐪嬪埌涓嬮潰涓夎灏辨槸鎴愬姛锛?
```
INFO:     Started server process [xxxxx]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

> 鈿狅笍 **璇ョ獥鍙ｄ笉鑳藉叧**锛屽畠鍦ㄥ墠鍙拌緭鍑烘湇鍔℃棩蹇椼€?
### 姝ラ 4锛氬惎鍔ㄦ枃浠跺鍏ユ湇鍔★紙绔彛 8000锛?
**鍐嶅紑 PowerShell 绐楀彛 B**锛岃繍琛岋細

```powershell
Set-Location "D:\windsuf project\smart_agent_system"
uv run uvicorn app.import_process.api.file_import_service:app --host 0.0.0.0 --port 8000
```

鐪嬪埌 `Uvicorn running on http://0.0.0.0:8000` 鍗虫垚鍔熴€?
### 姝ラ 5锛氭祻瑙堝櫒璁块棶

鎵撳紑娴忚鍣ㄨ繘鍏?[璁块棶鍏ュ彛](#鍏闂叆鍙?銆?
---

## 鍥涖€佸仠姝㈡湇鍔?
### 4.1 鍋?FastAPI

鍦ㄤ袱涓?PowerShell 绐楀彛鍒嗗埆鎸?`Ctrl + C`銆?
### 4.2 鍋?Docker 瀹瑰櫒锛堜繚鐣欐暟鎹級

```powershell
Set-Location "D:\windsuf project\smart_agent_system"
docker compose stop
```

### 4.3 閿€姣佸鍣紙鏁版嵁浠嶅湪 `./volumes/`锛?
```powershell
docker compose down
```

### 4.4 鏁版嵁涓€骞舵竻绌猴紙**鎱庣敤**锛屼細涓㈡帀 Milvus / Neo4j 鍏ㄩ儴鏁版嵁锛?
```powershell
docker compose down -v
Remove-Item -Recurse -Force .\volumes\
```

---

## 浜斻€佷竴閿惎鍔ㄨ剼鏈?
椤圭洰鏍圭洰褰曞凡鑷甫 `start.ps1`锛堝鏈敓鎴愬彲鐢ㄤ笅闈㈠唴瀹瑰垱寤猴級锛?
```powershell
# start.ps1 - 涓€閿惎鍔?Docker + 涓や釜 FastAPI 鏈嶅姟
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

# 1) 鎷夎捣 Docker Desktop
$dockerExe = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
if (-not (Get-Process "com.docker.backend" -ErrorAction SilentlyContinue)) {
    Write-Host ">> 鍚姩 Docker Desktop..." -ForegroundColor Cyan
    Start-Process $dockerExe
    for ($i=0; $i -lt 90; $i++) {
        $r = docker version --format '{{.Server.Version}}' 2>&1 | Out-String
        if ($r -match '^\d') { Write-Host ">> Docker 灏辩华: $($r.Trim())" -ForegroundColor Green; break }
        Start-Sleep -Seconds 2
    }
}

# 2) 鍚姩 Milvus + Neo4j 鏍?Write-Host ">> docker compose up -d ..." -ForegroundColor Cyan
docker compose up -d

# 3) 璧?query 鏈嶅姟锛堟柊绐楀彛锛?Write-Host ">> 鍚姩鏌ヨ鏈嶅姟 :8001 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command",
    "Set-Location '$root'; uv run uvicorn app.query_process.api.query_service:app --host 0.0.0.0 --port 8001"

# 4) 璧?import 鏈嶅姟锛堟柊绐楀彛锛?Write-Host ">> 鍚姩瀵煎叆鏈嶅姟 :8000 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command",
    "Set-Location '$root'; uv run uvicorn app.import_process.api.file_import_service:app --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 3
Write-Host ""
Write-Host "======================================" -ForegroundColor Yellow
Write-Host "  闂瓟椤?  http://localhost:8001/chat.html" -ForegroundColor Yellow
Write-Host "  瀵煎叆椤?  http://localhost:8000/import.html" -ForegroundColor Yellow
Write-Host "  Neo4j:   http://localhost:7474" -ForegroundColor Yellow
Write-Host "======================================" -ForegroundColor Yellow
```

**鐢ㄦ硶**锛氬彸閿?`start.ps1` 鈫?鐢?PowerShell 杩愯锛堥娆￠渶鏀惧紑鎵ц绛栫暐锛夛細

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.\start.ps1
```

鍚屾牱鍦版湁 `stop.ps1`锛?
```powershell
# stop.ps1 - 涓€閿仠姝?Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)
Write-Host ">> 鍋滄 uvicorn..." -ForegroundColor Cyan
Get-Process python -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -like '*uvicorn*' } |
    Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host ">> docker compose stop..." -ForegroundColor Cyan
docker compose stop
Write-Host ">> 瀹屾垚" -ForegroundColor Green
```

---

## 鍏€佽闂叆鍙?
### 6.1 涓氬姟鍓嶇 / API

| 鐢ㄩ€?| 鍦板潃 | 璇存槑 |
|------|------|------|
| 馃挰 鏅鸿兘闂瓟椤?| <http://localhost:8001/chat.html> | 涓诲璇濈晫闈?|
| 馃摛 鏂囦欢瀵煎叆椤?| <http://localhost:8000/import.html> | PDF/MD 涓婁紶鍒扮煡璇嗗簱 |
| 馃摎 Query API 鏂囨。 | <http://localhost:8001/docs> | FastAPI Swagger |
| 馃摎 Import API 鏂囨。 | <http://localhost:8000/docs> | FastAPI Swagger |
| 馃┖ 鍋ュ悍妫€鏌?| <http://localhost:8001/health> | 杩斿洖 `{"ok": true}` |

### 6.2 鏁版嵁搴撳彲瑙嗗寲锛堣繍缁?/ 璋冭瘯鐢級

| 鏁版嵁搴?| 宸ュ叿 | 鍏ュ彛 / 杩炴帴涓?| 璐﹀瘑 |
|--------|------|----------------|------|
| 馃 **Milvus**锛堝悜閲忓簱锛?| Attu Web UI | <http://localhost:8002> | 鏃狅紙鐩磋繛 `smart-agent-milvus:19530`锛?|
| 馃敻 **Neo4j**锛堝浘璋憋級 | Neo4j Browser | <http://localhost:7474> | `neo4j` / `<瑙?.env NEO4J_PASSWORD>` |
| 馃摐 **MongoDB**锛堣亰澶╁巻鍙诧級 | **MongoDB Compass**锛堟闈?App锛岄渶鑷涓嬭浇锛?| `mongodb://<user>:<password>@localhost:27017/?authSource=admin` | 瑙?`docker-compose.yml` 鐨?`MONGO_INITDB_ROOT_*` |
| 馃 **MinIO**锛堝璞″瓨鍌級 | MinIO Console | `http://<your-minio-host>:9001` | 瑙?`.env` 鐨?`MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY` |

> **MongoDB Compass 涓嬭浇**锛?https://www.mongodb.com/try/download/compass>
> **Attu** 宸查€氳繃 `docker-compose.yml` 鑷姩闅忛」鐩惎鍔紝鏃犻渶鍗曠嫭瀹夎

### 6.3 鐩戞帶 / 鍋ュ悍绔偣

| 鐢ㄩ€?| 鍦板潃 | 璇存槑 |
|------|------|------|
| 鈿欙笍 Milvus Metrics | <http://localhost:9091/healthz> | Milvus 鍋ュ悍绔偣 |
| 鈿欙笍 Attu 鍋ュ悍 | <http://localhost:8002> | 鎵撳紑鑳界湅鍒扮櫥褰曢〉鍗虫甯?|

### 6.4 MongoDB Compass 瀹炴搷鎸囧崡

#### 涓嬭浇瀹夎

瀹樻柟涓嬭浇锛?https://www.mongodb.com/try/download/compass>锛圵indows 閫?`.exe` 瀹夎鐗堬紝瑁呭畬鑷姩娣诲姞鍒板紑濮嬭彍鍗曪級銆?
#### 棣栨杩炴帴

鍚姩 Compass 鈫?`New Connection` 鈫?URI 妗嗙矘璐达細

```
mongodb://<user>:<password>@localhost:27017/?authSource=admin
```

> URI 鎷嗚В锛?> - `<user>:<password>` 璐﹀瘑锛堜笌 `docker-compose.yml` 涓?`MONGO_INITDB_ROOT_USERNAME/PASSWORD` 涓€鑷达紝榛樿寮€鍙戣处瀵嗚椤圭洰椤堕儴瀹夊叏璀﹀憡锛?> - `localhost:27017` 鏈満 Docker 鏆撮湶绔彛
> - `?authSource=admin` **蹇呴渶锛?* 鍛婅瘔 Mongo 鍘?admin 搴撴煡鐢ㄦ埛锛岀己浜嗕細鎶?`Authentication failed`

灞曞紑 `Save Connection` 璧蜂釜鍚嶅瓧锛堝 `鏈満 KB002`锛夊啀 `Save & Connect`锛屼互鍚庣偣鏀惰棌鐩存帴杩炪€?
#### 杩涘叆涓氬姟搴?
宸︿晶瀵艰埅鐐?`kb002` 鈫?`chat_message` 鈫?`Documents` 鏍囩椤点€?
闆嗗悎缁撴瀯锛?
| 瀛楁 | 绫诲瀷 | 鍚箟 |
|------|------|------|
| `_id` | ObjectId | 涓婚敭 |
| `session_id` | string | 娴忚鍣ㄤ細璇?ID锛堝 `sess-xxxxx`锛?|
| `role` | string | `user` 鎴?`assistant` |
| `text` | string | 娑堟伅鏂囨湰 |
| `rewritten_query` | string | LLM 鏀瑰啓鍚庣殑鐙珛闂 |
| `item_names` | Array | 鏈疆璇嗗埆鐨勫晢鍝佸悕 |
| `image_urls` | Array | 绛旀寮曠敤鐨勫浘鐗?URL |
| `ts` | long | 鍐欏叆鏃堕棿鎴筹紙姣锛?|

#### 甯哥敤杩囨护鏌ヨ

鍦?Documents 椤甸《閮?**Filter** 妗嗛噷濉互涓?JSON锛屽洖杞︽垨鐐?`Find`锛?
| 鐩殑 | Filter |
|------|--------|
| 鍙湅鐢ㄦ埛鎻愰棶 | `{ "role": "user" }` |
| 鍙湅鏌?session 鐨勫畬鏁村璇?| `{ "session_id": "sess-xxxxx" }` |
| 鏌ユ煇浜у搧琚棶杩囩殑鎵€鏈夐棶棰?| `{ "item_names": "RS-12鏁板瓧涓囩敤琛? }` |
| 鏌ユ煇鏃堕棿娈靛悗鐨勬秷鎭紙ts 鏄绉掞級 | `{ "ts": { "$gte": 1730908800000 } }` |

鎺掑簭妗?**Sort** 濉?`{ "ts": -1 }` 鈫?鎸夋椂闂村€掑簭锛?*Limit** 濉?`10` 鈫?鍙彇鏈€杩?10 鏉°€?
#### 瀵煎嚭鏁版嵁

椤堕儴鑿滃崟 `Export Data 鈫?Export the entire collection` 鈫?閫?JSON 鎴?CSV 鈫?涓€閿笅杞藉埌鏈湴銆?
#### 甯歌韪╁潙

- **Filter 鎼?`{ "role": "user" }` 娌＄粨鏋?*锛氶泦鍚堟湰韬繕娌℃暟鎹€傚厛鍘?<http://localhost:8001/chat.html> 鑱婁竴鍙ヨ瘽锛屽洖 Compass 鍒锋柊銆?- **杩炴帴鎶?`Authentication failed`**锛歎RI 灏戜簡 `?authSource=admin`锛岃ˉ涓婂嵆鍙€?- **Compass 鎵撳紑鍚庤繛鎺ヨ秴鏃?*锛氱‘璁?`smart-agent-mongo` 瀹瑰櫒鍦ㄨ窇锛歚docker ps --filter name=smart-agent-mongo`銆?
---

## 涓冦€佺洰褰曠粨鏋?
```
smart_agent_system/
鈹溾攢鈹€ .env                           # 鐜鍙橀噺锛圓PI Key銆佹ā鍨嬭矾寰勩€佹湇鍔″湴鍧€锛?鈹溾攢鈹€ pyproject.toml                 # uv 渚濊禆澹版槑
鈹溾攢鈹€ uv.lock                        # 渚濊禆閿佸畾
鈹溾攢鈹€ docker-compose.yml             # Milvus / Neo4j / MongoDB / Attu 鏍?鈹溾攢鈹€ README.md                      # 鏈枃浠?鈹溾攢鈹€ start.ps1 / stop.ps1           # 涓€閿惎鍋滐紙鍙€夛級
鈹溾攢鈹€ app/
鈹?  鈹溾攢鈹€ clients/                   # Milvus / MinIO / MongoDB / Neo4j 瀹㈡埛绔?鈹?  鈹溾攢鈹€ conf/                      # 鍚勭粍浠堕厤缃姞杞斤紙dataclass 椋庢牸锛?鈹?  鈹溾攢鈹€ core/
鈹?  鈹?  鈹溾攢鈹€ logger.py              # loguru 鍏ㄥ眬鏃ュ織
鈹?  鈹?  鈹斺攢鈹€ load_prompt.py         # 鎻愮ず璇嶅姞杞?鈹?  鈹溾攢鈹€ lm/                        # 澶фā鍨?/ Embedding / Reranker 宸ュ叿
鈹?  鈹溾攢鈹€ tool/
鈹?  鈹?  鈹溾攢鈹€ download_bgem3.py      # 涓嬭浇 BGE-M3
鈹?  鈹?  鈹斺攢鈹€ download_reranker.py   # 涓嬭浇 BGE Reranker
鈹?  鈹溾攢鈹€ utils/                     # SSE 闃熷垪銆佷换鍔＄姸鎬併€佽矾寰勭瓑
鈹?  鈹溾攢鈹€ query_process/             # 鏌ヨ鏈嶅姟
鈹?  鈹?  鈹溾攢鈹€ api/query_service.py   # FastAPI 鍏ュ彛锛堢鍙?8001锛?鈹?  鈹?  鈹溾攢鈹€ agent/main_graph.py    # LangGraph 缂栨帓
鈹?  鈹?  鈹溾攢鈹€ agent/nodes/           # 鍚勪釜妫€绱?閲嶆帓/鐢熸垚鑺傜偣
鈹?  鈹?  鈹斺攢鈹€ page/chat.html         # 鍓嶇椤甸潰
鈹?  鈹斺攢鈹€ import_process/            # 瀵煎叆鏈嶅姟
鈹?      鈹溾攢鈹€ api/file_import_service.py  # FastAPI 鍏ュ彛锛堢鍙?8000锛?鈹?      鈹溾攢鈹€ agent/main_graph.py    # 瀵煎叆 LangGraph 缂栨帓
鈹?      鈹溾攢鈹€ agent/nodes/           # 瑙ｆ瀽 / 鍒囩墖 / 鍚戦噺鍖?/ 鍏ュ簱鑺傜偣
鈹?      鈹斺攢鈹€ page/import.html       # 鍓嶇椤甸潰
鈹溾攢鈹€ doc/                           # 娴嬭瘯 PDF 鏂囨。
鈹溾攢鈹€ prompts/                       # 鎻愮ず璇嶆ā鏉?鈹溾攢鈹€ output/                        # 鏂囦欢瑙ｆ瀽涓棿浜х墿锛堟寜鏃ユ湡/浠诲姟鍒嗗眰锛?鈹溾攢鈹€ logs/                          # loguru 鏃ュ織鎸夊ぉ婊氬姩
鈹溾攢鈹€ volumes/                       # Docker 鍗锋寕杞斤紙Milvus銆丯eo4j銆乪tcd 鏁版嵁锛?鈹斺攢鈹€ test/                          # 娴嬭瘯鑴氭湰
```

---

## 鍏€佸父瑙侀棶棰樻帓鏌?
### Q1锛歚docker compose up` 鎶?`dialing registry-1.docker.io:443 ...failed`

鍥藉唴璁块棶 Docker Hub 涓嶉€氥€傚洖鍘诲仛 [2.2 闀滃儚鍔犻€焆(#22-閰嶇疆-docker-闀滃儚鍔犻€熷浗鍐呭繀鍋?銆?
### Q2锛歚uv sync` 涓€旀煇涓寘涓嬭浇瓒呮椂

娓呭崕闀滃儚鍋跺彂鎶介锛屾崲闃块噷婧愶細
```powershell
uv sync --default-index https://mirrors.aliyun.com/pypi/simple/ --index-strategy unsafe-best-match
```

### Q3锛氬惎鍔?query_service 鎶?`BGEM3EmbeddingFunction` 鍔犺浇澶辫触

妯″瀷璺緞涓嶅銆傛鏌ワ細
```powershell
Test-Path "D:\ai_models\modelscope_cache\models\BAAI\bge-m3\config.json"
Test-Path "D:\ai_models\modelscope_cache\models\rerank\BAAI\bge-reranker-large\config.json"
```
涓や釜閮借繑鍥?`True` 鎵嶈銆傚惁鍒欓噸璺?[2.3 妯″瀷涓嬭浇](#23-涓嬭浇-bge-妯″瀷绾?36-gb)銆?
### Q4锛氳闂?chat.html 鑳芥墦寮€锛屼絾鎻愰棶鍚庨〉闈㈠崱浣?
鎵撳紑绐楀彛 A 鏌?query_service 鏃ュ織锛屽父瑙佸師鍥狅細

- **绗竴娆¤姹?*锛欱GE-M3 妯″瀷鍐峰惎鍔ㄩ渶 30鈥?0 绉掞紝鑰愬績绛夈€?- **Milvus 娌℃暟鎹?*锛氬厛鍘?`import.html` 涓婁紶鍑犱釜 PDF 璁╁鍏ユ祦绋嬫妸鏁版嵁鐏屽叆 Milvus 鍐嶉棶銆?- **DashScope 鎶?401**锛氭鏌?`.env` 鐨?`OPENAI_API_KEY` 鏄惁杩囨湡銆?- **Neo4j 鎷掔粷杩炴帴**锛歚docker compose logs neo4j` 鐪嬫槸涓嶆槸瀵嗙爜涓嶅锛圢EO4J_AUTH 闇€涓?.env 鐨?NEO4J_PASSWORD 涓€鑷达級銆?
### Q5锛氱鍙ｈ鍗?
```powershell
# 鎵捐皝鍗犱簡 8001
Get-NetTCPConnection -LocalPort 8001 -State Listen | Select-Object OwningProcess
# 鏉€鎺?Stop-Process -Id <涓婇潰鐨勮繘绋嬪彿> -Force
```

鎴栬€呮敼鐢ㄥ埆鐨勭鍙ｅ惎鍔細

```powershell
uv run uvicorn app.query_process.api.query_service:app --host 0.0.0.0 --port 18001
```

### Q6锛氭兂鍒囨崲鍒?GPU 鍔犻€?
缂栬緫 `.env`锛?```ini
BGE_DEVICE=cuda:0
BGE_FP16=1
BGE_RERANKER_DEVICE=cuda:0
BGE_RERANKER_FP16=1
```
闇€鍏堢‘淇?PyTorch 瑁呬簡 CUDA 鐗堟湰锛?```powershell
uv run python -c "import torch; print(torch.cuda.is_available())"
```

### Q7锛歁ilvus / Neo4j / Mongo 鏁版嵁涓簡

鏁版嵁鍒嗗埆瀛樻斁锛?
| 缁勪欢 | 瀛樺偍浣嶇疆 | 绫诲瀷 |
|------|----------|------|
| Milvus | `./volumes/milvus/` | 缁戝畾鎸傝浇锛坆ind mount锛?|
| etcd锛圡ilvus 鍏冩暟鎹級 | `./volumes/etcd/` | 缁戝畾鎸傝浇 |
| milvus-minio锛圡ilvus 鍐呴儴锛?| `./volumes/milvus-minio/` | 缁戝畾鎸傝浇 |
| Neo4j | `./volumes/neo4j/` | 缁戝畾鎸傝浇 |
| MongoDB | Docker 鍛藉悕鍗?`smart_agent_system_mongo_data` | 鍛藉悕鍗凤紙鏀惧湪 Docker Desktop VM 鍐呴儴锛?|

鍙涓嶆墽琛?`docker compose down -v` 鎴栨墜鍔ㄥ垹闄?`volumes/`锛宍docker compose up -d` 閲嶅惎鍚庢暟鎹兘浼氭仮澶嶃€?
> **涓轰粈涔?Mongo 涓嶇敤鏈湴 `volumes/mongo/` 鑰岀敤鍛藉悕鍗凤紵**
> Windows 涓?Docker Desktop 鐨?WSL2 backend 瀵规湰鍦拌矾寰勭粦瀹氭寕杞芥敮鎸佷笉浣斥€斺€擬ongoDB 鍒濆鍖栨椂瑕?`chown`/`chmod` 鏁版嵁鐩綍锛岃法鏂囦欢绯荤粺缈昏瘧缁忓父澶辫触锛堝鍣ㄤ細鐩存帴閫€鍑猴級銆傚懡鍚嶅嵎鐢?Docker 鍦?VM 鍐呴儴绠＄悊锛屽師鐢?ext4锛岀ǔ瀹氬緱澶氥€?>
> 鎯冲浠藉懡鍚嶅嵎鍒版湰鍦帮細
> ```powershell
> docker run --rm -v smart_agent_system_mongo_data:/data -v ${PWD}:/backup alpine tar czf /backup/mongo-backup.tar.gz /data
> ```

### Q8锛氭彁闂?"浣犲ソ" 鍙繑鍥?`鎶辨瓑锛屾湭鎵惧埌鐩稿叧浜у搧...`

**杩欐槸璁捐琛屼负锛屼笉鏄?bug銆?*

姝ょ郴缁熷畾浣嶆槸 **B 绔骇鍝佸鏈嶇煡璇嗗簱**锛屼笉鏄€氱敤鑱婂ぉ鏈哄櫒浜恒€傝妭鐐?`node_item_name_confirm` 鐨勮璁★細

1. LLM 鎻愬彇鐢ㄦ埛闂涓殑**浜у搧鍨嬪彿**
2. 鑻?*娌℃彁鍙栧埌鍟嗗搧鍚?* 鈫?杩涘叆**鍒嗘敮 C**锛岀洿鎺ョ‖缂栫爜杩斿洖 `鎶辨瓑锛屾湭鎵惧埌鐩稿叧浜у搧锛岃鎻愪緵鍑嗙‘鍨嬪彿浠ヤ究鎴戜负鎮ㄦ煡璇€俙锛?*LLM 瀹屽叏涓嶄細琚皟鐢?*锛?3. 鑻ユ彁鍙栧埌鍟嗗搧鍚?鈫?Milvus 鍚戦噺妫€绱㈠榻?鈫?璧板畬鏁?RAG 娴佺▼

杩欐牱璁捐鐨勫ソ澶勶細鏉滅粷 LLM 鍦?*娌℃湁鐭ヨ瘑搴撴敮鎸?*鏃剁殑骞昏鍥炵瓟銆備唬浠凤細涓嶈兘闂茶亰鎵撴嫑鍛笺€?
**姝ｇ‘鐢ㄦ硶**锛氬甫涓婁骇鍝佸瀷鍙锋彁闂紝渚嬪锛?
```
RS-12鏁板瓧涓囩敤琛ㄦ€庝箞浣跨敤锛?RS-12鏁板瓧涓囩敤琛ㄧ殑娴嬮噺鑼冨洿鏄灏戯紵
```

**鎯宠瀹冩敮鎸侀棽鑱婏紵** 鏀?`@app/query_process/agent/nodes/node_item_name_confirm.py:272-275` 鍒嗘敮 C 鐨勯€昏緫锛屽綋 `item_names` 涓虹┖鏃惰浆缁?LLM 鍋氶€氱敤鍥炲锛?*娉ㄦ剰锛氫細寮曞叆骞昏椋庨櫓**锛夈€?
### Q9锛歁ongoDB Compass 宸茶繛涓婏紝浣?filter 鎼滀换浣曟潯浠堕兘娌＄粨鏋?
闆嗗悎閲屾病鏁版嵁銆傚幓 <http://localhost:8001/chat.html> 闂竴鍙ュ甫浜у搧鍨嬪彿鐨勯棶棰橈紙濡?`RS-12鏁板瓧涓囩敤琛ㄦ€庝箞浣跨敤锛焋锛夛紝绛夌瓟妗堝嚭鏉ュ悗鍥?Compass 鐐瑰彸涓婅 馃攧 鍒锋柊锛屽簲鑳界湅鍒?`user` + `assistant` 涓ゆ潯鏂囨。銆?
---

## 涔濄€佹妧鏈爤閫熸煡

| 绫诲埆 | 缁勪欢 | 鐗堟湰 |
|------|------|------|
| Web 妗嗘灦 | FastAPI + Uvicorn | 0.135+ / 0.42+ |
| Agent 缂栨帓 | LangGraph + LangChain | 1.1+ / 1.2+ |
| 澶фā鍨?| 闃块噷鐧剧偧 DashScope锛圤penAI 鍏煎锛?| qwen-flash / qwen3-vl-flash |
| Embedding | BGE-M3锛堢瀵?+ 绋€鐤忔贩鍚堬級 | 鏈湴鎺ㄧ悊 |
| 閲嶆帓 | BGE Reranker Large | 鏈湴鎺ㄧ悊 |
| 鍚戦噺搴?| Milvus Standalone | v2.5.10锛堟湰鍦?Docker锛?|
| 鍚戦噺搴?UI | Attu | v2.5锛堟湰鍦?Docker锛岀鍙?8002锛?|
| 鐭ヨ瘑鍥捐氨 | Neo4j Community | v5.26锛堟湰鍦?Docker锛?|
| 鏂囨。搴?| MongoDB | v6.0锛堟湰鍦?Docker锛岀鍙?27017锛?|
| 鏂囨。搴?UI | MongoDB Compass | 妗岄潰 App锛岄渶鍗曠嫭涓嬭浇 |
| 瀵硅薄瀛樺偍 | MinIO | 鑷缓/鑷€?MinIO 瀹炰緥 |
| PDF 瑙ｆ瀽 | MinerU + magic-pdf | 1.3+ |
| 缃戠粶鎼滅储 | DashScope MCP WebSearch | SSE 娴佸紡 |
| 鍖呯鐞?| uv | 0.11+ |
| 鏃ュ織 | loguru | 0.7+ |

---

閮ㄧ讲鏈夐棶棰橀殢鏃跺弽棣堟棩蹇楀唴瀹癸紝浼氱户缁府浣犵湅銆?
