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
        <span class="kw">async</span> <span class="fn">execute</span>(args) { <span class="kw">return</span> <span class="st">`Hello ${args.foo}!`</span> },
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
<p>加载器的稳健，藏在它把这条链拆成的<strong>几个清晰阶段</strong>里：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">install</span><span class="t-txt">若是 npm 包，先把它装下来（网络/版本可能失败→可重试）</span></div>
  <div class="t-row"><span class="t-num">entry</span><span class="t-txt">找到模块的导入入口</span></div>
  <div class="t-row"><span class="t-num">compatibility</span><span class="t-txt">检查版本兼容性</span></div>
  <div class="t-row"><span class="t-num">load</span><span class="t-txt">真正 <span class="mono">import</span> 模块、拿到 Plugin 函数</span></div>
</div>
<p>这几步里真正会<strong>重试</strong>的只有 <span class="mono">install</span>（装 npm 包，网络/版本最易抖动）；<span class="mono">loader.ts</span> 的 <span class="mono">isRetryableResolveError</span> 对非 install 阶段一律返回 false，失败就直接透明上报。最后 <span class="mono">loadExternal</span> 把配置里所有插件<strong>并行</strong>解析加载。这种「分阶段、可重试、并行」的设计，是因为插件加载触及了 opencode 最不可控的边界——<strong>第三方代码 + 网络安装</strong>：包可能没装上、入口可能找不到、版本可能不兼容。把这条易错的链拆成清晰的阶段、每段独立重试与报错，就是在「向外敞开」与「自身稳健」之间的务实平衡——<strong>敞开大门迎接第三方，但绝不让一个装不上的插件拖垮整个启动。</strong></p>
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
        <span class="kw">async</span> <span class="fn">execute</span>(args) { <span class="kw">return</span> <span class="st">`Hello ${args.foo}!`</span> },
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
<p>The loader's robustness hides in the <strong>several clear stages</strong> it splits this chain into:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">install</span><span class="t-txt">if an npm package, install it first (network/version may fail→retryable)</span></div>
  <div class="t-row"><span class="t-num">entry</span><span class="t-txt">find the module's import entry</span></div>
  <div class="t-row"><span class="t-num">compatibility</span><span class="t-txt">check version compatibility</span></div>
  <div class="t-row"><span class="t-num">load</span><span class="t-txt">actually <span class="mono">import</span> the module, get the Plugin function</span></div>
</div>
<p>Of these, only <span class="mono">install</span> is retried (installing an npm package — network/version flakiness); <span class="mono">loader.ts</span>'s <span class="mono">isRetryableResolveError</span> returns false for any non-install stage, so other failures surface immediately. Finally <span class="mono">loadExternal</span> resolves and loads all configured plugins <strong>in parallel</strong>. This "staged, retryable, parallel" design is because plugin loading touches opencode's least-controllable boundary—<strong>third-party code + network install</strong>: the package may not install, the entry may not be found, the version may not be compatible. Splitting this error-prone chain into clear stages, each independently retried and reported, is the pragmatic balance between "opening outward" and "staying robust"—<strong>open the door to welcome third parties, but never let one un-installable plugin drag down the whole startup.</strong></p>
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
    <li><strong>config-driven + dynamic loading</strong> (<span class="mono">plugin/loader.ts</span>): config <span class="mono">plugin:[...]</span> (npm name/local path)→loader resolve (install/entry/compatibility/load stages; only install retried)→import→<span class="mono">Plugin(input)</span>→hook up Hooks; <span class="mono">loadExternal</span> loads in parallel. Staged retry = open outward yet stay robust.</li>
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
    <li><strong>config-driven + dynamic loading</strong> (<span class="mono">plugin/loader.ts</span>): config <span class="mono">plugin:[...]</span> (npm name/local path)→resolve (install/entry/compatibility/load stages; only install retried)→import→<span class="mono">Plugin(input)</span>→hook up Hooks; <span class="mono">loadExternal</span> in parallel. Staged retry = open outward (third-party code + network install) yet not dragged down by one bad plugin.</li>
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
LESSON_59 = {
    "zh": r"""
<p class="lead">前两课讲的插件，是 opencode 向第三方敞开的「通用之门」。这一课讲一种更<strong>专门</strong>的集成，它解决 agent 编码时一个致命的软肋：<strong>它在「盲打」</strong>。想想看，一个 agent 改一行 TypeScript，它怎么知道自己有没有把类型改崩？它想跳到某个函数的定义，靠 grep 猜一个名字、撞运气。而你——一个人类开发者——身边有 IDE 时刻盯着：红色波浪线告诉你哪行编译不过、Ctrl-点击就跳到定义、悬停就看到类型。这一课讲的 <strong>LSP 集成</strong>，就是把这套「IDE 的大脑」装到 agent 身上，让它从「盲打」变成「<strong>边写边看着红线写</strong>」。</p>
<p>这一课有两个最值得带走的洞见。第一，<strong>opencode 不自己造「代码智能」，而是借来整个 IDE 生态的大脑</strong>。它说的是 <strong>LSP（Language Server Protocol，语言服务器协议）</strong>——VS Code、Neovim 等编辑器共用的那套标准协议；于是它能直接跑<strong>和 VS Code 一模一样的语言服务器</strong>（typescript-language-server、gopls、pyright……）。每种语言的理解何其复杂，opencode 一种都不自己实现，全交给那些千锤百炼的语言服务器。第二，<strong>代码智能有「被动」与「主动」两副面孔</strong>：被动的是<strong>诊断（diagnostics）</strong>——agent 改完一个文件，opencode 自动把语言服务器报出的编译错误喂给它，于是 agent <strong>能看见自己刚犯的错</strong>、当即修正；主动的是 <strong>lsp 工具</strong>——agent 能主动调它去精确地「跳定义、找引用、看类型」，而非靠 grep 瞎猜。读懂这两点，你就懂了「为什么 opencode 改起代码来，不像在猜，而像一个手边开着 IDE 的人」。</p>

<div class="card analogy">
  <div class="tag">👓 生活类比</div>
  把 LSP 集成想象成 agent <strong>终于戴上了一副眼镜</strong>。在此之前，agent 写代码像是<strong>闭着眼睛在键盘上敲</strong>——它能打出字，却看不见屏幕上自己刚制造的一片红色波浪线。装上 LSP 这副「眼镜」后，每改完一处，它眼前立刻浮现出和你 IDE 里<strong>一模一样的反馈</strong>：「第 12 行：类型 string 不能赋给 number」「第 30 行：找不到名字 foo」。它看得见自己的错，于是能像你一样<strong>改了再看、看了再改</strong>，直到红线全消。而那个 <strong>lsp 工具</strong>，则像给了它 IDE 里的 <strong>Ctrl-点击</strong>和<strong>悬停提示</strong>：想知道某个函数定义在哪？不必满仓库 grep 一个名字、再从一堆同名里猜——直接问语言服务器，它<strong>精确地</strong>指给你看。<strong>一个能看见红线、能精确跳转的 agent，和一个盲打的 agent，编码质量是天壤之别</strong>——而这副眼镜，opencode 不是自己磨的，是接来了整个编辑器世界共用的那副。
</div>

<h2>LSP：借来整个 IDE 生态的大脑</h2>
<p>要给 agent「代码智能」，最笨的办法是自己为每种语言写一套理解器——但那意味着重新实现 TypeScript 编译器、Go 的类型检查器、Python 的分析器……一种语言就是一个天坑。opencode 的聪明之处，是它根本不碰这个坑，而是站到了一个早已解决此问题的巨人肩上：<strong>LSP</strong>。LSP 当初被发明出来，正是为了解一道「<strong>M × N</strong>」的难题——<span class="mono">M</span> 种编辑器要支持 <span class="mono">N</span> 种语言，若各自对接就是 M×N 套适配；而 LSP 定一套标准协议，编辑器和语言各自只对接协议，难题就塌缩成了「<strong>M + N</strong>」。opencode 做的，就是<strong>把自己当成又一个「编辑器」</strong>接进这套协议：</p>
<div class="layers">
  <div class="layer"><span class="l-tag">opencode（LSP 客户端）</span><span class="l-desc">opencode 把自己当一个编辑器，说标准 LSP——<span class="mono">lsp/client.ts</span></span></div>
  <div class="layer"><span class="l-tag">JSON-RPC 连接</span><span class="l-desc">客户端与服务器之间的标准通信（didOpen / 请求 / 通知）</span></div>
  <div class="layer"><span class="l-tag">语言服务器（独立进程）</span><span class="l-desc">typescript-language-server / gopls / pyright…—和 VS Code 跑的同一批</span></div>
</div>
<p>opencode 是 <strong>LSP 客户端</strong>，真正懂语言的是那些<strong>独立进程</strong>的语言服务器，两者通过 JSON-RPC 对话。而 <span class="mono">lsp/server.ts</span> 里维护着一张<strong>「认识的语言服务器」注册表</strong>：每种语言一条目，记着它的 <span class="mono">id</span>、负责哪些<strong>文件扩展名</strong>、以及怎么<strong>找到或装上</strong>那个服务器的二进制。</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">typescript</div><div class="c-txt">.ts/.tsx/.js…→typescript-language-server</div></div>
  <div class="cell"><div class="c-tag">gopls</div><div class="c-txt">.go→gopls（没装就 <span class="mono">go install</span>）</div></div>
  <div class="cell"><div class="c-tag">pyright / rust / eslint…</div><div class="c-txt">各语言/工具各一条目，按扩展名匹配</div></div>
  <div class="cell"><div class="c-tag">biome / oxlint / vue / deno…</div><div class="c-txt">连各种 linter / 框架专用服务器也收录在册</div></div>
</div>
<p>于是当 agent 碰一个 <span class="mono">.go</span> 文件，opencode 就按注册表找到 gopls（必要时自动装）、把它作为子进程拉起、用 LSP 和它对话。<strong>这是全书反复出现的「复用成熟工具」智慧的又一次、也是最壮观的一次登场</strong>——L39 复用 Ripgrep、L51 复用 git，而这里复用的，是<strong>整个语言服务器生态</strong>，是无数人为「让编辑器懂代码」积累了十几年的全部成果。opencode 一行语言分析代码都不必写，就让 agent 拥有了和顶级 IDE 同源的代码理解力。</p>

<h2>诊断：让 agent 看见自己刚犯的错</h2>
<p>代码智能的第一副面孔，是<strong>诊断（diagnostics）</strong>——也是对 agent 最关键的那一副。它是<strong>被动、自动</strong>的：agent 不必开口问，opencode 会在它改完文件后，主动把「这文件现在有哪些编译错误」端到它面前。整条反馈回路是这样转的：</p>
<div class="flow">
  <div class="f-node">agent 改了文件<br><small>write/edit 工具</small></div>
  <div class="f-arrow">通知 →</div>
  <div class="f-node">告诉语言服务器<br><small>didChange</small></div>
  <div class="f-arrow">分析 →</div>
  <div class="f-node">服务器推回诊断<br><small>publishDiagnostics</small></div>
  <div class="f-arrow">格式化 →</div>
  <div class="f-node">喂给 agent<br><small>&lt;diagnostics&gt; 文本块</small></div>
</div>
<p>这条回路的「最后一公里」——把语言服务器吐出的诊断<strong>整理成 agent 读得懂的样子</strong>——藏在朴素的 <span class="mono">diagnostic.ts</span> 里，几个小决定却很见功力。把一条原始诊断变成最终喂给 agent 的文本，走的是这样几步：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">过滤：只留 <span class="mono">severity===1</span> 的 ERROR，丢掉 warn/info/hint 噪音</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">封顶：每文件最多 20 条，超出附一句「... and N more」</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">格式：<span class="mono">pretty</span> 把每条格成 <span class="mono">ERROR [行:列] 消息</span>（行列 +1 对齐编辑器 1-based）</span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">包裹：<span class="mono">&lt;diagnostics file="..."&gt;…&lt;/diagnostics&gt;</span>，无错误则返回空串</span></div>
</div>
<p>这几个小决定却很见功力：<span class="mono">pretty</span> 把一条诊断格成 <span class="mono">ERROR [行:列] 消息</span> 这样一行（行列都 +1，对齐编辑器里人眼看到的 1-based 坐标）；<span class="mono">report</span> 则做了三件克制的事——<strong>只留 ERROR</strong>（severity 1，过滤掉一堆 warning/hint 的噪音）、<strong>每文件最多 20 条</strong>（超出只提示「还有 N 条」）、用 <span class="mono">&lt;diagnostics file="..."&gt;</span> 标签包好。为什么这么克制？因为这些诊断要<strong>占用模型宝贵的上下文</strong>（呼应 L42 有界输出的同一种焦虑）：把几百条 warning 一股脑塞给模型，既烧 token 又会淹没真正要命的那几个编译错误。<strong>只报错误、且有界</strong>，是在「让 agent 看见问题」和「别撑爆它的注意力」之间的精准拿捏。而这一整套机制的意义，怎么强调都不为过：<strong>它把 agent 从一个「写完就不知死活」的盲改者，变成了一个能即时收到「你这下改对了/改崩了」反馈的、会自我纠错的编码者</strong>——这正是 M4 那个 agent 循环最需要的高质量反馈信号。</p>

<h2>lsp 工具：让 agent 主动问「这是什么」</h2>
<p>代码智能的第二副面孔，是 <span class="mono">lsp</span> <strong>工具</strong>（<span class="mono">tool/lsp.ts</span>）——它是<strong>主动、按需</strong>的：agent 想精确理解某处代码时，主动调这个工具去问语言服务器。它把 IDE 里你最常用的那些「代码导航」能力，做成了一个工具的几个操作：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">goToDefinition / goToImplementation</div><div class="c-txt">跳到定义 / 实现——「这个符号到底定义在哪？」</div></div>
  <div class="cell"><div class="c-tag">findReferences</div><div class="c-txt">找所有引用——「改它会牵连到哪些地方？」</div></div>
  <div class="cell"><div class="c-tag">hover</div><div class="c-txt">悬停看类型/文档——「这个变量是什么类型？」</div></div>
  <div class="cell"><div class="c-tag">documentSymbol / workspaceSymbol</div><div class="c-txt">列文件/全工程符号——「这文件里有哪些函数类？」</div></div>
  <div class="cell"><div class="c-tag">callHierarchy（prepare/incoming/outgoing）</div><div class="c-txt">调用层级——先 prepare 定位、再问「谁调用了它/它调用了谁？」</div></div>
</div>
<p>这些操作的参数也很「IDE 味」：<span class="mono">filePath</span> + <span class="mono">line</span> + <span class="mono">character</span>（行列都<strong>从 1 开始</strong>，正是你在编辑器里看到的坐标）。它和诊断恰好是「<strong>一被动、一主动</strong>」的互补：诊断是 opencode <strong>塞</strong>给 agent 的（「你改崩了这几处」），lsp 工具是 agent <strong>主动拉</strong>的（「我想知道这个函数定义在哪」）。把这两副面孔并排，代码智能的全貌就清晰了：</p>
<div class="cols">
  <div class="col"><h4>诊断（被动 · 自动）</h4><p>opencode 主动塞给 agent。触发=改完文件。内容=编译错误。价值=即时「红线」反馈，让 agent 看见自己刚犯的错、当即纠正。无需 agent 开口。</p></div>
  <div class="col"><h4>lsp 工具（主动 · 按需）</h4><p>agent 主动调用去问。触发=想理解某处代码。内容=跳定义/找引用/看类型/列符号。价值=语义级精确导航，替代 grep 瞎猜。</p></div>
</div>
<p>这种主动查询为什么珍贵？因为 agent 此前理解代码，靠的多是 <span class="mono">grep</span> 一个名字——但同名的符号可能有十几个，grep 分不清哪个是真正的定义、更给不出类型。而 lsp 工具直接问语言服务器，拿到的是<strong>语义级的精确答案</strong>：这个 <span class="mono">foo</span> 就是定义在那个文件那一行、它的类型就是这个、引用它的就是这十处。<strong>从「文本级的猜」升级到「语义级的知」</strong>——这让 agent 在大型陌生代码库里的导航，第一次有了和人类用 IDE 时相近的精度。把诊断（被动看见错）和 lsp 工具（主动查清楚）合起来，opencode 就给了 agent 一双完整的「<strong>会看红线、能精确跳转</strong>」的开发者之眼。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观视角</div>
  <p>这一课讲清了 opencode 如何用 LSP 给 agent 装上「代码智能」：</p>
  <ul>
    <li><strong>借来整个 IDE 生态的大脑</strong>：opencode 不自造代码理解，而是说标准 <strong>LSP</strong> 协议、跑和 VS Code 同源的语言服务器（typescript-language-server/gopls/pyright…）。LSP 把「M 编辑器 × N 语言」难题塌缩成「M + N」；opencode 把自己当又一个「编辑器」接进去。<span class="mono">lsp/client.ts</span>=LSP 客户端，语言服务器=独立进程，JSON-RPC 对话；<span class="mono">lsp/server.ts</span>=按扩展名匹配的语言服务器注册表（找/装二进制）。复用成熟生态最壮观一例（同 L39 Ripgrep、L51 git）。</li>
    <li><strong>诊断（被动·自动）</strong>：agent 改文件→didChange→服务器 publishDiagnostics→<span class="mono">diagnostic.ts</span> 的 <span class="mono">report</span> 格式化（<span class="mono">pretty</span>=ERROR[行:列]消息、行列 1-based；<strong>只留 ERROR</strong>、每文件<strong>≤20 条</strong>、<span class="mono">&lt;diagnostics&gt;</span> 包裹）→喂 agent。有界=别撑爆上下文（呼应 L42）。让 agent 看见自己刚犯的错、即时自我纠错（喂给 M4 循环的高质量反馈）。</li>
    <li><strong>lsp 工具（主动·按需）</strong>（<span class="mono">tool/lsp.ts</span>）：9 个操作=goToDefinition/findReferences/hover/documentSymbol/workspaceSymbol/goToImplementation/callHierarchy…；参数 filePath+line+character（1-based）。agent 主动问语言服务器，拿语义级精确答案，而非 grep 文本级猜。</li>
    <li><strong>一被动一主动，互补成「开发者之眼」</strong>：诊断是 opencode 塞给 agent（你改崩了），lsp 工具是 agent 主动拉（这是什么）。从「文本级的猜」升级到「语义级的知」，让 agent 在大型代码库导航有了近人类 IDE 的精度。</li>
  </ul>
  <p>LSP 给了 agent「看懂代码」的眼睛。M11 还剩两课讲更底层的集成：L60 讲 <strong>PTY 与 shell</strong>——终端进程怎么被管理、环境变量怎么层层叠加（正接 L58 的 shell.env 钩子），L61 讲 <strong>ACP 与 Location 抽象</strong>——opencode 怎么作为一个 ACP server 被别的编辑器接入、会话怎么跨「位置」移动。讲完这两课，M11「扩展与集成」就收官。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p><span class="mono">diagnostic.ts</span> 的 <span class="mono">report</span>，把「怎么把诊断恰到好处地喂给模型」写得朴素而克制（简化自源码）：</p>
  <pre class="code"><span class="kw">const</span> MAX_PER_FILE = <span class="nu">20</span>

<span class="kw">export function</span> <span class="fn">report</span>(file, issues) {
  <span class="kw">const</span> errors = issues.<span class="fn">filter</span>((i) =&gt; i.severity === <span class="nu">1</span>)   <span class="cm">// ← 只留 ERROR，滤掉 warn/hint 噪音</span>
  <span class="kw">if</span> (errors.length === <span class="nu">0</span>) <span class="kw">return</span> <span class="st">""</span>                  <span class="cm">// 没错误就什么都不说</span>
  <span class="kw">const</span> limited = errors.<span class="fn">slice</span>(<span class="nu">0</span>, MAX_PER_FILE)         <span class="cm">// ← 每文件最多 20 条</span>
  <span class="kw">const</span> more = errors.length - MAX_PER_FILE
  <span class="kw">return</span> <span class="st">`&lt;diagnostics file="${file}"&gt;\n`</span> +
    limited.<span class="fn">map</span>(pretty).<span class="fn">join</span>(<span class="st">"\n"</span>) +                  <span class="cm">// pretty: ERROR [行:列] 消息</span>
    (more &gt; <span class="nu">0</span> ? <span class="st">`\n... and ${more} more`</span> : <span class="st">""</span>) + <span class="st">`\n&lt;/diagnostics&gt;`</span>
}</pre>
  <p>这二十来行代码里，藏着一个常被新手忽略、却对 agent 体验至关重要的判断：<strong>什么该说、什么不该说。</strong>一个朴素的实现可能会把语言服务器吐出的<strong>所有</strong>诊断（错误、警告、提示、风格建议）一股脑塞给模型——结果是灾难：模型的上下文被几百条「这里少个分号」「建议用 const」的噪音淹没，真正会导致编译失败的那三条 ERROR 反而被埋了。<span class="mono">report</span> 做了三层克制：<strong>只报 ERROR</strong>（agent 当下最该管的是「能不能编译过」，warning 多是风格偏好，可以稍后再说）、<strong>每文件封顶 20 条</strong>（一个文件错到 20 条以上，再多列也没意义，先修这些）、<strong>没错误就返回空字符串</strong>（一个字都不浪费）。这背后是一个深刻的产品直觉：<strong>给 agent 的反馈，不是越多越好，而是越「准」越好。</strong>信息过载和信息缺失一样有害——前者淹没重点、烧光上下文，后者让 agent 盲目。<span class="mono">report</span> 这二十行的全部用心，就是在这两者之间，为「agent 此刻最需要知道什么」找到那个恰到好处的量。这和 L42 有界工具输出是同一种对「模型注意力稀缺」的敬畏，只不过这次稀缺的对象，是那几条<strong>真正要命</strong>的编译错误。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>LSP=借来整个 IDE 生态的大脑</strong>：opencode 不自造代码理解，说标准 LSP 协议、跑和 VS Code 同源的语言服务器（typescript-language-server/gopls/pyright…）。LSP 把「M 编辑器×N 语言」塌缩成「M+N」，opencode 当又一个「编辑器」接入。客户端(<span class="mono">lsp/client.ts</span>)↔JSON-RPC↔语言服务器(独立进程)；<span class="mono">server.ts</span>=按扩展名匹配的注册表。复用成熟生态最壮观一例（同 L39/L51）。</li>
    <li><strong>诊断（被动·自动）</strong>：改文件→didChange→服务器 publishDiagnostics→<span class="mono">diagnostic.report</span> 格式化→喂 agent。<span class="mono">pretty</span>=ERROR[行:列]消息(1-based)；只留 ERROR、每文件≤20、<span class="mono">&lt;diagnostics&gt;</span> 包裹。有界=别撑爆上下文（呼应 L42）。让 agent 看见自己刚犯的错、即时自我纠错（喂 M4 循环）。</li>
    <li><strong>lsp 工具（主动·按需）</strong>（<span class="mono">tool/lsp.ts</span>）：9 操作 goToDefinition/findReferences/hover/documentSymbol/workspaceSymbol/goToImplementation/callHierarchy；参数 filePath+line+character(1-based)。主动问服务器拿语义级精确答案，而非 grep 文本级猜。</li>
    <li><strong>一被动一主动=「开发者之眼」</strong>：诊断 opencode 塞给 agent(你改崩了)、lsp 工具 agent 主动拉(这是什么)。从「文本级猜」升级到「语义级知」，大库导航近人类 IDE 精度。</li>
    <li><strong>给 agent 的反馈越准越好，非越多越好</strong>：<span class="mono">report</span> 只报 ERROR、封顶 20、无错返空——信息过载与缺失同样有害。对「模型注意力稀缺」的敬畏（同 L42），这次稀缺对象是真正要命的编译错误。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">The plugins of the last two lessons are opencode's "general door" open to third parties. This lesson covers a more <strong>specialized</strong> integration, solving a fatal weakness when an agent codes: <strong>it's "typing blind."</strong> Think about it—an agent changes a line of TypeScript, how does it know whether it broke the types? It wants to jump to some function's definition, and grep-guesses a name, trusting luck. But you—a human developer—have an IDE watching at all times: red squiggles tell you which line won't compile, Ctrl-click jumps to the definition, hover shows the type. This lesson's <strong>LSP integration</strong> installs this "IDE brain" onto the agent, turning it from "typing blind" into "<strong>writing while watching the red lines</strong>."</p>
<p>This lesson has two highlights most worth taking away. First, <strong>opencode doesn't build its own "code intelligence" but borrows the whole IDE ecosystem's brain</strong>. It speaks <strong>LSP (Language Server Protocol)</strong>—the standard protocol shared by editors like VS Code, Neovim; so it can run <strong>the exact same language servers as VS Code</strong> (typescript-language-server, gopls, pyright…). However complex understanding each language is, opencode implements not one itself, handing it all to those battle-hardened language servers. Second, <strong>code intelligence has two faces, "passive" and "active"</strong>: the passive is <strong>diagnostics</strong>—after the agent edits a file, opencode automatically feeds it the compile errors the language server reports, so the agent <strong>can see the mistake it just made</strong> and fix it at once; the active is the <strong>lsp tool</strong>—the agent can actively call it to precisely "jump to definition, find references, see types" rather than grep-guessing. Grasp these two and you'll understand "why opencode, when changing code, doesn't seem to be guessing but like someone with an IDE open at hand."</p>

<div class="card analogy">
  <div class="tag">👓 Analogy</div>
  Picture LSP integration as the agent <strong>finally putting on a pair of glasses</strong>. Before this, the agent wrote code like <strong>tapping the keyboard with its eyes closed</strong>—it could type characters but couldn't see the patch of red squiggles it just created on screen. With these LSP "glasses" on, after each edit, the exact same feedback as in your IDE immediately appears before it: "line 12: type string is not assignable to number," "line 30: cannot find name foo." It sees its own errors, so it can, like you, <strong>edit then look, look then edit</strong>, until the red lines are all gone. And that <strong>lsp tool</strong> is like giving it the IDE's <strong>Ctrl-click</strong> and <strong>hover tooltip</strong>: want to know where some function is defined? No need to grep a name across the whole repo and guess among a pile of same-names—just ask the language server, which <strong>precisely</strong> points it out. <strong>An agent that can see red lines and jump precisely versus one typing blind is a world apart in coding quality</strong>—and these glasses opencode didn't grind itself, it borrowed the pair the whole editor world shares.
</div>

<h2>LSP: borrowing the whole IDE ecosystem's brain</h2>
<p>To give an agent "code intelligence," the dumbest way is to write your own understander for each language—but that means reimplementing the TypeScript compiler, Go's type checker, Python's analyzer… each language a bottomless pit. opencode's cleverness is not touching this pit at all but standing on the shoulders of a giant that long solved this: <strong>LSP</strong>. LSP was invented precisely to solve an "<strong>M × N</strong>" problem—<span class="mono">M</span> editors needing to support <span class="mono">N</span> languages, each pairing up being M×N adapters; while LSP defines one standard protocol, editors and languages each only pair with the protocol, and the problem collapses to "<strong>M + N</strong>." What opencode does is <strong>treat itself as yet another "editor"</strong> plugging into this protocol:</p>
<div class="layers">
  <div class="layer"><span class="l-tag">opencode (LSP client)</span><span class="l-desc">opencode treats itself as an editor, speaks standard LSP—<span class="mono">lsp/client.ts</span></span></div>
  <div class="layer"><span class="l-tag">JSON-RPC connection</span><span class="l-desc">standard communication between client and server (didOpen / requests / notifications)</span></div>
  <div class="layer"><span class="l-tag">language server (separate process)</span><span class="l-desc">typescript-language-server / gopls / pyright…—the same batch VS Code runs</span></div>
</div>
<p>opencode is the <strong>LSP client</strong>, what truly understands the language is those <strong>separate-process</strong> language servers, the two talking via JSON-RPC. And <span class="mono">lsp/server.ts</span> maintains a <strong>"known language servers" registry</strong>: one entry per language, recording its <span class="mono">id</span>, which <strong>file extensions</strong> it handles, and how to <strong>find or install</strong> that server's binary.</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">typescript</div><div class="c-txt">.ts/.tsx/.js…→typescript-language-server</div></div>
  <div class="cell"><div class="c-tag">gopls</div><div class="c-txt">.go→gopls (if absent, <span class="mono">go install</span>)</div></div>
  <div class="cell"><div class="c-tag">pyright / rust / eslint…</div><div class="c-txt">one entry per language/tool, matched by extension</div></div>
  <div class="cell"><div class="c-tag">biome / oxlint / vue / deno…</div><div class="c-txt">even various linters / framework-specific servers are on the books</div></div>
</div>
<p>So when the agent touches a <span class="mono">.go</span> file, opencode finds gopls per the registry (auto-installing if needed), spawns it as a child process, and talks LSP with it. <strong>This is another—and the most spectacular—appearance of the book's recurring "reuse a mature tool" wisdom</strong>—L39 reused Ripgrep, L51 reused git, and here what's reused is <strong>the entire language-server ecosystem</strong>, all the fruits countless people accumulated over a decade-plus to "make editors understand code." opencode needn't write one line of language-analysis code, yet gives the agent code understanding from the same source as a top IDE.</p>

<h2>Diagnostics: letting the agent see the mistake it just made</h2>
<p>Code intelligence's first face is <strong>diagnostics</strong>—also the most crucial one for the agent. It's <strong>passive, automatic</strong>: the agent needn't ask, opencode proactively delivers "what compile errors this file now has" after it edits a file. The whole feedback loop turns like this:</p>
<div class="flow">
  <div class="f-node">agent edits a file<br><small>write/edit tool</small></div>
  <div class="f-arrow">notify →</div>
  <div class="f-node">tell the language server<br><small>didChange</small></div>
  <div class="f-arrow">analyze →</div>
  <div class="f-node">server pushes diagnostics back<br><small>publishDiagnostics</small></div>
  <div class="f-arrow">format →</div>
  <div class="f-node">feed to the agent<br><small>&lt;diagnostics&gt; text block</small></div>
</div>
<p>This loop's "last mile"—<strong>tidying the diagnostics the language server spits into something the agent can read</strong>—hides in the plain <span class="mono">diagnostic.ts</span>, a few small decisions yet quite crafty. Turning a raw diagnostic into the final text fed to the agent goes through these steps:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">filter: keep only <span class="mono">severity===1</span> ERRORs, drop warn/info/hint noise</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">cap: at most 20 per file, append "... and N more" if over</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">format: <span class="mono">pretty</span> shapes each into <span class="mono">ERROR [line:col] message</span> (line/col +1 to match the editor's 1-based)</span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">wrap: <span class="mono">&lt;diagnostics file="..."&gt;…&lt;/diagnostics&gt;</span>, return empty string if no errors</span></div>
</div>
<p>These small decisions are quite crafty: <span class="mono">pretty</span> shapes a diagnostic into a line like <span class="mono">ERROR [line:col] message</span> (line and col both +1, matching the 1-based coordinates a human sees in the editor); <span class="mono">report</span> does three restrained things—<strong>keep only ERROR</strong> (severity 1, filtering out a pile of warning/hint noise), <strong>at most 20 per file</strong> (over that just hint "N more"), and wrap with the <span class="mono">&lt;diagnostics file="..."&gt;</span> tag. Why so restrained? Because these diagnostics will <strong>occupy the model's precious context</strong> (echoing L42 bounded output's same anxiety): stuffing hundreds of warnings into the model both burns tokens and drowns the few truly fatal compile errors. <strong>Report only errors, and bounded</strong>, is the precise calibration between "letting the agent see problems" and "not overflowing its attention." And the significance of this whole mechanism can't be overstated: <strong>it turns the agent from a blind editor who "doesn't know its fate after writing" into a self-correcting coder who instantly receives "you got it right / broke it"</strong>—exactly the high-quality feedback signal that M4's agent loop most needs.</p>

<h2>The lsp tool: letting the agent actively ask "what is this"</h2>
<p>Code intelligence's second face is the <span class="mono">lsp</span> <strong>tool</strong> (<span class="mono">tool/lsp.ts</span>)—it's <strong>active, on-demand</strong>: when the agent wants to precisely understand some code, it actively calls this tool to ask the language server. It turns those "code navigation" abilities you most use in an IDE into a tool's several operations:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">goToDefinition / goToImplementation</div><div class="c-txt">jump to definition / implementation—"where exactly is this symbol defined?"</div></div>
  <div class="cell"><div class="c-tag">findReferences</div><div class="c-txt">find all references—"what places will changing it affect?"</div></div>
  <div class="cell"><div class="c-tag">hover</div><div class="c-txt">hover to see type/docs—"what type is this variable?"</div></div>
  <div class="cell"><div class="c-tag">documentSymbol / workspaceSymbol</div><div class="c-txt">list file/whole-project symbols—"what functions and classes are in this file?"</div></div>
  <div class="cell"><div class="c-tag">callHierarchy (prepare/incoming/outgoing)</div><div class="c-txt">call hierarchy—prepare to locate, then "who calls it / what does it call?"</div></div>
</div>
<p>These operations' parameters are very "IDE-flavored" too: <span class="mono">filePath</span> + <span class="mono">line</span> + <span class="mono">character</span> (line and col both <strong>start at 1</strong>, exactly the coordinates you see in the editor). It and diagnostics are exactly a "<strong>one passive, one active</strong>" complement: diagnostics are <strong>pushed</strong> by opencode to the agent ("you broke these spots"), the lsp tool is <strong>actively pulled</strong> by the agent ("I want to know where this function is defined"). Putting the two faces side by side, code intelligence's full picture is clear:</p>
<div class="cols">
  <div class="col"><h4>diagnostics (passive · automatic)</h4><p>opencode proactively pushes to the agent. Trigger = after editing a file. Content = compile errors. Value = instant "red line" feedback, letting the agent see its just-made mistake and correct at once. No need for the agent to ask.</p></div>
  <div class="col"><h4>lsp tool (active · on-demand)</h4><p>the agent actively calls to ask. Trigger = wanting to understand some code. Content = jump-def/find-refs/see-type/list-symbols. Value = semantic-level precise navigation, replacing grep-guessing.</p></div>
</div>
<p>Why is this active querying precious? Because the agent previously understood code mostly by <span class="mono">grep</span>-ing a name—but a same-named symbol may have a dozen, grep can't tell which is the real definition, much less give the type. The lsp tool asks the language server directly, getting a <strong>semantic-level precise answer</strong>: this <span class="mono">foo</span> is defined in that file at that line, its type is this, the ones referencing it are these ten spots. <strong>Upgrading from "text-level guessing" to "semantic-level knowing"</strong>—this gives the agent's navigation in a large unfamiliar codebase, for the first time, precision close to a human using an IDE. Combining diagnostics (passively seeing errors) and the lsp tool (actively asking clearly), opencode gives the agent a complete pair of developer's eyes that "<strong>can see red lines and jump precisely</strong>."</p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>This lesson clarifies how opencode installs "code intelligence" onto the agent with LSP:</p>
  <ul>
    <li><strong>borrowing the whole IDE ecosystem's brain</strong>: opencode doesn't build its own code understanding but speaks standard <strong>LSP</strong> and runs the same-source language servers as VS Code (typescript-language-server/gopls/pyright…). LSP collapses the "M editors × N languages" problem to "M + N"; opencode plugs in as yet another "editor." <span class="mono">lsp/client.ts</span> = LSP client, language servers = separate processes, JSON-RPC dialogue; <span class="mono">lsp/server.ts</span> = a by-extension registry of language servers (find/install the binary). The most spectacular case of reusing a mature ecosystem (like L39 Ripgrep, L51 git).</li>
    <li><strong>diagnostics (passive · automatic)</strong>: agent edits file→didChange→server publishDiagnostics→<span class="mono">diagnostic.ts</span>'s <span class="mono">report</span> formats (<span class="mono">pretty</span>=ERROR[line:col] message, 1-based; <strong>keep only ERROR</strong>, <strong>≤20 per file</strong>, <span class="mono">&lt;diagnostics&gt;</span> wrap)→feed the agent. Bounded = don't overflow context (echoing L42). Lets the agent see its just-made mistake, self-correct instantly (high-quality feedback feeding M4's loop).</li>
    <li><strong>lsp tool (active · on-demand)</strong> (<span class="mono">tool/lsp.ts</span>): 9 operations = goToDefinition/findReferences/hover/documentSymbol/workspaceSymbol/goToImplementation/callHierarchy…; params filePath+line+character (1-based). The agent actively asks the language server for semantic-level precise answers, not grep text-level guessing.</li>
    <li><strong>one passive one active, complementing into "developer's eyes"</strong>: diagnostics opencode pushes to the agent (you broke it), the lsp tool the agent actively pulls (what is this). Upgrading from "text-level guessing" to "semantic-level knowing," giving the agent's large-codebase navigation precision close to a human IDE.</li>
  </ul>
  <p>LSP gives the agent eyes to "understand code." M11 has two lessons left on lower-level integrations: L60 covers <strong>PTY and shell</strong>—how terminal processes are managed, how env vars stack layer by layer (connecting L58's shell.env hook), L61 covers <strong>ACP and the Location model</strong>—how opencode, as an ACP server, gets connected by other editors, how sessions move across "locations." After these two, M11 "Extensibility and integration" wraps up.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p><span class="mono">diagnostic.ts</span>'s <span class="mono">report</span> writes "how to feed diagnostics to the model just right" plainly and with restraint (simplified from source):</p>
  <pre class="code"><span class="kw">const</span> MAX_PER_FILE = <span class="nu">20</span>

<span class="kw">export function</span> <span class="fn">report</span>(file, issues) {
  <span class="kw">const</span> errors = issues.<span class="fn">filter</span>((i) =&gt; i.severity === <span class="nu">1</span>)   <span class="cm">// ← keep only ERROR, filter warn/hint noise</span>
  <span class="kw">if</span> (errors.length === <span class="nu">0</span>) <span class="kw">return</span> <span class="st">""</span>                  <span class="cm">// no errors, say nothing</span>
  <span class="kw">const</span> limited = errors.<span class="fn">slice</span>(<span class="nu">0</span>, MAX_PER_FILE)         <span class="cm">// ← at most 20 per file</span>
  <span class="kw">const</span> more = errors.length - MAX_PER_FILE
  <span class="kw">return</span> <span class="st">`&lt;diagnostics file="${file}"&gt;\n`</span> +
    limited.<span class="fn">map</span>(pretty).<span class="fn">join</span>(<span class="st">"\n"</span>) +                  <span class="cm">// pretty: ERROR [line:col] message</span>
    (more &gt; <span class="nu">0</span> ? <span class="st">`\n... and ${more} more`</span> : <span class="st">""</span>) + <span class="st">`\n&lt;/diagnostics&gt;`</span>
}</pre>
  <p>In these twenty-odd lines hides a judgment often overlooked by beginners yet crucial to the agent experience: <strong>what to say and what not to.</strong> A naive implementation might stuff <strong>all</strong> the diagnostics the language server spits (errors, warnings, hints, style suggestions) into the model—a disaster: the model's context is drowned in hundreds of "missing semicolon here," "suggest const" noise, while the three ERRORs truly causing compile failure get buried. <span class="mono">report</span> does three layers of restraint: <strong>report only ERROR</strong> (what the agent should care about now is "does it compile," warnings are mostly style preferences, can wait), <strong>cap at 20 per file</strong> (a file erroring over 20 times, listing more is pointless, fix these first), <strong>return an empty string if no errors</strong> (don't waste a single word). Behind this is a profound product intuition: <strong>feedback to the agent isn't better the more, but better the more "precise."</strong> Information overload is as harmful as information absence—the former drowns the focus and burns context, the latter leaves the agent blind. The whole care of <span class="mono">report</span>'s twenty lines is finding, between these two, the just-right amount for "what the agent most needs to know right now." This is the same reverence for "the model's scarce attention" as L42's bounded tool output, only this time the scarce object is the few <strong>truly fatal</strong> compile errors.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>LSP = borrowing the whole IDE ecosystem's brain</strong>: opencode doesn't build its own code understanding, speaks standard LSP and runs same-source language servers as VS Code (typescript-language-server/gopls/pyright…). LSP collapses "M editors × N languages" to "M+N," opencode plugs in as another "editor." client (<span class="mono">lsp/client.ts</span>)↔JSON-RPC↔language server (separate process); <span class="mono">server.ts</span> = a by-extension registry. The most spectacular case of reusing a mature ecosystem (like L39/L51).</li>
    <li><strong>diagnostics (passive · automatic)</strong>: edit file→didChange→server publishDiagnostics→<span class="mono">diagnostic.report</span> formats→feed agent. <span class="mono">pretty</span>=ERROR[line:col] message (1-based); keep only ERROR, ≤20 per file, <span class="mono">&lt;diagnostics&gt;</span> wrap. Bounded = don't overflow context (echoing L42). Lets the agent see its just-made mistake, self-correct instantly (feeding M4's loop).</li>
    <li><strong>lsp tool (active · on-demand)</strong> (<span class="mono">tool/lsp.ts</span>): 9 operations goToDefinition/findReferences/hover/documentSymbol/workspaceSymbol/goToImplementation/callHierarchy; params filePath+line+character (1-based). Actively asks the server for semantic-level precise answers, not grep text-level guessing.</li>
    <li><strong>one passive one active = "developer's eyes"</strong>: diagnostics opencode pushes to the agent (you broke it), the lsp tool the agent actively pulls (what is this). Upgrading from "text-level guessing" to "semantic-level knowing," large-codebase navigation with near-human IDE precision.</li>
    <li><strong>feedback to the agent better the more precise, not the more</strong>: <span class="mono">report</span> reports only ERROR, caps at 20, returns empty if no errors—information overload and absence are equally harmful. Reverence for "the model's scarce attention" (like L42), this time the scarce object being the truly fatal compile errors.</li>
  </ul>
</div>
""",
}
LESSON_60 = {
    "zh": r"""
<p class="lead">还记得第 39 课那个关键澄清吗——opencode 的 bash 工具是<strong>批处理</strong>（启动子进程、跑完、收 stdout），而 <span class="mono">pty/*</span> 是<strong>另一套</strong>给交互式终端用的基础设施。当时我们把 PTY 搁下了，这一课就来补上：<strong>PTY（pseudo-terminal，伪终端）</strong>。问题很实在：为什么 opencode 光有批处理的 bash 还不够、非得搞一套真终端？因为有些程序<strong>非真终端不可</strong>——交互式 REPL（你得能边看输出边输入）、会检测「自己是不是连着终端」才显示彩色/进度条的程序、需要你<strong>实时打字进去</strong>的命令。批处理的 bash 对这些无能为力（它一问一答、不能中途输入、程序也知道自己没连终端）。PTY 给的，是一个<strong>真实的、能流式看输出、能打字进去、能调整大小</strong>的终端——就像你在屏幕上开的那个终端窗口本身。</p>
<p>这一课有两个最值得带走的洞见。第一，<strong>PTY 是一个干净的、跨平台的「真终端」抽象</strong>：一个 <span class="mono">Proc</span> 接口（<span class="mono">onData</span> 流式收输出、<span class="mono">write</span> 打字进去、<span class="mono">resize</span> 调大小、<span class="mono">kill</span> 杀掉），背后由 Bun 和 Node 两套实现撑着；它的输出还能<strong>经 WebSocket 流给客户端</strong>（带「游标重放」，断了能从某处接着看），并用<strong>短时令牌（ticket）</strong>守住「谁能连上这个终端」。第二，也是最点睛的——<strong>PTY 的环境变量是「层层叠加」出来的</strong>，而且叠加的顺序暗藏深意：先是<strong>调用方传的值</strong>，再叠一层<strong>宿主覆盖</strong>（正是第 58 课那个 <span class="mono">shell.env</span> 插件钩子！），最后强制盖上 <strong>opencode 写死的终端不变量</strong>（如 <span class="mono">TERM</span>、<span class="mono">OPENCODE_TERMINAL</span>）。读懂这个「<strong>可定制的在中间、不可妥协的在最后</strong>」的叠加顺序，你就懂了一个老练的系统是怎么<strong>既给足灵活性、又守住底线</strong>的。</p>

<div class="card analogy">
  <div class="tag">🖥️ 生活类比</div>
  把<strong>批处理 bash</strong>（L39）想象成<strong>寄一封信</strong>：你写好一条命令寄出去，对方跑完，把结果打印成一张纸寄回来——全程你插不上话，对方也知道这是封「信」而非面对面。而 <strong>PTY</strong>，是给了你一个<strong>真正的视频通话窗口</strong>：你能实时看到对方屏幕的每一帧、能随时打字过去、窗口还能拉大拉小——对方程序也确确实实「感觉到」自己正连着一个活人在用的终端，于是放心地输出彩色、画进度条、等你输入。至于那套<strong>环境变量的叠加</strong>，像极了<strong>上班穿衣服</strong>：最底层是你自己挑的衣服（调用方传的环境），公司再给你套一件<strong>工服</strong>（插件 <span class="mono">shell.env</span> 钩子的覆盖），而最外面，是那件<strong>无论如何都得穿、谁也不准脱的安全背心</strong>（opencode 强制的 <span class="mono">TERM</span> 等终端不变量）。顺序很关键：<strong>个性化的让你和公司随意叠，但保命的那件永远盖在最外、压住一切</strong>——这样既不妨碍你穿出风格，又绝不让任何人把安全背心脱掉。
</div>

<h2>PTY vs 批处理：为什么需要一个真终端</h2>
<p>第 39 课已经点明：bash 工具经 <span class="mono">AppProcess</span> 走<strong>批处理</strong>（spawn 子进程、跑完收结果），而 PTY 是<strong>另一套</strong>。两者的区别，不是「快慢」而是「能不能交互」：</p>
<div class="cols">
  <div class="col"><h4>批处理 bash（L39）</h4><p>一问一答：给一条命令、等它跑完、收 stdout。<strong>不能中途输入</strong>、程序也知道自己<strong>没连终端</strong>（于是常不输出彩色/进度条）。适合「跑个命令拿结果」给模型。</p></div>
  <div class="col"><h4>交互式 PTY</h4><p>真终端：<strong>流式</strong>看输出、<strong>随时打字</strong>进去、能 <strong>resize</strong>。程序「以为」自己连着真人，放心交互。适合 REPL、需 TTY 的工具、给人实时操作。</p></div>
</div>
<p>PTY 把「一个真终端」抽象成了一个极简的 <span class="mono">Proc</span> 接口（<span class="mono">pty/pty.ts</span>），干净得像一台设备的遥控器：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">onData(listener)</div><div class="c-txt">订阅终端吐出的输出（流式，一块块来）</div></div>
  <div class="cell"><div class="c-tag">write(data)</div><div class="c-txt">往终端打字（把输入送进去）</div></div>
  <div class="cell"><div class="c-tag">resize(cols, rows)</div><div class="c-txt">调终端尺寸（窗口拉大拉小时同步）</div></div>
  <div class="cell"><div class="c-tag">onExit / kill</div><div class="c-txt">监听退出 / 杀掉进程</div></div>
</div>
<p>这个接口最妙的，是它<strong>把「平台差异」彻底藏在了背后</strong>。创建一个真伪终端这件事，Bun 和 Node 的底层 API 并不一样，于是 opencode 提供了 <span class="mono">pty.bun.ts</span> 和 <span class="mono">pty.node.ts</span> 两套实现，<strong>都满足同一个 <span class="mono">Proc</span> 接口</strong>。上层代码只管对着 <span class="mono">Proc</span> 编程——<span class="mono">onData</span>/<span class="mono">write</span>/<span class="mono">resize</span>——根本不必关心此刻跑在 Bun 还是 Node 上。这又是「<strong>定义一个干净接口、多套实现各自满足</strong>」的经典手法（同 L52 opentui 把不同终端能力抽象掉、L46 MCP 把 stdio/HTTP transport 抽象掉）：<strong>把善变的、平台相关的脏活封在接口之下，让上层永远面对同一张稳定的脸。</strong></p>

<h2>流式与连接：把终端送到客户端</h2>
<p>一个 PTY 跑在服务器上，但<strong>看它、用它</strong>的可能是别处的客户端（你的 TUI、甚至一个远程会话）。从「创建一个 PTY」到「客户端连上实时看」，走的是这样一条路：</p>
<div class="flow">
  <div class="f-node">创建 PTY<br><small>Proc：起真终端</small></div>
  <div class="f-arrow">申领 →</div>
  <div class="f-node">短时 ticket 令牌<br><small>绑 ptyID+目录、60 秒</small></div>
  <div class="f-arrow">凭票连 →</div>
  <div class="f-node">WebSocket 流<br><small>原始块 + 游标帧</small></div>
  <div class="f-arrow">断线 →</div>
  <div class="f-node">凭游标重放续看<br><small>从断点接着流</small></div>
</div>
<p>opencode 用一套 WebSocket 协议（<span class="mono">pty/protocol.ts</span>）把终端「送出去」，几个设计很务实：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">原始 UTF-8 块出站</div><div class="c-txt">终端输出就是一块块原始字节，直接流给客户端</div></div>
  <div class="cell"><div class="c-tag">游标控制帧（0x00+JSON）</div><div class="c-txt">夹一个特殊帧报「当前输出到第几个字节」——断线后能<strong>从游标续看</strong></div></div>
  <div class="cell"><div class="c-tag">REPLAY_CHUNK=64KB</div><div class="c-txt">重放可能有几 MB，分成有界的块发，不一次撑爆</div></div>
  <div class="cell"><div class="c-tag">ticket 连接令牌</div><div class="c-txt">连一个 PTY 要先拿<strong>短时令牌</strong>（60 秒 TTL、限定 ptyID+目录+工作区）</div></div>
</div>
<p>这里两处尤其值得点出。其一，<strong>游标重放</strong>：终端的输出是连续的一长串，客户端断线重连时不必从头来过，凭一个「游标」（已看到第几个字节）就能<strong>从断点接着流</strong>——这让远程/不稳网络下用 PTY 成为可能。其二，<strong>ticket 令牌</strong>：你不能随便连上任意一个终端。连接前必须先<strong>申领一张短命令牌</strong>（<span class="mono">pty/ticket.ts</span>，60 秒过期、绑死某个具体 ptyID + 目录 + 工作区），用一次即焚。一个能让人<strong>实时打字进去</strong>的终端是极强的能力，若谁都能连，就是天大的安全洞——ticket 把这道门用「短时、限定作用域、一次性」的令牌守住，正是把「强大能力」和「严格授权」绑在一起的务实之举（呼应 L41 权限、L46 MCP 的 OAuth）。</p>

<h2>环境叠加：可定制的在中间，不可妥协的在最后</h2>
<p>现在来到这一课最点睛的设计。创建一个 PTY 时，它该带着<strong>什么环境变量</strong>跑？opencode 的答案不是「用某一份环境」，而是把环境<strong>分层叠加</strong>出来——按 CONTEXT.md 写明的顺序，<strong>合并调用方的值、再叠宿主覆盖、最后强制盖上 opencode 的终端不变量</strong>：</p>
<div class="layers">
  <div class="layer"><span class="l-tag">① 调用方传入的值</span><span class="l-desc">最底层：发起 PTY 的一方给的环境（如继承当前进程的 env）</span></div>
  <div class="layer"><span class="l-tag">② 宿主覆盖（plugin shell.env）</span><span class="l-desc">中间层：触发第 58 课的 <span class="mono">shell.env</span> 钩子，让插件注入/覆盖（如内部代理、CI 标记）</span></div>
  <div class="layer"><span class="l-tag">③ 核心强制的终端不变量</span><span class="l-desc">最上层：opencode 写死盖上 <span class="mono">TERM</span>、<span class="mono">OPENCODE_TERMINAL</span> 等——一个真终端必须有的</span></div>
</div>
<p>这个叠加顺序，绝不是随手排的，它编码了一套清晰的<strong>优先级哲学</strong>。最底层是调用方的「基础环境」，给出一个合理起点；中间层是<strong>可定制的口子</strong>——通过 <span class="mono">shell.env</span> 插件钩子（正是第 58 课那个「改草稿」钩子的一个触发点），让组织/用户能注入自己的环境变量（比如给所有终端注入一个内部 npm 镜像、一个代理地址）；而最上层，是 opencode <strong>强制盖上、谁也覆盖不了</strong>的终端不变量。为什么 <span class="mono">TERM</span>、<span class="mono">OPENCODE_TERMINAL</span> 这些要放<strong>最后、压住一切</strong>？因为它们是「一个真终端之所以是真终端」的<strong>底线</strong>：少了 <span class="mono">TERM</span>，程序就不知道该用什么终端类型来渲染、彩色和光标控制全乱套。这些<strong>不能让任何中间层（哪怕是好心的插件）不小心改坏</strong>，所以必须<strong>最后强制写入</strong>——叠加顺序里，越往后优先级越高，而「不可妥协的底线」就该享有最高优先级。</p>
<p>把这套叠加用一次创建走一遍，那个「可定制与不可妥协」的分寸感就跃然纸上：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">取调用方传的 env 作基底（如继承 process.env）</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">trigger <span class="mono">shell.env</span> 钩子 → 插件往里注入/覆盖几个变量</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">最后强制写入 <span class="mono">TERM</span>/<span class="mono">OPENCODE_TERMINAL</span> → 覆盖前面任何同名项</span></div>
  <div class="t-row"><span class="t-num">✓</span><span class="t-txt">既允许灵活定制，又绝不让终端底线被改坏</span></div>
</div>
<p>CONTEXT.md 还点出一个干净的职责切分：<strong>「PTY 环境」是服务器层的事，而非 Core PTY 的事</strong>。Core 的 PTY 只管「造一个真终端」这件纯粹的事；而「这个终端该带什么环境」——要不要触发插件、要叠哪些不变量——是<strong>服务器层</strong>的职责（独立服务器用一个空适配器即可）。这种「Core 只做最纯粹的事、把策略性的装配留给上层」的分层，又是全书反复出现的审美：<strong>把『机制』（造终端）和『策略』（配什么环境）切开</strong>，让 Core 保持极简纯粹、可在任何场景复用，而把会因场景而变的策略性组装，留给更靠上、更懂上下文的那一层。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观视角</div>
  <p>这一课补齐了 L39 搁下的 PTY——opencode 的真终端基础设施：</p>
  <ul>
    <li><strong>PTY=真交互终端</strong>（vs L39 批处理 bash）：批处理一问一答不能中途输入；PTY 流式看输出+随时打字+resize，程序「以为」连着真人。<span class="mono">Proc</span> 接口（<span class="mono">pty/pty.ts</span>）=onData/write/resize/onExit/kill，<strong>Bun/Node 两套实现满足同一接口</strong>（平台差异藏在接口下，同 L52/L46）。</li>
    <li><strong>流式+连接</strong>（<span class="mono">pty/protocol.ts</span>/<span class="mono">ticket.ts</span>）：WebSocket 送终端给客户端，原始 UTF-8 块出站 + 游标控制帧(0x00+JSON)做<strong>断线重放</strong>、REPLAY_CHUNK 64KB 分块；连接要<strong>短时 ticket 令牌</strong>（60 秒、绑 ptyID+目录+工作区、一次性）守门（强能力绑严授权，同 L41/L46）。</li>
    <li><strong>环境叠加（最点睛）</strong>：PTY 创建按序合并 ①调用方值 → ②宿主覆盖（触发 L58 <span class="mono">shell.env</span> 插件钩子）→ ③核心强制终端不变量（<span class="mono">TERM</span>/<span class="mono">OPENCODE_TERMINAL</span>）。<strong>可定制的在中间、不可妥协的在最后压住一切</strong>——越后优先级越高，底线享最高优先级。</li>
    <li><strong>机制 vs 策略的分层</strong>：「PTY 环境」是服务器层的事、非 Core PTY 的事——Core 只造终端（纯机制），「配什么环境」（策略）留给更懂上下文的服务器层（独立服务器用空适配器）。同全书「切开机制与策略」审美。</li>
  </ul>
  <p>真终端这块基础设施补齐了。M11 还剩最后一课 L61：<strong>ACP 与 Location 抽象</strong>——opencode 怎么反过来作为一个 <strong>ACP server</strong> 被别的编辑器（如 Zed）接入、会话怎么跨「位置（Location）」移动、control plane 怎么协调。讲完 L61，整个 M11「扩展与集成」就收官，opencode「向外敞开的所有门」也就讲全了。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p>CONTEXT.md 用一句话钉死了环境叠加的顺序，而 <span class="mono">pty-environment</span> 插件正是那「中间层」的实现（简化自源码）：</p>
  <pre class="code"><span class="cm">// CONTEXT.md：PTY creation merges caller values, then the host</span>
<span class="cm">// overlay, then Core-forced terminal invariants such as TERM</span>
<span class="cm">// 即：调用方值 → 宿主覆盖 → 强制不变量（后者覆盖前者）</span>

<span class="cm">// 宿主覆盖层 = 触发 shell.env 插件钩子（第 58 课）</span>
PtyEnvironment.Service.of({
  get: (input) =&gt;
    plugin
      .<span class="fn">trigger</span>(<span class="st">"shell.env"</span>, { cwd: input.cwd }, { env: {} })   <span class="cm">// ← 插件往 env 注入</span>
      .<span class="fn">pipe</span>(Effect.<span class="fn">map</span>((result) =&gt; result.env)),
})</pre>
  <p>这段代码最值得品的，是它如何把<strong>第 58 课的插件机制</strong>，<strong>无缝嵌</strong>进了 PTY 环境的「中间层」。你看那个 <span class="mono">plugin.trigger("shell.env", {cwd}, {env:{}})</span>——它正是 L58 讲的「改草稿」：opencode 递一个空的 <span class="mono">{env:{}}</span> 草稿、插件往里填，最后拿到插件改过的 env 作为「宿主覆盖」那一层。<strong>于是 PTY 的环境定制，根本不需要为它发明一套新机制——直接复用了已有的插件钩子。</strong>这正是一套设计良好的系统该有的「<strong>积木相扣</strong>」之美：L58 造好的 <span class="mono">shell.env</span> 钩子是一块通用积木，到了 L60 的 PTY 环境这里，它<strong>恰好就是「中间那一层可定制覆盖」</strong>，严丝合缝地嵌了进去。一个系统里，当你发现「这个新需求，用现成的某个机制一拼就成」时，往往说明前面那些抽象的接缝找得准——它们不是为某一处专门造的，而是<strong>通用到能在意想不到的地方再次复用</strong>。从 L58 的 shell.env 到 L60 的环境叠加，正是这种「<strong>一块积木、多处复用</strong>」的范例。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>PTY=真交互终端</strong>（vs L39 批处理 bash）：批处理一问一答不能中途输入、程序知道没连终端；PTY 流式看输出+随时打字+resize，程序「以为」连真人（REPL/需 TTY 的工具/给人实时操作）。<span class="mono">Proc</span> 接口 onData/write/resize/kill，Bun/Node 两实现满足同一接口（平台差异藏接口下，同 L52/L46）。</li>
    <li><strong>流式+连接</strong>：WebSocket 送终端（<span class="mono">protocol.ts</span>），原始 UTF-8 块 + 游标帧(0x00+JSON)断线重放、REPLAY_CHUNK 64KB；连接要短时 ticket（60 秒/绑 ptyID+目录+工作区/一次性，<span class="mono">ticket.ts</span>）守门——强能力绑严授权（同 L41/L46）。</li>
    <li><strong>环境叠加（最点睛）</strong>：PTY 创建按序合并 ①调用方值→②宿主覆盖（触发 L58 <span class="mono">shell.env</span> 钩子）→③核心强制不变量（<span class="mono">TERM</span>/<span class="mono">OPENCODE_TERMINAL</span>）。可定制在中间、不可妥协在最后压住一切——越后优先级越高，底线享最高优先级。</li>
    <li><strong>积木相扣</strong>：PTY 环境的「中间层」直接复用 L58 的 <span class="mono">shell.env</span> 钩子（<span class="mono">plugin.trigger("shell.env",{cwd},{env:{}})</span>「改草稿」）——新需求用现成机制一拼即成，说明接缝找得准、抽象通用到能意外复用。</li>
    <li><strong>机制 vs 策略分层</strong>：「PTY 环境」是服务器层事、非 Core PTY 事——Core 只造终端（纯机制），配什么环境（策略）留给更懂上下文的上层（独立服务器用空适配器）。同全书「切开机制与策略」。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Remember that key clarification in lesson 39—opencode's bash tool is <strong>batch</strong> (spawn a child process, run to completion, collect stdout), while <span class="mono">pty/*</span> is <strong>a separate</strong> infrastructure for interactive terminals. We set PTY aside then; this lesson fills it in: <strong>PTY (pseudo-terminal)</strong>. The question is concrete: why isn't a batch bash enough for opencode, why build a real terminal too? Because some programs <strong>require a real terminal</strong>—interactive REPLs (you must read output while typing input), programs that detect "am I attached to a terminal?" before showing color/progress bars, commands you need to <strong>type into in real time</strong>. Batch bash is helpless with these (it's one-shot Q&A, can't input mid-way, and the program knows it isn't attached to a terminal). PTY gives a <strong>real terminal you can stream output from, type into, and resize</strong>—just like that terminal window you open on screen itself.</p>
<p>This lesson has two highlights most worth taking away. First, <strong>PTY is a clean, cross-platform "real terminal" abstraction</strong>: a <span class="mono">Proc</span> interface (<span class="mono">onData</span> streams output, <span class="mono">write</span> types in, <span class="mono">resize</span> adjusts size, <span class="mono">kill</span> kills it), backed by two implementations, Bun and Node; its output can also <strong>stream to a client over WebSocket</strong> (with "cursor replay," resume from a point after a drop), guarded by <strong>short-lived tickets</strong> on "who can attach to this terminal." Second, and the most eye-opening—<strong>a PTY's environment variables are "stacked layer by layer,"</strong> and the stacking order hides intent: first the <strong>caller's values</strong>, then a <strong>host overlay</strong> (exactly lesson 58's <span class="mono">shell.env</span> plugin hook!), and finally opencode's <strong>forced terminal invariants</strong> (like <span class="mono">TERM</span>, <span class="mono">OPENCODE_TERMINAL</span>) stamped on top. Grasp this "<strong>customizable in the middle, non-negotiable last</strong>" stacking order and you'll understand how a seasoned system <strong>gives ample flexibility yet holds the bottom line</strong>.</p>

<div class="card analogy">
  <div class="tag">🖥️ Analogy</div>
  Picture <strong>batch bash</strong> (L39) as <strong>mailing a letter</strong>: you write a command, mail it out, the other side runs it and mails back a printed page of results—you can't interject the whole time, and the other side knows it's a "letter," not face-to-face. <strong>PTY</strong> gives you a <strong>real video-call window</strong>: you can watch every frame of the other's screen in real time, type over anytime, and the window can be stretched larger or smaller—and the program really does "feel" it's attached to a terminal a live person is using, so it confidently outputs color, draws progress bars, awaits your input. As for that <strong>environment-variable stacking</strong>, it's just like <strong>dressing for work</strong>: the bottom layer is the clothes you picked (the caller's env), the company adds a <strong>uniform</strong> over it (the plugin <span class="mono">shell.env</span> hook's overlay), and outermost is the <strong>mandatory safety vest no one's allowed to remove</strong> (opencode's forced <span class="mono">TERM</span> and other terminal invariants). The order is key: <strong>let you and the company stack the personalized freely, but the life-saving piece always covers outermost, overriding all</strong>—so it doesn't stop you dressing with style, yet never lets anyone take the safety vest off.
</div>

<h2>PTY vs batch: why you need a real terminal</h2>
<p>Lesson 39 already noted: the bash tool goes <strong>batch</strong> via <span class="mono">AppProcess</span> (spawn a child process, run to completion, collect the result), while PTY is <strong>a separate</strong> thing. The difference isn't "fast vs slow" but "interactive or not":</p>
<div class="cols">
  <div class="col"><h4>batch bash (L39)</h4><p>one-shot Q&A: give a command, wait for it to finish, collect stdout. <strong>Can't input mid-way</strong>, and the program knows it's <strong>not attached to a terminal</strong> (so it often omits color/progress bars). Suited to "run a command, get the result" for the model.</p></div>
  <div class="col"><h4>interactive PTY</h4><p>a real terminal: <strong>stream</strong> output, <strong>type in anytime</strong>, can <strong>resize</strong>. The program "thinks" it's attached to a live person, interacting confidently. Suited to REPLs, TTY-requiring tools, real-time human operation.</p></div>
</div>
<p>PTY abstracts "a real terminal" into a minimal <span class="mono">Proc</span> interface (<span class="mono">pty/pty.ts</span>), clean as a device's remote control:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">onData(listener)</div><div class="c-txt">subscribe to the terminal's output (streaming, chunk by chunk)</div></div>
  <div class="cell"><div class="c-tag">write(data)</div><div class="c-txt">type into the terminal (send input in)</div></div>
  <div class="cell"><div class="c-tag">resize(cols, rows)</div><div class="c-txt">adjust terminal size (sync when the window is stretched)</div></div>
  <div class="cell"><div class="c-tag">onExit / kill</div><div class="c-txt">listen for exit / kill the process</div></div>
</div>
<p>The finest thing about this interface is it <strong>fully hides "platform differences" behind it</strong>. Creating a real pseudo-terminal differs between Bun's and Node's low-level APIs, so opencode provides two implementations, <span class="mono">pty.bun.ts</span> and <span class="mono">pty.node.ts</span>, <strong>both satisfying the same <span class="mono">Proc</span> interface</strong>. Upper code just programs against <span class="mono">Proc</span>—<span class="mono">onData</span>/<span class="mono">write</span>/<span class="mono">resize</span>—not caring whether it's running on Bun or Node right now. This is again the classic technique of "<strong>define a clean interface, multiple implementations each satisfy it</strong>" (like L52 opentui abstracting away different terminal capabilities, L46 MCP abstracting away stdio/HTTP transports): <strong>seal the changeable, platform-specific dirty work beneath an interface, so the upper layer always faces the same stable face.</strong></p>

<h2>Streaming and connecting: delivering the terminal to the client</h2>
<p>A PTY runs on the server, but what <strong>watches and uses</strong> it may be a client elsewhere (your TUI, even a remote session). From "create a PTY" to "the client attaches and watches live," the path is:</p>
<div class="flow">
  <div class="f-node">create PTY<br><small>Proc: start a real terminal</small></div>
  <div class="f-arrow">issue →</div>
  <div class="f-node">short-lived ticket<br><small>bound to ptyID+dir, 60s</small></div>
  <div class="f-arrow">attach with ticket →</div>
  <div class="f-node">WebSocket stream<br><small>raw chunks + cursor frame</small></div>
  <div class="f-arrow">on drop →</div>
  <div class="f-node">replay by cursor to resume<br><small>continue streaming from the break</small></div>
</div>
<p>opencode uses a WebSocket protocol (<span class="mono">pty/protocol.ts</span>) to "deliver" the terminal, with a few pragmatic designs:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">raw UTF-8 chunks outbound</div><div class="c-txt">the terminal output is raw bytes, streamed directly to the client chunk by chunk</div></div>
  <div class="cell"><div class="c-tag">cursor control frame (0x00+JSON)</div><div class="c-txt">a special frame reports "the current output byte position"—after a drop you can <strong>resume from the cursor</strong></div></div>
  <div class="cell"><div class="c-tag">REPLAY_CHUNK=64KB</div><div class="c-txt">replay may be several MB, sent in bounded chunks, not overflowing at once</div></div>
  <div class="cell"><div class="c-tag">ticket connection token</div><div class="c-txt">attaching to a PTY first needs a <strong>short-lived ticket</strong> (60s TTL, scoped to ptyID+directory+workspace)</div></div>
</div>
<p>Two points here especially worth noting. First, <strong>cursor replay</strong>: the terminal's output is a continuous long stream; on reconnect after a drop the client needn't start over—with a "cursor" (which byte it's seen) it can <strong>resume streaming from the break</strong>—making PTY usable over remote/unstable networks. Second, <strong>the ticket</strong>: you can't just attach to any terminal. Before connecting you must <strong>claim a short-lived ticket</strong> (<span class="mono">pty/ticket.ts</span>, 60s expiry, bound to a specific ptyID + directory + workspace), used once then burned. A terminal you can <strong>type into in real time</strong> is an extremely strong capability; if anyone could attach, it'd be a giant security hole—the ticket guards this door with "short-lived, scope-limited, one-time" tokens, exactly the pragmatic move of binding "strong capability" to "strict authorization" (echoing L41 permissions, L46 MCP's OAuth).</p>

<h2>Environment stacking: customizable in the middle, non-negotiable last</h2>
<p>Now to this lesson's most eye-opening design. When creating a PTY, with <strong>what environment variables</strong> should it run? opencode's answer isn't "use some one env" but stacks the environment <strong>in layers</strong>—per the order spelled out in CONTEXT.md, <strong>merge the caller's values, then stack the host overlay, then forcibly stamp opencode's terminal invariants on top</strong>:</p>
<div class="layers">
  <div class="layer"><span class="l-tag">① caller-passed values</span><span class="l-desc">bottom layer: the env the PTY initiator gave (e.g. inherit the current process's env)</span></div>
  <div class="layer"><span class="l-tag">② host overlay (plugin shell.env)</span><span class="l-desc">middle layer: trigger lesson 58's <span class="mono">shell.env</span> hook, letting plugins inject/override (e.g. internal proxy, CI marker)</span></div>
  <div class="layer"><span class="l-tag">③ core-forced terminal invariants</span><span class="l-desc">top layer: opencode forcibly stamps <span class="mono">TERM</span>, <span class="mono">OPENCODE_TERMINAL</span>, etc.—what a real terminal must have</span></div>
</div>
<p>This stacking order is by no means casually arranged; it encodes a clear <strong>priority philosophy</strong>. The bottom layer is the caller's "base environment," giving a reasonable starting point; the middle layer is the <strong>customizable hatch</strong>—via the <span class="mono">shell.env</span> plugin hook (exactly lesson 58's "edit a draft" hook at one of its trigger points), letting orgs/users inject their own env vars (e.g. inject an internal npm mirror, a proxy address, into all terminals); and the top layer is the terminal invariants opencode <strong>forcibly stamps, that no one can override</strong>. Why put <span class="mono">TERM</span>, <span class="mono">OPENCODE_TERMINAL</span> these <strong>last, overriding all</strong>? Because they're the <strong>bottom line</strong> of "what makes a real terminal a real terminal": without <span class="mono">TERM</span>, a program doesn't know which terminal type to render with, and color and cursor control all break. These <strong>can't be accidentally broken by any middle layer (even a well-meaning plugin)</strong>, so they must be <strong>force-written last</strong>—in the stacking order, the later the higher priority, and the "non-negotiable bottom line" deserves the highest priority.</p>
<p>Walking this stacking through one creation, that sense of "customizable yet non-negotiable" leaps out:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">take the caller's env as the base (e.g. inherit process.env)</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">trigger the <span class="mono">shell.env</span> hook → plugins inject/override a few vars into it</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">finally force-write <span class="mono">TERM</span>/<span class="mono">OPENCODE_TERMINAL</span> → override any same-named items before</span></div>
  <div class="t-row"><span class="t-num">✓</span><span class="t-txt">both allow flexible customization and never let the terminal's bottom line be broken</span></div>
</div>
<p>CONTEXT.md also points out a clean separation of responsibility: <strong>the "PTY Environment" is a server-layer concern, not a Core PTY concern</strong>. Core's PTY just handles the pure thing of "making a real terminal"; while "what env this terminal should carry"—whether to trigger plugins, which invariants to stack—is the <strong>server layer</strong>'s job (a standalone server just uses an empty adapter). This layering of "Core does only the purest thing, leaving the strategic assembly to the upper layer" is again the book's recurring aesthetic: <strong>cut "mechanism" (making a terminal) from "policy" (what env to configure)</strong>, letting Core stay minimal, pure, reusable in any scenario, while leaving the scenario-varying strategic assembly to a higher, more context-aware layer.</p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>This lesson fills in the PTY L39 set aside—opencode's real-terminal infrastructure:</p>
  <ul>
    <li><strong>PTY = real interactive terminal</strong> (vs L39 batch bash): batch is one-shot Q&A, can't input mid-way; PTY streams output + type anytime + resize, the program "thinks" it's attached to a live person. The <span class="mono">Proc</span> interface (<span class="mono">pty/pty.ts</span>) = onData/write/resize/onExit/kill, <strong>Bun/Node two implementations satisfy the same interface</strong> (platform difference hidden under the interface, like L52/L46).</li>
    <li><strong>streaming + connecting</strong> (<span class="mono">pty/protocol.ts</span>/<span class="mono">ticket.ts</span>): WebSocket delivers the terminal to clients, raw UTF-8 chunks outbound + cursor control frame (0x00+JSON) for <strong>drop replay</strong>, REPLAY_CHUNK 64KB chunking; connecting needs a <strong>short-lived ticket</strong> (60s, bound to ptyID+directory+workspace, one-time) to guard (strong capability bound to strict authorization, like L41/L46).</li>
    <li><strong>environment stacking (most eye-opening)</strong>: PTY creation merges in order ① caller values → ② host overlay (triggers L58 <span class="mono">shell.env</span> plugin hook) → ③ core-forced terminal invariants (<span class="mono">TERM</span>/<span class="mono">OPENCODE_TERMINAL</span>). <strong>Customizable in the middle, non-negotiable last overriding all</strong>—the later the higher priority, the bottom line gets the highest priority.</li>
    <li><strong>mechanism vs policy layering</strong>: the "PTY Environment" is a server-layer concern, not a Core PTY one—Core only makes the terminal (pure mechanism), "what env to configure" (policy) is left to the more context-aware server layer (standalone server uses an empty adapter). The book's "cut mechanism from policy" aesthetic.</li>
  </ul>
  <p>The real-terminal infrastructure is filled in. M11 has one lesson left, L61: <strong>ACP and the Location model</strong>—how opencode, conversely, gets connected by other editors (like Zed) as an <strong>ACP server</strong>, how sessions move across "Locations," how the control plane coordinates. After L61, the whole M11 "Extensibility and integration" wraps up, and "all the doors opencode opens outward" are fully covered.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p>CONTEXT.md nails the env-stacking order in one sentence, and the <span class="mono">pty-environment</span> plugin is exactly that "middle layer"'s implementation (simplified from source):</p>
  <pre class="code"><span class="cm">// CONTEXT.md: PTY creation merges caller values, then the host</span>
<span class="cm">// overlay, then Core-forced terminal invariants such as TERM</span>
<span class="cm">// i.e.: caller values → host overlay → forced invariants (later overrides earlier)</span>

<span class="cm">// the host-overlay layer = trigger the shell.env plugin hook (lesson 58)</span>
PtyEnvironment.Service.of({
  get: (input) =&gt;
    plugin
      .<span class="fn">trigger</span>(<span class="st">"shell.env"</span>, { cwd: input.cwd }, { env: {} })   <span class="cm">// ← plugins inject into env</span>
      .<span class="fn">pipe</span>(Effect.<span class="fn">map</span>((result) =&gt; result.env)),
})</pre>
  <p>What's most worth savoring is how it <strong>seamlessly embeds lesson 58's plugin mechanism</strong> into the PTY environment's "middle layer." Look at that <span class="mono">plugin.trigger("shell.env", {cwd}, {env:{}})</span>—it's exactly L58's "edit a draft": opencode hands an empty <span class="mono">{env:{}}</span> draft, plugins fill into it, and finally the plugin-edited env is taken as the "host overlay" layer. <strong>So PTY environment customization needn't invent a new mechanism at all—it directly reuses the existing plugin hook.</strong> This is the "<strong>building blocks interlocking</strong>" beauty a well-designed system should have: the <span class="mono">shell.env</span> hook L58 built is a generic block, and here at L60's PTY environment, it <strong>happens to be exactly "that customizable overlay in the middle,"</strong> snapping in perfectly. In a system, when you find "this new need is just a snap-together of some existing mechanism," it often means the earlier abstraction seams were found accurately—they weren't built for one spot but are <strong>generic enough to be reused again in unexpected places</strong>. From L58's shell.env to L60's environment stacking is exactly this "<strong>one block, reused in many places</strong>" exemplar.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>PTY = real interactive terminal</strong> (vs L39 batch bash): batch is one-shot Q&A can't input mid-way, the program knows it's not attached; PTY streams output + type anytime + resize, the program "thinks" it's attached to a live person (REPLs/TTY-requiring tools/real-time human operation). The <span class="mono">Proc</span> interface onData/write/resize/kill, Bun/Node two implementations satisfy the same interface (platform difference hidden under the interface, like L52/L46).</li>
    <li><strong>streaming + connecting</strong>: WebSocket delivers the terminal (<span class="mono">protocol.ts</span>), raw UTF-8 chunks + cursor frame (0x00+JSON) for drop replay, REPLAY_CHUNK 64KB; connecting needs a short-lived ticket (60s/bound to ptyID+directory+workspace/one-time, <span class="mono">ticket.ts</span>) to guard—strong capability bound to strict authorization (like L41/L46).</li>
    <li><strong>environment stacking (most eye-opening)</strong>: PTY creation merges in order ① caller values → ② host overlay (triggers L58 <span class="mono">shell.env</span> hook) → ③ core-forced invariants (<span class="mono">TERM</span>/<span class="mono">OPENCODE_TERMINAL</span>). Customizable in the middle, non-negotiable last overriding all—the later the higher priority, the bottom line gets the highest priority.</li>
    <li><strong>blocks interlocking</strong>: the PTY environment's "middle layer" directly reuses L58's <span class="mono">shell.env</span> hook (<span class="mono">plugin.trigger("shell.env",{cwd},{env:{}})</span> "edit a draft")—a new need snaps together from an existing mechanism, showing the seams were found accurately, the abstraction generic enough for unexpected reuse.</li>
    <li><strong>mechanism vs policy layering</strong>: the "PTY Environment" is a server-layer concern, not a Core PTY one—Core only makes the terminal (pure mechanism), what env to configure (policy) is left to the more context-aware upper layer (standalone server uses an empty adapter). The book's "cut mechanism from policy."</li>
  </ul>
</div>
""",
}
LESSON_61 = {
    "zh": r"""
<p class="lead">M11 一路讲来，我们看了 opencode 向外敞开的好几扇门：插件（L57/58）让你挂进它的生命周期、LSP（L59）让它接来语言服务器的大脑、PTY（L60）让它管理真终端。这最后一课，讲的是<strong>最深的一层敞开</strong>——它不再是「给 opencode 加点什么」，而是把 <strong>agent 本身</strong>，变成一个<strong>不绑定特定前端、也不绑定特定位置</strong>的、可被任意驱动、可自由移动的实体。这背后是两个抽象：<strong>ACP</strong>（让 opencode 反过来作为一个「agent 服务器」，被别的编辑器接入）和 <strong>Location</strong>（把「会话」和「它在哪儿跑」彻底解耦的「位置」抽象）。读完这一课，你会看到 opencode 把「向外敞开」做到了一个深刻的层次：连「谁来用这个 agent」「这个 agent 在哪儿干活」，都成了可替换、可移动的。</p>
<p>这一课有两个最值得带走的洞见。第一，<strong>ACP 是 LSP 的镜像</strong>。还记得 L59 吗——那里 opencode 是 <strong>LSP 客户端</strong>，去<strong>消费</strong>语言服务器的代码智能。而这里反了过来：opencode 实现了 <strong>ACP（Agent Client Protocol，智能体客户端协议）</strong>、把自己变成一个 <strong>ACP 服务器</strong>，被别的编辑器（如 Zed）<strong>消费</strong>——编辑器当「客户端」、opencode 当「agent 后端」。<span class="mono">ACP 之于 agent，正如 LSP 之于语言服务器</span>：都用一套标准协议，把「M 个编辑器 × N 个 agent」的难题塌缩成「M + N」。第二，<strong>Location 把「会话」与「它在哪儿跑」解耦了</strong>。一个 <span class="mono">Location</span> 不过是 <span class="mono">{目录, 工作区, 项目}</span> 这么一份「位置信息」，而 opencode 把工具、权限、文件系统、模型解析全都做成 <strong>Location 作用域</strong>的——于是一个会话<strong>不被钉死在某一个位置</strong>，它能被 <span class="mono">move-session</span> 连同它的文件改动一起<strong>搬到另一个目录</strong>去继续。读懂这两点，你就懂了贯穿这一课的那条主线：<strong>把「是什么」和「在哪里」解耦——agent 不绑定编辑器、会话不绑定目录。</strong></p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  把 <strong>ACP</strong> 想象成<strong>统一的电源插座标准</strong>。有了这套标准，任何电器（编辑器）都能插上任何电源（agent），只要两边都遵守这个插座规格——不必为「Zed 配 opencode」「某编辑器配某 agent」各造一套专用接口。L59 里 opencode 是「电器」（去插语言服务器这个「电源」），而这一课里它成了「电源」（被编辑器这个「电器」插上）。同一套协议，opencode 两头都能站。而 <strong>Location 与 move-session</strong>，则像一台<strong>不绑定某张书桌的笔记本电脑</strong>。你的工作（会话）活在笔记本里，而不是焊死在某张桌子上——你可以<strong>合上电脑、换一张桌子（换一个目录），打开继续干</strong>，连桌上那些没保存的草稿（未提交的文件改动）都能一起带走。<strong>正因为「工作」和「哪张桌子」是分开的，工作才有了「可移动」的自由</strong>；正因为 agent 和「哪个编辑器」是分开的、会话和「哪个目录」是分开的，它们才有了被任意前端驱动、在任意位置流转的自由。
</div>

<h2>ACP：opencode 反过来做「agent 服务器」</h2>
<p>L59 里，opencode 戴上「LSP 客户端」的帽子，去消费别人的语言服务器。这一课，它戴上另一顶帽子——<strong>ACP 服务器</strong>。<strong>ACP（Agent Client Protocol）</strong>是一套让「编辑器」和「AI agent」对话的标准协议（正是 Zed 等编辑器接入 AI agent 用的那套）。opencode 实现了它，于是别的编辑器能把 opencode <strong>当成自己的 AI 后端</strong>来驱动。把它和 L59 并排，这对「镜像」就清晰了：</p>
<div class="cols">
  <div class="col"><h4>L59：opencode 是 LSP 客户端</h4><p>opencode <strong>消费</strong>语言服务器（typescript-language-server…）的代码智能。它是「编辑器」那一头，去接「语言服务」。</p></div>
  <div class="col"><h4>L61：opencode 是 ACP 服务器</h4><p>opencode <strong>被</strong>编辑器（Zed…）消费，提供 agent 能力。它是「agent 服务」那一头，被「编辑器」接。</p></div>
</div>
<p>opencode 的 ACP 实现（<span class="mono">acp/agent.ts</span>）是一个实现了标准 <span class="mono">ACPAgent</span> 接口的 <span class="mono">Agent</span> 类，它把 agent 的全部能力，翻译成 ACP 协议规定的一组方法：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">initialize / authenticate</div><div class="c-txt">握手、认证——编辑器接上 opencode 的第一步</div></div>
  <div class="cell"><div class="c-tag">newSession / loadSession / forkSession</div><div class="c-txt">开新会话 / 载入 / 分叉——会话的生命周期管理</div></div>
  <div class="cell"><div class="c-tag">prompt / cancel</div><div class="c-txt">发提示词 / 取消——和 agent 的核心来回</div></div>
  <div class="cell"><div class="c-tag">setSessionModel / Mode / ConfigOption</div><div class="c-txt">切模型 / 切模式 / 调选项——编辑器侧的控制</div></div>
</div>
<p>这套实现的意义，怎么强调都不为过：<strong>它让 opencode 这颗 agent 内核，挣脱了「只能用 opencode 自家 TUI」的绑定。</strong>一个用惯了 Zed 的开发者，不必离开 Zed、不必学一套新界面，就能在自己最熟的编辑器里，用上 opencode 这颗 agent。而这正是协议的力量——<strong>ACP 把「agent 的能力」和「展示它的前端」彻底切开</strong>：opencode 只管做好一个标准的 ACP 服务器，剩下「用什么编辑器、长什么样」全交给客户端。回想 L56 我们曾说「同一份会话能渲染成 TUI、也能渲染成 run 日志」——那是 opencode <strong>自己</strong>的多副前端；而 ACP 把这个「前端可替换」的范围，扩张到了<strong>整个生态的任意编辑器</strong>。这是「数据与表现分离」在协议层面的终极形态。</p>

<h2>Location：把「会话」与「它在哪儿跑」解耦</h2>
<p>第二个抽象更底层，也更精妙。<span class="mono">Location</span>（<span class="mono">core/src/location.ts</span>）回答一个看似简单的问题：「<strong>一个会话，到底在哪儿干活？</strong>」它的答案，是一份极简的「位置信息」：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">directory</div><div class="c-txt">工作目录——agent 在哪个目录下读写文件、跑命令</div></div>
  <div class="cell"><div class="c-tag">workspaceID?</div><div class="c-txt">可选的工作区标识（为未来的集群/远程放置预留）</div></div>
  <div class="cell"><div class="c-tag">project</div><div class="c-txt">解析出的项目（id + 根目录）——这个目录属于哪个项目</div></div>
</div>
<p>这份「位置」看着不起眼，但 opencode 的一个核心设计决定让它分量极重：<strong>工具、权限、文件系统、模型解析、会话运行器（SessionRunner）……全都是「Location 作用域」的。</strong>把这些「跟着 Location 走」的子系统列出来，你就能体会这份解耦有多彻底：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">文件系统</div><div class="c-txt">能读写哪些文件、相对哪个目录解析——随 Location 定</div></div>
  <div class="cell"><div class="c-tag">权限</div><div class="c-txt">L41 的权限规则在哪个目录上生效——随 Location 定</div></div>
  <div class="cell"><div class="c-tag">工具注册表</div><div class="c-txt">L37 的工具绑在哪个 Location 上自我登记</div></div>
  <div class="cell"><div class="c-tag">模型解析 / 运行器</div><div class="c-txt">用哪个模型、SessionRunner 在哪儿跑——皆 Location 作用域</div></div>
</div>
<p>也就是说，「能读写哪些文件」「权限规则怎么算」「用哪个模型」这些，都是<strong>相对于一个 Location 来确定的</strong>，而非写死在某个全局状态里。这个决定的深远之处在于：它把<strong>「会话是谁、要干什么」（身份与逻辑）</strong>和<strong>「会话在哪儿跑」（位置）</strong>，变成了<strong>两件正交、可分别替换的事</strong>。一个会话的「灵魂」（它的消息、上下文、意图）不再和某个具体目录焊死——你换一个 Location，同一个会话就能在新的目录下、用新的文件系统视图和权限继续跑。<strong>这正是「把『是什么』和『在哪里』解耦」在系统最底层的落地。</strong></p>

<h2>move-session：会话因此能「搬家」</h2>
<p>Location 解耦带来的最直接、最能让人「啊哈」的回报，就是 <span class="mono">move-session</span>（<span class="mono">control-plane/move-session.ts</span>）——一个会话能<strong>整体搬到另一个目录</strong>去继续。既然会话不被钉死在原地，「搬家」就成了可能。它的流程很见功力：</p>
<div class="flow">
  <div class="f-node">move(会话, 目的目录)<br><small>moveChanges?</small></div>
  <div class="f-arrow">校验 →</div>
  <div class="f-node">目的项目须匹配<br><small>否则 ProjectMismatch</small></div>
  <div class="f-arrow">捕获 →</div>
  <div class="f-node">用 git 捕获工作改动<br><small>把未提交的改动打包</small></div>
  <div class="f-arrow">搬运+应用 →</div>
  <div class="f-node">在目的目录重放改动<br><small>会话在新位置继续</small></div>
</div>
<p>这条流水里藏着几处老练的考量。其一，<strong>校验目的地的项目必须匹配</strong>（<span class="mono">DestinationProjectMismatchError</span>）——你不能把一个会话搬到一个<strong>属于完全不同项目</strong>的目录去，那样会话的上下文就全乱了；这道校验守住了「搬家可以，但得搬到同一个项目的另一处」的边界。其二，<strong>可选地连同文件改动一起搬</strong>（<span class="mono">moveChanges</span>）：它用 <strong>git</strong> 在源目录<strong>捕获</strong>会话造成的未提交改动、再在目的目录<strong>应用</strong>（<span class="mono">CaptureChangesError</span>/<span class="mono">ApplyChangesError</span> 守着这两步）——又一次复用 git 这把利器（同 L51 快照），让「搬家」连「桌上的草稿」都不落下。<strong>而这一切之所以可能、之所以不是天方夜谭，根全在上一节那个 Location 解耦上</strong>：正因为会话的逻辑早已和「具体在哪个目录」剥离开，「换一个目录继续」才不过是「给它一个新 Location + 把改动带过去」这么一件自然的事。<strong>一个好的底层抽象（Location），会在你意想不到的上层（move-session）开出花来</strong>——这正是 L60 末尾「积木相扣」那个主题的又一次印证：会话可移动这个看似高级的能力，根本没有专门为它写一套复杂逻辑，它只是「会话本就和位置解耦」这个地基上，自然生长出的一颗果子。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观视角</div>
  <p>这一课收束 M11——ACP 与 Location，opencode「向外敞开」最深的一层：</p>
  <ul>
    <li><strong>ACP=LSP 的镜像</strong>：L59 opencode 是 LSP <strong>客户端</strong>（消费语言服务器）；L61 opencode 实现 <strong>ACP（Agent Client Protocol）</strong>、做 <strong>ACP 服务器</strong>，被编辑器（Zed…）消费当 AI 后端。<span class="mono">acp/agent.ts</span> 的 <span class="mono">Agent</span> 实现 <span class="mono">ACPAgent</span> 接口：initialize/authenticate/newSession/loadSession/forkSession/prompt/cancel/setSessionModel·Mode·ConfigOption。ACP:agent = LSP:语言服务器，把 M 编辑器×N agent 塌缩成 M+N。</li>
    <li><strong>把 agent 能力与前端切开</strong>：ACP 让 opencode 内核挣脱「只能用自家 TUI」——Zed 用户不离开 Zed 就能用 opencode。是 L56「数据与表现分离」在协议层的终极形态（前端可替换范围扩到整个生态）。</li>
    <li><strong>Location=「在哪儿跑」抽象</strong>（<span class="mono">location.ts</span>）：<span class="mono">{directory, workspaceID?, project}</span>。工具/权限/文件系统/模型解析/SessionRunner 全 <strong>Location 作用域</strong>——把「会话是谁要干什么」（身份逻辑）与「在哪儿跑」（位置）解耦成正交可替换两件事。</li>
    <li><strong>move-session=会话可搬家</strong>（<span class="mono">control-plane/move-session.ts</span>）：校验目的项目匹配（ProjectMismatch）→git 捕获工作改动→目的目录重放（可选 moveChanges，复用 git 同 L51）。会话可移动这个高级能力，是 Location 解耦地基上自然生长的果（积木相扣，同 L60）。</li>
  </ul>
  <p>贯穿主线：<strong>把「是什么」和「在哪里」解耦</strong>——agent 不绑定编辑器（ACP）、会话不绑定目录（Location/move-session）。把这两条解耦并排，这一课的主旨就一目了然：</p>
  <div class="cols">
    <div class="col"><h4>ACP：解耦「agent」与「编辑器」</h4><p>agent 能力不绑定某个前端；任意会 ACP 的编辑器都能驱动 opencode。「谁来用」可替换。</p></div>
    <div class="col"><h4>Location：解耦「会话」与「目录」</h4><p>会话逻辑不绑定某个位置；换个 Location 就换个文件系统/权限视图。「在哪儿跑」可替换、可移动。</p></div>
  </div>
  <p>至此 <strong>M11「扩展与集成」收官</strong>：从插件、LSP、PTY，到 ACP 与 Location，opencode「向外敞开的所有门」讲全了。最后一部分 <strong>M12 转向实战、贡献与速查</strong>：怎么在本地把 opencode 构建调试起来（L62）、怎么测试与给它贡献代码（L63）、以及一份贯通全书的术语表与索引（L64），为整本 opencode 学习指南收尾。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p><span class="mono">Location.Info</span> 这个极简的数据类，是「会话与位置解耦」的支点（简化自 <span class="mono">location.ts</span>）：</p>
  <pre class="code"><span class="cm">// 一份「位置信息」：目录 + 可选工作区 + 解析出的项目</span>
<span class="kw">class</span> Info <span class="kw">extends</span> Schema.Class(<span class="st">"Location.Info"</span>)({
  directory: AbsolutePath,                   <span class="cm">// agent 在哪个目录干活</span>
  workspaceID: optional(WorkspaceV2.ID),     <span class="cm">// 可选（为集群/远程放置预留）</span>
  project: { id: Project.ID, directory: AbsolutePath },  <span class="cm">// 属于哪个项目</span>
}) {}

<span class="cm">// Location 作为一个 Effect 服务，按一个 Ref(目录) 解析出来</span>
<span class="kw">const</span> layer = (ref: Ref) =&gt; Layer.<span class="fn">effect</span>(Service, Effect.<span class="fn">gen</span>(<span class="kw">function*</span>() {
  <span class="kw">const</span> resolved = <span class="kw">yield*</span> project.<span class="fn">resolve</span>(ref.directory)   <span class="cm">// 目录→项目</span>
  <span class="kw">return</span> Service.<span class="fn">of</span>({ directory: ref.directory, project: {...}, ... })
}))</pre>
  <p>这个类小得不能再小，但它在 opencode 架构里的位置极其关键——<strong>它是一条「接缝」，把一整个会话从「它在哪儿」这件事上剥离了开来。</strong>注意它被实现成一个 Effect 的 <span class="mono">Service</span>（第 2 部分的依赖注入）：工具、权限、文件系统这些子系统，都<strong>通过依赖这个 <span class="mono">Location.Service</span> 来确定自己的作用域</strong>，而非各自去摸一个全局的「当前目录」。这一个小小的设计选择，带来了惊人的杠杆：<strong>因为「位置」是被注入的、而非写死的，所以换一份 Location，整个会话的「文件系统视图、权限边界、能跑的命令」就整体平移到了新位置——而会话的逻辑代码一行都不用改。</strong>这正是依赖注入（M2）最深刻的威力：把一个横切一切的关注点（「在哪儿」）抽成一个可注入的服务，于是「换地方」从「改一大堆硬编码路径」的噩梦，变成了「换一个注入值」的举手之劳。<span class="mono">workspaceID</span> 那个「为未来集群/远程放置预留」的可选字段，更透露了这条接缝的雄心：今天它让会话能在本地不同目录间搬家，明天它就能让会话在<strong>不同机器、不同远程位置</strong>间流转。<strong>一个想透了的底层抽象，不只解决眼前的问题，还为还没到来的未来，悄悄留好了门。</strong></p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>ACP=LSP 的镜像</strong>：L59 opencode 是 LSP 客户端（消费语言服务器）；L61 opencode 实现 ACP（Agent Client Protocol）做 ACP 服务器，被编辑器（Zed…）消费当 AI 后端。<span class="mono">acp/agent.ts</span> <span class="mono">Agent</span> 实现 <span class="mono">ACPAgent</span>：initialize/newSession/loadSession/forkSession/prompt/cancel/setSessionModel·Mode。ACP:agent=LSP:语言服务器，M×N 塌缩 M+N。</li>
    <li><strong>agent 能力与前端切开</strong>：ACP 让 opencode 内核挣脱「只能用自家 TUI」，Zed 用户不离开 Zed 就能用。L56「数据与表现分离」在协议层的终极形态——前端可替换扩到整个生态。</li>
    <li><strong>Location=「在哪儿跑」抽象</strong>（<span class="mono">location.ts</span>）：<span class="mono">{directory, workspaceID?, project}</span>，实现成 Effect <span class="mono">Service</span>（DI）。工具/权限/文件系统/模型/SessionRunner 全 Location 作用域——把「会话是谁要干什么」与「在哪儿跑」解耦成正交可替换两件事。</li>
    <li><strong>move-session=会话可搬家</strong>（<span class="mono">control-plane/move-session.ts</span>）：校验目的项目匹配→git 捕获改动→目的目录重放（可选 moveChanges 复用 git 同 L51）。高级能力是 Location 解耦地基上自然生长的果（积木相扣，同 L60）。</li>
    <li><strong>主线：解耦「是什么」与「在哪里」</strong>——agent 不绑定编辑器（ACP）、会话不绑定目录（Location）。DI 把「在哪儿」抽成可注入服务=换地方只需换注入值、逻辑零改；<span class="mono">workspaceID</span> 为未来跨机器/远程放置留门。M11 收官。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">All through M11 we've seen several doors opencode opens outward: plugins (L57/58) let you hook into its lifecycle, LSP (L59) lets it borrow language servers' brains, PTY (L60) lets it manage real terminals. This final lesson covers <strong>the deepest layer of opening</strong>—it's no longer "add something to opencode" but making <strong>the agent itself</strong> an entity <strong>not bound to a specific frontend, nor to a specific location</strong>, drivable by anyone, freely movable. Behind this are two abstractions: <strong>ACP</strong> (letting opencode, conversely, be an "agent server" that other editors connect to) and <strong>Location</strong> (the "place" abstraction that fully decouples a "session" from "where it runs"). After this lesson, you'll see opencode took "opening outward" to a profound level: even "who uses this agent" and "where this agent works" become replaceable and movable.</p>
<p>This lesson has two highlights most worth taking away. First, <strong>ACP is the mirror of LSP</strong>. Remember L59—there opencode was an <strong>LSP client</strong>, going to <strong>consume</strong> language servers' code intelligence. Here it's reversed: opencode implements <strong>ACP (Agent Client Protocol)</strong>, making itself an <strong>ACP server</strong> to be <strong>consumed</strong> by other editors (like Zed)—the editor as "client," opencode as "agent backend." <span class="mono">ACP is to agents what LSP is to language servers</span>: both use a standard protocol to collapse the "M editors × N agents" problem into "M + N." Second, <strong>Location decouples a "session" from "where it runs."</strong> A <span class="mono">Location</span> is just a piece of "location info," <span class="mono">{directory, workspace, project}</span>, and opencode makes tools, permissions, the filesystem, model resolution all <strong>Location-scoped</strong>—so a session <strong>isn't nailed to one location</strong>, it can be <span class="mono">move-session</span>'d, along with its file changes, <strong>to another directory</strong> to continue. Grasp these two and you'll understand this lesson's throughline: <strong>decoupling "what" from "where"—the agent isn't bound to the editor, the session isn't bound to the directory.</strong></p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  Picture <strong>ACP</strong> as a <strong>unified power-socket standard</strong>. With this standard, any appliance (editor) can plug into any power source (agent), as long as both follow the socket spec—no need to build a dedicated interface for "Zed with opencode," "some editor with some agent." In L59 opencode was the "appliance" (plugging into language servers, the "power"), and here it becomes the "power" (plugged into by editors, the "appliances"). Same protocol, opencode can stand at either end. And <strong>Location and move-session</strong> are like a <strong>laptop not tied to one desk</strong>. Your work (the session) lives in the laptop, not welded to a desk—you can <strong>close the lid, switch desks (switch directories), open and keep working</strong>, even carrying along the unsaved drafts on the desk (uncommitted file changes). <strong>Precisely because "the work" and "which desk" are separated, the work gains the freedom to be "movable"</strong>; precisely because the agent and "which editor," the session and "which directory," are separated, they gain the freedom to be driven by any frontend and to flow across any location.
</div>

<h2>ACP: opencode conversely as an "agent server"</h2>
<p>In L59, opencode wore the "LSP client" hat, going to consume others' language servers. This lesson, it wears another hat—<strong>ACP server</strong>. <strong>ACP (Agent Client Protocol)</strong> is a standard protocol letting "editors" and "AI agents" talk (exactly what editors like Zed use to connect AI agents). opencode implements it, so other editors can drive opencode <strong>as their own AI backend</strong>. Side by side with L59, this "mirror" pair is clear:</p>
<div class="cols">
  <div class="col"><h4>L59: opencode is an LSP client</h4><p>opencode <strong>consumes</strong> language servers' (typescript-language-server…) code intelligence. It's the "editor" end, plugging into "language services."</p></div>
  <div class="col"><h4>L61: opencode is an ACP server</h4><p>opencode <strong>is consumed</strong> by editors (Zed…), providing agent capability. It's the "agent service" end, plugged into by "editors."</p></div>
</div>
<p>opencode's ACP implementation (<span class="mono">acp/agent.ts</span>) is an <span class="mono">Agent</span> class implementing the standard <span class="mono">ACPAgent</span> interface, translating the agent's full capabilities into a set of methods ACP prescribes:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">initialize / authenticate</div><div class="c-txt">handshake, auth—the editor's first step attaching to opencode</div></div>
  <div class="cell"><div class="c-tag">newSession / loadSession / forkSession</div><div class="c-txt">open new session / load / fork—session lifecycle management</div></div>
  <div class="cell"><div class="c-tag">prompt / cancel</div><div class="c-txt">send a prompt / cancel—the core back-and-forth with the agent</div></div>
  <div class="cell"><div class="c-tag">setSessionModel / Mode / ConfigOption</div><div class="c-txt">switch model / mode / tweak options—editor-side control</div></div>
</div>
<p>The significance of this implementation can't be overstated: <strong>it frees opencode's agent core from the binding of "usable only in opencode's own TUI."</strong> A developer used to Zed needn't leave Zed, needn't learn a new interface, yet can use opencode's agent in their most familiar editor. And this is exactly the power of a protocol—<strong>ACP fully cuts "the agent's capability" from "the frontend showing it"</strong>: opencode just needs to be a good standard ACP server, leaving "which editor, what it looks like" all to the client. Recall L56 where we said "the same session can render as a TUI or as a run log"—that was opencode's <strong>own</strong> multiple frontends; ACP expands this "frontend replaceability" to <strong>any editor in the whole ecosystem</strong>. This is the ultimate form of "data separated from presentation" at the protocol level.</p>

<h2>Location: decoupling "the session" from "where it runs"</h2>
<p>The second abstraction is lower-level and more exquisite. <span class="mono">Location</span> (<span class="mono">core/src/location.ts</span>) answers a seemingly simple question: "<strong>where exactly does a session work?</strong>" Its answer is a minimal piece of "location info":</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">directory</div><div class="c-txt">the working directory—which directory the agent reads/writes files and runs commands in</div></div>
  <div class="cell"><div class="c-tag">workspaceID?</div><div class="c-txt">an optional workspace identifier (reserved for future cluster/remote placement)</div></div>
  <div class="cell"><div class="c-tag">project</div><div class="c-txt">the resolved project (id + root directory)—which project this directory belongs to</div></div>
</div>
<p>This "location" looks unremarkable, but a core opencode design decision makes it hugely weighty: <strong>tools, permissions, the filesystem, model resolution, the SessionRunner… are all "Location-scoped."</strong> Listing these subsystems that "go with the Location," you feel how thorough this decoupling is:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">filesystem</div><div class="c-txt">which files can be read/written, relative to which directory—per Location</div></div>
  <div class="cell"><div class="c-tag">permissions</div><div class="c-txt">which directory L41's permission rules take effect on—per Location</div></div>
  <div class="cell"><div class="c-tag">tool registry</div><div class="c-txt">L37's tools self-register bound to which Location</div></div>
  <div class="cell"><div class="c-tag">model resolution / runner</div><div class="c-txt">which model, where the SessionRunner runs—all Location-scoped</div></div>
</div>
<p>That is, "which files can be read/written," "how permission rules compute," "which model to use" are all <strong>determined relative to a Location</strong>, not hardcoded into some global state. The profundity of this decision: it turns <strong>"who the session is, what it wants to do" (identity and logic)</strong> and <strong>"where the session runs" (location)</strong> into <strong>two orthogonal, separately-replaceable things</strong>. A session's "soul" (its messages, context, intent) is no longer welded to a specific directory—switch a Location and the same session can keep running under a new directory, with a new filesystem view and permissions. <strong>This is exactly "decoupling 'what' from 'where'" landing at the system's deepest level.</strong></p>

<h2>move-session: so a session can "move house"</h2>
<p>The most direct, most "aha" payoff of the Location decoupling is <span class="mono">move-session</span> (<span class="mono">control-plane/move-session.ts</span>)—a session can be <strong>moved wholesale to another directory</strong> to continue. Since the session isn't nailed in place, "moving house" becomes possible. Its flow is quite crafty:</p>
<div class="flow">
  <div class="f-node">move(session, dest dir)<br><small>moveChanges?</small></div>
  <div class="f-arrow">validate →</div>
  <div class="f-node">dest project must match<br><small>else ProjectMismatch</small></div>
  <div class="f-arrow">capture →</div>
  <div class="f-node">git-capture working changes<br><small>package uncommitted edits</small></div>
  <div class="f-arrow">move+apply →</div>
  <div class="f-node">replay changes at dest<br><small>session continues at new location</small></div>
</div>
<p>This flow hides several seasoned considerations. First, <strong>validate the destination's project must match</strong> (<span class="mono">DestinationProjectMismatchError</span>)—you can't move a session to a directory <strong>belonging to a completely different project</strong>, that would scramble the session's context; this validation holds the boundary "moving is fine, but to another spot of the same project." Second, <strong>optionally move the file changes along</strong> (<span class="mono">moveChanges</span>): it uses <strong>git</strong> to <strong>capture</strong> the session's uncommitted changes in the source directory and <strong>apply</strong> them in the destination (<span class="mono">CaptureChangesError</span>/<span class="mono">ApplyChangesError</span> guarding these two steps)—reusing git, that sharp tool, again (like L51 snapshots), so "moving house" doesn't leave even "the drafts on the desk" behind. <strong>And all this is possible, isn't a fantasy, entirely thanks to the Location decoupling of the last section</strong>: precisely because the session's logic was long peeled apart from "which directory it's in," "continue in another directory" is no more than "give it a new Location + bring the changes over," a natural thing. <strong>A good low-level abstraction (Location) blossoms in unexpected upper layers (move-session)</strong>—exactly another proof of L60's closing "blocks interlocking" theme: this seemingly advanced "session is movable" capability needed no complex logic written specially for it, it's just a fruit naturally grown on the foundation of "the session is already decoupled from location."</p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>This lesson closes M11—ACP and Location, opencode's deepest layer of "opening outward":</p>
  <ul>
    <li><strong>ACP = the mirror of LSP</strong>: L59 opencode is an LSP <strong>client</strong> (consumes language servers); L61 opencode implements <strong>ACP (Agent Client Protocol)</strong>, being an <strong>ACP server</strong>, consumed by editors (Zed…) as an AI backend. <span class="mono">acp/agent.ts</span>'s <span class="mono">Agent</span> implements the <span class="mono">ACPAgent</span> interface: initialize/authenticate/newSession/loadSession/forkSession/prompt/cancel/setSessionModel·Mode·ConfigOption. ACP:agent = LSP:language servers, collapsing M editors×N agents into M+N.</li>
    <li><strong>cutting agent capability from the frontend</strong>: ACP frees opencode's core from "usable only in its own TUI"—a Zed user uses opencode without leaving Zed. The ultimate form of L56's "data separated from presentation" at the protocol level (frontend replaceability expanded to the whole ecosystem).</li>
    <li><strong>Location = the "where it runs" abstraction</strong> (<span class="mono">location.ts</span>): <span class="mono">{directory, workspaceID?, project}</span>. Tools/permissions/filesystem/model resolution/SessionRunner all <strong>Location-scoped</strong>—decoupling "who the session is, what it wants" (identity logic) from "where it runs" (location) into two orthogonal, replaceable things.</li>
    <li><strong>move-session = a session can move house</strong> (<span class="mono">control-plane/move-session.ts</span>): validate destination project match (ProjectMismatch)→git-capture working changes→replay at destination (optional moveChanges, reusing git like L51). The advanced "session is movable" capability is a fruit naturally grown on the Location-decoupling foundation (blocks interlocking, like L60).</li>
  </ul>
  <p>The throughline: <strong>decoupling "what" from "where"</strong>—the agent isn't bound to the editor (ACP), the session isn't bound to the directory (Location/move-session). Putting these two decouplings side by side, this lesson's thesis is clear at a glance:</p>
  <div class="cols">
    <div class="col"><h4>ACP: decouple "agent" from "editor"</h4><p>agent capability isn't bound to a frontend; any ACP-speaking editor can drive opencode. "Who uses it" is replaceable.</p></div>
    <div class="col"><h4>Location: decouple "session" from "directory"</h4><p>session logic isn't bound to a location; switch a Location and switch the filesystem/permission view. "Where it runs" is replaceable, movable.</p></div>
  </div>
  <p>With this, <strong>M11 "Extensibility and integration" wraps up</strong>: from plugins, LSP, PTY, to ACP and Location, "all the doors opencode opens outward" are fully covered. The last part <strong>M12 turns to practice, contribution, and reference</strong>: how to build and debug opencode locally (L62), how to test and contribute code to it (L63), and a glossary and index threading the whole book (L64), closing out the entire opencode learning guide.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p><span class="mono">Location.Info</span>, this minimal data class, is the fulcrum of "decoupling session from location" (simplified from <span class="mono">location.ts</span>):</p>
  <pre class="code"><span class="cm">// a piece of "location info": directory + optional workspace + resolved project</span>
<span class="kw">class</span> Info <span class="kw">extends</span> Schema.Class(<span class="st">"Location.Info"</span>)({
  directory: AbsolutePath,                   <span class="cm">// which directory the agent works in</span>
  workspaceID: optional(WorkspaceV2.ID),     <span class="cm">// optional (reserved for cluster/remote placement)</span>
  project: { id: Project.ID, directory: AbsolutePath },  <span class="cm">// which project it belongs to</span>
}) {}

<span class="cm">// Location is an Effect service, resolved from a Ref(directory)</span>
<span class="kw">const</span> layer = (ref: Ref) =&gt; Layer.<span class="fn">effect</span>(Service, Effect.<span class="fn">gen</span>(<span class="kw">function*</span>() {
  <span class="kw">const</span> resolved = <span class="kw">yield*</span> project.<span class="fn">resolve</span>(ref.directory)   <span class="cm">// directory→project</span>
  <span class="kw">return</span> Service.<span class="fn">of</span>({ directory: ref.directory, project: {...}, ... })
}))</pre>
  <p>This class is as tiny as can be, but its place in opencode's architecture is utterly crucial—<strong>it's a "seam" that peels an entire session apart from the matter of "where it is."</strong> Note it's implemented as an Effect <span class="mono">Service</span> (Part 2's dependency injection): subsystems like tools, permissions, the filesystem all <strong>determine their scope by depending on this <span class="mono">Location.Service</span></strong>, rather than each reaching for a global "current directory." This one small design choice brings astonishing leverage: <strong>because "location" is injected, not hardcoded, switching a Location shifts the whole session's "filesystem view, permission boundary, runnable commands" to a new place wholesale—without changing one line of the session's logic code.</strong> This is exactly dependency injection's (M2) most profound power: abstracting a concern that cuts across everything ("where") into an injectable service, so "switching places" turns from the nightmare of "changing a pile of hardcoded paths" into the trivial "swap one injected value." That <span class="mono">workspaceID</span> optional field "reserved for future cluster/remote placement" further reveals this seam's ambition: today it lets a session move house among local directories, tomorrow it can let a session flow across <strong>different machines, different remote locations</strong>. <strong>A well-thought-through low-level abstraction doesn't just solve the problem at hand but quietly leaves a door open for a future not yet arrived.</strong></p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>ACP = the mirror of LSP</strong>: L59 opencode is an LSP client (consumes language servers); L61 opencode implements ACP (Agent Client Protocol) as an ACP server, consumed by editors (Zed…) as an AI backend. <span class="mono">acp/agent.ts</span>'s <span class="mono">Agent</span> implements <span class="mono">ACPAgent</span>: initialize/newSession/loadSession/forkSession/prompt/cancel/setSessionModel·Mode. ACP:agent = LSP:language servers, M×N collapses to M+N.</li>
    <li><strong>cutting agent capability from the frontend</strong>: ACP frees opencode's core from "usable only in its own TUI," a Zed user uses it without leaving Zed. The ultimate form of L56's "data separated from presentation" at the protocol level—frontend replaceability expanded to the whole ecosystem.</li>
    <li><strong>Location = the "where it runs" abstraction</strong> (<span class="mono">location.ts</span>): <span class="mono">{directory, workspaceID?, project}</span>, implemented as an Effect <span class="mono">Service</span> (DI). Tools/permissions/filesystem/model/SessionRunner all Location-scoped—decoupling "who the session is, what it wants" from "where it runs" into two orthogonal, replaceable things.</li>
    <li><strong>move-session = a session can move house</strong> (<span class="mono">control-plane/move-session.ts</span>): validate destination project match→git-capture changes→replay at destination (optional moveChanges reusing git like L51). The advanced capability is a fruit naturally grown on the Location-decoupling foundation (blocks interlocking, like L60).</li>
    <li><strong>throughline: decouple "what" from "where"</strong>—the agent isn't bound to the editor (ACP), the session isn't bound to the directory (Location). DI abstracts "where" into an injectable service = switching places needs only swapping the injected value, zero logic change; <span class="mono">workspaceID</span> leaves a door open for future cross-machine/remote placement. M11 wraps up.</li>
  </ul>
</div>
""",
}
