# L2 · Part 9 — 持久化与存储 (Persistence)

**课程：** L48–L51 ｜ **状态：** 已完成

## 职责

Part 9 回答一个在 agent 跑起来（M4–M8）之后必然要问的问题：**agent 跑出来的会话、消息、上下文、权限规则，进程退出后存到哪儿、又怎么管？** 它把「持久化」拆成两层：先是「忠实地存」——用 SQLite 当嵌入式单文件底座、用 Drizzle 以「代码即 schema」定义表、用双路径迁移系统安全演进结构（L48）；核心表网以 session 为中枢、外键织成级联删除网、seq 编码顺序与一致性（L49）；再把早期散落在文件里的 V1 数据迁进 V2 SQLite，「搬运」与「翻译」解耦（L50）。然后是「智慧地管」——压缩把超长对话折成结构化锚定摘要、快照用「影子 git 仓库」给工作目录做时间机器、revert 把对话与文件绑在同一时间轴一起回退（L51）。读完这部分，你就理解了 opencode 如何忠实地存、安全地搬、智慧地管它的全部「记忆」。

## 覆盖范围

| 课 | 主题 | 一句话 |
| --- | --- | --- |
| L48 | Drizzle 与 SQLite | SQLite 嵌入式单文件库(<span>opencode.db</span>，按渠道分)；Drizzle「代码即 schema」(<span>sqliteTable</span> 在 <span>*.sql.ts</span>、snake_case 列名免重写、json 模式+$type 品牌、references cascade、Timestamps 复用)；database.ts PRAGMA(WAL/synchronous NORMAL/foreign_keys ON/busy_timeout/cache_size)；drizzle-kit 比对 schema 生成迁移；**双路径 apply**：新空库套 schema.gen 快照+全部迁移记「已完成」、老库 applyOnly 只补增量；migration 日志表(id+time_completed)幂等、各迁移裹事务、Semaphore(1) 串行 |
| L49 | 核心数据表 | **session 是表网中枢**(项目归属/展示/用量 tokens/状态 model·permission·revert JSON/时间)；几乎所有表外键回指 session 且 onDelete:cascade=**级联删除网**「无孤儿」(须 foreign_keys=ON)；parent_id 自指=子会话；**V1(message+part，data JSON 两级) 与 V2(session_message，单表+seq+type) 同堂**=平滑演进；**V2 三件套**：session_message(unique session,seq 定序)、session_input(durable 输入箱：admitted_seq 入箱→promoted_seq 晋升，崩溃不丢)、session_context_epoch(M5 快照 1:1)；seq 单调+唯一索引=全序+幂等；列策略=要查/排序/约束立真列、松散负载塞 JSON |
| L50 | V1 存储与迁移 | **V1 文件存储**(storage.ts)：键即路径 <span>file(dir,key)=join(dir,...key)+".json"</span>，string[] 键→嵌套 JSON 文件、整库=目录树、每文件 TxReentrantLock 读写锁；简单代价(无索引/事务/外键/关系查询)逼出 SQLite；连文件也内置 MIGRATIONS+storage/migration 标记(migration 1 用 git 根提交哈希 rev-list --max-parents=0 当稳定项目 ID 重组布局)；**V1→V2 数据迁移**用 data_migration 表(name+time_completed)记账(同 L48 migration 表「记账即幂等」，一个 schema 一个数据)；V1 数据搬进 message/part 表仍存 V1-shaped JSON、语义转换推迟到读取时 message-v2 投影=**搬运与翻译解耦** |
| L51 | 压缩、摘要与快照 | **压缩**(compaction.ts)：请求 token 超 上下文−max(输出,缓冲20k) 触发；select 切分=近况≈8k token(DEFAULT_KEEP_TOKENS)留原文+远的折结构化摘要(固定模板 Goal/Constraints/Progress/Decisions/Next Steps/Context/Files)；LLM 无工具限 4096 生成；**锚定式增量更新**(旧摘要上保留/删除/并入，主线不断裂)；可从单条消息中间切。**快照**(snapshot/index.ts)：**影子 git 仓库**(独立 --git-dir+--work-tree 指真实工作目录，绝不碰你的 .git)；track=write-tree 树哈希、restore=read-tree+checkout-index；alternates 共享对象、尊重 gitignore。**Revert**(revert.ts)：退对话(裁消息 N 之后)+退文件(restore 快照)同一时间轴；可 unrevert(revert 前先 track 存当前)，状态存 L49 session.revert 列 |

## 与相邻部分的关系

- **承接 Part 4–8**：M4 的 agent 循环、M5 的 Context Epoch、M7 的工具、M8 的配置/agent，跑出来的会话/消息/上下文/权限规则，全靠本部分落盘。L49 的 session 表存着 model/agent/permission(L41)/revert；session_context_epoch 持久化 M5 的 System Context 快照；session_input 是 V2 durable 输入箱。
- **复用全书机制**：L48 双路径迁移、L50 文件迁移、L50 数据迁移三处都用「日志表记账即幂等」同一范式；L51 压缩回响 L42「上下文稀缺」、L51 快照复用 git（如 L39 复用 Ripgrep、L35 复用上游目录）；L51 revert 依赖 L49 的 session.revert JSON 列。
- **引出 Part 10**：本部分把「记忆怎么存怎么管」讲透；这些存下来的会话、消息、上下文，最终要在终端被渲染成交互界面——这正是下一部分 **TUI 与客户端渲染** 要解决的。

## 核心心智模型

1. **代码即 schema + 双路径迁移**（L48）：表用 Drizzle 在 *.sql.ts 定义、snake_case 列名免重写；新库套完整快照、老库补增量；日志表记账给幂等、事务给原子、信号量给串行——结构演进既快又安全。
2. **session 为根、外键织网、seq 定序**（L49）：整个状态是一棵以 session 为根的树，cascade 保证无孤儿，单调 seq + 唯一索引把「顺序与不重不漏」直接编码进 schema——让数据库结构本身成为正确性的最后防线。
3. **新旧同堂是演进常态**（L49/L50）：V1 与 V2 在同一库共存、V1 文件数据先原样搬进 SQLite 再读取时投影成 V2——真实世界的 schema 是续写的历史，把「搬运」和「翻译」解耦让最危险的批量迁移退化成最无脑的字节复制。
4. **记账即幂等的迁移范式被复用三次**（L48 schema migration、L50 storage 文件布局 migration、L50 data_migration）：同一个「日志表记已完成、跳过已记录、失败即停不前进」的朴素思想，解决三类不同问题。
5. **持久化之上是记忆管理**（L51）：压缩管容量（近况留原文+远的折锚定摘要，回响 L42）、快照/revert 管时间轴（影子 git 复用 git 又隔离副作用、对话与文件绑同一时间轴一起回退才自洽）。存是基础，管才让记忆既装得下又退得回。
