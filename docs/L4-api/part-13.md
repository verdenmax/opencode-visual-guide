# L4 · Part 13 源文件 → 课 对照 (API map)

opencode 源文件（`/home/verden/course/opencode`）→ Part 13 中讲到它的课。本部分覆盖 EventV2、命令、http-recorder、account/凭据、生态各包，以及三处深度扩写涉及的源。

| opencode 源文件 / 符号 | 关键点 | 讲到它的课 |
| --- | --- | --- |
| `core/src/event.ts` | `export * as EventV2`；`Cursor`(品牌化 NonNegativeInt，durable 重放续点)；`Definition{version, aggregate, data}`；`Payload`(可选 seq/version/replay)；`Projector/CommitGuard/Listener/Sync`=`(Payload)=>Effect<void>`；`SerializedEvent{seq, aggregateID}`；`versionedType(t,v)`；`InvalidSyncEventError` | L65 |
| `core/src/event/sql.ts` | `EventSequenceTable("event_sequence")={aggregate_id PK, seq, owner_id?}`；`EventTable("event")={id PK, aggregate_id→refs onDelete cascade, seq, type, data json}`；`uniqueIndex("event_aggregate_seq_idx").on(aggregate_id, seq)` + `index(aggregate_id, type, seq)` | L65 |
| `opencode/src/sync/README.md` | 单写入者⇒无分布式时钟/因果排序，单调 seq 给全序；向后兼容 `Bus`，`SyncEvent.run/subscribeAll` 类型安全 | L65 |
| `opencode/src/command/index.ts` | `Info`(Schema.Struct：name?/agent?/model?/source?Literals[command,mcp,skill]/template:Unknown/subtask?/hints:Array)，`type Info` template→`Promise<string>\|string`；`hints(template)`=`/\$\d+/g`+`includes("$ARGUMENTS")`；`Default={INIT,REVIEW}`；`Service`(`@opencode/Command`) `get/list`；`layer` yields Config/MCP/Skill；`Event.executed`="command.executed" | L66 |
| `opencode/src/command/template/{initialize,review}.txt` | 内置命令模板正文，含 `$ARGUMENTS`、`${path}` 占位符；`review.txt` 开头 "Input: $ARGUMENTS" | L66 |
| `packages/http-recorder/src/index.ts` | `HttpRecorder={http, socket}`；命名空间类型 `CassetteMetadata`/`RecorderOptions`/`RedactOptions`/`RequestMatcher`/`RequestSnapshot` | L67 |
| `packages/http-recorder/src/matching.ts` | `canonicalSnapshot(snapshot)`=JSON{method,url,`canonicalizeJson(headers)`,body 经 `decodeJson`}；归一化让语义同/字节序不同的请求命中同一磁带 | L67 |
| `packages/http-recorder/src/redaction.ts` | `REDACTED="[REDACTED]"`、`DEFAULT_REDACT_HEADERS`(authorization/x-api-key/x-goog-api-key…)、`DEFAULT_REDACT_QUERY`——录时盖密钥，磁带可安全入库 | L67 |
| `core/test/session-runner-recorded.test.ts` | `HttpRecorder.http("session-runner/openai-chat-streams-text", {directory:fixtures/recordings, mode:"record"?})`+`HttpRecorderInternal.cassetteLayer`，回放整条 V2 runner | L67 |
| `opencode/src/account/account.ts` | `DeviceAuth{device_code, user_code, verification_uri_complete, expires_in, interval}`；`DeviceTokenSuccess{access_token, refresh_token, token_type:"Bearer", expires_in}`；`DeviceTokenError.toPollResult()`(pending/slow_down/expired/denied→状态类)；`DeviceTokenRequest`/`TokenRefreshRequest`；`clientId="opencode-cli"`；`eagerRefreshThreshold=Duration.minutes(5)` | L68 |
| `core/src/credential.ts` | `OAuth{type:"oauth",access,refresh,expires,methodID,metadata?}`、`Key{type:"key",key,metadata?}`、`Info=Union([OAuth,Key]).toTaggedUnion("type")`、`Stored{id,integrationID,label,value}`、`Interface{all,list,get,create,update,remove}`、`CredentialTable` | L68 |
| `core/src/plugin/provider/openai-auth.ts` | 把凭据鉴权接进 provider（OAuth access 作 Bearer）——呼应 L35/L47 | L68 |
| `packages/app` (`@opencode-ai/app`) | SolidJS web UI，依赖 `@opencode-ai/sdk`+`core`+`ui`——经 SDK+事件连 server（网页面孔） | L69 |
| `packages/desktop` (`@opencode-ai/desktop`) | Electron（`electron-updater`/`electron-store`/`electron-log`）套壳 web app，带自动更新（桌面面孔） | L69 |
| `packages/slack` / `packages/enterprise` | `@slack/bolt`+sdk（Slack bot）／`@solidjs/start`+core+ui+aws4fetch（企业版） | L69 |
| `opencode/src/share/session.ts` | `Service`(`@opencode/SessionShare`) `share(sessionID)→{url}`/`unshare`，配 `share-next.ts`——把本地会话变可分享链接 | L69 |
| `packages/function/src/api.ts` | `SyncServer extends DurableObject<Env>`（Cloudflare），`SYNC_SERVER: DurableObjectNamespace`，`fetch()` 里 `WebSocketPair`+`ctx.acceptWebSocket`+`ctx.storage.list()` 取 `session/` 前缀——云端分享同步中转（建在 L65 单写入上） | L69 |
| `core/src/integration.ts` | `export * as Integration`，`IntegrationSchema`/`MethodID`/`IntegrationConnection`——声明式连接/触发器把外部事件接进会话 | L69 |
| `infra/` | SST 基础设施即代码，描述云端部署 | L69 |
| `packages/server/src` (`@opencode-ai/server`) | V2 API **契约表面**（`Api=HttpApi.make("server")`、`groups/handlers/middleware`），独立包，区别于 `opencode/src/server`（装配/启动）——深度扩写 | L10 |
| `packages/effect-drizzle-sqlite` / `packages/effect-sqlite-node` | 自研封装：把 Drizzle 的 driver/查询/迁移套进 Effect Service/Layer（`effect-sqlite` 驱动、迁移器）——L48 默认在用、深度扩写 | L48 |
| `opencode/src/worktree/index.ts` | `Event{worktree.ready, worktree.failed}`、`Info`(annotate "Worktree")、`CreateInput`、`import { Git }`——git worktree 给一次运行开隔离工作副本（同「复用 git」）——深度扩写 | L51 |
