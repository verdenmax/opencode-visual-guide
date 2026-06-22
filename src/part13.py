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
LESSON_66 = wip('斜杠命令系统', 'Slash commands')
LESSON_67 = wip('http-recorder 磁带录放测试', 'http-recorder tape testing')
LESSON_68 = wip('Account 与设备码 OAuth', 'Account & device-code OAuth')
LESSON_69 = wip('其余生态一览', 'Ecosystem tour')
