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
LESSON_58 = wip('插件 hooks 详解', 'Plugin hooks in depth')
LESSON_59 = wip('LSP 集成', 'LSP integration')
LESSON_60 = wip('PTY 与 shell', 'PTY & shell')
LESSON_61 = wip('ACP 与 Location 抽象', 'ACP & the Location model')
