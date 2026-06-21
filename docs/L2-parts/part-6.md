# L2 · Part 6 — LLM 协议层 (LLM Protocol Layer)

**课程：** L28–L35 ｜ **状态：** 已完成

## 职责

Part 6 回答一个第四、五部分一直假定为「已解决」的问题：**core 说一种规范语言，外面的模型供应商各说各的方言，这道鸿沟怎么跨？** 它用一套**反腐层（anti-corruption layer）**给出答案：core 永远只说规范语（出 `LLMRequest`、回 `LLMEvent` 流），一层**协议适配器**把它翻成各家方言、再把回话翻回规范事件；适配器之外，还有**传输 / 分帧 / 端点 / 认证**这条真正搬运字节的传送带，以及把「模型名」解析成「一条配好的链路」的 **catalog + models.dev**。读完这部分，你就理解了 opencode「与十几家供应商打交道却不被任何一家绑架」的全部秘密，也补上了第 17 课 `llm.stream` 消费的那套 `LLMEvent` 的来历。

## 覆盖范围

| 课 | 主题 | 一句话 |
| --- | --- | --- |
| L28 | LLM 层总览 | 反腐层：core 说规范语、适配器砌翻译墙；协议(线缆格式,6 种)≠供应商(具体厂商,多对多)；OpenAI 兼容白嫖生态 |
| L29 | 协议适配器骨架 | 每个协议填同一张两栏表：body(请求侧 from 函数)+stream(响应侧状态机 step:(State,Event)→[State,LLMEvent[]])；Protocol.make 是恒等接缝 |
| L30 | Anthropic Messages 协议 | 一切皆「块」+ 顶层 system；4 个缓存断点预算(可变 Breakpoints 计数器穿过 lower*，超额悄悄丢，与 Bedrock 共享 utils/cache)；usage 两半合并 |
| L31 | OpenAI Chat/Responses 协议 | 一家两协议：Chat 扁平角色 vs Responses 带类型条目+推理一等公民(encrypted_content)；24 行 openai-compatible 整份复用 Chat 协议 |
| L32 | Gemini 与 Bedrock 协议 | Gemini 全面改名(contents/parts/model/thoughtSignature，思考三家三名)；Bedrock 同 Claude 方言、异 AWS 二进制传输→另起协议；套娃状态机(字节→帧→事件) |
| L33 | 路由与传输 | 一个 Route=四个正交件(protocol/endpoint/auth/framing)+id（源码原话「four orthogonal pieces」）；完整流水线；HTTP vs WebSocket(transport 是 framing 维的延伸)；framing 是字节流形状的缝、帧类型对它不透明 |
| L34 | 流式事件与缓存 | LLMEvent(16 成员，反腐层入站半边，补全翻译墙)；cache-policy 自动打 3 断点缓存稳定前缀(接通 L24 Context Epoch)；RESPECTS_INLINE_HINTS 跳过 OpenAI/Gemini |
| L35 | 模型解析与 Copilot | models.dev(外置社区模型大全，事实地基，cost 供 L34 算账)→catalog(模型名→配好的 Route，类型化错误)；Copilot 复用 OpenAI 协议、只换 endpoint+auth |

## 与相邻部分的关系

- **承接 Part 4/5**：Part 4 的 agent 循环（L17）那句 `llm.stream(request)` 消费的，正是本部分定义的规范 `LLMEvent` 流；Part 5 的 Context Epoch（L24）死守「基线前缀稳定」，其**真正目的**到本部分 L34 的 prompt 缓存才图穷匕见（稳定 = 可缓存 = 省钱）。
- **建在 Part 2 之上**：协议状态机、framing 缓冲、Route 组合都用 Effect 的 Schema/Stream/Codec；类型参数 `Frame` 在 framing↔protocol 接缝处强制对齐，是「类型即契约」的延续。
- **引出 Part 7**：本部分讲「LLM 是 agent 的嘴和脑」（怎么和模型对话）；下一部分工具系统讲「工具是 agent 的手」（模型决定要调的工具怎么定义、执行、隔离）。

## 核心心智模型

1. **反腐层一进一出**（L28/L34）：core 只认规范的 `LLMRequest`（出）和 `LLMEvent` 流（回）；一道翻译墙挡住所有供应商差异，墙内 agent 循环对供应商一无所知。
2. **协议即一张两栏表**（L29）：`body`（请求侧，一个 `from` 函数，一次成形）+ `stream`（响应侧，一台 `(State,Event)→[State,LLMEvent[]]` 状态机，边收边攒）。不对称映射现实：请求一次发出、响应流式到达。
3. **协议 ≠ 供应商**（L28/L31/L35）：6 种协议（线缆格式）复用覆盖十几家供应商；OpenAI 兼容 24 行、Copilot 只换 auth，都是「复用协议、只拧一两个旋钮」。
4. **四个正交件 + id**（L33）：源码 `Route.make` 注释明言「four orthogonal pieces」=`{protocol, endpoint, auth, framing}`，加一个 id，各自独立替换；transport 是 framing 维在非 HTTP 时的替换（二者只传其一）。前面所有「轻巧复用」本质都是「只换一两件」。
5. **差异交给适配层吸收，而非假装统一**（贯穿 L30–L35）：缓存机制各异（Anthropic/Bedrock 显式内联 vs OpenAI/Gemini 隐式 → cache-policy 整段跳过）、推理签名三家三名、模型事实外置给 models.dev——好抽象懂得在哪统一、在哪放手。
