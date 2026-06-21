# L2 · Part 2 — Effect 函数式地基 (Effect Foundations)

**课程：** L05–L08 ｜ **状态：** 已完成

## 职责

Part 2 打的是 V2 的**函数式地基**。`packages/core` 满屏的 `Effect.gen`/`yield*`/`Layer` 不先弄懂，后面的会话引擎、上下文系统、LLM 层都读不下去。本部分**先讲动机、再讲机制、最后讲项目自建的工具**，让读者带着"为什么"去读后面的"怎么用"。

## 覆盖范围

| 课 | 主题 | 一句话 |
| --- | --- | --- |
| L05 | 为什么是 Effect | agent 缠着副作用/错误/并发/依赖四难题；Effect 把计算描述成值 `Effect<A,E,R>`，把 E/R 抬进类型 |
| L06 | Service 与 Layer | Service=能力插槽(契约/R)，Layer=接上实现；yield* 欠债、Layer 还债；makeRuntime+memoMap |
| L07 | 并发原语 | Fiber=可中断句柄；FiberSet 管一组；结构化并发"开多少收多少"；uninterruptibleMask/Semaphore |
| L08 | Effect 工具箱 | effect/ 自建件：Effect.fn(命名)、memoMap(去重)、KeyedMutex(按key排队)、serviceUse(省样板) |

## 与相邻部分的关系

- **承接 Part 1**：L04 说 V2 是"小协作者"，本部分揭示**正是 Effect 的依赖模型塑造了这种模块形状**。
- **支撑 Part 3–9**：server（Part 3）、agent 循环（Part 4）、Context Epoch（Part 5）、LLM 层（Part 6）全建在 Effect 之上；本部分是读懂它们的前提。
- L07 的 FiberSet 直接对应 L03/L18 的"并发跑工具"；L06 的 memoMap 对应 L08 的 `effect/memo-map.ts`。

## 核心心智模型

1. **Effect 是"先描述、再运行"的值**，E/R 进类型（L05）。
2. **Service 声明、Layer 提供**，换实现=换一层 Layer（L06）。
3. **结构化并发**：开了多少就能干净收回多少（L07）。
4. **工具箱固化高频正确做法**，让 core 读得顺、写不错（L08）。
