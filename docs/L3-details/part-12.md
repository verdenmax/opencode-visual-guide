# L3 · Part 12 细节要点 (Details)

## L62 本地构建与调试

- **`bun dev` = 从源码即时跑的 `opencode`**：两者是同一套 CLI 的两副面孔，命令一一对应（`bun dev serve`↔`opencode serve`、`web`、`<目录>`）。`bun dev` 把 TypeScript 源码直接喂给 Bun 运行时即时执行（省掉编译、秒级反馈，适合高频「改一点看一眼」），`opencode` 是编译固化的二进制。要求 `Bun 1.3+`；根目录 `bun install`+`bun dev`。
- **默认工作目录与切换**：`bun dev` 默认在 `packages/opencode` 里跑（用 opencode 编辑自己的包）；`bun dev <目录>` 对着别的目录跑、`bun dev .` 对着 opencode 仓库根。这个灵活是 L61 **Location** 解耦的直接红利。`bun dev serve` 单起无头服务器，默认 `4096` 端口。
- **为什么选 Bun**：Bun 既是包管理器、又是能直接跑 TS 的运行时、还是打包器——一套工具贯穿「装依赖→跑源码→编成品」，省去传统 Node 的 `tsc`+`node`+`webpack` 拼装（同 L62「一套工具贯穿全程」）。
- **monorepo 结构**：`packages/opencode`（核心+server）、`cli/cmd/tui/`（TUI，SolidJS+opentui）、`packages/app`（共享 Web UI）、`packages/desktop`（Electron 包 app）、`packages/plugin`（`@opencode-ai/plugin` 源）；改 server/SDK 后跑 `script/generate.ts` 重生成 SDK。
- **`build.ts` = 编译成自包含单文件二进制**（`packages/opencode/script/build.ts`）：用 `Bun.build({compile})` 把三样**嵌进一个二进制**——①业务代码 bundle+minify；②Web UI 先 `build packages/app`、再把 dist 每个文件 `import ... with {type:"file"}` 编进去（`createEmbeddedWebUIBundle`）；③models.dev 数据用 `define` 注入 `OPENCODE_MODELS_DEV` 常量。产物不依赖 node_modules/运行时，是 rust-embed 式「编译期固化资源、运行期零外部依赖」。
- **构建流水线 + `--single`**：清 dist→嵌 Web UI→按目标 `Bun.build compile`→冒烟测试 `opencode --version`（失败 `exit(1)`）→写 per-target `package.json`。`--single` 只为当前平台编一个原生二进制；不加则跨平台矩阵（linux/darwin/win32 × arm64/x64 × musl/baseline，CI 发版用）。产物在 `dist/opencode-<平台>/bin/opencode`。单文件自包含是 `curl | bash` 一行装好、跨平台分发的工程底座。
- **调试器**：Bun 调试「还很粗糙」，最可靠是手动 `bun run --inspect=ws://localhost:6499/ dev ...` + attach。**关键坑**：`bun dev` 把 server 跑在 **worker 线程**里，主线程断点映不进→不触发；解法 `bun dev spawn`（server 不进 worker 线程）。这坑恰好印证 L09–L13 的 client/server 分离——server 是能独立存在的进程。
- **分开调 + VSCode**：`spawn` 不灵就分开调——server `bun run --inspect=ws://... --cwd packages/opencode ./src/index.ts serve --port 4096` + `opencode attach http://localhost:4096`；TUI 加 `--conditions=browser`。技巧：`export BUN_OPTIONS=--inspect=...`、`--inspect-wait`/`--inspect-brk`。VSCode 用 `.vscode/*.example.json`，避开 `"request":"launch"` 与 JavaScript Debug Terminal（断点错位）。

## L63 测试与贡献

- **Bun 内置测试 + 根目录护栏**：`bun test` 无需额外框架，全仓 500+ `*.test.ts`。**不能在根目录跑**——根 `package.json` 的 `test` 脚本故意写成 `echo 'do not run tests from root' && exit 1`。因为是 monorepo，每个包有自己的测试/环境，要 `cd packages/opencode && bun test`（opencode 包加 `--timeout 30000 --only-failures`）。护栏=「让用错的姿势立刻、响亮地失败」（同 L37 stale 工具调用、L48 库非空无表、L53 Provider 外用 context）。
- **类型检查与 lint**：根 `typecheck`=`bun turbo typecheck`（批量各包）、包内 `tsgo --noEmit`；根 `lint`=`oxlint`（Rust 实现的超快 linter）。
- **怎么写测试**（AGENTS 风格指南）：**尽量别用 mock、测真实实现**，别把逻辑在测试里再抄一遍（否则测的是「你抄得对不对」）。mock 太多易测出「假绿」（mock 顺、真实崩）。CONTRIBUTING「逻辑改动」要求：说清测了什么、审阅者如何复现/确认——测试终点是「别人能照着确认它真的对」。
- **Issue First Policy**：所有 PR 必须先有 issue（`Fixes #123`/`Closes #123`），没关联 issue 的 PR 可能不经审阅直接关。Issue 必须用模板（`bug-report`/`feature-request`/`question`），不许空白；自动检查不合规给 **2 小时**修改、否则自动关。
- **流程与分支/提交规范**：开 issue（模板）→认领→开分支改→提 PR（小而专注+约定式标题+说明如何验证；UI 附截图）→审阅合并（UI/核心功能须先过设计评审）。分支名短≤3 词、连字符、无 `feat/` 前缀；默认分支 `dev`；提交/PR 标题约定式 `type(scope): summary`（type∈feat/fix/docs/chore/refactor/test）。
- **No AI-Generated Walls of Text**：又长又空的 AI 生成 PR/issue 不可接受、可能被忽略；用自己的话简短说清「改了什么、为什么」（说不清=PR 太大）。新功能须先开 issue 做设计对话。这是「保护维护者注意力」（同 L42/L59 信号稀缺，守护的是人的注意力）。
- **vouch 信任系统**（`.github/VOUCHED.td`）：vouched（已背书）/ everyone-else（无需背书也能正常开 issue/PR，默认开放）/ denounced（issue/PR 自动关，专留给反复灌低质量 AI 内容/灌水/恶意者，**不**用于分歧或诚实失误）。维护者评论 `vouch`/`denounce`/`unvouch` 管理，自动提交。精妙在分寸：既开放又有底线。新增 provider 通常无需改码，去 models.dev 提 PR。

## L64 术语表与索引

- **精确词汇即工程工具**：opencode 根部 `CONTEXT.md` 的 `Language` 一节像字典般定义每个核心概念，并写明「_Avoid_」别名（如 System Context _Avoid_ system prompt、Session History _Avoid_ Session Context）。当团队（含 AI 协作者）共享一套精确无歧义词汇，沟通损耗/误解 bug/来回澄清大减。这份术语表是「用词即设计」哲学的延续，非附录。
- **概念依赖图（自底向上）**：地基 Effect（DI/Fiber/错误即值）→骨架 client/server（Hono·SSE·SDK）→主循环 Session（agent loop·工具调用）→记忆 Context Epoch→嘴巴 LLM 协议→双手 工具（Tool.make·权限）→装配 配置/持久化→表面 TUI/扩展。这条链既是本书 12 部分的顺序、也是 opencode 代码的依赖方向；新读者「从最左地基读起」。
- **术语速查表**：按 12 部分组织，每个核心术语一句话定义 + 链接回详讲它的那一课（opencode/Effect/Layer·Context/Fiber/Server/Event Bus/Session·Message·Part/Agent Loop/Projected History/System Context/Context Source/Context Epoch/协议适配器/Model Resolution/Tool.make/Permissions/Skills/Agents/MCP/Provider Plugin/Drizzle·SQLite/Compaction·Snapshot/opentui/frecency/Plugin·Hooks/LSP/PTY/ACP·Location）。是日后查阅主入口。
- **可迁移智慧表**：复用成熟生态（L39/L59）、编辑一份草稿（L54/L58）、找准接缝（L47/L61）、用错即响亮失败（L37/L63）、注意力稀缺（L42/L63）、统一模子刻同形（L36/L53）——跨越具体技术、可迁移到读者自己的项目。
- **SOFT_EXEMPT**：L64 是 `check_html` 的软豁免项（`SOFT_EXEMPT={"64-glossary.html"}`），免去 ≥3000 CJK / ≥6 图示 / key-points / analogy 等软约束——因为索引页的形态本就不同于教学课。但仍需 zh+en 双语、h1/title/desc 齐全（否则 ERROR）。
