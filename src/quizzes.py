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
