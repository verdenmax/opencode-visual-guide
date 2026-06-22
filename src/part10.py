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
<p class="lead">上一课我们知道了 opentui 会把一棵 SolidJS 组件树画成终端界面。但<strong>那棵树本身长什么样</strong>？翻开 <span class="mono">app.tsx</span>，你会看到一个让人眼前一晕的景象：<span class="mono">render()</span> 里嵌套着<strong>二十多层</strong>的「Provider」——<span class="mono">ExitProvider</span> 套 <span class="mono">SDKProvider</span> 套 <span class="mono">ProjectProvider</span> 套 <span class="mono">SyncProvider</span> 套 <span class="mono">DataProvider</span> 套 <span class="mono">ThemeProvider</span>……一层裹一层，最里面才是真正的 <span class="mono">&lt;App/&gt;</span>。这一课就讲清这座<strong>「Provider 金字塔」</strong>：它不是杂乱的嵌套，而是 opencode TUI <strong>组织全 App 共享状态与服务</strong>的骨架。读懂它，你就拿到了在 TUI 代码里「任何一个组件想要什么、去哪儿拿」的地图。这套「Provider + use 钩子」的模式，正是 React/SolidJS 世界里组织全局状态的<strong>主流答案</strong>——所以这一课讲的虽是 opencode 的 TUI，学到的却是一套你在任何现代前端项目里都能直接复用的结构功夫。</p>
<p>这一课有两个层层递进的洞见。第一，<strong>这座金字塔是一套结构化的「依赖注入」</strong>：每一层 Provider 只负责<strong>一件事</strong>（SDK 管和服务器的连接、Project 管项目状态、Theme 管主题、Route 管路由……），而<strong>嵌套的顺序，编码的正是它们之间的依赖关系</strong>——<span class="mono">ProjectProvider</span> 的初始化里要 <span class="mono">useSDK()</span>，所以 <span class="mono">SDKProvider</span> 必须裹在它外面。外层是地基、内层是上层建筑，一个组件能用到的「服务」，就是它头顶所有 Provider 的并集。第二，<strong>这二十多个 Provider 全用同一个模子刻出来</strong>：一个叫 <span class="mono">createSimpleContext</span> 的小助手，把「建 context + 写 provider + 给 use 钩子」这套样板一次封好，于是每个 context 都长一个样、都有一个<strong>用错地方就当场报错</strong>的 <span class="mono">use()</span>。读懂这两点，你看到的就不再是一团吓人的嵌套，而是一座<strong>层次分明、各司其职、依赖清晰</strong>的状态金字塔。</p>

<div class="card analogy">
  <div class="tag">🏢 生活类比</div>
  把这座 Provider 金字塔想象成一栋大楼的<strong>「公共设施分层」</strong>。最底层是<strong>供电</strong>（<span class="mono">SDKProvider</span>，和服务器的连接——没有它楼里什么都转不起来）；往上是<strong>供水</strong>（<span class="mono">ProjectProvider</span>，但水泵得先有电，所以它装在供电之上）；再往上是<strong>暖通、网络、安防</strong>（Sync/Data/Theme/Dialog……），每一层设施都<strong>依赖它下面的层</strong>。而楼里任何一个房间（一个组件），想用电就 <span class="mono">useSDK()</span>、想用主题就 <span class="mono">useTheme()</span>——<strong>直接「插上插座」取用即可，不必关心这服务是从哪一层、怎么接进来的</strong>。最妙的是那个「用错地方就报错」的设计：如果你在一个<strong>没接通供电的房间</strong>里去 <span class="mono">useSDK()</span>，系统不会默默给你一个空值让你之后莫名其妙地崩，而是<strong>立刻明确报错</strong>「你得在 SDKProvider 里头用」——就像在没通电的毛坯房按开关，灯不亮会立刻告诉你「这儿还没通电」，而非让你对着黑灯瞎猜。
</div>

<h2>Provider 金字塔：嵌套即依赖</h2>
<p><span class="mono">app.tsx</span> 的 <span class="mono">render()</span> 里，那一长串 Provider 大致按这个顺序从外到内嵌套（外层先就位、内层才能用上）。下面这张图只画<strong>依赖 SDK 的那条主链</strong>；另有 Route、Toast、KV 等<strong>不</strong>依赖 SDK 的 provider，其实裹在比 SDK 更外层，为聚焦从略：</p>
<div class="layers">
  <div class="layer"><span class="l-tag">ExitProvider / ErrorBoundary</span><span class="l-desc">最外层：退出钩子、错误边界（兜底崩溃）</span></div>
  <div class="layer"><span class="l-tag">SDKProvider</span><span class="l-desc">和服务器的连接（SDK 客户端 + SSE 事件流）——一切数据的源头</span></div>
  <div class="layer"><span class="l-tag">ProjectProvider</span><span class="l-desc">项目/工作区状态（init 里 useSDK，故在 SDK 之内）</span></div>
  <div class="layer"><span class="l-tag">SyncProvider → DataProvider</span><span class="l-desc">事件→store 的归约（下一课主题，依赖 SDK 的事件）</span></div>
  <div class="layer"><span class="l-tag">ThemeProvider</span><span class="l-desc">主题/调色板</span></div>
  <div class="layer"><span class="l-tag">Dialog / Frecency / PromptHistory…</span><span class="l-desc">对话框、常用度、prompt 历史等交互状态</span></div>
  <div class="layer"><span class="l-tag">&lt;App/&gt;</span><span class="l-desc">最里层：真正的界面，头顶所有 Provider 的服务任它取用</span></div>
</div>
<p>这个嵌套顺序<strong>绝非随意</strong>——它是一张<strong>依赖关系图</strong>的拓扑排序。看 <span class="mono">project.tsx</span> 就明白了：<span class="mono">ProjectProvider</span> 的 <span class="mono">init</span> 函数第一行就是 <span class="mono">const sdk = useSDK()</span>——它要用 SDK 去拉项目信息。既然 <span class="mono">useSDK()</span> 只能在 <span class="mono">SDKProvider</span> 内部用，那 <span class="mono">ProjectProvider</span> 就<strong>必须</strong>被 <span class="mono">SDKProvider</span> 包在里头。同理，<span class="mono">RouteProvider</span> 的 <span class="mono">init</span> 只用 <span class="mono">useTuiStartup()</span>、<strong>并不</strong>依赖 SDK，所以它<strong>反而裹在 <span class="mono">SDKProvider</span> 之外</strong>（同在外层的还有 Toast、KV 等）；而 <span class="mono">SyncProvider</span> 与 <span class="mono">DataProvider</span> 的 <span class="mono">init</span> 都通过 <span class="mono">useEvent()</span>（其内部又调 <span class="mono">useSDK()</span>）<strong>各自独立地</strong>消费 SDK 的事件流——两者都依赖 SDK、故都在 SDKProvider 之内（它俩彼此并不依赖，<span class="mono">Sync→Data</span> 的相邻只是惯例排序）……<strong>每一处「内层 init 调用外层的 use」，都在这座金字塔里钉下一条「谁必须在谁外面」的硬约束</strong>。于是这座塔从下到上，恰好是一条「越基础越靠外、越上层越靠内」的依赖链：连接（SDK）→ 项目 → 数据同步 → 主题 → 交互状态 → 界面。这种「用嵌套顺序表达依赖」的手法，其实比一份显式的依赖声明更巧妙：你<strong>无需另写一张「谁依赖谁」的表</strong>，依赖关系就<strong>物理地</strong>体现在代码的缩进层级里——外层一定先于内层就位，内层天然能用上外层的一切。读 <span class="mono">app.tsx</span> 那段嵌套，从上往下读一遍，就等于把整个 App 的「服务依赖图」从地基到屋顶走了一遍。一个新人想搞懂「TUI 启动时各种服务按什么顺序就位」，不必翻文档，看这一段 JSX 的嵌套顺序即可——<strong>结构本身就是文档</strong>。</p>

<h2>同一个模子：createSimpleContext</h2>
<p>二十多个 Provider，没有一个是从零手写的——它们全用一个叫 <span class="mono">createSimpleContext</span> 的小助手（<span class="mono">context/helper.tsx</span>）刻出来。与其让每个 context 各写一遍「建 context、写 Provider、写 use 钩子」的样板（还很容易在某一处忘了判空、忘了门控），不如把这套样板封进一个工具、让所有 context 都从同一个模子里出来。这个助手把「SolidJS 的 context 三件套」封成一行：</p>
<div class="flow">
  <div class="f-node">createSimpleContext<br><small>{ name, init }</small></div>
  <div class="f-arrow">产出 →</div>
  <div class="f-node">provider 组件<br><small>跑 init(props)、按 ready 门控</small></div>
  <div class="f-arrow">+</div>
  <div class="f-node">use() 钩子<br><small>取值，缺则当场报错</small></div>
</div>
<p>用起来就是一行解构：<span class="mono">const { use: useSDK, provider: SDKProvider } = createSimpleContext({ name: "SDK", init: (props) =&gt; {…} })</span>。这个小封装藏着两个体贴的设计。其一，<strong>「未就绪就先不渲染」的门控</strong>：provider 里有个 <span class="mono">&lt;Show when={init.ready === undefined || init.ready === true}&gt;</span>，如果某个 context 需要异步准备（如先连上服务器），可以让它<strong>在没就绪时不渲染子树</strong>，避免下面的组件拿到半成品状态。其二，也是最点睛的——<strong>那个会抛错的 <span class="mono">use()</span></strong>：</p>
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
  <p>这一课讲清了 opencode TUI 的应用结构——那座由二十多层 Provider 垒成、各司其职又依赖清晰的金字塔：</p>
  <ul>
    <li><strong>Provider 金字塔 = 结构化依赖注入</strong>（<span class="mono">app.tsx</span>）：二十多层 Provider 从外到内嵌套，<strong>每层只 owns 一件事</strong>（SDK 连接/Project 项目/Sync·Data 数据/Theme 主题/Route 路由/Dialog 对话框…）。一个组件可用的服务=它头顶所有 Provider 的并集。</li>
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
      <span class="kw">if</span> (!value) <span class="kw">throw new</span> <span class="fn">Error</span>(<span class="st">`${input.name} context must be used within a context provider`</span>)  <span class="cm">// ← 快速失败</span>
      <span class="kw">return</span> value
    },
  }
}</pre>
  <p>这十几行代码的价值，远超它的长度。它把一个在 SolidJS/React 项目里<strong>会被重复几十遍</strong>的样板（<span class="mono">createContext</span> → 写一个 Provider 组件 → 写一个 <span class="mono">useContext</span> + 判空的 hook）<strong>收敛成一处</strong>，于是新增一个 context 只需 <span class="mono">createSimpleContext({ name, init })</span> 一行。这本身就是「不要重复自己」的范本。但更深一层的妙处在于：<strong>它把「正确用法」做成了唯一好走的路</strong>。因为 <span class="mono">use()</span> 已经替你处理了「判空 + 报错」，没人会再图省事写一个「不判空、直接返回」的脆弱版本；因为 provider 已经统一了 <span class="mono">ready</span> 门控，异步就绪的处理也有了标准姿势。<strong>把一套良好实践（快速失败、就绪门控、命名一致）固化进一个谁都会顺手用的小工具里，远比写一篇『大家请记得判空』的规范文档有效得多</strong>——好的抽象不是用文档约束人，而是让正确的事成为最省力的事。这也呼应了全书一再出现的主题：用统一的小模子（L36 的 Tool.make、L47 的 PluginV2.define）把一类东西刻成同形，整个系统就因「处处同形」而易读、易扩、难出错。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>Provider 金字塔=结构化依赖注入</strong>（<span class="mono">app.tsx</span>）：二十多层 Provider 嵌套，每层只 owns 一件事；组件可用服务=头顶所有 Provider 的并集，要什么 <span class="mono">useXxx()</span> 精准取什么。</li>
    <li><strong>嵌套顺序=依赖拓扑</strong>：内层 init 里 use 外层 context（<span class="mono">ProjectProvider</span> 调 <span class="mono">useSDK()</span>→SDK 必在外）。塔从下到上越基础越靠外：连接(SDK)→项目→数据(Sync/Data)→主题→交互(Dialog…)→<span class="mono">&lt;App/&gt;</span>。</li>
    <li><strong>同一个模子 createSimpleContext</strong>（<span class="mono">helper.tsx</span>）：一行封「建 context+provider(init、<span class="mono">ready</span> 门控)+use()」。每个 context 同形——同 L36 Tool.make、L47 PluginV2.define「统一模子刻同形」。</li>
    <li><strong>use() 快速失败</strong>：<span class="mono">if(!value) throw</span>「must be used within a context provider」——把「Provider 外用 context→undefined→远处崩」的隐蔽 bug 提前成当场点名报错（同 L37/L48 快速失败）。</li>
    <li><strong>各司其职 vs 上帝对象</strong>：一格状态由一个 Provider 独家拥有，所有权清晰、可独立读懂/测试/替换；配 L52 细粒度响应式，边界清晰的状态格天然是细粒度更新边界——「拆得清」即「更得省」，是复杂 TUI 仍有条理的结构性原因。这套 Provider+use 模式在任何 React/SolidJS 项目都通用。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Last lesson we learned opentui paints a SolidJS component tree into a terminal interface. But <strong>what does that tree itself look like</strong>? Open <span class="mono">app.tsx</span> and you'll see a dizzying sight: inside <span class="mono">render()</span> nests <strong>twenty-some layers</strong> of "Providers"—<span class="mono">ExitProvider</span> wraps <span class="mono">SDKProvider</span> wraps <span class="mono">ProjectProvider</span> wraps <span class="mono">SyncProvider</span> wraps <span class="mono">DataProvider</span> wraps <span class="mono">ThemeProvider</span>… layer wrapping layer, with the real <span class="mono">&lt;App/&gt;</span> only at the innermost. This lesson clarifies this <strong>"Provider pyramid"</strong>: it's not messy nesting but the skeleton by which opencode's TUI <strong>organizes app-wide shared state and services</strong>. Grasp it and you hold the map of "what any component wants, and where to get it" in the TUI code. This "Provider + use hook" pattern is precisely the <strong>mainstream answer</strong> for organizing global state in the React/SolidJS world—so though this lesson covers opencode's TUI, what you learn is structural craft directly reusable in any modern frontend project.</p>
<p>This lesson has two progressively deeper insights. First, <strong>this pyramid is a structured "dependency injection"</strong>: each Provider layer owns just <strong>one thing</strong> (SDK manages the server connection, Project the project state, Theme the theme, Route the routing…), and <strong>the nesting order encodes exactly the dependencies among them</strong>—<span class="mono">ProjectProvider</span>'s init calls <span class="mono">useSDK()</span>, so <span class="mono">SDKProvider</span> must wrap outside it. The outer is the foundation, the inner the superstructure; the services a component can use are the union of all Providers above it. Second, <strong>all these nearly-twenty Providers are stamped from the same mold</strong>: a little helper called <span class="mono">createSimpleContext</span> seals the boilerplate of "build context + write provider + give a use hook" once, so every context looks the same and has a <span class="mono">use()</span> that <strong>errors on the spot when used in the wrong place</strong>. Grasp these two and you no longer see a scary tangle of nesting but a <strong>cleanly-layered, single-responsibility, dependency-clear</strong> state pyramid.</p>

<div class="card analogy">
  <div class="tag">🏢 Analogy</div>
  Picture this Provider pyramid as a building's <strong>"layered utility infrastructure."</strong> The bottom layer is <strong>power</strong> (<span class="mono">SDKProvider</span>, the server connection—without it nothing in the building runs); above is <strong>water</strong> (<span class="mono">ProjectProvider</span>, but the pump needs power first, so it's installed above power); above that <strong>HVAC, network, security</strong> (Sync/Data/Theme/Dialog…), each utility layer <strong>depending on the layers below it</strong>. And any room in the building (a component), to use power calls <span class="mono">useSDK()</span>, to use the theme calls <span class="mono">useTheme()</span>—<strong>just "plug into the socket" and use it, no need to care which layer the service comes from or how it's wired in</strong>. The finest part is the "error in the wrong place" design: if you call <span class="mono">useSDK()</span> in a <strong>room not yet wired to power</strong>, the system won't silently hand you a null that mysteriously crashes later but <strong>immediately, clearly errors</strong> "you must use it inside SDKProvider"—like flipping a switch in an un-electrified shell room, the light not coming on tells you right away "no power here yet" rather than leaving you guessing in the dark.
</div>

<h2>The Provider pyramid: nesting is dependency</h2>
<p>In <span class="mono">app.tsx</span>'s <span class="mono">render()</span>, that long string of Providers roughly nests outer-to-inner in this order (outer in place first, inner can then use it). The diagram below draws only the <strong>SDK-rooted main chain</strong>; other providers like Route, Toast, KV that <strong>don't</strong> depend on the SDK actually wrap further out than SDK, omitted here for focus:</p>
<div class="layers">
  <div class="layer"><span class="l-tag">ExitProvider / ErrorBoundary</span><span class="l-desc">outermost: exit hooks, error boundary (crash backstop)</span></div>
  <div class="layer"><span class="l-tag">SDKProvider</span><span class="l-desc">the server connection (SDK client + SSE event stream)—the source of all data</span></div>
  <div class="layer"><span class="l-tag">ProjectProvider</span><span class="l-desc">project/workspace state (init calls useSDK, so inside SDK)</span></div>
  <div class="layer"><span class="l-tag">SyncProvider → DataProvider</span><span class="l-desc">event→store reduction (next lesson's theme, depends on SDK's events)</span></div>
  <div class="layer"><span class="l-tag">ThemeProvider</span><span class="l-desc">theme/palette</span></div>
  <div class="layer"><span class="l-tag">Dialog / Frecency / PromptHistory…</span><span class="l-desc">dialogs, frecency, prompt history and other interaction state</span></div>
  <div class="layer"><span class="l-tag">&lt;App/&gt;</span><span class="l-desc">innermost: the real interface, free to use all Providers' services above it</span></div>
</div>
<p>This nesting order is <strong>by no means arbitrary</strong>—it's a topological sort of a <strong>dependency graph</strong>. Look at <span class="mono">project.tsx</span> to get it: <span class="mono">ProjectProvider</span>'s <span class="mono">init</span> function's first line is <span class="mono">const sdk = useSDK()</span>—it uses the SDK to fetch project info. Since <span class="mono">useSDK()</span> can only be used inside <span class="mono">SDKProvider</span>, <span class="mono">ProjectProvider</span> <strong>must</strong> be wrapped by <span class="mono">SDKProvider</span>. Likewise, <span class="mono">RouteProvider</span>'s <span class="mono">init</span> uses only <span class="mono">useTuiStartup()</span> and <strong>doesn't</strong> depend on the SDK, so it actually wraps <strong>outside</strong> <span class="mono">SDKProvider</span> (along with Toast, KV, etc.); while both <span class="mono">SyncProvider</span>'s and <span class="mono">DataProvider</span>'s <span class="mono">init</span> consume the SDK event stream <strong>each independently</strong> via <span class="mono">useEvent()</span> (which internally calls <span class="mono">useSDK()</span>)—both depend on SDK, so both sit inside SDKProvider (they don't depend on each other; the adjacent <span class="mono">Sync→Data</span> order is just convention)… <strong>every "inner init calling an outer use" nails down a hard "who must be outside whom" constraint in this pyramid</strong>. So this tower, bottom to top, is exactly a dependency chain of "the more fundamental the more outer, the more upper the more inner": connection (SDK) → project → data sync → theme → interaction state → interface. This "express dependency via nesting order" technique is actually cleverer than an explicit dependency declaration: you <strong>needn't write a separate "who depends on whom" table</strong>—the dependencies are <strong>physically</strong> embodied in the code's indentation levels: the outer is always in place before the inner, the inner naturally uses everything in the outer. Reading that nesting in <span class="mono">app.tsx</span> top to bottom is walking the whole App's "service dependency graph" from foundation to roof. A newcomer wanting to understand "in what order the various services come up at TUI startup" needn't read docs—just look at this JSX's nesting order—<strong>the structure itself is the documentation</strong>.</p>

<h2>The same mold: createSimpleContext</h2>
<p>Of the twenty-some Providers, not one is hand-written from scratch—they're all stamped from a little helper called <span class="mono">createSimpleContext</span> (<span class="mono">context/helper.tsx</span>). Rather than have each context write the boilerplate of "build context, write Provider, write use hook" anew (and easily forget a null-check or a gate somewhere), better to seal this boilerplate into a tool and have all contexts come from the same mold. This helper packs "SolidJS's context trio" into one line:</p>
<div class="flow">
  <div class="f-node">createSimpleContext<br><small>{ name, init }</small></div>
  <div class="f-arrow">produces →</div>
  <div class="f-node">provider component<br><small>runs init(props), gates on ready</small></div>
  <div class="f-arrow">+</div>
  <div class="f-node">use() hook<br><small>get value, errors on spot if missing</small></div>
</div>
<p>Using it is one destructuring line: <span class="mono">const { use: useSDK, provider: SDKProvider } = createSimpleContext({ name: "SDK", init: (props) =&gt; {…} })</span>. This little wrapper hides two thoughtful designs. First, the <strong>"don't render until ready" gate</strong>: the provider has a <span class="mono">&lt;Show when={init.ready === undefined || init.ready === true}&gt;</span>, so if a context needs async prep (e.g. connect to the server first), it can <strong>not render its subtree until ready</strong>, avoiding components below getting a half-baked state. Second, and the most pointed—<strong>that throwing <span class="mono">use()</span></strong>:</p>
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
  <p>This lesson clarifies opencode TUI's app structure—that pyramid built of twenty-some Provider layers, each with its own role yet dependency-clear:</p>
  <ul>
    <li><strong>Provider pyramid = structured dependency injection</strong> (<span class="mono">app.tsx</span>): twenty-some Providers nest outer-to-inner, <strong>each owning one thing</strong> (SDK connection/Project/Sync·Data data/Theme/Route/Dialog…). A component's available services = the union of all Providers above it.</li>
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
      <span class="kw">if</span> (!value) <span class="kw">throw new</span> <span class="fn">Error</span>(<span class="st">`${input.name} context must be used within a context provider`</span>)  <span class="cm">// ← fail fast</span>
      <span class="kw">return</span> value
    },
  }
}</pre>
  <p>These dozen lines' value far exceeds their length. They <strong>converge to one place</strong> a boilerplate that in a SolidJS/React project <strong>would be repeated dozens of times</strong> (<span class="mono">createContext</span> → write a Provider component → write a <span class="mono">useContext</span> + null-check hook), so adding a context needs only the one line <span class="mono">createSimpleContext({ name, init })</span>. That itself is a model of "don't repeat yourself." But the deeper cleverness: <strong>it makes "the correct usage" the only easy road</strong>. Because <span class="mono">use()</span> already handles "null-check + error" for you, no one will, to save effort, write a fragile "no-check, return directly" version; because the provider already standardizes the <span class="mono">ready</span> gate, async readiness has a standard posture too. <strong>Solidifying a set of good practices (fail fast, readiness gate, consistent naming) into a little tool everyone reaches for is far more effective than writing a 'please remember to null-check' guideline doc</strong>—a good abstraction doesn't constrain people with docs but makes the right thing the least-effort thing. This also echoes a recurring book theme: stamping a class of things into the same shape with a uniform little mold (L36's Tool.make, L47's PluginV2.define) makes the whole system, by "same shape everywhere," easy to read, easy to extend, hard to get wrong.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>Provider pyramid = structured dependency injection</strong> (<span class="mono">app.tsx</span>): twenty-some Providers nested, each owning one thing; a component's available services = the union of all Providers above it, grab precisely what's wanted via <span class="mono">useXxx()</span>.</li>
    <li><strong>nesting order = dependency topology</strong>: an inner init uses an outer context (<span class="mono">ProjectProvider</span> calls <span class="mono">useSDK()</span>→SDK must be outside). The tower bottom-to-top more fundamental more outer: connection(SDK)→project→data(Sync/Data)→theme→interaction(Dialog…)→<span class="mono">&lt;App/&gt;</span>.</li>
    <li><strong>the same mold createSimpleContext</strong> (<span class="mono">helper.tsx</span>): one line packs "build context+provider(init, <span class="mono">ready</span> gate)+use()." Every context same-shaped—like L36 Tool.make, L47 PluginV2.define "uniform mold stamps same shape."</li>
    <li><strong>use() fails fast</strong>: <span class="mono">if(!value) throw</span> "must be used within a context provider"—moving the hidden bug of "use context outside Provider→undefined→crash afar" forward to an on-the-spot named error (like L37/L48 fail fast).</li>
    <li><strong>single responsibility vs god object</strong>: each cell of state exclusively owned by one Provider, ownership clear, independently readable/testable/replaceable; paired with L52 fine-grained reactivity, a cleanly-bounded state cell is naturally the boundary of fine-grained updates—"split clean" is "update lean," the structural reason a complex TUI stays orderly. This Provider+use pattern is universal in any React/SolidJS project.</li>
  </ul>
</div>
""",
}
LESSON_54 = {
    "zh": r"""
<p class="lead">上一课我们看清了 Provider 金字塔，也注意到其中 <span class="mono">Sync</span>/<span class="mono">Data</span> 两层专管「把事件变成状态」。这一课就钻进这条<strong>数据流</strong>：服务器源源不断推来的事件，是怎么变成那个驱动整个界面的<strong>响应式 store</strong> 的。这是理解 opencode TUI <strong>为什么是「活的」</strong>的关键——你看到对话流里新消息一个字一个字地冒出来、工具调用的状态实时翻转、待办项打勾，背后都是这条「事件→store→重渲染」的流水在飞速运转。但这里藏着一个魔鬼细节：当 agent 全速流式输出时，事件会像<strong>消防水龙头</strong>一样喷涌而来——若每来一个事件就重画一次屏幕，界面会卡成幻灯片。opencode 怎么让界面在事件洪流下依然丝般顺滑？答案是一记精巧的 <strong>16ms 批处理</strong>。</p>
<p>这一课有两个层层递进的洞见。第一，<strong>TUI 的状态是「事件溯源」出来的</strong>：它不是「拉一份数据、整个替换」，而是<strong>订阅服务器的事件流</strong>，再用一个 <span class="mono">switch(event.type)</span> 的 <strong>reducer</strong> 把每个事件<strong>归约</strong>进本地的响应式 store——store 是这条事件流的一份<strong>投影</strong>。这和你熟悉的 Redux「action→reducer→state」是同一个心智，只不过 action 来自服务器、state 是 SolidJS 的细粒度 store。第二，<strong>16ms 的「批处理 + 低延迟」双策略</strong>：所有在约 16ms（一个 60fps 帧）窗口内涌到的事件，会被<strong>攒成一批</strong>、在一次 SolidJS <span class="mono">batch()</span> 里统一应用——于是「一串事件」只触发<strong>一次重渲染</strong>；但若此刻很闲（距上次刷新超过 16ms），则<strong>立刻处理</strong>不攒，保证低延迟。读懂这两点，你就懂了「为什么 opencode 的终端界面，能在 agent 狂吐 token 的洪流里，依然每秒只稳稳地重画几十帧、既不卡也不闪」。</p>

<div class="card analogy">
  <div class="tag">📊 生活类比</div>
  把那个响应式 store 想象成体育馆里的<strong>实时记分牌</strong>。场上的每一个动作——进球、犯规、换人——都是一条<strong>「事件」</strong>，通过广播流不断报进来；记分牌后台有个小工（<strong>reducer</strong>），听到「主队进球」就给主队 +1、听到「换人」就改阵容表——<strong>每条事件只精准改动记分牌的相关那一格</strong>，而非把整块牌子擦了重写。但问题来了：比赛精彩时，进球、助攻、数据更新可能在一两秒内<strong>连珠炮般砸来十几条</strong>。如果每来一条就把记分牌<strong>刷新一遍</strong>，整块牌子会闪得让人眼花。聪明的做法是：给记分牌定一个<strong>「最小刷新间隔」</strong>（比如每 16 毫秒最多刷一次）——这一小段时间内攒下的所有更新，<strong>合并成一次</strong>刷上去。于是哪怕事件像洪水，观众看到的记分牌始终是<strong>稳定、流畅、不闪</strong>的。这正是 opencode TUI 处理事件洪流的办法。
</div>

<h2>事件 → reducer → store：UI 状态的事件溯源</h2>
<p>opencode 的 TUI 不会傻乎乎地「每隔一秒拉一次最新状态」。它做的是<strong>订阅</strong>：<span class="mono">SDKProvider</span> 通过 SSE（Server-Sent Events）连上服务器的事件流，服务器一有动静（新消息、工具状态变化、权限请求……）就<strong>主动推</strong>一个事件过来。而把这些事件<strong>变成状态</strong>的，是 <span class="mono">sync.tsx</span> 里那个巨大的 reducer——一个 <span class="mono">switch(event.type)</span>，针对每种事件类型，做一次精准的 store 更新：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">permission.asked</div><div class="c-txt"><span class="mono">setStore("permission", sessionID, [request])</span>——挂一个待批权限请求</div></div>
  <div class="cell"><div class="c-tag">todo.updated</div><div class="c-txt"><span class="mono">setStore("todo", sessionID, todos)</span>——替换该会话的待办列表</div></div>
  <div class="cell"><div class="c-tag">session.updated</div><div class="c-txt"><span class="mono">setStore("session", index, reconcile(info))</span>——就地更新某会话</div></div>
  <div class="cell"><div class="c-tag">session.status</div><div class="c-txt"><span class="mono">setStore("session_status", sessionID, status)</span>——刷新运行状态（如「思考中」）</div></div>
</div>
<p>这就是经典的「<strong>action → reducer → state</strong>」三段式，只不过 action 是服务器推来的事件、state 是 <span class="mono">sync.tsx</span> 用 <span class="mono">createStore</span> 建的那个<strong>响应式大 store</strong>（装着所有会话、消息、权限、待办、配置、provider……整个 App 的服务器侧状态）。整条流水串起来是这样：</p>
<div class="flow">
  <div class="f-node">服务器 SSE 事件<br><small>新消息/状态变化…</small></div>
  <div class="f-arrow">推送 →</div>
  <div class="f-node">事件队列<br><small>SDKProvider 收下</small></div>
  <div class="f-arrow">flush →</div>
  <div class="f-node">reducer 归约<br><small>switch(type)→setStore</small></div>
  <div class="f-arrow">更新 →</div>
  <div class="f-node">响应式 store→重渲染<br><small>只动相关组件(L52)</small></div>
</div>
<p>更新 store 时，reducer 用了两个 SolidJS 的利器：<span class="mono">produce</span> 和 <span class="mono">reconcile</span>。<span class="mono">produce</span> 让你像改普通对象一样在一个「草稿」上就地修改（immer 风格），SolidJS 会自动算出哪些路径变了；<span class="mono">reconcile</span> 则在用「一个新对象」替换 store 某处时，<strong>智能地只改真正不同的字段</strong>、而非整块替换——这对保持细粒度响应至关重要：若粗暴整块替换，会让一大片本没变的组件也被迫重渲染。reducer 里还藏着一个二分查找 <span class="mono">search</span>：会话等数组按 id 排好序存着，新事件来时用二分<strong>O(log n)</strong> 地「找到就更新、找不到就插入」，避免线性扫描。<strong>这些细节合起来，让「把一个事件吸收进庞大 store」这件事既精准又高效。</strong></p>

<h2>16ms 批处理：把事件洪流压成每帧一渲</h2>
<p>现在来到最精妙的一环。设想 agent 正在全速流式输出一段长回答：服务器会<strong>每吐几个字就推一个事件</strong>，一秒钟可能涌来上百个事件。如果<strong>每个事件都立刻触发一次重渲染</strong>，那就是一秒上百次重画——终端绘制本就昂贵（L52），这么搞界面必然卡成幻灯片、还疯狂闪烁。opencode 的解法藏在 <span class="mono">sdk.tsx</span> 的 <span class="mono">handleEvent</span> 里，逻辑只有几行，却拿捏得极准：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">每个事件先 <span class="mono">queue.push</span> 入队，不立刻处理</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">看距上次 flush 过了多久（<span class="mono">elapsed</span>）</span></div>
  <div class="t-row"><span class="t-num">3a</span><span class="t-txt"><span class="mono">elapsed &lt; 16ms</span>（刚刷过、正处于洪流）→ 设个 <span class="mono">setTimeout(flush, 16)</span>，把它和后续事件攒一起</span></div>
  <div class="t-row"><span class="t-num">3b</span><span class="t-txt"><span class="mono">elapsed ≥ 16ms</span>（很闲）→ <strong>立刻 flush</strong>，零延迟</span></div>
</div>
<p>而 <span class="mono">flush</span> 的关键，是把队列里所有事件的应用<strong>裹进一个 SolidJS <span class="mono">batch()</span></strong>：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">queue 攒批</div><div class="c-txt">16ms 窗口内涌来的事件全攒进一个队列，不逐个触发渲染</div></div>
  <div class="cell"><div class="c-tag">batch() 合一</div><div class="c-txt"><span class="mono">batch(() =&gt; 逐个 emit)</span>——一批事件的所有 store 更新合并成<strong>一次</strong>重渲染</div></div>
  <div class="cell"><div class="c-tag">闲时直发</div><div class="c-txt"><span class="mono">elapsed ≥ 16</span> 时立刻 flush——空闲时不引入任何延迟</div></div>
  <div class="cell"><div class="c-tag">16ms ≈ 一帧</div><div class="c-txt">60fps 下一帧约 16.7ms——这个窗口正好「每帧最多渲一次」</div></div>
</div>
<p>这个策略的精髓，是<strong>「负载下攒批、空闲时直发」的二者兼得</strong>。当事件稀疏（你刚敲完一句、等 agent 反应），第一个事件 <span class="mono">elapsed ≥ 16</span> 会被立刻处理，界面<strong>零延迟</strong>响应你；而一旦进入洪流（agent 狂吐 token），后续事件就被 16ms 的窗口<strong>不断收拢成一批批</strong>，每 16ms 才统一渲一次——把「一秒上百次重画」死死压到「一秒最多 60 次」。16ms 这个数字不是随便选的：它恰好是 60fps 下一帧的时长，意味着批处理的节奏<strong>正好踩在屏幕刷新的节拍上</strong>，多渲也是浪费。<strong>这一层「时间维度的批处理」，和 L52 那层「空间维度的细粒度更新」叠在一起，构成了 opencode TUI 流畅的双重保险</strong>：16ms 批处理保证「每帧最多渲一次」，细粒度响应式保证「每次渲只动该动的那几个字符格」。一纵一横，事件洪流再凶，落到终端上也只是平稳的每秒几十帧。</p>

<h2>全景：一个 token 从服务器到你眼前</h2>
<p>把前两节合起来，看一个流式 token 走完的完整旅程，就能看清这套设计如何层层把「洪流」驯服成「顺滑」。先看 16ms 窗口在时间轴上是怎么收拢事件的：</p>
<div class="timeline">
  <div class="tl-item"><div class="tl-time">t=0ms</div><div class="tl-text">空闲中来了第 1 个事件 → elapsed≥16 → 立刻 flush+渲染（零延迟）</div></div>
  <div class="tl-item"><div class="tl-time">t=2~15ms</div><div class="tl-text">洪流来了：事件 2/3/4…陆续涌到 → 全攒进 queue，排一个 16ms 后的 flush</div></div>
  <div class="tl-item"><div class="tl-time">t=16ms</div><div class="tl-text">flush：把这一窗口攒下的 N 个事件裹进一个 batch → 只渲染 1 次</div></div>
  <div class="tl-item"><div class="tl-time">t=16ms+</div><div class="tl-text">洪流继续 → 每 16ms 一批一渲，稳定 60fps；洪流停 → 下个事件又走零延迟分支</div></div>
</div>
<p>对比一下「没有 16ms 批处理」会怎样，这层防护的价值就一目了然：</p>
<div class="cols">
  <div class="col"><h4>朴素：每事件一渲（卡）</h4><p>agent 一秒吐 100 个 token=100 个事件=100 次重渲染。终端绘制昂贵，根本刷不过来，界面卡成幻灯片还疯狂闪烁——用户体验崩溃。</p></div>
  <div class="col"><h4>opencode：16ms 批处理（顺）</h4><p>100 个事件被 16ms 窗口收拢成约 6 批=最多 60 次渲染/秒。配合细粒度响应式，每次只刷变化的字符格——洪流下依然丝般顺滑。</p></div>
</div>
<p>所以一个流式 token 的完整旅程是：<strong>服务器算出这个 token → SSE 推一个事件 → SDKProvider 收进队列 → 16ms 窗口把它和同批伙伴攒在一起 → 一次 batch 里，reducer 把它们逐个归约进 store（store 里对应那条消息的文本 +N 个字）→ store 变更只通知依赖它的那个 <span class="mono">&lt;text&gt;</span> 组件 → opentui 只重画屏幕上那几格字符。</strong>从「服务器的一个字节」到「你眼前多出来的一个字」，中间隔着<strong>事件流、队列、批处理、reducer、响应式 store、细粒度渲染</strong>这一整条精心设计的流水——而它们协同的唯一目的，就是让你在终端里看到的对话，<strong>像在最丝滑的网页里一样自然地流淌</strong>。这条从字节到字符的旅程，正是 opencode 把「服务器的事件世界」和「你眼前的终端界面」缝合起来的那根线。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观视角</div>
  <p>这一课讲清了 opencode TUI 的数据流——服务器事件如何变成驱动界面的响应式状态：</p>
  <ul>
    <li><strong>事件溯源的 UI 状态</strong>：TUI 不「拉取替换」，而是 <span class="mono">SDKProvider</span> 经 SSE 订阅服务器事件流，再用 <span class="mono">sync.tsx</span> 的 <span class="mono">switch(event.type)</span> reducer 把每个事件归约进 <span class="mono">createStore</span> 建的响应式大 store（会话/消息/权限/待办/配置…）。store=事件流的投影。同 Redux「action→reducer→state」，action 来自服务器。</li>
    <li><strong>reducer 的两大利器</strong>：<span class="mono">produce</span>（immer 风草稿就地改、自动算变更路径）+ <span class="mono">reconcile</span>（替换时只改真正不同的字段、保细粒度）；数组按 id 排序 + 二分 <span class="mono">search</span> O(log n) 找到即更新/找不到即插入。</li>
    <li><strong>16ms 批处理</strong>（<span class="mono">sdk.tsx</span> handleEvent/flush）：事件入队；<span class="mono">elapsed&lt;16ms</span>（洪流中）→ <span class="mono">setTimeout(flush,16)</span> 攒批，<span class="mono">≥16ms</span>（空闲）→ 立刻 flush。flush 把整批事件裹进 <span class="mono">batch()</span>→一批事件只触发一次重渲染。16ms≈60fps 一帧。</li>
    <li><strong>流畅的双重保险</strong>：16ms 批处理（时间维：每帧最多渲一次）× L52 细粒度响应式（空间维：每次只动该动的字符格）=事件洪流下仍平稳每秒几十帧、不卡不闪。「负载下攒批、空闲时直发」二者兼得。</li>
  </ul>
  <p>数据流看清了——事件经 reducer 归约进 store、16ms 批处理把洪流压成每帧一渲、细粒度响应式只重画变化处。至此你已掌握 opencode TUI 的「骨架（L53 Provider 金字塔）+ 血液（L54 事件数据流）+ 画笔（L52 opentui）」。接下来两课转向具体的<strong>界面组件</strong>：L55 讲那个你天天敲字的 <strong>prompt 编辑器</strong>（自动补全、历史、frecency 常用度排序），L56 讲<strong>对话框、命令面板</strong>与 run CLI 的 scrollback。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p><span class="mono">sdk.tsx</span> 的 <span class="mono">handleEvent</span>+<span class="mono">flush</span>，把「攒批 vs 直发」的取舍写得极简（简化自源码）：</p>
  <pre class="code"><span class="kw">const</span> flush = () =&gt; {
  <span class="kw">if</span> (queue.length === <span class="nu">0</span>) <span class="kw">return</span>
  <span class="kw">const</span> events = queue; queue = []; timer = undefined; last = Date.<span class="fn">now</span>()
  <span class="cm">// 把一批事件的所有 emit 裹进一个 batch → 只触发一次渲染</span>
  <span class="fn">batch</span>(() =&gt; { <span class="kw">for</span> (<span class="kw">const</span> event <span class="kw">of</span> events) emitter.<span class="fn">emit</span>(<span class="st">"event"</span>, event) })
}

<span class="kw">const</span> handleEvent = (event) =&gt; {
  queue.<span class="fn">push</span>(event)
  <span class="kw">const</span> elapsed = Date.<span class="fn">now</span>() - last
  <span class="kw">if</span> (timer) <span class="kw">return</span>                    <span class="cm">// 已排了一次 flush，等它</span>
  <span class="kw">if</span> (elapsed &lt; <span class="nu">16</span>) {                  <span class="cm">// 刚刷过、正处洪流</span>
    timer = <span class="fn">setTimeout</span>(flush, <span class="nu">16</span>)     <span class="cm">// ← 攒批，下一帧再统一刷</span>
    <span class="kw">return</span>
  }
  <span class="fn">flush</span>()                            <span class="cm">// ← 空闲：立刻处理，零延迟</span>
}</pre>
  <p>这段代码最值得品的，是它对<strong>「延迟」与「吞吐」这对天生矛盾</strong>的精巧平衡。一个朴素的实现往往只能二选一：要么「每个事件立刻处理」（延迟最低，但洪流下卡死），要么「固定每 16ms 才处理一次」（吞吐稳定，但空闲时也白白慢 16ms）。而这里用一个 <span class="mono">elapsed &lt; 16</span> 的判断<strong>把两种模式自动切换</strong>：闲的时候走「立刻」分支、忙的时候走「攒批」分支——<strong>系统自己根据负载在「低延迟」和「高吞吐」之间无缝滑动</strong>，无需任何手动调参。这种「自适应批处理」是高性能事件系统里一个极优雅的模式，它的精髓在于看清了一个洞察：<strong>用户对延迟的敏感，恰恰发生在事件稀疏时（你在等响应）；而高吞吐的需求，恰恰发生在事件密集时（你在看流式输出）。</strong>两种需求在时间上天然错开，于是一个简单的「最近是否刚忙过」判断，就能让系统永远站在当下最该站的那一边。读懂这一手，你会对「好的性能优化往往不是更复杂、而是更懂场景」有更深的体会。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>事件溯源的 UI 状态</strong>：TUI 经 SSE 订阅服务器事件流（非拉取替换），<span class="mono">sync.tsx</span> 的 <span class="mono">switch(event.type)</span> reducer 把每事件归约进 <span class="mono">createStore</span> 响应式大 store。store=事件流投影，同 Redux action→reducer→state（action 来自服务器）。</li>
    <li><strong>reducer 利器</strong>：<span class="mono">produce</span>（草稿就地改、自动算变更）+ <span class="mono">reconcile</span>（只改真正不同字段、保细粒度）；数组按 id 排序 + 二分 <span class="mono">search</span> O(log n) 找到即更新/找不到即插入。</li>
    <li><strong>16ms 批处理</strong>（<span class="mono">sdk.tsx</span>）：事件入队；<span class="mono">elapsed&lt;16</span>（洪流）→ <span class="mono">setTimeout(flush,16)</span> 攒批、<span class="mono">≥16</span>（空闲）→ 立刻 flush；flush 把整批裹进 <span class="mono">batch()</span>→一批事件只触发一次渲染。16ms≈60fps 一帧。</li>
    <li><strong>自适应批处理</strong>：<span class="mono">elapsed&lt;16</span> 一个判断在「低延迟（空闲立刻发）」与「高吞吐（洪流攒批）」间无缝自动切换——洞察=用户对延迟敏感发生在事件稀疏时、高吞吐需求发生在事件密集时，两者时间上天然错开。</li>
    <li><strong>流畅双重保险</strong>：16ms 批处理（时间维：每帧最多渲一次）× L52 细粒度响应式（空间维：每次只动该动的字符格）=事件洪流下仍平稳每秒几十帧、不卡不闪。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Last lesson we saw the Provider pyramid, noting its <span class="mono">Sync</span>/<span class="mono">Data</span> layers specifically manage "turning events into state." This lesson drills into this <strong>data flow</strong>: how the events the server pushes continuously become the <strong>reactive store</strong> that drives the whole interface. This is the key to understanding <strong>why opencode's TUI is "alive"</strong>—you see new messages appear character by character in the conversation stream, tool-call statuses flip in real time, todo items get checked, all powered by this "event→store→re-render" pipeline running at high speed. But here hides a devilish detail: when the agent streams output at full speed, events gush in like a <strong>fire hose</strong>—if every event triggered a screen redraw, the interface would stutter into a slideshow. How does opencode keep the interface silky-smooth under a flood of events? The answer is an exquisite <strong>16ms batch</strong>.</p>
<p>This lesson has two progressively deeper insights. First, <strong>the TUI's state is "event-sourced"</strong>: it doesn't "pull a copy of data and replace wholesale" but <strong>subscribes to the server's event stream</strong>, then uses a <span class="mono">switch(event.type)</span> <strong>reducer</strong> to <strong>reduce</strong> each event into a local reactive store—the store is a <strong>projection</strong> of this event stream. This is the same mental model as the Redux "action→reducer→state" you know, only the action comes from the server and the state is SolidJS's fine-grained store. Second, the <strong>16ms "batch + low-latency" dual strategy</strong>: all events arriving within a ~16ms (one 60fps frame) window get <strong>amassed into a batch</strong> and applied together in one SolidJS <span class="mono">batch()</span>—so "a string of events" triggers only <strong>one re-render</strong>; but if it's idle right now (more than 16ms since the last flush), it's <strong>processed immediately</strong> with no amassing, ensuring low latency. Grasp these two and you'll understand "why opencode's terminal interface, amid the flood of the agent spewing tokens, still steadily redraws only a few dozen frames per second—neither stuttering nor flickering."</p>

<div class="card analogy">
  <div class="tag">📊 Analogy</div>
  Picture that reactive store as a stadium's <strong>live scoreboard</strong>. Every action on the field—a goal, a foul, a substitution—is an <strong>"event"</strong>, reported continuously via a broadcast stream; behind the scoreboard sits a worker (the <strong>reducer</strong>) who, hearing "home team scores," adds +1 to the home side, hearing "substitution," updates the lineup—<strong>each event precisely changes only the relevant cell of the scoreboard</strong>, not wiping and rewriting the whole board. But here's the problem: when the game is exciting, goals, assists, stat updates may slam in <strong>a dozen in rapid fire</strong> within a second or two. If the scoreboard <strong>refreshed once per event</strong>, the whole board would flicker dizzyingly. The smart move: give the scoreboard a <strong>"minimum refresh interval"</strong> (say, at most once per 16 milliseconds)—all updates amassed in that little window <strong>merged into one</strong> refresh. So even if events flood, what spectators see is always a <strong>stable, fluid, flicker-free</strong> scoreboard. That's exactly how opencode's TUI handles the event flood.
</div>

<h2>Event → reducer → store: event-sourcing the UI state</h2>
<p>opencode's TUI doesn't foolishly "pull the latest state every second." It <strong>subscribes</strong>: <span class="mono">SDKProvider</span> connects to the server's event stream via SSE (Server-Sent Events), and the moment the server has news (new message, tool status change, permission request…) it <strong>actively pushes</strong> an event over. What <strong>turns these events into state</strong> is that giant reducer in <span class="mono">sync.tsx</span>—a <span class="mono">switch(event.type)</span> that, per event type, does one precise store update:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">permission.asked</div><div class="c-txt"><span class="mono">setStore("permission", sessionID, [request])</span>—hang a pending permission request</div></div>
  <div class="cell"><div class="c-tag">todo.updated</div><div class="c-txt"><span class="mono">setStore("todo", sessionID, todos)</span>—replace that session's todo list</div></div>
  <div class="cell"><div class="c-tag">session.updated</div><div class="c-txt"><span class="mono">setStore("session", index, reconcile(info))</span>—update some session in place</div></div>
  <div class="cell"><div class="c-tag">session.status</div><div class="c-txt"><span class="mono">setStore("session_status", sessionID, status)</span>—refresh run status (e.g. "thinking")</div></div>
</div>
<p>This is the classic "<strong>action → reducer → state</strong>" triad, only the action is an event pushed by the server and the state is that <strong>big reactive store</strong> <span class="mono">sync.tsx</span> builds with <span class="mono">createStore</span> (holding all sessions, messages, permissions, todos, config, providers… the whole App's server-side state). The whole pipeline strung together:</p>
<div class="flow">
  <div class="f-node">server SSE event<br><small>new message/status change…</small></div>
  <div class="f-arrow">push →</div>
  <div class="f-node">event queue<br><small>SDKProvider receives</small></div>
  <div class="f-arrow">flush →</div>
  <div class="f-node">reducer reduces<br><small>switch(type)→setStore</small></div>
  <div class="f-arrow">update →</div>
  <div class="f-node">reactive store→re-render<br><small>only related components(L52)</small></div>
</div>
<p>When updating the store, the reducer uses two SolidJS power tools: <span class="mono">produce</span> and <span class="mono">reconcile</span>. <span class="mono">produce</span> lets you modify a "draft" in place like an ordinary object (immer-style), and SolidJS auto-computes which paths changed; <span class="mono">reconcile</span>, when replacing some part of the store with "a new object," <strong>intelligently changes only the truly-different fields</strong> rather than replacing the whole block—crucial for keeping fine-grained reactivity: a crude whole-block replace would force a large swath of unchanged components to re-render too. The reducer also hides a binary search <span class="mono">search</span>: arrays like sessions are stored sorted by id, and when a new event comes a binary search <strong>O(log n)</strong> "finds-and-updates or inserts," avoiding a linear scan. <strong>These details together make "absorbing one event into the giant store" both precise and efficient.</strong></p>

<h2>16ms batching: squeezing the event flood to one render per frame</h2>
<p>Now the most exquisite part. Imagine the agent streaming a long answer at full speed: the server <strong>pushes an event every few characters</strong>, possibly a hundred events gushing in per second. If <strong>every event immediately triggered a re-render</strong>, that's a hundred redraws per second—terminal painting is already expensive (L52), and doing this the interface would inevitably stutter into a slideshow and flicker madly. opencode's solution hides in <span class="mono">sdk.tsx</span>'s <span class="mono">handleEvent</span>, a few lines of logic yet nailed precisely:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">each event first <span class="mono">queue.push</span>es into the queue, not processed immediately</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">check how long since the last flush (<span class="mono">elapsed</span>)</span></div>
  <div class="t-row"><span class="t-num">3a</span><span class="t-txt"><span class="mono">elapsed &lt; 16ms</span> (just flushed, in the flood) → set a <span class="mono">setTimeout(flush, 16)</span>, amass it with future events</span></div>
  <div class="t-row"><span class="t-num">3b</span><span class="t-txt"><span class="mono">elapsed ≥ 16ms</span> (idle) → <strong>flush immediately</strong>, zero latency</span></div>
</div>
<p>And <span class="mono">flush</span>'s key is wrapping the application of all queued events <strong>in one SolidJS <span class="mono">batch()</span></strong>:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">queue amasses</div><div class="c-txt">events gushing in within the 16ms window all amass into a queue, not triggering a render each</div></div>
  <div class="cell"><div class="c-tag">batch() merges</div><div class="c-txt"><span class="mono">batch(() =&gt; emit each)</span>—all a batch's store updates merge into <strong>one</strong> re-render</div></div>
  <div class="cell"><div class="c-tag">idle sends directly</div><div class="c-txt"><span class="mono">elapsed ≥ 16</span> flushes immediately—no latency introduced when idle</div></div>
  <div class="cell"><div class="c-tag">16ms ≈ one frame</div><div class="c-txt">at 60fps one frame is ~16.7ms—this window is exactly "at most one render per frame"</div></div>
</div>
<p>The essence of this strategy is <strong>having both "batch under load" and "send directly when idle."</strong> When events are sparse (you just typed a sentence, awaiting the agent's reaction), the first event with <span class="mono">elapsed ≥ 16</span> is processed immediately, the interface responds to you with <strong>zero latency</strong>; but once the flood begins (the agent spewing tokens), subsequent events are <strong>continuously gathered into batches</strong> by the 16ms window, rendering once per 16ms—pressing "a hundred redraws per second" firmly down to "at most 60 per second." The number 16ms isn't arbitrary: it's exactly one frame's duration at 60fps, meaning the batching's rhythm <strong>steps precisely on the beat of the screen refresh</strong>, rendering more would be waste. <strong>This layer of "temporal-dimension batching," stacked with L52's layer of "spatial-dimension fine-grained updates," forms the double insurance of opencode TUI's fluidity</strong>: 16ms batching guarantees "at most one render per frame," fine-grained reactivity guarantees "each render touches only the few character cells that should change." One vertical, one horizontal—however fierce the event flood, landing on the terminal it's just a steady few dozen frames per second.</p>

<h2>The full picture: a token's journey from server to your eyes</h2>
<p>Combining the prior two sections, watching a streaming token's complete journey shows how this design tames the "flood" into "smoothness" layer by layer. First see how the 16ms window gathers events along a timeline:</p>
<div class="timeline">
  <div class="tl-item"><div class="tl-time">t=0ms</div><div class="tl-text">in idle, event 1 arrives → elapsed≥16 → flush+render immediately (zero latency)</div></div>
  <div class="tl-item"><div class="tl-time">t=2~15ms</div><div class="tl-text">flood comes: events 2/3/4… gush in → all amass into queue, schedule a flush 16ms out</div></div>
  <div class="tl-item"><div class="tl-time">t=16ms</div><div class="tl-text">flush: wraps the N events amassed this window into one batch → renders only once</div></div>
  <div class="tl-item"><div class="tl-time">t=16ms+</div><div class="tl-text">flood continues → one batch one render per 16ms, steady 60fps; flood stops → the next event takes the zero-latency branch again</div></div>
</div>
<p>Compare what "without 16ms batching" would be like, and this layer's value is clear at a glance:</p>
<div class="cols">
  <div class="col"><h4>naive: one render per event (stutter)</h4><p>the agent spews 100 tokens/sec = 100 events = 100 re-renders. Terminal painting is expensive, can't keep up at all, the interface stutters into a slideshow and flickers madly—UX collapse.</p></div>
  <div class="col"><h4>opencode: 16ms batching (smooth)</h4><p>100 events gathered by the 16ms window into ~6 batches = at most 60 renders/sec. Paired with fine-grained reactivity, each render flushes only changed character cells—silky-smooth even under flood.</p></div>
</div>
<p>So a streaming token's complete journey is: <strong>the server computes this token → SSE pushes an event → SDKProvider receives it into the queue → the 16ms window amasses it with its batch-mates → in one batch, the reducer reduces them one by one into the store (the text of the corresponding message in the store +N characters) → the store change notifies only the one <span class="mono">&lt;text&gt;</span> component depending on it → opentui repaints only those few character cells on screen.</strong> From "a byte at the server" to "a character newly appearing before your eyes," in between sits this whole carefully-designed pipeline of <strong>event stream, queue, batching, reducer, reactive store, fine-grained rendering</strong>—and their sole shared purpose is to make the conversation you see in the terminal <strong>flow as naturally as in the silkiest web page</strong>. This journey from byte to character is exactly the thread by which opencode stitches "the server's event world" to "the terminal interface before your eyes."</p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>This lesson clarifies opencode TUI's data flow—how server events become the reactive state driving the interface:</p>
  <ul>
    <li><strong>event-sourced UI state</strong>: the TUI doesn't "pull-and-replace" but <span class="mono">SDKProvider</span> subscribes to the server event stream via SSE, then <span class="mono">sync.tsx</span>'s <span class="mono">switch(event.type)</span> reducer reduces each event into the reactive store built with <span class="mono">createStore</span> (sessions/messages/permissions/todos/config…). store = projection of the event stream. Like Redux "action→reducer→state," the action comes from the server.</li>
    <li><strong>the reducer's two power tools</strong>: <span class="mono">produce</span> (immer-style draft in-place edit, auto-computes changed paths) + <span class="mono">reconcile</span> (on replace, changes only truly-different fields, keeps fine-grained); arrays sorted by id + binary <span class="mono">search</span> O(log n) find-and-update or insert.</li>
    <li><strong>16ms batching</strong> (<span class="mono">sdk.tsx</span> handleEvent/flush): events queued; <span class="mono">elapsed&lt;16ms</span> (in flood) → <span class="mono">setTimeout(flush,16)</span> amass, <span class="mono">≥16ms</span> (idle) → flush immediately. flush wraps the whole batch in <span class="mono">batch()</span> → a batch of events triggers only one re-render. 16ms ≈ one 60fps frame.</li>
    <li><strong>double insurance of fluidity</strong>: 16ms batching (temporal: at most one render per frame) × L52 fine-grained reactivity (spatial: each render touches only the cells that should change) = steady few dozen fps under flood, no stutter no flicker. "Batch under load, send directly when idle"—both at once.</li>
  </ul>
  <p>The data flow is clear—events reduced into the store via the reducer, 16ms batching squeezing the flood to one render per frame, fine-grained reactivity repainting only changes. By here you've grasped opencode TUI's "skeleton (L53 Provider pyramid) + blood (L54 event data flow) + brush (L52 opentui)." The next two lessons turn to concrete <strong>interface components</strong>: L55 covers that <strong>prompt editor</strong> you type into daily (autocomplete, history, frecency sorting), L56 covers <strong>dialogs, the command palette</strong>, and the run CLI's scrollback.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p><span class="mono">sdk.tsx</span>'s <span class="mono">handleEvent</span>+<span class="mono">flush</span> writes the "amass vs send directly" trade-off minimally (simplified from source):</p>
  <pre class="code"><span class="kw">const</span> flush = () =&gt; {
  <span class="kw">if</span> (queue.length === <span class="nu">0</span>) <span class="kw">return</span>
  <span class="kw">const</span> events = queue; queue = []; timer = undefined; last = Date.<span class="fn">now</span>()
  <span class="cm">// wrap all emits of a batch in one batch → triggers only one render</span>
  <span class="fn">batch</span>(() =&gt; { <span class="kw">for</span> (<span class="kw">const</span> event <span class="kw">of</span> events) emitter.<span class="fn">emit</span>(<span class="st">"event"</span>, event) })
}

<span class="kw">const</span> handleEvent = (event) =&gt; {
  queue.<span class="fn">push</span>(event)
  <span class="kw">const</span> elapsed = Date.<span class="fn">now</span>() - last
  <span class="kw">if</span> (timer) <span class="kw">return</span>                    <span class="cm">// a flush already scheduled, wait for it</span>
  <span class="kw">if</span> (elapsed &lt; <span class="nu">16</span>) {                  <span class="cm">// just flushed, in the flood</span>
    timer = <span class="fn">setTimeout</span>(flush, <span class="nu">16</span>)     <span class="cm">// ← amass, flush together next frame</span>
    <span class="kw">return</span>
  }
  <span class="fn">flush</span>()                            <span class="cm">// ← idle: process immediately, zero latency</span>
}</pre>
  <p>What's most worth savoring here is its exquisite balance of <strong>"latency" and "throughput," a born contradiction</strong>. A naive implementation often can only pick one: either "process each event immediately" (lowest latency, but stutters under flood) or "process only once per fixed 16ms" (stable throughput, but needlessly 16ms slower when idle). Here a single <span class="mono">elapsed &lt; 16</span> check <strong>auto-switches between the two modes</strong>: when idle take the "immediate" branch, when busy take the "amass" branch—<strong>the system itself slides seamlessly between "low latency" and "high throughput" per load</strong>, with no manual tuning. This "adaptive batching" is an extremely elegant pattern in high-performance event systems, its essence being an insight: <strong>a user's sensitivity to latency happens exactly when events are sparse (you're awaiting a response); while the need for high throughput happens exactly when events are dense (you're watching streaming output).</strong> The two needs are naturally staggered in time, so a simple "was it busy recently" check lets the system always stand on the side it most should right now. Grasp this move and you'll feel more deeply that "good performance optimization is often not more complex but more attuned to the scenario."</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>event-sourced UI state</strong>: the TUI subscribes to the server event stream via SSE (not pull-and-replace), <span class="mono">sync.tsx</span>'s <span class="mono">switch(event.type)</span> reducer reduces each event into the <span class="mono">createStore</span> reactive store. store = projection of the event stream, like Redux action→reducer→state (action from the server).</li>
    <li><strong>reducer power tools</strong>: <span class="mono">produce</span> (draft in-place edit, auto-computes changes) + <span class="mono">reconcile</span> (changes only truly-different fields, keeps fine-grained); arrays sorted by id + binary <span class="mono">search</span> O(log n) find-and-update or insert.</li>
    <li><strong>16ms batching</strong> (<span class="mono">sdk.tsx</span>): events queued; <span class="mono">elapsed&lt;16</span> (flood) → <span class="mono">setTimeout(flush,16)</span> amass, <span class="mono">≥16</span> (idle) → flush immediately; flush wraps the whole batch in <span class="mono">batch()</span> → a batch of events triggers only one render. 16ms ≈ one 60fps frame.</li>
    <li><strong>adaptive batching</strong>: one <span class="mono">elapsed&lt;16</span> check seamlessly auto-switches between "low latency (idle sends immediately)" and "high throughput (flood amasses)"—the insight = a user's latency sensitivity happens when events are sparse, the throughput need when events are dense, the two naturally staggered in time.</li>
    <li><strong>double insurance of fluidity</strong>: 16ms batching (temporal: at most one render per frame) × L52 fine-grained reactivity (spatial: each render touches only the cells that should change) = steady few dozen fps under flood, no stutter no flicker.</li>
  </ul>
</div>
""",
}
LESSON_55 = {
    "zh": r"""
<p class="lead">前三课讲透了 TUI 的「机器」——opentui 渲染器（L52）、Provider 金字塔（L53）、事件数据流（L54）。这一课转向你<strong>每天接触最多的那个组件</strong>：<span class="mono">prompt</span> 编辑器——你敲字、发问、@文件、/命令的那个输入框。乍看它只是个文本框，但 opencode 给它塞进了四样让它「懂你」的本事：<strong>编辑器</strong>（多行输入 + 富内容：文本、@文件提及、@agent）、<strong>自动补全</strong>（敲 <span class="mono">@</span> 补文件、敲 <span class="mono">/</span> 补命令）、<strong>历史</strong>（↑↓ 翻出你刚发过的话）、以及最妙的 <strong>frecency</strong>（按你的使用习惯给文件排序，把你最可能想要的那个顶到最前）。这一课就拆开这四件套，看一个朴素的输入框如何被打磨成<strong>「越用越顺手」</strong>的高手工具。</p>
<p>这一课有两个最值得带走的亮点。第一，<strong>frecency 这个排序算法</strong>——它的名字是 <strong>frequency（频率）+ recency（最近度）</strong>的合成词，公式只有一行却极其精妙：<span class="mono">frequency / (1 + 距上次打开的天数)</span>。一个文件你开得越<strong>频繁</strong>、上次开得越<strong>近</strong>，分越高。正是它，让你敲 <span class="mono">@</span> 时，<strong>真正想要的那个文件浮到候选列表最前面</strong>——既不会被你三个月前点过一次的文件干扰，也不会让你天天用的核心文件沉底。第二，<strong>历史与 frecency 都用「追加式 JSONL 日志 + 定期压缩」来持久化</strong>：每次更新只往文件<strong>追加一行</strong>（O(1)、抗崩溃），超过上限或加载时再<strong>重写压缩、顺带自愈损坏</strong>。这个朴素的持久化范式，和 M9 的迁移日志、L54 的事件溯源遥相呼应——<strong>追加是廉价又安全的，整理留到不影响热路径的时候做</strong>。读懂这两点，你就懂了「为什么 opencode 的输入框用着用着，就好像越来越懂你想敲什么」。</p>

<div class="card analogy">
  <div class="tag">⌨️ 生活类比</div>
  把这个 prompt 编辑器想象成一个<strong>「会学习的命令行 + 智能键盘」</strong>的合体。它的<strong>历史</strong>就像 shell 里按 ↑ 翻出上一条命令——肌肉记忆般顺手。它的 <strong>frecency</strong>，则像你手机输入法推荐 emoji 的逻辑：不是简单按「用得最多」排（否则你半年前疯狂用过的某个表情会永远霸榜），也不是单纯按「最近用过」排（否则一个误触的表情会插到最前），而是<strong>把「常用」和「最近」揉成一个分数</strong>——你<strong>既常用、又刚用过</strong>的那几个，才会被顶到最顺手的位置。所以你打开一个文件、再敲 <span class="mono">@</span> 时，它就出现在候选第一个；你冷落一个文件几天，它就悄悄往下沉。<strong>这个输入框不是被动等你打字，而是在默默观察你的习惯、并据此把「你最可能想要的」一次次端到你面前</strong>——这正是「好工具越用越合手」的奥秘。
</div>

<h2>四件套：把文本框打磨成高手工具</h2>
<p>opencode 的 prompt 不是一个 <span class="mono">&lt;textarea&gt;</span> 就完事，而是<strong>四个协作的部件</strong>（都在 <span class="mono">component/prompt/</span> 与 <span class="mono">prompt/</span> 下）。先纵览它们各管一摊：</p>
<table class="t">
  <tr><th>部件</th><th>职责</th><th>关键</th></tr>
  <tr><td>编辑器（index.tsx）</td><td>多行输入 + 富内容</td><td><span class="mono">PromptInfo</span>={input, parts[]}；parts 可含文本/@文件/@agent；normal/shell 模式</td></tr>
  <tr><td>自动补全（autocomplete.tsx）</td><td>敲 @ 补文件、敲 / 补命令</td><td>触发→过滤→排序；<span class="mono">visible: false｜"@"｜"/"</span></td></tr>
  <tr><td>历史（history.tsx）</td><td>↑↓ 翻出发过的话</td><td><span class="mono">move(±1)</span> 导航、<span class="mono">append</span> 去重存；上限 50 条</td></tr>
  <tr><td>frecency（frecency.tsx）</td><td>按使用习惯给文件排序</td><td><span class="mono">freq/(1+天数)</span>；@补全靠它把常用文件顶前</td></tr>
</table>
<p>这四件套的分工很清楚：<strong>编辑器</strong>是承载你输入的画布，它存的不只是一串字符，而是一个结构化的 <span class="mono">PromptInfo</span>——里面除了纯文本 <span class="mono">input</span>，还有 <span class="mono">parts</span> 数组，记着你 @ 进来的文件、@ 上的 agent，甚至每个提及在原文里的位置。<strong>自动补全</strong>是输入时的助手：它盯着你敲的字符，一旦发现 <span class="mono">@</span> 或 <span class="mono">/</span> 这样的「触发符」（靠 <span class="mono">mentionTriggerIndex</span> 定位），就弹出候选列表。它的工作是一条「触发→过滤→排序」的小流水：</p>
<div class="flow">
  <div class="f-node">检测触发符<br><small>@文件 / /命令</small></div>
  <div class="f-arrow">过滤 →</div>
  <div class="f-node">按已敲文字筛<br><small>match 候选项</small></div>
  <div class="f-arrow">排序 →</div>
  <div class="f-node">frecency 排名<br><small>常用又最近的顶前</small></div>
  <div class="f-arrow">展示 →</div>
  <div class="f-node">候选浮层<br><small>选中即插入</small></div>
</div>
<p><strong>历史</strong>和 <strong>frecency</strong> 则是两种「记忆」：历史记得你<strong>说过什么</strong>（整条 prompt），frecency 记得你<strong>用过哪些文件、多频繁、多近</strong>。历史的导航就像 shell 里按 ↑↓：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">↑</span><span class="t-txt"><span class="mono">move(-1)</span>：index 往回退一格，取出更早的那条 prompt 填进输入框</span></div>
  <div class="t-row"><span class="t-num">↓</span><span class="t-txt"><span class="mono">move(+1)</span>：向「当前」方向前进一格，index=0 时回到空白的「当前」</span></div>
  <div class="t-row"><span class="t-num">发送</span><span class="t-txt"><span class="mono">append</span>：去重后入列（与上一条相同则不重复存），index 归 0</span></div>
</div>
<p>后面两节，我们重点拆历史与 frecency 这两种「记忆」——它们才是让输入框「懂你」的关键。</p>

<h2>frecency：把「常用」与「最近」揉成一个分数</h2>
<p>先看那个一行公式的核心（<span class="mono">frecency.tsx</span> 的 <span class="mono">calculateFrecency</span>）：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">frequency（分子）</div><div class="c-txt">这个文件被打开过几次——次数越多，基础分越高</div></div>
  <div class="cell"><div class="c-tag">(now − lastOpen)/86400000</div><div class="c-txt">距上次打开的<strong>天数</strong>（86400000=一天的毫秒数）</div></div>
  <div class="cell"><div class="c-tag">分母 1 + 天数</div><div class="c-txt">隔得越久、分母越大、分越被「衰减」；+1 防止刚开时除以零</div></div>
  <div class="cell"><div class="c-tag">分数 = freq /(1+天数)</div><div class="c-txt">又常用、又最近=高分；常用但很久没碰=被时间稀释</div></div>
</div>
<p>这个公式的妙处，在于它<strong>同时打败了两种朴素方案</strong>。如果<strong>只按频率排</strong>（开得多的在前），那你半年前因为某个原因疯狂打开过几十次的文件，会<strong>永远霸占榜首</strong>——哪怕你早就不碰它了。如果<strong>只按最近排</strong>（刚开的在前），那你<strong>误点一次</strong>的某个无关文件，会瞬间插到你天天用的核心文件前面。而 frecency 用「频率<strong>除以</strong>时间衰减」把两者揉到一起：一个文件哪怕历史频率很高，只要久不碰，分母 <span class="mono">(1+天数)</span> 就把它的分数<strong>慢慢拖低</strong>；而一个刚开的新文件，频率虽低但 <span class="mono">天数≈0</span>、分母≈1，能暂时靠前——但若你不再回头开它，它的分也很快随频率不再增长而被后来者超过。<strong>「频率给你长期偏好，最近度给你当下意图，相除让两者动态平衡」</strong>——这就是为什么你敲 <span class="mono">@</span> 时，列表顶端总是「你这阵子又常用、又刚碰过」的那几个文件。这个算法不是 opencode 的独创，而是 Firefox 地址栏、各种编辑器文件选择器背后<strong>同一个久经验证的排序智慧</strong>——一个值得你装进工具箱、随处可用的小而美的算法。三种排序方案的高下，并排一看便知：</p>
<div class="cols">
  <div class="col"><h4>纯频率 / 纯最近（各有硬伤）</h4><p><strong>纯频率</strong>：开得多的永远在前→半年前疯狂用过的文件霸榜，早不碰了也赖着不走。<strong>纯最近</strong>：刚开的在前→误点一次的无关文件瞬间插到核心文件前面。各偏一极。</p></div>
  <div class="col"><h4>frecency（动态平衡）</h4><p>频率 ÷ 时间衰减：历史频率再高，久不碰也被分母慢慢拖低；刚开的新文件能暂时靠前，但不持续就被超过。<strong>长期偏好 × 当下意图，相除自洽</strong>。</p></div>
</div>
<p>每次你打开一个文件，<span class="mono">updateFrecency</span> 就给它的 <span class="mono">frequency +1</span>、把 <span class="mono">lastOpen</span> 刷成当下。于是这个分数<strong>随你的行为持续演化</strong>，永远反映你「最近这阵子」的真实习惯。</p>

<h2>追加式日志：抗崩溃又自愈的持久化</h2>
<p>历史和 frecency 都得<strong>跨会话记住</strong>——你今天翻得到昨天发过的话、@ 得到上周常用的文件。它俩用了同一套朴素而稳健的持久化：<strong>追加式 JSONL 日志 + 定期压缩</strong>。存档是两个文件：<span class="mono">prompt-history.jsonl</span> 和 <span class="mono">frecency.jsonl</span>，每行一条 JSON 记录。其运作有三步：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">追加（热路径）</div><div class="c-txt">每次更新只 <span class="mono">appendText</span> 往文件<strong>追加一行</strong>——O(1)、不重写全文、即便崩了也只丢最后一行</div></div>
  <div class="cell"><div class="c-tag">压缩（冷路径）</div><div class="c-txt">超过上限（历史 50/frecency 1000）时 <span class="mono">writeText</span> 重写：去重、保留最新 N 条</div></div>
  <div class="cell"><div class="c-tag">自愈（加载时）</div><div class="c-txt">读取时跳过解析失败的坏行；若有有效行就重写一遍，<strong>顺手修复损坏、抹掉超额</strong></div></div>
</div>
<p>为什么不直接「每次都把整个列表重写一遍」？因为那样既慢（列表越长写得越久）、又<strong>不抗崩溃</strong>（重写到一半断电，整个文件可能损坏）。而「追加一行」永远是<strong>廉价且原子的</strong>——这正是数据库预写日志（WAL，L48 见过）、事件溯源（L54）背后的同一个道理：<strong>把高频的「记录」做成廉价的追加，把昂贵的「整理」推迟到低频、不影响体验的时刻</strong>（超限时或下次启动时）。<span class="mono">parseFrecency</span> 读日志时还很聪明：同一个文件可能在日志里出现多行（每次打开追加一次），它用 <span class="mono">reduce</span> 让<strong>后出现的覆盖先出现的</strong>，于是自然取到每个文件的最新状态——这又是 L41 权限、L44 配置那个 <span class="mono">findLast</span>「后者胜」的同款思路。<strong>一个看似不起眼的「记历史」需求，背后藏着一整套「追加—压缩—自愈、后者覆盖前者」的成熟工程范式</strong>，而它在 opencode 里被复用得如此自然，恰恰说明好的范式是跨场景通用的。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观视角</div>
  <p>这一课拆开了 opencode 的 prompt 编辑器——那个「越用越懂你」的输入框：</p>
  <ul>
    <li><strong>四件套</strong>（<span class="mono">component/prompt/</span>、<span class="mono">prompt/</span>）：编辑器（<span class="mono">PromptInfo</span>={input,parts[]}，富内容 @文件/@agent、normal/shell 模式）+ 自动补全（@补文件//补命令，<span class="mono">mentionTriggerIndex</span> 触发→过滤→排序）+ 历史（↑↓ <span class="mono">move(±1)</span>、<span class="mono">append</span> 去重，上限 50）+ frecency（按习惯排文件）。</li>
    <li><strong>frecency 算法</strong>（<span class="mono">frequency/(1+天数)</span>）：频率给长期偏好、最近度给当下意图、相除动态平衡——同时打败「纯频率（旧favorite霸榜）」与「纯最近（误点插队）」。@补全靠它把「又常用又刚碰」的文件顶前。Firefox 地址栏同款经典算法。</li>
    <li><strong>追加式 JSONL 持久化</strong>：历史/frecency 都存 <span class="mono">*.jsonl</span>，<strong>追加</strong>（O(1)抗崩溃，热路径）+ <strong>压缩</strong>（超限重写去重，冷路径）+ <strong>自愈</strong>（加载跳坏行、重写修复）。同 L48 WAL、L54 事件溯源「廉价追加、推迟整理」。</li>
    <li><strong>后者覆盖前者</strong>：<span class="mono">parseFrecency</span> 用 reduce 让日志里同路径后出现的覆盖先出现的，自然取最新——同 L41 权限/L44 配置 <span class="mono">findLast</span>「后者胜」。</li>
  </ul>
  <p>输入框拆完了——四件套协作、frecency 排序、追加式日志记忆。M10 还剩最后一课 L56：<strong>对话框、命令面板</strong>（那些弹出来让你选模型、切 agent、跑命令的浮层）<strong>与 run CLI 的 scrollback</strong>（<span class="mono">opencode run</span> 非交互模式下，把对话以滚动日志形式打印出来）。讲完 L56，整个 M10「TUI 与客户端渲染」就收官，opencode 那套从渲染器到具体组件的终端 UI 全貌也就完整了。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p><span class="mono">frecency.tsx</span> 的核心就这么几行，把「频率 × 时间衰减」写得朴素而精确（简化自源码）：</p>
  <pre class="code"><span class="cm">// 一天的毫秒数</span>
<span class="kw">const</span> DAY = <span class="nu">86400000</span>

<span class="kw">function</span> <span class="fn">calculateFrecency</span>(entry) {
  <span class="kw">if</span> (!entry) <span class="kw">return</span> <span class="nu">0</span>
  <span class="cm">// 频率 ÷ (1 + 距上次打开的天数) ——越久没碰、分母越大、分越低</span>
  <span class="kw">return</span> entry.frequency / (<span class="nu">1</span> + (Date.<span class="fn">now</span>() - entry.lastOpen) / DAY)
}

<span class="kw">function</span> <span class="fn">updateFrecency</span>(filePath) {
  <span class="kw">const</span> abs = path.<span class="fn">resolve</span>(cwd, filePath)
  <span class="cm">// 打开一次：频率 +1，最近度刷成当下</span>
  <span class="kw">const</span> entry = { frequency: (store.data[abs]?.frequency || <span class="nu">0</span>) + <span class="nu">1</span>, lastOpen: Date.<span class="fn">now</span>() }
  <span class="fn">setStore</span>(<span class="st">"data"</span>, abs, entry)
  <span class="fn">appendText</span>(frecencyPath, JSON.<span class="fn">stringify</span>({ path: abs, ...entry }) + <span class="st">"\n"</span>)  <span class="cm">// ← 只追加一行</span>
}</pre>
  <p>最值得品的，是这个设计如何用<strong>一个极简的数学式</strong>，优雅地表达了一个本来很「主观」的需求——「把我最可能想要的文件排前面」。「我最可能想要什么」听起来像要靠机器学习、要建用户画像的复杂问题，但 frecency 用一行除法就给出了一个<strong>足够好</strong>的答案：你的<strong>长期偏好</strong>（频率）和<strong>当下意图</strong>（最近度）本就是预测「你想要什么」的两个最强信号，而「频率 ÷ 时间」恰好让它们以一种<strong>会自动新陈代谢</strong>的方式融合——新习惯随你的打开行为不断累积上分，旧习惯随时间流逝自动褪色。<strong>不需要任何显式的「过期」「清理」逻辑，时间衰减让排序永远自动跟着你「最近这阵子」的真实状态走。</strong>这是一个绝佳的范例，说明<strong>很多看似需要「智能」的产品体验，其实一个想透了的简单公式就能漂亮地解决</strong>——关键不在算法多复杂，而在你是否看清了「真正该度量的是什么」。把它装进你的工具箱：任何「最近常用项排序」的需求，frecency 都是第一个该想到的答案。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>prompt 四件套</strong>（<span class="mono">component/prompt/</span>、<span class="mono">prompt/</span>）：编辑器（<span class="mono">PromptInfo</span>={input,parts[]}，富内容 @文件/@agent、normal/shell）+ 自动补全（@///触发→过滤→排序）+ 历史（↑↓ <span class="mono">move</span>、<span class="mono">append</span> 去重、上限 50）+ frecency（按习惯排文件）。把朴素文本框打磨成「越用越顺手」的高手工具。</li>
    <li><strong>frecency=frequency+recency</strong>：<span class="mono">freq/(1+天数)</span>。频率给长期偏好、最近度给当下意图、相除动态平衡——同时打败纯频率（旧 favorite 霸榜）与纯最近（误点插队）。@补全靠它把「又常用又刚碰」的文件顶前。Firefox 地址栏同款经典算法。</li>
    <li><strong>时间衰减自动新陈代谢</strong>：<span class="mono">updateFrecency</span> 每次打开 frequency+1、lastOpen 刷新；分母 (1+天数) 让久不碰的自动褪色——无需显式「过期/清理」，排序永远跟着你最近的真实习惯走。</li>
    <li><strong>追加式 JSONL 持久化</strong>：历史/frecency 存 <span class="mono">*.jsonl</span>，追加（O(1) 抗崩溃，热路径）+ 压缩（超限重写去重，冷路径）+ 自愈（加载跳坏行、重写修复）。同 L48 WAL、L54 事件溯源「廉价追加、推迟整理」。</li>
    <li><strong>后者覆盖前者</strong>：<span class="mono">parseFrecency</span> 用 reduce 让同路径后出现的覆盖先出现的→自然取最新——同 L41 权限/L44 配置 <span class="mono">findLast</span>「后者胜」。简单公式漂亮解决看似需要「智能」的体验。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">The prior three lessons covered the TUI's "machinery"—the opentui renderer (L52), the Provider pyramid (L53), the event data flow (L54). This lesson turns to the component <strong>you touch most every day</strong>: the <span class="mono">prompt</span> editor—the input box where you type, ask, @ files, / commands. At first glance it's just a text box, but opencode packs four "understand-you" talents into it: an <strong>editor</strong> (multi-line input + rich content: text, @file mentions, @agent), <strong>autocomplete</strong> (type <span class="mono">@</span> for files, <span class="mono">/</span> for commands), <strong>history</strong> (↑↓ to recall what you just sent), and the cleverest, <strong>frecency</strong> (ranking files by your usage habits, floating the one you're most likely to want to the very top). This lesson disassembles these four pieces to see how a plain input box is polished into a power tool that <strong>"gets handier the more you use it."</strong></p>
<p>This lesson has two highlights most worth taking away. First, <strong>the frecency ranking algorithm</strong>—its name is a portmanteau of <strong>frequency + recency</strong>, its formula one line yet exquisite: <span class="mono">frequency / (1 + days since last open)</span>. The more <strong>frequently</strong> you open a file and the more <strong>recently</strong> you opened it, the higher its score. It's exactly what makes the file you <strong>actually want float to the top of the candidate list</strong> when you type <span class="mono">@</span>—neither disturbed by a file you clicked once three months ago, nor letting the core file you use daily sink to the bottom. Second, <strong>both history and frecency persist via "append-only JSONL log + periodic compaction"</strong>: each update only <strong>appends one line</strong> to the file (O(1), crash-safe), and on exceeding a cap or on load it <strong>rewrites to compact, healing corruption along the way</strong>. This plain persistence paradigm echoes M9's migration journals and L54's event sourcing—<strong>appending is cheap and safe, tidying is left for moments that don't affect the hot path</strong>. Grasp these two and you'll understand "why opencode's input box, the more you use it, seems to increasingly know what you want to type."</p>

<div class="card analogy">
  <div class="tag">⌨️ Analogy</div>
  Picture this prompt editor as a fusion of <strong>"a learning command line + a smart keyboard."</strong> Its <strong>history</strong> is like pressing ↑ in a shell to recall the last command—handy as muscle memory. Its <strong>frecency</strong> is like the logic by which your phone's keyboard recommends emoji: not simply by "used most" (else some emoji you frantically used half a year ago would forever top the list), nor purely by "used recently" (else one mis-tapped emoji jumps to the front), but by <strong>kneading "frequent" and "recent" into one score</strong>—the few you <strong>both use often and just used</strong> get floated to the handiest spot. So when you open a file then type <span class="mono">@</span>, it appears first in the candidates; neglect a file for a few days and it quietly sinks. <strong>This input box doesn't passively wait for you to type but silently observes your habits and, accordingly, repeatedly hands you "what you're most likely to want"</strong>—exactly the secret of "a good tool fits better the more you use it."
</div>

<h2>The four pieces: polishing a text box into a power tool</h2>
<p>opencode's prompt isn't done with a single <span class="mono">&lt;textarea&gt;</span> but is <strong>four collaborating parts</strong> (all under <span class="mono">component/prompt/</span> and <span class="mono">prompt/</span>). First an overview of what each manages:</p>
<table class="t">
  <tr><th>part</th><th>responsibility</th><th>key</th></tr>
  <tr><td>editor (index.tsx)</td><td>multi-line input + rich content</td><td><span class="mono">PromptInfo</span>={input, parts[]}; parts may hold text/@file/@agent; normal/shell modes</td></tr>
  <tr><td>autocomplete (autocomplete.tsx)</td><td>type @ for files, / for commands</td><td>trigger→filter→rank; <span class="mono">visible: false｜"@"｜"/"</span></td></tr>
  <tr><td>history (history.tsx)</td><td>↑↓ recall what you sent</td><td><span class="mono">move(±1)</span> navigate, <span class="mono">append</span> dedup-store; cap 50</td></tr>
  <tr><td>frecency (frecency.tsx)</td><td>rank files by usage habits</td><td><span class="mono">freq/(1+days)</span>; @complete relies on it to float frequent files up</td></tr>
</table>
<p>The four pieces' division is clear: the <strong>editor</strong> is the canvas bearing your input, storing not just a string of characters but a structured <span class="mono">PromptInfo</span>—besides the plain-text <span class="mono">input</span>, a <span class="mono">parts</span> array records files you @'d in, agents you @'d, even each mention's position in the original text. <strong>Autocomplete</strong> is the assistant while typing: it watches the characters you type, and once it spots a "trigger" like <span class="mono">@</span> or <span class="mono">/</span> (located via <span class="mono">mentionTriggerIndex</span>), pops a candidate list. Its work is a little "trigger→filter→rank" pipeline:</p>
<div class="flow">
  <div class="f-node">detect trigger<br><small>@file / /command</small></div>
  <div class="f-arrow">filter →</div>
  <div class="f-node">filter by typed text<br><small>match candidates</small></div>
  <div class="f-arrow">rank →</div>
  <div class="f-node">frecency ranking<br><small>frequent-and-recent on top</small></div>
  <div class="f-arrow">show →</div>
  <div class="f-node">candidate overlay<br><small>select to insert</small></div>
</div>
<p><strong>History</strong> and <strong>frecency</strong> are two kinds of "memory": history remembers <strong>what you said</strong> (whole prompts), frecency remembers <strong>which files you used, how often, how recently</strong>. History's navigation is like pressing ↑↓ in a shell:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">↑</span><span class="t-txt"><span class="mono">move(-1)</span>: index steps back, takes the earlier prompt into the input box</span></div>
  <div class="t-row"><span class="t-num">↓</span><span class="t-txt"><span class="mono">move(+1)</span>: walks forward, at index=0 returns to the blank "current"</span></div>
  <div class="t-row"><span class="t-num">send</span><span class="t-txt"><span class="mono">append</span>: enqueues after dedup (same as the last → not re-stored), index resets to 0</span></div>
</div>
<p>The next two sections focus on history and frecency, these two "memories"—they're the key to the input box "knowing you."</p>

<h2>frecency: kneading "frequent" and "recent" into one score</h2>
<p>First the core of that one-line formula (<span class="mono">frecency.tsx</span>'s <span class="mono">calculateFrecency</span>):</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">frequency (numerator)</div><div class="c-txt">how many times this file was opened—more times, higher base score</div></div>
  <div class="cell"><div class="c-tag">(now − lastOpen)/86400000</div><div class="c-txt">the <strong>days</strong> since last open (86400000 = ms in a day)</div></div>
  <div class="cell"><div class="c-tag">denominator 1 + days</div><div class="c-txt">the longer ago, the bigger the denominator, the more the score "decays"; +1 prevents divide-by-zero just after opening</div></div>
  <div class="cell"><div class="c-tag">score = freq /(1+days)</div><div class="c-txt">frequent and recent = high score; frequent but long untouched = diluted by time</div></div>
</div>
<p>This formula's beauty is that it <strong>defeats two naive schemes at once</strong>. If you <strong>rank by frequency only</strong> (most-opened first), a file you frantically opened dozens of times half a year ago for some reason would <strong>forever squat at the top</strong>—even if you stopped touching it long ago. If you <strong>rank by recency only</strong> (just-opened first), some irrelevant file you <strong>mis-clicked once</strong> would instantly jump ahead of the core file you use daily. frecency kneads both together via "frequency <strong>divided by</strong> time decay": however high a file's historical frequency, as long as it's untouched a while, the denominator <span class="mono">(1+days)</span> <strong>slowly drags its score down</strong>; while a just-opened new file, though low-frequency, has <span class="mono">days≈0</span> and denominator≈1, can rank up temporarily—but if you don't reopen it, its score is soon overtaken as its frequency stops growing. <strong>"Frequency gives you long-term preference, recency gives you present intent, division dynamically balances the two"</strong>—that's why, when you type <span class="mono">@</span>, the list's top is always the few files you've "lately both used often and just touched." This algorithm isn't opencode's invention but the <strong>same time-tested ranking wisdom</strong> behind Firefox's address bar and various editors' file pickers—a small, beautiful algorithm worth putting in your toolbox for use anywhere. The merits of the three ranking schemes, side by side, are clear at a glance:</p>
<div class="cols">
  <div class="col"><h4>pure frequency / pure recency (each flawed)</h4><p><strong>pure frequency</strong>: most-opened always first → a file frantically used half a year ago squats the top, clings on though long untouched. <strong>pure recency</strong>: just-opened first → an irrelevant file mis-clicked once instantly jumps ahead of core files. Each leans to an extreme.</p></div>
  <div class="col"><h4>frecency (dynamic balance)</h4><p>frequency ÷ time decay: however high the historical frequency, long untouched is slowly dragged down by the denominator; a just-opened new file can rank up temporarily but is overtaken if not sustained. <strong>Long-term preference × present intent, self-consistent by division</strong>.</p></div>
</div>
<p>Each time you open a file, <span class="mono">updateFrecency</span> gives its <span class="mono">frequency +1</span> and refreshes <span class="mono">lastOpen</span> to now. So this score <strong>continuously evolves with your behavior</strong>, always reflecting your "lately" real habits.</p>

<h2>Append-only log: crash-safe, self-healing persistence</h2>
<p>Both history and frecency must <strong>remember across sessions</strong>—you can recall yesterday's prompts today, @ last week's frequent files. They use the same plain, robust persistence: <strong>append-only JSONL log + periodic compaction</strong>. The archives are two files: <span class="mono">prompt-history.jsonl</span> and <span class="mono">frecency.jsonl</span>, one JSON record per line. Its operation has three steps:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">append (hot path)</div><div class="c-txt">each update only <span class="mono">appendText</span> <strong>appends one line</strong>—O(1), no full rewrite, even a crash loses only the last line</div></div>
  <div class="cell"><div class="c-tag">compact (cold path)</div><div class="c-txt">on exceeding a cap (history 50/frecency 1000) <span class="mono">writeText</span> rewrites: dedup, keep latest N</div></div>
  <div class="cell"><div class="c-tag">self-heal (on load)</div><div class="c-txt">on read skip lines that fail to parse; if valid lines exist rewrite once, <strong>healing corruption, trimming overflow</strong></div></div>
</div>
<p>Why not just "rewrite the whole list every time"? Because that's both slow (the longer the list, the longer the write) and <strong>not crash-safe</strong> (power cut mid-rewrite may corrupt the whole file). "Append one line" is always <strong>cheap and atomic</strong>—exactly the same principle behind a database's write-ahead log (WAL, seen in L48) and event sourcing (L54): <strong>make the high-frequency "record" a cheap append, defer the expensive "tidy" to a low-frequency, experience-free moment</strong> (on overflow or next startup). <span class="mono">parseFrecency</span> is clever when reading the log too: the same file may appear on multiple lines (one append per open), and it uses <span class="mono">reduce</span> to let <strong>later occurrences override earlier</strong>, naturally getting each file's latest state—again the same <span class="mono">findLast</span> "later wins" idea of L41 permissions and L44 config. <strong>A seemingly unremarkable "remember history" need hides a whole mature engineering paradigm of "append—compact—self-heal, later overrides earlier,"</strong> and that it's reused so naturally in opencode is exactly why good paradigms are cross-scenario universal.</p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>This lesson disassembled opencode's prompt editor—that "gets-to-know-you-as-you-use-it" input box:</p>
  <ul>
    <li><strong>four pieces</strong> (<span class="mono">component/prompt/</span>, <span class="mono">prompt/</span>): editor (<span class="mono">PromptInfo</span>={input,parts[]}, rich content @file/@agent, normal/shell modes) + autocomplete (@ for files / / for commands, <span class="mono">mentionTriggerIndex</span> trigger→filter→rank) + history (↑↓ <span class="mono">move(±1)</span>, <span class="mono">append</span> dedup, cap 50) + frecency (rank files by habit).</li>
    <li><strong>frecency algorithm</strong> (<span class="mono">frequency/(1+days)</span>): frequency gives long-term preference, recency gives present intent, division dynamically balances—defeating both "pure frequency (old favorite squats)" and "pure recency (mis-click jumps)" at once. @complete relies on it to float "frequent-and-just-touched" files up. The same classic algorithm as Firefox's address bar.</li>
    <li><strong>append-only JSONL persistence</strong>: history/frecency both store <span class="mono">*.jsonl</span>, <strong>append</strong> (O(1) crash-safe, hot path) + <strong>compact</strong> (rewrite-dedup on overflow, cold path) + <strong>self-heal</strong> (skip bad lines on load, rewrite to fix). Like L48 WAL, L54 event sourcing "cheap append, defer tidy."</li>
    <li><strong>later overrides earlier</strong>: <span class="mono">parseFrecency</span> uses reduce to let same-path later occurrences override earlier, naturally getting the latest—like L41 permission/L44 config <span class="mono">findLast</span> "later wins."</li>
  </ul>
  <p>The input box is disassembled—four pieces collaborating, frecency ranking, append-only log memory. M10 has one lesson left, L56: <strong>dialogs, the command palette</strong> (those overlays that pop up to let you pick a model, switch agents, run commands) <strong>and the run CLI's scrollback</strong> (in <span class="mono">opencode run</span> non-interactive mode, printing the conversation as a scrolling log). After L56, the whole M10 "TUI and client rendering" wraps up, and opencode's full picture of terminal UI from renderer to concrete components is complete.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p><span class="mono">frecency.tsx</span>'s core is just these few lines, writing "frequency × time decay" plainly and precisely (simplified from source):</p>
  <pre class="code"><span class="cm">// ms in a day</span>
<span class="kw">const</span> DAY = <span class="nu">86400000</span>

<span class="kw">function</span> <span class="fn">calculateFrecency</span>(entry) {
  <span class="kw">if</span> (!entry) <span class="kw">return</span> <span class="nu">0</span>
  <span class="cm">// frequency ÷ (1 + days since last open) — longer untouched, bigger denominator, lower score</span>
  <span class="kw">return</span> entry.frequency / (<span class="nu">1</span> + (Date.<span class="fn">now</span>() - entry.lastOpen) / DAY)
}

<span class="kw">function</span> <span class="fn">updateFrecency</span>(filePath) {
  <span class="kw">const</span> abs = path.<span class="fn">resolve</span>(cwd, filePath)
  <span class="cm">// one open: frequency +1, refresh recency to now</span>
  <span class="kw">const</span> entry = { frequency: (store.data[abs]?.frequency || <span class="nu">0</span>) + <span class="nu">1</span>, lastOpen: Date.<span class="fn">now</span>() }
  <span class="fn">setStore</span>(<span class="st">"data"</span>, abs, entry)
  <span class="fn">appendText</span>(frecencyPath, JSON.<span class="fn">stringify</span>({ path: abs, ...entry }) + <span class="st">"\n"</span>)  <span class="cm">// ← only append a line</span>
}</pre>
  <p>What's most worth savoring is how this design uses <strong>a minimal mathematical expression</strong> to elegantly express a need that's inherently "subjective"—"put the file I'm most likely to want up front." "What am I most likely to want" sounds like a complex problem needing machine learning and user profiling, but frecency gives a <strong>good-enough</strong> answer with one line of division: your <strong>long-term preference</strong> (frequency) and <strong>present intent</strong> (recency) are already the two strongest signals for predicting "what you want," and "frequency ÷ time" happens to fuse them in a <strong>self-metabolizing</strong> way—new habits keep scoring up with your opening behavior, old habits auto-fade with passing time. <strong>No explicit "expire" or "cleanup" logic needed; time decay keeps the ranking always automatically tracking your "lately" real state.</strong> This is a superb example that <strong>many product experiences seemingly needing "intelligence" can actually be beautifully solved by one well-thought-through simple formula</strong>—the key isn't how complex the algorithm but whether you've seen clearly "what should truly be measured." Put it in your toolbox: for any "rank recently-frequent items" need, frecency is the first answer to reach for.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>prompt's four pieces</strong> (<span class="mono">component/prompt/</span>, <span class="mono">prompt/</span>): editor (<span class="mono">PromptInfo</span>={input,parts[]}, rich content @file/@agent, normal/shell) + autocomplete (@///trigger→filter→rank) + history (↑↓ <span class="mono">move</span>, <span class="mono">append</span> dedup, cap 50) + frecency (rank files by habit). Polishes a plain text box into a "handier the more you use it" power tool.</li>
    <li><strong>frecency=frequency+recency</strong>: <span class="mono">freq/(1+days)</span>. frequency gives long-term preference, recency gives present intent, division dynamically balances—defeating pure frequency (old favorite squats) and pure recency (mis-click jumps) at once. @complete floats "frequent-and-just-touched" files up. Same classic algorithm as Firefox's address bar.</li>
    <li><strong>time decay auto-metabolizes</strong>: <span class="mono">updateFrecency</span> on each open frequency+1, refreshes lastOpen; the denominator (1+days) auto-fades the long-untouched—no explicit "expire/cleanup," the ranking always tracks your lately real habits.</li>
    <li><strong>append-only JSONL persistence</strong>: history/frecency store <span class="mono">*.jsonl</span>, append (O(1) crash-safe, hot path) + compact (rewrite-dedup on overflow, cold path) + self-heal (skip bad lines on load, rewrite to fix). Like L48 WAL, L54 event sourcing "cheap append, defer tidy."</li>
    <li><strong>later overrides earlier</strong>: <span class="mono">parseFrecency</span> uses reduce to let same-path later occurrences override earlier → naturally gets the latest—like L41 permission/L44 config <span class="mono">findLast</span> "later wins." A simple formula beautifully solves an experience seemingly needing "intelligence."</li>
  </ul>
</div>
""",
}
LESSON_56 = {
    "zh": r"""
<p class="lead">M10 一路讲来，我们已经把交互式 TUI 的渲染器（L52）、结构（L53）、数据流（L54）、prompt 编辑器（L55）都拆透了。这最后一课收两个尾：一是 TUI 里那批<strong>对话框与命令面板</strong>——你按下快捷键弹出来、用来选模型、切 agent、跑命令、挑主题的那些浮层；二是一个耐人寻味的对照：<span class="mono">opencode run</span> 这个<strong>非交互 CLI 模式</strong>下的 <strong>scrollback</strong>。同样一段对话，在交互式 TUI 里是一个可滚动、可点选、模态层叠的全屏应用；而在 <span class="mono">run</span> 模式下，它变成了一条<strong>线性追加、打印到 stdout 的滚动日志</strong>——能被管道接走、塞进脚本、喂给 CI。这一课最大的看点，正是这个对照背后的深意：<strong>同一份会话数据，可以被「渲染」成两种截然不同的界面。</strong></p>
<p>这一课有两个最值得带走的洞见。第一，<strong>对话框是一个「模态栈」</strong>：每开一个对话框就<strong>压栈</strong>，按 ESC 就<strong>弹出栈顶</strong>那一个——栈这个数据结构，恰好完美匹配「模态框还能再开模态框」的需求（比如选模型的对话框里再弹出选变体的对话框）。而那二十多个具体对话框（选模型、选 agent、选 MCP、选技能、选主题、列会话……）外加命令面板，<strong>几乎全建在同一个可复用的「<span class="mono">DialogSelect</span>（带过滤的选择框）」之上</strong>——又一次「统一模子刻同形」。第二，也是更深的一层：<strong>TUI 和 run scrollback 是同一份会话数据的两个「前端」</strong>。底层的 session、message（M9）是一份，怎么把它<strong>呈现</strong>给你——是做成一个交互式全屏应用，还是一条 pipe 友好的流式日志——是一个<strong>可替换的表现层</strong>。读懂这一点，你就懂了「为什么 opencode 既能给你一个漂亮的终端界面，又能在 <span class="mono">opencode run \"...\" | tee log.txt</span> 这种脚本场景里同样好用」。</p>

<div class="card analogy">
  <div class="tag">🃏 生活类比</div>
  把<strong>对话框</strong>想象成一叠<strong>可层叠的卡片</strong>：你每召唤一个对话框，就往桌上<strong>盖一张新卡</strong>在最上面（压栈）；你按 ESC，就<strong>掀掉最上面那张</strong>（弹栈），露出它下面的那张。这套「后进先出」的玩法，天然支持「从一张卡里再翻出一张卡」——选模型的卡上点开「变体」，又盖一张变体卡上去，挑完 ESC 掀掉、退回模型卡。而 <strong>TUI 与 run scrollback 的对照</strong>，则像同一场球赛的两种「看法」：交互式 TUI 是<strong>现场大屏直播</strong>——你能暂停、回看、点开数据面板、和它互动；run scrollback 则是赛后<strong>逐字打印的文字战报</strong>——它不互动，但能被你剪下来贴进报告、传给别人、存进档案。<strong>同一场比赛（同一份会话数据），既能做成沉浸的现场体验，也能做成朴素的文字记录——选哪种，取决于你此刻是想「亲临」还是想「留存与传递」。</strong>
</div>

<h2>对话框与命令面板：模态栈 + 一个可复用的选择框</h2>
<p>opencode 的对话框系统（<span class="mono">ui/dialog.tsx</span>）核心是一个 <strong>栈</strong>（<span class="mono">store.stack</span>）。它的运作简单而严谨：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">开 = 压栈</div><div class="c-txt">召唤一个对话框 → push 进 <span class="mono">stack</span>，渲染在最上层</div></div>
  <div class="cell"><div class="c-tag">栈非空 = 进入模态</div><div class="c-txt"><span class="mono">modeStack.push("modal")</span>——下层界面被「冻住」，键盘焦点归对话框</div></div>
  <div class="cell"><div class="c-tag">ESC = 弹栈顶</div><div class="c-txt"><span class="mono">stack.slice(0, -1)</span>——只关最上面那一个，露出下面的</div></div>
  <div class="cell"><div class="c-tag">可层叠</div><div class="c-txt">对话框里能再开对话框（选模型→选变体），栈天然支持嵌套</div></div>
</div>
<p>为什么用「栈」而不是「一个当前对话框」的变量？因为模态框的本质需求就是<strong>后进先出</strong>：你打开 A，又从 A 里打开 B，此刻该响应 ESC 的、该接收键盘的，<strong>永远是最新打开的那个 B</strong>；关掉 B，理应<strong>退回 A</strong> 而非直接全关。一个 <span class="mono">stack.at(-1)</span> 取栈顶、<span class="mono">slice(0,-1)</span> 弹栈顶，就把这套「层层进入、层层退出」的交互表达得干干净净。而真正<strong>填进这些对话框的内容</strong>，绝大多数是同一个零件：<span class="mono">DialogSelect</span>——一个「<strong>带搜索过滤的列表选择框</strong>」。看看它被复用了多少地方：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">选模型 / 变体 / Provider</div><div class="c-txt">dialog-model / variant / provider</div></div>
  <div class="cell"><div class="c-tag">选 agent / 技能 / MCP</div><div class="c-txt">dialog-agent / skill / mcp</div></div>
  <div class="cell"><div class="c-tag">列会话 / 选主题 / 工作区</div><div class="c-txt">dialog-session-list / theme-list / workspace-list</div></div>
  <div class="cell"><div class="c-tag">命令面板</div><div class="c-txt">command-palette——同样是 <span class="mono">DialogSelect</span>，列出所有命令</div></div>
</div>
<p>这里又见全书反复出现的智慧：<strong>把「从一个过滤列表里选一项」这个通用交互，做成一个零件 <span class="mono">DialogSelect</span>，二十多个对话框 + 命令面板大多从它生出来。</strong>于是「选模型」和「选主题」用着<strong>完全一致的搜索、上下键导航、回车确认</strong>体验——用户学一次、处处会用；开发者加一个新对话框，只需喂给 <span class="mono">DialogSelect</span> 一份选项列表即可。其中<strong>命令面板</strong>尤其点睛：它从 keymap 里 <span class="mono">getCommandEntries</span> 取出<strong>所有可见命令</strong>，连同它们的快捷键、分类、是否「建议」一起列成可搜索的列表，选中即 <span class="mono">dispatchCommand</span> 执行。它的流水是这样：</p>
<div class="flow">
  <div class="f-node">keymap.getCommandEntries<br><small>取所有命令</small></div>
  <div class="f-arrow">过滤 →</div>
  <div class="f-node">只留可见命令<br><small>+分类/建议标记</small></div>
  <div class="f-arrow">DialogSelect →</div>
  <div class="f-node">搜索 + 上下选<br><small>同款选择框</small></div>
  <div class="f-arrow">选中 →</div>
  <div class="f-node">dispatchCommand<br><small>执行该命令</small></div>
</div>
<p>它的意义是<strong>「可发现性」</strong>——你不必背下所有快捷键，敲开命令面板、搜个关键词，就能找到并执行任何命令。keymap 是命令的唯一真源，命令面板只是把它<strong>摊开成一张人能搜的清单</strong>。</p>

<h2>run scrollback：同一份数据的另一种「皮」</h2>
<p>现在来到那个耐人寻味的对照。<span class="mono">opencode run \"修复这个 bug\"</span> 不会弹出全屏 TUI，而是走<strong>非交互模式</strong>（<span class="mono">run.ts</span> 注释明说它有三种模式，默认这种「发一个 prompt、把事件流式打印到 stdout、会话空闲即退出」）。它把对话渲染成 <strong>scrollback</strong>——一条<strong>线性、只追加</strong>的滚动日志。<span class="mono">scrollback.surface.ts</span> 那套「保留式追加」机制，专管在内容还在流式到达时，把助手回复、推理、工具进度<strong>稳定地</strong>逐块打印出来（markdown 排版、代码高亮都不乱）。把它和交互式 TUI 并排，对照就格外清晰：</p>
<div class="cols">
  <div class="col"><h4>交互式 TUI</h4><p>全屏应用；可滚动回看、鼠标点选；<strong>模态对话框层叠</strong>、命令面板；键盘焦点、实时交互。给「<strong>亲自坐在终端前操作</strong>」的你。</p></div>
  <div class="col"><h4>run scrollback</h4><p>线性、只追加的日志，打印到 stdout；<strong>不交互</strong>，但能被<strong>管道接走</strong>（<span class="mono">| tee</span>、<span class="mono">&gt; log</span>）、塞进脚本与 CI；流式但排版稳定。给「<strong>自动化、留存、传递</strong>」的场景。</p></div>
</div>
<p>同一个 <span class="mono">opencode run</span>，其实还藏着三种模式（见 <span class="mono">run.ts</span>），把「交互程度」铺成一条光谱：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">非交互（默认）</div><div class="c-txt">发一个 prompt → 事件流式打印到 stdout → 会话空闲即退出。脚本/CI 友好</div></div>
  <div class="cell"><div class="c-tag">交互本地（--interactive）</div><div class="c-txt">启一个进程内服务器，跑「分屏 footer」直接模式，无需外部 HTTP</div></div>
  <div class="cell"><div class="c-tag">交互附着（--interactive --attach）</div><div class="c-txt">连上一个正在运行的 opencode 服务器，对它跑交互模式</div></div>
</div>
<p>从「一发即走」的纯管道，到「分屏直接模式」，再到完整 TUI——<strong>opencode 把同一颗 agent 内核，包进了粗细不同的好几层「皮」</strong>，让你按场景挑：写脚本就用非交互、想边看边插话就用交互、要沉浸操作就用完整 TUI。而这一切之所以可能，是因为下一节要点破的那个底层设计。</p>

<h2>数据与表现分离：一颗内核，多副面孔</h2>
<p>把前两节连起来，一个贯穿 opencode 架构的根本原则就浮出水面了：<strong>会话的「数据与逻辑」，和它的「呈现方式」，是彻底分开的两层。</strong>底层只有一份东西——存在 SQLite 里的 session、message、part（M9），由服务器的事件流（L54）实时驱动。而<strong>怎么把这份数据端到你面前，是一个可以整个替换的表现层</strong>：</p>
<div class="flow">
  <div class="f-node">一份会话数据<br><small>session/message (M9)</small></div>
  <div class="f-arrow">事件流 →</div>
  <div class="f-node">同一套内核逻辑<br><small>agent 循环/工具/协议</small></div>
  <div class="f-arrow">表现层分叉 →</div>
  <div class="f-node">交互式 TUI<br><small>全屏/模态/可滚</small></div>
  <div class="f-arrow">或 →</div>
  <div class="f-node">run scrollback<br><small>线性/追加/管道友好</small></div>
</div>
<p>这种分离的威力，正是 opencode 能「一鱼多吃」的根本：同一颗 agent 内核，既驱动了交互式 TUI（本部分 M10），也驱动了 run 的非交互日志，甚至——回想 L52 提过的——还能驱动浏览器里的 Web 应用、桌面端。<strong>因为「agent 在干什么」和「你怎么看它干」从一开始就被切成了两件事，每多一种「看法」，都不必重写那颗内核。</strong>这呼应了全书最深的一条主线：好的架构，反复在做的就是<strong>找到正确的接缝、把会变的和不变的切开</strong>——L47 把「核心编排」与「各家 provider」切开、L50 把「数据搬运」与「语义翻译」切开、L54 把「事件数据」与「渲染时机」切开，而这一课，把「<strong>agent 的会话</strong>」与「<strong>会话的呈现</strong>」切开。<strong>切口找得越准，系统就越能在不动根基的前提下，长出越来越多的可能。</strong>至此 M10 收官：你已经完整走过了 opencode 终端 UI 的全貌——从 opentui 渲染器，到 Provider 金字塔与事件数据流，到 prompt、对话框、命令面板，再到 run 这另一副面孔。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观视角</div>
  <p>这一课收束 M10——对话框、命令面板，以及 run scrollback 这个对照：</p>
  <ul>
    <li><strong>对话框 = 模态栈</strong>（<span class="mono">ui/dialog.tsx</span>）：开=push、ESC=弹栈顶（<span class="mono">slice(0,-1)</span>）、栈非空进 modal；栈天然支持「对话框里再开对话框」（后进先出，如选模型→选变体）。</li>
    <li><strong>DialogSelect 一个零件，处处复用</strong>：二十多个对话框（模型/agent/MCP/技能/主题/会话…）+ 命令面板大多建在「带过滤的选择框」上——一致的搜索/导航/确认体验，加新对话框只需喂一份选项。又见「统一模子刻同形」（同 L36/L47/L53）。</li>
    <li><strong>命令面板 = 可发现性</strong>（<span class="mono">command-palette.tsx</span>）：从 keymap <span class="mono">getCommandEntries</span> 取所有可见命令成可搜列表，选中 <span class="mono">dispatchCommand</span>。不必背快捷键，搜关键词即可执行。keymap 是唯一真源，面板只是摊开成清单。</li>
    <li><strong>run scrollback = 同数据另一副皮</strong>（<span class="mono">run/scrollback.surface.ts</span>）：<span class="mono">opencode run</span> 非交互模式把对话渲染成线性只追加、打印 stdout 的滚动日志（保留式追加保流式排版稳定），可管道/脚本/CI。三模式：非交互(默认)/交互本地/交互附着。</li>
  </ul>
  <p>根本原则：<strong>数据逻辑与呈现分离</strong>——一份 session/message（M9）+ 一套内核，驱动多副面孔（TUI / run / Web / 桌面）。每多一种「看法」不必重写内核，正是好架构「找准接缝、切开会变与不变」的又一例（呼应 L47/L50/L54）。M10「TUI 与客户端渲染」至此完整。下一部分 <strong>M11 转向扩展与集成</strong>：插件系统、LSP、格式化器、ACP/MCP——opencode 如何把自己向第三方与外部工具敞开。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p><span class="mono">ui/dialog.tsx</span> 把「模态栈」的开关写得朴素到位（简化自源码）：</p>
  <pre class="code"><span class="kw">const</span> [store, setStore] = <span class="fn">createStore</span>({ stack: [] })

<span class="cm">// 栈一非空，就进入「模态」模式：冻住下层、焦点归对话框</span>
<span class="fn">createEffect</span>(() =&gt; {
  <span class="kw">if</span> (store.stack.length === <span class="nu">0</span>) <span class="kw">return</span>
  <span class="kw">const</span> popMode = modeStack.<span class="fn">push</span>(<span class="st">"modal"</span>)
  <span class="fn">onCleanup</span>(popMode)                       <span class="cm">// 栈空了自动退出 modal</span>
})

<span class="cm">// ESC：只弹掉最上面那一个对话框</span>
keymap.<span class="fn">bind</span>(<span class="st">"escape"</span>, () =&gt; {
  <span class="kw">const</span> current = store.stack.<span class="fn">at</span>(-<span class="nu">1</span>)        <span class="cm">// 栈顶 = 最新打开的</span>
  current?.onClose?.()
  <span class="fn">setStore</span>(<span class="st">"stack"</span>, store.stack.<span class="fn">slice</span>(<span class="nu">0</span>, -<span class="nu">1</span>))  <span class="cm">// ← 弹栈顶，露出下面的</span>
})

<span class="cm">// 开一个对话框 = push 进栈（可在已有对话框之上再叠）</span>
<span class="kw">function</span> <span class="fn">open</span>(component) {
  <span class="fn">setStore</span>(<span class="st">"stack"</span>, [...store.stack, component])
}</pre>
  <p>这段代码最值得品的，是它如何用「栈」这一个最朴素的数据结构，<strong>精准命中了模态交互的本质</strong>。模态框的全部规矩——「最新打开的最优先」「ESC 只关最上面这层」「关掉一层退回上一层」「全关才解冻下层」——没有一条需要特判，全都<strong>自然地从「栈」的后进先出语义里长出来</strong>。<span class="mono">at(-1)</span> 就是「当前该响应谁」，<span class="mono">slice(0,-1)</span> 就是「退一层」，栈空就是「回到非模态」。这是「<strong>选对数据结构，逻辑就自己变简单</strong>」的教科书示范：如果你硬用「一个 currentDialog 变量 + 一堆 if 判断要不要恢复上一个」去做，立刻会陷入「上一个是谁、它的状态还在不在」的泥潭；而换成栈，那些纠结<strong>根本不会发生</strong>。<strong>把交互的「形状」映射到一个语义恰好吻合的数据结构上</strong>——模态用栈、有序覆盖用 findLast（L41/L44）、待办用队列——往往比任何精巧的控制流都更能从根上消除复杂度。下次你面对一个棘手的状态管理，不妨先问：有没有一个数据结构，它的天然语义正好就是我要的规矩？</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>对话框 = 模态栈</strong>（<span class="mono">ui/dialog.tsx</span>）：开=push、ESC=弹栈顶 <span class="mono">slice(0,-1)</span>、栈非空进 modal。栈的后进先出天然匹配「对话框里再开对话框、ESC 只关最上层、关掉退回上一层」——选对数据结构逻辑自简化。</li>
    <li><strong>DialogSelect 处处复用</strong>：二十多个对话框（模型/agent/MCP/技能/主题/会话…）+ 命令面板大多建在「带过滤选择框」上，一致体验、加新对话框只需喂选项。又见「统一模子刻同形」（L36/L47/L53）。</li>
    <li><strong>命令面板 = 可发现性</strong>（<span class="mono">command-palette.tsx</span>）：keymap <span class="mono">getCommandEntries</span> 取所有可见命令成可搜列表、选中 <span class="mono">dispatchCommand</span>。不必背快捷键。keymap 是唯一真源、面板只摊开成清单。</li>
    <li><strong>run scrollback = 同数据另一副皮</strong>（<span class="mono">run/scrollback.surface.ts</span>）：非交互模式把对话渲染成线性只追加、打印 stdout 的滚动日志，可管道/脚本/CI；三模式=非交互/交互本地/交互附着，把「交互程度」铺成光谱。</li>
    <li><strong>数据与表现分离</strong>：一份 session/message（M9）+ 一套内核 → 多副面孔（TUI/run/Web/桌面），每多一种「看法」不必重写内核。好架构「找准接缝、切开会变与不变」的又一例（呼应 L47/L50/L54）。M10 收官。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">All through M10 we've disassembled the interactive TUI's renderer (L52), structure (L53), data flow (L54), prompt editor (L55). This final lesson ties off two loose ends: one is the batch of <strong>dialogs and the command palette</strong> in the TUI—those overlays that pop up on a keypress to pick a model, switch agents, run commands, choose a theme; the other is an intriguing contrast: the <strong>scrollback</strong> in <span class="mono">opencode run</span>'s <strong>non-interactive CLI mode</strong>. The same conversation, in the interactive TUI, is a scrollable, clickable, modally-stacked full-screen app; while in <span class="mono">run</span> mode it becomes a <strong>linearly-appended scrolling log printed to stdout</strong>—pipeable, scriptable, CI-feedable. This lesson's biggest highlight is the deeper meaning behind this contrast: <strong>the same session data can be "rendered" into two wholly different interfaces.</strong></p>
<p>This lesson has two highlights most worth taking away. First, <strong>dialogs are a "modal stack"</strong>: opening a dialog <strong>pushes</strong>, pressing ESC <strong>pops the top</strong> one—the stack data structure perfectly matches the need "a modal can open another modal" (e.g. the model-picking dialog pops a variant-picking dialog). And those twenty-some concrete dialogs (pick model, pick agent, pick MCP, pick skill, pick theme, list sessions…) plus the command palette are <strong>nearly all built on the same reusable "<span class="mono">DialogSelect</span> (filtered select box)"</strong>—again "a uniform mold stamps the same shape." Second, and deeper: <strong>the TUI and run scrollback are two "front-ends" over the same session data</strong>. The underlying session, message (M9) are one copy; how to <strong>present</strong> it to you—as an interactive full-screen app or a pipe-friendly streaming log—is a <strong>replaceable presentation layer</strong>. Grasp this and you'll understand "why opencode gives you a pretty terminal interface yet is equally usable in a script scenario like <span class="mono">opencode run \"...\" | tee log.txt</span>."</p>

<div class="card analogy">
  <div class="tag">🃏 Analogy</div>
  Picture <strong>dialogs</strong> as a stack of <strong>stackable cards</strong>: each time you summon a dialog, you <strong>lay a new card</strong> on top of the pile (push); pressing ESC, you <strong>flip off the topmost</strong> (pop), revealing the one beneath. This "last-in-first-out" play naturally supports "flipping another card out of a card"—on the model-pick card open "variant," lay a variant card atop, choose then ESC flips it off, back to the model card. And the <strong>TUI vs run scrollback contrast</strong> is like two "viewings" of the same ball game: the interactive TUI is a <strong>live big-screen broadcast</strong>—you can pause, replay, open the stats panel, interact with it; run scrollback is the post-game <strong>verbatim printed report</strong>—it doesn't interact, but you can clip it into a report, send it to others, file it away. <strong>The same game (the same session data) can be an immersive live experience or a plain text record—which you pick depends on whether you want to "be there" or to "keep and pass on."</strong>
</div>

<h2>Dialogs and command palette: a modal stack + a reusable select box</h2>
<p>opencode's dialog system (<span class="mono">ui/dialog.tsx</span>) is at heart a <strong>stack</strong> (<span class="mono">store.stack</span>). Its operation is simple yet rigorous:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">open = push</div><div class="c-txt">summon a dialog → push into <span class="mono">stack</span>, rendered on top</div></div>
  <div class="cell"><div class="c-tag">stack non-empty = enter modal</div><div class="c-txt"><span class="mono">modeStack.push("modal")</span>—the layer below is "frozen," keyboard focus to the dialog</div></div>
  <div class="cell"><div class="c-tag">ESC = pop top</div><div class="c-txt"><span class="mono">stack.slice(0, -1)</span>—closes only the topmost, revealing the one below</div></div>
  <div class="cell"><div class="c-tag">stackable</div><div class="c-txt">a dialog can open a dialog (pick model→pick variant), the stack naturally supports nesting</div></div>
</div>
<p>Why a "stack" rather than a single "current dialog" variable? Because a modal's essential need is <strong>last-in-first-out</strong>: you open A, then open B from A, and right now what should respond to ESC, what should receive the keyboard, is <strong>always the newest-opened B</strong>; close B and you should <strong>fall back to A</strong>, not close everything. One <span class="mono">stack.at(-1)</span> takes the top, <span class="mono">slice(0,-1)</span> pops the top, expressing this "enter layer by layer, exit layer by layer" interaction cleanly. And what actually <strong>fills these dialogs</strong> is, for the vast majority, the same part: <span class="mono">DialogSelect</span>—a "<strong>search-filtered list select box</strong>." Look how many places reuse it:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">pick model / variant / provider</div><div class="c-txt">dialog-model / variant / provider</div></div>
  <div class="cell"><div class="c-tag">pick agent / skill / MCP</div><div class="c-txt">dialog-agent / skill / mcp</div></div>
  <div class="cell"><div class="c-tag">list sessions / pick theme / workspace</div><div class="c-txt">dialog-session-list / theme-list / workspace-list</div></div>
  <div class="cell"><div class="c-tag">command palette</div><div class="c-txt">command-palette—also a <span class="mono">DialogSelect</span>, listing all commands</div></div>
</div>
<p>Here's the wisdom recurring across the book again: <strong>making "pick one item from a filtered list," that generic interaction, into a part <span class="mono">DialogSelect</span>, from which most of the twenty-some dialogs + the command palette are born.</strong> So "pick model" and "pick theme" use a <strong>completely consistent search, up/down navigation, enter-to-confirm</strong> experience—the user learns once, uses everywhere; a developer adding a new dialog need only feed <span class="mono">DialogSelect</span> an options list. Among them the <strong>command palette</strong> is especially the eye-opener: it takes <strong>all visible commands</strong> from the keymap via <span class="mono">getCommandEntries</span>, listing them with their keybindings, categories, and "suggested" flag into a searchable list, dispatching the chosen one via <span class="mono">dispatchCommand</span>. Its pipeline:</p>
<div class="flow">
  <div class="f-node">keymap.getCommandEntries<br><small>take all commands</small></div>
  <div class="f-arrow">filter →</div>
  <div class="f-node">keep only visible<br><small>+category/suggested flags</small></div>
  <div class="f-arrow">DialogSelect →</div>
  <div class="f-node">search + up/down<br><small>the same select box</small></div>
  <div class="f-arrow">select →</div>
  <div class="f-node">dispatchCommand<br><small>run that command</small></div>
</div>
<p>Its significance is <strong>"discoverability"</strong>—you needn't memorize every keybinding; open the command palette, search a keyword, and you can find and run any command. The keymap is the single source of truth for commands, the palette just <strong>lays it out as a human-searchable list</strong>.</p>

<h2>run scrollback: another "skin" over the same data</h2>
<p>Now to that intriguing contrast. <span class="mono">opencode run \"fix this bug\"</span> won't pop a full-screen TUI but takes the <strong>non-interactive mode</strong> (<span class="mono">run.ts</span>'s comment explicitly says it has three modes, the default being this "send one prompt, stream events to stdout, exit when the session goes idle"). It renders the conversation as <strong>scrollback</strong>—a <strong>linear, append-only</strong> scrolling log. That "retained-append" machinery in <span class="mono">scrollback.surface.ts</span> specifically handles printing assistant replies, reasoning, tool progress <strong>stably</strong> block by block while content is still streaming in (markdown layout, code highlighting stay intact). Side by side with the interactive TUI, the contrast is especially clear:</p>
<div class="cols">
  <div class="col"><h4>interactive TUI</h4><p>full-screen app; scroll back, mouse-click; <strong>stacked modal dialogs</strong>, command palette; keyboard focus, real-time interaction. For you "<strong>sitting at the terminal operating in person</strong>."</p></div>
  <div class="col"><h4>run scrollback</h4><p>linear, append-only log printed to stdout; <strong>non-interactive</strong>, but pipeable (<span class="mono">| tee</span>, <span class="mono">&gt; log</span>), scriptable, CI-feedable; streaming yet stably laid out. For "<strong>automation, keeping, passing on</strong>" scenarios.</p></div>
</div>
<p>The same <span class="mono">opencode run</span> actually hides three modes (see <span class="mono">run.ts</span>), spreading "degree of interactivity" into a spectrum:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">non-interactive (default)</div><div class="c-txt">send one prompt → stream events to stdout → exit when session idle. Script/CI friendly</div></div>
  <div class="cell"><div class="c-tag">interactive local (--interactive)</div><div class="c-txt">spin up an in-process server, run "split-footer" direct mode, no external HTTP</div></div>
  <div class="cell"><div class="c-tag">interactive attach (--interactive --attach)</div><div class="c-txt">connect to a running opencode server, run interactive mode against it</div></div>
</div>
<p>From the pure-pipe "fire and exit," to "split-footer direct mode," to the full TUI—<strong>opencode wraps the same agent core in several "skins" of varying thickness</strong>, letting you pick by scenario: scripting takes non-interactive, watch-and-interject takes interactive, immersive operation takes the full TUI. And all this is possible because of the underlying design the next section spells out.</p>

<h2>Data and presentation separated: one core, many faces</h2>
<p>Connecting the prior two sections, a fundamental principle running through opencode's architecture surfaces: <strong>a conversation's "data and logic" and its "presentation" are two thoroughly separated layers.</strong> Underneath is just one copy of a thing—the session, message, part stored in SQLite (M9), driven in real time by the server's event stream (L54). And <strong>how to deliver this data before you is a presentation layer wholly replaceable</strong>:</p>
<div class="flow">
  <div class="f-node">one copy of session data<br><small>session/message (M9)</small></div>
  <div class="f-arrow">event stream →</div>
  <div class="f-node">the same core logic<br><small>agent loop/tools/protocol</small></div>
  <div class="f-arrow">presentation forks →</div>
  <div class="f-node">interactive TUI<br><small>full-screen/modal/scrollable</small></div>
  <div class="f-arrow">or →</div>
  <div class="f-node">run scrollback<br><small>linear/append/pipe-friendly</small></div>
</div>
<p>The power of this separation is exactly the root of opencode's "one fish, many dishes": the same agent core drives both the interactive TUI (this part M10) and run's non-interactive log, and even—recall L52's mention—the web app in the browser and the desktop. <strong>Because "what the agent is doing" and "how you watch it do it" were cut into two things from the start, each added "viewing" needn't rewrite that core.</strong> This echoes the book's deepest throughline: what good architecture repeatedly does is <strong>find the right seam, cutting the changing from the unchanging</strong>—L47 cut "core orchestration" from "each provider," L50 cut "data moving" from "semantic translation," L54 cut "event data" from "render timing," and this lesson cuts "<strong>the agent's conversation</strong>" from "<strong>the conversation's presentation</strong>." <strong>The more accurately the cut is found, the more the system can grow ever more possibilities without disturbing its foundation.</strong> With this M10 wraps up: you've fully walked opencode's terminal UI in full—from the opentui renderer, to the Provider pyramid and event data flow, to the prompt, dialogs, command palette, to run, that other face.</p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>This lesson closes M10—dialogs, the command palette, and the run scrollback contrast:</p>
  <ul>
    <li><strong>dialog = modal stack</strong> (<span class="mono">ui/dialog.tsx</span>): open=push, ESC=pop top (<span class="mono">slice(0,-1)</span>), stack non-empty enters modal; the stack naturally supports "a dialog opening a dialog" (LIFO, e.g. pick model→pick variant).</li>
    <li><strong>DialogSelect one part, reused everywhere</strong>: twenty-some dialogs (model/agent/MCP/skill/theme/session…) + command palette mostly built on a "filtered select box"—consistent search/navigate/confirm experience, adding a new dialog needs only an options list. Again "a uniform mold stamps the same shape" (like L36/L47/L53).</li>
    <li><strong>command palette = discoverability</strong> (<span class="mono">command-palette.tsx</span>): keymap <span class="mono">getCommandEntries</span> takes all visible commands into a searchable list, select <span class="mono">dispatchCommand</span>. No memorizing keybindings, search a keyword to run. The keymap is the single source, the palette just lays it out as a list.</li>
    <li><strong>run scrollback = another skin over the same data</strong> (<span class="mono">run/scrollback.surface.ts</span>): <span class="mono">opencode run</span> non-interactive mode renders the conversation as a linear, append-only, stdout-printed scrolling log (retained-append keeps streaming layout stable), pipeable/scriptable/CI. Three modes: non-interactive(default)/interactive local/interactive attach.</li>
  </ul>
  <p>The fundamental principle: <strong>data-logic separated from presentation</strong>—one session/message (M9) + one core, driving many faces (TUI / run / Web / desktop). Each added "viewing" needn't rewrite the core, another example of good architecture "finding the seam, cutting the changing from the unchanging" (echoing L47/L50/L54). M10 "TUI and client rendering" is hereby complete. The next part <strong>M11 turns to extensibility and integration</strong>: the plugin system, LSP, formatters, ACP/MCP—how opencode opens itself to third parties and external tools.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p><span class="mono">ui/dialog.tsx</span> writes the "modal stack"'s switches plainly and aptly (simplified from source):</p>
  <pre class="code"><span class="kw">const</span> [store, setStore] = <span class="fn">createStore</span>({ stack: [] })

<span class="cm">// once the stack is non-empty, enter "modal" mode: freeze the layer below, focus to the dialog</span>
<span class="fn">createEffect</span>(() =&gt; {
  <span class="kw">if</span> (store.stack.length === <span class="nu">0</span>) <span class="kw">return</span>
  <span class="kw">const</span> popMode = modeStack.<span class="fn">push</span>(<span class="st">"modal"</span>)
  <span class="fn">onCleanup</span>(popMode)                       <span class="cm">// stack emptied auto-exits modal</span>
})

<span class="cm">// ESC: pop only the topmost dialog</span>
keymap.<span class="fn">bind</span>(<span class="st">"escape"</span>, () =&gt; {
  <span class="kw">const</span> current = store.stack.<span class="fn">at</span>(-<span class="nu">1</span>)        <span class="cm">// top = newest-opened</span>
  current?.onClose?.()
  <span class="fn">setStore</span>(<span class="st">"stack"</span>, store.stack.<span class="fn">slice</span>(<span class="nu">0</span>, -<span class="nu">1</span>))  <span class="cm">// ← pop top, reveal the one below</span>
})

<span class="cm">// open a dialog = push onto the stack (can stack atop an existing dialog)</span>
<span class="kw">function</span> <span class="fn">open</span>(component) {
  <span class="fn">setStore</span>(<span class="st">"stack"</span>, [...store.stack, component])
}</pre>
  <p>What's most worth savoring is how it uses "the stack," the plainest data structure, to <strong>precisely hit the essence of modal interaction</strong>. All a modal's rules—"newest-opened takes priority," "ESC closes only this top layer," "closing a layer falls back to the previous," "freeze the layer below only until all closed"—need not one special case, all <strong>growing naturally from the stack's last-in-first-out semantics</strong>. <span class="mono">at(-1)</span> is "who should respond now," <span class="mono">slice(0,-1)</span> is "back one layer," empty stack is "back to non-modal." This is a textbook demonstration of "<strong>pick the right data structure and the logic simplifies itself</strong>": if you forced "a currentDialog variable + a pile of ifs deciding whether to restore the previous," you'd instantly sink into the quagmire of "who was the previous, is its state still there"; switch to a stack and those tangles <strong>simply don't happen</strong>. <strong>Mapping an interaction's "shape" onto a data structure whose semantics exactly fit</strong>—modal to stack, ordered-override to findLast (L41/L44), todos to a queue—often eliminates complexity at the root better than any clever control flow. Next time you face a thorny state-management problem, first ask: is there a data structure whose natural semantics are exactly the rule I want?</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>dialog = modal stack</strong> (<span class="mono">ui/dialog.tsx</span>): open=push, ESC=pop top <span class="mono">slice(0,-1)</span>, stack non-empty enters modal. The stack's LIFO naturally matches "a dialog opening a dialog, ESC closes only the top, closing falls back one layer"—pick the right data structure and logic simplifies itself.</li>
    <li><strong>DialogSelect reused everywhere</strong>: twenty-some dialogs (model/agent/MCP/skill/theme/session…) + command palette mostly built on a "filtered select box," consistent experience, adding a new dialog needs only options. Again "a uniform mold stamps the same shape" (L36/L47/L53).</li>
    <li><strong>command palette = discoverability</strong> (<span class="mono">command-palette.tsx</span>): keymap <span class="mono">getCommandEntries</span> takes all visible commands into a searchable list, select <span class="mono">dispatchCommand</span>. No memorizing keybindings. The keymap is the single source, the palette just lays it out.</li>
    <li><strong>run scrollback = another skin over the same data</strong> (<span class="mono">run/scrollback.surface.ts</span>): non-interactive mode renders the conversation as a linear, append-only, stdout-printed scrolling log, pipeable/scriptable/CI; three modes = non-interactive/interactive local/interactive attach, spreading "degree of interactivity" into a spectrum.</li>
    <li><strong>data separated from presentation</strong>: one session/message (M9) + one core → many faces (TUI/run/Web/desktop), each added "viewing" needn't rewrite the core. Another example of good architecture "finding the seam, cutting the changing from the unchanging" (echoing L47/L50/L54). M10 wraps up.</li>
  </ul>
</div>
""",
}
