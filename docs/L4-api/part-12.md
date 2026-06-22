# L4 · Part 12 源文件 → 课 对照 (API map)

opencode 源文件（`/home/verden/course/opencode`）→ Part 12 中讲到它的课。这一部分多是<strong>仓库根级</strong>的构建/测试/贡献配置与脚本，而非业务源码。

| opencode 源文件 / 符号 | 关键点 | 讲到它的课 |
| --- | --- | --- |
| `CONTRIBUTING.md` | 贡献圣经：开发（`bun install`+`bun dev`、`bun dev <目录>`、Bun 1.3+）、`build.ts --single` 编单文件、调试器（worker 线程坑→`bun dev spawn`、分开调 server/TUI、VSCode 避坑）、Issue First Policy、PR 期望、**No AI-Generated Walls of Text**、PR 标题约定式、风格偏好、vouch/信任系统 | L62, L63 |
| `AGENTS.md` | 风格指南：默认分支 `dev`（本地或无 `main`，对比用 `origin/dev`）；分支名短≤3 词无前缀；提交/PR 标题 `type(scope): summary`（feat/fix/docs/chore/refactor/test）；编码风格（避 else/let、能 `.catch` 不 try/catch、避 any、不别名/星号导入、用 Bun API）；改 SDK 跑 `./packages/sdk/js/script/build.ts` | L63 |
| `packages/opencode/script/build.ts` | **编译成自包含二进制**：`Bun.build({compile})`（minify/splitting/format esm/target 形如 bun-linux-x64/outfile）；`createEmbeddedWebUIBundle`（build app→dist 每文件 `import ... with {type:"file"}`→映射→虚拟入口 `opencode-web-ui.gen.ts`）；`define` 注入 `OPENCODE_MODELS_DEV`/version/channel/libc；`allTargets` 跨平台矩阵；`--single`/`--baseline`/`--skip-install`/`--sourcemaps`/`--skip-embed-web-ui`；冒烟测试 `--version` 失败即 `exit(1)` | L62 |
| 根 `package.json`（scripts） | `dev`=`bun run --cwd packages/opencode --conditions=browser src/index.ts`；`test`=`echo 'do not run tests from root' && exit 1`（**护栏**）；`lint`=`oxlint`；`typecheck`=`bun turbo typecheck`；workspaces=`packages/*` 等 | L62, L63 |
| `packages/opencode/package.json`（scripts） | `test`=`bun test --timeout 30000 --only-failures`；`typecheck`=`tsgo --noEmit`；`build`=`bun run script/build.ts`；`dev`=`bun run --conditions=browser ./src/index.ts`；`test:httpapi`（覆盖/auth/effect 三模式校验） | L63 |
| `packages/*/**/*.test.ts`（500+ 个） | Bun 内置 `bun test` 运行的单测；约定**少用 mock、测真实实现**；须在**包目录**而非根目录跑 | L63 |
| `.github/ISSUE_TEMPLATE/` | 必用模板：`bug-report.yml`/`feature-request.yml`/`question.yml`（+`config.yml`）；不许空白 issue；自动检查不合规给 2 小时窗口否则自动关 | L63 |
| `.github/VOUCHED.td` | **vouch 信任名单**：vouched/denounced/everyone-else 三档；维护者评论 `vouch`/`denounce`/`unvouch` 管理、自动提交；denounced 的 issue/PR 自动关，专留给反复低质量 AI 贡献/灌水/恶意 | L63 |
| `CONTEXT.md`（`## Language` 节） | **受控词汇表**：像字典般定义核心概念（System Context/Session History/Context Source/Context Epoch/Baseline/Snapshot…）并标注「_Avoid_」别名——「精确词汇即工程工具」的范例，L64 术语表的源头 | L64 |
| `.vscode/settings.example.json` · `launch.example.json` | VSCode 调试范本；避开 `"request":"launch"` 与 JavaScript Debug Terminal（断点错位） | L62 |
| `models.dev`（外部仓库） | 新增 provider 通常**无需改 opencode 码**，去 `models.dev` 提 PR 即可；`build.ts` 经 `generate.ts` 把其数据 `define` 进二进制 | L62, L63 |
