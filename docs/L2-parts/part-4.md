# L2 · Part 4 — Session 核心与 agent 循环 (Session Core)

**课程：** L14–L20 ｜ **状态：** 已完成

## 职责

Part 4 是全书**第一个核心引擎舱**：一个 prompt 进来后，怎么一步步变成回答。它把整条主链——**数据模型 → 入账 → 调度 → 循环 → 工具 → 投影 → 护栏**——逐块拆开，每块用一个朴素而硬核的机制守住一条不变量。读完这部分，你就理解了 opencode「让模型自驱地、安全地、可恢复地完成任务」这件极难的事，到底是怎么办到的。

## 覆盖范围

| 课 | 主题 | 一句话 |
| --- | --- | --- |
| L14 | Session、消息与 part | 三层嵌套数据模型：Session(可分叉/账单/location) ⊃ Message(8 种标签联合) ⊃ Part(text/reasoning/tool)；tool 内含 ToolState 4 态机 |
| L15 | 事件溯源输入收件箱 | admit 把 prompt 发布成不可变事件（admitted_seq）落进 session_input，再 advisory wake；幂等/崩不丢/并发不抢；steer vs queue |
| L16 | 运行协调器 | 按会话 key 串行排空、跨会话并发（KeyedMutex 精装版）；run(发车/并入) vs wake(摇铃/合并)；coalesce；idle→draining 状态机 |
| L17 | V2 agent 循环 | while(activity){for(step<25){runTurn}}；一轮一次 llm.stream；逐事件增量落盘；工具先记账再动手、FiberSet 并发等齐；每轮重读投影历史 |
| L18 | 工具调用与 FiberSet | materialize 按权限亮 definitions + settle 执行；FiberSet(run/await/clear) vs Promise.all；uninterruptibleMask+restore；ToolOutputStore 大输出落盘 |
| L19 | 投影历史 | 事件(底账,写)→投影器→消息/部件表(报表,读)→history.load；CQRS 读模型；窗口由 compaction + 上下文纪元基线裁边 |
| L20 | 有界步数与错误处理 | 三道护栏：MAX_STEPS=25→StepLimitExceededError；RunError 联合(错误即值)；干净喊停(FiberSet.clear+failUnsettledTools)，工具终态不变量 |

## 与相邻部分的关系

- **承接 Part 2/3**：循环全建在 Effect 之上（Service/Layer、FiberSet、uninterruptibleMask 来自 Part 2）；协调器应答的 wake、循环喂的 SDK，根在 Part 3 的 server 与传输。
- **引出 Part 5**：L19/L20 反复点到「每轮该读哪段历史」——这正是 **Part 5 上下文纪元**的核心问题。L17 的循环跑起来了，Part 5 决定它「该读什么世界」。
- L18 的权限亮工具呼应 Part 7（工具系统）、Part 8（agent 权限）；L19 的 compaction 呼应 L51。

## 核心心智模型

1. **三层数据 + 状态机**：Session⊃Message⊃Part，tool 有 ToolState 终态机（L14）。
2. **先记账、再执行**：admit 把输入落成不可变事件，与模型执行解耦（L15）——这条脊梁在 L17 工具层、L19 投影端反复复刻。
3. **同会话串行、跨会话并发**：协调器按 key 分车道（L16）。
4. **有界、流式、每轮重读**的自驱循环（L17）。
5. **结构化并发**跑工具，可整体召回（L18）。
6. **一份真相、两种形状**：事件(底账)投影成消息(报表)（L19）。
7. **三道护栏**让危险引擎安全：有界/类型化错误/干净喊停（L20）。
