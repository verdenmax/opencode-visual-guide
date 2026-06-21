"""Part 2 (Part 2 · Effect Foundations) content. Placeholders until M2 fills them in."""
from placeholder import wip

LESSON_05 = {
    "zh": r"""
<p class="lead">从这一课起，我们要去补 V2 的<strong>地基</strong>——Effect。你打开 <span class="mono">packages/core</span> 会发现满屏都是 <span class="mono">Effect.gen</span>、<span class="mono">yield*</span>、<span class="mono">Layer</span> 这些陌生写法，不先搞懂它们，后面的会话引擎、上下文系统根本读不下去。但这一课先不急着学语法，而是回答一个更重要的问题：<strong>opencode 为什么要费这么大劲引入 Effect？</strong>想清楚"为什么"，再学"怎么用"，你才不会把它当成又一个要硬记的框架。</p>
<p>说句实在话：很多人读 opencode 卡在 <span class="mono">packages/core</span>，不是因为业务逻辑难，而是因为<strong>没先理解 Effect 想解决什么</strong>，于是把满屏的 <span class="mono">yield*</span> 和 <span class="mono">Layer</span> 当成天书硬啃。所以这一课我们刻意<strong>慢一拍</strong>——先一行语法都不教，只把"为什么非它不可"讲透。等你打心底认同了"普通写法确实扛不住 agent 这种复杂度"，再回头去学 Service、Layer、Fiber，它们就不再是要硬记的负担，而是一件件<strong>趁手的工具</strong>，每一件都解你一个具体的痛。学一个重框架，本该是这个顺序。</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  普通代码像<strong>直接开火炒菜</strong>：你站在灶台前，抓起锅就炒，火候、放盐、翻面全凭手感，一边炒一边出状况——糊了？当场手忙脚乱。Effect 则像<strong>先写一张详细菜谱</strong>：你不立刻动手，而是先把整道菜<strong>写成一张纸</strong>，连"万一糊了怎么补救""需要哪些食材""能不能同时开三个灶"都写进去；这张纸是个<strong>可以传阅、可以修改、可以复用</strong>的东西，最后才在灶边照着它执行一次。"先描述、再执行"这一步之差，正是 Effect 全部威力的来源。菜谱还有个妙处：它能被<strong>复用和改写</strong>——同一张谱子，今天用真食材做、明天换替代品试，主体一字不改。Effect 值也一样，写一次，真实环境和测试环境都能照着跑。
</div>

<h2>agent 代码的四样难题</h2>
<p>一个 AI 编程 agent 的核心逻辑，天生就同时缠着四样最难对付的东西。它们不是偶尔冒头，而是<strong>每一步都在</strong>：</p>
<div class="cols">
  <div class="col"><h4>① 副作用</h4><p>读写文件、发网络请求、起子进程……几乎每个动作都在<strong>改变外部世界</strong>，没有一处是"纯函数"。</p></div>
  <div class="col"><h4>② 错误</h4><p>provider 挂了、工具跑失败、用户中途打断……<strong>失败是常态</strong>，而且种类繁多。</p></div>
  <div class="col"><h4>③ 并发</h4><p>一步里要同时跑好几个工具，还得能<strong>干净地取消</strong>——某个慢了、用户喊停，都要稳稳收住。</p></div>
  <div class="col"><h4>④ 依赖</h4><p>处处要用到配置、数据库、模型目录……这些<strong>外部依赖</strong>缠绕在每一层逻辑里。</p></div>
</div>
<p>难就难在<strong>四样同时来</strong>。单独对付任何一个都不算事，但当"有副作用、可能失败、要并发、还依赖一堆东西"全压在一个函数上时，用普通的写法，你会发现自己在和语言<strong>对抗</strong>，而不是被它<strong>托住</strong>。</p>
<p>更麻烦的是，这四样还会<strong>互相放大</strong>：并发地跑多个有副作用的操作，其中一个失败了，你不仅要处理这个错误，还要<strong>取消其余正在跑的</strong>、并<strong>清理它们已经打开的资源</strong>——错误、并发、副作用、资源四件事在这一瞬间全缠在一起。这种"复合难题"用普通写法去对付，写出来的往往是一堆嵌套的 <span class="mono">try</span>、手动的取消标志位、和提心吊胆的清理代码，又长又脆。而 agent 每一轮工具执行，几乎都在面对这种复合场景——这正是 opencode 觉得"必须换个地基"的起点。</p>

<h2>普通写法，悄悄藏起了什么</h2>
<p>用最朴素的 <span class="mono">async/await</span> + <span class="mono">try/catch</span> 写上面这些，问题不是"写不出来"，而是太多关键信息<strong>从类型里消失了</strong>，编译器帮不上忙：</p>
<table class="t">
  <tr><th>难题</th><th>普通写法把它藏在哪</th></tr>
  <tr><td>错误</td><td><span class="mono">catch (e)</span> 里的 <span class="mono">e</span> 类型是 <span class="mono">unknown</span>——<strong>编译器忘了这里会失败、会怎样失败</strong>，你也很容易忘记去 catch。</td></tr>
  <tr><td>依赖</td><td>直接 <span class="mono">import</span> 一个全局单例或满天飞的参数——<strong>想换成测试假实现</strong>？几乎不可能。</td></tr>
  <tr><td>并发</td><td>手写 <span class="mono">Promise.all</span> + 手动记着取消——一旦要"某个失败就全取消"，逻辑立刻打结。</td></tr>
  <tr><td>资源</td><td>靠 <span class="mono">try/finally</span> 手动关——<strong>漏关一个</strong>，就是一个泄漏。</td></tr>
</table>
<p>核心痛点是：这些信息<strong>明明至关重要，却没写进类型</strong>。于是它们变成了"你必须时刻在脑子里记着、一旦忘了编译器也不会提醒"的隐形负担。代码越大，这种负担越致命——而 agent 的会话引擎，恰恰是 opencode 里最大、最关键的一块。</p>
<p>举个具体例子最能说明问题。假设一个工具函数会有"网络超时"和"返回格式错误"两种失败，普通写法里你 <span class="mono">catch</span> 到的只是一个 <span class="mono">unknown</span>，到底是哪种、该重试还是该直接报错，全得你在运行时用 <span class="mono">if</span> 去猜；更糟的是，如果某个调用方<strong>忘了 catch</strong>，编译器一声不吭，错误就一路冒泡，可能在某个完全不相干的地方把整个会话搞崩。"会失败"这件事如此重要，却得不到类型系统一丝一毫的保护——这就是普通写法在大型有状态系统里最致命的软肋，也是 bug 最爱藏身的地方。</p>

<h2>Effect 的核心一招：先描述，再运行</h2>
<p>Effect 的破解之道，听起来近乎哲学，却极其实用：<strong>不要立刻"运行"一段计算，而是先把它"描述"成一个值。</strong></p>
<p>普通函数你一调用，它<strong>当场就跑</strong>了，副作用立刻发生，错误当场抛出。Effect 不是——你写出的是一个 <span class="mono">Effect</span> <strong>值</strong>，它只是"<strong>一段计算的说明书</strong>"，描述了"将来运行时会做什么、可能产出什么、可能怎样失败、需要什么"。它本身<strong>什么都还没做</strong>。</p>
<div class="flow">
  <div class="node"><div class="nt">描述</div><div class="nd">写出一个 Effect 值</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">组合</div><div class="nd">map / retry / race / 注入依赖</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">在边缘运行一次</div><div class="nd">runPromise</div></div>
</div>
<p>因为它只是个值，你就能在<strong>真正运行之前</strong>，对它任意加工：给它套上重试、和别的 Effect 赛跑（race）、把依赖注进去、组合成更大的 Effect……直到最后，才在程序的<strong>最外层边缘</strong>把它运行一次。这一步"延迟"，把"做什么"和"何时做、怎么做"彻底分开了——而这正是掌控复杂度的关键。</p>
<p>"延迟执行"听着抽象，好处却非常具体。因为 Effect 值在运行前只是一张说明书，你能对它做<strong>普通代码做不到的事</strong>：给任意一段计算<strong>统一套上重试</strong>而不改它内部一行；让两个计算<strong>赛跑</strong>、谁先完成用谁、另一个自动取消；把"需要数据库"这件事<strong>推迟到最外层</strong>再决定用真库还是测试库。普通代码一旦 <span class="mono">await</span> 就木已成舟，而 Effect 把"组装计划"和"按下执行键"分开了，于是<strong>整个计划在执行前都还能重新编排</strong>。这种可编排性，正是应付 agent 那种随时可能变向的流程的底气。</p>

<h2>类型里的三个格子：A / E / R</h2>
<p>这张说明书的类型，写作 <span class="mono">Effect&lt;A, E, R&gt;</span>，三个格子缺一不可，而它们正好对上了前面的难题：</p>
<div class="cellgroup">
  <div class="cg-cap"><b>Effect&lt;A, E, R&gt;</b>：一段"将来运行时"的计算说明书</div>
  <div class="cells">
    <span class="cell scale">A</span><span class="lab">成功时产出的值（success）</span>
  </div>
  <div class="cells">
    <span class="cell q">E</span><span class="lab">可能的<strong>类型化错误</strong>——编译器知道这里会怎样失败，逼你处理</span>
  </div>
  <div class="cells">
    <span class="cell">R</span><span class="lab">需要的<strong>依赖/服务</strong>——把"它要用什么"写进类型，可替换、可注入</span>
  </div>
</div>
<p>关键就在 <strong>E</strong> 和 <strong>R</strong>。普通写法里被藏起来的"会怎样失败"和"依赖什么"，Effect 把它们<strong>抬到了类型签名里</strong>：错误成了类型的一部分，编译器会<strong>逼你处理</strong>，不再有"忘了 catch"；依赖也成了类型的一部分，于是测试时<strong>换个假实现</strong>就是顺理成章的事。前面四样难题里最棘手的两样，就这样被收进了类型系统。</p>
<table class="t">
  <tr><th>类型格子</th><th>普通写法</th><th>Effect</th></tr>
  <tr><td>成功值</td><td>函数返回类型</td><td>A（一样清楚）</td></tr>
  <tr><td>会怎样失败</td><td>藏进 <span class="mono">unknown</span></td><td><strong>E：写进类型，逼你处理</strong></td></tr>
  <tr><td>需要什么依赖</td><td>隐式 import / 全局</td><td><strong>R：写进类型，可注入替换</strong></td></tr>
</table>
<p>单说 <strong>R</strong> 这个格子，威力常被低估。把"我需要 Config、需要 Database、需要模型目录"写进类型后，一段逻辑<strong>不再自己去 import 全局单例</strong>，而是声明"给我这些服务我才能跑"。于是测试时，你只要<strong>注入一套假服务</strong>（假数据库、固定配置），就能在不碰真实文件、不连真实网络的情况下，把这段逻辑单独验透。V1 的巨石之所以难测，正因为依赖是写死、藏在 import 里的；V2 把依赖搬进 R，<strong>可测试性</strong>几乎是白送的副产品。</p>

<h2>它到底给 V2 换来什么</h2>
<p>把"先描述、错误和依赖进类型"这套落到 opencode，就换来了四样 V1 很难补上的能力：</p>
<div class="vflow">
  <div class="step"><b>类型化错误</b>　用 <span class="mono">Schema.TaggedErrorClass</span> 把每种失败写成值，编译器替你盯着</div>
  <div class="step"><b>依赖注入</b>　用 <span class="mono">Context.Service</span> + <span class="mono">Layer</span> 声明依赖，真实/测试实现随手换（第 6 课）</div>
  <div class="step"><b>结构化并发</b>　用 <span class="mono">Fiber</span> / <span class="mono">FiberSet</span> 并发跑工具、干净取消（第 7 课，正是 agent 循环的做法）</div>
  <div class="step"><b>资源安全</b>　用 <span class="mono">acquireRelease</span> / <span class="mono">Scope</span> 保证打开的东西一定关上</div>
</div>
<p>这四样，恰好一一对上了"agent 四难题"。这也是为什么 V2 的会话引擎读起来和 V1 那种命令式巨石<strong>气质完全不同</strong>——不是风格偏好，而是 Effect 这套地基决定了上层只能、也应该长成那个样子。接下来第 6、7、8 课，就分别去拆 Service/Layer、并发原语、和项目里的 Effect 工具箱。</p>
<p>最后值得强调：Effect 不是为了"显得高级"。它每一个机制，都精准地对着 agent 的一个具体痛点而来——正因为要并发跑工具又要能取消，才需要 Fiber；正因为失败种类繁多又不能漏，才需要类型化错误；正因为要能脱离真实环境做测试，才需要把依赖搬进类型。<strong>是先有痛点，才有 Effect</strong>，而不是反过来。带着这个视角去读后面三课，你会发现每个看似抽象的概念背后，都站着一个很具体的工程问题——这也是读懂 V2 一切设计的正确姿势。</p>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  AI 编程 agent 的核心逻辑天生缠着<strong>副作用、错误、并发、依赖</strong>四样难题，而普通 <span class="mono">async/await + try/catch</span> 把后两样<strong>藏出了类型</strong>，全靠你脑子记。Effect 的破解之道是<strong>先把计算描述成一个值</strong> <span class="mono">Effect&lt;A, E, R&gt;</span>——成功值 A、<strong>类型化错误 E</strong>、<strong>依赖 R</strong> 都写进类型，先组合、最后在边缘运行一次。这把复杂度从"脑子记"挪进了"编译器管"，正是 V2 选 Effect 的根本原因。说到底，Effect 是一种<strong>把隐性负担变成显性类型</strong>的世界观——凡是你原本要靠脑子记、靠纪律守的东西（会不会失败、依赖了谁、谁来收尾），它都尽量挪进类型、交给编译器去盯。理解了这一层，你就握住了读懂整个 V2 内核的总钥匙，后面三课不过是把这把钥匙的齿纹一道道看清。
</div>

<div class="card detail">
  <div class="tag">🔬 细节 / 源码对应</div>
  同一段"读配置再干活"，对比普通写法和 Effect（<span class="mono">packages/core</span> 全程用 Effect，风格由 <span class="mono">AGENTS.md</span> 明文规定）：
<pre class="code"><span class="cm">// 普通：错误和依赖都不在类型里</span>
<span class="kw">import</span> { config } <span class="kw">from</span> <span class="st">"./globals"</span>   <span class="cm">// 依赖：隐式全局，测试难换</span>
<span class="kw">try</span> {
  <span class="kw">const</span> r = <span class="kw">await</span> <span class="fn">doWork</span>(config)
} <span class="kw">catch</span> (e) { <span class="cm">/* e: unknown —— 会怎样失败？没人知道 */</span> }

<span class="cm">// Effect：错误进 E、依赖进 R，编译器替你盯着</span>
<span class="kw">const</span> program = Effect.<span class="fn">gen</span>(<span class="kw">function*</span> () {
  <span class="kw">const</span> cfg = <span class="kw">yield</span>* Config        <span class="cm">// 依赖显式：R 里就有 Config</span>
  <span class="kw">return</span> <span class="kw">yield</span>* <span class="fn">doWork</span>(cfg)      <span class="cm">// 失败类型进 E，必须被处理</span>
})  <span class="cm">// program: Effect&lt;Result, WorkError, Config&gt;，到边缘才 runPromise</span></pre>
  <span class="mono">AGENTS.md</span> 明文要求："用 <span class="mono">Effect.gen</span> 组合""用 <span class="mono">Schema.TaggedErrorClass</span> 写错误""尽量避免 <span class="mono">try/catch</span>"。
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>agent 核心逻辑天生缠着<strong>副作用、错误、并发、依赖</strong>四样难题。</li>
    <li>普通 <span class="mono">async/await + try/catch</span> 把<strong>错误类型和依赖藏出了类型</strong>，全靠脑子记。</li>
    <li>Effect 的核心一招：<strong>先把计算描述成一个值</strong>，组合好，最后在边缘运行一次。</li>
    <li><span class="mono">Effect&lt;A, E, R&gt;</span>：成功值 A、<strong>类型化错误 E</strong>、<strong>依赖 R</strong> 都进类型。</li>
    <li>它给 V2 换来类型化错误、依赖注入、结构化并发、资源安全——正对四难题。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">From here, we lay V2's <strong>foundation</strong> — Effect. Open <span class="mono">packages/core</span> and you'll see screens of unfamiliar <span class="mono">Effect.gen</span>, <span class="mono">yield*</span>, <span class="mono">Layer</span>; without grasping these, the session engine and context system are unreadable. But this lesson doesn't rush into syntax — it answers a more important question first: <strong>why did opencode go to such lengths to adopt Effect?</strong> Understand the "why," then learn the "how," and you won't treat it as yet another framework to memorize.</p>
<p>Honestly: many people stall in <span class="mono">packages/core</span> not because the business logic is hard, but because they <strong>didn't first understand what Effect is for</strong>, so the screens of <span class="mono">yield*</span> and <span class="mono">Layer</span> read like gibberish. So this lesson deliberately <strong>slows down</strong> — teaching not one line of syntax, only making "why it has to be this" crystal clear. Once you genuinely agree that "plain code can't carry an agent's complexity," learning Service, Layer, Fiber later feels not like a burden but like a set of <strong>handy tools</strong>, each solving one concrete pain. That's the right order to learn a heavy framework.</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  Plain code is like <strong>cooking on the fly</strong>: you stand at the stove, grab the pan, and cook — heat, salt, flipping all by feel, troubleshooting mid-cook; burnt it? You scramble on the spot. Effect is like <strong>first writing a detailed recipe</strong>: you don't act immediately, you write the whole dish down <strong>on paper</strong> — including "what if it burns (errors), which ingredients are needed (deps), can I run three burners at once (concurrency)"; that paper is something you can <strong>pass around, edit, and reuse</strong>, and only at the very end do you cook once by following it. "Describe first, then run" — that one step's difference is the source of all of Effect's power. A recipe has another perk: it's <strong>reusable and rewritable</strong> — the same recipe, made with real ingredients today and substitutes tomorrow, its body unchanged. An Effect value is the same: write once, run it in both real and test environments.
</div>

<h2>An agent's code: four hard things at once</h2>
<p>An AI coding agent's core logic is natively tangled with the four hardest things to handle. They don't appear occasionally — they're present at <strong>every step</strong>:</p>
<div class="cols">
  <div class="col"><h4>① Side effects</h4><p>Reading/writing files, network requests, spawning processes… almost every action <strong>changes the outside world</strong>; nothing is a "pure function."</p></div>
  <div class="col"><h4>② Errors</h4><p>The provider is down, a tool fails, the user interrupts mid-run… <strong>failure is the norm</strong>, and of many kinds.</p></div>
  <div class="col"><h4>③ Concurrency</h4><p>One step runs several tools at once, and must <strong>cancel cleanly</strong> — one stalls, the user stops, you must wind down safely.</p></div>
  <div class="col"><h4>④ Dependencies</h4><p>Config, the database, the model catalog needed everywhere… these <strong>external deps</strong> wind through every layer.</p></div>
</div>
<p>The hard part is <strong>all four arriving together</strong>. Any one alone is fine; but when "has side effects, can fail, needs concurrency, and depends on a pile of things" all press on one function, with plain code you find yourself <strong>fighting</strong> the language rather than being <strong>held up</strong> by it.</p>
<p>Worse, these four <strong>amplify each other</strong>: run several side-effecting operations concurrently, one fails, and you must not only handle that error but also <strong>cancel the others still running</strong> and <strong>clean up the resources they already opened</strong> — errors, concurrency, side effects, and resources all tangled in one instant. Tackled with plain code, this "compound problem" tends to produce nested <span class="mono">try</span>s, manual cancellation flags, and anxious cleanup code — long and fragile. And every round of an agent's tool execution faces exactly this compound scenario — the very starting point for opencode deciding it "needs a new foundation."</p>

<h2>What plain code quietly hides</h2>
<p>Writing the above with plain <span class="mono">async/await</span> + <span class="mono">try/catch</span>, the problem isn't "you can't write it," but that too much crucial information <strong>vanishes from the types</strong>, so the compiler can't help:</p>
<table class="t">
  <tr><th>Difficulty</th><th>Where plain code hides it</th></tr>
  <tr><td>Errors</td><td>The <span class="mono">e</span> in <span class="mono">catch (e)</span> is typed <span class="mono">unknown</span> — <strong>the compiler forgot this can fail, and how</strong>, and it's easy to forget to catch.</td></tr>
  <tr><td>Dependencies</td><td>A directly-<span class="mono">import</span>ed global singleton or args everywhere — <strong>swap in a test fake?</strong> Nearly impossible.</td></tr>
  <tr><td>Concurrency</td><td>Hand-rolled <span class="mono">Promise.all</span> + remembering to cancel — once "cancel all if one fails" is needed, the logic knots up.</td></tr>
  <tr><td>Resources</td><td>Manual <span class="mono">try/finally</span> — <strong>miss one close</strong> and that's a leak.</td></tr>
</table>
<p>The core pain: this info is <strong>clearly crucial yet not written into the types</strong>. So it becomes "an invisible burden you must keep in your head at all times, and the compiler won't remind you if you forget." The bigger the code, the more fatal this gets — and an agent's session engine is precisely opencode's biggest, most critical piece.</p>
<p>A concrete example makes it vivid. Suppose a tool function can fail two ways — "network timeout" and "bad response format"; in plain code your <span class="mono">catch</span> gets only an <span class="mono">unknown</span>, and which one it is, whether to retry or just report, you must guess at runtime with <span class="mono">if</span>; worse, if some caller <strong>forgets to catch</strong>, the compiler stays silent, the error bubbles up, and may crash the whole session somewhere totally unrelated. "Can fail" is so important, yet gets not a shred of protection from the type system — that's plain code's most fatal weakness in a large stateful system, and where bugs love to hide.</p>

<h2>Effect's core move: describe first, run later</h2>
<p>Effect's solution sounds almost philosophical yet is intensely practical: <strong>don't "run" a computation immediately; first "describe" it as a value.</strong></p>
<p>Call a plain function and it <strong>runs on the spot</strong> — side effects happen at once, errors throw at once. Effect doesn't — what you write is an <span class="mono">Effect</span> <strong>value</strong>, just "<strong>a spec for a computation</strong>" describing "what it will do when run, what it may produce, how it may fail, what it needs." It has <strong>done nothing yet</strong>.</p>
<div class="flow">
  <div class="node"><div class="nt">describe</div><div class="nd">write an Effect value</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">compose</div><div class="nd">map / retry / race / inject deps</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">run once at the edge</div><div class="nd">runPromise</div></div>
</div>
<p>Because it's just a value, <strong>before it actually runs</strong> you can work on it freely: wrap it in retries, race it against another Effect (first done wins, the other auto-cancels), inject its dependencies, compose it into a bigger Effect… until finally you run it once at the program's <strong>outermost edge</strong>. That one "deferral" cleanly separates "what to do" from "when and how to do it" — and that's the key to taming complexity.</p>
<p>"Deferred execution" sounds abstract but the payoff is very concrete. Because an Effect value is just a spec before running, you can do things <strong>plain code can't</strong>: <strong>uniformly wrap any computation in retries</strong> without touching one line inside it; <strong>race</strong> two computations, use whoever finishes first, auto-cancel the other; <strong>defer "needs a database" to the outermost layer</strong> to decide real vs test DB. Plain code, once it <span class="mono">await</span>s, is set in stone; Effect splits "assembling the plan" from "pressing the run button," so <strong>the whole plan stays re-arrangeable until it runs</strong>. That re-arrangeability is exactly the confidence for handling an agent's ever-shifting flows.</p>

<h2>Three slots in the type: A / E / R</h2>
<p>This spec's type is written <span class="mono">Effect&lt;A, E, R&gt;</span>; all three slots are essential, and they line up exactly with the earlier difficulties:</p>
<div class="cellgroup">
  <div class="cg-cap"><b>Effect&lt;A, E, R&gt;</b>: a spec for a "to-be-run" computation</div>
  <div class="cells">
    <span class="cell scale">A</span><span class="lab">the value produced on success</span>
  </div>
  <div class="cells">
    <span class="cell q">E</span><span class="lab">the possible <strong>typed errors</strong> — the compiler knows how it can fail and forces you to handle it</span>
  </div>
  <div class="cells">
    <span class="cell">R</span><span class="lab">the required <strong>deps/services</strong> — "what it needs" is in the type, swappable, injectable</span>
  </div>
</div>
<p>The key is <strong>E</strong> and <strong>R</strong>. The "how it can fail" and "what it depends on" that plain code hides, Effect <strong>lifts into the type signature</strong>: errors become part of the type and the compiler <strong>forces you to handle them</strong> — no more "forgot to catch"; dependencies become part of the type, so <strong>swapping a fake</strong> in tests is natural. The two thorniest of the four difficulties are thus folded into the type system.</p>
<table class="t">
  <tr><th>Type slot</th><th>Plain code</th><th>Effect</th></tr>
  <tr><td>Success value</td><td>function return type</td><td>A (just as clear)</td></tr>
  <tr><td>How it can fail</td><td>hidden in <span class="mono">unknown</span></td><td><strong>E: in the type, forces handling</strong></td></tr>
  <tr><td>What deps it needs</td><td>implicit import / global</td><td><strong>R: in the type, injectable/swappable</strong></td></tr>
</table>
<p>The <strong>R</strong> slot alone is often underrated. Once "I need Config, Database, the model catalog" is in the type, a piece of logic <strong>no longer imports a global singleton itself</strong> but declares "give me these services and I'll run." So in tests you just <strong>inject a set of fakes</strong> (fake DB, fixed config) and verify that logic thoroughly without touching real files or networks. V1's monoliths are hard to test precisely because deps are hard-wired, hidden in imports; V2 moves deps into R, and <strong>testability</strong> comes almost free as a byproduct.</p>

<h2>What it actually buys V2</h2>
<p>Land "describe-first, errors-and-deps-in-the-type" onto opencode and it buys four capabilities V1 can hardly retrofit:</p>
<div class="vflow">
  <div class="step"><b>Typed errors</b>　<span class="mono">Schema.TaggedErrorClass</span> writes each failure as a value; the compiler watches for you</div>
  <div class="step"><b>Dependency injection</b>　<span class="mono">Context.Service</span> + <span class="mono">Layer</span> declare deps; real/test impls swap freely (Lesson 6)</div>
  <div class="step"><b>Structured concurrency</b>　<span class="mono">Fiber</span> / <span class="mono">FiberSet</span> run tools concurrently and cancel cleanly (Lesson 7 — exactly how the agent loop runs tools)</div>
  <div class="step"><b>Resource safety</b>　<span class="mono">acquireRelease</span> / <span class="mono">Scope</span> guarantee what's opened gets closed</div>
</div>
<p>These four line up one-to-one with the "four agent difficulties." That's why V2's session engine reads with a <strong>completely different temperament</strong> from V1's imperative monoliths — not a style preference, but Effect as a foundation dictating that the upper layers can and should grow that way. Lessons 6, 7, 8 next take apart Service/Layer, concurrency primitives, and the project's Effect toolbox respectively.</p>
<p>Finally, stress this: Effect isn't about "looking advanced." Each of its mechanisms targets one concrete agent pain — because you must run tools concurrently and cancel them, you need Fiber; because failures are many and must not be missed, you need typed errors; because you must test away from the real environment, you need deps in the type. <strong>The pain comes first, then Effect</strong>, not the reverse. Read the next three lessons with this lens and you'll find a concrete engineering problem standing behind every seemingly abstract concept — the right posture for understanding all of V2's design.</p>

<div class="card macro">
  <div class="tag">🌍 Big picture</div>
  An AI coding agent's core logic is natively tangled with four difficulties — <strong>side effects, errors, concurrency, dependencies</strong> — and plain <span class="mono">async/await + try/catch</span> <strong>hides the last two out of the types</strong>, leaving them to your memory. Effect's fix is to <strong>describe the computation as a value first</strong>, <span class="mono">Effect&lt;A, E, R&gt;</span> — success A, <strong>typed error E</strong>, <strong>deps R</strong> all in the type, compose first, run once at the edge. This moves complexity from "your head" to "the compiler," the root reason V2 chose Effect. Ultimately Effect is a worldview of <strong>turning implicit burdens into explicit types</strong> — whatever you'd otherwise track by memory or discipline (can it fail, who it depends on, who cleans up), it moves into the type for the compiler to watch. Grasp this and you hold the master key to the whole V2 kernel; the next three lessons just trace its teeth one by one.
</div>

<div class="card detail">
  <div class="tag">🔬 Source detail</div>
  The same "read config then work," plain vs Effect (<span class="mono">packages/core</span> uses Effect throughout, the style mandated by <span class="mono">AGENTS.md</span>):
<pre class="code"><span class="cm">// Plain: errors and deps aren't in the type</span>
<span class="kw">import</span> { config } <span class="kw">from</span> <span class="st">"./globals"</span>   <span class="cm">// dep: implicit global, hard to swap in tests</span>
<span class="kw">try</span> {
  <span class="kw">const</span> r = <span class="kw">await</span> <span class="fn">doWork</span>(config)
} <span class="kw">catch</span> (e) { <span class="cm">/* e: unknown — how can it fail? nobody knows */</span> }

<span class="cm">// Effect: error goes in E, dep goes in R, the compiler watches for you</span>
<span class="kw">const</span> program = Effect.<span class="fn">gen</span>(<span class="kw">function*</span> () {
  <span class="kw">const</span> cfg = <span class="kw">yield</span>* Config        <span class="cm">// dep explicit: Config is in R</span>
  <span class="kw">return</span> <span class="kw">yield</span>* <span class="fn">doWork</span>(cfg)      <span class="cm">// failure type goes in E, must be handled</span>
})  <span class="cm">// program: Effect&lt;Result, WorkError, Config&gt;, runPromise only at the edge</span></pre>
  <span class="mono">AGENTS.md</span> mandates it: "Use <span class="mono">Effect.gen</span> for composition", "Use <span class="mono">Schema.TaggedErrorClass</span> for typed errors", "Avoid <span class="mono">try/catch</span> where possible."
</div>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>An agent's core logic is natively tangled with <strong>side effects, errors, concurrency, dependencies</strong>.</li>
    <li>Plain <span class="mono">async/await + try/catch</span> <strong>hides error types and deps out of the types</strong>, leaving them to memory.</li>
    <li>Effect's core move: <strong>describe the computation as a value first</strong>, compose, then run once at the edge.</li>
    <li><span class="mono">Effect&lt;A, E, R&gt;</span>: success A, <strong>typed error E</strong>, <strong>deps R</strong> all in the type.</li>
    <li>It buys V2 typed errors, dependency injection, structured concurrency, resource safety — matching the four difficulties.</li>
  </ul>
</div>
""",
}
LESSON_06 = {
    "zh": r"""
<p class="lead">上一课我们说：Effect 把"依赖"写进了类型的 <strong>R</strong> 槽。但话只说了一半——光声明"我需要 Config"还不够，总得有人<strong>真的把一个 Config 递进来</strong>。这一课就讲 opencode 里这套"声明依赖、再注入依赖"的机制：<strong>Service</strong> 负责声明一个能力插槽，<strong>Layer</strong> 负责把插槽接上真正的实现。读懂这两个词，<span class="mono">packages/core</span> 里那种"满屏 <span class="mono">yield* XxxService</span>、最后用 <span class="mono">Layer</span> 拼起来"的结构，就全通了。</p>
<p>这一课会有点"绕"，因为 Service 和 Layer 是一对<strong>互相成全</strong>的概念，单独看哪个都不完整。所以下面我们用"插座与布线"这个比喻贯穿全程：每读到一个新点，你都可以回到这个画面里对一对号。把这一对吃透，你就拿到了读 <span class="mono">packages/core</span> 的<strong>万能钥匙</strong>——因为那里几乎每一个模块，从 Agent、Database 到 LLM、Tool，都是照着 Service + Layer 这同一个模子刻出来的。学会读一个，就等于学会了读全部；反过来，要是这一对没吃透，你看每个模块都会觉得"似曾相识却又说不清"，那种卡顿感正是没认出模子的表现。</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  把 <strong>Service</strong> 想成墙上的一个<strong>标准插座</strong>：它只规定"这里能插一个提供电力的东西"，定义了形状和接口，却<strong>不关心电从哪来</strong>。把 <strong>Layer</strong> 想成<strong>布线施工</strong>：它真正把一台发电机（或市电、或一节电池）接到这个插座背后。你的电器（业务代码）只管说"我要插在电力插座上"，至于背后接的是发电机还是电池，<strong>由施工方决定、随时可换</strong>。Service 定义"需要什么"，Layer 决定"用什么满足"——两者一拆开，可替换性就来了。施工的好处还在于：你家电器永远不用关心墙后接的是市电还是太阳能，哪天想从市电切到自家光伏，<strong>动布线、不动电器</strong>。软件里这意味着：换实现的成本，被死死摁在了最外层那一处接线上，而不会渗进成百上千个用到它的地方。
</div>

<h2>Service：声明一个能力插槽</h2>
<p>在 opencode 里，一个 Service 就是一个<strong>带名字的能力契约</strong>。它用一个固定的写法声明出来：一个接口（这个能力能做什么），加一个全局唯一的<strong>标签</strong>（给它起个名字，让 Effect 能认出它）。</p>
<pre class="code"><span class="cm">// 简化自 packages/core/src/agent.ts</span>
<span class="kw">interface</span> Interface { <span class="fn">get</span>(id: string): Effect&lt;Agent&gt; }
<span class="kw">export class</span> Service <span class="kw">extends</span> Context.<span class="fn">Service</span>&lt;Service, Interface&gt;()(<span class="st">"@opencode/v2/Agent"</span>) {}</pre>
<p>关键就在那个字符串标签 <span class="mono">"@opencode/v2/Agent"</span>：它是这个插槽的<strong>全局身份证</strong>。当某段代码说"我需要 Agent 服务"时，Effect 就靠这个标签去找谁填了这个槽。注意此刻<strong>还没有任何实现</strong>——Service 只是个<strong>形状</strong>、一个承诺，就像墙上那个还没接线的插座。这一步把"<strong>需要什么</strong>"和"<strong>谁来提供</strong>"干净地分开了。</p>
<div class="cellgroup">
  <div class="cg-cap"><b>Context.Service&lt;Service, Interface&gt;()("@opencode/v2/Agent")</b> 三件套</div>
  <div class="cells"><span class="cell q">Interface</span><span class="lab">这个能力能做什么——方法签名的集合</span></div>
  <div class="cells"><span class="cell scale">标签字符串</span><span class="lab">全局唯一身份，Effect 靠它在运行时认出这个槽</span></div>
  <div class="cells"><span class="cell">Service 类</span><span class="lab">既当类型用（写进 R），又是运行时能 yield* 的"钥匙"</span></div>
</div>
<p>为什么要写成一个 <span class="mono">class</span>？因为它要<strong>身兼两职</strong>：在类型层面，<span class="mono">Service</span> 是个类型，被记进别人的 R；在运行时层面，它又是一个能 <span class="mono">yield*</span> 出来的值——一把"钥匙"，凭它去运行时的"账本"里取出对应实现。一个名字同时是类型和值，这正是 Effect 把"依赖"做得既类型安全、又能在运行时注入的关键设计。你不必记住它的全部魔法，只需认得这个固定骨架：<strong>一个接口 + 一个标签 + 一个 Service 类</strong>。</p>

<h2>Layer：把插槽接上真正的实现</h2>
<p>光有插槽不通电。<strong>Layer</strong> 就是那段"布线施工"，它把一个真正的实现<strong>绑定</strong>到 Service 标签上：</p>
<pre class="code"><span class="cm">// 简化自 packages/core/src/agent.ts</span>
<span class="kw">export const</span> layer = Layer.<span class="fn">effect</span>(
  Service,                          <span class="cm">// 填哪个槽</span>
  Effect.<span class="fn">gen</span>(<span class="kw">function*</span> () {        <span class="cm">// 怎么造出实现（本身也是一段 Effect）</span>
    <span class="kw">const</span> db = <span class="kw">yield</span>* Database     <span class="cm">// Layer 自己也能依赖别的 Service</span>
    <span class="kw">return</span> { <span class="fn">get</span>: (id) =&gt; <span class="cm">/* …用 db 实现… */</span> }
  }),
)</pre>
<p><span class="mono">Layer.effect(Service, make)</span> 读作："用 <span class="mono">make</span> 这段计算造出实现，把它装进 <span class="mono">Service</span> 这个槽"。妙的是 <span class="mono">make</span> 本身就是一段 Effect，所以<strong>一个 Layer 在构造时还能依赖别的 Service</strong>（上面就 <span class="mono">yield* Database</span>）。于是 Layer 之间能像积木一样<strong>层层堆叠</strong>：Agent 依赖 Database，Database 依赖 Config……每一层只管声明自己要什么、产出什么。</p>
<table class="t">
  <tr><th></th><th>Service</th><th>Layer</th></tr>
  <tr><td>是什么</td><td>能力的<strong>契约</strong>（接口 + 标签）</td><td>契约的<strong>实现 + 接线</strong></td></tr>
  <tr><td>类比</td><td>墙上的插座（形状）</td><td>把发电机接到插座背后的布线</td></tr>
  <tr><td>关心</td><td>"能做什么"</td><td>"怎么造出来、依赖谁"</td></tr>
  <tr><td>可替换性</td><td>消费方只认它</td><td>随时换一套（真/假实现）</td></tr>
</table>
<p>把 Service 和 Layer 分成两个东西，而不是揉成一个"类 + new 出实例"，正是整套设计的精髓所在。因为消费方只依赖 <strong>Service（契约）</strong>，谁来当 <strong>Layer（实现）</strong>就成了一个能在最外层自由决定的旋钮。这种"契约与实现分离"在传统 OOP 里要靠接口 + 依赖注入框架费力搭，而 Effect 把它做成了<strong>语言级、类型安全</strong>的一等公民——这也是为什么 opencode 几乎每个模块都严格遵循这个骨架。</p>
<p>还有一个常被忽略的好处：因为 Layer 的构造本身是一段 Effect，它<strong>也能失败、也能依赖别人</strong>。于是"启动一个服务"这件麻烦事——连数据库、读配置、建连接池、装好后台任务——就被统一纳进了同一套类型化、可组合的框架里，而不是散落在各处、彼此顺序全靠人脑记的初始化代码。整个应用的"开机顺序"，最终化成了一道 Layer 的组合表达式：清晰、可推理、不怕漏，谁依赖谁、谁先起来，编译器和运行时替你保证。把"接线"也变成一等公民，是这套设计常被低估的一笔。</p>

<h2>消费：yield* 一个 Service</h2>
<p>业务代码怎么用这个能力？在 <span class="mono">Effect.gen</span> 里直接 <span class="mono">yield*</span> 那个 Service 就行：</p>
<div class="flow">
  <div class="node"><div class="nt">Service</div><div class="nd">声明插槽（标签）</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">yield* Service</div><div class="nd">取出能力来用</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">R 里多一笔</div><div class="nd">"我需要 Agent"</div></div>
</div>
<p>当你写 <span class="mono">const agent = yield* AgentV2.Service</span>，你拿到的就是那个 Interface，可以直接调它的方法。代价是：这段计算的类型 <span class="mono">Effect&lt;A, E, R&gt;</span> 里，<strong>R 会自动多记一笔"我需要 Agent"</strong>。这笔"债"会一直挂在类型上，<strong>直到某个 Layer 来还它</strong>。换句话说，<span class="mono">yield*</span> 一个 Service = 在 R 上欠下一个依赖；提供对应 Layer = 还清这笔债。编译器全程盯着账本，少还一笔都不让你运行。</p>

<h2>组合：用 Layer 搭出整个 app</h2>
<p>整个 opencode 的运行时，本质就是<strong>把一堆 Layer 拼在一起</strong>，直到所有人的依赖都被满足、R 被还干净。</p>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">业务</span><span class="name">SessionRunner</span></div><div class="ld">yield* Agent、Database、LLM…</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">Layer</span><span class="name">Agent.layer · LLM.layer</span></div><div class="ld">各自又依赖下层</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">Layer</span><span class="name">Database.layer · Config.layer</span></div><div class="ld">更基础的能力</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">运行时</span><span class="name">makeRuntime（memoMap 去重）</span></div><div class="ld">把组合好的 Layer 变成可运行的运行时</div></div>
</div>
<p>opencode 用一个 <span class="mono">makeRuntime</span>（在 <span class="mono">src/effect/run-service.ts</span>）把这堆 Layer 组装成运行时，它背后有个<strong>共享的 memoMap</strong>：同一个 Layer 被多处依赖时，<strong>只构造一次</strong>、大家共享，不会重复建十个 Database。这正是"声明式依赖"的红利——你只管说"我要谁"，至于"谁该先造、谁能共享"，框架替你算清楚。</p>
<div class="vflow">
  <div class="step"><b>① 收集债务</b>　每个 yield* 的 Service 在 R 里记一笔"我需要它"</div>
  <div class="step"><b>② 提供 Layer</b>　把对应的 Layer 一个个交给运行时</div>
  <div class="step"><b>③ 拓扑排序</b>　按依赖关系算出"谁先造"（Layer 也可能依赖 Layer）</div>
  <div class="step"><b>④ memoMap 去重</b>　同一个 Layer 多处依赖，只构造一次、共享实例</div>
  <div class="step"><b>⑤ R 还清 → 可运行</b>　所有依赖都被满足，Effect 才能真正跑起来</div>
</div>
<p>这条流水线里最值得记住的是第 ④ 步。设想 <span class="mono">Agent</span>、<span class="mono">Session</span>、<span class="mono">Tool</span> 都依赖 <span class="mono">Database</span>——如果各自 new 一个，就会有三个数据库连接，状态还可能对不上。memoMap 保证<strong>整棵依赖树里 Database 只活一份</strong>，谁要都给同一个。你完全不用手动管这种"单例共享"，只要照常声明依赖，框架就替你把图算对、把实例对齐。这种"声明即正确"的省心，正是依赖注入相对手写 <span class="mono">new</span> 的根本优势。</p>

<p>这套"欠债—还债"的账本机制，带来一个很舒服的性质：<strong>一段代码需要什么，全写在它的类型里，一眼可见。</strong>你不用翻遍函数体去找它偷偷 import 了哪些全局、碰了哪些单例——它的 R 就是一张诚实的依赖清单。读 <span class="mono">packages/core</span> 时这一点尤其省心：看一个 <span class="mono">Effect.fn</span> 的签名，就知道它要动用哪些服务；想复用它，照着把那些 Layer 备齐即可。<strong>依赖显式化</strong>，让大型代码库里"这段逻辑到底牵扯了什么"这个老大难问题，变得可以直接从类型读出来。</p>

<h2>换一层，就换了整个世界</h2>
<p>这套机制最实在的回报，在测试时显现。因为业务代码只认 Service 这个<strong>插槽</strong>、不认背后的具体实现，你想测它，只要<strong>提供一套不同的 Layer</strong> 就行：</p>
<div class="cols">
  <div class="col"><h4>生产环境</h4><p>提供 <span class="mono">Database.layer</span>（真 SQLite）、<span class="mono">LLM.layer</span>（真 provider）。</p></div>
  <div class="col"><h4>测试环境</h4><p>同一段业务代码，换上<strong>假 Database</strong>、<strong>假 LLM</strong> 的 Layer——不碰真文件、不连真网络，照样跑通。</p></div>
</div>
<p>业务代码<strong>一行都不用改</strong>，只是喂给它的 Layer 变了。这就是第 5 课说的"可测试性几乎白送"的真正含义：依赖被显式声明成 Service、由 Layer 在最外层注入，于是"换实现"退化成"换一层 Layer"。V1 那种把依赖写死在 import 里的巨石，永远做不到这一点。</p>
<p>再往深想一层：能"换一层 Layer 就换掉整个实现"，受益的远不止单元测试。同一套业务代码配上不同的 Layer，就能跑在<strong>不同的环境</strong>里——本地用真 SQLite、CI 里用内存库、将来要上多节点时换一套分布式实现，而业务逻辑<strong>原封不动</strong>。opencode 之所以能为"本地单机"和"未来集群"同时留余地（第十一部分会提到 Location、ownership 这些接缝），底气正来自这套"实现可整体替换"的依赖注入。Service / Layer 不只是测试友好，更是<strong>架构能往前演进</strong>的地基。</p>
<p>顺带说一句，这也回答了第 4 课埋下的一个伏笔：为什么 V2 是"一堆小协作者"、V1 是"几块巨石"？因为一旦每个能力都被切成 Service + Layer，模块之间就只剩下<strong>契约</strong>这一种耦合，自然会长成一个个小而独立、可单独测试与替换的件；而 V1 把依赖写死、逻辑揉成一团，就只能滚成大石头。<strong>是 Effect 的依赖模型，悄悄塑造了 V2 的模块形状</strong>——一个架构的"气质"，往往是它最底层那几样工具的选择决定的。</p>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  <strong>Service</strong> 用一个带全局标签的接口，声明一个"能力插槽"（对应 Effect 的 R）；<strong>Layer</strong>（<span class="mono">Layer.effect(Service, make)</span>）把真正的实现接到这个槽上，而且构造时还能依赖别的 Service。业务代码 <span class="mono">yield* Service</span> 取用能力、在 R 上欠下依赖，由组合好的 Layer 在最外层（<span class="mono">makeRuntime</span>，memoMap 去重）一次性还清。"声明 vs 提供"一拆开，换实现就退化成换一层 Layer——这是 V2 可测试、可组合的根。再往大里说，这套机制把"一个东西依赖什么、由谁满足、何时构造、能否共享"这些原本散落在代码各处、全靠约定维系的事，统统收进了类型与运行时去管。你读 V2 任何一个模块，只要先认出它的 Service 契约、再看它的 Layer 接了什么，就抓住了它的"接口"与"接线"两件大事，剩下的实现细节不过是填空。把这套"契约 + 接线"的读法练成本能，整部 <span class="mono">packages/core</span> 在你眼里就会从一团迷雾，变成一张结构分明、处处可预期、读起来心里踏实的地图。
</div>

<div class="card detail">
  <div class="tag">🔬 细节 / 源码对应</div>
  opencode 几乎每个核心模块都长这个样子（简化自 <span class="mono">packages/core/src/agent.ts</span>）；<span class="mono">AGENTS.md</span> 还规定了模块的自重导出写法：
<pre class="code"><span class="cm">// src/agent.ts —— 一个 Service 模块的标准骨架</span>
<span class="kw">interface</span> Interface { <span class="cm">/* … */</span> }
<span class="kw">export class</span> Service <span class="kw">extends</span> Context.<span class="fn">Service</span>&lt;Service, Interface&gt;()(<span class="st">"@opencode/v2/Agent"</span>) {}
<span class="kw">export const</span> layer = Layer.<span class="fn">effect</span>(Service, make)

<span class="kw">export</span> * <span class="kw">as</span> AgentV2 <span class="kw">from</span> <span class="st">"./agent"</span>   <span class="cm">// 自重导出，消费方 import { AgentV2 }</span></pre>
  消费方写 <span class="mono">import { AgentV2 } from "@/agent"</span>，再 <span class="mono">yield* AgentV2.Service</span> / 提供 <span class="mono">AgentV2.layer</span>——名字、接口、实现三者由这套固定结构串起来。
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><strong>Service</strong> = 带全局标签的接口，声明一个"能力插槽"（对应 R）。</li>
    <li><strong>Layer</strong> = <span class="mono">Layer.effect(Service, make)</span>，把真实现接到槽上；构造时还能依赖别的 Service。</li>
    <li>消费：<span class="mono">yield* Service</span> 取能力，R 上自动欠下一笔依赖。</li>
    <li>组合：把 Layer 拼到一起、用 <span class="mono">makeRuntime</span> 还清 R（memoMap 让同一 Layer 只造一次）。</li>
    <li>测试 = 换一套假 Layer，业务代码一行不改——可测试性的根。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Last lesson we said Effect puts "dependencies" into the type's <strong>R</strong> slot. But that's only half the story — declaring "I need Config" isn't enough; someone must <strong>actually hand a Config in</strong>. This lesson covers opencode's "declare deps, then inject deps" machinery: <strong>Service</strong> declares a capability slot, <strong>Layer</strong> wires that slot to a real implementation. Grasp these two words and the structure all over <span class="mono">packages/core</span> — "screens of <span class="mono">yield* XxxService</span>, assembled at the end with <span class="mono">Layer</span>" — clicks into place.</p>
<p>This lesson is a bit "circular," because Service and Layer are a <strong>mutually-completing</strong> pair — neither is whole on its own. So we run the "socket and wiring" metaphor throughout: each new point, return to that picture and match it up. Master this pair and you hold the <strong>master key</strong> to reading <span class="mono">packages/core</span> — because nearly every module there, from Agent and Database to LLM and Tool, is cut from this same Service + Layer mold. Learn to read one and you've learned to read them all; conversely, if this pair isn't solid, every module feels "vaguely familiar yet unclear" — that stutter is the sign you haven't recognized the mold.</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  Think of <strong>Service</strong> as a <strong>standard wall socket</strong>: it only specifies "something providing power plugs in here," defining shape and interface, while <strong>not caring where the power comes from</strong>. Think of <strong>Layer</strong> as the <strong>wiring work</strong>: it actually connects a generator (or the grid, or a battery) behind that socket. Your appliance (business code) just says "I plug into a power socket"; whether a generator or a battery sits behind it is <strong>decided by the wiring crew, swappable anytime</strong>. Service defines "what's needed," Layer decides "what fulfills it" — split the two and swappability appears. The wiring perk: your appliance never cares whether the grid or solar sits behind the wall; to switch from grid to your own solar, you <strong>change the wiring, not the appliance</strong>. In software that means the cost of swapping an implementation is pinned to one spot at the outermost layer, never seeping into the hundreds of places that use it.
</div>

<h2>Service: declare a capability slot</h2>
<p>In opencode, a Service is a <strong>named capability contract</strong>. It's declared with a fixed shape: an interface (what this capability can do) plus a globally-unique <strong>tag</strong> (a name so Effect can recognize it).</p>
<pre class="code"><span class="cm">// simplified from packages/core/src/agent.ts</span>
<span class="kw">interface</span> Interface { <span class="fn">get</span>(id: string): Effect&lt;Agent&gt; }
<span class="kw">export class</span> Service <span class="kw">extends</span> Context.<span class="fn">Service</span>&lt;Service, Interface&gt;()(<span class="st">"@opencode/v2/Agent"</span>) {}</pre>
<p>The key is that string tag <span class="mono">"@opencode/v2/Agent"</span>: it's the slot's <strong>global ID card</strong>. When some code says "I need the Agent service," Effect uses this tag to find who filled the slot. Note there's <strong>no implementation yet</strong> — Service is just a <strong>shape</strong>, a promise, like an unwired socket on the wall. This step cleanly separates "<strong>what's needed</strong>" from "<strong>who provides it</strong>".</p>
<div class="cellgroup">
  <div class="cg-cap"><b>Context.Service&lt;Service, Interface&gt;()("@opencode/v2/Agent")</b>, three parts</div>
  <div class="cells"><span class="cell q">Interface</span><span class="lab">what this capability can do — the set of method signatures</span></div>
  <div class="cells"><span class="cell scale">tag string</span><span class="lab">globally-unique identity; Effect uses it to recognize the slot at runtime</span></div>
  <div class="cells"><span class="cell">Service class</span><span class="lab">both a type (goes into R) and the runtime "key" you yield*</span></div>
</div>
<p>Why a <span class="mono">class</span>? Because it must <strong>do two jobs</strong>: at the type level, <span class="mono">Service</span> is a type recorded in others' R; at runtime, it's a value you can <span class="mono">yield*</span> — a "key" to fetch the matching implementation from the runtime's "ledger." One name being both type and value is exactly Effect's key trick for making "dependencies" both type-safe and runtime-injectable. You needn't memorize all its magic — just recognize the fixed skeleton: <strong>an interface + a tag + a Service class</strong>.</p>

<h2>Layer: wire the slot to a real implementation</h2>
<p>A slot alone has no power. <strong>Layer</strong> is that "wiring work," <strong>binding</strong> a real implementation to a Service tag:</p>
<pre class="code"><span class="cm">// simplified from packages/core/src/agent.ts</span>
<span class="kw">export const</span> layer = Layer.<span class="fn">effect</span>(
  Service,                          <span class="cm">// which slot to fill</span>
  Effect.<span class="fn">gen</span>(<span class="kw">function*</span> () {        <span class="cm">// how to build the impl (itself an Effect)</span>
    <span class="kw">const</span> db = <span class="kw">yield</span>* Database     <span class="cm">// a Layer can itself depend on other Services</span>
    <span class="kw">return</span> { <span class="fn">get</span>: (id) =&gt; <span class="cm">/* …implemented with db… */</span> }
  }),
)</pre>
<p><span class="mono">Layer.effect(Service, make)</span> reads "build the impl with <span class="mono">make</span>, install it into the <span class="mono">Service</span> slot." Neatly, <span class="mono">make</span> is itself an Effect, so <strong>a Layer can depend on other Services while constructing</strong> (above, <span class="mono">yield* Database</span>). So Layers <strong>stack like blocks</strong>: Agent depends on Database, Database on Config… each layer only declaring what it needs and produces.</p>
<table class="t">
  <tr><th></th><th>Service</th><th>Layer</th></tr>
  <tr><td>What</td><td>the capability's <strong>contract</strong> (interface + tag)</td><td>the contract's <strong>impl + wiring</strong></td></tr>
  <tr><td>Analogy</td><td>the wall socket (shape)</td><td>wiring a generator behind the socket</td></tr>
  <tr><td>Cares about</td><td>"what it can do"</td><td>"how to build it, who it depends on"</td></tr>
  <tr><td>Swappability</td><td>consumers only know it</td><td>swap a set anytime (real/fake)</td></tr>
</table>
<p>Splitting Service and Layer into two things, rather than mashing them into one "class + new an instance," is the heart of the design. Because consumers depend only on <strong>Service (the contract)</strong>, who plays <strong>Layer (the impl)</strong> becomes a knob freely set at the outermost layer. This "contract-vs-impl separation" takes interfaces + a DI framework to build laboriously in traditional OOP; Effect makes it a <strong>language-level, type-safe</strong> first-class citizen — which is why nearly every opencode module strictly follows this skeleton.</p>
<p>One more often-missed perk: because a Layer's construction is itself an Effect, it <strong>can also fail and depend on others</strong>. So "starting a service" — connecting the DB, reading config, building a pool, wiring background tasks — is folded into the same typed, composable framework, instead of init code scattered everywhere whose order lives only in someone's head. The whole app's "boot order" becomes one Layer-composition expression: clear, reasoned-about, leak-proof — who depends on whom and who starts first, the compiler and runtime guarantee. Making "wiring" a first-class citizen too is an underrated stroke of this design.</p>

<h2>Consume: yield* a Service</h2>
<p>How does business code use this capability? Just <span class="mono">yield*</span> the Service inside <span class="mono">Effect.gen</span>:</p>
<div class="flow">
  <div class="node"><div class="nt">Service</div><div class="nd">declare slot (tag)</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">yield* Service</div><div class="nd">take the capability</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">one more in R</div><div class="nd">"I need Agent"</div></div>
</div>
<p>When you write <span class="mono">const agent = yield* AgentV2.Service</span>, you get that Interface and can call its methods directly. The cost: this computation's type <span class="mono">Effect&lt;A, E, R&gt;</span> <strong>auto-records one more "I need Agent" in R</strong>. That "debt" stays on the type <strong>until some Layer repays it</strong>. In other words, <span class="mono">yield*</span> a Service = owe a dependency in R; provide the matching Layer = repay it. The compiler watches the ledger throughout — short one repayment and it won't let you run.</p>
<p>This "owe–repay" ledger gives a comfortable property: <strong>what a piece of code needs is written in its type, visible at a glance.</strong> You needn't comb the function body for which globals it secretly imported or which singletons it touched — its R is an honest dependency list. Reading <span class="mono">packages/core</span> this is especially easy: look at an <span class="mono">Effect.fn</span>'s signature and you know which services it draws on; to reuse it, just have those Layers ready. <strong>Making dependencies explicit</strong> turns the old "what does this logic actually involve" headache, in a big codebase, into something you read straight off the type.</p>

<h2>Compose: build the whole app with Layers</h2>
<p>opencode's entire runtime is essentially <strong>assembling a pile of Layers</strong> until everyone's deps are satisfied and R is fully repaid.</p>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">Business</span><span class="name">SessionRunner</span></div><div class="ld">yield* Agent, Database, LLM…</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">Layer</span><span class="name">Agent.layer · LLM.layer</span></div><div class="ld">each depends on lower ones</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">Layer</span><span class="name">Database.layer · Config.layer</span></div><div class="ld">more basic capabilities</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">Runtime</span><span class="name">makeRuntime (memoMap dedups)</span></div><div class="ld">turn composed Layers into a runnable runtime</div></div>
</div>
<p>opencode uses a <span class="mono">makeRuntime</span> (in <span class="mono">src/effect/run-service.ts</span>) to assemble these Layers into a runtime, backed by a <strong>shared memoMap</strong>: when one Layer is depended on in many places, it's <strong>constructed once</strong> and shared, never ten Databases. That's the dividend of "declarative dependencies" — you just say "who I need," and "who builds first, who can be shared" the framework works out for you.</p>
<div class="vflow">
  <div class="step"><b>① Collect debts</b>　each yield*'d Service records an "I need it" in R</div>
  <div class="step"><b>② Provide Layers</b>　hand the matching Layers to the runtime</div>
  <div class="step"><b>③ Topo-sort</b>　compute "who builds first" from deps (Layers may depend on Layers)</div>
  <div class="step"><b>④ memoMap dedup</b>　a Layer depended on in many places is built once, shared</div>
  <div class="step"><b>⑤ R repaid → runnable</b>　all deps satisfied, only then can the Effect run</div>
</div>
<p>The step to remember is ④. Imagine <span class="mono">Agent</span>, <span class="mono">Session</span>, <span class="mono">Tool</span> all depend on <span class="mono">Database</span> — if each new'd one, you'd get three DB connections with possibly mismatched state. memoMap guarantees <strong>one Database across the whole dep tree</strong>, the same one for everyone. You never hand-manage this "singleton sharing"; just declare deps as usual and the framework gets the graph right and aligns the instances. This "declare and it's correct" ease is DI's fundamental edge over hand-written <span class="mono">new</span>.</p>

<h2>Swap a layer, swap the whole world</h2>
<p>This machinery's most tangible payoff shows in testing. Because business code knows only the Service <strong>slot</strong>, not the concrete impl behind it, to test it you just <strong>provide a different set of Layers</strong>:</p>
<div class="cols">
  <div class="col"><h4>Production</h4><p>provide <span class="mono">Database.layer</span> (real SQLite), <span class="mono">LLM.layer</span> (real provider).</p></div>
  <div class="col"><h4>Test</h4><p>the same business code, swapped onto a <strong>fake Database</strong> and <strong>fake LLM</strong> Layer — no real files, no real network, still runs.</p></div>
</div>
<p>The business code <strong>doesn't change one line</strong>; only the Layers fed to it change. That's the real meaning of Lesson 5's "testability almost free": deps are explicitly declared as Services and injected by Layers at the outermost layer, so "swap impl" degenerates into "swap a Layer." V1's monoliths, hard-wiring deps in imports, can never do this.</p>
<p>One level deeper: "swap a Layer to swap the whole impl" benefits far more than unit tests. The same business code, with different Layers, runs in <strong>different environments</strong> — real SQLite locally, an in-memory DB in CI, a distributed impl when going multi-node later — while the business logic stays <strong>untouched</strong>. opencode can leave room for both "local single-machine" and "future cluster" (Part 11 mentions seams like Location, ownership) precisely thanks to this "wholesale-swappable impl" DI. Service / Layer isn't just test-friendly; it's the foundation for the <strong>architecture to evolve forward</strong>.</p>
<p>Incidentally, this answers a thread Lesson 4 left dangling: why is V2 "a pile of small collaborators" and V1 "a few boulders"? Because once every capability is cut into Service + Layer, the only coupling left between modules is the <strong>contract</strong>, so they naturally grow into small, independent, separately-testable-and-swappable pieces; whereas V1, hard-wiring deps and mashing logic together, can only roll into boulders. <strong>It's Effect's dependency model that quietly shapes V2's module shape</strong> — an architecture's "temperament" is often decided by the choice of its lowest-level few tools.</p>

<div class="card macro">
  <div class="tag">🌍 Big picture</div>
  <strong>Service</strong> uses a globally-tagged interface to declare a "capability slot" (matching Effect's R); <strong>Layer</strong> (<span class="mono">Layer.effect(Service, make)</span>) wires the real impl into that slot, and can itself depend on other Services while constructing. Business code <span class="mono">yield* Service</span> takes the capability and owes a dep in R, repaid wholesale at the outermost layer by composed Layers (<span class="mono">makeRuntime</span>, memoMap dedup). Split "declare vs provide" and swapping impls degenerates into swapping a Layer — the root of V2's testability and composability. More broadly, this machinery folds "what something depends on, who satisfies it, when it's built, whether it's shared" — once scattered across code and held together by convention — into the type and runtime. Read any V2 module: recognize its Service contract, see what its Layer wires in, and you've grasped its "interface" and "wiring," the rest being fill-in-the-blank. Drill this "contract + wiring" reading into instinct and all of <span class="mono">packages/core</span> turns from fog into a clear, predictable, reassuring map.
</div>

<div class="card detail">
  <div class="tag">🔬 Source detail</div>
  Nearly every core opencode module looks like this (simplified from <span class="mono">packages/core/src/agent.ts</span>); <span class="mono">AGENTS.md</span> also mandates the module's self-reexport form:
<pre class="code"><span class="cm">// src/agent.ts — the standard skeleton of a Service module</span>
<span class="kw">interface</span> Interface { <span class="cm">/* … */</span> }
<span class="kw">export class</span> Service <span class="kw">extends</span> Context.<span class="fn">Service</span>&lt;Service, Interface&gt;()(<span class="st">"@opencode/v2/Agent"</span>) {}
<span class="kw">export const</span> layer = Layer.<span class="fn">effect</span>(Service, make)

<span class="kw">export</span> * <span class="kw">as</span> AgentV2 <span class="kw">from</span> <span class="st">"./agent"</span>   <span class="cm">// self-reexport; consumers import { AgentV2 }</span></pre>
  Consumers write <span class="mono">import { AgentV2 } from "@/agent"</span>, then <span class="mono">yield* AgentV2.Service</span> / provide <span class="mono">AgentV2.layer</span> — name, interface, and impl strung together by this fixed structure.
</div>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li><strong>Service</strong> = a globally-tagged interface declaring a "capability slot" (matching R).</li>
    <li><strong>Layer</strong> = <span class="mono">Layer.effect(Service, make)</span>, wiring the real impl into the slot; can depend on other Services while constructing.</li>
    <li>Consume: <span class="mono">yield* Service</span> takes the capability, auto-owing a dep in R.</li>
    <li>Compose: assemble Layers, repay R via <span class="mono">makeRuntime</span> (memoMap builds each Layer once).</li>
    <li>Test = swap in a fake-Layer set, business code unchanged — the root of testability.</li>
  </ul>
</div>
""",
}
LESSON_07 = wip('并发原语', 'Concurrency primitives')
LESSON_08 = wip('项目里的 Effect 工具箱', 'The Effect toolbox')
