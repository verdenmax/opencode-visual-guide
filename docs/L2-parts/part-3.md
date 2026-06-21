# L2 · Part 3 — 客户端/服务器骨架 (Client/Server)

**课程：** L09–L13 ｜ **状态：** 已完成

## 职责

Part 3 讲清 opencode 的**对外骨架**：那个"拥有一切"的 server 长什么样、客户端怎么和它对话。它把一条主线讲透——**server 是一个建在类型化 HttpApi 上的 `(request) => Response` 纯函数**，由此自然长出四样东西：分门别类的路由、实时事件流、自动生成的 SDK、可热插拔的传输。读完这部分，读者就掌握了"所有客户端与大脑对话的总入口"。

## 覆盖范围

| 课 | 主题 | 一句话 |
| --- | --- | --- |
| L09 | server 总览 | 不是 Hono/Express，而是 Effect 的 HttpApi；对外是一个 webHandler `(request)=>Response`；21 个路由组；`OpenApi.fromApi`→SDK |
| L10 | 路由组与 handler | 组=声明契约(纯类型)、handler=接到 core(薄)、中间件=外圈横切关卡；21 组 + 20 handler + 9 中间件 |
| L11 | SSE 事件总线 | event 组 success=`text/event-stream`；handler 流水线：eager 监听→无界队列→按实例 filter→合并心跳→SSE 编码 |
| L12 | SDK 生成 | `OpenApi.fromApi(PublicApi)` 把类型读成规范 → generate 加料/格式化 → @hey-api 印 SDK；清洗+补丁 |
| L13 | 多客户端传输 | 接缝=`fetch`；真 fetch(网络) ╱ `createWorkerFetch`(进程内 RPC→worker→同一 app.fetch)；事件也走 RPC |

## 与相邻部分的关系

- **承接 Part 2**：server 表面整个建在 Effect 之上——HttpApi、handler 里的 `Effect.gen`、事件 handler 的 `Stream`、中间件的 `Effect.catchCause` 全是 Part 2 的机制在 server 层的应用。
- **支撑 Part 4+**：L10 说 handler "薄、把活转给 core"，Part 4 起就推门进入那个 core（会话、Agent 循环、工具）。L11 的事件总线是 Part 4 一切实时反馈的源头，下游消费在 L54。
- L13 的"零网络富 TUI"对应 L03 的请求生命周期、以及 Part 11（TUI）的整体架构。

## 核心心智模型

1. **server = 一个 `(request)=>Response` 纯函数**，建在类型化 HttpApi 上（L09）。
2. **声明与实现分离**：组声明契约、handler 干活、中间件成环（L10）。
3. **实时是推出来的**：SSE 把共享事件总线推成每客户端的实时流（L11）。
4. **类型即单一事实来源**：API 类型→规范→SDK，自动生成、永不漂移（L12）。
5. **传输与逻辑解耦**：换掉那个 `fetch`，同一 server+SDK 在网络/进程内间自由切换（L13）。
