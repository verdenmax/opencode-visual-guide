# L4 · Part 4 源文件 → 课 对照 (API map)

opencode 源文件（`/home/verden/course/opencode`，均在 `packages/core/src/`）→ Part 4 中讲到它的课。

| opencode 源文件 / 符号 | 关键点 | 讲到它的课 |
| --- | --- | --- |
| `session/schema.ts` | `SessionSchema.Info`：id("ses_" 品牌化)、parentID、projectID、agent、model、cost、tokens、time、title、location、subpath | L14 |
| `session/message.ts` | `Message` = 8 成员 `Schema.Union`(按 type)；`AssistantContent` = text/reasoning/tool；`Assistant.content: Array`；`ToolState` = Pending/Running/Completed/Error | L14, L20 |
| `session/info.ts` | `fromRow`：DB 行 → SessionSchema.Info | L14 |
| `session/input.ts` | `SessionInput.admit`（publish Admitted 事件→admitted_seq，按 id 幂等）；`Admitted` 类；`Delivery` = steer/queue；`hasPending` | L15, L17 |
| `session/sql.ts` | `SessionInputTable`（id/prompt/delivery/admitted_seq/**promoted_seq**/time_created + 索引）；`SessionTable`/`MessageTable`/`PartTable` | L14, L15, L19 |
| `session/execution.ts` | `SessionExecution` 接口：`resume` / `wake(sessionID, seq?)` / `interrupt`（advisory drain 调度） | L15, L16 |
| `session/execution/local.ts` | `SessionRunCoordinator.make({ drain: …SessionRunner.run({force: mode==="run"}) })`；`{resume:coordinator.run, wake:coordinator.wake, interrupt:coordinator.interrupt}` | L16 |
| `session/run-coordinator.ts` | `Coordinator<Key,A,E>`（run/wake/awaitIdle/interrupt）；`make`；`Map<Key,Entry>`（每会话一车道）；`coalesce`（run 压倒 wake、wake 取 maxSeq）；状态机注释 idle→draining | L16 |
| `session/runner/llm.ts` | `MAX_STEPS=25`；`while(openActivity){for(step<MAX_STEPS){runTurn}}`；`llm.stream(request)`（一轮一次）；`FiberSet.make/run/clear`、`awaitToolFibers=raceFirst(join,awaitEmpty)`；`uninterruptibleMask((restore)=>restore(...))`；`failInterruptedTools`/`failUnsettledTools`；顶部契约清单注释 | L17, L18, L20 |
| `session/runner/index.ts` | `StepLimitExceededError`(TaggedErrorClass: sessionID/limit)；`RunError` 联合；`SessionRunner.Service`/`run({sessionID, force?})` | L17, L20 |
| `tool/registry.ts` | `ToolRegistry.materialize(permissions)` → `{definitions, settle}`；`whollyDisabled` → `registrations.delete(name)`（按权限筛） | L18 |
| `tool/tool.ts` | `settle(tool, call, context)`、`permission(tool, name)`、`definition(name, tool)`、`withPermission` | L18 |
| `tool-output-store.ts` | `MAX_LINES=2000`、`MAX_BYTES=50KB`、`RETENTION=7天`、`MANAGED_DIRECTORY="tool-output"`、`outputPaths` | L18 |
| `session/projector.ts` | `SessionProjector`：消费事件 insert/update `MessageTable`/`PartTable`；「新回合取代过时残行」注释；`PromptAlreadyProjected`/`SessionAlreadyProjected` | L19 |
| `session/history.ts` | `load`（并发取 baseline_seq + `latestCompaction`，据边界 `messageRows` → `decodeMessageRow`）；`loadForRunner`/`entriesForRunner`；`MessageDecodeError` | L17, L19, L20 |
| `session/event.ts` | `SessionEvent.PromptLifecycle.Admitted`、`SessionEvent.Step.Failed`（错误事件） | L15, L20 |
