# L3 · Part 1 细节要点 (Details)

## L01 opencode 是什么

- opencode = **客户端/服务器**架构的开源 AI 编程 agent；一个常驻 server 掌管 agent 逻辑、会话、工具、provider、持久化，多个瘦客户端经生成的 SDK 通信。
- **agent 循环**：server 反复"调 LLM → 执行工具 → 喂回结果"，直到模型不再调工具。
- 多入口同一内核：`opencode`（TUI）/`serve`（headless）/`run`/`acp`/`mcp`（`src/index.ts` yargs 注册）。
- 技术栈：Bun + TypeScript + Effect + Drizzle/SQLite + SolidJS/opentui。
- 代码正从 V1 迁向 V2（引出 L04）。

## L02 项目全景地图

- ~24 个 package 分四组：**CORE**（opencode·core·llm·server·sdk·plugin）、**客户端/UI**（tui·cli·app·ui·desktop·web）、**云端/集成**（enterprise·function·slack·console·identity·containers·stats）、**基础库**（effect-drizzle-sqlite·effect-sqlite-node·http-recorder·script·storybook）。
- 依赖方向：客户端 → sdk → server → core(+llm) → provider。
- 反直觉点：`core` 是 V2（新），`opencode` 主二进制含 V1（旧）。
- turborepo（`turbo.json`）编排 typecheck/build/test；Bun workspaces。

## L03 一次对话的生命周期

- 11 跳：①按键 ②RPC worker 传输 ③Effect HttpApi server ④事件溯源收件箱 ⑤System Context ⑥建 LLM 请求 ⑦流式 provider ⑧工具调用(FiberSet 并发) ⑨工具执行(权限闸门) ⑩有界循环(MAX_STEPS=25) ⑪事件流回(16ms 批渲染)。
- **下行收敛、上行发散**：下行把意图收拢成一次 `llm.stream`，上行把每个状态变化广播成事件。
- 富 TUI 用**进程内 RPC worker**（`createWorkerFetch` 换掉 SDK 的 fetch），零网络、可逆（serve 模式走真 HTTP）。
- agent 循环 = 问一轮 → FiberSet 并发干一轮 → reload 投影历史再问。

## L04 V1 与 V2：架构迁移

- **看路径定身份**：`opencode/src/session`=V1，`core/src/session`=V2。
- 体量：V1 巨石（prompt.ts ~1704 / session.ts ~1119 / processor.ts ~1084）；V2 小协作者（runner/llm.ts ~404 等）。
- 四条分界线：AI-SDK vs 自研 llm；JSON 文件 vs Drizzle+SQLite；函数参数 vs 事件溯源；命令式 vs Effect。
- 迁移图的是可测试/可恢复/可并发/可扩展 + V2 独有的 Context Epoch。
- 迁移渐进、两套并存；本指南以 V2 为主线、关键处对照 V1。
