# L3 · Part 9 细节要点 (Details)

## L48 Drizzle 与 SQLite

- **SQLite 当底座**：嵌入式、单文件关系库。`database.ts` 路径按发布渠道分：latest/beta/prod → `opencode.db`，其它 → `opencode-<channel>.db`（`OPENCODE_DB` flag 可覆盖，支持 `:memory:`/绝对路径/data 目录相对）。
- **开库即设 PRAGMA**（`database.ts`）：`journal_mode=WAL`（读写并发、耐崩溃）、`synchronous=NORMAL`（安全/速度折中）、`busy_timeout=5000`、`cache_size=-64000`（≈64MB）、`foreign_keys=ON`（让 references cascade 生效——SQLite 默认不强制外键，必须显式开）、`wal_checkpoint(PASSIVE)`。随后 `DatabaseMigration.apply(db)`。
- **Drizzle「代码即 schema」**：`drizzle.config.ts` 的 `schema:["./src/**/*.sql.ts","./src/**/sql.ts"]` 让表结构与领域代码同处。`sqliteTable("name",{cols},(t)=>[indices])`。列工具箱：`text()/integer()/real()`、`text({mode:"json"}).$type<T>()`（JSON 列+TS 类型）、`.$type<BrandedID>()`（品牌 ID 防混用）、`.references(()=>X.id,{onDelete:"cascade"})`、`.notNull()/.default()/.primaryKey()`。`Timestamps` 复用片段：`time_created`($default Date.now)+`time_updated`($onUpdate Date.now)，各表 `...Timestamps` 展开。
- **snake_case 命名约定**：列名用 snake_case（`project_id`），因 Drizzle 默认拿字段名当列名——`project_id:text()` 列名即 `project_id`，无需 `projectID:text("project_id")` 重写，省掉字段名/列名对不上的错误。
- **迁移自动生成**：drizzle-kit 比对 `*.sql.ts` 新结构与上版差异 → 生成 SQL 迁移到 `out:"./migration"`。迁移文件=`{id, up(tx)}`（如 `ALTER TABLE session ADD path text`，`satisfies DatabaseMigration.Migration`）。`migration.gen.ts` 按时间戳序汇总全部迁移（三十多个）；`schema.gen.ts`=drizzle-kit 自动重生的当前完整 schema 快照（两百多行 CREATE TABLE，永远等于「跑完所有增量后的结构」）。
- **双路径 `apply`**（`migration.ts`）：取 `Semaphore(1)` 串行 → 查 sqlite_master。① 有 `session` 表 → `applyOnly`：读 migration 日志已完成 id 集合、只补跑没记过的（各裹 `db.transaction`）；老 Drizzle 装机用 `__drizzle_migrations` journal，首次 seed 进新 migration 表避免重放。② 无表且空库 → 一个事务里跑 `schema.up`（schema.gen 完整快照）+ 建 migration 表 + 把全部迁移一次记「已完成」（不重放）。③ 非空却无 session 表 → `Effect.die("Database is not empty and has no session table")`（防误伤陌生库）。
- **三道纪律**：migration 日志表(id+time_completed)记已跑→幂等；各迁移裹事务→升级 SQL 与记账同生共死；Semaphore(1)→同时仅一个迁移流程。

## L49 核心数据表

- **session 表**（`session/sql.ts`，表网中枢）：`id`(PK)、`project_id`(→ProjectTable，cascade)、`workspace_id`、`parent_id`(自指→父会话)、`slug`、`directory`/`path`(DatabasePath 自定义列)、`title`/`version`/`share_url`/`summary_*`、`cost`(real)/`tokens_input·output·reasoning·cache_read·cache_write`、`agent`、`model`(JSON)、`permission`(JSON,PermissionV1.Ruleset)、`revert`(JSON{messageID,partID?,snapshot?,diff?})、`...Timestamps`、`time_compacting`/`time_archived`。索引 project/workspace/parent。
- **级联删除网**：project→session(project_id)、session→message→part(两级)、session→session_message/session_input/session_context_epoch/todo，外键几乎都 `onDelete:"cascade"`——删根连根带走、结构层保证无孤儿（依赖 L48 `foreign_keys=ON`）。注意 `parent_id`（子会话）是**带索引的普通自指列、并非外键**（无 `.references()`），**不参与级联**——删父会话不连带删子会话。
- **V1 message+part**：`message`(id,session_id→cascade,Timestamps,data JSON=V1MessageData)→`part`(id,message_id→cascade,session_id,Timestamps,data JSON=V1PartData)。两级、data 是 V1-shaped JSON 大对象。
- **V2 session_message**：id、session_id(cascade)、`type`、`seq`(单调)、Timestamps、data JSON；`uniqueIndex(session_id,seq)`（同会话不重号）+ 多个查询索引。
- **V2 session_input**（durable 输入箱）：id、session_id(cascade)、`prompt`(JSON)、`delivery`、`admitted_seq`(入箱号)、`promoted_seq?`(晋升号)；uniqueIndex(session,admitted_seq)、(session,promoted_seq)。先持久入箱→串行运行器在安全边界晋升成可见 session_message→崩溃不丢输入。
- **V2 session_context_epoch**：`session_id`(PK 即外键，1:1 cascade)、`baseline`、`agent`(default AgentV2.defaultID)、`snapshot`(JSON SystemContext.Snapshot)、`baseline_seq`、`replacement_seq?`、`revision`(default 0)。M5 上下文纪元落盘。
- **其它**：`todo`(复合 PK session_id+position)、`event`/`event_sequence`（EventV2 事件溯源：aggregate_id、seq、uniqueIndex(aggregate,seq)）。
- **seq 设计哲学**：单调递增序号 + 唯一索引 = 全序(谁在前) + 幂等(同号不插两次)；session_message/session_input/event 皆用。**列策略**：要查询/排序/约束的(id/session_id/type/seq)立结构化真列，松散负载(消息内容千变万化)塞 `text({mode:"json"})`——结构化骨架+JSON 血肉。

## L50 V1 存储与迁移

- **V1 文件存储**（`opencode/src/storage/storage.ts`）：`Storage` 服务 read/write/update/remove/list（key=`string[]`）。核心 `file(dir,key)=path.join(dir,...key)+".json"`——键即文件路径，`["session","proj","ses"]`→`storage/session/proj/ses.json`，整库=`Global.Path.data/storage` 下目录树。每文件路径配 `TxReentrantLock`（RcMap）：read 读锁、write/update 写锁，update=握写锁读改写。`list` 无索引只能 glob 整子树反推键。
- **文件存储的代价**：无索引（查询=遍历）、无跨对象事务、无外键 cascade、无关系查询——逼出向 SQLite（L48/L49）的迁移。
- **连文件也要迁移**：storage.ts 内置 `MIGRATIONS` 数组 + `storage/migration` 标记文件（整数）。驱动循环：读标记→从该处跑 `MIGRATIONS[i..]`→成功 `writeWithDirs(marker, i+1)`、失败 `logError`+`break`（不推进，下次重试）。`migration 1`：早期用目录名当项目 ID 不稳，改用 `git rev-list --max-parents=0 --all` 取仓库根提交哈希当稳定项目 ID，重组到 `session/<projID>/`、`message/<sesID>/`、`part/<msgID>/`。`migration 2`：抽 summary diff 到 `session_diff/`、摘要精简为增删行数汇总。
- **V1→V2 数据迁移**：`data-migration.sql.ts` 仅定义 `data_migration` 表（name PK + time_completed）——记账「哪个数据迁移已跑」，与 L48 `migration` 表同款「记账即幂等」（一个记 schema、一个记数据搬运）。
- **搬运与翻译解耦**：V1 文件数据搬进 SQLite `message`/`part` 表时**仍存 V1-shaped JSON**（即 L49「V1 同堂」之源），不立刻翻译；真正 V1→V2 语义转换**推迟到读取时**由 `session/message-v2.ts` 从 PartTable/MessageTable 读出 V1 行、当场投影成 V2 结构。好处：搬运退化成无脑字节复制（最安全）、语义映射集中一处可改、原始字节保真留「重新解释」退路。

## L51 压缩、摘要与快照

- **压缩触发**（`core/src/session/compaction.ts`）：`compactIfNeeded` 在 `auto` 开启且 `estimate({system,messages,tools}) > context − max(output, buffer)` 时调 `compactAfterOverflow`。常量：`DEFAULT_BUFFER=20000`、`DEFAULT_KEEP_TOKENS=8000`、`SUMMARY_OUTPUT_TOKENS=4096`、`TOOL_OUTPUT_MAX_CHARS=2000`。
- **select 切分**：从对话末尾倒着累加 token，保留最近 `tokens`(=keep 8k) 的消息逐字为 `recent`、更早为 `head`(待摘要)；切分点的消息可按剩余字符(`×4`≈token×4)劈成 splitPrefix(→head)/splitSuffix(→recent)。`serialize` 把各类消息(user/assistant/tool/system/synthetic/shell)转文本行、工具输出截断 2000 字符。
- **锚定式增量摘要**：`buildPrompt` 若已有 previousSummary（历史里有 `compaction` 消息）则「用对话历史更新这份锚定摘要：保留仍成立、删过时、并入新事实」，否则新建。固定 `SUMMARY_TEMPLATE`：Goal / Constraints & Preferences / Progress(Done/In Progress/Blocked) / Key Decisions / Next Steps / Critical Context / Relevant Files。LLM `stream`（无工具、maxTokens=summaryOutput≤4096）生成；发 `Compaction.Started`/`Ended` 事件携带 {summary, recent}。
- **快照=影子 git 仓库**（`opencode/src/snapshot/index.ts`）：gitdir=`Global.Path.data/snapshot/<project.id>/Hash.fast(worktree)`，所有命令带 `--git-dir <gitdir> --work-tree <worktree>`，**绝不碰项目真实 .git**。`track()`：首次 `git init`+一堆 tuning config(manyFiles/index.version 4/untrackedCache…)+`seed()`(`objects/info/alternates` 复用源仓库对象、copy 源 index 加速)→`add()`→`git write-tree` 返树哈希。`restore(snapshot)`：`git read-tree <snapshot>`+`checkout-index -a -f`。`diff/patch` 算改动。尊重 `.gitignore`(`--no-index` check-ignore)、屏蔽超大文件、`gc --prune`。每操作走 `lock(gitdir).withPermits(1)` 串行。
- **用 write-tree 而非 commit**：只需捕获文件状态树，不需 commit 信息/作者/父提交——最轻 git 原语。复用 git 内容寻址存储（如 L39 复用 Ripgrep）。
- **Revert**（`opencode/src/session/revert.ts`）：`revert({sessionID,messageID,partID?})`=退对话(裁掉 id≥messageID 的消息)+退文件(`snap.revert(patches)` 按补丁逐一还原改动过的文件)；revert 前 `rev.snapshot = session.revert?.snapshot ?? snap.track()`（先存「现在」）→ 若是再次 revert 先 `snap.restore` 旧快照 → `snap.revert(patches)`，算 diff 写 `session_diff`、存进 L49 session 表 `revert` 列。`unrevert`：`snap.restore(session.revert.snapshot)` 整体还原到 revert 前。状态持久化→重启仍有效。**对话与文件绑同一时间轴一起回退才自洽**。
