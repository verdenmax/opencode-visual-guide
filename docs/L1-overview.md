# L1 — 全书与 opencode 整体概览 (Overview)

> 分层文档约定：**L1** 整本指南 + opencode 整体架构一页概览；**L2** 每个部分的职责；
> **L3** 每个部分内各课的细节；**L4** opencode 源文件 → 讲到它的课 的对照。
> 本文件随里程碑推进逐步收口（M0 建立框架，M12 定稿）。

## opencode 是什么

opencode 是一个**开源的 AI 编程 agent**（类比 Claude Code / Cursor 的命令行形态）。它是一个
**Bun + TypeScript 的 monorepo**，采用**客户端/服务器**架构：一个长期运行的 **server**
（Effect HttpApi + SSE 事件总线）拥有全部 agent 逻辑、session、工具、provider 与持久化；
多个**客户端**（TUI、`run` CLI、web、desktop、Slack、ACP）通过**生成的 SDK** 与之通信。

## 整体架构（自底向上）

```
客户端 (TUI / run CLI / web / desktop / Slack / ACP)
   │  生成的 SDK（REST + SSE）  /  TUI 走进程内 RPC worker
   ▼
server（Effect HttpApi + OpenApi + SSE 事件总线）
   ▼
Session 引擎
   ├─ V1（packages/opencode/src/session，基于 Vercel AI-SDK，文件/JSON 存储）
   └─ V2 Session Core（packages/core，纯 Effect + Drizzle/SQLite）★ 主线
        ├─ agent 循环（runner/llm.ts）
        ├─ System Context / Context Epoch
        ├─ 工具系统 + 权限 + 有界输出
        └─ 持久化（Drizzle + SQLite）
   ▼
LLM 协议层（packages/llm：provider-agnostic，多协议适配器 + 路由/传输）
   ▼
Provider（Anthropic / OpenAI / Gemini / Bedrock / Copilot …，经 models.dev 解析）
```

**技术栈：** Bun（运行时）· TypeScript · **Effect**（函数式：Service/Layer/Fiber/Stream）·
**Drizzle ORM + SQLite**（V2 持久化）· **SolidJS + opentui**（TUI）· Effect HttpApi（server）。

**最独特、最值得深读的四处：** ① V2 agent 循环 ② System Context / Context Epoch ③ 自研多协议
LLM 层 ④ 贯穿全局的 Effect 模式。

## 12 部分索引与依赖顺序

| 部分 | 主题 | 课 | 依赖 |
| --- | --- | --- | --- |
| 1 | 宏观全景 | L01–04 | — |
| 2 | Effect 地基 | L05–08 | 1 |
| 3 | 客户端/服务器 | L09–13 | 2 |
| 4 | Session 与 agent 循环 ★ | L14–20 | 2,3 |
| 5 | Context Epoch 系统 ★ | L21–27 | 4 |
| 6 | LLM 协议层 ★ | L28–35 | 4 |
| 7 | 工具系统 | L36–43 | 4 |
| 8 | 配置·Agents·Provider | L44–47 | 6,7 |
| 9 | 持久化 | L48–51 | 4 |
| 10 | TUI | L52–56 | 3 |
| 11 | 扩展与集成 | L57–61 | 7,8 |
| 12 | 实战与速查 | L62–64 | 全部 |

## 文档进度

- L1：本文件（M0 建立框架，M12 收口）。
- L2–L4：见 `docs/L2-parts/`、`docs/L3-details/`、`docs/L4-api/`，**12 个部分（part-1 ~ part-12）已全部填充完成**。
- 全书 64 课已全部完成；`check_html.py` 全站 0 error/0 warning、`check_links.py` 全部解析。
