# L4 · Part 2 源文件 → 课 对照 (API map)

opencode 源文件（`/home/verden/course/opencode`）→ Part 2 中讲到它的课。

| opencode 源文件 / 符号 | 关键点 | 讲到它的课 |
| --- | --- | --- |
| `AGENTS.md` (Effect rules) | `Effect.gen` / `Effect.fn("Domain.method")` / `fnUntraced` / `Schema.TaggedErrorClass` / "Avoid try/catch" | L05, L06, L08 |
| `packages/core/src/effect/` | 自建 Effect 工具箱目录 | L08 |
| `packages/core/src/effect/memo-map.ts` | `export const memoMap = Layer.makeMemoMapUnsafe()` | L06, L08 |
| `packages/core/src/effect/keyed-mutex.ts` | `KeyedMutex<Key>`：同 key 串行、异 key 并行 | L08 |
| `packages/core/src/effect/service-use.ts` | `serviceUse(tag)`：省调用服务样板 | L08 |
| `packages/core/src/effect/runtime.ts` | `makeRuntime`（共享 memoMap 去重 Layer） | L06, L08 |
| `packages/core/src/agent.ts` | `Context.Service<Service,Interface>()("@opencode/v2/Agent")` + `Layer.effect(Service, …)` + `export * as AgentV2` | L06 |
| 各 `packages/core/src/*.ts` | 普遍的 `Context.Service` / `Layer.effect` / `Effect.fn` 模式（277 处 Effect.fn） | L05, L06, L08 |
| `packages/core/src/session/runner/llm.ts` | `FiberSet.make/run/join/awaitEmpty/clear`、`Semaphore.makeUnsafe(1).withPermit`、`Effect.uninterruptibleMask`、`Cause.hasInterrupts` | L07 |
| `packages/core/src/session/run-coordinator.ts` | 按 session 排队（呼应 KeyedMutex） | L07, L08 |
