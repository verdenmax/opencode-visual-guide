# L4 · Part 11 源文件 → 课 对照 (API map)

opencode 源文件（`/home/verden/course/opencode`）→ Part 11 中讲到它的课。插件公共 API 在 `packages/plugin/src/`，加载器/LSP/ACP 在 `packages/opencode/src/`，PTY/Location/control-plane 在 `packages/core/src/`。

| opencode 源文件 / 符号 | 关键点 | 讲到它的课 |
| --- | --- | --- |
| `packages/plugin/src/index.ts` | **公共插件 API** `@opencode-ai/plugin`：`Plugin = (input: PluginInput, options?) => Promise<Hooks>`；`PluginInput`={client(SDK)/project/directory/worktree/serverUrl/`$`(BunShell)/experimental_workspace}；`Hooks` 接口声明可挂的生命周期点 | L57, L58 |
| `packages/opencode/src/plugin/loader.ts` | `PluginLoader.loadExternal`：分阶段健壮加载 install→entry→compatibility→load，每阶段失败精准报错；解析配置 `plugin: Array<string \| [string, options]>` | L57 |
| `packages/opencode/src/plugin/*`(trigger) | `plugin.trigger(name, input, output)`：内核在生命周期点给插件传只读 input + 可变 output 草稿，插件 `(input,output)=>void` 就地涂改、按注册序叠加（编辑一份草稿，同 L54/L47） | L58 |
| `packages/opencode/src/session/llm/request.ts:114` | trigger `chat.params`：发给模型的请求参数成形处，插件可改温度/模型参数（内置 cloudflare/copilot/codex 都用此钩子） | L58 |
| `packages/opencode/src/session/agent.ts:379` | trigger `system.transform`：系统提示成形处，插件可改 system prompt（experimental.chat.system） | L58 |
| `Hooks` 五类钩子(`plugin/src/index.ts` ~222) | ①observe(event/config/dispose)；②auth/provider；③chat(message/params/headers + experimental.system/messages.transform)；④tool(execute.before/after + 注册 tool)；⑤permission.ask({status:"ask"\|"deny"\|"allow"}) | L58 |
| `packages/opencode/src/lsp/client.ts` | LSP **客户端**：连语言服务器、`publishDiagnostics` 处理器收诊断；opencode 戴「编辑器」帽子消费现成语言服务器 | L59 |
| `packages/opencode/src/lsp/diagnostic.ts` | `report`：只留 `severity===1` ERROR、`MAX_PER_FILE=20`、`pretty`=`ERROR [line:col] message`、`<diagnostics file>` 包裹塞上下文——编辑后让 agent 看见刚犯的错（注意力稀缺只报最关键） | L59 |
| `packages/opencode/src/lsp/server.ts` | 语言服务器**注册表**：按扩展名映射 typescript-language-server/gopls/pyright/biome/oxlint/vue/deno；打开文件即启动对应 server | L59 |
| `packages/opencode/src/tool/lsp.ts` | **`lsp` 工具**：9 操作 goToDefinition/findReferences/hover/documentSymbol/workspaceSymbol/goToImplementation/prepareCallHierarchy/incomingCalls/outgoingCalls；参数 filePath+line+character(1-based)；让 agent 主动问「这是什么/谁调它」 | L59 |
| `packages/core/src/pty/pty.ts` | `Proc` 抽象接口：pid/onData/onExit/write/resize/kill——给交互式程序(vim/top/REPL)一个真 TTY | L60 |
| `packages/core/src/pty/pty.bun.ts` / `pty.node.ts` | 两个后端实现、同一 `Proc` 接口(Bun/Node 运行时各一)——引擎可插拔、接口统一(同 L52 渲染器) | L60 |
| `packages/core/src/pty/protocol.ts` | WebSocket 协议：裸 UTF-8 数据块 + `0x00`+JSON 光标控制帧(供重放)；`REPLAY_CHUNK=64KB` 分块重放历史——把终端流给客户端 | L60 |
| `packages/core/src/pty/ticket.ts` | 60s TTL 票据，绑定 ptyID+directory+workspace——短时效强绑定鉴权，防连错终端 | L60 |
| `CONTEXT.md:105` | **环境叠加**顺序：调用者值 → host overlay → Core 强制不变量(TERM/OPENCODE_TERMINAL)；可定制的在中间、不可妥协的在最后 | L60 |
| `packages/core/src/pty/pty-environment.ts` | host overlay 来源：触发 L58 的 `shell.env` 钩子产生环境叠加——**复用 L58 钩子**，积木相扣 | L60 |
| `packages/opencode/src/acp/agent.ts` | `Agent` 实现 ACP 的 `ACPAgent`：initialize/authenticate/newSession/loadSession/forkSession/prompt/cancel/setSessionModel·Mode·ConfigOption——opencode 当 **ACP 服务器**被编辑器(Zed)消费，是 L59 LSP 客户端的镜像 | L61 |
| `packages/core/src/location.ts` | `Location.Info`={directory, workspaceID?(集群/远程预留), project}；实现成 Effect Service(DI)；工具/权限/文件系统/模型/SessionRunner 全 Location 作用域——解耦「会话是什么」与「在哪儿跑」 | L61 |
| `packages/core/src/control-plane/move-session.ts` | `MoveSession`：会话搬到新目录续跑；校验 `DestinationProjectMismatchError`；可选 `moveChanges` 用 git 捕获/应用未提交改动(`CaptureChangesError`/`ApplyChangesError`)——Location 解耦地基上自然长出的果 | L61 |
