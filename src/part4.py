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
LESSON_15 = {
    "zh": r"""
<p class="lead">上一课我们认识了 Session/Message/Part 这三个名词。这一课要回答一个看似简单、实则暗藏凶险的问题：当你按下回车、一个 prompt 飞向 server 时，opencode 是怎么<strong>把它「收下」</strong>的？最天真的答案是「马上拿去跑模型」——但这恰恰是 opencode <strong>坚决不做</strong>的。它先把你的 prompt <strong>当成一个不可变的事件，原原本本记进一个叫「收件箱」的地方</strong>，拿到一个序号，<strong>然后才</strong>不紧不慢地安排去执行。这一课就讲这个「先入账、再执行」的设计——它叫<strong>事件溯源的输入收件箱</strong>，是 opencode 会话引擎能做到「崩了不丢、重试不乱、并发不抢」的根。</p>
<p>为什么「收 prompt」这件小事值得专讲？因为它是<strong>持久与执行的分水岭</strong>。设想反面：如果 prompt 一到就直接喂模型，那么——进程在「收到」和「开跑」之间崩了，prompt 就<strong>凭空蒸发</strong>；模型正说到一半，新 prompt 进来，两股逻辑<strong>当场打架</strong>；网络抖动重发了一次，同一句话被<strong>跑了两遍</strong>。opencode 用「先把输入落成持久事件」这一招，把这三个噩梦一次性消解。理解了这一课，你就理解了为什么 opencode 的会话<strong>经得起中断、重试和并发</strong>——而这正是一个严肃 agent 引擎和一个玩具脚本的分野。</p>

<div class="card analogy">
  <div class="tag">🍳 生活类比</div>
  想象一家忙碌餐厅的<strong>厨房挂单轨</strong>。你点了菜，服务员<strong>不会</strong>冲进后厨、拽住正在颠勺的大厨让他立刻做你的菜——那只会让手上的菜糊掉。服务员做的是：把你的订单写成一张<strong>带编号的票</strong>，「啪」地挂上轨道（这就是<strong>admit，入账</strong>）。这张票从此<strong>实打实地存在了</strong>：有编号（先来后到一目了然）、可持久（厨房就算着了火重启，票还挂在轨上，一张不丢）。大厨则在<strong>每道菜的干净间隙</strong>，从轨上取票来做（这叫<strong>promote，提单</strong>）。而且票还分两种：「<strong>插话式</strong>」——冲着正在做的那道菜喊一句「这盘不要葱！」，当场并进去；「<strong>排队式</strong>」——一张独立的新订单，乖乖等前面做完再轮到。看懂这条挂单轨，你就看懂了 opencode 收 prompt 的全部门道。
</div>

<h2>天真的做法，与它的三个噩梦</h2>
<p>先把「错误答案」摆出来，才显得正确答案珍贵。一个玩具版 agent 会这样写：<span class="mono">收到 prompt → 立刻 await 模型.run(prompt)</span>。简单直接，但它在三个地方会碎掉：</p>
<div class="cols">
  <div class="col"><h4>💥 崩溃丢失</h4><p>进程在「收到」与「开跑」之间挂了，prompt 没留下任何痕迹，凭空蒸发。</p></div>
  <div class="col"><h4>💥 并发打架</h4><p>模型正输出到一半，新 prompt 闯进来，两段执行抢同一个会话状态。</p></div>
  <div class="col"><h4>💥 重试翻倍</h4><p>网络抖动、客户端重发，同一句话被当成两次请求，跑两遍。</p></div>
</div>
<p>这三个噩梦的共同根源，是<strong>把「接收」和「执行」绑死成了一步</strong>。只要它们是同一个动作，接收的可靠性就被执行的脆弱性拖累——执行要调模型、要花几十秒、随时可能被打断，而接收本该是一瞬间、绝不该失败的事。opencode 的破局思路朴素而有力：<strong>把这一步劈成两步</strong>。先做那个又快又稳的「接收」，把它做成不可失败的持久记录；再把那个又慢又险的「执行」，交给后面从容调度。</p>
<p>这个「劈成两步」的思路，其实和数据库里的<strong>预写日志（WAL）</strong>如出一辙。数据库改数据前，从不直接动真正的数据页，而是先把「我打算这么改」写进一条只追加的日志——日志落盘了，这笔操作就<strong>赖不掉、丢不了</strong>，哪怕下一秒断电，重启后照日志重放即可。opencode 收 prompt 用的是同一套智慧：<span class="mono">admit</span> 就是那条预写日志，把「用户提了这个 prompt」这件事先<strong>稳稳钉死在持久层</strong>，至于真正费劲的执行，反而是可以事后从容补做的。<strong>先记录意图、再兑现意图</strong>——这条朴素的原则，是几乎所有「经得起崩溃」的系统共同的脊梁。</p>

<h2>admit：把 prompt 记成一个事件</h2>
<p>opencode 收 prompt 的真正入口是 <span class="mono">SessionInput.admit</span>（<span class="mono">session/input.ts</span>）。它<strong>不跑任何模型</strong>，只做一件事：把这个 prompt <strong>作为一个不可变事件发布出去</strong>，落进持久存储，并拿回一个序号。看它的骨架：</p>
<pre class="code"><span class="cm">// 简化自 session/input.ts</span>
<span class="kw">export const</span> admit = Effect.<span class="fn">fn</span>(<span class="kw">function</span>* (db, events, input) {
  <span class="kw">const</span> existing = <span class="kw">yield</span>* <span class="fn">find</span>(db, input.id)
  <span class="kw">if</span> (existing !== <span class="kw">undefined</span>) <span class="kw">return</span> existing   <span class="cm">// ① 幂等：同 id 直接返回旧的</span>
  <span class="kw">return</span> <span class="kw">yield</span>* events.<span class="fn">publish</span>(
    SessionEvent.PromptLifecycle.Admitted, {       <span class="cm">// ② 发布"已入账"事件</span>
      messageID: input.id, prompt: input.prompt, delivery: input.delivery, ...
    }).<span class="fn">pipe</span>(Effect.<span class="fn">map</span>((event) =&gt;
      <span class="kw">new</span> <span class="fn">Admitted</span>({ admittedSeq: event.seq, ... })))  <span class="cm">// ③ 序号=事件的 seq</span>
})</pre>
<p>三步，步步是关键。<strong>① 幂等</strong>：先按 <span class="mono">input.id</span> 查一遍，已经入过账就直接返回旧记录——于是<strong>重发同一个 prompt（同一个 id）只会入账一次</strong>，第三个噩梦当场消失。<strong>② 发布事件</strong>：admit 不是去改某个字段，而是 <span class="mono">publish</span> 一个 <span class="mono">PromptLifecycle.Admitted</span> 事件——这就是「<strong>事件溯源</strong>」四个字的含义：系统的真相是一连串<strong>只追加的事件</strong>，而不是一个被反复覆写的当前值。<strong>③ 拿序号</strong>：每个事件都被赋予一个单调递增的 <span class="mono">seq</span>，admit 把它记成 <span class="mono">admittedSeq</span>——这就是挂单轨上那张票的编号，先来后到从此有了铁证。</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">find(db, id)：这个 id 入过账没？入过 → 返回旧的（幂等）</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">events.publish(Admitted, {prompt, delivery…})：发一个不可变事件</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">事件被赋予单调 seq → 记为 admittedSeq（票号）</span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">返回 Admitted —— prompt 已持久、已编号，但一行模型代码都没跑</span></div>
</div>
<p>请把第 4 步咂摸一下：<span class="mono">admit</span> 返回时，你的 prompt 已经<strong>板上钉钉地存在</strong>了——它在数据库里、有编号、崩了也还在——可此刻<strong>模型连热身都还没开始</strong>。「已收下」和「已执行」被干净地剥成了两件事。这就是为什么前两个噩梦也跟着消失：崩溃？事件早落库了，重启后照样能从收件箱里捞出来接着跑。并发？所有输入都先排进同一条带序号的轨道，由后面的串行执行者一张张取，谁也别想插队抢状态。</p>
<div class="flow">
  <div class="node">prompt 到达<span class="sub">你按下回车</span></div>
  <div class="arrow">admit →</div>
  <div class="node">持久事件<span class="sub">入库·拿 seq</span></div>
  <div class="arrow">wake →</div>
  <div class="node">建议排空<span class="sub">advisory·可合并</span></div>
  <div class="arrow">promote →</div>
  <div class="node">可见消息<span class="sub">安全间隙·喂模型</span></div>
</div>
<p>这里还藏着一个容易被滑过、却极能体现功力的细节：admit 末尾对「发布失败」的兜底。万一 <span class="mono">publish</span> 抛了 defect，代码不是直接报错，而是<strong>再查一次 find</strong>——因为那个失败有可能只是「事件其实写成功了、但返回路上出了岔子」。再查一次，如果记录其实已经在了，就把它当成功返回。这种「失败了先别急着喊崩，回头确认一下真实状态」的谨慎，正是持久层该有的素养：在「绝不丢」和「绝不重」这两条红线之间，它宁可多查一次，也不肯赌。</p>

<h2>收件箱长什么样：session_input 表</h2>
<p>这些入了账的 prompt，落在一张叫 <span class="mono">session_input</span> 的表里（<span class="mono">session/sql.ts</span>）。它的字段，就是那张「挂单票」的全部信息：</p>
<div class="cellgroup">
  <div class="cell"><div class="k">id</div><div class="v">消息 ID（主键）—— 幂等就靠它</div></div>
  <div class="cell"><div class="k">prompt</div><div class="v">prompt 内容本体（JSON）</div></div>
  <div class="cell"><div class="k">delivery</div><div class="v">"steer"（插话）或 "queue"（排队）</div></div>
  <div class="cell"><div class="k">admitted_seq</div><div class="v">入账序号（每会话唯一、单调）—— 票号</div></div>
  <div class="cell"><div class="k">promoted_seq</div><div class="v">提单序号；为 NULL = 还在收件箱里待领</div></div>
</div>
<p>最值得玩味的是 <span class="mono">promoted_seq</span> 这个可空字段。它扮演着<strong>「这张票领了没」的标记</strong>：一条记录刚入账时，<span class="mono">promoted_seq</span> 是 <span class="mono">NULL</span>，意味着它<strong>还躺在收件箱里、等着被处理</strong>；等后面的串行执行者在某个安全的间隙把它「提」出来、变成一条用户能看见的真实消息时，才给它填上 <span class="mono">promoted_seq</span>。于是「收件箱里还有哪些没处理的输入」这个问题，简化成了一句极廉价的查询：<strong>找出这个会话里所有 <span class="mono">promoted_seq IS NULL</span> 的行</strong>。两个序号——一个记「何时入账」、一个记「何时提单」——把一个 prompt 从进门到落地的整段旅程，刻成了可查询的事实。</p>
<p>为什么要用<strong>两个</strong>序号，而不是一个状态字段了事？因为序号不只标记「办没办」，它还<strong>定义了顺序</strong>。<span class="mono">admitted_seq</span> 在每个会话内单调递增、且建了唯一索引，这等于给同一会话的所有输入排了一条<strong>铁打的先后队</strong>——串行执行者照着 <span class="mono">admitted_seq</span> 从小到大取，先提的 prompt 永远先被处理，绝不会因为并发或重试而乱序。一个布尔的「已处理/未处理」给不了你这个：它只说得清「有没有」，说不清「谁先谁后」。opencode 选择用序号而非状态位，正是因为它在意的从来不只是「这条输入处理了吗」，更是「整个会话的输入，是按什么不可争辩的顺序流过的」。</p>
<div class="timeline">
  <div class="tl-item"><span class="tl-time">① admit</span><span class="tl-desc">入账：写 admitted_seq，promoted_seq = NULL（待领）</span></div>
  <div class="tl-item"><span class="tl-time">② 在收件箱</span><span class="tl-desc">持久躺着，等串行执行者来取；崩溃重启依然在</span></div>
  <div class="tl-item"><span class="tl-time">③ promote</span><span class="tl-desc">安全间隙提单：填 promoted_seq，变成可见的 User 消息</span></div>
  <div class="tl-item"><span class="tl-time">④ 执行</span><span class="tl-desc">这才轮到喂模型、跑 agent 循环（第 16、17 课）</span></div>
</div>

<h2>steer 还是 queue：两种投递方式</h2>
<p>最后看那个 <span class="mono">delivery</span> 字段，它对应挂单票的「两种脾气」。当一个会话<strong>正在忙</strong>（模型正输出）时，新来的 prompt 该怎么办？opencode 给了你两个选择：</p>
<div class="cols">
  <div class="col"><h4>steer · 插话（默认）</h4><p>并入<strong>当前正在跑的活动</strong>，在下一个安全的「回合边界」生效。像冲着正在做的菜喊一句「不要葱」。你日常追加的指令，走的就是这条。</p></div>
  <div class="col"><h4>queue · 排队</h4><p>开一个<strong>独立的未来活动</strong>，等当前这轮彻底结束后，再 FIFO 地一个个轮到。像一张全新的订单，乖乖排在后面。</p></div>
</div>
<p>这两个词之所以要<strong>显式</strong>地写进数据模型，是因为它们对应着两种截然不同的意图，而 opencode 不愿替你猜。「我想纠正/补充<strong>这一轮</strong>」和「我想等它忙完<strong>再说另一件事</strong>」，是完全不同的诉求；把它钉成 <span class="mono">delivery</span> 字段，就让这份意图<strong>一路可追、可调度</strong>，而不是糊成「反正有条新消息来了」。注意两者都尊重<strong>「安全边界」</strong>：steer 不会粗暴打断模型的当前句子，而是等一个回合的干净缝隙才并入——这又呼应了第 7 课结构化并发那套「该收的时候干净地收」的纪律。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <p>这一课讲的是 prompt 进入 core 的<strong>第一道关</strong>，也是「持久」与「执行」的分界：</p>
  <ul>
    <li><strong>admit（入账）</strong>：把 prompt 发布成不可变事件，拿到单调 <span class="mono">admitted_seq</span>，落进 <span class="mono">session_input</span> 收件箱——又快又稳，绝不跑模型。</li>
    <li><strong>事件溯源</strong>：真相是只追加的事件流（呼应第 14 课「换模型也是一条消息」）；幂等靠 id、排序靠 seq。</li>
    <li><strong>promoted_seq</strong>：收件箱的「待领」标记；NULL = 还没处理。</li>
    <li><strong>delivery</strong>：steer（插话进当前活动）/ queue（排队成未来活动），把用户意图显式化。</li>
  </ul>
  <p>那么，是谁在「安全的间隙」把这些入账的输入<strong>提单、变成可见消息、再真正喂给模型</strong>的？那个串行的调度者，就是下一课的主角——<strong>运行协调器（run coordinator，第 16 课）</strong>。收件箱负责「稳稳收下」，协调器负责「有序取出」，两者合起来，才是 opencode 会话引擎的下半身。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p>「入账」与「执行」是<strong>两个独立的动作</strong>，这一点在接口签名上就划得清清楚楚：</p>
  <pre class="code"><span class="cm">// admit 只管持久落账（session/input.ts）</span>
SessionInput.<span class="fn">admit</span>(db, events, { id, sessionID, prompt, delivery })
  <span class="cm">// → 返回 Admitted{ admittedSeq, … }，不跑模型</span>

<span class="cm">// wake 只管"提醒去排空"（session/execution.ts）</span>
<span class="cm">// "Schedule a drain after durable work is recorded. 重复 wake 会合并。"</span>
SessionExecution.<span class="fn">wake</span>(sessionID, seq?)
  <span class="cm">// → 安排一次 drain；advisory（建议性），可被合并</span></pre>
  <p>典型流程是：先 <span class="mono">admit</span>（持久、拿序号），<strong>再</strong> <span class="mono">wake</span>（建议性地叫一声「有活了，去排空」）。注意 wake 的注释——重复的叫醒会<strong>合并</strong>：哪怕你瞬间塞十个 prompt，也不会触发十次重复排空。<strong>持久的是 admit、建议的是 wake</strong>，一个负责「绝不丢」，一个负责「别空转」，职责泾渭分明。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li>opencode <strong>不把刚到的 prompt 直接喂模型</strong>，而是「先入账、再执行」——把<strong>接收</strong>（快、稳、不可失败）与<strong>执行</strong>（慢、险、可中断）劈成两步。</li>
    <li><span class="mono">SessionInput.admit</span> 把 prompt <strong>发布成不可变事件</strong>（事件溯源），拿到单调 <span class="mono">admitted_seq</span>，落进 <span class="mono">session_input</span> 收件箱——一行模型代码都不跑。</li>
    <li>这一招同时消解三个噩梦：<strong>崩溃丢失</strong>（事件已落库）、<strong>并发打架</strong>（统一排序、串行取）、<strong>重试翻倍</strong>（按 id 幂等）。</li>
    <li><span class="mono">promoted_seq IS NULL</span> 标记一条输入「还在收件箱待领」；提单时填上它、变成可见的 User 消息。</li>
    <li><span class="mono">delivery</span> 显式区分 <strong>steer</strong>（插话进当前活动，下个安全边界生效）与 <strong>queue</strong>（排队成未来活动），把用户意图刻进数据。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Last lesson we met the nouns Session/Message/Part. This lesson answers a question that looks simple but hides real danger: when you hit enter and a prompt flies to the server, how does opencode <strong>"receive" it</strong>? The naivest answer is "run the model right away" — and that's exactly what opencode <strong>refuses</strong> to do. It first records your prompt <strong>verbatim as an immutable event in a place called the "inbox,"</strong> gets it a sequence number, and <strong>only then</strong> calmly schedules execution. This lesson is about that "admit first, run later" design — the <strong>event-sourced input inbox</strong>, the root of how opencode's session engine can be "crash-safe, retry-safe, concurrency-safe."</p>
<p>Why does "receiving a prompt" deserve its own lesson? Because it's the <strong>watershed between durability and execution</strong>. Picture the opposite: if a prompt is fed to the model the instant it arrives, then — the process crashes between "received" and "started" and the prompt <strong>vanishes into thin air</strong>; the model is mid-sentence when a new prompt arrives and the two logics <strong>fight on the spot</strong>; a network hiccup resends once and the same sentence <strong>runs twice</strong>. opencode's move of "land the input as a durable event first" dissolves all three nightmares at once. Understand this lesson and you understand why opencode's sessions <strong>withstand interruption, retry, and concurrency</strong> — which is precisely what separates a serious agent engine from a toy script.</p>

<div class="card analogy">
  <div class="tag">🍳 Analogy</div>
  Picture a busy restaurant's <strong>kitchen ticket rail</strong>. You order, and the server <strong>doesn't</strong> charge into the kitchen and grab the chef mid-stir to make your dish now — that would only burn the dish in hand. What the server does is write your order on a <strong>numbered ticket</strong> and clip it onto the rail (this is <strong>admit</strong>). From then on that ticket <strong>solidly exists</strong>: it has a number (first-come order at a glance) and is durable (even if the kitchen catches fire and restarts, the ticket still hangs on the rail, not one lost). The chef pulls tickets off the rail at <strong>clean gaps between dishes</strong> (this is <strong>promote</strong>). And tickets come in two tempers: "<strong>steer</strong>" — shout "no onions on that!" at the dish being cooked right now, merged in on the spot; "<strong>queue</strong>" — a separate new order that waits its FIFO turn. See this ticket rail and you've seen all the craft in how opencode receives a prompt.
</div>

<h2>The naive way, and its three nightmares</h2>
<p>Lay out the "wrong answer" first and the right one shines. A toy agent writes it thus: <span class="mono">receive prompt → immediately await model.run(prompt)</span>. Simple and direct, but it shatters in three places:</p>
<div class="cols">
  <div class="col"><h4>💥 crash loss</h4><p>the process dies between "received" and "started"; the prompt leaves no trace, vanished.</p></div>
  <div class="col"><h4>💥 concurrency clash</h4><p>the model is mid-output when a new prompt barges in; two executions grab the same session state.</p></div>
  <div class="col"><h4>💥 retry doubling</h4><p>a network hiccup, the client resends; the same sentence is taken as two requests and runs twice.</p></div>
</div>
<p>The common root of these three nightmares is <strong>welding "receive" and "execute" into one step</strong>. As long as they're one action, receiving's reliability is dragged down by execution's fragility — execution calls the model, takes tens of seconds, can be interrupted anytime, while receiving should be instant and must never fail. opencode's break is plain and forceful: <strong>split the step in two</strong>. Do the fast, stable "receive" first, made an unfailable durable record; then hand the slow, risky "execute" to unhurried later scheduling.</p>
<p>This "split in two" idea is in fact the same as a database's <strong>write-ahead log (WAL)</strong>. Before changing data, a database never touches the real data pages directly; it first writes "here's what I intend to change" into an append-only log — once the log is on disk, the operation is <strong>undeniable, unlosable</strong>, and even if power dies the next second, a restart replays the log. opencode receives prompts with the same wisdom: <span class="mono">admit</span> is that write-ahead log, nailing "the user posed this prompt" firmly into the durable layer first, while the truly laborious execution can be made up calmly afterward. <strong>Record the intent first, fulfil it later</strong> — this plain principle is the shared backbone of nearly every "crash-proof" system.</p>

<h2>admit: record the prompt as an event</h2>
<p>opencode's real entry for receiving a prompt is <span class="mono">SessionInput.admit</span> (<span class="mono">session/input.ts</span>). It <strong>runs no model</strong>; it does one thing: <strong>publish this prompt as an immutable event</strong>, land it in durable storage, and get back a sequence number. See its skeleton:</p>
<pre class="code"><span class="cm">// simplified from session/input.ts</span>
<span class="kw">export const</span> admit = Effect.<span class="fn">fn</span>(<span class="kw">function</span>* (db, events, input) {
  <span class="kw">const</span> existing = <span class="kw">yield</span>* <span class="fn">find</span>(db, input.id)
  <span class="kw">if</span> (existing !== <span class="kw">undefined</span>) <span class="kw">return</span> existing   <span class="cm">// (1) idempotent: same id returns the old</span>
  <span class="kw">return</span> <span class="kw">yield</span>* events.<span class="fn">publish</span>(
    SessionEvent.PromptLifecycle.Admitted, {       <span class="cm">// (2) publish an "admitted" event</span>
      messageID: input.id, prompt: input.prompt, delivery: input.delivery, ...
    }).<span class="fn">pipe</span>(Effect.<span class="fn">map</span>((event) =&gt;
      <span class="kw">new</span> <span class="fn">Admitted</span>({ admittedSeq: event.seq, ... })))  <span class="cm">// (3) the number = event's seq</span>
})</pre>
<p>Three steps, each crucial. <strong>(1) Idempotent</strong>: it first looks up by <span class="mono">input.id</span>, and if already admitted returns the old record — so <strong>resending the same prompt (same id) admits only once</strong>, and the third nightmare disappears on the spot. <strong>(2) Publish an event</strong>: admit doesn't edit some field; it <span class="mono">publish</span>es a <span class="mono">PromptLifecycle.Admitted</span> event — and that's the meaning of "<strong>event sourcing</strong>": the system's truth is a string of <strong>append-only events</strong>, not one current value overwritten again and again. <strong>(3) Get a number</strong>: every event is given a monotonically increasing <span class="mono">seq</span>, which admit records as <span class="mono">admittedSeq</span> — the number on that ticket on the rail, an ironclad record of first-come order.</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">find(db, id): has this id been admitted? yes → return the old (idempotent)</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">events.publish(Admitted, {prompt, delivery…}): emit an immutable event</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">the event is given a monotonic seq → recorded as admittedSeq (ticket number)</span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">return Admitted — prompt is durable, numbered, yet not one line of model ran</span></div>
</div>
<p>Savor step 4: when <span class="mono">admit</span> returns, your prompt <strong>definitively exists</strong> — it's in the database, numbered, survives a crash — yet at this moment <strong>the model hasn't even warmed up</strong>. "Received" and "executed" are cleanly peeled into two things. That's why the first two nightmares also vanish: crash? the event landed long ago, and after restart it can be fished out of the inbox and resumed. concurrency? all inputs first line up on one numbered track, pulled one ticket at a time by the later serial executor, with no one cutting in to grab state.</p>
<div class="flow">
  <div class="node">prompt arrives<span class="sub">you hit enter</span></div>
  <div class="arrow">admit →</div>
  <div class="node">durable event<span class="sub">stored · gets seq</span></div>
  <div class="arrow">wake →</div>
  <div class="node">advisory drain<span class="sub">advisory · coalescable</span></div>
  <div class="arrow">promote →</div>
  <div class="node">visible message<span class="sub">safe gap · feed model</span></div>
</div>
<p>One more easily-skipped detail that really shows craft: admit's fallback for "publish failed" at the end. Should <span class="mono">publish</span> throw a defect, the code doesn't just error out but <strong>looks up find once more</strong> — because that failure might only be "the event actually wrote successfully, but something went wrong on the return path." Look again, and if the record is in fact already there, return it as success. This caution of "don't cry crash on failure; go confirm the real state first" is exactly the maturity a durable layer needs: between the two red lines of "never lose" and "never duplicate," it would rather query once more than gamble.</p>

<h2>What the inbox looks like: the session_input table</h2>
<p>These admitted prompts land in a table called <span class="mono">session_input</span> (<span class="mono">session/sql.ts</span>). Its fields are all the information on that "rail ticket":</p>
<div class="cellgroup">
  <div class="cell"><div class="k">id</div><div class="v">message ID (primary key) — idempotency rests on it</div></div>
  <div class="cell"><div class="k">prompt</div><div class="v">the prompt content itself (JSON)</div></div>
  <div class="cell"><div class="k">delivery</div><div class="v">"steer" (cut in) or "queue" (line up)</div></div>
  <div class="cell"><div class="k">admitted_seq</div><div class="v">admission number (per-session unique, monotonic) — the ticket number</div></div>
  <div class="cell"><div class="k">promoted_seq</div><div class="v">promotion number; NULL = still waiting in the inbox</div></div>
</div>
<p>The most intriguing is the nullable <span class="mono">promoted_seq</span> field. It plays the <strong>marker of "has this ticket been pulled"</strong>: when a record is freshly admitted, <span class="mono">promoted_seq</span> is <span class="mono">NULL</span>, meaning it <strong>still lies in the inbox, waiting to be processed</strong>; only when the later serial executor "pulls" it out at some safe gap and turns it into a real user-visible message does it get a <span class="mono">promoted_seq</span>. So "which unprocessed inputs remain in the inbox" reduces to one dirt-cheap query: <strong>find all rows in this session with <span class="mono">promoted_seq IS NULL</span></strong>. Two numbers — one recording "when admitted," one "when promoted" — carve a prompt's whole journey from arrival to landing into a queryable fact.</p>
<p>Why <strong>two</strong> numbers, not one status field? Because a number marks not just "done or not" but also <strong>defines order</strong>. <span class="mono">admitted_seq</span> increases monotonically within each session and has a unique index, so it lines up all of a session's inputs into an <strong>ironclad order</strong> — the serial executor pulls them by <span class="mono">admitted_seq</span> ascending, the earlier-admitted prompt always processed first, never reordered by concurrency or retry. A boolean "processed/unprocessed" can't give you this: it states "whether," not "who first." opencode chose a sequence number over a status bit precisely because what it cares about was never just "was this input processed" but "in what indisputable order did the whole session's inputs flow through."</p>
<div class="timeline">
  <div class="tl-item"><span class="tl-time">① admit</span><span class="tl-desc">admitted: write admitted_seq, promoted_seq = NULL (waiting)</span></div>
  <div class="tl-item"><span class="tl-time">② in inbox</span><span class="tl-desc">lies durable, awaiting the serial executor; survives a restart</span></div>
  <div class="tl-item"><span class="tl-time">③ promote</span><span class="tl-desc">pulled at a safe gap: fill promoted_seq, become a visible User message</span></div>
  <div class="tl-item"><span class="tl-time">④ execute</span><span class="tl-desc">only now feed the model, run the agent loop (Lessons 16, 17)</span></div>
</div>

<h2>steer or queue: two ways of delivery</h2>
<p>Finally the <span class="mono">delivery</span> field, matching the ticket's "two tempers." When a session is <strong>busy</strong> (the model outputting), what to do with a newly-arrived prompt? opencode gives you two choices:</p>
<div class="cols">
  <div class="col"><h4>steer · cut in (default)</h4><p>merge into the <strong>currently running activity</strong>, taking effect at the next safe "turn boundary." Like shouting "no onions" at the dish being made. Your everyday follow-up instructions take this road.</p></div>
  <div class="col"><h4>queue · line up</h4><p>open a <strong>separate future activity</strong>, taking its FIFO turn only after the current one fully ends. Like a brand-new order, waiting patiently behind.</p></div>
</div>
<p>These two words are written <strong>explicitly</strong> into the data model because they correspond to two utterly different intents, and opencode won't guess for you. "I want to correct/add to <strong>this turn</strong>" and "I want to wait till it's done <strong>then say another thing</strong>" are entirely different needs; nailing it as a <span class="mono">delivery</span> field makes that intent <strong>traceable and schedulable all the way</strong>, not mashed into "anyway a new message arrived." Note both respect the <strong>"safe boundary"</strong>: steer won't rudely interrupt the model's current sentence but waits for a turn's clean gap to merge in — echoing Lesson 7's structured-concurrency discipline of "collect cleanly when it's time to collect."</p>

<div class="card macro">
  <div class="tag">🗺️ The big picture</div>
  <p>This lesson is about the <strong>first gate</strong> a prompt passes into core, and the boundary between "durable" and "execute":</p>
  <ul>
    <li><strong>admit</strong>: publish the prompt as an immutable event, get a monotonic <span class="mono">admitted_seq</span>, land it in the <span class="mono">session_input</span> inbox — fast and stable, runs no model.</li>
    <li><strong>event sourcing</strong>: the truth is an append-only event stream (echoing Lesson 14's "switch model is a message"); idempotency by id, ordering by seq.</li>
    <li><strong>promoted_seq</strong>: the inbox's "waiting" marker; NULL = not yet processed.</li>
    <li><strong>delivery</strong>: steer (cut into the current activity) / queue (line up as a future activity), making user intent explicit.</li>
  </ul>
  <p>So who, "at the safe gap," <strong>promotes these admitted inputs, turns them into visible messages, and actually feeds the model</strong>? That serial scheduler is next lesson's star — the <strong>run coordinator (Lesson 16)</strong>. The inbox handles "receive steadily," the coordinator handles "pull in order," and together they form the lower half of opencode's session engine.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source detail</div>
  <p>"Admit" and "execute" are <strong>two independent actions</strong>, and the interface signatures draw it cleanly:</p>
  <pre class="code"><span class="cm">// admit only does durable landing (session/input.ts)</span>
SessionInput.<span class="fn">admit</span>(db, events, { id, sessionID, prompt, delivery })
  <span class="cm">// → returns Admitted{ admittedSeq, … }, runs no model</span>

<span class="cm">// wake only "nudges to drain" (session/execution.ts)</span>
<span class="cm">// "Schedule a drain after durable work is recorded. Repeated wakeups may coalesce."</span>
SessionExecution.<span class="fn">wake</span>(sessionID, seq?)
  <span class="cm">// → schedule a drain; advisory, coalescable</span></pre>
  <p>The typical flow: <span class="mono">admit</span> first (durable, get the number), <strong>then</strong> <span class="mono">wake</span> (advisorily call out "there's work, go drain"). Note wake's comment — repeated wakeups <strong>coalesce</strong>: even if you stuff in ten prompts in an instant, it won't trigger ten redundant drains. <strong>admit is durable, wake is advisory</strong>, one for "never lose," one for "don't spin idle," with cleanly separated duties.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key points</div>
  <ul>
    <li>opencode <strong>doesn't feed a just-arrived prompt to the model</strong>; it "admits first, runs later" — splitting <strong>receive</strong> (fast, stable, unfailable) from <strong>execute</strong> (slow, risky, interruptible).</li>
    <li><span class="mono">SessionInput.admit</span> <strong>publishes the prompt as an immutable event</strong> (event sourcing), gets a monotonic <span class="mono">admitted_seq</span>, lands it in the <span class="mono">session_input</span> inbox — running no model code at all.</li>
    <li>This one move dissolves three nightmares: <strong>crash loss</strong> (event already landed), <strong>concurrency clash</strong> (unified ordering, pulled serially), <strong>retry doubling</strong> (idempotent by id).</li>
    <li><span class="mono">promoted_seq IS NULL</span> marks an input as "still waiting in the inbox"; promotion fills it and turns it into a visible User message.</li>
    <li><span class="mono">delivery</span> explicitly distinguishes <strong>steer</strong> (cut into the current activity, effective at the next safe boundary) from <strong>queue</strong> (line up as a future activity), carving user intent into the data.</li>
  </ul>
</div>
""",
}
LESSON_16 = {
    "zh": r"""
<p class="lead">上一课，prompt 被稳稳地<strong>入账</strong>进了收件箱，并摇响了一记<strong>建议性的铃</strong>（<span class="mono">wake</span>）。可铃响了，谁来应？谁负责<strong>从收件箱里把输入一条条取出、按序号执行，同时死死保证「同一个会话绝不会被两股执行同时蹂躏」</strong>？这就是这一课的主角——<strong>运行协调器（run coordinator）</strong>。如果说收件箱解决了「怎么稳稳收下」，协调器解决的就是「怎么有序取出」。它是 opencode 会话引擎的<strong>调度中枢</strong>：一边吸收纷至沓来的执行请求，一边把它们驯服成<strong>每会话严格串行、跨会话自由并发</strong>的干净节奏。</p>
<p>为什么这层调度值得专讲？因为它是「<strong>并发正确性</strong>」的兜底人。一个 agent 会话的执行，绝不能容忍两份同时跑——它们会抢同一段历史、同一批工具状态，瞬间把数据搅成一团乱麻。但若简单粗暴地「全局只许一个会话跑」，又会让你开十个会话时只能干等。协调器要的是那个微妙的平衡点：<strong>同一会话内，至多一条执行链在跑；不同会话间，谁也不挡谁。</strong>这一课就拆开它是用什么精巧的状态机，把「串行」与「并发」这对看似矛盾的需求，同时、优雅地满足的。</p>

<div class="card analogy">
  <div class="tag">🚉 生活类比</div>
  把每个会话想成一座<strong>火车站</strong>，每座站只有<strong>一条单轨</strong>。一座站的轨道上，<strong>同一时刻只容一列车</strong>跑——这就是「同会话串行」：绝不让两列车在一条轨上对撞。但<strong>不同的站各有各的轨</strong>，互不干涉，可以同时各跑各的——这就是「跨会话并发」。现在看信号：「<strong>发车</strong>」（run）是一道明确的调度令，要么发出一列新车，要么并入正在跑的那列。「<strong>有货</strong>」（wake）只是货场摇的一记铃：「轨上可能有新货要拉了」——可如果车正在跑，你<strong>不会</strong>再硬塞一列，只是按下一个「跑完这趟再多兜一圈」的标记。哪怕这铃在一趟车的途中摇了十次，也只换来<strong>一次</strong>额外兜圈（因为一趟车本就把轨上所有货一次拉完）。一站一轨、车随铃动、铃多归一——这套调度，就是运行协调器。
</div>

<h2>核心铁律：同会话串行，跨会话并发</h2>
<p>协调器的全部设计，都围着源码注释里的一句话转：「<strong>每个 key 至多跑一条排空链，不同 key 可并发排空</strong>」。这里的 key 就是会话 ID。把它翻成两条铁律：</p>
<div class="cols">
  <div class="col"><h4>🚆 同会话：严格串行</h4><p>同一个会话，任一时刻<strong>至多一条执行链</strong>在跑。第二个请求来了，不另起炉灶，而是<strong>并入</strong>当前这条链。从根上杜绝了「两股执行抢同一份历史」。</p></div>
  <div class="col"><h4>🚄 跨会话：自由并发</h4><p>不同会话各有各的执行链，<strong>互不阻塞</strong>。你开十个会话，它们能同时推进，谁也不必排队等别人。</p></div>
</div>
<p>实现这条铁律的，是一个朴素到家的数据结构：协调器内部维护一个 <span class="mono">Map&lt;Key, Entry&gt;</span>——<strong>每个会话一个 Entry</strong>（一条「执行车道」）。同一个会话 ID 永远命中同一个 Entry，于是它的所有请求都被这唯一的 Entry 串成一条线；而不同会话 ID 命中不同 Entry，天然互不相干、各跑各的。<strong>「串行」与「并发」的全部魔法，就藏在「按 key 分桶」这一下里</strong>——这其实正是第 8 课 <span class="mono">KeyedMutex</span>「同 key 串行、异 key 并行」那个理念，在会话执行这一层被打磨成了一个更精巧的专用版本。</p>
<p>值得停下来体会「为什么必须串行」。一个 agent 会话的执行，会不断<strong>读写同一份共享状态</strong>：当前的消息历史、各个工具的状态、累计的 token 账单。若放任两趟执行同时跑，它们就会像两只手同时改一张纸——A 刚写下半句，B 把它覆盖，最后谁也说不清这张纸到底该是什么样。这类 bug 还特别阴险：它只在「恰好两个请求撞在一起」的罕见时刻才发作，平时测都测不出来。协调器用「同会话至多一条链」这条硬规则，把这种竞态<strong>从结构上彻底排除</strong>——不是靠加锁去亡羊补牢，而是让「两趟同时跑」这件事<strong>根本无法发生</strong>。这是比「小心翼翼地加锁」高明得多的解法：最好的并发 bug，是那些被设计得压根不可能出现的。</p>
<div class="flow">
  <div class="node">收件箱<span class="sub">admit + wake（第 15 课）</span></div>
  <div class="arrow">→</div>
  <div class="node">运行协调器<span class="sub">按会话分车道</span></div>
  <div class="arrow">drain →</div>
  <div class="node">SessionRunner.run<span class="sub">真正的 agent 循环（第 17 课）</span></div>
</div>

<h2>run 与 wake：一个发车、一个摇铃</h2>
<p>协调器对外的两个主要动作，对应类比里的「发车」与「摇铃」，语义截然不同。<strong><span class="mono">run</span>（发车）</strong>是<strong>显式</strong>的执行请求：会话空闲就起一条新链，会话正忙就<strong>并入</strong>当前链——并入时调用方仍拿到「显式执行」的语义（比如它能等到这趟真正跑完）。<strong><span class="mono">wake</span>（摇铃）</strong>则是<strong>建议性</strong>的：它只是报告「持久层可能有新活了」——空闲时它会起一条链，但若正忙，它<strong>只登记一个被合并的后续</strong>，绝不另起第二条。</p>
<div class="cols">
  <div class="col"><h4>run · 显式发车</h4><p>主动要求执行。起链，或<strong>并入</strong>当前链。用于「明确就是要现在跑这个会话」（比如续跑 resume）。</p></div>
  <div class="col"><h4>wake · 建议摇铃</h4><p>报告「可能有活」。空闲起链；忙则<strong>合并</strong>成至多一个后续。第 15 课 admit 之后摇的，就是这记铃。</p></div>
</div>
<p>两者的分野，正好接住了上一课的设计：admit 之后调的是 <span class="mono">wake</span>——因为入账只是「可能有活了」的一记提示，至于真去排空、什么时候排，交给协调器拿捏。而像「用户明确点了续跑」这种<strong>非它不可</strong>的请求，走的才是 <span class="mono">run</span>。<strong>建议的归 wake、命令的归 run</strong>，这条线划得和第 15 课「持久的归 admit、建议的归 wake」一脉相承。这种「把不同强度的意图，用不同的动词显式区分开」的做法，你在这套代码里会一再遇到——它让调度器永远知道「这一下到底是非跑不可，还是跑不跑都行」，从而做出恰如其分的取舍。</p>

<h2>coalesce：十次摇铃，一次兜圈</h2>
<p>协调器最妙的一笔，是 <span class="mono">coalesce</span>（合并）。设想一个会话正在排空（drain 正跑），这期间又有五个 prompt 入账、摇了五次 <span class="mono">wake</span>。天真的做法会排五次队、跑五趟。但协调器只留<strong>至多一个</strong>「待办后续」：这五次 wake 全被<strong>折叠成一个</strong>。为什么一个就够？因为一趟 drain 本就会把收件箱里<strong>当前所有合格的行一次扫光</strong>——所以只需要在当前这趟跑完后，<strong>再补跑一趟</strong>去兜住「我这趟跑的途中又新来的那些」，一趟足矣。</p>
<pre class="code"><span class="cm">// 简化自 session/run-coordinator.ts</span>
<span class="kw">const</span> coalesce = (left, right) =&gt; {
  <span class="kw">if</span> (left?._tag === <span class="st">"run"</span> || right._tag === <span class="st">"run"</span>)
    <span class="kw">return</span> { _tag: <span class="st">"run"</span> }          <span class="cm">// ① run 压倒 wake</span>
  <span class="kw">return</span> { _tag: <span class="st">"wake"</span>, seq: <span class="fn">maxSeq</span>(left?.seq, right.seq) }  <span class="cm">// ② wake 取最新 seq</span>
}</pre>
<p>合并规则只有两条，却字字千金。<strong>① run 压倒 wake</strong>：待办里只要掺进一个显式 run，合并结果就是 run——「命令」永远盖过「建议」，因为有人明确要求执行，就不能被降格成一记可有可无的铃。<strong>② wake 取最新 seq</strong>：两记 wake 合并时，保留<strong>更大的那个序号</strong>——这样后续那趟排空，知道至少要追到「目前已知最新入账的那条」为止，一条都不漏。<strong>合并不是丢弃，而是「取并集里最强的那个意图」</strong>：要么升格成 run，要么追上最新的 seq。十记铃声归并成一次精准的兜圈，既不空跑、也不漏单。</p>
<div class="timeline">
  <div class="tl-item"><span class="tl-time">t0</span><span class="tl-desc">drain 开始跑（处理当前收件箱所有合格行）</span></div>
  <div class="tl-item"><span class="tl-time">t1–t5</span><span class="tl-desc">途中又来 5 个 prompt：wake×5，全被 coalesce 成 1 个待办</span></div>
  <div class="tl-item"><span class="tl-time">t6</span><span class="tl-desc">本趟 drain 结束 → 看到那 1 个待办</span></div>
  <div class="tl-item"><span class="tl-time">t7</span><span class="tl-desc">补跑 1 趟，一次扫光这 5 个新来的 → 回到 idle</span></div>
</div>
<p>为什么不怕「合并把活漏掉」？关键在那个 seq。每记 wake 都带着「目前已知最新入账序号」，合并时取最大值；而一趟 drain 的契约是「把截至某序号为止、所有合格的行全部处理完」。于是即便途中来了一百记 wake，只要合并后的待办记着那个最大的 seq，补跑的这一趟就<strong>保证覆盖到第一百条</strong>。<strong>用「一个带最新进度的待办」顶替「一长串重复待办」</strong>——这是把幂等思想从第 15 课的「按 id 去重」，推进到了调度层的「按 seq 收敛」。少跑了无数趟冗余 drain，却一笔活都没少干。</p>

<h2>那台状态机：idle → draining → 收尾</h2>
<p>把上面这些拼起来，每条会话车道其实就是一台小小的<strong>状态机</strong>，源码注释画得明明白白：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">idle</span><span class="t-txt">空闲：没有执行链在跑</span></div>
  <div class="t-row"><span class="t-num">→</span><span class="t-txt">来一个 run/wake → 起一条排空链，进入 draining</span></div>
  <div class="t-row"><span class="t-num">draining</span><span class="t-txt">正在排空：期间再来的 run/wake 不另起，只 coalesce 成"至多一个待办后续"</span></div>
  <div class="t-row"><span class="t-num">→</span><span class="t-txt">本趟跑完，若有待办 → 再补跑一趟（coalesced rerun）</span></div>
  <div class="t-row"><span class="t-num">idle</span><span class="t-txt">待办也清空了 → 回到空闲，静待下一记铃</span></div>
</div>
<p>这台状态机的美，在于它把「<strong>至多一条链在跑</strong>」这个不变量焊得死死的：无论外面 run、wake 来得多猛、多密，一个会话<strong>同时最多只有一趟 drain 在跑、外加最多一个待办</strong>。它既不会因为请求太密而并发失控，也不会因为合并而漏掉任何一笔已入账的活。还有第三个动作 <span class="mono">interrupt</span>（中断）：它能停掉当前这条执行链——这是「能干净地喊停一个正在长考的 agent」的底层开关，我们留到第 20 课再细看它怎么和「有界步数、错误处理」配合。这里只需记住：协调器不只管「怎么开跑」，也管「怎么停下」。</p>
<div class="cellgroup">
  <div class="cell"><div class="k">run(key)</div><div class="v">显式发车：起链或并入当前链</div></div>
  <div class="cell"><div class="k">wake(key, seq?)</div><div class="v">建议摇铃：起链或合并一个后续</div></div>
  <div class="cell"><div class="k">awaitIdle(key)</div><div class="v">等这条链彻底跑完、回到空闲</div></div>
  <div class="cell"><div class="k">interrupt(key, seq?)</div><div class="v">停掉当前执行链（第 20 课细看）</div></div>
</div>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <p>协调器是收件箱（第 15 课）与 agent 循环（第 17 课）之间的<strong>调度枢纽</strong>，也是「并发正确性」的守门人：</p>
  <ul>
    <li><strong>铁律</strong>：同会话至多一条执行链（串行）、跨会话各跑各的（并发）——靠 <span class="mono">Map&lt;Key, Entry&gt;</span> 按会话分车道实现，是第 8 课 KeyedMutex 的精装版。</li>
    <li><strong>run vs wake</strong>：run 是显式发车（起链或并入）；wake 是建议摇铃（起链或合并后续）。第 15 课 admit 后摇的是 wake。</li>
    <li><strong>coalesce</strong>：途中纷至的请求折叠成至多一个后续——run 压倒 wake、wake 取最新 seq；十记铃声归一次精准兜圈。</li>
    <li><strong>状态机</strong>：idle → draining → 至多一次合并补跑 → idle，把「至多一条链」焊死。</li>
  </ul>
  <p>那么，被协调器一趟趟「drain」出来、真正喂给模型去跑的，到底是怎样一个循环？它怎么把一条用户消息，变成「想→调工具→看结果→再想」的反复推进？那就是下一课的主角——<strong>V2 agent 循环（第 17 课）</strong>，opencode 这颗大脑真正"思考"的地方。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p>协调器并不知道「排空」具体在干嘛——它只是个通用的串行+合并外壳，真正的活由传进来的 <span class="mono">drain</span> 回调决定。看 <span class="mono">SessionExecution</span> 是怎么把二者接起来的：</p>
  <pre class="code"><span class="cm">// 简化自 session/execution/local.ts</span>
<span class="kw">const</span> coordinator = <span class="kw">yield</span>* SessionRunCoordinator.<span class="fn">make</span>({
  drain: (sessionID, mode) =&gt;                       <span class="cm">// ← 协调器只负责"何时、串行地"调它</span>
    SessionRunner.Service.<span class="fn">use</span>((runner) =&gt;
      runner.<span class="fn">run</span>({ sessionID, force: mode === <span class="st">"run"</span> })),  <span class="cm">// ← 真正的 agent 循环</span>
})
<span class="cm">// SessionExecution 把三个动作直接转接给协调器：</span>
{ resume: coordinator.run, wake: coordinator.wake, interrupt: coordinator.interrupt }</pre>
  <p>这是一处漂亮的<strong>关注点分离</strong>：协调器只懂「按 key 串行、合并、起停」这套<strong>纯调度</strong>逻辑，对「排空时到底跑什么」一无所知；而具体的 agent 循环（<span class="mono">SessionRunner.run</span>）则完全不操心并发与排队。注意那个 <span class="mono">force: mode === "run"</span>——它把「这趟是显式发车还是建议摇铃」原样透传给 runner，让下游也能区分对待。<strong>调度与执行解耦</strong>，各自都能被单独读懂、单独测试。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li>运行协调器是收件箱与 agent 循环之间的<strong>调度枢纽</strong>：应答 <span class="mono">wake</span> 的铃，把入账的输入有序地排空执行。</li>
    <li><strong>核心铁律</strong>：同一会话至多一条执行链（<strong>串行</strong>），不同会话各跑各的（<strong>并发</strong>）——靠 <span class="mono">Map&lt;Key, Entry&gt;</span> 按会话分车道，是 KeyedMutex 的精装版。</li>
    <li><strong>run（显式发车）</strong>起链或并入当前链；<strong>wake（建议摇铃）</strong>起链或只登记一个合并后续。admit 之后摇的是 wake。</li>
    <li><strong>coalesce</strong>把途中纷至的请求折叠成至多一个后续：<strong>run 压倒 wake、wake 取最新 seq</strong>，十记铃声归一次精准补跑、不空跑不漏单。</li>
    <li>每条车道是一台 <strong>idle→draining→至多一次补跑→idle</strong> 的状态机，把「至多一条链」焊死；<span class="mono">interrupt</span> 提供干净喊停的开关（第 20 课）。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Last lesson, the prompt was steadily <strong>admitted</strong> into the inbox and rang an <strong>advisory bell</strong> (<span class="mono">wake</span>). But the bell rang — who answers? Who <strong>pulls inputs from the inbox one by one, executes them in sequence order, while ironclad-guaranteeing "the same session is never ravaged by two executions at once"</strong>? That's this lesson's star — the <strong>run coordinator</strong>. If the inbox solved "how to receive steadily," the coordinator solves "how to pull in order." It's opencode's session engine's <strong>scheduling hub</strong>: absorbing the flood of incoming execution requests on one side, taming them into a clean rhythm that's <strong>strictly serial within a session, freely concurrent across sessions</strong> on the other.</p>
<p>Why does this scheduling layer deserve its own lesson? Because it's the backstop of <strong>concurrency correctness</strong>. An agent session's execution must never tolerate two running at once — they'd grab the same history, the same tool states, instantly churning the data into a tangle. But crudely "only one session may run globally" would force you to wait idle when you open ten sessions. The coordinator wants that delicate balance: <strong>within one session, at most one execution chain runs; across sessions, no one blocks anyone.</strong> This lesson unpacks the clever state machine it uses to satisfy "serial" and "concurrent" — these seemingly contradictory needs — at once and elegantly.</p>

<div class="card analogy">
  <div class="tag">🚉 Analogy</div>
  Think of each session as a <strong>train station</strong>, each with <strong>a single track</strong>. On one station's track, <strong>only one train runs at a time</strong> — that's "serial within a session": never let two trains collide on one track. But <strong>different stations have their own tracks</strong>, mutually independent, running at the same time — that's "concurrent across sessions." Now the signals: "<strong>depart</strong>" (run) is an explicit dispatch order — either send out a new train or merge into the running one. "<strong>cargo ready</strong>" (wake) is just a bell rung at the yard: "there may be new cargo to haul" — but if a train is running, you <strong>don't</strong> jam in a second; you just press a "do one more round after this trip" marker. Even if this bell rings ten times during a trip, it buys only <strong>one</strong> extra round (because one trip already hauls all the cargo on the track at once). One station one track, trains move on the bell, many bells fold into one — this scheduling is the run coordinator.
</div>

<h2>The iron law: serial within a session, concurrent across</h2>
<p>The coordinator's whole design revolves around one line in the source comment: "<strong>Runs at most one drain chain per key while allowing different keys to drain concurrently.</strong>" Here the key is the session ID. Translated into two iron laws:</p>
<div class="cols">
  <div class="col"><h4>🚆 same session: strictly serial</h4><p>One session, at any instant <strong>at most one execution chain</strong> runs. A second request comes? Not a new fire; it <strong>merges</strong> into the current chain. Root-out of "two executions grabbing the same history."</p></div>
  <div class="col"><h4>🚄 across sessions: freely concurrent</h4><p>Different sessions each have their own chain, <strong>mutually non-blocking</strong>. Open ten sessions and they advance together, none queuing behind another.</p></div>
</div>
<p>What implements this law is a structure plain to the bone: the coordinator keeps a <span class="mono">Map&lt;Key, Entry&gt;</span> internally — <strong>one Entry per session</strong> (an "execution lane"). The same session ID always hits the same Entry, so all its requests are strung into one line by that sole Entry; while different session IDs hit different Entries, naturally unrelated, each running its own. <strong>All the magic of "serial" and "concurrent" hides in this one move of "bucket by key"</strong> — this is in fact Lesson 8's <span class="mono">KeyedMutex</span> idea of "same key serial, different key parallel," polished into a more refined specialized version at the session-execution layer.</p>
<p>It's worth pausing on "why serial is mandatory." An agent session's execution constantly <strong>reads and writes the same shared state</strong>: the current message history, each tool's state, the cumulative token bill. Let two executions run at once and they'd be like two hands editing one sheet of paper — A writes half a sentence, B overwrites it, and in the end no one can say what the sheet should be. Such bugs are also especially insidious: they fire only in the rare moment "two requests happen to collide," untestable in normal times. The coordinator uses the hard rule of "at most one chain per session" to <strong>structurally eliminate</strong> this race — not patching with locks after the fact, but making "two running at once" <strong>simply impossible</strong>. That's a far cleverer solution than "carefully add locks": the best concurrency bugs are the ones designed to be impossible.</p>
<div class="flow">
  <div class="node">inbox<span class="sub">admit + wake (Lesson 15)</span></div>
  <div class="arrow">→</div>
  <div class="node">run coordinator<span class="sub">lane by session</span></div>
  <div class="arrow">drain →</div>
  <div class="node">SessionRunner.run<span class="sub">the real agent loop (Lesson 17)</span></div>
</div>

<h2>run and wake: one departs, one rings</h2>
<p>The coordinator's two main actions, matching the analogy's "depart" and "ring," differ sharply in meaning. <strong><span class="mono">run</span> (depart)</strong> is an <strong>explicit</strong> execution request: idle session starts a new chain, busy session <strong>merges</strong> into the current chain — and on merge the caller still gets "explicit run" semantics (e.g. it can await this trip's actual completion). <strong><span class="mono">wake</span> (ring)</strong> is <strong>advisory</strong>: it merely reports "durable work may now be available" — while idle it starts a chain, but if busy it <strong>only registers one coalesced follow-up</strong>, never a second chain.</p>
<div class="cols">
  <div class="col"><h4>run · explicit depart</h4><p>Actively demand execution. Start a chain, or <strong>merge</strong> into the current one. For "I definitely want this session run now" (e.g. resume).</p></div>
  <div class="col"><h4>wake · advisory ring</h4><p>Report "there may be work." Idle starts a chain; busy <strong>coalesces</strong> into at most one follow-up. After Lesson 15's admit, this is the bell that's rung.</p></div>
</div>
<p>Their divide neatly catches last lesson's design: after admit, <span class="mono">wake</span> is called — because admission is only a hint of "there may be work," and whether and when to actually drain is left to the coordinator's judgment. A request that <strong>must</strong> run, like "the user explicitly clicked resume," takes <span class="mono">run</span>. <strong>Advisory goes to wake, command goes to run</strong>, a line drawn in the same lineage as Lesson 15's "durable goes to admit, advisory goes to wake." This habit of "explicitly distinguishing intents of different strength with different verbs" recurs throughout this code — it lets the scheduler always know "is this a must-run or a maybe-run," and thus make exactly the right trade-off.</p>

<h2>coalesce: ten bells, one extra round</h2>
<p>The coordinator's cleverest stroke is <span class="mono">coalesce</span>. Suppose a session is draining (a drain is running), and during it five more prompts are admitted, ringing <span class="mono">wake</span> five times. The naive way queues five times and runs five trips. But the coordinator keeps <strong>at most one</strong> "pending follow-up": those five wakes are <strong>folded into one</strong>. Why is one enough? Because one drain already <strong>sweeps all currently-eligible rows in the inbox at once</strong> — so you only need, after the current trip finishes, <strong>one more trip</strong> to catch "those that arrived mid-trip," and one suffices.</p>
<pre class="code"><span class="cm">// simplified from session/run-coordinator.ts</span>
<span class="kw">const</span> coalesce = (left, right) =&gt; {
  <span class="kw">if</span> (left?._tag === <span class="st">"run"</span> || right._tag === <span class="st">"run"</span>)
    <span class="kw">return</span> { _tag: <span class="st">"run"</span> }          <span class="cm">// (1) run dominates wake</span>
  <span class="kw">return</span> { _tag: <span class="st">"wake"</span>, seq: <span class="fn">maxSeq</span>(left?.seq, right.seq) }  <span class="cm">// (2) wake keeps newest seq</span>
}</pre>
<p>Two rules only, yet every word is gold. <strong>(1) run dominates wake</strong>: if the pending mixes in one explicit run, the merged result is run — "command" always overrides "advice," because if someone explicitly demanded execution, it can't be demoted to a dispensable bell. <strong>(2) wake keeps the newest seq</strong>: merging two wakes keeps <strong>the larger sequence number</strong> — so the follow-up drain knows to catch at least up to "the latest known admission so far," missing none. <strong>Coalescing isn't discarding but "taking the strongest intent in the union"</strong>: either upgrade to run, or catch up to the latest seq. Ten bell-rings merge into one precise extra round — no idle running, no missed tickets.</p>
<div class="timeline">
  <div class="tl-item"><span class="tl-time">t0</span><span class="tl-desc">drain starts (processes all currently-eligible inbox rows)</span></div>
  <div class="tl-item"><span class="tl-time">t1–t5</span><span class="tl-desc">5 more prompts arrive mid-trip: wake×5, all coalesced into 1 pending</span></div>
  <div class="tl-item"><span class="tl-time">t6</span><span class="tl-desc">this drain ends → sees that 1 pending</span></div>
  <div class="tl-item"><span class="tl-time">t7</span><span class="tl-desc">one extra round sweeps the 5 newcomers at once → back to idle</span></div>
</div>
<p>Why not fear "coalescing drops work"? The key is that seq. Each wake carries "the latest known admission sequence," and merging keeps the max; while a drain's contract is "process all eligible rows up to some sequence." So even if a hundred wakes arrive mid-trip, as long as the coalesced pending remembers that max seq, the extra round is <strong>guaranteed to cover the hundredth</strong>. <strong>Replacing "a long string of duplicate pendings" with "one pending carrying the latest progress"</strong> — this pushes the idempotency idea from Lesson 15's "dedupe by id" onward to the scheduling layer's "converge by seq." Countless redundant drains skipped, yet not one ticket of work lost.</p>

<h2>That state machine: idle → draining → wind-down</h2>
<p>Put the above together and each session lane is really a tiny <strong>state machine</strong>, drawn plainly in the source comment:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">idle</span><span class="t-txt">idle: no execution chain running</span></div>
  <div class="t-row"><span class="t-num">→</span><span class="t-txt">a run/wake arrives → start a drain chain, enter draining</span></div>
  <div class="t-row"><span class="t-num">draining</span><span class="t-txt">draining: further run/wake don't start anew, only coalesce into "at most one pending follow-up"</span></div>
  <div class="t-row"><span class="t-num">→</span><span class="t-txt">this trip ends; if a pending exists → one more trip (coalesced rerun)</span></div>
  <div class="t-row"><span class="t-num">idle</span><span class="t-txt">pending also cleared → back to idle, awaiting the next bell</span></div>
</div>
<p>This state machine's beauty is welding the invariant "<strong>at most one chain runs</strong>" shut: however fierce and dense the outside run/wake come, one session has <strong>at most one drain running plus at most one pending</strong> at a time. It won't lose concurrency control from too-dense requests, nor miss any admitted work due to coalescing. There's also a third action, <span class="mono">interrupt</span>: it can stop the current execution chain — the underlying switch for "cleanly halting an agent deep in thought," which we leave to Lesson 20 to see how it pairs with "bounded steps, error handling." Here just remember: the coordinator manages not only "how to start" but "how to stop."</p>
<div class="cellgroup">
  <div class="cell"><div class="k">run(key)</div><div class="v">explicit depart: start a chain or merge the current</div></div>
  <div class="cell"><div class="k">wake(key, seq?)</div><div class="v">advisory ring: start a chain or coalesce a follow-up</div></div>
  <div class="cell"><div class="k">awaitIdle(key)</div><div class="v">wait until this chain fully finishes, back to idle</div></div>
  <div class="cell"><div class="k">interrupt(key, seq?)</div><div class="v">stop the current execution chain (Lesson 20)</div></div>
</div>

<div class="card macro">
  <div class="tag">🗺️ The big picture</div>
  <p>The coordinator is the <strong>scheduling hub</strong> between the inbox (Lesson 15) and the agent loop (Lesson 17), and the gatekeeper of "concurrency correctness":</p>
  <ul>
    <li><strong>Iron law</strong>: at most one chain per session (serial), each session running its own (concurrent) — via a <span class="mono">Map&lt;Key, Entry&gt;</span> laning by session, a deluxe edition of Lesson 8's KeyedMutex.</li>
    <li><strong>run vs wake</strong>: run is explicit depart (start or merge); wake is advisory ring (start or coalesce a follow-up). After Lesson 15's admit it's wake that's rung.</li>
    <li><strong>coalesce</strong>: mid-trip requests fold into at most one follow-up — run dominates wake, wake keeps newest seq; ten bells become one precise extra round.</li>
    <li><strong>state machine</strong>: idle → draining → at most one coalesced rerun → idle, welding "at most one chain" shut.</li>
  </ul>
  <p>So what kind of loop is it that the coordinator "drains" out, trip by trip, and actually feeds the model to run? How does it turn one user message into the repeated advance of "think → call tool → see result → think again"? That's next lesson's star — the <strong>V2 agent loop (Lesson 17)</strong>, where this brain of opencode truly "thinks."</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source detail</div>
  <p>The coordinator doesn't know what "drain" actually does — it's just a generic serial+coalesce shell, and the real work is decided by the <span class="mono">drain</span> callback passed in. See how <span class="mono">SessionExecution</span> wires the two:</p>
  <pre class="code"><span class="cm">// simplified from session/execution/local.ts</span>
<span class="kw">const</span> coordinator = <span class="kw">yield</span>* SessionRunCoordinator.<span class="fn">make</span>({
  drain: (sessionID, mode) =&gt;                       <span class="cm">// ← coordinator only decides "when, serially" to call it</span>
    SessionRunner.Service.<span class="fn">use</span>((runner) =&gt;
      runner.<span class="fn">run</span>({ sessionID, force: mode === <span class="st">"run"</span> })),  <span class="cm">// ← the real agent loop</span>
})
<span class="cm">// SessionExecution forwards its three actions straight to the coordinator:</span>
{ resume: coordinator.run, wake: coordinator.wake, interrupt: coordinator.interrupt }</pre>
  <p>This is a lovely <strong>separation of concerns</strong>: the coordinator understands only the <strong>pure scheduling</strong> logic of "serial by key, coalesce, start/stop," knowing nothing of "what to run on drain"; while the concrete agent loop (<span class="mono">SessionRunner.run</span>) needn't worry at all about concurrency and queuing. Note that <span class="mono">force: mode === "run"</span> — it passes "is this trip an explicit depart or an advisory ring" through to the runner verbatim, so the downstream can also treat them differently. <strong>Scheduling decoupled from execution</strong>, each readable and testable on its own.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key points</div>
  <ul>
    <li>The run coordinator is the <strong>scheduling hub</strong> between inbox and agent loop: it answers the <span class="mono">wake</span> bell and drains admitted inputs into execution, in order.</li>
    <li><strong>Iron law</strong>: at most one execution chain per session (<strong>serial</strong>), different sessions running their own (<strong>concurrent</strong>) — via <span class="mono">Map&lt;Key, Entry&gt;</span> laning by session, a deluxe KeyedMutex.</li>
    <li><strong>run (explicit depart)</strong> starts or merges the current chain; <strong>wake (advisory ring)</strong> starts or only registers one coalesced follow-up. After admit it's wake that's rung.</li>
    <li><strong>coalesce</strong> folds mid-trip requests into at most one follow-up: <strong>run dominates wake, wake keeps newest seq</strong>, ten bells into one precise rerun — no idle running, no missed tickets.</li>
    <li>Each lane is an <strong>idle→draining→at most one rerun→idle</strong> state machine welding "at most one chain" shut; <span class="mono">interrupt</span> gives the clean-halt switch (Lesson 20).</li>
  </ul>
</div>
""",
}
LESSON_17 = {
    "zh": r"""
<p class="lead">前面三课像在搭舞台：第 14 课认了演员（Session/Message/Part），第 15 课把剧本稳稳收进收件箱，第 16 课的协调器安排了谁先上、谁串行。现在<strong>大幕拉开</strong>——协调器一声 <span class="mono">drain</span>，调用的 <span class="mono">SessionRunner.run</span>，就是 opencode 这颗大脑<strong>真正「思考」的地方</strong>。这一课讲那个让 agent 之所以是 agent 的核心：<strong>「想 → 调工具 → 看结果 → 再想」反复推进的循环</strong>。它不是一次问答，而是一台会自己迭代、自己取数据、自己决定何时收手的引擎。读懂这一课，你就摸到了 opencode 智能的心脏。</p>
<p>为什么这个循环值得一整课？因为「agent」和「聊天机器人」的全部分野，就在这个循环里。聊天机器人是<strong>一问一答</strong>：你说一句，它回一句，完。agent 是<strong>一个目标、多轮自驱</strong>：你给个任务，它自己<strong>反复</strong>地想一步、动一下手（读文件、跑命令）、看看结果、再想下一步——直到任务完成或撞上边界。这一课就拆开这台「自驱循环」：它每一轮干什么、靠什么保证不失控、又怎么把第 15、16 课的 steer/queue 接进来。这是整个第四部分的<strong>引擎舱</strong>。</p>

<div class="card analogy">
  <div class="tag">🔬 生活类比</div>
  把 agent 循环想成一位<strong>查案的研究助理</strong>。你交给他一桩案子，他<strong>不会</strong>当场拍脑袋给结论，而是进入一个节奏：<strong>读一遍当前的案卷</strong>（加载历史）→ <strong>想一想，要么写下结论、要么开几张「调档单」</strong>（模型这一轮的输出：文字 + 工具调用）→ <strong>等档案室把材料送回来、归档</strong>（执行工具、记录结果）→ <strong>把更新后的案卷再从头读一遍</strong>，接着想下一步。如此一轮轮推进，直到案子破了，或者——这点很关键——<strong>轮数撞上了上限（25 轮）</strong>，他就停下来跟你汇报，绝不无休止地查下去。最讲究的一条铁律是：他<strong>每一轮都重新通读整份案卷</strong>，从不凭脑子里那份可能过时的记忆办案。看懂这位一丝不苟的助理，你就看懂了 agent 循环。
</div>

<h2>循环的形状：有界的「想—动」往复</h2>
<p>剥开 <span class="mono">runner/llm.ts</span>，循环的骨架其实异常清晰——两层嵌套，外加一个硬上限：</p>
<pre class="code"><span class="cm">// 简化自 session/runner/llm.ts</span>
<span class="kw">while</span> (openActivity) {                       <span class="cm">// 外层：一个个「活动」</span>
  <span class="kw">for</span> (<span class="kw">let</span> step = 0; step &lt; MAX_STEPS; step++) {  <span class="cm">// 内层：有界的轮次（≤25）</span>
    needsContinuation = <span class="kw">yield</span>* <span class="fn">runTurn</span>(sessionID, promotion)  <span class="cm">// 跑一轮 provider turn</span>
    <span class="kw">if</span> (!needsContinuation) needsContinuation = <span class="kw">yield</span>* <span class="fn">hasPending</span>(<span class="st">"steer"</span>)  <span class="cm">// 有插话→继续</span>
    <span class="kw">if</span> (!needsContinuation) <span class="kw">break</span>             <span class="cm">// 没活了→收手</span>
  }
  <span class="kw">if</span> (needsContinuation) <span class="kw">return</span> <span class="kw">new</span> <span class="fn">StepLimitExceededError</span>({ limit: MAX_STEPS })  <span class="cm">// 撞上限</span>
  openActivity = <span class="kw">yield</span>* <span class="fn">hasPending</span>(<span class="st">"queue"</span>)  <span class="cm">// 还有排队的活动？开下一个</span>
}</pre>
<p>三个层次，各管一摊。<strong>内层 <span class="mono">for</span></strong> 是核心：每转一圈就是一轮 <span class="mono">runTurn</span>——模型「想一步、可能动一次手」。<span class="mono">runTurn</span> 返回一个 <span class="mono">needsContinuation</span>：如果这一轮调了工具、需要看着结果再想，就回 <span class="mono">true</span>，循环继续；如果模型给出了最终答复、无事可做，就回 <span class="mono">false</span>，<span class="mono">break</span> 收手。<strong>外层 <span class="mono">while</span></strong> 管「活动」：当前这摊忙完，看看有没有排队（queue）的新活动要开（呼应第 15 课的 queue 投递）。而那个 <span class="mono">MAX_STEPS = 25</span>，是钉死的<strong>硬上限</strong>：无论模型多想继续，单个活动最多迭代 25 轮，超了就抛 <span class="mono">StepLimitExceededError</span>——这是 agent「绝不无限空转」的安全绳（细节留到第 20 课）。</p>
<div class="cellgroup">
  <div class="cell"><div class="k">外层 while(openActivity)</div><div class="v">一个个「活动」：当前忙完，看有没有排队的 queue 活动要开</div></div>
  <div class="cell"><div class="k">内层 for(step&lt;25)</div><div class="v">有界轮次：每圈一轮 runTurn，最多 25 轮</div></div>
  <div class="cell"><div class="k">runTurn → needsContinuation</div><div class="v">true=调了工具要再想；false=给出最终答复、可收手</div></div>
</div>
<div class="flow">
  <div class="node">读案卷<span class="sub">加载投影历史</span></div>
  <div class="arrow">→</div>
  <div class="node">想 + 开调档单<span class="sub">llm.stream 一轮</span></div>
  <div class="arrow">→</div>
  <div class="node">取材料·归档<span class="sub">执行工具·记结果</span></div>
  <div class="arrow">↺ 再读案卷</div>
  <div class="node">下一轮<span class="sub">≤25 轮·或收手</span></div>
</div>
<p>停下来体会这个「双层 + 上限」的结构有多克制。内层那个 <span class="mono">for</span> 之所以用计数器而非 <span class="mono">while(true)</span>，是因为<strong>模型并不总知道自己该停</strong>——它可能陷进「再查一个文件、再查一个文件」的兔子洞。给它套一个 25 的硬环，等于在「让它自由迭代」和「绝不失控空转」之间，划了一道不容商量的红线。而外层 <span class="mono">while</span> 与内层 <span class="mono">for</span> 的分工也很讲究：一次「活动」是一段完整的自驱任务，里面可以有至多 25 轮往复；活动之间则靠 queue 排队、一个个来。<strong>有界的轮、排队的活动</strong>——两层结构把「单个任务别失控」和「多个任务有秩序」这两件事，干净地分到了两层去管。</p>

<h2>一轮 = 恰好一次 llm.stream</h2>
<p>每一轮 <span class="mono">runTurn</span> 的核心，是源码反复强调的一句话：<strong>「每个 provider turn 恰好一次 <span class="mono">llm.stream(request)</span>」</strong>。模型不是被一口气问完，而是<strong>一轮一次</strong>地被请教。而 <span class="mono">stream</span> 这个词是字面意思——模型的输出是<strong>流式</strong>到达的：先冒出几个思考片段（reasoning），再吐文字（text），中途可能抛出一个工具调用（tool-call）……这些事件<strong>一边到达、一边被增量地存进数据模型</strong>。</p>
<div class="timeline">
  <div class="tl-item"><span class="tl-time">reasoning</span><span class="tl-desc">"我得先看看这个函数怎么写的…" → 即时存为 reasoning part</span></div>
  <div class="tl-item"><span class="tl-time">text</span><span class="tl-desc">"我来帮你重构它。" → 即时存为 text part</span></div>
  <div class="tl-item"><span class="tl-time">tool-call</span><span class="tl-desc">read(file.ts) → 即时存为 tool part（状态 pending）</span></div>
  <div class="tl-item"><span class="tl-time">…</span><span class="tl-desc">流结束 → 这一轮模型「说完」了</span></div>
</div>
<p>还记得第 14 课那个「content 是 part 数组、还能逐 part 增量更新」的设计吗？这里就是它发光的时刻：模型每吐出一个片段，循环就把它<strong>当场塞进当前 Assistant 消息的 content 数组、并发一个事件</strong>。于是第 11 课那条 SSE 河立刻把它推给所有客户端——你在 TUI 里看到的「AI 一个字一个字往外蹦、思考实时展开」，根就在这一轮 stream 的逐事件落盘与推送。<strong>L14 的数据形状、L11 的事件流、L17 的循环</strong>，在这一刻严丝合缝地咬在一起。</p>

<h2>工具：先记账，再动手，并发跑，全等齐</h2>
<p>当这一轮的流里冒出 <span class="mono">tool-call</span>，循环对它的处理藏着几条深思熟虑的纪律。第一条最关键：<strong>先把这次工具调用「durably 记录」下来，再开始任何副作用</strong>。也就是说，「我要调 read(file.ts)」这件事，<strong>先落库</strong>成一个 tool part（状态 pending），<strong>然后</strong>才真去读文件。为什么？因为读文件、跑命令是<strong>有副作用、可能崩、可能被中断</strong>的——万一执行到一半进程挂了，至少「我发起过这个调用」这件事铁证还在，重启后能据此收拾残局（还记得 <span class="mono">run</span> 开头那句 <span class="mono">failInterruptedTools</span> 吗？专门清理上次被打断、卡在 pending/running 的工具）。<strong>这又是第 15 课「先记录意图、再兑现」那条脊梁，在工具层的复刻。</strong></p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">流里来了 tool-call：read(file.ts)</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">先 durably 记成 tool part（pending）—— 副作用还没开始</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">settle：真去执行；作为一个 fiber 丢进 FiberSet 并发跑</span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">多个工具调用 → 多个 fiber 同时跑（第 7 课的结构化并发）</span></div>
  <div class="t-row"><span class="t-num">5</span><span class="t-txt">await 全部 fiber 结束 → 才进入下一轮</span></div>
</div>
<p>第二条纪律：<strong>并发执行、但等齐再走</strong>。一轮里模型可能一口气要调三个工具（比如同时读三个文件）。循环把每个调用<strong>作为一个 fiber 丢进 <span class="mono">FiberSet</span> 并发地跑</strong>——这正是第 7 课结构化并发的用武之地：三个工具同时跑，省时间；但循环<strong>会等这一批全部 settle（成功/失败都算）之后，才进入下一轮</strong>。绝不会「工具还没回来就急着问模型下一步」。<strong>并发求快、等齐求稳</strong>，FiberSet 把这两件事一手包办。每个工具的结果——成功的 result、失败的 error——也都<strong>按类型存回那个 tool part 的 state</strong>（pending → running → completed/error，正是第 14 课那台状态机）。</p>
<div class="cellgroup">
  <div class="cell"><div class="k">① 先记账</div><div class="v">durably 记成 tool part(pending)，再开始任何副作用</div></div>
  <div class="cell"><div class="k">② 并发起</div><div class="v">每个调用一个 fiber，丢进 FiberSet 同时跑</div></div>
  <div class="cell"><div class="k">③ 等齐</div><div class="v">await 这批全部 settle（成败都算）才进下一轮</div></div>
  <div class="cell"><div class="k">④ 按类型存</div><div class="v">result/error 存回 state：pending→running→completed/error</div></div>
</div>
<p>为什么非要「等齐再走」？因为模型下一轮的思考，<strong>必须建立在这一轮所有工具结果都到位的前提上</strong>。设想只回来两个工具结果就急着问模型「接下来怎么办」——它会基于残缺的信息做判断，等第三个结果姗姗来迟，模型早已拐到错误的岔路上。「等齐」保证了每一轮 provider turn 看到的，都是一份<strong>完整、一致的世界状态</strong>，而不是东一块西一块的半成品。这条纪律看似拖慢了节奏，实则是 agent 推理质量的保险：宁可多等那最慢的一个工具，也不让模型在残缺的事实上瞎猜。</p>

<h2>每一轮，都重读案卷</h2>
<p>最后这条纪律，最不起眼，却最能体现 V2 的设计哲学：<strong>每开始新一轮 provider turn 之前，重新加载「投影历史」</strong>。循环<strong>不</strong>把会话状态攒在内存里一路带着跑；它每一轮都<strong>从持久层重新读出</strong>当前完整的历史，据此重新拼出喂给模型的请求。就像那位研究助理，每轮都把案卷从头通读一遍，绝不靠脑子里那份可能过时的记忆。</p>
<div class="cols">
  <div class="col"><h4>❌ 内存里攒状态</h4><p>把历史攒在内存变量里一路带。快，但：崩了就丢、别处改了不知道、用户中途插的话进不来。状态成了一份脆弱的私货。</p></div>
  <div class="col"><h4>✅ 每轮重读投影历史</h4><p>每轮从持久层重新读。慢一点点，但：崩了能接着跑、永远是最新真相、用户的 steer 下一轮自动并入。持久层是唯一权威。</p></div>
</div>
<p>这条「每轮重读」看着笨，实则是 agent 一切高级能力的<strong>地基</strong>。正因为每轮都回持久层取最新真相，第 15 课那个 <span class="mono">steer</span>（插话）才能生效：你在模型忙活时补的一句话，被 admit 进收件箱、提单成一条新消息——<strong>下一轮重读案卷时，它自然就在里面了</strong>，模型当轮就能看到、就能顺着改。循环里那句 <span class="mono">if (!needsContinuation) needsContinuation = hasPending("steer")</span> 正是这个意思：哪怕模型本想收手，只要收件箱里还有你刚插的话，循环就再转一圈去消化它。<strong>「每轮重读」不是性能负担，而是 agent 能被实时引导、能从崩溃中恢复、能多端一致的总开关。</strong>它也正是第 19 课「投影历史」要专门展开的主题。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <p>这一课是第四部分的<strong>引擎舱</strong>，把前几课的零件全点着了：</p>
  <ul>
    <li><strong>循环形状</strong>：<span class="mono">while(activity) { for(step&lt;25) { runTurn } }</span>——「想→动→看→再想」的有界往复，超 25 轮抛 <span class="mono">StepLimitExceededError</span>。</li>
    <li><strong>一轮 = 一次 <span class="mono">llm.stream</span></strong>：模型流式输出 reasoning/text/tool-call，逐事件增量落盘（喂活第 14 课的 part 数组、第 11 课的 SSE）。</li>
    <li><strong>工具</strong>：先 durably 记账、再动手；用 FiberSet 并发跑、await 全部 settle 才继续（第 7 课结构化并发）。</li>
    <li><strong>每轮重读投影历史</strong>：持久层是唯一真相——这让 steer 能即时并入、崩溃能恢复、多端能一致。</li>
  </ul>
  <p>循环里被一笔带过的两件事，各自还要展开成一整课：工具调用具体怎么被 FiberSet 并发驱动、怎么把权限和结果安顿好——是第 18 课；而那个被反复重读的「投影历史」到底是什么、怎么从一堆事件投影出来——是第 19 课。这一课先建立总图：<strong>agent 之所以会「自己干活」，靠的就是这台有界、流式、先记账、每轮重读的循环。</strong></p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p>源码顶部有一段长长的「契约清单」注释，几乎是这台循环的<strong>设计说明书</strong>。摘几条已落实（<span class="mono">[x]</span>）的，正好对上本课四节：</p>
  <pre class="code"><span class="cm">// 摘自 session/runner/llm.ts 顶部契约注释</span>
[x] Bound model steps.                               <span class="cm">// 有界：MAX_STEPS=25</span>
[x] Stream exactly one llm.stream(request) per turn. <span class="cm">// 一轮一次 stream</span>
[x] Persist reasoning/text/tool-call incrementally.  <span class="cm">// 逐事件增量落盘</span>
[x] Durably record each tool call before side effects begin.  <span class="cm">// 先记账再动手</span>
[x] Start each call eagerly and await all settlements.        <span class="cm">// 并发起、等齐</span>
[x] Reload projected history before the next provider turn.   <span class="cm">// 每轮重读</span>
[x] Continue for durable user steering accepted mid-turn.     <span class="cm">// steer 即时并入</span></pre>
  <p>把代码当文档来写，是这套代码库的一个习惯：用一张带 <span class="mono">[x]</span>/<span class="mono">[ ]</span> 的清单，把「这台循环已经做到了什么、还差什么」一目了然地钉在文件最显眼处。你读这段注释，等于读到了作者亲手画的循环边界——本课讲的每一条，都能在这张清单上找到对应的那一行。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li>agent 循环是 opencode 真正「思考」的地方：<strong>「想→调工具→看结果→再想」的有界往复</strong>，这正是 agent 区别于一问一答聊天机器人的根本。</li>
    <li><strong>形状</strong>：<span class="mono">while(activity){ for(step&lt;MAX_STEPS=25){ runTurn } }</span>；超 25 轮抛 <span class="mono">StepLimitExceededError</span>（第 20 课）。</li>
    <li><strong>一轮 = 恰好一次 <span class="mono">llm.stream(request)</span></strong>：reasoning/text/tool-call 流式到达、<strong>逐事件增量落盘</strong>，喂活第 14 课的 part 数组与第 11 课的 SSE 实时推送。</li>
    <li><strong>工具纪律</strong>：先 durably 记账、再动副作用（崩溃可收拾）；用 <strong>FiberSet 并发</strong>跑、<strong>await 全部 settle</strong> 才进下一轮（第 7 课）。</li>
    <li><strong>每轮重读投影历史</strong>（不在内存攒状态）：持久层即唯一真相——这是 steer 即时并入、崩溃恢复、多端一致的总开关（第 19 课展开）。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">The past three lessons were like setting a stage: Lesson 14 met the actors (Session/Message/Part), Lesson 15 steadily filed the script into the inbox, Lesson 16's coordinator arranged who goes first and runs serially. Now <strong>the curtain rises</strong> — the coordinator calls <span class="mono">drain</span>, invoking <span class="mono">SessionRunner.run</span>, which is where opencode's brain <strong>truly "thinks."</strong> This lesson is about the core that makes an agent an agent: <strong>the loop that repeatedly advances "think → call tool → see result → think again."</strong> It's not one Q&A but an engine that iterates itself, fetches its own data, and decides on its own when to stop. Understand this lesson and you've touched the heart of opencode's intelligence.</p>
<p>Why does this loop deserve a whole lesson? Because the entire divide between an "agent" and a "chatbot" lives in it. A chatbot is <strong>one ask, one answer</strong>: you say a line, it replies, done. An agent is <strong>one goal, many self-driven rounds</strong>: you give a task and it <strong>repeatedly</strong> thinks a step, acts (reads a file, runs a command), checks the result, thinks the next step — until the task is done or it hits a boundary. This lesson unpacks that "self-driving loop": what it does each round, what keeps it from running wild, and how it wires in Lessons 15-16's steer/queue. This is Part 4's <strong>engine room</strong>.</p>

<div class="card analogy">
  <div class="tag">🔬 Analogy</div>
  Think of the agent loop as a <strong>research assistant working a case</strong>. You hand him a case, and he <strong>doesn't</strong> blurt a conclusion on the spot; he enters a rhythm: <strong>read the current case file once</strong> (load history) → <strong>think, then either write conclusions or file a few "records requests"</strong> (this round's model output: text + tool calls) → <strong>wait for the archive to send materials back, file them</strong> (execute tools, record results) → <strong>read the updated case file from the top again</strong>, then think the next step. Round after round, until the case is cracked, or — crucially — <strong>the round count hits its ceiling (25 rounds)</strong>, at which he stops and reports to you, never investigating endlessly. His strictest iron rule: he <strong>rereads the whole case file every round</strong>, never working from a possibly-stale memory in his head. See this meticulous assistant and you've seen the agent loop.
</div>

<h2>The loop's shape: a bounded "think–act" back-and-forth</h2>
<p>Peel open <span class="mono">runner/llm.ts</span> and the loop's skeleton is remarkably clear — two nested levels plus a hard ceiling:</p>
<pre class="code"><span class="cm">// simplified from session/runner/llm.ts</span>
<span class="kw">while</span> (openActivity) {                       <span class="cm">// outer: one "activity" at a time</span>
  <span class="kw">for</span> (<span class="kw">let</span> step = 0; step &lt; MAX_STEPS; step++) {  <span class="cm">// inner: bounded rounds (&le;25)</span>
    needsContinuation = <span class="kw">yield</span>* <span class="fn">runTurn</span>(sessionID, promotion)  <span class="cm">// run one provider turn</span>
    <span class="kw">if</span> (!needsContinuation) needsContinuation = <span class="kw">yield</span>* <span class="fn">hasPending</span>(<span class="st">"steer"</span>)  <span class="cm">// steering → continue</span>
    <span class="kw">if</span> (!needsContinuation) <span class="kw">break</span>             <span class="cm">// nothing left → stop</span>
  }
  <span class="kw">if</span> (needsContinuation) <span class="kw">return</span> <span class="kw">new</span> <span class="fn">StepLimitExceededError</span>({ limit: MAX_STEPS })  <span class="cm">// hit ceiling</span>
  openActivity = <span class="kw">yield</span>* <span class="fn">hasPending</span>(<span class="st">"queue"</span>)  <span class="cm">// a queued activity left? open the next</span>
}</pre>
<p>Three levels, each minding its own. <strong>The inner <span class="mono">for</span></strong> is the core: each turn is one <span class="mono">runTurn</span> — the model "thinks a step, maybe acts once." <span class="mono">runTurn</span> returns a <span class="mono">needsContinuation</span>: if this round called a tool and needs to see results then think more, it returns <span class="mono">true</span> and the loop continues; if the model gave its final reply with nothing to do, it returns <span class="mono">false</span> and <span class="mono">break</span>s. <strong>The outer <span class="mono">while</span></strong> minds "activities": when the current one's done, check whether there's a queued (queue) new activity to open (echoing Lesson 15's queue delivery). And that <span class="mono">MAX_STEPS = 25</span> is a nailed-down <strong>hard ceiling</strong>: however much the model wants to continue, a single activity iterates at most 25 rounds; exceed it and it throws <span class="mono">StepLimitExceededError</span> — the agent's "never spin forever" safety rope (details in Lesson 20).</p>
<div class="cellgroup">
  <div class="cell"><div class="k">outer while(openActivity)</div><div class="v">one "activity" at a time: when done, check for a queued activity to open</div></div>
  <div class="cell"><div class="k">inner for(step&lt;25)</div><div class="v">bounded rounds: one runTurn per loop, at most 25</div></div>
  <div class="cell"><div class="k">runTurn → needsContinuation</div><div class="v">true=called tools, think more; false=final reply, may stop</div></div>
</div>
<div class="flow">
  <div class="node">read the file<span class="sub">load projected history</span></div>
  <div class="arrow">→</div>
  <div class="node">think + file requests<span class="sub">one llm.stream</span></div>
  <div class="arrow">→</div>
  <div class="node">fetch · file results<span class="sub">execute tools · record</span></div>
  <div class="arrow">↺ reread file</div>
  <div class="node">next round<span class="sub">&le;25 rounds · or stop</span></div>
</div>
<p>Pause to feel how restrained this "two levels + ceiling" structure is. The inner <span class="mono">for</span> uses a counter rather than <span class="mono">while(true)</span> because <strong>the model doesn't always know to stop</strong> — it can fall down a "check one more file, one more file" rabbit hole. Putting a hard ring of 25 around it draws a non-negotiable red line between "let it iterate freely" and "never spin out of control." The split between outer <span class="mono">while</span> and inner <span class="mono">for</span> is also deliberate: one "activity" is a complete self-driven task, within which there can be up to 25 rounds of back-and-forth; between activities, queue lines them up one at a time. <strong>Bounded rounds, queued activities</strong> — the two levels cleanly split "don't let one task run wild" from "keep multiple tasks orderly."</p>

<h2>One round = exactly one llm.stream</h2>
<p>The core of each <span class="mono">runTurn</span> is a line the source stresses repeatedly: <strong>"exactly one <span class="mono">llm.stream(request)</span> per provider turn."</strong> The model isn't asked all at once but consulted <strong>once per round</strong>. And <span class="mono">stream</span> is literal — the model's output arrives <strong>streaming</strong>: first a few thinking fragments (reasoning), then text, possibly throwing a tool-call mid-way… these events <strong>are persisted incrementally into the data model as they arrive</strong>.</p>
<div class="timeline">
  <div class="tl-item"><span class="tl-time">reasoning</span><span class="tl-desc">"Let me first see how this function is written…" → instantly stored as a reasoning part</span></div>
  <div class="tl-item"><span class="tl-time">text</span><span class="tl-desc">"I'll help you refactor it." → instantly stored as a text part</span></div>
  <div class="tl-item"><span class="tl-time">tool-call</span><span class="tl-desc">read(file.ts) → instantly stored as a tool part (state pending)</span></div>
  <div class="tl-item"><span class="tl-time">…</span><span class="tl-desc">stream ends → this round the model has "finished speaking"</span></div>
</div>
<p>Remember Lesson 14's design of "content is a part array, updatable incrementally part by part"? This is its moment to shine: every fragment the model emits, the loop <strong>slots straight into the current Assistant message's content array and emits an event</strong>. So Lesson 11's SSE river immediately pushes it to all clients — the "AI spitting one character at a time, thinking unfolding live" you see in the TUI is rooted in this round's per-event landing and pushing. <strong>L14's data shape, L11's event stream, L17's loop</strong> mesh seamlessly at this moment.</p>

<h2>Tools: record first, then act, run concurrently, await all</h2>
<p>When a <span class="mono">tool-call</span> emerges in this round's stream, the loop's handling hides several deliberate disciplines. The first is most crucial: <strong>durably record this tool call first, before any side effect begins</strong>. That is, "I'm going to call read(file.ts)" <strong>lands first</strong> as a tool part (state pending), and <strong>only then</strong> does it actually read the file. Why? Because reading files and running commands have <strong>side effects, can crash, can be interrupted</strong> — if the process dies mid-execution, at least the ironclad record "I initiated this call" remains, so a restart can clean up the aftermath (remember that <span class="mono">failInterruptedTools</span> line at the start of <span class="mono">run</span>? it specifically clears tools left pending/running by a prior interruption). <strong>This is Lesson 15's backbone of "record intent first, fulfil later," replicated at the tool layer.</strong></p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">a tool-call arrives in the stream: read(file.ts)</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">durably record as a tool part (pending) first — side effects not yet begun</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">settle: actually execute; tossed as a fiber into a FiberSet, run concurrently</span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">multiple tool calls → multiple fibers running at once (Lesson 7's structured concurrency)</span></div>
  <div class="t-row"><span class="t-num">5</span><span class="t-txt">await all fibers to finish → only then enter the next round</span></div>
</div>
<p>The second discipline: <strong>execute concurrently, but await all before moving on</strong>. In one round the model may call three tools at once (e.g. read three files). The loop tosses each call <strong>as a fiber into a <span class="mono">FiberSet</span> to run concurrently</strong> — exactly Lesson 7's structured concurrency at work: three tools run at once, saving time; but the loop <strong>waits for the whole batch to settle (success or failure) before entering the next round</strong>. It never "rushes to ask the model the next step before the tools are back." <strong>Concurrent for speed, await-all for stability</strong>, FiberSet handles both. Each tool's result — a success's result, a failure's error — is also <strong>stored by type back into that tool part's state</strong> (pending → running → completed/error, exactly Lesson 14's state machine).</p>
<div class="cellgroup">
  <div class="cell"><div class="k">① record first</div><div class="v">durably store as a tool part(pending) before any side effect</div></div>
  <div class="cell"><div class="k">② start concurrently</div><div class="v">one fiber per call, tossed into a FiberSet to run at once</div></div>
  <div class="cell"><div class="k">③ await all</div><div class="v">await the whole batch to settle (success or fail) before the next round</div></div>
  <div class="cell"><div class="k">④ store by type</div><div class="v">result/error back into state: pending→running→completed/error</div></div>
</div>
<p>Why insist on "await all before moving on"? Because the model's next round of thinking <strong>must rest on the premise that all of this round's tool results are in</strong>. Imagine rushing to ask the model "what next" with only two of three results back — it would judge on incomplete information, and by the time the third result trickles in, the model has long taken a wrong fork. "Await all" guarantees that each provider turn sees a <strong>complete, consistent world state</strong>, not a half-built patchwork. This discipline seems to slow the pace but is actually insurance for the agent's reasoning quality: better to wait for the slowest tool than let the model guess on incomplete facts.</p>

<h2>Every round, reread the case file</h2>
<p>This last discipline is the least conspicuous yet most telling of V2's design philosophy: <strong>before starting each new provider turn, reload the "projected history."</strong> The loop does <strong>not</strong> hoard session state in memory and carry it along; it <strong>rereads the full current history from the durable layer</strong> each round, and rebuilds from it the request fed to the model. Just like that research assistant, rereading the whole case file every round, never relying on a possibly-stale memory in his head.</p>
<div class="cols">
  <div class="col"><h4>❌ hoard state in memory</h4><p>Keep history in a memory variable and carry it. Fast, but: a crash loses it, changes elsewhere go unseen, the user's mid-flight steering can't get in. State becomes fragile private cargo.</p></div>
  <div class="col"><h4>✅ reread projected history each round</h4><p>Reread from the durable layer each round. A touch slower, but: a crash can resume, it's always the latest truth, the user's steer auto-merges next round. The durable layer is the sole authority.</p></div>
</div>
<p>This "reread each round" looks dumb but is actually the <strong>foundation</strong> of all the agent's advanced abilities. Precisely because each round goes back to the durable layer for the latest truth, Lesson 15's <span class="mono">steer</span> (cut-in) can take effect: a line you add while the model is busy gets admitted into the inbox, promoted into a new message — and <strong>when the next round rereads the case file, it's naturally in there</strong>, visible and followable that very round. The loop's line <span class="mono">if (!needsContinuation) needsContinuation = hasPending("steer")</span> means exactly this: even if the model meant to stop, as long as there's a steer you just inserted in the inbox, the loop runs one more round to digest it. <strong>"Reread each round" isn't a performance burden but the master switch for an agent being live-steerable, crash-recoverable, and multi-client consistent.</strong> It's also exactly the theme Lesson 19's "projected history" will unfold.</p>

<div class="card macro">
  <div class="tag">🗺️ The big picture</div>
  <p>This lesson is Part 4's <strong>engine room</strong>, igniting all the parts from prior lessons:</p>
  <ul>
    <li><strong>Loop shape</strong>: <span class="mono">while(activity) { for(step&lt;25) { runTurn } }</span> — a bounded "think→act→see→think again" back-and-forth, over 25 rounds throws <span class="mono">StepLimitExceededError</span>.</li>
    <li><strong>One round = one <span class="mono">llm.stream</span></strong>: the model streams reasoning/text/tool-call, persisted per-event incrementally (feeding Lesson 14's part array, Lesson 11's SSE).</li>
    <li><strong>Tools</strong>: durably record first, then act; run concurrently via FiberSet, await all settlements before continuing (Lesson 7's structured concurrency).</li>
    <li><strong>Reread projected history each round</strong>: the durable layer is the sole truth — this lets steer merge instantly, crashes recover, clients stay consistent.</li>
  </ul>
  <p>The two things the loop glosses over each unfold into a whole lesson: how tool calls are concurrently driven by FiberSet and how permissions and results are settled — that's Lesson 18; and what that repeatedly-reread "projected history" actually is and how it's projected from a pile of events — that's Lesson 19. This lesson builds the master diagram first: <strong>the reason the agent "works on its own" is this bounded, streaming, record-first, reread-each-round loop.</strong></p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source detail</div>
  <p>At the top of the source is a long "contract checklist" comment, almost the loop's <strong>design spec</strong>. A few done (<span class="mono">[x]</span>) items map right onto this lesson's four sections:</p>
  <pre class="code"><span class="cm">// from the contract comment atop session/runner/llm.ts</span>
[x] Bound model steps.                               <span class="cm">// bounded: MAX_STEPS=25</span>
[x] Stream exactly one llm.stream(request) per turn. <span class="cm">// one stream per round</span>
[x] Persist reasoning/text/tool-call incrementally.  <span class="cm">// per-event incremental landing</span>
[x] Durably record each tool call before side effects begin.  <span class="cm">// record first, act later</span>
[x] Start each call eagerly and await all settlements.        <span class="cm">// concurrent start, await all</span>
[x] Reload projected history before the next provider turn.   <span class="cm">// reread each round</span>
[x] Continue for durable user steering accepted mid-turn.     <span class="cm">// steer merges instantly</span></pre>
  <p>Writing code as documentation is a habit of this codebase: a checklist with <span class="mono">[x]</span>/<span class="mono">[ ]</span> nails "what this loop already does, what's still missing" right at the file's most visible spot. Reading this comment is reading the author's own hand-drawn loop boundary — every point this lesson makes has a corresponding line on that checklist.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key points</div>
  <ul>
    <li>The agent loop is where opencode truly "thinks": <strong>a bounded "think→call tool→see result→think again" back-and-forth</strong> — exactly what separates an agent from a one-ask-one-answer chatbot.</li>
    <li><strong>Shape</strong>: <span class="mono">while(activity){ for(step&lt;MAX_STEPS=25){ runTurn } }</span>; over 25 rounds throws <span class="mono">StepLimitExceededError</span> (Lesson 20).</li>
    <li><strong>One round = exactly one <span class="mono">llm.stream(request)</span></strong>: reasoning/text/tool-call arrive streaming, <strong>persisted per-event incrementally</strong>, feeding Lesson 14's part array and Lesson 11's live SSE push.</li>
    <li><strong>Tool discipline</strong>: durably record first, then side-effect (crash-cleanable); run <strong>concurrently via FiberSet</strong>, <strong>await all settlements</strong> before the next round (Lesson 7).</li>
    <li><strong>Reread projected history each round</strong> (no in-memory state hoarding): the durable layer is the sole truth — the master switch for instant steer-merge, crash recovery, and multi-client consistency (unfolded in Lesson 19).</li>
  </ul>
</div>
""",
}
LESSON_18 = {
    "zh": r"""
<p class="lead">上一课，我们站在高处俯瞰了 agent 循环：「想→调工具→看结果→再想」。其中「调工具」那一步被一笔带过——「丢进 FiberSet 并发跑、等齐再走」。这一课，我们<strong>蹲下来，把那一步拆到底</strong>：工具是怎么被「亮」给模型看的（而且只亮它有权用的）？一次调用具体怎么被执行、结果怎么安顿？那个 <span class="mono">FiberSet</span> 凭什么能让一群并发的工具「要么齐头并进、要么一声令下全体召回」？还有，模型正调着工具时被中断，怎么保证不留下半拉子的烂摊子？这一课是循环的<strong>引擎舱里的引擎舱</strong>——工具执行的精密机械。</p>
<p>为什么值得为「调工具」单开一课？因为工具是 agent <strong>伸向真实世界的手</strong>。模型本身只会生成文本，是工具让它能读文件、改代码、跑命令——可一旦能「动手」，安全与正确就成了头等大事：不该让模型用的工具，绝不能亮给它；并发跑的工具，必须能被干净地整体叫停；动到一半被打断，绝不能把数据撕成两半；产出一大坨输出，不能把会话历史撑爆。这一课就看 opencode 用 <span class="mono">ToolRegistry</span>、<span class="mono">FiberSet</span> 和一套中断纪律，怎么把「让模型安全地动手」这件险事，办得稳稳当当。</p>

<div class="card analogy">
  <div class="tag">🏗️ 生活类比</div>
  把工具执行想成一个<strong>工地的调度台</strong>。开工前，门口的<strong>器械库管理员</strong>（ToolRegistry）按你的<strong>权限</strong>发料：你的工牌能领什么，台账上就只列什么——没权限的电锯，连出现在清单上的资格都没有（这就是「按权限亮工具」）。开工后，调度台把活派给一支<strong>工人队</strong>：可以一口气派出三个人同时干（并发），调度板上<strong>记着每一个人</strong>（FiberSet），既能等全队收工，也能在任一人出事时立刻知道——更关键的是，一声哨响能把<strong>全队整建制召回</strong>，绝不留下还在角落里闷头干的散兵。还有两条规矩：工人干活时可以中途叫停，但<strong>必须等记录员把这一笔写完账</strong>，才准撤（不留烂账）；干出来的大件成品不堆在办公桌上，而是<strong>送进仓库、桌上只留一张提货单</strong>（输出落盘、消息里只存路径）。看懂这个调度台，你就看懂了 opencode 的工具执行。
</div>

<h2>materialize：只把「有权用的」工具亮给模型</h2>
<p>一切的起点，是 <span class="mono">ToolRegistry.materialize(permissions)</span>（<span class="mono">tool/registry.ts</span>）。它做两件事，产出一个 <span class="mono">Materialization</span>：一份要<strong>亮给模型看</strong>的工具清单（<span class="mono">definitions</span>），和一个<strong>用来执行单次调用</strong>的 <span class="mono">settle</span> 函数。这里最要紧的，是 <span class="mono">definitions</span> 的生成<strong>带着权限过滤</strong>：</p>
<pre class="code"><span class="cm">// 简化自 tool/registry.ts —— materialize 时按权限筛掉禁用工具</span>
<span class="kw">for</span> (<span class="kw">const</span> name <span class="kw">of</span> registrations.<span class="fn">keys</span>()) {
  <span class="kw">if</span> (<span class="fn">whollyDisabled</span>(<span class="fn">permission</span>(tool, name), permissions))
    registrations.<span class="fn">delete</span>(name)        <span class="cm">// ← 没权限的工具，直接从清单移除</span>
}
<span class="kw">return</span> { definitions: ..., settle: ... }   <span class="cm">// 只有"亮得出来"的，才进 definitions</span></pre>
<p>这一步的分量，怎么强调都不过分。模型能调什么工具，<strong>不是模型说了算，是权限说了算</strong>。一个被权限「完全禁用」的工具，根本<strong>不会出现在亮给模型的清单里</strong>——模型连它的存在都不知道，自然无从调起。这比「模型调了、我们再拦」要干净得多：<strong>最好的拦截，是让那个选项压根不出现</strong>。这又是全书反复出现的那个思路——把约束做进「形状」里，而不是事后补救。materialize 产出的 <span class="mono">definitions</span>，就是这一轮模型眼中「世界上存在哪些工具」的<strong>完整且唯一</strong>的真相。</p>
<p>这里还藏着一个微妙却重要的点：权限过滤发生在 <span class="mono">materialize</span> 这个<strong>每轮都会重跑</strong>的环节，而不是一次性写死在某处。这意味着权限是<strong>动态、随上下文生效</strong>的——同一个工具，在权限收紧的语境下这一轮就可能不出现，在放开的语境下又重新亮出来。把「亮哪些工具」做成每轮按当前权限重算的结果，而非启动时定死的清单，agent 才谈得上「在不同 agent、不同场景下，能力边界随之伸缩」（第 45 课的 agent 会用到这点）。<strong>权限不是一道一次性的闸门，而是每轮重新校准的视野。</strong></p>
<div class="cellgroup">
  <div class="cell"><div class="k">definitions</div><div class="v">亮给模型的工具清单——已按权限筛过，禁用的不出现</div></div>
  <div class="cell"><div class="k">settle(call)</div><div class="v">执行单次调用，产出 Settlement（result / output / outputPaths）</div></div>
</div>

<h2>settle：一次调用的落地</h2>
<p>模型在流里抛出一个 <span class="mono">tool-call</span>（比如 <span class="mono">read(file.ts)</span>），循环就调 <span class="mono">toolMaterialization.settle({sessionID, agent, assistantMessageID, call})</span>。这个 <span class="mono">settle</span> 顺着注册表找到对应的工具实现，执行它，再把产物打包成一个 <span class="mono">Settlement</span> 交回来。回顾上一课的纪律：这次执行<strong>之前</strong>，那条 <span class="mono">tool-call</span> 已经被 durably 记成 pending 的 tool part 了；<span class="mono">settle</span> 跑完，结果（成功的 <span class="mono">result</span>、失败的 <span class="mono">error</span>）再按类型写回那台 <span class="mono">ToolState</span> 状态机（第 14 课）。<span class="mono">settle</span> 是「契约」与「真实副作用」之间的<strong>那道门</strong>：门内是声明好的工具定义，门外是真去读文件、真去跑命令。</p>
<div class="flow">
  <div class="node">materialize<span class="sub">按权限出清单</span></div>
  <div class="arrow">definitions →</div>
  <div class="node">模型这一轮<span class="sub">只见有权工具</span></div>
  <div class="arrow">tool-call →</div>
  <div class="node">settle<span class="sub">找实现·执行</span></div>
  <div class="arrow">Settlement →</div>
  <div class="node">写回 state<span class="sub">completed/error</span></div>
</div>

<h2>FiberSet：一群工人，一声召回</h2>
<p>关键来了：一轮里若有多个 <span class="mono">tool-call</span>，循环不是一个个排队跑，而是把每个 <span class="mono">settle</span> <strong>作为一个 fiber 丢进同一个 <span class="mono">FiberSet</span></strong>（<span class="mono">FiberSet.run(toolFibers)</span>），让它们<strong>并发</strong>。但 <span class="mono">FiberSet</span> 的精髓，远不止「并发」二字——它是一个<strong>被整体管理的 fiber 集合</strong>。看它的几个动作：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">make</span><span class="t-txt">建一个空集合：toolFibers = FiberSet.make()</span></div>
  <div class="t-row"><span class="t-num">run</span><span class="t-txt">每个工具调用 → FiberSet.run(toolFibers)，并发起跑、纳入集合</span></div>
  <div class="t-row"><span class="t-num">await</span><span class="t-txt">raceFirst(join, awaitEmpty)：要么全完成、要么一出错就立刻知道</span></div>
  <div class="t-row"><span class="t-num">clear</span><span class="t-txt">一旦被中断（Cause.hasInterrupts）→ FiberSet.clear：全体召回</span></div>
</div>
<p>把它和最朴素的 <span class="mono">Promise.all</span> 比一比，差别就出来了。<span class="mono">Promise.all</span> 是「发射后不管」：你启动一批 Promise，它们就在外面野跑，你<strong>没法把它们叫回来</strong>——某个失败了，其余的还在闷头跑，徒耗资源。<span class="mono">FiberSet</span> 不一样：集合里的每个 fiber 都<strong>被记着、可召回</strong>。所以当这一轮被中断（用户喊停、或某工具失败要求收场），一句 <span class="mono">FiberSet.clear</span> 就能把<strong>所有还在飞的工具 fiber 干净地全部取消</strong>，绝不留下「主流程都结束了、某个工具还在后台改文件」的幽灵。这正是第 7 课<strong>结构化并发</strong>的灵魂：<strong>开出去多少，就能一口气收回多少</strong>，不留野线程。</p>
<div class="cols">
  <div class="col"><h4>Promise.all：发射后不管</h4><p>启动一批就撒手。失败时其余仍野跑，无法整体取消。出了范围还在跑的，成了幽灵。</p></div>
  <div class="col"><h4>FiberSet：记账可召回</h4><p>每个 fiber 纳入集合、可整体 clear。中断时一声令下全员撤，开多少收多少，不留野线程。</p></div>
</div>

<h2>中断纪律与输出仓库</h2>
<p>能「整体召回」带来一个新问题：工人正干到一半被叫停，会不会把账记成半拉子？opencode 用 <span class="mono">Effect.uninterruptibleMask((restore) =&gt; restore(settle(...)))</span> 这个第 7 课的招式来守住。它的意思是：默认这块是<strong>不可中断</strong>的（保护那些记账式的关键操作不被撕开），但用 <span class="mono">restore</span> 把<strong>真正执行工具</strong>的那段重新「开放」成可中断——于是<strong>长跑的工具可以被干净地打断，而它周围的记账逻辑却始终原子完整</strong>。中断来了，撕开的是工具执行本身，绝不是「记一半的账」。<strong>该能停的地方能停，该完整的地方完整</strong>，这条线划得清清楚楚。</p>
<div class="cols">
  <div class="col"><h4>外层·不可中断（默认）</h4><p>记账式的关键操作——发起记录、写回状态——被保护，绝不会被中断撕成一半。</p></div>
  <div class="col"><h4>内层·restore 还原可中断</h4><p>真正执行工具的那段重新开放：长跑的命令/读写可被干净打断，不连累周围记账。</p></div>
</div>
<p>为什么这个「默认锁死、局部开放」的方向是对的，而不是反过来？因为对一个要持久、要可恢复的系统来说，<strong>「记账的完整」比「执行能停」优先级更高</strong>。设想反过来——默认可中断、只在执行工具时临时锁住——那么发起记录、写回状态这些动作就暴露在中断的刀口下，一旦在「写了一半 state」时被砍，留下的就是一条<strong>谁也读不懂的烂记录</strong>，比工具没跑完还糟。opencode 选择「外层锁死、内层用 restore 开一扇可中断的窗」，正是把这个优先级<strong>编码进了中断的默认方向</strong>：宁可让长跑工具多挨一会儿才停，也绝不容许账本被撕裂。中断是把锋利的刀，而 <span class="mono">uninterruptibleMask</span> 决定的，是这把刀<strong>只许落在哪儿</strong>。</p>
<p>最后一个零件，关乎「工具吐出一大坨输出」怎么办。想象模型让你 <span class="mono">cat</span> 一个十万行的日志——若把这十万行原样塞进消息历史，下一轮喂给模型时，光这一坨就能把上下文窗口撑爆。opencode 的对策是 <span class="mono">ToolOutputStore</span>：超过阈值（<span class="mono">MAX_LINES = 2000</span> 行 / <span class="mono">MAX_BYTES = 50KB</span>）的输出，<strong>落到磁盘上的一个专门目录</strong>，消息里只留一个 <span class="mono">outputPaths</span> 引用。</p>
<div class="cellgroup">
  <div class="cell"><div class="k">MAX_LINES / MAX_BYTES</div><div class="v">2000 行 / 50KB —— 超了就不塞进消息</div></div>
  <div class="cell"><div class="k">outputPaths</div><div class="v">大输出落盘，消息里只存「提货单」（路径引用）</div></div>
  <div class="cell"><div class="k">RETENTION</div><div class="v">落盘文件保留 7 天，到期清理</div></div>
</div>
<p>这一招的妙处，是<strong>把「给模型看的」和「完整留存的」分了家</strong>。模型的上下文寸土寸金，不该被一坨日志霸占；但那坨日志又不能直接丢——万一用户要看全貌呢？落盘 + 路径引用，让消息保持轻盈、上下文不被撑爆，同时完整产物一份不少地存在仓库里、随时可取。这正是第 42 课「有界输出」的雏形，也再次呼应第 14 课那个反复出现的智慧：<strong>轻的身份与重的内容，分开存。</strong>把这条原则从会话层一路贯彻到工具输出层，正是这套设计前后一致的体现。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <p>这一课把上一课循环里「调工具」那一步，拆成了一套精密机械：</p>
  <ul>
    <li><strong>materialize</strong>：按<strong>权限</strong>产出 <span class="mono">definitions</span>（亮给模型，禁用的不出现）+ <span class="mono">settle</span>（执行单次调用）。最好的拦截是让选项压根不出现。</li>
    <li><strong>settle</strong>：契约与真实副作用之间的那道门；结果按类型写回 ToolState 状态机。</li>
    <li><strong>FiberSet</strong>：被整体管理的并发 fiber 集合——可 <span class="mono">run</span> 并发、可 <span class="mono">await</span> 等齐、可 <span class="mono">clear</span> 一声召回。结构化并发，开多少收多少。</li>
    <li><strong>中断纪律</strong>：<span class="mono">uninterruptibleMask + restore</span> 让工具执行可停、记账逻辑原子。<strong>输出仓库</strong>：大输出落盘、消息存路径。</li>
  </ul>
  <p>到这里，「工具怎么被安全地调」讲透了。但循环每轮都在「重读投影历史」——那份被反复重读、由一堆事件投影出来的「历史」，到底是怎么从第 15 课那些只追加的事件，变成模型能读的一段干净对话的？那是下一课——<strong>投影历史（第 19 课）</strong>——要揭开的魔术。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p>「并发跑、能召回」这套结构化并发，在 <span class="mono">llm.ts</span> 里就是 <span class="mono">FiberSet</span> 的几个动作串起来的：</p>
  <pre class="code"><span class="cm">// 简化自 session/runner/llm.ts</span>
<span class="kw">const</span> toolFibers = <span class="kw">yield</span>* FiberSet.<span class="fn">make</span>()              <span class="cm">// 建集合</span>
<span class="cm">// …每个 tool-call：</span>
<span class="fn">settle</span>(call).<span class="fn">pipe</span>(FiberSet.<span class="fn">run</span>(toolFibers))           <span class="cm">// 并发起跑、纳入集合</span>

<span class="cm">// 等齐：要么全空、要么一出错就返回</span>
<span class="kw">const</span> awaitToolFibers = Effect.<span class="fn">raceFirst</span>(
  FiberSet.<span class="fn">join</span>(fibers), FiberSet.<span class="fn">awaitEmpty</span>(fibers))

<span class="kw">if</span> (Cause.<span class="fn">hasInterrupts</span>(cause)) <span class="kw">yield</span>* FiberSet.<span class="fn">clear</span>(toolFibers)  <span class="cm">// 中断→全体召回</span></pre>
  <p>读 <span class="mono">awaitToolFibers</span> 那行：<span class="mono">raceFirst(join, awaitEmpty)</span>——<span class="mono">awaitEmpty</span> 在「全部干完」时返回，<span class="mono">join</span> 在「任一个失败」时返回，两者赛跑取先到。于是这一句话同时表达了两个意图：<strong>正常时等所有工具齐活，异常时第一时间炸出来</strong>。而 <span class="mono">Cause.hasInterrupts</span> 一旦为真，<span class="mono">FiberSet.clear</span> 立刻把残余 fiber 全部取消——这就是「整体召回」落到代码上的样子。短短几行，把并发、等齐、错误传播、整体取消，全说清了。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>materialize 按权限亮工具</strong>：被禁用的工具<strong>根本不出现</strong>在给模型的 <span class="mono">definitions</span> 里——最好的拦截是让选项压根不出现。</li>
    <li><strong>settle</strong> 是「工具定义」与「真实副作用」之间的门：执行单次调用，结果按类型写回 ToolState 状态机。</li>
    <li><strong>FiberSet</strong> 是被整体管理的并发 fiber 集合：<span class="mono">run</span>（并发）/<span class="mono">awaitToolFibers</span>（等齐或速错）/<span class="mono">clear</span>（一声召回）——结构化并发，开多少收多少，不留野线程。</li>
    <li><strong>对比 <span class="mono">Promise.all</span></strong>：FiberSet 可整体取消，Promise.all 发射后不管；中断时这是「干净收场」与「留下幽灵」的分野。</li>
    <li><strong>中断纪律</strong> <span class="mono">uninterruptibleMask+restore</span>：工具执行可停、记账原子完整；<strong>ToolOutputStore</strong> 把大输出（&gt;2000 行/50KB）落盘、消息只存 <span class="mono">outputPaths</span>，防上下文被撑爆。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Last lesson we surveyed the agent loop from on high: "think→call tool→see result→think again." The "call tool" step was glossed over — "toss into a FiberSet, run concurrently, await all." This lesson, we <strong>crouch down and take that step apart to the bottom</strong>: how are tools "shown" to the model (and only the ones it's permitted)? How is one call actually executed and its result settled? What lets that <span class="mono">FiberSet</span> make a crowd of concurrent tools "either advance together or all be recalled on one command"? And, if the model is interrupted mid-tool-call, how is no half-built mess left behind? This lesson is the loop's <strong>engine room within the engine room</strong> — the precise machinery of tool execution.</p>
<p>Why a whole lesson for "calling tools"? Because tools are the agent's <strong>hand reaching into the real world</strong>. The model itself only generates text; tools are what let it read files, edit code, run commands — but once it can "act," safety and correctness become paramount: a tool the model shouldn't use must never be shown to it; concurrently-running tools must be cleanly halt-able as a whole; an interruption mid-action must never tear the data in two; a huge output must not blow up the session history. This lesson sees how opencode uses <span class="mono">ToolRegistry</span>, <span class="mono">FiberSet</span>, and an interruption discipline to handle the risky business of "letting the model act safely" with steady poise.</p>

<div class="card analogy">
  <div class="tag">🏗️ Analogy</div>
  Think of tool execution as a <strong>construction dispatch desk</strong>. Before work begins, the gate's <strong>equipment-depot keeper</strong> (ToolRegistry) issues gear by your <strong>permit</strong>: only what your badge allows is even listed on the ledger — a chainsaw you lack clearance for doesn't even get to appear on the list ("show tools by permission"). Once work starts, the desk assigns jobs to a <strong>work crew</strong>: it can send three people at once (concurrent), the dispatch board <strong>tracks every one</strong> (FiberSet), can wait for the whole crew to finish, and knows instantly if anyone hits trouble — and crucially, one whistle <strong>recalls the entire crew as a unit</strong>, never leaving stragglers grinding away in a corner. Two more rules: a worker can be stopped mid-task, but <strong>only after the clerk finishes that ledger entry</strong> (no torn records); and bulky finished goods aren't piled on the desk but <strong>sent to a warehouse, leaving only a claim slip on the desk</strong> (output to disk, message holds only a path). See this dispatch desk and you've seen opencode's tool execution.
</div>

<h2>materialize: show the model only the tools it may use</h2>
<p>It all begins with <span class="mono">ToolRegistry.materialize(permissions)</span> (<span class="mono">tool/registry.ts</span>). It does two things, producing a <span class="mono">Materialization</span>: a list of tools to <strong>show the model</strong> (<span class="mono">definitions</span>), and a <span class="mono">settle</span> function to <strong>execute one call</strong>. The most important part is that <span class="mono">definitions</span> is generated <strong>with permission filtering</strong>:</p>
<pre class="code"><span class="cm">// simplified from tool/registry.ts — materialize filters out disabled tools by permission</span>
<span class="kw">for</span> (<span class="kw">const</span> name <span class="kw">of</span> registrations.<span class="fn">keys</span>()) {
  <span class="kw">if</span> (<span class="fn">whollyDisabled</span>(<span class="fn">permission</span>(tool, name), permissions))
    registrations.<span class="fn">delete</span>(name)        <span class="cm">// ← a tool without permission, removed from the list</span>
}
<span class="kw">return</span> { definitions: ..., settle: ... }   <span class="cm">// only "showable" ones enter definitions</span></pre>
<p>This step's weight can't be overstated. What tools the model can call is <strong>not the model's call but the permission's</strong>. A tool "wholly disabled" by permission simply <strong>won't appear in the list shown to the model</strong> — the model doesn't even know it exists, so it can't call it. This is far cleaner than "the model called it, then we block it": <strong>the best interception is making the option not appear at all</strong>. This is again the book's recurring idea — bake the constraint into the "shape," not patch it after. The <span class="mono">definitions</span> materialize produces is the <strong>complete and sole</strong> truth of "what tools exist in the world" in the model's eyes this round.</p>
<p>There's also a subtle but important point here: permission filtering happens in <span class="mono">materialize</span>, a step that <strong>reruns every round</strong>, not hard-coded once somewhere. This means permissions are <strong>dynamic, taking effect by context</strong> — the same tool may not appear this round in a permission-tightened context, and reappear in a loosened one. By making "which tools to show" the result of recomputing against current permissions each round, rather than a list fixed at startup, an agent can have "its capability boundary flex with different agents and scenarios" (Lesson 45's agents use this). <strong>Permission isn't a one-time gate but a field of view recalibrated each round.</strong></p>
<div class="cellgroup">
  <div class="cell"><div class="k">definitions</div><div class="v">the tool list shown to the model — already permission-filtered, disabled ones absent</div></div>
  <div class="cell"><div class="k">settle(call)</div><div class="v">execute one call, producing a Settlement (result / output / outputPaths)</div></div>
</div>

<h2>settle: landing one call</h2>
<p>The model throws a <span class="mono">tool-call</span> in the stream (e.g. <span class="mono">read(file.ts)</span>), and the loop calls <span class="mono">toolMaterialization.settle({sessionID, agent, assistantMessageID, call})</span>. This <span class="mono">settle</span> follows the registry to find the matching tool implementation, executes it, then packs the products into a <span class="mono">Settlement</span> to hand back. Recall last lesson's discipline: <strong>before</strong> this execution, that <span class="mono">tool-call</span> was already durably recorded as a pending tool part; once <span class="mono">settle</span> runs, the result (a success's <span class="mono">result</span>, a failure's <span class="mono">error</span>) is written back by type into that <span class="mono">ToolState</span> machine (Lesson 14). <span class="mono">settle</span> is <strong>the door</strong> between "contract" and "real side effect": inside is the declared tool definition, outside is actually reading the file, actually running the command.</p>
<div class="flow">
  <div class="node">materialize<span class="sub">list by permission</span></div>
  <div class="arrow">definitions →</div>
  <div class="node">model this round<span class="sub">sees only permitted tools</span></div>
  <div class="arrow">tool-call →</div>
  <div class="node">settle<span class="sub">find impl · execute</span></div>
  <div class="arrow">Settlement →</div>
  <div class="node">write back state<span class="sub">completed/error</span></div>
</div>

<h2>FiberSet: a crew of workers, one recall</h2>
<p>Here's the key: if a round has multiple <span class="mono">tool-call</span>s, the loop doesn't queue them one by one but tosses each <span class="mono">settle</span> <strong>as a fiber into one <span class="mono">FiberSet</span></strong> (<span class="mono">FiberSet.run(toolFibers)</span>), running them <strong>concurrently</strong>. But <span class="mono">FiberSet</span>'s essence is far more than "concurrency" — it's a <strong>collectively-managed set of fibers</strong>. See its few actions:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">make</span><span class="t-txt">build an empty set: toolFibers = FiberSet.make()</span></div>
  <div class="t-row"><span class="t-num">run</span><span class="t-txt">each tool call → FiberSet.run(toolFibers), start concurrently, enter the set</span></div>
  <div class="t-row"><span class="t-num">await</span><span class="t-txt">raceFirst(join, awaitEmpty): either all finish, or know the instant one errors</span></div>
  <div class="t-row"><span class="t-num">clear</span><span class="t-txt">once interrupted (Cause.hasInterrupts) → FiberSet.clear: recall everyone</span></div>
</div>
<p>Compare it with the plainest <span class="mono">Promise.all</span> and the difference shows. <span class="mono">Promise.all</span> is "fire and forget": you start a batch of Promises and they run wild outside, you <strong>can't call them back</strong> — one fails and the rest grind on, wasting resources. <span class="mono">FiberSet</span> is different: every fiber in the set is <strong>tracked, recallable</strong>. So when this round is interrupted (user halts, or a tool fails forcing a wrap-up), one <span class="mono">FiberSet.clear</span> can <strong>cleanly cancel all still-flying tool fibers</strong>, never leaving the ghost of "the main flow ended but some tool is still editing a file in the background." This is exactly Lesson 7's <strong>structured concurrency</strong> soul: <strong>collect back as many as you sent out</strong>, leaving no stray threads.</p>
<div class="cols">
  <div class="col"><h4>Promise.all: fire and forget</h4><p>Start a batch and let go. On failure the rest run wild, no whole-set cancel. What runs past scope becomes a ghost.</p></div>
  <div class="col"><h4>FiberSet: tracked, recallable</h4><p>Each fiber enters the set, whole-set clear-able. On interrupt, one command recalls all; collect as many as you sent, no stray threads.</p></div>
</div>

<h2>Interruption discipline and the output warehouse</h2>
<p>Being able to "recall as a whole" brings a new problem: if a worker is stopped mid-task, won't the ledger be left half-written? opencode guards this with Lesson 7's move <span class="mono">Effect.uninterruptibleMask((restore) =&gt; restore(settle(...)))</span>. It means: this block is by default <strong>uninterruptible</strong> (protecting the ledger-like critical operations from being torn open), but <span class="mono">restore</span> reopens <strong>the part that actually executes the tool</strong> as interruptible — so <strong>a long-running tool can be cleanly interrupted, while the bookkeeping around it stays atomic and whole</strong>. When interruption comes, what's torn is the tool execution itself, never "a half-written ledger." <strong>What should be stoppable is stoppable, what should be whole is whole</strong>, the line drawn cleanly.</p>
<div class="cols">
  <div class="col"><h4>outer · uninterruptible (default)</h4><p>Ledger-like critical ops — recording the initiation, writing back state — are protected, never torn in half by an interrupt.</p></div>
  <div class="col"><h4>inner · restore reopens interruptible</h4><p>The part that actually executes the tool is reopened: a long-running command/IO can be cleanly interrupted, without dragging the surrounding bookkeeping.</p></div>
</div>
<p>Why is this direction of "lock by default, open locally" right, not the reverse? Because for a system that must be durable and recoverable, <strong>"ledger integrity" outranks "execution being stoppable."</strong> Imagine the reverse — interruptible by default, locked only while executing the tool — then recording the initiation and writing back state are exposed to the interrupt's blade, and if cut "mid-write of state," what's left is <strong>a record no one can read</strong>, worse than a tool that didn't finish. opencode chooses "lock the outer, open an interruptible window inner via restore," precisely <strong>encoding this priority into the default direction of interruption</strong>: rather let a long tool take a bit longer to stop than ever allow the ledger to be torn. Interruption is a sharp knife, and what <span class="mono">uninterruptibleMask</span> decides is <strong>where the knife may land</strong>.</p>
<p>The last piece concerns what to do when "a tool spews a huge output." Imagine the model asks you to <span class="mono">cat</span> a hundred-thousand-line log — stuffing those hundred thousand lines verbatim into the message history would, on the next round's feed to the model, blow up the context window by itself. opencode's countermeasure is <span class="mono">ToolOutputStore</span>: output exceeding a threshold (<span class="mono">MAX_LINES = 2000</span> lines / <span class="mono">MAX_BYTES = 50KB</span>) <strong>lands in a dedicated directory on disk</strong>, with the message holding only an <span class="mono">outputPaths</span> reference.</p>
<div class="cellgroup">
  <div class="cell"><div class="k">MAX_LINES / MAX_BYTES</div><div class="v">2000 lines / 50KB — beyond it, not stuffed into the message</div></div>
  <div class="cell"><div class="k">outputPaths</div><div class="v">big output to disk, message holds only a "claim slip" (path reference)</div></div>
  <div class="cell"><div class="k">RETENTION</div><div class="v">on-disk files kept 7 days, cleaned on expiry</div></div>
</div>
<p>The beauty of this move is <strong>separating "what's shown to the model" from "what's fully retained."</strong> The model's context is precious real estate, not to be hogged by a log dump; yet that log can't just be discarded — what if the user wants the full picture? Disk + path reference keeps the message light and the context unblown, while the complete product sits in the warehouse, every bit retained, retrievable anytime. This is the prototype of Lesson 42's "bounded output," and again echoes Lesson 14's recurring wisdom: <strong>store the light identity and the heavy content separately.</strong> Carrying this principle all the way from the session layer to the tool-output layer is exactly what makes this design coherent.</p>

<div class="card macro">
  <div class="tag">🗺️ The big picture</div>
  <p>This lesson takes apart the "call tool" step of last lesson's loop into a piece of precise machinery:</p>
  <ul>
    <li><strong>materialize</strong>: produce <span class="mono">definitions</span> by <strong>permission</strong> (shown to the model, disabled ones absent) + <span class="mono">settle</span> (execute one call). The best interception is making the option not appear.</li>
    <li><strong>settle</strong>: the door between contract and real side effect; results written back by type into the ToolState machine.</li>
    <li><strong>FiberSet</strong>: a collectively-managed set of concurrent fibers — <span class="mono">run</span> (concurrent), <span class="mono">await</span> (all-done or fail-fast), <span class="mono">clear</span> (recall on one command). Structured concurrency, collect as many as you send.</li>
    <li><strong>Interruption discipline</strong>: <span class="mono">uninterruptibleMask + restore</span> makes tool execution stoppable, bookkeeping atomic. <strong>Output warehouse</strong>: big output to disk, message holds paths.</li>
  </ul>
  <p>By here, "how tools are called safely" is fully covered. But the loop "rereads projected history" each round — that repeatedly-reread "history," projected from a pile of events, how does it turn Lesson 15's append-only events into a clean conversation the model can read? That's the magic the next lesson — <strong>projected history (Lesson 19)</strong> — unveils.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source detail</div>
  <p>This structured concurrency of "run concurrently, recallable" is, in <span class="mono">llm.ts</span>, just a few <span class="mono">FiberSet</span> actions strung together:</p>
  <pre class="code"><span class="cm">// simplified from session/runner/llm.ts</span>
<span class="kw">const</span> toolFibers = <span class="kw">yield</span>* FiberSet.<span class="fn">make</span>()              <span class="cm">// build the set</span>
<span class="cm">// …each tool-call:</span>
<span class="fn">settle</span>(call).<span class="fn">pipe</span>(FiberSet.<span class="fn">run</span>(toolFibers))           <span class="cm">// start concurrently, enter the set</span>

<span class="cm">// await all: return either when all empty, or when one errors</span>
<span class="kw">const</span> awaitToolFibers = Effect.<span class="fn">raceFirst</span>(
  FiberSet.<span class="fn">join</span>(fibers), FiberSet.<span class="fn">awaitEmpty</span>(fibers))

<span class="kw">if</span> (Cause.<span class="fn">hasInterrupts</span>(cause)) <span class="kw">yield</span>* FiberSet.<span class="fn">clear</span>(toolFibers)  <span class="cm">// interrupt → recall all</span></pre>
  <p>Read the <span class="mono">awaitToolFibers</span> line: <span class="mono">raceFirst(join, awaitEmpty)</span> — <span class="mono">awaitEmpty</span> returns when "all done," <span class="mono">join</span> returns when "any one fails," racing for whichever comes first. So this one line expresses two intents at once: <strong>normally await all tools to finish, abnormally blow up at the first failure</strong>. And once <span class="mono">Cause.hasInterrupts</span> is true, <span class="mono">FiberSet.clear</span> immediately cancels all remaining fibers — that's "recall as a whole" landed in code. A few short lines say it all: concurrency, await-all, error propagation, whole-set cancellation.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key points</div>
  <ul>
    <li><strong>materialize shows tools by permission</strong>: a disabled tool <strong>simply doesn't appear</strong> in the <span class="mono">definitions</span> given to the model — the best interception is making the option not appear at all.</li>
    <li><strong>settle</strong> is the door between "tool definition" and "real side effect": execute one call, result written back by type into the ToolState machine.</li>
    <li><strong>FiberSet</strong> is a collectively-managed set of concurrent fibers: <span class="mono">run</span> (concurrent) / <span class="mono">awaitToolFibers</span> (all-done or fail-fast) / <span class="mono">clear</span> (recall on one command) — structured concurrency, collect as many as you send, no stray threads.</li>
    <li><strong>vs <span class="mono">Promise.all</span></strong>: FiberSet is whole-set cancellable, Promise.all is fire-and-forget; on interrupt this is the divide between "clean wrap-up" and "leaving ghosts."</li>
    <li><strong>Interruption discipline</strong> <span class="mono">uninterruptibleMask+restore</span>: tool execution stoppable, bookkeeping atomic; <strong>ToolOutputStore</strong> lands big output (&gt;2000 lines/50KB) on disk, message holds only <span class="mono">outputPaths</span>, preventing context blow-up.</li>
  </ul>
</div>
""",
}
LESSON_19 = wip('投影历史', 'Projected history')
LESSON_20 = wip('有界步数与错误处理', 'Bounded steps & errors')
