"""Part 9 (Part 9 · Persistence) content. Placeholders until M9 fills them in."""
from placeholder import wip

LESSON_48 = {
    "zh": r"""
<p class="lead">前八个部分，我们一直在讲 agent「活着」时的事：怎么和模型对话（M6）、怎么调工具（M7）、怎么被配置成一个角色（M8）。但 agent 不可能永远活着——进程会退出、机器会重启、你关掉终端明天再来。那么它<strong>跑过的会话、来回的消息、攒下的上下文，存到哪儿去了？</strong>这就是 M9「持久化与存储」要回答的。这一课是 M9 的地基：opencode 用 <strong>SQLite</strong>（一个嵌入式、单文件的关系型数据库）当存储底座，用 <strong>Drizzle</strong>（一个 TypeScript 的类型安全 ORM）把数据库的「表结构」用代码写出来。这一课不讲具体存了哪些表（那是下一课 L49 的事），而专讲<strong>两件地基性的事</strong>：① 表结构怎么用 Drizzle 以「代码即 schema」的方式定义；② 当表结构需要演进（加一列、改一个表）时，那套<strong>数据库迁移（migration）</strong>系统是怎么安全地把老库升级到新结构的。</p>
<p>这一课最值得带走的洞见，藏在 opencode 的迁移系统里——它走的是一条<strong>「双路径」</strong>：对一个<strong>全新的空数据库</strong>，它不会傻乎乎地把历史上三十多个迁移从头重放一遍，而是<strong>直接套用当前最新的完整 schema 快照</strong>，再把那三十多个迁移<strong>统统标记为「已完成」</strong>；只有对一个<strong>已存在的老数据库</strong>，它才<strong>逐个补跑那些还没跑过的迁移</strong>。这个「新库套快照、老库补增量」的设计极其聪明：它让新用户的首次启动又快又干净（一步到位建好最新结构），又让老用户的库能平滑地一点点升级而绝不丢数据。读懂这套机制，你就懂了「一个软件如何在不断改数据结构的同时，既不拖累新用户、也不抛弃老用户」——这是所有需要长期演进的有状态软件都绕不开的核心难题。</p>

<div class="card analogy">
  <div class="tag">🗄️ 生活类比</div>
  把 SQLite 想象成一个<strong>嵌进你家书桌里的文件柜</strong>——不是去外面租一间仓库（那是 PostgreSQL 这类要单独跑服务器的数据库），而是就在手边、整个柜子就是<strong>一个文件</strong>（<span class="mono">opencode.db</span>），随软件一起带走。而 Drizzle 的 schema，就是这个文件柜的<strong>「抽屉图纸」</strong>：每个抽屉（表）叫什么、里面分几格（列）、每格放什么类型的东西，全用代码画清楚。最妙的是<strong>迁移</strong>那一套——它像文件柜的<strong>「装修施工日志」</strong>：「3 月 12 日，给 session 抽屉加一个 path 格」「4 月 28 日，加一个 archived 格」……每一笔改造都按日期编号、记进日志。来了个<strong>全新的空柜子</strong>？不必把历史上每笔改造重做一遍，直接照<strong>最新版图纸</strong>一次装好，再在日志上把所有历史改造都打个「✓ 已做」的勾。而一个<strong>用了半年的旧柜子</strong>？翻开它的日志，看哪几笔改造还没做，<strong>就只补做那几笔</strong>——半点不多动，半点不少做。
</div>

<h2>代码即 schema：用 Drizzle 定义表</h2>
<p>opencode 的表结构不是写在一堆 <span class="mono">.sql</span> 文件里，而是<strong>用 TypeScript 代码定义</strong>的。看 <span class="mono">drizzle.config.ts</span>：它把 schema 的来源指向 <span class="mono">["./src/**/*.sql.ts", "./src/**/sql.ts"]</span>——也就是说，<strong>每个领域的表结构，就和那个领域的代码放在一起</strong>（session 的表在 <span class="mono">session/sql.ts</span>、project 的表在 <span class="mono">project/sql.ts</span>），而非集中在某个远离业务的角落。一张表就是一个 <span class="mono">sqliteTable("表名", { 列定义 }, (t) =&gt; [索引])</span>。Drizzle 给了一套小巧的「列定义工具箱」：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">text() / integer() / real()</div><div class="c-txt">三种基础 SQLite 类型：文本 / 整数 / 浮点</div></div>
  <div class="cell"><div class="c-tag">text({ mode: "json" }).$type&lt;T&gt;()</div><div class="c-txt">把一个对象/数组以 JSON 存进一列，并标注它的 TS 类型</div></div>
  <div class="cell"><div class="c-tag">.$type&lt;BrandedID&gt;()</div><div class="c-txt">给列贴上「品牌 ID」类型，编译期防止把 SessionID 当 MessageID 用</div></div>
  <div class="cell"><div class="c-tag">.references(() =&gt; X.id, {onDelete:"cascade"})</div><div class="c-txt">外键：父行删了，子行级联自动删（数据库帮你保证一致性）</div></div>
  <div class="cell"><div class="c-tag">.notNull() / .default(0) / .primaryKey()</div><div class="c-txt">非空约束 / 默认值 / 主键</div></div>
  <div class="cell"><div class="c-tag">Timestamps（复用片段）</div><div class="c-txt"><span class="mono">time_created</span>(插入时填) + <span class="mono">time_updated</span>(更新时自动刷)，一处定义、各表展开复用</div></div>
</div>
<p>这里有个贯穿全 opencode 的<strong>命名约定</strong>值得专门点出：列名一律用 <strong>snake_case</strong>（如 <span class="mono">project_id</span>、<span class="mono">time_created</span>），而不是 camelCase。为什么？因为 Drizzle 默认<strong>直接拿字段名当列名</strong>——写 <span class="mono">project_id: text()</span>，列名就是 <span class="mono">project_id</span>，<strong>无需再把列名当字符串重写一遍</strong>（不必写 <span class="mono">projectID: text("project_id")</span>）。一个小约定，省掉了一整类「字段名和列名字符串对不上」的低级错误。而 <span class="mono">Timestamps</span> 那个复用片段更见功力：它把「每张表都要有的创建时间、更新时间」抽成一个对象，各表用 <span class="mono">...Timestamps</span> 展开——<span class="mono">time_created</span> 用 <span class="mono">$default(() =&gt; Date.now())</span> 在插入时自动填、<span class="mono">time_updated</span> 用 <span class="mono">$onUpdate(() =&gt; Date.now())</span> 在每次更新时自动刷新。<strong>把横切所有表的公共结构抽成可复用片段</strong>，正是「代码即 schema」相对裸 SQL 的最大红利：SQL 复制粘贴不了，代码可以。</p>
<p>顺带点明一处底座：L48 讲的「用 Drizzle 定义表、跑迁移」之所以能在 opencode 的 Effect 世界里顺滑运转，靠的是它自建的一层封装——<span class="mono">packages/effect-drizzle-sqlite</span>（含 <span class="mono">effect-sqlite</span> 驱动、迁移器等）与 <span class="mono">packages/effect-sqlite-node</span>。它们把 Drizzle 的 driver、查询构造、迁移都套进 Effect 的 Service/Layer，于是你能像取别的服务一样 <span class="mono">yield*</span> 出一个数据库、用 Effect 的方式管事务与错误。这又是一次「为自己造趁手件」（同 L08 工具箱）——把一个成熟库（Drizzle）包成贴合自家范式（Effect）的样子，复杂的胶水一次写好、藏进包里，上层用起来就只剩干净的 <span class="mono">yield*</span>。</p>

<h2>从 schema 到 SQL：迁移文件怎么来的</h2>
<p>表结构用代码定义好了，但数据库认的是 SQL（<span class="mono">CREATE TABLE</span>、<span class="mono">ALTER TABLE</span>）。这中间的翻译，由 Drizzle 的配套工具 <strong>drizzle-kit</strong> 完成：你改了 <span class="mono">*.sql.ts</span> 里的表定义，drizzle-kit <strong>比对「代码里的新结构」和「上一版结构」的差异</strong>，把差异生成一个 SQL 迁移，落到 <span class="mono">drizzle.config.ts</span> 指定的 <span class="mono">out: "./migration"</span> 目录。整个链条是这样的：</p>
<div class="flow">
  <div class="f-node">改 <span class="mono">*.sql.ts</span><br><small>加一列 / 改一个表</small></div>
  <div class="f-arrow">drizzle-kit 比对差异 →</div>
  <div class="f-node">生成迁移文件<br><small>migration/&lt;时间戳&gt;_xxx.ts</small></div>
  <div class="f-arrow">汇总 →</div>
  <div class="f-node"><span class="mono">migration.gen.ts</span><br><small>按序 import 全部迁移</small></div>
  <div class="f-arrow">启动时 →</div>
  <div class="f-node">迁移运行器执行<br><small>migration.ts apply()</small></div>
</div>
<p>一个迁移文件长得朴素得很——它就是个 <span class="mono">{ id, up(tx) }</span> 对象，<span class="mono">id</span> 是带时间戳的唯一名字、<span class="mono">up</span> 是一段在事务里跑的升级 SQL。例如「给 session 表加一个 path 列」这个迁移，核心就一行：<span class="mono">ALTER TABLE session ADD path text</span>。所有迁移文件被 <span class="mono">migration.gen.ts</span> <strong>按时间戳顺序</strong>汇总成一个数组（opencode 目前有三十多个迁移），这个顺序就是数据库结构的<strong>演化时间线</strong>：</p>
<div class="timeline">
  <div class="tl-item"><div class="tl-time">20260127</div><div class="tl-text">familiar_lady_ursula（初始）</div></div>
  <div class="tl-item"><div class="tl-time">20260312</div><div class="tl-text">session_message_cursor</div></div>
  <div class="tl-item"><div class="tl-time">20260428</div><div class="tl-text">add_session_path（+path 列）</div></div>
  <div class="tl-item"><div class="tl-time">20260604</div><div class="tl-text">event_sourced_session_input（V2 输入箱）</div></div>
  <div class="tl-item"><div class="tl-time">20260612</div><div class="tl-text">project_dir_strategy（最新）</div></div>
</div>
<p>除了这一串「增量」迁移，drizzle-kit 还维护一份特殊的 <span class="mono">schema.gen.ts</span>——它是当前<strong>完整 schema 的「快照」</strong>：一口气 <span class="mono">CREATE TABLE</span> 出所有表的最新结构（两百多行）。增量链 + 完整快照，正是下面「双路径」迁移的两件武器。值得一提的是，<span class="mono">schema.gen.ts</span> 并不是手写维护的，而是 drizzle-kit 随着每次 schema 变更<strong>自动重新生成</strong>的——它永远等于「把所有增量迁移依次跑完后得到的最终结构」。于是同一套表结构有了两种等价表述：一条是<strong>历史视角</strong>的增量链（一笔笔怎么改过来的），一份是<strong>当下视角</strong>的完整快照（现在长什么样）。新库要的是后者（一步到位），老库要的是前者里它还缺的那几笔——双路径之所以成立，正因这两种表述被同时维护、且保证一致。</p>

<h2>双路径迁移：新库套快照，老库补增量</h2>
<p>启动时，<span class="mono">database.ts</span> 先打开/创建那个 <span class="mono">.db</span> 文件、设好一组 SQLite 的 <strong>PRAGMA</strong>（性能与一致性开关），再调 <span class="mono">DatabaseMigration.apply(db)</span> 把库升到最新。<span class="mono">apply</span> 的逻辑就是那条核心洞见——先看库里有没有表，分两条路走：</p>
<div class="cols">
  <div class="col"><h4>全新空库 · 套快照</h4><p>库里一张表都没有 → <strong>直接跑 <span class="mono">schema.gen</span> 那份完整快照</strong>，一步建好所有最新表；然后建一张 <span class="mono">migration</span> 日志表，把<strong>全部三十多个迁移一次性记成「已完成」</strong>。新用户绝不重放历史——一步到位。</p></div>
  <div class="col"><h4>已有老库 · 补增量</h4><p>库里已有 <span class="mono">session</span> 表 → 走 <span class="mono">applyOnly</span>：读出 <span class="mono">migration</span> 日志里<strong>已完成的迁移 id 集合</strong>，遍历全部迁移，<strong>只补跑那些还没记过的</strong>，每跑一个就在日志里记一笔。老用户只补差量——平滑升级。</p></div>
</div>
<p>这条 <span class="mono">migration</span> 日志表（就两列：<span class="mono">id</span> + <span class="mono">time_completed</span>）是整套系统的「记忆」：它记着「哪些迁移已经跑过了」，于是迁移天然<strong>幂等</strong>——跑过的不再跑，重启一百次也不会把同一个 <span class="mono">ALTER TABLE</span> 执行两遍。而且每个迁移都<strong>裹在一个事务里</strong>（<span class="mono">db.transaction</span>）：升级 SQL 和「记一笔日志」要么一起成功、要么一起回滚，绝不会出现「表改了一半、日志却没记」的撕裂状态。整个 <span class="mono">apply</span> 还被一个 <span class="mono">Semaphore(1)</span> 信号量串行化——<strong>同一时刻只允许一个迁移流程在跑</strong>，杜绝多进程同时升级互相打架。把这套「幂等 + 事务 + 串行」的纪律走一遍：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">取 Semaphore 许可（同一时刻仅一个迁移流程）</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">查 sqlite_master：库里有哪些表？</span></div>
  <div class="t-row"><span class="t-num">3a</span><span class="t-txt">无 session 表且空库 → 跑 schema.gen 快照 + 全部迁移记「已完成」</span></div>
  <div class="t-row"><span class="t-num">3b</span><span class="t-txt">有 session 表 → applyOnly：逐个补跑「日志里没有」的迁移（各裹事务）</span></div>
  <div class="t-row"><span class="t-num">!</span><span class="t-txt">非空但没 session 表 → die「库非空却无 session 表」（防误伤陌生库）</span></div>
</div>
<p>顺带一提开头那组 PRAGMA，它们是为「一个本地、单用户的 agent 数据库」量身调的：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">journal_mode=WAL</div><div class="c-txt">预写日志：读写可并发、更耐崩溃</div></div>
  <div class="cell"><div class="c-tag">synchronous=NORMAL</div><div class="c-txt">在数据安全与写入速度间折中</div></div>
  <div class="cell"><div class="c-tag">foreign_keys=ON</div><div class="c-txt">让上面那些 references cascade 真正生效</div></div>
  <div class="cell"><div class="c-tag">busy_timeout=5000</div><div class="c-txt">锁忙时等 5 秒再报错，而非立刻失败</div></div>
  <div class="cell"><div class="c-tag">cache_size=-64000</div><div class="c-txt">约 64 MB 页缓存（负数=按 KB 计）</div></div>
  <div class="cell"><div class="c-tag">wal_checkpoint(PASSIVE)</div><div class="c-txt">启动时温和地把 WAL 合并回主库</div></div>
</div>
<p>这些都不是花哨功能，而是让一个嵌入式库在真实使用里<strong>跑得稳、扛得住并发、崩了能恢复</strong>的务实配置。其中 <span class="mono">WAL</span>（Write-Ahead Logging）尤其关键：传统的回滚日志模式下读写互斥，而 WAL 让「读」和「写」可以同时进行——这对一个 agent 边把消息流式写进库、TUI 边从库里读出来渲染的场景，几乎是刚需。而 <span class="mono">foreign_keys=ON</span> 这一行也不可省：SQLite 出于历史原因<strong>默认不强制外键</strong>，必须显式打开，上一节那些 <span class="mono">onDelete:"cascade"</span> 才会真的级联生效——否则它们只是一句被无视的注释。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观视角</div>
  <p>这一课讲清了 opencode 持久化的地基——存储底座与结构演化：</p>
  <ul>
    <li><strong>SQLite 当底座</strong>：嵌入式、单文件（<span class="mono">opencode.db</span>，按发布渠道分 <span class="mono">opencode-&lt;channel&gt;.db</span>）关系型库；<span class="mono">database.ts</span> 开库 + 设 PRAGMA（WAL / synchronous NORMAL / foreign_keys ON / busy_timeout / cache_size）+ apply 迁移。</li>
    <li><strong>Drizzle「代码即 schema」</strong>：表用 <span class="mono">sqliteTable</span> 在 <span class="mono">*.sql.ts</span> 里定义、与领域代码同处；列工具箱 text/integer/real、<span class="mono">json</span> 模式 + <span class="mono">$type</span> 品牌、<span class="mono">references cascade</span>、<span class="mono">Timestamps</span> 复用片段。约定列名 <strong>snake_case</strong>=字段名直接当列名、免重写。</li>
    <li><strong>迁移从 schema 自动生成</strong>：drizzle-kit 比对差异 → SQL 迁移文件（TS <span class="mono">{id, up(tx)}</span>）→ <span class="mono">migration.gen.ts</span> 按序汇总（三十多个）+ <span class="mono">schema.gen.ts</span> 完整快照。</li>
    <li><strong>双路径 apply</strong>（<span class="mono">migration.ts</span>）：新空库→套 <span class="mono">schema.gen</span> 快照 + 全部迁移记「已完成」（不重放）；老库→<span class="mono">applyOnly</span> 只补跑日志里没有的迁移。<span class="mono">migration</span> 日志表(id+time_completed)给幂等；各迁移裹事务；<span class="mono">Semaphore(1)</span> 串行。</li>
  </ul>
  <p>地基铺好了——SQLite 这个文件柜、Drizzle 画的图纸、迁移这套装修日志。下一课（L49）就走进柜子，看<strong>具体存了哪些核心表</strong>：session（会话）、message/part（V1 消息）、session_message（V2 消息）、session_input（V2 durable 输入箱）、session_context_epoch（M5 上下文纪元的落盘）——以及它们之间用外键织成的关系网。M9 后续还会讲 V1 文件存储到 V2 SQLite 的数据迁移（L50）、以及压缩/快照/revert（L51）。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p><span class="mono">migration.ts</span> 的 <span class="mono">apply</span> 把「双路径」写得干净利落（简化自源码）：</p>
  <pre class="code"><span class="kw">export function</span> <span class="fn">apply</span>(db) {
  <span class="kw">return</span> lock.<span class="fn">withPermit</span>(Effect.<span class="fn">gen</span>(<span class="kw">function*</span> () {   <span class="cm">// Semaphore(1) 串行</span>
    <span class="kw">const</span> tables = <span class="kw">yield*</span> db.<span class="fn">all</span>(
      sql<span class="st">`SELECT name FROM sqlite_master WHERE type='table' ...`</span>)
    <span class="cm">// 路径 B：已有 session 表 → 只补增量</span>
    <span class="kw">if</span> (tables.<span class="fn">some</span>((t) =&gt; t.name === <span class="st">"session"</span>))
      <span class="kw">return yield*</span> <span class="fn">applyOnly</span>(db, migrations)
    <span class="cm">// 防呆：非空却无 session 表 → 这不是我的库，别乱动</span>
    <span class="kw">if</span> (tables.length &gt; 0)
      <span class="kw">return yield*</span> Effect.<span class="fn">die</span>(<span class="st">"Database is not empty and has no session table"</span>)
    <span class="cm">// 路径 A：全新空库 → 套快照 + 全部迁移记「已完成」</span>
    <span class="kw">yield*</span> db.<span class="fn">transaction</span>((tx) =&gt; Effect.<span class="fn">gen</span>(<span class="kw">function*</span> () {
      <span class="kw">yield*</span> schema.<span class="fn">up</span>(tx)                       <span class="cm">// schema.gen 完整快照</span>
      <span class="kw">yield*</span> tx.<span class="fn">run</span>(sql<span class="st">`CREATE TABLE migration (id TEXT PRIMARY KEY, ...)`</span>)
      <span class="kw">yield*</span> Effect.<span class="fn">forEach</span>(migrations, (m) =&gt;        <span class="cm">// 全标记已完成</span>
        tx.<span class="fn">run</span>(sql<span class="st">`INSERT INTO migration (id, time_completed) VALUES (${m.id}, ...)`</span>))
    }))
  }))
}</pre>
  <p>最值得品的，是那句 <span class="mono">if (tables.length &gt; 0) die(...)</span> 的<strong>防呆</strong>：如果库里<strong>有表、却偏偏没有 <span class="mono">session</span> 表</strong>，opencode 不会贸然往里建表，而是直接<strong>报错退出</strong>。为什么这么谨慎？因为「有表但不是我认识的结构」极可能意味着——你把 <span class="mono">OPENCODE_DB</span> 指错了文件、指到了别的程序的数据库上。这时候<strong>「拒绝动手」远比「自作主张建表」安全</strong>：宁可清楚地报一句「这库非空却没有 session 表」，也不要在一个陌生的库里乱建表、把人家的数据搅乱。这正是好的迁移系统该有的敬畏——<strong>它清楚自己只该升级「自己的」库，对来历不明的库宁停勿乱。</strong>还有那个「新库把所有迁移记成已完成」的小动作，背后是同一种克制：<strong>快照已经包含了所有历史迁移的累积结果，再重放一遍既浪费又危险（老迁移可能依赖早已不存在的中间状态）</strong>，所以记个账、跳过它们，才是对的。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>SQLite + Drizzle 是持久化地基</strong>：SQLite=嵌入式单文件关系库（<span class="mono">opencode.db</span>）；Drizzle=类型安全、「代码即 schema」的 ORM。本课讲地基（schema 定义 + 迁移），具体表见 L49。</li>
    <li><strong>代码即 schema</strong>：<span class="mono">sqliteTable</span> 在 <span class="mono">*.sql.ts</span> 与领域代码同处定义；列工具箱 text/integer/real、<span class="mono">json</span> 模式 + <span class="mono">$type</span> 品牌 ID、<span class="mono">references {onDelete:"cascade"}</span>、<span class="mono">Timestamps</span> 复用片段。约定 <strong>snake_case 列名</strong>=字段名直接当列名、免把列名当字符串重写。</li>
    <li><strong>迁移自动生成</strong>：drizzle-kit 比对 schema 差异 → SQL 迁移（TS <span class="mono">{id, up(tx)}</span>，如 <span class="mono">ALTER TABLE session ADD path</span>）→ <span class="mono">migration.gen.ts</span> 按时间戳序汇总（三十多个）+ <span class="mono">schema.gen.ts</span> 完整快照。</li>
    <li><strong>双路径 apply</strong>：新空库→直接套 <span class="mono">schema.gen</span> 快照 + 全部迁移一次记「已完成」（不重放，又快又安全）；老库→<span class="mono">applyOnly</span> 只补跑日志里没有的迁移（平滑升级）。非空却无 session 表→<strong>报错退出</strong>（防误伤陌生库）。</li>
    <li><strong>幂等 + 事务 + 串行</strong>：<span class="mono">migration</span> 日志表(id+time_completed)记已跑过的→幂等；每个迁移裹 <span class="mono">db.transaction</span>（升级 SQL 与记账同生共死）；<span class="mono">Semaphore(1)</span> 串行化（同时只一个迁移流程）。PRAGMA：WAL / synchronous NORMAL / foreign_keys ON / busy_timeout / cache_size。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">The first eight parts were all about the agent while it's "alive": how it talks to the model (M6), calls tools (M7), gets configured into a role (M8). But an agent can't live forever—processes exit, machines reboot, you close the terminal and come back tomorrow. So <strong>where do the sessions it ran, the messages back and forth, the context it accrued, get stored?</strong> That's what M9 "Persistence and Storage" answers. This lesson is M9's foundation: opencode uses <strong>SQLite</strong> (an embedded, single-file relational database) as the storage base, and <strong>Drizzle</strong> (a type-safe TypeScript ORM) to write out the database's "table structure" as code. This lesson isn't about which specific tables are stored (that's the next lesson, L49) but specifically about <strong>two foundational things</strong>: ① how the table structure is defined with Drizzle in a "code-as-schema" way; ② when the structure needs to evolve (add a column, change a table), how that <strong>database migration</strong> system safely upgrades an old DB to the new structure.</p>
<p>The insight to take from this lesson hides in opencode's migration system—it walks a <strong>"dual path"</strong>: for a <strong>brand-new empty database</strong>, it won't foolishly replay all thirty-some historical migrations from scratch, but <strong>directly applies the current latest full schema snapshot</strong>, then marks those thirty-some migrations <strong>all as "completed"</strong>; only for an <strong>existing old database</strong> does it <strong>backfill, one by one, the migrations not yet run</strong>. This "snapshot for new, increment for old" design is exceptionally clever: it makes a new user's first launch fast and clean (the latest structure built in one shot), and lets an old user's DB smoothly upgrade bit by bit without ever losing data. Grasp this and you'll understand "how software, while constantly changing its data structures, neither burdens new users nor abandons old ones"—the core dilemma every long-evolving stateful software inevitably faces.</p>

<div class="card analogy">
  <div class="tag">🗄️ Analogy</div>
  Picture SQLite as a <strong>file cabinet built into your own desk</strong>—not renting a warehouse outside (that's a database like PostgreSQL that runs a separate server), but right at hand, the whole cabinet being <strong>one file</strong> (<span class="mono">opencode.db</span>), carried along with the software. And Drizzle's schema is this cabinet's <strong>"drawer blueprint"</strong>: what each drawer (table) is called, how many compartments (columns) it has, what type goes in each—all drawn clear in code. The finest part is <strong>migrations</strong>—like the cabinet's <strong>"renovation log"</strong>: "Mar 12, add a path compartment to the session drawer," "Apr 28, add an archived compartment"… each modification numbered by date, logged. A <strong>brand-new empty cabinet</strong> arrives? No need to redo every historical modification—just build it once from the <strong>latest blueprint</strong>, then tick "✓ done" on all historical modifications in the log. A <strong>cabinet used for half a year</strong>? Open its log, see which modifications haven't been done, <strong>do only those</strong>—not one extra, not one missed.
</div>

<h2>Code as schema: defining tables with Drizzle</h2>
<p>opencode's table structure isn't written in a pile of <span class="mono">.sql</span> files but <strong>defined in TypeScript code</strong>. See <span class="mono">drizzle.config.ts</span>: it points the schema source at <span class="mono">["./src/**/*.sql.ts", "./src/**/sql.ts"]</span>—meaning <strong>each domain's table structure sits with that domain's code</strong> (session's tables in <span class="mono">session/sql.ts</span>, project's in <span class="mono">project/sql.ts</span>), not centralized in some corner far from the business. A table is just one <span class="mono">sqliteTable("name", { columns }, (t) =&gt; [indices])</span>. Drizzle gives a compact "column-definition toolkit":</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">text() / integer() / real()</div><div class="c-txt">three base SQLite types: text / integer / float</div></div>
  <div class="cell"><div class="c-tag">text({ mode: "json" }).$type&lt;T&gt;()</div><div class="c-txt">store an object/array as JSON in a column, annotated with its TS type</div></div>
  <div class="cell"><div class="c-tag">.$type&lt;BrandedID&gt;()</div><div class="c-txt">tag a column with a "branded ID" type, compile-time preventing using a SessionID as a MessageID</div></div>
  <div class="cell"><div class="c-tag">.references(() =&gt; X.id, {onDelete:"cascade"})</div><div class="c-txt">foreign key: parent row deleted, child rows cascade-deleted (the DB guarantees consistency for you)</div></div>
  <div class="cell"><div class="c-tag">.notNull() / .default(0) / .primaryKey()</div><div class="c-txt">not-null constraint / default value / primary key</div></div>
  <div class="cell"><div class="c-tag">Timestamps (reusable fragment)</div><div class="c-txt"><span class="mono">time_created</span>(filled on insert) + <span class="mono">time_updated</span>(auto-refreshed on update), defined once, spread-reused across tables</div></div>
</div>
<p>There's a <strong>naming convention</strong> running through all of opencode worth pointing out specially: column names are uniformly <strong>snake_case</strong> (e.g. <span class="mono">project_id</span>, <span class="mono">time_created</span>), not camelCase. Why? Because Drizzle by default <strong>takes the field name directly as the column name</strong>—write <span class="mono">project_id: text()</span> and the column is <span class="mono">project_id</span>, <strong>no need to rewrite the column name as a string again</strong> (no <span class="mono">projectID: text("project_id")</span>). A small convention eliminates a whole class of "field name and column-name string don't match" low-level bugs. And that <span class="mono">Timestamps</span> reusable fragment shows even more craft: it abstracts "the created/updated time every table needs" into an object, each table spreads it via <span class="mono">...Timestamps</span>—<span class="mono">time_created</span> auto-fills on insert via <span class="mono">$default(() =&gt; Date.now())</span>, <span class="mono">time_updated</span> auto-refreshes on every update via <span class="mono">$onUpdate(() =&gt; Date.now())</span>. <strong>Abstracting common structure that cuts across all tables into a reusable fragment</strong> is exactly "code-as-schema"'s biggest dividend over raw SQL: SQL can't be reused, code can.</p>
<p>One foundation worth naming: L48's "define tables with Drizzle, run migrations" runs smoothly in opencode's Effect world thanks to a self-built wrapper layer—<span class="mono">packages/effect-drizzle-sqlite</span> (with an <span class="mono">effect-sqlite</span> driver, a migrator, etc.) and <span class="mono">packages/effect-sqlite-node</span>. They wrap Drizzle's driver, query building, and migrations into Effect's Service/Layer, so you can <span class="mono">yield*</span> a database like any other service and manage transactions and errors the Effect way. This is another "build a handy part for yourself" (like L08's toolbox)—wrapping a mature library (Drizzle) into a shape that fits the house paradigm (Effect); the complex glue is written once, hidden in the package, and the upper layer is left with just a clean <span class="mono">yield*</span>.</p>

<h2>From schema to SQL: where migration files come from</h2>
<p>The table structure is defined in code, but the database speaks SQL (<span class="mono">CREATE TABLE</span>, <span class="mono">ALTER TABLE</span>). The translation between is done by Drizzle's companion tool <strong>drizzle-kit</strong>: you change a table definition in <span class="mono">*.sql.ts</span>, drizzle-kit <strong>diffs "the new structure in code" against "the previous structure"</strong>, generates the diff into a SQL migration, dropped into the <span class="mono">out: "./migration"</span> directory <span class="mono">drizzle.config.ts</span> specifies. The whole chain is:</p>
<div class="flow">
  <div class="f-node">change <span class="mono">*.sql.ts</span><br><small>add a column / change a table</small></div>
  <div class="f-arrow">drizzle-kit diffs →</div>
  <div class="f-node">generate migration file<br><small>migration/&lt;timestamp&gt;_xxx.ts</small></div>
  <div class="f-arrow">collect →</div>
  <div class="f-node"><span class="mono">migration.gen.ts</span><br><small>import all migrations in order</small></div>
  <div class="f-arrow">at startup →</div>
  <div class="f-node">migration runner executes<br><small>migration.ts apply()</small></div>
</div>
<p>A migration file looks plain indeed—it's just a <span class="mono">{ id, up(tx) }</span> object, <span class="mono">id</span> a timestamped unique name, <span class="mono">up</span> a stretch of upgrade SQL run in a transaction. For example the "add a path column to the session table" migration's core is one line: <span class="mono">ALTER TABLE session ADD path text</span>. All migration files are collected by <span class="mono">migration.gen.ts</span> <strong>in timestamp order</strong> into an array (opencode currently has thirty-some), and this order is the database structure's <strong>evolution timeline</strong>:</p>
<div class="timeline">
  <div class="tl-item"><div class="tl-time">20260127</div><div class="tl-text">familiar_lady_ursula (initial)</div></div>
  <div class="tl-item"><div class="tl-time">20260312</div><div class="tl-text">session_message_cursor</div></div>
  <div class="tl-item"><div class="tl-time">20260428</div><div class="tl-text">add_session_path (+path column)</div></div>
  <div class="tl-item"><div class="tl-time">20260604</div><div class="tl-text">event_sourced_session_input (V2 inbox)</div></div>
  <div class="tl-item"><div class="tl-time">20260612</div><div class="tl-text">project_dir_strategy (latest)</div></div>
</div>
<p>Besides this string of "incremental" migrations, drizzle-kit also maintains a special <span class="mono">schema.gen.ts</span>—it's the current <strong>full schema "snapshot"</strong>: <span class="mono">CREATE TABLE</span>-ing all tables' latest structure in one go (two-hundred-some lines). The incremental chain + the full snapshot are exactly the two weapons of the "dual-path" migration below. Worth noting, <span class="mono">schema.gen.ts</span> isn't hand-maintained but <strong>auto-regenerated</strong> by drizzle-kit on each schema change—it always equals "the final structure after running all incremental migrations in sequence." So the same table structure has two equivalent expressions: one a <strong>historical view</strong>'s incremental chain (how it was changed step by step), one a <strong>present view</strong>'s full snapshot (what it looks like now). A new DB wants the latter (one shot), an old DB wants the few of the former it still lacks—the dual path works precisely because both expressions are maintained simultaneously and guaranteed consistent.</p>

<h2>Dual-path migration: snapshot for new, increment for old</h2>
<p>At startup, <span class="mono">database.ts</span> first opens/creates that <span class="mono">.db</span> file, sets a group of SQLite <strong>PRAGMAs</strong> (performance and consistency switches), then calls <span class="mono">DatabaseMigration.apply(db)</span> to bring the DB to latest. <span class="mono">apply</span>'s logic is that core insight—first check whether the DB has tables, then split into two paths:</p>
<div class="cols">
  <div class="col"><h4>brand-new empty DB · apply snapshot</h4><p>not a single table in the DB → <strong>run <span class="mono">schema.gen</span>'s full snapshot directly</strong>, building all latest tables in one step; then create a <span class="mono">migration</span> journal table, marking <strong>all thirty-some migrations as "completed" at once</strong>. New users never replay history—done in one shot.</p></div>
  <div class="col"><h4>existing old DB · backfill increments</h4><p>the DB already has a <span class="mono">session</span> table → take <span class="mono">applyOnly</span>: read the <strong>set of completed migration ids</strong> from the <span class="mono">migration</span> journal, iterate all migrations, <strong>backfill only those not yet recorded</strong>, logging each one run. Old users backfill only the delta—smooth upgrade.</p></div>
</div>
<p>This <span class="mono">migration</span> journal table (just two columns: <span class="mono">id</span> + <span class="mono">time_completed</span>) is the whole system's "memory": it records "which migrations have run," so migration is naturally <strong>idempotent</strong>—run ones never rerun, restart a hundred times and the same <span class="mono">ALTER TABLE</span> won't execute twice. And each migration is <strong>wrapped in a transaction</strong> (<span class="mono">db.transaction</span>): the upgrade SQL and "log an entry" either both succeed or both roll back, never a torn state of "table half-changed, journal not recorded." The whole <span class="mono">apply</span> is also serialized by a <span class="mono">Semaphore(1)</span>—<strong>only one migration flow may run at a time</strong>, preventing multiple processes upgrading at once and fighting. Walking through this "idempotent + transactional + serial" discipline:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">acquire the Semaphore permit (only one migration flow at a time)</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">query sqlite_master: which tables does the DB have?</span></div>
  <div class="t-row"><span class="t-num">3a</span><span class="t-txt">no session table and empty DB → run schema.gen snapshot + record all migrations "completed"</span></div>
  <div class="t-row"><span class="t-num">3b</span><span class="t-txt">has session table → applyOnly: backfill migrations "not in journal" one by one (each in a transaction)</span></div>
  <div class="t-row"><span class="t-num">!</span><span class="t-txt">non-empty but no session table → die "DB non-empty yet has no session table" (guard against a stranger DB)</span></div>
</div>
<p>A note on that PRAGMA group at the start—they're tailored for "a local, single-user agent database":</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">journal_mode=WAL</div><div class="c-txt">write-ahead log: reads and writes can be concurrent, more crash-resistant</div></div>
  <div class="cell"><div class="c-tag">synchronous=NORMAL</div><div class="c-txt">a compromise between data safety and write speed</div></div>
  <div class="cell"><div class="c-tag">foreign_keys=ON</div><div class="c-txt">makes those references cascade above actually take effect</div></div>
  <div class="cell"><div class="c-tag">busy_timeout=5000</div><div class="c-txt">wait 5s when the lock is busy before erroring, not failing instantly</div></div>
  <div class="cell"><div class="c-tag">cache_size=-64000</div><div class="c-txt">~64 MB page cache (negative = counted in KB)</div></div>
  <div class="cell"><div class="c-tag">wal_checkpoint(PASSIVE)</div><div class="c-txt">gently merge the WAL back into the main DB at startup</div></div>
</div>
<p>None of these are fancy features but pragmatic config to make an embedded DB <strong>run stably, withstand concurrency, recover from crashes</strong> in real use. Among them <span class="mono">WAL</span> (Write-Ahead Logging) is especially key: under the traditional rollback-journal mode reads and writes are mutually exclusive, while WAL lets "read" and "write" proceed simultaneously—near-essential for a scenario where an agent streams messages into the DB while the TUI reads from the DB to render. And the <span class="mono">foreign_keys=ON</span> line can't be omitted either: SQLite for historical reasons <strong>doesn't enforce foreign keys by default</strong> and must explicitly turn them on, so those <span class="mono">onDelete:"cascade"</span> from the last section actually cascade—otherwise they're just an ignored comment.</p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>This lesson clarifies the foundation of opencode persistence—the storage base and structure evolution:</p>
  <ul>
    <li><strong>SQLite as base</strong>: embedded, single-file (<span class="mono">opencode.db</span>, split by release channel into <span class="mono">opencode-&lt;channel&gt;.db</span>) relational DB; <span class="mono">database.ts</span> opens the DB + sets PRAGMAs (WAL / synchronous NORMAL / foreign_keys ON / busy_timeout / cache_size) + applies migrations.</li>
    <li><strong>Drizzle "code as schema"</strong>: tables defined with <span class="mono">sqliteTable</span> in <span class="mono">*.sql.ts</span>, co-located with domain code; column toolkit text/integer/real, <span class="mono">json</span> mode + <span class="mono">$type</span> branding, <span class="mono">references cascade</span>, <span class="mono">Timestamps</span> reusable fragment. Convention: <strong>snake_case</strong> column names = field name directly as column name, no rewriting.</li>
    <li><strong>migrations auto-generated from schema</strong>: drizzle-kit diffs → SQL migration files (TS <span class="mono">{id, up(tx)}</span>) → <span class="mono">migration.gen.ts</span> collected in order (thirty-some) + <span class="mono">schema.gen.ts</span> full snapshot.</li>
    <li><strong>dual-path apply</strong> (<span class="mono">migration.ts</span>): new empty DB → apply <span class="mono">schema.gen</span> snapshot + mark all migrations "completed" (no replay); old DB → <span class="mono">applyOnly</span> backfills only migrations not in the journal. The <span class="mono">migration</span> journal table (id+time_completed) gives idempotency; each migration wrapped in a transaction; <span class="mono">Semaphore(1)</span> serializes.</li>
  </ul>
  <p>The foundation is laid—SQLite the file cabinet, the blueprint Drizzle draws, the renovation log of migrations. The next lesson (L49) walks into the cabinet to see <strong>which core tables are actually stored</strong>: session, message/part (V1 messages), session_message (V2 messages), session_input (V2 durable inbox), session_context_epoch (M5 context epoch on disk)—and the web of relationships woven among them by foreign keys. M9 will further cover data migration from V1 file storage to V2 SQLite (L50), and compaction/snapshots/revert (L51).</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p><span class="mono">migration.ts</span>'s <span class="mono">apply</span> writes the "dual path" cleanly (simplified from source):</p>
  <pre class="code"><span class="kw">export function</span> <span class="fn">apply</span>(db) {
  <span class="kw">return</span> lock.<span class="fn">withPermit</span>(Effect.<span class="fn">gen</span>(<span class="kw">function*</span> () {   <span class="cm">// Semaphore(1) serial</span>
    <span class="kw">const</span> tables = <span class="kw">yield*</span> db.<span class="fn">all</span>(
      sql<span class="st">`SELECT name FROM sqlite_master WHERE type='table' ...`</span>)
    <span class="cm">// Path B: has session table → backfill increments only</span>
    <span class="kw">if</span> (tables.<span class="fn">some</span>((t) =&gt; t.name === <span class="st">"session"</span>))
      <span class="kw">return yield*</span> <span class="fn">applyOnly</span>(db, migrations)
    <span class="cm">// guard: non-empty yet no session table → not my DB, don't touch</span>
    <span class="kw">if</span> (tables.length &gt; 0)
      <span class="kw">return yield*</span> Effect.<span class="fn">die</span>(<span class="st">"Database is not empty and has no session table"</span>)
    <span class="cm">// Path A: brand-new empty DB → snapshot + mark all migrations "completed"</span>
    <span class="kw">yield*</span> db.<span class="fn">transaction</span>((tx) =&gt; Effect.<span class="fn">gen</span>(<span class="kw">function*</span> () {
      <span class="kw">yield*</span> schema.<span class="fn">up</span>(tx)                       <span class="cm">// schema.gen full snapshot</span>
      <span class="kw">yield*</span> tx.<span class="fn">run</span>(sql<span class="st">`CREATE TABLE migration (id TEXT PRIMARY KEY, ...)`</span>)
      <span class="kw">yield*</span> Effect.<span class="fn">forEach</span>(migrations, (m) =&gt;        <span class="cm">// mark all completed</span>
        tx.<span class="fn">run</span>(sql<span class="st">`INSERT INTO migration (id, time_completed) VALUES (${m.id}, ...)`</span>))
    }))
  }))
}</pre>
  <p>What's most worth savoring is that <span class="mono">if (tables.length &gt; 0) die(...)</span> <strong>guard</strong>: if the DB <strong>has tables yet lacks a <span class="mono">session</span> table</strong>, opencode won't rashly build tables into it but <strong>errors out directly</strong>. Why so cautious? Because "has tables but not a structure I recognize" very likely means—you pointed <span class="mono">OPENCODE_DB</span> at the wrong file, at some other program's database. Here <strong>"refuse to act" is far safer than "build tables on my own initiative"</strong>: better to clearly report "this DB is non-empty yet has no session table" than to scatter tables into a stranger DB and scramble its data. This is exactly the reverence a good migration system should have—<strong>it knows it should only upgrade "its own" DB, and for a DB of unknown origin would rather stop than meddle.</strong> And that little "new DB marks all migrations completed" act comes from the same restraint: <strong>the snapshot already contains the cumulative result of all historical migrations, replaying them again is both wasteful and dangerous (an old migration may depend on an intermediate state that no longer exists)</strong>, so logging them and skipping is the right call.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>SQLite + Drizzle are the persistence foundation</strong>: SQLite = embedded single-file relational DB (<span class="mono">opencode.db</span>); Drizzle = type-safe, "code-as-schema" ORM. This lesson covers the foundation (schema definition + migration), specific tables in L49.</li>
    <li><strong>Code as schema</strong>: <span class="mono">sqliteTable</span> defined in <span class="mono">*.sql.ts</span> co-located with domain code; column toolkit text/integer/real, <span class="mono">json</span> mode + <span class="mono">$type</span> branded ID, <span class="mono">references {onDelete:"cascade"}</span>, <span class="mono">Timestamps</span> reusable fragment. Convention: <strong>snake_case column names</strong> = field name directly as column name, no rewriting the column name as a string.</li>
    <li><strong>migrations auto-generated</strong>: drizzle-kit diffs schema → SQL migration (TS <span class="mono">{id, up(tx)}</span>, e.g. <span class="mono">ALTER TABLE session ADD path</span>) → <span class="mono">migration.gen.ts</span> collected in timestamp order (thirty-some) + <span class="mono">schema.gen.ts</span> full snapshot.</li>
    <li><strong>dual-path apply</strong>: new empty DB → apply <span class="mono">schema.gen</span> snapshot directly + mark all migrations "completed" at once (no replay, fast and safe); old DB → <span class="mono">applyOnly</span> backfills only migrations not in the journal (smooth upgrade). Non-empty yet no session table → <strong>error out</strong> (guard against a stranger DB).</li>
    <li><strong>idempotent + transactional + serial</strong>: the <span class="mono">migration</span> journal table (id+time_completed) records what's run → idempotent; each migration wrapped in <span class="mono">db.transaction</span> (upgrade SQL and logging live or die together); <span class="mono">Semaphore(1)</span> serializes (only one migration flow at a time). PRAGMAs: WAL / synchronous NORMAL / foreign_keys ON / busy_timeout / cache_size.</li>
  </ul>
</div>
""",
}
LESSON_49 = {
    "zh": r"""
<p class="lead">上一课我们打造了文件柜（SQLite）、学会了画图纸（Drizzle）、读懂了装修日志（迁移）。这一课，我们<strong>拉开抽屉，看 opencode 到底存了哪些核心表</strong>，以及它们之间用外键织成的关系网。这些表定义在各领域的 <span class="mono">*/sql.ts</span> 里（主要是 <span class="mono">session/sql.ts</span>），是整个 agent 状态的<strong>落盘形态</strong>——你和 agent 的每一次对话、每一条消息、每一份上下文，最终都变成这些表里的一行行记录。spec 点名的六张核心表是：<span class="mono">session</span>（会话）、<span class="mono">message</span>/<span class="mono">part</span>（V1 消息/片段）、<span class="mono">session_message</span>（V2 消息）、<span class="mono">session_input</span>（V2 输入箱）、<span class="mono">session_context_epoch</span>（上下文纪元）。读懂这张表网，你就拿到了理解 opencode「记忆」如何组织的钥匙。</p>
<p>这一课有三个层层递进的洞见。第一，<strong><span class="mono">session</span> 是整张表网的「中枢」</strong>：几乎每张表都通过外键指回 session（或经 project→session），而且这些外键几乎都带 <span class="mono">onDelete:"cascade"</span>——删掉一个 session，它名下的消息、片段、输入、纪元、待办会<strong>像拔起一棵树连根带走所有枝叶</strong>，数据库自动保证不留孤儿。第二，<strong>V1 与 V2 两代消息模型在同一个库里并存</strong>：<span class="mono">message</span>/<span class="mono">part</span> 是老的 V1 模型、<span class="mono">session_message</span> 是新的 V2 模型——这种「新旧同堂」不是混乱，而是为了平滑迁移（下一课 L50 的主题）。第三，<strong>到处可见的 <span class="mono">seq</span>（序号）撑起了「顺序」与「不重不漏」</strong>：V2 的消息、输入、事件都靠单调递增的序号排定先后、靠唯一索引防止重复。读懂这三点，你看到的就不再是一堆孤立的表，而是一个<strong>以 session 为根、用外键和序号精心组织的状态树</strong>。</p>

<div class="card analogy">
  <div class="tag">🗂️ 生活类比</div>
  把这套表网想象成一个<strong>档案系统</strong>。<span class="mono">project</span> 是<strong>最外层的项目档案盒</strong>，<span class="mono">session</span> 是盒里的<strong>一份份「案卷」</strong>（每次对话一卷）。一份案卷里，夹着它的<strong>往来信件</strong>（message）、每封信的<strong>分页内容</strong>（part）、新格式的<strong>会议纪要</strong>（session_message）、还没正式归档的<strong>待处理来件</strong>（session_input），以及一张<strong>「当前背景速览卡」</strong>（context_epoch）。最关键的是：所有这些都<strong>夹在案卷这个「母夹子」里</strong>——你把整份案卷抽走销毁（删 session），夹在里面的信件、附页、来件、速览卡<strong>一张不留地跟着消失</strong>（cascade 级联删除），绝不会有「信还在、案卷没了」的孤魂野鬼。而每封信、每条纪要都按<strong>收发流水号</strong>（seq）排着，谁先谁后、有没有漏号，一目了然。
</div>

<h2>session：整张表网的中枢</h2>
<p><span class="mono">session</span> 表是一切的根。它的列出奇地多，但别被吓到——这恰恰说明一次「会话」承载了多少信息：它是谁、属于哪个项目、用什么模型和权限在跑、花了多少 token、几时创建几时归档。把这些列大致分成几组，每组回答关于一次会话的一个问题：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">身份与归属</div><div class="c-txt"><span class="mono">id</span>(主键)、<span class="mono">project_id</span>(→project,cascade)、<span class="mono">workspace_id</span>、<span class="mono">parent_id</span>(自指→父会话)、<span class="mono">slug</span>、<span class="mono">directory</span>/<span class="mono">path</span></div></div>
  <div class="cell"><div class="c-tag">展示</div><div class="c-txt"><span class="mono">title</span>、<span class="mono">version</span>、<span class="mono">share_url</span>、<span class="mono">summary_*</span>(改动行数/文件/diff)</div></div>
  <div class="cell"><div class="c-tag">用量统计</div><div class="c-txt"><span class="mono">cost</span>、<span class="mono">tokens_input/output/reasoning/cache_read/cache_write</span></div></div>
  <div class="cell"><div class="c-tag">运行状态</div><div class="c-txt"><span class="mono">agent</span>、<span class="mono">model</span>(JSON)、<span class="mono">permission</span>(JSON,L41 Ruleset)、<span class="mono">revert</span>(JSON)</div></div>
  <div class="cell"><div class="c-tag">时间</div><div class="c-txt"><span class="mono">...Timestamps</span>、<span class="mono">time_compacting</span>、<span class="mono">time_archived</span></div></div>
</div>
<p>注意 <span class="mono">parent_id</span> 那个<strong>自指列</strong>：一个 session 可以是另一个 session 的子会话——这正是 M4 里 agent 派生子任务（subagent）时，子会话挂在父会话名下的落盘方式。但要留神：<span class="mono">parent_id</span> 只是一个<strong>带索引的普通列、并非强制外键</strong>（源码里它没有 <span class="mono">.references()</span>），所以删掉父会话<strong>不会</strong>级联删掉子会话。而其它表则大多通过<strong>带 cascade 的外键</strong>指回 session。把这张关系网铺开看：</p>
<table class="t">
  <tr><th>父表</th><th>子表</th><th>关系（是否级联）</th></tr>
  <tr><td>project</td><td>session（project_id）</td><td>一个项目 N 个会话 · cascade</td></tr>
  <tr><td>session</td><td>session（parent_id）</td><td>父会话 N 个子会话 · <strong>自指索引、非外键、不级联</strong></td></tr>
  <tr><td>session</td><td>message → part</td><td>V1：会话 N 消息 N 片段 · cascade</td></tr>
  <tr><td>session</td><td>session_message</td><td>V2：会话 N 消息（按 seq）· cascade</td></tr>
  <tr><td>session</td><td>session_input</td><td>V2：会话 N 条待处理输入 · cascade</td></tr>
  <tr><td>session</td><td>session_context_epoch</td><td>1:1（主键即 session_id）· cascade</td></tr>
  <tr><td>session</td><td>todo</td><td>会话 N 条待办 · cascade</td></tr>
</table>
<p>这张表最该品的，是那一片 <span class="mono">onDelete:"cascade"</span> 编织出的<strong>「级联删除网」</strong>（注意它<strong>不含</strong> parent_id 那条——自指列没有外键，不参与级联）。删一个 project，它名下所有 session 跟着删；删一个 session，它名下所有 message/part/session_message/session_input/epoch/todo 全部跟着删。<strong>数据库在结构层面就保证了「没有孤儿数据」</strong>——你永远不会查到一条「属于某个早已不存在的会话」的消息。这种一致性不是靠应用代码小心翼翼地手动删，而是靠外键约束<strong>由数据库强制兜底</strong>（也正因如此，上一课那句 <span class="mono">PRAGMA foreign_keys=ON</span> 才不可省）。把一次「删掉 project」的级联走一遍，就能看清这棵树是怎么连根拔起的：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">删</span><span class="t-txt">DELETE FROM project WHERE id=…（拔起树根）</span></div>
  <div class="t-row"><span class="t-num">↓</span><span class="t-txt">该 project 名下所有 session 自动删（project_id cascade）</span></div>
  <div class="t-row"><span class="t-num">↓</span><span class="t-txt">每个 session 名下 message → 每条 message 名下 part 自动删（两级 cascade）</span></div>
  <div class="t-row"><span class="t-num">↓</span><span class="t-txt">同时 session_message / session_input / session_context_epoch / todo 全删</span></div>
  <div class="t-row"><span class="t-num">✓</span><span class="t-txt">一行应用代码都没写，数据库保证不留一条孤儿</span></div>
</div>

<h2>V1 与 V2：两代消息模型同堂</h2>
<p>仔细看会发现一件有趣的事：存「消息」的表竟有<strong>两套</strong>。一套是 <span class="mono">message</span> + <span class="mono">part</span>（V1），一套是 <span class="mono">session_message</span>（V2）。它们为什么并存？</p>
<div class="cols">
  <div class="col"><h4>V1 · message + part</h4><p><span class="mono">message</span>(一条消息) → <span class="mono">part</span>(消息的一个片段，如一段文字、一次工具调用)，两级。每行的 <span class="mono">data</span> 列是一个 <strong>JSON 大对象</strong>，装着 V1 时代的消息结构。这是 opencode 早期的消息模型。</p></div>
  <div class="col"><h4>V2 · session_message</h4><p><span class="mono">session_message</span> 单表，带 <span class="mono">type</span>(消息类型) + <span class="mono">seq</span>(会话内单调序号) + <span class="mono">data</span>(JSON)。这是重构后的新模型，配套 <span class="mono">session_input</span>、<span class="mono">session_context_epoch</span> 一起构成 V2 的 session 核心。</p></div>
</div>
<p>「新旧同堂」绝非设计混乱，而是<strong>大型有状态系统演进时的常态与智慧</strong>：你不可能在某个深夜「啪」地把所有历史会话从 V1 瞬间切到 V2——那风险太大。正确的做法是让两代模型<strong>在同一个库里共存一段时间</strong>，旧数据继续以 V1 形态躺着、新数据以 V2 形态写入，再用一个专门的迁移过程慢慢把 V1 翻译成 V2（这正是下一课 L50 的主题）。</p>
<p>这张「同堂」的快照，本身就是 opencode 正处在<strong>从 V1 向 V2 演进途中</strong>的活化石。你也能从中读出一条朴素的工程真理：<strong>真实世界的数据库 schema 从不是一张定稿的蓝图，而是一部还在续写的历史</strong>——能优雅地容纳「上一代」与「这一代」共存，是成熟系统的标志。</p>
<p>另外值得一提的是 V1 那两级结构本身：<span class="mono">message</span>→<span class="mono">part</span> 的拆分，对应着「一条助手消息里，可以夹着好几个片段」——一段思考文字是一个 part、一次工具调用是一个 part、工具返回又是一个 part。这种「消息含多片段」的结构其实很合理，V2 的 <span class="mono">session_message</span> 也延续了类似的思路，只是把组织方式重做得更利于按 <span class="mono">seq</span> 流式追加。两代之间的差异，更多在「怎么编号、怎么入箱、上下文怎么落盘」这些<strong>会话编排层面</strong>，而非「一条消息长什么样」这个内容层面。</p>

<h2>V2 三件套与 seq：顺序、纪元与不重不漏</h2>
<p>V2 的 session 核心由三张表撑起，它们的设计把「顺序」和「一致性」刻进了表结构本身：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">session_message</div><div class="c-txt">V2 可见消息；<span class="mono">seq</span> 单调序号 + <strong>唯一索引(session,seq)</strong> 保证会话内序号不重——总顺序的脊梁</div></div>
  <div class="cell"><div class="c-tag">session_input</div><div class="c-txt">durable 输入箱；<span class="mono">prompt</span>(JSON) + <span class="mono">delivery</span> + <span class="mono">admitted_seq</span>(入箱号) + <span class="mono">promoted_seq</span>?(转正号)——先持久入箱、再择机晋升为可见消息</div></div>
  <div class="cell"><div class="c-tag">session_context_epoch</div><div class="c-txt">M5 上下文纪元落盘；主键即 <span class="mono">session_id</span>(1:1)；<span class="mono">baseline</span>/<span class="mono">snapshot</span>(SystemContext)/<span class="mono">baseline_seq</span>/<span class="mono">revision</span></div></div>
</div>
<p><span class="mono">session_input</span> 这张表，藏着 V2 最精巧的一笔——它是一个 <strong>durable（持久化）的输入箱</strong>。当你给 agent 发一句话，opencode 不是直接把它塞进对话，而是<strong>先把它作为一行 <span class="mono">session_input</span> 持久地「入箱」</strong>（记一个 <span class="mono">admitted_seq</span> 入箱号），之后由那个串行化的运行器在<strong>安全的边界</strong>把入箱的输入<strong>「晋升」</strong>成一条可见的 <span class="mono">session_message</span>（记一个 <span class="mono">promoted_seq</span> 转正号）。<span class="mono">delivery</span> 字段则区分这条输入是「插队打断」还是「排队等待」。<strong>为什么要先入箱、再晋升？</strong>因为这样即使进程在「收到输入」和「处理输入」之间崩溃，那条输入也<strong>已经稳稳躺在库里</strong>，重启后能接着处理——输入永不丢失。把这条输入的一生画出来：</p>
<div class="flow">
  <div class="f-node">你发一句话<br><small>SessionV2.prompt</small></div>
  <div class="f-arrow">持久入箱 →</div>
  <div class="f-node">session_input 一行<br><small>记 admitted_seq</small></div>
  <div class="f-arrow">安全边界 →</div>
  <div class="f-node">运行器晋升<br><small>记 promoted_seq</small></div>
  <div class="f-arrow">转正 →</div>
  <div class="f-node">可见 session_message<br><small>进入对话被模型看到</small></div>
</div>
<p>而 <span class="mono">session_context_epoch</span> 则把 M5 那套精心算出的 <strong>System Context 快照</strong>落盘（主键就是 session_id，一个会话一份），<span class="mono">baseline_seq</span>/<span class="mono">revision</span> 记着它对应到消息序列的哪个位置、迭代到第几版——让「当前上下文是怎么算出来的」可持久、可追溯。</p>
<p>把这三张表连起来看，你会发现 <span class="mono">seq</span> 这个看似不起眼的整数，是 V2 一致性的<strong>无名英雄</strong>：<span class="mono">session_message</span> 用 <span class="mono">unique(session,seq)</span> 保证消息顺序不乱、不重；<span class="mono">session_input</span> 用 <span class="mono">admitted_seq</span>/<span class="mono">promoted_seq</span> 把「入箱顺序」和「晋升顺序」分开记账；甚至还有一张 <span class="mono">event</span> 表（事件溯源）用 <span class="mono">unique(aggregate,seq)</span> 给事件流编号。<strong>单调递增的序号 + 唯一索引</strong>，是数据库给「分布式/并发世界里如何确定先后、如何防止重复处理」这道难题的经典答案——它同时给了你<strong>全序</strong>（谁在谁之前）和<strong>幂等</strong>（同一个号不会插两次）。这一点对 agent 这种「可能崩溃、可能重启、可能并发」的系统尤其重要：当运行器重启后想接着干，它只需问一句「这个会话晋升到第几号了」，就能精确知道从哪儿继续，绝不会把同一条输入晋升两遍、也不会漏掉中间任何一条。把<strong>顺序与一致性直接编码进 schema 的索引约束</strong>（而非寄望应用代码每次都记得检查），是 opencode 持久化层最值得学的一手——<strong>让数据库的结构本身，成为正确性的最后一道防线。</strong></p>

<div class="card macro">
  <div class="tag">🗺️ 宏观视角</div>
  <p>这一课走进 SQLite 文件柜，看清了 opencode 状态落盘的核心表网，也看清了「记忆」如何以行与外键的形式组织起来：</p>
  <ul>
    <li><strong>session 是中枢</strong>（<span class="mono">session/sql.ts</span>）：列分身份归属(id/project_id/parent_id 自指/directory)、展示(title/summary)、用量(cost/tokens_*)、状态(agent/model/permission/revert JSON)、时间(Timestamps/time_compacting/archived)。几乎所有表外键指回它。</li>
    <li><strong>级联删除网</strong>：project→session→message→part、session→session_message/input/epoch/todo，外键几乎都 <span class="mono">onDelete:"cascade"</span>——删根连根带走，数据库结构层保证「无孤儿」（靠 <span class="mono">foreign_keys=ON</span>）。</li>
    <li><strong>V1/V2 同堂</strong>：<span class="mono">message+part</span>(V1，data JSON 两级) vs <span class="mono">session_message</span>(V2，单表+seq+type)。并存是平滑演进的智慧，为 L50 的 V1→V2 迁移埋下伏笔。</li>
    <li><strong>V2 三件套 + seq</strong>：<span class="mono">session_message</span>(unique session,seq 定序)、<span class="mono">session_input</span>(durable 输入箱：admitted_seq 入箱→promoted_seq 晋升，delivery 区分插队/排队，崩溃不丢输入)、<span class="mono">session_context_epoch</span>(M5 快照落盘，1:1)。seq 单调序号+唯一索引=全序+幂等。</li>
  </ul>
  <p>核心表网看清了——以 session 为根、外键织网、seq 定序。但你可能注意到 message/part 的 <span class="mono">data</span> 列装的是 <strong>V1</strong> 结构：那些老数据当初并不在 SQLite 里，而在文件系统中。下一课（L50）就讲 <strong>V1 文件存储</strong>是什么样、以及 opencode 如何把散落在文件里的 V1 数据<strong>迁移进 V2 的 SQLite</strong>。之后 L51 讲压缩、摘要与快照/revert——会话太长了怎么压、怎么回滚到历史某一刻。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p>看 <span class="mono">session_message</span> 与 <span class="mono">session_input</span> 的索引定义，「顺序」与「不重」是怎么刻进 schema 的（简化自 <span class="mono">session/sql.ts</span>）：</p>
  <pre class="code"><span class="cm">// V2 可见消息：seq 单调，唯一索引保证会话内不重号</span>
sqliteTable(<span class="st">"session_message"</span>, {
  id: <span class="fn">text</span>().<span class="fn">primaryKey</span>(),
  session_id: <span class="fn">text</span>()...<span class="fn">references</span>(() =&gt; SessionTable.id, { onDelete: <span class="st">"cascade"</span> }),
  type: <span class="fn">text</span>().<span class="fn">notNull</span>(),
  seq: <span class="fn">integer</span>().<span class="fn">notNull</span>(),
  data: <span class="fn">text</span>({ mode: <span class="st">"json"</span> }).<span class="fn">notNull</span>(),
}, (t) =&gt; [
  <span class="fn">uniqueIndex</span>(...).<span class="fn">on</span>(t.session_id, t.seq),          <span class="cm">// ← 同会话 seq 不可重复</span>
  <span class="fn">index</span>(...).<span class="fn">on</span>(t.session_id, t.type, t.seq),       <span class="cm">// 按类型查、仍按序</span>
])

<span class="cm">// V2 输入箱：入箱号、晋升号分离；各自唯一</span>
sqliteTable(<span class="st">"session_input"</span>, {
  prompt: <span class="fn">text</span>({ mode: <span class="st">"json"</span> }).<span class="fn">notNull</span>(),
  delivery: <span class="fn">text</span>().<span class="fn">notNull</span>(),         <span class="cm">// 插队 steer / 排队 queue</span>
  admitted_seq: <span class="fn">integer</span>().<span class="fn">notNull</span>(),  <span class="cm">// 持久入箱时的号</span>
  promoted_seq: <span class="fn">integer</span>(),            <span class="cm">// 晋升为可见消息后的号（晋升前为空）</span>
}, (t) =&gt; [
  <span class="fn">uniqueIndex</span>(...).<span class="fn">on</span>(t.session_id, t.admitted_seq),
  <span class="fn">uniqueIndex</span>(...).<span class="fn">on</span>(t.session_id, t.promoted_seq),
])</pre>
  <p>这里最见功力的，是 <span class="mono">data</span> 列用 <span class="mono">text({ mode: "json" })</span> 存「松散负载」，而 <span class="mono">id/session_id/type/seq/admitted_seq</span> 这些<strong>需要被查询、被排序、被约束</strong>的字段，全是<strong>结构化的真列</strong>。这是一条贯穿全库的取舍哲学：<strong>「你要拿来查询/排序/做约束的，立成真列；你只是整团存取的，塞进 JSON」</strong>。消息的具体内容千变万化（文字、工具调用、图片……），用 JSON 装最灵活、不必为每种内容改 schema；但「它属于哪个会话、第几号、什么类型」必须是真列——否则没法建唯一索引保证不重号、没法高效地「按 session 按 seq 取这段对话」。一张表里<strong>结构化骨架 + JSON 血肉</strong>的混搭，既要了关系型数据库的查询/约束能力，又留了文档型的灵活——这正是现代「JSON 列」用得好的典范。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>session 是表网中枢</strong>（<span class="mono">session/sql.ts</span>）：列分身份归属(id/project_id→project/parent_id 自指子会话/directory)、展示、用量(cost/tokens_*)、状态(agent/model/permission/revert JSON)、时间。几乎所有表外键指回它。</li>
    <li><strong>级联删除网</strong>：project→session→message→part、session→session_message/input/epoch/todo，外键几乎都 <span class="mono">onDelete:"cascade"</span>——删根连根带走、结构层保证「无孤儿」（须 <span class="mono">foreign_keys=ON</span> 才生效，呼应 L48）。</li>
    <li><strong>V1/V2 两代消息同堂</strong>：<span class="mono">message+part</span>(V1，data JSON，两级) vs <span class="mono">session_message</span>(V2，单表+seq+type)。并存=平滑演进的智慧，引出 L50 的 V1→V2 迁移。</li>
    <li><strong>session_input = durable 输入箱</strong>：发给 agent 的话先持久「入箱」(admitted_seq)、再由串行运行器在安全边界「晋升」成可见 session_message(promoted_seq)，delivery 区分插队/排队。崩溃也不丢输入（先落库再处理）。</li>
    <li><strong>seq 单调序号 + 唯一索引 = 全序 + 幂等</strong>：session_message unique(session,seq)、event unique(aggregate,seq)——并发世界里定先后、防重复处理的经典答案。列策略：要查/排序/约束的立真列，松散负载塞 JSON。session_context_epoch 把 M5 快照 1:1 落盘。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Last lesson we built the file cabinet (SQLite), learned to draw blueprints (Drizzle), read the renovation log (migrations). This lesson, we <strong>pull open the drawers and see which core tables opencode actually stores</strong>, and the web of relationships woven among them by foreign keys. These tables are defined in each domain's <span class="mono">*/sql.ts</span> (chiefly <span class="mono">session/sql.ts</span>), the <strong>on-disk form</strong> of the whole agent state—every conversation, every message, every piece of context with the agent ultimately becomes rows in these tables. The six core tables the spec names: <span class="mono">session</span>, <span class="mono">message</span>/<span class="mono">part</span> (V1 message/part), <span class="mono">session_message</span> (V2 message), <span class="mono">session_input</span> (V2 inbox), <span class="mono">session_context_epoch</span> (context epoch). Grasp this table web and you hold the key to understanding how opencode's "memory" is organized.</p>
<p>This lesson has three progressively deeper insights. First, <strong><span class="mono">session</span> is the "hub" of the whole table web</strong>: nearly every table points back to session by foreign key (or via project→session), and these foreign keys almost all carry <span class="mono">onDelete:"cascade"</span>—delete a session and its messages, parts, inputs, epochs, todos are <strong>uprooted like a tree taking all its branches</strong>, the database automatically guaranteeing no orphans remain. Second, <strong>two generations of message model, V1 and V2, coexist in the same DB</strong>: <span class="mono">message</span>/<span class="mono">part</span> is the old V1 model, <span class="mono">session_message</span> the new V2 model—this "old and new under one roof" isn't chaos but for smooth migration (next lesson L50's theme). Third, <strong>the <span class="mono">seq</span> (sequence number) everywhere upholds "order" and "no-dup-no-miss"</strong>: V2's messages, inputs, events all rely on monotonically increasing sequence numbers to order and on unique indices to prevent duplication. Grasp these three and you no longer see a pile of isolated tables but a <strong>state tree rooted at session, carefully organized by foreign keys and sequence numbers</strong>.</p>

<div class="card analogy">
  <div class="tag">🗂️ Analogy</div>
  Picture this table web as an <strong>archive system</strong>. <span class="mono">project</span> is the <strong>outermost project archive box</strong>, <span class="mono">session</span> the <strong>case files</strong> in the box (one file per conversation). Within a case file are clipped its <strong>correspondence</strong> (message), each letter's <strong>paged content</strong> (part), the new-format <strong>meeting minutes</strong> (session_message), the <strong>pending inbound mail</strong> not yet officially filed (session_input), plus a <strong>"current-context overview card"</strong> (context_epoch). Crucially: all of these are <strong>clipped inside the case file's "mother folder"</strong>—pull the whole case file out and shred it (delete session), and the letters, attachments, inbound mail, overview card clipped inside <strong>vanish along with it, not one left</strong> (cascade delete), never a ghost of "the letter remains, the case file gone." And each letter, each minute is ordered by a <strong>send/receive serial number</strong> (seq), who's before whom, any gaps, all at a glance.
</div>

<h2>session: the hub of the whole table web</h2>
<p>The <span class="mono">session</span> table is the root of everything. Its columns are surprisingly many—but don't be daunted; that's exactly how much information a "session" carries: who it is, which project it belongs to, what model and permissions it runs with, how many tokens it spent, when created and when archived. Roughly grouped, each group answers one question about a session:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">identity &amp; belonging</div><div class="c-txt"><span class="mono">id</span>(PK), <span class="mono">project_id</span>(→project,cascade), <span class="mono">workspace_id</span>, <span class="mono">parent_id</span>(self-ref→parent session), <span class="mono">slug</span>, <span class="mono">directory</span>/<span class="mono">path</span></div></div>
  <div class="cell"><div class="c-tag">display</div><div class="c-txt"><span class="mono">title</span>, <span class="mono">version</span>, <span class="mono">share_url</span>, <span class="mono">summary_*</span>(changed lines/files/diff)</div></div>
  <div class="cell"><div class="c-tag">usage stats</div><div class="c-txt"><span class="mono">cost</span>, <span class="mono">tokens_input/output/reasoning/cache_read/cache_write</span></div></div>
  <div class="cell"><div class="c-tag">runtime state</div><div class="c-txt"><span class="mono">agent</span>, <span class="mono">model</span>(JSON), <span class="mono">permission</span>(JSON,L41 Ruleset), <span class="mono">revert</span>(JSON)</div></div>
  <div class="cell"><div class="c-tag">time</div><div class="c-txt"><span class="mono">...Timestamps</span>, <span class="mono">time_compacting</span>, <span class="mono">time_archived</span></div></div>
</div>
<p>Note that <span class="mono">parent_id</span> <strong>self-referencing column</strong>: a session can be a sub-session of another—exactly how, in M4 when an agent spawns a subtask (subagent), the sub-session is parked under the parent on disk. But note: <span class="mono">parent_id</span> is just an <strong>indexed plain column, not an enforced foreign key</strong> (it has no <span class="mono">.references()</span> in source), so deleting a parent session does <strong>not</strong> cascade-delete sub-sessions. Other tables, by contrast, mostly point back to session via a <strong>cascading foreign key</strong>. Spreading out this relationship web:</p>
<table class="t">
  <tr><th>parent table</th><th>child table</th><th>relation (cascading?)</th></tr>
  <tr><td>project</td><td>session (project_id)</td><td>one project N sessions · cascade</td></tr>
  <tr><td>session</td><td>session (parent_id)</td><td>parent session N sub-sessions · <strong>self-ref index, not FK, no cascade</strong></td></tr>
  <tr><td>session</td><td>message → part</td><td>V1: session N messages N parts · cascade</td></tr>
  <tr><td>session</td><td>session_message</td><td>V2: session N messages (by seq) · cascade</td></tr>
  <tr><td>session</td><td>session_input</td><td>V2: session N pending inputs · cascade</td></tr>
  <tr><td>session</td><td>session_context_epoch</td><td>1:1 (PK is session_id) · cascade</td></tr>
  <tr><td>session</td><td>todo</td><td>session N todos · cascade</td></tr>
</table>
<p>What this table most deserves savoring is the <strong>"cascade-delete web"</strong> woven by all those <span class="mono">onDelete:"cascade"</span> (note it <strong>excludes</strong> the parent_id row—a self-ref column has no foreign key and takes no part in cascade). Delete a project, all its sessions delete; delete a session, all its message/part/session_message/session_input/epoch/todo delete. <strong>At the structural level the database guarantees "no orphan data"</strong>—you'll never query a message "belonging to a session that no longer exists." This consistency isn't from app code carefully deleting by hand but from foreign-key constraints <strong>enforced as a backstop by the database</strong> (and exactly why last lesson's <span class="mono">PRAGMA foreign_keys=ON</span> can't be omitted). Walking through one "delete a project" cascade shows how the tree is uprooted:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">del</span><span class="t-txt">DELETE FROM project WHERE id=… (pull the root)</span></div>
  <div class="t-row"><span class="t-num">↓</span><span class="t-txt">all sessions under that project auto-delete (project_id cascade)</span></div>
  <div class="t-row"><span class="t-num">↓</span><span class="t-txt">each session's message → each message's part auto-delete (two-level cascade)</span></div>
  <div class="t-row"><span class="t-num">↓</span><span class="t-txt">meanwhile session_message / session_input / session_context_epoch / todo all delete</span></div>
  <div class="t-row"><span class="t-num">✓</span><span class="t-txt">not a line of app code written, the DB guarantees not one orphan left</span></div>
</div>

<h2>V1 and V2: two generations of message model under one roof</h2>
<p>Look closely and you find something interesting: there are <strong>two sets</strong> of tables storing "messages." One is <span class="mono">message</span> + <span class="mono">part</span> (V1), one is <span class="mono">session_message</span> (V2). Why do they coexist?</p>
<div class="cols">
  <div class="col"><h4>V1 · message + part</h4><p><span class="mono">message</span>(a message) → <span class="mono">part</span>(a fragment of the message, e.g. a stretch of text, a tool call), two levels. Each row's <span class="mono">data</span> column is a <strong>big JSON object</strong> holding the V1-era message structure. This is opencode's early message model.</p></div>
  <div class="col"><h4>V2 · session_message</h4><p><span class="mono">session_message</span> single table, with <span class="mono">type</span>(message type) + <span class="mono">seq</span>(monotonic per-session sequence) + <span class="mono">data</span>(JSON). This is the refactored new model, together with <span class="mono">session_input</span>, <span class="mono">session_context_epoch</span> forming the V2 session core.</p></div>
</div>
<p>"Old and new under one roof" is by no means design chaos but <strong>the norm and wisdom of large stateful systems as they evolve</strong>: you can't, one late night, "snap" all historical sessions from V1 to V2 instantly—too risky. The right way is to let the two generations <strong>coexist in the same DB for a while</strong>, old data lying in V1 form, new data written in V2 form, then slowly translate V1 into V2 with a dedicated migration process (exactly next lesson L50's theme).</p>
<p>This "under one roof" snapshot is itself a living fossil of opencode mid-evolution <strong>from V1 toward V2</strong>. You can also read from it a plain engineering truth: <strong>a real-world database schema is never a finalized blueprint but a history still being written</strong>—gracefully accommodating "the last generation" and "this generation" coexisting is the mark of a mature system.</p>
<p>Also worth noting is V1's two-level structure itself: the <span class="mono">message</span>→<span class="mono">part</span> split corresponds to "one assistant message can clip several fragments"—a stretch of thinking text is a part, a tool call is a part, the tool return another part. This "message contains multiple parts" structure is quite reasonable, and V2's <span class="mono">session_message</span> continues a similar idea, only reworking the organization to favor streaming-append by <span class="mono">seq</span>. The difference between generations is more at the <strong>conversation-orchestration level</strong> of "how to number, how to inbox, how to persist context" than the content level of "what a message looks like."</p>

<h2>The V2 trio and seq: order, epochs, and no-dup-no-miss</h2>
<p>V2's session core is upheld by three tables whose design carves "order" and "consistency" into the table structure itself:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">session_message</div><div class="c-txt">V2 visible messages; <span class="mono">seq</span> monotonic + <strong>unique index(session,seq)</strong> ensures per-session no duplicate seq—the spine of total order</div></div>
  <div class="cell"><div class="c-tag">session_input</div><div class="c-txt">durable inbox; <span class="mono">prompt</span>(JSON) + <span class="mono">delivery</span> + <span class="mono">admitted_seq</span>(inbox no.) + <span class="mono">promoted_seq</span>?(promotion no.)—durably inboxed first, then promoted to a visible message at the right time</div></div>
  <div class="cell"><div class="c-tag">session_context_epoch</div><div class="c-txt">M5 context epoch on disk; PK is <span class="mono">session_id</span>(1:1); <span class="mono">baseline</span>/<span class="mono">snapshot</span>(SystemContext)/<span class="mono">baseline_seq</span>/<span class="mono">revision</span></div></div>
</div>
<p>The <span class="mono">session_input</span> table hides V2's most exquisite stroke—it's a <strong>durable inbox</strong>. When you send the agent a sentence, opencode doesn't stuff it straight into the conversation but <strong>first durably "admits" it as a <span class="mono">session_input</span> row</strong> (recording an <span class="mono">admitted_seq</span> inbox number), after which that serialized runner <strong>"promotes"</strong> the inboxed input into a visible <span class="mono">session_message</span> at a <strong>safe boundary</strong> (recording a <span class="mono">promoted_seq</span> promotion number). The <span class="mono">delivery</span> field distinguishes whether this input is "cut in line / interrupt" or "queue and wait." <strong>Why admit first, promote later?</strong> Because this way, even if the process crashes between "receiving the input" and "processing the input," that input <strong>already lies safely in the DB</strong> and can be processed after restart—input is never lost. Drawing this input's life:</p>
<div class="flow">
  <div class="f-node">you send a sentence<br><small>SessionV2.prompt</small></div>
  <div class="f-arrow">durably admit →</div>
  <div class="f-node">a session_input row<br><small>record admitted_seq</small></div>
  <div class="f-arrow">safe boundary →</div>
  <div class="f-node">runner promotes<br><small>record promoted_seq</small></div>
  <div class="f-arrow">go visible →</div>
  <div class="f-node">visible session_message<br><small>enters conversation, seen by model</small></div>
</div>
<p>And <span class="mono">session_context_epoch</span> persists M5's carefully-computed <strong>System Context snapshot</strong> on disk (PK is session_id, one per session), <span class="mono">baseline_seq</span>/<span class="mono">revision</span> recording which position in the message sequence it corresponds to and which iteration it's at—making "how the current context was computed" persistable and traceable.</p>
<p>Connecting these three tables, you find <span class="mono">seq</span>, that seemingly humble integer, is V2 consistency's <strong>unsung hero</strong>: <span class="mono">session_message</span> uses <span class="mono">unique(session,seq)</span> to keep message order intact and unduplicated; <span class="mono">session_input</span> uses <span class="mono">admitted_seq</span>/<span class="mono">promoted_seq</span> to journal "inbox order" and "promotion order" separately; there's even an <span class="mono">event</span> table (event sourcing) using <span class="mono">unique(aggregate,seq)</span> to number the event stream. <strong>A monotonically increasing sequence number + a unique index</strong> is the database's classic answer to "how to determine order and prevent duplicate processing in a distributed/concurrent world"—it gives you both <strong>total order</strong> (who's before whom) and <strong>idempotency</strong> (the same number won't insert twice). This matters especially for an agent—a "may crash, may restart, may run concurrently" system: when the runner restarts and wants to continue, it need only ask "what number has this session promoted to" to know exactly where to resume, never promoting the same input twice nor missing any in between. <strong>Encoding order and consistency directly into the schema's index constraints</strong> (rather than hoping app code remembers to check every time) is the most learnable move of opencode's persistence layer—<strong>let the database structure itself be the last line of defense for correctness.</strong></p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>This lesson walks into the SQLite cabinet and sees clearly opencode's core table web of state on disk, and how "memory" is organized as rows and foreign keys:</p>
  <ul>
    <li><strong>session is the hub</strong> (<span class="mono">session/sql.ts</span>): columns split into identity/belonging (id/project_id/parent_id self-ref/directory), display (title/summary), usage (cost/tokens_*), state (agent/model/permission/revert JSON), time (Timestamps/time_compacting/archived). Nearly all tables point back to it by FK.</li>
    <li><strong>cascade-delete web</strong>: project→session→message→part, session→session_message/input/epoch/todo, FKs almost all <span class="mono">onDelete:"cascade"</span>—delete the root uproots all, the DB structure guarantees "no orphans" (relies on <span class="mono">foreign_keys=ON</span>).</li>
    <li><strong>V1/V2 under one roof</strong>: <span class="mono">message+part</span>(V1, data JSON, two levels) vs <span class="mono">session_message</span>(V2, single table+seq+type). Coexistence is the wisdom of smooth evolution, setting up L50's V1→V2 migration.</li>
    <li><strong>V2 trio + seq</strong>: <span class="mono">session_message</span>(unique session,seq orders), <span class="mono">session_input</span>(durable inbox: admitted_seq admit→promoted_seq promote, delivery distinguishes cut-in/queue, crash doesn't lose input), <span class="mono">session_context_epoch</span>(M5 snapshot on disk, 1:1). seq monotonic+unique index = total order + idempotency.</li>
  </ul>
  <p>The core table web is clear—rooted at session, woven by foreign keys, ordered by seq. But you may have noticed message/part's <span class="mono">data</span> column holds <strong>V1</strong> structure: that old data originally wasn't in SQLite but in the file system. The next lesson (L50) covers what <strong>V1 file storage</strong> looks like and how opencode <strong>migrates V1 data scattered in files into V2's SQLite</strong>. Then L51 covers compaction, summaries, and snapshots/revert—how to compress a too-long session, how to roll back to a historical moment.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p>Look at <span class="mono">session_message</span> and <span class="mono">session_input</span>'s index definitions—how "order" and "no-dup" are carved into the schema (simplified from <span class="mono">session/sql.ts</span>):</p>
  <pre class="code"><span class="cm">// V2 visible messages: seq monotonic, unique index ensures no dup seq per session</span>
sqliteTable(<span class="st">"session_message"</span>, {
  id: <span class="fn">text</span>().<span class="fn">primaryKey</span>(),
  session_id: <span class="fn">text</span>()...<span class="fn">references</span>(() =&gt; SessionTable.id, { onDelete: <span class="st">"cascade"</span> }),
  type: <span class="fn">text</span>().<span class="fn">notNull</span>(),
  seq: <span class="fn">integer</span>().<span class="fn">notNull</span>(),
  data: <span class="fn">text</span>({ mode: <span class="st">"json"</span> }).<span class="fn">notNull</span>(),
}, (t) =&gt; [
  <span class="fn">uniqueIndex</span>(...).<span class="fn">on</span>(t.session_id, t.seq),          <span class="cm">// ← same session, seq can't repeat</span>
  <span class="fn">index</span>(...).<span class="fn">on</span>(t.session_id, t.type, t.seq),       <span class="cm">// query by type, still in order</span>
])

<span class="cm">// V2 inbox: admit no. and promotion no. separated; each unique</span>
sqliteTable(<span class="st">"session_input"</span>, {
  prompt: <span class="fn">text</span>({ mode: <span class="st">"json"</span> }).<span class="fn">notNull</span>(),
  delivery: <span class="fn">text</span>().<span class="fn">notNull</span>(),         <span class="cm">// cut-in steer / queue</span>
  admitted_seq: <span class="fn">integer</span>().<span class="fn">notNull</span>(),  <span class="cm">// number at durable admission</span>
  promoted_seq: <span class="fn">integer</span>(),            <span class="cm">// number after promotion to visible (empty before)</span>
}, (t) =&gt; [
  <span class="fn">uniqueIndex</span>(...).<span class="fn">on</span>(t.session_id, t.admitted_seq),
  <span class="fn">uniqueIndex</span>(...).<span class="fn">on</span>(t.session_id, t.promoted_seq),
])</pre>
  <p>What shows the most craft here is that <span class="mono">data</span> uses <span class="mono">text({ mode: "json" })</span> for the "loose payload," while <span class="mono">id/session_id/type/seq/admitted_seq</span>—fields that <strong>need to be queried, sorted, constrained</strong>—are all <strong>structured real columns</strong>. This is a trade-off philosophy running through the whole DB: <strong>"what you'll query/sort/constrain becomes a real column; what you just store as a blob goes into JSON."</strong> A message's concrete content varies endlessly (text, tool call, image…), so JSON holds it most flexibly, no schema change per content type; but "which session it belongs to, what number, what type" must be real columns—else you can't build a unique index to guarantee no dup seq, can't efficiently "fetch this conversation by session by seq." A table's mix of <strong>structured skeleton + JSON flesh</strong> takes both the relational DB's query/constraint power and the document store's flexibility—exactly the exemplar of modern "JSON columns" used well.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>session is the table-web hub</strong> (<span class="mono">session/sql.ts</span>): columns split into identity/belonging (id/project_id→project/parent_id self-ref sub-session/directory), display, usage (cost/tokens_*), state (agent/model/permission/revert JSON), time. Nearly all tables FK back to it.</li>
    <li><strong>cascade-delete web</strong>: project→session→message→part, session→session_message/input/epoch/todo, FKs almost all <span class="mono">onDelete:"cascade"</span>—delete the root uproots all, structure guarantees "no orphans" (needs <span class="mono">foreign_keys=ON</span> to take effect, echoing L48).</li>
    <li><strong>two generations of message model under one roof</strong>: <span class="mono">message+part</span>(V1, data JSON, two levels) vs <span class="mono">session_message</span>(V2, single table+seq+type). Coexistence = wisdom of smooth evolution, setting up L50's V1→V2 migration.</li>
    <li><strong>session_input = durable inbox</strong>: a sentence sent to the agent is first durably "admitted" (admitted_seq), then "promoted" into a visible session_message (promoted_seq) by the serial runner at a safe boundary, delivery distinguishing cut-in/queue. Crash doesn't lose input (persist before processing).</li>
    <li><strong>seq monotonic + unique index = total order + idempotency</strong>: session_message unique(session,seq), event unique(aggregate,seq)—the classic answer to ordering and preventing duplicate processing in a concurrent world. Column strategy: query/sort/constrain → real column, loose payload → JSON. session_context_epoch persists the M5 snapshot 1:1.</li>
  </ul>
</div>
""",
}
LESSON_50 = {
    "zh": r"""
<p class="lead">上一课我们看到一件耐人寻味的事：SQLite 里的 <span class="mono">message</span>/<span class="mono">part</span> 表，存的是 <strong>V1</strong> 结构的数据。但这些 V1 数据当初<strong>根本不在 SQLite 里</strong>——它们躺在文件系统中，一个对象一个 JSON 文件。这一课就讲清这段「迁徙史」：opencode 的 <strong>V1 文件存储</strong>长什么样（<span class="mono">storage/storage.ts</span>），以及它如何把散落在成千上万个 JSON 文件里的数据，<strong>迁移进 V2 的 SQLite</strong>。这不是一个边角细节，而是几乎每个长期演进的软件都会经历的真实剧情：<strong>你最初用了一个最简单的存储方案，跑了很久，直到它的简单开始变成负担，于是你必须在「不丢一条老数据」的前提下，把整个家当搬进一个更强的新方案。</strong></p>
<p>这一课最值得带走的洞见有两层。第一，<strong>「键即路径」的极简文件存储</strong>：V1 把每个对象存成一个 JSON 文件，用一个 <span class="mono">string[]</span> 数组当键，直接映射成嵌套的文件路径——<span class="mono">read(["session", 项目ID, 会话ID])</span> 就去读 <span class="mono">storage/session/&lt;项目ID&gt;/&lt;会话ID&gt;.json</span>。整个「数据库」就是一棵目录树，朴素到不需要任何数据库引擎。第二，<strong>「日志表记账」的迁移范式被复用了两次</strong>：上一课 L48 讲的 schema 迁移用一张 <span class="mono">migration</span> 表记「哪些结构变更跑过了」；这一课的 V1→V2 数据迁移，用<strong>另一张 <span class="mono">data_migration</span> 表</strong>记「哪些数据搬运跑过了」。同一个「记账即幂等」的朴素思想，被用在了两个不同的问题上。读懂这两点，你就理解了「一个软件如何从『一堆文件』优雅地长成『一个数据库』，又不在搬家途中摔碎任何一件旧家具」。</p>

<div class="card analogy">
  <div class="tag">📦 生活类比</div>
  把 V1 文件存储想象成一间<strong>用鞋盒装资料的小仓库</strong>：每份资料单独装一个鞋盒（一个 JSON 文件），鞋盒按「架子→格子→位置」的标签摆放（<span class="mono">string[]</span> 键即路径）。这套办法<strong>简单到极致</strong>——不需要管理员、不需要数据库，找资料就是顺着标签去对应位置取那个盒子。但当资料涨到成千上万盒，麻烦来了：想「找出所有标了某关键词的盒子」得<strong>把每个盒子都打开看一遍</strong>（没有索引）；想「同时改三个盒子、要么全改要么全不改」做不到（没有事务）；想「删掉一个项目、连带它所有资料」得自己一个个找出来删（没有级联）。于是你决定<strong>搬进一座配了检索系统的现代档案馆</strong>（SQLite）。搬家时最关键的纪律是：<strong>搬一批、在花名册上勾一批</strong>（<span class="mono">data_migration</span> 日志），万一搬到一半停电，来电后照着花名册<strong>只搬还没勾的</strong>，绝不会把同一盒资料搬两遍、也不会漏下任何一盒。
</div>

<h2>V1 文件存储：键即路径的极简方案</h2>
<p><span class="mono">storage.ts</span> 里的 <span class="mono">Storage</span> 服务，是 opencode 最早的持久化方案，朴素得只有五个方法：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">read(key)</div><div class="c-txt">读一个键对应的 JSON 文件，没有则报 NotFoundError</div></div>
  <div class="cell"><div class="c-tag">write(key, content)</div><div class="c-txt">把内容序列化成 JSON 写进对应文件（自动建目录）</div></div>
  <div class="cell"><div class="c-tag">update(key, fn)</div><div class="c-txt">读出→改→写回（读改写一条龙，写锁保护）</div></div>
  <div class="cell"><div class="c-tag">remove(key)</div><div class="c-txt">删掉对应文件</div></div>
  <div class="cell"><div class="c-tag">list(prefix)</div><div class="c-txt">列出某前缀下所有键（glob 目录树）</div></div>
</div>
<p>核心魔法就一行：<span class="mono">file(dir, key) = path.join(dir, ...key) + ".json"</span>——把 <span class="mono">string[]</span> 键<strong>直接拼成文件路径</strong>。于是 <span class="mono">["session", "proj_abc", "ses_123"]</span> 这个键，对应的就是磁盘上 <span class="mono">storage/session/proj_abc/ses_123.json</span> 这个文件。整个「数据库」<strong>就是 <span class="mono">Global.Path.data/storage</span> 下的一棵目录树</strong>，每个叶子是一个 JSON 文件。几个键到文件的映射例子，一看就懂：</p>
<table class="t">
  <tr><th>string[] 键</th><th>磁盘上的文件</th></tr>
  <tr><td><span class="mono">["session", "proj_abc", "ses_123"]</span></td><td><span class="mono">storage/session/proj_abc/ses_123.json</span></td></tr>
  <tr><td><span class="mono">["message", "ses_123", "msg_1"]</span></td><td><span class="mono">storage/message/ses_123/msg_1.json</span></td></tr>
  <tr><td><span class="mono">["part", "msg_1", "prt_9"]</span></td><td><span class="mono">storage/part/msg_1/prt_9.json</span></td></tr>
</table>
<p>这种「键即路径、对象即文件」的设计<strong>简单得令人发指</strong>——不需要数据库引擎、文件还人眼可读可调试，对一个早期项目而言是再合理不过的起点。为了在多个读写者并发时不出乱子，每个文件路径还配了一把 <span class="mono">TxReentrantLock</span>（读写锁）：<span class="mono">read</span> 取读锁、<span class="mono">write</span>/<span class="mono">update</span> 取写锁，<span class="mono">update</span> 的「读出→改→写回」全程握着写锁，避免两个写者互相覆盖。值得一提的是 <span class="mono">list(prefix)</span>：它没有索引可用，只能 glob 整棵子目录树、把每个文件路径反推回键再排序——这正是「无索引」在文件存储里最直白的体现：想枚举一类对象，只能去翻目录。</p>
<p>但「简单」是有代价的，而正是这些代价，在数据量与功能复杂度上来后逐一显形，最终逼出了向 SQLite 的迁移：</p>
<div class="cols">
  <div class="col"><h4>文件存储 · 简单但受限</h4><p>一个对象一个 JSON 文件、键即路径、人眼可读。但：<strong>无索引</strong>（查询=遍历所有文件）、<strong>无跨对象事务</strong>（改多个文件无法原子）、<strong>无外键级联</strong>（删项目得手动清子数据）、<strong>无关系查询</strong>（「按 seq 取这段对话」做不到）。</p></div>
  <div class="col"><h4>SQLite · 复杂但强大</h4><p>所有对象进表。换来：<strong>索引</strong>（高效查询/排序）、<strong>事务</strong>（多表原子升降）、<strong>外键 cascade</strong>（删根连根带走，L49）、<strong>关系查询</strong>（unique(session,seq) 定序，L49）。代价是引入一个数据库引擎。</p></div>
</div>

<h2>连文件存储也要迁移：内部布局演化</h2>
<p>有意思的是，<strong>即便只是一堆文件，schema/布局也躲不过演化</strong>。<span class="mono">storage.ts</span> 自己就内置了一套文件布局迁移（<span class="mono">MIGRATIONS</span> 数组），并用一个 <span class="mono">storage/migration</span> 标记文件记「跑到第几个了」。它的运行逻辑和 L48 如出一辙：读标记 → 从该处往后跑没跑过的迁移 → 每跑成一个就把标记 +1（失败则停下不前进）：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">读 <span class="mono">storage/migration</span> 标记文件 → 一个整数 N（没有则 0）</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">从第 N 个迁移开始，逐个往后跑 <span class="mono">MIGRATIONS[N..]</span></span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">每成功一个 → 把标记写成 N+1（幂等：重启从标记处续）</span></div>
  <div class="t-row"><span class="t-num">!</span><span class="t-txt">某个失败 → logError 并 break，不推进标记（下次重试）</span></div>
</div>
<p>这套布局迁移干了什么真事？看 <span class="mono">migration 1</span> 就懂了：早期 opencode 用<strong>目录名</strong>当项目 ID，但目录名不稳定。于是这个迁移做了件聪明事——它打开每个项目下的会话消息文件，找出它的 git 工作树，再用 <span class="mono">git rev-list --max-parents=0 --all</span> 取出<strong>仓库的根提交哈希</strong>，拿这个永不改变的哈希当稳定的项目 ID，把数据重新组织到 <span class="mono">session/&lt;项目ID&gt;/</span>、<span class="mono">message/&lt;会话ID&gt;/</span>、<span class="mono">part/&lt;消息ID&gt;/</span> 的新布局下。<span class="mono">migration 2</span> 则把会话摘要里的 diff 明细抽到单独的 <span class="mono">session_diff/</span> 文件、把摘要精简成增删行数的汇总。<strong>这印证了 L48 的那条真理在文件世界同样成立：数据结构从不是定稿的，连「一堆 JSON 文件」也需要一套有版本、幂等、可断点续跑的迁移机制来管理它的演化。</strong></p>

<h2>V1→V2：把文件搬进 SQLite</h2>
<p>当 opencode 决定从「一堆文件」升级到「一个 SQLite 库」（L48/L49），就需要一次<strong>数据大迁移</strong>：把 V1 文件里的会话、消息、片段，统统读出来、写进 SQLite 的表。这次迁移的「账本」，就是 <span class="mono">data-migration.sql.ts</span> 里那张朴素得只有两列的表：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">data_migration 表</div><div class="c-txt"><span class="mono">name</span>(主键) + <span class="mono">time_completed</span>——记「哪个数据迁移已跑完」</div></div>
  <div class="cell"><div class="c-tag">对比 L48 的 migration 表</div><div class="c-txt">同样两列、同样「记账即幂等」；区别：migration 记 <strong>schema</strong> 变更，data_migration 记 <strong>数据</strong> 搬运</div></div>
  <div class="cell"><div class="c-tag">落点：V1 形态的 SQLite 表</div><div class="c-txt">V1 数据搬进 <span class="mono">message</span>/<span class="mono">part</span> 表，<span class="mono">data</span> 列仍是 V1-shaped JSON（即 L49 见到的「V1 同堂」）</div></div>
</div>
<p>把整条迁徙路径连起来看，就是这样一条流水线：</p>
<div class="flow">
  <div class="f-node">V1 JSON 文件<br><small>storage/session/…、message/…</small></div>
  <div class="f-arrow">读出 →</div>
  <div class="f-node">逐个搬运<br><small>查 data_migration 账本跳过已搬</small></div>
  <div class="f-arrow">写入 →</div>
  <div class="f-node">SQLite message/part 表<br><small>data 列存 V1-shaped JSON</small></div>
  <div class="f-arrow">读取时 →</div>
  <div class="f-node">V2 投影<br><small>message-v2 把 V1 行投影成 V2 结构</small></div>
</div>
<p>这里有个非常务实的设计：V1 数据搬进 SQLite 时，<strong>并没有立刻被「翻译」成 V2 结构</strong>——它仍以 V1-shaped 的 JSON 原样躺在 <span class="mono">message</span>/<span class="mono">part</span> 表的 <span class="mono">data</span> 列里（这正是 L49 看到的「V1 同堂」之源）。真正的「V1→V2 语义转换」是<strong>读取时按需发生</strong>的：<span class="mono">message-v2.ts</span> 从 <span class="mono">PartTable</span>/<span class="mono">MessageTable</span> 读出 V1 行，<strong>当场投影（project）成 V2 的消息结构</strong>交给上层。</p>
<p>这种「<strong>先把字节原样搬过来、语义转换推迟到读取时</strong>」的策略极其聪明：它让<strong>数据迁移这一步变得简单又安全</strong>——只是把文件内容照搬进表，不动一个字节的语义，出错风险最小；而复杂易变的「V1 语义怎么映射成 V2」逻辑则集中在读取路径上一处维护、随时可改。<strong>把「搬运」和「翻译」解耦，让最危险的批量数据迁移退化成最无脑的字节复制</strong>——这是大型数据迁移里一条值得反复回味的智慧。</p>
<p>它还顺带带来一个好处：万一某天发现「V1→V2 的语义映射」写错了，你<strong>不必重跑那场代价高昂的数据大迁移</strong>，只要改读取时的投影逻辑、重新读一遍即可，因为原始 V1 字节<strong>始终原封不动地保存在库里</strong>。原始数据不被破坏性改写，就永远留着一条「重新解释」的退路——这种「保真原始、按需解释」的克制，和 L42 有界输出「全文 spill、按需回取」、L43 skills「名字常驻、正文按需」是同一种深谋远虑。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观视角</div>
  <p>这一课讲清了 opencode 从 V1 文件存储到 V2 SQLite 的迁徙史：</p>
  <ul>
    <li><strong>V1 文件存储</strong>（<span class="mono">storage/storage.ts</span>）：<span class="mono">Storage</span> 服务 read/write/update/remove/list；核心 <span class="mono">file(dir,key)=join(dir,...key)+".json"</span>——<span class="mono">string[]</span> 键即文件路径，整个库就是 <span class="mono">Global.Path.data/storage</span> 下一棵目录树；每文件配 <span class="mono">TxReentrantLock</span> 读写锁，<span class="mono">update</span>=握写锁读改写。</li>
    <li><strong>简单的代价</strong>：文件存储无索引/无跨对象事务/无外键 cascade/无关系查询——正是这些逼出了向 SQLite（L48/L49 给了索引/事务/cascade/关系查询）的迁移。</li>
    <li><strong>连文件也要迁移</strong>：<span class="mono">storage.ts</span> 内置 <span class="mono">MIGRATIONS</span> + <span class="mono">storage/migration</span> 标记，逻辑同 L48（读标记→跑 pending→标记+1，失败 break）。migration 1 用 git 根提交哈希(<span class="mono">rev-list --max-parents=0</span>)当稳定项目 ID 重组布局；migration 2 抽 summary diff。</li>
    <li><strong>V1→V2 数据迁移</strong>：<span class="mono">data_migration</span> 表(name+time_completed)记账，与 L48 的 <span class="mono">migration</span> 表同款「记账即幂等」（一个记 schema、一个记数据）。V1 文件搬进 SQLite <span class="mono">message</span>/<span class="mono">part</span> 表仍存 V1-shaped JSON；语义转换推迟到读取时由 <span class="mono">message-v2</span> 投影——「搬运」与「翻译」解耦。</li>
  </ul>
  <p>至此「数据从哪来、怎么存、怎么搬」讲透了。M9 还剩最后一课 L51：当一个会话<strong>太长</strong>（消息多到撑爆上下文），怎么<strong>压缩（compaction）</strong>和<strong>摘要</strong>它；以及 opencode 怎么用 git 集成做<strong>快照（snapshot）与 revert</strong>，让你能把工作目录回滚到对话历史中的某一刻。压缩与快照，正是「持久化」之上更高阶的「记忆管理」。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p><span class="mono">storage.ts</span> 的迁移驱动循环，把「断点续跑 + 失败即停」写得很克制（简化自源码）：</p>
  <pre class="code"><span class="cm">// 读标记文件：已跑到第几个迁移（没有则 0）</span>
<span class="kw">const</span> migration = <span class="kw">yield*</span> fs.<span class="fn">readFileString</span>(marker).<span class="fn">pipe</span>(
  Effect.<span class="fn">map</span>(parseMigration),
  Effect.<span class="fn">catchIf</span>(missing, () =&gt; Effect.<span class="fn">succeed</span>(<span class="nu">0</span>)),   <span class="cm">// 文件不存在=从 0 开始</span>
)
<span class="kw">for</span> (<span class="kw">let</span> i = migration; i &lt; MIGRATIONS.length; i++) {
  <span class="kw">const</span> exit = <span class="kw">yield*</span> Effect.<span class="fn">exit</span>(<span class="fn">step</span>(dir, fs, git))
  <span class="kw">if</span> (Exit.<span class="fn">isFailure</span>(exit)) {
    <span class="kw">yield*</span> Effect.<span class="fn">logError</span>(<span class="st">"failed to run migration"</span>, { index: i, cause: exit.cause })
    <span class="kw">break</span>                                <span class="cm">// ← 失败即停，不推进标记 → 下次重试这一个</span>
  }
  <span class="kw">yield*</span> fs.<span class="fn">writeWithDirs</span>(marker, <span class="fn">String</span>(i + <span class="nu">1</span>))   <span class="cm">// 成功才推进</span>
}</pre>
  <p>最值得品的是那句 <span class="mono">break</span> 的<strong>克制</strong>：一旦某个迁移失败，它<strong>立刻停下、绝不跳过去跑后面的</strong>，也<strong>不推进标记</strong>。为什么这么保守？因为迁移之间往往<strong>有先后依赖</strong>——后一个迁移很可能假设前一个已经把数据整理成某种形态。如果前一个失败了还硬着头皮跑后面的，极可能在一个<strong>半残的数据状态</strong>上越搞越乱，最终酿成无法收拾的损坏。「失败就停在原地、下次重试这一个」远比「带病前进」安全得多。这和 L48 schema 迁移那句 <span class="mono">die("库非空却无 session 表")</span> 的防呆是同一种工程品格——<strong>在数据迁移这种「错了就可能丢数据」的高危操作上，宁可保守地停下报错，绝不乐观地猜测推进。</strong>配合标记文件的「断点续跑」，整个迁移既能从中断处接着走，又绝不会在出错时把事情搞得更糟。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>V1 文件存储=键即路径的极简方案</strong>（<span class="mono">storage/storage.ts</span>）：<span class="mono">Storage</span> 服务 read/write/update/remove/list；<span class="mono">file(dir,key)=join(dir,...key)+".json"</span>，<span class="mono">string[]</span> 键直接拼成文件路径，整库=目录树；每文件 <span class="mono">TxReentrantLock</span> 读写锁，<span class="mono">update</span>=握写锁读改写。</li>
    <li><strong>简单的代价逼出迁移</strong>：文件存储无索引/无事务/无外键 cascade/无关系查询；SQLite（L48/L49）用一个数据库引擎换来这一切。文件 vs SQLite=简单受限 vs 复杂强大。</li>
    <li><strong>连文件存储也要迁移</strong>：<span class="mono">storage.ts</span> 内置 <span class="mono">MIGRATIONS</span> + <span class="mono">storage/migration</span> 标记（读标记→跑 pending→+1，失败 break，同 L48）。migration 1 用 git 根提交哈希当稳定项目 ID 重组布局；migration 2 抽 summary diff。</li>
    <li><strong>V1→V2 数据迁移用 data_migration 表记账</strong>（<span class="mono">data-migration.sql.ts</span>，name+time_completed）：与 L48 的 <span class="mono">migration</span> 表同款「记账即幂等」，一个管 schema、一个管数据搬运。</li>
    <li><strong>搬运与翻译解耦</strong>：V1 数据先原样搬进 SQLite <span class="mono">message</span>/<span class="mono">part</span> 表（data 列存 V1-shaped JSON=L49「V1 同堂」之源）；V1→V2 语义转换推迟到读取时由 <span class="mono">message-v2</span> 投影。让最危险的批量迁移退化成最无脑的字节复制。失败即 break 不前进（保守优于带病前进）。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Last lesson we saw something intriguing: the <span class="mono">message</span>/<span class="mono">part</span> tables in SQLite store <strong>V1</strong>-structured data. But that V1 data originally <strong>wasn't in SQLite at all</strong>—it lay in the file system, one JSON file per object. This lesson clarifies that "migration history": what opencode's <strong>V1 file storage</strong> looks like (<span class="mono">storage/storage.ts</span>), and how it migrates data scattered across thousands of JSON files <strong>into V2's SQLite</strong>. This isn't a corner detail but a real plot nearly every long-evolving software lives through: <strong>you start with the simplest storage scheme, run it a long time, until its simplicity starts to become a burden, and then you must, without losing a single piece of old data, move your whole household into a stronger new scheme.</strong></p>
<p>This lesson's insight has two layers. First, the <strong>"key-as-path" minimalist file storage</strong>: V1 stores each object as a JSON file, using a <span class="mono">string[]</span> array as the key, directly mapped to a nested file path—<span class="mono">read(["session", projectID, sessionID])</span> reads <span class="mono">storage/session/&lt;projectID&gt;/&lt;sessionID&gt;.json</span>. The whole "database" is a directory tree, plain enough to need no database engine. Second, <strong>the "journal-table bookkeeping" migration paradigm is reused twice</strong>: last lesson L48's schema migration uses a <span class="mono">migration</span> table recording "which structure changes ran"; this lesson's V1→V2 data migration uses <strong>another <span class="mono">data_migration</span> table</strong> recording "which data moves ran." The same "bookkeeping = idempotency" plain idea applied to two different problems. Grasp these two and you understand "how software gracefully grows from 'a pile of files' into 'a database' without shattering any old furniture mid-move."</p>

<div class="card analogy">
  <div class="tag">📦 Analogy</div>
  Picture V1 file storage as a <strong>small warehouse storing documents in shoeboxes</strong>: each document packed in its own shoebox (a JSON file), boxes placed by a "shelf→slot→position" label (<span class="mono">string[]</span> key as path). This approach is <strong>simple to the extreme</strong>—no manager, no database; finding a document is just following the label to fetch that box. But when documents grow to thousands, trouble comes: to "find all boxes labeled with some keyword" you must <strong>open every box and look</strong> (no index); to "change three boxes at once, all or nothing" you can't (no transaction); to "delete a project and all its documents" you must find and delete them one by one (no cascade). So you decide to <strong>move into a modern archive hall with a retrieval system</strong> (SQLite). The key discipline while moving: <strong>move a batch, tick a batch on the roster</strong> (the <span class="mono">data_migration</span> journal); should the power cut mid-move, after it returns, <strong>move only the unticked ones</strong> per the roster, never moving the same box twice nor missing any.
</div>

<h2>V1 file storage: a key-as-path minimalist scheme</h2>
<p>The <span class="mono">Storage</span> service in <span class="mono">storage.ts</span> is opencode's earliest persistence scheme, plain with only five methods:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">read(key)</div><div class="c-txt">read the JSON file for a key, NotFoundError if absent</div></div>
  <div class="cell"><div class="c-tag">write(key, content)</div><div class="c-txt">serialize content to JSON into the corresponding file (auto-mkdir)</div></div>
  <div class="cell"><div class="c-tag">update(key, fn)</div><div class="c-txt">read→modify→write back (read-modify-write in one, write-lock protected)</div></div>
  <div class="cell"><div class="c-tag">remove(key)</div><div class="c-txt">delete the corresponding file</div></div>
  <div class="cell"><div class="c-tag">list(prefix)</div><div class="c-txt">list all keys under a prefix (glob the directory tree)</div></div>
</div>
<p>The core magic is one line: <span class="mono">file(dir, key) = path.join(dir, ...key) + ".json"</span>—joining the <span class="mono">string[]</span> key <strong>directly into a file path</strong>. So the key <span class="mono">["session", "proj_abc", "ses_123"]</span> corresponds to the file <span class="mono">storage/session/proj_abc/ses_123.json</span> on disk. The whole "database" <strong>is a directory tree under <span class="mono">Global.Path.data/storage</span></strong>, each leaf a JSON file. A few key-to-file mapping examples make it instantly clear:</p>
<table class="t">
  <tr><th>string[] key</th><th>file on disk</th></tr>
  <tr><td><span class="mono">["session", "proj_abc", "ses_123"]</span></td><td><span class="mono">storage/session/proj_abc/ses_123.json</span></td></tr>
  <tr><td><span class="mono">["message", "ses_123", "msg_1"]</span></td><td><span class="mono">storage/message/ses_123/msg_1.json</span></td></tr>
  <tr><td><span class="mono">["part", "msg_1", "prt_9"]</span></td><td><span class="mono">storage/part/msg_1/prt_9.json</span></td></tr>
</table>
<p>This "key-as-path, object-as-file" design is <strong>shockingly simple</strong>—no database engine needed, and the files are human-readable and debuggable, a most reasonable starting point for an early project. To avoid trouble when multiple readers/writers run concurrently, each file path also has a <span class="mono">TxReentrantLock</span> (read/write lock): <span class="mono">read</span> takes a read lock, <span class="mono">write</span>/<span class="mono">update</span> a write lock, and <span class="mono">update</span>'s "read→modify→write back" holds the write lock throughout, avoiding two writers overwriting each other. Worth noting is <span class="mono">list(prefix)</span>: with no index available, it can only glob the whole subtree, reverse each file path back to a key, and sort—exactly the most direct manifestation of "no index" in file storage: to enumerate a class of objects, you can only walk the directory.</p>
<p>But "simple" has a cost, and these very costs, surfacing one by one as data volume and feature complexity grew, eventually forced the migration to SQLite:</p>
<div class="cols">
  <div class="col"><h4>file storage · simple but limited</h4><p>one object one JSON file, key as path, human-readable. But: <strong>no index</strong> (query = scan all files), <strong>no cross-object transaction</strong> (changing multiple files can't be atomic), <strong>no foreign-key cascade</strong> (deleting a project means manually clearing children), <strong>no relational query</strong> ("fetch this conversation by seq" can't be done).</p></div>
  <div class="col"><h4>SQLite · complex but powerful</h4><p>all objects into tables. In return: <strong>indices</strong> (efficient query/sort), <strong>transactions</strong> (multi-table atomic up/down), <strong>foreign-key cascade</strong> (delete root uproots all, L49), <strong>relational query</strong> (unique(session,seq) orders, L49). The cost: introducing a database engine.</p></div>
</div>

<h2>Even file storage needs migrations: internal layout evolution</h2>
<p>Interestingly, <strong>even a pile of files can't escape schema/layout evolution</strong>. <span class="mono">storage.ts</span> itself has a built-in set of file-layout migrations (the <span class="mono">MIGRATIONS</span> array), using a <span class="mono">storage/migration</span> marker file to record "how many ran." Its run logic is just like L48: read the marker → run migrations not yet run from there on → bump the marker by 1 for each success (stop without advancing on failure):</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">read the <span class="mono">storage/migration</span> marker file → an integer N (0 if absent)</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">from the Nth migration, run <span class="mono">MIGRATIONS[N..]</span> one by one</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">each success → write the marker to N+1 (idempotent: restart resumes from the marker)</span></div>
  <div class="t-row"><span class="t-num">!</span><span class="t-txt">some failure → logError and break, don't advance the marker (retry next time)</span></div>
</div>
<p>What real work does this layout migration do? <span class="mono">migration 1</span> makes it clear: early opencode used the <strong>directory name</strong> as the project ID, but directory names are unstable. So this migration did something clever—it opens each project's session message files, finds its git worktree, then uses <span class="mono">git rev-list --max-parents=0 --all</span> to get the <strong>repo's root commit hash</strong>, using this never-changing hash as a stable project ID, reorganizing the data into the new <span class="mono">session/&lt;projectID&gt;/</span>, <span class="mono">message/&lt;sessionID&gt;/</span>, <span class="mono">part/&lt;messageID&gt;/</span> layout. <span class="mono">migration 2</span> extracts the diff details from session summaries into separate <span class="mono">session_diff/</span> files and trims the summary to additions/deletions totals. <strong>This confirms L48's truth holds in the file world too: data structures are never finalized—even "a pile of JSON files" needs a versioned, idempotent, resumable migration mechanism to manage its evolution.</strong></p>

<h2>V1→V2: moving files into SQLite</h2>
<p>When opencode decided to upgrade from "a pile of files" to "a SQLite database" (L48/L49), it needed a <strong>big data migration</strong>: read out the sessions, messages, parts in V1 files and write them into SQLite tables. This migration's "ledger" is that plainly-two-column table in <span class="mono">data-migration.sql.ts</span>:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">data_migration table</div><div class="c-txt"><span class="mono">name</span>(PK) + <span class="mono">time_completed</span>—records "which data migration completed"</div></div>
  <div class="cell"><div class="c-tag">vs L48's migration table</div><div class="c-txt">same two columns, same "bookkeeping = idempotency"; difference: migration records <strong>schema</strong> changes, data_migration records <strong>data</strong> moves</div></div>
  <div class="cell"><div class="c-tag">landing: V1-shaped SQLite tables</div><div class="c-txt">V1 data moves into <span class="mono">message</span>/<span class="mono">part</span> tables, the <span class="mono">data</span> column still V1-shaped JSON (the "V1 under one roof" seen in L49)</div></div>
</div>
<p>Connecting the whole migration path gives this pipeline:</p>
<div class="flow">
  <div class="f-node">V1 JSON files<br><small>storage/session/…, message/…</small></div>
  <div class="f-arrow">read out →</div>
  <div class="f-node">move one by one<br><small>check data_migration ledger, skip moved</small></div>
  <div class="f-arrow">write in →</div>
  <div class="f-node">SQLite message/part tables<br><small>data column holds V1-shaped JSON</small></div>
  <div class="f-arrow">on read →</div>
  <div class="f-node">V2 projection<br><small>message-v2 projects V1 rows into V2 structure</small></div>
</div>
<p>There's a very pragmatic design here: when V1 data moves into SQLite, it's <strong>not immediately "translated" into V2 structure</strong>—it still lies as V1-shaped JSON verbatim in the <span class="mono">message</span>/<span class="mono">part</span> tables' <span class="mono">data</span> column (exactly the source of L49's "V1 under one roof"). The real "V1→V2 semantic conversion" <strong>happens on demand at read time</strong>: <span class="mono">message-v2.ts</span> reads V1 rows from <span class="mono">PartTable</span>/<span class="mono">MessageTable</span> and <strong>projects them on the spot into V2 message structures</strong> for upper layers.</p>
<p>This "<strong>move the bytes verbatim first, defer semantic conversion to read time</strong>" strategy is exceptionally clever: it makes <strong>the data-migration step simple and safe</strong>—just copy file content into tables, not touching a byte of semantics, minimizing error risk; while the complex, mutable "how V1 semantics map to V2" logic stays maintained in one place on the read path, changeable anytime. <strong>Decoupling "moving" from "translating," letting the most dangerous bulk data migration degrade into the most brainless byte copy</strong>—a wisdom in large data migrations worth savoring repeatedly.</p>
<p>It also brings a side benefit: should you one day find the "V1→V2 semantic mapping" was written wrong, you <strong>needn't rerun that costly big data migration</strong>—just fix the read-time projection and re-read, because the original V1 bytes <strong>stay untouched in the DB the whole time</strong>. Original data not destructively rewritten always leaves a "re-interpret" escape route—this "preserve the original, interpret on demand" restraint is the same foresight as L42's bounded output "spill the full text, fetch on demand" and L43's skills "names resident, body on demand."</p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>This lesson clarifies opencode's migration history from V1 file storage to V2 SQLite:</p>
  <ul>
    <li><strong>V1 file storage</strong> (<span class="mono">storage/storage.ts</span>): the <span class="mono">Storage</span> service read/write/update/remove/list; core <span class="mono">file(dir,key)=join(dir,...key)+".json"</span>—<span class="mono">string[]</span> key as file path, the whole DB a directory tree under <span class="mono">Global.Path.data/storage</span>; each file has a <span class="mono">TxReentrantLock</span> read/write lock, <span class="mono">update</span> = hold write lock read-modify-write.</li>
    <li><strong>simplicity's cost</strong>: file storage has no index / no cross-object transaction / no FK cascade / no relational query—exactly what forced the migration to SQLite (L48/L49 gave index/transaction/cascade/relational query).</li>
    <li><strong>even files need migrations</strong>: <span class="mono">storage.ts</span> has built-in <span class="mono">MIGRATIONS</span> + a <span class="mono">storage/migration</span> marker, logic like L48 (read marker→run pending→marker+1, break on failure). migration 1 uses the git root commit hash (<span class="mono">rev-list --max-parents=0</span>) as a stable project ID to reorganize layout; migration 2 extracts summary diffs.</li>
    <li><strong>V1→V2 data migration</strong>: the <span class="mono">data_migration</span> table (name+time_completed) bookkeeps, same "bookkeeping = idempotency" as L48's <span class="mono">migration</span> table (one records schema, one records data). V1 files move into SQLite <span class="mono">message</span>/<span class="mono">part</span> tables still holding V1-shaped JSON; semantic conversion deferred to read time, projected by <span class="mono">message-v2</span>—"moving" decoupled from "translating."</li>
  </ul>
  <p>By here "where data comes from, how it's stored, how it's moved" is fully explained. M9 has one lesson left, L51: when a session is <strong>too long</strong> (messages overflowing the context), how to <strong>compact</strong> and <strong>summarize</strong> it; and how opencode does <strong>snapshots and revert</strong> with git integration, letting you roll the working directory back to a moment in conversation history. Compaction and snapshots are higher-order "memory management" atop "persistence."</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p><span class="mono">storage.ts</span>'s migration driver loop writes "resumable + stop-on-failure" with restraint (simplified from source):</p>
  <pre class="code"><span class="cm">// read the marker file: which migration we reached (0 if absent)</span>
<span class="kw">const</span> migration = <span class="kw">yield*</span> fs.<span class="fn">readFileString</span>(marker).<span class="fn">pipe</span>(
  Effect.<span class="fn">map</span>(parseMigration),
  Effect.<span class="fn">catchIf</span>(missing, () =&gt; Effect.<span class="fn">succeed</span>(<span class="nu">0</span>)),   <span class="cm">// file absent = start from 0</span>
)
<span class="kw">for</span> (<span class="kw">let</span> i = migration; i &lt; MIGRATIONS.length; i++) {
  <span class="kw">const</span> exit = <span class="kw">yield*</span> Effect.<span class="fn">exit</span>(<span class="fn">step</span>(dir, fs, git))
  <span class="kw">if</span> (Exit.<span class="fn">isFailure</span>(exit)) {
    <span class="kw">yield*</span> Effect.<span class="fn">logError</span>(<span class="st">"failed to run migration"</span>, { index: i, cause: exit.cause })
    <span class="kw">break</span>                                <span class="cm">// ← stop on failure, don't advance marker → retry this one next time</span>
  }
  <span class="kw">yield*</span> fs.<span class="fn">writeWithDirs</span>(marker, <span class="fn">String</span>(i + <span class="nu">1</span>))   <span class="cm">// advance only on success</span>
}</pre>
  <p>What's most worth savoring is that <span class="mono">break</span>'s <strong>restraint</strong>: the moment a migration fails, it <strong>stops immediately, never jumps ahead to run later ones</strong>, and <strong>doesn't advance the marker</strong>. Why so conservative? Because migrations often have <strong>order dependencies</strong>—a later migration likely assumes the prior one already shaped the data a certain way. If the prior failed and you barrel ahead, you very likely make a bigger mess on a <strong>half-broken data state</strong>, ending in unsalvageable corruption. "Stop in place on failure, retry this one next time" is far safer than "advance while sick." This is the same engineering character as L48 schema migration's <span class="mono">die("DB non-empty yet has no session table")</span> guard—<strong>on a high-risk operation like data migration where "a slip can lose data," rather conservatively stop and error than optimistically guess and advance.</strong> Paired with the marker file's "resumable from interruption," the whole migration both continues from where it stopped and never makes things worse on error.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>V1 file storage = key-as-path minimalist scheme</strong> (<span class="mono">storage/storage.ts</span>): the <span class="mono">Storage</span> service read/write/update/remove/list; <span class="mono">file(dir,key)=join(dir,...key)+".json"</span>, <span class="mono">string[]</span> key joined directly into a file path, the whole DB a directory tree; each file a <span class="mono">TxReentrantLock</span> read/write lock, <span class="mono">update</span> = hold write lock read-modify-write.</li>
    <li><strong>simplicity's cost forces migration</strong>: file storage has no index / no transaction / no FK cascade / no relational query; SQLite (L48/L49) buys all this with a database engine. files vs SQLite = simple-limited vs complex-powerful.</li>
    <li><strong>even file storage needs migrations</strong>: <span class="mono">storage.ts</span> has built-in <span class="mono">MIGRATIONS</span> + a <span class="mono">storage/migration</span> marker (read marker→run pending→+1, break on failure, like L48). migration 1 uses the git root commit hash as a stable project ID to reorganize layout; migration 2 extracts summary diffs.</li>
    <li><strong>V1→V2 data migration bookkept by data_migration table</strong> (<span class="mono">data-migration.sql.ts</span>, name+time_completed): same "bookkeeping = idempotency" as L48's <span class="mono">migration</span> table, one managing schema, one managing data moves.</li>
    <li><strong>moving decoupled from translating</strong>: V1 data moves into SQLite <span class="mono">message</span>/<span class="mono">part</span> tables verbatim first (data column holds V1-shaped JSON = source of L49's "V1 under one roof"); V1→V2 semantic conversion deferred to read time, projected by <span class="mono">message-v2</span>. Lets the most dangerous bulk migration degrade into the most brainless byte copy. Break on failure without advancing (conservative beats advancing-while-sick).</li>
  </ul>
</div>
""",
}
LESSON_51 = {
    "zh": r"""
<p class="lead">前三课（L48–50）讲的都是「把数据忠实地存好、搬好」——SQLite 地基、核心表网、V1→V2 迁移。但光会存还不够。这一课讲<strong>「持久化」之上更高阶的「记忆管理」</strong>，它要解决两个真实的痛点。第一个痛点是<strong>记忆太多</strong>：一场对话越聊越长，消息多到撑爆模型有限的上下文窗口怎么办？答案是<strong>压缩（compaction）与摘要</strong>——把陈旧的对话折叠成一份结构化摘要，只留最近的若干轮原文。第二个痛点是<strong>想回到过去</strong>：agent 改了一堆文件，你后悔了，想把对话和工作目录一起<strong>退回到几步之前</strong>怎么办？答案是 <strong>快照（snapshot）与 revert</strong>——opencode 用一个巧妙的「影子 git 仓库」给工作目录做时间机器。压缩管「记忆的容量」，快照管「记忆的时间轴」，两者合起来，才让 agent 的「记忆」既装得下、又退得回。</p>
<p>这一课有两个最值得带走的设计。其一，<strong>压缩 = 「留近况原文 + 把远的折成结构化摘要」</strong>：当对话的 token 估算超出上下文窗口（减去输出余量），opencode 自动把最近约 8000 token 的对话<strong>原样保留</strong>、把更早的对话交给 LLM<strong>填进一张固定结构的摘要模板</strong>（目标/约束/进展/决策/下一步/关键上下文/相关文件），而且这份摘要是<strong>「锚定式」增量更新</strong>的——下次压缩不重写，而是在旧摘要上「保留仍成立的、删过时的、并入新的」。</p>
<p>其二，<strong>快照 = 「影子 git 仓库」</strong>：opencode 不动你真实的 <span class="mono">.git</span>，而是在数据目录下另起一个独立的 git 仓库（<span class="mono">--git-dir</span> 指向它、<span class="mono">--work-tree</span> 指向你的真实工作目录），用 <span class="mono">git write-tree</span> 给工作目录拍一张「树快照」、用 <span class="mono">read-tree</span>+<span class="mono">checkout-index</span> 还原。<strong>它把 git 强大的内容寻址存储借来当时间机器，却绝不污染你自己的提交历史。</strong></p>
<p>读懂这两笔，你就懂了「一个 agent 如何在有限的上下文里装下无限长的对话，又如何安全地给你一颗『后悔药』」。</p>

<div class="card analogy">
  <div class="tag">⏳ 生活类比</div>
  把<strong>压缩</strong>想象成一场冗长会议的<strong>「会议纪要」</strong>：你不会把三小时的逐字录音从头听一遍，而是手边备一份<strong>结构化纪要</strong>（议题、决定、待办……）外加<strong>最近十分钟的原话</strong>——纪要随会议推进不断<strong>增补改写</strong>，而非每次重写。这正是 compaction 的做法：远的折成摘要、近的留原文、摘要锚定式更新。再把<strong>快照</strong>想象成电子游戏的<strong>「存档点」</strong>：你在关键处存个档，万一后面玩砸了，<strong>读档退回</strong>那一刻重来。妙的是 opencode 的存档<strong>放在一个独立的存档文件里</strong>（影子 git 仓库），跟你正在玩的「主进度」（你真实的 git 提交历史）<strong>井水不犯河水</strong>——它给你随便存随便读的自由，却绝不弄乱你自己的存档。而 <strong>revert</strong>，就是「读档」：把对话和你的文件<strong>一起</strong>退回到某条消息时的样子；而且还能<strong>反悔（unrevert）</strong>，因为读档前它偷偷又存了一档。
</div>

<h2>压缩与摘要：把长对话折叠进上下文</h2>
<p>模型的上下文窗口是有限且昂贵的（M5、L42 反复强调过这点）。当一场对话的消息累积到<strong>快要撑爆窗口</strong>时，<span class="mono">compaction.ts</span> 的 <span class="mono">compactIfNeeded</span> 就会触发：它估算整个请求（system + messages + tools）的 token，一旦超过 <span class="mono">上下文 − max(输出量, 缓冲)</span>（缓冲默认 20000 token），就启动压缩。压缩的核心是 <span class="mono">select</span> 函数那一刀<strong>「切分」</strong>：</p>
<div class="cols">
  <div class="col"><h4>recent · 近况留原文</h4><p>从对话末尾往前累加，保留最近约 <strong>8000 token</strong>（<span class="mono">DEFAULT_KEEP_TOKENS</span>）的消息<strong>逐字原样</strong>。最近的来回往往最相关——模型刚做了什么、你刚说了什么，必须精确无损。</p></div>
  <div class="col"><h4>head · 远的折成摘要</h4><p>更早的那一大段对话，<strong>不再逐字保留</strong>，而是交给 LLM 浓缩成一份结构化摘要。陈年细节用摘要「够用就好」，把宝贵的上下文额度让给近况和摘要。</p></div>
</div>
<p>那份摘要不是随意的散文，而是填进一张<strong>固定结构的模板</strong>（<span class="mono">SUMMARY_TEMPLATE</span>）——这保证了无论压缩多少次，关键维度都不丢：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">Goal</div><div class="c-txt">一句话任务目标</div></div>
  <div class="cell"><div class="c-tag">Constraints &amp; Preferences</div><div class="c-txt">用户的约束、偏好、规格</div></div>
  <div class="cell"><div class="c-tag">Progress（Done/In Progress/Blocked）</div><div class="c-txt">已完成 / 进行中 / 受阻</div></div>
  <div class="cell"><div class="c-tag">Key Decisions</div><div class="c-txt">关键决策及其理由</div></div>
  <div class="cell"><div class="c-tag">Next Steps</div><div class="c-txt">有序的下一步行动</div></div>
  <div class="cell"><div class="c-tag">Critical Context / Relevant Files</div><div class="c-txt">关键技术事实、报错、未决问题 / 相关文件及其意义</div></div>
</div>
<p>整条压缩流水线串起来是这样的：</p>
<div class="flow">
  <div class="f-node">估算请求 token<br><small>超过 上下文−max(输出,缓冲)?</small></div>
  <div class="f-arrow">溢出 →</div>
  <div class="f-node">select 切分<br><small>head(远) / recent(近)</small></div>
  <div class="f-arrow">summarize →</div>
  <div class="f-node">LLM 填摘要模板<br><small>无工具、限 4096 token</small></div>
  <div class="f-arrow">产出 →</div>
  <div class="f-node">compaction 消息<br><small>{summary, recent} 替代远段</small></div>
</div>
<p>最见功力的是<strong>「锚定式增量摘要」</strong>：如果这场对话<strong>之前已经压缩过</strong>（历史里已有一条 <span class="mono">compaction</span> 消息），这次不会从头重写摘要，而是把旧摘要塞进提示里，让模型「<strong>用上面的对话历史更新这份锚定摘要：保留仍成立的细节、删掉过时的、并入新事实</strong>」。为什么这很重要？因为摘要本身会被<strong>反复压缩</strong>——如果每次都从仅剩的近况重新生成，越早的信息会在一次次压缩中被<strong>逐渐稀释、最终遗忘</strong>。</p>
<p>而「锚定 + 增量更新」让那份摘要像一条<strong>不断被修订、却始终连续的主线</strong>，把整场对话从头到尾的关键脉络<strong>一路传下去</strong>，不因压缩而断裂。这和 L42「有界输出」是同一种哲学在不同层级的回响：L42 管<strong>单个工具输出</strong>别撑爆上下文，压缩管<strong>整场对话</strong>别撑爆上下文——稀缺的永远是模型那点宝贵的注意力。</p>

<h2>快照：给工作目录开一个「影子 git 仓库」</h2>
<p>压缩管的是「对话记忆」，而快照管的是「文件记忆」——agent 改了你的代码，怎么能让你<strong>退回到改之前</strong>？<span class="mono">snapshot/index.ts</span> 的答案巧妙得令人拍案：<strong>另起一个影子 git 仓库</strong>。它绝不碰你项目里真实的 <span class="mono">.git</span>，而是在 <span class="mono">数据目录/snapshot/&lt;项目&gt;/&lt;工作目录哈希&gt;</span> 下建一个<strong>独立的 git 仓库</strong>，所有 git 命令都带上 <span class="mono">--git-dir &lt;影子仓库&gt; --work-tree &lt;你的真实工作目录&gt;</span>：</p>
<div class="layers">
  <div class="layer"><span class="l-tag">你的真实仓库</span><span class="l-desc"><span class="mono">项目/.git</span>——你自己的提交历史，opencode <strong>一个字节都不碰</strong></span></div>
  <div class="layer"><span class="l-tag">影子快照仓库</span><span class="l-desc"><span class="mono">数据目录/snapshot/…</span>——独立 git-dir，<span class="mono">--work-tree</span> 指向你的真实工作目录</span></div>
  <div class="layer"><span class="l-tag">共享对象（alternates）</span><span class="l-desc">影子仓库通过 <span class="mono">objects/info/alternates</span> 复用真实仓库的 git 对象，巨型仓库也不重复占空间</span></div>
</div>
<p>「拍快照」与「还原」用的都是 git 的底层管道命令，轻量得很：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">track()</div><div class="c-txt"><span class="mono">git add</span> 暂存工作目录改动 → <span class="mono">git write-tree</span> 写出一个<strong>树对象</strong>，返回它的哈希——这个哈希就是一张「快照」</div></div>
  <div class="cell"><div class="c-tag">restore(snapshot)</div><div class="c-txt"><span class="mono">git read-tree &lt;快照&gt;</span> + <span class="mono">checkout-index -a -f</span> → 把工作目录的文件<strong>还原</strong>到那张树快照的样子</div></div>
  <div class="cell"><div class="c-tag">diff / patch</div><div class="c-txt">对比某快照与当前工作目录，算出改了哪些文件、增删多少行</div></div>
</div>
<p>这套设计有三处特别值得品。其一，用 <span class="mono">write-tree</span> 而非 <span class="mono">commit</span>：只需要捕获「文件状态」这一棵树，不需要提交信息、作者、父提交那一整套——<strong>用最轻的 git 原语干最纯粹的事</strong>。其二，<strong>影子仓库与真实 <span class="mono">.git</span> 彻底隔离</strong>：opencode 频繁地拍快照（几乎每步工具操作前后），如果这些都污染你的提交历史，那将是灾难；放进影子仓库，你的 <span class="mono">git log</span> 永远干干净净。其三，<strong>复用 git 而非自己造轮子</strong>：工作目录的版本管理是个难题（增量存储、内容去重、高效 diff），而 git 二十年磨一剑的内容寻址存储正是为此而生——opencode 像 L39 复用 Ripgrep、L35 复用上游模型目录一样，<strong>把这件难事交给久经考验的 git</strong>，自己只负责「在影子仓库里、什么时候、拍哪一张」。它还顺带尊重你的 <span class="mono">.gitignore</span>、屏蔽超大文件，让快照既准又省。</p>
<p>这种「复用 git」的思路在 opencode 里还有第二处落点：<strong>worktree（工作树）</strong>（<span class="mono">opencode/src/worktree/index.ts</span>）。git 的 worktree 能从同一个仓库<strong>检出多份相互隔离的工作副本</strong>，opencode 借它给一次运行开一个<strong>隔离的工作目录</strong>——发 <span class="mono">worktree.ready</span> / <span class="mono">worktree.failed</span> 事件标志就绪或失败。这和「影子 git 快照」是同一种智慧的两面：快照是「在原地给历史拍照」，worktree 是「另起一处干净副本干活、互不打扰」；前者管「能退回」，后者管「能隔离」。它也呼应第 61 课 move-session 的「会话可搬家」——都建立在「把『在哪儿干活』与『干什么』解耦」的地基上。</p>

<h2>Revert：把对话与文件一起退回过去</h2>
<p>压缩（对话记忆）和快照（文件记忆）合体，就有了 <strong>revert</strong>——一颗真正的「后悔药」。<span class="mono">revert.ts</span> 让你指定退回到某条消息（<span class="mono">messageID</span>，可细到 <span class="mono">partID</span>），它做的是<strong>两件事的合体</strong>：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">退对话</div><div class="c-txt">把该消息<strong>之后</strong>的消息从可见历史里裁掉——对话回到那一刻</div></div>
  <div class="cell"><div class="c-tag">退文件</div><div class="c-txt"><span class="mono">snap.revert(补丁)</span> 把改动过的文件逐一还原——文件回到那一刻</div></div>
  <div class="cell"><div class="c-tag">可反悔</div><div class="c-txt">revert 前先 <span class="mono">snap.track()</span> 存下当前状态；<span class="mono">unrevert</span> 再用 <span class="mono">snap.restore</span> 整体还原回去——后悔药也有后悔药</div></div>
</div>
<p>这个「可反悔」的设计尤其周到：<span class="mono">revert</span> 在还原之前，会<strong>先给「现在」拍一张快照</strong>存进 session 的 <span class="mono">revert</span> 字段（还记得 L49 session 表那个 <span class="mono">revert: {messageID, partID?, snapshot?, diff?}</span> JSON 列吗？这里正是它的用武之地）。于是 <span class="mono">unrevert</span> 能把你<strong>带回 revert 之前的那一刻</strong>——退回过去之后，你<strong>还能反悔退回的动作本身</strong>。（细分一下：前进的 revert 用 <span class="mono">snap.revert</span> 按补丁把改动过的文件逐一退回，而 unrevert 用 <span class="mono">snap.restore</span> 把 revert 前那张整快照一次性还原。）把这条时间轴画出来：</p>
<div class="timeline">
  <div class="tl-item"><div class="tl-time">每步</div><div class="tl-text">工具操作前后 track() 不断拍快照</div></div>
  <div class="tl-item"><div class="tl-time">revert</div><div class="tl-text">先 track 存下「现在」→ snap.revert 把改动过的文件退回消息 N 时的状态 + 裁掉 N 之后的消息</div></div>
  <div class="tl-item"><div class="tl-time">结果</div><div class="tl-text">对话与文件一起回到消息 N 那一刻</div></div>
  <div class="tl-item"><div class="tl-time">unrevert</div><div class="tl-text">snap.restore 回 revert 前存下的快照——反悔成功</div></div>
</div>
<p>把对话与文件<strong>绑定在同一条时间轴上一起回退</strong>，是 revert 最关键的洞见：单退对话不退文件，你会面对「对话以为没改过、文件却已被改」的错乱；单退文件不退对话同理。唯有<strong>两者作为一个整体一起回到过去</strong>，那一刻的世界才是自洽的。这背后是 L49 那张 session 表的 <span class="mono">revert</span> 列在默默支撑——状态被持久化，所以哪怕重启，这颗「后悔药」依然有效。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观视角</div>
  <p>这一课讲清了「持久化」之上的「记忆管理」——容量与时间轴两个维度：</p>
  <ul>
    <li><strong>压缩与摘要</strong>（<span class="mono">session/compaction.ts</span>）：<span class="mono">compactIfNeeded</span> 在请求 token &gt; <span class="mono">上下文−max(输出,缓冲20k)</span> 时触发；<span class="mono">select</span> 切分=近况留原文(<span class="mono">DEFAULT_KEEP_TOKENS</span>≈8k)+远的折成结构化摘要(固定模板 Goal/Constraints/Progress/Decisions/Next Steps/Context/Files)；LLM 无工具限 4096 token 生成；<strong>锚定式增量更新</strong>（旧摘要上保留/删除/并入，主线不断裂）。回响 L42「上下文稀缺」。</li>
    <li><strong>快照=影子 git 仓库</strong>（<span class="mono">snapshot/index.ts</span>）：独立 <span class="mono">--git-dir</span>（数据目录下）+ <span class="mono">--work-tree</span> 指真实工作目录，<strong>绝不碰你的 .git</strong>；<span class="mono">track</span>=<span class="mono">write-tree</span> 出树哈希、<span class="mono">restore</span>=<span class="mono">read-tree</span>+<span class="mono">checkout-index</span>；<span class="mono">alternates</span> 共享对象省空间、尊重 .gitignore、屏蔽大文件。复用 git（如 L39 复用 Ripgrep）。</li>
    <li><strong>Revert=对话+文件一起回退</strong>（<span class="mono">session/revert.ts</span>）：退对话(裁掉消息 N 之后)+退文件(<span class="mono">snap.revert</span> 按补丁逐一还原改动过的文件)；<strong>可反悔</strong>（revert 前先 track 存当前→unrevert 用 <span class="mono">snap.restore</span> 整体还原），状态存进 L49 session 表的 <span class="mono">revert</span> JSON 列，重启仍有效。</li>
    <li><strong>统一主题</strong>：L48–50 忠实地<strong>存</strong>，L51 智慧地<strong>管</strong>——压缩管记忆容量、快照/revert 管记忆时间轴。对话与文件绑在同一时间轴一起回退，那一刻的世界才自洽。</li>
  </ul>
  <p>至此 <strong>M9 持久化与存储</strong>全部讲完：从 Drizzle/SQLite 地基（L48）、核心表网（L49）、V1→V2 迁移（L50），到这一课的压缩与快照/revert（L51）——opencode 如何忠实地存、安全地搬、智慧地管它的全部「记忆」。下一部分 <strong>M10 转向 TUI 与客户端渲染</strong>：这些存下来的会话、消息、上下文，最终怎样在你的终端里被渲染成一个流畅的交互界面。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p><span class="mono">select</span> 函数从对话末尾倒着走、按 token 切「近况/远段」，连切分点的那条消息都能从中间劈开（简化自 <span class="mono">compaction.ts</span>）：</p>
  <pre class="code"><span class="cm">// 从最后一条往前累加 token，直到超过要保留的额度</span>
<span class="kw">for</span> (<span class="kw">let</span> index = conversation.length - <span class="nu">1</span>; index &gt;= <span class="nu">0</span>; index--) {
  <span class="kw">const</span> next = total + Token.<span class="fn">estimate</span>(conversation[index])
  <span class="kw">if</span> (next &gt; tokens) {                       <span class="cm">// 这条会超额</span>
    <span class="kw">const</span> remaining = Math.<span class="fn">max</span>(<span class="nu">0</span>, tokens - total) * <span class="nu">4</span>   <span class="cm">// 还能塞的字符数(≈token×4)</span>
    <span class="kw">if</span> (remaining &gt; <span class="nu">0</span>) {
      splitPrefix = conversation[index].<span class="fn">slice</span>(<span class="nu">0</span>, -remaining)   <span class="cm">// 前半→归入远段(摘要)</span>
      splitSuffix = conversation[index].<span class="fn">slice</span>(-remaining)    <span class="cm">// 后半→归入近况(原文)</span>
      split = index + <span class="nu">1</span>
    }
    <span class="kw">break</span>
  }
  total = next
  split = index
}
<span class="cm">// head=远段(待摘要)，recent=近况(留原文)</span>
<span class="kw">return</span> {
  head: [...conversation.<span class="fn">slice</span>(<span class="nu">0</span>, split), splitPrefix].<span class="fn">filter</span>(Boolean).<span class="fn">join</span>(<span class="st">"\n\n"</span>),
  recent: [splitSuffix, ...conversation.<span class="fn">slice</span>(split)].<span class="fn">filter</span>(Boolean).<span class="fn">join</span>(<span class="st">"\n\n"</span>),
}</pre>
  <p>最妙的是它<strong>连一条消息都能从中间劈开</strong>：当累加到某条消息会超出保留额度、但还剩一点空间时，它把这条消息<strong>按剩余字符数切两半</strong>——前半 <span class="mono">splitPrefix</span> 并入待摘要的 <span class="mono">head</span>、后半 <span class="mono">splitSuffix</span> 留进逐字保留的 <span class="mono">recent</span>（这里 <span class="mono">×4</span> 是「1 token ≈ 4 字符」的粗略换算）。为什么要这么细？因为消息有长有短，若只能<strong>整条整条地切</strong>，碰上一条特别长的消息卡在边界上，就只能要么全摘要、要么全保留，白白浪费或挤占宝贵的额度。<strong>允许从消息中间切，是把「保留最近 N token」这个预算用到极致的关键</strong>——它让切分点能精确落在 token 预算上，而非被消息边界牵着走。这种「为了把稀缺资源用满，连最小单位都愿意再细分」的较真，正是 opencode 在上下文管理上一以贯之的克制与精打细算。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>压缩=近况留原文+远的折成摘要</strong>（<span class="mono">compaction.ts</span>）：请求 token 超 <span class="mono">上下文−max(输出,缓冲20k)</span> 触发；<span class="mono">select</span> 保留最近≈8k token 原文、其余交 LLM 填固定结构摘要模板（Goal/Constraints/Progress/Decisions/Next Steps/Context/Files）；可从单条消息中间切，把保留预算用到极致。</li>
    <li><strong>锚定式增量摘要</strong>：已压缩过则在旧摘要上「保留/删除/并入」而非重写，让主线跨多次压缩不断裂、不被逐渐稀释遗忘。同 L42「上下文稀缺」哲学的不同层级回响。</li>
    <li><strong>快照=影子 git 仓库</strong>（<span class="mono">snapshot/index.ts</span>）：独立 <span class="mono">--git-dir</span>+<span class="mono">--work-tree</span> 指真实工作目录，<strong>绝不碰你的 .git</strong>；<span class="mono">track</span>=<span class="mono">write-tree</span>（轻量树快照而非 commit）、<span class="mono">restore</span>=<span class="mono">read-tree</span>+<span class="mono">checkout-index</span>；alternates 共享对象、尊重 gitignore。复用 git 这把利器（如 L39 复用 Ripgrep）。</li>
    <li><strong>Revert=对话+文件一起回退</strong>（<span class="mono">revert.ts</span>）：退对话(裁消息 N 之后)+退文件(<span class="mono">snap.revert</span> 按补丁还原)绑在同一时间轴，那一刻才自洽；<strong>可 unrevert 反悔</strong>（revert 前先 track 存当前，unrevert 用 <span class="mono">snap.restore</span> 整体还原）。状态存进 L49 session 表 <span class="mono">revert</span> JSON 列、重启仍有效。</li>
    <li><strong>M9 收官</strong>：L48–50 忠实地存/搬，L51 智慧地管（容量靠压缩、时间轴靠快照/revert）。下一部分 M10 讲 TUI——这些记忆怎样在终端被渲染成交互界面。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">The last three lessons (L48–50) were all about faithfully storing and moving data—the SQLite foundation, the core table web, V1→V2 migration. But storing alone isn't enough. This lesson covers <strong>higher-order "memory management" atop "persistence,"</strong> solving two real pains. The first pain is <strong>too much memory</strong>: a conversation grows longer and longer, messages overflowing the model's limited context window—what then? The answer is <strong>compaction and summarization</strong>—folding stale conversation into a structured summary, keeping only the most recent few rounds verbatim. The second pain is <strong>wanting to go back in time</strong>: the agent changed a pile of files, you regret it, you want to roll the conversation and working directory <strong>back to a few steps ago</strong>—how? The answer is <strong>snapshots and revert</strong>—opencode gives the working directory a time machine via a clever "shadow git repo." Compaction manages "memory capacity," snapshots manage "memory's timeline"; together they let the agent's "memory" both fit and roll back.</p>
<p>This lesson has two designs most worth taking away. First, <strong>compaction = "keep recent verbatim + fold the far into a structured summary"</strong>: when the conversation's token estimate exceeds the context window (minus the output margin), opencode automatically keeps the most recent ~8000 tokens of conversation <strong>verbatim</strong> and hands the earlier conversation to the LLM to <strong>fill into a fixed-structure summary template</strong> (Goal/Constraints/Progress/Decisions/Next Steps/Critical Context/Relevant Files), and this summary is <strong>"anchored" incrementally updated</strong>—the next compaction doesn't rewrite but, on the old summary, "keeps still-true, removes stale, merges new."</p>
<p>Second, <strong>snapshot = a "shadow git repo"</strong>: opencode doesn't touch your real <span class="mono">.git</span> but spins up a separate git repo under the data directory (<span class="mono">--git-dir</span> pointing at it, <span class="mono">--work-tree</span> at your real working directory), using <span class="mono">git write-tree</span> to take a "tree snapshot" of the working directory and <span class="mono">read-tree</span>+<span class="mono">checkout-index</span> to restore. <strong>It borrows git's powerful content-addressable storage as a time machine, yet never pollutes your own commit history.</strong></p>
<p>Grasp these two and you'll understand "how an agent fits an infinitely long conversation into a limited context, and how it safely hands you a 'regret pill.'"</p>

<div class="card analogy">
  <div class="tag">⏳ Analogy</div>
  Picture <strong>compaction</strong> as a long meeting's <strong>"minutes"</strong>: you won't replay the three-hour verbatim recording from the top but keep at hand a <strong>structured minutes</strong> (topics, decisions, todos…) plus <strong>the last ten minutes' actual words</strong>—the minutes are <strong>amended and rewritten</strong> as the meeting proceeds, not rewritten each time. That's exactly compaction: fold the far into a summary, keep the near verbatim, anchored incremental update. Now picture <strong>snapshot</strong> as a video game's <strong>"save point"</strong>: you save at a key spot, and if you botch it later, <strong>load back</strong> to that moment and redo. The clever part is opencode's saves <strong>live in a separate save file</strong> (the shadow git repo), in <strong>strict non-interference</strong> with your "main progress" (your real git commit history)—it gives you free rein to save and load, yet never scrambles your own saves. And <strong>revert</strong> is "load": roll the conversation and your files <strong>together</strong> back to how they were at some message; and you can even <strong>take it back (unrevert)</strong>, because it quietly saved another file before loading.
</div>

<h2>Compaction and summary: folding a long conversation into context</h2>
<p>The model's context window is limited and expensive (M5, L42 stressed this repeatedly). When a conversation's messages accumulate to <strong>nearly overflowing the window</strong>, <span class="mono">compaction.ts</span>'s <span class="mono">compactIfNeeded</span> triggers: it estimates the whole request's (system + messages + tools) tokens, and once it exceeds <span class="mono">context − max(output, buffer)</span> (buffer defaults to 20000 tokens), starts compaction. Compaction's core is the <strong>"split"</strong> of the <span class="mono">select</span> function:</p>
<div class="cols">
  <div class="col"><h4>recent · keep the near verbatim</h4><p>Accumulating backward from the conversation's end, keep the most recent ~<strong>8000 tokens</strong> (<span class="mono">DEFAULT_KEEP_TOKENS</span>) of messages <strong>word-for-word</strong>. The recent exchanges are usually most relevant—what the model just did, what you just said, must be precise and lossless.</p></div>
  <div class="col"><h4>head · fold the far into a summary</h4><p>The big earlier stretch of conversation is <strong>no longer kept verbatim</strong> but handed to the LLM to condense into a structured summary. Aged detail "good enough" via summary, ceding the precious context budget to the recent and the summary.</p></div>
</div>
<p>That summary isn't arbitrary prose but filled into a <strong>fixed-structure template</strong> (<span class="mono">SUMMARY_TEMPLATE</span>)—this guarantees that no matter how many compactions, the key dimensions aren't lost:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">Goal</div><div class="c-txt">single-sentence task summary</div></div>
  <div class="cell"><div class="c-tag">Constraints &amp; Preferences</div><div class="c-txt">user constraints, preferences, specs</div></div>
  <div class="cell"><div class="c-tag">Progress (Done/In Progress/Blocked)</div><div class="c-txt">completed / current / blocked</div></div>
  <div class="cell"><div class="c-tag">Key Decisions</div><div class="c-txt">key decisions and their reasons</div></div>
  <div class="cell"><div class="c-tag">Next Steps</div><div class="c-txt">ordered next actions</div></div>
  <div class="cell"><div class="c-tag">Critical Context / Relevant Files</div><div class="c-txt">key technical facts, errors, open questions / relevant files and their significance</div></div>
</div>
<p>The whole compaction pipeline strung together:</p>
<div class="flow">
  <div class="f-node">estimate request tokens<br><small>over context−max(output,buffer)?</small></div>
  <div class="f-arrow">overflow →</div>
  <div class="f-node">select split<br><small>head(far) / recent(near)</small></div>
  <div class="f-arrow">summarize →</div>
  <div class="f-node">LLM fills the template<br><small>no tools, capped 4096 tokens</small></div>
  <div class="f-arrow">produce →</div>
  <div class="f-node">compaction message<br><small>{summary, recent} replaces the far</small></div>
</div>
<p>What shows the most craft is the <strong>"anchored incremental summary"</strong>: if this conversation has <strong>been compacted before</strong> (a <span class="mono">compaction</span> message already in history), this time it won't rewrite the summary from scratch but stuffs the old summary into the prompt, telling the model to "<strong>update this anchored summary using the conversation history above: preserve still-true details, remove stale ones, merge in new facts</strong>." Why does this matter? Because the summary itself gets <strong>repeatedly compacted</strong>—if each time it regenerated from only the surviving recent, the earliest information would be <strong>gradually diluted and finally forgotten</strong> across successive compactions.</p>
<p>"Anchored + incremental update" makes that summary like a <strong>continuously revised yet always continuous main thread</strong>, carrying the key throughline of the entire conversation from start to finish <strong>all the way down</strong>, unbroken by compaction. This is the same philosophy as L42's "bounded output" echoing at a different level: L42 keeps <strong>a single tool output</strong> from overflowing context, compaction keeps <strong>a whole conversation</strong> from overflowing context—the scarce thing is always the model's precious attention.</p>

<h2>Snapshots: opening a "shadow git repo" for the working directory</h2>
<p>Compaction manages "conversation memory," snapshots manage "file memory"—the agent changed your code, how can it let you <strong>roll back to before the change</strong>? <span class="mono">snapshot/index.ts</span>'s answer is admirably clever: <strong>spin up a shadow git repo</strong>. It never touches your project's real <span class="mono">.git</span> but builds a <strong>separate git repo</strong> under <span class="mono">data-dir/snapshot/&lt;project&gt;/&lt;worktree-hash&gt;</span>, all git commands carrying <span class="mono">--git-dir &lt;shadow repo&gt; --work-tree &lt;your real working directory&gt;</span>:</p>
<div class="layers">
  <div class="layer"><span class="l-tag">your real repo</span><span class="l-desc"><span class="mono">project/.git</span>—your own commit history, opencode <strong>touches not one byte</strong></span></div>
  <div class="layer"><span class="l-tag">shadow snapshot repo</span><span class="l-desc"><span class="mono">data-dir/snapshot/…</span>—a separate git-dir, <span class="mono">--work-tree</span> pointing at your real working directory</span></div>
  <div class="layer"><span class="l-tag">shared objects (alternates)</span><span class="l-desc">the shadow repo reuses the real repo's git objects via <span class="mono">objects/info/alternates</span>, no duplicate storage even on huge repos</span></div>
</div>
<p>Both "take a snapshot" and "restore" use git's low-level plumbing commands, very lightweight:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">track()</div><div class="c-txt"><span class="mono">git add</span> stages working-dir changes → <span class="mono">git write-tree</span> writes a <strong>tree object</strong>, returns its hash—that hash is a "snapshot"</div></div>
  <div class="cell"><div class="c-tag">restore(snapshot)</div><div class="c-txt"><span class="mono">git read-tree &lt;snapshot&gt;</span> + <span class="mono">checkout-index -a -f</span> → <strong>restore</strong> the working dir's files to that tree snapshot</div></div>
  <div class="cell"><div class="c-tag">diff / patch</div><div class="c-txt">compare a snapshot to the current working dir, computing which files changed and how many lines added/removed</div></div>
</div>
<p>This design has three points specially worth savoring. First, using <span class="mono">write-tree</span> not <span class="mono">commit</span>: it only needs to capture the "file state" as one tree, not the whole apparatus of commit message, author, parent commit—<strong>the lightest git primitive for the purest job</strong>. Second, <strong>the shadow repo is fully isolated from the real <span class="mono">.git</span></strong>: opencode snapshots frequently (around almost every tool operation); if these all polluted your commit history it'd be a disaster; put in the shadow repo, your <span class="mono">git log</span> stays forever clean. Third, <strong>reuse git rather than reinvent</strong>: version-managing a working directory is a hard problem (incremental storage, content dedup, efficient diff), and git's twenty-years-honed content-addressable storage is born for exactly this—opencode, like L39 reusing Ripgrep and L35 reusing the upstream model catalog, <strong>hands this hard thing to battle-tested git</strong>, owning only "in the shadow repo, when, take which snapshot." It also respects your <span class="mono">.gitignore</span> and blocks oversized files, keeping snapshots both accurate and frugal.</p>
<p>This "reuse git" idea has a second landing spot in opencode: <strong>worktrees</strong> (<span class="mono">opencode/src/worktree/index.ts</span>). git's worktree can check out <strong>multiple mutually-isolated working copies</strong> from the same repo, and opencode borrows it to give a run an <strong>isolated working directory</strong>—emitting <span class="mono">worktree.ready</span> / <span class="mono">worktree.failed</span> events to signal readiness or failure. This and "shadow-git snapshots" are two sides of the same wisdom: a snapshot is "photograph history in place," a worktree is "work in a fresh copy elsewhere, undisturbed"; the former handles "can revert," the latter "can isolate." It also echoes Lesson 61's move-session "a session can move"—both built on the foundation of "decoupling 'where you work' from 'what you do.'"</p>

<h2>Revert: rolling conversation and files back together</h2>
<p>Compaction (conversation memory) and snapshot (file memory) combined give <strong>revert</strong>—a real "regret pill." <span class="mono">revert.ts</span> lets you specify rolling back to a message (<span class="mono">messageID</span>, down to <span class="mono">partID</span>), doing a <strong>fusion of two things</strong>:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">rewind the conversation</div><div class="c-txt">trim messages <strong>after</strong> that message from visible history—the conversation returns to that moment</div></div>
  <div class="cell"><div class="c-tag">rewind the files</div><div class="c-txt"><span class="mono">snap.revert(patches)</span> reverts the changed files one by one—files return to that moment</div></div>
  <div class="cell"><div class="c-tag">reversible</div><div class="c-txt">before revert, <span class="mono">snap.track()</span> saves the current state; <span class="mono">unrevert</span> restores wholesale via <span class="mono">snap.restore</span>—even the regret pill has a regret pill</div></div>
</div>
<p>This "reversible" design is especially thoughtful: before restoring, <span class="mono">revert</span> <strong>first takes a snapshot of "now"</strong> and stores it in the session's <span class="mono">revert</span> field (remember L49's session-table <span class="mono">revert: {messageID, partID?, snapshot?, diff?}</span> JSON column? here's exactly where it earns its keep). So <span class="mono">unrevert</span> can <strong>bring you back to the moment before revert</strong>—after rolling back to the past, you <strong>can still take back the rollback itself</strong>. (To be precise: the forward revert uses <span class="mono">snap.revert</span> to roll the changed files back per-patch, while unrevert uses <span class="mono">snap.restore</span> to restore that whole pre-revert snapshot in one shot.) Drawing this timeline:</p>
<div class="timeline">
  <div class="tl-item"><div class="tl-time">each step</div><div class="tl-text">track() keeps snapshotting around tool operations</div></div>
  <div class="tl-item"><div class="tl-time">revert</div><div class="tl-text">first track to save "now" → snap.revert rolls the changed files back to message N's state + trim messages after N</div></div>
  <div class="tl-item"><div class="tl-time">result</div><div class="tl-text">conversation and files return together to the moment of message N</div></div>
  <div class="tl-item"><div class="tl-time">unrevert</div><div class="tl-text">snap.restore back to the snapshot saved before revert—take-back succeeds</div></div>
</div>
<p>Binding conversation and files <strong>on the same timeline to roll back together</strong> is revert's key insight: rewind the conversation but not the files and you face the disorder of "the conversation thinks nothing changed, yet the files are already changed"; rewind files but not conversation, likewise. Only when <strong>both, as a whole, return to the past together</strong> is that moment's world self-consistent. Behind this is L49's session-table <span class="mono">revert</span> column quietly supporting it—the state is persisted, so even after a restart this "regret pill" still works.</p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>This lesson clarifies "memory management" atop "persistence"—the two dimensions of capacity and timeline:</p>
  <ul>
    <li><strong>compaction and summary</strong> (<span class="mono">session/compaction.ts</span>): <span class="mono">compactIfNeeded</span> triggers when request tokens &gt; <span class="mono">context−max(output,buffer 20k)</span>; <span class="mono">select</span> split = keep the near verbatim (<span class="mono">DEFAULT_KEEP_TOKENS</span>≈8k) + fold the far into a structured summary (fixed template Goal/Constraints/Progress/Decisions/Next Steps/Context/Files); LLM generates with no tools capped at 4096 tokens; <strong>anchored incremental update</strong> (preserve/remove/merge on the old summary, main thread unbroken). Echoes L42's "context scarce."</li>
    <li><strong>snapshot = shadow git repo</strong> (<span class="mono">snapshot/index.ts</span>): a separate <span class="mono">--git-dir</span> (under data dir) + <span class="mono">--work-tree</span> at the real working directory, <strong>never touching your .git</strong>; <span class="mono">track</span>=<span class="mono">write-tree</span> for a tree hash, <span class="mono">restore</span>=<span class="mono">read-tree</span>+<span class="mono">checkout-index</span>; <span class="mono">alternates</span> share objects to save space, respects .gitignore, blocks large files. Reuse git (like L39 reusing Ripgrep).</li>
    <li><strong>revert = conversation+files roll back together</strong> (<span class="mono">session/revert.ts</span>): rewind conversation (trim after message N) + rewind files (<span class="mono">snap.revert</span> rolls the changed files back per-patch); <strong>reversible</strong> (track current before revert → unrevert restores wholesale via <span class="mono">snap.restore</span>), state stored in L49 session-table's <span class="mono">revert</span> JSON column, works after restart.</li>
    <li><strong>unifying theme</strong>: L48–50 faithfully <strong>store</strong>, L51 wisely <strong>manage</strong>—compaction manages memory capacity, snapshot/revert manages memory's timeline. Conversation and files bound on the same timeline to roll back together, only then is that moment's world self-consistent.</li>
  </ul>
  <p>With this <strong>M9 Persistence and Storage</strong> is fully covered: from the Drizzle/SQLite foundation (L48), the core table web (L49), V1→V2 migration (L50), to this lesson's compaction and snapshot/revert (L51)—how opencode faithfully stores, safely moves, and wisely manages all its "memory." The next part <strong>M10 turns to TUI and client rendering</strong>: how these stored sessions, messages, contexts ultimately get rendered into a fluid interactive interface in your terminal.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p>The <span class="mono">select</span> function walks backward from the conversation's end, splitting "near/far" by token, even slicing the boundary message down the middle (simplified from <span class="mono">compaction.ts</span>):</p>
  <pre class="code"><span class="cm">// accumulate tokens backward from the last, until exceeding the keep budget</span>
<span class="kw">for</span> (<span class="kw">let</span> index = conversation.length - <span class="nu">1</span>; index &gt;= <span class="nu">0</span>; index--) {
  <span class="kw">const</span> next = total + Token.<span class="fn">estimate</span>(conversation[index])
  <span class="kw">if</span> (next &gt; tokens) {                       <span class="cm">// this one would exceed</span>
    <span class="kw">const</span> remaining = Math.<span class="fn">max</span>(<span class="nu">0</span>, tokens - total) * <span class="nu">4</span>   <span class="cm">// chars still fittable (≈token×4)</span>
    <span class="kw">if</span> (remaining &gt; <span class="nu">0</span>) {
      splitPrefix = conversation[index].<span class="fn">slice</span>(<span class="nu">0</span>, -remaining)   <span class="cm">// front half → into far (summary)</span>
      splitSuffix = conversation[index].<span class="fn">slice</span>(-remaining)    <span class="cm">// back half → into near (verbatim)</span>
      split = index + <span class="nu">1</span>
    }
    <span class="kw">break</span>
  }
  total = next
  split = index
}
<span class="cm">// head=far (to summarize), recent=near (kept verbatim)</span>
<span class="kw">return</span> {
  head: [...conversation.<span class="fn">slice</span>(<span class="nu">0</span>, split), splitPrefix].<span class="fn">filter</span>(Boolean).<span class="fn">join</span>(<span class="st">"\n\n"</span>),
  recent: [splitSuffix, ...conversation.<span class="fn">slice</span>(split)].<span class="fn">filter</span>(Boolean).<span class="fn">join</span>(<span class="st">"\n\n"</span>),
}</pre>
  <p>The finest part is it <strong>can slice even a single message down the middle</strong>: when accumulation reaches a message that would exceed the keep budget but a little space remains, it <strong>cuts that message in two by the remaining char count</strong>—the front <span class="mono">splitPrefix</span> joins the to-summarize <span class="mono">head</span>, the back <span class="mono">splitSuffix</span> stays in the verbatim-kept <span class="mono">recent</span> (here <span class="mono">×4</span> is the rough "1 token ≈ 4 chars" conversion). Why so fine? Because messages vary in length; if it could only cut <strong>whole message by whole message</strong>, a particularly long message stuck on the boundary would force either all-summary or all-keep, wastefully squandering or crowding the precious budget. <strong>Allowing a cut mid-message is the key to using the "keep recent N tokens" budget to the hilt</strong>—it lets the split point land precisely on the token budget rather than being dragged by message boundaries. This "to fill a scarce resource, willing to subdivide even the smallest unit" meticulousness is exactly opencode's consistent restraint and careful calculation in context management.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>compaction = keep near verbatim + fold far into summary</strong> (<span class="mono">compaction.ts</span>): triggers when request tokens exceed <span class="mono">context−max(output,buffer 20k)</span>; <span class="mono">select</span> keeps the most recent ≈8k tokens verbatim, hands the rest to the LLM to fill a fixed-structure summary template (Goal/Constraints/Progress/Decisions/Next Steps/Context/Files); can cut mid-message to use the keep budget to the hilt.</li>
    <li><strong>anchored incremental summary</strong>: if already compacted, "preserve/remove/merge" on the old summary rather than rewrite, keeping the main thread unbroken across multiple compactions, not gradually diluted and forgotten. The same "context scarce" philosophy as L42 echoing at a different level.</li>
    <li><strong>snapshot = shadow git repo</strong> (<span class="mono">snapshot/index.ts</span>): a separate <span class="mono">--git-dir</span>+<span class="mono">--work-tree</span> at the real working directory, <strong>never touching your .git</strong>; <span class="mono">track</span>=<span class="mono">write-tree</span> (lightweight tree snapshot, not a commit), <span class="mono">restore</span>=<span class="mono">read-tree</span>+<span class="mono">checkout-index</span>; alternates share objects, respects gitignore. Reuse git's power (like L39 reusing Ripgrep).</li>
    <li><strong>revert = conversation+files roll back together</strong> (<span class="mono">revert.ts</span>): rewind conversation (trim after message N) + rewind files (<span class="mono">snap.revert</span> per-patch) bound on the same timeline, only then self-consistent; <strong>can unrevert</strong> (track current before revert, unrevert restores wholesale via <span class="mono">snap.restore</span>). State stored in L49 session-table's <span class="mono">revert</span> JSON column, works after restart.</li>
    <li><strong>M9 finale</strong>: L48–50 faithfully store/move, L51 wisely manage (capacity via compaction, timeline via snapshot/revert). The next part M10 covers TUI—how these memories get rendered into an interactive interface in the terminal.</li>
  </ul>
</div>
""",
}
