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
LESSON_46 = {
    "zh": r"""
<p class="lead">前面三课（L37–43）讲的工具，都是 opencode <strong>自己写死在源码里</strong>的：read、bash、grep……它们在编译期就定义好了，数量固定。但 AI agent 真正的威力，在于能<strong>临时接上你自己的工具</strong>——查公司内部数据库、调某个 SaaS 的 API、操作你私有的服务。这正是 <strong>MCP（Model Context Protocol，模型上下文协议）</strong>要解决的：它是一套标准协议，让你把<strong>外部的「工具服务器」</strong>接进 opencode，服务器上有什么工具，agent 运行时就<strong>动态地</strong>多出什么工具。这一课的两条主线，正是 MCP 集成最精彩的两面：<strong>动态作用域工具</strong>（外部工具如何被发现、命名、并入和内置工具同一套体系）和 <strong>OAuth</strong>（远程服务器需要登录授权时，那套浏览器回调的认证舞蹈）。</p>
<p>这一课最值得你带走的洞见是：<strong>MCP 工具「出身是二等公民，待遇是一等公民」</strong>。它们不是 opencode 亲手写的，而是运行时从一个外部服务器「问」来的；但一旦被发现，它们就被<strong>裹进和内置工具一模一样的外壳</strong>，并入<strong>同一个工具注册表</strong>（L37）、走<strong>同一道权限闸门</strong>（L41）、被<strong>同一批插件钩子</strong>观察。对模型、对会话循环、对权限系统来说，一个 MCP 工具和一个内置 read 工具<strong>长得完全一样</strong>——唯一的差别，藏在它 <span class="mono">execute()</span> 的最深处：内置工具在本地跑代码，MCP 工具则把调用<strong>转发给那台远程/本地的服务器</strong>。读懂这件事，你就懂了「一个好的扩展机制，是如何让『外来的』和『原生的』在系统里平起平坐的」。</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  把 opencode 的内置工具想象成一台电脑<strong>出厂自带的端口</strong>（USB、HDMI）——数量固定、焊死在主板上。而 MCP，就像给这台电脑接上一个 <strong>USB 拓展坞</strong>：你插上拓展坞（配一台 MCP 服务器），它上面有几个口（服务器提供几个工具），电脑<strong>当场就多认出几个设备</strong>，无需重装系统、不必拆机焊新口。更妙的是，操作系统对待拓展坞上的设备，和对待主板自带口上的设备<strong>一视同仁</strong>——同样要走驱动、同样受权限管控。而 OAuth，就像有些<strong>付费拓展坞要先刷一下你的会员卡</strong>：你得先在官网登录、授权，拿到一张「通行令牌」，之后这台拓展坞才肯为你工作——而这张令牌会被妥善锁进抽屉，下次免刷。
</div>

<h2>动态工具：运行时发现，裹成同一副外壳</h2>
<p>内置工具（L36）是 <span class="mono">Tool.make(...)</span> 在编译期写死的；MCP 工具恰恰相反——它们在<strong>运行时</strong>才被「发现」。opencode 连上一台 MCP 服务器后，向它发一个 <span class="mono">tools/list</span> 请求，把服务器<strong>当场报上来</strong>的工具定义，逐个裹进 AI SDK 的 <span class="mono">dynamicTool(...)</span>：</p>
<div class="flow">
  <div class="f-node">连上 MCP 服务器<br><small>本地进程 / 远程 HTTP</small></div>
  <div class="f-arrow">listTools →</div>
  <div class="f-node">服务器报出工具定义<br><small>name + inputSchema + description</small></div>
  <div class="f-arrow">convertTool →</div>
  <div class="f-node">裹进 dynamicTool<br><small>execute=client.callTool</small></div>
  <div class="f-arrow">并入 →</div>
  <div class="f-node">同一个工具注册表<br><small>和内置工具肩并肩</small></div>
</div>
<p>关键在 <span class="mono">catalog.ts</span> 的 <span class="mono">convertTool</span>：它把 MCP 服务器报的工具定义，转成一个 <span class="mono">dynamicTool</span>——保留服务器给的 <span class="mono">inputSchema</span> 作参数约束，而 <span class="mono">execute</span> 的实现，只是<strong>把参数原样转发</strong>给 <span class="mono">client.callTool(name, args)</span>，再把服务器返回的结果转回来。所谓「dynamic（动态）」，正是相对于内置工具的「static（静态）」而言：内置工具的 schema 和实现都写在源码里，而 MCP 工具的 schema 是运行时问来的、实现只是一根<strong>通往远端的转发线</strong>。这里还藏着一个呼应全书的主题——「<strong>便宜地广而告之，按需地昂贵兑现</strong>」（L37 注册表只存定义、L42 预览/溢出、L43 skills 只报名字）：opencode 连上服务器时，只<strong>廉价地拉一份工具清单</strong>（名字 + schema + 描述），真正昂贵的工具执行，要等模型<strong>实际点名调用</strong>那一刻，才通过 <span class="mono">callTool</span> 转发过去。一台 MCP 服务器哪怕提供上百个工具，发现阶段也只是过一遍清单，绝不会预先把它们全跑一遍。</p>
<p>那「作用域（scoped）」又是什么意思？多台 MCP 服务器可能各有一个叫 <span class="mono">search</span> 的工具，怎么不打架？opencode 的办法是给每个工具名<strong>冠上服务器名做前缀</strong>。名字先经 <span class="mono">sanitize</span> 洗一遍（把非 <span class="mono">[a-zA-Z0-9_-]</span> 的字符替换成 <span class="mono">_</span>），再用 <span class="mono">:</span>（冒号）拼起来：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">sanitize</div><div class="c-txt"><span class="mono">/[^a-zA-Z0-9_-]/g → "_"</span>：洗掉工具名里不合法的字符</div></div>
  <div class="cell"><div class="c-tag">命名规则</div><div class="c-txt"><span class="mono">sanitize(服务器名) + ":" + sanitize(工具名)</span></div></div>
  <div class="cell"><div class="c-tag">例子</div><div class="c-txt">github 服务器的 search → <span class="mono">github:search</span>；jira 的 search → <span class="mono">jira:search</span>，互不冲突</div></div>
</div>
<p>这个带前缀的名字，就是 MCP 工具的「作用域」——它既避免了重名冲突，又让模型一眼看出某工具来自哪台服务器。而这串名字最妙的去处在 <span class="mono">session/tools.ts</span>：MCP 工具被并入会话工具集时，那道权限闸门写的是 <span class="mono">ctx.ask({ permission: key, ... })</span>——<strong>这个 key，正是上面那个带服务器前缀的作用域名</strong>。也就是说，MCP 工具<strong>和内置工具走的是同一套权限系统</strong>（第 41 课的 Ruleset），你完全可以在配置里写「<span class="mono">github:*</span> 一律放行、<span class="mono">jira:delete_*</span> 必须问」这样的规则，精确管控每台外部服务器、每个外部工具的权限。这就是开头那句「待遇是一等公民」的落地：<strong>外来工具一旦进门，就和原生工具共享注册表、权限、插件钩子，没有半点二等待遇。</strong></p>

<h2>两种服务器：本地进程 vs 远程 HTTP</h2>
<p>MCP 服务器从哪来？配置里 <span class="mono">mcp</span> 那一格（<span class="mono">config/mcp.ts</span>）定义了两种，是一个按 <span class="mono">type</span> 区分的标签联合：</p>
<div class="cols">
  <div class="col"><h4>local · 本地进程</h4><p><span class="mono">type:"local"</span>，给一条 <span class="mono">command</span>（命令 + 参数）。opencode 用 <strong>StdioClientTransport</strong> 把它<strong>当子进程拉起来</strong>，通过标准输入/输出（stdio）和它通信。适合跑在你机器上的工具服务器。还可配 <span class="mono">cwd</span>（工作目录）、<span class="mono">environment</span>（环境变量）。</p></div>
  <div class="col"><h4>remote · 远程 HTTP</h4><p><span class="mono">type:"remote"</span>，给一个 <span class="mono">url</span>。opencode 通过 HTTP 连它，<strong>先试 StreamableHTTP，失败再回退到 SSE</strong>。适合接公网上的托管服务。可配 <span class="mono">headers</span>（自定义请求头）和 <span class="mono">oauth</span>（认证，见下一节）。</p></div>
</div>
<p>这套配置 schema 同样朴素得像填表：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">Local</div><div class="c-txt"><span class="mono">command[]</span>（必填）、<span class="mono">cwd?</span>、<span class="mono">environment?</span>、<span class="mono">disabled?</span>、<span class="mono">timeout?</span></div></div>
  <div class="cell"><div class="c-tag">Remote</div><div class="c-txt"><span class="mono">url</span>（必填）、<span class="mono">headers?</span>、<span class="mono">oauth?</span>、<span class="mono">disabled?</span>、<span class="mono">timeout?</span></div></div>
  <div class="cell"><div class="c-tag">连接安全</div><div class="c-txt"><span class="mono">connectTransport</span> 用 acquireUseRelease：连接失败就<strong>自动关掉 transport</strong>，绝不泄漏进程/连接</div></div>
</div>
<p>两种 transport 殊途同归：无论是本地拉起的子进程，还是远程 HTTP 连接，连上后<strong>都得到同一个 MCP <span class="mono">Client</span></strong>，后续 <span class="mono">listTools</span>、<span class="mono">callTool</span> 的代码<strong>完全一样</strong>——传输层的差异，被 MCP SDK 的 transport 抽象彻底吃掉了。这又是一处好设计：<strong>把「怎么连」和「连上之后怎么用」干净地切开</strong>，上层逻辑根本不必关心工具究竟来自本地进程还是远端服务。而那个「先试 StreamableHTTP、失败再回退 SSE」的小细节也颇有讲究：StreamableHTTP 是较新的、更高效的双向流式传输，SSE（Server-Sent Events）则是更老、更通用的回退方案——opencode 优先用新的、连不上才退而求其次，既吃到新协议的好处，又不至于把只支持老协议的服务器拒之门外。<strong>「优先用更好的，但永远留一条兼容的退路」</strong>，是接入异构外部世界时最务实的姿态。</p>

<h2>OAuth：远程服务器的登录授权舞蹈</h2>
<p>远程服务器常常需要<strong>认证</strong>——它凭什么让你调它的工具？MCP 用的是标准的 <strong>OAuth</strong>。opencode 第一次连一台需要认证的远程服务器时，会撞上 <span class="mono">UnauthorizedError</span>，于是把该服务器标成 <span class="mono">needs_auth</span> 状态，并提示你：<span class="mono">运行 opencode mcp auth &lt;名字&gt;</span>。这之后，就是一段经典的「浏览器回调」认证舞蹈：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">你运行 <span class="mono">opencode mcp auth &lt;名字&gt;</span></span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">opencode 在本机起一个 <strong>localhost 回调 HTTP 服务器</strong>（监听 callback 端口）</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">打开<strong>浏览器</strong>跳到服务器的授权页（带 PKCE 的 code_challenge + state 防 CSRF）</span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">你在那个页面<strong>登录、授权</strong></span></div>
  <div class="t-row"><span class="t-num">5</span><span class="t-txt">服务器把浏览器<strong>重定向回</strong> <span class="mono">localhost:端口/callback?code=…&amp;state=…</span></span></div>
  <div class="t-row"><span class="t-num">6</span><span class="t-txt">回调服务器<strong>截获 code</strong>、核对 state，拿 code + PKCE 的 code_verifier <strong>换取令牌</strong></span></div>
  <div class="t-row"><span class="t-num">7</span><span class="t-txt">令牌<strong>存进</strong> <span class="mono">mcp-auth.json</span>；之后每次连接，transport 自动带上令牌，免再登录</span></div>
</div>
<p>这套流程里有几样必须<strong>持久保存</strong>的「凭证碎片」，由 <span class="mono">auth.ts</span> 统一锁进 <span class="mono">mcp-auth.json</span> 管理：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">tokens</div><div class="c-txt">accessToken / refreshToken / expiresAt——真正的通行令牌（含过期时间）</div></div>
  <div class="cell"><div class="c-tag">codeVerifier</div><div class="c-txt">PKCE 校验码：授权时生成，换令牌时回证，防授权码被劫持</div></div>
  <div class="cell"><div class="c-tag">oauthState</div><div class="c-txt">随机 state：防 CSRF，回调时核对是否同一次发起</div></div>
  <div class="cell"><div class="c-tag">clientInfo</div><div class="c-txt">动态客户端注册拿到的 clientId/secret（服务器不支持时需手填 clientId）</div></div>
</div>
<p>一处值得品的安全细节：<span class="mono">mcp-auth.json</span> 写入时用的是 <span class="mono">0o600</span> 权限（仅文件主可读写）——令牌是<strong>敏感凭证</strong>，理应锁死，绝不能让同机其他用户读到。而且整个文件读写都用<strong>文件锁</strong>（flock）串行化，避免多个 opencode 进程同时改这份认证文件、把彼此的令牌冲掉。还有个体贴的设计：当服务器<strong>不支持「动态客户端注册」</strong>时，opencode 不会傻等，而是把状态标成 <span class="mono">needs_client_registration</span> 并弹出明确提示——「请在配置里手动提供 clientId」。<strong>把每一种认证失败都翻译成一句人能照做的话</strong>，而非甩一个晦涩的 OAuth 报错，这是把「协议的复杂」挡在用户体验之外的功夫。还有一层值得一提：令牌不是一劳永逸的，<span class="mono">tokens</span> 里带 <span class="mono">expiresAt</span>（过期时间），<span class="mono">auth.ts</span> 专门有个 <span class="mono">isTokenExpired</span> 来判断令牌是否过期——配合 <span class="mono">refreshToken</span>，opencode 能在令牌快到期时<strong>悄悄续期</strong>，而不必每次都把你拽回浏览器重登一遍。<strong>「一次授权，长期免登」</strong>背后，正是这套 tokens + 过期判断 + 刷新令牌的小机制在默默兜底——好的认证体验，是让用户只在第一次有感、之后近乎无感。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观视角</div>
  <p>这一课讲清了 opencode 如何把<strong>外部工具</strong>动态接进 agent：</p>
  <ul>
    <li><strong>动态工具</strong>：MCP 工具在<strong>运行时</strong>经 <span class="mono">listTools</span> 发现，由 <span class="mono">catalog.ts</span> 的 <span class="mono">convertTool</span> 裹进 AI SDK 的 <span class="mono">dynamicTool</span>（execute 转发给 <span class="mono">client.callTool</span>），与内置工具（L36 静态 <span class="mono">Tool.make</span>）相对。</li>
    <li><strong>作用域</strong>：工具名 = <span class="mono">sanitize(服务器名) + ":" + sanitize(工具名)</span>，避免多服务器重名冲突。这个作用域名同时是<strong>权限 key</strong>——MCP 工具在 <span class="mono">session/tools.ts</span> 走<strong>和内置工具同一道权限闸门</strong>（L41 Ruleset）、同一批插件钩子。出身二等、待遇一等。</li>
    <li><strong>两种服务器</strong>（<span class="mono">config/mcp.ts</span>）：local（<span class="mono">command</span>，StdioClientTransport 拉子进程）vs remote（<span class="mono">url</span>，StreamableHTTP→SSE 回退）。连上后同得一个 MCP <span class="mono">Client</span>，上层用法一致。</li>
    <li><strong>OAuth</strong>：远程服务器需认证时标 <span class="mono">needs_auth</span>，<span class="mono">opencode mcp auth</span> 走「起本地回调服务器→开浏览器授权→截获 code→PKCE 换令牌→存 <span class="mono">mcp-auth.json</span>(0o600)」舞蹈。凭证碎片（tokens/codeVerifier/oauthState/clientInfo）由 <span class="mono">auth.ts</span> 加文件锁持久化。</li>
  </ul>
  <p>有了 MCP，agent 的「手」（工具）就能伸到 opencode 源码之外的任何服务。下一课（L47）讲 <strong>Provider 插件</strong>：与 MCP 扩展「手」相对，Provider 扩展的是 agent 的「脑」——几十家模型供应商如何注册，供 agent 的 <span class="mono">model</span> 字段挑选。L44 配置定义意图，L45 agent 是凝成的角色，L46 MCP 接上外部的手、L47 Provider 接上外部的脑——一个真正可用、可定制、可无限扩展的 agent，至此「攒」齐。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p><span class="mono">session/tools.ts</span> 把 MCP 工具并入会话工具集时，那道权限闸门用的正是工具的作用域名（简化自源码）：</p>
  <pre class="code"><span class="cm">// 遍历 MCP 动态工具，逐个并入会话工具集</span>
<span class="kw">for</span> (<span class="kw">const</span> [key, item] <span class="kw">of</span> Object.<span class="fn">entries</span>(<span class="kw">yield*</span> mcp.<span class="fn">tools</span>())) {
  <span class="kw">const</span> execute = item.execute
  <span class="kw">if</span> (!execute) <span class="kw">continue</span>
  item.execute = (args, opts) =&gt;
    run.<span class="fn">promise</span>(Effect.<span class="fn">gen</span>(<span class="kw">function*</span> () {
      <span class="cm">// ← 和内置工具同一道权限闸门，key=「服务器名:工具名」作用域名</span>
      <span class="kw">yield*</span> ctx.<span class="fn">ask</span>({ permission: key, patterns: [<span class="st">"*"</span>], always: [<span class="st">"*"</span>] })
      <span class="kw">return</span> <span class="kw">yield*</span> Effect.<span class="fn">promise</span>(() =&gt; <span class="fn">execute</span>(args, opts))
    }))
}</pre>
  <p>注意那行 <span class="mono">ctx.ask({ permission: key, ... })</span>——<span class="mono">key</span> 就是 <span class="mono">github:search</span> 这样的作用域名。这意味着 MCP 工具<strong>没有自己的一套权限逻辑</strong>，而是<strong>复用</strong>了第 41 课那套统一的权限系统：同样的 ask（allow/ask/deny 三态）、同样的 Ruleset 匹配。这正是「待遇一等公民」最硬的证据——<strong>系统没有为「外来工具」开任何后门，它必须和原生工具走完全相同的安全检查</strong>。这种「不为扩展点破例」的纪律极其重要：一旦你为某类工具开了「免检」绿色通道，整个权限系统的可信度就崩了。opencode 的做法是反过来的——<strong>越是外来的、越不可控的工具（谁知道某个第三方 MCP 服务器会让你的 agent 干什么），就越要让它老老实实排进同一道闸门。</strong></p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>MCP 让外部工具动态接入</strong>：opencode 内置工具（L36–43）编译期写死、数量固定；MCP 让你接一台<strong>外部工具服务器</strong>，运行时<strong>动态</strong>多出工具。两条主线=动态作用域工具 + OAuth。</li>
    <li><strong>动态工具</strong>：运行时 <span class="mono">listTools</span> 发现，<span class="mono">convertTool</span>（catalog.ts）裹进 AI SDK <span class="mono">dynamicTool</span>，<span class="mono">execute</span> 只是转发给 <span class="mono">client.callTool</span>——相对内置工具的静态 <span class="mono">Tool.make</span>。</li>
    <li><strong>作用域 = 权限 key</strong>：工具名 = <span class="mono">sanitize(服务器名)+":"+sanitize(工具名)</span>（如 <span class="mono">github:search</span>），既防重名，又作为 <span class="mono">session/tools.ts</span> 里的权限 key——MCP 工具走<strong>和内置工具同一道权限闸门</strong>（L41）。出身二等，待遇一等。</li>
    <li><strong>两种服务器</strong>（config/mcp.ts）：local（<span class="mono">command</span> + StdioClientTransport 拉子进程）vs remote（<span class="mono">url</span> + StreamableHTTP→SSE 回退）。连上后同得一个 MCP <span class="mono">Client</span>，上层用法一致。</li>
    <li><strong>OAuth 舞蹈</strong>：needs_auth → <span class="mono">opencode mcp auth</span> → 起 localhost 回调服务器 → 开浏览器授权（PKCE + state）→ 截获 code → 换令牌 → 存 <span class="mono">mcp-auth.json</span>（<span class="mono">0o600</span> + 文件锁）。凭证碎片：tokens/codeVerifier/oauthState/clientInfo。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">The tools in the last few lessons (L37–43) are all <strong>hardcoded in opencode's source</strong>: read, bash, grep… defined at compile time, fixed in number. But an AI agent's real power is being able to <strong>plug in your own tools on the fly</strong>—query your company's internal database, call some SaaS's API, operate your private service. This is what <strong>MCP (Model Context Protocol)</strong> solves: a standard protocol that lets you connect an <strong>external "tool server"</strong> into opencode—whatever tools the server has, the agent <strong>dynamically</strong> gains at runtime. This lesson's two threads are MCP integration's two finest faces: <strong>dynamic scoped tools</strong> (how external tools get discovered, named, merged into the same system as built-ins) and <strong>OAuth</strong> (the browser-callback authentication dance when a remote server needs login).</p>
<p>The insight to take from this lesson: <strong>MCP tools are "second-class in origin, first-class in treatment."</strong> They're not written by opencode but "asked" at runtime from an external server; yet once discovered, they're <strong>wrapped in the exact same shell as built-in tools</strong>, merged into the <strong>same tool registry</strong> (L37), routed through the <strong>same permission gate</strong> (L41), observed by the <strong>same plugin hooks</strong>. To the model, the session loop, the permission system, an MCP tool and a built-in read tool <strong>look identical</strong>—the only difference hides deep inside its <span class="mono">execute()</span>: a built-in runs local code, an MCP tool <strong>forwards the call to that remote/local server</strong>. Grasp this and you'll understand "how a good extension mechanism makes the 'foreign' and the 'native' equal citizens in the system."</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  Picture opencode's built-in tools as a computer's <strong>factory-fitted ports</strong> (USB, HDMI)—fixed in number, soldered to the board. MCP is like plugging in a <strong>USB dock</strong>: attach the dock (configure an MCP server), and however many ports it has (however many tools the server provides), the computer <strong>recognizes that many new devices on the spot</strong>—no OS reinstall, no opening the case to solder new ports. Better still, the OS treats devices on the dock <strong>exactly like</strong> devices on board-native ports—same driver path, same permission control. And OAuth is like some <strong>paid docks needing you to swipe your membership card first</strong>: you log in on the official site, authorize, get a "pass token," and only then will the dock work for you—and that token is safely locked in a drawer, no re-swipe next time.
</div>

<h2>Dynamic tools: runtime-discovered, wrapped in the same shell</h2>
<p>Built-in tools (L36) are hardcoded at compile time by <span class="mono">Tool.make(...)</span>; MCP tools are the opposite—they get "discovered" at <strong>runtime</strong>. After opencode connects to an MCP server, it sends a <span class="mono">tools/list</span> request and wraps the tool definitions the server <strong>reports on the spot</strong>, one by one, into the AI SDK's <span class="mono">dynamicTool(...)</span>:</p>
<div class="flow">
  <div class="f-node">connect MCP server<br><small>local process / remote HTTP</small></div>
  <div class="f-arrow">listTools →</div>
  <div class="f-node">server reports tool defs<br><small>name + inputSchema + description</small></div>
  <div class="f-arrow">convertTool →</div>
  <div class="f-node">wrap in dynamicTool<br><small>execute=client.callTool</small></div>
  <div class="f-arrow">merge →</div>
  <div class="f-node">the same tool registry<br><small>shoulder to shoulder with built-ins</small></div>
</div>
<p>The key is <span class="mono">convertTool</span> in <span class="mono">catalog.ts</span>: it turns an MCP server's reported tool def into a <span class="mono">dynamicTool</span>—keeping the server-given <span class="mono">inputSchema</span> as the parameter constraint, while <span class="mono">execute</span>'s implementation merely <strong>forwards the args verbatim</strong> to <span class="mono">client.callTool(name, args)</span> and converts the server's result back. "dynamic" is precisely relative to built-ins' "static": a built-in's schema and implementation both live in source, while an MCP tool's schema is asked at runtime and its implementation is just a <strong>forwarding wire to the far end</strong>. There's also a book-wide theme echoed here—"<strong>advertise cheap, fulfill expensively on demand</strong>" (L37's registry stores only definitions, L42's preview/spill, L43's skills report only names): when opencode connects, it only <strong>cheaply pulls a tool list</strong> (name + schema + description); the truly expensive tool execution waits until the model <strong>actually calls a tool by name</strong>, then forwards it via <span class="mono">callTool</span>. Even if an MCP server offers a hundred tools, discovery just runs through the list, never pre-running them all.</p>
<p>So what does "scoped" mean? Multiple MCP servers might each have a tool named <span class="mono">search</span>—how to avoid collision? opencode's way is to <strong>prefix each tool name with the server name</strong>. The name first runs through <span class="mono">sanitize</span> (replacing non-<span class="mono">[a-zA-Z0-9_-]</span> chars with <span class="mono">_</span>), then joins them with <span class="mono">:</span> (a colon):</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">sanitize</div><div class="c-txt"><span class="mono">/[^a-zA-Z0-9_-]/g → "_"</span>: wash out illegal chars in a tool name</div></div>
  <div class="cell"><div class="c-tag">naming rule</div><div class="c-txt"><span class="mono">sanitize(serverName) + ":" + sanitize(toolName)</span></div></div>
  <div class="cell"><div class="c-tag">example</div><div class="c-txt">github server's search → <span class="mono">github:search</span>; jira's search → <span class="mono">jira:search</span>, no collision</div></div>
</div>
<p>This prefixed name is the MCP tool's "scope"—it avoids name collisions and lets the model see at a glance which server a tool comes from. And this name's finest destination is in <span class="mono">session/tools.ts</span>: when MCP tools merge into the session's tool set, the permission gate writes <span class="mono">ctx.ask({ permission: key, ... })</span>—<strong>this key is exactly that server-prefixed scoped name</strong>. That is, MCP tools <strong>go through the same permission system as built-in tools</strong> (L41's Ruleset); you can perfectly well write rules in config like "<span class="mono">github:*</span> all allowed, <span class="mono">jira:delete_*</span> must ask," precisely governing each external server's, each external tool's permission. That's the landing of the opening's "first-class treatment": <strong>once a foreign tool is in the door, it shares registry, permissions, plugin hooks with native tools—no second-class treatment whatsoever.</strong></p>

<h2>Two server kinds: local process vs remote HTTP</h2>
<p>Where do MCP servers come from? The config's <span class="mono">mcp</span> cell (<span class="mono">config/mcp.ts</span>) defines two, a tagged union discriminated by <span class="mono">type</span>:</p>
<div class="cols">
  <div class="col"><h4>local · local process</h4><p><span class="mono">type:"local"</span>, given a <span class="mono">command</span> (command + args). opencode uses <strong>StdioClientTransport</strong> to <strong>spawn it as a child process</strong>, communicating via stdin/stdout (stdio). Suited to tool servers running on your machine. Can also set <span class="mono">cwd</span> (working dir), <span class="mono">environment</span> (env vars).</p></div>
  <div class="col"><h4>remote · remote HTTP</h4><p><span class="mono">type:"remote"</span>, given a <span class="mono">url</span>. opencode connects over HTTP, <strong>trying StreamableHTTP first, falling back to SSE on failure</strong>. Suited to hosted services on the public net. Can set <span class="mono">headers</span> (custom request headers) and <span class="mono">oauth</span> (auth, see next section).</p></div>
</div>
<p>This config schema is likewise plain as filling a form:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">Local</div><div class="c-txt"><span class="mono">command[]</span> (required), <span class="mono">cwd?</span>, <span class="mono">environment?</span>, <span class="mono">disabled?</span>, <span class="mono">timeout?</span></div></div>
  <div class="cell"><div class="c-tag">Remote</div><div class="c-txt"><span class="mono">url</span> (required), <span class="mono">headers?</span>, <span class="mono">oauth?</span>, <span class="mono">disabled?</span>, <span class="mono">timeout?</span></div></div>
  <div class="cell"><div class="c-tag">connect safety</div><div class="c-txt"><span class="mono">connectTransport</span> uses acquireUseRelease: on connect failure it <strong>auto-closes the transport</strong>, never leaking a process/connection</div></div>
</div>
<p>The two transports converge: whether a locally-spawned child process or a remote HTTP connection, once connected <strong>both yield the same MCP <span class="mono">Client</span></strong>, and the subsequent <span class="mono">listTools</span>, <span class="mono">callTool</span> code is <strong>completely identical</strong>—the transport-layer difference is fully absorbed by the MCP SDK's transport abstraction. Another good design: <strong>cleanly separating "how to connect" from "how to use once connected,"</strong> so the upper logic needn't care whether a tool comes from a local process or a remote service. And that "try StreamableHTTP first, fall back to SSE" detail is deliberate too: StreamableHTTP is the newer, more efficient bidirectional streaming transport, SSE (Server-Sent Events) the older, more universal fallback—opencode prefers the new, retreats only if it can't connect, getting the new protocol's benefits without shutting out servers that only speak the old one. <strong>"Prefer the better, but always keep a compatible fallback"</strong> is the most pragmatic posture for connecting to a heterogeneous external world.</p>

<h2>OAuth: the remote server's login-authorization dance</h2>
<p>Remote servers often need <strong>authentication</strong>—why should it let you call its tools? MCP uses standard <strong>OAuth</strong>. When opencode first connects to a remote server needing auth, it hits an <span class="mono">UnauthorizedError</span>, marks the server <span class="mono">needs_auth</span>, and prompts you: <span class="mono">run opencode mcp auth &lt;name&gt;</span>. After that comes a classic "browser callback" auth dance:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">you run <span class="mono">opencode mcp auth &lt;name&gt;</span></span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">opencode starts a <strong>localhost callback HTTP server</strong> on your machine (listening on the callback port)</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">opens the <strong>browser</strong> to the server's authorization page (with PKCE code_challenge + state for CSRF)</span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">you <strong>log in, authorize</strong> on that page</span></div>
  <div class="t-row"><span class="t-num">5</span><span class="t-txt">the server <strong>redirects the browser back</strong> to <span class="mono">localhost:port/callback?code=…&amp;state=…</span></span></div>
  <div class="t-row"><span class="t-num">6</span><span class="t-txt">the callback server <strong>captures the code</strong>, verifies state, exchanges code + PKCE code_verifier <strong>for tokens</strong></span></div>
  <div class="t-row"><span class="t-num">7</span><span class="t-txt">tokens <strong>saved to</strong> <span class="mono">mcp-auth.json</span>; on every later connect the transport auto-attaches the token, no re-login</span></div>
</div>
<p>This flow has several "credential fragments" that must be <strong>persisted</strong>, managed by <span class="mono">auth.ts</span> locked into <span class="mono">mcp-auth.json</span>:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">tokens</div><div class="c-txt">accessToken / refreshToken / expiresAt—the real pass token (with expiry)</div></div>
  <div class="cell"><div class="c-tag">codeVerifier</div><div class="c-txt">PKCE verifier: generated at authorize, proved back at token exchange, prevents code interception</div></div>
  <div class="cell"><div class="c-tag">oauthState</div><div class="c-txt">random state: prevents CSRF, checked at callback that it's the same initiation</div></div>
  <div class="cell"><div class="c-tag">clientInfo</div><div class="c-txt">clientId/secret from dynamic client registration (must hand-fill clientId if the server doesn't support it)</div></div>
</div>
<p>A security detail worth savoring: <span class="mono">mcp-auth.json</span> is written with <span class="mono">0o600</span> permissions (owner read/write only)—tokens are <strong>sensitive credentials</strong>, rightly locked down, never readable by other users on the same machine. And the whole file read/write is serialized with a <strong>file lock</strong> (flock), avoiding multiple opencode processes editing this auth file at once and clobbering each other's tokens. Another thoughtful design: when a server <strong>doesn't support "dynamic client registration,"</strong> opencode won't wait dumbly but marks the status <span class="mono">needs_client_registration</span> and pops a clear prompt—"please manually provide clientId in config." <strong>Translating every auth failure into a sentence a human can act on</strong>, rather than throwing an obscure OAuth error, is the craft of keeping "protocol complexity" outside the user experience. One more layer worth mentioning: tokens aren't one-and-done—<span class="mono">tokens</span> carries <span class="mono">expiresAt</span>, and <span class="mono">auth.ts</span> has a dedicated <span class="mono">isTokenExpired</span> to judge expiry—paired with <span class="mono">refreshToken</span>, opencode can <strong>silently renew</strong> as a token nears expiry, without dragging you back to the browser each time. Behind <strong>"authorize once, stay logged in long"</strong> is exactly this little tokens + expiry-check + refresh-token mechanism quietly backstopping—good auth experience makes the user feel it only the first time, near-imperceptible after.</p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>This lesson clarifies how opencode dynamically connects <strong>external tools</strong> into the agent:</p>
  <ul>
    <li><strong>Dynamic tools</strong>: MCP tools are discovered at <strong>runtime</strong> via <span class="mono">listTools</span>, wrapped by <span class="mono">catalog.ts</span>'s <span class="mono">convertTool</span> into the AI SDK's <span class="mono">dynamicTool</span> (execute forwards to <span class="mono">client.callTool</span>), as against built-in tools (L36's static <span class="mono">Tool.make</span>).</li>
    <li><strong>Scope</strong>: tool name = <span class="mono">sanitize(serverName) + ":" + sanitize(toolName)</span>, avoiding multi-server name collisions. This scoped name is also the <strong>permission key</strong>—in <span class="mono">session/tools.ts</span> MCP tools go through the <strong>same permission gate as built-ins</strong> (L41 Ruleset), the same plugin hooks. Second-class origin, first-class treatment.</li>
    <li><strong>Two server kinds</strong> (<span class="mono">config/mcp.ts</span>): local (<span class="mono">command</span>, StdioClientTransport spawns a child process) vs remote (<span class="mono">url</span>, StreamableHTTP→SSE fallback). Once connected both yield the same MCP <span class="mono">Client</span>, upper usage identical.</li>
    <li><strong>OAuth</strong>: remote servers needing auth are marked <span class="mono">needs_auth</span>, <span class="mono">opencode mcp auth</span> runs the "start local callback server→open browser authorize→capture code→PKCE exchange tokens→save <span class="mono">mcp-auth.json</span>(0o600)" dance. Credential fragments (tokens/codeVerifier/oauthState/clientInfo) persisted by <span class="mono">auth.ts</span> with a file lock.</li>
  </ul>
  <p>With MCP, the agent's "hands" (tools) can reach any service outside opencode's source. The next lesson (47) covers <strong>Provider plugins</strong>: against MCP extending the "hands," Provider extends the agent's "brain"—how dozens of model providers register for the agent's <span class="mono">model</span> field to pick. L44 config defines intent, L45 the agent is intent crystallized into a role, L46 MCP connects external hands, L47 Provider connects external brains—a truly usable, customizable, infinitely-extensible agent is hereby "assembled."</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p>When <span class="mono">session/tools.ts</span> merges MCP tools into the session's tool set, the permission gate uses exactly the tool's scoped name (simplified from source):</p>
  <pre class="code"><span class="cm">// iterate MCP dynamic tools, merge each into the session tool set</span>
<span class="kw">for</span> (<span class="kw">const</span> [key, item] <span class="kw">of</span> Object.<span class="fn">entries</span>(<span class="kw">yield*</span> mcp.<span class="fn">tools</span>())) {
  <span class="kw">const</span> execute = item.execute
  <span class="kw">if</span> (!execute) <span class="kw">continue</span>
  item.execute = (args, opts) =&gt;
    run.<span class="fn">promise</span>(Effect.<span class="fn">gen</span>(<span class="kw">function*</span> () {
      <span class="cm">// ← same permission gate as built-ins, key="serverName:toolName" scoped name</span>
      <span class="kw">yield*</span> ctx.<span class="fn">ask</span>({ permission: key, patterns: [<span class="st">"*"</span>], always: [<span class="st">"*"</span>] })
      <span class="kw">return</span> <span class="kw">yield*</span> Effect.<span class="fn">promise</span>(() =&gt; <span class="fn">execute</span>(args, opts))
    }))
}</pre>
  <p>Note that <span class="mono">ctx.ask({ permission: key, ... })</span> line—<span class="mono">key</span> is a scoped name like <span class="mono">github:search</span>. This means MCP tools have <strong>no permission logic of their own</strong> but <strong>reuse</strong> lesson 41's unified permission system: the same ask (allow/ask/deny tri-state), the same Ruleset matching. This is the hardest evidence of "first-class treatment"—<strong>the system opens no backdoor for "foreign tools"; they must pass the exact same security check as native tools</strong>. This "no exception for extension points" discipline is crucial: the moment you open a "no-inspection" green channel for some class of tool, the whole permission system's credibility collapses. opencode does the reverse—<strong>the more foreign, the less controllable a tool (who knows what some third-party MCP server will have your agent do), the more it must queue obediently into the same gate.</strong></p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>MCP connects external tools dynamically</strong>: opencode's built-in tools (L36–43) are hardcoded at compile time, fixed in number; MCP lets you connect an <strong>external tool server</strong> that <strong>dynamically</strong> adds tools at runtime. Two threads = dynamic scoped tools + OAuth.</li>
    <li><strong>Dynamic tools</strong>: discovered at runtime via <span class="mono">listTools</span>, wrapped by <span class="mono">convertTool</span> (catalog.ts) into the AI SDK's <span class="mono">dynamicTool</span>, <span class="mono">execute</span> just forwards to <span class="mono">client.callTool</span>—against built-ins' static <span class="mono">Tool.make</span>.</li>
    <li><strong>Scope = permission key</strong>: tool name = <span class="mono">sanitize(serverName)+":"+sanitize(toolName)</span> (e.g. <span class="mono">github:search</span>), avoiding collisions and serving as the permission key in <span class="mono">session/tools.ts</span>—MCP tools go through the <strong>same permission gate as built-ins</strong> (L41). Second-class origin, first-class treatment.</li>
    <li><strong>Two server kinds</strong> (config/mcp.ts): local (<span class="mono">command</span> + StdioClientTransport spawns a child process) vs remote (<span class="mono">url</span> + StreamableHTTP→SSE fallback). Once connected both yield the same MCP <span class="mono">Client</span>, upper usage identical.</li>
    <li><strong>OAuth dance</strong>: needs_auth → <span class="mono">opencode mcp auth</span> → start localhost callback server → open browser authorize (PKCE + state) → capture code → exchange tokens → save <span class="mono">mcp-auth.json</span> (<span class="mono">0o600</span> + file lock). Credential fragments: tokens/codeVerifier/oauthState/clientInfo.</li>
  </ul>
</div>
""",
}
LESSON_47 = {
    "zh": r"""
<p class="lead">上一课的 MCP，给 agent 接上了外部的「手」（工具）。这一课讲 <strong>Provider 插件</strong>——给 agent 接上外部的「脑」（模型）。opencode 支持<strong>三十多家</strong>模型供应商：Anthropic、OpenAI、Google、Amazon Bedrock、Groq、xAI、Mistral、Cohere、OpenRouter、Azure、Vertex……你在配置里把 <span class="mono">model</span> 写成哪家的，agent 就用哪家的脑子思考。问题来了：要支持这么多供应商，opencode 是不是写了一个三十多个分支的巨型 <span class="mono">switch</span>？<strong>恰恰相反</strong>。opencode 用的是一套优雅的<strong>插件架构</strong>：每一家供应商，都是一个<strong>独立的、自包含的插件文件</strong>（<span class="mono">core/src/plugin/provider/anthropic.ts</span>、<span class="mono">openai.ts</span>……），它们被收进一个数组 <span class="mono">ProviderPlugins</span>。<strong>新增一家供应商，等于加一个插件文件 + 在数组里加一行——核心代码一行都不用动。</strong></p>
<p>这一课最值得带走的洞见，是 opencode 解决「一对多」的办法：<strong>不是核心去逐个认领供应商，而是把「谁能处理这个包」广播出去，让插件自己举手认领。</strong>当 agent 要用某个模型时，opencode 不去 <span class="mono">if (provider === "anthropic") ... else if ...</span>，而是<strong>广播一个事件</strong>：「有谁能处理 <span class="mono">@ai-sdk/anthropic</span> 这个包？」三十多个插件都收到这条广播，但只有 Anthropic 插件认出「这是我的包」，于是站出来把 SDK 造好。这种「广播 + 自我认领」的设计，把核心和具体供应商<strong>彻底解耦</strong>了——核心永远不知道、也不必知道总共有哪些供应商，它只管喊一嗓子，剩下的交给插件自己响应。读懂这套机制，你就懂了「一个真正可扩展的系统，是如何做到『加新功能不改老代码』的」。</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  把 opencode 对接模型供应商，想象成一间<strong>大公司的前台转接电话</strong>。笨办法是前台背一本厚厚的通讯录：「财务找张三、法务找李四……」——每多一个部门，就得改一次通讯录（巨型 switch）。opencode 的办法聪明得多：前台<strong>对着整层楼喊一嗓子</strong>「有个找 <span class="mono">@ai-sdk/anthropic</span> 的电话，谁接？」——三十多个工位都听见了，但只有 Anthropic 那个工位的人<strong>举手「我接！」</strong>。前台根本不需要知道楼里坐了哪些部门、各在哪个工位，<strong>它只管广播，认领交给各部门自己</strong>。来了个新部门？新部门自己搬张桌子坐进来（加个插件文件）、记得「听到喊我就举手」即可——前台的工作流一个字都不用改。而那个永远<strong>坐在最后一个工位的「兜底接线员」</strong>（DynamicProviderPlugin）：凡是没人举手的电话，他统统接下来，临时去把对应的人请来（npm 装包）。
</div>

<h2>一个 Provider 插件长什么样</h2>
<p>先看最小的样本——<span class="mono">alibaba.ts</span>，整个文件不到 20 行，却是所有 provider 插件的标准模板：</p>
<pre class="code"><span class="kw">export const</span> AlibabaPlugin = PluginV2.<span class="fn">define</span>({
  id: PluginV2.ID.<span class="fn">make</span>(<span class="st">"alibaba"</span>),
  effect: Effect.<span class="fn">gen</span>(<span class="kw">function*</span> () {
    <span class="kw">return</span> {
      <span class="st">"aisdk.sdk"</span>: Effect.<span class="fn">fn</span>(<span class="kw">function*</span> (evt) {
        <span class="kw">if</span> (evt.package !== <span class="st">"@ai-sdk/alibaba"</span>) <span class="kw">return</span>   <span class="cm">// ← 不是我的包，闭嘴</span>
        <span class="kw">const</span> mod = <span class="kw">yield*</span> Effect.<span class="fn">promise</span>(() =&gt; <span class="fn">import</span>(<span class="st">"@ai-sdk/alibaba"</span>))
        evt.sdk = mod.<span class="fn">createAlibaba</span>(evt.options)         <span class="cm">// ← 是我的包，造 SDK</span>
      }),
    }
  }),
})</pre>
<p>一个 provider 插件，就是 <span class="mono">PluginV2.define({ id, effect })</span>：<span class="mono">id</span> 是插件名，<span class="mono">effect</span> 是一段返回<strong>钩子函数表</strong>的 Effect。最核心的钩子叫 <span class="mono">"aisdk.sdk"</span>，它的逻辑朴素到只有两步：<strong>第一步「自我认领」</strong>——<span class="mono">if (evt.package !== "@ai-sdk/alibaba") return</span>，不是我负责的包就直接返回、什么都不做；<strong>第二步「造 SDK」</strong>——确认是自己的包后，<strong>动态 import</strong> 对应的 AI SDK 模块，调它的 <span class="mono">createAlibaba(options)</span> 工厂，把造好的 SDK 塞进 <span class="mono">evt.sdk</span>。</p>
<p>这里有个容易被忽略却很关键的细节：那句 <span class="mono">import("@ai-sdk/alibaba")</span> 是<strong>动态导入</strong>。意味着只有当你<strong>真的用到</strong>阿里的模型时，阿里的 SDK 包才会被加载进内存——你没用到的三十多家 SDK，一行代码都不会跑、一点内存都不占。三十多个 provider 插件虽然全都「在场待命」，但每个都<strong>极其廉价</strong>（不到 20 行 + 一个延迟加载的 import），真正昂贵的 SDK 加载严格按需发生。</p>
<p>这又是那个全书主题——<strong>「便宜地在场，昂贵地按需」</strong>——在 provider 层的又一次回响。那么这三十多家「在场待命」的供应商都有谁？<span class="mono">ProviderPlugins</span> 数组里大致可分几类：</p>
<table class="t">
  <tr><th>类别</th><th>代表供应商（插件文件）</th></tr>
  <tr><td>一线大厂</td><td>Anthropic、OpenAI、Google、xAI、Mistral、Cohere</td></tr>
  <tr><td>云平台</td><td>Amazon Bedrock、Azure、Google Vertex、Snowflake Cortex、SAP AI Core</td></tr>
  <tr><td>推理加速 / 聚合</td><td>Groq、Cerebras、DeepInfra、Together、Perplexity、Nvidia</td></tr>
  <tr><td>网关 / 路由</td><td>OpenRouter、Vercel Gateway、Cloudflare AI Gateway、LLMGateway、opencode</td></tr>
  <tr><td>OpenAI 兼容 / 兜底</td><td>openai-compatible（通用兼容端点）、<strong>DynamicProviderPlugin</strong>（万能兜底）</td></tr>
</table>
<p>这张表本身就说明了插件架构的价值：从一线大厂到小众网关，从需要 AWS 签名的 Bedrock 到只认 OpenAI 协议的兼容端点，<strong>形态如此各异的三十多家，却被同一套 <span class="mono">PluginV2.define</span> 模板收得整整齐齐</strong>。每家的特殊性都被封进自己那个文件，对外却呈现完全一致的形状。换个角度看，这张表也是一份「<strong>能力地图</strong>」：当你纠结「opencode 到底支不支持某家模型」时，答案几乎总是「支持」——要么它已在这三十多个内置插件里有专属一格，要么它能被最后那个万能兜底动态接入。<strong>这种「明确支持的列表很长、列表之外还有兜底」的双保险，正是一个成熟工具对接外部生态时该有的从容。</strong></p>

<h2>广播与自我认领：核心与供应商的解耦</h2>
<p>这些插件是怎么被「喊」到的？看 <span class="mono">aisdk.ts</span>：当 agent 需要某个模型时，<span class="mono">AISDK.language(model)</span> 会<strong>触发（trigger）一个 <span class="mono">"aisdk.sdk"</span> 事件</strong>，把 <span class="mono">{ model, package, options }</span> 广播给<strong>所有</strong>插件：</p>
<div class="flow">
  <div class="f-node">agent 要用某模型<br><small>AISDK.language(model)</small></div>
  <div class="f-arrow">广播 →</div>
  <div class="f-node">trigger "aisdk.sdk"<br><small>{ model, package, options }</small></div>
  <div class="f-arrow">三十多插件都收到 →</div>
  <div class="f-node">各自判断 evt.package<br><small>只有对的那个举手</small></div>
  <div class="f-arrow">认领者 →</div>
  <div class="f-node">createXxx(options)<br><small>evt.sdk = 造好的 SDK</small></div>
</div>
<p>关键就在「广播给所有插件、各自判断」这一步：核心的 <span class="mono">aisdk.ts</span> 从头到尾<strong>没有一个 if-else 在区分供应商</strong>，它只是把事件抛出去；是 Anthropic 插件自己用 <span class="mono">if (evt.package !== "@ai-sdk/anthropic") return</span> 认领了自己那一份。如果广播完一圈下来 <span class="mono">evt.sdk</span> 还是空的（没人举手），核心就报一个清楚的错：<span class="mono">No AISDK provider plugin returned an SDK</span>。整个 provider 体系其实围绕<strong>三个钩子</strong>展开：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">aisdk.sdk</div><div class="c-txt">按 package 认领，造出该供应商的 SDK 实例（最核心、人人都有）</div></div>
  <div class="cell"><div class="c-tag">aisdk.language</div><div class="c-txt">从 SDK 造出具体的语言模型，可定制路由（如 Copilot 选 Responses vs Chat）</div></div>
  <div class="cell"><div class="c-tag">catalog.transform</div><div class="c-txt">改写模型目录，如 Anthropic 加 beta 请求头、Copilot 隐藏冲突的模型别名</div></div>
</div>
<p>把一次完整的「从 model 配置到可用语言模型」的解析走一遍，就是这样一条链：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">agent 需要 model（如 <span class="mono">anthropic/claude-...</span>）→ <span class="mono">AISDK.language(model)</span></span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">查 <span class="mono">sdks</span> 缓存；命中则直接复用，免重复构造</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">未命中 → trigger <span class="mono">"aisdk.sdk"</span> 广播 <span class="mono">{package:"@ai-sdk/anthropic"}</span></span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">Anthropic 插件认领 → <span class="mono">import("@ai-sdk/anthropic")</span> → <span class="mono">createAnthropic(options)</span> → 设 <span class="mono">evt.sdk</span></span></div>
  <div class="t-row"><span class="t-num">5</span><span class="t-txt">trigger <span class="mono">"aisdk.language"</span> → 插件定制（或默认 <span class="mono">sdk.languageModel(id)</span>）</span></div>
  <div class="t-row"><span class="t-num">6</span><span class="t-txt">得到可用的 LanguageModel，缓存并返回 → 交给 M6 协议层去 stream</span></div>
</div>
<p>而数组 <span class="mono">ProviderPlugins</span> 的<strong>最后一个</strong>位置，永远留给那个「兜底接线员」<span class="mono">DynamicProviderPlugin</span>。它的 <span class="mono">aisdk.sdk</span> 钩子第一行是 <span class="mono">if (evt.sdk) return</span>——<strong>只要前面任何一个内置插件已经认领了，它就不插手</strong>；只有当三十多个内置插件全都没举手时，它才出场：把那个未知的包<strong>用 npm 临时装下来</strong>，import 进来，找一个 <span class="mono">create</span> 开头的导出当工厂。这一笔极其漂亮——<strong>内置三十多家是「快路径」，而 DynamicProviderPlugin 兜住了「剩下的所有家」</strong>：哪怕某家供应商 opencode 从没听说过，只要它发布了一个符合 AI SDK 约定的 npm 包，就能被这个兜底插件动态接进来。<strong>三十多家明确支持 + 一个万能兜底 = 理论上支持任意供应商。</strong></p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">内置插件（快路径）</div><div class="c-txt">认死一个包名 <span class="mono">if (evt.package !== "@ai-sdk/xxx") return</span>；命中即 createXxx，无需联网装包</div></div>
  <div class="cell"><div class="c-tag">DynamicProviderPlugin（兜底）</div><div class="c-txt">数组末位，<span class="mono">if (evt.sdk) return</span> 仅在无人认领时出场：<span class="mono">npm.add(package)</span> → import → 找 <span class="mono">create*</span> 导出</div></div>
</div>

<h2>不止造 SDK：插件还能微调行为</h2>
<p>最小的插件只实现 <span class="mono">aisdk.sdk</span>，但「重」一点的供应商会用上另两个钩子，做精细的定制。两个真实例子最能说明问题：</p>
<div class="cols">
  <div class="col"><h4>Anthropic · 加 beta 头</h4><p>它额外实现 <span class="mono">catalog.transform</span>，给所有 Anthropic 模型的请求头塞进 <span class="mono">anthropic-beta: interleaved-thinking…,fine-grained-tool-streaming…</span>——开启交错思考、细粒度工具流式等 beta 能力。这正是第 30 课 Anthropic 协议特性在 provider 层的「开关」。</p></div>
  <div class="col"><h4>Copilot · 选路由</h4><p>它实现 <span class="mono">aisdk.language</span>，对 GPT-5 类模型走 Responses API、对 mini 变体仍走 Chat Completions——一个 <span class="mono">shouldUseResponses(modelID)</span> 当场裁决。这正是第 31、35 课「Responses vs Chat 双端点」在 provider 层的落地。</p></div>
</div>
<p>这两个例子揭示了 provider 插件真正的威力：它不只是「把 SDK 造出来」的工厂，更是每家供应商<strong>容纳自己怪癖的容器</strong>。Anthropic 要 beta 头、Copilot 要分模型选端点、Azure 要换鉴权、Bedrock 要 AWS 签名……这些<strong>千奇百怪的特殊处理，全都被关进各自的插件文件里，绝不外溢到核心</strong>。核心的 <span class="mono">aisdk.ts</span> 始终干干净净，只管「广播事件、收集结果、缓存 SDK」这套通用流程。最后值得一提的是：provider 插件并非孤例，它只是 opencode <strong>整套插件系统</strong>的一类成员——看 <span class="mono">boot.ts</span> 的启动序列，agent（L45）、command、skill（L43）、config（L44）<strong>全都是以插件形式注册的</strong>。<strong>「插件」是贯穿 opencode 的统一扩展范式</strong>：无论你想加一家模型供应商、一个 agent、一个命令还是一项技能，套路都一样——写一个自包含的插件，挂上钩子，注册进去。读懂了 provider 插件，你就读懂了 opencode 整个可扩展架构的骨架。换句话说，这一课表面在讲「怎么对接三十多家模型」，骨子里讲的是 opencode <strong>面对一切「一对多」扩展时的统一答卷</strong>——把变化点（每家供应商、每个 agent、每条命令）做成可插拔的插件，让恒定的核心只负责「广播事件、收集结果」这套通用编排。变与不变就此清爽地分了家。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观视角</div>
  <p>这一课讲清了 opencode 如何用插件架构支持三十多家模型供应商：</p>
  <ul>
    <li><strong>每家供应商 = 一个自包含插件</strong>（<span class="mono">core/src/plugin/provider/*.ts</span>），<span class="mono">PluginV2.define({ id, effect→钩子表 })</span>。最小的 <span class="mono">alibaba.ts</span> 不到 20 行。三十多个插件收进 <span class="mono">ProviderPlugins</span> 数组。<strong>新增供应商 = 加文件 + 加一行，不动核心。</strong></li>
    <li><strong>广播 + 自我认领</strong>：<span class="mono">aisdk.ts</span> 的 <span class="mono">AISDK.language</span> 触发 <span class="mono">"aisdk.sdk"</span> 事件广播给所有插件；每个插件用 <span class="mono">if (evt.package !== "@ai-sdk/xxx") return</span> 自我认领，只有匹配的那个 <span class="mono">createXxx(options)</span> 设 <span class="mono">evt.sdk</span>。核心零 if-else 区分供应商。</li>
    <li><strong>三个钩子</strong>：<span class="mono">aisdk.sdk</span>（造 SDK，人人都有）、<span class="mono">aisdk.language</span>（造语言模型、可定制路由，如 Copilot Responses/Chat）、<span class="mono">catalog.transform</span>（改目录，如 Anthropic beta 头）。<span class="mono">import("@ai-sdk/xxx")</span> 动态导入=按需加载。</li>
    <li><strong>DynamicProviderPlugin 兜底</strong>：数组最后一位，<span class="mono">if (evt.sdk) return</span> 只在没人认领时出场，npm 临时装包、找 <span class="mono">create*</span> 导出。三十多家快路径 + 一个万能兜底 = 支持任意供应商。</li>
  </ul>
  <p>至此 M8（配置/Agents/Provider）讲完：L44 配置定义意图、L45 agent 凝成角色、L46 MCP 接上外部的手、L47 Provider 接上外部的脑。一个可配置、可定制、可无限扩展的 agent 全貌成形。而 provider 插件揭示的「插件是贯穿全系统的统一扩展范式」（<span class="mono">boot.ts</span> 里 agent/command/skill/config 皆插件），也为后续埋下伏笔。下一部分 M9 转向<strong>持久化与存储</strong>：agent 跑出来的会话、消息、上下文，如何用 Drizzle + SQLite 落到磁盘、又如何在版本间迁移。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p><span class="mono">aisdk.ts</span> 里「广播事件、收集 SDK」的核心流程（简化自源码）：</p>
  <pre class="code"><span class="cm">// 没有任何 if (provider==="anthropic") 之类的分支！</span>
<span class="kw">const</span> sdk = sdks.<span class="fn">get</span>(sdkKey) ??
  (<span class="kw">yield*</span> plugin
    .<span class="fn">trigger</span>(<span class="st">"aisdk.sdk"</span>, { model, package: model.api.package, options }, {})
  ).sdk
<span class="kw">if</span> (!sdk)                                  <span class="cm">// 广播一圈没人认领</span>
  <span class="kw">return yield*</span> <span class="kw">new</span> <span class="fn">InitError</span>({
    providerID: model.providerID,
    cause: <span class="kw">new</span> <span class="fn">Error</span>(<span class="st">"No AISDK provider plugin returned an SDK"</span>),
  })
sdks.<span class="fn">set</span>(sdkKey, sdk)               <span class="cm">// 缓存：同样的包+选项不重复造</span>
<span class="cm">// 再触发 aisdk.language，让插件定制语言模型（如 Copilot 选端点）</span>
<span class="kw">const</span> result = <span class="kw">yield*</span> plugin.<span class="fn">trigger</span>(<span class="st">"aisdk.language"</span>, { model, sdk, options }, {})
<span class="kw">const</span> language = result.language ?? sdk.<span class="fn">languageModel</span>(model.api.id)</pre>
  <p>这段代码最值得品的，是它的「<strong>空</strong>」——通篇<strong>没有一个供应商的名字</strong>。核心只做三件通用的事：广播 <span class="mono">aisdk.sdk</span> 收 SDK、广播 <span class="mono">aisdk.language</span> 收语言模型、用 <span class="mono">sdkKey</span> 缓存避免重复构造。具体「Anthropic 怎么造、Copilot 怎么路由」的知识，<strong>全都不在这里</strong>，而在各自的插件里。这就是<strong>控制反转（IoC）</strong>的精髓：传统写法是核心主动调用每个供应商（核心依赖供应商），而这里是<strong>核心定义「广播-认领」的协议、供应商反过来挂进核心</strong>（供应商依赖核心）。依赖方向一反，「加供应商」就从「改核心的 switch」变成了「写个新插件挂上去」——<strong>核心对扩展开放、对修改封闭</strong>，这正是开闭原则活生生的样子。还有那行 <span class="mono">result.language ?? sdk.languageModel(...)</span>：插件没定制就走 SDK 默认，定制了就用插件的——<strong>用「可选覆盖」给每个钩子都留了「不管就走合理默认」的温柔出口。</strong></p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>三十多家供应商 = 三十多个自包含插件</strong>（<span class="mono">plugin/provider/*.ts</span>），<span class="mono">PluginV2.define({ id, effect→钩子表 })</span>，收进 <span class="mono">ProviderPlugins</span> 数组。<strong>新增供应商 = 加文件 + 加一行，核心零改动</strong>（开闭原则）。</li>
    <li><strong>广播 + 自我认领</strong>：<span class="mono">aisdk.ts</span> 触发 <span class="mono">"aisdk.sdk"</span> 广播给所有插件，每个用 <span class="mono">if (evt.package !== "@ai-sdk/xxx") return</span> 认领，只匹配者 <span class="mono">createXxx</span> 设 <span class="mono">evt.sdk</span>。核心零 if-else 区分供应商=控制反转。</li>
    <li><strong>三个钩子</strong>：<span class="mono">aisdk.sdk</span>（造 SDK）、<span class="mono">aisdk.language</span>（造语言模型、定制路由，如 Copilot Responses/Chat，呼应 L31/35）、<span class="mono">catalog.transform</span>（改目录，如 Anthropic beta 头，呼应 L30）。各家怪癖关进各自插件，核心始终干净。</li>
    <li><strong>动态导入按需加载</strong>：<span class="mono">import("@ai-sdk/xxx")</span> 让没用到的 SDK 一行不跑、一字节不占——「便宜地在场，昂贵地按需」在 provider 层的回响。</li>
    <li><strong>DynamicProviderPlugin 兜底</strong>：数组最后一位，<span class="mono">if (evt.sdk) return</span>，只在内置全没认领时 npm 装包、找 <span class="mono">create*</span> 工厂。三十多快路径 + 一个万能兜底 = 任意供应商。provider 只是 opencode <strong>统一插件范式</strong>的一类（boot.ts 里 agent/command/skill/config 皆插件）。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Last lesson's MCP connected external "hands" (tools) to the agent. This lesson covers <strong>Provider plugins</strong>—connecting external "brains" (models) to the agent. opencode supports <strong>thirty-some</strong> model providers: Anthropic, OpenAI, Google, Amazon Bedrock, Groq, xAI, Mistral, Cohere, OpenRouter, Azure, Vertex… whichever one you write into the config's <span class="mono">model</span>, that's the brain the agent thinks with. The question: to support so many providers, did opencode write one giant <span class="mono">switch</span> with thirty-some branches? <strong>Quite the opposite.</strong> opencode uses an elegant <strong>plugin architecture</strong>: each provider is an <strong>independent, self-contained plugin file</strong> (<span class="mono">core/src/plugin/provider/anthropic.ts</span>, <span class="mono">openai.ts</span>…), gathered into one array <span class="mono">ProviderPlugins</span>. <strong>Adding a provider equals adding a plugin file + one line in the array—not a single line of core code changes.</strong></p>
<p>The insight to take from this lesson is opencode's way of solving "one-to-many": <strong>instead of the core claiming providers one by one, it broadcasts "who can handle this package" and lets plugins raise their own hand.</strong> When the agent needs a model, opencode doesn't <span class="mono">if (provider === "anthropic") ... else if ...</span>; it <strong>broadcasts an event</strong>: "who can handle the <span class="mono">@ai-sdk/anthropic</span> package?" All thirty-some plugins receive this broadcast, but only the Anthropic plugin recognizes "this is mine" and steps up to build the SDK. This "broadcast + self-claim" design <strong>fully decouples</strong> the core from concrete providers—the core never knows, never needs to know, how many providers exist in total; it just shouts, and the rest is left to plugins to respond. Grasp this and you'll understand "how a truly extensible system achieves 'add new features without touching old code.'"</p>

<div class="card analogy">
  <div class="tag">🧩 Analogy</div>
  Picture opencode connecting to model providers as a <strong>big company's front desk routing calls</strong>. The dumb way: the receptionist memorizes a thick directory—"finance is Zhang, legal is Li…"—and every new department means editing the directory (a giant switch). opencode's way is far smarter: the receptionist <strong>shouts across the whole floor</strong> "there's a call for <span class="mono">@ai-sdk/anthropic</span>, who takes it?"—all thirty-some desks hear it, but only the person at the Anthropic desk <strong>raises a hand: "I've got it!"</strong> The receptionist needn't know which departments sit on the floor or at which desks; <strong>it just broadcasts, claiming is left to each department</strong>. A new department arrives? It moves in its own desk (adds a plugin file), remembers to "raise a hand when called"—the receptionist's workflow doesn't change one word. And that <strong>"catch-all operator" forever at the last desk</strong> (DynamicProviderPlugin): every call no one claims, it takes them all, temporarily fetching the right person (npm-installs the package).
</div>

<h2>What a Provider plugin looks like</h2>
<p>First the smallest sample—<span class="mono">alibaba.ts</span>, the whole file under 20 lines, yet the standard template for all provider plugins:</p>
<pre class="code"><span class="kw">export const</span> AlibabaPlugin = PluginV2.<span class="fn">define</span>({
  id: PluginV2.ID.<span class="fn">make</span>(<span class="st">"alibaba"</span>),
  effect: Effect.<span class="fn">gen</span>(<span class="kw">function*</span> () {
    <span class="kw">return</span> {
      <span class="st">"aisdk.sdk"</span>: Effect.<span class="fn">fn</span>(<span class="kw">function*</span> (evt) {
        <span class="kw">if</span> (evt.package !== <span class="st">"@ai-sdk/alibaba"</span>) <span class="kw">return</span>   <span class="cm">// ← not my package, stay quiet</span>
        <span class="kw">const</span> mod = <span class="kw">yield*</span> Effect.<span class="fn">promise</span>(() =&gt; <span class="fn">import</span>(<span class="st">"@ai-sdk/alibaba"</span>))
        evt.sdk = mod.<span class="fn">createAlibaba</span>(evt.options)         <span class="cm">// ← my package, build the SDK</span>
      }),
    }
  }),
})</pre>
<p>A provider plugin is just <span class="mono">PluginV2.define({ id, effect })</span>: <span class="mono">id</span> is the plugin name, <span class="mono">effect</span> is an Effect returning a <strong>table of hook functions</strong>. The core hook is <span class="mono">"aisdk.sdk"</span>, whose logic is plain as two steps: <strong>step one "self-claim"</strong>—<span class="mono">if (evt.package !== "@ai-sdk/alibaba") return</span>, not my package so return immediately, do nothing; <strong>step two "build the SDK"</strong>—once confirmed it's my package, <strong>dynamically import</strong> the corresponding AI SDK module, call its <span class="mono">createAlibaba(options)</span> factory, stuff the built SDK into <span class="mono">evt.sdk</span>.</p>
<p>There's an easily-overlooked yet crucial detail: that <span class="mono">import("@ai-sdk/alibaba")</span> is a <strong>dynamic import</strong>. It means only when you <strong>actually use</strong> Alibaba's model does Alibaba's SDK package get loaded into memory—the thirty-some SDKs you don't use won't run a line of code or occupy a byte of memory. Though all thirty-some provider plugins are "present on standby," each is <strong>extremely cheap</strong> (under 20 lines + a lazy-loaded import), and the truly expensive SDK loading happens strictly on demand.</p>
<p>This is another echo of the book-wide theme—<strong>"present cheaply, fulfilled expensively on demand"</strong>—at the provider layer. So who are these thirty-some "on standby" providers? The <span class="mono">ProviderPlugins</span> array roughly splits into a few categories:</p>
<table class="t">
  <tr><th>Category</th><th>Representative providers (plugin files)</th></tr>
  <tr><td>First-tier majors</td><td>Anthropic, OpenAI, Google, xAI, Mistral, Cohere</td></tr>
  <tr><td>Cloud platforms</td><td>Amazon Bedrock, Azure, Google Vertex, Snowflake Cortex, SAP AI Core</td></tr>
  <tr><td>Inference accel / aggregators</td><td>Groq, Cerebras, DeepInfra, Together, Perplexity, Nvidia</td></tr>
  <tr><td>Gateways / routers</td><td>OpenRouter, Vercel Gateway, Cloudflare AI Gateway, LLMGateway, opencode</td></tr>
  <tr><td>OpenAI-compatible / catch-all</td><td>openai-compatible (generic compatible endpoint), <strong>DynamicProviderPlugin</strong> (universal catch-all)</td></tr>
</table>
<p>This table itself shows the plugin architecture's value: from first-tier majors to niche gateways, from Bedrock needing AWS signing to compatible endpoints speaking only the OpenAI protocol, <strong>thirty-some so wildly varied providers are gathered neatly by the same <span class="mono">PluginV2.define</span> template</strong>. Each one's peculiarity is sealed into its own file, yet presents an entirely uniform shape outward. From another angle, this table is also a "<strong>capability map</strong>": when you wonder "does opencode support some model," the answer is almost always "yes"—either it already has a dedicated cell among these thirty-some built-in plugins, or it can be dynamically connected by that last universal catch-all. <strong>This "long explicit-support list, with a catch-all beyond the list" double insurance is exactly the composure a mature tool should have when connecting to an external ecosystem.</strong></p>

<h2>Broadcast and self-claim: decoupling core from providers</h2>
<p>How do these plugins get "called"? See <span class="mono">aisdk.ts</span>: when the agent needs a model, <span class="mono">AISDK.language(model)</span> <strong>triggers an <span class="mono">"aisdk.sdk"</span> event</strong>, broadcasting <span class="mono">{ model, package, options }</span> to <strong>all</strong> plugins:</p>
<div class="flow">
  <div class="f-node">agent needs a model<br><small>AISDK.language(model)</small></div>
  <div class="f-arrow">broadcast →</div>
  <div class="f-node">trigger "aisdk.sdk"<br><small>{ model, package, options }</small></div>
  <div class="f-arrow">all 30+ plugins receive →</div>
  <div class="f-node">each checks evt.package<br><small>only the right one raises a hand</small></div>
  <div class="f-arrow">claimer →</div>
  <div class="f-node">createXxx(options)<br><small>evt.sdk = built SDK</small></div>
</div>
<p>The key is that "broadcast to all plugins, each judges for itself" step: the core <span class="mono">aisdk.ts</span> has <strong>not one if-else distinguishing providers</strong> from start to finish, it merely throws the event out; it's the Anthropic plugin that claims its share with <span class="mono">if (evt.package !== "@ai-sdk/anthropic") return</span>. If after a full broadcast round <span class="mono">evt.sdk</span> is still empty (no one raised a hand), the core reports a clear error: <span class="mono">No AISDK provider plugin returned an SDK</span>. The whole provider system actually revolves around <strong>three hooks</strong>:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">aisdk.sdk</div><div class="c-txt">claim by package, build that provider's SDK instance (most core, everyone has it)</div></div>
  <div class="cell"><div class="c-tag">aisdk.language</div><div class="c-txt">build the concrete language model from the SDK, customizable routing (e.g. Copilot picks Responses vs Chat)</div></div>
  <div class="cell"><div class="c-tag">catalog.transform</div><div class="c-txt">rewrite the model catalog, e.g. Anthropic adds beta headers, Copilot hides a conflicting model alias</div></div>
</div>
<p>Walking through one complete "from model config to usable language model" resolution gives this chain:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">agent needs a model (e.g. <span class="mono">anthropic/claude-...</span>) → <span class="mono">AISDK.language(model)</span></span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">check the <span class="mono">sdks</span> cache; hit → reuse directly, no rebuild</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">miss → trigger <span class="mono">"aisdk.sdk"</span> broadcasting <span class="mono">{package:"@ai-sdk/anthropic"}</span></span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">Anthropic plugin claims → <span class="mono">import("@ai-sdk/anthropic")</span> → <span class="mono">createAnthropic(options)</span> → set <span class="mono">evt.sdk</span></span></div>
  <div class="t-row"><span class="t-num">5</span><span class="t-txt">trigger <span class="mono">"aisdk.language"</span> → plugin customizes (or default <span class="mono">sdk.languageModel(id)</span>)</span></div>
  <div class="t-row"><span class="t-num">6</span><span class="t-txt">get a usable LanguageModel, cache and return → hand to M6's protocol layer to stream</span></div>
</div>
<p>And the <strong>last</strong> position in the <span class="mono">ProviderPlugins</span> array is forever reserved for that "catch-all operator" <span class="mono">DynamicProviderPlugin</span>. Its <span class="mono">aisdk.sdk</span> hook's first line is <span class="mono">if (evt.sdk) return</span>—<strong>so long as any built-in plugin before it already claimed, it stays out</strong>; only when all thirty-some built-in plugins failed to raise a hand does it step up: <strong>temporarily npm-installs</strong> that unknown package, imports it, finds an export starting with <span class="mono">create</span> as the factory. This stroke is exquisite—<strong>the thirty-some built-ins are the "fast path," while DynamicProviderPlugin catches "all the rest"</strong>: even if opencode has never heard of some provider, as long as it published an npm package conforming to AI SDK conventions, this catch-all plugin can dynamically connect it. <strong>Thirty-some explicitly supported + one universal catch-all = supporting any provider in theory.</strong></p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">Built-in plugin (fast path)</div><div class="c-txt">claims one fixed package name <span class="mono">if (evt.package !== "@ai-sdk/xxx") return</span>; on match createXxx, no network install</div></div>
  <div class="cell"><div class="c-tag">DynamicProviderPlugin (catch-all)</div><div class="c-txt">last in the array, <span class="mono">if (evt.sdk) return</span>, steps up only when unclaimed: <span class="mono">npm.add(package)</span> → import → find <span class="mono">create*</span> export</div></div>
</div>

<h2>More than building SDKs: plugins can fine-tune behavior</h2>
<p>The smallest plugins implement only <span class="mono">aisdk.sdk</span>, but "heavier" providers use the other two hooks for fine customization. Two real examples illustrate it best:</p>
<div class="cols">
  <div class="col"><h4>Anthropic · adds beta headers</h4><p>It additionally implements <span class="mono">catalog.transform</span>, stuffing <span class="mono">anthropic-beta: interleaved-thinking…,fine-grained-tool-streaming…</span> into all Anthropic models' request headers—enabling interleaved thinking, fine-grained tool streaming, and other beta capabilities. This is exactly lesson 30's Anthropic protocol features as a "switch" at the provider layer.</p></div>
  <div class="col"><h4>Copilot · picks routing</h4><p>It implements <span class="mono">aisdk.language</span>, routing GPT-5-class models to the Responses API, mini variants still to Chat Completions—a <span class="mono">shouldUseResponses(modelID)</span> adjudicates on the spot. This is exactly lessons 31 and 35's "Responses vs Chat dual-endpoint" landing at the provider layer.</p></div>
</div>
<p>These two examples reveal the provider plugin's real power: it's not just a factory that "builds the SDK," but a <strong>container holding each provider's quirks</strong>. Anthropic wants beta headers, Copilot wants per-model endpoint selection, Azure wants different auth, Bedrock wants AWS signing… these <strong>wildly varied special handlings are all locked into their own plugin files, never spilling into the core</strong>. The core <span class="mono">aisdk.ts</span> stays spotless, handling only the generic flow of "broadcast event, collect result, cache SDK." Finally worth mentioning: provider plugins aren't a lone case but just one member of opencode's <strong>whole plugin system</strong>—look at <span class="mono">boot.ts</span>'s startup sequence: agent (L45), command, skill (L43), config (L44) are <strong>all registered as plugins</strong>. <strong>"Plugin" is the unified extension paradigm running through opencode</strong>: whether you want to add a model provider, an agent, a command, or a skill, the routine is the same—write a self-contained plugin, hook it in, register it. Grasp the provider plugin and you grasp the skeleton of opencode's entire extensible architecture. Put differently, this lesson on the surface is about "how to connect thirty-some models," but at heart it's opencode's <strong>unified answer to all "one-to-many" extension</strong>—make the variable points (each provider, each agent, each command) pluggable plugins, leaving the constant core responsible only for the generic orchestration of "broadcast events, collect results." Variable and invariant thus part cleanly.</p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>This lesson clarifies how opencode uses a plugin architecture to support thirty-some model providers:</p>
  <ul>
    <li><strong>Each provider = one self-contained plugin</strong> (<span class="mono">core/src/plugin/provider/*.ts</span>), <span class="mono">PluginV2.define({ id, effect→hook table })</span>. The smallest <span class="mono">alibaba.ts</span> is under 20 lines. Thirty-some plugins gathered into the <span class="mono">ProviderPlugins</span> array. <strong>Adding a provider = add a file + add a line, no core change.</strong></li>
    <li><strong>Broadcast + self-claim</strong>: <span class="mono">aisdk.ts</span>'s <span class="mono">AISDK.language</span> triggers the <span class="mono">"aisdk.sdk"</span> event broadcasting to all plugins; each self-claims with <span class="mono">if (evt.package !== "@ai-sdk/xxx") return</span>, only the matching one's <span class="mono">createXxx(options)</span> sets <span class="mono">evt.sdk</span>. Core has zero if-else distinguishing providers.</li>
    <li><strong>Three hooks</strong>: <span class="mono">aisdk.sdk</span> (build SDK, everyone has it), <span class="mono">aisdk.language</span> (build language model, customizable routing, e.g. Copilot Responses/Chat), <span class="mono">catalog.transform</span> (rewrite catalog, e.g. Anthropic beta headers). <span class="mono">import("@ai-sdk/xxx")</span> dynamic import = lazy loading.</li>
    <li><strong>DynamicProviderPlugin catch-all</strong>: last in the array, <span class="mono">if (evt.sdk) return</span> steps up only when unclaimed, npm-installs the package, finds a <span class="mono">create*</span> export. Thirty-some fast path + one universal catch-all = supporting any provider.</li>
  </ul>
  <p>This completes M8 (config/Agents/Provider): L44 config defines intent, L45 the agent crystallizes a role, L46 MCP connects external hands, L47 Provider connects external brains. The full picture of a configurable, customizable, infinitely-extensible agent takes shape. And the "plugin is the unified extension paradigm running through the system" that provider plugins reveal (in <span class="mono">boot.ts</span>, agent/command/skill/config are all plugins) lays groundwork for what follows. The next part M9 turns to <strong>persistence and storage</strong>: how the sessions, messages, contexts the agent produces land on disk with Drizzle + SQLite, and how they migrate across versions.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p>The core "broadcast event, collect SDK" flow in <span class="mono">aisdk.ts</span> (simplified from source):</p>
  <pre class="code"><span class="cm">// not a single if (provider==="anthropic")-type branch!</span>
<span class="kw">const</span> sdk = sdks.<span class="fn">get</span>(sdkKey) ??
  (<span class="kw">yield*</span> plugin
    .<span class="fn">trigger</span>(<span class="st">"aisdk.sdk"</span>, { model, package: model.api.package, options }, {})
  ).sdk
<span class="kw">if</span> (!sdk)                                  <span class="cm">// a full broadcast, no one claimed</span>
  <span class="kw">return yield*</span> <span class="kw">new</span> <span class="fn">InitError</span>({
    providerID: model.providerID,
    cause: <span class="kw">new</span> <span class="fn">Error</span>(<span class="st">"No AISDK provider plugin returned an SDK"</span>),
  })
sdks.<span class="fn">set</span>(sdkKey, sdk)               <span class="cm">// cache: same package+options not rebuilt</span>
<span class="cm">// then trigger aisdk.language, letting plugins customize the model (e.g. Copilot picks endpoint)</span>
<span class="kw">const</span> result = <span class="kw">yield*</span> plugin.<span class="fn">trigger</span>(<span class="st">"aisdk.language"</span>, { model, sdk, options }, {})
<span class="kw">const</span> language = result.language ?? sdk.<span class="fn">languageModel</span>(model.api.id)</pre>
  <p>What's most worth savoring in this code is its "<strong>emptiness</strong>"—<strong>not one provider's name</strong> appears throughout. The core does only three generic things: broadcast <span class="mono">aisdk.sdk</span> to collect the SDK, broadcast <span class="mono">aisdk.language</span> to collect the language model, cache with <span class="mono">sdkKey</span> to avoid rebuilding. The concrete knowledge of "how Anthropic builds, how Copilot routes" is <strong>nowhere here</strong> but in each plugin. This is the essence of <strong>inversion of control (IoC)</strong>: the traditional way has the core actively call each provider (core depends on providers), while here <strong>the core defines the "broadcast-claim" protocol and providers hook into the core in reverse</strong> (providers depend on core). Flip the dependency direction and "adding a provider" turns from "editing the core's switch" into "writing a new plugin and hooking it in"—<strong>the core is open to extension, closed to modification</strong>, exactly what the open-closed principle looks like alive. And that <span class="mono">result.language ?? sdk.languageModel(...)</span> line: plugin didn't customize → take the SDK default, did → use the plugin's—<strong>using "optional override" to give every hook a gentle exit of "do nothing and get a sensible default."</strong></p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>Thirty-some providers = thirty-some self-contained plugins</strong> (<span class="mono">plugin/provider/*.ts</span>), <span class="mono">PluginV2.define({ id, effect→hook table })</span>, gathered into the <span class="mono">ProviderPlugins</span> array. <strong>Adding a provider = add a file + add a line, zero core change</strong> (open-closed principle).</li>
    <li><strong>Broadcast + self-claim</strong>: <span class="mono">aisdk.ts</span> triggers <span class="mono">"aisdk.sdk"</span> broadcasting to all plugins, each claims with <span class="mono">if (evt.package !== "@ai-sdk/xxx") return</span>, only the matching one <span class="mono">createXxx</span> sets <span class="mono">evt.sdk</span>. Core has zero if-else distinguishing providers = inversion of control.</li>
    <li><strong>Three hooks</strong>: <span class="mono">aisdk.sdk</span> (build SDK), <span class="mono">aisdk.language</span> (build language model, customize routing, e.g. Copilot Responses/Chat, echoing L31/35), <span class="mono">catalog.transform</span> (rewrite catalog, e.g. Anthropic beta headers, echoing L30). Each provider's quirks locked into its own plugin, core stays clean.</li>
    <li><strong>Dynamic import lazy-loads</strong>: <span class="mono">import("@ai-sdk/xxx")</span> means unused SDKs run no line, occupy no byte—"present cheaply, fulfilled expensively on demand" echoing at the provider layer.</li>
    <li><strong>DynamicProviderPlugin catch-all</strong>: last in the array, <span class="mono">if (evt.sdk) return</span>, npm-installs and finds a <span class="mono">create*</span> factory only when no built-in claimed. Thirty-some fast path + one universal catch-all = any provider. Provider is just one kind of opencode's <strong>unified plugin paradigm</strong> (in boot.ts, agent/command/skill/config are all plugins).</li>
  </ul>
</div>
""",
}
