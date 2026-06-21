# L3 · Part 4 细节要点 (Details)

## L14 Session、消息与 part

- core 一切最终落在三层嵌套：**Session ⊃ Message ⊃ Part**。
- **Session.Info**（`session/schema.ts`）：id（"ses_" 品牌化）、**parentID**（可分叉成树）、projectID/agent/model、**cost/tokens**（账单一等公民）、time、title、**location**（作用域）。只装元数据，不装内容（轻身份/重内容分开）。
- **Message** 是 8 成员标签联合（`message.ts`，按 `type` 分）：User、Assistant、System、Synthetic、Shell、Compaction、**AgentSwitched/ModelSwitched**（换 agent/model 也是不可变历史消息——事件溯源伏笔）。
- **Assistant.content 是 part 数组**（不是字符串）：AssistantContent 联合 = **text / reasoning / tool**，支持交错与逐 part 增量更新（喂活 L11 SSE）。
- **tool part 内含 ToolState 状态机**：pending → running → completed/error，信息逐阶段递增；这是 L20「工具终态不变量」守护的对象。

## L15 事件溯源输入收件箱

- prompt 到达后**不直接跑模型**，先 **admit**：`SessionInput.admit`（`input.ts`）把 prompt **publish 成 PromptLifecycle.Admitted 事件**、拿单调 **admitted_seq**、落进 `session_input` 表——又快又稳，不跑模型。
- **三个噩梦一次消解**：崩溃丢失（事件已落库）、并发打架（统一 seq 排队、串行取）、重试翻倍（按 id 幂等：`if (existing) return existing`）。类比数据库 WAL：先记意图、再兑现。
- **session_input 表**（`sql.ts`）：id（PK）、prompt(JSON)、delivery、admitted_seq（唯一/单调）、**promoted_seq（NULL=待领）**、time_created。两个序号刻出一个 prompt 的旅程；序号比布尔状态位多给「顺序」。
- **delivery**：`steer`（插话，并入当前活动、下个安全边界生效）/ `queue`（排队，开未来活动）。admit 后调 `SessionExecution.wake`（advisory，可合并）。

## L16 运行协调器

- 铁律（源码注释）：「**每个 key 至多一条排空链，不同 key 可并发**」。key=会话 ID。靠内部 `Map<Key, Entry>`（每会话一车道）：同 ID 串行、异 ID 并发。是 L08 KeyedMutex 精装版。
- **为什么串行**：agent 执行不断读写同一份共享状态（历史/工具状态/账单），两趟同跑=竞态。协调器从结构上排除，而非加锁补救。
- **run vs wake**：`run`=显式发车（起链或**并入**当前链）；`wake`=建议摇铃（空闲起链，忙则只**合并一个后续**）。admit 后摇的是 wake。
- **coalesce**（`run-coordinator.ts`）：途中纷至的请求折叠成至多一个后续——**run 压倒 wake；wake 取 maxSeq**。十记铃归一次精准补跑（drain 本就扫光当前所有合格行，故一个后续足矣）。
- 状态机：`idle → draining → 至多一次合并补跑 → idle`，焊死「至多一条链」。还有 `interrupt`（L20）。`SessionExecution.make({drain})` 把 drain=`SessionRunner.run` 接进来，调度与执行解耦。

## L17 V2 agent 循环

- agent ≠ 聊天机器人：一个目标、多轮自驱「想→调工具→看结果→再想」。`SessionRunner.run`（`runner/llm.ts`）是大脑真正思考处。
- 形状：`while(openActivity){ for(step<MAX_STEPS=25){ needsContinuation = runTurn(...) } }`；超 25 抛 StepLimitExceededError；外层 while 开 queue 活动，内层 for 有界轮次。
- **一轮 = 恰好一次 `llm.stream(request)`**：reasoning/text/tool-call 流式到达、**逐事件增量落盘**（填 L14 part 数组、推 L11 SSE）。
- **工具纪律**：先 durably 记成 pending（再动副作用）；FiberSet 并发起、await 全部 settle 才进下一轮（等齐保证下一轮看到完整世界状态）。
- **每轮重读投影历史**（不在内存攒状态）：持久层即唯一真相——steer 即时并入（`if(!needsContinuation) needsContinuation = hasPending("steer")`）、崩溃恢复、多端一致。`failInterruptedTools` 在开跑前清理上次残留。
- 顶部有带 `[x]/[ ]` 的契约清单注释，是循环的设计说明书。

## L18 工具调用与 FiberSet

- **materialize**（`tool/registry.ts`）按 **permissions 筛 definitions**：`whollyDisabled` 的工具 `registrations.delete(name)`——禁用工具**根本不出现**在给模型的清单里（最好的拦截=让选项不出现）。每轮重跑→权限是动态视野。
- **settle**：契约与真实副作用之间的门，执行单次调用，结果按类型写回 ToolState。
- **FiberSet**：`make` → 每个 settle `FiberSet.run(toolFibers)`（并发）→ `awaitToolFibers = raceFirst(join, awaitEmpty)`（全完成 or 速错）→ `clear`（中断时全体召回）。对比 `Promise.all`：FiberSet 可整体取消、不留野线程（L07 结构化并发）。
- **中断纪律**：`Effect.uninterruptibleMask((restore) => restore(settle(...)))`——默认锁死记账、仅 restore 把工具执行开放成可中断。方向是「记账完整 > 执行能停」。
- **ToolOutputStore**（`tool-output-store.ts`）：`MAX_LINES=2000` / `MAX_BYTES=50KB` / `RETENTION=7天`；大输出落盘、消息只存 `outputPaths`（L42 有界输出雏形）。

## L19 投影历史

- **一份真相、两种形状**（CQRS / 事件溯源读模型）：写端=append-only 事件（底账，求稳），读端=投影出的 `MessageTable`/`PartTable`（报表，求快）。
- **投影器**（`SessionProjector`，`projector.ts`）：消费事件、insert/update 消息行（Admitted→User 消息、流式片段→Assistant part 数组、工具翻牌→更新 state）。注释「新回合取代过时残行，绝不续投更老 assistant」保证读模型自洽。它是 L14 结构化数据的「填表人」。
- **为什么投影而非每次重放**：循环每轮重读，长会话上千事件，全重放代价线性增长。投影=拿写端一次性成本换读端长久廉价（读时 select）。同物化视图/索引。
- **history.load**（`history.ts`）：L17「重读投影历史」的底层。并发取 **baseline_seq（上下文纪元）+ latestCompaction**，据这两条边界 `messageRows` 只取**有界窗口**、逐行 decode。窗口由 compaction（L51）+ 纪元基线（L24）裁边——「读历史」=「读当前该看的一段」。

## L20 有界步数与错误处理

- agent 循环强大但危险（听不可信模型、跑有副作用工具、可中断/崩溃），需三道护栏。
- **护栏一·有界步数**：`MAX_STEPS=25`，撞限抛 **StepLimitExceededError**（`runner/index.ts`，`TaggedErrorClass` 带 sessionID/limit），不是默默停。25 是经验校准的折中、显式常量。
- **护栏二·类型化错误**：**RunError** 联合（LLMError / StepLimitExceededError / MessageDecodeError / SessionRunnerModel.Error / ContextSnapshotDecodeError / InitializationBlocked / AgentReplacementBlocked / ToolOutputStore.Error）。`run` 返回 `Effect<void, RunError>`——错误即值、写进签名，编译器逼调用者面对每一种。错误联合也是极佳文档。
- **护栏三·干净喊停**：`Cause.hasInterrupts` → `FiberSet.clear`（召回工具）+ **failUnsettledTools**（把没结清的工具标记 error）。配合开跑前的 **failInterruptedTools**，两把扫帚保证**工具终态不变量**：每个工具最终落到明确终态，绝无「永远 running」残骸。
- 收尾哲学：分情况收尾但殊途同归到 failUnsettledTools，最后 `Effect.failCause` 如实上抛——先收干净自己的烂摊子，再诚实交出错误。
