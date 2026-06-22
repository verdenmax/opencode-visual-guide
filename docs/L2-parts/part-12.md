# L2 · Part 12 — 实战、贡献与速查 (Practice, Contribution & Reference)

**课程：** L62–L64 ｜ **状态：** 已完成

## 职责

Part 12 是全书的收官部分。在 M1–M11 把 opencode 的<strong>内部机制</strong>从地基到表面讲透之后，这一部分回答三个最朴素、却最实战的问题：**怎么把它在自己机器上跑起来、改起来、调起来？怎么验证改动、贡献回去？以及——这 64 课到底教了我什么？** L62 讲<strong>本地构建与调试</strong>：`bun dev` 是从源码即时跑的 `opencode`（开发回路），`build.ts` 用 Bun 把代码+Web UI+模型数据编译嵌进一个自包含二进制（生产成品），而调试器「断点不触发」的坑恰好是一扇窥见 server 跑在 worker 线程、client/server 分离的窗口。L63 讲<strong>测试与贡献</strong>：`bun test` 在包目录而非根目录跑（根目录护栏故意报错）、测真实实现少用 mock、issue 先行、PR 小而专注、拒绝 AI 长篇大论、vouch 信任名单——一整套规范背后是同一条暗线：**在 AI 能批量生成的时代，死守信噪比、敬重维护者时间**。L64 是<strong>术语表与索引</strong>（SOFT_EXEMPT）：一张从地基到表面的概念依赖图、一份链接回每一课的术语速查表、一张「可迁移智慧」的收束表，并点出 opencode 自己 `CONTEXT.md` 的 `Language` 一节正是「精确词汇即工程工具」的范例。读完这部分，你就从「读懂 opencode」毕业为「能动手用、改、贡献 opencode，并带走可迁移的工程智慧」。

## 覆盖范围

| 课 | 主题 | 一句话 |
| --- | --- | --- |
| L62 | 本地构建与调试 | **从源码到二进制的实战回路**。`bun dev` = 从源码即时跑的 `opencode`（同一套 CLI，`serve`/`web`/`<目录>` 一一对应；秒级反馈、无需编译；默认在 `packages/opencode` 跑、`bun dev <目录>` 换工作对象=L61 Location 红利；要求 Bun 1.3+）。`build.ts` = 用 `Bun.build({compile})` 把**代码 + Web UI（`with {type:"file"}` 嵌入）+ models.dev 数据（`define` 注入）**编进**一个自包含二进制**（不依赖 node_modules/运行时，同 rust-embed；`--single` 只编当前平台、否则跨平台矩阵；冒烟测试 `--version` 失败即 `exit(1)`）。**调试**：最可靠是手动 `--inspect=ws://...`+attach；坑=`bun dev` 把 server 跑在 worker 线程→断点映不进→`bun dev spawn`，或借 client/server 分离分开调（`serve --port 4096`+`opencode attach`；TUI 加 `--conditions=browser`）；避开 VSCode `"request":"launch"` 与 Debug Terminal |
| L63 | 测试与贡献 | **验证改动 + 体面贡献**。测试：Bun 内置 `bun test`，**不能在根目录跑**（根 `test` 脚本故意 `echo 'do not run tests from root' && exit 1`——monorepo 护栏，同 L37/L48/L53「用错即响亮失败」），要 `cd` 进包目录（opencode 包加 `--timeout 30000 --only-failures`）；**少用 mock、测真实实现**（别把逻辑抄进测试）；配 `tsgo --noEmit`+`oxlint`。贡献：**issue 先行**（所有 PR 必须先有 issue，`Fixes #123`）、用模板（不合规 2 小时自动关）、分支名短≤3 词无前缀、默认分支 `dev`、PR 小而专注+约定式标题+说明如何验证、**拒绝 AI 长篇大论**。信任：**vouch 名单**（`.github/VOUCHED.td`）默认对所有人开放、只对反复灌低质量 AI 内容者除名。**暗线**：整套为「AI 时代死守信噪比、敬重维护者时间」服务 |
| L64 | 术语表与索引 | **全书地图 + 速查**（SOFT_EXEMPT）。**概念依赖图**：地基(Effect)→骨架(client/server)→主循环(Session)→记忆(Context Epoch)→嘴巴(LLM)→双手(工具)→装配(配置/持久化)→表面(TUI/扩展)，自底向上、即 12 部分的组织顺序。**术语速查表**：每个核心概念一句话+链接回详讲它的那一课（System Context/Context Epoch/Tool.make/frecency/ACP…）。**可迁移智慧表**：复用成熟生态、编辑一份草稿、找准接缝、用错即响亮失败、注意力稀缺、统一模子刻同形——各指 1–2 课为范例。**亮点**：opencode `CONTEXT.md` 的 `Language` 节像字典般定义术语、甚至写明「_Avoid_」别名——**精确共享的词汇本身就是工程工具**，这份指南做的是同一件事 |

## 与相邻部分的关系

- **收束全书 Part 1–11**：L64 的概念依赖图与术语表把 M1–M11 的所有核心概念（Effect/Session/Context Epoch/LLM 协议/工具/持久化/TUI/扩展）串成一张可跳转的地图；L62 的「调试器坑」回头印证 M3 的 client/server 分离、「`bun dev <目录>`」复用 L61 Location；L63 的「根目录测试护栏」复用全书 L37/L48/L53「用错即响亮失败」，「拒绝 AI 长篇」呼应 L42/L59「注意力稀缺」。
- **复用全书机制**：L62 `build.ts` 嵌入 Web UI/模型数据呼应「编译期固化资源」、借 Bun 编译呼应 L39/L51/L59「复用成熟工具」；L63 测真实实现少用 mock 呼应全书「测真东西、能被复现」的工程态度；L64 把「找准接缝/编辑草稿/统一模子」等贯穿主题正式收拢成「可迁移智慧」。
- **全书终点**：Part 12 之后再无新机制——它把读者从「理解 opencode 内部」送达「能跑、能改、能贡献，并带走可迁移工程智慧」。L64 末尾正式为 64 课画上句点。

## 核心心智模型

1. **开发即时、发布自包含**（L62）：`bun dev` 从源码秒级反馈照顾高频迭代，`build.ts` 编译成单文件二进制照顾零依赖分发——同一份 CLI、同一套代码，只是「源码跑 vs 编译跑」。双形态从根上消除「开发能跑、上线就挂」。
2. **护栏即文档**（L62+L63）：调试器的 worker 线程坑被诚实写进 CONTRIBUTING、根目录测试被故意写成报错护栏——一个成熟项目把「容易踩的坑」提前变成「踩到就报警 + 告诉你正确姿势」，把工具的粗糙之处坦诚记档比假装顺滑更厚道。
3. **测试是写给未来读它、信它的人看的**（L63）：测真实实现、少用 mock、要能被审阅者复现——终点不是「我本地过了」而是「别人能照着确认它真的对」。假绿（mock 顺但真实崩）比红更危险。
4. **AI 时代死守信噪比**（L63）：issue 先行、PR 小而专注、拒绝 AI 长篇、vouch 除名灌水者——一个本身就是 AI 助手的项目，却在门口要求「别把未经消化的 AI 产物倾倒给维护者」。判断与提炼仍是人的责任，不该被工具便利稀释。
5. **精确词汇即工程工具**（L64）：给概念起好名字、坚持只用这个名字（CONTEXT.md 的 `Language` + `_Avoid_`），是把复杂系统讲清楚的第一步。术语表不是附录，是「用词即设计」哲学的延续。
