# L3 · Part 2 细节要点 (Details)

## L05 为什么是 Effect

- agent 核心逻辑天生缠着四难题：**副作用、错误、并发、依赖**，且四样同时来、互相放大。
- 普通 `async/await + try/catch` 把**错误类型（catch 到 unknown）和依赖（隐式 import）藏出了类型**，全靠脑子记。
- Effect 核心一招：**不立刻运行，先把计算描述成一个值**，可先组合(retry/race/注入)，最后在边缘 runPromise 一次。
- `Effect<A, E, R>`：A=成功值、**E=类型化错误（编译器逼你处理）**、**R=依赖（可注入替换）**。
- 给 V2 换来：类型化错误、依赖注入、结构化并发、资源安全——正对四难题。

## L06 Service 与 Layer

- **Service** = 带全局标签的接口（`Context.Service<Service,Interface>()("@opencode/v2/...")`），声明一个能力插槽（对应 R）。
- **Layer** = `Layer.effect(Service, make)`，把真实现接到槽上；make 本身是 Effect，构造时可依赖别的 Service。
- 消费 `yield* Service` → 在 R 欠下依赖；提供 Layer → 还清；编译器盯账本。
- 组合：`makeRuntime` + **memoMap 去重**（同一 Layer 全进程只造一份）。
- 测试=换一套假 Layer，业务代码一行不改；也是 V2"小协作者"形状的根源。

## L07 并发原语

- **Fiber** = 一个正在跑的 Effect 的句柄，可 `join`/`interrupt`（有序中断+清理）；普通 Promise 无法取消。
- **FiberSet**：`make`/`run`(并发)/`join`·`awaitEmpty`/`clear`(一键召回)，管一组动态任务。
- **结构化并发**：派生任务框在范围内，开多少收多少，不留野线程；这是正确性而非性能。
- 关键区用 `uninterruptibleMask`(原子) + `Semaphore`(互斥) 护住；默认可中断、关键处不可中断。
- 正是 agent 循环"并发跑工具、可干净中断"的实现（L18 细拆）。

## L08 Effect 工具箱

- `packages/core/src/effect/` 是 opencode 在 Effect 之上自建的工具箱。
- **Effect.fn("Domain.method")**：给 effect 命名（277 处），近乎零负担的可观测性；内部用 `fnUntraced`。
- **memoMap**（`Layer.makeMemoMapUnsafe()`，一行）：同一 Layer 全进程一份、实例一致。
- **KeyedMutex<Key>**：同 key 串行、异 key 并行（天然适配 session ID）。
- **serviceUse(tag)**：把"取服务+调方法"合一，省样板。这些是"护栏"，让正确成为默认。
