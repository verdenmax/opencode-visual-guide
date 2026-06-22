# L2 · Part 13 — 深入专题 (Advanced Topics)

**课程：** L65–L69 ｜ **状态：** 已完成

## 职责

Part 13 是核心 12 部分之后的**进阶附录**。前 64 课走完后，引擎层已约 90% 完整；这一部分补齐覆盖分析发现的、**真正概念性、非顺带可推得**的几处缺口，并把全书几条主线收束起来。它讲 5 个深入专题：**L65 EventV2** 补上 L11（只讲了 SSE 传输）与 L19（只讲了投影）之间的拼图——事件如何被持久化、用单调 seq 定序、并让多端靠重放追平（单写入换简单）；**L66 斜杠命令** 揭示「命令 = 参数化 prompt 模板」，且把命令/MCP/skill 三源塑成同一个 `Info`（统一模子）；**L67 http-recorder** 给出「如何确定性地测试一个不确定系统」的标准解——把真实 LLM 往返录成磁带、回放（含脱敏）；**L68 设备码 OAuth** 讲 CLI 没浏览器回调怎么登录（显示码+后台轮询）、以及凭据库如何把 OAuth|Key 统一存取；**L69 生态一览** 鸟瞰内核之外的一整圈（多前端、分享云同步、集成、Slack、企业、基础设施），点破「一台引擎、多副面孔」这条贯穿全书的主线。读完这部分，你对 opencode 的理解从「引擎内部」扩展到「引擎驱动的整个生态」，并带走若干可迁移的工程智慧（用约束换简单、异质塑同形、录放驯服非确定、间接物解耦两端）。

## 覆盖范围

| 课 | 主题 | 一句话 |
| --- | --- | --- |
| L65 | EventV2 持久事件溯源与单写入同步 | **单写入换简单**：同一会话只许一台设备写，于是「谁先谁后」不需分布式时钟/共识——一个单调 +1 的 `seq` 给出全序。两张表 `event_sequence`(每聚合当前最大 seq) + `event`(逐条不可变事件, data JSON)，`uniqueIndex(aggregate_id, seq)` 钉死全序。同步=带 `Cursor` 拉「之后」的事件依序重放（喂给 L19 投影器）追平。向后兼容 `Bus`；补 L11(SSE 传输)/L19(投影)/L15(事件溯源) 之间的拼图。区别 L08 KeyedMutex（进程内按文件/插件 key 串行）：本课是跨设备定序 |
| L66 | 斜杠命令系统 | **命令 = 参数化 prompt 模板**：`Info`{name, description, template(`Promise<string>\|string`), source, hints, agent?/model?/subtask?}；`hints(template)` 用 `/\$\d+/g`+`includes("$ARGUMENTS")` 从模板正文读出参数清单；调用=填占位符成 prompt→跑→发 `command.executed` 事件（流进 L65）。最点睛：`Command.layer` 把**三源**（内置/config、MCP prompt、skill）统一塑成同一个 `Info`（`source` 记出身），上层 `get/list` 一视同仁——「统一模子刻同形」（同 L36/L43/L47）|
| L67 | http-recorder 磁带录放测试 | **录放驯服非确定**：agent 循环调真实 LLM（非确定/花钱/慢），直接打真 API 让测试今天绿明天红。**录制**真打一次、存磁带；**回放**让进来请求经 `canonicalSnapshot` 归一化、`RequestMatcher` 匹配、原样放出响应。两通道 `http`+`socket`。**脱敏**：`REDACTED="[REDACTED]"`+`DEFAULT_REDACT_HEADERS/QUERY` 盖掉密钥→磁带可安全入库。边界：不验「模型答得对」，验「给定已知响应我的 runner/协议/工具对不对」（同 L63「测真实、少 mock」，是其极致手法）。落地 `session-runner-recorded.test.ts` 回放整条 V2 runner |
| L68 | Account 与设备码 OAuth | **设备码流**：CLI 没浏览器回调，故把流程拆成「显示码+后台轮询」——终端显示 `user_code`+URL（`DeviceAuth`），你在任意有浏览器的设备授权，CLI 每隔 `interval` 轮询；`DeviceTokenError.toPollResult` 把 `authorization_pending`/`slow_down`/`expired_token`/`access_denied` 翻成轮询状态，成功得 `DeviceTokenSuccess`。「授权在别处、令牌落 CLI」用短码解耦。**凭据库**：`Credential.Info=Union[OAuth, Key]` 按 type 标签区分，进有 CRUD 的库（落 SQLite），`eagerRefreshThreshold=5min` 预判续期。喂给 provider（L35/L47），与 L46 MCP OAuth 互补。又一次「异质塑同形」|
| L69 | 其余生态一览 | **一台引擎、多副面孔**：内核 server 只有一个（L09），TUI/web(`app`)/桌面(`desktop`，Electron 套壳 web、带自动更新) 都经同一套 SDK（L12）+ 事件流（L11）连它——L56「数据与表现分离」的终极兑现。**分享+云同步**：`share(sessionID)→{url}` 把本地会话变链接，背后 `packages/function` 的 Cloudflare Durable Object `SyncServer`（WebSocket）让他人只读旁观——建在 L65 单写入 sync 上。**接入与运维**：`integration`(声明式触发器)、`slack`(@slack/bolt)、`enterprise`(SolidStart)、`infra`(SST)。全书收束：正因内核「数据与表现分离、广开门户」（L09/L56/L61），才能长出这么多面孔而不重复造轮子 |

## 与相邻部分的关系

- **收束全书 Part 1–12**：L65 补 L11/L15/L19 的事件主线深度盲点；L66/L68 复用 L36/L47「统一模子」、L66 接 L43 skills/L46 MCP；L67 接 L17 agent 循环 + L28+ 协议 + L63 测试哲学；L68 接 L35/L47/L46/L48 凭据持久化；L69 把 L09/L56/L61 的「一个 server、多副面孔」彻底展开，并把 L65 的单写入 sync 用在云端分享。
- **三处就地深度扩写**（不属本部分新课，但同期补入）：L10 点明 V2 API 表面在独立包 `@opencode-ai/server`（vs `opencode/src/server` 装配启动）；L48 补讲 `effect-drizzle-sqlite`/`effect-sqlite-node` 自研封装（把 Drizzle 包成 Effect 服务+迁移器）；L51 扩 `worktree`（隔离运行，同「复用 git」）。
- **全书终点**：Part 13 之后再无新机制——它把读者从「理解 opencode 引擎」送达「理解引擎驱动的整个生态」，并以 L69 的鸟瞰为全书画上句点。

## 核心心智模型

1. **用约束换简单**（L65）：与其去解「多写入者一致性」这个分布式难题，不如规定「只许一个写入者」，让全序塌缩成一个 `counter += 1`。主动施加一个约束，换来整套系统的极致简单——这是「找准接缝」之外的另一种工程智慧。
2. **异质塑同形**（L66+L68）：命令的三源、凭据的 OAuth|Key，本是异质的东西，却被塑成同一个带 type 标签的 `Info`，复杂度收进「塑形点」，上层一视同仁。读「把多种东西统一呈现」的子系统时，去找那个塑形点。同 L36/L43/L47。
3. **录放驯服非确定**（L67）：把「与外部世界的真实交互」从测试每次运行里抽出来、只做一次、冻成确定磁带——既真实（真协议字节）又确定（可重放），是 L63「测真实、少 mock」的极致手法，专治「非确定循环怎么测」。
4. **间接物解耦两端**（L68）：设备码用一个短码把「在浏览器授权」和「令牌落到收不了回调的 CLI」牵起来——用一个间接物（短码/票据）解耦两个本无法直接对接的端。轮询是「收不了推送时」的退而求其次。
5. **一个内核、多副面孔**（L69）：内核被做成「数据与表现分离、广开门户」，于是 TUI/web/桌面/Slack/云分享都只是连它的客户端，加一副面孔不必重写内核。读庞大系统先找那个大家共享的核心，再看每圈周边如何围着它生长。
