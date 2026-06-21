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
