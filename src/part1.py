"""Part 1 (Part 1 · The Big Picture) content. Placeholders until M1 fills them in."""
from placeholder import wip

LESSON_01 = {
    "zh": r"""
<p class="lead">opencode 是一个<strong>开源的 AI 编程 agent</strong>：你在终端里敲下需求，它就能读你的代码、改文件、跑命令，装着大模型一步步把活干完。但它远不止"一个聊天框套了 LLM"——它的内核是一个<strong>常驻的服务器</strong>，掌管全部 agent 逻辑、会话历史、工具与模型接入；你面前的终端界面只是连上这台服务器的<strong>一个客户端</strong>。这一课先建立全景：opencode 是什么、为什么是"客户端/服务器"、一次对话宏观上怎么流动、它由什么搭成。</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  把 opencode 想成一间<strong>「AI 编程工作室」</strong>。<strong>服务器</strong>是常驻的"工头大脑"，记得整个项目的来龙去脉、手里攥着各种工具；<strong>大模型</strong>是请来的"会写代码的顾问"，但顾问只动嘴、不动手；<strong>客户端</strong>（你的终端 TUI）是工头面前的"操作台"，你在这儿下指令、看进展。工头听顾问的建议，<strong>亲自</strong>用工具（读文件、改代码、跑测试）干活，再把结果讲给顾问听，如此往复，直到完成。
</div>

<h2>它到底解决什么问题</h2>
<p>今天的 AI 编程助手大致两类：一类是编辑器里的<strong>补全</strong>（如 Copilot），贴着你的光标续写下一段；一类是<strong>聊天面板</strong>（如 Cursor 的 chat），在侧边和你对话。它们很强，却有共同的天花板：会话和上下文<strong>锁在某个编辑器里</strong>、难以脚本化与自动化、工具能力受宿主限制、换台机器或换个前端就得从头来。</p>
<p>opencode 反着设计：把"AI 编程 agent"做成一个<strong>独立的、长期运行的服务</strong>，前端只是它的一张脸。于是同一个 agent 可以被终端、网页、桌面、Slack、甚至别的编辑器共享，会话存在服务端不丢，还能 headless 跑在 CI 里。</p>

<table class="t">
  <tr><th>维度</th><th>编辑器补全 / 聊天</th><th>opencode</th></tr>
  <tr><td>形态</td><td>编辑器插件 / 面板</td><td><strong>独立常驻服务</strong> + 多种客户端</td></tr>
  <tr><td>会话上下文</td><td>绑定在某个编辑器进程</td><td><strong>持久化在服务端</strong>（SQLite），换端不丢</td></tr>
  <tr><td>工具能力</td><td>受宿主 API 限制</td><td>服务端统一提供（读写/执行/搜索/LSP…）</td></tr>
  <tr><td>自动化</td><td>难以脚本化</td><td><strong>headless</strong> <span class="mono">serve</span> + HTTP API</td></tr>
  <tr><td>扩展</td><td>插件体系各异</td><td>统一的插件 / MCP / provider 体系</td></tr>
</table>

<p>这一步"<strong>把 agent 抽成独立服务</strong>"看似只是工程上的搬家，实则改变了 AI 编程的形态：agent 不再是某个编辑器的附属功能，而成了一个<strong>可被任意工作流调用的能力</strong>。你可以在终端里和它结对编程，也可以在 CI 流水线里让它自动跑一轮重构、修测试；可以本地独占，也可以把 server 部署到远端供团队共享。前端从"能力的提供者"退回成"能力的展示窗口"——这正是 opencode 区别于编辑器插件的根本一步，也是它能长出 TUI、网页、桌面、Slack、ACP 这么多张脸的前提。</p>
<p>换个角度看：编辑器插件是"<strong>把 AI 塞进工具里</strong>"，opencode 是"<strong>把工具交给 AI</strong>"。前者 AI 是配角，处处受编辑器能力的边界约束；后者 AI 是主角，server 主动把读写文件、跑命令、查 LSP 这些能力<strong>武装</strong>给它。这个主客易位，决定了 opencode 想完成的是"端到端把一个任务做完"，而不只是"在你写代码时搭把手"——理解了这一点，后面所有的设计取舍才有了出发点。</p>
<p>还有一层不能略过：opencode 是<strong>开源</strong>的。这意味着它的模型接入、工具、provider、乃至 agent 的行为都<strong>可审计、可改、可自托管</strong>——你能看到它到底把什么发给了大模型，也能加自己的工具、接自己的私有模型。对想弄明白"一个真实的 AI 编程 agent 内部到底怎么运转"的人来说，这是一份难得的、完整的、还在高速演进的活教材——而这，正是这份指南存在的理由。</p>

<h2>客户端 / 服务器：为什么这样切</h2>
<p>opencode 把所有"重"的东西——<strong>agent 循环、会话持久化、工具执行、模型接入、权限</strong>——都收进<strong>一个 server</strong>。客户端只干两件事：<strong>把你的话发给 server</strong>、<strong>把 server 推来的事件画出来</strong>。这条边界切得很干净，带来四个直接好处：</p>
<div class="cols">
  <div class="col"><h4>一个内核，多张脸</h4><p>TUI、网页、桌面、Slack、ACP 共用同一个 server，行为一致，不用各写一套 agent 逻辑。</p></div>
  <div class="col"><h4>会话不丢</h4><p>会话存在 server 的 SQLite 里；关掉前端、重启、换台机器，历史都还在。</p></div>
  <div class="col"><h4>自动化友好</h4><p><span class="mono">opencode serve</span> 起一个无界面 HTTP 服务，脚本 / CI 直接调 API。</p></div>
  <div class="col"><h4>工具集中</h4><p>读写文件、跑命令、搜索、LSP 诊断都由 server 提供，不受前端能力限制。</p></div>
</div>
<p>这套分层，从底到顶可以摞成一座塔——你的请求自上而下穿过它，结果再自下而上冒回来：</p>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">客户端</span><span class="name">TUI · run · web · desktop · Slack · ACP</span></div>
    <div class="ld">收集你的输入、渲染 server 推来的事件流（经<strong>生成的 SDK</strong> 通信）</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">服务器</span><span class="name">Effect HttpApi + SSE 事件总线</span></div>
    <div class="ld">对外提供 HTTP API 与事件流；把请求路由到会话引擎</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">会话引擎</span><span class="name">Session / agent 循环</span></div>
    <div class="ld">组装上下文、反复调用大模型、执行工具、持久化会话（V1 → V2 迁移中）</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">模型接入</span><span class="name">LLM 协议层 · Provider</span></div>
    <div class="ld">把请求编码成各家 provider 的协议，流式拿回 token（Anthropic / OpenAI / Gemini …）</div></div>
</div>

<p>这条边界还有个容易被忽略的性质：<strong>server 是有状态、长生命周期的，client 是瘦的、可随时断开重连的</strong>。server 一直活着、攥着会话历史和正在跑的 agent 循环；client 则可以关掉再打开、甚至换一个完全不同的前端，重连时通过<strong>事件流</strong>立刻同步到会话此刻的样子。正因如此，多个 client 能同时盯着同一个会话——server 把每一个变化都作为事件广播出去，谁连上谁就跟得上进度。</p>
<p>它们之间说话，靠的是一套<strong>从 server 自动生成的 SDK</strong>（第 12 课详谈）：server 用 Effect 的 HttpApi 描述自己的接口，再据此生成类型安全的客户端代码——于是前端调用 server 就像调用本地函数一样有类型提示，接口一改、客户端类型立刻跟着变。富终端 TUI 还有个巧妙之处：它和 server 跑在<strong>同一个进程</strong>里，用进程内 RPC 代替网络往返（第 13 课），既省去起网络服务的开销，又复用了完全一样的 SDK 接口。</p>
<p>具体说，连向这台 server 的"脸"是一大家子：你最常用的<strong>富终端 TUI</strong>、脚本友好的 <span class="mono">run</span> 滚动输出模式、<strong>网页</strong>与 <strong>Electron 桌面应用</strong>、把 opencode 接进团队沟通的 <strong>Slack 机器人</strong>，以及通过 <strong>ACP（Agent Client Protocol）</strong>把 opencode 当作 agent 后端接入的外部编辑器。它们形态各异，却都只是同一个 server 的客户端——这也是为什么这份指南把"会话引擎"而不是"某个界面"当作真正的主角。</p>
<p>把能力集中到 server 还有一个安全上的好处：<strong>所有危险操作都经过同一道权限闸门</strong>。agent 要删文件、跑一条可能有副作用的命令时，server 可以按策略要求你先确认——这道闸门只需在 server 实现一次，所有客户端自动受益（第 41 课细讲）。换句话说，"集中"不只是为了复用，也是为了让"放手让 AI 干活"这件事<strong>可控、可信</strong>。</p>

<h2>一次对话，宏观看一眼</h2>
<p>你在 TUI 敲下"帮我修复这个 bug"，宏观上会发生这样一串接力——记住这条线，后面每一课都是在放大其中某一段：</p>
<div class="flow">
  <div class="node"><div class="nt">你输入</div><div class="nd">TUI 提交 prompt</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">server</div><div class="nd">存会话 · 组装上下文</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">大模型</div><div class="nd">流式返回：要调工具</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">执行工具</div><div class="nd">读文件 / 改代码 / 跑命令</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">喂回结果</div><div class="nd">再问大模型</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">循环到完成</div><div class="nd">事件流回 TUI</div></div>
</div>
<p>关键在那个<strong>循环</strong>：大模型一次只"想一步"——它说"我要先读这个文件"，server 就<strong>替它</strong>读、把内容塞回去；它再说"现在改这一行"，server 就改。直到大模型不再要求调工具、给出最终答复，循环才停。整个过程 server 不停把"它在想什么、做了什么"作为<strong>事件流</strong>推给 TUI，你才能实时看到它敲下的每一步。这条"反复 调模型 → 执行工具"的循环，就是所谓 <strong>agent 循环</strong>，是 opencode 真正的心脏（第 17 课会逐跳拆开）。</p>
<p>把这条循环落到一个真实的"修 bug"上，大致是这样一串接力：大模型先要求用 <span class="mono">grep</span> 搜关键字、定位到出错的文件 → server 执行搜索、把命中的行喂回去 → 大模型要求<strong>读</strong>那个文件的相关片段 → 读回来后它判断"这里少了个空值判断，改这一行" → server 用 <span class="mono">edit</span> 工具落实修改 → 大模型不放心，要求<strong>跑一遍测试</strong> → server 执行 <span class="mono">bash</span> 跑测试、把输出喂回 → 测试通过，大模型给出一句话总结。<strong>这七八步里没有一步是你手动做的</strong>，但每一步你都在 TUI 里看得清清楚楚——这种"它自己一步步把活干完、你全程在场监督"的体感，就是 agent 循环的魅力，也是 opencode 想给你的核心体验。</p>
<p>这种"全程在场监督"之所以可能，是因为 server 把 agent 的每一个动作——读了什么、决定调哪个工具、工具返回了什么、接下来打算怎么做——都<strong>作为一条条事件</strong>实时推出来。对使用者，这是信任的来源：你不是把任务丢进黑盒等结果，而是看着它一步步推进、随时可喊停或纠正。对开发者，这是 opencode 架构的一条暗线：<strong>几乎所有状态变化都先落成事件，再被持久化、被广播、被前端渲染</strong>——记住"事件"这个词，第三、四部分会反复见到它。</p>
<p>还有个容易被忽略的细节：循环里的工具调用并不总是一个接一个地跑。当大模型在一步里同时要求"把这三个文件都读一下"时，server 可以<strong>并发</strong>地把它们一起执行、再统一把结果喂回去（第 18 课会看到它背后用的是 Effect 的并发原语 <span class="mono">FiberSet</span>）。所以 agent 循环的真实节奏是"一轮里可能并行干好几件事，再整体推进到下一轮"——既更快，也让大模型一次能看到更完整的上下文。把握住这个"一轮多事、轮轮推进"的图像，后面读 agent 循环源码时就不会被并发细节绕晕。</p>

<h2>它由什么搭成（技术栈一瞥）</h2>
<p>opencode 是一个 <strong>Bun + TypeScript 的 monorepo</strong>（一个仓库装下 20 多个包）。几块地基值得先记个脸熟，后面会反复遇到：</p>
<div class="cols">
  <div class="col"><h4>Bun</h4><p>运行时与工具链：比 Node 启动快，自带打包、测试、SQLite 绑定。<span class="mono">bun dev</span> 即可跑起来。</p></div>
  <div class="col"><h4>Effect</h4><p>函数式框架：把<strong>副作用、错误、依赖</strong>都写进类型，贯穿 V2 内核（第二部分专讲）。</p></div>
  <div class="col"><h4>Drizzle + SQLite</h4><p>类型安全的 ORM + 嵌入式数据库：V2 把会话、消息、上下文都持久化进本地 SQLite。</p></div>
  <div class="col"><h4>SolidJS + opentui</h4><p>用写网页组件的方式，把 UI <strong>渲染到终端</strong>——TUI 本质是"终端里的浏览器"（第十部分）。</p></div>
</div>
<p>模型接入也有意思：opencode 同时有两套——V1 直接用 Vercel 的 <span class="mono">ai</span>（AI-SDK），V2 则<strong>自研了一层多协议 LLM 客户端</strong>（第六部分）。这引出整个项目最重要的背景：它正处在一场<strong>从 V1 到 V2 的架构迁移</strong>中，两套代码并存——下一课就专门讲这条迁移线，那是读懂整个仓库的钥匙。</p>

<p>为什么偏偏是这套组合？因为它们各自啃下了 agent 这类程序最硬的一块骨头：<strong>Bun</strong> 让"一个二进制就能跑、装起来简单"成为可能；<strong>Effect</strong> 把"反复调模型、并发执行多个工具、随时可能失败或被用户打断"这种<strong>充满副作用与并发</strong>的逻辑收拢进类型系统，让它可推理、可测试、可组合；<strong>SQLite</strong> 给会话一个零配置、随装随用的本地持久化；<strong>SolidJS + opentui</strong> 让终端 UI 也能像写网页一样组件化。四个选择都指向同一个目标——<strong>一个轻、稳、可嵌入、离线也能跑的本地 agent</strong>。这套技术品味本身，就是读懂 opencode 设计哲学的第一条线索。</p>
<p>顺带认一下这个 monorepo 的"主干包"，后面会反复点名：<span class="mono">packages/opencode</span> 是主二进制（CLI、V1 会话引擎、server 宿主）；<span class="mono">packages/core</span> 是 V2 的 Session Core（纯 Effect 内核）；<span class="mono">packages/llm</span> 是自研 LLM 协议层；<span class="mono">packages/tui</span> 是富终端界面；<span class="mono">packages/sdk</span> 是从 server 生成的客户端；还有 <span class="mono">plugin</span>、<span class="mono">server</span>、<span class="mono">desktop</span> 等。下一课的"项目地图"会把这 20 多个包一次摊开。</p>
<p>关于这场迁移，这里先埋个伏笔：你在源码里会看到两套并存的实现——<span class="mono">packages/opencode/src/session</span> 是 <strong>V1</strong>（基于 Vercel AI-SDK、把会话存成磁盘上的 JSON 文件），<span class="mono">packages/core</span> 是 <strong>V2 Session Core</strong>（纯 Effect、存进 SQLite）。V1 仍是当前默认跑的路径，V2 是正在成形的未来。这份指南以 V2 为主线深讲，但会在关键处对照 V1——因为你读源码时一定会同时撞见它俩。下一课就专门把这条迁移线讲清楚。</p>

<h2>这套指南怎么读</h2>
<p>opencode 的代码量不小，直接扎进源码容易迷路。这份指南按"<strong>自底向上、层层递进</strong>"组织成 12 个部分：先打地基，再盖楼，最后装修。建议顺着读，因为每一部分都踩在前一部分的概念之上：</p>
<div class="vflow">
  <div class="step"><b>① 宏观全景</b>　先建立你正在看的这张全景图（就是本部分）</div>
  <div class="step"><b>② Effect 地基</b>　读懂贯穿全局的函数式底座，后面才不至于处处卡壳</div>
  <div class="step"><b>③ 客户端/服务器</b>　server 骨架、路由、SDK 与事件流</div>
  <div class="step"><b>④–⑤ 会话内核 ★</b>　agent 循环 + System Context / Context Epoch，opencode 最核心的两块</div>
  <div class="step"><b>⑥ LLM 协议层 ★</b>　自研的多协议模型接入</div>
  <div class="step"><b>⑦–⑨ 工具 · 配置 · 持久化</b>　让 agent 真正能干活、能配置、记得住</div>
  <div class="step"><b>⑩–⑫ TUI · 扩展 · 实战</b>　终端渲染、插件/LSP/MCP 生态、构建与贡献</div>
</div>
<p>为什么是"自底向上"而不是"自顶向下"？因为 opencode 的上层都建立在一层层抽象之上：不先弄懂 Effect 的 Service 与 Layer，就看不懂 server 怎么被组装出来；不先理解 agent 循环，就说不清 TUI 上那些实时跳动的事件究竟从何而来。所以我们从地基开始，每一层都为上一层备好概念，读到后面会越来越顺。</p>
<p>带 ★ 的两部分是 opencode 最独特、最值钱的内核，也是这份指南着墨最多的地方。如果你时间有限、只想抓重点，可以先通读第一部分建立全景，再直接跳到第四、五部分；其余部分则可当作"需要时再查"的纵深资料。无论怎么读，都请记住那条主线——<strong>客户端发消息 → server 跑 agent 循环 → 事件流回客户端</strong>——它会像一根线，把后面 63 课串成一串。</p>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  opencode = <strong>一个常驻 server</strong>（掌管 agent 循环、会话、工具、provider、持久化）+ <strong>多个瘦客户端</strong>（经生成的 SDK 通信）。记住这条主线：<strong>客户端发消息 → server 跑 agent 循环（反复 调 LLM → 执行工具）→ 事件流回客户端</strong>。这套指南接下来的每一课，都是在放大这条主线上的某一段。
</div>

<div class="card detail">
  <div class="tag">🔬 细节 / 源码对应</div>
  命令行入口是 <span class="inline">packages/opencode/src/index.ts</span>：用 <span class="mono">yargs</span> 注册了一大批子命令——"同一套 server 逻辑、多个入口"正是客户端/服务器在命令行上的直接体现：
<pre class="code"><span class="cm">// 简化自 packages/opencode/src/index.ts</span>
const cli = <span class="fn">yargs</span>(<span class="fn">hideBin</span>(process.argv))
  .<span class="fn">scriptName</span>(<span class="st">"opencode"</span>)
  .<span class="fn">command</span>(TuiThreadCommand)   <span class="cm">// 默认：交互式终端 UI（一个客户端）</span>
  .<span class="fn">command</span>(RunCommand)         <span class="cm">// 一次性跑一个 prompt（脚本友好）</span>
  .<span class="fn">command</span>(ServeCommand)       <span class="cm">// 起 headless HTTP server（无界面）</span>
  .<span class="fn">command</span>(AcpCommand)         <span class="cm">// 作为 ACP server 接入外部编辑器</span>
  .<span class="fn">command</span>(McpCommand)         <span class="cm">// 管理 MCP 工具服务器</span>
  <span class="cm">// … 还有 generate / agent / models / session / db …</span></pre>
  跑 <span class="mono">opencode</span> 默认进 TUI，<span class="mono">opencode serve</span> 起无界面服务，<span class="mono">opencode run "…"</span> 脚本式跑一轮——它们都连向同一套会话引擎。这也解释了一个初见时容易困惑的现象：明明是同一个 <span class="mono">opencode</span> 命令，加不同子命令就成了完全不同的东西——它们共享内核，只是<strong>把同一套能力包装成了不同的入口</strong>。
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>opencode 是<strong>开源 AI 编程 agent</strong>，采用<strong>客户端/服务器</strong>架构。</li>
    <li>server <strong>掌管一切</strong>：agent 循环、会话、工具、provider、持久化；client 只是视图。</li>
    <li>一次对话 = server <strong>反复（调 LLM → 执行工具）</strong>直到完成，事件流实时回 client。</li>
    <li>技术栈：<strong>Bun + TypeScript + Effect + Drizzle/SQLite + SolidJS/opentui</strong>。</li>
    <li>代码正从 <strong>V1</strong>（AI-SDK、文件存储）迁移到 <strong>V2</strong>（纯 Effect、SQLite）——下一课展开。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">opencode is an <strong>open-source AI coding agent</strong>: type a request in your terminal and it reads your code, edits files, runs commands, and drives a large language model step by step to get the job done. But it is far more than "a chat box wrapping an LLM" — its core is a <strong>long-running server</strong> that owns all the agent logic, session history, tools, and model access; the terminal interface in front of you is just <strong>one client</strong> connected to that server. This lesson builds the big picture: what opencode is, why it is client/server, how one prompt flows at a high level, and what it is built from.</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  Picture opencode as an <strong>"AI coding workshop."</strong> The <strong>server</strong> is the resident "foreman brain" that remembers the whole project and holds all the tools. The <strong>LLM</strong> is a hired "coding advisor" who only talks, never acts. The <strong>client</strong> (your terminal TUI) is the "control desk" where you give orders and watch progress. The foreman takes the advisor's suggestions and <strong>personally</strong> uses tools (read files, edit code, run tests), then reports results back to the advisor — round and round until the work is done.
</div>

<h2>What problem does it solve</h2>
<p>Today's AI coding helpers come in two flavors: in-editor <strong>completion</strong> (like Copilot) that continues from your cursor, and a <strong>chat panel</strong> (like Cursor's chat) that talks alongside you. Both are powerful, but share a ceiling: the session and context are <strong>locked inside one editor</strong>, hard to script or automate, tool power is limited by the host, and switching machines or front-ends means starting over.</p>
<p>opencode flips the design: it makes the "AI coding agent" a <strong>standalone, long-running service</strong>, and the front-end is just one of its faces. So one agent can be shared by terminal, web, desktop, Slack, even other editors; sessions live server-side and survive; and it can run headless in CI.</p>

<table class="t">
  <tr><th>Dimension</th><th>Editor completion / chat</th><th>opencode</th></tr>
  <tr><td>Form</td><td>Editor plugin / panel</td><td><strong>Standalone resident service</strong> + many clients</td></tr>
  <tr><td>Session context</td><td>Bound to one editor process</td><td><strong>Persisted server-side</strong> (SQLite), survives client switches</td></tr>
  <tr><td>Tool power</td><td>Limited by host APIs</td><td>Provided centrally by the server (read/write/exec/search/LSP…)</td></tr>
  <tr><td>Automation</td><td>Hard to script</td><td><strong>headless</strong> <span class="mono">serve</span> + HTTP API</td></tr>
  <tr><td>Extensibility</td><td>Varying plugin systems</td><td>Unified plugin / MCP / provider system</td></tr>
</table>

<p>This step — <strong>extracting the agent into a standalone service</strong> — looks like mere engineering relocation, but it changes the shape of AI coding: the agent is no longer a feature bolted onto some editor, but <strong>a capability any workflow can call</strong>. You can pair with it in the terminal, or let it auto-run a refactor in CI; use it locally, or deploy the server remotely for a team to share. The front-end demotes from "provider of the capability" to "display window for it" — exactly the step that separates opencode from editor plugins, and the prerequisite for growing so many faces: TUI, web, desktop, Slack, ACP.</p>
<p>Put differently: editor plugins <strong>stuff AI into the tool</strong>; opencode <strong>hands the tools to the AI</strong>. In the former the AI is a supporting actor, bounded by the editor's reach; in the latter the AI is the lead, and the server actively <strong>arms</strong> it with reading/writing files, running commands, querying the LSP. That swap of lead and support is why opencode aims to "carry a task end to end," not just "lend a hand while you type" — grasp this and every later design choice has a starting point.</p>
<p>One more layer worth not skipping: opencode is <strong>open source</strong>. That means its model access, tools, providers, even the agent's behavior are all <strong>auditable, changeable, self-hostable</strong> — you can see exactly what it sends to the LLM, and add your own tools or wire up your own private model. For anyone trying to understand "how a real AI coding agent actually works inside," this is a rare, complete, still-rapidly-evolving living textbook — which is exactly why this guide exists.</p>

<h2>Client / server: why split it this way</h2>
<p>opencode puts everything "heavy" — <strong>the agent loop, session persistence, tool execution, model access, permissions</strong> — into <strong>one server</strong>. A client does just two things: <strong>send your words to the server</strong> and <strong>render the events it streams back</strong>. That clean boundary buys four things:</p>
<div class="cols">
  <div class="col"><h4>One core, many faces</h4><p>TUI, web, desktop, Slack, ACP all share one server with consistent behavior — no re-implementing agent logic per front-end.</p></div>
  <div class="col"><h4>Sessions survive</h4><p>Sessions live in the server's SQLite; close the front-end, restart, switch machines — the history is still there.</p></div>
  <div class="col"><h4>Automation-friendly</h4><p><span class="mono">opencode serve</span> starts a headless HTTP service; scripts and CI call the API directly.</p></div>
  <div class="col"><h4>Tools centralized</h4><p>File I/O, running commands, search, LSP diagnostics all come from the server, unconstrained by the front-end.</p></div>
</div>
<p>Stacked bottom-up, these layers form a tower — your request flows down through it, results bubble back up:</p>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">Clients</span><span class="name">TUI · run · web · desktop · Slack · ACP</span></div>
    <div class="ld">Collect your input, render the server's event stream (talking via a <strong>generated SDK</strong>)</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">Server</span><span class="name">Effect HttpApi + SSE event bus</span></div>
    <div class="ld">Exposes the HTTP API and event stream; routes requests to the session engine</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">Session engine</span><span class="name">Session / agent loop</span></div>
    <div class="ld">Assembles context, calls the LLM repeatedly, runs tools, persists sessions (V1 → V2 in flight)</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">Model access</span><span class="name">LLM protocol layer · Provider</span></div>
    <div class="ld">Encodes requests into each provider's protocol, streams tokens back (Anthropic / OpenAI / Gemini …)</div></div>
</div>

<p>That boundary has an easily-missed property: <strong>the server is stateful and long-lived; the client is thin and can disconnect and reconnect anytime</strong>. The server stays alive, holding the session history and the running agent loop; the client can close and reopen, even switch to a completely different front-end, and on reconnect it immediately syncs — via the <strong>event stream</strong> — to what the session looks like right now. That's why several clients can watch one session at once: the server broadcasts every change as an event, and whoever connects catches up.</p>
<p>They talk through an <strong>SDK generated automatically from the server</strong> (Lesson 12): the server describes its interface with Effect's HttpApi, and type-safe client code is generated from it — so calling the server feels like calling a local function, with type hints, and changing an endpoint instantly updates the client types. The rich TUI has a neat twist: it runs in the <strong>same process</strong> as the server, replacing network round-trips with in-process RPC (Lesson 13), saving the overhead of a network service while reusing the exact same SDK interface.</p>
<p>Concretely, the "faces" connecting to this server are a big family: the <strong>rich terminal TUI</strong> you use most, the script-friendly <span class="mono">run</span> scrollback mode, the <strong>web</strong> and <strong>Electron desktop</strong> apps, a <strong>Slack bot</strong> that pipes opencode into team chat, and external editors that plug opencode in as an agent backend via <strong>ACP (Agent Client Protocol)</strong>. Different shapes, all just clients of the same server — which is why this guide treats the "session engine," not "some interface," as the real protagonist.</p>
<p>Centralizing capability into the server has a safety upside too: <strong>every dangerous operation passes through one permission gate</strong>. When the agent wants to delete a file or run a possibly side-effecting command, the server can require your confirmation per policy — a gate implemented once in the server, and every client benefits automatically (Lesson 41). In other words, "centralized" isn't only for reuse; it's also what makes "letting the AI loose to work" <strong>controllable and trustworthy</strong>.</p>

<h2>One prompt, from a distance</h2>
<p>You type "fix this bug" in the TUI. At a high level, a relay unfolds — remember this line; every later lesson zooms into one segment of it:</p>
<div class="flow">
  <div class="node"><div class="nt">You type</div><div class="nd">TUI submits a prompt</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">server</div><div class="nd">store session · assemble context</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">LLM</div><div class="nd">streams back: call a tool</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">run tool</div><div class="nd">read / edit / run command</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">feed result</div><div class="nd">ask the LLM again</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">loop to done</div><div class="nd">events stream to TUI</div></div>
</div>
<p>The key is that <strong>loop</strong>: the LLM "thinks one step" at a time — it says "first read this file," and the server reads it <strong>on its behalf</strong> and feeds the content back; it says "now change this line," and the server changes it. Only when the LLM stops asking for tools and gives a final answer does the loop stop. Throughout, the server streams "what it's thinking and doing" as an <strong>event stream</strong> to the TUI, so you watch every step live. This "repeatedly call the model → run tools" loop is the so-called <strong>agent loop</strong>, opencode's true heart (Lesson 17 takes it apart hop by hop).</p>
<p>Drop this loop onto a real "fix a bug" and it's a relay like this: the LLM first asks to <span class="mono">grep</span> a keyword to locate the failing file → the server runs the search and feeds the matching lines back → the LLM asks to <strong>read</strong> the relevant slice of that file → on reading it, it judges "a null check is missing here, change this line" → the server applies the change with the <span class="mono">edit</span> tool → uneasy, the LLM asks to <strong>run the tests</strong> → the server runs <span class="mono">bash</span> and feeds the output back → tests pass, the LLM gives a one-line summary. <strong>Not one of those seven or eight steps was done by your hand</strong>, yet you watched every one in the TUI — that feel of "it finishes the job step by step while you supervise throughout" is the charm of the agent loop, and the core experience opencode wants to give you.</p>
<p>This "present throughout, supervising" is possible because the server pushes out every one of the agent's moves — what it read, which tool it chose, what the tool returned, what it plans next — as <strong>individual events</strong>, live. For the user that's the source of trust: you're not tossing a task into a black box and waiting, you're watching it progress step by step, free to stop or correct at any time. For the developer it's a hidden through-line of opencode's architecture: <strong>nearly every state change first becomes an event, then gets persisted, broadcast, and rendered</strong> — remember the word "event"; Parts 3 and 4 meet it again and again.</p>
<p>One more easily-missed detail: tool calls in the loop don't always run one after another. When the LLM asks in a single step to "read all three of these files," the server can execute them <strong>concurrently</strong> and feed the results back together (Lesson 18 shows the Effect concurrency primitive behind it, <span class="mono">FiberSet</span>). So the real rhythm of the agent loop is "possibly do several things in parallel within a round, then advance as a whole to the next" — faster, and letting the LLM see fuller context at once. Hold this "many things per round, advancing round by round" picture and the concurrency details in the agent-loop source won't tangle you later.</p>

<h2>What it is built from (a tech-stack glance)</h2>
<p>opencode is a <strong>Bun + TypeScript monorepo</strong> (one repo holding 20+ packages). A few foundations are worth recognizing now; you'll meet them again and again:</p>
<div class="cols">
  <div class="col"><h4>Bun</h4><p>Runtime and toolchain: faster startup than Node, with built-in bundling, testing, and SQLite bindings. <span class="mono">bun dev</span> just runs it.</p></div>
  <div class="col"><h4>Effect</h4><p>A functional framework that writes <strong>side effects, errors, and dependencies</strong> into the types, running through the V2 core (Part 2).</p></div>
  <div class="col"><h4>Drizzle + SQLite</h4><p>A type-safe ORM + embedded database: V2 persists sessions, messages, and context into local SQLite.</p></div>
  <div class="col"><h4>SolidJS + opentui</h4><p>Render UI <strong>to the terminal</strong> using web-component style — the TUI is essentially "a browser in your terminal" (Part 10).</p></div>
</div>
<p>Model access is interesting too: opencode carries two stacks — V1 uses Vercel's <span class="mono">ai</span> (AI-SDK) directly, while V2 has its <strong>own multi-protocol LLM client</strong> (Part 6). That points to the project's most important backdrop: it is mid <strong>migration from V1 to V2</strong>, with both codebases coexisting — the next lesson is devoted to that migration line, the key to reading the whole repo.</p>

<p>Why this exact combination? Because each tackles one of the hardest bones of a program like an agent: <strong>Bun</strong> makes "one binary just runs, easy to install" possible; <strong>Effect</strong> gathers logic that is <strong>full of side effects and concurrency</strong> — calling the model repeatedly, running several tools at once, failing or being interrupted at any moment — into the type system, making it reasoned-about, testable, composable; <strong>SQLite</strong> gives sessions a zero-config, ready-to-use local persistence; <strong>SolidJS + opentui</strong> let terminal UI be componentized like writing web pages. All four choices point at one goal — <strong>a light, stable, embeddable, offline-capable local agent</strong>. This technical taste itself is the first clue to opencode's design philosophy.</p>
<p>While we're here, meet the monorepo's "trunk packages," named repeatedly later: <span class="mono">packages/opencode</span> is the main binary (CLI, V1 session engine, server host); <span class="mono">packages/core</span> is V2's Session Core (the pure-Effect kernel); <span class="mono">packages/llm</span> is the in-house LLM protocol layer; <span class="mono">packages/tui</span> is the rich terminal UI; <span class="mono">packages/sdk</span> is the client generated from the server; plus <span class="mono">plugin</span>, <span class="mono">server</span>, <span class="mono">desktop</span>, and more. The next lesson's "project map" spreads all 20-plus packages out at once.</p>
<p>On that migration, a foreshadowing: in the source you'll see two implementations side by side — <span class="mono">packages/opencode/src/session</span> is <strong>V1</strong> (built on Vercel's AI-SDK, storing sessions as JSON files on disk), and <span class="mono">packages/core</span> is <strong>V2 Session Core</strong> (pure Effect, into SQLite). V1 is still the default path running today; V2 is the future taking shape. This guide teaches V2 as the main line but contrasts V1 at key points — because reading the source you'll bump into both. The next lesson is devoted to making this migration line clear.</p>

<h2>How to read this guide</h2>
<p>opencode's codebase isn't small, and diving straight into the source is a good way to get lost. This guide is organized <strong>bottom-up, layer by layer</strong> into 12 parts: lay the foundation, raise the building, then finish the interior. Read in order, because each part stands on the concepts of the one before:</p>
<p>Why "bottom-up" and not "top-down"? Because opencode's upper layers stand on layer upon layer of abstraction: without first grasping Effect's Service and Layer, you can't see how the server is assembled; without first understanding the agent loop, you can't say where those live, flickering events in the TUI come from. So we start at the foundation, each layer preparing concepts for the next, and it reads more smoothly as you go.</p>
<div class="vflow">
  <div class="step"><b>① The big picture</b>　build the panorama you're looking at now (this part)</div>
  <div class="step"><b>② Effect foundations</b>　grasp the functional base that runs through everything</div>
  <div class="step"><b>③ Client/server</b>　the server skeleton, routes, SDK, and event stream</div>
  <div class="step"><b>④–⑤ Session core ★</b>　the agent loop + System Context / Context Epoch, opencode's two most central pieces</div>
  <div class="step"><b>⑥ LLM protocol layer ★</b>　the in-house multi-protocol model access</div>
  <div class="step"><b>⑦–⑨ Tools · config · persistence</b>　making the agent actually work, be configured, and remember</div>
  <div class="step"><b>⑩–⑫ TUI · extensibility · practice</b>　terminal rendering, the plugin/LSP/MCP ecosystem, building &amp; contributing</div>
</div>
<p>The two ★ parts are opencode's most distinctive, most valuable core, and where this guide spends the most ink. Short on time? Read Part 1 for the panorama, then jump straight to Parts 4 and 5; treat the rest as deep reference to consult when needed. However you read, hold that main line — <strong>client sends a message → server runs the agent loop → events stream back to the client</strong> — it threads the other 63 lessons together.</p>

<div class="card macro">
  <div class="tag">🌍 Big picture</div>
  opencode = <strong>one resident server</strong> (owning the agent loop, sessions, tools, providers, persistence) + <strong>several thin clients</strong> (talking via a generated SDK). Hold this line: <strong>client sends a message → server runs the agent loop (repeatedly call the LLM → run tools) → events stream back to the client</strong>. Every lesson ahead zooms into one segment of this line.
</div>

<div class="card detail">
  <div class="tag">🔬 Source detail</div>
  The CLI entry point is <span class="inline">packages/opencode/src/index.ts</span>: <span class="mono">yargs</span> registers a whole set of subcommands — "one server core, many entry points" is the client/server idea made concrete on the command line:
<pre class="code"><span class="cm">// simplified from packages/opencode/src/index.ts</span>
const cli = <span class="fn">yargs</span>(<span class="fn">hideBin</span>(process.argv))
  .<span class="fn">scriptName</span>(<span class="st">"opencode"</span>)
  .<span class="fn">command</span>(TuiThreadCommand)   <span class="cm">// default: interactive terminal UI (a client)</span>
  .<span class="fn">command</span>(RunCommand)         <span class="cm">// run one prompt once (script-friendly)</span>
  .<span class="fn">command</span>(ServeCommand)       <span class="cm">// start a headless HTTP server</span>
  .<span class="fn">command</span>(AcpCommand)         <span class="cm">// act as an ACP server for external editors</span>
  .<span class="fn">command</span>(McpCommand)         <span class="cm">// manage MCP tool servers</span>
  <span class="cm">// … plus generate / agent / models / session / db …</span></pre>
  Running <span class="mono">opencode</span> defaults to the TUI, <span class="mono">opencode serve</span> starts a headless service, and <span class="mono">opencode run "…"</span> runs one turn for scripts — all wired to the same session engine. This also explains a confusing-at-first phenomenon: the same <span class="mono">opencode</span> command becomes a completely different thing with a different subcommand — they share the kernel and merely <strong>wrap one set of capabilities into different entry points</strong>.
</div>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>opencode is an <strong>open-source AI coding agent</strong> with a <strong>client/server</strong> architecture.</li>
    <li>The server <strong>owns everything</strong>: the agent loop, sessions, tools, providers, persistence; the client is just a view.</li>
    <li>One conversation = the server <strong>repeatedly (call LLM → run tools)</strong> until done, streaming events to the client live.</li>
    <li>Tech stack: <strong>Bun + TypeScript + Effect + Drizzle/SQLite + SolidJS/opentui</strong>.</li>
    <li>The code is migrating from <strong>V1</strong> (AI-SDK, file storage) to <strong>V2</strong> (pure Effect, SQLite) — next lesson expands on it.</li>
  </ul>
</div>
""",
}
LESSON_02 = {
    "zh": r"""
<p class="lead">上一课记住了一条主线——客户端发消息、server 跑 agent 循环、事件流回客户端。可当你真把 opencode clone 下来、打开 <span class="mono">packages/</span> 目录，会一头撞进<strong>二十多个包</strong>，瞬间不知从哪看起。这一课就发你一张<strong>项目地图</strong>：把这些包按角色分成四组，标清谁依赖谁、哪些在"运行时 agent 路径"上、哪些只是周边。把这张图记牢，后面 62 课每点到一个包，你都知道它挂在地图的哪个位置。</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  把这个 monorepo 想成一座<strong>规划过的城市</strong>。<strong>市中心</strong>（CORE）是真正办事的地方——市政厅、发电厂、自来水公司，你每次"用 opencode 干一次活"跑的就是这几个包。<strong>临街店面</strong>（客户端）是市民看得见的脸：终端、网页、桌面、Slack，形态各异却都连着市中心。<strong>海外分部</strong>（云端集成）在另一个国度（Cloudflare）办公，你本地跑 opencode 根本惊动不到它们。<strong>地下水电管网</strong>（基础库）谁都在用却没人天天想起。而 <strong>turborepo</strong> 是这座城的交通调度，决定你改了一处、该重修哪几条路。
</div>

<h2>一个仓库，二十多个包</h2>
<p>opencode 是一个 <strong>Bun + turborepo 的 monorepo</strong>：一个 git 仓库装下约 <strong>24 个包</strong>，全躺在 <span class="mono">packages/</span> 下。为什么不拆成几十个独立仓库？因为这些包之间<strong>类型互通</strong>——server 改一个接口，sdk 立刻重新生成、客户端的类型跟着报错，<strong>一次提交</strong>就能横跨"客户端/服务器"那条线把改动做完，不必发版、不必对版本号。</p>
<p>一条 <span class="mono">bun install</span> 装好全部依赖，一张 turbo 任务图统一 <span class="mono">typecheck / build / test</span>。根 <span class="mono">package.json</span> 的 workspaces 还特意把 <span class="mono">packages/console/*</span>、<span class="mono">packages/stats/*</span> 这种"子应用树"也纳进来——所以"24 个包"是个约数：console、stats 内部又各自分了 app / core / server 几个小包。</p>
<div class="flow">
  <div class="node"><div class="nt">bun install</div><div class="nd">一次装好全仓依赖</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">turbo typecheck</div><div class="nd">全仓类型检查</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">turbo build</div><div class="nd">产出 dist/**</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">turbo test</div><div class="nd">dependsOn ^build</div></div>
</div>
<p>注意末尾那个 <span class="mono">^build</span>：turbo 规定"测一个包前，先把它依赖的<strong>上游包</strong>都 build 好"。换句话说，这张构建图本身就编码了包与包之间的<strong>依赖 DAG</strong>——一时读不懂依赖关系时，<span class="mono">turbo.json</span> 就是一份现成的地图。</p>
<p>monorepo 也不是没有代价——24 个包挤在一起，最怕"改一行、全仓重编"。opencode 用两件事压住它：<strong>Bun</strong> 让安装与打包飞快，<strong>turbo</strong> 靠内容哈希做<strong>增量缓存</strong>，只重跑真正受影响的包。于是仓库虽大，日常 <span class="mono">typecheck</span> 往往几秒就回。</p>
<p>反过来想：要是把 server、sdk、tui 拆成三个独立 npm 包，改一次 server 接口你就得发版 server、升级 sdk、再升级 tui——三次 PR、三次对版本。monorepo 把这一切压成<strong>一次提交</strong>。对一个正在 V1→V2 高速重构的项目，这种"原子改动"几乎是刚需。</p>
<p>还有个一脉相承的取向：它用的是 <strong>Bun 的 workspaces</strong>，而不是 npm/pnpm。Bun 既是包管理器、又是运行时与打包器，整条工具链就一个 <span class="mono">bun</span> 命令——这和第 1 课说的"一个二进制、装起来简单"是同一种品味。</p>
<p>说到底，monorepo 是 opencode 给"<strong>快速演进</strong>"下的注：当一个项目还在大改架构、接口天天变，把相关代码全摁进同一个仓库、用一条工具链统一约束，远比维护十几个互相对版本的独立包省心。它的取舍很清楚——<strong>用一点构建复杂度，换整体改动的灵活与一致</strong>。</p>
<p>也别被"包多"吓到：真正需要你<strong>从头读到尾</strong>的，其实只有那一小撮核心；其余大多数包，你读这份指南可能都不会打开第二眼。仓库的<strong>体量</strong>和你要投入的<strong>注意力</strong>从来不是一回事——分清这一点，是不被大型代码库劝退的第一步。</p>

<h2>四个角色分区</h2>
<p>把 24 个包按<strong>角色</strong>一摊开，其实只有四类：① <strong>CORE</strong>——在"运行时 agent 路径"上、你每跑一次 prompt 都会执行的包；② <strong>客户端</strong>——连向 server 的各种脸；③ <strong>云端 / 集成</strong>——跑在 Cloudflare 或作为机器人的服务；④ <strong>基础库</strong>——被反复复用的工具层。读源码时先认清一个包属于哪一类，就不会在 24 个里迷路。</p>
<p>这套"四分法"看着简单，价值却在于<strong>给每个包一个落点</strong>：以后你在某个文件顶部看到一长串 import，只要扫一眼它拉进来的是哪几组的东西，就能立刻判断"这是核心逻辑，还是某张脸的渲染，还是云上的运维"。地图的意义从来不是记住每条街的名字，而是<strong>一眼知道自己站在哪个城区</strong>。</p>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">客户端 · 脸</span><span class="name">tui · cli · app · ui · desktop · web</span></div>
    <div class="ld">收集你的输入、渲染 server 推来的事件流——同一个内核的多张脸</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">CORE · 运行时路径</span><span class="name">opencode · core · llm · server · sdk · plugin</span></div>
    <div class="ld">agent 循环、会话、模型接入、server 契约——跑一次 prompt 真正执行的只有这一组</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">云端 · 集成</span><span class="name">enterprise · function · slack · console · identity · containers · stats</span></div>
    <div class="ld">部署在 Cloudflare 或作为机器人/服务，本地内核完全用不到</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">基础库</span><span class="name">effect-drizzle-sqlite · effect-sqlite-node · http-recorder · script · storybook</span></div>
    <div class="ld">被复用的地基：DB 胶水、HTTP 录放、构建脚本、组件工坊</div></div>
</div>
<p>为什么按"角色"分，而不按"语言"或"技术栈"？因为同一种技术会散落在不同角色里——SolidJS 既在 tui 又在 app，Effect 既在 core 又在 cli。真正决定"我读源码要不要管它"的，是这个包<strong>在不在运行时跑</strong>，而不是它用什么写的。</p>
<p>这四组里，真正值得第一时间记住的是 <strong>CORE 与"周边"的切分</strong>——它是读这个仓库最省力的一把筛子：</p>
<div class="cols">
  <div class="col"><h4>CORE（6 个 · 运行时路径）</h4><p>opencode · core · llm · server · sdk · plugin。<strong>只有这 6 个</strong>在你本地跑 prompt 时执行——想搞懂 agent 怎么工作，九成答案都在这里。</p></div>
  <div class="col"><h4>周边（其余约 18 个）</h4><p>客户端的脸、云端服务、基础库。它们重要，但都<strong>围着 CORE 转</strong>：要么是它的前端，要么是它的运维，要么是它复用的工具。</p></div>
</div>
<p>怎么一眼判断一个包属于哪组？看三件事：它<strong>依赖 server / core 吗</strong>（多半是 CORE 或客户端）、它<strong>部署到 Cloudflare 吗</strong>（云端）、它<strong>有没有自己的"脸"</strong>（有界面是客户端，纯函数库是基础库）。这套判断，后面每撞见一个新包都用得上。</p>
<p>这条线还有个实用推论：<strong>读这份指南，你九成时间会待在 CORE 那 6 个包里</strong>。后面十二个部分，除了第一、十二部分讲全景与工程，其余几乎都在 CORE 内部纵深。所以现在就把这 6 个名字记熟，绝对划算。</p>
<p>要强调的是，这四组的<strong>边界并非一刀切得绝对干净</strong>：有的包会同时沾上两重身份（比如下面就会看到的 <span class="mono">cli</span>），有的基础库其实只服务于某一个上层。但作为<strong>第一层认知</strong>，这套分法已经足够好用——先有张粗地图，细节等到具体那一课再补。</p>

<h2>CORE：运行时路径上的六个包</h2>
<p>CORE 的 6 个包从"外壳"到"内核"层层递进，各管一段。下面这张表是你之后反复要回头看的<strong>主干索引</strong>：</p>
<table class="t">
  <tr><th>包</th><th>一句话职责</th><th>后续展开</th></tr>
  <tr><td class="mono">opencode</td><td>主二进制：yargs CLI + V1 会话引擎 + <strong>server 宿主</strong>（providers / MCP / LSP 也在此）</td><td>第 3、4 课</td></tr>
  <tr><td class="mono">core</td><td><strong>V2 Session Core</strong>：Effect 服务 + Drizzle/SQLite + 会话 / 工具 / system-context / pty</td><td>第四、五部分</td></tr>
  <tr><td class="mono">llm</td><td>自研、与 provider 无关的<strong>多协议 LLM 客户端</strong></td><td>第六部分</td></tr>
  <tr><td class="mono">server</td><td><strong>瘦契约层</strong>：cors、路由组、共享类型</td><td>第三部分</td></tr>
  <tr><td class="mono">sdk</td><td>从 server 的 OpenAPI <strong>生成</strong>的类型安全 TS 客户端</td><td>第 12 课</td></tr>
  <tr><td class="mono">plugin</td><td>对外的 <span class="mono">@opencode-ai/plugin</span> 插件 SDK</td><td>第十一部分</td></tr>
</table>
<p>把一次请求顺着这 6 个包走一遍最直观：你的话先进 <span class="mono">opencode</span> / <span class="mono">cli</span> 的命令外壳，由它宿主的 <span class="mono">server</span> 收下；server 按契约把活派给 <span class="mono">core</span> 的会话引擎；core 要调模型时找 <span class="mono">llm</span>；llm 再把请求编码成某家 provider 的协议。一层套一层，正是"外壳 → 内核"。</p>
<p>换个比方，这 6 个包像一条<strong>从人到模型的传送带</strong>：最外面接住你的人话，最里面吐出给大模型的协议字节，中间每一段都只做一件清清楚楚的事、再把半成品交给下一段。读源码时若被某个文件绕晕，回到这条传送带上想想"我现在在哪一段、上一段递给了我什么、我又该交给下一段什么"，往往立刻就清醒了。</p>
<p>也正因为分段清楚，每一段都能<strong>单独替换</strong>：换个 provider 只动最里那段、换张前端只动最外那段，中间纹丝不动。这种"一段坏不牵连全身"的解耦，是后面很多设计能成立的前提。</p>
<p>一个容易看花眼的细节：<span class="mono">opencode</span> 自己<strong>同时</strong>是核心包<strong>和</strong>宿主——它一边扛着整套 <strong>V1</strong> 引擎，一边把 <strong>V2 的 core</strong> 当作 server 背后的内核装进来。所以它正好骑在 V1/V2 这条迁移线上（第 4 课细说）。</p>
<p>还有个彩蛋：opencode 其实有<strong>两个二进制</strong>。<span class="mono">packages/opencode</span> 是当前主用的 <span class="mono">opencode</span> 命令（yargs、偏 V1）；<span class="mono">packages/cli</span> 则是另一个叫 <span class="mono">lildax</span> 的二进制，用 Effect 命令框架把 <span class="mono">core + server + tui + sdk</span> 打包到一起——那是<strong>正在成形的 V2 入口</strong>。</p>
<div class="flow">
  <div class="node"><div class="nt">客户端</div><div class="nd">tui · app · desktop · cli</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">sdk</div><div class="nd">生成的类型安全客户端</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">server</div><div class="nd">瘦契约层</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">core (+llm)</div><div class="nd">V2 内核 + 模型层</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">provider</div><div class="nd">Anthropic · OpenAI · …</div></div>
</div>
<p>这 6 个包的<strong>依赖只朝一个方向流</strong>：客户端从不直接 import <span class="mono">core</span>，而是经<strong>生成的 sdk</strong> 调 <span class="mono">server</span>，再由 server 落到 <span class="mono">core</span> 与 <span class="mono">llm</span>，最后打到各家 provider。这正是上一课那条"客户端/服务器"边界在包结构上的样子——而 sdk 这道缝，是在<strong>构建时反向</strong>从 server 的 OpenAPI 生成出来的（第 12 课）。</p>
<p>别被 <span class="mono">server</span> 的"瘦"字骗了——它瘦，是因为<strong>重活全在 core</strong>。server 只把 HTTP 请求按契约翻成对 core 的调用，再把 core 吐出的事件流编码回 SSE。这种"薄壳厚核"的切法，让同一套 core 既能被网络 server 包、也能被 cli 进程内直接调（第 13 课）。</p>
<p><span class="mono">sdk</span> 与 <span class="mono">plugin</span> 是 CORE 朝外开的两扇门：<span class="mono">sdk</span> 给<strong>客户端</strong>用（"我要调 server"），<span class="mono">plugin</span> 给<strong>第三方扩展</strong>用（"我要往 agent 里塞钩子"）。两扇门都从内核生成或导出类型，所以你写前端、写插件时都有完整的类型提示。</p>
<p>为什么 <span class="mono">core</span> 要单独成包、而不直接长在 <span class="mono">opencode</span> 里？因为 V2 想让内核<strong>不绑定任何具体宿主</strong>：同一个 core，既能被 opencode 的网络 server 包，也能被 cli 进程内驱动，甚至将来搬上云端。把内核抽出来，"一处实现、多处复用"才谈得上。</p>
<p>还有一点值得记一辈子：这些依赖几乎都是<strong>单向</strong>的——客户端依赖 sdk、sdk 依赖 server 的契约、server 依赖 core，反过来却绝不成立。core 永远不知道谁在用它，tui 的任何改动也烧不到内核。<strong>依赖只朝一个方向流</strong>，正是这套架构能拆能换、能同时养活一堆前端的根本原因。</p>
<p>真要动手读 CORE，建议<strong>从 <span class="mono">core</span> 入手，而不是从 <span class="mono">opencode</span></strong>：前者是 V2 想长久留下的内核，结构干净、边界清楚；后者背着 V1 的历史包袱，读起来更杂。先在 core 里把"会话、工具、系统上下文"几条主线摸清，再回头看 opencode 如何把它们接上 CLI 与服务器，思路会顺很多。</p>

<h2>周边三组：客户端 / 云端 / 基础库</h2>
<p>看懂 CORE 之后，周边就轻松了——它们都<strong>不在你本地的运行时路径上</strong>，可以等需要时再翻：</p>
<p>把周边整组先搁一边，不是说它们不重要，而是<strong>它们的复杂度彼此独立</strong>：你不懂 Electron 也能读懂 agent 循环，不懂 Cloudflare 也能读懂会话存储。这种"可以分开理解"的性质，正是好的模块划分留给读者的礼物——它让你一次只扛一份认知负担，而不必把整座城同时塞进脑子。</p>
<div class="cols">
  <div class="col"><h4>客户端 · 脸</h4><p><strong>tui</strong>（SolidJS + opentui 富终端）· <strong>cli</strong>（lildax 二进制）· <strong>app</strong>（SolidJS 网页 UI）· <strong>ui</strong>（渲染库：markdown / diff / shiki / katex）· <strong>desktop</strong>（Electron 壳）· <strong>web</strong>（Astro + Starlight 官网/文档）</p></div>
  <div class="col"><h4>云端 · 集成</h4><p><strong>enterprise</strong>（Hono + SolidStart on Cloudflare）· <strong>function</strong>（CF functions：GitHub app 鉴权）· <strong>slack</strong>（Slack 机器人）· <strong>console</strong> · <strong>identity</strong> · <strong>containers</strong> · <strong>stats</strong></p></div>
  <div class="col"><h4>基础库</h4><p><strong>effect-drizzle-sqlite</strong> 与 <strong>effect-sqlite-node</strong>（Effect↔DB 胶水）· <strong>http-recorder</strong>（录制/回放 HTTP，给 LLM 测试用）· <strong>script</strong>（构建/发布）· <strong>storybook</strong></p></div>
</div>
<p>客户端为什么这么多张脸？因为"把 agent 抽成服务"之后，加一张脸的成本极低——它们共享同一套 sdk 与事件流，于是终端党有 tui、桌面党有 desktop、团队协作有 slack，各取所需，却不必各写一遍 agent 逻辑（呼应第 1 课）。</p>
<p>这里藏着一个好设计：<span class="mono">app</span> 是真正的网页应用，<span class="mono">ui</span> 是被抽出来的<strong>渲染组件库</strong>——markdown、diff、语法高亮、数学公式只实现一次，就能同时喂给网页、终端 TUI 和桌面三种脸。</p>
<p>基础库与云端也各有看点：<span class="mono">effect-drizzle-sqlite</span> 这类包，把 core 的持久化地基<strong>抽成可复用的独立库</strong>（第九部分会站在它们之上）；<span class="mono">http-recorder</span> 用"磁带"录下 provider 的 HTTP 往返，让 LLM 层的测试<strong>不烧 token、可复现</strong>。而那一整组云端包跑在 Cloudflare 或作为机器人——<strong>本地跑 opencode 时它们一个都不会启动</strong>，读内核时尽管略过。</p>
<p>云端这组是 opencode 的"<strong>云上半边</strong>"：<span class="mono">enterprise</span> 做团队版与共享，<span class="mono">function</span> 处理 GitHub app 的鉴权回调，<span class="mono">stats</span> 收匿名用量，<span class="mono">identity</span> 与 <span class="mono">console</span> 管账户和控制台。它们都和本地内核解耦，所以你完全可以只用本地、一行云端代码都不碰。</p>
<p>一个常被忽略的点：<span class="mono">cli</span> 这个包<strong>跨了两重身份</strong>——它既是一张"脸"（你敲的命令行），又把 core + server 打包进自己进程。于是它同时带着客户端与宿主两个角色。这正是 V2 想要的形态：一个二进制、自带 server，连网络服务都不必先起（第 13 课）。</p>
<p>云端这组里还藏着一个容易混淆的点：<span class="mono">console</span>、<span class="mono">stats</span> 这些名字下面其实<strong>各自又是一棵小树</strong>，里面再分 app / core / server。所以"约 24 个包"只是顶层的粗略口径，真要细数还能更多——但对建立地图来说，记住顶层这层就够了，钻进子树是具体那一课的事。</p>
<p>基础库这一组还体现了 opencode 的另一种工程习惯：<strong>把通用能力沉淀成独立小包</strong>。数据库访问、HTTP 录放、构建脚本，本可以散在各处随手写，它却特意抽出来、单独命名、单独测试。地基足够稳，上层才敢放心踩着它们盖楼——这也是为什么读到第九部分时，你会觉得持久化层格外清爽。</p>

<h2>这张地图怎么用</h2>
<p>把真实的 <span class="mono">packages/</span> 目录按角色上个色，就是下面这张"全景小抄"——CORE 高亮、客户端暖色、云端蓝色、基础库灰一档：</p>
<div class="cellgroup">
  <div class="cg-cap">真实的 <b>packages/</b> 目录（按角色着色）</div>
  <div class="cells">
    <div class="cell hl">opencode</div><div class="cell hl">core</div><div class="cell hl">llm</div><div class="cell hl">server</div><div class="cell hl">sdk</div><div class="cell hl">plugin</div>
    <span class="lab">CORE</span>
  </div>
  <div class="cells">
    <div class="cell scale">tui</div><div class="cell scale">cli</div><div class="cell scale">app</div><div class="cell scale">ui</div><div class="cell scale">desktop</div><div class="cell scale">web</div>
    <span class="lab">客户端</span>
  </div>
  <div class="cells">
    <div class="cell q">enterprise</div><div class="cell q">function</div><div class="cell q">slack</div><div class="cell q">console</div><div class="cell q">identity</div><div class="cell q">containers</div><div class="cell q">stats</div>
    <span class="lab">云端</span>
  </div>
  <div class="cells">
    <div class="cell">effect-drizzle-sqlite</div><div class="cell">effect-sqlite-node</div><div class="cell">http-recorder</div><div class="cell">script</div><div class="cell">storybook</div>
    <span class="lab">基础库</span>
  </div>
</div>
<p>真正读起来，这份指南就是顺着 CORE 一个个把包拆开。记住这条"后面去哪找"的路线，地图就活了：</p>
<div class="vflow">
  <div class="step"><b>server · sdk → 第三部分</b>　server 骨架、路由、SSE 事件总线、SDK 生成</div>
  <div class="step"><b>core → 第四、五部分 ★</b>　V2 会话内核：agent 循环 + System Context / Context Epoch</div>
  <div class="step"><b>llm → 第六部分 ★</b>　自研多协议模型层：协议适配、流式、路由</div>
  <div class="step"><b>core 的工具 / 配置 / 存储 → 第七、八、九部分</b>　让 agent 真能干活、能配置、记得住</div>
  <div class="step"><b>tui → 第十部分；plugin / LSP / MCP → 第十一部分</b>　终端渲染与扩展生态</div>
</div>
<p>举个例子：你想搞清"一次工具调用到底怎么跑"。顺着地图——它在 <span class="mono">core</span> 的 agent 循环里（第四部分），工具的定义与注册在第七部分，要<strong>并发</strong>跑多个工具又牵出 llm 与 Effect 的并发原语（第六、二部分）。地图的价值，就是把一个模糊的问题<strong>翻译成几个明确的落点</strong>。</p>
<p>所以这一课真正想交给你的，不是 24 个包名的清单，而是一种<strong>看待陌生大仓库的姿势</strong>：先问"哪些在运行时真的会跑"，圈出那一小撮核心；再把其余按"脸 / 云 / 库"归类、安心推迟。带着这张地图往下走，后面每一课都像往早已画好的格子里填字——这正是从"被代码淹没"到"在代码里散步"的分界线。</p>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  opencode 的 monorepo = <strong>四个角色分区</strong>：<strong>CORE</strong>（opencode · core · llm · server · sdk · plugin，唯一在运行时 agent 路径上）+ <strong>客户端</strong>（多张脸）+ <strong>云端集成</strong>（跑在别处）+ <strong>基础库</strong>（复用地基）。依赖只朝一个方向流：<strong>客户端 → sdk → server → core(+llm) → provider</strong>。读这个仓库的第一把筛子，就是先盯住 6 个 CORE 包，其余等用到再查。
</div>

<div class="card detail">
  <div class="tag">🔬 细节 / 源码对应</div>
  这张地图的"行政区划"，直接写在仓库根的 <span class="inline">package.json</span> 与 <span class="inline">turbo.json</span> 里：workspaces 圈定哪些目录算包，turbo 的 tasks 则定义全仓怎么 <span class="mono">typecheck / build / test</span>：
<pre class="code"><span class="cm">// 简化自 仓库根 package.json</span>
{
  <span class="st">"workspaces"</span>: { <span class="st">"packages"</span>: [
    <span class="st">"packages/*"</span>,          <span class="cm">// core·llm·server·tui·sdk·opencode …</span>
    <span class="st">"packages/console/*"</span>,   <span class="cm">// 控制台子应用树</span>
    <span class="st">"packages/stats/*"</span>,
    <span class="st">"packages/sdk/js"</span>, <span class="st">"packages/slack"</span>
  ] }
}
<span class="cm">// 简化自 turbo.json —— 一张构建任务图</span>
{ <span class="st">"tasks"</span>: {
  <span class="st">"typecheck"</span>: {},
  <span class="st">"build"</span>: { <span class="st">"outputs"</span>: [<span class="st">"dist/**"</span>] },
  <span class="st">"opencode#test"</span>: { <span class="st">"dependsOn"</span>: [<span class="st">"^build"</span>] }  <span class="cm">// 先 build 上游</span>
} }</pre>
  <span class="mono">"packages/*"</span> 一行就把 <span class="mono">packages/</span> 下每个带 <span class="mono">package.json</span> 的目录纳为工作区；<span class="mono">opencode#test</span> 的 <span class="mono">dependsOn: ["^build"]</span> 则告诉 turbo："测 opencode 前，先 build 它依赖的上游包"——一句配置，就把包之间的依赖顺序交给了构建系统。根 <span class="mono">package.json</span> 里还有一张 <span class="mono">catalog</span>，把 Effect、SolidJS 等公共依赖的版本统一钉死、全仓共用——这也是 monorepo 省心的一处。
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>opencode 是 <strong>Bun + turborepo</strong> 的 monorepo，约 <strong>24 个包</strong>按角色分四组。</li>
    <li><strong>CORE 六包</strong>（opencode · core · llm · server · sdk · plugin）是唯一在运行时 agent 路径上的——读内核先看它们。</li>
    <li><strong>opencode</strong> 既是核心包又是 server 宿主、还扛着 V1；<strong>core</strong> 是 V2 内核（第 4 课）。</li>
    <li>依赖单向流：<strong>客户端 → sdk → server → core(+llm) → provider</strong>；sdk 在构建时反向从 server 生成。</li>
    <li>周边 = 客户端的脸 / 云端服务 / 基础库，<strong>本地跑 prompt 时多数不参与</strong>。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Last lesson we locked in one through-line — the client sends a message, the server runs the agent loop, events stream back. But the moment you actually clone opencode and open <span class="mono">packages/</span>, you slam into <strong>twenty-some packages</strong> with no idea where to look. This lesson hands you a <strong>map</strong>: it sorts those packages into four role groups and marks who depends on whom, which sit on the "runtime agent path," and which are mere periphery. Memorize this map and, whenever a later lesson names a package, you'll know exactly where it hangs.</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  Picture this monorepo as a <strong>zoned city</strong>. <strong>Downtown</strong> (CORE) is where work actually happens — city hall, the power plant, the water utility; these are the packages that run every time you "do a job with opencode." The <strong>storefronts</strong> (clients) are the faces citizens see: terminal, web, desktop, Slack — different shapes, all wired to downtown. The <strong>overseas branches</strong> (cloud integrations) operate in another country (Cloudflare); running opencode locally never disturbs them. The <strong>underground utilities</strong> (infra libs) everyone uses but nobody thinks about daily. And <strong>turborepo</strong> is the city's traffic control, deciding which roads to repave when you change one thing.
</div>

<h2>One repo, twenty-some packages</h2>
<p>opencode is a <strong>Bun + turborepo monorepo</strong>: one git repo holding about <strong>24 packages</strong>, all under <span class="mono">packages/</span>. Why not split into dozens of separate repos? Because the packages <strong>share types</strong> — change one server endpoint and the sdk regenerates, the clients' types break immediately, and a <strong>single commit</strong> carries a change across the "client/server" line with no publishing and no version juggling.</p>
<p>One <span class="mono">bun install</span> wires every dependency; one turbo task graph unifies <span class="mono">typecheck / build / test</span>. The root <span class="mono">package.json</span> workspaces even fold in "sub-app trees" like <span class="mono">packages/console/*</span> and <span class="mono">packages/stats/*</span> — so "24 packages" is approximate: console and stats each split internally into app / core / server.</p>
<div class="flow">
  <div class="node"><div class="nt">bun install</div><div class="nd">wire the whole repo once</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">turbo typecheck</div><div class="nd">type-check every package</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">turbo build</div><div class="nd">emit dist/**</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">turbo test</div><div class="nd">dependsOn ^build</div></div>
</div>
<p>Notice that trailing <span class="mono">^build</span>: turbo says "before testing a package, build its <strong>upstream</strong> dependencies first." In other words, the build graph itself encodes the <strong>dependency DAG</strong> between packages — when you can't tell what depends on what, <span class="mono">turbo.json</span> is a ready-made map.</p>
<p>A monorepo isn't free, though — pack 24 packages together and the nightmare is "change one line, rebuild everything." opencode beats that with two things: <strong>Bun</strong> makes install and bundling fast, and <strong>turbo</strong> does <strong>incremental caching</strong> by content hash, re-running only the packages actually affected. So the repo is big, yet a routine <span class="mono">typecheck</span> usually returns in seconds.</p>
<p>Flip it around: if server, sdk, and tui were three separate npm packages, changing one server endpoint would mean publishing server, upgrading sdk, then upgrading tui — three PRs, three version bumps. The monorepo collapses all that into <strong>one commit</strong>. For a project mid V1→V2 rebuild, that "atomic change" is close to a necessity.</p>
<p>One more consistent choice: it uses <strong>Bun workspaces</strong>, not npm/pnpm. Bun is package manager, runtime, and bundler at once, so the whole toolchain is a single <span class="mono">bun</span> command — the same taste as Lesson 1's "one binary, easy to install."</p>
<p>Ultimately the monorepo is opencode's bet on <strong>fast evolution</strong>: when a project is still reshaping its architecture and its interfaces change weekly, cramming all the related code into one repo under one toolchain is far less painful than maintaining a dozen separate, version-juggling packages. The trade is clear — <strong>a little build complexity in exchange for flexible, consistent repo-wide change</strong>.</p>
<p>And don't let the package count scare you: the only ones you truly need to <strong>read end to end</strong> are that small core; most of the rest you may never open twice across this guide. A repo's <strong>size</strong> and the <strong>attention</strong> it demands of you were never the same thing — telling them apart is the first step to not being scared off by a large codebase.</p>

<h2>Four role groups</h2>
<p>Spread the 24 packages out by <strong>role</strong> and there are really only four kinds: ① <strong>CORE</strong> — packages on the "runtime agent path," executed every time you run a prompt; ② <strong>clients</strong> — the faces connecting to the server; ③ <strong>cloud / integrations</strong> — services on Cloudflare or running as bots; ④ <strong>infra libs</strong> — reused tooling. Place a package in its bucket first and you won't get lost among the 24.</p>
<p>This four-way split looks trivial, but its value is <strong>giving every package a home</strong>: later, when you see a long list of imports at the top of a file, one glance at which groups they pull from tells you whether you're in core logic, some face's rendering, or cloud ops. A map's worth was never memorizing every street name — it's <strong>knowing at a glance which district you're standing in</strong>.</p>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">Clients · faces</span><span class="name">tui · cli · app · ui · desktop · web</span></div>
    <div class="ld">Collect your input, render the server's event stream — many faces of one kernel</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">CORE · runtime path</span><span class="name">opencode · core · llm · server · sdk · plugin</span></div>
    <div class="ld">Agent loop, sessions, model access, server contract — only this group runs a prompt</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">Cloud · integrations</span><span class="name">enterprise · function · slack · console · identity · containers · stats</span></div>
    <div class="ld">Deployed on Cloudflare or as bots/services; the local kernel never touches them</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">Infra libs</span><span class="name">effect-drizzle-sqlite · effect-sqlite-node · http-recorder · script · storybook</span></div>
    <div class="ld">Reused foundations: DB glue, HTTP record/replay, build scripts, component workshop</div></div>
</div>
<p>Why split by <strong>role</strong> rather than by language or stack? Because the same technology is scattered across roles — SolidJS lives in both tui and app, Effect in both core and cli. What actually decides "do I care about this while reading source" is whether the package <strong>runs at runtime</strong>, not what it's written in.</p>
<p>Of these four, the split worth memorizing first is <strong>CORE vs "periphery"</strong> — the cheapest filter for reading this repo:</p>
<div class="cols">
  <div class="col"><h4>CORE (6 · runtime path)</h4><p>opencode · core · llm · server · sdk · plugin. <strong>Only these 6</strong> execute when you run a prompt locally — to understand how the agent works, nine-tenths of the answer is here.</p></div>
  <div class="col"><h4>Periphery (the other ~18)</h4><p>Client faces, cloud services, infra libs. They matter, but they all <strong>orbit CORE</strong>: each is either its front-end, its ops, or a tool it reuses.</p></div>
</div>
<p>How do you place a package at a glance? Check three things: does it <strong>depend on server / core</strong> (likely CORE or a client), does it <strong>deploy to Cloudflare</strong> (cloud), and does it <strong>have its own "face"</strong> (a UI means client; a pure function library means infra). You'll use this test every time a new package shows up.</p>
<p>This line has a practical corollary: <strong>reading this guide, you'll spend nine-tenths of your time inside those 6 CORE packages</strong>. Of the twelve parts ahead, all but Parts 1 and 12 (panorama and engineering) drill into CORE. So learning these 6 names now pays off handsomely.</p>
<p>To be clear, these four groups <strong>aren't cut absolutely cleanly</strong>: some packages wear two identities at once (like <span class="mono">cli</span>, coming up), and some infra libs really serve only one upper layer. But as a <strong>first layer of understanding</strong>, the split is good enough — get the rough map first, fill in details when the specific lesson arrives.</p>

<h2>CORE: the six packages on the runtime path</h2>
<p>CORE's six packages step inward from "shell" to "kernel," each owning one segment. This table is the <strong>trunk index</strong> you'll keep coming back to:</p>
<table class="t">
  <tr><th>Package</th><th>One-line responsibility</th><th>Expanded in</th></tr>
  <tr><td class="mono">opencode</td><td>Main binary: yargs CLI + V1 session engine + <strong>server host</strong> (providers / MCP / LSP live here too)</td><td>Lessons 3, 4</td></tr>
  <tr><td class="mono">core</td><td><strong>V2 Session Core</strong>: Effect services + Drizzle/SQLite + sessions / tools / system-context / pty</td><td>Parts 4-5</td></tr>
  <tr><td class="mono">llm</td><td>In-house, provider-agnostic <strong>multi-protocol LLM client</strong></td><td>Part 6</td></tr>
  <tr><td class="mono">server</td><td><strong>Thin contract layer</strong>: cors, route groups, shared types</td><td>Part 3</td></tr>
  <tr><td class="mono">sdk</td><td>Type-safe TS client <strong>generated</strong> from the server's OpenAPI</td><td>Lesson 12</td></tr>
  <tr><td class="mono">plugin</td><td>The outward-facing <span class="mono">@opencode-ai/plugin</span> SDK</td><td>Part 11</td></tr>
</table>
<p>The most vivid way to see them is to follow one request through all six: your words enter the <span class="mono">opencode</span> / <span class="mono">cli</span> command shell, whose hosted <span class="mono">server</span> receives them; the server hands the work by contract to <span class="mono">core</span>'s session engine; when core needs a model it calls <span class="mono">llm</span>; and llm encodes the request into some provider's protocol. Layer wrapping layer — exactly "shell → kernel."</p>
<p>Another metaphor: the six packages form a <strong>conveyor belt from human to model</strong> — the outer end catches your plain words, the inner end emits protocol bytes for the LLM, and each segment in between does one clearly-defined thing before handing the half-product onward. When a file tangles you up, step back onto the belt and ask "which segment am I in, what did the previous one hand me, what do I owe the next" — clarity usually returns at once.</p>
<p>And because the segments are so clearly delineated, each can be <strong>swapped on its own</strong>: a new provider touches only the innermost segment, a new front-end only the outermost, the middle untouched. This "one segment breaks without dragging the rest down" decoupling is the premise behind many later designs.</p>
<p>An easily-missed detail: <span class="mono">opencode</span> is <strong>both</strong> a core package <strong>and</strong> the host — it carries the entire <strong>V1</strong> engine while embedding <strong>V2's core</strong> as the kernel behind the server. So it straddles the V1/V2 migration line (Lesson 4).</p>
<p>An easter egg: opencode actually ships <strong>two binaries</strong>. <span class="mono">packages/opencode</span> is today's main <span class="mono">opencode</span> command (yargs, V1-leaning); <span class="mono">packages/cli</span> is a second binary called <span class="mono">lildax</span> that uses an Effect command framework to bundle <span class="mono">core + server + tui + sdk</span> — the <strong>V2 entry point taking shape</strong>.</p>
<div class="flow">
  <div class="node"><div class="nt">clients</div><div class="nd">tui · app · desktop · cli</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">sdk</div><div class="nd">generated type-safe client</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">server</div><div class="nd">thin contract layer</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">core (+llm)</div><div class="nd">V2 kernel + model layer</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">provider</div><div class="nd">Anthropic · OpenAI · …</div></div>
</div>
<p>These six packages' <strong>dependencies flow one way</strong>: clients never import <span class="mono">core</span> directly; they call <span class="mono">server</span> through the <strong>generated sdk</strong>, and the server lands on <span class="mono">core</span> and <span class="mono">llm</span>, finally hitting each provider. This is the previous lesson's "client/server" boundary made concrete in package form — and the sdk seam is generated <strong>backward at build time</strong> from the server's OpenAPI (Lesson 12).</p>
<p>Don't be fooled by <span class="mono">server</span>'s "thin": it's thin because <strong>the heavy lifting all lives in core</strong>. The server only translates HTTP requests by contract into calls on core, then encodes core's event stream back into SSE. This "thin shell, thick kernel" cut lets the same core be wrapped by a network server or driven in-process by cli (Lesson 13).</p>
<p><span class="mono">sdk</span> and <span class="mono">plugin</span> are CORE's two outward-facing doors: <span class="mono">sdk</span> is for <strong>clients</strong> ("I want to call the server"), <span class="mono">plugin</span> is for <strong>third-party extensions</strong> ("I want to hook into the agent"). Both generate or export types from the kernel, so writing a front-end or a plugin gives you full type hints.</p>
<p>Why is <span class="mono">core</span> its own package instead of living inside <span class="mono">opencode</span>? Because V2 wants the kernel <strong>bound to no particular host</strong>: one core can be wrapped by opencode's network server, driven in-process by cli, even shipped to the cloud later. Only by extracting the kernel does "implement once, reuse everywhere" become possible.</p>

<p>One more thing worth remembering for life: these dependencies are almost all <strong>one-directional</strong> — clients depend on sdk, sdk on the server's contract, server on core, but never the reverse. core never knows who uses it, and no tui change can singe the kernel. <strong>Dependencies flowing only one way</strong> is precisely why this architecture can be split, swapped, and feed a whole crowd of front-ends at once.</p>
<p>When you actually start reading CORE, begin from <strong><span class="mono">core</span>, not <span class="mono">opencode</span></strong>: the former is the kernel V2 wants to keep for the long run — clean structure, clear boundaries — while the latter still carries V1's historical baggage and reads messier. Trace the "sessions, tools, system-context" throughlines inside core first, then come back to see how opencode wires them to the CLI and server; the path is far smoother.</p>

<h2>The periphery in three groups: clients / cloud / infra</h2>
<p>Once CORE is clear, the periphery is easy — none of it sits on your local runtime path, so flip to it only when needed:</p>
<p>Setting the whole periphery aside doesn't mean it's unimportant — it means <strong>its complexity is mutually independent</strong>: you can grasp the agent loop without knowing Electron, and session storage without knowing Cloudflare. That "understandable in isolation" property is the gift good modular design leaves the reader — it lets you carry one cognitive load at a time instead of cramming the whole city into your head at once.</p>
<div class="cols">
  <div class="col"><h4>Clients · faces</h4><p><strong>tui</strong> (SolidJS + opentui rich terminal) · <strong>cli</strong> (the lildax binary) · <strong>app</strong> (SolidJS web UI) · <strong>ui</strong> (render lib: markdown / diff / shiki / katex) · <strong>desktop</strong> (Electron shell) · <strong>web</strong> (Astro + Starlight site/docs)</p></div>
  <div class="col"><h4>Cloud · integrations</h4><p><strong>enterprise</strong> (Hono + SolidStart on Cloudflare) · <strong>function</strong> (CF functions: GitHub app auth) · <strong>slack</strong> (Slack bot) · <strong>console</strong> · <strong>identity</strong> · <strong>containers</strong> · <strong>stats</strong></p></div>
  <div class="col"><h4>Infra libs</h4><p><strong>effect-drizzle-sqlite</strong> and <strong>effect-sqlite-node</strong> (Effect↔DB glue) · <strong>http-recorder</strong> (record/replay HTTP, for LLM tests) · <strong>script</strong> (build/release) · <strong>storybook</strong></p></div>
</div>
<p>Why so many client faces? Because once you extract the agent into a service, adding a face costs almost nothing — they share the same sdk and event stream, so terminal folk get tui, desktop folk get desktop, teams get slack, each taking what it needs without re-writing agent logic (echoing Lesson 1).</p>
<p>A nice design hides here: <span class="mono">app</span> is the actual web application, while <span class="mono">ui</span> is the extracted <strong>render/component library</strong> — markdown, diffs, syntax highlighting, and math are implemented once, then fed to all three faces: web, terminal TUI, and desktop.</p>
<p>Infra and cloud each repay a look: packages like <span class="mono">effect-drizzle-sqlite</span> factor core's persistence foundation into <strong>reusable standalone libs</strong> (Part 9 builds on them); <span class="mono">http-recorder</span> tapes provider HTTP round-trips so the LLM layer's tests <strong>burn no tokens and stay reproducible</strong>. And that whole cloud group runs on Cloudflare or as bots — <strong>none of it starts when you run opencode locally</strong>, so skip it while reading the kernel.</p>
<p>The cloud group is opencode's "<strong>upper half in the cloud</strong>": <span class="mono">enterprise</span> handles the team edition and sharing, <span class="mono">function</span> handles the GitHub app's auth callbacks, <span class="mono">stats</span> collects anonymous usage, and <span class="mono">identity</span> and <span class="mono">console</span> manage accounts and the console. All are decoupled from the local kernel, so you can stay fully local and touch not a line of cloud code.</p>
<p>An often-missed point: the <span class="mono">cli</span> package <strong>spans two identities</strong> — it's both a "face" (the command line you type) and a host that bundles core + server into its own process. So it carries the client and host roles at once. This is exactly the V2 shape: one binary, server included, no network service to start first (Lesson 13).</p>
<p>The cloud group hides one easily-confused point: names like <span class="mono">console</span> and <span class="mono">stats</span> are each <strong>a little tree of their own</strong>, further split into app / core / server inside. So "about 24 packages" is just the rough top-level count — count finely and there are more. But for building a map, the top level is enough; diving into the sub-trees is a job for the specific lesson.</p>
<p>The infra group also reflects another opencode habit: <strong>distilling general capability into standalone packages</strong>. Database access, HTTP record/replay, build scripts — all could have been scribbled inline here and there, yet they're deliberately extracted, named, and tested on their own. Only with a solid foundation do upper layers dare build on top — which is why the persistence layer feels so clean when you reach Part 9.</p>

<h2>How to use this map</h2>
<p>Color the real <span class="mono">packages/</span> directory by role and you get this "panorama cheat-sheet" — CORE highlighted, clients warm, cloud blue, infra dimmed a notch:</p>
<div class="cellgroup">
  <div class="cg-cap">The real <b>packages/</b> directory (colored by role)</div>
  <div class="cells">
    <div class="cell hl">opencode</div><div class="cell hl">core</div><div class="cell hl">llm</div><div class="cell hl">server</div><div class="cell hl">sdk</div><div class="cell hl">plugin</div>
    <span class="lab">CORE</span>
  </div>
  <div class="cells">
    <div class="cell scale">tui</div><div class="cell scale">cli</div><div class="cell scale">app</div><div class="cell scale">ui</div><div class="cell scale">desktop</div><div class="cell scale">web</div>
    <span class="lab">Clients</span>
  </div>
  <div class="cells">
    <div class="cell q">enterprise</div><div class="cell q">function</div><div class="cell q">slack</div><div class="cell q">console</div><div class="cell q">identity</div><div class="cell q">containers</div><div class="cell q">stats</div>
    <span class="lab">Cloud</span>
  </div>
  <div class="cells">
    <div class="cell">effect-drizzle-sqlite</div><div class="cell">effect-sqlite-node</div><div class="cell">http-recorder</div><div class="cell">script</div><div class="cell">storybook</div>
    <span class="lab">Infra</span>
  </div>
</div>
<p>In practice this guide simply walks CORE, prying open one package at a time. Memorize this "where to find it later" route and the map comes alive:</p>
<div class="vflow">
  <div class="step"><b>server · sdk → Part 3</b>　server skeleton, routes, SSE event bus, SDK generation</div>
  <div class="step"><b>core → Parts 4-5 ★</b>　the V2 session kernel: agent loop + System Context / Context Epoch</div>
  <div class="step"><b>llm → Part 6 ★</b>　the in-house multi-protocol model layer: protocol adapters, streaming, routing</div>
  <div class="step"><b>core's tools / config / storage → Parts 7-9</b>　make the agent actually work, be configured, remember</div>
  <div class="step"><b>tui → Part 10; plugin / LSP / MCP → Part 11</b>　terminal rendering and the extension ecosystem</div>
</div>
<p>For example: you want to understand "how a single tool call actually runs." Follow the map — it's in <span class="mono">core</span>'s agent loop (Part 4), the tool's definition and registry are in Part 7, and running several tools <strong>concurrently</strong> pulls in llm and Effect's concurrency primitives (Parts 6 and 2). The map's value is turning one vague question into a few precise landing spots.</p>
<p>So what this lesson really hands you isn't a list of 24 package names, but a <strong>posture for facing any large unfamiliar repo</strong>: first ask "which actually run at runtime" and circle that small core; then bucket the rest into "faces / cloud / libs" and defer them with a clear conscience. Carry this map forward and every later lesson feels like filling words into a grid already drawn — exactly the line between "drowning in code" and "strolling through it."</p>

<div class="card macro">
  <div class="tag">🌍 Big picture</div>
  opencode's monorepo = <strong>four role groups</strong>: <strong>CORE</strong> (opencode · core · llm · server · sdk · plugin, the only one on the runtime agent path) + <strong>clients</strong> (many faces) + <strong>cloud integrations</strong> (run elsewhere) + <strong>infra libs</strong> (reused foundations). Dependencies flow one way: <strong>clients → sdk → server → core(+llm) → provider</strong>. The first filter for reading this repo is to lock onto the 6 CORE packages and look up the rest only when needed.
</div>

<div class="card detail">
  <div class="tag">🔬 Source detail</div>
  This map's "zoning" is written directly into the repo-root <span class="inline">package.json</span> and <span class="inline">turbo.json</span>: workspaces decide which directories count as packages, and turbo's tasks define how the whole repo runs <span class="mono">typecheck / build / test</span>:
<pre class="code"><span class="cm">// simplified from repo-root package.json</span>
{
  <span class="st">"workspaces"</span>: { <span class="st">"packages"</span>: [
    <span class="st">"packages/*"</span>,          <span class="cm">// core·llm·server·tui·sdk·opencode …</span>
    <span class="st">"packages/console/*"</span>,   <span class="cm">// console sub-app tree</span>
    <span class="st">"packages/stats/*"</span>,
    <span class="st">"packages/sdk/js"</span>, <span class="st">"packages/slack"</span>
  ] }
}
<span class="cm">// simplified from turbo.json — one build task graph</span>
{ <span class="st">"tasks"</span>: {
  <span class="st">"typecheck"</span>: {},
  <span class="st">"build"</span>: { <span class="st">"outputs"</span>: [<span class="st">"dist/**"</span>] },
  <span class="st">"opencode#test"</span>: { <span class="st">"dependsOn"</span>: [<span class="st">"^build"</span>] }  <span class="cm">// build upstream first</span>
} }</pre>
  The single line <span class="mono">"packages/*"</span> enrolls every directory under <span class="mono">packages/</span> that has a <span class="mono">package.json</span> as a workspace; <span class="mono">opencode#test</span>'s <span class="mono">dependsOn: ["^build"]</span> tells turbo "before testing opencode, build its upstream deps" — one line of config hands the inter-package build order to the build system. The root <span class="mono">package.json</span> also carries a <span class="mono">catalog</span> that pins shared dependency versions (Effect, SolidJS, and so on) once for the whole repo — another way the monorepo saves trouble.
</div>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>opencode is a <strong>Bun + turborepo</strong> monorepo, ~<strong>24 packages</strong> in four role groups.</li>
    <li>The <strong>six CORE packages</strong> (opencode · core · llm · server · sdk · plugin) are the only ones on the runtime agent path — read them first.</li>
    <li><strong>opencode</strong> is both a core package and the server host, and still carries V1; <strong>core</strong> is the V2 kernel (Lesson 4).</li>
    <li>Dependencies flow one way: <strong>clients → sdk → server → core(+llm) → provider</strong>; the sdk is generated backward from the server at build time.</li>
    <li>The periphery = client faces / cloud services / infra libs, <strong>mostly idle when you run a prompt locally</strong>.</li>
  </ul>
</div>
""",
}
LESSON_03 = {
    "zh": r"""
<p class="lead">前两课你拿到了全景图。现在我们做一件最能打通任督二脉的事：<strong>跟着一条 prompt 走完全程</strong>。你在 TUI 敲下"帮我修个 bug"回车，到屏幕上一个字一个字地冒出回复——中间这一路，请求<strong>自上而下</strong>穿过整座塔，结果再<strong>自下而上</strong>冒回来，而最关键的中段会<strong>反复循环</strong>。把这一趟看清楚，后面 61 课你都知道自己正站在哪一跳。</p>
<p>为什么值得为"一次对话"专门花一整课？因为它是 opencode 所有复杂度的<strong>汇合点</strong>：传输层、路由、上下文组装、模型协议、工具执行、并发调度、持久化、前端渲染——几乎每一个子系统，都会在这趟短短几秒的旅程里露一次脸。先把这条<strong>主干道</strong>从头到尾走通，建立起"谁在前、谁在后、谁会重复"的骨架感，再回头逐个深挖那些岔路，你就不会"只见树木、不见森林"。可以说，这一课是后面所有深水区课程的<strong>导览图</strong>：每讲一个模块，你都能把它精准地挂回这趟旅程的某一跳上。</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  把一次对话想成餐厅里的<strong>一张点单</strong>。你（客户端）把单子递进窗口；<strong>领班</strong>（server）登记、把它送进后厨；<strong>主厨</strong>（大模型）看一眼说"先去拿食材"——但主厨只发指令、不亲自跑腿，<strong>打荷</strong>（工具执行）替他取菜、切配、下锅，再把半成品端回来给主厨看；主厨接着说下一步……如此往返几轮，直到主厨说"出餐"。整个过程后厨的每个动作都<strong>实时报给前台</strong>，你在座位上就能看到"备菜中、烹饪中、即将上桌"。
</div>

<h2>鸟瞰：一座塔，上下各一趟</h2>
<p>先把整条路压成一张图。请求从最上面的客户端出发，逐层下沉到模型；模型要调工具时，结果又逐层上浮、再下沉——<strong>下行是"请求"，上行是"结果与事件"</strong>。这趟往返的中段（组装上下文 → 调模型 → 执行工具）会重复多次，直到模型不再要工具。</p>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">① 客户端</span><span class="name">TUI prompt 组件 · app.tsx</span></div>
    <div class="ld">收按键、提交 prompt；订阅事件流往屏幕上画</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">②③ 传输 + server</span><span class="name">RPC worker · Effect HttpApi</span></div>
    <div class="ld">把请求送进 server 的 session 路由组；事件经 SSE/RPC 回流</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">④–⑩ 会话引擎</span><span class="name">input → coordinator → runner/llm.ts</span></div>
    <div class="ld">组装上下文、跑 agent 循环、执行工具、持久化</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">⑥⑦ 模型接入</span><span class="name">LLM 协议层 · provider</span></div>
    <div class="ld">编码成 provider 协议、流式拿回 LLMEvent</div></div>
</div>
<div class="cols">
  <div class="col"><h4>↓ 下行（请求）</h4><p>按键 → 序列化成 HTTP 请求 → session handler → 投影历史 + System Context → LLM 请求 → provider。一路<strong>把意图收拢</strong>。</p></div>
  <div class="col"><h4>↑ 上行（结果 / 事件）</h4><p>流式 token、工具结果、持久化产生的事件 → GlobalBus → SSE → TUI 批量渲染。一路<strong>把进展广播</strong>。</p></div>
</div>
<p>这张"下行 / 上行"图，是读懂 opencode 最省力的心智模型。<strong>下行是一个收敛的过程</strong>：你模糊的一句"帮我修个 bug"，经过会话登记、历史投影、上下文渲染，被一步步<strong>翻译成模型能吃的精确请求</strong>；每往下一层，信息就更结构化一分，最终收拢成一次干净的模型调用。</p>
<p><strong>上行则是一个发散的过程</strong>：模型吐出的文本碎片、工具跑出的结果、持久化顺手产生的记录，被打散成一个个<strong>事件</strong>向上广播，谁订阅谁就看得到。两股流方向相反、却同时进行——下行在"问"，上行在"答与报告"。后面每讲一个模块，你都可以先问自己：它在下行还是上行？属于哪一层？理解立刻就有了坐标。这也是为什么这趟旅程值得在第一部分就走一遍：它是整本书的<strong>地图坐标系</strong>。</p>

<h2>第 1–3 跳：从按键到 server</h2>
<p>你敲下的字符先落进 TUI 的 prompt 组件（<span class="mono">packages/tui/src/component/prompt</span>）。回车后，TUI 不是发网络请求——富终端有个巧妙设计：<strong>server 就跑在同一进程的一个 Worker 里</strong>。<span class="mono">cli/cmd/tui.ts</span> 用 <span class="mono">createWorkerFetch</span> 把 SDK 的 <span class="mono">fetch</span> 偷偷换成"对 Worker 发 RPC"，于是前端代码照常调 SDK，底层却<strong>零网络开销</strong>（第 13 课细讲）。</p>
<div class="flow">
  <div class="node"><div class="nt">按键</div><div class="nd">prompt 组件</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">createWorkerFetch</div><div class="nd">SDK.fetch → RPC</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">worker.ts</div><div class="nd">Server.listen</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">HttpApi</div><div class="nd">session 路由组</div></div>
</div>
<p>worker（<span class="mono">cli/tui/worker.ts</span>）里跑着真正的 <span class="mono">Server.listen</span>，还顺手架了条回程：<span class="mono">GlobalBus.on("event", e =&gt; Rpc.emit("global.event", e))</span>——server 内部每冒一个事件，就经 RPC 推回前端。server 本身（<span class="mono">server/server.ts</span>）<strong>不是 Hono</strong>，而是 Effect 的 <span class="mono">HttpApi + OpenApi</span> 架在 <span class="mono">NodeHttpServer</span> 上（第 9 课）。</p>
<p>为什么富 TUI 要这么绕——明明可以起个本地 HTTP server、前端用 fetch 连过去？因为那样要占端口、要处理网络错误、还多一层序列化开销。</p>
<p>opencode 的取巧之处在于：让 server 跑在<strong>同进程的一个 Worker 线程</strong>里，再把 SDK 底层的 <span class="mono">fetch</span> 偷换成"对 Worker 发一条 RPC 消息"。这样前端代码<strong>一行都不用改</strong>——它以为自己在调一个普通的 HTTP SDK，底层却是进程内通信：零网络、零端口、还自动复用 server 那套完整的类型化接口。妙就妙在它<strong>可逆</strong>：当你用 <span class="mono">opencode serve</span> 把 server 起成真正的网络服务时，同一套 SDK 又能无缝改走真 HTTP，前端依旧无感。<strong>同一接口、两种传输</strong>——这是 opencode "一个内核多张脸"在传输层的精确落地，第 13 课会把这套 worker 机制整段拆开。</p>

<h2>第 4–7 跳：组装上下文，开口问模型</h2>
<p>请求进了 session handler，就交给 V2 会话引擎。它不直接"调模型"，而是先走三步准备：</p>
<table class="t">
  <tr><th>跳</th><th>做什么</th><th>源码锚点</th></tr>
  <tr><td>④ 收件箱</td><td>prompt 先落成一条<strong>事件溯源</strong>的输入记录，再唤醒运行器</td><td><span class="mono">session/input.ts</span> → <span class="mono">run-coordinator.ts</span></td></tr>
  <tr><td>⑤ 上下文</td><td>渲染<strong>基线 System Context</strong>（指令、日期、skill…）</td><td><span class="mono">system-context/index.ts</span></td></tr>
  <tr><td>⑥ 建请求</td><td>把投影历史翻译成 LLM 消息、解析模型</td><td><span class="mono">runner/to-llm-message.ts</span> · <span class="mono">model.ts</span></td></tr>
  <tr><td>⑦ 发起流</td><td><span class="mono">llm.stream()</span> 经协议适配器发给 provider</td><td><span class="mono">llm/src/route/client.ts</span></td></tr>
</table>
<p>第 ⑦ 跳拿回的不是一坨完整答复，而是一条<strong>流</strong>——类型签名直白地写着 <span class="mono">Stream.Stream&lt;LLMEvent, LLMError&gt;</span>：文本碎片、推理、工具调用请求、用量，全都作为一个个 <span class="mono">LLMEvent</span> 陆续吐出来。server 一边收一边<strong>增量持久化</strong>，所以哪怕中途断了也不全丢。</p>
<p>这里值得停一下：第 ⑦ 跳为什么是"流"而不是"一次性返回"？因为大模型是<strong>逐 token 生成</strong>的，等它整段写完再返回，你就得干等十几秒、屏幕上什么也没有。流式则让 server 一拿到碎片就<strong>边收、边持久化、边发事件</strong>，于是你几乎瞬间看到第一个字往外蹦。更关键的是，<strong>工具调用也藏在这条流里</strong>——模型可能写了半句话，突然插一句"我要调 edit 工具"，runner 必须在流的<strong>中途</strong>就把它揪出来执行，而不能等整段说完。所以这一跳的真实姿态不是"问完、等、拿答案"，而是"<strong>一边听、一边记、一边随时准备干活</strong>"。把这点想清楚，你才会理解为什么 V2 的 runner 不是一个简单的 request/response 函数，而是一台围着事件流转的状态机。</p>
<p>还有一步"隐形的准备"值得点名：第 ⑤ 跳的 <strong>System Context</strong>。模型并不是只看你这一句话——在你的话被发出去之前，server 会先渲染一段<strong>基线系统上下文</strong>：当前日期、项目里的 <span class="mono">AGENTS.md</span> 指令、可用的 skill 清单、当前是 build 还是 plan agent 等等，拼在整段对话的最前面。它就像每次问诊前先递给医生的一份病历，让模型"开口就懂你的处境"。这段上下文怎么组装、变了之后又怎么增量地通知模型，是 opencode 最独特的设计之一，第五部分整章都在讲它。这里你只需记住：<strong>每次开口问模型之前，都有一段你看不见、却至关重要的上下文被悄悄拼上去</strong>。</p>

<h2>第 8–10 跳：agent 循环的心跳</h2>
<p>这是整趟旅程的<strong>心脏</strong>。当流里出现一个"工具调用"事件，runner 不会傻等，而是把它丢进一个 <span class="mono">FiberSet</span> <strong>并发</strong>地执行（同一步要"读三个文件"就三个一起跑）；工具由 <span class="mono">ToolRegistry</span> 落实，危险操作先过权限闸门。等这一轮工具都结算完，runner <strong>重新加载投影历史</strong>、再开<strong>下一个</strong> provider turn——把工具结果喂回去让模型接着想。</p>
<div class="vflow">
  <div class="step"><b>组装</b>　reload 投影历史 + System Context</div>
  <div class="step"><b>问一轮</b>　一次 <span class="mono">llm.stream(request)</span></div>
  <div class="step"><b>干活</b>　tool-call → FiberSet 并发 settle → 持久化结果</div>
  <div class="step"><b>判断</b>　还有工具调用？是→回到顶；否→收尾</div>
  <div class="step"><b>护栏</b>　步数 &lt; <span class="mono">MAX_STEPS = 25</span>，否则 StepLimitExceeded</div>
</div>
<p>这条"<strong>问一轮 → 干一轮 → 再问</strong>"的循环，正是第 1 课说的 agent 循环。它最多转 25 圈（一个硬护栏，防止模型无限调工具打转），第 17 课会把 <span class="mono">runner/llm.ts</span> 一行行拆开。</p>
<p>两个设计选择特别能体现 V2 的考量。其一，工具用 <span class="mono">FiberSet</span> <strong>并发</strong>执行而非排队：模型一步里要"读 a、读 b、读 c"时，三个读操作同时跑、一起回来，既更快，也让模型一次看到更完整的上下文。</p>
<p>其二，每轮结束要<strong>重新加载投影历史</strong>再续问，而不是把工具结果直接拼到内存里的消息数组上——因为历史才是<strong>持久化的事实来源</strong>，重新投影能保证：即使进程崩了重启、或有别的输入半路插进来，模型下一轮看到的永远是"当前最准的会话状态"。这两点都指向同一种克制：<strong>不依赖内存里的临时状态，一切以持久化为准</strong>。这种"以事实为准、可随时重建"的思路，是 V2 相对 V1 最大的气质差别，第四部分会反复印证。</p>
<p>循环转起来之后，你并不是只能干等。opencode 允许你<strong>中途插话</strong>——模型还在干活时，你再敲一句"等等，先别动那个文件"，这条新输入会作为一条新的收件箱记录被接住，在下一个<strong>安全边界</strong>融入当前活动，悄悄改变接下来的走向。这正是为什么第 ④ 跳要把输入做成<strong>事件溯源的收件箱</strong>，而不是一个普通的函数参数：因为"对话"本质上是<strong>可以随时被你插队、纠偏的活物</strong>，而不是一道发出去就只能等结果的命令。这种"随时可被引导"的手感，是 agent 好不好用的关键，也是 V2 在并发模型上反复打磨的原因。</p>

<h2>第 11 跳：事件流回，画到屏上</h2>
<p>循环每推进一点，增量持久化就<strong>顺手发事件</strong>到 <span class="mono">GlobalBus</span>；事件经 SSE 事件组（<span class="mono">groups/event.ts</span>）或 RPC 回程涌向客户端。TUI 在 <span class="mono">context/sdk.tsx</span> 里订阅 <span class="mono">sdk.global.event(...)</span>，但<strong>不是来一个画一个</strong>——它按 ~16ms 一帧<strong>攒一批再渲染</strong>，于是你看到的是顺滑的逐字流，而不是疯狂闪烁。</p>
<div class="flow">
  <div class="node"><div class="nt">增量持久化</div><div class="nd">发事件</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">GlobalBus</div><div class="nd">SSE / RPC</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">sdk.global.event</div><div class="nd">订阅</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">16ms 批渲染</div><div class="nd">Solid store → 屏幕</div></div>
</div>
<p>这一跳的"批渲染"也不只是为了好看。事件可能<strong>来得非常密</strong>——逐 token 的文本、工具的进度、用量统计，一秒钟几百条；若来一条就触发一次终端重绘，CPU 会被刷屏拖垮、画面还会撕裂。攒够 ~16ms（约一帧）再统一渲染，既省算力又顺滑。而这套"<strong>一切先成事件</strong>"的回流机制还有个隐藏红利：因为每个状态变化都广播了出去，<strong>多个客户端能同时盯着同一个会话</strong>，断线重连也只需重放事件就能追上进度。你甚至可以一边在 TUI 里看、一边在网页端打开同一个会话——两边追的是同一条事件流。第三部分讲事件总线、第十部分讲 TUI 渲染时，都会再回到这一跳。</p>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  一次对话 = <strong>一趟下行的请求</strong> + <strong>中段反复的 agent 循环</strong> + <strong>一路上行的事件流</strong>。下行把意图收拢到一次 <span class="mono">llm.stream</span>；中段"问一轮、干一轮"最多转 25 圈；上行让每个状态变化都先成事件、再被持久化与渲染。看任何一课，先问自己：我现在站在这趟旅程的哪一跳？
</div>

<div class="card detail">
  <div class="tag">🔬 细节 / 源码对应</div>
  把第 8–10 跳的循环骨架抽出来（大幅简化自 <span class="inline">packages/core/src/session/runner/llm.ts</span>）：
<pre class="code"><span class="cm">// 每个 provider turn 恰好一次 llm.stream；工具并发结算后再续下一轮</span>
<span class="kw">while</span> (openActivity) {
  <span class="kw">for</span> (<span class="kw">let</span> step = 0; step &lt; <span class="fn">MAX_STEPS</span>; step++) {
    <span class="kw">const</span> events = llm.<span class="fn">stream</span>(request)        <span class="cm">// 一轮，拿回 LLMEvent 流</span>
    <span class="kw">for</span> <span class="kw">await</span> (<span class="kw">const</span> e <span class="kw">of</span> events) {
      <span class="kw">if</span> (e.type === <span class="st">"tool-call"</span>)
        toolMaterialization.<span class="fn">settle</span>(e)         <span class="cm">// 丢进 FiberSet 并发执行</span>
      persist(e)                                <span class="cm">// 增量持久化 → 发事件</span>
    }
    <span class="kw">if</span> (!hadToolCalls) <span class="kw">break</span>                  <span class="cm">// 模型不再要工具 → 收尾</span>
    request = <span class="fn">reloadProjectedHistory</span>()        <span class="cm">// 把工具结果喂回，开下一轮</span>
  }
}</pre>
  记住三个关键词：<strong>一轮一次 stream</strong>、<strong>FiberSet 并发结算</strong>、<strong>有界 25 步</strong>。
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>一次对话是一趟<strong>下行请求 + 中段循环 + 上行事件</strong>的往返。</li>
    <li>富 TUI 用<strong>进程内 RPC worker</strong>连 server，零网络、复用同一套 SDK。</li>
    <li>server 是 <strong>Effect HttpApi</strong>（不是 Hono）；事件经 <strong>GlobalBus</strong> 回流。</li>
    <li>agent 循环 = <strong>问一轮 → FiberSet 并发干一轮 → 喂回再问</strong>，上限 <span class="mono">MAX_STEPS=25</span>。</li>
    <li>TUI 按 <strong>~16ms 批渲染</strong>事件，所以是顺滑流而非闪烁。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">The first two lessons gave you the map. Now we do the one thing that connects everything: <strong>follow one prompt all the way through</strong>. You type "fix this bug" in the TUI and hit enter, and a reply streams out character by character — in between, the request travels <strong>down</strong> the whole tower and results bubble <strong>up</strong>, while the crucial middle stretch <strong>loops repeatedly</strong>. See this round trip clearly and, for the next 61 lessons, you'll always know which hop you're standing on.</p>
<p>Why spend a whole lesson on "one conversation"? Because it's the <strong>confluence</strong> of all of opencode's complexity: transport, routing, context assembly, model protocol, tool execution, concurrency scheduling, persistence, front-end rendering — nearly every subsystem makes an appearance in this few-second journey. Walk this <strong>main road</strong> end to end first, building a skeleton sense of "what comes before what, and what repeats," and the deep-dive lessons later won't make you "miss the forest for the trees." This lesson is the <strong>tour map</strong> for every deep-water lesson ahead: each module you meet, you can hang precisely onto one hop of this journey.</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  Picture one conversation as a <strong>restaurant order ticket</strong>. You (the client) hand the ticket through the window; the <strong>maître d'</strong> (the server) logs it and sends it to the kitchen; the <strong>head chef</strong> (the LLM) glances and says "go get the ingredients first" — but the chef only gives orders, never runs around; the <strong>line cook</strong> (tool execution) fetches, preps, and cooks, then brings the half-finished dish back for the chef to inspect; the chef calls the next step… round and round for a few rounds until the chef says "plate it." Throughout, every kitchen action is <strong>reported live to the front desk</strong>, so from your seat you see "prepping, cooking, almost ready."
</div>

<h2>Bird's eye: one tower, two passes</h2>
<p>First compress the whole route into one picture. The request starts at the topmost client and sinks layer by layer to the model; when the model wants a tool, results float up and then sink again — <strong>downward is "request," upward is "results and events."</strong> The middle of this round trip (assemble context → ask the model → run tools) repeats several times, until the model stops asking for tools.</p>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">① Client</span><span class="name">TUI prompt component · app.tsx</span></div>
    <div class="ld">Take keystrokes, submit the prompt; subscribe to the event stream to paint the screen</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">②③ Transport + server</span><span class="name">RPC worker · Effect HttpApi</span></div>
    <div class="ld">Send the request into the server's session route group; events flow back via SSE/RPC</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">④–⑩ Session engine</span><span class="name">input → coordinator → runner/llm.ts</span></div>
    <div class="ld">Assemble context, run the agent loop, execute tools, persist</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">⑥⑦ Model access</span><span class="name">LLM protocol layer · provider</span></div>
    <div class="ld">Encode into the provider protocol, stream LLMEvents back</div></div>
</div>
<div class="cols">
  <div class="col"><h4>↓ Down (request)</h4><p>keystroke → serialize into an HTTP request → session handler → projected history + System Context → LLM request → provider. All the way, <strong>converging your intent</strong>.</p></div>
  <div class="col"><h4>↑ Up (results / events)</h4><p>streamed tokens, tool results, events from persistence → GlobalBus → SSE → TUI batched render. All the way, <strong>broadcasting progress</strong>.</p></div>
</div>
<p>This "down / up" picture is the cheapest mental model for reading opencode. <strong>Down is a converging process</strong>: your vague sentence, through session logging, history projection, and context rendering, is step by step <strong>translated into a precise request the model can eat</strong>; each layer down, the information gets more structured, finally converging into one clean model call.</p>
<p><strong>Up is a diverging process</strong>: the model's text fragments, the tool results, the records persistence produces — all shattered into individual <strong>events</strong> broadcast upward, visible to whoever subscribes. Two streams, opposite directions, running at once — down is "asking," up is "answering and reporting." For every module later, ask yourself first: is it on the way down or up? Which layer? Understanding instantly gets a coordinate. That's why this journey is worth walking in Part 1: it's the whole book's <strong>map coordinate system</strong>.</p>

<h2>Hops 1–3: from keystroke to server</h2>
<p>The characters you type land first in the TUI's prompt component (<span class="mono">packages/tui/src/component/prompt</span>). On enter, the TUI doesn't send a network request — the rich terminal has a clever design: <strong>the server runs in a Worker inside the same process</strong>. <span class="mono">cli/cmd/tui.ts</span> uses <span class="mono">createWorkerFetch</span> to quietly swap the SDK's <span class="mono">fetch</span> for "send an RPC to the Worker," so the front-end code calls the SDK as usual while underneath there is <strong>zero network overhead</strong> (Lesson 13).</p>
<div class="flow">
  <div class="node"><div class="nt">keystroke</div><div class="nd">prompt component</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">createWorkerFetch</div><div class="nd">SDK.fetch → RPC</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">worker.ts</div><div class="nd">Server.listen</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">HttpApi</div><div class="nd">session route group</div></div>
</div>
<p>The worker (<span class="mono">cli/tui/worker.ts</span>) runs the real <span class="mono">Server.listen</span> and also wires a return path: <span class="mono">GlobalBus.on("event", e =&gt; Rpc.emit("global.event", e))</span> — every event the server emits is pushed back to the front-end over RPC. The server itself (<span class="mono">server/server.ts</span>) is <strong>not Hono</strong>, but Effect's <span class="mono">HttpApi + OpenApi</span> on <span class="mono">NodeHttpServer</span> (Lesson 9).</p>
<p>Why does the rich TUI bother with this detour — couldn't it just start a local HTTP server and connect with fetch? Because that would occupy a port, force network-error handling, and add a serialization layer.</p>
<p>opencode's trick: run the server in a <strong>Worker thread in the same process</strong>, then swap the SDK's underlying <span class="mono">fetch</span> for "send one RPC message to the Worker." The front-end code <strong>doesn't change a single line</strong> — it thinks it's calling an ordinary HTTP SDK, but underneath it's in-process: zero network, zero ports, reusing the server's full typed interface. The beauty is it's <strong>reversible</strong>: when you start the server as a real network service with <span class="mono">opencode serve</span>, the same SDK seamlessly switches to real HTTP, front-end none the wiser. <strong>One interface, two transports</strong> — opencode's "one core, many faces" landing precisely at the transport layer; Lesson 13 unpacks this worker mechanism in full.</p>

<h2>Hops 4–7: assemble context, ask the model</h2>
<p>Once the request hits the session handler, it's handed to the V2 session engine. It doesn't "call the model" directly; it first takes three prep steps:</p>
<table class="t">
  <tr><th>Hop</th><th>What</th><th>Source anchor</th></tr>
  <tr><td>④ Inbox</td><td>the prompt first becomes an <strong>event-sourced</strong> input record, then wakes the runner</td><td><span class="mono">session/input.ts</span> → <span class="mono">run-coordinator.ts</span></td></tr>
  <tr><td>⑤ Context</td><td>render the <strong>baseline System Context</strong> (instructions, date, skills…)</td><td><span class="mono">system-context/index.ts</span></td></tr>
  <tr><td>⑥ Build request</td><td>translate projected history into LLM messages, resolve the model</td><td><span class="mono">runner/to-llm-message.ts</span> · <span class="mono">model.ts</span></td></tr>
  <tr><td>⑦ Open the stream</td><td><span class="mono">llm.stream()</span> sends to the provider via a protocol adapter</td><td><span class="mono">llm/src/route/client.ts</span></td></tr>
</table>
<p>Hop ⑦ returns not a finished answer but a <strong>stream</strong> — the type signature says it plainly: <span class="mono">Stream.Stream&lt;LLMEvent, LLMError&gt;</span>. Text fragments, reasoning, tool-call requests, usage — all spat out as individual <span class="mono">LLMEvent</span>s over time. The server <strong>persists incrementally</strong> as it receives, so even a mid-stream disconnect doesn't lose everything.</p>
<p>One more "invisible prep" deserves a name: hop ⑤'s <strong>System Context</strong>. The model doesn't only see your sentence — before your words go out, the server renders a <strong>baseline system context</strong>: the current date, the project's <span class="mono">AGENTS.md</span> instructions, the available skill list, whether the current agent is build or plan, all prepended to the conversation. It's like a chart handed to a doctor before each visit, so the model "understands your situation the moment it opens its mouth." How this context is assembled, and how changes are incrementally announced to the model, is one of opencode's most distinctive designs — Part 5 is devoted to it. Here, just remember: <strong>before every single model call, an invisible but crucial slice of context is quietly prepended</strong>.</p>

<h2>Hops 8–10: the agent loop's heartbeat</h2>
<p>This is the <strong>heart</strong> of the whole journey. When a "tool-call" event appears in the stream, the runner doesn't sit and wait — it tosses it into a <span class="mono">FiberSet</span> and runs it <strong>concurrently</strong> (asked to "read three files" in one step, all three run together); the tool is carried out by the <span class="mono">ToolRegistry</span>, with dangerous operations gated by a permission check first. Once this round's tools all settle, the runner <strong>reloads projected history</strong> and opens the <strong>next</strong> provider turn — feeding tool results back so the model can keep thinking.</p>
<div class="vflow">
  <div class="step"><b>Assemble</b>　reload projected history + System Context</div>
  <div class="step"><b>Ask a round</b>　one <span class="mono">llm.stream(request)</span></div>
  <div class="step"><b>Do work</b>　tool-call → FiberSet concurrent settle → persist results</div>
  <div class="step"><b>Decide</b>　more tool calls? yes → back to top; no → wrap up</div>
  <div class="step"><b>Guardrail</b>　steps &lt; <span class="mono">MAX_STEPS = 25</span>, else StepLimitExceeded</div>
</div>
<p>This "<strong>ask a round → do a round → ask again</strong>" loop is exactly the agent loop from Lesson 1. It turns at most 25 times (a hard guardrail against the model spinning on tool calls forever); Lesson 17 takes <span class="mono">runner/llm.ts</span> apart line by line.</p>
<p>Two design choices really show V2's thinking. First, tools run <strong>concurrently</strong> via <span class="mono">FiberSet</span> rather than queued: when the model asks in one step to "read a, read b, read c," the three reads run together and return together — faster, and letting the model see fuller context at once.</p>
<p>Second, each round ends by <strong>reloading projected history</strong> before continuing, rather than splicing tool results onto an in-memory message array — because history is the <strong>persisted source of truth</strong>, and re-projecting guarantees that even if the process crashed and restarted, or another input cut in midway, the model's next round always sees "the most accurate current session state." Both point to the same restraint: <strong>don't rely on temporary in-memory state; everything defers to persistence</strong>. This "truth-first, rebuildable-anytime" mindset is V2's biggest temperamental difference from V1, confirmed again and again in Part 4.</p>
<p>Once the loop is spinning, you're not stuck just waiting. opencode lets you <strong>cut in midway</strong> — while the model is working, type "wait, don't touch that file yet," and this new input is caught as a new inbox record and, at the next <strong>safe boundary</strong>, folds into the active activity, quietly bending what happens next. That's exactly why hop ④ makes input an <strong>event-sourced inbox</strong> rather than a plain function argument: because a "conversation" is fundamentally <strong>a living thing you can interrupt and correct anytime</strong>, not a command that, once issued, only waits for a result. This "steerable anytime" quality is key to whether an agent feels good to use, and the reason V2 polishes its concurrency model so hard.</p>

<h2>Hop 11: events flow back, painted to screen</h2>
<p>Every time the loop advances a bit, incremental persistence <strong>emits an event</strong> to <span class="mono">GlobalBus</span>; events surge toward the client via the SSE event group (<span class="mono">groups/event.ts</span>) or the RPC return path. The TUI subscribes to <span class="mono">sdk.global.event(...)</span> in <span class="mono">context/sdk.tsx</span> — but <strong>not one-paint-per-event</strong>; it <strong>batches a frame's worth every ~16ms</strong> before rendering, so what you see is a smooth character stream, not frantic flicker.</p>
<div class="flow">
  <div class="node"><div class="nt">incremental persist</div><div class="nd">emit event</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">GlobalBus</div><div class="nd">SSE / RPC</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">sdk.global.event</div><div class="nd">subscribe</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">16ms batch render</div><div class="nd">Solid store → screen</div></div>
</div>
<p>This hop's "batched render" isn't only for looks. Events can <strong>come very densely</strong> — per-token text, tool progress, usage stats, hundreds a second; if each one triggered a terminal repaint, the CPU would choke and the screen would tear. Batching ~16ms (about one frame) before rendering saves cycles and stays smooth. And this "<strong>everything becomes an event first</strong>" return mechanism has a hidden bonus: because every state change is broadcast, <strong>multiple clients can watch one session at once</strong>, and a reconnect just replays events to catch up. You could even watch in the TUI and open the same session in the web client — both follow the same event stream. Part 3 (the event bus) and Part 10 (TUI rendering) both return here.</p>

<div class="card macro">
  <div class="tag">🌍 Big picture</div>
  One conversation = <strong>a downward request</strong> + <strong>a repeating agent loop in the middle</strong> + <strong>an upward event stream</strong>. Down converges intent into one <span class="mono">llm.stream</span>; the middle "ask a round, do a round" turns at most 25 times; up makes every state change become an event first, then persisted and rendered. For any lesson, ask yourself first: which hop of this journey am I standing on?
</div>

<div class="card detail">
  <div class="tag">🔬 Source detail</div>
  The loop skeleton of hops 8–10 (heavily simplified from <span class="inline">packages/core/src/session/runner/llm.ts</span>):
<pre class="code"><span class="cm">// exactly one llm.stream per provider turn; settle tools concurrently, then continue</span>
<span class="kw">while</span> (openActivity) {
  <span class="kw">for</span> (<span class="kw">let</span> step = 0; step &lt; <span class="fn">MAX_STEPS</span>; step++) {
    <span class="kw">const</span> events = llm.<span class="fn">stream</span>(request)        <span class="cm">// one round, returns an LLMEvent stream</span>
    <span class="kw">for</span> <span class="kw">await</span> (<span class="kw">const</span> e <span class="kw">of</span> events) {
      <span class="kw">if</span> (e.type === <span class="st">"tool-call"</span>)
        toolMaterialization.<span class="fn">settle</span>(e)         <span class="cm">// toss into a FiberSet, run concurrently</span>
      persist(e)                                <span class="cm">// incremental persist → emit event</span>
    }
    <span class="kw">if</span> (!hadToolCalls) <span class="kw">break</span>                  <span class="cm">// model stops asking for tools → wrap up</span>
    request = <span class="fn">reloadProjectedHistory</span>()        <span class="cm">// feed tool results back, next round</span>
  }
}</pre>
  Three keywords to remember: <strong>one stream per round</strong>, <strong>FiberSet concurrent settle</strong>, <strong>bounded 25 steps</strong>.
</div>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>One conversation is a round trip: <strong>downward request + middle loop + upward events</strong>.</li>
    <li>The rich TUI connects via an <strong>in-process RPC worker</strong> — zero network, reusing the same SDK.</li>
    <li>The server is <strong>Effect HttpApi</strong> (not Hono); events flow back via <strong>GlobalBus</strong>.</li>
    <li>The agent loop = <strong>ask a round → settle tools concurrently via FiberSet → feed back and ask again</strong>, capped at <span class="mono">MAX_STEPS=25</span>.</li>
    <li>The TUI <strong>batch-renders events ~16ms</strong> at a time, so it's a smooth stream, not flicker.</li>
  </ul>
</div>
""",
}
LESSON_04 = {
    "zh": r"""
<p class="lead">如果你 clone 下 opencode、开始翻源码，很快会撞上一件怪事：好像有<strong>两套</strong>会话引擎。一套在 <span class="mono">packages/opencode/src/session</span>，又大又老；另一套在 <span class="mono">packages/core</span>，又新又碎。这不是谁写重复了——opencode 正处在一场<strong>从 V1 到 V2 的架构迁移</strong>中，两套代码<strong>并存</strong>。读不懂这条迁移线，你会在源码里反复迷路；读懂了，整个仓库豁然开朗。这一课就把这条线讲透，它是读懂后面所有课的<strong>钥匙</strong>。</p>
<p>这条迁移线之所以值得单独花一课讲，是因为它是新读者最容易栽跟头的地方。你照着一篇教程去读那个上千行的会话文件，读到一半却发现它和另一处的写法完全对不上号，于是开始怀疑是不是自己理解错了——其实你没错，你只是<strong>同时撞上了新旧两套实现</strong>，还把它们当成了一套。很多人卡在 opencode 源码门口，不是因为某段逻辑太难，而是因为没人先告诉他们："你看到的是一座正在翻修的房子，墙里有两套线。"先认清这个事实再去读，前面种种对不上号的矛盾，才会忽然变得顺理成章。</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  把这场迁移想成<strong>一边住人、一边翻修的老房子</strong>。<strong>V1 是老电路</strong>：还在给全屋供电，灯照亮、插座照用，你不能拔——一拔整个家就黑了。<strong>V2 是新电路</strong>：电工正一个房间一个房间地重新布线，布好一间就切一间过去。于是某段时间里，墙里<strong>新旧两套线并存</strong>，有的房间走新线、有的还靠老线。你读 opencode 源码时撞见的"两套 session"，正是这堵墙里并排的新旧线缆——知道哪根是哪根，你才不会误把老线当新线读。翻修的智慧也在这里：你不必为了装一个新插座就把全屋停电——老线先扛着照明，新线在墙里慢慢铺，等某个房间的新线测稳了，再优雅地把这一间切过去。opencode 的迁移，走的正是这条"不停机、逐间换"的稳妥路子。
</div>

<h2>源码里的两块门牌</h2>
<p>先认门牌。最省事的判断法：<strong>看路径</strong>。凡是 <span class="mono">packages/opencode/src/session/*</span>，是 V1；凡是 <span class="mono">packages/core/src/session/*</span>，是 V2。它俩干的是同一件事——把你的话变成一轮轮"调模型、跑工具"，但内部气质截然不同。</p>
<div class="cols">
  <div class="col"><h4>V1 · packages/opencode</h4><p>老牌主力：基于 Vercel <span class="mono">AI-SDK</span>，会话存成<strong>磁盘 JSON 文件</strong>，命令式写法。<strong>至今仍是默认跑的路径</strong>。</p></div>
  <div class="col"><h4>V2 · packages/core</h4><p>新生内核（"Session Core"）：纯 <strong>Effect</strong>，会话进 <strong>Drizzle + SQLite</strong>，自研 LLM 协议层。<strong>正在成形的未来</strong>。</p></div>
</div>
<p>注意一个反直觉点：名字叫 <span class="mono">core</span> 的那个包，反而是<strong>更新</strong>的 V2；而叫 <span class="mono">opencode</span> 的主二进制里，装着<strong>更老</strong>的 V1。所以"想读最核心的逻辑就去 core"这句话，今天才成立——半年前可不是。</p>
<p>为什么会有这种错位——最新的内核，偏偏藏在一个叫"核心"的包里，而最老的逻辑，留在那个就叫 opencode 的主包里？因为后者是项目<strong>最早</strong>的主二进制，命令行、服务器、第一代会话引擎，全都先长在了它身上；后来团队决定重写内核，便另起一个干净的新包，把第二代一点点养在里面，<strong>暂不惊动</strong>还在服役的老引擎。于是包名记录的是<strong>诞生的先后</strong>，而不是新旧的高下。读资历深的开源项目常要这样"考古"——名字往往滞后于架构好几个版本，别被它带偏了方向。</p>

<h2>体量与气质：巨石 vs 协作者</h2>
<p>翻开两边的文件，第一眼的差别就是<strong>体量</strong>。V1 是几块"巨石"，单文件动辄上千行；V2 是一堆小而专的"协作者"，每个只管一件事。</p>
<table class="t">
  <tr><th>V1（巨石）</th><th>行数</th><th>V2（协作者）</th><th>行数</th></tr>
  <tr><td><span class="mono">session/prompt.ts</span>（V1 循环）</td><td>~1704</td><td><span class="mono">session/runner/llm.ts</span>（V2 循环）</td><td>~404</td></tr>
  <tr><td><span class="mono">session/session.ts</span></td><td>~1119</td><td><span class="mono">session/run-coordinator.ts</span></td><td>~284</td></tr>
  <tr><td><span class="mono">session/processor.ts</span></td><td>~1084</td><td><span class="mono">session/input.ts</span></td><td>~353</td></tr>
</table>
<p>别小看这组数字背后的差别。V1 的 <span class="mono">prompt.ts</span> 一个文件把"调模型、处理流、跑工具、生成标题、压缩历史"全揽了，读起来要在脑子里同时装下一千多行；V2 把这些<strong>拆成各自独立、可单独测试</strong>的小件，<span class="mono">runner/llm.ts</span> 只管编排那条循环，把工具、协调、投影历史交给别的协作者。"<strong>一个文件只干一件事</strong>"，正是 V2 在可维护性上的核心赌注。</p>
<p>巨石文件的麻烦，远不只是"读起来累"。当调模型、处理流、跑工具、生成标题、压缩历史全挤在一千七百行的函数群里，任何一处改动都可能<strong>牵一发而动全身</strong>，想单独测试其中一小块几乎不可能——它们的状态盘根错节地缠在一起，你拎不出任何一段干净地验。V2 把每件事拆成独立小协作者后，你可以<strong>单独喂输入、单独验输出</strong>，改一处不必提心吊胆怕震动全局。这就是"拆分"换来的最实在的红利：<strong>可测试、可替换、可独立演进</strong>。代码越关键，这种可控性越值钱——而会话引擎，恰恰是 opencode 最关键的那块。</p>
<p>这种"巨石 vs 小件"的差别，你甚至不用读懂逻辑，光从<strong>目录结构</strong>就能看出来：V1 的 session 目录下，躺着十来个动辄上千行的大文件，平铺在一起；而 V2 的 session 目录被进一步切成了 <span class="mono">runner/</span>、<span class="mono">execution/</span> 这样的子目录，每个文件都短小、名字直白地写着自己只负责的那一件事。<strong>目录的形状，往往就是架构的形状</strong>——以后判断一个陌生模块有没有被精心拆分过，先扫一眼它的目录树，常常就有答案了。</p>

<h2>四条分界线</h2>
<p>体量之外，V1 和 V2 在四件根本的事上做了不同选择。这张表是本课最该记牢的：</p>
<table class="t">
  <tr><th>维度</th><th>V1</th><th>V2</th></tr>
  <tr><td>模型接入</td><td>Vercel <span class="mono">AI-SDK</span>（<span class="mono">import { tool } from "ai"</span>）</td><td>自研 <span class="mono">@opencode-ai/llm</span> 多协议层</td></tr>
  <tr><td>持久化</td><td>磁盘 <strong>JSON 文件</strong>（key-value）</td><td><strong>Drizzle + SQLite</strong>（双后端 bun/node）</td></tr>
  <tr><td>输入模型</td><td>函数参数，临时态</td><td><strong>事件溯源收件箱</strong>，持久化为准</td></tr>
  <tr><td>编程范式</td><td>命令式 async/await</td><td>函数式 <strong>Effect</strong>（Service/Layer/Fiber）</td></tr>
</table>
<p>这四条不是孤立的偏好，而是层层相扣：选了 Effect，就能用它的 <span class="mono">FiberSet</span> 优雅地并发跑工具；选了 SQLite + 事件溯源，崩溃重启后就能从持久化里<strong>重建</strong>状态；自研 LLM 层，才能精确控制每家 provider 的协议细节与缓存。<strong>范式、存储、接入，是一整套相互成全的选择</strong>。</p>
<p>顺便点破一个容易误会的点：V2 用 Effect、用 SQLite，<strong>不是为了赶时髦</strong>。Effect 让"反复调模型、并发跑工具、随时可能失败或被打断"这种天然混乱的逻辑变得<strong>可推理、可组合</strong>；SQLite 让会话有了一个零配置、可查询、可随版本迁移的家。每个选择都对着 V1 的一个具体痛点而来。等你后面读到 Effect 的 Service 与 Layer（第二部分）、读到 Drizzle 的 schema（第九部分），不妨回想这一课：它们不是装饰，而是 V2 之所以成为 V2 的<strong>地基</strong>。</p>

<h2>为什么要费劲迁移</h2>
<p>把一个还能跑的引擎推倒重来，代价不小。V2 图的是 V1 难以补上的几样东西：</p>
<div class="vflow">
  <div class="step"><b>可测试</b>　小协作者 + Effect，把副作用关进类型，单测不再要起半个世界</div>
  <div class="step"><b>可恢复</b>　事件溯源 + SQLite，进程崩了能从持久化重建会话</div>
  <div class="step"><b>可并发</b>　FiberSet 并发跑工具、协调多个 session，不靠脆弱的手写锁</div>
  <div class="step"><b>可扩展</b>　为将来的多节点/集群留出 Location、ownership 等接缝</div>
  <div class="step"><b>新能力</b>　System Context / Context Epoch 这套独特设计，只在 V2 里有</div>
</div>
<p>最后一条尤其关键：第五部分要讲的 <strong>Context Epoch</strong>（会话上下文的不可变纪元）是 opencode 最独特的设计，它<strong>只存在于 V2</strong>。换句话说，V2 不只是"把 V1 重写得更干净"，而是要长出 V1 架构撑不起来的<strong>新能力</strong>。这也是为什么这份指南把 V2 当主线。</p>
<p>但要强调：迁移是<strong>渐进而务实</strong>的，不是某天"啪"地一声整体切换。两套引擎会并存相当长一段时间，功能一块块从 V1 挪到 V2，挪一块、稳一块。对团队，这意味着随时能回退、用户几乎无感；对你这个读者，这意味着<strong>两边的代码都还活着、都值得读</strong>——读 V2 看清"它想去哪"，读 V1 理解"当下到底在跑什么"。把"正在迁移中"这个状态本身，当成 opencode 现阶段的一个<strong>基本事实</strong>记下来，很多源码里"为什么这里有两份"的困惑，就都迎刃而解了。</p>
<p>举个最能体现差别的场景：假设 agent 正跑到一半，机器突然断电。老引擎把会话状态摊在内存和零散的文件里，重启之后"刚才跑到哪、做了什么"很可能对不齐、只能从头再来；新引擎因为每一步都先落成事件、写进数据库，重启后能从持久化里把整段会话<strong>重新投影出来</strong>，清楚知道自己上一刻进行到哪。这种"经得起崩"的底气，是老架构很难补上的，也正是新引擎把"一切以持久化为准"刻进骨子里换来的回报——你会在第四、第九部分反复看到这条原则发力。</p>

<h2>读者该怎么自处</h2>
<p>面对两套并存的代码，普通读者最容易犯的错是"分不清自己在读哪套、把两边的概念串在一起"。给你三条实用守则：</p>
<div class="cols">
  <div class="col"><h4>① 先看路径</h4><p><span class="mono">opencode/src/session</span> = V1；<span class="mono">core/src/session</span> = V2。一眼定身份。</p></div>
  <div class="col"><h4>② 以 V2 为主</h4><p>想懂"opencode 想成为什么"，读 V2；本指南正文也以 V2 为主线。</p></div>
  <div class="col"><h4>③ 遇到 V1 别慌</h4><p>它仍是默认运行路径，关键处本指南会对照它，知道"老线长这样"即可。</p></div>
</div>
<p>把这条迁移线画成一张图，也许最能帮你随时定位"我读到了哪一段"：</p>
<div class="flow">
  <div class="node"><div class="nt">V1 全量在跑</div><div class="nd">opencode/src/session</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">V2 内核成形</div><div class="nd">core 逐块接管</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">两套并存</div><div class="nd">看路径定身份</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">V2 为主</div><div class="nd">未来方向</div></div>
</div>
<p>opencode 此刻正站在"<strong>两套并存</strong>"这一格——这也是你打开源码时会看到的真实样子。读这份指南时，每翻到一个模块，先在心里问一句：这是老线还是新线？答案，往往就写在它的路径里。</p>
<p>读到这儿，你其实已经握住了贯穿全书的那把钥匙。下一部分，我们就去补 V2 的地基——也就是那个名字听起来有点唬人、却在 <span class="mono">packages/core</span> 里处处都在的函数式框架 Effect。因为不先弄懂它的几个核心概念，你看新引擎里那些满屏的函数式写法时会处处卡壳；而一旦把地基打牢，再回头看 V2 的会话引擎、上下文系统、模型协议层，就会有种"原来如此、本该如此"的顺畅。架构迁移的故事讲到这里告一段落，真正的深水区，从下一课开始。</p>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  opencode 同时活着<strong>两套</strong>会话引擎：<strong>V1</strong>（<span class="mono">packages/opencode/src/session</span>，AI-SDK + JSON 文件 + 命令式巨石，仍是默认）和 <strong>V2</strong>（<span class="mono">packages/core</span>，Effect + SQLite + 事件溯源的小协作者，正在成形）。迁移是渐进的、两套并存。读源码先看路径定身份，以 V2 为主线、遇 V1 不慌——这是读懂整个仓库的钥匙。说到底，opencode 不是一份写完就定型的代码，而是一个<strong>正在生长</strong>的活项目；这一课教你的，与其说是 V1 和 V2 的区别，不如说是一种读"演进中的大型代码库"的眼光——先分清新旧、再以新为主、对旧存敬。这种眼光，会一直陪你走完后面六十课。
</div>

<div class="card detail">
  <div class="tag">🔬 细节 / 源码对应</div>
  把"AI-SDK vs 自研 Effect"这条最大的分界，落到两段对照代码上（都大幅简化）：
<pre class="code"><span class="cm">// V1：packages/opencode/src/session（prompt.ts 定义 tool、llm.ts 调 streamText）—— 用 Vercel AI-SDK</span>
<span class="kw">import</span> { tool, streamText } <span class="kw">from</span> <span class="st">"ai"</span>
<span class="kw">const</span> result = <span class="fn">streamText</span>({ model, messages, tools: { edit: <span class="fn">tool</span>({ <span class="cm">/* … */</span> }) } })

<span class="cm">// V2：packages/core/src/session/runner/llm.ts —— 纯 Effect + 自研 llm</span>
<span class="kw">import</span> { Effect, FiberSet, Stream } <span class="kw">from</span> <span class="st">"effect"</span>
Effect.<span class="fn">gen</span>(<span class="kw">function*</span> () {
  <span class="kw">const</span> events = llm.<span class="fn">stream</span>(request)        <span class="cm">// 一轮一次，拿回 LLMEvent 流</span>
  <span class="cm">// tool-call → FiberSet 并发结算 → reload 投影历史 → 续下一轮</span>
})</pre>
  同一件事——"调模型、跑工具"——V1 交给 AI-SDK 的 <span class="mono">streamText</span>，V2 自己用 Effect 编排，从而掌控并发、持久化与协议细节。
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>opencode 并存<strong>两套</strong>会话引擎，正从 V1 迁向 V2。</li>
    <li>看路径定身份：<span class="mono">opencode/src/session</span>=V1，<span class="mono">core/src/session</span>=V2。</li>
    <li>V1 = AI-SDK + JSON 文件 + 命令式巨石（仍默认）；V2 = Effect + SQLite + 事件溯源小协作者。</li>
    <li>迁移图的是<strong>可测试、可恢复、可并发、可扩展</strong>，以及 V2 独有的 Context Epoch。</li>
    <li>本指南以 <strong>V2 为主线</strong>，关键处对照 V1。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Clone opencode, start digging through the source, and you'll soon hit something strange: there seem to be <strong>two</strong> session engines. One lives in <span class="mono">packages/opencode/src/session</span>, big and old; the other in <span class="mono">packages/core</span>, new and granular. Nobody duplicated work — opencode is mid <strong>migration from V1 to V2</strong>, and the two codebases <strong>coexist</strong>. Miss this migration line and you'll get lost in the source again and again; grasp it and the whole repo snaps into focus. This lesson makes that line clear — it's the <strong>key</strong> to reading every lesson ahead.</p>
<p>Why a whole lesson on the migration line? Because it's where new readers stumble most. You follow a tutorial to read that thousand-line session file, and halfway through it doesn't match the style of another file at all, so you start doubting your own understanding — but you're not wrong; you simply <strong>hit two implementations at once</strong> and treated them as one. Many stall at opencode's doorstep not because some logic is hard, but because no one told them first: "you're looking at a house mid-renovation, with two sets of wiring in the walls." Accept that fact first, and the contradictions ahead suddenly make sense.</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  Picture the migration as an <strong>old house being renovated while people still live in it</strong>. <strong>V1 is the old wiring</strong>: still powering the whole place, lights on, outlets working — you can't yank it, or the house goes dark. <strong>V2 is the new wiring</strong>: an electrician is rewiring room by room, switching each over once it's run. So for a while, <strong>old and new wires coexist</strong> in the walls — some rooms on the new line, some still on the old. The "two sessions" you meet in opencode's source are exactly those parallel old/new cables — know which is which and you won't misread the old line as the new. The wisdom of renovation is here too: you don't black out the whole house to add one outlet — the old line keeps the lights on while the new line is run, and once a room's new line tests stable, you switch that room over gracefully. opencode's migration takes exactly this "no-downtime, room-by-room" path.
</div>

<h2>Two addresses in the source</h2>
<p>First learn the addresses. The easiest test: <strong>look at the path</strong>. Anything under <span class="mono">packages/opencode/src/session/*</span> is V1; anything under <span class="mono">packages/core/src/session/*</span> is V2. They do the same job — turn your words into rounds of "call the model, run tools" — but their internal temperament is utterly different.</p>
<div class="cols">
  <div class="col"><h4>V1 · packages/opencode</h4><p>The old workhorse: built on Vercel <span class="mono">AI-SDK</span>, sessions stored as <strong>JSON files on disk</strong>, imperative style. <strong>Still the default runtime path today.</strong></p></div>
  <div class="col"><h4>V2 · packages/core</h4><p>The new kernel ("Session Core"): pure <strong>Effect</strong>, sessions into <strong>Drizzle + SQLite</strong>, an in-house LLM protocol layer. <strong>The future taking shape.</strong></p></div>
</div>
<p>Note a counterintuitive point: the package named <span class="mono">core</span> is actually the <strong>newer</strong> V2; while the main binary named <span class="mono">opencode</span> holds the <strong>older</strong> V1. So "to read the core logic, go to core" only holds true today — it wasn't half a year ago.</p>
<p>Why the mismatch — the newest kernel hiding in a package called "core," the oldest logic staying in the main package called opencode? Because the latter was the project's <strong>earliest</strong> main binary; the CLI, the server, the first-generation session engine all grew on it first. Later the team decided to rewrite the kernel, started a clean new package, and raised V2 inside it bit by bit, <strong>without disturbing</strong> the old engine still in service. So package names record <strong>birth order</strong>, not new-vs-old. Reading a long-lived open-source project often takes this kind of "archaeology" — names lag the architecture by several versions; don't let them mislead you.</p>

<h2>Size and temperament: monoliths vs collaborators</h2>
<p>Open the files on each side and the first difference is <strong>size</strong>. V1 is a few "boulders," single files routinely over a thousand lines; V2 is a pile of small, focused "collaborators," each minding one thing.</p>
<table class="t">
  <tr><th>V1 (boulders)</th><th>LOC</th><th>V2 (collaborators)</th><th>LOC</th></tr>
  <tr><td><span class="mono">session/prompt.ts</span> (V1 loop)</td><td>~1704</td><td><span class="mono">session/runner/llm.ts</span> (V2 loop)</td><td>~404</td></tr>
  <tr><td><span class="mono">session/session.ts</span></td><td>~1119</td><td><span class="mono">session/run-coordinator.ts</span></td><td>~284</td></tr>
  <tr><td><span class="mono">session/processor.ts</span></td><td>~1084</td><td><span class="mono">session/input.ts</span></td><td>~353</td></tr>
</table>
<p>Don't underestimate the difference behind these numbers. V1's <span class="mono">prompt.ts</span> packs "call the model, process the stream, run tools, generate titles, compact history" into one file — reading it means holding 1700+ lines in your head at once; V2 splits these into <strong>independent, separately testable</strong> small pieces, with <span class="mono">runner/llm.ts</span> only orchestrating that loop and handing tools, coordination, and history projection to other collaborators. "<strong>One file does one thing</strong>" is V2's core maintainability bet.</p>
<p>This "boulders vs pieces" difference shows even from the <strong>directory shape</strong>, without reading any logic: V1's session dir holds a dozen big files routinely over a thousand lines, laid flat; V2's session dir is further cut into subdirectories like <span class="mono">runner/</span> and <span class="mono">execution/</span>, each file short, its name plainly stating the one thing it owns. <strong>The shape of the directory is often the shape of the architecture</strong> — to judge whether an unfamiliar module was carefully split, scan its directory tree first; the answer is often right there.</p>

<h2>Four dividing lines</h2>
<p>Beyond size, V1 and V2 chose differently on four fundamental things. This table is the one to memorize:</p>
<table class="t">
  <tr><th>Dimension</th><th>V1</th><th>V2</th></tr>
  <tr><td>Model access</td><td>Vercel <span class="mono">AI-SDK</span> (<span class="mono">import { tool } from "ai"</span>)</td><td>in-house <span class="mono">@opencode-ai/llm</span> multi-protocol layer</td></tr>
  <tr><td>Persistence</td><td>on-disk <strong>JSON files</strong> (key-value)</td><td><strong>Drizzle + SQLite</strong> (dual bun/node backend)</td></tr>
  <tr><td>Input model</td><td>function args, transient</td><td><strong>event-sourced inbox</strong>, persistence-as-truth</td></tr>
  <tr><td>Paradigm</td><td>imperative async/await</td><td>functional <strong>Effect</strong> (Service/Layer/Fiber)</td></tr>
</table>
<p>These four aren't isolated preferences; they interlock. Choose Effect and you can elegantly run tools concurrently with its <span class="mono">FiberSet</span>; choose SQLite + event sourcing and you can <strong>rebuild</strong> state from persistence after a crash; build your own LLM layer and you can precisely control each provider's protocol details and caching. <strong>Paradigm, storage, and access are one set of mutually-reinforcing choices.</strong></p>
<p>And to clear up a common misread: V2 uses Effect and SQLite <strong>not to be trendy</strong>. Effect makes inherently messy logic — calling the model repeatedly, running tools concurrently, failing or being interrupted at any moment — <strong>reasoned-about and composable</strong>; SQLite gives sessions a zero-config, queryable, version-migratable home. Each choice targets a concrete V1 pain point. When you later read Effect's Service and Layer (Part 2) or Drizzle's schema (Part 9), recall this lesson: they aren't decoration, they're the <strong>foundation</strong> that makes V2 V2.</p>

<h2>Why bother migrating</h2>
<p>Tearing down a working engine to start over isn't cheap. V2 is after several things V1 can't easily gain:</p>
<div class="vflow">
  <div class="step"><b>Testable</b>　small collaborators + Effect put side effects in the types; unit tests no longer need half the world running</div>
  <div class="step"><b>Recoverable</b>　event sourcing + SQLite rebuild a session from persistence after a crash</div>
  <div class="step"><b>Concurrent</b>　FiberSet runs tools concurrently and coordinates multiple sessions, no fragile hand-written locks</div>
  <div class="step"><b>Scalable</b>　leaves seams (Location, ownership) for future multi-node / clustering</div>
  <div class="step"><b>New power</b>　the System Context / Context Epoch design exists only in V2</div>
</div>
<p>The last point is key: the <strong>Context Epoch</strong> (the immutable epoch of a session's context), covered in Part 5, is opencode's most distinctive design, and it <strong>only exists in V2</strong>. In other words, V2 isn't just "V1 rewritten cleaner" — it grows <strong>new capabilities</strong> V1's architecture can't support. That's why this guide treats V2 as the main line.</p>
<p>But stress this: the migration is <strong>gradual and pragmatic</strong>, not a sudden flip one day. The two engines coexist for a good while, features moving from V1 to V2 piece by piece, each settling before the next. For the team that means easy rollback and near-invisible-to-users change; for you the reader it means <strong>both codebases are alive and worth reading</strong> — read V2 to see where it's heading, read V1 to understand what actually runs today. Hold "mid-migration" itself as a <strong>basic fact</strong> of opencode's current stage, and many "why are there two of these here" puzzles in the source resolve themselves.</p>
<p>A scenario that captures the difference: suppose the agent is mid-run and the machine loses power. The old engine spreads session state across memory and scattered files, so after restart "where it was, what it did" may not line up and it likely starts over; the new engine, because every step first becomes an event written to the database, can <strong>re-project the whole session</strong> from persistence on restart, knowing exactly where it left off. That "survives a crash" confidence is hard to retrofit into the old architecture, and is precisely the payoff of the new engine carving "persistence-as-truth" into its bones — you'll see this principle pay off again in Parts 4 and 9.</p>

<h2>How a reader should cope</h2>
<p>Facing two coexisting codebases, the easiest mistake is "not knowing which one you're reading and tangling the two sides' concepts together." Three practical rules:</p>
<div class="cols">
  <div class="col"><h4>① Path first</h4><p><span class="mono">opencode/src/session</span> = V1; <span class="mono">core/src/session</span> = V2. Identity at a glance.</p></div>
  <div class="col"><h4>② V2 as main</h4><p>To grasp "what opencode wants to be," read V2; this guide's main line is V2 too.</p></div>
  <div class="col"><h4>③ Don't panic at V1</h4><p>It's still the default runtime path; this guide contrasts it at key points — knowing "the old line looks like this" is enough.</p></div>
</div>
<p>Draw the migration line as a picture and it may best help you locate "which stretch am I reading":</p>
<div class="flow">
  <div class="node"><div class="nt">V1 fully running</div><div class="nd">opencode/src/session</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">V2 kernel forms</div><div class="nd">core takes over piece by piece</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">both coexist</div><div class="nd">path tells identity</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">V2 as main</div><div class="nd">the direction</div></div>
</div>
<p>opencode stands right now on the "<strong>both coexist</strong>" square — exactly what you'll see opening the source. Reading this guide, each time you reach a module, ask yourself first: is this the old line or the new? The answer is often written right in its path.</p>
<p>By now you hold the key that runs through the whole book. Next, Part 2 lays V2's foundation — the functional framework whose name sounds a bit intimidating yet is everywhere in <span class="mono">packages/core</span>: Effect. Without first grasping its core concepts, the functional style filling the new engine will trip you up everywhere; once the foundation is solid, looking back at V2's session engine, context system, and protocol layer brings a smooth "ah, of course." The migration story pauses here; the real deep water starts next lesson.</p>

<div class="card macro">
  <div class="tag">🌍 Big picture</div>
  opencode runs <strong>two</strong> session engines at once: <strong>V1</strong> (<span class="mono">packages/opencode/src/session</span>, AI-SDK + JSON files + imperative monoliths, still default) and <strong>V2</strong> (<span class="mono">packages/core</span>, Effect + SQLite + event-sourced small collaborators, taking shape). The migration is gradual; both coexist. Read source by path-first identity, with V2 as the main line and no panic at V1 — that's the key to reading the whole repo. Ultimately opencode isn't code frozen at completion but a <strong>living, growing</strong> project; this lesson teaches less the V1/V2 difference than a way of reading "a large codebase mid-evolution": tell new from old, favor the new, respect the old. That lens stays with you for the next sixty lessons.
</div>

<div class="card detail">
  <div class="tag">🔬 Source detail</div>
  Drop the biggest dividing line — "AI-SDK vs in-house Effect" — onto two contrasting snippets (both heavily simplified):
<pre class="code"><span class="cm">// V1: packages/opencode/src/session (tool in prompt.ts, streamText in llm.ts) — Vercel AI-SDK</span>
<span class="kw">import</span> { tool, streamText } <span class="kw">from</span> <span class="st">"ai"</span>
<span class="kw">const</span> result = <span class="fn">streamText</span>({ model, messages, tools: { edit: <span class="fn">tool</span>({ <span class="cm">/* … */</span> }) } })

<span class="cm">// V2: packages/core/src/session/runner/llm.ts — pure Effect + in-house llm</span>
<span class="kw">import</span> { Effect, FiberSet, Stream } <span class="kw">from</span> <span class="st">"effect"</span>
Effect.<span class="fn">gen</span>(<span class="kw">function*</span> () {
  <span class="kw">const</span> events = llm.<span class="fn">stream</span>(request)        <span class="cm">// one round, returns an LLMEvent stream</span>
  <span class="cm">// tool-call → settle concurrently on a FiberSet → reload projected history → continue</span>
})</pre>
  Same job — "call the model, run tools" — V1 hands it to AI-SDK's <span class="mono">streamText</span>; V2 orchestrates it itself with Effect, taking control of concurrency, persistence, and protocol detail.
</div>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>opencode runs <strong>two</strong> session engines, migrating from V1 to V2.</li>
    <li>Identity by path: <span class="mono">opencode/src/session</span>=V1, <span class="mono">core/src/session</span>=V2.</li>
    <li>V1 = AI-SDK + JSON files + imperative monoliths (still default); V2 = Effect + SQLite + event-sourced small collaborators.</li>
    <li>The migration is after <strong>testability, recoverability, concurrency, scalability</strong>, plus V2-only Context Epoch.</li>
    <li>This guide's main line is <strong>V2</strong>, contrasting V1 at key points.</li>
  </ul>
</div>
""",
}
