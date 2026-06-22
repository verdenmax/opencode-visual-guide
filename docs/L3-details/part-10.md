# L3 · Part 10 细节要点 (Details)

## L52 opentui 渲染器

- **opentui = 渲染到终端的 SolidJS**：现代框架「渲染器与框架分离」——SolidJS 管组件/signal/响应式，渲染目标可插拔（DOM=网页、终端=opentui）。两层包：`@opentui/core`（引擎：布局/绘制/输入）+ `@opentui/solid`（绑定：`render`/`useRenderer`/`useTerminalDimensions`/`TimeToFirstDraw`）。
- **JSX 原语 = 终端版 HTML 标签**：`<box>`(≈div，flexbox 容器，TUI 用得最多)、`<text>`(文字，可设色/粗体)、`<scrollbox>`(≈overflow:auto，对话流)、`<input>`/`<textarea>`(表单控件，prompt 底座)。
- **flexbox 布局**：`flexDirection`(122 处)/`flexGrow`/`flexShrink`/`justifyContent`/`alignItems`=CSS flexbox；opentui 内置布局引擎按此算每元素占终端哪几行列。「左定宽侧栏+右自适应主区」=flexDirection:row+定宽+flexGrow:1，与写网页一致。
- **渲染管线**（`app.tsx` `run`）：`createCliRenderer(options)` → `render(()=><组件树>)` → SolidJS 协调成元素树 → flexbox 算尺寸位置 → 帧缓冲(字符格网格) → 差分出变化格 → ANSI 转义码刷 TTY。options：`externalOutputMode:"passthrough"`、`targetFps:60`、`exitOnCtrlC:false`、`useKittyKeyboard:{}`、`useMouse`、`consoleOptions`(调试控制台浮层)。
- **Effect acquireRelease 包渲染器**：`Effect.acquireRelease(createCliRenderer, renderer=>destroyRenderer(renderer))`——渲染器独占改写终端状态(备用屏/关回显/raw 模式)，退出（正常/异常/SIGHUP）必 destroyRenderer 恢复终端。同 M2 Effect 资源管理。
- **细粒度响应式红利**：终端绘制昂贵（成千上万字符格+ANSI，带宽有限尤其 SSH）；整屏重画扛不住 60fps 还闪。signal 变→只标脏依赖它的元素→opentui 只重布局/绘制脏元素→只刷变化字符格（差分）。无需手动「重画哪块」。

## L53 TUI 应用结构

- **Provider 金字塔**（`app.tsx` `render()`）：二十多层 Provider 从外到内嵌套：ExitProvider/ErrorBoundary → SDKProvider → ProjectProvider → SyncProvider → DataProvider → ThemeProvider → Dialog/Frecency/PromptHistory/… → `<App/>`。一个组件可用服务=头顶所有 Provider 的并集。
- **嵌套顺序=依赖拓扑**：内层 Provider 的 `init` 里 `use` 外层 context——`ProjectProvider` init 第一行 `const sdk = useSDK()`（要用 SDK 拉项目），故 SDKProvider 必裹在外；`RouteProvider` init 用 `useTuiStartup()`；`SyncProvider` 与 `DataProvider` 的 init 都用 `useEvent()`（内部调 `useSDK()`）各自独立消费 SDK 事件流、都依赖 SDK 故都在 SDKProvider 内（彼此不依赖，Sync→Data 相邻只是惯例）。塔从下到上=越基础越靠外：连接→项目→数据→主题→交互→界面。结构即文档。
- **`createSimpleContext`**（`context/helper.tsx`）：封 `createContext` + provider(`<Show when={init.ready!==false}>` 门控 + `ctx.Provider value={init(props)}`) + `use()`(`if(!value) throw "${name} context must be used within a context provider"`)。一行解构 `const { use, provider } = createSimpleContext({ name, init })`。
- **use() 快速失败**：Provider 外用 context → useContext 返回空 → 当场抛错点名 context。把「Provider 外用→undefined→远处崩」的隐蔽 bug 提前成响亮报错（同 L37 Stale tool call、L48「库非空却无 session 表」）。
- **各司其职**：SDKProvider(SDK 客户端+SSE 订阅+事件批量 flush)、ProjectProvider(createStore 项目/实例/工作区，sync() 拉)、Sync/DataProvider(事件归约 store，L54)、ThemeProvider(主题/调色板)、RouteProvider(createStore<Route> home/session/plugin，navigate())、Dialog/PromptHistory/Frecency(交互状态)。每格 createStore+reconcile。

## L54 事件到 store

- **事件溯源 UI 状态**：TUI 不拉取替换，而是 SDKProvider 经 SSE(`sdk.global.event`)订阅服务器事件流。`sync.tsx` 的 `switch(event.type)` reducer 把每事件归约进 `createStore` 建的响应式大 store（provider/agent/command/permission/question/config/session/session_status/session_diff/todo…）。store=事件流投影，同 Redux action→reducer→state，action 来自服务器。
- **reducer 利器**：`produce`(immer 风草稿就地改、SolidJS 自动算变更路径)、`reconcile`(替换 store 某处时只改真正不同字段、保细粒度，避免大片无关组件重渲染)。数组(如 session)按 id 排序存 + 二分 `search` O(log n) 找到即 reconcile 更新/找不到即插入。示例：permission.asked→setStore("permission",sid,[req])、session.updated→setStore("session",index,reconcile(info))。
- **16ms 批处理**（`sdk.tsx` handleEvent/flush）：每事件 `queue.push` 入队；`elapsed = now - last`；`if (timer) return`（已排 flush）；`elapsed<16` → `setTimeout(flush,16)` 攒批；`elapsed≥16` → 立刻 `flush`。`flush`：取出 queue、`last=now`、`batch(()=>{ for event: emit })`——一批事件的所有 store 更新合并成一次渲染。16ms≈60fps 一帧(16.7ms)。
- **自适应批处理**：一个 `elapsed<16` 判断在「低延迟（空闲立刻发）」与「高吞吐（洪流攒批）」间无缝自动切换，无需手动调参。洞察=用户对延迟敏感发生在事件稀疏时(等响应)、高吞吐需求发生在事件密集时(看流式)，两者时间上天然错开。
- **流畅双重保险**：16ms 批处理(时间维：每帧最多渲一次)×L52 细粒度响应式(空间维：每次只动该动的字符格)=事件洪流下仍平稳每秒几十帧、不卡不闪。

## L55 prompt 组件

- **四件套**（`component/prompt/`、`prompt/`）：①编辑器(`index.tsx`)：`PromptInfo`={input, parts[]}，parts 可含 TextPart/FilePart(@文件)/AgentPart(@agent)+原文位置；normal/shell 模式。②自动补全(`autocomplete.tsx`)：`mentionTriggerIndex` 检测 `@`(文件)/`/`(命令)触发→按已敲文字过滤→排序(用 useFrecency)；`visible: false|"@"|"/"`。③历史(`history.tsx`)：`move(±1, input)` ↑↓ 导航(index 0=当前，负=回溯)、`append` 去重(`isDuplicateEntry` JSON 比较)存，`MAX_HISTORY_ENTRIES=50`。④frecency(`frecency.tsx`)。
- **frecency 算法**：`calculateFrecency(entry) = entry.frequency / (1 + (Date.now() - entry.lastOpen) / 86400000)`（86400000=一天毫秒）。频率(分子)给长期偏好、(now-lastOpen)/天(分母含)给当下意图、相除动态平衡。打败纯频率(旧 favorite 永霸榜)与纯最近(误点插队)。Firefox 地址栏同款经典。`updateFrecency(path)`：frequency+1、lastOpen=now、appendText 追加。时间衰减自动新陈代谢——读取时实时算，无需显式过期/清理。
- **追加式 JSONL 持久化**：`prompt-history.jsonl`、`frecency.jsonl`(在 `paths.state`)，每行一条 JSON。①追加(热路径)：`appendText` 追加一行，O(1)、抗崩溃(崩了只丢最后一行)。②压缩(冷路径)：超上限(历史 50/frecency `MAX_FRECENCY_ENTRIES=1000`)`writeText` 重写去重保最新 N。③自愈(加载)：`parseFrecency`/`parsePromptHistory` 跳解析失败的坏行，有有效行就重写修复。同 L48 WAL/L54 事件溯源「廉价追加、推迟整理」。
- **后者覆盖前者**：`parseFrecency` 用 `reduce` 让同 path 后出现的行覆盖先出现的(每次打开追加一行，同文件多行)→自然取每文件最新状态，同 L41 权限/L44 配置 `findLast`「后者胜」。

## L56 对话框与 scrollback

- **对话框=模态栈**（`ui/dialog.tsx`）：核心 `store.stack`。开对话框=push 进 stack 渲染最上层；`createEffect` 栈非空→`modeStack.push("modal")`(冻下层/焦点归对话框)、`onCleanup(popMode)` 栈空退出 modal；ESC=`current=stack.at(-1)`、`current?.onClose?.()`、`setStore("stack", stack.slice(0,-1))` 只弹栈顶。LIFO 天然支持「对话框里再开对话框」(选模型→选变体)、ESC 只关最上层、关掉退回上一层。约 21 个具体对话框(dialog-model/agent/mcp/skill/theme-list/session-list/variant/provider/workspace-…)。
- **DialogSelect 复用**：绝大多数对话框 + 命令面板都建在 `ui/dialog-select.tsx` 的 `DialogSelect`(带搜索过滤的列表选择框)上——一致的搜索/上下导航/回车确认。加新对话框只需喂选项列表。同 L36 Tool.make/L47 PluginV2.define/L53 createSimpleContext「统一模子刻同形」。
- **命令面板**（`command-palette.tsx`）：`CommandPaletteDialog` 用 `DialogSelect`，`keymap.getCommandEntries({filter: isVisiblePaletteCommand})` 取所有可见命令(连快捷键/category/suggested)成列表，选中 `keymap.dispatchCommand(name)`。意义=可发现性：不必背快捷键、搜关键词即可执行。keymap 是命令唯一真源、面板只摊开成清单。
- **run scrollback**（`opencode/src/cli/cmd/run.ts` + `run/scrollback.surface.ts`）：`opencode run` 三模式(`run.ts` 注释)：①非交互(默认)=发一 prompt、事件流式打印 stdout、会话空闲即退出(脚本/CI 友好)；②交互本地(`--interactive`)=进程内服务器+分屏 footer 直接模式；③交互附着(`--interactive --attach`)=连运行中的服务器。scrollback.surface.ts=「保留式追加」机制，把助手/推理/工具进度在流式到达时稳定逐块打印(markdown/代码高亮不乱)，用 opentui 的 `ScrollbackSurface`+Markdown/Code/Text renderable。
- **数据与表现分离**：一份 session/message/part(M9，事件流 L54 驱动)+一套内核 → 表现层可整个替换：交互 TUI / run scrollback / Web / 桌面。每多一种「看法」不必重写内核。同 L47(核心 vs provider)/L50(搬运 vs 翻译)/L54(事件数据 vs 渲染时机)「找准接缝、切开会变与不变」。
