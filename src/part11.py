"""Part 11 (Part 11 · Extensibility) content. Placeholders until M11 fills them in."""
from placeholder import wip

LESSON_57 = {
    "zh": r"""
<p class="lead">从这一部分 M11 起，我们换一个视角：不再看 opencode <strong>自己</strong>怎么运转，而是看它<strong>怎么向外敞开</strong>——让第三方、让外部工具、让你，都能把自己的能力接进来。这一课讲的，是 opencode 最核心的一扇「敞开之门」：<strong>插件系统</strong>。它解决的问题很实在：你想给 opencode 加点料——拦截每次工具调用做审计、给某家模型自定义请求头、注册一个全新的工具、接一个内部认证……但你<strong>不想 fork 整个项目、不想改它的源码</strong>。插件系统就是答案：<strong>写一个小插件、在配置里加一行、它就挂进了 agent 的生命周期。</strong>而最让人惊喜的是这个插件能有多简单——它就是<strong>一个函数</strong>。</p>
<p>这一课有两个最值得带走的洞见。第一，<strong>一个插件 = 一个返回「钩子表」的函数</strong>：<span class="mono">Plugin = (input) =&gt; Promise&lt;Hooks&gt;</span>。没有类、没有继承、没有样板——你写一个 async 函数，它收到一份 <span class="mono">PluginInput</span> 上下文，返回一个 <span class="mono">Hooks</span> 对象（里面是你想挂的各种生命周期钩子）。而那份 <span class="mono">input</span> 给得极其慷慨：里面有 <strong>opencode 的 SDK 客户端</strong>（于是你的插件能反过来调用 opencode 自己的 API——读会话、发消息）、有 project/directory/worktree 上下文、甚至有一个 <strong>Bun shell <span class="mono">$</span></strong> 让你直接跑命令。第二，<strong>插件从配置里加载、无需改源码</strong>：配置里的 <span class="mono">plugin: [...]</span> 列出你要的插件（npm 包名或本地路径），加载器负责把它们装好、导入、挂上。<strong>扩展 opencode，从此是「往配置加一行」，而不是「fork 一个仓库」。</strong>读懂这两点，你就懂了「为什么 opencode 能在不臃肿的前提下，长出几乎无限的可能」。</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  把 opencode 的插件想象成<strong>浏览器扩展</strong>（或 VS Code 插件）。你不会为了「给浏览器加个去广告功能」就去改浏览器源码、自己编译一个浏览器——你<strong>装一个扩展</strong>就行。扩展之所以能这么轻便，靠的是浏览器给了它两样东西：一套<strong>明确的 API</strong>（扩展能读写页面、发请求——对应 opencode 给插件的 <strong>SDK 客户端</strong>），和一组<strong>事件钩子</strong>（「标签页打开时」「网络请求发出前」——对应 opencode 的 <strong>Hooks</strong>）。扩展只管说「<strong>在某事发生时，请调用我这段逻辑</strong>」，宿主负责在恰当的时机回调它。opencode 的插件一模一样：你声明「<strong>工具执行前请叫我</strong>」「<strong>聊天参数定下来前让我改改</strong>」，opencode 就在那些时刻执行你的钩子。<strong>宿主不必知道有哪些插件、插件也不必改宿主——双方只通过「API + 钩子」这份契约打交道</strong>，于是生态能在不动内核的前提下野蛮生长。
</div>

<h2>一个插件，就是一个返回钩子的函数</h2>
<p>opencode 的插件系统朴素得惊人。看公开包 <span class="mono">@opencode-ai/plugin</span> 里那个例子插件，整个就这么几行：</p>
<pre class="code"><span class="kw">import</span> { Plugin, tool } <span class="kw">from</span> <span class="st">"@opencode-ai/plugin"</span>

<span class="kw">export const</span> ExamplePlugin: Plugin = <span class="kw">async</span> (ctx) =&gt; {
  <span class="kw">return</span> {                                  <span class="cm">// ← 返回一个 Hooks 对象</span>
    tool: {                                 <span class="cm">// 注册一个自定义工具</span>
      mytool: <span class="fn">tool</span>({
        description: <span class="st">"This is a custom tool"</span>,
        args: { foo: tool.schema.<span class="fn">string</span>() },
        <span class="kw">async</span> <span class="fn">execute</span>(args) { <span class="kw">return</span> <span class="st">`Hello ${'$'}{args.foo}!`</span> },
      }),
    },
  }
}</pre>
<p>就这么简单：一个 <span class="mono">async</span> 函数，收一个上下文 <span class="mono">ctx</span>，返回一个对象。类型定义把这件事说得明明白白：<span class="mono">Plugin = (input: PluginInput, options?) =&gt; Promise&lt;Hooks&gt;</span>。<strong>没有要继承的基类、没有要实现的接口方法、没有要注册的装饰器</strong>——就是「函数进、钩子出」。这种极简，本身就是一种善意：它把「写一个插件」的门槛压到了几乎为零，任何会写一个 JS 函数的人，五分钟就能给 opencode 加上自己的工具。你不必先去读一本厚厚的「插件开发指南」、不必理解一套陌生的框架概念，只要会写一个返回对象的 async 函数，你就已经会写 opencode 插件了——剩下的，不过是查一查那张钩子表里有哪些键可填。而那个传进来的 <span class="mono">input</span>（<span class="mono">PluginInput</span>），是 opencode 递给插件的<strong>「工具箱」</strong>，慷慨得超乎想象：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">client</div><div class="c-txt">opencode 的 <strong>SDK 客户端</strong>——插件能反过来调 opencode 自己的 API（读会话、发消息…）</div></div>
  <div class="cell"><div class="c-tag">project / directory / worktree</div><div class="c-txt">当前项目、目录、工作树——插件知道自己在哪儿干活</div></div>
  <div class="cell"><div class="c-tag">$（Bun shell）</div><div class="c-txt">一个开箱即用的 shell，插件能直接跑外部命令</div></div>
  <div class="cell"><div class="c-tag">serverUrl / experimental_workspace</div><div class="c-txt">服务器地址、注册工作区适配器的口子</div></div>
</div>
<p>这份 <span class="mono">input</span> 里最点睛的，是那个 <span class="mono">client</span>——<strong>opencode 把自己的整套 API 客户端，交到了插件手里</strong>。这意味着插件不是一个只能被动响应钩子的「小跟班」，而是一个能<strong>主动操作 opencode</strong> 的完整公民：它能在钩子里读取当前会话的消息、能往会话里发一条新消息、能查询配置……再配上那个 Bun shell <span class="mono">$</span>，插件甚至能去跑任意外部命令、把结果带回来。<strong>给插件「宿主的 API + 一个 shell」，就等于给了它「既能感知 opencode、又能驱动 opencode、还能伸手到外部世界」的全部本钱</strong>——这正是一个强大插件系统该有的慷慨。</p>

<h2>Hooks：插件挂进生命周期的那些点</h2>
<p>函数返回的那个 <span class="mono">Hooks</span> 对象，才是插件真正<strong>「接入」</strong> opencode 的地方。它是一张「钩子表」——每个键是一个生命周期时刻，值是「那一刻请执行我这段逻辑」。这些钩子大致分几类（下一课 L58 会逐个细讲，这里先看全景）：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">event / config</div><div class="c-txt">每个事件发生时 / 配置加载时——最通用的观察点</div></div>
  <div class="cell"><div class="c-tag">auth / provider</div><div class="c-txt">注册自定义认证、自定义模型 provider（接公司内部模型网关）</div></div>
  <div class="cell"><div class="c-tag">chat.message / params / headers</div><div class="c-txt">聊天消息后、定参数前、定请求头前——改写发往模型的请求</div></div>
  <div class="cell"><div class="c-tag">tool.execute.before / after</div><div class="c-txt">工具执行前后——审计、改参数、改结果（含 tool.definition 改工具描述）</div></div>
  <div class="cell"><div class="c-tag">permission.ask</div><div class="c-txt">权限询问时——插件可改裁决（allow/ask/deny），实现自定义策略</div></div>
</div>
<p>这张表覆盖了 agent 运转的几乎每一个关键关节：从「和模型说什么话」（chat.*）、到「能不能动手」（permission.ask）、到「工具怎么跑」（tool.*）、到「接哪家模型」（provider）。<strong>插件只需在表里填上自己关心的那几格</strong>——想做审计就填 <span class="mono">tool.execute.before</span>、想接内部模型就填 <span class="mono">provider</span>、想自定义权限策略就填 <span class="mono">permission.ask</span>，其余留空即可。这种「<strong>一张钩子表、按需填格</strong>」的设计，和你在 L47 见过的内置 provider 插件（<span class="mono">PluginV2.define</span> 返回钩子表）<strong>是同一个灵魂</strong>：opencode 内部用这套机制接模型，对外也用这套机制接你的扩展——内外同构，一通百通。</p>

<h2>从配置到运行：插件怎么被加载</h2>
<p>插件写好了，opencode 怎么找到并跑起它？答案是<strong>配置驱动 + 动态加载</strong>。你在配置的 <span class="mono">plugin</span> 数组里列出要用的插件（一个 npm 包名，或一个本地文件路径，可带选项），<span class="mono">plugin/loader.ts</span> 里的加载器就负责把它们一一就位：</p>
<div class="flow">
  <div class="f-node">配置 <span class="mono">plugin: [...]</span><br><small>npm 包名 / 本地路径</small></div>
  <div class="f-arrow">resolve →</div>
  <div class="f-node">解析 + 必要时装包<br><small>npm 安装、找入口</small></div>
  <div class="f-arrow">import →</div>
  <div class="f-node">动态导入模块<br><small>拿到 Plugin 函数</small></div>
  <div class="f-arrow">调用 →</div>
  <div class="f-node">Plugin(input)→Hooks<br><small>钩子挂进生命周期</small></div>
</div>
<p>加载器的稳健，藏在它把这条链拆成的<strong>几个可重试阶段</strong>里：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">install</span><span class="t-txt">若是 npm 包，先把它装下来（网络/版本可能失败→可重试）</span></div>
  <div class="t-row"><span class="t-num">entry</span><span class="t-txt">找到模块的导入入口</span></div>
  <div class="t-row"><span class="t-num">compatibility</span><span class="t-txt">检查版本兼容性</span></div>
  <div class="t-row"><span class="t-num">load</span><span class="t-txt">真正 <span class="mono">import</span> 模块、拿到 Plugin 函数</span></div>
</div>
<p>每一阶段都可能因网络、版本等原因失败，加载器对可重试的失败分阶段重试、并统一汇报。最后 <span class="mono">loadExternal</span> 把配置里所有插件<strong>并行</strong>解析加载。这种「分阶段、可重试、并行」的设计，是因为插件加载触及了 opencode 最不可控的边界——<strong>第三方代码 + 网络安装</strong>：包可能没装上、入口可能找不到、版本可能不兼容。把这条易错的链拆成清晰的阶段、每段独立重试与报错，就是在「向外敞开」与「自身稳健」之间的务实平衡——<strong>敞开大门迎接第三方，但绝不让一个装不上的插件拖垮整个启动。</strong></p>
<p>说到这里，你可能想起 L47 那个内置的 provider 插件系统（<span class="mono">PluginV2.define</span>）。它俩什么关系？并排一看就清楚：</p>
<div class="cols">
  <div class="col"><h4>内部 PluginV2（L47）</h4><p>opencode <strong>自己</strong>用来接三十多家模型 provider 的内部机制；<span class="mono">PluginV2.define({id, effect→钩子})</span>，编进 opencode 源码。面向「opencode 的内核开发者」。</p></div>
  <div class="col"><h4>公开 Plugin（L57）</h4><p>opencode 给<strong>第三方/你</strong>的公开扩展 API（<span class="mono">@opencode-ai/plugin</span>）；<span class="mono">(input)=&gt;Promise&lt;Hooks&gt;</span>，从配置加载。面向「opencode 的用户与生态」。</p></div>
</div>
<p>两者灵魂相通——<strong>都是「一个返回钩子表的东西」</strong>，只是一个对内、一个对外。这正是好架构的自洽：opencode 接自己的模型、和你接自己的扩展，用的是<strong>同一套「填钩子表」的思路</strong>，内外一以贯之。有了这扇门，能干的事五花八门：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">审计 / 合规</div><div class="c-txt"><span class="mono">tool.execute.before</span> 记录每次工具调用、拦截危险操作</div></div>
  <div class="cell"><div class="c-tag">接内部模型</div><div class="c-txt"><span class="mono">provider</span>/<span class="mono">auth</span> 接公司私有模型网关与认证</div></div>
  <div class="cell"><div class="c-tag">自定义工具</div><div class="c-txt"><span class="mono">tool</span> 注册查内部系统、调专有 API 的新工具</div></div>
  <div class="cell"><div class="c-tag">自定义权限策略</div><div class="c-txt"><span class="mono">permission.ask</span> 按公司规则自动 allow/deny</div></div>
</div>

<div class="card macro">
  <div class="tag">🗺️ 宏观视角</div>
  <p>这一课打开了 opencode 的扩展之门——让第三方、外部工具与你都能把能力接进来的插件系统：</p>
  <ul>
    <li><strong>插件 = 返回钩子表的函数</strong>（<span class="mono">@opencode-ai/plugin</span> 的 <span class="mono">Plugin = (input, options?) =&gt; Promise&lt;Hooks&gt;</span>）：无类无继承无样板，async 函数收 <span class="mono">PluginInput</span>、返回 <span class="mono">Hooks</span>。例子插件几行就注册一个自定义工具。</li>
    <li><strong>PluginInput = 慷慨的工具箱</strong>：<span class="mono">client</span>(opencode SDK 客户端，插件能反调 opencode API)、project/directory/worktree、<span class="mono">$</span>(Bun shell 跑命令)、serverUrl、experimental_workspace。给插件「宿主 API + shell」=既能感知又能驱动 opencode、还能伸手外部。</li>
    <li><strong>Hooks = 生命周期接入点</strong>：event/config、auth/provider、chat.message/params/headers、tool.execute.before/after(+definition)、permission.ask——按需填格。与 L47 内置 <span class="mono">PluginV2.define</span> 返回钩子表内外同构。</li>
    <li><strong>配置驱动 + 动态加载</strong>（<span class="mono">plugin/loader.ts</span>）：配置 <span class="mono">plugin:[...]</span>(npm 名/本地路径)→loader resolve(install/entry/compatibility/load 四阶段可重试)→import→<span class="mono">Plugin(input)</span>→挂 Hooks；<span class="mono">loadExternal</span> 并行加载。分阶段重试=向外敞开又自身稳健。</li>
  </ul>
  <p>门打开了——你现在知道了插件「是什么、怎么写、怎么被加载」。但那张 <span class="mono">Hooks</span> 表里每个钩子<strong>具体在何时触发、能改什么、典型怎么用</strong>，还是个轮廓。下一课（L58）就<strong>逐个细讲这些钩子</strong>：auth/provider 怎么接模型、chat.* 怎么改请求、tool.* 怎么包工具、permission.ask 怎么定策略——把这张「插件接入点地图」彻底点亮。再往后 L59 讲 LSP 集成、L60 讲 PTY/shell、L61 讲 ACP 与 Location 抽象。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p>插件系统的全部「契约」，浓缩在 <span class="mono">@opencode-ai/plugin</span> 的几行类型定义里（简化自源码）：</p>
  <pre class="code"><span class="cm">// 插件能拿到的上下文：宿主 API + 项目信息 + shell</span>
<span class="kw">export type</span> PluginInput = {
  client: <span class="fn">ReturnType</span>&lt;<span class="kw">typeof</span> createOpencodeClient&gt;   <span class="cm">// opencode SDK 客户端</span>
  project: Project
  directory: string
  worktree: string
  serverUrl: URL
  $: BunShell                              <span class="cm">// Bun shell，跑命令</span>
}

<span class="cm">// 一个插件 = 收上下文、返回钩子表的 async 函数</span>
<span class="kw">export type</span> Plugin = (input: PluginInput, options?: PluginOptions) =&gt; Promise&lt;Hooks&gt;

<span class="cm">// 配置里这样列插件：包名 或 [包名, 选项]</span>
<span class="kw">export type</span> Config = { plugin?: Array&lt;string | [string, PluginOptions]&gt; }</pre>
  <p>最值得品的，是这套设计如何用<strong>「函数 + 上下文 + 钩子表」三件极朴素的东西</strong>，撑起了一个完整的扩展生态。对比一下传统插件框架常见的重器械——要你继承一个 <span class="mono">AbstractPlugin</span> 基类、实现一堆生命周期方法、用复杂的依赖注入容器、配一份 XML/JSON 清单——opencode 把这一切<strong>削到只剩一个函数签名</strong>。这种极简不是偷懒，而是看透了插件的本质<strong>只需要回答两个问题</strong>：「你能给我什么？」（<span class="mono">PluginInput</span> 这份上下文）和「你想在何时介入？」（返回的 <span class="mono">Hooks</span> 这张表）。把契约收敛到这两点，其余全是普通的 JS/TS——没有要学的框架黑话、没有要背的生命周期顺序。<strong>一个好的扩展机制，门槛低到「会写函数就会写插件」，威力却大到「能接模型、能改请求、能定权限、能调宿主 API」——低门槛与高威力并不矛盾，关键在于把契约设计得既极简又恰好够用。</strong>这也呼应了全书反复出现的审美：最强的抽象，往往是最朴素的那个（L36 一张 Tool.make 表、L47 一个 PluginV2.define、L53 一个 createSimpleContext）。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>插件 = 返回钩子表的函数</strong>：<span class="mono">Plugin = (input: PluginInput, options?) =&gt; Promise&lt;Hooks&gt;</span>（<span class="mono">@opencode-ai/plugin</span>）。无类无继承无样板，async 函数进、Hooks 出。例子几行注册一个自定义工具。门槛低到「会写函数就会写插件」。</li>
    <li><strong>PluginInput = 慷慨工具箱</strong>：<span class="mono">client</span>(opencode SDK 客户端→插件能反调 opencode API)、project/directory/worktree、<span class="mono">$</span>(Bun shell)、serverUrl。给插件「宿主 API + shell」=能感知+能驱动 opencode+能伸手外部，不只是被动钩子。</li>
    <li><strong>Hooks = 生命周期接入点</strong>：event/config、auth/provider、chat.message/params/headers、tool.execute.before/after(+definition)、permission.ask——一张表、按需填格。与 L47 <span class="mono">PluginV2.define</span> 内外同构（opencode 内部接模型、对外接扩展，同一机制）。</li>
    <li><strong>配置驱动 + 动态加载</strong>（<span class="mono">plugin/loader.ts</span>）：配置 <span class="mono">plugin:[...]</span>(npm 名/本地路径)→resolve(install/entry/compatibility/load 四阶段可重试)→import→<span class="mono">Plugin(input)</span>→挂 Hooks；<span class="mono">loadExternal</span> 并行。分阶段重试=向外敞开（第三方代码+网络安装）又不被一个坏插件拖垮启动。</li>
    <li><strong>极简契约撑起完整生态</strong>：插件只需答两问——「你能给我什么」(PluginInput)+「你想何时介入」(Hooks)，其余全是普通 JS/TS。低门槛与高威力不矛盾。呼应全书「最强抽象往往最朴素」（L36/L47/L53）。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">From this part M11 on, we switch viewpoint: no longer how opencode runs <strong>itself</strong>, but how it <strong>opens outward</strong>—letting third parties, external tools, and you all plug your own capabilities in. This lesson covers opencode's most core "door of openness": the <strong>plugin system</strong>. The problem it solves is concrete: you want to add something to opencode—intercept every tool call for auditing, set custom request headers for some model, register a brand-new tool, hook in internal authentication…—but you <strong>don't want to fork the whole project or modify its source</strong>. The plugin system is the answer: <strong>write a little plugin, add a line to config, and it hooks into the agent's lifecycle.</strong> And the most delightful part is how simple that plugin can be—it's just <strong>a function</strong>.</p>
<p>This lesson has two highlights most worth taking away. First, <strong>a plugin = a function returning a "hook table"</strong>: <span class="mono">Plugin = (input) =&gt; Promise&lt;Hooks&gt;</span>. No class, no inheritance, no boilerplate—you write an async function, it receives a <span class="mono">PluginInput</span> context and returns a <span class="mono">Hooks</span> object (the various lifecycle hooks you want to hang). And that <span class="mono">input</span> is given extremely generously: it contains <strong>opencode's SDK client</strong> (so your plugin can in turn call opencode's own API—read sessions, send messages), the project/directory/worktree context, even a <strong>Bun shell <span class="mono">$</span></strong> to run commands directly. Second, <strong>plugins load from config, no source change</strong>: the <span class="mono">plugin: [...]</span> in config lists the plugins you want (npm package names or local paths), and the loader installs, imports, and hooks them up. <strong>Extending opencode is henceforth "add a line to config," not "fork a repo."</strong> Grasp these two and you'll understand "why opencode can grow nearly unlimited possibilities without bloating."</p>

<div class="card analogy">
  <div class="tag">🧩 Analogy</div>
  Picture opencode's plugins as <strong>browser extensions</strong> (or VS Code extensions). You wouldn't modify the browser's source and compile your own browser just "to add an ad-blocker"—you <strong>install an extension</strong>. An extension can be so lightweight because the browser gives it two things: a <strong>clear API</strong> (the extension can read/write the page, make requests—corresponding to the <strong>SDK client</strong> opencode gives the plugin) and a set of <strong>event hooks</strong> ("when a tab opens," "before a network request fires"—corresponding to opencode's <strong>Hooks</strong>). The extension just says "<strong>when something happens, please call my logic</strong>," and the host calls it back at the right moment. opencode's plugins are exactly the same: you declare "<strong>call me before a tool executes</strong>," "<strong>let me tweak the chat params before they're finalized</strong>," and opencode runs your hook at those moments. <strong>The host needn't know which plugins exist, and plugins needn't modify the host—both deal only through the "API + hooks" contract</strong>, so the ecosystem can grow wildly without touching the core.
</div>

<h2>A plugin is a function returning hooks</h2>
<p>opencode's plugin system is astonishingly plain. Look at that example plugin in the public package <span class="mono">@opencode-ai/plugin</span>—it's just these few lines:</p>
<pre class="code"><span class="kw">import</span> { Plugin, tool } <span class="kw">from</span> <span class="st">"@opencode-ai/plugin"</span>

<span class="kw">export const</span> ExamplePlugin: Plugin = <span class="kw">async</span> (ctx) =&gt; {
  <span class="kw">return</span> {                                  <span class="cm">// ← return a Hooks object</span>
    tool: {                                 <span class="cm">// register a custom tool</span>
      mytool: <span class="fn">tool</span>({
        description: <span class="st">"This is a custom tool"</span>,
        args: { foo: tool.schema.<span class="fn">string</span>() },
        <span class="kw">async</span> <span class="fn">execute</span>(args) { <span class="kw">return</span> <span class="st">`Hello ${'$'}{args.foo}!`</span> },
      }),
    },
  }
}</pre>
<p>Just that simple: an <span class="mono">async</span> function, take a context <span class="mono">ctx</span>, return an object. The type definition spells it out plainly: <span class="mono">Plugin = (input: PluginInput, options?) =&gt; Promise&lt;Hooks&gt;</span>. <strong>No base class to inherit, no interface methods to implement, no decorator to register</strong>—just "function in, hooks out." This minimalism is itself a kindness: it presses the barrier of "writing a plugin" to nearly zero; anyone who can write a JS function can add their own tool to opencode in five minutes. You needn't first read a thick "plugin development guide," needn't understand an unfamiliar set of framework concepts—as long as you can write an async function returning an object, you already know how to write an opencode plugin; the rest is just looking up which keys you can fill in that hook table. And that passed-in <span class="mono">input</span> (<span class="mono">PluginInput</span>) is the <strong>"toolbox"</strong> opencode hands the plugin, generous beyond imagination:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">client</div><div class="c-txt">opencode's <strong>SDK client</strong>—the plugin can in turn call opencode's own API (read sessions, send messages…)</div></div>
  <div class="cell"><div class="c-tag">project / directory / worktree</div><div class="c-txt">the current project, directory, worktree—the plugin knows where it's working</div></div>
  <div class="cell"><div class="c-tag">$ (Bun shell)</div><div class="c-txt">a ready-to-use shell, the plugin can run external commands directly</div></div>
  <div class="cell"><div class="c-tag">serverUrl / experimental_workspace</div><div class="c-txt">server address, a hook to register workspace adapters</div></div>
</div>
<p>The most eye-opening thing in this <span class="mono">input</span> is that <span class="mono">client</span>—<strong>opencode hands its entire API client into the plugin's hands</strong>. This means the plugin isn't a "sidekick" that can only passively respond to hooks, but a full citizen that can <strong>actively operate opencode</strong>: within a hook it can read the current session's messages, send a new message into the session, query config… Paired with that Bun shell <span class="mono">$</span>, the plugin can even run arbitrary external commands and bring results back. <strong>Giving the plugin "the host's API + a shell" equals giving it all the capital to "sense opencode, drive opencode, and reach out to the external world"</strong>—exactly the generosity a powerful plugin system should have.</p>

<h2>Hooks: the points where a plugin hooks into the lifecycle</h2>
<p>That <span class="mono">Hooks</span> object the function returns is where the plugin actually <strong>"plugs into"</strong> opencode. It's a "hook table"—each key is a lifecycle moment, the value is "at that moment please run my logic." These hooks roughly split into a few categories (the next lesson L58 details each one by one; here's the overview):</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">event / config</div><div class="c-txt">when each event fires / when config loads—the most generic observation points</div></div>
  <div class="cell"><div class="c-tag">auth / provider</div><div class="c-txt">register custom auth, custom model providers (hook in a company's internal model gateway)</div></div>
  <div class="cell"><div class="c-tag">chat.message / params / headers</div><div class="c-txt">after a chat message, before params finalized, before headers finalized—rewrite the request to the model</div></div>
  <div class="cell"><div class="c-tag">tool.execute.before / after</div><div class="c-txt">before/after tool execution—audit, tweak args, tweak results (incl. tool.definition to alter the tool's description)</div></div>
  <div class="cell"><div class="c-tag">permission.ask</div><div class="c-txt">when permission is asked—the plugin can change the verdict (allow/ask/deny), implementing a custom policy</div></div>
</div>
<p>This table covers nearly every key joint of the agent's operation: from "what to say to the model" (chat.*), to "may it act" (permission.ask), to "how a tool runs" (tool.*), to "which model to connect" (provider). <strong>A plugin need only fill in the few cells it cares about</strong>—want auditing, fill <span class="mono">tool.execute.before</span>; want to connect an internal model, fill <span class="mono">provider</span>; want a custom permission policy, fill <span class="mono">permission.ask</span>, leave the rest blank. This "<strong>one hook table, fill cells on demand</strong>" design is <strong>the same soul</strong> as the built-in provider plugins you saw in L47 (<span class="mono">PluginV2.define</span> returning a hook table): opencode uses this mechanism internally to connect models and externally to connect your extensions—isomorphic inside and out, learn one and master both.</p>

<h2>From config to runtime: how plugins are loaded</h2>
<p>The plugin is written; how does opencode find and run it? The answer is <strong>config-driven + dynamic loading</strong>. In the config's <span class="mono">plugin</span> array you list the plugins to use (an npm package name, or a local file path, optionally with options), and the loader in <span class="mono">plugin/loader.ts</span> brings them into place one by one:</p>
<div class="flow">
  <div class="f-node">config <span class="mono">plugin: [...]</span><br><small>npm name / local path</small></div>
  <div class="f-arrow">resolve →</div>
  <div class="f-node">resolve + install if needed<br><small>npm install, find entry</small></div>
  <div class="f-arrow">import →</div>
  <div class="f-node">dynamic import module<br><small>get the Plugin function</small></div>
  <div class="f-arrow">call →</div>
  <div class="f-node">Plugin(input)→Hooks<br><small>hooks hung into lifecycle</small></div>
</div>
<p>The loader's robustness hides in the <strong>several retryable stages</strong> it splits this chain into:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">install</span><span class="t-txt">if an npm package, install it first (network/version may fail→retryable)</span></div>
  <div class="t-row"><span class="t-num">entry</span><span class="t-txt">find the module's import entry</span></div>
  <div class="t-row"><span class="t-num">compatibility</span><span class="t-txt">check version compatibility</span></div>
  <div class="t-row"><span class="t-num">load</span><span class="t-txt">actually <span class="mono">import</span> the module, get the Plugin function</span></div>
</div>
<p>Each stage may fail for network, version, etc. reasons; the loader retries retryable failures per stage and reports uniformly. Finally <span class="mono">loadExternal</span> resolves and loads all configured plugins <strong>in parallel</strong>. This "staged, retryable, parallel" design is because plugin loading touches opencode's least-controllable boundary—<strong>third-party code + network install</strong>: the package may not install, the entry may not be found, the version may not be compatible. Splitting this error-prone chain into clear stages, each independently retried and reported, is the pragmatic balance between "opening outward" and "staying robust"—<strong>open the door to welcome third parties, but never let one un-installable plugin drag down the whole startup.</strong></p>
<p>Speaking of which, you may recall L47's built-in provider plugin system (<span class="mono">PluginV2.define</span>). How do they relate? Side by side it's clear:</p>
<div class="cols">
  <div class="col"><h4>internal PluginV2 (L47)</h4><p>the internal mechanism opencode uses <strong>itself</strong> to connect thirty-some model providers; <span class="mono">PluginV2.define({id, effect→hooks})</span>, compiled into opencode's source. For "opencode's core developers."</p></div>
  <div class="col"><h4>public Plugin (L57)</h4><p>the public extension API opencode gives <strong>third parties/you</strong> (<span class="mono">@opencode-ai/plugin</span>); <span class="mono">(input)=&gt;Promise&lt;Hooks&gt;</span>, loaded from config. For "opencode's users and ecosystem."</p></div>
</div>
<p>The two share a soul—<strong>both are "a thing that returns a hook table"</strong>, only one inward, one outward. This is exactly good architecture's self-consistency: opencode connecting its own models and you connecting your own extensions use the <strong>same "fill the hook table" idea</strong>, consistent inside and out. With this door, the things you can do are myriad:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">audit / compliance</div><div class="c-txt"><span class="mono">tool.execute.before</span> log every tool call, intercept dangerous operations</div></div>
  <div class="cell"><div class="c-tag">connect internal models</div><div class="c-txt"><span class="mono">provider</span>/<span class="mono">auth</span> hook in a company's private model gateway and auth</div></div>
  <div class="cell"><div class="c-tag">custom tools</div><div class="c-txt"><span class="mono">tool</span> register new tools that query internal systems, call proprietary APIs</div></div>
  <div class="cell"><div class="c-tag">custom permission policy</div><div class="c-txt"><span class="mono">permission.ask</span> auto allow/deny per company rules</div></div>
</div>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>This lesson opens opencode's door to extension—the plugin system that lets third parties, external tools, and you plug capabilities in:</p>
  <ul>
    <li><strong>plugin = a function returning a hook table</strong> (<span class="mono">@opencode-ai/plugin</span>'s <span class="mono">Plugin = (input, options?) =&gt; Promise&lt;Hooks&gt;</span>): no class, no inheritance, no boilerplate, an async function takes <span class="mono">PluginInput</span>, returns <span class="mono">Hooks</span>. The example plugin registers a custom tool in a few lines.</li>
    <li><strong>PluginInput = a generous toolbox</strong>: <span class="mono">client</span> (opencode SDK client, the plugin can call opencode's API back), project/directory/worktree, <span class="mono">$</span> (Bun shell to run commands), serverUrl, experimental_workspace. Giving the plugin "host API + shell" = it can sense and drive opencode, and reach the outside.</li>
    <li><strong>Hooks = lifecycle plug-in points</strong>: event/config, auth/provider, chat.message/params/headers, tool.execute.before/after(+definition), permission.ask—fill cells on demand. Isomorphic with L47's built-in <span class="mono">PluginV2.define</span> returning a hook table.</li>
    <li><strong>config-driven + dynamic loading</strong> (<span class="mono">plugin/loader.ts</span>): config <span class="mono">plugin:[...]</span> (npm name/local path)→loader resolve (install/entry/compatibility/load four retryable stages)→import→<span class="mono">Plugin(input)</span>→hook up Hooks; <span class="mono">loadExternal</span> loads in parallel. Staged retry = open outward yet stay robust.</li>
  </ul>
  <p>The door is open—you now know what a plugin "is, how to write, how it's loaded." But exactly <strong>when each hook in that <span class="mono">Hooks</span> table fires, what it can change, how it's typically used</strong> is still an outline. The next lesson (L58) <strong>details these hooks one by one</strong>: how auth/provider connect models, how chat.* rewrites requests, how tool.* wraps tools, how permission.ask sets policy—fully lighting up this "plugin plug-in-point map." Further on, L59 covers LSP integration, L60 PTY/shell, L61 ACP and the Location model.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p>The whole "contract" of the plugin system is condensed into a few type definitions in <span class="mono">@opencode-ai/plugin</span> (simplified from source):</p>
  <pre class="code"><span class="cm">// the context a plugin gets: host API + project info + shell</span>
<span class="kw">export type</span> PluginInput = {
  client: <span class="fn">ReturnType</span>&lt;<span class="kw">typeof</span> createOpencodeClient&gt;   <span class="cm">// opencode SDK client</span>
  project: Project
  directory: string
  worktree: string
  serverUrl: URL
  $: BunShell                              <span class="cm">// Bun shell, run commands</span>
}

<span class="cm">// a plugin = an async function taking the context, returning a hook table</span>
<span class="kw">export type</span> Plugin = (input: PluginInput, options?: PluginOptions) =&gt; Promise&lt;Hooks&gt;

<span class="cm">// in config you list plugins like: a name, or [name, options]</span>
<span class="kw">export type</span> Config = { plugin?: Array&lt;string | [string, PluginOptions]&gt; }</pre>
  <p>What's most worth savoring is how this design uses <strong>three utterly plain things—"a function + a context + a hook table"</strong>—to hold up a complete extension ecosystem. Contrast the heavy machinery common in traditional plugin frameworks—inherit an <span class="mono">AbstractPlugin</span> base class, implement a pile of lifecycle methods, use a complex dependency-injection container, configure an XML/JSON manifest—opencode <strong>pares all this down to one function signature</strong>. This minimalism isn't laziness but seeing through that a plugin's essence <strong>need only answer two questions</strong>: "what can you give me?" (the <span class="mono">PluginInput</span> context) and "when do you want to step in?" (the returned <span class="mono">Hooks</span> table). Converge the contract to these two points and the rest is plain JS/TS—no framework jargon to learn, no lifecycle order to memorize. <strong>A good extension mechanism with a barrier so low that "if you can write a function you can write a plugin," yet power so great that it "can connect models, rewrite requests, set permissions, call the host API"—low barrier and high power aren't contradictory, the key is designing a contract both minimal and just-enough.</strong> This also echoes a recurring book aesthetic: the strongest abstraction is often the plainest one (L36's one Tool.make table, L47's one PluginV2.define, L53's one createSimpleContext).</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>plugin = a function returning a hook table</strong>: <span class="mono">Plugin = (input: PluginInput, options?) =&gt; Promise&lt;Hooks&gt;</span> (<span class="mono">@opencode-ai/plugin</span>). No class, no inheritance, no boilerplate, async function in, Hooks out. The example registers a custom tool in a few lines. Barrier so low that "if you can write a function you can write a plugin."</li>
    <li><strong>PluginInput = a generous toolbox</strong>: <span class="mono">client</span> (opencode SDK client→the plugin can call opencode's API back), project/directory/worktree, <span class="mono">$</span> (Bun shell), serverUrl. Giving the plugin "host API + shell" = it can sense + drive opencode + reach the outside, not just passive hooks.</li>
    <li><strong>Hooks = lifecycle plug-in points</strong>: event/config, auth/provider, chat.message/params/headers, tool.execute.before/after(+definition), permission.ask—one table, fill cells on demand. Isomorphic with L47's <span class="mono">PluginV2.define</span> (opencode connects models internally, extensions externally, same mechanism).</li>
    <li><strong>config-driven + dynamic loading</strong> (<span class="mono">plugin/loader.ts</span>): config <span class="mono">plugin:[...]</span> (npm name/local path)→resolve (install/entry/compatibility/load four retryable stages)→import→<span class="mono">Plugin(input)</span>→hook up Hooks; <span class="mono">loadExternal</span> in parallel. Staged retry = open outward (third-party code + network install) yet not dragged down by one bad plugin.</li>
    <li><strong>a minimal contract holds up a complete ecosystem</strong>: a plugin need only answer two questions—"what can you give me" (PluginInput) + "when do you want to step in" (Hooks), the rest is plain JS/TS. Low barrier and high power aren't contradictory. Echoes the book's "the strongest abstraction is often the plainest" (L36/L47/L53).</li>
  </ul>
</div>
""",
}
LESSON_58 = {
    "zh": r"""
<p class="lead">上一课我们知道了一个插件就是「一个返回 <span class="mono">Hooks</span> 钩子表的函数」，也扫了一眼那张表里大致有哪些类别。这一课，我们<strong>逐个钻进这些钩子</strong>，看清三件事：每个钩子<strong>在何时被触发</strong>、<strong>能改什么</strong>、<strong>典型怎么用</strong>。spec 把它们分成五大类：<strong>auth（认证）、provider（模型）、chat（聊天请求）、tool（工具）、permission（权限）</strong>——恰好覆盖了一个 agent 从「接哪家模型」到「和模型说什么」到「能不能动手」到「工具怎么跑」的全链路。读懂这张「插件接入点地图」，你就知道了：想实现任何一个扩展需求，该去填哪一格钩子。</p>
<p>这一课最值得带走的洞见，是所有这些钩子<strong>共享的同一个机制——「改草稿」</strong>。绝大多数钩子的签名都长一个样：<span class="mono">(input, output) =&gt; Promise&lt;void&gt;</span>。注意它<strong>不返回任何值</strong>（返回 <span class="mono">void</span>），而是收<strong>两个</strong>参数：<span class="mono">input</span> 是只读的上下文（告诉你「现在是什么情况」），<span class="mono">output</span> 是一个<strong>可变的「草稿」对象</strong>（你<strong>就地修改它</strong>来施加影响）。背后的触发机制是这样：opencode 先算出一份<strong>默认的 output</strong>，把 <span class="mono">(input, output)</span> 交给每个注册了该钩子的插件，每个插件<strong>在 output 上涂改一笔</strong>，最后 opencode 拿着这份被层层涂改过的 output 继续干活。<strong>插件不是「返回一个新值替换」，而是「在 opencode 递来的草稿上改几笔」</strong>——这个「传入可变草稿、就地修改」的模式，你在 L54 的 <span class="mono">produce</span>、L47 的 provider 钩子里都见过，这一课它成了整个插件系统的统一语言。</p>

<div class="card analogy">
  <div class="tag">📝 生活类比</div>
  把插件钩子想象成一份<strong>在流水线上传递的「申请单」</strong>。opencode 先填好一份<strong>默认的申请单</strong>（比如「发给模型的请求：温度 0.7、这些消息、这些请求头」），然后把这份单子<strong>依次递给每一个插件</strong>过目。每个插件都可以<strong>在单子上改几笔</strong>——审计插件在「工具调用」那栏盖个章记录一下、合规插件把「危险操作」那栏的批准改成「拒绝」、某模型插件在「请求头」那栏补一行特殊标记。改完，单子<strong>传给下一个插件</strong>，最后回到 opencode 手里——它照着这份<strong>被大家改过的最终单子</strong>去执行。关键在于：<strong>插件从不自己另开一张新单子，只在 opencode 给的这张上涂改</strong>。这样既保证了 opencode 始终掌着「单子的最终形态」（它给默认值、它拿最终结果），又让每个插件都能<strong>精准地只改自己关心的那一栏</strong>、互不干扰。这份「传递的申请单」，就是那个 <span class="mono">output</span> 草稿对象。
</div>

<h2>统一机制：trigger 一份草稿，插件层层涂改</h2>
<p>先看清这个贯穿所有钩子的机制。opencode 在代码里到处是这样的调用：<span class="mono">plugin.trigger(钩子名, input, 默认output)</span>。以「定聊天参数」为例（<span class="mono">session/llm/request.ts</span>）：opencode 先备好默认参数，<span class="mono">trigger("chat.params", {model,…}, {temperature, topP, …})</span> 把它交给插件们，插件改完，opencode 拿最终值发给模型。这条「默认→涂改→采用」的链是这样跑的：</p>
<div class="flow">
  <div class="f-node">opencode 备默认 output<br><small>如 temperature:0.7</small></div>
  <div class="f-arrow">trigger →</div>
  <div class="f-node">插件 A 改 output<br><small>(input,output)=&gt;void</small></div>
  <div class="f-arrow">接力 →</div>
  <div class="f-node">插件 B 再改<br><small>就地涂改同一草稿</small></div>
  <div class="f-arrow">回到 →</div>
  <div class="f-node">opencode 用最终 output<br><small>发给模型/执行</small></div>
</div>
<p>这个机制有几个值得品的设计抉择。其一，<strong>opencode 永远给默认值、拿最终值</strong>——主动权始终在宿主手里，插件只是「在中间插一脚」，就算一个插件都没装，那份默认 output 也能正常工作。其二，<strong>多个插件能叠加</strong>：它们依次涂改同一份草稿，后面的看得到前面改的结果（像 L41 权限、L44 配置的「层层叠加」）。其三，<strong>钩子返回 void、靠副作用（改 output）生效</strong>，而非返回新值——这避免了「插件返回了个残缺对象怎么办」的麻烦：草稿的<strong>完整结构由 opencode 保证</strong>，插件只负责往里改几个字段。这是个朴素却老练的接口设计：<strong>用「传入可变草稿」代替「返回新值」，既给了插件充分的修改权，又让宿主牢牢掌着数据结构的完整性与主动权。</strong></p>
<p>把五大类钩子摊成一张「接入点地图」，你就能一眼定位「想做某件事该填哪一格」：</p>
<table class="t">
  <tr><th>类别</th><th>钩子</th><th>能改什么</th></tr>
  <tr><td>观察</td><td>event / config / dispose</td><td>每个事件 / 配置加载 / 插件卸载——纯观察与清理</td></tr>
  <tr><td>chat（请求）</td><td>chat.message / params / headers / *.transform</td><td>进来的消息、模型参数、请求头、系统提示与消息列表</td></tr>
  <tr><td>tool（工具）</td><td>tool / execute.before / after / shell.env</td><td>注册新工具、执行前 args、执行后结果、命令环境变量</td></tr>
  <tr><td>permission</td><td>permission.ask</td><td>一次权限的裁决（allow / ask / deny）</td></tr>
  <tr><td>auth / provider</td><td>auth / provider</td><td>自定义认证方式、自定义模型 provider</td></tr>
</table>
<p>这张表里最容易被忽略、却最基础的，是「<strong>观察</strong>」类那三个钩子——它们不改请求、不改裁决，只是<strong>在事情发生时被通知</strong>：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">event</div><div class="c-txt">每个事件发生时被叫到——最通用的「全局监听器」，做日志、做指标、做外部同步</div></div>
  <div class="cell"><div class="c-tag">config</div><div class="c-txt">配置加载完成时——插件可据此初始化自己</div></div>
  <div class="cell"><div class="c-tag">dispose</div><div class="c-txt">插件卸载时——清理资源（关连接、停后台任务）</div></div>
</div>

<h2>chat 与 tool：拦在「请求」与「执行」前后</h2>
<p>最常用的钩子，集中在「<strong>发往模型的请求</strong>」和「<strong>工具的执行</strong>」这两个最关键的关节上。先看 <strong>chat.*</strong> 这一组——它们让你拦在「opencode 把请求发给模型」之前，改写这个请求的方方面面：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">chat.message</div><div class="c-txt">收到一条新消息时——观察/调整进来的 message 与 parts</div></div>
  <div class="cell"><div class="c-tag">chat.params</div><div class="c-txt">改发给模型的参数：temperature/topP/topK/maxOutputTokens/options</div></div>
  <div class="cell"><div class="c-tag">chat.headers</div><div class="c-txt">改 HTTP 请求头（如补一个鉴权头、特性开关头）</div></div>
  <div class="cell"><div class="c-tag">experimental.chat.system/messages.transform</div><div class="c-txt">重写整个系统提示数组 / 整个消息列表</div></div>
</div>
<p>这组钩子的威力，opencode 自己就是最好的证明：内置的 Cloudflare、GitHub Copilot、OpenAI Codex 等插件，全都实现了 <span class="mono">"chat.params"</span> 来给自家模型调特定参数。<strong>opencode 用同一套公开钩子来接自己的模型——这本身就是对这套机制能力的最强背书。</strong>再看 <strong>tool.*</strong> 这一组，它们拦在「工具执行」前后：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">tool（注册）</div><div class="c-txt">直接注册一个全新的自定义工具（L57 例子插件就用这个）</div></div>
  <div class="cell"><div class="c-tag">tool.execute.before</div><div class="c-txt">工具执行<strong>前</strong>——改 args（审计、改写参数、注入默认值）</div></div>
  <div class="cell"><div class="c-tag">tool.execute.after</div><div class="c-txt">工具执行<strong>后</strong>——改 output（title/output/metadata，后处理结果）</div></div>
  <div class="cell"><div class="c-tag">shell.env</div><div class="c-txt">改 shell 命令的环境变量（往 output.env 注入）</div></div>
</div>
<p><span class="mono">tool.execute.before</span> 和 <span class="mono">after</span> 像一对「<strong>三明治</strong>」，把工具的真正执行<strong>夹在中间</strong>：before 能在工具跑起来前最后改一次参数（或记录下来做审计），after 能在工具跑完后对结果再加工一道。这正是做「<strong>横切关注点</strong>」（审计、日志、安全过滤、结果脱敏）的理想位置——你不必改任何一个具体工具的代码，只要在这对钩子里写一遍逻辑，就<strong>一次性套用到所有工具</strong>上。试想若没有这对钩子，你想给「每个工具调用都记一笔审计日志」，就得去改 read、write、bash、grep…每一个工具的代码——既繁琐又容易漏。而 before/after 这对横切钩子，把这件事收敛成<strong>一处编写、处处生效</strong>。而 <span class="mono">shell.env</span> 则是个小而实用的口子：它让插件能给 opencode 跑的 shell 命令<strong>注入环境变量</strong>（下一课 L60 的 PTY environment 正与此相关）——比如给所有命令注入一个内部代理地址、或一个 CI 标记。</p>

<h2>permission 与 auth/provider：守门与接源</h2>
<p>最后两类钩子，管的是 agent 的「<strong>权力</strong>」与「<strong>来源</strong>」。<span class="mono">permission.ask</span> 是个尤其有分量的钩子：每当 opencode 要为某个动作征求权限（回想 L41 的 allow/ask/deny），这个钩子就被触发，插件能<strong>直接改写那个裁决</strong>：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">opencode 要执行某动作 → 按 L41 规则算出默认裁决，填进 output.status</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">trigger <span class="mono">permission.ask</span>(input=Permission, output={status})</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">插件按自定义策略改 <span class="mono">output.status</span>=「allow / ask / deny」</span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">opencode 照最终 status 放行 / 询问 / 拒绝</span></div>
</div>
<p>这把第 41 课的权限系统<strong>向外敞开了一道口</strong>：企业可以写一个插件，把「凡是在生产目录下的写操作一律 deny」「凡是只读命令一律 allow」这样的<strong>公司级安全策略</strong>，用代码精确表达——而不必依赖用户每次手动点选。<span class="mono">permission.ask</span> 让 opencode 的权限从「内置规则 + 用户即时决定」扩展成「<strong>内置规则 + 用户决定 + 插件策略</strong>」三层，把安全管控的能力交给了组织。而 <span class="mono">auth</span> 与 <span class="mono">provider</span> 两个钩子，则管「<strong>agent 的脑从哪来</strong>」：<span class="mono">auth</span> 注册自定义认证方式（OAuth、API key…）、<span class="mono">provider</span> 注册自定义模型 provider——这让你能把<strong>公司内部的私有模型网关</strong>接进 opencode，像用官方模型一样用自己的模型。<strong>从守住「能不能动手」（permission）到接通「用谁的脑子」（auth/provider），插件钩子把 agent 最敏感的两端，都变成了可由组织定制的策略。</strong></p>

<div class="card macro">
  <div class="tag">🗺️ 宏观视角</div>
  <p>这一课点亮了那张「插件接入点地图」——五大类钩子逐个看清：</p>
  <ul>
    <li><strong>统一机制=「改草稿」</strong>：钩子签名 <span class="mono">(input, output) =&gt; Promise&lt;void&gt;</span>，返回 void、靠就地改 <span class="mono">output</span> 生效。<span class="mono">plugin.trigger(名, input, 默认output)</span>：opencode 给默认值→各插件层层涂改同一草稿→opencode 拿最终值。宿主掌主动权与结构完整性，插件只改关心的字段（同 L54 produce、L41/L44 层叠）。</li>
    <li><strong>chat.*（请求前拦截）</strong>：chat.message(进来的消息)、chat.params(temperature/topP/maxOutputTokens/options)、chat.headers(请求头)、experimental.chat.system/messages.transform(重写系统提示/消息列表)。opencode 内置 Cloudflare/Copilot/Codex 插件都用 chat.params 接自家模型。</li>
    <li><strong>tool.*（执行前后夹）</strong>：tool(注册新工具)、tool.execute.before(改 args)、tool.execute.after(改结果 title/output/metadata)、shell.env(注入命令环境变量)。before/after 像三明治夹住工具执行，是做审计/日志/安全过滤等横切关注点的理想位置——一处逻辑套用所有工具。</li>
    <li><strong>permission.ask + auth/provider</strong>：permission.ask 改裁决(allow/ask/deny)→把 L41 权限向外敞开，企业可写代码级安全策略；auth/provider 注册自定义认证与模型 provider→接公司私有模型网关。守门(权力)+接源(脑子)，agent 最敏感两端皆可组织定制。</li>
  </ul>
  <p>插件这扇门的里里外外，至此讲透了（L57 是什么/怎么加载、L58 各钩子细节）。接下来三课转向 opencode 与<strong>具体外部系统</strong>的集成：L59 讲 <strong>LSP</strong>（接语言服务器，给 agent 真正的「代码智能」——诊断、跳转），L60 讲 <strong>PTY 与 shell</strong>（终端进程管理、环境叠加，正接本课的 shell.env），L61 讲 <strong>ACP 与 Location 抽象</strong>（opencode 作为 ACP server、会话跨位置移动）。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p>几个钩子的类型签名并排一看，「改草稿」这个统一模式就跃然纸上（简化自 <span class="mono">@opencode-ai/plugin</span> 的 <span class="mono">Hooks</span>）：</p>
  <pre class="code"><span class="cm">// 改发给模型的参数：input 只读，output 是可变草稿</span>
<span class="st">"chat.params"</span>?: (
  input: { sessionID, agent, model, provider, message },
  output: { temperature, topP, topK, maxOutputTokens, options },  <span class="cm">// ← 就地改</span>
) =&gt; Promise&lt;<span class="kw">void</span>&gt;

<span class="cm">// 改权限裁决：把 output.status 改成 allow/deny/ask</span>
<span class="st">"permission.ask"</span>?: (input: Permission, output: { status: <span class="st">"ask"</span>|<span class="st">"deny"</span>|<span class="st">"allow"</span> }) =&gt; Promise&lt;<span class="kw">void</span>&gt;

<span class="cm">// 工具执行前改 args / 执行后改结果</span>
<span class="st">"tool.execute.before"</span>?: (input: { tool, sessionID, callID }, output: { args }) =&gt; Promise&lt;<span class="kw">void</span>&gt;
<span class="st">"tool.execute.after"</span>?: (input: { tool, …, args }, output: { title, output, metadata }) =&gt; Promise&lt;<span class="kw">void</span>&gt;</pre>
  <p>盯着这四个签名，一个深刻的一致性浮现出来：<strong>它们全是 <span class="mono">(只读 input, 可变 output) =&gt; void</span> 的同一个形状。</strong>无论你想改的是「发给模型的温度」、「一次权限的裁决」、还是「一个工具的参数与结果」，<strong>动作都一样——读 input 看情况、改 output 施影响</strong>。这种「<strong>所有钩子同构</strong>」的设计威力极大：你学会了一个钩子怎么用，就等于学会了所有钩子怎么用；opencode 内部触发钩子的代码，也能用<strong>同一个 <span class="mono">trigger(名, input, output)</span> 模板</strong>处理所有类型，无需为每个钩子写特殊逻辑。这正是「<strong>统一形状</strong>」的复利——它同时降低了「插件作者学习的成本」和「宿主实现的复杂度」。对比一下若每个钩子各设计一套自己的调用约定（有的返回值、有的回调、有的 emit 事件），插件作者要逐个记、宿主要逐个适配，复杂度会爆炸。<strong>把一大类「拦截/修改」的需求，统一收敛到「读 input、改 output、返回 void」一个形状里</strong>——这又是全书反复礼赞的那种审美：用一个想透了的统一模子，把一整类问题刻成同形，于是处处易学、易实现、难出错（L36 Tool.make、L47 PluginV2、L53 createSimpleContext、L56 DialogSelect 皆然）。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>统一机制=「改草稿」</strong>：绝大多数钩子签名 <span class="mono">(input 只读, output 可变) =&gt; Promise&lt;void&gt;</span>，返回 void、靠就地改 output 生效。<span class="mono">plugin.trigger(名, input, 默认output)</span>：opencode 给默认值→各插件层层涂改同一草稿→opencode 拿最终值。所有钩子同构=学一个会全部。</li>
    <li><strong>chat.*（请求前拦截）</strong>：chat.message、chat.params(temperature/topP/maxOutputTokens/options)、chat.headers、experimental.chat.system/messages.transform。opencode 内置 Cloudflare/Copilot/Codex 插件都用 chat.params 接自家模型（自证机制威力）。</li>
    <li><strong>tool.*（执行前后夹）</strong>：tool(注册新工具)、tool.execute.before(改 args)、tool.execute.after(改 title/output/metadata)、shell.env(注入命令环境变量，接 L60)。before/after 三明治夹住执行=审计/日志/安全过滤等横切关注点的理想位，一处逻辑套所有工具。</li>
    <li><strong>permission.ask</strong>：改裁决 allow/ask/deny→把 L41 权限向外敞开，企业可写代码级安全策略（生产目录写一律 deny 等），权限=内置规则+用户决定+插件策略三层。</li>
    <li><strong>auth/provider</strong>：注册自定义认证(OAuth/API key)与模型 provider→接公司私有模型网关。守门(permission)+接源(auth/provider)，agent 最敏感两端皆可组织定制。统一形状的复利=学习成本与实现复杂度双降（同 L36/L47/L53/L56）。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Last lesson we learned a plugin is "a function returning a <span class="mono">Hooks</span> hook table," and glanced at roughly which categories the table holds. This lesson, we <strong>drill into these hooks one by one</strong>, getting clear on three things: when each hook <strong>fires</strong>, what it <strong>can change</strong>, and how it's <strong>typically used</strong>. The spec splits them into five categories: <strong>auth, provider, chat (the chat request), tool, permission</strong>—exactly covering an agent's whole chain from "which model to connect" to "what to say to the model" to "may it act" to "how a tool runs." Grasp this "plugin plug-in-point map" and you'll know: to implement any extension need, which hook cell to fill.</p>
<p>The insight most worth taking away is the single mechanism all these hooks <strong>share—"editing a draft."</strong> The vast majority of hooks have the same signature: <span class="mono">(input, output) =&gt; Promise&lt;void&gt;</span>. Note it <strong>returns nothing</strong> (returns <span class="mono">void</span>) but takes <strong>two</strong> arguments: <span class="mono">input</span> is read-only context (telling you "what the situation is now"), <span class="mono">output</span> is a <strong>mutable "draft" object</strong> (you <strong>modify it in place</strong> to exert influence). The trigger mechanism behind it: opencode first computes a <strong>default output</strong>, hands <span class="mono">(input, output)</span> to each plugin that registered this hook, each plugin <strong>marks up the output</strong>, and finally opencode takes this layer-by-layer marked-up output and carries on. <strong>A plugin doesn't "return a new value to replace" but "marks up a few strokes on the draft opencode handed it"</strong>—this "pass a mutable draft, modify in place" pattern, which you saw in L54's <span class="mono">produce</span> and L47's provider hooks, here becomes the unified language of the whole plugin system.</p>

<div class="card analogy">
  <div class="tag">📝 Analogy</div>
  Picture plugin hooks as an <strong>"application form passed down an assembly line."</strong> opencode first fills in a <strong>default form</strong> (e.g. "request to the model: temperature 0.7, these messages, these headers"), then <strong>hands this form to each plugin in turn</strong> for review. Each plugin can <strong>mark up a few strokes on the form</strong>—the audit plugin stamps the "tool call" box for the record, the compliance plugin changes the "dangerous operation" box's approval to "deny," some model plugin adds a special tag in the "headers" box. After editing, the form <strong>passes to the next plugin</strong>, and finally returns to opencode—which executes per this <strong>final form everyone edited</strong>. The key: <strong>a plugin never opens a new form of its own, only marks up the one opencode gave</strong>. This both ensures opencode always holds "the form's final shape" (it gives the default, it takes the final result) and lets each plugin <strong>precisely edit only the box it cares about</strong>, without interfering. This "passed application form" is that <span class="mono">output</span> draft object.
</div>

<h2>The unified mechanism: trigger a draft, plugins mark up layer by layer</h2>
<p>First see clearly this mechanism running through all hooks. opencode's code is full of calls like: <span class="mono">plugin.trigger(hookName, input, defaultOutput)</span>. Take "setting chat params" (<span class="mono">session/llm/request.ts</span>): opencode prepares the default params, <span class="mono">trigger("chat.params", {model,…}, {temperature, topP, …})</span> hands it to the plugins, the plugins edit, opencode takes the final value and sends it to the model. This "default→mark up→adopt" chain runs like:</p>
<div class="flow">
  <div class="f-node">opencode prepares default output<br><small>e.g. temperature:0.7</small></div>
  <div class="f-arrow">trigger →</div>
  <div class="f-node">plugin A edits output<br><small>(input,output)=&gt;void</small></div>
  <div class="f-arrow">relay →</div>
  <div class="f-node">plugin B edits more<br><small>marks up the same draft in place</small></div>
  <div class="f-arrow">back to →</div>
  <div class="f-node">opencode uses final output<br><small>send to model/execute</small></div>
</div>
<p>This mechanism has a few design choices worth savoring. First, <strong>opencode always gives the default and takes the final</strong>—the initiative is always in the host's hands, plugins just "step in the middle," and even with no plugins installed, that default output works fine. Second, <strong>multiple plugins can stack</strong>: they mark up the same draft in turn, later ones seeing earlier edits (like L41 permission, L44 config's "layered stacking"). Third, <strong>hooks return void, taking effect by side effect (editing output)</strong> rather than returning a new value—this avoids the trouble of "what if a plugin returns a defective object": the draft's <strong>complete structure is guaranteed by opencode</strong>, the plugin only edits a few fields into it. This is a plain yet seasoned interface design: <strong>using "pass a mutable draft" instead of "return a new value" gives plugins ample editing power while letting the host firmly hold the data structure's integrity and initiative.</strong></p>
<p>Spreading the five categories into a "plug-in-point map," you can locate at a glance "to do something, which cell to fill":</p>
<table class="t">
  <tr><th>category</th><th>hooks</th><th>what it can change</th></tr>
  <tr><td>observe</td><td>event / config / dispose</td><td>each event / config loaded / plugin unloaded—pure observation and cleanup</td></tr>
  <tr><td>chat (request)</td><td>chat.message / params / headers / *.transform</td><td>incoming message, model params, headers, system prompts and message list</td></tr>
  <tr><td>tool</td><td>tool / execute.before / after / shell.env</td><td>register new tools, pre-execution args, post-execution result, command env vars</td></tr>
  <tr><td>permission</td><td>permission.ask</td><td>a permission's verdict (allow / ask / deny)</td></tr>
  <tr><td>auth / provider</td><td>auth / provider</td><td>custom auth methods, custom model providers</td></tr>
</table>
<p>The most easily overlooked yet most basic in this table are the three "<strong>observe</strong>" hooks—they don't change the request or the verdict, just <strong>get notified when things happen</strong>:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">event</div><div class="c-txt">called when each event fires—the most generic "global listener," for logging, metrics, external sync</div></div>
  <div class="cell"><div class="c-tag">config</div><div class="c-txt">when config finishes loading—the plugin can initialize itself accordingly</div></div>
  <div class="cell"><div class="c-tag">dispose</div><div class="c-txt">when the plugin unloads—clean up resources (close connections, stop background tasks)</div></div>
</div>

<h2>chat and tool: intercepting before/after "request" and "execution"</h2>
<p>The most-used hooks concentrate on the two most key joints: "<strong>the request sent to the model</strong>" and "<strong>tool execution</strong>." First the <strong>chat.*</strong> group—they let you intercept before "opencode sends the request to the model," rewriting every aspect of this request:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">chat.message</div><div class="c-txt">when a new message arrives—observe/adjust the incoming message and parts</div></div>
  <div class="cell"><div class="c-tag">chat.params</div><div class="c-txt">change params sent to the model: temperature/topP/topK/maxOutputTokens/options</div></div>
  <div class="cell"><div class="c-tag">chat.headers</div><div class="c-txt">change HTTP request headers (e.g. add an auth header, a feature-flag header)</div></div>
  <div class="cell"><div class="c-tag">experimental.chat.system/messages.transform</div><div class="c-txt">rewrite the whole system-prompt array / the whole message list</div></div>
</div>
<p>This group's power is best proven by opencode itself: built-in plugins like Cloudflare, GitHub Copilot, OpenAI Codex all implement <span class="mono">"chat.params"</span> to tune specific params for their own models. <strong>opencode uses the same public hooks to connect its own models—itself the strongest endorsement of this mechanism's capability.</strong> Now the <strong>tool.*</strong> group, intercepting before/after "tool execution":</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">tool (register)</div><div class="c-txt">directly register a brand-new custom tool (L57's example plugin uses this)</div></div>
  <div class="cell"><div class="c-tag">tool.execute.before</div><div class="c-txt"><strong>before</strong> tool execution—change args (audit, rewrite params, inject defaults)</div></div>
  <div class="cell"><div class="c-tag">tool.execute.after</div><div class="c-txt"><strong>after</strong> tool execution—change output (title/output/metadata, post-process the result)</div></div>
  <div class="cell"><div class="c-tag">shell.env</div><div class="c-txt">change shell commands' env vars (inject into output.env)</div></div>
</div>
<p><span class="mono">tool.execute.before</span> and <span class="mono">after</span> are like a "<strong>sandwich</strong>," <strong>sandwiching</strong> the tool's actual execution in between: before can make one last change to args before the tool runs (or record them for audit), after can rework the result once the tool finishes. This is the ideal spot for "<strong>cross-cutting concerns</strong>" (audit, logging, security filtering, result redaction)—you needn't change any concrete tool's code, just write the logic once in this pair of hooks to <strong>apply it to all tools at once</strong>. Imagine without this pair, to "log an audit entry for every tool call" you'd have to change read, write, bash, grep… every tool's code—both tedious and easily missed. The before/after cross-cutting pair converges this into <strong>write once, take effect everywhere</strong>. And <span class="mono">shell.env</span> is a small, practical hatch: it lets plugins <strong>inject env vars</strong> into the shell commands opencode runs (next lesson L60's PTY environment relates to this exactly)—e.g. inject an internal proxy address, or a CI marker, into all commands.</p>

<h2>permission and auth/provider: gatekeeping and connecting sources</h2>
<p>The last two hook categories manage the agent's "<strong>power</strong>" and "<strong>sources</strong>." <span class="mono">permission.ask</span> is an especially weighty hook: whenever opencode asks for permission for some action (recall L41's allow/ask/deny), this hook fires, and the plugin can <strong>directly rewrite that verdict</strong>:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">opencode is about to execute an action → computes the default verdict per L41 rules, fills output.status</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">trigger <span class="mono">permission.ask</span>(input=Permission, output={status})</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">the plugin changes <span class="mono">output.status</span>="allow / ask / deny" per its custom policy</span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">opencode allows / asks / denies per the final status</span></div>
</div>
<p>This <strong>opens a hatch outward</strong> in lesson 41's permission system: an enterprise can write a plugin expressing <strong>company-level security policies</strong> precisely in code—"any write under the production directory is always denied," "any read-only command is always allowed"—without relying on the user clicking each time. <span class="mono">permission.ask</span> extends opencode's permissions from "built-in rules + the user's instant decision" to "<strong>built-in rules + user decision + plugin policy</strong>," three layers, handing security control to the organization. And the <span class="mono">auth</span> and <span class="mono">provider</span> hooks manage "<strong>where the agent's brain comes from</strong>": <span class="mono">auth</span> registers custom auth methods (OAuth, API key…), <span class="mono">provider</span> registers custom model providers—letting you connect a <strong>company's private model gateway</strong> into opencode, using your own model like an official one. <strong>From guarding "may it act" (permission) to connecting "whose brain to use" (auth/provider), plugin hooks turn the agent's two most sensitive ends both into policies the organization can customize.</strong></p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>This lesson lights up that "plugin plug-in-point map"—the five hook categories seen one by one:</p>
  <ul>
    <li><strong>unified mechanism = "edit a draft"</strong>: hook signature <span class="mono">(input, output) =&gt; Promise&lt;void&gt;</span>, returns void, takes effect by editing <span class="mono">output</span> in place. <span class="mono">plugin.trigger(name, input, defaultOutput)</span>: opencode gives the default→each plugin marks up the same draft in turn→opencode takes the final value. The host holds initiative and structural integrity, the plugin edits only the fields it cares about (like L54 produce, L41/L44 stacking).</li>
    <li><strong>chat.* (intercept before request)</strong>: chat.message (incoming message), chat.params (temperature/topP/maxOutputTokens/options), chat.headers (request headers), experimental.chat.system/messages.transform (rewrite system prompts/message list). opencode's built-in Cloudflare/Copilot/Codex plugins all use chat.params to connect their own models.</li>
    <li><strong>tool.* (sandwich before/after execution)</strong>: tool (register a new tool), tool.execute.before (change args), tool.execute.after (change result title/output/metadata), shell.env (inject command env vars). before/after sandwich the tool execution, the ideal spot for cross-cutting concerns like audit/logging/security filtering—one logic applies to all tools.</li>
    <li><strong>permission.ask + auth/provider</strong>: permission.ask changes the verdict (allow/ask/deny)→opens L41 permissions outward, enterprises can write code-level security policies; auth/provider register custom auth and model providers→connect a company's private model gateway. Gatekeeping (power) + connecting sources (brain), both of the agent's most sensitive ends are organization-customizable.</li>
  </ul>
  <p>The inside and outside of the plugin door are now fully covered (L57 what it is/how it loads, L58 each hook's detail). The next three lessons turn to opencode's integration with <strong>concrete external systems</strong>: L59 covers <strong>LSP</strong> (connecting language servers, giving the agent real "code intelligence"—diagnostics, navigation), L60 covers <strong>PTY and shell</strong> (terminal process management, environment stacking, connecting this lesson's shell.env), L61 covers <strong>ACP and the Location model</strong> (opencode as an ACP server, sessions moving across locations).</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p>Several hooks' type signatures side by side make the unified "edit a draft" pattern leap out (simplified from <span class="mono">@opencode-ai/plugin</span>'s <span class="mono">Hooks</span>):</p>
  <pre class="code"><span class="cm">// change params sent to the model: input read-only, output a mutable draft</span>
<span class="st">"chat.params"</span>?: (
  input: { sessionID, agent, model, provider, message },
  output: { temperature, topP, topK, maxOutputTokens, options },  <span class="cm">// ← edit in place</span>
) =&gt; Promise&lt;<span class="kw">void</span>&gt;

<span class="cm">// change the permission verdict: set output.status to allow/deny/ask</span>
<span class="st">"permission.ask"</span>?: (input: Permission, output: { status: <span class="st">"ask"</span>|<span class="st">"deny"</span>|<span class="st">"allow"</span> }) =&gt; Promise&lt;<span class="kw">void</span>&gt;

<span class="cm">// change args before tool execution / change the result after</span>
<span class="st">"tool.execute.before"</span>?: (input: { tool, sessionID, callID }, output: { args }) =&gt; Promise&lt;<span class="kw">void</span>&gt;
<span class="st">"tool.execute.after"</span>?: (input: { tool, …, args }, output: { title, output, metadata }) =&gt; Promise&lt;<span class="kw">void</span>&gt;</pre>
  <p>Staring at these four signatures, a profound consistency surfaces: <strong>they're all the same shape, <span class="mono">(read-only input, mutable output) =&gt; void</span>.</strong> Whether you want to change "the temperature sent to the model," "a permission verdict," or "a tool's args and result," <strong>the action is the same—read input to see the situation, edit output to exert influence</strong>. This "<strong>all hooks isomorphic</strong>" design is hugely powerful: learn how to use one hook and you've learned them all; opencode's hook-triggering code can also handle all types with <strong>the same <span class="mono">trigger(name, input, output)</span> template</strong>, no special logic per hook. This is the compounding of "<strong>a unified shape</strong>"—it lowers both "the plugin author's learning cost" and "the host's implementation complexity" at once. Contrast designing each hook with its own calling convention (some return a value, some a callback, some emit events): plugin authors must memorize each, the host must adapt to each, complexity explodes. <strong>Converging a whole class of "intercept/modify" needs into one shape—"read input, edit output, return void"</strong>—is again the aesthetic the book repeatedly praises: with one well-thought-through unified mold, stamp a whole class of problems into the same shape, so everything's easy to learn, easy to implement, hard to get wrong (L36 Tool.make, L47 PluginV2, L53 createSimpleContext, L56 DialogSelect all so).</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>unified mechanism = "edit a draft"</strong>: the vast majority of hooks have signature <span class="mono">(read-only input, mutable output) =&gt; Promise&lt;void&gt;</span>, return void, take effect by editing output in place. <span class="mono">plugin.trigger(name, input, defaultOutput)</span>: opencode gives the default→each plugin marks up the same draft in turn→opencode takes the final. All hooks isomorphic = learn one, know all.</li>
    <li><strong>chat.* (intercept before request)</strong>: chat.message, chat.params (temperature/topP/maxOutputTokens/options), chat.headers, experimental.chat.system/messages.transform. opencode's built-in Cloudflare/Copilot/Codex plugins all use chat.params to connect their own models (self-proof of the mechanism's power).</li>
    <li><strong>tool.* (sandwich before/after execution)</strong>: tool (register a new tool), tool.execute.before (change args), tool.execute.after (change title/output/metadata), shell.env (inject command env vars, connecting L60). before/after sandwich the execution = ideal spot for cross-cutting concerns like audit/logging/security filtering, one logic applies to all tools.</li>
    <li><strong>permission.ask</strong>: change the verdict allow/ask/deny→opens L41 permissions outward, enterprises can write code-level security policies (any production-dir write always denied, etc.), permission = built-in rules + user decision + plugin policy, three layers.</li>
    <li><strong>auth/provider</strong>: register custom auth (OAuth/API key) and model providers→connect a company's private model gateway. Gatekeeping (permission) + connecting sources (auth/provider), both of the agent's most sensitive ends organization-customizable. The compounding of a unified shape = lowering learning cost and implementation complexity at once (like L36/L47/L53/L56).</li>
  </ul>
</div>
""",
}
LESSON_59 = wip('LSP 集成', 'LSP integration')
LESSON_60 = wip('PTY 与 shell', 'PTY & shell')
LESSON_61 = wip('ACP 与 Location 抽象', 'ACP & the Location model')
