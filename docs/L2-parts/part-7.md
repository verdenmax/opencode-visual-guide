# L2 · Part 7 — 工具系统 (Tool System)

**课程：** L36–L43 ｜ **状态：** 已完成

## 职责

Part 7 回答一个第六部分（LLM 是「脑」）之后必然要问的问题：**模型决定了「要调某个工具」，这个工具到底是怎么定义、收集、执行、被管住的？** 它把「agent 的手」做成一套**统一、可控、可扩展**的工具体系：每个工具都填同一张 `Tool.make` 的 Config 表（schema 在三处把关）；注册表用作用域绑定收集、按权限物化成模型可见的清单；文件/搜索/执行/网络各类具体工具是这张表的不同填法；权限系统（allow/deny/ask）给每个动作装上边界；有界输出（截断+外溢）护住模型稀缺的上下文；Skills 把成套本领打包、两段式按需加载。读完这部分，你就理解了 opencode「让一颗 LLM 真正动手改变世界，又始终可控」的全过程。

## 覆盖范围

| 课 | 主题 | 一句话 |
| --- | --- | --- |
| L36 | 工具定义 | `Tool.make(config)`={description,input,output,execute,toModelOutput?}；schema 一肩三役(给模型 JSON/解码入/编码出)；返回冻结空对象、runtime 在 WeakMap(能力凭证)；settle=decode→execute→encode→{structured,content} |
| L37 | 工具注册表 | register(作用域绑定·同名叠摞·addFinalizer 按 token 撤销·uninterruptible)；materialize(快照+权限滤 whollyDisabled→{definitions,settle})；settle 验 identity 防 Stale tool call；builtins.locationLayer |
| L38 | 文件工具 | read/write/edit/apply_patch 覆盖改动光谱；edit 护栏(精确匹配/歧义拒绝/行尾归一/writeIfUnchanged 乐观并发 compare-and-swap)；路径相对 Location，外部需 external_directory |
| L39 | 搜索与执行工具 | glob(按名)/grep(按内容)架 Ripgrep(尊重 .gitignore)+limit；bash 全权限逃生舱：限时(2/10分)/限量(1MB)/双许可/detached+forceKill/stdin ignore；**bash≠PTY**(AppProcess/spawn 批处理 vs pty 交互式) |
| L40 | 其他内置工具 | 两条新轴：向外(webfetch 默认转 markdown / websearch 本地 Exa/Parallel、注入当前年份)、转内(question 反向工具从用户拉答案 / todowrite 作用于 agent 自身状态 SessionTodo) |
| L41 | 权限系统 | allow/deny/ask 三态规则引擎；evaluate=findLast 通配(后匹配胜)+默认 ask(安全默认)；once/always/reject(always→持久化 project 作用域规则)；两级把关(deny=菜单层/ask=调用层)；CorrectedError 反馈回模型 |
| L42 | 有界工具输出 | ToolOutputStore：上下文稀缺→限 2000行/50KB(可配)；preview 掐头去尾(head+tail，非只 head)；全文 spill 到托管文件 tool-output/、outputPaths 交模型、read 回取；7天清理；bash 1MB(内存) vs 本课(上下文) |
| L43 | Skills 系统 | 两段式：名字半经 Context Source(M5)常驻、正文半经权限化 skill 工具按需(渐进式披露)；skill 只发讲义不干活(执行靠通用工具)；M5+M7 交汇点(用全 Tool.make/注册表/权限/read)；可发现/下载 |

## 与相邻部分的关系

- **承接 Part 6/Part 4**：M6 的 LLM 是 agent 的「脑」（怎么和模型对话）、第 17 课 agent 循环消费模型吐出的 `tool-call` 事件——而那些工具调用，正由本部分定义、注册、执行。L37 的 settle 把工具失败收成值、把输出有界化，正好回到第 17 课循环里。
- **建在 Part 2/M5 之上**：工具系统重度使用 Effect（Service/Layer/Scope/acquireRelease/WeakMap/uninterruptible/Deferred）；L43 Skills 的「名字半」直接复用 M5 的 System Context（Context Source）。
- **引出 Part 8**：本部分把「手」（工具）讲透；下一部分讲**配置、Agents 与 Provider**——一个具体 agent 怎么被配置出来、配上哪组工具与哪个模型、怎么跑起来。

## 核心心智模型

1. **一个工具 = 填一张统一的 Config 表**（L36），schema 在三处把关；正因所有工具同形，它们才能互相衔接、彼此兜底（L42 用 read 回取 spill 全文）。
2. **「先廉价广而告之，再昂贵按需兑现」**（L37 definitions/settle、L42 预览/spill、L43 名字/正文）——同一个渐进式披露套路在三处现身。
3. **能力 × 边界**：工具给「能做什么」（L36-40、L43），权限给「准做什么」（L41 allow/deny/ask、默认问），有界输出给「结果怎么安全回模型」（L42）——三者合起来才是可控的 agent。
4. **凡可能量大处皆有界**（贯穿 L38-42）：read offset/limit、搜索 limit、bash timeout/字节、ToolOutputStore 行/字节——稀缺的是模型上下文与内存。
5. **为不同交互模型选不同机制，不强求统一**（L39 批处理 bash vs 交互式 pty；L40 本地 vs 供应商搜索）——好抽象懂得在哪统一、在哪放手。
