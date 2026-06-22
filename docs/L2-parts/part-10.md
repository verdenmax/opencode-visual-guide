# L2 · Part 10 — TUI 与客户端渲染 (TUI / Client Rendering)

**课程：** L52–L56 ｜ **状态：** 已完成

## 职责

Part 10 回答一个在「agent 跑起来、记忆存好了」（M4–M9）之后的问题：**这一切，怎么在你的终端里被渲染成一个流畅、可交互的界面？** 它把 opencode 的 TUI 拆成「机器 + 组件 + 另一副面孔」三块：渲染地基是 **opentui**——一个把 SolidJS 渲染到终端的渲染器，「终端里的浏览器」（L52）；应用结构是一座近二十层的 **Provider 金字塔**，用嵌套顺序编码依赖、用统一的 `createSimpleContext` 模子刻出每个 context（L53）；数据流是**事件溯源**——服务器 SSE 事件经 reducer 归约进响应式 store，再用 16ms 自适应批处理把事件洪流压成每帧一渲（L54）；具体组件里，**prompt 编辑器**用 frecency 算法按习惯排文件、用追加式 JSONL 记历史（L55），**对话框**是模态栈、**命令面板**建在可复用的 DialogSelect 上（L56）。最后 L56 用 `run` 的 scrollback 点破一条根本原则：**数据逻辑与呈现分离**——同一份会话能被渲染成交互 TUI、也能渲染成 pipe 友好的流式日志。读完这部分，你就理解了 opencode 如何把存在 SQLite 里的会话，渲染成你眼前那个「越用越顺手」的终端界面。

## 覆盖范围

| 课 | 主题 | 一句话 |
| --- | --- | --- |
| L52 | opentui 渲染器 | **终端里的浏览器**：把整套 Web 渲染范式（DOM 般元素树+flexbox+60fps 绘制循环+键鼠事件）搬进 TTY。`@opentui/core`(引擎)+`@opentui/solid`(SolidJS 绑定)；JSX 原语 `<box>`(≈div)/`<text>`/`<scrollbox>`/`<input>`/`<textarea>`，布局用 `flexDirection/flexGrow` CSS flexbox；`createCliRenderer`(targetFps 60/kitty/mouse/passthrough)→`render(()=><树>)`→协调→flexbox 布局→帧缓冲→ANSI；渲染器包进 Effect `acquireRelease`(退出含 SIGHUP/崩溃必 destroyRenderer 恢复终端)；**细粒度响应式**=signal 变只重画依赖它的字符格 |
| L53 | TUI 应用结构 | **Provider 金字塔**=结构化依赖注入（`app.tsx`）：近二十层 Provider 嵌套，每层 owns 一件事（SDK/Project/Sync/Data/Theme/Route/Dialog…）；**嵌套顺序=依赖拓扑**（内层 init 里 use 外层，如 ProjectProvider 调 useSDK→SDK 必在外）；同一个模子 `createSimpleContext`(`helper.tsx`)封「建 context+provider(init+ready 门控)+use()」；**use() 快速失败**(Provider 外用即抛，同 L37/L48)；各司其职+细粒度响应式=拆得清即更得省 |
| L54 | 事件到 store | **事件溯源**：SDKProvider 经 SSE 订阅服务器事件流，`sync.tsx` 的 `switch(event.type)` reducer 把每事件归约进 `createStore` 响应式 store（store=事件流投影，同 Redux action→reducer→state，action 来自服务器）；reducer 用 `produce`(草稿就地改)+`reconcile`(只改真正不同字段)，数组按 id 排序+二分 search；**16ms 批处理**(`sdk.tsx`)：事件入队，elapsed<16ms(洪流)→setTimeout(flush,16) 攒批、≥16ms(空闲)→立刻 flush，flush 把整批裹进 `batch()`→一批只渲一次；**自适应**=低延迟(空闲)与高吞吐(洪流)无缝切换；双重保险=16ms 批(时间维)×细粒度(空间维) |
| L55 | prompt 组件 | prompt 四件套（`component/prompt/`、`prompt/`）：编辑器(`PromptInfo`={input,parts[]}，@文件/@agent、normal/shell)+自动补全(@///触发→过滤→排序)+历史(↑↓ `move`、`append` 去重、上限 50)+frecency；**frecency=frequency+recency**：`freq/(1+天数)`，频率给长期偏好/最近度给当下意图/相除动态平衡，打败纯频率(旧 favorite 霸榜)与纯最近(误点插队)，Firefox 地址栏同款；**追加式 JSONL 持久化**=追加(O(1)抗崩溃)+压缩(超限重写去重)+自愈(加载跳坏行)，同 L48 WAL/L54 事件溯源；parseFrecency 用 reduce 后者覆盖前者(同 L41/L44 findLast) |
| L56 | 对话框与 scrollback | **对话框=模态栈**(`ui/dialog.tsx`)：开=push、ESC=弹栈顶 `slice(0,-1)`、栈非空进 modal，LIFO 天然支持「对话框里再开对话框」（选对数据结构逻辑自简化）；**DialogSelect 处处复用**：二十多对话框(模型/agent/MCP/技能/主题/会话…)+命令面板全建在「带过滤选择框」上（同 L36/L47/L53 统一模子）；**命令面板=可发现性**(`command-palette.tsx`)：keymap.getCommandEntries→可搜列表→dispatchCommand；**run scrollback**(`run/scrollback.surface.ts`)=同数据另一副皮：非交互模式渲染成线性只追加打印 stdout 的日志(可管道/脚本/CI)，三模式=非交互/交互本地/交互附着；根本原则=**数据与表现分离**(一份 session/message+一套内核→多副面孔，呼应 L47/L50/L54「找准接缝」) |

## 与相邻部分的关系

- **承接 Part 3/Part 9**：M3 的客户端/服务器架构（SSE 事件流、SDK 客户端）是本部分 L54 数据流的源头；M9 的 session/message（SQLite）是 TUI 渲染的底层数据。SDKProvider 连服务器、Sync/Data 把事件归约成 store、组件渲染 store。
- **复用全书机制**：L52 渲染器生命周期用 M2 Effect `acquireRelease`；L53/L56 的「统一模子刻同形」呼应 L36 Tool.make、L47 PluginV2.define；L55 追加式 JSONL 呼应 L48 WAL、L54 事件溯源；L55 frecency 的「后者覆盖」与 L41 权限/L44 配置的 `findLast` 同源；L56「数据与表现分离」呼应 L47/L50/L54 的「找准接缝」。
- **引出 Part 11**：本部分把「opencode 自己的界面」讲透；L56 末点出「数据与表现分离」让 agent 内核能驱动多副面孔——而 opencode 如何向**第三方与外部工具**敞开（插件、LSP、格式化器、ACP/MCP），正是下一部分**扩展与集成**的主题。

## 核心心智模型

1. **把成熟范式整体搬到新目标**（L52）：opentui 把整个 Web 渲染范式（元素树+flexbox+绘制循环+事件）搬进终端，让你用写网页的心智搭 TUI。复用整个前端范式（同 L51 复用 git、L39 复用 Ripgrep）。
2. **嵌套顺序即依赖、统一模子即一致**（L53）：Provider 金字塔用嵌套表达依赖（结构即文档）；createSimpleContext 把「建 context+护栏」固化进一个谁都顺手用的工具，让正确的事成为最省力的事。
3. **流畅 = 时间维 × 空间维双重保险**（L52+L54）：16ms 自适应批处理（每帧最多渲一次）× 细粒度响应式（每次只动该动的字符格）=事件洪流下仍丝般顺滑。好优化往往不是更复杂、而是更懂场景。
4. **廉价追加、推迟整理**（L55）：历史/frecency 用追加式 JSONL（O(1) 抗崩溃）+ 定期压缩 + 加载自愈——同 WAL/事件溯源的范式。简单公式（frecency）漂亮解决看似需要「智能」的体验。
5. **选对数据结构、找准接缝**（L56）：模态用栈、有序覆盖用 findLast——把交互的形状映射到语义吻合的数据结构，从根上消除复杂度。数据逻辑与呈现分离，一颗内核多副面孔，是好架构「切开会变与不变」的又一例。
