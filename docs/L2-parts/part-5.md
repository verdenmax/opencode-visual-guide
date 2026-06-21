# L2 · Part 5 — 上下文纪元系统 (Context Epoch)

**课程：** L21–L27 ｜ **状态：** 已完成

## 职责

Part 5 回答一个第四部分一直含糊带过的核心问题：**模型每轮该看到怎样一份「世界」？** 它把「系统上下文」（目录、日期、git、指令这类环境底色）做成一套**可组合、可增量、可持久、可演进**的「源 + 纪元」系统。这套系统和会话引擎**共享同一条事件时间线**：基线钉进会话序号、更新作为原位事件、换 agent 走原子替换。读完这部分，你就理解了 opencode「让模型恰到好处地了解它所处的世界」全过程，也补上了第 19 课 `baselineSeq` 那个悬了多课的伏笔。

## 覆盖范围

| 课 | 主题 | 一句话 |
| --- | --- | --- |
| L21 | System Context 总览 | 系统上下文=可组合/带类型/独立刷新的 Source；make 藏类型+combine 组合（代数）；baseline/update 省 token；unavailable≠removed |
| L22 | Context Source | 单源一生：codec 派生 encode/decode/equivalent（声明结构判等自来）；baseline=一说一记；compare=Unchanged/Updated/Incompatible |
| L23 | System Context Registry | 注册表收集源：register（acquireRelease 作用域绑定、自动注销）+ load（按 key 排序求稳、并发观察求快、combine） |
| L24 | Context Epoch | 把基线钉成会话里带 baseline_seq 的锚点（合上第 19 课）；prepare 每次运行对表：initialize/reconcile(Updated 发 ContextUpdated 事件)/replace |
| L25 | 会话中系统消息 | ContextUpdated 投影成原位 System 消息（和 Text/Tool 同一流水线）；位置即时机即意义；可重放环境史 |
| L26 | 内置 Context Sources | core/environment(<env> 目录/根/git/平台)、core/date(连日期都是源,跨午夜)、InstructionContext；~5 行定义=好抽象试金石 |
| L27 | Agent 切换与 Epoch 替换 | 换 agent 走 replace(从零重建基线)；源不齐则 ReplacementBlocked(unavailable≠removed 终极兑现)；fence+revision 保原子一致 |

## 与相邻部分的关系

- **承接 Part 2/4**：源框架建在 Effect 之上（Service/Layer/Scope/acquireRelease/Ref）；纪元的「先持久再推进」「原子 commit」「版本守护」都是 Part 4 事件溯源纪律的延续。
- **合上 Part 4 第 19 课**：`baselineSeq` 是 `history.load` 给历史窗口裁边那条线——本部分（L24）正是它的来源。
- **引出 Part 6**：这套系统决定「模型该读什么世界」；下一部分 LLM 协议层决定「这份世界与对话，怎么翻译成各供应商的方言发出去」。

## 核心心智模型

1. **上下文即一组可独立刷新的源**（L21），每个源 codec 一肩三挑、baseline/update 省 token（L22）。
2. **注册表编排而不生产**：作用域绑定收集、按 key 定序、并发观察（L23）。
3. **纪元=快照+锚点**：钉进会话序号 baselineSeq，与历史窗口咬合（L24）。
4. **上下文更新也是事件**：原位 System 消息，位置承载时机（L25）。
5. **抽象的回报是源极简**（L26）；**根基性变更要么完整、要么不动**（L27）。
