"""Shared HTML shell (CSS design system + navigation) for the opencode visual guide."""

import base64

# ---- favicon (inline SVG, base64) ----
_FAVICON_SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'>"
    "<rect width='32' height='32' rx='7' fill='#c2630e'/>"
    "<text x='16' y='22' font-family='system-ui,sans-serif' font-size='15'"
    " font-weight='800' fill='#fff' text-anchor='middle'>ll</text></svg>"
)
FAVICON = "data:image/svg+xml;base64," + base64.b64encode(_FAVICON_SVG.encode()).decode()


def esc(s):
    """Escape plain text for an HTML text/attribute context.

    For chrome/meta strings that are NOT meant to carry inline markup (page
    titles, descriptions). Do NOT use on lesson body content or bi() inputs,
    which may legitimately contain inline tags.
    """
    return (
        str(s).replace("&", "&amp;").replace("<", "&lt;")
        .replace(">", "&gt;").replace('"', "&quot;")
    )


def head_meta(title, description, og_type="website"):
    """SEO / social meta tags + favicon for a page <head>."""
    t = esc(title)
    d = esc(description)
    return (
        f'<meta name="description" content="{d}">\n'
        f'<meta name="theme-color" content="#c2630e">\n'
        f'<link rel="icon" type="image/svg+xml" href="{FAVICON}">\n'
        f'<meta property="og:type" content="{og_type}">\n'
        f'<meta property="og:site_name" content="opencode 图解指南">\n'
        f'<meta property="og:title" content="{t}">\n'
        f'<meta property="og:description" content="{d}">\n'
        f'<meta name="twitter:card" content="summary">\n'
        f'<meta name="twitter:title" content="{t}">\n'
        f'<meta name="twitter:description" content="{d}">'
    )


# Ordered list of all pages:
# (filename, title_zh, title_en, part_zh, part_en)
PAGES = [
    ('01-what-is-opencode.html', 'opencode 是什么', 'What is opencode',
     '第一部分 · 宏观全景', 'Part 1 · The Big Picture'),
    ('02-project-map.html', '项目全景地图', 'The monorepo map',
     '第一部分 · 宏观全景', 'Part 1 · The Big Picture'),
    ('03-request-lifecycle.html', '一次对话的生命周期', 'Lifecycle of one prompt',
     '第一部分 · 宏观全景', 'Part 1 · The Big Picture'),
    ('04-v1-vs-v2.html', 'V1 与 V2：架构迁移', 'V1 vs V2: the migration',
     '第一部分 · 宏观全景', 'Part 1 · The Big Picture'),
    ('05-why-effect.html', '为什么是 Effect', 'Why Effect',
     '第二部分 · Effect 地基', 'Part 2 · Effect Foundations'),
    ('06-context-layer.html', 'Context.Service 与 Layer', 'Services & Layers',
     '第二部分 · Effect 地基', 'Part 2 · Effect Foundations'),
    ('07-concurrency-primitives.html', '并发原语', 'Concurrency primitives',
     '第二部分 · Effect 地基', 'Part 2 · Effect Foundations'),
    ('08-effect-toolbox.html', '项目里的 Effect 工具箱', 'The Effect toolbox',
     '第二部分 · Effect 地基', 'Part 2 · Effect Foundations'),
    ('09-server-overview.html', 'server 总览', 'The server, overview',
     '第三部分 · 客户端/服务器', 'Part 3 · Client/Server'),
    ('10-route-groups.html', '路由组与 handler', 'Route groups & handlers',
     '第三部分 · 客户端/服务器', 'Part 3 · Client/Server'),
    ('11-event-bus.html', 'SSE 事件总线', 'The SSE event bus',
     '第三部分 · 客户端/服务器', 'Part 3 · Client/Server'),
    ('12-sdk-generation.html', 'SDK 生成', 'Generating the SDK',
     '第三部分 · 客户端/服务器', 'Part 3 · Client/Server'),
    ('13-transports.html', '多客户端传输', 'Multi-client transports',
     '第三部分 · 客户端/服务器', 'Part 3 · Client/Server'),
    ('14-session-messages-parts.html', 'Session、消息与 part', 'Sessions, messages, parts',
     '第四部分 · Session 与 agent 循环', 'Part 4 · Session Core'),
    ('15-input-inbox.html', '事件溯源输入收件箱', 'The event-sourced inbox',
     '第四部分 · Session 与 agent 循环', 'Part 4 · Session Core'),
    ('16-run-coordinator.html', '运行协调器', 'The run coordinator',
     '第四部分 · Session 与 agent 循环', 'Part 4 · Session Core'),
    ('17-agent-loop.html', 'V2 agent 循环', 'The V2 agent loop',
     '第四部分 · Session 与 agent 循环', 'Part 4 · Session Core'),
    ('18-tool-calls-fiberset.html', '工具调用与 FiberSet', 'Tool calls & FiberSet',
     '第四部分 · Session 与 agent 循环', 'Part 4 · Session Core'),
    ('19-projected-history.html', '投影历史', 'Projected history',
     '第四部分 · Session 与 agent 循环', 'Part 4 · Session Core'),
    ('20-steps-errors.html', '有界步数与错误处理', 'Bounded steps & errors',
     '第四部分 · Session 与 agent 循环', 'Part 4 · Session Core'),
    ('21-system-context.html', 'System Context 总览', 'System Context overview',
     '第五部分 · Context Epoch 系统', 'Part 5 · Context System'),
    ('22-context-source.html', 'Context Source', 'Context Sources',
     '第五部分 · Context Epoch 系统', 'Part 5 · Context System'),
    ('23-context-registry.html', 'System Context Registry', 'The context registry',
     '第五部分 · Context Epoch 系统', 'Part 5 · Context System'),
    ('24-context-epoch.html', 'Context Epoch', 'The Context Epoch',
     '第五部分 · Context Epoch 系统', 'Part 5 · Context System'),
    ('25-mid-conversation.html', '会话中系统消息', 'Mid-conversation messages',
     '第五部分 · Context Epoch 系统', 'Part 5 · Context System'),
    ('26-builtin-sources.html', '内置 Context Sources', 'Built-in sources',
     '第五部分 · Context Epoch 系统', 'Part 5 · Context System'),
    ('27-agent-switch-epoch.html', 'Agent 切换与 Epoch 替换', 'Agent switch & epoch',
     '第五部分 · Context Epoch 系统', 'Part 5 · Context System'),
    ('28-llm-overview.html', 'LLM 层总览', 'The LLM layer',
     '第六部分 · LLM 协议层', 'Part 6 · LLM Layer'),
    ('29-protocol-adapters.html', '协议适配器', 'Protocol adapters',
     '第六部分 · LLM 协议层', 'Part 6 · LLM Layer'),
    ('30-anthropic-protocol.html', 'Anthropic Messages 协议', 'The Anthropic protocol',
     '第六部分 · LLM 协议层', 'Part 6 · LLM Layer'),
    ('31-openai-protocol.html', 'OpenAI Chat/Responses 协议', 'The OpenAI protocols',
     '第六部分 · LLM 协议层', 'Part 6 · LLM Layer'),
    ('32-gemini-bedrock.html', 'Gemini 与 Bedrock 协议', 'Gemini & Bedrock',
     '第六部分 · LLM 协议层', 'Part 6 · LLM Layer'),
    ('33-routing-transport.html', '路由与传输', 'Routing & transport',
     '第六部分 · LLM 协议层', 'Part 6 · LLM Layer'),
    ('34-streaming-cache.html', '流式事件与缓存', 'Streaming & caching',
     '第六部分 · LLM 协议层', 'Part 6 · LLM Layer'),
    ('35-model-resolution.html', '模型解析与 Copilot provider', 'Model resolution & Copilot',
     '第六部分 · LLM 协议层', 'Part 6 · LLM Layer'),
    ('36-tool-definition.html', '工具定义', 'Defining a tool',
     '第七部分 · 工具系统', 'Part 7 · Tool System'),
    ('37-tool-registry.html', '工具注册表', 'The tool registry',
     '第七部分 · 工具系统', 'Part 7 · Tool System'),
    ('38-file-tools.html', '文件工具', 'File tools',
     '第七部分 · 工具系统', 'Part 7 · Tool System'),
    ('39-search-exec-tools.html', '搜索与执行工具', 'Search & exec tools',
     '第七部分 · 工具系统', 'Part 7 · Tool System'),
    ('40-other-tools.html', '其他内置工具', 'Other built-in tools',
     '第七部分 · 工具系统', 'Part 7 · Tool System'),
    ('41-permissions.html', '权限系统', 'Permissions',
     '第七部分 · 工具系统', 'Part 7 · Tool System'),
    ('42-bounded-output.html', '有界工具输出', 'Bounded tool output',
     '第七部分 · 工具系统', 'Part 7 · Tool System'),
    ('43-skills.html', 'Skills 系统', 'The skills system',
     '第七部分 · 工具系统', 'Part 7 · Tool System'),
    ('44-config-loading.html', '配置加载', 'Loading config',
     '第八部分 · 配置·Agents·Provider', 'Part 8 · Config, Agents, Providers'),
    ('45-agents.html', 'Agents：build 与 plan', 'Agents: build & plan',
     '第八部分 · 配置·Agents·Provider', 'Part 8 · Config, Agents, Providers'),
    ('46-mcp.html', 'MCP 集成', 'MCP integration',
     '第八部分 · 配置·Agents·Provider', 'Part 8 · Config, Agents, Providers'),
    ('47-provider-plugins.html', 'Provider 插件定义', 'Provider plugins',
     '第八部分 · 配置·Agents·Provider', 'Part 8 · Config, Agents, Providers'),
    ('48-drizzle-sqlite.html', 'Drizzle 与 SQLite', 'Drizzle & SQLite',
     '第九部分 · 持久化', 'Part 9 · Persistence'),
    ('49-core-tables.html', '核心数据表', 'The core tables',
     '第九部分 · 持久化', 'Part 9 · Persistence'),
    ('50-v1-storage-migration.html', 'V1 存储与迁移', 'V1 storage & migration',
     '第九部分 · 持久化', 'Part 9 · Persistence'),
    ('51-compaction-snapshots.html', '压缩、摘要与快照', 'Compaction & snapshots',
     '第九部分 · 持久化', 'Part 9 · Persistence'),
    ('52-opentui.html', 'opentui 渲染器', 'The opentui renderer',
     '第十部分 · TUI', 'Part 10 · The TUI'),
    ('53-tui-structure.html', 'TUI 应用结构', 'TUI app structure',
     '第十部分 · TUI', 'Part 10 · The TUI'),
    ('54-events-to-store.html', '事件到 store', 'Events to store',
     '第十部分 · TUI', 'Part 10 · The TUI'),
    ('55-prompt-component.html', 'prompt 组件', 'The prompt component',
     '第十部分 · TUI', 'Part 10 · The TUI'),
    ('56-dialogs-scrollback.html', '对话框与 scrollback', 'Dialogs & scrollback',
     '第十部分 · TUI', 'Part 10 · The TUI'),
    ('57-plugin-system.html', '插件系统', 'The plugin system',
     '第十一部分 · 扩展与集成', 'Part 11 · Extensibility'),
    ('58-plugin-hooks.html', '插件 hooks 详解', 'Plugin hooks in depth',
     '第十一部分 · 扩展与集成', 'Part 11 · Extensibility'),
    ('59-lsp.html', 'LSP 集成', 'LSP integration',
     '第十一部分 · 扩展与集成', 'Part 11 · Extensibility'),
    ('60-pty-shell.html', 'PTY 与 shell', 'PTY & shell',
     '第十一部分 · 扩展与集成', 'Part 11 · Extensibility'),
    ('61-acp-location.html', 'ACP 与 Location 抽象', 'ACP & the Location model',
     '第十一部分 · 扩展与集成', 'Part 11 · Extensibility'),
    ('62-build-debug.html', '本地构建与调试', 'Build & debug',
     '第十二部分 · 实战与速查', 'Part 12 · Practice & Reference'),
    ('63-test-contribute.html', '测试与贡献', 'Test & contribute',
     '第十二部分 · 实战与速查', 'Part 12 · Practice & Reference'),
    ('64-glossary.html', '术语表与索引', 'Glossary & index',
     '第十二部分 · 实战与速查', 'Part 12 · Practice & Reference'),
]


def bi(zh, en):
    """Inline bilingual pair; only the active language is shown (CSS-controlled)."""
    return f'<span class="lang-zh">{zh}</span><span class="lang-en">{en}</span>'


INDEX_FILE = "index.html"

CSS = r"""
* { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --bg: #f6f7f9; --panel: #ffffff; --panel-2: #f0f2f5; --ink: #1d2129;
  --muted: #5b6470; --faint: #8a939f; --line: #e1e5ea;
  --accent: #c2630e; --accent-soft: #fbeede; --accent-ink: #8a4708;
  --blue: #2563eb; --blue-soft: #e7efff; --amber: #b4690e; --amber-soft: #fdf1dd;
  --purple: #7c3aed; --purple-soft: #f0e9ff; --red: #d23f3f; --red-soft: #fbe6e6;
  --code-bg: #0f172a; --code-ink: #e2e8f0; --code-line: #1e293b;
  --shadow: 0 1px 2px rgba(16,24,40,.06), 0 8px 24px rgba(16,24,40,.06);
  --radius: 14px;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0e1116; --panel: #161b22; --panel-2: #1c232c; --ink: #e6edf3;
    --muted: #9aa6b2; --faint: #6e7a86; --line: #2a323c;
    --accent: #e8923f; --accent-soft: #3a2410; --accent-ink: #f3b673;
    --blue: #6ea8fe; --blue-soft: #16243f; --amber: #e0a44a; --amber-soft: #33270f;
    --purple: #b794f6; --purple-soft: #271a40; --red: #f08080; --red-soft: #3a1a1a;
    --code-bg: #0a0f1a; --code-ink: #d8e2f0; --code-line: #14202f;
    --shadow: 0 1px 2px rgba(0,0,0,.4), 0 10px 30px rgba(0,0,0,.35);
  }
}
html { scroll-behavior: smooth; overflow-x: hidden; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC",
    "PingFang SC", "Microsoft YaHei", system-ui, sans-serif;
  background: var(--bg); color: var(--ink); line-height: 1.7;
  -webkit-font-smoothing: antialiased;
}
a { color: var(--accent); text-decoration: none; }
code, .mono { font-family: "SF Mono", "JetBrains Mono", "Fira Code", ui-monospace, Menlo, Consolas, monospace; overflow-wrap: break-word; }

/* ---- top progress bar ---- */
.topbar {
  position: sticky; top: 0; z-index: 50; background: var(--panel);
  border-bottom: 1px solid var(--line); backdrop-filter: blur(8px);
}
.topbar-inner {
  max-width: 960px; margin: 0 auto; padding: .7rem 1.25rem;
  display: flex; align-items: center; justify-content: space-between; gap: 1rem;
}
.topbar .home { font-size: .82rem; color: var(--muted); font-weight: 600; display:flex; gap:.5rem; align-items:center; }
.topbar .home b { color: var(--accent); }
.topbar .pill { font-size: .72rem; color: var(--muted); background: var(--panel-2);
  padding: .2rem .6rem; border-radius: 999px; border: 1px solid var(--line); white-space: nowrap; }
.progress { height: 3px; background: var(--panel-2); }
.progress > span { display: block; height: 100%; background: linear-gradient(90deg, var(--accent), var(--blue)); }

.wrap { max-width: 820px; margin: 0 auto; padding: 2.4rem 1.25rem 5rem; }

/* ---- hero ---- */
.hero { margin-bottom: 2rem; }
.hero .part { font-size: .76rem; letter-spacing: .08em; text-transform: uppercase;
  color: var(--accent); font-weight: 700; margin-bottom: .55rem; }
.hero h1 { font-size: 2.05rem; line-height: 1.2; letter-spacing: -.01em; font-weight: 750; }
.hero .lead { margin-top: .9rem; font-size: 1.06rem; color: var(--muted); }

h2 { font-size: 1.32rem; margin: 2.4rem 0 .9rem; letter-spacing: -.01em;
  display: flex; align-items: center; gap: .55rem; }
h2::before { content: ""; width: 4px; height: 1.05em; background: var(--accent); border-radius: 3px; display: inline-block; }
h3 { font-size: 1.05rem; margin: 1.4rem 0 .5rem; }
p { margin: .7rem 0; }
ul, ol { margin: .6rem 0 .6rem 1.3rem; }
li { margin: .3rem 0; }
strong { color: var(--ink); font-weight: 680; }
.inline { background: var(--panel-2); border: 1px solid var(--line); border-radius: 6px;
  padding: .08em .4em; font-size: .9em; color: var(--accent-ink); }

/* ---- callout cards ---- */
.card { border-radius: var(--radius); padding: 1.05rem 1.2rem; margin: 1.2rem 0;
  border: 1px solid var(--line); background: var(--panel); box-shadow: var(--shadow); }
.card .tag { font-size: .72rem; font-weight: 700; letter-spacing: .04em; text-transform: uppercase;
  display: inline-flex; align-items: center; gap: .4rem; margin-bottom: .5rem; }
.card.macro { border-left: 4px solid var(--blue); }
.card.macro .tag { color: var(--blue); }
.card.detail { border-left: 4px solid var(--purple); }
.card.detail .tag { color: var(--purple); }
.card.analogy { border-left: 4px solid var(--amber); background: var(--amber-soft); }
.card.analogy .tag { color: var(--amber); }
.card.key { border-left: 4px solid var(--accent); background: var(--accent-soft); }
.card.key .tag { color: var(--accent-ink); }
.card.warn { border-left: 4px solid var(--red); background: var(--red-soft); }
.card.warn .tag { color: var(--red); }
.card.spark { border-left: 4px solid #e0a000;
  background: linear-gradient(100deg, rgba(224,160,0,.12), transparent 70%); }
.card.spark .tag { color: #c98a00; }
@media (prefers-color-scheme: dark) { .card.spark .tag { color: #f0c050; } }

/* ---- code file callout ---- */
.codefile { margin: 1.2rem 0; border-radius: 12px; overflow: hidden; border: 1px solid var(--line);
  box-shadow: var(--shadow); }
.codefile .cf-head { display: flex; align-items: center; gap: .55rem; padding: .5rem .85rem;
  background: var(--panel-2); border-bottom: 1px solid var(--line); font-size: .8rem; }
.codefile .cf-head .dot { width: 9px; height: 9px; border-radius: 50%; background: var(--accent); flex-shrink:0; }
.codefile .cf-head .path { font-family: ui-monospace, monospace; color: var(--ink); font-weight: 600; }
.codefile .cf-head .ln { margin-left: auto; color: var(--faint); font-size: .72rem; }
.codefile pre { background: var(--code-bg); color: var(--code-ink); padding: .9rem 1rem;
  overflow-x: auto; font-size: .82rem; line-height: 1.6; }
.codefile pre .cm { color: #7d8aa3; }
.codefile pre .kw { color: #c792ea; }
.codefile pre .fn { color: #82aaff; }
.codefile pre .st { color: #c3e88d; }
.codefile pre .nb { color: #f78c6c; }

pre.code { background: var(--code-bg); color: var(--code-ink); padding: .9rem 1rem; border-radius: 12px;
  overflow-x: auto; font-size: .83rem; line-height: 1.6; margin: 1.1rem 0; box-shadow: var(--shadow); }
pre.code .cm { color: #7d8aa3; } pre.code .kw { color: #c792ea; }
pre.code .fn { color: #82aaff; } pre.code .st { color: #c3e88d; } pre.code .nb { color: #f78c6c; }

/* ---- collapsible accordion (details/summary) ---- */
.accordion { border: 1px solid var(--line); border-radius: 12px; background: var(--panel);
  margin: .7rem 0; box-shadow: var(--shadow); overflow: hidden; }
.accordion > summary { cursor: pointer; padding: .85rem 1.1rem; font-weight: 650; font-size: .96rem;
  list-style: none; display: flex; align-items: center; gap: .6rem; user-select: none; }
.accordion > summary::-webkit-details-marker { display: none; }
.accordion > summary::after { content: "▶"; font-size: .68rem; color: var(--accent);
  margin-left: auto; transition: transform .15s ease; }
.accordion[open] > summary::after { transform: rotate(90deg); }
.accordion > summary:hover { background: var(--panel-2); }
.accordion[open] > summary { border-bottom: 1px solid var(--line); }
.accordion .badge-num { background: var(--accent-soft); color: var(--accent-ink);
  width: 1.6rem; height: 1.6rem; border-radius: 7px; display: inline-flex; align-items: center;
  justify-content: center; font-size: .82rem; font-weight: 700; flex-shrink: 0; }
.accordion .hint { font-size: .72rem; color: var(--faint); font-weight: 400; }
.acc-body { padding: .9rem 1.1rem 1.1rem; }
.acc-intro { color: var(--muted); font-size: .9rem; margin: .2rem 0 .4rem; }
.qa { margin: 1rem 0; }
.qa:first-child { margin-top: .3rem; }
.qa .q { font-weight: 680; font-size: .9rem; display: flex; gap: .45rem; align-items: center; margin-bottom: .3rem; }
.qa .a { color: var(--muted); font-size: .9rem; }
.qa .a strong { color: var(--ink); }
.qa pre.code { margin: .5rem 0 0; font-size: .78rem; }

/* ---- flow diagram ---- */
.flow { display: flex; align-items: stretch; gap: 0; flex-wrap: wrap; margin: 1.3rem 0;
  background: var(--panel); border: 1px solid var(--line); border-radius: var(--radius);
  padding: 1.2rem 1rem; box-shadow: var(--shadow); }
.flow .node { flex: 1 1 0; min-width: 110px; text-align: center; padding: .7rem .5rem;
  border-radius: 10px; background: var(--panel-2); border: 1px solid var(--line); }
.flow .node .nt { font-weight: 700; font-size: .92rem; }
.flow .node .nd { font-size: .76rem; color: var(--muted); margin-top: .2rem; }
.flow .node.hl { background: var(--accent-soft); border-color: var(--accent); }
.flow .arrow { align-self: center; color: var(--faint); font-size: 1.3rem; padding: 0 .35rem; }

/* vertical flow */
.vflow { margin: 1.3rem 0; }
.vflow .step { display: flex; gap: .9rem; position: relative; padding-bottom: 1.1rem; }
.vflow .step:not(:last-child)::before { content:""; position:absolute; left: 15px; top: 34px; bottom: -2px;
  width: 2px; background: var(--line); }
.vflow .num { width: 32px; height: 32px; border-radius: 50%; background: var(--accent); color: #fff;
  display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: .85rem; flex-shrink: 0; z-index:1; }
.vflow .sc h4 { margin: .25rem 0 .2rem; font-size: 1rem; }
.vflow .sc p { margin: .15rem 0; font-size: .92rem; color: var(--muted); }
.vflow .sc .mono { font-size: .8rem; color: var(--accent-ink); }

/* layered architecture */
.layers { margin: 1.3rem 0; display: flex; flex-direction: column; gap: .55rem; }
.layer { border-radius: 12px; padding: .85rem 1.1rem; border: 1px solid var(--line); background: var(--panel);
  box-shadow: var(--shadow); }
.layer .lh { display: flex; align-items: center; gap: .6rem; }
.layer .lh .badge { font-size: .7rem; font-weight: 700; padding: .12rem .5rem; border-radius: 999px; }
.layer .lh .name { font-weight: 700; font-family: ui-monospace, monospace; }
.layer .ld { font-size: .85rem; color: var(--muted); margin-top: .35rem; }
.layer.l-core { border-left: 4px solid var(--accent); } .layer.l-core .badge { background: var(--accent-soft); color: var(--accent-ink); }
.layer.l-main { border-left: 4px solid var(--blue); } .layer.l-main .badge { background: var(--blue-soft); color: var(--blue); }
.layer.l-part { border-left: 4px solid var(--purple); } .layer.l-part .badge { background: var(--purple-soft); color: var(--purple); }
.layer.l-app { border-left: 4px solid var(--amber); } .layer.l-app .badge { background: var(--amber-soft); color: var(--amber); }

/* two-column compare */
.cols { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1.2rem 0; }
@media (max-width: 640px) { .cols { grid-template-columns: 1fr; } }
.col { background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 1rem 1.1rem; box-shadow: var(--shadow); min-width: 0; }
.col h4 { margin: 0 0 .4rem; font-size: .95rem; }

table.t { width: 100%; border-collapse: collapse; margin: 1.1rem 0; font-size: .9rem;
  background: var(--panel); border-radius: 12px; overflow: hidden; box-shadow: var(--shadow); }
table.t th, table.t td { padding: .6rem .8rem; text-align: left; border-bottom: 1px solid var(--line); }
table.t th { background: var(--panel-2); font-size: .8rem; letter-spacing: .02em; }
table.t tr:last-child td { border-bottom: none; }
table.t td.mono, table.t td .mono { font-family: ui-monospace, monospace; font-size: .82rem; color: var(--accent-ink); }
@media (max-width: 640px) {
  /* Wide multi-column tables: scroll within their own box instead of
     forcing page-level horizontal overflow (which clipped right columns). */
  table.t { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
  table.t th, table.t td { padding: .5rem .6rem; }
}
.selftest { margin: 2.2rem 0 0; border-top: 2px dashed var(--line); padding-top: 1.2rem; }
.selftest > h2 { margin-top: .2rem; }
.quiz { background: var(--panel); border: 1px solid var(--line); border-left: 4px solid var(--blue);
  border-radius: 12px; padding: .9rem 1.1rem; margin: 1rem 0; box-shadow: var(--shadow); }
.quiz .qn { font-weight: 650; }
.quiz ol.opts { list-style: upper-alpha; margin: .55rem 0 .6rem 1.5rem; padding: 0; }
.quiz ol.opts li { margin: .3rem 0; padding-left: .15rem; }
.quiz details.accordion { margin: .5rem 0 0; }
.selftest code { font-family: ui-monospace, monospace; font-size: .9em; color: var(--accent-ink);
  background: var(--accent-soft); padding: 0 .28em; border-radius: 4px; }

/* footer nav */
.footnav { display: flex; justify-content: space-between; gap: 1rem; margin-top: 3rem;
  padding-top: 1.4rem; border-top: 1px solid var(--line); }
.footnav a { flex: 1; padding: .85rem 1.1rem; border-radius: 12px; border: 1px solid var(--line);
  background: var(--panel); box-shadow: var(--shadow); transition: .15s; }
.footnav a:hover { border-color: var(--accent); transform: translateY(-1px); }
.footnav a.next { text-align: right; }
.footnav .dir { font-size: .72rem; color: var(--faint); text-transform: uppercase; letter-spacing: .05em; }
.footnav .ttl { font-weight: 700; color: var(--ink); margin-top: .15rem; }
.footnav a.disabled { opacity: .35; pointer-events: none; }

/* index page */
.toc { display: grid; gap: .7rem; margin-top: 1.6rem; }
.toc-part { font-size: .78rem; font-weight: 700; letter-spacing: .05em; text-transform: uppercase;
  color: var(--accent); margin: 1.4rem 0 .2rem; }
.toc a { display: flex; align-items: center; gap: .9rem; padding: .85rem 1.05rem; border-radius: 12px;
  background: var(--panel); border: 1px solid var(--line); box-shadow: var(--shadow); transition: .15s; }
.toc a:hover { border-color: var(--accent); transform: translateX(3px); }
.toc .n { width: 30px; height: 30px; border-radius: 8px; background: var(--accent-soft); color: var(--accent-ink);
  display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: .85rem; flex-shrink: 0; }
.toc .tt { font-weight: 650; color: var(--ink); }
.toc .ts { font-size: .8rem; color: var(--muted); margin-left: auto; text-align: right; }
.toc-search { position: relative; margin: 1.6rem 0 -.4rem; }
.toc-search input { width: 100%; box-sizing: border-box; padding: .75rem 2.8rem .75rem 1rem;
  border-radius: 12px; border: 1px solid var(--line); background: var(--panel); color: var(--ink);
  font-size: .98rem; box-shadow: var(--shadow); }
.toc-search input:focus { outline: none; border-color: var(--accent); }
.toc-search .qcount { position: absolute; right: 1rem; top: 50%; transform: translateY(-50%);
  color: var(--faint); font-size: .8rem; pointer-events: none; }
.toc a.hide, .toc .toc-part.hide { display: none; }
.toc-empty { display: none; color: var(--muted); padding: 1rem; text-align: center; }
.toc-empty.show { display: block; }
.hero.index h1 { font-size: 2.3rem; }
.legend { display:flex; gap:1.2rem; flex-wrap:wrap; margin-top:1rem; font-size:.8rem; color:var(--muted); }
.legend span { display:flex; align-items:center; gap:.4rem; }
.legend i { width:12px; height:12px; border-radius:3px; display:inline-block; }
.pdf-btn { display:inline-flex; align-items:center; gap:.4rem; padding:.55rem 1.1rem;
  background:var(--accent); color:#fff; border-radius:10px; font-size:.9rem; font-weight:650;
  box-shadow:var(--shadow); transition:.15s; }
.pdf-btn:hover { background:var(--accent-ink); transform:translateY(-1px); }

/* ---- bilingual language switch ----
   Contract: <html> must carry data-lang="zh" (default) or "en".
   page()/index_page() hard-code data-lang="zh"; LANG_BOOT may switch to "en". */
html[data-lang="en"] .lang-zh { display: none !important; }
html[data-lang="zh"] .lang-en { display: none !important; }
.langtoggle { font-size:.72rem; font-weight:700; color:var(--accent-ink);
  background:var(--accent-soft); border:1px solid var(--accent); border-radius:999px;
  padding:.22rem .7rem; cursor:pointer; line-height:1.4; white-space:nowrap; }
.langtoggle:hover { background:var(--accent); color:#fff; }

/* ---- schematic: cell strips (token sequences / quant blocks / KV columns) ---- */
.cellgroup { margin: 1.2rem 0; background: var(--panel); border: 1px solid var(--line);
  border-radius: var(--radius); padding: 1rem 1.1rem; box-shadow: var(--shadow); }
.cellgroup .cg-cap { font-size: .82rem; color: var(--muted); margin-bottom: .55rem; }
.cellgroup .cg-cap b { color: var(--ink); }
.cells { display: flex; flex-wrap: wrap; gap: .35rem; align-items: center; }
.cells + .cells { margin-top: .5rem; }
.cell { min-width: 2.1rem; padding: .38rem .5rem; text-align: center; border-radius: 8px;
  background: var(--panel-2); border: 1px solid var(--line); font-size: .78rem;
  font-family: ui-monospace, monospace; white-space: nowrap; }
.cell.scale { background: var(--amber-soft); border-color: var(--amber); color: var(--amber); font-weight: 700; }
.cell.hl    { background: var(--accent-soft); border-color: var(--accent); color: var(--accent-ink); font-weight: 700; }
.cell.q     { background: var(--blue-soft); border-color: var(--blue); color: var(--blue); }
.cell.dim   { opacity: .45; }
.cells .lab { font-size: .76rem; color: var(--faint); padding: 0 .35rem; }
.cells .sep { color: var(--faint); padding: 0 .1rem; }

/* ---- schematic: timeline lanes (prefill vs decode, step-by-step) ---- */
.timeline { margin: 1.2rem 0; display: flex; flex-direction: column; gap: .5rem;
  background: var(--panel); border: 1px solid var(--line); border-radius: var(--radius);
  padding: 1rem 1.1rem; box-shadow: var(--shadow); }
.timeline .lane { display: flex; align-items: center; gap: .5rem; flex-wrap: wrap; }
.timeline .lane-label { min-width: 6rem; font-size: .8rem; font-weight: 700; color: var(--muted); }
.timeline .tslot { padding: .4rem .6rem; border-radius: 8px; background: var(--panel-2);
  border: 1px solid var(--line); font-size: .78rem; text-align: center; font-family: ui-monospace, monospace; }
.timeline .tslot.span { flex: 1; min-width: 8rem; background: var(--blue-soft); border-color: var(--blue);
  color: var(--blue); font-weight: 700; }
.timeline .tslot.now { background: var(--accent-soft); border-color: var(--accent); color: var(--accent-ink); font-weight: 700; }

/* ---- worked-example trace: one concrete input, stepped through ---- */
.trace { margin: 1.3rem 0; background: var(--panel); border: 1px solid var(--line);
  border-left: 4px solid var(--accent); border-radius: var(--radius); padding: 1rem 1.1rem; box-shadow: var(--shadow); }
.trace .tcap { font-size: .82rem; color: var(--muted); margin-bottom: .7rem; }
.trace .tcap b { color: var(--accent-ink); }
.trace .stations { display: flex; align-items: stretch; gap: 0; flex-wrap: wrap; }
.trace .stn { flex: 1 1 0; min-width: 116px; border: 1px solid var(--line); border-radius: 10px;
  padding: .55rem; background: var(--bg); }
.trace .stn h5 { margin: 0 0 .45rem; font-size: .8rem; color: var(--ink); }
.trace .cellrow { display: flex; gap: .3rem; align-items: center; flex-wrap: wrap; }
.trace .vc { min-width: 2.1rem; padding: .32rem .45rem; text-align: center; border-radius: 7px;
  background: var(--panel-2); border: 1px solid var(--line); font: 600 .76rem ui-monospace, monospace; white-space: nowrap; }
.trace .vc.hot  { background: var(--accent-soft); border-color: var(--accent); color: var(--accent-ink); }
.trace .vc.blue { background: var(--blue-soft); border-color: var(--blue); color: var(--blue); }
.trace .vc.dim  { opacity: .42; }
.trace .tlab { font-size: .68rem; color: var(--faint); margin-top: .35rem; }
.trace .op { align-self: center; color: var(--accent); font: 700 .72rem ui-monospace, monospace;
  padding: 0 .5rem; text-align: center; white-space: nowrap; }
.trace svg { max-width: 100%; height: auto; display: block; margin: .3rem auto; }
@media (max-width: 640px) { .trace .stations { flex-direction: column; } .trace .op { padding: .3rem 0; } }
"""

SEARCH_JS = """
(function(){
  var q=document.getElementById('q'); if(!q) return;
  var toc=document.querySelector('.toc');
  var empty=document.getElementById('tocempty');
  var count=document.getElementById('qcount');
  var links=[].slice.call(toc.querySelectorAll('a'));
  var heads=[].slice.call(toc.querySelectorAll('.toc-part'));
  links.forEach(function(a){ a.setAttribute('data-s',(a.textContent||'').toLowerCase()); });
  function run(){
    var t=(q.value||'').toLowerCase().trim(), n=0;
    links.forEach(function(a){
      var hit=!t||a.getAttribute('data-s').indexOf(t)>=0;
      a.classList.toggle('hide',!hit); if(hit)n++;
    });
    heads.forEach(function(h){
      var el=h.nextElementSibling, any=false;
      while(el && !el.classList.contains('toc-part')){
        if(el.tagName==='A' && !el.classList.contains('hide')){any=true;break;}
        el=el.nextElementSibling;
      }
      h.classList.toggle('hide',!any);
    });
    empty.classList.toggle('show', !!t && n===0);
    count.textContent = t ? String(n) : '';
  }
  q.addEventListener('input',run);
})();
"""

LANG_JS = """
function lcvgSetLang(l){
  l=(l==='en')?'en':'zh';
  var d=document.documentElement;
  d.dataset.lang=l; d.lang=(l==='en'?'en':'zh-CN');
  try{localStorage.setItem('lcvg-lang',l);}catch(e){}
}
function lcvgToggleLang(){
  lcvgSetLang(document.documentElement.dataset.lang==='en'?'zh':'en');
}
"""

# Runs in <head> before first paint to avoid a flash of the wrong language.
LANG_BOOT = (
    "<script>try{var l=localStorage.getItem('lcvg-lang');"
    "if(l==='en'){document.documentElement.dataset.lang='en';"
    "document.documentElement.lang='en';}}catch(e){}</script>"
)


def page(filename, content, home_href="../index.html"):
    """Wrap one lesson's bilingual content in the full HTML shell.

    ``content`` is a dict ``{"zh": html, "en": html}``. Both are emitted; CSS
    shows only the active language. Navigation uses plain relative ``href``
    links so the site works via file:// and any static server (lessons share
    one directory; home defaults to ``../index.html``).
    """
    idx = next(i for i, p in enumerate(PAGES) if p[0] == filename)
    fname, title_zh, title_en, part_zh, part_en = PAGES[idx]
    total = len(PAGES)
    pct = int((idx + 1) / total * 100)
    home = home_href

    if idx > 0:
        p = PAGES[idx - 1]
        prev_link = (
            f'<a class="prev" href="{p[0]}"><div class="dir">{bi("← 上一课", "← Prev")}</div>'
            f'<div class="ttl">{bi(esc(p[1]), esc(p[2]))}</div></a>'
        )
    else:
        prev_link = (
            f'<a class="prev" href="{home}"><div class="dir">{bi("← 返回", "← Back")}</div>'
            f'<div class="ttl">{bi("目录", "Contents")}</div></a>'
        )
    if idx + 1 < total:
        p = PAGES[idx + 1]
        next_link = (
            f'<a class="next" href="{p[0]}"><div class="dir">{bi("下一课 →", "Next →")}</div>'
            f'<div class="ttl">{bi(esc(p[1]), esc(p[2]))}</div></a>'
        )
    else:
        next_link = (
            f'<a class="next" href="{home}"><div class="dir">{bi("完成 →", "Done →")}</div>'
            f'<div class="ttl">{bi("返回目录", "Back to index")}</div></a>'
        )

    title_tag = f"{idx+1:02d} · {title_zh} / {title_en} - opencode 图解指南"
    desc = f"{part_zh}｜{title_zh} - opencode 图解指南（中英双语，配真实源码对应、折叠深挖与设计亮点）"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN" data-lang="zh"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{LANG_BOOT}
<title>{esc(title_tag)}</title>
{head_meta(title_tag, desc, og_type="article")}
<style>{CSS}</style>
</head><body>
<div class="topbar">
  <div class="topbar-inner">
    <a class="home" href="{home}">🤖 <b class="lang-zh">opencode 图解指南</b><b class="lang-en">opencode Visual Guide</b></a>
    <span class="pill">{bi(esc(part_zh), esc(part_en))}</span>
    <span class="pill">{idx+1:02d} / {total:02d}</span>
    <button class="langtoggle" onclick="lcvgToggleLang()" aria-label="switch language"><span class="lang-zh">EN</span><span class="lang-en">中</span></button>
  </div>
  <div class="progress"><span style="width:{pct}%"></span></div>
</div>
<div class="wrap">
  <div class="hero">
    <div class="part">{bi(esc(part_zh), esc(part_en))}</div>
    <h1><span class="lang-zh">{esc(title_zh)}</span><span class="lang-en">{esc(title_en)}</span></h1>
  </div>
  <div class="lang-zh">{content["zh"]}</div>
  <div class="lang-en">{content["en"]}</div>
  <div class="footnav">{prev_link}{next_link}</div>
</div>
<script>{LANG_JS}</script>
</body></html>"""
    return html


# Per-lesson TOC subtitle: filename -> (zh, en). Missing entries render blank.
SUBTITLES = {}


def index_page(lesson_prefix="lessons/"):
    """Build the bilingual index (table of contents). Always relative links."""
    order = []   # ordered list of (part_zh, part_en)
    groups = {}  # part_zh -> [(num, fname, title_zh, title_en), ...]
    for i, (fname, tz, te, pz, pe) in enumerate(PAGES):
        if pz not in groups:
            groups[pz] = []
            order.append((pz, pe))
        groups[pz].append((i + 1, fname, tz, te))

    blocks = []
    for pz, pe in order:
        blocks.append(f'<div class="toc-part">{bi(esc(pz), esc(pe))}</div>')
        for num, fname, tz, te in groups[pz]:
            sz, se = SUBTITLES.get(fname, ("", ""))
            blocks.append(
                f'<a href="{lesson_prefix}{fname}"><span class="n">{num:02d}</span>'
                f'<span class="tt"><span class="lang-zh">{esc(tz)}</span>'
                f'<span class="lang-en">{esc(te)}</span></span>'
                f'<span class="ts"><span class="lang-zh">{esc(sz)}</span>'
                f'<span class="lang-en">{esc(se)}</span></span></a>'
            )
    toc = "\n".join(blocks)
    total = len(PAGES)
    nparts = len(order)

    title_tag = "opencode 图解指南 · 从零理解整个项目 / opencode Visual Guide"
    desc = ("从零理解整个 opencode 项目源码的中英双语图解指南：Effect 地基、客户端/服务器、Session Core 与 Context Epoch、LLM 协议层、工具系统、TUI 与扩展，每课配真实源码对应与设计亮点。")

    return f"""<!DOCTYPE html>
<html lang="zh-CN" data-lang="zh"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{LANG_BOOT}
<title>{esc(title_tag)}</title>
{head_meta(title_tag, desc, og_type="website")}
<style>{CSS}</style>
</head><body>
<div class="topbar">
  <div class="topbar-inner">
    <span class="home">🤖 <b class="lang-zh">opencode 图解指南</b><b class="lang-en">opencode Visual Guide</b></span>
    <span class="pill"><span class="lang-zh">共 {total} 课 · {nparts} 个部分</span><span class="lang-en">{total} lesson{'' if total == 1 else 's'} · {nparts} part{'' if nparts == 1 else 's'}</span></span>
    <button class="langtoggle" onclick="lcvgToggleLang()" aria-label="switch language"><span class="lang-zh">EN</span><span class="lang-en">中</span></button>
  </div>
  <div class="progress"><span style="width:100%"></span></div>
</div>
<div class="wrap">
  <div class="hero index">
    <div class="part">{bi("从零开始 · 面向完全新手", "From scratch · for complete beginners")}</div>
    <h1><span class="lang-zh">用图解理解整个 opencode 项目</span><span class="lang-en">Understand the whole opencode project, visually</span></h1>
    <p class="lead"><span class="lang-zh">这套指南带你<strong>自底向上</strong>读懂 opencode 的源码：先打 <strong>Effect 函数式地基</strong>，再看<strong>客户端/服务器骨架</strong>，然后深入 <strong>V2 Session Core</strong>（agent 循环、Context Epoch）、<strong>自研 LLM 协议层</strong>与<strong>工具系统</strong>，最后覆盖存储、TUI、扩展与实战。每课配真实源码对应、图解与设计亮点。</span>
    <span class="lang-en">A bottom-up tour of the opencode source: start with the <strong>Effect foundations</strong>, then the <strong>client/server skeleton</strong>, dive into the <strong>V2 Session Core</strong> (agent loop, Context Epoch), the <strong>in-house LLM protocol layer</strong> and <strong>tool system</strong>, then storage, the TUI, extensibility and practice. Every lesson maps to real source, with diagrams and design insights.</span></p>
    <div class="legend">
      <span><i style="background:var(--blue)"></i>{bi("宏观理解", "Big picture")}</span>
      <span><i style="background:var(--purple)"></i>{bi("细节 / 源码", "Details / source")}</span>
      <span><i style="background:var(--amber)"></i>{bi("生活类比", "Analogy")}</span>
      <span><i style="background:var(--accent)"></i>{bi("关键要点", "Key points")}</span>
    </div>
    <p style="margin:.8rem 0 0;color:var(--faint);font-size:.8rem">{bi("📌 对照 opencode 仓库真实源码核实 · 源码引用以“文件 + 符号名”为主（行号随上游更新而变）", "📌 Verified against the real opencode source; references cite file + symbol (line numbers drift upstream)")}</p>
  </div>
  <div class="toc-search">
    <input id="q" type="search" placeholder="🔎 搜索课程 / Search lessons" autocomplete="off" aria-label="search">
    <span class="qcount" id="qcount"></span>
  </div>
  <div class="toc">{toc}</div>
  <div class="toc-empty" id="tocempty">{bi("没有匹配的课程，换个关键词试试。", "No matching lessons, try another keyword.")}</div>
</div>
<script>{LANG_JS}</script>
<script>{SEARCH_JS}</script>
</body></html>"""
