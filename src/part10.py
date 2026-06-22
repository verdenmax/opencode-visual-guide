"""Part 10 (Part 10 · The TUI) content. Placeholders until M10 fills them in."""
from placeholder import wip

LESSON_52 = {
    "zh": r"""
<p class="lead">M9 把 agent 的「记忆」忠实地存好、管好了。但记忆躺在 SQLite 里没人看见——它最终得<strong>被渲染成一个你能看、能输入、能交互的界面</strong>。从这一课起的 M10，讲的就是 opencode 的 <strong>TUI（Terminal User Interface，终端用户界面）</strong>：那个你敲 <span class="mono">opencode</span> 后弹出来的、有侧边栏、有对话流、能打字能滚动的漂亮终端界面。但这里有个根本难题：终端本质上只是一块<strong>能显示字符的网格</strong>，没有 DOM、没有 CSS、没有浏览器——你要怎么在这么原始的画布上，盖出一座<strong>响应式、可交互</strong>的现代 UI？opencode 的答案是 <strong>opentui</strong>：一个把 <strong>SolidJS 渲染到终端</strong>的渲染器。你照样写 JSX（<span class="mono">&lt;box&gt;</span>、<span class="mono">&lt;text&gt;</span>）、照样用 signal 做响应式，而 opentui 负责把这棵组件树<strong>画成终端里的一个个字符格</strong>。这一课是 M10 的地基：opentui 到底是什么、它如何把一棵组件树变成终端上的「像素」。</p>
<p>这一课最值得带走的洞见，是一句话：<strong>opentui 就是「终端里的浏览器」</strong>。它把整套 Web 渲染范式<strong>原样搬进了 TTY</strong>——一棵 DOM 般的元素树、一个 flexbox 布局引擎、一个 60fps 的绘制循环、一套键盘/鼠标事件，甚至一个出错时弹出的控制台浮层。这意味着：你用<strong>和写网页一模一样的心智模型</strong>（SolidJS 组件、signal、JSX、flex 布局）来搭一个终端 App，而 opentui 把「这棵组件树怎么变成屏幕上的字符」这件脏活全包了。这是一记极高杠杆的复用：opencode <strong>不必为终端发明一套全新的 UI 框架</strong>，而是直接借来 SolidJS 久经考验的细粒度响应式 + 程序员人人都懂的 flexbox 模型。读懂这一层，你就懂了「为什么 opencode 的 TUI 代码读起来像在写一个 React/Solid 网页，只不过跑在了终端里」。</p>

<div class="card analogy">
  <div class="tag">🖥️ 生活类比</div>
  <strong>opentui 之于终端，正如浏览器之于网页。</strong>浏览器拿到 HTML/CSS/JS，在你眼前画出一个个像素；opentui 拿到 JSX/flex 属性/signal，在终端里画出一个个<strong>字符格</strong>。一一对应得严丝合缝：网页里的 <span class="mono">&lt;div&gt;</span>，在终端里是 <span class="mono">&lt;box&gt;</span>（装东西的盒子）；网页的文字节点，是 <span class="mono">&lt;text&gt;</span>；CSS 的 flexbox 布局，是 box 上的 <span class="mono">flexDirection</span>/<span class="mono">flexGrow</span> 属性；浏览器那个每秒重绘的 <span class="mono">requestAnimationFrame</span>，是 opentui 的 60fps 绘制循环；网页的点击/键入事件，是终端的鼠标/键盘事件。<strong>你脑子里那套「写网页」的肌肉记忆，几乎可以原封不动地拿来「写终端 App」</strong>——这正是 opentui 最大的善意：它没逼你学一套全新的终端绘图 API，而是把你早已烂熟的浏览器模型，整个挪到了那块只能显示字符的小黑屏上。
</div>

<h2>opentui 是什么：渲染到终端的 SolidJS</h2>
<p>现代前端框架（React/SolidJS）的精髓，是<strong>「渲染器」与「框架」分离</strong>：SolidJS 负责「组件、signal、响应式更新」这套逻辑，而<strong>具体把元素画到哪儿</strong>由一个可插拔的「渲染器」决定——画到浏览器 DOM 就是网页，画到 Canvas 就是图形，而 opentui 把它<strong>画到了终端</strong>。这种「同一套框架、不同渲染目标」的对应关系，列出来一目了然：</p>
<div class="cols">
  <div class="col"><h4>浏览器（网页）</h4><p>DOM 元素树 · <span class="mono">&lt;div&gt;</span>/文字节点 · CSS flexbox · <span class="mono">requestAnimationFrame</span> 重绘 · 点击/键入事件 · 像素帧缓冲</p></div>
  <div class="col"><h4>opentui（终端）</h4><p>Renderable 元素树 · <span class="mono">&lt;box&gt;</span>/<span class="mono">&lt;text&gt;</span> · 同款 flex 属性 · 60fps 绘制循环 · 鼠标/键盘事件 · <strong>字符格</strong>帧缓冲</p></div>
</div>
<p>它分两层包：<span class="mono">@opentui/core</span> 是渲染引擎（管布局、绘制、输入），<span class="mono">@opentui/solid</span> 是 SolidJS 绑定（提供 <span class="mono">render</span>、<span class="mono">useRenderer</span>、<span class="mono">useTerminalDimensions</span> 等钩子）。你能用的 JSX 元素，就是终端版的「HTML 标签」：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">&lt;box&gt;</div><div class="c-txt">容器/盒子（≈ <span class="mono">&lt;div&gt;</span>），支持 flexbox 布局，TUI 里用得最多</div></div>
  <div class="cell"><div class="c-tag">&lt;text&gt;</div><div class="c-txt">文字（≈文字节点），可设颜色、粗体等属性</div></div>
  <div class="cell"><div class="c-tag">&lt;scrollbox&gt;</div><div class="c-txt">可滚动容器（≈ <span class="mono">overflow:auto</span> 的 div），对话流就靠它</div></div>
  <div class="cell"><div class="c-tag">&lt;input&gt; / &lt;textarea&gt;</div><div class="c-txt">单行/多行输入框（≈表单控件），prompt 编辑器的底座</div></div>
</div>
<p>布局也是你熟悉的那套：opencode 的 TUI 代码里到处是 <span class="mono">flexDirection</span>（122 处）、<span class="mono">flexGrow</span>、<span class="mono">justifyContent</span>、<span class="mono">alignItems</span>——<strong>就是 CSS flexbox</strong>。opentui 内置了一个 flexbox 布局引擎，按这些属性算出每个元素该占终端的哪几行哪几列、多宽多高。于是「左边固定宽的侧边栏 + 右边自适应的主区」这种布局，你用 <span class="mono">flexDirection:"row"</span> + 侧边栏定宽 + 主区 <span class="mono">flexGrow:1</span> 就搞定了，和写网页<strong>一字不差</strong>。这种「把成熟模型整体复用」的思路，正是全书反复出现的智慧（L51 复用 git、L39 复用 Ripgrep）——只不过这次复用的，是整个<strong>前端渲染范式</strong>。值得想一想这背后省掉了多少事：终端绘图的传统做法，是直接拼接 ANSI 转义码——「把光标移到第 5 行第 12 列、设成红色、打印这串字、再复位」。这种手工绘图既<strong>难写又难维护</strong>：稍微复杂一点的布局（一个会随窗口缩放的多栏界面）就得自己算每个字符的坐标，改一处动全身。而 opentui 把这层彻底<strong>抽象掉了</strong>：你只声明「我要一个横向排列、左栏定宽、右栏自适应的盒子」，至于「第 5 行第 12 列该打什么字、什么颜色」，全交给布局引擎和绘制器去算。<strong>从「手动摆字符」到「声明式描述布局」，正是 TUI 开发体验的一次代际跃迁</strong>——而这一跃，opencode 没有自己造，是借 opentui 白捡的。</p>

<h2>渲染管线：从 JSX 到终端字符</h2>
<p>opencode 启动 TUI 的入口是 <span class="mono">app.tsx</span> 的 <span class="mono">run</span> 函数，它干两件事：先 <span class="mono">createCliRenderer</span> 造一个渲染器，再 <span class="mono">render(() =&gt; &lt;组件树&gt;)</span> 把组件挂上去。要理解这条管线，先看 opentui 内部分了哪几层——从你写的 JSX，到终端上的字符，中间隔着这样一摞：</p>
<div class="layers">
  <div class="layer"><span class="l-tag">SolidJS 响应式</span><span class="l-desc">你写的组件 + signal，决定「界面该长什么样」</span></div>
  <div class="layer"><span class="l-tag">Renderable 元素树</span><span class="l-desc">JSX 协调出一棵 box/text 元素树（终端版 DOM）</span></div>
  <div class="layer"><span class="l-tag">flexbox 布局引擎</span><span class="l-desc">按 flex 属性算出每个元素占终端的哪几行哪几列</span></div>
  <div class="layer"><span class="l-tag">帧缓冲（字符格网格）</span><span class="l-desc">把元素「画」进一块字符+颜色的二维网格</span></div>
  <div class="layer"><span class="l-tag">ANSI 输出 → 终端</span><span class="l-desc">差分出变化的格子，转成转义码刷给 TTY</span></div>
</div>
<p>整条管线串起来是这样的：</p>
<div class="flow">
  <div class="f-node">createCliRenderer<br><small>造渲染器(60fps/键鼠)</small></div>
  <div class="f-arrow">render(JSX) →</div>
  <div class="f-node">SolidJS 协调<br><small>组件树→元素树</small></div>
  <div class="f-arrow">布局 →</div>
  <div class="f-node">flexbox 算尺寸位置<br><small>每个元素占哪几格</small></div>
  <div class="f-arrow">绘制 →</div>
  <div class="f-node">帧缓冲→ANSI<br><small>字符+颜色刷到终端</small></div>
</div>
<p><span class="mono">createCliRenderer</span> 的那组选项，定义了这块「终端画布」的能力：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">targetFps: 60</div><div class="c-txt">绘制循环目标帧率——像浏览器一样每秒最多刷 60 帧</div></div>
  <div class="cell"><div class="c-tag">useKittyKeyboard</div><div class="c-txt">启用现代 Kitty 键盘协议，能识别更丰富的按键组合</div></div>
  <div class="cell"><div class="c-tag">useMouse</div><div class="c-txt">开启鼠标支持（点击、滚轮、选区）</div></div>
  <div class="cell"><div class="c-tag">externalOutputMode: "passthrough"</div><div class="c-txt">让子进程（如工具跑的命令）的输出能穿透显示</div></div>
  <div class="cell"><div class="c-tag">exitOnCtrlC: false</div><div class="c-txt">Ctrl-C 不直接退出，交给 app 自己处理（如二次确认）</div></div>
  <div class="cell"><div class="c-tag">consoleOptions</div><div class="c-txt">内建一个调试控制台浮层（连 Ctrl-Y 复制选区都配好了）</div></div>
</div>
<p>渲染器造好后，<span class="mono">render(() =&gt; &lt;ExitProvider&gt;…&lt;App/&gt;…&lt;/&gt;)</span> 把整棵 SolidJS 组件树挂进去。从这一刻起，组件树的每一次变化，都会被 opentui 转译成终端上字符的变化。你写下的每一个 <span class="mono">&lt;box&gt;</span>、每一处 flex 属性、每一个 signal，最终都会落到屏幕上某几行某几列的字符与颜色——而这套从「声明」到「字符」的转译，对你是完全透明的。opencode 还把整个渲染器的生命周期<strong>包进 Effect 的 <span class="mono">acquireRelease</span></strong>：渲染器是「acquire」出来的资源，App 退出时（或收到 SIGHUP）自动 <span class="mono">destroyRenderer</span> 把终端恢复原状——这又是第 2 部分 Effect 资源管理在 TUI 层的落地，确保无论怎么退出，都不会把用户的终端搞得一团糟。</p>

<h2>为什么这套设计很妙：细粒度响应式的红利</h2>
<p>把渲染范式搬进终端，最大的红利来自 SolidJS 的<strong>细粒度响应式</strong>。终端绘制是<strong>昂贵</strong>的——每帧都要把成千上万个字符格连同颜色算出来、再通过一串 ANSI 转义码刷给终端。如果每次状态变化都<strong>整屏重画</strong>，60fps 根本扛不住，画面还会闪。而且终端的「带宽」是有限的：要刷的字符越多，通过管道写出去的转义码就越长、越慢，在 SSH 等远程场景下尤其明显。所以「每次只刷最少的格子」不是锦上添花，而是流畅 TUI 的<strong>生死线</strong>。而 SolidJS 的 signal 机制让更新变得<strong>外科手术般精确</strong>：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">某个 signal 变了（如新到一条消息）</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">只有<strong>依赖这个 signal 的那几个元素</strong>被标记为「脏」</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">opentui 只对脏元素重新布局、重新绘制</span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">下一帧只把<strong>变化的字符格</strong>刷给终端（差分更新）</span></div>
</div>
<p>这就是「写网页的心智模型」带来的隐形红利：你只管用 signal 描述「数据是什么」，<strong>从不手动操心「要重画屏幕的哪一块」</strong>——SolidJS 的依赖追踪 + opentui 的差分绘制，自动把每次更新压到最小。这和你在浏览器里用 Solid/React 的体验<strong>一模一样</strong>，只不过「最小更新」的单位从「DOM 节点」变成了「终端字符格」。<strong>把一个为高频 UI 更新而生的成熟响应式系统，整个搬到终端</strong>——这是 opencode 能在终端里做出如此流畅、复杂界面的根本原因，也是它没有重新发明一套笨拙的「手动重绘」TUI 逻辑的关键。再往深一层看，这个选择还悄悄统一了 opencode 三个客户端的心智：浏览器里的 Web 应用（M3 提到的 app 包）、桌面端、以及这个终端 TUI，<strong>都可以用同一套 SolidJS 组件思维去写</strong>，区别只在最终「画到哪块画布」。一次掌握 signal/JSX/flex，三处通用——这种「一套范式打通多端」的整齐，正是「选对地基」带来的长远复利。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观视角</div>
  <p>这一课讲清了 opencode TUI 的渲染地基——opentui 这个「终端里的浏览器」，以及它如何把一棵 SolidJS 组件树变成终端上的一格格字符：</p>
  <ul>
    <li><strong>opentui = 渲染到终端的 SolidJS</strong>：<span class="mono">@opentui/core</span>(引擎：布局/绘制/输入) + <span class="mono">@opentui/solid</span>(SolidJS 绑定：render/useRenderer/useTerminalDimensions)。JSX 原语=终端版 HTML 标签：<span class="mono">&lt;box&gt;</span>(≈div,flexbox 容器)、<span class="mono">&lt;text&gt;</span>、<span class="mono">&lt;scrollbox&gt;</span>、<span class="mono">&lt;input&gt;/&lt;textarea&gt;</span>。</li>
    <li><strong>flexbox 布局</strong>：<span class="mono">flexDirection/flexGrow/justifyContent/alignItems</span> 就是 CSS flexbox，opentui 内置布局引擎按此算每个元素占终端的哪几行列。「写网页」的肌肉记忆直接复用。</li>
    <li><strong>渲染管线</strong>（<span class="mono">app.tsx</span> run）：<span class="mono">createCliRenderer</span>(targetFps 60/kitty 键盘/mouse/passthrough/exitOnCtrlC false/console 浮层) → <span class="mono">render(()=&gt;&lt;组件树&gt;)</span> → SolidJS 协调 → flexbox 布局 → 帧缓冲→ANSI 刷终端。渲染器生命周期包进 Effect <span class="mono">acquireRelease</span>，退出自动恢复终端。</li>
    <li><strong>细粒度响应式红利</strong>：signal 变→只有依赖它的元素变脏→只重画脏元素→只刷变化的字符格（差分）。把为高频 UI 更新而生的响应式系统搬进终端，无需手动「重画哪一块」，是流畅复杂 TUI 的根本。</li>
  </ul>
  <p>地基铺好了——你现在知道 opencode 用「终端里的浏览器」opentui，以 SolidJS 组件 + flexbox 来搭 TUI。下一课（L53）走进 <span class="mono">app.tsx</span> 的<strong>组件结构</strong>：那一长串嵌套的 <strong>context provider</strong>（SDK/Project/Sync/Data/Theme/Dialog…）如何像金字塔一样，把全 App 共享的状态与服务层层注入给每个组件。再往后 L54 讲事件如何流进 store、L55 讲 prompt 编辑器组件、L56 讲对话框与命令面板。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p><span class="mono">app.tsx</span> 的 <span class="mono">run</span> 把「造渲染器」和「挂组件树」用 Effect 串起来（简化自源码）：</p>
  <pre class="code"><span class="kw">const</span> renderer = <span class="kw">yield*</span> Effect.<span class="fn">acquireRelease</span>(
  Effect.<span class="fn">tryPromise</span>(() =&gt;
    <span class="fn">createCliRenderer</span>({
      externalOutputMode: <span class="st">"passthrough"</span>,
      targetFps: <span class="nu">60</span>,
      exitOnCtrlC: <span class="kw">false</span>,
      useKittyKeyboard: {},
      useMouse: !Flag.OPENCODE_DISABLE_MOUSE &amp;&amp; input.config.mouse,
    }),
  ),
  (renderer) =&gt; Effect.<span class="fn">sync</span>(() =&gt; <span class="fn">destroyRenderer</span>(renderer)),  <span class="cm">// ← 退出必清理</span>
)
<span class="cm">// 把整棵 SolidJS 组件树挂进渲染器</span>
<span class="kw">await</span> <span class="fn">render</span>(() =&gt; (
  &lt;ExitProvider exit={...}&gt;
    {<span class="cm">/* …一长串 context provider… */</span>}
    &lt;App /&gt;
  &lt;/ExitProvider&gt;
))</pre>
  <p>最值得品的，是 <span class="mono">createCliRenderer</span> 被裹在 <span class="mono">Effect.acquireRelease</span> 里：渲染器是一个会<strong>独占并改写你终端状态</strong>的资源（切到备用屏、关回显、进 raw 模式…），一旦 App 崩了或被强杀，若不复原，你的终端会<strong>彻底错乱</strong>（光标乱跑、看不见输入）。<span class="mono">acquireRelease</span> 保证了无论以何种方式退出——正常关、抛异常、收到 SIGHUP——那个 <span class="mono">destroyRenderer</span> 清理函数<strong>必定被执行</strong>，把终端恢复如初。这正是第 2 部分 Effect「资源的获取与释放绑定在一起、释放必然发生」那套纪律，在「最容易把终端搞坏」的 TUI 入口上的关键应用。<strong>一个体贴的 TUI，不仅要画得好看，更要在退出时把舞台收拾干净</strong>——而 Effect 的结构化资源管理，让「收拾干净」从一件靠自觉的事，变成了一件结构上无法遗漏的事。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>opentui = 终端里的浏览器</strong>：把整套 Web 渲染范式（DOM 般元素树 + flexbox 布局 + 60fps 绘制循环 + 键鼠事件）搬进 TTY。你用和写网页一样的心智模型（SolidJS 组件/signal/JSX/flex）搭终端 App。</li>
    <li><strong>渲染到终端的 SolidJS</strong>：<span class="mono">@opentui/core</span>(引擎)+<span class="mono">@opentui/solid</span>(绑定)。JSX 原语 <span class="mono">&lt;box&gt;</span>(≈div)/<span class="mono">&lt;text&gt;</span>/<span class="mono">&lt;scrollbox&gt;</span>/<span class="mono">&lt;input&gt;/&lt;textarea&gt;</span>；布局用 <span class="mono">flexDirection/flexGrow/justifyContent</span> 等 CSS flexbox。</li>
    <li><strong>渲染管线</strong>：<span class="mono">createCliRenderer</span>(targetFps 60/kitty/mouse/passthrough) → <span class="mono">render(()=&gt;&lt;树&gt;)</span> → SolidJS 协调 → flexbox 布局 → 帧缓冲→ANSI。渲染器包进 Effect <span class="mono">acquireRelease</span>，退出（含 SIGHUP/崩溃）必 <span class="mono">destroyRenderer</span> 恢复终端。</li>
    <li><strong>细粒度响应式红利</strong>：signal 变→只标脏依赖它的元素→只重画脏元素→只刷变化字符格（差分）。无需手动管「重画哪块」，把为高频更新而生的响应式系统搬进终端=流畅复杂 TUI 的根本。复用整个前端范式（同 L51 复用 git、L39 复用 Ripgrep）。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">M9 faithfully stored and managed the agent's "memory." But memory lying in SQLite is seen by no one—it ultimately must be <strong>rendered into an interface you can see, type into, interact with</strong>. M10, starting here, covers opencode's <strong>TUI (Terminal User Interface)</strong>: that pretty terminal interface that pops up when you type <span class="mono">opencode</span>—with a sidebar, a conversation stream, where you can type and scroll. But here's a fundamental challenge: a terminal is essentially just <strong>a grid that can display characters</strong>, with no DOM, no CSS, no browser—how do you, on such a primitive canvas, build a <strong>reactive, interactive</strong> modern UI? opencode's answer is <strong>opentui</strong>: a renderer that renders <strong>SolidJS to the terminal</strong>. You still write JSX (<span class="mono">&lt;box&gt;</span>, <span class="mono">&lt;text&gt;</span>), still use signals for reactivity, and opentui handles <strong>painting this component tree into character cells in the terminal</strong>. This lesson is M10's foundation: what opentui actually is, and how it turns a component tree into terminal "pixels."</p>
<p>The insight to take from this lesson is one sentence: <strong>opentui is "a browser for the terminal."</strong> It transplants the whole web rendering paradigm <strong>verbatim into the TTY</strong>—a DOM-like element tree, a flexbox layout engine, a 60fps paint loop, keyboard/mouse events, even a console overlay that pops up on error. This means: you build a terminal app with <strong>the exact same mental model as building a web page</strong> (SolidJS components, signals, JSX, flex layout), and opentui handles all the dirty work of "how this component tree becomes characters on the screen." This is extremely high-leverage reuse: opencode <strong>needn't invent a brand-new UI framework for the terminal</strong> but directly borrows SolidJS's battle-tested fine-grained reactivity + the flexbox model every programmer knows. Grasp this layer and you'll understand "why opencode's TUI code reads like writing a React/Solid web page, only running in the terminal."</p>

<div class="card analogy">
  <div class="tag">🖥️ Analogy</div>
  <strong>opentui is to the terminal what a browser is to a web page.</strong> A browser takes HTML/CSS/JS and paints pixels before your eyes; opentui takes JSX/flex-props/signals and paints <strong>character cells</strong> in the terminal. The correspondence is seamless: a web page's <span class="mono">&lt;div&gt;</span> is the terminal's <span class="mono">&lt;box&gt;</span> (a box that holds things); a web page's text node is <span class="mono">&lt;text&gt;</span>; CSS's flexbox is the box's <span class="mono">flexDirection</span>/<span class="mono">flexGrow</span> props; the browser's per-second-redrawing <span class="mono">requestAnimationFrame</span> is opentui's 60fps paint loop; a web page's click/keypress events are the terminal's mouse/keyboard events. <strong>That "writing web pages" muscle memory in your head can be carried over almost untouched to "writing terminal apps"</strong>—exactly opentui's greatest kindness: it doesn't force you to learn a brand-new terminal-drawing API but moves the browser model you already know cold, wholesale, onto that little black screen that can only show characters.
</div>

<h2>What opentui is: SolidJS rendered to the terminal</h2>
<p>The essence of modern frontend frameworks (React/SolidJS) is <strong>separating "renderer" from "framework"</strong>: SolidJS handles the "components, signals, reactive update" logic, while <strong>where exactly elements get painted</strong> is decided by a pluggable "renderer"—paint to the browser DOM and it's a web page, to a Canvas and it's graphics, and opentui paints it <strong>to the terminal</strong>. This "same framework, different render target" correspondence, laid out, is clear at a glance:</p>
<div class="cols">
  <div class="col"><h4>browser (web page)</h4><p>DOM element tree · <span class="mono">&lt;div&gt;</span>/text node · CSS flexbox · <span class="mono">requestAnimationFrame</span> redraw · click/keypress events · pixel framebuffer</p></div>
  <div class="col"><h4>opentui (terminal)</h4><p>Renderable element tree · <span class="mono">&lt;box&gt;</span>/<span class="mono">&lt;text&gt;</span> · the same flex props · 60fps paint loop · mouse/keyboard events · <strong>character-cell</strong> framebuffer</p></div>
</div>
<p>It's two packages: <span class="mono">@opentui/core</span> is the render engine (layout, paint, input), <span class="mono">@opentui/solid</span> is the SolidJS bindings (providing <span class="mono">render</span>, <span class="mono">useRenderer</span>, <span class="mono">useTerminalDimensions</span> hooks). The JSX elements you can use are the terminal version of "HTML tags":</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">&lt;box&gt;</div><div class="c-txt">container/box (≈ <span class="mono">&lt;div&gt;</span>), supports flexbox layout, used most in the TUI</div></div>
  <div class="cell"><div class="c-tag">&lt;text&gt;</div><div class="c-txt">text (≈ text node), can set color, bold, etc.</div></div>
  <div class="cell"><div class="c-tag">&lt;scrollbox&gt;</div><div class="c-txt">scrollable container (≈ <span class="mono">overflow:auto</span> div), the conversation stream relies on it</div></div>
  <div class="cell"><div class="c-tag">&lt;input&gt; / &lt;textarea&gt;</div><div class="c-txt">single/multi-line input (≈ form controls), the prompt editor's base</div></div>
</div>
<p>Layout is the set you know too: opencode's TUI code is full of <span class="mono">flexDirection</span> (122 spots), <span class="mono">flexGrow</span>, <span class="mono">justifyContent</span>, <span class="mono">alignItems</span>—<strong>it's CSS flexbox</strong>. opentui has a built-in flexbox layout engine that, per these props, computes which rows and columns of the terminal each element occupies, how wide and tall. So a layout like "a fixed-width sidebar on the left + an adaptive main area on the right," you do with <span class="mono">flexDirection:"row"</span> + a fixed-width sidebar + main area <span class="mono">flexGrow:1</span>, <strong>identical to writing a web page</strong>. This "reuse a mature model wholesale" approach is exactly the wisdom recurring across the book (L51 reusing git, L39 reusing Ripgrep)—only this time what's reused is the entire <strong>frontend rendering paradigm</strong>. Worth pondering how much this saves: the traditional way to draw in a terminal is splicing ANSI escape codes directly—"move the cursor to row 5 col 12, set it red, print this string, then reset." This manual drawing is <strong>both hard to write and hard to maintain</strong>: a slightly complex layout (a multi-column interface that resizes with the window) means computing each character's coordinates yourself, change one spot and everything shifts. opentui <strong>fully abstracts</strong> this layer away: you just declare "I want a horizontally-arranged box, left column fixed-width, right column adaptive," and "what character at row 5 col 12, what color" is all left to the layout engine and painter. <strong>From "manually placing characters" to "declaratively describing layout" is a generational leap in the TUI development experience</strong>—and this leap, opencode didn't build itself, it picked up free from opentui.</p>

<h2>The render pipeline: from JSX to terminal characters</h2>
<p>opencode's TUI entry is the <span class="mono">run</span> function in <span class="mono">app.tsx</span>, which does two things: first <span class="mono">createCliRenderer</span> to build a renderer, then <span class="mono">render(() =&gt; &lt;component tree&gt;)</span> to mount the components. To understand this pipeline, first see what layers opentui splits internally—from the JSX you write to characters on the terminal, in between sits this stack:</p>
<div class="layers">
  <div class="layer"><span class="l-tag">SolidJS reactivity</span><span class="l-desc">your components + signals, deciding "what the interface should look like"</span></div>
  <div class="layer"><span class="l-tag">Renderable element tree</span><span class="l-desc">JSX reconciles into a box/text element tree (the terminal's DOM)</span></div>
  <div class="layer"><span class="l-tag">flexbox layout engine</span><span class="l-desc">per flex props computes which rows/cols each element occupies</span></div>
  <div class="layer"><span class="l-tag">framebuffer (character-cell grid)</span><span class="l-desc">"paints" elements into a 2D grid of chars + colors</span></div>
  <div class="layer"><span class="l-tag">ANSI output → terminal</span><span class="l-desc">diffs the changed cells, turns them into escape codes flushed to the TTY</span></div>
</div>
<p>The whole pipeline strung together:</p>
<div class="flow">
  <div class="f-node">createCliRenderer<br><small>build renderer (60fps/kb+mouse)</small></div>
  <div class="f-arrow">render(JSX) →</div>
  <div class="f-node">SolidJS reconcile<br><small>component tree→element tree</small></div>
  <div class="f-arrow">layout →</div>
  <div class="f-node">flexbox computes size/pos<br><small>which cells each element takes</small></div>
  <div class="f-arrow">paint →</div>
  <div class="f-node">framebuffer→ANSI<br><small>chars+colors flushed to terminal</small></div>
</div>
<p><span class="mono">createCliRenderer</span>'s option group defines this "terminal canvas"'s capabilities:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">targetFps: 60</div><div class="c-txt">paint-loop target frame rate—like a browser, up to 60 frames per second</div></div>
  <div class="cell"><div class="c-tag">useKittyKeyboard</div><div class="c-txt">enables the modern Kitty keyboard protocol, recognizing richer key combos</div></div>
  <div class="cell"><div class="c-tag">useMouse</div><div class="c-txt">turns on mouse support (click, scroll wheel, selection)</div></div>
  <div class="cell"><div class="c-tag">externalOutputMode: "passthrough"</div><div class="c-txt">lets child processes' (e.g. tool-run commands) output pass through to display</div></div>
  <div class="cell"><div class="c-tag">exitOnCtrlC: false</div><div class="c-txt">Ctrl-C doesn't exit directly, handed to the app itself (e.g. a second confirm)</div></div>
  <div class="cell"><div class="c-tag">consoleOptions</div><div class="c-txt">a built-in debug console overlay (even Ctrl-Y copy-selection is configured)</div></div>
</div>
<p>Once the renderer is built, <span class="mono">render(() =&gt; &lt;ExitProvider&gt;…&lt;App/&gt;…&lt;/&gt;)</span> mounts the whole SolidJS component tree. From this moment, every change in the component tree is translated by opentui into changes of characters on the terminal. Every <span class="mono">&lt;box&gt;</span> you write, every flex prop, every signal, ultimately lands as characters and colors at some rows and columns on the screen—and this translation from "declaration" to "characters" is entirely transparent to you. opencode also wraps the whole renderer lifecycle <strong>in Effect's <span class="mono">acquireRelease</span></strong>: the renderer is an "acquired" resource, and on App exit (or on SIGHUP) it auto-<span class="mono">destroyRenderer</span>s to restore the terminal—again Part 2's Effect resource management landing at the TUI layer, ensuring that however you exit, the user's terminal isn't left a mess.</p>

<h2>Why this design is clever: the dividend of fine-grained reactivity</h2>
<p>Transplanting the render paradigm into the terminal, the biggest dividend comes from SolidJS's <strong>fine-grained reactivity</strong>. Terminal painting is <strong>expensive</strong>—each frame must compute thousands of character cells along with colors, then flush them to the terminal via a string of ANSI escape codes. If every state change <strong>redrew the whole screen</strong>, 60fps couldn't hold and the screen would flicker. And the terminal's "bandwidth" is limited: the more characters to flush, the longer and slower the escape codes written through the pipe, especially noticeable over SSH and other remote scenarios. So "flush the fewest cells each time" isn't a nice-to-have but a fluid TUI's <strong>lifeline</strong>. SolidJS's signal mechanism makes updates <strong>surgically precise</strong>:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">some signal changes (e.g. a new message arrives)</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">only <strong>the few elements depending on this signal</strong> are marked "dirty"</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">opentui re-lays-out, re-paints only the dirty elements</span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">the next frame flushes only the <strong>changed character cells</strong> to the terminal (diff update)</span></div>
</div>
<p>This is the invisible dividend of the "writing-web-pages mental model": you just describe "what the data is" with signals, <strong>never manually worrying "which part of the screen to redraw"</strong>—SolidJS's dependency tracking + opentui's diff painting automatically squeeze each update to the minimum. This is <strong>identical</strong> to your experience with Solid/React in the browser, only the unit of "minimal update" changes from "a DOM node" to "a terminal character cell." <strong>Transplanting a mature reactive system born for high-frequency UI updates wholesale into the terminal</strong>—this is the root reason opencode can make such a fluid, complex interface in the terminal, and the key to it not reinventing a clumsy "manual redraw" TUI logic. Looking deeper, this choice also quietly unifies the mental model across opencode's three clients: the web app in the browser (the app package mentioned in M3), the desktop, and this terminal TUI <strong>can all be written with the same SolidJS component thinking</strong>, differing only in "which canvas to finally paint to." Master signal/JSX/flex once, use it in three places—this "one paradigm spanning multiple targets" neatness is exactly the long-term compounding return of "picking the right foundation."</p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>This lesson clarifies opencode TUI's render foundation—opentui, this "browser for the terminal," and how it turns a SolidJS component tree into character cells on the terminal:</p>
  <ul>
    <li><strong>opentui = SolidJS rendered to the terminal</strong>: <span class="mono">@opentui/core</span> (engine: layout/paint/input) + <span class="mono">@opentui/solid</span> (SolidJS bindings: render/useRenderer/useTerminalDimensions). JSX primitives = terminal HTML tags: <span class="mono">&lt;box&gt;</span> (≈div, flexbox container), <span class="mono">&lt;text&gt;</span>, <span class="mono">&lt;scrollbox&gt;</span>, <span class="mono">&lt;input&gt;/&lt;textarea&gt;</span>.</li>
    <li><strong>flexbox layout</strong>: <span class="mono">flexDirection/flexGrow/justifyContent/alignItems</span> is CSS flexbox, opentui's built-in layout engine computes which rows/cols each element takes. The "writing web pages" muscle memory directly reused.</li>
    <li><strong>render pipeline</strong> (<span class="mono">app.tsx</span> run): <span class="mono">createCliRenderer</span> (targetFps 60/kitty keyboard/mouse/passthrough/exitOnCtrlC false/console overlay) → <span class="mono">render(()=&gt;&lt;tree&gt;)</span> → SolidJS reconcile → flexbox layout → framebuffer→ANSI to terminal. Renderer lifecycle wrapped in Effect <span class="mono">acquireRelease</span>, exit auto-restores the terminal.</li>
    <li><strong>fine-grained reactivity dividend</strong>: signal changes → only dependent elements marked dirty → only dirty elements repainted → only changed character cells flushed (diff). Transplanting a reactive system born for high-frequency UI updates into the terminal, no manual "which part to redraw," is the root of a fluid complex TUI.</li>
  </ul>
  <p>The foundation is laid—you now know opencode uses "the browser for the terminal" opentui, building the TUI with SolidJS components + flexbox. The next lesson (L53) walks into <span class="mono">app.tsx</span>'s <strong>component structure</strong>: how that long string of nested <strong>context providers</strong> (SDK/Project/Sync/Data/Theme/Dialog…) injects app-wide shared state and services layer by layer to every component, like a pyramid. Further on, L54 covers how events flow into the store, L55 the prompt editor component, L56 dialogs and the command palette.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p><span class="mono">app.tsx</span>'s <span class="mono">run</span> strings "build renderer" and "mount component tree" together with Effect (simplified from source):</p>
  <pre class="code"><span class="kw">const</span> renderer = <span class="kw">yield*</span> Effect.<span class="fn">acquireRelease</span>(
  Effect.<span class="fn">tryPromise</span>(() =&gt;
    <span class="fn">createCliRenderer</span>({
      externalOutputMode: <span class="st">"passthrough"</span>,
      targetFps: <span class="nu">60</span>,
      exitOnCtrlC: <span class="kw">false</span>,
      useKittyKeyboard: {},
      useMouse: !Flag.OPENCODE_DISABLE_MOUSE &amp;&amp; input.config.mouse,
    }),
  ),
  (renderer) =&gt; Effect.<span class="fn">sync</span>(() =&gt; <span class="fn">destroyRenderer</span>(renderer)),  <span class="cm">// ← must clean up on exit</span>
)
<span class="cm">// mount the whole SolidJS component tree into the renderer</span>
<span class="kw">await</span> <span class="fn">render</span>(() =&gt; (
  &lt;ExitProvider exit={...}&gt;
    {<span class="cm">/* …a long string of context providers… */</span>}
    &lt;App /&gt;
  &lt;/ExitProvider&gt;
))</pre>
  <p>What's most worth savoring is that <span class="mono">createCliRenderer</span> is wrapped in <span class="mono">Effect.acquireRelease</span>: the renderer is a resource that <strong>exclusively takes over and rewrites your terminal's state</strong> (switches to the alternate screen, turns off echo, enters raw mode…), and once the App crashes or is force-killed, if not restored, your terminal will be <strong>thoroughly scrambled</strong> (cursor flying around, input invisible). <span class="mono">acquireRelease</span> guarantees that however you exit—normal close, thrown exception, received SIGHUP—that <span class="mono">destroyRenderer</span> cleanup function <strong>is necessarily executed</strong>, restoring the terminal to as-new. This is exactly Part 2's Effect "resource acquisition and release bound together, release necessarily happens" discipline, key-applied at the "most likely to break the terminal" TUI entry. <strong>A thoughtful TUI must not only paint nicely but, on exit, tidy up the stage</strong>—and Effect's structured resource management turns "tidying up" from a matter of self-discipline into a matter structurally impossible to forget.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>opentui = a browser for the terminal</strong>: transplants the whole web rendering paradigm (DOM-like element tree + flexbox layout + 60fps paint loop + kb/mouse events) into the TTY. You build a terminal app with the same mental model as a web page (SolidJS components/signals/JSX/flex).</li>
    <li><strong>SolidJS rendered to the terminal</strong>: <span class="mono">@opentui/core</span> (engine) + <span class="mono">@opentui/solid</span> (bindings). JSX primitives <span class="mono">&lt;box&gt;</span> (≈div)/<span class="mono">&lt;text&gt;</span>/<span class="mono">&lt;scrollbox&gt;</span>/<span class="mono">&lt;input&gt;/&lt;textarea&gt;</span>; layout via <span class="mono">flexDirection/flexGrow/justifyContent</span> CSS flexbox.</li>
    <li><strong>render pipeline</strong>: <span class="mono">createCliRenderer</span> (targetFps 60/kitty/mouse/passthrough) → <span class="mono">render(()=&gt;&lt;tree&gt;)</span> → SolidJS reconcile → flexbox layout → framebuffer→ANSI. Renderer wrapped in Effect <span class="mono">acquireRelease</span>, exit (incl. SIGHUP/crash) necessarily <span class="mono">destroyRenderer</span>s to restore the terminal.</li>
    <li><strong>fine-grained reactivity dividend</strong>: signal changes → only dependent elements marked dirty → only dirty elements repainted → only changed character cells flushed (diff). No manual "which part to redraw," transplanting a reactive system born for high-frequency updates into the terminal = the root of a fluid complex TUI. Reuses the entire frontend paradigm (like L51 reusing git, L39 reusing Ripgrep).</li>
  </ul>
</div>
""",
}
LESSON_53 = {
    "zh": r"""
<p class="lead">上一课我们知道了 opentui 会把一棵 SolidJS 组件树画成终端界面。但<strong>那棵树本身长什么样</strong>？翻开 <span class="mono">app.tsx</span>，你会看到一个让人眼前一晕的景象：<span class="mono">render()</span> 里嵌套着<strong>近二十层</strong>的「Provider」——<span class="mono">ExitProvider</span> 套 <span class="mono">SDKProvider</span> 套 <span class="mono">ProjectProvider</span> 套 <span class="mono">SyncProvider</span> 套 <span class="mono">DataProvider</span> 套 <span class="mono">ThemeProvider</span>……一层裹一层，最里面才是真正的 <span class="mono">&lt;App/&gt;</span>。这一课就讲清这座<strong>「Provider 金字塔」</strong>：它不是杂乱的嵌套，而是 opencode TUI <strong>组织全 App 共享状态与服务</strong>的骨架。读懂它，你就拿到了在 TUI 代码里「任何一个组件想要什么、去哪儿拿」的地图。这套「Provider + use 钩子」的模式，正是 React/SolidJS 世界里组织全局状态的<strong>主流答案</strong>——所以这一课讲的虽是 opencode 的 TUI，学到的却是一套你在任何现代前端项目里都能直接复用的结构功夫。</p>
<p>这一课有两个层层递进的洞见。第一，<strong>这座金字塔是一套结构化的「依赖注入」</strong>：每一层 Provider 只负责<strong>一件事</strong>（SDK 管和服务器的连接、Project 管项目状态、Theme 管主题、Route 管路由……），而<strong>嵌套的顺序，编码的正是它们之间的依赖关系</strong>——<span class="mono">ProjectProvider</span> 的初始化里要 <span class="mono">useSDK()</span>，所以 <span class="mono">SDKProvider</span> 必须裹在它外面。外层是地基、内层是上层建筑，一个组件能用到的「服务」，就是它头顶所有 Provider 的并集。第二，<strong>这近二十个 Provider 全用同一个模子刻出来</strong>：一个叫 <span class="mono">createSimpleContext</span> 的小助手，把「建 context + 写 provider + 给 use 钩子」这套样板一次封好，于是每个 context 都长一个样、都有一个<strong>用错地方就当场报错</strong>的 <span class="mono">use()</span>。读懂这两点，你看到的就不再是一团吓人的嵌套，而是一座<strong>层次分明、各司其职、依赖清晰</strong>的状态金字塔。</p>

<div class="card analogy">
  <div class="tag">🏢 生活类比</div>
  把这座 Provider 金字塔想象成一栋大楼的<strong>「公共设施分层」</strong>。最底层是<strong>供电</strong>（<span class="mono">SDKProvider</span>，和服务器的连接——没有它楼里什么都转不起来）；往上是<strong>供水</strong>（<span class="mono">ProjectProvider</span>，但水泵得先有电，所以它装在供电之上）；再往上是<strong>暖通、网络、安防</strong>（Sync/Data/Theme/Dialog……），每一层设施都<strong>依赖它下面的层</strong>。而楼里任何一个房间（一个组件），想用电就 <span class="mono">useSDK()</span>、想用主题就 <span class="mono">useTheme()</span>——<strong>直接「插上插座」取用即可，不必关心这服务是从哪一层、怎么接进来的</strong>。最妙的是那个「用错地方就报错」的设计：如果你在一个<strong>没接通供电的房间</strong>里去 <span class="mono">useSDK()</span>，系统不会默默给你一个空值让你之后莫名其妙地崩，而是<strong>立刻明确报错</strong>「你得在 SDKProvider 里头用」——就像在没通电的毛坯房按开关，灯不亮会立刻告诉你「这儿还没通电」，而非让你对着黑灯瞎猜。
</div>

<h2>Provider 金字塔：嵌套即依赖</h2>
<p><span class="mono">app.tsx</span> 的 <span class="mono">render()</span> 里，那一长串 Provider 大致按这个顺序从外到内嵌套（外层先就位、内层才能用上）：</p>
<div class="layers">
  <div class="layer"><span class="l-tag">ExitProvider / ErrorBoundary</span><span class="l-desc">最外层：退出钩子、错误边界（兜底崩溃）</span></div>
  <div class="layer"><span class="l-tag">SDKProvider</span><span class="l-desc">和服务器的连接（SDK 客户端 + SSE 事件流）——一切数据的源头</span></div>
  <div class="layer"><span class="l-tag">ProjectProvider</span><span class="l-desc">项目/工作区状态（init 里 useSDK，故在 SDK 之内）</span></div>
  <div class="layer"><span class="l-tag">SyncProvider → DataProvider</span><span class="l-desc">事件→store 的归约（下一课主题，依赖 SDK 的事件）</span></div>
  <div class="layer"><span class="l-tag">ThemeProvider</span><span class="l-desc">主题/调色板</span></div>
  <div class="layer"><span class="l-tag">Dialog / Frecency / PromptHistory…</span><span class="l-desc">对话框、常用度、prompt 历史等交互状态</span></div>
  <div class="layer"><span class="l-tag">&lt;App/&gt;</span><span class="l-desc">最里层：真正的界面，头顶所有 Provider 的服务任它取用</span></div>
</div>
<p>这个嵌套顺序<strong>绝非随意</strong>——它是一张<strong>依赖关系图</strong>的拓扑排序。看 <span class="mono">project.tsx</span> 就明白了：<span class="mono">ProjectProvider</span> 的 <span class="mono">init</span> 函数第一行就是 <span class="mono">const sdk = useSDK()</span>——它要用 SDK 去拉项目信息。既然 <span class="mono">useSDK()</span> 只能在 <span class="mono">SDKProvider</span> 内部用，那 <span class="mono">ProjectProvider</span> 就<strong>必须</strong>被 <span class="mono">SDKProvider</span> 包在里头。同理，<span class="mono">RouteProvider</span> 的 <span class="mono">init</span> 用了 <span class="mono">useTuiStartup()</span>、<span class="mono">DataProvider</span> 依赖 <span class="mono">SyncProvider</span> 的事件……<strong>每一处「内层 init 调用外层的 use」，都在这座金字塔里钉下一条「谁必须在谁外面」的硬约束</strong>。于是这座塔从下到上，恰好是一条「越基础越靠外、越上层越靠内」的依赖链：连接（SDK）→ 项目 → 数据同步 → 主题 → 交互状态 → 界面。这种「用嵌套顺序表达依赖」的手法，其实比一份显式的依赖声明更巧妙：你<strong>无需另写一张「谁依赖谁」的表</strong>，依赖关系就<strong>物理地</strong>体现在代码的缩进层级里——外层一定先于内层就位，内层天然能用上外层的一切。读 <span class="mono">app.tsx</span> 那段嵌套，从上往下读一遍，就等于把整个 App 的「服务依赖图」从地基到屋顶走了一遍。一个新人想搞懂「TUI 启动时各种服务按什么顺序就位」，不必翻文档，看这一段 JSX 的嵌套顺序即可——<strong>结构本身就是文档</strong>。</p>

<h2>同一个模子：createSimpleContext</h2>
<p>近二十个 Provider，没有一个是从零手写的——它们全用一个叫 <span class="mono">createSimpleContext</span> 的小助手（<span class="mono">context/helper.tsx</span>）刻出来。与其让每个 context 各写一遍「建 context、写 Provider、写 use 钩子」的样板（还很容易在某一处忘了判空、忘了门控），不如把这套样板封进一个工具、让所有 context 都从同一个模子里出来。这个助手把「SolidJS 的 context 三件套」封成一行：</p>
<div class="flow">
  <div class="f-node">createSimpleContext<br><small>{ name, init }</small></div>
  <div class="f-arrow">产出 →</div>
  <div class="f-node">provider 组件<br><small>跑 init(props)、按 ready 门控</small></div>
  <div class="f-arrow">+</div>
  <div class="f-node">use() 钩子<br><small>取值，缺则当场报错</small></div>
</div>
<p>用起来就是一行解构：<span class="mono">const { use: useSDK, provider: SDKProvider } = createSimpleContext({ name: "SDK", init: (props) =&gt; {…} })</span>。这个小封装藏着两个体贴的设计。其一，<strong>「未就绪就先不渲染」的门控</strong>：provider 里有个 <span class="mono">&lt;Show when={init.ready !== false}&gt;</span>，如果某个 context 需要异步准备（如先连上服务器），可以让它<strong>在没就绪时不渲染子树</strong>，避免下面的组件拿到半成品状态。其二，也是最点睛的——<strong>那个会抛错的 <span class="mono">use()</span></strong>：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">name</div><div class="c-txt">这个 context 的名字（仅用于报错信息）</div></div>
  <div class="cell"><div class="c-tag">init(props)</div><div class="c-txt">初始化这一格状态/服务（可在内部 use 外层 context）</div></div>
  <div class="cell"><div class="c-tag">ready 门控</div><div class="c-txt"><span class="mono">&lt;Show when={ready}&gt;</span>——没就绪不渲染子树</div></div>
  <div class="cell"><div class="c-tag">use() 报错</div><div class="c-txt">不在对应 Provider 内调用 → 立刻抛「must be used within a context provider」</div></div>
</div>
<p>那句 <span class="mono">use()</span> 里的 <span class="mono">if (!value) throw new Error(...)</span> 看似不起眼，却是一道<strong>极有价值的护栏</strong>。一个组件调 <span class="mono">useSDK()</span> 时，背后发生的是这样一条「向上找」的链路：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">组件调 <span class="mono">useSDK()</span> → 内部 <span class="mono">useContext(SDK ctx)</span></span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">SolidJS 顺组件树<strong>向上</strong>找最近的 <span class="mono">SDKProvider</span></span></div>
  <div class="t-row"><span class="t-num">3a</span><span class="t-txt">找到 → 返回该 Provider 的 <span class="mono">init</span> 值（SDK 客户端）</span></div>
  <div class="t-row"><span class="t-num">3b</span><span class="t-txt">没找到（不在 Provider 内）→ value 为空 → <strong>当场抛错</strong>，点名「SDK」</span></div>
</div>
<p>在 SolidJS/React 里，最常见也最难查的 bug 之一，就是「在 Provider 外面用了 context，拿到 undefined，然后在某个八竿子打不着的地方崩掉」。而这里<strong>把这个错误从『沉默的 undefined』提前成『响亮的当场报错』</strong>——一旦你把组件放错了位置（忘了用某个 Provider 包住），运行的第一时间就会告诉你「<span class="mono">SDK context 必须在 Provider 内使用</span>」，连具体哪个 context 都点名了。<strong>把一类隐蔽的运行期错误，钉死在最接近源头、最易诊断的地方</strong>——这是「快速失败」原则一个朴素而高频的应用，全书已多次见到（L37 的 Stale tool call、L48 的「库非空却无 session 表」、L52 的资源清理）。</p>

<h2>各司其职：每个 Provider owns 一格</h2>
<p>金字塔之所以不乱，是因为每一层 Provider 都<strong>只拥有一件事</strong>、互不越界。这种「单一职责」让每一格都能被单独理解、单独测试、单独替换。挑几个关键的看：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">SDKProvider（sdk.tsx）</div><div class="c-txt">造 opencode SDK 客户端、订阅 SSE 事件流；事件入队后<strong>批量 flush</strong>（一批事件→一次渲染，呼应 L54）</div></div>
  <div class="cell"><div class="c-tag">ProjectProvider（project.tsx）</div><div class="c-txt">用 <span class="mono">createStore</span> 持项目/实例/工作区状态，<span class="mono">sync()</span> 从 SDK 拉取</div></div>
  <div class="cell"><div class="c-tag">Sync / DataProvider</div><div class="c-txt">把服务器事件归约进响应式 store（下一课 L54 详解）</div></div>
  <div class="cell"><div class="c-tag">ThemeProvider（theme.tsx）</div><div class="c-txt">主题与调色板（亮/暗、各色），供组件取色</div></div>
  <div class="cell"><div class="c-tag">RouteProvider（route.tsx）</div><div class="c-txt"><span class="mono">createStore&lt;Route&gt;</span>(home/session/plugin)，<span class="mono">navigate()</span> 切屏</div></div>
  <div class="cell"><div class="c-tag">Dialog / PromptHistory / Frecency</div><div class="c-txt">对话框栈、prompt 历史、命令常用度等交互状态</div></div>
</div>
<p>这种「一个 Provider 一格关注点」的拆法，好处和 L44 配置、L47 provider 插件一脉相承：<strong>每一格都小而自洽、可独立读懂与修改</strong>，组件要什么就 <span class="mono">useXxx()</span> 精准取什么，绝不会被迫去依赖一个无所不包的巨型上帝对象。对比一下「把所有状态塞进一个大 App 组件」的反面：那样一来，任何一点状态变化都可能牵连整个 App 重渲染，任何一个组件都能摸到任何状态、改坏任何东西，代码很快就糊成一团。两种活法的差别，摊开看格外刺眼：</p>
<div class="cols">
  <div class="col"><h4>上帝对象 App（反面）</h4><p>所有状态塞进一个巨型组件。后果：谁都能摸到、改坏任何状态；一点变化牵连整个 App 重渲染；新人读不懂「这个值从哪来、谁在改」；测试要把整个世界 mock 起来。</p></div>
  <div class="col"><h4>Provider 金字塔（opencode）</h4><p>每格状态由一个 Provider 独家拥有。组件 <span class="mono">useXxx()</span> 精准取所需；所有权清晰、依赖显式；细粒度更新只触动用到该格的组件；每个 Provider 可独立读懂、独立改。</p></div>
</div>
<p>金字塔式的拆分，则让<strong>状态的所有权清清楚楚</strong>——某格状态由某个 Provider 独家拥有、独家维护，谁依赖谁一目了然。再配上 SolidJS 的细粒度响应式（L52），<strong>「拆得清」与「更得省」就合二为一了</strong>：边界清晰的状态格，天然就是细粒度更新的边界，一格变了只触动用到这一格的组件。这正是 opencode 的 TUI 能既复杂又有条理的结构性原因。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观视角</div>
  <p>这一课讲清了 opencode TUI 的应用结构——那座由近二十层 Provider 垒成、各司其职又依赖清晰的金字塔：</p>
  <ul>
    <li><strong>Provider 金字塔 = 结构化依赖注入</strong>（<span class="mono">app.tsx</span>）：近二十层 Provider 从外到内嵌套，<strong>每层只 owns 一件事</strong>（SDK 连接/Project 项目/Sync·Data 数据/Theme 主题/Route 路由/Dialog 对话框…）。一个组件可用的服务=它头顶所有 Provider 的并集。</li>
    <li><strong>嵌套顺序=依赖拓扑</strong>：内层 Provider 的 <span class="mono">init</span> 里 <span class="mono">use</span> 外层 context（如 <span class="mono">ProjectProvider</span> init 调 <span class="mono">useSDK()</span>），就钉下「SDK 必在 Project 外」的硬约束。塔从下到上=越基础越靠外：连接→项目→数据→主题→交互→界面。</li>
    <li><strong>同一个模子 createSimpleContext</strong>（<span class="mono">context/helper.tsx</span>）：封装「建 context + provider(跑 init、<span class="mono">&lt;Show when=ready&gt;</span> 门控) + use() 钩子」。一行解构出 <span class="mono">{ use, provider }</span>。每个 context 同形。</li>
    <li><strong>use() 快速失败</strong>：不在对应 Provider 内调用即抛「must be used within a context provider」——把「Provider 外用 context 拿到 undefined」这个隐蔽 bug 提前成当场报错（同 L37 Stale、L48 防呆的「快速失败」）。各司其职+细粒度响应式=拆得清即更得省。</li>
  </ul>
  <p>结构看清了——一座各司其职、依赖清晰的 Provider 金字塔。但你可能注意到 <span class="mono">SDKProvider</span> 里有个「事件入队、批量 flush」的细节，<span class="mono">Sync</span>/<span class="mono">Data</span> 两层更是专管「把事件变成状态」。下一课（L54）就钻进这条<strong>数据流</strong>：服务器的 SSE 事件如何经 reducer 归约进响应式 store、又如何用 16ms 的批处理把「一串事件」压成「一次渲染」。再往后 L55 讲 prompt 编辑器、L56 讲对话框与命令面板。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p><span class="mono">createSimpleContext</span> 本体短得惊人，却把样板与护栏一次封死（简化自 <span class="mono">helper.tsx</span>）：</p>
  <pre class="code"><span class="kw">export function</span> <span class="fn">createSimpleContext</span>(input) {
  <span class="kw">const</span> ctx = <span class="fn">createContext</span>()
  <span class="kw">return</span> {
    provider: (props) =&gt; {
      <span class="kw">const</span> init = input.<span class="fn">init</span>(props)              <span class="cm">// 初始化这一格</span>
      <span class="kw">return</span> (
        &lt;Show when={init.ready === undefined || init.ready === <span class="kw">true</span>}&gt;  <span class="cm">// ← 没就绪不渲染</span>
          &lt;ctx.Provider value={init}&gt;{props.children}&lt;/ctx.Provider&gt;
        &lt;/Show&gt;
      )
    },
    <span class="fn">use</span>() {
      <span class="kw">const</span> value = <span class="fn">useContext</span>(ctx)
      <span class="kw">if</span> (!value) <span class="kw">throw new</span> <span class="fn">Error</span>(<span class="st">`${'$'}{input.name} context must be used within a context provider`</span>)  <span class="cm">// ← 快速失败</span>
      <span class="kw">return</span> value
    },
  }
}</pre>
  <p>这十几行代码的价值，远超它的长度。它把一个在 SolidJS/React 项目里<strong>会被重复几十遍</strong>的样板（<span class="mono">createContext</span> → 写一个 Provider 组件 → 写一个 <span class="mono">useContext</span> + 判空的 hook）<strong>收敛成一处</strong>，于是新增一个 context 只需 <span class="mono">createSimpleContext({ name, init })</span> 一行。这本身就是「不要重复自己」的范本。但更深一层的妙处在于：<strong>它把「正确用法」做成了唯一好走的路</strong>。因为 <span class="mono">use()</span> 已经替你处理了「判空 + 报错」，没人会再图省事写一个「不判空、直接返回」的脆弱版本；因为 provider 已经统一了 <span class="mono">ready</span> 门控，异步就绪的处理也有了标准姿势。<strong>把一套良好实践（快速失败、就绪门控、命名一致）固化进一个谁都会顺手用的小工具里，远比写一篇『大家请记得判空』的规范文档有效得多</strong>——好的抽象不是用文档约束人，而是让正确的事成为最省力的事。这也呼应了全书一再出现的主题：用统一的小模子（L36 的 Tool.make、L47 的 PluginV2.define）把一类东西刻成同形，整个系统就因「处处同形」而易读、易扩、难出错。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>Provider 金字塔=结构化依赖注入</strong>（<span class="mono">app.tsx</span>）：近二十层 Provider 嵌套，每层只 owns 一件事；组件可用服务=头顶所有 Provider 的并集，要什么 <span class="mono">useXxx()</span> 精准取什么。</li>
    <li><strong>嵌套顺序=依赖拓扑</strong>：内层 init 里 use 外层 context（<span class="mono">ProjectProvider</span> 调 <span class="mono">useSDK()</span>→SDK 必在外）。塔从下到上越基础越靠外：连接(SDK)→项目→数据(Sync/Data)→主题→交互(Dialog…)→<span class="mono">&lt;App/&gt;</span>。</li>
    <li><strong>同一个模子 createSimpleContext</strong>（<span class="mono">helper.tsx</span>）：一行封「建 context+provider(init、<span class="mono">ready</span> 门控)+use()」。每个 context 同形——同 L36 Tool.make、L47 PluginV2.define「统一模子刻同形」。</li>
    <li><strong>use() 快速失败</strong>：<span class="mono">if(!value) throw</span>「must be used within a context provider」——把「Provider 外用 context→undefined→远处崩」的隐蔽 bug 提前成当场点名报错（同 L37/L48 快速失败）。</li>
    <li><strong>各司其职 vs 上帝对象</strong>：一格状态由一个 Provider 独家拥有，所有权清晰、可独立读懂/测试/替换；配 L52 细粒度响应式，边界清晰的状态格天然是细粒度更新边界——「拆得清」即「更得省」，是复杂 TUI 仍有条理的结构性原因。这套 Provider+use 模式在任何 React/SolidJS 项目都通用。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Last lesson we learned opentui paints a SolidJS component tree into a terminal interface. But <strong>what does that tree itself look like</strong>? Open <span class="mono">app.tsx</span> and you'll see a dizzying sight: inside <span class="mono">render()</span> nests <strong>nearly twenty layers</strong> of "Providers"—<span class="mono">ExitProvider</span> wraps <span class="mono">SDKProvider</span> wraps <span class="mono">ProjectProvider</span> wraps <span class="mono">SyncProvider</span> wraps <span class="mono">DataProvider</span> wraps <span class="mono">ThemeProvider</span>… layer wrapping layer, with the real <span class="mono">&lt;App/&gt;</span> only at the innermost. This lesson clarifies this <strong>"Provider pyramid"</strong>: it's not messy nesting but the skeleton by which opencode's TUI <strong>organizes app-wide shared state and services</strong>. Grasp it and you hold the map of "what any component wants, and where to get it" in the TUI code. This "Provider + use hook" pattern is precisely the <strong>mainstream answer</strong> for organizing global state in the React/SolidJS world—so though this lesson covers opencode's TUI, what you learn is structural craft directly reusable in any modern frontend project.</p>
<p>This lesson has two progressively deeper insights. First, <strong>this pyramid is a structured "dependency injection"</strong>: each Provider layer owns just <strong>one thing</strong> (SDK manages the server connection, Project the project state, Theme the theme, Route the routing…), and <strong>the nesting order encodes exactly the dependencies among them</strong>—<span class="mono">ProjectProvider</span>'s init calls <span class="mono">useSDK()</span>, so <span class="mono">SDKProvider</span> must wrap outside it. The outer is the foundation, the inner the superstructure; the services a component can use are the union of all Providers above it. Second, <strong>all these nearly-twenty Providers are stamped from the same mold</strong>: a little helper called <span class="mono">createSimpleContext</span> seals the boilerplate of "build context + write provider + give a use hook" once, so every context looks the same and has a <span class="mono">use()</span> that <strong>errors on the spot when used in the wrong place</strong>. Grasp these two and you no longer see a scary tangle of nesting but a <strong>cleanly-layered, single-responsibility, dependency-clear</strong> state pyramid.</p>

<div class="card analogy">
  <div class="tag">🏢 Analogy</div>
  Picture this Provider pyramid as a building's <strong>"layered utility infrastructure."</strong> The bottom layer is <strong>power</strong> (<span class="mono">SDKProvider</span>, the server connection—without it nothing in the building runs); above is <strong>water</strong> (<span class="mono">ProjectProvider</span>, but the pump needs power first, so it's installed above power); above that <strong>HVAC, network, security</strong> (Sync/Data/Theme/Dialog…), each utility layer <strong>depending on the layers below it</strong>. And any room in the building (a component), to use power calls <span class="mono">useSDK()</span>, to use the theme calls <span class="mono">useTheme()</span>—<strong>just "plug into the socket" and use it, no need to care which layer the service comes from or how it's wired in</strong>. The finest part is the "error in the wrong place" design: if you call <span class="mono">useSDK()</span> in a <strong>room not yet wired to power</strong>, the system won't silently hand you a null that mysteriously crashes later but <strong>immediately, clearly errors</strong> "you must use it inside SDKProvider"—like flipping a switch in an un-electrified shell room, the light not coming on tells you right away "no power here yet" rather than leaving you guessing in the dark.
</div>

<h2>The Provider pyramid: nesting is dependency</h2>
<p>In <span class="mono">app.tsx</span>'s <span class="mono">render()</span>, that long string of Providers roughly nests outer-to-inner in this order (outer in place first, inner can then use it):</p>
<div class="layers">
  <div class="layer"><span class="l-tag">ExitProvider / ErrorBoundary</span><span class="l-desc">outermost: exit hooks, error boundary (crash backstop)</span></div>
  <div class="layer"><span class="l-tag">SDKProvider</span><span class="l-desc">the server connection (SDK client + SSE event stream)—the source of all data</span></div>
  <div class="layer"><span class="l-tag">ProjectProvider</span><span class="l-desc">project/workspace state (init calls useSDK, so inside SDK)</span></div>
  <div class="layer"><span class="l-tag">SyncProvider → DataProvider</span><span class="l-desc">event→store reduction (next lesson's theme, depends on SDK's events)</span></div>
  <div class="layer"><span class="l-tag">ThemeProvider</span><span class="l-desc">theme/palette</span></div>
  <div class="layer"><span class="l-tag">Dialog / Frecency / PromptHistory…</span><span class="l-desc">dialogs, frecency, prompt history and other interaction state</span></div>
  <div class="layer"><span class="l-tag">&lt;App/&gt;</span><span class="l-desc">innermost: the real interface, free to use all Providers' services above it</span></div>
</div>
<p>This nesting order is <strong>by no means arbitrary</strong>—it's a topological sort of a <strong>dependency graph</strong>. Look at <span class="mono">project.tsx</span> to get it: <span class="mono">ProjectProvider</span>'s <span class="mono">init</span> function's first line is <span class="mono">const sdk = useSDK()</span>—it uses the SDK to fetch project info. Since <span class="mono">useSDK()</span> can only be used inside <span class="mono">SDKProvider</span>, <span class="mono">ProjectProvider</span> <strong>must</strong> be wrapped by <span class="mono">SDKProvider</span>. Likewise, <span class="mono">RouteProvider</span>'s <span class="mono">init</span> uses <span class="mono">useTuiStartup()</span>, <span class="mono">DataProvider</span> depends on <span class="mono">SyncProvider</span>'s events… <strong>every "inner init calling an outer use" nails down a hard "who must be outside whom" constraint in this pyramid</strong>. So this tower, bottom to top, is exactly a dependency chain of "the more fundamental the more outer, the more upper the more inner": connection (SDK) → project → data sync → theme → interaction state → interface. This "express dependency via nesting order" technique is actually cleverer than an explicit dependency declaration: you <strong>needn't write a separate "who depends on whom" table</strong>—the dependencies are <strong>physically</strong> embodied in the code's indentation levels: the outer is always in place before the inner, the inner naturally uses everything in the outer. Reading that nesting in <span class="mono">app.tsx</span> top to bottom is walking the whole App's "service dependency graph" from foundation to roof. A newcomer wanting to understand "in what order the various services come up at TUI startup" needn't read docs—just look at this JSX's nesting order—<strong>the structure itself is the documentation</strong>.</p>

<h2>The same mold: createSimpleContext</h2>
<p>Of the nearly twenty Providers, not one is hand-written from scratch—they're all stamped from a little helper called <span class="mono">createSimpleContext</span> (<span class="mono">context/helper.tsx</span>). Rather than have each context write the boilerplate of "build context, write Provider, write use hook" anew (and easily forget a null-check or a gate somewhere), better to seal this boilerplate into a tool and have all contexts come from the same mold. This helper packs "SolidJS's context trio" into one line:</p>
<div class="flow">
  <div class="f-node">createSimpleContext<br><small>{ name, init }</small></div>
  <div class="f-arrow">produces →</div>
  <div class="f-node">provider component<br><small>runs init(props), gates on ready</small></div>
  <div class="f-arrow">+</div>
  <div class="f-node">use() hook<br><small>get value, errors on spot if missing</small></div>
</div>
<p>Using it is one destructuring line: <span class="mono">const { use: useSDK, provider: SDKProvider } = createSimpleContext({ name: "SDK", init: (props) =&gt; {…} })</span>. This little wrapper hides two thoughtful designs. First, the <strong>"don't render until ready" gate</strong>: the provider has a <span class="mono">&lt;Show when={init.ready !== false}&gt;</span>, so if a context needs async prep (e.g. connect to the server first), it can <strong>not render its subtree until ready</strong>, avoiding components below getting a half-baked state. Second, and the most pointed—<strong>that throwing <span class="mono">use()</span></strong>:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">name</div><div class="c-txt">this context's name (only for the error message)</div></div>
  <div class="cell"><div class="c-tag">init(props)</div><div class="c-txt">initializes this cell of state/service (may use outer contexts inside)</div></div>
  <div class="cell"><div class="c-tag">ready gate</div><div class="c-txt"><span class="mono">&lt;Show when={ready}&gt;</span>—don't render the subtree until ready</div></div>
  <div class="cell"><div class="c-tag">use() errors</div><div class="c-txt">not called inside the matching Provider → immediately throws "must be used within a context provider"</div></div>
</div>
<p>That <span class="mono">if (!value) throw new Error(...)</span> in <span class="mono">use()</span> seems unremarkable yet is a <strong>highly valuable guardrail</strong>. When a component calls <span class="mono">useSDK()</span>, behind it is this "look upward" chain:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">component calls <span class="mono">useSDK()</span> → internally <span class="mono">useContext(SDK ctx)</span></span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">SolidJS walks <strong>up</strong> the component tree for the nearest <span class="mono">SDKProvider</span></span></div>
  <div class="t-row"><span class="t-num">3a</span><span class="t-txt">found → returns that Provider's <span class="mono">init</span> value (the SDK client)</span></div>
  <div class="t-row"><span class="t-num">3b</span><span class="t-txt">not found (not inside a Provider) → value empty → <strong>throws on the spot</strong>, naming "SDK"</span></div>
</div>
<p>In SolidJS/React, one of the most common and hardest-to-trace bugs is "using a context outside its Provider, getting undefined, then crashing somewhere utterly unrelated." Here it <strong>moves this error from a 'silent undefined' forward to a 'loud on-the-spot error'</strong>—the moment you misplace a component (forget to wrap it in some Provider), the very first run tells you "<span class="mono">SDK context must be used within a context provider</span>," even naming the specific context. <strong>Nailing a class of hidden runtime error to the spot closest to the source and easiest to diagnose</strong>—this is a plain, high-frequency application of the "fail fast" principle, seen many times across the book (L37's Stale tool call, L48's "DB non-empty yet no session table," L52's resource cleanup).</p>

<h2>Single responsibility: each Provider owns one cell</h2>
<p>The pyramid stays orderly because each Provider layer <strong>owns just one thing</strong>, never overstepping. This "single responsibility" lets each cell be understood, tested, and replaced on its own. A few key ones:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">SDKProvider (sdk.tsx)</div><div class="c-txt">builds the opencode SDK client, subscribes to the SSE event stream; events queued then <strong>batch-flushed</strong> (a batch of events→one render, echoing L54)</div></div>
  <div class="cell"><div class="c-tag">ProjectProvider (project.tsx)</div><div class="c-txt">holds project/instance/workspace state with <span class="mono">createStore</span>, <span class="mono">sync()</span> fetches from the SDK</div></div>
  <div class="cell"><div class="c-tag">Sync / DataProvider</div><div class="c-txt">reduces server events into reactive stores (detailed next lesson L54)</div></div>
  <div class="cell"><div class="c-tag">ThemeProvider (theme.tsx)</div><div class="c-txt">theme and palette (light/dark, colors), for components to pick colors</div></div>
  <div class="cell"><div class="c-tag">RouteProvider (route.tsx)</div><div class="c-txt"><span class="mono">createStore&lt;Route&gt;</span>(home/session/plugin), <span class="mono">navigate()</span> switches screens</div></div>
  <div class="cell"><div class="c-tag">Dialog / PromptHistory / Frecency</div><div class="c-txt">dialog stack, prompt history, command frecency and other interaction state</div></div>
</div>
<p>This "one Provider one cell of concern" split's benefits are of a piece with L44's config and L47's provider plugins: <strong>each cell is small and self-consistent, independently readable and changeable</strong>, a component grabs precisely what it wants via <span class="mono">useXxx()</span>, never forced to depend on an all-encompassing god object. Contrast the opposite, "stuff all state into one big App component": then any bit of state change can drag the whole App into re-rendering, any component can touch any state and break anything, and the code quickly congeals into a mess. The two ways of living, laid out, are starkly different:</p>
<div class="cols">
  <div class="col"><h4>god-object App (the bad)</h4><p>all state stuffed into one giant component. Consequence: anyone can touch and break any state; one change drags the whole App into re-render; newcomers can't tell "where this value comes from, who changes it"; testing must mock the whole world.</p></div>
  <div class="col"><h4>Provider pyramid (opencode)</h4><p>each cell of state exclusively owned by one Provider. Components <span class="mono">useXxx()</span> grab precisely what's needed; ownership clear, dependencies explicit; fine-grained updates touch only components using that cell; each Provider independently readable, independently changeable.</p></div>
</div>
<p>The pyramid split makes <strong>state ownership crystal clear</strong>—some cell of state is exclusively owned and maintained by some Provider, who depends on whom at a glance. Paired with SolidJS's fine-grained reactivity (L52), <strong>"split clean" and "update lean" become one</strong>: a cleanly-bounded state cell is naturally the boundary of fine-grained updates, change one cell and only components using it are touched. This is exactly the structural reason opencode's TUI can be both complex and orderly.</p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>This lesson clarifies opencode TUI's app structure—that pyramid built of nearly twenty Provider layers, each with its own role yet dependency-clear:</p>
  <ul>
    <li><strong>Provider pyramid = structured dependency injection</strong> (<span class="mono">app.tsx</span>): nearly twenty Providers nest outer-to-inner, <strong>each owning one thing</strong> (SDK connection/Project/Sync·Data data/Theme/Route/Dialog…). A component's available services = the union of all Providers above it.</li>
    <li><strong>nesting order = dependency topology</strong>: an inner Provider's <span class="mono">init</span> uses an outer context (e.g. <span class="mono">ProjectProvider</span> init calls <span class="mono">useSDK()</span>), nailing "SDK must be outside Project." The tower bottom-to-top = more fundamental more outer: connection→project→data→theme→interaction→interface. The structure is the documentation.</li>
    <li><strong>the same mold createSimpleContext</strong> (<span class="mono">context/helper.tsx</span>): packs "build context + provider (run init, <span class="mono">&lt;Show when=ready&gt;</span> gate) + use() hook." One destructuring line yields <span class="mono">{ use, provider }</span>. Every context same-shaped.</li>
    <li><strong>use() fails fast</strong>: not called inside the matching Provider throws "must be used within a context provider"—moving the hidden bug of "use context outside Provider→undefined→crash elsewhere" forward to an on-the-spot named error (like L37 Stale, L48's guard "fail fast"). Single responsibility + fine-grained reactivity = split clean is update lean.</li>
  </ul>
  <p>The structure is clear—a single-responsibility, dependency-clear Provider pyramid. But you may have noticed <span class="mono">SDKProvider</span> has an "events queued, batch-flushed" detail, and the <span class="mono">Sync</span>/<span class="mono">Data</span> layers specifically manage "turning events into state." The next lesson (L54) drills into this <strong>data flow</strong>: how the server's SSE events get reduced into reactive stores via reducers, and how 16ms batching squeezes "a string of events" into "one render." Further on, L55 covers the prompt editor, L56 dialogs and the command palette.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p><span class="mono">createSimpleContext</span> itself is astonishingly short yet seals the boilerplate and guardrail at once (simplified from <span class="mono">helper.tsx</span>):</p>
  <pre class="code"><span class="kw">export function</span> <span class="fn">createSimpleContext</span>(input) {
  <span class="kw">const</span> ctx = <span class="fn">createContext</span>()
  <span class="kw">return</span> {
    provider: (props) =&gt; {
      <span class="kw">const</span> init = input.<span class="fn">init</span>(props)              <span class="cm">// initialize this cell</span>
      <span class="kw">return</span> (
        &lt;Show when={init.ready === undefined || init.ready === <span class="kw">true</span>}&gt;  <span class="cm">// ← don't render until ready</span>
          &lt;ctx.Provider value={init}&gt;{props.children}&lt;/ctx.Provider&gt;
        &lt;/Show&gt;
      )
    },
    <span class="fn">use</span>() {
      <span class="kw">const</span> value = <span class="fn">useContext</span>(ctx)
      <span class="kw">if</span> (!value) <span class="kw">throw new</span> <span class="fn">Error</span>(<span class="st">`${'$'}{input.name} context must be used within a context provider`</span>)  <span class="cm">// ← fail fast</span>
      <span class="kw">return</span> value
    },
  }
}</pre>
  <p>These dozen lines' value far exceeds their length. They <strong>converge to one place</strong> a boilerplate that in a SolidJS/React project <strong>would be repeated dozens of times</strong> (<span class="mono">createContext</span> → write a Provider component → write a <span class="mono">useContext</span> + null-check hook), so adding a context needs only the one line <span class="mono">createSimpleContext({ name, init })</span>. That itself is a model of "don't repeat yourself." But the deeper cleverness: <strong>it makes "the correct usage" the only easy road</strong>. Because <span class="mono">use()</span> already handles "null-check + error" for you, no one will, to save effort, write a fragile "no-check, return directly" version; because the provider already standardizes the <span class="mono">ready</span> gate, async readiness has a standard posture too. <strong>Solidifying a set of good practices (fail fast, readiness gate, consistent naming) into a little tool everyone reaches for is far more effective than writing a 'please remember to null-check' guideline doc</strong>—a good abstraction doesn't constrain people with docs but makes the right thing the least-effort thing. This also echoes a recurring book theme: stamping a class of things into the same shape with a uniform little mold (L36's Tool.make, L47's PluginV2.define) makes the whole system, by "same shape everywhere," easy to read, easy to extend, hard to get wrong.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>Provider pyramid = structured dependency injection</strong> (<span class="mono">app.tsx</span>): nearly twenty Providers nested, each owning one thing; a component's available services = the union of all Providers above it, grab precisely what's wanted via <span class="mono">useXxx()</span>.</li>
    <li><strong>nesting order = dependency topology</strong>: an inner init uses an outer context (<span class="mono">ProjectProvider</span> calls <span class="mono">useSDK()</span>→SDK must be outside). The tower bottom-to-top more fundamental more outer: connection(SDK)→project→data(Sync/Data)→theme→interaction(Dialog…)→<span class="mono">&lt;App/&gt;</span>.</li>
    <li><strong>the same mold createSimpleContext</strong> (<span class="mono">helper.tsx</span>): one line packs "build context+provider(init, <span class="mono">ready</span> gate)+use()." Every context same-shaped—like L36 Tool.make, L47 PluginV2.define "uniform mold stamps same shape."</li>
    <li><strong>use() fails fast</strong>: <span class="mono">if(!value) throw</span> "must be used within a context provider"—moving the hidden bug of "use context outside Provider→undefined→crash afar" forward to an on-the-spot named error (like L37/L48 fail fast).</li>
    <li><strong>single responsibility vs god object</strong>: each cell of state exclusively owned by one Provider, ownership clear, independently readable/testable/replaceable; paired with L52 fine-grained reactivity, a cleanly-bounded state cell is naturally the boundary of fine-grained updates—"split clean" is "update lean," the structural reason a complex TUI stays orderly. This Provider+use pattern is universal in any React/SolidJS project.</li>
  </ul>
</div>
""",
}
LESSON_54 = wip('事件到 store', 'Events to store')
LESSON_55 = wip('prompt 组件', 'The prompt component')
LESSON_56 = wip('对话框与 scrollback', 'Dialogs & scrollback')
