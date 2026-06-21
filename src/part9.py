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
<p>注意 <span class="mono">parent_id</span> 那个<strong>自指外键</strong>：一个 session 可以是另一个 session 的子会话——这正是 M4 里 agent 派生子任务（subagent）时，子会话挂在父会话名下的落盘方式。而几乎所有其它表，都通过外键指回 session。把这张关系网铺开看：</p>
<table class="t">
  <tr><th>父表</th><th>子表（外键 + cascade）</th><th>关系</th></tr>
  <tr><td>project</td><td>session（project_id）</td><td>一个项目 N 个会话</td></tr>
  <tr><td>session</td><td>session（parent_id 自指）</td><td>父会话 N 个子会话</td></tr>
  <tr><td>session</td><td>message → part</td><td>V1：会话 N 消息 N 片段</td></tr>
  <tr><td>session</td><td>session_message</td><td>V2：会话 N 消息（按 seq）</td></tr>
  <tr><td>session</td><td>session_input</td><td>V2：会话 N 条待处理输入</td></tr>
  <tr><td>session</td><td>session_context_epoch</td><td>1:1（主键即 session_id）</td></tr>
  <tr><td>session</td><td>todo</td><td>会话 N 条待办</td></tr>
</table>
<p>这张表最该品的，是那一片 <span class="mono">onDelete:"cascade"</span> 编织出的<strong>「级联删除网」</strong>。删一个 project，它名下所有 session 跟着删；删一个 session，它名下所有 message/part/session_message/session_input/epoch/todo 全部跟着删。<strong>数据库在结构层面就保证了「没有孤儿数据」</strong>——你永远不会查到一条「属于某个早已不存在的会话」的消息。这种一致性不是靠应用代码小心翼翼地手动删，而是靠外键约束<strong>由数据库强制兜底</strong>（也正因如此，上一课那句 <span class="mono">PRAGMA foreign_keys=ON</span> 才不可省）。把一次「删掉 project」的级联走一遍，就能看清这棵树是怎么连根拔起的：</p>
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
<p>「新旧同堂」绝非设计混乱，而是<strong>大型有状态系统演进时的常态与智慧</strong>：你不可能在某个深夜「啪」地把所有历史会话从 V1 瞬间切到 V2——那风险太大。正确的做法是让两代模型<strong>在同一个库里共存一段时间</strong>，旧数据继续以 V1 形态躺着、新数据以 V2 形态写入，再用一个专门的迁移过程慢慢把 V1 翻译成 V2（这正是下一课 L50 的主题）。这张「同堂」的快照，本身就是 opencode 正处在<strong>从 V1 向 V2 演进途中</strong>的活化石。你也能从中读出一条朴素的工程真理：<strong>真实世界的数据库 schema 从不是一张定稿的蓝图，而是一部还在续写的历史</strong>——能优雅地容纳「上一代」与「这一代」共存，是成熟系统的标志。另外值得一提的是 V1 那两级结构本身：<span class="mono">message</span>→<span class="mono">part</span> 的拆分，对应着「一条助手消息里，可以夹着好几个片段」——一段思考文字是一个 part、一次工具调用是一个 part、工具返回又是一个 part。这种「消息含多片段」的结构其实很合理，V2 的 <span class="mono">session_message</span> 也延续了类似的思路，只是把组织方式重做得更利于按 <span class="mono">seq</span> 流式追加。两代之间的差异，更多在「怎么编号、怎么入箱、上下文怎么落盘」这些<strong>会话编排层面</strong>，而非「一条消息长什么样」这个内容层面。</p>

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
  <div class="cell"><div class="c-tag">identity & belonging</div><div class="c-txt"><span class="mono">id</span>(PK), <span class="mono">project_id</span>(→project,cascade), <span class="mono">workspace_id</span>, <span class="mono">parent_id</span>(self-ref→parent session), <span class="mono">slug</span>, <span class="mono">directory</span>/<span class="mono">path</span></div></div>
  <div class="cell"><div class="c-tag">display</div><div class="c-txt"><span class="mono">title</span>, <span class="mono">version</span>, <span class="mono">share_url</span>, <span class="mono">summary_*</span>(changed lines/files/diff)</div></div>
  <div class="cell"><div class="c-tag">usage stats</div><div class="c-txt"><span class="mono">cost</span>, <span class="mono">tokens_input/output/reasoning/cache_read/cache_write</span></div></div>
  <div class="cell"><div class="c-tag">runtime state</div><div class="c-txt"><span class="mono">agent</span>, <span class="mono">model</span>(JSON), <span class="mono">permission</span>(JSON,L41 Ruleset), <span class="mono">revert</span>(JSON)</div></div>
  <div class="cell"><div class="c-tag">time</div><div class="c-txt"><span class="mono">...Timestamps</span>, <span class="mono">time_compacting</span>, <span class="mono">time_archived</span></div></div>
</div>
<p>Note that <span class="mono">parent_id</span> <strong>self-referencing foreign key</strong>: a session can be a sub-session of another—exactly how, in M4 when an agent spawns a subtask (subagent), the sub-session is parked under the parent on disk. And nearly all other tables point back to session by foreign key. Spreading out this relationship web:</p>
<table class="t">
  <tr><th>parent table</th><th>child table (FK + cascade)</th><th>relation</th></tr>
  <tr><td>project</td><td>session (project_id)</td><td>one project N sessions</td></tr>
  <tr><td>session</td><td>session (parent_id self-ref)</td><td>parent session N sub-sessions</td></tr>
  <tr><td>session</td><td>message → part</td><td>V1: session N messages N parts</td></tr>
  <tr><td>session</td><td>session_message</td><td>V2: session N messages (by seq)</td></tr>
  <tr><td>session</td><td>session_input</td><td>V2: session N pending inputs</td></tr>
  <tr><td>session</td><td>session_context_epoch</td><td>1:1 (PK is session_id)</td></tr>
  <tr><td>session</td><td>todo</td><td>session N todos</td></tr>
</table>
<p>What this table most deserves savoring is the <strong>"cascade-delete web"</strong> woven by all those <span class="mono">onDelete:"cascade"</span>. Delete a project, all its sessions delete; delete a session, all its message/part/session_message/session_input/epoch/todo delete. <strong>At the structural level the database guarantees "no orphan data"</strong>—you'll never query a message "belonging to a session that no longer exists." This consistency isn't from app code carefully deleting by hand but from foreign-key constraints <strong>enforced as a backstop by the database</strong> (and exactly why last lesson's <span class="mono">PRAGMA foreign_keys=ON</span> can't be omitted). Walking through one "delete a project" cascade shows how the tree is uprooted:</p>
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
<p>"Old and new under one roof" is by no means design chaos but <strong>the norm and wisdom of large stateful systems as they evolve</strong>: you can't, one late night, "snap" all historical sessions from V1 to V2 instantly—too risky. The right way is to let the two generations <strong>coexist in the same DB for a while</strong>, old data lying in V1 form, new data written in V2 form, then slowly translate V1 into V2 with a dedicated migration process (exactly next lesson L50's theme). This "under one roof" snapshot is itself a living fossil of opencode mid-evolution <strong>from V1 toward V2</strong>. You can also read from it a plain engineering truth: <strong>a real-world database schema is never a finalized blueprint but a history still being written</strong>—gracefully accommodating "the last generation" and "this generation" coexisting is the mark of a mature system. Also worth noting is V1's two-level structure itself: the <span class="mono">message</span>→<span class="mono">part</span> split corresponds to "one assistant message can clip several fragments"—a stretch of thinking text is a part, a tool call is a part, the tool return another part. This "message contains multiple parts" structure is quite reasonable, and V2's <span class="mono">session_message</span> continues a similar idea, only reworking the organization to favor streaming-append by <span class="mono">seq</span>. The difference between generations is more at the <strong>conversation-orchestration level</strong> of "how to number, how to inbox, how to persist context" than the content level of "what a message looks like."</p>

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
LESSON_50 = wip('V1 存储与迁移', 'V1 storage & migration')
LESSON_51 = wip('压缩、摘要与快照', 'Compaction & snapshots')
