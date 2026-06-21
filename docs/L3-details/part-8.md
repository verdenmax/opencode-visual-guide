# L3 · Part 8 细节要点 (Details)

## L44 配置加载

- **`Config.Info`（`config.ts`）= 类型化 Schema 的接线总成**：用 Effect Schema 定义的大类，几乎汇集 opencode 所有子系统的旋钮——model/shell、agents（L45）、permissions（L41 Ruleset）、mcp（L46）、tool_output（L42）、skills（L43）、instructions/commands/lsp…。类型化 → 加载即校验（写错字段/类型在解析关被挡，schema 即契约）。「一处声明、各取所需」：用户只在一处声明，每个子系统从同一份 Config.Info 取自己那格。
- **加载流程**：识别 `["config.json","opencode.json","opencode.jsonc"]`；从「打开的目录」**向上走到项目根**，沿途找 `.opencode` 目录 + 配置文件，再加全局配置目录；排成 `Entry[]`（`Document`｜`Directory`）**低→高优先级**。
- **`latest(entries, key)`**：`entries.filter(type==document).map(e=>e.info[key]).findLast(v=>v!==undefined)`——逐 key 取**最高优先级里有定义**的那项（last-wins）。与 L41 权限 `evaluate` 用同一个 `findLast`。
- **源码铁律**：「A config closer to the opened directory should win over one higher up.」优先级低→高：全局默认 < 项目根 < 更靠近 cwd 的特例。**特异压过宽泛**——全局是「我大体喜欢这样」，子目录是「就这块儿要特别这样」。
- **可解释性**：不预算合成一个大对象，而把有序来源留着、按 key 当场裁决——每项「从哪份配置来、为何是这值」清楚可追，排查「这 model 怎么是这个」顺优先级层层看即可。

## L45 Agents：build 与 plan

- **`AgentV2.Info`（`agent.ts`，已解析的 agent）= 一束角色配置**：`{model?, system?, mode:"subagent"|"primary"|"all", steps?, permissions:Ruleset, hidden, color?, description?}`。`defaultID = ID.make("build")`。`mode` 决定出场：primary（可作直接对话的主 agent）/ subagent（只能被派为子任务，L18 FiberSet）/ all。
- **config 侧 `ConfigAgent.Info`（`config/agent.ts`）字段几乎全可选**——配置只表达「想覆盖什么」，没写的走默认。「config 可选、resolved 必填」=L44「层叠覆盖」在 agent 上的落地。
- **build vs plan（核心对比）**：二者共用**同一套 agent 引擎、同样的工具、（默认）同一模型**——唯一实质区别是**权限画像**。build=默认全能编码 agent（可 edit）；plan=「Plan mode. Disallows all edit tools.」，定义本质=在默认权限上叠 `edit:{"*":"deny", ".opencode/plans/*.md":"allow"}`（拒一切编辑、只放行写计划文件）+ `task.general:"deny"` + `plan_exit:"allow"`。两者 `mode:"primary"`、native。
- **`Permission.merge(defaults, agentRules, user)`**：分层覆盖，**用户最高优先级**（同 L44 就近覆盖）。`plan_enter`/`plan_exit` 是在 build↔plan 间互转的权限动作。「角色=可声明配置+权限画像」→ 造受限新角色 = 写几条 deny；plan 的 `edit:"*":"deny"` 一句声明出「只规划、不动手」的安全 agent，原生支持「先规划、再执行」工作流。
- **system 拼装**：角色基底 prompt + config 的 system 覆盖 + M5 环境上下文（L21–27）。专用内置 agent 的 prompt 外置成 `agent/prompt/*.txt`（explore/compaction/summary/title…）——prompt 是会反复打磨的「文案」，理应当文档对待，非当代码编译。

## L46 MCP 集成

- **MCP = 把外部工具服务器动态接进 agent**：内置工具（L36–43）编译期写死、数量固定；MCP 让外部「工具服务器」运行时**动态**多出工具。两条主线=动态作用域工具 + OAuth。
- **动态工具**：连上服务器后发 `tools/list`，把服务器报的工具定义逐个经 `convertTool`（`catalog.ts`）裹进 AI SDK 的 `dynamicTool`——保留服务器 `inputSchema` 作约束，`execute` 只是把参数转发给 `client.callTool(name, args)`。相对内置工具的「static `Tool.make`」。
- **作用域 = 权限 key**：工具名 = `sanitize(serverName) + "_" + sanitize(toolName)`（`sanitize` = `/[^a-zA-Z0-9_-]/g → "_"`），如 `github_search`，防多服务器重名。这个作用域名同时是 `session/tools.ts` 里 `ctx.ask({ permission: key })` 的 key——**MCP 工具走和内置工具同一道权限闸门**（L41 Ruleset）、同一批插件钩子（tool.execute.before/after）。出身二等、待遇一等。
- **两种服务器**（`config/mcp.ts`，按 type 标签联合）：`Local{type:"local", command[], cwd?, environment?, disabled?, timeout?}` → `StdioClientTransport` 拉子进程、stdio 通信；`Remote{type:"remote", url, headers?, oauth?, disabled?, timeout?}` → HTTP 连，**先 StreamableHTTP、失败回退 SSE**。`connectTransport` 用 acquireUseRelease：连接失败自动关 transport。两种连上后同得一个 MCP `Client`，listTools/callTool 完全一致。
- **OAuth 舞蹈**：首连需认证的远程服务器撞 `UnauthorizedError` → 标 `needs_auth` → 提示 `opencode mcp auth <名>`。流程：起 localhost 回调 HTTP 服务器 → 开浏览器到授权页（PKCE code_challenge + state 防 CSRF）→ 登录授权 → 服务器重定向回 `localhost:port/callback?code&state` → 回调服务器截 code、核 state → code+code_verifier 换令牌 → 存 `mcp-auth.json`。
- **凭证存储**（`auth.ts`）：`mcp-auth.json` 用 `0o600`（仅文件主可读写，令牌是敏感凭证）+ 文件锁（flock 串行化，防多进程互相冲掉）。凭证碎片：tokens(accessToken/refreshToken/expiresAt)、codeVerifier(PKCE)、oauthState(CSRF)、clientInfo(动态客户端注册)。`isTokenExpired` 判过期、配 refreshToken 悄悄续期。服务器不支持动态注册 → 标 `needs_client_registration` 提示手填 clientId。

## L47 Provider 插件定义

- **每家供应商 = 一个自包含插件**（`core/src/plugin/provider/*.ts`）：`PluginV2.define({ id: PluginV2.ID.make("..."), effect: Effect.gen→钩子表 })`。最小的 `alibaba.ts` 不到 20 行。三十多个插件收进 `provider.ts` 的 `ProviderPlugins` 数组。**新增供应商 = 加文件 + 在数组加一行，核心零改动**（开闭原则）。
- **核心钩子 `aisdk.sdk`**：两步——① 自我认领 `if (evt.package !== "@ai-sdk/xxx") return`；② 造 SDK `const mod = yield* import("@ai-sdk/xxx"); evt.sdk = mod.createXxx(evt.options)`。`import()` 是**动态导入**，没用到的 SDK 不加载（按需）。
- **广播 + 自我认领**（`aisdk.ts`）：`AISDK.language(model)` → 查 `sdks` 缓存（按 sdkKey）→ 未命中则 `plugin.trigger("aisdk.sdk", {model, package, options}, {})` 广播给**所有**插件，匹配者设 evt.sdk → 仍空报 `No AISDK provider plugin returned an SDK` → 缓存 → `trigger("aisdk.language", {model, sdk, options})` → `result.language ?? sdk.languageModel(model.api.id)`。**核心通篇无一供应商名字**=控制反转（IoC）：供应商挂进核心，而非核心调供应商。
- **三个钩子**：`aisdk.sdk`（按 package 认领、造 SDK，人人都有）；`aisdk.language`（从 SDK 造语言模型、可定制路由，如 `github-copilot.ts` 的 `shouldUseResponses(modelID)` 对 GPT-5 类走 Responses、mini 走 Chat——L31/35 落地）；`catalog.transform`（改模型目录，如 `anthropic.ts` 给请求头加 `anthropic-beta: interleaved-thinking…,fine-grained-tool-streaming…`——L30 落地；Copilot 隐藏冲突的 `gpt-5-chat-latest` 别名）。
- **`DynamicProviderPlugin` 兜底**（`dynamic.ts`，数组末位）：`aisdk.sdk` 首行 `if (evt.sdk) return`——仅在内置全没认领时出场：`npm.add(package)` 临时装包 → import → 找 `create` 开头的导出当工厂。三十多家快路径 + 一个万能兜底 = 理论上任意供应商。`openai-compatible.ts` 同样 `if (evt.sdk) return` 守卫，处理通用 OpenAI 兼容端点。
- **统一插件范式**：provider 只是一类。`boot.ts` 启动序列里 AgentPlugin（L45）、CommandPlugin、SkillPlugin（L43）、各 ProviderPlugins、ModelsDevPlugin、Config*Plugin（L44）**全是插件**。`PluginV2.define({id, effect})` 的 effect 返回 `HookFunctions`（钩子名→处理器），output 字段是 Draft（immer 风格可变草稿），故插件 `evt.sdk = ...` 直接改。
