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
LESSON_22 = wip('Context Source', 'Context Sources')
LESSON_23 = wip('System Context Registry', 'The context registry')
LESSON_24 = wip('Context Epoch', 'The Context Epoch')
LESSON_25 = wip('会话中系统消息', 'Mid-conversation messages')
LESSON_26 = wip('内置 Context Sources', 'Built-in sources')
LESSON_27 = wip('Agent 切换与 Epoch 替换', 'Agent switch & epoch')
