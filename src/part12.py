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
  <div class="cel"><b>cli/cmd/tui/</b><br>TUI 代码，SolidJS + opentui（L52–56）</div>
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
<p>为什么非要做成「单文件、自包含」？因为这直接决定了<strong>分发体验</strong>。如果产物依赖 node_modules，用户就得先装 Node、再 <span class="mono">npm install</span> 一大堆依赖，版本不对还会出岔子；而一个自包含二进制，<span class="mono">curl | bash</span> 下载一个文件、<span class="mono">chmod +x</span> 就能跑，没有任何外部依赖、不挑机器环境。跨平台矩阵的意义也在此：CI 一次把所有平台的二进制都编好，无论用户在 Mac、Linux 还是 Windows、是 Intel 还是 ARM，都能下到一个<strong>专门为他那台机器编译好</strong>的原生文件。这种「一处编译、处处可跑」的发布形态，是 opencode 能做到「一行命令装好」的工程底座——而它几乎是<strong>免费</strong>得来的，全靠 Bun 把「编译成单文件可执行程序」这件以前很麻烦的事变成了一个 <span class="mono">Bun.build</span> 调用。回头看，这也呼应了全书反复出现的主题：<strong>站在成熟工具的肩膀上</strong>——L39 借 Ripgrep、L51 借 git、L59 借语言服务器，而这里借 Bun 的编译能力，把本该自己造的轮子统统省掉，专注于真正独特的 agent 逻辑。</p>

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
    "en": r"""__EN_L62__""",
}

LESSON_63 = wip('测试与贡献', 'Test & contribute')
LESSON_64 = wip('术语表与索引', 'Glossary & index')
