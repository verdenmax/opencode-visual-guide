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
  <div class="tl-item"><div class="tl-time">20260603</div><div class="tl-text">session_input_inbox（V2 输入箱）</div></div>
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
        tx.<span class="fn">run</span>(sql<span class="st">`INSERT INTO migration (id, time_completed) VALUES (${'$'}{m.id}, ...)`</span>))
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
  <div class="tl-item"><div class="tl-time">20260603</div><div class="tl-text">session_input_inbox (V2 inbox)</div></div>
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
        tx.<span class="fn">run</span>(sql<span class="st">`INSERT INTO migration (id, time_completed) VALUES (${'$'}{m.id}, ...)`</span>))
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
LESSON_49 = wip('核心数据表', 'The core tables')
LESSON_50 = wip('V1 存储与迁移', 'V1 storage & migration')
LESSON_51 = wip('压缩、摘要与快照', 'Compaction & snapshots')
