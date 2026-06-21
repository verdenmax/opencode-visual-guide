# L2 · Part 8 — 配置、Agents 与 Provider (Config / Agents / Providers)

**课程：** L44–L47 ｜ **状态：** 已完成

## 职责

Part 8 回答一个在「脑」（M6 LLM）与「手」（M7 工具）都讲透之后必然要问的问题：**这一切，怎么被用户配置、定制、组装成一个真正可用的 agent？** 它把「一个 agent 怎么攒出来」拆成四块：配置系统（L44）把全系统的可调项收齐、校验、按「就近覆盖」合成一份生效配置；agent（L45）是配置里最核心的一格，一束「角色配置」（脑+手+许可+怎么跑），build 与 plan 揭示「角色差异≈权限差异」；MCP（L46）把外部工具服务器动态接进来，给 agent 接上 opencode 源码之外的「手」；Provider 插件（L47）用「广播+自我认领」的插件架构支持三十多家模型供应商，给 agent 接上外部的「脑」。读完这部分，你就理解了 opencode「如何把一颗脑、一双手，配置成一个可定制、可无限扩展的具体 agent」的全过程。

## 覆盖范围

| 课 | 主题 | 一句话 |
| --- | --- | --- |
| L44 | 配置加载 | `Config.Info`(config.ts)=类型化 Schema 接线总成（model/agents/permissions/mcp/tool_output/skills…）；识别 config.json/opencode.json(c)；从打开目录向项目根走 + 全局目录，排成 `Entry[]` 低→高优先级；`latest(entries,key)`=filter(document).map(key).findLast(≠undefined)（逐 key last-wins，同 L41 findLast）；铁律「越靠近打开目录的配置越优先」 |
| L45 | Agents：build 与 plan | `AgentV2.Info`(agent.ts)={model?,system?,mode:subagent\|primary\|all,steps?,permissions:Ruleset,hidden,color?,description?}；`defaultID=ID.make("build")`；**build vs plan 唯一实质区别在权限画像**：build 默认全能(可 edit)、plan「Plan mode. Disallows all edit tools」(`edit:{"*":"deny",plans/*.md:"allow"}`+task.general:deny+plan_exit:allow)；`Permission.merge(defaults,agent,user)` 用户最高；system 由角色基底+config 覆盖+M5 环境拼装；专用 agent prompt 外置 `agent/prompt/*.txt` |
| L46 | MCP 集成 | 外部工具服务器→**动态作用域工具**；`convertTool`(catalog.ts) 裹 AI SDK `dynamicTool`(execute=client.callTool)；名=`sanitize(server)+"_"+sanitize(tool)`(防重名)，同时是 `session/tools.ts` 的权限 key（**走和内置工具同一道权限闸门** L41）；local(command+StdioClientTransport 拉子进程) vs remote(url+StreamableHTTP→SSE 回退)；OAuth：needs_auth→`opencode mcp auth`→起 localhost 回调服务器→浏览器授权(PKCE+state)→换令牌→存 `mcp-auth.json`(0o600+文件锁) |
| L47 | Provider 插件定义 | 三十多家供应商=三十多个自包含插件(`plugin/provider/*.ts`)，`PluginV2.define({id,effect→钩子表})`，收进 `ProviderPlugins` 数组；**广播+自我认领**：`aisdk.ts` trigger `"aisdk.sdk"` 给所有插件，每个 `if(evt.package!=="@ai-sdk/xxx")return` 认领，匹配者 `createXxx` 设 evt.sdk（核心零 if-else=IoC）；三钩子 aisdk.sdk/aisdk.language(如 Copilot 选 Responses/Chat)/catalog.transform(如 Anthropic beta 头)；`import()` 动态导入按需加载；`DynamicProviderPlugin` 数组末位兜底(npm 装包) |

## 与相邻部分的关系

- **承接 Part 6/Part 7**：M6 给了 agent 的「脑」（怎么和模型对话）、M7 给了「手」（工具怎么定义/执行/管住）。本部分把它们**配置、组装**成一个具体 agent——L45 的 agent 一格指明用哪个脑（model→L47 Provider 解析）、配哪组手与权限（L41）；L46 给「手」加外部工具、L47 给「脑」加外部供应商。
- **复用 Part 5/Part 7 的机制**：L44 的 `latest` 用 L41 权限同款 `findLast`（就近覆盖）；L45 的 build/plan 差异完全落在 L41 的 Ruleset 上；L46 MCP 工具走 L37 注册表 + L41 权限 + 插件钩子，与内置工具一视同仁；L45 的 system 拼装直接用 M5 的 System Context（L21–27）。
- **引出 Part 9**：本部分把「一个 agent 怎么配出来、跑起来」讲透；agent 跑出来的会话、消息、上下文、权限规则，需要**落到磁盘并跨版本迁移**——这正是下一部分**持久化与存储**（Drizzle+SQLite）要解决的。

## 核心心智模型

1. **一个 agent = 配置攒出来的角色**（L45）：脑（model）+ 手（tools/MCP）+ 许可（permissions）+ 怎么跑（mode/steps），全是可声明、可定制的数据，不是写死的代码。加个新角色=往配置加一束卡，不改源码。
2. **就近覆盖、保留有序来源**（L44）：多来源配置排成 `Entry[]` 低→高，`latest` 逐 key `findLast` 取最高优先级的定义值——不预算合成，让每项「从哪来、为何是这值」始终可追（可解释性）。同套思路见 L41 权限 evaluate。
3. **角色差异 ≈ 权限差异**（L45）：build 与 plan 共用同一引擎/模型/工具，唯一实质区别是权限画像（plan 把 edit 全 deny）。把「这角色能做什么」做成可声明的权限规则，造受限新角色轻到只需写几条 deny。
4. **外来与原生平起平坐**（L46）：MCP 工具出身二等（运行时从外部服务器问来）、待遇一等（并入同一注册表、走同一道权限闸门、被同一批插件钩子观察）。系统不为扩展点开后门——越外来越不可控的工具，越要排进同一道闸。
5. **广播+自我认领=对扩展开放、对修改封闭**（L47）：核心不逐个认领供应商，而是广播「谁能处理这个包」，让插件自己举手。核心零 if-else 区分供应商（IoC），加供应商从「改核心 switch」变成「写新插件挂上去」。「插件」是贯穿 opencode 的统一扩展范式（boot.ts 里 agent/command/skill/config 皆插件）。
