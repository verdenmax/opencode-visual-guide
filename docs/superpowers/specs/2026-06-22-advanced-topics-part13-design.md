# opencode 图解指南 — 第 13 部分「深入专题」+ 深度扩写 设计文档

- 日期：2026-06-22
- 状态：草案（待用户评审）
- 类型：已完成 64 课指南的**增量扩展**
- 触发：全书 opus 审计后的覆盖缺口分析（4 个 must-add 概念缺口 + 3 处深度偏薄 + 低优先生态）

---

## 1. 概述 (Overview)

64 课指南在**引擎层**已约 90% 完整，但覆盖分析（已逐条核对源码确认存在）发现若干**真正概念性、非顺带可推得**的缺口。本次扩展在**不改动现有 L01–L64 任何编号与交叉引用**的前提下（用户已确认方案 A），新增 **Part 13「深入专题 (Advanced Topics)」**，含 5 门新课（L65–L69），并就地扩写 3 处深度偏薄的既有课。

设计原则：**零重排、增量安全、与既有同标准**。每门新课维持全书既有质量门（zh ≥3000 CJK、≥6 图示、类比卡 + 要点卡、3 个 `<h2>`、测验 3 MCQ + 2 open、双语页内可切换、引用标注来源的真实源码片段）；每个里程碑跑双阶段 opus 审计（源码准确性 + 规范合规）。

## 2. 目标与非目标 (Goals / Non-Goals)

**目标**
- 补齐 4 个 must-add 概念缺口 + 1 课生态一览，作为 Part 13（L65–L69）。
- 就地扩写 L09/L10、L48、L51 三处深度缺口（双语等量、保持各项指标）。
- 全套收尾：glossary L64 增补、L2/L3/L4 `part-13.md`、README 13 部分表、L1-overview 索引、print 重建、全站质检 0/0。

**非目标**
- 不改动 L01–L64 的编号、slug 或彼此交叉引用（"第 N 课"全保持）。
- 不深挖低优先生态的每个包（desktop/app/share/integration/slack/enterprise/infra）到独立课；它们由 L69 一课**鸟瞰式**带过。
- 不重写既有课的核心内容（仅在指定 3 课做加法式扩写）。

## 3. 结构与放置 (Structure & Placement)

- 新增 **Part 13 · 深入专题 (Advanced Topics)**，逻辑定位为「核心 12 部分之后的进阶附录」。
- 新课编号 **L65–L69**，slug 两位编号延续：`65-event-sourcing-sync` … `69-ecosystem-tour`。
- 代码改动点：
  - `src/part13.py` 新建，含 `LESSON_65..69`。
  - `src/registry.py` 注册 5 个新 slug→LESSON。
  - `src/check_html.py`：`MAX_LESSON` 64→69；`PAGES` 增 5 项（归入第 13 部分）。
  - `src/quizzes.py`：新增 5 课测验（L69 视为正常教学课，含测验；非 SOFT_EXEMPT）。
  - `build.py` / `build_print.py` 自动纳入（依赖 PAGES/registry）。
- glossary **L64 仍在原位**（核心课程索引），但：增补新术语与 5 课链接；将"全书完结"措辞调成"核心课程 + 进阶专题"，避免与其后的 Part 13 冲突。

## 4. 五门新课 (New Lessons L65–L69)

每课给：slug、亮点（核心可迁移洞见）、源码锚点、要讲到的关键机制。

### L65 — EventV2 持久事件溯源与单写入同步　`65-event-sourcing-sync`
- **亮点**：一个写入者 + 单调 `seq` ⇒ 任何客户端都能从游标重放到一致状态。这是多客户端一致性与投影历史（L19）的真正地基；补 L11「只讲了 SSE 传输这层皮」的深度盲点。
- **锚点**：`core/src/event.ts`（`Cursor`、`sync.version`/`aggregate`、replay `Stream`）、`core/src/event/sql.ts`（`EventTable` + `EventSequenceTable` 序号）、`opencode/src/sync/README.md`（"only one writer"、`seq`、类型安全订阅）。
- **关键机制**：事件持久化 + 单调序号；游标重放；单写入者一致性；与 L11(SSE 传输)、L19(投影历史)、L15(事件溯源)的关系。

### L66 — 斜杠命令系统　`66-slash-commands`
- **亮点**：命令 = **参数化的 prompt 模板**；自定义命令 / MCP prompt / skill 三种来源被统一成同一种"模板"抽象，一套接口。
- **锚点**：`opencode/src/command/index.ts`（`Info` schema、`command.executed` 事件、`source: command|mcp|skill`、subtask/hints）、`command/template/{initialize,review}.txt`。
- **关键机制**：模板取数与参数注入；三来源归一；与 L43(skills)、L46(MCP) 的呼应。

### L67 — http-recorder 磁带录放测试　`67-http-recorder`
- **亮点**：把一次**真实 provider turn 录成磁带**，让调用真实 LLM 的**非确定 agent 循环**变得可重放、可断言（含密钥脱敏）。
- **锚点**：`packages/http-recorder/{cassette,recorder,redaction,matching,schema}.ts`、`core/test/session-runner-recorded.test.ts`。
- **关键机制**：录制/匹配/回放；redaction 脱敏；如何测一个不确定循环；与 L17(agent 循环)、L28+(协议层)、L63(测试) 呼应。

### L68 — Account 与设备码 OAuth　`68-account-auth`
- **亮点**：无浏览器回调的**设备码（device-code）登录**，以及拿到的**凭据如何喂给 provider**。
- **锚点**：`opencode/src/account/{account,repo,schema,url}.ts`、`opencode/src/auth/index.ts`、`core/src/credential.ts`、`core/src/plugin/provider/openai-auth.ts`。
- **关键机制**：设备码流（AccessToken/DeviceCode）；凭据库存取；与 L35(Copilot provider)、L46(MCP OAuth) 互补。

### L69 — 其余生态一览　`69-ecosystem-tour`
- **亮点**：一个 server，**多种前端与接入**；以及环绕内核的**分发 / 运维 / 企业**生态——"同一内核、广开门户"的最终展开（呼应 L09/L56/L61）。
- **锚点**：`packages/desktop`(Electron)、`packages/app`(web)、`opencode/src/share/*` + `packages/function`(Cloudflare Durable Object `SyncServer`)、`core/src/integration.ts`、`packages/slack`、`packages/enterprise`、`infra/`。
- **关键机制**：鸟瞰式——GUI 前端(desktop/app)、会话分享+云同步、integration 触发器、Slack/enterprise/infra；每块一句话定位 + 与内核的关系，不深挖实现。

## 5. 三处就地深度扩写 (In-place Depth Expansions)

加法式扩写既有课（双语等量增补，保持该课 ≥6 图 / 3 h2 / `<p>` 平衡 / parity）：

- **L09/L10**（server）：点明 V2 API 表面其实在**独立包 `@opencode-ai/server`**（`packages/server/src/{api,groups,handlers,middleware}`），与 `opencode/src/server` 的分工，避免读者混淆"两个 server"。
- **L48**（Drizzle）：补讲支撑它的自研封装 `packages/effect-drizzle-sqlite`/`effect-sqlite-node`——把 Drizzle 查询构造器包成 Effect 服务 + 迁移器。
- **L51**（snapshot/revert）：扩 `opencode/src/worktree/index.ts`——隔离运行用的 worktree。

## 6. 标准与流程 (Standards & Process)

- 每课质量门同全书：zh ≥3000 CJK（`check_html` 同正则计数）、≥6 图示（`layers/vflow/flow/cols/cellgroup/timeline/trace` + `table.t`，**双语各 ≥3**）、3 个 `<h2>`（双语相等）、`<p>`/`</p>` 平衡且双语相等、类比卡 + `本课要点`/`Key points` 卡、测验（quizzes.py，3 MCQ 4 选项 + 2 open，`answer` 写 0、render 时 `_shuffle` 重排）。
- 内容用 `r"""..."""` 原始字符串；模板字面量直接写 `${x}`（**不要** `${'$'}` 转义——会漏成字面文本）。
- 每个里程碑（每课或每小批）跑**双阶段 opus 审计**（model `claude-opus-4.8`、high）：① 源码准确性逐条核对 file:line；② 规范/parity/亮点/测验。审计发现先核对源码再修。
- 每课：build + check_html（grep 该 slug 无 warning）+ check_links + 提交（含 Co-authored-by）。

## 7. 收尾 (Closeout)

- glossary **L64** 增补新术语（EventV2/单写入 sync、slash command、http-recorder、device-code OAuth、Durable Object 等）+ 5 课跳转链接；调整结尾措辞。
- 文档：`docs/L2-parts/part-13.md`、`docs/L3-details/part-13.md`、`docs/L4-api/part-13.md`；`docs/L2-parts/README.md` 加 part-13 行；`docs/L1-overview.md` 13 部分索引 + 文档进度。
- `README.md` 12→13 部分表。
- 重建 `print_zh.html`/`print_en.html`；`check_html.py` **全站 0 error/0 warning**（69 课 + index）；`check_links.py` 全绿；`build.py` 重跑无 diff。
- 最终审计：抽查 5 新课 + 3 扩写课的 parity/亮点/图示/字数 + 术语表链接全解析 → 修正 → 最终 commit。

## 8. 验收 (Acceptance)

- 69 课全部 build/check 通过；5 新课 + 3 扩写课双语 parity；glossary/README/L1-L4/print 全部同步；全套质检 0/0 绿；每里程碑双阶段审计通过并修复。
