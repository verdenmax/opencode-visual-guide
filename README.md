<div align="center">

# 📖 opencode 图解学习指南 · opencode Visual Guide

**A visual, bilingual (中文 + English) deep-dive into the _internals_ of [opencode](https://github.com/anomalyco/opencode).**

_From "what is opencode" all the way to "how it's built and how to contribute" — 69 illustrated, source-accurate lessons._

<br/>

[![Read online](https://img.shields.io/badge/Read_online-Live_Demo-6d5ce7?logo=githubpages&logoColor=white)](https://verdenmax.github.io/opencode-visual-guide/)
[![CI](https://github.com/verdenmax/opencode-visual-guide/actions/workflows/ci.yml/badge.svg)](https://github.com/verdenmax/opencode-visual-guide/actions/workflows/ci.yml)
[![Deploy](https://github.com/verdenmax/opencode-visual-guide/actions/workflows/deploy.yml/badge.svg)](https://github.com/verdenmax/opencode-visual-guide/actions/workflows/deploy.yml)

[![Lessons](https://img.shields.io/badge/lessons-69-6d5ce7)](https://verdenmax.github.io/opencode-visual-guide/)
[![Parts](https://img.shields.io/badge/parts-13-7048e8)](https://verdenmax.github.io/opencode-visual-guide/)
[![Bilingual](https://img.shields.io/badge/bilingual-中文_+_English-7048e8)](https://verdenmax.github.io/opencode-visual-guide/)
[![Explains opencode](https://img.shields.io/badge/explains-opencode-0b7285?logo=github&logoColor=white)](https://github.com/anomalyco/opencode)
[![Dependencies](https://img.shields.io/badge/dependencies-0-2b8a3e)](#build--validate)
[![Code: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![Content: CC BY 4.0](https://img.shields.io/badge/content-CC_BY_4.0-blue.svg)](LICENSE-CONTENT)

[**🌐 Read online**](https://verdenmax.github.io/opencode-visual-guide/) · [**🖨️ Print / PDF**](#-print--export-pdf) · [**📚 Curriculum**](#-what-it-covers) · [**中文说明**](#-中文说明)

</div>

> [!NOTE]
> **Third-party, unofficial** educational material *about* opencode. It contains **no opencode source code** — it explains opencode by quoting small, **cited** snippets. opencode itself is licensed by its own authors.

---

## ✨ Why this guide

- 🧭 **Source-code-internals oriented** — not a user manual. Every claim is traced to real `file:line` and verified against the opencode source.
- 🌏 **Fully bilingual** — every lesson embeds 中文 + English; toggle the language right on the page.
- 🎨 **Visual first** — hand-drawn-style diagrams, worked-example traces, and real (cited) TypeScript/Effect snippets carry the explanation.
- 🧩 **Bottom-up** — 13 parts build on each other, from the Effect foundation to the whole ecosystem.
- 🧠 **Active recall** — each lesson ends with a short self-test quiz (multiple-choice + open questions).
- 📦 **Zero dependencies** — a tiny pure-Python static-site generator; `python3 build.py` and you're done.

> **Deepest dives:** the V2 agent loop · the System Context / Context Epoch system · the in-house multi-protocol LLM layer · the Effect patterns that run through everything.

---

## 📚 What it covers

The guide is organized into **13 parts**, built up bottom-up:

| # | Part | What you'll learn | Lessons |
| :-: | --- | --- | :-: |
| 1 | **The Big Picture** | what opencode is, the monorepo map, one prompt's lifecycle | `L01–04` |
| 2 | **Effect Foundations** | why Effect, Services & Layers, concurrency, the toolbox | `L05–08` |
| 3 | **Client / Server** | the server, routes, the SSE event bus, SDK, transports | `L09–13` |
| 4 | **Session Core** ★ | sessions, the event-sourced inbox, the **V2 agent loop** | `L14–20` |
| 5 | **Context System** ★ | System Context, Context Sources, the **Context Epoch** | `L21–27` |
| 6 | **LLM Layer** ★ | the in-house multi-protocol LLM client | `L28–35` |
| 7 | **Tool System** | defining/registering tools, permissions, bounded output, skills | `L36–43` |
| 8 | **Config · Agents · Providers** | config loading, build/plan agents, MCP | `L44–47` |
| 9 | **Persistence** | Drizzle + SQLite, the core tables, migration, compaction | `L48–51` |
| 10 | **The TUI** | opentui, app structure, events→store, prompt, dialogs | `L52–56` |
| 11 | **Extensibility** | plugins, hooks, LSP, PTY, ACP & the Location model | `L57–61` |
| 12 | **Practice & Reference** | build/debug, test/contribute, glossary | `L62–64` |
| 13 | **Advanced Topics** | event sourcing/sync, slash commands, http-recorder, device-code OAuth, ecosystem tour | `L65–69` |

<sub>★ = the most unique, most worth-reading parts.</sub>

---

## 🚀 Quick start

**Read online** → **<https://verdenmax.github.io/opencode-visual-guide/>**

**Build locally** (zero dependencies, just Python 3):

```bash
cd src
python3 build.py        # generates ../index.html + ../lessons/*.html
# then open ../index.html in your browser
```

## 🖨️ Print / export PDF

```bash
cd src
python3 build_print.py  # generates ../print_zh.html + ../print_en.html
# open print_zh.html (中文) or print_en.html (English), then
# File → Print → Save as PDF (Ctrl/Cmd+P). Each lesson starts on a new page.
```

---

## 🗂️ Project structure

```text
src/                         generators + tooling (pure Python 3, no dependencies)
  part1.py … part13.py       lesson content (bilingual), grouped by part
  quizzes.py                 per-lesson self-test questions
  shell.py                   page shell + shared CSS + the PAGES list
  registry.py                ordered filename → bilingual content map
  build.py                   builds index.html + lessons/*.html
  build_print.py             builds print_zh.html + print_en.html
  check_html.py              structural HTML validation
  check_links.py             internal link validation
lessons/                     generated lesson pages (committed, kept in sync)
index.html                   generated table of contents (committed)
print_*.html                 generated print editions (committed)
docs/                        layered L1–L4 docs + superpowers/ (specs + plans)
```

## Build & validate

```bash
cd src
python3 build.py          # regenerate index.html + lessons/*.html
python3 build_print.py    # regenerate print_zh.html + print_en.html
python3 check_html.py     # structural checks (0 error / 0 warning expected)
python3 check_links.py    # all internal links must resolve
```

The generated HTML is **committed and kept in sync** with the sources — a re-run of `build.py` should produce no diff (CI enforces this).

## 🌐 Deploy (GitHub Pages)

Deployment runs on GitHub Actions ([`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)) on every push to `main`. The repository owner must enable Pages **once**: **Settings → Pages → Source → "GitHub Actions"**. The workflow only deploys; it cannot create the Pages site itself (it lacks admin scope).

## 📄 License

Dual-licensed:

| Part | License | |
| --- | --- | --- |
| **Code** (everything under `src/`) | MIT | [LICENSE](LICENSE) |
| **Content** (lesson text & diagrams in `index.html`, `lessons/*.html`, `print_*.html`) | CC BY 4.0 | [LICENSE-CONTENT](LICENSE-CONTENT) |

---

## 📘 中文说明

一份 [opencode](https://github.com/anomalyco/opencode) **内部源码原理**的**图解、双语**学习指南，共 **69 课 · 13 个部分**，自底向上从"opencode 是什么"一路讲到"它如何构建、怎么贡献"。每条讲解都对应真实源码 `file:line`，并已逐条核对。

> [!NOTE]
> 本项目是**第三方、非官方**的学习材料，**不包含 opencode 源码**，只通过引用少量、标注来源的代码片段来讲解。opencode 本身由其作者按其许可发布。

**特点**

- 🧭 **面向源码内部原理**，不是使用手册；
- 🌏 **全程中英双语**，页内一键切换；
- 🎨 **图解优先** —— 手绘风格图 + worked-example 追踪图 + 标注来源的真实代码片段；
- 🧩 **自底向上** 13 个部分层层递进；
- 🧠 每课配 **自测题**（选择 + 发散思考）；
- 📦 **零依赖**，纯 Python 3 静态站点生成器。

**13 个部分**（自底向上）：① 宏观全景（L01–04）② Effect 地基（L05–08）③ 客户端/服务器（L09–13）④ Session 与 agent 循环 ★（L14–20）⑤ Context Epoch 系统 ★（L21–27）⑥ LLM 协议层 ★（L28–35）⑦ 工具系统（L36–43）⑧ 配置·Agents·Provider（L44–47）⑨ 持久化（L48–51）⑩ TUI（L52–56）⑪ 扩展与集成（L57–61）⑫ 实战与速查（L62–64）⑬ 深入专题（L65–69）。

**怎么看：** 在线版 → <https://verdenmax.github.io/opencode-visual-guide/>；本地零依赖 `cd src && python3 build.py` 后浏览器打开 `index.html`。

**怎么打印：** `cd src && python3 build_print.py`，打开 `print_zh.html`（中文）或 `print_en.html`（英文），`Ctrl/Cmd+P` 导出 PDF，每课自动分页。

**许可：** 双许可 —— 代码（`src/`）用 **MIT**（见 [LICENSE](LICENSE)）；教学内容（课程文字与图）用 **CC BY 4.0**（见 [LICENSE-CONTENT](LICENSE-CONTENT)）。

<div align="center"><sub>Made with diagrams, pseudocode, and a lot of source-reading. · 用图、伪代码和大量源码阅读做成。</sub></div>
