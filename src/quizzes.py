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
            {"zh": "21 个路由组的名字本身就是一张 opencode 能力地图。挑其中 3 个组，猜一猜它们各自大概提供什么能力。", "en": "The 21 route-group names are themselves a map of opencode's abilities. Pick 3 groups and guess what each roughly provides."},
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
