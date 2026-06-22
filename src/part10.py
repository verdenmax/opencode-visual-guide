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
LESSON_53 = wip('TUI 应用结构', 'TUI app structure')
LESSON_54 = wip('事件到 store', 'Events to store')
LESSON_55 = wip('prompt 组件', 'The prompt component')
LESSON_56 = wip('对话框与 scrollback', 'Dialogs & scrollback')
