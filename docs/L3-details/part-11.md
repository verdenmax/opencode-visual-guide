# L3 · Part 11 细节要点 (Details)

## L57 插件系统

- **公共插件 API = `@opencode-ai/plugin`**（`packages/plugin/src/index.ts`）：一个插件就是一个函数 `Plugin = (input: PluginInput, options?) => Promise<Hooks>`。函数体里做初始化（读配置、连资源），返回一个 `Hooks` 对象声明「我想挂在生命周期的哪些点」。最小例子：`export const myPlugin: Plugin = async (ctx) => ({ tool: { execute: { before: async (input, output) => {...} } } })`。
- **`PluginInput` = 给插件的「环境包」**：`{ client (opencode SDK 客户端，可回调服务器), project, directory, worktree, serverUrl, $ (BunShell，跑 shell 命令), experimental_workspace }`。一次性把「我是谁、在哪、能调用谁」交给插件——插件无需自己摸全局，所需上下文全靠注入（同 M2 DI 精神）。
- **加载流程**（`packages/opencode/src/plugin/loader.ts` `PluginLoader.loadExternal`）：分阶段健壮加载，每阶段失败给精准报错——`install`（按名/路径装包）→`entry`（定位入口）→`compatibility`（版本/API 兼容检查）→`load`（执行函数拿 Hooks）。分阶段让「插件装不上」能定位到底卡在哪一步。
- **配置驱动**：`plugin: Array<string | [string, options]>`——数组每项是插件名/路径（或 `[名, 选项]` 带配置）。用户不改 opencode 源码，只在配置里列个名字，插件就接上了。把「要不要扩展、用哪些扩展」交给配置而非代码。
- **与 L47 的区别**：L47 的 `PluginV2.define` 是**内核内部**的自登记装配（provider 插件用 IoC 把自己注册进内核）；L57 的 `@opencode-ai/plugin` 是面向**外部第三方用户**的公共 API。一个是「内核如何装配自己」，一个是「外人如何安全改造内核」。

## L58 插件钩子详解

- **统一机制：`plugin.trigger(name, input, output)`**：内核在每个生命周期点调 `plugin.trigger`，给已注册插件传两样东西——只读 `input`（当前上下文）+ 可变 `output` 草稿（默认行为，预填好）。每个钩子签名 `(input, output) => Promise<void>`，插件**就地改 `output`**（`output.temperature = 0` 之类），不返回新值。多个插件按注册序依次涂同一张草稿，各改一笔自然叠加。例：`session/llm/request.ts:114` trigger `chat.params`、`agent.ts:379` trigger `system.transform`、`pty.ts:71` trigger `shell.env`。
- **「编辑一份草稿」范式**：这是全书反复出现的模式——L54 `produce` 改 store 草稿、L47 IoC 让插件填装配草稿、这里让插件涂行为草稿。好处：组合性。不必设计「N 个插件的返回值怎么合并」，大家改同一张草稿即可，顺序即优先级。
- **五类钩子**：①**observe**（旁观，不改行为）：`event`（收事件流）、`config`（配置就绪）、`dispose`（清理）；②**auth / provider**：接入自定义鉴权与模型源；③**chat**（拦「请求」）：`chat.message` / `chat.params`（改温度/模型参数）/ `chat.headers` + `experimental.chat.system`（改系统提示）/ `experimental.chat.messages`（transform 改消息）；④**tool**（拦「执行」）：`tool`（注册新工具）、`tool.execute.before` / `tool.execute.after`（执行前后拦截）、`shell.env`（注入环境变量）；⑤**permission.ask**（守门）：返回 `{status: "ask" | "deny" | "allow"}` 决定某操作是否放行。
- **chat 与 tool = 拦在「请求」与「执行」前后**：chat 类钩子在「发给模型的请求」成形前后改它（改参数/系统提示/消息）；tool 类钩子在「工具执行」前后拦它（改输入/看输出/加工具）。两类正好夹住 agent 循环的两个关键边界——问模型、动手做。
- **permission 与 auth/provider = 守门与接源**：`permission.ask` 是策略钩子，让插件对「要不要允许这次写文件/跑命令」自定义裁决（呼应 M7 权限）；auth/provider 让插件把新的鉴权方式、新的模型来源接进来。内置插件 cloudflare/copilot/codex 都用 `chat.params` 调参。

## L59 LSP 集成

- **opencode = LSP 客户端（不是服务器）**：LSP（Language Server Protocol）本是编辑器与语言服务器对话的标准协议。opencode 戴「编辑器」帽子，去消费现成的语言服务器，借来整个 IDE 生态积累的代码智能，自己一行语言分析都不写。
- **服务器注册表**（`packages/opencode/src/lsp/server.ts`）：按文件扩展名映射到对应语言服务器——typescript-language-server(.ts/.tsx/.js)、gopls(.go)、pyright(.py)、biome、oxlint、vue、deno 等。打开某语言文件即启动对应服务器。
- **两副面孔之一：被动诊断**（`packages/opencode/src/lsp/diagnostic.ts` + `lsp/client.ts`）：client 收语言服务器推来的 `publishDiagnostics`；`report` 做关键过滤——只留 `severity === 1` 的 ERROR（丢警告/提示）、每文件最多 `MAX_PER_FILE = 20` 条、`pretty` 格式化成 `ERROR [line:col] message`、用 `<diagnostics file>...</diagnostics>` 包裹塞进上下文。意义：agent 编辑完代码，立刻「看见自己刚犯的错」（语法错、类型错），形成编辑安全网。只报 ERROR 是因为注意力稀缺（同 L42 主题）——别用一堆 lint 警告淹没 agent。
- **两副面孔之二：主动 lsp 工具**（`packages/opencode/src/tool/lsp.ts`）：暴露一个 `lsp` 工具，9 个操作——`goToDefinition` / `findReferences` / `hover` / `documentSymbol` / `workspaceSymbol` / `goToImplementation` / `prepareCallHierarchy` / `incomingCalls` / `outgoingCalls`，参数 `filePath` + `line` + `character`（1-based，对人友好）。让 agent 主动问「这符号定义在哪/谁引用它/它什么类型/谁调用它」——像程序员用 IDE 的「跳转/查找引用」一样理解大代码库。
- **被动 + 主动 = 安全网 + 眼睛**：同一套语言服务器，诊断是「编辑后自动报错的安全网」，lsp 工具是「主动探索代码的眼睛」。复用整个 IDE 生态（同 L39 Ripgrep、L51 git）。

## L60 PTY 与 shell

- **为什么需要真终端**：L39 的 bash 工具够跑 `ls`、`grep` 这类「发命令收输出」的批处理；但交互式 TUI 程序（vim、top、python REPL）需要一个真 TTY——行编辑、颜色、光标定位、窗口大小变化信号（SIGWINCH）。PTY（伪终端）就是给程序一个「以为自己连着真终端」的假终端。
- **`Proc` 抽象 + 双后端**（`packages/core/src/pty/pty.ts`）：`Proc` 接口 = `pid` / `onData`（输出回调）/ `onExit` / `write`（送输入）/ `resize`（改尺寸）/ `kill`。`pty.bun.ts` 与 `pty.node.ts` 是两个后端实现、同一接口（Bun 运行时用前者、Node 用后者）——同 L52 渲染器「引擎可插拔、接口统一」。
- **流式与连接**（`packages/core/src/pty/protocol.ts`）：用 WebSocket 把终端送到客户端。协议两种帧——裸 UTF-8 数据块（终端输出原样转发）+ `0x00` 前缀 + JSON 的光标控制帧（供重放定位）；`REPLAY_CHUNK = 64KB` 分块重放历史输出（新客户端连上能补看之前的）。
- **票据鉴权**（`packages/core/src/pty/ticket.ts`）：60 秒 TTL 的票据，绑定 `ptyID + directory + workspace`——短时效、强绑定，防止任意客户端连到别人的终端。
- **环境叠加**（`CONTEXT.md:105`）：PTY 创建时 env 分层组装、后层覆盖前层——①调用者传入的值（最底，可定制）→②host overlay（主机叠加层）→③Core 强制的终端不变量（最高，如 `TERM`、`OPENCODE_TERMINAL`，不可妥协）。「可定制的在中间，不可妥协的在最后」=既给灵活性又守住底线。
- **host overlay 复用 `shell.env` 钩子**：host overlay 由 `pty-environment.ts` 插件触发 L58 的 `shell.env` 钩子产生——**积木相扣**：L58 定义的钩子，在 L60 的 PTY 环境组装里被复用。一个机制服务多处，是好设计的标志。

## L61 ACP 与 Location

- **opencode = ACP 服务器（L59 的镜像）**（`packages/opencode/src/acp/agent.ts`）：ACP（Agent Client Protocol）是编辑器与 AI agent 对话的标准协议。opencode 的 `Agent` 类实现 ACP 的 `ACPAgent` 接口——`initialize` / `authenticate` / `newSession` / `loadSession` / `forkSession` / `prompt` / `cancel` / `setSessionModel` / `setSessionMode` / `setSessionConfigOption`。于是 Zed 等编辑器能把 opencode 当 AI 后端驱动。**镜像关系**：L59 里 opencode 当 LSP 客户端消费语言服务器，L61 里它当 ACP 服务器被编辑器消费——ACP 之于 agent 正如 LSP 之于语言服务器，都用标准协议把「M 编辑器 × N agent」塌缩成 M+N。
- **Location = 把「会话」与「它在哪儿跑」解耦**（`packages/core/src/location.ts`）：`Location.Info` = `{ directory（工作目录）, workspaceID?（可选，为集群/远程放置预留）, project（解析出的项目）}`。一份极简位置信息，但分量极重：工具、权限、文件系统、模型解析、SessionRunner **全是 Location 作用域的**——「能读写哪些文件、权限怎么算、用哪个模型」都相对一个 Location 确定，而非写死全局。
- **实现成 Effect Service（DI）**：Location 是个可注入的作用域服务（M2 依赖注入）。子系统通过依赖 `Location.Service` 确定作用域，而非各自摸全局「当前目录」。因为位置是注入的、非写死的，换一个 Location，整个会话的文件系统/权限/可跑命令视图整体平移，逻辑代码零改。这把「会话是谁要干什么」（身份）与「会话在哪儿跑」（位置）变成正交、可分别替换的两件事。
- **move-session = 会话「搬家」**（`packages/core/src/control-plane/move-session.ts`）：`MoveSession` 让会话整体搬到另一目录续跑。流程：①校验目的项目须匹配（`DestinationProjectMismatchError`，不能搬到属于完全不同项目的目录）；②可选连同文件改动搬（`moveChanges`）——用 git 在源目录捕获未提交改动、在目的目录应用（`CaptureChangesError` / `ApplyChangesError` 守着），又一次复用 git（同 L51 快照）。
- **「搬家」是地基自然长出的果**：之所以会话能换目录续跑、不是天方夜谭，根全在 Location 解耦——正因会话逻辑早已和「具体在哪个目录」剥离，「换目录继续」才不过是「给它新 Location + 把改动带过去」这么自然一件事，根本没为它写专门复杂逻辑。一个好的底层抽象（Location）会在意想不到的上层（move-session）开花——同 L60 末「积木相扣」主题。
