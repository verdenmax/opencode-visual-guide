"""Part 8 (Part 8 · Config, Agents, Providers) content. Placeholders until M8 fills them in."""
from placeholder import wip

LESSON_44 = {
    "zh": r"""
<p class="lead">前两个 part，我们把 agent 的「脑」（M6 LLM）和「手」（M7 工具）都拆透了。但有一个朴素的问题一直没答：这些零件——用哪个模型、配哪组工具、什么权限、接哪些 MCP——<strong>是谁、在哪、按什么规则「定」下来的？</strong>答案是<strong>配置（config）</strong>。M8 这个 part 讲的就是「<strong>怎么把一个具体的 agent 攒出来</strong>」，而第一课，是这一切的源头：<strong>配置是怎么被加载、被合并的。</strong>你会看到，opencode 的配置不是「一个文件读进来」这么简单，而是一套<strong>分层叠加、就近覆盖</strong>的优雅机制——全局给默认、项目给特化、越靠近你打开的目录、说话越算数。</p>
<p>这一课有两个要点。其一，<strong>配置是整个系统的「接线总成」</strong>：一个叫 <span class="mono">Config.Info</span> 的类型化 schema，几乎把前面所有子系统的旋钮都收在了一处——模型、agents、权限（第 41 课）、MCP（第 46 课）、工具输出上限（第 42 课）、skills（第 43 课）…… 都在这张表里有一格。其二，也是更精妙的，<strong>加载是「分层 + 就近覆盖」</strong>：全局配置垫底、从项目根一路向你打开的目录走、越近的越优先；取某个设置的最终值，就是「<strong>从高优先级往低看，谁先定了这一项就用谁</strong>」。读懂这套层叠机制，你就懂了 opencode 怎么让「机器级默认、项目级约定、目录级特例」三者<strong>各管一摊、又自动合成一份生效配置</strong>。</p>

<div class="card analogy">
  <div class="tag">📋 生活类比</div>
  把配置想象成一家公司里<strong>层层叠加的着装规范</strong>。公司有一份<strong>总章程</strong>（全局配置）——「上班穿正装」。你所在的<strong>部门</strong>又贴了一条（项目配置）——「我们部门周五可以休闲」。你的<strong>小组</strong>白板上还写着一行（更靠近你的配置）——「本组评审日穿队服」。当有人问「<strong>这周五我该穿啥</strong>」，你不会把三份规则一股脑读完，而是<strong>从最贴近你的那条往上看，谁先答了这个问题就听谁的</strong>——小组没说周五穿啥，就看部门的「周五休闲」；部门要没说，才退回公司总章程。<strong>越具体、越靠近你的规则，越优先；越宽泛、越高层的，越是垫底的默认。</strong>三层规则不冲突地共存，而你任何时刻要的「<strong>生效着装</strong>」，是它们就近合成出来的那一份。opencode 的配置加载，正是这套「就近覆盖、层层垫底」的智慧。
</div>

<h2>Config.Info：整个系统的接线总成</h2>
<p>先看配置<strong>装了什么</strong>。打开 <span class="mono">config.ts</span>，<span class="mono">Config.Info</span> 是一个用 Effect Schema 定义的大类——它几乎是 opencode 所有子系统的<strong>旋钮汇集处</strong>：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">model / shell</div><div class="c-txt">默认用哪个模型、用什么 shell</div></div>
  <div class="cell"><div class="c-tag">agents</div><div class="c-txt">定义有哪些 agent（第 45 课）</div></div>
  <div class="cell"><div class="c-tag">permissions</div><div class="c-txt">权限规则集 Ruleset（第 41 课那套 allow/deny/ask）</div></div>
  <div class="cell"><div class="c-tag">mcp</div><div class="c-txt">接哪些 MCP server（第 46 课）</div></div>
  <div class="cell"><div class="c-tag">tool_output / skills</div><div class="c-txt">工具输出上限（第 42 课）、技能目录（第 43 课）</div></div>
  <div class="cell"><div class="c-tag">instructions / commands / lsp…</div><div class="c-txt">指令、自定义命令、LSP、格式化器、压缩…</div></div>
</div>
<p>看这张表你就明白：<strong>配置不是某个孤立模块的设置，而是把全系统的「用户可调项」汇到一处的总枢纽</strong>。第 41 课的权限、第 42 课的输出上限、第 43 课的 skills、第 46 课的 MCP……它们各自的「该怎么配」，最终都落到 <span class="mono">Config.Info</span> 的某一格里。而它是一个<strong>类型化的 Schema 类</strong>——这意味着配置文件在加载时就被<strong>校验</strong>：写错了字段、给错了类型，在解析关就被挡下（又是第 5、22 课「schema 即契约」的体现），而不是等到某个子系统运行时才神秘出错。<strong>一份配置文件，是用户向整个系统下达意图的统一入口；一个 Config.Info schema，是这份意图的类型化契约。</strong>这种「<strong>把全系统的可调项收拢到一个类型化结构里</strong>」的做法本身就是一种设计美德：用户不必去十几个地方改十几种格式的设置，只在一处声明；而每个子系统也不必各自发明一套读配置的办法，都从这同一份 <span class="mono">Config.Info</span> 里取自己那一格。<strong>一处声明、各取所需</strong>，配置因此既好写、又好校验、又好演进——加一个新可调项，就是给 schema 添一个字段。</p>

<h2>分层加载：全局垫底、就近覆盖</h2>
<p>再看配置<strong>怎么来</strong>。这才是这一课真正精妙的地方。opencode 不是「读一个文件」，而是<strong>从多处收集、按优先级排好</strong>。它认三种文件名，并把发现的东西分成两类 <span class="mono">Entry</span>：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">config.json</div><div class="c-txt">认的三种配置文件名之一</div></div>
  <div class="cell"><div class="c-tag">opencode.json(c)</div><div class="c-txt">另两种（.jsonc 允许注释）</div></div>
  <div class="cell"><div class="c-tag">Entry = Document</div><div class="c-txt">一份加载好的配置文档（type/path/info）</div></div>
  <div class="cell"><div class="c-tag">Entry = Directory</div><div class="c-txt">一个补充资源目录（如 .opencode，放 skills/commands）</div></div>
</div>
<p>它并从两类位置发现配置：</p>
<div class="flow">
  <div class="f-node">全局配置目录<br><small>global.config，机器级默认</small></div>
  <div class="f-arrow">+ 向上走 →</div>
  <div class="f-node">从项目根…到你打开的目录<br><small>沿途的 .opencode 与配置文件</small></div>
  <div class="f-arrow">排序 →</div>
  <div class="f-node">一串 Entry：低→高优先级<br><small>越靠近 cwd 越优先</small></div>
</div>
<p>它从你<strong>打开的目录</strong>开始，一路<strong>向上走到项目根</strong>，沿途找 <span class="mono">.opencode</span> 目录和那几个配置文件名；再加上机器级的<strong>全局配置目录</strong>。所有发现的配置被排成一串 <span class="mono">Entry</span>（每个是一份配置文档 <span class="mono">Document</span> 或一个补充目录 <span class="mono">Directory</span>），<strong>从低优先级到高优先级</strong>。排序的铁律就一句，写在源码注释里：「<strong>更靠近所打开目录的配置，应当胜过更高层的</strong>」（A config closer to the opened directory should win over one higher up）。为什么是「越近越优先」、而不是反过来？因为这<strong>恰好对应人的意图的「特异性」</strong>：你在机器全局写的，是「我大体上喜欢这样」的宽泛默认；你在某个子目录里专门写的，是「<strong>就这块儿，我要特别这样</strong>」的明确意图。特异的意图理应压过宽泛的默认——否则「专门为这个角落写的设置」反而被一个全局默认盖掉，那就荒谬了。「就近覆盖」让<strong>越具体的声明越有话语权</strong>，正合人对「我特意写在这儿，当然该听我的」这种直觉。于是优先级从低到高大致是：</p>
<div class="layers">
  <div class="layer"><div class="l-name">全局配置（最低）</div><div class="l-desc">~/.config 之类，机器级默认——所有项目共享的底色</div></div>
  <div class="layer"><div class="l-name">项目根配置</div><div class="l-desc">仓库根的 opencode.json——这个项目的团队约定</div></div>
  <div class="layer"><div class="l-name">更靠近 cwd 的配置（最高）</div><div class="l-desc">子目录里的 .opencode / 配置——最具体的特例，谁也盖不过</div></div>
</div>
<p>全局与项目这两层，承担的角色截然不同，值得分清：</p>
<div class="cols">
  <div class="col"><h4>全局配置（机器级）</h4><p>放<strong>跨项目共享的默认</strong>：你惯用的模型、shell、个人偏好。它是底色，几乎不该写「某个项目特有」的东西。通常进入用户的个人配置目录，<strong>不入版本库</strong>。</p></div>
  <div class="col"><h4>项目配置（仓库级）</h4><p>放<strong>这个项目特有的约定</strong>：该用哪个模型、哪些权限规则、接哪些 MCP。它<strong>随仓库提交</strong>，于是团队成员一拉代码，就共享同一套项目配置——配置成了代码的一部分。</p></div>
</div>

<h2>per-key 取值：latest 的就近裁决</h2>
<p>有了这串「低→高」排好的 Entry，怎么得到某个设置的<strong>最终生效值</strong>？靠一个简洁的 <span class="mono">latest(entries, key)</span> 函数。它的逻辑就一句话：<strong>在所有配置文档里，取「最高优先级的、定义了这个 key 的那一份」的值</strong>。也就是<strong>逐项的「后者胜出」</strong>（last-wins）：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">问</span><span class="t-txt">model 这一项，最终用哪个？</span></div>
  <div class="t-row"><span class="t-num">查</span><span class="t-txt">从最高优先级的 Entry 往低看，谁第一个定义了 model</span></div>
  <div class="t-row"><span class="t-num">取</span><span class="t-txt">子目录配置定义了 → 用它；没定义 → 退回项目配置；再没有 → 退回全局；都没有 → undefined</span></div>
</div>
<p>这套「<strong>保留一串有序来源、按 key 逐项就近裁决</strong>」的设计，比「急着把所有配置深合并成一个大对象」要干净得多。它不预先算一份合成结果，而是<strong>把来源原样按优先级留着，谁问哪个 key，就当场为那个 key 裁决一次</strong>。好处是：每一项的「<strong>它从哪份配置来的、为什么是这个值</strong>」始终清清楚楚、可追溯——你要排查「这个 model 怎么是这个」，顺着优先级一层层看就行，不会迷失在一个早已合并、来源难辨的大对象里。<strong>把『有哪些来源』和『某一项最终取谁』分开，是这套配置系统可解释性的根基。</strong>这种可解释性在现实里极其值钱：当一个团队成员困惑「为什么我的 agent 用了这个奇怪的模型」，答案不是去翻一个早已揉成一团的合成对象，而是顺着那串有序 Entry 一层层问「这一层定义 model 了吗」，立刻就能定位到「哦，是我自己子目录里那份 .opencode 写的」。<strong>配置出问题时最怕的就是『来源成谜』，而这套设计从结构上就让来源始终可追。</strong>这和第 41 课权限的 <span class="mono">findLast</span>「后匹配者胜」、第 37 课注册表的「摞顶最新」，又是同一种「有序来源、就近取值」的思路在不同地方的回响。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <p>配置加载是「攒一个 agent」的源头，把用户意图喂给整个系统：</p>
  <ul>
    <li><strong>Config.Info = 接线总成</strong>（<span class="mono">config.ts</span>）：一个类型化 Schema 类，几乎汇集了全系统旋钮——model/shell、agents（L45）、permissions（L41）、mcp（L46）、tool_output（L42）、skills（L43）、instructions/commands/lsp…。加载即校验（schema 即契约）。</li>
    <li><strong>分层发现</strong>：认 <span class="mono">config.json/opencode.json/opencode.jsonc</span>；从打开的目录向上走到项目根找 <span class="mono">.opencode</span> 与配置文件，再加全局配置目录；排成一串 <span class="mono">Entry</span>（Document/Directory）低→高优先级。</li>
    <li><strong>就近覆盖</strong>：源码铁律「越靠近所打开目录的配置越优先」。优先级：全局（默认）< 项目根 < 更靠近 cwd（最具体）。</li>
    <li><strong>per-key 就近裁决</strong>：<span class="mono">latest(entries, key)</span> 取「最高优先级里定义了该 key」的值（逐项 last-wins）。保留有序来源、按 key 当场裁决——比急着深合并更可解释、可追溯。与第 41 课 <span class="mono">findLast</span>、第 37 课「摞顶最新」同一思路。</li>
  </ul>
  <p>有了这份「生效配置」，下一课（第 45 课）就能讲 <strong>Agents</strong> 了：配置里的 <span class="mono">agents</span> 那一格怎么变成一个个能跑的 agent，build/plan 这些内置 agent 怎么定义、它们的提示词怎么组装。再往后第 46 课讲 <strong>MCP</strong>（配置里的 mcp 那一格怎么接出动态工具）、第 47 课讲 <strong>Provider 插件</strong>（几十家模型供应商怎么注册）。配置是这一切的<strong>总开关</strong>——它先把「用户想要什么」收齐、校验、合成，后面的子系统才各取所需地跑起来。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p><span class="mono">latest</span> 的实现，把「按 key 就近取值」写得很直白（简化自 config.ts）：</p>
  <pre class="code"><span class="cm">// entries 已按 低→高 优先级排好；取最高优先级里定义了 key 的那份的值</span>
<span class="kw">function</span> <span class="fn">latest</span>&lt;K&gt;(entries: Entry[], key: K) {
  <span class="kw">return</span> entries
    .<span class="fn">filter</span>(e =&gt; e.type === <span class="st">"document"</span>)   <span class="cm">// 只看配置文档（Directory 是补充目录）</span>
    .<span class="fn">map</span>(d =&gt; d.info[key])
    .<span class="fn">findLast</span>(v =&gt; v !== undefined)        <span class="cm">// 最后一个（=最高优先级）有定义的</span>
}</pre>
  <p>注意 <span class="mono">findLast</span> 这个细节——和第 41 课权限的 <span class="mono">evaluate</span> 用的是<strong>同一个方法</strong>：因为 entries 是「低→高」排的，<span class="mono">findLast</span> 取的就是<strong>最高优先级里有定义的那一项</strong>，干净利落地实现「就近覆盖」。这也解释了为什么 <span class="mono">Entry</span> 要分 <span class="mono">Document</span>（一份配置文件）和 <span class="mono">Directory</span>（一个补充目录）两种：有些位置贡献的不是「配置值」，而是「<strong>额外的资源目录</strong>」（比如放 skills、commands 的文件夹），它们也要按同样的优先级参与进来，但 <span class="mono">latest</span> 取值时只看 <span class="mono">Document</span>。<strong>一个 filter + 一个 findLast，就把「分层配置该取谁」这件听起来很复杂的事，化成了三行</strong>——又一次印证：好的机制往往不靠复杂，而靠把对的数据结构（有序的 Entry 列表）和对的默认（就近者胜）摆对位置。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>配置是「攒一个 agent」的源头</strong>，M8 第一课。<span class="mono">Config.Info</span>（<span class="mono">core/src/config.ts</span>）是<strong>类型化 Schema 接线总成</strong>，几乎汇集全系统旋钮：model/shell、agents（L45）、permissions（L41 Ruleset）、mcp（L46）、tool_output（L42）、skills（L43）、instructions/commands/lsp/formatter/compaction…。加载即 schema 校验。</li>
    <li><strong>分层发现</strong>：认 <span class="mono">config.json/opencode.json/opencode.jsonc</span>；从打开目录<strong>向上走到项目根</strong>找 <span class="mono">.opencode</span> 与配置文件，再加<strong>全局配置目录</strong>；排成 <span class="mono">Entry[]</span>（<span class="mono">Document</span>=配置文件 / <span class="mono">Directory</span>=补充目录）<strong>低→高优先级</strong>。</li>
    <li><strong>就近覆盖</strong>（源码铁律）：「越靠近所打开目录的配置越优先」。优先级 全局默认 < 项目根 < 更靠近 cwd 的特例。</li>
    <li><strong>per-key 就近裁决</strong>：<span class="mono">latest(entries, key)</span> = filter 出 Document → <span class="mono">findLast</span> 有定义的（=最高优先级）。<strong>逐项 last-wins</strong>，保留有序来源、按 key 当场裁决——比急着深合并更可解释、可追溯。与第 41 课权限 <span class="mono">findLast</span>、第 37 课「摞顶最新」同一「有序来源、就近取值」思路。</li>
    <li>配置是后续 L45 Agents / L46 MCP / L47 Provider 的<strong>总开关</strong>：先把用户意图收齐、校验、合成，子系统再各取所需。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">The prior two parts dissected the agent's "brain" (M6 LLM) and "hands" (M7 tools). But one plain question stayed unanswered: these parts—which model to use, which tools, what permissions, which MCPs to connect—<strong>who, where, by what rules, "decides" them?</strong> The answer is <strong>config</strong>. This part, M8, covers "<strong>how to assemble a concrete agent</strong>," and this first lesson is the source of it all: <strong>how config is loaded and merged.</strong> You'll see opencode's config isn't "read one file" but an elegant mechanism of <strong>layered cascade with closer-overrides</strong>—global gives defaults, project gives specializations, and the closer to the directory you opened, the more its say counts.</p>
<p>This lesson has two points. One, <strong>config is the system's "wiring harness"</strong>: a typed schema called <span class="mono">Config.Info</span> gathers nearly every prior subsystem's knobs in one place—model, agents, permissions (lesson 41), MCP (lesson 46), tool output cap (lesson 42), skills (lesson 43)… each has a cell in this table. Two, and more exquisite, <strong>loading is "layered + closer-overrides"</strong>: global config at the bottom, walking from the project root toward the directory you opened, the closer taking precedence; getting a setting's final value is "<strong>look from high priority to low, whoever defines this item first wins</strong>." Grasp this cascade and you'll understand how opencode lets "machine-level defaults, project-level conventions, directory-level exceptions" <strong>each mind its own yet auto-compose into one effective config</strong>.</p>

<div class="card analogy">
  <div class="tag">📋 Analogy</div>
  Picture config as a company's <strong>layered dress code</strong>. The company has a <strong>master charter</strong> (global config)—"wear formal to work." Your <strong>department</strong> posted one too (project config)—"our department can dress casual on Fridays." Your <strong>team</strong>'s whiteboard adds a line (config closer to you)—"this team wears jerseys on review days." When someone asks "<strong>what do I wear this Friday</strong>," you don't read all three rules at once, but <strong>look from the rule closest to you upward, listening to whoever answers the question first</strong>—the team didn't say what to wear Friday, so check the department's "casual Friday"; if the department didn't say, fall back to the company charter. <strong>The more specific and closer the rule, the higher priority; the broader and higher-level, the more it's the bottom default.</strong> Three layers of rules coexist without conflict, and the "<strong>effective dress code</strong>" you need at any moment is the one they compose closer-first. opencode's config loading is exactly this "closer-overrides, layer-by-layer-bottoming" wisdom.
</div>

<h2>Config.Info: the system's wiring harness</h2>
<p>First, what config <strong>holds</strong>. Open <span class="mono">config.ts</span> and <span class="mono">Config.Info</span> is a big class defined with Effect Schema—it's nearly the <strong>knob-gathering place</strong> for all of opencode's subsystems:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">model / shell</div><div class="c-txt">which model to default to, which shell to use</div></div>
  <div class="cell"><div class="c-tag">agents</div><div class="c-txt">defines which agents exist (lesson 45)</div></div>
  <div class="cell"><div class="c-tag">permissions</div><div class="c-txt">a permission Ruleset (lesson 41's allow/deny/ask)</div></div>
  <div class="cell"><div class="c-tag">mcp</div><div class="c-txt">which MCP servers to connect (lesson 46)</div></div>
  <div class="cell"><div class="c-tag">tool_output / skills</div><div class="c-txt">tool output cap (lesson 42), skill directories (lesson 43)</div></div>
  <div class="cell"><div class="c-tag">instructions / commands / lsp…</div><div class="c-txt">instructions, custom commands, LSP, formatter, compaction…</div></div>
</div>
<p>From this table you see: <strong>config isn't some isolated module's settings but the hub gathering the whole system's "user-tunable items" in one place</strong>. Lesson 41's permissions, lesson 42's output cap, lesson 43's skills, lesson 46's MCP… their respective "how to configure" all land in a cell of <span class="mono">Config.Info</span>. And it's a <strong>typed Schema class</strong>—meaning the config file is <strong>validated</strong> at load: a wrong field, a wrong type, gets stopped at the parse gate (again lessons 5, 22's "schema is contract"), not mysteriously erroring at some subsystem's runtime later. <strong>A config file is the user's unified entry for issuing intent to the whole system; a Config.Info schema is the typed contract of that intent.</strong> This "<strong>gathering the whole system's tunables into one typed structure</strong>" is itself a design virtue: the user needn't change a dozen settings in a dozen formats in a dozen places, but declares in one; and each subsystem needn't invent its own way to read config, all taking its cell from this same <span class="mono">Config.Info</span>. <strong>Declare in one place, each takes what it needs</strong>—config is thus easy to write, validate, and evolve—adding a new tunable is adding a field to the schema.</p>

<h2>Layered loading: global at the bottom, closer overrides</h2>
<p>Now, where config <strong>comes from</strong>. This is where the lesson gets truly exquisite. opencode doesn't "read one file" but <strong>collects from multiple places, sorted by priority</strong>. It recognizes three filenames and splits findings into two kinds of <span class="mono">Entry</span>:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">config.json</div><div class="c-txt">one of the three recognized config filenames</div></div>
  <div class="cell"><div class="c-tag">opencode.json(c)</div><div class="c-txt">the other two (.jsonc allows comments)</div></div>
  <div class="cell"><div class="c-tag">Entry = Document</div><div class="c-txt">a loaded config document (type/path/info)</div></div>
  <div class="cell"><div class="c-tag">Entry = Directory</div><div class="c-txt">a supplemental resource directory (e.g. .opencode, holding skills/commands)</div></div>
</div>
<p>And it discovers config from two kinds of location:</p>
<div class="flow">
  <div class="f-node">global config dir<br><small>global.config, machine-level default</small></div>
  <div class="f-arrow">+ walk up →</div>
  <div class="f-node">from project root… to the dir you opened<br><small>.opencode and config files along the way</small></div>
  <div class="f-arrow">sort →</div>
  <div class="f-node">a list of Entry: low→high priority<br><small>closer to cwd = higher</small></div>
</div>
<p>It starts from the directory <strong>you opened</strong>, walks <strong>up to the project root</strong>, finding <span class="mono">.opencode</span> directories and those config filenames along the way; plus the machine-level <strong>global config directory</strong>. All discovered configs are sorted into a list of <span class="mono">Entry</span> (each a config document <span class="mono">Document</span> or a supplemental <span class="mono">Directory</span>), <strong>from low priority to high</strong>. The sorting's iron law is one line in the source comment: "<strong>A config closer to the opened directory should win over one higher up</strong>." Why "closer = higher," not the reverse? Because it <strong>maps exactly to the "specificity" of human intent</strong>: what you write in the machine global is "I generally like this" broad default; what you write specifically in some subdirectory is "<strong>right here, I want it specially like this</strong>" explicit intent. The specific intent should override the broad default—else "settings written specially for this corner" would be covered by a global default, which is absurd. "Closer-overrides" gives <strong>the more specific declaration more say</strong>, matching the human intuition "I wrote it here on purpose, of course it should win." So priority low-to-high is roughly:</p>
<div class="layers">
  <div class="layer"><div class="l-name">global config (lowest)</div><div class="l-desc">~/.config etc., machine-level default—the backdrop shared by all projects</div></div>
  <div class="layer"><div class="l-name">project-root config</div><div class="l-desc">the repo root's opencode.json—this project's team convention</div></div>
  <div class="layer"><div class="l-name">config closer to cwd (highest)</div><div class="l-desc">a subdirectory's .opencode / config—the most specific exception, unbeatable</div></div>
</div>
<p>The global and project layers play starkly different roles, worth distinguishing:</p>
<div class="cols">
  <div class="col"><h4>global config (machine-level)</h4><p>Holds <strong>cross-project shared defaults</strong>: your habitual model, shell, personal preferences. It's the backdrop, almost never holding "project-specific" things. Usually goes into the user's personal config dir, <strong>not in version control</strong>.</p></div>
  <div class="col"><h4>project config (repo-level)</h4><p>Holds <strong>this project's specific conventions</strong>: which model, which permission rules, which MCPs. It's <strong>committed with the repo</strong>, so team members pulling the code share the same project config—config becomes part of the code.</p></div>
</div>

<h2>per-key resolution: latest's closer-first adjudication</h2>
<p>With this "low→high" sorted Entry list, how to get a setting's <strong>final effective value</strong>? Via a concise <span class="mono">latest(entries, key)</span> function. Its logic is one line: <strong>among all config documents, take the value from "the highest-priority one that defines this key"</strong>. That is, <strong>per-item "later-wins"</strong> (last-wins):</p>
<div class="trace">
  <div class="t-row"><span class="t-num">ask</span><span class="t-txt">the model item—which finally?</span></div>
  <div class="t-row"><span class="t-num">check</span><span class="t-txt">from highest-priority Entry down, who first defines model</span></div>
  <div class="t-row"><span class="t-num">take</span><span class="t-txt">subdir config defines it → use it; not → fall back to project config; still not → global; none → undefined</span></div>
</div>
<p>This "<strong>keep an ordered list of sources, resolve per-key closer-first</strong>" is far cleaner than "eagerly deep-merge all config into one big object." It doesn't pre-compute a merged result but <strong>keeps the sources as-is by priority, and whoever asks for a key, adjudicates that key on the spot</strong>. The benefit: each item's "<strong>which config it came from, why this value</strong>" stays crystal clear and traceable—to investigate "why is this model this," just look layer by layer down priority, never lost in a long-merged, source-obscured big object. <strong>Separating "which sources exist" from "which one an item finally takes" is the foundation of this config system's explainability.</strong> This explainability is hugely valuable in practice: when a teammate is puzzled "why does my agent use this odd model," the answer isn't to dig through a long-mashed merged object but to ask the ordered Entry list layer by layer "did this layer define model," instantly locating "oh, it's that .opencode in my own subdir." <strong>Config trouble's worst nightmare is "source is a mystery," and this design structurally keeps the source always traceable.</strong> This, lesson 41's permission <span class="mono">findLast</span> "last match wins," and lesson 37's registry "stack-top latest," is again the same "ordered sources, closer-first value" idea echoing in different places.</p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>Config loading is the source of "assembling an agent," feeding user intent to the whole system:</p>
  <ul>
    <li><strong>Config.Info = wiring harness</strong> (<span class="mono">config.ts</span>): a typed Schema class gathering nearly the whole system's knobs—model/shell, agents (L45), permissions (L41), mcp (L46), tool_output (L42), skills (L43), instructions/commands/lsp…. Loading = validation (schema is contract).</li>
    <li><strong>Layered discovery</strong>: recognizes <span class="mono">config.json/opencode.json/opencode.jsonc</span>; walks from the opened dir up to the project root finding <span class="mono">.opencode</span> and config files, plus the global config dir; sorted into <span class="mono">Entry</span> list (Document/Directory) low→high priority.</li>
    <li><strong>Closer-overrides</strong>: the source iron law "config closer to the opened dir wins." Priority: global (default) < project root < closer to cwd (most specific).</li>
    <li><strong>per-key closer-first adjudication</strong>: <span class="mono">latest(entries, key)</span> takes the value from "the highest-priority one defining that key" (per-item last-wins). Keep ordered sources, adjudicate per-key on the spot—more explainable, traceable than eager deep-merge. Same idea as lesson 41's <span class="mono">findLast</span>, lesson 37's "stack-top latest."</li>
  </ul>
  <p>With this "effective config," the next lesson (45) can cover <strong>Agents</strong>: how the <span class="mono">agents</span> cell becomes runnable agents, how built-in agents like build/plan are defined, how their prompts are assembled. Further, lesson 46 covers <strong>MCP</strong> (how the mcp cell connects out dynamic tools), lesson 47 covers <strong>Provider plugins</strong> (how dozens of model providers register). Config is the <strong>master switch</strong> of it all—it first gathers, validates, composes "what the user wants," then the downstream subsystems each take what they need and run.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p><span class="mono">latest</span>'s implementation writes "per-key closer-first value" plainly (simplified from config.ts):</p>
  <pre class="code"><span class="cm">// entries sorted low→high priority; take the value from the highest-priority one defining key</span>
<span class="kw">function</span> <span class="fn">latest</span>&lt;K&gt;(entries: Entry[], key: K) {
  <span class="kw">return</span> entries
    .<span class="fn">filter</span>(e =&gt; e.type === <span class="st">"document"</span>)   <span class="cm">// only config documents (Directory is supplemental)</span>
    .<span class="fn">map</span>(d =&gt; d.info[key])
    .<span class="fn">findLast</span>(v =&gt; v !== undefined)        <span class="cm">// the last (=highest-priority) one with a definition</span>
}</pre>
  <p>Note the <span class="mono">findLast</span> detail—the <strong>same method</strong> as lesson 41's permission <span class="mono">evaluate</span>: because entries are "low→high," <span class="mono">findLast</span> takes <strong>the highest-priority one with a definition</strong>, cleanly implementing "closer-overrides." This also explains why <span class="mono">Entry</span> splits <span class="mono">Document</span> (a config file) and <span class="mono">Directory</span> (a supplemental dir): some locations contribute not a "config value" but an "<strong>extra resource directory</strong>" (e.g. a folder holding skills, commands), which must also participate at the same priority, but <span class="mono">latest</span> only looks at <span class="mono">Document</span> when resolving. <strong>One filter + one findLast turns the complex-sounding "which one does layered config take" into three lines</strong>—again confirming: a good mechanism often relies not on complexity but on putting the right data structure (an ordered Entry list) and the right default (closer wins) in the right place.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>Config is the source of "assembling an agent"</strong>, M8's first lesson. <span class="mono">Config.Info</span> (<span class="mono">core/src/config.ts</span>) is a <strong>typed Schema wiring harness</strong> gathering nearly the whole system's knobs: model/shell, agents (L45), permissions (L41 Ruleset), mcp (L46), tool_output (L42), skills (L43), instructions/commands/lsp/formatter/compaction…. Loading = schema validation.</li>
    <li><strong>Layered discovery</strong>: recognizes <span class="mono">config.json/opencode.json/opencode.jsonc</span>; walks from the opened dir <strong>up to the project root</strong> finding <span class="mono">.opencode</span> and config files, plus the <strong>global config dir</strong>; sorted into <span class="mono">Entry[]</span> (<span class="mono">Document</span>=config file / <span class="mono">Directory</span>=supplemental dir) <strong>low→high priority</strong>.</li>
    <li><strong>Closer-overrides</strong> (source iron law): "config closer to the opened dir wins." Priority: global default < project root < closer-to-cwd exception. Maps to intent specificity—specific overrides broad.</li>
    <li><strong>per-key closer-first adjudication</strong>: <span class="mono">latest(entries, key)</span> = filter Documents → <span class="mono">findLast</span> with a definition (=highest priority). <strong>Per-item last-wins</strong>, keep ordered sources, adjudicate per-key on the spot—more explainable/traceable than eager deep-merge. Same "ordered sources, closer-first" idea as lesson 41's <span class="mono">findLast</span>, lesson 37's "stack-top latest."</li>
    <li>Config is the <strong>master switch</strong> for L45 Agents / L46 MCP / L47 Provider: it gathers, validates, composes user intent first, then subsystems take what they need.</li>
  </ul>
</div>
""",
}
LESSON_45 = {
    "zh": r"""
<p class="lead">上一课的配置，把「用户想要什么」收齐、校验、合成成一份生效配置。这一课，我们盯住其中最核心的一格——<span class="mono">agents</span>——看一个<strong>「agent」到底是什么</strong>，又是怎么从配置变成一个能跑的角色的。你可能以为「agent」是个很玄的东西，但 opencode 把它定义得朴素得惊人：<strong>一个 agent，就是一束「角色配置」</strong>——用哪个模型（脑）、配什么系统提示（指令）、有哪些权限（能干什么）、怎么跑（mode/步数上限）。把这几样一捆，给它起个名字，就是一个 agent。这种「把复杂的东西还原成一份配置」的做法，本身就值得玩味：它意味着「<strong>agent</strong>」不是一个需要写代码去 new 出来的对象，而是一份<strong>可以被声明、被配置、被用户随手定制</strong>的数据。你想要一个「专门写测试的 agent」「专门审查安全的 agent」？不必改一行 opencode 的源码，往配置里加一束角色卡即可。</p>
<p>这一课最有启发的，是 opencode 内置的<strong>两个 agent：<span class="mono">build</span> 和 <span class="mono">plan</span></strong>——它俩是理解整个 agent 抽象的最佳样本。<strong>build</strong> 是默认的全能编码 agent，能改文件、跑命令、放手干；<strong>plan</strong> 是「规划模式」，能读、能搜、能想，<strong>却被禁止动任何代码</strong>（只允许写计划文件）。最妙的是：<strong>build 和 plan 用的是同一套 agent 机器、同样的模型与工具，唯一的差别，几乎全在「权限画像」上</strong>。这把第 41 课的权限和这一课的 agent 漂亮地接在了一起——<strong>换一套权限，同一个 agent 引擎就活成了另一个角色</strong>。读懂 build vs plan，你就懂了「为什么 agent 这层抽象，本质是『脑 + 手 + 一张许可证』的命名打包」。</p>

<div class="card analogy">
  <div class="tag">🪪 生活类比</div>
  把一个 agent 想象成你派给一名员工的<strong>「岗位角色」</strong>。同一个员工（同一个模型 + 同一套工具），换一份<strong>岗位说明书</strong>（系统提示）、换一张<strong>门禁卡</strong>（权限），就成了两个截然不同的角色。<strong>build</strong> 像一名<strong>全权工程师</strong>：门禁卡能开所有门，可以直接改代码、提交、上线。<strong>plan</strong> 则像一名<strong>顾问</strong>：他能<strong>翻阅一切资料、四处考察</strong>，最后写出一份<strong>方案书</strong>——但他那张门禁卡，<strong>偏偏打不开「实际改动生产」的那扇门</strong>（只放他进「写方案」那一间）。同一个人、同一间办公室、同样的本事，<strong>只因门禁卡上的权限不同，就一个能动手、一个只能建言</strong>。agent 这层抽象的全部精髓，就在这「同一套人马、不同一张证」里。
</div>

<h2>一个 agent 是什么：一束角色配置</h2>
<p>先看 <span class="mono">core/src/agent.ts</span> 里的 <span class="mono">AgentV2.Info</span>——它就是「一个 agent」的定义。干净得像一张角色卡：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">model</div><div class="c-txt">用哪个模型（这个角色的「脑」）</div></div>
  <div class="cell"><div class="c-tag">system</div><div class="c-txt">系统提示（这个角色的「岗位说明书」）</div></div>
  <div class="cell"><div class="c-tag">mode</div><div class="c-txt">subagent / primary / all——能当主 agent、还是只能当子 agent</div></div>
  <div class="cell"><div class="c-tag">steps</div><div class="c-txt">步数上限（呼应第 20 课有界步数）</div></div>
  <div class="cell"><div class="c-tag">permissions</div><div class="c-txt">这个角色自己的权限规则集（第 41 课 Ruleset）</div></div>
  <div class="cell"><div class="c-tag">description / color / hidden</div><div class="c-txt">描述、UI 颜色、是否隐藏</div></div>
</div>
<p>看清楚这张卡，「agent」就不再玄了：它<strong>不是一段神秘的智能，而是一份『配置』</strong>——把「哪个脑（model）、什么指令（system）、什么许可（permissions）、怎么跑（mode/steps）」打包命名。默认 agent 的 ID 就叫 <span class="mono">"build"</span>（<span class="mono">defaultID = ID.make("build")</span>）。其中 <span class="mono">mode</span> 这一项决定它能出现在哪：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">primary</div><div class="c-txt">能作为你直接对话的主 agent（如 build/plan）</div></div>
  <div class="cell"><div class="c-tag">subagent</div><div class="c-txt">只能被其它 agent 当子任务派出去（回忆第 18 课 FiberSet 子任务）</div></div>
  <div class="cell"><div class="c-tag">all</div><div class="c-txt">两者皆可——既能当主、也能被派为子</div></div>
</div>
<p>这也解释了配置里的 <span class="mono">agents</span> 那一格：用户可以在配置中<strong>定义自己的 agent</strong>（给个名字、挑个模型、写段 system、设权限），于是「造一个新角色」就是「往配置里加一束这样的卡」。值得一提的是，核心的 <span class="mono">AgentV2.Info</span>（解析后的 agent）字段大多是<strong>必填带默认</strong>的（mode、permissions 都有定值），而配置侧的 <span class="mono">ConfigAgent.Info</span> 字段几乎全是<strong>可选</strong>的——因为配置只表达「我想覆盖什么」，没写的就走默认。这一「配置可选、解析必填」的分工，又是第 44 课「层叠覆盖」在 agent 上的具体落地。</p>

<h2>build vs plan：同一套机器，两张许可证</h2>
<p>现在来看最精彩的对照——opencode 内置的两个 primary agent。它俩的描述就把差别点透了：<span class="mono">build</span> = 「默认 agent，按配置的权限执行工具」；<span class="mono">plan</span> = 「<strong>规划模式，禁用一切编辑工具</strong>」。</p>
<div class="cols">
  <div class="col"><h4>build · 全权工程师</h4><p>默认 agent。权限=默认集 + 允许 question/plan_enter + 用户配置。<strong>能改文件、跑命令、放手干</strong>。你日常让 agent「去把这个实现了」，用的就是它。</p></div>
  <div class="col"><h4>plan · 只读顾问</h4><p>规划模式。权限在默认集上叠了一条狠的：<span class="mono">edit: {"*": "deny"}</span>——<strong>禁掉所有编辑</strong>，只对 <span class="mono">plans/*.md</span> 网开一面。它能读、能搜、能想，<strong>但碰不了你的真实代码</strong>，只能把方案写进计划文件。</p></div>
</div>
<p>这个对照是整个 agent 抽象的<strong>点睛之笔</strong>。注意：build 和 plan <strong>共用同一套 agent 引擎、同样的工具、（默认）同一个模型</strong>——它俩几乎一切都一样，<strong>唯一实质的差别，是那张「权限画像」</strong>。plan 的定义里，核心就是在默认权限上叠加：<span class="mono">edit: {"*": "deny", ".opencode/plans/*.md": "allow", …}</span>（禁所有编辑、只放行写计划文件）、<span class="mono">task.general: "deny"</span>、<span class="mono">plan_exit: "allow"</span>（允许退出规划模式回到 build）。换句话说：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">build</span><span class="t-txt">edit 默认放行 → 能直接改你的代码</span></div>
  <div class="t-row"><span class="t-num">plan</span><span class="t-txt">edit:* deny（除 plans/*.md）→ 只能读/搜/想 + 写方案，碰不了真实代码</span></div>
  <div class="t-row"><span class="t-num">切换</span><span class="t-txt">build 允许 plan_enter（进规划）、plan 允许 plan_exit（出规划）——两个模式可互相切</span></div>
</div>
<p>这就把第 41 课和这一课<strong>焊死</strong>了：<strong>agent 这层抽象之所以强大，正因为「角色的差异」很大程度上可以归结为「权限的差异」</strong>。你不需要为「规划模式」重写一套逻辑、再造一个引擎——你只要拿同一个 agent，<strong>换一张更严的许可证</strong>，它就自动变成了一个「只看不改」的规划者。这是一种极简的威力：<strong>把『这个 agent 能干什么』做成可声明的数据（权限规则），而非写死的代码</strong>，于是「造一个受限的新角色」轻得只剩「写几条 deny 规则」。plan 模式那条 <span class="mono">edit:"*":"deny"</span>，就是用一行声明，造出了一个「安全的、只规划不动手」的 agent。</p>
<p>再往深想一层，这种「角色 = 权限画像」的设计，给<strong>安全</strong>带来了巨大的好处。当你不太信任一个任务、或在一个敏感的代码库里干活时，你可以先用 <span class="mono">plan</span> 模式让 agent <strong>把方案想清楚、写下来</strong>——这期间它<strong>从结构上就不可能误改你的代码</strong>（不是「它保证不改」，而是「权限层面它根本改不了」）。你审完方案、满意了，再切到 <span class="mono">build</span> 让它动手。<strong>「先规划、后执行」这个对人类协作再自然不过的工作流，被 opencode 用『两个权限画像 + 可互切的模式』直接做进了产品</strong>。而这一切的底层，不过是「同一个 agent 引擎 + 两套不同的权限规则」——没有为 plan 模式特制的引擎、没有散落各处的「if 在 plan 模式则禁止」。<strong>当『角色』被还原成『一束可声明的配置 + 一张权限画像』，新角色、新模式就成了配置层面的事，而非又一轮代码工程。</strong>这正是好抽象的标志：它让本来要写代码才能办到的事，变成了填一张表就能办到。</p>

<h2>系统提示是怎么组装的</h2>
<p>一个 agent 的 <span class="mono">system</span>（系统提示）也不是凭空一段死文本，而是<strong>组装</strong>出来的。它把「角色的固有指令 + 用户配置的 system + 当前环境上下文」拼成模型最终看到的那段系统提示：</p>
<div class="flow">
  <div class="f-node">角色基底提示<br><small>该 agent 的固有指令</small></div>
  <div class="f-arrow">+ 用户 system →</div>
  <div class="f-node">配置里的 system 覆盖<br><small>用户对这个角色的额外要求</small></div>
  <div class="f-arrow">+ 环境上下文 →</div>
  <div class="f-node">M5 的 System Context<br><small>目录/git/日期…（第 21~27 课）</small></div>
</div>
<p>opencode 里还有一批<strong>专职内部 agent</strong>，它们的提示直接来自 <span class="mono">agent/prompt/*.txt</span> 文件——各司一项专门任务：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">explore.txt</div><div class="c-txt">探索子 agent（被派出去搜代码，回忆第 18 课）</div></div>
  <div class="cell"><div class="c-tag">compaction.txt</div><div class="c-txt">压缩历史的 agent（把长对话浓缩，呼应会话压缩）</div></div>
  <div class="cell"><div class="c-tag">summary.txt</div><div class="c-txt">生成摘要</div></div>
  <div class="cell"><div class="c-tag">title.txt</div><div class="c-txt">给会话起标题</div></div>
</div>
<p>把这些专职提示<strong>外置成 .txt 文件</strong>是个小而好的工程选择：提示词是<strong>会反复打磨的「文案」</strong>，把它从代码里拎出来放进纯文本，既好读好改、又能让非程序员参与调优，还不必为改一句话重新编译。<strong>agent 的「岗位说明书」，理应像文档一样被对待，而非像代码一样被编译。</strong>你会发现这些专职 agent 本身也印证了「agent = 一束配置」：一个 <span class="mono">explore</span> 子 agent，无非就是「一段 explore.txt 提示 + subagent 模式 + 一组适合搜索的工具与权限」的打包——和 build/plan 是同一套抽象，只是被裁成了更专、更窄的角色。<strong>从全能的 build，到只读的 plan，再到单一职责的 explore——它们全是同一张『角色卡』的不同填法。</strong></p>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <p>这一课把「配置里的 agents 那一格」具体成了能跑的角色：</p>
  <ul>
    <li><strong>一个 agent = 一束角色配置</strong>（<span class="mono">AgentV2.Info</span>，<span class="mono">core/src/agent.ts</span>）：model（脑）+ system（指令）+ permissions（许可，L41 Ruleset）+ mode（subagent/primary/all）+ steps（上限，L20）+ description/color/hidden。默认 agent ID = <span class="mono">"build"</span>。用户可在配置 <span class="mono">agents</span> 格自定义角色。</li>
    <li><strong>build vs plan = 同机器、异许可</strong>：build（默认全能、能编辑）vs plan（规划模式、<span class="mono">edit:"*":"deny"</span> 只放行写 plans/*.md）。<strong>唯一实质差别是权限画像</strong>——把第 41 课权限和 agent 抽象焊在一起：换一张许可证，同一引擎变一个角色。</li>
    <li><strong>mode 决定出场</strong>：primary（可作主 agent 直接对话）/ subagent（只能被派为子任务，L18）/ all。plan_enter / plan_exit 这两个权限动作，实现两模式互切。</li>
    <li><strong>system 是组装出来的</strong>：角色基底提示 + 配置 system 覆盖 + M5 环境上下文（L21~27）。专职内部 agent（explore/compaction/summary/title）的提示外置成 <span class="mono">agent/prompt/*.txt</span>——提示是文案，该当文档对待。</li>
  </ul>
  <p>有了「一个 agent 怎么定义、build/plan 怎么分」，下一课（第 46 课）讲 <strong>MCP 集成</strong>：配置里的 <span class="mono">mcp</span> 那一格，怎么把一个外部 MCP server 接成 agent 能用的<strong>动态工具</strong>（区别于第 37~43 课那些内置工具）。第 47 课讲 <strong>Provider 插件</strong>：几十家模型供应商怎么注册进来供 agent 的 <span class="mono">model</span> 字段挑选。配置（L44）定义意图，agent（L45）是意图凝成的角色，MCP（L46）与 Provider（L47）则把这个角色的「手」和「脑」接到更广的外部世界——一步步，一个真正可用、可定制的 agent 就被「攒」齐了。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p>plan agent 的权限定义，把「只读规划」写成了几条声明（简化自 opencode 的 agent 定义）：</p>
  <pre class="code"><span class="cm">// plan：在默认权限上叠加，核心是禁掉所有 edit</span>
plan: {
  name: <span class="st">"plan"</span>,
  description: <span class="st">"Plan mode. Disallows all edit tools."</span>,
  permission: Permission.<span class="fn">merge</span>(defaults, Permission.<span class="fn">fromConfig</span>({
    question: <span class="st">"allow"</span>,
    plan_exit: <span class="st">"allow"</span>,                 <span class="cm">// 允许退出规划模式</span>
    task: { general: <span class="st">"deny"</span> },
    edit: {
      <span class="st">"*"</span>: <span class="st">"deny"</span>,                       <span class="cm">// ← 禁掉所有编辑</span>
      <span class="st">".opencode/plans/*.md"</span>: <span class="st">"allow"</span>,    <span class="cm">// 只放行写计划文件</span>
    },
  }), user),
  mode: <span class="st">"primary"</span>, native: <span class="kw">true</span>,
}</pre>
  <p>注意 <span class="mono">Permission.merge(defaults, …, user)</span> 这个顺序——它正是第 44 课「分层就近覆盖」的同款思路：<strong>默认权限垫底、agent 自己的规则叠中间、用户配置盖最上</strong>。于是用户始终能<strong>在最高优先级覆盖</strong>掉内置 agent 的任何一条权限（比如你嫌 plan 太严，可以在自己的配置里给它放开某些 edit）。还有个值得品的细节：plan 不是「<strong>什么都不能写</strong>」，而是「<strong>除了写计划文件，什么都不能写</strong>」——<span class="mono">.opencode/plans/*.md</span> 那条 allow，给规划者留了一支「<strong>把方案落到纸上</strong>」的笔。一个真正有用的规划模式，不该是个哑巴，它得能把想出来的方案<strong>持久地写下来</strong>，供你审阅、供后续的 build 模式照着做。<strong>用权限规则的『禁中有放』，精确地雕出一个角色的行为边界</strong>——这比写一堆 if-else 判断「这个 agent 此刻能不能 edit」优雅太多。更进一步说，把边界写成<strong>声明式的数据</strong>，意味着它既能被静态地读懂与审查，也能被用户在配置里逐条覆盖、组合出自己想要的角色，而无需理解引擎内部任何一行控制流——这正是「角色即权限画像」这套设计真正的可扩展性所在。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>一个 agent = 一束角色配置</strong>（<span class="mono">AgentV2.Info</span>，<span class="mono">core/src/agent.ts</span>）：<span class="mono">model</span>（脑）+ <span class="mono">system</span>（指令）+ <span class="mono">permissions</span>（许可，L41 Ruleset）+ <span class="mono">mode</span>（subagent/primary/all）+ <span class="mono">steps</span>（上限，L20）+ description/color/hidden。默认 ID=<span class="mono">"build"</span>。用户可在配置 <span class="mono">agents</span> 格自定义。</li>
    <li><strong>build vs plan = 同一套引擎、两张许可证</strong>：build=默认全能（能 edit）；plan=「规划模式，禁用一切编辑工具」，核心是 <span class="mono">edit:{"*":"deny", "plans/*.md":"allow"}</span> + <span class="mono">task.general:deny</span> + <span class="mono">plan_exit:allow</span>。<strong>唯一实质差别是权限画像</strong>——焊接第 41 课与 agent 抽象。</li>
    <li><strong>把「能干什么」做成可声明数据而非死代码</strong>：造受限角色 = 写几条 deny 规则。plan 的 <span class="mono">edit:"*":"deny"</span> 一行声明出一个「只规划不动手」的安全 agent。</li>
    <li><strong>mode 决定出场</strong>：primary（主 agent）/ subagent（只被派为子任务，L18）/ all。<span class="mono">plan_enter</span>/<span class="mono">plan_exit</span> 实现 build↔plan 互切。</li>
    <li><strong>system 是组装的</strong>：角色基底 + 配置 system 覆盖 + M5 环境上下文（L21~27）。专职内部 agent 提示外置 <span class="mono">agent/prompt/*.txt</span>（explore/compaction/summary/title）——提示是文案，该当文档对待。<span class="mono">Permission.merge(defaults, agent, user)</span> 顺序=第 44 课就近覆盖，用户始终能最高优先级覆盖。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Last lesson's config gathered, validated, and composed "what the user wants" into one effective config. This lesson fixes on its most core cell—<span class="mono">agents</span>—to see <strong>what an "agent" actually is</strong>, and how it becomes a runnable role from config. You might think "agent" is something mystical, but opencode defines it strikingly plainly: <strong>an agent is a bundle of "role config"</strong>—which model (brain), what system prompt (instructions), which permissions (what it can do), how it runs (mode/step cap). Bundle these, give it a name, and that's an agent. This "reduce the complex into a config" approach is itself worth savoring: it means "<strong>agent</strong>" isn't an object you must write code to new up, but data that can be <strong>declared, configured, customized by the user at will</strong>. Want a "test-writing agent" or a "security-review agent"? No need to change a line of opencode source—just add a role card to the config.</p>
<p>This lesson's most illuminating part is opencode's two built-in agents: <strong><span class="mono">build</span> and <span class="mono">plan</span></strong>—the best sample for understanding the whole agent abstraction. <strong>build</strong> is the default all-around coding agent, able to edit files, run commands, do anything; <strong>plan</strong> is "plan mode," able to read, search, think, <strong>yet forbidden from touching any code</strong> (allowed only to write plan files). The cleverest part: <strong>build and plan use the same agent machinery, the same model and tools, and the only difference is almost entirely in the "permission profile."</strong> This beautifully connects lesson 41's permissions with this lesson's agent—<strong>swap a permission set, and the same agent engine lives as a different role</strong>. Grasp build vs plan and you'll understand "why the agent abstraction is, at heart, a named packaging of 'brain + hands + a permit.'"</p>

<div class="card analogy">
  <div class="tag">🪪 Analogy</div>
  Picture an agent as a <strong>"job role"</strong> you assign to an employee. The same employee (same model + same tools), with a different <strong>job description</strong> (system prompt) and a different <strong>access badge</strong> (permissions), becomes two wholly different roles. <strong>build</strong> is like a <strong>full-authority engineer</strong>: the badge opens all doors, can directly change code, commit, deploy. <strong>plan</strong> is like a <strong>consultant</strong>: he can <strong>read everything, survey everywhere</strong>, and finally write a <strong>proposal</strong>—but his badge <strong>just won't open the door to "actually change production"</strong> (only lets him into the "write proposal" room). Same person, same office, same skills, <strong>yet only because the badge's permissions differ, one can act and the other can only advise</strong>. The whole essence of the agent abstraction is in this "same crew, different badge."
</div>

<h2>What an agent is: a bundle of role config</h2>
<p>First look at <span class="mono">AgentV2.Info</span> in <span class="mono">core/src/agent.ts</span>—it's the definition of "an agent." Clean as a role card:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">model</div><div class="c-txt">which model (this role's "brain")</div></div>
  <div class="cell"><div class="c-tag">system</div><div class="c-txt">system prompt (this role's "job description")</div></div>
  <div class="cell"><div class="c-tag">mode</div><div class="c-txt">subagent / primary / all—can it be a primary agent, or only a subagent</div></div>
  <div class="cell"><div class="c-tag">steps</div><div class="c-txt">step cap (echoing lesson 20's bounded steps)</div></div>
  <div class="cell"><div class="c-tag">permissions</div><div class="c-txt">this role's own permission ruleset (lesson 41's Ruleset)</div></div>
  <div class="cell"><div class="c-tag">description / color / hidden</div><div class="c-txt">description, UI color, whether hidden</div></div>
</div>
<p>See this card and "agent" stops being mystical: it's <strong>not a mysterious intelligence but a "config"</strong>—packaging and naming "which brain (model), what instructions (system), what permits (permissions), how it runs (mode/steps)." The default agent's ID is <span class="mono">"build"</span> (<span class="mono">defaultID = ID.make("build")</span>). The <span class="mono">mode</span> item decides where it can appear:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">primary</div><div class="c-txt">can be a primary agent you converse with directly (e.g. build/plan)</div></div>
  <div class="cell"><div class="c-tag">subagent</div><div class="c-txt">only dispatchable as a subtask by other agents (recall lesson 18's FiberSet subtasks)</div></div>
  <div class="cell"><div class="c-tag">all</div><div class="c-txt">both—can be primary, can also be dispatched as a sub</div></div>
</div>
<p>This also explains the config's <span class="mono">agents</span> cell: the user can <strong>define their own agents</strong> in config (give a name, pick a model, write a system, set permissions), so "make a new role" is "add such a card to the config." Worth noting, the core <span class="mono">AgentV2.Info</span> (the resolved agent) has mostly <strong>required-with-default</strong> fields (mode, permissions have set values), while the config-side <span class="mono">ConfigAgent.Info</span> fields are almost all <strong>optional</strong>—because config only expresses "what I want to override," with unwritten ones defaulting. This "config optional, resolved required" division is again lesson 44's "cascade override" landing on agents.</p>

<h2>build vs plan: same machinery, two badges</h2>
<p>Now the most brilliant contrast—opencode's two built-in primary agents. Their descriptions nail the difference: <span class="mono">build</span> = "the default agent, executes tools per configured permissions"; <span class="mono">plan</span> = "<strong>plan mode, disallows all edit tools</strong>."</p>
<div class="cols">
  <div class="col"><h4>build · full-authority engineer</h4><p>The default agent. Permissions = default set + allow question/plan_enter + user config. <strong>Can change files, run commands, do anything</strong>. When you daily tell an agent "go implement this," that's it.</p></div>
  <div class="col"><h4>plan · read-only consultant</h4><p>Plan mode. Its permissions layer one fierce rule on the default set: <span class="mono">edit: {"*": "deny"}</span>—<strong>deny all edits</strong>, with only <span class="mono">plans/*.md</span> spared. It can read, search, think, <strong>but can't touch your real code</strong>, only write the proposal into a plan file.</p></div>
</div>
<p>This contrast is the agent abstraction's <strong>crowning touch</strong>. Note: build and plan <strong>share the same agent engine, the same tools, the (default) same model</strong>—nearly everything is the same, <strong>the only substantive difference is that "permission profile."</strong> plan's definition is essentially layering on the default permissions: <span class="mono">edit: {"*": "deny", ".opencode/plans/*.md": "allow", …}</span> (deny all edits, allow only writing plan files), <span class="mono">task.general: "deny"</span>, <span class="mono">plan_exit: "allow"</span> (allow exiting plan mode back to build). In other words:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">build</span><span class="t-txt">edit default-allowed → can directly change your code</span></div>
  <div class="t-row"><span class="t-num">plan</span><span class="t-txt">edit:* deny (except plans/*.md) → only read/search/think + write proposal, can't touch real code</span></div>
  <div class="t-row"><span class="t-num">switch</span><span class="t-txt">build allows plan_enter (into plan), plan allows plan_exit (out of plan)—the two modes interconvert</span></div>
</div>
<p>This <strong>welds</strong> lesson 41 and this lesson together: <strong>the agent abstraction is powerful precisely because "role differences" can largely reduce to "permission differences."</strong> You needn't rewrite logic for "plan mode" or build another engine—you just take the same agent, <strong>swap a stricter badge</strong>, and it automatically becomes a "look-don't-change" planner. It's a minimalist power: <strong>make "what this agent can do" declarable data (permission rules), not hardcoded code</strong>, so "make a restricted new role" gets as light as "write a few deny rules." plan mode's <span class="mono">edit:"*":"deny"</span> is one declaration making a "safe, plan-only, hands-off" agent.</p>
<p>One layer deeper, this "role = permission profile" design brings huge <strong>security</strong> benefits. When you don't quite trust a task, or work in a sensitive codebase, you can first use <span class="mono">plan</span> mode to have the agent <strong>think the proposal through and write it down</strong>—during which it's <strong>structurally incapable of mis-editing your code</strong> (not "it promises not to change," but "at the permission level it simply can't"). You review the plan, satisfied, then switch to <span class="mono">build</span> to act. <strong>The "plan first, execute later" workflow, so natural to human collaboration, is baked straight into the product by opencode via "two permission profiles + interconvertible modes."</strong> And underneath it all is merely "the same agent engine + two different permission sets"—no plan-mode-bespoke engine, no scattered "if in plan mode then forbid." <strong>When a "role" is reduced to "a bundle of declarable config + a permission profile," new roles and modes become a config-level matter, not another round of code engineering.</strong> That's the mark of a good abstraction: it turns what would take code into what a filled-in form can do.</p>

<h2>How the system prompt is assembled</h2>
<p>An agent's <span class="mono">system</span> (system prompt) isn't some out-of-nowhere fixed text either, but <strong>assembled</strong>. It stitches "the role's inherent instructions + the user's config system + the current environment context" into the system prompt the model finally sees:</p>
<div class="flow">
  <div class="f-node">role base prompt<br><small>this agent's inherent instructions</small></div>
  <div class="f-arrow">+ user system →</div>
  <div class="f-node">config's system override<br><small>the user's extra demands on this role</small></div>
  <div class="f-arrow">+ env context →</div>
  <div class="f-node">M5's System Context<br><small>directory/git/date… (lessons 21–27)</small></div>
</div>
<p>opencode also has a batch of <strong>dedicated internal agents</strong>, whose prompts come straight from <span class="mono">agent/prompt/*.txt</span> files—each for a specialized task:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">explore.txt</div><div class="c-txt">explore subagent (dispatched to search code, recall lesson 18)</div></div>
  <div class="cell"><div class="c-tag">compaction.txt</div><div class="c-txt">history-compacting agent (condensing long conversations)</div></div>
  <div class="cell"><div class="c-tag">summary.txt</div><div class="c-txt">generating summaries</div></div>
  <div class="cell"><div class="c-tag">title.txt</div><div class="c-txt">titling a session</div></div>
</div>
<p>Externalizing these dedicated prompts into <strong>.txt files</strong> is a small good engineering choice: prompts are <strong>"copy" that gets refined repeatedly</strong>, and pulling them out of code into plain text makes them easy to read/change, lets non-programmers tune them, and avoids recompiling to change a sentence. <strong>An agent's "job description" deserves to be treated like a document, not compiled like code.</strong> You'll find these dedicated agents themselves confirm "agent = a bundle of config": an <span class="mono">explore</span> subagent is just a packaging of "an explore.txt prompt + subagent mode + a set of search-suited tools and permissions"—the same abstraction as build/plan, only cut into a narrower, more specialized role. <strong>From the all-around build, to the read-only plan, to the single-purpose explore—they're all different fillings of the same "role card."</strong></p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>This lesson makes "the config's agents cell" concrete into runnable roles:</p>
  <ul>
    <li><strong>An agent = a bundle of role config</strong> (<span class="mono">AgentV2.Info</span>, <span class="mono">core/src/agent.ts</span>): model (brain) + system (instructions) + permissions (permit, L41 Ruleset) + mode (subagent/primary/all) + steps (cap, L20) + description/color/hidden. Default agent ID = <span class="mono">"build"</span>. The user can customize roles in the config <span class="mono">agents</span> cell.</li>
    <li><strong>build vs plan = same machinery, different badges</strong>: build (default all-around, can edit) vs plan (plan mode, <span class="mono">edit:"*":"deny"</span> allowing only writing plans/*.md). <strong>The only substantive difference is the permission profile</strong>—welding lesson 41's permissions to the agent abstraction: swap a badge, the same engine becomes a different role.</li>
    <li><strong>mode decides appearance</strong>: primary (can be a directly-conversed primary agent) / subagent (only dispatchable as a subtask, L18) / all. The <span class="mono">plan_enter</span> / <span class="mono">plan_exit</span> permission actions interconvert the two modes.</li>
    <li><strong>system is assembled</strong>: role base prompt + config system override + M5 env context (L21–27). Dedicated internal agents' (explore/compaction/summary/title) prompts externalized into <span class="mono">agent/prompt/*.txt</span>—prompts are copy, treat them as documents. <span class="mono">Permission.merge(defaults, agent, user)</span> order = lesson 44's closer-overrides, the user always overrides at highest priority.</li>
  </ul>
  <p>With "how an agent is defined, how build/plan differ," the next lesson (46) covers <strong>MCP integration</strong>: how the config's <span class="mono">mcp</span> cell connects an external MCP server into <strong>dynamic tools</strong> the agent can use (distinct from lessons 37–43's built-in tools). Lesson 47 covers <strong>Provider plugins</strong>: how dozens of model providers register for the agent's <span class="mono">model</span> field to pick. Config (L44) defines intent, the agent (L45) is intent crystallized into a role, MCP (L46) and Provider (L47) connect this role's "hands" and "brain" to the wider external world—step by step, a truly usable, customizable agent gets "assembled."</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p>The plan agent's permission definition writes "read-only planning" as a few declarations (simplified from opencode's agent definition):</p>
  <pre class="code"><span class="cm">// plan: layered on default permissions, the core is denying all edit</span>
plan: {
  name: <span class="st">"plan"</span>,
  description: <span class="st">"Plan mode. Disallows all edit tools."</span>,
  permission: Permission.<span class="fn">merge</span>(defaults, Permission.<span class="fn">fromConfig</span>({
    question: <span class="st">"allow"</span>,
    plan_exit: <span class="st">"allow"</span>,                 <span class="cm">// allow exiting plan mode</span>
    task: { general: <span class="st">"deny"</span> },
    edit: {
      <span class="st">"*"</span>: <span class="st">"deny"</span>,                       <span class="cm">// ← deny all edits</span>
      <span class="st">".opencode/plans/*.md"</span>: <span class="st">"allow"</span>,    <span class="cm">// allow only writing plan files</span>
    },
  }), user),
  mode: <span class="st">"primary"</span>, native: <span class="kw">true</span>,
}</pre>
  <p>Note the <span class="mono">Permission.merge(defaults, …, user)</span> order—exactly lesson 44's "layered closer-overrides" idea: <strong>default permissions at the bottom, the agent's own rules in the middle, user config on top</strong>. So the user can always <strong>override at the highest priority</strong> any of a built-in agent's permission rules (e.g. if you find plan too strict, you can open some edits for it in your own config). Another savory detail: plan isn't "<strong>can write nothing</strong>" but "<strong>can write nothing except plan files</strong>"—that <span class="mono">.opencode/plans/*.md</span> allow leaves the planner a pen to "<strong>commit the proposal to paper</strong>." A truly useful plan mode shouldn't be mute; it must be able to <strong>persistently write down</strong> the proposal it conceives, for you to review and for a subsequent build mode to follow. <strong>Using permission rules' "denial with exceptions" to precisely carve a role's behavioral boundary</strong>—far more elegant than a pile of if-else judging "can this agent edit right now."</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>An agent = a bundle of role config</strong> (<span class="mono">AgentV2.Info</span>, <span class="mono">core/src/agent.ts</span>): <span class="mono">model</span> (brain) + <span class="mono">system</span> (instructions) + <span class="mono">permissions</span> (permit, L41 Ruleset) + <span class="mono">mode</span> (subagent/primary/all) + <span class="mono">steps</span> (cap, L20) + description/color/hidden. Default ID=<span class="mono">"build"</span>. User-customizable in the config <span class="mono">agents</span> cell.</li>
    <li><strong>build vs plan = same engine, two badges</strong>: build=default all-around (can edit); plan="plan mode, disallows all edit tools," core being <span class="mono">edit:{"*":"deny", "plans/*.md":"allow"}</span> + <span class="mono">task.general:deny</span> + <span class="mono">plan_exit:allow</span>. <strong>The only substantive difference is the permission profile</strong>—welding lesson 41 to the agent abstraction.</li>
    <li><strong>Make "what it can do" declarable data, not hardcoded code</strong>: making a restricted role = writing a few deny rules. plan's <span class="mono">edit:"*":"deny"</span> declares a "plan-only, hands-off" safe agent in one line; enables the "plan first, execute later" secure workflow.</li>
    <li><strong>mode decides appearance</strong>: primary (primary agent) / subagent (only dispatched as a subtask, L18) / all. <span class="mono">plan_enter</span>/<span class="mono">plan_exit</span> interconvert build↔plan.</li>
    <li><strong>system is assembled</strong>: role base + config system override + M5 env context (L21–27). Dedicated internal agent prompts externalized as <span class="mono">agent/prompt/*.txt</span> (explore/compaction/summary/title)—prompts are copy, treat as documents. <span class="mono">Permission.merge(defaults, agent, user)</span> order = lesson 44's closer-overrides, user always overrides at highest priority.</li>
  </ul>
</div>
""",
}
LESSON_46 = wip('MCP 集成', 'MCP integration')
LESSON_47 = wip('Provider 插件定义', 'Provider plugins')
