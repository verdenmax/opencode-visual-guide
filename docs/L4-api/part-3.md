# L4 · Part 3 源文件 → 课 对照 (API map)

opencode 源文件（`/home/verden/course/opencode`）→ Part 3 中讲到它的课。

| opencode 源文件 / 符号 | 关键点 | 讲到它的课 |
| --- | --- | --- |
| `packages/opencode/src/server/server.ts` | `HttpApiApp.webHandler().handler`（`(request)=>Response`）；`Server.openapi()` = `OpenApi.fromApi(PublicApi)`；`Server.Default().app.fetch` | L09, L12, L13 |
| `packages/opencode/src/server/routes/instance/httpapi/groups/` | **21 个路由组**目录（能力地图） | L09, L10 |
| `…/httpapi/api.ts` | 把各组用 `.addHttpApi(...)` 汇总成 `InstanceHttpApi` / `RootHttpApi` / `OpenCodeHttpApi` | L09 |
| `…/httpapi/groups/session.ts` | `HttpApi.make("session").add(HttpApiGroup.make(…).add(HttpApiEndpoint.get("list", …, {query,success,error}).annotateMerge(…)))` | L10 |
| `…/httpapi/groups/event.ts` | 单端点 `subscribe`，`success: Schema.String.pipe(HttpApiSchema.asText({contentType:"text/event-stream"}))` | L11 |
| `…/httpapi/handlers/` | **20 个 handler 文件**（实现各组端点） | L10 |
| `…/httpapi/handlers/session.ts` | `HttpApiBuilder.group(InstanceHttpApi, "session", h => Effect.gen(…))`；`.handle("list", list)` / `.handleRaw("create", …)` | L10 |
| `…/httpapi/handlers/event.ts` | `events.listen` + `Queue.unbounded` + `addFinalizer` + `Stream.fromQueue/filter/merge` + `Sse.encode()` + 心跳 + `GlobalBus.on` | L11 |
| `…/httpapi/middleware/` | **9 个中间件**（authorization, compression, cors-vary, error, fence, instance-context, proxy, schema-error, workspace-routing） | L10 |
| `…/httpapi/middleware/error.ts` | `HttpRouter.middleware` + `Effect.catchCause`：只兜底 defect 裸崩溃→带 `ref` 的 500，有类型失败放行 | L10 |
| `…/httpapi/public.ts` | `PublicApi = OpenCodeHttpApi.annotateMerge(OpenApi.annotations({title,version,transform:matchLegacyOpenApi}))`；`OpenApi.fromApi`；`stripOptionalNull`（清洗 `{type:null}`） | L09, L12 |
| `packages/opencode/src/cli/cmd/generate.ts` | `Server.openapi()` → 注入 `x-codeSamples` → prettier 格式化 → 写 stdout | L12 |
| `packages/sdk/js/script/build.ts` | `bun dev generate > openapi.json` → `createClient({input, output, plugins:[@hey-api/typescript, @hey-api/sdk(OpencodeClient), @hey-api/client-fetch]})` + 末尾打补丁 | L12 |
| `packages/sdk/js/src/v2/gen/{types,sdk,client}.gen.ts` | 生成产物（入库）：类型、`OpencodeClient` 方法、fetch 客户端 | L12 |
| `packages/opencode/src/cli/cmd/tui.ts` | `createWorkerFetch(client): typeof fetch`（内部 `client.call("fetch", …)`）；`new Worker(file)`；`Rpc.client<typeof rpc>(worker)`；`fetch: createWorkerFetch(client)` vs `fetch: transport.fetch` | L13 |
| `packages/opencode/src/cli/tui/worker.ts` | `rpc.fetch` → `Server.Default().app.fetch(request)`；`GlobalBus.on("event", e => Rpc.emit("global.event", e))`；`rpc.{server,reload,snapshot,checkUpgrade}` | L13 |
| `packages/opencode/src/util/rpc.ts` | `Rpc.client` / `Rpc.emit`：跨 Worker 线程的类型安全 RPC | L13 |
