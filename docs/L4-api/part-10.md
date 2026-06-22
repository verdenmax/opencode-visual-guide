# L4 · Part 10 源文件 → 课 对照 (API map)

opencode 源文件（`/home/verden/course/opencode`）→ Part 10 中讲到它的课。TUI 源码在 `packages/tui/src/`，run CLI 在 `packages/opencode/src/cli/cmd/`。

| opencode 源文件 / 符号 | 关键点 | 讲到它的课 |
| --- | --- | --- |
| `packages/tui/src/app.tsx` | TUI 入口 `run(input)`：`Effect.acquireRelease(createCliRenderer({externalOutputMode:"passthrough",targetFps:60,exitOnCtrlC:false,useKittyKeyboard:{},useMouse,consoleOptions}), r=>destroyRenderer(r))`；`render(()=><ExitProvider…<App/>…>)` 挂组件树；近二十层 context provider 嵌套；SIGHUP→destroyRenderer | L52, L53 |
| `@opentui/core`(createCliRenderer) | 渲染引擎：布局/绘制/输入；`createCliRenderer(options)`→`CliRenderer`；`destroyRenderer`；JSX 原语 `<box>`/`<text>`/`<scrollbox>`/`<input>`/`<textarea>`；flexbox 布局 | L52 |
| `@opentui/solid`(render) | SolidJS 绑定：`render(()=><JSX>)`、`useRenderer`、`useTerminalDimensions`、`TimeToFirstDraw` | L52, L53 |
| `packages/tui/src/context/helper.tsx` | `createSimpleContext({name, init})`→`{context, provider, use}`；provider 跑 `init(props)`+`<Show when={init.ready!==false}>` 门控；`use()`=`useContext` + `if(!value) throw "${name} context must be used within a context provider"`（快速失败） | L53 |
| `packages/tui/src/context/sdk.tsx` | `SDKProvider`/`useSDK`：`createOpencodeClient`；SSE `startSSE`(`sdk.global.event`)；**16ms 批处理** `handleEvent`(queue.push + elapsed<16→setTimeout(flush,16)/≥16→flush)、`flush`(batch(()=>emit each))；`emitter`/`handlers` | L53, L54 |
| `packages/tui/src/context/project.tsx` | `ProjectProvider`/`useProject`：init 调 `useSDK()`(故在 SDK 内)；`createStore` project/instance/workspace；`sync()` 从 SDK 拉 | L53 |
| `packages/tui/src/context/route.tsx` | `RouteProvider`/`useRoute`：`createStore<Route>`(HomeRoute/SessionRoute/PluginRoute)；`navigate(route)`=setStore reconcile；init 用 `useTuiStartup()` | L53 |
| `packages/tui/src/context/sync.tsx` | `SyncProvider`/`useSync`：巨大 `createStore`(provider/agent/command/permission/question/config/session/session_status/session_diff/todo…)；`switch(event.type)` reducer→`setStore`(produce/reconcile)；二分 `search`(数组按 id 排序) | L54 |
| `packages/tui/src/context/data.tsx` | `DataProvider`/`useData`：依赖 SyncProvider 事件，进一步派生/归约的响应式数据 | L53, L54 |
| `packages/tui/src/prompt/frecency.tsx` | `FrecencyProvider`/`useFrecency`：`calculateFrecency=freq/(1+(now-lastOpen)/86400000)`；`updateFrecency`(freq+1/lastOpen=now/appendText)；`parseFrecency`(reduce 后者覆盖→sort lastOpen→slice MAX)；`MAX_FRECENCY_ENTRIES=1000`；存 `frecency.jsonl` | L55 |
| `packages/tui/src/prompt/history.tsx` | `PromptHistoryProvider`/`usePromptHistory`：`PromptInfo`={input,mode?,parts[]}；`move(±1,input)`(index 导航)、`append`(structuredClone+isDuplicateEntry 去重+cap)；`MAX_HISTORY_ENTRIES=50`；存 `prompt-history.jsonl`(appendText/writeText 自愈) | L55 |
| `packages/tui/src/component/prompt/index.tsx` | prompt 编辑器主体(57KB)：`<textarea>` 多行输入、parts 富内容、normal/shell 模式、@/ 集成 | L55 |
| `packages/tui/src/component/prompt/autocomplete.tsx` | `Autocomplete`：`@`(文件)/`/`(命令)触发(`mentionTriggerIndex`)→过滤→排序(`useFrecency`)；`AutocompleteRef`={visible:false\|"@"\|"/"}；`AutocompleteOption` | L55 |
| `packages/tui/src/util/persistence.ts` | `appendText`/`readText`/`writeText`——追加式 JSONL 持久化的底层(history/frecency 共用) | L55 |
| `packages/tui/src/ui/dialog.tsx` | **模态栈** `Dialog`/`DialogContext`：`createStore({stack:[]})`；开=push、`createEffect` 栈非空→`modeStack.push("modal")`、ESC=`stack.at(-1).onClose()` + `setStore("stack", slice(0,-1))`(弹栈顶) | L56 |
| `packages/tui/src/ui/dialog-select.tsx` | `DialogSelect`/`DialogSelectRef`：带搜索过滤的列表选择框——绝大多数对话框+命令面板复用的零件 | L56 |
| `packages/tui/src/component/command-palette.tsx` | `CommandPaletteDialog`：`DialogSelect` + `keymap.getCommandEntries({filter:isVisiblePaletteCommand})`(连快捷键/category/suggested)→选中 `keymap.dispatchCommand(name)`；可发现性 | L56 |
| `packages/tui/src/component/dialog-*.tsx` | 约 21 个具体对话框(model/variant/provider/agent/skill/mcp/theme-list/session-list/workspace-…)，几乎全建在 `DialogSelect` 上 | L56 |
| `packages/opencode/src/cli/cmd/run.ts` | `opencode run` 入口：三模式(注释)——非交互(默认，发 prompt→流式 stdout→空闲退出)/交互本地(`--interactive` 进程内服务器+分屏 footer)/交互附着(`--attach` 连运行中服务器)；`--command`/`--format json`/`--continue`/`--session`/`--fork` | L56 |
| `packages/opencode/src/cli/cmd/run/scrollback.surface.ts` | **保留式追加** scrollback：把助手/推理/工具进度在流式到达时稳定逐块打印(markdown/代码高亮稳定)；用 opentui `ScrollbackSurface`+`MarkdownRenderable`/`CodeRenderable`/`TextRenderable`；`ActiveEntry`/`commitMarkdownBlocks` | L56 |
