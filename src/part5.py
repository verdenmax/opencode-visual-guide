"""Part 5 (Part 5 · Context System) content. Placeholders until M5 fills them in."""
from placeholder import wip

LESSON_21 = {
    "zh": r"""
<p class="lead">第四部分，我们把那台 agent 引擎从头看到尾——它会自驱地想、调工具、每轮重读历史。但有一个问题，我们一直<strong>故意含糊</strong>着：模型每轮读的那段「历史」里，除了你和它的对话，还藏着一批<strong>你从没打过的字</strong>——当前在哪个目录、今天几号、这是不是个 git 仓库、项目的 AGENTS.md 写了什么规矩……这些「<strong>环境底色</strong>」是谁、怎么、按什么规矩塞进模型视野的？这就是第五部分——<strong>上下文纪元（Context Epoch）系统</strong>——要回答的。这一课先建立总图：opencode 把这批「系统上下文」建模成一套<strong>可组合、带类型、能各自独立刷新</strong>的「源」。读懂这套设计，你就握住了 opencode「让模型恰到好处地了解它所处的世界」的钥匙。</p>
<p>为什么「往模型里塞环境信息」这件听起来很简单的事，值得一整个部分？因为它暗藏三道难关。其一，<strong>种类繁杂</strong>：目录、时间、git 状态、用户指令……形态各异，硬塞一坨字符串迟早乱成一团。其二，<strong>会变</strong>：你 <span class="mono">cd</span> 到别处、时间流逝、git 提交了——上下文是活的，得能<strong>刷新</strong>。其三，<strong>token 寸土寸金</strong>：第一次得把环境完整告诉模型（baseline），但之后每轮都重发一遍全文，纯属浪费——更聪明的做法是只发<strong>「变了什么」</strong>（update）。opencode 的解法，是给每一块环境信息都配一个<strong>懂得观察自己、比较自己、渲染自己</strong>的「源」，再用一套<strong>代数</strong>把它们统一组合起来。这一课就拆开这套优雅的抽象。</p>

<div class="card analogy">
  <div class="tag">📋 生活类比</div>
  把系统上下文想成一份<strong>出任务前的简报夹</strong>。夹子里分着几页：<strong>当前位置</strong>、<strong>日期</strong>、<strong>这片区域是不是己方领地</strong>（git 仓库）、<strong>上级的常规命令</strong>（AGENTS.md）……每一页都<strong>懂得自己更新</strong>：第一次交给特工时，写一份<strong>完整的本页内容</strong>（baseline）；之后再交，只附一张<strong>「本页相比上次变了什么」</strong>的便签（update）——绝不让特工每次都把整本夹子从头重读。更讲究的是：万一某页一时<strong>查不到</strong>（比如网络抖了），简报官<strong>不会把这页直接撕掉</strong>，而是标一句「暂不可用、稍后补」——因为「查不到」和「这页本就该删」是两码事，混淆了会让特工误以为某项情报消失了。这份会自我更新、还分得清「暂缺」与「删除」的简报夹，就是 opencode 的系统上下文。
</div>

<h2>什么是「系统上下文」</h2>
<p>先把概念钉清楚。模型每轮看到的输入，可以分成两类：一类是<strong>对话本身</strong>（你的提问、它的回答、工具结果——第 14~19 课讲的那些）；另一类，是<strong>对话之外、但模型必须知道的「环境底色」</strong>——你在哪个目录干活、今天的日期、当前是不是 git 仓库、项目根目录在哪、有哪些常驻指令。后者就是<strong>系统上下文（system context）</strong>，源码的措辞是「<strong>privileged system context</strong>」（特权系统上下文）——之所以「特权」，是因为它不是用户随口说的，而是系统<strong>替模型主动注入</strong>的、关于「你此刻身处何种世界」的可信事实。</p>
<div class="cellgroup">
  <div class="cell"><div class="k">core/environment</div><div class="v">工作目录、项目根、是否 git 仓库</div></div>
  <div class="cell"><div class="k">core/date</div><div class="v">当前日期</div></div>
  <div class="cell"><div class="k">指令上下文</div><div class="v">AGENTS.md 等常驻规矩（InstructionContext）</div></div>
  <div class="cell"><div class="k">…可扩展</div><div class="v">每个源一个命名空间 key，如 "core/environment"；新源即插即用</div></div>
</div>
<p>没有这层底色，模型就是个<strong>悬空的大脑</strong>：它不知道「这里」是哪、「现在」是何时、能不能用 git。系统上下文，就是把模型<strong>锚定到它所处的真实世界</strong>的那根缆绳。而这一部分要讲的，正是这根缆绳<strong>怎么被精心地编织、刷新、和持久化</strong>。</p>
<p>这里有个容易被忽略的设计选择值得点出：系统上下文是<strong>「特权」</strong>的——它和用户说的话<strong>不在一个层级</strong>。用户可能撒谎、可能记错，但「当前目录是 /home/proj」这种事实，是系统<strong>亲自观察、亲自背书</strong>的，模型可以无条件信任。把这两类信息（用户的话 vs 系统的事实）在来源上分清楚，对一个要动你文件、跑你命令的 agent 至关重要：它得知道哪些信息是<strong>铁打的环境真相</strong>、哪些只是对话里的一面之词。这条「特权」的界线，正是把系统上下文从普通消息里单拎出来、专门建一套机制伺候的根本理由。说到底，一个 agent 要安全地行动，前提是它得<strong>分得清自己脚下哪块地是实的</strong>。</p>

<h2>一个「源」：观察、比较、渲染</h2>
<p>opencode 的核心抽象，是把每一块系统上下文，建模成一个 <span class="mono">Source&lt;A&gt;</span>（<span class="mono">system-context/index.ts</span>）。它是一份<strong>声明</strong>，讲清这块上下文的三件事：怎么<strong>观察</strong>到它当前的值、怎么<strong>比较</strong>新旧值、怎么把它<strong>渲染</strong>成给模型看的文字。</p>
<div class="cellgroup">
  <div class="cell"><div class="k">key</div><div class="v">命名空间唯一标识，如 "core/date"</div></div>
  <div class="cell"><div class="k">load</div><div class="v">观察：取当前值（或返回 unavailable）</div></div>
  <div class="cell"><div class="k">codec</div><div class="v">值怎么序列化（好持久化、好比较）</div></div>
  <div class="cell"><div class="k">baseline(current)</div><div class="v">渲染：第一次的完整文本</div></div>
  <div class="cell"><div class="k">update(prev, cur)</div><div class="v">渲染：变化时的「差异」文本</div></div>
  <div class="cell"><div class="k">removed(prev)</div><div class="v">渲染：被移除时的文本（可选）</div></div>
</div>
<p>注意 <span class="mono">baseline</span> 和 <span class="mono">update</span> 这对孪生方法——它俩正是那道「token 难关」的解药。<strong>第一次</strong>把某个源纳入上下文，调 <span class="mono">baseline</span>，给模型一份完整介绍（「你在 /home/proj 目录，这是个 git 仓库」）；<strong>之后</strong>这个源的值变了，调 <span class="mono">update</span>，只告诉模型差异（「你刚 cd 到了 /home/proj/src」）。把「完整」与「增量」两种渲染做成源自己的职责，opencode 就能在<strong>「让模型知情」和「省 token」之间</strong>取得精确平衡——每个源自己最清楚，它的「全文」和「变化」该怎么写。</p>
<div class="cols">
  <div class="col"><h4>baseline · 第一次的全文</h4><p>把这块上下文完整告诉模型。「当前目录 /home/proj，git 仓库，项目根 /home/proj」。一次说清。</p></div>
  <div class="col"><h4>update · 之后的差异</h4><p>值变了只发增量。「目录已切到 /home/proj/src」。不重发全文，省下大把 token。</p></div>
</div>
<p>这对孪生方法背后，藏着一个对「上下文成本」的清醒认识：模型的每一个 token 都是钱、也都是有限上下文窗口里的一寸地皮。一个会聊上百轮的会话，如果每轮都把「当前目录、日期、git 状态」的全文重复一遍，累计浪费的 token 相当可观——而其中绝大多数轮，这些信息<strong>压根没变</strong>。把「首次」和「变化」拆成两个方法，等于让系统<strong>只在真正有新消息时才花那份 token</strong>。这是一种把「增量」思想贯彻到上下文层的精打细算：变化才值得被言说，不变就该沉默。</p>

<h2>代数：让不同类型的源统一组合</h2>
<p>难点在于：<span class="mono">core/date</span> 的值是个日期，<span class="mono">core/environment</span> 的值是个目录结构——<strong>类型各不相同</strong>。怎么把这些「值类型各异」的源装进同一个容器、统一处理？答案是 <span class="mono">make&lt;A&gt;(source)</span>：它<strong>把具体的值类型 <span class="mono">A</span> 藏起来（closes over A）</strong>，产出一个<strong>不透明的 <span class="mono">SystemContext</span></strong>——从外面看，所有源都长一个样，无论它内部装的是日期还是目录。于是 <span class="mono">combine([...])</span> 就能把一堆类型迥异的源<strong>均匀地拼成一个</strong>。</p>
<div class="flow">
  <div class="node">Source&lt;Date&gt;<span class="sub">core/date</span></div>
  <div class="arrow">make →</div>
  <div class="node">SystemContext<span class="sub">藏起类型·不透明</span></div>
  <div class="arrow">combine →</div>
  <div class="node">一个组合上下文<span class="sub">均匀处理</span></div>
  <div class="arrow">initialize →</div>
  <div class="node">Generation<span class="sub">baseline 文本 + Snapshot</span></div>
</div>
<p>这正是「<strong>代数</strong>」二字的含义：<span class="mono">make</span> 把异类的源<strong>归一</strong>成同一种可组合的东西，<span class="mono">combine</span> 把它们<strong>合并</strong>，就像数字能被「加」、集合能被「并」一样——一套统一的运算，作用在一堆看似不同的东西上。把值类型藏进 <span class="mono">make</span> 这一手，是整套设计优雅的支点：它让「再加一种新的上下文源」变成一件<strong>无需改动任何现有代码</strong>的事——你只管写一个新 <span class="mono">Source</span>、<span class="mono">make</span> 一下、<span class="mono">combine</span> 进去，整个系统对它一视同仁。这是第 6 课「面向接口、实现可插拔」那套思想，在「上下文」这个维度上的又一次绽放。</p>
<div class="cols">
  <div class="col"><h4>❌ 一坨死字符串</h4><p>把目录、日期、git、指令拼成一大段文本硬塞。加一种就改一处拼接逻辑；想做 baseline/update 增量？做不到——信息一拼就成了铁板一块。</p></div>
  <div class="col"><h4>✅ 源的代数</h4><p>每块是一个能自观察/比较/渲染的源，make/combine 统一组合。加新源零改动；每个源各自决定全文与增量。扩展性与省 token 兼得。</p></div>
</div>
<p>顺带点破 <span class="mono">initialize</span> 这一步：把组合好的上下文「初始化」一遍，会观察所有源、产出一个 <span class="mono">Generation</span>——里面装着<strong>给模型看的 baseline 全文</strong>，和一份 <span class="mono">Snapshot</span>（每个源当前值的<strong>结构化快照</strong>，留着下次比较用）。这个 Snapshot 是整套「增量」机制的记忆：没有它，系统就不知道「上次是什么样」，也就无从算出「这次变了什么」。换句话说，<span class="mono">baseline</span> 负责说，<span class="mono">Snapshot</span> 负责记——一说一记，下一轮的 <span class="mono">update</span> 才有据可依。这条「观察→渲染 baseline + 留 Snapshot→下次比对出 update」的链路，就是第 22~25 课要一步步拧紧的主线。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景·第五部分序幕</div>
  <p>这一课为整个第五部分立了纲。系统上下文这套设计，会在接下来几课层层展开：</p>
  <ul>
    <li><strong>第 21 课·本课</strong>：总图——系统上下文 = 一套可组合、带类型、能独立刷新的<strong>源</strong>（Source 代数）。</li>
    <li><strong>第 22 课</strong>：单个<strong>源</strong>怎么观察/比较/渲染（baseline vs update 的细节）。</li>
    <li><strong>第 23 课</strong>：<strong>注册表</strong>——源怎么注册、汇总。</li>
    <li><strong>第 24 课</strong>：<strong>上下文纪元</strong>——把 baseline 持久化成 baselineSeq（接回第 19 课 history.load 那条裁边线！）。</li>
    <li><strong>第 25~27 课</strong>：对话中途的刷新、内置源、换 agent 触发新纪元。</li>
  </ul>
  <p>记住这一课最核心的直觉：<strong>opencode 不把环境信息当一坨死字符串硬塞，而是把每一块都做成一个「懂得观察、比较、渲染自己」的源，再用代数统一组合。</strong>这套抽象，是它能优雅应对「上下文会变、token 要省、种类要扩展」三道难关的总钥匙。下一课，我们就拧开第一把锁——深入单个源，看 <span class="mono">baseline</span> 与 <span class="mono">update</span> 这对孪生渲染，到底怎么把「省 token」做到极致。</p>
  <div class="layers">
    <div class="layer l-app"><div class="lh"><span class="badge">L21</span><span class="name">Source 代数（本课）</span></div><div class="ld">系统上下文 = 可组合、带类型、独立刷新的源</div></div>
    <div class="layer l-part"><div class="lh"><span class="badge">L22-23</span><span class="name">源 + 注册表</span></div><div class="ld">单源怎么观察/比较/渲染；源怎么注册汇总</div></div>
    <div class="layer l-main"><div class="lh"><span class="badge">L24-25</span><span class="name">上下文纪元 + 中途刷新</span></div><div class="ld">持久化 baselineSeq（接回 L19）；对话中途更新</div></div>
    <div class="layer l-core"><div class="lh"><span class="badge">L26-27</span><span class="name">内置源 + 换 agent</span></div><div class="ld">具体内置源；换 agent 触发新纪元（AgentReplacementBlocked）</div></div>
  </div>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p>「暂不可用」和「已移除」是两码事——这个区分，源码用一句注释和一个专门的符号 <span class="mono">unavailable</span> 钉得死死的：</p>
  <pre class="code"><span class="cm">// system-context/index.ts</span>
<span class="cm">// 表示某个源"一时观察不到"，但不等于"该把它从上下文里删掉"</span>
<span class="kw">export const</span> unavailable = Symbol.<span class="fn">for</span>(<span class="st">"@opencode/SystemContext.Unavailable"</span>)

<span class="cm">// load 可以返回真实值 A，也可以返回 unavailable：</span>
load: Effect.Effect&lt;A | Unavailable&gt;</pre>
  <p>读这段注释的良苦用心：<span class="mono">load</span> 返回 <span class="mono">unavailable</span>，意思是「这个源此刻没观察成功（也许网络抖了一下）」——但系统<strong>绝不</strong>因此就当它被删了。区别在哪？<strong>刷新时，它会保住上一份已采纳的快照</strong>，宁可等一等，也不会悄悄拼出一份缺了这块的、不完整的 baseline。把「暂缺」和「删除」严格分开，是这种「关乎正确性的细节」最容易被忽略、也最能体现功力的地方：一个粗糙的实现会把「没读到」直接当「没有」，于是模型某轮突然以为「这里不再是 git 仓库了」——而其实只是那一下没查成。opencode 用一个专门的符号，杜绝了这种鬼影。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>系统上下文（system context）</strong>是对话之外、系统替模型主动注入的「环境底色」：工作目录、日期、git 状态、常驻指令——把模型锚定到它所处的真实世界。</li>
    <li>三道难关：<strong>种类繁杂、会变、token 寸土寸金</strong>。opencode 的解法是把每块上下文做成一个能<strong>观察/比较/渲染</strong>自己的源。</li>
    <li><strong>Source&lt;A&gt;</strong> 声明六件事：key、load（观察）、codec、<strong>baseline（首次全文）</strong>、<strong>update（变化差异）</strong>、removed。baseline/update 这对孪生是「省 token」的解药。</li>
    <li><strong>代数</strong>：<span class="mono">make&lt;A&gt;</span> 把值类型藏起、归一成不透明的 <span class="mono">SystemContext</span>，<span class="mono">combine</span> 统一组合——加新源无需改任何现有代码（第 6 课思想的延伸）。</li>
    <li><strong>unavailable ≠ removed</strong>：「暂时观察不到」不等于「删除」；刷新保住上一份快照，绝不悄悄拼出残缺 baseline——关乎正确性的关键细节。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">In Part 4 we saw that agent engine end to end — it thinks self-drivenly, calls tools, rereads history each round. But one question we kept <strong>deliberately vague</strong>: in the "history" the model reads each round, beyond your conversation hides a batch of words <strong>you never typed</strong> — which directory it's in, today's date, whether this is a git repo, what rules the project's AGENTS.md lays down… Who, how, and by what rules is this "<strong>ambient backdrop</strong>" injected into the model's view? That's what Part 5 — the <strong>Context Epoch system</strong> — answers. This lesson builds the master diagram first: opencode models this "system context" as a set of <strong>composable, typed, independently-refreshable</strong> "sources." Understand this design and you hold the key to opencode's "letting the model know its world just right."</p>
<p>Why does "injecting environment info into the model," which sounds simple, deserve a whole part? Because it hides three hurdles. First, <strong>variety</strong>: directory, time, git status, user instructions… all different shapes; cramming one blob of string in eventually turns into a mess. Second, <strong>it changes</strong>: you <span class="mono">cd</span> elsewhere, time passes, git commits — context is alive and must <strong>refresh</strong>. Third, <strong>tokens are precious</strong>: the first time you must tell the model the full environment (baseline), but resending the full text every round is pure waste — smarter is to send only <strong>"what changed"</strong> (update). opencode's solution gives each piece of environment info a "source" that <strong>knows how to observe, compare, and render itself</strong>, then composes them uniformly with an <strong>algebra</strong>. This lesson unpacks this elegant abstraction.</p>

<div class="card analogy">
  <div class="tag">📋 Analogy</div>
  Think of system context as a <strong>mission briefing folder</strong>. The folder has several pages: <strong>current location</strong>, <strong>date</strong>, <strong>whether this area is friendly territory</strong> (git repo), <strong>standing orders from command</strong> (AGENTS.md)… Each page <strong>knows how to update itself</strong>: the first time handed to the agent, write a <strong>complete version of this page</strong> (baseline); handed again later, just attach a sticky note of <strong>"what changed on this page since last time"</strong> (update) — never making the agent reread the whole folder every time. Even finer: if a page is momentarily <strong>unobtainable</strong> (say the network hiccuped), the briefing officer <strong>doesn't tear the page out</strong> but marks "temporarily unavailable, to follow" — because "can't fetch" and "this page should be deleted" are two different things, and confusing them would make the agent think some intel vanished. This self-updating folder that distinguishes "temporarily missing" from "deleted" is opencode's system context.
</div>

<h2>What is "system context"</h2>
<p>First nail down the concept. The model's input each round splits in two: one is <strong>the conversation itself</strong> (your questions, its answers, tool results — what Lessons 14-19 covered); the other is <strong>the "ambient backdrop" outside the conversation that the model must know</strong> — which directory you work in, today's date, whether it's a git repo now, where the project root is, what standing instructions exist. The latter is <strong>system context</strong>, which the source calls "<strong>privileged system context</strong>" — "privileged" because it's not something the user casually said but trusted facts the system <strong>actively injects on the model's behalf</strong> about "what world you're in right now."</p>
<div class="cellgroup">
  <div class="cell"><div class="k">core/environment</div><div class="v">working directory, project root, whether a git repo</div></div>
  <div class="cell"><div class="k">core/date</div><div class="v">current date</div></div>
  <div class="cell"><div class="k">instruction context</div><div class="v">standing rules like AGENTS.md (InstructionContext)</div></div>
  <div class="cell"><div class="k">…extensible</div><div class="v">one namespaced key per source, e.g. "core/environment"; new sources plug in</div></div>
</div>
<p>Without this backdrop, the model is a <strong>brain suspended in air</strong>: it doesn't know where "here" is, when "now" is, whether it can use git. System context is the cable that <strong>anchors the model to its real world</strong>. And what this part covers is exactly how this cable is <strong>carefully woven, refreshed, and persisted</strong>.</p>
<p>A design choice easily overlooked is worth pointing out: system context is <strong>"privileged"</strong> — it's <strong>not on the same level</strong> as what the user says. The user may lie or misremember, but a fact like "the current directory is /home/proj" is something the system <strong>observed and vouched for itself</strong>, which the model can trust unconditionally. Separating these two kinds of info (the user's words vs the system's facts) by source is crucial for an agent that touches your files and runs your commands: it must know which info is <strong>ironclad environmental truth</strong> and which is just one side of a conversation. This "privileged" line is the fundamental reason for lifting system context out of ordinary messages and building a dedicated mechanism for it.</p>

<h2>A "source": observe, compare, render</h2>
<p>opencode's core abstraction models each piece of system context as a <span class="mono">Source&lt;A&gt;</span> (<span class="mono">system-context/index.ts</span>). It's a <strong>declaration</strong> spelling out three things about this context: how to <strong>observe</strong> its current value, how to <strong>compare</strong> old and new, and how to <strong>render</strong> it into text for the model.</p>
<div class="cellgroup">
  <div class="cell"><div class="k">key</div><div class="v">namespaced unique identity, e.g. "core/date"</div></div>
  <div class="cell"><div class="k">load</div><div class="v">observe: get the current value (or return unavailable)</div></div>
  <div class="cell"><div class="k">codec</div><div class="v">how the value serializes (for persistence and comparison)</div></div>
  <div class="cell"><div class="k">baseline(current)</div><div class="v">render: the first-time full text</div></div>
  <div class="cell"><div class="k">update(prev, cur)</div><div class="v">render: the "diff" text on change</div></div>
  <div class="cell"><div class="k">removed(prev)</div><div class="v">render: text on removal (optional)</div></div>
</div>
<p>Note the twin methods <span class="mono">baseline</span> and <span class="mono">update</span> — they're the antidote to that "token hurdle." The <strong>first time</strong> a source enters the context, call <span class="mono">baseline</span>, giving the model a full intro ("you're in /home/proj, it's a git repo"); <strong>later</strong> when the source's value changes, call <span class="mono">update</span>, telling the model only the diff ("you just cd'd to /home/proj/src"). Making "full" and "incremental" rendering the source's own responsibility lets opencode strike a precise balance <strong>between "keeping the model informed" and "saving tokens"</strong> — each source knows best how to write its "full text" and its "change."</p>
<div class="cols">
  <div class="col"><h4>baseline · the first-time full text</h4><p>Tell the model this context in full. "Current dir /home/proj, git repo, project root /home/proj." Said once, clearly.</p></div>
  <div class="col"><h4>update · the later diff</h4><p>On change, send only the increment. "Directory switched to /home/proj/src." No resending the full text, saving heaps of tokens.</p></div>
</div>
<p>Behind these twin methods is a clear-eyed grasp of "context cost": every token of the model is money, and an inch of land in a finite context window. A session that chats hundreds of rounds, if it repeats the full "current directory, date, git status" each round, wastes a considerable cumulative amount of tokens — when in the vast majority of rounds, this info <strong>hasn't changed at all</strong>. Splitting "first time" and "change" into two methods lets the system <strong>spend that token only when there's truly new information</strong>. It's a frugality that carries the "incremental" idea into the context layer: change deserves to be spoken, sameness should stay silent.</p>

<h2>The algebra: composing sources of different types uniformly</h2>
<p>The difficulty: <span class="mono">core/date</span>'s value is a date, <span class="mono">core/environment</span>'s is a directory structure — <strong>different types</strong>. How to put these "differently-typed-value" sources in one container and handle them uniformly? The answer is <span class="mono">make&lt;A&gt;(source)</span>: it <strong>hides the concrete value type <span class="mono">A</span> (closes over A)</strong>, producing an <strong>opaque <span class="mono">SystemContext</span></strong> — from outside, all sources look the same, whether inside is a date or a directory. So <span class="mono">combine([...])</span> can <strong>uniformly stitch</strong> a pile of wildly-different sources into one.</p>
<div class="flow">
  <div class="node">Source&lt;Date&gt;<span class="sub">core/date</span></div>
  <div class="arrow">make →</div>
  <div class="node">SystemContext<span class="sub">type hidden · opaque</span></div>
  <div class="arrow">combine →</div>
  <div class="node">one composed context<span class="sub">handled uniformly</span></div>
  <div class="arrow">initialize →</div>
  <div class="node">Generation<span class="sub">baseline text + Snapshot</span></div>
</div>
<p>This is what "<strong>algebra</strong>" means: <span class="mono">make</span> <strong>unifies</strong> heterogeneous sources into one composable thing, <span class="mono">combine</span> <strong>merges</strong> them, just as numbers can be "added" and sets "unioned" — one uniform operation acting on a pile of seemingly different things. Hiding the value type inside <span class="mono">make</span> is the elegant pivot of the whole design: it makes "add a new kind of context source" something <strong>requiring no change to any existing code</strong> — you just write a new <span class="mono">Source</span>, <span class="mono">make</span> it, <span class="mono">combine</span> it in, and the whole system treats it equally. This is Lesson 6's "program to an interface, pluggable implementations" blooming again on the "context" dimension.</p>
<div class="cols">
  <div class="col"><h4>❌ one blob of dead string</h4><p>Concatenate directory, date, git, instructions into one big text and cram it. Adding a kind means editing the concat logic; want baseline/update increments? Can't — once concatenated, info becomes a monolith.</p></div>
  <div class="col"><h4>✅ the algebra of sources</h4><p>Each piece is a self-observing/comparing/rendering source, uniformly composed by make/combine. New source, zero change; each source decides its full text and increment. Extensibility and token-saving, both.</p></div>
</div>
<p>Note also the <span class="mono">initialize</span> step: "initializing" the composed context observes all sources and produces a <span class="mono">Generation</span> — holding <strong>the baseline full text for the model</strong> and a <span class="mono">Snapshot</span> (a <strong>structured snapshot</strong> of each source's current value, kept for next comparison). This Snapshot is the memory of the whole "incremental" mechanism: without it the system wouldn't know "what it looked like last time," hence couldn't compute "what changed this time." In other words, <span class="mono">baseline</span> speaks, <span class="mono">Snapshot</span> remembers — one speaks, one remembers, so the next round's <span class="mono">update</span> has ground to stand on. This chain of "observe → render baseline + keep Snapshot → diff into update next time" is the main line Lessons 22-25 tighten step by step.</p>

<div class="card macro">
  <div class="tag">🗺️ The big picture · Part 5 prologue</div>
  <p>This lesson sets the outline for all of Part 5. This system-context design unfolds layer by layer over the next lessons:</p>
  <ul>
    <li><strong>Lesson 21 · this one</strong>: the master diagram — system context = a set of composable, typed, independently-refreshable <strong>sources</strong> (the Source algebra).</li>
    <li><strong>Lesson 22</strong>: how a single <strong>source</strong> observes/compares/renders (the detail of baseline vs update).</li>
    <li><strong>Lesson 23</strong>: the <strong>registry</strong> — how sources register and gather.</li>
    <li><strong>Lesson 24</strong>: the <strong>context epoch</strong> — persisting the baseline into a baselineSeq (reconnecting to Lesson 19's history.load edge-trim line!).</li>
    <li><strong>Lessons 25-27</strong>: mid-conversation refresh, built-in sources, agent switch triggering a new epoch.</li>
  </ul>
  <p>Remember this lesson's core intuition: <strong>opencode doesn't cram environment info as one dead string but makes each piece a source that "knows how to observe, compare, render itself," then composes them uniformly with an algebra.</strong> This abstraction is the master key to gracefully facing the three hurdles "context changes, tokens must be saved, kinds must extend." Next lesson we turn the first lock — diving into a single source to see how the twin renderings <span class="mono">baseline</span> and <span class="mono">update</span> push "token-saving" to the extreme.</p>
  <div class="layers">
    <div class="layer l-app"><div class="lh"><span class="badge">L21</span><span class="name">the Source algebra (this lesson)</span></div><div class="ld">system context = composable, typed, independently-refreshable sources</div></div>
    <div class="layer l-part"><div class="lh"><span class="badge">L22-23</span><span class="name">source + registry</span></div><div class="ld">how a single source observes/compares/renders; how sources register and gather</div></div>
    <div class="layer l-main"><div class="lh"><span class="badge">L24-25</span><span class="name">context epoch + mid-conversation refresh</span></div><div class="ld">persist baselineSeq (reconnecting L19); mid-conversation update</div></div>
    <div class="layer l-core"><div class="lh"><span class="badge">L26-27</span><span class="name">built-in sources + agent switch</span></div><div class="ld">concrete built-ins; agent switch triggers a new epoch (AgentReplacementBlocked)</div></div>
  </div>
</div>

<div class="card detail">
  <div class="tag">🔬 Source detail</div>
  <p>"Temporarily unavailable" and "removed" are two different things — a distinction the source nails with one comment and a dedicated symbol <span class="mono">unavailable</span>:</p>
  <pre class="code"><span class="cm">// system-context/index.ts</span>
<span class="cm">// indicates a source "can't be observed right now" — NOT "delete it from the context"</span>
<span class="kw">export const</span> unavailable = Symbol.<span class="fn">for</span>(<span class="st">"@opencode/SystemContext.Unavailable"</span>)

<span class="cm">// load may return a real value A, or unavailable:</span>
load: Effect.Effect&lt;A | Unavailable&gt;</pre>
  <p>Read the care in this comment: <span class="mono">load</span> returning <span class="mono">unavailable</span> means "this source failed to observe right now (maybe the network hiccuped)" — but the system <strong>never</strong> therefore treats it as deleted. The difference? <strong>On refresh, it preserves the last admitted snapshot</strong>, rather wait than silently assemble an incomplete baseline missing this piece. Strictly separating "temporarily missing" from "deleted" is exactly the kind of correctness-bearing detail that's easiest to overlook and most reveals craft: a crude implementation treats "couldn't read" directly as "absent," so one round the model suddenly thinks "this is no longer a git repo" — when really that one fetch just failed. opencode uses a dedicated symbol to banish this ghost.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key points</div>
  <ul>
    <li><strong>System context</strong> is the "ambient backdrop" the system actively injects on the model's behalf, outside the conversation: working directory, date, git status, standing instructions — anchoring the model to its real world.</li>
    <li>Three hurdles: <strong>variety, change, precious tokens</strong>. opencode's solution makes each piece a source that <strong>observes/compares/renders</strong> itself.</li>
    <li><strong>Source&lt;A&gt;</strong> declares six things: key, load (observe), codec, <strong>baseline (first-time full)</strong>, <strong>update (the change diff)</strong>, removed. The baseline/update twin is the antidote to "saving tokens."</li>
    <li><strong>The algebra</strong>: <span class="mono">make&lt;A&gt;</span> hides the value type, unifying into an opaque <span class="mono">SystemContext</span>, <span class="mono">combine</span> composes uniformly — adding a new source requires no change to any existing code (an extension of Lesson 6's idea).</li>
    <li><strong>unavailable ≠ removed</strong>: "temporarily unobservable" isn't "deleted"; refresh preserves the last snapshot, never silently assembling an incomplete baseline — a key correctness detail.</li>
  </ul>
</div>
""",
}
LESSON_22 = {
    "zh": r"""
<p class="lead">上一课我们俯瞰了系统上下文的全景——一套可组合的「源」，配一对 <span class="mono">baseline</span>/<span class="mono">update</span> 孪生渲染。这一课，我们把镜头怼到<strong>单个源</strong>身上，看它的一生：它怎么<strong>观察</strong>到自己当前的值，怎么把这个值<strong>快照</strong>下来留作记忆，又怎么在下一轮<strong>比较</strong>出「变了没、变了啥」，从而决定该闭嘴、该报差异、还是该从头说起。这套机制的精巧之处，全藏在一个叫 <span class="mono">codec</span> 的小字段里——它一个人，撑起了「序列化、反序列化、判等」三副担子。读懂单个源怎么转，你就摸清了整套上下文增量更新的发动机。</p>
<p>为什么要花一课死磕「一个源怎么工作」？因为<strong>魔鬼全在细节里</strong>。「检测一个值变没变」听起来简单，可一旦较真，问题就冒出来：值的类型五花八门（日期、目录、字符串列表），怎么统一地比？存下来的旧值，万一格式都对不上了（源的 schema 改过）怎么办？「没读到」和「值变了」怎么区分？opencode 没有为每个源手写一套比较逻辑，而是用一个统一的 <span class="mono">codec</span>，把这些琐碎而易错的活<strong>一次性、类型安全地</strong>解决掉。这一课，就看它怎么做到的。</p>

<div class="card analogy">
  <div class="tag">📄 生活类比</div>
  还记得上一课那本简报夹吗？这一课我们盯着<strong>其中一页</strong>看。这一页有一份<strong>「格式规范」</strong>（codec）——它规定了这页内容<strong>怎么落成白纸黑字</strong>（序列化）、<strong>怎么读懂一份旧的本页存档</strong>（反序列化）、以及<strong>怎么判断两份存档说的是不是一回事</strong>（判等）。每次要更新这页，简报官就照规范走三步：先把<strong>上次的存档</strong>读出来，和<strong>这次新观察到的</strong>比一比——<strong>一样？</strong>那就一个字都不写，省纸（Unchanged）；<strong>不一样？</strong>写一张「这次相比上次变了什么」的便签（Updated）；<strong>连旧存档都读不懂了？</strong>（比如格式规范升级过、旧档作废）那就别勉强比对，干脆重写一份完整的（Incompatible）。一份「格式规范」，就把这页的写、读、比三件事全管了——这就是 codec 的全部魔力。
</div>

<h2>codec：一个字段，三副担子</h2>
<p>每个 <span class="mono">Source&lt;A&gt;</span> 都要提供一个 <span class="mono">codec</span>——一个描述「值类型 <span class="mono">A</span> 怎么和 JSON 互转」的 <span class="mono">Schema.Codec</span>。<span class="mono">make</span> 函数拿到它，<strong>立刻从它身上派生出三样工具</strong>：</p>
<pre class="code"><span class="cm">// 简化自 system-context/index.ts 的 make()</span>
<span class="kw">const</span> decode = Schema.<span class="fn">decodeUnknownOption</span>(source.codec)  <span class="cm">// 反序列化：旧存档 → 值</span>
<span class="kw">const</span> encode = Schema.<span class="fn">encodeSync</span>(source.codec)          <span class="cm">// 序列化：值 → 可存的 JSON</span>
<span class="kw">const</span> equivalent = Schema.<span class="fn">toEquivalence</span>(source.codec)    <span class="cm">// 判等：两个值一样吗</span></pre>
<p>这是整套设计最优雅的一笔。源的作者<strong>只需声明一件事</strong>——「我的值长这样」（一个 codec），框架就<strong>白送</strong>了他三种能力：把值<strong>编码</strong>成能存进快照的 JSON、把存下的快照<strong>解码</strong>回值、以及<strong>判断</strong>两个值等不等。尤其那个 <span class="mono">toEquivalence</span>——它从「值的结构描述」里，<strong>自动推导出了「怎么比较两个这种值」</strong>。源的作者再也不用手写「日期怎么比、目录结构怎么比」这种又琐碎又容易写错的判等逻辑了：<strong>声明结构，判等自来。</strong></p>
<div class="cellgroup">
  <div class="cell"><div class="k">encode</div><div class="v">值 → JSON：存进快照（Snapshot）留作记忆</div></div>
  <div class="cell"><div class="k">decode</div><div class="v">JSON → 值：把上次的快照读回来（可能失败 → Option）</div></div>
  <div class="cell"><div class="k">equivalent</div><div class="v">值 × 值 → 布尔：自动推导的判等，检测「变了没」，无需手写</div></div>
</div>
<div class="cols">
  <div class="col"><h4>❌ 每个源手写判等</h4><p>日期源写「比年月日」、目录源写「逐字段比」、列表源写「逐项比」……N 个源 N 套比较逻辑，琐碎、重复、容易写错（漏比一个字段就漏报变化）。</p></div>
  <div class="col"><h4>✅ 声明 codec，判等自来</h4><p>每个源只声明「值长这样」，<span class="mono">toEquivalence</span> 从结构自动推出判等。N 个源共享同一套推导，零手写、不漏比，省心又可靠。</p></div>
</div>
<p>别小看「判等自动推导」这件事的份量。在很多代码库里，「两个对象算不算相等」是 bug 的重灾区：有人忘了比某个新加的字段，有人把引用相等错当成值相等，有人在嵌套结构里比漏了一层。这些 bug 还特别隐蔽——它只在「值其实变了、却被误判为没变」时悄悄发作，表现为「模型怎么不知道我 cd 了」这种莫名其妙的现象。opencode 用 <span class="mono">Schema.toEquivalence(codec)</span> 把判等<strong>从「人来写」变成「从结构推」</strong>，等于把这一整类 bug 连根拔掉：只要你的 codec 如实描述了值的结构，判等就自动正确，再不会因为「手写比较时漏了一笔」而误判。<strong>让正确成为默认、而非靠每个人小心翼翼</strong>——这正是第 8 课工具箱那套「护栏」哲学，在上下文层的又一次现身。说到底，正确不该是某个人的功劳或疏忽，而该是结构本身带来的必然。</p>

<h2>baseline：观察一次，留下记忆</h2>
<p>一个源被纳入上下文时，先走 <span class="mono">load</span> 观察出当前值。若 <span class="mono">load</span> 返回 <span class="mono">unavailable</span>（上一课讲过：暂缺，非删除），就此打住、保住旧状态。若拿到了真实值，就产出一个 <span class="mono">baseline</span> 渲染——它做两件事：调 <span class="mono">source.baseline(value)</span> 得到<strong>给模型看的全文</strong>，同时把 <span class="mono">encode(value)</span> 的结果<strong>存进一个 <span class="mono">SourceSnapshot</span></strong>。</p>
<div class="flow">
  <div class="node">load<span class="sub">观察当前值</span></div>
  <div class="arrow">unavailable? → 止</div>
  <div class="node">baseline(value)<span class="sub">渲染全文</span></div>
  <div class="arrow">+</div>
  <div class="node">encode(value)<span class="sub">存进 Snapshot</span></div>
</div>
<p>这里「一说一记」的配合是关键：<span class="mono">baseline</span> 那段全文，是<strong>说给模型听</strong>的（进入它的上下文）；而那份 <span class="mono">encode</span> 出来的快照，是<strong>记给系统自己</strong>的（存着，下次比较用）。说给模型的是人类可读的散文（「你在 /home/proj，这是 git 仓库」），记给自己的是结构化的 JSON（<span class="mono">{"dir":"/home/proj","git":true}</span>）。<strong>同一次观察，渲染出两种形态：一种为了沟通，一种为了记忆。</strong>没有那份记忆，下一轮就无从知道「变了没」——快照，是整个增量机制的锚点。</p>
<p>为什么不干脆拿「给模型的那段全文」当记忆、下次直接比文本？因为<strong>人话和机器记忆，要的东西正好相反</strong>。给模型的散文追求<strong>可读</strong>，可能这一版写「你在 /home/proj」、下一版心血来潮写成「当前工作目录：/home/proj」——文字变了，事实没变，若拿文本比就会误报一次「变化」。而 <span class="mono">encode</span> 出的结构化快照追求<strong>精确</strong>：它只记那个规范化的值（<span class="mono">{"dir":"/home/proj"}</span>），不掺任何措辞。拿结构比结构，<span class="mono">equivalent</span> 才能干净利落地回答「事实到底变没变」，不被表达方式的抖动干扰。<strong>沟通用散文、记忆用结构</strong>——把这两件事分开，是这个源能既「说得人话」又「比得精准」的根本。</p>

<h2>compare：变了没？变了啥？</h2>
<p>下一轮，这个源再次被观察。这次它手里多了一样东西：<strong>上一轮存下的快照</strong>。于是它走 <span class="mono">compare(previous)</span>，三步定乾坤：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">decode(previous)：把上次的快照解码回值。解不出来？→ Incompatible（schema 变过，旧档作废）</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">解出来了 → equivalent(旧值, 新值)：一样吗？</span></div>
  <div class="t-row"><span class="t-num">3a</span><span class="t-txt">一样 → Unchanged：一个字都不发，省 token</span></div>
  <div class="t-row"><span class="t-num">3b</span><span class="t-txt">不一样 → Updated：调 update(旧, 新) 渲染差异，并存下新快照</span></div>
</div>
<p>这三个结果，对应着一个值在两轮之间可能的全部命运。<strong>Unchanged</strong> 是最常见、也最省的情况——大多数轮，目录没变、日期没变，那就<strong>沉默</strong>，不浪费模型一个 token。<strong>Updated</strong> 是真有变化时的正路——渲染一份「差异」，并<strong>顺手更新快照</strong>（这样下下轮又能和这次比）。最微妙的是 <strong>Incompatible</strong>：它意味着<strong>连上次的快照都解码不出来了</strong>——通常是因为这个源的 <span class="mono">codec</span> 在两轮之间被改过（比如版本升级），旧格式的快照成了「天书」。这时候硬去 diff 是危险的，明智的做法是<strong>放弃增量、退回重来</strong>（重新 baseline）。这个分支看似冷门，却是一个长期演进的系统必须考虑的现实：<strong>数据的格式会变，而你存下的旧数据不会自动跟着变。</strong></p>
<p><span class="mono">Incompatible</span> 这一分支，最能看出这套设计的成熟。一个只想着「跑通」的实现，根本不会去想「万一旧快照解不出来怎么办」——它会假设存下的东西永远读得回来，于是某天 codec 一升级，旧快照解码时直接抛个异常、循环崩在半路。opencode 偏偏正面接住了这种情况：解不出来？那是<strong>预料之中的一种结果</strong>，不是意外——退回去重新 baseline 就是了，模型顶多这一轮多收一份全文，绝不会因此崩溃。<strong>能优雅地处理「自己存的旧数据已经读不懂了」，是一个系统从『能用』走向『耐用』的标志</strong>：它默认了「我也会变，我的过去未必还认得我的现在」，并为这种自我演进预留了一条不慌不乱的退路。</p>
<div class="cols">
  <div class="col"><h4>Unchanged · 沉默</h4><p>值没变。一个 token 都不发。最常见、最省。</p></div>
  <div class="col"><h4>Updated · 报差异</h4><p>值变了。渲染 update 差异文本，更新快照。</p></div>
  <div class="col"><h4>Incompatible · 重来</h4><p>旧快照解不出（schema 变了）。放弃增量、退回重 baseline，绝不硬比。</p></div>
</div>
<p>把一个源在连续几轮里的遭遇连起来看，这套机制的节律就清楚了：</p>
<div class="timeline">
  <div class="tl-item"><span class="tl-time">第 1 轮</span><span class="tl-desc">首次纳入 → baseline：发全文「你在 /home/proj，git 仓库」+ 存快照 {dir,git}</span></div>
  <div class="tl-item"><span class="tl-time">第 2 轮</span><span class="tl-desc">compare：解出旧快照，equivalent 判定一样 → Unchanged → 沉默</span></div>
  <div class="tl-item"><span class="tl-time">第 3 轮</span><span class="tl-desc">你 cd 了 → compare：不一样 → Updated「目录切到 /home/proj/src」+ 更新快照</span></div>
  <div class="tl-item"><span class="tl-time">第 4 轮</span><span class="tl-desc">没再动 → compare：和第 3 轮的快照比 → Unchanged → 又沉默</span></div>
</div>
<p>看这条时间线，你会发现一个源<strong>绝大多数时候都在「沉默」</strong>——只有在它真正发生变化的那一轮，才花一份 token 说一句「我变成这样了」。这正是 baseline/update 这套设计的回报在微观层面的兑现：<strong>上下文不是每轮重新灌一遍，而是像水面一样，平时风平浪静、有波动才泛起一圈涟漪。</strong>一个聊几小时的会话，环境信息真正变化的次数屈指可数，于是这套机制省下的，是成百上千轮里本会被白白重复的 token。而每一次「涟漪」，又都靠着上一轮留下的那份快照做参照——<strong>记忆，让沉默成为可能。</strong></p>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <p>这一课把单个源的「一生」讲透了，它正是上一课那套代数的<strong>微观引擎</strong>：</p>
  <ul>
    <li><strong>codec 一肩三挑</strong>：从一个 <span class="mono">Schema.Codec</span> 派生出 encode（存快照）、decode（读快照）、equivalent（判变化）——声明结构，判等自来。</li>
    <li><strong>baseline = 一说一记</strong>：渲染全文给模型 + encode 快照给自己。快照是增量机制的锚。</li>
    <li><strong>compare = 三选一</strong>：Unchanged（沉默省 token）/ Updated（报差异 + 更新快照）/ Incompatible（旧档作废，退回重来）。</li>
    <li>这套「观察→快照→下轮比对」的循环，让每个源都能<strong>独立地、增量地</strong>刷新自己。</li>
  </ul>
  <p>但有个问题还悬着：这些源是<strong>谁攒起来的</strong>？<span class="mono">core/date</span>、<span class="mono">core/environment</span>、还有插件可能贡献的源……它们怎么被收集、汇总成那个传给 <span class="mono">combine</span> 的列表？这就是下一课<strong>注册表（第 23 课）</strong>的活：一个让各路源「报到登记」的地方。源知道怎么刷新自己（本课），注册表知道有哪些源（下一课），两者合起来，系统上下文才真正运转起来。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p><span class="mono">compare</span> 的三分支，在 <span class="mono">make</span> 里就是一段优雅的 <span class="mono">Option.match</span> + 判等：</p>
  <pre class="code"><span class="cm">// 简化自 system-context/index.ts</span>
compare: (previous) =&gt; Option.<span class="fn">match</span>(<span class="fn">decode</span>(previous), {
  onNone: () =&gt; ({ _tag: <span class="st">"Incompatible"</span> }),        <span class="cm">// 解不出旧档</span>
  onSome: (decoded) =&gt;
    <span class="fn">equivalent</span>(decoded, value)
      ? { _tag: <span class="st">"Unchanged"</span> }                       <span class="cm">// 一样 → 沉默</span>
      : { _tag: <span class="st">"Updated"</span>, render: () =&gt; ({       <span class="cm">// 变了 → 渲染差异</span>
          text: source.<span class="fn">update</span>(decoded, value),
          snapshot: <span class="fn">snapshot</span>() }) },
})</pre>
  <p>注意 <span class="mono">decode</span> 返回的是 <span class="mono">Option</span>（用了 <span class="mono">decodeUnknownOption</span>，而不是会抛异常的版本）——解不出来不是「崩」，而是规规矩矩地走 <span class="mono">onNone</span> 分支，变成一个有名有姓的 <span class="mono">Incompatible</span> 结果。这又是第 5、8 课「错误是值、不靠异常」那套世界观的微观体现：连「旧快照读不出来」这种边角情况，都被收进了类型，成了 <span class="mono">Compared</span> 联合里一个明确的分支，而不是一个会半路炸出来的意外。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>codec 一肩三挑</strong>：源只需声明一个 <span class="mono">Schema.Codec</span>，<span class="mono">make</span> 就从它派生出 <strong>encode</strong>（存快照）、<strong>decode</strong>（读快照）、<strong>equivalent</strong>（判等）——声明结构，判等自来，无需手写比较逻辑。</li>
    <li><strong>baseline = 一说一记</strong>：<span class="mono">source.baseline(value)</span> 渲染人类可读全文给模型，<span class="mono">encode(value)</span> 存结构化快照给系统——同一次观察、两种形态。</li>
    <li><strong>快照是增量机制的锚</strong>：没有上轮存的快照，就无从比出「变了没」。</li>
    <li><strong>compare 三选一</strong>：<span class="mono">Unchanged</span>（值没变→沉默省 token）/ <span class="mono">Updated</span>（变了→渲染差异+更新快照）/ <span class="mono">Incompatible</span>（旧快照解不出，schema 变过→退回重 baseline）。</li>
    <li><span class="mono">decode</span> 用 Option（解不出走 onNone→Incompatible），把「旧档读不出」这种边角也收进类型——第 5、8 课「错误即值」的微观延续。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Last lesson we surveyed the panorama of system context — a set of composable "sources" with a twin <span class="mono">baseline</span>/<span class="mono">update</span> rendering. This lesson we zoom the lens onto a <strong>single source</strong> and watch its life: how it <strong>observes</strong> its current value, how it <strong>snapshots</strong> that value as memory, and how it <strong>compares</strong> next round to find "did it change, and what changed," thereby deciding to stay silent, report the diff, or start over. The cleverness of this mechanism all hides in a small field called <span class="mono">codec</span> — which, single-handedly, shoulders the three burdens of "serialize, deserialize, compare." Understand how a single source turns and you've grasped the engine of the whole context-incremental update.</p>
<p>Why spend a lesson hammering on "how one source works"? Because <strong>the devil is all in the details</strong>. "Detect whether a value changed" sounds simple, but get serious and problems pop up: values come in all types (date, directory, string list), how to compare uniformly? The stored old value, what if its format no longer matches (the source's schema changed)? How to distinguish "couldn't read" from "value changed"? opencode doesn't hand-write a comparison for each source but uses one unified <span class="mono">codec</span> to solve these fiddly, error-prone chores <strong>once, type-safely</strong>. This lesson sees how.</p>

<div class="card analogy">
  <div class="tag">📄 Analogy</div>
  Remember last lesson's briefing folder? This lesson we stare at <strong>one of its pages</strong>. This page has a <strong>"format spec"</strong> (codec) — defining how this page's content <strong>gets written down in black and white</strong> (serialize), <strong>how to read an old archived copy of this page</strong> (deserialize), and <strong>how to tell whether two copies say the same thing</strong> (compare). Each time the page needs updating, the briefing officer follows three steps by spec: read out <strong>last time's archive</strong>, compare with <strong>what's newly observed</strong> — <strong>same?</strong> write not a word, save paper (Unchanged); <strong>different?</strong> write a "what changed since last time" note (Updated); <strong>can't even read the old archive?</strong> (say the format spec was upgraded, the old archive void) then don't force a comparison, just rewrite a full one (Incompatible). One "format spec" handles all three — write, read, compare — for this page. That's all of codec's magic.
</div>

<h2>codec: one field, three burdens</h2>
<p>Every <span class="mono">Source&lt;A&gt;</span> must provide a <span class="mono">codec</span> — a <span class="mono">Schema.Codec</span> describing "how value type <span class="mono">A</span> converts to and from JSON." The <span class="mono">make</span> function takes it and <strong>immediately derives three tools from it</strong>:</p>
<pre class="code"><span class="cm">// simplified from make() in system-context/index.ts</span>
<span class="kw">const</span> decode = Schema.<span class="fn">decodeUnknownOption</span>(source.codec)  <span class="cm">// deserialize: old archive → value</span>
<span class="kw">const</span> encode = Schema.<span class="fn">encodeSync</span>(source.codec)          <span class="cm">// serialize: value → storable JSON</span>
<span class="kw">const</span> equivalent = Schema.<span class="fn">toEquivalence</span>(source.codec)    <span class="cm">// compare: are two values the same</span></pre>
<p>This is the design's most elegant stroke. The source author <strong>declares just one thing</strong> — "my value looks like this" (a codec) — and the framework <strong>gives for free</strong> three abilities: <strong>encode</strong> the value into JSON storable in a snapshot, <strong>decode</strong> the stored snapshot back into a value, and <strong>judge</strong> whether two values are equal. Especially that <span class="mono">toEquivalence</span> — it <strong>automatically derives "how to compare two such values"</strong> from "the value's structure description." The source author no longer hand-writes the fiddly, error-prone equality logic of "how to compare dates, how to compare directory structures": <strong>declare the structure, equality comes for free.</strong></p>
<div class="cellgroup">
  <div class="cell"><div class="k">encode</div><div class="v">value → JSON: store in the Snapshot as memory</div></div>
  <div class="cell"><div class="k">decode</div><div class="v">JSON → value: read back last time's snapshot (may fail → Option)</div></div>
  <div class="cell"><div class="k">equivalent</div><div class="v">value × value → bool: auto-derived equality, detect "changed?", no hand-writing</div></div>
</div>
<div class="cols">
  <div class="col"><h4>❌ hand-write equality per source</h4><p>The date source writes "compare Y/M/D," the directory source "compare field by field," the list source "compare item by item"… N sources, N comparison logics, fiddly, repetitive, error-prone (miss a field, miss a change).</p></div>
  <div class="col"><h4>✅ declare a codec, equality comes</h4><p>Each source declares "the value looks like this," <span class="mono">toEquivalence</span> derives equality from structure. N sources share one derivation, zero hand-writing, no missed comparisons.</p></div>
</div>
<p>Don't underrate the weight of "auto-derived equality." In many codebases, "do two objects count as equal" is a bug hotspot: someone forgets a newly-added field, someone mistakes reference equality for value equality, someone misses a layer in a nested structure. These bugs are also especially sneaky — they fire only when "the value actually changed but was misjudged unchanged," showing up as baffling "why doesn't the model know I cd'd." opencode uses <span class="mono">Schema.toEquivalence(codec)</span> to turn equality <strong>from "a human writes it" into "derived from structure,"</strong> uprooting this whole class of bug: as long as your codec faithfully describes the value's structure, equality is automatically correct, never misjudging because "a hand-written comparison missed a stroke." <strong>Making correctness the default rather than relying on everyone's care</strong> — exactly Lesson 8's toolbox "guardrail" philosophy appearing again at the context layer.</p>

<h2>baseline: observe once, leave a memory</h2>
<p>When a source enters the context, it first runs <span class="mono">load</span> to observe the current value. If <span class="mono">load</span> returns <span class="mono">unavailable</span> (covered last lesson: temporarily missing, not removed), it stops there, preserving the old state. If it gets a real value, it produces a <span class="mono">baseline</span> rendering — doing two things: call <span class="mono">source.baseline(value)</span> for <strong>the full text for the model</strong>, and store the result of <span class="mono">encode(value)</span> <strong>into a <span class="mono">SourceSnapshot</span></strong>.</p>
<div class="flow">
  <div class="node">load<span class="sub">observe current value</span></div>
  <div class="arrow">unavailable? → stop</div>
  <div class="node">baseline(value)<span class="sub">render full text</span></div>
  <div class="arrow">+</div>
  <div class="node">encode(value)<span class="sub">store in Snapshot</span></div>
</div>
<p>The pairing of "speak once, remember once" is key: that <span class="mono">baseline</span> full text is <strong>spoken to the model</strong> (entering its context); while that <span class="mono">encode</span>d snapshot is <strong>remembered by the system itself</strong> (stored, for next comparison). What's spoken to the model is human-readable prose ("you're in /home/proj, it's a git repo"); what's remembered is structured JSON (<span class="mono">{"dir":"/home/proj","git":true}</span>). <strong>One observation, rendered into two forms: one for communication, one for memory.</strong> Without that memory, the next round can't know "changed?" — the snapshot is the anchor of the whole incremental mechanism.</p>
<p>Why not just use "the full text for the model" as the memory and compare text next time? Because <strong>human words and machine memory want exactly opposite things</strong>. The prose for the model seeks <strong>readability</strong>, and this version might write "you're in /home/proj" while the next on a whim writes "Current working directory: /home/proj" — the words changed, the fact didn't, and comparing text would falsely report a "change." But the structured snapshot from <span class="mono">encode</span> seeks <strong>precision</strong>: it records only the normalized value (<span class="mono">{"dir":"/home/proj"}</span>), free of any wording. Comparing structure to structure, <span class="mono">equivalent</span> can cleanly answer "did the fact actually change," undisturbed by the jitter of phrasing. <strong>Prose for communication, structure for memory</strong> — separating these two is the root of how this source can both "speak human" and "compare precisely."</p>

<h2>compare: changed? changed what?</h2>
<p>Next round, this source is observed again. This time it holds one more thing: <strong>the snapshot stored last round</strong>. So it runs <span class="mono">compare(previous)</span>, settling things in three steps:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">decode(previous): decode last time's snapshot back to a value. Can't decode? → Incompatible (schema changed, old archive void)</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">decoded → equivalent(old value, new value): same?</span></div>
  <div class="t-row"><span class="t-num">3a</span><span class="t-txt">same → Unchanged: send not a word, save tokens</span></div>
  <div class="t-row"><span class="t-num">3b</span><span class="t-txt">different → Updated: call update(old, new) to render the diff, and store the new snapshot</span></div>
</div>
<p>These three outcomes cover all of a value's possible fates between two rounds. <strong>Unchanged</strong> is the most common and most frugal case — most rounds, the directory didn't change, the date didn't change, so <strong>stay silent</strong>, wasting not one token of the model. <strong>Updated</strong> is the main road when there's a real change — render a "diff" and <strong>update the snapshot in passing</strong> (so the round after can compare against this one). The most subtle is <strong>Incompatible</strong>: it means <strong>even last time's snapshot can't be decoded</strong> — usually because this source's <span class="mono">codec</span> was changed between rounds (say a version upgrade), making the old-format snapshot "gibberish." Forcing a diff then is dangerous, and the wise move is to <strong>abandon the increment and start over</strong> (re-baseline). This branch seems obscure but is a reality any long-evolving system must consider: <strong>data formats change, and the old data you stored won't change with them automatically.</strong></p>
<p>The <span class="mono">Incompatible</span> branch most reveals this design's maturity. An implementation thinking only of "make it work" wouldn't even consider "what if the old snapshot can't be decoded" — it'd assume what's stored always reads back, so one day the codec upgrades, decoding the old snapshot throws, and the loop crashes mid-way. opencode squarely catches this case: can't decode? that's <strong>an expected outcome</strong>, not an accident — just fall back to re-baseline, the model at most gets one extra full text this round, never crashing. <strong>Handling gracefully "the old data I stored is no longer readable by me" is the mark of a system going from 'works' to 'lasts'</strong>: it presumes "I too will change, my past may not recognize my present," and reserves a calm fallback for that self-evolution.</p>
<div class="cols">
  <div class="col"><h4>Unchanged · silent</h4><p>Value didn't change. Send not a token. Most common, most frugal.</p></div>
  <div class="col"><h4>Updated · report the diff</h4><p>Value changed. Render the update diff text, refresh the snapshot.</p></div>
  <div class="col"><h4>Incompatible · start over</h4><p>Old snapshot can't decode (schema changed). Abandon the increment, re-baseline.</p></div>
</div>
<p>String together a source's experience over several consecutive rounds and the mechanism's rhythm becomes clear:</p>
<div class="timeline">
  <div class="tl-item"><span class="tl-time">round 1</span><span class="tl-desc">first inclusion → baseline: send full text "you're in /home/proj, git repo" + store snapshot {dir,git}</span></div>
  <div class="tl-item"><span class="tl-time">round 2</span><span class="tl-desc">compare: decode the old snapshot, equivalent judges same → Unchanged → silent</span></div>
  <div class="tl-item"><span class="tl-time">round 3</span><span class="tl-desc">you cd'd → compare: different → Updated "directory switched to /home/proj/src" + update snapshot</span></div>
  <div class="tl-item"><span class="tl-time">round 4</span><span class="tl-desc">no more moves → compare: against round 3's snapshot → Unchanged → silent again</span></div>
</div>
<p>Look at this timeline and you'll find a source is <strong>silent the vast majority of the time</strong> — only in the round it truly changes does it spend a token to say "I became this." This is the payoff of the baseline/update design cashed out at the micro level: <strong>context isn't re-poured every round but, like a water surface, stays calm in normal times and ripples only when there's a disturbance.</strong> A session chatting for hours sees environment info truly change a countable few times, so what this mechanism saves is the tokens that would have been pointlessly repeated across hundreds of rounds. And each "ripple" references the snapshot left by the previous round — <strong>memory is what makes silence possible.</strong></p>

<div class="card macro">
  <div class="tag">🗺️ The big picture</div>
  <p>This lesson covers a single source's "life" thoroughly — the <strong>micro-engine</strong> of last lesson's algebra:</p>
  <ul>
    <li><strong>codec shoulders three</strong>: from one <span class="mono">Schema.Codec</span> derive encode (store snapshot), decode (read snapshot), equivalent (judge change) — declare the structure, equality comes free.</li>
    <li><strong>baseline = speak once, remember once</strong>: render full text for the model + encode a snapshot for itself. The snapshot is the increment's anchor.</li>
    <li><strong>compare = one of three</strong>: Unchanged (silent, save tokens) / Updated (report diff + update snapshot) / Incompatible (old archive void, start over).</li>
    <li>This loop of "observe → snapshot → compare next round" lets each source <strong>refresh itself independently and incrementally</strong>.</li>
  </ul>
  <p>But one question still hangs: who <strong>gathers</strong> these sources? <span class="mono">core/date</span>, <span class="mono">core/environment</span>, and sources plugins might contribute… how are they collected and gathered into the list passed to <span class="mono">combine</span>? That's the job of next lesson's <strong>registry (Lesson 23)</strong>: a place where all sources "check in and register." A source knows how to refresh itself (this lesson), the registry knows what sources exist (next lesson), and together system context truly runs.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source detail</div>
  <p><span class="mono">compare</span>'s three branches are, in <span class="mono">make</span>, an elegant <span class="mono">Option.match</span> + equality:</p>
  <pre class="code"><span class="cm">// simplified from system-context/index.ts</span>
compare: (previous) =&gt; Option.<span class="fn">match</span>(<span class="fn">decode</span>(previous), {
  onNone: () =&gt; ({ _tag: <span class="st">"Incompatible"</span> }),        <span class="cm">// can't decode old archive</span>
  onSome: (decoded) =&gt;
    <span class="fn">equivalent</span>(decoded, value)
      ? { _tag: <span class="st">"Unchanged"</span> }                       <span class="cm">// same → silent</span>
      : { _tag: <span class="st">"Updated"</span>, render: () =&gt; ({       <span class="cm">// changed → render the diff</span>
          text: source.<span class="fn">update</span>(decoded, value),
          snapshot: <span class="fn">snapshot</span>() }) },
})</pre>
  <p>Note <span class="mono">decode</span> returns an <span class="mono">Option</span> (using <span class="mono">decodeUnknownOption</span>, not the throwing version) — failing to decode isn't a "crash" but dutifully takes the <span class="mono">onNone</span> branch, becoming a named <span class="mono">Incompatible</span> result. This is again Lessons 5 and 8's worldview of "errors are values, not exceptions" at the micro level: even an edge case like "the old snapshot can't be read" is folded into the type, becoming a definite branch of the <span class="mono">Compared</span> union, not an accident that blows up mid-way.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key points</div>
  <ul>
    <li><strong>codec shoulders three</strong>: a source declares just one <span class="mono">Schema.Codec</span>, and <span class="mono">make</span> derives <strong>encode</strong> (store snapshot), <strong>decode</strong> (read snapshot), <strong>equivalent</strong> (judge equality) — declare the structure, equality comes free, no hand-written comparison.</li>
    <li><strong>baseline = speak once, remember once</strong>: <span class="mono">source.baseline(value)</span> renders human-readable full text for the model, <span class="mono">encode(value)</span> stores a structured snapshot for the system — one observation, two forms.</li>
    <li><strong>The snapshot is the increment's anchor</strong>: without the previous round's stored snapshot, there's no way to compare "changed?"</li>
    <li><strong>compare, one of three</strong>: <span class="mono">Unchanged</span> (value unchanged → silent, save tokens) / <span class="mono">Updated</span> (changed → render diff + update snapshot) / <span class="mono">Incompatible</span> (old snapshot won't decode, schema changed → fall back to re-baseline).</li>
    <li><span class="mono">decode</span> uses Option (can't decode → onNone → Incompatible), folding even "old archive unreadable" into the type — Lessons 5, 8's "errors are values" continued at the micro level.</li>
  </ul>
</div>
""",
}
LESSON_23 = {
    "zh": r"""
<p class="lead">前两课，我们把<strong>单个源</strong>讲透了：它懂得观察、比较、渲染自己。但还剩一个朴素却关键的问题没答——<strong>系统里到底有哪些源？谁来把它们攒到一起？</strong><span class="mono">core/date</span>、<span class="mono">core/environment</span>、还有将来插件可能贡献的源……它们散落各处，总得有个地方让它们「报到登记」，再在需要时被统一收齐、一起观察、拼成那个传给 <span class="mono">combine</span> 的完整列表。这就是这一课的主角——<strong>系统上下文注册表（SystemContextRegistry）</strong>。它看着不起眼，却藏着两个极漂亮的设计：<strong>注册是「带生命周期」的</strong>（来去自动），<strong>汇总是「确定有序」的</strong>（结果稳定）。读懂这个小小的注册表，你就看清了 opencode 怎么把一堆来路各异的源，管成一份井井有条的清单。</p>
<p>为什么「攒源」这件事需要一个专门的注册表，而不是写死一个数组？因为源的来源是<strong>动态且分散</strong>的。内置源（环境、日期）由 core 提供，但还有指令上下文、未来插件贡献的源——它们在<strong>不同时机、不同地方</strong>加入。更要命的是，有些源是<strong>有寿命的</strong>：一个插件加载时贡献了它的源，卸载时这个源就该<strong>干净地消失</strong>，绝不能赖在清单上变成幽灵。写死的数组应付不了这种「随用随加、用完即走」的动态。注册表用 Effect 的两件法宝——<strong>作用域（Scope）</strong>和 <strong>Ref</strong>——把这件事办得既灵活又不漏。这一课就拆开它。</p>

<div class="card analogy">
  <div class="tag">📖 生活类比</div>
  把注册表想成一栋办公楼门厅里的<strong>签到簿</strong>。每个部门（一个源）开门营业时，就在簿子上<strong>签到</strong>；打烊时，<strong>自动签退</strong>——没有哪个部门走了还赖在簿子上（这就是「带生命周期的注册」：来去自动，靠的是 Effect 的作用域）。当楼里要出一份<strong>全楼现况报告</strong>时，前台就翻开签到簿，做三件事：先按<strong>部门名的字母顺序</strong>排好（这样每次报告的顺序都一样、可对照）；再<strong>同时</strong>给所有在册部门打电话问「你现在什么情况」（并发观察，谁也不等谁）；最后把各家的回话<strong>汇编成一份报告</strong>。一本会自动签到签退、还总按固定顺序汇编的签到簿——这就是系统上下文注册表。它不生产情报，只负责「<strong>谁在册</strong>」和「<strong>怎么收齐</strong>」。
</div>

<h2>注册表的形状：两个方法</h2>
<p>注册表的接口朴素到极点——一个 <span class="mono">Entry</span>（一条登记）加两个方法：</p>
<div class="cellgroup">
  <div class="cell"><div class="k">Entry</div><div class="v">{ key, load }：一条登记 = 命名空间 key + 怎么观察它</div></div>
  <div class="cell"><div class="k">register(entry)</div><div class="v">把一个源登记进来（作用域绑定，来去自动）</div></div>
  <div class="cell"><div class="k">load()</div><div class="v">收齐当前所有源、并发观察、合并成一个 SystemContext</div></div>
</div>
<p>注意 <span class="mono">Entry</span> 里那个 <span class="mono">load</span> 的类型是 <span class="mono">Effect&lt;SystemContext&gt;</span>——也就是说，登记的不是一个<strong>死的值</strong>，而是一段<strong>「怎么观察出值」的描述</strong>。这点很关键：注册表存的是「<strong>怎么取</strong>」，不是「取到的<strong>什么</strong>」。于是每次 <span class="mono">load()</span> 都会<strong>重新跑一遍</strong>这些观察，拿到的永远是<strong>此刻最新</strong>的环境——而不是注册那一刻的旧快照。把「源」存成「一段可重复执行的观察」，正是它能随时反映最新世界的根。</p>

<h2>register：带生命周期的注册</h2>
<p>注册表内部，其实就是一个 <span class="mono">Ref</span>（一个可变的引用单元）裹着一个<strong>源列表</strong>。源通过 <span class="mono">register(entry)</span> 加入——而这里第一个漂亮设计是：注册用了 <span class="mono">Effect.acquireRelease</span>，是<strong>作用域绑定</strong>的。</p>
<pre class="code"><span class="cm">// 简化自 system-context/registry.ts</span>
register: (entry) =&gt; Effect.<span class="fn">acquireRelease</span>(
  <span class="cm">// 获取：把 entry 加进列表（重名直接 die）</span>
  Ref.<span class="fn">modify</span>(entries, (cur) =&gt; cur.<span class="fn">some</span>(e =&gt; e.key === entry.key)
    ? [<span class="kw">false</span>, cur] : [<span class="kw">true</span>, [...cur, entry]]),
  <span class="cm">// 释放：作用域结束时，把 entry 从列表移除</span>
  (entry) =&gt; Ref.<span class="fn">update</span>(entries, (cur) =&gt; cur.<span class="fn">filter</span>(e =&gt; e !== entry)),
)</pre>
<p><span class="mono">acquireRelease</span> 是 Effect 里「资源安全」的看家招式（第 7 课的远亲）：它把「获取」和「释放」<strong>配成一对</strong>，绑定在一个作用域上——作用域一结束，释放<strong>必然执行</strong>。用在这里，意思就是：一个源 <span class="mono">register</span> 进来，它就在列表里待着；可一旦它所属的那个作用域关闭（比如贡献它的插件被卸载），它<strong>会被自动从列表里摘掉</strong>，干净利落、绝不残留。<strong>注册和注销，被焊成了一枚硬币的两面</strong>——你只管声明「在这个作用域里，加上这个源」，离场清理的活，框架替你包了。这就根除了「忘了注销、源越积越多、最后清单里全是早该消失的幽灵」这类经典内存/状态泄漏。这种「把清理绑死在获取上」的纪律，在长跑的服务里尤其救命：一个 agent 进程可能开开关关无数会话、加加卸卸无数插件，若每一处都靠人记得手动清理，迟早有一处会漏——而漏掉的代价，是状态里悄悄堆积的垃圾，和某天莫名其妙的诡异行为。<span class="mono">acquireRelease</span> 把这份「记得清理」的心智负担，从程序员肩上彻底卸了下来。</p>
<div class="timeline">
  <div class="tl-item"><span class="tl-time">作用域开</span><span class="tl-desc">插件加载 → register 它的源 → 进入 entries 列表</span></div>
  <div class="tl-item"><span class="tl-time">存续期</span><span class="tl-desc">每次 load() 都会观察到它，贡献进上下文</span></div>
  <div class="tl-item"><span class="tl-time">作用域关</span><span class="tl-desc">插件卸载 → release 必然触发 → 自动从 entries 摘除</span></div>
  <div class="tl-item"><span class="tl-time">此后</span><span class="tl-desc">load() 再也观察不到它 —— 无残留、无幽灵</span></div>
</div>
<div class="cols">
  <div class="col"><h4>❌ 手动 register / unregister</h4><p>加的时候记得加，走的时候<strong>得记得删</strong>。一旦某条路径忘了删（异常、提前 return），源就永远赖在清单上，成幽灵。</p></div>
  <div class="col"><h4>✅ 作用域绑定（acquireRelease）</h4><p>注册即声明「在此作用域内存在」。作用域一关，<strong>必然</strong>注销。无需手动清理，无路径能遗漏。</p></div>
</div>
<p>顺带留意那个<strong>重名检查</strong>：往列表里加之前，先看有没有同 <span class="mono">key</span> 的，已经有了就 <span class="mono">die</span>（直接判定为程序错误）。这和第 21 课 <span class="mono">combine</span> 拒绝重复 key 是一脉相承的纪律——<strong>每个源的命名空间 key 必须全局唯一</strong>，因为整个增量机制都靠 key 来认领「这是哪个源的快照」。两个源撞了 key，比较时就会张冠李戴，所以宁可在注册的那一刻就硬性拦下，绝不放它进门。</p>

<h2>load：确定有序地汇总</h2>
<p>当系统需要当前的完整上下文时，调 <span class="mono">load()</span>。它干三件事，每一件都有讲究：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">取出当前所有在册 entry</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">按 key 排序（toSorted）—— 确定的顺序，与注册先后无关</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">并发 load 每个源（concurrency: unbounded），再 combine 成一个</span></div>
</div>
<p>第 2 步那个「<strong>按 key 排序</strong>」，看着随手，实则至关重要。设想不排序：源在列表里的顺序，取决于它们<strong>注册的先后</strong>——而注册先后可能受加载时序、并发等一堆偶然因素影响，今天是这个顺序、明天可能是那个。那么拼出来的 baseline 全文，顺序就会<strong>飘忽不定</strong>。这有两个坏处：一是<strong>不可复现</strong>（同样的环境，两次跑出来的上下文文本不一样，调试时抓狂）；二是<strong>干扰增量</strong>（顺序一变，diff 机制就以为「变了」，白白触发更新）。按 key 排序，等于给汇总钉了一个<strong>确定的顺序</strong>：无论源们以什么乱序注册进来，最终拼出的清单永远<strong>长一个样</strong>。<strong>确定性，是可复现与可比较的前提。</strong></p>
<p>这个「按 key 排序」的小动作，其实触到了一个更深的工程原则：<strong>凡是要被比较、被复现的东西，都不能依赖偶然的顺序</strong>。并发是好东西，但并发的代价就是「完成的先后不确定」——如果让这种不确定性<strong>泄漏</strong>到最终结果的顺序里，那「可复现」「可 diff」这些性质就全毁了。聪明的做法，是<strong>享受并发的快，但在汇总时强行抹掉它带来的顺序随机</strong>——并发去观察，排序来定序，两者井水不犯河水。你会发现这正是注册表设计的精髓：它在同一个 <span class="mono">load</span> 里，<strong>既要了并发的快，又要了确定的稳</strong>，靠的就是把「观察」和「定序」拆成两个互不干扰的步骤。快与稳本不矛盾，前提是你想清楚——哪里该放手让它乱跑，哪里必须钉死。</p>
<p>第 3 步那个「<strong>并发 load</strong>」也值得一提。每个源的 <span class="mono">load</span>（观察当前值）都是<strong>互相独立</strong>的——读目录、读日期、读 git 状态，谁也不依赖谁。所以注册表用 <span class="mono">concurrency: "unbounded"</span> 把它们<strong>一股脑同时发出去</strong>，而不是一个等一个地串行观察。在「都独立、且可能各自有点 IO 延迟」的场景下，并发能把总耗时从「各源耗时之和」压成「最慢那个源的耗时」。观察彼此独立、汇总要求有序——注册表把这两件事各用最合适的手段办了：<strong>观察求快（并发），排序求稳（按 key）。</strong></p>
<div class="cellgroup">
  <div class="cell"><div class="k">① 排序</div><div class="v">toSorted by key：确定顺序，与注册先后无关 → 可复现、不假性 diff</div></div>
  <div class="cell"><div class="k">② 并发观察</div><div class="v">forEach concurrency:unbounded：各源独立、同时发 → 求快</div></div>
  <div class="cell"><div class="k">③ 合并</div><div class="v">combine：归一成一个 SystemContext，并再校验 key 唯一</div></div>
</div>
<p>把这三步合起来看，注册表其实在扮演一个<strong>「指挥与编排者」</strong>的角色，而非「内容生产者」。它自己<strong>不知道、也不关心</strong>任何一个源具体在观察什么——日期也好、git 状态也好，对它都是不透明的 <span class="mono">SystemContext</span>（第 21 课 <span class="mono">make</span> 藏起了类型）。它只负责三件纯粹「编排」的事：谁在册、按什么顺序、怎么并发收齐。这种<strong>「编排与内容彻底分离」</strong>的干净，正是这套设计能无限扩展的根：你写多少种稀奇古怪的源，注册表都<strong>一行不用改</strong>——因为它从头到尾就没碰过源的「内容」，只摆弄源的「名册」。这又一次印证了贯穿全书的那句话：<strong>把会变的（有哪些源）和不变的（怎么收集源）分开，系统就有了无限生长的空间。</strong></p>
<div class="flow">
  <div class="node">各路源<span class="sub">register（作用域绑定）</span></div>
  <div class="arrow">→</div>
  <div class="node">entries（Ref）<span class="sub">当前在册列表</span></div>
  <div class="arrow">load →</div>
  <div class="node">按 key 排序<span class="sub">确定顺序</span></div>
  <div class="arrow">并发 load + combine</div>
  <div class="node">一个 SystemContext<span class="sub">交给 initialize</span></div>
</div>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <p>三课下来，系统上下文的「生产侧」就完整了：</p>
  <ul>
    <li><strong>第 21 课</strong>：源的代数（make/combine，把异类源归一组合）。</li>
    <li><strong>第 22 课</strong>：单个源的一生（codec 派生 encode/decode/equivalent；baseline/compare）。</li>
    <li><strong>第 23 课·本课</strong>：注册表——<strong>带生命周期地</strong>收集源（acquireRelease，来去自动），<strong>确定有序地</strong>汇总（按 key 排序 + 并发 load + combine）。</li>
  </ul>
  <p>到这里，「有哪些源、怎么收齐、怎么各自刷新」都讲清了。但还有个大问题悬而未决：<span class="mono">load()</span> 拼出的这份上下文，<strong>怎么和一个具体的会话绑定、并持久化下来</strong>？那个被反复提到、还接着第 19 课 history.load 裁边线的 <span class="mono">baselineSeq</span>，到底是怎么来的？这就是下一课——<strong>上下文纪元（Context Epoch，第 24 课）</strong>——的核心：把「这一刻的系统上下文」<strong>钉成会话历史里一个带序号的锚点</strong>。生产侧讲完了，接下来看它怎么落进会话、变成持久的一笔。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p><span class="mono">load</span> 的「排序 + 并发 + 合并」三连，在源码里就是紧凑的几行：</p>
  <pre class="code"><span class="cm">// 简化自 system-context/registry.ts</span>
load: () =&gt; Effect.<span class="fn">gen</span>(<span class="kw">function</span>* () {
  <span class="kw">const</span> current = (<span class="kw">yield</span>* Ref.<span class="fn">get</span>(entries))
    .<span class="fn">toSorted</span>((a, b) =&gt; a.key &lt; b.key ? -1 : a.key &gt; b.key ? 1 : 0)  <span class="cm">// ① 按 key 定序</span>
  <span class="kw">return</span> SystemContext.<span class="fn">combine</span>(                                  <span class="cm">// ③ 合并成一个</span>
    <span class="kw">yield</span>* Effect.<span class="fn">forEach</span>(current, (e) =&gt; e.load,
      { concurrency: <span class="st">"unbounded"</span> }))                            <span class="cm">// ② 并发观察</span>
})</pre>
  <p>三行代码，三个决策。<span class="mono">toSorted</span> 用 key 给出<strong>确定顺序</strong>（不是 <span class="mono">sort</span> 原地改，而是返回新数组，不污染 Ref 里的原始登记顺序）；<span class="mono">forEach + concurrency: "unbounded"</span> 让所有源的观察<strong>并发</strong>跑；<span class="mono">combine</span> 把结果<strong>归一</strong>（并再次校验 key 唯一）。「该有序的地方有序、该并发的地方并发」——一个看似简单的「收集」操作，被这三个恰到好处的选择，做成了既快又稳又可复现的样子。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>注册表</strong>解决「系统里有哪些源、谁来攒齐」：内部是一个 <span class="mono">Ref</span> 裹着源列表，对外提供 <span class="mono">register</span> 和 <span class="mono">load</span>。</li>
    <li><strong>register 带生命周期</strong>：用 <span class="mono">Effect.acquireRelease</span> 作用域绑定——注册即声明「在此作用域内存在」，作用域一关<strong>必然自动注销</strong>，根除「忘了删、源变幽灵」的泄漏。重名 key 直接 <span class="mono">die</span>。</li>
    <li><strong>load 确定有序</strong>：① <strong>按 key 排序</strong>（与注册先后无关的确定顺序，保证可复现、不假性触发 diff）；② <strong>并发 load</strong>（各源观察互相独立，<span class="mono">concurrency: unbounded</span> 求快）；③ <strong>combine</strong> 归一。</li>
    <li>设计精髓：<strong>观察求快（并发），排序求稳（按 key）</strong>——各用最合适的手段。</li>
    <li>这一课收尾了系统上下文的「生产侧」；下一课（Context Epoch）讲它怎么<strong>落进会话、持久成带序号的锚点</strong>（baselineSeq）。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">The past two lessons covered a <strong>single source</strong> thoroughly: it knows how to observe, compare, render itself. But one plain yet crucial question remains — <strong>what sources does the system actually have? Who gathers them?</strong> <span class="mono">core/date</span>, <span class="mono">core/environment</span>, and sources plugins may contribute in future… they're scattered, so there must be a place for them to "check in," then be gathered, observed together, and stitched into that complete list passed to <span class="mono">combine</span>. That's this lesson's star — the <strong>system context registry (SystemContextRegistry)</strong>. It looks unremarkable but hides two beautiful designs: <strong>registration is "lifecycle-bound"</strong> (comes and goes automatically), and <strong>gathering is "deterministically ordered"</strong> (a stable result). Understand this little registry and you see how opencode manages a pile of differently-sourced sources into one orderly list.</p>
<p>Why does "gathering sources" need a dedicated registry rather than a hard-coded array? Because sources come from <strong>dynamic and scattered</strong> origins. Built-in sources (environment, date) come from core, but there's also instruction context, sources future plugins contribute — they join at <strong>different times, different places</strong>. Worse, some sources have a <strong>lifespan</strong>: a plugin contributes its source on load, and on unload that source should <strong>cleanly vanish</strong>, never lingering on the list as a ghost. A hard-coded array can't handle this "add on demand, leave when done" dynamism. The registry uses Effect's two treasures — <strong>Scope</strong> and <strong>Ref</strong> — to do this flexibly and leak-free. This lesson unpacks it.</p>

<div class="card analogy">
  <div class="tag">📖 Analogy</div>
  Think of the registry as a <strong>sign-in book</strong> in an office building's lobby. Each department (a source) <strong>signs in</strong> when it opens for business; <strong>signs out automatically</strong> when it closes — no department lingers on the book after leaving (this is "lifecycle-bound registration": comes and goes automatically, via Effect's scope). When the building needs a <strong>whole-building status report</strong>, the front desk opens the book and does three things: first sort by <strong>department name alphabetically</strong> (so every report's order is the same, comparable); then <strong>simultaneously</strong> call all listed departments asking "what's your situation now" (concurrent observation, no one waits); finally <strong>compile</strong> everyone's replies into one report. A sign-in book that auto-signs-in/out and always compiles in a fixed order — that's the system context registry. It produces no intel, only handles "<strong>who's listed</strong>" and "<strong>how to gather</strong>."
</div>

<h2>The registry's shape: two methods</h2>
<p>The registry's interface is plain to the extreme — one <span class="mono">Entry</span> plus two methods:</p>
<div class="cellgroup">
  <div class="cell"><div class="k">Entry</div><div class="v">{ key, load }: a listing = namespaced key + how to observe it</div></div>
  <div class="cell"><div class="k">register(entry)</div><div class="v">list a source (scope-bound, comes and goes automatically)</div></div>
  <div class="cell"><div class="k">load()</div><div class="v">gather all current sources, observe concurrently, combine into one SystemContext</div></div>
</div>
<p>Note that <span class="mono">Entry</span>'s <span class="mono">load</span> has type <span class="mono">Effect&lt;SystemContext&gt;</span> — meaning what's listed isn't a <strong>dead value</strong> but a <strong>description of "how to observe the value."</strong> This is key: the registry stores "<strong>how to fetch</strong>," not "<strong>what</strong> was fetched." So each <span class="mono">load()</span> <strong>reruns</strong> these observations, always getting <strong>the latest now</strong> — not a stale snapshot from registration time. Storing a "source" as "a repeatable observation" is the root of how it can reflect the latest world at any time.</p>

<h2>register: lifecycle-bound registration</h2>
<p>Inside, the registry is just a <span class="mono">Ref</span> (a mutable reference cell) wrapping a <strong>source list</strong>. Sources join via <span class="mono">register(entry)</span> — and the first beautiful design here is: registration uses <span class="mono">Effect.acquireRelease</span>, it's <strong>scope-bound</strong>.</p>
<pre class="code"><span class="cm">// simplified from system-context/registry.ts</span>
register: (entry) =&gt; Effect.<span class="fn">acquireRelease</span>(
  <span class="cm">// acquire: add entry to the list (duplicate key → die)</span>
  Ref.<span class="fn">modify</span>(entries, (cur) =&gt; cur.<span class="fn">some</span>(e =&gt; e.key === entry.key)
    ? [<span class="kw">false</span>, cur] : [<span class="kw">true</span>, [...cur, entry]]),
  <span class="cm">// release: on scope close, remove entry from the list</span>
  (entry) =&gt; Ref.<span class="fn">update</span>(entries, (cur) =&gt; cur.<span class="fn">filter</span>(e =&gt; e !== entry)),
)</pre>
<p><span class="mono">acquireRelease</span> is Effect's signature move for "resource safety" (a relative of Lesson 7): it <strong>pairs</strong> "acquire" and "release," bound to a scope — when the scope ends, release <strong>necessarily runs</strong>. Used here, it means: a source <span class="mono">register</span>s and stays on the list; but once its owning scope closes (say the plugin contributing it is unloaded), it's <strong>automatically removed from the list</strong>, cleanly, with no residue. <strong>Registration and deregistration are welded into two sides of one coin</strong> — you just declare "in this scope, add this source," and the framework handles the exit cleanup. This uproots the classic memory/state leak of "forgot to deregister, sources pile up, the list fills with ghosts that should've vanished long ago." This discipline of "welding cleanup to acquisition" is especially lifesaving in long-running services: an agent process may open and close countless sessions, load and unload countless plugins, and if every spot relied on a human to remember manual cleanup, sooner or later one would leak — and the cost of a leak is garbage quietly piling in state, and one day inexplicable weird behavior. <span class="mono">acquireRelease</span> lifts this "remember to clean up" mental burden entirely off the programmer's shoulders.</p>
<div class="timeline">
  <div class="tl-item"><span class="tl-time">scope opens</span><span class="tl-desc">plugin loads → register its source → enters the entries list</span></div>
  <div class="tl-item"><span class="tl-time">lifetime</span><span class="tl-desc">every load() observes it, contributing to the context</span></div>
  <div class="tl-item"><span class="tl-time">scope closes</span><span class="tl-desc">plugin unloads → release necessarily fires → auto-removed from entries</span></div>
  <div class="tl-item"><span class="tl-time">thereafter</span><span class="tl-desc">load() never observes it again — no residue, no ghost</span></div>
</div>
<div class="cols">
  <div class="col"><h4>❌ manual register / unregister</h4><p>Remember to add on the way in, <strong>remember to remove</strong> on the way out. Forget to remove on one path (exception, early return) and the source lingers on the list forever, a ghost.</p></div>
  <div class="col"><h4>✅ scope-bound (acquireRelease)</h4><p>Registration declares "exists within this scope." Scope closes, deregistration <strong>necessarily</strong> happens. No manual cleanup, no path can miss it.</p></div>
</div>
<p>Note also the <strong>duplicate-key check</strong>: before adding to the list, check for an existing same <span class="mono">key</span>, and if present, <span class="mono">die</span> (deemed a program error outright). This is the same discipline as Lesson 21's <span class="mono">combine</span> rejecting duplicate keys — <strong>each source's namespaced key must be globally unique</strong>, because the whole incremental mechanism relies on keys to claim "this is which source's snapshot." Two sources colliding on a key would mix up snapshots during comparison, so better to hard-stop at registration time, never letting it in the door.</p>

<h2>load: gathering deterministically ordered</h2>
<p>When the system needs the current full context, it calls <span class="mono">load()</span>. It does three things, each with care:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">fetch all currently-listed entries</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">sort by key (toSorted) — a deterministic order, independent of registration order</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">concurrently load each source (concurrency: unbounded), then combine into one</span></div>
</div>
<p>Step 2's "<strong>sort by key</strong>" looks casual but is crucial. Imagine not sorting: a source's order in the list depends on its <strong>registration order</strong> — which can be affected by load timing, concurrency, and a heap of incidental factors, this order today, that order tomorrow. Then the stitched baseline full text's order would <strong>waver</strong>. Two harms: one, <strong>not reproducible</strong> (same environment, two runs produce different context text, maddening to debug); two, <strong>disrupts the increment</strong> (order changes, the diff mechanism thinks "it changed," pointlessly triggering an update). Sorting by key nails a <strong>deterministic order</strong> on the gathering: however out-of-order the sources register, the final stitched list always <strong>looks the same</strong>. <strong>Determinism is the prerequisite for reproducibility and comparability.</strong></p>
<p>This little "sort by key" act actually touches a deeper engineering principle: <strong>anything to be compared or reproduced must not depend on incidental order</strong>. Concurrency is good, but its cost is "uncertain order of completion" — and if you let that uncertainty <strong>leak</strong> into the final result's order, properties like "reproducible" and "diffable" are destroyed. The smart move is to <strong>enjoy concurrency's speed but forcibly erase its order randomness when gathering</strong> — observe concurrently, sort to order, the two minding their own business. You'll find this is the registry design's essence: in one <span class="mono">load</span>, it <strong>wants both concurrency's speed and determinism's stability</strong>, by splitting "observe" and "order" into two non-interfering steps. Speed and stability aren't inherently at odds, provided you've thought it through — where to let it run loose, where to nail it down.</p>
<p>Step 3's "<strong>concurrent load</strong>" is worth noting too. Each source's <span class="mono">load</span> (observing the current value) is <strong>mutually independent</strong> — reading the directory, the date, git status, none depends on another. So the registry uses <span class="mono">concurrency: "unbounded"</span> to fire them all <strong>at once</strong>, rather than observing serially one waiting for another. In a scenario of "all independent, each possibly with some IO latency," concurrency compresses total time from "the sum of all sources' times" to "the slowest source's time." Observation mutually independent, gathering requiring order — the registry handles each with the fittest means: <strong>observe for speed (concurrent), order for stability (by key).</strong></p>
<div class="cellgroup">
  <div class="cell"><div class="k">① sort</div><div class="v">toSorted by key: deterministic order, independent of registration order → reproducible, no false diff</div></div>
  <div class="cell"><div class="k">② observe concurrently</div><div class="v">forEach concurrency:unbounded: sources independent, fired at once → for speed</div></div>
  <div class="cell"><div class="k">③ combine</div><div class="v">combine: unify into one SystemContext, re-checking key uniqueness</div></div>
</div>
<p>Put the three steps together and the registry is really playing a <strong>"conductor and orchestrator"</strong>, not a "content producer." It <strong>doesn't know or care</strong> what any source observes — date or git status, to it they're all opaque <span class="mono">SystemContext</span> (Lesson 21's <span class="mono">make</span> hid the type). It only handles three purely "orchestration" things: who's listed, in what order, how to gather concurrently. This cleanness of <strong>"orchestration fully separated from content"</strong> is the root of this design's infinite extensibility: however many strange sources you write, the registry <strong>needs not one line changed</strong> — because it never touched a source's "content" from start to finish, only juggled the source "roster." This proves again the line running through the book: <strong>separate the variable (what sources exist) from the invariant (how to gather sources), and the system has room to grow without limit.</strong></p>
<div class="flow">
  <div class="node">various sources<span class="sub">register (scope-bound)</span></div>
  <div class="arrow">→</div>
  <div class="node">entries (Ref)<span class="sub">current listed list</span></div>
  <div class="arrow">load →</div>
  <div class="node">sort by key<span class="sub">deterministic order</span></div>
  <div class="arrow">concurrent load + combine</div>
  <div class="node">one SystemContext<span class="sub">handed to initialize</span></div>
</div>

<div class="card macro">
  <div class="tag">🗺️ The big picture</div>
  <p>Three lessons in, system context's "production side" is complete:</p>
  <ul>
    <li><strong>Lesson 21</strong>: the source algebra (make/combine, unifying and composing heterogeneous sources).</li>
    <li><strong>Lesson 22</strong>: a single source's life (codec derives encode/decode/equivalent; baseline/compare).</li>
    <li><strong>Lesson 23 · this one</strong>: the registry — <strong>lifecycle-bound</strong> source collection (acquireRelease, comes and goes automatically), <strong>deterministically ordered</strong> gathering (sort by key + concurrent load + combine).</li>
  </ul>
  <p>By here, "what sources exist, how to gather, how each refreshes" is clear. But a big question hangs: this context that <span class="mono">load()</span> stitches — <strong>how is it bound to a concrete session and persisted</strong>? That repeatedly-mentioned <span class="mono">baselineSeq</span>, connecting to Lesson 19's history.load edge-trim, where does it come from? That's the core of next lesson — the <strong>Context Epoch (Lesson 24)</strong>: nailing "this moment's system context" into <strong>a numbered anchor in the session history</strong>. The production side covered, next we see how it lands in the session and becomes a persistent record.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source detail</div>
  <p><span class="mono">load</span>'s "sort + concurrent + combine" trio is, in source, a compact few lines:</p>
  <pre class="code"><span class="cm">// simplified from system-context/registry.ts</span>
load: () =&gt; Effect.<span class="fn">gen</span>(<span class="kw">function</span>* () {
  <span class="kw">const</span> current = (<span class="kw">yield</span>* Ref.<span class="fn">get</span>(entries))
    .<span class="fn">toSorted</span>((a, b) =&gt; a.key &lt; b.key ? -1 : a.key &gt; b.key ? 1 : 0)  <span class="cm">// (1) order by key</span>
  <span class="kw">return</span> SystemContext.<span class="fn">combine</span>(                                  <span class="cm">// (3) combine into one</span>
    <span class="kw">yield</span>* Effect.<span class="fn">forEach</span>(current, (e) =&gt; e.load,
      { concurrency: <span class="st">"unbounded"</span> }))                            <span class="cm">// (2) observe concurrently</span>
})</pre>
  <p>Three lines, three decisions. <span class="mono">toSorted</span> gives a <strong>deterministic order</strong> by key (not in-place <span class="mono">sort</span> but returning a new array, not polluting the Ref's original registration order); <span class="mono">forEach + concurrency: "unbounded"</span> runs all sources' observation <strong>concurrently</strong>; <span class="mono">combine</span> <strong>unifies</strong> the results (and re-checks key uniqueness). "Ordered where it should be ordered, concurrent where it should be concurrent" — a seemingly simple "gather" operation, made fast, stable, and reproducible by these three just-right choices.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key points</div>
  <ul>
    <li><strong>The registry</strong> solves "what sources exist, who gathers them": inside is a <span class="mono">Ref</span> wrapping a source list, exposing <span class="mono">register</span> and <span class="mono">load</span>.</li>
    <li><strong>register is lifecycle-bound</strong>: via <span class="mono">Effect.acquireRelease</span> scope-binding — registration declares "exists within this scope," scope closes and deregistration <strong>necessarily happens automatically</strong>, uprooting the "forgot to remove, sources become ghosts" leak. A duplicate key outright <span class="mono">die</span>s.</li>
    <li><strong>load is deterministically ordered</strong>: (1) <strong>sort by key</strong> (a deterministic order independent of registration order, ensuring reproducibility, no false diff); (2) <strong>concurrent load</strong> (sources observe independently, <span class="mono">concurrency: unbounded</span> for speed); (3) <strong>combine</strong> unifies.</li>
    <li>Design essence: <strong>observe for speed (concurrent), order for stability (by key)</strong> — each by the fittest means.</li>
    <li>This lesson wraps up system context's "production side"; next lesson (Context Epoch) covers how it <strong>lands in the session, persisted as a numbered anchor</strong> (baselineSeq).</li>
  </ul>
</div>
""",
}
LESSON_24 = {
    "zh": r"""
<p class="lead">前三课，我们把系统上下文的「生产侧」讲全了：源怎么观察自己、怎么增量比较、怎么被注册表收齐。但这些都还停在<strong>「半空中」</strong>——它们产出的那份上下文，<strong>怎么落到一个具体的会话里、并被持久地记下来</strong>？这一课就回答它，而答案，正是第五部分的同名概念——<strong>上下文纪元（Context Epoch）</strong>。它把「此刻这个会话的系统上下文」<strong>钉成一个带序号的锚点</strong>，存进数据库。而那个序号 <span class="mono">baselineSeq</span>，你应该还记得——正是第 19 课 <span class="mono">history.load</span> 用来给历史窗口<strong>裁边</strong>的那条线！读懂这一课，第 19 课那个悬而未决的伏笔，和整个第五部分，就一齐合上了环。</p>
<p>为什么叫「纪元（epoch）」？这个词用得极准。纪元，是一个<strong>时间的基准点</strong>——就像公元纪年从某一刻起算。系统上下文也是如此：在会话历史的<strong>某个序号点</strong>，确立一份完整的「基线（baseline）」；此后环境的每一点变化，都只是<strong>相对这个基线的增量更新</strong>；直到某个重大事件（比如换了 agent），才需要<strong>开启一个全新的纪元</strong>、重立基线。「确立基线 → 增量更新 → 必要时重立」——这套节律，就是「纪元」二字的全部含义。换句话说，纪元让上下文有了「分期」：每一期都有自己的起点和演进，期与期之间则是一次干净的改朝换代。这一课，我们看它怎么把抽象的源，钉进一个具体会话的时间线里。</p>

<div class="card analogy">
  <div class="tag">🏕️ 生活类比</div>
  把上下文纪元想成登山时建立的<strong>大本营</strong>。出发前，你在某个明确的位置扎下大本营（确立 baseline），并<strong>记下它的坐标</strong>（baselineSeq——「本营建于此处」）。此后一路向上，你<strong>不再每次都从头描述整座山</strong>，只记「相对大本营，我又往上爬了多少」（增量更新）。这个大本营的坐标至关重要：它是<strong>「基线到此为止、往后都是新路程」的分界</strong>——回看记录时，坐标之前的一切被「在大本营」这一句概括，坐标之后才是你真正的攀爬轨迹（这正是第 19 课 history.load 拿 baselineSeq 裁边的道理）。而如果你<strong>换了一支完全不同的队伍</strong>（换 agent），旧大本营的坐标和补给可能就不适用了——这时要么平稳交接、要么<strong>另立新营</strong>（新纪元）。一座标好坐标、可增量、必要时重立的大本营——这就是上下文纪元。
</div>

<h2>纪元是什么：会话里一份带序号的基线</h2>
<p>上下文纪元，是<strong>每个会话一行</strong>的持久记录（<span class="mono">session_context_epoch</span> 表）。它存着「这个会话当前的系统上下文」的全部要件：</p>
<div class="cellgroup">
  <div class="cell"><div class="k">baseline</div><div class="v">给模型看的基线全文（所有源 baseline 拼成）</div></div>
  <div class="cell"><div class="k">baseline_seq</div><div class="v">★ 基线锚定的序号——history.load 据此裁边（第 19 课）</div></div>
  <div class="cell"><div class="k">snapshot</div><div class="v">所有源当前值的结构化快照（用于下次比较）</div></div>
  <div class="cell"><div class="k">revision</div><div class="v">改过几次——乐观并发的版本号</div></div>
  <div class="cell"><div class="k">agent</div><div class="v">这份基线属于哪个 agent（换 agent 会触发重立）</div></div>
</div>
<p>把这几个字段连起来读，纪元的全貌就清楚了：它是一张「<strong>快照 + 锚点</strong>」——<span class="mono">baseline</span> 是<strong>说给模型的</strong>那份基线全文，<span class="mono">snapshot</span> 是<strong>记给系统的</strong>那份结构化记忆（这正是第 22 课「一说一记」在会话层的落地），<span class="mono">baseline_seq</span> 则是把这份基线<strong>钉在会话时间线某一点</strong>的图钉。最妙的是这枚图钉：它一头连着系统上下文（基线从这里开始），一头连着第 19 课的历史窗口（<span class="mono">history.load</span> 只读这个序号之后的对话）。<strong>纪元，就是系统上下文和会话历史交汇、咬合的那个点。</strong></p>
<p>注意那个 <span class="mono">revision</span> 字段，它不起眼却很关键：它是一个<strong>乐观并发的版本号</strong>。源码里 <span class="mono">prepare</span> 外面套着一层 <span class="mono">retryRevisionMismatch</span>——意思是，如果两处几乎同时想更新同一个会话的纪元，它们会比对 revision，发现「我读到的版本，已经被别人改过了」，于是<strong>退让、重试</strong>，而非盲目覆盖、造成丢更新。这又是第 16 课那套「同会话串行」之外的另一道并发防线：纪元的更新用版本号守住，确保两个并发的 prepare 不会把彼此的修改踩没。一个小小的 <span class="mono">revision</span> 整数，背后是「绝不悄悄丢失一次上下文更新」的承诺。</p>
<div class="timeline">
  <div class="tl-item"><span class="tl-time">…seq &lt; baselineSeq</span><span class="tl-desc">被基线全文概括——history.load 不再逐条读</span></div>
  <div class="tl-item"><span class="tl-time">baselineSeq（锚点）</span><span class="tl-desc">★ 基线在此确立：「往前是底色，往后是对话」</span></div>
  <div class="tl-item"><span class="tl-time">seq &gt; baselineSeq</span><span class="tl-desc">真正的对话历史——history.load 逐条读、喂给模型</span></div>
</div>

<h2>prepare：每次运行前，对一次表</h2>
<p>纪元不是建一次就不管了。每次会话要运行（第 17 课循环启动）前，都会调一次 <span class="mono">SessionContextEpoch.prepare</span>——它做的事，本质是「<strong>拿此刻观察到的环境，和存着的那份基线对一次表</strong>」。这个「每次运行前对表」的节奏，和第 17 课「每轮重读投影历史」是<strong>同一种心跳</strong>：都不信任内存里攒着的旧状态，每到关口就回持久层、拿最新的真相重新校准一遍。逻辑分几种情况：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">首次</span><span class="t-txt">没有存档 → initialize：观察全部源、拼出基线、insert，拿到 baselineSeq，revision=0</span></div>
  <div class="t-row"><span class="t-num">同 agent</span><span class="t-txt">有存档、agent 没变 → reconcile：和 snapshot 比对</span></div>
  <div class="t-row"><span class="t-num">→ Unchanged</span><span class="t-txt">环境没变 → 沿用旧 baseline/baselineSeq，啥也不发</span></div>
  <div class="t-row"><span class="t-num">→ Updated</span><span class="t-txt">环境变了 → publish 一个 ContextUpdated 事件（带差异文本）、revision+1</span></div>
  <div class="t-row"><span class="t-num">换 agent</span><span class="t-txt">agent 变了 → replace：尝试重立纪元（可能被 block，第 27 课）</span></div>
</div>
<p>这套「对表」逻辑，把前几课的零件全用上了。<strong>首次</strong>，就是第 21~23 课那条「注册表 load → combine → initialize → Generation」的链路落地成一行数据库记录。<strong>同 agent 的 reconcile</strong>，正是第 22 课那个 compare 的会话级版本：环境没变就<strong>沉默</strong>（Unchanged，沿用旧基线，连 baselineSeq 都不动）；变了就走 <strong>Updated</strong>——但注意它这里不是简单改个字段，而是 <strong>publish 一个 <span class="mono">ContextUpdated</span> 事件</strong>！这个细节极重要：上下文的变化，被当成<strong>会话历史里一条正式的事件</strong>记下来（还记得第 14、15 课「一切皆事件、只追加」吗？）——于是模型在下一轮重读历史时，自然就读到「哦，目录变了」这条更新，无缝衔接。<strong>系统上下文的演进，本身也是事件溯源的一部分。</strong></p>
<div class="cols">
  <div class="col"><h4>reconcile · 同 agent，算增量</h4><p>agent 没变。拿当前环境和存档 snapshot 比，算出「变了什么」。常态运转走这条：沉默或发增量。</p></div>
  <div class="col"><h4>replace · 换 agent，重立纪元</h4><p>agent 变了。旧基线可能不再适用，尝试整体替换成新纪元——而这一步可能被拦下（第 27 课）。</p></div>
</div>
<p>为什么「换 agent」要走完全不同的 <span class="mono">replace</span> 路径，而不是当成一次普通的「变了」？因为 agent 不是环境里的一个普通字段，它<strong>决定了整份上下文的「人设」和规矩</strong>。同一个目录、同一个时间，换一个 agent 来看，该强调的、该带的指令可能<strong>面目全非</strong>。这种变化太根本，不是「在旧基线上补一句增量」能表达的——它需要的是<strong>掀掉旧基线、重立一份</strong>，就像登山换了支队伍、得另立大本营，而非在旧营地上贴张便条。把「同 agent 的演进」和「换 agent 的改朝换代」分成 reconcile 与 replace 两条路，正是纪元设计对「变化有大小之分」的清醒：小变化增量补，大变化整个重来。</p>
<div class="cellgroup">
  <div class="cell"><div class="k">Unchanged</div><div class="v">环境没变 → 沿用旧基线，啥也不发</div></div>
  <div class="cell"><div class="k">Updated</div><div class="v">环境变了 → 发 ContextUpdated 事件 + revision+1</div></div>
  <div class="cell"><div class="k">ReplacementReady</div><div class="v">换 agent 且可替换 → 重立纪元，revision+1</div></div>
  <div class="cell"><div class="k">ReplacementBlocked</div><div class="v">换 agent 但被拦 → AgentReplacementBlocked（第 27 课）</div></div>
</div>

<h2>baselineSeq：合上第 19 课的环</h2>
<p>现在可以正式合上那个悬了五课的伏笔了。第 19 课讲 <span class="mono">history.load</span> 时，它并发取的两条裁边线之一，就是 <strong>context epoch 的 <span class="mono">baseline_seq</span></strong>。当时我们说「这条线界定历史窗口」，却没说它从哪来。现在答案揭晓：<strong>它就是这一课的纪元，在确立基线时钉下的那个序号。</strong>一个跨越五课才被填上的伏笔，落点竟是如此朴素的一个整数——但正是这个整数，让前面看似各自为政的两套机制，严丝合缝地对接了起来。</p>
<div class="flow">
  <div class="node">源（L21-23）<span class="sub">observe + combine</span></div>
  <div class="arrow">initialize →</div>
  <div class="node">Generation<span class="sub">baseline + snapshot</span></div>
  <div class="arrow">insert →</div>
  <div class="node">纪元（持久）<span class="sub">钉下 baselineSeq</span></div>
  <div class="arrow">history.load 读 →</div>
  <div class="node">裁出历史窗口<span class="sub">第 19 课</span></div>
</div>
<p>把这条链看一遍，整个第四、五部分就<strong>咬合成了一个闭环</strong>：系统上下文（L21-23）被观察、拼成基线 → 确立为一个纪元、钉下 baselineSeq（本课）→ 这个 baselineSeq 反过来告诉 history.load「历史从哪读起」（L19）→ 读出的历史窗口，连同基线，一起喂给 agent 循环（L17）→ 循环跑出新消息、新事件 → 下一轮 prepare 又来对表…… 系统上下文不是孤立地挂在一边，而是<strong>深深织进了会话的时间线和事件流里</strong>。<span class="mono">baselineSeq</span> 这枚小小的图钉，就是把「上下文系统」和「会话引擎」缝在一起的那一针。</p>
<p>退一步看这个闭环，你会对这套架构的「整体性」有更深的体会。一个不那么用心的设计，很可能会把「系统上下文」做成一个<strong>独立的小模块</strong>：每轮临时拼一段环境信息、塞到 prompt 最前面，完事。这样也能跑，但它和会话历史是<strong>两张皮</strong>——上下文的变化无迹可循，历史窗口的边界全靠猜。opencode 偏不：它让上下文的基线<strong>钉进会话的同一条序号时间线</strong>，让上下文的更新<strong>变成会话的同一种事件</strong>，于是「上下文」和「对话」共享同一套持久化、同一套事件流、同一条裁边线。<strong>不是两个系统勉强对接，而是一个系统的两个侧面。</strong>这种「万物归于同一条事件时间线」的整体感，是读懂 opencode 设计品味的关键一课——而上下文纪元，正是这种品味最集中的体现。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <p>这一课是第五部分的<strong>枢纽</strong>，把抽象的源，钉进了具体会话的时间线：</p>
  <ul>
    <li><strong>纪元 = 快照 + 锚点</strong>：<span class="mono">session_context_epoch</span> 表存 baseline（说给模型）、snapshot（记给系统）、<strong>baseline_seq（钉在时间线的图钉）</strong>、revision、agent。</li>
    <li><strong>prepare 每次运行前对表</strong>：首次 initialize；同 agent 走 reconcile（Unchanged 沉默 / Updated <strong>发 ContextUpdated 事件</strong>+revision+1）；换 agent 走 replace（第 27 课）。</li>
    <li><strong>上下文的变化也是事件</strong>：Updated 不是改字段，而是 publish 一条 ContextUpdated——系统上下文的演进，是事件溯源的一部分。</li>
    <li><strong>baselineSeq 合上第 19 课</strong>：纪元钉下的序号，正是 history.load 裁历史窗口那条线——上下文系统与会话引擎，由此缝合。</li>
  </ul>
  <p>但有两件事这一课只点了名、没展开：其一，「环境变了，发一条 <span class="mono">ContextUpdated</span> 更新事件」——这条更新，模型在对话<strong>中途</strong>到底是以什么形式读到的？那是<strong>第 25 课（会话中系统消息）</strong>。其二，「换了 agent，纪元要重立、还可能被 block」——这个 <span class="mono">AgentReplacementBlocked</span> 到底是怎么回事、为什么要 block？那是<strong>第 27 课（Agent 切换与 Epoch 替换）</strong>。纪元的「常态运转」讲完了，剩下两课讲它的「两种特殊时刻」：中途更新，与改朝换代。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p><span class="mono">prepareOnce</span> 里「环境变了」那一支，最能体现「上下文变化即事件」：</p>
  <pre class="code"><span class="cm">// 简化自 session/context-epoch.ts 的 prepareOnce</span>
<span class="kw">const</span> result = <span class="kw">yield</span>* SystemContext.<span class="fn">reconcile</span>(value, snapshot)  <span class="cm">// 对表</span>
<span class="cm">// …Unchanged / ReplacementReady 等分支略…</span>
<span class="cm">// 环境确有更新 → 把它作为一条会话事件发布出去：</span>
<span class="kw">yield</span>* events.<span class="fn">publish</span>(
  SessionEvent.ContextUpdated,
  { sessionID, messageID: ..., timestamp: ..., text: result.text },  <span class="cm">// ← 差异文本</span>
  { commit: () =&gt; <span class="fn">advance</span>(db, sessionID, stored.revision, result.snapshot) })  <span class="cm">// 推进 revision + 存新快照</span></pre>
  <p>读这段：<span class="mono">reconcile</span> 算出「变了什么」（<span class="mono">result.text</span> 就是第 22 课那个 update 差异文本），然后 <span class="mono">publish(SessionEvent.ContextUpdated, …)</span> 把它发成一条事件。注意那个 <span class="mono">commit</span> 回调——它和事件发布<strong>绑成一笔原子操作</strong>：事件落库的同时，<span class="mono">advance</span> 才推进 revision、存下新快照。「发更新事件」和「推进纪元状态」要么一起成、要么一起不成，绝不会出现「事件发了、快照没更新」的撕裂。<strong>连上下文更新这一步，都恪守着第 15 课那套「先持久、再推进」的事件溯源纪律。</strong></p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>上下文纪元</strong>把抽象的源，钉成一个会话里<strong>带序号的基线</strong>：<span class="mono">session_context_epoch</span> 表存 baseline、snapshot、<strong>baseline_seq</strong>、revision、agent。</li>
    <li><strong>「纪元」之名</strong>：在某序号点确立基线 → 此后只发增量 → 重大事件（换 agent）才重立新纪元。</li>
    <li><strong>prepare 每次运行前对表</strong>：首次 initialize；同 agent reconcile（Unchanged 沉默 / Updated 发 <span class="mono">ContextUpdated</span> 事件+revision+1）；换 agent replace。</li>
    <li><strong>上下文变化也走事件溯源</strong>：Updated 是 publish 一条 ContextUpdated（而非改字段），且与推进 revision 绑成原子的 commit——「先持久、再推进」（第 15 课）。</li>
    <li><strong>baselineSeq 合上第 19 课的环</strong>：纪元钉下的序号，正是 <span class="mono">history.load</span> 给历史窗口裁边那条线——上下文系统与会话引擎由此缝成一体。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">The past three lessons covered system context's "production side" fully: how a source observes itself, compares incrementally, gets gathered by the registry. But these all hung <strong>"in mid-air"</strong> — the context they produce, <strong>how does it land in a concrete session and get persistently recorded</strong>? This lesson answers that, and the answer is Part 5's namesake concept — the <strong>Context Epoch</strong>. It nails "this moment's system context for this session" into <strong>a numbered anchor</strong>, stored in the database. And that number, <span class="mono">baselineSeq</span>, you should recall — is exactly the line Lesson 19's <span class="mono">history.load</span> used to <strong>edge-trim</strong> the history window! Understand this lesson and Lesson 19's hanging hook, and all of Part 5, close the loop at once.</p>
<p>Why "epoch"? The word is precisely chosen. An epoch is a <strong>reference point in time</strong> — like a calendar era counting from a certain moment. System context is the same: at <strong>some sequence point</strong> in the session history, a complete "baseline" is established; thereafter every change in the environment is just an <strong>incremental update relative to this baseline</strong>; until a major event (say an agent switch) requires <strong>opening a wholly new epoch</strong>, re-establishing the baseline. "Establish the baseline → incremental updates → re-establish when needed" — this rhythm is all "epoch" means. In other words, the epoch gives context "periods": each has its own start and evolution, and between periods is a clean changing of the guard. This lesson sees how it nails abstract sources into a concrete session's timeline.</p>

<div class="card analogy">
  <div class="tag">🏕️ Analogy</div>
  Think of the context epoch as a <strong>base camp</strong> established when mountaineering. Before setting off, you pitch base camp at a definite location (establish the baseline) and <strong>record its coordinates</strong> (baselineSeq — "base camp pitched here"). Climbing on, you <strong>no longer describe the whole mountain each time</strong>, just note "relative to base camp, I climbed this much higher" (incremental updates). This base camp's coordinates are crucial: they're the <strong>boundary of "baseline ends here, beyond is new journey"</strong> — reviewing the record, everything before the coordinates is summarized by "at base camp," only beyond is your real climbing track (exactly the logic of Lesson 19's history.load edge-trimming by baselineSeq). And if you <strong>switch to a wholly different team</strong> (switch agent), the old base camp's coordinates and supplies may no longer apply — then either hand off smoothly or <strong>pitch a new camp</strong> (new epoch). A base camp with marked coordinates, incrementable, re-pitched when needed — that's the context epoch.
</div>

<h2>What an epoch is: a numbered baseline in the session</h2>
<p>The context epoch is a persistent record, <strong>one row per session</strong> (the <span class="mono">session_context_epoch</span> table). It stores all the essentials of "this session's current system context":</p>
<div class="cellgroup">
  <div class="cell"><div class="k">baseline</div><div class="v">the baseline full text for the model (all sources' baselines stitched)</div></div>
  <div class="cell"><div class="k">baseline_seq</div><div class="v">★ the sequence the baseline anchors at — history.load edge-trims by it (Lesson 19)</div></div>
  <div class="cell"><div class="k">snapshot</div><div class="v">structured snapshot of all sources' current values (for next comparison)</div></div>
  <div class="cell"><div class="k">revision</div><div class="v">how many times changed — optimistic-concurrency version number</div></div>
  <div class="cell"><div class="k">agent</div><div class="v">which agent this baseline belongs to (switching agent triggers re-establishment)</div></div>
</div>
<p>Read these fields together and the epoch's whole picture is clear: it's a "<strong>snapshot + anchor</strong>" — <span class="mono">baseline</span> is the baseline full text <strong>spoken to the model</strong>, <span class="mono">snapshot</span> is the structured memory <strong>remembered by the system</strong> (exactly Lesson 22's "speak once, remember once" landed at the session layer), and <span class="mono">baseline_seq</span> is the pin nailing this baseline <strong>to a point on the session timeline</strong>. The cleverest is this pin: one end connects to system context (the baseline starts here), the other to Lesson 19's history window (<span class="mono">history.load</span> reads only the conversation after this sequence). <strong>The epoch is the point where system context and session history meet and mesh.</strong></p>
<p>Note the <span class="mono">revision</span> field, inconspicuous but key: it's an <strong>optimistic-concurrency version number</strong>. In the source, <span class="mono">prepare</span> is wrapped in a <span class="mono">retryRevisionMismatch</span> layer — meaning, if two places try to update the same session's epoch almost simultaneously, they compare revisions, find "the version I read has already been changed by someone else," and <strong>back off and retry</strong>, rather than blindly overwriting and causing a lost update. This is another concurrency defense beyond Lesson 16's "serial within a session": epoch updates are guarded by a version number, ensuring two concurrent prepares don't trample each other's changes. A tiny <span class="mono">revision</span> integer carries the promise of "never silently losing a context update."</p>
<div class="timeline">
  <div class="tl-item"><span class="tl-time">…seq &lt; baselineSeq</span><span class="tl-desc">summarized by the baseline full text — history.load no longer reads each</span></div>
  <div class="tl-item"><span class="tl-time">baselineSeq (anchor)</span><span class="tl-desc">★ baseline established here: "before is backdrop, after is conversation"</span></div>
  <div class="tl-item"><span class="tl-time">seq &gt; baselineSeq</span><span class="tl-desc">the real conversation history — history.load reads each, feeds the model</span></div>
</div>

<h2>prepare: reconcile before each run</h2>
<p>The epoch isn't built once and forgotten. Before each session run (Lesson 17's loop starting), <span class="mono">SessionContextEpoch.prepare</span> is called — what it does, essentially, is "<strong>reconcile the environment observed now against the stored baseline</strong>." This rhythm of "reconcile before each run" is <strong>the same heartbeat</strong> as Lesson 17's "reread projected history each round": both distrust the old state hoarded in memory, and at each checkpoint go back to the durable layer to recalibrate against the latest truth. The logic branches into cases:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">first time</span><span class="t-txt">no stored record → initialize: observe all sources, stitch the baseline, insert, get baselineSeq, revision=0</span></div>
  <div class="t-row"><span class="t-num">same agent</span><span class="t-txt">stored record, agent unchanged → reconcile: compare against the snapshot</span></div>
  <div class="t-row"><span class="t-num">→ Unchanged</span><span class="t-txt">environment unchanged → keep old baseline/baselineSeq, send nothing</span></div>
  <div class="t-row"><span class="t-num">→ Updated</span><span class="t-txt">environment changed → publish a ContextUpdated event (with diff text), revision+1</span></div>
  <div class="t-row"><span class="t-num">switch agent</span><span class="t-txt">agent changed → replace: try to re-establish the epoch (may be blocked, Lesson 27)</span></div>
</div>
<p>This "reconcile" logic uses all the prior lessons' parts. <strong>First time</strong> is Lessons 21-23's chain "registry load → combine → initialize → Generation" landed as one database row. <strong>Same-agent reconcile</strong> is exactly Lesson 22's compare at the session level: environment unchanged → <strong>silence</strong> (Unchanged, keep the old baseline, don't even touch baselineSeq); changed → <strong>Updated</strong> — but note it's not simply editing a field but <strong>publishing a <span class="mono">ContextUpdated</span> event</strong>! This detail is vital: the context change is recorded as <strong>a formal event in the session history</strong> (remember Lessons 14, 15's "everything is an event, append-only"?) — so when the model rereads history next round, it naturally reads the "oh, the directory changed" update, seamlessly. <strong>The evolution of system context is itself part of event sourcing.</strong></p>
<div class="cols">
  <div class="col"><h4>reconcile · same agent, compute increment</h4><p>Agent unchanged. Compare current environment with the stored snapshot, compute "what changed." Normal operation takes this: silence or send an increment.</p></div>
  <div class="col"><h4>replace · switch agent, re-establish epoch</h4><p>Agent changed. The old baseline may no longer apply, try a wholesale replacement into a new epoch — and this step may be blocked (Lesson 27).</p></div>
</div>
<p>Why does "switching agent" take an entirely different <span class="mono">replace</span> path rather than counting as an ordinary "changed"? Because the agent isn't an ordinary field in the environment, it <strong>determines the whole context's "persona" and rules</strong>. The same directory, the same time, seen by a different agent, what to emphasize and what instructions to carry may be <strong>utterly different</strong>. This change is too fundamental to express as "append an increment onto the old baseline" — it needs <strong>tearing down the old baseline and re-establishing one</strong>, like switching mountaineering teams and pitching a new base camp rather than sticking a note on the old one. Splitting "same-agent evolution" and "agent-switch changing of the guard" into reconcile and replace paths is the epoch design's clarity about "changes come in sizes": small changes incremented, big changes started over.</p>
<div class="cellgroup">
  <div class="cell"><div class="k">Unchanged</div><div class="v">environment unchanged → keep old baseline, send nothing</div></div>
  <div class="cell"><div class="k">Updated</div><div class="v">environment changed → publish ContextUpdated event + revision+1</div></div>
  <div class="cell"><div class="k">ReplacementReady</div><div class="v">agent switched and replaceable → re-establish epoch, revision+1</div></div>
  <div class="cell"><div class="k">ReplacementBlocked</div><div class="v">agent switched but blocked → AgentReplacementBlocked (Lesson 27)</div></div>
</div>

<h2>baselineSeq: closing Lesson 19's loop</h2>
<p>Now we can formally close that hook hanging for five lessons. When Lesson 19 covered <span class="mono">history.load</span>, one of the two edge-trim lines it concurrently fetched was the <strong>context epoch's <span class="mono">baseline_seq</span></strong>. We said then "this line bounds the history window" but didn't say where it came from. Now the answer: <strong>it's this lesson's epoch, the sequence nailed down when the baseline was established.</strong> A hook five lessons in the making lands on so plain an integer — but it's exactly this integer that meshes the two seemingly-independent mechanisms seamlessly together.</p>
<div class="flow">
  <div class="node">sources (L21-23)<span class="sub">observe + combine</span></div>
  <div class="arrow">initialize →</div>
  <div class="node">Generation<span class="sub">baseline + snapshot</span></div>
  <div class="arrow">insert →</div>
  <div class="node">epoch (persisted)<span class="sub">nails down baselineSeq</span></div>
  <div class="arrow">history.load reads →</div>
  <div class="node">trim the history window<span class="sub">Lesson 19</span></div>
</div>
<p>Walk this chain and all of Parts 4 and 5 <strong>mesh into a closed loop</strong>: system context (L21-23) is observed, stitched into a baseline → established as an epoch, nailing down baselineSeq (this lesson) → this baselineSeq in turn tells history.load "where to start reading history" (L19) → the read history window, with the baseline, is fed to the agent loop (L17) → the loop produces new messages, new events → the next round's prepare reconciles again… System context doesn't hang isolated to the side but is <strong>deeply woven into the session's timeline and event stream</strong>. That tiny <span class="mono">baselineSeq</span> pin is the stitch sewing "the context system" and "the session engine" together.</p>
<p>Step back to this loop and you'll feel the architecture's "wholeness" more deeply. A less careful design might make "system context" a <strong>standalone little module</strong>: each round temporarily stitch some environment info, jam it at the front of the prompt, done. That works too, but it's <strong>two separate skins</strong> from the session history — context changes leave no trace, the history window's boundary is all guesswork. opencode refuses: it nails the context baseline <strong>into the session's same numbered timeline</strong>, makes context updates <strong>the session's same kind of event</strong>, so "context" and "conversation" share one persistence, one event stream, one edge-trim line. <strong>Not two systems forced to connect, but two sides of one system.</strong> This sense of "everything belonging to one event timeline" is a key lesson in understanding opencode's design taste — and the context epoch is that taste's most concentrated expression.</p>

<div class="card macro">
  <div class="tag">🗺️ The big picture</div>
  <p>This lesson is Part 5's <strong>hub</strong>, nailing abstract sources into a concrete session's timeline:</p>
  <ul>
    <li><strong>Epoch = snapshot + anchor</strong>: the <span class="mono">session_context_epoch</span> table stores baseline (spoken to the model), snapshot (remembered by the system), <strong>baseline_seq (the pin on the timeline)</strong>, revision, agent.</li>
    <li><strong>prepare reconciles before each run</strong>: first time initialize; same agent reconcile (Unchanged silent / Updated <strong>publishes a ContextUpdated event</strong>+revision+1); switch agent replace (Lesson 27).</li>
    <li><strong>Context changes also go through event sourcing</strong>: Updated isn't editing a field but publishing a ContextUpdated — system context's evolution is part of event sourcing.</li>
    <li><strong>baselineSeq closes Lesson 19</strong>: the epoch's nailed-down sequence is exactly history.load's history-window edge-trim line — the context system and session engine are stitched thereby.</li>
  </ul>
  <p>But two things this lesson only named without unfolding: one, "environment changed, send a <span class="mono">ContextUpdated</span> update event" — in what form does the model read this update <strong>mid-conversation</strong>? That's <strong>Lesson 25 (mid-conversation messages)</strong>. Two, "switched agent, the epoch must re-establish and may be blocked" — what is this <span class="mono">AgentReplacementBlocked</span>, why block? That's <strong>Lesson 27 (agent switch & epoch replacement)</strong>. The epoch's "normal operation" covered, the remaining lessons cover its "two special moments": mid-conversation update, and changing of the guard.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source detail</div>
  <p><span class="mono">prepareOnce</span>'s "environment changed" branch best shows "context change is an event":</p>
  <pre class="code"><span class="cm">// simplified from prepareOnce in session/context-epoch.ts</span>
<span class="kw">const</span> result = <span class="kw">yield</span>* SystemContext.<span class="fn">reconcile</span>(value, snapshot)  <span class="cm">// reconcile</span>
<span class="cm">// …Unchanged / ReplacementReady branches omitted…</span>
<span class="cm">// environment did update → publish it as a session event:</span>
<span class="kw">yield</span>* events.<span class="fn">publish</span>(
  SessionEvent.ContextUpdated,
  { sessionID, messageID: ..., timestamp: ..., text: result.text },  <span class="cm">// ← diff text</span>
  { commit: () =&gt; <span class="fn">advance</span>(db, sessionID, stored.revision, result.snapshot) })  <span class="cm">// advance revision + store new snapshot</span></pre>
  <p>Read it: <span class="mono">reconcile</span> computes "what changed" (<span class="mono">result.text</span> is exactly Lesson 22's update diff text), then <span class="mono">publish(SessionEvent.ContextUpdated, …)</span> emits it as an event. Note that <span class="mono">commit</span> callback — it's <strong>bound into one atomic operation</strong> with the event publish: only as the event lands does <span class="mono">advance</span> push the revision and store the new snapshot. "Send the update event" and "advance the epoch state" either both succeed or both don't, never a tear of "event sent, snapshot not updated." <strong>Even the context-update step abides by Lesson 15's event-sourcing discipline of "persist first, advance later."</strong></p>
</div>

<div class="card key">
  <div class="tag">🎯 Key points</div>
  <ul>
    <li><strong>The context epoch</strong> nails abstract sources into a <strong>numbered baseline</strong> in a session: the <span class="mono">session_context_epoch</span> table stores baseline, snapshot, <strong>baseline_seq</strong>, revision, agent.</li>
    <li><strong>The name "epoch"</strong>: establish a baseline at some sequence point → thereafter send only increments → a major event (switch agent) re-establishes a new epoch.</li>
    <li><strong>prepare reconciles before each run</strong>: first time initialize; same agent reconcile (Unchanged silent / Updated publishes a <span class="mono">ContextUpdated</span> event+revision+1); switch agent replace.</li>
    <li><strong>Context changes also go through event sourcing</strong>: Updated publishes a ContextUpdated (not editing a field), bound with advancing revision into an atomic commit — "persist first, advance later" (Lesson 15).</li>
    <li><strong>baselineSeq closes Lesson 19's loop</strong>: the epoch's nailed-down sequence is exactly <span class="mono">history.load</span>'s history-window edge-trim line — the context system and session engine stitched into one thereby.</li>
  </ul>
</div>
""",
}
LESSON_25 = {
    "zh": r"""
<p class="lead">上一课，纪元的 <span class="mono">prepare</span> 在环境变化时，<strong>publish 了一条 <span class="mono">ContextUpdated</span> 事件</strong>——我们说「模型下一轮重读历史时自然就读到了」，但没说<strong>它具体以什么形式、出现在历史的哪个位置</strong>。这一课就补上这关键一环。答案出奇地优雅：一条上下文更新，会被<strong>投影成一条 <span class="mono">System</span> 消息</strong>，<strong>原位插</strong>在会话历史里——就在它实际发生的那个时间点上。于是模型读历史时，会在恰当的位置看到「目录变成了 /src」这样一条系统旁白。这一课要让你看清：opencode 怎么把「对话中途的环境变化」，不靠任何特殊机制，<strong>无缝织进对话的时间线</strong>。</p>
<p>为什么「变化出现在哪个位置」这么重要？因为<strong>时机就是意义</strong>。设想你在第 6 条消息时说「跑一下测试」，那会儿你在 <span class="mono">/proj</span> 目录；第 7 条消息时你 <span class="mono">cd</span> 到了 <span class="mono">/proj/src</span>；第 8 条你又说「再跑一次」。这两次「跑测试」，因为中间夹着一次目录切换，<strong>含义可能完全不同</strong>。如果模型只看到「当前目录是 /src」这一句、却不知道它是<strong>何时</strong>变的，它就无法理解第 6 条那个「测试」指的是别处——它丢失了<strong>因果的时间线</strong>。这一课的核心，就是 opencode 怎么用「原位插入的 System 消息」，把环境变化的<strong>时机</strong>，原原本本地保留下来。</p>

<div class="card analogy">
  <div class="tag">🎭 生活类比</div>
  把一段会话想成一个<strong>剧本</strong>。演员的对白（user/assistant 消息）之间，剧本里穿插着<strong>舞台提示</strong>（System 消息）：「<em>（灯光转暗）</em>」「<em>（两人走进厨房）</em>」。这些提示的妙处，在于它们<strong>就印在对应的那一行旁边</strong>——演员读到某句台词时，能一眼看出此刻是在客厅还是厨房、灯亮还是灯暗。<strong>位置即时机</strong>：提示出现在剧本的哪一行，就代表那个变化发生在哪一刻。反过来想：要是把所有场景信息都<strong>钉在剧本扉页</strong>（「全剧地点：厨房」），演员就再也分不清哪句台词是在客厅说的、哪句是在厨房说的了——时间线被压扁了。opencode 处理上下文更新，走的正是「舞台提示」这条路：变化作为一条 System 旁白，<strong>原位插</strong>在它发生的那一刻，让模型像演员读剧本一样，时刻清楚「此情此景」。
</div>

<h2>System 消息：上下文更新的化身</h2>
<p>回顾第 14 课那个八成员的 Message 联合，其中有一种是 <span class="mono">System</span>。它的定义朴素得很——一个 <span class="mono">type: "system"</span>，加一个 <span class="mono">text</span> 字段。而这个 <span class="mono">text</span> 字段的类型，藏着这一课的钥匙：</p>
<pre class="code"><span class="cm">// session/message.ts</span>
<span class="kw">class</span> System {
  type: <span class="st">"system"</span>
  text: SessionEvent.ContextUpdated.data.fields.text   <span class="cm">// ← 就是 ContextUpdated 的 text！</span>
}</pre>
<p>看见没？<span class="mono">System</span> 消息的 <span class="mono">text</span>，<strong>类型上直接复用了 <span class="mono">ContextUpdated</span> 事件的 text</strong>。这不是巧合，而是明示：<strong>一条 System 消息，就是一次上下文更新在对话历史里的「化身」</strong>。第 24 课 <span class="mono">reconcile</span> 算出的那段差异文本（「目录切到 /src」），先成为一个 <span class="mono">ContextUpdated</span> 事件，再被投影成一条 <span class="mono">System</span> 消息，最终作为对话里的一条旁白，被模型读到。<strong>事件是底账里的一笔，System 消息是它在报表（投影历史）里的样子</strong>——这正是第 19 课「事件 → 投影」那套机制，作用在上下文更新上的具体一例。</p>
<p>这里要厘清一个常见的误会：很多人一听「System 消息」，会以为它就是那个老生常谈的「system prompt」（系统提示词，整段贴在对话最前面、定义 AI 人设的那一大段）。但 opencode 这里的 System 消息<strong>是另一回事</strong>：它不是开场那段一次性的角色设定，而是<strong>对话进行中、随环境变化而即时插入的一条条「旁白」</strong>。一个是<strong>开幕前的剧本说明</strong>（贴在最前、基本不变），一个是<strong>演出过程中的舞台提示</strong>（随剧情即时给出、各就各位）。把这两者分清楚很重要：opencode 真正的「开场设定」其实落在基线（baseline，第 24 课）里，而这一课的 System 消息，专指那些<strong>「中途才发生、所以要插在中途」</strong>的环境变化。理解了这个区分，你才能体会为什么它非得「原位」不可——开场设定无所谓位置，中途变化却字字看时机。混淆这两者，是新手读这套代码时最容易栽的一个跟头。说穿了：baseline 回答「这场对话从一开始处在什么世界」，System 消息回答「这个世界后来在哪一刻、怎么变了」。</p>
<div class="cellgroup">
  <div class="cell"><div class="k">type</div><div class="v">"system" —— Message 联合八成员之一（第 14 课）</div></div>
  <div class="cell"><div class="k">text</div><div class="v">复用 ContextUpdated.text —— 就是 reconcile 的差异文本</div></div>
  <div class="cell"><div class="k">位置</div><div class="v">由事件的 seq 决定 —— 原位插在变化发生的那一刻</div></div>
</div>

<h2>投影：和其它事件走同一条流水线</h2>
<p>这套设计最让人叫绝的，是它<strong>毫无特殊之处</strong>。打开投影器（<span class="mono">projector.ts</span>），你会看到一长串 <span class="mono">events.project(...)</span> 的登记——<span class="mono">Text</span>（文字）、<span class="mono">Tool</span>（工具）、<span class="mono">Reasoning</span>（思考）、<span class="mono">Shell</span>、<span class="mono">Step</span>…… 而 <span class="mono">ContextUpdated</span> 就<strong>安安静静地排在这一串里</strong>，和它们一模一样地被投影成消息。</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">你 cd 了 → 下次 prepare 的 reconcile 发现变化</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">publish 一条 ContextUpdated 事件（text=「目录切到 /src」，带 seq）</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">投影器把它和 Text/Tool 等事件一样，投影成一条 System 消息</span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">System 消息按 seq 落在历史里 —— 正好在变化发生的位置</span></div>
  <div class="t-row"><span class="t-num">5</span><span class="t-txt">下一轮 history.load 读出这段历史，模型原位读到这条旁白</span></div>
</div>
<p>「<span class="mono">ContextUpdated</span> 只是投影器列表里普普通通的一员」——这件事的份量，远比它听起来大。它意味着 opencode <strong>没有为「上下文更新」发明任何特殊通道</strong>：没有一个旁路的「系统提示注入器」，没有一段「每轮把环境拼到 prompt 开头」的特判逻辑。上下文更新，就是<strong>会话事件流里的一种普通事件</strong>，享受和文字、工具调用<strong>完全相同的待遇</strong>：一样地 publish、一样地投影、一样地按 seq 落位、一样地被 history.load 读出。<strong>把「特殊的东西」做成「不特殊」，是这套设计真正的高明之处</strong>——因为「不特殊」，它就自动继承了整条事件流水线的所有好处：持久、有序、可重放、原位。</p>
<div class="flow">
  <div class="node">ContextUpdated 事件<span class="sub">第 24 课 reconcile 产出</span></div>
  <div class="arrow">project →</div>
  <div class="node">投影器<span class="sub">和 Text/Tool 同一条流水线</span></div>
  <div class="arrow">→</div>
  <div class="node">System 消息<span class="sub">按 seq 原位落位</span></div>
  <div class="arrow">history.load →</div>
  <div class="node">模型原位读到<span class="sub">第 17 课循环</span></div>
</div>
<div class="cellgroup">
  <div class="cell"><div class="k">Text.Started/Ended</div><div class="v">模型吐的文字 → text part</div></div>
  <div class="cell"><div class="k">Tool.Called/Success…</div><div class="v">工具调用与结果 → tool part</div></div>
  <div class="cell"><div class="k">Reasoning.Started/Ended</div><div class="v">模型思考 → reasoning part</div></div>
  <div class="cell"><div class="k">ContextUpdated</div><div class="v">★ 上下文更新 → System 消息（和上面三个一视同仁）</div></div>
</div>
<p>看这张「投影器登记表」，你会更直观地体会那种「一视同仁」：模型的文字、工具的调用、内心的思考、环境的变化——在投影器眼里，<strong>全是「一种会话事件，投影成历史里的一笔」</strong>。它不关心这笔事件的来路是模型、是工具、还是系统对环境的观察；它只机械地、统一地把每种事件，按 seq 投影成历史里对应的那条消息或 part。这种「来源各异、待遇划一」的均质感，正是第 19 课「事件 → 投影」那套抽象的威力所在：<strong>只要你能把一件事表达成一个带 seq 的事件，它就能自动、原位地、可重放地，出现在模型读到的历史里。</strong>上下文更新，不过是又一个证明这套抽象有多通用的例子。</p>

<h2>位置即意义：保住时间线</h2>
<p>现在把前两节合起来，看它解决了开头那个难题。因为 System 消息<strong>按 seq 原位落在历史里</strong>，那段对话读起来就是这样的：</p>
<div class="timeline">
  <div class="tl-item"><span class="tl-time">msg 6</span><span class="tl-desc">User：「跑一下测试」（此刻在 /proj）</span></div>
  <div class="tl-item"><span class="tl-time">msg 7</span><span class="tl-desc">System：「目录切换到 /proj/src」←★ 上下文更新原位插入</span></div>
  <div class="tl-item"><span class="tl-time">msg 8</span><span class="tl-desc">User：「再跑一次」（此刻在 /proj/src）</span></div>
</div>
<p>模型读到这段，<strong>时间线一目了然</strong>：它能清清楚楚看到，第一次「跑测试」时在 <span class="mono">/proj</span>，中间切了目录，第二次「跑测试」已经在 <span class="mono">/proj/src</span> 了。环境变化的<strong>因果位置</strong>，被这条原位的 System 旁白<strong>完整保住</strong>。对比一下「把当前目录钉在 prompt 扉页」的笨办法：模型只会看到「当前目录 /proj/src」，却完全不知道这个目录是第 7 条才变的——于是它无从理解第 6 条那个「测试」其实指向别处。<strong>位置，承载着时机；时机，承载着意义。</strong>opencode 用「上下文更新即原位 System 消息」这一招，把这份「时机的意义」一丝不漏地交给了模型。</p>
<p>这件事还有一层更深的好处，关乎<strong>可重放</strong>。因为环境变化是一条<strong>原位的、不可变的事件</strong>，所以哪怕这个会话被关掉、几天后又打开，重新投影一遍历史，那条「第 7 条切了目录」的 System 消息<strong>依然原封不动地待在第 7 条的位置</strong>。换句话说，<strong>这段对话的「环境演变史」是可以被精确重建的</strong>——任何时候回看，第几条消息时在什么目录、用的什么 agent，都查得一清二楚。这正是第 19 课「事件是底账、永不改写」那条原则的红利在上下文层的兑现：把环境变化做成原位事件，等于给会话的「环境维度」也配上了一份可信、可重放的历史，而不是只留一个「当前是什么」的、丢失了过去的瞬时快照。<strong>能忠实回放过去任意一刻的环境，是「把上下文织进事件流」换来的、最不易察觉却最珍贵的能力。</strong></p>
<div class="cols">
  <div class="col"><h4>❌ 钉在 prompt 扉页</h4><p>每轮把「当前环境」拼到最前面。模型只知「现在是什么」，不知「何时变的」——时间线被压扁，早先消息的语境全丢。</p></div>
  <div class="col"><h4>✅ 原位 System 消息</h4><p>变化按 seq 插在发生点。模型读历史时，环境变化的时机一目了然，每条消息的语境都对得上。</p></div>
</div>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <p>这一课接住了第 24 课那条 <span class="mono">ContextUpdated</span> 事件，讲清了它怎么抵达模型：</p>
  <ul>
    <li><strong>System 消息 = 上下文更新的化身</strong>：其 <span class="mono">text</span> 类型直接复用 <span class="mono">ContextUpdated.text</span>——事件是底账一笔，System 消息是它在投影历史里的样子。</li>
    <li><strong>走同一条投影流水线</strong>：<span class="mono">ContextUpdated</span> 只是投影器里和 Text/Tool/Reasoning 并列的普通一员，没有任何特殊通道——「把特殊做成不特殊」，自动继承持久/有序/可重放/原位。</li>
    <li><strong>位置即意义</strong>：System 消息按 seq <strong>原位插入</strong>，保住了环境变化的时机；模型因此能正确理解早先消息的语境（对比「钉在 prompt 扉页」会压扁时间线）。</li>
  </ul>
  <p>到这里，上下文纪元的「常态运转 + 中途更新」都讲透了。整个第五部分只剩最后两块拼图：第 26 课看那些<strong>具体的内置源</strong>（环境、日期、指令）到底长什么样、各自怎么实现；第 27 课啃下唯一还没展开的硬骨头——<strong>换 agent 时的 <span class="mono">AgentReplacementBlocked</span></strong>，那个第 24 课反复点名、却一直没拆的「改朝换代」难题。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p><span class="mono">System</span> 消息的 text 复用 <span class="mono">ContextUpdated</span> 的 text，以及投影器里它和众多事件并列的那一行：</p>
  <pre class="code"><span class="cm">// session/message.ts —— text 类型直接借自事件</span>
text: SessionEvent.ContextUpdated.data.fields.text

<span class="cm">// session/projector.ts —— ContextUpdated 和 Text/Tool/… 并列登记</span>
<span class="kw">yield</span>* events.<span class="fn">project</span>(SessionEvent.ContextUpdated, (event) =&gt; <span class="fn">run</span>(db, event))
<span class="kw">yield</span>* events.<span class="fn">project</span>(SessionEvent.Synthetic, ...)
<span class="kw">yield</span>* events.<span class="fn">project</span>(SessionEvent.Text.Started, ...)
<span class="kw">yield</span>* events.<span class="fn">project</span>(SessionEvent.Tool.Called, ...)   <span class="cm">// ← 全是同一种 project 待遇</span></pre>
  <p>第一行用 <span class="mono">SessionEvent.ContextUpdated.data.fields.text</span> 给 System 消息的 text<strong>借用</strong>事件的字段类型——这是一种很 opencode 的写法：与其重新声明一遍「text 是个字符串」，不如<strong>直接指向事件里那个字段</strong>，让类型系统替你保证「消息的 text 永远和事件的 text 同形」。下面那一串 <span class="mono">project</span> 登记则一目了然：<span class="mono">ContextUpdated</span> 和 <span class="mono">Text</span>、<span class="mono">Tool</span> 排排坐、吃果果，没有一丝特殊待遇。<strong>代码的「平淡无奇」，恰恰是设计「浑然一体」的证据。</strong></p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li>第 24 课的 <span class="mono">ContextUpdated</span> 事件，被投影成一条 <strong>System 消息</strong>（第 14 课 Message 联合的一员），<strong>原位插</strong>在它发生的 seq 位置。</li>
    <li><strong>System.text 复用 ContextUpdated.text</strong>：一条 System 消息，就是一次上下文更新在投影历史里的「化身」（第 19 课事件→投影的具体一例）。</li>
    <li><strong>走同一条投影流水线</strong>：<span class="mono">ContextUpdated</span> 在投影器里和 Text/Tool/Reasoning <strong>并列</strong>，没有特殊通道——「把特殊做成不特殊」，自动继承持久/有序/可重放/原位。</li>
    <li><strong>位置即意义</strong>：原位插入保住了环境变化的<strong>时机</strong>，模型因此能正确理解早先消息的语境——对比「钉在 prompt 扉页」会压扁时间线、丢失因果。</li>
    <li>设计哲学：<strong>万物归于同一条事件时间线</strong>——上下文更新不是旁路特判，而是对话流里的一等公民。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Last lesson, the epoch's <span class="mono">prepare</span>, on an environment change, <strong>published a <span class="mono">ContextUpdated</span> event</strong> — we said "the model naturally reads it when rereading history next round," but didn't say <strong>in what form, at what position in the history, it appears</strong>. This lesson supplies that crucial link. The answer is surprisingly elegant: a context update is <strong>projected into a <span class="mono">System</span> message</strong>, <strong>inserted in place</strong> in the session history — right at the moment it actually happened. So when the model reads history, it sees, at the right spot, a system aside like "the directory changed to /src." This lesson shows you how opencode weaves "a mid-conversation environment change" <strong>seamlessly into the conversation timeline</strong>, with no special mechanism.</p>
<p>Why does "where the change appears" matter so much? Because <strong>timing is meaning</strong>. Suppose at message 6 you said "run the tests," then in <span class="mono">/proj</span>; at message 7 you <span class="mono">cd</span>'d to <span class="mono">/proj/src</span>; at message 8 you said "run them again." These two "run the tests," with a directory switch between, <strong>may mean entirely different things</strong>. If the model only sees "the current directory is /src" without knowing <strong>when</strong> it changed, it can't understand that message 6's "tests" meant somewhere else — it's lost the <strong>causal timeline</strong>. This lesson's core is how opencode uses "in-place System messages" to preserve the <strong>timing</strong> of environment changes intact.</p>

<div class="card analogy">
  <div class="tag">🎭 Analogy</div>
  Think of a conversation as a <strong>screenplay</strong>. Between the actors' dialogue (user/assistant messages), the script interleaves <strong>stage directions</strong> (System messages): "<em>(lights dim)</em>," "<em>(they walk into the kitchen)</em>." The beauty of these directions is they're <strong>printed right beside the corresponding line</strong> — reading a given line, an actor sees at a glance whether they're now in the living room or kitchen, lights up or down. <strong>Position is timing</strong>: which line of the script a direction appears at represents which moment that change happened. Conversely: if you pinned all scene info to the <strong>title page</strong> ("Whole play's location: kitchen"), the actor could no longer tell which lines were spoken in the living room vs the kitchen — the timeline is flattened. opencode handles context updates exactly the "stage direction" way: a change, as a System aside, is <strong>inserted in place</strong> at the moment it happens, so the model, like an actor reading a script, always knows "the here and now."
</div>

<h2>The System message: the avatar of a context update</h2>
<p>Recall Lesson 14's eight-member Message union, one of which is <span class="mono">System</span>. Its definition is quite plain — a <span class="mono">type: "system"</span> plus a <span class="mono">text</span> field. And that <span class="mono">text</span> field's type holds this lesson's key:</p>
<pre class="code"><span class="cm">// session/message.ts</span>
<span class="kw">class</span> System {
  type: <span class="st">"system"</span>
  text: SessionEvent.ContextUpdated.data.fields.text   <span class="cm">// ← it IS ContextUpdated's text!</span>
}</pre>
<p>See it? The <span class="mono">System</span> message's <span class="mono">text</span> <strong>type-wise directly reuses the <span class="mono">ContextUpdated</span> event's text</strong>. Not a coincidence but a declaration: <strong>a System message is a context update's "avatar" in the conversation history</strong>. Lesson 24's <span class="mono">reconcile</span>-computed diff text ("directory switched to /src") first becomes a <span class="mono">ContextUpdated</span> event, then is projected into a <span class="mono">System</span> message, finally read by the model as an aside in the conversation. <strong>The event is an entry in the ledger, the System message is its look in the statement (projected history)</strong> — exactly Lesson 19's "event → projection" mechanism applied to a context update.</p>
<p>Clear up a common misconception here: many, hearing "System message," assume it's the well-worn "system prompt" (the big block pasted at the very front defining the AI's persona). But opencode's System message here <strong>is another thing</strong>: not the opening one-time role setup but <strong>asides inserted in real time, mid-conversation, as the environment changes</strong>. One is the <strong>pre-curtain script note</strong> (pasted at front, basically unchanging), the other the <strong>stage directions during the show</strong> (given in real time as the plot unfolds, each in its place). Distinguishing them matters: opencode's true "opening setup" actually lands in the baseline (Lesson 24), while this lesson's System messages refer specifically to <strong>"environment changes that happened mid-way, hence inserted mid-way."</strong> Grasp this distinction and you can appreciate why it must be "in place" — opening setup doesn't care about position, but a mid-way change is all about timing. Confusing the two is the easiest stumble for a newcomer reading this code.</p>
<div class="cellgroup">
  <div class="cell"><div class="k">type</div><div class="v">"system" — one of the Message union's eight members (Lesson 14)</div></div>
  <div class="cell"><div class="k">text</div><div class="v">reuses ContextUpdated.text — exactly reconcile's diff text</div></div>
  <div class="cell"><div class="k">position</div><div class="v">determined by the event's seq — inserted in place at the moment of change</div></div>
</div>

<h2>Projection: the same pipeline as other events</h2>
<p>The most marvelous part of this design is it's <strong>nothing special</strong>. Open the projector (<span class="mono">projector.ts</span>) and you see a long string of <span class="mono">events.project(...)</span> registrations — <span class="mono">Text</span>, <span class="mono">Tool</span>, <span class="mono">Reasoning</span>, <span class="mono">Shell</span>, <span class="mono">Step</span>… and <span class="mono">ContextUpdated</span> <strong>sits quietly in this string</strong>, projected into a message exactly like them.</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">you cd'd → next prepare's reconcile finds the change</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">publish a ContextUpdated event (text="directory switched to /src", with seq)</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">the projector, like with Text/Tool events, projects it into a System message</span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">the System message lands in history by seq — right at the change's position</span></div>
  <div class="t-row"><span class="t-num">5</span><span class="t-txt">next round history.load reads this history, the model reads the aside in place</span></div>
</div>
<p>"<span class="mono">ContextUpdated</span> is just an ordinary member of the projector's list" — this carries far more weight than it sounds. It means opencode <strong>invented no special channel for "context updates"</strong>: no side "system-prompt injector," no special-case logic of "stitch the environment to the prompt's front each round." A context update is just <strong>one ordinary event in the session event stream</strong>, enjoying <strong>exactly the same treatment</strong> as text and tool calls: published the same, projected the same, positioned by seq the same, read by history.load the same. <strong>Making "the special thing" "unspecial" is this design's true cleverness</strong> — because it's "unspecial," it automatically inherits all the benefits of the whole event pipeline: durable, ordered, replayable, in-place.</p>
<div class="flow">
  <div class="node">ContextUpdated event<span class="sub">Lesson 24 reconcile produces</span></div>
  <div class="arrow">project →</div>
  <div class="node">projector<span class="sub">same pipeline as Text/Tool</span></div>
  <div class="arrow">→</div>
  <div class="node">System message<span class="sub">positioned in place by seq</span></div>
  <div class="arrow">history.load →</div>
  <div class="node">model reads it in place<span class="sub">Lesson 17 loop</span></div>
</div>
<div class="cellgroup">
  <div class="cell"><div class="k">Text.Started/Ended</div><div class="v">the model's text → text part</div></div>
  <div class="cell"><div class="k">Tool.Called/Success…</div><div class="v">tool calls and results → tool part</div></div>
  <div class="cell"><div class="k">Reasoning.Started/Ended</div><div class="v">the model's thinking → reasoning part</div></div>
  <div class="cell"><div class="k">ContextUpdated</div><div class="v">★ context update → System message (treated identically to the three above)</div></div>
</div>
<p>Look at this "projector registration table" and you feel the "equal treatment" more vividly: the model's text, tool calls, inner thinking, environment changes — to the projector, <strong>all are "a kind of session event, projected into an entry in history."</strong> It doesn't care whether the event came from the model, a tool, or the system observing the environment; it mechanically, uniformly projects each event type, by seq, into the corresponding message or part in history. This homogeneity of "varied origins, uniform treatment" is exactly the power of Lesson 19's "event → projection" abstraction: <strong>as long as you can express something as an event with a seq, it can automatically, in-place, replayably appear in the history the model reads.</strong> A context update is just another example proving how general this abstraction is.</p>

<h2>Position is meaning: preserving the timeline</h2>
<p>Now combine the past two sections and see how it solves the opening puzzle. Because the System message <strong>lands in place in history by seq</strong>, that stretch of conversation reads like this:</p>
<div class="timeline">
  <div class="tl-item"><span class="tl-time">msg 6</span><span class="tl-desc">User: "run the tests" (now in /proj)</span></div>
  <div class="tl-item"><span class="tl-time">msg 7</span><span class="tl-desc">System: "directory switched to /proj/src" ←★ context update inserted in place</span></div>
  <div class="tl-item"><span class="tl-time">msg 8</span><span class="tl-desc">User: "run them again" (now in /proj/src)</span></div>
</div>
<p>Reading this, the model has <strong>a clear timeline</strong>: it can plainly see that the first "run the tests" was in <span class="mono">/proj</span>, a directory switch happened in between, and the second "run the tests" is already in <span class="mono">/proj/src</span>. The <strong>causal position</strong> of the environment change is <strong>fully preserved</strong> by this in-place System aside. Contrast the clumsy "pin the current directory to the prompt's title page": the model only sees "current directory /proj/src," with no idea this directory only changed at message 7 — so it can't understand that message 6's "tests" pointed elsewhere. <strong>Position carries timing; timing carries meaning.</strong> opencode, with "a context update is an in-place System message," hands the model this "meaning of timing" without losing a drop.</p>
<p>There's a deeper benefit too, about <strong>replayability</strong>. Because an environment change is an <strong>in-place, immutable event</strong>, even if this session is closed and reopened days later, reprojecting the history, that "directory switched at message 7" System message <strong>still sits untouched at message 7's position</strong>. In other words, <strong>this conversation's "environment evolution history" can be precisely reconstructed</strong> — anytime you look back, which directory at which message, which agent, all queryable clearly. This is Lesson 19's "events are the ledger, never rewritten" dividend cashed at the context layer: making environment changes in-place events equips the session's "environment dimension" too with a trustworthy, replayable history, rather than only a "what's current" instantaneous snapshot that lost its past. <strong>Being able to faithfully replay the environment of any past moment is the least noticeable yet most precious ability bought by "weaving context into the event stream."</strong></p>
<div class="cols">
  <div class="col"><h4>❌ pinned to the prompt's title page</h4><p>Stitch "current environment" to the front each round. The model knows only "what's now," not "when it changed" — the timeline flattened, earlier messages' context lost.</p></div>
  <div class="col"><h4>✅ in-place System message</h4><p>The change is inserted by seq at the point it happened. Reading history, the model sees the timing of environment changes clearly, every message's context lining up.</p></div>
</div>

<div class="card macro">
  <div class="tag">🗺️ The big picture</div>
  <p>This lesson catches Lesson 24's <span class="mono">ContextUpdated</span> event and explains how it reaches the model:</p>
  <ul>
    <li><strong>System message = a context update's avatar</strong>: its <span class="mono">text</span> type directly reuses <span class="mono">ContextUpdated.text</span> — the event is a ledger entry, the System message its look in projected history.</li>
    <li><strong>The same projection pipeline</strong>: <span class="mono">ContextUpdated</span> is just an ordinary member alongside Text/Tool/Reasoning in the projector, no special channel — "make the special unspecial," automatically inheriting durable/ordered/replayable/in-place.</li>
    <li><strong>Position is meaning</strong>: the System message <strong>inserted in place</strong> by seq preserves the timing of environment changes; the model can thus correctly understand earlier messages' context (vs "pinned to the title page," which flattens the timeline).</li>
  </ul>
  <p>By here, the context epoch's "normal operation + mid-conversation update" is covered. Part 5 has only two puzzle pieces left: Lesson 26 looks at what the concrete <strong>built-in sources</strong> (environment, date, instructions) actually look like and how each is implemented; Lesson 27 cracks the one hard bone left unopened — <strong>the <span class="mono">AgentReplacementBlocked</span> on agent switch</strong>, that "changing of the guard" puzzle Lesson 24 kept naming but never unpacked.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source detail</div>
  <p>The <span class="mono">System</span> message's text reusing <span class="mono">ContextUpdated</span>'s text, and its line in the projector alongside many events:</p>
  <pre class="code"><span class="cm">// session/message.ts — text type borrowed directly from the event</span>
text: SessionEvent.ContextUpdated.data.fields.text

<span class="cm">// session/projector.ts — ContextUpdated registered alongside Text/Tool/…</span>
<span class="kw">yield</span>* events.<span class="fn">project</span>(SessionEvent.ContextUpdated, (event) =&gt; <span class="fn">run</span>(db, event))
<span class="kw">yield</span>* events.<span class="fn">project</span>(SessionEvent.Synthetic, ...)
<span class="kw">yield</span>* events.<span class="fn">project</span>(SessionEvent.Text.Started, ...)
<span class="kw">yield</span>* events.<span class="fn">project</span>(SessionEvent.Tool.Called, ...)   <span class="cm">// ← all the same project treatment</span></pre>
  <p>The first line uses <span class="mono">SessionEvent.ContextUpdated.data.fields.text</span> to <strong>borrow</strong> the event's field type for the System message's text — a very opencode move: rather than redeclaring "text is a string," <strong>point directly at that field in the event</strong>, letting the type system guarantee "the message's text is forever the same shape as the event's text." The string of <span class="mono">project</span> registrations below is plain to see: <span class="mono">ContextUpdated</span> sits side by side with <span class="mono">Text</span>, <span class="mono">Tool</span>, with not a shred of special treatment. <strong>The code's "unremarkableness" is precisely the evidence of the design's "wholeness."</strong></p>
</div>

<div class="card key">
  <div class="tag">🎯 Key points</div>
  <ul>
    <li>Lesson 24's <span class="mono">ContextUpdated</span> event is projected into a <strong>System message</strong> (a member of Lesson 14's Message union), <strong>inserted in place</strong> at its seq position.</li>
    <li><strong>System.text reuses ContextUpdated.text</strong>: a System message is a context update's "avatar" in projected history (a concrete instance of Lesson 19's event→projection).</li>
    <li><strong>The same projection pipeline</strong>: <span class="mono">ContextUpdated</span> sits <strong>alongside</strong> Text/Tool/Reasoning in the projector, no special channel — "make the special unspecial," automatically inheriting durable/ordered/replayable/in-place.</li>
    <li><strong>Position is meaning</strong>: in-place insertion preserves the <strong>timing</strong> of environment changes, so the model correctly understands earlier messages' context — vs "pinned to the title page," which flattens the timeline and loses causality.</li>
    <li>Design philosophy: <strong>everything belongs to one event timeline</strong> — context updates aren't a side special case but a first-class citizen of the conversation stream.</li>
  </ul>
</div>
""",
}
LESSON_26 = {
    "zh": r"""
<p class="lead">第 21 到 25 课，我们造了一台相当精密的机器：源的代数、codec 派生的判等、注册表、上下文纪元、原位 System 消息……一路都在讲<strong>「机制」</strong>。这一课，终于到了<strong>掀开盖子、看看里面实际装了什么零件</strong>的时候——opencode 真正内置的那几个上下文源，到底长什么样。而最让人会心一笑的发现是：<strong>它们简单得不可思议</strong>。一个源的完整定义，往往就十来行。前五课那套看似复杂的机制，到了具体的源这里，<strong>全化成了寥寥几行清爽的声明</strong>。这一课要让你体会的，正是「好抽象」最甜的回报：<strong>把复杂吸进框架，让使用处简单到近乎透明。</strong></p>
<p>为什么「源居然这么简单」值得专门点出来？因为这是检验一套抽象成不成功的<strong>试金石</strong>。一套糟糕的抽象，会让「加一个新东西」变得繁琐——要懂一堆内部细节、要小心翼翼地接好各种线。而一套好的抽象，会让「加一个新东西」变得<strong>近乎填空</strong>：你只需声明这个东西<strong>独有</strong>的那一点点信息，其余的——序列化、判等、注册、刷新、投影——框架全替你包圆了。这一课通过 <span class="mono">core/environment</span> 和 <span class="mono">core/date</span> 这两个真实的内置源，让你亲眼看看：前面五课的机制，把「写一个上下文源」这件事，简化到了什么程度。</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  想象你花大力气搭好了一套<strong>「智能表单系统」</strong>：它能自动校验、自动存历史版本、自动高亮「这次比上次改了哪里」。系统本身很复杂——但正因为它复杂，<strong>真正去填一张表，就简单到了极点</strong>。比如填「当前地点表」，你只需写一行「地点：北京」；填「日期表」，只需写一行「今天：周一」。校验、存档、比对、提醒变化——这些活，全是表单系统在背后默默干，<strong>填表的人一概不用操心</strong>。opencode 的内置源就是这样几张「填好的表」：<span class="mono">core/environment</span> 这张表填的是「目录、项目根、是不是 git 仓库」，<span class="mono">core/date</span> 那张填的是「今天几号」。表本身短得可怜，因为前五课那套「表单系统」（源框架），早已把所有重活扛走了。<strong>表越简单，越证明系统越强大。</strong>
</div>

<h2>core/environment：你身处的环境</h2>
<p>第一个内置源，是 <span class="mono">core/environment</span>——它告诉模型「你此刻在一个什么样的运行环境里」。它观察的值，是一段用 <span class="mono">&lt;env&gt;</span> 标签裹起来的环境描述：</p>
<pre class="code"><span class="cm">// 简化自 system-context/builtins.ts</span>
<span class="kw">const</span> environment = [
  <span class="st">"&lt;env&gt;"</span>,
  <span class="st">`  Working directory: ${'$'}{location.directory}`</span>,        <span class="cm">// 工作目录</span>
  <span class="st">`  Workspace root folder: ${'$'}{location.project.directory}`</span>, <span class="cm">// 项目根</span>
  <span class="st">`  Is directory a git repo: ${'$'}{...}`</span>,                  <span class="cm">// 是不是 git 仓库</span>
  <span class="st">`  Platform: ${'$'}{process.platform}`</span>,                    <span class="cm">// 操作系统平台</span>
  <span class="st">"&lt;/env&gt;"</span>,
].<span class="fn">join</span>(<span class="st">"\n"</span>)</pre>
<p>留意那对 <span class="mono">&lt;env&gt;...&lt;/env&gt;</span> 标签——这是给大模型喂结构化信息的一个常用小技巧：用类 XML 的标签把一块信息<strong>圈出清晰的边界</strong>，模型一眼就能认出「这是环境块」，不会和正文混淆。里面四项也都挑得很实在：<strong>工作目录</strong>（我在哪干活）、<strong>项目根</strong>（这个项目的边界在哪）、<strong>是否 git 仓库</strong>（能不能用 git 命令）、<strong>平台</strong>（是 Linux 还是 Mac，影响命令写法）。这四样，正是一个要帮你写代码、跑命令的 agent <strong>最起码得知道的「我在哪」</strong>。</p>
<p>这四项的取舍，本身就透着设计者对「agent 真正需要什么」的拿捏。它<strong>没有</strong>一股脑把整个系统的环境变量、磁盘容量、CPU 型号全倒给模型——那些大多是噪声，只会挤占宝贵的上下文、还分散模型注意力。它精选的，是<strong>会实打实影响 agent 决策</strong>的那几样：知道<strong>工作目录</strong>，相对路径才算得对；知道<strong>项目根</strong>，才不会改到项目外的文件；知道<strong>是不是 git 仓库</strong>，才决定要不要用 git 来看改动；知道<strong>平台</strong>，写命令时才知道是 <span class="mono">ls</span> 还是 <span class="mono">dir</span>。<strong>给模型的上下文，贵精不贵多</strong>——每一项都该是「不给它就会做错事」的，而非「给了也无妨」的。这种克制，和第 18 课工具输出落盘、整套系统对「token 寸土寸金」的敬畏，是一以贯之的。</p>
<div class="cellgroup">
  <div class="cell"><div class="k">Working directory</div><div class="v">当前工作目录——命令在哪执行、相对路径从哪算</div></div>
  <div class="cell"><div class="k">Workspace root</div><div class="v">项目根目录——项目的边界</div></div>
  <div class="cell"><div class="k">Is git repo</div><div class="v">能不能用 git（影响 agent 的操作选择）</div></div>
  <div class="cell"><div class="k">Platform</div><div class="v">linux/darwin/win32——命令语法因平台而异</div></div>
</div>

<h2>core/date：连「日期」都是一个源</h2>
<p>第二个内置源 <span class="mono">core/date</span>，简单到只有一行 <span class="mono">load</span>：取今天的日期。但它最值得玩味的地方，恰恰是一个问题：<strong>「日期」这么个东西，为什么要做成一个带 <span class="mono">baseline</span>/<span class="mono">update</span> 的源，而不是开场写死一句「今天是 X」就完事？</strong></p>
<pre class="code"><span class="cm">// 简化自 system-context/builtins.ts —— 一个源，十行不到</span>
SystemContext.<span class="fn">make</span>({
  key: SystemContext.Key.<span class="fn">make</span>(<span class="st">"core/date"</span>),
  codec: Schema.<span class="fn">toCodecJson</span>(Schema.String),
  load: DateTime.nowAsDate.<span class="fn">pipe</span>(Effect.<span class="fn">map</span>((d) =&gt; d.<span class="fn">toDateString</span>())),
  baseline: (date) =&gt; <span class="st">`Today's date: ${'$'}{date}`</span>,            <span class="cm">// 首次</span>
  update: (_prev, date) =&gt; <span class="st">`Today's date is now: ${'$'}{date}`</span>,  <span class="cm">// 跨天后</span>
})</pre>
<p>答案是：<strong>因为日期会变</strong>。一个会话可能从晚上聊到第二天凌晨——<strong>跨过了午夜</strong>。如果日期是开场写死的，那么过了午夜，模型脑子里的「今天」就<strong>错了</strong>，它可能把昨天当今天、把 deadline 算错一天。把日期做成源，下一轮 <span class="mono">prepare</span> 一对表，<span class="mono">reconcile</span> 就会发现「日期变了」，自动 publish 一条更新——模型于是读到「Today's date is now: ...」，时钟无缝拨正。<strong>连「日期」这种看似一成不变的东西，在一个可能长跑的会话里，都是「活」的</strong>——这正是前五课那套增量机制存在的意义：它不挑大小，任何「可能会变」的环境信息，都能用同一套源框架，优雅地保持新鲜。</p>
<div class="timeline">
  <div class="tl-item"><span class="tl-time">周一 21:00</span><span class="tl-desc">会话开始 → baseline：「Today's date: Mon Jun 23」</span></div>
  <div class="tl-item"><span class="tl-time">周一 23:30</span><span class="tl-desc">还在聊 → reconcile：日期没变 → Unchanged，沉默</span></div>
  <div class="tl-item"><span class="tl-time">★ 跨午夜 00:00</span><span class="tl-desc">日期变了！</span></div>
  <div class="tl-item"><span class="tl-time">周二 00:15</span><span class="tl-desc">下一轮 → reconcile：变了 → update：「Today's date is now: Tue Jun 24」</span></div>
</div>
<div class="cols">
  <div class="col"><h4>baseline：「Today's date: X」</h4><p>首次告知。措辞像在<strong>陈述一个事实</strong>。</p></div>
  <div class="col"><h4>update：「Today's date is now: X」</h4><p>跨天后告知。那个 <strong>now</strong>，在向模型明示「这是一个<strong>变化</strong>」。</p></div>
</div>
<p>顺带品一下 <span class="mono">baseline</span> 和 <span class="mono">update</span> 的<strong>措辞差异</strong>：首次是「Today's date: X」（平铺直叙），变化后是「Today's date is now: X」——多出来的那个 <span class="mono">now</span>，是在轻轻提醒模型「<strong>注意，这是新变的</strong>」。环境源那边也一样：baseline 说「Here is some useful information…」，update 说「The environment …is now：」。这种<strong>用措辞本身去区分「初始」与「变化」</strong>的小心思，看似微不足道，却让模型读起来语感更自然——它能从字里行间感到「哦，这是后来才变的」，而非又一次重复。<strong>好的上下文，不只内容对，连「这是不是新消息」的语气都对。</strong></p>
<p>这个细节小到几乎没人会注意，却恰恰是「为读者着想」这件事最纯粹的体现——只不过这里的「读者」是个大模型。一个不走心的实现，baseline 和 update 大可以用一模一样的措辞，反正信息都传到了。但 opencode 多花了这一点心思：让「首次陈述」读起来像陈述，让「后续变化」读起来像变化。对模型而言，「now」这个词就是一个微弱却清晰的信号，帮它把「这是当前状态的重申」和「这是刚刚发生的改变」区分开。<strong>把使用者（哪怕是个 AI）的阅读体验放在心上，连一个单词的取舍都不肯随便——这种近乎偏执的体贴，往往是区分「能用」和「好用」的那道细微而决定性的分水岭。</strong></p>

<h2>还有指令：InstructionContext</h2>
<p>除了环境和日期，还有一个更「重」的内置源——<span class="mono">InstructionContext</span>（<span class="mono">instruction-context.ts</span>）。它管的是项目里那些<strong>常驻指令</strong>：<span class="mono">AGENTS.md</span> 之类的文件，写着「这个项目用什么规范、有什么禁忌、希望 agent 怎么干活」。这些指令也被包装成一个源，注册进同一个注册表——于是它和环境、日期<strong>一视同仁</strong>地参与基线、增量、投影。<strong>项目规范变了（你改了 AGENTS.md），它也能像目录变化一样，被增量地告知模型。</strong></p>
<p>把这三个源放一起看，opencode「喂给模型的世界」就有了血肉：<strong>环境</strong>告诉它「我在哪、什么平台」，<strong>日期</strong>告诉它「现在何时」，<strong>指令</strong>告诉它「这个项目的规矩」。三者各是一个独立的源，各自观察、各自增量、各自原位更新，最后由注册表汇成一份完整、有序、可增量的系统上下文。<strong>这就是前五课那套抽象，落到实处的全部模样。</strong></p>
<p>还有一点值得回味：这三个源是 opencode <strong>内置</strong>的，但它们和「将来某个插件贡献的源」<strong>站在完全平等的位置</strong>上。<span class="mono">core/environment</span> 并不因为姓「core」就享有什么特权——它也是规规矩矩 <span class="mono">make</span> 一个 <span class="mono">Source</span>、注册进同一个注册表。这意味着：<strong>opencode 自己用的，和它开放给第三方扩展的，是同一套机制</strong>。这种「自己人和外人吃同一锅饭」的设计（业界叫 dogfooding——吃自家的狗粮），是一套扩展机制健康的最好证明：因为框架的作者自己就靠它过日子，它就不可能是个糊弄人的、二等的扩展点。你将来想给 opencode 加一个「当前分支名」或「最近一次构建状态」的上下文源，走的会是和 <span class="mono">core/date</span> 一模一样的那五行——这，就是好抽象最慷慨的承诺。</p>
<div class="cellgroup">
  <div class="cell"><div class="k">core/environment</div><div class="v">「我在哪」：目录、项目根、git、平台</div></div>
  <div class="cell"><div class="k">core/date</div><div class="v">「现在何时」：今天的日期（跨天会更新）</div></div>
  <div class="cell"><div class="k">InstructionContext</div><div class="v">「这里的规矩」：AGENTS.md 等常驻指令</div></div>
</div>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <p>这一课把第五部分前五课的抽象，<strong>兑现成了几个真实、极简的源</strong>：</p>
  <ul>
    <li><strong>源的定义短得惊人</strong>：十来行声明 key/codec/load/baseline/update，重活全被框架（codec 派生判等、注册表、纪元、投影）吸走——这是「好抽象」的试金石。</li>
    <li><strong>core/environment</strong>：用 <span class="mono">&lt;env&gt;</span> 标签裹住目录/项目根/git/平台——agent 最起码得知道的「我在哪」。</li>
    <li><strong>core/date</strong>：连「日期」都是源，因为会话可能<strong>跨午夜</strong>——任何「可能变」的信息都值得用源框架保持新鲜。</li>
    <li><strong>措辞区分</strong>：baseline 平铺、update 用「now」轻点「这是变化」——连语气都为模型着想。</li>
    <li><strong>InstructionContext</strong>：AGENTS.md 等项目指令，也是一个一视同仁的源。</li>
  </ul>
  <p>到这里，系统上下文的「常态」全部讲透：抽象（L21-23）、落进会话（L24）、中途更新（L25）、具体内置（本课）。整个第五部分只剩最后一块、也是最硬的一块拼图——第 24 课反复点名、却始终没拆的 <span class="mono">AgentReplacementBlocked</span>：<strong>当你中途换了一个 agent，那份属于旧 agent 的上下文纪元，该怎么办？为什么「替换」有时会被「阻挡」？</strong>这就是下一课、也是第五部分压轴的 <strong>Agent 切换与 Epoch 替换（第 27 课）</strong>。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p>一个完整的源定义有多简单？看 <span class="mono">core/environment</span> 的全貌——五个字段，没一句废话：</p>
  <pre class="code"><span class="cm">// 简化自 system-context/builtins.ts</span>
SystemContext.<span class="fn">make</span>({
  key: SystemContext.Key.<span class="fn">make</span>(<span class="st">"core/environment"</span>),     <span class="cm">// 唯一标识</span>
  codec: Schema.<span class="fn">toCodecJson</span>(Schema.String),               <span class="cm">// 值是字符串</span>
  load: Effect.<span class="fn">succeed</span>(environment),                      <span class="cm">// 怎么观察</span>
  baseline: (env) =&gt; <span class="st">`Here is ...:\n${'$'}{env}`</span>,            <span class="cm">// 首次全文</span>
  update: (_prev, env) =&gt; <span class="st">`The environment ...is now:\n${'$'}{env}`</span>, <span class="cm">// 变化文本</span>
})</pre>
  <p>就这么五行。<strong>没有</strong>一行在写「怎么序列化」（<span class="mono">codec</span> 一指，第 22 课的 encode/decode/equivalent 自动就位）；<strong>没有</strong>一行在写「怎么注册、怎么排序、怎么并发」（交给第 23 课的注册表）；<strong>没有</strong>一行在写「怎么持久化、怎么钉序号、怎么投影成 System 消息」（交给第 24、25 课）。一个源的作者，只需回答五个最本质的问题：<strong>叫什么、值长啥样、怎么观察、首次怎么说、变了怎么说</strong>。其余一切，前五课那套机制全替他答了。<strong>这五行的清爽，是前面所有复杂换来的——复杂被收进了框架，简单留给了使用者。</strong></p>
  <div class="cols">
    <div class="col"><h4>框架扛走的（你看不见）</h4><p>encode/decode/equivalent 判等、scoped 注册、按 key 排序、并发观察、纪元持久化、钉 baselineSeq、投影成 System 消息、原位落位……一大堆。</p></div>
    <div class="col"><h4>源作者写的（就五行）</h4><p>key、codec、load、baseline、update。回答「叫什么/值长啥样/怎么观察/首次怎么说/变了怎么说」，完。</p></div>
  </div>
  <div class="cellgroup">
    <div class="cell"><div class="k">key</div><div class="v">"core/date" —— 唯一标识</div></div>
    <div class="cell"><div class="k">codec</div><div class="v">Schema.String —— 值是字符串</div></div>
    <div class="cell"><div class="k">load</div><div class="v">取今天日期 —— 怎么观察</div></div>
    <div class="cell"><div class="k">baseline / update</div><div class="v">「Today's date: X」/「…is now: X」—— 首次 / 变化怎么说</div></div>
  </div>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li>前五课的抽象，兑现成的真实源<strong>简单得惊人</strong>：十来行声明 <strong>key/codec/load/baseline/update</strong>，重活全被框架吸走——这是「好抽象」的试金石。</li>
    <li><strong>core/environment</strong>：<span class="mono">&lt;env&gt;</span> 标签裹住<strong>目录、项目根、是否 git、平台</strong>——agent 最起码得知道的「我在哪」。</li>
    <li><strong>core/date</strong>：连「日期」都做成源，因为会话可能<strong>跨午夜</strong>变天——任何「可能变」的信息都值得用源框架保持新鲜。</li>
    <li><strong>措辞区分初始与变化</strong>：baseline「Today's date: X」平铺，update「Today's date is now: X」用 now 轻点变化——连语气都为模型着想。</li>
    <li><strong>InstructionContext</strong>（AGENTS.md 等项目指令）也是一视同仁的源：环境「我在哪」、日期「何时」、指令「规矩」，三者共同织成模型所处的世界。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Lessons 21 to 25 built a rather precise machine: the source algebra, codec-derived equality, the registry, the context epoch, in-place System messages… all about <strong>"mechanism."</strong> This lesson, at last, is time to <strong>lift the lid and see what parts are actually inside</strong> — what opencode's truly built-in context sources actually look like. And the most knowing-smile discovery is: <strong>they're unbelievably simple</strong>. A source's complete definition is often a dozen lines. The seemingly-complex machinery of the past five lessons, at the concrete source, <strong>dissolves into a few crisp declarations</strong>. What this lesson wants you to feel is the sweetest reward of "good abstraction": <strong>absorb the complexity into the framework, leave the use site simple to near-transparency.</strong></p>
<p>Why call out "sources are this simple"? Because it's the <strong>touchstone</strong> of whether an abstraction succeeds. A bad abstraction makes "add a new thing" tedious — you must know a heap of internal detail, carefully wire up various connections. A good abstraction makes "add a new thing" <strong>nearly fill-in-the-blank</strong>: you only declare the bit of info <strong>unique</strong> to this thing, and the rest — serialization, equality, registration, refresh, projection — the framework wraps up for you. Through two real built-in sources, <span class="mono">core/environment</span> and <span class="mono">core/date</span>, this lesson lets you see firsthand: to what degree the past five lessons' machinery simplifies "writing a context source."</p>

<div class="card analogy">
  <div class="tag">🧩 Analogy</div>
  Imagine you spent great effort building a <strong>"smart form system"</strong>: it auto-validates, auto-stores version history, auto-highlights "what changed since last time." The system itself is complex — but precisely because it's complex, <strong>actually filling in a form is dead simple</strong>. To fill the "current location form," you just write one line "Location: Beijing"; the "date form," just "Today: Monday." Validation, archiving, comparison, change-flagging — these the form system silently does behind the scenes, and <strong>the form-filler needn't worry about any of it</strong>. opencode's built-in sources are just such "filled-in forms": <span class="mono">core/environment</span> fills "directory, project root, is-git-repo," <span class="mono">core/date</span> fills "what's today." The forms are pitifully short, because the past five lessons' "form system" (the source framework) long since carried off all the heavy lifting. <strong>The simpler the form, the more it proves how powerful the system is.</strong>
</div>

<h2>core/environment: the environment you're in</h2>
<p>The first built-in source is <span class="mono">core/environment</span> — it tells the model "what runtime environment you're in right now." The value it observes is an environment description wrapped in <span class="mono">&lt;env&gt;</span> tags:</p>
<pre class="code"><span class="cm">// simplified from system-context/builtins.ts</span>
<span class="kw">const</span> environment = [
  <span class="st">"&lt;env&gt;"</span>,
  <span class="st">`  Working directory: ${'$'}{location.directory}`</span>,        <span class="cm">// working directory</span>
  <span class="st">`  Workspace root folder: ${'$'}{location.project.directory}`</span>, <span class="cm">// project root</span>
  <span class="st">`  Is directory a git repo: ${'$'}{...}`</span>,                  <span class="cm">// is it a git repo</span>
  <span class="st">`  Platform: ${'$'}{process.platform}`</span>,                    <span class="cm">// OS platform</span>
  <span class="st">"&lt;/env&gt;"</span>,
].<span class="fn">join</span>(<span class="st">"\n"</span>)</pre>
<p>Note the <span class="mono">&lt;env&gt;...&lt;/env&gt;</span> tags — a common trick for feeding structured info to an LLM: XML-like tags <strong>draw clear boundaries</strong> around a block of info, so the model recognizes "this is the environment block" at a glance, not confusing it with the body. The four items inside are also chosen practically: <strong>working directory</strong> (where I work), <strong>project root</strong> (where this project's boundary is), <strong>is-git-repo</strong> (whether git commands are usable), <strong>platform</strong> (Linux or Mac, affecting command syntax). These four are exactly the bare minimum an agent meant to write code and run commands for you <strong>must know about "where am I."</strong></p>
<p>The selection of these four itself shows the designer's grasp of "what an agent truly needs." It does <strong>not</strong> dump the whole system's environment variables, disk capacity, CPU model at the model — mostly noise that only crowds the precious context and distracts the model. What it handpicks is the few that <strong>genuinely affect the agent's decisions</strong>: knowing the <strong>working directory</strong>, relative paths compute right; knowing the <strong>project root</strong>, it won't edit files outside the project; knowing <strong>is-git-repo</strong>, it decides whether to use git for diffs; knowing the <strong>platform</strong>, it knows to write <span class="mono">ls</span> or <span class="mono">dir</span>. <strong>Context given to the model is about quality, not quantity</strong> — each item should be one where "not giving it would cause mistakes," not "no harm giving it." This restraint is of one piece with Lesson 18's tool output to disk, and the whole system's reverence for "tokens are precious."</p>
<div class="cellgroup">
  <div class="cell"><div class="k">Working directory</div><div class="v">current dir — where commands run, where relative paths compute from</div></div>
  <div class="cell"><div class="k">Workspace root</div><div class="v">project root directory — the project's boundary</div></div>
  <div class="cell"><div class="k">Is git repo</div><div class="v">whether git is usable (affects the agent's choices)</div></div>
  <div class="cell"><div class="k">Platform</div><div class="v">linux/darwin/win32 — command syntax varies by platform</div></div>
</div>

<h2>core/date: even "the date" is a source</h2>
<p>The second built-in source <span class="mono">core/date</span> is simple to a single <span class="mono">load</span> line: get today's date. But its most intriguing point is exactly a question: <strong>why make "the date," of all things, a source with <span class="mono">baseline</span>/<span class="mono">update</span>, rather than just hard-code "today is X" at the start and be done?</strong></p>
<pre class="code"><span class="cm">// simplified from system-context/builtins.ts — a source, under ten lines</span>
SystemContext.<span class="fn">make</span>({
  key: SystemContext.Key.<span class="fn">make</span>(<span class="st">"core/date"</span>),
  codec: Schema.<span class="fn">toCodecJson</span>(Schema.String),
  load: DateTime.nowAsDate.<span class="fn">pipe</span>(Effect.<span class="fn">map</span>((d) =&gt; d.<span class="fn">toDateString</span>())),
  baseline: (date) =&gt; <span class="st">`Today's date: ${'$'}{date}`</span>,            <span class="cm">// first time</span>
  update: (_prev, date) =&gt; <span class="st">`Today's date is now: ${'$'}{date}`</span>,  <span class="cm">// after crossing a day</span>
})</pre>
<p>The answer: <strong>because the date changes</strong>. A session may chat from evening into the next morning — <strong>crossing midnight</strong>. If the date is hard-coded at the start, then past midnight the model's "today" is <strong>wrong</strong>, possibly mistaking yesterday for today, miscounting a deadline by a day. Make the date a source, and the next round's <span class="mono">prepare</span> reconcile finds "the date changed," auto-publishing an update — so the model reads "Today's date is now: ...," the clock seamlessly corrected. <strong>Even "the date," seemingly unchanging, is "alive" in a possibly-long session</strong> — exactly the meaning of the past five lessons' incremental mechanism: it doesn't care about size, any "possibly-changing" environment info can be kept fresh elegantly by the same source framework.</p>
<div class="timeline">
  <div class="tl-item"><span class="tl-time">Mon 21:00</span><span class="tl-desc">session starts → baseline: "Today's date: Mon Jun 23"</span></div>
  <div class="tl-item"><span class="tl-time">Mon 23:30</span><span class="tl-desc">still chatting → reconcile: date unchanged → Unchanged, silent</span></div>
  <div class="tl-item"><span class="tl-time">★ midnight 00:00</span><span class="tl-desc">the date changed!</span></div>
  <div class="tl-item"><span class="tl-time">Tue 00:15</span><span class="tl-desc">next round → reconcile: changed → update: "Today's date is now: Tue Jun 24"</span></div>
</div>
<div class="cols">
  <div class="col"><h4>baseline: "Today's date: X"</h4><p>First notification. The wording reads like <strong>stating a fact</strong>.</p></div>
  <div class="col"><h4>update: "Today's date is now: X"</h4><p>After crossing a day. That <strong>now</strong> signals to the model "this is a <strong>change</strong>."</p></div>
</div>
<p>Savor the <strong>wording difference</strong> between <span class="mono">baseline</span> and <span class="mono">update</span>: first is "Today's date: X" (flatly stated), after change is "Today's date is now: X" — the extra <span class="mono">now</span> gently reminds the model "note, this is newly changed." Same on the environment source: baseline says "Here is some useful information…," update says "The environment …is now:". This little care of <strong>using the wording itself to distinguish "initial" from "change"</strong> seems trivial but makes the model's reading more natural — it senses from between the lines "oh, this changed later," rather than yet another repetition. <strong>Good context isn't only correct in content but correct in the tone of "is this new news."</strong></p>
<p>This detail is so small almost no one would notice, yet it's the purest expression of "considering the reader" — only here the "reader" is an LLM. A careless implementation could use identical wording for baseline and update; the info gets through either way. But opencode spent this extra care: making the "first statement" read like a statement, the "subsequent change" read like a change. To the model, "now" is a faint but clear signal helping it separate "a restatement of the current state" from "a change just happened." <strong>Keeping the user's (even an AI's) reading experience in mind, refusing to be casual about even a single word's choice — this near-obsessive thoughtfulness is often the subtle, decisive watershed between "works" and "works well."</strong></p>

<h2>And instructions: InstructionContext</h2>
<p>Beyond environment and date, there's a "heavier" built-in source — <span class="mono">InstructionContext</span> (<span class="mono">instruction-context.ts</span>). It handles the project's <strong>standing instructions</strong>: files like <span class="mono">AGENTS.md</span>, stating "what conventions this project uses, what's taboo, how it wants the agent to work." These instructions are also wrapped into a source, registered into the same registry — so it participates in baseline, increment, projection <strong>on equal footing</strong> with environment and date. <strong>Change the project conventions (you edit AGENTS.md), and it too can be incrementally told to the model, just like a directory change.</strong></p>
<p>Put these three sources together and opencode's "world fed to the model" has flesh and blood: <strong>environment</strong> tells it "where I am, what platform," <strong>date</strong> tells it "when it is now," <strong>instructions</strong> tell it "this project's rules." Each is an independent source, each observing, each incrementing, each updating in place, finally gathered by the registry into one complete, ordered, incrementable system context. <strong>This is the full look of the past five lessons' abstraction landed in practice.</strong></p>
<p>One more thing to mull: these three sources are opencode's <strong>built-ins</strong>, but they stand on <strong>completely equal footing</strong> with "a source some plugin contributes in future." <span class="mono">core/environment</span> enjoys no privilege for being surnamed "core" — it too dutifully <span class="mono">make</span>s a <span class="mono">Source</span> and registers into the same registry. This means: <strong>what opencode uses itself and what it opens to third-party extension are the same mechanism</strong>. This "insiders and outsiders eat from the same pot" design (the industry calls it dogfooding — eating your own dog food) is the best proof of a healthy extension mechanism: because the framework's authors live on it themselves, it can't be a perfunctory, second-class extension point. Want to add a "current branch name" or "last build status" context source to opencode in future? You'd write the exact same five lines as <span class="mono">core/date</span> — that's the most generous promise of a good abstraction.</p>
<div class="cellgroup">
  <div class="cell"><div class="k">core/environment</div><div class="v">"where I am": directory, project root, git, platform</div></div>
  <div class="cell"><div class="k">core/date</div><div class="v">"when it is now": today's date (updates across days)</div></div>
  <div class="cell"><div class="k">InstructionContext</div><div class="v">"the rules here": standing instructions like AGENTS.md</div></div>
</div>

<div class="card macro">
  <div class="tag">🗺️ The big picture</div>
  <p>This lesson cashes the first five lessons' abstraction <strong>into a few real, minimal sources</strong>:</p>
  <ul>
    <li><strong>Source definitions are astonishingly short</strong>: a dozen lines declaring key/codec/load/baseline/update, the heavy lifting all absorbed by the framework (codec-derived equality, registry, epoch, projection) — the touchstone of "good abstraction."</li>
    <li><strong>core/environment</strong>: <span class="mono">&lt;env&gt;</span> tags wrapping directory/project-root/git/platform — the bare minimum an agent must know about "where am I."</li>
    <li><strong>core/date</strong>: even "the date" is a source, because a session may <strong>cross midnight</strong> — any "possibly-changing" info deserves keeping fresh by the source framework.</li>
    <li><strong>Wording distinction</strong>: baseline flat, update uses "now" to lightly flag "this is a change" — even the tone considers the model.</li>
    <li><strong>InstructionContext</strong>: project instructions like AGENTS.md are also an equal-footing source.</li>
  </ul>
  <p>By here, system context's "normal state" is fully covered: abstraction (L21-23), landing in the session (L24), mid-conversation update (L25), concrete built-ins (this lesson). Part 5 has only the last and hardest puzzle piece left — the <span class="mono">AgentReplacementBlocked</span> Lesson 24 kept naming but never unpacked: <strong>when you switch an agent mid-way, what becomes of the context epoch belonging to the old agent? Why is "replacement" sometimes "blocked"?</strong> That's the next lesson, Part 5's finale — <strong>Agent switch & epoch replacement (Lesson 27)</strong>.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source detail</div>
  <p>How simple is a complete source definition? See <span class="mono">core/environment</span> in full — five fields, not a wasted word:</p>
  <pre class="code"><span class="cm">// simplified from system-context/builtins.ts</span>
SystemContext.<span class="fn">make</span>({
  key: SystemContext.Key.<span class="fn">make</span>(<span class="st">"core/environment"</span>),     <span class="cm">// unique identity</span>
  codec: Schema.<span class="fn">toCodecJson</span>(Schema.String),               <span class="cm">// value is a string</span>
  load: Effect.<span class="fn">succeed</span>(environment),                      <span class="cm">// how to observe</span>
  baseline: (env) =&gt; <span class="st">`Here is ...:\n${'$'}{env}`</span>,            <span class="cm">// first-time full text</span>
  update: (_prev, env) =&gt; <span class="st">`The environment ...is now:\n${'$'}{env}`</span>, <span class="cm">// change text</span>
})</pre>
  <p>Just these five lines. <strong>Not</strong> a line writing "how to serialize" (one point to a <span class="mono">codec</span>, and Lesson 22's encode/decode/equivalent fall into place automatically); <strong>not</strong> a line writing "how to register, sort, parallelize" (handed to Lesson 23's registry); <strong>not</strong> a line writing "how to persist, pin a sequence, project into a System message" (handed to Lessons 24, 25). A source author need only answer five most-essential questions: <strong>what it's called, what the value looks like, how to observe, how to say it first time, how to say it on change</strong>. Everything else, the past five lessons' machinery answers for them. <strong>The crispness of these five lines is bought by all the prior complexity — complexity absorbed into the framework, simplicity left for the user.</strong></p>
  <div class="cols">
    <div class="col"><h4>what the framework carries (unseen)</h4><p>encode/decode/equivalent equality, scoped registration, sort by key, concurrent observe, epoch persistence, pin baselineSeq, project into a System message, in-place positioning… a whole heap.</p></div>
    <div class="col"><h4>what the source author writes (just five lines)</h4><p>key, codec, load, baseline, update. Answer "name/value shape/how to observe/first-time/on-change," done.</p></div>
  </div>
  <div class="cellgroup">
    <div class="cell"><div class="k">key</div><div class="v">"core/date" — unique identity</div></div>
    <div class="cell"><div class="k">codec</div><div class="v">Schema.String — value is a string</div></div>
    <div class="cell"><div class="k">load</div><div class="v">get today's date — how to observe</div></div>
    <div class="cell"><div class="k">baseline / update</div><div class="v">"Today's date: X" / "…is now: X" — first-time / on-change</div></div>
  </div>
</div>

<div class="card key">
  <div class="tag">🎯 Key points</div>
  <ul>
    <li>The first five lessons' abstraction cashes into real sources that are <strong>astonishingly simple</strong>: a dozen lines declaring <strong>key/codec/load/baseline/update</strong>, the heavy lifting all absorbed by the framework — the touchstone of "good abstraction."</li>
    <li><strong>core/environment</strong>: <span class="mono">&lt;env&gt;</span> tags wrapping <strong>directory, project root, is-git, platform</strong> — the bare minimum an agent must know about "where am I."</li>
    <li><strong>core/date</strong>: even "the date" is a source, because a session may <strong>cross midnight</strong> — any "possibly-changing" info deserves keeping fresh by the source framework.</li>
    <li><strong>Wording distinguishes initial from change</strong>: baseline "Today's date: X" flat, update "Today's date is now: X" with "now" lightly flagging the change — even the tone considers the model.</li>
    <li><strong>InstructionContext</strong> (project instructions like AGENTS.md) is also an equal-footing source: environment "where I am," date "when," instructions "the rules" — together weaving the world the model is in.</li>
  </ul>
</div>
""",
}
LESSON_27 = wip('Agent 切换与 Epoch 替换', 'Agent switch & epoch')
