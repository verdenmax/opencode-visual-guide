# L4 · Part 8 源文件 → 课 对照 (API map)

opencode 源文件（`/home/verden/course/opencode`，除注明外均在 `packages/core/src/`）→ Part 8 中讲到它的课。

| opencode 源文件 / 符号 | 关键点 | 讲到它的课 |
| --- | --- | --- |
| `config.ts` | `Config.Info`=Effect Schema 大类（接线总成：model/shell/agents/permissions/mcp/tool_output/skills/instructions/commands/lsp…）；识别 `["config.json","opencode.json","opencode.jsonc"]`；从打开目录向项目根走 + 全局目录 → `Entry[]`(Document｜Directory) 低→高优先级；`latest(entries,key)`=filter(document).map(key).`findLast`(≠undefined)（逐 key last-wins，同 L41）；铁律「closer to opened dir wins」 | L44 |
| `config/*`（各 config 模块） | 子配置 schema（`config/mcp.ts`、`config/agent.ts`、`config/tool-output.ts`…）；顶部自导出模式 `export * as ConfigXxx from "./xxx"` | L44, L45, L46 |
| `v1/config/*` | V1 配置兼容层（`ConfigV1`、`ConfigMCPV1`…），与 V2 config 并存 | L44, L46 |
| `agent.ts` | `AgentV2.Info{model?,system?,mode:"subagent"\|"primary"\|"all",steps?,permissions:Ruleset,hidden,color?,description?}`；`defaultID=ID.make("build")`；mode 决定 primary/subagent/all 出场 | L45 |
| `config/agent.ts` | `ConfigAgent.Info`（config 侧 agent 配置，字段几乎全可选——只表达想覆盖什么） | L45 |
| `packages/opencode/src/agent/agent.ts` | **build vs plan 定义**：build=「default agent, executes tools based on configured permissions」(可 edit)；plan=「Plan mode. Disallows all edit tools.」`Permission.merge(defaults, fromConfig({question:allow, plan_exit:allow, task:{general:deny}, edit:{"*":"deny", ".opencode/plans/*.md":"allow"}}), user)`；两者 mode:"primary"、native；`plan_enter`/`plan_exit` 互转 | L45 |
| `packages/opencode/src/agent/prompt/*.txt` | 专用内置 agent 的 prompt 外置纯文本：`explore.txt`(探索子 agent)、`compaction.txt`(压历史)、`summary.txt`、`title.txt`、`generate.txt`——prompt 当文档管理 | L45 |
| `packages/opencode/src/mcp/index.ts` | MCP 服务（`layer`）：`connectLocal`(StdioClientTransport spawn `command`)、`connectRemote`(StreamableHTTP→SSE 回退 + OAuth)、`connectTransport`(acquireUseRelease 连接失败自动关)；`tools()`=遍历 connected clients、`McpCatalog.sanitize(client)+"_"+sanitize(tool)` 作 key、`convertTool` 物化；`needs_auth`/`needs_client_registration` 状态；`ToolsChanged` 事件 | L46 |
| `packages/opencode/src/mcp/catalog.ts` | `convertTool(mcpTool,client,timeout)`→AI SDK `dynamicTool`(execute=client.callTool)；`sanitize`=`/[^a-zA-Z0-9_-]/g→"_"`；`defs`(listTools 容错 outputSchema)、`paginate`、`prompts`/`resources`(按 capabilities)；fetch 用 `sanitize(client)+":"+sanitize(name)` | L46 |
| `packages/opencode/src/mcp/auth.ts` | `McpAuth` 服务：`mcp-auth.json`（`Global.Path.data`）存 `Entry{tokens,clientInfo,codeVerifier,oauthState,serverUrl}`；写用 `0o600` + `EffectFlock` 文件锁；`isTokenExpired`(expiresAt<now)；get/set/updateTokens/updateCodeVerifier/updateOAuthState… | L46 |
| `packages/opencode/src/mcp/oauth-provider.ts` | `McpOAuthProvider implements OAuthClientProvider`：`redirectUrl`、`clientInformation`/`saveClientInformation`(动态注册)、`tokens`/`saveTokens`、`codeVerifier`/`saveCodeVerifier`(PKCE)、`state`/`saveState`(CSRF)、`redirectToAuthorization`、`invalidateCredentials` | L46 |
| `packages/opencode/src/mcp/oauth-callback.ts` | localhost 回调 HTTP 服务器（`createServer`）：`ensureRunning(redirectUri)`、`handleRequest` 解析 `?code&state`、`pending.resolve(code)`、`escapeHtml` 防注入；多 pendingAuths 计数、空了关 server | L46 |
| `core/src/config/mcp.ts` | `ConfigMCP`：`Local{type:"local",command[],cwd?,environment?,disabled?,timeout?}`、`Remote{type:"remote",url,headers?,oauth?,disabled?,timeout?}`、`OAuth{client_id?,client_secret?,scope?,callback_port?,redirect_uri?}`；`Server=Union(Local,Remote) toTaggedUnion("type")` | L46 |
| `packages/opencode/src/cli/cmd/mcp.ts` | `opencode mcp auth/list/add` 命令；`oauthServers`(筛 remote+oauth≠false)、`authState`、状态文案(authenticated/needs authentication) | L46 |
| `packages/opencode/src/session/tools.ts` | 把 `mcp.tools()` 动态工具并入会话工具集；`ctx.ask({permission: key, patterns:["*"], always:["*"]})`——**MCP 工具走和内置工具同一道权限闸门**（key=作用域名）；plugin `tool.execute.before/after` 钩子 | L46 |
| `core/src/plugin/provider.ts` | `ProviderPlugins` 数组：导入并列出三十多个 provider 插件（Alibaba/Anthropic/OpenAI/Google/Bedrock/Groq/xAI…），**`DynamicProviderPlugin` 排末位** | L47 |
| `core/src/plugin/provider/alibaba.ts` | 最小插件模板：`PluginV2.define({id, effect})`，`"aisdk.sdk"`=`if(evt.package!=="@ai-sdk/alibaba")return; evt.sdk=createAlibaba(options)`（动态 import） | L47 |
| `core/src/plugin/provider/anthropic.ts` | `catalog.transform`：给 `@ai-sdk/anthropic` 模型加 `anthropic-beta: interleaved-thinking-2025-05-14,fine-grained-tool-streaming-2025-05-14` 请求头（L30 落地）；+ `aisdk.sdk` | L47 |
| `core/src/plugin/provider/github-copilot.ts` | `aisdk.language`：`shouldUseResponses(modelID)`(gpt-≥5 且非 mini→Responses，否则 Chat)（L31/35 落地）；`catalog.transform` 隐藏冲突的 `gpt-5-chat-latest` 别名；`aisdk.sdk` 导 `copilot-provider` | L47 |
| `core/src/plugin/provider/dynamic.ts` | `DynamicProviderPlugin`：`if(evt.sdk)return`（兜底）；`npm.add(package)` 临时装包 → `import` → 找 `create` 开头导出当工厂 | L47 |
| `core/src/plugin/provider/openai-compatible.ts` | `if(evt.sdk)return` + `if(!evt.package.includes("@ai-sdk/openai-compatible"))return`；`createOpenAICompatible`；默认 `includeUsage=true` | L47 |
| `core/src/aisdk.ts` | `AISDK.language(model)`：`sdks` 缓存(sdkKey)；`plugin.trigger("aisdk.sdk", {model,package,options})` 广播收 sdk → 空报 `No AISDK provider plugin returned an SDK`；`trigger("aisdk.language")` → `result.language ?? sdk.languageModel(id)`；**通篇无供应商名**(IoC) | L47 |
| `core/src/plugin.ts` | `PluginV2.define({id, effect})`；`HookSpec`（`aisdk.sdk`{in:{model,package,options} out:{sdk?}}、`aisdk.language`{out:{language?}}、`catalog.transform`…）；`HookFunctions`；output 字段为 Draft（immer 可变草稿） | L47 |
| `core/src/plugin/boot.ts` | 启动序列 `boot`：add AgentPlugin/CommandPlugin/SkillPlugin → `for ProviderPlugins` → ModelsDevPlugin → Config*Plugin——**全系统皆插件**的统一范式 | L47 |
