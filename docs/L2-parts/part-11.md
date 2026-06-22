# L2 · Part 11 — 扩展与集成 (Extensibility & Integration)

**课程：** L57–L61 ｜ **状态：** 已完成

## 职责

Part 11 回答一个在「opencode 自己的界面讲透了」（M10）之后的问题：**这套内核如何向第三方与外部生态敞开——既让别人改造它，也让它借用别人？** 它分两条主线。第一条是**对外开放自己**：用 `@opencode-ai/plugin` 把「一个插件 = 一个返回钩子的函数」（L57），插件把函数挂进生命周期的 **Hooks**，统一靠 `plugin.trigger(name, input, output)`「传一份草稿、插件层层涂改」的模式涂改默认行为（L58，呼应 L54 produce、L47 IoC）。第二条是**反过来借用别人**：LSP 集成让 opencode 当 **LSP 客户端**，借来整个 IDE 生态的语言服务器，既被动收诊断（让 agent 看见自己刚犯的错）、又主动用 `lsp` 工具问「这是什么」（L59，呼应 L39 复用 Ripgrep）；PTY 让 agent 拿到一个**真终端**跑交互式命令，并用 WebSocket 把终端流给客户端、用「环境叠加」分层组装 env（L60，复用 L58 的 `shell.env` 钩子）。最后 L61 把视角拔高：opencode 反过来实现 **ACP** 当「agent 服务器」（被 Zed 等编辑器消费，是 L59「LSP 客户端」的镜像），并用 **Location** 把「会话是什么」与「它在哪儿跑」解耦，让 `move-session`「搬家」成为地基上自然长出的果。读完这部分，你就理解了 opencode 如何既是一个可被插件改造、可被编辑器驱动的「开放平台」，又是一个善于站在 IDE 生态肩膀上的「聪明借用者」。

## 覆盖范围

| 课 | 主题 | 一句话 |
| --- | --- | --- |
| L57 | 插件系统 | **一个插件 = 一个返回钩子的函数**（`@opencode-ai/plugin`）：`Plugin = (input: PluginInput, options?) => Promise<Hooks>`；`PluginInput`={client(opencode SDK 客户端)/project/directory/worktree/serverUrl/`$`(BunShell)/experimental_workspace}——给足「我是谁、在哪、能调谁」；返回 `Hooks` 对象声明「我想挂在哪些生命周期点」。`loader.ts` 的 `PluginLoader.loadExternal` 分阶段(install/entry/compatibility/load)健壮加载；配置 `plugin: Array<string | [string, options]>`（名/路径，可带选项）。**配置驱动**=不改内核、列个名字就接上；区别于 L47 的内核内部 `PluginV2.define`（这是给「外部用户」的公共 API） |
| L58 | 插件钩子详解 | **统一机制：trigger 一份草稿、插件层层涂改**：`plugin.trigger(name, input, output)`(如 `chat.params`、`system.transform`、`shell.env`)给每个钩子传只读 `input` + 可变 `output` 草稿，插件 `(input, output) => { output.xxx = ... }` **就地改草稿**、依注册序层层叠加(同 L54 produce/L47 IoC「编辑一份草稿」)。五类钩子：①observe(event/config/dispose 旁观)；②auth/provider(接入鉴权与模型源)；③chat(message/params/headers + experimental.system/messages.transform 改请求)；④tool(execute.before/after + shell.env 拦执行)；⑤permission.ask({status:"ask"\|"deny"\|"allow"} 守门)。内置 cloudflare/copilot/codex 都用 chat.params |
| L59 | LSP 集成 | **借来整个 IDE 生态的大脑**：opencode 是 **LSP 客户端**(非服务器)，复用成熟语言服务器(typescript/gopls/pyright/biome/oxlint/vue/deno，`lsp/server.ts` 按扩展名注册)。两副面孔：①**被动诊断**(`lsp/diagnostic.ts`)：收 `publishDiagnostics`，`report` 只留 severity===1 的 ERROR、`MAX_PER_FILE=20`、`pretty`=`ERROR [line:col] message`、`<diagnostics file>` 包裹——让 agent 编辑后立刻看见自己犯的错(注意力稀缺只报最关键)；②**主动 lsp 工具**(`tool/lsp.ts`)：9 个操作(goToDefinition/findReferences/hover/documentSymbol/workspaceSymbol/goToImplementation/prepareCallHierarchy/incoming·outgoingCalls)，参数 filePath+line+character(1-based)，让 agent 主动问「这符号是什么/谁调它」。复用整个生态(同 L39 Ripgrep/L51 git) |
| L60 | PTY 与 shell | **为什么需要一个真终端**：批处理(L39 bash)够跑 `ls`，但交互式 TUI 程序(vim/top/REPL)要 TTY(行编辑/颜色/光标/SIGWINCH)。`core/src/pty/pty.ts` 抽象 `Proc`(pid/onData/onExit/write/resize/kill)，`pty.bun.ts`/`pty.node.ts` 两后端同接口(同 L52 渲染器可插拔)。**流式与连接**：`pty/protocol.ts` 用 WebSocket——裸 UTF-8 数据块 + `0x00`+JSON 光标控制帧(供重放，`REPLAY_CHUNK=64KB`)；`pty/ticket.ts` 60s TTL 票据(绑 ptyID+directory+workspace)鉴权。**环境叠加**(CONTEXT.md:105)=调用者值→host overlay→Core 强制不变量(TERM/OPENCODE_TERMINAL)层层覆盖；host overlay 由 `pty-environment.ts` 触发 `shell.env` 钩子——**复用 L58**，积木相扣 |
| L61 | ACP 与 Location | **opencode 反过来做 agent 服务器**：`acp/agent.ts` 的 `Agent` 实现 ACP（Agent Client Protocol）的 `ACPAgent`(initialize/authenticate/newSession/loadSession/forkSession/prompt/cancel/setSessionModel·Mode·ConfigOption)，让 Zed 等编辑器把 opencode 当 AI 后端——**是 L59「LSP 客户端」的镜像**(ACP 之于 agent = LSP 之于语言服务器，标准协议把 M×N 塌缩成 M+N)。**Location**(`core/src/location.ts`)={directory, workspaceID?(为集群/远程预留), project}，实现成 Effect Service(M2 DI)；工具/权限/文件系统/模型/SessionRunner 全 Location 作用域——把「会话是什么」与「在哪儿跑」解耦成正交两件事。**move-session**(`control-plane/move-session.ts`)：会话搬到新目录续跑(校验 DestinationProjectMismatchError、可选 git 捕获/应用改动 moveChanges)——正因早已解耦，「换目录」只是「换个 Location」，是地基上自然长出的果 |

## 与相邻部分的关系

- **承接 Part 8/Part 7**：L57/L58 的外部插件是 M8 L47「provider 插件 / IoC 自登记」的对外公开版——L47 讲内核内部如何用 `PluginV2.define` 装配自己，本部分讲如何用 `@opencode-ai/plugin` 让**外部用户**安全改造它；L58 钩子里的 `tool.execute.before/after` 正是包在 M7 工具系统外的拦截点。
- **复用全书机制**：L58「trigger 传草稿、插件涂改」呼应 L54 `produce`、L47 IoC「编辑一份草稿」；L59 复用语言服务器、L60 复用 PTY 生态、L61 复用 git，同 L39 Ripgrep/L51 git「复用成熟工具」；L59 诊断「只报最关键」呼应 L42 注意力稀缺；L60 双后端同接口呼应 L52 渲染器可插拔；L60 的 env 复用 L58 `shell.env` 钩子（积木相扣）；L61 Location 作用域注入呼应 M2 Effect DI；L61「解耦是什么与在哪里」呼应 L47/L50/L54/L56「找准接缝」。
- **引出 Part 12**：本部分把「opencode 怎么向生态敞开、又怎么借用生态」讲透；至此全书的内核机制（M1–M11）已全部展开——剩下的是**怎么亲手把它跑起来、改起来、贡献回去**，以及一张串起全书概念的速查图，正是收官部分 **实战与速查** 的主题。

## 核心心智模型

1. **开放 = 把生命周期点暴露成钩子、把扩展做成配置项**（L57+L58）：插件不改内核源码，只「声明我想挂在哪、要改什么」，内核在固定点 `trigger` 出一份草稿让插件涂改。把「谁来扩展、扩展什么」从内核手里交出去（控制反转），让内核对未知的未来开放。
2. **传一份可变草稿，比传一堆参数更可组合**（L58）：`(input, output) => void` 让多个插件依次涂同一张草稿、各改一笔自然叠加，无需约定复杂的返回值合并——同 L54 produce、L47 IoC。这是贯穿全书的「编辑一份草稿」范式在扩展层的落地。
3. **站在生态肩膀上：能借就不自造**（L59+L60+L61）：语言智能借语言服务器(LSP)、真终端借 PTY 生态、版本控制借 git——opencode 反复选择复用成熟生态而非重造轮子，把精力留给真正独特的「agent 编排」。同 L39 Ripgrep、L51 git。
4. **诊断与工具：被动看见 + 主动询问**（L59）：同一套语言服务器，既被动推诊断让 agent「看见刚犯的错」(编辑后的安全网)、又被 `lsp` 工具主动查让 agent「问这是什么」(理解代码的眼睛)。一份能力两副面孔，且诊断只报最关键(注意力稀缺)。
5. **解耦「是什么」与「在哪里」，好抽象自会开花**（L61）：ACP 解耦 agent 与编辑器、Location 解耦会话与目录——把正交的两件事切开，于是 opencode 能被任意编辑器驱动、会话能在目录间「搬家」。`move-session` 这种高级能力没写专门逻辑，只是 Location 地基上自然长出的果。同 L47/L50/L54/L56「找准接缝」。
