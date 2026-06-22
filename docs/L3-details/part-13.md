# L3 · Part 13 细节要点 (Details)

## L65 EventV2 持久事件溯源与单写入同步

- **单写入者 = 全序变简单**：`sync/README.md` 原话——"only one device is allowed to write, we don't need any kind of sophisticated distributed system clocks or causal ordering. We implement total ordering with a simple sequence id (a number) and increment it by one every time we generate an event." 多写入者一致性是分布式难题（需向量时钟/共识），opencode 从源头消灭它：只留一个写入者，全序塌缩成 `counter += 1`。
- **核心类型**（`core/src/event.ts`，`export * as EventV2`）：`Cursor = NonNegativeInt.pipe(Schema.brand("EventV2.Cursor"))`（durable 重放续点）；`Definition{version, aggregate, data:Schema}`；`Payload`（可选 `seq`/`version`/`replay`，seq 注释「Durable aggregate order, populated while synchronized events are projected」）；`Projector/CommitGuard/Listener/Sync` 均 `(Payload)=>Effect<void>`；`SerializedEvent{seq, aggregateID}`；`versionedType(t,v)=`${t}.${v}``；`InvalidSyncEventError`。
- **两张表**（`event/sql.ts`）：`EventSequenceTable("event_sequence")={aggregate_id PK, seq, owner_id?}`（每聚合当前最大序号，会更新）；`EventTable("event")={id PK, aggregate_id→refs onDelete cascade, seq, type, data json}`（逐条不可变）。`uniqueIndex("event_aggregate_seq_idx").on(aggregate_id, seq)` 数据库层钉死「同聚合无重复 seq」（物理兜底，bug/并发抢同号即拒写，同 L37/L48「用错即响亮失败」）；`index(aggregate_id, type, seq)` 加速按类型查。
- **游标重放即同步**：同步设备带 `Cursor`→拉 `seq > cursor` 的事件依序成流→喂本地 `Projector` 重放（同 L19 投影器）→追平。durable cursor 让断线/几天后回来都不必从头重放。向后兼容 `Bus`（`SyncEvent.run/subscribeAll`），落地零可见变化。
- **三课一链**：L11 SSE=事件的实时**传输**；本课 EventV2=事件的**持久化+定序+同步**；L19 投影器=把带 seq 事件投成读模型。区别 L08 KeyedMutex：那是进程内按**文件路径/插件 id** 串行（非 session），本课是**跨设备**定序。

## L66 斜杠命令系统

- **命令 = 参数化模板**：`Info=Schema.Struct({name?, agent?, model?, source?:Schema.Literals(["command","mcp","skill"]), template:Schema.Unknown, subtask?, hints:Schema.Array(String)})`；`type Info` 把 template 收窄成 `Promise<string>|string`（MCP 远程是 lazy promise）。
- **hints 从模板读参数清单**：`hints(template)`=`template.match(/\$\d+/g)`（`$1/$2`，去重排序）+ `includes("$ARGUMENTS")`。让命令系统「不必额外声明几个参数」——直接从模板正文读。占位符：`$ARGUMENTS`(整串)、`$1/$N`(位置参)、`${path}`(构建模板时 `.replace("${path}", ctx.worktree)`，等环境而非等用户)。
- **三源归一（最点睛）**：`Command.layer=Layer.effect` 中 `yield* Config.Service / MCP.Service / Skill.Service`，把三种异质来源（本地 config/`.txt`、MCP 远程暴露、skill 体系）统一塑成同一个 `Record<string, Info>`，用 `source` 字段记出身。差异在 layer 构建期一次性吃掉，上层 `Service{get/list}` 一视同仁——「统一模子刻同形」（同 L36 Tool.make、L47 PluginV2）。
- **内置命令 + 执行**：`Default={INIT:"init", REVIEW:"review"}`，模板 `import PROMPT_INITIALIZE from "./template/initialize.txt"`/`PROMPT_REVIEW from "./template/review.txt"`，`review` 带 `subtask:true`。执行=取 Info→填占位符→成 prompt→跑（可 subtask/指定 agent·model）→发 `command.executed` 事件（流进 L65，可持久化/多端同步）。`list()` 供命令面板（L56）。

## L67 http-recorder 磁带录放测试

- **为什么难测**：agent 循环（L17）每次「问模型」非确定、花钱、慢、要联网。好测试要确定/快/免费/可离线，真打 API 全破。
- **录放机制**：`HttpRecorder={http, socket}`（`packages/http-recorder/src/index.ts`）录放 HTTP + WebSocket。**录制**真打一次、存命名磁带；**回放**让进来请求匹配磁带、原样放出响应。类型：`CassetteMetadata`、`RecorderOptions`、`RedactOptions`(「Additive redaction and header-preservation policy」)、`RequestMatcher`(「Returns whether an incoming HTTP request matches a recorded request」)、`RequestSnapshot`(「The normalized HTTP request representation used for matching」)。
- **匹配靠归一化**：`matching.ts` 的 `canonicalSnapshot(snapshot)`=JSON{method, url, `canonicalizeJson(headers)`, body 经 `decodeJson` 后规范化}。归一化让「语义同、字节序不同」（JSON 字段顺序/空白）的请求稳定命中同一磁带，逐字节比反而会因无关差异找不到录音。
- **脱敏故能入库**：`redaction.ts`：`REDACTED="[REDACTED]"`，`DEFAULT_REDACT_HEADERS`(authorization/x-api-key/x-goog-api-key…)、`DEFAULT_REDACT_QUERY`。录时盖掉密钥→磁带不含真实秘密、可安全提交当 fixture。`RedactOptions` 叠加式（默认底线+可再加，同 L60「安全默认+可定制」）。
- **边界与落地**：不验「模型答得对」，验「给定已知响应，runner/协议解析/工具调度对不对」——把「模型」这个不确定变量固定住。是 L63「测真实、少 mock」的极致手法（磁带=真实录音，非凭空捏造的 mock，不会假绿）。`core/test/session-runner-recorded.test.ts` 用一盘磁带回放整条 V2 runner，`mode:"record"` 切换重录。

## L68 Account 与设备码 OAuth

- **设备码流**（`opencode/src/account/account.ts`）：网页 OAuth 靠浏览器回调，CLI 没浏览器/没回调地址→走不通。设备码（OAuth 2.0 Device Authorization Grant，本为智能电视等输入受限设备设计）拆成「显示码+后台轮询」。`DeviceAuth{device_code(保密), user_code(给人输), verification_uri_complete, expires_in, interval}`；终端显示 user_code+URL、自己揣 device_code。
- **轮询与状态翻译**：终端每隔 `interval` 拿 device_code 问令牌端点（`DeviceTokenRequest{grant_type, device_code, client_id}`，`client_id="opencode-cli"`），返回 `DeviceTokenSuccess{access_token, refresh_token, token_type:"Bearer", expires_in}` 或 `DeviceTokenError`。`DeviceTokenError.toPollResult()` 把 error 串翻成状态类：authorization_pending→PollPending / slow_down→PollSlow / expired_token→PollExpired / access_denied→PollDenied / 其余→PollError——让轮询循环干净 switch 而非比对魔法字符串（同 L05/L20「原始值升格成有类型的值」）。
- **凭据库**（`core/src/credential.ts`）：`OAuth{type:"oauth", access, refresh, expires, methodID, metadata?}`、`Key{type:"key", key, metadata?}`、`Info=Union([OAuth,Key]).toTaggedUnion("type")`、`Stored{id, integrationID, label, value:Info}`、`Interface{all,list,get,create,update,remove}`、`CredentialTable`(`credential/sql`，落 SQLite)。OAuth 与 Key 异质塑成同形（同 L66/L36），上层按 type 分叉取用。
- **喂 provider + 预判续期**：取凭据喂 provider——OAuth 用 access 作 Bearer（呼应 L35 Copilot `AuthOptions.bearer`、L47 provider 插件 `plugin/provider/openai-auth.ts`）、Key 直接用；与 L46 MCP OAuth 互补。`eagerRefreshThreshold=Duration.minutes(5)`：过期前 5 分钟主动用 refresh 续，让你感觉不到令牌过期。

## L69 其余生态一览

- **一个 server、多副面孔**（L03/L09 决定）：内核跑成 server，所有界面只是客户端。`packages/app`(`@opencode-ai/app`，SolidJS web，依赖 sdk+core)、`packages/desktop`(`@opencode-ai/desktop`，Electron 套壳 web app、`electron-updater` 自动更新)、TUI（L52–56）、`packages/slack`(`@slack/bolt`+sdk)、`packages/enterprise`(SolidStart)，全经同一套 SDK（L12）+ 事件流（L11）连同一个 server——L56「数据与表现分离」终极兑现。桌面版几乎只是「给 web app 套 Electron 壳」。
- **分享 + 云同步**：`opencode/src/share/session.ts` 的 `Service`(`@opencode/SessionShare`) 提供 `share(sessionID)→{url}`/`unshare`。背后 `packages/function/src/api.ts` 的 `SyncServer extends DurableObject<Env>`（Cloudflare Durable Object，`fetch()` 里 `WebSocketPair`+`ctx.acceptWebSocket`+`ctx.storage.list()` 取 `session/` 前缀）接收推上的事件、广播给旁观者。建在 L65 单写入 sync 上：你是写入者，旁观浏览器/手机是「其他设备」只读重放追平。
- **接入与运维**：`core/src/integration.ts`(`export * as Integration`，`IntegrationSchema`/`MethodID`/`IntegrationConnection`，声明式触发器把外部事件接进会话，连外部服务要凭据→呼应 L68)；`packages/slack`(借 Slack 现成聊天界面当一副面孔)；`packages/enterprise`(SolidStart 企业版)；`infra/`(SST 基础设施即代码)。
- **全书收束**：内核（L09 拥有一切，自描述、广开门户）+ SDK/事件（L11/L12）→ 面孔（L52–56、本课）+ 扩展（L57–61）+ 接入运维（本课）。正因内核「数据与表现分离、广开门户」（L09/L56/L61），才能长出这么多面孔而不重复造轮子。读源码眼光：先找共享内核，再看周边如何围着它生长（从 `package.json` 依赖图就能读出「都连一个内核」）。
