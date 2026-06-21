"""Part 4 (Part 4 · Session Core) content. Placeholders until M4 fills them in."""
from placeholder import wip

LESSON_14 = {
    "zh": r"""
<p class="lead">第三部分我们绕着大脑的外墙走了一圈，看清了所有客户端进出的那扇门。现在，<strong>推门进去</strong>。第四部分是整本书的<strong>第一个核心</strong>——会话引擎与 agent 循环：一个 prompt 进来后，是怎么一步步变成回答的。但在看「循环怎么转」之前，这一课得先教你<strong>循环操作的那些名词</strong>。就像读小说前要先认识主角，读 agent 引擎前，你得先认识它的三个基本数据结构：<strong>Session（会话）、Message（消息）、Part（部件）</strong>。这一课不讲流程，只建词汇——把这三个词的形状刻进脑子，后面六课才不至于满眼名词却不知所指。</p>
<p>为什么数据模型值得开篇专讲？因为<strong>opencode 的几乎一切，最后都落在这三层结构上</strong>。你在 TUI 里看到的每一行、SDK 取到的每个对象、数据库里存的每条记录、第 11 课那条事件流推送的每个更新——本质上都是在<strong>读写或变更 Session/Message/Part</strong>。把数据模型当成地基：地基的形状，决定了上面能盖出什么样的楼。读懂这三层怎么嵌套、各装什么，你就拿到了理解整个 core 的「坐标系」。</p>

<div class="card analogy">
  <div class="tag">🎬 生活类比</div>
  把一次会话想成一部<strong>正在拍摄的剧本</strong>。整部剧本（<strong>Session</strong>）有自己的档案：片名、隶属哪个项目、用哪位导演（agent）、哪台摄影机（model）、花了多少预算（cost/tokens）。剧本里是一段段<strong>台词块</strong>（<strong>Message</strong>）：有的是用户说的、有的是 AI 说的，还有系统旁白、场记备注……角色远不止两个。而每个 AI 的台词块，又不是一句平铺的话，而是由几种<strong>不同成分</strong>（<strong>Part</strong>）拼起来的：有「内心独白」（reasoning，AI 的思考）、有「说出口的台词」（text）、还有「去做一个动作」的指令（tool call）。最妙的是那个动作指令本身还会<strong>演一段小戏</strong>：从「准备做」到「正在做」再到「做完了/搞砸了」。看懂这部剧本的层层结构，你就看懂了 opencode 记录一切的方式。
</div>

<h2>Session：一次会话的档案袋</h2>
<p>最外层是 <span class="mono">Session.Info</span>（定义在 <span class="mono">session/schema.ts</span>）。它不装对话内容，只装这次会话的<strong>元数据</strong>——像一个贴满标签的档案袋。瞥一眼它的字段，一次会话的「身份」就全在这了：</p>
<div class="cellgroup">
  <div class="cell"><div class="k">id</div><div class="v">以 "ses_" 开头的品牌化 ID，全局唯一</div></div>
  <div class="cell"><div class="k">parentID</div><div class="v">父会话 —— 会话能从某条消息「分叉」出子会话</div></div>
  <div class="cell"><div class="k">projectID / agent / model</div><div class="v">隶属项目、用哪个 agent、哪个模型</div></div>
  <div class="cell"><div class="k">cost / tokens</div><div class="v">这次会话的账单：花了多少钱、各类 token 用量</div></div>
  <div class="cell"><div class="k">time / title / location</div><div class="v">创建/更新/归档时间、标题、所在位置</div></div>
</div>
<p>这里有个字段值得专门停一下：<span class="mono">parentID</span>。它的存在意味着会话不是一条孤立的直线，而能<strong>长成一棵树</strong>——你可以从某次对话的中途「分叉」出一个子会话，去试一条不同的路，而不污染原来那条。这种「可分叉」的能力，正是靠数据模型里一个小小的父指针撑起来的。还有 <span class="mono">cost</span> 和 <span class="mono">tokens</span>：把账单直接刻进会话的身份里，意味着「这次对话花了多少」永远是个<strong>一等公民</strong>，随时可查、随时可显示，而不是事后再去某个日志里扒。</p>
<p>另外注意 <span class="mono">location</span> 这个字段——它呼应了第二部分反复出现的「Location 作用域」。一次会话<strong>属于某个具体位置</strong>（哪个工作区、哪个目录），这把会话和它的运行环境绑定在了一起。档案袋上贴着「这份卷宗归哪个办公室管」，后面的模型解析、工具注册、文件系统访问，全要看这个位置标签行事。</p>
<p>还有一个容易被当成「废话」却很关键的观察：Session 里<strong>装的全是元数据，唯独没有对话内容本身</strong>。片名、预算、用了哪台摄影机都在，但一句台词都不在档案袋里。这是有意的分层——会话的「身份」很小、很稳定，能被廉价地列出来（想想 TUI 左边那列会话列表，加载它根本不需要把每次对话的几万字都读进来）；而真正庞大的对话内容，分开存在 Message 那一层，要看具体某次会话时才按需加载。<strong>把「轻的身份」和「重的内容」分开</strong>，是几乎所有能扛住规模的系统都会做的事，opencode 在最外层就把这条界线划清楚了。</p>

<h2>Message：八种角色，不止你和 AI</h2>
<p>会话里的内容，是一条条 <span class="mono">Message</span>。新手最容易的误解，是以为消息只有「用户说的」和「AI 说的」两种。打开 <span class="mono">session/message.ts</span> 末尾那个 <span class="mono">Schema.Union</span>，你会看到 <strong>Message 是个有八个成员的标签联合</strong>（tagged union，靠 <span class="mono">type</span> 字段区分）：</p>
<div class="cellgroup">
  <div class="cell"><div class="k">User</div><div class="v">用户的输入</div></div>
  <div class="cell"><div class="k">Assistant</div><div class="v">AI 的回复（本课重点，最复杂）</div></div>
  <div class="cell"><div class="k">System</div><div class="v">系统消息</div></div>
  <div class="cell"><div class="k">Synthetic</div><div class="v">合成消息（程序造的，非真人）</div></div>
  <div class="cell"><div class="k">Shell</div><div class="v">shell 相关</div></div>
  <div class="cell"><div class="k">Compaction</div><div class="v">压缩标记（长对话被概括，第 51 课）</div></div>
  <div class="cell"><div class="k">AgentSwitched / ModelSwitched</div><div class="v">中途换了 agent / 换了模型的记录</div></div>
</div>
<p>这八种里，<span class="mono">AgentSwitched</span> 和 <span class="mono">ModelSwitched</span> 特别能说明问题：<strong>「换了 agent」「换了模型」本身，也是会话历史里的一条消息</strong>。这不是把当前状态改个字段就完事，而是把「在这个时间点，我们从 A 模型切到了 B 模型」当成一个<strong>不可变的历史事件</strong>记下来。这种「一切皆消息、历史只追加」的取向，是后面第 15 课「事件溯源」和第 19 课「投影历史」的伏笔——会话的过去，是一长串只增不改的记录。用标签联合来建模，还有个直接好处：处理消息时 <span class="mono">switch (msg.type)</span>，编译器会<strong>逼你把八种都考虑到</strong>，漏一种就报错。</p>
<p>多花一秒想想「换模型也是一条消息」有多反直觉、又有多正确。最省事的写法，是在 Session 上放个 <span class="mono">currentModel</span> 字段，换模型时改一下——可那样一来，会话的历史就<strong>说谎</strong>了：你回看三天前那段对话，只会看到「现在的模型」，而不知道当时其实用的是另一个。把切换记成历史里的一个时间点，会话才能诚实地回答「在第 5 条消息时，我们用的是谁」。<strong>能不能忠实地重建过去的任意一刻</strong>，是 opencode 会话模型反复在守护的东西——而守护它的方式，就是绝不用「改写当前状态」去顶替「追加一条历史」。</p>

<h2>Part：一条 AI 回复里的几种成分</h2>
<p>现在放大最复杂、也最有意思的那种消息——<span class="mono">Assistant</span>。它的 <span class="mono">content</span> 字段<strong>不是一个字符串，而是一个数组</strong>：<span class="mono">AssistantContent</span> 的数组。而 <span class="mono">AssistantContent</span> 又是一个三选一的联合，对应一条 AI 回复里可能交错出现的三种<strong>成分（part）</strong>：</p>
<div class="cols">
  <div class="col"><h4>text · 说出口的话</h4><p>AI 真正输出给你看的文字回答。</p></div>
  <div class="col"><h4>reasoning · 内心独白</h4><p>AI 的思考过程（若模型支持），和最终答案分开存。</p></div>
  <div class="col"><h4>tool · 一个动作</h4><p>一次工具调用：名字、参数，以及它的执行状态。</p></div>
</div>
<p>「content 是 part 数组」这个设计，是理解整个 agent 体验的钥匙。为什么不直接存一大段字符串？因为一条 AI 回复，真实形态本就是<strong>交错的</strong>：它可能先想一会儿（reasoning），说两句（text），调个工具（tool），看了结果再接着说（text）……把这些拆成有序的 part 数组，系统就能<strong>分别对待每一种</strong>：思考折叠起来、文字正常显示、工具调用画成一张带状态的卡片。第 11 课那条事件流之所以能让你看到 AI「一个字一个字往外蹦、工具状态实时翻牌」，正是因为底层是这样一个<strong>可逐 part 增量更新</strong>的结构，而不是一锤子定音的字符串。</p>
<p>把这件事和别的聊天工具对比一下就更清楚了。很多简单的对话应用，一条 AI 消息就是一个字符串字段——思考、工具、文字全糊成一团纯文本，想把工具调用单独画成卡片？做不到，因为信息在存的时候就被压扁了。opencode 反其道而行：<strong>在最源头就把一条回复拆成带类型的零件</strong>，于是「能不能漂亮地渲染」「能不能实时更新某一块」这些问题，在数据进库的那一刻就已经有了肯定的答案。这又是那个反复出现的主题——<strong>形状定得好，下游全都顺；形状压扁了，再多的前端努力也补不回丢掉的结构</strong>。reasoning 和 text 分开存也是同理：它让客户端可以选择「默认折叠思考、只显示答案」，而这只有在两者本就是不同 part 时才办得到。</p>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">外</span><span class="name">Session</span></div><div class="ld">一次会话的档案袋（元数据）</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">中</span><span class="name">Message ×8 种</span></div><div class="ld">User / Assistant / System / …</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">内</span><span class="name">Part ×3 种</span></div><div class="ld">text / reasoning / tool（Assistant 的 content 数组）</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">芯</span><span class="name">ToolState ×4 态</span></div><div class="ld">tool part 内部的状态机（下一节）</div></div>
</div>

<h2>ToolState：一个工具调用的一生</h2>
<p>三种 part 里，<span class="mono">tool</span> 最特别——它不是个静态的「调用记录」，而内含一个<strong>会随时间推进的状态</strong>。<span class="mono">AssistantTool</span> 有个 <span class="mono">state</span> 字段，类型是 <span class="mono">ToolState</span>，又是一个标签联合，描述这次工具调用走过的<strong>四个阶段</strong>：</p>
<div class="timeline">
  <div class="tl-item"><span class="tl-time">pending</span><span class="tl-desc">准备调用 —— 参数还是原始字符串，尚未执行</span></div>
  <div class="tl-item"><span class="tl-time">running</span><span class="tl-desc">正在执行 —— 参数已解析，开始产出 content</span></div>
  <div class="tl-item"><span class="tl-time">completed</span><span class="tl-desc">成功 —— 带 result、structured、attachments、outputPaths</span></div>
  <div class="tl-item"><span class="tl-time">error</span><span class="tl-desc">失败 —— 带 error 与已产出的 content</span></div>
</div>
<p>把工具调用的「一生」直接编码进数据模型，是个深思熟虑的决定。它意味着<strong>「这个工具现在处于什么阶段」是一个一等的、可查询的事实</strong>，而不是散落在某处的临时变量。于是 TUI 能照着 state 实时画出「⏳ 正在运行 / ✓ 完成 / ✗ 出错」；agent 循环能据此知道哪些工具还没回来、要不要等；历史重放（第 19 课）能精确复现每个工具当时的状态。注意四个阶段携带的字段是<strong>递增</strong>的：<span class="mono">pending</span> 只有原始 input，<span class="mono">running</span> 多了解析后的 input 和流式 content，<span class="mono">completed</span> 再添上 result 和产物路径。<strong>状态往前走一步，已知的信息就多一层</strong>——这正是一个状态机最自然的样子。</p>
<p>退一步看，你会发现这一整套数据模型贯穿着同一种气质：<strong>把「正在发生的事」结构化、显性化、可追踪化</strong>。会话有账单、消息有种类、回复有成分、工具有状态——没有哪一样是含混地塞进一个大字符串里的。这种近乎执拗的「给每样东西一个明确的形状」，正是 opencode 能把一个本质上混沌、流动、随时可能出错的 agent 过程，管理得井井有条的根本原因。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <p>这一课为整个第四部分建好了<strong>词汇表</strong>。三层嵌套，记住它们：</p>
  <ul>
    <li><strong>Session</strong>：一次会话的档案袋——id（可分叉的 parentID）、项目/agent/model、账单、位置。</li>
    <li><strong>Message（8 种）</strong>：会话内容的基本单位，标签联合——连「换了 agent/model」都是一条消息。</li>
    <li><strong>Part（3 种）</strong>：Assistant 回复的 content 是 text/reasoning/tool 的<strong>有序数组</strong>，支持交错与增量更新。</li>
    <li><strong>ToolState（4 态）</strong>：tool part 内的状态机，pending→running→completed/error，信息逐阶段递增。</li>
  </ul>
  <p>带着这套词汇，下一课我们看这些消息是怎么<strong>被安全地「收」进会话</strong>的——一个事件溯源的输入收件箱（第 15 课），它解释了为什么 opencode 的会话历史能做到「只追加、不丢失、可重放」。</p>
  <div class="flow">
    <div class="node">你输入 prompt<span class="sub">"帮我重构这个函数"</span></div>
    <div class="arrow">→</div>
    <div class="node">Session<span class="sub">归档到某个会话</span></div>
    <div class="arrow">→</div>
    <div class="node">User Message<span class="sub">记下你说的话</span></div>
    <div class="arrow">→</div>
    <div class="node">Assistant Message<span class="sub">content: [reasoning, text, tool…]</span></div>
  </div>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p>Assistant 消息「content 是 part 数组、tool part 内含状态机」的形状，浓缩在 <span class="mono">message.ts</span> 这几个声明里：</p>
  <pre class="code"><span class="cm">// 简化自 session/message.ts</span>
<span class="kw">class</span> <span class="fn">Assistant</span> {
  type: <span class="st">"assistant"</span>
  content: AssistantContent[]   <span class="cm">// ← 不是 string，是 part 数组</span>
}
<span class="kw">const</span> AssistantContent = Schema.<span class="fn">Union</span>([
  AssistantText, AssistantReasoning, AssistantTool ])  <span class="cm">// text/reasoning/tool</span>

<span class="kw">class</span> <span class="fn">AssistantTool</span> {
  type: <span class="st">"tool"</span>; name: <span class="kw">string</span>
  state: ToolState   <span class="cm">// ← Pending|Running|Completed|Error 状态机</span>
}</pre>
  <p>三层联合层层嵌套：<span class="mono">Message</span> 是八选一，其中 <span class="mono">Assistant.content</span> 是三种 part 的数组，其中 <span class="mono">tool</span> part 的 <span class="mono">state</span> 又是四选一。每一层都是<strong>标签联合</strong>，每一层都让编译器替你守住「分支别漏」。数据的形状里，已经写好了处理它的纪律。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li>core 的一切最终都落在三层结构上：<strong>Session ⊃ Message ⊃ Part</strong>；读懂它们就拿到了理解整个引擎的坐标系。</li>
    <li><strong>Session.Info</strong> 是会话的元数据档案袋：id、可分叉的 <span class="mono">parentID</span>、项目/agent/model、cost/tokens 账单、location 作用域。</li>
    <li><strong>Message 是 8 成员的标签联合</strong>（不止 user/assistant）：连「换 agent/换 model」都作为不可变历史消息记下——事件溯源的伏笔。</li>
    <li><strong>Assistant 的 content 是 part 数组</strong>（text/reasoning/tool），支持思考/文字/工具<strong>交错与逐 part 增量更新</strong>——这是实时 UI 的根。</li>
    <li><strong>tool part 内含 ToolState 状态机</strong>（pending→running→completed/error），信息逐阶段递增；工具调用的「一生」是一等可查的事实。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">In Part 3 we walked the brain's outer wall and saw the door every client passes through. Now, <strong>push the door open</strong>. Part 4 is the book's <strong>first core</strong> — the session engine and agent loop: how a prompt, once it comes in, turns step by step into an answer. But before watching "how the loop turns," this lesson must teach you <strong>the nouns the loop operates on</strong>. Just as you meet the protagonists before reading a novel, before the agent engine you must meet its three basic data structures: <strong>Session, Message, Part</strong>. This lesson isn't about flow, only vocabulary — carve the shapes of these three words into your mind, and the next six lessons won't drown you in undefined terms.</p>
<p>Why does the data model deserve its own opening lesson? Because <strong>almost everything in opencode ultimately lands on these three layers</strong>. Every line you see in the TUI, every object the SDK fetches, every record stored in the database, every update pushed by Lesson 11's event stream — at heart they all <strong>read, write, or mutate Session/Message/Part</strong>. Treat the data model as the foundation: the foundation's shape decides what building can rise on it. Understand how these three layers nest and what each holds, and you've got the "coordinate system" for understanding the whole core.</p>

<div class="card analogy">
  <div class="tag">🎬 Analogy</div>
  Think of a conversation as a <strong>screenplay in production</strong>. The whole screenplay (<strong>Session</strong>) has its own file: title, which project it belongs to, which director (agent), which camera (model), how much budget it spent (cost/tokens). Inside are <strong>blocks of lines</strong> (<strong>Message</strong>): some spoken by the user, some by the AI, plus system narration, script notes… far more than two roles. And each AI line-block isn't one flat sentence, but assembled from several <strong>different components</strong> (<strong>Part</strong>): an "inner monologue" (reasoning, the AI's thinking), the "spoken line" (text), and an instruction to "go do an action" (tool call). Best of all, that action instruction itself <strong>plays a little scene</strong>: from "about to do it," to "doing it," to "done / botched it." See this screenplay's layered structure and you've seen how opencode records everything.
</div>

<h2>Session: a conversation's file folder</h2>
<p>The outermost layer is <span class="mono">Session.Info</span> (defined in <span class="mono">session/schema.ts</span>). It holds no conversation content, only this session's <strong>metadata</strong> — like a folder covered in labels. Glance at its fields and a session's "identity" is all here:</p>
<div class="cellgroup">
  <div class="cell"><div class="k">id</div><div class="v">a branded ID starting with "ses_", globally unique</div></div>
  <div class="cell"><div class="k">parentID</div><div class="v">parent session — a session can "fork" a child from some message</div></div>
  <div class="cell"><div class="k">projectID / agent / model</div><div class="v">which project, which agent, which model</div></div>
  <div class="cell"><div class="k">cost / tokens</div><div class="v">this session's bill: money spent, token usage by kind</div></div>
  <div class="cell"><div class="k">time / title / location</div><div class="v">created/updated/archived time, title, where it lives</div></div>
</div>
<p>One field is worth pausing on: <span class="mono">parentID</span>. Its existence means a session isn't a lone straight line but can <strong>grow into a tree</strong> — you can "fork" a child session midway through a conversation to try a different path without polluting the original. This "forkable" ability rests on one small parent pointer in the data model. And <span class="mono">cost</span> and <span class="mono">tokens</span>: carving the bill straight into the session's identity means "how much did this conversation cost" is forever a <strong>first-class citizen</strong>, queryable and displayable anytime, not something to dig out of a log afterward.</p>
<p>Note also the <span class="mono">location</span> field — it echoes Part 2's recurring "Location scope." A session <strong>belongs to a specific location</strong> (which workspace, which directory), binding the session to its runtime environment. The folder is labeled "which office owns this dossier," and the later model resolution, tool registry, and filesystem access all act according to this location tag.</p>
<p>Here's an observation easily dismissed as obvious yet quite crucial: Session holds <strong>all metadata and nothing of the conversation content itself</strong>. Title, budget, which camera was used — all there, but not one line of dialogue is in the folder. This is deliberate layering — a session's "identity" is small and stable, cheaply listable (think of that session list down the TUI's left side; loading it shouldn't require reading every conversation's tens of thousands of words). The truly bulky conversation content lives separately at the Message layer, loaded on demand only when you open a specific session. <strong>Separating "light identity" from "heavy content"</strong> is what nearly every system that survives scale does, and opencode draws this line cleanly at the outermost layer.</p>

<h2>Message: eight roles, not just you and the AI</h2>
<p>A session's content is a sequence of <span class="mono">Message</span>s. The beginner's easiest misconception is thinking messages come in only two kinds, "user said" and "AI said." Open the <span class="mono">Schema.Union</span> at the end of <span class="mono">session/message.ts</span> and you'll see <strong>Message is a tagged union with eight members</strong> (distinguished by the <span class="mono">type</span> field):</p>
<div class="cellgroup">
  <div class="cell"><div class="k">User</div><div class="v">the user's input</div></div>
  <div class="cell"><div class="k">Assistant</div><div class="v">the AI's reply (this lesson's focus, the most complex)</div></div>
  <div class="cell"><div class="k">System</div><div class="v">system message</div></div>
  <div class="cell"><div class="k">Synthetic</div><div class="v">synthetic message (program-made, not a real person)</div></div>
  <div class="cell"><div class="k">Shell</div><div class="v">shell-related</div></div>
  <div class="cell"><div class="k">Compaction</div><div class="v">compaction marker (long convo summarized, Lesson 51)</div></div>
  <div class="cell"><div class="k">AgentSwitched / ModelSwitched</div><div class="v">a record of switching agent / model midway</div></div>
</div>
<p>Among the eight, <span class="mono">AgentSwitched</span> and <span class="mono">ModelSwitched</span> are especially telling: <strong>"switched agent" and "switched model" are themselves a message in the session history</strong>. This isn't done by editing a current-state field; it records "at this point in time, we switched from model A to model B" as an <strong>immutable historical event</strong>. This "everything is a message, history only appends" stance foreshadows Lesson 15's "event sourcing" and Lesson 19's "projected history" — a session's past is a long, append-only record. Modeling with a tagged union also has a direct benefit: when handling messages with <span class="mono">switch (msg.type)</span>, the compiler <strong>forces you to consider all eight</strong>, and missing one is an error.</p>
<p>Take a second to feel how counterintuitive yet correct "a model switch is a message" is. The lazy way is to put a <span class="mono">currentModel</span> field on the Session and edit it on switch — but then the session's history <strong>lies</strong>: look back at a conversation from three days ago and you'd only see "the current model," not knowing it actually used a different one then. By recording the switch as a point in history, the session can honestly answer "at message 5, which one were we using." <strong>Whether it can faithfully reconstruct any past moment</strong> is what opencode's session model keeps guarding — and the way it guards it is by never substituting "rewrite current state" for "append a history entry."</p>

<h2>Part: the components inside one AI reply</h2>
<p>Now zoom into the most complex and most interesting message kind — <span class="mono">Assistant</span>. Its <span class="mono">content</span> field <strong>is not a string but an array</strong>: an array of <span class="mono">AssistantContent</span>. And <span class="mono">AssistantContent</span> is itself a three-way union, for the three <strong>parts</strong> that may interleave in one AI reply:</p>
<div class="cols">
  <div class="col"><h4>text · spoken words</h4><p>the text answer the AI actually outputs for you to read.</p></div>
  <div class="col"><h4>reasoning · inner monologue</h4><p>the AI's thinking process (if the model supports it), stored apart from the final answer.</p></div>
  <div class="col"><h4>tool · an action</h4><p>one tool call: name, params, and its execution state.</p></div>
</div>
<p>The "content is a part array" design is the key to understanding the whole agent experience. Why not just store one big string? Because an AI reply's real form is inherently <strong>interleaved</strong>: it might think a while (reasoning), say a couple lines (text), call a tool (tool), see the result and keep talking (text)… Split into an ordered part array, the system can <strong>treat each kind separately</strong>: fold up the thinking, show text normally, draw a tool call as a status-bearing card. Lesson 11's event stream can show the AI "spitting out one character at a time, tool status flipping live" precisely because the underlying structure is one that <strong>updates incrementally part by part</strong>, not a one-shot string.</p>
<p>Contrast this with other chat tools and it's clearer. Many simple conversation apps make an AI message one string field — thinking, tools, text all mashed into plain text; want to draw the tool call as its own card? Can't, because the information was flattened at storage time. opencode does the opposite: <strong>it splits a reply into typed pieces right at the source</strong>, so questions like "can this render nicely" and "can a single block update in real time" already have a yes the moment data enters the store. This is that recurring theme again — <strong>get the shape right and everything downstream flows; flatten the shape and no amount of frontend effort recovers the lost structure</strong>. Storing reasoning and text apart is the same logic: it lets clients choose "fold thinking by default, show only the answer," which is only possible when the two are distinct parts to begin with.</p>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">outer</span><span class="name">Session</span></div><div class="ld">a conversation's file folder (metadata)</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">mid</span><span class="name">Message ×8 kinds</span></div><div class="ld">User / Assistant / System / …</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">inner</span><span class="name">Part ×3 kinds</span></div><div class="ld">text / reasoning / tool (Assistant's content array)</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">core</span><span class="name">ToolState ×4 states</span></div><div class="ld">the state machine inside a tool part (next section)</div></div>
</div>

<h2>ToolState: the life of one tool call</h2>
<p>Of the three parts, <span class="mono">tool</span> is the most special — it isn't a static "call record" but contains a <strong>state that advances over time</strong>. <span class="mono">AssistantTool</span> has a <span class="mono">state</span> field of type <span class="mono">ToolState</span>, again a tagged union, describing the <strong>four stages</strong> a tool call passes through:</p>
<div class="timeline">
  <div class="tl-item"><span class="tl-time">pending</span><span class="tl-desc">about to call — args still a raw string, not yet executed</span></div>
  <div class="tl-item"><span class="tl-time">running</span><span class="tl-desc">executing — args parsed, starting to produce content</span></div>
  <div class="tl-item"><span class="tl-time">completed</span><span class="tl-desc">success — with result, structured, attachments, outputPaths</span></div>
  <div class="tl-item"><span class="tl-time">error</span><span class="tl-desc">failed — with error and the content produced so far</span></div>
</div>
<p>Encoding a tool call's "life" straight into the data model is a deliberate decision. It means <strong>"what stage is this tool in now" is a first-class, queryable fact</strong>, not a temp variable scattered somewhere. So the TUI can draw "⏳ running / ✓ done / ✗ error" live from the state; the agent loop can know which tools haven't returned and whether to wait; history replay (Lesson 19) can reproduce each tool's state at the time exactly. Note the fields each stage carries are <strong>incremental</strong>: <span class="mono">pending</span> has only the raw input, <span class="mono">running</span> adds the parsed input and streaming content, <span class="mono">completed</span> further adds result and output paths. <strong>Step the state forward and the known information gains another layer</strong> — exactly what a state machine looks like at its most natural.</p>
<p>Step back and you'll find this whole data model is suffused with one temperament: <strong>making "what's happening" structured, explicit, and traceable</strong>. Sessions have bills, messages have kinds, replies have components, tools have states — none of it vaguely stuffed into one big string. This almost obstinate "give everything a definite shape" is the fundamental reason opencode can keep an inherently chaotic, flowing, error-prone agent process so orderly.</p>

<div class="card macro">
  <div class="tag">🗺️ The big picture</div>
  <p>This lesson builds the <strong>vocabulary</strong> for all of Part 4. Three nested layers — remember them:</p>
  <ul>
    <li><strong>Session</strong>: a conversation's file folder — id (forkable parentID), project/agent/model, the bill, location.</li>
    <li><strong>Message (8 kinds)</strong>: the basic unit of session content, a tagged union — even "switched agent/model" is a message.</li>
    <li><strong>Part (3 kinds)</strong>: an Assistant reply's content is an <strong>ordered array</strong> of text/reasoning/tool, supporting interleaving and incremental updates.</li>
    <li><strong>ToolState (4 states)</strong>: the state machine inside a tool part, pending→running→completed/error, info incremental by stage.</li>
  </ul>
  <p>Armed with this vocabulary, next lesson we see how these messages are <strong>safely "received" into a session</strong> — an event-sourced input inbox (Lesson 15), which explains why opencode's session history can be "append-only, never lost, replayable."</p>
  <div class="flow">
    <div class="node">you type a prompt<span class="sub">"refactor this function for me"</span></div>
    <div class="arrow">→</div>
    <div class="node">Session<span class="sub">filed under some session</span></div>
    <div class="arrow">→</div>
    <div class="node">User Message<span class="sub">records what you said</span></div>
    <div class="arrow">→</div>
    <div class="node">Assistant Message<span class="sub">content: [reasoning, text, tool…]</span></div>
  </div>
</div>

<div class="card detail">
  <div class="tag">🔬 Source detail</div>
  <p>The Assistant message's shape — "content is a part array, the tool part holds a state machine" — is condensed in these declarations in <span class="mono">message.ts</span>:</p>
  <pre class="code"><span class="cm">// simplified from session/message.ts</span>
<span class="kw">class</span> <span class="fn">Assistant</span> {
  type: <span class="st">"assistant"</span>
  content: AssistantContent[]   <span class="cm">// ← not string, a part array</span>
}
<span class="kw">const</span> AssistantContent = Schema.<span class="fn">Union</span>([
  AssistantText, AssistantReasoning, AssistantTool ])  <span class="cm">// text/reasoning/tool</span>

<span class="kw">class</span> <span class="fn">AssistantTool</span> {
  type: <span class="st">"tool"</span>; name: <span class="kw">string</span>
  state: ToolState   <span class="cm">// ← Pending|Running|Completed|Error state machine</span>
}</pre>
  <p>Three unions nest layer in layer: <span class="mono">Message</span> is one-of-eight, within which <span class="mono">Assistant.content</span> is an array of three part kinds, within which the <span class="mono">tool</span> part's <span class="mono">state</span> is one-of-four. Every layer is a <strong>tagged union</strong>, every layer makes the compiler guard "don't miss a branch" for you. The discipline for handling the data is already written into the data's shape.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key points</div>
  <ul>
    <li>Everything in core ultimately lands on three layers: <strong>Session ⊃ Message ⊃ Part</strong>; understand them and you have the coordinate system for the whole engine.</li>
    <li><strong>Session.Info</strong> is the session's metadata folder: id, forkable <span class="mono">parentID</span>, project/agent/model, the cost/tokens bill, location scope.</li>
    <li><strong>Message is an 8-member tagged union</strong> (not just user/assistant): even "switch agent/model" is recorded as an immutable history message — foreshadowing event sourcing.</li>
    <li><strong>An Assistant's content is a part array</strong> (text/reasoning/tool), supporting <strong>interleaving and per-part incremental updates</strong> — the root of the real-time UI.</li>
    <li><strong>A tool part holds a ToolState machine</strong> (pending→running→completed/error), info incremental by stage; a tool call's "life" is a first-class queryable fact.</li>
  </ul>
</div>
""",
}
LESSON_15 = wip('事件溯源输入收件箱', 'The event-sourced inbox')
LESSON_16 = wip('运行协调器', 'The run coordinator')
LESSON_17 = wip('V2 agent 循环', 'The V2 agent loop')
LESSON_18 = wip('工具调用与 FiberSet', 'Tool calls & FiberSet')
LESSON_19 = wip('投影历史', 'Projected history')
LESSON_20 = wip('有界步数与错误处理', 'Bounded steps & errors')
