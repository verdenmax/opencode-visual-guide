# L4 · Part 1 源文件 → 课 对照 (API map)

opencode 源文件（位于 `/home/verden/course/opencode`）→ Part 1 中讲到它的课。

| opencode 源文件 / 符号 | 关键点 | 讲到它的课 |
| --- | --- | --- |
| `packages/opencode/src/index.ts` | yargs CLI 入口，注册 tui/serve/run/acp/mcp… 多命令 | L01 |
| `packages/opencode/package.json` | 依赖揭示技术栈（effect/drizzle/ai-sdk/opentui/workspace 包） | L01, L02 |
| `turbo.json` | turborepo 任务编排（typecheck/build/test） | L02 |
| `packages/*`（24 个包） | monorepo 包地图与依赖方向 | L02 |
| `packages/opencode/src/cli/cmd/tui.ts` | `createWorkerFetch`：把 SDK fetch 换成 RPC worker | L03 |
| `packages/opencode/src/cli/tui/worker.ts` | `Server.listen` + `GlobalBus.on("event")→Rpc.emit` 桥接 | L03 |
| `packages/opencode/src/server/server.ts` | Effect `HttpApi`+`OpenApi`+`NodeHttpServer`（非 Hono） | L03 |
| `packages/core/src/session/input.ts` | 事件溯源输入收件箱 | L03, L04 |
| `packages/core/src/session/run-coordinator.ts` | run/wake/interrupt 协调 | L03, L04 |
| `packages/core/src/session/runner/llm.ts` | V2 agent 循环；`MAX_STEPS=25`；FiberSet 并发 | L03, L04 |
| `packages/core/src/system-context/index.ts` | 基线 System Context 组装（第 5 部分展开） | L03 |
| `packages/llm/src/route/client.ts` | `stream()`→协议适配器，返回 `Stream.Stream<LLMEvent,LLMError>` | L03 |
| `packages/core/src/tool/registry.ts` | ToolRegistry 执行内置工具 | L03 |
| `packages/opencode/src/server/routes/instance/httpapi/groups/event.ts` | SSE 事件组（事件流回客户端） | L03 |
| `packages/tui/src/context/sdk.tsx` | 订阅 `sdk.global.event`，~16ms 批渲染 | L03 |
| `packages/opencode/src/session/{prompt,session,processor}.ts` | V1 巨石（~1704/1119/1084 LOC，AI-SDK） | L04 |
| `packages/opencode/src/storage/storage.ts` | V1 文件/JSON 存储 | L04 |
| `packages/core/src/database/` | V2 Drizzle+SQLite（双后端 bun/node） | L04 |
