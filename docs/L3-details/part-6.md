# L3 · Part 6 细节要点 (Details)

## L28 LLM 层总览

- **反腐层（anti-corruption layer）**：core 与外部供应商之间砌一道翻译墙。core 永远说**规范语**——出去 `LLMRequest`、回来 `LLMEvent` 流；适配器把它翻成各家方言、把回话翻回规范事件。墙内 agent 循环（L17 的 `llm.stream`）对供应商一无所知。
- **协议（protocol）≠ 供应商（provider）**：协议 = 线缆格式（请求/响应具体长啥样，**6 种**）；供应商 = 具体厂商（用哪种协议 + 认证 + 端点）。二者**多对多**：一种协议被多家用、一家也可能支持两套协议。
- **OpenAI 兼容的杠杆**：「OpenAI 兼容」已是事实标准，实现一次就免费搭上整个生态（OpenRouter/xAI/本地模型…），新厂商无需加代码。
- **LLM 包独立于 core**（`packages/llm`）：6 协议（AnthropicMessages/BedrockConverse/Gemini/OpenAIChat/OpenAICompatibleChat/OpenAIResponses）、众多 provider。

## L29 协议适配器骨架

- **`Protocol<Body, Frame, Event, State>`**（`route/protocol.ts`）只有两块：`body`（请求侧）+ `stream`（响应侧）。四个类型参数逼每个协议明确回答：请求体长啥样、一帧原始数据是啥、解码后一个事件啥结构、解析器攒什么状态。
- **`body`（出去）**：`{schema: Codec<Body>, from: (LLMRequest)→Effect<Body>}`。`from` 是「出境翻译」的全部——一个函数，一次成形（请求是静态的）。
- **`stream`（回来）= 状态机**：`{event: Codec<Event,Frame>, initial:(LLMRequest)→State, step:(State,Event)→[State, LLMEvent[]], terminal?, onHalt?}`。`step` 是灵魂：碎片进、累积进 State、攒齐才吐完整 LLMEvent。
- **不对称映射现实**：请求一次发出（函数够用），响应流式到达（工具参数跨帧到齐，必须状态机边收边攒）。
- **`Protocol.make` = 恒等函数** `(input)=>input`：纯「类型化接缝」，为未来横切关注点（tracing 等）预留统一入口；schema 和解析函数才是真理之源。

## L30 Anthropic Messages 协议

- **一切皆「块」**：内容拆成带 `type` 的结构化块——text/image/tool_use/tool_result/server_tool_use/服务端工具结果（web_search/code_execution/web_fetch，**整块到达、无流式增量、无客户端 tool_result 往返**）。`system` 是**请求体顶层独立字段**（文本块数组），区别于 OpenAI 当首条消息。
- **4 个缓存断点预算**：Anthropic 每请求最多 4 个 `cache_control` 断点（跨 tools/system/messages 合计），第 5 个 → 400。`cacheControl` 带一个可变 `Breakpoints{remaining, dropped}` 穿过所有 `lower*`：每打一个 `remaining--`，超额 `dropped++` 并返回 `undefined`（悄悄丢、不报错）。消耗次序 tools→system→messages（越前缀越优先）。
- **TTL 两档**：`ttlBucket` 把 ≥3600s → `"1h"`，否则默认 5m。这套逻辑抽到 `protocols/utils/cache.ts` 与 **Bedrock 共享**（同一供应商约束）。
- **可变计数器是刻意的本地、单趟手法**，区别于 stream 状态机的显式传状态。
- **stream**：message_start / content_block_start / content_block_delta(text_delta、input_json_delta) / content_block_stop / message_delta(stop_reason+最终 usage) / message_stop。`mergeUsage` 合并 message_start(输入)+message_delta(输出) 两半 usage；`mapUsage` 把 input_tokens/output_tokens/cache_read_input_tokens/cache_creation_input_tokens → 规范 inputTokens/outputTokens/cacheRead/cacheWrite；**思考 token 不单列**（算进 output，reasoningTokens 留 undefined）；stop_reason "tool_use"→"tool-calls"。

## L31 OpenAI Chat/Responses 协议

- **一家两协议**：`openai-chat.ts`（老牌 `/chat/completions`，事实标准）+ `openai-responses.ts`（新锐 `/responses`）。反映 OpenAI API 新老迁移，opencode 两边都填。
- **Chat = 扁平角色联合**：system（content 字符串）/ user / assistant（tool_calls: [{type:function, function:{name,arguments}}]）/ tool（tool_call_id）。流式 `choices[].delta` 推 content/tool_calls 片段 + `finish_reason`。
- **Responses = 带类型条目 + 推理一等公民**：input_text/input_image/output_text/reasoning/function_call/function_call_output/item_reference。`reasoning` 条目带 `encrypted_content`（加密思维链，原样回传即续上）；`store`（存服务端）+ `item_reference`（按 id 引用，无需重发）；流式基于条目事件，State 用 `reasoningItems` 折叠多段推理。
- **24 行的复利**：`openai-compatible-chat.ts` ≈ 24 行，`Route.make({id, protocol: OpenAIChat.protocol, endpoint: "/chat/completions", framing: Framing.sse})`——**整份复用 Chat 协议**，只覆盖 route id + 端点。一大票「OpenAI 兼容」厂商免费接入。
- **Route 与 Protocol 正交**：换供应商常常只是「换端点、复用 protocol」。「Chat 不够先进反而无处不在」（越朴素越好模仿）。

## L32 Gemini 与 Bedrock 协议

- **Gemini（`gemini.ts`）全面改名**：顶层 `contents`，每条 `{role, parts}`，role 只有 `"user"`/`"model"`（**无 assistant**）；system 进顶层 `systemInstruction`；parts = text/functionCall/functionResponse/inlineData；`thought`+`thoughtSignature`；usage `thoughtsTokenCount`（**思考 token 单列**，与 Anthropic 相反）；toolChoice `functionCallingConfig.mode` AUTO/NONE/ANY。
- **「信任上轮推理」三家三名**：Anthropic `signature`（密码学签名）/ OpenAI Responses `encrypted_content`（加密托管）/ Gemini `thoughtSignature`（思考签名）。
- **Bedrock（`bedrock-converse.ts`）= 同 Claude 方言、异传输**：转售 Claude，用 AWS Converse API；块 text/toolUse/toolResult/reasoningContent(signature)，system 顶层块数组，共享 `utils/bedrock-cache` 的 4 断点。**方言≈Anthropic，但传输用 AWS 二进制事件流，故必须另起协议。**
- **二进制帧结构**（`bedrock-event-stream.ts`）：`[length:4][headers-length:4][prelude-crc:4][headers][payload][crc:4]`；借 `@smithy/eventstream-codec` 校验 CRC、按 `:event-type` 头重组 JSON。framing 是 Route 里与 protocol 正交的零件。
- **套娃状态机**：`FrameBufferState{buffer, offset}` 把字节攒成帧——`appendChunk` 接新 chunk 时**压缩**丢弃 offset 前已消费字节（有界内存：最多比活跃窗口多一个 chunk），读取用**零拷贝 subarray**；`consumeFrames` 够一帧切一帧。字节→帧（framing）与帧→事件（protocol.stream）两台 `(state,input)→[state,out]` 状态机叠在一起。

## L33 路由与传输

- **协议不碰网络**：protocol 只管语言层（body.from 编码 / stream 解码）；真正搬字节的是传输基础设施。两段以「请求体」「帧」为抽象接口对接。
- **完整流水线（`Route.stream`）**：①protocol.body.from 编码 → ②endpoint 寻址 → ③auth 签名 → ④transport 取字节流 → ⑤framing 切帧 → ⑥protocol.stream 解码成 LLMEvent。
- **两种 transport**（`route/transport/`）：HTTP（请求/响应，绝大多数）；WebSocket（持久双向，`WebSocketConnection{sendText, messages 流}`）。**唯 OpenAI Responses 同时支持两者**（`openai-responses.ts` 导出 httpTransport + webSocketTransport；请求体 HTTP/WS 共享形状，HTTP 加 `stream:true`、WS 加 `type:"response.create"`）。
- **framing = 字节流形状的缝**（`route/framing.ts`）：`Framing<Frame>{id, frame:(bytes Stream)→Frame Stream}`。`Framing.sse`（UTF-8 解码 + SSE 通道解码 + 丢空行/[DONE]，每帧是一个 data: JSON）/ AWS 二进制。**帧类型对这一层不透明**，故同一种 framing 被任意协议复用（SSE 同时服务 Anthropic/Gemini/OpenAI）。
- **四个正交件 + id**：源码注释明言 Route 由「four orthogonal pieces」`{protocol, endpoint, auth, framing}` 加 id 拼成。常见 HTTP 写法 `Route.make({id, protocol, endpoint, auth, framing})`（Route 据 framing 自动建 HttpTransport）；走 WS 时以 `transport` 顶替 `framing`（`make` 两个重载，二者传其一）。类型参数 `Frame` 强制 framing（产 `Framing<Frame>`）↔ protocol（`stream.event: Codec<Event,Frame>`）对齐——正交但不放任。

## L34 流式事件与缓存

- **`LLMEvent`（`schema/events.ts`，16 成员）= 反腐层入站规范词汇**：step-start / step-finish；text-start/-delta/-end；reasoning-start/-delta/-end；tool-input-start/-delta/-end；tool-call；tool-result；tool-error；finish（带 Usage）；provider-error。会「一点点来」的内容都拆成 start→delta…→end 三段式（L29 状态机吐出形态）。六种协议 stream.step 全翻译成它，agent 循环（L17）只消费它——补全 L28「翻译墙」入站半边。
- **`cache-policy.ts` 的 "auto" 打 3 断点**：`markLastTool`（最后工具定义）+ `markLastSystem`（最后系统提示）+ `markMessages`（"latest-user-message"，最新用户消息）。缓存「整回合不变的稳定前缀」。
- **接通 L24 Context Epoch**：断点打在「最新用户消息」边界，使回合内每次 assistant↔tool 往返（L17）都命中同一缓存前缀；这正是 Context Epoch 死守「基线前缀稳定」的真正目的。
- **缓存默认开**（`undefined→"auto"`）：Anthropic 5m 缓存写 1.25x、读 0.1x，5 分钟内复用一次即回本（1.25+0.1<2），工具回合复用多次稳赚。
- **`RESPECTS_INLINE_HINTS = {anthropic-messages, bedrock-converse}`**：只有这俩认内联标记；OpenAI（隐式前缀缓存）、Gemini（隐式 + 带外 CachedContent）`applyCachePolicy` 第一句即整段跳过、原样返回。承认各家缓存哲学差异。
- **热路径细节**：`markMessageAt` 故意不用 `.map()` 而用 `slice + 下标赋值`（长对话每次请求都跑、`.map()` 的闭包派发与整组复制在 profiling 里冒头）。只填调用方留白、不覆盖手工标记。
- **职责分层**：cache-policy 决定「打哪」（战略，编码前跑）、protocol 的断点预算（L30）执行「打上且不超 4 个」（战术）。

## L35 模型解析与 Copilot

- **models.dev = 外置社区模型目录**（`core/src/models-dev.ts`，HTTP 拉取、缓存、发 `models-dev.refreshed` 事件）。`Model` schema：id/name/family/release_date、能力 attachment/reasoning/temperature/tool_call、`cost`（输入/输出/cache_read/cache_write 单价，**L34 算账数据源**）、`limit`（context/input/output 上限）、`modalities`（text/audio/image/video/pdf）、status（alpha/beta/deprecated）。把易变事实挡在代码外，新模型常零改动即识别。
- **catalog（`core/src/catalog.ts` CatalogV2）= 解析器**：`providers: Map<ProviderID, ProviderRecord{provider, models: Map<ModelID, ModelInfo>}>`，`defaultModel`。模型名经两次字典查找 → `ModelInfo`（含走哪条 Route）；查不到给**类型化错误** `ProviderNotFoundError` / `ModelNotFoundError`（分清「供应商没找到」vs「供应商有但模型没找到」）。
- **解析全链路**：模型名 → 拆 providerID+modelID → catalog 查 ModelInfo → L33 的积木式 Route → 可发起 stream。
- **Copilot = 积木式架构终极演示**（`packages/llm/src/providers/github-copilot.ts`）：import `OpenAIChat` + `OpenAIResponses`，**直接复用它们的 `.route`**（零重写）；用 `.with({ endpoint: {baseURL}, auth: AuthOptions.bearer(...) })` 只覆盖 `endpoint`（Copilot baseURL）+ `auth`（bearer token，由 GitHub OAuth 换取）。`shouldUseResponsesApi`(gpt-5+→Responses)。注：`core/src/github-copilot/copilot-provider.ts` 是另一套基于 Vercel AI-SDK 的 provider（`LanguageModelV3`），不展示 Route 六件式。
- **差异是配置、不是分支**：Copilot 与 OpenAI 的不同收敛成「换 headers + baseURL」配置，而非协议里的 `if(isCopilot)`。`provider.chat`/`provider.responses` 直指 OpenAI 兼容实现。令牌交换 = 最小权限 + 短时效凭证的安全惯例，整个封装进 auth 旋钮、不惊动协议层。
