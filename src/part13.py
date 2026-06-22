"""Part 13 (Advanced Topics · 深入专题) content."""
from placeholder import wip

LESSON_65 = {
    "zh": r"""<p class="lead">第 11 课讲事件总线时，我们看的是<strong>传输</strong>那一层：服务器经 SSE 把事件<strong>推</strong>给客户端。但有个更深的问题一直没碰：这些事件<strong>怎么被持久化、怎么定序、怎么让多台设备最终看到同一份会话？</strong>这就是 <span class="mono">EventV2</span>——opencode 的<strong>持久事件溯源 + 单写入同步</strong>底座（<span class="mono">core/src/event.ts</span>、<span class="mono">event/sql.ts</span>、<span class="mono">opencode/src/sync/README.md</span>）。它也正是第 19 课「投影历史」脚下那块地基：投影器之所以能从事件投出一份干净的读模型，前提是事件本身<strong>有持久的、全序的编号</strong>。它还回答了一个很实际的产品问题：你在终端里开着一个会话，又想在网页或手机上<strong>看到同一个会话的实时进展</strong>——这份「多端看到同一份会话」的能力，底层靠的就是本课讲的事件日志与同步。这一课，我们就把第 11 课只讲了「传输」、第 19 课只讲了「投影」之间那块缺失的拼图补上。</p>
<p>这一课最值得带走的洞见只有一个，但它优雅得让人会心一笑：<strong>因为 opencode 规定「<em>同一个会话只允许一台设备写</em>」，整个同步系统就被极大地简化了</strong>。源码 <span class="mono">sync/README.md</span> 把话说得很直白——"<strong>只有一台设备能写，我们就不需要任何复杂的分布式时钟或因果排序</strong>"。多设备协作里最难的那部分（两个人同时改、到底谁先谁后、怎么合并）被一个设计决定直接绕开了：既然只有一个写入者，那就<strong>用一个简单的、单调递增的序号 <span class="mono">seq</span>（每生成一个事件就 +1）来给出全序</strong>。其他设备要「同步」，无非是<strong>拿到事件日志、从自己上次的位置往后重放</strong>，放完就和写入者一字不差。读懂这条「<strong>用约束换简单</strong>」的思路，你就懂了为什么 opencode 能用几张朴素的表，做到多端一致——而不必背上一套分布式共识的重担。这是工程里一种反复奏效却常被忽略的智慧：<strong>与其去解一个难题，不如换一个不产生这个难题的设计</strong>。多写入者的一致性是难题，那就只留一个写入者；这一让，整套系统就从「需要博士论文」变成了「一个计数器加一本流水账」。</p>

<div class="card analogy">
  <div class="tag">📒 生活类比</div>
  想象一个班级的<strong>流水账本</strong>。规矩是：<strong>只有班长一个人能往账本上写</strong>，而且每写一笔就在旁边<strong>编一个连续的号</strong>（第 1 笔、第 2 笔、第 3 笔……这就是 <span class="mono">seq</span>）。别的同学想随时知道「账目现在到哪了」，根本不用把班长喊来对账——他只要记住<strong>自己上次抄到了第几号</strong>（这就是<strong>游标 cursor</strong>），下次来就<strong>从那一号之后接着抄</strong>，抄完，他手里的账和班长的<strong>分毫不差</strong>。哪怕他请了一周假，回来也不用从第 1 笔重抄，只需从自己记下的号往后补——这就是 cursor「持久」的好处。妙就妙在「只有班长能写」这条规矩：如果允许全班同时往一个本子上写，你就得操心「两个人同时写第 5 行怎么办、谁的先算、笔迹叠在一起怎么读」——那是<strong>分布式共识</strong>的噩梦。而「单写入者 + 连续编号」把这一切化简成了小学生都会的「抄账本」。opencode 的多端同步，本质就是这本编了号的流水账：班长是你正在用的那台设备，其他同学是你想同步过去看的网页、手机。
</div>

<h2>单写入者：为什么一个 <span class="mono">seq</span> 就够</h2>
<p>分布式系统里「多个节点都能写、还要让大家看到一致的顺序」是出了名的难——要么上向量时钟/因果排序，要么上 Paxos/Raft 这类共识协议，复杂度陡增。难在哪？难在<strong>「同时」</strong>：两台设备在网络两端几乎同一瞬间各写了一笔，没有一个公共的「现在几点」能裁定谁先谁后，于是要么引入逻辑时钟去推断因果、要么让节点们投票达成共识——任何一种都意味着大量的协议、消息往返和边界情况。opencode 的 <span class="mono">sync</span> 设计做了一个<strong>极聪明的取舍</strong>：它不去解这道难题，而是<strong>从源头消灭它</strong>——直接规定<strong>一个会话同一时刻只有一台设备是「写入者」</strong>，其余设备都是只读的「同步者」。这个约束一立，难题就塌缩了：</p>
<div class="cols">
  <div class="col"><h4>多写入者（绕开了）</h4><p>若 N 台设备都能写，就得回答「两笔几乎同时发生的写，谁排前面」——需要分布式时钟、因果排序、甚至共识协议。难、慢、易错。</p></div>
  <div class="col"><h4>单写入者（opencode 选这个）</h4><p>只有一台写，顺序<strong>天然唯一</strong>：写入者生成事件时给它一个<strong>单调 +1 的 <span class="mono">seq</span></strong>。全序不靠协议，靠「就一个人在编号」。</p></div>
</div>
<p>源码原文（<span class="mono">sync/README.md</span>）：<strong>"Because only one device is allowed to write, we don't need any kind of sophisticated distributed system clocks or causal ordering. We implement total ordering with a simple sequence id (a number) and increment it by one every time we generate an event."</strong> 一句话——<strong>单写入把「全序」从一个分布式难题降格成了一个 <span class="mono">counter += 1</span></strong>。这不是偷懒，而是对场景的精准拿捏：opencode 的会话本来就是「一个人在一台机器上主导地干活」，强行支持「多人同时狂写同一会话」既不符合真实用法、又要付出巨大的复杂度代价——把它砍掉，反而成全了简单与可靠。而且这套 EventV2 是<strong>向后兼容</strong>既有 <span class="mono">Bus</span> 的（<span class="mono">SyncEvent.run</span> 发事件、<span class="mono">subscribeAll</span> 类型安全地收），不另起炉灶、不重复已有的 <span class="mono">session.created</span> 这类事件——是「在旧骨架上长出新能力」而非推倒重来，落地时对用户<strong>零可见变化</strong>。事件本身用一组干净的类型来描述：</p>
<div class="cellgroup">
  <div class="cel"><b>Definition</b><br><span class="mono">{version, aggregate, data:Schema}</span>：一类事件的定义（属于哪个聚合、第几版、数据形状）</div>
  <div class="cel"><b>Payload</b><br>一条事件实例，带可选 <span class="mono">seq</span>（同步投影时填上的全序号）、<span class="mono">version</span>、<span class="mono">replay</span> 标记</div>
  <div class="cel"><b>Cursor</b><br>品牌化的 <span class="mono">NonNegativeInt</span>：一个「重放到哪了」的持久续点</div>
  <div class="cel"><b>Projector / Listener / Sync</b><br>都是 <span class="mono">(event)=&gt;Effect&lt;void&gt;</span>：消费一条事件去干各自的活</div>
  <div class="cel"><b>SerializedEvent</b><br><span class="mono">{seq, aggregateID, …}</span>：落库/上网时的序列化形态</div>
  <div class="cel"><b>versionedType(t,v)</b><br>返回 <span class="mono">`${t}.${v}`</span>：把类型名带上版本，便于演进</div>
</div>

<h2>事件表与序号：两张表撑起全序</h2>
<p>这套「单写入 + 单调 seq」落到 SQLite，是 <span class="mono">event/sql.ts</span> 里<strong>两张配合的表</strong>。为什么要两张而不是一张？因为「逐条事件」和「这个聚合现在编到几号了」是两件不同的事：事件本身是<strong>只增不改</strong>的流水，而「当前最大序号」是个<strong>会不断更新</strong>的小计数器。把它们分开，写一条新事件时就能先去计数器那「领号」、再把带号的事件追加进流水表。一张管「每个聚合（如一个会话）现在编到第几号了」，另一张管「逐条事件本身」：</p>
<table class="t">
  <tr><th>表</th><th>字段</th><th>作用</th></tr>
  <tr><td><span class="mono">event_sequence</span></td><td><span class="mono">aggregate_id</span>(主键)、<span class="mono">seq</span>、<span class="mono">owner_id?</span></td><td>记每个聚合<strong>当前的最大序号</strong>——下一条事件 +1 从这取</td></tr>
  <tr><td><span class="mono">event</span></td><td><span class="mono">id</span>(主键)、<span class="mono">aggregate_id</span>(→引用 sequence，级联删)、<span class="mono">seq</span>、<span class="mono">type</span>、<span class="mono">data</span>(JSON)</td><td>逐条不可变事件；<span class="mono">data</span> 直接以 JSON 存</td></tr>
</table>
<p>关键的正确性保险在两个索引上：<span class="mono">uniqueIndex("event_aggregate_seq_idx").on(aggregate_id, seq)</span>——<strong>同一个聚合内 <span class="mono">(aggregate_id, seq)</span> 唯一</strong>，数据库层面就钉死了「同一会话里不可能有两条 seq 相同的事件」，全序由此<strong>不可破坏</strong>。这道保险很重要：单写入者在内存里 +1 编号是约定，而这个唯一索引是<strong>兜底的物理保证</strong>——万一某个 bug 或并发让两条事件抢到了同一个号，写库时数据库会直接拒绝，让错误<strong>当场暴露</strong>而不是悄悄毁掉全序（又一次「让用错的姿势立刻、响亮地失败」，同 L37/L48）。另一个 <span class="mono">index(aggregate_id, type, seq)</span> 则让「按类型、按序」的查询走得快。注意 <span class="mono">event.aggregate_id</span> <span class="mono">references</span> <span class="mono">event_sequence.aggregate_id</span> 且 <span class="mono">onDelete: cascade</span>——删一个聚合，它名下的事件随之清掉。整条写路径于是非常朴素：</p>
<div class="flow">
  <div class="node">生成一个事件<br><span class="mono">Payload</span></div>
  <div class="arrow">→</div>
  <div class="node">查/进 <span class="mono">event_sequence</span><br>取该聚合下一个 seq</div>
  <div class="arrow">→</div>
  <div class="node">写入 <span class="mono">event</span> 表<br>带上 (aggregate_id, seq)</div>
  <div class="arrow">→</div>
  <div class="node"><span class="mono">uniqueIndex</span> 守门<br>全序不可破坏</div>
</div>

<h2>游标重放与同步：其他设备怎么追平</h2>
<p>有了「一条不可变、带全序号的事件日志」，<strong>同步</strong>就成了最朴素的一件事：一台同步设备记住自己<strong>重放到哪了</strong>（一个 <span class="mono">Cursor</span>），下次来就<strong>把 cursor 之后的事件捞出来、依序重放</strong>，放完它的本地状态就和写入者一致。这正是 <span class="mono">Cursor</span> 注释说的「durable aggregate continuation position for embedded replay streams」——一个可持久化的「接着放」的位置。注意它是<strong>持久（durable）</strong>的：设备断线、关机、过几天再回来，都不必从头重放整条历史，只要从上次记下的 cursor 接着往后追就行——这对一条可能很长的会话事件流至关重要。整个同步像这样走：</p>
<div class="trace">
  <div class="step"><span class="n">1</span> 设备 B（只读同步者）报出自己的 <span class="mono">Cursor</span>：「我重放到第 N 号了」</div>
  <div class="step"><span class="n">2</span> 拉取 <span class="mono">event</span> 表里该聚合 <span class="mono">seq &gt; N</span> 的事件，按 seq 升序成一条流</div>
  <div class="step"><span class="n">3</span> 逐条喂给本地 <span class="mono">Projector</span> 重放（同 L19 投影器把事件「应用」成读模型）</div>
  <div class="step"><span class="n">4</span> 重放到最新，<span class="mono">Cursor</span> 推进到最大 seq——B 与写入者<strong>状态一致</strong></div>
</div>
<p>把这块拼图嵌回全书，三课就连成一条完整链路了：<strong>EventV2（本课）负责事件的「持久化 + 定序 + 同步」，第 11 课的 SSE 负责事件的「实时传输」，第 19 课的投影器负责把事件「投影成可读的消息」。</strong>同一条事件流，三种角色各取所需——这也解释了为什么这三课讲的是「同一件事的不同切面」：事件是贯穿 opencode 的中枢神经，而本课讲的，是这条神经如何被<strong>可靠地记录下来、并在多端之间保持一致</strong>。还有一点容易混淆、值得一辨：第 8 课的 <span class="mono">KeyedMutex</span> 也讲「按 key 排队」，但那是<strong>进程内</strong>同一文件/插件的并发串行；本课的「单写入者 + seq 全序」是<strong>跨设备</strong>的一致性定序——两者都体现「先把顺序定下来，后面就好办」的智慧，但作用在完全不同的层面：一个守的是单机内存里的竞态，一个守的是多台机器之间的一致。</p>
<div class="vflow">
  <div class="vnode"><b>L15 事件溯源</b>：输入 <span class="mono">admit</span> 也是往事件流追加不可变记录——本课给这条流配上了持久的全序号</div>
  <div class="vnode"><b>L11 SSE 传输</b>：把新事件实时推给已连接的客户端（传输层）；本课管的是这些事件如何被<strong>持久存下、定序</strong></div>
  <div class="vnode"><b>L19 投影历史</b>：投影器消费带 seq 的事件，投出读模型——本课的「重放到 cursor」正是投影的驱动力</div>
</div>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <span class="mono">EventV2</span> 是 opencode <strong>多端一致</strong>的底座。一句话串起来：<strong>同一会话只许一台设备写</strong>（单写入者）→ 写入者每生成一个事件就给它一个<strong>单调 +1 的 <span class="mono">seq</span></strong>（全序，无需分布式时钟）→ 事件连同序号落进 <span class="mono">event</span>/<span class="mono">event_sequence</span> 两张表，<span class="mono">uniqueIndex(aggregate_id, seq)</span> 钉死全序 → 其他设备带着 <span class="mono">Cursor</span>，把「我之后」的事件拉来<strong>重放</strong>，即可追平。  它向后兼容既有 <span class="mono">Bus</span>，与 L11(SSE 传输)、L19(投影读模型)、L15(事件溯源) 共用同一条事件流。<strong>用一个约束（单写入）换来整套同步的极致简单</strong>——这是全书「找准接缝、切开会变与不变」之外，又一种「用约束买简单」的工程智慧。下次你设计一个看起来需要分布式协调的系统时，不妨先问一句：这个「同时」真的必须支持吗？砍掉它，往往海阔天空。
</div>

<div class="card detail">
  <div class="tag">🔬 实现细节</div>
  <span class="mono">core/src/event.ts</span>：<span class="mono">export * as EventV2</span>；<span class="mono">ID</span> 是 <span class="mono">evt_</span> 前缀串；<span class="mono">Cursor = NonNegativeInt.pipe(Schema.brand("EventV2.Cursor"))</span>；<span class="mono">Payload.seq</span> 注释「Durable aggregate order, populated while synchronized events are projected」、<span class="mono">replay</span> 注释「Internal replay marker for projectors that own non-replicated operational state」；<span class="mono">Projector/CommitGuard/Listener/Sync</span> 均为 <span class="mono">(Payload)=&gt;Effect&lt;void&gt;</span>；<span class="mono">InvalidSyncEventError</span>(TaggedErrorClass)。<span class="mono">event/sql.ts</span>：<span class="mono">EventSequenceTable("event_sequence")</span> = {aggregate_id PK, seq, owner_id?}；<span class="mono">EventTable("event")</span> = {id PK, aggregate_id→ref onDelete cascade, seq, type, data json} + <span class="mono">uniqueIndex(aggregate_id, seq)</span> + <span class="mono">index(aggregate_id, type, seq)</span>。<span class="mono">sync/README.md</span>：单写入者、总序、与 <span class="mono">Bus</span> 向后兼容、<span class="mono">SyncEvent.run/subscribeAll</span> 类型安全。
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>单写入者 = 全序变简单</strong>：同一会话只许一台设备写，于是「谁先谁后」不需要分布式时钟/共识——<strong>一个单调 +1 的 <span class="mono">seq</span></strong> 就给出全序（<span class="mono">sync/README.md</span> 原话：only one writer ⇒ no distributed clocks）。补 L11（只讲 SSE 传输）与 L19（只讲投影）之间的拼图。</li>
    <li><strong>两张表撑全序</strong>：<span class="mono">event_sequence</span>(每聚合当前最大 seq) + <span class="mono">event</span>(逐条不可变事件, data 存 JSON)；<span class="mono">uniqueIndex(aggregate_id, seq)</span> 数据库层钉死「同会话无重复 seq」，全序不可破坏；aggregate 外键 onDelete cascade。核心类型 Cursor/Definition/Payload/Projector/versionedType。</li>
    <li><strong>游标重放即同步</strong>：同步设备带 <span class="mono">Cursor</span>（重放续点）→ 拉 <span class="mono">seq &gt; cursor</span> 的事件依序重放（喂给 L19 投影器）→ 追平写入者。向后兼容 <span class="mono">Bus</span>；与 L11(传输)/L19(投影)/L15(事件溯源) 同流不同角色。区别 L08 KeyedMutex（进程内按 key 串行）：本课是<strong>跨设备</strong>定序。</li>
  </ul>
</div>
""",
    "en": r"""<p class="lead">When Lesson 11 covered the event bus, we looked at the <strong>transport</strong> layer: the server <strong>pushes</strong> events to clients over SSE. But a deeper question went untouched: how do these events get <strong>persisted, ordered, and made consistent across multiple devices</strong>? That's <span class="mono">EventV2</span>—opencode's <strong>persistent event-sourcing + single-writer sync</strong> foundation (<span class="mono">core/src/event.ts</span>, <span class="mono">event/sql.ts</span>, <span class="mono">opencode/src/sync/README.md</span>). It's also the ground beneath Lesson 19's "projected history": the projector can project a clean read model from events only because the events themselves <strong>carry durable, totally-ordered numbering</strong>. It also answers a very practical product question: you have a session open in the terminal and want to <strong>see its live progress on the web or your phone</strong>—that "many devices, one session" ability rests, underneath, on the event log and sync this lesson covers. This lesson fills the missing piece between Lesson 11's "transport" and Lesson 19's "projection."</p>
<p>There's only one insight worth taking away, but it's elegant enough to make you smile: <strong>because opencode mandates "<em>only one device may write a given session</em>," the entire sync system is radically simplified</strong>. The source <span class="mono">sync/README.md</span> says it plainly—"<strong>Because only one device is allowed to write, we don't need any kind of sophisticated distributed system clocks or causal ordering.</strong>" The hardest part of multi-device collaboration (two people editing at once, who came first, how to merge) is sidestepped by one design decision: since there's only one writer, just <strong>use a simple, monotonically-increasing <span class="mono">seq</span> (incremented by one per event) to give a total order</strong>. For other devices to "sync" is nothing more than <strong>fetching the event log and replaying it forward from where they last were</strong>—replay it and they match the writer exactly. Grasp this "<strong>trade a constraint for simplicity</strong>" idea and you'll see why opencode achieves multi-end consistency with a few plain tables—without shouldering a distributed-consensus burden. This is a repeatedly-effective yet often-overlooked engineering wisdom: <strong>rather than solving a hard problem, switch to a design that doesn't produce it</strong>. Multi-writer consistency is a hard problem, so keep only one writer; that one concession turns the whole system from "needs a PhD thesis" into "a counter plus a ledger."</p>

<div class="card analogy">
  <div class="tag">📒 Analogy</div>
  Picture a classroom <strong>running ledger</strong>. The rule: <strong>only the monitor may write in it</strong>, and each entry gets a <strong>consecutive number</strong> beside it (entry 1, 2, 3… that's <span class="mono">seq</span>). When other students want to know "where do the accounts stand now," they needn't summon the monitor to reconcile—each just remembers <strong>which number they last copied to</strong> (that's the <strong>cursor</strong>), and next time <strong>copies onward from after that number</strong>; once done, their copy matches the monitor's <strong>exactly</strong>. Even after a week's absence they needn't recopy from entry 1, just continue from their saved number—that's the benefit of the cursor being "durable." The beauty is the "only the monitor writes" rule: if the whole class could write the same book at once, you'd fret over "two people writing line 5 at the same time, whose counts first, overlapping handwriting"—the <strong>distributed-consensus</strong> nightmare. "Single writer + consecutive numbering" reduces all that to grade-school "copy the ledger." opencode's multi-end sync is essentially this numbered running ledger: the monitor is the device you're using, the other students are the web and phone you want to sync to.
</div>

<h2>Single writer: why one <span class="mono">seq</span> is enough</h2>
<p>"Multiple nodes can all write, yet everyone must see a consistent order" is famously hard in distributed systems—either vector clocks/causal ordering, or consensus protocols like Paxos/Raft, sharply raising complexity. Where's the difficulty? In <strong>"simultaneity"</strong>: two devices on opposite ends of a network each write almost the same instant, with no shared "what time is it now" to adjudicate who's first, so you must introduce logical clocks to infer causality or have nodes vote for consensus—either way, lots of protocol, message round-trips, and edge cases. opencode's <span class="mono">sync</span> design makes a <strong>very clever trade-off</strong>: it doesn't solve this hard problem, it <strong>eliminates it at the source</strong>—it simply mandates that <strong>a session has only one "writer" device at a time</strong>, all others being read-only "synchronizers." With that constraint, the problem collapses:</p>
<div class="cols">
  <div class="col"><h4>Multi-writer (sidestepped)</h4><p>If N devices could write, you'd answer "two near-simultaneous writes, which goes first"—needing distributed clocks, causal ordering, even consensus protocols. Hard, slow, error-prone.</p></div>
  <div class="col"><h4>Single writer (opencode's choice)</h4><p>With only one writing, the order is <strong>naturally unique</strong>: the writer gives each event it generates a <strong>monotonically +1 <span class="mono">seq</span></strong>. Total order comes not from a protocol but from "just one person numbering."</p></div>
</div>
<p>The source's words (<span class="mono">sync/README.md</span>): <strong>"Because only one device is allowed to write, we don't need any kind of sophisticated distributed system clocks or causal ordering. We implement total ordering with a simple sequence id (a number) and increment it by one every time we generate an event."</strong> In a word—<strong>single-writer demotes "total order" from a distributed hard problem to a <span class="mono">counter += 1</span></strong>. This isn't laziness but precise read of the scenario: an opencode session is inherently "one person driving on one machine"; forcibly supporting "many people frantically writing one session at once" neither fits real usage nor justifies the huge complexity cost—cutting it actually buys simplicity and reliability. Moreover this EventV2 is <strong>backwards-compatible</strong> with the existing <span class="mono">Bus</span> (<span class="mono">SyncEvent.run</span> emits, <span class="mono">subscribeAll</span> receives type-safely), not a fresh start, not duplicating existing <span class="mono">session.created</span>-type events—"new ability grown on the old skeleton" rather than a rewrite, landing with <strong>zero visible change</strong> to users. The events themselves are described by a clean set of types:</p>
<div class="cellgroup">
  <div class="cel"><b>Definition</b><br><span class="mono">{version, aggregate, data:Schema}</span>: a class of event (which aggregate, what version, data shape)</div>
  <div class="cel"><b>Payload</b><br>an event instance, with optional <span class="mono">seq</span> (the total-order number filled in during sync projection), <span class="mono">version</span>, <span class="mono">replay</span> marker</div>
  <div class="cel"><b>Cursor</b><br>a branded <span class="mono">NonNegativeInt</span>: a durable "where replay reached" continuation point</div>
  <div class="cel"><b>Projector / Listener / Sync</b><br>all <span class="mono">(event)=&gt;Effect&lt;void&gt;</span>: consume one event to do their own job</div>
  <div class="cel"><b>SerializedEvent</b><br><span class="mono">{seq, aggregateID, …}</span>: the serialized form for storage/network</div>
  <div class="cel"><b>versionedType(t,v)</b><br>returns <span class="mono">`${t}.${v}`</span>: tags the type name with a version for evolution</div>
</div>

<h2>Event tables &amp; the sequence: two tables hold the total order</h2>
<p>This "single-writer + monotonic seq" lands in SQLite as <strong>two cooperating tables</strong> in <span class="mono">event/sql.ts</span>. Why two and not one? Because "each event" and "what number this aggregate has reached" are two different things: events are an <strong>append-only, never-modified</strong> stream, while "current max sequence" is a <strong>constantly-updated</strong> little counter. Splitting them lets a new write first "draw a number" from the counter, then append the numbered event to the stream. One tracks "what number each aggregate (e.g. one session) has reached," the other tracks "each event itself":</p>
<table class="t">
  <tr><th>Table</th><th>Fields</th><th>Role</th></tr>
  <tr><td><span class="mono">event_sequence</span></td><td><span class="mono">aggregate_id</span>(PK), <span class="mono">seq</span>, <span class="mono">owner_id?</span></td><td>each aggregate's <strong>current max number</strong>—the next event +1 from here</td></tr>
  <tr><td><span class="mono">event</span></td><td><span class="mono">id</span>(PK), <span class="mono">aggregate_id</span>(→refs sequence, cascade delete), <span class="mono">seq</span>, <span class="mono">type</span>, <span class="mono">data</span>(JSON)</td><td>each immutable event; <span class="mono">data</span> stored directly as JSON</td></tr>
</table>
<p>The key correctness insurance is in two indexes: <span class="mono">uniqueIndex("event_aggregate_seq_idx").on(aggregate_id, seq)</span>—<strong><span class="mono">(aggregate_id, seq)</span> is unique within one aggregate</strong>, so the database layer nails down "one session can't have two events with the same seq," making the total order <strong>unbreakable</strong>. This insurance matters: the single writer's in-memory +1 numbering is a convention, while this unique index is the <strong>physical backstop</strong>—should some bug or race let two events grab the same number, the database rejects the write, exposing the error <strong>on the spot</strong> rather than silently corrupting the total order (again "let wrong usage fail immediately and loudly," like L37/L48). The other <span class="mono">index(aggregate_id, type, seq)</span> speeds "by type, by order" queries. Note <span class="mono">event.aggregate_id</span> <span class="mono">references</span> <span class="mono">event_sequence.aggregate_id</span> with <span class="mono">onDelete: cascade</span>—delete an aggregate and its events go with it. So the write path is very plain:</p>
<div class="flow">
  <div class="node">generate an event<br><span class="mono">Payload</span></div>
  <div class="arrow">→</div>
  <div class="node">read/bump <span class="mono">event_sequence</span><br>get this aggregate's next seq</div>
  <div class="arrow">→</div>
  <div class="node">write to <span class="mono">event</span> table<br>with (aggregate_id, seq)</div>
  <div class="arrow">→</div>
  <div class="node"><span class="mono">uniqueIndex</span> guards<br>total order unbreakable</div>
</div>

<h2>Cursor replay &amp; sync: how other devices catch up</h2>
<p>With "an immutable, totally-numbered event log," <strong>sync</strong> becomes the plainest thing: a syncing device remembers <strong>where it replayed to</strong> (a <span class="mono">Cursor</span>), and next time <strong>pulls the events after the cursor and replays them in order</strong>; once done, its local state matches the writer's. This is exactly what the <span class="mono">Cursor</span> comment says—"durable aggregate continuation position for embedded replay streams"—a persistable "resume here" position. Note it's <strong>durable</strong>: a device that disconnects, shuts down, or returns days later needn't replay the whole history from scratch—just continue from the last recorded cursor—crucial for a possibly-long session event stream. The sync goes like this:</p>
<div class="trace">
  <div class="step"><span class="n">1</span> Device B (read-only synchronizer) reports its <span class="mono">Cursor</span>: "I've replayed to number N"</div>
  <div class="step"><span class="n">2</span> Pull this aggregate's events with <span class="mono">seq &gt; N</span> from the <span class="mono">event</span> table, ascending by seq into a stream</div>
  <div class="step"><span class="n">3</span> Feed them one by one to the local <span class="mono">Projector</span> to replay (same as L19's projector "applying" events into a read model)</div>
  <div class="step"><span class="n">4</span> Replayed to the latest, the <span class="mono">Cursor</span> advances to the max seq—B is now <strong>consistent</strong> with the writer</div>
</div>
<p>Fit this piece back into the book and three lessons connect into one full chain: <strong>EventV2 (this lesson) handles events' "persistence + ordering + sync," Lesson 11's SSE handles their "live transport," and Lesson 19's projector handles "projecting events into readable messages."</strong> One event stream, three roles each taking what they need—which is why these three lessons cover "different facets of one thing": events are opencode's central nervous system, and this lesson covers how that nerve gets <strong>reliably recorded and kept consistent across devices</strong>. One more easily-confused point worth distinguishing: Lesson 8's <span class="mono">KeyedMutex</span> also covers "queue by key," but that's <strong>in-process</strong> serialization of concurrent same-file/plugin work; this lesson's "single-writer + seq total order" is <strong>cross-device</strong> consistency ordering—both embody "pin down the order first and the rest is easy," but at completely different layers: one guards races in one machine's memory, the other guards consistency across many machines.</p>
<div class="vflow">
  <div class="vnode"><b>L15 event sourcing</b>: input <span class="mono">admit</span> also appends immutable records to the event stream—this lesson gives that stream durable total-order numbers</div>
  <div class="vnode"><b>L11 SSE transport</b>: pushes new events live to connected clients (transport layer); this lesson is about how those events get <strong>durably stored, ordered</strong></div>
  <div class="vnode"><b>L19 projected history</b>: the projector consumes seq-bearing events to project a read model—this lesson's "replay to cursor" is exactly projection's driver</div>
</div>

<div class="card macro">
  <div class="tag">🗺️ Big picture</div>
  <span class="mono">EventV2</span> is opencode's foundation for <strong>multi-end consistency</strong>. In one line: <strong>only one device may write a session</strong> (single writer) → the writer gives each generated event a <strong>monotonically +1 <span class="mono">seq</span></strong> (total order, no distributed clock) → events with their numbers land in the <span class="mono">event</span>/<span class="mono">event_sequence</span> tables, <span class="mono">uniqueIndex(aggregate_id, seq)</span> pinning the order → other devices, carrying a <span class="mono">Cursor</span>, pull "after me" events to <strong>replay</strong> and catch up. It's backwards-compatible with the existing <span class="mono">Bus</span>, sharing one event stream with L11(SSE transport), L19(projected read model), L15(event sourcing). <strong>Trading one constraint (single writer) for the whole sync system's extreme simplicity</strong>—beyond the book's "find the seam, cut what changes from what doesn't," this is another "buy simplicity with a constraint" engineering wisdom. Next time you design a system that looks like it needs distributed coordination, first ask: does that "simultaneity" really have to be supported? Cut it, and the sky often opens up.
</div>

<div class="card detail">
  <div class="tag">🔬 Implementation details</div>
  <span class="mono">core/src/event.ts</span>: <span class="mono">export * as EventV2</span>; <span class="mono">ID</span> is an <span class="mono">evt_</span>-prefixed string; <span class="mono">Cursor = NonNegativeInt.pipe(Schema.brand("EventV2.Cursor"))</span>; <span class="mono">Payload.seq</span> comment "Durable aggregate order, populated while synchronized events are projected," <span class="mono">replay</span> comment "Internal replay marker for projectors that own non-replicated operational state"; <span class="mono">Projector/CommitGuard/Listener/Sync</span> are all <span class="mono">(Payload)=&gt;Effect&lt;void&gt;</span>; <span class="mono">InvalidSyncEventError</span>(TaggedErrorClass). <span class="mono">event/sql.ts</span>: <span class="mono">EventSequenceTable("event_sequence")</span> = {aggregate_id PK, seq, owner_id?}; <span class="mono">EventTable("event")</span> = {id PK, aggregate_id→ref onDelete cascade, seq, type, data json} + <span class="mono">uniqueIndex(aggregate_id, seq)</span> + <span class="mono">index(aggregate_id, type, seq)</span>. <span class="mono">sync/README.md</span>: single writer, total ordering, backwards-compatible with <span class="mono">Bus</span>, <span class="mono">SyncEvent.run/subscribeAll</span> type-safe.
</div>

<div class="card key">
  <div class="tag">🎯 Key points</div>
  <ul>
    <li><strong>Single writer = total order made simple</strong>: only one device may write a session, so "who's first" needs no distributed clock/consensus—<strong>a monotonically +1 <span class="mono">seq</span></strong> gives the total order (<span class="mono">sync/README.md</span> verbatim: only one writer ⇒ no distributed clocks). Fills the piece between L11 (transport only) and L19 (projection only).</li>
    <li><strong>Two tables hold the total order</strong>: <span class="mono">event_sequence</span>(each aggregate's current max seq) + <span class="mono">event</span>(each immutable event, data as JSON); <span class="mono">uniqueIndex(aggregate_id, seq)</span> pins "no duplicate seq in a session" at the DB layer, making the order unbreakable; aggregate FK onDelete cascade. Core types Cursor/Definition/Payload/Projector/versionedType.</li>
    <li><strong>Cursor replay is sync</strong>: a syncing device carries a <span class="mono">Cursor</span> (replay continuation) → pulls events with <span class="mono">seq &gt; cursor</span> and replays in order (fed to L19's projector) → catches up to the writer. Backwards-compatible with <span class="mono">Bus</span>; same stream, different roles vs L11(transport)/L19(projection)/L15(sourcing). Distinct from L08 KeyedMutex (in-process serial by key): this lesson is <strong>cross-device</strong> ordering.</li>
  </ul>
</div>
""",
}
LESSON_66 = {
    "zh": r"""<p class="lead">你在 opencode 里敲 <span class="mono">/init</span> 或 <span class="mono">/review</span>，按下回车，一段精心写好的长提示词就被发给了模型。这些「斜杠命令」是怎么实现的？翻开 <span class="mono">opencode/src/command/index.ts</span>，你会发现一个出奇简洁、又出奇通用的设计：<strong>一个命令，本质就是一段「参数化的 prompt 模板」</strong>。它有名字、有描述、有一段留了「空」的模板文本，调用时把你给的参数填进空里，就成了发给模型的完整提示词。这件事乍看不起眼，细想却很关键：在一个 AI 编程 agent 里，<strong>「你想让模型干什么」几乎全靠提示词表达</strong>，而把高频、复杂的提示词固化成命令，等于给用户配了一套「常用动作的快捷键」。更妙的是——<strong>自定义命令、MCP 暴露的 prompt、以及 skill，这三种来源完全不同的东西，被塑成了同一种 <span class="mono">Info</span> 形状</strong>，藏在同一个 <span class="mono">get/list</span> 接口后面。你用 <span class="mono">/xxx</span> 的时候，根本感觉不到它来自哪儿。</p>
<p>这一课最值得带走的洞见有两个。第一，<strong>命令 = 模板 + 占位符</strong>：模板里用 <span class="mono">$ARGUMENTS</span>、<span class="mono">$1/$2</span>、<span class="mono">${path}</span> 这类「空」标记参数位置，<span class="mono">hints()</span> 扫一遍就知道「这个命令吃哪些参数」，调用时把实参填进去——一段死板的 prompt 就变成了一个<strong>可复用、可传参的小工具</strong>。这看似平常，却把「提示词工程」从「每次现敲」升级成了「沉淀成可调用的资产」：一段好提示词写一次，存成命令，全团队 <span class="mono">/它</span> 一下就用上了。第二，也是最点睛的——<strong>三种来源、一套接口</strong>：内置命令（读配置）、MCP 服务器暴露的 prompt、skill，本是三类毫不相干的东西，却被 <span class="mono">Command.layer</span> 统一收集、塑成同一个 <span class="mono">Info</span>（靠一个 <span class="mono">source: "command" | "mcp" | "skill"</span> 字段记出身）。这是全书反复出现的「<strong>统一模子刻同形</strong>」（同 L36 Tool.make、L43 skills、L47 PluginV2）在用户命令层的又一次登场：把异质的东西塑成同形，上层就能一视同仁地用，而所有「它们到底哪不一样」的复杂，都被收进了那个塑形的地方。</p>

<div class="card analogy">
  <div class="tag">✉️ 生活类比</div>
  把一个斜杠命令想象成一张<strong>「填空式的信件模板」</strong>。<span class="mono">/review</span> 不是一封写死的信，而是一张<strong>印好骨架、留了空格</strong>的信纸：「你是代码审查员……要审查的输入：<u>＿＿＿</u>」。你调用 <span class="mono">/review 这个 PR</span> 时，就是把「这个 PR」填进那个空格（<span class="mono">$ARGUMENTS</span>），一封完整的信（prompt）就成了，寄给模型。<span class="mono">hints()</span> 就像信纸上<strong>标出来的所有空格</strong>，提醒你「这封信要填几个空、填什么」。而最妙的是<strong>「信纸供应商」有三家</strong>：opencode 自带的（内置命令）、外部 MCP 服务器寄来的（MCP prompt）、技能包带来的（skill）——它们的「进货渠道」天差地别（一个在本地抽屉、一个要打电话叫快递、一个是另一套技能体系），但它们都被做成<strong>同一种规格的信纸</strong>，你从抽屉里抽一张用，根本分不清也不用分清它是哪家产的。一套「抽信纸→填空→寄出」的动作，服务所有来源——这正是「统一模子」省心的地方：你只学一种用法，就用上了三种来源的全部命令。
</div>

<h2>命令 = 参数化的 prompt 模板</h2>
<p>命令的数据形状是 <span class="mono">Info</span>（<span class="mono">Schema.Struct</span>）。它把「一个命令是什么」讲得清清楚楚，每个字段都对应命令的一个侧面——名字让你呼叫它、描述让你和命令面板知道它干嘛、模板是它的「正文」、来源记它的出身、参数清单告诉你怎么喂它、可选的 agent/model/subtask 微调它怎么跑：</p>
<div class="cellgroup">
  <div class="cel"><b>name</b><br>命令名，如 <span class="mono">init</span>、<span class="mono">review</span>（你敲的 <span class="mono">/xxx</span>）</div>
  <div class="cel"><b>description</b><br>一句话说明，如「review changes [commit\|branch\|pr]」</div>
  <div class="cel"><b>template</b><br><span class="mono">Promise&lt;string&gt; | string</span>：模板正文（MCP 来的是 lazy promise）</div>
  <div class="cel"><b>source</b><br><span class="mono">"command" | "mcp" | "skill"</span>：这命令的出身</div>
  <div class="cel"><b>hints</b><br><span class="mono">string[]</span>：模板里的参数槽（<span class="mono">$1</span>/<span class="mono">$ARGUMENTS</span>…）</div>
  <div class="cel"><b>agent? / model? / subtask?</b><br>可选：用哪个 agent/模型跑、是否作为子任务</div>
</div>
<p>「参数化」靠的是模板里的<strong>占位符</strong>，以及 <span class="mono">hints()</span> 这个小函数。<span class="mono">hints(template)</span> 做的事极简单却很聪明：用正则 <span class="mono">/\$\d+/g</span> 扫出模板里所有 <span class="mono">$1</span>、<span class="mono">$2</span> 这类<strong>编号占位符</strong>（去重、排序），再看有没有 <span class="mono">$ARGUMENTS</span>（「把整串参数塞这」），合起来就是这个命令的「<strong>参数清单</strong>」。换句话说，命令系统<strong>不需要你额外声明「我有几个参数」</strong>——它直接从模板正文里「读」出来：你在模板哪里写了 <span class="mono">$1</span>、哪里写了 <span class="mono">$ARGUMENTS</span>，参数清单就是什么。这是一种「<strong>让数据自己说清楚自己</strong>」的省心设计。它扫描的过程像这样：</p>
<div class="trace">
  <div class="step"><span class="n">1</span> 拿到模板正文，如 <span class="mono">"Diff $1 against $2. Focus: $ARGUMENTS"</span></div>
  <div class="step"><span class="n">2</span> <span class="mono">match(/\$\d+/g)</span> 扫出 <span class="mono">["$1","$2"]</span>，去重 + 排序</div>
  <div class="step"><span class="n">3</span> <span class="mono">includes("$ARGUMENTS")</span> 为真，追加 <span class="mono">"$ARGUMENTS"</span></div>
  <div class="step"><span class="n">4</span> 得 <span class="mono">hints = ["$1","$2","$ARGUMENTS"]</span>——这命令的参数清单</div>
</div>
<p>调用时，把你敲的实参替换进这些位置，模板就「活」成了一段具体 prompt。看真实的两个内置命令：<span class="mono">init</span>（「guided AGENTS.md setup」，模板 <span class="mono">initialize.txt</span> 里 <span class="mono">$ARGUMENTS</span> 收你给的关注点、<span class="mono">${path}</span> 被换成 worktree 路径）；<span class="mono">review</span>（模板 <span class="mono">review.txt</span> 开头「Input: <span class="mono">$ARGUMENTS</span>」，且 <span class="mono">subtask: true</span> 表示当子任务跑）。这两个模板都是几十上百行精心打磨的提示词——把它们做成命令，意味着这份打磨<strong>只需做一次</strong>，之后人人 <span class="mono">/review</span> 一下就复用了团队沉淀的「怎么审代码」的最佳实践。对比一下「写死的 prompt」和「参数化命令」的差别：</p>
<div class="cols">
  <div class="col"><h4>写死的 prompt</h4><p>每次审查代码都重敲一长段「你是代码审查员……」，换个对象就得整段重写。重复、易错、不可复用，团队里每个人还各写各的。</p></div>
  <div class="col"><h4>参数化命令</h4><p>把那段长 prompt 存成模板、留个 <span class="mono">$ARGUMENTS</span> 空；以后 <span class="mono">/review &lt;任意对象&gt;</span> 一行调用，模板自动填好。一次写好，处处复用，全团队共享同一套。</p></div>
</div>

<h2>三源归一：一套接口，三种出身</h2>
<p>命令系统真正的精彩，在 <span class="mono">Command.layer</span>。它在构建时 <span class="mono">yield*</span> 了三个服务——<span class="mono">Config.Service</span>、<span class="mono">MCP.Service</span>、<span class="mono">Skill.Service</span>——然后把来自这<strong>三个完全不同来源</strong>的命令，统统塑成同一个 <span class="mono">Record&lt;string, Info&gt;</span>。注意这三个来源本身有多不一样：内置命令是<strong>本地配置和 <span class="mono">.txt</span> 文件</strong>里读出来的；MCP prompt 是<strong>外部进程经协议远程暴露</strong>的、取它的正文甚至要发网络请求；skill 又是<strong>另一套</strong>「名字常驻、正文按需」的机制（L43）。它们的获取方式、生命周期、数据来源全不同——可一旦塑成 <span class="mono">Info</span>，在命令系统眼里就<strong>没有区别</strong>了：</p>
<div class="vflow">
  <div class="vnode"><b>内置 / 配置命令</b>（<span class="mono">source:"command"</span>）：如 <span class="mono">init</span>、<span class="mono">review</span>，模板来自 <span class="mono">.txt</span> 文件或用户配置</div>
  <div class="vnode"><b>MCP prompt</b>（<span class="mono">source:"mcp"</span>）：外部 MCP 服务器（L46）暴露的 prompt，被裹成命令——因为是远程解析，<span class="mono">template</span> 是个 <strong>lazy promise</strong>（源码注释明说："lazy promises from MCP prompt resolution"）</div>
  <div class="vnode"><b>skill</b>（<span class="mono">source:"skill"</span>）：技能（L43）也作为一种命令来源接入</div>
</div>
<p>三类异质的东西，最后都长成同一个 <span class="mono">Info</span>，只用一个 <span class="mono">source</span> 字段记着「我从哪来」。上层（命令面板、调用逻辑）于是<strong>一视同仁</strong>：它不关心一个命令是内置的、MCP 的还是 skill 的，只管 <span class="mono">get(name)</span> 拿到一个 <span class="mono">Info</span>、填好模板、跑起来。这正是 <span class="mono">template</span> 的类型要写成 <span class="mono">Promise&lt;string&gt; | string</span> 的原因——它得同时容纳「本地就是字符串」和「MCP 远程要 await」两种形态。为什么这种「三源归一」值得专门拿出来讲？因为它体现了一个深刻的设计权衡：<strong>异质性总要有人消化，问题只是在哪一层消化</strong>。如果不归一，上层每处用命令的地方都要写「如果是内置就这样、如果是 MCP 就那样、如果是 skill 又另一样」的分叉，复杂度会像藤蔓一样爬满整个上层。而 <span class="mono">Command.layer</span> 选择<strong>在「塑形」这一处把差异一次性吃掉</strong>——把三种来源都翻译成同一个 <span class="mono">Info</span>，于是上层每一处都干净。把「来源的差异」收进一个字段、把「共同的形状」抽成一个 <span class="mono">Info</span>，<strong>异质塑同形</strong>，是这套设计能如此干净的根。你会发现这和 L36 的 <span class="mono">Tool.make</span>（各种工具塑成同一个工具形状）、L47 的 <span class="mono">PluginV2</span>（各家 provider 塑成同一个插件形状）是<strong>一模一样的招式</strong>，只是这次塑的是「命令」。</p>

<h2>执行与事件：跑起来，并留下痕迹</h2>
<p><span class="mono">Service</span> 接口极小，只有两个方法：<span class="mono">get(name)</span>（按名取一个命令）和 <span class="mono">list()</span>（列全部命令，供命令面板 L56 摊开）。「接口小」本身就是一种设计美德——把异质来源的复杂全压在 <span class="mono">layer</span> 的构建里，暴露给外界的却只是「按名取、列全部」这两件最朴素的事。一个命令被执行时，模板填好实参成 prompt、按 <span class="mono">agent</span>/<span class="mono">model</span> 覆盖选好模型、若 <span class="mono">subtask:true</span> 就作为子任务跑（不污染主对话，跑完把结果带回）；并发出一个 <span class="mono">command.executed</span> 事件（记下「哪个命令、什么参数被执行了」）——这条事件正好流进 L65 讲的事件体系，可被持久化、被其他设备同步看到。也就是说，「你执行了哪些命令」本身也是会话历史的一部分，可回放、可在网页端同步看到。把整条路径走一遍：</p>
<div class="flow">
  <div class="node">你敲 <span class="mono">/review PR#42</span></div>
  <div class="arrow">→</div>
  <div class="node"><span class="mono">get("review")</span><br>拿到 Info</div>
  <div class="arrow">→</div>
  <div class="node">填占位符<br><span class="mono">$ARGUMENTS</span>→PR#42</div>
  <div class="arrow">→</div>
  <div class="node">成完整 prompt<br>(按 subtask/agent 跑)</div>
  <div class="arrow">→</div>
  <div class="node">发 <span class="mono">command.executed</span><br>事件留痕</div>
</div>
<p>占位符的语义也值得收个表，方便你日后写自己的命令模板：</p>
<table class="t">
  <tr><th>占位符</th><th>含义</th><th>来源</th></tr>
  <tr><td><span class="mono">$ARGUMENTS</span></td><td>把整串参数原样塞进来</td><td><span class="mono">hints</span> 检测 <span class="mono">includes("$ARGUMENTS")</span></td></tr>
  <tr><td><span class="mono">$1 / $2 / …</span></td><td>第 N 个位置参数</td><td><span class="mono">hints</span> 用 <span class="mono">/\$\d+/g</span> 扫出、去重排序</td></tr>
  <tr><td><span class="mono">${path}</span></td><td>当前 worktree 路径（构建模板时替换）</td><td>内置命令 <span class="mono">template</span> getter 里 <span class="mono">.replace</span></td></tr>
</table>
<p>顺带辨析一点常见疑惑：<span class="mono">$1/$ARGUMENTS</span> 是<strong>调用时</strong>才填的「用户参数」（由 <span class="mono">hints</span> 列出、等你敲实参），而 <span class="mono">${path}</span> 是<strong>构建模板时</strong>就由内置命令的 <span class="mono">template</span> getter 用 <span class="mono">.replace("${path}", ctx.worktree)</span> 替换好的「上下文」——一个等用户、一个等环境，时机不同。理解这点，你写自己的命令模板时就不会把「该让用户填的」和「系统自动给的」搞混。</p>
<p>到这你就看清了斜杠命令的全貌：它不是一堆散落的硬编码功能，而是<strong>一个「参数化 prompt 模板」的统一抽象</strong>——模板留空、<span class="mono">hints</span> 列空、调用时填空；并把内置/MCP/skill 三种异质来源塑成同一个 <span class="mono">Info</span>，藏在一个 <span class="mono">get/list</span> 接口后。它是 L43 skills「名字常驻、正文按需」、L46 MCP「动态接入外部工具」、L36「统一模子」这些主题在<strong>用户最常摸到的「斜杠命令」</strong>这一面的交汇。回头看，这一课其实给了你一个观察 opencode（乃至任何好系统）的透镜：<strong>当一个系统要把「很多种不同的东西」用「一种统一的方式」呈现给用户时，去找那个「塑形点」——差异在哪被吃掉、同形在哪被定义</strong>。找到它，你就找到了这个系统把复杂藏在哪、把简单留给谁的答案。斜杠命令的塑形点，就是 <span class="mono">Command.layer</span> 那寥寥几行「收三源、塑一形」。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  斜杠命令 = <strong>参数化的 prompt 模板</strong>。数据形状是 <span class="mono">Info</span>{name, description, template(<span class="mono">Promise&lt;string&gt;|string</span>), source, hints, agent?/model?/subtask?}；<span class="mono">hints(template)</span> 扫 <span class="mono">$\d+</span>/<span class="mono">$ARGUMENTS</span> 得参数清单；调用 = 取 <span class="mono">Info</span> → 填占位符 → 成 prompt → 跑（可作 subtask、可指定 agent/model）→ 发 <span class="mono">command.executed</span> 事件（流进 L65）。最点睛处是 <span class="mono">Command.layer</span> 把<strong>三种来源</strong>（内置/config、MCP prompt、skill）统一收集、塑成同一个 <span class="mono">Info</span>，靠 <span class="mono">source</span> 字段记出身，上层一视同仁——这是「统一模子刻同形」（同 L36/L43/L47）在用户命令层的体现：<strong>把异质塑成同形，复杂度就被收进了那个「塑形」的地方，上层于是干净。</strong>读 opencode 任何「把多种东西统一呈现」的子系统时，都可以问一句：塑形点在哪？答案往往就是那个系统最值得学的一行。
</div>

<div class="card detail">
  <div class="tag">🔬 实现细节</div>
  <span class="mono">opencode/src/command/index.ts</span>：<span class="mono">Info = Schema.Struct({name?, agent?, model?, source?:Schema.Literals(["command","mcp","skill"]), template:Schema.Unknown, subtask?, hints:Schema.Array(String)})</span>；<span class="mono">type Info</span> 把 template 收窄成 <span class="mono">Promise&lt;string&gt;|string</span>（注释："Some command templates are lazy promises from MCP prompt resolution"）。<span class="mono">hints(template)</span>：<span class="mono">template.match(/\$\d+/g)</span> 去重排序 + 检测 <span class="mono">includes("$ARGUMENTS")</span>。<span class="mono">Default={INIT:"init", REVIEW:"review"}</span>，模板 <span class="mono">import PROMPT_INITIALIZE from "./template/initialize.txt"</span> / <span class="mono">PROMPT_REVIEW from "./template/review.txt"</span>，内置命令 <span class="mono">get template()</span> 里 <span class="mono">.replace("${path}", ctx.worktree)</span>，<span class="mono">review</span> 带 <span class="mono">subtask:true</span>。<span class="mono">Service</span>(<span class="mono">Context.Service…("@opencode/Command")</span>) 接口 <span class="mono">get/list</span>；<span class="mono">layer = Layer.effect</span> 中 <span class="mono">yield* Config.Service / MCP.Service / Skill.Service</span> 收集三源。<span class="mono">Event.executed</span> type <span class="mono">"command.executed"</span>。整套设计的妙处在于：<span class="mono">layer</span> 把三种来源的差异（本地读 config、MCP 远程 lazy promise、skill 体系）在<strong>构建期一次性吃掉</strong>，对外只暴露 <span class="mono">get/list</span> 两个极简方法，外加一个 <span class="mono">source</span> 字段留作出身标记——异质塑同形的复杂度，被牢牢锁在了 <span class="mono">layer</span> 里。
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>命令 = 参数化 prompt 模板</strong>：<span class="mono">Info</span>{name, description, template, source, hints, agent?/model?/subtask?}。模板用 <span class="mono">$ARGUMENTS</span>/<span class="mono">$1</span>/<span class="mono">${path}</span> 留空；<span class="mono">hints(template)</span> 用 <span class="mono">/\$\d+/g</span>+<span class="mono">includes("$ARGUMENTS")</span> 扫出参数清单（让数据自己说清自己有几个参数）；调用时填空成 prompt。把死板 prompt 变成可复用、可传参、可全团队共享的小工具。</li>
    <li><strong>三源归一（最点睛）</strong>：<span class="mono">Command.layer</span> <span class="mono">yield*</span> <span class="mono">Config/MCP/Skill</span> 三服务，把<strong>内置命令 / MCP prompt / skill</strong> 三种异质来源统一塑成同一个 <span class="mono">Info</span>，用 <span class="mono">source:"command"\|"mcp"\|"skill"</span> 记出身。MCP 远程解析故 <span class="mono">template</span> 是 <span class="mono">Promise&lt;string&gt;|string</span>。上层 <span class="mono">get/list</span> 一视同仁——「统一模子刻同形」（同 L36/L43/L47）。</li>
    <li><strong>执行与留痕</strong>：取 <span class="mono">Info</span>→填占位符→成 prompt→跑（可 <span class="mono">subtask</span>、可指定 <span class="mono">agent/model</span>）→发 <span class="mono">command.executed</span> 事件（流进 L65 事件体系，可持久化/多端同步）。<span class="mono">list()</span> 供命令面板（L56）摊开。</li>
  </ul>
</div>
""",
    "en": r"""<p class="lead">You type <span class="mono">/init</span> or <span class="mono">/review</span> in opencode, hit enter, and a carefully-written long prompt gets sent to the model. How are these "slash commands" implemented? Open <span class="mono">opencode/src/command/index.ts</span> and you find a surprisingly simple, surprisingly general design: <strong>a command is essentially a "parameterized prompt template."</strong> It has a name, a description, and template text with "blanks"; on invocation you fill your arguments into the blanks and it becomes the full prompt sent to the model. This looks unremarkable but is key on reflection: in an AI coding agent, <strong>"what you want the model to do" is expressed almost entirely through prompts</strong>, and crystallizing high-frequency, complex prompts into commands gives users a set of "shortcuts for common actions." Better still—<strong>custom commands, prompts exposed by MCP, and skills—three things of completely different origins—are shaped into the same <span class="mono">Info</span></strong>, hidden behind one <span class="mono">get/list</span> interface. When you use <span class="mono">/xxx</span>, you can't tell where it came from.</p>
<p>There are two insights worth taking away. First, <strong>command = template + placeholders</strong>: the template marks parameter positions with "blanks" like <span class="mono">$ARGUMENTS</span>, <span class="mono">$1/$2</span>, <span class="mono">${path}</span>, <span class="mono">hints()</span> scans once to know "which parameters this command takes," and on invocation you fill the actuals in—a rigid prompt becomes a <strong>reusable, parameterizable little tool</strong>. This seems ordinary but upgrades "prompt engineering" from "retyped each time" to "crystallized into a callable asset": write a good prompt once, save it as a command, and the whole team <span class="mono">/it</span> to use it. Second, the real gem—<strong>three sources, one interface</strong>: built-in commands (read config), prompts exposed by MCP servers, and skills are three unrelated things, yet <span class="mono">Command.layer</span> gathers and shapes them into the same <span class="mono">Info</span> (a <span class="mono">source: "command" | "mcp" | "skill"</span> field records origin). This is the book's recurring "<strong>one mold stamps the same shape</strong>" (like L36 Tool.make, L43 skills, L47 PluginV2) appearing again at the user-command layer: shape heterogeneous things into one form and the upper layer uses them uniformly, while all the "how are they different" complexity is absorbed into that shaping spot.</p>

<div class="card analogy">
  <div class="tag">✉️ Analogy</div>
  Picture a slash command as a <strong>"fill-in-the-blank letter template."</strong> <span class="mono">/review</span> isn't a fixed letter but stationery with the <strong>skeleton printed and blanks left</strong>: "You are a code reviewer… input to review: <u>＿＿＿</u>." Invoking <span class="mono">/review this PR</span> fills "this PR" into that blank (<span class="mono">$ARGUMENTS</span>), and a complete letter (prompt) is ready to mail to the model. <span class="mono">hints()</span> is like <strong>all the marked blanks</strong> on the stationery, reminding you "how many blanks this letter has, what to fill." The beauty is there are <strong>three "stationery suppliers"</strong>: opencode's own (built-in commands), ones mailed from external MCP servers (MCP prompts), ones from skill packs (skills)—their "supply channels" differ wildly (one in a local drawer, one a phone-order courier, one another skill system), yet all are made into <strong>the same-spec stationery</strong>; you pull a sheet from the drawer and can't (and needn't) tell who made it. One "pull stationery → fill blanks → mail" routine serves all sources—that's the ease of "one mold": learn one usage and you get every command from all three sources.
</div>

<h2>Command = a parameterized prompt template</h2>
<p>A command's data shape is <span class="mono">Info</span> (a <span class="mono">Schema.Struct</span>). It spells out "what a command is" clearly, each field a facet of the command—the name lets you call it, the description tells you and the command palette what it does, the template is its "body," the source records its origin, the hints tell you how to feed it, the optional agent/model/subtask tweak how it runs:</p>
<div class="cellgroup">
  <div class="cel"><b>name</b><br>command name, e.g. <span class="mono">init</span>, <span class="mono">review</span> (the <span class="mono">/xxx</span> you type)</div>
  <div class="cel"><b>description</b><br>one-line blurb, e.g. "review changes [commit\|branch\|pr]"</div>
  <div class="cel"><b>template</b><br><span class="mono">Promise&lt;string&gt; | string</span>: the template body (MCP's is a lazy promise)</div>
  <div class="cel"><b>source</b><br><span class="mono">"command" | "mcp" | "skill"</span>: this command's origin</div>
  <div class="cel"><b>hints</b><br><span class="mono">string[]</span>: the template's parameter slots (<span class="mono">$1</span>/<span class="mono">$ARGUMENTS</span>…)</div>
  <div class="cel"><b>agent? / model? / subtask?</b><br>optional: which agent/model to run, whether as a subtask</div>
</div>
<p>"Parameterization" relies on <strong>placeholders</strong> in the template plus the little <span class="mono">hints()</span> function. <span class="mono">hints(template)</span> does something dead-simple yet clever: regex <span class="mono">/\$\d+/g</span> scans all <span class="mono">$1</span>, <span class="mono">$2</span>-style <strong>numbered placeholders</strong> (deduped, sorted), then checks for <span class="mono">$ARGUMENTS</span> ("stuff the whole argument string here"); together that's the command's "<strong>parameter list</strong>." In other words, the command system <strong>needs no extra declaration of "how many parameters I have"</strong>—it "reads" them straight from the template body: wherever you wrote <span class="mono">$1</span> or <span class="mono">$ARGUMENTS</span> in the template, that's the parameter list. A worry-free design of "<strong>letting the data describe itself</strong>." Its scan goes like this:</p>
<div class="trace">
  <div class="step"><span class="n">1</span> take the template body, e.g. <span class="mono">"Diff $1 against $2. Focus: $ARGUMENTS"</span></div>
  <div class="step"><span class="n">2</span> <span class="mono">match(/\$\d+/g)</span> finds <span class="mono">["$1","$2"]</span>, dedup + sort</div>
  <div class="step"><span class="n">3</span> <span class="mono">includes("$ARGUMENTS")</span> is true, append <span class="mono">"$ARGUMENTS"</span></div>
  <div class="step"><span class="n">4</span> get <span class="mono">hints = ["$1","$2","$ARGUMENTS"]</span>—this command's parameter list</div>
</div>
<p>On invocation, your actuals replace these positions and the template "comes alive" into a concrete prompt. Look at the two real built-in commands: <span class="mono">init</span> ("guided AGENTS.md setup," with <span class="mono">$ARGUMENTS</span> in <span class="mono">initialize.txt</span> taking your focus, <span class="mono">${path}</span> replaced by the worktree path); <span class="mono">review</span> (<span class="mono">review.txt</span> opening "Input: <span class="mono">$ARGUMENTS</span>," and <span class="mono">subtask: true</span> meaning run as a subtask). Both templates are dozens-to-hundreds of lines of polished prompt—making them commands means that polish is <strong>done once</strong>, after which anyone <span class="mono">/review</span>s to reuse the team's accumulated best practice of "how to review code." Compare "hardcoded prompt" vs "parameterized command":</p>
<div class="cols">
  <div class="col"><h4>Hardcoded prompt</h4><p>Retype a long "You are a code reviewer…" every review; switch targets and rewrite the whole thing. Repetitive, error-prone, non-reusable, and everyone on the team writes their own.</p></div>
  <div class="col"><h4>Parameterized command</h4><p>Save that long prompt as a template with a <span class="mono">$ARGUMENTS</span> blank; later <span class="mono">/review &lt;any target&gt;</span> in one line, the template auto-fills. Write once, reuse everywhere, whole team shares one.</p></div>
</div>

<h2>Three sources, one form: one interface, three origins</h2>
<p>The command system's real brilliance is in <span class="mono">Command.layer</span>. At construction it <span class="mono">yield*</span>s three services—<span class="mono">Config.Service</span>, <span class="mono">MCP.Service</span>, <span class="mono">Skill.Service</span>—then shapes commands from these <strong>three completely different sources</strong> all into the same <span class="mono">Record&lt;string, Info&gt;</span>. Note how different these sources are: built-in commands are read from <strong>local config and <span class="mono">.txt</span> files</strong>; MCP prompts are <strong>remotely exposed by an external process over a protocol</strong>, fetching their body may even require a network request; skills are <strong>yet another</strong> "name-resident, body-on-demand" mechanism (L43). Their fetch methods, lifecycles, and data origins all differ—yet once shaped into <span class="mono">Info</span>, in the command system's eyes there's <strong>no difference</strong>:</p>
<div class="vflow">
  <div class="vnode"><b>built-in / config commands</b> (<span class="mono">source:"command"</span>): e.g. <span class="mono">init</span>, <span class="mono">review</span>, templates from <span class="mono">.txt</span> files or user config</div>
  <div class="vnode"><b>MCP prompts</b> (<span class="mono">source:"mcp"</span>): prompts exposed by an external MCP server (L46), wrapped as commands—because it's remote resolution, <span class="mono">template</span> is a <strong>lazy promise</strong> (the source comment says "lazy promises from MCP prompt resolution")</div>
  <div class="vnode"><b>skill</b> (<span class="mono">source:"skill"</span>): skills (L43) also plug in as a command source</div>
</div>
<p>Three heterogeneous things all grow into the same <span class="mono">Info</span>, with only a <span class="mono">source</span> field noting "where I came from." So the upper layer (command palette, invocation logic) treats them <strong>uniformly</strong>: it doesn't care whether a command is built-in, MCP, or skill, just <span class="mono">get(name)</span> for an <span class="mono">Info</span>, fill the template, run it. This is exactly why <span class="mono">template</span>'s type is <span class="mono">Promise&lt;string&gt; | string</span>—it must hold both "locally a string" and "MCP remote needs await." Why is this "three sources, one form" worth singling out? Because it embodies a deep trade-off: <strong>heterogeneity must be digested somewhere, the only question is which layer</strong>. Without unifying, every upper-layer use of a command would branch "if built-in do this, if MCP do that, if skill another way," complexity creeping like vines over the whole upper layer. <span class="mono">Command.layer</span> chooses to <strong>eat the difference once at the "shaping" spot</strong>—translating all three sources into one <span class="mono">Info</span>, so every upper-layer site is clean. Tucking "source differences" into one field and abstracting "the common shape" into one <span class="mono">Info</span>, <strong>shaping the heterogeneous into one form</strong>, is the root of this design's cleanness. You'll find this is the <strong>exact same move</strong> as L36's <span class="mono">Tool.make</span> (various tools into one tool shape) and L47's <span class="mono">PluginV2</span> (each provider into one plugin shape), only this time it's "commands" being shaped.</p>

<h2>Execution &amp; events: run it, and leave a trace</h2>
<p>The <span class="mono">Service</span> interface is tiny, just two methods: <span class="mono">get(name)</span> (fetch a command by name) and <span class="mono">list()</span> (list all commands, for the command palette L56 to lay out). "A small interface" is itself a design virtue—pressing all the heterogeneous-source complexity into <span class="mono">layer</span>'s construction, exposing only the plainest "fetch by name, list all." When a command runs, the template fills actuals into a prompt, the model is chosen per <span class="mono">agent</span>/<span class="mono">model</span> overrides, and if <span class="mono">subtask:true</span> it runs as a subtask (not polluting the main conversation, bringing results back when done); and a <span class="mono">command.executed</span> event fires (recording "which command, what arguments ran")—this event flows right into L65's event system, persistable and seen via sync on other devices. That is, "which commands you ran" is itself part of session history, replayable and visible on the web. Trace the whole path:</p>
<div class="flow">
  <div class="node">you type <span class="mono">/review PR#42</span></div>
  <div class="arrow">→</div>
  <div class="node"><span class="mono">get("review")</span><br>fetch the Info</div>
  <div class="arrow">→</div>
  <div class="node">fill placeholders<br><span class="mono">$ARGUMENTS</span>→PR#42</div>
  <div class="arrow">→</div>
  <div class="node">becomes full prompt<br>(run per subtask/agent)</div>
  <div class="arrow">→</div>
  <div class="node">emit <span class="mono">command.executed</span><br>event leaves a trace</div>
</div>
<p>The placeholder semantics are worth a small table too, handy when you write your own command templates:</p>
<table class="t">
  <tr><th>Placeholder</th><th>Meaning</th><th>Source</th></tr>
  <tr><td><span class="mono">$ARGUMENTS</span></td><td>stuff the whole argument string in verbatim</td><td><span class="mono">hints</span> detects <span class="mono">includes("$ARGUMENTS")</span></td></tr>
  <tr><td><span class="mono">$1 / $2 / …</span></td><td>the Nth positional argument</td><td><span class="mono">hints</span> scans via <span class="mono">/\$\d+/g</span>, dedup+sort</td></tr>
  <tr><td><span class="mono">${path}</span></td><td>current worktree path (replaced at template build)</td><td>built-in command <span class="mono">template</span> getter's <span class="mono">.replace</span></td></tr>
</table>
<p>One common confusion worth clearing: <span class="mono">$1/$ARGUMENTS</span> are <strong>filled at invocation</strong> "user arguments" (listed by <span class="mono">hints</span>, waiting for your actuals), while <span class="mono">${path}</span> is "context" <strong>already replaced at template-build time</strong> by the built-in command's <span class="mono">template</span> getter via <span class="mono">.replace("${path}", ctx.worktree)</span>—one waits on the user, one on the environment, different timing. Grasp this and writing your own command templates won't mix up "what the user should fill" with "what the system auto-supplies."</p>
<p>By now you see the slash command whole: not a pile of scattered hardcoded features, but <strong>one unified abstraction of a "parameterized prompt template"</strong>—template leaves blanks, <span class="mono">hints</span> lists blanks, invocation fills blanks; and the built-in/MCP/skill heterogeneous sources are shaped into one <span class="mono">Info</span>, hidden behind a <span class="mono">get/list</span> interface. It's the meeting point of L43 skills' "name-resident, body-on-demand," L46 MCP's "dynamically plug in external tools," and L36's "one mold" themes, on the side of "<strong>slash commands</strong>" that users touch most. In hindsight this lesson gives you a lens for observing opencode (and any good system): <strong>when a system presents "many different things" to the user in "one unified way," find the "shaping spot"—where the difference is eaten, where the common form is defined</strong>. Find it and you've found where the system hides its complexity and who it leaves the simplicity to. The slash command's shaping spot is those few lines of <span class="mono">Command.layer</span>'s "gather three sources, shape one form."</p>

<div class="card macro">
  <div class="tag">🗺️ Big picture</div>
  Slash command = <strong>a parameterized prompt template</strong>. Its data shape is <span class="mono">Info</span>{name, description, template(<span class="mono">Promise&lt;string&gt;|string</span>), source, hints, agent?/model?/subtask?}; <span class="mono">hints(template)</span> scans <span class="mono">$\d+</span>/<span class="mono">$ARGUMENTS</span> for the parameter list; invoke = fetch <span class="mono">Info</span> → fill placeholders → become prompt → run (can be a subtask, can specify agent/model) → emit <span class="mono">command.executed</span> (flows into L65). The gem is <span class="mono">Command.layer</span> gathering <strong>three sources</strong> (built-in/config, MCP prompt, skill) and shaping them into one <span class="mono">Info</span>, with the <span class="mono">source</span> field noting origin, the upper layer uniform—"one mold stamps the same shape" (like L36/L43/L47) at the user-command layer: <strong>shape the heterogeneous into one form, and complexity is tucked into that "shaping" spot, so the upper layer is clean.</strong> Reading any opencode subsystem that "presents many things uniformly," you can ask: where's the shaping spot? The answer is often that system's most worth-learning line.
</div>

<div class="card detail">
  <div class="tag">🔬 Implementation details</div>
  <span class="mono">opencode/src/command/index.ts</span>: <span class="mono">Info = Schema.Struct({name?, agent?, model?, source?:Schema.Literals(["command","mcp","skill"]), template:Schema.Unknown, subtask?, hints:Schema.Array(String)})</span>; <span class="mono">type Info</span> narrows template to <span class="mono">Promise&lt;string&gt;|string</span> (comment: "Some command templates are lazy promises from MCP prompt resolution"). <span class="mono">hints(template)</span>: <span class="mono">template.match(/\$\d+/g)</span> dedup+sort + check <span class="mono">includes("$ARGUMENTS")</span>. <span class="mono">Default={INIT:"init", REVIEW:"review"}</span>, templates <span class="mono">import PROMPT_INITIALIZE from "./template/initialize.txt"</span> / <span class="mono">PROMPT_REVIEW from "./template/review.txt"</span>, built-in commands' <span class="mono">get template()</span> does <span class="mono">.replace("${path}", ctx.worktree)</span>, <span class="mono">review</span> has <span class="mono">subtask:true</span>. <span class="mono">Service</span>(<span class="mono">Context.Service…("@opencode/Command")</span>) interface <span class="mono">get/list</span>; <span class="mono">layer = Layer.effect</span> with <span class="mono">yield* Config.Service / MCP.Service / Skill.Service</span> gathering three sources. <span class="mono">Event.executed</span> type <span class="mono">"command.executed"</span>. The beauty: <span class="mono">layer</span> eats the three sources' differences (local config read, MCP remote lazy promise, skill system) <strong>once at construction</strong>, exposing only the two minimal <span class="mono">get/list</span> methods plus a <span class="mono">source</span> origin tag—the heterogeneous-into-one-form complexity is locked firmly inside <span class="mono">layer</span>.
</div>

<div class="card key">
  <div class="tag">🎯 Key points</div>
  <ul>
    <li><strong>Command = parameterized prompt template</strong>: <span class="mono">Info</span>{name, description, template, source, hints, agent?/model?/subtask?}. The template leaves blanks with <span class="mono">$ARGUMENTS</span>/<span class="mono">$1</span>/<span class="mono">${path}</span>; <span class="mono">hints(template)</span> scans the parameter list via <span class="mono">/\$\d+/g</span>+<span class="mono">includes("$ARGUMENTS")</span> (letting the data state its own parameter count); invocation fills blanks into a prompt. Turns a rigid prompt into a reusable, parameterizable, team-shareable little tool.</li>
    <li><strong>Three sources, one form (the gem)</strong>: <span class="mono">Command.layer</span> <span class="mono">yield*</span>s <span class="mono">Config/MCP/Skill</span> services, shaping <strong>built-in commands / MCP prompts / skills</strong>—three heterogeneous sources—into one <span class="mono">Info</span>, with <span class="mono">source:"command"\|"mcp"\|"skill"</span> noting origin. MCP is remote-resolved so <span class="mono">template</span> is <span class="mono">Promise&lt;string&gt;|string</span>. The upper layer's <span class="mono">get/list</span> treats them uniformly—"one mold stamps the same shape" (like L36/L43/L47).</li>
    <li><strong>Execution &amp; trace</strong>: fetch <span class="mono">Info</span>→fill placeholders→become prompt→run (can be a <span class="mono">subtask</span>, can specify <span class="mono">agent/model</span>)→emit <span class="mono">command.executed</span> event (flows into L65's event system, persistable/sync-able across devices). <span class="mono">list()</span> feeds the command palette (L56).</li>
  </ul>
</div>
""",
}
LESSON_67 = {
    "zh": r"""<p class="lead">怎么给一个会<strong>调用真实大模型</strong>的 agent 循环写测试？这是个真问题：模型<strong>每次回答都不一样</strong>（非确定）、调一次<strong>要花钱</strong>、还<strong>慢</strong>、网络还可能抽风。直接在测试里打真 API，等于让测试结果听天由命——今天绿、明天红，谁也说不清是代码坏了还是模型那天心情不好。opencode 的答案是 <span class="mono">http-recorder</span>（<span class="mono">packages/http-recorder/</span>）：<strong>把一次真实的 provider 往返「录成磁带（cassette）」，之后测试时不再打真 API，而是「放磁带」——回放那盘录好的响应</strong>。于是一个本质非确定的循环，被钉成了<strong>可重放、可断言、不花钱、飞快</strong>的确定测试。<span class="mono">core/test/session-runner-recorded.test.ts</span> 就是这么干的：用一盘录好的 OpenAI 流式响应磁带，<strong>回放整条 V2 session runner</strong>（L17 的 agent 循环）。这一课讲的，是 opencode 为「测自己最核心、又最难测的那条循环」打造的专门工具——它本身就是一个独立的包 <span class="mono">@opencode-ai/http-recorder</span>，足见这套「录放」机制在工程上的分量。</p>
<p>这一课最值得带走的洞见有两个。第一，<strong>「录放（record/replay）」是驯服非确定性的经典手法</strong>：第一次用<strong>录制模式</strong>真打一次 API、把请求与响应原样存成一盘命名磁带；以后用<strong>回放模式</strong>，让进来的请求去磁带库里<strong>按「请求长什么样」匹配</strong>到对应那盘，直接返回录好的响应——外部世界的随机与昂贵，被一次性「冻」进了磁带。第二，也是工程上很见功力的一点——<strong>录的时候自动脱敏（redact）</strong>：API key、<span class="mono">Authorization</span> 头这类秘密会被替换成 <span class="mono">[REDACTED]</span> 再落盘，于是磁带能安全地提交进仓库、当 fixture 用，不会把你的密钥一起带进 git。读懂这套「<strong>把真实世界录一次，之后无限次重放</strong>」，你就掌握了「如何确定性地测试一个不确定系统」这一最棘手测试难题的标准解法。这个手法远不止 opencode 专用——任何依赖外部服务（第三方 API、支付网关、地图服务……）的代码，都面临「测试时要不要真打外部」的两难，而「录放（在测试圈里常叫 VCR / cassette 模式）」就是业界对这道难题的经典答案。opencode 把它做进自己的 <span class="mono">http-recorder</span> 包，正是因为「调真实大模型」恰恰是这类难题里最尖锐的一种：又贵、又慢、又每次不一样。</p>
<div class="card analogy">
  <div class="tag">🎙️ 生活类比</div>
  想象你要反复<strong>排练一场「打电话问专家」的戏</strong>。专家（大模型）很贵、每次回答还都不一样、还可能占线——你总不能每排练一遍就真打一次长途。聪明的做法是：<strong>认认真真打一次真电话，把整通对话<u>录成磁带</u></strong>（录制模式）；录的时候，把里头的<strong>电话号码、口令这类敏感信息「消音」</strong>（脱敏 redact，盖成「<span class="mono">[REDACTED]</span>」）。之后无论排练多少遍，都<strong>不再打真电话，直接放这盘磁带</strong>（回放模式）：剧务听到「拨了某个号、问了某句话」，就去磁带架上<strong>按「号码 + 问的内容」找到对应那盘</strong>，把录好的回答原样放出来。于是每次排练<strong>分毫不差</strong>、不花一分钱、快如闪电，磁带还因为消了音可以安全地存进剧团档案（提交进仓库当 fixture）。<span class="mono">http-recorder</span> 就是这套「录一次真的、之后放无数次假的」的磁带机。
</div>

<h2>为什么难测：一个非确定的循环</h2>
<p>L17 的 agent 循环本质是「问模型 → 跑工具 → 把结果喂回 → 再问」，而这条循环的<strong>每一次「问模型」都是不确定的</strong>：同样的输入，模型今天可能这么答、明天那么答；调用要<strong>花真金白银</strong>、要走网络（慢且可能失败）。这给测试出了道难题——一个好测试要<strong>确定（每次跑结果一样）、快、免费、可离线</strong>，而「真打模型 API」把这四条全破了：把这道难题摆明，你就懂了为什么 opencode 宁可专门写一个录放包，也不愿让核心循环的测试去碰真实 API。</p>
<div class="cols">
  <div class="col"><h4>测试里真打 API</h4><p>结果随模型漂移（今天绿明天红）、每跑一次花钱、慢、要联网、密钥还得管。测试变得<strong>不可靠</strong>，红了你都不知道是代码的锅还是模型的锅。</p></div>
  <div class="col"><h4>录放（http-recorder）</h4><p>真打<strong>一次</strong>、录成磁带；之后回放——结果<strong>恒定</strong>、零成本、毫秒级、可离线、磁带脱敏后可入库。测试重新变得<strong>可信</strong>。</p></div>
</div>
<p>这正是「录放」这一手法的价值：它把「与外部世界的那一次真实交互」从测试的<strong>每一次运行</strong>里抽出来，只做一次、冻成磁带，让后续每次测试都跑在这盘<strong>确定的录音</strong>上。注意它的边界——录放并不验证「模型答得对不对」（那不是单测该管的），它验证的是「<strong>给定这盘已知的模型响应，我的 runner / 协议解析 / 工具调度逻辑处理得对不对</strong>」。也就是说，它把「模型」这个不确定变量<strong>固定住</strong>，好让你专心测自己那部分代码。打个比方：你要测一台「自动售货机」在收到一张钞票后会不会正确出货，你不会去测「印钞厂印得对不对」——你会拿一张<strong>已知为真的样钞</strong>反复投，看售货机的逻辑。磁带就是那张样钞：一份已知、固定的真实输入。这与 L63「测真实实现、少用 mock」一脉相承：磁带不是凭空捏造的假响应（那就成了 mock，容易测出「假绿」——mock 顺、真实环境却崩），而是<strong>一次真实交互的忠实录音</strong>——测的仍是真实的协议字节、真实的流式分帧，只是把它「定格」了。这是「真实」与「确定」之间一个漂亮的平衡：既不像真打 API 那样不可控，又不像纯 mock 那样脱离真实。</p>

<h2>磁带机制：录一次，放无数次</h2>
<p><span class="mono">HttpRecorder = { http, socket }</span>——它能录放两种通道：普通 HTTP，以及 WebSocket（<span class="mono">socket</span>，对应 L33 的流式传输）。围绕「一盘磁带」有一组干净的类型：</p>
<div class="cellgroup">
  <div class="cel"><b>Cassette（磁带）</b><br>一盘命名录音，存一次（或多次）请求-响应；按 <span class="mono">directory</span> 落盘</div>
  <div class="cel"><b>RecorderOptions</b><br>录制器配置（目录、<span class="mono">mode:"record"</span> vs 回放…）</div>
  <div class="cel"><b>RequestSnapshot</b><br>「归一化后的请求表示」——用于匹配的标准形态</div>
  <div class="cel"><b>RequestMatcher</b><br>「判断一个进来的请求是否匹配某条录音」</div>
  <div class="cel"><b>RedactOptions</b><br>「叠加式的脱敏与保头策略」——录时盖掉哪些秘密</div>
  <div class="cel"><b>CassetteMetadata</b><br>随磁带一起存的 JSON 元数据</div>
</div>
<p>回放的关键在<strong>匹配</strong>：一个磁带库里可能录了好几条请求-响应，进来一个新请求，怎么知道该放哪一盘？靠 <span class="mono">RequestMatcher</span> + <span class="mono">RequestSnapshot</span>。<span class="mono">matching.ts</span> 里的 <span class="mono">canonicalSnapshot(snapshot)</span> 把一个请求<strong>归一化</strong>成一段规范 JSON——取它的 <span class="mono">method</span>、<span class="mono">url</span>、<span class="mono">canonicalizeJson(headers)</span>、以及把 body 当 JSON 解出来再规范化（<span class="mono">decodeJson</span>）。「归一化」是为了让「语义相同但字节顺序不同」的两个请求被认成同一个（比如 JSON 字段顺序不同、空白不同），从而稳定地命中同一盘磁带。为什么需要归一化而不直接逐字节比对？因为 HTTP 请求的「字面形态」会有许多无关紧要的抖动——同一个 JSON body，序列化时字段顺序、缩进都可能变，但<strong>语义是同一个请求</strong>。若逐字节比，回放就会因为这些无关差异而<strong>找不到磁带</strong>、测试莫名其妙地失败；归一化把这些噪声抹平，只保留「语义指纹」，匹配才稳。整条回放路径于是是：</p>
<div class="trace">
  <div class="step"><span class="n">1</span> 测试里 runner 发出一个请求（如打 OpenAI 的 <span class="mono">/chat/completions</span>）</div>
  <div class="step"><span class="n">2</span> <span class="mono">canonicalSnapshot</span> 把它归一化成规范形态（method+url+headers+body）</div>
  <div class="step"><span class="n">3</span> <span class="mono">RequestMatcher</span> 在磁带库里找到匹配的那条录音</div>
  <div class="step"><span class="n">4</span> 把录好的响应（含流式分帧）原样放出，runner 照常处理 → 断言结果</div>
</div>

<h2>脱敏与落地：磁带为何能安全入库</h2>
<p>录制时如果原样把请求存下来，你的 API key、<span class="mono">Authorization</span> 头就会被写进磁带文件——一旦提交进 git，等于把密钥泄露了。<span class="mono">http-recorder</span> 用 <strong>脱敏（redaction）</strong>解决这点：<span class="mono">redaction.ts</span> 定义 <span class="mono">REDACTED = "[REDACTED]"</span>，以及一组默认要盖掉的敏感头/查询参数（<span class="mono">DEFAULT_REDACT_HEADERS</span> 含 <span class="mono">authorization</span>、<span class="mono">x-api-key</span>、<span class="mono">x-goog-api-key</span> 等；<span class="mono">DEFAULT_REDACT_QUERY</span> 同理）——录的时候，这些字段被替换成 <span class="mono">[REDACTED]</span> 再落盘。注意 <span class="mono">RedactOptions</span> 的措辞是「<strong>叠加式（additive）</strong>」：默认清单是个安全底线，你可以在它之上再加要盖的字段，而不必从零写一份——这是把「安全的默认」和「可定制」叠在一起的典型做法（呼应 L60 PTY 环境「可定制在中间、不可妥协在最后」）。于是磁带既保留了「请求长什么样」（够用来匹配），又<strong>不含任何真实秘密</strong>，可以放心提交进仓库、当作测试 fixture 长期复用。整条<strong>录制</strong>路径是这样：</p>
<div class="flow">
  <div class="node">runner 真打一次 API</div>
  <div class="arrow">→</div>
  <div class="node">截下请求-响应</div>
  <div class="arrow">→</div>
  <div class="node"><strong>脱敏</strong><br>key/Authorization→<span class="mono">[REDACTED]</span></div>
  <div class="arrow">→</div>
  <div class="node">写入命名磁带<br>(可安全入库)</div>
</div>
<p>默认脱敏清单大致是：</p>
<table class="t">
  <tr><th>类别</th><th>默认脱敏项（示例）</th><th>替换为</th></tr>
  <tr><td>请求头</td><td><span class="mono">authorization</span>、<span class="mono">x-api-key</span>、<span class="mono">x-goog-api-key</span>…</td><td><span class="mono">[REDACTED]</span></td></tr>
  <tr><td>查询参数</td><td><span class="mono">DEFAULT_REDACT_QUERY</span> 里的敏感键</td><td><span class="mono">[REDACTED]</span></td></tr>
  <tr><td>策略</td><td><span class="mono">RedactOptions</span>：叠加式，可在默认上再加</td><td>（可保留指定头）</td></tr>
</table>
<p>落到实战，<span class="mono">session-runner-recorded.test.ts</span> 把这一切串了起来：它用 <span class="mono">HttpRecorder.http("session-runner/openai-chat-streams-text", { directory: fixtures/recordings, … })</span> 加载一盘<strong>录好的 OpenAI 流式响应磁带</strong>，然后<strong>回放整条 V2 session runner</strong>——L17 的 agent 循环、L28+ 的协议解析、流式分帧，全在这盘确定的录音上跑一遍，最后断言「runner 处理得对不对」。它甚至支持一个 <span class="mono">mode:"record"</span> 开关：平时回放（CI 里又快又稳），需要更新磁带时切到录制、真打一次 API 重录——这套「平时放磁带、要更新时重录一次」的工作流，正是成熟项目对待「依赖外部服务的测试」的标准姿势。把这一课嵌回全书，它处在三条线的交汇点：</p>
<div class="vflow">
  <div class="vnode"><b>L17 agent 循环</b>：本课<strong>被测的对象</strong>就是那条「问模型→跑工具→喂回」的非确定循环——磁带把「模型」这一变量固定住</div>
  <div class="vnode"><b>L28–L35 协议层</b>：本课<strong>被录的字节</strong>正是各家 provider 的真实 HTTP/流式响应——录放测的是真实协议解析，不是 mock 的假响应</div>
  <div class="vnode"><b>L63 测试哲学</b>：「测真实、可复现、少 mock」——本课是这条哲学的极致兑现：用真实录音而非凭空捏造，让不确定的循环变得可复现</div>
</div>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <span class="mono">http-recorder</span> 用「<strong>录放（record/replay）</strong>」驯服「调真实大模型」的非确定性。<strong>录制模式</strong>：真打一次 API，把请求-响应存成一盘命名 <strong>磁带（cassette）</strong>，落盘前把 API key/<span class="mono">Authorization</span> 等<strong>脱敏</strong>成 <span class="mono">[REDACTED]</span>（故磁带可安全入库当 fixture）。<strong>回放模式</strong>：进来的请求经 <span class="mono">canonicalSnapshot</span> 归一化 → <span class="mono">RequestMatcher</span> 匹配到对应录音 → 原样放出响应（含流式分帧）。两通道：<span class="mono">http</span> + <span class="mono">socket</span>。落地 <span class="mono">session-runner-recorded.test.ts</span> 用一盘磁带<strong>回放整条 V2 runner</strong>（L17）。本质：把「与外部世界的真实交互」从测试的每次运行里抽出来、只做一次、冻成确定录音——这是 L63「测真实、可复现」的极致手法，专治「非确定循环怎么测」。这套思路（测试圈常称 VCR/cassette 模式）适用于一切「依赖外部服务」的测试，而 opencode 把它用在了最尖锐的场景：调真实大模型。
</div>

<div class="card detail">
  <div class="tag">🔬 实现细节</div>
  <span class="mono">packages/http-recorder/src/index.ts</span>：<span class="mono">HttpRecorder = { http, socket }</span>；命名空间类型 <span class="mono">CassetteMetadata</span>(随磁带的 JSON 元数据)、<span class="mono">RecorderOptions</span>、<span class="mono">RedactOptions</span>(「Additive redaction and header-preservation policy」)、<span class="mono">RequestMatcher</span>(「Returns whether an incoming HTTP request matches a recorded request」)、<span class="mono">RequestSnapshot</span>(「The normalized HTTP request representation used for matching」)。<span class="mono">matching.ts</span>：<span class="mono">canonicalSnapshot(snapshot)</span> = JSON {method, url, <span class="mono">canonicalizeJson(headers)</span>, body: <span class="mono">decodeJson</span> 后规范化}；<span class="mono">decodeJson = Schema.decodeUnknownOption(JsonValue)</span>。<span class="mono">redaction.ts</span>：<span class="mono">REDACTED = "[REDACTED]"</span>、<span class="mono">DEFAULT_REDACT_HEADERS</span>(authorization/x-api-key/x-goog-api-key…)、<span class="mono">DEFAULT_REDACT_QUERY</span>。<span class="mono">core/test/session-runner-recorded.test.ts</span>：<span class="mono">HttpRecorder.http("session-runner/openai-chat-streams-text", {directory: fixtures/recordings, mode:"record"?})</span> + <span class="mono">HttpRecorderInternal.cassetteLayer</span>，回放整条 runner。整体看，<span class="mono">http-recorder</span> 是个职责单一、可独立复用的小包：录制器（recorder）、磁带（cassette）、匹配（matching）、脱敏（redaction）各管一摊，合起来提供「录一次、放无数次」的能力——又一个「为自己造趁手件」的例子（同 L08 工具箱）。
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>录放驯服非确定性</strong>：agent 循环每次「问模型」都不确定/花钱/慢，直接打真 API 让测试今天绿明天红。<span class="mono">http-recorder</span> 用<strong>录制</strong>（真打一次、存磁带）+ <strong>回放</strong>（之后放磁带）把它钉成确定、免费、毫秒、可离线的测试。边界：不验「模型答得对不对」，而验「给定已知响应，我的 runner/协议/工具逻辑对不对」（同 L63「测真实、少 mock」）。</li>
    <li><strong>磁带与匹配</strong>：<span class="mono">HttpRecorder={http,socket}</span> 录放 HTTP + WebSocket。回放靠 <span class="mono">RequestSnapshot</span>+<span class="mono">RequestMatcher</span>：<span class="mono">canonicalSnapshot</span> 把请求归一化成 {method,url,headers,body} 规范 JSON（<span class="mono">canonicalizeJson</span>/<span class="mono">decodeJson</span>），好让「语义同、字节序不同」的请求稳定命中同一盘。</li>
    <li><strong>脱敏故能入库</strong>：<span class="mono">redaction.ts</span> 把 <span class="mono">authorization</span>/<span class="mono">x-api-key</span>… 等（<span class="mono">DEFAULT_REDACT_HEADERS/QUERY</span>）替换成 <span class="mono">[REDACTED]</span> 再落盘，磁带不含真实密钥、可安全提交当 fixture。落地：<span class="mono">session-runner-recorded.test.ts</span> 用一盘磁带回放整条 V2 runner（L17 循环 + L28+ 协议）。是「如何确定地测不确定系统」的标准解。</li>
  </ul>
</div>
""",
    "en": r"""<p class="lead">How do you test an agent loop that <strong>calls a real LLM</strong>? It's a genuine problem: the model <strong>answers differently every time</strong> (non-deterministic), each call <strong>costs money</strong>, is <strong>slow</strong>, and the network may glitch. Hitting the real API in tests leaves results to fate—green today, red tomorrow, no one able to say whether the code broke or the model was just in a mood. opencode's answer is <span class="mono">http-recorder</span> (<span class="mono">packages/http-recorder/</span>): <strong>record a real provider round-trip onto a "cassette," then in tests stop hitting the real API and "play the tape"—replay that recorded response</strong>. So an inherently non-deterministic loop is pinned into a <strong>replayable, assertable, free, blazing-fast</strong> deterministic test. <span class="mono">core/test/session-runner-recorded.test.ts</span> does exactly this: with a recorded OpenAI streaming-response cassette, it <strong>replays the whole V2 session runner</strong> (L17's agent loop). This lesson covers the dedicated tool opencode built to "test its most core, hardest-to-test loop"—itself a standalone package <span class="mono">@opencode-ai/http-recorder</span>, showing how engineering-weighty this "record/replay" mechanism is.</p>
<p>There are two insights worth taking away. First, <strong>"record/replay" is the classic way to tame non-determinism</strong>: the first time, in <strong>record mode</strong>, really hit the API once and store the request and response verbatim as a named cassette; thereafter in <strong>replay mode</strong>, let an incoming request <strong>match by "what the request looks like"</strong> to its cassette and return the recorded response—the outside world's randomness and cost frozen into the tape once and for all. Second, an engineering touch of real finesse—<strong>auto-redaction on record</strong>: secrets like API keys and the <span class="mono">Authorization</span> header are replaced with <span class="mono">[REDACTED]</span> before saving, so the cassette can be safely committed to the repo as a fixture without dragging your keys into git. Grasp this "<strong>record the real world once, replay it infinitely</strong>" and you've mastered the standard solution to that thorniest testing problem: "how to deterministically test a non-deterministic system." This trick is hardly opencode-only—any code depending on an external service (third-party APIs, payment gateways, map services…) faces the "do we hit the real thing in tests" dilemma, and "record/replay (often called the VCR / cassette pattern in testing circles)" is the industry's classic answer. opencode built it into its own <span class="mono">http-recorder</span> package precisely because "calling a real LLM" is the sharpest of these problems: expensive, slow, different every time.</p>

<div class="card analogy">
  <div class="tag">🎙️ Analogy</div>
  Imagine rehearsing a play of "<strong>phoning an expert</strong>" over and over. The expert (the LLM) is expensive, answers differently each time, and may be busy—you can't place a real long-distance call every rehearsal. The clever move: <strong>place one real call carefully and <u>record the whole conversation onto a tape</u></strong> (record mode); while recording, <strong>"bleep out" sensitive info like phone numbers and passwords</strong> (redaction, masked as "<span class="mono">[REDACTED]</span>"). Thereafter, however many rehearsals, <strong>don't call for real—just play that tape</strong> (replay mode): the stagehand hears "dialed a certain number, asked a certain line," goes to the tape rack and <strong>finds the matching tape by "number + what was asked,"</strong> and plays back the recorded answer verbatim. So every rehearsal is <strong>identical</strong>, costs nothing, is lightning-fast, and the tape—being bleeped—can be safely filed in the troupe's archive (committed to the repo as a fixture). <span class="mono">http-recorder</span> is exactly this "record the real thing once, play the fake one endlessly" tape machine.
</div>

<h2>Why it's hard to test: a non-deterministic loop</h2>
<p>L17's agent loop is essentially "ask the model → run tools → feed results back → ask again," and <strong>each "ask the model" in this loop is non-deterministic</strong>: same input, the model may answer this way today, that way tomorrow; the call <strong>costs real money</strong> and goes over the network (slow and may fail). This poses a testing dilemma—a good test should be <strong>deterministic (same result each run), fast, free, offline-able</strong>, and "really hitting the model API" breaks all four: state the dilemma and you see why opencode would rather write a dedicated record/replay package than let the core loop's tests touch a real API.</p>
<div class="cols">
  <div class="col"><h4>Hitting the API in tests</h4><p>Results drift with the model (green today, red tomorrow), each run costs money, is slow, needs network, and keys must be managed. Tests become <strong>unreliable</strong>—when red, you can't tell if it's the code's fault or the model's.</p></div>
  <div class="col"><h4>Record/replay (http-recorder)</h4><p>Hit for real <strong>once</strong>, record a cassette; thereafter replay—results <strong>constant</strong>, zero cost, millisecond, offline-able, the redacted cassette committable. Tests become <strong>trustworthy</strong> again.</p></div>
</div>
<p>This is record/replay's value: it lifts "that one real interaction with the outside world" out of <strong>every test run</strong>, doing it once, freezing it into a tape, so every later test runs on this <strong>deterministic recording</strong>. Note its boundary—record/replay does not verify "whether the model answered correctly" (not a unit test's job); it verifies "<strong>given this known model response, does my runner / protocol parsing / tool dispatch logic handle it correctly</strong>." That is, it <strong>fixes</strong> the non-deterministic variable "the model" so you can focus on testing your own code. An analogy: to test whether a "vending machine" dispenses correctly on receiving a bill, you don't test "whether the mint printed the bill right"—you take a <strong>known-genuine sample bill</strong> and feed it repeatedly to test the machine's logic. The cassette is that sample bill: a known, fixed, real input. This aligns with L63's "test the real implementation, few mocks": the cassette isn't a fabricated fake response (that'd be a mock, easily producing "fake green"—mock passes, real environment crashes), but a <strong>faithful recording of one real interaction</strong>—still testing real protocol bytes and real stream framing, just "freeze-framed." It's a beautiful balance between "real" and "deterministic": neither as uncontrollable as hitting the API for real, nor as detached from reality as pure mocks.</p>

<h2>The tape mechanism: record once, play endlessly</h2>
<p><span class="mono">HttpRecorder = { http, socket }</span>—it records/replays two channels: plain HTTP and WebSocket (<span class="mono">socket</span>, corresponding to L33's streaming transport). Around "a cassette" is a clean set of types:</p>
<div class="cellgroup">
  <div class="cel"><b>Cassette</b><br>a named recording storing one (or more) request-response; written by <span class="mono">directory</span></div>
  <div class="cel"><b>RecorderOptions</b><br>recorder config (directory, <span class="mono">mode:"record"</span> vs replay…)</div>
  <div class="cel"><b>RequestSnapshot</b><br>"the normalized HTTP request representation"—the canonical form for matching</div>
  <div class="cel"><b>RequestMatcher</b><br>"whether an incoming request matches a recorded one"</div>
  <div class="cel"><b>RedactOptions</b><br>"additive redaction &amp; header-preservation policy"—which secrets to mask on record</div>
  <div class="cel"><b>CassetteMetadata</b><br>JSON metadata stored with the cassette</div>
</div>
<p>Replay's key is <strong>matching</strong>: a cassette library may hold several request-responses; given a new incoming request, how to know which to play? Via <span class="mono">RequestMatcher</span> + <span class="mono">RequestSnapshot</span>. <span class="mono">matching.ts</span>'s <span class="mono">canonicalSnapshot(snapshot)</span> <strong>normalizes</strong> a request into canonical JSON—taking its <span class="mono">method</span>, <span class="mono">url</span>, <span class="mono">canonicalizeJson(headers)</span>, and the body parsed as JSON then normalized (<span class="mono">decodeJson</span>). "Normalization" makes two requests that are "semantically same but byte-order different" recognized as one (e.g. different JSON field order, different whitespace), reliably hitting the same cassette. Why normalize instead of comparing byte-for-byte? Because an HTTP request's "literal form" has much irrelevant jitter—the same JSON body may serialize with different field order or indentation, yet it's <strong>semantically the same request</strong>. With byte comparison, replay would <strong>fail to find the cassette</strong> over these irrelevant differences, the test failing inexplicably; normalization smooths out the noise, keeping only the "semantic fingerprint," so matching is stable. The replay path is thus:</p>
<div class="trace">
  <div class="step"><span class="n">1</span> the runner in the test sends a request (e.g. hits OpenAI's <span class="mono">/chat/completions</span>)</div>
  <div class="step"><span class="n">2</span> <span class="mono">canonicalSnapshot</span> normalizes it into canonical form (method+url+headers+body)</div>
  <div class="step"><span class="n">3</span> <span class="mono">RequestMatcher</span> finds the matching recording in the cassette library</div>
  <div class="step"><span class="n">4</span> plays back the recorded response (with stream framing), the runner handles it as usual → assert the result</div>
</div>

<h2>Redaction &amp; landing: why the cassette can be safely committed</h2>
<p>If on record you stored the request verbatim, your API key and <span class="mono">Authorization</span> header would be written into the cassette file—commit it to git and you've leaked the key. <span class="mono">http-recorder</span> solves this with <strong>redaction</strong>: <span class="mono">redaction.ts</span> defines <span class="mono">REDACTED = "[REDACTED]"</span> and a default set of sensitive headers/query params to mask (<span class="mono">DEFAULT_REDACT_HEADERS</span> includes <span class="mono">authorization</span>, <span class="mono">x-api-key</span>, <span class="mono">x-goog-api-key</span>, etc.; <span class="mono">DEFAULT_REDACT_QUERY</span> likewise)—on record, these fields are replaced with <span class="mono">[REDACTED]</span> before saving. Note <span class="mono">RedactOptions</span>'s wording is "<strong>additive</strong>": the default list is a safety floor, and you can add more fields to mask on top of it rather than write one from scratch—a typical way of stacking "safe defaults" with "customizable" (echoing L60 PTY env's "customizable in the middle, non-negotiable last"). So the cassette keeps "what the request looks like" (enough to match) yet <strong>contains no real secret</strong>, safely committable to the repo and reusable long-term as a test fixture. The <strong>record</strong> path is thus:</p>
<div class="flow">
  <div class="node">runner hits an API once</div>
  <div class="arrow">→</div>
  <div class="node">capture request-response</div>
  <div class="arrow">→</div>
  <div class="node"><strong>redact</strong><br>key/Authorization→<span class="mono">[REDACTED]</span></div>
  <div class="arrow">→</div>
  <div class="node">write a named cassette<br>(safely committable)</div>
</div>
<p>The default redaction list is roughly:</p>
<table class="t">
  <tr><th>Category</th><th>Default redacted (examples)</th><th>Replaced with</th></tr>
  <tr><td>Request headers</td><td><span class="mono">authorization</span>, <span class="mono">x-api-key</span>, <span class="mono">x-goog-api-key</span>…</td><td><span class="mono">[REDACTED]</span></td></tr>
  <tr><td>Query params</td><td>sensitive keys in <span class="mono">DEFAULT_REDACT_QUERY</span></td><td><span class="mono">[REDACTED]</span></td></tr>
  <tr><td>Policy</td><td><span class="mono">RedactOptions</span>: additive, add atop defaults</td><td>(can preserve specified headers)</td></tr>
</table>
<p>In practice, <span class="mono">session-runner-recorded.test.ts</span> ties it all together: it uses <span class="mono">HttpRecorder.http("session-runner/openai-chat-streams-text", { directory: fixtures/recordings, … })</span> to load a <strong>recorded OpenAI streaming-response cassette</strong>, then <strong>replays the whole V2 session runner</strong>—L17's agent loop, L28+'s protocol parsing, stream framing, all run once on this deterministic recording, finally asserting "does the runner handle it right." It even supports a <span class="mono">mode:"record"</span> switch: normally replay (fast and stable in CI), switch to record to re-hit the API and re-record when the cassette needs updating—this "play the tape normally, re-record once when updating" workflow is exactly mature projects' standard stance toward "tests depending on external services." Fit this lesson back into the book and it sits at the meeting of three threads:</p>
<div class="vflow">
  <div class="vnode"><b>L17 agent loop</b>: this lesson's <strong>subject under test</strong> is that "ask model→run tools→feed back" non-deterministic loop—the cassette fixes the "model" variable</div>
  <div class="vnode"><b>L28–L35 protocol layer</b>: the <strong>bytes being recorded</strong> are each provider's real HTTP/streaming response—record/replay tests real protocol parsing, not a mock's fake response</div>
  <div class="vnode"><b>L63 testing philosophy</b>: "test real, reproducible, few mocks"—this lesson is that philosophy's ultimate realization: use a real recording, not fabrication, to make a non-deterministic loop reproducible</div>
</div>

<div class="card macro">
  <div class="tag">🗺️ Big picture</div>
  <span class="mono">http-recorder</span> tames the non-determinism of "calling a real LLM" with "<strong>record/replay</strong>." <strong>Record mode</strong>: hit an API once, store the request-response as a named <strong>cassette</strong>, and before saving <strong>redact</strong> API keys/<span class="mono">Authorization</span> etc. to <span class="mono">[REDACTED]</span> (so the cassette is safely committable as a fixture). <strong>Replay mode</strong>: an incoming request is normalized by <span class="mono">canonicalSnapshot</span> → <span class="mono">RequestMatcher</span> matches the recording → plays back the response verbatim (with stream framing). Two channels: <span class="mono">http</span> + <span class="mono">socket</span>. Landing: <span class="mono">session-runner-recorded.test.ts</span> uses a cassette to <strong>replay the whole V2 runner</strong> (L17). Essence: lift "the real interaction with the outside world" out of every test run, do it once, freeze it into a deterministic recording—the ultimate form of L63's "test real, reproducible," curing "how to test a non-deterministic loop." This approach (often the VCR/cassette pattern in testing circles) applies to any "external-service-dependent" test, and opencode uses it on the sharpest case: calling a real LLM.
</div>

<div class="card detail">
  <div class="tag">🔬 Implementation details</div>
  <span class="mono">packages/http-recorder/src/index.ts</span>: <span class="mono">HttpRecorder = { http, socket }</span>; namespace types <span class="mono">CassetteMetadata</span>(JSON metadata with the cassette), <span class="mono">RecorderOptions</span>, <span class="mono">RedactOptions</span>("Additive redaction and header-preservation policy"), <span class="mono">RequestMatcher</span>("Returns whether an incoming HTTP request matches a recorded request"), <span class="mono">RequestSnapshot</span>("The normalized HTTP request representation used for matching"). <span class="mono">matching.ts</span>: <span class="mono">canonicalSnapshot(snapshot)</span> = JSON {method, url, <span class="mono">canonicalizeJson(headers)</span>, body: normalized after <span class="mono">decodeJson</span>}; <span class="mono">decodeJson = Schema.decodeUnknownOption(JsonValue)</span>. <span class="mono">redaction.ts</span>: <span class="mono">REDACTED = "[REDACTED]"</span>, <span class="mono">DEFAULT_REDACT_HEADERS</span>(authorization/x-api-key/x-goog-api-key…), <span class="mono">DEFAULT_REDACT_QUERY</span>. <span class="mono">core/test/session-runner-recorded.test.ts</span>: <span class="mono">HttpRecorder.http("session-runner/openai-chat-streams-text", {directory: fixtures/recordings, mode:"record"?})</span> + <span class="mono">HttpRecorderInternal.cassetteLayer</span>, replaying the whole runner. Overall, <span class="mono">http-recorder</span> is a single-responsibility, independently-reusable package: recorder, cassette, matching, redaction each handle one slice, together providing "record once, play endlessly"—another "build a handy part for yourself" example (like L08's toolbox).
</div>

<div class="card key">
  <div class="tag">🎯 Key points</div>
  <ul>
    <li><strong>Record/replay tames non-determinism</strong>: the agent loop's every "ask the model" is non-deterministic/costly/slow; hitting the real API makes tests green today, red tomorrow. <span class="mono">http-recorder</span> uses <strong>record</strong> (hit once, store a cassette) + <strong>replay</strong> (play the tape after) to pin it into a deterministic, free, millisecond, offline-able test. Boundary: it doesn't verify "did the model answer right" but "given a known response, is my runner/protocol/tool logic right" (like L63 "test real, few mocks").</li>
    <li><strong>Cassette &amp; matching</strong>: <span class="mono">HttpRecorder={http,socket}</span> records/replays HTTP + WebSocket. Replay relies on <span class="mono">RequestSnapshot</span>+<span class="mono">RequestMatcher</span>: <span class="mono">canonicalSnapshot</span> normalizes a request into canonical JSON {method,url,headers,body} (<span class="mono">canonicalizeJson</span>/<span class="mono">decodeJson</span>) so "semantically same, byte-order different" requests reliably hit the same cassette.</li>
    <li><strong>Redaction makes it committable</strong>: <span class="mono">redaction.ts</span> replaces <span class="mono">authorization</span>/<span class="mono">x-api-key</span>… (<span class="mono">DEFAULT_REDACT_HEADERS/QUERY</span>) with <span class="mono">[REDACTED]</span> before saving, so the cassette holds no real key and is safely committable as a fixture. Landing: <span class="mono">session-runner-recorded.test.ts</span> uses a cassette to replay the whole V2 runner (L17 loop + L28+ protocol). It's the standard solution to "how to deterministically test a non-deterministic system."</li>
  </ul>
</div>
""",
}
LESSON_68 = wip('Account 与设备码 OAuth', 'Account & device-code OAuth')
LESSON_69 = wip('其余生态一览', 'Ecosystem tour')
