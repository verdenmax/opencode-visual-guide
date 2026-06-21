# L4 · Part 5 源文件 → 课 对照 (API map)

opencode 源文件（`/home/verden/course/opencode`，均在 `packages/core/src/`）→ Part 5 中讲到它的课。

| opencode 源文件 / 符号 | 关键点 | 讲到它的课 |
| --- | --- | --- |
| `system-context/index.ts` | `Source<A>`（key/codec/load/baseline/update/removed）；`make<A>`（closes over A → 不透明 SystemContext）；`combine`（拒绝重复 key）；`Snapshot`/`SourceSnapshot`；`unavailable` 符号；`initialize`→`Generation`；`InitializationBlocked`/`DuplicateKeyError` | L21, L22 |
| `system-context/index.ts`（compare/reconcile/replace） | `make` 派生 `decodeUnknownOption`/`encodeSync`/`toEquivalence`；`Compared` = Incompatible/Unchanged/Updated；`reconcile`、`replace`（`replaceObservation`：Unavailable+旧快照有→`ReplacementBlocked`，否则 `ReplacementReady`） | L22, L24, L27 |
| `system-context/registry.ts` | `SystemContextRegistry`：`Entry{key,load}`；`register`（`Effect.acquireRelease` 作用域绑定、重复 key `die`）；`load`（`toSorted` by key + `forEach concurrency:"unbounded"` + `combine`） | L23 |
| `system-context/builtins.ts` | `core/environment`（`<env>` Working directory/Workspace root/Is git repo/Platform）、`core/date`（`DateTime.nowAsDate`→`toDateString`，baseline/update）；`layer`（merge InstructionContext + provide registry） | L26 |
| `instruction-context.ts` | `InstructionContext`：AGENTS.md 等项目指令包装成源 | L26 |
| `session/context-epoch.ts` | `SessionContextEpoch.prepare`/`prepareOnce`/`initialize`；`reconcile` vs `replace` 分支；`Prepared{baseline,baselineSeq,revision}`；**`AgentReplacementBlocked`**(sessionID/previous/current)；`fence`（核对 agent/revision→AgentMismatch/RevisionMismatch）；`requestReplacement`（set replacement_seq）；`retryRevisionMismatch` | L24, L27 |
| `session/sql.ts` | `SessionContextEpochTable`（`session_context_epoch`：baseline / **baseline_seq** / snapshot / revision / agent / replacement_seq） | L24 |
| `session/event.ts` | `SessionEvent.ContextUpdated`（type `session.next.context.updated`，字段 messageID + **text**） | L24, L25 |
| `session/message.ts` | `Session.Message.System`（`type:"system"`，`text: SessionEvent.ContextUpdated.data.fields.text`——借用事件字段类型） | L25 |
| `session/projector.ts` | `events.project(SessionEvent.ContextUpdated, …)` 与 Text/Tool/Reasoning/Synthetic/Step **并列**；`requestReplacement`（replay 时） | L25 |
| `session/history.ts` | `history.load` 并发取 `baseline_seq`（来自 SessionContextEpochTable）给历史窗口裁边——L24 钉下、此处消费 | L24（呼应 L19） |
