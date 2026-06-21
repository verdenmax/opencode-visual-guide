# L4 · Part 6 源文件 → 课 对照 (API map)

opencode 源文件（`/home/verden/course/opencode`）→ Part 6 中讲到它的课。除注明外，均在 `packages/llm/src/`。

| opencode 源文件 / 符号 | 关键点 | 讲到它的课 |
| --- | --- | --- |
| `route/protocol.ts` | `Protocol<Body, Frame, Event, State>` = `{id, body:{schema, from}, stream:{event, initial, step, terminal?, onHalt?}}`；`body.from:(LLMRequest)→Effect<Body>`（请求侧一次成形）；`stream.step:(State,Event)→[State, LLMEvent[]]`（响应侧状态机）；**`Protocol.make = (input)=>input`**（恒等接缝）；`jsonEvent` | L29 |
| `route/client.ts` | `Route<Body, Prepared>` / `Route.make`（注释：**four orthogonal pieces** `protocol`/`endpoint`/`auth`/`framing` + `id`；常见写法 `{id,protocol,endpoint,auth,framing}` 走 HTTP，或以 `transport` 顶替 `framing` 走 WS — 两个重载）；`stream`/`prepare`；`.with(...)` 覆盖局部件；类型参数 `Frame` 锁 framing↔protocol | L28, L33, L35 |
| `route/framing.ts` | `Framing<Frame>{id, frame:(bytes Stream)→Frame Stream}`（「传输与协议之间、字节流形状的缝」，帧类型**不透明**）；`Framing.sse`（UTF-8+SSE 通道+丢空行/[DONE]，每帧 data: JSON） | L33, L32 |
| `route/transport/http.ts` · `websocket.ts` · `index.ts` | `HttpTransport.sseJson`（请求/响应）；`WebSocketTransport.jsonTransport`、`WebSocketConnection{sendText, messages 流}`（持久双向） | L33 |
| `route/endpoint.ts` · `auth.ts` · `auth-options.ts` | `Endpoint.path(...)`（打哪个 URL）；`AuthDef`（怎么签名/认证）——Route 的两个独立旋钮 | L33, L35 |
| `protocols/anthropic-messages.ts` | 块类型(text/image/tool_use/tool_result/server_tool_use/*_tool_result)；`system` 顶层字段；`ANTHROPIC_BREAKPOINT_CAP=4`、`cacheControl`(可变 `Breakpoints{remaining,dropped}`，超额 `dropped++` 返 undefined)；`EPHEMERAL_5M`/`EPHEMERAL_1H`；`mergeUsage`/`mapUsage`(input/output/cache_read/cache_creation→规范，思考不单列)；`mapFinishReason`("tool_use"→"tool-calls")；结尾 `Protocol.make` | L30 |
| `protocols/utils/cache.ts` | `Breakpoints{remaining,dropped}`、`newBreakpoints(cap)`、`ttlBucket(≥3600→"1h" else undefined)`——Anthropic 与 **Bedrock 共享**的 4 上限+TTL 逻辑 | L30, L32 |
| `protocols/openai-chat.ts` | 扁平角色联合 system/user/assistant(`tool_calls`)/tool(`tool_call_id`)；`delta`/`finish_reason` 流式；`HttpTransport.sseJson`；导出 `protocol` 供 compatible 复用 | L31 |
| `protocols/openai-responses.ts` | 带类型条目 input_text/output_text/`reasoning`(`encrypted_content`)/function_call/_output/`item_reference`；`store`；`reasoningItems` 折叠；**导出 `httpTransport` + `webSocketTransport`**（唯一支持 WS） | L31, L33 |
| `protocols/openai-compatible-chat.ts` | **≈24 行**：`Route.make({id, protocol: OpenAIChat.protocol, endpoint: Endpoint.path("/chat/completions"), framing: Framing.sse})`——整份复用 Chat 协议、只改 id+端点 | L31 |
| `protocols/gemini.ts` | `contents`/`{role,parts}`(role `"user"`/`"model"`)；`systemInstruction` 顶层；parts text/functionCall/functionResponse/inlineData；`thought`+`thoughtSignature`；`usageMetadata.thoughtsTokenCount`(单列)；`functionCallingConfig.mode` | L32 |
| `protocols/bedrock-converse.ts` | Converse API；块 text/toolUse/toolResult/`reasoningContent`(`signature`)；`system` 顶层块；`BedrockCache`(共享 utils/cache)；cacheReadInputTokens/cacheWriteInputTokens；流式 chunk 按 `:event-type`(messageStart/contentBlockDelta…) | L32 |
| `protocols/bedrock-event-stream.ts` | AWS 二进制事件流 framing：帧 `[length:4][headers-length:4][prelude-crc:4][headers][payload][crc:4]`；`@smithy/eventstream-codec` 校验+按 `:event-type` 重组；`FrameBufferState{buffer,offset}`、`appendChunk`(压缩+有界内存)、`consumeFrames`(零拷贝 subarray) | L32 |
| `protocols/index.ts` | 6 协议清单：AnthropicMessages / BedrockConverse / Gemini / OpenAIChat / OpenAICompatibleChat / OpenAIResponses | L28 |
| `schema/events.ts` | **`LLMEvent`（16 成员标签联合）**：step-start/finish、text/reasoning/tool-input 各 start-delta-end、tool-call、tool-result、tool-error、finish、provider-error；`Usage`(inputTokens/outputTokens/cacheRead/cacheWrite) | L34, L28 |
| `schema/messages.ts` | `LLMRequest`(model/messages/system/tools/cache…)、`Message`、`ToolDefinition`、`ContentPart`、`CacheHint` | L28, L34 |
| `cache-policy.ts` | `applyCachePolicy(request)`：首句查 `RESPECTS_INLINE_HINTS={anthropic-messages,bedrock-converse}`(非则原样返回)；`AUTO={tools,system,messages:"latest-user-message"}`；`markLastTool`/`markLastSystem`/`markMessages`/`markMessageAt`(slice+下标，非 .map())；只填留白；写 1.25x/读 0.1x 注释 | L34 |
| `llm.ts` | 导出 `stream` / `generate` / `request`——上层（L17 agent 循环）入口 | L28, L34 |
| `core/src/models-dev.ts` | `Model` schema(id/name/family/release_date/能力/`cost`(cache_read/cache_write)/`limit`/`modalities`/status)、`Provider`(models)；HTTP 拉取；`Event` `models-dev.refreshed` | L35 |
| `core/src/github-copilot/copilot-provider.ts` | （旁注）基于 Vercel AI-SDK 的 Copilot provider：`createOpenaiCompatible`/`LanguageModelV3`，与 `llm` 包的 Route 体系不同，不展示六件式 | L35 |
| `core/src/catalog.ts` | `Catalog`(CatalogV2)：`providers: Map<ProviderID, ProviderRecord{provider, models: Map<ModelID, ModelInfo>}>`、`defaultModel`；`ProviderNotFoundError` / `ModelNotFoundError`(类型化错误)；`Editor` | L35 |
| `packages/llm/src/providers/github-copilot.ts` | **L35 六件式演示的真正出处**：import `OpenAIChat`/`OpenAIResponses`，复用 `OpenAIChat.route`/`OpenAIResponses.route`，`.with({ endpoint:{baseURL}, auth: AuthOptions.bearer(options,[]) })` 只覆盖 endpoint+auth；`shouldUseResponsesApi`、`routes`、`configure` | L35 |
| `CONTEXT.md`（repo 根） | Safe Provider-Turn Boundary（与 L24/L34 缓存前缀稳定相关的注入时序概念） | L34（呼应 L24） |
