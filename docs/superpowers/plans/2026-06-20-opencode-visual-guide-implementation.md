# opencode 图解学习指南 实施计划 (Implementation Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一份 **64 课、中英双语、源码内部导向**的 opencode 图解学习指南静态站点，复用参考项目（llama-cpp-visual-guide）的纯 Python 零依赖生成器，分 **M0–M12** 里程碑渐进交付；每课达到质量门（双语 parity、≥6 图示块、zh ≥3000 CJK、真实代码引用、自测题），每个里程碑经独立 subagent 两阶段审计。

**Architecture:** Fork 参考项目 `src/` 生成器（`shell/build/build_print/check_html/check_links/registry/quizzes`）。**M0 一次性立全 64 课 `PAGES` 骨架 + 占位内容**，确保 `build.py` + `check_html.py` + `check_links.py` 全绿（占位课产生 WARN，作为"未完成"看板）。**M1–M12 每个里程碑用真实内容替换一个 Part 的占位**，清零该部分 WARN，同步 L1–L4 文档，经 subagent 审计后提交。生成的 HTML 入库、与源同步（重跑 `build.py` 无 diff）。

**Tech Stack:** Python 3（零依赖生成器）、HTML/CSS（内嵌于 `shell.py`）、GitHub Actions（Pages 部署）。讲解对象 opencode 的技术栈为 Bun / TypeScript / Effect / Drizzle+SQLite / SolidJS+opentui。

**参考文档：** 设计 spec 在 `docs/superpowers/specs/2026-06-20-opencode-visual-guide-design.md`（含 64 课完整大纲与每课源码锚点，本计划不重复）。

---

## 里程碑总览 (Milestones)

| M | 范围 | 课程 | 主要产物 |
| --- | --- | --- | --- |
| **M0** | 脚手架 | — | fork 生成器、全 64 PAGES 骨架 + 占位、品牌、README/LICENSE/deploy/docs 骨架；build+check 全绿 |
| **M1** | Part 1 宏观全景 | L01–04 | 4 课真实内容（确立范式样板） |
| **M2** | Part 2 Effect 地基 | L05–08 | 4 课 |
| **M3** | Part 3 客户端/服务器 | L09–13 | 5 课 |
| **M4** | Part 4 Session/agent 循环 ⭐ | L14–20 | 7 课 |
| **M5** | Part 5 Context Epoch ⭐ | L21–27 | 7 课 |
| **M6** | Part 6 LLM 协议层 ⭐ | L28–35 | 8 课 |
| **M7** | Part 7 工具系统 | L36–43 | 8 课 |
| **M8** | Part 8 配置/Agents/Provider | L44–47 | 4 课 |
| **M9** | Part 9 持久化 | L48–51 | 4 课 |
| **M10** | Part 10 TUI | L52–56 | 5 课 |
| **M11** | Part 11 扩展集成 | L57–61 | 5 课 |
| **M12** | Part 12 实战/速查 + 收尾 | L62–64 | 3 课 + print 版 + 全站收口 |

每个里程碑的统一收尾：`build.py` → `check_html.py`/`check_links.py`（该 Part 0 WARN）→ 同步 L1–L4 文档 → **subagent 两阶段审计** → commit。

---

## 全局约定 (Conventions)

> 以下约定是所有内容里程碑（M1–M12）的执行规范，等价于"每课的验收标准"。

### C.1 每课内容结构 (Lesson skeleton)

每课在 `partK.py` 中是一个 `LESSON_NN = {"zh": r"""...""", "en": r"""..."""}`。zh 与 en 各是一段富 HTML 片段（不含 `<html>/<head>/<body>`，外壳由 `shell.page()` 套上）。每课**双语都**应包含、且顺序大致对应：

1. **开篇导语** `<p class="lead">…</p>`：1 段，点明"这一课解决什么问题、为什么重要"。
2. **类比卡** `<div class="card analogy"><div class="tag">🔌 生活类比 / Analogy</div>…</div>`：用一个贴切的日常类比降低门槛（check_html 要求 `card analogy`）。
3. **正文小节** 若干 `<h2>`：每节= 1–3 段解释（zh 段 <200 CJK、en 段 <120 词）+ 至少一个图示块。覆盖该课主题的"是什么 / 为什么这么设计 / 怎么运作"。
4. **宏观理解卡** `<div class="card macro"><div class="tag">🌍 宏观理解 / Big picture</div>…</div>`：提炼该课的核心心智模型。
5. **细节/源码卡** `<div class="card detail"><div class="tag">🔬 细节 / 源码对应 / Source</div>…<pre class="code">…</pre></div>`：放**简化自 opencode 源码**的 TS/Effect 片段，并在卡内标注来源路径（如 `packages/core/src/session/runner/llm.ts`）。
6. **本课要点卡**：`<div class="card key"><div class="tag">✅ 本课要点</div>…</div>`（en 用 `Key points`）。check_html 要求出现 `本课要点` 或 `Key points`。
7. 自测题由 `quizzes.py` 的 `render()` 自动追加，**不写在 `partK.py` 里**。

**图示块**（每课双语合计 ≥6，即每语 ≥3）从下列 `check_html.DIAGRAM_CLASSES` 中取：`layers` / `vflow` / `flow` / `cols` / `cellgroup` / `timeline` / `trace`，或 `<table class="t">`。优先按主题选型（见 C.3）。

### C.2 每课质量门 (Definition of Done per lesson)

**必过（check_html ERROR，否则构建失败）：**
- 标签平衡（div/details/table/pre/summary）、details 数 == summary 数。
- 恰好 1 个 `<h1>`（由外壳提供）、有 `<title>`、有 `name="description"`。
- 同时含 `class="lang-zh"` 与 `class="lang-en"`（外壳保证；正文亦用双语块）。
- `<pre>` 内无未转义的 `<`：代码里的 `<` 写 `&lt;`、`&` 写 `&amp;`（或包进 `<code>`/inline span）。
- "第 N 课"交叉引用 N ∈ [1, 64]（`MAX_LESSON=64`，允许前向引用）。
- `registry.CONTENT[fname]` 的 zh/en 各 ≥80 字符。

**必清（check_html WARN，里程碑收尾时该 Part 须为 0）：**
- 出现 `本课要点` / `Key points`（要点卡）。
- 出现 `card analogy`（类比卡）。
- 图示块 ≥6（每语 ≥3）。
- zh CJK ≥3000（软下限；**目标 4000+**）。

**人/subagent 复核（不被 check_html 自动捕获，必须审）：**
- **中英 parity**：en 与 zh 的小节、卡片、图示**一一对应**，信息量相当（不是一个详尽一个潦草）。
- **无文字墙**：zh 单段 <200 CJK、en 单段 <120 词；长内容拆段或转图示。
- **每张卡片有真亮点**：拒绝泛泛而谈（泛泛而谈/废话）；每块给出一个具体的、来自源码的洞见。
- **代码引用真实且标注来源**：片段为"简化自 opencode 源码"，标注 `packages/.../file.ts`；不杜撰 API 名。
- **worked-example / 追踪图**：核心课（⭐）应有一张"一次调用逐跳"的 `trace`/`timeline`/`flow` 图。

### C.3 CSS 图示组件速查 (Diagram toolbox)

复用 `shell.py` 内嵌 CSS 的现成组件（无需新增 CSS）：

| 组件 | class | 适合表达 |
| --- | --- | --- |
| 分层塔 | `layers` + `layer`/`lh`/`ld`/`badge`/`name`/`l-app`/`l-part`/`l-main`/`l-core` | 自底向上的架构层（如 server→core→llm→provider） |
| 流程 | `flow` + `node`/`arrow`/`nt`/`nd`/`hl` | 数据流、管线（如一次 prompt 的逐跳） |
| 双栏对比 | `cols` + `col`（内含 `h4`/`ul`） | A vs B（V1 vs V2、训练 vs 推理式对比） |
| 时间线 | `timeline` + `step` | 有序阶段（如 Context Epoch 生命周期） |
| 追踪 | `trace` | worked-example 逐步追踪（带状态变化） |
| 竖向流 | `vflow` | 纵向步骤/状态机 |
| 单元格组 | `cellgroup` + `cells`/`cell`/`cg-cap`/`scale`/`lab` | 数据结构布局（如 message/part、SQL 行） |
| 表格 | `<table class="t">` | 结构化对照（provider/协议/字段表） |
| 泳道 | `lane` + `lane-label` | 并发/角色泳道（如 client/server/provider） |
| 车站 | `stations` + `stn` | 里程碑式路径 |
| 代码文件框 | `codefile` + `cf-head`/`path`/`ln` | 带文件名与行号的源码摘录 |
| 卡片 | `card` + `analogy`/`macro`/`detail`/`key`/`warn` | 类比/宏观/源码/要点/警告 |
| 代码高亮 | `code`(pre) + `cm`(注释)/`fn`(函数)/`kw`(关键字)/`st`(字符串)/`mono`/`inline` | TS/Effect 片段 |

> 内联双语用 `shell.bi(zh, en)`；HTML 转义用 `shell.esc()`。`<pre>` 内代码的 `<`/`&` 必须转义。

### C.4 每课制作工作流 (Per-lesson workflow)

对内容里程碑里的**每一课**，执行：

- [ ] 1. **查源码**：按 spec 中该课的"锚点"，用 `grep`/`view` 实际打开 opencode 源文件，摘取并**简化**关键片段；记录真实路径与符号名。
- [ ] 2. **写 zh**：按 C.1 结构、C.2 质量门撰写中文富 HTML，填入 `partK.py` 的 `LESSON_NN["zh"]`（替换占位）。
- [ ] 3. **写 en**：撰写与 zh **一一对应**的英文（同样的小节/卡片/图示），填入 `LESSON_NN["en"]`。
- [ ] 4. **写自测题**：在 `quizzes.py` 的 `QUIZZES` 中加 `fname` 项（≥2 道 `mcq` 设计洞见题 + ≥1 道 `open`），中英齐全。
- [ ] 5. **build**：`cd src && python3 build.py`。
- [ ] 6. **check**：`python3 check_html.py` + `python3 check_links.py`；该课 0 ERROR，目标该课 0 WARN。
- [ ] 7. **修正**：未达标则回到 2–4 修正（字数/图示/parity/转义）。
- [ ] 8. **commit**：`git add -A && git commit -m "feat(MX): lesson NN <slug>"`。

### C.5 里程碑收尾与 subagent 两阶段审计 (Milestone audit)

每个内容里程碑完成全部课后，统一收尾：

- [ ] 1. `build.py` 重跑无 diff；`check_html.py` 该 Part **0 ERROR、0 WARN**；`check_links.py` 全绿。
- [ ] 2. **同步 L1–L4 文档**（见 C.6）。
- [ ] 3. **阶段 ① — spec 合规审计 subagent**：派一个 `code-review`/`general-purpose` subagent（**用当前主会话模型，不降级**），核对：该 Part 每课是否覆盖 spec 锚点主题、双语 parity、结构完整（六大块齐全）、代码引用真实且路径正确、交叉引用不越界。
- [ ] 4. **阶段 ② — 内容质量审计 subagent**：再派一个 subagent（同模型），核对：每卡有真亮点（无泛泛而谈）、无文字墙（zh 段 <200 CJK / en 段 <120 词）、图示表达力、CJK ≥4000 目标、parity 深度、亮点是否来自真实源码。
- [ ] 5. **修正**：按两份审计报告修正，回到 1 复验，直至两阶段均通过。
- [ ] 6. **commit**：`git commit -m "feat(MX): complete Part K (LNN–LMM)"`。

> 审计 subagent 是**独立**的（不复用写作上下文），以发现作者盲区。两个 subagent 都必须用当前主会话模型显式指定（`model` 参数）。

### C.6 L1–L4 文档同步 (Layered docs)

每个里程碑更新 `docs/`（与课程同 commit）：

- **L1** `docs/L1-overview.md`：全书 + opencode 整体架构一页概览（M0 建框架，里程碑微调）。
- **L2** `docs/L2-parts/part-K.md`：该 Part 的职责、覆盖范围、与相邻 Part 的关系。
- **L3** `docs/L3-details/part-K.md`：该 Part 内每课的细节要点（一课一小节）。
- **L4** `docs/L4-api/part-K.md`：该 Part 引用的 opencode 源文件 → 讲到它的课 的对照表。

---

---

## M0 — 脚手架 (Scaffold)

> M0 是真正的"代码"工作，bite-sized 且含完整改动。完成后站点能 `build` 出 64 课骨架并通过校验。

### Task 0.1：fork 参考项目的生成器基础设施

**Files:** Create `src/{shell.py,build.py,build_print.py,check_html.py,check_links.py}`（从参考项目复制后改），`src/{registry.py,quizzes.py,part1.py..part12.py}`（重建，不复制 llama 内容）。

- [ ] **Step 1：复制基础设施文件**

```bash
SRC=/home/verden/course/llama-cpp-visual-guide/src
DST=/home/verden/course/opencode-visual-guide/src
mkdir -p "$DST"
cp "$SRC"/shell.py "$SRC"/build.py "$SRC"/build_print.py "$SRC"/check_html.py "$SRC"/check_links.py "$DST"/
```

`build.py` 无需改动（它遍历 `shell.PAGES` + `registry.CONTENT` + `quizzes.render`，与项目无关）。`registry.py`、`quizzes.py`、`part*.py` 在后续 Task 重建。

### Task 0.2：改 `shell.py` 品牌与文案

**Files:** Modify `src/shell.py`。

- [ ] **Step 1：替换品牌标识**（🦙→🤖，llama.cpp→opencode）

把 `page()` 与 `index_page()` 中的品牌串改为 opencode：
- `🦙 ... llama.cpp 图解教程 / llama.cpp Visual Guide` → `🤖 ... opencode 图解指南 / opencode Visual Guide`
- `title_tag`/`desc` 里的 `llama.cpp 图解教程` → `opencode 图解指南`，`llama.cpp Visual Guide` 同理。
- `index_page()` hero 的 `<h1>`：`用图解理解整个 llama.cpp 项目` → `用图解理解整个 opencode 项目`；en 同理 `Understand the whole opencode project, visually`。
- hero `lead` 段重写为 opencode 的学习路线（见下）。
- 顶部"对照真实源码核实"注脚里的 `llama.cpp 仓库` → `opencode 仓库`。

- [ ] **Step 2：重写 index hero 的 lead 段**

```python
    <p class="lead"><span class="lang-zh">这套指南带你<strong>自底向上</strong>读懂 opencode 的源码：先打 <strong>Effect 函数式地基</strong>，
    再看<strong>客户端/服务器骨架</strong>，然后深入 <strong>V2 Session Core</strong>（agent 循环、Context Epoch）、
    <strong>自研 LLM 协议层</strong>与<strong>工具系统</strong>，最后覆盖存储、TUI、扩展与实战。每课配真实源码对应、图解与设计亮点。</span>
    <span class="lang-en">A bottom-up tour of the opencode source: start with the <strong>Effect foundations</strong>,
    then the <strong>client/server skeleton</strong>, dive into the <strong>V2 Session Core</strong> (agent loop, Context Epoch),
    the <strong>in-house LLM protocol layer</strong> and <strong>tool system</strong>, then storage, the TUI, extensibility and practice.
    Every lesson maps to real source, with diagrams and design insights.</span></p>
```

- [ ] **Step 3：`lcvgToggleLang` 等内部标识符可保留**（功能性命名，不影响品牌）。

### Task 0.3：用 64 课 `PAGES` 替换 `shell.py` 的 `PAGES`

**Files:** Modify `src/shell.py`（`PAGES = [...]` 整块替换）。

- [ ] **Step 1：写入 Part 1–6 的 PAGES 条目（L01–L35）**

```python
PAGES = [
    ("01-what-is-opencode.html", "opencode 是什么", "What is opencode",
     "第一部分 · 宏观全景", "Part 1 · The Big Picture"),
    ("02-project-map.html", "项目全景地图", "The monorepo map",
     "第一部分 · 宏观全景", "Part 1 · The Big Picture"),
    ("03-request-lifecycle.html", "一次对话的生命周期", "Lifecycle of one prompt",
     "第一部分 · 宏观全景", "Part 1 · The Big Picture"),
    ("04-v1-vs-v2.html", "V1 与 V2：架构迁移", "V1 vs V2: the migration",
     "第一部分 · 宏观全景", "Part 1 · The Big Picture"),
    ("05-why-effect.html", "为什么是 Effect", "Why Effect",
     "第二部分 · Effect 地基", "Part 2 · Effect Foundations"),
    ("06-context-layer.html", "Context.Service 与 Layer", "Services & Layers",
     "第二部分 · Effect 地基", "Part 2 · Effect Foundations"),
    ("07-concurrency-primitives.html", "并发原语", "Concurrency primitives",
     "第二部分 · Effect 地基", "Part 2 · Effect Foundations"),
    ("08-effect-toolbox.html", "项目里的 Effect 工具箱", "The Effect toolbox",
     "第二部分 · Effect 地基", "Part 2 · Effect Foundations"),
    ("09-server-overview.html", "server 总览", "The server, overview",
     "第三部分 · 客户端/服务器", "Part 3 · Client/Server"),
    ("10-route-groups.html", "路由组与 handler", "Route groups & handlers",
     "第三部分 · 客户端/服务器", "Part 3 · Client/Server"),
    ("11-event-bus.html", "SSE 事件总线", "The SSE event bus",
     "第三部分 · 客户端/服务器", "Part 3 · Client/Server"),
    ("12-sdk-generation.html", "SDK 生成", "Generating the SDK",
     "第三部分 · 客户端/服务器", "Part 3 · Client/Server"),
    ("13-transports.html", "多客户端传输", "Multi-client transports",
     "第三部分 · 客户端/服务器", "Part 3 · Client/Server"),
    ("14-session-messages-parts.html", "Session、消息与 part", "Sessions, messages, parts",
     "第四部分 · Session 与 agent 循环", "Part 4 · Session Core"),
    ("15-input-inbox.html", "事件溯源输入收件箱", "The event-sourced inbox",
     "第四部分 · Session 与 agent 循环", "Part 4 · Session Core"),
    ("16-run-coordinator.html", "运行协调器", "The run coordinator",
     "第四部分 · Session 与 agent 循环", "Part 4 · Session Core"),
    ("17-agent-loop.html", "V2 agent 循环", "The V2 agent loop",
     "第四部分 · Session 与 agent 循环", "Part 4 · Session Core"),
    ("18-tool-calls-fiberset.html", "工具调用与 FiberSet", "Tool calls & FiberSet",
     "第四部分 · Session 与 agent 循环", "Part 4 · Session Core"),
    ("19-projected-history.html", "投影历史", "Projected history",
     "第四部分 · Session 与 agent 循环", "Part 4 · Session Core"),
    ("20-steps-errors.html", "有界步数与错误处理", "Bounded steps & errors",
     "第四部分 · Session 与 agent 循环", "Part 4 · Session Core"),
    ("21-system-context.html", "System Context 总览", "System Context overview",
     "第五部分 · Context Epoch 系统", "Part 5 · Context System"),
    ("22-context-source.html", "Context Source", "Context Sources",
     "第五部分 · Context Epoch 系统", "Part 5 · Context System"),
    ("23-context-registry.html", "System Context Registry", "The context registry",
     "第五部分 · Context Epoch 系统", "Part 5 · Context System"),
    ("24-context-epoch.html", "Context Epoch", "The Context Epoch",
     "第五部分 · Context Epoch 系统", "Part 5 · Context System"),
    ("25-mid-conversation.html", "会话中系统消息", "Mid-conversation messages",
     "第五部分 · Context Epoch 系统", "Part 5 · Context System"),
    ("26-builtin-sources.html", "内置 Context Sources", "Built-in sources",
     "第五部分 · Context Epoch 系统", "Part 5 · Context System"),
    ("27-agent-switch-epoch.html", "Agent 切换与 Epoch 替换", "Agent switch & epoch",
     "第五部分 · Context Epoch 系统", "Part 5 · Context System"),
    ("28-llm-overview.html", "LLM 层总览", "The LLM layer",
     "第六部分 · LLM 协议层", "Part 6 · LLM Layer"),
    ("29-protocol-adapters.html", "协议适配器", "Protocol adapters",
     "第六部分 · LLM 协议层", "Part 6 · LLM Layer"),
    ("30-anthropic-protocol.html", "Anthropic Messages 协议", "The Anthropic protocol",
     "第六部分 · LLM 协议层", "Part 6 · LLM Layer"),
    ("31-openai-protocol.html", "OpenAI Chat/Responses 协议", "The OpenAI protocols",
     "第六部分 · LLM 协议层", "Part 6 · LLM Layer"),
    ("32-gemini-bedrock.html", "Gemini 与 Bedrock 协议", "Gemini & Bedrock",
     "第六部分 · LLM 协议层", "Part 6 · LLM Layer"),
    ("33-routing-transport.html", "路由与传输", "Routing & transport",
     "第六部分 · LLM 协议层", "Part 6 · LLM Layer"),
    ("34-streaming-cache.html", "流式事件与缓存", "Streaming & caching",
     "第六部分 · LLM 协议层", "Part 6 · LLM Layer"),
    ("35-model-resolution.html", "模型解析与 Copilot provider", "Model resolution & Copilot",
     "第六部分 · LLM 协议层", "Part 6 · LLM Layer"),
    # —— Part 7–12 在下一步追加 ——
]
```

- [ ] **Step 2：在 `PAGES` 末尾（占位注释处）追加 Part 7–12 条目（L36–L64）**

```python
    ("36-tool-definition.html", "工具定义", "Defining a tool",
     "第七部分 · 工具系统", "Part 7 · Tool System"),
    ("37-tool-registry.html", "工具注册表", "The tool registry",
     "第七部分 · 工具系统", "Part 7 · Tool System"),
    ("38-file-tools.html", "文件工具", "File tools",
     "第七部分 · 工具系统", "Part 7 · Tool System"),
    ("39-search-exec-tools.html", "搜索与执行工具", "Search & exec tools",
     "第七部分 · 工具系统", "Part 7 · Tool System"),
    ("40-other-tools.html", "其他内置工具", "Other built-in tools",
     "第七部分 · 工具系统", "Part 7 · Tool System"),
    ("41-permissions.html", "权限系统", "Permissions",
     "第七部分 · 工具系统", "Part 7 · Tool System"),
    ("42-bounded-output.html", "有界工具输出", "Bounded tool output",
     "第七部分 · 工具系统", "Part 7 · Tool System"),
    ("43-skills.html", "Skills 系统", "The skills system",
     "第七部分 · 工具系统", "Part 7 · Tool System"),
    ("44-config-loading.html", "配置加载", "Loading config",
     "第八部分 · 配置·Agents·Provider", "Part 8 · Config, Agents, Providers"),
    ("45-agents.html", "Agents：build 与 plan", "Agents: build & plan",
     "第八部分 · 配置·Agents·Provider", "Part 8 · Config, Agents, Providers"),
    ("46-mcp.html", "MCP 集成", "MCP integration",
     "第八部分 · 配置·Agents·Provider", "Part 8 · Config, Agents, Providers"),
    ("47-provider-plugins.html", "Provider 插件定义", "Provider plugins",
     "第八部分 · 配置·Agents·Provider", "Part 8 · Config, Agents, Providers"),
    ("48-drizzle-sqlite.html", "Drizzle 与 SQLite", "Drizzle & SQLite",
     "第九部分 · 持久化", "Part 9 · Persistence"),
    ("49-core-tables.html", "核心数据表", "The core tables",
     "第九部分 · 持久化", "Part 9 · Persistence"),
    ("50-v1-storage-migration.html", "V1 存储与迁移", "V1 storage & migration",
     "第九部分 · 持久化", "Part 9 · Persistence"),
    ("51-compaction-snapshots.html", "压缩、摘要与快照", "Compaction & snapshots",
     "第九部分 · 持久化", "Part 9 · Persistence"),
    ("52-opentui.html", "opentui 渲染器", "The opentui renderer",
     "第十部分 · TUI", "Part 10 · The TUI"),
    ("53-tui-structure.html", "TUI 应用结构", "TUI app structure",
     "第十部分 · TUI", "Part 10 · The TUI"),
    ("54-events-to-store.html", "事件到 store", "Events to store",
     "第十部分 · TUI", "Part 10 · The TUI"),
    ("55-prompt-component.html", "prompt 组件", "The prompt component",
     "第十部分 · TUI", "Part 10 · The TUI"),
    ("56-dialogs-scrollback.html", "对话框与 scrollback", "Dialogs & scrollback",
     "第十部分 · TUI", "Part 10 · The TUI"),
    ("57-plugin-system.html", "插件系统", "The plugin system",
     "第十一部分 · 扩展与集成", "Part 11 · Extensibility"),
    ("58-plugin-hooks.html", "插件 hooks 详解", "Plugin hooks in depth",
     "第十一部分 · 扩展与集成", "Part 11 · Extensibility"),
    ("59-lsp.html", "LSP 集成", "LSP integration",
     "第十一部分 · 扩展与集成", "Part 11 · Extensibility"),
    ("60-pty-shell.html", "PTY 与 shell", "PTY & shell",
     "第十一部分 · 扩展与集成", "Part 11 · Extensibility"),
    ("61-acp-location.html", "ACP 与 Location 抽象", "ACP & the Location model",
     "第十一部分 · 扩展与集成", "Part 11 · Extensibility"),
    ("62-build-debug.html", "本地构建与调试", "Build & debug",
     "第十二部分 · 实战与速查", "Part 12 · Practice & Reference"),
    ("63-test-contribute.html", "测试与贡献", "Test & contribute",
     "第十二部分 · 实战与速查", "Part 12 · Practice & Reference"),
    ("64-glossary.html", "术语表与索引", "Glossary & index",
     "第十二部分 · 实战与速查", "Part 12 · Practice & Reference"),
]
```

- [ ] **Step 3：更新 `SUBTITLES`**（`index_page` 用的目录副标题字典）：清空为 `SUBTITLES = {}`（可选副标题；占位阶段留空，内容里程碑可逐课补一句话副标题）。

### Task 0.4：适配 `check_html.py`

**Files:** Modify `src/check_html.py`。

- [ ] **Step 1：改最终课数与豁免页**

```python
MAX_LESSON = 64  # planned final lesson count; cross-refs may point forward
```

```python
SOFT_EXEMPT = {"64-glossary.html"}
```

其余阈值保持：`MIN_CONTENT = 80`、`MIN_DIAGRAMS = 6`、`MIN_CJK = 3000`、`DIAGRAM_CLASSES` 不变。注释里 "第 N 课" 交叉引用范围现为 1..64。

### Task 0.5：适配 `check_links.py`

**Files:** Modify `src/check_links.py`。

- [ ] **Step 1：改 `ALLOW_MISSING` 的 PDF 名**（部署时才生成；源码 checkout 中不存在）

```python
ALLOW_MISSING = {
    "opencode-visual-guide-zh.pdf",
    "opencode-visual-guide-en.pdf",
}
```

### Task 0.6：占位内容、注册表与自测题骨架

**Files:** Create `src/placeholder.py`, `src/part1.py`..`src/part12.py`, `src/registry.py`, `src/quizzes.py`。

- [ ] **Step 1：创建 `src/placeholder.py`**（共享"建设中"占位；内容里程碑逐课替换）

```python
"""Shared 'work in progress' placeholder for lessons not yet written.

Each content milestone (M1-M12) replaces its part's `LESSON_NN = wip(...)`
entries with real bilingual content dicts. The placeholder is intentionally
>80 chars per language (so check_html ERROR passes) but lacks analogy/key-points
cards and diagrams (so it WARNs - a built-in "unfinished" dashboard).
"""


def wip(zh_title, en_title):
    return {
        "zh": (
            f'<p class="lead">本课《{zh_title}》正在建设中，敬请期待。</p>'
            f'<div class="card macro"><div class="tag">🚧 建设中</div>'
            f'这一课会逐步拆解 opencode 中“{zh_title}”这一主题，配上图解、'
            f'简化自源码的真实代码引用与自测题。</div>'
        ),
        "en": (
            f'<p class="lead">This lesson "{en_title}" is under construction.</p>'
            f'<div class="card macro"><div class="tag">🚧 WIP</div>'
            f'It will break down the "{en_title}" topic in opencode, with diagrams, '
            f'simplified real source references and a self-test.</div>'
        ),
    }
```

- [ ] **Step 2：创建 `src/part1.py`**（模板；其余 part 同构）

```python
"""Part 1 (macro overview) content. Placeholders until M1 fills them in."""
from placeholder import wip

LESSON_01 = wip("opencode 是什么", "What is opencode")
LESSON_02 = wip("项目全景地图", "The monorepo map")
LESSON_03 = wip("一次对话的生命周期", "Lifecycle of one prompt")
LESSON_04 = wip("V1 与 V2：架构迁移", "V1 vs V2: the migration")
```

- [ ] **Step 3：创建 `src/part2.py`..`src/part12.py`**

每个文件 `from placeholder import wip`，按下表声明 `LESSON_NN = wip(zh, en)`（zh/en 取自 Task 0.3 的 PAGES 标题，编号连续）：

- `part2.py`：LESSON_05..08（Effect 地基）
- `part3.py`：LESSON_09..13（客户端/服务器）
- `part4.py`：LESSON_14..20（Session/agent 循环）
- `part5.py`：LESSON_21..27（Context Epoch）
- `part6.py`：LESSON_28..35（LLM 协议层）
- `part7.py`：LESSON_36..43（工具系统）
- `part8.py`：LESSON_44..47（配置/Agents/Provider）
- `part9.py`：LESSON_48..51（持久化）
- `part10.py`：LESSON_52..56（TUI）
- `part11.py`：LESSON_57..61（扩展集成）
- `part12.py`：LESSON_62..64（实战/速查）

- [ ] **Step 4：创建 `src/registry.py`**（filename → 内容；与 PAGES 一一对应）

```python
"""Single source of truth: ordered map of output filename -> bilingual content.

Each value is {"zh": html, "en": html}. build.py / build_print.py import this so
the lesson set stays in sync with shell.PAGES. Keys MUST match shell.PAGES.
"""
import part1, part2, part3, part4, part5, part6
import part7, part8, part9, part10, part11, part12

CONTENT = {
    "01-what-is-opencode.html": part1.LESSON_01,
    "02-project-map.html": part1.LESSON_02,
    "03-request-lifecycle.html": part1.LESSON_03,
    "04-v1-vs-v2.html": part1.LESSON_04,
    "05-why-effect.html": part2.LESSON_05,
    "06-context-layer.html": part2.LESSON_06,
    "07-concurrency-primitives.html": part2.LESSON_07,
    "08-effect-toolbox.html": part2.LESSON_08,
    "09-server-overview.html": part3.LESSON_09,
    "10-route-groups.html": part3.LESSON_10,
    "11-event-bus.html": part3.LESSON_11,
    "12-sdk-generation.html": part3.LESSON_12,
    "13-transports.html": part3.LESSON_13,
    "14-session-messages-parts.html": part4.LESSON_14,
    "15-input-inbox.html": part4.LESSON_15,
    "16-run-coordinator.html": part4.LESSON_16,
    "17-agent-loop.html": part4.LESSON_17,
    "18-tool-calls-fiberset.html": part4.LESSON_18,
    "19-projected-history.html": part4.LESSON_19,
    "20-steps-errors.html": part4.LESSON_20,
    "21-system-context.html": part5.LESSON_21,
    "22-context-source.html": part5.LESSON_22,
    "23-context-registry.html": part5.LESSON_23,
    "24-context-epoch.html": part5.LESSON_24,
    "25-mid-conversation.html": part5.LESSON_25,
    "26-builtin-sources.html": part5.LESSON_26,
    "27-agent-switch-epoch.html": part5.LESSON_27,
    "28-llm-overview.html": part6.LESSON_28,
    "29-protocol-adapters.html": part6.LESSON_29,
    "30-anthropic-protocol.html": part6.LESSON_30,
    "31-openai-protocol.html": part6.LESSON_31,
    "32-gemini-bedrock.html": part6.LESSON_32,
    "33-routing-transport.html": part6.LESSON_33,
    "34-streaming-cache.html": part6.LESSON_34,
    "35-model-resolution.html": part6.LESSON_35,
    "36-tool-definition.html": part7.LESSON_36,
    "37-tool-registry.html": part7.LESSON_37,
    "38-file-tools.html": part7.LESSON_38,
    "39-search-exec-tools.html": part7.LESSON_39,
    "40-other-tools.html": part7.LESSON_40,
    "41-permissions.html": part7.LESSON_41,
    "42-bounded-output.html": part7.LESSON_42,
    "43-skills.html": part7.LESSON_43,
    "44-config-loading.html": part8.LESSON_44,
    "45-agents.html": part8.LESSON_45,
    "46-mcp.html": part8.LESSON_46,
    "47-provider-plugins.html": part8.LESSON_47,
    "48-drizzle-sqlite.html": part9.LESSON_48,
    "49-core-tables.html": part9.LESSON_49,
    "50-v1-storage-migration.html": part9.LESSON_50,
    "51-compaction-snapshots.html": part9.LESSON_51,
    "52-opentui.html": part10.LESSON_52,
    "53-tui-structure.html": part10.LESSON_53,
    "54-events-to-store.html": part10.LESSON_54,
    "55-prompt-component.html": part10.LESSON_55,
    "56-dialogs-scrollback.html": part10.LESSON_56,
    "57-plugin-system.html": part11.LESSON_57,
    "58-plugin-hooks.html": part11.LESSON_58,
    "59-lsp.html": part11.LESSON_59,
    "60-pty-shell.html": part11.LESSON_60,
    "61-acp-location.html": part11.LESSON_61,
    "62-build-debug.html": part12.LESSON_62,
    "63-test-contribute.html": part12.LESSON_63,
    "64-glossary.html": part12.LESSON_64,
}
```

- [ ] **Step 5：重建 `src/quizzes.py`**

从参考项目复制 `quizzes.py` 的机制（模块 docstring、常量 `_HEAD/_SEE/_CLICK/_ANS/_SEP/_OPEN`、`_shuffle()`、`render()` 及其底部的校验逻辑），但把题库清空：

```python
QUIZZES = {}
```

`render(fname, lang)` 已对 `QUIZZES.get(fname)` 为空返回 `""`，故占位课无自测题也能 build。内容里程碑逐课向 `QUIZZES` 添加 `fname` 项。

```bash
cp /home/verden/course/llama-cpp-visual-guide/src/quizzes.py /home/verden/course/opencode-visual-guide/src/quizzes.py
# 然后把文件末尾的 QUIZZES = {大字典} 整体替换为 QUIZZES = {}
# （保留 _shuffle / render / 常量 / 末尾的逐项校验循环）
```

> 注意：参考项目 `quizzes.py` 末尾可能有遍历 `QUIZZES` 做断言的校验代码——清空字典后它自然空转，无需删。

### Task 0.7：项目文件（README / LICENSE / 部署 / 文档骨架）

**Files:** Create `README.md`, `LICENSE`, `LICENSE-CONTENT`, `.gitignore`, `.github/workflows/deploy.yml`, `docs/L1-overview.md`, `docs/L2-parts/`, `docs/L3-details/`, `docs/L4-api/`。

- [ ] **Step 1：创建 `README.md`**（双语，结构参照参考项目 README 改写）

结构与参考项目一致，替换品牌与内容：
- 标题：`# opencode 图解学习指南 / opencode Visual Guide`
- 一句话简介：对 opencode（开源 AI 编程 agent）**源码内部**的中英双语图解指南，**64 课**，自底向上从"opencode 是什么"讲到"测试与贡献"。
- **Disclaimer（必须，中英各一段，逐字）：**
  > **Disclaimer:** This is **third-party, unofficial** educational material *about* opencode. It contains **no opencode source code**; it explains opencode by quoting small, cited snippets. opencode itself is licensed by its own authors.
  >
  > **声明：** 本项目是**第三方、非官方**的学习材料，**不包含 opencode 源码**，只通过引用少量、标注来源的代码片段来讲解。opencode 本身由其作者按其许可发布。
- "What it covers" 表：12 部分（Part 1–12）对应课号（见 spec/PAGES）。
- "How to view"：`cd src && python3 build.py`，再开 `../index.html`。
- "How to print"：`python3 build_print.py` → `print_zh.html`/`print_en.html` → Ctrl/Cmd+P。
- "Project structure"：列 `src/`、`lessons/`、`index.html`、`print_*.html`、`docs/`。
- "Build & validate"：四条命令（build / build_print / check_html / check_links）。
- "Deploy note"：GitHub Pages 需所有者先在 Settings→Pages→Source 选 "GitHub Actions" 启用一次。
- "License"：双许可说明（指向 LICENSE / LICENSE-CONTENT）。

- [ ] **Step 2：创建 `LICENSE` 与 `LICENSE-CONTENT`**

```bash
cp /home/verden/course/llama-cpp-visual-guide/LICENSE         /home/verden/course/opencode-visual-guide/LICENSE
cp /home/verden/course/llama-cpp-visual-guide/LICENSE-CONTENT /home/verden/course/opencode-visual-guide/LICENSE-CONTENT
```

检查 `LICENSE`（MIT）版权行年份/作者，按需更新；`LICENSE-CONTENT`（CC BY 4.0）保持。

- [ ] **Step 3：创建 `.gitignore`**

```
__pycache__/
*.pyc
.DS_Store
*.pdf
```

- [ ] **Step 4：创建 `.github/workflows/deploy.yml` 与 `ci.yml`**

```bash
mkdir -p /home/verden/course/opencode-visual-guide/.github/workflows
cp /home/verden/course/llama-cpp-visual-guide/.github/workflows/deploy.yml /home/verden/course/opencode-visual-guide/.github/workflows/
cp /home/verden/course/llama-cpp-visual-guide/.github/workflows/ci.yml     /home/verden/course/opencode-visual-guide/.github/workflows/
```

改两处：
- 两个文件里 `branches: [master]` → `branches: [main]`（本仓库默认分支为 `main`）。
- `ci.yml` 的 `print-pdf` job 里 PDF 输出名改为与 `check_links.ALLOW_MISSING` 一致：
  `--print-to-pdf=opencode-visual-guide-zh.pdf print_zh.html`、`...-en.pdf print_en.html`，`upload-artifact` 的 `path: '*.pdf'` 不变。

> `ci.yml` 的 `build-and-validate` job 会 `git diff --cached --exit-code` 确保**生成的 HTML 已入库且与源同步**——这是关键守护，每次提交前本地也要先 `build.py` 再提交。

- [ ] **Step 5：创建 `docs/` 分层骨架**

```bash
cd /home/verden/course/opencode-visual-guide
mkdir -p docs/L2-parts docs/L3-details docs/L4-api
```

- `docs/L1-overview.md`：写全书一页概览——opencode 是什么、客户端/服务器+V1/V2 的整体架构图（文字版）、12 部分索引与依赖顺序。M0 建立框架，后续里程碑微调。
- `docs/L2-parts/README.md`、`docs/L3-details/README.md`、`docs/L4-api/README.md`：各写一句话说明该层用途（L2=每部分职责、L3=每课细节、L4=源文件→课对照），后续里程碑按 `part-K.md` 填充。

### Task 0.8：构建、校验与提交

**Files:** 生成 `lessons/*.html`、`index.html`、`print_*.html`。

- [ ] **Step 1：构建**

```bash
cd /home/verden/course/opencode-visual-guide/src
python3 build.py
python3 build_print.py
```
Expected: `Wrote 65 files`（64 课 + index）；2 个 print 文件。

- [ ] **Step 2：结构校验**

```bash
python3 check_html.py
```
Expected: **0 error(s)**，若干 warning（占位课缺类比卡/要点卡/图示/CJK——这是预期的"未完成"看板）；末行 `structural check passed`。

- [ ] **Step 3：链接校验**

```bash
python3 check_links.py
```
Expected: `all N internal links resolve`（0 broken）。

- [ ] **Step 4：提交**

```bash
cd /home/verden/course/opencode-visual-guide
git add -A
git commit -m "chore(M0): scaffold generator + 64-lesson skeleton

Fork the zero-dependency Python generator from llama-cpp-visual-guide;
brand for opencode; declare all 64 lessons across 12 parts in shell.PAGES;
placeholder content + empty quiz bank so build.py + check_html.py +
check_links.py are green (placeholder lessons WARN as an 'unfinished'
dashboard). Add README (with disclaimer), dual LICENSE, CI + Pages deploy,
and the docs/ L1-L4 skeleton.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 0.9：M0 脚手架审计（subagent 两阶段）

- [ ] **Step 1：阶段 ① 结构/对齐审计 subagent**（当前模型，不降级）核对：`shell.PAGES` 恰 64 项、12 部分、fname 唯一；`registry.CONTENT` 键与 PAGES **完全对齐**（无孤儿、无缺失）；`check_html.MAX_LESSON==64`、`SOFT_EXEMPT=={"64-glossary.html"}`；`build.py` 产出 64 lessons + index；`check_html` 0 ERROR；`check_links` 0 broken；品牌串无遗留 `llama`/🦙。
- [ ] **Step 2：阶段 ② 站点质量审计 subagent**（当前模型）核对：随机抽查 3 个生成的 `lessons/*.html`——语言切换按钮、prev/next 链正确、`index.html` 顶部 `共 64 课 · 12 个部分`、占位机制工作、`deploy.yml`/`ci.yml` 分支为 `main`、README disclaimer 中英齐全、双 LICENSE 存在。
- [ ] **Step 3：修正**任何审计发现的问题，回到 Task 0.8 复验后再进入 M1。

---

---

## M1–M12 — 内容里程碑 (Content Milestones)

> 每个内容里程碑：对每课执行 C.4 工作流，再执行 C.5 里程碑收尾与两阶段审计。下面每课给出**关键图示建议**与**核心锚点**（详细锚点见 spec）。内容为执行产物，不在计划中预写。

### M1 — Part 1 宏观全景（L01–04）

- [ ] **M1.1 — L01 opencode 是什么**：图示建议=client/server 分层(`layers`) + opencode↔Claude Code/Cursor 对比(`table.t`) + 一次对话总览(`flow`)；类比=常驻"大脑"server + 多种"终端"client；锚点=`README.md`、`packages/opencode/src/index.ts`。
- [ ] **M1.2 — L02 项目全景地图**：图示=24 package 的 CORE/周边分组(`cols`/`layers`) + 包依赖(`flow`)；锚点=`packages/*`、`turbo.json`、`package.json`。
- [ ] **M1.3 — L03 一次对话的生命周期**：图示=keypress→render 的 11 跳(`trace`/`flow`)（核心叙事课，务必做扎实）；锚点=`cli/cmd/tui.ts`、`server/server.ts`、`core/src/session/runner/llm.ts`。
- [ ] **M1.4 — L04 V1 与 V2**：图示=V1↔V2 双栏(`cols`) + 迁移时间线(`timeline`)；锚点=`packages/opencode/src/session/` vs `packages/core/`。
- [ ] **M1.R — 收尾+审计**：build/check（Part 1 = 0 ERROR/0 WARN）→ 写 `docs/L2-parts/part-1.md`、`L3-details/part-1.md`、`L4-api/part-1.md`、更新 `L1-overview.md` → C.5 两阶段审计 → commit。

### M2 — Part 2 Effect 函数式地基（L05–08）

- [ ] **M2.1 — L05 为什么是 Effect**：图示=`try/catch` vs Effect 双栏(`cols`) + Effect 类型签名拆解(`cellgroup`)；类比=把"副作用/错误/依赖"写进类型的电路图；锚点=`AGENTS.md`（风格）、`packages/core/src/effect/*`。
- [ ] **M2.2 — L06 Context.Service 与 Layer**：图示=Layer 组合(`layers`/`flow`) + 服务依赖图；锚点=`core/src/*` 中 `Context.Service`/`Layer.effect` 实例。
- [ ] **M2.3 — L07 并发原语**：图示=Fiber/FiberSet/Deferred/Latch 对照(`table.t`) + 并发执行(`trace`)；锚点=`core/src/session/runner/llm.ts`(FiberSet)、`run-coordinator.ts`。
- [ ] **M2.4 — L08 Effect 工具箱**：图示=keyed-mutex/memo-map 机制(`flow`)；锚点=`core/src/keyed-mutex.ts`、`memo-map.ts`、`service-use.ts`。
- [ ] **M2.R — 收尾+审计**：同 M1.R（Part 2 文档 + 两阶段审计 + commit）。

### M3 — Part 3 客户端/服务器（L09–13）

- [ ] **M3.1 — L09 server 总览**：图示=HttpApi 结构(`layers`) + 请求处理流(`flow`)；锚点=`server/server.ts`、`routes/instance/httpapi/api.ts`。
- [ ] **M3.2 — L10 路由组与 handler**：图示=路由组清单(`table.t`) + group→handler→middleware(`flow`)；锚点=`groups/*`、`handlers/*`、`middleware/*`。
- [ ] **M3.3 — L11 SSE 事件总线**：图示=GlobalBus→SSE→client 泳道(`lane`)；锚点=`groups/event.ts`、`GlobalBus`。
- [ ] **M3.4 — L12 SDK 生成**：图示=OpenAPI→生成客户端 pipeline(`flow`)；锚点=`script/generate.ts`、`sdk/js/src/gen/*`、`openapi.json`。
- [ ] **M3.5 — L13 多客户端传输**：图示=网络 server vs RPC worker 双栏(`cols`) + worker fetch 桥接(`flow`)；锚点=`cli/cmd/tui.ts` `createWorkerFetch()`、`cli/tui/worker.ts`。
- [ ] **M3.R — 收尾+审计**：同 M1.R。

### M4 — Part 4 Session 与 Agent 循环 ⭐（L14–20）

- [ ] **M4.1 — L14 Session、消息与 part**：图示=session→messages→parts 树(`cellgroup`) + part 类型(`table.t`)；锚点=`core/src/session/message.ts`、`session/sql.ts`。
- [ ] **M4.2 — L15 事件溯源输入收件箱**：图示=`session_input` 事件流(`trace`/`timeline`)；锚点=`core/src/session/input.ts`、`prompt.ts`。
- [ ] **M4.3 — L16 运行协调器**：图示=run/wake/interrupt 状态机(`vflow`) + 并发泳道(`lane`)；锚点=`core/src/session/run-coordinator.ts`、`execution.ts`。
- [ ] **M4.4 — L17 V2 agent 循环 ⭐⭐**：图示=一次 provider turn 逐跳(`trace`)（**全书最核心，做最扎实，CJK 充分**）；锚点=`core/src/session/runner/llm.ts`（头部 checklist 注释）。
- [ ] **M4.5 — L18 工具调用与 FiberSet**：图示=tool-call→settle 并发(`flow`/`lane`)；锚点=`runner/llm.ts`(~256–280)、`toolMaterialization.settle`。
- [ ] **M4.6 — L19 投影历史**：图示=event→projection(`flow`)；锚点=`core/src/session/projector.ts`、`history.ts`、`session_message` 表。
- [ ] **M4.7 — L20 有界步数与错误处理**：图示=MAX_STEPS 循环(`vflow`) + 错误分支(`flow`)；锚点=`runner/llm.ts`(~383–392)、`runner/index.ts`。
- [ ] **M4.R — 收尾+审计**：同 M1.R（Part 4 文档 + 两阶段审计 + commit）。

### M5 — Part 5 System Context 与 Context Epoch ⭐（L21–27）

- [ ] **M5.1 — L21 System Context 总览**：图示=System Context 组成(`layers`)；类比=会话的不可变"快照纪元"；锚点=`CONTEXT.md`、`core/src/system-context/index.ts`。
- [ ] **M5.2 — L22 Context Source**：图示=codec/loader/renderer 结构(`cellgroup`/`flow`)；锚点=`system-context/index.ts` `SystemContext.make`。
- [ ] **M5.3 — L23 System Context Registry**：图示=作用域生产者组合(`layers`)；锚点=`system-context/registry.ts`、`builtins.ts`。
- [ ] **M5.4 — L24 Context Epoch**：图示=epoch 生命周期(`timeline`/`vflow`) + snapshot 比对(`cellgroup`)；锚点=`core/src/session/context-epoch.ts`、迁移 `add_session_context_snapshot`。
- [ ] **M5.5 — L25 会话中系统消息**：图示=安全边界注入时序(`trace`)；锚点=`CONTEXT.md`（Safe Provider-Turn Boundary）、`context-epoch.ts`。
- [ ] **M5.6 — L26 内置 Context Sources**：图示=各 source 一览(`table.t`)；锚点=`system-context/builtins.ts`、`instruction-context.ts`。
- [ ] **M5.7 — L27 Agent 切换与 Epoch 替换**：图示=切换触发替换(`flow`) + fenced 重试；锚点=`core/src/agent.ts`、`context-epoch.ts`、迁移 `add_context_epoch_agent`。
- [ ] **M5.R — 收尾+审计**：同 M1.R。

### M6 — Part 6 LLM 协议层 ⭐（L28–35）

- [ ] **M6.1 — L28 LLM 层总览**：图示=provider-agnostic client 结构(`layers`)；锚点=`packages/llm/src/llm.ts`、`schema/*`。
- [ ] **M6.2 — L29 协议适配器**：图示=统一请求→各 wire 编码(`flow`)（核心概念："适配器独占 wire 编码"）；锚点=`llm/src/route/client.ts`、`CONTEXT.md`(49,103)。
- [ ] **M6.3 — L30 Anthropic Messages 协议**：图示=请求/流事件编码(`cellgroup`)；锚点=`protocols/anthropic-messages.ts`、`utils/cache.ts`。
- [ ] **M6.4 — L31 OpenAI Chat/Responses 协议**：图示=Chat vs Responses 双栏(`cols`)；锚点=`protocols/openai-chat.ts`、`openai-responses.ts`、`openai-compatible-chat.ts`。
- [ ] **M6.5 — L32 Gemini 与 Bedrock 协议**：图示=两协议对照(`table.t`) + bedrock eventstream(`trace`)；锚点=`protocols/gemini.ts`、`bedrock-converse.ts`、`bedrock-event-stream.ts`。
- [ ] **M6.6 — L33 路由与传输**：图示=HTTP vs WebSocket 双栏(`cols`) + framing(`flow`)；锚点=`llm/src/route/transport/http.ts`、`websocket.ts`、`framing.ts`。
- [ ] **M6.7 — L34 流式事件与缓存**：图示=LLMEvent 流(`trace`) + prompt 缓存前缀(`cellgroup`)（联动 Context Epoch 基线前缀）；锚点=`llm/src/schema/*`(LLMEvent)、`cache-policy.ts`。
- [ ] **M6.8 — L35 模型解析与 Copilot provider**：图示=models.dev 解析(`flow`)；锚点=`core/src/models-dev.ts`、`catalog.ts`、`core/src/github-copilot/*`。
- [ ] **M6.R — 收尾+审计**：同 M1.R。

### M7 — Part 7 工具系统（L36–43）

- [ ] **M7.1 — L36 工具定义**：图示=`Tool.make` 结构(`cellgroup`) + input/output/execute；锚点=`core/src/tool/tool.ts`（make/withPermission/definition/settle）。
- [ ] **M7.2 — L37 工具注册表**：图示=register→materialize(`flow`)；锚点=`core/src/tool/registry.ts`、`builtins.ts`(locationLayer)。
- [ ] **M7.3 — L38 文件工具**：图示=read/write/edit/apply-patch 一览(`table.t`) + 一次 edit 的 worked-example(`trace`)；锚点=`core/src/tool/{read,write,edit,apply-patch}.ts`。
- [ ] **M7.4 — L39 搜索与执行工具**：图示=glob/grep/bash 对照(`table.t`) + bash 经 PTY(`flow`)；锚点=`core/src/tool/{glob,grep,bash}.ts`、`pty/*`。
- [ ] **M7.5 — L40 其他内置工具**：图示=webfetch/websearch/question/todowrite 一览(`table.t`)；锚点=`core/src/tool/{webfetch,websearch,question,todowrite}.ts`。
- [ ] **M7.6 — L41 权限系统**：图示=permission 评估流(`flow`) + per-turn 冻结(`trace`)；锚点=`core/src/permission.ts`、`permission/{saved,schema,sql}.ts`。
- [ ] **M7.7 — L42 有界工具输出**：图示=截断+spill 到 Managed File(`flow`/`cellgroup`)；锚点=`core/src/tool-output-store.ts`、`config/tool-output.ts`、`CONTEXT.md`。
- [ ] **M7.8 — L43 Skills 系统**：图示=names(Context Source) vs body(经权限化 `skill` 工具)双栏(`cols`)；锚点=`core/src/skill/*`、`tool/skill.ts`。
- [ ] **M7.R — 收尾+审计**：同 M1.R。

### M8 — Part 8 配置、Agents 与 Provider（L44–47）

- [ ] **M8.1 — L44 配置加载**：图示=config 来源合并(`flow`/`layers`)（全局/项目/`opencode.json`）；锚点=`core/src/config.ts`、`config/*`、`core/src/v1/config/*`。
- [ ] **M8.2 — L45 Agents：build 与 plan**：图示=build vs plan 双栏(`cols`) + agent prompt 组装(`flow`)；锚点=`core/src/agent.ts`、`config/agent.ts`、`opencode/src/agent/prompt/*.txt`。
- [ ] **M8.3 — L46 MCP 集成**：图示=MCP server→动态工具(`flow`) + OAuth(`trace`)；锚点=`opencode/src/mcp/*`、`config/mcp.ts`、`groups/mcp.ts`。
- [ ] **M8.4 — L47 Provider 插件定义**：图示=~40 provider 注册(`layers`/`table.t`)；锚点=`core/src/plugin/provider/*`、`opencode/src/provider/provider.ts`。
- [ ] **M8.R — 收尾+审计**：同 M1.R。

### M9 — Part 9 持久化与存储（L48–51）

- [ ] **M9.1 — L48 Drizzle 与 SQLite**：图示=Drizzle schema→SQL(`cellgroup`) + migration 链(`timeline`)；锚点=`core/src/database/{database,migration}.ts`、`drizzle.config.ts`、`schema.json`。
- [ ] **M9.2 — L49 核心数据表**：图示=表关系 ER(`cellgroup`/`table.t`)（session/message/part/session_message/session_input/context_epoch）；锚点=`core/src/session/sql.ts`、各 `*/sql.ts`。
- [ ] **M9.3 — L50 V1 存储与迁移**：图示=V1 文件→V2 SQLite 迁移(`flow`)；锚点=`opencode/src/storage/storage.ts`、`core/src/data-migration.sql.ts`。
- [ ] **M9.4 — L51 压缩、摘要与快照**：图示=compaction 流(`flow`) + snapshot/revert 时间线(`timeline`)；锚点=`core/src/session/compaction.ts`、`opencode/src/snapshot/index.ts`、`session/revert.ts`。
- [ ] **M9.R — 收尾+审计**：同 M1.R。

### M10 — Part 10 TUI 与客户端渲染（L52–56）

- [ ] **M10.1 — L52 opentui 渲染器**：图示=opentui = "TTY 版浏览器 DOM"(`flow`/`layers`)；类比=把 JSX 渲染到终端；锚点=`@opentui/core` `createCliRenderer`、`packages/tui/src/app.tsx`。
- [ ] **M10.2 — L53 TUI 应用结构**：图示=context providers 树(`layers`)；锚点=`tui/src/context/{sdk,runtime,project,route,prompt,theme}.tsx`。
- [ ] **M10.3 — L54 事件到 store**：图示=event→reducer→store(`flow`) + 16ms 批渲染(`timeline`)；锚点=`tui/src/context/{sync,data}.tsx`。
- [ ] **M10.4 — L55 prompt 组件**：图示=editor/autocomplete/history/frecency(`table.t`)；锚点=`tui/src/component/prompt/*`。
- [ ] **M10.5 — L56 对话框与 scrollback**：图示=dialog/command-palette + `run` scrollback 双栏(`cols`)；锚点=`tui/src/component/{dialog-*,command-palette}.tsx`、`opencode/src/cli/cmd/run/scrollback.*`。
- [ ] **M10.R — 收尾+审计**：同 M1.R。

### M11 — Part 11 扩展与集成（L57–61）

- [ ] **M11.1 — L57 插件系统**：图示=Plugin→Hooks 加载(`flow`)；锚点=`packages/plugin/src/index.ts`、`opencode/src/plugin/loader.ts`、`core/src/plugin.ts`。
- [ ] **M11.2 — L58 插件 hooks 详解**：图示=各 hook 触发点(`table.t`/`trace`)（auth/provider/chat/tool/permission）；锚点=`plugin/src/index.ts`(Hooks ~222)、`opencode/src/plugin/*`。
- [ ] **M11.3 — L59 LSP 集成**：图示=LSP client→diagnostic(`flow`)；锚点=`opencode/src/lsp/{client,diagnostic,launch,server}.ts`、`tool/lsp.ts`。
- [ ] **M11.4 — L60 PTY 与 shell**：图示=PTY 创建+环境叠加(`flow`/`layers`)；锚点=`core/src/pty/*`、`CONTEXT.md`(PTY Environment)。
- [ ] **M11.5 — L61 ACP 与 Location 抽象**：图示=opencode 作为 ACP server 泳道(`lane`) + Location-scoped + move-session(`flow`)；锚点=`opencode/src/acp/*`、`core/src/location*.ts`、`control-plane/move-session.ts`。
- [ ] **M11.R — 收尾+审计**：同 M1.R。

### M12 — Part 12 实战、贡献与速查 + 全书收尾（L62–64）

- [ ] **M12.1 — L62 本地构建与调试**：图示=`bun dev` vs `opencode` 双栏(`cols`) + debugger 拓扑(`flow`)；锚点=`CONTRIBUTING.md`、`packages/opencode/script/build.ts`。
- [ ] **M12.2 — L63 测试与贡献**：图示=贡献流程(`timeline`) + issue-first/commit/style 规范(`table.t`)；锚点=`CONTRIBUTING.md`、`AGENTS.md`。
- [ ] **M12.3 — L64 术语表与索引**（SOFT_EXEMPT）：图示=概念依赖图(`flow`) + 术语一句话表(`table.t`) + 跳转回各课的链接；锚点=`CONTEXT.md`（Language 部分）+ 全书。
- [ ] **M12.4 — 全书收尾**：重建 `print_zh.html`/`print_en.html`；`check_html.py` **全站 0 ERROR / 0 WARN**；`check_links.py` 全绿；`build.py` 重跑无 diff；`README.md` 的 12 部分表定稿；`docs/L1-overview.md` 收口（全 64 课索引）。
- [ ] **M12.R — 全书最终审计**：C.5 两阶段审计**覆盖全书**（抽查每部分至少 1 课的 parity/亮点/图示/字数；核对术语表链接全部解析）→ 修正 → 最终 commit `feat: complete opencode visual guide (64 lessons, M12)`。

---

## Self-Review (计划自检)

**1. Spec 覆盖：** spec 的 64 课大纲 ↔ 本计划 M1–M12 的 64 个逐课 task 一一对应（Part 1–12 = M1–M12）；spec 的"构建/校验/部署"↔ M0 Task 0.4/0.5/0.8 + ci/deploy；spec 的"许可与声明"↔ M0 Task 0.7；spec 的"L1–L4 文档"↔ C.6 + 各 .R task；spec 的"M0–M12 里程碑"↔ 本计划同名里程碑。无遗漏。

**2. 占位符扫描：** 计划无 TBD/TODO；每课 task 给出图示建议 + 真实源码锚点；M0 给出完整可执行代码/命令。课程**内容**为执行产物（非占位符）——这是内容创作型项目的预期，质量由 C.2 质量门 + C.5 审计保证。

**3. 类型/命名一致：** `PAGES` 的 64 个 fname（Task 0.3）↔ `registry.CONTENT` 的 64 个键（Task 0.6 Step 4）↔ `partK.LESSON_NN` 编号 严格一致；`check_html.MAX_LESSON=64` ↔ 64 课；`SOFT_EXEMPT={"64-glossary.html"}` ↔ L64 fname；`ALLOW_MISSING` 的 PDF 名 ↔ `ci.yml` 的 `--print-to-pdf` 名一致（Task 0.5/0.7）。

**4. 关键依赖守护：** `build.py` 要求每个 PAGES 项在 CONTENT 中存在 → M0 全 64 占位满足；`check_html` ERROR 条件（≥80 字符、lang-zh/en、h1/title/desc）→ 占位 + 外壳满足；`quizzes.render` 对空题库返回 `""` → 占位课可 build。

---

## Execution Handoff

执行采用 **Subagent-Driven Development**（用户已授权自主从 M0 跑到 M12，每里程碑两阶段独立审计、审计 subagent 用当前主会话模型不降级）。M0 为代码脚手架（逐 Task 执行）；M1–M12 每课按 C.4、每里程碑按 C.5。
