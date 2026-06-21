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
LESSON_10 = wip('路由组与 handler', 'Route groups & handlers')
LESSON_11 = wip('SSE 事件总线', 'The SSE event bus')
LESSON_12 = wip('SDK 生成', 'Generating the SDK')
LESSON_13 = wip('多客户端传输', 'Multi-client transports')
