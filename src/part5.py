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
LESSON_23 = wip('System Context Registry', 'The context registry')
LESSON_24 = wip('Context Epoch', 'The Context Epoch')
LESSON_25 = wip('会话中系统消息', 'Mid-conversation messages')
LESSON_26 = wip('内置 Context Sources', 'Built-in sources')
LESSON_27 = wip('Agent 切换与 Epoch 替换', 'Agent switch & epoch')
