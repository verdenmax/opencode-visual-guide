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
    "03-request-lifecycle.html": {
        "mcq": [
            {
                "q": {"zh": "富终端 TUI 是怎么和 server 通信的？", "en": "How does the rich TUI talk to the server?"},
                "opts": [
                    {"zh": "通过本地 HTTP 网络请求", "en": "Via a local HTTP network request"},
                    {"zh": "通过进程内 RPC worker，把 SDK 的 fetch 换成 RPC，零网络", "en": "Via an in-process RPC worker that swaps the SDK fetch for RPC, zero network"},
                    {"zh": "直接读写 SQLite 数据库", "en": "By reading and writing SQLite directly"},
                    {"zh": "通过 stdin/stdout 管道", "en": "Through stdin/stdout pipes"},
                ],
                "answer": 1,
                "why": {"zh": "cli/cmd/tui.ts 的 createWorkerFetch 把 SDK 的 fetch 换成对 Worker 的 RPC；同一套 SDK 接口，只有 serve 模式才走真 HTTP。", "en": "createWorkerFetch in cli/cmd/tui.ts swaps the SDK fetch for RPC to a Worker; the same SDK interface only uses real HTTP in serve mode."},
            },
            {
                "q": {"zh": "agent 循环的护栏 MAX_STEPS 是多少、为什么要有它？", "en": "What is the agent loop guardrail MAX_STEPS, and why have it?"},
                "opts": [
                    {"zh": "25，防止模型无限调用工具、原地打转", "en": "25, to stop the model from calling tools forever and spinning in place"},
                    {"zh": "10，用来限制一次能调几个工具", "en": "10, to limit how many tools can be called at once"},
                    {"zh": "100，用来限制总 token 数", "en": "100, to cap total tokens"},
                    {"zh": "没有上限，一直转到模型停", "en": "No cap; it loops until the model stops"},
                ],
                "answer": 0,
                "why": {"zh": "runner/llm.ts 里 MAX_STEPS = 25；超过就抛 StepLimitExceeded，是防失控的硬护栏。", "en": "runner/llm.ts sets MAX_STEPS = 25; exceeding it throws StepLimitExceeded — a hard guardrail against runaway loops."},
            },
            {
                "q": {"zh": "为什么每轮结束要重新加载投影历史，而不是把工具结果拼到内存数组上？", "en": "Why reload projected history each round instead of splicing tool results onto an in-memory array?"},
                "opts": [
                    {"zh": "因为历史是持久化的事实来源，重投影保证崩溃重启或被插队后仍看到最准状态", "en": "Because history is the persisted source of truth; re-projecting guarantees the most accurate state even after a crash/restart or an interrupting input"},
                    {"zh": "纯粹为了省内存", "en": "Purely to save memory"},
                    {"zh": "因为大模型协议强制要求", "en": "Because the LLM protocol mandates it"},
                    {"zh": "因为这样更快", "en": "Because it is faster"},
                ],
                "answer": 0,
                "why": {"zh": "V2 的克制：不依赖内存临时状态，一切以持久化为准、可随时重建——崩溃或中途插话都不会让模型看到过时状态。", "en": "V2's restraint: never rely on temporary in-memory state; everything defers to persistence and is rebuildable — neither a crash nor a mid-flight interruption leaves the model with stale state."},
            },
        ],
        "open": [
            {"zh": "课里说请求向下收敛、结果向上发散。挑一个你感兴趣的子系统（比如工具执行或事件总线），说说它在下行还是上行、落在哪一层？", "en": "The lesson says requests converge downward and results diverge upward. Pick a subsystem you care about (e.g. tool execution or the event bus) and say whether it is on the way down or up, and which layer."},
            {"zh": "富 TUI 用进程内 RPC worker 换来了什么好处？如果改用真正的网络 server（serve 模式），哪些地方会不一样、又有哪些代价？", "en": "What does the in-process RPC worker buy the rich TUI? If you switched to a real network server (serve mode), what would differ, and at what cost?"},
        ],
    },
    "04-v1-vs-v2.html": {
        "mcq": [
            {
                "q": {"zh": "怎么一眼判断一段 session 代码属于 V1 还是 V2？", "en": "How do you tell at a glance whether a piece of session code is V1 or V2?"},
                "opts": [
                    {"zh": "看文件路径：opencode/src/session 是 V1，core/src/session 是 V2", "en": "By path: opencode/src/session is V1, core/src/session is V2"},
                    {"zh": "看文件有多少行", "en": "By how many lines the file has"},
                    {"zh": "看文件头部的注释声明", "en": "By a comment banner at the top of the file"},
                    {"zh": "看 git 提交时间", "en": "By the git commit date"},
                ],
                "answer": 0,
                "why": {"zh": "最省事的判断法就是看路径：opencode/src/session=V1（旧），core/src/session=V2（新）。", "en": "The easiest test is the path: opencode/src/session = V1 (old), core/src/session = V2 (new)."},
            },
            {
                "q": {"zh": "V2 相比 V1，在持久化上的根本变化是什么？", "en": "What is V2's fundamental change in persistence versus V1?"},
                "opts": [
                    {"zh": "从磁盘 JSON 文件，换成 Drizzle + SQLite", "en": "From on-disk JSON files to Drizzle + SQLite"},
                    {"zh": "从 SQLite 换回 JSON 文件", "en": "From SQLite back to JSON files"},
                    {"zh": "完全不持久化，只放内存", "en": "No persistence at all, memory only"},
                    {"zh": "改用 Redis", "en": "Switched to Redis"},
                ],
                "answer": 0,
                "why": {"zh": "V1 把会话存成磁盘 JSON 文件；V2 用 Drizzle ORM + SQLite（还带 bun/node 双后端），配合事件溯源做到崩溃可恢复。", "en": "V1 stores sessions as on-disk JSON; V2 uses Drizzle ORM + SQLite (dual bun/node backends), paired with event sourcing for crash recovery."},
            },
            {
                "q": {"zh": "下面哪项能力是 V2 独有、V1 架构撑不起来的？", "en": "Which capability is V2-only, unsupported by V1's architecture?"},
                "opts": [
                    {"zh": "System Context / Context Epoch（上下文纪元）", "en": "System Context / Context Epoch"},
                    {"zh": "调用大模型", "en": "Calling the LLM"},
                    {"zh": "执行 edit/bash 等工具", "en": "Running tools like edit/bash"},
                    {"zh": "读写项目里的文件", "en": "Reading and writing project files"},
                ],
                "answer": 0,
                "why": {"zh": "调模型、跑工具、读写文件 V1 也能做；但 Context Epoch 这套独特的上下文设计只存在于 V2，是迁移要长出的新能力（第五部分）。", "en": "Calling the model, running tools, file I/O all exist in V1; but the Context Epoch design is V2-only — a new capability the migration grows (Part 5)."},
            },
        ],
        "open": [
            {"zh": "V2 把 V1 的千行巨石拆成一堆小协作者。结合你自己的开发经验，说一个这种拆分在“改代码、加测试”时带来的具体好处。", "en": "V2 splits V1's thousand-line monoliths into small collaborators. From your own experience, name one concrete benefit of that split when changing code or adding tests."},
            {"zh": "迁移是渐进的、两套并存。如果你要给 opencode 修一个 bug，你会怎么先判断这个 bug 该在 V1 还是 V2 里改？", "en": "The migration is gradual and both coexist. If you had to fix a bug in opencode, how would you first decide whether to fix it in V1 or V2?"},
        ],
    },
    "05-why-effect.html": {
        "mcq": [
            {
                "q": {"zh": "Effect 区别于普通代码的核心一招是什么？", "en": "What is Effect's core move that sets it apart from plain code?"},
                "opts": [
                    {"zh": "先把计算描述成一个值，组合好，最后才在边缘运行一次", "en": "Describe the computation as a value first, compose it, then run once at the edge"},
                    {"zh": "让代码运行得更快", "en": "Make the code run faster"},
                    {"zh": "自动帮你写测试", "en": "Write your tests for you automatically"},
                    {"zh": "完全替代 TypeScript 的类型系统", "en": "Fully replace TypeScript's type system"},
                ],
                "answer": 0,
                "why": {"zh": "普通函数一调用就跑；Effect 写出的是一个值（说明书），可先 retry/race/注入依赖地组合，最后在最外层 runPromise 一次。", "en": "A plain function runs on call; an Effect is a value (a spec) you can compose (retry/race/inject) first, then runPromise once at the outermost edge."},
            },
            {
                "q": {"zh": "在 Effect&lt;A, E, R&gt; 里，E 和 R 分别代表什么？", "en": "In Effect&lt;A, E, R&gt;, what do E and R represent?"},
                "opts": [
                    {"zh": "E = 类型化错误，R = 需要的依赖/服务", "en": "E = typed errors, R = required deps/services"},
                    {"zh": "E = 成功值，R = 返回类型", "en": "E = success value, R = return type"},
                    {"zh": "E = 环境，R = 结果", "en": "E = environment, R = result"},
                    {"zh": "E = 事件，R = 请求", "en": "E = event, R = request"},
                ],
                "answer": 0,
                "why": {"zh": "A 是成功值、E 是可能的类型化错误（编译器逼你处理）、R 是需要的依赖（可注入替换）。E 和 R 正是普通写法藏起来的两样。", "en": "A is the success value, E the possible typed errors (the compiler forces handling), R the required deps (injectable). E and R are exactly what plain code hides."},
            },
            {
                "q": {"zh": "课里指出普通 try/catch 在大型系统里最致命的软肋是什么？", "en": "What does the lesson call plain try/catch's most fatal weakness in a large system?"},
                "opts": [
                    {"zh": "catch 到的 e 是 unknown——错误类型和依赖都不在类型里，全靠你脑子记、忘了编译器也不提醒", "en": "The caught e is unknown — error types and deps aren't in the type; you track them by memory and the compiler won't remind you"},
                    {"zh": "它运行得太慢", "en": "It runs too slowly"},
                    {"zh": "它不能嵌套使用", "en": "It cannot be nested"},
                    {"zh": "它不支持 async 函数", "en": "It does not support async functions"},
                ],
                "answer": 0,
                "why": {"zh": "关键信息（会怎样失败、依赖了谁）没写进类型，变成隐形负担；忘了处理编译器也不报错，bug 最爱藏这。", "en": "Crucial info (how it fails, what it depends on) isn't in the type, becoming an invisible burden; forget to handle it and the compiler stays silent — where bugs hide."},
            },
        ],
        "open": [
            {"zh": "课里说“先有痛点，才有 Effect”。从副作用/错误/并发/依赖这四难题里挑一个，说说 Effect 的哪个机制专门对付它。", "en": "The lesson says “the pain comes first, then Effect”. Pick one of the four (side effects / errors / concurrency / dependencies) and say which Effect mechanism targets it."},
            {"zh": "把依赖写进类型的 R 槽，对你日常写单元测试具体有什么好处？对比一下普通 import 全局单例的写法。", "en": "Putting dependencies in the type's R slot — what concrete benefit does that give your day-to-day unit testing, versus importing a global singleton?"},
        ],
    },
    "06-context-layer.html": {
        "mcq": [
            {
                "q": {"zh": "Service 和 Layer 各自负责什么？", "en": "What do Service and Layer each handle?"},
                "opts": [
                    {"zh": "Service 声明一个能力插槽（契约），Layer 把真实现接到这个槽上", "en": "Service declares a capability slot (contract); Layer wires a real implementation into that slot"},
                    {"zh": "Service 是实现，Layer 是接口", "en": "Service is the implementation, Layer is the interface"},
                    {"zh": "两个都只是接口，没有实现", "en": "Both are just interfaces, no implementation"},
                    {"zh": "Service 用于测试，Layer 用于生产", "en": "Service is for tests, Layer is for production"},
                ],
                "answer": 0,
                "why": {"zh": "Service 是带全局标签的契约（插座），Layer = Layer.effect(Service, make) 把真实现接上去（布线）。消费方只认 Service，换实现就退化成换 Layer。", "en": "Service is a globally-tagged contract (the socket); Layer = Layer.effect(Service, make) wires the real impl in. Consumers know only Service, so swapping impl becomes swapping a Layer."},
            },
            {
                "q": {"zh": "在 Effect.gen 里 yield* 一个 Service，会发生什么？", "en": "What happens when you yield* a Service inside Effect.gen?"},
                "opts": [
                    {"zh": "在该计算的类型 R 里欠下一笔依赖，要由某个 Layer 在最外层还清", "en": "It owes a dependency in the computation's R, to be repaid by some Layer at the outermost layer"},
                    {"zh": "立刻 new 出一个新实例", "en": "It immediately news up a fresh instance"},
                    {"zh": "直接打开数据库连接", "en": "It opens a database connection directly"},
                    {"zh": "立刻抛出一个错误", "en": "It immediately throws an error"},
                ],
                "answer": 0,
                "why": {"zh": "yield* Service = 在 R 上欠债；提供对应 Layer = 还债。编译器盯着账本，依赖没还清就不让运行。", "en": "yield* Service = owe a debt in R; providing the matching Layer = repay it. The compiler watches the ledger and won't run until R is repaid."},
            },
            {
                "q": {"zh": "makeRuntime 背后的 memoMap 解决了什么问题？", "en": "What problem does the memoMap behind makeRuntime solve?"},
                "opts": [
                    {"zh": "同一个 Layer 被多处依赖时，只构造一次、大家共享同一个实例", "en": "When one Layer is depended on in many places, it's built once and everyone shares the one instance"},
                    {"zh": "给依赖加密", "en": "It encrypts dependencies"},
                    {"zh": "给请求限速", "en": "It rate-limits requests"},
                    {"zh": "记录日志", "en": "It writes logs"},
                ],
                "answer": 0,
                "why": {"zh": "若 Agent/Session/Tool 各自 new 一个 Database 就会有三份、状态还可能对不上；memoMap 保证整棵依赖树里 Database 只活一份。", "en": "If Agent/Session/Tool each new'd a Database you'd get three with possibly mismatched state; memoMap guarantees one Database across the whole dep tree."},
            },
        ],
        "open": [
            {"zh": "为什么 opencode 要把 Service（契约）和 Layer（实现）拆成两个东西，而不是揉成一个类？这对“写测试”和“架构往后演进”分别有什么好处？", "en": "Why does opencode split Service (contract) and Layer (impl) into two things rather than one class? What does that buy for “writing tests” and for “evolving the architecture”?"},
            {"zh": "课里说“是 Effect 的依赖模型塑造了 V2 的模块形状”。结合第 4 课的“巨石 vs 小协作者”，谈谈你的理解。", "en": "The lesson says “Effect's dependency model shapes V2's module form”. Relate this to Lesson 4's “boulders vs small collaborators” in your own words."},
        ],
    },
    "07-concurrency-primitives.html": {
        "mcq": [
            {
                "q": {"zh": "Fiber 相比普通 Promise，最关键的多出来的能力是什么？", "en": "What is the key extra ability a Fiber has over a plain Promise?"},
                "opts": [
                    {"zh": "可以被有序地 interrupt（中断并清理资源），而普通 Promise 一旦发起就无法取消", "en": "It can be interrupted in an orderly way (cancel + clean up), while a plain Promise cannot be cancelled once started"},
                    {"zh": "它本身跑得更快", "en": "It simply runs faster"},
                    {"zh": "它会自动重试失败的任务", "en": "It auto-retries failed tasks"},
                    {"zh": "它占用更少内存", "en": "It uses less memory"},
                ],
                "answer": 0,
                "why": {"zh": "Fiber 是一个正在跑的 Effect 的句柄，可 join 等结果、可 interrupt 有序停下并清理。普通 Promise 无法取消——这对随时可能被用户打断的 agent 是刚需。", "en": "A Fiber is a handle to a running Effect: join for the result, interrupt to stop in order and clean up. A plain Promise cannot cancel — a must for an interruptible agent."},
            },
            {
                "q": {"zh": "agent 被用户打断时，runner 调用 FiberSet.clear(toolFibers) 做了什么？", "en": "When the user interrupts, what does the runner's FiberSet.clear(toolFibers) do?"},
                "opts": [
                    {"zh": "把整组正在跑的工具一次性中断，并触发它们各自的资源清理", "en": "Interrupt the whole running tool group at once and trigger each one's resource cleanup"},
                    {"zh": "清空日志文件", "en": "Clear the log files"},
                    {"zh": "重启整个 server", "en": "Restart the whole server"},
                    {"zh": "把当前进度存盘", "en": "Save the current progress to disk"},
                ],
                "answer": 0,
                "why": {"zh": "结构化并发保证开了多少就能收回多少：clear 把整组 Fiber 召回，避免出现“用户喊停了、某工具还在偷偷写文件”这种野任务。", "en": "Structured concurrency guarantees you reel back all you launched: clear recalls the whole Fiber group, avoiding a wild task still writing a file after the user stopped."},
            },
            {
                "q": {"zh": "为什么“记录结果、再发出事件”这样的关键区要包在 uninterruptibleMask 里？", "en": "Why wrap a critical region like record-then-emit in uninterruptibleMask?"},
                "opts": [
                    {"zh": "保证这类必须成对完成的操作不被半路打断，避免“记了却没通知”的不一致", "en": "To guarantee such paired operations are not interrupted midway, avoiding recorded-but-not-announced inconsistency"},
                    {"zh": "让它跑得更快", "en": "To make it run faster"},
                    {"zh": "禁止任何并发", "en": "To forbid all concurrency"},
                    {"zh": "给数据加密", "en": "To encrypt the data"},
                ],
                "answer": 0,
                "why": {"zh": "默认可中断很灵敏，但成对操作中途被打断会留下不一致；uninterruptibleMask 把那一小块圈成原子，必要时用 restore 再开可中断小窗。", "en": "Default interruptibility is responsive, but a paired op interrupted midway leaves inconsistency; uninterruptibleMask makes that small region atomic, with restore to reopen an interruptible window if needed."},
            },
        ],
        "open": [
            {"zh": "课里把结构化并发比作“消灭 goto”。说说“开了多少就能收回多少”对一个随时可被打断的 agent，为什么是正确性问题、而不只是性能问题。", "en": "The lesson likens structured concurrency to “killing goto”. Explain why “reel back all you launched” is a correctness issue (not just performance) for an interruptible agent."},
            {"zh": "对照表里，Promise.all 和 FiberSet 拉开差距的是哪两行？结合你实际用 AI agent 的体验，说说这两点为什么重要。", "en": "In the comparison table, which two rows separate Promise.all from FiberSet? From your own experience using an AI agent, say why those two matter."},
        ],
    },
    "08-effect-toolbox.html": {
        "mcq": [
            {
                "q": {"zh": "packages/core/src/effect/ 这个目录是什么？", "en": "What is the packages/core/src/effect/ directory?"},
                "opts": [
                    {"zh": "opencode 在 Effect 之上自建的小工具箱，把高频模式固化成趁手件", "en": "opencode's own small toolbox on top of Effect, crystallizing high-frequency patterns into handy parts"},
                    {"zh": "Effect 框架本身的源码", "en": "The source code of the Effect framework itself"},
                    {"zh": "存放单元测试的目录", "en": "A directory holding unit tests"},
                    {"zh": "项目的配置文件目录", "en": "The project's config directory"},
                ],
                "answer": 0,
                "why": {"zh": "这些小工具不改 Effect 的玩法，而是把项目里反复出现的模式（命名、去重、排队、省样板）做成现成件，让重复的活写得对、读得顺。", "en": "These tools don't change how Effect works; they turn recurring project patterns (naming, dedup, queuing, less boilerplate) into ready parts so repetitive work reads cleanly and runs correctly."},
            },
            {
                "q": {"zh": "Effect.fn(\"Domain.method\")(function*(){...}) 主要带来什么？", "en": "What does Effect.fn(\"Domain.method\")(function*(){...}) mainly bring?"},
                "opts": [
                    {"zh": "给这段 effect 命名，带来可观测性——出错/追踪时调用链里带着名字", "en": "It names the effect, giving observability — it appears named in the call chain on error/trace"},
                    {"zh": "让这段 effect 跑得更快", "en": "It makes the effect run faster"},
                    {"zh": "自动重试失败的 effect", "en": "It auto-retries a failed effect"},
                    {"zh": "给这段 effect 自动加锁", "en": "It automatically locks the effect"},
                ],
                "answer": 0,
                "why": {"zh": "命名是近乎零负担的可观测性：包进 Effect.fn 就有了轨迹；core 里 277 处命名，排查跨服务调用链时一眼可循。内部 helper 用 fnUntraced。", "en": "Naming is near-zero-cost observability: wrap in Effect.fn and you get a trail; core's 277 named spots make cross-service chains easy to follow. Internal helpers use fnUntraced."},
            },
            {
                "q": {"zh": "KeyedMutex 的核心特点是什么？", "en": "What is KeyedMutex's core characteristic?"},
                "opts": [
                    {"zh": "同一个 key 上的操作串行，不同 key 之间并行", "en": "Operations under the same key are serial; different keys run in parallel"},
                    {"zh": "全局一把大锁，锁住一切", "en": "One global lock over everything"},
                    {"zh": "什么都不锁", "en": "It locks nothing"},
                    {"zh": "只能用来锁数据库", "en": "It can only lock the database"},
                ],
                "answer": 0,
                "why": {"zh": "按 key 精确排队：以 session ID 为 key，同一会话的处理串成一条线、不打架，不同会话照样满速并行——既保正确又不牺牲并发。", "en": "Precise per-key queuing: with session ID as key, one session's processing is serialized and won't clash, while different sessions run at full concurrency — correctness without sacrificing parallelism."},
            },
        ],
        "open": [
            {"zh": "memoMap 只有一行代码，却解决了什么隐患？为什么“同一个服务全进程只造一份”对正确性很重要？", "en": "memoMap is one line, yet what hazard does it remove? Why is “one instance of a service per process” important for correctness?"},
            {"zh": "课里说这些小工具是“护栏”，让“正确成为默认”。结合你自己的项目，举一个你也想为团队做成“现成件”的高频动作。", "en": "The lesson calls these tools “guardrails” that make “correct the default”. From your own project, name one high-frequency action you'd also want to turn into a “ready part” for your team."},
        ],
    },
    "09-server-overview.html": {
        "mcq": [
            {
                "q": {"zh": "opencode 的 server 是用什么搭的？", "en": "What is opencode's server built on?"},
                "opts": [
                    {"zh": "Effect 的 HttpApi——先用类型声明整套 API 的形状，不是 Hono/Express", "en": "Effect's HttpApi — declare the whole API's shape in types first; not Hono/Express"},
                    {"zh": "Hono", "en": "Hono"},
                    {"zh": "Express", "en": "Express"},
                    {"zh": "用原生 http 模块手写路由", "en": "Hand-rolled routes on the raw http module"},
                ],
                "answer": 0,
                "why": {"zh": "server 架在 effect/unstable/httpapi 的 HttpApi 上：把每个端点的输入/输出/错误写进类型，编译器守契约，机器还能据此自动生成 SDK。", "en": "The server is built on HttpApi from effect/unstable/httpapi: each endpoint's input/output/error in the type, the compiler guards the contract, and a machine auto-generates the SDK from it."},
            },
            {
                "q": {"zh": "为什么 server 对外只是一个 (request) =&gt; Response 的 webHandler 很重要？", "en": "Why does it matter that the server is outwardly just one (request) =&gt; Response webHandler?"},
                "opts": [
                    {"zh": "因为它如此标准纯粹，所以能既架在网络服务器上、又塞进进程内 worker 直接调——一个 handler、两种传输", "en": "Because it's so standard and pure, it runs on a network server and can also be called inside an in-process worker — one handler, two transports"},
                    {"zh": "为了给请求加密", "en": "To encrypt requests"},
                    {"zh": "为了限制请求速率", "en": "To rate-limit requests"},
                    {"zh": "没有特别的原因", "en": "For no particular reason"},
                ],
                "answer": 0,
                "why": {"zh": "正因为 handler 没有对真实网络的硬依赖，富 TUI 才能用进程内 RPC 直接调它（第 3、13 课），实现零网络通信。", "en": "Because the handler has no hard dependency on a real network, the rich TUI can call it via in-process RPC (Lessons 3, 13) for zero-network communication."},
            },
            {
                "q": {"zh": "OpenApi.fromApi(PublicApi) 这一行带来的最大价值是什么？", "en": "What is the biggest value of the OpenApi.fromApi(PublicApi) line?"},
                "opts": [
                    {"zh": "API 自己描述自己→生成 OpenAPI 规范→自动生成各端 SDK，客户端类型永远和 server 对齐", "en": "The API describes itself → an OpenAPI spec → auto-generated SDKs, so client types always align with the server"},
                    {"zh": "让请求跑得更快", "en": "Makes requests run faster"},
                    {"zh": "自动压缩响应体", "en": "Auto-compresses responses"},
                    {"zh": "记录访问日志", "en": "Writes access logs"},
                ],
                "answer": 0,
                "why": {"zh": "因为 API 是结构化的类型，机器能读懂并生成规范与 SDK；API 一改、SDK 重生，所有客户端类型立刻同步，杜绝“前端拿过期接口”。", "en": "Because the API is a structured type, a machine reads it to generate the spec and SDK; change the API and the SDK regenerates, syncing all client types and killing stale-interface mismatches."},
            },
        ],
        "open": [
            {"zh": "课里说 HttpApi 比 Hono 多了“先声明形状”的繁琐，却值得。结合 opencode 要同时喂养 TUI/网页/桌面/Slack 多个客户端，说说这点繁琐换来了什么。", "en": "The lesson says HttpApi's extra “declare the shape first” tedium is worth it. Given opencode feeds TUI/web/desktop/Slack at once, what does that tedium buy?"},
            {"zh": "20 个路由组的名字本身就是一张 opencode 能力地图。挑其中 3 个组，猜一猜它们各自大概提供什么能力。", "en": "The 20 route-group names are themselves a map of opencode's abilities. Pick 3 groups and guess what each roughly provides."},
        ],
    },
    "10-route-groups.html": {
        "mcq": [
            {
                "q": {"zh": "opencode 里一个 API 端点的「组（group）」负责什么？", "en": "What does an API endpoint's \"group\" handle in opencode?"},
                "opts": [
                    {"zh": "声明契约——端点的名字、参数、返回、可能的错误，纯类型，不含实现", "en": "Declares the contract — the endpoint's name, params, return, possible errors; pure types, no implementation"},
                    {"zh": "查询数据库", "en": "Querying the database"},
                    {"zh": "渲染前端页面", "en": "Rendering frontend pages"},
                    {"zh": "管理 TCP 连接", "en": "Managing TCP connections"},
                ],
                "answer": 0,
                "why": {"zh": "组（groups/*.ts）全是类型声明：每个端点要什么、给什么、怎么错。正因为它纯、机器可读，才能据此自动生成 SDK。干活的是 handler。", "en": "Groups (groups/*.ts) are all type declarations: what each endpoint wants, gives, how it errors. Because they're pure and machine-readable, the SDK is auto-generated from them. The handler does the work."},
            },
            {
                "q": {"zh": "为什么说「理想的 handler 应该很薄」？", "en": "Why is \"an ideal handler should be thin\" the goal?"},
                "opts": [
                    {"zh": "因为输入已被组的类型校验，handler 只需把干净输入接到 core 服务；逻辑沉到 core 才能被多种传输共享", "en": "Input is already validated by the group's types, so the handler just wires clean input to core; logic sunk into core can be shared by many transports"},
                    {"zh": "因为薄的代码运行更快", "en": "Because thin code runs faster"},
                    {"zh": "因为 TypeScript 要求函数不能超过 10 行", "en": "Because TypeScript caps functions at 10 lines"},
                    {"zh": "因为薄 handler 不需要测试", "en": "Because thin handlers need no tests"},
                ],
                "answer": 0,
                "why": {"zh": "handler 胖起来=本该住 core 的逻辑漏到了 HTTP 层，结果只有走 HTTP 才能触发，第 13 课的进程内 RPC 等入口都享受不到。薄是有意的架构纪律。", "en": "A fat handler means logic that belongs in core leaked into HTTP, so it only fires over HTTP — Lesson 13's in-process RPC and other entries miss it. Thinness is deliberate discipline."},
            },
            {
                "q": {"zh": "错误中间件（middleware/error.ts）的行为是？", "en": "How does the error middleware (middleware/error.ts) behave?"},
                "opts": [
                    {"zh": "放行有类型、已声明的失败走正路；只兜底意料之外的裸崩溃，包成带 ref 编号的 500，真相进日志", "en": "Lets typed, declared failures take the main road; only catches unforeseen bare crashes, wrapping them into a 500 with a ref id and logging the truth"},
                    {"zh": "把所有异常都变成 500", "en": "Turns every exception into a 500"},
                    {"zh": "把所有错误都返回给客户端的完整堆栈", "en": "Returns the full stack of every error to the client"},
                    {"zh": "忽略所有错误", "en": "Ignores all errors"},
                ],
                "answer": 0,
                "why": {"zh": "「真相进日志、编号给客户端」：对外不泄露堆栈、只给一个 ref；运维拿 ref 去日志搜出完整因果。有类型的错误照常走声明过的路径。", "en": "“Truth into the log, an id to the client”: no stack leaked outward, just a ref; ops greps the ref for the full chain. Typed errors still take their declared path."},
            },
        ],
        "open": [
            {"zh": "课里把中间件比作「洋葱」而非「流水线」。用这个比喻解释：为什么压缩、补 CORS 头总发生在 handler 跑完之后的回程上，而鉴权却在最外层？", "en": "The lesson likens middleware to an “onion” not a “pipeline.” Use it to explain why compression and CORS headers happen on the return trip after the handler, while auth is outermost."},
            {"zh": "课里说 SDK 能在任何 handler 写好之前就生成。结合「契约先行」，说说这对一个同时供养 TUI/网页/桌面/Slack 的项目意味着什么。", "en": "The lesson says the SDK can be generated before any handler exists. With “contract-first” in mind, what does this mean for a project feeding TUI/web/desktop/Slack at once?"},
        ],
    },
    "11-event-bus.html": {
        "mcq": [
            {
                "q": {"zh": "opencode 用什么技术做服务器→客户端的实时推送？", "en": "What does opencode use for server→client real-time push?"},
                "opts": [
                    {"zh": "SSE——一个永不结束的 HTTP GET，响应体持续写入文本事件", "en": "SSE — an HTTP GET that never ends, continuously writing text events into the body"},
                    {"zh": "客户端每秒轮询一次", "en": "The client polls once per second"},
                    {"zh": "WebSocket 双向通道", "en": "A WebSocket bidirectional channel"},
                    {"zh": "gRPC 流", "en": "A gRPC stream"},
                ],
                "answer": 0,
                "why": {"zh": "event 组只有一个端点 subscribe，success 的 contentType 是 text/event-stream。SSE 就是 HTTP，所以路由组/中间件/鉴权全自动复用，且浏览器原生支持、断线自动重连。", "en": "The event group has one endpoint, subscribe, with success contentType text/event-stream. SSE is HTTP, so route groups/middleware/auth all auto-reuse, and browsers natively support it with auto-reconnect."},
            },
            {
                "q": {"zh": "为什么 handler 要「提前（eager）」登记事件监听器？", "en": "Why must the handler register the event listener \"eagerly\"?"},
                "opts": [
                    {"zh": "堵住「开始响应」与「登记监听」之间的缝隙，让订阅那一刻起的事件绝不丢失", "en": "To seal the gap between \"start responding\" and \"register listener,\" so no event is lost from the moment of subscription"},
                    {"zh": "为了让连接建立得更快", "en": "To make the connection establish faster"},
                    {"zh": "为了节省内存", "en": "To save memory"},
                    {"zh": "因为 Effect 强制要求", "en": "Because Effect mandates it"},
                ],
                "answer": 0,
                "why": {"zh": "若先发响应再登记，这两步之间发生的事件会永远漏掉。提前登记 + 无界队列蓄水，保证从订阅第一刻起事件只进队列、绝不丢失。", "en": "If you respond first then register, events between the two steps are lost forever. Eager registration + an unbounded queue guarantee events only enter the queue, never dropped, from the first moment."},
            },
            {
                "q": {"zh": "每 10 秒发一个 server.heartbeat 的主要目的是？", "en": "What's the main purpose of sending a server.heartbeat every 10 seconds?"},
                "opts": [
                    {"zh": "防止中间的代理/负载均衡把「一段时间没动静」的连接当死链掐掉", "en": "Prevent intermediary proxies/load balancers from cutting a quiet connection as a dead link"},
                    {"zh": "测量网络延迟", "en": "To measure network latency"},
                    {"zh": "同步客户端时钟", "en": "To sync the client clock"},
                    {"zh": "触发垃圾回收", "en": "To trigger garbage collection"},
                ],
                "answer": 0,
                "why": {"zh": "AI 长考时可能十几秒没新事件，连接易被中间设备掐断。心跳不断报「还活着」；响应头 no-transform 则央求代理别缓冲/压缩/改写这条流。", "en": "During long AI thinking, a dozen seconds may pass with no event and the connection risks being severed. Heartbeats keep saying \"alive\"; the no-transform header begs proxies not to buffer/compress/rewrite the stream."},
            },
        ],
        "open": [
            {"zh": "课里说事件总线是「全局共享」的，于是每条 SSE 连接要戴「过滤眼镜」（按 directory + workspaceID 过滤）。如果去掉这层过滤，会发生什么糟糕的事？", "en": "The lesson says the event bus is “globally shared,” so each SSE connection wears “filter glasses” (filtering by directory + workspaceID). What goes wrong if you remove this filter?"},
            {"zh": "课里把 server.connected / heartbeat / instance.disposed 比作河的「开闸、心跳、关闸」，让它们和业务事件走同一条流。说说「把连接管理也做成事件」相比「另开一条控制旁路」好在哪。", "en": "The lesson likens server.connected / heartbeat / instance.disposed to the river's “gates and heartbeat,” flowing in the same stream as business events. Why is “making connection management into events” better than a separate control side-channel?"},
        ],
    },
    "12-sdk-generation.html": {
        "mcq": [
            {
                "q": {"zh": "opencode 的客户端 SDK 是怎么来的？", "en": "Where does opencode's client SDK come from?"},
                "opts": [
                    {"zh": "OpenApi.fromApi(PublicApi) 把 20 个组的类型读成 OpenAPI 规范，再由 @hey-api 自动生成", "en": "OpenApi.fromApi(PublicApi) reads the 20 groups' types into an OpenAPI spec, then @hey-api auto-generates it"},
                    {"zh": "由维护者手写并手动维护", "en": "Hand-written and manually maintained by maintainers"},
                    {"zh": "运行时反射动态构造", "en": "Built dynamically via runtime reflection"},
                    {"zh": "从数据库 schema 推导", "en": "Derived from the database schema"},
                ],
                "answer": 0,
                "why": {"zh": "核心是一行 OpenApi.fromApi(PublicApi)：把结构化的 API 类型读成标准 OpenAPI 规范；opencode generate 加料+格式化；@hey-api 照规范印出 types/sdk/client 三个文件。全程没有手写。", "en": "The core is one line, OpenApi.fromApi(PublicApi): read the structured API types into a standard OpenAPI spec; generate seasons+formats; @hey-api prints types/sdk/client from the spec. None hand-written."},
            },
            {
                "q": {"zh": "为什么生成 SDK 能根除前后端「类型漂移」？", "en": "Why does a generated SDK eliminate frontend/backend \"type drift\"?"},
                "opts": [
                    {"zh": "前后端类型不再是两份副本，而是同一源头（server 类型）的两次投影；源头一动两边一起动，对不上当场编译报错", "en": "The two sides' types are no longer two copies but two projections of one source (server types); move the source and both move, mismatch fails compile on the spot"},
                    {"zh": "因为生成的代码运行更快", "en": "Because generated code runs faster"},
                    {"zh": "因为 SDK 不带类型", "en": "Because the SDK has no types"},
                    {"zh": "因为前端不再调后端", "en": "Because the frontend no longer calls the backend"},
                ],
                "answer": 0,
                "why": {"zh": "手写 SDK 里前后端是两份各自维护的副本，分叉编译期无感、运行时才炸。生成 SDK 让两边成为同一类型源的投影，隐患从「运行时才暴露」变成「编译期必现」。", "en": "With a hand-written SDK the two sides are separately maintained copies; a fork is invisible at compile time and blows up at runtime. Generation makes both projections of one type source, turning a runtime-only hazard into a compile-time-certain one."},
            },
            {
                "q": {"zh": "关于「自动生成」，这一课最想纠正的误解是？", "en": "About \"auto-generation,\" what misconception does this lesson most want to correct?"},
                "opts": [
                    {"zh": "自动生成不等于无人值守——输入侧要清洗（stripOptionalNull），输出侧要打补丁修 @hey-api 的已知 bug", "en": "Auto-generation isn't unattended — the input is cleaned (stripOptionalNull) and the output is patched to fix a known @hey-api bug"},
                    {"zh": "自动生成完全无需任何人工", "en": "Auto-generation needs zero human work at all"},
                    {"zh": "自动生成只能用于小型 API", "en": "Auto-generation only works for small APIs"},
                    {"zh": "自动生成会让类型不安全", "en": "Auto-generation makes things type-unsafe"},
                ],
                "answer": 0,
                "why": {"zh": "Effect Schema 翻 OpenAPI 会留「翻译腔」（如 optional 塞进 {type:null} 孤儿），需 stripOptionalNull 清洗；@hey-api 有个 SSE 类型 bug，需生成后精准改一处字符串。机器干 99%，人盯那 1% 毛刺。", "en": "Effect Schema leaves an accent translating to OpenAPI (e.g. optional injects a {type:null} orphan) needing stripOptionalNull; @hey-api has an SSE type bug needing a precise post-gen string edit. Machine does 99%, a human minds the 1% of burrs."},
            },
        ],
        "open": [
            {"zh": "课里说「类型即数据」是这套机制的支点：API 类型活到运行时、被 fromApi 逐字读出。除了生成 SDK，你还能想到把这份「契约数据」投影成什么有用的东西？", "en": "The lesson says “types as data” is the pivot: API types live to runtime and are read verbatim by fromApi. Besides generating an SDK, what else useful could you project this “contract data” into?"},
            {"zh": "生成物（openapi.json、SDK 文件）是要提交进仓库的，所以 opencode 执着于「逐字节可复现」（prettier、clean:true）。说说如果产物不可复现，code review 和协作会遇到什么麻烦。", "en": "The artifacts (openapi.json, SDK files) are committed to the repo, so opencode insists on “byte-reproducibility” (prettier, clean:true). What trouble would code review and collaboration hit if the artifact weren't reproducible?"},
        ],
    },
    "13-transports.html": {
        "mcq": [
            {
                "q": {"zh": "「同一 handler、两种传输」之所以可能，关键的「接缝」是什么？", "en": "What is the key \"seam\" that makes \"one handler, two transports\" possible?"},
                "opts": [
                    {"zh": "fetch——server 进出是 Request/Response，SDK 所有调用都经一个可配置的 fetch 函数", "en": "fetch — the server's in/out is Request/Response, and all SDK calls go through one configurable fetch function"},
                    {"zh": "一个共享的全局变量", "en": "A shared global variable"},
                    {"zh": "数据库连接池", "en": "A database connection pool"},
                    {"zh": "环境变量", "en": "Environment variables"},
                ],
                "answer": 0,
                "why": {"zh": "两头都以标准 fetch 形态为界面：server 是 app.fetch(request)，SDK 用可配置 fetch 发请求。只要提供一个「形状是 fetch、内部随意」的函数，就能把请求导向任何地方。", "en": "Both ends meet at the standard fetch shape: the server is app.fetch(request), the SDK sends via a configurable fetch. Supply a function shaped like fetch but free inside, and you can steer requests anywhere."},
            },
            {
                "q": {"zh": "富 TUI 用 createWorkerFetch 时，Worker 线程最终调用的是什么？", "en": "When the rich TUI uses createWorkerFetch, what does the Worker thread ultimately call?"},
                "opts": [
                    {"zh": "Server.Default().app.fetch(request)——就是第 9 课那个 webHandler，零网络", "en": "Server.Default().app.fetch(request) — exactly Lesson 9's webHandler, zero network"},
                    {"zh": "一个为 TUI 专写的本地数据访问层", "en": "A local data-access layer written specially for the TUI"},
                    {"zh": "通过 localhost HTTP 再发一次请求", "en": "Re-sends the request over localhost HTTP"},
                    {"zh": "直接读数据库", "en": "Reads the database directly"},
                ],
                "answer": 0,
                "why": {"zh": "createWorkerFetch 对外伪装成 fetch，对内把请求经 RPC 发给 worker；worker 的 rpc.fetch 重建 Request 后调同一个 app.fetch。绕一圈最终触达的，和网络客户端是同一个 handler。", "en": "createWorkerFetch disguises as fetch outwardly, ships the request via RPC inwardly; the worker's rpc.fetch rebuilds the Request and calls the same app.fetch. What it ultimately reaches is the same handler as the network client's."},
            },
            {
                "q": {"zh": "为什么富 TUI 要把 server 放进一个 Worker 线程，而不是主线程直接函数调用？", "en": "Why does the rich TUI put the server in a Worker thread instead of a direct main-thread function call?"},
                "opts": [
                    {"zh": "主线程要专心渲染保持跟手，重活放 worker；跨线程不能共享内存，只能用类型安全 RPC 传消息", "en": "The main thread must focus on rendering and stay responsive, heavy work goes to the worker; threads can't share memory, so type-safe RPC passes messages"},
                    {"zh": "为了绕过 TypeScript 的类型检查", "en": "To bypass TypeScript's type checking"},
                    {"zh": "因为 Effect 不能在主线程运行", "en": "Because Effect can't run on the main thread"},
                    {"zh": "纯粹是历史遗留，没有理由", "en": "Pure legacy, no reason"},
                ],
                "answer": 0,
                "why": {"zh": "模型调用、工具执行是重活，留在主线程会卡住 TUI 渲染，所以塞进 worker。而 Worker 线程间不能共享内存对象，只能传消息——RPC 把「跨线程调函数」包成了类型安全的消息往返。", "en": "Model calls and tool execution are heavy; left on the main thread they stall TUI rendering, so they go to the worker. Worker threads can't share memory objects, only pass messages — RPC wraps cross-thread calls into a type-safe message round-trip."},
            },
        ],
        "open": [
            {"zh": "课里说 opencode「没有为 TUI 单独发明一套本地通信协议」，而是逼进程内也走完整的 Request→handler→Response。这比写一条「直接调内部函数」的捷径多花了功夫，它换来了什么？", "en": "The lesson says opencode “didn't invent a separate local protocol for the TUI” but forces the in-process path through the full Request→handler→Response. This costs more than a “call internal functions directly” shortcut — what does it buy?"},
            {"zh": "课里强调「边界越窄，可替换性越强」，fetch 窄到只剩进 Request 出 Response。结合你自己写过的代码，说一个你曾经把边界定得太宽、结果难以替换的例子。", "en": "The lesson stresses “the narrower the boundary, the stronger the replaceability,” with fetch narrowed to just Request in, Response out. From your own code, give one example where you made a boundary too wide and it became hard to replace."},
        ],
    },
    "14-session-messages-parts.html": {
        "mcq": [
            {
                "q": {"zh": "opencode core 的三层基本数据结构是？", "en": "What are the three basic data layers of opencode's core?"},
                "opts": [
                    {"zh": "Session ⊃ Message ⊃ Part —— 会话装消息、消息装部件", "en": "Session ⊃ Message ⊃ Part — a session holds messages, a message holds parts"},
                    {"zh": "Table ⊃ Row ⊃ Column", "en": "Table ⊃ Row ⊃ Column"},
                    {"zh": "Request ⊃ Response ⊃ Body", "en": "Request ⊃ Response ⊃ Body"},
                    {"zh": "Project ⊃ File ⊃ Line", "en": "Project ⊃ File ⊃ Line"},
                ],
                "answer": 0,
                "why": {"zh": "TUI 每一行、SDK 每个对象、数据库每条记录、事件流每个更新，本质都是读写 Session/Message/Part 这三层嵌套结构。读懂它们=拿到理解整个 core 的坐标系。", "en": "Every TUI line, SDK object, DB record, and event-stream update is essentially reading/writing the nested Session/Message/Part structure. Understanding them = the coordinate system for the whole core."},
            },
            {
                "q": {"zh": "为什么 Assistant 消息的 content 是一个 part 数组，而不是一个字符串？", "en": "Why is an Assistant message's content a part array, not a string?"},
                "opts": [
                    {"zh": "因为一条回复本就是交错的（思考/文字/工具），拆成有序 part 才能分别渲染、逐 part 增量更新", "en": "Because a reply is inherently interleaved (reasoning/text/tool); split into ordered parts, each can render separately and update incrementally"},
                    {"zh": "因为字符串太占内存", "en": "Because strings use too much memory"},
                    {"zh": "因为 JSON 不支持字符串", "en": "Because JSON doesn't support strings"},
                    {"zh": "纯属历史包袱", "en": "Pure legacy baggage"},
                ],
                "answer": 0,
                "why": {"zh": "回复真实形态是交错的：想一会儿(reasoning)→说两句(text)→调工具(tool)→接着说。拆成 part 数组，系统能折叠思考、显示文字、把工具画成带状态的卡片——第 11 课实时 UI 的根。形状压扁了，结构就找不回来了。", "en": "A reply is interleaved: think (reasoning) → speak (text) → call a tool → continue. As a part array, the system folds thinking, shows text, draws tools as status cards — the root of Lesson 11's live UI. Flatten the shape and the structure is unrecoverable."},
            },
            {
                "q": {"zh": "tool part 内部的 ToolState 是什么？", "en": "What is the ToolState inside a tool part?"},
                "opts": [
                    {"zh": "一个状态机：pending→running→completed/error，信息逐阶段递增", "en": "A state machine: pending→running→completed/error, info incremental by stage"},
                    {"zh": "工具的名字", "en": "The tool's name"},
                    {"zh": "一个布尔值：成功或失败", "en": "A boolean: success or failure"},
                    {"zh": "工具的源代码", "en": "The tool's source code"},
                ],
                "answer": 0,
                "why": {"zh": "把工具调用的「一生」编码进数据模型：pending 只有原始 input，running 加解析后 input 和流式 content，completed 再加 result/产物路径。于是「工具现在什么阶段」是一等可查事实，TUI 能实时画状态、历史能精确重放。", "en": "It encodes a tool call's whole life: pending has raw input, running adds parsed input and streaming content, completed adds result/output paths. So a tool's current stage is a first-class queryable fact — the TUI draws status live, history replays exactly."},
            },
        ],
        "open": [
            {"zh": "课里说「换了模型」本身也是一条历史消息（ModelSwitched），而不是改 Session 上一个 currentModel 字段。这两种做法在「忠实重建过去任意一刻」上有什么本质差别？", "en": "The lesson says “switched model” is itself a history message (ModelSwitched), not editing a currentModel field on Session. What's the essential difference for “faithfully reconstructing any past moment”?"},
            {"zh": "Session 只装元数据、不装对话内容（内容在 Message 那层）。结合 TUI 左边那列会话列表，说说这种「轻身份 / 重内容」分离带来的好处。", "en": "Session holds only metadata, not conversation content (that's at the Message layer). With the TUI's left-side session list in mind, what does this “light identity / heavy content” separation buy?"},
        ],
    },
    "15-input-inbox.html": {
        "mcq": [
            {
                "q": {"zh": "一个 prompt 飞到 server 后，opencode 第一件事做什么？", "en": "When a prompt reaches the server, what does opencode do first?"},
                "opts": [
                    {"zh": "admit：把它作为不可变事件持久入账、拿一个序号——不跑任何模型", "en": "admit: persist it as an immutable event and get a sequence number — running no model"},
                    {"zh": "立刻 await 模型 run 这个 prompt", "en": "immediately await the model running the prompt"},
                    {"zh": "丢进内存队列，处理完就忘", "en": "drop it into an in-memory queue, forgotten once processed"},
                    {"zh": "直接改 Session 上的一个字段", "en": "directly edit a field on the Session"},
                ],
                "answer": 0,
                "why": {"zh": "SessionInput.admit 把 prompt 发布成 PromptLifecycle.Admitted 事件、落进 session_input 收件箱、拿到单调 admitted_seq——又快又稳，一行模型代码都不跑。执行是后面的事。", "en": "SessionInput.admit publishes the prompt as a PromptLifecycle.Admitted event, lands it in the session_input inbox, gets a monotonic admitted_seq — fast and stable, running no model. Execution comes later."},
            },
            {
                "q": {"zh": "「先入账、再执行」这一劈两半，消解了哪三个噩梦？", "en": "Splitting into \"admit first, run later\" dissolves which three nightmares?"},
                "opts": [
                    {"zh": "崩溃丢失、并发打架、重试翻倍", "en": "crash loss, concurrency clash, retry doubling"},
                    {"zh": "内存泄漏、死锁、栈溢出", "en": "memory leaks, deadlocks, stack overflow"},
                    {"zh": "类型错误、语法错误、拼写错误", "en": "type errors, syntax errors, typos"},
                    {"zh": "延迟高、带宽小、丢包", "en": "high latency, low bandwidth, packet loss"},
                ],
                "answer": 0,
                "why": {"zh": "崩溃：事件已落库，重启能从收件箱捞回。并发：所有输入先按 admitted_seq 排队、串行取，谁也别想插队抢状态。重试：admit 按 id 幂等，同一 prompt 只入账一次。", "en": "Crash: the event landed, restart fishes it from the inbox. Concurrency: all inputs queue by admitted_seq, pulled serially, none cutting in. Retry: admit is idempotent by id, the same prompt admitted once."},
            },
            {
                "q": {"zh": "session_input 表里 promoted_seq 为 NULL 代表什么？", "en": "In the session_input table, what does promoted_seq being NULL mean?"},
                "opts": [
                    {"zh": "这条输入还在收件箱里待领、尚未被提单成可见消息", "en": "this input still waits in the inbox, not yet promoted into a visible message"},
                    {"zh": "这条输入已经执行完了", "en": "this input has finished executing"},
                    {"zh": "这条输入出错了", "en": "this input errored"},
                    {"zh": "这条输入是空的", "en": "this input is empty"},
                ],
                "answer": 0,
                "why": {"zh": "刚入账时 promoted_seq=NULL（待领）；串行执行者在安全间隙把它提出来、变成 User 消息时才填上。于是「收件箱里还有哪些没处理」=查 promoted_seq IS NULL 的行，极廉价。", "en": "Freshly admitted, promoted_seq=NULL (waiting); the serial executor fills it when promoting at a safe gap into a User message. So \"what's unprocessed in the inbox\" = query rows with promoted_seq IS NULL, dirt cheap."},
            },
        ],
        "open": [
            {"zh": "课里把 admit 比作数据库的预写日志（WAL）：先记录意图、再兑现意图。结合你用过的任何「崩溃后还能恢复」的系统，说说这种「先持久化意图」的模式还在哪里见过。", "en": "The lesson likens admit to a database's write-ahead log (WAL): record intent first, fulfil it later. From any “crash-recoverable” system you've used, where else have you seen this “persist the intent first” pattern?"},
            {"zh": "为什么 opencode 用 admitted_seq / promoted_seq 两个序号，而不是一个布尔的「已处理/未处理」状态位？序号比状态位多给了什么？", "en": "Why does opencode use two numbers (admitted_seq / promoted_seq) rather than one boolean “processed/unprocessed” status bit? What does a sequence give that a status bit doesn't?"},
        ],
    },
    "16-run-coordinator.html": {
        "mcq": [
            {
                "q": {"zh": "运行协调器的核心铁律是什么？", "en": "What is the run coordinator's core iron law?"},
                "opts": [
                    {"zh": "同一会话至多一条执行链（串行），不同会话各跑各的（并发）", "en": "At most one execution chain per session (serial), different sessions each running their own (concurrent)"},
                    {"zh": "全局只许一个会话跑", "en": "Only one session may run globally"},
                    {"zh": "所有会话完全并发、无任何限制", "en": "All sessions fully concurrent with no limit"},
                    {"zh": "每个会话最多三条链", "en": "At most three chains per session"},
                ],
                "answer": 0,
                "why": {"zh": "靠内部一个 Map<Key,Entry>（每会话一个 Entry/车道）：同会话 ID 命中同一 Entry → 串成一条线；异会话 ID 命中不同 Entry → 各跑各的。是第 8 课 KeyedMutex「同 key 串行、异 key 并行」的精装版。", "en": "Via an internal Map<Key,Entry> (one Entry/lane per session): same session ID hits the same Entry → strung into one line; different IDs hit different Entries → each runs its own. A deluxe edition of Lesson 8's KeyedMutex."},
            },
            {
                "q": {"zh": "run 和 wake 的区别是？", "en": "What's the difference between run and wake?"},
                "opts": [
                    {"zh": "run 是显式发车（起链或并入当前链）；wake 是建议摇铃（空闲起链，忙则只合并一个后续）", "en": "run is explicit depart (start or merge the current chain); wake is advisory ring (idle starts a chain, busy only coalesces one follow-up)"},
                    {"zh": "run 同步、wake 异步，没别的区别", "en": "run is sync, wake is async, no other difference"},
                    {"zh": "run 用于读、wake 用于写", "en": "run for reads, wake for writes"},
                    {"zh": "两者完全等价", "en": "The two are entirely equivalent"},
                ],
                "answer": 0,
                "why": {"zh": "run 是「命令」：明确要求执行（如 resume）。wake 是「建议」：报告可能有活——第 15 课 admit 后摇的就是 wake。建议的归 wake、命令的归 run，与第 15 课「持久的归 admit、建议的归 wake」一脉相承。", "en": "run is a command: explicitly demand execution (e.g. resume). wake is advice: report there may be work — what's rung after Lesson 15's admit. Advisory to wake, command to run, of one lineage with Lesson 15."},
            },
            {
                "q": {"zh": "一趟 drain 进行中又来了 5 个 wake，coalesce 会怎么处理？", "en": "Five wakes arrive during a running drain — how does coalesce handle them?"},
                "opts": [
                    {"zh": "折叠成至多一个待办后续（保留最新 seq），本趟结束后补跑一趟即可一次扫光", "en": "Fold into at most one pending follow-up (keeping the newest seq); one extra round after this trip sweeps them all"},
                    {"zh": "排成 5 趟队，依次跑 5 趟", "en": "Queue 5 trips and run them one by one"},
                    {"zh": "直接丢弃这 5 个 wake", "en": "Discard the 5 wakes outright"},
                    {"zh": "立刻并发起 5 条新链", "en": "Immediately start 5 new chains concurrently"},
                ],
                "answer": 0,
                "why": {"zh": "一趟 drain 本就扫光收件箱当前所有合格行，故只需一个后续兜住途中新来的。合并规则：run 压倒 wake；wake 取最新 seq——补跑那趟据此保证覆盖到最新一条，不空跑不漏单。", "en": "One drain already sweeps all currently-eligible rows, so one follow-up suffices for mid-trip arrivals. Rules: run dominates wake; wake keeps the newest seq — so the rerun is guaranteed to cover the latest, no idle running, no missed tickets."},
            },
        ],
        "open": [
            {"zh": "课里说「最好的并发 bug，是那些被设计得压根不可能出现的」——协调器用「同会话至多一条链」从结构上排除竞态，而非事后加锁。对比这两种思路（结构性排除 vs 加锁补救），各自的代价和好处是什么？", "en": "The lesson says “the best concurrency bugs are the ones designed to be impossible” — the coordinator structurally eliminates races via “at most one chain per session” rather than locking after the fact. Compare the two approaches (structural elimination vs lock-patching): costs and benefits of each?"},
            {"zh": "协调器把「纯调度」（按 key 串行/合并/起停）和「具体排空时跑什么」（SessionRunner.run）彻底解耦，drain 只是个传进来的回调。这种解耦对「单独测试调度逻辑」有什么好处？", "en": "The coordinator fully decouples “pure scheduling” (serial/coalesce/start-stop by key) from “what to run on drain” (SessionRunner.run), with drain just a passed-in callback. What does this decoupling buy for “testing the scheduling logic in isolation”?"},
        ],
    },
    "17-agent-loop.html": {
        "mcq": [
            {
                "q": {"zh": "agent 循环和聊天机器人的根本区别是？", "en": "What fundamentally separates the agent loop from a chatbot?"},
                "opts": [
                    {"zh": "agent 是「一个目标、多轮自驱」：反复想一步→调工具→看结果→再想，直到完成或撞边界", "en": "An agent is \"one goal, many self-driven rounds\": repeatedly think→call tool→see result→think again, until done or it hits a boundary"},
                    {"zh": "agent 用的模型更大", "en": "An agent uses a bigger model"},
                    {"zh": "agent 不需要联网", "en": "An agent needs no network"},
                    {"zh": "没有区别", "en": "There is no difference"},
                ],
                "answer": 0,
                "why": {"zh": "聊天机器人一问一答；agent 给个目标就自驱迭代：while(activity){ for(step<25){ runTurn } }。每轮 runTurn 想一步、可能调工具，看结果再想下一步——这台有界自驱循环正是 agent 的心脏。", "en": "A chatbot is one ask, one answer; an agent self-drives on a goal: while(activity){ for(step<25){ runTurn } }. Each runTurn thinks, maybe calls tools, sees results, thinks next — this bounded self-driving loop is the agent's heart."},
            },
            {
                "q": {"zh": "循环对工具调用的第一条纪律是什么？", "en": "What's the loop's first discipline for tool calls?"},
                "opts": [
                    {"zh": "先把调用 durably 记成 tool part(pending)，再开始任何副作用", "en": "Durably record the call as a tool part(pending) first, before any side effect"},
                    {"zh": "先执行，成功了再记录", "en": "Execute first, record only on success"},
                    {"zh": "不记录，直接执行", "en": "Don't record, just execute"},
                    {"zh": "串行执行所有工具", "en": "Execute all tools serially"},
                ],
                "answer": 0,
                "why": {"zh": "读文件/跑命令有副作用、可能崩。先落库「我要调这个」再动手：万一执行中崩了，至少发起记录还在，重启能据此收拾（run 开头的 failInterruptedTools 就专清这些）。是第 15 课「先记意图、再兑现」在工具层的复刻。", "en": "Reading files/running commands has side effects and may crash. Record \"I'm calling this\" before acting: if it crashes mid-run, at least the initiation record remains, so restart can clean up (failInterruptedTools at run's start does exactly this). Lesson 15's \"record intent first\" at the tool layer."},
            },
            {
                "q": {"zh": "为什么循环每一轮都要重新加载「投影历史」，而不在内存里攒状态？", "en": "Why does the loop reload \"projected history\" every round instead of hoarding state in memory?"},
                "opts": [
                    {"zh": "持久层是唯一真相：这让 steer 即时并入、崩溃能恢复、多端能一致", "en": "The durable layer is the sole truth: this lets steer merge instantly, crashes recover, clients stay consistent"},
                    {"zh": "因为内存太贵", "en": "Because memory is expensive"},
                    {"zh": "因为模型要求这样", "en": "Because the model requires it"},
                    {"zh": "纯粹是性能优化", "en": "Purely a performance optimization"},
                ],
                "answer": 0,
                "why": {"zh": "每轮回持久层取最新真相，你在模型忙时插的话（admit→提单成消息）下一轮重读就在里面、当轮就能被消化（循环里 hasPending(steer) 那句）。看似笨，实则是 agent 可实时引导、可崩溃恢复、可多端一致的总开关。", "en": "Each round fetches the latest truth from the durable layer, so a line you insert while busy (admit→promoted to a message) is there on the next reread, digestible that round (the hasPending(steer) line). Seemingly dumb, it's the master switch for live-steerable, crash-recoverable, multi-client-consistent agents."},
            },
        ],
        "open": [
            {"zh": "课里说「等齐再走」——一轮里并发起的多个工具，必须全部 settle 才进下一轮。如果改成「回来一个就喂模型一个」，会出什么问题？为什么模型的下一步推理需要一份完整一致的世界状态？", "en": "The lesson says \"await all before moving on\" — multiple tools started concurrently in a round must all settle before the next round. What breaks if you instead \"feed the model each result as it returns\"? Why does the model's next reasoning need a complete, consistent world state?"},
            {"zh": "MAX_STEPS=25 给内层循环套了个硬环，而不是 while(true)。结合「模型并不总知道自己该停」，说说这个上限在「自由迭代」和「绝不失控」之间扮演的角色。", "en": "MAX_STEPS=25 puts a hard ring on the inner loop instead of while(true). Given \"the model doesn't always know to stop,\" discuss the role this ceiling plays between \"free iteration\" and \"never run wild.\""},
        ],
    },
    "18-tool-calls-fiberset.html": {
        "mcq": [
            {
                "q": {"zh": "ToolRegistry.materialize 在「按权限亮工具」上做了什么？", "en": "What does ToolRegistry.materialize do for \"showing tools by permission\"?"},
                "opts": [
                    {"zh": "被权限完全禁用的工具，根本不出现在给模型的 definitions 里——模型无从知晓、无从调用", "en": "A wholly-disabled tool simply doesn't appear in the definitions given to the model — unknown to it, uncallable"},
                    {"zh": "把所有工具都亮出来，调用时再拦", "en": "Show all tools, then block at call time"},
                    {"zh": "让模型自己决定能用哪些", "en": "Let the model decide which it may use"},
                    {"zh": "在启动时一次性写死工具清单", "en": "Hard-code the tool list once at startup"},
                ],
                "answer": 0,
                "why": {"zh": "materialize 每轮按当前权限筛 definitions：whollyDisabled 的工具直接从清单移除。最好的拦截是让选项压根不出现——把约束做进形状，而非事后补救。且每轮重算，权限因此是动态、随上下文生效的视野。", "en": "materialize filters definitions by current permission each round: a whollyDisabled tool is removed from the list. The best interception makes the option not appear — constraint in the shape, not patched after. Recomputed each round, so permission is a dynamic, context-sensitive field of view."},
            },
            {
                "q": {"zh": "FiberSet 相比 Promise.all 的关键优势是什么？", "en": "What's FiberSet's key advantage over Promise.all?"},
                "opts": [
                    {"zh": "集合里每个 fiber 都被记着、可整体召回（clear）——中断时一声令下全员干净取消，不留野线程", "en": "Every fiber in the set is tracked and whole-set recallable (clear) — on interrupt, one command cleanly cancels all, no stray threads"},
                    {"zh": "FiberSet 跑得更快", "en": "FiberSet runs faster"},
                    {"zh": "FiberSet 不需要 await", "en": "FiberSet needs no await"},
                    {"zh": "两者完全一样", "en": "They are identical"},
                ],
                "answer": 0,
                "why": {"zh": "Promise.all 是「发射后不管」：失败时其余仍野跑、无法整体取消、出范围成幽灵。FiberSet 把每个 fiber 纳入集合可整体 clear——这是第 7 课结构化并发「开多少收多少」的灵魂，中断时干净收场 vs 留下幽灵的分野。", "en": "Promise.all is fire-and-forget: on failure the rest run wild, no whole cancel, ghosts past scope. FiberSet tracks each fiber for whole-set clear — Lesson 7's structured-concurrency soul of \"collect as many as you send,\" the divide between clean wrap-up and leaving ghosts on interrupt."},
            },
            {
                "q": {"zh": "uninterruptibleMask((restore) => restore(settle)) 这个写法保护了什么？", "en": "What does uninterruptibleMask((restore) => restore(settle)) protect?"},
                "opts": [
                    {"zh": "默认锁死记账式关键操作，仅用 restore 把工具执行那段开放成可中断——工具可停、账本完整", "en": "Locks ledger-like critical ops by default, reopening only the tool-execution part as interruptible via restore — tool stoppable, ledger intact"},
                    {"zh": "让所有代码都不可中断", "en": "Makes all code uninterruptible"},
                    {"zh": "让所有代码都可中断", "en": "Makes all code interruptible"},
                    {"zh": "加快工具执行", "en": "Speeds up tool execution"},
                ],
                "answer": 0,
                "why": {"zh": "对持久可恢复的系统，「记账完整」优先于「执行能停」。默认不可中断保护发起记录/写回状态不被撕成半拉子；restore 只把真正执行工具那段开放成可中断。uninterruptibleMask 决定的，是中断这把刀只许落在哪儿。", "en": "For a durable, recoverable system, ledger integrity outranks execution being stoppable. Uninterruptible-by-default protects recording/state-write from being torn; restore reopens only the tool execution. uninterruptibleMask decides where the interrupt knife may land."},
            },
        ],
        "open": [
            {"zh": "课里说权限过滤发生在「每轮重跑的 materialize」，而非启动时写死，于是权限成了「每轮重新校准的视野」。这种动态权限对「同一工具在不同 agent/场景下能力边界伸缩」有什么意义？", "en": "The lesson says permission filtering happens in \"materialize, which reruns each round,\" not fixed at startup, so permission becomes \"a field of view recalibrated each round.\" What does this dynamic permission mean for \"the same tool's capability boundary flexing across agents/scenarios\"?"},
            {"zh": "ToolOutputStore 把超过 2000 行/50KB 的输出落盘、消息只存 outputPaths。这和第 14 课「Session 只装元数据、内容在 Message 那层」是同一种智慧吗？说说「轻身份/重内容分开存」这条原则在本书出现过的地方。", "en": "ToolOutputStore lands output over 2000 lines/50KB on disk, the message holding only outputPaths. Is this the same wisdom as Lesson 14's \"Session holds only metadata, content lives at the Message layer\"? Name where this \"separate light identity from heavy content\" principle has appeared in the book."},
        ],
    },
    "19-projected-history.html": {
        "mcq": [
            {
                "q": {"zh": "opencode 会话存储「一份真相、两种形状」指的是？", "en": "What does opencode's session storage \"one truth, two shapes\" mean?"},
                "opts": [
                    {"zh": "写端用 append-only 事件（底账），读端用投影出的消息/部件表（报表）", "en": "Write end uses append-only events (ledger); read end uses projected message/part tables (statement)"},
                    {"zh": "一份存数据库、一份存文件，内容相同", "en": "One copy in a database, one in a file, identical content"},
                    {"zh": "中文一份、英文一份", "en": "One Chinese copy, one English copy"},
                    {"zh": "压缩前一份、压缩后一份", "en": "One before compression, one after"},
                ],
                "answer": 0,
                "why": {"zh": "写要 append-only/不可变/有序（崩不丢、可重放）；读要当下/干净/现成（模型一读即用）。两端诉求相反，故分两形状：事件是底账，投影消息是报表，由 SessionProjector 连接。即 CQRS/事件溯源读模型。", "en": "Writing wants append-only/immutable/ordered (crash-safe, replayable); reading wants current/clean/ready-made (model reads as-is). Opposite needs, so two shapes: events the ledger, projected messages the statement, linked by SessionProjector. I.e. CQRS / event-sourcing read model."},
            },
            {
                "q": {"zh": "为什么不每次读历史就把事件从头重放一遍？", "en": "Why not replay events from scratch on every history read?"},
                "opts": [
                    {"zh": "agent 循环每轮都重读，重放代价随历史线性增长会拖垮高频读；维护投影=把贵活一次性付在写端", "en": "The agent loop rereads every round; replay cost grows linearly with history, dragging down high-frequency reads; a projection pays the expensive work once at the write end"},
                    {"zh": "重放会改写事件", "en": "Replaying rewrites the events"},
                    {"zh": "事件不能被读取", "en": "Events can't be read"},
                    {"zh": "模型不支持事件", "en": "The model doesn't support events"},
                ],
                "answer": 0,
                "why": {"zh": "第 17 课循环每轮重读历史，长会话上千事件。每轮全重放，代价越滚越大。维护投影=拿写端一次性成本换读端长久廉价（读时只 select）。同数据库物化视图/索引的算计：贵活挪到低频写端做一次。", "en": "Lesson 17's loop rereads each round; a long session has thousands of events. Replaying all each round snowballs. A projection trades a one-time write-end cost for lasting read-end cheapness (reads are just selects). Same as a DB's materialized views/indexes: move the expensive work to the low-frequency write end."},
            },
            {
                "q": {"zh": "SessionHistory.load 读出的是什么？", "en": "What does SessionHistory.load read?"},
                "opts": [
                    {"zh": "投影好的、且被最近压缩+上下文纪元基线裁过边的一段「有界」历史窗口", "en": "Projected history, edge-trimmed by latest compaction + context epoch baseline — a \"bounded\" window"},
                    {"zh": "开天辟地以来的全部消息", "en": "All messages since the dawn of time"},
                    {"zh": "只有最后一条消息", "en": "Only the last message"},
                    {"zh": "原始未处理的事件流", "en": "The raw unprocessed event stream"},
                ],
                "answer": 0,
                "why": {"zh": "模型上下文窗口装不下无限历史。load 不读全部：久远部分由 compaction（第 51 课）概括、从它往后读，再叠加上下文纪元 baseline_seq（第 24 课）。「读历史」=「读当前该看的那一段」。读的是投影消息，不重放事件。", "en": "The model's context window can't hold infinite history. load reads not all: the old part is summarized by compaction (Lesson 51), read from it onward, layered with the context epoch baseline_seq (Lesson 24). \"Reading history\" = \"reading the slice you should see now.\" It reads projected messages, not replayed events."},
            },
        ],
        "open": [
            {"zh": "课里说「报表丢了能照底账重投，底账改了才真失真」，所以权威放在不可变的事件端、便利放在可重建的投影端。用这副「底账 vs 报表」的眼镜，再举一个你熟悉的系统（如 git、缓存、数据库物化视图）说说同样的分工。", "en": "The lesson says \"lose the statement and it re-projects from the ledger; rewriting the ledger truly distorts,\" so authority sits at the immutable event end, convenience at the rebuildable projection end. With this \"ledger vs statement\" lens, name another system you know (git, caches, DB materialized views) with the same division."},
            {"zh": "投影器有一行注释：「更新的回合取代过时残行，绝不接着投影一条更老的 assistant 记录」。为什么投影不能无脑追加、必须懂得让新回合盖过旧的半截残留？举一个会出问题的场景。", "en": "The projector has a comment: \"a newer turn supersedes stale incomplete rows; never resume an older assistant projection.\" Why can't projection mindlessly append but must let a new turn override stale half-finished leftovers? Give a scenario that would break."},
        ],
    },
    "20-steps-errors.html": {
        "mcq": [
            {
                "q": {"zh": "撞上 MAX_STEPS=25 上限时，循环怎么处理？", "en": "When hitting the MAX_STEPS=25 cap, how does the loop handle it?"},
                "opts": [
                    {"zh": "抛出带 sessionID/limit 字段的类型化错误 StepLimitExceededError，而非默默停下", "en": "Throw a typed StepLimitExceededError carrying sessionID/limit fields, not silently stop"},
                    {"zh": "默默返回，假装完成了", "en": "Silently return, pretending it finished"},
                    {"zh": "无限继续，直到模型满意", "en": "Continue forever until the model is satisfied"},
                    {"zh": "重启整个进程", "en": "Restart the whole process"},
                ],
                "answer": 0,
                "why": {"zh": "模型不总知道该停，可能陷兔子洞烧钱。25 是不容商量的刹车。撞限抛带字段的 StepLimitExceededError（哪个会话、撞多少），上层据此明确知道「为何而停」、可恰当反应，而非面对语焉不详的结束。", "en": "The model doesn't always know to stop and may rabbit-hole, burning money. 25 is a non-negotiable brake. Hitting it throws a field-carrying StepLimitExceededError (which session, what cap), so the upper layer knows exactly why it stopped and can react, not face a vague ending."},
            },
            {
                "q": {"zh": "RunError 联合类型体现了什么设计原则？", "en": "What design principle does the RunError union embody?"},
                "opts": [
                    {"zh": "错误是值、写进签名：所有失败模式列进类型，编译器逼调用者面对每一种", "en": "Errors are values, written into the signature: all failure modes in the type, compiler forces callers to face each"},
                    {"zh": "所有错误都用 throw 抛出", "en": "Throw all errors with throw"},
                    {"zh": "忽略所有错误", "en": "Ignore all errors"},
                    {"zh": "把错误记进日志就行", "en": "Just log the errors"},
                ],
                "answer": 0,
                "why": {"zh": "run 返回 Effect<void, RunError>，RunError 挂在签名里。每种失败（LLMError/StepLimit/MessageDecode…）是类型里看得见、躲不开的分支，没有藏在 throw 里的暗雷。把不确定从运行时惊吓抬成编译期清单——这份清单本身还是极佳文档。", "en": "run returns Effect<void, RunError>, with RunError in the signature. Every failure (LLMError/StepLimit/MessageDecode…) is a visible, unavoidable branch, no landmine hidden in a throw. Lifting uncertainty from runtime fright to a compile-time checklist — which is itself excellent documentation."},
            },
            {
                "q": {"zh": "中断时 failUnsettledTools 保证了什么不变量？", "en": "On interrupt, what invariant does failUnsettledTools guarantee?"},
                "opts": [
                    {"zh": "每个工具最终都落到明确终态——绝无「永远卡在 running」的残骸", "en": "Every tool ultimately lands in a definite terminal state — no \"forever stuck in running\" wreckage"},
                    {"zh": "所有工具都成功", "en": "All tools succeed"},
                    {"zh": "工具不会被中断", "en": "Tools can't be interrupted"},
                    {"zh": "中断会回滚所有工具", "en": "Interrupt rolls back all tools"},
                ],
                "answer": 0,
                "why": {"zh": "ToolState 是 pending→running→completed/error。若中断砍在工具 running 时不管它，就永远卡在 running，成历史里的幽灵。failUnsettledTools 把没结清的标记 error；配合开跑前的 failInterruptedTools，两把扫帚保证每个工具都有明确归宿。", "en": "ToolState is pending→running→completed/error. If interrupt cuts while a tool is running and it's left alone, it's stuck in running forever, a ghost in history. failUnsettledTools marks unsettled ones error; with failInterruptedTools before the run, two brooms guarantee every tool has a definite fate."},
            },
        ],
        "open": [
            {"zh": "课里说安全护栏的艺术「不在有没有，而在卡在哪个值」——MAX_STEPS 太小掐断复杂任务、太大失控代价可怕，25 是经验折中。如果让你为一个会动用户文件的 agent 选这个上限，你会考虑哪些因素？", "en": "The lesson says a guardrail's art is \"not whether but at what value\" — too-small MAX_STEPS cuts off complex tasks, too-large makes runaway costs frightening, 25 an empirical compromise. If you set this cap for an agent that touches user files, what factors would you weigh?"},
            {"zh": "源码错误处理段对「失败」分得极细（被中断/工具炸了/模型报错各有收尾），但都殊途同归到 failUnsettledTools，最后才如实 failCause 上抛。「先收干净自己的烂摊子，再诚实交出错误」——为什么这个顺序很重要？", "en": "The source's error handling dissects \"failure\" finely (interrupted/tool-blew-up/model-error each with its wind-down) but all converge on failUnsettledTools, only then faithfully failCause-rethrowing. \"Clean up your own mess first, then hand the error over honestly\" — why does this order matter?"},
        ],
    },
    "21-system-context.html": {
        "mcq": [
            {
                "q": {"zh": "什么是 opencode 的「系统上下文（system context）」？", "en": "What is opencode's \"system context\"?"},
                "opts": [
                    {"zh": "对话之外、系统替模型主动注入的「环境底色」：工作目录、日期、git 状态、常驻指令", "en": "The \"ambient backdrop\" the system actively injects on the model's behalf, outside the conversation: directory, date, git status, standing instructions"},
                    {"zh": "用户发的每一条消息", "en": "Every message the user sends"},
                    {"zh": "模型的权重参数", "en": "The model's weight parameters"},
                    {"zh": "服务器的环境变量", "en": "The server's environment variables"},
                ],
                "answer": 0,
                "why": {"zh": "源码称之为 privileged system context（特权系统上下文）：不是用户随口说的，而是系统亲自观察、背书的可信事实，把模型锚定到它所处的真实世界。它和用户的话不在一个层级——一个要动你文件的 agent 必须分得清哪块地是实的。", "en": "The source calls it privileged system context: not what the user casually says but trusted facts the system observed and vouched for, anchoring the model to its real world. It's not on the same level as user words — an agent touching your files must know which ground is solid."},
            },
            {
                "q": {"zh": "Source 的 baseline 和 update 这对孪生方法解决了什么难关？", "en": "What hurdle do a Source's twin methods baseline and update solve?"},
                "opts": [
                    {"zh": "token 寸土寸金：第一次发全文(baseline)，之后只发变化(update)，不重发不变的信息", "en": "Tokens are precious: send the full text first (baseline), then only the change (update), never resending unchanged info"},
                    {"zh": "让模型跑得更快", "en": "Make the model run faster"},
                    {"zh": "加密上下文", "en": "Encrypt the context"},
                    {"zh": "压缩对话历史", "en": "Compress conversation history"},
                ],
                "answer": 0,
                "why": {"zh": "长会话每轮重复「当前目录/日期/git」全文是巨大浪费，而绝大多数轮这些没变。baseline 负责首次全文、update 负责变化差异——变化才值得被言说，不变就该沉默。这是把「增量」思想贯彻到上下文层的精打细算。", "en": "Repeating the full \"directory/date/git\" each round in a long session is huge waste, when most rounds these don't change. baseline does the first-time full text, update does the change diff — change deserves speaking, sameness stays silent. The \"incremental\" idea carried into the context layer."},
            },
            {
                "q": {"zh": "make<A>(source) 在这套「源代数」里起什么作用？", "en": "What role does make<A>(source) play in this \"source algebra\"?"},
                "opts": [
                    {"zh": "把具体值类型 A 藏起来，产出不透明的 SystemContext，让不同类型的源能被 combine 统一组合", "en": "Hide the concrete value type A, producing an opaque SystemContext so differently-typed sources can be uniformly combined"},
                    {"zh": "执行源、产生副作用", "en": "Execute the source, causing side effects"},
                    {"zh": "把源存进数据库", "en": "Store the source in a database"},
                    {"zh": "校验源的权限", "en": "Check the source's permission"},
                ],
                "answer": 0,
                "why": {"zh": "core/date 的值是日期、core/environment 是目录结构，类型各异。make 把 A closes over（藏起），产出长得一样的不透明 SystemContext，于是 combine 能均匀拼一堆异类源。加新源只需写 Source+make+combine，无需改任何现有代码——第 6 课「面向接口」的延伸。", "en": "core/date's value is a date, core/environment's a directory — different types. make closes over A, producing identical-looking opaque SystemContexts, so combine can uniformly stitch heterogeneous sources. A new source needs only Source+make+combine, no change to existing code — an extension of Lesson 6's \"program to an interface.\""},
            },
        ],
        "open": [
            {"zh": "课里强调 unavailable ≠ removed：「暂时观察不到」不等于「删除」，刷新时保住上一份快照。如果把二者混为一谈（没读到就当没有），会给模型造成什么具体的误导？举个例子。", "en": "The lesson stresses unavailable ≠ removed: \"temporarily unobservable\" isn't \"deleted\"; refresh preserves the last snapshot. If you conflate them (treat \"couldn't read\" as \"absent\"), what concrete misleading does it cause the model? Give an example."},
            {"zh": "课里说系统上下文是「特权」的，和用户的话不在一个层级。为什么对一个会动你文件、跑你命令的 agent 来说，分清「系统观察的事实」与「对话里的一面之词」如此重要？", "en": "The lesson says system context is \"privileged,\" not on the same level as user words. Why is distinguishing \"facts the system observed\" from \"one side of a conversation\" so important for an agent that touches your files and runs your commands?"},
        ],
    },
    "22-context-source.html": {
        "mcq": [
            {
                "q": {"zh": "一个 Source 的 codec 字段同时撑起哪三副担子？", "en": "What three burdens does a Source's codec field shoulder at once?"},
                "opts": [
                    {"zh": "encode(存快照)、decode(读快照)、equivalent(判等)——都从一个 Schema.Codec 派生", "en": "encode (store snapshot), decode (read snapshot), equivalent (compare) — all derived from one Schema.Codec"},
                    {"zh": "加密、压缩、签名", "en": "encrypt, compress, sign"},
                    {"zh": "渲染、路由、缓存", "en": "render, route, cache"},
                    {"zh": "观察、执行、清理", "en": "observe, execute, clean up"},
                ],
                "answer": 0,
                "why": {"zh": "源只声明「我的值长这样」(codec)，make 就白送三种能力：encode 值→JSON 存快照、decode 快照→值、Schema.toEquivalence 从结构自动推出判等。声明结构、判等自来，无需手写「日期/目录怎么比」这种易错逻辑。", "en": "A source declares just \"my value looks like this\" (codec), and make gives three abilities free: encode value→JSON for the snapshot, decode snapshot→value, and Schema.toEquivalence auto-derives equality from structure. Declare the structure, equality comes — no error-prone hand-written comparisons."},
            },
            {
                "q": {"zh": "为什么 baseline 既渲染人类可读全文、又 encode 一份结构化快照？", "en": "Why does baseline both render human-readable full text and encode a structured snapshot?"},
                "opts": [
                    {"zh": "全文说给模型听(求可读)、快照记给系统(求精确比较)——沟通用散文、记忆用结构", "en": "The full text is spoken to the model (readability), the snapshot remembered by the system (precise comparison) — prose for communication, structure for memory"},
                    {"zh": "为了双重备份", "en": "For double backup"},
                    {"zh": "一份给中文、一份给英文", "en": "One for Chinese, one for English"},
                    {"zh": "没有理由，冗余而已", "en": "No reason, just redundant"},
                ],
                "answer": 0,
                "why": {"zh": "给模型的散文求可读，措辞可能变(「你在 X」vs「当前目录：X」)，拿文本比会误报变化。encode 的快照只记规范化的值，拿结构比结构，equivalent 才能干净回答「事实变没变」，不被表达抖动干扰。", "en": "The model's prose seeks readability and wording may vary (\"you're in X\" vs \"Current dir: X\"), so comparing text falsely reports change. The encoded snapshot records only the normalized value; comparing structure to structure, equivalent cleanly answers \"did the fact change,\" undisturbed by phrasing jitter."},
            },
            {
                "q": {"zh": "compare 返回 Incompatible 意味着什么？", "en": "What does compare returning Incompatible mean?"},
                "opts": [
                    {"zh": "上次的快照连解码都解不出来(通常 codec 改过)——放弃增量、退回重 baseline", "en": "Last time's snapshot can't even be decoded (usually the codec changed) — abandon the increment, fall back to re-baseline"},
                    {"zh": "值变大了", "en": "The value got bigger"},
                    {"zh": "两个源冲突了", "en": "Two sources conflict"},
                    {"zh": "模型拒绝了这个源", "en": "The model rejected this source"},
                ],
                "answer": 0,
                "why": {"zh": "decode 用 Option：解不出走 onNone→Incompatible。通常因 codec 在两轮间升级、旧格式快照成天书。硬 diff 危险，明智做法是退回重 baseline——数据格式会变、旧数据不会自动跟着变。能优雅处理这点是系统从「能用」到「耐用」的标志。", "en": "decode uses Option: failing takes onNone→Incompatible. Usually the codec upgraded between rounds, making the old-format snapshot gibberish. Forcing a diff is dangerous; the wise move is re-baseline — data formats change, old data doesn't follow automatically. Handling this gracefully marks a system going from 'works' to 'lasts'."},
            },
        ],
        "open": [
            {"zh": "课里说 Schema.toEquivalence 把判等「从人来写变成从结构推」，连根拔掉了「手写比较漏字段」这一类 bug。结合你写过的代码，回忆一次「两个对象该不该相等」判断出错（或差点出错）的经历。", "en": "The lesson says Schema.toEquivalence turns equality \"from human-written to structure-derived,\" uprooting the \"hand-written comparison misses a field\" bug class. From your own code, recall a time an \"are these two objects equal\" judgment went (or nearly went) wrong."},
            {"zh": "看那条时间线：一个源绝大多数轮都在「沉默」，只有真变化的那轮才花 token。把这套「平时沉默、有变化才泛涟漪」的设计，和「每轮把全部环境信息重灌一遍」对比，在一个聊几小时的会话里差别有多大？", "en": "Look at that timeline: a source is silent most rounds, spending tokens only when it truly changes. Compare this \"silent normally, ripple only on change\" design with \"re-pour all environment info every round\" — how big is the difference in a session lasting hours?"},
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
