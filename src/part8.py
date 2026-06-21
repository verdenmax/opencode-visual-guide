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
LESSON_45 = wip('Agents：build 与 plan', 'Agents: build & plan')
LESSON_46 = wip('MCP 集成', 'MCP integration')
LESSON_47 = wip('Provider 插件定义', 'Provider plugins')
