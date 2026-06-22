"""Part 12 (Part 12 · Practice & Reference) content. Placeholders until M12 fills them in."""
from placeholder import wip

"""Part 12 (Part 12 · Practice & Reference) content. Placeholders until M12 fills them in."""
from placeholder import wip

LESSON_62 = {
    "zh": r"""<p class="lead">前面 61 课，我们把 opencode 的<strong>内部机制</strong>从头到尾拆了个透——Effect 地基、客户端/服务器、Session 主循环、上下文系统、LLM 协议、工具、配置、持久化、TUI、扩展集成。但有一件最朴素的事还没做：<strong>怎么把这个项目在你自己机器上跑起来、改起来、调起来？</strong>这一课就补上这条「从源码到能跑的二进制」的实战回路。它面向的是<strong>想给 opencode 贡献代码、或想深入折腾它</strong>的你——读懂内部机制是一回事，能亲手把它跑起来、改一行看到效果、出问题能下断点排查，又是另一回事。核心就两件事：开发时用 <span class="mono">bun dev</span> <strong>直接从源码即时跑</strong>（改完立刻见效，无需编译）；要发布时用 <span class="mono">build.ts</span> <strong>把整个项目压成一个自包含的单文件二进制</strong>（连 Web UI 和模型数据都塞进去，拷到哪台机器都能跑）。中间还夹着一个让无数人踩坑的话题：<strong>调试器怎么接</strong>。</p>
<p>这一课最值得带走的洞见有两个。第一，<strong><span class="mono">bun dev</span> 和 <span class="mono">opencode</span> 是<em>同一个</em> CLI 的两副面孔</strong>——前者从源码跑（开发回路，秒级反馈）、后者是编译好的成品（生产发布），命令完全一一对应（<span class="mono">bun dev serve</span> ↔ <span class="mono">opencode serve</span>）。理解这点，你就不会再被「开发版和正式版行为不一样吗」困扰——它们本就是一份代码，只是「跑法」不同：一个把源码喂给运行时即时执行，一个把源码编译固化成二进制。第二，也是最点睛的——<strong><span class="mono">build.ts</span> 用 Bun 的「编译成单文件可执行程序」能力，把<em>代码 + Web UI + models.dev 数据</em>三样东西全嵌进<em>一个</em>二进制里</strong>，产物不依赖 node_modules、不依赖运行时，是个真正「拷了就能跑」的独立文件。读懂这个「<strong>把一切嵌进一个自包含产物</strong>」的思路，你就懂了 opencode 为什么能做到 <span class="mono">curl | bash</span> 一行装好、且跨平台。这两个洞见合起来，回答了一个新贡献者最朴素的疑问：我改的源码，是怎么变成用户手里那个 <span class="mono">opencode</span> 命令的？</p>

<div class="card analogy">
  <div class="tag">🏗️ 生活类比</div>
  把 <strong><span class="mono">bun dev</span></strong> 想象成<strong>在自家厨房现做现吃</strong>：食材（源码）摊在台面上，你改一刀、尝一口，立刻知道味道对不对——快、直接、所见即所得，但这套「厨房 + 食材 + 你」缺一不可，没法整个搬走。而 <strong><span class="mono">build.ts</span> 构建</strong>，是把这道菜做成一盒<strong>压缩饼干式的「太空食品」</strong>：不光主菜，连配菜（Web UI）、连调料包（models.dev 数据）全都<strong>真空封装进一个袋子</strong>——不需要厨房、不需要食材、不需要你在场，谁拿到这一袋，撕开就能吃。至于<strong>调试器接不上</strong>那段，像极了想给一个<strong>在隔音录音棚里干活的人装监听</strong>：你在棚外装的窃听器（断点）根本听不到棚里（worker 线程里跑的 server）的声音——要么让他别进录音棚（<span class="mono">bun dev spawn</span>），要么你干脆推门进棚、贴身监听（单独起 server 进程再 attach）。
</div>

<h2><span class="mono">bun dev</span>：从源码直接跑的开发回路</h2>
<p>opencode 用 Bun 作运行时（要求 <span class="mono">Bun 1.3+</span>）。在仓库根目录，开发只需两行：<span class="mono">bun install</span> 装依赖、<span class="mono">bun dev</span> 起开发服务器。关键认知是：<span class="mono">bun dev</span> 不是「另一个程序」，它就是<strong>本地从源码跑的 <span class="mono">opencode</span></strong>——两者跑的是同一套 CLI，命令一一对应。这个设计看似平常，其实省去了一类常见的痛苦：很多项目的「开发模式」和「生产模式」是两套入口、两套配置，常出现「开发能复现、装好却不行」的灵异 bug。opencode 让两者共用一份代码、只差「源码跑 vs 编译跑」，从根上消除了这类差异：</p>
<div class="cols">
  <div class="col"><h4>开发（仓库根目录）</h4><p><span class="mono">bun dev --help</span> 看所有命令<br><span class="mono">bun dev serve</span> 起无头 API 服务器<br><span class="mono">bun dev web</span> 起服务器+开 Web 界面<br><span class="mono">bun dev &lt;目录&gt;</span> 在指定目录起 TUI</p><p>从<strong>源码</strong>直接跑，改完即生效，秒级反馈。</p></div>
  <div class="col"><h4>生产（装好的成品）</h4><p><span class="mono">opencode --help</span> 看所有命令<br><span class="mono">opencode serve</span> 起无头 API 服务器<br><span class="mono">opencode web</span> 起服务器+开 Web 界面<br><span class="mono">opencode &lt;目录&gt;</span> 在指定目录起 TUI</p><p>编译好的<strong>单文件二进制</strong>，拷了就能跑。</p></div>
</div>
<p>默认 <span class="mono">bun dev</span> 会在 <span class="mono">packages/opencode</span> 目录里跑 opencode（即「用 opencode 编辑 opencode 自己的那个包」）。要让它对着别的目录/仓库跑，加个参数即可：<span class="mono">bun dev &lt;目录&gt;</span>；要对着 opencode 仓库自己的根目录跑，就 <span class="mono">bun dev .</span>。这个「换个目录就换个工作对象」的灵活，正是 L61 <strong>Location</strong> 解耦的直接红利——会话逻辑和「在哪个目录」早已剥离，命令行换个路径，整个 opencode 就在新地方干活。要单独起无头服务器，<span class="mono">bun dev serve</span>，默认监听 <span class="mono">4096</span> 端口（<span class="mono">--port 8080</span> 可改）。</p>
<p>为什么开发要这样「从源码即时跑」而不是「每次先编译再运行」？因为编译要时间，而开发的本质是<strong>高频的「改一点、看一眼」循环</strong>——你可能一分钟内改十次，若每次都等几十秒编译，心流就断了。<span class="mono">bun dev</span> 直接把 TypeScript 源码喂给 Bun 运行时跑，省掉了编译这一步，改完保存、立刻见效，反馈是<strong>秒级</strong>的。这也是为什么 opencode 选 Bun：它既是包管理器、又是能直接跑 TS 的运行时、还是打包器，一套工具贯穿「装依赖→跑源码→编成品」全程，省去了传统 Node 项目里 <span class="mono">tsc</span>+<span class="mono">node</span>+<span class="mono">webpack</span> 那一堆拼装。理解了这点，下面这个由几块拼成、各司其职的 monorepo 结构也就顺理成章：</p>
<div class="cellgroup">
  <div class="cel"><b>packages/opencode</b><br>核心业务逻辑 + 服务器（CLI 入口、Session、工具…全在这）</div>
  <div class="cel"><b>cli/tui/</b><br>TUI 代码，SolidJS + opentui（L52–56）</div>
  <div class="cel"><b>packages/app</b><br>共享 Web UI 组件，SolidJS 写</div>
  <div class="cel"><b>packages/desktop</b><br>原生桌面端，Electron 包住 app</div>
  <div class="cel"><b>packages/plugin</b><br><span class="mono">@opencode-ai/plugin</span> 的源（L57）</div>
  <div class="cel"><b>script/generate.ts</b><br>改了 server/SDK 后跑它重生成 SDK</div>
</div>

<h2><span class="mono">build.ts</span>：把整个项目压成一个自包含二进制</h2>
<p>开发回路爽在「即时」，但你没法把「源码 + Bun + node_modules」整套塞给用户。生产发布要的是一个<strong>拷了就能跑</strong>的独立文件。这正是 <span class="mono">packages/opencode/script/build.ts</span> 干的事——用 Bun 的 <span class="mono">Bun.build({ compile: ... })</span>「编译成单文件可执行程序」能力，把三样东西<strong>全嵌进一个二进制</strong>。注意这里的「嵌」是字面意义的嵌入：Web UI 不是放在二进制旁边的一个文件夹，而是被<strong>编译进二进制内部</strong>；模型清单也不是运行时去网上拉，而是<strong>在编译时就写死成常量</strong>。最终你得到的不是「一个程序 + 一堆资源文件」，而是<strong>单独一个文件</strong>，里头什么都有：</p>
<div class="layers">
  <div class="layer"><b>① 业务代码</b>　<span class="mono">src/index.ts</span> 全部 TS 经 Bun bundle+minify 打成一份</div>
  <div class="layer"><b>② Web UI</b>　先 <span class="mono">build packages/app</span>，再把整个 dist 每个文件 <span class="mono">import ... with {type:"file"}</span> 嵌进去（<span class="mono">createEmbeddedWebUIBundle</span>）</div>
  <div class="layer"><b>③ models.dev 数据</b>　<span class="mono">define</span> 注入 <span class="mono">OPENCODE_MODELS_DEV</span>（模型清单编进常量）+ 版本/channel/libc</div>
  <div class="layer"><b>= 一个二进制</b>　<span class="mono">dist/opencode-&lt;平台&gt;/bin/opencode</span>，不依赖 node_modules/运行时</div>
</div>
<p>「把资源在编译期嵌进产物」这个思路，你应当眼熟——它和很多语言的「资源内嵌」（如 Rust 的 rust-embed）是同一招：<strong>编译期把所有依赖固化进单一产物，运行期零外部依赖</strong>。好处是部署极简（一个文件）、启动极快（不必运行时再去找资源）、版本绝不错配（资源和代码编在一起，不可能出现「代码是新的、资源是旧的」）。代价是产物体积大一些、且换资源就得重编——但对一个要分发给海量用户的 CLI 工具来说，这笔交易极其划算。整条流水线大致是：</p>
<div class="flow">
  <div class="node">清 <span class="mono">dist</span></div>
  <div class="arrow">→</div>
  <div class="node">嵌 Web UI</div>
  <div class="arrow">→</div>
  <div class="node">按目标平台<br><span class="mono">Bun.build compile</span></div>
  <div class="arrow">→</div>
  <div class="node">冒烟测试<br><span class="mono">opencode --version</span></div>
  <div class="arrow">→</div>
  <div class="node">写 per-target<br><span class="mono">package.json</span></div>
</div>
<p>本地想要一个独立可执行文件，跑 <span class="mono">./packages/opencode/script/build.ts --single</span>——<span class="mono">--single</span> 让它只为<strong>当前平台</strong>编一个原生二进制（不加则按一张<strong>跨平台矩阵</strong>把 linux/macOS/Windows × arm64/x64 × musl/baseline 全编一遍，那是 CI 发版用的）。编完产物在 <span class="mono">./packages/opencode/dist/opencode-&lt;平台&gt;/bin/opencode</span>（<span class="mono">&lt;平台&gt;</span> 如 <span class="mono">linux-x64</span>、<span class="mono">darwin-arm64</span>）。值得一提的是脚本里的<strong>冒烟测试</strong>：编完当前平台的二进制后，它会立刻跑一次 <span class="mono">opencode --version</span>，跑不出来就 <span class="mono">exit(1)</span>——一道「编出来的东西至少能启动」的最低保障，失败就当场拦下，绝不把坏二进制发出去。</p>
<p>为什么非要做成「单文件、自包含」？因为这直接决定了<strong>分发体验</strong>。如果产物依赖 node_modules，用户就得先装 Node、再 <span class="mono">npm install</span> 一大堆依赖，版本不对还会出岔子；而一个自包含二进制，<span class="mono">curl | bash</span> 下载一个文件、<span class="mono">chmod +x</span> 就能跑，没有任何外部依赖、不挑机器环境。</p>
<p>跨平台矩阵的意义也在此：CI 一次把所有平台的二进制都编好，无论用户在 Mac、Linux 还是 Windows、是 Intel 还是 ARM，都能下到一个<strong>专门为他那台机器编译好</strong>的原生文件。</p>
<p>这种「一处编译、处处可跑」的发布形态，是 opencode 能做到「一行命令装好」的工程底座——而它几乎是<strong>免费</strong>得来的，全靠 Bun 把「编译成单文件可执行程序」这件以前很麻烦的事变成了一个 <span class="mono">Bun.build</span> 调用。回头看，这也呼应了全书反复出现的主题：<strong>站在成熟工具的肩膀上</strong>——L39 借 Ripgrep、L51 借 git、L59 借语言服务器，而这里借 Bun 的编译能力，把本该自己造的轮子统统省掉，专注于真正独特的 agent 逻辑。</p>

<h2>调试器：为什么要 <span class="mono">spawn</span>、要分开调</h2>
<p>Bun 的调试体验官方坦言「还很粗糙」。最可靠的方式是<strong>手动</strong>带 <span class="mono">--inspect</span> 跑、再把调试器 attach 到那个 URL：<span class="mono">bun run --inspect=ws://localhost:6499/ dev ...</span>。这里的 <span class="mono">--inspect=ws://...</span> 是让 Bun 开一个调试协议的 WebSocket 端口，你的调试器（VSCode、Chrome DevTools）连上这个地址，就能下断点、看变量、单步执行。但这里有个最常见的坑，而它恰恰是一扇<strong>窥见 opencode 运行时结构的窗口</strong>：</p>
<div class="trace">
  <div class="step"><span class="n">1</span> 你想在 <strong>server 代码</strong>里下断点，于是 <span class="mono">--inspect</span> 跑 <span class="mono">bun dev</span></div>
  <div class="step"><span class="n">2</span> 但 <span class="mono">bun dev</span> 把 server 跑在一个 <strong>worker 线程</strong>里</div>
  <div class="step"><span class="n">3</span> 断点装在主线程的调试器上，<strong>映不进 worker 线程</strong> → 断点不触发</div>
  <div class="step"><span class="n">4</span> 解法：<span class="mono">bun dev spawn</span>（让 server 不进 worker 线程跑），断点就能命中</div>
</div>
<p>读懂这个坑，你顺带就证实了 L09–L13 讲的架构：opencode 的 server 确实是个<strong>能独立存在的进程/线程</strong>，TUI 只是连上它的客户端。如果 <span class="mono">spawn</span> 也不灵，就<strong>把 server 和 TUI 彻底分开调</strong>——这正是「客户端/服务器分离」给调试带来的便利：server 是个监听端口的独立进程，你完全可以单独把它带 <span class="mono">--inspect</span> 起起来、单独下断点，再用 <span class="mono">opencode attach</span> 把 TUI 接上去，两边互不干扰。这种「能分头调试」的能力，不是调试器的功劳，而是<strong>架构本身就把两者解耦了</strong>的副产品——又一次印证「好的架构会在意想不到的地方还你便利」（同 L61 move-session）。</p>
<div class="vflow">
  <div class="vnode"><b>分开调 server</b>：<span class="mono">bun run --inspect=ws://localhost:6499/ --cwd packages/opencode ./src/index.ts serve --port 4096</span>，再 <span class="mono">opencode attach http://localhost:4096</span> 把 TUI 接上去</div>
  <div class="vnode"><b>分开调 TUI</b>：<span class="mono">bun run --inspect=ws://localhost:6499/ --cwd packages/opencode --conditions=browser ./src/index.ts</span></div>
  <div class="vnode"><b>省事小技巧</b>：嫌每次写 <span class="mono">--inspect</span> 烦，<span class="mono">export BUN_OPTIONS=--inspect=ws://localhost:6499/</span> 一劳永逸；想「连上就停在第一行」用 <span class="mono">--inspect-wait</span>/<span class="mono">--inspect-brk</span></div>
</div>
<p>用 VSCode 的话，仓库给了 <span class="mono">.vscode/settings.example.json</span> 和 <span class="mono">launch.example.json</span> 作范本。但有两个<strong>已知会出问题</strong>的方式要避开：<span class="mono">"request": "launch"</span> 的调试配置、以及在 VSCode 的 <span class="mono">JavaScript Debug Terminal</span> 里跑——这两种都可能让断点<strong>错位</strong>（映到错误的行，等于没用）。官方建议优先用上面「手动 <span class="mono">--inspect</span> + attach」的路子。这背后是个朴素但重要的工程态度：<strong>诚实地把工具的粗糙之处和踩坑姿势写进文档</strong>，比假装一切顺滑、让贡献者自己撞墙要厚道得多。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  这一课串起的是一条<strong>开发者实战回路</strong>：左端是 <span class="mono">bun dev</span>——从<strong>源码即时跑</strong>，秒级反馈，配合 <span class="mono">--inspect</span> 调试（注意 worker 线程的坑、善用 server/TUI 分离）；右端是 <span class="mono">build.ts --single</span>——把<strong>代码 + Web UI + 模型数据</strong>编译嵌进<strong>一个自包含二进制</strong>，作为生产发布的成品。两端跑的是<strong>同一份 CLI、同一套代码</strong>，只是一个「从源码跑」、一个「编译后跑」。理解这条回路，你就具备了把这个项目<strong>跑起来、改起来、调起来、最终打包出去</strong>的全部基本功。
</div>

<div class="card detail">
  <div class="tag">🔬 实现细节</div>
  <span class="mono">build.ts</span> 的跨平台矩阵 <span class="mono">allTargets</span> 覆盖 linux/darwin/win32 × arm64/x64，并细分 <span class="mono">musl</span> ABI 与 <span class="mono">avx2:false</span> 的 baseline 变体；<span class="mono">--single</span> 时过滤成「仅当前 os+arch、且非 baseline/非 abi 特化」的一个原生目标。<span class="mono">Bun.build</span> 关键参数：<span class="mono">minify:true</span>、<span class="mono">splitting:true</span>、<span class="mono">format:"esm"</span>、<span class="mono">compile.target</span> 形如 <span class="mono">bun-linux-x64</span>、<span class="mono">compile.outfile</span> 指向 <span class="mono">dist/&lt;name&gt;/bin/opencode</span>。Web UI 嵌入用 <span class="mono">createEmbeddedWebUIBundle</span>：先 <span class="mono">bun run --cwd packages/app build</span>，再把 dist 下每个文件生成 <span class="mono">import file_i from "..." with {type:"file"}</span>，导出成一张「路径→文件」映射，作为虚拟入口 <span class="mono">opencode-web-ui.gen.ts</span> 一并编进二进制。改了 <span class="mono">server/server.ts</span> 这类 API/SDK 面，记得 <span class="mono">./script/generate.ts</span> 重生成 SDK。
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong><span class="mono">bun dev</span> = 从源码跑的 <span class="mono">opencode</span></strong>：同一套 CLI，命令一一对应（<span class="mono">serve</span>/<span class="mono">web</span>/<span class="mono">&lt;目录&gt;</span>）。要求 Bun 1.3+，根目录 <span class="mono">bun install</span>+<span class="mono">bun dev</span>；默认在 <span class="mono">packages/opencode</span> 跑、<span class="mono">bun dev &lt;目录&gt;</span> 换工作对象（L61 Location 红利）；<span class="mono">serve</span> 默认 4096 端口。monorepo=opencode(核心+server)/app(Web UI)/desktop(Electron)/plugin。</li>
    <li><strong><span class="mono">build.ts</span> = 编译成自包含单文件二进制</strong>：用 <span class="mono">Bun.build compile</span> 把<strong>代码 + Web UI（<span class="mono">with {type:"file"}</span> 嵌入）+ models.dev 数据（<span class="mono">define</span> 注入）</strong>全塞进一个二进制，不依赖 node_modules/运行时（同 rust-embed「编译期嵌资源」）。<span class="mono">--single</span> 只编当前平台、不加则跨平台矩阵；编后冒烟测试 <span class="mono">--version</span> 失败即 <span class="mono">exit(1)</span>。</li>
    <li><strong>调试看穿运行时结构</strong>：最可靠是手动 <span class="mono">--inspect=ws://...</span> 跑+attach。坑：<span class="mono">bun dev</span> 把 server 跑在 <strong>worker 线程</strong>→断点映不进→改用 <span class="mono">bun dev spawn</span>；或借「客户端/服务器分离」<strong>分开调</strong>（server <span class="mono">serve --port 4096</span> + <span class="mono">opencode attach</span>，TUI 加 <span class="mono">--conditions=browser</span>）。避开 VSCode <span class="mono">"request":"launch"</span> 与 Debug Terminal（断点错位）。</li>
  </ul>
</div>
""",
    "en": r"""<p class="lead">Over the previous 61 lessons we dissected opencode's <strong>internal mechanisms</strong> end to end—the Effect foundation, client/server, the Session main loop, the context system, the LLM protocol, tools, config, persistence, TUI, extensions and integration. But one humble thing remains: <strong>how do you actually run, change, and debug this project on your own machine?</strong> This lesson fills in that practical loop "from source to a runnable binary." It's aimed at <strong>you who want to contribute to opencode, or to seriously hack on it</strong>—understanding the internals is one thing; being able to run it yourself, change a line and see the effect, and set a breakpoint when something breaks is quite another. It comes down to two things: during development, <span class="mono">bun dev</span> <strong>runs straight from source, instantly</strong> (changes take effect immediately, no compile step); to ship, <span class="mono">build.ts</span> <strong>compresses the whole project into one self-contained single-file binary</strong> (Web UI and model data stuffed in, runnable on any machine). Sandwiched between is a topic countless people trip over: <strong>how to attach a debugger</strong>.</p>
<p>There are two insights worth taking away. First, <strong><span class="mono">bun dev</span> and <span class="mono">opencode</span> are two faces of the <em>same</em> CLI</strong>—the former runs from source (the dev loop, second-level feedback), the latter is the compiled product (production release), and the commands correspond one-to-one (<span class="mono">bun dev serve</span> ↔ <span class="mono">opencode serve</span>). Grasp this and you'll never again wonder "do the dev and release versions behave differently"—they're literally one codebase, just run differently: one feeds source to the runtime for instant execution, the other compiles source into a fixed binary. Second, the real gem—<strong><span class="mono">build.ts</span> uses Bun's "compile to a single executable" ability to embed <em>code + Web UI + models.dev data</em>, all three, into <em>one</em> binary</strong>; the artifact depends on neither node_modules nor a runtime, a truly "copy it and run" standalone file. Understand this "<strong>embed everything into one self-contained artifact</strong>" idea and you'll see why opencode can be installed with a single <span class="mono">curl | bash</span>, cross-platform. Together these two insights answer a new contributor's most basic question: how does the source I edit turn into that <span class="mono">opencode</span> command in a user's hands?</p>

<div class="card analogy">
  <div class="tag">🏗️ Analogy</div>
  Picture <strong><span class="mono">bun dev</span></strong> as <strong>cooking and tasting right in your own kitchen</strong>: the ingredients (source) are spread on the counter, you make a cut, take a bite, and instantly know if the flavor's right—fast, direct, what-you-see-is-what-you-get; but this "kitchen + ingredients + you" trio is indivisible, you can't ship the whole thing away. A <strong><span class="mono">build.ts</span> build</strong>, by contrast, turns the dish into a box of <strong>compressed-biscuit "space food"</strong>: not just the main course, but the sides (Web UI) and the seasoning packets (models.dev data) too, all <strong>vacuum-sealed into one bag</strong>—no kitchen, no ingredients, no you required; whoever gets the bag just tears it open and eats. As for the <strong>debugger-won't-attach</strong> bit, it's just like trying to bug <strong>someone working inside a soundproof recording booth</strong>: the wiretap (breakpoint) you plant outside simply can't hear what's inside the booth (the server running in a worker thread)—either keep him out of the booth (<span class="mono">bun dev spawn</span>), or push the door open and listen up close (start the server as a separate process and attach).
</div>

<h2><span class="mono">bun dev</span>: the dev loop that runs straight from source</h2>
<p>opencode uses Bun as its runtime (requires <span class="mono">Bun 1.3+</span>). At the repo root, development takes just two lines: <span class="mono">bun install</span> for deps, <span class="mono">bun dev</span> to start the dev server. The key realization: <span class="mono">bun dev</span> is not "another program," it <strong>is <span class="mono">opencode</span> run locally from source</strong>—both run the same CLI, commands corresponding one-to-one. This design looks ordinary but spares you a common pain: many projects have separate entry points and configs for "dev mode" and "production mode," breeding ghostly "reproduces in dev, fails once installed" bugs. opencode lets both share one codebase, differing only in "run from source vs run compiled," eliminating that class of divergence at the root:</p>
<div class="cols">
  <div class="col"><h4>Development (repo root)</h4><p><span class="mono">bun dev --help</span> show all commands<br><span class="mono">bun dev serve</span> start headless API server<br><span class="mono">bun dev web</span> start server + open Web UI<br><span class="mono">bun dev &lt;dir&gt;</span> start TUI in a given directory</p><p>Runs straight from <strong>source</strong>, changes take effect instantly, second-level feedback.</p></div>
  <div class="col"><h4>Production (the installed product)</h4><p><span class="mono">opencode --help</span> show all commands<br><span class="mono">opencode serve</span> start headless API server<br><span class="mono">opencode web</span> start server + open Web UI<br><span class="mono">opencode &lt;dir&gt;</span> start TUI in a given directory</p><p>A compiled <strong>single-file binary</strong>, copy it and run.</p></div>
</div>
<p>By default <span class="mono">bun dev</span> runs opencode inside the <span class="mono">packages/opencode</span> directory (i.e. "using opencode to edit opencode's own package"). To point it at another directory/repo, just add an argument: <span class="mono">bun dev &lt;dir&gt;</span>; to run it against the opencode repo's own root, <span class="mono">bun dev .</span>. This "swap the directory, swap the work target" flexibility is a direct dividend of L61's <strong>Location</strong> decoupling—the session logic was long peeled apart from "which directory," so changing the path on the command line makes the whole of opencode work in the new place. To start the headless server alone, <span class="mono">bun dev serve</span>, listening on port <span class="mono">4096</span> by default (<span class="mono">--port 8080</span> to change).</p>
<p>Why should development "run from source instantly" rather than "compile first, then run, every time"? Because compiling takes time, and development is essentially a <strong>high-frequency "tweak a bit, glance" loop</strong>—you might change things ten times a minute, and if each one waited tens of seconds to compile, the flow would break. <span class="mono">bun dev</span> feeds TypeScript source straight to the Bun runtime, skipping the compile step; save your change and it takes effect immediately, feedback in <strong>seconds</strong>. This is also why opencode chose Bun: it's package manager, a runtime that runs TS directly, and bundler all in one, spanning "install deps → run source → compile product" with a single tool, sparing the <span class="mono">tsc</span>+<span class="mono">node</span>+<span class="mono">webpack</span> assembly of a traditional Node project. With that understood, the monorepo's several-piece, each-with-its-job structure follows naturally:</p>
<div class="cellgroup">
  <div class="cel"><b>packages/opencode</b><br>Core business logic + server (CLI entry, Session, tools… all here)</div>
  <div class="cel"><b>cli/tui/</b><br>TUI code, SolidJS + opentui (L52–56)</div>
  <div class="cel"><b>packages/app</b><br>Shared Web UI components, written in SolidJS</div>
  <div class="cel"><b>packages/desktop</b><br>Native desktop app, Electron wrapping app</div>
  <div class="cel"><b>packages/plugin</b><br>Source of <span class="mono">@opencode-ai/plugin</span> (L57)</div>
  <div class="cel"><b>script/generate.ts</b><br>Run it after changing server/SDK to regenerate the SDK</div>
</div>

<h2><span class="mono">build.ts</span>: compress the whole project into one self-contained binary</h2>
<p>The dev loop is great for "instant," but you can't hand users the whole "source + Bun + node_modules." A production release needs one <strong>copy-it-and-run</strong> standalone file. That's exactly what <span class="mono">packages/opencode/script/build.ts</span> does—using Bun's <span class="mono">Bun.build({ compile: ... })</span> "compile to a single executable" ability to embed three things <strong>into one binary</strong>. Note "embed" is literal: the Web UI isn't a folder sitting next to the binary, it's <strong>compiled inside the binary</strong>; the model list isn't fetched from the network at runtime, it's <strong>hardcoded into a constant at compile time</strong>. What you end up with is not "a program + a pile of resource files," but <strong>a single file</strong> with everything inside:</p>
<div class="layers">
  <div class="layer"><b>① Business code</b>　all of <span class="mono">src/index.ts</span>'s TS bundled+minified by Bun into one</div>
  <div class="layer"><b>② Web UI</b>　first <span class="mono">build packages/app</span>, then embed every file of dist via <span class="mono">import ... with {type:"file"}</span> (<span class="mono">createEmbeddedWebUIBundle</span>)</div>
  <div class="layer"><b>③ models.dev data</b>　<span class="mono">define</span> injects <span class="mono">OPENCODE_MODELS_DEV</span> (model list baked into a constant) + version/channel/libc</div>
  <div class="layer"><b>= one binary</b>　<span class="mono">dist/opencode-&lt;platform&gt;/bin/opencode</span>, depends on neither node_modules nor a runtime</div>
</div>
<p>This "embed resources into the artifact at compile time" idea should look familiar—it's the same move as many languages' "resource embedding" (such as Rust's rust-embed): <strong>fix all dependencies into a single artifact at compile time, zero external dependencies at runtime</strong>. The upside is dead-simple deployment (one file), blazing startup (no hunting for resources at runtime), and never-mismatched versions (resources and code compiled together, so no "new code, old resources"). The cost is a somewhat larger artifact and a recompile to swap resources—but for a CLI tool distributed to a massive user base, that's an extremely good trade. The pipeline roughly goes:</p>
<div class="flow">
  <div class="node">clean <span class="mono">dist</span></div>
  <div class="arrow">→</div>
  <div class="node">embed Web UI</div>
  <div class="arrow">→</div>
  <div class="node">per target<br><span class="mono">Bun.build compile</span></div>
  <div class="arrow">→</div>
  <div class="node">smoke test<br><span class="mono">opencode --version</span></div>
  <div class="arrow">→</div>
  <div class="node">write per-target<br><span class="mono">package.json</span></div>
</div>
<p>For a standalone executable locally, run <span class="mono">./packages/opencode/script/build.ts --single</span>—<span class="mono">--single</span> makes it compile just one native binary for the <strong>current platform</strong> (without it, it compiles the whole <strong>cross-platform matrix</strong>: linux/macOS/Windows × arm64/x64 × musl/baseline, which is for CI releases). The result lands at <span class="mono">./packages/opencode/dist/opencode-&lt;platform&gt;/bin/opencode</span> (<span class="mono">&lt;platform&gt;</span> like <span class="mono">linux-x64</span>, <span class="mono">darwin-arm64</span>). Worth noting is the script's <strong>smoke test</strong>: after compiling the current-platform binary, it immediately runs <span class="mono">opencode --version</span> once, and <span class="mono">exit(1)</span> if that fails—a minimal "what we built can at least start" guarantee, caught on the spot, never shipping a broken binary.</p>
<p>Why insist on "single-file, self-contained"? Because it directly determines the <strong>distribution experience</strong>. If the artifact depended on node_modules, users would first install Node, then <span class="mono">npm install</span> a heap of deps, with version mismatches causing trouble; whereas a self-contained binary downloads as one file via <span class="mono">curl | bash</span>, <span class="mono">chmod +x</span>, and runs—no external deps, no fussiness about machine environment. </p>
<p>That's also the point of the cross-platform matrix: CI compiles binaries for all platforms at once, so whether a user is on Mac, Linux, or Windows, Intel or ARM, they can download a native file <strong>compiled specifically for their machine</strong>. </p>
<p>This "compile in one place, run everywhere" release form is the engineering bedrock of opencode's "install with one command"—and it comes almost <strong>for free</strong>, all thanks to Bun turning the once-painful "compile to a single executable" into a single <span class="mono">Bun.build</span> call. In hindsight this echoes a theme recurring throughout the book: <strong>standing on the shoulders of mature tools</strong>—L39 borrows Ripgrep, L51 borrows git, L59 borrows language servers, and here we borrow Bun's compile ability, sparing every wheel we'd otherwise reinvent to focus on the genuinely unique agent logic.</p>

<h2>The debugger: why <span class="mono">spawn</span>, why debug them separately</h2>
<p>Bun's debugging experience is, the maintainers admit, "still rough around the edges." The most reliable way is to <strong>manually</strong> run with <span class="mono">--inspect</span> and attach your debugger to that URL: <span class="mono">bun run --inspect=ws://localhost:6499/ dev ...</span>. Here <span class="mono">--inspect=ws://...</span> tells Bun to open a debug-protocol WebSocket port; your debugger (VSCode, Chrome DevTools) connects to that address and can then set breakpoints, inspect variables, and step. But there's a most-common pitfall here, and it's precisely a <strong>window into opencode's runtime structure</strong>:</p>
<div class="trace">
  <div class="step"><span class="n">1</span> You want a breakpoint in the <strong>server code</strong>, so you run <span class="mono">bun dev</span> with <span class="mono">--inspect</span></div>
  <div class="step"><span class="n">2</span> But <span class="mono">bun dev</span> runs the server in a <strong>worker thread</strong></div>
  <div class="step"><span class="n">3</span> The breakpoint sits on the main thread's debugger, <strong>doesn't map into the worker thread</strong> → it won't trigger</div>
  <div class="step"><span class="n">4</span> Fix: <span class="mono">bun dev spawn</span> (run the server outside the worker thread), and the breakpoint hits</div>
</div>
<p>Understand this pitfall and you've incidentally confirmed the architecture from L09–L13: opencode's server really is a <strong>process/thread that can exist independently</strong>, with the TUI merely a client connecting to it. If <span class="mono">spawn</span> doesn't work either, <strong>debug the server and TUI entirely separately</strong>—that's the debugging convenience the "client/server separation" affords: the server is a standalone process listening on a port, so you can start it alone with <span class="mono">--inspect</span>, set breakpoints alone, then connect the TUI via <span class="mono">opencode attach</span>, the two not interfering. This "debug them separately" ability isn't the debugger's doing, but a byproduct of <strong>the architecture having decoupled the two in the first place</strong>—another proof that "good architecture pays you back convenience in unexpected places" (like L61's move-session).</p>
<div class="vflow">
  <div class="vnode"><b>Debug the server separately</b>: <span class="mono">bun run --inspect=ws://localhost:6499/ --cwd packages/opencode ./src/index.ts serve --port 4096</span>, then <span class="mono">opencode attach http://localhost:4096</span> to connect the TUI</div>
  <div class="vnode"><b>Debug the TUI separately</b>: <span class="mono">bun run --inspect=ws://localhost:6499/ --cwd packages/opencode --conditions=browser ./src/index.ts</span></div>
  <div class="vnode"><b>Handy tip</b>: tired of writing <span class="mono">--inspect</span> every time? <span class="mono">export BUN_OPTIONS=--inspect=ws://localhost:6499/</span> once and for all; to "stop at the first line on connect" use <span class="mono">--inspect-wait</span>/<span class="mono">--inspect-brk</span></div>
</div>
<p>If you use VSCode, the repo provides <span class="mono">.vscode/settings.example.json</span> and <span class="mono">launch.example.json</span> as templates. But avoid two <strong>known-problematic</strong> approaches: debug configs with <span class="mono">"request": "launch"</span>, and running inside VSCode's <span class="mono">JavaScript Debug Terminal</span>—both can <strong>misplace</strong> breakpoints (mapping them to the wrong lines, i.e. useless). The maintainers recommend preferring the "manual <span class="mono">--inspect</span> + attach" path above. Behind this is a humble but important engineering attitude: <strong>honestly writing a tool's rough edges and pitfall-avoidance postures into the docs</strong> is far kinder than pretending everything's smooth and letting contributors hit the wall themselves.</p>

<div class="card macro">
  <div class="tag">🗺️ Big picture</div>
  What this lesson threads together is a <strong>developer's practical loop</strong>: at the left end is <span class="mono">bun dev</span>—running <strong>from source instantly</strong>, second-level feedback, debugged with <span class="mono">--inspect</span> (mind the worker-thread pitfall, make good use of server/TUI separation); at the right end is <span class="mono">build.ts --single</span>—compiling and embedding <strong>code + Web UI + model data</strong> into <strong>one self-contained binary</strong>, the product for production release. Both ends run the <strong>same CLI, the same codebase</strong>, one just "runs from source," the other "runs compiled." Understand this loop and you've got all the fundamentals to <strong>run, change, debug, and ultimately package out</strong> this project.
</div>

<div class="card detail">
  <div class="tag">🔬 Implementation details</div>
  <span class="mono">build.ts</span>'s cross-platform matrix <span class="mono">allTargets</span> covers linux/darwin/win32 × arm64/x64, further splitting into the <span class="mono">musl</span> ABI and <span class="mono">avx2:false</span> baseline variants; with <span class="mono">--single</span> it filters down to one native target "current os+arch only, non-baseline, non-abi-specialized." Key <span class="mono">Bun.build</span> params: <span class="mono">minify:true</span>, <span class="mono">splitting:true</span>, <span class="mono">format:"esm"</span>, <span class="mono">compile.target</span> like <span class="mono">bun-linux-x64</span>, <span class="mono">compile.outfile</span> pointing at <span class="mono">dist/&lt;name&gt;/bin/opencode</span>. Web UI embedding uses <span class="mono">createEmbeddedWebUIBundle</span>: first <span class="mono">bun run --cwd packages/app build</span>, then generate <span class="mono">import file_i from "..." with {type:"file"}</span> for each file under dist, exporting a "path→file" map as a virtual entry <span class="mono">opencode-web-ui.gen.ts</span> compiled into the binary too. Changed an API/SDK surface like <span class="mono">server/server.ts</span>? Remember <span class="mono">./script/generate.ts</span> to regenerate the SDK.
</div>

<div class="card key">
  <div class="tag">🎯 Key points</div>
  <ul>
    <li><strong><span class="mono">bun dev</span> = <span class="mono">opencode</span> run from source</strong>: the same CLI, commands corresponding one-to-one (<span class="mono">serve</span>/<span class="mono">web</span>/<span class="mono">&lt;dir&gt;</span>). Requires Bun 1.3+, <span class="mono">bun install</span>+<span class="mono">bun dev</span> at the root; runs in <span class="mono">packages/opencode</span> by default, <span class="mono">bun dev &lt;dir&gt;</span> swaps the work target (L61 Location dividend); <span class="mono">serve</span> on port 4096 by default. monorepo = opencode(core+server)/app(Web UI)/desktop(Electron)/plugin.</li>
    <li><strong><span class="mono">build.ts</span> = compile to a self-contained single-file binary</strong>: <span class="mono">Bun.build compile</span> stuffs <strong>code + Web UI (embedded via <span class="mono">with {type:"file"}</span>) + models.dev data (injected via <span class="mono">define</span>)</strong> all into one binary, depending on neither node_modules nor a runtime (same as rust-embed's "embed resources at compile time"). <span class="mono">--single</span> compiles only the current platform, without it the cross-platform matrix; a post-compile smoke test <span class="mono">--version</span> means <span class="mono">exit(1)</span> on failure.</li>
    <li><strong>Debugging sees through the runtime structure</strong>: most reliable is manually running with <span class="mono">--inspect=ws://...</span> + attach. Pitfall: <span class="mono">bun dev</span> runs the server in a <strong>worker thread</strong> → breakpoints don't map in → use <span class="mono">bun dev spawn</span>; or, leveraging "client/server separation," <strong>debug them separately</strong> (server <span class="mono">serve --port 4096</span> + <span class="mono">opencode attach</span>, TUI with <span class="mono">--conditions=browser</span>). Avoid VSCode <span class="mono">"request":"launch"</span> and the Debug Terminal (misplaced breakpoints).</li>
  </ul>
</div>
""",
}

LESSON_63 = {
    "zh": r"""<p class="lead">上一课你学会了把 opencode <strong>跑起来、编出来、调起来</strong>。这一课是临门一脚：<strong>怎么验证你的改动是对的，又怎么把它贡献回去？</strong>——也就是「测试」与「贡献流程」。这两件事看起来一个技术、一个流程，但读完你会发现，它们被同一条暗线串着。先说测试：opencode 用 Bun 自带的测试跑（<span class="mono">bun test</span>），全仓 500 多个测试文件，但有个反直觉的规矩——<strong>测试不能在仓库根目录跑</strong>，根目录的 <span class="mono">test</span> 脚本被故意写成「打印一句『别在根目录跑测试』然后报错退出」。再说贡献：opencode 有一套<strong>异常严格</strong>的流程——必须先开 issue、PR 必须小而专注、标题要遵循约定式提交、还专门立规矩<strong>禁止「AI 生成的长篇大论」</strong>，甚至有一套 vouch 信任名单能把反复灌水的人「除名」。</p>
<p>这一课最值得带走的洞见只有一个，但它能解释上面所有看似零散的规矩：<strong>opencode 的整套测试与贡献规范，都在为同一个目标服务——在 AI 能批量生成代码与文字的时代，<em>死守信噪比、敬重维护者的时间</em></strong>。你品品这些规矩背后的统一意图：「issue 先行」是怕重复劳动、让维护者能提前拦下不合适的方向；「PR 要小而专注 + 说清你怎么验证的」是让审阅者能快速读懂、能复现你的结论；「禁止 AI 长篇大论」「issue 必须用模板、空泛会被自动关」是过滤掉<strong>体量大但信息密度低</strong>的噪声；而 vouch 名单，干脆把「反复提交低质量 AI 贡献」明确列为除名理由。</p>
<p><strong>一个本身就是 AI 编程助手的项目，却在贡献门口竖起最严的牌子：请不要把未经你消化的 AI 产物倾倒给我们。</strong></p>
<p>这不矛盾，恰恰是清醒——AI 是放大器，放大的可以是信号、也可以是噪声，而 opencode 选择用规范死死咬住信号那一端。读懂这条暗线，你就读懂了这一课所有规矩的「为什么」。</p>

<div class="card analogy">
  <div class="tag">📨 生活类比</div>
  把给 opencode 贡献，想象成<strong>给一家以「严谨」著称的学术期刊投稿</strong>。你不能心血来潮写完就塞过去：得<strong>先递一份选题说明（issue）</strong>，让编辑确认这方向值得做、且没人在做（<strong>issue 先行</strong>，免得重复劳动）；正文要<strong>短而聚焦、一篇说清一件事</strong>（<strong>PR 小而专注</strong>），还得写明<strong>你是怎么做实验验证结论的</strong>（<strong>说明如何测试</strong>），好让审稿人能复现；标题得按期刊的<strong>固定格式</strong>写（<strong>约定式提交</strong>）。最关键的是，这家期刊<strong>最痛恨「用 AI 灌出来的、又长又空的稿子」</strong>——它甚至维护一份<strong>作者信誉名单</strong>：踏实的作者被「背书」、反复灌水的被「除名」（<strong>vouch 系统</strong>）。至于<strong>「测试别在根目录跑」</strong>，就像期刊规定「实验数据必须放在<strong>对应章节</strong>、不许堆在封面」——你要是堆错地方，系统会当场<strong>红字报错</strong>提醒你，绝不让你稀里糊涂交上去。
</div>

<h2>测试：从源码验证你的改动</h2>
<p>opencode 用 <strong>Bun 内置的测试跑</strong>器——直接 <span class="mono">bun test</span>，无需额外框架（又一次「一套工具贯穿全程」，同 L62）。全仓有 500 多个 <span class="mono">*.test.ts</span>。但这里有个新手必踩的坑，也是个有意思的设计：<strong>测试不能在仓库根目录跑</strong>。根 <span class="mono">package.json</span> 的 <span class="mono">test</span> 脚本被<strong>故意</strong>写成一句拦路的报错：</p>
<div class="cols">
  <div class="col"><h4>❌ 在根目录跑</h4><p><span class="mono">bun test</span>（根目录）→ 脚本是 <span class="mono">echo 'do not run tests from root' &amp;&amp; exit 1</span>，<strong>当场报错退出</strong>。这是一道<strong>故意设的护栏</strong>。</p></div>
  <div class="col"><h4>✅ 进对应包再跑</h4><p><span class="mono">cd packages/opencode &amp;&amp; bun test</span>。因为这是 <strong>monorepo</strong>，每个包有自己的测试与环境，得在<strong>包目录</strong>里跑才对。</p></div>
</div>
<p>为什么要专门设这道「别在根目录跑」的护栏？因为在 monorepo 里，根目录跑测试要么语义不清、要么会把所有包的测试一锅乱炖，徒增困惑。与其让你跑出一堆莫名其妙的结果，不如<strong>当场用一句响亮的报错拦住你</strong>、并告诉你正确姿势——这正是全书反复见到的「<strong>让用错的姿势立刻、响亮地失败</strong>」（同 L37 stale 工具调用即抛、L48 库非空却无表即抛、L53 Provider 外用 context 即抛）。一个深思熟虑的项目，会把「容易踩的坑」提前变成「踩到就报警」。日常验证你改动的三件套是：</p>
<div class="cellgroup">
  <div class="cel"><b>bun test</b><br>在包目录跑单测（opencode 包还加 <span class="mono">--timeout 30000 --only-failures</span>）</div>
  <div class="cel"><b>tsgo --noEmit</b><br>类型检查（根目录 <span class="mono">bun turbo typecheck</span> 批量跑各包）</div>
  <div class="cel"><b>oxlint</b><br>根目录 <span class="mono">bun lint</span>，超快的 Rust 实现 linter</div>
  <div class="cel"><b>说清「你怎么验证的」</b><br>CONTRIBUTING 要求：非 UI 改动要写明测了什么、审阅者怎么复现</div>
</div>
<p>opencode 对「怎么写测试」也有鲜明态度（见 AGENTS 风格指南）：<strong>尽量别用 mock</strong>、<strong>测真实实现</strong>，而不是把逻辑在测试里再抄一遍。道理很朴素——把逻辑复制进测试，测的其实是「你抄得对不对」，而非「代码对不对」；mock 太多则容易测出「假绿」（mock 都顺，真实环境却崩）。所以 CONTRIBUTING 在「逻辑改动」一节反复强调：<strong>说清你测了什么、审阅者如何复现/确认你的修复</strong>——测试的终点不是「我本地过了」，而是「<strong>别人能照着确认它真的对</strong>」。你看，连「怎么写测试」这件小事，背后都站着同一条暗线：<strong>测试是写给<em>未来要读它、要信它的人</em>看的</strong>，所以要测真东西、要能复现，而不是为了让 CI 那盏灯变绿而糊弄过去。一个测试若只测「自己抄的逻辑」或「自己搭的 mock」，绿灯再亮也是自欺。</p>

<h2>贡献流程：issue 先行，小步快跑</h2>
<p>opencode 的贡献流程，核心一句话：<strong>所有 PR 都必须先有一个 issue</strong>（Issue First Policy）。不是先写代码再补 issue，而是<strong>先开 issue 描述 bug/需求</strong>，让维护者能分诊、避免重复劳动；没关联 issue 的 PR 可能<strong>不经审阅直接关闭</strong>。在 PR 描述里用 <span class="mono">Fixes #123</span>/<span class="mono">Closes #123</span> 关联。整条流程像这样一步步走：</p>
<div class="timeline">
  <div class="tl-item"><div class="tl-dot"></div><b>① 开 issue（用模板）</b>：必须用 Bug report / Feature request / Question 之一，不许空白 issue；自动检查会校验，不合规给你 <strong>2 小时</strong>修改、否则自动关闭</div>
  <div class="tl-item"><div class="tl-dot"></div><b>② 认领</b>：想做就留言，维护者可能指派给你（除非是团队已在做的）</div>
  <div class="tl-item"><div class="tl-dot"></div><b>③ 开分支改</b>：分支名短、≤3 词、连字符，<strong>不要</strong> <span class="mono">feat/</span> 这类前缀；默认分支是 <span class="mono">dev</span></div>
  <div class="tl-item"><div class="tl-dot"></div><b>④ 提 PR</b>：小而专注，标题遵循约定式提交，<strong>说明你怎么验证的</strong>；UI 改动附前后截图</div>
  <div class="tl-item"><div class="tl-dot"></div><b>⑤ 审阅合并</b>：维护者审；UI/核心产品功能须先过设计评审</div>
</div>
<p>这套流程里藏着 opencode 最鲜明的一条文化红线——<strong>「不要 AI 生成的长篇大论」（No AI-Generated Walls of Text）</strong>。CONTRIBUTING 白纸黑字：又长又空的 AI 生成 PR 描述和 issue<strong>不可接受、可能被直接忽略</strong>；请用<strong>你自己的话</strong>简短说清「改了什么、为什么」；<strong>「如果你没法简短说清，可能是你的 PR 太大了」</strong>。连新加功能都要求<strong>先开 issue 做设计对话</strong>、等团队点头，而不是直接甩一个 feature PR。这些规矩看似在「设门槛」，实则在<strong>保护一种稀缺资源：维护者认真阅读的注意力</strong>——这与 L42/L59 反复出现的「注意力稀缺、只留高信号」是同一种智慧，只不过这次守护的是<strong>人</strong>的注意力。这条红线甚至被自动化进了 issue 流程：</p>
<div class="flow">
  <div class="node">提 issue</div>
  <div class="arrow">→</div>
  <div class="node">自动检查<br>是否用模板/有实质内容</div>
  <div class="arrow">→</div>
  <div class="node">不合规<br>评论指出 + 给 2 小时</div>
  <div class="arrow">→</div>
  <div class="node">改好则留；<br>否则<strong>自动关闭</strong></div>
</div>
<p>注意这套自动检查会因什么而<strong>亮红牌</strong>：没用模板、必填项留空或填占位符、<strong>「AI 生成的长篇大论」</strong>、缺乏有意义的内容——几乎每一条都直指「<strong>体量大但信息密度低</strong>」的噪声。在一个本身就是 AI 编程助手的项目里，这种对「未经消化的 AI 产物」的警惕近乎一种宣言：<strong>工具可以帮你生成，但<em>判断与提炼</em>仍是你的责任，别把这份责任连同原始输出一起甩给维护者</strong>。这正是这一课暗线最锋利的一处体现。</p>

<h2>规范与信任：约定 + vouch</h2>
<p>具体的编码与提交规范，opencode 写得很细（AGENTS 风格指南 + CONTRIBUTING）。挑最常用的几条列成一张速查表：</p>
<table class="t">
  <tr><th>维度</th><th>约定</th><th>例 / 备注</th></tr>
  <tr><td>分支名</td><td>短、≤3 词、连字符分隔，<strong>无</strong>斜杠/类型前缀</td><td><span class="mono">session-recovery</span>、<span class="mono">fix-scroll-state</span></td></tr>
  <tr><td>提交 / PR 标题</td><td>约定式：<span class="mono">type(scope): summary</span></td><td>type ∈ feat/fix/docs/chore/refactor/test；scope 如 core/tui/sdk</td></tr>
  <tr><td>控制流</td><td>避免 <span class="mono">else</span>，早返回；<span class="mono">const</span> 不 <span class="mono">let</span></td><td>不可变优先，三元/早返回代替重赋值</td></tr>
  <tr><td>错误处理</td><td>能用 <span class="mono">.catch()</span> 就别 <span class="mono">try/catch</span></td><td>避免 <span class="mono">any</span>；优先精确类型</td></tr>
  <tr><td>导入</td><td><strong>不</strong>别名导入、<strong>不</strong>星号导入</td><td>要命名空间就导出模块自己的命名空间</td></tr>
  <tr><td>运行时</td><td>能用 Bun API 就用</td><td>如 <span class="mono">Bun.file()</span></td></tr>
</table>
<p>这些规范不是凭空立的，它们都指向同一种审美：<strong>代码读起来要像「happy path 一条直线」</strong>——少嵌套（避 else）、少可变状态（避 let）、少例外路径（避 try/catch）、少间接（不别名/星号导入）。规范背后是「让下一个读代码的人省力」，和「贡献流程让审阅者省力」是同构的。最后是 opencode 应对 AI 时代噪声的<strong>终极一招——vouch 信任系统</strong>（信任名单存在 <span class="mono">.github/VOUCHED.td</span>）：</p>
<div class="vflow">
  <div class="vnode"><b>Vouched（已背书）</b>：被明确信任的贡献者</div>
  <div class="vnode"><b>Everyone else（其他所有人）</b>：<strong>无需</strong>背书也能正常开 issue/PR——默认开放，不设墙</div>
  <div class="vnode"><b>Denounced（已除名）</b>：其 issue/PR <strong>自动关闭</strong>；专门留给「反复提交低质量 AI 贡献、灌水、恶意行为」者，<strong>不</strong>用于分歧或诚实的错误</div>
</div>
<p>vouch 系统的精妙在于它的<strong>分寸</strong>：默认对所有人开放（不因你没背书就拒你），只对<strong>反复灌低质量 AI 内容</strong>的人亮红牌，且明确声明「除名不用于意见分歧或诚实的失误」。这是一套既<strong>开放</strong>又<strong>有底线</strong>的信任机制——它不预设你是坏人，但也绝不让少数灌水者拖垮维护者。至此你看清了这一课的全貌：从「测试要在对的地方跑、要测真实实现、要能被他人复现」，到「issue 先行、PR 小而专注、拒绝 AI 长篇」，再到「细致的风格规范 + vouch 信任名单」——<strong>每一条都在同一个方向上用力：在 AI 放大一切的时代，把信号留下，把噪声挡在门外，敬重每一份真正的注意力</strong>。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  这一课讲的是「<strong>把改动验证好、再体面地贡献回去</strong>」的完整链路。<strong>测试</strong>端：Bun 内置 <span class="mono">bun test</span>、<strong>在包目录而非根目录</strong>跑（根目录护栏当场报错）、<strong>测真实实现少用 mock</strong>、并能让审阅者复现。<strong>贡献</strong>端：<strong>issue 先行</strong> → 用模板 → 小而专注的 PR → 约定式标题 → 说清如何验证 → 审阅合并。<strong>规范与信任</strong>端：细致的分支/提交/编码约定，加上 <strong>vouch</strong> 信任名单。把这三端连起来看，你会发现它们共享同一条灵魂——<strong>在 AI 能批量产出的时代，死守信噪比、敬重维护者时间</strong>。这也是一个成熟开源项目最难得的工程文化。
</div>

<div class="card detail">
  <div class="tag">🔬 实现细节</div>
  根 <span class="mono">package.json</span>：<span class="mono">test</span>=<span class="mono">echo 'do not run tests from root' &amp;&amp; exit 1</span>（护栏）、<span class="mono">lint</span>=<span class="mono">oxlint</span>、<span class="mono">typecheck</span>=<span class="mono">bun turbo typecheck</span>、<span class="mono">dev</span>=<span class="mono">bun run --cwd packages/opencode --conditions=browser src/index.ts</span>。<span class="mono">packages/opencode</span> 包：<span class="mono">test</span>=<span class="mono">bun test --timeout 30000 --only-failures</span>、<span class="mono">typecheck</span>=<span class="mono">tsgo --noEmit</span>。Issue 模板在 <span class="mono">.github/ISSUE_TEMPLATE/</span>（<span class="mono">bug-report.yml</span>/<span class="mono">feature-request.yml</span>/<span class="mono">question.yml</span>/<span class="mono">config.yml</span>），自动检查不合规给 2 小时窗口。Vouch 名单 <span class="mono">.github/VOUCHED.td</span>，维护者用评论 <span class="mono">vouch</span>/<span class="mono">denounce</span>/<span class="mono">unvouch</span> 管理，自动提交。新增 provider 通常<strong>无需改码</strong>，去 <span class="mono">models.dev</span> 提 PR 即可。默认分支 <span class="mono">dev</span>（本地可能没有 <span class="mono">main</span>，对比用 <span class="mono">origin/dev</span>）。
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>测试：在对的地方、测真东西、能被复现</strong>。Bun 内置 <span class="mono">bun test</span>；<strong>不能在根目录跑</strong>（根 <span class="mono">test</span> 脚本故意报错退出——monorepo 护栏，同 L37/L48/L53「用错即响亮失败」），要 <span class="mono">cd</span> 进包目录。<strong>少用 mock、测真实实现</strong>（别把逻辑抄进测试）；CONTRIBUTING 要求逻辑改动<strong>说清测了什么、审阅者如何复现</strong>。配 <span class="mono">tsgo</span> 类型检查 + <span class="mono">oxlint</span>。</li>
    <li><strong>贡献：issue 先行，小步快跑</strong>。所有 PR 必须先有 issue（<span class="mono">Fixes #123</span>），用模板（不合规 2 小时后自动关）；分支名短≤3 词无前缀、默认分支 <span class="mono">dev</span>；PR 小而专注、约定式标题、<strong>说明如何验证</strong>。文化红线：<strong>拒绝 AI 长篇大论</strong>，用自己的话简短说清（说不清=PR 太大）——守护维护者注意力（同 L42/L59 信号稀缺）。</li>
    <li><strong>规范与信任：约定 + vouch</strong>。风格指向「happy path 直线」：避 <span class="mono">else</span>/<span class="mono">let</span>、能 <span class="mono">.catch</span> 不 <span class="mono">try/catch</span>、避 <span class="mono">any</span>、不别名/星号导入、用 Bun API。<strong>vouch 信任名单</strong>（<span class="mono">.github/VOUCHED.td</span>）默认对所有人开放、只对反复灌低质量 AI 内容者除名。<strong>暗线</strong>：整套规范都为「AI 时代死守信噪比、敬重维护者时间」服务。</li>
  </ul>
</div>
""",
    "en": r"""<p class="lead">Last lesson you learned to <strong>run, build, and debug</strong> opencode. This lesson is the final touch: <strong>how do you verify your change is correct, and how do you contribute it back?</strong>—that is, "testing" and "the contribution process." These two look like one's technical and one's procedural, but by the end you'll find they're threaded by the same hidden line. First, testing: opencode runs tests with Bun's built-in runner (<span class="mono">bun test</span>), 500-plus test files repo-wide, but with a counterintuitive rule—<strong>tests cannot run at the repo root</strong>, where the <span class="mono">test</span> script is deliberately written to "print 'do not run tests from root' and exit with an error." Next, contributing: opencode has an <strong>unusually strict</strong> process—you must open an issue first, PRs must be small and focused, titles must follow conventional commits, there's even an explicit rule <strong>forbidding "AI-generated walls of text,"</strong> and a vouch trust list that can "denounce" repeat spammers.</p>
<p>There's only one insight worth taking away, but it explains every seemingly-scattered rule above: <strong>opencode's entire testing and contribution norms serve one goal—in an age where AI can mass-produce code and text, <em>fiercely guarding the signal-to-noise ratio and respecting maintainers' time</em></strong>. Savor the unified intent behind these rules: "issue first" guards against duplicate work and lets maintainers head off unfit directions early; "PRs small and focused + explain how you verified" lets reviewers quickly grasp and reproduce your conclusion; "no AI walls of text" and "issues must use a template, vague ones auto-close" filter out <strong>high-volume, low-density</strong> noise; and the vouch list flatly names "repeatedly submitting low-quality AI contributions" as grounds for denouncement. </p>
<p><strong>A project that is itself an AI coding agent nonetheless plants the strictest sign at its contribution gate: please don't dump undigested AI output on us.</strong> </p>
<p>This isn't a contradiction, it's clear-headedness—AI is an amplifier, and what it amplifies can be signal or noise; opencode chooses, via its norms, to clamp hard onto the signal end. Understand this hidden line and you understand the "why" of every rule in this lesson.</p>

<div class="card analogy">
  <div class="tag">📨 Analogy</div>
  Picture contributing to opencode as <strong>submitting to an academic journal famed for "rigor."</strong> You can't just write on a whim and shove it over: you must <strong>first submit a topic proposal (an issue)</strong>, letting the editor confirm the direction is worthwhile and unclaimed (<strong>issue first</strong>, to avoid duplicate work); the body must be <strong>short and focused, one paper making one point</strong> (<strong>PR small and focused</strong>), and must state <strong>how you experimentally verified the conclusion</strong> (<strong>explain how you tested</strong>) so reviewers can reproduce it; the title must follow the journal's <strong>fixed format</strong> (<strong>conventional commits</strong>). Most crucially, this journal <strong>despises "long, hollow AI-stuffed manuscripts"</strong>—it even maintains an <strong>author reputation list</strong>: solid authors get "vouched," repeat spammers get "denounced" (<strong>the vouch system</strong>). As for <strong>"don't run tests at the root,"</strong> it's like the journal ruling "experimental data must go in the <strong>corresponding section</strong>, not piled on the cover"—pile it in the wrong place and the system gives you an on-the-spot <strong>red-letter error</strong>, never letting you submit it muddled.
</div>

<h2>Testing: verify your change from the source</h2>
<p>opencode runs tests with <strong>Bun's built-in test runner</strong>—just <span class="mono">bun test</span>, no extra framework (again "one tool spanning the whole thing," like L62). The repo has 500-plus <span class="mono">*.test.ts</span>. But here's a pitfall every newcomer hits, and an interesting design: <strong>tests can't run at the repo root</strong>. The root <span class="mono">package.json</span>'s <span class="mono">test</span> script is <strong>deliberately</strong> written as a blocking error:</p>
<div class="cols">
  <div class="col"><h4>❌ Run at the root</h4><p><span class="mono">bun test</span> (root) → the script is <span class="mono">echo 'do not run tests from root' &amp;&amp; exit 1</span>, <strong>erroring out on the spot</strong>. This is a <strong>deliberate guardrail</strong>.</p></div>
  <div class="col"><h4>✅ Enter the package, then run</h4><p><span class="mono">cd packages/opencode &amp;&amp; bun test</span>. Because this is a <strong>monorepo</strong>, each package has its own tests and environment, so you must run in the <strong>package directory</strong>.</p></div>
</div>
<p>Why set this "don't run at the root" guardrail specifically? Because in a monorepo, running tests at the root is either semantically unclear or stews all packages' tests into one pot, adding only confusion. Rather than let you produce a heap of baffling results, it's better to <strong>block you on the spot with a loud error</strong> and tell you the right posture—exactly the "<strong>let the wrong usage fail immediately and loudly</strong>" seen throughout the book (like L37 throwing on a stale tool call, L48 throwing when the DB is non-empty but lacks the table, L53 throwing when a context is used outside its Provider). A thoughtful project turns "easy-to-hit pitfalls" into "trips-an-alarm-on-contact" ahead of time. The daily trio for verifying your change:</p>
<div class="cellgroup">
  <div class="cel"><b>bun test</b><br>run unit tests in the package dir (the opencode package also adds <span class="mono">--timeout 30000 --only-failures</span>)</div>
  <div class="cel"><b>tsgo --noEmit</b><br>type check (root <span class="mono">bun turbo typecheck</span> runs all packages in batch)</div>
  <div class="cel"><b>oxlint</b><br>root <span class="mono">bun lint</span>, a blazing-fast Rust-implemented linter</div>
  <div class="cel"><b>Explain "how you verified"</b><br>CONTRIBUTING requires: non-UI changes must state what was tested and how a reviewer reproduces it</div>
</div>
<p>opencode also has a clear stance on "how to write tests" (see the AGENTS style guide): <strong>avoid mocks as much as possible</strong>, <strong>test the real implementation</strong>, rather than copying the logic into the test again. The reasoning is plain—copy the logic into a test and you're really testing "whether you copied it right," not "whether the code is right"; too many mocks easily produce "fake green" (mocks all pass, the real environment crashes). So CONTRIBUTING's "Logic Changes" section repeatedly stresses: <strong>spell out what you tested, and how a reviewer reproduces/confirms your fix</strong>—the endpoint of testing isn't "it passed on my machine" but "<strong>someone else can follow along and confirm it's truly correct</strong>." See, even the small matter of "how to write tests" stands on the same hidden line: <strong>a test is written for <em>whoever will read and trust it in the future</em></strong>, so it must test real things and be reproducible, not fudged just to turn that CI light green. A test that only tests "the logic you copied" or "the mock you built" is self-deception, however bright the green.</p>

<h2>The contribution process: issue first, small steps</h2>
<p>opencode's contribution process, in one sentence: <strong>every PR must have an issue first</strong> (the Issue First Policy). Not code-first-then-backfill-an-issue, but <strong>open an issue describing the bug/feature first</strong>, so maintainers can triage and avoid duplicate work; a PR without a linked issue may be <strong>closed without review</strong>. In the PR description, link it with <span class="mono">Fixes #123</span>/<span class="mono">Closes #123</span>. The whole process steps through like this:</p>
<div class="timeline">
  <div class="tl-item"><div class="tl-dot"></div><b>① Open an issue (with a template)</b>: must use one of Bug report / Feature request / Question, no blank issues; an automated check validates it, and non-compliance gives you <strong>2 hours</strong> to fix or it auto-closes</div>
  <div class="tl-item"><div class="tl-dot"></div><b>② Claim it</b>: comment if you want to take it, and a maintainer may assign it to you (unless the team's already on it)</div>
  <div class="tl-item"><div class="tl-dot"></div><b>③ Branch and change</b>: branch names short, ≤3 words, hyphenated, <strong>no</strong> <span class="mono">feat/</span>-style prefix; the default branch is <span class="mono">dev</span></div>
  <div class="tl-item"><div class="tl-dot"></div><b>④ Open a PR</b>: small and focused, title following conventional commits, <strong>explain how you verified it</strong>; UI changes include before/after screenshots</div>
  <div class="tl-item"><div class="tl-dot"></div><b>⑤ Review and merge</b>: maintainers review; UI/core product features must pass design review first</div>
</div>
<p>Hidden in this process is opencode's most vivid cultural red line—<strong>"No AI-Generated Walls of Text."</strong> CONTRIBUTING says it in black and white: long, hollow AI-generated PR descriptions and issues are <strong>unacceptable and may be ignored</strong>; please use <strong>your own words</strong> to briefly state "what changed and why"; <strong>"if you can't explain it briefly, your PR might be too large."</strong> Even new functionality is required to <strong>open an issue for a design conversation first</strong> and wait for the team's nod, rather than flinging a feature PR directly. These rules look like "setting a bar," but really they <strong>protect a scarce resource: the maintainers' attention for careful reading</strong>—the same wisdom as the "attention is scarce, keep only high signal" recurring in L42/L59, except this time what's guarded is <strong>human</strong> attention. This red line is even automated into the issue process:</p>
<div class="flow">
  <div class="node">open issue</div>
  <div class="arrow">→</div>
  <div class="node">auto-check<br>template used / has substance</div>
  <div class="arrow">→</div>
  <div class="node">non-compliant<br>comment + 2-hour window</div>
  <div class="arrow">→</div>
  <div class="node">fixed → kept;<br>else <strong>auto-closed</strong></div>
</div>
<p>Note what makes this auto-check <strong>throw a red flag</strong>: not using a template, required fields left empty or filled with placeholder text, <strong>"AI-generated walls of text,"</strong> missing meaningful content—nearly every one points straight at <strong>high-volume, low-density</strong> noise. In a project that is itself an AI coding agent, this wariness toward "undigested AI output" is nearly a manifesto: <strong>the tool can help you generate, but <em>judgment and distillation</em> remain your responsibility; don't fling that responsibility, along with the raw output, at the maintainers</strong>. This is the sharpest expression of the lesson's hidden line.</p>

<h2>Norms and trust: conventions + vouch</h2>
<p>The concrete coding and commit norms, opencode writes in fine detail (the AGENTS style guide + CONTRIBUTING). Here are the most-used few as a cheat sheet:</p>
<table class="t">
  <tr><th>Dimension</th><th>Convention</th><th>Example / note</th></tr>
  <tr><td>Branch name</td><td>short, ≤3 words, hyphen-separated, <strong>no</strong> slash/type prefix</td><td><span class="mono">session-recovery</span>, <span class="mono">fix-scroll-state</span></td></tr>
  <tr><td>Commit / PR title</td><td>conventional: <span class="mono">type(scope): summary</span></td><td>type ∈ feat/fix/docs/chore/refactor/test; scope like core/tui/sdk</td></tr>
  <tr><td>Control flow</td><td>avoid <span class="mono">else</span>, early return; <span class="mono">const</span> not <span class="mono">let</span></td><td>immutable-first, ternary/early-return over reassignment</td></tr>
  <tr><td>Error handling</td><td>prefer <span class="mono">.catch()</span> over <span class="mono">try/catch</span></td><td>avoid <span class="mono">any</span>; prefer precise types</td></tr>
  <tr><td>Imports</td><td><strong>no</strong> aliased imports, <strong>no</strong> star imports</td><td>for a namespace, import the module's own exported namespace</td></tr>
  <tr><td>Runtime</td><td>use Bun APIs when they fit</td><td>e.g. <span class="mono">Bun.file()</span></td></tr>
</table>
<p>These norms aren't set arbitrarily; they all point to one aesthetic: <strong>code should read like "the happy path, one straight line"</strong>—less nesting (avoid else), less mutable state (avoid let), fewer exceptional paths (avoid try/catch), less indirection (no aliased/star imports). Behind the norms is "make it easy for the next person reading the code," isomorphic to "the contribution process makes it easy for reviewers." Finally, opencode's <strong>ultimate move against AI-age noise—the vouch trust system</strong> (the trust list lives in <span class="mono">.github/VOUCHED.td</span>):</p>
<div class="vflow">
  <div class="vnode"><b>Vouched</b>: explicitly trusted contributors</div>
  <div class="vnode"><b>Everyone else</b>: can open issues/PRs normally <strong>without</strong> being vouched—open by default, no wall</div>
  <div class="vnode"><b>Denounced</b>: their issues/PRs <strong>auto-close</strong>; reserved for those who "repeatedly submit low-quality AI contributions, spam, or act in bad faith," <strong>not</strong> for disagreements or honest mistakes</div>
</div>
<p>The vouch system's elegance is in its <strong>proportion</strong>: open to everyone by default (it won't reject you for not being vouched), red-flagging only those who <strong>repeatedly pour in low-quality AI content</strong>, while explicitly stating "denouncement is not for disagreements or honest mistakes." It's a trust mechanism both <strong>open</strong> and with a <strong>bottom line</strong>—it doesn't presume you're a bad actor, yet never lets a spamming few drag down the maintainers. By now you see the lesson whole: from "tests must run in the right place, test the real implementation, and be reproducible by others," to "issue first, PRs small and focused, no AI walls," to "meticulous style norms + the vouch trust list"—<strong>every single one pushes in the same direction: in an age where AI amplifies everything, keep the signal, hold the noise at the gate, and respect every bit of genuine attention</strong>.</p>

<div class="card macro">
  <div class="tag">🗺️ Big picture</div>
  This lesson covers the full chain of "<strong>verify your change well, then contribute it back gracefully</strong>." On the <strong>testing</strong> end: Bun's built-in <span class="mono">bun test</span>, run <strong>in the package dir, not the root</strong> (the root guardrail errors on the spot), <strong>test the real implementation, few mocks</strong>, and reproducible by reviewers. On the <strong>contribution</strong> end: <strong>issue first</strong> → use a template → a small focused PR → conventional title → explain how you verified → review and merge. On the <strong>norms and trust</strong> end: meticulous branch/commit/coding conventions, plus the <strong>vouch</strong> trust list. Connect these three ends and you find they share one soul—<strong>in an age where AI can mass-produce, fiercely guard the signal-to-noise ratio and respect maintainers' time</strong>. This is the rarest engineering culture of a mature open-source project.
</div>

<div class="card detail">
  <div class="tag">🔬 Implementation details</div>
  Root <span class="mono">package.json</span>: <span class="mono">test</span>=<span class="mono">echo 'do not run tests from root' &amp;&amp; exit 1</span> (guardrail), <span class="mono">lint</span>=<span class="mono">oxlint</span>, <span class="mono">typecheck</span>=<span class="mono">bun turbo typecheck</span>, <span class="mono">dev</span>=<span class="mono">bun run --cwd packages/opencode --conditions=browser src/index.ts</span>. The <span class="mono">packages/opencode</span> package: <span class="mono">test</span>=<span class="mono">bun test --timeout 30000 --only-failures</span>, <span class="mono">typecheck</span>=<span class="mono">tsgo --noEmit</span>. Issue templates in <span class="mono">.github/ISSUE_TEMPLATE/</span> (<span class="mono">bug-report.yml</span>/<span class="mono">feature-request.yml</span>/<span class="mono">question.yml</span>/<span class="mono">config.yml</span>), the auto-check gives a 2-hour window on non-compliance. The vouch list <span class="mono">.github/VOUCHED.td</span>, maintainers manage it via comments <span class="mono">vouch</span>/<span class="mono">denounce</span>/<span class="mono">unvouch</span>, committed automatically. Adding a provider usually needs <strong>no code change</strong>—just open a PR at <span class="mono">models.dev</span>. The default branch is <span class="mono">dev</span> (locally there may be no <span class="mono">main</span>; diff against <span class="mono">origin/dev</span>).
</div>

<div class="card key">
  <div class="tag">🎯 Key points</div>
  <ul>
    <li><strong>Testing: in the right place, test real things, reproducible</strong>. Bun's built-in <span class="mono">bun test</span>; <strong>can't run at the root</strong> (the root <span class="mono">test</span> script deliberately errors out—a monorepo guardrail, like L37/L48/L53 "wrong usage fails loudly"), <span class="mono">cd</span> into the package dir. <strong>Few mocks, test the real implementation</strong> (don't copy logic into tests); CONTRIBUTING requires logic changes to <strong>spell out what was tested and how a reviewer reproduces it</strong>. Pair with <span class="mono">tsgo</span> type check + <span class="mono">oxlint</span>.</li>
    <li><strong>Contributing: issue first, small steps</strong>. Every PR must have an issue first (<span class="mono">Fixes #123</span>), using a template (auto-closes 2 hours after non-compliance); branch names short ≤3 words no prefix, default branch <span class="mono">dev</span>; PRs small and focused, conventional titles, <strong>explain how you verified</strong>. Cultural red line: <strong>reject AI walls of text</strong>, state it briefly in your own words (can't = PR too large)—guarding maintainers' attention (like L42/L59 scarce signal).</li>
    <li><strong>Norms and trust: conventions + vouch</strong>. Style points toward "the happy path, a straight line": avoid <span class="mono">else</span>/<span class="mono">let</span>, prefer <span class="mono">.catch</span> over <span class="mono">try/catch</span>, avoid <span class="mono">any</span>, no aliased/star imports, use Bun APIs. The <strong>vouch trust list</strong> (<span class="mono">.github/VOUCHED.td</span>) is open to everyone by default, denouncing only those who repeatedly pour in low-quality AI content. <strong>Hidden line</strong>: the whole norm set serves "in the AI age, fiercely guard the signal-to-noise ratio and respect maintainers' time."</li>
  </ul>
</div>
""",
}

LESSON_64 = {
    "zh": r"""<p class="lead">恭喜你走到了最后一课。前面 63 课，我们从「opencode 是什么」一路拆到「怎么给它贡献代码」——地基（Effect）、骨架（客户端/服务器）、主循环（Session 与 agent loop）、记忆（Context Epoch 系统）、嘴巴（LLM 协议）、双手（工具）、配置、持久化、界面（TUI）、扩展、实战。这一课不引入新机制，而是做两件收尾的事：<strong>一张把全书概念串起来的「概念地图」</strong>，和<strong>一份能跳回每一课的「术语速查表」</strong>。它既是复习、也是索引——当你日后读 opencode 源码、忘了某个词是什么意思，回到这里一查、点链接跳回那一课即可。</p>
<p>而这一课本身，也藏着一个<strong>值得带走的洞见</strong>：<strong>精确、共享的词汇表，本身就是一种工程工具</strong>。opencode 源码根部的 <span class="mono">CONTEXT.md</span> 专门有一节 <span class="mono">Language</span>，像字典一样给每个核心概念下定义，甚至明确写出「<strong>不要叫它什么</strong>」——比如「System Context」旁注「_Avoid_: System prompt」、「Session History」旁注「_Avoid_: Session Context」。为什么一个代码项目要如此较真用词？因为<strong>当一个团队（如今还包括 AI 协作者）共享一套精确、无歧义的词汇时，沟通的损耗、误解的 bug、来回的澄清，都会大幅减少</strong>。给概念起一个好名字、并坚持只用这个名字，是把复杂系统讲清楚的第一步——这本可视化指南做的，本质上也是同一件事。所以这份术语表不只是「附录」，它是 opencode「用词即设计」哲学的延续。</p>

<h2>概念地图：从地基到表面，层层垒起</h2>
<p>opencode 这套系统，是<strong>自底向上</strong>垒起来的：每一层都站在下一层的肩膀上。理解了这张依赖图，你就有了一张「该先读哪、再读哪」的路线图——下层是上层的地基，越往上越接近你眼睛看到的界面：</p>
<div class="flow">
  <div class="node"><b>地基</b><br>Effect（M2）<br><span class="mono">DI / Fiber / 错误即值</span></div>
  <div class="arrow">→</div>
  <div class="node"><b>骨架</b><br>客户端/服务器（M3）<br><span class="mono">Hono · SSE · SDK</span></div>
  <div class="arrow">→</div>
  <div class="node"><b>主循环</b><br>Session（M4）<br><span class="mono">agent loop · 工具调用</span></div>
  <div class="arrow">→</div>
  <div class="node"><b>记忆</b><br>Context Epoch（M5）<br><span class="mono">系统上下文的真源</span></div>
</div>
<div class="flow">
  <div class="node"><b>嘴巴</b><br>LLM 协议（M6）<br><span class="mono">多家 provider 归一</span></div>
  <div class="arrow">→</div>
  <div class="node"><b>双手</b><br>工具（M7）<br><span class="mono">Tool.make · 权限</span></div>
  <div class="arrow">→</div>
  <div class="node"><b>装配</b><br>配置/持久化（M8–9）<br><span class="mono">agents · SQLite</span></div>
  <div class="arrow">→</div>
  <div class="node"><b>表面</b><br>TUI/扩展（M10–11）<br><span class="mono">opentui · 插件 · LSP</span></div>
</div>
<p>这条「地基→骨架→主循环→记忆→嘴巴→双手→装配→表面」的链路，正是本书 12 个部分的组织顺序，也是 opencode 代码本身的依赖方向。一个新读者若问「我该从哪读起」，答案就在这张图里：<strong>从最左边的地基开始，因为上层的一切都建立在它之上</strong>。</p>

<h2>术语速查表：全书关键概念一句话 + 跳转</h2>
<p>下表按 12 个部分组织，每个核心术语给一句话定义，并链接回详讲它的那一课（点击即跳）。这是你日后查阅的主入口。</p>
<table class="t">
  <tr><th>术语</th><th>一句话</th><th>详见</th></tr>
  <tr><td><b>opencode</b></td><td>一个开源的 AI 编程 agent：客户端/服务器架构、可在终端/Web/桌面/编辑器里用</td><td><a href="01-what-is-opencode.html">L01</a></td></tr>
  <tr><td><b>Effect</b></td><td>贯穿全栈的函数式效果系统：把「副作用、依赖、错误」都变成可组合的值</td><td><a href="05-why-effect.html">L05</a></td></tr>
  <tr><td><b>Layer / Context（DI）</b></td><td>Effect 的依赖注入：用 Layer 装配服务、用 Context 索取依赖</td><td><a href="06-context-layer.html">L06</a></td></tr>
  <tr><td><b>Fiber</b></td><td>Effect 的轻量并发单元：可结构化地派生、中断、汇合</td><td><a href="07-concurrency-primitives.html">L07</a></td></tr>
  <tr><td><b>Server（Hono）</b></td><td>opencode 内核跑成一个本地 HTTP 服务器，TUI 等都是它的客户端</td><td><a href="09-server-overview.html">L09</a></td></tr>
  <tr><td><b>Event Bus（SSE）</b></td><td>服务器经 Server-Sent Events 把事件流推给客户端</td><td><a href="11-event-bus.html">L11</a></td></tr>
  <tr><td><b>Session / Message / Part</b></td><td>会话的三层数据模型：会话含消息、消息含片段（文本/工具/文件…）</td><td><a href="14-session-messages-parts.html">L14</a></td></tr>
  <tr><td><b>Agent Loop</b></td><td>「问模型→执行工具→把结果喂回→再问」的主循环</td><td><a href="17-agent-loop.html">L17</a></td></tr>
  <tr><td><b>Projected History</b></td><td>每轮 provider 调用前，从持久数据「投影」出的那份会话历史</td><td><a href="19-projected-history.html">L19</a></td></tr>
  <tr><td><b>System Context</b></td><td>呈给模型的结构化上下文事实集合（_勿称_ system prompt）</td><td><a href="21-system-context.html">L21</a></td></tr>
  <tr><td><b>Context Source</b></td><td>System Context 里一个独立观测的带类型值（稳定 key + 编解码 + 渲染器）</td><td><a href="22-context-source.html">L22</a></td></tr>
  <tr><td><b>Context Epoch</b></td><td>一份基线 System Context 保持不变的时间段，至压缩或基线替换才结束</td><td><a href="24-context-epoch.html">L24</a></td></tr>
  <tr><td><b>LLM 协议适配器</b></td><td>把 Anthropic/OpenAI/Gemini 等各家协议归一成统一内部表示</td><td><a href="29-protocol-adapters.html">L29</a></td></tr>
  <tr><td><b>Model Resolution</b></td><td>把「provider/模型名」解析成可调用的具体模型与传输</td><td><a href="35-model-resolution.html">L35</a></td></tr>
  <tr><td><b>Tool.make</b></td><td>定义工具的统一模子：名字 + 参数 schema + execute</td><td><a href="36-tool-definition.html">L36</a></td></tr>
  <tr><td><b>Permissions</b></td><td>工具执行前的策略门：ask/allow/deny（_后者胜_ 的 findLast）</td><td><a href="41-permissions.html">L41</a></td></tr>
  <tr><td><b>Skills</b></td><td>把「一组提示词+工具+规则」打包成可复用的技能</td><td><a href="43-skills.html">L43</a></td></tr>
  <tr><td><b>Agents（build/plan）</b></td><td>同一内核的不同「权限画像」：build 能写、plan 只读</td><td><a href="45-agents.html">L45</a></td></tr>
  <tr><td><b>MCP</b></td><td>Model Context Protocol：动态接入外部作用域工具（含 OAuth）</td><td><a href="46-mcp.html">L46</a></td></tr>
  <tr><td><b>Provider Plugin（IoC）</b></td><td>内核用控制反转让 provider 插件自登记装配（<span class="mono">PluginV2.define</span>）</td><td><a href="47-provider-plugins.html">L47</a></td></tr>
  <tr><td><b>Drizzle / SQLite</b></td><td>代码即 schema 的持久化：会话/消息存在本地 SQLite</td><td><a href="48-drizzle-sqlite.html">L48</a></td></tr>
  <tr><td><b>Compaction / Snapshot / Revert</b></td><td>记忆管理：压缩历史、影子 git 快照、回退</td><td><a href="51-compaction-snapshots.html">L51</a></td></tr>
  <tr><td><b>opentui</b></td><td>把 SolidJS 渲染到终端的「终端里的浏览器」</td><td><a href="52-opentui.html">L52</a></td></tr>
  <tr><td><b>frecency</b></td><td>frequency+recency 的排序公式：<span class="mono">freq/(1+天数)</span></td><td><a href="55-prompt-component.html">L55</a></td></tr>
  <tr><td><b>Plugin / Hooks</b></td><td>外部插件 = 返回 Hooks 的函数；trigger 传草稿、插件层层涂改</td><td><a href="57-plugin-system.html">L57</a></td></tr>
  <tr><td><b>LSP（客户端）</b></td><td>opencode 当 LSP 客户端，借来整个 IDE 语言服务器生态</td><td><a href="59-lsp.html">L59</a></td></tr>
  <tr><td><b>PTY</b></td><td>给交互式程序一个真终端；环境「可定制在中间、不可妥协在最后」</td><td><a href="60-pty-shell.html">L60</a></td></tr>
  <tr><td><b>ACP / Location</b></td><td>opencode 当 ACP 服务器（LSP 的镜像）；Location 解耦「会话」与「在哪儿跑」</td><td><a href="61-acp-location.html">L61</a></td></tr>
  <tr><td><b>EventV2 / 单写入 sync</b></td><td>持久事件溯源 + 单写入者 + 单调 seq；多端从游标重放追平</td><td><a href="65-event-sourcing-sync.html">L65</a></td></tr>
  <tr><td><b>斜杠命令</b></td><td>参数化 prompt 模板；命令/MCP/skill 三源塑成同一个 Info</td><td><a href="66-slash-commands.html">L66</a></td></tr>
  <tr><td><b>http-recorder</b></td><td>把真实 LLM 往返录成磁带、回放，让非确定循环可测（含脱敏）</td><td><a href="67-http-recorder.html">L67</a></td></tr>
  <tr><td><b>设备码 OAuth / 凭据库</b></td><td>CLI 无回调的设备码登录；OAuth\|Key 统一进凭据库</td><td><a href="68-account-auth.html">L68</a></td></tr>
  <tr><td><b>生态 / Durable Object</b></td><td>一个 server、多副面孔；分享经 Cloudflare Durable Object 云同步</td><td><a href="69-ecosystem-tour.html">L69</a></td></tr>
</table>

<h2>读完之后：opencode 教给你的「可迁移智慧」</h2>
<p>这本书真正想留给你的，不是 64 课的零散知识点，而是几条<strong>跨越具体技术、能迁移到你自己项目</strong>的设计智慧。它们在全书反复出现、彼此印证。最后用一张表把它们收拢，并各指一两课作为「最佳范例」，方便你日后回味：</p>
<table class="t">
  <tr><th>可迁移智慧</th><th>一句话</th><th>范例课</th></tr>
  <tr><td><b>复用成熟生态</b></td><td>能借就不自造：搜索借 Ripgrep、版本控制借 git、语言智能借 LSP、编译借 Bun</td><td><a href="39-search-exec-tools.html">L39</a> · <a href="59-lsp.html">L59</a></td></tr>
  <tr><td><b>编辑一份草稿</b></td><td>传一份可变草稿让各方层层涂改，比约定复杂的返回值合并更可组合</td><td><a href="54-events-to-store.html">L54</a> · <a href="58-plugin-hooks.html">L58</a></td></tr>
  <tr><td><b>找准接缝</b></td><td>切开「会变的」与「不变的」：核心 vs provider、数据 vs 表现、是什么 vs 在哪里</td><td><a href="47-provider-plugins.html">L47</a> · <a href="61-acp-location.html">L61</a></td></tr>
  <tr><td><b>用错即响亮失败</b></td><td>把易踩的坑提前变成「踩到就报警」，而非埋成远处的诡异 bug</td><td><a href="37-tool-registry.html">L37</a> · <a href="63-test-contribute.html">L63</a></td></tr>
  <tr><td><b>注意力是稀缺资源</b></td><td>无论模型还是维护者，注意力都有限——只留高信号，挡住噪声</td><td><a href="42-bounded-output.html">L42</a> · <a href="63-test-contribute.html">L63</a></td></tr>
  <tr><td><b>统一模子刻同形</b></td><td>一个谁都顺手用的模子（Tool.make/createSimpleContext/Plugin），让正确成为最省力</td><td><a href="36-tool-definition.html">L36</a> · <a href="53-tui-structure.html">L53</a></td></tr>
</table>
<p>如果你只带走一句话，那就让它是这个：<strong>opencode 之所以能在「AI agent」这个快速演化、充满不确定的领域里保持清晰，靠的不是更聪明的技巧，而是反复地「找准接缝、复用成熟、让正确省力、为未知留门」</strong>。这些智慧不属于 opencode，它们属于一切想把复杂系统做扎实的工程师——也包括正在读这本书的你。至此，全书核心 12 部分 64 课、连同进阶专题（第 13 部分 · L65–69）共 <strong>69 课</strong>圆满收尾。愿你带着这张地图，去读源码、去改它、去贡献，或者，去建造你自己的东西。</p>
""",
    "en": r"""<p class="lead">Congratulations on reaching the final lesson. Over the previous 63 lessons, we took apart everything from "what opencode is" all the way to "how to contribute code to it"—the foundation (Effect), the skeleton (client/server), the main loop (Session and the agent loop), memory (the Context Epoch system), the mouth (the LLM protocol), the hands (tools), config, persistence, the interface (TUI), extensions, and practice. This lesson introduces no new mechanism; it does two closing things: <strong>one "concept map" threading the whole book's concepts together</strong>, and <strong>one "glossary cheat sheet" that jumps back to every lesson</strong>. It's both review and index—when you later read opencode source and forget what some term means, come back here, look it up, and click the link to jump back to that lesson.</p>
<p>And this lesson itself hides an <strong>insight worth taking away</strong>: <strong>a precise, shared vocabulary is itself an engineering tool</strong>. opencode's root <span class="mono">CONTEXT.md</span> has a dedicated <span class="mono">Language</span> section that, like a dictionary, defines each core concept, even spelling out "<strong>what NOT to call it</strong>"—e.g. "System Context" annotated "_Avoid_: System prompt," "Session History" annotated "_Avoid_: Session Context." Why would a code project be so fussy about wording? Because <strong>when a team (now including AI collaborators) shares one precise, unambiguous vocabulary, communication loss, misunderstanding bugs, and back-and-forth clarification all drop sharply</strong>. Giving a concept a good name and insisting on only that name is the first step to explaining a complex system clearly—and what this visual guide does is, in essence, the same thing. So this glossary isn't merely an "appendix"; it's a continuation of opencode's "wording is design" philosophy.</p>

<h2>Concept map: from foundation to surface, stacked layer by layer</h2>
<p>opencode's system is built <strong>bottom-up</strong>: each layer stands on the shoulders of the one below. Understand this dependency graph and you have a "what to read first, then next" roadmap—the lower is the foundation of the upper, and the higher you go the closer you get to the interface your eyes see:</p>
<div class="flow">
  <div class="node"><b>Foundation</b><br>Effect (M2)<br><span class="mono">DI / Fiber / errors-as-values</span></div>
  <div class="arrow">→</div>
  <div class="node"><b>Skeleton</b><br>client/server (M3)<br><span class="mono">Hono · SSE · SDK</span></div>
  <div class="arrow">→</div>
  <div class="node"><b>Main loop</b><br>Session (M4)<br><span class="mono">agent loop · tool calls</span></div>
  <div class="arrow">→</div>
  <div class="node"><b>Memory</b><br>Context Epoch (M5)<br><span class="mono">source of truth for context</span></div>
</div>
<div class="flow">
  <div class="node"><b>Mouth</b><br>LLM protocol (M6)<br><span class="mono">many providers unified</span></div>
  <div class="arrow">→</div>
  <div class="node"><b>Hands</b><br>tools (M7)<br><span class="mono">Tool.make · permissions</span></div>
  <div class="arrow">→</div>
  <div class="node"><b>Assembly</b><br>config/persistence (M8–9)<br><span class="mono">agents · SQLite</span></div>
  <div class="arrow">→</div>
  <div class="node"><b>Surface</b><br>TUI/extensions (M10–11)<br><span class="mono">opentui · plugins · LSP</span></div>
</div>
<p>This "foundation → skeleton → main loop → memory → mouth → hands → assembly → surface" chain is exactly the order of the book's 12 parts, and also the dependency direction of opencode's own code. If a new reader asks "where should I start," the answer is in this graph: <strong>start from the leftmost foundation, because everything above is built on it</strong>.</p>

<h2>Glossary cheat sheet: one line per key concept + a jump</h2>
<p>The table below is organized by the 12 parts; each core term gets a one-line definition and links back to the lesson that covers it in depth (click to jump). This is your main entry point for future lookups.</p>
<table class="t">
  <tr><th>Term</th><th>One line</th><th>See</th></tr>
  <tr><td><b>opencode</b></td><td>An open-source AI coding agent: client/server architecture, usable in terminal/Web/desktop/editors</td><td><a href="01-what-is-opencode.html">L01</a></td></tr>
  <tr><td><b>Effect</b></td><td>A full-stack functional effect system: turns "side effects, dependencies, errors" all into composable values</td><td><a href="05-why-effect.html">L05</a></td></tr>
  <tr><td><b>Layer / Context (DI)</b></td><td>Effect's dependency injection: assemble services with Layer, request dependencies via Context</td><td><a href="06-context-layer.html">L06</a></td></tr>
  <tr><td><b>Fiber</b></td><td>Effect's lightweight concurrency unit: structurally forked, interrupted, joined</td><td><a href="07-concurrency-primitives.html">L07</a></td></tr>
  <tr><td><b>Server (Hono)</b></td><td>opencode's core runs as a local HTTP server; the TUI etc. are its clients</td><td><a href="09-server-overview.html">L09</a></td></tr>
  <tr><td><b>Event Bus (SSE)</b></td><td>The server pushes an event stream to clients via Server-Sent Events</td><td><a href="11-event-bus.html">L11</a></td></tr>
  <tr><td><b>Session / Message / Part</b></td><td>The session's three-tier data model: session holds messages, messages hold parts (text/tool/file…)</td><td><a href="14-session-messages-parts.html">L14</a></td></tr>
  <tr><td><b>Agent Loop</b></td><td>The main loop of "ask the model → run tools → feed results back → ask again"</td><td><a href="17-agent-loop.html">L17</a></td></tr>
  <tr><td><b>Projected History</b></td><td>The session history "projected" from durable data before each provider call</td><td><a href="19-projected-history.html">L19</a></td></tr>
  <tr><td><b>System Context</b></td><td>The structured collection of context facts presented to the model (_don't call_ it system prompt)</td><td><a href="21-system-context.html">L21</a></td></tr>
  <tr><td><b>Context Source</b></td><td>One independently-observed typed value within the System Context (stable key + codec + renderers)</td><td><a href="22-context-source.html">L22</a></td></tr>
  <tr><td><b>Context Epoch</b></td><td>The span during which one baseline System Context stays immutable, ending at compaction or baseline replacement</td><td><a href="24-context-epoch.html">L24</a></td></tr>
  <tr><td><b>LLM protocol adapter</b></td><td>Unifies each vendor's protocol (Anthropic/OpenAI/Gemini…) into one internal representation</td><td><a href="29-protocol-adapters.html">L29</a></td></tr>
  <tr><td><b>Model Resolution</b></td><td>Resolves "provider/model name" into a concrete callable model and transport</td><td><a href="35-model-resolution.html">L35</a></td></tr>
  <tr><td><b>Tool.make</b></td><td>The uniform mold for defining a tool: name + params schema + execute</td><td><a href="36-tool-definition.html">L36</a></td></tr>
  <tr><td><b>Permissions</b></td><td>A policy gate before tool execution: ask/allow/deny (_last wins_ via findLast)</td><td><a href="41-permissions.html">L41</a></td></tr>
  <tr><td><b>Skills</b></td><td>Packaging "a set of prompts + tools + rules" into a reusable skill</td><td><a href="43-skills.html">L43</a></td></tr>
  <tr><td><b>Agents (build/plan)</b></td><td>Different "permission profiles" of one core: build can write, plan is read-only</td><td><a href="45-agents.html">L45</a></td></tr>
  <tr><td><b>MCP</b></td><td>Model Context Protocol: dynamically attach external scoped tools (incl. OAuth)</td><td><a href="46-mcp.html">L46</a></td></tr>
  <tr><td><b>Provider Plugin (IoC)</b></td><td>The core uses inversion of control to let provider plugins self-register (<span class="mono">PluginV2.define</span>)</td><td><a href="47-provider-plugins.html">L47</a></td></tr>
  <tr><td><b>Drizzle / SQLite</b></td><td>Code-as-schema persistence: sessions/messages stored in local SQLite</td><td><a href="48-drizzle-sqlite.html">L48</a></td></tr>
  <tr><td><b>Compaction / Snapshot / Revert</b></td><td>Memory management: compress history, shadow-git snapshots, revert</td><td><a href="51-compaction-snapshots.html">L51</a></td></tr>
  <tr><td><b>opentui</b></td><td>A "browser inside the terminal" rendering SolidJS to a TTY</td><td><a href="52-opentui.html">L52</a></td></tr>
  <tr><td><b>frecency</b></td><td>A frequency+recency ranking formula: <span class="mono">freq/(1+days)</span></td><td><a href="55-prompt-component.html">L55</a></td></tr>
  <tr><td><b>Plugin / Hooks</b></td><td>An external plugin = a function returning Hooks; trigger passes a draft, plugins paint over it in layers</td><td><a href="57-plugin-system.html">L57</a></td></tr>
  <tr><td><b>LSP (client)</b></td><td>opencode acts as an LSP client, borrowing the whole IDE language-server ecosystem</td><td><a href="59-lsp.html">L59</a></td></tr>
  <tr><td><b>PTY</b></td><td>Gives interactive programs a real terminal; env "customizable in the middle, non-negotiable last"</td><td><a href="60-pty-shell.html">L60</a></td></tr>
  <tr><td><b>ACP / Location</b></td><td>opencode as an ACP server (mirror of LSP); Location decouples "the session" from "where it runs"</td><td><a href="61-acp-location.html">L61</a></td></tr>
  <tr><td><b>EventV2 / single-writer sync</b></td><td>persistent event sourcing + single writer + monotonic seq; devices replay from a cursor to catch up</td><td><a href="65-event-sourcing-sync.html">L65</a></td></tr>
  <tr><td><b>Slash commands</b></td><td>parameterized prompt templates; command/MCP/skill sources shaped into one Info</td><td><a href="66-slash-commands.html">L66</a></td></tr>
  <tr><td><b>http-recorder</b></td><td>record a real LLM round-trip to a cassette, replay to test a non-deterministic loop (with redaction)</td><td><a href="67-http-recorder.html">L67</a></td></tr>
  <tr><td><b>device-code OAuth / credential store</b></td><td>CLI callback-less device-code login; OAuth\|Key unified into a credential store</td><td><a href="68-account-auth.html">L68</a></td></tr>
  <tr><td><b>ecosystem / Durable Object</b></td><td>one server, many faces; sharing syncs via a Cloudflare Durable Object</td><td><a href="69-ecosystem-tour.html">L69</a></td></tr>
</table>

<h2>After finishing: the "transferable wisdom" opencode teaches you</h2>
<p>What this book really wants to leave you isn't 64 lessons' worth of scattered facts, but a few pieces of design wisdom that <strong>cross specific technologies and transfer to your own projects</strong>. They recur throughout the book, corroborating one another. Let's gather them in one table, each pointing to a lesson or two as a "best example" for you to revisit later:</p>
<table class="t">
  <tr><th>Transferable wisdom</th><th>One line</th><th>Example lessons</th></tr>
  <tr><td><b>Reuse mature ecosystems</b></td><td>Borrow rather than build: search borrows Ripgrep, version control git, language intelligence LSP, compilation Bun</td><td><a href="39-search-exec-tools.html">L39</a> · <a href="59-lsp.html">L59</a></td></tr>
  <tr><td><b>Edit a draft</b></td><td>Passing a mutable draft for parties to paint over in layers is more composable than negotiating complex return-value merges</td><td><a href="54-events-to-store.html">L54</a> · <a href="58-plugin-hooks.html">L58</a></td></tr>
  <tr><td><b>Find the seam</b></td><td>Cut "what changes" from "what doesn't": core vs provider, data vs presentation, what vs where</td><td><a href="47-provider-plugins.html">L47</a> · <a href="61-acp-location.html">L61</a></td></tr>
  <tr><td><b>Wrong usage fails loudly</b></td><td>Turn easy pitfalls into "trips an alarm on contact" ahead of time, rather than burying them as distant ghostly bugs</td><td><a href="37-tool-registry.html">L37</a> · <a href="63-test-contribute.html">L63</a></td></tr>
  <tr><td><b>Attention is scarce</b></td><td>Whether model or maintainer, attention is finite—keep only high signal, hold back the noise</td><td><a href="42-bounded-output.html">L42</a> · <a href="63-test-contribute.html">L63</a></td></tr>
  <tr><td><b>One mold stamps the same shape</b></td><td>A mold anyone uses comfortably (Tool.make/createSimpleContext/Plugin) makes the right thing the easiest thing</td><td><a href="36-tool-definition.html">L36</a> · <a href="53-tui-structure.html">L53</a></td></tr>
</table>
<p>If you take away only one sentence, let it be this: <strong>opencode stays clear in the fast-evolving, uncertainty-filled field of "AI agents" not through cleverer tricks, but by repeatedly "finding the seam, reusing the mature, making the right thing effortless, and leaving a door open for the unknown"</strong>. This wisdom doesn't belong to opencode; it belongs to every engineer who wants to build a complex system solidly—including you, reading this book. With that, the book's core 12 parts (64 lessons) plus the advanced topics (Part 13 · L65–69)—<strong>69 lessons</strong> in all—come to a close. May you take this map and go read the source, change it, contribute—or go build something of your own.</p>
""",
}
