# L3 · Part 3 细节要点 (Details)

## L09 server 总览

- opencode 的 server **不是 Hono/Express**，而是建在 `effect/unstable/httpapi` 的 **HttpApi** 上：先用类型声明整套 API 的"形状"（输入/输出/错误），编译器守契约，机器可据此生成 SDK。
- 对外其实就是**一个函数**：`HttpApiApp.webHandler().handler`，形态 `(request) => Response`。正因这么标准纯粹，既能架在 `NodeHttpServer` 上，也能塞进进程内 worker 直接调（L13 的根）。
- 整张 API 由 **21 个路由组**汇总而成（`routes/instance/httpapi/groups/`）；每个组是一个领域。
- `OpenApi.fromApi(PublicApi)`：API 自己描述自己 → OpenAPI 规范 → 自动生成 SDK，客户端类型永远和 server 对齐（L12 展开）。

## L10 路由组与 handler

- 每个 API 端点分两半：**组声明契约**（`groups/*.ts`，纯类型：name/params/query/payload/success/error），**handler 实现**（`handlers/*.ts`，调 core）。
- 端点用 `HttpApiEndpoint.get/post(name, path, {…}).annotateMerge(OpenApi.annotations(…))` 写成；`.add` 串成 `HttpApiGroup`，再 `.add` 进 `HttpApi.make`。
- **错误也是契约**：`error: [BadRequest, ApiNotFoundError]` 写进类型，SDK 据此类型已知。
- **21 个组的名字 = opencode 能力地图**；结构化声明让系统能自己回答"我有哪些能力"。
- handler 用 `HttpApiBuilder.group(InstanceHttpApi, "session", h => …).handle("list", list)` 认领；名字必须和组对齐，错一个编译报错。输入已被组的类型校验，**handler 应当很薄**；`handleRaw` 用于需手控 Response 的少数端点。
- **中间件**（`middleware/`，9 个）是外圈横切关卡（鉴权/路由/压缩/错误）；像洋葱，进出经同一批、方向相反。错误中间件"真相进日志、编号(ref)给客户端"，有类型的失败照常走正路。

## L11 SSE 事件总线

- opencode 用 **SSE**（一个永不结束的 HTTP GET）做服务器→客户端实时推送：比轮询省、比 WebSocket 轻，且自动复用既有 HTTP 骨架。
- `event` 组只有一个端点 `subscribe`，玄机在 `success` 的 `contentType: "text/event-stream"`——契约承诺的是一条流。
- handler（`handlers/event.ts`）流水线：**eager 登记监听**（`events.listen`）→ `Queue.unbounded` 蓄水 → `addFinalizer(unsubscribe)` → `Stream.fromQueue` 按 `directory`+`workspaceID` **filter** → merge 心跳/disposed → `Sse.encode()` 编码 → 流式写回。
- **提前登记监听**是关键正确性细节：堵住"开始响应"与"登记监听"之间的缝隙，订阅那刻起事件不丢。无界队列=宁可多占内存也不丢事件、不拖慢核心。
- **心跳每 10s** + 响应头 `Cache-Control: no-cache, no-transform`：防中间代理把连接当空闲掐断、防流被缓冲改写。生命周期事件：`server.connected`→…→`server.instance.disposed`(takeUntil 收尾)。

## L12 SDK 生成

- 核心一行：`OpenApi.fromApi(PublicApi)`（`server.ts` 的 `Server.openapi()`）——把 21 组的**类型当数据读**，吐出标准 OpenAPI 规范。只因 API 是结构化类型才可能；`/doc` 端点惰性计算（fromApi 非平凡）。
- `opencode generate`（`cli/cmd/generate.ts`）：给每个 operation 注入 **`x-codeSamples`**（JS 用法示例）+ 过 **prettier** 格式化（保证逐字节可复现、可入库）。
- `packages/sdk/js/script/build.ts`：`bun dev generate > openapi.json` → `createClient`（**@hey-api/openapi-ts**）按三插件产出 **types.gen / sdk.gen(OpencodeClient) / client.gen(fetch)**；`clean:true` 保证纯函数式产物。
- 端点名 → SDK 方法名，契约从 server **类型安全**贯通到客户端每次调用；**永不漂移**（两份副本→同一源头的两次投影）。
- 自动生成≠无人值守：输入侧 `stripOptionalNull`（剥 Effect→OpenAPI 的 `{type:null}` 翻译腔，`public.ts`），输出侧精准打补丁修 @hey-api 一个 SSE 类型 bug。

## L13 多客户端传输

- "同一 handler、两种传输"的接缝是 **`fetch`**：server 进出是 `Request/Response`，SDK 所有调用都经一个可配置 `fetch`。边界越窄(只剩进 Request 出 Response)、越标准(Web 标准)，可替换性越强。
- **传输 A（网络）**：填原生 `fetch` → HTTP/TCP → 端口 4096 → `NodeHttpServer` → webHandler。通用，有网络开销。
- **传输 B（进程内）**：`createWorkerFetch`（`cli/cmd/tui.ts`）对外断言成 `typeof fetch`，对内把 url/method/headers/body 经 RPC 发给 Worker；worker 的 `rpc.fetch`（`cli/tui/worker.ts`）重建 `Request` 后调 **`Server.Default().app.fetch`——就是 L09 那个 handler**，零网络。
- 分两线程：主线程渲染保持跟手，重活(模型/工具)进 worker；跨线程不能共享内存，故用**类型安全 RPC** 传消息。worker 还暴露 `server`(按需起网络 server，两传输可叠加)、`reload`、`snapshot` 等方法。
- **事件也走这条管道**：worker `GlobalBus.on("event", e => Rpc.emit("global.event", e))`，等价于网络端 SSE。整个 server 表面(端点+事件)在两传输下都完整可用——多端语义唯一。
