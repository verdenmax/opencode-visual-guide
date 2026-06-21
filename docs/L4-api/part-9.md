# L4 · Part 9 源文件 → 课 对照 (API map)

opencode 源文件（`/home/verden/course/opencode`，除注明外均在 `packages/core/src/`）→ Part 9 中讲到它的课。

| opencode 源文件 / 符号 | 关键点 | 讲到它的课 |
| --- | --- | --- |
| `database/database.ts` | `Database` 服务：`EffectDrizzleSqlite.makeWithDefaults()`；开库设 PRAGMA(`journal_mode=WAL`/`synchronous=NORMAL`/`busy_timeout=5000`/`cache_size=-64000`/`foreign_keys=ON`/`wal_checkpoint(PASSIVE)`)→`DatabaseMigration.apply`；`path()` 按 InstallationChannel 分 `opencode.db`/`opencode-<channel>.db`，`OPENCODE_DB` flag 覆盖 | L48 |
| `database/migration.ts` | `apply(db)`：`Semaphore(1)` 串行；有 session 表→`applyOnly`(读 migration 日志、补跑没记的、各裹事务、seed `__drizzle_migrations`)；空库→事务里 `schema.up`+建 migration 表+全部迁移记完成；非空无 session→`die`。`Migration={id,up(tx)}` | L48 |
| `database/migration.gen.ts` | 自动生成：按时间戳序 `import` 全部迁移(三十多个)汇成 `migrations` 数组 | L48 |
| `database/schema.gen.ts` | drizzle-kit 自动重生的当前完整 schema 快照(`schema.up(tx)`=一串 CREATE TABLE，两百多行)；新库套此快照 | L48 |
| `database/migration/<ts>_<name>.ts` | 单个迁移文件 `{id, up(tx)}`(如 `20260428..._add_session_path`=`ALTER TABLE session ADD path text`)；`20260511..._data_migration_state`=建 data_migration 表 | L48, L50 |
| `database/schema.sql.ts` | `Timestamps` 复用片段：`time_created`($default Date.now)+`time_updated`($onUpdate Date.now) | L48, L49 |
| `drizzle.config.ts`（`packages/core/`） | drizzle-kit 配置：`dialect:"sqlite"`、`schema:["./src/**/*.sql.ts","./src/**/sql.ts"]`、`out:"./migration"` | L48 |
| `database/path.ts` | 自定义列类型 `absoluteColumn`/`directoryColumn`/`pathColumn`/`absoluteArrayColumn`(路径规范化) | L48, L49 |
| `session/sql.ts` | **核心表网**：`SessionTable`(中枢：project_id→cascade/parent_id 自指/tokens/model·permission·revert JSON/Timestamps/time_compacting·archived)、`MessageTable`+`PartTable`(V1，data JSON 两级，cascade)、`SessionMessageTable`(V2，seq+type，uniqueIndex(session,seq))、`SessionInputTable`(durable 输入箱：prompt/delivery/admitted_seq/promoted_seq)、`SessionContextEpochTable`(M5 快照 1:1，session_id PK)、`TodoTable`(复合 PK) | L49 |
| `project/sql.ts` | `ProjectTable`(id/worktree/vcs/name/icon_*/sandboxes/commands JSON)、`ProjectDirectoryTable`(复合 PK project_id+directory，type main/root/git_worktree) | L49 |
| `event/sql.ts` | `EventSequenceTable`(aggregate_id PK/seq/owner_id)、`EventTable`(EventV2 事件溯源：aggregate_id→cascade/seq/type/data JSON，uniqueIndex(aggregate,seq)) | L49（对照） |
| `opencode/src/storage/storage.ts` | **V1 文件存储** `Storage` 服务 read/write/update/remove/list(key=string[])；`file(dir,key)=join(dir,...key)+".json"`(键即路径)；每文件 `TxReentrantLock`(RcMap) 读写锁，update=握写锁读改写；内置 `MIGRATIONS`(migration 1 用 `git rev-list --max-parents=0 --all` 根提交哈希当稳定项目 ID 重组布局；migration 2 抽 summary diff)+`storage/migration` 标记(读标记→跑 pending→成功+1/失败 break) | L50 |
| `data-migration.sql.ts` | `DataMigrationTable`=`data_migration`(name PK + time_completed)——V1→V2 数据迁移账本，同 L48 migration 表「记账即幂等」(一管 schema 一管数据) | L50 |
| `opencode/src/session/message-v2.ts` | 从 `PartTable`/`MessageTable` 读 V1 行、当场**投影**成 V2 消息结构(`SessionV1` 类型)——V1→V2 语义转换推迟到读取时，「搬运与翻译解耦」 | L50 |
| `session/compaction.ts` | **压缩**：`compactIfNeeded`(token 超 `context−max(output,buffer)` 触发)/`compactAfterOverflow`；`DEFAULT_BUFFER=20000`/`DEFAULT_KEEP_TOKENS=8000`/`SUMMARY_OUTPUT_TOKENS=4096`/`TOOL_OUTPUT_MAX_CHARS=2000`；`select`(倒序累加切 head/recent、可劈单条消息)、`serialize`、`buildPrompt`(锚定增量)、`SUMMARY_TEMPLATE`(Goal/Constraints/Progress/Decisions/Next Steps/Context/Files)；LLM stream 无工具生成、发 Compaction.Started/Ended | L51 |
| `opencode/src/snapshot/index.ts` | **快照=影子 git 仓库**：gitdir=`data/snapshot/<project.id>/Hash.fast(worktree)`、命令带 `--git-dir`+`--work-tree`(不碰真 .git)；`track`(init+tuning config+`seed` alternates 复用对象→`add`→`write-tree` 树哈希)、`restore`(`read-tree`+`checkout-index -a -f`)、`diff`/`diffFull`/`patch`；尊重 .gitignore、屏蔽大文件、`gc --prune`、`lock(gitdir).withPermits(1)` 串行 | L51 |
| `opencode/src/session/revert.ts` | **Revert**：`revert({sessionID,messageID,partID?})`=退对话(裁 id≥messageID)+退文件(`snap.restore`)，revert 前 `snap.track()` 存当前进 session.revert 列、算 diff 写 session_diff；`unrevert`(restore 回 revert 前)；状态持久化重启仍效 | L51 |
