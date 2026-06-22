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
    "68-account-auth.html": {
        "mcq": [
            {
                "q": {"zh": "课里说设备码（device-code）流是为「CLI 没有浏览器回调」设计的。它的核心机制和解决的问题是？", "en": "The lesson says the device-code flow is designed for \"a CLI with no browser callback.\" Its core mechanism and the problem it solves?"},
                "opts": [
                    {"zh": "把流程拆成「<strong>显示码 + 后台轮询</strong>」：终端显示 <span class=\"mono\">user_code</span>+URL，你<strong>在任意有浏览器的设备</strong>授权，终端同时轮询令牌端点直到成功——「授权在别处、令牌落 CLI」被一个短码解耦，绕开了「CLI 收不了浏览器回调」这个死结", "en": "Splitting the flow into \"<strong>show code + background polling</strong>\": the terminal shows <span class=\"mono\">user_code</span>+URL, you authorize on <strong>any device with a browser</strong>, the terminal polls the token endpoint until success—\"authorize elsewhere, token lands in the CLI\" decoupled by a short code, bypassing the deadlock that \"a CLI can't receive a browser callback\""},
                    {"zh": "让 CLI 自己弹出一个浏览器窗口接收回调", "en": "Having the CLI pop up its own browser window to receive the callback"},
                    {"zh": "把用户名密码明文存进配置文件，下次直接读", "en": "Storing username/password in plaintext in a config file to read next time"},
                    {"zh": "完全不需要授权，CLI 直接拿到令牌", "en": "Needing no authorization at all; the CLI just gets the token directly"},
                ],
                "answer": 0,
                "why": {"zh": "网页 OAuth 靠「浏览器回调」把授权结果送回应用，但 CLI 是个终端进程、没浏览器、没公网回调地址，这条路走不通。设备码（OAuth 2.0 Device Authorization Grant，本为智能电视等「输入受限」设备设计）把流程拆成两半：终端只<strong>显示</strong> <span class=\"mono\">user_code</span>+URL（来自 <span class=\"mono\">DeviceAuth</span>），你<strong>在任意有浏览器的设备</strong>打开网址、输码、授权；同时终端揣着保密的 <span class=\"mono\">device_code</span> 在后台<strong>轮询</strong>令牌端点，直到你授权完成就拿到令牌。「授权」在浏览器、「令牌」落 CLI，一个短码牵两头。所以不是「CLI 自己弹浏览器」「存明文密码」「不需授权」——这些都误解了设备码「把需浏览器的那步挪到别处」的本质。", "en": "Web OAuth relies on a \"browser callback\" to send the auth result back to the app, but a CLI is a terminal process—no browser, no public callback address—so that path is impossible. Device-code (OAuth 2.0 Device Authorization Grant, originally for \"input-constrained\" devices like smart TVs) splits the flow in two: the terminal only <strong>shows</strong> <span class=\"mono\">user_code</span>+URL (from <span class=\"mono\">DeviceAuth</span>), you on <strong>any device with a browser</strong> open the URL, enter the code, authorize; meanwhile the terminal, holding the secret <span class=\"mono\">device_code</span>, <strong>polls</strong> the token endpoint in the background until you finish, then gets the token. \"Authorization\" in the browser, \"token\" in the CLI, one short code linking both. So it's not \"the CLI pops its own browser,\" \"plaintext passwords,\" or \"no authorization\"—all misread the device-code essence of \"move the browser-needing step elsewhere.\""},
            },
            {
                "q": {"zh": "轮询令牌端点时，<span class=\"mono\">DeviceTokenError.toPollResult()</span> 把 <span class=\"mono\">authorization_pending</span>、<span class=\"mono\">slow_down</span> 等 error 字符串翻成 <span class=\"mono\">PollPending</span>、<span class=\"mono\">PollSlow</span> 等状态类。这体现了什么？", "en": "When polling the token endpoint, <span class=\"mono\">DeviceTokenError.toPollResult()</span> translates error strings like <span class=\"mono\">authorization_pending</span>, <span class=\"mono\">slow_down</span> into state classes like <span class=\"mono\">PollPending</span>, <span class=\"mono\">PollSlow</span>. What does this embody?"},
                "opts": [
                    {"zh": "把<strong>原始字符串升格成有名字的、有类型的值</strong>：OAuth 协议里「还没授权/轮太快/过期/被拒」都混在 error 字符串里，翻成状态类后轮询循环能干净地按状态分支，而不是到处比对魔法字符串（同 L20 RunError、L05「错误即值」）", "en": "Promoting <strong>a raw string into a named, typed value</strong>: in OAuth, \"not authorized/polling too fast/expired/denied\" are all jumbled in error strings; translating them into state classes lets the polling loop cleanly branch by state instead of comparing magic strings everywhere (like L20 RunError, L05 \"errors-as-values\")"},
                    {"zh": "把错误信息翻译成多国语言给用户看", "en": "Translating error messages into multiple languages for the user"},
                    {"zh": "把所有错误都当成致命错误、直接终止轮询", "en": "Treating all errors as fatal and terminating polling immediately"},
                    {"zh": "加密 error 字符串，防止泄露", "en": "Encrypting the error strings to prevent leaks"},
                ],
                "answer": 0,
                "why": {"zh": "设备码轮询里，令牌端点对「还没好」用 HTTP 错误 + error 字符串回应：<span class=\"mono\">authorization_pending</span>（继续等）、<span class=\"mono\">slow_down</span>（放慢）、<span class=\"mono\">expired_token</span>（过期重来）、<span class=\"mono\">access_denied</span>（被拒结束）。这些<strong>不全是「真错误」</strong>——有的是「正常的还没好」。<span class=\"mono\">toPollResult</span> 把这些字符串翻成有名状态类（<span class=\"mono\">PollPending/PollSlow/PollExpired/PollDenied/PollError</span>），轮询循环就能 <span class=\"mono\">switch</span> 这些状态、清清楚楚地决定「继续/放慢/重来/结束」，而不是满地 <span class=\"mono\">if (error === \"...\")</span> 比对魔法字符串。这正是全书「把原始值升格成有类型的值」（L05 错误即值、L20 RunError）。所以不是翻译语言/全当致命/加密——核心是<strong>让轮询逻辑类型化、可读</strong>。", "en": "In device-code polling, the token endpoint answers \"not ready\" with HTTP errors + error strings: <span class=\"mono\">authorization_pending</span> (keep waiting), <span class=\"mono\">slow_down</span> (slow down), <span class=\"mono\">expired_token</span> (expired, restart), <span class=\"mono\">access_denied</span> (denied, end). These <strong>aren't all \"real errors\"</strong>—some are \"a normal not-yet.\" <span class=\"mono\">toPollResult</span> translates these strings into named state classes (<span class=\"mono\">PollPending/PollSlow/PollExpired/PollDenied/PollError</span>), so the polling loop can <span class=\"mono\">switch</span> on states and clearly decide \"continue/slow/restart/end\" instead of scattered <span class=\"mono\">if (error === \"...\")</span> magic-string comparisons. This is the book's \"promote a raw value into a typed value\" (L05 errors-as-values, L20 RunError). So it's not translating languages/all-fatal/encryption—the core is <strong>making the polling logic typed and readable</strong>."},
            },
            {
                "q": {"zh": "凭据库（<span class=\"mono\">credential.ts</span>）把 OAuth 令牌和 API Key 都塑成同一个 <span class=\"mono\">Credential.Info = Union[OAuth, Key]</span>。这样做的好处，以及 <span class=\"mono\">eagerRefreshThreshold=5min</span> 的作用是？", "en": "The credential store (<span class=\"mono\">credential.ts</span>) shapes both OAuth tokens and API keys into one <span class=\"mono\">Credential.Info = Union[OAuth, Key]</span>. The benefit, and the role of <span class=\"mono\">eagerRefreshThreshold=5min</span>?"},
                "opts": [
                    {"zh": "<strong>异质塑同形</strong>：两种很不一样的凭据塑成同一个带 <span class=\"mono\">type</span> 标签的值、进同一个 CRUD 库，上层取用时差异只剩「分一下 type 叉」（同 L66/L36）。<span class=\"mono\">eagerRefreshThreshold</span> 让 OAuth 令牌在过期前 5 分钟<strong>主动用 refresh 续</strong>，避免「过期了调用才失败」", "en": "<strong>Shape the heterogeneous into one form</strong>: two very different credentials shaped into one <span class=\"mono\">type</span>-tagged value, into one CRUD store, so the upper layer's only difference is \"branch once on type\" (like L66/L36). <span class=\"mono\">eagerRefreshThreshold</span> makes the OAuth token <strong>proactively renew via refresh 5 minutes before expiry</strong>, avoiding \"the call fails only after expiry\""},
                    {"zh": "把 OAuth 和 Key 合并成一种，删掉 API Key 支持", "en": "Merging OAuth and Key into one, dropping API Key support"},
                    {"zh": "<span class=\"mono\">eagerRefreshThreshold</span> 是指令牌每 5 分钟就强制过期一次", "en": "<span class=\"mono\">eagerRefreshThreshold</span> means the token is force-expired every 5 minutes"},
                    {"zh": "凭据只存在内存里，重启 opencode 就没了", "en": "Credentials live only in memory and vanish when opencode restarts"},
                ],
                "answer": 0,
                "why": {"zh": "OAuth 令牌（access/refresh/expires、要管过期）和 API Key（一个字符串、不过期）本是两种东西，却被塑成同一个 <span class=\"mono\">Credential.Info</span> 标签联合（<span class=\"mono\">toTaggedUnion(\"type\")</span>），进同一个有 <span class=\"mono\">all/list/get/create/update/remove</span> 的库——上层 <span class=\"mono\">get(id)</span> 拿 <span class=\"mono\">Info</span>、按 <span class=\"mono\">type</span> 分一下叉即可，差异收进「一个 type 字段」（同 L66 三源归一、L36 统一模子）。<span class=\"mono\">eagerRefreshThreshold=Duration.minutes(5)</span> 是<strong>预判式刷新</strong>：令牌还差 5 分钟过期就主动用 <span class=\"mono\">refresh_token</span> 续，而非等过期、调用失败再补救，让你感觉不到过期。所以不是「删掉 Key 支持」「每 5 分钟强制过期」（恰相反，是提前续命），凭据也<strong>落 SQLite（<span class=\"mono\">CredentialTable</span>）持久化</strong>、不是只在内存。", "en": "An OAuth token (access/refresh/expires, manage expiry) and an API Key (one string, no expiry) are two different things, yet shaped into the same <span class=\"mono\">Credential.Info</span> tagged union (<span class=\"mono\">toTaggedUnion(\"type\")</span>), into one store with <span class=\"mono\">all/list/get/create/update/remove</span>—the upper layer <span class=\"mono\">get(id)</span>s the <span class=\"mono\">Info</span> and branches once on <span class=\"mono\">type</span>, the difference tucked into \"one type field\" (like L66 three-sources, L36 one-mold). <span class=\"mono\">eagerRefreshThreshold=Duration.minutes(5)</span> is <strong>predictive refresh</strong>: 5 minutes before expiry it proactively renews via <span class=\"mono\">refresh_token</span> rather than waiting for expiry and a failed call, so you never notice expiry. So it's not \"drop Key support\" or \"force-expire every 5 minutes\" (the opposite—renew early), and credentials <strong>land in SQLite (<span class=\"mono\">CredentialTable</span>) persistently</strong>, not only in memory."},
            },
        ],
        "open": [
            {"zh": "课里把设备码流的精髓提炼为「<strong>把『在哪授权』和『令牌落到哪』解耦</strong>」——授权在任意有浏览器的设备上完成，令牌却落到那个收不了回调的 CLI 里，靠一个短码牵两头。请你谈谈你对这种「<strong>用一个间接物（短码/票据）解耦两个本来无法直接对接的端</strong>」的设计模式的理解：它和你熟悉的哪些机制相通（如取餐号、二维码登录、OAuth state 参数、分布式系统里的 correlation id）？再谈谈「轮询（polling）」作为「无法接收推送时的退而求其次」，在什么场景下是合理的、又有什么代价（如 <span class=\"mono\">slow_down</span> 的存在说明了什么）。", "en": "The lesson distills the device-code flow's essence as \"<strong>decouple 'where you authorize' from 'where the token lands'</strong>\"—authorization completes on any device with a browser, yet the token lands in the CLI that can't receive a callback, the two linked by a short code. Discuss your understanding of this design pattern of \"<strong>using an intermediary (short code/ticket) to decouple two ends that otherwise can't directly connect</strong>\": what mechanisms you know does it resemble (order numbers, QR-code login, OAuth's state parameter, correlation ids in distributed systems)? Then discuss \"polling\" as \"a fallback when you can't receive a push\": in what scenarios is it reasonable, and at what cost (e.g. what does the existence of <span class=\"mono\">slow_down</span> tell us)?"},
            {"zh": "课里说凭据库把 OAuth 令牌和 API Key「异质塑同形」成一个 <span class=\"mono\">Credential.Info</span>，并落进 SQLite 成为「和会话、消息一样被持久化管理的一等数据」；还盛赞 <span class=\"mono\">eagerRefreshThreshold</span> 这种「在出问题前就解决掉」的预判式刷新是「做对了你根本不会注意到」的体贴。请你谈谈「<strong>把横切关注点（身份/凭据）抽成一个有清晰接口、统一形态、可持久化的子系统</strong>」相比「各处随手管理令牌」的价值（可测、可换、可安全审计…）。再结合 <span class=\"mono\">eagerRefreshThreshold</span>，谈谈你对「<strong>好的工程体贴往往是『隐形』的——它消除的是一类你本来会反复遇到的小麻烦</strong>」这一观点的理解，并举 1-2 个你见过的类似「隐形体贴」设计。", "en": "The lesson says the credential store shapes OAuth tokens and API keys into one <span class=\"mono\">Credential.Info</span> and lands them in SQLite as \"first-class data persistently managed like sessions and messages\"; it also praises <span class=\"mono\">eagerRefreshThreshold</span>'s \"solve it before it's a problem\" predictive refresh as \"thoughtfulness you never notice when done right.\" Discuss the value of \"<strong>abstracting a cross-cutting concern (identity/credentials) into a subsystem with a clear interface, unified form, and persistence</strong>\" vs \"managing tokens ad hoc everywhere\" (testable, swappable, securely auditable…). Then, drawing on <span class=\"mono\">eagerRefreshThreshold</span>, discuss your understanding of \"<strong>good engineering thoughtfulness is often 'invisible'—it eliminates a class of small troubles you'd otherwise hit repeatedly</strong>,\" and give 1-2 similar \"invisible thoughtfulness\" designs you've seen."},
        ],
    },

    "67-http-recorder.html": {
        "mcq": [
            {
                "q": {"zh": "agent 循环会调真实大模型（非确定、花钱、慢）。<span class=\"mono\">http-recorder</span> 怎么让它变得可测？", "en": "The agent loop calls a real LLM (non-deterministic, costly, slow). How does <span class=\"mono\">http-recorder</span> make it testable?"},
                "opts": [
                    {"zh": "<strong>录放（record/replay）</strong>：第一次「录制模式」真打一次 API、把请求-响应存成命名<strong>磁带</strong>；之后「回放模式」让进来的请求匹配到磁带、返回录好的响应——把「模型」这个不确定变量<strong>固定住</strong>，于是测试确定、免费、毫秒、可离线", "en": "<strong>Record/replay</strong>: the first time, \"record mode\" hits the API once and stores the request-response as a named <strong>cassette</strong>; thereafter \"replay mode\" matches an incoming request to a cassette and returns the recorded response—<strong>fixing</strong> the non-deterministic variable \"the model,\" so tests are deterministic, free, millisecond, offline-able"},
                    {"zh": "把模型换成一个更小的本地模型，凑合着测", "en": "Swap in a smaller local model and test with that"},
                    {"zh": "在测试里 mock 掉整个 HTTP 层，凭空返回写死的假响应", "en": "Mock out the entire HTTP layer in tests, returning hardcoded fake responses from nothing"},
                    {"zh": "重试 100 次取多数结果，抵消模型的随机性", "en": "Retry 100 times and take the majority result to cancel the model's randomness"},
                ],
                "answer": 0,
                "why": {"zh": "<span class=\"mono\">http-recorder</span> 用经典的「录放」手法：录制模式真打<strong>一次</strong> API、把往返存成一盘命名磁带；回放模式让进来的请求经 <span class=\"mono\">canonicalSnapshot</span> 归一化、由 <span class=\"mono\">RequestMatcher</span> 匹配到对应录音、原样放出响应。这把「与外部世界的真实交互」从测试每次运行里抽出来、只做一次、冻成确定录音，于是测试确定/免费/毫秒/可离线。注意它<strong>不是 mock</strong>（选项三）——磁带是<strong>一次真实交互的忠实录音</strong>（真实协议字节、真实流式分帧），不是凭空捏造，故不会像纯 mock 那样测出「假绿」（同 L63「测真实、少 mock」）。「换小模型」「重试取多数」都没解决「确定性」这个根本问题。", "en": "<span class=\"mono\">http-recorder</span> uses the classic \"record/replay\": record mode hits the API <strong>once</strong> and stores the round-trip as a named cassette; replay mode normalizes an incoming request via <span class=\"mono\">canonicalSnapshot</span>, matches it via <span class=\"mono\">RequestMatcher</span>, and plays back the response verbatim. This lifts \"the real interaction with the outside world\" out of every test run, does it once, freezes it into a deterministic recording—so tests are deterministic/free/millisecond/offline-able. Note it's <strong>not a mock</strong> (option 3)—the cassette is a <strong>faithful recording of one real interaction</strong> (real protocol bytes, real stream framing), not fabricated, so it won't produce \"fake green\" like pure mocks (per L63 \"test real, few mocks\"). \"Smaller model\" and \"retry-majority\" don't solve the root issue of determinism."},
            },
            {
                "q": {"zh": "回放时，<span class=\"mono\">canonicalSnapshot</span> 把请求<strong>归一化</strong>成 {method,url,headers,body} 的规范 JSON，而不是逐字节比对。为什么？", "en": "On replay, <span class=\"mono\">canonicalSnapshot</span> <strong>normalizes</strong> a request into canonical JSON {method,url,headers,body} rather than comparing byte-for-byte. Why?"},
                "opts": [
                    {"zh": "因为 HTTP 请求的「字面形态」有许多无关抖动（同一 JSON body 的字段顺序、空白可能不同），但<strong>语义是同一个请求</strong>；归一化抹平噪声、只留「语义指纹」，才能让「语义同、字节序不同」的请求<strong>稳定命中同一盘磁带</strong>，否则会因无关差异找不到录音、测试莫名失败", "en": "Because an HTTP request's \"literal form\" has much irrelevant jitter (the same JSON body may differ in field order or whitespace), yet it's <strong>semantically the same request</strong>; normalization smooths the noise and keeps only the \"semantic fingerprint,\" so \"semantically same, byte-order different\" requests <strong>reliably hit the same cassette</strong>—otherwise irrelevant differences would fail to find the recording and the test would fail inexplicably"},
                    {"zh": "为了压缩磁带文件，省磁盘空间", "en": "To compress the cassette file and save disk space"},
                    {"zh": "为了把请求加密，防止别人读懂磁带", "en": "To encrypt the request so others can't read the cassette"},
                    {"zh": "逐字节比对更准，归一化只是为了省 CPU", "en": "Byte-for-byte is more accurate; normalization is only to save CPU"},
                ],
                "answer": 0,
                "why": {"zh": "<span class=\"mono\">canonicalSnapshot</span>（<span class=\"mono\">matching.ts</span>）取 method/url/<span class=\"mono\">canonicalizeJson(headers)</span>/把 body 当 JSON 解出再规范化（<span class=\"mono\">decodeJson</span>），目的就是<strong>匹配的稳定性</strong>。同一个语义请求，序列化时字段顺序、缩进、空白都可能变；若逐字节比，回放会因这些<strong>无关差异</strong>找不到对应磁带、测试莫名其妙红。归一化把噪声抹平、只留「语义指纹」，让语义相同的请求稳定命中同一盘。所以不是为压缩/加密/省 CPU，而是为<strong>正确、稳定地匹配</strong>（逐字节反而<strong>不</strong>准——它会把语义无关的差异当成不匹配）。", "en": "<span class=\"mono\">canonicalSnapshot</span> (<span class=\"mono\">matching.ts</span>) takes method/url/<span class=\"mono\">canonicalizeJson(headers)</span>/body parsed as JSON then normalized (<span class=\"mono\">decodeJson</span>), aiming at <strong>match stability</strong>. The same semantic request may vary in field order, indentation, whitespace on serialization; byte comparison would fail to find the cassette over these <strong>irrelevant differences</strong>, turning the test inexplicably red. Normalization smooths the noise, keeping only the \"semantic fingerprint,\" so semantically-same requests reliably hit the same cassette. So it's not for compression/encryption/CPU but for <strong>correct, stable matching</strong> (byte comparison is actually <strong>less</strong> accurate—it treats semantically-irrelevant differences as mismatches)."},
            },
            {
                "q": {"zh": "录制时 <span class=\"mono\">http-recorder</span> 会把 <span class=\"mono\">authorization</span>、<span class=\"mono\">x-api-key</span> 等替换成 <span class=\"mono\">[REDACTED]</span>。这一步「脱敏（redaction）」的关键意义是？", "en": "On record, <span class=\"mono\">http-recorder</span> replaces <span class=\"mono\">authorization</span>, <span class=\"mono\">x-api-key</span>, etc. with <span class=\"mono\">[REDACTED]</span>. The key significance of this \"redaction\" step is?"},
                "opts": [
                    {"zh": "去掉真实密钥后，磁带<strong>不含任何秘密、可安全提交进 git</strong>当测试 fixture 长期复用——既保留「请求长什么样」（够匹配）、又不把密钥带进仓库。<span class=\"mono\">RedactOptions</span> 还是「叠加式」的（默认安全底线 + 可再加）", "en": "With real keys removed, the cassette <strong>contains no secret and is safely committable to git</strong> as a long-lived test fixture—keeping \"what the request looks like\" (enough to match) yet not dragging keys into the repo. <span class=\"mono\">RedactOptions</span> is also \"additive\" (a safe default floor + you can add more)"},
                    {"zh": "让磁带文件更小，加快回放速度", "en": "Makes the cassette file smaller and speeds replay"},
                    {"zh": "让模型无法识别是哪个用户在调用", "en": "Prevents the model from identifying which user is calling"},
                    {"zh": "把请求加密，回放时再解密", "en": "Encrypts the request and decrypts it on replay"},
                ],
                "answer": 0,
                "why": {"zh": "若原样存请求，API key/<span class=\"mono\">Authorization</span> 就写进了磁带文件——提交进 git 等于泄露密钥。脱敏（<span class=\"mono\">redaction.ts</span>：<span class=\"mono\">REDACTED=\"[REDACTED]\"</span> + <span class=\"mono\">DEFAULT_REDACT_HEADERS/QUERY</span>）把这些字段盖掉再落盘，于是磁带<strong>既够用来匹配、又不含真实秘密</strong>，可放心入库当 fixture 长期复用。<span class=\"mono\">RedactOptions</span> 是「叠加式」：默认清单是安全底线，可在其上再加要盖的字段（同 L60「安全默认 + 可定制」）。所以核心是<strong>安全地把磁带入库</strong>，不是为压缩/防识别/加密（回放并不需要解密——盖掉的字段本就不参与真实鉴权）。", "en": "If the request were stored verbatim, the API key/<span class=\"mono\">Authorization</span> would be written into the cassette—committing it to git leaks the key. Redaction (<span class=\"mono\">redaction.ts</span>: <span class=\"mono\">REDACTED=\"[REDACTED]\"</span> + <span class=\"mono\">DEFAULT_REDACT_HEADERS/QUERY</span>) masks these fields before saving, so the cassette is <strong>enough to match yet holds no real secret</strong>, safely committable as a long-lived fixture. <span class=\"mono\">RedactOptions</span> is \"additive\": the default list is a safety floor you can add to (like L60's \"safe default + customizable\"). So the core is <strong>safely committing the cassette</strong>, not compression/anti-identification/encryption (replay needs no decryption—masked fields don't participate in real auth anyway)."},
            },
        ],
        "open": [
            {"zh": "课里把 <span class=\"mono\">http-recorder</span> 称作「如何确定性地测试一个不确定系统」这道难题的标准解，并指出它本质是 L63「测真实、可复现、少 mock」的极致手法——磁带不是凭空捏造的假响应（mock），而是一次真实交互的忠实录音，因此既<strong>真实</strong>又<strong>确定</strong>。请你谈谈「录放（VCR/cassette 模式）」相比「纯 mock」和「真打外部 API」各自的取舍：三者在「真实性 / 确定性 / 维护成本 / 速度」四个维度上各处什么位置？再结合你的经验，谈谈什么样的测试适合录放、什么样的不适合（比如响应本身就高度动态、或外部协议频繁变化时，磁带会带来什么麻烦）。", "en": "The lesson calls <span class=\"mono\">http-recorder</span> the standard solution to \"how to deterministically test a non-deterministic system,\" noting it's the ultimate form of L63's \"test real, reproducible, few mocks\"—the cassette isn't a fabricated fake (mock) but a faithful recording of one real interaction, hence both <strong>real</strong> and <strong>deterministic</strong>. Discuss the trade-offs of \"record/replay (VCR/cassette pattern)\" vs \"pure mocks\" vs \"hitting the real API\": where does each sit on \"realism / determinism / maintenance cost / speed\"? Drawing on your experience, discuss what tests suit record/replay vs not (e.g. when the response itself is highly dynamic, or the external protocol changes often, what trouble do cassettes bring)."},
            {"zh": "课里强调录放的<strong>边界</strong>：它不验证「模型答得对不对」（拿一张已知为真的样钞测售货机，不测印钞厂），只验证「给定这盘已知响应，我的 runner/协议解析/工具调度对不对」。请你谈谈这个「<strong>固定不该测的变量、专注该测的逻辑</strong>」的测试思想：它和「单一职责」「关注点分离」是什么关系？再以 <span class=\"mono\">session-runner-recorded.test.ts</span> 回放整条 V2 runner 为例（L17 循环 + L28+ 协议 + 流式分帧都在一盘确定磁带上跑），谈谈「端到端地回放一条真实录音」相比「为每个小函数单独写 mock 单测」各有什么价值，以及二者如何互补。", "en": "The lesson stresses record/replay's <strong>boundary</strong>: it doesn't verify \"did the model answer right\" (take a known-genuine sample bill to test the vending machine, not the mint), only \"given this known response, is my runner/protocol parsing/tool dispatch right.\" Discuss this testing idea of \"<strong>fix the variable you shouldn't test, focus on the logic you should</strong>\": how does it relate to \"single responsibility\" and \"separation of concerns\"? Then, using <span class=\"mono\">session-runner-recorded.test.ts</span> replaying the whole V2 runner (L17 loop + L28+ protocol + stream framing all on one deterministic cassette), discuss the respective value of \"replaying one real recording end-to-end\" vs \"writing a separate mock unit test per small function,\" and how the two complement each other."},
        ],
    },

    "66-slash-commands.html": {
        "mcq": [
            {
                "q": {"zh": "课里说「一个斜杠命令，本质就是……」。最准确的是哪个？", "en": "The lesson says \"a slash command is essentially…\" Which is most accurate?"},
                "opts": [
                    {"zh": "一段<strong>参数化的 prompt 模板</strong>：模板用 <span class=\"mono\">$ARGUMENTS</span>/<span class=\"mono\">$1</span>/<span class=\"mono\">${path}</span> 留「空」，<span class=\"mono\">hints()</span> 用 <span class=\"mono\">/\\$\\d+/g</span>+检测 <span class=\"mono\">$ARGUMENTS</span> 从模板正文「读」出参数清单，调用时把实参填空成完整 prompt", "en": "A <strong>parameterized prompt template</strong>: the template leaves \"blanks\" with <span class=\"mono\">$ARGUMENTS</span>/<span class=\"mono\">$1</span>/<span class=\"mono\">${path}</span>, <span class=\"mono\">hints()</span> \"reads\" the parameter list from the template body via <span class=\"mono\">/\\$\\d+/g</span>+checking <span class=\"mono\">$ARGUMENTS</span>, and invocation fills actuals into a full prompt"},
                    {"zh": "一个编译成机器码的二进制可执行文件", "en": "A binary executable compiled to machine code"},
                    {"zh": "一条直接操作数据库的 SQL 语句", "en": "A SQL statement that directly manipulates the database"},
                    {"zh": "一个写死的、不能传参的固定提示词", "en": "A hardcoded, non-parameterizable fixed prompt"},
                ],
                "answer": 0,
                "why": {"zh": "命令的数据形状是 <span class=\"mono\">Info</span>{name, description, template, source, hints, agent?/model?/subtask?}。「参数化」靠模板里的占位符 + <span class=\"mono\">hints(template)</span>：后者用正则 <span class=\"mono\">/\\$\\d+/g</span> 扫出 <span class=\"mono\">$1/$2</span>（去重排序）、再检测 <span class=\"mono\">includes(\"$ARGUMENTS\")</span>，<strong>直接从模板正文读出参数清单</strong>——你不用额外声明有几个参数。调用时把实参填进这些「空」，死板 prompt 就成了可复用、可传参、全团队共享的小工具。所以它不是二进制、不是 SQL，更<strong>不是</strong>「写死不能传参」（恰恰相反，参数化正是它的精髓）。", "en": "A command's data shape is <span class=\"mono\">Info</span>{name, description, template, source, hints, agent?/model?/subtask?}. \"Parameterization\" relies on template placeholders + <span class=\"mono\">hints(template)</span>: the latter scans <span class=\"mono\">$1/$2</span> via regex <span class=\"mono\">/\\$\\d+/g</span> (dedup+sort), then checks <span class=\"mono\">includes(\"$ARGUMENTS\")</span>, <strong>reading the parameter list straight from the template body</strong>—you needn't separately declare how many parameters. Invocation fills actuals into these \"blanks,\" turning a rigid prompt into a reusable, parameterizable, team-shareable tool. So it's not a binary, not SQL, and <strong>not</strong> \"hardcoded, non-parameterizable\" (the opposite—parameterization is its essence)."},
            },
            {
                "q": {"zh": "<span class=\"mono\">Command.layer</span> 在构建时 <span class=\"mono\">yield*</span> 了 <span class=\"mono\">Config/MCP/Skill</span> 三个服务。这体现了什么设计、解决了什么？", "en": "<span class=\"mono\">Command.layer</span> <span class=\"mono\">yield*</span>s the <span class=\"mono\">Config/MCP/Skill</span> services at construction. What design does this embody, and what does it solve?"},
                "opts": [
                    {"zh": "<strong>三源归一 / 统一模子刻同形</strong>：把内置命令、MCP prompt、skill 三种异质来源统一塑成同一个 <span class=\"mono\">Info</span>（用 <span class=\"mono\">source</span> 字段记出身），差异在 <span class=\"mono\">layer</span> 构建期一次性吃掉，上层 <span class=\"mono\">get/list</span> 一视同仁——同 L36 Tool.make、L47 PluginV2", "en": "<strong>Three sources, one form / one mold stamps the same shape</strong>: it shapes built-in commands, MCP prompts, and skills—three heterogeneous sources—into one <span class=\"mono\">Info</span> (with <span class=\"mono\">source</span> noting origin), the difference eaten once at <span class=\"mono\">layer</span> construction, the upper layer's <span class=\"mono\">get/list</span> treating them uniformly—like L36 Tool.make, L47 PluginV2"},
                    {"zh": "让三个服务互相竞争，谁先返回用谁的命令", "en": "Making the three services compete, using whichever returns first"},
                    {"zh": "把命令系统拆成三个完全独立、互不知情的子系统", "en": "Splitting the command system into three fully independent, mutually-unaware subsystems"},
                    {"zh": "仅仅是为了日志，记录命令来自哪个服务", "en": "Merely for logging which service a command came from"},
                ],
                "answer": 0,
                "why": {"zh": "三种来源本身天差地别：内置命令读本地 config/<span class=\"mono\">.txt</span>；MCP prompt 是外部进程远程暴露的（取正文要 await，故 <span class=\"mono\">template</span> 是 <span class=\"mono\">Promise&lt;string&gt;|string</span>）；skill 又是「名字常驻、正文按需」的另一套（L43）。但 <span class=\"mono\">Command.layer</span> 把它们<strong>统一塑成同一个 <span class=\"mono\">Info</span></strong>，只用一个 <span class=\"mono\">source</span> 字段记出身——异质性在「塑形」这一处被一次性消化，上层每处用命令都干净（只 <span class=\"mono\">get/list</span>）。这正是全书「统一模子刻同形」：同 L36 各种工具塑成 Tool、L47 各家 provider 塑成插件。所以不是「竞争」「互不知情」，<span class=\"mono\">source</span> 也<strong>不止</strong>用于日志（它支撑的是「异质塑同形」这件事本身）。", "en": "The three sources differ wildly: built-in reads local config/<span class=\"mono\">.txt</span>; MCP prompts are remotely exposed by an external process (fetching the body needs await, so <span class=\"mono\">template</span> is <span class=\"mono\">Promise&lt;string&gt;|string</span>); skills are another \"name-resident, body-on-demand\" system (L43). But <span class=\"mono\">Command.layer</span> <strong>shapes them all into one <span class=\"mono\">Info</span></strong>, using only a <span class=\"mono\">source</span> field for origin—heterogeneity digested once at the \"shaping\" spot, every upper-layer command use clean (just <span class=\"mono\">get/list</span>). This is the book's \"one mold stamps the same shape\": like L36 shaping tools into Tool, L47 shaping providers into plugins. So it's not \"competition\" or \"mutually unaware,\" and <span class=\"mono\">source</span> is <strong>not just</strong> logging (it underpins the very \"heterogeneous into one form\")."},
            },
            {
                "q": {"zh": "命令模板里的 <span class=\"mono\">$ARGUMENTS</span> 和 <span class=\"mono\">${path}</span> 有什么本质区别？", "en": "What's the essential difference between <span class=\"mono\">$ARGUMENTS</span> and <span class=\"mono\">${path}</span> in a command template?"},
                "opts": [
                    {"zh": "<span class=\"mono\">$ARGUMENTS</span>/<span class=\"mono\">$1</span> 是<strong>调用时</strong>才填的「用户参数」（由 <span class=\"mono\">hints</span> 列出、等你敲实参）；<span class=\"mono\">${path}</span> 是<strong>构建模板时</strong>就由内置命令 <span class=\"mono\">template</span> getter 用 <span class=\"mono\">.replace(\"${path}\", ctx.worktree)</span> 替换好的「上下文」——一个等用户、一个等环境，时机不同", "en": "<span class=\"mono\">$ARGUMENTS</span>/<span class=\"mono\">$1</span> are \"user arguments\" filled <strong>at invocation</strong> (listed by <span class=\"mono\">hints</span>, awaiting your actuals); <span class=\"mono\">${path}</span> is \"context\" <strong>already replaced at template-build time</strong> by the built-in command's <span class=\"mono\">template</span> getter via <span class=\"mono\">.replace(\"${path}\", ctx.worktree)</span>—one waits on the user, one on the environment, different timing"},
                    {"zh": "两者完全一样，只是写法不同", "en": "They are identical, just written differently"},
                    {"zh": "<span class=\"mono\">$ARGUMENTS</span> 是系统自动填的，<span class=\"mono\">${path}</span> 要用户手动填", "en": "<span class=\"mono\">$ARGUMENTS</span> is auto-filled by the system, <span class=\"mono\">${path}</span> must be filled by the user"},
                    {"zh": "<span class=\"mono\">${path}</span> 会被发到 MCP 服务器解析", "en": "<span class=\"mono\">${path}</span> is sent to an MCP server to resolve"},
                ],
                "answer": 0,
                "why": {"zh": "二者时机正相反。<span class=\"mono\">$ARGUMENTS</span>/<span class=\"mono\">$1</span> 由 <span class=\"mono\">hints</span> 从模板扫出、列为「参数槽」，<strong>等你调用时敲实参</strong>才填——是「用户参数」。<span class=\"mono\">${path}</span> 则是内置命令的 <span class=\"mono\">template</span> getter 在<strong>构建模板那一刻</strong>就 <span class=\"mono\">.replace(\"${path}\", ctx.worktree)</span> 换成当前 worktree 路径——是「环境上下文」，用户根本不经手。所以第三个选项把谁填的搞反了（恰是 ${path} 系统填、$ARGUMENTS 等用户），「完全一样」「发给 MCP」也都错。理解这点，写命令模板时就不会混淆「该让用户填的」与「系统自动给的」。", "en": "Their timing is opposite. <span class=\"mono\">$ARGUMENTS</span>/<span class=\"mono\">$1</span> are scanned from the template by <span class=\"mono\">hints</span> as \"parameter slots,\" filled only <strong>when you type actuals at invocation</strong>—\"user arguments.\" <span class=\"mono\">${path}</span> is replaced to the current worktree path by the built-in command's <span class=\"mono\">template</span> getter <strong>at the moment of building the template</strong> via <span class=\"mono\">.replace(\"${path}\", ctx.worktree)</span>—\"environment context,\" never touched by the user. So the third option reverses who fills what (it's <span class=\"mono\">${path}</span> the system fills, <span class=\"mono\">$ARGUMENTS</span> awaiting the user); \"identical\" and \"sent to MCP\" are also wrong. Grasp this and writing command templates won't confuse \"what the user should fill\" with \"what the system auto-supplies.\""},
            },
        ],
        "open": [
            {"zh": "课里把斜杠命令的核心提炼为「<strong>把异质塑成同形</strong>」——内置命令、MCP prompt、skill 三种来源天差地别，却被 <span class=\"mono\">Command.layer</span> 统一塑成同一个 <span class=\"mono\">Info</span>，并说这和 L36 Tool.make、L47 PluginV2 是「一模一样的招式」。请你谈谈你对这个反复出现的「统一模子刻同形」模式的理解：它把「异质性的复杂度」收到了哪里、又给上层换来了什么？再举 2–3 个你熟悉的、用「统一抽象/统一接口」把多种异质实现藏在背后的例子（如文件系统的 VFS、数据库驱动接口、操作系统设备抽象、前端的虚拟 DOM 等），并谈谈这种「找一个塑形点、在那把差异一次性吃掉」的设计什么时候值得做、什么时候会过度抽象。", "en": "The lesson distills slash commands' core as \"<strong>shape the heterogeneous into one form</strong>\"—built-in commands, MCP prompts, skills differ wildly yet <span class=\"mono\">Command.layer</span> shapes them into one <span class=\"mono\">Info</span>, calling it \"the exact same move\" as L36 Tool.make, L47 PluginV2. Discuss your understanding of this recurring \"one mold stamps the same shape\" pattern: where does it tuck \"the complexity of heterogeneity,\" and what does it buy the upper layer? Give 2–3 examples you know of hiding multiple heterogeneous implementations behind \"one abstraction/interface\" (e.g. a filesystem's VFS, database driver interfaces, OS device abstraction, the frontend virtual DOM), and discuss when this \"find a shaping spot and eat the difference there once\" design is worth doing vs when it over-abstracts."},
            {"zh": "课里说，把高频复杂的提示词固化成命令，等于把「提示词工程」从「每次现敲」升级成「沉淀成可调用的资产」——一段好提示词写一次（如 <span class=\"mono\">review.txt</span>），全团队 <span class=\"mono\">/review</span> 就复用了。请你谈谈在 AI agent 时代，「<strong>把提示词当成可版本化、可复用、可共享的工程资产</strong>」这件事的价值：它和传统「把常用脚本/函数沉淀成库」有何异同？再结合 <span class=\"mono\">command.executed</span> 事件会流进 L65 事件体系（即「你执行了哪些命令」也是可回放、可多端同步的会话历史），谈谈「让用户的高层操作也成为一等公民的事件」对可观测性、可复现性、协作有什么好处。", "en": "The lesson says crystallizing high-frequency complex prompts into commands upgrades \"prompt engineering\" from \"retyped each time\" to \"crystallized into a callable asset\"—write a good prompt once (like <span class=\"mono\">review.txt</span>) and the whole team <span class=\"mono\">/review</span>s to reuse it. Discuss the value, in the AI-agent era, of \"<strong>treating prompts as versionable, reusable, shareable engineering assets</strong>\": how is it similar to/different from the traditional \"crystallize common scripts/functions into a library\"? Then, given that <span class=\"mono\">command.executed</span> flows into L65's event system (i.e. \"which commands you ran\" is also replayable, multi-device-syncable session history), discuss what \"making users' high-level actions first-class events too\" buys for observability, reproducibility, and collaboration."},
        ],
    },

    "65-event-sourcing-sync.html": {
        "mcq": [
            {
                "q": {"zh": "课里说 opencode 的同步系统「被一个设计决定极大简化了」。这个决定是什么，它为什么能简化？", "en": "The lesson says opencode's sync system is \"radically simplified by one design decision.\" What is it, and why does it simplify?"},
                "opts": [
                    {"zh": "规定<strong>同一会话只允许一台设备写</strong>（单写入者）。于是「谁先谁后」不再需要分布式时钟/因果排序/共识——写入者每生成一个事件就给它一个<strong>单调 +1 的 seq</strong>，全序天然唯一；其他设备只要拉事件日志、从自己游标往后重放就能追平", "en": "Mandating that <strong>only one device may write a session</strong> (single writer). So \"who's first\" no longer needs distributed clocks/causal ordering/consensus—the writer gives each event a <strong>monotonically +1 seq</strong>, the total order naturally unique; other devices just pull the log and replay forward from their cursor to catch up"},
                    {"zh": "用 Paxos/Raft 共识协议让所有设备投票决定事件顺序", "en": "Using Paxos/Raft consensus so all devices vote on event order"},
                    {"zh": "给每台设备一个向量时钟，靠因果排序合并并发写", "en": "Giving each device a vector clock and merging concurrent writes by causal ordering"},
                    {"zh": "禁止多设备，opencode 只能在一台机器上用", "en": "Forbidding multiple devices; opencode runs on only one machine"},
                ],
                "answer": 0,
                "why": {"zh": "源码 <span class=\"mono\">sync/README.md</span> 原话：「only one device is allowed to write, we don't need any kind of sophisticated distributed system clocks or causal ordering. We implement total ordering with a simple sequence id (a number) and increment it by one every time we generate an event.」关键在<strong>「用约束换简单」</strong>：多写入者的一致性是难题（要分布式时钟/共识），opencode 不去解它，而是<strong>从源头消灭它</strong>——只留一个写入者，于是全序塌缩成一个 <span class=\"mono\">counter += 1</span>，其他设备「同步」=拉日志从游标重放。所以正解不是「上共识」「上向量时钟」（那恰是被绕开的复杂方案），也不是「禁止多设备」（多设备只读同步是支持的，只是不能多写）。", "en": "Source <span class=\"mono\">sync/README.md</span> verbatim: \"only one device is allowed to write, we don't need any kind of sophisticated distributed system clocks or causal ordering. We implement total ordering with a simple sequence id (a number) and increment it by one every time we generate an event.\" The key is <strong>\"trade a constraint for simplicity\"</strong>: multi-writer consistency is hard (distributed clocks/consensus); opencode doesn't solve it but <strong>eliminates it at the source</strong>—keep one writer, so total order collapses to a <span class=\"mono\">counter += 1</span>, and \"sync\" = pull the log and replay from the cursor. So the answer isn't \"add consensus\" or \"add vector clocks\" (precisely the sidestepped complex schemes), nor \"forbid multiple devices\" (read-only multi-device sync IS supported; just not multi-write)."},
            },
            {
                "q": {"zh": "<span class=\"mono\">event/sql.ts</span> 里用 <strong>两张</strong>表（<span class=\"mono\">event_sequence</span> + <span class=\"mono\">event</span>）+ 一个 <span class=\"mono\">uniqueIndex(aggregate_id, seq)</span>。这套设计的要点是？", "en": "<span class=\"mono\">event/sql.ts</span> uses <strong>two</strong> tables (<span class=\"mono\">event_sequence</span> + <span class=\"mono\">event</span>) + a <span class=\"mono\">uniqueIndex(aggregate_id, seq)</span>. The point of this design is?"},
                "opts": [
                    {"zh": "<span class=\"mono\">event_sequence</span> 记每个聚合<strong>当前最大序号</strong>（小计数器，会更新）、<span class=\"mono\">event</span> 存<strong>逐条不可变事件</strong>（只增）；<span class=\"mono\">uniqueIndex(aggregate_id, seq)</span> 在数据库层钉死「同会话不可能有两条相同 seq」，即使有 bug/并发也<strong>当场拒写</strong>、保全序不可破坏", "en": "<span class=\"mono\">event_sequence</span> records each aggregate's <strong>current max number</strong> (a small, updated counter); <span class=\"mono\">event</span> stores <strong>each immutable event</strong> (append-only); <span class=\"mono\">uniqueIndex(aggregate_id, seq)</span> pins \"a session can't have two equal seq\" at the DB layer—even on a bug/race it <strong>rejects the write on the spot</strong>, keeping the order unbreakable"},
                    {"zh": "两张表是同一份数据的冗余备份，互为容灾", "en": "The two tables are redundant backups of the same data for disaster recovery"},
                    {"zh": "<span class=\"mono\">event</span> 表存最新状态、<span class=\"mono\">event_sequence</span> 存历史快照", "en": "The <span class=\"mono\">event</span> table stores current state, <span class=\"mono\">event_sequence</span> stores historical snapshots"},
                    {"zh": "uniqueIndex 只是为了查询更快，与正确性无关", "en": "The uniqueIndex is only for faster queries, unrelated to correctness"},
                ],
                "answer": 0,
                "why": {"zh": "把「逐条事件」（只增不改的流水）和「当前最大序号」（不断更新的小计数器）<strong>分两张表</strong>，写新事件时先去 <span class=\"mono\">event_sequence</span>「领号」、再把带号事件追加进 <span class=\"mono\">event</span>。<span class=\"mono\">uniqueIndex(aggregate_id, seq)</span> 是<strong>兜底的物理保证</strong>：单写入者内存里 +1 是约定，而唯一索引确保万一抢到同号，DB 直接拒绝、让错误当场暴露（同 L37/L48「用错即响亮失败」），全序不可破坏。还有 <span class=\"mono\">aggregate_id</span> 外键 <span class=\"mono\">onDelete cascade</span>。所以不是「冗余备份」（两表职责不同）、不是「存最新状态/快照」（event 是逐条历史、不是当前态）、uniqueIndex 也<strong>不止</strong>是查询快（它保正确性）。", "en": "Splitting \"each event\" (append-only stream) from \"current max number\" (a constantly-updated small counter) into <strong>two tables</strong>: a new write first \"draws a number\" from <span class=\"mono\">event_sequence</span>, then appends the numbered event to <span class=\"mono\">event</span>. <span class=\"mono\">uniqueIndex(aggregate_id, seq)</span> is the <strong>physical backstop</strong>: the single writer's in-memory +1 is a convention, while the unique index ensures that if two grab the same number, the DB rejects it, exposing the error on the spot (like L37/L48 \"fail loudly\"), keeping the order unbreakable. Plus the <span class=\"mono\">aggregate_id</span> FK <span class=\"mono\">onDelete cascade</span>. So it's not \"redundant backup\" (the tables differ in role), not \"current state/snapshots\" (event is per-event history, not current state), and the uniqueIndex is <strong>not just</strong> for speed (it guards correctness)."},
            },
            {
                "q": {"zh": "本课的 EventV2 与第 11 课的 SSE、第 8 课的 KeyedMutex 都和「事件/顺序」有关。它们的分工是？", "en": "This lesson's EventV2, Lesson 11's SSE, and Lesson 8's KeyedMutex all relate to \"events/order.\" How do they divide labor?"},
                "opts": [
                    {"zh": "EventV2=事件的<strong>持久化+定序+跨设备同步</strong>（本课）；SSE(L11)=事件的<strong>实时传输</strong>（推给已连客户端）；KeyedMutex(L8)=<strong>进程内</strong>同一文件/插件的并发串行。三者层面不同：L11 管传输、本课管存储与多端一致、L8 管单机内存竞态", "en": "EventV2 = events' <strong>persistence + ordering + cross-device sync</strong> (this lesson); SSE(L11) = events' <strong>live transport</strong> (push to connected clients); KeyedMutex(L8) = <strong>in-process</strong> serialization of same-file/plugin concurrency. Different layers: L11 is transport, this lesson is storage + multi-end consistency, L8 is single-machine memory races"},
                    {"zh": "三者是同一个机制的三个名字", "en": "They are three names for the same mechanism"},
                    {"zh": "SSE 负责持久化，EventV2 负责传输，KeyedMutex 负责投影", "en": "SSE handles persistence, EventV2 handles transport, KeyedMutex handles projection"},
                    {"zh": "KeyedMutex 用 session ID 为 key，正是 EventV2 的跨设备定序", "en": "KeyedMutex keys by session ID, which is exactly EventV2's cross-device ordering"},
                ],
                "answer": 0,
                "why": {"zh": "同一条事件流，多个角色各取所需：<strong>L11 SSE</strong> 是<strong>传输层</strong>——把新事件实时推给已连客户端；<strong>本课 EventV2</strong> 管这些事件如何被<strong>持久存下、用单调 seq 定序、并让多设备靠重放追平</strong>；<strong>L19 投影器</strong>再把带 seq 的事件投成读模型。<strong>L8 KeyedMutex</strong> 则是另一层面：<strong>进程内</strong>把同一文件/插件的并发操作串行（注意——L8 的 KeyedMutex 按<strong>文件路径/插件 id</strong> 加锁，不是 session ID；会话级串行是 run-coordinator）。所以三者不是同一机制、职责不可互换；最后一个选项还误把 KeyedMutex 说成按 session ID（错，已在 L8 厘清）。", "en": "One event stream, multiple roles: <strong>L11 SSE</strong> is the <strong>transport layer</strong>—pushing new events live to connected clients; <strong>this lesson's EventV2</strong> covers how those events get <strong>durably stored, ordered by a monotonic seq, and caught up across devices via replay</strong>; <strong>L19's projector</strong> then projects seq-bearing events into a read model. <strong>L8 KeyedMutex</strong> is a different layer: <strong>in-process</strong> serialization of same-file/plugin concurrency (note—L8's KeyedMutex locks by <strong>file path/plugin id</strong>, not session ID; per-session serialization is run-coordinator). So they're not one mechanism and their roles aren't interchangeable; the last option also wrongly says KeyedMutex keys by session ID (wrong, as clarified in L8)."},
            },
        ],
        "open": [
            {"zh": "课里把「单写入者 + 单调 seq」称作一种「<strong>用约束换简单</strong>」的工程智慧——与其去解「多写入者一致性」这个分布式难题，不如换一个不产生这个难题的设计。请你谈谈你对这种思路的理解：它和全书反复出现的「找准接缝、切开会变与不变」是什么关系？再举 2–3 个你熟悉的、「<strong>主动施加一个约束反而换来巨大简化</strong>」的系统设计例子（如不可变数据、单线程事件循环、append-only 日志、CRDT 的限定场景等），并谈谈「什么时候该坚持这个约束、什么时候它会变成枷锁」。", "en": "The lesson calls \"single-writer + monotonic seq\" an engineering wisdom of \"<strong>trading a constraint for simplicity</strong>\"—rather than solving the distributed hard problem of \"multi-writer consistency,\" switch to a design that doesn't produce it. Discuss your understanding of this idea: how does it relate to the book's recurring \"find the seam, cut what changes from what doesn't\"? Give 2–3 examples you know of \"<strong>deliberately imposing a constraint that buys huge simplification</strong>\" (e.g. immutable data, single-threaded event loops, append-only logs, CRDTs' bounded scenarios), and discuss \"when to hold the constraint vs when it becomes a shackle.\""},
            {"zh": "课里指出 EventV2、L11(SSE 传输)、L19(投影历史)、L15(事件溯源) 共用<strong>同一条事件流</strong>，只是各取一个切面。请你以一句用户操作（比如「在终端发了一句话，想在网页上实时看到回复」）为例，把这条事件从「产生 → 定序持久化(本课) → 实时传输(L11) → 投影成消息(L19) → 另一设备重放追平(本课)」完整地走一遍，说明每一步谁在做、为什么需要它。再谈谈「事件溯源（把状态变化记成不可变事件流，而非直接改当前态）」这种架构，给 opencode 这类需要回放/多端/可定责的系统带来了哪些好处，又有什么代价。", "en": "The lesson notes EventV2, L11(SSE transport), L19(projected history), L15(event sourcing) share <strong>one event stream</strong>, each taking a facet. Using one user action (say \"typed a message in the terminal, want to see the reply live on the web\"), trace one event all the way through \"generate → order &amp; persist (this lesson) → live transport (L11) → project into a message (L19) → another device replays to catch up (this lesson)\", saying who does each step and why it's needed. Then discuss what \"event sourcing (recording state changes as an immutable event stream rather than mutating current state)\" buys a system like opencode that needs replay/multi-end/accountability, and at what cost."},
        ],
    },

    "63-test-contribute.html": {
        "mcq": [
            {
                "q": {"zh": "课里反复点出一条「暗线」，说它能解释 opencode 测试与贡献规范里所有看似零散的规矩。这条暗线是什么？", "en": "The lesson repeatedly points to a \"hidden line\" said to explain every seemingly-scattered rule in opencode's testing and contribution norms. What is it?"},
                "opts": [
                    {"zh": "在 AI 能批量生成代码与文字的时代，<strong>死守信噪比、敬重维护者的时间</strong>——issue 先行（防重复劳动）、PR 小而专注+说清如何验证（让审阅者省力、能复现）、禁止 AI 长篇大论、vouch 名单除名灌水者，全是这一个意图的不同侧面", "en": "In an age where AI can mass-produce code and text, <strong>fiercely guard the signal-to-noise ratio and respect maintainers' time</strong>—issue-first (prevent duplicate work), small focused PRs + explain how you verified (ease reviewers, enable reproduction), no AI walls of text, vouch denouncing spammers, all facets of this one intent"},
                    {"zh": "尽可能提高自动化程度，让 CI 取代人工审阅", "en": "Maximize automation so CI replaces human review"},
                    {"zh": "强制所有贡献者使用 opencode 这个 AI 工具来写代码", "en": "Force all contributors to use the opencode AI tool to write code"},
                    {"zh": "通过严格规矩把贡献者数量控制在最少", "en": "Use strict rules to keep the number of contributors to a minimum"},
                ],
                "answer": 0,
                "why": {"zh": "课里把所有规矩归到同一个意图：<strong>在 AI 放大一切的时代，死守信噪比、敬重维护者的时间</strong>。逐条看背后的统一逻辑：「issue 先行」防重复劳动、让维护者提前拦下不合适方向；「PR 小而专注 + 说清你怎么验证」让审阅者快速读懂、能复现你的结论；「禁止 AI 长篇大论」「issue 必须用模板、空泛自动关」过滤掉<strong>体量大但信息密度低</strong>的噪声；vouch 名单干脆把「反复提交低质量 AI 贡献」列为除名理由。最妙的反差是——一个本身就是 AI 编程助手的项目，却在门口竖最严的牌子：别把<strong>未经你消化</strong>的 AI 产物倾倒给维护者。所以不是「让 CI 取代人工」（恰恰是保护人工审阅的注意力）、不是「强制用 opencode 写」、也不是「把人挡在外面」（vouch 默认对所有人开放）。", "en": "The lesson ties every rule to one intent: <strong>in an age where AI amplifies everything, guard the signal-to-noise ratio and respect maintainers' time</strong>. The unified logic, rule by rule: \"issue first\" prevents duplicate work and lets maintainers head off unfit directions; \"small focused PR + explain how you verified\" lets reviewers grasp quickly and reproduce; \"no AI walls of text\" and \"issues must use a template, vague ones auto-close\" filter <strong>high-volume, low-density</strong> noise; the vouch list flatly names \"repeatedly submitting low-quality AI contributions\" as grounds for denouncement. The neatest contrast—a project that is itself an AI coding agent plants the strictest sign at its gate: don't dump <strong>undigested</strong> AI output on maintainers. So it's not \"let CI replace humans\" (it precisely protects human reviewing attention), not \"force using opencode,\" nor \"keep people out\" (vouch is open to everyone by default)."},
            },
            {
                "q": {"zh": "opencode 根目录的 <span class=\"mono\">test</span> 脚本被故意写成 <span class=\"mono\">echo 'do not run tests from root' &amp;&amp; exit 1</span>。这个设计最贴切的解读是？", "en": "opencode's root <span class=\"mono\">test</span> script is deliberately written as <span class=\"mono\">echo 'do not run tests from root' &amp;&amp; exit 1</span>. The aptest reading of this design is?"},
                "opts": [
                    {"zh": "这是一道<strong>故意设的护栏</strong>：monorepo 里测试应在各包目录跑，根目录跑要么语义不清要么一锅乱炖，于是用一句响亮报错当场拦住你并提示正确姿势——同 L37/L48/L53「让用错的姿势立刻、响亮地失败」", "en": "It's a <strong>deliberate guardrail</strong>: in a monorepo tests should run in each package dir; running at the root is either unclear or stews everything together, so a loud error blocks you on the spot and hints the right posture—like L37/L48/L53 \"let wrong usage fail immediately and loudly\""},
                    {"zh": "opencode 根本没有测试，所以脚本只能报错", "en": "opencode has no tests at all, so the script can only error"},
                    {"zh": "这是个临时的 bug，作者忘了写真正的测试命令", "en": "It's a temporary bug; the author forgot to write the real test command"},
                    {"zh": "为了禁止贡献者运行任何测试", "en": "To forbid contributors from running any tests"},
                ],
                "answer": 0,
                "why": {"zh": "这不是 bug、更不是「没测试」（全仓 500 多个 <span class=\"mono\">*.test.ts</span>），而是<strong>有意的护栏</strong>。opencode 是 monorepo，每个包有自己的测试与环境，正确姿势是 <span class=\"mono\">cd packages/opencode &amp;&amp; bun test</span>。若放任你在根目录跑，结果要么语义不清、要么把所有包一锅乱炖，徒增困惑。与其让你跑出莫名其妙的结果，不如<strong>当场用一句响亮报错拦住你</strong>、并告诉你正确做法——这正是全书反复出现的「让用错的姿势立刻、响亮地失败」：L37 stale 工具调用即抛、L48 库非空却无表即抛、L53 Provider 外用 context 即抛。一个深思熟虑的项目，会把「容易踩的坑」提前变成「踩到就报警」。所以「没有测试」「临时 bug」「禁止跑测试」都误读了——它恰恰是<strong>引导你在对的地方跑测试</strong>。", "en": "This is neither a bug nor \"no tests\" (500-plus <span class=\"mono\">*.test.ts</span> repo-wide), but a <strong>deliberate guardrail</strong>. opencode is a monorepo; each package has its own tests and environment, and the right posture is <span class=\"mono\">cd packages/opencode &amp;&amp; bun test</span>. Letting you run at the root would be either semantically unclear or stew all packages together, adding only confusion. Rather than baffling results, <strong>block you on the spot with a loud error</strong> and tell you the right way—exactly the book's recurring \"let wrong usage fail immediately and loudly\": L37 throwing on a stale tool call, L48 throwing when the DB is non-empty but lacks the table, L53 throwing when a context is used outside its Provider. A thoughtful project turns \"easy pitfalls\" into \"trips an alarm on contact\" ahead of time. So \"no tests,\" \"temporary bug,\" and \"forbid testing\" all misread it—it precisely <strong>guides you to run tests in the right place</strong>."},
            },
            {
                "q": {"zh": "opencode 的 vouch 信任系统（<span class=\"mono\">.github/VOUCHED.td</span>）有 vouched / everyone-else / denounced 三档。它对「AI 时代噪声」的应对，精妙在哪？", "en": "opencode's vouch trust system (<span class=\"mono\">.github/VOUCHED.td</span>) has three tiers: vouched / everyone-else / denounced. Where lies its elegance in handling \"AI-age noise\"?"},
                "opts": [
                    {"zh": "在于<strong>分寸</strong>：默认对所有人开放（无需背书就能开 issue/PR、不因你没背书就拒你），只对「反复提交低质量 AI 贡献/灌水/恶意」者亮红牌自动关，且明确「除名不用于意见分歧或诚实失误」——既开放又有底线", "en": "In its <strong>proportion</strong>: open to everyone by default (open issues/PRs without being vouched, not rejected for lacking a vouch), red-flagging and auto-closing only those who \"repeatedly submit low-quality AI contributions/spam/bad faith,\" while explicitly stating \"denouncement is not for disagreements or honest mistakes\"—both open and with a bottom line"},
                    {"zh": "在于默认拒绝所有未背书用户，只有 vouched 才能贡献", "en": "In rejecting all non-vouched users by default; only the vouched can contribute"},
                    {"zh": "在于用 AI 自动判断每个 PR 的质量并打分", "en": "In using AI to automatically judge and score each PR's quality"},
                    {"zh": "在于只要意见与维护者不合就会被除名", "en": "In denouncing anyone who disagrees with maintainers"},
                ],
                "answer": 0,
                "why": {"zh": "vouch 系统的精妙在<strong>分寸</strong>：三档里「everyone else（其他所有人）」<strong>无需背书</strong>也能正常开 issue/PR——默认开放、不设墙；只有「denounced（已除名）」的 issue/PR 自动关闭，而这一档<strong>专门</strong>留给「反复提交低质量 AI 贡献、灌水、恶意行为」者，CONTRIBUTING 还明确声明「<strong>除名不用于意见分歧或诚实的失误</strong>」。所以它是一套既<strong>开放</strong>（不预设你是坏人、不因没背书就拒你）又<strong>有底线</strong>（绝不让少数灌水者拖垮维护者）的信任机制。选项里「默认拒绝所有未背书」「只有 vouched 能贡献」与「默认开放」相悖；「AI 自动打分」无此机制；「意见不合就除名」恰被文档明确否定。", "en": "The vouch system's elegance is in <strong>proportion</strong>: among the three tiers, \"everyone else\" can open issues/PRs normally <strong>without</strong> being vouched—open by default, no wall; only \"denounced\" issues/PRs auto-close, and that tier is <strong>reserved</strong> for those who \"repeatedly submit low-quality AI contributions, spam, or act in bad faith,\" with CONTRIBUTING explicitly stating \"<strong>denouncement is not for disagreements or honest mistakes</strong>.\" So it's a trust mechanism both <strong>open</strong> (doesn't presume you're a bad actor, won't reject you for lacking a vouch) and with a <strong>bottom line</strong> (never lets a spamming few drag down maintainers). The options \"reject all non-vouched by default\" and \"only vouched can contribute\" contradict \"open by default\"; \"AI auto-scoring\" is no such mechanism; \"denounce on disagreement\" is precisely what the docs reject."},
            },
        ],
        "open": [
            {"zh": "课里反复强调一条「暗线」：opencode 的测试与贡献规范，全为「在 AI 能批量生成的时代，死守信噪比、敬重维护者时间」服务，并把「禁止 AI 长篇大论」「vouch 除名反复灌低质量 AI 内容者」当作这条暗线最锋利的体现。请你谈谈这个<strong>耐人寻味的反差</strong>：一个本身就是 AI 编程助手的项目，为什么要在贡献门口对「未经消化的 AI 产物」竖起最严的牌子？结合你对「AI 是放大器，放大的可以是信号也可以是噪声」这句话的理解，谈谈在 AI 大量介入开源协作的当下，「判断与提炼仍是人的责任」为什么不该被工具的便利所稀释。", "en": "The lesson stresses a \"hidden line\": opencode's testing and contribution norms all serve \"in an age of AI mass-production, guard the signal-to-noise ratio and respect maintainers' time,\" treating \"no AI walls of text\" and \"vouch denouncing repeat low-quality-AI-content submitters\" as its sharpest expression. Discuss this <strong>thought-provoking contrast</strong>: why does a project that is itself an AI coding agent plant the strictest sign against \"undigested AI output\" at its contribution gate? Drawing on your reading of \"AI is an amplifier, amplifying signal or noise,\" discuss why, now that AI heavily enters open-source collaboration, \"judgment and distillation remain a human responsibility\" should not be diluted by the tool's convenience."},
            {"zh": "课里把「测试不能在根目录跑（根脚本故意报错）」与全书 L37/L48/L53 的「让用错的姿势立刻、响亮地失败」串在一起，又把「少用 mock、测真实实现、要能被审阅者复现」提炼为「测试是写给未来要读它、要信它的人看的」。请你结合这两点，谈谈你对「好的测试与好的报错」的理解：为什么「假绿」（mock 都顺但真实环境崩、或测试只是把逻辑抄了一遍）比「红」更危险？以及，「把容易踩的坑提前变成踩到就报警」这种防御式设计，在你自己的项目里可以用在哪些地方（举 2-3 个具体例子）？", "en": "The lesson threads \"tests can't run at the root (the root script deliberately errors)\" together with the book's L37/L48/L53 \"let wrong usage fail immediately and loudly,\" and distills \"few mocks, test the real implementation, be reproducible by reviewers\" into \"a test is written for whoever will read and trust it in the future.\" Drawing on both, discuss your understanding of \"good tests and good errors\": why is \"fake green\" (mocks all pass but the real environment crashes, or a test merely copies the logic) more dangerous than \"red\"? And where, in your own projects, can this defensive design of \"turn easy pitfalls into trips-an-alarm-on-contact ahead of time\" apply (give 2-3 concrete examples)?"},
        ],
    },

    "62-build-debug.html": {
        "mcq": [
            {
                "q": {"zh": "课里反复强调 <span class=\"mono\">bun dev</span> 和 <span class=\"mono\">opencode</span> 是「同一个 CLI 的两副面孔」。这个判断最准确的含义是？", "en": "The lesson stresses that <span class=\"mono\">bun dev</span> and <span class=\"mono\">opencode</span> are \"two faces of the same CLI.\" What's the most accurate meaning?"},
                "opts": [
                    {"zh": "它们跑的是同一套代码、同一套命令（<span class=\"mono\">serve</span>/<span class=\"mono\">web</span>/<span class=\"mono\">&lt;目录&gt;</span> 一一对应），只是「跑法」不同——<span class=\"mono\">bun dev</span> 把源码喂给运行时即时执行（开发回路），<span class=\"mono\">opencode</span> 是把源码编译固化成的二进制（生产成品）", "en": "They run the same code and same commands (<span class=\"mono\">serve</span>/<span class=\"mono\">web</span>/<span class=\"mono\">&lt;dir&gt;</span> correspond one-to-one), differing only in \"how they run\"—<span class=\"mono\">bun dev</span> feeds source to the runtime for instant execution (dev loop), <span class=\"mono\">opencode</span> is the binary compiled and fixed from that source (production product)"},
                    {"zh": "<span class=\"mono\">bun dev</span> 是开发版、<span class=\"mono\">opencode</span> 是功能更全的正式版，两者代码不同", "en": "<span class=\"mono\">bun dev</span> is a dev edition and <span class=\"mono\">opencode</span> a more full-featured release edition, with different code"},
                    {"zh": "<span class=\"mono\">bun dev</span> 只能跑 TUI，<span class=\"mono\">opencode</span> 只能跑服务器", "en": "<span class=\"mono\">bun dev</span> can only run the TUI, <span class=\"mono\">opencode</span> only the server"},
                    {"zh": "<span class=\"mono\">opencode</span> 是 <span class=\"mono\">bun dev</span> 的一个子命令", "en": "<span class=\"mono\">opencode</span> is a subcommand of <span class=\"mono\">bun dev</span>"},
                ],
                "answer": 0,
                "why": {"zh": "关键认知：<span class=\"mono\">bun dev</span> 不是「另一个程序」，它就是<strong>本地从源码跑的 <span class=\"mono\">opencode</span></strong>。两者跑同一套 CLI，命令一一对应（<span class=\"mono\">bun dev serve</span>↔<span class=\"mono\">opencode serve</span>、<span class=\"mono\">web</span>、<span class=\"mono\">&lt;目录&gt;</span>），唯一区别是「跑法」：<span class=\"mono\">bun dev</span> 直接把 TypeScript 源码喂给 Bun 运行时即时执行（省掉编译、秒级反馈，适合高频「改一点看一眼」的开发回路）；<span class=\"mono\">opencode</span> 是 <span class=\"mono\">build.ts</span> 把同一份源码编译固化成的单文件二进制（生产成品）。理解这点的价值：很多项目「开发模式」和「生产模式」是两套入口两套配置，常出「开发能复现、装好却不行」的灵异 bug；opencode 让两者共用一份代码、只差源码跑 vs 编译跑，从根上消除了这类差异。所以选项里「代码不同」「功能不同」「子命令」都错了——它们本就是一份代码的两种运行方式。", "en": "Key realization: <span class=\"mono\">bun dev</span> is not \"another program,\" it <strong>is <span class=\"mono\">opencode</span> run locally from source</strong>. Both run the same CLI, commands one-to-one (<span class=\"mono\">bun dev serve</span>↔<span class=\"mono\">opencode serve</span>, <span class=\"mono\">web</span>, <span class=\"mono\">&lt;dir&gt;</span>), the only difference being \"how they run\": <span class=\"mono\">bun dev</span> feeds TypeScript source straight to the Bun runtime for instant execution (no compile, second-level feedback, suited to the high-frequency \"tweak, glance\" dev loop); <span class=\"mono\">opencode</span> is the single-file binary <span class=\"mono\">build.ts</span> compiled and fixed from that same source (production product). Why it matters: many projects have separate entries/configs for \"dev\" and \"production,\" breeding ghostly \"reproduces in dev, fails installed\" bugs; opencode lets both share one codebase, differing only source-run vs compiled-run, eliminating that at the root. So \"different code,\" \"different features,\" and \"subcommand\" are all wrong—they're literally one codebase run two ways."},
            },
            {
                "q": {"zh": "<span class=\"mono\">build.ts</span> 把<strong>业务代码 + Web UI + models.dev 数据</strong>三样东西全编进一个二进制，产物不依赖 node_modules/运行时。这个「把一切嵌进一个自包含产物」的思路，最贴切的类比与意义是？", "en": "<span class=\"mono\">build.ts</span> compiles <strong>business code + Web UI + models.dev data</strong>, all three, into one binary, depending on neither node_modules nor a runtime. The aptest analogy and significance of this \"embed everything into one self-contained artifact\" idea is?"},
                "opts": [
                    {"zh": "同 Rust 的 rust-embed 等「编译期资源内嵌」：编译期把所有依赖固化进单一产物、运行期零外部依赖，于是部署极简（一个文件）、版本绝不错配、<span class=\"mono\">curl | bash</span> 一行装好且跨平台", "en": "Like Rust's rust-embed and other \"compile-time resource embedding\": fix all dependencies into a single artifact at compile time, zero external deps at runtime, so deployment is dead-simple (one file), versions never mismatch, and <span class=\"mono\">curl | bash</span> installs in one line, cross-platform"},
                    {"zh": "它把 Web UI 和模型数据放在二进制旁边的文件夹里，运行时再去加载", "en": "It puts the Web UI and model data in a folder next to the binary, loaded at runtime"},
                    {"zh": "它每次运行都从网上拉取最新的 models.dev 数据", "en": "It fetches the latest models.dev data from the network on every run"},
                    {"zh": "它只是把 TypeScript 转成 JavaScript，仍需用户自己装 Node 和依赖", "en": "It merely transpiles TypeScript to JavaScript, still requiring users to install Node and deps themselves"},
                ],
                "answer": 0,
                "why": {"zh": "<span class=\"mono\">build.ts</span> 用 Bun 的 <span class=\"mono\">Bun.build({compile})</span>「编译成单文件可执行程序」：①业务代码 bundle+minify 成一份；②Web UI 先 build 再把 dist 每个文件 <span class=\"mono\">import ... with {type:\"file\"}</span> <strong>编进二进制内部</strong>（<span class=\"mono\">createEmbeddedWebUIBundle</span>）；③models.dev 数据用 <span class=\"mono\">define</span> 注入成常量（<strong>编译时写死</strong>，不是运行时拉网）。「嵌」是字面意义的嵌入——产物是<strong>单独一个文件</strong>、里头什么都有，不依赖 node_modules/运行时。这正是 rust-embed 式「编译期把依赖固化进单一产物、运行期零外部依赖」的思路：部署极简、启动快、版本绝不错配（资源和代码编在一起）。意义直接落到分发：<span class=\"mono\">curl | bash</span> 下一个文件、<span class=\"mono\">chmod +x</span> 就跑，跨平台矩阵让每台机器都下到为它编好的原生文件。所以「放旁边文件夹」「运行时拉网」「仍需装 Node」都与「自包含」相悖。", "en": "<span class=\"mono\">build.ts</span> uses Bun's <span class=\"mono\">Bun.build({compile})</span> \"compile to a single executable\": ① business code bundled+minified into one; ② Web UI built first, then every dist file <span class=\"mono\">import ... with {type:\"file\"}</span> <strong>compiled inside the binary</strong> (<span class=\"mono\">createEmbeddedWebUIBundle</span>); ③ models.dev data injected as a constant via <span class=\"mono\">define</span> (<strong>hardcoded at compile time</strong>, not fetched at runtime). \"Embed\" is literal—the artifact is <strong>a single file</strong> with everything inside, depending on neither node_modules nor a runtime. This is exactly rust-embed's \"fix dependencies into a single artifact at compile time, zero external deps at runtime\": simple deployment, fast startup, never-mismatched versions (resources and code compiled together). The significance lands directly on distribution: <span class=\"mono\">curl | bash</span> one file, <span class=\"mono\">chmod +x</span>, run; the cross-platform matrix means each machine downloads a native file compiled for it. So \"folder next to it,\" \"fetch at runtime,\" and \"still install Node\" all contradict \"self-contained.\""},
            },
            {
                "q": {"zh": "课里说调试器那个「<span class=\"mono\">bun dev</span> 下断点不触发」的坑，恰恰是一扇「窥见 opencode 运行时结构的窗口」。它揭示了什么、解法又印证了什么？", "en": "The lesson says the debugger pitfall (\"breakpoints under <span class=\"mono\">bun dev</span> don't trigger\") is precisely a \"window into opencode's runtime structure.\" What does it reveal, and what does the fix confirm?"},
                "opts": [
                    {"zh": "揭示 <span class=\"mono\">bun dev</span> 把 server 跑在 <strong>worker 线程</strong>里（主线程的断点映不进去）；解法 <span class=\"mono\">bun dev spawn</span> 或「单独起 server 进程 + <span class=\"mono\">opencode attach</span> 接 TUI」分开调，正印证了 L09–L13 的<strong>客户端/服务器分离</strong>架构——server 是能独立存在的进程", "en": "Reveals that <span class=\"mono\">bun dev</span> runs the server in a <strong>worker thread</strong> (the main thread's breakpoints don't map in); the fix—<span class=\"mono\">bun dev spawn</span>, or \"start the server as a separate process + <span class=\"mono\">opencode attach</span> the TUI\" to debug separately—confirms exactly the <strong>client/server separation</strong> architecture of L09–L13: the server is a process that can exist independently"},
                    {"zh": "揭示 Bun 不支持断点，必须改用 Chrome DevTools 才能调试", "en": "Reveals Bun doesn't support breakpoints, so you must switch to Chrome DevTools to debug"},
                    {"zh": "揭示 server 和 TUI 是同一个线程，无法分开", "en": "Reveals the server and TUI are the same thread and can't be separated"},
                    {"zh": "揭示断点必须写在 <span class=\"mono\">build.ts</span> 里才有效", "en": "Reveals breakpoints only work if written in <span class=\"mono\">build.ts</span>"},
                ],
                "answer": 0,
                "why": {"zh": "坑的链条：你想在 server 代码下断点→<span class=\"mono\">--inspect</span> 跑 <span class=\"mono\">bun dev</span>→但 <span class=\"mono\">bun dev</span> 把 server 跑在一个 <strong>worker 线程</strong>里→断点装在主线程调试器上、映不进 worker 线程→不触发。解法一：<span class=\"mono\">bun dev spawn</span>（让 server 不进 worker 线程跑）。解法二：把 server 和 TUI <strong>彻底分开调</strong>——单独 <span class=\"mono\">--inspect</span> 起 server（<span class=\"mono\">serve --port 4096</span>）、再 <span class=\"mono\">opencode attach</span> 接 TUI；或单独调 TUI（加 <span class=\"mono\">--conditions=browser</span>）。能这样分头调，不是调试器的功劳，而是<strong>架构本就把 server 和 TUI 解耦成独立进程/客户端</strong>（L09–L13）的副产品——又一次「好架构在意想不到处还你便利」（同 L61 move-session）。所以「Bun 不支持断点」「同一线程不可分」「断点写 build.ts」都错。", "en": "The pitfall chain: you want a breakpoint in server code → run <span class=\"mono\">bun dev</span> with <span class=\"mono\">--inspect</span> → but <span class=\"mono\">bun dev</span> runs the server in a <strong>worker thread</strong> → the breakpoint sits on the main-thread debugger, doesn't map into the worker → won't trigger. Fix one: <span class=\"mono\">bun dev spawn</span> (run the server outside the worker thread). Fix two: debug the server and TUI <strong>entirely separately</strong>—start the server alone with <span class=\"mono\">--inspect</span> (<span class=\"mono\">serve --port 4096</span>), then <span class=\"mono\">opencode attach</span> the TUI; or debug the TUI alone (with <span class=\"mono\">--conditions=browser</span>). Being able to debug them apart isn't the debugger's doing but a byproduct of <strong>the architecture having decoupled server and TUI into an independent process/client</strong> (L09–L13)—again \"good architecture pays back convenience in unexpected places\" (like L61's move-session). So \"Bun doesn't support breakpoints,\" \"same thread, inseparable,\" and \"breakpoints in build.ts\" are all wrong."},
            },
        ],
        "open": [
            {"zh": "课里把 <span class=\"mono\">bun dev</span>（从源码即时跑、秒级反馈）与 <span class=\"mono\">build.ts --single</span>（编译成自包含二进制）描述成开发者实战回路的两端，并点出二者「同一份 CLI、同一套代码，只是跑法不同」。请你谈谈「开发期从源码即时跑、发布期编译成自包含产物」这种双形态对一个项目的价值：它如何同时照顾「开发的高频迭代体验」与「分发的零依赖体验」？再结合你的经验，谈谈当「开发模式」和「生产模式」走的是两套不同代码路径时，通常会埋下哪些隐患（如「开发能跑、上线就挂」），以及 opencode「两者共用一份代码」的做法为什么能从根上避免它。", "en": "The lesson casts <span class=\"mono\">bun dev</span> (run from source instantly, second-level feedback) and <span class=\"mono\">build.ts --single</span> (compile to a self-contained binary) as the two ends of a developer's practical loop, noting they are \"the same CLI, the same code, just run differently.\" Discuss the value of this dual form—\"run from source instantly during development, compile to a self-contained artifact for release\"—to a project: how does it serve both \"the high-frequency-iteration experience of development\" and \"the zero-dependency experience of distribution\"? Drawing on your experience, discuss what hidden risks usually get buried when \"dev mode\" and \"production mode\" take two different code paths (e.g. \"runs in dev, crashes in prod\"), and why opencode's \"both share one codebase\" approach avoids them at the root."},
            {"zh": "课里盛赞 <span class=\"mono\">build.ts</span> 把 Web UI 和模型数据「编译期嵌进二进制」、把以前很麻烦的「打包成单文件可执行程序」变成一个 <span class=\"mono\">Bun.build</span> 调用，并称这又一次是「站在成熟工具的肩膀上」（同 L39 借 Ripgrep、L51 借 git、L59 借语言服务器）。请你谈谈「编译期资源内嵌、零运行时依赖」这种发布形态的取舍：它换来了部署极简、版本绝不错配、跨平台原生分发，又付出了什么代价（产物体积、换资源要重编、构建复杂度）？再谈谈这种「能力几乎免费得来，全靠底层工具（Bun）把难事变简单」的现象，对你选型技术栈有何启发——什么时候值得为「一个工具贯穿装依赖→跑源码→编成品全程」买单？", "en": "The lesson praises <span class=\"mono\">build.ts</span> for \"embedding the Web UI and model data into the binary at compile time\" and turning the once-painful \"package into a single-file executable\" into a single <span class=\"mono\">Bun.build</span> call, calling it another case of \"standing on the shoulders of mature tools\" (like L39 borrowing Ripgrep, L51 git, L59 language servers). Discuss the trade-offs of this \"compile-time resource embedding, zero runtime dependency\" release form: it buys dead-simple deployment, never-mismatched versions, and cross-platform native distribution—but at what cost (artifact size, recompiling to swap resources, build complexity)? Then discuss what this phenomenon—\"the capability comes almost for free, all because a low-level tool (Bun) makes the hard thing simple\"—teaches you about choosing a tech stack: when is it worth paying for \"one tool spanning install-deps → run-source → compile-product\"?"},
        ],
    },

    "61-acp-location.html": {
        "mcq": [
            {
                "q": {"zh": "L59 里 opencode 是 LSP 客户端，L61 里它是 ACP 服务器。这对「镜像」是什么意思？", "en": "In L59 opencode is an LSP client, in L61 it's an ACP server. What does this \"mirror\" mean?"},
                "opts": [
                    {"zh": "L59 opencode 消费语言服务器的代码智能（当「编辑器」那头）；L61 opencode 实现 ACP（Agent Client Protocol）被编辑器（如 Zed）消费当 AI 后端（当「agent 服务」那头）。ACP 之于 agent 正如 LSP 之于语言服务器——都用标准协议把 M×N 塌缩成 M+N", "en": "L59 opencode consumes language servers' code intelligence (the \"editor\" end); L61 opencode implements ACP (Agent Client Protocol), consumed by editors (like Zed) as an AI backend (the \"agent service\" end). ACP is to agents what LSP is to language servers—both use a standard protocol to collapse M×N into M+N"},
                    {"zh": "ACP 和 LSP 是同一个协议", "en": "ACP and LSP are the same protocol"},
                    {"zh": "opencode 不能同时做客户端和服务器", "en": "opencode can't be both client and server"},
                    {"zh": "ACP 取代了 opencode 的 TUI", "en": "ACP replaced opencode's TUI"},
                ],
                "answer": 0,
                "why": {"zh": "L59 里 opencode 戴「LSP 客户端」帽子，去消费别人的语言服务器（typescript-language-server…）的代码智能——它是「编辑器」那一头。L61 里它戴「ACP 服务器」帽子：ACP（Agent Client Protocol）是让编辑器和 AI agent 对话的标准协议（Zed 等接入 agent 用的）。opencode 实现它（acp/agent.ts 的 Agent 类实现 ACPAgent 接口：initialize/authenticate/newSession/loadSession/forkSession/prompt/cancel/setSessionModel·Mode·ConfigOption），于是别的编辑器能把 opencode 当 AI 后端驱动——它是「agent 服务」那一头。ACP 之于 agent 正如 LSP 之于语言服务器：都用一套标准协议把「M 编辑器×N agent」塌缩成 M+N。意义：让 opencode 内核挣脱「只能用自家 TUI」，Zed 用户不离开 Zed 就能用 opencode。这是 L56「数据与表现分离」在协议层的终极形态——前端可替换范围扩到整个生态。", "en": "In L59 opencode wears the \"LSP client\" hat, going to consume others' language servers' (typescript-language-server…) code intelligence—it's the \"editor\" end. In L61 it wears the \"ACP server\" hat: ACP (Agent Client Protocol) is the standard protocol letting editors and AI agents talk (what Zed etc. use to connect agents). opencode implements it (acp/agent.ts's Agent class implements the ACPAgent interface: initialize/authenticate/newSession/loadSession/forkSession/prompt/cancel/setSessionModel·Mode·ConfigOption), so other editors can drive opencode as their AI backend—it's the \"agent service\" end. ACP is to agents what LSP is to language servers: both use a standard protocol to collapse \"M editors × N agents\" into M+N. The significance: freeing opencode's core from \"usable only in its own TUI,\" a Zed user uses opencode without leaving Zed. This is the ultimate form of L56's \"data separated from presentation\" at the protocol level—frontend replaceability expanded to the whole ecosystem."},
            },
            {
                "q": {"zh": "opencode 的 Location 抽象（{directory, workspaceID?, project}）+「工具/权限/文件系统全 Location 作用域」带来了什么深远的解耦？", "en": "What profound decoupling does opencode's Location abstraction ({directory, workspaceID?, project}) + \"tools/permissions/filesystem all Location-scoped\" bring?"},
                "opts": [
                    {"zh": "把「会话是谁要干什么」（身份逻辑）与「会话在哪儿跑」（位置）解耦成两件正交可替换的事——会话的灵魂不再焊死在某目录，换个 Location 同一会话就能在新目录、用新文件系统/权限视图继续跑", "en": "Decouples \"who the session is, what it wants\" (identity logic) from \"where the session runs\" (location) into two orthogonal, replaceable things—the session's soul is no longer welded to a directory, switch a Location and the same session keeps running under a new directory, with a new filesystem/permission view"},
                    {"zh": "让会话跑得更快", "en": "Makes sessions run faster"},
                    {"zh": "把所有会话存进一个目录", "en": "Stores all sessions in one directory"},
                    {"zh": "Location 只是个日志字段", "en": "Location is just a log field"},
                ],
                "answer": 0,
                "why": {"zh": "Location（location.ts）回答「一个会话到底在哪儿干活」：一份极简位置信息 {directory(工作目录), workspaceID?(可选，为集群/远程放置预留), project(解析出的项目)}。核心设计决定让它分量极重：工具、权限、文件系统、模型解析、SessionRunner 全是 Location 作用域的——「能读写哪些文件」「权限怎么算」「用哪个模型」都相对一个 Location 确定、而非写死全局。这把「会话是谁要干什么」（身份逻辑）和「会话在哪儿跑」（位置）变成两件正交、可分别替换的事：会话的灵魂（消息/上下文/意图）不再和某目录焊死，换个 Location 同一会话就能在新目录、用新文件系统视图和权限继续跑。它实现成 Effect Service（M2 DI）：子系统通过依赖 Location.Service 确定作用域，而非各摸全局「当前目录」——因为位置是注入的非写死的，换 Location 整个会话的文件系统/权限/可跑命令整体平移、逻辑代码零改。这是「解耦『是什么』与『在哪里』」在系统最底层的落地。", "en": "Location (location.ts) answers \"where exactly does a session work\": a minimal location info {directory (working dir), workspaceID? (optional, reserved for cluster/remote placement), project (resolved project)}. A core design decision makes it hugely weighty: tools, permissions, filesystem, model resolution, SessionRunner are all Location-scoped—\"which files can be read/written,\" \"how permissions compute,\" \"which model\" are all determined relative to a Location, not hardcoded globally. This turns \"who the session is, what it wants\" (identity logic) and \"where the session runs\" (location) into two orthogonal, separately-replaceable things: the session's soul (messages/context/intent) is no longer welded to a directory, switch a Location and the same session keeps running under a new directory, with a new filesystem view and permissions. It's implemented as an Effect Service (M2 DI): subsystems determine their scope by depending on Location.Service rather than each reaching for a global \"current directory\"—because location is injected not hardcoded, switching a Location shifts the whole session's filesystem/permissions/runnable-commands wholesale, zero logic change. This is \"decoupling 'what' from 'where'\" landing at the system's deepest level."},
            },
            {
                "q": {"zh": "move-session（会话能搬到另一个目录继续，可选带上文件改动）为什么说它是「Location 解耦地基上自然生长的果」？", "en": "Why is move-session (a session can move to another directory to continue, optionally carrying file changes) called \"a fruit naturally grown on the Location-decoupling foundation\"?"},
                "opts": [
                    {"zh": "正因会话逻辑早已和「具体在哪个目录」剥离，「换目录继续」不过是「给它新 Location + 把改动带过去」——没为它写专门的复杂逻辑，是地基上自然长出的果（积木相扣，同 L60）", "en": "Precisely because the session's logic was long peeled apart from \"which directory it's in,\" \"continue in another directory\" is no more than \"give it a new Location + bring the changes over\"—no complex logic written specially for it, a fruit naturally grown on the foundation (blocks interlocking, like L60)"},
                    {"zh": "move-session 用了一套全新的会话引擎", "en": "move-session uses a brand-new session engine"},
                    {"zh": "它把会话复制了一份", "en": "It copies the session"},
                    {"zh": "搬家会丢失所有上下文", "en": "Moving loses all context"},
                ],
                "answer": 0,
                "why": {"zh": "move-session（control-plane/move-session.ts）让会话整体搬到另一目录继续。流程：①校验目的项目须匹配（DestinationProjectMismatchError——不能搬到属于完全不同项目的目录，否则上下文乱）；②可选连同文件改动搬（moveChanges）：用 git 在源目录捕获未提交改动、在目的目录应用（CaptureChangesError/ApplyChangesError 守着）——又一次复用 git（同 L51 快照），连「桌上的草稿」都不落下。关键：这一切之所以可能、不是天方夜谭，根全在 Location 解耦——正因会话逻辑早已和「具体在哪个目录」剥离，「换目录继续」才不过是「给它新 Location + 把改动带过去」这么自然的一件事，根本没为它写专门复杂逻辑。一个好的底层抽象（Location）会在意想不到的上层（move-session）开花——这是 L60 末「积木相扣」主题的又一印证：会话可移动这个看似高级的能力，只是「会话本就和位置解耦」地基上自然生长的果。", "en": "move-session (control-plane/move-session.ts) lets a session move wholesale to another directory to continue. Flow: ① validate the destination project must match (DestinationProjectMismatchError—can't move to a directory belonging to a completely different project, else the context scrambles); ② optionally move file changes along (moveChanges): use git to capture uncommitted changes in the source directory and apply them in the destination (CaptureChangesError/ApplyChangesError guarding)—reusing git again (like L51 snapshots), not leaving even \"the drafts on the desk\" behind. The key: all this is possible, not a fantasy, entirely thanks to the Location decoupling—precisely because the session's logic was long peeled apart from \"which directory it's in,\" \"continue in another directory\" is no more than \"give it a new Location + bring the changes over,\" a natural thing, with no complex logic written specially for it. A good low-level abstraction (Location) blossoms in unexpected upper layers (move-session)—another proof of L60's closing \"blocks interlocking\" theme: this seemingly advanced \"session is movable\" capability is just a fruit naturally grown on the foundation of \"the session is already decoupled from location.\""},
            },
        ],
        "open": [
            {"zh": "课里把这一课的主线提炼为「解耦『是什么』与『在哪里』」——ACP 解耦 agent 与编辑器、Location 解耦会话与目录，并把 ACP 称作 LSP 的镜像（opencode 既当 LSP 客户端消费语言服务器、又当 ACP 服务器被编辑器消费）。请你谈谈「标准协议」这种东西为什么有如此大的解耦威力：它把「M×N 套专用对接」塌缩成「M+N 套协议对接」的本质是什么？再举几个你熟悉的「靠一套标准协议解耦了一个生态」的例子（HTTP、SQL、POSIX、USB、OAuth），并谈谈成为「协议的实现者」（而非协议的发明者）对一个产品的战略价值。", "en": "The lesson distills this lesson's throughline as \"decoupling 'what' from 'where'\"—ACP decouples agent from editor, Location decouples session from directory, calling ACP the mirror of LSP (opencode is both an LSP client consuming language servers and an ACP server consumed by editors). Discuss why a \"standard protocol\" has such great decoupling power: what's the essence of collapsing \"M×N dedicated integrations\" into \"M+N protocol integrations\"? Give a few examples you know of \"a standard protocol decoupling an ecosystem\" (HTTP, SQL, POSIX, USB, OAuth), and discuss the strategic value to a product of being a \"protocol implementer\" (rather than the protocol's inventor)."},
            {"zh": "课里盛赞 Location 这个极小的数据类是一条「接缝」——它实现成 Effect Service（DI），让工具/权限/文件系统通过依赖它确定作用域、而非各摸全局「当前目录」，于是「换地方」从「改一堆硬编码路径」变成「换一个注入值」；还指出 workspaceID 这个可选字段「为未来集群/远程放置留门」。请你结合 M2 的依赖注入，谈谈「把一个横切一切的关注点（如『当前位置』『当前用户』『当前租户』）抽成可注入的作用域服务」这种模式的威力：它如何让系统天然支持多租户/多位置/可测试？反过来，过度依赖注入、把太多东西做成可注入作用域，又可能带来什么复杂度？「为未来留门」（如 workspaceID）和「YAGNI（你不会需要它）」之间，你怎么把握？", "en": "The lesson praises the tiny Location data class as a \"seam\"—implemented as an Effect Service (DI), letting tools/permissions/filesystem determine their scope by depending on it rather than each reaching for a global \"current directory,\" so \"switching places\" turns from \"changing a pile of hardcoded paths\" into \"swapping one injected value\"; it also notes the optional workspaceID field \"leaves a door open for future cluster/remote placement.\" From M2's dependency injection, discuss the power of this \"abstract a concern cutting across everything (like 'current location,' 'current user,' 'current tenant') into an injectable scoped service\" pattern: how does it make a system naturally support multi-tenancy/multi-location/testability? Conversely, what complexity might over-relying on DI, making too many things injectable scopes, bring? Between \"leaving a door open for the future\" (like workspaceID) and \"YAGNI (You Aren't Gonna Need It),\" how do you strike the balance?"},
        ],
    },

    "60-pty-shell.html": {
        "mcq": [
            {
                "q": {"zh": "为什么 opencode 光有批处理的 bash 工具（L39）还不够，非得搞一套 PTY 真终端？", "en": "Why isn't opencode's batch bash tool (L39) enough, requiring a PTY real-terminal infrastructure too?"},
                "opts": [
                    {"zh": "有些程序非真终端不可——交互式 REPL（要边看输出边输入）、检测到 TTY 才显示彩色/进度条的程序、需实时打字进去的命令；批处理一问一答、不能中途输入、程序也知道没连终端", "en": "Some programs require a real terminal—interactive REPLs (read output while typing input), programs showing color/progress bars only on a TTY, commands you type into in real time; batch is one-shot Q&A, can't input mid-way, and the program knows it's not attached to a terminal"},
                    {"zh": "PTY 比批处理跑得快", "en": "PTY runs faster than batch"},
                    {"zh": "批处理不能跑 shell 命令", "en": "Batch can't run shell commands"},
                    {"zh": "纯粹是为了好看", "en": "Purely for aesthetics"},
                ],
                "answer": 0,
                "why": {"zh": "L39 已澄清：bash 工具经 AppProcess 走批处理（spawn 子进程、跑完收 stdout），PTY 是另一套。区别不是快慢而是能不能交互。批处理一问一答：给命令、等跑完、收 stdout，不能中途输入，程序也知道自己没连终端（常不输出彩色/进度条），适合「跑个命令拿结果」给模型。但有些程序非真终端不可：交互式 REPL（你得能边看输出边输入）、会检测「自己是否连着终端」才显示彩色/进度条的程序、需要实时打字进去的命令——批处理对这些无能为力。PTY 给的是真终端：流式看输出、随时打字（write）、能 resize，程序「以为」连着真人于是放心交互。PTY 把真终端抽象成极简的 Proc 接口（onData/write/resize/onExit/kill），由 Bun/Node 两套实现满足同一接口，平台差异藏在接口下（同 L52 opentui、L46 MCP transport）。", "en": "L39 already clarified: the bash tool goes batch via AppProcess (spawn a child process, run to completion, collect stdout), PTY is a separate thing. The difference isn't fast/slow but interactive-or-not. Batch is one-shot Q&A: give a command, wait, collect stdout, can't input mid-way, and the program knows it's not attached to a terminal (often omits color/progress bars), suited to \"run a command, get the result\" for the model. But some programs require a real terminal: interactive REPLs (you must read output while typing input), programs that detect \"am I attached to a terminal?\" before showing color/progress bars, commands you type into in real time—batch is helpless with these. PTY gives a real terminal: stream output, type anytime (write), can resize, the program \"thinks\" it's attached to a live person and interacts confidently. PTY abstracts a real terminal into a minimal Proc interface (onData/write/resize/onExit/kill), with Bun/Node two implementations satisfying the same interface, platform difference hidden under the interface (like L52 opentui, L46 MCP transport)."},
            },
            {
                "q": {"zh": "创建 PTY 时，它的环境变量是按「调用方值 → 宿主覆盖 → 核心强制终端不变量(TERM 等)」分层叠加的。这个顺序为什么这么排？", "en": "When creating a PTY, its env vars are stacked in order \"caller values → host overlay → core-forced terminal invariants (TERM etc.).\" Why this order?"},
                "opts": [
                    {"zh": "可定制的在中间、不可妥协的在最后压住一切——越后优先级越高；TERM/OPENCODE_TERMINAL 是「真终端之所以是真终端」的底线，不能被任何中间层（哪怕好心插件）改坏，故最后强制写入、享最高优先级", "en": "Customizable in the middle, non-negotiable last overriding all—the later the higher priority; TERM/OPENCODE_TERMINAL are the bottom line of \"what makes a real terminal real,\" can't be broken by any middle layer (even a well-meaning plugin), so force-written last, getting the highest priority"},
                    {"zh": "按字母顺序排的", "en": "Arranged alphabetically"},
                    {"zh": "随便排的、顺序无所谓", "en": "Arranged arbitrarily, order doesn't matter"},
                    {"zh": "核心不变量在最底层", "en": "Core invariants at the bottom layer"},
                ],
                "answer": 0,
                "why": {"zh": "CONTEXT.md 写明：PTY 创建合并调用方值、再叠宿主覆盖、最后核心强制终端不变量如 TERM。这个顺序编码了优先级哲学：①最底=调用方基础环境（合理起点，如继承 process.env）；②中间=可定制口子，通过 shell.env 插件钩子（正是 L58「改草稿」钩子的触发点）让组织/用户注入自己的环境变量（内部 npm 镜像、代理地址等）；③最上=opencode 强制盖上、谁也覆盖不了的终端不变量。为什么 TERM/OPENCODE_TERMINAL 放最后压住一切？因为它们是「真终端之所以是真终端」的底线——少了 TERM 程序就不知用什么终端类型渲染、彩色和光标控制全乱套。这些不能让任何中间层（哪怕好心插件）改坏，故必须最后强制写入。叠加里越往后优先级越高，「不可妥协的底线」就该享最高优先级——既给足定制灵活性、又守住底线。这是老练系统的分寸。", "en": "CONTEXT.md spells out: PTY creation merges caller values, then stacks the host overlay, then core-forced terminal invariants like TERM. This order encodes a priority philosophy: ① bottom = caller's base environment (a reasonable starting point, e.g. inherit process.env); ② middle = customizable hatch, via the shell.env plugin hook (exactly L58's \"edit a draft\" hook's trigger point) letting orgs/users inject their own env vars (internal npm mirror, proxy address, etc.); ③ top = the terminal invariants opencode forcibly stamps that no one can override. Why put TERM/OPENCODE_TERMINAL last overriding all? Because they're the bottom line of \"what makes a real terminal real\"—without TERM a program doesn't know which terminal type to render with, color and cursor control all break. These can't be broken by any middle layer (even a well-meaning plugin), so must be force-written last. In the stacking the later the higher priority, the \"non-negotiable bottom line\" deserves the highest priority—both giving ample customization flexibility and holding the bottom line. This is a seasoned system's sense of proportion."},
            },
            {
                "q": {"zh": "PTY 的环境「中间层」（宿主覆盖）是怎么实现的？这体现了什么设计之美？", "en": "How is the PTY environment's \"middle layer\" (host overlay) implemented? What design beauty does this embody?"},
                "opts": [
                    {"zh": "直接复用 L58 的 shell.env 插件钩子——plugin.trigger(\"shell.env\",{cwd},{env:{}}) 递空草稿让插件填；新需求用现成机制一拼即成，说明 L58 的接缝找得准、抽象通用到能意外复用（积木相扣）", "en": "Directly reuses L58's shell.env plugin hook—plugin.trigger(\"shell.env\",{cwd},{env:{}}) hands an empty draft for plugins to fill; a new need snaps together from an existing mechanism, showing L58's seam was found accurately, the abstraction generic enough for unexpected reuse (blocks interlocking)"},
                    {"zh": "为 PTY 环境专门发明了一套新机制", "en": "A new mechanism specially invented for PTY environment"},
                    {"zh": "硬编码一份固定的环境变量", "en": "Hardcodes a fixed set of env vars"},
                    {"zh": "让用户手动改配置文件", "en": "Lets the user manually edit a config file"},
                ],
                "answer": 0,
                "why": {"zh": "pty-environment 插件的 get() 实现就是：plugin.trigger(\"shell.env\", {cwd: input.cwd}, {env:{}}).pipe(map(result => result.env))——正是 L58 讲的「改草稿」：opencode 递一个空的 {env:{}} 草稿、插件往里填，最后拿插件改过的 env 作为「宿主覆盖」那一层。于是 PTY 的环境定制根本不需要为它发明新机制，直接复用了已有的 shell.env 插件钩子。这正是设计良好系统的「积木相扣」之美：L58 造好的 shell.env 钩子是一块通用积木，到 L60 的 PTY 环境这里它恰好就是「中间那一层可定制覆盖」，严丝合缝嵌进去。当你发现「这个新需求用现成机制一拼即成」时，往往说明前面那些抽象的接缝找得准——它们不是为某一处专门造的，而是通用到能在意想不到的地方再次复用。另外 CONTEXT.md 点出干净的职责切分：PTY 环境是服务器层的事、非 Core PTY 的事——Core 只造终端（纯机制），配什么环境（策略）留给更懂上下文的上层（切开机制与策略）。", "en": "The pty-environment plugin's get() implementation is exactly: plugin.trigger(\"shell.env\", {cwd: input.cwd}, {env:{}}).pipe(map(result => result.env))—exactly L58's \"edit a draft\": opencode hands an empty {env:{}} draft, plugins fill into it, finally the plugin-edited env is taken as the \"host overlay\" layer. So PTY environment customization needn't invent a new mechanism at all, directly reusing the existing shell.env plugin hook. This is the \"building blocks interlocking\" beauty of a well-designed system: the shell.env hook L58 built is a generic block, and here at L60's PTY environment it happens to be exactly \"that customizable overlay in the middle,\" snapping in perfectly. When you find \"this new need is just a snap-together of some existing mechanism,\" it often means the earlier abstraction seams were found accurately—they weren't built for one spot but are generic enough to be reused again in unexpected places. Also CONTEXT.md points out a clean separation of responsibility: the PTY environment is a server-layer concern, not a Core PTY one—Core only makes the terminal (pure mechanism), what env to configure (policy) is left to the more context-aware upper layer (cut mechanism from policy)."},
            },
        ],
        "open": [
            {"zh": "课里反复礼赞 PTY 的环境叠加「可定制的在中间、不可妥协的在最后压住一切」——通过叠加顺序让插件能灵活注入、又让 TERM 等终端不变量绝不被改坏。请你提炼这种「用『层的顺序』来表达『优先级/不可覆盖性』」的设计模式，并把它和你见过的类似机制串起来：CSS 的 !important 与层叠顺序、Kubernetes 的 admission webhook 链、配置的 defaults→user→forced 三层、防火墙规则的顺序。它们如何用「顺序」编码「谁能覆盖谁」？设计这类系统时，把「强制项」放最后（最高优先级）相比放最前，安全性上各有何利弊？", "en": "The lesson repeatedly praises PTY's env stacking \"customizable in the middle, non-negotiable last overriding all\"—using the stacking order to let plugins inject flexibly yet never let TERM and other terminal invariants be broken. Distill this \"use 'layer order' to express 'priority/non-overridability'\" design pattern, connecting it with similar mechanisms you've seen: CSS's !important and cascade order, Kubernetes admission webhook chains, config's defaults→user→forced three layers, firewall rule order. How do they use \"order\" to encode \"who can override whom\"? Designing such systems, what are the security pros/cons of putting \"forced items\" last (highest priority) versus first?"},
            {"zh": "课里说一个能让人实时打字进去的 PTY 终端是极强的能力，若谁都能连就是天大的安全洞，于是用「短时、限定作用域、一次性」的 ticket 令牌守门（60 秒 TTL、绑死 ptyID+目录+工作区）。请你结合 L41 权限、L46 MCP 的 OAuth，提炼 opencode 反复出现的「把强大能力绑定到严格授权」的安全设计原则。再设计一个思想实验：如果让你为「远程连接一个正在运行的 agent 终端」设计授权，你会怎样权衡 ticket 的 TTL（太长不安全、太短体验差）、作用域粒度、是否一次性、能否续期？短时令牌相比长期 token / session cookie，在「强能力短暴露窗口」上的优势是什么？", "en": "The lesson says a PTY terminal you can type into in real time is an extremely strong capability, a giant security hole if anyone could attach, so it's guarded with \"short-lived, scope-limited, one-time\" tickets (60s TTL, bound to ptyID+directory+workspace). From L41 permissions and L46 MCP's OAuth, distill opencode's recurring \"bind strong capability to strict authorization\" security design principle. Then design a thought experiment: if you designed authorization for \"remotely attaching to a running agent terminal,\" how would you weigh the ticket's TTL (too long unsafe, too short poor UX), scope granularity, one-time-ness, renewability? What's the advantage of short-lived tickets over long-lived tokens / session cookies in \"a short exposure window for a strong capability\"?"},
        ],
    },

    "59-lsp.html": {
        "mcq": [
            {
                "q": {"zh": "opencode 怎么给 agent「代码智能」（诊断、跳定义、看类型）？", "en": "How does opencode give the agent \"code intelligence\" (diagnostics, jump-to-def, see types)?"},
                "opts": [
                    {"zh": "不自造，而是说标准 LSP 协议、跑和 VS Code 同源的语言服务器（typescript-language-server/gopls/pyright…）——opencode 当 LSP 客户端，语言服务器是独立进程，JSON-RPC 对话；复用整个语言服务器生态", "en": "Doesn't build its own but speaks standard LSP and runs same-source language servers as VS Code (typescript-language-server/gopls/pyright…)—opencode is the LSP client, language servers are separate processes, JSON-RPC dialogue; reusing the entire language-server ecosystem"},
                    {"zh": "自己为每种语言实现一套编译器/类型检查器", "en": "Implements its own compiler/type-checker for each language"},
                    {"zh": "靠大模型直接猜代码的类型", "en": "Relies on the LLM to directly guess code types"},
                    {"zh": "只用 grep 搜索文本", "en": "Uses only grep text search"},
                ],
                "answer": 0,
                "why": {"zh": "给 agent 代码智能，自造每种语言的理解器是天坑（要重实现 TS 编译器、Go 类型检查器…）。opencode 站到巨人肩上：说 LSP（Language Server Protocol）——VS Code/Neovim 共用的标准协议，于是能直接跑和 VS Code 一模一样的语言服务器。LSP 当初就是为解「M 编辑器 × N 语言」难题：各自对接是 M×N 套适配，LSP 定一套标准协议让两边各对接协议、塌缩成 M+N。opencode 把自己当又一个「编辑器」接进去：lsp/client.ts=LSP 客户端，真正懂语言的是独立进程的语言服务器，两者 JSON-RPC 对话；lsp/server.ts=按文件扩展名匹配的语言服务器注册表（找/装二进制，如 .go→gopls 没装就 go install）。这是全书「复用成熟工具」最壮观一例（同 L39 Ripgrep、L51 git）——复用整个语言服务器生态，opencode 一行语言分析代码都不写就让 agent 有了顶级 IDE 同源的代码理解力。", "en": "Giving an agent code intelligence by building each language's understander is a bottomless pit (reimplement the TS compiler, Go type-checker…). opencode stands on a giant's shoulders: speaks LSP (Language Server Protocol)—the standard protocol shared by VS Code/Neovim, so it can run the exact same language servers as VS Code. LSP was invented to solve the \"M editors × N languages\" problem: each pairing is M×N adapters, LSP defines one standard protocol so both sides pair only with it, collapsing to M+N. opencode plugs in as yet another \"editor\": lsp/client.ts=LSP client, what truly understands the language is separate-process language servers, the two in JSON-RPC dialogue; lsp/server.ts=a by-extension registry of language servers (find/install the binary, e.g. .go→gopls, go install if absent). This is the book's most spectacular case of \"reusing a mature tool\" (like L39 Ripgrep, L51 git)—reusing the entire language-server ecosystem, opencode writes not one line of language analysis yet gives the agent code understanding from the same source as a top IDE."},
            },
            {
                "q": {"zh": "代码智能的「诊断」一面是被动自动的。它的反馈回路怎么转？diagnostic.report 为什么只报 ERROR、每文件封顶 20 条？", "en": "Code intelligence's \"diagnostics\" face is passive-automatic. How does its feedback loop turn? Why does diagnostic.report report only ERROR, capping at 20 per file?"},
                "opts": [
                    {"zh": "agent 改文件→didChange 通知服务器→服务器 publishDiagnostics 推回→report 格式化(只留 ERROR、每文件≤20、<diagnostics> 包裹)→喂 agent；有界是因诊断占模型宝贵上下文，全报会淹没真正要命的编译错误（同 L42）", "en": "agent edits file→didChange notifies server→server publishDiagnostics pushes back→report formats (keep only ERROR, ≤20 per file, <diagnostics> wrap)→feed agent; bounded because diagnostics occupy the model's precious context, reporting all would drown the truly fatal compile errors (like L42)"},
                    {"zh": "agent 必须主动开口问才有诊断", "en": "The agent must actively ask to get diagnostics"},
                    {"zh": "report 报所有级别的诊断、不设上限", "en": "report reports all severity levels with no cap"},
                    {"zh": "诊断只在程序崩溃时才生成", "en": "Diagnostics are only generated when the program crashes"},
                ],
                "answer": 0,
                "why": {"zh": "诊断是被动自动的：agent 改完文件→opencode 经 didChange 通知语言服务器→服务器分析后 publishDiagnostics 推回诊断→diagnostic.ts 的 report 整理成 agent 读得懂的样子→喂给 agent。report 做三件克制事：只留 severity===1 的 ERROR（滤掉 warn/hint 噪音）、每文件最多 20 条（超出附「... and N more」）、<diagnostics file> 包裹，无错误返空串。pretty 把每条格成 ERROR [行:列] 消息（行列 +1 对齐编辑器 1-based）。为什么克制？因为诊断要占模型宝贵上下文（同 L42 有界输出的焦虑）：几百条 warning 一股脑塞给模型既烧 token 又淹没真正要命的编译错误。「只报错误、且有界」是「让 agent 看见问题」与「别撑爆注意力」间的精准拿捏——给 agent 的反馈越准越好、非越多越好，信息过载与缺失同样有害。这把 agent 从盲改者变成能即时收到「改对了/改崩了」反馈的自我纠错编码者（喂 M4 循环）。", "en": "Diagnostics are passive-automatic: agent edits file→opencode notifies the language server via didChange→the server analyzes and publishDiagnostics pushes back→diagnostic.ts's report tidies into something the agent can read→feed the agent. report does three restrained things: keep only severity===1 ERROR (filter warn/hint noise), at most 20 per file (append \"... and N more\" if over), <diagnostics file> wrap, return empty if no errors. pretty shapes each into ERROR [line:col] message (line/col +1 to match the editor's 1-based). Why restrained? Because diagnostics occupy the model's precious context (the same anxiety as L42 bounded output): stuffing hundreds of warnings into the model both burns tokens and drowns the truly fatal compile errors. \"Report only errors, and bounded\" is the precise calibration between \"letting the agent see problems\" and \"not overflowing its attention\"—feedback to the agent is better the more precise, not the more, information overload and absence equally harmful. This turns the agent from a blind editor into a self-correcting coder who instantly receives \"got it right / broke it\" (feeding M4's loop)."},
            },
            {
                "q": {"zh": "代码智能的「lsp 工具」一面（主动按需）相比 agent 以前靠 grep 理解代码，强在哪？", "en": "How is code intelligence's \"lsp tool\" face (active on-demand) stronger than the agent previously understanding code via grep?"},
                "opts": [
                    {"zh": "直接问语言服务器拿语义级精确答案（这个 foo 定义在哪行、类型是什么、引用它的是哪十处）；grep 同名符号有十几个、分不清哪个是真定义、更给不出类型——从「文本级猜」升级到「语义级知」", "en": "Asks the language server directly for semantic-level precise answers (which line foo is defined, its type, the ten spots referencing it); grep has a dozen same-named symbols, can't tell which is the real definition, much less give the type—upgrading from \"text-level guessing\" to \"semantic-level knowing\""},
                    {"zh": "lsp 工具搜索更快", "en": "The lsp tool searches faster"},
                    {"zh": "lsp 工具能改代码", "en": "The lsp tool can modify code"},
                    {"zh": "两者没区别", "en": "There's no difference"},
                ],
                "answer": 0,
                "why": {"zh": "lsp 工具（tool/lsp.ts）是主动按需的：agent 想精确理解某处代码就调它问语言服务器。它把 IDE 的代码导航做成 9 个操作：goToDefinition/goToImplementation（跳定义/实现）、findReferences（找引用）、hover（看类型/文档）、documentSymbol/workspaceSymbol（列文件/全工程符号）、callHierarchy incoming/outgoing（调用层级）；参数 filePath+line+character（1-based，对齐编辑器坐标）。它和诊断是「一被动一主动」互补：诊断是 opencode 塞给 agent（你改崩了），lsp 工具是 agent 主动拉（这是什么）。为什么珍贵？agent 此前靠 grep 一个名字理解代码，但同名符号可能十几个，grep 分不清哪个是真定义、更给不出类型；lsp 工具直接问语言服务器，拿语义级精确答案：foo 定义在那文件那行、类型是这个、引用它的就这十处。从「文本级的猜」升级到「语义级的知」，让 agent 在大型陌生代码库导航第一次有了近人类用 IDE 的精度。诊断（被动看见错）+lsp 工具（主动查清楚）=完整的「会看红线、能精确跳转」开发者之眼。", "en": "The lsp tool (tool/lsp.ts) is active on-demand: when the agent wants to precisely understand some code it calls it to ask the language server. It turns IDE code navigation into 9 operations: goToDefinition/goToImplementation (jump def/impl), findReferences (find refs), hover (see type/docs), documentSymbol/workspaceSymbol (list file/whole-project symbols), callHierarchy incoming/outgoing (call hierarchy); params filePath+line+character (1-based, matching editor coordinates). It and diagnostics are a \"one passive one active\" complement: diagnostics opencode pushes to the agent (you broke it), the lsp tool the agent actively pulls (what is this). Why precious? The agent previously understood code by grep-ing a name, but a same-named symbol may have a dozen, grep can't tell which is the real definition, much less give the type; the lsp tool asks the language server directly for semantic-level precise answers: foo is defined in that file at that line, its type is this, the ones referencing it are these ten spots. Upgrading from \"text-level guessing\" to \"semantic-level knowing,\" giving the agent's large-codebase navigation, for the first time, precision close to a human using an IDE. Diagnostics (passively seeing errors) + lsp tool (actively asking clearly) = a complete pair of \"see red lines, jump precisely\" developer's eyes."},
            },
        ],
        "open": [
            {"zh": "课里把 opencode 集成 LSP 称作全书「复用成熟工具」智慧最壮观的一次——复用整个语言服务器生态（typescript-language-server/gopls/pyright…），一行语言分析代码都不写。请你把它和 L39 复用 Ripgrep、L51 复用 git（影子仓库）、L52 复用 SolidJS 渲染范式串起来，提炼 opencode 一以贯之的「不重造轮子、站在成熟生态肩上」的工程哲学：怎样判断一个能力「该复用现成的、还是该自己造」？复用一个庞大外部生态（要管理子进程、协议版本、二进制安装）带来的复杂度与依赖风险，又该如何权衡？", "en": "The lesson calls opencode integrating LSP the book's most spectacular case of \"reusing a mature tool\"—reusing the entire language-server ecosystem (typescript-language-server/gopls/pyright…), writing not one line of language analysis. Connect it with L39 reusing Ripgrep, L51 reusing git (shadow repo), L52 reusing the SolidJS rendering paradigm, distilling opencode's consistent \"don't reinvent the wheel, stand on a mature ecosystem's shoulders\" engineering philosophy: how to judge whether a capability \"should reuse something ready-made or build your own\"? How to weigh the complexity and dependency risk of reusing a huge external ecosystem (managing child processes, protocol versions, binary installs)?"},
            {"zh": "课里反复强调诊断的「有界」（只报 ERROR、每文件 20 条），并把它和 L42 有界工具输出归为对「模型注意力稀缺」的同一种敬畏，提炼出『给 agent 的反馈越准越好、非越多越好，信息过载与缺失同样有害』。请你结合 agent 编码的实际，谈谈「给 LLM 的反馈/上下文」的『信噪比』为什么如此关键：哪些信息是高信噪比（编译 ERROR、失败的测试）、哪些是低信噪比（风格 warning、冗长日志）？一个 agent 系统该如何系统性地为模型「过滤噪音、突出要害」？过度过滤又可能漏掉什么（比如某些 warning 其实预示了真 bug）？", "en": "The lesson repeatedly stresses diagnostics' \"boundedness\" (report only ERROR, 20 per file), grouping it with L42 bounded tool output as the same reverence for \"the model's scarce attention,\" distilling \"feedback to the agent is better the more precise, not the more, information overload and absence equally harmful.\" From the reality of agent coding, discuss why the \"signal-to-noise ratio\" of \"feedback/context given to the LLM\" is so crucial: which information is high SNR (compile ERRORs, failing tests), which is low SNR (style warnings, verbose logs)? How should an agent system systematically \"filter noise, highlight the critical\" for the model? What might over-filtering miss (e.g. some warnings actually foreshadow real bugs)?"},
        ],
    },

    "58-plugin-hooks.html": {
        "mcq": [
            {
                "q": {"zh": "opencode 插件的绝大多数钩子签名都是 (input, output) => Promise<void>，返回 void。插件怎么靠它施加影响？", "en": "Most opencode plugin hooks have the signature (input, output) => Promise<void>, returning void. How does a plugin exert influence through it?"},
                "opts": [
                    {"zh": "「改草稿」——opencode 先算一份默认 output，把(只读 input, 可变 output)交给每个插件，插件就地改 output 几个字段，opencode 拿最终的 output 继续干活；插件不返回新值，只在宿主给的草稿上涂改", "en": "\"Edit a draft\"—opencode first computes a default output, hands (read-only input, mutable output) to each plugin, the plugin edits a few fields of output in place, opencode takes the final output and carries on; the plugin doesn't return a new value, only marks up the draft the host gave"},
                    {"zh": "插件 return 一个新对象替换掉 output", "en": "The plugin returns a new object replacing output"},
                    {"zh": "插件 throw 一个异常来传值", "en": "The plugin throws an exception to pass a value"},
                    {"zh": "插件直接修改 opencode 的全局变量", "en": "The plugin directly modifies opencode's global variables"},
                ],
                "answer": 0,
                "why": {"zh": "所有钩子共享同一个「改草稿」机制：签名 (input, output) => Promise<void>，返回 void、靠就地改 output 生效。input 是只读上下文（现在什么情况），output 是可变草稿对象（改它来施加影响）。触发机制：opencode 先算一份默认 output，plugin.trigger(钩子名, input, 默认output) 把(input,output)交给每个注册该钩子的插件，每个在 output 上涂改一笔，最后 opencode 拿这份被层层涂改过的 output 继续干活。插件不是「返回新值替换」，而是「在 opencode 递来的草稿上改几笔」。好处：①opencode 永远给默认值拿最终值，主动权在宿主、零插件也能正常工作；②多插件可叠加，后者看得到前者的改动（同 L41/L44 层叠）；③草稿的完整结构由 opencode 保证，插件只改几个字段，避免「插件返回残缺对象」。这个「传入可变草稿、就地修改」同 L54 produce。", "en": "All hooks share the same \"edit a draft\" mechanism: signature (input, output) => Promise<void>, returns void, takes effect by editing output in place. input is read-only context (what the situation is), output is a mutable draft object (edit it to exert influence). The trigger mechanism: opencode first computes a default output, plugin.trigger(hookName, input, defaultOutput) hands (input,output) to each plugin that registered the hook, each marks up the output, finally opencode takes this layer-by-layer marked-up output and carries on. The plugin doesn't \"return a new value to replace\" but \"marks up a few strokes on the draft opencode handed.\" Benefits: ① opencode always gives the default and takes the final, initiative with the host, works fine with zero plugins; ② multiple plugins can stack, later ones see earlier edits (like L41/L44 stacking); ③ the draft's complete structure is guaranteed by opencode, the plugin only edits a few fields, avoiding \"plugin returns a defective object.\" This \"pass a mutable draft, modify in place\" is like L54 produce."},
            },
            {
                "q": {"zh": "tool.execute.before 和 tool.execute.after 这对钩子，为什么是做审计/日志/安全过滤等「横切关注点」的理想位置？", "en": "Why is the pair tool.execute.before and tool.execute.after the ideal spot for \"cross-cutting concerns\" like audit/logging/security filtering?"},
                "opts": [
                    {"zh": "它们像三明治夹住工具的真正执行（before 改 args、after 改结果）；你不必改 read/write/bash/grep 每个工具的代码，只在这对钩子写一遍逻辑就一次性套用到所有工具——一处编写、处处生效", "en": "They sandwich the tool's actual execution (before changes args, after changes the result); you needn't change read/write/bash/grep every tool's code, just write the logic once in this pair to apply to all tools at once—write once, take effect everywhere"},
                    {"zh": "它们让工具执行得更快", "en": "They make tool execution faster"},
                    {"zh": "它们只能用于 bash 工具", "en": "They only work for the bash tool"},
                    {"zh": "它们绕过了权限系统", "en": "They bypass the permission system"},
                ],
                "answer": 0,
                "why": {"zh": "tool.execute.before(input={tool,sessionID,callID}, output={args}) 在工具执行前改 args；tool.execute.after(input={tool,…,args}, output={title,output,metadata}) 在执行后改结果。它俩像一对三明治把工具的真正执行夹在中间：before 能在工具跑起来前最后改一次参数或记录下来做审计，after 能在工具跑完后对结果再加工。这正是横切关注点（审计、日志、安全过滤、结果脱敏）的理想位置——你不必改任何一个具体工具(read/write/bash/grep…)的代码，只要在这对钩子写一遍逻辑就一次性套用到所有工具。试想没有它们，想给「每个工具调用记一笔审计」就得改每个工具的代码，既繁琐又易漏；而 before/after 把这件事收敛成一处编写、处处生效。另外 shell.env 让插件给 opencode 跑的 shell 命令注入环境变量（接 L60 PTY environment）。", "en": "tool.execute.before(input={tool,sessionID,callID}, output={args}) changes args before tool execution; tool.execute.after(input={tool,…,args}, output={title,output,metadata}) changes the result after. They're like a sandwich holding the tool's actual execution in between: before can make a last change to args before the tool runs or record them for audit, after can rework the result once the tool finishes. This is the ideal spot for cross-cutting concerns (audit, logging, security filtering, result redaction)—you needn't change any concrete tool's (read/write/bash/grep…) code, just write the logic once in this pair to apply to all tools at once. Imagine without them, to \"log an audit entry per tool call\" you'd change every tool's code, tedious and easily missed; before/after converge this into write once, take effect everywhere. Also shell.env lets plugins inject env vars into the shell commands opencode runs (connecting L60 PTY environment)."},
            },
            {
                "q": {"zh": "permission.ask 钩子让插件能改写权限裁决（allow/ask/deny）。它给 opencode 的权限系统带来了什么？", "en": "The permission.ask hook lets a plugin rewrite the permission verdict (allow/ask/deny). What does it bring to opencode's permission system?"},
                "opts": [
                    {"zh": "把 L41 权限向外敞开——企业可写插件用代码精确表达公司级安全策略（如生产目录下写操作一律 deny），权限从「内置规则+用户即时决定」扩展成「内置规则+用户决定+插件策略」三层", "en": "Opens L41 permissions outward—an enterprise can write a plugin expressing company-level security policies precisely in code (e.g. any write under the production directory always denied), extending permissions from \"built-in rules + user's instant decision\" to \"built-in rules + user decision + plugin policy,\" three layers"},
                    {"zh": "让权限询问弹得更快", "en": "Makes permission prompts pop faster"},
                    {"zh": "完全取代了 L41 的权限规则", "en": "Wholly replaces L41's permission rules"},
                    {"zh": "让插件能无视所有权限", "en": "Lets plugins ignore all permissions"},
                ],
                "answer": 0,
                "why": {"zh": "每当 opencode 要为某动作征求权限（回想 L41 allow/ask/deny），permission.ask(input=Permission, output={status}) 就被触发：opencode 按 L41 规则算出默认裁决填进 output.status，插件按自定义策略改 output.status，opencode 照最终 status 放行/询问/拒绝。这把第 41 课的权限系统向外敞开了一道口：企业可写插件，把「凡生产目录下的写操作一律 deny」「凡只读命令一律 allow」这样的公司级安全策略用代码精确表达，不必依赖用户每次手动点选。于是权限从「内置规则+用户即时决定」扩展成「内置规则+用户决定+插件策略」三层，把安全管控的能力交给组织。配合 auth/provider 钩子（注册自定义认证与模型 provider、接公司私有模型网关），插件钩子把 agent 最敏感的两端——守门(能不能动手)与接源(用谁的脑子)——都变成可由组织定制的策略。", "en": "Whenever opencode asks for permission for an action (recall L41 allow/ask/deny), permission.ask(input=Permission, output={status}) fires: opencode computes the default verdict per L41 rules into output.status, the plugin changes output.status per its custom policy, opencode allows/asks/denies per the final status. This opens lesson 41's permission system outward: an enterprise can write a plugin expressing company-level security policies precisely in code—\"any write under the production directory always denied,\" \"any read-only command always allowed\"—without relying on the user clicking each time. So permissions extend from \"built-in rules + user's instant decision\" to \"built-in rules + user decision + plugin policy,\" three layers, handing security control to the organization. Paired with the auth/provider hooks (register custom auth and model providers, connect a company's private model gateway), plugin hooks turn the agent's two most sensitive ends—gatekeeping (may it act) and connecting sources (whose brain)—both into organization-customizable policies."},
            },
        ],
        "open": [
            {"zh": "课里反复强调所有插件钩子「同构」——都是 (只读 input, 可变 output) => void 一个形状，并说这种统一形状同时降低了「插件作者的学习成本」和「宿主实现的复杂度」。请你对比这种「传入可变草稿、就地修改、返回 void」的拦截器模式，与其他几种常见的扩展/中间件模式：①返回新值替换（pure function pipeline）；②回调/事件 emit（观察者）；③洋葱模型 next() 中间件（Koa/Express）。它们各自如何把控制权和数据在「宿主 ↔ 扩展」间传递？在「让扩展能修改数据」与「让宿主掌控数据结构完整性」之间，opencode 的「改草稿」做了怎样的权衡？什么场景下你会选另一种？", "en": "The lesson repeatedly stresses all plugin hooks are \"isomorphic\"—all one shape (read-only input, mutable output) => void, saying this unified shape lowers both \"the plugin author's learning cost\" and \"the host's implementation complexity.\" Compare this \"pass a mutable draft, modify in place, return void\" interceptor pattern with other common extension/middleware patterns: ① return a new value to replace (pure function pipeline); ② callback/event emit (observer); ③ onion-model next() middleware (Koa/Express). How does each pass control and data between \"host ↔ extension\"? Between \"letting extensions modify data\" and \"letting the host control data-structure integrity,\" what trade-off does opencode's \"edit a draft\" make? In what scenario would you choose another?"},
            {"zh": "课里指出 opencode 自己内置的 Cloudflare/Copilot/Codex 等插件都用 chat.params 公开钩子来接自家模型，并称「opencode 用同一套公开钩子来接自己的模型，是对这套机制能力的最强背书」。请你谈谈这种「dogfooding——宿主用自己对外开放的扩展 API 来实现自己的核心功能」的设计实践：它给插件作者、给 API 质量分别带来什么保证？又有什么风险（公开 API 被内部需求绑架、内部能走捷径而第三方不能造成的不对等）？你见过哪些「把内部实现也建在公开扩展点上」的成功或失败案例？", "en": "The lesson notes opencode's own built-in Cloudflare/Copilot/Codex plugins all use the public chat.params hook to connect their own models, calling it \"opencode using the same public hooks to connect its own models is the strongest endorsement of this mechanism's capability.\" Discuss this \"dogfooding—the host uses its own externally-open extension API to implement its own core features\" design practice: what guarantees does it bring to plugin authors and to API quality respectively? What risks (the public API hijacked by internal needs, the inequity of internals taking shortcuts third parties can't)? What successful or failed cases of \"building internal implementations on public extension points too\" have you seen?"},
        ],
    },

    "57-plugin-system.html": {
        "mcq": [
            {
                "q": {"zh": "在 opencode 里，一个公开插件（@opencode-ai/plugin）本质上是什么？", "en": "In opencode, what is a public plugin (@opencode-ai/plugin) essentially?"},
                "opts": [
                    {"zh": "一个返回「钩子表」的 async 函数——Plugin = (input: PluginInput, options?) => Promise<Hooks>，无类无继承无样板，收一份上下文、返回一个 Hooks 对象", "en": "An async function returning a \"hook table\"—Plugin = (input: PluginInput, options?) => Promise<Hooks>, no class/inheritance/boilerplate, takes a context, returns a Hooks object"},
                    {"zh": "一个必须继承 AbstractPlugin 基类的类", "en": "A class that must inherit an AbstractPlugin base class"},
                    {"zh": "一个独立运行的微服务进程", "en": "A standalone microservice process"},
                    {"zh": "一段要编进 opencode 源码的代码", "en": "Code that must be compiled into opencode's source"},
                ],
                "answer": 0,
                "why": {"zh": "opencode 公开插件朴素得惊人：Plugin = (input: PluginInput, options?) => Promise<Hooks>——一个 async 函数，收一份 input 上下文、返回一个 Hooks 对象。无要继承的基类、无要实现的接口方法、无要注册的装饰器，就是「函数进、钩子出」。例子插件几行就注册一个自定义工具：async (ctx) => ({ tool: { mytool: tool({...}) } })。这种极简把「写一个插件」的门槛压到几乎为零——会写一个返回对象的 async 函数就会写 opencode 插件，剩下只是查那张钩子表有哪些键可填。对比传统插件框架的重器械（继承基类、实现一堆生命周期方法、DI 容器、XML 清单），opencode 削到只剩一个函数签名，因为看透了插件本质只需答两问：「你能给我什么」(PluginInput)+「你想何时介入」(Hooks)。呼应全书「最强抽象往往最朴素」（L36 Tool.make、L47 PluginV2.define、L53 createSimpleContext）。", "en": "opencode's public plugin is astonishingly plain: Plugin = (input: PluginInput, options?) => Promise<Hooks>—an async function, takes an input context, returns a Hooks object. No base class to inherit, no interface methods to implement, no decorator to register, just \"function in, hooks out.\" The example plugin registers a custom tool in a few lines: async (ctx) => ({ tool: { mytool: tool({...}) } }). This minimalism presses the barrier of \"writing a plugin\" to nearly zero—if you can write an async function returning an object you can write an opencode plugin, the rest is just looking up which keys you can fill in that hook table. Contrast the heavy machinery of traditional plugin frameworks (inherit a base class, implement a pile of lifecycle methods, a DI container, an XML manifest), opencode pares down to one function signature, because it sees through that a plugin's essence need only answer two questions: \"what can you give me\" (PluginInput) + \"when do you want to step in\" (Hooks). Echoes the book's \"the strongest abstraction is often the plainest\" (L36 Tool.make, L47 PluginV2.define, L53 createSimpleContext)."},
            },
            {
                "q": {"zh": "opencode 递给插件的 PluginInput 里，最点睛的是那个 client（SDK 客户端）。它意味着什么？", "en": "In the PluginInput opencode hands the plugin, the most eye-opening is that client (SDK client). What does it mean?"},
                "opts": [
                    {"zh": "插件不只是被动响应钩子，而是能主动操作 opencode——在钩子里读会话消息、发新消息、查配置；再配 Bun shell $ 还能跑外部命令。「宿主 API + shell」=既能感知又能驱动 opencode、还能伸手外部", "en": "The plugin isn't just a passive hook responder but can actively operate opencode—within a hook read session messages, send new messages, query config; paired with the Bun shell $ it can also run external commands. \"Host API + shell\" = it can sense and drive opencode, and reach outside"},
                    {"zh": "client 只能用来打印日志", "en": "client can only be used to print logs"},
                    {"zh": "client 是给 opencode 内核用的、插件不能碰", "en": "client is for opencode's core, plugins can't touch it"},
                    {"zh": "client 让插件运行得更快", "en": "client makes the plugin run faster"},
                ],
                "answer": 0,
                "why": {"zh": "PluginInput 是 opencode 递给插件的「工具箱」：client(opencode SDK 客户端)、project/directory/worktree、$(Bun shell)、serverUrl、experimental_workspace。最点睛的是 client——opencode 把自己的整套 API 客户端交到插件手里。这意味着插件不是只能被动响应钩子的「小跟班」，而是能主动操作 opencode 的完整公民：在钩子里读取当前会话消息、往会话发新消息、查询配置……再配那个 Bun shell $，插件甚至能跑任意外部命令、把结果带回。给插件「宿主的 API + 一个 shell」=给了它「既能感知 opencode、又能驱动 opencode、还能伸手到外部世界」的全部本钱——这正是一个强大插件系统该有的慷慨。这也是「浏览器扩展」类比的核心：宿主给扩展一套明确 API（读写页面/发请求）+ 一组事件钩子，扩展只说「某事发生时叫我」，双方只通过「API+钩子」契约打交道。", "en": "PluginInput is the \"toolbox\" opencode hands the plugin: client (opencode SDK client), project/directory/worktree, $ (Bun shell), serverUrl, experimental_workspace. The most eye-opening is client—opencode hands its entire API client into the plugin's hands. This means the plugin isn't a \"sidekick\" that can only passively respond to hooks, but a full citizen that can actively operate opencode: within a hook read the current session's messages, send a new message into the session, query config… Paired with that Bun shell $, the plugin can even run arbitrary external commands and bring results back. Giving the plugin \"the host's API + a shell\" = giving it all the capital to \"sense opencode, drive opencode, and reach the external world\"—exactly the generosity a powerful plugin system should have. This is also the core of the \"browser extension\" analogy: the host gives the extension a clear API (read/write page, make requests) + a set of event hooks, the extension just says \"call me when something happens,\" both dealing only through the \"API + hooks\" contract."},
            },
            {
                "q": {"zh": "插件从配置加载时，loader 为什么把加载拆成 install/entry/compatibility/load 几个可重试阶段？", "en": "When loading plugins from config, why does the loader split loading into retryable stages install/entry/compatibility/load?"},
                "opts": [
                    {"zh": "插件加载触及 opencode 最不可控的边界——第三方代码+网络安装（包可能没装上/入口找不到/版本不兼容）；分阶段独立重试+报错，在「向外敞开」与「自身稳健」间平衡，绝不让一个坏插件拖垮整个启动", "en": "Plugin loading touches opencode's least-controllable boundary—third-party code + network install (package may not install / entry not found / version incompatible); staged independent retry+reporting balances \"open outward\" and \"stay robust,\" never letting one bad plugin drag down the whole startup"},
                    {"zh": "为了让插件加载得更快", "en": "To make plugins load faster"},
                    {"zh": "因为 npm 要求这么做", "en": "Because npm requires it"},
                    {"zh": "纯粹是代码风格", "en": "Purely a code style"},
                ],
                "answer": 0,
                "why": {"zh": "你在配置 plugin 数组里列插件（npm 包名/本地路径），loader.ts 负责就位：resolve（解析+必要时 npm 装包、找入口）→import（动态导入拿到 Plugin 函数）→调用 Plugin(input)→挂 Hooks。加载器的稳健藏在它把链拆成的可重试阶段：install（装包，网络/版本可能失败）→entry（找入口）→compatibility（版本兼容检查）→load（真正 import）。每阶段可能失败，loader 对可重试失败分阶段重试并统一汇报；loadExternal 把所有插件并行加载。为什么这么设计？因为插件加载触及 opencode 最不可控的边界——第三方代码+网络安装：包可能没装上、入口找不到、版本不兼容。把易错的链拆成清晰阶段、每段独立重试报错，是「向外敞开」与「自身稳健」间的务实平衡——敞门迎第三方，但绝不让一个装不上的插件拖垮整个启动。", "en": "You list plugins in the config plugin array (npm name/local path), and loader.ts brings them into place: resolve (parse + npm install if needed, find entry)→import (dynamic import to get the Plugin function)→call Plugin(input)→hook up Hooks. The loader's robustness hides in the retryable stages it splits the chain into: install (install package, network/version may fail)→entry (find entry)→compatibility (version compat check)→load (actually import). Each stage may fail; the loader retries retryable failures per stage and reports uniformly; loadExternal loads all plugins in parallel. Why this design? Because plugin loading touches opencode's least-controllable boundary—third-party code + network install: the package may not install, entry not found, version incompatible. Splitting the error-prone chain into clear stages, each independently retried and reported, is the pragmatic balance between \"opening outward\" and \"staying robust\"—open the door to third parties, but never let one un-installable plugin drag down the whole startup."},
            },
        ],
        "open": [
            {"zh": "课里反复强调 opencode 插件「极简到只剩一个函数签名」，并把它和 L36 Tool.make、L47 PluginV2.define、L53 createSimpleContext 归为「最强抽象往往最朴素」。请你提炼这种「把扩展契约收敛到『你能给我什么(上下文)+你想何时介入(钩子)』两点」的设计哲学：它为什么能同时做到低门槛（会写函数就会写插件）与高威力（能接模型/改请求/定权限/调宿主 API）？再对比你用过的「重」插件框架（要继承基类、实现一堆生命周期、配清单/DI 容器），谈谈它们的复杂度从哪来、是否必要、各自适合什么场景？", "en": "The lesson repeatedly stresses opencode plugins are \"minimal down to one function signature,\" grouping it with L36 Tool.make, L47 PluginV2.define, L53 createSimpleContext as \"the strongest abstraction is often the plainest.\" Distill this \"converge the extension contract to just two points—what can you give me (context) + when do you want to step in (hooks)\" design philosophy: why can it achieve both low barrier (if you can write a function you can write a plugin) and high power (connect models/rewrite requests/set permissions/call host API)? Contrast \"heavy\" plugin frameworks you've used (inherit a base class, implement a pile of lifecycles, configure a manifest/DI container): where does their complexity come from, is it necessary, and what scenario does each suit?"},
            {"zh": "课里指出 opencode 给插件的 PluginInput 里有一个 client——把自己整套 SDK 客户端交到插件手里，让插件能反过来调用 opencode 自己的 API，再配一个 Bun shell $ 能跑任意外部命令。这种「给插件极大权力」的设计，威力与风险并存。请你谈谈：把宿主的完整 API + 一个 shell 交给第三方插件，能解锁哪些强大用法？又带来哪些安全隐患（恶意/有 bug 的插件能读你的会话、跑任意命令）？一个既要「开放强大」又要「安全可控」的插件系统，该如何在权限、沙箱、信任模型上权衡（对比浏览器扩展的权限声明、VS Code 的扩展信任）？", "en": "The lesson notes opencode's PluginInput has a client—handing its entire SDK client into the plugin's hands, letting the plugin call opencode's own API back, paired with a Bun shell $ that can run arbitrary external commands. This \"give the plugin great power\" design has power and risk both. Discuss: handing the host's full API + a shell to a third-party plugin, what powerful uses does it unlock? What security risks does it bring (a malicious/buggy plugin can read your sessions, run arbitrary commands)? A plugin system wanting both \"open and powerful\" and \"safe and controllable,\" how should it weigh permissions, sandboxing, and the trust model (contrast browser extensions' permission declarations, VS Code's extension trust)?"},
        ],
    },

    "56-dialogs-scrollback.html": {
        "mcq": [
            {
                "q": {"zh": "opencode 的对话框系统用一个「栈」来管理。为什么栈这个数据结构特别适合模态对话框？", "en": "opencode's dialog system uses a \"stack.\" Why is the stack data structure especially suited to modal dialogs?"},
                "opts": [
                    {"zh": "模态框的本质是后进先出——开=push、ESC=弹栈顶 slice(0,-1)；「对话框里再开对话框、ESC 只关最上层、关掉退回上一层、全关才解冻」全都自然从栈的 LIFO 语义里长出来，无需任何特判", "en": "A modal's essence is last-in-first-out—open=push, ESC=pop top slice(0,-1); \"a dialog opening a dialog, ESC closes only the top, closing falls back one layer, freeze only until all closed\" all grow naturally from the stack's LIFO semantics, needing no special cases"},
                    {"zh": "栈比数组占内存少", "en": "A stack uses less memory than an array"},
                    {"zh": "栈能让对话框渲染更快", "en": "A stack makes dialogs render faster"},
                    {"zh": "SolidJS 要求用栈", "en": "SolidJS requires a stack"},
                ],
                "answer": 0,
                "why": {"zh": "ui/dialog.tsx 的核心是 store.stack。开对话框=push 进栈、渲染在最上层；栈非空就 modeStack.push(\"modal\") 冻住下层、焦点归对话框；ESC=current=stack.at(-1)、setStore stack.slice(0,-1) 只弹栈顶。为什么用栈而非「一个 currentDialog 变量」？因为模态本质就是后进先出：你开 A 又从 A 开 B，此刻该响应 ESC、该接键盘的永远是最新的 B；关 B 应退回 A 而非全关。at(-1)=「当前该响应谁」、slice(0,-1)=「退一层」、栈空=「回非模态」——模态全部规矩自然从栈的 LIFO 长出来，一条都不用特判。若硬用「currentDialog + 一堆 if 判断要不要恢复上一个」立刻陷入「上一个是谁、状态还在不在」的泥潭。这是「选对数据结构逻辑自简化」的范例：把交互的形状映射到语义恰好吻合的数据结构（模态用栈、有序覆盖用 findLast、待办用队列）。", "en": "ui/dialog.tsx's core is store.stack. Opening a dialog=push onto the stack, rendered on top; stack non-empty triggers modeStack.push(\"modal\") freezing the layer below, focus to the dialog; ESC=current=stack.at(-1), setStore stack.slice(0,-1) pops only the top. Why a stack not \"a currentDialog variable\"? Because a modal's essence is LIFO: you open A then open B from A, and right now what should respond to ESC and receive the keyboard is always the newest B; closing B should fall back to A, not close all. at(-1)=\"who should respond now\", slice(0,-1)=\"back one layer\", empty stack=\"back to non-modal\"—all a modal's rules grow naturally from the stack's LIFO, not one special case. Forcing \"currentDialog + a pile of ifs deciding whether to restore the previous\" instantly sinks into the quagmire of \"who was the previous, is its state still there.\" This is an example of \"pick the right data structure and logic simplifies itself\": mapping an interaction's shape onto a data structure whose semantics exactly fit (modal to stack, ordered-override to findLast, todos to a queue)."},
            },
            {
                "q": {"zh": "opencode 的二十多个对话框（选模型/agent/MCP/主题…）和命令面板有什么共同点？", "en": "What do opencode's twenty-some dialogs (pick model/agent/MCP/theme…) and the command palette have in common?"},
                "opts": [
                    {"zh": "几乎全建在同一个可复用零件 DialogSelect（带搜索过滤的列表选择框）上——一致的搜索/上下选/回车确认体验，加新对话框只需喂一份选项列表。又见「统一模子刻同形」", "en": "Nearly all built on the same reusable part DialogSelect (a search-filtered list select box)—consistent search/up-down/enter-confirm experience, adding a new dialog needs only an options list. Again \"a uniform mold stamps the same shape\""},
                    {"zh": "它们都直接操作 DOM", "en": "They all manipulate the DOM directly"},
                    {"zh": "每个对话框都是从零手写的独立实现", "en": "Each dialog is a hand-written independent implementation from scratch"},
                    {"zh": "它们都不可搜索", "en": "None of them are searchable"},
                ],
                "answer": 0,
                "why": {"zh": "二十多个对话框（dialog-model/agent/mcp/skill/theme-list/session-list…）和 command-palette 几乎全建在同一个零件 DialogSelect（带搜索过滤的列表选择框）上。好处：「选模型」和「选主题」用着完全一致的搜索、上下键导航、回车确认——用户学一次处处会用；开发者加新对话框只需喂 DialogSelect 一份选项列表。其中命令面板尤其点睛：从 keymap.getCommandEntries 取所有可见命令（连快捷键/分类/是否建议）成可搜列表，选中 dispatchCommand 执行——意义是「可发现性」，不必背快捷键、搜关键词即可执行任何命令，keymap 是唯一真源、面板只摊开成清单。这是全书反复的「把通用交互做成一个零件、处处复用」智慧（同 L36 Tool.make、L47 PluginV2.define、L53 createSimpleContext）。", "en": "Twenty-some dialogs (dialog-model/agent/mcp/skill/theme-list/session-list…) and command-palette are nearly all built on the same part DialogSelect (a search-filtered list select box). Benefits: \"pick model\" and \"pick theme\" use a completely consistent search, up/down navigation, enter-confirm—the user learns once, uses everywhere; a developer adding a new dialog need only feed DialogSelect an options list. Among them the command palette is especially the eye-opener: takes all visible commands from keymap.getCommandEntries (with keybindings/categories/suggested) into a searchable list, dispatchCommand on select—its significance is \"discoverability,\" no memorizing keybindings, search a keyword to run any command, the keymap is the single source, the palette just lays it out. This is the book's recurring \"make a generic interaction into a part, reuse everywhere\" wisdom (like L36 Tool.make, L47 PluginV2.define, L53 createSimpleContext)."},
            },
            {
                "q": {"zh": "同一段对话，在交互式 TUI 里是全屏可滚的应用，在 opencode run 里却是打印到 stdout 的线性日志。这个对照揭示了什么根本设计原则？", "en": "The same conversation is a full-screen scrollable app in the interactive TUI but a linear log printed to stdout in opencode run. What fundamental design principle does this contrast reveal?"},
                "opts": [
                    {"zh": "数据与表现分离——一份 session/message（M9）+ 一套内核，可被渲染成多副面孔（交互 TUI / run scrollback / Web / 桌面）；每多一种「看法」不必重写内核", "en": "Data separated from presentation — one session/message (M9) + one core, can be rendered into many faces (interactive TUI / run scrollback / Web / desktop); each added \"viewing\" needn't rewrite the core"},
                    {"zh": "run 模式其实是个完全独立的程序", "en": "run mode is actually a wholly separate program"},
                    {"zh": "TUI 和 run 用各自独立的会话数据", "en": "TUI and run use their own separate session data"},
                    {"zh": "scrollback 比 TUI 功能更强", "en": "scrollback is more powerful than the TUI"},
                ],
                "answer": 0,
                "why": {"zh": "TUI 与 run scrollback 是同一份会话数据的两个「前端」。底层只有一份——存 SQLite 的 session/message/part（M9），由服务器事件流（L54）驱动；怎么呈现它（交互式全屏应用 vs pipe 友好的流式日志）是一个可整个替换的表现层。这种分离让 opencode「一鱼多吃」：同一颗 agent 内核既驱动交互 TUI、也驱动 run 非交互日志、甚至 Web 应用和桌面端——因为「agent 在干什么」和「你怎么看它干」从一开始就被切成两件事，每多一种看法不必重写内核。run 本身还有三模式（非交互默认/交互本地/交互附着），把交互程度铺成光谱。这呼应全书最深主线：好架构反复在「找准接缝、切开会变与不变」——L47 切核心与 provider、L50 切搬运与翻译、L54 切事件数据与渲染时机，本课切 agent 会话与会话呈现。切口越准，越能不动根基长出更多可能。", "en": "The TUI and run scrollback are two \"front-ends\" over the same session data. Underneath is just one copy—the session/message/part stored in SQLite (M9), driven by the server event stream (L54); how to present it (interactive full-screen app vs pipe-friendly streaming log) is a wholly replaceable presentation layer. This separation lets opencode do \"one fish, many dishes\": the same agent core drives the interactive TUI, run's non-interactive log, even the Web app and desktop—because \"what the agent is doing\" and \"how you watch it do it\" were cut into two things from the start, each added viewing needn't rewrite the core. run itself has three modes (non-interactive default/interactive local/interactive attach), spreading interactivity into a spectrum. This echoes the book's deepest throughline: good architecture repeatedly \"finds the seam, cuts the changing from the unchanging\"—L47 cut core from provider, L50 cut moving from translation, L54 cut event data from render timing, this lesson cuts the agent's conversation from the conversation's presentation. The more accurate the cut, the more possibilities grow without disturbing the foundation."},
            },
        ],
        "open": [
            {"zh": "课里把「对话框用栈」称作「选对数据结构、逻辑就自己变简单」的教科书示范，并列举了「模态用栈、有序覆盖用 findLast（L41/L44）、待办用队列」等映射。请你再举几个「把交互/业务的『形状』映射到一个语义恰好吻合的数据结构，从而从根上消除复杂度」的例子（如撤销重做用双栈、LRU 缓存用链表+哈希、事件优先级用堆）。反过来，谈谈「数据结构选错」导致逻辑里堆满特判的惨痛经历。你总结出哪些「识别正确数据结构」的思维线索？", "en": "The lesson calls \"dialogs use a stack\" a textbook demonstration of \"pick the right data structure and logic simplifies itself,\" listing mappings like \"modal to stack, ordered-override to findLast (L41/L44), todos to a queue.\" Give a few more examples of \"mapping an interaction's/business's 'shape' onto a data structure whose semantics exactly fit, thereby eliminating complexity at the root\" (e.g. undo-redo with two stacks, LRU cache with linked-list+hash, event priority with a heap). Conversely, discuss a painful experience where \"a wrong data-structure choice\" piled the logic with special cases. What thinking cues have you distilled for \"recognizing the right data structure\"?"},
            {"zh": "课里把「数据与表现分离」立为贯穿 opencode 的根本原则：一份 session/message + 一套内核，能驱动交互 TUI、run scrollback、Web、桌面多副面孔，并将它和 L47（核心 vs provider）、L50（搬运 vs 翻译）、L54（事件数据 vs 渲染时机）归为「找准接缝、切开会变与不变」的同一手法。请你提炼这条「找正确接缝」的架构思想：一个好的「接缝」应满足什么（两侧能独立演化、接口窄而稳定、改一侧不波及另一侧）？以你做过的系统为例，谈一个「接缝找对了，后来轻松加了新功能」和一个「接缝找错了/没切，后来寸步难行」的对比。怎样在项目早期就尽量找对关键接缝，又不陷入过度抽象？", "en": "The lesson establishes \"data separated from presentation\" as a fundamental principle running through opencode: one session/message + one core can drive the interactive TUI, run scrollback, Web, desktop—many faces, grouping it with L47 (core vs provider), L50 (moving vs translation), L54 (event data vs render timing) as the same \"find the seam, cut the changing from the unchanging\" technique. Distill this \"find the right seam\" architectural idea: what should a good \"seam\" satisfy (both sides can evolve independently, a narrow stable interface, changing one side doesn't ripple to the other)? From systems you've built, contrast a case of \"the seam was right, later easily added a new feature\" with one of \"the seam was wrong/uncut, later stuck.\" How do you find the key seams right early in a project without falling into over-abstraction?"},
        ],
    },

    "55-prompt-component.html": {
        "mcq": [
            {
                "q": {"zh": "opencode 的 frecency 算法（freq/(1+距上次打开的天数)）为什么比「纯按频率排」或「纯按最近排」都好？", "en": "Why is opencode's frecency algorithm (freq/(1+days since last open)) better than either \"rank by frequency only\" or \"rank by recency only\"?"},
                "opts": [
                    {"zh": "频率给长期偏好、最近度给当下意图，相除让两者动态平衡——纯频率会让半年前疯狂用过的文件永远霸榜，纯最近会让误点一次的文件插到核心文件前；frecency 两者都避开", "en": "Frequency gives long-term preference, recency gives present intent, division dynamically balances—pure frequency lets a file frantically used half a year ago forever squat the top, pure recency lets a mis-clicked file jump ahead of core files; frecency avoids both"},
                    {"zh": "frecency 计算更快", "en": "frecency computes faster"},
                    {"zh": "frecency 占用内存更少", "en": "frecency uses less memory"},
                    {"zh": "纯属代码风格偏好", "en": "Purely a code-style preference"},
                ],
                "answer": 0,
                "why": {"zh": "frecency=frequency+recency，公式 frequency/(1+(now-lastOpen)/86400000)（86400000=一天毫秒数）。它同时打败两种朴素方案：纯频率（开得多的永远在前）→半年前疯狂打开过的文件永远霸榜、早不碰也赖着；纯最近（刚开的在前）→误点一次的无关文件瞬间插到天天用的核心文件前。frecency 用「频率÷时间衰减」揉合：历史频率再高，久不碰，分母(1+天数)就把分慢慢拖低；刚开的新文件频率虽低但天数≈0、分母≈1能暂时靠前，但不持续就被超过。频率给长期偏好、最近度给当下意图、相除动态平衡。这正是 Firefox 地址栏、编辑器文件选择器背后同一个久经验证的排序智慧——值得装进工具箱、随处可用。", "en": "frecency=frequency+recency, formula frequency/(1+(now-lastOpen)/86400000) (86400000=ms in a day). It defeats two naive schemes at once: pure frequency (most-opened always first) → a file frantically opened half a year ago forever squats the top, clings on though untouched; pure recency (just-opened first) → an irrelevant file mis-clicked once instantly jumps ahead of the daily core file. frecency kneads both via \"frequency ÷ time decay\": however high the historical frequency, long untouched, the denominator (1+days) slowly drags the score down; a just-opened new file though low-frequency has days≈0, denominator≈1, can rank up temporarily but is overtaken if not sustained. Frequency gives long-term preference, recency gives present intent, division dynamically balances. This is the same time-tested ranking wisdom behind Firefox's address bar and editors' file pickers—worth putting in your toolbox for use anywhere."},
            },
            {
                "q": {"zh": "opencode 的 prompt 历史和 frecency 都怎么跨会话持久化？为什么不每次都重写整个文件？", "en": "How do opencode's prompt history and frecency persist across sessions? Why not rewrite the whole file each time?"},
                "opts": [
                    {"zh": "追加式 JSONL 日志：每次更新只 appendText 追加一行（O(1)、抗崩溃，热路径），超限时才 writeText 重写去重（冷路径），加载时跳过坏行并重写自愈——「廉价追加、推迟整理」", "en": "Append-only JSONL log: each update only appendText appends one line (O(1), crash-safe, hot path), only on overflow writeText rewrites-dedup (cold path), on load skips bad lines and rewrites to self-heal—\"cheap append, defer tidy\""},
                    {"zh": "每次更新都把整个列表重写一遍", "en": "Rewrites the whole list on every update"},
                    {"zh": "只存在内存里、退出即丢", "en": "Only in memory, lost on exit"},
                    {"zh": "存进 SQLite 数据库", "en": "Stored in a SQLite database"},
                ],
                "answer": 0,
                "why": {"zh": "历史/frecency 都存 *.jsonl（prompt-history.jsonl、frecency.jsonl），每行一条 JSON。三步：①追加（热路径）——每次更新只 appendText 追加一行，O(1)、不重写全文，即便崩了也只丢最后一行；②压缩（冷路径）——超过上限（历史 50/frecency 1000）时 writeText 重写去重、保留最新 N；③自愈（加载时）——跳过解析失败的坏行，有有效行就重写一遍修复损坏、抹掉超额。为什么不每次重写整个文件？那样既慢（列表越长写越久）又不抗崩溃（重写到一半断电可能整文件损坏）。「追加一行」永远廉价且原子——同 L48 数据库 WAL、L54 事件溯源的道理：把高频「记录」做成廉价追加，把昂贵「整理」推迟到低频不影响体验时。parseFrecency 读日志用 reduce 让同路径后出现的覆盖先出现的，自然取最新——同 L41/L44 的 findLast「后者胜」。", "en": "History/frecency both store *.jsonl (prompt-history.jsonl, frecency.jsonl), one JSON per line. Three steps: ① append (hot path)—each update only appendText appends one line, O(1), no full rewrite, even a crash loses only the last line; ② compact (cold path)—on exceeding a cap (history 50/frecency 1000) writeText rewrites-dedup, keeps latest N; ③ self-heal (on load)—skip lines that fail to parse, if valid lines exist rewrite once to fix corruption and trim overflow. Why not rewrite the whole file each time? That's both slow (longer list, longer write) and not crash-safe (power cut mid-rewrite may corrupt the whole file). \"Append one line\" is always cheap and atomic—the same principle as L48's database WAL and L54's event sourcing: make the high-frequency \"record\" a cheap append, defer the expensive \"tidy\" to a low-frequency, experience-free moment. parseFrecency reading the log uses reduce to let same-path later occurrences override earlier, naturally getting the latest—like L41/L44's findLast \"later wins.\""},
            },
            {
                "q": {"zh": "课里说 frecency 不需要任何显式的「过期」「清理」逻辑，排序就能永远跟着你「最近这阵子」的真实习惯走。这是靠什么实现的？", "en": "The lesson says frecency needs no explicit \"expire\" or \"cleanup\" logic, yet the ranking always tracks your \"lately\" real habits. What achieves this?"},
                "opts": [
                    {"zh": "时间衰减自动新陈代谢——分母(1+天数)让久不碰的分数随时间自动褪色，新习惯随打开行为持续累积上分，无需显式过期/清理", "en": "Time decay auto-metabolizes—the denominator (1+days) auto-fades the score of the long-untouched over time, new habits keep scoring up with opening behavior, no explicit expire/cleanup needed"},
                    {"zh": "一个后台定时任务每天清理旧条目", "en": "A background cron cleans old entries daily"},
                    {"zh": "每次打开都把所有其它文件的分数减一", "en": "Each open decrements every other file's score by one"},
                    {"zh": "用户必须手动删除不用的条目", "en": "The user must manually delete unused entries"},
                ],
                "answer": 0,
                "why": {"zh": "frecency 的精妙在于把「过期」内建进了公式本身，而非靠外部逻辑。calculateFrecency=frequency/(1+(now-lastOpen)/天)：分子 frequency 随 updateFrecency 每次打开 +1（新习惯持续累积上分），分母 (1+距上次打开天数) 随时间流逝自动变大（旧习惯自动褪色）。因为分数是「读取时实时算」的（now 永远是当下），所以一个文件哪怕数据原封不动躺着，它的 frecency 分也会随着「天数」增长而自动下降——无需任何后台清理、无需显式过期标记，排序永远自动反映你最近的真实状态。这是个绝佳范例：很多看似需要「智能」（机器学习、用户画像）的产品体验，一个想透了的简单公式就能漂亮解决——关键不在算法多复杂，而在看清「真正该度量的是什么」（这里是长期偏好×当下意图）。任何「最近常用项排序」需求，frecency 都是第一个该想到的答案。", "en": "frecency's cleverness is building \"expiry\" into the formula itself, not relying on external logic. calculateFrecency=frequency/(1+(now-lastOpen)/day): the numerator frequency +1 with each open via updateFrecency (new habits keep scoring up), the denominator (1+days since last open) auto-grows with passing time (old habits auto-fade). Because the score is \"computed live on read\" (now is always the present), a file's frecency score auto-declines as \"days\" grow even if its data lies untouched—no background cleanup, no explicit expiry flag, the ranking always auto-reflects your lately real state. A superb example: many product experiences seemingly needing \"intelligence\" (machine learning, user profiling) can be beautifully solved by one well-thought-through simple formula—the key isn't how complex the algorithm but seeing clearly \"what should truly be measured\" (here, long-term preference × present intent). For any \"rank recently-frequent items\" need, frecency is the first answer to reach for."},
            },
        ],
        "open": [
            {"zh": "课里把 frecency 称作「用一个极简数学式优雅表达一个本来很主观的需求」的范例，并说『很多看似需要「智能」的产品体验，其实一个想透了的简单公式就能漂亮解决，关键不在算法多复杂，而在你是否看清了「真正该度量的是什么」』。请你结合自己的经验，举一两个「本可以用简单启发式/公式解决、却被过度工程化成复杂 ML 系统」的反面案例，或反过来「一个朴素公式意外好用」的正面案例。你怎样判断一个排序/推荐需求该用「简单公式」还是「学习模型」？frecency 这类公式的局限又在哪（冷启动、对抗性操纵、无法捕捉复杂关联）？", "en": "The lesson calls frecency an example of \"using a minimal mathematical expression to elegantly express an inherently subjective need,\" saying \"many product experiences seemingly needing 'intelligence' can actually be beautifully solved by one well-thought-through simple formula; the key isn't how complex the algorithm but whether you've seen clearly 'what should truly be measured.'\" From your experience, give one or two counterexamples of \"something solvable by a simple heuristic/formula but over-engineered into a complex ML system,\" or conversely a positive case of \"a plain formula working surprisingly well.\" How do you judge whether a ranking/recommendation need should use a \"simple formula\" or a \"learned model\"? What are the limits of formulas like frecency (cold start, adversarial manipulation, inability to capture complex correlations)?"},
            {"zh": "课里指出历史与 frecency 都用「追加式 JSONL 日志 + 定期压缩 + 加载自愈」持久化，并把它和 L48 数据库 WAL、L54 事件溯源归为同一个「廉价追加、推迟整理」的范式。请你提炼这个范式的通用结构（热路径只追加→冷路径压缩→读取时折叠/自愈），分析它为什么同时兼顾了「写入性能」「抗崩溃」「最终一致」三者。再谈谈它的代价：日志会无限增长直到压缩、读取需要回放/折叠全部记录、压缩本身若崩溃如何保证安全？你在自己的项目里实现过类似的 append-only + compaction 机制吗（如指标上报、审计日志、LSM-tree 存储）？", "en": "The lesson notes history and frecency both persist via \"append-only JSONL log + periodic compaction + load-time self-heal,\" grouping it with L48's database WAL and L54's event sourcing as the same \"cheap append, defer tidy\" paradigm. Distill this paradigm's general structure (hot path only appends → cold path compacts → read-time folds/self-heals), analyze why it simultaneously serves \"write performance,\" \"crash safety,\" and \"eventual consistency.\" Then discuss its costs: the log grows unboundedly until compaction, reads must replay/fold all records, and how is safety guaranteed if compaction itself crashes? Have you implemented a similar append-only + compaction mechanism in your own projects (e.g. metrics reporting, audit logs, LSM-tree storage)?"},
        ],
    },

    "54-events-to-store.html": {
        "mcq": [
            {
                "q": {"zh": "opencode TUI 的界面状态是怎么来的？它和 Redux 的「action→reducer→state」是什么关系？", "en": "Where does opencode TUI's interface state come from? How does it relate to Redux's \"action→reducer→state\"?"},
                "opts": [
                    {"zh": "事件溯源——SDKProvider 经 SSE 订阅服务器事件流，sync.tsx 的 switch(event.type) reducer 把每个事件归约进 createStore 响应式 store；store 是事件流的投影，正是 Redux 三段式，只是 action 来自服务器", "en": "Event-sourced — SDKProvider subscribes to the server event stream via SSE, sync.tsx's switch(event.type) reducer reduces each event into the createStore reactive store; the store is a projection of the event stream, exactly the Redux triad, only the action comes from the server"},
                    {"zh": "每隔一秒拉一次完整状态、整个替换", "en": "Pulls the full state every second and replaces it wholesale"},
                    {"zh": "状态全存在服务器、TUI 不存", "en": "All state lives on the server, the TUI stores none"},
                    {"zh": "用轮询查询数据库", "en": "Polls the database"},
                ],
                "answer": 0,
                "why": {"zh": "opencode TUI 不「每秒拉一次最新状态」，而是订阅：SDKProvider 经 SSE 连服务器事件流，服务器一有动静（新消息/工具状态变化/权限请求…）就主动推事件。把事件变成状态的，是 sync.tsx 那个巨大的 switch(event.type) reducer——针对每种类型做一次精准 setStore（如 permission.asked→setStore(\"permission\",sessionID,[request])、session.updated→setStore(\"session\",index,reconcile(info))）。这正是「action→reducer→state」三段式，只是 action 是服务器推的事件、state 是 createStore 建的响应式大 store（装所有会话/消息/权限/待办/配置…）。store 是事件流的一份投影。reducer 用 produce（草稿就地改、自动算变更路径）和 reconcile（替换时只改真正不同字段、保细粒度），数组按 id 排序 + 二分 search O(log n) 找到即更新/找不到即插入。", "en": "opencode TUI doesn't \"pull the latest state every second\" but subscribes: SDKProvider connects to the server event stream via SSE, and the moment the server has news (new message/tool status change/permission request…) it actively pushes an event. What turns events into state is sync.tsx's giant switch(event.type) reducer—one precise setStore per type (e.g. permission.asked→setStore(\"permission\",sessionID,[request]), session.updated→setStore(\"session\",index,reconcile(info))). This is exactly the \"action→reducer→state\" triad, only the action is a server-pushed event and the state is the big reactive store built with createStore (holding all sessions/messages/permissions/todos/config…). The store is a projection of the event stream. The reducer uses produce (draft in-place edit, auto-computes changed paths) and reconcile (on replace, changes only truly-different fields, keeps fine-grained), arrays sorted by id + binary search O(log n) find-and-update or insert."},
            },
            {
                "q": {"zh": "当 agent 全速流式输出、一秒涌来上百个事件时，opencode 怎么避免「每个事件一次重渲染」把界面卡死？", "en": "When the agent streams at full speed and a hundred events gush in per second, how does opencode avoid \"one re-render per event\" stuttering the interface to death?"},
                "opts": [
                    {"zh": "16ms 批处理——事件入队；距上次 flush<16ms（洪流中）就 setTimeout(flush,16) 攒批、≥16ms（空闲）就立刻 flush；flush 把整批事件裹进 SolidJS batch()，一批事件只触发一次重渲染（16ms≈60fps 一帧）", "en": "16ms batching — events queued; <16ms since last flush (in flood) → setTimeout(flush,16) amass, ≥16ms (idle) → flush immediately; flush wraps the whole batch in SolidJS batch(), a batch of events triggers only one re-render (16ms≈one 60fps frame)"},
                    {"zh": "丢弃多余的事件、只处理第一个", "en": "Discards excess events, processes only the first"},
                    {"zh": "把渲染搬到后台线程", "en": "Moves rendering to a background thread"},
                    {"zh": "降低终端分辨率", "en": "Lowers the terminal resolution"},
                ],
                "answer": 0,
                "why": {"zh": "agent 流式输出时服务器每吐几个字就推一个事件，一秒可能上百个。若每个都立刻重渲染=一秒上百次重画，终端绘制昂贵（L52），必然卡成幻灯片还狂闪。opencode 的解法在 sdk.tsx 的 handleEvent：每个事件先 queue.push 入队不立即处理；看距上次 flush 过了多久（elapsed）——elapsed<16ms（刚刷过、正处洪流）就 setTimeout(flush,16) 把它和后续攒一起，elapsed≥16ms（很闲）就立刻 flush 零延迟。flush 把队列所有事件的应用裹进一个 SolidJS batch()——一批事件的所有 store 更新合并成一次重渲染。16ms≈60fps 一帧时长，节奏正好踩在屏幕刷新节拍上，把「一秒上百次重画」压到「一秒最多 60 次」。这层「时间维批处理」和 L52「空间维细粒度更新」叠加=流畅双重保险。", "en": "When the agent streams, the server pushes an event every few characters, possibly a hundred per second. If each immediately re-rendered = a hundred redraws/sec, terminal painting being expensive (L52), it'd inevitably stutter into a slideshow and flicker madly. opencode's solution is in sdk.tsx's handleEvent: each event first queue.pushes without immediate processing; check how long since the last flush (elapsed)—elapsed<16ms (just flushed, in the flood) → setTimeout(flush,16) amasses it with subsequent ones, elapsed≥16ms (idle) → flushes immediately, zero latency. flush wraps the application of all queued events in one SolidJS batch()—all a batch's store updates merge into one re-render. 16ms≈one 60fps frame's duration, the rhythm steps precisely on the screen-refresh beat, pressing \"a hundred redraws/sec\" down to \"at most 60/sec.\" This \"temporal-dimension batching\" stacked with L52's \"spatial-dimension fine-grained updates\" = the double insurance of fluidity."},
            },
            {
                "q": {"zh": "16ms 批处理那个 elapsed<16 的判断，巧在哪里？", "en": "What's clever about that elapsed<16 check in 16ms batching?"},
                "opts": [
                    {"zh": "用一个判断在「低延迟（空闲立刻发）」和「高吞吐（洪流攒批）」间无缝自动切换——洞察是：用户对延迟敏感发生在事件稀疏时(等响应)、高吞吐需求发生在事件密集时(看流式)，两者时间上天然错开", "en": "One check seamlessly auto-switches between \"low latency (idle sends immediately)\" and \"high throughput (flood amasses)\" — the insight: a user's latency sensitivity happens when events are sparse (awaiting a response), the throughput need when events are dense (watching streaming), the two naturally staggered in time"},
                    {"zh": "16 是 2 的幂、计算更快", "en": "16 is a power of 2, computes faster"},
                    {"zh": "纯粹是为了兼容老终端", "en": "Purely for old-terminal compatibility"},
                    {"zh": "为了限制每秒事件数量", "en": "To cap the number of events per second"},
                ],
                "answer": 0,
                "why": {"zh": "「延迟」与「吞吐」是天生矛盾。朴素实现只能二选一：每事件立刻处理（延迟最低，但洪流卡死），或固定每 16ms 才处理一次（吞吐稳，但空闲也白慢 16ms）。opencode 用一个 elapsed<16 的判断把两种模式自动切换：闲时走「立刻」分支、忙时走「攒批」分支——系统自己按负载在低延迟和高吞吐间无缝滑动，无需手动调参。这种「自适应批处理」的精髓是一个洞察：用户对延迟的敏感恰恰发生在事件稀疏时（你在等响应），高吞吐需求恰恰发生在事件密集时（你在看流式输出），两种需求在时间上天然错开。于是一个简单的「最近是否刚忙过」判断，就能让系统永远站在当下最该站的那一边。好的性能优化往往不是更复杂、而是更懂场景。", "en": "\"Latency\" and \"throughput\" are a born contradiction. A naive implementation can only pick one: process each event immediately (lowest latency, but stutters under flood), or process only once per fixed 16ms (stable throughput, but needlessly 16ms slower when idle). opencode uses one elapsed<16 check to auto-switch between the two modes: when idle take the \"immediate\" branch, when busy take the \"amass\" branch—the system slides seamlessly between low latency and high throughput per load, no manual tuning. This \"adaptive batching\"'s essence is an insight: a user's sensitivity to latency happens exactly when events are sparse (you're awaiting a response), the need for high throughput exactly when events are dense (you're watching streaming output), the two needs naturally staggered in time. So a simple \"was it busy recently\" check lets the system always stand on the side it most should right now. Good performance optimization is often not more complex but more attuned to the scenario."},
            },
        ],
        "open": [
            {"zh": "课里把 opencode TUI 的流畅归功于「双重保险」：16ms 批处理（时间维：每帧最多渲一次）× 细粒度响应式（空间维：每次只动该动的字符格）。请你分别解释这两层各自解决了什么问题、缺了任何一层会怎样（只有批处理没有细粒度？只有细粒度没有批处理？），并谈谈这种「时间维 + 空间维」正交叠加的优化思路，在你熟悉的其他高频渲染场景（游戏循环、股票行情、聊天室、日志面板）里有没有对应的影子？", "en": "The lesson credits opencode TUI's fluidity to \"double insurance\": 16ms batching (temporal: at most one render per frame) × fine-grained reactivity (spatial: each render touches only the cells that should change). Explain what each layer solves and what would happen missing either (only batching, no fine-grained? only fine-grained, no batching?), and discuss this \"temporal + spatial\" orthogonally-stacked optimization approach—does it have echoes in other high-frequency rendering scenarios you know (game loops, stock tickers, chat rooms, log panels)?"},
            {"zh": "课里盛赞 16ms 自适应批处理「用一个 elapsed<16 的判断在低延迟与高吞吐间无缝切换」，并提炼出洞察：用户对延迟的敏感发生在事件稀疏时、高吞吐需求发生在事件密集时，两者时间上天然错开。请你把这个「按当前负载在两种策略间自适应切换」的模式，与你见过的其他自适应机制（TCP 拥塞控制、自适应防抖/节流、数据库的批量提交、Nagle 算法）做类比：它们共享什么样的结构？设计一个好的「自适应阈值」要权衡什么（这里 16ms 选大选小各有什么后果）？什么场景下「固定策略」反而比「自适应」更可取？", "en": "The lesson praises 16ms adaptive batching for \"using one elapsed<16 check to seamlessly switch between low latency and high throughput,\" distilling the insight: a user's latency sensitivity happens when events are sparse, the throughput need when events are dense, the two naturally staggered in time. Compare this \"adaptively switch between two strategies per current load\" pattern with other adaptive mechanisms you've seen (TCP congestion control, adaptive debounce/throttle, database batch commits, the Nagle algorithm): what structure do they share? What does designing a good \"adaptive threshold\" trade off (here, what are the consequences of choosing 16ms larger or smaller)? In what scenarios is a \"fixed strategy\" preferable to \"adaptive\"?"},
        ],
    },

    "53-tui-structure.html": {
        "mcq": [
            {
                "q": {"zh": "app.tsx 里二十多层嵌套的 context Provider（SDK 套 Project 套 Sync 套 Data…），这个嵌套顺序是怎么决定的？", "en": "In app.tsx's twenty-some nested context Providers (SDK wraps Project wraps Sync wraps Data…), how is the nesting order decided?"},
                "opts": [
                    {"zh": "嵌套顺序=依赖拓扑：内层 Provider 的 init 里会 use 外层 context（如 ProjectProvider init 调 useSDK()），所以 SDK 必须裹在 Project 外面——越基础的越靠外", "en": "Nesting order = dependency topology: an inner Provider's init uses an outer context (e.g. ProjectProvider init calls useSDK()), so SDK must wrap outside Project—the more fundamental the more outer"},
                    {"zh": "按字母顺序排列", "en": "Arranged alphabetically"},
                    {"zh": "随意嵌套，顺序无所谓", "en": "Nested arbitrarily, order doesn't matter"},
                    {"zh": "按 Provider 的代码行数从多到少", "en": "By each Provider's line count, most to least"},
                ],
                "answer": 0,
                "why": {"zh": "嵌套顺序绝非随意，而是一张依赖关系图的拓扑排序。看 project.tsx：ProjectProvider 的 init 第一行就是 const sdk = useSDK()——它要用 SDK 拉项目信息。既然 useSDK() 只能在 SDKProvider 内部用，ProjectProvider 就必须被 SDKProvider 包在里头。同理 RouteProvider init 用 useTuiStartup()；而 SyncProvider 与 DataProvider 的 init 都用 useEvent()（内部又调 useSDK()）各自独立消费 SDK 事件流、都依赖 SDK 故都在 SDKProvider 内（彼此并不依赖）……每一处「内层 init 调外层 use」都钉下一条「谁必在谁外」的硬约束。于是塔从下到上恰好是「越基础越靠外」的依赖链：连接(SDK)→项目→数据同步→主题→交互状态→界面。妙处：无需另写一张依赖表，依赖关系物理地体现在代码缩进层级里——结构本身就是文档，从上往下读这段 JSX 就等于走了一遍服务依赖图。", "en": "The nesting order is by no means arbitrary but a topological sort of a dependency graph. See project.tsx: ProjectProvider's init's first line is const sdk = useSDK()—it uses the SDK to fetch project info. Since useSDK() can only be used inside SDKProvider, ProjectProvider must be wrapped by SDKProvider. Likewise RouteProvider init uses useTuiStartup(); while both SyncProvider's and DataProvider's init consume the SDK event stream independently via useEvent() (which internally calls useSDK()), both depending on SDK so both inside SDKProvider (they don't depend on each other)… every \"inner init calling an outer use\" nails a hard \"who must be outside whom\" constraint. So the tower bottom-to-top is exactly a \"more fundamental more outer\" dependency chain: connection(SDK)→project→data sync→theme→interaction state→interface. The cleverness: no separate dependency table needed, dependencies are physically embodied in the code's indentation levels—the structure is the documentation, reading this JSX top-to-bottom walks the whole service dependency graph."},
            },
            {
                "q": {"zh": "opencode 的二十多个 context 全用一个 createSimpleContext 助手刻出来，它那个会抛错的 use() 解决了什么问题？", "en": "opencode's twenty-some contexts are all stamped from one createSimpleContext helper; what does its throwing use() solve?"},
                "opts": [
                    {"zh": "快速失败——不在对应 Provider 内调用就当场抛「must be used within a context provider」并点名 context，把「Provider 外用 context→拿到 undefined→在远处莫名崩溃」这个隐蔽 bug 提前成响亮的当场报错", "en": "Fail fast — not called inside the matching Provider throws \"must be used within a context provider\" naming the context, moving the hidden bug of \"use context outside Provider→get undefined→crash mysteriously afar\" forward to a loud on-the-spot error"},
                    {"zh": "让 context 取值更快", "en": "Makes context value retrieval faster"},
                    {"zh": "自动创建缺失的 Provider", "en": "Auto-creates the missing Provider"},
                    {"zh": "把所有 context 合并成一个", "en": "Merges all contexts into one"},
                ],
                "answer": 0,
                "why": {"zh": "createSimpleContext(helper.tsx)封了「建 context+provider(跑 init、<Show when=ready> 门控)+use() 钩子」。其 use() 里有 if(!value) throw new Error(`${name} context must be used within a context provider`)。在 SolidJS/React 里最难查的 bug 之一就是「在 Provider 外用了 context、拿到 undefined、然后在八竿子打不着的地方崩」。这里把错误从『沉默的 undefined』提前成『响亮的当场报错』——一旦组件放错位置（忘了用某 Provider 包住），运行第一时间就告诉你哪个 context 没在 Provider 内用。这是「快速失败」的高频应用（同 L37 Stale tool call、L48「库非空却无 session 表」）。更深一层：把良好实践（判空报错、就绪门控、命名一致）固化进一个谁都顺手用的小工具，让正确的事成为最省力的事，远胜写一篇『请记得判空』的文档——同 L36 Tool.make、L47 PluginV2.define「统一模子刻同形」。", "en": "createSimpleContext (helper.tsx) packs \"build context+provider (run init, <Show when=ready> gate)+use() hook.\" Its use() has if(!value) throw new Error(`${name} context must be used within a context provider`). In SolidJS/React one of the hardest-to-trace bugs is \"using a context outside its Provider, getting undefined, then crashing somewhere unrelated.\" Here it moves the error from a 'silent undefined' forward to a 'loud on-the-spot error'—the moment a component is misplaced (forgot to wrap in some Provider), the first run tells you which context wasn't used inside a Provider. This is a high-frequency \"fail fast\" application (like L37 Stale tool call, L48 \"DB non-empty yet no session table\"). Deeper: solidifying good practices (null-check error, readiness gate, consistent naming) into a tool everyone reaches for makes the right thing the least-effort thing, far beating a 'please null-check' doc—like L36 Tool.make, L47 PluginV2.define \"uniform mold stamps same shape.\""},
            },
            {
                "q": {"zh": "为什么 opencode TUI 用「每个 Provider 只 owns 一格状态」的金字塔，而不是把所有状态塞进一个大 App 组件？", "en": "Why does opencode's TUI use a pyramid of \"each Provider owns one cell of state\" rather than stuffing all state into one big App component?"},
                "opts": [
                    {"zh": "所有权清晰（某格状态由某 Provider 独家拥有/维护）、各格可独立读懂测试替换；配 L52 细粒度响应式，边界清晰的状态格天然是细粒度更新边界——「拆得清」即「更得省」", "en": "Ownership is clear (some cell of state exclusively owned/maintained by some Provider), each cell independently readable/testable/replaceable; paired with L52 fine-grained reactivity, a cleanly-bounded state cell is naturally the boundary of fine-grained updates—\"split clean\" is \"update lean\""},
                    {"zh": "Provider 比组件渲染更快", "en": "Providers render faster than components"},
                    {"zh": "SolidJS 不支持大组件", "en": "SolidJS doesn't support big components"},
                    {"zh": "纯粹是为了代码好看", "en": "Purely for code aesthetics"},
                ],
                "answer": 0,
                "why": {"zh": "「一个 Provider 一格关注点」的拆法，好处和 L44 配置、L47 provider 插件一脉相承：每格小而自洽、可独立读懂与修改，组件 useXxx() 精准取所需，绝不被迫依赖一个无所不包的上帝对象。对比「所有状态塞进一个大 App」的反面：任何状态变化都可能牵连整个 App 重渲染、任何组件能摸到改坏任何状态、新人读不懂值从哪来谁在改、测试要 mock 整个世界。金字塔式拆分让状态所有权清清楚楚——某格由某 Provider 独家拥有、谁依赖谁一目了然。再配 SolidJS 细粒度响应式（L52）：边界清晰的状态格天然就是细粒度更新的边界，一格变了只触动用到它的组件。「拆得清」与「更得省」合二为一，正是 opencode TUI 既复杂又有条理的结构性原因。", "en": "The \"one Provider one cell of concern\" split's benefits are of a piece with L44's config and L47's provider plugins: each cell small and self-consistent, independently readable and changeable, a component grabs precisely what it wants via useXxx(), never forced to depend on an all-encompassing god object. Contrast \"stuff all state into one big App\": any state change can drag the whole App into re-render, any component can touch and break any state, newcomers can't tell where a value comes from or who changes it, testing must mock the whole world. The pyramid split makes state ownership crystal clear—some cell exclusively owned by some Provider, who depends on whom at a glance. Paired with SolidJS fine-grained reactivity (L52): a cleanly-bounded state cell is naturally the boundary of fine-grained updates, change one cell and only components using it are touched. \"Split clean\" and \"update lean\" become one—exactly the structural reason opencode's TUI is both complex and orderly."},
            },
        ],
        "open": [
            {"zh": "课里把「用嵌套顺序表达 Provider 间的依赖」称作比「另写一张显式依赖表」更巧妙，因为「结构本身就是文档」——从上往下读 app.tsx 的 JSX 嵌套就等于走了一遍服务依赖图。请你辩证地评价这种「隐式依赖（靠嵌套顺序）」vs「显式依赖（如 DI 容器声明）」：前者的优点（直观、改一处即改顺序、无需同步两份信息）和风险（深度嵌套的「金字塔地狱」、循环依赖难发现、重排顺序易出错）各是什么？当 Provider 涨到几十个时，你会怎样在「保持嵌套直观」和「避免金字塔过深」之间取舍？", "en": "The lesson calls \"expressing Provider dependencies via nesting order\" cleverer than \"a separate explicit dependency table\" because \"the structure is the documentation\"—reading app.tsx's JSX nesting top-to-bottom walks the whole service dependency graph. Dialectically evaluate this \"implicit dependency (via nesting order)\" vs \"explicit dependency (e.g. DI container declaration)\": what are the former's pros (intuitive, change one spot changes the order, no syncing two sources of info) and risks (deep-nesting \"pyramid hell,\" circular dependencies hard to spot, reordering error-prone)? When Providers grow to dozens, how would you trade off between \"keeping nesting intuitive\" and \"avoiding an over-deep pyramid\"?"},
            {"zh": "课里盛赞 createSimpleContext 这十几行小工具：它把一类会重复几十遍的样板收敛成一处，更把「快速失败、就绪门控、命名一致」这套良好实践固化进一个谁都顺手用的工具，「让正确的事成为最省力的事」，并把它和 L36 Tool.make、L47 PluginV2.define 归为「统一模子刻同形」的同一手法。请你提炼这种「用一个小封装把良好实践变成默认路径」的设计哲学：它为什么比写规范文档、靠 code review 把关更有效？你在自己的项目里有没有「本该封装成统一模子、却放任各处手写、最终样板漂移/护栏遗漏」的教训？反过来，过度封装又有什么风险？", "en": "The lesson praises the dozen-line createSimpleContext tool: it converges a boilerplate that'd repeat dozens of times to one place, and solidifies the good practices of \"fail fast, readiness gate, consistent naming\" into a tool everyone reaches for, \"making the right thing the least-effort thing,\" grouping it with L36 Tool.make and L47 PluginV2.define as the same \"uniform mold stamps same shape\" technique. Distill this \"use a small wrapper to make good practices the default path\" design philosophy: why is it more effective than writing guideline docs or relying on code review? In your own projects, do you have a lesson of \"something that should've been wrapped into a uniform mold but was left hand-written everywhere, leading to boilerplate drift / missing guardrails\"? Conversely, what are the risks of over-wrapping?"},
        ],
    },

    "52-opentui.html": {
        "mcq": [
            {
                "q": {"zh": "opencode 怎么在「只能显示字符的终端」里搭出一个响应式、可交互的现代 UI？", "en": "How does opencode build a reactive, interactive modern UI in a \"terminal that can only display characters\"?"},
                "opts": [
                    {"zh": "用 opentui——一个把 SolidJS 渲染到终端的渲染器，是「终端里的浏览器」：你照样写 JSX(<box>/<text>)、用 signal 做响应式，opentui 负责把组件树画成终端字符格", "en": "With opentui — a renderer that renders SolidJS to the terminal, \"a browser for the terminal\": you still write JSX (<box>/<text>), use signals for reactivity, and opentui paints the component tree into terminal character cells"},
                    {"zh": "直接手写 ANSI 转义码、手动算每个字符的坐标", "en": "Hand-write ANSI escape codes directly, manually computing each character's coordinates"},
                    {"zh": "在终端里嵌一个真正的浏览器", "en": "Embed an actual browser in the terminal"},
                    {"zh": "把界面渲染成图片显示", "en": "Render the interface as an image to display"},
                ],
                "answer": 0,
                "why": {"zh": "opencode 用 opentui——一个把 SolidJS 渲染到终端的渲染器，本质是「终端里的浏览器」。现代框架的精髓是「渲染器与框架分离」：SolidJS 管组件/signal/响应式，画到哪由可插拔渲染器决定——画到浏览器 DOM 是网页、画到终端就是 opentui。它分两层：@opentui/core(引擎：布局/绘制/输入)+@opentui/solid(SolidJS 绑定：render/useRenderer)。JSX 原语是终端版 HTML 标签：<box>(≈div,flexbox 容器)、<text>、<scrollbox>、<input>/<textarea>。布局用 flexDirection/flexGrow/justifyContent 等 CSS flexbox。于是你用和写网页一样的心智模型搭终端 App，opentui 把「组件树怎么变成屏幕字符」全包了——无需手写 ANSI、手算坐标。这是把整个前端渲染范式整体复用（同 L51 复用 git、L39 复用 Ripgrep）。", "en": "opencode uses opentui — a renderer that renders SolidJS to the terminal, essentially \"a browser for the terminal.\" The essence of modern frameworks is \"separating renderer from framework\": SolidJS handles components/signals/reactivity, where to paint is decided by a pluggable renderer — paint to the browser DOM and it's a web page, to the terminal and it's opentui. It's two layers: @opentui/core (engine: layout/paint/input) + @opentui/solid (SolidJS bindings: render/useRenderer). JSX primitives are terminal HTML tags: <box> (≈div, flexbox container), <text>, <scrollbox>, <input>/<textarea>. Layout via flexDirection/flexGrow/justifyContent CSS flexbox. So you build a terminal app with the same mental model as a web page, opentui handles all of \"how the component tree becomes screen characters\" — no hand-writing ANSI, no manual coordinates. This reuses the entire frontend rendering paradigm wholesale (like L51 reusing git, L39 reusing Ripgrep)."},
            },
            {
                "q": {"zh": "为什么把 SolidJS 的「细粒度响应式」搬进终端，对一个流畅的 TUI 如此关键？", "en": "Why is transplanting SolidJS's \"fine-grained reactivity\" into the terminal so crucial to a fluid TUI?"},
                "opts": [
                    {"zh": "终端绘制昂贵、带宽有限（尤其 SSH），整屏重画扛不住 60fps 还会闪；signal 让 signal 变→只标脏依赖它的元素→只重画脏元素→只刷变化的字符格（差分），把每次更新压到最小", "en": "Terminal painting is expensive, bandwidth limited (especially SSH); full-screen redraw can't sustain 60fps and flickers; signals make a signal change → only mark dependent elements dirty → only repaint dirty elements → only flush changed character cells (diff), squeezing each update to the minimum"},
                    {"zh": "细粒度响应式让代码更短", "en": "Fine-grained reactivity makes code shorter"},
                    {"zh": "终端不支持整屏重画", "en": "Terminals don't support full-screen redraw"},
                    {"zh": "为了兼容旧终端", "en": "For compatibility with old terminals"},
                ],
                "answer": 0,
                "why": {"zh": "终端绘制是昂贵的：每帧要把成千上万字符格连同颜色算出来、经一串 ANSI 转义码刷给终端。如果每次状态变化都整屏重画，60fps 扛不住、画面还会闪；而且终端「带宽」有限——刷的字符越多，写出去的转义码越长越慢，SSH 远程尤其明显。所以「每次只刷最少的格子」是流畅 TUI 的生死线。SolidJS 的 signal 让更新外科手术般精确：某 signal 变→只有依赖它的那几个元素被标脏→opentui 只对脏元素重新布局/绘制→下一帧只刷变化的字符格（差分更新）。你只管用 signal 描述「数据是什么」，从不手动操心「重画屏幕哪一块」——依赖追踪+差分绘制自动把更新压到最小，和浏览器里用 Solid/React 一模一样，只是最小更新单位从 DOM 节点变成终端字符格。", "en": "Terminal painting is expensive: each frame must compute thousands of character cells with colors and flush them via a string of ANSI escape codes. If every state change redrew the whole screen, 60fps couldn't hold and the screen would flicker; and the terminal's \"bandwidth\" is limited — the more characters flushed, the longer/slower the escape codes written, especially over SSH. So \"flush the fewest cells each time\" is a fluid TUI's lifeline. SolidJS's signals make updates surgically precise: some signal changes → only the few elements depending on it are marked dirty → opentui re-lays-out/repaints only dirty elements → the next frame flushes only changed character cells (diff update). You just describe \"what the data is\" with signals, never manually worrying \"which part of the screen to redraw\" — dependency tracking + diff painting auto-squeeze updates to the minimum, identical to using Solid/React in the browser, only the minimal-update unit changes from a DOM node to a terminal character cell."},
            },
            {
                "q": {"zh": "opencode 为什么把 createCliRenderer 包进 Effect 的 acquireRelease 里？", "en": "Why does opencode wrap createCliRenderer in Effect's acquireRelease?"},
                "opts": [
                    {"zh": "渲染器是个会独占并改写终端状态的资源（切备用屏/关回显/进 raw 模式）；acquireRelease 保证无论怎么退出（正常/异常/SIGHUP）destroyRenderer 必被执行，把终端恢复原状、不留烂摊子", "en": "The renderer is a resource that exclusively takes over and rewrites terminal state (alt screen/echo off/raw mode); acquireRelease guarantees that however you exit (normal/exception/SIGHUP) destroyRenderer is necessarily executed, restoring the terminal, leaving no mess"},
                    {"zh": "为了让渲染器跑得更快", "en": "To make the renderer run faster"},
                    {"zh": "acquireRelease 能减少内存占用", "en": "acquireRelease reduces memory usage"},
                    {"zh": "纯粹是代码风格要求", "en": "Purely a code-style requirement"},
                ],
                "answer": 0,
                "why": {"zh": "渲染器是一个会独占并改写你终端状态的资源（切到备用屏、关回显、进 raw 模式…）。一旦 App 崩了或被强杀，若不复原，终端会彻底错乱（光标乱跑、看不见输入）。Effect.acquireRelease 把「获取资源」和「释放资源」绑在一起，保证无论以何种方式退出——正常关、抛异常、收到 SIGHUP——那个 destroyRenderer 清理函数必定被执行，把终端恢复如初。这正是第 2 部分 Effect「资源获取与释放绑定、释放必然发生」的纪律，用在最容易把终端搞坏的 TUI 入口上。一个体贴的 TUI 不仅要画得好看，更要在退出时把舞台收拾干净——而结构化资源管理让「收拾干净」从靠自觉变成结构上无法遗漏。", "en": "The renderer is a resource that exclusively takes over and rewrites your terminal state (switches to the alternate screen, turns off echo, enters raw mode…). Once the App crashes or is force-killed, if not restored, the terminal will be thoroughly scrambled (cursor flying, input invisible). Effect.acquireRelease binds \"acquire resource\" and \"release resource\" together, guaranteeing that however you exit — normal close, thrown exception, received SIGHUP — that destroyRenderer cleanup function is necessarily executed, restoring the terminal to as-new. This is exactly Part 2's Effect \"acquisition and release bound, release necessarily happens\" discipline, applied at the TUI entry most likely to break the terminal. A thoughtful TUI must not only paint nicely but tidy up the stage on exit — and structured resource management turns \"tidying up\" from self-discipline into something structurally impossible to forget."},
            },
        ],
        "open": [
            {"zh": "课里反复强调 opentui 是「终端里的浏览器」——把整套 Web 渲染范式（DOM 般元素树、flexbox、60fps 绘制循环、键鼠事件）搬进 TTY，让你用和写网页一样的心智模型搭终端 App。请你谈谈这种「把成熟范式整体复用到新目标」的设计决策：它给 opencode 省下了什么（不必发明新 UI 框架、复用 SolidJS 生态、三端统一心智）？又有什么代价或局限（终端的字符网格 vs 像素、颜色/字体受限、依赖 opentui 的成熟度）？你是否见过/做过类似「把 React 渲染到非 DOM 目标」（react-three-fiber、Ink、react-native）的案例？它们的得失如何？", "en": "The lesson repeatedly stresses opentui is \"a browser for the terminal\" — transplanting the whole web rendering paradigm (DOM-like element tree, flexbox, 60fps paint loop, kb/mouse events) into the TTY, letting you build a terminal app with the same mental model as a web page. Discuss this \"reuse a mature paradigm wholesale on a new target\" design decision: what does it save opencode (no new UI framework, reuse the SolidJS ecosystem, unified mental model across three clients)? What are the costs or limitations (the terminal's character grid vs pixels, limited colors/fonts, dependence on opentui's maturity)? Have you seen/done a similar \"render React to a non-DOM target\" case (react-three-fiber, Ink, react-native)? How do their tradeoffs compare?"},
            {"zh": "课里说终端绘制昂贵、带宽有限，所以「每次只刷最少的字符格」是流畅 TUI 的生死线，而 SolidJS 的细粒度响应式恰好天然满足这点（signal 变→只重画依赖它的元素→只刷变化的格子）。请你对比「细粒度响应式（SolidJS signal）」与「虚拟 DOM diff（React）」两种『把更新压到最小』的思路：它们各自如何决定「重画什么」？在终端这种『刷新成本极高、带宽极有限』的渲染目标上，为什么细粒度响应式可能比 vDOM diff 更有优势？反过来，vDOM 有没有它的长处？", "en": "The lesson says terminal painting is expensive and bandwidth limited, so \"flush the fewest character cells each time\" is a fluid TUI's lifeline, and SolidJS's fine-grained reactivity happens to satisfy this naturally (signal changes → only repaint elements depending on it → only flush changed cells). Compare \"fine-grained reactivity (SolidJS signals)\" with \"virtual DOM diff (React)\" as two approaches to \"squeezing updates to the minimum\": how does each decide \"what to repaint\"? On a render target like the terminal where \"refresh cost is very high, bandwidth very limited,\" why might fine-grained reactivity have an edge over vDOM diff? Conversely, does vDOM have its own strengths?"},
        ],
    },

    "51-compaction-snapshots.html": {
        "mcq": [
            {
                "q": {"zh": "当一场对话快撑爆模型上下文窗口时，opencode 的压缩（compaction）怎么做？", "en": "When a conversation nearly overflows the model's context window, how does opencode's compaction work?"},
                "opts": [
                    {"zh": "select 切分=最近约 8000 token 的消息逐字留原文、更早的交 LLM 折成一份固定结构摘要（Goal/Constraints/Progress/Decisions/Next Steps/Context/Files），且摘要锚定式增量更新（旧摘要上保留/删除/并入，主线不断裂）", "en": "select split = keep the most recent ~8000 tokens of messages verbatim, fold the earlier into a fixed-structure summary via LLM (Goal/Constraints/Progress/Decisions/Next Steps/Context/Files), with the summary anchored incrementally updated (preserve/remove/merge on the old summary, main thread unbroken)"},
                    {"zh": "直接删掉最早的一半消息", "en": "Just delete the earliest half of messages"},
                    {"zh": "把整场对话压成一句话", "en": "Compress the whole conversation into one sentence"},
                    {"zh": "换一个上下文窗口更大的模型", "en": "Switch to a model with a larger context window"},
                ],
                "answer": 0,
                "why": {"zh": "compactIfNeeded 在请求 token 超过 上下文−max(输出量, 缓冲20000) 时触发。核心是 select 那一刀切分：从对话末尾倒着累加，保留最近约 8000 token（DEFAULT_KEEP_TOKENS）的消息逐字原样（recent），更早的一大段（head）交 LLM 浓缩成结构化摘要——填进固定模板（Goal/Constraints & Preferences/Progress(Done/In Progress/Blocked)/Key Decisions/Next Steps/Critical Context/Relevant Files），保证关键维度不丢。最妙是锚定式增量：已压缩过则在旧摘要上「保留仍成立、删过时、并入新事实」而非重写——否则越早的信息会在一次次压缩中被稀释遗忘；锚定让主线跨多次压缩不断裂。select 甚至能从单条消息中间按剩余字符切两半（×4≈1token4字符），把保留预算用到极致。和 L42 有界输出同一种「上下文稀缺」哲学的不同层级回响。", "en": "compactIfNeeded triggers when request tokens exceed context−max(output, buffer 20000). The core is the select split: accumulating backward from the conversation's end, keep the most recent ~8000 tokens (DEFAULT_KEEP_TOKENS) of messages verbatim (recent), hand the big earlier stretch (head) to the LLM to condense into a structured summary—filled into a fixed template (Goal/Constraints & Preferences/Progress(Done/In Progress/Blocked)/Key Decisions/Next Steps/Critical Context/Relevant Files), guaranteeing key dimensions aren't lost. The finest is anchored incremental: if already compacted, \"preserve still-true, remove stale, merge new facts\" on the old summary rather than rewrite—else the earliest info would be diluted and forgotten across successive compactions; anchoring keeps the main thread unbroken across compactions. select can even cut a single message in two by remaining chars (×4≈1token 4chars), using the keep budget to the hilt. The same \"context scarce\" philosophy as L42 bounded output echoing at a different level."},
            },
            {
                "q": {"zh": "opencode 的快照（snapshot）系统如何给工作目录做版本管理，又不污染你自己的 git 提交历史？", "en": "How does opencode's snapshot system version-manage the working directory without polluting your own git commit history?"},
                "opts": [
                    {"zh": "用一个「影子 git 仓库」——独立 --git-dir（在数据目录下）+ --work-tree 指你的真实工作目录，绝不碰你的 .git；track=git write-tree 出树哈希、restore=read-tree+checkout-index 还原；alternates 共享对象省空间", "en": "Use a \"shadow git repo\" — a separate --git-dir (under the data dir) + --work-tree pointing at your real working directory, never touching your .git; track=git write-tree for a tree hash, restore=read-tree+checkout-index; alternates share objects to save space"},
                    {"zh": "在你的 .git 里频繁 commit", "en": "Frequently commit into your .git"},
                    {"zh": "把整个工作目录复制一份到别处", "en": "Copy the entire working directory elsewhere"},
                    {"zh": "用自研的二进制 diff 格式存快照", "en": "Store snapshots in a self-made binary diff format"},
                ],
                "answer": 0,
                "why": {"zh": "snapshot/index.ts 的妙招是另起一个影子 git 仓库：在 数据目录/snapshot/<项目>/<工作目录哈希> 下建独立 git 仓库，所有命令带 --git-dir <影子> --work-tree <你的真实工作目录>，绝不碰项目里真实的 .git。track()=git add 暂存→git write-tree 写出一个树对象返回哈希（这就是一张快照，用最轻的 git 原语、不需 commit 信息/作者/父提交）；restore(snapshot)=git read-tree <快照>+checkout-index -a -f 还原工作目录。三处妙：① write-tree 而非 commit（最轻原语干最纯的事）；② 影子仓库与 .git 彻底隔离（opencode 几乎每步都拍快照，若污染你的 git log 是灾难）；③ 复用 git 二十年的内容寻址存储（增量/去重/diff），如 L39 复用 Ripgrep。还通过 objects/info/alternates 共享真实仓库对象省空间、尊重 .gitignore、屏蔽大文件。", "en": "snapshot/index.ts's trick is spinning up a shadow git repo: build a separate git repo under data-dir/snapshot/<project>/<worktree-hash>, all commands carrying --git-dir <shadow> --work-tree <your real working directory>, never touching the project's real .git. track()=git add stages→git write-tree writes a tree object returning a hash (that's a snapshot, the lightest git primitive, no commit message/author/parent needed); restore(snapshot)=git read-tree <snapshot>+checkout-index -a -f restores the working dir. Three clever points: ① write-tree not commit (lightest primitive for the purest job); ② the shadow repo is fully isolated from .git (opencode snapshots around almost every step; polluting your git log would be a disaster); ③ reuse git's twenty-years content-addressable storage (incremental/dedup/diff), like L39 reusing Ripgrep. It also shares the real repo's objects via objects/info/alternates to save space, respects .gitignore, blocks large files."},
            },
            {
                "q": {"zh": "revert（退回到某条消息）为什么必须把「对话」和「文件」绑在同一条时间轴上一起回退？又如何做到可反悔（unrevert）？", "en": "Why must revert (rolling back to a message) bind \"conversation\" and \"files\" on the same timeline to roll back together? And how is it reversible (unrevert)?"},
                "opts": [
                    {"zh": "只退对话不退文件（或反之）会造成「对话以为没改、文件却已改」的错乱，唯有两者一起回到过去那一刻才自洽；revert 前先 snap.track() 把「现在」存进 session.revert 字段，故 unrevert 能 restore 回 revert 前", "en": "Rewinding only the conversation but not files (or vice versa) causes the disorder of \"the conversation thinks nothing changed yet files are changed\"; only both returning together is self-consistent; before revert, snap.track() saves \"now\" into the session.revert field, so unrevert can restore back to before revert"},
                    {"zh": "只需退对话，文件不用管", "en": "Only the conversation needs rewinding, files don't matter"},
                    {"zh": "revert 不可反悔，是一次性操作", "en": "revert is irreversible, a one-shot operation"},
                    {"zh": "靠用户手动备份文件", "en": "Relies on the user manually backing up files"},
                ],
                "answer": 0,
                "why": {"zh": "revert.ts 让你退回某条消息（messageID，可细到 partID），做两件事的合体：退对话（裁掉该消息之后的消息）+退文件（snap.revert 按补丁把改动过的文件逐一退回那时的状态）。为什么必须一起退？因为单退对话不退文件，会面对「对话以为没改过、文件却已被改」的错乱；单退文件不退对话同理——唯有两者作为整体一起回到过去，那一刻的世界才自洽。可反悔的关键：revert 在还原前先 snap.track() 给「现在」拍快照、存进 L49 session 表那个 revert:{messageID,partID?,snapshot?,diff?} JSON 列，于是 unrevert 能用 snap.restore 整体还原回 revert 之前——后悔药也有后悔药。状态被持久化，重启仍有效。这正是 L49 session.revert 列的用武之地、L51 compaction(对话记忆)+snapshot(文件记忆)的合体。", "en": "revert.ts lets you roll back to a message (messageID, down to partID), a fusion of two things: rewind conversation (trim messages after it) + rewind files (snap.revert rolls the changed files back per-patch to that state). Why must they roll back together? Because rewinding only the conversation not files faces the disorder of \"the conversation thinks nothing changed yet files are changed\"; rewinding only files not conversation likewise—only both, as a whole, returning to the past is that moment's world self-consistent. The key to reversibility: before reverting, revert first snap.track()s a snapshot of \"now,\" storing it in L49 session-table's revert:{messageID,partID?,snapshot?,diff?} JSON column, so unrevert can use snap.restore to restore wholesale back to before revert—even the regret pill has a regret pill. The state is persisted, works after restart. This is exactly where L49's session.revert column earns its keep, and L51's fusion of compaction (conversation memory) + snapshot (file memory)."},
            },
        ],
        "open": [
            {"zh": "课里把 compaction（压缩对话）和 L42 有界工具输出归为「同一种『上下文稀缺』哲学在不同层级的回响」——L42 管单个工具输出别撑爆上下文、compaction 管整场对话别撑爆。请你沿这条线，把全书出现过的「上下文/资源稀缺」应对策略串起来（L42 预览+spill、L37 definitions/settle、L43 skills 名字/正文、本课压缩的 recent/head 切分），提炼它们共同的「渐进式披露 / 按需兑现」骨架。再谈谈：把陈旧对话折成 LLM 生成的摘要，本质是「有损压缩」——这会带来什么风险（摘要遗漏、幻觉、不可逆）？锚定式增量更新在多大程度上缓解了它？", "en": "The lesson groups compaction (compressing conversation) with L42 bounded tool output as \"the same 'context scarce' philosophy echoing at different levels\"—L42 keeps a single tool output from overflowing context, compaction keeps a whole conversation from overflowing. Along this line, string together the \"context/resource scarcity\" coping strategies seen across the book (L42 preview+spill, L37 definitions/settle, L43 skills name/body, this lesson's compaction recent/head split), distilling their shared \"progressive disclosure / fulfill on demand\" skeleton. Then discuss: folding stale conversation into an LLM-generated summary is essentially \"lossy compression\"—what risks does this bring (summary omission, hallucination, irreversibility)? To what extent does anchored incremental update mitigate it?"},
            {"zh": "课里盛赞「影子 git 仓库」的设计：opencode 频繁给工作目录拍快照、却放进一个独立 git-dir，绝不污染你真实的 .git 提交历史，还通过 alternates 复用 git 对象。这体现了「复用一个成熟工具的强大能力、却把它隔离起来避免副作用」的工程智慧。请你结合 L39 复用 Ripgrep、L35 复用上游模型目录等例子，谈谈 opencode 反复出现的「站在巨人肩上、但小心隔离」模式：什么时候该复用现成的强大工具而非自研？复用时如何划清边界、避免它的副作用（如这里的「别弄乱用户的 git」）泄漏出来？你做过类似的「借力又隔离」的设计吗？", "en": "The lesson praises the \"shadow git repo\" design: opencode frequently snapshots the working directory yet puts it in a separate git-dir, never polluting your real .git commit history, and reuses git objects via alternates. This embodies the engineering wisdom of \"reuse a mature tool's powerful capability yet isolate it to avoid side effects.\" From examples like L39 reusing Ripgrep and L35 reusing the upstream model catalog, discuss opencode's recurring \"stand on giants' shoulders but isolate carefully\" pattern: when should you reuse a ready-made powerful tool rather than build your own? When reusing, how to draw clear boundaries and prevent its side effects (here, \"don't scramble the user's git\") from leaking out? Have you done a similar \"borrow power yet isolate\" design?"},
        ],
    },

    "50-v1-storage-migration.html": {
        "mcq": [
            {
                "q": {"zh": "V1 文件存储（storage.ts）的核心设计「键即路径」是什么意思？", "en": "What does V1 file storage's (storage.ts) core design \"key as path\" mean?"},
                "opts": [
                    {"zh": "用 string[] 数组当键，file(dir,key)=join(dir,...key)+\".json\" 直接拼成文件路径——一个对象一个 JSON 文件，整个「数据库」就是 storage 下一棵目录树，不需要任何数据库引擎", "en": "Uses a string[] array as the key, file(dir,key)=join(dir,...key)+\".json\" joins directly into a file path — one object one JSON file, the whole \"database\" a directory tree under storage, needing no database engine"},
                    {"zh": "把所有数据存进一个巨大的 JSON 文件", "en": "Stores all data in one giant JSON file"},
                    {"zh": "用一个内存哈希表当数据库", "en": "Uses an in-memory hash table as the database"},
                    {"zh": "键是随机生成的、和路径无关", "en": "Keys are randomly generated, unrelated to paths"},
                ],
                "answer": 0,
                "why": {"zh": "storage.ts 的 Storage 服务用 string[] 数组当键，核心魔法一行：file(dir,key)=path.join(dir,...key)+\".json\"——把键直接拼成文件路径。于是 [\"session\",\"proj_abc\",\"ses_123\"] 对应磁盘上 storage/session/proj_abc/ses_123.json。一个对象一个 JSON 文件，整个「数据库」就是 Global.Path.data/storage 下一棵目录树，每个叶子是个 JSON。简单到不需要数据库引擎、文件还人眼可读——对早期项目是合理起点。五个方法 read/write/update/remove/list，每文件配 TxReentrantLock 读写锁（update=握写锁读改写）。但简单有代价：list 无索引只能 glob 整棵树、无跨对象事务、无外键 cascade、无关系查询——正是这些逼出了向 SQLite 的迁移。", "en": "storage.ts's Storage service uses a string[] array as the key, the core magic one line: file(dir,key)=path.join(dir,...key)+\".json\"—joining the key directly into a file path. So [\"session\",\"proj_abc\",\"ses_123\"] maps to storage/session/proj_abc/ses_123.json on disk. One object one JSON file, the whole \"database\" a directory tree under Global.Path.data/storage, each leaf a JSON. Simple enough to need no database engine, files human-readable too—a reasonable start for an early project. Five methods read/write/update/remove/list, each file a TxReentrantLock read/write lock (update = hold write lock read-modify-write). But simplicity has a cost: list has no index so must glob the whole tree, no cross-object transaction, no FK cascade, no relational query—exactly what forced the migration to SQLite."},
            },
            {
                "q": {"zh": "L48 的 schema 迁移用 migration 表记账，本课 V1→V2 数据迁移用 data_migration 表记账。这两张表的关系是？", "en": "L48's schema migration bookkeeps with a migration table, this lesson's V1→V2 data migration with a data_migration table. The relationship between these two tables is?"},
                "opts": [
                    {"zh": "同款「记账即幂等」范式用在两个不同问题上——migration 记『哪些 schema 结构变更跑过了』，data_migration 记『哪些数据搬运跑过了』；都是两列(name/id + time_completed)、都靠记录已完成项实现幂等", "en": "The same \"bookkeeping = idempotency\" paradigm on two different problems — migration records \"which schema structure changes ran,\" data_migration records \"which data moves ran\"; both two columns (name/id + time_completed), both achieve idempotency by recording completed items"},
                    {"zh": "data_migration 是 migration 表的备份", "en": "data_migration is a backup of the migration table"},
                    {"zh": "两张表完全无关，纯属重名", "en": "The two tables are wholly unrelated, just a name coincidence"},
                    {"zh": "data_migration 取代了 migration 表", "en": "data_migration replaced the migration table"},
                ],
                "answer": 0,
                "why": {"zh": "同一个「日志表记账即幂等」的朴素思想被复用了两次，解决两个不同问题：L48 的 migration 表记 schema 变更（结构演化：加列、改表），本课 data_migration 表（data-migration.sql.ts，就两列 name+time_completed）记数据搬运（V1 文件→V2 SQLite）。两者都靠「记录哪些已完成、跳过已记录的」实现幂等——跑过的不重跑。这种「一个好范式解决多类问题」正是优秀工程的标志。值得注意：V1 数据搬进 SQLite 的 message/part 表时仍存 V1-shaped JSON（即 L49 见到的「V1 同堂」之源），并未立刻翻译成 V2；真正的 V1→V2 语义转换推迟到读取时由 message-v2 投影——「搬运」与「翻译」解耦，让最危险的批量迁移退化成最无脑的字节复制。", "en": "The same \"journal-table bookkeeping = idempotency\" plain idea reused twice, solving two different problems: L48's migration table records schema changes (structure evolution: add column, change table), this lesson's data_migration table (data-migration.sql.ts, just two columns name+time_completed) records data moves (V1 files→V2 SQLite). Both achieve idempotency by \"recording what's completed, skipping recorded ones\"—run ones don't rerun. This \"one good paradigm solving multiple problem types\" is the mark of excellent engineering. Note: when V1 data moves into SQLite's message/part tables it still holds V1-shaped JSON (the source of L49's \"V1 under one roof\"), not immediately translated to V2; the real V1→V2 semantic conversion is deferred to read time, projected by message-v2—\"moving\" decoupled from \"translating,\" letting the most dangerous bulk migration degrade into the most brainless byte copy."},
            },
            {
                "q": {"zh": "storage.ts 的迁移驱动循环里，一旦某个迁移失败就 break（停下、不推进标记）。为什么这么保守？", "en": "In storage.ts's migration driver loop, the moment a migration fails it breaks (stops, doesn't advance the marker). Why so conservative?"},
                "opts": [
                    {"zh": "迁移间常有先后依赖——后一个假设前一个已把数据整理成某形态；前一个失败还硬跑后面的，会在半残状态上越搞越乱酿成损坏。「失败就停在原地、下次重试这一个」远比「带病前进」安全", "en": "Migrations often have order dependencies — a later one assumes the prior shaped the data a certain way; if the prior failed and you barrel ahead, you make a bigger mess on a half-broken state, causing corruption. \"Stop in place on failure, retry this one next time\" is far safer than \"advance while sick\""},
                    {"zh": "为了让迁移跑得更快", "en": "To make migration run faster"},
                    {"zh": "因为 SQLite 不支持连续迁移", "en": "Because SQLite doesn't support consecutive migrations"},
                    {"zh": "为了节省磁盘空间", "en": "To save disk space"},
                ],
                "answer": 0,
                "why": {"zh": "迁移之间往往有先后依赖：后一个迁移很可能假设前一个已经把数据整理成某种形态。如果前一个失败了还硬着头皮跑后面的，极可能在一个半残的数据状态上越搞越乱，最终酿成无法收拾的损坏。所以 storage.ts 一旦某迁移失败就立刻 break、不推进标记——「失败就停在原地、下次重试这一个」远比「带病前进」安全。配合标记文件的断点续跑（读标记→从该处跑 pending→成功才+1），整个迁移既能从中断处接着走、又绝不在出错时把事情搞得更糟。这和 L48 schema 迁移那句 die(\"库非空却无 session 表\") 的防呆是同一种工程品格：在「错了就可能丢数据」的高危操作上，宁可保守地停下报错，绝不乐观地猜测推进。", "en": "Migrations often have order dependencies: a later migration likely assumes the prior already shaped the data a certain way. If the prior failed and you barrel ahead, you very likely make a bigger mess on a half-broken data state, ending in unsalvageable corruption. So the moment a migration fails storage.ts breaks immediately, not advancing the marker—\"stop in place on failure, retry this one next time\" is far safer than \"advance while sick.\" Paired with the marker file's resumability (read marker→run pending from there→+1 only on success), the whole migration both continues from where it stopped and never makes things worse on error. This is the same engineering character as L48 schema migration's die(\"DB non-empty yet no session table\") guard: on a high-risk operation where \"a slip can lose data,\" rather conservatively stop and error than optimistically guess and advance."},
            },
        ],
        "open": [
            {"zh": "课里讲 V1→V2 迁移有个务实设计：V1 数据搬进 SQLite 时不立刻翻译成 V2，而是以 V1-shaped JSON 原样躺着，真正的语义转换推迟到读取时由 message-v2 投影——「搬运」与「翻译」解耦，且原始字节始终保真（写错映射只需改投影、不必重跑迁移）。课里还把这条「保真原始、按需解释」和 L42 有界输出「全文 spill、按需回取」、L43 skills「名字常驻、正文按需」归为同一种深谋远虑。请你提炼这种「不破坏性改写原始数据、把转换推迟到使用时」的设计模式，谈谈它的威力（可纠错、可重新解释、迁移更安全）与代价（读取时开销、两种形态共存的复杂度），并举一个你见过的类似例子。", "en": "The lesson covers a pragmatic design in V1→V2 migration: V1 data moved into SQLite isn't immediately translated to V2 but lies as V1-shaped JSON verbatim, the real semantic conversion deferred to read time, projected by message-v2—\"moving\" decoupled from \"translating,\" and original bytes stay faithful (a wrong mapping needs only fixing the projection, no rerun of the migration). The lesson also groups this \"preserve the original, interpret on demand\" with L42 bounded output's \"spill full text, fetch on demand\" and L43 skills' \"names resident, body on demand\" as the same foresight. Distill this \"don't destructively rewrite original data, defer conversion to use time\" design pattern, discuss its power (error-correctable, re-interpretable, safer migration) and cost (read-time overhead, complexity of two coexisting forms), and give a similar example you've seen."},
            {"zh": "课里说 V1 文件存储「简单到极致」（一个对象一个 JSON、键即路径、人眼可读），但最终被它的代价（无索引/无事务/无外键/无关系查询）逼着迁移到 SQLite。这是几乎每个长期项目都会经历的「从简单方案长成复杂方案」的剧情。请你结合自己的经验谈谈：你会怎样判断「一个简单存储方案什么时候该升级」？过早上数据库（YAGNI 的反面）和拖太久才迁移（技术债爆炸）各有什么风险？如果重来一次，你认为 opencode「先用文件、后迁 SQLite」这个演进路径是明智的，还是「一开始就该用 SQLite」？为什么？", "en": "The lesson says V1 file storage is \"simple to the extreme\" (one object one JSON, key as path, human-readable) but was eventually forced to migrate to SQLite by its costs (no index/no transaction/no FK/no relational query). This is the \"grow from a simple scheme into a complex one\" plot nearly every long-term project lives through. From your own experience, discuss: how would you judge \"when a simple storage scheme should be upgraded\"? What are the risks of adopting a database too early (the opposite of YAGNI) versus migrating too late (tech-debt explosion)? If you did it over, do you think opencode's \"use files first, migrate to SQLite later\" evolution path was wise, or \"should have used SQLite from the start\"? Why?"},
        ],
    },

    "49-core-tables.html": {
        "mcq": [
            {
                "q": {"zh": "opencode 核心表网里，session 表扮演什么角色？删掉一个 session 会怎样？", "en": "In opencode's core table web, what role does the session table play? What happens when you delete a session?"},
                "opts": [
                    {"zh": "session 是整张表网的中枢——几乎所有表（message/part/session_message/session_input/epoch/todo）外键指回它且带 onDelete:cascade；删一个 session，其名下所有记录连根带走，数据库保证不留孤儿", "en": "session is the hub of the whole table web — nearly all tables (message/part/session_message/session_input/epoch/todo) FK back to it with onDelete:cascade; delete a session and all its records are uprooted, the DB guarantees no orphans"},
                    {"zh": "session 只是一张普通表，删它不影响其它表", "en": "session is just an ordinary table, deleting it doesn't affect others"},
                    {"zh": "删 session 需要应用代码手动逐表清理", "en": "Deleting a session requires app code to manually clean each table"},
                    {"zh": "session 表存所有消息内容", "en": "The session table stores all message content"},
                ],
                "answer": 0,
                "why": {"zh": "session 是整张表网的根/中枢：project→session（project_id），session→message→part（两级）、session→session_message/session_input/session_context_epoch/todo，几乎所有外键都带 onDelete:cascade。于是删一个 project，其下所有 session 跟着删；删一个 session，其下所有 message/part/session_message/input/epoch/todo 全部跟着删——「拔起树根连根带走所有枝叶」。这种「无孤儿」一致性不是靠应用代码小心手动删，而是靠外键约束由数据库强制兜底（也正因此 L48 那句 PRAGMA foreign_keys=ON 不可省——SQLite 默认不强制外键，必须显式打开 cascade 才生效）。session 自身还有 parent_id 自指列（带索引的普通列、并非外键），指向父会话（subagent 落盘）；注意它没有 cascade，删父会话不会连带删子会话。", "en": "session is the root/hub of the whole table web: project→session (project_id), session→message→part (two levels), session→session_message/session_input/session_context_epoch/todo, nearly all FKs with onDelete:cascade. So delete a project, all its sessions follow; delete a session, all its message/part/session_message/input/epoch/todo follow — \"uproot the tree taking all branches.\" This \"no orphan\" consistency isn't from app code carefully deleting by hand but from FK constraints enforced as a backstop by the DB (and exactly why L48's PRAGMA foreign_keys=ON can't be omitted — SQLite doesn't enforce FKs by default, cascade only works if explicitly turned on). session itself also has a parent_id self-referencing column (an indexed plain column, not a foreign key) pointing at the parent session (subagent on disk); note it has no cascade, so deleting a parent session doesn't delete its sub-sessions."},
            },
            {
                "q": {"zh": "为什么 opencode 库里同时有 message+part（V1）和 session_message（V2）两套存消息的表？", "en": "Why does opencode's DB have both message+part (V1) and session_message (V2), two sets of tables storing messages?"},
                "opts": [
                    {"zh": "两代消息模型为平滑迁移而同堂——不可能一夜把所有历史会话从 V1 瞬切 V2，正确做法是两代在同一库共存一段时间，旧数据 V1 形态躺着、新数据 V2 写入，再慢慢迁移（L50 主题）", "en": "Two generations of message model coexist for smooth migration — you can't snap all historical sessions from V1 to V2 overnight; the right way is the two coexist in the same DB for a while, old data in V1 form, new data written in V2, then slowly migrate (L50's theme)"},
                    {"zh": "V1 存文字、V2 存图片，分工不同", "en": "V1 stores text, V2 stores images, different duties"},
                    {"zh": "纯属冗余设计失误", "en": "Pure redundant design mistake"},
                    {"zh": "V2 是 V1 的实时备份", "en": "V2 is a real-time backup of V1"},
                ],
                "answer": 0,
                "why": {"zh": "「新旧同堂」不是混乱，而是大型有状态系统演进的常态与智慧：你不可能某个深夜「啪」地把所有历史会话从 V1 瞬切到 V2，风险太大。正确做法是让两代模型在同一库共存一段时间——旧数据继续以 V1（message+part，data 是 JSON 大对象，两级结构）躺着、新数据以 V2（session_message，单表+seq+type）写入，再用专门迁移过程慢慢把 V1 翻译成 V2（正是 L50 主题）。这张「同堂」快照本身就是 opencode 正从 V1 向 V2 演进途中的活化石，揭示一条工程真理：真实世界的 schema 从不是定稿蓝图，而是还在续写的历史。两代差异更多在「怎么编号/入箱/上下文落盘」的编排层，而非「一条消息长什么样」的内容层。", "en": "\"Old and new under one roof\" isn't chaos but the norm and wisdom of large stateful systems evolving: you can't, one late night, snap all historical sessions from V1 to V2 — too risky. The right way is to let the two coexist in the same DB for a while — old data lying in V1 (message+part, data is a big JSON object, two-level structure), new data written in V2 (session_message, single table+seq+type), then slowly translate V1 into V2 with a dedicated migration (exactly L50's theme). This \"under one roof\" snapshot is itself a living fossil of opencode mid-evolution from V1 toward V2, revealing an engineering truth: a real-world schema is never a finalized blueprint but a history still being written. The generational difference is more at the orchestration level of \"how to number/inbox/persist context\" than the content level of \"what a message looks like.\""},
            },
            {
                "q": {"zh": "V2 的 session_input 是个「durable 输入箱」：你发的话先「入箱」(admitted_seq)、再由运行器「晋升」成可见 session_message(promoted_seq)。为什么不直接塞进对话？", "en": "V2's session_input is a \"durable inbox\": a sentence you send is first \"admitted\" (admitted_seq), then \"promoted\" by the runner into a visible session_message (promoted_seq). Why not stuff it straight into the conversation?"},
                "opts": [
                    {"zh": "先持久入箱再晋升，能保证即使进程在「收到输入」和「处理输入」之间崩溃，输入也已稳稳躺在库里，重启后接着处理——输入永不丢失", "en": "Admit durably first then promote guarantees that even if the process crashes between \"receiving input\" and \"processing input,\" the input already lies safely in the DB and is processed after restart — input is never lost"},
                    {"zh": "为了让输入显示得更快", "en": "To make input display faster"},
                    {"zh": "为了节省数据库空间", "en": "To save database space"},
                    {"zh": "因为 SQLite 不支持直接插入消息", "en": "Because SQLite can't insert messages directly"},
                ],
                "answer": 0,
                "why": {"zh": "session_input 是 V2 最精巧的一笔——durable（持久化）输入箱。发给 agent 的话不直接进对话，而是先作为一行 session_input 持久「入箱」（记 admitted_seq），之后串行运行器在安全边界把它「晋升」成可见 session_message（记 promoted_seq）；delivery 字段区分插队(steer)还是排队(queue)。先入箱再晋升的意义：即使进程在「收到」和「处理」之间崩溃，输入也已落库，重启能接着处理——永不丢失。这背后是 seq 这个无名英雄：session_message 用 unique(session,seq) 定序防重、session_input 用 admitted_seq/promoted_seq 分离记账、event 用 unique(aggregate,seq) 编号——单调序号+唯一索引同时给「全序」和「幂等」，重启的运行器只需问「晋升到第几号」就知从哪继续，绝不重复晋升、绝不漏。", "en": "session_input is V2's most exquisite stroke — a durable inbox. A sentence to the agent doesn't go straight into the conversation but is first durably \"admitted\" as a session_input row (record admitted_seq), then the serial runner \"promotes\" it into a visible session_message at a safe boundary (record promoted_seq); the delivery field distinguishes cut-in (steer) vs queue. The point of admit-first-promote-later: even if the process crashes between \"received\" and \"processed,\" the input is already in the DB and can be processed after restart — never lost. Behind this is seq, the unsung hero: session_message uses unique(session,seq) to order and prevent dups, session_input uses admitted_seq/promoted_seq for separate journaling, event uses unique(aggregate,seq) to number — monotonic number + unique index gives both \"total order\" and \"idempotency,\" a restarted runner need only ask \"promoted to what number\" to know where to resume, never re-promoting, never missing."},
            },
        ],
        "open": [
            {"zh": "课里点出一条贯穿全库的列设计哲学：需要被查询/排序/做约束的字段（id/session_id/type/seq）立成结构化真列，而千变万化的松散负载（消息内容）塞进 text({mode:\"json\"}) 列。请你解释这种「结构化骨架 + JSON 血肉」混搭的取舍：它分别从关系型数据库和文档型数据库各取了什么长处？什么时候一个字段「值得」从 JSON 里提升为真列？反过来，把本该是真列的东西埋进 JSON 会带来什么麻烦（查询、索引、约束、迁移）？结合你用过的系统谈谈。", "en": "The lesson points out a column-design philosophy running through the whole DB: fields needing query/sort/constraint (id/session_id/type/seq) become structured real columns, while the endlessly-varying loose payload (message content) goes into a text({mode:\"json\"}) column. Explain the trade-off of this \"structured skeleton + JSON flesh\" mix: what does it take from relational DBs and document DBs respectively? When is a field \"worth\" promoting from JSON to a real column? Conversely, what trouble does burying what should be a real column into JSON cause (query, index, constraint, migration)? Discuss from systems you've used."},
            {"zh": "课里强调 opencode 把「顺序与一致性」直接编码进 schema 的索引约束——session_message 的 unique(session,seq)、session_input 的 admitted_seq/promoted_seq、event 的 unique(aggregate,seq)——而非寄望应用代码每次记得检查，让「数据库结构本身成为正确性的最后一道防线」。请你谈谈「把不变量交给数据库约束兜底」相比「在应用层手动维护」的优劣：前者强在哪（崩溃/并发/多进程下仍可靠）？又有什么代价（约束冲突如何优雅处理、跨表/跨服务的不变量数据库管不了怎么办）？你会怎样划分「哪些不变量该下沉到 DB、哪些该留在应用层」？", "en": "The lesson stresses opencode encodes \"order and consistency\" directly into the schema's index constraints — session_message's unique(session,seq), session_input's admitted_seq/promoted_seq, event's unique(aggregate,seq) — rather than hoping app code remembers to check each time, letting \"the database structure itself be the last line of defense for correctness.\" Discuss the pros/cons of \"delegating invariants to DB constraints as a backstop\" versus \"manually maintaining them in the app layer\": where is the former strong (still reliable under crash/concurrency/multi-process)? What are its costs (how to gracefully handle constraint conflicts, what about cross-table/cross-service invariants the DB can't manage)? How would you divide \"which invariants should sink into the DB, which stay in the app layer\"?"},
        ],
    },

    "48-drizzle-sqlite.html": {
        "mcq": [
            {
                "q": {"zh": "opencode 用 Drizzle「代码即 schema」定义表，列名一律用 snake_case（如 project_id）而非 camelCase，主要好处是什么？", "en": "opencode defines tables with Drizzle \"code-as-schema,\" using snake_case column names (e.g. project_id) not camelCase; the main benefit is?"},
                "opts": [
                    {"zh": "Drizzle 默认直接拿字段名当列名——写 project_id: text() 列名就是 project_id，无需再把列名当字符串重写一遍（不必 projectID: text(\"project_id\")），省掉一类字段名/列名对不上的低级错误", "en": "Drizzle by default takes the field name as the column name — write project_id: text() and the column is project_id, no rewriting the column name as a string (no projectID: text(\"project_id\")), eliminating a class of field/column-name mismatch bugs"},
                    {"zh": "snake_case 查询更快", "en": "snake_case queries are faster"},
                    {"zh": "SQLite 只支持 snake_case 列名", "en": "SQLite only supports snake_case column names"},
                    {"zh": "为了和 Python 风格统一", "en": "To match Python style"},
                ],
                "answer": 0,
                "why": {"zh": "Drizzle 默认把字段名直接当列名：写 project_id: text()，列名就是 project_id，无需再写 projectID: text(\"project_id\") 把列名当字符串重复一遍。用 snake_case 字段名，字段名与列名天然一致，省掉一整类「字段名和列名字符串对不上」的低级错误——这是 opencode 全库的命名约定。课里还点出 Timestamps 复用片段（time_created $default、time_updated $onUpdate）：把横切所有表的公共结构抽成对象、各表 ...Timestamps 展开，正是「代码即 schema」相对裸 SQL 的红利——SQL 复制粘贴不了，代码可以。", "en": "Drizzle by default takes the field name as the column name: write project_id: text() and the column is project_id, no need for projectID: text(\"project_id\") rewriting the column name as a string. Using snake_case field names, field and column names naturally match, eliminating a whole class of \"field name and column-name string mismatch\" bugs — opencode's whole-codebase naming convention. The lesson also notes the Timestamps reusable fragment (time_created $default, time_updated $onUpdate): abstracting common structure cutting across all tables into an object, each table spreading ...Timestamps, is exactly \"code-as-schema\"'s dividend over raw SQL — SQL can't be copy-pasted, code can."},
            },
            {
                "q": {"zh": "面对「一个全新空库」和「一个用了半年的老库」，opencode 的迁移系统 apply() 分别怎么做？", "en": "Facing \"a brand-new empty DB\" and \"an old DB used for half a year,\" how does opencode's migration apply() handle each?"},
                "opts": [
                    {"zh": "双路径——新空库：直接套 schema.gen 完整快照建好所有最新表 + 把全部三十多个迁移一次记「已完成」(不重放)；老库：applyOnly 读 migration 日志、只补跑还没记过的迁移", "en": "Dual path — new empty DB: apply schema.gen full snapshot to build all latest tables + mark all thirty-some migrations \"completed\" at once (no replay); old DB: applyOnly reads the migration journal, backfills only migrations not yet recorded"},
                    {"zh": "两种库都从头重放全部三十多个迁移", "en": "Both DBs replay all thirty-some migrations from scratch"},
                    {"zh": "新库不建表、等用户手动建", "en": "New DB builds no tables, waits for the user to build manually"},
                    {"zh": "老库每次启动都重建整个库", "en": "Old DB rebuilds the entire DB on every startup"},
                ],
                "answer": 0,
                "why": {"zh": "apply() 先查 sqlite_master 看库里有没有表，分两条路：① 全新空库（无表）→ 跑 schema.gen 那份完整快照一步建好所有最新表，再建 migration 日志表、把全部三十多个迁移一次性记成「已完成」——新用户绝不重放历史。② 已有 session 表 → applyOnly：读 migration 日志里已完成的 id 集合，遍历全部迁移、只补跑那些还没记过的，每跑一个记一笔。这个「新库套快照、老库补增量」设计让新用户首次启动又快又干净、老用户平滑升级不丢数据。背后两件武器：增量迁移链（历史视角）+ schema.gen 完整快照（当下视角），由 drizzle-kit 同时维护并保证一致。", "en": "apply() first queries sqlite_master for whether the DB has tables, splitting two paths: ① brand-new empty DB (no tables) → run schema.gen's full snapshot to build all latest tables in one step, then create the migration journal table, marking all thirty-some migrations \"completed\" at once — new users never replay history. ② has session table → applyOnly: read the set of completed ids from the migration journal, iterate all migrations, backfill only those not yet recorded, logging each. This \"snapshot for new, increment for old\" design makes new users' first launch fast and clean, old users upgrade smoothly without losing data. Two weapons behind it: the incremental migration chain (historical view) + schema.gen full snapshot (present view), both maintained by drizzle-kit and guaranteed consistent."},
            },
            {
                "q": {"zh": "迁移系统靠什么保证「同一个 ALTER TABLE 重启一百次也不会执行两遍」，以及「表改了一半、日志没记」的撕裂状态不会出现？", "en": "What lets the migration system guarantee \"the same ALTER TABLE won't execute twice across a hundred restarts\" and that a torn \"table half-changed, journal unrecorded\" state never appears?"},
                "opts": [
                    {"zh": "migration 日志表(id+time_completed)记已跑过的→幂等；每个迁移裹在 db.transaction 里(升级 SQL 与记账同生共死)；整个 apply 被 Semaphore(1) 串行化", "en": "the migration journal table (id+time_completed) records what's run → idempotent; each migration wrapped in db.transaction (upgrade SQL and logging live or die together); the whole apply serialized by Semaphore(1)"},
                    {"zh": "每次迁移前手动备份数据库", "en": "Manually back up the DB before each migration"},
                    {"zh": "靠 SQLite 自动去重 ALTER 语句", "en": "Relying on SQLite to auto-dedupe ALTER statements"},
                    {"zh": "迁移只在第一次安装时跑，之后永不再跑", "en": "Migrations run only on first install, never again"},
                ],
                "answer": 0,
                "why": {"zh": "三道纪律：① 幂等——migration 日志表(就两列 id+time_completed)记着哪些迁移跑过了，applyOnly 遍历时跳过已记录的，所以重启多少次同一迁移都不会重跑。② 事务——每个迁移裹在 db.transaction 里：升级 SQL 和「往日志插一笔」要么一起提交、要么一起回滚，绝不会出现「表改了一半日志却没记」的撕裂。③ 串行——整个 apply 被 Semaphore(1) 信号量串行化，同一时刻只允许一个迁移流程在跑，杜绝多进程同时升级互相打架。配合 database.ts 的 PRAGMA（WAL 读写并发、foreign_keys=ON 让 cascade 生效等），整套存储既稳又能扛并发。", "en": "Three disciplines: ① idempotent — the migration journal table (just two columns id+time_completed) records which migrations ran, applyOnly skips recorded ones while iterating, so no matter how many restarts the same migration won't rerun. ② transactional — each migration wrapped in db.transaction: the upgrade SQL and \"insert a journal entry\" either both commit or both roll back, never a torn \"table half-changed, journal unrecorded\" state. ③ serial — the whole apply serialized by a Semaphore(1), only one migration flow at a time, preventing multiple processes upgrading at once and fighting. Combined with database.ts's PRAGMAs (WAL read/write concurrency, foreign_keys=ON making cascade effective, etc.), the whole storage is both stable and concurrency-tolerant."},
            },
        ],
        "open": [
            {"zh": "课里讲 apply() 有个防呆：如果库里「有表、却偏偏没有 session 表」，opencode 不贸然建表，而是直接报错退出——因为这极可能意味着 OPENCODE_DB 指错了别的程序的数据库。请你谈谈这种「对来历不明的库宁停勿乱」的设计哲学：它体现了什么样的工程克制？再结合你用过的工具（迁移框架、构建工具、配置加载器），举一个「工具自作主张反而酿成大祸」的反例，说明「拒绝动手」有时为何比「尽力修复」更安全。", "en": "The lesson covers a guard in apply(): if the DB \"has tables yet lacks a session table,\" opencode won't rashly build tables but errors out directly — because this very likely means OPENCODE_DB points at some other program's database. Discuss this \"for a DB of unknown origin, rather stop than meddle\" design philosophy: what engineering restraint does it embody? Then, from tools you've used (migration frameworks, build tools, config loaders), give a counterexample of \"a tool acting on its own initiative causing disaster,\" explaining why \"refuse to act\" is sometimes safer than \"try hard to fix.\""},
            {"zh": "课里说同一套表结构有两种等价表述：增量迁移链（历史视角，一笔笔怎么改过来的）和 schema.gen 完整快照（当下视角，现在长什么样），drizzle-kit 同时维护二者并保证一致。请你解释：为什么「新库用快照、老库用增量」这种双轨制是必要的？如果只保留增量链（新库也从头重放三十多个迁移）会有什么问题？如果只保留快照（丢掉历史迁移）又会有什么问题？这种「历史 vs 当下」的双重表述，在你熟悉的其他系统（如 git、事件溯源、Redux）里有没有类似的影子？", "en": "The lesson says the same table structure has two equivalent expressions: the incremental migration chain (historical view, how it was changed step by step) and the schema.gen full snapshot (present view, what it looks like now), both maintained by drizzle-kit and guaranteed consistent. Explain: why is this \"snapshot for new, increment for old\" dual track necessary? What problem arises if only the incremental chain is kept (new DBs also replay thirty-some migrations from scratch)? What problem if only the snapshot is kept (dropping historical migrations)? Does this \"history vs present\" dual expression have echoes in other systems you know (e.g. git, event sourcing, Redux)?"},
        ],
    },

    "47-provider-plugins.html": {
        "mcq": [
            {
                "q": {"zh": "opencode 要支持三十多家模型供应商（Anthropic/OpenAI/Groq/Bedrock…），它用的是什么架构？", "en": "To support thirty-some model providers (Anthropic/OpenAI/Groq/Bedrock…), what architecture does opencode use?"},
                "opts": [
                    {"zh": "插件架构——每家供应商是一个自包含插件文件（PluginV2.define），收进 ProviderPlugins 数组；新增供应商=加文件+加一行，核心零改动", "en": "A plugin architecture — each provider is a self-contained plugin file (PluginV2.define), gathered into the ProviderPlugins array; adding a provider = add a file + a line, zero core change"},
                    {"zh": "一个三十多分支的巨型 switch 语句", "en": "One giant switch statement with thirty-some branches"},
                    {"zh": "每家供应商一个独立的微服务", "en": "An independent microservice per provider"},
                    {"zh": "把所有供应商硬编码进 aisdk.ts", "en": "Hardcode all providers into aisdk.ts"},
                ],
                "answer": 0,
                "why": {"zh": "opencode 用插件架构：每家供应商是一个独立、自包含的插件文件（core/src/plugin/provider/anthropic.ts、openai.ts…），都是 PluginV2.define({ id, effect→钩子表 })。最小的 alibaba.ts 不到 20 行。三十多个插件收进 ProviderPlugins 数组。新增一家供应商=加一个插件文件 + 在数组里加一行，核心代码一行都不用动——这正是开闭原则（对扩展开放、对修改封闭）的活样子。对比「巨型 switch」：那种写法每加一家就要改核心，而插件架构把变化点（每家供应商）隔离进各自的文件，恒定的核心永不被触碰。", "en": "opencode uses a plugin architecture: each provider is an independent, self-contained plugin file (core/src/plugin/provider/anthropic.ts, openai.ts…), all PluginV2.define({ id, effect→hook table }). The smallest alibaba.ts is under 20 lines. Thirty-some plugins gathered into the ProviderPlugins array. Adding a provider = add a plugin file + a line in the array, not a single line of core changes — exactly the open-closed principle (open to extension, closed to modification) alive. Versus a \"giant switch\": that way edits the core per provider, while the plugin architecture isolates the variable point (each provider) into its own file, the constant core never touched."},
            },
            {
                "q": {"zh": "当 agent 需要某个模型时，核心 aisdk.ts 如何找到负责该供应商的插件？", "en": "When the agent needs a model, how does the core aisdk.ts find the plugin responsible for that provider?"},
                "opts": [
                    {"zh": "广播 + 自我认领——trigger \"aisdk.sdk\" 事件给所有插件，每个用 if (evt.package !== \"@ai-sdk/xxx\") return 自我判断，只有匹配的那个 createXxx 设 evt.sdk；核心零 if-else 区分供应商", "en": "Broadcast + self-claim — trigger an \"aisdk.sdk\" event to all plugins, each judges with if (evt.package !== \"@ai-sdk/xxx\") return, only the matching one's createXxx sets evt.sdk; core has zero if-else distinguishing providers"},
                    {"zh": "核心维护一张供应商→插件的查找表，直接索引", "en": "The core keeps a provider→plugin lookup table, indexes directly"},
                    {"zh": "遍历所有插件，调用每一个的 createXxx", "en": "Iterates all plugins, calls every one's createXxx"},
                    {"zh": "按字母顺序试，直到有一个不报错", "en": "Tries alphabetically until one doesn't error"},
                ],
                "answer": 0,
                "why": {"zh": "aisdk.ts 的 AISDK.language(model) 触发（trigger）一个 \"aisdk.sdk\" 事件，把 { model, package, options } 广播给所有插件。核心从头到尾没有一个 if-else 在区分供应商，它只是把事件抛出去；是各插件自己用 if (evt.package !== \"@ai-sdk/anthropic\") return 认领自己那一份，只有匹配的那个 import 对应包、调 createXxx(options)、设 evt.sdk。若广播一圈 evt.sdk 仍空就报 No AISDK provider plugin returned an SDK。这是控制反转（IoC）：传统是核心主动调每个供应商（核心依赖供应商），这里是核心定义「广播-认领」协议、供应商反过来挂进核心（供应商依赖核心）。依赖方向一反，加供应商从「改核心 switch」变成「写新插件挂上去」。", "en": "aisdk.ts's AISDK.language(model) triggers an \"aisdk.sdk\" event, broadcasting { model, package, options } to all plugins. The core has not one if-else distinguishing providers start to finish; it just throws the event out; each plugin claims its share with if (evt.package !== \"@ai-sdk/anthropic\") return, only the matching one imports its package, calls createXxx(options), sets evt.sdk. If after a full broadcast evt.sdk is still empty it reports No AISDK provider plugin returned an SDK. This is inversion of control (IoC): traditionally the core actively calls each provider (core depends on providers), here the core defines the \"broadcast-claim\" protocol and providers hook into the core in reverse (providers depend on core). Flip the dependency direction and adding a provider turns from \"editing the core switch\" into \"writing a new plugin and hooking it in.\""},
            },
            {
                "q": {"zh": "ProviderPlugins 数组最后一位的 DynamicProviderPlugin 起什么作用？", "en": "What role does DynamicProviderPlugin, last in the ProviderPlugins array, play?"},
                "opts": [
                    {"zh": "兜底——它的钩子第一行 if (evt.sdk) return，只在三十多个内置插件都没认领时出场：npm 临时装下未知包、import、找 create* 导出当工厂。三十多家快路径 + 一个万能兜底 = 支持任意供应商", "en": "Catch-all — its hook's first line if (evt.sdk) return, steps up only when all thirty-some built-ins failed to claim: npm-installs the unknown package, imports, finds a create* export as factory. Thirty-some fast path + one universal catch-all = supporting any provider"},
                    {"zh": "它负责管理所有内置供应商的生命周期", "en": "It manages the lifecycle of all built-in providers"},
                    {"zh": "它是默认供应商，没配置时用它", "en": "It's the default provider, used when none is configured"},
                    {"zh": "它缓存其他插件造好的 SDK", "en": "It caches SDKs built by other plugins"},
                ],
                "answer": 0,
                "why": {"zh": "DynamicProviderPlugin 永远排在 ProviderPlugins 数组最后一位，是「兜底接线员」。它的 aisdk.sdk 钩子第一行 if (evt.sdk) return——只要前面任何内置插件已认领（已设 evt.sdk），它就不插手；只有三十多个内置全没举手时才出场：把未知包用 npm 临时装下来（npm.add）、import 进来、找一个 create 开头的导出当工厂。这样内置三十多家是「快路径」（认死包名、无需联网），而 DynamicProviderPlugin 兜住「剩下所有家」——哪怕 opencode 从没听说过某供应商，只要它发布了符合 AI SDK 约定的 npm 包就能被动态接入。三十多明确支持 + 一个万能兜底 = 理论上支持任意供应商。这种「长列表 + 列表外兜底」的双保险，是成熟工具对接外部生态的从容。", "en": "DynamicProviderPlugin is forever last in the ProviderPlugins array, the \"catch-all operator.\" Its aisdk.sdk hook's first line if (evt.sdk) return — so long as any built-in before it claimed (set evt.sdk), it stays out; only when all thirty-some built-ins failed to raise a hand does it step up: npm-installs the unknown package (npm.add), imports it, finds an export starting with create as factory. So the thirty-some built-ins are the \"fast path\" (claim fixed package names, no network), while DynamicProviderPlugin catches \"all the rest\" — even if opencode never heard of some provider, as long as it published an npm package conforming to AI SDK conventions it can be dynamically connected. Thirty-some explicitly supported + one universal catch-all = any provider in theory. This \"long list + catch-all beyond the list\" double insurance is a mature tool's composure connecting to an external ecosystem."},
            },
        ],
        "open": [
            {"zh": "课里说核心 aisdk.ts 的解析代码最值得品的是它的「空」——通篇没有一个供应商的名字，只做「广播 aisdk.sdk 收 SDK、广播 aisdk.language 收语言模型、用 sdkKey 缓存」三件通用事，而「Anthropic 怎么造、Copilot 怎么路由」全在各自插件里。请你用「控制反转 / 依赖倒置 / 开闭原则」解释这种设计为什么能做到「加供应商不改核心」，并结合你写过的代码，谈谈一个「巨型 switch / if-else 链」在什么信号出现时，就该被重构成这种「广播 + 自我认领」的插件架构？这种重构的代价和风险又是什么？", "en": "The lesson says what's most worth savoring in core aisdk.ts's resolution code is its \"emptiness\" — not one provider name throughout, doing only three generic things (broadcast aisdk.sdk to collect SDK, broadcast aisdk.language to collect language model, cache with sdkKey), while \"how Anthropic builds, how Copilot routes\" lives entirely in each plugin. Explain with \"inversion of control / dependency inversion / open-closed principle\" why this design achieves \"add a provider without changing core,\" and from code you've written, discuss at what signal a \"giant switch / if-else chain\" should be refactored into this \"broadcast + self-claim\" plugin architecture? What are the costs and risks of such a refactor?"},
            {"zh": "课里揭示「插件是贯穿 opencode 的统一扩展范式」——boot.ts 里 agent（L45）、command、skill（L43）、config（L44）全是以插件形式注册的，provider 只是其中一类。同时课里给了 Anthropic（catalog.transform 加 beta 头）和 Copilot（aisdk.language 选 Responses/Chat 端点）两个「重」插件例子，说明插件不只是造 SDK 的工厂，更是「容纳每家供应商怪癖的容器」。请你谈谈：把每家的特殊处理（AWS 签名、beta 头、端点路由…）封进各自插件、绝不外溢到核心，对一个长期演进的项目意味着什么？当某个「怪癖」开始被多家供应商共享时，你会如何在「保持插件自包含」和「避免重复」之间权衡？", "en": "The lesson reveals \"plugin is the unified extension paradigm running through opencode\" — in boot.ts agent (L45), command, skill (L43), config (L44) are all registered as plugins, provider just one kind. It also gives two \"heavy\" plugin examples, Anthropic (catalog.transform adds beta headers) and Copilot (aisdk.language picks Responses/Chat endpoint), showing plugins aren't just SDK-building factories but \"containers holding each provider's quirks.\" Discuss: what does sealing each provider's special handling (AWS signing, beta headers, endpoint routing…) into its own plugin, never spilling to core, mean for a long-evolving project? When some \"quirk\" starts being shared by multiple providers, how would you weigh between \"keeping plugins self-contained\" and \"avoiding duplication\"?"},
        ],
    },

    "46-mcp.html": {
        "mcq": [
            {
                "q": {"zh": "MCP 工具和 opencode 内置工具（read/bash 等）最本质的关系是什么？", "en": "What is the most essential relationship between MCP tools and opencode's built-in tools (read/bash etc.)?"},
                "opts": [
                    {"zh": "「出身二等、待遇一等」——MCP 工具运行时才从外部服务器发现，但一旦进门就并入同一注册表、走同一道权限闸门（L41）、被同一批插件钩子观察，对模型/会话/权限系统而言和内置工具长得完全一样", "en": "\"Second-class origin, first-class treatment\" — MCP tools are discovered from an external server at runtime, but once in the door they merge into the same registry, go through the same permission gate (L41), are observed by the same plugin hooks; to the model/session/permission system they look identical to built-ins"},
                    {"zh": "MCP 工具绕过权限系统、可以直接执行", "en": "MCP tools bypass the permission system and execute directly"},
                    {"zh": "MCP 工具和内置工具用两套完全独立的注册表与权限", "en": "MCP tools and built-ins use two wholly separate registries and permissions"},
                    {"zh": "MCP 工具其实就是内置工具的别名", "en": "MCP tools are really just aliases of built-in tools"},
                ],
                "answer": 0,
                "why": {"zh": "内置工具编译期写死、数量固定；MCP 工具运行时从外部服务器经 listTools「问」来，由 catalog.ts 的 convertTool 裹进 AI SDK 的 dynamicTool（execute 只是转发给 client.callTool）。但裹好后，它们并入同一个工具注册表（L37）、在 session/tools.ts 走同一道权限闸门 ctx.ask（L41 Ruleset 的 allow/ask/deny 三态）、被同一批插件钩子（tool.execute.before/after）观察。对模型、会话循环、权限系统而言，一个 MCP 工具和一个内置 read 完全一样——唯一差别藏在 execute 最深处：内置跑本地代码，MCP 把调用转发给远端/本地服务器。这就是「出身二等、待遇一等」：系统不为外来工具开任何后门，它必须和原生工具走完全相同的安全检查——这种「不为扩展点破例」的纪律，正是权限系统可信的根基。", "en": "Built-ins are hardcoded at compile time, fixed in number; MCP tools are \"asked\" from an external server at runtime via listTools, wrapped by catalog.ts's convertTool into the AI SDK's dynamicTool (execute just forwards to client.callTool). But once wrapped, they merge into the same tool registry (L37), go through the same permission gate ctx.ask in session/tools.ts (L41 Ruleset's allow/ask/deny tri-state), are observed by the same plugin hooks (tool.execute.before/after). To the model, session loop, permission system, an MCP tool and a built-in read are identical — the only difference hides deep in execute: built-ins run local code, MCP forwards the call to a remote/local server. That's \"second-class origin, first-class treatment\": the system opens no backdoor for foreign tools; they must pass the exact same security check as native tools — this \"no exception for extension points\" discipline is the foundation of a trustworthy permission system."},
            },
            {
                "q": {"zh": "多台 MCP 服务器可能各有一个叫 search 的工具，opencode 如何避免冲突、又让工具名能被权限规则精确管控？", "en": "Multiple MCP servers might each have a tool named search; how does opencode avoid collision while letting the tool name be precisely governed by permission rules?"},
                "opts": [
                    {"zh": "工具名 = sanitize(服务器名)+\"_\"+sanitize(工具名)（如 github_search、jira_search），这个带前缀的作用域名同时就是 session/tools.ts 里的权限 key", "en": "tool name = sanitize(serverName)+\"_\"+sanitize(toolName) (e.g. github_search, jira_search); this prefixed scoped name is also the permission key in session/tools.ts"},
                    {"zh": "谁先连上谁用 search，后连的报错", "en": "Whoever connects first gets search, later ones error"},
                    {"zh": "随机给工具编号", "en": "Randomly number the tools"},
                    {"zh": "把所有 search 合并成一个", "en": "Merge all searches into one"},
                ],
                "answer": 0,
                "why": {"zh": "opencode 给每个工具名冠上服务器名前缀：先 sanitize（把非 [a-zA-Z0-9_-] 的字符替换成 _）洗一遍名字，再用 _ 拼成 sanitize(服务器名)+\"_\"+sanitize(工具名)。于是 github 的 search → github_search、jira 的 search → jira_search，互不冲突。这串带前缀的「作用域名」最妙的去处在 session/tools.ts：MCP 工具并入会话工具集时，权限闸门写 ctx.ask({ permission: key })——这个 key 正是作用域名。所以你能在配置里写「github_* 一律放行、jira_delete_* 必须问」，精确管控每台外部服务器、每个外部工具。命名既解决重名，又直接成为权限系统的抓手。", "en": "opencode prefixes each tool name with the server name: first sanitize (replace non-[a-zA-Z0-9_-] chars with _) washes the name, then joins with _ into sanitize(serverName)+\"_\"+sanitize(toolName). So github's search → github_search, jira's search → jira_search, no collision. This prefixed \"scoped name\"'s finest destination is session/tools.ts: when MCP tools merge into the session tool set, the permission gate writes ctx.ask({ permission: key }) — this key is exactly the scoped name. So you can write in config \"github_* all allowed, jira_delete_* must ask,\" precisely governing each external server and tool. Naming both solves collisions and directly becomes the permission system's handle."},
            },
            {
                "q": {"zh": "MCP 配置里 local 和 remote 两种服务器，连接方式有何不同？连上之后呢？", "en": "In MCP config, how do local and remote servers differ in connection? And after connecting?"},
                "opts": [
                    {"zh": "local 用 StdioClientTransport 拉子进程（command）、remote 用 HTTP（先 StreamableHTTP 失败回退 SSE）；但连上后都得到同一个 MCP Client，listTools/callTool 代码完全一致", "en": "local uses StdioClientTransport to spawn a child process (command), remote uses HTTP (StreamableHTTP first, falling back to SSE); but once connected both yield the same MCP Client, listTools/callTool code is identical"},
                    {"zh": "local 和 remote 连上后用两套完全不同的 API", "en": "local and remote use two wholly different APIs after connecting"},
                    {"zh": "remote 只能用 SSE、local 只能用 WebSocket", "en": "remote can only use SSE, local only WebSocket"},
                    {"zh": "两者都必须先 OAuth 才能连", "en": "Both must OAuth before connecting"},
                ],
                "answer": 0,
                "why": {"zh": "config/mcp.ts 按 type 分两种：local（type:\"local\"，给 command；opencode 用 StdioClientTransport 把它当子进程拉起来，经 stdio 通信；可配 cwd/environment）、remote（type:\"remote\"，给 url；经 HTTP 连，先试 StreamableHTTP、失败回退 SSE；可配 headers/oauth）。但两种 transport 殊途同归：连上后都得到同一个 MCP Client，后续 listTools、callTool 完全一样——传输层差异被 MCP SDK 的 transport 抽象吃掉了。这是「把『怎么连』和『连上后怎么用』干净切开」。那个 StreamableHTTP→SSE 回退也有讲究：优先用更新更高效的，连不上才退到更老更通用的，既吃新协议好处、又不拒绝只支持老协议的服务器——「优先用更好的，但永远留一条兼容退路」。", "en": "config/mcp.ts splits two by type: local (type:\"local\", given command; opencode spawns it as a child process via StdioClientTransport, communicating over stdio; can set cwd/environment), remote (type:\"remote\", given url; connects over HTTP, trying StreamableHTTP first, falling back to SSE; can set headers/oauth). But the two transports converge: once connected both yield the same MCP Client, subsequent listTools, callTool identical — the transport-layer difference is absorbed by the MCP SDK's transport abstraction. This \"cleanly separates 'how to connect' from 'how to use once connected.'\" That StreamableHTTP→SSE fallback is deliberate too: prefer the newer, more efficient one, retreat to the older, more universal only if it can't connect — getting the new protocol's benefits without rejecting servers that only speak the old. \"Prefer the better, but always keep a compatible fallback.\""},
            },
        ],
        "open": [
            {"zh": "课里把 OAuth 认证形容成一段「浏览器回调舞蹈」：起 localhost 回调服务器→开浏览器授权（带 PKCE 的 code_challenge + state 防 CSRF）→截获 code→换令牌→存 mcp-auth.json（0o600 + 文件锁）。请你逐步解释：为什么需要 PKCE 的 codeVerifier 和随机 state 这两样东西？它们各防住了什么攻击？再谈谈把令牌存成 0o600 权限、用文件锁串行读写，分别在防范什么——一个处理敏感凭证的本地系统，还应该考虑哪些你想到的安全隐患？", "en": "The lesson describes OAuth as a \"browser callback dance\": start localhost callback server → open browser authorize (with PKCE code_challenge + state for CSRF) → capture code → exchange tokens → save mcp-auth.json (0o600 + file lock). Explain step by step: why are PKCE's codeVerifier and the random state both needed? What attack does each prevent? Then discuss what storing tokens at 0o600 and serializing read/write with a file lock each guard against — for a local system handling sensitive credentials, what other security risks can you think of that it should consider?"},
            {"zh": "课里反复强调一个全书主题——「便宜地广而告之，按需地昂贵兑现」：MCP 连上只廉价地拉一份工具清单（名字+schema+描述），真正昂贵的执行要等模型实际点名才经 callTool 转发。请你把这个原则和 L37 注册表（只存定义、用时 settle）、L42 预览/溢出、L43 skills（只报名字、body 按需加载）串起来，提炼这种「先报名、后兑现」的惰性设计的共同价值（省 token、省启动、省资源），并谈谈它的代价——当「广告」和「真实能力」脱节（服务器报了工具却调用失败）时，会带来什么麻烦？该如何缓解？", "en": "The lesson repeatedly stresses a book-wide theme — \"advertise cheap, fulfill expensively on demand\": MCP connect only cheaply pulls a tool list (name+schema+description); the truly expensive execution waits until the model actually calls by name, forwarded via callTool. Connect this principle with L37's registry (stores only definitions, settles on use), L42's preview/spill, L43's skills (report only names, body loaded on demand), distill the shared value of this \"advertise first, fulfill later\" lazy design (save tokens, save startup, save resources), and discuss its cost — when \"advertisement\" and \"real capability\" decouple (server reports a tool but the call fails), what trouble arises? How to mitigate?"},
        ],
    },

    "45-agents.html": {
        "mcq": [
            {
                "q": {"zh": "在 opencode 里，一个「agent」本质上是什么？", "en": "In opencode, what is an \"agent\" essentially?"},
                "opts": [
                    {"zh": "一束「角色配置」（AgentV2.Info）——把 model（大脑）+ system（说明书）+ permissions（许可）+ mode/steps（怎么跑）打包并起个名；agent 是可声明、可配置、用户可随意定制的数据", "en": "A bundle of \"role config\" (AgentV2.Info) — packaging model (brain) + system (instructions) + permissions (permit) + mode/steps (how it runs) and naming it; an agent is declarable, configurable, user-customizable data"},
                    {"zh": "一个必须写代码 new 出来的神秘智能对象", "en": "A mysterious intelligence object you must write code to new up"},
                    {"zh": "一段固定的、不可配置的内置逻辑", "en": "A fixed, non-configurable piece of built-in logic"},
                    {"zh": "仅仅是一个模型名字符串", "en": "Just a model-name string"},
                ],
                "answer": 0,
                "why": {"zh": "AgentV2.Info（core/src/agent.ts）就是「一个 agent」的定义，干净得像张角色卡：model（这角色的大脑）、system（这角色的工作说明书）、permissions（L41 的 Ruleset 许可）、mode（subagent/primary/all）、steps（步数上限，呼应 L20）、description/color/hidden。看懂这张卡，agent 就不神秘了：它不是神秘智能而是「一份配置」。这种「把复杂收敛成配置」的好处是：agent 不是必须写代码 new 出来的对象，而是可声明、可配置、用户可随意定制的数据——想要个「写测试的 agent」「做安全审查的 agent」，不用改 opencode 源码一行，往配置里加一张角色卡即可。默认 agent 的 ID 是「build」。", "en": "AgentV2.Info (core/src/agent.ts) is the definition of \"an agent,\" clean as a role card: model (this role's brain), system (its job description), permissions (L41's Ruleset permit), mode (subagent/primary/all), steps (step cap, echoing L20), description/color/hidden. See this card and an agent stops being mystical: it's not mysterious intelligence but \"a config.\" The benefit of \"reducing the complex to config\": an agent isn't an object you must write code to new up, but declarable, configurable, user-customizable data — want a \"test-writing agent\" or \"security-review agent\"? No source change needed, just add a role card to config. The default agent's ID is \"build\"."},
            },
            {
                "q": {"zh": "内置的 build 与 plan 两个 agent，最本质的区别在哪里？", "en": "What is the most essential difference between the built-in build and plan agents?"},
                "opts": [
                    {"zh": "几乎只在「权限画像」——同一套 agent 机制、同一模型与工具，plan 在默认权限上叠了 edit:{\"*\":\"deny\"}（仅放行写 plans/*.md），把同一引擎活成「只读规划者」", "en": "Almost only the \"permission profile\" — same agent machinery, same model and tools; plan layers edit:{\"*\":\"deny\"} (allowing only writing plans/*.md) on default permissions, making the same engine live as a \"read-only planner\""},
                    {"zh": "用了完全不同的两套引擎和模型", "en": "They use two wholly different engines and models"},
                    {"zh": "plan 用更快的模型、build 用更慢的", "en": "plan uses a faster model, build a slower one"},
                    {"zh": "build 能读文件、plan 不能读文件", "en": "build can read files, plan cannot read files"},
                ],
                "answer": 0,
                "why": {"zh": "build 与 plan 共用同一套 agent 引擎、同一批工具、（默认）同一模型——几乎一切都一样，唯一实质区别就是那份「权限画像」。build=默认全能编码 agent（能改文件、跑命令）；plan=「Plan mode. Disallows all edit tools.」，定义本质是在默认权限上叠：edit:{\"*\":\"deny\", \".opencode/plans/*.md\":\"allow\"}（拒绝一切编辑，只放行写计划文件）+ task.general:deny + plan_exit:allow。这把 L41 权限和本课 agent 焊在一起：agent 抽象之所以强，正因「角色差异」能大幅归结为「权限差异」——换一套更严的徽章，同一引擎自动变成「只看不改」的规划者。这是极简的力量：把「这个 agent 能做什么」做成可声明的数据（权限规则），而非写死的代码。", "en": "build and plan share the same agent engine, same tools, (default) same model — nearly everything is the same, the only substantive difference is that \"permission profile.\" build = default all-around coding agent (can edit files, run commands); plan = \"Plan mode. Disallows all edit tools,\" essentially layering on default permissions: edit:{\"*\":\"deny\", \".opencode/plans/*.md\":\"allow\"} (deny all edits, allow only writing plan files) + task.general:deny + plan_exit:allow. This welds L41's permissions to this lesson's agent: the agent abstraction is powerful precisely because \"role differences\" largely reduce to \"permission differences\" — swap a stricter badge, the same engine becomes a \"look-don't-change\" planner. A minimalist power: make \"what this agent can do\" declarable data (permission rules), not hardcoded code."},
            },
            {
                "q": {"zh": "agent 的 mode 字段（subagent/primary/all）决定了什么？", "en": "What does an agent's mode field (subagent/primary/all) decide?"},
                "opts": [
                    {"zh": "它能在哪里「出场」——primary 可作直接对话的主 agent，subagent 只能被别的 agent 派为子任务（呼应 L18 FiberSet），all 两者皆可", "en": "Where it can \"appear\" — primary can be a directly-conversed primary agent, subagent can only be dispatched as a subtask by others (echoing L18 FiberSet), all means both"},
                    {"zh": "它用哪个模型", "en": "Which model it uses"},
                    {"zh": "它的 UI 颜色", "en": "Its UI color"},
                    {"zh": "它能跑多少步", "en": "How many steps it can run"},
                ],
                "answer": 0,
                "why": {"zh": "mode 决定 agent 在哪里出场：primary（可作你直接对话的主 agent，如 build/plan）、subagent（只能被别的 agent 派为子任务，回想 L18 用 FiberSet 派子任务的 explore）、all（两者皆可——既能作主、也能被派为子）。这也解释了配置里的 agents 格：用户能在配置里定义自己的 agent，「造个新角色」就是「往配置加这样一张卡」。注意核心 AgentV2.Info（已解析的 agent）字段多是「必填带默认」的（mode、permissions 有定值），而配置侧 ConfigAgent.Info 字段几乎全可选——因为配置只表达「我想覆盖什么」，没写的走默认，这又是 L44「层叠覆盖」在 agent 上的落地。plan_enter/plan_exit 是在两个模式间互转的权限动作。", "en": "mode decides where an agent appears: primary (can be a directly-conversed primary agent, like build/plan), subagent (only dispatchable as a subtask by others, recall L18's explore dispatched via FiberSet), all (both — can be primary or dispatched as a sub). This also explains the config's agents cell: the user can define their own agents in config, so \"make a new role\" = \"add such a card to config.\" Note the core AgentV2.Info (resolved agent) fields are mostly \"required-with-default\" (mode, permissions have set values), while config-side ConfigAgent.Info fields are almost all optional — because config only expresses \"what I want to override,\" unwritten ones default; again L44's \"cascade override\" landing on agents. plan_enter/plan_exit are permission actions interconverting the two modes."},
            },
        ],
        "open": [
            {"zh": "课里反复强调 build 与 plan「同一套机制、两张徽章」——唯一实质区别在权限画像。请你提炼这种「把角色差异归结为权限差异」的设计的威力与代价：它让「造一个受限新角色」轻到只需写几条 deny 规则（如 plan 的 edit:\"*\":\"deny\"），从而把「先规划、再执行」这种人类协作的工作流原生焊进产品。但当角色越来越多、权限规则越叠越深，会带来什么新的复杂度？你会怎样设计才能既享受这种声明式的轻便、又不让权限画像变成一团难以推理的乱麻？", "en": "The lesson repeatedly stresses build and plan are \"same machinery, two badges\" — the only substantive difference is the permission profile. Distill the power and cost of this \"reduce role differences to permission differences\" design: it makes \"making a restricted new role\" as light as writing a few deny rules (like plan's edit:\"*\":\"deny\"), welding the human \"plan first, execute later\" workflow natively into the product. But as roles multiply and permission rules stack deeper, what new complexity arises? How would you design to enjoy this declarative lightness yet keep the permission profile from becoming an un-reasonable-about tangle?"},
            {"zh": "课里指出 opencode 把一批专用内置 agent（explore/compaction/summary/title）的 prompt 外置成了 agent/prompt/*.txt 文件，并说「agent 的『工作说明书』理应像文档一样对待，而非像代码一样编译」。请你结合你做过的 prompt 工程，谈谈把 prompt 当「会被反复打磨的文案」从代码里抽出来、放进纯文本/独立文件管理，带来了哪些实际好处（可读、可改、非程序员可调、改一句话不必重编译）？又有什么隐患（与代码逻辑脱节、版本漂移、缺少类型/测试保护）？一个成熟系统该如何管理这些「会演化的 prompt 资产」？", "en": "The lesson notes opencode externalizes a batch of dedicated internal agents' (explore/compaction/summary/title) prompts into agent/prompt/*.txt files, saying \"an agent's 'job description' deserves to be treated like a document, not compiled like code.\" From your prompt-engineering experience, discuss the practical benefits of pulling prompts — as \"copy that gets refined repeatedly\" — out of code into plain-text/separate files (readable, changeable, non-programmer-tunable, change a sentence without recompiling). What are the pitfalls (decoupling from code logic, version drift, lack of type/test protection)? How should a mature system manage these \"evolving prompt assets\"?"},
        ],
    },

    "44-config-loading.html": {
        "mcq": [
            {
                "q": {"zh": "opencode 的 Config.Info 在系统里扮演什么角色？", "en": "What role does opencode's Config.Info play in the system?"},
                "opts": [
                    {"zh": "一个类型化 Schema 的「接线总成」——把全系统几乎所有用户可调项（model/agents/permissions/mcp/tool_output/skills…）汇到一处；加载即校验", "en": "A typed-Schema \"wiring harness\" — gathering nearly all the system's user-tunable items (model/agents/permissions/mcp/tool_output/skills…) in one place; loading = validation"},
                    {"zh": "只存一个 model 字段", "en": "Stores only a model field"},
                    {"zh": "运行时才组装、没有 schema", "en": "Assembled at runtime, no schema"},
                    {"zh": "每个子系统各自一份独立配置文件", "en": "Each subsystem has its own separate config file"},
                ],
                "answer": 0,
                "why": {"zh": "Config.Info（config.ts）是用 Effect Schema 定义的大类，几乎汇集 opencode 所有子系统的旋钮：model/shell、agents（L45）、permissions（L41 Ruleset）、mcp（L46）、tool_output（L42）、skills（L43）、instructions/commands/lsp…。它是类型化的，所以加载时就校验（写错字段/类型在解析关被挡下，schema 即契约）。「一处声明、各取所需」：用户只在一处声明，每个子系统从同一份 Config.Info 取自己那格——好写、好校验、好演进（加可调项=加字段）。", "en": "Config.Info (config.ts) is a big class defined with Effect Schema, gathering nearly all of opencode's subsystem knobs: model/shell, agents (L45), permissions (L41 Ruleset), mcp (L46), tool_output (L42), skills (L43), instructions/commands/lsp…. It's typed, so it's validated at load (a wrong field/type stopped at the parse gate, schema is contract). \"Declare in one place, each takes what it needs\": the user declares in one spot, each subsystem takes its cell from this same Config.Info — easy to write, validate, evolve (adding a tunable = adding a field)."},
            },
            {
                "q": {"zh": "当全局配置和某个子目录配置对同一项（如 model）给了不同值，最终用哪个？为什么？", "en": "When global config and some subdirectory config give different values for the same item (e.g. model), which wins, and why?"},
                "opts": [
                    {"zh": "子目录配置（更靠近打开的目录）胜出——「越靠近所打开目录的配置越优先」，因为它对应更具体的意图，特异应压过宽泛默认", "en": "The subdirectory config (closer to the opened dir) wins — \"config closer to the opened dir wins,\" because it maps to more specific intent, specific should override broad default"},
                    {"zh": "全局配置永远胜出", "en": "Global config always wins"},
                    {"zh": "随机选一个", "en": "Picks one at random"},
                    {"zh": "报冲突错误、拒绝加载", "en": "Errors on conflict, refuses to load"},
                ],
                "answer": 0,
                "why": {"zh": "源码铁律：「A config closer to the opened directory should win over one higher up」。优先级低→高：全局默认 < 项目根 < 更靠近 cwd 的特例。为什么越近越优先？因为它对应人的意图的「特异性」——全局写的是「我大体喜欢这样」的宽泛默认，子目录专门写的是「就这块儿我要特别这样」的明确意图；特异理应压过宽泛，否则专门为某角落写的设置反被全局默认盖掉就荒谬了。配置被排成 Entry[] 低→高，便于就近覆盖。", "en": "The source iron law: \"A config closer to the opened directory should win over one higher up.\" Priority low→high: global default < project root < closer-to-cwd exception. Why closer wins? Because it maps to intent specificity — the global is \"I generally like this\" broad default, the subdir specifically is \"right here I want it specially\" explicit intent; specific should override broad, else a setting written for a corner being covered by a global default would be absurd. Config is sorted into Entry[] low→high for closer-overrides."},
            },
            {
                "q": {"zh": "latest(entries, key) 怎么得到某个设置的最终生效值？这种「保留有序来源、按 key 当场裁决」相比「急着深合并成一个大对象」好在哪？", "en": "How does latest(entries, key) get a setting's final effective value, and how is \"keep ordered sources, adjudicate per-key on the spot\" better than \"eagerly deep-merge into one big object\"?"},
                "opts": [
                    {"zh": "filter 出 Document 再 findLast 有定义的（=最高优先级）；保留有序来源让每项「从哪来、为何是这值」始终可追溯，配置出问题不会「来源成谜」", "en": "filter Documents then findLast with a definition (=highest priority); keeping ordered sources keeps each item's \"where from, why this value\" always traceable, config trouble never \"source is a mystery\""},
                    {"zh": "把所有配置随机打乱再取第一个", "en": "Shuffles all configs and takes the first"},
                    {"zh": "只读全局配置", "en": "Reads only global config"},
                    {"zh": "深合并更快所以更好", "en": "Deep-merge is faster so better"},
                ],
                "answer": 0,
                "why": {"zh": "latest 逻辑：filter 出 type==document 的 Entry → map 取该 key → findLast(≠undefined)。因 entries 是低→高排的，findLast 取最高优先级里有定义的那项——逐项 last-wins。和第 41 课权限 evaluate 用同一个 findLast。不预算合成结果、而把来源按优先级留着按 key 当场裁决：每项「从哪份配置来、为何是这值」清清楚楚可追溯，排查「这 model 怎么是这个」顺着优先级一层层看即可，不会迷失在早已揉成一团、来源难辨的大对象里。把『有哪些来源』和『某项最终取谁』分开=可解释性的根基。", "en": "latest logic: filter Entries with type==document → map the key → findLast(≠undefined). Because entries are low→high, findLast takes the highest-priority one with a definition — per-item last-wins. Same findLast as lesson 41's permission evaluate. It doesn't pre-compute a merged result but keeps sources by priority and adjudicates per-key on the spot: each item's \"which config it came from, why this value\" stays clear and traceable; to debug \"why is this model this,\" look layer by layer down priority, never lost in a long-mashed, source-obscured big object. Separating \"which sources exist\" from \"which one an item finally takes\" = the foundation of explainability."},
            },
        ],
        "open": [
            {"zh": "课里把 opencode 的配置层叠（全局默认 < 项目 < 更靠近 cwd）和 CSS cascade、.gitconfig（system<global<local）、editorconfig 等归为同一类「分层就近覆盖」机制。请你提炼这类机制的共同结构（多个有序来源、就近/就具体者覆盖、按项取值），并谈谈它为什么比「单一全局配置」或「每处独立配置」都更好用。它的代价（心智负担、来源排查）又在哪？", "en": "The lesson groups opencode's config cascade (global default < project < closer-to-cwd) with CSS cascade, .gitconfig (system<global<local), editorconfig as the same \"layered closer-overrides\" mechanism. Distill this class's common structure (multiple ordered sources, closer/more-specific overrides, per-item resolution), and discuss why it beats both \"a single global config\" and \"independent config everywhere.\" What's its cost (cognitive load, source debugging)?"},
            {"zh": "课里强调这套配置系统的「可解释性」：保留有序来源、按 key 当场裁决，让每一项的来源始终可追，避免「来源成谜」。请结合你维护过的配置系统（如环境变量层叠、k8s 多层 values、构建工具配置），谈谈「配置来源难追溯」给你造成过什么麻烦？一个系统该如何设计，才能在合并多来源配置的同时，仍让人随时回答「这个值到底从哪来」？", "en": "The lesson stresses this config system's \"explainability\": keeping ordered sources and adjudicating per-key keeps each item's source always traceable, avoiding \"source is a mystery.\" From config systems you've maintained (env-var layering, k8s multi-layer values, build-tool config), discuss what trouble \"config source hard to trace\" caused you. How should a system be designed so that, while merging multi-source config, it still lets you answer \"where exactly does this value come from\" anytime?"},
        ],
    },

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
                "why": {"zh": "按 key 精确排队：例如以文件路径为 key（file-mutation.ts），对同一文件的并发改动串成一条线、不打架，不同文件照样满速并行——既保正确又不牺牲并发。（注意：会话级的「同一时刻一路 drain」是 run-coordinator 干的，不是 KeyedMutex，但二者都是「按 key 排队」这同一思路。）", "en": "Precise per-key queuing: e.g. with the file path as key (file-mutation.ts), concurrent edits to one file are serialized and won't clash, while different files run at full concurrency — correctness without sacrificing parallelism. (Note: per-session «one drain at a time» is done by run-coordinator, not KeyedMutex, though both use the same «queue by key» idea.)"},
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
                "why": {"zh": "核心是一行 OpenApi.fromApi(PublicApi)：把结构化的 API 类型读成标准 OpenAPI 规范；opencode generate 加料+格式化；@hey-api 照规范印出 types/sdk/client 三个文件。全程没有手写。", "en": "The core is one line, OpenApi.fromApi(PublicApi): read the structured API types into a standard OpenAPI spec; the `generate` command adds extras and formats it; @hey-api prints types/sdk/client from the spec. None hand-written."},
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
                    {"zh": "写端用 append-only 事件（底账），读端用投影出的消息表 SessionMessageTable（报表）", "en": "Write end uses append-only events (ledger); read end uses the projected SessionMessageTable (statement)"},
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
            {"zh": "课里说安全护栏的艺术「不在有没有，而在卡在哪个值」——MAX_STEPS 太小掐断复杂任务、太大失控代价可怕，而 25 这个具体数字源码注释自己都打了问号（「它合理吗？」）。如果让你为一个会动用户文件的 agent 选这个上限，你会考虑哪些因素？又该如何验证它选得合不合适？", "en": "The lesson says a guardrail's art is \"not whether but at what value\" — too-small MAX_STEPS cuts off complex tasks, too-large makes runaway costs frightening, and the source comment itself question-marks the exact 25 (\"Does it make sense?\"). If you set this cap for an agent that touches user files, what factors would you weigh, and how would you validate the choice?"},
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
                "q": {"zh": "为什么说一个 Route 是由几个「正交件」拼出来的？这对新增供应商意味着什么？", "en": "Why is a Route said to be assembled from a few \"orthogonal pieces\"? What does this mean for adding a provider?"},
                "opts": [
                    {"zh": "Route.make 注释明言由四个正交件 protocol/endpoint/auth/framing 加一个 id 组成（transport 是 framing 维在非 HTTP 时的替换）；新增一家常常只是「给这几件挑一组取值」，复用本质是「只换一两件」", "en": "Route.make\u2019s comment states four orthogonal pieces protocol/endpoint/auth/framing plus an id (transport is framing\u2019s alternative for non-HTTP); adding one is often just \"pick a set of values for these pieces,\" reuse is essentially \"swap one or two pieces\""},
                    {"zh": "Route 是铁板一块，新增供应商要从头重写", "en": "Route is monolithic; adding a provider means rewriting from scratch"},
                    {"zh": "这几件必须一起改，不能单独动", "en": "All the pieces must change together, none alone"},
                    {"zh": "旋钮越多说明设计越糟", "en": "More knobs means worse design"},
                ],
                "answer": 0,
                "why": {"zh": "源码 Route.make 注释明言「four orthogonal pieces」=protocol/endpoint/auth/framing，加一个 id，各管一维、可独立替换，组合空间却覆盖所有现实供应商。这把前几课的「魔法」全祛魅了：OpenAI 兼容=拨 protocol 到 openai-chat+改 endpoint；Bedrock=把 framing 从 SSE 拨到二进制；Responses WS=以 transport 顶替 framing 走 WS（transport 与 framing 是同一维两种写法，二者传其一）。每个聪明复用都是「只换一两件、其余照旧」。而类型参数 Frame 在 framing↔protocol 接缝强制对齐——正交但不放任，自由组合+类型兜底。", "en": "The source Route.make comment states \"four orthogonal pieces\" = protocol/endpoint/auth/framing, plus an id, each owning one dimension, independently swappable, yet the combination space covers all real providers. This demystifies prior lessons' \"magic\": OpenAI-compatible = turn protocol to openai-chat + change endpoint; Bedrock = turn framing from SSE to binary; Responses WS = supply transport in place of framing for WS (transport and framing are two spellings of one axis, you pass one xor the other). Each clever reuse is \"swap one or two pieces, leave the rest.\" And the type parameter Frame forces framing↔protocol alignment at the seam — orthogonal but not lawless, free composition + type backstop."},
            },
        ],
        "open": [
            {"zh": "课里把 OpenAI Responses 同时支持 HTTP 与 WebSocket，解释为「哪种传输划算就用哪种，并把选择做成一个可拨动的旋钮」，而不是「为了时髦上 WebSocket」。结合 HTTP（无状态、省心、universal）与 WebSocket（双向、实时、但要管连接保活/重连）的权衡，谈谈你会在什么场景选 WebSocket、什么场景坚持 HTTP？把传输做成「旋钮」而非写死，给未来留下了什么样的余地？", "en": "The lesson explains OpenAI Responses supporting both HTTP and WebSocket as \"use whichever transport is worthwhile, making the choice a turnable knob,\" not \"adopt WebSocket to be trendy.\" Weighing HTTP (stateless, carefree, universal) against WebSocket (bidirectional, real-time, but must manage keepalive/reconnect), discuss when you'd choose WebSocket and when you'd stick with HTTP. Making transport a \"knob\" rather than hardcoded leaves what headroom for the future?"},
            {"zh": "课里强调「正交不等于放任」：这几个正交件能自由组合，但类型参数 Frame 在 framing 和 protocol 的接缝处强制对齐（SSE 切出 string 帧，配它的 protocol.stream.event 就得是 Codec<Event, string>）。请谈谈「用类型系统在模块接缝处设防」相比「靠文档约定/代码评审来防止错配」的优势；你能想到自己项目里哪个接缝，也值得用类型（而非口头约定）来强制对齐？", "en": "The lesson stresses \"orthogonal doesn't mean lawless\": the orthogonal pieces combine freely, but the type parameter Frame forces alignment at the framing/protocol seam (SSE cuts string frames, so its protocol.stream.event must be Codec<Event, string>). Discuss the advantage of \"guarding a module seam with the type system\" over \"preventing mismatches via documentation/code review.\" Which seam in your own project also deserves type-enforced (not verbal) alignment?"},
        ],
    },
    "34-streaming-cache.html": {
        "mcq": [
            {
                "q": {"zh": "LLMEvent（schema/events.ts，16 个成员）在整套设计里扮演什么角色？", "en": "What role does LLMEvent (schema/events.ts, 16 members) play in the whole design?"},
                "opts": [
                    {"zh": "反腐层的「入站」规范词汇——六种协议的 stream.step 都把各自方言翻译成它，agent 循环只消费它，补全第 28 课「翻译墙」的回来一面", "en": "The anti-corruption layer's \"inbound\" canonical vocabulary — all six protocols' stream.step translate their dialect into it, the agent loop consumes only it, completing the inbound face of lesson 28's \"translation wall\""},
                    {"zh": "只是 Anthropic 协议的内部事件类型", "en": "Just Anthropic's internal event type"},
                    {"zh": "用于 UI 渲染的前端数据结构", "en": "A frontend data structure for UI rendering"},
                    {"zh": "数据库里存事件日志的表", "en": "A DB table storing event logs"},
                ],
                "answer": 0,
                "why": {"zh": "第 28 课的反腐层有一进一出：出去 LLMRequest、回来 LLMEvent 流。LLMEvent 是六种协议的「最大公约数」——Anthropic content_block_delta、OpenAI choices[].delta、Gemini part、Bedrock 二进制帧，都被 stream.step 翻译成这同一套 16 种事件。于是 agent 循环（L17）只认这 16 种就能驱动任何模型，新增第七家供应商它一行不改。", "en": "Lesson 28's anti-corruption layer has an out and a back: out LLMRequest, back the LLMEvent stream. LLMEvent is the six protocols' \"greatest common divisor\" — Anthropic's content_block_delta, OpenAI's choices[].delta, Gemini's parts, Bedrock's binary frames, all translated by stream.step into this same 16-event set. So the agent loop (L17) drives any model knowing only these 16, and adding a seventh provider changes not a line of it."},
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
    "35-model-resolution.html": {
        "mcq": [
            {
                "q": {"zh": "为什么 opencode 不把「某模型支持多大上下文、输入输出多少钱」写死在代码里，而去拉取 models.dev？", "en": "Why doesn't opencode hardcode \"a model's context size, input/output price\" in code, but fetch models.dev instead?"},
                "opts": [
                    {"zh": "这些事实随厂商发版不断变化；外置到一个社区维护、会自更新的目录，新模型常常零改动即可识别，把「易变事实」挡在代码之外", "en": "These facts keep changing with vendor releases; externalizing to a community-maintained, self-updating catalog means a new model is often recognized with zero code changes, blocking \"volatile facts\" out of the code"},
                    {"zh": "因为 models.dev 跑得更快", "en": "Because models.dev runs faster"},
                    {"zh": "因为代码里不能写数字", "en": "Because you can't put numbers in code"},
                    {"zh": "纯粹为了多一个网络依赖", "en": "Purely to add a network dependency"},
                ],
                "answer": 0,
                "why": {"zh": "模型的上限、价格、能力随厂商发版频繁变动，写死就得每次改代码发版。opencode 改去拉取 models.dev——一个社区维护、覆盖几乎所有 LLM 的公开目录，缓存住并在刷新时发 models-dev.refreshed 事件。这是「把变化挡在代码外」的智慧（和第 31 课 OpenAI 兼容白嫖生态同源），更是把「维护事实」的脏活交给最了解它们的上游社区——不重复维护事实，是更高层的复用。", "en": "Model limits, prices, capabilities change frequently with vendor releases; hardcoding means changing code and shipping each time. opencode fetches models.dev instead — a community-maintained public catalog covering nearly all LLMs, cached and emitting models-dev.refreshed on refresh. It's the \"keep change out of the code\" wisdom (same root as lesson 31's OpenAI-compatible free-ride), and hands the grunt work of \"maintaining facts\" to the upstream community that knows them best — not re-maintaining facts is a higher-order reuse."},
            },
            {
                "q": {"zh": "catalog 解析「模型名」失败时，给的是 ProviderNotFoundError 和 ModelNotFoundError 两个不同错误，而非一个 null。好处是？", "en": "When catalog fails to resolve a \"model name,\" it gives two distinct errors, ProviderNotFoundError and ModelNotFoundError, not one null. The benefit?"},
                "opts": [
                    {"zh": "明确区分「供应商没找到」和「供应商有但模型没找到」两种失败——它们修复方式不同，分开后上层能给精准提示", "en": "Clearly distinguishes \"provider not found\" from \"provider exists but model not found\"—their fixes differ, so separated, the upper layer can give precise hints"},
                    {"zh": "两个错误纯粹是冗余", "en": "The two errors are pure redundancy"},
                    {"zh": "为了让代码更长", "en": "To make the code longer"},
                    {"zh": "错误越多显得越专业", "en": "More errors look more professional"},
                ],
                "answer": 0,
                "why": {"zh": "catalog 是两层字典：先按 providerID 查供应商、再按 modelID 查模型。两种失败的修复截然不同——ProviderNotFound 你得检查 provider 段、ModelNotFound 你得检查 model 段（错误还带上 providerID+modelID）。用不同错误类型把它们分开，而非返回含糊的 null 让上层猜「哪步错了」，上层就能给出精准提示。这呼应全书「让错误自己说清自己是谁」。", "en": "catalog is a two-level dictionary: find provider by providerID, then model by modelID. The two failures' fixes differ entirely — ProviderNotFound you check the provider segment, ModelNotFound you check the model segment (error carries providerID+modelID). Separating them with distinct error types, rather than a vague null leaving the upper layer to guess \"which step failed,\" lets the upper layer give precise hints. Echoes the book's \"let errors say who they are.\""},
            },
            {
                "q": {"zh": "GitHub Copilot 作为「特殊供应商」，它的「特殊」主要体现在 Route 哪一件上？", "en": "GitHub Copilot as a \"special provider\"—its \"specialness\" mainly shows in which Route piece?"},
                "opts": [
                    {"zh": "auth（和 endpoint）：协议整套复用 OpenAI Chat/Responses，只换端点 + 一套「GitHub 工牌换短期 token」的独特认证", "en": "auth (and endpoint): protocol entirely reuses OpenAI Chat/Responses, swapping only the endpoint + a distinctive \"GitHub badge exchanges short-lived token\" auth"},
                    {"zh": "protocol：它发明了一套全新协议", "en": "protocol: it invented a brand-new protocol"},
                    {"zh": "framing：它用二进制分帧", "en": "framing: it uses binary framing"},
                    {"zh": "Route 的每一件全都和别人不同", "en": "Every Route piece differs from everyone"},
                ],
                "answer": 0,
                "why": {"zh": "packages/llm/src/providers/github-copilot.ts 直接复用 OpenAIChat.route / OpenAIResponses.route——协议、framing 零重写。它的「特殊」全在 auth：不能用固定 API key，要先拿 GitHub OAuth 工牌换一个有时效的 Copilot token 再做 Bearer 认证（AuthOptions.bearer），endpoint 也指向 Copilot 自己。这是第 33 课积木式 Route 的最佳实战：复用 protocol 件、只用 .with(...) 换 endpoint+auth。差异收敛成「换 baseURL+auth」的配置，而非协议里的 if(isCopilot)。", "en": "packages/llm/src/providers/github-copilot.ts directly reuses OpenAIChat.route / OpenAIResponses.route — protocol and framing zero rewrite. Its \"specialness\" is all in auth: no fixed API key, but first exchange a GitHub OAuth badge for a time-limited Copilot token then Bearer-auth (AuthOptions.bearer), with endpoint also pointing to Copilot's own. This is lesson 33's building-block Route's best field test: reuse the protocol piece, .with(...)-swap only endpoint+auth. The difference converges into \"swap baseURL+auth\" config, not if(isCopilot) in the protocol."},
            },
        ],
        "open": [
            {"zh": "课里说 opencode 把「模型的价格、上限、能力」这些事实，外置给 models.dev 社区目录来维护，自己只负责消费——称之为「不重复维护事实」的更高层复用。请结合你做过的项目，举一个「本可以外置给权威上游、却被自己硬编码维护」的事实（如时区表、汇率、国家区号、第三方 API 的字段）。把它外置会带来什么好处与什么新风险（如上游不可用、数据格式漂移）？", "en": "The lesson says opencode externalizes facts like \"model prices, limits, capabilities\" to the models.dev community catalog to maintain, only consuming them—calling it the higher-order reuse of \"not re-maintaining facts.\" From a project you've done, give an example of a fact that \"could have been externalized to an authoritative upstream but was hardcoded and self-maintained\" (e.g. timezone tables, exchange rates, country codes, a third-party API's fields). What benefits and what new risks (upstream unavailability, data-format drift) would externalizing bring?"},
            {"zh": "Copilot 的认证用「令牌交换」：先拿长期的 GitHub OAuth 凭证，换一个短期、限定用途的 Copilot token，再拿它去认证。课里说这是「最小权限 + 短时效凭证」的安全惯例，且这套复杂流程被整个封装进 auth 这一件、不惊动协议层。请论证：为什么「不直接把长期凭证发给推理端点，而是换一个短期 token」更安全？把这种安全复杂性隔离在 auth 这一层（而非散落各处），对整个系统的可维护性和可审计性有什么好处？", "en": "Copilot's auth uses \"token exchange\": take the long-lived GitHub OAuth credential, exchange for a short-lived, purpose-limited Copilot token, then authenticate with it. The lesson calls this the \"least privilege + short-lived credential\" security convention, with the whole complex flow encapsulated into the auth piece, undisturbing the protocol layer. Argue: why is \"not sending the long-lived credential to inference endpoints, but exchanging for a short-lived token\" more secure? What does isolating this security complexity in the auth layer (rather than scattering it) do for the system's maintainability and auditability?"},
        ],
    },
    "43-skills.html": {
        "mcq": [
            {
                "q": {"zh": "Skills 系统的「两段式架构」是怎么把一个技能劈成两半的？", "en": "How does the Skills system's \"two-stage architecture\" split a skill in two?"},
                "opts": [
                    {"zh": "「名字」半（name+description）经 Context Source 常驻注入系统上下文（随时可见、省 token）；「正文」半经权限化的 skill 工具按需注入（完整指令+基准目录+文件清单）", "en": "The \"name\" half (name+description) is resident-injected into system context via Context Source (always visible, token-saving); the \"body\" half is injected on demand via the permissioned skill tool (full instructions+base dir+file list)"},
                    {"zh": "前一半给模型、后一半给用户", "en": "First half to the model, second half to the user"},
                    {"zh": "随机劈成两段", "en": "Randomly split into two parts"},
                    {"zh": "其实没劈，整个技能一次性全加载", "en": "Not split at all, the whole skill loaded at once"},
                ],
                "answer": 0,
                "why": {"zh": "「全都加载」行不通：上百个技能、每个正文几千字，开局全塞进上下文会瞬间爆满。但模型又必须知道有哪些技能可用。两段式正是这对矛盾的解：把「有什么」（廉价名字+描述，经 SkillGuidance→SystemContext 常驻，第21~27课 Context Source）和「具体是什么」（昂贵正文，经 skill 工具——Tool.make+内部 permission.assert(action skill)——按需注入）分开——渐进式披露/懒加载。这和第37课「definitions 全列/settle 按需」、第42课「预览常驻/全文 spill」是同一套路。", "en": "\"Load everything\" won't work: hundreds of skills, each body thousands of words, stuffed into context at the start would instantly max it out. Yet the model must know which skills exist. The two stages resolve this: separate \"what exists\" (cheap name+description, resident via SkillGuidance→SystemContext, lessons 21–27's Context Source) from \"what it specifically is\" (expensive body, injected on demand via the skill tool — Tool.make + internal permission.assert(action skill)) — progressive disclosure/lazy loading. Same pattern as lesson 37's \"list definitions/settle on demand\" and lesson 42's \"preview resident/full text spilled.\""},
            },
            {
                "q": {"zh": "skill 工具被调用后，是它自己「干活」完成任务吗？", "en": "After the skill tool is called, does it \"do the work\" to complete the task itself?"},
                "opts": [
                    {"zh": "不是。skill 只「发讲义」：注入完整正文（指令+基准目录+文件清单）；真正执行靠模型已有的通用工具（read 读脚本、bash 跑、edit 改）。技能扩展「知道该怎么做」，非「能做什么」", "en": "No. The skill only \"hands out the handbook\": injects the full body (instructions+base dir+file list); actual execution via the model's existing general tools (read for scripts, bash to run, edit to change). A skill extends \"knowing how to do it,\" not \"what it can do\""},
                    {"zh": "是的，skill 工具内部把所有事都做完", "en": "Yes, the skill tool does everything internally"},
                    {"zh": "它会启动一个新的 agent 来做", "en": "It spawns a new agent to do it"},
                    {"zh": "它直接修改模型权重", "en": "It directly modifies the model weights"},
                ],
                "answer": 0,
                "why": {"zh": "skill 工具本身不干活、只发讲义。toModelOutput 注入 <skill_content>：指令正文 + 基准目录 URL + <skill_files> 清单。即一个技能=「一份说明书 + 一个装脚本资料的文件夹」。接下来真正的活，是模型用它已有的通用工具去干——read 读 scripts/ 下的脚本、bash 跑、edit 改。漂亮的分工：skill 负责把对的剧本递到手上，执行剧本还是 M7 那套通用的手。模型本就会用这些工具（能做什么固定），它缺的是「该按什么顺序、用什么诀窍组织它们」——这正是技能正文承载的方法论。", "en": "The skill tool itself doesn't work, only hands out the handbook. toModelOutput injects <skill_content>: the instruction body + base directory URL + <skill_files> list. So a skill = \"a manual + a folder holding scripts/materials.\" The actual work that follows is done by the model using its existing general tools — read for scripts under scripts/, bash to run, edit to change. A beautiful division of labor: the skill puts the right script in hand, executing it still uses M7's general hands. The model already knows these tools (what it can do is fixed); what it lacks is \"in what order, with what tricks to organize them\" — exactly the methodology the skill body carries."},
            },
            {
                "q": {"zh": "为什么说 Skills 是 M5（System Context）和 M7（工具）的「交汇点」？", "en": "Why is Skills called the \"meeting point\" of M5 (System Context) and M7 (tools)?"},
                "opts": [
                    {"zh": "一个技能半是上下文、半是工具：名字半走 Context Source（M5），正文半走 skill 工具（M7）；它用全了 Tool.make/注册表/权限/read 等前面所有抽象，是建在它们之上的更高层复用", "en": "A skill is half-context, half-tool: the name half via Context Source (M5), the body half via the skill tool (M7); it fully uses Tool.make/registry/permissions/read and all prior abstractions, a higher-level reuse built atop them"},
                    {"zh": "因为它在 M5 和 M7 两个文件夹里都有代码", "en": "Because it has code in both the M5 and M7 folders"},
                    {"zh": "纯属命名巧合", "en": "Pure naming coincidence"},
                    {"zh": "因为它同时被两个团队维护", "en": "Because two teams maintain it"},
                ],
                "answer": 0,
                "why": {"zh": "Skills 一只脚踩在系统上下文（M5，决定模型看见什么世界）、一只脚踩在工具系统（M7，决定模型能做什么）：名字半经 SystemContext 常驻、正文半经 skill 工具按需。它几乎用全了前面所有零件——Context Source（M5）、Tool.make（L36）、注册表（L37，SkillTool.layer）、权限（L41）、read（L38）。这说明它不是又一个孤立功能，而是建立在前面所有抽象之上的更高层复用。好的高层抽象，往往是底层零件足够扎实后自然『长』出来的。", "en": "Skills has one foot in system context (M5, what world the model sees) and one in the tool system (M7, what the model can do): the name half resident via SystemContext, the body half on demand via the skill tool. It uses nearly all the prior parts — Context Source (M5), Tool.make (L36), registry (L37, SkillTool.layer), permissions (L41), read (L38). This shows it isn't another isolated feature but a higher-level reuse built atop all prior abstractions. A good high-level abstraction often \"grows\" naturally once the lower parts are solid enough."},
            },
        ],
        "open": [
            {"zh": "课里指出「先廉价地广而告之、再昂贵地按需兑现」这个套路，在 opencode 里至少出现三次：第37课注册表（definitions 全列/settle 按需）、第42课有界输出（预览常驻/全文 spill）、第43课 Skills（名字常驻/正文按需）。请你提炼这个模式的共同结构（什么东西便宜、什么东西贵、用什么把二者连起来），并举一个你熟悉的系统里同样用「目录/索引 + 按需取详情」的例子（如网页分页、数据库游标、CDN）。", "en": "The lesson notes the pattern \"cheaply advertise first, expensively fulfill on demand\" appears at least three times in opencode: lesson 37 registry (list definitions/settle on demand), lesson 42 bounded output (preview resident/full text spilled), lesson 43 Skills (names resident/body on demand). Distill this pattern's common structure (what's cheap, what's expensive, what connects them), and give an example from a system you know that also uses \"catalog/index + fetch details on demand\" (web pagination, database cursors, CDN)."},
            {"zh": "课里说技能扩展的是 agent「知道该怎么做」（方法论），而非「能做什么」（能力）——模型本就会用 read/edit/bash，缺的是「面对某类任务该按什么顺序、用什么诀窍组织它们」。请结合你的经验，谈谈「把领域专家脑子里的 SOP 写成可加载的技能」这种做法的价值与局限：它在什么任务上特别有效？又在什么情况下，一份静态 SOP 反而会束缚 agent 的灵活应变？", "en": "The lesson says a skill extends the agent's \"knowing how to do it\" (methodology), not \"what it can do\" (capability)—the model already knows read/edit/bash, what it lacks is \"in what order, with what tricks to organize them for a kind of task.\" From your experience, discuss the value and limits of \"writing a domain expert's SOP into a loadable skill\": for what tasks is it especially effective? And when might a static SOP instead constrain the agent's flexible adaptation?"},
        ],
    },
    "42-bounded-output.html": {
        "mcq": [
            {
                "q": {"zh": "ToolOutputStore 截断超长输出时，为什么保留「头一半 + 尾一半」而不是「只留前 N 行」？", "en": "When ToolOutputStore truncates over-long output, why keep \"first half + last half\" instead of \"only first N lines\"?"},
                "opts": [
                    {"zh": "工具输出的信息密度集中在两端：开头=在跑啥/什么配置，结尾=结果/报错/汇总，中间多是重复进度行；只留前 N 行会砍掉最关键的『最终结果/报错』", "en": "Tool output's info density concentrates at both ends: start=what's running/config, end=result/error/summary, the middle mostly repetitive progress; keep-only-first-N would chop the all-important 'final result/error'"},
                    {"zh": "纯粹是为了对称好看", "en": "Purely for symmetric aesthetics"},
                    {"zh": "因为尾部数据更新", "en": "Because the tail data is newer"},
                    {"zh": "随机选的策略", "en": "A randomly chosen strategy"},
                ],
                "answer": 0,
                "why": {"zh": "preview 保留头 headLines=⌈max/2⌉ + 尾 tailLines=⌊max/2⌋，中夹 marker，字节超界同理头尾各取一半。对日志/测试/转储，最有用的信息几乎总在两端：开头说在跑什么，结尾说成没成、错在哪。天真地「只留前 1000 行」恰恰会砍掉最关键的最终结果——模型看半天进度却不知成败。这是把截断当成「有限预算里尽量多留有用信息」的优化，而非无脑砍到 N 行。", "en": "preview keeps head headLines=⌈max/2⌉ + tail tailLines=⌊max/2⌋ with a marker between, same half-each for bytes. For logs/tests/dumps, the most useful info is almost always at both ends: start says what's running, end says success or where the error is. Naively \"keep only the first 1000 lines\" would chop the all-important final result — the model reads progress forever yet doesn't know the outcome. This treats truncation as optimizing \"keep as much useful info as possible within a limited budget,\" not brainlessly chopping to N lines."},
            },
            {
                "q": {"zh": "截断必然损失信息，那被砍掉的中间部分怎么办？模型还能拿到全文吗？", "en": "Truncation inevitably loses info—what about the chopped middle? Can the model still get the full text?"},
                "opts": [
                    {"zh": "能：截断的同时把全文 write 到一份托管文件，路径放进 outputPaths 交给模型；要看全的，模型用第38课的 read 工具去读那份文件（可翻页）", "en": "Yes: while truncating, write the full text to a managed file, put the path in outputPaths for the model; to see the full thing, the model reads that file with lesson 38's read tool (pageable)"},
                    {"zh": "不能，中间永久丢失", "en": "No, the middle is permanently lost"},
                    {"zh": "全文被压缩成一句话", "en": "The full text is compressed into one sentence"},
                    {"zh": "全文被发邮件给用户", "en": "The full text is emailed to the user"},
                ],
                "answer": 0,
                "why": {"zh": "这是设计的第二处巧妙：截断给模型看的同时，把完整输出 write 到 {global.data}/tool-output/tool_{递增ID}（flag:wx 独占创建），bound 把路径放进 outputPaths。模型拿到「预览 + 全文在这个路径」的线索，真要看中间就用 read 工具读那份文件。这是漂亮的闭环——spill 出去的全文靠 read 收得回来，工具系统自我兜底（复用已有的 read，不另造接口，正是第36课统一工具表的红利）。有界视图+完整备份+按需回取+7天自动清理。", "en": "This is the design's second cleverness: while truncating what the model sees, write the full output to {global.data}/tool-output/tool_{ascending ID} (flag:wx exclusive create), and bound puts the path in outputPaths. The model gets \"a preview + the full text is at this path,\" and to see the middle reads that file with the read tool. A beautiful loop — the spilled full text is retrievable via read, the tool system backstopping itself (reusing the existing read, no new interface, exactly lesson 36's unified-tool-form dividend). Bounded view + full backup + on-demand retrieval + 7-day auto-cleanup."},
            },
            {
                "q": {"zh": "bash 的 1 MB 内存上限（第39课）和 ToolOutputStore 的 2000行/50KB 界（本课）是同一个东西吗？", "en": "Are bash's 1 MB memory cap (lesson 39) and ToolOutputStore's 2000-line/50KB bound (this lesson) the same thing?"},
                "opts": [
                    {"zh": "不是，是两层不同的界：bash 的防『内存』（命令 stdout 不在进程里堆爆），ToolOutputStore 的防『上下文』（任何工具结果回模型前限到 2000行/50KB）", "en": "No, two different bounds: bash's guards 'memory' (a command's stdout not piling up to blow the process), ToolOutputStore's guards 'context' (any tool result bounded to 2000 lines/50KB before returning to the model)"},
                    {"zh": "是的，完全一样", "en": "Yes, identical"},
                    {"zh": "bash 的更严，覆盖了 ToolOutputStore", "en": "bash's is stricter, supersedes ToolOutputStore"},
                    {"zh": "两者都只在配置文件里", "en": "Both exist only in config files"},
                ],
                "answer": 0,
                "why": {"zh": "两层不同的界，各防各的资源。bash 的 MAX_CAPTURE_BYTES=1MB 是更早、更底层的一道闸，防的是一条命令的 stdout 在进程内存里无限堆积撑爆内存。ToolOutputStore 的 2000行/50KB 是最终、面向模型的一道闸，防的是任何工具的结果回到模型前撑爆上下文窗口。一个管内存安全、一个管上下文预算，分工清晰、各守一摊。这也是 M7 反复出现的『凡可能量大处皆有界』红线在不同层面的体现。", "en": "Two different bounds, each guarding its own resource. bash's MAX_CAPTURE_BYTES=1MB is an earlier, lower-level gate guarding against a command's stdout piling up unboundedly in process memory. ToolOutputStore's 2000-line/50KB is the final, model-facing gate guarding against any tool's result blowing the context window before returning to the model. One governs memory safety, the other context budget, cleanly divided. This is M7's recurring 'anywhere volume could be large is bounded' red thread at different layers."},
            },
        ],
        "open": [
            {"zh": "课里说 ToolOutputStore 用 read 工具来「回取」spill 出去的全文——没有给自己另造一个『读回全文』的接口，而是复用了已有的 read，因为全文落成普通文件、读文件本就有人管。这被称为「第36课统一工具表的红利：因为所有工具同形，才能互相衔接、彼此兜底」。请举一个你见过的「因为接口统一/数据格式统一，模块得以意外地互相复用」的例子（如 Unix 一切皆文件、管道）。统一抽象带来的这种「组合性红利」，为什么常常事先想不到、事后才显现？", "en": "The lesson says ToolOutputStore uses the read tool to \"retrieve\" the spilled full text—it didn't build a dedicated 'read back the full text' interface but reused the existing read, because the full text lands as an ordinary file and reading files is already handled. This is called \"lesson 36's unified-tool-form dividend: because all tools are isomorphic, they can interconnect and backstop each other.\" Give an example you've seen of \"because the interface/data format is unified, modules unexpectedly reuse each other\" (Unix everything-is-a-file, pipes). Why is this \"composability dividend\" of a unified abstraction often unforeseeable beforehand, only emerging afterward?"},
            {"zh": "课里强调「有界是不容许差不多的承诺」：boundedPreview 连 marker（『…已截断…』）自身占的字节都算进 maxBytes 预算，不让提示语本身使总量超界。请谈谈这种「连边角料都算进预算」的严格，在你做过的资源约束场景（如固定缓冲区、限流配额、内存池）里为什么重要？「差不多就行」的近似预算，会在什么情况下酿成真实的 bug？", "en": "The lesson stresses \"bounded is a promise that allows no close-enough\": boundedPreview counts even the marker's ('…truncated…') own bytes into the maxBytes budget, not letting the notice itself overshoot. Discuss why this rigor of \"counting even the scraps into the budget\" matters in resource-constrained scenarios you've worked on (fixed buffers, rate-limit quotas, memory pools). Under what conditions does a \"close enough\" approximate budget breed a real bug?"},
        ],
    },
    "41-permissions.html": {
        "mcq": [
            {
                "q": {"zh": "权限系统的 evaluate 在「一条规则都没匹配上」时，默认给什么 effect？为什么这个默认很关键？", "en": "When no rule matches, what effect does the permission system's evaluate default to, and why is this default crucial?"},
                "opts": [
                    {"zh": "默认 ask（问用户）——安全默认：把所有「未被预先考虑」的敏感操作都落到「问一下」的安全网，agent 无法钻空子悄悄做未批准的事", "en": "Defaults to ask (ask the user) — secure default: every \"not pre-considered\" sensitive operation falls into the \"ask\" safety net, the agent can't game it into doing unapproved things silently"},
                    {"zh": "默认 allow，怎么方便怎么来", "en": "Defaults to allow, whatever's convenient"},
                    {"zh": "默认 deny，一律拒绝", "en": "Defaults to deny, refuse everything"},
                    {"zh": "直接崩溃报错", "en": "Crashes outright"},
                ],
                "answer": 0,
                "why": {"zh": "evaluate 把各 ruleset 拼起、findLast 通配匹配（后匹配者胜），一条都没命中时默认 effect:ask。这是整套安全模型的定盘星：若默认 allow，每出现一个设计者没预料的新动作，agent 就可能悄无声息做了你本想拦下的事；默认 ask 把这种「漏网」从根上堵死，代价不过初期多问几句，再用 always 把省事挣回来。把「未知」归到「问人」而非「放行」，是这套系统最重要的选择。", "en": "evaluate concatenates rulesets, findLast wildcard-match (last match wins), and when none match defaults to effect:ask. This is the security model's keystone: if it defaulted to allow, every new action the designers didn't foresee could let the agent silently do something you'd want blocked; defaulting to ask plugs this slip-through at the root, at the cost of a few early prompts, earning convenience back via always. Defaulting \"unknown\" to \"ask\" rather than \"allow\" is the system's most important choice."},
            },
            {
                "q": {"zh": "用户对一次 ask 回答 always，会发生什么？", "en": "What happens when the user answers always to an ask?"},
                "opts": [
                    {"zh": "放行这次 + 把决定持久化成一条规则（saved.add→SQLite permission 表、project 作用域），以后同样的 action×resource 直接 allow、不再问；还顺带解除被新规则覆盖的其它挂起询问", "en": "Permit this time + persist the decision into a rule (saved.add→SQLite permission table, project-scoped), future same action×resource is allowed directly, no more asking; also releases other pending asks the new rule covers"},
                    {"zh": "只放行这一次，下次还问", "en": "Permits just this once, asks again next time"},
                    {"zh": "永久禁用该工具", "en": "Permanently disables the tool"},
                    {"zh": "什么都不做", "en": "Does nothing"},
                ],
                "answer": 0,
                "why": {"zh": "always 不只「放行这次」，还把用户的决定固化成规则存进 permission 表（按 project 作用域、跨会话存活）。下次同样的 action×resource 再评估，这条 saved 规则让 evaluate 直接得到 allow，不再打扰用户。这让权限系统有「会学习」的体感：默认保守（问），每点一次 always 就少一类未来打扰，随信任积累问得越来越少——在「放手干」与「人在环」间动态平衡，把自由度的决定权可回收地交给用户。源码还顺带解除被新规则覆盖的其它挂起询问。", "en": "always does more than \"permit this time\"; it solidifies the user's decision into a rule stored in the permission table (project-scoped, cross-session). Next time the same action×resource is evaluated, this saved rule makes evaluate return allow directly, no more bothering the user. This gives the system a \"learning\" feel: conservative by default (ask), each always sheds a class of future interruptions, asking less as trust accumulates — dynamically balancing \"run free\" and \"human in the loop,\" handing the freedom decision revocably to the user. The source also releases other pending asks the new rule covers."},
            },
            {
                "q": {"zh": "deny 和 ask 这两种 effect，分别在哪一层把关？", "en": "At which layer do the two effects deny and ask each gate?"},
                "opts": [
                    {"zh": "deny 在「菜单层」（第37课 whollyDisabled，工具根本不出现给模型）；ask 在「调用层」（工具在菜单上、模型能点，但执行前发问）——纵深防御", "en": "deny at the \"menu layer\" (lesson 37 whollyDisabled, the tool not even shown to the model); ask at the \"call layer\" (the tool's on the menu, the model can pick it, but asks before executing) — defense in depth"},
                    {"zh": "两者都在同一层、做同一件事", "en": "Both at the same layer doing the same thing"},
                    {"zh": "deny 在调用层、ask 在菜单层", "en": "deny at the call layer, ask at the menu layer"},
                    {"zh": "两者都只在数据库层", "en": "Both only at the database layer"},
                ],
                "answer": 0,
                "why": {"zh": "纵深防御：被彻底 deny 的工具在 materialize 时就被 whollyDisabled 滤掉，根本不进发给模型的清单——模型连「有这个工具」都不知道（最干净的拒绝是让对方不知道有这个选项，第37课）。而 ask 的工具在菜单上、模型能点，但每次真要执行时 assert 先发问——执行前的最后一道闸。deny 管「能不能有」、ask 管「这次行不行」，各司其职。", "en": "Defense in depth: a wholly-denied tool is filtered by whollyDisabled at materialize, not even entering the list sent to the model — the model doesn't even know \"this tool exists\" (the cleanest refusal is to not let the other know the option exists, lesson 37). An ask tool is on the menu and the model can pick it, but each time it's about to execute, assert asks first — the last gate before execution. deny governs \"can it exist,\" ask governs \"is this time OK,\" each its own job."},
            },
        ],
        "open": [
            {"zh": "课里说权限系统在「让 agent 放手干」和「让人始终在环」之间找动态平衡：默认保守（问），随 always 攒规则逐步放开，把自由度可回收地交给用户。请结合你用过的「权限/同意」机制（如手机 App 权限、sudo、CI 部署审批），谈谈「一次性同意 vs 永久授权 vs 每次都问」各自的利弊。一个好的「人在环」系统，应该如何随时间调整它打扰用户的频率？", "en": "The lesson says the permission system finds a dynamic balance between \"let the agent run free\" and \"keep a human in the loop\": conservative by default (ask), gradually loosening as always accrues rules, handing the freedom decision revocably to the user. Using permission/consent mechanisms you've used (mobile app permissions, sudo, CI deploy approvals), discuss the pros/cons of \"one-time consent vs permanent authorization vs ask every time.\" How should a good \"human-in-the-loop\" system adjust how often it bothers the user over time?"},
            {"zh": "课里指出 reject 有两种形态：纯 RejectedError（光说不行）和 CorrectedError（拒绝 + 附理由，理由回传给模型让它纠偏），后者把「拒绝」从死胡同变成一次纠偏，让「人在环」不只是卡危险、更是引导 agent 向对。请论证：为什么「带反馈的拒绝」比「光拒绝」对一个 LLM agent 更有价值？这和你给人/系统反馈时「不只说不行、还说怎么改」是同一种智慧吗？", "en": "The lesson notes reject has two forms: pure RejectedError (just \"no\") and CorrectedError (reject + attached reason, the reason fed back to the model to course-correct), the latter turning \"rejection\" from a dead end into a correction, making \"human in the loop\" not just block danger but steer the agent toward right. Argue: why is \"rejection with feedback\" more valuable than \"plain rejection\" for an LLM agent? Is this the same wisdom as \"don't just say no, say how to fix it\" when giving feedback to people/systems?"},
        ],
    },
    "40-other-tools.html": {
        "mcq": [
            {
                "q": {"zh": "webfetch/websearch/question/todowrite 这四个工具，相比前面的文件/搜索/执行工具，新增了什么？", "en": "What do webfetch/websearch/question/todowrite add compared to the earlier file/search/exec tools?"},
                "opts": [
                    {"zh": "把 agent 的「手」从本地代码库伸向三个新去处：网络（webfetch/websearch）、人（question）、agent 自身状态（todowrite）", "en": "Extend the agent's \"hands\" from the local codebase to three new destinations: the network (webfetch/websearch), people (question), the agent's own state (todowrite)"},
                    {"zh": "只是前面工具的别名", "en": "Just aliases of the earlier tools"},
                    {"zh": "它们不是工具，是配置项", "en": "They're not tools but config options"},
                    {"zh": "它们替换了文件工具", "en": "They replace the file tools"},
                ],
                "answer": 0,
                "why": {"zh": "前面工具几乎都指向本地文件系统；这四个沿两条新轴外推：向外伸向网络（webfetch 读指定页、websearch 搜开放网，破「只懂本地」「知识截止日」两墙），转内朝向人与自己（question 从用户拉回答案、todowrite 维护 agent 自己的待办）。一个 agent 的能力边界很大程度由「手能伸到哪」决定。四者仍是第 36 课 Config 表的不同填法。", "en": "Earlier tools almost all pointed at the local filesystem; these four push along two new axes: outward to the network (webfetch reads a specific page, websearch searches the open net, breaking the \"only local\" and \"knowledge cutoff\" walls), inward to people and self (question pulls answers from the user, todowrite maintains the agent's own todos). An agent's capability boundary is largely set by \"where its hands can reach.\" All four are still different fillings of lesson 36's Config form."},
            },
            {
                "q": {"zh": "opencode 的 websearch 工具和「供应商自带的 web search」有什么区别？为什么 opencode 要自己做一个本地的？", "en": "How does opencode's websearch tool differ from \"the provider's own web search,\" and why does opencode make a local one?"},
                "opts": [
                    {"zh": "本课 websearch 是 opencode 自己跑的本地工具（背后 Exa/Parallel），在 opencode 侧执行；供应商自带的在供应商侧执行。自己做→搜网能力不被模型供应商绑定，换供应商行为一致", "en": "This websearch is opencode's own local tool (backed by Exa/Parallel), executing on opencode's side; the provider's executes provider-side. Making its own → web-search capability isn't bound to the model provider, behavior consistent across provider switches"},
                    {"zh": "两者完全一样", "en": "They're identical"},
                    {"zh": "本地的更慢但更便宜", "en": "The local one is slower but cheaper"},
                    {"zh": "供应商自带的不存在", "en": "The provider's doesn't exist"},
                ],
                "answer": 0,
                "why": {"zh": "「让模型搜网」有两条路：opencode 拿 Exa/Parallel key 在本地搜（本课 websearch），或用供应商内建搜索（在供应商服务器跑）。opencode 把本地这条做成标准工具，于是搜网能力不依赖「你用的供应商支不支持」——无论今天 Anthropic、明天 Gemini，行为都一致，且 opencode 自主决定接哪家后端、怎么调参。这是「把能力下沉到自己这层、不被上游绑定」（呼应第 28 课）。description 还注入当前年份补模型时间盲区。", "en": "\"Letting the model search the web\" has two paths: opencode searching locally with an Exa/Parallel key (this websearch), or using the provider's built-in search (running on the provider's server). opencode makes the local path a standard tool, so web-search capability doesn't depend on \"whether your provider supports it\" — Anthropic today or Gemini tomorrow, behavior stays consistent, and opencode independently decides which backend and tuning. This is \"sink the capability to your own layer, not bound by the upstream\" (echoing lesson 28). The description also injects the current year to fill the model's time blind spot."},
            },
            {
                "q": {"zh": "todowrite 工具的「作用对象」有什么特别？", "en": "What's special about todowrite's \"target of effect\"?"},
                "opts": [
                    {"zh": "它不改外部世界，只维护 agent 自己的一份会话待办清单（SessionTodo）——是「外置工作记忆」，帮长任务里的模型不忘全局、让用户看见进度", "en": "It changes nothing external, only maintaining the agent's own session todo list (SessionTodo) — an \"externalized working memory,\" helping the model in long tasks not forget the big picture and letting the user see progress"},
                    {"zh": "它直接修改用户的文件系统", "en": "It directly modifies the user's filesystem"},
                    {"zh": "它向网络发请求", "en": "It makes network requests"},
                    {"zh": "它会重启 agent", "en": "It restarts the agent"},
                ],
                "answer": 0,
                "why": {"zh": "绝大多数工具把意志推向外部（改文件、跑命令、搜网），todowrite 却作用于 agent 自己的状态——维护「当前会话的结构化待办」（接 SessionTodo）。在动辄十几步的长任务里，模型注意力被当前步占满、易忘全局；todowrite 把计划与进度从模型易失的脑内挪到一份持久可见的清单上，既帮模型不跑偏、也让用户实时看到「打算干啥、做到哪」。它还把 agent 的思路外化成可观测产物，这种透明是信任的基础。", "en": "Most tools push the will outward (change files, run commands, search); todowrite acts on the agent's own state — maintaining \"the current session's structured todos\" (backed by SessionTodo). In a dozen-plus-step long task, the model's attention is consumed by the current step and easily forgets the big picture; todowrite moves plan and progress from the model's volatile mind to a persistent, visible list, helping the model stay on track and letting the user see in real time \"what it plans, where it's at.\" It also externalizes the agent's thinking into an observable artifact, and this transparency is the basis of trust."},
            },
        ],
        "open": [
            {"zh": "课里说 question 是整个工具集里的「异类」——别的工具都把 agent 的意志推向外部，它却从人那里把信息拉回来。请谈谈一个能「在该问的时候问」的 agent，比一个「永远自作主张」的 agent 好在哪？又：什么样的决策该问用户、什么样的该自己定？过度地问（事事都问）和过度地不问（重大抉择也擅自决定）各有什么害处？", "en": "The lesson calls question the \"oddball\" of the toolset—other tools push the agent's will outward, but it pulls info back from a person. Discuss how an agent that \"asks when it should\" beats one that \"always decides alone.\" Also: what decisions should be asked of the user, which decided alone? What are the harms of over-asking (asking everything) versus under-asking (deciding major choices unilaterally)?"},
            {"zh": "课里反复出现一个主题：工具的「用户」是个模型，于是定义里处处藏着对模型的体贴——webfetch 默认转 markdown、websearch 注入当前年份、format 可省略默认 markdown。请再举一个「为 LLM 调用而设计」与「为人调用而设计」会做出不同取舍的接口细节（如返回格式、默认值、错误信息、字段命名）。为模型设计接口时，你会特别优化什么？", "en": "A recurring theme: the tool's \"user\" is a model, so the definitions hide care for the model everywhere—webfetch defaults to markdown, websearch injects the current year, format is omittable defaulting to markdown. Give another interface detail where \"designed for LLM calls\" vs \"designed for human calls\" would make a different tradeoff (return format, defaults, error messages, field naming). Designing an interface for a model, what would you especially optimize?"},
        ],
    },
    "39-search-exec-tools.html": {
        "mcq": [
            {
                "q": {"zh": "glob 和 grep 这两个搜索工具的底层是什么？为什么这么选？", "en": "What are the two search tools glob and grep built on, and why?"},
                "opts": [
                    {"zh": "都架在 Ripgrep（rg）服务上——业界最快的代码搜索之一、默认尊重 .gitignore；opencode 复用权威上游而非自己手写遍历+正则", "en": "Both built on the Ripgrep (rg) service — one of the fastest code searches, respects .gitignore by default; opencode reuses the authoritative upstream rather than hand-writing traversal+regex"},
                    {"zh": "各自手写文件系统遍历和正则匹配", "en": "Each hand-writes filesystem traversal and regex matching"},
                    {"zh": "用数据库全文索引", "en": "Use a database full-text index"},
                    {"zh": "调用一个云搜索 API", "en": "Call a cloud search API"},
                ],
                "answer": 0,
                "why": {"zh": "glob（按文件名）和 grep（按内容正则）都架在 Ripgrep 服务上。ripgrep 是业界公认最快的代码搜索之一，且默认尊重 .gitignore（不把 node_modules/dist 搜进来污染结果）。opencode 没自己手写遍历+正则（又慢又易错），而是站在 ripgrep 肩膀上、只包成两个窄接口——这正是第 35 课「不重复造轮子、复用权威上游」的同一种智慧。两者都带 limit 防结果撑爆模型上下文。", "en": "glob (by filename) and grep (by content regex) are both built on the Ripgrep service. ripgrep is one of the acknowledged fastest code searches, respecting .gitignore by default (not polluting results with node_modules/dist). opencode didn't hand-write traversal+regex (slow, error-prone) but stands on ripgrep's shoulders, wrapping just two narrow interfaces — the same wisdom as lesson 35's \"don't reinvent the wheel, reuse the authoritative upstream.\" Both carry limit to keep results from blowing the model's context."},
            },
            {
                "q": {"zh": "bash 工具拥有「宿主用户的文件/进程/网络全权限」，opencode 给它配了哪些护栏？", "en": "The bash tool holds \"the host user's full file/process/network authority\"; what guardrails does opencode give it?"},
                "opts": [
                    {"zh": "限时（默认2分/最长10分，schema 卡上限）+ 限量（stdout/stderr 各1MB）+ 双重 permission（workdir+命令）+ 可强制终止（detached+forceKillAfter 3秒）+ stdin ignore", "en": "Time-limited (default 2min/max 10min, schema-capped) + volume-limited (stdout/stderr each 1MB) + dual permission (workdir+command) + force-terminable (detached+forceKillAfter 3s) + stdin ignore"},
                    {"zh": "没有任何护栏，模型说啥跑啥", "en": "No guardrails, runs whatever the model says"},
                    {"zh": "只允许跑预先白名单里的命令", "en": "Only allows pre-whitelisted commands"},
                    {"zh": "每条命令都要用户手动确认", "en": "Every command needs manual user confirmation"},
                ],
                "answer": 0,
                "why": {"zh": "能力越大、护栏越严。bash 是「什么都能干」的逃生舱，被限时/限量/限地/可中断地团团围住：超时（默认2分、最长10分，且在 schema 层就 ≤MAX_TIMEOUT_MS 卡死）防死循环挂死 agent；1MB 内存上限防 cat 大文件撑爆内存；workdir+命令两道 permission.assert；detached 启动 + forceKillAfter 3秒宽限可强制收尾；stdin=ignore 防命令反问模型。超时还被降格成带 timedOut 的正常结果，回一句「加大 timeout 重试」的可操作指引。", "en": "Greater power, stricter guardrails. bash is the \"do-anything\" escape hatch, hemmed in time/volume/place-limited and interruptible: timeout (default 2min, max 10min, capped ≤MAX_TIMEOUT_MS at the schema layer) prevents an infinite loop hanging the agent; the 1MB in-memory cap prevents cat huge-file blowing memory; dual permission.assert on workdir+command; detached launch + forceKillAfter 3s grace for force cleanup; stdin=ignore prevents commands prompting the model. Timeout is also demoted to a normal result with timedOut, returning an actionable \"retry with a larger timeout\" guide."},
            },
            {
                "q": {"zh": "课里特别澄清：bash 工具是经「PTY 伪终端」运行的吗？", "en": "The lesson specially clarifies: does the bash tool run via \"PTY pseudo-terminal\"?"},
                "opts": [
                    {"zh": "不是。bash 经 AppProcess.run→ChildProcessSpawner（spawn/child_process 批处理）；pty/* 是另一套给交互式终端（实时流+可输入）用的基础设施", "en": "No. bash runs via AppProcess.run→ChildProcessSpawner (spawn/child_process batch); pty/* is separate infrastructure for interactive terminals (live stream + typeable)"},
                    {"zh": "是的，bash 就是 PTY", "en": "Yes, bash is PTY"},
                    {"zh": "bash 和 pty 是同一个模块", "en": "bash and pty are the same module"},
                    {"zh": "bash 既不用 spawn 也不用 pty", "en": "bash uses neither spawn nor pty"},
                ],
                "answer": 0,
                "why": {"zh": "常见误解。bash 工具通过 AppProcess.run 执行，底层是 ChildProcessSpawner（child_process/spawn 的跨平台封装）——「启动子进程、跑完、收 stdout/stderr」的批处理模型，不是伪终端。pty/*（Proc.onData/write/resize）是另一套：给交互式终端用（第10课 pty/pty-connect 路由、第33课 WebSocketTracker），让真人在界面开实时可输入的 shell。模型需要确定性批处理（一问一答），不需要会不断吐字符、还等输入的实时流（所以 stdin 干脆 ignore）。两种交互模型，两套机制，诚实切分而非强求统一。", "en": "A common misconception. The bash tool executes via AppProcess.run, underneath ChildProcessSpawner (a cross-platform wrapper over child_process/spawn) — a batch model of \"launch child process, run, collect stdout/stderr,\" not a pseudo-terminal. pty/* (Proc.onData/write/resize) is separate: for interactive terminals (lesson 10's pty/pty-connect routes, lesson 33's WebSocketTracker), letting a human open a live typeable shell in the UI. The model needs deterministic batch (Q&A), not a live stream that spits characters and awaits input (so stdin is ignore). Two interaction models, two mechanisms, an honest split rather than forced unification."},
            },
        ],
        "open": [
            {"zh": "课里把工具分成「专用」（glob/grep，把高频事做窄做快）和「通用」（bash，全权限的逃生舱），并给出原则：「能力越大、护栏越严」。请结合你设计或用过的系统，谈谈这条原则的体现（如 sudo、危险 API 的二次确认、生产环境的写权限）。一个「什么都能干」的通用接口，相比一组「各管一摊」的专用接口，各自的利弊是什么？", "en": "The lesson splits tools into \"specialized\" (glob/grep, making high-frequency things narrow and fast) and \"general\" (bash, the full-authority escape hatch), with the principle \"greater power, stricter guardrails.\" From a system you've designed or used, discuss this principle's manifestations (sudo, double-confirmation for dangerous APIs, write permission in production). What are the pros/cons of one \"do-anything\" general interface versus a set of \"each minds its own\" specialized interfaces?"},
            {"zh": "课里强调 opencode 用两套不同机制分别服务「给模型跑命令」（批处理 spawn）和「给真人开终端」（PTY 流式可输入），拒绝硬把一套套到另一种交互上。请论证：为什么「实时交互式」和「确定性批处理」是本质不同的需求？把模型的「思考-行动」节奏（一问一答）和真人盯终端（要实时、要能 Ctrl-C、要能答 y）对照，说说各自为什么需要不同的执行模型。", "en": "The lesson stresses opencode uses two different mechanisms for \"run commands for the model\" (batch spawn) and \"open a terminal for a human\" (PTY streaming, typeable), refusing to force one onto the other interaction. Argue: why are \"real-time interactive\" and \"deterministic batch\" essentially different needs? Contrasting the model's \"think-act\" rhythm (Q&A) with a human watching a terminal (wants real-time, Ctrl-C, typing y), explain why each needs a different execution model."},
        ],
    },
    "38-file-tools.html": {
        "mcq": [
            {
                "q": {"zh": "opencode 的四个文件工具 read/write/edit/apply_patch 覆盖了什么？它们和第 36 课的关系是？", "en": "What do opencode's four file tools read/write/edit/apply_patch cover, and how do they relate to lesson 36?"},
                "opts": [
                    {"zh": "一条「从粗到细、从单到多」的改动光谱（整写/精改/批量补丁/只读），且全是第 36 课 Config 表的不同填法（input/output schema + execute + 权限）", "en": "A \"coarse-to-fine, single-to-many\" change spectrum (whole-write/precise-edit/batch-patch/read-only), all different fillings of lesson 36's Config form (input/output schema + execute + permission)"},
                    {"zh": "四个互不相干、各自从头实现的独立程序", "en": "Four unrelated standalone programs each implemented from scratch"},
                    {"zh": "其实是同一个工具的四个别名", "en": "Actually four aliases of the same tool"},
                    {"zh": "只有 read 是工具，其余是内部函数", "en": "Only read is a tool, the rest are internal functions"},
                ],
                "answer": 0,
                "why": {"zh": "write 最粗（整页换）、edit 最细（一句改）、apply_patch 最广（跨文件一把梭）、read 是唯一无副作用的观察者。不同改动形状配不同工具最省 token、最不易错：改一行用 edit、重写整文件用 write、跨文件重构用 apply_patch，模型自己挑趁手的。四者都在填第 36 课那张 Config 表——各声明 input/output schema + execute，套权限（write/edit/apply_patch 经 withPermission \"edit\"、read 经内部 permission.assert）。这正是「一张表、各自填空」的果。", "en": "write coarsest (whole-page swap), edit finest (one-sentence change), apply_patch broadest (cross-file in one go), read the only side-effect-free observer. Different change shapes fit different tools to save tokens and least err: change one line with edit, rewrite a whole file with write, refactor across files with apply_patch, the model picking. All four fill lesson 36's Config form — declaring input/output schema + execute, permissioned (write/edit/apply_patch via withPermission \"edit\", read via internal permission.assert). The fruit of \"one form, each fills blanks.\""},
            },
            {
                "q": {"zh": "edit 工具发现 oldString 在文件里出现了多次、而调用没设 replaceAll，它会怎么做？", "en": "If edit finds oldString appears multiple times in the file and the call didn't set replaceAll, what does it do?"},
                "opts": [
                    {"zh": "停手反问：返回 ToolFailure「有多处匹配，请提供更多上下文或设 replaceAll」——绝不替模型猜该改哪一处", "en": "Stops and asks back: returns ToolFailure \"multiple matches, provide more context or set replaceAll\" — never guessing for the model which to change"},
                    {"zh": "默认改第一处", "en": "Changes the first by default"},
                    {"zh": "默认全部都改", "en": "Changes all by default"},
                    {"zh": "随机改一处", "en": "Changes a random one"},
                ],
                "answer": 0,
                "why": {"zh": "面对歧义，最负责任的动作不是「猜一个」而是「把歧义如实抛回去」。模型说「把 return x 改成 return y」，可文件有三处 return x——改哪个？莽撞工具改第一个或全改会酿 bug；edit 选择停手返回 ToolFailure，让模型多给上下文再来。这条拒绝（连同「找不到 oldString，必须一字不差」）都走 ToolFailure 回传，错误消息本身成了给模型的操作指南。这是把玩具 demo 和敢用在真实代码库上的工具区分开的东西。", "en": "Facing ambiguity, the most responsible action isn't \"guess one\" but \"throw the ambiguity back faithfully.\" The model says \"change return x to return y,\" but the file has three return x—which? A reckless tool changing the first or all breeds a bug; edit stops and returns ToolFailure, having the model give more context and retry. This rejection (like \"could not find oldString, must match exactly\") goes through ToolFailure, the error message itself the model's operating guide. This separates a toy demo from a tool you'd dare use on a real codebase."},
            },
            {
                "q": {"zh": "edit 最后用 writeIfUnchanged({target, expected: 刚读到的字节, content}) 落盘。这是为了什么？", "en": "edit finally lands via writeIfUnchanged({target, expected: just-read bytes, content}). What for?"},
                "opts": [
                    {"zh": "compare-and-swap：只在磁盘内容仍等于当初读到的那份时才写，否则拒——把「读-改-写」并发风险关进原子操作，防丢失更新（乐观并发，不上悲观锁）", "en": "Compare-and-swap: write only if disk content still equals what was originally read, else reject — locking \"read-modify-write\" concurrency risk into an atomic operation, preventing lost updates (optimistic concurrency, no pessimistic lock)"},
                    {"zh": "为了写得更快", "en": "To write faster"},
                    {"zh": "为了压缩文件", "en": "To compress the file"},
                    {"zh": "纯属多余的检查", "en": "A purely redundant check"},
                ],
                "answer": 0,
                "why": {"zh": "从③读字节到⑦写回，中间隔着数匹配、算替换——这期间别的进程（另一 agent、用户在编辑器手改、watch 脚本）可能也改了同一文件。闷头写就会悄悄抹掉别人的改动（丢失更新）。writeIfUnchanged 带上 expected=读到的原字节，语义是 compare-and-swap：仅当盘上内容仍等于 expected 才写，变了就拒。它不上悲观锁（不阻塞别人），乐观假设没人动、写时核对——数据库/分布式系统的 OCC。在多 agent 并行的未来尤其关键。", "en": "From ③ reading bytes to ⑦ writing back, counting and computing the replacement intervene—during which another process (another agent, the user editing, a watch script) may have changed the same file. Blindly writing would silently erase their changes (lost update). writeIfUnchanged carries expected=the read bytes, semantics compare-and-swap: write only if disk still equals expected, reject if changed. It takes no pessimistic lock (doesn't block others), optimistically assumes no one touched it, verifying at write—databases'/distributed systems' OCC. Especially crucial in a multi-agent parallel future."},
            },
        ],
        "open": [
            {"zh": "课里说 edit 的执行里「真正替换只一行，其余全是护栏」，并把四道护栏（精确匹配/歧义拒绝/行尾归一/乐观并发）对应到「让 AI 改代码会踩的真实坑」。请结合你写过的、需要被不可靠输入调用的工具或接口，谈谈「核心逻辑很短、护栏很长」是不是常态？你会如何判断「哪些护栏值得加、哪些是过度防御」？", "en": "The lesson says in edit's execution \"only one line actually replaces, the rest all guardrails,\" mapping four guardrails (exact match/ambiguity refusal/line-ending normalization/optimistic concurrency) to \"real pits of letting AI change code.\" From a tool or interface you've written that's called by unreliable input, discuss whether \"short core logic, long guardrails\" is the norm. How would you judge \"which guardrails are worth adding, which are over-defense\"?"},
            {"zh": "课里强调 edit 的拒绝消息（\"must match exactly\"、\"set replaceAll to true\"）是「写给模型看的操作指南」——因为工具的「用户」是个会照错误信息调整的模型。这和「写给人看的错误信息」有何异同？为一个 LLM 调用的工具设计错误信息时，你会特别注意什么（如可操作性、是否暴露内部细节、是否引导正确重试）？", "en": "The lesson stresses edit's rejection messages (\"must match exactly,\" \"set replaceAll to true\") are \"operating guides written for the model\"—because the tool's \"user\" is a model that adjusts per the error message. How is this similar to/different from \"error messages written for humans\"? Designing error messages for an LLM-called tool, what would you especially mind (actionability, exposing internal details, guiding correct retry)?"},
        ],
    },
    "37-tool-registry.html": {
        "mcq": [
            {
                "q": {"zh": "工具注册表的 register 怎么管理工具的「存在」？", "en": "How does the tool registry's register manage a tool's \"existence\"?"},
                "opts": [
                    {"zh": "Scope 绑定 + 同名叠成一摞：登记时装 addFinalizer，作用域关→按 token 自动撤销；同名取 .at(-1) 最新顶班，撤走后被覆盖者自动复位", "en": "Scope binding + same-name stacking: registration installs addFinalizer, scope close→auto-revoke by token; same-name takes .at(-1) latest on shift, the covered one auto-restores on revoke"},
                    {"zh": "一个全局 Map<名字,工具>，新登记直接覆盖旧的、永不恢复", "en": "A global Map<name,tool>, new registration overwrites old, never restored"},
                    {"zh": "把工具写进数据库，手动增删", "en": "Writes tools into a database, manually added/removed"},
                    {"zh": "工具一旦登记就永久存在", "en": "Once registered a tool exists forever"},
                ],
                "answer": 0,
                "why": {"zh": "local 是 Map<名字, 登记数组>——同名叠成一摞。register 生成唯一 token，把登记压栈，并 addFinalizer：作用域关闭时按 token 精准抽走本次登记，空了删名、剩的自动顶上。于是「工具的存在与作用域同生共死，覆盖可自动恢复」——插件卸载（scope 关）那一刻，它的覆盖自动消失、内置版自动复位，无需手动注销。这是第 23 课 acquireRelease「把清理焊在获取上」的延伸。压栈+装 finalizer 还裹在 uninterruptible 里原子完成。", "en": "local is Map<name, registration array> — same-name stacks up. register generates a unique token, pushes the registration, and addFinalizer: scope close precisely pulls this call's registration by token, deletes the name if empty, the rest auto-surfaces. So \"a tool's existence lives and dies with its scope, overrides auto-restore\" — the moment a plugin unloads (scope closes), its override vanishes and the built-in restores, no manual unregister. An extension of lesson 23's acquireRelease \"weld cleanup onto acquisition.\" Push+finalizer also wrapped in uninterruptible for atomicity."},
            },
            {
                "q": {"zh": "一个被权限策略彻底禁用的工具，在 materialize 后会怎样？", "en": "What happens to a tool fully disabled by permission policy after materialize?"},
                "opts": [
                    {"zh": "根本不进 definitions——模型连「有这个工具」都不知道，自然不会去点（最好的拒绝是让它不知道有这个选项）", "en": "It doesn't even enter definitions — the model doesn't even know \"this tool exists,\" so won't order it (the best refusal is to not let it know the option exists)"},
                    {"zh": "照样进菜单，模型点了再返回拒绝", "en": "Still enters the menu, the model orders then gets refused"},
                    {"zh": "进菜单但标记为「禁用」", "en": "Enters the menu but marked \"disabled\""},
                    {"zh": "导致 materialize 报错", "en": "Causes materialize to error"},
                ],
                "answer": 0,
                "why": {"zh": "materialize 合并 applications + local 摞顶后，用传入的权限规则集过一遍，把 whollyDisabled 的工具从清单里删掉，再产出 {definitions, settle}。于是权限过滤发生在「菜单」这一层——被禁工具压根不出现在发给模型的 definitions 里，比「点了再拒」干净得多。materialize 是不可变快照，与还在随作用域变动的 local 解耦：register 管「有哪些工具」、materialize 管「这一轮看见哪些」。", "en": "materialize merges applications + local stack-tops, runs the passed permission ruleset over them, removes whollyDisabled tools, then produces {definitions, settle}. So permission filtering happens at the \"menu\" layer — a banned tool doesn't even appear in the definitions sent to the model, far cleaner than \"order then refuse.\" materialize is an immutable snapshot, decoupled from the scope-changing local: register owns \"which tools exist,\" materialize owns \"which this turn sees.\""},
            },
            {
                "q": {"zh": "settle 执行前会核对每个登记的 identity（一个唯一空对象），不一致就报「Stale tool call」。这防的是什么？", "en": "settle before executing verifies each registration's identity (a unique empty object), reporting \"Stale tool call\" on mismatch. What does this prevent?"},
                "opts": [
                    {"zh": "防「名字相同、身份已换」的错配：从模型看到菜单到它点这道菜之间，该工具的登记可能变了；验章保证「所见即所调」，不把调用悄悄派给一个模型没见过的同名工具", "en": "Prevents \"same name, identity changed\" mismatch: between the model seeing the menu and ordering, the tool's registration may have changed; the seal guarantees \"what you see is what you call,\" not silently dispatching to a same-named tool the model never saw"},
                    {"zh": "防止两个工具同名", "en": "Prevents two tools sharing a name"},
                    {"zh": "防止 SQL 注入", "en": "Prevents SQL injection"},
                    {"zh": "防止模型调用太频繁", "en": "Prevents the model calling too often"},
                ],
                "answer": 0,
                "why": {"zh": "在工具能动态来去的系统里，「模型看到菜单」与「模型点这道菜」之间有时间差——这期间该工具的登记可能因作用域关闭或被重新登记而变了。每次登记带一个唯一 identity={}，materialize 把它记进菜单，settle 执行前核对「当前这个名字下的 identity 还是不是菜单上那个」，不一致即 Stale tool call。它把「名字相同、人已换」的错配变成一个明确可观测的错误，守住「所见即所调」，而非一桩无声的灵异事件。", "en": "In a system where tools come and go dynamically, there's a time gap between \"the model saw the menu\" and \"the model orders this dish\" — during which the tool's registration may have changed via scope close or re-registration. Each registration carries a unique identity={}, materialize records it into the menu, and settle before executing checks \"is the identity under this name still the menu's one,\" mismatch → Stale tool call. It turns the \"same name, different person\" mismatch into an explicit, observable error, preserving \"what you see is what you call,\" not a silent uncanny event."},
            },
        ],
        "open": [
            {"zh": "课里说 register（可变·带作用域的「有哪些工具」）和 materialize（不可变·快照的「这一轮看见哪些」）被刻意切成两层。请论证：把「随时在变的注册表」和「某一刻定格的快照」分开，对正确性（如并发、重放）和可推理性各有什么好处？如果 agent 循环直接读那个随时在变的 local、而不先 materialize 一份快照，可能出什么乱子？", "en": "The lesson says register (mutable·scoped \"which tools exist\") and materialize (immutable·snapshot \"which this turn sees\") are deliberately split into two layers. Argue: separating \"the ever-changing registry\" from \"a snapshot frozen at one moment\" — what does it buy for correctness (concurrency, replay) and reasoning? If the agent loop read the ever-changing local directly instead of materializing a snapshot first, what could go wrong?"},
            {"zh": "课里两次出现「空对象 {} 作唯一标识」：token 标识「哪次 register 调用」、identity 标识「哪个具体登记」，利用 {} !== {}（引用天生唯一）。请谈谈这个技巧相比「生成 UUID 字符串」的利弊（唯一性、性能、可序列化、跨进程）。它在什么场景适用、什么场景会失效（比如需要把标识写进日志或数据库时）？", "en": "The lesson twice uses \"an empty object {} as a unique identifier\": token identifies \"which register call,\" identity identifies \"which specific registration,\" leveraging {} !== {} (reference inherently unique). Discuss this trick's pros/cons versus \"generating a UUID string\" (uniqueness, performance, serializability, cross-process). Where does it fit, and where does it break down (e.g. when the identifier must be written to a log or database)?"},
        ],
    },
    "36-tool-definition.html": {
        "mcq": [
            {
                "q": {"zh": "opencode 里「定义一个工具」靠的是什么？", "en": "What is \"defining a tool\" in opencode based on?"},
                "opts": [
                    {"zh": "填一张 Tool.make 的 Config 表：description（给模型读）+ input/output（schema）+ execute（干活）+ 可选 toModelOutput——每个工具都填这同一张表", "en": "Filling a Tool.make Config form: description (read by the model) + input/output (schema) + execute (do work) + optional toModelOutput — every tool fills this same form"},
                    {"zh": "继承一个 BaseTool 抽象类、重写一堆方法", "en": "Subclassing a BaseTool abstract class and overriding many methods"},
                    {"zh": "在一个巨大的 switch 里加一个 case", "en": "Adding a case to one giant switch"},
                    {"zh": "写一个独立的微服务", "en": "Writing a standalone microservice"},
                ],
                "answer": 0,
                "why": {"zh": "Tool.make(config)（core/src/tool/tool.ts）是定义工具的唯一入口。Config 核心三件是 input/output/execute：声明「吃什么、吐什么、怎么算」，execute 签名 (input, context) => Effect<output, ToolFailure> 输入输出带类型、错误是值。这和第 29 课「每个协议填同一张两栏表」是同一种设计哲学——把共性钉成一张表，每个实例只管填空。read/bash/grep 千差万别，都在填这同一张 Config。", "en": "Tool.make(config) (core/src/tool/tool.ts) is the sole entry to defining a tool. Config's core three are input/output/execute: declaring \"what it takes, produces, how it computes,\" with execute's signature (input, context) => Effect<output, ToolFailure> typed I/O and errors-as-values. Same design philosophy as lesson 29's \"every protocol fills the two-column form\" — nail the commonality into one form, each instance just fills blanks. read/bash/grep, wildly different, all fill this same Config."},
            },
            {
                "q": {"zh": "一个工具的 input/output schema 同时承担哪几件事？", "en": "What does a tool's input/output schema do all at once?"},
                "opts": [
                    {"zh": "三件：① definition 转 JSON Schema 给模型当说明书；② settle 用 input schema 解码校验进来的参数；③ 用 output schema 编码校验出去的结果", "en": "Three: ① definition turns it into JSON Schema as the model's manual; ② settle decode-validates incoming params via the input schema; ③ encode-validates the outgoing result via the output schema"},
                    {"zh": "只用来生成 TypeScript 类型，运行时不参与", "en": "Only for generating TypeScript types, not involved at runtime"},
                    {"zh": "只用来写文档", "en": "Only for documentation"},
                    {"zh": "只校验输入，不管输出", "en": "Only validates input, ignores output"},
                ],
                "answer": 0,
                "why": {"zh": "同一份 schema 声明一次、三处把关：对外是给模型的说明书（definition→JSON Schema），对内是输入的安检门（decode）和输出的质检口（encode）。这是第 22 课「codec 一肩三役」在工具层的再现。关键收益在失败处理：模型传来不合 schema 的乱参数、工具吐出不合规结果，两种脏数据都被挡成一个规规矩矩的 ToolFailure 值，而非异常炸穿 agent 循环。schema 是工具与混沌世界之间的防线。", "en": "The same schema, declared once, guards three gates: outward the model's manual (definition→JSON Schema), inward the input's checkpoint (decode) and output's QC (encode). A recurrence of lesson 22's \"codec wears three hats\" at the tool layer. The key payoff is failure handling: the model passing schema-violating params, a tool spitting non-conforming output — both dirty-data kinds are stopped into a well-behaved ToolFailure value, not an exception blasting the agent loop. The schema is the tool's line of defense against a chaotic world."},
            },
            {
                "q": {"zh": "Tool.make 返回的「工具」其实是 Object.freeze({})（冻结的空对象），真正的行为藏在模块级 WeakMap 里。为什么这么设计？", "en": "Tool.make's returned \"tool\" is actually Object.freeze({}) (a frozen empty object), the real behavior hidden in a module-level WeakMap. Why this design?"},
                "opts": [
                    {"zh": "让工具成为不可篡改的「能力凭证」：只能交给 Tool.settle/definition 用；withPermission 派生新句柄而非改原值；类型层只剩 Input/Output 幽灵参数、运行时脏活不污染类型", "en": "Make the tool an immutable \"capability token\": only usable via Tool.settle/definition; withPermission derives a new handle instead of mutating; the type layer has only phantom Input/Output params, runtime grunt work not polluting types"},
                    {"zh": "纯粹是个 bug", "en": "Purely a bug"},
                    {"zh": "为了节省内存", "en": "To save memory"},
                    {"zh": "因为 TypeScript 不支持类", "en": "Because TypeScript doesn't support classes"},
                ],
                "answer": 0,
                "why": {"zh": "返回空对象、行为入 WeakMap，一次买齐三件好事：① 不可篡改——拿到工具改不了它的行为，只能照规矩用；② 装饰即新值——withPermission 派生一把新钥匙牌指向增强 Runtime，原工具纹丝不动（不可变思维）；③ 类型与运行时分离——类型层只剩 Input/Output 两个幽灵参数供编译器对齐，运行时藏在 WeakMap 不污染类型。WeakMap 还附带：工具被 GC 时 Runtime 自动释放，无泄漏。withPermission 正是第 41 课权限系统的接入点。", "en": "Returning an empty object with behavior in a WeakMap buys three goods at once: ① immutability — holders can't change a tool's behavior, only use it by the rules; ② decoration yields a new value — withPermission derives a new key tag pointing at the enhanced Runtime, the original untouched (immutable thinking); ③ types/runtime separated — the type layer keeps only the two phantom Input/Output params for the compiler to align, runtime hidden in the WeakMap without polluting types. WeakMap also throws in: a GC'd tool's Runtime auto-releases, no leak. withPermission is exactly lesson 41's permission plug-in point."},
            },
        ],
        "open": [
            {"zh": "课里说 settle 吐出两份——structured（给系统归档的结构化值）和 content（给模型读的 text/file），并把它们刻意解耦：「系统要记的」和「模型该看的」常常不是一回事（如文件读取：结构化里有字节数/行号/编码，给模型只需内容本身）。请结合你设计过的接口，谈谈「同一次操作的结果，对内详尽、对外精炼」这种双输出为什么有用？它和第 42 课「有界工具输出」会怎样配合？", "en": "The lesson says settle emits two copies—structured (the structured value filed for the system) and content (text/file read by the model)—deliberately decoupled: \"what the system records\" and \"what the model should see\" are often not the same (e.g. file-read: structured has byte counts/line numbers/encoding, the model needs only the content). From an interface you've designed, discuss why this dual output of \"detailed inward, concise outward for the same operation's result\" is useful. How would it cooperate with lesson 42's \"bounded tool output\"?"},
            {"zh": "课里把工具的 execute 签名 (input, context) => Effect<output, ToolFailure> 和第 29 课协议的「两栏表」相提并论，都是「把一类东西的共性钉成一张表，让每个实例只管填空」。请再举两个你熟悉的、用「同一张表/同一个接口、各自填空」来统一一族实现的例子（如插件系统、Web 中间件、数据库驱动）。这种「定义一张共同的形」相比「每个实现各搞一套」，在新增、测试、复用上分别带来什么好处？", "en": "The lesson likens a tool's execute signature (input, context) => Effect<output, ToolFailure> to lesson 29's protocol \"two-column form,\" both \"nailing a category's commonality into one form so each instance just fills blanks.\" Give two more examples you know of unifying a family of implementations via \"the same form/interface, each filling blanks\" (e.g. plugin systems, web middleware, database drivers). Versus \"each implementation doing its own thing,\" what does \"defining one common shape\" buy for adding, testing, and reuse respectively?"},
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
