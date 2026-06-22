# opencode 图解学习指南 / opencode Visual Guide

A visual, bilingual (English + 中文) guide to the **internals** of
[opencode](https://github.com/anomalyco/opencode) — **69 lessons** that take you
from "what is opencode" all the way to "how it's built and how to contribute".

> **Disclaimer:** This is **third-party, unofficial** educational material *about*
> opencode. It contains **no opencode source code**; it explains opencode by
> quoting small, cited snippets. opencode itself is licensed by its own authors.

Every lesson is self-contained, embeds both languages (toggle in the page), and uses
hand-drawn diagrams, worked-example traces, real (cited) TypeScript/Effect snippets,
and a short self-test quiz.

---

## What it covers

The guide is organized into **13 parts**, built up bottom-up:

| Part | Topic | Lessons |
| --- | --- | --- |
| 1 | The Big Picture — what opencode is, the monorepo map, one prompt's lifecycle | L01–04 |
| 2 | Effect Foundations — why Effect, Services & Layers, concurrency, the toolbox | L05–08 |
| 3 | Client/Server — the server, routes, the SSE event bus, SDK, transports | L09–13 |
| 4 | Session Core — sessions, the event-sourced inbox, the **V2 agent loop** | L14–20 |
| 5 | Context System — System Context, Context Sources, the **Context Epoch** | L21–27 |
| 6 | LLM Layer — the in-house multi-protocol LLM client | L28–35 |
| 7 | Tool System — defining/registering tools, permissions, bounded output, skills | L36–43 |
| 8 | Config, Agents, Providers — config loading, build/plan agents, MCP | L44–47 |
| 9 | Persistence — Drizzle+SQLite, the core tables, migration, compaction | L48–51 |
| 10 | The TUI — opentui, app structure, events→store, prompt, dialogs | L52–56 |
| 11 | Extensibility — plugins, hooks, LSP, PTY, ACP & the Location model | L57–61 |
| 12 | Practice & Reference — build/debug, test/contribute, glossary | L62–64 |
| 13 | Advanced Topics — event sourcing/sync, slash commands, http-recorder, device-code OAuth, ecosystem tour | L65–69 |

## How to view

**Locally** (zero dependencies, just Python 3):

```bash
cd src
python3 build.py
# then open ../index.html in a browser
```

**Online:** published via GitHub Pages (see the Deploy note below to enable it).

## How to print / export a PDF

```bash
cd src
python3 build_print.py
# open ../print_zh.html (Chinese) or ../print_en.html (English), then
# File -> Print -> Save as PDF (Ctrl/Cmd+P). Each lesson starts on a new page.
```

## Project structure

```
src/            generators + tooling (pure Python 3, no dependencies)
  part1.py .. part12.py   lesson content (bilingual), grouped by part
  quizzes.py              per-lesson self-test questions
  shell.py                page shell + the shared CSS + PAGES list
  registry.py             ordered filename -> bilingual content map
  placeholder.py          "work in progress" placeholder for unwritten lessons
  build.py                builds index.html + lessons/*.html
  build_print.py          builds print_zh.html + print_en.html
  check_html.py           structural HTML validation
  check_links.py          internal link validation
lessons/        generated lesson pages (committed, kept in sync)
index.html      generated table of contents (committed)
print_*.html    generated print editions (committed)
docs/           layered L1-L4 docs + superpowers/ (specs + plans)
```

## Build & validate

```bash
cd src
python3 build.py          # regenerate index.html + lessons/*.html
python3 build_print.py    # regenerate print_zh.html + print_en.html
python3 check_html.py     # structural checks (0 error expected)
python3 check_links.py    # all internal links must resolve
```

The generated HTML is committed and kept in sync with the sources; a re-run of
`build.py` should produce no diff. Lessons not yet written show a "work in
progress" placeholder and surface as `check_html` warnings until completed.

## Deploy note (GitHub Pages)

Deployment uses GitHub Actions (`.github/workflows/deploy.yml`). The repository
owner must enable Pages **once**: go to **Settings -> Pages -> Source** and select
**"GitHub Actions"**. The workflow cannot create the Pages site automatically (it
lacks admin scope); it only deploys.

## License

Dual-licensed:

- **Code** (everything under `src/`) — MIT, see [LICENSE](LICENSE).
- **Content** (the lesson text and diagrams rendered into `index.html`,
  `lessons/*.html`, `print_*.html`) — CC BY 4.0, see [LICENSE-CONTENT](LICENSE-CONTENT).

---

## 中文说明

这是一份 [opencode](https://github.com/anomalyco/opencode) **内部源码原理**的**图解、双语**
学习指南，共 **69 课**，自底向上从"opencode 是什么"一路讲到"它如何构建、怎么贡献"。

> **声明：** 本项目是**第三方、非官方**的学习材料，**不包含 opencode 源码**，只通过引用
> 少量、标注来源的代码片段来讲解。opencode 本身由其作者按其许可发布。

每一课都自成一体、内嵌中英双语（页内可切换），用手绘风格图、worked-example 追踪图、
真实（标注来源的）TypeScript/Effect 代码片段，以及一段自测题来讲清一个概念。

**13 个部分**（自底向上，层层递进）：① 宏观全景（L01–04）② Effect 地基（L05–08）
③ 客户端/服务器（L09–13）④ Session 与 agent 循环（L14–20）⑤ Context Epoch 系统（L21–27）
⑥ LLM 协议层（L28–35）⑦ 工具系统（L36–43）⑧ 配置·Agents·Provider（L44–47）
⑨ 持久化（L48–51）⑩ TUI（L52–56）⑪ 扩展与集成（L57–61）⑫ 实战与速查（L62–64）⑬ 深入专题（L65–69）。

**怎么看：** 本地零依赖，`cd src && python3 build.py` 后用浏览器打开 `index.html`；
在线版见 GitHub Pages。

**怎么打印：** `cd src && python3 build_print.py`，再打开 `print_zh.html`（中文）或
`print_en.html`（英文），用 `Ctrl/Cmd+P` 导出 PDF，每课自动分页。

**许可：** 双许可 —— 代码（`src/`）用 MIT（见 LICENSE），教学内容（课程文字与图）用
CC BY 4.0（见 LICENSE-CONTENT）。

**部署须知：** GitHub Pages 需所有者先在 **Settings -> Pages -> Source** 手动选
**"GitHub Actions"** 启用一次。
