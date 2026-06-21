"""Part 3 (Part 3 · Client/Server) content. Placeholders until M3 fills them in."""
from placeholder import wip

LESSON_09 = {
    "zh": r"""
<p class="lead">第一、二部分搭好了地基：你懂了 opencode 的全貌，也懂了它脚下的 Effect。现在进入第三部分——<strong>客户端/服务器骨架</strong>。这一课先看 <strong>server</strong> 本身：它是怎么对外提供能力的？答案有点出人意料——它<strong>不是 Hono、不是 Express</strong>，而是架在 Effect 的实验性 <span class="mono">HttpApi</span> 上。这个选择不是赶时髦：它让整套 API <strong>类型安全、还能自己描述自己</strong>，进而自动生成 SDK。读懂这一课，你就抓住了所有客户端与 server 对话的总入口。</p>
<p>为什么从 server 讲起，而不是从你天天看的 TUI？因为<strong>server 才是真正"拥有一切"的那个</strong>（第 1 课的主线）。TUI、网页只是它的脸；要理解 opencode 怎么运作，必须先看清这个大脑对外开的那扇门长什么样。这一部分接下来几课——路由组与 handler、事件流、SDK 生成、多客户端传输——都是在放大这扇门的不同侧面。先把门本身看清楚，后面才不至于只见树木。</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  把 server 想成一家酒店的<strong>总服务台</strong>。所有客人（TUI、网页、Slack……）有事都来这一个台子，台子背后挂着一张<strong>分门别类的服务清单</strong>——前台事务、客房、餐饮、叫车……每一类就是一个"路由组"。更妙的是，这张清单是<strong>用统一格式写死的</strong>，于是酒店能<strong>照着它自动印出一本对客手册</strong>（SDK）发给每个客人，手册上每项服务的名字、要填的表格、会得到的回执，全和后台<strong>一字不差</strong>。改了后台一项服务，手册自动跟着改——客人永远不会拿着过期手册来办事。这家酒店还有个讲究：总台<strong>不挑客人</strong>——不管你从大门、侧门还是打电话来，只要按手册说话，就能办成同样的事。这正是 server"广开门户、契约统一"的写照。
</div>

<h2>不是 Hono，而是 Effect 的 HttpApi</h2>
<p>很多 TS 后端用 Hono 或 Express：你写一个个 <span class="mono">app.get("/path", handler)</span>，框架帮你把请求路由到函数。opencode 的 server 走了一条更"Effect"的路——用 <span class="mono">effect/unstable/httpapi</span> 的 <span class="mono">HttpApi</span>。它和 Hono 最大的不同是：<strong>你不是先写路径字符串、再写处理函数，而是先用类型把整套 API 的"形状"声明出来</strong>——每个端点要什么输入、给什么输出、可能怎样失败，全写进类型。</p>
<p>为什么这么做？因为前两课的道理在这里又一次兑现：<strong>把契约抬进类型，编译器就能替你守住它</strong>。端点的输入输出错了，编译期就报错；而且——这是关键——既然整套 API 的形状是<strong>结构化的类型</strong>，机器就能读懂它，从而<strong>自动生成客户端 SDK</strong>（第 12 课）。Hono 给你灵活，HttpApi 给你的是<strong>一份机器可读、前后端共享的契约</strong>。对一个要同时喂养 TUI、网页、桌面、Slack 多个客户端的项目，后者的价值是压倒性的。</p>
<div class="cols">
  <div class="col"><h4>Hono / Express 式</h4><p>先写路径字符串 + 处理函数；灵活，但 API 的"形状"散落在代码各处，机器读不出，前后端各对各的。</p></div>
  <div class="col"><h4>Effect HttpApi 式</h4><p>先用<strong>类型</strong>声明整套 API 的形状；编译器守契约，机器能读懂它，从而<strong>自动生成 SDK</strong>。</p></div>
</div>

<p>这背后其实是一个深刻的取舍：<strong>用一点"先声明形状"的繁琐，换整套系统的可推理性</strong>。Hono 让你三秒写出一个路由，但当端点有几十上百个、还要喂养五六种客户端时，"灵活"就成了"各处对不齐的源头"。HttpApi 逼你先把契约写清楚，看似多花了功夫，实则把"接口会不会对错"这个最烦人的问题，在编译期一次性解决了。这正是第 5 课"把隐性负担变成显性类型"那套世界观，从单个函数<strong>放大到了整个 API 表面</strong>。</p>

<h2>一个 webHandler，收下所有请求</h2>
<p>整个 server 对外，其实就是<strong>一个函数</strong>：把进来的 HTTP <span class="mono">Request</span> 变成 <span class="mono">Response</span>。</p>
<pre class="code"><span class="cm">// 简化自 packages/opencode/src/server/server.ts</span>
<span class="kw">const</span> handler = HttpApiApp.<span class="fn">webHandler</span>().handler
<span class="kw">const</span> server = {
  fetch: (request: Request) =&gt; <span class="fn">handler</span>(request, HttpApiApp.context),
}</pre>
<p>这个 <span class="mono">webHandler</span> 是把所有路由组拼装起来后得到的<strong>总处理器</strong>：一个请求进来，它按路径分发到对应的组、对应的 handler，跑完再把结果编码成 <span class="mono">Response</span>。注意它的形态是标准的 <span class="mono">(request) =&gt; Response</span>——正因为这么"标准"，它既能架在真正的网络服务器上（<span class="mono">NodeHttpServer</span>），也能被<strong>塞进一个进程内的 worker</strong> 直接调用。还记得第 3 课富 TUI 那套"零网络 RPC"吗？底层调的就是这同一个 <span class="mono">fetch</span> 形态的 handler。<strong>一个 handler，两种传输</strong>，根就在这里。</p>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">客户端</span><span class="name">TUI / web / Slack…</span></div><div class="ld">发 HTTP Request（或进程内 RPC）</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">总处理器</span><span class="name">webHandler</span></div><div class="ld">(request) =&gt; Response，按路径分发</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">路由组</span><span class="name">session / event / config… ×21</span></div><div class="ld">各领域的端点契约</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">handler</span><span class="name">handlers/*</span></div><div class="ld">调用 core 服务，干真正的活</div></div>
</div>

<p>"server 对外只是一个函数"这个事实，比它听起来更重要。正因为 handler 的形态如此标准、如此纯粹——进一个 Request、出一个 Response，没有任何对"真实网络"的硬依赖——它才能被随意<strong>嫁接到不同的传输上</strong>：架在 Node 的 HTTP 服务器上，它是个网络服务；塞进一个 worker 线程里直接调用，它就成了富 TUI 那套零网络的进程内通信。<strong>同一套业务逻辑、传输层可热插拔</strong>——这又是第 6 课"实现可整体替换"在 server 这一层的回响。</p>
<p>那 handler 里到底装着什么？一个端点的 handler，干的就是"<strong>把校验过的输入，翻译成对 core 服务的调用，再把结果编码回去</strong>"——它是这扇门和门后真正干活的 core 之间<strong>薄薄的一层转接</strong>。理想情况下 handler 应该很薄：重活都在 core 的 Session、Tool 那些服务里，handler 只负责"在 HTTP 世界和 Effect 世界之间搬运"。下一课就专门拆开路由组与 handler，看这层转接具体长什么样。</p>

<h2>21 个路由组：按领域切开</h2>
<p>这张"服务清单"不是一长串扁平的路径，而是<strong>按领域切成了 21 个组</strong>，各管一摊：</p>
<table class="t">
  <tr><th>组</th><th>管什么</th></tr>
  <tr><td><span class="mono">session</span></td><td>会话：创建、发 prompt、取历史——agent 的主战场</td></tr>
  <tr><td><span class="mono">event</span></td><td>事件流：把 server 内部的事件推给客户端（SSE）</td></tr>
  <tr><td><span class="mono">config</span> · <span class="mono">provider</span></td><td>配置、模型 provider</td></tr>
  <tr><td><span class="mono">permission</span> · <span class="mono">question</span></td><td>权限确认、向用户提问</td></tr>
  <tr><td><span class="mono">file</span> · <span class="mono">project</span> · <span class="mono">pty</span></td><td>文件、项目、伪终端</td></tr>
  <tr><td><span class="mono">mcp</span> · <span class="mono">tui</span> · <span class="mono">workspace</span> …</td><td>MCP、TUI 专用、工作区等（共 21 组）</td></tr>
</table>
<p>"按领域切组"是个很要紧的工程决定。它让庞大的 API 表面变得<strong>可导航</strong>：想找"发 prompt"的接口？去 <span class="mono">session</span> 组；想订阅实时事件？去 <span class="mono">event</span> 组。每个组是一个<strong>独立、内聚的契约单元</strong>，可以单独读、单独改、单独测。这和第二部分"小协作者"的气质一脉相承——<strong>大系统，由清晰分界的小块拼成</strong>。</p>
<div class="flow">
  <div class="node"><div class="nt">POST /session/…</div><div class="nd">请求进来</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">webHandler</div><div class="nd">按路径分发</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">session 组</div><div class="nd">匹配端点、校验输入</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">handler</div><div class="nd">调 core → 编码 Response</div></div>
</div>

<p>顺带说，这 21 个组的名字本身，就是一张 opencode 能力的<strong>地图</strong>：<span class="mono">session</span> 是 agent 主战场，<span class="mono">event</span> 撑起实时性，<span class="mono">permission</span>/<span class="mono">question</span> 管"放手让 AI 干活但可控"，<span class="mono">pty</span>/<span class="mono">file</span> 让它能真的动你的项目，<span class="mono">mcp</span>/<span class="mono">workspace</span> 通向扩展与多实例。你几乎可以靠这份组清单，倒推出 opencode 大致能做哪些事。后面好几课会逐一深入其中的组——它们在 server 这一层的"门牌"，就挂在这里。换句话说，读 server 的路由组，就像读一份目录——你还没翻开任何一章，已经大致知道这本书讲些什么了。</p>

<h2>类型即契约：API 自己描述自己</h2>
<p>HttpApi 最迷人的回报在这一行：</p>
<pre class="code"><span class="cm">// 简化自 server.ts —— 从 API 定义生成 OpenAPI 规范</span>
<span class="kw">return</span> OpenApi.<span class="fn">fromApi</span>(PublicApi)</pre>
<p>因为整套 API 是用类型结构化声明的，<span class="mono">OpenApi.fromApi</span> 能<strong>直接从它生成一份 OpenAPI 规范</strong>——一份机器可读的、描述"这个 server 有哪些端点、各要什么给什么"的标准文档。有了它，就能<strong>自动生成各语言的客户端 SDK</strong>（第 12 课详讲）。这就是开篇那个比喻的兑现：<strong>后台的服务清单，自动印成了发给客人的手册</strong>。API 改一处，规范跟着变，SDK 重新生成，所有客户端的类型立刻同步——再不会有"前端拿着过期接口对不上"的事。</p>
<div class="vflow">
  <div class="step"><b>① 类型声明 API</b>　每个端点的输入/输出/错误都写进类型</div>
  <div class="step"><b>② OpenApi.fromApi</b>　从定义自动生成 OpenAPI 规范</div>
  <div class="step"><b>③ 生成 SDK</b>　据规范生成各语言类型安全的客户端代码</div>
  <div class="step"><b>④ 客户端同步</b>　API 一改，规范变、SDK 重生，所有端类型对齐</div>
</div>
<p>停下来体会一下这条链的分量：它把"<strong>接口契约</strong>"从一份要靠人维护、容易过期的文档，变成了<strong>从代码自动流出的、永不撒谎的产物</strong>。前端再也不用猜后端改了什么，编译器会直接告诉你"这个字段没了"。对一个有 TUI、网页、桌面、Slack 这么多张嘴要喂的项目，这条"<strong>一处定义、处处同步</strong>"的链，省下的是无数次接口对不齐的扯皮。这也是 opencode 宁可用还带"实验性"标签的 HttpApi、也不用成熟 Hono 的根本原因——它赌的是<strong>类型安全的契约</strong>这件事，长期看回报巨大。</p>
<p>值得一提，"自描述的 API"还有个隐藏好处：它天然就是<strong>最新、最准的文档</strong>。新人想知道 server 能干什么，不必去翻散落的注释或过期的 wiki，直接看生成的 OpenAPI 规范、或它生成的 SDK 类型，就一目了然。代码即文档、且永不撒谎——在一个高速演进的项目里，这一点的价值怎么强调都不为过。</p>

<h2>顺带认两个零件：MDNS 与 WebSocket</h2>
<p>server 启动时还带着两个小零件，先混个脸熟：</p>
<div class="cols">
  <div class="col"><h4>MDNS（本地发现）</h4><p>在局域网里<strong>广播自己的存在</strong>，让同机/同网的客户端能自动发现这个 server，不用手填地址。</p></div>
  <div class="col"><h4>WebSocketTracker</h4><p>跟踪当前的 WebSocket 连接——某些实时双向通道（如 LLM 流的一种传输）要用到。</p></div>
</div>
<p>它们不是主角，但点出了一件事：server 不只是"收 HTTP 请求"，它还要管<strong>发现、实时连接</strong>这些"活"的东西。把这些都收进同一个 server，正是第 1 课"server 拥有一切"的具体体现。</p>
<p>把这两个零件和前面的 webHandler、路由组放一起看，server 的全貌就清楚了：它是一个<strong>常驻的、自描述的、可被多种方式连上的能力中枢</strong>。它不挑客户端——谁能说 HTTP、谁能连上来，就能调用它的全部本事。这种"<strong>一个中枢、广开门户</strong>"的姿态，正是 opencode 能长出 TUI、网页、桌面、Slack、ACP 这么多张脸的底层原因，也是下一课要深入的"路由组与 handler"所站立的地基。</p>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  opencode 的 server <strong>不是 Hono</strong>，而是架在 Effect <span class="mono">HttpApi</span> 上：你<strong>先用类型声明整套 API 的形状</strong>（每个端点的输入/输出/错误），编译器替你守契约，机器还能读懂它。对外它就是<strong>一个 <span class="mono">(request) =&gt; Response</span> 的 webHandler</strong>（所以能既走网络、又走进程内 RPC）；内部按领域切成 <strong>21 个路由组</strong>（session/event/config…）。最大的回报是 <span class="mono">OpenApi.fromApi</span>——<strong>API 自己描述自己</strong>，自动生成 SDK，让多个客户端的类型永远和 server 对齐。把这一课收进一句话：server 是 opencode <strong>自描述的能力中枢</strong>，所有客户端都顺着这份类型化的契约来和它对话——读懂了这扇门，就读懂了整个第三部分的入口。再往深一层，这个选择体现了 opencode 的一贯主张：宁可前期多花功夫把契约钉进类型，也不愿后期为"接口对不齐"反复买单。记住这条主线：客户端永远不直接碰 core，而是隔着这扇<strong>类型化的门</strong>说话；门后是 21 个分领域的房间，门本身则自动印出进门用的手册。把这扇门看清楚，第三部分后面几课（路由与 handler、事件流、SDK、多客户端传输）都只是在放大它的不同侧面。
</div>

<div class="card detail">
  <div class="tag">🔬 细节 / 源码对应</div>
  server 的骨架（简化自 <span class="inline">packages/opencode/src/server/server.ts</span>）：
<pre class="code"><span class="kw">import</span> { NodeHttpServer } <span class="kw">from</span> <span class="st">"@effect/platform-node"</span>
<span class="kw">import</span> { OpenApi } <span class="kw">from</span> <span class="st">"effect/unstable/httpapi"</span>   <span class="cm">// 注意：实验性 HttpApi，不是 Hono</span>
<span class="kw">import</span> { HttpApiApp } <span class="kw">from</span> <span class="st">"./routes/instance/httpapi/server"</span>

<span class="cm">// 对外：一个 (request) =&gt; Response 的 handler</span>
<span class="kw">const</span> handler = HttpApiApp.<span class="fn">webHandler</span>().handler
<span class="kw">const</span> server = { fetch: (req: Request) =&gt; <span class="fn">handler</span>(req, HttpApiApp.context) }

<span class="cm">// API 自描述：从定义生成 OpenAPI → 用于生成 SDK（第 12 课）</span>
<span class="kw">export const</span> openapi = () =&gt; OpenApi.<span class="fn">fromApi</span>(PublicApi)</pre>
  路由组都在 <span class="mono">routes/instance/httpapi/groups/</span> 下（session.ts、event.ts、config.ts… 共 21 个），handler 在 <span class="mono">handlers/</span>，请求进组前还会先过一层 <span class="mono">middleware/</span> 统一鉴权、压缩、处理错误。
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>server <strong>不是 Hono</strong>，而是 Effect 的 <span class="mono">HttpApi</span>：<strong>先用类型声明 API 形状</strong>，契约进类型。</li>
    <li>对外是<strong>一个 <span class="mono">(request) =&gt; Response</span> 的 webHandler</strong>——所以能既走网络、又走进程内 RPC（第 3、13 课）。</li>
    <li>按领域切成 <strong>21 个路由组</strong>（session/event/config/provider/mcp…），各自内聚。</li>
    <li><span class="mono">OpenApi.fromApi(PublicApi)</span> 让 <strong>API 自己描述自己</strong>，自动生成 SDK（第 12 课）。</li>
    <li>还带 MDNS（本地发现）与 WebSocketTracker（实时连接）。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Parts 1 and 2 laid the foundation: you know opencode's whole shape and the Effect beneath it. Now Part 3 — the <strong>client/server skeleton</strong>. This lesson looks at the <strong>server</strong> itself: how does it expose its abilities? The answer is a bit surprising — it's <strong>not Hono, not Express</strong>, but built on Effect's experimental <span class="mono">HttpApi</span>. This choice isn't a fad: it makes the whole API <strong>type-safe and self-describing</strong>, hence auto-generating an SDK. Grasp this lesson and you've caught the single entry point through which every client talks to the server.</p>
<p>Why start from the server, not the TUI you stare at daily? Because <strong>the server is the one that truly "owns everything"</strong> (Lesson 1's main line). The TUI and web are just its faces; to understand how opencode works you must first see clearly what door this brain opens to the outside. The next few lessons in this part — route groups and handlers, the event stream, SDK generation, multi-client transport — all magnify a different side of this door. See the door itself first and you won't miss the forest later.</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  Think of the server as a hotel's <strong>front desk</strong>. All guests (TUI, web, Slack…) come to this one desk for anything, and behind it hangs a <strong>categorized service menu</strong> — front-desk affairs, rooms, dining, cars… each category a "route group." Better still, this menu is <strong>written in a fixed format</strong>, so the hotel can <strong>auto-print a guidebook from it</strong> (the SDK) for every guest, where each service's name, the form to fill, the receipt you'll get, all match the back office <strong>to the letter</strong>. Change one back-office service and the guidebook updates — a guest never shows up with an outdated one. This hotel has another rule: the desk <strong>doesn't pick guests</strong> — front door, side door, or phone, speak per the guidebook and you get the same thing done. That's the picture of the server "open to all, one unified contract."
</div>

<h2>Not Hono, but Effect's HttpApi</h2>
<p>Many TS backends use Hono or Express: you write <span class="mono">app.get("/path", handler)</span> one by one, and the framework routes requests to functions. opencode's server takes a more "Effect" road — Effect's <span class="mono">HttpApi</span> from <span class="mono">effect/unstable/httpapi</span>. Its biggest difference from Hono: <strong>you don't write a path string then a handler; you first declare the whole API's "shape" in types</strong> — each endpoint's input, output, and possible failures, all written into the type.</p>
<p>Why? Because the last two lessons' lesson pays off again: <strong>lift the contract into the type and the compiler guards it for you</strong>. Wrong endpoint input/output errors at compile time; and — crucially — since the whole API's shape is a <strong>structured type</strong>, a machine can read it and thus <strong>auto-generate a client SDK</strong> (Lesson 12). Hono gives you flexibility; HttpApi gives you <strong>a machine-readable contract shared by front and back</strong>. For a project feeding TUI, web, desktop, Slack at once, the latter's value is overwhelming.</p>
<div class="cols">
  <div class="col"><h4>Hono / Express style</h4><p>Write path strings + handler functions; flexible, but the API's "shape" is scattered through code, machine-unreadable, each side guessing.</p></div>
  <div class="col"><h4>Effect HttpApi style</h4><p>Declare the whole API's shape in <strong>types</strong> first; the compiler guards the contract, a machine reads it, hence <strong>auto-generated SDK</strong>.</p></div>
</div>
<p>Behind this is a deep tradeoff: <strong>trade a little "declare the shape first" tedium for the whole system's reasonability</strong>. Hono lets you write a route in three seconds, but with dozens or hundreds of endpoints feeding five or six clients, "flexible" becomes "the source of mismatches everywhere." HttpApi forces you to write the contract clearly — seemingly more work, but it solves the most annoying "will the interface be wrong" problem once at compile time. This is Lesson 5's "turn implicit burdens into explicit types" worldview, scaled from one function to <strong>the whole API surface</strong>.</p>

<h2>One webHandler takes all requests</h2>
<p>The server outward is really <strong>one function</strong>: turn an incoming HTTP <span class="mono">Request</span> into a <span class="mono">Response</span>.</p>
<pre class="code"><span class="cm">// simplified from packages/opencode/src/server/server.ts</span>
<span class="kw">const</span> handler = HttpApiApp.<span class="fn">webHandler</span>().handler
<span class="kw">const</span> server = {
  fetch: (request: Request) =&gt; <span class="fn">handler</span>(request, HttpApiApp.context),
}</pre>
<p>This <span class="mono">webHandler</span> is the <strong>master handler</strong> obtained after assembling all route groups: a request comes in, it dispatches by path to the matching group and handler, runs it, then encodes the result into a <span class="mono">Response</span>. Note its form is a standard <span class="mono">(request) =&gt; Response</span> — precisely because it's so "standard," it can sit on a real network server (<span class="mono">NodeHttpServer</span>) and also be <strong>called directly inside a worker process</strong>. Remember the rich TUI's "zero-network RPC" from Lesson 3? Underneath it calls this same <span class="mono">fetch</span>-shaped handler. <strong>One handler, two transports</strong> — the root is right here.</p>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">Clients</span><span class="name">TUI / web / Slack…</span></div><div class="ld">send an HTTP Request (or in-process RPC)</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">Master handler</span><span class="name">webHandler</span></div><div class="ld">(request) =&gt; Response, dispatch by path</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">Route groups</span><span class="name">session / event / config… ×21</span></div><div class="ld">per-domain endpoint contracts</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">handler</span><span class="name">handlers/*</span></div><div class="ld">call core services, do the real work</div></div>
</div>
<p>The fact "the server outward is just a function" matters more than it sounds. Precisely because the handler's form is so standard and pure — in a Request, out a Response, no hard dependency on a "real network" — it can be freely <strong>grafted onto different transports</strong>: on Node's HTTP server it's a network service; dropped into a worker thread and called directly, it becomes the rich TUI's zero-network in-process communication. <strong>One business logic, hot-swappable transport</strong> — again Lesson 6's "wholesale-swappable impl" echoing at the server layer.</p>
<p>What's actually inside a handler? An endpoint's handler does "<strong>translate validated input into calls on core services, then encode the result back</strong>" — it's a <strong>thin layer of adaptation</strong> between this door and the core that does the real work behind it. Ideally a handler is thin: the heavy lifting is in core's Session, Tool services, and the handler only "ferries between the HTTP world and the Effect world." The next lesson takes route groups and handlers apart to see what this adaptation looks like.</p>

<h2>21 route groups: cut by domain</h2>
<p>This "service menu" isn't one long flat list of paths but <strong>cut into 21 groups by domain</strong>, each minding one area:</p>
<table class="t">
  <tr><th>Group</th><th>What it handles</th></tr>
  <tr><td><span class="mono">session</span></td><td>sessions: create, send a prompt, fetch history — the agent's main battlefield</td></tr>
  <tr><td><span class="mono">event</span></td><td>the event stream: push the server's internal events to clients (SSE)</td></tr>
  <tr><td><span class="mono">config</span> · <span class="mono">provider</span></td><td>config, model providers</td></tr>
  <tr><td><span class="mono">permission</span> · <span class="mono">question</span></td><td>permission confirmation, asking the user</td></tr>
  <tr><td><span class="mono">file</span> · <span class="mono">project</span> · <span class="mono">pty</span></td><td>files, projects, pseudo-terminal</td></tr>
  <tr><td><span class="mono">mcp</span> · <span class="mono">tui</span> · <span class="mono">workspace</span> …</td><td>MCP, TUI-specific, workspaces, etc. (21 groups total)</td></tr>
</table>
<p>"Cut into groups by domain" is an important engineering decision. It makes a huge API surface <strong>navigable</strong>: want the "send a prompt" endpoint? Go to <span class="mono">session</span>; want to subscribe to live events? Go to <span class="mono">event</span>. Each group is an <strong>independent, cohesive contract unit</strong>, readable, changeable, testable on its own. This shares Part 2's "small collaborators" temperament — <strong>a big system built from clearly-bounded small pieces</strong>.</p>
<div class="flow">
  <div class="node"><div class="nt">POST /session/…</div><div class="nd">request comes in</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">webHandler</div><div class="nd">dispatch by path</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">session group</div><div class="nd">match endpoint, validate input</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">handler</div><div class="nd">call core → encode Response</div></div>
</div>
<p>Incidentally, these 21 groups' names are themselves a <strong>map</strong> of opencode's abilities: <span class="mono">session</span> is the agent's battlefield, <span class="mono">event</span> powers real-time, <span class="mono">permission</span>/<span class="mono">question</span> manage "let the AI work but stay in control," <span class="mono">pty</span>/<span class="mono">file</span> let it actually touch your project, <span class="mono">mcp</span>/<span class="mono">workspace</span> lead to extensibility and multi-instance. You could almost reverse-engineer roughly what opencode can do from this group list. Several later lessons dive into these groups — their "doorplate" at the server layer hangs right here. In other words, reading the server's route groups is like reading a table of contents — before opening any chapter you roughly know what the book is about.</p>

<h2>Types as contract: the API describes itself</h2>
<p>HttpApi's most charming payoff is in this line:</p>
<pre class="code"><span class="cm">// simplified from server.ts — generate an OpenAPI spec from the API definition</span>
<span class="kw">return</span> OpenApi.<span class="fn">fromApi</span>(PublicApi)</pre>
<p>Because the whole API is declared structurally in types, <span class="mono">OpenApi.fromApi</span> can <strong>generate an OpenAPI spec directly from it</strong> — a machine-readable standard doc describing "what endpoints this server has, each taking/giving what." With it, you can <strong>auto-generate client SDKs in any language</strong> (Lesson 12). That's the opening metaphor cashed out: <strong>the back-office menu auto-printed into the guidebook handed to guests</strong>. Change the API in one place, the spec updates, the SDK regenerates, all clients' types sync instantly — no more "the front-end holds an outdated interface that doesn't line up."</p>
<div class="vflow">
  <div class="step"><b>① Declare API in types</b>　each endpoint's input/output/error in the type</div>
  <div class="step"><b>② OpenApi.fromApi</b>　auto-generate an OpenAPI spec from the definition</div>
  <div class="step"><b>③ Generate SDK</b>　type-safe client code per the spec, any language</div>
  <div class="step"><b>④ Clients sync</b>　change the API, spec updates, SDK regens, all types align</div>
</div>
<p>Pause to feel this chain's weight: it turns the "interface contract" from a human-maintained, easily-stale doc into <strong>a product that flows automatically from the code and never lies</strong>. The front-end no longer guesses what the back changed; the compiler tells you straight "this field is gone." For a project with as many mouths to feed as TUI, web, desktop, Slack, this "<strong>define once, sync everywhere</strong>" chain saves countless interface-mismatch squabbles. It's also the root reason opencode would rather use the still-"experimental"-labeled HttpApi than mature Hono — it bets on <strong>type-safe contracts</strong>, a bet with huge long-term returns.</p>
<p>Worth noting, a "self-describing API" has a hidden perk: it's naturally the <strong>freshest, most accurate doc</strong>. A newcomer wanting to know what the server can do needn't dig through scattered comments or a stale wiki — just look at the generated OpenAPI spec, or its generated SDK types, at a glance. Code as documentation, never lying — in a fast-evolving project, this value can't be overstated.</p>

<h2>Two more parts: MDNS and WebSocket</h2>
<p>On startup the server carries two small parts — get acquainted:</p>
<div class="cols">
  <div class="col"><h4>MDNS (local discovery)</h4><p><strong>Broadcasts its presence</strong> on the LAN so same-machine/same-network clients can auto-discover this server without typing an address.</p></div>
  <div class="col"><h4>WebSocketTracker</h4><p>Tracks current WebSocket connections — needed by some real-time bidirectional channels (e.g. one transport for LLM streams).</p></div>
</div>
<p>They aren't the stars, but they point out one thing: the server isn't just "take HTTP requests"; it also manages <strong>discovery and live connections</strong>, the "living" things. Folding these into the same server is the concrete embodiment of Lesson 1's "the server owns everything." Put these two with the earlier webHandler and route groups and the server's whole shape is clear: it's a <strong>resident, self-describing capability hub connectable many ways</strong>. It doesn't pick clients — whoever speaks HTTP and connects gets all its abilities. This "<strong>one hub, doors wide open</strong>" stance is the underlying reason opencode grows so many faces — TUI, web, desktop, Slack, ACP — and the ground the next lesson's "route groups and handlers" stands on.</p>

<div class="card macro">
  <div class="tag">🌍 Big picture</div>
  opencode's server is <strong>not Hono</strong> but built on Effect <span class="mono">HttpApi</span>: you <strong>declare the whole API's shape in types first</strong> (each endpoint's input/output/error), the compiler guards the contract, and a machine can read it. Outward it's <strong>one <span class="mono">(request) =&gt; Response</span> webHandler</strong> (so it runs over the network or in-process RPC); internally it's cut by domain into <strong>21 route groups</strong> (session/event/config…). The biggest payoff is <span class="mono">OpenApi.fromApi</span> — <strong>the API describes itself</strong>, auto-generating an SDK so many clients' types always align with the server. In one line: the server is opencode's self-describing capability hub; all clients talk to it along this typed contract — see this door clearly and the rest of Part 3 (routes, event stream, SDK, transport) just magnifies its sides.
</div>

<div class="card detail">
  <div class="tag">🔬 Source detail</div>
  The server's skeleton (simplified from <span class="inline">packages/opencode/src/server/server.ts</span>):
<pre class="code"><span class="kw">import</span> { NodeHttpServer } <span class="kw">from</span> <span class="st">"@effect/platform-node"</span>
<span class="kw">import</span> { OpenApi } <span class="kw">from</span> <span class="st">"effect/unstable/httpapi"</span>   <span class="cm">// note: experimental HttpApi, not Hono</span>
<span class="kw">import</span> { HttpApiApp } <span class="kw">from</span> <span class="st">"./routes/instance/httpapi/server"</span>

<span class="cm">// outward: one (request) =&gt; Response handler</span>
<span class="kw">const</span> handler = HttpApiApp.<span class="fn">webHandler</span>().handler
<span class="kw">const</span> server = { fetch: (req: Request) =&gt; <span class="fn">handler</span>(req, HttpApiApp.context) }

<span class="cm">// API self-describes: generate OpenAPI from the definition → used to generate the SDK (Lesson 12)</span>
<span class="kw">export const</span> openapi = () =&gt; OpenApi.<span class="fn">fromApi</span>(PublicApi)</pre>
  Route groups live under <span class="mono">routes/instance/httpapi/groups/</span> (session.ts, event.ts, config.ts… 21 total), handlers under <span class="mono">handlers/</span>, with a <span class="mono">middleware/</span> layer doing auth, compression, and error handling before a request reaches its group.
</div>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>The server is <strong>not Hono</strong> but Effect's <span class="mono">HttpApi</span>: <strong>declare the API shape in types</strong>, contract in the type.</li>
    <li>Outward it's <strong>one <span class="mono">(request) =&gt; Response</span> webHandler</strong> — so it runs over network or in-process RPC (Lessons 3, 13).</li>
    <li>Cut by domain into <strong>21 route groups</strong> (session/event/config/provider/mcp…), each cohesive.</li>
    <li><span class="mono">OpenApi.fromApi(PublicApi)</span> makes <strong>the API describe itself</strong>, auto-generating the SDK (Lesson 12).</li>
    <li>It also carries MDNS (local discovery) and WebSocketTracker (live connections).</li>
  </ul>
</div>
""",
}
LESSON_10 = {
    "zh": r"""
<p class="lead">上一课我们站在门口，看清了 server 这扇门的整体长相：一个 <span class="mono">webHandler</span>、背后挂着 <strong>21 个路由组</strong>。这一课我们<strong>推门进去</strong>，把镜头怼到<strong>其中一个组</strong>身上，看它到底由什么拼成。你会发现 opencode 的每个 API 端点都分成两半：<strong>「组」负责声明契约</strong>（这个端点叫什么、要什么、给什么、可能怎么错），<strong>「handler」负责照约办事</strong>（把校验过的输入翻译成对 core 的调用）。再加上裹在外面的一圈<strong>中间件</strong>，三者合起来，才是一个请求从进门到出门的完整旅程。读懂这一课，你就能拿着任何一个 API 路径，自己摸到它的声明在哪、实现在哪。</p>
<p>为什么要把「声明」和「实现」拆成两半？这其实是第 5、6 课那套世界观的又一次兑现：<strong>把契约抬到显眼、机器可读的地方，把杂活留在实现里</strong>。组里全是类型，没有一行业务逻辑——正因为它「纯」，机器才能读它、据它生成 SDK（第 12 课）。handler 里全是干活的调用，但它<strong>不必再操心校验</strong>——输入合不合法，组的类型在它跑之前就替它把过关了。两边各司其职，这就是 opencode 路由层的基本骨法。</p>

<div class="card analogy">
  <div class="tag">🏨 生活类比</div>
  还记得上一课那家酒店吗？这一课我们走近<strong>服务清单上的某一栏</strong>。每一栏（一个「组」）写明这一类的每项服务：<strong>叫什么名字</strong>（list / get / create）、<strong>要你填哪张表</strong>（params / query / payload）、<strong>会给你什么回执</strong>（success）、<strong>可能怎么被拒</strong>（error）。但清单只是「写明」，真正<strong>照单办事的是柜台后的柜员</strong>（handler）——他拿到你填好的表，转身去后厨/库房（core 服务）取货，再把结果递回给你。而你递表之前，还得先过门口那<strong>一排关卡</strong>（中间件）：安检（鉴权）、翻译（实例路由）、出错时兜底的值班经理（错误中间件）。<strong>清单写契约、柜员干活、关卡把关</strong>——这三层就是这一课的全部。
</div>

<h2>路由组：每个端点都是一份契约</h2>
<p>打开 <span class="mono">groups/session.ts</span>，你看不到任何「怎么查数据库」的代码，只看到<strong>一连串端点声明</strong>。每个端点用 <span class="mono">HttpApiEndpoint.get/post(名字, 路径, {…})</span> 写成，大括号里把这个端点的<strong>五个侧面</strong>钉死：路径参数、查询参数、请求体、成功返回、可能的错误。它<strong>只描述形状，不含实现</strong>——这正是「声明式」的精髓。</p>
<div class="cellgroup">
  <div class="cell"><div class="k">name</div><div class="v">"get" —— 端点的标识名，handler 靠它对号入座</div></div>
  <div class="cell"><div class="k">params</div><div class="v">{ sessionID } —— 路径里的占位，带类型</div></div>
  <div class="cell"><div class="k">query</div><div class="v">WorkspaceRoutingQuery —— ?后面的查询参数</div></div>
  <div class="cell"><div class="k">success</div><div class="v">Session.Info —— 成功时返回的形状</div></div>
  <div class="cell"><div class="k">error</div><div class="v">[BadRequest, ApiNotFoundError] —— 声明在案的失败</div></div>
</div>
<p>注意最后那个 <span class="mono">error</span>：失败也是契约的一部分。一个端点<strong>可能怎么错</strong>，被明明白白写进类型，而不是藏在某个 <span class="mono">throw</span> 里靠运气发现。这就是第 8 课「错误是值、写进签名」那条原则，在 API 表面上的体现——客户端拿到 SDK 时，连「这个调用可能返回 404」都是类型已知的。每个端点还跟着一段 <span class="mono">.annotateMerge(OpenApi.annotations({…}))</span>，补上人类可读的 summary/description，这些文字最后会原样流进自动生成的 OpenAPI 文档与 SDK 注释里。</p>
<p>把这些端点用 <span class="mono">.add(...)</span> 串起来，就组成一个 <span class="mono">HttpApiGroup</span>；再把一个个组 <span class="mono">.add(...)</span> 进 <span class="mono">HttpApi.make(...)</span>，就拼出了整张 API。<strong>端点 → 组 → API</strong>，层层 <span class="mono">.add</span> 累加，整个过程没有一行「运行时逻辑」，纯是在用类型搭一座契约的脚手架。</p>
<p>这里有个容易被忽略却很关键的好处：因为「声明」先于「实现」，<strong>SDK 可以在任何 handler 写好之前就生成出来</strong>。换句话说，前端团队不必等后端把活干完，只要契约定了，类型化的客户端就有了——大家照着同一份契约并行开工。对一个要同时喂养 TUI、网页、桌面、Slack 的项目，这种「契约先行、各端解耦」的协作方式，几乎是把多端一致性从「靠纪律维持」升级成了「靠类型保证」。这正是声明式那点前期啰嗦真正买到的东西。</p>
<div class="flow">
  <div class="node">HttpApiEndpoint<span class="sub">单个端点·五个侧面</span></div>
  <div class="arrow">.add →</div>
  <div class="node">HttpApiGroup<span class="sub">一个领域·如 session</span></div>
  <div class="arrow">.add →</div>
  <div class="node">HttpApi<span class="sub">整张 API·21 组汇总</span></div>
</div>

<h2>21 个组，就是一张能力地图</h2>
<p>这 21 个组的<strong>名字本身</strong>，几乎就是 opencode 全部对外能力的目录。你不用读实现，光看组名就能猜个八九不离十：</p>
<div class="cellgroup">
  <div class="cell"><div class="k">session</div><div class="v">会话：列表/创建/发消息/中止/分享</div></div>
  <div class="cell"><div class="k">event</div><div class="v">事件流：SSE 实时推送（第 11 课）</div></div>
  <div class="cell"><div class="k">config</div><div class="v">配置读写</div></div>
  <div class="cell"><div class="k">file</div><div class="v">文件读写、搜索</div></div>
  <div class="cell"><div class="k">permission</div><div class="v">工具权限的批准/拒绝</div></div>
  <div class="cell"><div class="k">provider</div><div class="v">模型供应商与可用模型</div></div>
  <div class="cell"><div class="k">mcp</div><div class="v">MCP 外部工具服务器</div></div>
  <div class="cell"><div class="k">tui</div><div class="v">给富 TUI 的专用端点</div></div>
</div>
<p>（上面只列了 8 个，其余还有 instance、workspace、project、question、pty、sync、control、global 等，凑满 21 个。）这件事很值得停下来体会：<strong>当 API 是结构化声明时，它的「目录」是天然存在、可枚举的</strong>。你想知道 opencode 能干什么？不用读文档、不用问人，把 <span class="mono">groups/</span> 目录 <span class="mono">ls</span> 一遍，能力清单就在眼前。这是 Hono 那种「路由散落各处」的写法给不了的——在那里，没有人能一眼说清「这个服务总共开了哪些口」。声明式的代价是前期啰嗦，红利是<strong>系统永远能自己回答「我有哪些能力」</strong>。这种「可枚举性」还会一路传导：能力可枚举，文档就能自动生成、SDK 就能自动产出，连测试都能照着清单逐个覆盖——一份结构化的契约，喂饱了下游一整条工具链。</p>
<div class="cols">
  <div class="col"><h4>组 = 契约（声明）</h4><p>groups/*.ts，21 个文件，全是类型。回答「有什么端点、各要什么」。机器可读 → 生成 SDK。</p></div>
  <div class="col"><h4>handler = 实现（干活）</h4><p>handlers/*.ts，20 个文件。回答「这个端点具体怎么办」。调用 core 服务，把活真正干掉。</p></div>
</div>

<h2>handler：把契约接到 core</h2>
<p>契约写好了，谁来兑现？这就是 <span class="mono">handlers/session.ts</span> 的活。它用 <span class="mono">HttpApiBuilder.group(InstanceHttpApi, "session", handlers =&gt; …)</span> 认领「session 这个组」，然后<strong>给组里每个端点名字配上一个实现函数</strong>——<span class="mono">.handle("list", list).handle("get", get)…</span>。名字必须和组里声明的对上，少一个、拼错一个，编译器立刻报错。这就是「契约」二字的分量：<strong>声明和实现被类型死死焊在一起</strong>。</p>
<pre class="code"><span class="cm">// 简化自 handlers/session.ts</span>
<span class="kw">export const</span> sessionHandlers = HttpApiBuilder.<span class="fn">group</span>(InstanceHttpApi, <span class="st">"session"</span>, (handlers) =&gt;
  Effect.<span class="fn">gen</span>(<span class="kw">function</span>* () {
    <span class="kw">const</span> session = <span class="kw">yield</span>* Session
    <span class="kw">return</span> handlers
      .<span class="fn">handle</span>(<span class="st">"list"</span>, list)
      .<span class="fn">handle</span>(<span class="st">"get"</span>, get)
      .<span class="fn">handleRaw</span>(<span class="st">"create"</span>, createRaw)
  }))</pre>
<p>留意一个细节：handler 函数<strong>不用再校验输入</strong>。当 <span class="mono">list</span> 跑起来时，它拿到的 <span class="mono">ctx.params</span>、<span class="mono">ctx.query</span> 都<strong>已经被组里的类型解码、校验过了</strong>——非法请求在到达 handler 之前就被挡下并返回了。所以理想的 handler 应该<strong>很薄</strong>：取出已经干净的输入 → 调一个 core 服务（<span class="mono">yield* session.list(...)</span>）→ 把结果返回。重活全在 core 的 Session/Tool 服务里，handler 只是 <strong>HTTP 世界和 Effect 世界之间一层薄薄的转接</strong>。</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">请求进来：GET /session/abc123</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">组的类型解码 params/query —— 非法即挡，返回声明过的错误</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">派发到 handler 的 get：拿到干净的 ctx.params.sessionID</span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">yield* session.get(sessionID) —— 调 core 服务干真正的活</span></div>
  <div class="t-row"><span class="t-num">5</span><span class="t-txt">返回 Session.Info —— 框架按 success 契约编码成 Response</span></div>
</div>
<p>偶尔你会看到 <span class="mono">.handleRaw(...)</span> 而不是 <span class="mono">.handle(...)</span>，比如上面的 <span class="mono">create</span>。区别在于：<span class="mono">handle</span> 让框架替你把返回值按 success 契约自动编码成 <span class="mono">Response</span>；而 <span class="mono">handleRaw</span> 把 <span class="mono">Response</span> 的控制权交还给你，用于需要手搓响应头、流式输出、自定义状态码的少数场景。<strong>常规走 handle，特殊才 raw</strong>——这是一条很实用的阅读线索：看到 raw，就知道这个端点有点「不走寻常路」。</p>
<p>「handler 要薄」不只是审美洁癖，它是一条能帮你<strong>嗅出坏味道</strong>的诊断线。如果某个 handler 越长越胖、开始出现成段的业务判断、循环、对数据的拼装，那几乎可以断定：<strong>有本该住在 core 里的逻辑，漏到 HTTP 这一层了</strong>。后果很现实——这段逻辑只有走 HTTP 才能触发，第 13 课那条进程内 RPC、或者将来任何别的入口，都享受不到它。所以「薄」是有意为之的架构纪律：让业务逻辑沉到 core，HTTP 层只做翻译，core 才能被多种传输共享。读 handler 时，不妨拿「它够不够薄」当尺子，量一量这个端点的健康度。</p>

<h2>中间件：handler 跑之前和之后</h2>
<p>请求到达 handler 之前、离开之后，还要穿过一圈<strong>中间件</strong>（<span class="mono">middleware/</span> 下 9 个文件）。它们是横切关注点——鉴权、压缩、CORS、实例路由、错误兜底——<strong>每个端点都要</strong>，但你不想在每个 handler 里重写一遍，于是抽成一圈「关卡」，套在 handler 外面。</p>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">外</span><span class="name">authorization</span></div><div class="ld">鉴权：你有没有资格调这个口</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">↓</span><span class="name">workspace-routing / instance-context</span></div><div class="ld">实例路由：这个请求归哪个工作区/实例处理</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">核</span><span class="name">handler</span></div><div class="ld">真正干活的那一层（上一节）</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">↑</span><span class="name">error / compression / cors-vary</span></div><div class="ld">回程：兜底错误、压缩响应、补 CORS 头</div></div>
</div>
<p>其中<strong>错误中间件</strong>（<span class="mono">middleware/error.ts</span>）的设计很能体现 opencode 的克制。它<strong>不</strong>粗暴地把所有异常都拦下来变成 500——恰恰相反，它特意放行那些<strong>已经声明在契约里的、有类型的失败</strong>（比如 404、BadRequest），让它们沿着自己声明过的错误路径正常返回。它只管一件事：<strong>兜住那些没人预料到的「裸崩溃」（defect）</strong>，把它们包成一个带 <span class="mono">ref</span> 编号的 500，并把真实堆栈写进服务器日志。</p>
<pre class="code"><span class="cm">// 简化自 middleware/error.ts —— 只兜底「意料之外」的崩溃</span>
<span class="kw">const</span> ref = <span class="st">`err_${'$'}{crypto.randomUUID().slice(0, 8)}`</span>
<span class="kw">yield</span>* Effect.<span class="fn">logError</span>(<span class="st">"failed"</span>, { ref, error })  <span class="cm">// 真相进日志</span>
<span class="kw">return</span> HttpServerResponse.<span class="fn">jsonUnsafe</span>(
  { message: <span class="st">"Unexpected server error. Check server logs."</span>, ref },
  { status: 500 })  <span class="cm">// 客户端只拿到一个编号</span></pre>
<p>这个设计的妙处在于<strong>「真相进日志、编号给客户端」</strong>：用户/客户端只看到一句「服务器开小差了，编号 err_3f9a1c0b」，不会泄露内部堆栈；而运维拿着这个 ref 去日志里一搜，完整的错误因果链就在眼前。<strong>对外克制、对内详尽</strong>——安全和可调试性两头都顾到了。这也再次呼应第 8 课：有类型的错误走正路，没类型的崩溃才需要这道最后防线。</p>
<p>还有一点值得专门点出：中间件的<strong>顺序不是随意的</strong>。鉴权必须排在最外层——还没确认你有没有资格，就不该让请求往里走半步；错误兜底则要能<strong>包住它里面的一切</strong>，否则内层任何一处裸崩溃都会漏出去变成一个空白的 500。所以这一圈关卡更像<strong>洋葱</strong>而非流水线：请求一层层往里穿到 handler，响应再一层层往外穿回来，进去和出来经过的是同一批关卡、只是方向相反。理解了这个「洋葱」结构，你就能解释很多看似奇怪的现象——比如为什么压缩、补 CORS 头这类「修饰响应」的活，总是发生在 handler 跑完<strong>之后</strong>的回程上。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <p>把这一课拼回上一课：上一课的 <span class="mono">webHandler</span> 是「总台」，这一课拆开了总台背后的<strong>三件套</strong>——</p>
  <ul>
    <li><strong>组（21 个，groups/）</strong>：声明契约，纯类型，喂养 SDK 生成。</li>
    <li><strong>handler（20 个，handlers/）</strong>：薄薄一层，把校验过的输入接到 core 服务。</li>
    <li><strong>中间件（9 个，middleware/）</strong>：套在外圈的横切关卡，鉴权/路由/压缩/错误兜底。</li>
  </ul>
  <p>一个请求的完整旅程：<strong>进门 → 穿过中间件外圈 → 组按类型解码校验 → 派发到对应 handler → handler 调 core 干活 → 结果按 success 契约编码 → 穿回中间件 → 出门</strong>。下一课我们专挑 <span class="mono">event</span> 这个特殊的组：它不返回一次性结果，而是开一条<strong>持续推送</strong>的 SSE 长连接。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p>声明（组）与实现（handler）如何靠端点名对齐，一图看尽：</p>
  <pre class="code"><span class="cm">// groups/session.ts —— 端点即契约（只声明形状）</span>
HttpApiEndpoint.<span class="fn">get</span>(<span class="st">"get"</span>, SessionPaths.get, {
  params: { sessionID: SessionID },
  success: <span class="fn">described</span>(Session.Info, <span class="st">"Get session"</span>),
  error: [HttpApiError.BadRequest, ApiNotFoundError],
})

<span class="cm">// handlers/session.ts —— 同名实现，编译器强制对齐</span>
handlers.<span class="fn">handle</span>(<span class="st">"get"</span>, get)
<span class="cm">// "get" 拼错或漏写 → 编译期报错。声明与实现被类型焊死。</span></pre>
  <p>这正是「契约」二字落到代码上的样子：<span class="mono">groups/</span> 说「应该有什么」，<span class="mono">handlers/</span> 说「具体怎么做」，而 TypeScript 站在中间，确保两边<strong>一个名字都不许对不上</strong>。下次你想搞清某个 API 路径的来龙去脉，路线图就很清晰了：先去 <span class="mono">groups/</span> 找它的契约（要什么、给什么、会怎么错），再去同名的 <span class="mono">handlers/</span> 看它怎么把活接到 core——两站之间，类型替你保证了它们说的是同一件事。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li>opencode 的每个 API 端点分两半：<strong>组声明契约</strong>（名字/参数/返回/错误，纯类型），<strong>handler 实现</strong>（调 core 干活）。</li>
    <li>端点的<strong>错误也是契约</strong>：可能返回什么错，写进类型，客户端的 SDK 据此都是类型已知的。</li>
    <li><strong>21 个组的名字就是 opencode 的能力地图</strong>——结构化声明让系统永远能自己回答「我有哪些能力」。</li>
    <li>handler 应当<strong>很薄</strong>：输入已被组的类型校验，它只负责「取干净输入 → 调 core → 返回」。<span class="mono">handleRaw</span> 用于需要手控 Response 的少数端点。</li>
    <li><strong>中间件</strong>是套在外圈的横切关卡；错误中间件「真相进日志、编号给客户端」，有类型的失败照常走正路。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Last lesson we stood at the door and saw the server's overall shape: one <span class="mono">webHandler</span>, with <strong>21 route groups</strong> behind it. This lesson we <strong>push the door open</strong> and zoom in on <strong>one group</strong> to see what it's made of. You'll find every opencode API endpoint splits in two: <strong>the "group" declares the contract</strong> (what this endpoint is called, what it wants, what it gives back, how it might fail), and <strong>the "handler" fulfils it</strong> (translating validated input into a call on core). Wrap a ring of <strong>middleware</strong> around them, and the three together make a request's full journey in and out. Grasp this lesson and you can take any API path and find, on your own, where it's declared and where it's implemented.</p>
<p>Why split "declaration" from "implementation"? It's Lessons 5 and 6's worldview cashing out again: <strong>lift the contract to a visible, machine-readable place, and leave the chores in the implementation</strong>. The group is all types, not one line of business logic — because it's "pure," a machine can read it and generate the SDK from it (Lesson 12). The handler is all real calls, but it <strong>needn't worry about validation</strong> — whether input is legal, the group's types settle before the handler ever runs. Each side to its own job — that's the basic skeleton of opencode's routing layer.</p>

<div class="card analogy">
  <div class="tag">🏨 Analogy</div>
  Remember last lesson's hotel? This time we walk up to <strong>one column on the service menu</strong>. Each column (a "group") spells out every service in that category: <strong>what it's called</strong> (list / get / create), <strong>which form you fill</strong> (params / query / payload), <strong>what receipt you'll get</strong> (success), <strong>how you might be refused</strong> (error). But the menu only "states" things — the one who <strong>actually does the work is the clerk behind the counter</strong> (handler), who takes your filled form, turns to the kitchen/storeroom (core services) to fetch goods, then hands the result back. And before you submit your form, you pass <strong>a row of checkpoints</strong> at the door (middleware): security (auth), translation (instance routing), the duty manager who catches falls (error middleware). <strong>The menu writes the contract, the clerk does the work, the checkpoints guard</strong> — these three layers are this whole lesson.
</div>

<h2>Route groups: every endpoint is a contract</h2>
<p>Open <span class="mono">groups/session.ts</span> and you see no "how to query the database" code at all, only <strong>a chain of endpoint declarations</strong>. Each endpoint is written as <span class="mono">HttpApiEndpoint.get/post(name, path, {…})</span>, and inside the braces it nails down the endpoint's <strong>five facets</strong>: path params, query params, request body, success return, possible errors. It <strong>only describes shape, contains no implementation</strong> — that's the essence of "declarative."</p>
<div class="cellgroup">
  <div class="cell"><div class="k">name</div><div class="v">"get" — the endpoint's identifier; the handler matches by it</div></div>
  <div class="cell"><div class="k">params</div><div class="v">{ sessionID } — typed placeholders in the path</div></div>
  <div class="cell"><div class="k">query</div><div class="v">WorkspaceRoutingQuery — the params after ?</div></div>
  <div class="cell"><div class="k">success</div><div class="v">Session.Info — the shape returned on success</div></div>
  <div class="cell"><div class="k">error</div><div class="v">[BadRequest, ApiNotFoundError] — declared failures</div></div>
</div>
<p>Notice that last <span class="mono">error</span>: failure is part of the contract too. <strong>How an endpoint might fail</strong> is written plainly into the type, not hidden in some <span class="mono">throw</span> you discover by luck. That's Lesson 8's "errors are values, written into the signature" showing up at the API surface — when a client gets the SDK, even "this call may return 404" is type-known. Each endpoint also trails a <span class="mono">.annotateMerge(OpenApi.annotations({…}))</span> adding human-readable summary/description, and that text flows verbatim into the auto-generated OpenAPI doc and SDK comments.</p>
<p>String these endpoints together with <span class="mono">.add(...)</span> and you get an <span class="mono">HttpApiGroup</span>; <span class="mono">.add(...)</span> group after group into <span class="mono">HttpApi.make(...)</span> and you've assembled the whole API. <strong>Endpoint → group → API</strong>, layer on layer of <span class="mono">.add</span>, with not one line of "runtime logic" in the whole process — purely scaffolding a contract out of types.</p>
<p>Here's an easily-missed but crucial payoff: because "declaration" precedes "implementation," <strong>the SDK can be generated before any handler is written</strong>. In other words, the frontend team needn't wait for the backend to finish the work — once the contract is set, the typed client exists, and everyone builds in parallel against the same contract. For a project feeding TUI, web, desktop and Slack at once, this "contract-first, ends decoupled" way of collaborating essentially upgrades multi-client consistency from "kept by discipline" to "guaranteed by types." That's what the declarative style's bit of up-front verbosity really buys.</p>
<div class="flow">
  <div class="node">HttpApiEndpoint<span class="sub">one endpoint · five facets</span></div>
  <div class="arrow">.add →</div>
  <div class="node">HttpApiGroup<span class="sub">one domain · e.g. session</span></div>
  <div class="arrow">.add →</div>
  <div class="node">HttpApi<span class="sub">whole API · 21 groups merged</span></div>
</div>

<h2>21 groups are a map of capabilities</h2>
<p>The <strong>names themselves</strong> of these 21 groups are almost a complete table of contents for everything opencode exposes. You needn't read the implementation; the group names alone tell you most of it:</p>
<div class="cellgroup">
  <div class="cell"><div class="k">session</div><div class="v">sessions: list/create/prompt/abort/share</div></div>
  <div class="cell"><div class="k">event</div><div class="v">event stream: real-time SSE push (Lesson 11)</div></div>
  <div class="cell"><div class="k">config</div><div class="v">read/write configuration</div></div>
  <div class="cell"><div class="k">file</div><div class="v">file read/write, search</div></div>
  <div class="cell"><div class="k">permission</div><div class="v">approve/deny tool permissions</div></div>
  <div class="cell"><div class="k">provider</div><div class="v">model providers and available models</div></div>
  <div class="cell"><div class="k">mcp</div><div class="v">MCP external tool servers</div></div>
  <div class="cell"><div class="k">tui</div><div class="v">endpoints dedicated to the rich TUI</div></div>
</div>
<p>(That lists only 8; the rest include instance, workspace, project, question, pty, sync, control, global and more, making 21.) This is worth pausing on: <strong>when the API is a structured declaration, its "directory" naturally exists and is enumerable</strong>. Want to know what opencode can do? No docs to read, no one to ask — <span class="mono">ls</span> the <span class="mono">groups/</span> directory and the capability list is right there. The Hono style of "routes scattered everywhere" can't give you this — there, no one can say at a glance "what ports does this service open in total." The declarative cost is up-front verbosity; the dividend is that <strong>the system can always answer "what capabilities do I have"</strong> by itself. This "enumerability" propagates downstream too: capabilities enumerable, docs auto-generate, SDKs auto-emit, even tests can cover the list one by one — one structured contract feeds a whole downstream toolchain.</p>
<div class="cols">
  <div class="col"><h4>group = contract (declaration)</h4><p>groups/*.ts, 21 files, all types. Answers "what endpoints exist, what each wants." Machine-readable → generates SDK.</p></div>
  <div class="col"><h4>handler = implementation (the work)</h4><p>handlers/*.ts, 20 files. Answers "how this endpoint actually does it." Calls core services, gets the work done.</p></div>
</div>

<h2>Handlers: wiring the contract to core</h2>
<p>The contract's written — who honours it? That's <span class="mono">handlers/session.ts</span>'s job. It uses <span class="mono">HttpApiBuilder.group(InstanceHttpApi, "session", handlers =&gt; …)</span> to claim "the session group," then <strong>pairs each endpoint name in the group with an implementation function</strong> — <span class="mono">.handle("list", list).handle("get", get)…</span>. The name must match what the group declared; miss one or misspell one and the compiler complains at once. That's the weight of the word "contract": <strong>declaration and implementation are welded together by types</strong>.</p>
<pre class="code"><span class="cm">// simplified from handlers/session.ts</span>
<span class="kw">export const</span> sessionHandlers = HttpApiBuilder.<span class="fn">group</span>(InstanceHttpApi, <span class="st">"session"</span>, (handlers) =&gt;
  Effect.<span class="fn">gen</span>(<span class="kw">function</span>* () {
    <span class="kw">const</span> session = <span class="kw">yield</span>* Session
    <span class="kw">return</span> handlers
      .<span class="fn">handle</span>(<span class="st">"list"</span>, list)
      .<span class="fn">handle</span>(<span class="st">"get"</span>, get)
      .<span class="fn">handleRaw</span>(<span class="st">"create"</span>, createRaw)
  }))</pre>
<p>Note one detail: the handler function <strong>needn't validate input again</strong>. When <span class="mono">list</span> runs, the <span class="mono">ctx.params</span> and <span class="mono">ctx.query</span> it receives have <strong>already been decoded and validated by the group's types</strong> — illegal requests were rejected and returned before reaching the handler. So an ideal handler is <strong>thin</strong>: take the already-clean input → call one core service (<span class="mono">yield* session.list(...)</span>) → return the result. The heavy work all lives in core's Session/Tool services; the handler is just a <strong>thin layer of adaptation between the HTTP world and the Effect world</strong>.</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">request arrives: GET /session/abc123</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">group's types decode params/query — illegal = rejected, returns a declared error</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">dispatched to handler's get: receives clean ctx.params.sessionID</span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">yield* session.get(sessionID) — call core service for the real work</span></div>
  <div class="t-row"><span class="t-num">5</span><span class="t-txt">return Session.Info — framework encodes it to a Response per the success contract</span></div>
</div>
<p>Occasionally you'll see <span class="mono">.handleRaw(...)</span> instead of <span class="mono">.handle(...)</span>, like <span class="mono">create</span> above. The difference: <span class="mono">handle</span> lets the framework auto-encode your return value into a <span class="mono">Response</span> per the success contract; <span class="mono">handleRaw</span> hands <span class="mono">Response</span> control back to you, for the few cases needing hand-rolled headers, streaming output, or custom status codes. <strong>Regular goes handle, special goes raw</strong> — a handy reading cue: see raw, and you know this endpoint goes a little "off the beaten path."</p>
<p>"Handlers should be thin" isn't just aesthetic fussiness; it's a diagnostic line that helps you <strong>smell rot</strong>. If a handler grows long and fat, sprouting paragraphs of business decisions, loops, data assembly, you can almost conclude: <strong>logic that should live in core has leaked into the HTTP layer</strong>. The consequence is real — that logic fires only over HTTP; Lesson 13's in-process RPC, or any other future entry, gets none of it. So "thin" is deliberate architectural discipline: let business logic sink into core, the HTTP layer only translate, so core can be shared by many transports. When reading a handler, use "is it thin enough" as a ruler to gauge that endpoint's health.</p>

<h2>Middleware: before and after the handler runs</h2>
<p>Before reaching the handler, and after leaving it, a request passes a ring of <strong>middleware</strong> (9 files under <span class="mono">middleware/</span>). They're cross-cutting concerns — auth, compression, CORS, instance routing, error catch-all — that <strong>every endpoint needs</strong> but you don't want to rewrite in each handler, so they're factored into a ring of "checkpoints" wrapped around the handler.</p>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">out</span><span class="name">authorization</span></div><div class="ld">auth: are you entitled to call this port</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">↓</span><span class="name">workspace-routing / instance-context</span></div><div class="ld">instance routing: which workspace/instance handles this</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">core</span><span class="name">handler</span></div><div class="ld">the layer that does the real work (last section)</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">↑</span><span class="name">error / compression / cors-vary</span></div><div class="ld">return trip: catch errors, compress response, add CORS headers</div></div>
</div>
<p>The <strong>error middleware</strong> (<span class="mono">middleware/error.ts</span>) especially shows opencode's restraint. It does <strong>not</strong> crudely catch every exception and turn it into a 500 — quite the opposite, it deliberately lets through those <strong>typed failures already declared in the contract</strong> (like 404, BadRequest), letting them return normally along their own declared error path. It minds only one thing: <strong>catching the unforeseen "bare crashes" (defects)</strong>, wrapping them into a 500 with a <span class="mono">ref</span> id, and writing the real stack into the server log.</p>
<pre class="code"><span class="cm">// simplified from middleware/error.ts — only catches "unforeseen" crashes</span>
<span class="kw">const</span> ref = <span class="st">`err_${'$'}{crypto.randomUUID().slice(0, 8)}`</span>
<span class="kw">yield</span>* Effect.<span class="fn">logError</span>(<span class="st">"failed"</span>, { ref, error })  <span class="cm">// truth into the log</span>
<span class="kw">return</span> HttpServerResponse.<span class="fn">jsonUnsafe</span>(
  { message: <span class="st">"Unexpected server error. Check server logs."</span>, ref },
  { status: 500 })  <span class="cm">// client gets only an id</span></pre>
<p>The beauty is <strong>"truth into the log, an id to the client"</strong>: the user/client sees only "the server hiccuped, id err_3f9a1c0b," with no internal stack leaked; while ops greps the log for that ref and the full causal chain of the error is right there. <strong>Restrained outward, detailed inward</strong> — both security and debuggability are served. It echoes Lesson 8 again: typed errors take the main road; only untyped crashes need this last line of defense.</p>
<p>One more thing worth calling out: middleware <strong>order is not arbitrary</strong>. Auth must be outermost — before confirming you're entitled, the request shouldn't step half a pace inward; the error catch-all must be able to <strong>wrap everything inside it</strong>, or any bare crash deeper in leaks out as a blank 500. So this ring of checkpoints is more an <strong>onion</strong> than a pipeline: the request threads inward layer by layer to the handler, the response threads back out layer by layer, going in and coming out through the same checkpoints in opposite directions. Grasp this "onion" structure and you can explain many seemingly odd things — like why "response-decorating" work such as compression and adding CORS headers always happens on the return trip, <strong>after</strong> the handler runs.</p>

<div class="card macro">
  <div class="tag">🗺️ The big picture</div>
  <p>Stitch this lesson back to the last: last lesson's <span class="mono">webHandler</span> is the "front desk," and this lesson opened the <strong>three-piece set</strong> behind it —</p>
  <ul>
    <li><strong>groups (21, groups/)</strong>: declare contracts, pure types, feed SDK generation.</li>
    <li><strong>handlers (20, handlers/)</strong>: a thin layer wiring validated input to core services.</li>
    <li><strong>middleware (9, middleware/)</strong>: the cross-cutting checkpoints in the outer ring — auth/routing/compression/error catch-all.</li>
  </ul>
  <p>A request's full journey: <strong>in the door → through the middleware outer ring → group decodes and validates by type → dispatch to the matching handler → handler calls core for the work → result encoded per the success contract → back out through middleware → out the door</strong>. Next lesson we pick the special <span class="mono">event</span> group: it returns not a one-shot result but opens a continuously-pushing SSE long connection.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source detail</div>
  <p>How declaration (group) and implementation (handler) align by endpoint name, in one view:</p>
  <pre class="code"><span class="cm">// groups/session.ts — endpoint as contract (declares shape only)</span>
HttpApiEndpoint.<span class="fn">get</span>(<span class="st">"get"</span>, SessionPaths.get, {
  params: { sessionID: SessionID },
  success: <span class="fn">described</span>(Session.Info, <span class="st">"Get session"</span>),
  error: [HttpApiError.BadRequest, ApiNotFoundError],
})

<span class="cm">// handlers/session.ts — same-name implementation, alignment enforced</span>
handlers.<span class="fn">handle</span>(<span class="st">"get"</span>, get)
<span class="cm">// misspell or omit "get" → compile error. Declaration and impl welded by types.</span></pre>
  <p>This is what "contract" looks like landed in code: <span class="mono">groups/</span> says "what should exist," <span class="mono">handlers/</span> says "how to do it," and TypeScript stands in the middle ensuring the two sides <strong>can't mismatch on a single name</strong>. Next time you want to trace an API path's full story, the route map is clear: go to <span class="mono">groups/</span> for its contract (what it wants, gives, how it errors), then the same-named <span class="mono">handlers/</span> for how it wires the work to core — and between the two stations, types guarantee they speak of the same thing.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key points</div>
  <ul>
    <li>Every opencode API endpoint splits in two: <strong>the group declares the contract</strong> (name/params/return/error, pure types), <strong>the handler implements</strong> (calls core for the work).</li>
    <li>An endpoint's <strong>errors are part of the contract</strong> too: what it might return is in the type, so the client's SDK knows it all by type.</li>
    <li><strong>The 21 group names are opencode's capability map</strong> — structured declaration lets the system always answer "what capabilities do I have."</li>
    <li>Handlers should be <strong>thin</strong>: input already validated by the group's types, it only "take clean input → call core → return." <span class="mono">handleRaw</span> is for the few endpoints needing manual Response control.</li>
    <li><strong>Middleware</strong> is the cross-cutting checkpoint ring; the error middleware does "truth into the log, an id to the client," while typed failures still take the main road.</li>
  </ul>
</div>
""",
}
LESSON_11 = {
    "zh": r"""
<p class="lead">上一课的 21 个组里，大多数都是「你问一句、我答一句」的一次性买卖：GET 一下拿到会话列表，POST 一下创建会话。但有一个组特别不一样——<span class="mono">event</span>。它只有<strong>一个端点</strong>，可这个端点一旦连上就<strong>不挂断</strong>，而是变成一条<strong>持续往客户端推送</strong>的长河。这一课我们就解剖这条河：服务器内部状态一变（来了新消息、工具开始跑、会话状态变了），怎么<strong>实时</strong>告诉每一个正在看的客户端？答案是 <strong>SSE（Server-Sent Events，服务器推送事件）</strong>，而它的源头，是一条贯穿 core 的<strong>事件总线</strong>。</p>
<p>为什么这条河值得单独讲一课？因为它是 opencode「<strong>多端实时一致</strong>」的命脉。你在 TUI 里看到 AI 一个字一个字往外蹦、工具调用的状态实时翻牌——这些<strong>不是 TUI 自己算出来的</strong>，而是 server 通过这条 SSE 河推过来的。网页端、桌面端连的是<strong>同一条河</strong>，所以它们看到的画面天然同步。读懂这一课，你就明白了 opencode 那种「换个客户端、进度一模一样」的魔法，根在哪里。</p>

<div class="card analogy">
  <div class="tag">📡 生活类比</div>
  想象你订了一份<strong>实时新闻直播</strong>。老办法（轮询）是你每隔十秒打一次电话问编辑部：「有新闻吗？有新闻吗？」——既烦人又总慢半拍。SSE 的办法是：你<strong>打通一个电话就一直挂着</strong>，编辑部那头<strong>一有新消息就立刻念给你听</strong>，你什么都不用做，只管听。更妙的是几个细节：你一拨通，编辑部<strong>第一句先报「连上了」</strong>（server.connected）让你安心；之后哪怕一时没新闻，对方也会每隔十秒「喂、还在吗」地<strong>响一声</strong>（heartbeat），免得线路被中间的总机当成空闲给掐了；而且——这点最关键——<strong>你一拨通的瞬间，编辑部就开始为你攒稿了</strong>，哪怕第一条还在路上，期间发生的新闻一条都不会漏。这通「永不挂断、主动播报、定时报平安、接通即开始攒」的电话，就是 SSE。
</div>

<h2>为什么是 SSE，而不是轮询或 WebSocket</h2>
<p>客户端要跟上服务器的变化，理论上有三条路。<strong>轮询</strong>：客户端每隔几秒问一次「有变化吗」——简单，但要么浪费（大多数时候没变化）、要么迟钝（间隔越大越慢）。<strong>WebSocket</strong>：开一条双向全双工通道——强大，但它是<strong>另一套协议</strong>，要单独握手、单独处理，对「只需要服务器→客户端单向推」的场景属于杀鸡用牛刀。<strong>SSE</strong> 取了个巧妙的中间点：它就是一个<strong>普通的 HTTP GET 请求</strong>，只不过响应体<strong>永远不结束</strong>，服务器源源不断往里写文本。</p>
<div class="cols">
  <div class="col"><h4>轮询 Polling</h4><p>客户端反复问。简单，但浪费带宽或反应迟钝，二选一。</p></div>
  <div class="col"><h4>WebSocket</h4><p>双向全双工。强大，但是另一套协议，单向场景下过重。</p></div>
  <div class="col"><h4>SSE（opencode 选这个）</h4><p>就是个不结束的 HTTP GET。单向推送、纯文本、浏览器原生支持、断线自动重连。</p></div>
</div>
<p>对 opencode 的需求来说，SSE 简直是量身定做：事件<strong>本来就是单向的</strong>（服务器有事告诉客户端，客户端没什么要实时回推的）；它<strong>就是 HTTP</strong>，于是上一课那套路由组、中间件、鉴权全都自动复用，不必为它另起炉灶；浏览器还<strong>原生支持</strong> <span class="mono">EventSource</span>、断了会自动重连。一个「不结束的 GET」，就把实时推送这件事，轻轻巧巧地塞进了既有的 HTTP 骨架里。</p>
<p>这里其实藏着一条很值得记住的设计哲学：<strong>能复用既有骨架，就别另造一套</strong>。WebSocket 不是不好，而是它带来的「另一套协议、另一套鉴权、另一套调试工具」的成本，只有在真正需要双向实时时才划算。opencode 的场景是清一色的「服务器播报、客户端收听」，于是它果断选了那个<strong>能让上一课所有基础设施原封不动复用</strong>的方案。这种「先问需求的形状、再挑最贴合的工具」的判断力，比记住三种技术的优劣表更重要——它解释的不是「SSE 是什么」，而是「为什么是 SSE」。</p>

<h2>event 组：一个端点，却返回一条流</h2>
<p>翻开 <span class="mono">groups/event.ts</span>，整个组干净得出奇——<strong>只有一个端点</strong> <span class="mono">subscribe</span>，路径 <span class="mono">GET /event</span>。但它的 <span class="mono">success</span> 类型，藏着全部玄机：</p>
<pre class="code"><span class="cm">// groups/event.ts —— success 不是 JSON，而是事件流</span>
HttpApiEndpoint.<span class="fn">get</span>(<span class="st">"subscribe"</span>, <span class="st">"/event"</span>, {
  query: WorkspaceRoutingQuery,
  success: Schema.String.<span class="fn">pipe</span>(
    HttpApiSchema.<span class="fn">asText</span>({ contentType: <span class="st">"text/event-stream"</span> })),
})</pre>
<p>看见 <span class="mono">contentType: "text/event-stream"</span> 了吗？这一行就是「我返回的不是一坨 JSON，而是一条 SSE 流」的官方声明。在上一课的契约世界里，这依然是一份规规矩矩的契约——只不过它承诺的回执，是<strong>一条永不终结的文本河</strong>，而非一次性的对象。组的末尾照例挂着三道中间件（实例上下文、工作区路由、鉴权），说明这条流和别的端点一样，<strong>要先过安检、要认领是哪个实例的事</strong>。声明部分到此为止，真正把河水接出来的活，在 handler 里。</p>
<div class="cellgroup">
  <div class="cell"><div class="k">端点</div><div class="v">只有一个：subscribe（GET /event）</div></div>
  <div class="cell"><div class="k">success</div><div class="v">text/event-stream —— 不是 JSON，是 SSE 流</div></div>
  <div class="cell"><div class="k">中间件</div><div class="v">实例上下文 + 工作区路由 + 鉴权，照常把关</div></div>
</div>

<h2>handler 里的流水线：从总线到 SSE</h2>
<p><span class="mono">handlers/event.ts</span> 是这一课的高潮。它把「core 里到处发生的事件」一路接成「写给客户端的 SSE 文本」，中间是一条优雅的 Effect <span class="mono">Stream</span> 流水线。我们顺着水流走一遍：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">events.listen(...) —— 立刻向实例事件总线登记一个监听器</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">每来一个事件，offer 进一个 unbounded 队列（先攒着，不丢）</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">addFinalizer(unsubscribe) —— 连接断了就注销监听，绝不泄漏</span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">Stream.fromQueue → filter：只留属于「本实例本工作区」的事件</span></div>
  <div class="t-row"><span class="t-num">5</span><span class="t-txt">merge 心跳流 + disposed 流，再 SSE 编码成文本，流式写回</span></div>
</div>
<p>第 1、2 步藏着一个<strong>极其重要、又极易被忽略</strong>的正确性细节。注意源码里那句注释：监听器是<strong>「eager（提前）」</strong>登记的——在 HTTP 响应体那个 fiber 还没真正开始吐数据之前，监听就已经挂好、事件已经开始往队列里攒了。为什么非这样不可？设想反过来：如果先开始发响应、再去登记监听，那么<strong>「发响应」和「登记监听」之间的那一瞬间</strong>里发生的事件，就会<strong>永远漏掉</strong>——客户端以为自己订阅了，却恰好错过了刚连上那一刻的几条消息。把登记提前到最前面，再配一个<strong>无界队列</strong>当蓄水池，就堵死了这个缝隙：<strong>从你订阅的第一刻起，事件只进队列、绝不丢失</strong>。</p>
<div class="flow">
  <div class="node">core 各处<span class="sub">发布 EventV2 事件</span></div>
  <div class="arrow">→</div>
  <div class="node">事件总线<span class="sub">listen 登记（eager）</span></div>
  <div class="arrow">→</div>
  <div class="node">unbounded 队列<span class="sub">蓄水·不丢</span></div>
  <div class="arrow">→</div>
  <div class="node">filter<span class="sub">只留本实例</span></div>
  <div class="arrow">→</div>
  <div class="node">SSE 流<span class="sub">写回客户端</span></div>
</div>
<p>第 4 步的 <span class="mono">filter</span> 也值得说一句。一台机器上可能同时跑着多个实例、多个工作区的会话，但事件总线是<strong>全局共享</strong>的——大家的事件都往同一条总线上发。所以每一条 SSE 连接都得<strong>戴上一副「过滤眼镜」</strong>：只放行 <span class="mono">directory</span> 和 <span class="mono">workspaceID</span> 都对得上自己的事件。这样一来，同一台 server 上 A 工作区的客户端，绝不会串台收到 B 工作区的动静。<strong>一条共享总线、N 副过滤眼镜</strong>——这就是多实例隔离在事件层的实现。</p>
<p>顺带留意那个队列选的是<strong>无界（unbounded）</strong>，这背后是一次有意的取舍。无界意味着：哪怕客户端读得慢、网络发得慢，生产者那头<strong>永远不会被堵住</strong>——core 里发事件的代码该跑就跑，绝不会因为某个客户端卡了而被反压拖慢。代价是内存：万一某条连接彻底不读了，队列会一直涨。opencode 在这里选了<strong>「宁可多占点内存，也绝不丢事件、绝不拖慢核心」</strong>，并用前面那个 <span class="mono">addFinalizer</span> 兜底——连接一断就注销监听、释放队列，把内存风险收口在「连接存活期间」。从这个小小的 unbounded 里，你能读出 opencode 对事件流的态度：<strong>事件的完整与核心的流畅，优先于内存的精打细算</strong>。</p>

<h2>开场白、心跳、与谢幕</h2>
<p>最后一步把流真正组装成 SSE 响应，这里有三个贴心的设计，对应一段连接的<strong>一生</strong>。开场：流的第一条永远是 <span class="mono">server.connected</span>，等于电话接通后那句「连上了」，让客户端确认订阅成功。中场：把真正的业务事件流，和一条<strong>每 10 秒一跳的心跳流</strong>（<span class="mono">server.heartbeat</span>）<span class="mono">merge</span> 在一起。谢幕：整条流 <span class="mono">takeUntil</span> 收到 <span class="mono">server.instance.disposed</span>——实例被销毁，河就到此为止，优雅地流干、关闭。</p>
<div class="cellgroup">
  <div class="cell"><div class="k">server.connected</div><div class="v">开场白·流的第一条·确认订阅成功</div></div>
  <div class="cell"><div class="k">server.heartbeat</div><div class="v">每 10s 一跳·报平安·防连接被掐</div></div>
  <div class="cell"><div class="k">server.instance.disposed</div><div class="v">谢幕信号·takeUntil 据此结束整条流</div></div>
</div>
<p>这三条「带 server. 前缀」的事件，和真正的业务事件（message.updated、tool.start 之类）混在同一条流里，但角色完全不同：业务事件是<strong>河里的水</strong>，而这三条是<strong>河的开闸、心跳与关闸</strong>——它们不携带业务信息，只负责管理这条连接本身的生命周期。把「连接管理」也做成事件、和数据走同一条管道，是个很干净的设计：客户端只需<strong>一套</strong>处理事件的逻辑，连「我连上了没」「对面还活着吗」「该收尾了」这些控制信号，都顺着同一条河自然流过来，不必另开旁路。</p>
<div class="timeline">
  <div class="tl-item"><span class="tl-time">t=0</span><span class="tl-desc">server.connected —— 「连上了」，订阅确认</span></div>
  <div class="tl-item"><span class="tl-time">t=0.3s</span><span class="tl-desc">message.updated、tool.start… 真实业务事件陆续推来</span></div>
  <div class="tl-item"><span class="tl-time">每 10s</span><span class="tl-desc">server.heartbeat —— 「还在」，防止线路被当空闲掐掉</span></div>
  <div class="tl-item"><span class="tl-time">t=end</span><span class="tl-desc">server.instance.disposed —— 实例销毁，takeUntil 结束这条流</span></div>
</div>
<p>那条<strong>心跳</strong>看似无聊，实则是工程上的救命设计。现实里，客户端和 server 之间常隔着代理、负载均衡、网关——这些中间设备最爱干一件事：<strong>把「一段时间没动静」的连接当成死链给掐了</strong>。一旦 AI 正在长考、十几秒没有新事件，连接就可能被中途掐断。每 10 秒发一个 <span class="mono">server.heartbeat</span>，等于不断告诉沿途所有设备「这条线还活着，别动它」。响应头里那句 <span class="mono">Cache-Control: no-cache, no-transform</span> 也是同样的苦心——<strong>no-transform</strong> 是在央求中间的代理：千万别自作聪明地缓冲、压缩、改写我这条流，逐条原样放行就好。实时系统的细节，全在这些和基础设施「斗智斗勇」的小动作里。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <p>把这一课放回全局：opencode 里<strong>「读」状态有两条通道</strong>——一次性的查询（GET 会话、消息，第 10 课那些普通端点），和持续的推送（这一课的 SSE）。两者分工明确：</p>
  <ul>
    <li><strong>core 各处</strong>发布 EventV2 事件到共享<strong>事件总线</strong>（GlobalBus / 实例总线）。</li>
    <li><strong>event handler</strong> 把总线接成 SSE：eager 监听 → 无界队列蓄水 → 按实例过滤 → 合并心跳 → 编码推出。</li>
    <li><strong>客户端</strong>（TUI/网页/桌面）连一次 <span class="mono">GET /event</span>，就拿到一条实时的状态河，多端天然同步。</li>
  </ul>
  <p>这条河的「下游」是谁、客户端拿到事件后怎么把它喂进自己的本地状态？那是第 54 课（events → store）的故事。这一课你只要记住：<strong>实时，是推出来的，不是问出来的</strong>。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p>SSE 响应的组装，是一段教科书级的 Stream 拼接——开场白 ++ (业务事件 merge 心跳) → SSE 编码 → 文本：</p>
  <pre class="code"><span class="cm">// 简化自 handlers/event.ts</span>
HttpServerResponse.<span class="fn">stream</span>(
  Stream.<span class="fn">make</span>({ type: <span class="st">"server.connected"</span>, ... })  <span class="cm">// 开场白</span>
    .<span class="fn">pipe</span>(
      Stream.<span class="fn">concat</span>(output.<span class="fn">pipe</span>(
        Stream.<span class="fn">merge</span>(heartbeat, { haltStrategy: <span class="st">"left"</span> }))),  <span class="cm">// 业务+心跳</span>
      Stream.<span class="fn">map</span>(eventData),
      Stream.<span class="fn">pipeThroughChannel</span>(Sse.<span class="fn">encode</span>()),  <span class="cm">// 编成 SSE 线格式</span>
      Stream.encodeText,
    ),
  { contentType: <span class="st">"text/event-stream"</span>,
    headers: { <span class="st">"Cache-Control"</span>: <span class="st">"no-cache, no-transform"</span> } })</pre>
  <p>每一段 <span class="mono">.pipe</span> 都是一道工序：先放开场白，接上「业务事件与心跳合流」的主体，逐条变成 SSE 事件对象，过 <span class="mono">Sse.encode()</span> 编成 <span class="mono">data: ...\n\n</span> 的线缆格式，最后转成字节流写回。<strong>声明式的流水线，把「实时推送」这件复杂的事，写成了一串可读的管道。</strong></p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li>opencode 用 <strong>SSE</strong>（一个永不结束的 HTTP GET）做服务器→客户端的实时推送：比轮询省、比 WebSocket 轻，且自动复用既有 HTTP 骨架。</li>
    <li><span class="mono">event</span> 组只有一个端点，玄机在 <span class="mono">success</span> 的 <span class="mono">contentType: "text/event-stream"</span>——契约承诺的是一条流，不是一个对象。</li>
    <li>handler 的流水线：<strong>eager 登记监听 → 无界队列蓄水 → 按实例/工作区 filter → 合并心跳 → SSE 编码推出</strong>。</li>
    <li><strong>提前登记监听</strong>是关键正确性细节：堵住「开始响应」与「登记监听」之间的缝隙，订阅那一刻起事件绝不丢失。</li>
    <li><strong>心跳（每 10s）+ no-transform</strong> 是为了对抗中间代理：防连接被当空闲掐断、防流被缓冲改写。多端实时一致的根，就是这条河。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Of the last lesson's 21 groups, most are one-shot "you ask, I answer" deals: GET the session list, POST to create a session. But one group is special — <span class="mono">event</span>. It has <strong>a single endpoint</strong>, yet once that endpoint connects it <strong>never hangs up</strong>, instead becoming a long river that <strong>continuously pushes to the client</strong>. This lesson dissects that river: when the server's internal state changes (a new message arrives, a tool starts running, a session's status flips), how does it tell every watching client <strong>in real time</strong>? The answer is <strong>SSE (Server-Sent Events)</strong>, and its headwater is an <strong>event bus</strong> running through core.</p>
<p>Why does this river deserve its own lesson? Because it's the lifeline of opencode's <strong>multi-client real-time consistency</strong>. The AI spitting out one character at a time in your TUI, tool-call statuses flipping live — these <strong>aren't computed by the TUI itself</strong>; the server pushes them down this SSE river. The web and desktop clients connect to the <strong>same river</strong>, so what they see is naturally in sync. Grasp this lesson and you'll know where opencode's "switch clients, identical progress" magic is rooted.</p>

<div class="card analogy">
  <div class="tag">📡 Analogy</div>
  Imagine you subscribe to a <strong>live news feed</strong>. The old way (polling) is calling the newsroom every ten seconds: "Any news? Any news?" — annoying and always a beat behind. The SSE way: you <strong>dial once and keep the line open</strong>, and the newsroom <strong>reads each new item to you the instant it breaks</strong>; you do nothing but listen. Better still, a few details: the moment you connect, they <strong>first say "you're connected"</strong> (server.connected) to reassure you; then even with no news, they <strong>chirp every ten seconds</strong> ("still there?") (heartbeat), lest some switchboard in the middle mistake the line for idle and cut it; and — most crucial — <strong>the instant you dial in, they start saving copy for you</strong>, so even while the first item is still en route, nothing breaking in the meantime is missed. This "never hangs up, broadcasts actively, pings periodically, starts saving on connect" call is SSE.
</div>

<h2>Why SSE, not polling or WebSocket</h2>
<p>To keep up with the server's changes, a client has, in theory, three roads. <strong>Polling</strong>: the client asks "any change?" every few seconds — simple, but either wasteful (mostly nothing changed) or sluggish (the longer the interval, the slower). <strong>WebSocket</strong>: open a bidirectional full-duplex channel — powerful, but it's <strong>a separate protocol</strong> needing its own handshake and handling, overkill for a "server→client one-way push" scenario. <strong>SSE</strong> takes a clever middle point: it's just an <strong>ordinary HTTP GET request</strong>, except the response body <strong>never ends</strong> and the server keeps writing text into it.</p>
<div class="cols">
  <div class="col"><h4>Polling</h4><p>Client asks repeatedly. Simple, but pick one: wasted bandwidth or sluggish reaction.</p></div>
  <div class="col"><h4>WebSocket</h4><p>Bidirectional full-duplex. Powerful, but a separate protocol, too heavy for one-way.</p></div>
  <div class="col"><h4>SSE (opencode's pick)</h4><p>Just a GET that never ends. One-way push, plain text, native browser support, auto-reconnect.</p></div>
</div>
<p>For opencode's needs, SSE is tailor-made: events are <strong>one-way by nature</strong> (the server has things to tell the client; the client has nothing to push back in real time); it <strong>is HTTP</strong>, so the last lesson's route groups, middleware, and auth all auto-reuse with no separate setup; and browsers <strong>natively support</strong> <span class="mono">EventSource</span> and auto-reconnect on drop. One "GET that never ends" slips real-time push neatly into the existing HTTP skeleton.</p>
<p>There's a design philosophy here worth remembering: <strong>if you can reuse the existing skeleton, don't build another</strong>. WebSocket isn't bad; its cost — "another protocol, another auth, another set of debugging tools" — only pays off when you truly need bidirectional real-time. opencode's scenario is uniformly "server broadcasts, client listens," so it decisively chose the option that <strong>lets all of last lesson's infrastructure be reused untouched</strong>. This "ask the shape of the need first, then pick the most fitting tool" judgment matters more than memorizing a pros-and-cons table of three technologies — it explains not "what SSE is" but "why SSE."</p>

<h2>The event group: one endpoint, but it returns a stream</h2>
<p>Open <span class="mono">groups/event.ts</span> and the whole group is startlingly clean — <strong>just one endpoint</strong>, <span class="mono">subscribe</span>, path <span class="mono">GET /event</span>. But its <span class="mono">success</span> type hides the whole trick:</p>
<pre class="code"><span class="cm">// groups/event.ts — success is not JSON but an event stream</span>
HttpApiEndpoint.<span class="fn">get</span>(<span class="st">"subscribe"</span>, <span class="st">"/event"</span>, {
  query: WorkspaceRoutingQuery,
  success: Schema.String.<span class="fn">pipe</span>(
    HttpApiSchema.<span class="fn">asText</span>({ contentType: <span class="st">"text/event-stream"</span> })),
})</pre>
<p>See <span class="mono">contentType: "text/event-stream"</span>? That one line is the official declaration of "what I return is not a blob of JSON but an SSE stream." In last lesson's contract world, this is still a perfectly proper contract — only the receipt it promises is <strong>a never-ending river of text</strong>, not a one-shot object. The group's tail carries three middlewares as usual (instance context, workspace routing, auth), meaning this stream, like any endpoint, <strong>passes security first and claims which instance it belongs to</strong>. The declaration ends here; the real work of piping the water out is in the handler.</p>
<div class="cellgroup">
  <div class="cell"><div class="k">endpoint</div><div class="v">just one: subscribe (GET /event)</div></div>
  <div class="cell"><div class="k">success</div><div class="v">text/event-stream — not JSON, an SSE stream</div></div>
  <div class="cell"><div class="k">middleware</div><div class="v">instance context + workspace routing + auth, guarding as usual</div></div>
</div>

<h2>The pipeline in the handler: from bus to SSE</h2>
<p><span class="mono">handlers/event.ts</span> is this lesson's climax. It pipes "events happening all over core" into "SSE text written to the client," via an elegant Effect <span class="mono">Stream</span> pipeline. Let's walk the current:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">events.listen(...) — register a listener on the instance event bus immediately</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">every event arriving is offered into an unbounded queue (buffered, not dropped)</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">addFinalizer(unsubscribe) — connection drops, listener unregisters, never leaks</span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">Stream.fromQueue → filter: keep only events for "this instance, this workspace"</span></div>
  <div class="t-row"><span class="t-num">5</span><span class="t-txt">merge a heartbeat stream + a disposed stream, then SSE-encode to text, stream back</span></div>
</div>
<p>Steps 1 and 2 hide a correctness detail that is <strong>extremely important yet easily overlooked</strong>. Note the comment in the source: the listener is registered <strong>"eagerly"</strong> — before the HTTP response-body fiber even starts emitting, the listener is already hooked up and events are already piling into the queue. Why must it be this way? Picture the reverse: if you started sending the response first and only then registered the listener, any event in that <strong>instant between "start responding" and "register listener"</strong> would be <strong>lost forever</strong> — the client thinks it subscribed but happens to miss the few messages from the very moment it connected. Moving registration to the very front, paired with an <strong>unbounded queue</strong> as a reservoir, seals this gap: <strong>from the first moment you subscribe, events only enter the queue, never dropped</strong>.</p>
<div class="flow">
  <div class="node">all over core<span class="sub">publish EventV2 events</span></div>
  <div class="arrow">→</div>
  <div class="node">event bus<span class="sub">listen registered (eager)</span></div>
  <div class="arrow">→</div>
  <div class="node">unbounded queue<span class="sub">buffer · no drop</span></div>
  <div class="arrow">→</div>
  <div class="node">filter<span class="sub">keep this instance</span></div>
  <div class="arrow">→</div>
  <div class="node">SSE stream<span class="sub">write to client</span></div>
</div>
<p>Step 4's <span class="mono">filter</span> deserves a word too. One machine may run sessions for several instances and workspaces at once, but the event bus is <strong>globally shared</strong> — everyone's events go onto the same bus. So each SSE connection must <strong>put on a pair of "filter glasses"</strong>: only let through events whose <span class="mono">directory</span> and <span class="mono">workspaceID</span> match its own. That way, on the same server, workspace A's client never crosses wires to receive workspace B's activity. <strong>One shared bus, N pairs of filter glasses</strong> — that's multi-instance isolation at the event layer.</p>
<p>Note in passing that the queue chosen is <strong>unbounded</strong>, a deliberate tradeoff. Unbounded means: even if the client reads slowly or the network sends slowly, the producer side is <strong>never blocked</strong> — the event-publishing code in core runs as it should, never slowed by backpressure from a stuck client. The cost is memory: if some connection stops reading entirely, the queue grows. Here opencode chose <strong>"rather spend a bit more memory than ever drop an event or ever slow the core,"</strong> backstopped by that <span class="mono">addFinalizer</span> — the moment a connection drops, the listener unregisters and the queue is released, capping the memory risk to "while the connection lives." From this tiny unbounded you can read opencode's stance on event streams: <strong>completeness of events and smoothness of core take priority over penny-pinching memory</strong>.</p>

<h2>Opening line, heartbeat, and curtain call</h2>
<p>The last step assembles the stream into an actual SSE response, with three thoughtful designs matching a connection's <strong>whole life</strong>. Opening: the stream's first item is always <span class="mono">server.connected</span>, like "you're connected" right after the call goes through, confirming the subscription. Middle: the real business-event stream is <span class="mono">merge</span>d with a <strong>heartbeat stream that ticks every 10 seconds</strong> (<span class="mono">server.heartbeat</span>). Curtain call: the whole stream <span class="mono">takeUntil</span> it receives <span class="mono">server.instance.disposed</span> — the instance is destroyed, the river ends here, draining and closing gracefully.</p>
<div class="cellgroup">
  <div class="cell"><div class="k">server.connected</div><div class="v">opening · stream's first item · confirms subscription</div></div>
  <div class="cell"><div class="k">server.heartbeat</div><div class="v">every 10s · "still alive" · keeps the connection from being cut</div></div>
  <div class="cell"><div class="k">server.instance.disposed</div><div class="v">curtain signal · takeUntil ends the whole stream on it</div></div>
</div>
<p>These three "server.-prefixed" events mix into the same stream as real business events (message.updated, tool.start, and so on), but their role is entirely different: business events are <strong>the water in the river</strong>, while these three are <strong>the river's opening gate, heartbeat, and closing gate</strong> — they carry no business info, only manage this connection's own lifecycle. Making "connection management" into events too, traveling the same pipe as data, is a very clean design: the client needs only <strong>one</strong> set of event-handling logic, and even control signals like "am I connected," "is the other side still alive," "time to wrap up" flow down the same river naturally, with no side channel.</p>
<div class="timeline">
  <div class="tl-item"><span class="tl-time">t=0</span><span class="tl-desc">server.connected — "you're connected," subscription confirmed</span></div>
  <div class="tl-item"><span class="tl-time">t=0.3s</span><span class="tl-desc">message.updated, tool.start… real business events stream in</span></div>
  <div class="tl-item"><span class="tl-time">every 10s</span><span class="tl-desc">server.heartbeat — "still here," keeps the line from being cut as idle</span></div>
  <div class="tl-item"><span class="tl-time">t=end</span><span class="tl-desc">server.instance.disposed — instance destroyed, takeUntil ends the stream</span></div>
</div>
<p>That <strong>heartbeat</strong> looks dull but is a lifesaving piece of engineering. In reality, proxies, load balancers, and gateways often sit between client and server — and their favorite trick is to <strong>cut a connection that's been quiet for a while as a dead link</strong>. The moment the AI is deep in thought and a dozen seconds pass with no new event, the connection could be severed mid-way. Sending a <span class="mono">server.heartbeat</span> every 10 seconds keeps telling every device along the path "this line is alive, leave it be." The <span class="mono">Cache-Control: no-cache, no-transform</span> in the response headers comes from the same care — <strong>no-transform</strong> begs the intermediary proxies: don't cleverly buffer, compress, or rewrite my stream; pass it through item by item. The details of a real-time system all live in these little "outsmart-the-infrastructure" moves.</p>

<div class="card macro">
  <div class="tag">🗺️ The big picture</div>
  <p>Place this lesson back in the whole: opencode has <strong>two channels for "reading" state</strong> — one-shot queries (GET sessions, messages, the ordinary endpoints of Lesson 10), and continuous push (this lesson's SSE). Their division of labor is clear:</p>
  <ul>
    <li><strong>All over core</strong>, EventV2 events are published to a shared <strong>event bus</strong> (GlobalBus / instance bus).</li>
    <li><strong>The event handler</strong> pipes the bus into SSE: eager listen → unbounded queue buffer → filter by instance → merge heartbeat → encode and push out.</li>
    <li><strong>Clients</strong> (TUI/web/desktop) connect once to <span class="mono">GET /event</span> and get a real-time river of state, naturally in sync across ends.</li>
  </ul>
  <p>Who is this river's "downstream," and how does a client feed received events into its own local state? That's Lesson 54's story (events → store). For this lesson, just remember: <strong>real-time is pushed, not asked for</strong>.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source detail</div>
  <p>Assembling the SSE response is a textbook Stream concatenation — opening ++ (business events merge heartbeat) → SSE encode → text:</p>
  <pre class="code"><span class="cm">// simplified from handlers/event.ts</span>
HttpServerResponse.<span class="fn">stream</span>(
  Stream.<span class="fn">make</span>({ type: <span class="st">"server.connected"</span>, ... })  <span class="cm">// opening</span>
    .<span class="fn">pipe</span>(
      Stream.<span class="fn">concat</span>(output.<span class="fn">pipe</span>(
        Stream.<span class="fn">merge</span>(heartbeat, { haltStrategy: <span class="st">"left"</span> }))),  <span class="cm">// business+heartbeat</span>
      Stream.<span class="fn">map</span>(eventData),
      Stream.<span class="fn">pipeThroughChannel</span>(Sse.<span class="fn">encode</span>()),  <span class="cm">// encode to SSE wire format</span>
      Stream.encodeText,
    ),
  { contentType: <span class="st">"text/event-stream"</span>,
    headers: { <span class="st">"Cache-Control"</span>: <span class="st">"no-cache, no-transform"</span> } })</pre>
  <p>Each <span class="mono">.pipe</span> is a stage: lay down the opening, attach the body of "business events and heartbeat merged," turn each into an SSE event object, run it through <span class="mono">Sse.encode()</span> into the <span class="mono">data: ...\n\n</span> wire format, and finally turn it into a byte stream written back. <strong>A declarative pipeline turns the complex matter of "real-time push" into a readable string of pipes.</strong></p>
</div>

<div class="card key">
  <div class="tag">🎯 Key points</div>
  <ul>
    <li>opencode uses <strong>SSE</strong> (an HTTP GET that never ends) for server→client real-time push: cheaper than polling, lighter than WebSocket, and auto-reuses the existing HTTP skeleton.</li>
    <li>The <span class="mono">event</span> group has one endpoint; the trick is <span class="mono">success</span>'s <span class="mono">contentType: "text/event-stream"</span> — the contract promises a stream, not an object.</li>
    <li>The handler pipeline: <strong>eager listen → unbounded queue buffer → filter by instance/workspace → merge heartbeat → SSE-encode and push</strong>.</li>
    <li><strong>Registering the listener eagerly</strong> is the key correctness detail: it seals the gap between "start responding" and "register listener," so no event is lost from the moment of subscription.</li>
    <li><strong>Heartbeat (every 10s) + no-transform</strong> fight intermediary proxies: prevent the connection being cut as idle, prevent the stream being buffered or rewritten. Multi-client real-time consistency is rooted in this river.</li>
  </ul>
</div>
""",
}
LESSON_12 = wip('SDK 生成', 'Generating the SDK')
LESSON_13 = wip('多客户端传输', 'Multi-client transports')
