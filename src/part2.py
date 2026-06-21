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
LESSON_06 = wip('Context.Service 与 Layer', 'Services & Layers')
LESSON_07 = wip('并发原语', 'Concurrency primitives')
LESSON_08 = wip('项目里的 Effect 工具箱', 'The Effect toolbox')
