"""Per-lesson bilingual self-test (自测题): design-insight multiple-choice + open prompts.

Schema per lesson::

    "NN-file.html": {
        "mcq": [
            {
                "q":   {"zh": "...", "en": "..."},
                "opts": [{"zh": "...", "en": "..."}, ...],
                "answer": 1,                      # 0-based index into opts (as written)
                "why": {"zh": "...", "en": "..."},
            },
        ],
        "open": [{"zh": "...", "en": "..."}],
    }

``render(fname, lang)`` turns it into HTML that build.py appends to the bottom of
each language's lesson body. Options are deterministically shuffled per question
(same permutation for zh and en, so the correct letter matches across languages).

Quiz text (q/opts/why) is raw HTML in a text context (like the lesson body):
write literal ``<``/``&`` as ``&lt;``/``&amp;`` (or wrap code in ``<code>``).
"""
import hashlib

_HEAD = {"zh": "🧪 自测 · 想一想为什么这么设计", "en": "🧪 Self-test - think about the design"}
_SEE = {"zh": "看答案与解析", "en": "Show answer &amp; explanation"}
_CLICK = {"zh": "点击展开", "en": "click to expand"}
_ANS = {"zh": "答案：", "en": "Answer: "}
_SEP = {"zh": "。", "en": ". "}
_OPEN = {
    "zh": "💭 发散思考（没有标准答案，动手或动脑想想）",
    "en": "💭 Open questions (no single right answer - just think or try)",
}


def _shuffle(opts, answer, seed):
    """Deterministically permute opts (stable across builds); return
    (new_opts, new_answer_index) so the correct option lands in a varied slot."""
    order = sorted(
        range(len(opts)),
        key=lambda i: hashlib.md5(f"{seed}:{i}".encode("utf-8")).hexdigest(),
    )
    return [opts[i] for i in order], order.index(answer)


QUIZZES = {
    "01-what-is-opencode.html": {
        "mcq": [
            {
                "q": {
                    "zh": "opencode 把 agent 逻辑、会话、工具、provider 都收进一个常驻 server，客户端只负责收发与渲染。这个“客户端/服务器”切分最主要换来了什么？",
                    "en": "opencode puts agent logic, sessions, tools, and providers into one resident server; clients only send and render. What does this client/server split mainly buy?",
                },
                "opts": [
                    {"zh": "让大模型的补全速度更快", "en": "Faster LLM completion"},
                    {"zh": "一个内核多种前端复用、会话服务端持久化、可 headless 自动化", "en": "One core reused by many front-ends, server-side session persistence, headless automation"},
                    {"zh": "彻底不需要大模型", "en": "Removing the need for an LLM entirely"},
                    {"zh": "把 agent 绑定到某个特定编辑器", "en": "Binding the agent to one specific editor"},
                ],
                "answer": 1,
                "why": {
                    "zh": "server 拥有一切、client 只是视图：于是 TUI/web/桌面/Slack/ACP 共用一个内核，会话存在 SQLite 不丢，还能用 serve 模式脚本化。",
                    "en": "The server owns everything and the client is just a view: TUI/web/desktop/Slack/ACP share one core, sessions persist in SQLite, and serve mode enables scripting.",
                },
            },
            {
                "q": {
                    "zh": "课里反复强调的“agent 循环”具体指什么？",
                    "en": "What exactly is the “agent loop” the lesson keeps emphasizing?",
                },
                "opts": [
                    {"zh": "server 反复地“调大模型 → 执行工具 → 把结果喂回”，直到模型不再调工具", "en": "The server repeatedly “calls the LLM, runs tools, feeds results back” until the model stops calling tools"},
                    {"zh": "大模型一次性写出全部代码", "en": "The LLM writes all the code in one shot"},
                    {"zh": "用户手动重复同样的操作", "en": "The user manually repeats the same action"},
                    {"zh": "编译器内部的优化循环", "en": "An optimization loop inside the compiler"},
                ],
                "answer": 0,
                "why": {
                    "zh": "大模型一次只“想一步”，由 server 替它执行工具再喂回上下文，循环推进——这正是 opencode 的心脏，第 17 课逐跳拆解。",
                    "en": "The LLM thinks one step at a time; the server runs tools on its behalf and feeds context back, advancing the loop — opencode's heart, dissected in Lesson 17.",
                },
            },
            {
                "q": {
                    "zh": "关于 V1 与 V2，下面哪个说法是对的？",
                    "en": "Which statement about V1 and V2 is correct?",
                },
                "opts": [
                    {"zh": "V2 是 packages/core（纯 Effect + SQLite），V1 是 packages/opencode/src/session（AI-SDK + 文件存储）", "en": "V2 is packages/core (pure Effect + SQLite); V1 is packages/opencode/src/session (AI-SDK + file storage)"},
                    {"zh": "V1 用 Effect + SQLite，V2 用 AI-SDK + 文件存储", "en": "V1 uses Effect + SQLite; V2 uses AI-SDK + file storage"},
                    {"zh": "V1 和 V2 是两个不同的开源项目", "en": "V1 and V2 are two different open-source projects"},
                    {"zh": "V2 已经完全取代 V1，源码里看不到 V1", "en": "V2 has fully replaced V1; V1 is gone from the source"},
                ],
                "answer": 0,
                "why": {
                    "zh": "代码正从 V1（AI-SDK、磁盘 JSON）迁移到 V2 Session Core（纯 Effect、SQLite），两套并存，V1 仍是当前默认路径。",
                    "en": "The code is migrating from V1 (AI-SDK, on-disk JSON) to V2 Session Core (pure Effect, SQLite); both coexist, and V1 is still the default path today.",
                },
            },
        ],
        "open": [
            {
                "zh": "假设你要给 opencode 加一个全新的前端（比如一个 VSCode 插件）。按它的客户端/服务器架构，你需要做什么、又不需要重做什么？",
                "en": "Suppose you add a brand-new front-end to opencode (say a VSCode extension). Given its client/server architecture, what would you need to build, and what would you not need to reimplement?",
            },
            {
                "zh": "课里说几乎所有状态变化都先落成事件。想一想：这种事件优先的设计，对多个客户端看同一个会话、以及出错后重放，分别带来什么好处？",
                "en": "The lesson says nearly every state change first becomes an event. Consider: what does this event-first design give you for multiple clients watching one session, and for replay after a failure?",
            },
        ],
    },
    "02-project-map.html": {
        "mcq": [
            {
                "q": {
                    "zh": "读 opencode 这个 24 个包的仓库时，课里为什么说先分清“CORE / 周边”是最省力的一把筛子？",
                    "en": "When reading opencode's 24-package repo, why does the lesson call the “CORE vs periphery” split the cheapest filter?",
                },
                "opts": [
                    {"zh": "因为周边的包都是废弃代码，可以直接删掉", "en": "Because the periphery is all dead code you can delete"},
                    {"zh": "因为只有 CORE 那 6 个包在运行时 agent 路径上执行，搞懂 agent 九成答案都在那里", "en": "Because only the 6 CORE packages run on the runtime agent path, where nine-tenths of how the agent works lives"},
                    {"zh": "因为 CORE 的包名都更短，好记", "en": "Because CORE package names are shorter and easier to remember"},
                    {"zh": "因为周边的包都没法编译通过", "en": "Because the periphery packages don't compile"},
                ],
                "answer": 1,
                "why": {
                    "zh": "CORE（opencode·core·llm·server·sdk·plugin）是你每跑一次 prompt 真正执行的路径；客户端、云端、基础库都围着它转，第一次读源码盯住这 6 个就不会迷路。",
                    "en": "CORE (opencode·core·llm·server·sdk·plugin) is the path that actually runs on every prompt; clients, cloud, and infra all orbit it, so locking onto those 6 keeps you from getting lost.",
                },
            },
            {
                "q": {
                    "zh": "课里画的依赖方向是“客户端 → sdk → server → core(+llm) → provider”。关于这条线，下面哪个说法对？",
                    "en": "The lesson draws dependencies flowing “clients → sdk → server → core(+llm) → provider.” Which statement about that line is correct?",
                },
                "opts": [
                    {"zh": "客户端直接 import core，绕开 server", "en": "Clients import core directly, bypassing the server"},
                    {"zh": "客户端经“生成的 sdk”调 server，再由 server 落到 core 与 llm；sdk 是在构建时反向从 server 的 OpenAPI 生成的", "en": "Clients call the server via the “generated sdk,” which lands on core and llm; the sdk is generated backward from the server's OpenAPI at build time"},
                    {"zh": "provider 是依赖的起点，反过来去调客户端", "en": "The provider is the start of the chain and calls back into clients"},
                    {"zh": "sdk 是手写的，和 server 没有关系", "en": "The sdk is hand-written and unrelated to the server"},
                ],
                "answer": 1,
                "why": {
                    "zh": "这正是上一课“客户端/服务器”边界在包结构上的样子：sdk 是从 server 的 OpenAPI 生成的那道缝，运行时依赖单向流向 provider。",
                    "en": "This is the previous lesson's client/server boundary in package form: the sdk is the seam generated from the server's OpenAPI, and runtime dependencies flow one way toward the provider.",
                },
            },
            {
                "q": {
                    "zh": "关于这个仓库里的“二进制”，下面哪个说法准确？",
                    "en": "Which statement about the repo's “binaries” is accurate?",
                },
                "opts": [
                    {"zh": "整个仓库只有一个二进制，就是 opencode", "en": "The repo ships only one binary, opencode"},
                    {"zh": "packages/opencode 是当前主用的 opencode（yargs、偏 V1）；packages/cli 是另一个叫 lildax 的二进制，打包 core+server+tui+sdk，是正在成形的 V2 入口", "en": "packages/opencode is today's main opencode (yargs, V1-leaning); packages/cli is a second binary called lildax bundling core+server+tui+sdk — the emerging V2 entry point"},
                    {"zh": "packages/cli 才是 V1，packages/opencode 是 V2", "en": "packages/cli is the V1 one; packages/opencode is V2"},
                    {"zh": "两个二进制属于两个完全独立的开源项目", "en": "The two binaries belong to two entirely separate open-source projects"},
                ],
                "answer": 1,
                "why": {
                    "zh": "opencode 同时是核心包、server 宿主、还扛着 V1；而 packages/cli（lildax）用 Effect 命令框架把 V2 内核打包成新入口——两者正骑在 V1→V2 迁移线上。",
                    "en": "opencode is at once a core package, the server host, and the V1 carrier; packages/cli (lildax) uses an Effect command framework to bundle the V2 kernel into a new entry — both straddle the V1→V2 migration.",
                },
            },
        ],
        "open": [
            {
                "zh": "假设你要给 LLM 协议层接一个全新的 provider。按这张地图，你大概率只会改动哪个（哪些）包？又有哪些包完全不用碰？为什么？",
                "en": "Suppose you wire a brand-new provider into the LLM protocol layer. Given this map, which package(s) would you most likely touch, and which would you not touch at all — and why?",
            },
            {
                "zh": "console、slack、enterprise 这些云端包，本地跑一次 prompt 时一个都不会启动。那么把它们和 CORE 放进同一个 monorepo，到底图什么好处？",
                "en": "Cloud packages like console, slack, and enterprise never start when you run a prompt locally. So what is actually gained by keeping them in the same monorepo as CORE?",
            },
        ],
    },
}

def render(fname, lang):
    """Return the self-test HTML block for ``fname`` in ``lang`` ('' if none)."""
    data = QUIZZES.get(fname)
    if not data or not (data.get("mcq") or data.get("open")):
        return ""
    out = ['<div class="selftest">', f'<h2>{_HEAD[lang]}</h2>']
    for i, item in enumerate(data.get("mcq", []), 1):
        shuffled, ans = _shuffle(item["opts"], item["answer"], f"{fname}:{i}")
        opts = "\n".join(f"    <li>{o[lang]}</li>" for o in shuffled)
        letter = chr(65 + ans)
        out.append(
            f'<div class="quiz">\n'
            f'  <div class="qn">{i}. {item["q"][lang]}</div>\n'
            f'  <ol class="opts">\n{opts}\n  </ol>\n'
            f'  <details class="accordion">\n'
            f'    <summary>{_SEE[lang]} <span class="hint">{_CLICK[lang]}</span></summary>\n'
            f'    <div class="acc-body"><div class="qa"><div class="a">'
            f'<strong>{_ANS[lang]}{letter}</strong>{_SEP[lang]}{item["why"][lang]}'
            f"</div></div></div>\n"
            f"  </details>\n"
            f"</div>"
        )
    opens = data.get("open", [])
    if opens:
        lis = "\n".join(f"    <li>{o[lang]}</li>" for o in opens)
        out.append(
            '<div class="card spark">\n'
            f'  <div class="tag">{_OPEN[lang]}</div>\n'
            f"  <ul>\n{lis}\n  </ul>\n"
            "</div>"
        )
    out.append("</div>")
    return "\n".join(out)


def _validate():
    """Fail fast on authoring mistakes in QUIZZES (clear message names the lesson)."""
    for fname, data in QUIZZES.items():
        for qi, item in enumerate(data.get("mcq", []), 1):
            opts = item["opts"]
            if not (0 <= item["answer"] < len(opts)):
                raise ValueError(
                    f"quizzes[{fname!r}] Q{qi}: answer {item['answer']} out of range 0..{len(opts) - 1}"
                )
            for o in opts:
                if not ({"zh", "en"} <= o.keys()):
                    raise ValueError(f"quizzes[{fname!r}] Q{qi}: an option is missing zh/en")
            if not ({"zh", "en"} <= item["q"].keys() and {"zh", "en"} <= item["why"].keys()):
                raise ValueError(f"quizzes[{fname!r}] Q{qi}: q/why missing zh/en")
        for oi, o in enumerate(data.get("open", []), 1):
            if not ({"zh", "en"} <= o.keys()):
                raise ValueError(f"quizzes[{fname!r}] open{oi}: missing zh/en")


_validate()
