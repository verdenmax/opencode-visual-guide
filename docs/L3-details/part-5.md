# L3 · Part 5 细节要点 (Details)

## L21 System Context 总览

- **系统上下文（privileged system context）**：对话之外、系统替模型主动注入的「环境底色」（目录/日期/git/指令）——把模型锚定到真实世界，且**特权**：和用户的话不在一个层级。
- **Source&lt;A&gt;**（`system-context/index.ts`）声明六件事：key（命名空间 `domain/path`）、codec、load（观察，或返回 **unavailable**）、**baseline(current)**（首次全文）、**update(prev,cur)**（变化差异）、removed。
- **代数**：`make<A>(source)` 把值类型 A closes over → 不透明 `SystemContext`；`combine([...])` 均匀组合异类源、拒绝重复 key。加新源无需改任何现有代码（第 6 课思想延伸）。
- **baseline/update** 解「token 难关」：首次发全文、之后只发增量。
- **unavailable ≠ removed**：`load` 返 `unavailable` 表「暂时观察不到」≠ 删除；刷新保住上一份快照，绝不悄悄拼残缺 baseline（L27 终极兑现）。`initialize` 产 `Generation`（baseline 文本 + Snapshot）。

## L22 Context Source

- **codec 一肩三挑**：`make` 从 `source.codec` 派生 `decodeUnknownOption`（读快照）、`encodeSync`（存快照）、`toEquivalence`（判等）。**声明结构、判等自来**，无需手写「日期/目录怎么比」。
- **baseline = 一说一记**：`source.baseline(value)` 渲染人类可读全文给模型，`encode(value)` 存结构化 `SourceSnapshot` 给系统（沟通用散文、记忆用结构）。快照是增量机制的锚。
- **compare(previous)** 三选一：`decode` 旧快照→ `onNone`=**Incompatible**（codec 变过、旧档作废→退回重 baseline）；`onSome` + `equivalent`→ **Unchanged**（沉默省 token）/ **Updated**（渲染 update 差异 + 存新快照）。
- `decode` 用 Option，把「旧档读不出」收进类型（第 5、8 课「错误即值」微观体现）。

## L23 System Context Registry

- 内部一个 `Ref<Entry[]>`；`Entry = {key, load: Effect<SystemContext>}`（存「怎么取」而非「取到啥」→每次 load 重新观察、永远最新）。
- **register** 用 `Effect.acquireRelease`（作用域绑定）：注册即声明「在此作用域内存在」，作用域关**必然自动注销**——根除「忘了删、源变幽灵」泄漏。重复 key 直接 `die`。
- **load**：① `toSorted` 按 key 排序（确定顺序、与注册先后无关→可复现、不假性 diff）；② `forEach concurrency:"unbounded"` 并发观察（各源独立、求快）；③ `combine` 归一。**观察求快、排序求稳**。
- 注册表是「编排者」而非「内容生产者」：源对它是不透明 SystemContext，故加多少源都零改动。

## L24 Context Epoch

- **纪元 = 快照 + 锚点**，每会话一行（`session_context_epoch` 表）：`baseline`（说给模型）、**`baseline_seq`**（钉在时间线的图钉）、`snapshot`（记给系统）、`revision`（乐观并发版本号）、`agent`、`replacement_seq`。
- **prepare 每次运行前对表**（`SessionContextEpoch.prepare`→`prepareOnce`）：并发取 context 值 + stored 存档。
  - 无存档 → `SystemContext.initialize` → `insert` → baselineSeq, revision=0。
  - 同 agent → `reconcile`：Unchanged（沿用旧基线）/ Updated（**publish `SessionEvent.ContextUpdated`** + `advance` revision；与发事件绑成原子 commit）。
  - 换 agent → `replace`（L27）。
- **上下文变化也走事件溯源**：Updated 是 publish 一条 ContextUpdated（非改字段）——「先持久、再推进」（第 15 课）。
- **baselineSeq 合上第 19 课**：`history.load` 并发取 `baseline_seq` 给历史窗口裁边——上下文系统与会话引擎由此缝成一体。`retryRevisionMismatch` 守乐观并发。

## L25 会话中系统消息

- 第 24 课的 `ContextUpdated` 事件被**投影成一条 System 消息**（`message.ts`：`type:"system"`，`text` 直接复用 `SessionEvent.ContextUpdated.data.fields.text`），按 seq **原位插**在变化发生点。
- **走同一条投影流水线**：`projector.ts` 里 `ContextUpdated` 和 `Text`/`Tool`/`Reasoning`/`Synthetic`/`Step` **并列** `events.project(...)`，无特殊通道——「把特殊做成不特殊」，自动继承持久/有序/可重放/原位。
- **位置即意义**：原位保住环境变化的**时机**，模型才能理解早先消息语境（对比「钉在 prompt 扉页」会压扁时间线、丢失因果）。还让环境演变史可精确重放。
- 辨析：这里的 System 消息 ≠ 开场定义人设的 system prompt（那个落在 baseline）；它专指「中途才发生、所以插在中途」的环境变化。

## L26 内置 Context Sources

- **core/environment**（`builtins.ts`）：`<env>` 标签裹 Working directory / Workspace root / Is git repo / Platform——agent 最起码的「我在哪」。贵精不贵多。
- **core/date**：`load = DateTime.nowAsDate → toDateString()`；baseline「Today's date: X」、update「Today's date is now: X」。**连日期都是源**，因会话可能跨午夜。措辞用 `now` 区分初始/变化。
- **InstructionContext**（`instruction-context.ts`）：AGENTS.md 等项目指令，也是一视同仁的源。
- 源定义 ~5 行（key/codec/load/baseline/update），重活全被框架吸走=**好抽象试金石**。core 源和插件源同一套机制（dogfooding）。

## L27 Agent 切换与 Epoch 替换

- 换 agent → `SystemContext.replace`：**从零重建**基线（旧「人设」作废）。
- **关键差异**：`reconcile` 容忍源 unavailable（保住旧快照）；`replace` 不能——新基线无旧快照保底，每源须当场新鲜观察到。
- **为什么 block**：`replaceObservation` 若发现「某源现在 Unavailable **且**旧快照里曾经有」→ `ReplacementBlocked`。硬拼等于把该源从新 agent 世界悄悄抹掉。`prepareOnce` 据此抛 **`AgentReplacementBlocked`**（带 sessionID/previous/current），保留旧纪元、等重试——第 21 课 unavailable≠removed 终极兑现。
- **fence + revision**：`fence` 写入前核对 agent/版本，不符 `die` RevisionMismatch/AgentMismatch → `retryRevisionMismatch` 退让重试——切换原子一致，绝无半切错乱纪元。
- 两道防线（block 防残缺 / fence 防错乱）= 对「根基性中间态」零容忍：纪元要么完整一致地建立、要么不动。
