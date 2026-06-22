# Part 13「深入专题」(L65–L69) + 深度扩写 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不改动现有 L01–L64 编号的前提下，新增 Part 13（5 课 L65–L69）并就地扩写 3 处深度缺口，保持全书既有质量门与双语 parity。

**Architecture:** 新建 `src/part13.py`（`LESSON_65..69`），注册进 `registry.py`，`check_html.py` 的 `MAX_LESSON`/`PAGES` 扩到 69；每课走「研究源码 → 写中文 → 补英文 parity → 加测验 → build/check → 提交」既有流程；每个里程碑跑双阶段 opus 审计；最后扩写 3 课 + 收尾（glossary/docs/README/print）。

**Tech Stack:** Python 3 零依赖静态站点生成器（`build.py`/`build_print.py`/`check_html.py`/`check_links.py`）；课程内容为 `r"""..."""` 原始字符串内嵌中英双语 HTML 片段；`quizzes.py` 测验。

**质量门（每课必须满足）：**
- zh ≥3000 CJK（`check_html` 用 `[\u4e00-\u9fff]` 计数，与本机校验同正则）
- ≥6 图示**双语各 ≥3**（类名 `layers/vflow/flow/cols/cellgroup/timeline/trace` + `<table class="t">`）
- 3 个 `<h2>`（中英相等）；`<p>`/`</p>` 平衡且中英相等
- 类比卡（`card analogy`）+ 要点卡（含 `本课要点` / `Key points`）
- 测验：3 MCQ（每题 4 选项，`answer` 写 0）+ 2 open；`import quizzes` 通过
- 模板字面量直接写 `${x}`，**禁止** `${'$'}`（会漏成字面文本）
- build + `check_html`（grep 该 slug 无 warning）+ `check_links` 全绿后提交（含 `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`）

**命令（在 `src/` 下运行）：** `python3 build.py`、`python3 check_html.py`、`python3 check_links.py`、`python3 build_print.py`

---

## File Structure

| 文件 | 职责 | 动作 |
| --- | --- | --- |
| `src/part13.py` | Part 13 五课内容（`LESSON_65..69` dict，中英双语） | Create |
| `src/registry.py` | slug → LESSON 映射 | Modify（加 5 项） |
| `src/check_html.py` | `MAX_LESSON`、`PAGES`（含部分归属） | Modify（64→69，PAGES 加 5 项） |
| `src/quizzes.py` | 每课测验 | Modify（加 5 课测验） |
| `src/part3.py` | L09/L10 深度扩写 | Modify |
| `src/part9.py` | L48 深度扩写 | Modify |
| `src/part9.py`/`part11.py` | L51 深度扩写（确认 L51 所在文件） | Modify |
| `docs/L2-parts/part-13.md`、`docs/L3-details/part-13.md`、`docs/L4-api/part-13.md` | 分层文档 | Create |
| `docs/L2-parts/README.md`、`docs/L1-overview.md`、`README.md` | 索引/状态/13 部分表 | Modify |
| `lessons/*.html`、`index.html`、`print_*.html` | 生成产物 | 重建（由脚本生成） |

---

## M0 — 脚手架 (Scaffolding)

让 5 个新 slug 能 build（用占位内容先跑通管道，再逐课填充）。

**Files:** Create `src/part13.py`；Modify `src/registry.py`、`src/check_html.py`

- [ ] **Step 1: 确认现有约定**

Run（在 `src/`）：
```bash
grep -n "MAX_LESSON" check_html.py
grep -n "from placeholder import wip\|def wip" placeholder.py
sed -n '/^PAGES/,/^]/p' check_html.py | tail -20   # 看 PAGES 结构与「部分」如何标注
tail -8 registry.py
```
Expected: `MAX_LESSON = 64`；`placeholder.wip(zh_title, en_title)` 存在；PAGES 是含部分分组的列表；registry 末尾是 part12 的三项映射。

- [ ] **Step 2: 创建 `src/part13.py` 占位**

```python
"""Part 13 (Advanced Topics · 深入专题) content."""
from placeholder import wip

LESSON_65 = wip('EventV2 持久事件溯源与单写入同步', 'Event sourcing & single-writer sync')
LESSON_66 = wip('斜杠命令系统', 'Slash commands')
LESSON_67 = wip('http-recorder 磁带录放测试', 'http-recorder tape testing')
LESSON_68 = wip('Account 与设备码 OAuth', 'Account & device-code OAuth')
LESSON_69 = wip('其余生态一览', 'Ecosystem tour')
```

- [ ] **Step 3: 注册 5 个 slug（`registry.py`）**

在 `registry.py` 顶部 import 区加 `import part13`，并在 CONTENT 映射 part12 三项之后追加：
```python
    '65-event-sourcing-sync.html': part13.LESSON_65,
    '66-slash-commands.html': part13.LESSON_66,
    '67-http-recorder.html': part13.LESSON_67,
    '68-account-auth.html': part13.LESSON_68,
    '69-ecosystem-tour.html': part13.LESSON_69,
```

- [ ] **Step 4: 扩 `check_html.py` 的 `MAX_LESSON` 与 `PAGES`**

`MAX_LESSON = 64` → `MAX_LESSON = 69`。在 `PAGES` 末尾（part12 之后）按既有「部分分组」格式追加 Part 13 的 5 项（参照 Step 1 看到的 PAGES 结构，新增一个「第 13 部分 · 深入专题」分组，含 5 个 fname + 中英标题）。

- [ ] **Step 5: build 跑通**

Run（`src/`）：
```bash
python3 -c "import part13, registry, quizzes; print('OK')"
python3 build.py 2>&1 | tail -3
python3 check_html.py 2>&1 | tail -1
python3 check_links.py 2>&1 | tail -1
```
Expected: import OK；build 生成 69 课 + index；check_html 仅对 5 个占位课报 WARN（占位无图/字数，预期），ERROR 为 0；check_links 全解析。

- [ ] **Step 6: 提交**

```bash
git add -A && git commit -m "chore(M13): scaffold Part 13 (L65-69) placeholders + registry + MAX_LESSON"
```

---

## M1 — L65 EventV2 持久事件溯源与单写入同步

**slug:** `65-event-sourcing-sync.html` ｜ **Files:** Modify `src/part13.py`（`LESSON_65`）、`src/quizzes.py`

**亮点（核心洞见）：** 因为**只允许一个写入者**，就不需要分布式时钟/因果排序——一个**单调递增的 `seq`** 就给出全序；任何其他设备只要**拉事件日志、本地重放到某游标**，就能到达一致状态。这是多客户端一致性与 L19「投影历史」的真正地基，补 L11「只讲了 SSE 传输」的深度盲点。

**已核实的源码事实（务必照此写，勿杜撰）：**
- `core/src/event.ts`：`export * as EventV2`。`Cursor` = 品牌化 `NonNegativeInt`（"durable aggregate continuation position for embedded replay streams"）。`Definition` = `{version:number, aggregate:string, data:Schema}`。`Payload` = `{…, seq?:number, version?:number, replay?:boolean}`（`seq` 注释："Durable aggregate order, populated while synchronized events are projected"；`replay` 注释："Internal replay marker for projectors that own non-replicated operational state"）。`Projector`/`CommitGuard`/`Listener`/`Sync` 都是 `(event:Payload)=>Effect<void>`。`SerializedEvent` = `{…, seq:number, aggregateID:string}`。`CursorEvent` = `{cursor:Cursor, …}`。`versionedType(type, version)` 返回 `` `${type}.${version}` ``。`InvalidSyncEventError`（TaggedErrorClass）。
- `core/src/event/sql.ts`：`EventSequenceTable("event_sequence")` = `{aggregate_id: text PK, seq: integer notNull, owner_id: text?}`。`EventTable("event")` = `{id: text PK ($type EventV2.ID), aggregate_id: text→references EventSequenceTable.aggregate_id onDelete cascade, seq: integer notNull, type: text notNull, data: text json notNull}` + `uniqueIndex("event_aggregate_seq_idx").on(aggregate_id, seq)` + `index("event_aggregate_type_seq_idx").on(aggregate_id, type, seq)`。
- `opencode/src/sync/README.md`：「**Syncing with only one writer**」——"only one device is allowed to write, we don't need any kind of sophisticated distributed system clocks or causal ordering. We implement total ordering with a simple sequence id (a number) and increment it by one every time we generate an event." 其他设备"sync"=拿事件日志重放。**向后兼容 `Bus`**（`SyncEvent.run/subscribeAll`，类型安全；不重复既有 `session.created` 等）。

**建议的 3 个 `<h2>`：**
1. 单写入者：为什么一个 `seq` 就够（vs 分布式时钟）
2. 事件表与序号：`EventTable` + `EventSequenceTable`、aggregate 内全序、`uniqueIndex(aggregate_id, seq)`
3. 游标重放与同步：`Cursor`、replay `Stream`、其他设备如何追平；与 `Bus`/SSE(L11)/投影(L19) 的关系

**建议图示（≥6，双语各 ≥3）：** `cols`（单写入 vs 分布式共识，对比）；`cellgroup`（EventV2 核心类型：Cursor/Definition/Payload/Projector…）；`layers` 或 `flow`（写：生成事件→分配 seq→落 EventTable）；`trace`（同步：设备 B 带 cursor 拉日志→重放→追平）；`table.t`（两张表字段）；`vflow`（与 L11 SSE / L19 投影 / L15 事件溯源的关系）。

**跨课呼应：** L11（SSE 是事件的**传输**，本课是事件的**持久化+定序+同步**）、L19（投影历史从事件投影出读模型）、L15（输入 admit 的事件溯源）、L48/L49（SQLite 表）、L08（KeyedMutex「按 key 排队」≠ 这里的单写入定序，可点一句区分）。

- [ ] **Step 1: 深读源码确认细节**

Run（在 `/home/verden/course/opencode`）：
```bash
sed -n '1,120p' packages/core/src/event.ts
sed -n '1,40p' packages/core/src/event/sql.ts
sed -n '1,80p' packages/opencode/src/sync/README.md
```
逐条核对上面「已核实事实」，补全任何要引用的签名/常量。

- [ ] **Step 2: 写中文（`LESSON_65['zh']`）**

把 `LESSON_65 = wip(...)` 替换为完整 dict：先写 zh（结构 = `<p class="lead">` 开场 + 一段双洞见 + `card analogy` + 3×`<h2>`含图示 + `card macro`/`card detail` + `card key`(本课要点)），en 先放 `__EN_L65__` 占位。**目标 zh ≥3050 CJK、6 图示、3 h2、`<p>` 平衡。** 类比建议：单写入者像「一个班只有一个人记流水账，旁人抄账」——无需对表。

- [ ] **Step 3: 校中文指标**

Run（`src/`）：
```bash
python3 -c "import re,part13 as p; t=p.LESSON_65['zh']; print('CJK',len(re.findall(r'[\u4e00-\u9fff]',t)),'dia',sum(t.count(f'class=\"{c}\"') for c in ('layers','vflow','flow','cols','cellgroup','timeline','trace'))+t.count('<table class=\"t\"'),'h2',t.count('<h2'),'p',t.count('<p>')+len(re.findall(r'<p ',t)),'/p',t.count('</p>'))"
```
Expected: CJK ≥3000、dia ≥6、h2=3、p==/p。不足则补写。

- [ ] **Step 4: 补英文 parity（替换 `__EN_L65__`）**

逐元素翻译，**结构完全对齐**：同样 3 h2（标题为对应英译、同序）、同样 6 图示（同类型同位置）、`<p>`/`</p>` 与 zh 相等。

- [ ] **Step 5: 校 parity**

Run（`src/`）：
```bash
python3 -c "import re,part13 as p
for L in ('zh','en'):
    t=p.LESSON_65[L]; print(L,'dia',sum(t.count(f'class=\"{c}\"') for c in ('layers','vflow','flow','cols','cellgroup','timeline','trace'))+t.count('<table class=\"t\"'),'h2',t.count('<h2'),'p',t.count('<p>')+len(re.findall(r'<p ',t)),'/p',t.count('</p>'))"
```
Expected: zh/en 的 dia、h2、p、/p 全相等。

- [ ] **Step 6: 加测验（`quizzes.py`）**

在 `QUIZZES = {` 之后插入 `"65-event-sourcing-sync.html": {…}`（3 MCQ + 2 open，`answer` 写 0，双语）。MCQ 建议：①单写入为何免分布式时钟（正解=单调 seq 给全序、设备重放追平）；②`EventSequenceTable`/`EventTable` 与 `uniqueIndex(aggregate_id,seq)` 的作用；③本课(持久化+定序+同步) vs L11(SSE 传输) 的区别。open：单写入模型的取舍；事件溯源读模型（呼应 L19）。
Run：`python3 -c "import quizzes; print('65-event-sourcing-sync.html' in quizzes.QUIZZES)"` → True。

- [ ] **Step 7: build + check + 提交**

Run（`src/`）：
```bash
python3 build.py 2>&1 | tail -1
python3 check_html.py 2>&1 | grep "65-event" ; echo "above empty = clean"
python3 check_links.py 2>&1 | tail -1
```
Expected: build OK；`65-event` 无 WARN（grep 空）；links 全解析。然后：
```bash
git add -A && git commit -m "feat(M13): lesson 65 EventV2 event sourcing & single-writer sync"
```

---

> 后续里程碑（M2–M7）见下文续写。

---

## M2 — L66 斜杠命令系统

**slug:** `66-slash-commands.html` ｜ **Files:** Modify `src/part13.py`（`LESSON_66`）、`src/quizzes.py` ｜ **流程同 M1 的 Step 1–7（研究→写中文→校指标→补英文→校 parity→加测验→build/check/提交）。**

**亮点：** 命令 = **参数化的 prompt 模板**；自定义命令 / MCP prompt / skill 三种来源被 `source` 字段统一成同一种「模板 + 占位符」抽象，一套 `Service` 接口取用。

**已核实源码事实（`opencode/src/command/index.ts`）：**
- `Info = Schema.Struct({ name?, agent?:string, model?:string, source?:Schema.Literals(["command","mcp","skill"]), template:Schema.Unknown, subtask?:boolean, hints:Schema.Array(String) })`；`type Info` 把 `template` 收窄成 `Promise<string> | string`（注释："Some command templates are lazy promises from MCP prompt resolution"）。
- `Event.executed` = `{ type:"command.executed", schema:{…} }`。
- `hints(template)`：用 `template.match(/\$\d+/g)` 提取 `$1,$2,…` 编号占位符；若含 `$ARGUMENTS` 也加入。即「模板里有哪些参数槽」。
- `Default = { initialize, review }`，模板来自 `./template/initialize.txt`、`./template/review.txt`（`import …txt`）。
- `Service`（`Context.Service…("@opencode/Command")`）+ `layer`，接口 `get(name)`/`list()`。
- **三来源**：`source: "command" | "mcp" | "skill"`——内置/用户命令、MCP 暴露的 prompt、skill，全部塑形成同一个 `Info`。

**建议 3 个 `<h2>`：** ① 命令 = 参数化模板（`Info`、`template`、`$1/$ARGUMENTS` 占位符与 `hints`）；② 三源归一（command/mcp/skill 一套接口，`source` 区分，lazy promise 容纳 MCP）；③ 执行与事件（`get/list`、`command.executed`、subtask/agent/model 覆盖）。
**建议图示（≥6，双语各 ≥3）：** `cellgroup`（`Info` 字段）；`cols`（命令 vs 朴素硬编码 prompt）；`flow`（取命令→填占位符→成 prompt→执行）；`vflow` 或 `layers`（三来源→统一 `Info`）；`trace`（`/review $1` 一次调用的展开）；`table.t`（`$N`/`$ARGUMENTS` 占位符语义）。
**跨课呼应：** L43（skills 也是「名字常驻、正文按需」，命令把 skill 当一种 source）、L46（MCP prompt 作为一种 source，lazy promise）、L36/L47/L53（统一模子刻同形）。

---

## M3 — L67 http-recorder 磁带录放测试

**slug:** `67-http-recorder.html` ｜ **Files:** Modify `src/part13.py`（`LESSON_67`）、`src/quizzes.py` ｜ **流程同 M1 Step 1–7。**

**亮点：** 把一次**真实 provider turn 录成「磁带（cassette）」**，让一个会调用真实 LLM、本质**非确定**的 agent 循环，变成**可重放、可断言**的确定测试——还顺手把密钥**脱敏**掉。

**已核实源码事实：**
- `packages/http-recorder/src/index.ts`：`export const HttpRecorder = { http, socket }`；命名空间类型 `CassetteMetadata`、`RecorderOptions`、`RedactOptions`、`RequestMatcher`、`RequestSnapshot`。即 HTTP 与 WebSocket 两种录放。
- `redaction.ts`：`REDACTED = "[REDACTED]"`；`DEFAULT_REDACT_HEADERS`（含 `authorization`、`x-api-key`、`x-goog-api-key`…）、`DEFAULT_REDACT_QUERY`——录制时自动把敏感头/查询参数替换成 `[REDACTED]`。
- `matching.ts`：`RequestMatcher`——回放时如何把进来的请求匹配到磁带里的某次快照。
- `cassette.ts`/`recorder.ts`/`schema.ts`：磁带的存储格式与录制器。
- `core/test/session-runner-recorded.test.ts`：用真实响应磁带**回放整条 V2 runner**——直接呼应 L17 的 agent 循环。

**建议 3 个 `<h2>`：** ① 为什么难测：非确定的循环（模型每次不一样、还要真花钱）；② 磁带机制（录制→匹配→回放，`RequestMatcher`、HTTP/socket 两路）；③ 脱敏与落地（`REDACTED`、默认脱敏头/查询；`session-runner-recorded.test.ts` 回放整条 runner）。
**建议图示（≥6）：** `cols`（真实调用 vs 磁带回放）；`flow`（录制：请求→脱敏→存磁带）；`trace`（回放：请求→matcher→取磁带响应→断言）；`cellgroup`（核心类型 Cassette/Recorder/Matcher/Redact）；`table.t`（默认脱敏的头/查询）；`vflow`（与 L17 agent 循环 / L28+ 协议层的关系）。
**跨课呼应：** L17（agent 循环本质非确定，这正是被回放的对象）、L28–L35（协议层就是被录的 HTTP/socket）、L63（测试哲学：测真实、可复现——本课是「测真实」的极致手法）。

---

## M4 — L68 Account 与设备码 OAuth

**slug:** `68-account-auth.html` ｜ **Files:** Modify `src/part13.py`（`LESSON_68`）、`src/quizzes.py` ｜ **流程同 M1 Step 1–7。**

**亮点：** **设备码（device-code）登录**——在没有浏览器回调的 CLI/终端里，靠「显示一个码、后台轮询」完成 OAuth；拿到的**凭据（OAuth token 或 API Key）存进凭据库**，再喂给 provider 去调模型。

**已核实源码事实：**
- `opencode/src/account/account.ts`：`AccessToken`、`DeviceCode` 类型；`DeviceAuth { device_code: DeviceCode, … }`、`TokenRefresh { access_token: AccessToken, … }`；用 `Cache`/`Clock`/`Duration`（token 过期与轮询节奏）；`AccountOrgs`/`ActiveOrg`/`RemoteConfig`（账号与组织）。`DurationFromSeconds`（秒↔Duration 编解码）。
- `core/src/credential.ts`：`export * as Credential`；`OAuth` 类、`Key` 类、`Info = Schema.Union([OAuth, Key])`、`Stored`；`CredentialTable`（`credential/sql`）；`Interface`（存取凭据）。即**凭据有两形态**：OAuth token / 直接 API Key。
- `core/src/plugin/provider/openai-auth.ts`：凭据如何接到 provider（呼应 L35 Copilot、L47 provider 插件）。

**建议 3 个 `<h2>`：** ① 设备码流：CLI 没浏览器回调怎么办（显示码→后台轮询→拿 token）；② 凭据库：`OAuth | Key` 两形态、`Stored`、`CredentialTable`；③ 喂给 provider：凭据如何被 provider 取用（呼应 L35/L47）。
**建议图示（≥6）：** `trace`（设备码 5 步：请求→显示码→用户授权→轮询→拿 token）；`cols`（设备码 vs 浏览器回调 OAuth）；`cellgroup`（Credential.OAuth / Key / Stored 字段）；`flow`（凭据存取：login→存库→provider 取用）；`table.t`（凭据两形态对比）；`vflow`（account/credential/provider 三者关系）。
**跨课呼应：** L35（Copilot provider 用凭据）、L46（MCP OAuth）、L47（provider 插件接源）、L48/L49（CredentialTable 也是 SQLite 持久化）。

---

## M5 — L69 其余生态一览

**slug:** `69-ecosystem-tour.html` ｜ **Files:** Modify `src/part13.py`（`LESSON_69`）、`src/quizzes.py` ｜ **流程同 M1 Step 1–7（鸟瞰式，但仍满足全部质量门）。**

**亮点：** **一个 server，多种前端与接入**；以及环绕内核的**分发 / 运维 / 企业**生态——这是 L09「server 拥有一切」、L56「数据与表现分离」、L61「ACP 被编辑器消费」的最终展开：内核广开门户，长出 TUI 之外的一整圈面孔与接入点。

**已核实源码事实（鸟瞰，每块一句话定位即可，勿深挖实现）：**
- **GUI 前端**：`packages/desktop`（Electron 包住 web app）、`packages/app`（SolidJS web UI，与 TUI 共享同一 SDK/SSE）。
- **会话分享 + 云同步**：`opencode/src/share/{session,share-next}.ts` + `packages/function/src/api.ts`（`SyncServer extends DurableObject<Env>`，Cloudflare Durable Object，`SYNC_SERVER` 命名空间）——把本地单写入 sync（L65）投影到云端可分享只读视图。
- **Integration 自动化/接入**：`core/src/integration.ts`（`export * as Integration`，`IntegrationSchema`/`MethodID`/`IntegrationConnection`）——声明式触发器/连接把外部事件接进 session。
- **Slack / 企业 / 基础设施**：`packages/slack`、`packages/enterprise`、`infra/`（SST）。
- 收束：所有这些都连同一个 server（L09），靠同一套 SDK/事件（L11/L12）。

**建议 3 个 `<h2>`：** ① 多前端：desktop/app/TUI 共享一个 server（呼应 L09/L56）；② 分享与云同步：`share/*` + `function`(Durable Object)，本地单写入→云端只读（呼应 L65）；③ 接入与运维：integration 触发器、slack/enterprise/infra 一句话定位。
**建议图示（≥6）：** `layers` 或 `cols`（一个 server → 多前端）；`cellgroup`（生态各包一句话）；`flow`（本地 session → share → 云 Durable Object → 他人只读）；`vflow`（integration 触发器接外部事件）；`table.t`（生态包 × 职责 × 与内核关系）；`trace` 或 `cols`（TUI/web/desktop 三前端同源对比）。
**跨课呼应：** L09（server 拥有一切）、L11/L12（SSE/SDK 是多前端的共同总线）、L56（数据与表现分离）、L61（ACP 也是一种「门户」）、L65（云同步建立在单写入 sync 上）。

---

> 续：M6（深度扩写）、M7（收尾与最终审计）见下文。

---

## M6 — 三处就地深度扩写

加法式扩写：在既有课里**双语等量增补**一小节（1 个 `<h2>` 子节 + 1–2 段 + 可选 1 个小图），**中英同步**，扩完该课 `<p>`/`</p>` 仍平衡、zh==en、图示双语仍各 ≥3、CJK 仍 ≥3000。每处扩写后单独 build+check+提交。

### M6.1 — L09/L10：点明独立的 `@opencode-ai/server` 包
**File:** Modify `src/part3.py`（`LESSON_09` 或 `LESSON_10`，择内容更贴的一课）

- [ ] **Step 1:** 读源确认：`packages/server/src/api.ts` 有 `export const Api = HttpApi.make("server")`；`packages/server/src/groups/`（agent/command/credential/event/fs/health/integration/location/message…）+ `handlers/` + `middleware/`。这是 **V2 API 表面所在的独立包**，与 `packages/opencode/src/server`（装配/启动那层）分工不同。
- [ ] **Step 2:** 在 L09 或 L10 增一小节（zh+en），讲清「两个 server」：`@opencode-ai/server`（`packages/server`）定义 API 组与 handler 的**契约表面**；`opencode/src/server` 负责**把它装配成可跑的本地服务器**（`webHandler`、MDNS、WebSocket 等，L09 已讲）。避免读者混淆。
- [ ] **Step 3:** 校 parity（zh==en 的 p/h2/dia）→ build → `check_html` grep 该 slug 无 WARN → `check_links` → 提交 `docs(M13): clarify @opencode-ai/server package in L09/L10`。

### M6.2 — L48：补讲自研 `effect-drizzle-sqlite` 封装
**File:** Modify `src/part9.py`（`LESSON_48`）

- [ ] **Step 1:** 读源确认：`packages/effect-drizzle-sqlite/src/`（`effect-sqlite/{driver,index}`、`sqlite-core`、`up-migrations`、`internal`、`index.ts`）与 `packages/effect-sqlite-node`——把 Drizzle 查询构造器**包成 Effect 服务**并提供**迁移器**，是 L48 默认在用却没拆的底座。
- [ ] **Step 2:** 在 L48 增一小节（zh+en）：L48 讲的「代码即 schema + 双路迁移」之所以能在 Effect 世界里顺滑运转，靠的是这层自研封装——它把 Drizzle 的 driver/查询/迁移都套进 Effect 的 Service/Layer（呼应 L06/L08「为自己造趁手件」）。
- [ ] **Step 3:** 校 parity → build → check → 提交 `docs(M13): cover effect-drizzle-sqlite wrapper in L48`。

### M6.3 — L51：扩 worktree（隔离运行）
**File:** Modify `src/part9.py`（`LESSON_51`）

- [ ] **Step 1:** 读源确认：`packages/opencode/src/worktree/index.ts`——`Event { worktree.ready, worktree.failed }`、`Info`（`annotate identifier:"Worktree"`）、`CreateInput`、`import { Git }`。用 git worktree 给会话开**隔离的工作副本**。
- [ ] **Step 2:** 在 L51（快照/回退/影子 git）增一小节（zh+en）：除了「影子 git 快照」，opencode 还能用 **git worktree** 把一次运行隔离到独立工作副本（`worktree.ready/failed` 事件），与 L51 的「复用 git」主题一脉相承，也呼应 L61 move-session 的「会话可搬家」。
- [ ] **Step 3:** 校 parity → build → check → 提交 `docs(M13): expand worktree (isolated runs) in L51`。

---

## M6.R — 新内容双阶段 opus 审计

对 **L65–L69 五课 + 三处扩写**跑双阶段审计（同全书既有流程）。

- [ ] **Step 1: 派两个后台 `code-review` 子代理**（model `claude-opus-4.8`，reasoning_effort high，并行）：
  - **源码准确性**：逐条把 L65–L69 + 扩写的每个技术断言核对 `/home/verden/course/opencode` 源码 file:line（EventV2 类型/表、command Info/hints、http-recorder redaction/matching、account DeviceCode/Credential、生态各包、server/effect-drizzle/worktree）。
  - **规范合规**：角度/亮点是否兑现、zh/en parity（同事实+同段落，警惕 en 漏段）、图示双语各 ≥3、CJK、测验 `opts[0]` 真为正解、术语一致。
- [ ] **Step 2:** 读两份报告，**逐条先核对源码再修**（HIGH/MED 必修，LOW 酌情）。
- [ ] **Step 3:** 修完 build + `check_html`（全站）+ `check_links` 全绿 → 提交 `fix(M13): audit fixes for L65-69 + expansions`。

---

## M7 — 收尾 (Closeout)

**Files:** Modify `src/part12.py`(`LESSON_64` glossary)、`docs/*`、`README.md`；Create `docs/{L2-parts,L3-details,L4-api}/part-13.md`

- [ ] **Step 1: 更新 glossary L64**
  - 增补新术语行（链接到新课）：EventV2/单写入 sync→L65、斜杠命令→L66、http-recorder→L67、设备码 OAuth/凭据库→L68、Durable Object 云同步→L69。
  - 「可迁移智慧」表可加一行或在相应行补 L65/L67 范例（如「复用成熟生态」加 L67 录放、「找准接缝」加 L65 单写入）。
  - 调整结尾措辞：把「全书 64 课圆满收尾」改为「核心 12 部分 64 课 + 进阶专题（Part 13, L65–69）」，避免与其后的 Part 13 冲突。zh+en 同步，保持 SOFT_EXEMPT 下的双语与链接解析。

- [ ] **Step 2: 写 `docs/L2-parts/part-13.md` / `L3-details/part-13.md` / `L4-api/part-13.md`**
  - 照 part-11/part-12 既有格式：L2=职责/覆盖范围表/与相邻部分关系/核心心智模型；L3=逐课细节（L65–L69）；L4=源文件→课对照表（含扩写涉及的 server/effect-drizzle/worktree）。

- [ ] **Step 3: 更新索引/状态**
  - `docs/L2-parts/README.md`：加 `part-13.md … 已完成` 行。
  - `docs/L1-overview.md`：13 部分索引加一行（Part 13 · 深入专题 · L65–69 · 依赖「全部」）；文档进度更新为 13 部分 / 69 课。
  - `README.md`：12→13 部分表，加 Part 13 行（L65–69）；课程数 64→69、12→13 部分（含中英两处）。

- [ ] **Step 4: 重建产物 + 全站质检**

Run（`src/`）：
```bash
python3 build.py >/dev/null 2>&1 && python3 build_print.py >/dev/null 2>&1
python3 check_html.py 2>&1 | tail -1     # 期望：Checked 69 lessons + index — 0 error(s), 0 warning(s)
python3 check_links.py 2>&1 | tail -1    # 期望：all N internal links resolve
git status --short                        # 重跑 build 后应无未提交 diff（确定性）
```
Expected: check_html **69 课 0/0**；check_links 全解析；重建无 diff。

- [ ] **Step 5: 最终全书 parity 抽查**

Run（`src/`）：复用既有全书 parity 扫描脚本，确认 69 课中只有已知的 L09/L37/L39 美观差（其余 zh==en、p 平衡、h2 相等），且 5 新课 + 3 扩写课全 parity。

- [ ] **Step 6: 提交收尾**

```bash
git add -A && git commit -m "docs(M13): glossary + L2/L3/L4 part-13 + README/L1 + print; finalize Part 13"
```

---

## Self-Review（计划自检）

- **Spec 覆盖**：spec §4 五课 ↔ M1–M5；§5 三扩写 ↔ M6.1–M6.3；§6 标准 ↔ 各课 7 步质量门 + M6.R 审计；§7 收尾 ↔ M7；§3 结构改动 ↔ M0。无遗漏。
- **占位符扫描**：无 TBD/TODO；每课给真实源码锚点 + 已核实事实 + 图示/角度/跨课建议；M0 给可执行命令。课程**内容**为执行产物（内容创作型项目预期），质量由各课质量门 + M6.R 审计保证。
- **类型/命名一致**：5 个 slug（`65-event-sourcing-sync` … `69-ecosystem-tour`）在 part13.py / registry.py / check_html PAGES / quizzes keys 严格一致；`MAX_LESSON=69` ↔ 69 课；glossary/README/L1 的「69 课 / 13 部分」一致。
- **依赖守护**：M0 先让 5 课占位 build 通过（满足 build.py 的 PAGES↔CONTENT 一一对应），再逐课填充；每课 build+check 后提交。


