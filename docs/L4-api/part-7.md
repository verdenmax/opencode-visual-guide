# L4 · Part 7 源文件 → 课 对照 (API map)

opencode 源文件（`/home/verden/course/opencode`，除注明外均在 `packages/core/src/`）→ Part 7 中讲到它的课。

| opencode 源文件 / 符号 | 关键点 | 讲到它的课 |
| --- | --- | --- |
| `tool/tool.ts` | `Tool.make(config)`（Config={description,input,output,execute,toModelOutput?}）；返回 `Object.freeze({})`（不透明句柄）+ 模块级 `WeakMap<AnyTool,Runtime>`；`settle`(decode→execute→encode→{structured,content})；`definition(name)`(→JSON Schema)；`withPermission`；`validateName` 正则；`Context{sessionID,agent,assistantMessageID,toolCallID}`；`Content=text\|file` | L36 |
| `tool/registry.ts` | `ToolRegistry`：`register`（`local: Map<name,Array<{token,registration:{identity,tool}}>>` 叠摞、`addFinalizer` 按 token 撤销、`uninterruptible`）；`materialize`（applications+local 摞顶、删 `whollyDisabled`→`{definitions,settle}`）；`settleWith`（验 identity→Stale tool call、catch ToolFailure、`resources.bound`） | L37 |
| `tool/builtins.ts` | `locationLayer` = `Layer.mergeAll`(ApplyPatch/Bash/Edit/Glob/Grep/Question/Read(+FileSystem)/Skill/TodoWrite/WebFetch/WebSearch/Write).layer——各内置工具 Location 作用域自我登记 | L37, L38, L39, L40, L43 |
| `tool/read.ts` · `read-filesystem.ts` | `read{path,offset?,limit?}`→`Content\|TextPage\|ListPage`（读文件 OR 列目录、翻页、图片→base64+图片 mime）；`permission.assert` 读权限 | L38 |
| `tool/write.ts` | `write{path,content}`→`{operation:write,target,resource,existed}`；`withPermission "edit"`（write/edit/apply_patch 共用 "edit" 权限）；外部绝对路径需 external_directory | L38 |
| `tool/edit.ts` | `edit{path,oldString,newString,replaceAll?}`→`{...,replacements}`；验参(old==new/空串)→ToolFailure；`detectLineEnding`/`convertToLineEnding`(\n↔\r\n)；`countOccurrences`(0→拒/>1&!replaceAll→拒)；**`writeIfUnchanged({target,expected:source.content,content})`**(乐观并发 CAS)；`withPermission "edit"` | L38 |
| `tool/apply-patch.ts` | `apply_patch{patchText}`→`{applied:[{type:add\|update\|delete,resource,target}]}`；`Patch` 模块；`name="apply_patch"`；`withPermission` | L38 |
| `tool/glob.ts` · `grep.ts` | glob{pattern,path?,limit?}→Entry[]、grep{pattern,path?,include?,limit?}→Match[]；都用 `Ripgrep` 服务（默认尊重 .gitignore）；limit 上限 | L39 |
| `tool/bash.ts` | `bash{command,workdir?,timeout?,description?}`→{command,cwd,exitCode?,output,truncated,timedOut?}；`DEFAULT_TIMEOUT_MS`=2分/`MAX_TIMEOUT_MS`=10分(schema isLessThanOrEqualTo)/`MAX_CAPTURE_BYTES`=1MB；双 `permission.assert`；spawn detached+`forceKillAfter`3s、`stdin:"ignore"`；经 `AppProcess.run`（非 PTY）；timeout `catchTag`→timedOut | L39 |
| `process.ts` | `AppProcess`（`run`/`runStream`）→ `ChildProcessSpawner`/`CrossSpawnSpawner`（child_process/spawn 批处理）——bash 工具的执行后端，**非 PTY** | L39 |
| `pty/{pty,pty.bun,pty.node,protocol,schema,ticket}.ts` | `Proc{onData,write,resize}`——交互式伪终端基础设施（第 10 课 pty/pty-connect 路由、第 33 课 WebSocketTracker），**与 bash 工具分属两套** | L39（对照） |
| `tool/webfetch.ts` | `webfetch{url,format(text/markdown/html，**默认 markdown** via `withDecodingDefault`),timeout?}`→{url,contentType,format,...}；HTML→markdown | L40 |
| `tool/websearch.ts` | `websearch{query,numResults?(默认8),livecrawl?,type?(auto/fast/deep),contextMaxCharacters?}`；**本地工具**(Exa/Parallel)，区别于供应商自带；description 注入 `new Date().getFullYear()` | L40 |
| `tool/question.ts` | `question{questions:QuestionV2.Prompt[]}`→`{answers:QuestionV2.Answer[]}`；反向工具；custom 默认开→UI 自动补 freeform、模型别加「Other」 | L40 |
| `tool/todowrite.ts` | `todowrite{todos:SessionTodo.Info[]}`→`{todos}`；接 `SessionTodo` 服务；作用于 agent 自身状态（外置工作记忆） | L40 |
| `permission.ts` | `evaluate(action,resource,...rulesets)`=`flat().findLast(Wildcard.match)` ?? `{effect:"ask"}`(后匹配胜+默认 ask)；`assert`(deny→`DeniedError`/allow/ask→`permission.v2.asked`+`uninterruptibleMask` 挂起)；`reply`(once/always/reject)；`Reply`/`DeniedError`/`RejectedError`/`CorrectedError`；`missingAgentPermissions=[{*,*,deny}]` | L41 |
| `permission/schema.ts` | `Effect=allow\|deny\|ask`；`Rule={action,resource,effect}`；`Ruleset=Rule[]` | L41 |
| `permission/saved.ts` · `sql.ts` | `PermissionSaved`(always 规则持久化：`add`/`list`)；`PermissionTable`(`permission` 表 project_id+action+resource、唯一索引)——project 作用域、跨会话 | L41 |
| `tool-output-store.ts` | `ToolOutputStore`：`MAX_LINES`=2000/`MAX_BYTES`=50KB/`RETENTION`=7天/`MANAGED_DIRECTORY`="tool-output"；`bound`/`limits`/`preview`(掐头去尾 ceil/floor head+tail)/`boundedPreview`(marker 算进预算)/`write`(spill `tool_{ascending}` flag wx)→`outputPaths` | L42 |
| `config/tool-output.ts` | `ConfigToolOutput.Info{max_lines?,max_bytes?}`——覆盖默认界 | L42 |
| `skill/guidance.ts` | `SkillGuidance.load(agent)`→`SystemContext`（注入技能名+描述清单，Context Source）；Summary{name,description} | L43 |
| `skill/discovery.ts` | `SkillDiscovery`：从目录索引（`Index{skills:IndexSkill{name,files}}`）、能从 URL `download` 技能 | L43 |
| `tool/skill.ts` | `skill{name}`→{name,directory,output}；`Tool.make` + 内部 `permission.assert`(action: skill)（非 withPermission）；`toModelOutput` 注入 `<skill_content>`（content + 基准目录 URL + `<skill_files>` 清单，"file list is sampled"） | L43 |
| `CONTEXT.md`（repo 根） | 与有界工具输出、Managed File 相关的设计概念 | L42 |
