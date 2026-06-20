# opencode 图解学习指南 — 设计文档 (Design Spec)

- 日期：2026-06-20
- 状态：草案（待用户评审）
- 类型：教育材料项目（第三方、非官方）
- 模仿对象：`llama-cpp-visual-guide`（同级独立项目）

---

## 1. 概述 (Overview)

一份**图解、双语（中文 + English）**的学习指南，深入讲解开源 AI 编程 agent
[**opencode**](https://github.com/anomalyco/opencode) 的**内部源码与架构**——从"opencode 是什么"
一路讲到"V2 Session Core 的 agent 循环、Context Epoch 系统、自研多协议 LLM 层、Effect 函数式架构"
等最核心、最独特的实现细节，最终覆盖整个 monorepo 的全部 package。

指南是一个**独立项目**，放在 `/home/verden/course/opencode-visual-guide/`，与 `llama-cpp-visual-guide`
平级，拥有独立的 git 历史。它**不包含 opencode 源码**，只通过引用少量、标注来源的代码片段来讲解；
opencode 本身由其作者按其许可发布。

每一课自成一体、内嵌中英双语（页内可切换），用手绘风格图、worked-example 追踪图、
真实（标注来源的）TypeScript/Effect 代码片段，以及一段自测题来讲清一个概念。

## 2. 目标与非目标 (Goals / Non-Goals)

**目标：**

- 让读者读懂 opencode 的**内部实现**，能据此阅读源码、定位模块、乃至贡献代码。
- 自底向上、层层递进地覆盖**整个 monorepo 的所有 package**（核心 + 周边）。
- 每课达到参考项目的质量标准：双语 parity、≥6 图示块、zh ≥3000 中文字（目标 4000+）、
  真实代码引用、要点卡 + 类比卡 + 自测题。
- 零依赖、可复现的构建（纯 Python 3 生成 HTML），生成产物入库并与源同步。

**非目标：**

- 不是 opencode 的**使用教程**（安装/配置/日常使用）——本指南面向"读懂内部"，不面向"会用"。
- 不收录 opencode 源码全文，只引用必要的小片段并标注来源。
- 不追求与 opencode 上游实时同步；以某一快照时点的源码为讲解基准，必要时标注版本/提交。

## 3. 关键设计决策 (Decisions)

下列决策已在头脑风暴阶段与用户逐项确认：

| 维度 | 决策 | 说明 |
| --- | --- | --- |
| 定位 | **源码/内部架构导向** | 像 llama-cpp-guide 那样深入讲内部实现，面向想读懂/贡献源码的开发者 |
| 范围 | **全覆盖所有 package** | 核心运行时 + 所有周边（desktop/web/slack/enterprise/SDK/基础设施），约 64 课 |
| 语言 | **双语 zh/en** | 每课内嵌中英文，页内切换；中英 parity |
| 技术栈 | **沿用 Python 生成器** | 直接 fork 参考项目 `src/` 基础设施（零依赖、模板成熟） |
| 位置 | **独立新目录** | `/home/verden/course/opencode-visual-guide/`，独立 git 仓 |
| 组织 | **自底向上分层** | 先打 Effect/技术栈地基 → 客户端/服务器骨架 → V2 核心主线 → 存储/TUI/扩展 → 实战 |

## 4. 架构 (Architecture)

### 4.1 项目结构

```
opencode-visual-guide/
  src/                  纯 Python 3，零依赖（fork 自参考项目）
    part1.py .. part12.py   各部分的双语课程内容（每课一个 LESSON_NN dict）
    quizzes.py              每课自测题
    shell.py                页面外壳 + 共享 CSS + PAGES 列表（filename, zh_title, en_title, part）
    registry.py             文件名 → {"zh":..., "en":...} 映射（CONTENT）
    build.py                生成 index.html + lessons/*.html
    build_print.py          生成 print_zh.html + print_en.html
    check_html.py           结构校验（适配新课数 MAX_LESSON=64）
    check_links.py          内部链接校验
  lessons/              生成的课程页（入库，与源同步）
  index.html            生成的目录页（入库）
  print_zh.html / print_en.html   打印版（入库）
  docs/                 L1-L4 分层文档 + superpowers/（specs + plans）
  README.md             双语项目说明（含构建/部署/许可）
  LICENSE               MIT（代码）
  LICENSE-CONTENT       CC BY 4.0（内容）
  .github/workflows/deploy.yml   GitHub Pages via Actions
```

### 4.2 生成器流水线 (Generator pipeline)

沿用参考项目的**单一事实来源**模式：

1. `shell.py` 定义 `PAGES`（有序的 `(filename, zh_title, en_title, part)` 列表）与共享 CSS、页面外壳。
2. `partN.py` 定义每课的 `LESSON_NN = {"zh": r"""<html>""", "en": r"""<html>"""}`（富 HTML 片段）。
3. `registry.py` 把文件名映射到课程内容（`CONTENT`），与 `PAGES` 保持同步。
4. `quizzes.py` 提供每课自测题。
5. `build.py` 读取上述内容，套上 `shell.py` 的外壳，生成 `index.html` 与 `lessons/*.html`。
6. `build_print.py` 生成中/英两个单文件打印版。
7. `check_html.py` / `check_links.py` 做结构与链接回归校验（CI 0 error / 0 warning 期望）。

生成的 HTML **入库并与源同步**：重跑 `build.py` 应无 diff。

### 4.3 每课格式与质量标准

复用参考项目 `check_html.py` 的硬/软约束，并按 opencode 特点适配：

- **双语**：每课同时含 `lang-zh` 与 `lang-en` 两块内容，页内切换。
- **要点卡 + 类比卡**：每课含一张"本课要点 / Key points"卡与一张"生活类比"卡。
- **图示密度**：每课 **≥6 个图示块**（`layers`/`flow`/`cols`/`cellgroup`/`timeline`/`trace` 或 `table.t`），
  即每种语言 ≥3 个。opencode 偏重：client/server 流向图、Effect Layer 组合图、状态机（Context Epoch）、
  时序图（一次 provider turn）、数据结构图（messages/parts、SQL 表）。
- **字数**：zh **≥3000 中文字**（软下限，目标 4000+），中英 parity，无大段文字墙
  （zh 单段 <200 中文字，en 单段 <120 词）。
- **真实代码引用**：从 opencode 源码摘取并**简化**的 TypeScript/Effect 片段，
  在卡片内标注来源路径（如 `packages/core/src/session/runner/llm.ts`）。`<pre>` 内不得出现未转义的 `<`。
- **导航链**：每课含 prev/next 链，与 `PAGES` 顺序一致。
- **自测题**：每课末尾一段 self-test。
- **术语表（L64）** 作为 `SOFT_EXEMPT`，豁免图示/字数等软约束。

### 4.4 分层文档 L1-L4

> 注：此处 **L1-L4 指文档层级**（单位数），与**课程编号 L01-L64**（两位零填充）是两套独立体系，勿混淆。

放在 `docs/`，**边写课程边同步填充**（随课程一起提交）：

- **L1**（`docs/L1-overview.md`）：整个指南 + opencode 整体架构的一页概览。
- **L2**（`docs/L2-parts/`）：每个部分（Part 1-12）的职责与覆盖范围。
- **L3**（`docs/L3-details/`）：每个部分内各主题的细节要点。
- **L4**（`docs/L4-api/`）：逐源文件的 API/职责对照（opencode 源文件 → 讲到它的课）。

### 4.5 适配 opencode 的内容策略

- 代码片段语言：从参考项目的 C/C++ 换成 **TypeScript + Effect**；保留"简化自源码 + 标注路径"的做法。
- 类比基调：服务器="常驻大脑"、客户端="各种终端"、SDK="统一的电话线"、
  Effect Layer="可插拔的依赖电路"、Context Epoch="一次会话的不可变快照纪元"。
- 重点深讲 4 个 opencode 最独特处（见大纲 ⭐）：V2 agent 循环、System Context/Context Epoch、
  自研多协议 LLM 层、Effect 函数式架构。
- V1/V2 并存：以 V2 Session Core 为主线，但在关键处（如 agent 循环、存储、配置）**对照 V1**，
  因为 V1 仍是当前默认运行路径，读者会在源码中遇到它。

## 5. 完整课程大纲 (Lesson Outline)

共 **64 课 · 12 部分**。⭐ = opencode 最独特、最值得深讲。每课附主要源码锚点（讲解时摘取并简化）。

### Part 1 — 宏观全景 (Overview)

- **L01 opencode 是什么**：客户端/服务器架构的 AI 编程 agent；对比 Claude Code / Cursor。锚点：`README.md`、`packages/opencode/src/index.ts`。
- **L02 项目地图**：monorepo 24 个 package 全景，CORE vs 周边。锚点：`packages/*`、`package.json`、`turbo.json`。
- **L03 一次对话的端到端旅程**：keypress → render 的数据流总览（约 11 跳）。锚点：`cli/cmd/tui.ts`、`server/server.ts`、`core/src/session/runner/llm.ts`。
- **L04 V1 与 V2**：一场正在进行的架构迁移（AI-SDK/文件存储 → 纯 Effect/Drizzle）。锚点：`packages/opencode/src/session/` vs `packages/core/`。

### Part 2 — Effect 函数式地基 (Effect Foundations)

- **L05 为什么是 Effect** ⭐：从 try/catch 到类型化 effect、错误即值。锚点：`AGENTS.md`（风格）、`packages/core/src/effect/*`。
- **L06 Context.Service 与 Layer**：依赖注入与组合。锚点：`core/src/*` 中的 `Context.Service`/`Layer.effect`。
- **L07 并发原语**：Fiber / FiberSet / Deferred / Latch / Stream。锚点：`core/src/session/runner/llm.ts`（FiberSet）、`run-coordinator.ts`。
- **L08 项目里的 Effect 工具箱**：keyed-mutex / memo-map / service-use / Effect.fn。锚点：`core/src/keyed-mutex.ts`、`memo-map.ts`、`service-use.ts`。

### Part 3 — 客户端/服务器架构 (Client/Server)

- **L09 server 总览**：Effect HttpApi + OpenApi（为什么不用 Hono）。锚点：`packages/opencode/src/server/server.ts`、`routes/instance/httpapi/api.ts`。
- **L10 路由组与 handler**：session / event / config / provider…。锚点：`routes/instance/httpapi/groups/*`、`handlers/*`、`middleware/*`。
- **L11 SSE 事件总线**：GlobalBus → 客户端实时更新。锚点：`groups/event.ts`、`GlobalBus`。
- **L12 SDK 生成**：从 OpenAPI 到类型安全客户端。锚点：`script/generate.ts`、`packages/sdk/js/src/gen/*`、`openapi.json`。
- **L13 多客户端传输**：网络 server vs RPC worker（嵌入式 server 模式）。锚点：`cli/cmd/tui.ts` `createWorkerFetch()`、`cli/tui/worker.ts`。

### Part 4 — V2 Session 与 Agent 循环 ⭐ (Session Core)

- **L14 Session 是什么**：messages 与 parts。锚点：`core/src/session/message.ts`、`session/sql.ts`。
- **L15 事件溯源的输入收件箱**：`session_input`。锚点：`core/src/session/input.ts`、`prompt.ts`。
- **L16 SessionRunCoordinator**：run / wake / interrupt 并发协调。锚点：`core/src/session/run-coordinator.ts`、`execution.ts`。
- **L17 V2 agent 循环** ⭐⭐：一次 provider turn 的解剖（必讲）。锚点：`core/src/session/runner/llm.ts`（含头部 checklist 注释）。
- **L18 工具调用与 FiberSet 并发执行**：tool-call → settle。锚点：`runner/llm.ts`（~256-280）、`toolMaterialization.settle`。
- **L19 投影历史**：projector 与 history 重载。锚点：`core/src/session/projector.ts`、`history.ts`、`session_message` 表。
- **L20 有界步数、settlement 与错误处理**：MAX_STEPS、StepLimitExceededError。锚点：`runner/llm.ts`（~383-392）、`runner/index.ts`。

### Part 5 — System Context 与 Context Epoch ⭐ (Context System)

- **L21 System Context 总览** ⭐：opencode 最独特的抽象。锚点：`CONTEXT.md`、`core/src/system-context/index.ts`。
- **L22 Context Source**：codec / loader / 纯 renderer（baseline/update/removal）。锚点：`system-context/index.ts` `SystemContext.make`。
- **L23 System Context Registry**：作用域化的有序生产者。锚点：`system-context/registry.ts`、`builtins.ts`。
- **L24 Context Epoch**：不可变基线 + Context Snapshot。锚点：`core/src/session/context-epoch.ts`、迁移 `add_session_context_snapshot`。
- **L25 Mid-Conversation System Messages**：安全边界的上下文注入。锚点：`CONTEXT.md`（Safe Provider-Turn Boundary）、`context-epoch.ts`。
- **L26 内置 Context Sources**：指令(AGENTS.md) / 日期 / skill 引导。锚点：`system-context/builtins.ts`、`instruction-context.ts`。
- **L27 Agent 切换与 Epoch 替换**：`add_context_epoch_agent`。锚点：`CONTEXT.md`、`core/src/agent.ts`、`context-epoch.ts`。

### Part 6 — LLM 协议层 ⭐ (LLM Layer)

- **L28 LLM 层总览**：provider-agnostic 客户端。锚点：`packages/llm/src/llm.ts`、`schema/*`。
- **L29 协议适配器概念** ⭐：谁拥有 wire 编码。锚点：`llm/src/route/client.ts`、`CONTEXT.md`（lines 49,103）。
- **L30 Anthropic Messages 协议**。锚点：`llm/src/protocols/anthropic-messages.ts`、`protocols/utils/cache.ts`。
- **L31 OpenAI Chat / Responses 协议**。锚点：`protocols/openai-chat.ts`、`openai-responses.ts`、`openai-compatible-chat.ts`。
- **L32 Gemini / Bedrock Converse 协议**。锚点：`protocols/gemini.ts`、`bedrock-converse.ts`、`bedrock-event-stream.ts`。
- **L33 路由与传输**：HTTP vs WebSocket / eventstream。锚点：`llm/src/route/transport/http.ts`、`websocket.ts`、`framing.ts`。
- **L34 流式 LLMEvent 与 prompt 缓存**：联动 Context Epoch 基线前缀。锚点：`llm/src/schema/*`(LLMEvent)、`cache-policy.ts`。
- **L35 模型/provider 解析与 Copilot 自定义 provider**：models.dev。锚点：`core/src/models-dev.ts`、`catalog.ts`、`core/src/github-copilot/*`。

### Part 7 — 工具系统 (Tool System)

- **L36 工具定义**：`Tool.make` 与 schema codec。锚点：`core/src/tool/tool.ts`（make/withPermission/definition/settle）。
- **L37 工具注册表**：ToolRegistry 与 materialize。锚点：`core/src/tool/registry.ts`、`builtins.ts`（locationLayer）。
- **L38 文件工具**：read / write / edit / apply-patch。锚点：`core/src/tool/{read,write,edit,apply-patch}.ts`。
- **L39 搜索与执行工具**：glob / grep / bash。锚点：`core/src/tool/{glob,grep,bash}.ts`、`pty/*`。
- **L40 其他内置工具**：webfetch / websearch / question / todowrite。锚点：`core/src/tool/{webfetch,websearch,question,todowrite}.ts`。
- **L41 权限系统**：withPermission / policy / saved，per-turn 冻结。锚点：`core/src/permission.ts`、`permission/{saved,schema,sql}.ts`。
- **L42 有界工具输出**：Model Tool Output + Managed Tool Output File。锚点：`core/src/tool-output-store.ts`、`config/tool-output.ts`、`CONTEXT.md`。
- **L43 Skills 系统**：names 作为 Context Source，body 经权限化 `skill` 工具。锚点：`core/src/skill/*`、`tool/skill.ts`。

### Part 8 — 配置、Agents 与 Provider (Config / Agents / Providers)

- **L44 配置加载**：`opencode.json`，V1/V2 config。锚点：`core/src/config.ts`、`config/*`、`core/src/v1/config/*`。
- **L45 Agents**：build / plan，agent prompt 模板，plan 模式。锚点：`core/src/agent.ts`、`config/agent.ts`、`opencode/src/agent/prompt/*.txt`。
- **L46 MCP 集成**：动态作用域工具 + OAuth。锚点：`opencode/src/mcp/*`、`config/mcp.ts`、`groups/mcp.ts`。
- **L47 Provider 插件定义**：~40 个 provider。锚点：`core/src/plugin/provider/*`、`opencode/src/provider/provider.ts`。

### Part 9 — 持久化与存储 (Persistence)

- **L48 Drizzle + SQLite**：schema 与 migration。锚点：`core/src/database/{database,migration}.ts`、`drizzle.config.ts`、`schema.json`。
- **L49 核心表**：session / message / part / session_message / session_input / context_epoch。锚点：`core/src/session/sql.ts`、各 `*/sql.ts`。
- **L50 V1 文件存储与 V1→V2 数据迁移**。锚点：`opencode/src/storage/storage.ts`、`core/src/data-migration.sql.ts`。
- **L51 Compaction、摘要与 Snapshots / revert**：git 集成。锚点：`core/src/session/compaction.ts`、`opencode/src/snapshot/index.ts`、`session/revert.ts`。

### Part 10 — TUI 与客户端渲染 (TUI)

- **L52 opentui**：终端里的 SolidJS 渲染器。锚点：`@opentui/core` `createCliRenderer`、`packages/tui/src/app.tsx`。
- **L53 TUI 应用结构**：app.tsx 与 context providers。锚点：`tui/src/context/{sdk,runtime,project,route,prompt,theme}.tsx`。
- **L54 事件 → store**：sync / data reducers 与 16ms 批渲染。锚点：`tui/src/context/{sync,data}.tsx`。
- **L55 prompt 组件**：编辑器 / 自动补全 / 历史 / frecency。锚点：`tui/src/component/prompt/*`。
- **L56 对话框、命令面板与 run CLI 的 scrollback**。锚点：`tui/src/component/{dialog-*,command-palette}.tsx`、`opencode/src/cli/cmd/run/scrollback.*`。

### Part 11 — 扩展与集成 (Extensibility)

- **L57 插件系统**：Plugin 与 Hooks。锚点：`packages/plugin/src/index.ts`、`opencode/src/plugin/loader.ts`、`core/src/plugin.ts`。
- **L58 插件 hooks 详解**：auth / provider / chat / tool / permission。锚点：`plugin/src/index.ts`（Hooks ~222）、内置插件 `opencode/src/plugin/*`。
- **L59 LSP 集成**：诊断与代码智能。锚点：`opencode/src/lsp/{client,diagnostic,launch,server}.ts`、`tool/lsp.ts`。
- **L60 PTY / shell**：终端进程管理。锚点：`core/src/pty/*`（bun/node 后端、ticket、protocol）、`CONTEXT.md`（PTY Environment）。
- **L61 ACP 与 Location 抽象**：opencode 作为 ACP server，session 移动与 control plane。锚点：`opencode/src/acp/*`、`core/src/location*.ts`、`control-plane/move-session.ts`。

### Part 12 — 实战、贡献与速查 (Practice & Reference)

- **L62 本地构建与调试**：bun dev，debugger。锚点：`CONTRIBUTING.md`、`packages/opencode/script/build.ts`。
- **L63 跑测试与贡献流程**：issue-first、conventional commits、风格指南。锚点：`CONTRIBUTING.md`、`AGENTS.md`。
- **L64 术语表 & 概念索引**（SOFT_EXEMPT）：汇总全书关键术语，链接回相应课。锚点：`CONTEXT.md`（Language 部分）。

## 6. 构建、校验与部署 (Build / Validate / Deploy)

```bash
cd src
python3 build.py          # 生成 index.html + lessons/*.html
python3 build_print.py    # 生成 print_zh.html + print_en.html
python3 check_html.py     # 结构校验（0 error / 0 warning 期望）
python3 check_links.py    # 内部链接必须全部解析
```

- 生成的 HTML 入库并与源同步：重跑 `build.py` 应无 diff（CI 可据此守护）。
- `check_html.py` 适配：`MAX_LESSON=64`、`PAGES` 含 64 项 12 部分、`SOFT_EXEMPT={"64-glossary.html"}`。
- 部署：`.github/workflows/deploy.yml` 用 GitHub Actions 发布到 Pages；仓库所有者需先在
  Settings → Pages → Source 选 "GitHub Actions" 启用一次（workflow 无管理员权限，不能自动建站）。

## 7. 许可与声明 (License & Disclaimer)

- **双许可**：代码（`src/`）MIT，见 `LICENSE`；教学内容（`index.html`/`lessons/*`/`print_*`）CC BY 4.0，见 `LICENSE-CONTENT`。
- **声明**：第三方、非官方学习材料，不包含 opencode 源码，只通过引用少量、标注来源的代码片段讲解；
  opencode 本身由其作者按其许可发布。README 顶部需中英文各放一段 disclaimer。

## 8. 实施分期 (Milestones)

建议分里程碑推进，每个里程碑产出可校验、可部署的增量（每课达标后再进入下一课）：

- **M0 — 脚手架**：fork `src/` 基础设施；改 `shell.py` 的 CSS 品牌/标题、`PAGES`（64 项占位）、
  `check_html.py` 的 `MAX_LESSON`；建 `README`、双 `LICENSE`、`deploy.yml`、`docs/` 骨架。
  产出：能 `build.py` 出空骨架并通过 `check_html`（允许内容缺失的占位课先不计 ERROR，或先放最小合格内容）。
- **M1 — Part 1 宏观全景**（L01-04）：先打通"一课完整达标"的样板，确立图示/类比/代码引用的范式。
- **M2 — Part 2 Effect 地基**（L05-08）。
- **M3 — Part 3 客户端/服务器**（L09-13）。
- **M4 — Part 4 Session/agent 循环 ⭐**（L14-20）。
- **M5 — Part 5 Context Epoch ⭐**（L21-27）。
- **M6 — Part 6 LLM 协议层 ⭐**（L28-35）。
- **M7 — Part 7 工具系统**（L36-43）。
- **M8 — Part 8 配置/Agents/Provider**（L44-47）。
- **M9 — Part 9 持久化**（L48-51）。
- **M10 — Part 10 TUI**（L52-56）。
- **M11 — Part 11 扩展集成**（L57-61）。
- **M12 — Part 12 实战/速查 + 全书收尾**（L62-64，含 print 版、链接校验、L1-L4 文档收口）。

每个里程碑：写课程内容 → `build.py` → `check_html.py`/`check_links.py` 全绿 → 同步 L1-L4 文档 → 提交。

## 9. 风险与开放问题 (Risks / Open Questions)

- **工程量大**：64 课双语、每课 ≥3000 中文字 + ≥6 图示，是长期工程；分里程碑、可中途暂停/续作。
- **源码会漂移**：opencode 处于 V1→V2 迁移中，文件路径/行号可能变动。对策：引用以"模块+函数"为主、
  行号为辅，必要时在 README 标注讲解基准时点。
- **部分周边包信息稀**（console/identity/containers/stats 多无 package.json）：这些课以"它在整体中的位置"
  为主，篇幅可酌情精简，但仍保证达标的图示与字数。
- **代码片段许可**：仅引用**小段**并标注来源、配 disclaimer；不整文件搬运。

## 10. 成功标准 (Definition of Done)

- 64 课全部存在，`build.py` 重跑无 diff，`check_html.py`/`check_links.py` 0 error。
- 每课双语 parity、要点卡 + 类比卡、≥6 图示、zh ≥3000 中文字、真实代码引用、自测题。
- L1-L4 文档与课程同步、`README` 双语、双 `LICENSE`、`deploy.yml` 就绪。
