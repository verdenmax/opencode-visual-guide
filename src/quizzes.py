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
    "23-context-registry.html": {
        "mcq": [
            {
                "q": {"zh": "注册表的 register 为什么用 Effect.acquireRelease（作用域绑定）？", "en": "Why does the registry's register use Effect.acquireRelease (scope-bound)?"},
                "opts": [
                    {"zh": "注册即声明「在此作用域内存在」，作用域一关必然自动注销——根除「忘了删、源变幽灵」的泄漏", "en": "Registration declares \"exists within this scope\"; scope closes and deregistration necessarily happens — uprooting the \"forgot to remove, source becomes a ghost\" leak"},
                    {"zh": "为了让注册更快", "en": "To make registration faster"},
                    {"zh": "为了加密源", "en": "To encrypt sources"},
                    {"zh": "没有特别理由", "en": "No particular reason"},
                ],
                "answer": 0,
                "why": {"zh": "acquireRelease 把获取与释放配成一对、绑在作用域上，作用域结束释放必然执行。一个源 register 进来、所属作用域关闭时自动摘除，无需手动清理、无路径能遗漏。长跑服务里开关无数会话/插件，靠人记得删迟早漏一处。", "en": "acquireRelease pairs acquire and release bound to a scope; when the scope ends, release necessarily runs. A source registers and is auto-removed when its scope closes — no manual cleanup, no path can miss it. In long-running services opening/closing countless sessions/plugins, relying on humans to remember would leak eventually."},
            },
            {
                "q": {"zh": "load() 为什么要「按 key 排序」？", "en": "Why does load() \"sort by key\"?"},
                "opts": [
                    {"zh": "给汇总钉一个确定顺序（与注册先后无关）——保证可复现、且不让顺序变动假性触发 diff", "en": "Nail a deterministic order on the gathering (independent of registration order) — ensuring reproducibility and preventing order changes from falsely triggering a diff"},
                    {"zh": "为了让 key 短的源排前面", "en": "To put shorter-key sources first"},
                    {"zh": "为了删除重复的源", "en": "To delete duplicate sources"},
                    {"zh": "排序能让 load 更快", "en": "Sorting makes load faster"},
                ],
                "answer": 0,
                "why": {"zh": "不排序时源的顺序取决于注册先后（受加载时序/并发等偶然因素影响），拼出的 baseline 顺序就飘忽：既不可复现、又会让 diff 误判「变了」。凡要被比较/复现的东西都不能依赖偶然顺序——并发去观察、排序来定序，快与稳两不耽误。", "en": "Without sorting, source order depends on registration order (affected by load timing/concurrency), so the baseline order wavers: not reproducible, and makes the diff misjudge \"changed.\" Anything to be compared/reproduced mustn't depend on incidental order — observe concurrently, sort to order; speed and stability both kept."},
            },
            {
                "q": {"zh": "课里说注册表是「指挥与编排者」而非「内容生产者」，这意味着什么？", "en": "The lesson calls the registry a \"conductor/orchestrator,\" not a \"content producer.\" What does this mean?"},
                "opts": [
                    {"zh": "它不知道也不关心任何源观察什么(都是不透明 SystemContext)，只管谁在册/什么顺序/怎么并发收齐——故加多少种源都零改动", "en": "It doesn't know or care what any source observes (all opaque SystemContext), only handling who's listed/in what order/how to gather concurrently — so any number of new sources needs zero change"},
                    {"zh": "它自己生成所有上下文内容", "en": "It generates all context content itself"},
                    {"zh": "它指挥模型怎么回答", "en": "It directs how the model answers"},
                    {"zh": "它是个 UI 组件", "en": "It's a UI component"},
                ],
                "answer": 0,
                "why": {"zh": "第 21 课 make 藏起了源的值类型，对注册表每个源都是不透明 SystemContext。它只做纯编排：谁在册、按什么序、怎么并发。编排与内容彻底分离=无限扩展：写多少稀奇的源，注册表一行不改。又是「把会变的与不变的分开」。", "en": "Lesson 21's make hid the source's value type, so to the registry each source is an opaque SystemContext. It does pure orchestration: who's listed, in what order, how concurrent. Orchestration fully separated from content = infinite extension: however many odd sources, the registry needs no change. Again \"separate the variable from the invariant.\""},
            },
        ],
        "open": [
            {"zh": "课里说「凡要被比较、被复现的东西，都不能依赖偶然的顺序」——并发的代价是完成先后不确定，不能让它泄漏到结果。结合你写过的并发代码，举一个「顺序随机泄漏进结果、导致不可复现」的坑。", "en": "The lesson says \"anything to be compared or reproduced must not depend on incidental order\" — concurrency's cost is uncertain completion order, which mustn't leak into the result. From your own concurrent code, give a pitfall where \"order randomness leaked into the result, breaking reproducibility.\""},
            {"zh": "Entry 里的 load 是 Effect<SystemContext>（一段「怎么观察」的描述），而非一个死值。这让每次 load() 都重新观察、拿到最新环境。如果改成注册时就存死一个值，会丢失什么能力？", "en": "An Entry's load is Effect<SystemContext> (a description of \"how to observe\"), not a dead value. This makes each load() re-observe, getting the latest environment. If you instead stored a fixed value at registration time, what ability would you lose?"},
        ],
    },
    "24-context-epoch.html": {
        "mcq": [
            {
                "q": {"zh": "上下文纪元里的 baseline_seq 是什么、为什么重要？", "en": "What is baseline_seq in the context epoch, and why does it matter?"},
                "opts": [
                    {"zh": "把基线钉在会话时间线某序号的图钉——正是第 19 课 history.load 给历史窗口裁边那条线", "en": "The pin nailing the baseline at a sequence on the session timeline — exactly Lesson 19's history.load history-window edge-trim line"},
                    {"zh": "一个随机生成的会话 ID", "en": "A randomly generated session ID"},
                    {"zh": "模型的版本号", "en": "The model's version number"},
                    {"zh": "token 计数", "en": "A token count"},
                ],
                "answer": 0,
                "why": {"zh": "纪元确立基线时钉下 baseline_seq：往前的历史被基线全文概括、history.load 不逐条读，往后才是真正的对话。它一头连系统上下文、一头连会话历史窗口——是上下文系统与会话引擎缝合的那一针，合上了第 19 课的伏笔。", "en": "The epoch nails baseline_seq when establishing the baseline: history before it is summarized by the baseline text (history.load skips reading each), after it is the real conversation. One end connects system context, the other the history window — the stitch joining the context system and session engine, closing Lesson 19's hook."},
            },
            {
                "q": {"zh": "reconcile 发现环境变了，prepare 怎么记录这次变化？", "en": "When reconcile finds the environment changed, how does prepare record it?"},
                "opts": [
                    {"zh": "publish 一条 ContextUpdated 事件（带差异文本）——上下文变化也是会话历史里的正式事件", "en": "Publish a ContextUpdated event (with diff text) — a context change is also a formal event in the session history"},
                    {"zh": "直接改 baseline 字段", "en": "Directly edit the baseline field"},
                    {"zh": "打印到日志", "en": "Print to a log"},
                    {"zh": "什么都不做", "en": "Do nothing"},
                ],
                "answer": 0,
                "why": {"zh": "Updated 不是改字段，而是 publish(SessionEvent.ContextUpdated, {text: 差异})。于是模型下一轮重读历史自然读到这条更新、无缝衔接。且发事件与推进 revision/存快照绑成原子 commit——「先持久、再推进」，系统上下文的演进本身就是事件溯源的一部分（呼应第 14、15 课）。", "en": "Updated isn't editing a field but publish(SessionEvent.ContextUpdated, {text: diff}). So the model rereads it naturally next round, seamlessly. And the publish is bound atomically with advancing revision/storing snapshot — \"persist first, advance later\"; system context's evolution is itself part of event sourcing (echoing Lessons 14, 15)."},
            },
            {
                "q": {"zh": "为什么「换 agent」走 replace（重立纪元）而非当成普通的 Updated？", "en": "Why does \"switch agent\" take replace (re-establish epoch) rather than count as an ordinary Updated?"},
                "opts": [
                    {"zh": "agent 决定整份上下文的「人设」和规矩，变化太根本，需掀掉旧基线重立——而非在旧基线上补增量", "en": "The agent determines the whole context's \"persona\" and rules; the change is too fundamental, needing to tear down and re-establish the baseline — not append an increment onto the old one"},
                    {"zh": "因为 agent 字段更长", "en": "Because the agent field is longer"},
                    {"zh": "为了删除旧会话", "en": "To delete the old session"},
                    {"zh": "没有区别，只是代码风格", "en": "No difference, just code style"},
                ],
                "answer": 0,
                "why": {"zh": "agent 不是环境里普通字段，它决定该强调什么、带什么指令。同一目录同一时间，换个 agent 来看可能面目全非——不是「补一句增量」能表达的，需重立基线（像登山换队伍要另立大本营）。把同 agent 演进(reconcile)与换 agent 改朝换代(replace)分两条路，是对「变化有大小」的清醒。", "en": "The agent isn't an ordinary field; it decides what to emphasize and which instructions to carry. Same dir, same time, a different agent may see something utterly different — not expressible as \"append an increment,\" needing re-establishment (like a new mountaineering team pitching a new base camp). Splitting same-agent evolution (reconcile) from agent-switch changing-of-the-guard (replace) is clarity about \"changes come in sizes.\""},
            },
        ],
        "open": [
            {"zh": "课里说上下文纪元让「上下文」和「对话」共享同一套持久化、同一条事件流、同一条裁边线——「不是两个系统勉强对接，而是一个系统的两个侧面」。对比「把系统上下文做成独立小模块、每轮临时拼一段塞进 prompt」，后者会丢失什么？", "en": "The lesson says the context epoch makes \"context\" and \"conversation\" share one persistence, one event stream, one edge-trim line — \"not two systems forced to connect, but two sides of one system.\" Compared to \"making system context a standalone module, stitching a bit into the prompt each round,\" what does the latter lose?"},
            {"zh": "revision 是个乐观并发版本号，prepare 外套 retryRevisionMismatch：两处并发更新同一会话纪元时比对版本、退让重试，绝不盲目覆盖。这道防线和第 16 课「同会话串行」有何不同、又如何互补？", "en": "revision is an optimistic-concurrency version number, with prepare wrapped in retryRevisionMismatch: two concurrent updates to the same session's epoch compare versions, back off and retry, never blindly overwriting. How does this defense differ from and complement Lesson 16's \"serial within a session\"?"},
        ],
    },
    "25-mid-conversation.html": {
        "mcq": [
            {
                "q": {"zh": "第 24 课的 ContextUpdated 事件，最终以什么形式抵达模型？", "en": "In what form does Lesson 24's ContextUpdated event ultimately reach the model?"},
                "opts": [
                    {"zh": "被投影成一条 System 消息，按 seq 原位插在它发生的那个时间点", "en": "Projected into a System message, inserted in place by seq at the moment it happened"},
                    {"zh": "拼到 system prompt 最前面", "en": "Stitched to the front of the system prompt"},
                    {"zh": "打印到服务器日志", "en": "Printed to the server log"},
                    {"zh": "通过一个旁路的注入器", "en": "Through a side injector"},
                ],
                "answer": 0,
                "why": {"zh": "System 消息(第 14 课 Message 联合之一)的 text 类型直接复用 ContextUpdated.text。reconcile 的差异文本→ContextUpdated 事件→投影成 System 消息→按 seq 原位落在历史里。一条 System 消息就是一次上下文更新在投影历史里的化身。", "en": "A System message (one of Lesson 14's Message union) reuses ContextUpdated.text as its text type. reconcile's diff → ContextUpdated event → projected into a System message → lands in place by seq. A System message is a context update's avatar in projected history."},
            },
            {
                "q": {"zh": "上下文变化是「什么时候」被注入历史的？", "en": "When exactly is a context change injected into history?"},
                "opts": [
                    {"zh": "懒惰采样、只在「安全 provider-turn 边界」（一次 provider 调用之前、输入提单+工具结清之后）采纳，绝不异步推送", "en": "Sampled lazily, admitted only at a \"safe provider-turn boundary\" (before a provider call, after input promotion + tool settlement), never pushed asynchronously"},
                    {"zh": "源一变就立刻异步推一条进历史", "en": "Pushed into history asynchronously the instant a source changes"},
                    {"zh": "会话结束时一次性补齐", "en": "Filled in all at once when the session ends"},
                    {"zh": "由模型自己决定何时读", "en": "The model decides when to read it"},
                ],
                "answer": 0,
                "why": {"zh": "异步推送会乱套(模型可能正吐字到一半)。opencode 把采样推迟到「下一次 provider 调用之前」这个干净缝隙：先落定刚提单的用户输入/已结清的工具结果，再采样各源变没变→变了就 admit 一条；多源同时变合并成一条。这正是第 15 课 steer「安全边界生效」同一种纪律。", "en": "Async pushing breeds chaos (the model may be mid-stream). opencode defers sampling to the clean gap \"just before the next provider call\": settle just-promoted user input/settled tool results first, then sample whether sources changed → if so admit one; multiple changes at one boundary combine into one. Exactly Lesson 15's steer \"takes effect at a safe boundary\" discipline."},
            },
            {
                "q": {"zh": "为什么 System 消息「原位插入」（而非钉在 prompt 扉页）如此重要？", "en": "Why is the System message being \"inserted in place\" (vs pinned to the prompt's title page) so important?"},
                "opts": [
                    {"zh": "位置承载时机、时机承载意义：原位保住了环境变化何时发生，模型才能理解早先消息的语境", "en": "Position carries timing, timing carries meaning: in-place preserves when the change happened, so the model understands earlier messages' context"},
                    {"zh": "原位插入能省 token", "en": "In-place insertion saves tokens"},
                    {"zh": "为了让历史更短", "en": "To make history shorter"},
                    {"zh": "纯粹是格式好看", "en": "Purely for nice formatting"},
                ],
                "answer": 0,
                "why": {"zh": "msg6「跑测试」时在 /proj，msg7 切到 /src，msg8「再跑」。两次「跑测试」含义可能不同。原位 System 消息让模型看清切换时机；若只钉「当前 /src」在扉页，模型不知它 msg7 才变、就误解了 msg6 的「测试」。位置=时机=意义。还顺带让环境演变史可精确重放。", "en": "At msg6 \"run tests\" in /proj, msg7 cd to /src, msg8 \"again.\" The two may differ. In-place System messages show the model the switch timing; pinning only \"current /src\" at the front, the model doesn't know it changed at msg7 and misreads msg6's \"tests.\" Position=timing=meaning. It also makes the environment's evolution precisely replayable."},
            },
        ],
        "open": [
            {"zh": "课里特别澄清：这里的 System 消息不是开场那段定义 AI 人设的「system prompt」，而是对话进行中随环境变化即时插入的「舞台提示」（开场设定其实落在 baseline）。用「剧本扉页说明 vs 演出中舞台提示」这个比喻，说说为什么前者无所谓位置、后者字字看时机。", "en": "The lesson clarifies: the System message here isn't the opening \"system prompt\" defining the AI's persona, but \"stage directions\" inserted mid-conversation as the environment changes (the opening setup actually lands in the baseline). With the \"title-page note vs mid-show stage direction\" metaphor, explain why the former doesn't care about position while the latter is all about timing."},
            {"zh": "课里说「只要你能把一件事表达成一个带 seq 的事件，它就能自动、原位、可重放地出现在模型读到的历史里」。基于这条，设想一种 opencode 目前没有、但可以用同样方式接入的新「中途信息」，说说它会怎么走这条流水线。", "en": "The lesson says \"as long as you can express something as an event with a seq, it can automatically, in-place, replayably appear in the history the model reads.\" Based on this, imagine a new kind of \"mid-conversation info\" opencode doesn't yet have but could plug in the same way, and describe how it would travel this pipeline."},
        ],
    },
    "26-builtin-sources.html": {
        "mcq": [
            {
                "q": {"zh": "为什么连「日期」都要做成一个带 baseline/update 的源？", "en": "Why is even \"the date\" made a source with baseline/update?"},
                "opts": [
                    {"zh": "因为日期会变——会话可能跨午夜，跨天后 reconcile 自动发更新、把模型的「今天」拨正", "en": "Because the date changes — a session may cross midnight; after crossing, reconcile auto-sends an update, correcting the model's \"today\""},
                    {"zh": "因为日期很重要", "en": "Because the date is important"},
                    {"zh": "为了占满上下文窗口", "en": "To fill up the context window"},
                    {"zh": "纯粹是为了演示框架", "en": "Purely to demo the framework"},
                ],
                "answer": 0,
                "why": {"zh": "会话可能从晚聊到凌晨、跨过午夜。若日期开场写死，过午夜模型的「今天」就错了(把昨天当今天、deadline 算错)。做成源后下轮 reconcile 发现变化、publish 更新「Today's date is now:…」。任何「可能变」的信息都值得用源框架保持新鲜。", "en": "A session may chat from evening into early morning, crossing midnight. Hard-coded at start, past midnight the model's \"today\" is wrong (yesterday as today, miscounted deadline). As a source, next round's reconcile finds the change and publishes \"Today's date is now:…\". Any possibly-changing info deserves staying fresh via the source framework."},
            },
            {
                "q": {"zh": "内置源的定义往往只有十来行，这说明了什么？", "en": "Built-in source definitions are often just a dozen lines — what does this show?"},
                "opts": [
                    {"zh": "好抽象的试金石：复杂被吸进框架，源作者只需声明 key/codec/load/baseline/update 五件本质的事", "en": "The touchstone of good abstraction: complexity absorbed into the framework, the source author declares only five essentials — key/codec/load/baseline/update"},
                    {"zh": "说明这些源功能很弱", "en": "It shows these sources are weak"},
                    {"zh": "说明代码没写完", "en": "It shows the code is unfinished"},
                    {"zh": "说明日期和环境不重要", "en": "It shows date and environment don't matter"},
                ],
                "answer": 0,
                "why": {"zh": "源里没一行写「怎么序列化/注册/排序/并发/持久化/钉序号/投影成 System 消息」——这些全被前五课的框架吸走。作者只答五个本质问题：叫什么/值长啥样/怎么观察/首次怎么说/变了怎么说。加新东西近乎填空=好抽象；反之繁琐=坏抽象。", "en": "No line writes \"how to serialize/register/sort/parallelize/persist/pin-seq/project into a System message\" — all absorbed by the past five lessons' framework. The author answers five essentials: name/value shape/how to observe/first-time/on-change. Adding a thing being near fill-in-the-blank = good abstraction; tedious = bad."},
            },
            {
                "q": {"zh": "core/environment 为什么只挑了目录/项目根/git/平台这四项，而非把所有环境变量都倒给模型？", "en": "Why does core/environment pick only directory/root/git/platform, not dump all environment variables at the model?"},
                "opts": [
                    {"zh": "给模型的上下文贵精不贵多——只给「不给就会做错事」的，多余信息是噪声、挤占 token、分散注意", "en": "Context for the model is about quality not quantity — give only what \"would cause mistakes if omitted\"; extra info is noise, crowds tokens, distracts"},
                    {"zh": "因为其它环境变量读不到", "en": "Because other env vars can't be read"},
                    {"zh": "为了让代码更短", "en": "To make the code shorter"},
                    {"zh": "随便挑的，没有理由", "en": "Picked at random, no reason"},
                ],
                "answer": 0,
                "why": {"zh": "这四项各自影响 agent 决策：工作目录→相对路径算对、项目根→不改项目外文件、is-git→要不要用 git、平台→ls 还是 dir。其余环境变量大多是噪声，只会挤占宝贵上下文、分散模型注意。贵精不贵多，和第 18 课对 token 寸土寸金的敬畏一以贯之。", "en": "Each of the four affects agent decisions: working dir→relative paths, project root→don't edit outside, is-git→whether to use git, platform→ls or dir. Other env vars are mostly noise crowding precious context and distracting. Quality not quantity, of one piece with Lesson 18's reverence for precious tokens."},
            },
        ],
        "open": [
            {"zh": "课里说 core 内置源和「将来插件贡献的源」站在完全平等的位置（dogfooding/吃自家狗粮）——框架作者自己就靠它过日子，扩展点就不可能是二等的。为什么「自己人和外人吃同一套机制」是扩展机制健康的最好证明？", "en": "The lesson says core built-in sources stand on equal footing with \"sources future plugins contribute\" (dogfooding) — the framework authors live on it themselves, so the extension point can't be second-class. Why is \"insiders and outsiders using the same mechanism\" the best proof of a healthy extension mechanism?"},
            {"zh": "课里赞赏 baseline/update 用「now」一词的差别去暗示「这是变化」——一个几乎没人会注意的细节。结合你用过的工具/读过的提示，举一个「为读者（哪怕是 AI）多花一点心思的措辞」让体验明显变好的例子。", "en": "The lesson praises baseline/update using the word \"now\" to hint \"this is a change\" — a detail almost no one notices. From tools you've used or prompts you've read, give an example where \"a bit more care in wording for the reader (even an AI)\" noticeably improved the experience."},
        ],
    },
    "27-agent-switch-epoch.html": {
        "mcq": [
            {
                "q": {"zh": "为什么换 agent 时 SystemContext.replace 会因「某个源 unavailable」而 block？", "en": "Why does SystemContext.replace block on \"a source unavailable\" when switching agents?"},
                "opts": [
                    {"zh": "新基线要从零重建、没有旧快照保底；某源曾经有现在却看不到，硬拼等于悄悄把它从新 agent 的世界抹掉", "en": "The new baseline rebuilds from scratch with no old-snapshot fallback; a source once present now unseen, forcing it through would silently erase it from the new agent's world"},
                    {"zh": "因为 replace 太慢", "en": "Because replace is too slow"},
                    {"zh": "因为 agent 不允许切换", "en": "Because agents can't be switched"},
                    {"zh": "为了节省内存", "en": "To save memory"},
                ],
                "answer": 0,
                "why": {"zh": "reconcile（同 agent）容忍源暂缺——保住旧快照即可。但 replace 拼全新基线、没有旧快照保底，每个源必须当场新鲜观察到。若某源「曾经有、现在却 unavailable」，硬拼会把它抹掉、新 agent 误以为「这里不是 git 仓库」。宁可 block 也不交付残缺基线——第 21 课 unavailable≠removed 的终极兑现。", "en": "reconcile (same agent) tolerates a missing source — keep the old snapshot. But replace stitches a brand-new baseline with no fallback; every source must be freshly observed now. If a source is \"once present, now unavailable,\" forcing it erases it, the new agent wrongly thinks \"not a git repo.\" Rather block than deliver an incomplete baseline — the ultimate cash-out of Lesson 21's unavailable≠removed."},
            },
            {
                "q": {"zh": "为什么同样是「一个源没读到」，reconcile 当小事、replace 当大事？", "en": "Why is the same \"a source unread\" trivial for reconcile but grave for replace?"},
                "opts": [
                    {"zh": "reconcile 站在已有基线肩上(旧快照是安全网)；replace 是从零奠基，缺一块就把残缺焊进地基", "en": "reconcile stands on an existing baseline (old snapshot as safety net); replace lays a foundation from scratch, missing a piece welds the gap into the bedrock"},
                    {"zh": "因为 replace 用的模型不同", "en": "Because replace uses a different model"},
                    {"zh": "因为 reconcile 不读源", "en": "Because reconcile doesn't read sources"},
                    {"zh": "没有区别", "en": "There's no difference"},
                ],
                "answer": 0,
                "why": {"zh": "增量更新缺一笔，晚补一轮即可，基线始终完整；奠基时缺一块，是把残缺焊进地基，往后每轮都带这缺口。「打地基」和「添砖加瓦」根本不是一回事——opencode 区别对待，正是看透了这点。", "en": "An increment missing one entry catches up a round later, the baseline always complete; laying a foundation missing a piece welds the gap into the bedrock, carried every round after. \"Laying a foundation\" and \"adding bricks\" are fundamentally different — opencode treating them differently is exactly seeing through this."},
            },
            {
                "q": {"zh": "fence + revision 在 agent 切换里扮演什么角色？", "en": "What role do fence + revision play in agent switching?"},
                "opts": [
                    {"zh": "写入前核对 agent/版本，不符则退让重试——保证切换原子一致，绝无半切错乱的纪元", "en": "Double-check agent/version before write, mismatch → back off and retry — ensuring an atomic, consistent switch, never a half-switched garbled epoch"},
                    {"zh": "加快切换速度", "en": "Speed up the switch"},
                    {"zh": "阻止所有切换", "en": "Block all switches"},
                    {"zh": "记录切换日志", "en": "Log the switch"},
                ],
                "answer": 0,
                "why": {"zh": "fence 写入前再核对：当前 agent 还是我以为的吗？revision 还是我读到的吗？有一样不符=有人在我盘算时动过手→die RevisionMismatch/AgentMismatch→外层 retryRevisionMismatch 退让重试。乐观并发确保两处并发切换最终只一次干净落定。", "en": "fence rechecks before write: is the current agent still what I thought? is revision still what I read? Any mismatch = someone acted while I planned → die RevisionMismatch/AgentMismatch → outer retryRevisionMismatch backs off and retries. Optimistic concurrency ensures two concurrent switches settle just once, cleanly."},
            },
        ],
        "open": [
            {"zh": "课里说 opencode 守着两道防线：block 防残缺、fence 防错乱，都指向「纪元要么完整一致地建立、要么不动」。结合「可靠系统 vs 能跑的脚本」之分，说说为什么「异常情况下能优雅地什么都不破坏」比「正常情况能跑通」更难、更值钱。", "en": "The lesson says opencode keeps two defenses: block against incompleteness, fence against garbling, both pointing to \"an epoch is either established completely and consistently, or not touched.\" With the \"reliable system vs script that runs\" divide, explain why \"gracefully breaking nothing in the abnormal case\" is harder and more valuable than \"running in the normal case.\""},
            {"zh": "第 21 课那个 unavailable≠removed 原则，当时看像无关痛痒的设计洁癖，六课后却在「换 agent」这个最关键场景结出最重要的果实。回顾你读过的代码/系统，举一个「当初一个不起眼的克制，后来成了关键能力」的例子。", "en": "Lesson 21's unavailable≠removed principle seemed like inconsequential fastidiousness then, yet six lessons later bears its most important fruit in the critical \"switch agent\" scenario. From code/systems you've read, give an example where \"an early, unremarkable bit of restraint later became a key capability.\""},
        ],
    },
    "28-llm-overview.html": {
        "mcq": [
            {
                "q": {"zh": "opencode 的 core 怎么和各说各话的模型供应商打交道？", "en": "How does opencode's core deal with model providers that each speak their own tongue?"},
                "opts": [
                    {"zh": "core 只说一种规范语言（LLMRequest/LLMEvent），一层协议适配器翻成各家方言、再翻回来", "en": "Core speaks only one canonical language (LLMRequest/LLMEvent); a protocol-adapter layer translates to each dialect and back"},
                    {"zh": "core 里到处 if (provider === ...) 分别处理", "en": "core handles each with if (provider === ...) everywhere"},
                    {"zh": "只支持一家供应商", "en": "Supports only one provider"},
                    {"zh": "让模型自己适配", "en": "Lets the model adapt itself"},
                ],
                "answer": 0,
                "why": {"zh": "经典「反腐层」：core 和外部供应商之间砌一道翻译墙。core 永远说规范语（出去 LLMRequest、回来 LLMEvent 流），适配器把它翻成各家方言、把回话翻回规范事件。墙内 agent 循环对供应商一无所知——第 17 课那句 llm.stream 消费的就是规范 LLMEvent。", "en": "Classic anti-corruption layer: a translation wall between core and external providers. Core always speaks canonical (outbound LLMRequest, inbound LLMEvent stream), adapters translate to each dialect and replies back to canonical events. The agent loop inside knows nothing of the provider — Lesson 17's llm.stream consumes exactly these canonical LLMEvents."},
            },
            {
                "q": {"zh": "「协议（protocol）」和「供应商（provider）」的区别是？", "en": "What's the difference between a \"protocol\" and a \"provider\"?"},
                "opts": [
                    {"zh": "协议=线缆格式(请求/响应具体长啥样,6 种)；供应商=具体厂商(用哪种协议+认证+端点)，二者多对多", "en": "Protocol = wire format (what request/response look like, 6 of them); provider = specific vendor (which protocol + auth + endpoint); many-to-many"},
                    {"zh": "协议是新的、供应商是旧的", "en": "Protocols are new, providers are old"},
                    {"zh": "两者完全一样", "en": "They are identical"},
                    {"zh": "协议是付费的、供应商是免费的", "en": "Protocols are paid, providers are free"},
                ],
                "answer": 0,
                "why": {"zh": "协议像插头制式、供应商像具体电器：一种制式插一堆电器，一台电器也可能支持两种制式。OpenAI Chat 协议不只 OpenAI 用，一堆「OpenAI 兼容」厂商都借它说话；OpenAI 自己又有 Chat+Responses 两套。解耦二者→6 种协议复用覆盖十几家供应商，少量协议大量复用。", "en": "Protocol is like a plug standard, provider like a specific appliance: one standard fits many appliances, one appliance may support two standards. The OpenAI Chat protocol isn't used only by OpenAI but by many \"OpenAI-compatible\" vendors; OpenAI itself has both Chat and Responses. Decoupling → 6 protocols reusably cover a dozen-plus providers."},
            },
            {
                "q": {"zh": "为什么 OpenAI-Compatible 这一种协议特别有杠杆？", "en": "Why is the OpenAI-Compatible protocol especially high-leverage?"},
                "opts": [
                    {"zh": "「OpenAI 兼容」已是事实标准，实现一次就免费搭上整个生态(OpenRouter/xAI/本地模型…)，新厂商无需加代码", "en": "\"OpenAI-compatible\" is a de facto standard; implementing it once free-rides the whole ecosystem (OpenRouter/xAI/local models…), new vendors needing no new code"},
                    {"zh": "因为它跑得最快", "en": "Because it runs fastest"},
                    {"zh": "因为它最便宜", "en": "Because it's cheapest"},
                    {"zh": "因为它是 OpenAI 官方的", "en": "Because it's OpenAI official"},
                ],
                "answer": 0,
                "why": {"zh": "市面上一大票厂商自称「OpenAI 兼容」、API 形态几乎一样。把这套线缆格式抽成一个协议，opencode 实现一次，所有这些厂商都自动接上——它们数量还在涨，opencode 一行新协议代码都不用加。这就是「把线缆格式抽象成协议」的复利。", "en": "A crowd of vendors claim \"OpenAI compatibility\" with near-identical API forms. Abstracting this wire format into one protocol, opencode implements it once and all of them auto-connect — their number grows while opencode adds not a line of new protocol code. That's the compound interest of abstracting the wire format into a protocol."},
            },
        ],
        "open": [
            {"zh": "课里把「一种规范语言」和第 12 课「用 OpenAPI 规范解耦前后端」说成同一种智慧：中间立一份双方都认的契约，两端就都获得不被对方绑架的自由。结合你做过的集成，说一个「中间立契约，两端各自演化」让你受益（或缺它而受苦）的例子。", "en": "The lesson calls \"one canonical language\" the same wisdom as Lesson 12's \"decouple front/back ends with an OpenAPI spec\": stand a contract both sides honor in the middle, both ends gain freedom from being held hostage. From an integration you've done, give an example where \"a middle contract letting both ends evolve\" benefited you (or its absence hurt)."},
            {"zh": "课里给了一条判断法则：「凡是『这家供应商怎么怎么样』的知识，都只该住在 llm 包里；一旦泄漏进 core，就是一处设计破窗」。为什么把这种知识的「物理位置」管住，比口头约定「大家别在 core 里写供应商特判」更可靠？", "en": "The lesson gives a rule of thumb: \"any 'how this provider behaves' knowledge should live only in the llm package; once it leaks into core, that's a broken window.\" Why is controlling the physical location of such knowledge more reliable than a verbal agreement \"let's not write provider special-cases in core\"?"},
        ],
    },
    "29-protocol-adapters.html": {
        "mcq": [
            {
                "q": {"zh": "Protocol 接口（route/protocol.ts）长什么样？", "en": "What does the Protocol interface (route/protocol.ts) look like?"},
                "opts": [
                    {"zh": "一张两栏表：body（请求侧，把规范请求编码成这家请求体）+ stream（响应侧，一台把流式响应解码回规范事件的状态机）", "en": "A two-column form: body (request side, encode canonical request into this body) + stream (response side, a state machine decoding the streaming response back into canonical events)"},
                    {"zh": "一个超大函数，把所有供应商的逻辑写在一起", "en": "One giant function with all providers' logic together"},
                    {"zh": "只有一个 send() 方法", "en": "Just a single send() method"},
                    {"zh": "一堆 if (provider === ...) 分支", "en": "A pile of if (provider === ...) branches"},
                ],
                "answer": 0,
                "why": {"zh": "接口干净得像张表，只有两块：body 管「出去」、stream 管「回来」。body 就一个 from(LLMRequest)→Body 函数加一个 schema；stream 是 initial/event/step/terminal?/onHalt? 五件套的状态机。所有协议都填这同一张表——认清它，第 30~32 课就只是「同一张表的不同方言填法」。", "en": "The interface is clean as a table, just two blocks: body owns \"out,\" stream owns \"back.\" body is one from(LLMRequest)→Body function plus a schema; stream is a five-part state machine (initial/event/step/terminal?/onHalt?). Every protocol fills this same form — grasp it and lessons 30–32 are just \"the same form filled in different dialects.\""},
            },
            {
                "q": {"zh": "为什么请求侧只是一个函数，响应侧却是一台状态机？", "en": "Why is the request side just a function, but the response side a state machine?"},
                "opts": [
                    {"zh": "请求是静态的、一次性拼好整个发出；响应是流式碎片到达（如工具参数 JSON 跨多帧），必须边收边攒、记住「目前到哪了」", "en": "A request is static, assembled and sent whole at once; a response arrives as streaming fragments (e.g. tool-arg JSON across frames), so you must accumulate as you receive, remembering \"where you are so far\""},
                    {"zh": "纯属历史包袱，没有道理", "en": "Pure legacy baggage, no reason"},
                    {"zh": "因为响应比请求大", "en": "Because responses are bigger than requests"},
                    {"zh": "为了让代码更长", "en": "To make the code longer"},
                ],
                "answer": 0,
                "why": {"zh": "这个不对称忠实映射现实。请求在你按下发送时就尘埃落定，一个 from 函数足矣。响应却是模型流式吐回：一个工具调用的参数 JSON 跨好几帧才到齐——你收到「{\\\"path\\\":」这半截时无从处理，必须用 State 当草稿纸攒着，等拼齐再吐出完整事件。step(State,Event)→[State, LLMEvent[]] 正是为此。", "en": "The asymmetry faithfully maps reality. A request is settled the moment you hit send — one from function suffices. But a response streams back: one tool call's argument JSON arrives across several frames — receiving the half \"{\\\"path\\\":\" leaves you nothing to do, you must use State as scratch paper, accumulate, and emit a whole event only once assembled. step(State,Event)→[State, LLMEvent[]] exists exactly for this."},
            },
            {
                "q": {"zh": "Protocol.make 的实现是 (input) => input，一个恒等函数。它为什么存在？", "en": "Protocol.make is implemented as (input) => input, an identity function. Why does it exist?"},
                "opts": [
                    {"zh": "作为一个「类型化接缝」：今天什么都不做，但为将来给所有协议统一加横切关注点（如 tracing）预留唯一入口", "en": "As a \"typed seam\": doing nothing today, but reserving a single entry point to later add cross-cutting concerns (like tracing) across all protocols at once"},
                    {"zh": "它会校验并修正请求体", "en": "It validates and fixes the request body"},
                    {"zh": "它负责发送 HTTP 请求", "en": "It sends the HTTP request"},
                    {"zh": "它是个 bug，应该删掉", "en": "It's a bug and should be deleted"},
                ],
                "answer": 0,
                "why": {"zh": "源码注释说得明白：schema 和解析函数才是真理之源，make 不做运行时的事。但留这个壳是克制的远见——将来想给六个协议统一加一层（tracing、instrumentation）时，有唯一下手处，不必去改每个协议的定义。一个今天什么都不做的恒等函数，是为明天的「统一改造」留的门。", "en": "The source comment is explicit: the schemas and parser functions are the source of truth, make does nothing at runtime. But leaving this shell is restrained foresight — when you later want to add one layer (tracing, instrumentation) across six protocols, there's a single place to do it, without touching each protocol's definition. An identity function doing nothing today is a door left open for tomorrow's unified retrofit."},
            },
        ],
        "open": [
            {"zh": "stream.step 的签名是 (State, Event) => [State, LLMEvent[]]——它把「新状态」一并返回，而不是偷偷改一个全局变量。结合本课的工具调用例子（参数跨帧到齐），说说「显式传递状态」相比「就地修改」，给这台流式解码状态机带来了什么好处（提示：可预测性、可测试性、并发）。", "en": "stream.step's signature is (State, Event) => [State, LLMEvent[]] — it returns the \"new state\" alongside, rather than secretly mutating a global. Using this lesson's tool-call example (arguments arriving across frames), discuss what \"explicitly threading state\" buys this streaming-decode state machine over \"in-place mutation\" (hint: predictability, testability, concurrency)."},
            {"zh": "本课说六种协议「要解决的问题是同构的」，于是用一个 Protocol 接口钉成一张所有协议都填的表。回想你接触过的「多个后端/多种格式但本质同构」的场景（如多种支付渠道、多种导出格式），如果当初也抽出这样一张「统一接口表」，会让新增一种渠道/格式变得多容易？反过来，没抽会怎样？", "en": "This lesson says the six protocols solve an \"isomorphic problem,\" so it nails them into one Protocol interface every protocol fills. Recall a \"many backends/formats but essentially isomorphic\" scenario you've met (e.g. multiple payment channels, multiple export formats). Had you abstracted such a \"unified interface form,\" how much easier would adding a new channel/format become? Conversely, what happens without it?"},
        ],
    },
    "30-anthropic-protocol.html": {
        "mcq": [
            {
                "q": {"zh": "Anthropic 协议里，系统提示（system）是怎么摆的？", "en": "In the Anthropic protocol, how is the system prompt placed?"},
                "opts": [
                    {"zh": "请求体顶层一个独立字段（文本块数组），不是 messages 里的一条消息——区别于 OpenAI 把它当首条 role:system 消息", "en": "A separate top-level field of the request body (text-block array), not a message in messages — unlike OpenAI treating it as the first role:system message"},
                    {"zh": "和普通用户消息完全一样，混在 messages 里", "en": "Exactly like a normal user message, mixed into messages"},
                    {"zh": "Anthropic 不支持系统提示", "en": "Anthropic doesn't support system prompts"},
                    {"zh": "放在 HTTP 请求头里", "en": "Put in an HTTP header"},
                ],
                "answer": 0,
                "why": {"zh": "这正是「协议即方言」最直观的例子：同一个规范 system，Anthropic 的 body.from 把它摆成顶层 system 字段（文本块数组），OpenAI 那份却把它摆成 messages 数组的头一条。core 只有一份不带口音的 system，谁把它摆哪、是适配器在默默吸收的差异。", "en": "This is the most vivid example of \"protocol = dialect\": the same canonical system, Anthropic's body.from places as a top-level system field (text-block array), while OpenAI's places it as the first entry of the messages array. core has only one accent-free system; who places it where is the difference the adapter quietly absorbs."},
            },
            {
                "q": {"zh": "Anthropic 的「4 个缓存断点上限」，opencode 的 lowering 层怎么应对？", "en": "How does opencode's lowering layer handle Anthropic's \"4 cache-breakpoint cap\"?"},
                "opts": [
                    {"zh": "带一个可变计数器 Breakpoints{remaining,dropped} 穿过所有 lower*，每打一个标记 remaining--，超额就 dropped++ 悄悄放弃（不打、不报错）", "en": "Thread a mutable counter Breakpoints{remaining,dropped} through all lower*; each marker does remaining--, and past the cap does dropped++ and quietly gives up (no marker, no error)"},
                    {"zh": "打满 5 个，让 API 自己报 400", "en": "Emit 5 and let the API throw 400 itself"},
                    {"zh": "从不打任何缓存标记", "en": "Never emit any cache marker"},
                    {"zh": "随机丢弃一半标记", "en": "Randomly drop half the markers"},
                ],
                "answer": 0,
                "why": {"zh": "Anthropic 每请求最多 4 个 cache_control 断点（跨 tools/system/messages 合计），第 5 个直接 400。opencode 从源头杜绝：一个共享的可变计数器穿过 lower*，按 tools→system→messages 次序消耗名额（越靠前缀越优先），用完后超额的标记只 dropped++ 然后返回 undefined。缓存是优化，不该因「想多缓存」把请求搞挂——所以悄悄丢，不报错。", "en": "Anthropic allows at most 4 cache_control breakpoints per request (counted across tools/system/messages); a 5th 400s outright. opencode kills it at the source: a shared mutable counter threads through lower*, consuming slots in tools→system→messages order (prefix-y parts prioritized), and past the cap excess markers just dropped++ then return undefined. Caching is an optimization, it shouldn't break the request for \"wanting more cache\" — so drop silently, no error."},
            },
            {
                "q": {"zh": "「4 断点 + TTL 两档」的缓存逻辑被抽到 utils/cache.ts 共享，为什么？", "en": "The \"4-breakpoint + two-TTL-bucket\" cache logic is hoisted into utils/cache.ts to be shared. Why?"},
                "opts": [
                    {"zh": "因为 Bedrock 上的 Claude 吃同一套规矩——同一供应商约束被两个协议复用，抽出共性免得写两遍", "en": "Because Claude on Bedrock eats the same rules — one provider constraint reused by two protocols, factor out the commonality to avoid writing it twice"},
                    {"zh": "纯粹为了让文件更多", "en": "Purely to have more files"},
                    {"zh": "因为缓存逻辑必须放在 utils 目录", "en": "Because cache logic must live in a utils directory"},
                    {"zh": "为了让 Anthropic 协议更短", "en": "To make the Anthropic protocol shorter"},
                ],
                "answer": 0,
                "why": {"zh": "Anthropic 和 Bedrock 上的 Claude 共享同一套缓存约束（4 上限、5m/1h 两档 TTL）。把计数器和 TTL 映射抽到 utils/cache.ts，两个协议都引它——又一处「把共性抽出来」的复利，和第 28 课 OpenAI-Compatible 协议复用、第 31 课 Chat/Responses 共享，是同一种省力智慧。", "en": "Anthropic and Claude-on-Bedrock share the same cache constraint (4-cap, 5m/1h TTL buckets). Hoisting the counter and TTL mapping into utils/cache.ts lets both protocols import it — another instance of \"factor out the commonality\" compounding, the same labor-saving wisdom as lesson 28's OpenAI-Compatible reuse and lesson 31's Chat/Responses sharing."},
            },
        ],
        "open": [
            {"zh": "课里点出一处「天作之合」：Anthropic 的缓存断点，和第 24 课 Context Epoch 拼命维持的「基线前缀稳定」严丝合缝——前缀稳，缓存才持续命中，省下真金白银。请你顺着这条线，说说为什么「让 prompt 的前缀尽量不变」会同时利好「缓存命中率」和「省钱」；如果上层频繁改写前缀（比如每轮都往最前面插一句变化的内容），会发生什么？", "en": "The lesson points out a \"match made in heaven\": Anthropic's cache breakpoints dovetail with lesson 24's Context Epoch effort to keep the \"baseline prefix stable\" — a stable prefix means the cache keeps hitting, saving hard cash. Follow this thread: explain why \"keeping the prompt's prefix as unchanged as possible\" benefits both \"cache hit rate\" and \"cost.\" If the upper layer frequently rewrites the prefix (e.g. inserting a changing line at the very front each turn), what happens?"},
            {"zh": "课里对比了两种状态管理：第 29 课的 stream.step「显式传新状态」，本课缓存预算的 Breakpoints「就地修改一个共享计数器」。课文说前者图「可预测、可重放」，后者图「一趟性的直白」。结合这两个场景，谈谈你判断「该用不可变显式传递，还是该用可变就地修改」的标准是什么？", "en": "The lesson contrasts two styles of state management: lesson 29's stream.step \"threads new state explicitly,\" while this lesson's cache budget Breakpoints \"mutates a shared counter in place.\" The text says the former seeks \"predictability and replayability,\" the latter \"single-pass directness.\" Using these two scenarios, discuss your criteria for deciding \"immutable explicit threading vs mutable in-place modification.\""},
        ],
    },
    "31-openai-protocol.html": {
        "mcq": [
            {
                "q": {"zh": "为什么 OpenAI 在 opencode 里独占两份协议文件（openai-chat 和 openai-responses）？", "en": "Why does OpenAI uniquely take two protocol files in opencode (openai-chat and openai-responses)?"},
                "opts": [
                    {"zh": "OpenAI 的 API 正从老的 Chat Completions 迁移到新的 Responses，两者都还活着、都有人用，opencode 两边都支持", "en": "OpenAI's API is migrating from the old Chat Completions to the new Responses; both are alive and used, so opencode supports both"},
                    {"zh": "纯属代码冗余，应该合并", "en": "Pure code redundancy that should be merged"},
                    {"zh": "一份给付费用户、一份给免费用户", "en": "One for paid users, one for free users"},
                    {"zh": "一份处理请求、一份处理响应", "en": "One handles requests, one handles responses"},
                ],
                "answer": 0,
                "why": {"zh": "这不是冗余，而是忠实反映现实：OpenAI 正处在 Chat→Responses 的 API 迁移途中。Chat（/chat/completions）是用了多年、被当成事实标准的老接口；Responses（/responses）是更强大的新接口（带类型条目、推理一等公民、服务端状态）。两者都有人用，opencode 于是两份都填，让用户按模型按需选。", "en": "Not redundancy but a faithful reflection of reality: OpenAI is mid-migration from Chat to Responses. Chat (/chat/completions) is the years-old interface treated as a de facto standard; Responses (/responses) is the more powerful new interface (typed items, first-class reasoning, server-side state). Both are used, so opencode fills both, letting users choose per model."},
            },
            {
                "q": {"zh": "openai-compatible-chat.ts 只有 24 行，它是怎么做到「撑起半个生态」的？", "en": "openai-compatible-chat.ts is only 24 lines; how does it \"prop up half an ecosystem\"?"},
                "opts": [
                    {"zh": "整份复用 OpenAIChat.protocol，只覆盖 route id + 端点路径——编解码一个字不重写，一大票「OpenAI 兼容」厂商即可免费接入", "en": "Reuses OpenAIChat.protocol wholesale, overriding only route id + endpoint path — not a word of codec rewritten, letting a crowd of \"OpenAI-compatible\" vendors connect for free"},
                    {"zh": "它用 AI 自动生成每家厂商的适配代码", "en": "It auto-generates adapter code for each vendor with AI"},
                    {"zh": "它把所有厂商的逻辑压缩进 24 行", "en": "It compresses all vendors' logic into 24 lines"},
                    {"zh": "它只支持 24 家厂商", "en": "It supports only 24 vendors"},
                ],
                "answer": 0,
                "why": {"zh": "因为「协议」和「供应商」解耦（第 28 课），Chat 协议这套通用线缆格式早成事实标准。compatible-chat 整份引用 OpenAIChat.protocol，只改 id 和端点 /chat/completions——请求编码、响应解码全是 Chat 原班人马。于是 OpenRouter/xAI/本地模型…一大票兼容厂商全自动接入，再多一家也只需配端点、协议代码一行不加。这是「协议≠供应商」最掷地有声的现金回报。", "en": "Because \"protocol\" and \"provider\" are decoupled (lesson 28), the Chat protocol's universal wire format long became a de facto standard. compatible-chat references OpenAIChat.protocol wholesale, changing only id and endpoint /chat/completions — request encode and response decode are all the Chat original cast. So OpenRouter/xAI/local models… all auto-connect, and one more needs only an endpoint config, not a line of protocol code. That's the most resounding cash reward of \"protocol ≠ provider.\""},
            },
            {
                "q": {"zh": "Responses 协议的 reasoning 条目带 encrypted_content，它和 Anthropic 的 signature 解决的是同一个什么问题？", "en": "Responses' reasoning item carries encrypted_content; what same problem does it solve as Anthropic's signature?"},
                "opts": [
                    {"zh": "「让模型跨轮信任/延续自己上一轮的推理」——Responses 用加密密文托管、Anthropic 用密码学签名验真，同题异解", "en": "\"Letting the model trust/continue its own prior reasoning across turns\" — Responses via encrypted-ciphertext custody, Anthropic via cryptographic signature verification; same question, different answers"},
                    {"zh": "压缩 token 用量", "en": "Compressing token usage"},
                    {"zh": "加密用户的隐私数据", "en": "Encrypting users' private data"},
                    {"zh": "防止网络中间人攻击", "en": "Preventing network man-in-the-middle attacks"},
                ],
                "answer": 0,
                "why": {"zh": "两家都把「推理」当一等公民，都要让模型在多轮间延续自己的思维链，又都不愿把明文推理直接交给客户端。Responses 给你一团加密 encrypted_content，你原样回传、模型自行解开续上；Anthropic 给推理块盖个 signature 签名，回传时验真。同一个问题、两种方言两种解法——正是「协议即方言」的又一例证。", "en": "Both treat reasoning as first-class, both let the model continue its chain of thought across turns, and both decline to hand plaintext reasoning straight to the client. Responses gives you an encrypted encrypted_content you feed back verbatim for the model to unpack and continue; Anthropic stamps a signature on reasoning blocks, verified on feedback. Same problem, two dialects, two solutions — another instance of \"protocol = dialect.\""},
            },
        ],
        "open": [
            {"zh": "课里有个反直觉的论断：「Chat 协议的『不够先进』，反而成就了它的『无处不在』」——因为越朴素越好模仿，所以遍地是「Chat 兼容」厂商，却几乎没有「Responses 兼容」厂商。结合你见过的技术标准（如 HTTP、JSON、Markdown），谈谈「简单」在一项标准能否成为事实标准里，扮演了多重要的角色？「先进」有时为什么反而是普及的阻力？", "en": "The lesson makes a counterintuitive claim: \"Chat protocol's 'not-advanced-enough' is exactly what made it 'ubiquitous'\"—because the plainer a thing the easier to mimic, so \"Chat-compatible\" vendors are everywhere while \"Responses-compatible\" ones barely exist. Using tech standards you've seen (HTTP, JSON, Markdown), discuss how big a role \"simplicity\" plays in whether a standard becomes de facto. Why is \"advancement\" sometimes a barrier to adoption?"},
            {"zh": "课里强调 Route 与 Protocol 是正交的两层：protocol 管编解码、route 管端点/分帧/认证，于是「换供应商常常只是换端点、复用 protocol」。下一课的 Bedrock 是反例——同样的 Anthropic 方言，却因传输/认证走 AWS 而需另一份协议。请你想象：如果当初没有把 protocol 和 route 拆开，而是把端点、认证都写死在协议里，新增「OpenAI 兼容」厂商和「Bedrock 上的 Claude」会分别变得多痛苦？", "en": "The lesson stresses Route and Protocol are orthogonal: protocol owns codec, route owns endpoint/framing/auth, so \"switching providers is often just switch endpoint, reuse protocol.\" Next lesson's Bedrock is a counterexample—the same Anthropic dialect, yet needing another protocol because transport/auth go via AWS. Imagine: had protocol and route not been split, with endpoint and auth hardcoded into the protocol, how painful would adding an \"OpenAI-compatible\" vendor and \"Claude on Bedrock\" each become?"},
        ],
    },
    "32-gemini-bedrock.html": {
        "mcq": [
            {
                "q": {"zh": "「让模型跨轮信任自己上一轮的推理」，三大供应商各起了什么名字？", "en": "For \"letting the model trust its own prior reasoning across turns,\" what did the three big vendors each name it?"},
                "opts": [
                    {"zh": "Anthropic 叫 signature、OpenAI Responses 叫 encrypted_content、Gemini 叫 thoughtSignature——同一概念三家三个名字", "en": "Anthropic calls it signature, OpenAI Responses encrypted_content, Gemini thoughtSignature — one concept, three names"},
                    {"zh": "三家都叫 signature", "en": "All three call it signature"},
                    {"zh": "三家都不支持这个功能", "en": "None of the three support this"},
                    {"zh": "三家都叫 reasoning_token", "en": "All three call it reasoning_token"},
                ],
                "answer": 0,
                "why": {"zh": "这是「协议即方言」最直观的注脚：能力几乎一样（都让模型延续思维链、都不把明文推理直接给客户端），叫法却三家三样——signature（密码学签名验真）/ encrypted_content（加密密文托管）/ thoughtSignature（思考签名）。core 只认一套规范名，全靠各家 body.from 把这些异名翻译过去。", "en": "This is the most vivid footnote to \"protocol = dialect\": near-identical capability (all let the model continue its chain of thought, none hand plaintext reasoning straight to the client), yet three different names—signature (cryptographic verification) / encrypted_content (encrypted custody) / thoughtSignature (thought signature). core knows only one canonical set of names; each vendor's body.from translates these aliases over."},
            },
            {
                "q": {"zh": "Bedrock 上跑的就是 Claude、方言几乎等同 Anthropic，为什么还要单独写一份协议、不能像 openai-compatible 那样几行复用？", "en": "Bedrock runs Claude with a dialect nearly identical to Anthropic, so why a separate protocol instead of a few-line reuse like openai-compatible?"},
                "opts": [
                    {"zh": "因为传输方式不同：Anthropic 官方用 SSE 文本流，Bedrock 用 AWS 二进制事件流，framing（分帧）必须换——方言可复用，但拆帧的机器不同", "en": "Because the transport differs: Anthropic official uses SSE text streams, Bedrock uses AWS binary event streams, so framing must change — the dialect is reusable but the frame-cutting machine differs"},
                    {"zh": "因为 Bedrock 上的 Claude 是不同的模型", "en": "Because Claude on Bedrock is a different model"},
                    {"zh": "因为 AWS 要求每家都重写", "en": "Because AWS requires everyone to rewrite"},
                    {"zh": "因为 Bedrock 不支持工具调用", "en": "Because Bedrock doesn't support tool calls"},
                ],
                "answer": 0,
                "why": {"zh": "方言（编解码：块+signature、共享 4 断点缓存）几乎等于 Anthropic，但传输彻底不同：Bedrock 走 AWS 二进制事件流（每帧 [length][headers-length][prelude-crc][headers][payload][crc]），不是 SSE。framing 是 Route 里与 protocol 正交的独立零件，Bedrock 换掉它、其余尽量复用。这正印证第 31 课「方言同、网络异 → 另一份协议」。", "en": "The dialect (codec: blocks+signature, shared 4-breakpoint cache) nearly equals Anthropic, but the transport differs entirely: Bedrock uses AWS binary event stream (each frame [length][headers-length][prelude-crc][headers][payload][crc]), not SSE. framing is an independent part of Route orthogonal to protocol; Bedrock swaps it, reuses the rest. This confirms lesson 31's \"same dialect, different network → another protocol.\""},
            },
            {
                "q": {"zh": "Bedrock framing 的 FrameBufferState{buffer,offset}，在 appendChunk 时为什么要「压缩」丢掉 offset 之前的字节？", "en": "Why does Bedrock framing's FrameBufferState{buffer,offset} \"compact\" away bytes before offset on appendChunk?"},
                "opts": [
                    {"zh": "为了保证有界内存：把已消费、再不用的前缀丢掉，buffer 增长被限制在「最多比活跃窗口多一个网络 chunk」，无论流多长", "en": "To guarantee bounded memory: dropping the consumed, never-again-needed prefix bounds buffer growth to \"at most one network chunk past the active window,\" however long the stream"},
                    {"zh": "为了让代码更短", "en": "To make the code shorter"},
                    {"zh": "为了加密缓冲区内容", "en": "To encrypt the buffer contents"},
                    {"zh": "压缩纯粹是装饰，没有作用", "en": "Compaction is purely decorative, does nothing"},
                ],
                "answer": 0,
                "why": {"zh": "若天真地「只追加不丢弃」，一个传几兆字节的长流会让 buffer 无限膨胀、把整个响应堆进内存。每次 append 顺手扔掉 offset 之前已读完的字节，只留「还没拼成完整帧的活跃窗口」+ 新 chunk，于是内存有上界。读取用零拷贝 subarray、只在 append 分配一次——处理无界流时，这种有界内存的自觉正是生产级代码的标志。", "en": "Naively \"append-only, never drop\" would let a megabyte-long stream grow the buffer unboundedly, piling the whole response into memory. Each append incidentally discards already-read bytes before offset, keeping only \"the active window not yet a full frame\" + the new chunk, so memory is bounded. Reads use zero-copy subarray, allocating only on append — when handling unbounded streams, this bounded-memory awareness is the mark of production-grade code."},
            },
        ],
        "open": [
            {"zh": "课里揭示流式解码是「套娃」的：framing 把字节攒成帧、protocol.stream 把帧攒成事件，两层都是同一个骨架 (state, input) → [state, out]。请你举一个自己写过或见过的「同一个模式在不同抽象层反复出现」的例子（如解析器、网络协议栈、编译器各 pass），并说说「认得这个骨架」是怎么帮你更快读懂陌生代码的。", "en": "The lesson reveals streaming decode is a \"nesting doll\": framing accumulates bytes into frames, protocol.stream accumulates frames into events, both the same skeleton (state, input) → [state, out]. Give an example you've written or seen of \"the same pattern recurring at different abstraction layers\" (e.g. parsers, network protocol stacks, compiler passes), and discuss how \"recognizing this skeleton\" helped you read unfamiliar code faster."},
            {"zh": "课里说 Gemini 的差异「不在能力而在叫法」：functionCall / tool_use / tool_calls 指的是同一件事，\"model\" 和 \"assistant\" 是同一个角色。core 坚持只认一套规范名、让适配器翻译，而不是认全部三套叫法。请论证：为什么「让 N 个外部系统各自适配到 1 套内部规范」，比「让内部认得 N 套外部叫法」更可扩展？当外部供应商从 4 家涨到 40 家时，两种方案的维护成本曲线分别是什么样的？", "en": "The lesson says Gemini's differences are \"not in capability but in naming\": functionCall / tool_use / tool_calls mean the same thing, \"model\" and \"assistant\" are the same role. core insists on one canonical name set and lets adapters translate, rather than knowing all three sets. Argue: why is \"having N external systems each adapt to 1 internal canonical\" more scalable than \"having the internal know N external namings\"? As vendors grow from 4 to 40, what do the two approaches' maintenance-cost curves look like?"},
        ],
    },
    "33-routing-transport.html": {
        "mcq": [
            {
                "q": {"zh": "一次 Route.stream 请求，从规范请求到规范事件，经历的完整流水线是？", "en": "What's the complete pipeline of one Route.stream request, from canonical request to canonical events?"},
                "opts": [
                    {"zh": "①protocol.body.from 编码 → ②endpoint 寻址 → ③auth 签名 → ④transport 取字节流 → ⑤framing 切帧 → ⑥protocol.stream 解码成 LLMEvent", "en": "①protocol.body.from encode → ②endpoint address → ③auth sign → ④transport to byte stream → ⑤framing cut frames → ⑥protocol.stream decode to LLMEvent"},
                    {"zh": "protocol 一个函数直接发请求、收响应、解码，全包了", "en": "protocol does it all in one function: send, receive, decode"},
                    {"zh": "transport 负责编解码，protocol 负责发网络", "en": "transport does codec, protocol does the network"},
                    {"zh": "framing 负责认证，auth 负责切帧", "en": "framing does auth, auth does framing"},
                ],
                "answer": 0,
                "why": {"zh": "①⑥是协议（语言层）的活，②③④⑤是传输基础设施（网络层）的活。两段以「请求体」和「帧」为抽象接口对接：协议吐出/吃进抽象物、不碰网络；基础设施只搬字节、只切帧、不认方言。正是这种干净分工让每段都能单独替换——第 29 课的「两栏表」至此接上了完整上下文，第一次通上电转起来。", "en": "①⑥ are the protocol's (language layer) work, ②③④⑤ the transport infrastructure's (network layer). The two halves interface via \"request body\" and \"frame\" abstractions: protocol emits/eats abstractions, never touching the network; infrastructure only moves bytes and cuts frames, knowing no dialect. This clean division lets each segment be swapped alone — lesson 29's \"two-column form\" now has full context, powered up and spinning for the first time."},
            },
            {
                "q": {"zh": "framing.ts 的注释说「帧的类型对这一层是不透明的」，这句话为什么重要？", "en": "framing.ts's comment says \"the frame type is opaque to this layer\"; why does this matter?"},
                "opts": [
                    {"zh": "因为 framing 只管「把字节切成一份份」、不管每份里装什么，所以同一种分帧（如 SSE）能被任意协议复用，服务 Anthropic/Gemini/OpenAI 三套方言", "en": "Because framing only \"cuts bytes into portions,\" not caring what each holds, so one framing (e.g. SSE) is reusable by any protocol, serving Anthropic/Gemini/OpenAI's three dialects"},
                    {"zh": "因为 framing 会加密帧内容", "en": "Because framing encrypts the frame contents"},
                    {"zh": "因为帧必须是二进制的", "en": "Because frames must be binary"},
                    {"zh": "因为 framing 比 protocol 更重要", "en": "Because framing is more important than protocol"},
                ],
                "answer": 0,
                "why": {"zh": "framing 是「传输与协议之间、字节流形状的那道缝」：接口只有 frame:(字节流)=>(帧流)。它对「帧里是什么」保持无知，于是 SSE 这一种分帧能同时服务三套完全不同的方言——「帧里是什么」是协议 stream.event 解码该操心的。假如没这道缝，「按 data: 空行切」就得在每个协议里各抄一遍，又是第 28 课最忌讳的重复。一道恰当的缝换来上下两层各自的自由。", "en": "framing is \"the byte-stream-shaped seam between transport and protocol\": its interface is just frame:(bytes)=>(frames). It stays ignorant of \"what's in the frame,\" so the single SSE framing serves three wholly different dialects at once — \"what's in the frame\" is the protocol stream.event decode's worry. Without this seam, \"cut by data: blank line\" would be copied into each protocol, again lesson 28's abhorred duplication. A well-placed seam buys both layers their freedom."},
            },
            {
                "q": {"zh": "为什么说一个 Route 是「六个正交旋钮」拼出来的？这对新增供应商意味着什么？", "en": "Why is a Route said to be assembled from \"six orthogonal knobs\"? What does this mean for adding a provider?"},
                "opts": [
                    {"zh": "Route.make 由 id/protocol/endpoint/auth/transport/framing 六个可独立替换的零件组成；新增一家常常只是「给六个旋钮挑一组取值」，复用本质是「只拧一两个旋钮」", "en": "Route.make is six independently-swappable parts: id/protocol/endpoint/auth/transport/framing; adding one is often just \"pick a set of values for the six knobs,\" reuse is essentially \"turn one or two knobs\""},
                    {"zh": "Route 是铁板一块，新增供应商要从头重写", "en": "Route is monolithic; adding a provider means rewriting from scratch"},
                    {"zh": "六个旋钮必须一起改，不能单独动", "en": "All six knobs must change together, none alone"},
                    {"zh": "旋钮越多说明设计越糟", "en": "More knobs means worse design"},
                ],
                "answer": 0,
                "why": {"zh": "六个旋钮各管一维、可独立替换，组合空间却覆盖所有现实供应商。这把前几课的「魔法」全祛魅了：OpenAI 兼容=拨 protocol 到 openai-chat+改 endpoint；Bedrock=把 framing 从 SSE 拨到二进制；Responses WS=把 transport 从 HTTP 拨到 WS。每个聪明复用都是「只拧一两个旋钮、其余照旧」。而类型参数 Frame 在 framing↔protocol 接缝强制对齐——正交但不放任，自由组合+类型兜底。", "en": "Six knobs each own one dimension, independently swappable, yet the combination space covers all real providers. This demystifies prior lessons' \"magic\": OpenAI-compatible = turn protocol to openai-chat + change endpoint; Bedrock = turn framing from SSE to binary; Responses WS = turn transport from HTTP to WS. Each clever reuse is \"turn one or two knobs, leave the rest.\" And the type parameter Frame forces framing↔protocol alignment at the seam — orthogonal but not lawless, free composition + type backstop."},
            },
        ],
        "open": [
            {"zh": "课里把 OpenAI Responses 同时支持 HTTP 与 WebSocket，解释为「哪种传输划算就用哪种，并把选择做成一个可拨动的旋钮」，而不是「为了时髦上 WebSocket」。结合 HTTP（无状态、省心、universal）与 WebSocket（双向、实时、但要管连接保活/重连）的权衡，谈谈你会在什么场景选 WebSocket、什么场景坚持 HTTP？把传输做成「旋钮」而非写死，给未来留下了什么样的余地？", "en": "The lesson explains OpenAI Responses supporting both HTTP and WebSocket as \"use whichever transport is worthwhile, making the choice a turnable knob,\" not \"adopt WebSocket to be trendy.\" Weighing HTTP (stateless, carefree, universal) against WebSocket (bidirectional, real-time, but must manage keepalive/reconnect), discuss when you'd choose WebSocket and when you'd stick with HTTP. Making transport a \"knob\" rather than hardcoded leaves what headroom for the future?"},
            {"zh": "课里强调「正交不等于放任」：六个旋钮能自由组合，但类型参数 Frame 在 framing 和 protocol 的接缝处强制对齐（SSE 切出 string 帧，配它的 protocol.stream.event 就得是 Codec<Event, string>）。请谈谈「用类型系统在模块接缝处设防」相比「靠文档约定/代码评审来防止错配」的优势；你能想到自己项目里哪个接缝，也值得用类型（而非口头约定）来强制对齐？", "en": "The lesson stresses \"orthogonal doesn't mean lawless\": the six knobs combine freely, but the type parameter Frame forces alignment at the framing/protocol seam (SSE cuts string frames, so its protocol.stream.event must be Codec<Event, string>). Discuss the advantage of \"guarding a module seam with the type system\" over \"preventing mismatches via documentation/code review.\" Which seam in your own project also deserves type-enforced (not verbal) alignment?"},
        ],
    },
    "34-streaming-cache.html": {
        "mcq": [
            {
                "q": {"zh": "LLMEvent（schema/events.ts，17 个成员）在整套设计里扮演什么角色？", "en": "What role does LLMEvent (schema/events.ts, 17 members) play in the whole design?"},
                "opts": [
                    {"zh": "反腐层的「入站」规范词汇——六种协议的 stream.step 都把各自方言翻译成它，agent 循环只消费它，补全第 28 课「翻译墙」的回来一面", "en": "The anti-corruption layer's \"inbound\" canonical vocabulary — all six protocols' stream.step translate their dialect into it, the agent loop consumes only it, completing the inbound face of lesson 28's \"translation wall\""},
                    {"zh": "只是 Anthropic 协议的内部事件类型", "en": "Just Anthropic's internal event type"},
                    {"zh": "用于 UI 渲染的前端数据结构", "en": "A frontend data structure for UI rendering"},
                    {"zh": "数据库里存事件日志的表", "en": "A DB table storing event logs"},
                ],
                "answer": 0,
                "why": {"zh": "第 28 课的反腐层有一进一出：出去 LLMRequest、回来 LLMEvent 流。LLMEvent 是六种协议的「最大公约数」——Anthropic content_block_delta、OpenAI choices[].delta、Gemini part、Bedrock 二进制帧，都被 stream.step 翻译成这同一套 17 种事件。于是 agent 循环（L17）只认这 17 种就能驱动任何模型，新增第七家供应商它一行不改。", "en": "Lesson 28's anti-corruption layer has an out and a back: out LLMRequest, back the LLMEvent stream. LLMEvent is the six protocols' \"greatest common divisor\" — Anthropic's content_block_delta, OpenAI's choices[].delta, Gemini's parts, Bedrock's binary frames, all translated by stream.step into this same 17-event set. So the agent loop (L17) drives any model knowing only these 17, and adding a seventh provider changes not a line of it."},
            },
            {
                "q": {"zh": "cache-policy 的 \"auto\" 默认把缓存断点打在「最后工具定义、最后系统提示、最新用户消息」三处，为什么是这三处？", "en": "cache-policy's \"auto\" default places breakpoints at \"last tool definition, last system part, latest user message.\" Why these three?"},
                "opts": [
                    {"zh": "这三处之前正好是「整回合不变的稳定前缀」；一个回合炸开成多次工具往返，每次都重发该前缀，打在「最新用户消息」边界让回合内每次往返都命中缓存", "en": "Up to these three is exactly the \"stable prefix unchanged through the turn\"; a turn explodes into many tool round-trips each resending that prefix, so marking the \"latest user message\" boundary makes every round-trip in the turn hit the cache"},
                    {"zh": "随机选的三个位置", "en": "Three randomly chosen positions"},
                    {"zh": "因为这三处内容最短", "en": "Because these three are the shortest"},
                    {"zh": "为了凑满 4 个断点上限", "en": "To fill the 4-breakpoint cap"},
                ],
                "answer": 0,
                "why": {"zh": "工具定义、系统提示通常整回合不变，直到「最新用户消息」为止的前缀也是。第 17 课的 agent 循环里，一条用户消息会炸开成许多次 assistant↔tool 往返，每次都重发整段前缀。把断点打在这条边界上，回合内每次往返的 API 调用都命中同一段缓存前缀——一次写入、N 次命中，省钱成倍。这正是第 24 课 Context Epoch 死守「基线前缀稳定」的真正目的。", "en": "Tool definitions and system prompts usually stay fixed all turn, as does the prefix up to the \"latest user message.\" In lesson 17's agent loop, one user message explodes into many assistant↔tool round-trips, each resending the whole prefix. Marking this boundary makes every round-trip's API call in the turn hit the same cached prefix — one write, N hits, multiplied savings. This is the true purpose of lesson 24's Context Epoch guarding \"baseline prefix stable.\""},
            },
            {
                "q": {"zh": "applyCachePolicy 第一句就检查 RESPECTS_INLINE_HINTS，对 OpenAI/Gemini 整套策略跳过、原样返回。为什么？", "en": "applyCachePolicy's first line checks RESPECTS_INLINE_HINTS, skipping the whole policy for OpenAI/Gemini and returning as-is. Why?"},
                "opts": [
                    {"zh": "因为只有 Anthropic/Bedrock 认内联 cache_control 标记；OpenAI 用隐式前缀缓存、Gemini 用隐式+带外 CachedContent，给它们打内联标记「无害但无意义」", "en": "Because only Anthropic/Bedrock recognize inline cache_control markers; OpenAI uses implicit prefix caching, Gemini implicit + out-of-band CachedContent, so inline marks for them are \"harmless but pointless\""},
                    {"zh": "因为 OpenAI/Gemini 不支持缓存", "en": "Because OpenAI/Gemini don't support caching"},
                    {"zh": "因为 OpenAI/Gemini 的请求太大", "en": "Because OpenAI/Gemini requests are too big"},
                    {"zh": "这是个 bug", "en": "It's a bug"},
                ],
                "answer": 0,
                "why": {"zh": "各家缓存机制根本不同：Anthropic/Bedrock 要你显式在 part 上打 cache_control 内联标记；OpenAI 是隐式前缀缓存（自动，你不用标记）；Gemini 是隐式 + 带外 CachedContent API。cache-policy 这套「打内联标记」只对前两家有意义，对后两家无害但无意义，故整段跳过。这是很克制的设计——承认各家缓存哲学的差异，不硬塞进一个假装统一的抽象，正是 M6 的主旋律。", "en": "Cache mechanisms differ fundamentally: Anthropic/Bedrock want explicit inline cache_control marks on parts; OpenAI is implicit prefix caching (automatic, no marking); Gemini is implicit + out-of-band CachedContent API. cache-policy's \"inline marking\" matters only for the first two, harmless but pointless for the latter, so it skips entirely. A restrained design — acknowledging each vendor's caching philosophy rather than cramming into a fake-unified abstraction, exactly M6's main melody."},
            },
        ],
        "open": [
            {"zh": "课里说 LLMEvent 把「会一点点来的内容」（正文/推理/工具参数）都拆成 start→delta…→end 三段式。请你想想：为什么流式 UI（边生成边显示）几乎必然要求事件被设计成这种「有头、有连续增量、有尾」的形状？如果只有一个「完整事件」、没有 delta，流式体验会损失什么？这种三段式还在你见过的哪些系统里出现过？", "en": "The lesson says LLMEvent splits \"content arriving bit by bit\" (body/reasoning/tool args) into a start→delta…→end triple. Consider: why does streaming UI (display-while-generating) almost necessarily require events shaped as \"a head, continuous deltas, a tail\"? If there were only one \"complete event\" and no deltas, what would the streaming experience lose? Where else have you seen this triple appear?"},
            {"zh": "课里揭示一个跨课的「合谋」：cache-policy 在出站时把断点打在稳定前缀的边界（战略：缓存哪里最划算），protocol 的断点预算在更下层落实且不超 4 个名额（战术：硬约束内执行），而 Context Epoch（L24）在更上层死守前缀不变（保住命中）。请用你自己的话说清这三层各自的职责，并论证：为什么把「决定缓存哪里」「执行打标记」「维持前缀稳定」拆给三个不同的层，比揉成一坨更好？", "en": "The lesson reveals a cross-lesson \"conspiracy\": cache-policy marks breakpoints at the stable-prefix boundary on the way out (strategy: where caching pays most), the protocol's breakpoint budget enforces it lower down within the 4-slot cap (tactics: executing within the hard constraint), while Context Epoch (L24) guards the prefix unchanged higher up (preserving hits). In your own words, articulate each of these three layers' responsibilities, and argue: why is splitting \"decide where to cache,\" \"execute marking,\" and \"keep the prefix stable\" across three different layers better than mashing them into one?"},
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
