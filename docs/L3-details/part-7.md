# L3 · Part 7 细节要点 (Details)

## L36 工具定义

- **`Tool.make(config)`**（`tool/tool.ts`）：`Config = {description（给模型读）, input, output（schema/codec）, execute: (input, context) => Effect<output, ToolFailure>, toModelOutput?}`。每个工具都填这同一张表（同第 29 课协议两栏表）。
- **schema 一肩三役**：① `definition(name)` 把 input/output schema 转 JSON Schema 给模型当说明书；② `settle` 用 input schema 解码校验进来的参数（脏输入→ToolFailure）；③ 用 output schema 编码校验出去的结果（脏输出→ToolFailure）。第 22 课「codec 一肩三役」在工具层再现。
- **不透明句柄 + WeakMap**：`make` 返回 `Object.freeze({})`（空对象），真正 Runtime（definition/settle/permission）藏在模块级 `WeakMap<AnyTool, Runtime>`。工具是「能力凭证」，只能交给 `Tool.settle/definition`；好处=不可篡改 + 装饰即派生新值（`withPermission`）+ 类型(Input/Output 幽灵参数)与运行时分离。WeakMap → 工具 GC 时 Runtime 自动释放。
- **settle 流水线**：`decodeUnknownEffect(input)(call.input)` → `execute(input, context)` → `encodeEffect(output)(result)` → `{structured（系统归档）, content（模型可读 text/file）}`。无 toModelOutput 且 output 为字符串时 content 默认即该字符串。
- `Context = {sessionID, agent, assistantMessageID, toolCallID}`（把调用锚回会话/agent）；`validateName` 正则 `/^[A-Za-z][A-Za-z0-9_-]{0,63}$/`。

## L37 工具注册表

- **register（可变·带作用域）**（`tool/registry.ts`）：`validateName` 每个名字 → `local: Map<name, Array<{token, registration:{identity,tool}}>>`（**同名叠成一摞**、`.at(-1)` 最新顶班）→ `Effect.addFinalizer` 按唯一 `token={}` 撤销（空了删名、剩的自动复位）。压栈+装 finalizer 裹在 `Effect.uninterruptible` 里原子完成。作用域关→登记自动消失、被覆盖者自动复位（第 23 课 acquireRelease 延伸）。
- **materialize(permissions)（不可变·快照）**：applications + local 摞顶合并 → 删掉 `whollyDisabled`（权限彻底禁的）→ `{definitions: ToolDefinition[]（给模型的菜单）, settle}`。**权限过滤在菜单层**——被禁工具不进 definitions，模型根本看不见。
- **settleWith（派单+防伪+善后）**：按 call.name 找摞顶登记 → **验 `identity`**（物化时记的 ≠ 当前 → `Stale tool call`，保证「所见即所调」）→ 第 36 课 settle → catch `ToolFailure` 成错误值 → `resources.bound(...)`（第 42 课）截断大输出。
- `token`=标识「哪次 register 调用」（撤销用）；`identity`=标识「哪个具体登记」（验防伪用）；空对象 `{}` 作天然唯一标识（引用唯一、`{}!=={}`、免 UUID）。`builtins.locationLayer` = `Layer.mergeAll` 内置工具 layer，各自 Location 作用域自我登记。

## L38 文件工具

- **四把手覆盖改动光谱**（`tool/{read,write,edit,apply-patch}.ts`，全是第 36 课 Config 表填法）：`read{path,offset?,limit?}`→Content/TextPage/ListPage（**读文件 OR 列目录**、翻页、图片→base64+图片 mime）；`write{path,content}`（整文件覆盖/新建）；`edit{path,oldString,newString,replaceAll?}`→{...,replacements}；`apply_patch{patchText}`→{applied:[{type:add|update|delete,...}]}（多文件批量、顺序施工）。
- **edit 执行=护栏流水线**：①验参（old==new→拒「无改动」、old==""→拒「用 write」，碰盘前）②`permission.assert` ③readFile+decodeUtf8(BOM) ④`detectLineEnding`+`convertToLineEnding`(\n↔\r\n 归一) ⑤`countOccurrences`：0→拒「找不到，须一字不差」、>1 且非 replaceAll→拒「多匹配，加上下文或设 replaceAll」 ⑥replaceAll?replaceAll:replace ⑦`writeIfUnchanged({target, expected: source.content, content})`。真正替换只第 ⑥ 步一行。
- **四道护栏**：精确匹配（含空格缩进）；歧义拒绝（不替模型猜）；行尾自动归一（避免假性失配）；**`writeIfUnchanged` = compare-and-swap 乐观并发**（只在磁盘内容仍等于读到的 `expected` 字节时才写，否则拒——防丢失更新；不上悲观锁）。
- 路径相对「当前 Location」解析；外部绝对路径需 `external_directory` 批准。所有「拒绝」走 `ToolFailure` 回传，错误消息即给模型的操作指南。

## L39 搜索与执行工具

- **glob/grep（`tool/{glob,grep}.ts`）= 两种「找」**：glob 按文件名 pattern、grep 按内容正则（+include 文件 glob）；output 文件/命中清单。**都架在 `Ripgrep` 服务上**（快、默认尊重 .gitignore），都带 `limit` 防结果撑爆上下文。复用权威上游（第 35 课同理）。
- **bash（`tool/bash.ts`）= 通用逃生舱**：input `{command, workdir?, timeout?, description?}`，拥有宿主用户的文件/进程/网络权限。护栏：限时（`DEFAULT_TIMEOUT_MS`=2 分 / `MAX_TIMEOUT_MS`=10 分，schema `isLessThanOrEqualTo` 卡上限）；限量（stdout/stderr 各 `MAX_CAPTURE_BYTES`=1 MB）；双重 `permission.assert`（workdir + 命令）；spawn `detached`（非 win32）+ `forceKillAfter` 3 秒；`stdin:"ignore"`。超时被 `catchTag` 降格成带 `timedOut:true` 的正常结果，回「加大 timeout 重试」。
- **bash ≠ PTY（关键澄清）**：bash 经 `AppProcess.run` → `ChildProcessSpawner`（`process.ts`，基于 child_process/spawn 的批处理：启动子进程、跑完、收 stdout/stderr），**不是伪终端**。`pty/*`（`Proc.onData/write/resize`）是**另一套**给交互式终端用的基础设施（第 10 课 pty/pty-connect 路由、第 33 课 WebSocketTracker）。批处理（给模型，一问一答）vs 交互式（给真人，实时流+可输入），两套机制，诚实切分。

## L40 其他内置工具

- **两条新轴外推 agent 能力**（`tool/{webfetch,websearch,question,todowrite}.ts`），全是第 36 课 Config 填法。
- **向外·网络**：`webfetch{url, format(text/markdown/html，**默认 markdown** via `withDecodingDefault`), timeout?}`——把网页转成模型好消化的干净正文，非原始 HTML。`websearch{query, numResults?(默认 8,有上限), livecrawl?, type?(auto/fast/deep), contextMaxCharacters?}`——opencode **本地工具**（背后 Exa/Parallel），区别于「供应商自带、在供应商侧执行」的 web search（搜网能力不被供应商绑定）；description **注入 `new Date().getFullYear()`** 补模型时间盲区。
- **转内·人与自己**：`question{questions[]}`→`{answers[]}`——**反向**工具（从用户拉回答案，处理歧义/抉择）；多选优先，`custom` 默认开时 UI 自动补 freeform，故叮嘱模型别加「Other」。`todowrite{todos[]}`→`{todos}`——作用于 **agent 自身状态**（接 `SessionTodo` 服务），维护会话待办、随做随更新——「外置工作记忆」，帮长任务不忘全局、让用户看见进度。

## L41 权限系统

- **三态规则引擎**（`permission/schema.ts`）：`Rule = {action, resource, effect: allow|deny|ask}`，`Ruleset = Rule[]`。
- **`evaluate(action, resource, ...rulesets)`**（`permission.ts`）：`rulesets.flat().findLast(Wildcard.match(action)&&match(resource))` ?? `{effect:"ask"}`。**后匹配者胜**（顺序即优先级，saved/agent/config 规则拼接）；**未命中默认 ask**（安全默认：未知交给人；agent 无法钻空子悄悄做未批准的事）。`{*,*,deny}`=全拒兜底（`missingAgentPermissions`）。
- **`assert`**：deny→`DeniedError`（且第 37 课 `whollyDisabled` 不进菜单）；allow→静默放行；ask→发 `permission.v2.asked` 事件、`uninterruptibleMask` 内用 Deferred 挂起等回答。
- **`reply` once/always/reject**：once 仅此次；**always→放行 + `saved.add` 持久化规则**（`permission/sql.ts` `permission` 表：project_id+action+resource 唯一索引，**project 作用域、跨会话**，下次直接 allow；顺带解除被新规则覆盖的其它挂起询问）；reject→`RejectedError`，带反馈→`CorrectedError`（理由回传模型=纠偏而非死胡同）。
- **两级把关**（纵深防御）：deny 在「菜单层」（whollyDisabled，模型看不见）；ask 在「调用层」（执行前发问）。会随信任减少打扰：默认保守、always 攒规则逐步放开。

## L42 有界工具输出

- **动机**：模型上下文有限且昂贵，工具输出可能极大（grep 万行/cat 几兆），原样回灌会烧钱、拖慢、更会把重要内容挤出窗口。`ToolOutputStore`（`tool-output-store.ts`）是工具结果回模型前的最后一道闸（第 37 课 settle 调的 `resources.bound`）。
- **常量**：`MAX_LINES=2000`、`MAX_BYTES=50KB`（`config/tool-output.ts` 的 `max_lines/max_bytes` 可覆盖）、`RETENTION=7 天`、`MANAGED_DIRECTORY="tool-output"`。
- **掐头去尾截断**（`preview`）：超界保留 `headLines=ceil(maxLines/2)` + `tailLines=floor(maxLines/2)`（**头+尾，非只 head**，奇数时头多留一行），中夹 marker；字节超界同理 `takePrefix(headBytes)`+`takeSuffix(tailBytes)`。因信息密度集中两端（头=在跑啥、尾=结果/报错），只留前 N 行会砍掉最关键的结果。`boundedPreview` 把 marker 自身字节也算进预算（`maxBytes - markerBytes - 4`）。
- **外溢 spill + 回取**：截断同时 `write` 全文到 `{global.data}/tool-output/tool_{Identifier.ascending()}`（`flag:"wx"` 独占创建），路径入 `outputPaths` 交模型；要看全文用第 38 课 read 工具读（可翻页）——有界视图 + 完整备份 + 按需访问，工具系统自我兜底（复用已有 read，第 36 课统一工具表的红利）。
- **两层界**：bash 1 MB 内存上限（第 39 课）防内存 vs ToolOutputStore 2000 行/50 KB 防上下文。

## L43 Skills 系统

- **skill = 知识+步骤+配套文件的打包单元**（`skill/*`、`tool/skill.ts`），按需加载。给 agent 加本领=往技能库丢一个 skill，不重训模型、不改代码。
- **两段式架构（核心）**：**名字半**经 `SkillGuidance.load(agent)` → `SystemContext`（M5 Context Source、第 21~27 课）常驻注入（仅 `<name>`+`<description>` + 一句「匹配时用 skill 工具加载」，省 token、随时可见）；**正文半**经 `withPermission` 的 `skill` 工具（input `{name}`）`toModelOutput` 按需注入完整 `<skill_content>`（指令 + 基准目录 URL + `<skill_files>` 清单）。**渐进式披露/懒加载**——与第 37 课「definitions 全列/settle 按需」、第 42 课「预览常驻/全文 spill」同一套路。
- **skill 只「发讲义」不「干活」**：注入正文（含基准目录与文件清单），真正执行靠模型已有通用工具（read 读 scripts/、bash 跑、edit 改）。技能扩展「知道该怎么做」（方法论），非「能做什么」（能力）。
- **M5+M7 交汇点**：用全 Context Source（M5）+ Tool.make（L36）+ 注册表（L37，`SkillTool.layer`）+ 权限（L41）+ read（L38）；半上下文、半工具。`SkillDiscovery`（`skill/discovery.ts`）从目录索引（Index{name,files}）、能从 URL 下载——可发现/分发/扩展。文件清单标注 `sampled`（抽样、有界），层层懒加载。
