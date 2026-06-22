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
  <div class="layer l-main"><div class="lh"><span class="badge">路由组</span><span class="name">session / event / config… ×20</span></div><div class="ld">各领域的端点契约</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">handler</span><span class="name">handlers/*</span></div><div class="ld">调用 core 服务，干真正的活</div></div>
</div>

<p>"server 对外只是一个函数"这个事实，比它听起来更重要。正因为 handler 的形态如此标准、如此纯粹——进一个 Request、出一个 Response，没有任何对"真实网络"的硬依赖——它才能被随意<strong>嫁接到不同的传输上</strong>：架在 Node 的 HTTP 服务器上，它是个网络服务；塞进一个 worker 线程里直接调用，它就成了富 TUI 那套零网络的进程内通信。<strong>同一套业务逻辑、传输层可热插拔</strong>——这又是第 6 课"实现可整体替换"在 server 这一层的回响。</p>
<p>那 handler 里到底装着什么？一个端点的 handler，干的就是"<strong>把校验过的输入，翻译成对 core 服务的调用，再把结果编码回去</strong>"——它是这扇门和门后真正干活的 core 之间<strong>薄薄的一层转接</strong>。理想情况下 handler 应该很薄：重活都在 core 的 Session、Tool 那些服务里，handler 只负责"在 HTTP 世界和 Effect 世界之间搬运"。下一课就专门拆开路由组与 handler，看这层转接具体长什么样。</p>

<h2>20 个路由组：按领域切开</h2>
<p>这张"服务清单"不是一长串扁平的路径，而是<strong>按领域切成了 20 个组</strong>，各管一摊：</p>
<table class="t">
  <tr><th>组</th><th>管什么</th></tr>
  <tr><td><span class="mono">session</span></td><td>会话：创建、发 prompt、取历史——agent 的主战场</td></tr>
  <tr><td><span class="mono">event</span></td><td>事件流：把 server 内部的事件推给客户端（SSE）</td></tr>
  <tr><td><span class="mono">config</span> · <span class="mono">provider</span></td><td>配置、模型 provider</td></tr>
  <tr><td><span class="mono">permission</span> · <span class="mono">question</span></td><td>权限确认、向用户提问</td></tr>
  <tr><td><span class="mono">file</span> · <span class="mono">project</span> · <span class="mono">pty</span></td><td>文件、项目、伪终端</td></tr>
  <tr><td><span class="mono">mcp</span> · <span class="mono">tui</span> · <span class="mono">workspace</span> …</td><td>MCP、TUI 专用、工作区等（共 20 组）</td></tr>
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

<p>顺带说，这 20 个组的名字本身，就是一张 opencode 能力的<strong>地图</strong>：<span class="mono">session</span> 是 agent 主战场，<span class="mono">event</span> 撑起实时性，<span class="mono">permission</span>/<span class="mono">question</span> 管"放手让 AI 干活但可控"，<span class="mono">pty</span>/<span class="mono">file</span> 让它能真的动你的项目，<span class="mono">mcp</span>/<span class="mono">workspace</span> 通向扩展与多实例。你几乎可以靠这份组清单，倒推出 opencode 大致能做哪些事。后面好几课会逐一深入其中的组——它们在 server 这一层的"门牌"，就挂在这里。换句话说，读 server 的路由组，就像读一份目录——你还没翻开任何一章，已经大致知道这本书讲些什么了。</p>

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
  <div class="col"><h4>WebSocketTracker</h4><p>跟踪当前的 WebSocket 连接——给 pty 终端、工作区代理这类真正用到 WebSocket 的双向通道收尾用的。</p></div>
</div>
<p>它们不是主角，但点出了一件事：server 不只是"收 HTTP 请求"，它还要管<strong>发现、实时连接</strong>这些"活"的东西。把这些都收进同一个 server，正是第 1 课"server 拥有一切"的具体体现。</p>
<p>把这两个零件和前面的 webHandler、路由组放一起看，server 的全貌就清楚了：它是一个<strong>常驻的、自描述的、可被多种方式连上的能力中枢</strong>。它不挑客户端——谁能说 HTTP、谁能连上来，就能调用它的全部本事。这种"<strong>一个中枢、广开门户</strong>"的姿态，正是 opencode 能长出 TUI、网页、桌面、Slack、ACP 这么多张脸的底层原因，也是下一课要深入的"路由组与 handler"所站立的地基。</p>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  opencode 的 server <strong>不是 Hono</strong>，而是架在 Effect <span class="mono">HttpApi</span> 上：你<strong>先用类型声明整套 API 的形状</strong>（每个端点的输入/输出/错误），编译器替你守契约，机器还能读懂它。对外它就是<strong>一个 <span class="mono">(request) =&gt; Response</span> 的 webHandler</strong>（所以能既走网络、又走进程内 RPC）；内部按领域切成 <strong>20 个路由组</strong>（session/event/config…）。最大的回报是 <span class="mono">OpenApi.fromApi</span>——<strong>API 自己描述自己</strong>，自动生成 SDK，让多个客户端的类型永远和 server 对齐。把这一课收进一句话：server 是 opencode <strong>自描述的能力中枢</strong>，所有客户端都顺着这份类型化的契约来和它对话——读懂了这扇门，就读懂了整个第三部分的入口。再往深一层，这个选择体现了 opencode 的一贯主张：宁可前期多花功夫把契约钉进类型，也不愿后期为"接口对不齐"反复买单。记住这条主线：客户端永远不直接碰 core，而是隔着这扇<strong>类型化的门</strong>说话；门后是 20 个分领域的房间，门本身则自动印出进门用的手册。把这扇门看清楚，第三部分后面几课（路由与 handler、事件流、SDK、多客户端传输）都只是在放大它的不同侧面。
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
  路由组都在 <span class="mono">routes/instance/httpapi/groups/</span> 下（session.ts、event.ts、config.ts… 20 个组、21 个 .ts 文件），handler 在 <span class="mono">handlers/</span>，请求进组前还会先过一层 <span class="mono">middleware/</span> 统一鉴权、压缩、处理错误。
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>server <strong>不是 Hono</strong>，而是 Effect 的 <span class="mono">HttpApi</span>：<strong>先用类型声明 API 形状</strong>，契约进类型。</li>
    <li>对外是<strong>一个 <span class="mono">(request) =&gt; Response</span> 的 webHandler</strong>——所以能既走网络、又走进程内 RPC（第 3、13 课）。</li>
    <li>按领域切成 <strong>20 个路由组</strong>（session/event/config/provider/mcp…），各自内聚。</li>
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
  <div class="layer l-main"><div class="lh"><span class="badge">Route groups</span><span class="name">session / event / config… ×20</span></div><div class="ld">per-domain endpoint contracts</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">handler</span><span class="name">handlers/*</span></div><div class="ld">call core services, do the real work</div></div>
</div>
<p>The fact "the server outward is just a function" matters more than it sounds. Precisely because the handler's form is so standard and pure — in a Request, out a Response, no hard dependency on a "real network" — it can be freely <strong>grafted onto different transports</strong>: on Node's HTTP server it's a network service; dropped into a worker thread and called directly, it becomes the rich TUI's zero-network in-process communication. <strong>One business logic, hot-swappable transport</strong> — again Lesson 6's "wholesale-swappable impl" echoing at the server layer.</p>
<p>What's actually inside a handler? An endpoint's handler does "<strong>translate validated input into calls on core services, then encode the result back</strong>" — it's a <strong>thin layer of adaptation</strong> between this door and the core that does the real work behind it. Ideally a handler is thin: the heavy lifting is in core's Session, Tool services, and the handler only "ferries between the HTTP world and the Effect world." The next lesson takes route groups and handlers apart to see what this adaptation looks like.</p>

<h2>20 route groups: cut by domain</h2>
<p>This "service menu" isn't one long flat list of paths but <strong>cut into 20 groups by domain</strong>, each minding one area:</p>
<table class="t">
  <tr><th>Group</th><th>What it handles</th></tr>
  <tr><td><span class="mono">session</span></td><td>sessions: create, send a prompt, fetch history — the agent's main battlefield</td></tr>
  <tr><td><span class="mono">event</span></td><td>the event stream: push the server's internal events to clients (SSE)</td></tr>
  <tr><td><span class="mono">config</span> · <span class="mono">provider</span></td><td>config, model providers</td></tr>
  <tr><td><span class="mono">permission</span> · <span class="mono">question</span></td><td>permission confirmation, asking the user</td></tr>
  <tr><td><span class="mono">file</span> · <span class="mono">project</span> · <span class="mono">pty</span></td><td>files, projects, pseudo-terminal</td></tr>
  <tr><td><span class="mono">mcp</span> · <span class="mono">tui</span> · <span class="mono">workspace</span> …</td><td>MCP, TUI-specific, workspaces, etc. (20 groups total)</td></tr>
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
<p>Incidentally, these 20 groups' names are themselves a <strong>map</strong> of opencode's abilities: <span class="mono">session</span> is the agent's battlefield, <span class="mono">event</span> powers real-time, <span class="mono">permission</span>/<span class="mono">question</span> manage "let the AI work but stay in control," <span class="mono">pty</span>/<span class="mono">file</span> let it actually touch your project, <span class="mono">mcp</span>/<span class="mono">workspace</span> lead to extensibility and multi-instance. You could almost reverse-engineer roughly what opencode can do from this group list. Several later lessons dive into these groups — their "doorplate" at the server layer hangs right here. In other words, reading the server's route groups is like reading a table of contents — before opening any chapter you roughly know what the book is about.</p>

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
  <div class="col"><h4>WebSocketTracker</h4><p>Tracks current WebSocket connections — used to shut down pty terminals and workspace-proxy channels, the parts that actually use WebSocket.</p></div>
</div>
<p>They aren't the stars, but they point out one thing: the server isn't just "take HTTP requests"; it also manages <strong>discovery and live connections</strong>, the "living" things. Folding these into the same server is the concrete embodiment of Lesson 1's "the server owns everything." Put these two with the earlier webHandler and route groups and the server's whole shape is clear: it's a <strong>resident, self-describing capability hub connectable many ways</strong>. It doesn't pick clients — whoever speaks HTTP and connects gets all its abilities. This "<strong>one hub, doors wide open</strong>" stance is the underlying reason opencode grows so many faces — TUI, web, desktop, Slack, ACP — and the ground the next lesson's "route groups and handlers" stands on.</p>

<div class="card macro">
  <div class="tag">🌍 Big picture</div>
  opencode's server is <strong>not Hono</strong> but built on Effect <span class="mono">HttpApi</span>: you <strong>declare the whole API's shape in types first</strong> (each endpoint's input/output/error), the compiler guards the contract, and a machine can read it. Outward it's <strong>one <span class="mono">(request) =&gt; Response</span> webHandler</strong> (so it runs over the network or in-process RPC); internally it's cut by domain into <strong>20 route groups</strong> (session/event/config…). The biggest payoff is <span class="mono">OpenApi.fromApi</span> — <strong>the API describes itself</strong>, auto-generating an SDK so many clients' types always align with the server. In one line: the server is opencode's self-describing capability hub; all clients talk to it along this typed contract — see this door clearly and the rest of Part 3 (routes, event stream, SDK, transport) just magnifies its sides.
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
  Route groups live under <span class="mono">routes/instance/httpapi/groups/</span> (session.ts, event.ts, config.ts… 20 groups across 21 files), handlers under <span class="mono">handlers/</span>, with a <span class="mono">middleware/</span> layer doing auth, compression, and error handling before a request reaches its group.
</div>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>The server is <strong>not Hono</strong> but Effect's <span class="mono">HttpApi</span>: <strong>declare the API shape in types</strong>, contract in the type.</li>
    <li>Outward it's <strong>one <span class="mono">(request) =&gt; Response</span> webHandler</strong> — so it runs over network or in-process RPC (Lessons 3, 13).</li>
    <li>Cut by domain into <strong>20 route groups</strong> (session/event/config/provider/mcp…), each cohesive.</li>
    <li><span class="mono">OpenApi.fromApi(PublicApi)</span> makes <strong>the API describe itself</strong>, auto-generating the SDK (Lesson 12).</li>
    <li>It also carries MDNS (local discovery) and WebSocketTracker (live connections).</li>
  </ul>
</div>
""",
}
LESSON_10 = {
    "zh": r"""
<p class="lead">上一课我们站在门口，看清了 server 这扇门的整体长相：一个 <span class="mono">webHandler</span>、背后挂着 <strong>20 个路由组</strong>。这一课我们<strong>推门进去</strong>，把镜头怼到<strong>其中一个组</strong>身上，看它到底由什么拼成。你会发现 opencode 的每个 API 端点都分成两半：<strong>「组」负责声明契约</strong>（这个端点叫什么、要什么、给什么、可能怎么错），<strong>「handler」负责照约办事</strong>（把校验过的输入翻译成对 core 的调用）。再加上裹在外面的一圈<strong>中间件</strong>，三者合起来，才是一个请求从进门到出门的完整旅程。读懂这一课，你就能拿着任何一个 API 路径，自己摸到它的声明在哪、实现在哪。</p>
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
  <div class="node">HttpApi<span class="sub">整张 API·20 组汇总</span></div>
</div>

<h2>20 个组，就是一张能力地图</h2>
<p>这 20 个组的<strong>名字本身</strong>，几乎就是 opencode 全部对外能力的目录。你不用读实现，光看组名就能猜个八九不离十：</p>
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
<p>（上面只列了 8 个，其余还有 instance、workspace、project、question、pty、sync、control、global 等，凑满 20 个组——groups/ 目录里其实有 21 个 .ts 文件，但 metadata.ts、query.ts 只是辅助模块，而 pty.ts 拆出 pty 与 pty-connect 两个组。）这件事很值得停下来体会：<strong>当 API 是结构化声明时，它的「目录」是天然存在、可枚举的</strong>。你想知道 opencode 能干什么？不用读文档、不用问人，把 <span class="mono">groups/</span> 目录 <span class="mono">ls</span> 一遍，能力清单就在眼前。这是 Hono 那种「路由散落各处」的写法给不了的——在那里，没有人能一眼说清「这个服务总共开了哪些口」。声明式的代价是前期啰嗦，红利是<strong>系统永远能自己回答「我有哪些能力」</strong>。这种「可枚举性」还会一路传导：能力可枚举，文档就能自动生成、SDK 就能自动产出，连测试都能照着清单逐个覆盖——一份结构化的契约，喂饱了下游一整条工具链。</p>
<div class="cols">
  <div class="col"><h4>组 = 契约（声明）</h4><p>groups/*.ts，20 个组，全是类型。回答「有什么端点、各要什么」。机器可读 → 生成 SDK。</p></div>
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
<span class="kw">const</span> ref = <span class="st">`err_${crypto.randomUUID().slice(0, 8)}`</span>
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
    <li><strong>组（20 个，groups/）</strong>：声明契约，纯类型，喂养 SDK 生成。</li>
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
    <li><strong>20 个组的名字就是 opencode 的能力地图</strong>——结构化声明让系统永远能自己回答「我有哪些能力」。</li>
    <li>handler 应当<strong>很薄</strong>：输入已被组的类型校验，它只负责「取干净输入 → 调 core → 返回」。<span class="mono">handleRaw</span> 用于需要手控 Response 的少数端点。</li>
    <li><strong>中间件</strong>是套在外圈的横切关卡；错误中间件「真相进日志、编号给客户端」，有类型的失败照常走正路。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Last lesson we stood at the door and saw the server's overall shape: one <span class="mono">webHandler</span>, with <strong>20 route groups</strong> behind it. This lesson we <strong>push the door open</strong> and zoom in on <strong>one group</strong> to see what it's made of. You'll find every opencode API endpoint splits in two: <strong>the "group" declares the contract</strong> (what this endpoint is called, what it wants, what it gives back, how it might fail), and <strong>the "handler" fulfils it</strong> (translating validated input into a call on core). Wrap a ring of <strong>middleware</strong> around them, and the three together make a request's full journey in and out. Grasp this lesson and you can take any API path and find, on your own, where it's declared and where it's implemented.</p>
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
  <div class="node">HttpApi<span class="sub">whole API · 20 groups merged</span></div>
</div>

<h2>20 groups are a map of capabilities</h2>
<p>The <strong>names themselves</strong> of these 20 groups are almost a complete table of contents for everything opencode exposes. You needn't read the implementation; the group names alone tell you most of it:</p>
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
<p>(That lists only 8; the rest include instance, workspace, project, question, pty, sync, control, global and more, making 20 groups — the groups/ dir actually has 21 .ts files, but metadata.ts and query.ts are just helpers, while pty.ts splits into pty and pty-connect.) This is worth pausing on: <strong>when the API is a structured declaration, its "directory" naturally exists and is enumerable</strong>. Want to know what opencode can do? No docs to read, no one to ask — <span class="mono">ls</span> the <span class="mono">groups/</span> directory and the capability list is right there. The Hono style of "routes scattered everywhere" can't give you this — there, no one can say at a glance "what ports does this service open in total." The declarative cost is up-front verbosity; the dividend is that <strong>the system can always answer "what capabilities do I have"</strong> by itself. This "enumerability" propagates downstream too: capabilities enumerable, docs auto-generate, SDKs auto-emit, even tests can cover the list one by one — one structured contract feeds a whole downstream toolchain.</p>
<div class="cols">
  <div class="col"><h4>group = contract (declaration)</h4><p>groups/*.ts, 20 groups, all types. Answers "what endpoints exist, what each wants." Machine-readable → generates SDK.</p></div>
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
<span class="kw">const</span> ref = <span class="st">`err_${crypto.randomUUID().slice(0, 8)}`</span>
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
    <li><strong>groups (20, groups/)</strong>: declare contracts, pure types, feed SDK generation.</li>
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
    <li><strong>The 20 group names are opencode's capability map</strong> — structured declaration lets the system always answer "what capabilities do I have."</li>
    <li>Handlers should be <strong>thin</strong>: input already validated by the group's types, it only "take clean input → call core → return." <span class="mono">handleRaw</span> is for the few endpoints needing manual Response control.</li>
    <li><strong>Middleware</strong> is the cross-cutting checkpoint ring; the error middleware does "truth into the log, an id to the client," while typed failures still take the main road.</li>
  </ul>
</div>
""",
}
LESSON_11 = {
    "zh": r"""
<p class="lead">上一课的 20 个组里，大多数都是「你问一句、我答一句」的一次性买卖：GET 一下拿到会话列表，POST 一下创建会话。但有一个组特别不一样——<span class="mono">event</span>。它只有<strong>一个端点</strong>，可这个端点一旦连上就<strong>不挂断</strong>，而是变成一条<strong>持续往客户端推送</strong>的长河。这一课我们就解剖这条河：服务器内部状态一变（来了新消息、工具开始跑、会话状态变了），怎么<strong>实时</strong>告诉每一个正在看的客户端？答案是 <strong>SSE（Server-Sent Events，服务器推送事件）</strong>，而它的源头，是一条贯穿 core 的<strong>事件总线</strong>。</p>
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
<p class="lead">Of the last lesson's 20 groups, most are one-shot "you ask, I answer" deals: GET the session list, POST to create a session. But one group is special — <span class="mono">event</span>. It has <strong>a single endpoint</strong>, yet once that endpoint connects it <strong>never hangs up</strong>, instead becoming a long river that <strong>continuously pushes to the client</strong>. This lesson dissects that river: when the server's internal state changes (a new message arrives, a tool starts running, a session's status flips), how does it tell every watching client <strong>in real time</strong>? The answer is <strong>SSE (Server-Sent Events)</strong>, and its headwater is an <strong>event bus</strong> running through core.</p>
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
LESSON_12 = {
    "zh": r"""
<p class="lead">第 9 课我们立了一个 flag：opencode 的 API「<strong>自己描述自己，进而自动生成 SDK</strong>」。第 10 课我们看清了这个「自己」是什么——20 个组、每个端点都是一份类型化的契约。这一课，我们终于<strong>兑现那个承诺</strong>：把「类型化的契约」真正变成「能 <span class="mono">import</span> 就用的客户端 SDK」，中间那台机器到底是怎么运转的。一句话剧透：核心只有一个函数 <span class="mono">OpenApi.fromApi(PublicApi)</span>——它读一遍整套 API 的类型，吐出一份标准 OpenAPI 规范；剩下的，就是让一台现成的代码生成器照着规范，把各端 SDK 一行行打印出来。</p>
<p>为什么这件事值得专门花一课？因为它是 opencode「<strong>多端永不漂移</strong>」的终极保证。手写 SDK 的项目，永远在和一个幽灵搏斗：后端改了个字段，前端的类型忘了跟着改，于是某天线上突然 <span class="mono">undefined is not a function</span>。opencode 把这条搏斗线<strong>彻底删除了</strong>——SDK 不是人写的，是从 server 的类型机器生成的。server 一改、SDK 重新生成，类型对不上的地方<strong>编译期当场报错</strong>，根本活不到上线。读懂这一课，你就理解了为什么「契约先行」那点前期繁琐，最后变成了压倒性的工程红利。</p>

<div class="card analogy">
  <div class="tag">🏭 生活类比</div>
  把这套机制想成一座<strong>工厂的「蓝图→说明书」流水线</strong>。工程师手里有一张<strong>主蓝图</strong>（20 个组的类型化 API）——它精确、严谨，但满是只有内部人看得懂的专业符号。第一步，一台<strong>制版机</strong>（<span class="mono">OpenApi.fromApi</span>）扫描整张蓝图，把它翻译成一份<strong>行业标准规格书</strong>（OpenAPI JSON）——从此任何懂这套标准的下游机器都能读它。第二步，一条<strong>装订流水线</strong>（@hey-api 生成器）照着规格书，自动印出一本本<strong>即拿即用的工具手册</strong>（各端 SDK），手册里每个零件的名字、要填的参数、会得到的回执，全和主蓝图一字不差。最妙的是：<strong>改了主蓝图，重跑一遍流水线，所有手册自动更新</strong>。没人需要手抄、没人会抄错。流水线上甚至还有道<strong>质检工序</strong>，专门修掉一个已知的印刷瑕疵——因为再好的机器，也总有那么一两个需要人盯着的角落。
</div>

<h2>第一步：fromApi，把类型读成规范</h2>
<p>整条流水线的「制版机」，是 <span class="mono">server.ts</span> 里一个朴素到不起眼的函数：</p>
<pre class="code"><span class="cm">// server.ts —— 一行，把整套 API 变成 OpenAPI 规范</span>
<span class="kw">export async function</span> <span class="fn">openapi</span>() {
  <span class="kw">return</span> OpenApi.<span class="fn">fromApi</span>(PublicApi)
}</pre>
<p>就这么一行。<span class="mono">PublicApi</span> 是把 20 个组汇总后、再贴上标题/版本/描述注解的那个完整 API 对象（第 10 课的终点）。<span class="mono">OpenApi.fromApi</span> 把它<strong>当数据来读</strong>：遍历每个组、每个端点，把声明里的 params/query/payload/success/error 一一翻译成 OpenAPI 规范里的 paths、schemas、responses。这一步之所以可能，<strong>完全仰仗</strong>前几课那个反复强调的事实——API 是<strong>结构化的类型，而非散落各处的字符串</strong>。机器能遍历类型，却没法遍历你写在 Hono 里的一行行 <span class="mono">app.get("/x", fn)</span>。声明式那点前期繁琐，到这一步连本带利全赚了回来。</p>
<p>停下来体会一下这件事有多不寻常：<strong>你写的类型，被当成可以遍历、可以转换的「数据」用了</strong>。在很多语言里，类型是编译期一写完就蒸发的影子，运行时啥也不剩。而在这里，整套 API 的类型不仅活到了运行时，还被一个函数<strong>逐字读出来、翻译成另一种格式</strong>。这正是 opencode 选择「声明式 HttpApi」最深的回报：当契约是数据，它就能被无限次地<strong>投影</strong>成别的东西——今天投影成 OpenAPI 规范喂 SDK，明天可以投影成校验器、投影成 mock server、投影成测试桩。一次声明，处处复用，靠的就是「类型即数据」这个支点。</p>
<div class="flow">
  <div class="node">PublicApi<span class="sub">20 组·类型化契约</span></div>
  <div class="arrow">fromApi →</div>
  <div class="node">OpenAPI 规范<span class="sub">标准 JSON·机器可读</span></div>
  <div class="arrow">@hey-api →</div>
  <div class="node">各端 SDK<span class="sub">即拿即用·类型对齐</span></div>
</div>
<p>注意源码里有个小细节：<span class="mono">OpenApi.fromApi</span> 被注释为「非平凡（non-trivial）」，所以 <span class="mono">/doc</span> 那个返回规范的端点是<strong>惰性</strong>的——真有人来访问才计算，不白白占启动时间。一个「把整套 API 翻成规范」的操作不便宜，这个惰性处理也再次呼应了 opencode 处处可见的工程克制。</p>

<h2>第二步：generate，给规范加点料</h2>
<p>有了 <span class="mono">Server.openapi()</span>，<span class="mono">opencode generate</span> 这个 CLI 命令（<span class="mono">cli/cmd/generate.ts</span>）就把规范<strong>打磨成最终交付物</strong>，写到标准输出。它不只是「打印 JSON」，还顺手做了两件贴心事。其一，<strong>给每个端点注入一段示例代码</strong>（<span class="mono">x-codeSamples</span>）：</p>
<pre class="code"><span class="cm">// cli/cmd/generate.ts —— 给每个 operation 塞一段 JS 用法示例</span>
operation[<span class="st">"x-codeSamples"</span>] = [{
  lang: <span class="st">"js"</span>,
  source: [
    <span class="st">`import { createOpencodeClient } from "@opencode-ai/sdk"`</span>,
    <span class="st">`const client = createOpencodeClient()`</span>,
    <span class="st">`await client.${operation.operationId}({ ... })`</span>,
  ].<span class="fn">join</span>(<span class="st">"\n"</span>),
}]</pre>
<p>于是生成出来的 API 文档里，每个端点旁边都自带一段「这样调用我」的复制即用代码——文档不再是干巴巴的字段表，而是<strong>能直接照抄的活例子</strong>。其二，整份 JSON <strong>过一遍 prettier 格式化</strong>，确保无论谁在什么机器上跑，产出的文件都<strong>逐字节一致</strong>。这个「可复现」的执念很关键：因为生成物是<strong>要提交进仓库</strong>的，只有逐字节稳定，代码评审里才不会冒出一堆无意义的格式 diff。</p>
<p>这两件「顺手事」其实都不小。<span class="mono">x-codeSamples</span> 体现的是一种态度：<strong>文档不该只告诉你「有什么」，还该告诉你「怎么用」</strong>。一个只列字段名的接口文档，读者还得自己拼调用代码；而带了示例的文档，复制粘贴就能跑——而且因为示例也是从 <span class="mono">operationId</span> 自动拼的，它永远和真实接口同步，不会像手写示例那样过几个月就过期。至于 prettier 那道格式化，看似洁癖，背后是对「<strong>生成物入库</strong>」这个决定的认真负责：既然要把机器产物当源码提交，就得让它在任何环境下都稳定复现，否则每次有人重跑生成，diff 里全是空格和换行的噪声，真正的改动反而被淹没。</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">build.ts 跑 `bun dev generate` &gt; openapi.json —— 拿到规范</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">createClient({ input: openapi.json, output: src/v2/gen, plugins: [...] })</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">@hey-api 照规范生成 types.gen / sdk.gen / client.gen 三个文件</span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">质检工序：补丁修掉一个已知的 hey-api 代码生成 bug</span></div>
  <div class="t-row"><span class="t-num">5</span><span class="t-txt">生成物提交进仓库 —— 客户端 import 即用</span></div>
</div>

<h2>第三步：@hey-api，规范变 SDK</h2>
<p>真正把规范「印成」TypeScript SDK 的，是 <span class="mono">packages/sdk/js/script/build.ts</span> 里调用的开源生成器 <span class="mono">@hey-api/openapi-ts</span>。它读入 <span class="mono">openapi.json</span>，按配置里挂的几个插件，分工产出三个文件：</p>
<div class="cellgroup">
  <div class="cell"><div class="k">@hey-api/typescript</div><div class="v">→ types.gen.ts：把规范里的 schema 全变成 TS 类型</div></div>
  <div class="cell"><div class="k">@hey-api/sdk</div><div class="v">→ sdk.gen.ts：OpencodeClient，每个端点一个方法</div></div>
  <div class="cell"><div class="k">@hey-api/client-fetch</div><div class="v">→ client.gen.ts：底层 fetch 客户端，默认指向 localhost:4096</div></div>
</div>
<p>三者合起来，就是你 <span class="mono">import { createOpencodeClient }</span> 之后拿到的那个对象。<span class="mono">client.session.list()</span> 这样的调用，方法名来自端点的 <span class="mono">operationId</span>，参数和返回类型来自规范里的 schema——<strong>全程没有一行是人手写的</strong>。这也解释了第 10 课那句「端点名错一个、编译期就报错」的下游意义：端点名最终变成了 SDK 的方法名，契约从 server 一路<strong>类型安全地</strong>贯通到了客户端的每一次调用。</p>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">上</span><span class="name">types.gen.ts</span></div><div class="ld">所有数据形状的 TS 类型，贯穿其余两层</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">中</span><span class="name">sdk.gen.ts · OpencodeClient</span></div><div class="ld">每个端点一个方法，方法名=operationId</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">下</span><span class="name">client.gen.ts · fetch</span></div><div class="ld">底层 HTTP 客户端，真正发请求</div></div>
</div>
<p>这三层的分工，本身就是一份很好的「关注点分离」范本：最底层只管<strong>怎么发请求</strong>（fetch、baseUrl），中间层只管<strong>有哪些方法、各对应哪个端点</strong>，最上层的类型则像一条线，把前两层的输入输出全<strong>缝</strong>到一起。你调 <span class="mono">client.session.get(...)</span> 时，编译器顺着这条线，一路替你核对参数对不对、返回能不能那么用——而这一切的源头，仍然是 server 里那份类型声明。</p>
<div class="cols">
  <div class="col"><h4>手写 SDK（别的项目）</h4><p>后端改字段 → 得记得手动改前端类型 → 忘了就漂移 → 某天线上炸。人肉维持一致，迟早出错。</p></div>
  <div class="col"><h4>生成 SDK（opencode）</h4><p>后端改类型 → 重跑生成 → SDK 自动更新 → 对不上当场编译报错。一致性由机器保证。</p></div>
</div>
<p>「漂移」这个词值得多说一句，因为它是几乎每个前后端分离项目都踩过的坑。手写 SDK 的世界里，后端和前端的类型是<strong>两份各自维护的副本</strong>：理论上它们该一模一样，实际上只要有人改了一处、忘了同步另一处，两份副本就开始悄悄分叉。可怕的是，这种分叉<strong>编译期毫无察觉</strong>——前端代码自己内部是自洽的，只有真到运行时、真发出那个请求，才发现后端早就不认这个字段了。opencode 用生成 SDK 把这个问题<strong>从根上消灭</strong>：前后端的类型不再是两份副本，而是<strong>同一个源头的两次投影</strong>。源头一动，两边一起动；源头要是和某处用法对不上，TypeScript 编译当场就拦下来。把一个「运行时才暴露、且高度依赖人记性」的隐患，换成了一个「编译期必现、且无需任何人操心」的保证——这就是这套流水线最值钱的地方。</p>

<h2>诚实的角落：清洗与补丁</h2>
<p>到这里你可能觉得这套流水线完美得像魔法。但真实的工程从不是魔法——它在两个地方留下了<strong>诚实的、需要人盯着的角落</strong>，恰恰是这两处，最能让你看清「自动生成」的真实质地。第一处是<strong>规范清洗</strong>。Effect 的 Schema 翻成 OpenAPI 时，会留下一些「翻译腔」：比如 <span class="mono">Schema.optional</span> 会在联合类型里塞进一个 <span class="mono">{type:"null"}</span> 的孤儿分支。<span class="mono">public.ts</span> 里专门有个 <span class="mono">stripOptionalNull</span> 把这些孤儿一一剥掉，还有一段逻辑处理自引用 schema——这些都是为了让交给下游的规范<strong>干净、标准、无歧义</strong>。</p>
<p>第二处更耐人寻味：build.ts 末尾有一道<strong>打补丁</strong>工序，专门修 <span class="mono">@hey-api</span> 自己的一个代码生成 bug——它在生成 SSE 相关类型时，错把端点的 <span class="mono">TError</span> 塞进了异步生成器 <span class="mono">TReturn</span> 的位置。opencode 的做法不是 fork 整个生成器，而是<strong>生成完之后，精准地改那一处字符串</strong>。源码里那段补丁注释写得清清楚楚：哪个 bug、为什么错、怎么修。这两个角落传递的信息是一致的：<strong>「自动生成」不等于「无人值守」</strong>。它把 99% 的机械活交给机器，但那剩下 1% 的毛刺，仍需要人用最克制的方式——清洗输入、修补输出——亲手抹平。</p>
<div class="cellgroup">
  <div class="cell"><div class="k">输入侧·清洗</div><div class="v">stripOptionalNull 等：剥掉 Effect→OpenAPI 的翻译腔，给下游干净规范</div></div>
  <div class="cell"><div class="k">输出侧·补丁</div><div class="v">改掉 @hey-api 一个已知 bug：精准改字符串，而非 fork 生成器</div></div>
</div>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <p>这一课把第 9–12 课串成了一个<strong>闭环</strong>，也是整个第三部分的高潮：</p>
  <ul>
    <li><strong>第 10 课</strong>：用类型把 20 个组的契约声明出来（结构化、机器可读）。</li>
    <li><strong>第 12 课·这一课</strong>：<span class="mono">fromApi</span> 把类型读成 OpenAPI 规范 → generate 加料/格式化 → @hey-api 印成 SDK → 提交入库。</li>
    <li><strong>结果</strong>：客户端 <span class="mono">import</span> 即用，类型从 server 到调用点全程对齐，<strong>永不漂移</strong>。</li>
  </ul>
  <p>「单一事实来源（single source of truth）」这个被说滥的词，在这里有了最具体的样子：<strong>server 的类型，就是唯一的真相</strong>；文档、SDK、示例代码全是它的自动投影。换个角度看，这也是一种「<strong>责任的收口</strong>」：维护一致性的担子，从「每个写客户端的人都得记得跟上后端」，收拢成了「只要后端类型对，下游自动全对」。一个人改对一处，胜过十个人分头记得改十处。下一课我们看这套生成出来的 SDK，怎么被富 TUI 用一种「零网络」的奇特方式调用。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p>整条流水线的「装订机」配置，浓缩在 build.ts 这几行里：</p>
  <pre class="code"><span class="cm">// packages/sdk/js/script/build.ts</span>
<span class="kw">await</span> $<span class="st">`bun dev generate &gt; ${dir}/openapi.json`</span>.<span class="fn">cwd</span>(opencode)  <span class="cm">// 先 dump 规范</span>

<span class="kw">await</span> <span class="fn">createClient</span>({
  input: <span class="st">"./openapi.json"</span>,
  output: { path: <span class="st">"./src/v2/gen"</span>, clean: <span class="kw">true</span> },
  plugins: [
    { name: <span class="st">"@hey-api/typescript"</span> },               <span class="cm">// → types.gen.ts</span>
    { name: <span class="st">"@hey-api/sdk"</span>, instance: <span class="st">"OpencodeClient"</span> }, <span class="cm">// → sdk.gen.ts</span>
    { name: <span class="st">"@hey-api/client-fetch"</span>, baseUrl: <span class="st">"http://localhost:4096"</span> },
  ],
})</pre>
  <p><span class="mono">clean: true</span> 意味着每次生成都把旧目录清空重写——产物是<strong>纯函数式</strong>的：同一份规范，永远生成同一套文件。这就是为什么生成物可以放心提交进仓库：它不是「手工成果」，而是「输入的确定性投影」，谁来跑都一样。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li>SDK 生成的核心是 <span class="mono">OpenApi.fromApi(PublicApi)</span>：把 20 个组的<strong>类型</strong>读成一份标准 OpenAPI 规范——这一步只因 API 是结构化类型才可能。</li>
    <li><span class="mono">opencode generate</span> 给规范<strong>注入示例代码</strong>（x-codeSamples）并 <strong>prettier 格式化</strong>，保证产出逐字节可复现、可入库。</li>
    <li><span class="mono">@hey-api/openapi-ts</span> 按三个插件把规范印成 <strong>types.gen / sdk.gen / client.gen</strong>：类型、OpencodeClient 方法、fetch 客户端。</li>
    <li>端点名 → SDK 方法名，契约从 server <strong>类型安全地</strong>贯通到客户端每次调用；<strong>永不漂移</strong>，对不上当场编译报错。</li>
    <li>自动生成<strong>不等于无人值守</strong>：输入侧 <span class="mono">stripOptionalNull</span> 清洗翻译腔，输出侧精准打补丁修 @hey-api 的已知 bug。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">In Lesson 9 we planted a flag: opencode's API "<strong>describes itself, and so auto-generates an SDK</strong>." In Lesson 10 we saw what that "itself" is — 20 groups, each endpoint a typed contract. This lesson finally <strong>cashes that promise</strong>: how the machine that turns "typed contracts" into "an importable client SDK" actually runs. One-line spoiler: the core is a single function <span class="mono">OpenApi.fromApi(PublicApi)</span> — it reads the whole API's types once and emits a standard OpenAPI spec; the rest is letting an off-the-shelf code generator print each client's SDK line by line from that spec.</p>
<p>Why does this deserve a whole lesson? Because it's the ultimate guarantee of opencode's <strong>never-drifting multi-client consistency</strong>. Projects with a hand-written SDK forever fight a ghost: the backend changes a field, the frontend's type forgets to follow, and one day production throws <span class="mono">undefined is not a function</span>. opencode <strong>deletes this fight entirely</strong> — the SDK isn't written by a person, it's generated from the server's types. Change the server, regenerate the SDK, and any mismatch <strong>fails at compile time on the spot</strong>, never living to reach production. Grasp this lesson and you understand why that bit of "contract-first" up-front tedium turns into an overwhelming engineering dividend.</p>

<div class="card analogy">
  <div class="tag">🏭 Analogy</div>
  Think of this as a factory's <strong>"blueprint → manual" assembly line</strong>. The engineer holds a <strong>master blueprint</strong> (the typed API of 20 groups) — precise and rigorous, but full of professional symbols only insiders read. Step one, a <strong>platemaker</strong> (<span class="mono">OpenApi.fromApi</span>) scans the whole blueprint and translates it into an <strong>industry-standard spec sheet</strong> (OpenAPI JSON) — now any downstream machine that knows the standard can read it. Step two, a <strong>binding line</strong> (the @hey-api generator) follows the spec sheet and auto-prints <strong>ready-to-use toolkit manuals</strong> (each client's SDK), where every part's name, the params to fill, the receipt you'll get, all match the master blueprint to the letter. Best of all: <strong>change the master blueprint, rerun the line, and every manual updates automatically</strong>. No one transcribes, no one mistranscribes. The line even has a <strong>QA station</strong> that fixes one known misprint — because even the best machine always has a corner or two needing a human's eye.
</div>

<h2>Step 1: fromApi, reading types into a spec</h2>
<p>The whole line's "platemaker" is a function in <span class="mono">server.ts</span> so plain it's unremarkable:</p>
<pre class="code"><span class="cm">// server.ts — one line turns the whole API into an OpenAPI spec</span>
<span class="kw">export async function</span> <span class="fn">openapi</span>() {
  <span class="kw">return</span> OpenApi.<span class="fn">fromApi</span>(PublicApi)
}</pre>
<p>Just that one line. <span class="mono">PublicApi</span> is the complete API object after merging the 20 groups and tagging on title/version/description annotations (Lesson 10's endpoint). <span class="mono">OpenApi.fromApi</span> <strong>reads it as data</strong>: it walks each group and endpoint, translating the declared params/query/payload/success/error into the spec's paths, schemas, responses. This step is possible <strong>entirely thanks to</strong> the fact the past lessons kept stressing — the API is <strong>structured types, not strings scattered everywhere</strong>. A machine can walk types; it cannot walk your line-by-line <span class="mono">app.get("/x", fn)</span> in Hono. The declarative style's up-front tedium is repaid here with interest.</p>
<div class="flow">
  <div class="node">PublicApi<span class="sub">20 groups · typed contracts</span></div>
  <div class="arrow">fromApi →</div>
  <div class="node">OpenAPI spec<span class="sub">standard JSON · machine-readable</span></div>
  <div class="arrow">@hey-api →</div>
  <div class="node">each client's SDK<span class="sub">ready-to-use · type-aligned</span></div>
</div>
<p>Pause to feel how unusual this is: <strong>the types you wrote are used as "data" that can be walked and transformed</strong>. In many languages, a type is a shadow that evaporates once compilation ends, leaving nothing at runtime. Here, the whole API's types not only live to runtime but are <strong>read out verbatim by a function and translated into another format</strong>. This is the deepest payoff of opencode choosing "declarative HttpApi": when the contract is data, it can be <strong>projected</strong> endlessly into other things — today into an OpenAPI spec to feed the SDK, tomorrow into a validator, a mock server, a test stub. Declare once, reuse everywhere, all pivoting on "types as data."</p>
<p>Note a small detail in the source: <span class="mono">OpenApi.fromApi</span> is commented as "non-trivial," so the <span class="mono">/doc</span> endpoint that returns the spec is <strong>lazy</strong> — computed only when someone actually hits it, not wasting startup time. An operation that "translates the whole API into a spec" isn't cheap, and this lazy handling echoes the engineering restraint visible all over opencode.</p>

<h2>Step 2: generate, seasoning the spec</h2>
<p>With <span class="mono">Server.openapi()</span> in hand, the <span class="mono">opencode generate</span> CLI command (<span class="mono">cli/cmd/generate.ts</span>) <strong>polishes the spec into the final deliverable</strong> and writes it to stdout. It doesn't just "print JSON"; it also does two thoughtful things. First, <strong>inject a code sample into each endpoint</strong> (<span class="mono">x-codeSamples</span>):</p>
<pre class="code"><span class="cm">// cli/cmd/generate.ts — inject a JS usage sample into each operation</span>
operation[<span class="st">"x-codeSamples"</span>] = [{
  lang: <span class="st">"js"</span>,
  source: [
    <span class="st">`import { createOpencodeClient } from "@opencode-ai/sdk"`</span>,
    <span class="st">`const client = createOpencodeClient()`</span>,
    <span class="st">`await client.${operation.operationId}({ ... })`</span>,
  ].<span class="fn">join</span>(<span class="st">"\n"</span>),
}]</pre>
<p>So in the generated API docs, each endpoint comes with a copy-and-run snippet of "call me like this" — the docs are no longer a dry field table but <strong>a live example you can copy verbatim</strong>. Second, the whole JSON <strong>passes through prettier formatting</strong>, ensuring that whoever runs it on whatever machine, the output file is <strong>byte-identical</strong>. This "reproducibility" obsession matters: because the artifact is <strong>committed into the repo</strong>, only byte-stability keeps code review free of meaningless formatting diffs.</p>
<p>Both "side errands" are actually big. <span class="mono">x-codeSamples</span> reflects an attitude: <strong>docs shouldn't only tell you "what exists" but also "how to use it."</strong> An interface doc that only lists field names leaves the reader to assemble the call themselves; a doc with examples runs on copy-paste — and because the example is auto-assembled from <span class="mono">operationId</span>, it's forever in sync with the real interface, never going stale like a hand-written sample after a few months. As for the prettier pass, seemingly fussy, it's a serious commitment to the decision of "committing the artifact": if a machine product is committed as source, it must reproduce stably in any environment, or every regeneration buries the real change under a flood of whitespace-and-newline noise.</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">build.ts runs `bun dev generate` &gt; openapi.json — get the spec</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">createClient({ input: openapi.json, output: src/v2/gen, plugins: [...] })</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">@hey-api generates types.gen / sdk.gen / client.gen from the spec</span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">QA station: a patch fixes a known @hey-api codegen bug</span></div>
  <div class="t-row"><span class="t-num">5</span><span class="t-txt">artifact committed into the repo — clients import and use it</span></div>
</div>

<h2>Step 3: @hey-api, spec becomes SDK</h2>
<p>What actually "prints" the spec into a TypeScript SDK is the open-source generator <span class="mono">@hey-api/openapi-ts</span>, invoked in <span class="mono">packages/sdk/js/script/build.ts</span>. It reads <span class="mono">openapi.json</span> and, per the plugins hung in its config, produces three files by division of labor:</p>
<div class="cellgroup">
  <div class="cell"><div class="k">@hey-api/typescript</div><div class="v">→ types.gen.ts: turns every schema in the spec into TS types</div></div>
  <div class="cell"><div class="k">@hey-api/sdk</div><div class="v">→ sdk.gen.ts: OpencodeClient, one method per endpoint</div></div>
  <div class="cell"><div class="k">@hey-api/client-fetch</div><div class="v">→ client.gen.ts: the low-level fetch client, defaulting to localhost:4096</div></div>
</div>
<p>The three together are the object you get after <span class="mono">import { createOpencodeClient }</span>. A call like <span class="mono">client.session.list()</span> takes its method name from the endpoint's <span class="mono">operationId</span>, its param and return types from the spec's schemas — <strong>not one line hand-written anywhere</strong>. This also explains the downstream meaning of Lesson 10's "misspell one endpoint name and the compiler complains": endpoint names become SDK method names, and the contract runs <strong>type-safely</strong> all the way from the server to every client call.</p>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">top</span><span class="name">types.gen.ts</span></div><div class="ld">TS types for all data shapes, threading through the other two</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">mid</span><span class="name">sdk.gen.ts · OpencodeClient</span></div><div class="ld">one method per endpoint, method name = operationId</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">low</span><span class="name">client.gen.ts · fetch</span></div><div class="ld">the low-level HTTP client that actually sends requests</div></div>
</div>
<p>This three-layer split is itself a fine model of "separation of concerns": the bottom only cares <strong>how to send the request</strong> (fetch, baseUrl), the middle only cares <strong>what methods exist and which endpoint each maps to</strong>, and the top types are like a thread <strong>stitching</strong> the inputs and outputs of the first two together. When you call <span class="mono">client.session.get(...)</span>, the compiler follows this thread, checking for you whether the params are right and whether the return can be used that way — and the source of it all is still that type declaration in the server.</p>
<div class="cols">
  <div class="col"><h4>Hand-written SDK (other projects)</h4><p>backend changes a field → must remember to hand-edit the frontend type → forget and it drifts → one day it blows up in prod. Hand-kept consistency errs sooner or later.</p></div>
  <div class="col"><h4>Generated SDK (opencode)</h4><p>backend changes types → regenerate → SDK auto-updates → mismatch fails compile on the spot. Consistency guaranteed by machine.</p></div>
</div>
<p>"Drift" deserves a few more words, because it's a pit nearly every split frontend/backend project has fallen into. In the hand-written-SDK world, the backend's and frontend's types are <strong>two separately-maintained copies</strong>: in theory identical, in practice the moment someone edits one and forgets to sync the other, the two copies quietly fork. The scary part is this fork is <strong>invisible at compile time</strong> — the frontend code is internally self-consistent; only at runtime, only when that request actually fires, do you discover the backend stopped recognizing the field long ago. opencode's generated SDK <strong>eliminates this at the root</strong>: the two sides' types are no longer two copies but <strong>two projections of the same source</strong>. Move the source and both move; if the source mismatches some usage, TypeScript stops it at compile time on the spot. It swaps a "runtime-only, memory-dependent" hazard for a "compile-time-certain, zero-attention-needed" guarantee — and that's this line's most valuable trait.</p>

<h2>The honest corners: cleaning and patching</h2>
<p>By now this line may seem flawless, like magic. But real engineering is never magic — it leaves <strong>honest corners that need a human's eye</strong> in two places, and it's precisely these two that show you the true texture of "auto-generation." The first is <strong>spec cleaning</strong>. When Effect's Schema translates to OpenAPI, it leaves a "translation accent": e.g. <span class="mono">Schema.optional</span> stuffs an orphan <span class="mono">{type:"null"}</span> arm into a union type. <span class="mono">public.ts</span> has a dedicated <span class="mono">stripOptionalNull</span> to peel these orphans off one by one, plus logic handling self-referencing schemas — all to make the spec handed downstream <strong>clean, standard, unambiguous</strong>.</p>
<p>The second is more telling: build.ts ends with a <strong>patching</strong> step that fixes a codegen bug in <span class="mono">@hey-api</span> itself — when generating SSE-related types, it wrongly stuffs the endpoint's <span class="mono">TError</span> into the async generator's <span class="mono">TReturn</span> slot. opencode's approach is not to fork the whole generator but to <strong>precisely edit that one string after generation</strong>. The patch comment in the source spells it out: which bug, why wrong, how fixed. Both corners convey the same message: <strong>"auto-generation" doesn't mean "unattended."</strong> It hands 99% of the mechanical work to the machine, but the remaining 1% of burrs still needs a human to smooth by the most restrained means — clean the input, patch the output — by hand.</p>
<div class="cellgroup">
  <div class="cell"><div class="k">input side · cleaning</div><div class="v">stripOptionalNull etc.: peel off the Effect→OpenAPI accent, hand downstream a clean spec</div></div>
  <div class="cell"><div class="k">output side · patching</div><div class="v">fix a known @hey-api bug: precisely edit a string, not fork the generator</div></div>
</div>

<div class="card macro">
  <div class="tag">🗺️ The big picture</div>
  <p>This lesson ties Lessons 9–12 into a <strong>closed loop</strong>, the climax of all of Part 3:</p>
  <ul>
    <li><strong>Lesson 10</strong>: declare the 20 groups' contracts in types (structured, machine-readable).</li>
    <li><strong>Lesson 12 · this one</strong>: <span class="mono">fromApi</span> reads the types into an OpenAPI spec → generate seasons/formats → @hey-api prints the SDK → committed to the repo.</li>
    <li><strong>Result</strong>: clients <span class="mono">import</span> and use it, types aligned from server to call site, <strong>never drifting</strong>.</li>
  </ul>
  <p>"Single source of truth," that over-used phrase, gets its most concrete form here: <strong>the server's types are the only truth</strong>; docs, SDK, code samples are all its automatic projections. Seen another way, it's a "<strong>consolidation of responsibility</strong>": the burden of maintaining consistency shrinks from "every client author must remember to keep up with the backend" to "as long as the backend types are right, downstream is automatically right." One person fixing one place beats ten people each remembering to fix ten places. Next lesson we see how this generated SDK is called by the rich TUI in a peculiar "zero-network" way.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source detail</div>
  <p>The whole line's "binder" config is condensed in these lines of build.ts:</p>
  <pre class="code"><span class="cm">// packages/sdk/js/script/build.ts</span>
<span class="kw">await</span> $<span class="st">`bun dev generate &gt; ${dir}/openapi.json`</span>.<span class="fn">cwd</span>(opencode)  <span class="cm">// dump the spec first</span>

<span class="kw">await</span> <span class="fn">createClient</span>({
  input: <span class="st">"./openapi.json"</span>,
  output: { path: <span class="st">"./src/v2/gen"</span>, clean: <span class="kw">true</span> },
  plugins: [
    { name: <span class="st">"@hey-api/typescript"</span> },               <span class="cm">// → types.gen.ts</span>
    { name: <span class="st">"@hey-api/sdk"</span>, instance: <span class="st">"OpencodeClient"</span> }, <span class="cm">// → sdk.gen.ts</span>
    { name: <span class="st">"@hey-api/client-fetch"</span>, baseUrl: <span class="st">"http://localhost:4096"</span> },
  ],
})</pre>
  <p><span class="mono">clean: true</span> means every generation wipes and rewrites the old directory — the artifact is <strong>purely functional</strong>: the same spec always generates the same set of files. That's why the artifact can be committed without worry: it isn't "handcraft" but "a deterministic projection of the input," identical no matter who runs it.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key points</div>
  <ul>
    <li>The core of SDK generation is <span class="mono">OpenApi.fromApi(PublicApi)</span>: it reads the 20 groups' <strong>types</strong> into a standard OpenAPI spec — possible only because the API is structured types.</li>
    <li><span class="mono">opencode generate</span> <strong>injects code samples</strong> (x-codeSamples) into the spec and <strong>prettier-formats</strong> it, ensuring byte-reproducible, committable output.</li>
    <li><span class="mono">@hey-api/openapi-ts</span> prints the spec into <strong>types.gen / sdk.gen / client.gen</strong> via three plugins: types, OpencodeClient methods, fetch client.</li>
    <li>Endpoint name → SDK method name; the contract runs <strong>type-safely</strong> from server to every client call; <strong>never drifts</strong>, mismatch fails compile on the spot.</li>
    <li>Auto-generation <strong>isn't unattended</strong>: the input side <span class="mono">stripOptionalNull</span> cleans the translation accent, the output side precisely patches a known @hey-api bug.</li>
  </ul>
</div>
""",
}
LESSON_13 = {
    "zh": r"""
<p class="lead">第 9 课我们埋了一个伏笔：server 对外只是一个 <span class="mono">(request) =&gt; Response</span> 的函数，「正因为这么标准，它既能架在网络服务器上，也能塞进进程内 worker 直接调」。第 12 课又给了我们一把<strong>以 <span class="mono">fetch</span> 为参数</strong>的 SDK。这一课，是第三部分的<strong>收官与高潮</strong>：我们把这两块拼在一起，亲眼看富 TUI 怎么用<strong>零网络</strong>的方式，调用那个和网页端<strong>一模一样</strong>的 server。谜底就藏在一个函数里——<span class="mono">createWorkerFetch</span>，它造出一个长得和标准 <span class="mono">fetch</span> 分毫不差、却根本不碰网络的「假 fetch」。</p>
<p>为什么这是整个第三部分的题眼？因为它把前面所有的伏笔一次性收拢：server 是纯函数（第 9 课）、SDK 吃一个 <span class="mono">fetch</span>（第 12 课）、事件靠 SSE 流（第 11 课）——这三件事拼起来，就得到一个惊人的结论：<strong>同一套业务逻辑、同一套 SDK，传输层可以随意热插拔</strong>。换个 <span class="mono">fetch</span>，TUI 就从「网络客户端」变成了「进程内客户端」，而 server 和 SDK<strong>一个字都不用改</strong>。这正是第 6 课「实现可整体替换」那条原则，在整个系统最外层的终极兑现。</p>

<div class="card analogy">
  <div class="tag">🏨 生活类比</div>
  还记得第 9 课那家酒店的总服务台吗？总台只会干一件事：<strong>收一张点单、办成一件事、递回一张回执</strong>——它根本不关心这张点单是<strong>怎么</strong>送到它面前的。一位住在楼里的客人（富 TUI），不必跑到大门外用公用电话打进来，而是直接走到台前、或用楼内的<strong>气动传送管</strong>把单子「嗖」地送到台上——这就是 <span class="mono">createWorkerFetch</span>：楼内直送，不出大楼、不碰电话网。而一位外地客人（网页/桌面端），只能<strong>打电话</strong>进来（真正的网络 HTTP）。两位客人，<strong>同一个总台、同一张服务清单、同一本对客手册</strong>（SDK），唯一的差别只是「单子怎么送到台前」。把「送单方式」抽象成一个可替换的零件，同一个总台就能同时服务楼内楼外——这就是这一课的全部魔法。
</div>

<h2>缝在哪里：fetch 这道接缝</h2>
<p>要理解传输能热插拔，先得看清「接缝」开在哪。回顾两个事实：server 是 <span class="mono">app.fetch(request)</span>——进一个 <span class="mono">Request</span>、出一个 <span class="mono">Response</span>；而 SDK 在第 12 课里是用 <span class="mono">@hey-api/client-fetch</span> 生成的，它内部<strong>所有的网络调用，都通过一个可配置的 <span class="mono">fetch</span> 函数</strong>发出去。两头都以 <span class="mono">fetch</span> 这个标准形态为界面——<strong>这就是那道接缝</strong>。只要你能提供一个「形状是 <span class="mono">fetch</span>、但内部爱干嘛干嘛」的函数，就能把 SDK 的请求<strong>导向任何你想要的地方</strong>。</p>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">调用</span><span class="name">client.session.list()</span></div><div class="ld">SDK 方法（第 12 课生成）</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">接缝</span><span class="name">fetch(request) =&gt; Response</span></div><div class="ld">★ 可替换的那道缝 ★</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">传输</span><span class="name">真 fetch ╱ createWorkerFetch</span></div><div class="ld">网络 HTTP，或进程内 RPC</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">处理</span><span class="name">app.fetch(request)</span></div><div class="ld">同一个 webHandler（第 9 课）</div></div>
</div>
<p>看清这张图，整一课就通了七成：最上和最下两层是<strong>雷打不动</strong>的——SDK 方法不变、server 处理器不变。能换的只有中间那层<strong>「传输」</strong>。网页端往这层填真正的 <span class="mono">fetch</span>，请求就走网络；富 TUI 往这层填 <span class="mono">createWorkerFetch</span>，请求就走进程内。<strong>接缝以上、接缝以下都原封不动，只把接缝处插的零件一换</strong>，传输方式就彻底变了。这就是「面向接口、而非面向实现」最干净利落的一次实战。</p>
<p>这道接缝之所以能开得这么干净，靠的是一个常被低估的设计眼光：<strong>选一个「窄到极致、却又标准到极致」的边界</strong>。<span class="mono">fetch</span> 的形态简单得只剩「进 Request、出 Response」——正因为窄，任何人都能轻松实现一个；又因为它是 Web 标准，SDK、浏览器、运行时早就都认它。假如当初 server 对外暴露的是一个臃肿的、带几十个方法的客户端接口，想换传输就得把那几十个方法全重写一遍；而压缩成单一的 <span class="mono">fetch</span>，换传输就只剩「实现一个函数」。<strong>边界越窄，可替换性越强</strong>——这是贯穿 opencode 的审美，在这一课被推到了极致。</p>

<h2>传输 A：真 fetch，走网络</h2>
<p>这条路最直白，也是大多数客户端走的路。网页端、桌面端、远程连接的客户端，离 server 进程<strong>有真正的距离</strong>——它们和 server 之间隔着一条真实的网络。于是 SDK 里填的就是浏览器/运行时<strong>原生的那个 <span class="mono">fetch</span></strong>：请求被序列化成 HTTP 报文，经 TCP 发到 server 监听的端口（默认 4096），server 的 <span class="mono">NodeHttpServer</span> 收下、交给 webHandler 处理，再把 <span class="mono">Response</span> 序列化回来。一切都是标准的 HTTP，没有任何花招。这条路的好处是<strong>通用</strong>：任何能发 HTTP 的东西都能当 opencode 的客户端。代价是<strong>有网络开销</strong>：序列化、TCP、反序列化，每一跳都要钱。</p>
<div class="cols">
  <div class="col"><h4>传输 A · 网络 fetch</h4><p>真 fetch → HTTP/TCP → 端口 4096。<strong>通用</strong>：浏览器、桌面、远程都能连。<strong>代价</strong>：序列化 + 网络往返。</p></div>
  <div class="col"><h4>传输 B · worker fetch</h4><p>createWorkerFetch → RPC → 隔壁线程。<strong>极快</strong>：零网络、零序列化成 HTTP。<strong>限制</strong>：只适用于同进程的富 TUI。</p></div>
</div>

<h2>传输 B：createWorkerFetch，零网络</h2>
<p>富 TUI 的处境完全不同：它和 server <strong>跑在同一个进程里</strong>——只不过分在两个线程。主线程负责画界面（要快、要跟手），server 的重活（调模型、跑工具）则被放进一个 <strong>Worker 线程</strong>。两个线程之间，隔的不是网络，而是一条进程内的消息通道。既然 server 就在隔壁线程，何必把请求序列化成 HTTP、绕一圈网络再回来？<span class="mono">createWorkerFetch</span> 就是来抄这条近路的：</p>
<pre class="code"><span class="cm">// 简化自 cli/cmd/tui.ts —— 一个长得像 fetch、却走 RPC 的函数</span>
<span class="kw">function</span> <span class="fn">createWorkerFetch</span>(client: RpcClient): <span class="kw">typeof</span> fetch {
  <span class="kw">const</span> fn = <span class="kw">async</span> (input, init) =&gt; {
    <span class="kw">const</span> result = <span class="kw">await</span> client.<span class="fn">call</span>(<span class="st">"fetch"</span>, {  <span class="cm">// ← RPC 到 worker，不走网络</span>
      url: ..., method: ..., headers: ..., body: ...,
    })
    <span class="kw">return new</span> <span class="fn">Response</span>(result.body, { status: result.status, ... })
  }
  <span class="kw">return</span> fn <span class="kw">as typeof</span> fetch  <span class="cm">// ← 对外伪装成标准 fetch</span>
}</pre>
<p>看它的两端：<strong>对外</strong>，它的签名被断言成 <span class="mono">typeof fetch</span>——在 SDK 眼里，它和真 <span class="mono">fetch</span> 没有任何区别，SDK 浑然不觉自己其实没在上网。<strong>对内</strong>，它没有发任何 HTTP，而是把请求的四要素（url/method/headers/body）打包，通过 <span class="mono">client.call("fetch", ...)</span> 用 RPC 发给 Worker 线程，再把 worker 回传的 <span class="mono">{status, headers, body}</span> <strong>重新拼成一个 <span class="mono">Response</span></strong> 交还给 SDK。一进一出，形态和真 fetch 一模一样，中间却没碰一下网卡。</p>
<div class="flow">
  <div class="node">主线程<span class="sub">client.session.list()</span></div>
  <div class="arrow">→</div>
  <div class="node">createWorkerFetch<span class="sub">假 fetch·打包请求</span></div>
  <div class="arrow">RPC →</div>
  <div class="node">Worker 线程<span class="sub">rpc.fetch 收下</span></div>
  <div class="arrow">→</div>
  <div class="node">app.fetch<span class="sub">同一个 webHandler</span></div>
</div>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">主线程：SDK 调 client.session.list()，内部调那个「假 fetch」</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">createWorkerFetch 把 url/method/headers/body 打包，client.call("fetch", ...)</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">RPC 消息跨线程送到 Worker —— 不经网卡，不走 TCP</span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">worker 的 rpc.fetch 重建 Request，调 Server.Default().app.fetch</span></div>
  <div class="t-row"><span class="t-num">5</span><span class="t-txt">回传 {status, headers, body}，主线程拼回 Response 交给 SDK</span></div>
</div>

<h2>Worker 那头：同一个 handler</h2>
<p>RPC 消息飞到 Worker 线程，落在 <span class="mono">cli/tui/worker.ts</span> 暴露的 <span class="mono">rpc.fetch</span> 上。这里是全课最值得拍案的一行——worker 收到请求后，干的事情是：</p>
<pre class="code"><span class="cm">// 简化自 cli/tui/worker.ts —— worker 侧的 fetch 实现</span>
<span class="kw">async</span> <span class="fn">fetch</span>(input) {
  <span class="kw">const</span> request = <span class="kw">new</span> <span class="fn">Request</span>(input.url, {
    method: input.method, headers, body: input.body })
  <span class="kw">const</span> response = <span class="kw">await</span> Server.<span class="fn">Default</span>().app.<span class="fn">fetch</span>(request)  <span class="cm">// ← 就是第 9 课那个 handler！</span>
  <span class="kw">return</span> { status: response.status,
    headers: Object.<span class="fn">fromEntries</span>(response.headers.<span class="fn">entries</span>()),
    body: <span class="kw">await</span> response.<span class="fn">text</span>() }
}</pre>
<p><span class="mono">Server.Default().app.fetch(request)</span>——这正是第 9 课里那个「收下所有请求」的 webHandler，<strong>一字不差</strong>。绕了这么一大圈，worker 最终调的，和网络客户端最终触达的，是<strong>同一个处理器、同一套路由组、同一批 handler</strong>。网络那条路只是在它前面多套了「序列化→TCP→反序列化」几层壳；进程内这条路把那几层壳全省了，直接把 <span class="mono">Request</span> 递到 handler 嘴边。<strong>业务逻辑只有一份，且只写了一遍</strong>——这就是「server 是纯函数」这个朴素事实，所兑换来的全部红利。</p>
<div class="cols">
  <div class="col"><h4>为什么要分两个线程</h4><p>主线程要专心渲染 TUI、保持跟手；模型调用、工具执行这些重活塞进 worker，免得卡住界面。</p></div>
  <div class="col"><h4>为什么不直接函数调用</h4><p>跨线程不能共享内存对象，只能传消息。RPC 就是把「跨线程调函数」包装成了类型安全的消息往返。</p></div>
</div>
<p>顺带一提，worker 暴露的 RPC 接口远不止 <span class="mono">fetch</span> 一个方法——它是富 TUI 操纵这个「隔壁大脑」的整套遥控器。瞥一眼这些方法名，你就能感到进程内这条路的便利：很多在网络端要专门设端点的事，在这里只是 worker 对象上的一个普通方法。</p>
<div class="cellgroup">
  <div class="cell"><div class="k">fetch</div><div class="v">本课主角：把请求转交给 app.fetch，零网络</div></div>
  <div class="cell"><div class="k">server</div><div class="v">按需真的起一个网络 server（让别的客户端也能连进来）</div></div>
  <div class="cell"><div class="k">reload</div><div class="v">让 worker 重新加载配置，热更新</div></div>
  <div class="cell"><div class="k">snapshot</div><div class="v">写一份堆快照，给内存调试用</div></div>
</div>
<p>这里藏着一个很妙的细节：worker 上有个 <span class="mono">server</span> 方法，能<strong>按需把网络 server 也启动起来</strong>。也就是说，富 TUI 平时自己走零网络的进程内通道，但只要你需要，它能<strong>顺手把大门也打开</strong>，让网页端、远程客户端同时连进<strong>同一个大脑</strong>。两种传输不是二选一，而是能<strong>叠加共存</strong>——同一个 server 实例，既服务楼内的 TUI，又服务楼外打电话进来的客人。这正是「传输与逻辑解耦」最实在的好处：加一种访问方式，不是重写一个系统，只是多开一扇门。</p>

<h2>连事件也走这条管道</h2>
<p>还有一处优雅得容易被错过：<strong>第 11 课那条 SSE 事件流，在进程内模式下也照样工作</strong>，只不过换了运力。看 worker 启动时的这几行：它订阅全局事件总线，每来一个事件，就用 <span class="mono">Rpc.emit</span> 沿 RPC 通道<strong>主动推</strong>给主线程：</p>
<pre class="code"><span class="cm">// cli/tui/worker.ts —— 把全局事件经 RPC 转发给主线程</span>
GlobalBus.<span class="fn">on</span>(<span class="st">"event"</span>, (event) =&gt; {
  Rpc.<span class="fn">emit</span>(<span class="st">"global.event"</span>, event)  <span class="cm">// ← 不经 SSE/HTTP，直接走 RPC</span>
})</pre>
<p>于是无论走哪条传输，<strong>客户端拿到的「世界」是一致的</strong>：网络客户端通过 SSE 长连接收事件，进程内 TUI 通过 RPC 收事件，但两者收到的是<strong>同一条总线上的同一批事件</strong>。第 9 到 13 课构建的整个 server 表面——请求端点、事件流——在两种传输下都<strong>完整可用</strong>。这就是为什么你在 TUI 里和在网页里，看到的会话、消息、实时进度会<strong>分毫不差</strong>：它们面对的本就是同一个大脑，只是有人打电话、有人走楼内传送管而已。</p>
<p>把这件事想透，你会发现 opencode 在这里做了一个很高明的归一：<strong>它没有为 TUI 单独发明一套「本地通信协议」</strong>。最偷懒也最常见的做法，是给进程内场景写一条捷径——TUI 直接调内部函数拿数据、内部回调收事件，绕开整个 HTTP/SSE 表面。可那样一来，TUI 和网页端就成了<strong>两套并行演化的代码</strong>，迟早各长各的、行为漂移。opencode 偏不：它逼着进程内这条路也<strong>老老实实走完 Request→handler→Response、走完事件总线→推送</strong>，只是把「运力」从网络换成了 RPC。代价是多搭了 <span class="mono">createWorkerFetch</span> 这层薄薄的转接，收益却是<strong>所有客户端共享唯一一套语义</strong>——这笔账，和第 12 课「宁可生成也不手写 SDK」算的是同一本。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景·第三部分收官</div>
  <p>这一课让整个「客户端/服务器」部分（第 9–13 课）<strong>合龙</strong>了。回望这条主线：</p>
  <ul>
    <li><strong>第 9 课</strong>：server = 一个 <span class="mono">(request)=&gt;Response</span> 的纯函数，建在类型化的 HttpApi 上。</li>
    <li><strong>第 10 课</strong>：20 个组声明契约，handler 接到 core，中间件成环。</li>
    <li><strong>第 11 课</strong>：event 组用 SSE 把事件总线推成实时流。</li>
    <li><strong>第 12 课</strong>：fromApi 把类型读成规范，自动生成吃 <span class="mono">fetch</span> 的 SDK。</li>
    <li><strong>第 13 课·本课</strong>：换掉那个 <span class="mono">fetch</span>，同一套 server + SDK 就在「网络」与「进程内」两种传输间自由切换。</li>
  </ul>
  <p>一句话总结整个第三部分：<strong>opencode 把「能力」「契约」「事件」「客户端」彻底解耦，让同一个大脑，能被任意数量、任意距离的客户端，以最合适的方式访问。</strong>下一部分（第四部分）我们将<strong>推门走进这个大脑</strong>——看一个 prompt 进来后，会话、消息、Agent 循环、工具调用是怎么一步步把它变成回答的。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p>传输的切换，落到代码上只是<strong>填进去的 <span class="mono">fetch</span> 不同</strong>而已。看 tui.ts 里组装 SDK 时那一念之差：</p>
  <pre class="code"><span class="cm">// cli/cmd/tui.ts —— 同一个 SDK，喂不同的 fetch</span>
<span class="cm">// 富 TUI：进程内，喂 worker fetch</span>
{ fetch: <span class="fn">createWorkerFetch</span>(client) }   <span class="cm">// → RPC → worker → app.fetch</span>

<span class="cm">// 其它客户端：喂真正的 transport.fetch</span>
{ fetch: transport.fetch }              <span class="cm">// → 网络 HTTP → app.fetch</span></pre>
  <p>两行的差别，就是「打电话」和「走楼内传送管」的差别。但请注意：<strong>差别仅此一处</strong>。SDK 的方法、server 的逻辑、事件的语义，全都共享、全都只写了一遍。把一个系统最易变的维度（部署/传输）压缩成「换一个参数」，是架构设计能达到的相当优雅的境界。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li>「同一 handler、两种传输」在这一课兑现：<strong>接缝就是 <span class="mono">fetch</span></strong>——server 进出是 <span class="mono">Request/Response</span>，SDK 的所有调用都经一个可配置的 <span class="mono">fetch</span>。</li>
    <li><strong>传输 A（网络）</strong>：填原生 <span class="mono">fetch</span> → HTTP/TCP → NodeHttpServer → webHandler。通用，但有网络开销。</li>
    <li><strong>传输 B（进程内）</strong>：<span class="mono">createWorkerFetch</span> 对外伪装成 <span class="mono">fetch</span>，对内把请求经 RPC 发给 Worker 线程，worker 直接调 <span class="mono">Server.Default().app.fetch</span>——同一个 handler，零网络。</li>
    <li>分两线程是为<strong>主线程渲染不被重活拖卡</strong>；跨线程不能共享内存，故用<strong>类型安全的 RPC</strong> 传消息。</li>
    <li>连<strong>事件流</strong>也复用这条管道：worker 把 GlobalBus 事件经 <span class="mono">Rpc.emit</span> 推给主线程，等价于网络端的 SSE。整个 server 表面在两种传输下都完整可用。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">In Lesson 9 we laid a hook: the server is outwardly just a <span class="mono">(request) =&gt; Response</span> function, and "because it's so standard, it runs on a network server and can also be called inside an in-process worker." In Lesson 12 we got an SDK <strong>parameterized by <span class="mono">fetch</span></strong>. This lesson is Part 3's <strong>finale and climax</strong>: we snap these two pieces together and watch the rich TUI call — with <strong>zero network</strong> — the very same server the web client uses. The answer hides in one function: <span class="mono">createWorkerFetch</span>, which builds a "fake fetch" indistinguishable in shape from the standard <span class="mono">fetch</span>, yet touching no network at all.</p>
<p>Why is this the keystone of all of Part 3? Because it gathers every earlier hook at once: the server is a pure function (Lesson 9), the SDK eats a <span class="mono">fetch</span> (Lesson 12), events ride an SSE stream (Lesson 11) — snap these three together and you reach a striking conclusion: <strong>the same business logic, the same SDK, with a hot-swappable transport layer</strong>. Swap the <span class="mono">fetch</span> and the TUI turns from a "network client" into an "in-process client," while the server and SDK <strong>change not a single character</strong>. This is Lesson 6's "implementation replaceable wholesale," cashed out at the system's very outermost layer.</p>

<div class="card analogy">
  <div class="tag">🏨 Analogy</div>
  Remember Lesson 9's hotel front desk? The desk does only one thing: <strong>take an order ticket, get it done, hand back a receipt</strong> — it doesn't care <strong>how</strong> the ticket reached it. A guest staying in the building (the rich TUI) needn't run outside to a payphone to call in; they walk up to the desk, or use the building's <strong>pneumatic tube</strong> to whoosh the ticket onto the counter — that's <span class="mono">createWorkerFetch</span>: in-building delivery, never leaving the building, never touching the phone network. A guest in another city (web/desktop) can only <strong>phone in</strong> (real network HTTP). Two guests, <strong>same desk, same service menu, same guidebook</strong> (SDK); the only difference is "how the ticket gets to the counter." Abstract "how the ticket arrives" into a replaceable part, and the one desk can serve inside and outside at once — that's all the magic of this lesson.
</div>

<h2>Where's the seam: fetch is the joint</h2>
<p>To see why transport is hot-swappable, first spot where the "seam" is cut. Recall two facts: the server is <span class="mono">app.fetch(request)</span> — in a <span class="mono">Request</span>, out a <span class="mono">Response</span>; and the SDK in Lesson 12 was generated with <span class="mono">@hey-api/client-fetch</span>, so <strong>all its network calls go out through one configurable <span class="mono">fetch</span> function</strong>. Both ends meet at the standard <span class="mono">fetch</span> shape — <strong>that's the seam</strong>. As long as you can supply a function "shaped like <span class="mono">fetch</span> but doing whatever it likes inside," you can steer the SDK's requests <strong>anywhere you want</strong>.</p>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">call</span><span class="name">client.session.list()</span></div><div class="ld">SDK method (generated in Lesson 12)</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">seam</span><span class="name">fetch(request) =&gt; Response</span></div><div class="ld">★ the replaceable joint ★</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">transport</span><span class="name">real fetch ╱ createWorkerFetch</span></div><div class="ld">network HTTP, or in-process RPC</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">handle</span><span class="name">app.fetch(request)</span></div><div class="ld">the same webHandler (Lesson 9)</div></div>
</div>
<p>Grasp this diagram and 70% of the lesson clicks: the top and bottom layers are <strong>immovable</strong> — the SDK method doesn't change, the server handler doesn't change. The only swappable thing is the middle <strong>"transport"</strong> layer. The web fills it with the real <span class="mono">fetch</span> and requests go over the network; the rich TUI fills it with <span class="mono">createWorkerFetch</span> and requests go in-process. <strong>Everything above and below the seam stays untouched; swap only the part plugged into the seam</strong>, and the transport changes completely. This is "program to an interface, not an implementation" in its cleanest field test.</p>
<p>This seam can be cut so cleanly thanks to an often-underrated design eye: <strong>pick a boundary that's "extremely narrow yet extremely standard."</strong> The <span class="mono">fetch</span> shape is so simple it's down to "in Request, out Response" — being narrow, anyone can implement one; being a Web standard, the SDK, browsers, and runtimes all already recognize it. Had the server exposed a bloated client interface with dozens of methods, swapping transport would mean rewriting all dozens; compressed to a single <span class="mono">fetch</span>, swapping transport is just "implement one function." <strong>The narrower the boundary, the stronger the replaceability</strong> — an aesthetic running through opencode, pushed to its extreme in this lesson.</p>

<h2>Transport A: real fetch, over the network</h2>
<p>This road is the most straightforward, and the one most clients take. Web, desktop, and remote clients are at a <strong>real distance</strong> from the server process — a real network sits between them. So the SDK is filled with the browser/runtime's <strong>native <span class="mono">fetch</span></strong>: the request is serialized to an HTTP message, sent over TCP to the server's listening port (default 4096), the server's <span class="mono">NodeHttpServer</span> receives it, hands it to the webHandler, then serializes the <span class="mono">Response</span> back. It's all standard HTTP, no tricks. This road's upside is <strong>universality</strong>: anything that can send HTTP can be an opencode client. The cost is <strong>network overhead</strong>: serialization, TCP, deserialization, every hop costs.</p>
<div class="cols">
  <div class="col"><h4>Transport A · network fetch</h4><p>real fetch → HTTP/TCP → port 4096. <strong>Universal</strong>: browser, desktop, remote all connect. <strong>Cost</strong>: serialization + network round-trip.</p></div>
  <div class="col"><h4>Transport B · worker fetch</h4><p>createWorkerFetch → RPC → the next thread over. <strong>Very fast</strong>: zero network, zero HTTP serialization. <strong>Limit</strong>: only for the same-process rich TUI.</p></div>
</div>

<h2>Transport B: createWorkerFetch, zero network</h2>
<p>The rich TUI's situation is entirely different: it runs <strong>in the same process</strong> as the server — just split across two threads. The main thread renders the UI (must be fast, must feel responsive), while the server's heavy work (calling models, running tools) is placed in a <strong>Worker thread</strong>. Between the two threads is not a network but an in-process message channel. Since the server is right next door in another thread, why serialize the request to HTTP and loop around the network and back? <span class="mono">createWorkerFetch</span> is here to take that shortcut:</p>
<pre class="code"><span class="cm">// simplified from cli/cmd/tui.ts — a function shaped like fetch but riding RPC</span>
<span class="kw">function</span> <span class="fn">createWorkerFetch</span>(client: RpcClient): <span class="kw">typeof</span> fetch {
  <span class="kw">const</span> fn = <span class="kw">async</span> (input, init) =&gt; {
    <span class="kw">const</span> result = <span class="kw">await</span> client.<span class="fn">call</span>(<span class="st">"fetch"</span>, {  <span class="cm">// ← RPC to the worker, no network</span>
      url: ..., method: ..., headers: ..., body: ...,
    })
    <span class="kw">return new</span> <span class="fn">Response</span>(result.body, { status: result.status, ... })
  }
  <span class="kw">return</span> fn <span class="kw">as typeof</span> fetch  <span class="cm">// ← disguised outwardly as the standard fetch</span>
}</pre>
<p>Look at its two ends: <strong>outwardly</strong>, its signature is asserted as <span class="mono">typeof fetch</span> — in the SDK's eyes it's indistinguishable from real <span class="mono">fetch</span>; the SDK is blissfully unaware it isn't on the network. <strong>Inwardly</strong>, it sends no HTTP at all; it packs the request's four essentials (url/method/headers/body) and ships them via <span class="mono">client.call("fetch", ...)</span> over RPC to the Worker thread, then <strong>reassembles a <span class="mono">Response</span></strong> from the worker's returned <span class="mono">{status, headers, body}</span> and hands it back to the SDK. In and out, the shape is identical to real fetch, yet the network card was never touched.</p>
<div class="flow">
  <div class="node">main thread<span class="sub">client.session.list()</span></div>
  <div class="arrow">→</div>
  <div class="node">createWorkerFetch<span class="sub">fake fetch · packs request</span></div>
  <div class="arrow">RPC →</div>
  <div class="node">Worker thread<span class="sub">rpc.fetch receives</span></div>
  <div class="arrow">→</div>
  <div class="node">app.fetch<span class="sub">the same webHandler</span></div>
</div>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">main thread: SDK calls client.session.list(), internally calling the "fake fetch"</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">createWorkerFetch packs url/method/headers/body, client.call("fetch", ...)</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">the RPC message crosses threads to the Worker — no NIC, no TCP</span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">the worker's rpc.fetch rebuilds the Request, calls Server.Default().app.fetch</span></div>
  <div class="t-row"><span class="t-num">5</span><span class="t-txt">returns {status, headers, body}; the main thread reassembles a Response for the SDK</span></div>
</div>

<h2>The worker side: the same handler</h2>
<p>The RPC message flies to the Worker thread and lands on the <span class="mono">rpc.fetch</span> exposed by <span class="mono">cli/tui/worker.ts</span>. Here is the lesson's most applause-worthy line — on receiving the request, the worker does this:</p>
<pre class="code"><span class="cm">// simplified from cli/tui/worker.ts — the worker-side fetch impl</span>
<span class="kw">async</span> <span class="fn">fetch</span>(input) {
  <span class="kw">const</span> request = <span class="kw">new</span> <span class="fn">Request</span>(input.url, {
    method: input.method, headers, body: input.body })
  <span class="kw">const</span> response = <span class="kw">await</span> Server.<span class="fn">Default</span>().app.<span class="fn">fetch</span>(request)  <span class="cm">// ← it's Lesson 9's handler!</span>
  <span class="kw">return</span> { status: response.status,
    headers: Object.<span class="fn">fromEntries</span>(response.headers.<span class="fn">entries</span>()),
    body: <span class="kw">await</span> response.<span class="fn">text</span>() }
}</pre>
<p><span class="mono">Server.Default().app.fetch(request)</span> — this is exactly Lesson 9's "receive every request" webHandler, <strong>character for character</strong>. After this whole loop, what the worker ultimately calls, and what the network client ultimately reaches, is the <strong>same handler, same route groups, same handlers</strong>. The network road just wraps a few extra shells in front of it — "serialize → TCP → deserialize"; the in-process road drops all those shells and hands the <span class="mono">Request</span> straight to the handler's lips. <strong>There's only one copy of the business logic, written only once</strong> — that's the entire dividend bought by the plain fact that "the server is a pure function."</p>
<div class="cols">
  <div class="col"><h4>Why two threads</h4><p>The main thread must focus on rendering the TUI and staying responsive; heavy work like model calls and tool execution goes into the worker, lest the UI stall.</p></div>
  <div class="col"><h4>Why not a direct function call</h4><p>Threads can't share memory objects, only pass messages. RPC wraps "call a function across threads" into a type-safe message round-trip.</p></div>
</div>
<p>By the way, the worker's RPC interface has far more than just <span class="mono">fetch</span> — it's the rich TUI's full remote control for this "brain next door." Glance at the method names and you feel the convenience of the in-process road: many things that need a dedicated endpoint on the network side are, here, just an ordinary method on the worker object.</p>
<div class="cellgroup">
  <div class="cell"><div class="k">fetch</div><div class="v">this lesson's star: hand the request to app.fetch, zero network</div></div>
  <div class="cell"><div class="k">server</div><div class="v">on demand, actually start a network server (so other clients can connect too)</div></div>
  <div class="cell"><div class="k">reload</div><div class="v">make the worker reload config, hot-update</div></div>
  <div class="cell"><div class="k">snapshot</div><div class="v">write a heap snapshot for memory debugging</div></div>
</div>
<p>A neat detail hides here: the worker has a <span class="mono">server</span> method that can <strong>start the network server on demand</strong>. That is, the rich TUI normally rides its own zero-network in-process channel, but whenever you need it, it can <strong>open the front door too</strong>, letting web and remote clients connect into the <strong>same brain</strong> at the same time. The two transports aren't either-or; they can <strong>coexist, stacked</strong> — one server instance serving both the in-building TUI and the guests phoning in from outside. This is the most concrete benefit of "decoupling transport from logic": adding an access method isn't rewriting a system, just opening one more door.</p>

<h2>Even events ride this pipe</h2>
<p>One more elegance easily missed: <strong>Lesson 11's SSE event stream works just as well in in-process mode</strong>, only on different haulage. Look at these lines at worker startup: it subscribes to the global event bus, and on each event <strong>actively pushes</strong> it to the main thread over the RPC channel via <span class="mono">Rpc.emit</span>:</p>
<pre class="code"><span class="cm">// cli/tui/worker.ts — forward global events to the main thread over RPC</span>
GlobalBus.<span class="fn">on</span>(<span class="st">"event"</span>, (event) =&gt; {
  Rpc.<span class="fn">emit</span>(<span class="st">"global.event"</span>, event)  <span class="cm">// ← not via SSE/HTTP, straight over RPC</span>
})</pre>
<p>So whichever transport is taken, <strong>the "world" the client receives is identical</strong>: the network client receives events over an SSE long connection, the in-process TUI receives events over RPC, but both get the <strong>same events from the same bus</strong>. The whole server surface built across Lessons 9–13 — request endpoints, event stream — is <strong>fully usable</strong> under both transports. That's why the sessions, messages, and live progress you see in the TUI versus in the web are <strong>identical to the letter</strong>: they face the same brain all along; some just phone in while others use the building's tube.</p>
<p>Think this through and you'll see opencode made a clever unification here: <strong>it didn't invent a separate "local communication protocol" just for the TUI</strong>. The laziest and most common move would be to write a shortcut for the in-process case — the TUI directly calling internal functions for data and internal callbacks for events, bypassing the whole HTTP/SSE surface. But then the TUI and the web become <strong>two codebases evolving in parallel</strong>, sooner or later growing apart and drifting in behavior. opencode refuses: it forces the in-process road to also <strong>faithfully run the full Request→handler→Response and the full event bus→push</strong>, only swapping the "haulage" from network to RPC. The cost is the thin <span class="mono">createWorkerFetch</span> adapter; the payoff is <strong>all clients sharing one and only one set of semantics</strong> — the same ledger Lesson 12 balanced with "generate rather than hand-write the SDK."</p>

<div class="card macro">
  <div class="tag">🗺️ The big picture · Part 3 finale</div>
  <p>This lesson makes the whole "client/server" part (Lessons 9–13) <strong>close up</strong>. Look back along the main line:</p>
  <ul>
    <li><strong>Lesson 9</strong>: server = a <span class="mono">(request)=&gt;Response</span> pure function, built on the typed HttpApi.</li>
    <li><strong>Lesson 10</strong>: 20 groups declare contracts, handlers wire to core, middleware forms a ring.</li>
    <li><strong>Lesson 11</strong>: the event group pushes the event bus into a real-time stream via SSE.</li>
    <li><strong>Lesson 12</strong>: fromApi reads types into a spec, auto-generating an SDK that eats a <span class="mono">fetch</span>.</li>
    <li><strong>Lesson 13 · this one</strong>: swap that <span class="mono">fetch</span> and the same server + SDK move freely between "network" and "in-process" transports.</li>
  </ul>
  <p>One line for all of Part 3: <strong>opencode fully decouples "capability," "contract," "events," and "client," so one brain can be accessed by any number of clients, at any distance, in the most fitting way.</strong> Next part (Part 4) we <strong>push the door open into this brain</strong> — watching how, after a prompt comes in, the session, messages, Agent loop, and tool calls turn it step by step into an answer.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source detail</div>
  <p>Switching transport, landed in code, is merely <strong>a different <span class="mono">fetch</span> filled in</strong>. See the one-thought difference when tui.ts assembles the SDK:</p>
  <pre class="code"><span class="cm">// cli/cmd/tui.ts — same SDK, fed a different fetch</span>
<span class="cm">// rich TUI: in-process, feed the worker fetch</span>
{ fetch: <span class="fn">createWorkerFetch</span>(client) }   <span class="cm">// → RPC → worker → app.fetch</span>

<span class="cm">// other clients: feed the real transport.fetch</span>
{ fetch: transport.fetch }              <span class="cm">// → network HTTP → app.fetch</span></pre>
  <p>The difference between the two lines is the difference between "phoning in" and "using the building's tube." But note: <strong>the difference is only here</strong>. The SDK's methods, the server's logic, the events' semantics are all shared, all written once. Compressing a system's most volatile dimension (deployment/transport) into "swap one argument" is a fairly elegant height for architecture to reach.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key points</div>
  <ul>
    <li>"One handler, two transports" is cashed out here: <strong>the seam is <span class="mono">fetch</span></strong> — the server's in/out is <span class="mono">Request/Response</span>, and all SDK calls go through one configurable <span class="mono">fetch</span>.</li>
    <li><strong>Transport A (network)</strong>: fill in the native <span class="mono">fetch</span> → HTTP/TCP → NodeHttpServer → webHandler. Universal, but with network overhead.</li>
    <li><strong>Transport B (in-process)</strong>: <span class="mono">createWorkerFetch</span> disguises as <span class="mono">fetch</span> outwardly, inwardly ships the request via RPC to the Worker thread, which calls <span class="mono">Server.Default().app.fetch</span> directly — the same handler, zero network.</li>
    <li>Two threads exist so the <strong>main thread's rendering isn't stalled by heavy work</strong>; threads can't share memory, so messages travel via <strong>type-safe RPC</strong>.</li>
    <li>Even the <strong>event stream</strong> reuses this pipe: the worker pushes GlobalBus events to the main thread via <span class="mono">Rpc.emit</span>, equivalent to the network side's SSE. The whole server surface is fully usable under both transports.</li>
  </ul>
</div>
""",
}
