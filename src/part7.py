"""Part 7 (Part 7 · Tool System) content. Placeholders until M7 fills them in."""
from placeholder import wip

LESSON_36 = {
    "zh": r"""
<p class="lead">M6 我们讲完了「LLM 协议层」——那是 agent 的<strong>嘴和脑</strong>：怎么跟模型对话、把话翻成各家方言。但一个 agent 光会说话还不够，它得真能<strong>干活</strong>：读文件、改代码、跑命令、搜索……这些「干活」的能力，就是<strong>工具（tool）</strong>，是 agent 的<strong>手</strong>。M7 这一整个 part，讲的就是 opencode 的工具系统。而这第一课，我们从最根上问起：<strong>「一个工具」到底是什么？怎么定义出来的？</strong>答案出奇地简洁——一个工具，就是填一张叫 <span class="mono">Tool.make</span> 的<strong>表</strong>，而这张表的灵魂，是一份<strong>在每一道关口都说了算的 schema</strong>。</p>
<p>读这一课时，你会反复想起 M6 的两个老朋友：第 29 课「每个协议都填同一张两栏表」，和第 22 课「codec 一肩三役」。工具的设计是同一种智慧的再现——<strong>每个工具都填同一张 <span class="mono">Config</span> 表</strong>（无论它是 read 还是 bash），而<strong>一份 schema 同时管三件事</strong>：告诉模型怎么调、校验模型传进来的输入、校验工具吐出来的输出。把这两点看透，你就握住了整个工具系统的钥匙——后面 L38~L40 讲的所有具体工具，都只是「这张表的不同填法」，无论它读文件还是跑命令，骨架分毫不差。</p>

<div class="card analogy">
  <div class="tag">🔬 生活类比</div>
  把一个工具想象成实验室里一台<strong>带规格说明书的精密仪器</strong>。模型（用户）<strong>不能直接去拨弄仪器的线路</strong>——它只能：先读<strong>说明书</strong>（这台仪器吃什么输入、吐什么输出，即 JSON schema），照着填一张<strong>申请单</strong>（input），交给<strong>调度员</strong>（<span class="mono">settle</span>）。调度员办三件事：一、<strong>查申请单填得对不对</strong>（按 input schema 解码校验，填错了当场退回）；二、<strong>开动仪器</strong>（execute）；三、<strong>查仪器吐出来的结果合不合规格</strong>（按 output schema 编码校验），然后把结果<strong>同时</strong>交出两份——一份<strong>结构化档案</strong>（归档用）、一份<strong>人话摘要</strong>（给模型读）。至于仪器的<strong>内部线路</strong>，被锁在一个<strong>专用柜子</strong>里（WeakMap）——你拿到的「仪器」其实只是一把钥匙牌，真正的机芯你碰不到，只能通过调度员的窗口去操作它。这套「说明书 + 申请单 + 调度员 + 上锁的机芯」，就是 opencode 一个工具的全貌。
</div>

<h2>一张定义表：Tool.make 的 Config</h2>
<p>打开 <span class="mono">core/src/tool/tool.ts</span>，定义一个工具的入口就一个函数 <span class="mono">Tool.make(config)</span>。这个 <span class="mono">config</span> 长什么样？干净得像一张表格——<strong>每个工具都填这同一张表</strong>：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">description</div><div class="c-txt">这工具是干嘛的（这段话直接给模型读，是它决定要不要调的依据）</div></div>
  <div class="cell"><div class="c-tag">input</div><div class="c-txt">输入的 Schema（codec）：这工具吃什么参数</div></div>
  <div class="cell"><div class="c-tag">output</div><div class="c-txt">输出的 Schema（codec）：这工具吐什么结果</div></div>
  <div class="cell"><div class="c-tag">execute</div><div class="c-txt">真正干活的函数：(input, context) =&gt; Effect&lt;output, ToolFailure&gt;</div></div>
  <div class="cell"><div class="c-tag">toModelOutput?</div><div class="c-txt">可选：把结果渲染成给模型看的内容（text / file）</div></div>
</div>
<p>这张表的<strong>核心三件</strong>是 <span class="mono">input</span> / <span class="mono">output</span> / <span class="mono">execute</span>：声明「吃什么、吐什么、怎么算」。<span class="mono">execute</span> 的签名 <span class="mono">(input, context) =&gt; Effect&lt;output, ToolFailure&gt;</span> 透着浓浓的本书气息——<strong>输入输出都是带类型的</strong>（由 input/output schema 推导）、<strong>错误是值不是异常</strong>（<span class="mono">ToolFailure</span>，呼应第 5、8 课）、还捎上一个 <span class="mono">context</span>。这和第 29 课协议的「两栏表」是同一种设计哲学：<strong>把一类东西的共性钉成一张表，让每个实例只管填空</strong>。read 工具、bash 工具、grep 工具……千差万别，但都在填这同一张 <span class="mono">Config</span> 表。</p>
<p>那个捎带的 <span class="mono">context</span> 是什么？它是每次工具执行都会拿到的<strong>「身份四件套」</strong>，把这次调用<strong>锚回它所属的会话与 agent</strong>：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">sessionID</div><div class="c-txt">这次调用属于哪个会话（接回第 14 课的会话数据模型）</div></div>
  <div class="cell"><div class="c-tag">agent</div><div class="c-txt">是哪个 agent 在调（接回 M8 的 agents）</div></div>
  <div class="cell"><div class="c-tag">assistantMessageID</div><div class="c-txt">挂在哪条助手消息下</div></div>
  <div class="cell"><div class="c-tag">toolCallID</div><div class="c-txt">这是第几次工具调用（一轮里可能有好多次）</div></div>
</div>
<p>别小看这四个字段：它让一个工具<strong>「知道自己身处何地」</strong>。一个 read 工具要读「当前会话的工作目录」、一个权限检查要问「这个 agent 允不允许」、一个输出要挂到「正确的那条消息」上——靠的都是 context。工具不是悬空运行的纯函数，它<strong>长在一棵会话树上</strong>，context 就是那根连着树根、让它时刻知道「我为谁、在哪、第几次」干活的线。</p>

<h2>schema 一肩三役：每道关口都说了算</h2>
<p>这一课最该带走的洞见，是 <span class="mono">input</span>/<span class="mono">output</span> 这两份 schema 的<strong>分量</strong>。它们不只是「类型标注」，而是<strong>在工具生命周期的三个关口同时把关的契约</strong>：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">① 给模型看</div><div class="c-txt">definition(name) 把 input/output schema 转成 JSON Schema，连同 description 一起发给模型——模型据此知道「这工具怎么调」</div></div>
  <div class="cell"><div class="c-tag">② 校验进来的输入</div><div class="c-txt">settle 先用 input schema 解码模型传来的原始参数；不合法 → ToolFailure，不是崩溃</div></div>
  <div class="cell"><div class="c-tag">③ 校验出去的输出</div><div class="c-txt">execute 算完，再用 output schema 编码校验；工具吐错了形状 → 也是 ToolFailure</div></div>
</div>
<p>看明白了吗？<strong>同一份 schema，声明一次，却在三处把关</strong>：对外，它是给模型的「使用说明书」；对内，它是输入的「安检门」和输出的「质检口」。这正是第 22 课「codec 一肩三役」在工具层的再现——你只声明「这工具的输入长这样、输出长这样」，<strong>「怎么生成说明书、怎么校验、怎么序列化」全都自来</strong>。更妙的是它对<strong>失败的处理</strong>：模型常常会传来不合 schema 的乱参数（幻觉、笔误），工具也可能因 bug 吐出不合规的结果——这两种「脏数据」都被 schema 在关口<strong>挡成一个规规矩矩的 <span class="mono">ToolFailure</span> 值</strong>，而不是让一个异常炸穿整个 agent 循环。<strong>schema 是工具与混沌世界之间的那道防线</strong>，它把外部的不确定，挡成了内部一个确定的值。</p>
<div class="trace">
  <div class="t-row"><span class="t-num">①decode</span><span class="t-txt">decodeUnknown(input)(call.input)：校验模型传来的参数 → 失败即 ToolFailure</span></div>
  <div class="t-row"><span class="t-num">②execute</span><span class="t-txt">config.execute(input, context)：真正干活</span></div>
  <div class="t-row"><span class="t-num">③encode</span><span class="t-txt">encode(output)(结果)：校验输出形状 → 失败即 ToolFailure</span></div>
  <div class="t-row"><span class="t-num">④出两份</span><span class="t-txt">{ structured: 结构化结果, content: 给模型看的 text/file }</span></div>
</div>
<p>最后那一步 <span class="mono">④</span> 也值得品：<span class="mono">settle</span> 吐出的不是一坨东西，而是<strong>两份</strong>——<span class="mono">structured</span>（结构化结果，给系统归档）和 <span class="mono">content</span>（给模型读的内容）。<span class="mono">content</span> 怎么来？若工具提供了 <span class="mono">toModelOutput</span>，就用它渲染；否则，输出是字符串就直接当文本给模型、不是字符串就给空。这是「<strong>对系统用结构、对模型用人话</strong>」的分治——又一次呼应第 22 课「沟通用散文、记忆用结构」。</p>
<div class="cols">
  <div class="col"><h4>structured（给系统）</h4><p>output schema 编码后的<strong>结构化值</strong>，原原本本归档进消息历史，供日后程序化读取、重放、审计。</p></div>
  <div class="col"><h4>content（给模型）</h4><p>由 <span class="mono">toModelOutput</span> 渲染的 <span class="mono">text</span>/<span class="mono">file</span> 列表——只放<strong>模型该看的那一面</strong>。一个工具可以「内部记一大坨、只给模型看一句」。</p></div>
</div>
<p>为什么要把这两份<strong>分开</strong>？因为「系统要记的」和「模型该看的」常常不是一回事。比如一个文件读取工具，结构化结果里可能有完整的字节数、行号、编码信息（系统归档有用），但给模型的 content 只需要文件内容本身；又比如某些工具内部结果很大，却只想给模型一句「已完成，写入 42 行」。把 <span class="mono">structured</span> 和 <span class="mono">content</span> 解耦，工具就能<strong>各按所需地「对内详尽、对外精炼」</strong>——这也为第 42 课「有界输出」埋了伏笔：给模型的那一面，是可以被裁剪的。</p>

<h2>不透明的句柄：一把钥匙牌 + 上锁的机芯</h2>
<p>还有个设计精巧到容易被忽略的细节：<span class="mono">Tool.make</span> 返回的「工具」<strong>到底是个什么东西</strong>？你可能以为是个带方法的对象。但看源码——它返回的是 <span class="mono">Object.freeze({})</span>，<strong>一个冻结的空对象</strong>！那真正的行为（definition/settle/permission）藏哪了？藏在一个模块级的 <span class="mono">WeakMap&lt;AnyTool, Runtime&gt;</span> 里：</p>
<div class="flow">
  <div class="f-node">Tool.make(config)<br><small>返回 Object.freeze(&#123;&#125;)</small></div>
  <div class="f-arrow">登记 →</div>
  <div class="f-node">WeakMap&lt;工具, Runtime&gt;<br><small>真正的 definition/settle 在这</small></div>
  <div class="f-arrow">Tool.settle(工具,…) 查 →</div>
  <div class="f-node">取出 Runtime 执行<br><small>外人碰不到机芯</small></div>
</div>
<p>为什么要这么绕？因为这样一来，「工具」这个值对外就是一把<strong>纯粹的「钥匙牌」</strong>——它的类型 <span class="mono">Definition&lt;Input, Output&gt;</span> 只携带幽灵般的类型信息（用一个 <span class="mono">[TypeId]</span> 记住 Input/Output 是什么），<strong>没有任何可被外人直接拨弄的运行时表面</strong>。你拿到一个工具，<strong>除了把它交给 <span class="mono">Tool.settle</span> / <span class="mono">Tool.definition</span>，什么也做不了</strong>。这是「信息隐藏」做到极致的优雅：值是一张<strong>能力凭证</strong>，行为锁在私有登记处。装饰器 <span class="mono">withPermission(tool, "权限名")</span> 也顺理成章——它造一把<strong>新钥匙牌</strong>，在 WeakMap 里指向一份「带权限」的 Runtime（第 41 课权限系统的接入点就在这）。而用 WeakMap 还有个隐藏福利：工具被 GC 回收时，它的 Runtime <strong>自动一起释放</strong>，不留内存泄漏。</p>
<p>这种「值是凭证、行为在别处」的写法，初看绕，细想极有道理。它换来三样东西：其一，<strong>不可篡改</strong>——拿到工具的人改不了它的行为（空对象上没有任何方法可覆盖），只能照规矩用；其二，<strong>装饰即新值</strong>——<span class="mono">withPermission</span> 不去<strong>修改</strong>原工具，而是<strong>派生</strong>一把新钥匙牌指向增强后的 Runtime，原工具纹丝不动（不可变思维，第 24 课的老调重弹）；其三，<strong>类型与运行时彻底分离</strong>——类型层只剩 <span class="mono">Input</span>/<span class="mono">Output</span> 两个幽灵参数，编译器能据此保证你给某工具传的 input、收的 output 都对得上号，而运行时的脏活全藏在 WeakMap 里不污染类型。<strong>一个看似奇怪的「返回空对象」，其实是把「不可篡改、可派生、类型干净」三件好事一次性买齐。</strong></p>
<p>顺带一提工具名的小门槛：<span class="mono">validateName</span> 要求名字匹配 <span class="mono">/^[A-Za-z][A-Za-z0-9_-]{0,63}$/</span>——字母开头、最长 64 字符、只含字母数字和 <span class="mono">-_</span>。为什么要管这个？因为工具名要<strong>原样进入发给模型的 JSON Schema</strong>、还要在权限和注册表里当 key，一个干净规整的命名约束，能从源头挡掉一堆奇怪字符引发的麻烦。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <p>这一课立起了整个工具系统的<strong>地基</strong>：</p>
  <ul>
    <li><strong>一个工具 = 填一张 <span class="mono">Config</span> 表</strong>（<span class="mono">Tool.make</span>）：description（给模型读）+ input/output（schema）+ execute（干活）+ 可选 toModelOutput。每个工具都填这同一张表，正如第 29 课每个协议都填「两栏表」。</li>
    <li><strong>schema 一肩三役</strong>：① <span class="mono">definition</span> 转 JSON Schema 给模型当说明书；② <span class="mono">settle</span> 用 input schema 解码校验进来的参数；③ 用 output schema 编码校验出去的结果。脏输入/脏输出都被挡成 <span class="mono">ToolFailure</span> 值，不炸 agent 循环。</li>
    <li><strong>settle 流水线</strong>：decode 输入 → execute 干活 → encode 输出 → 出 <span class="mono">{structured, content}</span> 两份（系统用结构、模型用人话）。</li>
    <li><strong>不透明句柄 + WeakMap</strong>：<span class="mono">make</span> 返回冻结空对象，真正 Runtime 锁在 <span class="mono">WeakMap&lt;AnyTool,Runtime&gt;</span>；工具是「能力凭证」，只能交给 settle/definition 用。<span class="mono">withPermission</span> 造新句柄叠权限。</li>
  </ul>
  <p>有了这张「工具的形」，后面就顺了：第 37 课讲<strong>工具注册表</strong>（这些定义好的工具怎么被收集、按 Location 物化成模型可见的清单）；第 38~40 课讲<strong>具体工具</strong>（read/write/edit、glob/grep/bash、webfetch/question/todowrite——全是这张 Config 表的不同填法）；第 41 课讲<strong>权限</strong>（就是 <span class="mono">withPermission</span> 埋下的那条线）；第 42 课讲<strong>有界输出</strong>（execute 吐出的大结果怎么截断）。这一课的 <span class="mono">Tool.make</span>，是后面这一切的原点。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p><span class="mono">settle</span> 那条 Effect 链，把「校验—执行—再校验」串得极漂亮（简化自 tool.ts）：</p>
  <pre class="code"><span class="cm">// settle：一条 decode → execute → encode 的管道</span>
Schema.<span class="fn">decodeUnknownEffect</span>(config.input)(call.input).pipe(
  Effect.<span class="fn">mapError</span>(e =&gt; <span class="kw">new</span> ToolFailure({ message: <span class="st">`Invalid tool input: ...`</span> })),
  Effect.<span class="fn">flatMap</span>(input =&gt;
    config.<span class="fn">execute</span>(input, context).pipe(        <span class="cm">// 真正干活</span>
      Effect.<span class="fn">flatMap</span>(output =&gt;
        Schema.<span class="fn">encodeEffect</span>(config.output)(output)   <span class="cm">// 校验输出形状</span>
          .pipe(Effect.<span class="fn">mapError</span>(e =&gt; <span class="kw">new</span> ToolFailure({ ... }))),
      ),
      Effect.<span class="fn">map</span>(output =&gt; ({ structured: output, content: ... })),
    ),
  ),
)</pre>
  <p>注意两处 <span class="mono">mapError</span> 把两类失败都<strong>收敛成同一种 <span class="mono">ToolFailure</span></strong>：输入不合法、输出不合规——对上层而言，工具失败就是一个统一的值，agent 循环（第 17 课）拿到它就能优雅处理（把错误回传给模型让它改），而不必区分「是模型传错了还是工具算错了」。还有个收尾的小心思：当工具没给 <span class="mono">toModelOutput</span>、且输出本身就是个字符串时，<span class="mono">content</span> 默认<strong>直接把这串字符当文本</strong>给模型——让「输出即文本」的简单工具零负担。<strong>复杂留给需要的人，简单还给大多数</strong>，这种默认值的体贴，是好 API 的标志。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>工具是 agent 的「手」</strong>：M6 是嘴和脑（对话模型），M7 是手（读写文件/跑命令/搜索）。本课问「一个工具怎么定义」。</li>
    <li><strong><span class="mono">Tool.make(config)</span> 一张表</strong>（<span class="mono">core/src/tool/tool.ts</span>）：<span class="mono">description</span>（给模型读）/ <span class="mono">input</span> / <span class="mono">output</span>（schema）/ <span class="mono">execute: (input, context) =&gt; Effect&lt;output, ToolFailure&gt;</span> / 可选 <span class="mono">toModelOutput</span>。每个工具都填这同一张表（同第 29 课协议两栏表）。</li>
    <li><strong>schema 一肩三役</strong>：① <span class="mono">definition(name)</span> → JSON Schema 给模型当说明书；② <span class="mono">settle</span> 用 input schema 解码校验输入；③ 用 output schema 编码校验输出。脏输入/脏输出都收敛成 <span class="mono">ToolFailure</span> 值（不炸循环）。是第 22 课「codec 一肩三役」的再现。</li>
    <li><strong><span class="mono">settle</span> 流水线</strong>：decode → execute → encode → <span class="mono">{structured（系统归档）, content（模型可读 text/file）}</span>。无 toModelOutput 且输出为字符串时，content 默认即该字符串。</li>
    <li><strong>不透明句柄 + WeakMap</strong>：<span class="mono">make</span> 返回 <span class="mono">Object.freeze({})</span>，真正 Runtime（definition/settle/permission）藏在模块级 <span class="mono">WeakMap&lt;AnyTool, Runtime&gt;</span>。工具是「能力凭证」，只能交给 <span class="mono">Tool.settle/definition</span>；<span class="mono">withPermission</span> 造新句柄叠权限（第 41 课接入点）。<span class="mono">Context = {sessionID, agent, assistantMessageID, toolCallID}</span>。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">M6 finished the "LLM protocol layer"—the agent's <strong>mouth and brain</strong>: how to talk to models, translating speech into each vendor's dialect. But an agent that only talks isn't enough; it must actually <strong>do work</strong>: read files, edit code, run commands, search… These "do-work" capabilities are <strong>tools</strong>, the agent's <strong>hands</strong>. This whole part, M7, covers opencode's tool system. And this first lesson asks the most foundational question: <strong>what exactly is "a tool"? How is one defined?</strong> The answer is surprisingly clean—a tool is just filling out a <strong>form</strong> called <span class="mono">Tool.make</span>, and that form's soul is a <strong>schema that has the final say at every gate</strong>.</p>
<p>Reading this lesson, you'll repeatedly recall two old friends from M6: lesson 29's "every protocol fills the same two-column form," and lesson 22's "a codec wears three hats." A tool's design is the same wisdom recurring—<strong>every tool fills the same <span class="mono">Config</span> form</strong> (whether read or bash), and <strong>one schema governs three things at once</strong>: telling the model how to call it, validating the input the model passes in, validating the output the tool spits out. Grasp these two points and you hold the key to the whole tool system—all the concrete tools in L38–L40 are just "different fillings of this form."</p>

<div class="card analogy">
  <div class="tag">🔬 Analogy</div>
  Picture a tool as a <strong>precision lab instrument with a spec sheet</strong>. The model (user) <strong>can't directly fiddle with the instrument's wiring</strong>—it can only: first read the <strong>spec sheet</strong> (what inputs the instrument takes, what outputs it produces, i.e. the JSON schema), fill out a <strong>request form</strong> accordingly (the input), and hand it to the <strong>dispatcher</strong> (<span class="mono">settle</span>). The dispatcher does three things: one, <strong>check the form is filled correctly</strong> (decode-validate against the input schema; if wrong, bounce it back); two, <strong>run the instrument</strong> (execute); three, <strong>check the instrument's output meets spec</strong> (encode-validate against the output schema), then hand back <strong>two</strong> copies—a <strong>structured record</strong> (for the files) and a <strong>plain-language summary</strong> (for the model to read). As for the instrument's <strong>internal wiring</strong>, it's locked in a <strong>dedicated cabinet</strong> (a WeakMap)—the "instrument" you hold is really just a key tag, the actual mechanism you can't touch, only operate through the dispatcher's slots. This "spec sheet + request form + dispatcher + locked mechanism" is the full picture of one opencode tool.
</div>

<h2>One definition form: Tool.make's Config</h2>
<p>Open <span class="mono">core/src/tool/tool.ts</span> and the entry to defining a tool is one function <span class="mono">Tool.make(config)</span>. What does this <span class="mono">config</span> look like? Clean as a table—<strong>every tool fills this same form</strong>:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">description</div><div class="c-txt">what the tool does (this text goes straight to the model—its basis for deciding whether to call it)</div></div>
  <div class="cell"><div class="c-tag">input</div><div class="c-txt">the input Schema (codec): what parameters this tool takes</div></div>
  <div class="cell"><div class="c-tag">output</div><div class="c-txt">the output Schema (codec): what result this tool produces</div></div>
  <div class="cell"><div class="c-tag">execute</div><div class="c-txt">the function that actually works: (input, context) =&gt; Effect&lt;output, ToolFailure&gt;</div></div>
  <div class="cell"><div class="c-tag">toModelOutput?</div><div class="c-txt">optional: render the result into content the model sees (text / file)</div></div>
</div>
<p>The form's <strong>core three</strong> are <span class="mono">input</span> / <span class="mono">output</span> / <span class="mono">execute</span>: declaring "what it takes, what it produces, how it computes." <span class="mono">execute</span>'s signature <span class="mono">(input, context) =&gt; Effect&lt;output, ToolFailure&gt;</span> reeks of this book's spirit—<strong>typed input and output</strong> (inferred from the input/output schemas), <strong>errors as values not exceptions</strong> (<span class="mono">ToolFailure</span>, echoing lessons 5, 8), plus a <span class="mono">context</span>. This is the same design philosophy as lesson 29's protocol "two-column form": <strong>nail a category's commonality into one form, and each instance just fills in the blanks</strong>. The read tool, bash tool, grep tool… wildly different, all filling this same <span class="mono">Config</span>.</p>
<p>What's that tagging-along <span class="mono">context</span>? It's the <strong>"identity four-pack"</strong> every tool execution receives, <strong>anchoring this call back to its session and agent</strong>:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">sessionID</div><div class="c-txt">which session this call belongs to (back to lesson 14's session data model)</div></div>
  <div class="cell"><div class="c-tag">agent</div><div class="c-txt">which agent is calling (back to M8's agents)</div></div>
  <div class="cell"><div class="c-tag">assistantMessageID</div><div class="c-txt">under which assistant message it hangs</div></div>
  <div class="cell"><div class="c-tag">toolCallID</div><div class="c-txt">which tool call this is (a turn may have many)</div></div>
</div>
<p>Don't underestimate these four fields: they let a tool <strong>"know where it is."</strong> A read tool reading "the current session's working directory," a permission check asking "does this agent allow it," an output hanging onto "the right message"—all rely on context. A tool isn't a free-floating pure function; it <strong>grows on a session tree</strong>, and context is the thread tying it to the root.</p>

<h2>The schema wears three hats: final say at every gate</h2>
<p>This lesson's must-take insight is the <strong>weight</strong> of the two schemas <span class="mono">input</span>/<span class="mono">output</span>. They aren't just "type annotations" but a <strong>contract guarding three gates of the tool lifecycle at once</strong>:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">① shown to the model</div><div class="c-txt">definition(name) turns input/output schemas into JSON Schema, sent with description to the model—so it knows "how to call this tool"</div></div>
  <div class="cell"><div class="c-tag">② validating input in</div><div class="c-txt">settle first decodes the model's raw params via the input schema; invalid → ToolFailure, not a crash</div></div>
  <div class="cell"><div class="c-tag">③ validating output out</div><div class="c-txt">after execute, encode-validate via the output schema; a tool spitting the wrong shape → also ToolFailure</div></div>
</div>
<p>See it? <strong>The same schema, declared once, guards three gates</strong>: outward, it's the model's "user manual"; inward, it's the input's "security checkpoint" and the output's "quality control." This is lesson 22's "codec wears three hats" recurring at the tool layer—you only declare "this tool's input looks like this, output like that," and <strong>"how to generate the manual, how to validate, how to serialize" all come for free</strong>. Even nicer is its <strong>handling of failure</strong>: the model often passes params that don't fit the schema (hallucinations, typos), and a tool may, due to a bug, spit out a non-conforming result—both kinds of "dirty data" are <strong>stopped at the gate into a well-behaved <span class="mono">ToolFailure</span> value</strong>, rather than an exception blasting through the whole agent loop. <strong>The schema is the line of defense between the tool and a chaotic world.</strong></p>
<div class="trace">
  <div class="t-row"><span class="t-num">①decode</span><span class="t-txt">decodeUnknown(input)(call.input): validate the model's params → failure is ToolFailure</span></div>
  <div class="t-row"><span class="t-num">②execute</span><span class="t-txt">config.execute(input, context): actually do the work</span></div>
  <div class="t-row"><span class="t-num">③encode</span><span class="t-txt">encode(output)(result): validate the output shape → failure is ToolFailure</span></div>
  <div class="t-row"><span class="t-num">④two copies</span><span class="t-txt">{ structured: the structured result, content: text/file shown to the model }</span></div>
</div>
<p>That final step <span class="mono">④</span> is worth savoring too: <span class="mono">settle</span> emits not one lump but <strong>two</strong> copies—<span class="mono">structured</span> (structured result, for the system to file) and <span class="mono">content</span> (content for the model to read). Where does <span class="mono">content</span> come from? If the tool provides <span class="mono">toModelOutput</span>, use it to render; otherwise, if the output is a string show it as text, if not give nothing. This is the divide-and-conquer of "<strong>structure for the system, plain language for the model</strong>"—again echoing lesson 22's "prose to communicate, structure to remember."</p>
<div class="cols">
  <div class="col"><h4>structured (for the system)</h4><p>The <strong>structured value</strong> after output-schema encoding, filed verbatim into message history for later programmatic reading, replay, audit.</p></div>
  <div class="col"><h4>content (for the model)</h4><p>The <span class="mono">text</span>/<span class="mono">file</span> list rendered by <span class="mono">toModelOutput</span>—holding only <strong>the side the model should see</strong>. A tool can "record a lot internally, show the model one line."</p></div>
</div>
<p>Why <strong>separate</strong> these two? Because "what the system records" and "what the model should see" are often not the same. E.g. a file-read tool's structured result might hold full byte counts, line numbers, encoding (useful for the system's files), but the model's content needs only the file content itself; or some tools' internal result is huge yet want to tell the model just "done, wrote 42 lines." Decoupling <span class="mono">structured</span> and <span class="mono">content</span> lets a tool <strong>be "detailed inward, concise outward" as needed</strong>—which also foreshadows lesson 42's "bounded output": the side shown to the model can be trimmed.</p>

<h2>The opaque handle: a key tag + a locked mechanism</h2>
<p>One detail so cleverly designed it's easy to miss: <strong>what exactly is</strong> the "tool" that <span class="mono">Tool.make</span> returns? You might assume an object with methods. But look at the source—it returns <span class="mono">Object.freeze({})</span>, <strong>a frozen empty object</strong>! So where's the real behavior (definition/settle/permission) hidden? In a module-level <span class="mono">WeakMap&lt;AnyTool, Runtime&gt;</span>:</p>
<div class="flow">
  <div class="f-node">Tool.make(config)<br><small>returns Object.freeze(&#123;&#125;)</small></div>
  <div class="f-arrow">register →</div>
  <div class="f-node">WeakMap&lt;tool, Runtime&gt;<br><small>the real definition/settle live here</small></div>
  <div class="f-arrow">Tool.settle(tool,…) looks up →</div>
  <div class="f-node">retrieve Runtime, run<br><small>outsiders can't touch the mechanism</small></div>
</div>
<p>Why so roundabout? Because this way, the "tool" value is, to the outside, a pure <strong>"key tag"</strong>—its type <span class="mono">Definition&lt;Input, Output&gt;</span> carries only phantom type info (a <span class="mono">[TypeId]</span> remembering what Input/Output are), <strong>with zero runtime surface for outsiders to fiddle with</strong>. Holding a tool, you <strong>can do nothing but hand it to <span class="mono">Tool.settle</span> / <span class="mono">Tool.definition</span></strong>. This is information hiding at its elegant extreme: the value is a <strong>capability token</strong>, the behavior locked in a private registry. The decorator <span class="mono">withPermission(tool, "permName")</span> follows naturally—it makes a <strong>new key tag</strong> pointing at a "permissioned" Runtime in the WeakMap (lesson 41's permission system plugs in right here). And using a WeakMap has a hidden perk: when a tool is GC'd, its Runtime is <strong>released automatically</strong>, no memory leak.</p>
<p>This "value is a token, behavior lives elsewhere" style looks roundabout but is deeply sensible on reflection. It buys three things: one, <strong>immutability</strong>—whoever holds a tool can't change its behavior (an empty object has no method to override), only use it by the rules; two, <strong>decoration yields a new value</strong>—<span class="mono">withPermission</span> doesn't <strong>mutate</strong> the original tool but <strong>derives</strong> a new key tag pointing at the enhanced Runtime, the original untouched (immutable thinking, lesson 24's refrain); three, <strong>types and runtime fully separated</strong>—the type layer has only the two phantom params <span class="mono">Input</span>/<span class="mono">Output</span>, by which the compiler guarantees the input you pass and output you receive line up, while the runtime grunt work hides in the WeakMap without polluting the types. <strong>A seemingly odd "return an empty object" actually buys "immutable, derivable, type-clean" all in one.</strong></p>
<p>A passing note on the tool-name bar: <span class="mono">validateName</span> requires the name match <span class="mono">/^[A-Za-z][A-Za-z0-9_-]{0,63}$/</span>—letter-led, up to 64 chars, only alphanumerics and <span class="mono">-_</span>. Why care? Because the tool name goes <strong>verbatim into the JSON Schema sent to the model</strong>, and also serves as a key in permissions and the registry; a clean, regular naming constraint blocks a heap of weird-character trouble at the source.</p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>This lesson lays the <strong>foundation</strong> of the whole tool system:</p>
  <ul>
    <li><strong>A tool = filling a <span class="mono">Config</span> form</strong> (<span class="mono">Tool.make</span>): description (read by the model) + input/output (schema) + execute (do work) + optional toModelOutput. Every tool fills this same form, just as lesson 29's every protocol fills the "two-column form."</li>
    <li><strong>The schema wears three hats</strong>: ① <span class="mono">definition</span> turns it into JSON Schema as the model's manual; ② <span class="mono">settle</span> decode-validates incoming params via the input schema; ③ encode-validates the outgoing result via the output schema. Dirty input/output is stopped into a <span class="mono">ToolFailure</span> value, not blasting the agent loop.</li>
    <li><strong>The settle pipeline</strong>: decode input → execute → encode output → emit <span class="mono">{structured, content}</span> two copies (structure for the system, plain language for the model).</li>
    <li><strong>Opaque handle + WeakMap</strong>: <span class="mono">make</span> returns a frozen empty object, the real Runtime locked in <span class="mono">WeakMap&lt;AnyTool,Runtime&gt;</span>; a tool is a "capability token," only usable via settle/definition. <span class="mono">withPermission</span> derives a new handle layering permission.</li>
  </ul>
  <p>With this "shape of a tool," the rest flows: lesson 37 covers the <strong>tool registry</strong> (how these defined tools are collected, materialized per Location into a model-visible list); lessons 38–40 cover <strong>concrete tools</strong> (read/write/edit, glob/grep/bash, webfetch/question/todowrite—all different fillings of this Config form); lesson 41 covers <strong>permissions</strong> (the line <span class="mono">withPermission</span> planted); lesson 42 covers <strong>bounded output</strong> (how execute's large results get trimmed). This lesson's <span class="mono">Tool.make</span> is the origin point of all that follows.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p><span class="mono">settle</span>'s Effect chain strings "validate—execute—revalidate" beautifully (simplified from tool.ts):</p>
  <pre class="code"><span class="cm">// settle: a decode → execute → encode pipeline</span>
Schema.<span class="fn">decodeUnknownEffect</span>(config.input)(call.input).pipe(
  Effect.<span class="fn">mapError</span>(e =&gt; <span class="kw">new</span> ToolFailure({ message: <span class="st">`Invalid tool input: ...`</span> })),
  Effect.<span class="fn">flatMap</span>(input =&gt;
    config.<span class="fn">execute</span>(input, context).pipe(        <span class="cm">// actually do the work</span>
      Effect.<span class="fn">flatMap</span>(output =&gt;
        Schema.<span class="fn">encodeEffect</span>(config.output)(output)   <span class="cm">// validate output shape</span>
          .pipe(Effect.<span class="fn">mapError</span>(e =&gt; <span class="kw">new</span> ToolFailure({ ... }))),
      ),
      Effect.<span class="fn">map</span>(output =&gt; ({ structured: output, content: ... })),
    ),
  ),
)</pre>
  <p>Note the two <span class="mono">mapError</span>s converge both failure kinds into the <strong>same <span class="mono">ToolFailure</span></strong>: invalid input, non-conforming output—to the upper layer, a tool failure is one uniform value, and the agent loop (lesson 17) receiving it can handle gracefully (pass the error back to the model to retry), without distinguishing "did the model pass wrong or the tool compute wrong." One more closing nicety: when a tool gives no <span class="mono">toModelOutput</span> and its output is itself a string, <span class="mono">content</span> defaults to <strong>handing that string straight as text</strong> to the model—zero burden for the simple "output is text" tool. <strong>Complexity for those who need it, simplicity returned to the majority</strong>—this thoughtfulness in defaults is the mark of a good API.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>Tools are the agent's "hands"</strong>: M6 is mouth and brain (talking to models), M7 is hands (read/write files, run commands, search). This lesson asks "how is a tool defined."</li>
    <li><strong><span class="mono">Tool.make(config)</span> is one form</strong> (<span class="mono">core/src/tool/tool.ts</span>): <span class="mono">description</span> (read by model) / <span class="mono">input</span> / <span class="mono">output</span> (schema) / <span class="mono">execute: (input, context) =&gt; Effect&lt;output, ToolFailure&gt;</span> / optional <span class="mono">toModelOutput</span>. Every tool fills this same form (like lesson 29's protocol two-column form).</li>
    <li><strong>The schema wears three hats</strong>: ① <span class="mono">definition(name)</span> → JSON Schema as the model's manual; ② <span class="mono">settle</span> decode-validates input via the input schema; ③ encode-validates output via the output schema. Dirty input/output converge into a <span class="mono">ToolFailure</span> value (no blasting the loop). A recurrence of lesson 22's "codec wears three hats."</li>
    <li><strong><span class="mono">settle</span> pipeline</strong>: decode → execute → encode → <span class="mono">{structured (system files), content (model-readable text/file)}</span>. With no toModelOutput and a string output, content defaults to that string.</li>
    <li><strong>Opaque handle + WeakMap</strong>: <span class="mono">make</span> returns <span class="mono">Object.freeze({})</span>, the real Runtime (definition/settle/permission) hidden in module-level <span class="mono">WeakMap&lt;AnyTool, Runtime&gt;</span>. A tool is a "capability token," only usable via <span class="mono">Tool.settle/definition</span>; <span class="mono">withPermission</span> derives a new handle layering permission (lesson 41 plug-in). <span class="mono">Context = {sessionID, agent, assistantMessageID, toolCallID}</span>.</li>
  </ul>
</div>
""",
}
LESSON_37 = {
    "zh": r"""
<p class="lead">上一课我们学会了「<strong>定义</strong>一个工具」（<span class="mono">Tool.make</span> 那张表）。可定义出来的工具，怎么<strong>被收集起来、变成模型真正能看到、能调用的一份清单</strong>？这就是<strong>工具注册表（ToolRegistry）</strong>的活儿。它是一座桥：一头连着「<strong>一堆零散定义好的工具</strong>」（L36），一头连着「<strong>这一轮对话，模型该看到哪些工具、点了能派给谁干</strong>」（第 17 课 agent 循环要用的东西）。注册表把这座桥拆成两个动作：<strong>register（登记）</strong>——工具来报到；<strong>materialize（物化）</strong>——按当下情形，现场印出一份「<strong>今日菜单</strong>」交给模型。</p>
<p>读这一课，你会强烈地想起第 23 课「System Context 注册表」——它俩几乎是<strong>同一种智慧的两次现身</strong>：都用 <strong>Scope（作用域）绑定</strong>来管理「谁在、谁走」，作用域一关、登记自动撤销，绝不留幽灵。但工具注册表多了两手更精巧的设计：<strong>「同名工具叠成一摞、最新的盖在最上面」</strong>（支持覆盖与自动恢复），以及<strong>「物化时按权限筛、还盖个防伪章」</strong>（被禁的工具压根不进菜单、防止「点了张过期的菜」）。把这两手看懂，你就懂了 opencode 怎么在「插件随时来去、权限随时变」的动态世界里，仍给模型递上一份<strong>干净、当下、可信</strong>的工具清单。</p>

<div class="card analogy">
  <div class="tag">🍽️ 生活类比</div>
  把注册表想象成一家餐厅的<strong>前台花名册 + 今日菜单机</strong>。厨师（工具）上岗要<strong>打卡报到</strong>（register）——但打卡是<strong>「绑定班次」</strong>的：你这一班在，名字就在花名册上；班次一结束，<strong>自动消失</strong>，不用谁记得去划掉。要是两个厨师<strong>重名</strong>（比如一个「招牌版」盖住「基础版」），花名册把他们<strong>叠成一摞</strong>，永远<strong>最新打卡的那位顶班</strong>；他下班了，下面那位<strong>自动顶上来</strong>。每当一桌客人（模型）落座，前台就现场<strong>印一份「今日菜单」</strong>（materialize）：它扫一遍当前花名册，把<strong>今天被禁的菜划掉</strong>（权限过滤），印成两样东西——一份<strong>给客人看的菜单</strong>（definitions），一个<strong>派单台</strong>（settle，客人点了菜就派给对应厨师）。而且菜单上每道菜都<strong>盖了今日防伪章</strong>：万一客人拿着旧菜单来点、而那厨师早已下班换了人，派单台一看章对不上，当即拦下——「<strong>这是张过期的菜</strong>」。
</div>

<h2>register：打卡报到，绑定作用域</h2>
<p>先看 <span class="mono">register(tools)</span>——把一批工具（一个 <span class="mono">{名字: 工具}</span> 的字典）登记进来。它的实现处处是第 23 课的影子，但更见功力：</p>
<div class="flow">
  <div class="f-node">register(tools)</div>
  <div class="f-arrow">①校验 →</div>
  <div class="f-node">validateName<br><small>每个名字合规</small></div>
  <div class="f-arrow">②入摞 →</div>
  <div class="f-node">local[name].push(&#123;token, 工具&#125;)<br><small>同名叠成一摞</small></div>
  <div class="f-arrow">③登记善后 →</div>
  <div class="f-node">addFinalizer<br><small>作用域关→按 token 撤销</small></div>
</div>
<p>三步看似平常，细节全是讲究。其一，<strong>每个名字先过 <span class="mono">validateName</span></strong>（第 36 课那个 <span class="mono">/^[A-Za-z]...{0,63}$/</span> 的规矩）——不合规的名字进不来，从源头保证菜单干净。其二，<span class="mono">local</span> 不是 <span class="mono">Map&lt;名字, 工具&gt;</span>，而是 <span class="mono">Map&lt;名字, 工具数组&gt;</span>——<strong>同一个名字底下是一摞登记</strong>。为什么要叠成摞？因为这样就支持<strong>覆盖</strong>：一个插件想用自己的 <span class="mono">read</span> 盖掉内置的 <span class="mono">read</span>，只需再登记一个同名工具压在摞顶；取用时永远取 <span class="mono">.at(-1)</span>（摞顶、最新那个）。其三，也是最关键的——<strong><span class="mono">Effect.addFinalizer</span> 绑定作用域</strong>：登记时生成一个唯一 <span class="mono">token = {}</span>，作用域关闭时，finalizer 按这个 token <strong>精准地把自己那次登记从摞里抽走</strong>。抽走后若摞空了就删掉这个名字，若摞里还有（被它盖住的那个）就<strong>自动浮上来顶班</strong>。</p>
<p>这套「叠摞 + 按 token 撤销」合起来，给出一个极优雅的性质：<strong>工具的「存在」与它的作用域同生共死，且覆盖可自动恢复</strong>。插件在它的 scope 里登记一个 <span class="mono">read</span> 覆盖内置版，插件卸载（scope 关）的一刻，覆盖<strong>自动消失</strong>、内置版<strong>自动复位</strong>——没有任何手动「记得去注销」的负担，也不可能出现「插件走了、它的工具还赖着」的幽灵。这正是第 23 课 <span class="mono">acquireRelease</span> 思想的延伸：<strong>把「清理」焊死在「获取」上，让生命周期自己管自己。</strong></p>

<h2>materialize：现印一份「今日菜单」</h2>
<p>当一轮对话要开始，agent 循环需要「<strong>这一轮模型能用哪些工具</strong>」。这就是 <span class="mono">materialize(permissions)</span> 干的事——它<strong>不是</strong>返回那个随时在变的 <span class="mono">local</span>，而是<strong>在此刻拍一张快照</strong>，加工成一份当下可用的清单：</p>
<div class="flow">
  <div class="f-node">applications<br><small>应用级常驻工具</small></div>
  <div class="f-arrow">叠上 local 摞顶 →</div>
  <div class="f-node">当前全量工具<br><small>各名字取最新</small></div>
  <div class="f-arrow">按权限筛 →</div>
  <div class="f-node">删掉 whollyDisabled<br><small>被禁的不进菜单</small></div>
  <div class="f-arrow">产出 →</div>
  <div class="f-node">&#123;definitions, settle&#125;</div>
</div>
<p>三步走：先把<strong>应用级常驻工具</strong>（<span class="mono">applications</span>）和 <span class="mono">local</span> 各名字的<strong>摞顶</strong>合并，得到「此刻全部工具」；再用传入的<strong>权限规则集</strong>过一遍，把 <span class="mono">whollyDisabled</span>（被彻底禁用）的工具<strong>从清单里删掉</strong>；最后产出两样东西：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">definitions</div><div class="c-txt">每个存活工具的 ToolDefinition（JSON Schema + description）——这就是发给模型的「菜单」</div></div>
  <div class="cell"><div class="c-tag">settle</div><div class="c-txt">一个派单函数：模型点了某工具，按名字找到它、派去执行</div></div>
</div>
<p>这里有个容易滑过、却很重要的设计点：<strong>权限过滤发生在「菜单」这一层</strong>。一个被策略彻底禁掉的工具，<strong>根本不会出现在发给模型的 definitions 里</strong>——模型连「有这么个工具」都不知道，自然不会去点。这比「让模型点了再拒绝」干净得多：<strong>最好的拒绝，是让它压根不知道有这个选项</strong>（第 41 课权限系统会深入这条线）。另一面，<span class="mono">materialize</span> 产出的是一份<strong>快照</strong>——它把「此刻有哪些工具、各自的身份」定格下来，与还在随作用域变动的 <span class="mono">local</span> <strong>解耦</strong>。<strong>register 管「有哪些工具」（可变、带作用域），materialize 管「这一轮看见哪些」（不可变快照）</strong>，两者分得清清楚楚：</p>
<div class="cols">
  <div class="col"><h4>register · 注册表（可变）</h4><p>随插件、Location 作用域<strong>不断增删</strong>的「活」状态；同名叠摞、最新顶班；问的是「<strong>当前世界上有哪些工具</strong>」。</p></div>
  <div class="col"><h4>materialize · 物化（不可变）</h4><p>某一刻拍下的<strong>快照</strong> + 权限过滤 + 身份定格；问的是「<strong>这一轮，模型该看见、能调用哪些</strong>」。一旦印出，本轮不再变。</p></div>
</div>

<h2>派单与防伪：settle 的「过期菜」拦截</h2>
<p>菜单印好了，模型点了一道菜（发起一次工具调用），<span class="mono">settle</span> 就负责<strong>派单 + 执行 + 善后</strong>。这条链把前面几课的伏笔都收了起来：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">①找人</span><span class="t-txt">按 call.name 找到摞顶的登记（或 applications 里的）</span></div>
  <div class="t-row"><span class="t-num">②验章</span><span class="t-txt">物化时记下的 identity 与当前是否一致？不一致→「Stale tool call」</span></div>
  <div class="t-row"><span class="t-num">③执行</span><span class="t-txt">settle(tool, call, context)：第 36 课那条 decode→execute→encode</span></div>
  <div class="t-row"><span class="t-num">④收错</span><span class="t-txt">catch ToolFailure → 变成 &#123;type:error, value:消息&#125; 回传模型</span></div>
  <div class="t-row"><span class="t-num">⑤截断</span><span class="t-txt">resources.bound(...)：大输出截断/外溢（第 42 课）</span></div>
</div>
<p>第 <span class="mono">②</span> 步「验章」最见匠心。从「模型看到菜单」到「模型点这道菜」之间，是有<strong>时间差</strong>的——这期间，那个工具的登记完全可能变了（它的作用域关了、或被重新登记成了别的东西）。怎么保证模型点的，<strong>正是它当初在菜单上看到的那一个</strong>？靠的是每次登记都带的一个唯一 <span class="mono">identity = {}</span> 对象：<span class="mono">materialize</span> 把它一并记进菜单，<span class="mono">settle</span> 执行前核对「<strong>当前这个名字下的 identity，还是不是菜单上那个</strong>」。对不上，就果断报「<span class="mono">Stale tool call</span>（过期的工具调用）」，绝不<strong>张冠李戴</strong>地把调用派给一个名字相同、身份已换的工具。这是个微妙却重要的正确性保证——在一个工具能动态来去的系统里，它守住了「<strong>所见即所调</strong>」。设想没有这道验章会怎样：模型读到菜单上的 <span class="mono">read</span>（内置版）、正准备调用，恰在此刻一个插件登记了自己的 <span class="mono">read</span> 压上摞顶；若不验身份，模型这次调用就会<strong>悄悄被派给插件那个它从没见过的工具</strong>——行为对不上模型的预期，且毫无察觉。验章把这种「名字相同、人已换」的错配，变成一个<strong>明确、可观测的错误</strong>，而不是一桩无声的灵异事件。</p>
<p>第 <span class="mono">④⑤</span> 两步则是与后面课程的接口：<strong>④ 把工具的 <span class="mono">ToolFailure</span> 收成一个「错误结果值」</strong>回传模型（让模型自己看错、重试），而不是让异常炸穿循环——上层（第 17 课 agent 循环）拿到的永远是个规规矩矩的结果。<strong>⑤ 把执行结果交给 <span class="mono">ToolOutputStore</span> 做「有界化」</strong>：一个 grep 可能吐出几万行，直接塞回对话会撑爆上下文，于是这里截断、把全文外溢到一个托管文件（第 42 课的主角）。注册表，就是这两条横切关注点（权限、有界输出）<strong>挂载到工具执行流上的那个点</strong>。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <p>工具注册表是「定义好的工具」与「agent 循环用的工具」之间的<strong>桥</strong>：</p>
  <ul>
    <li><strong>register（登记，可变·带作用域）</strong>：<span class="mono">validateName</span> → 同名<strong>叠成一摞</strong>（最新顶班）→ <span class="mono">addFinalizer</span> 按 token 撤销。作用域一关、登记自动消失、被覆盖者自动复位。是第 23 课 <span class="mono">acquireRelease</span> 思想的延伸。</li>
    <li><strong>materialize（物化，不可变·快照）</strong>：applications + local 摞顶 → 按权限删掉 <span class="mono">whollyDisabled</span> → 产出 <span class="mono">{definitions（给模型的菜单）, settle（派单台）}</span>。<strong>权限过滤在菜单层</strong>：被禁的工具模型根本看不见。</li>
    <li><strong>settle（派单·防伪·善后）</strong>：按名找人 → <strong>验 identity 防「过期菜」</strong>（Stale tool call）→ 第 36 课的 decode/execute/encode → catch <span class="mono">ToolFailure</span> 成错误值 → <span class="mono">ToolOutputStore.bound</span> 截断大输出。</li>
    <li><strong>builtins.locationLayer</strong>：用 <span class="mono">Layer.mergeAll</span> 把内置工具（read/write/edit/bash/glob/grep/question/todowrite/webfetch/websearch/skill/apply-patch）的 layer 组合起来，各自 Location-作用域地自我登记。</li>
  </ul>
  <p>register/materialize 这条线，把「哪些工具存在」和「这一轮看见哪些」干净地切开，让权限（第 41 课）与有界输出（第 42 课）有了明确的挂载点。那这些内置工具又是从哪「报到」的？答案是 <span class="mono">builtins.ts</span> 里的 <span class="mono">locationLayer</span>——它用 <span class="mono">Layer.mergeAll</span> 把所有出厂内置工具的 layer 合成一个，每个工具的 layer 在自己被装配时<strong>自我登记</strong>进注册表：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">文件类</div><div class="c-txt">read / write / edit / apply-patch（第 38 课）</div></div>
  <div class="cell"><div class="c-tag">搜索执行</div><div class="c-txt">glob / grep / bash（第 39 课）</div></div>
  <div class="cell"><div class="c-tag">其他</div><div class="c-txt">webfetch / websearch / question / todowrite（第 40 课）</div></div>
  <div class="cell"><div class="c-tag">Skills</div><div class="c-txt">skill（第 43 课，经权限化的特殊工具）</div></div>
</div>
<p>注意 <span class="mono">locationLayer</span> 这个名字里的 <strong>Location</strong>——这些工具是<strong>按 Location（工作区/文件系统作用域）登记的</strong>。这正好和前面「register 绑定作用域」对上了：每个 Location 有自己的一套工具登记，Location 的生命周期一到头，这套工具也随之退场。<strong>「工具随 Location 来去」，是 register 作用域机制在内置工具上的直接兑现。</strong></p>
<p>下一课起（第 38~40 课）我们就钻进<strong>一个个具体工具</strong>：read/write/edit/apply-patch（文件）、glob/grep/bash（搜索与执行）、webfetch/websearch/question/todowrite（其他）——它们全是第 36 课那张 <span class="mono">Config</span> 表的不同填法，而它们能被模型看见、调用，靠的全是这一课的注册表。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p><span class="mono">register</span> 的「叠摞 + 按 token 撤销」是这套优雅的核心（简化自 registry.ts）：</p>
  <pre class="code"><span class="cm">// 登记：同名压栈；作用域关闭时按 token 精准撤走</span>
<span class="kw">const</span> token = {}
<span class="kw">for</span> (<span class="kw">const</span> [name, tool] <span class="kw">of</span> entries)
  local.set(name, [...(local.get(name) ?? []), { token, registration: { identity: {}, tool } }])

Effect.<span class="fn">addFinalizer</span>(() =&gt; {
  <span class="kw">for</span> (<span class="kw">const</span> [name] <span class="kw">of</span> entries) {
    <span class="kw">const</span> rest = local.get(name)?.filter(r =&gt; r.token !== token) ?? []
    rest.length &gt; 0 ? local.set(name, rest) : local.delete(name)  <span class="cm">// 空了就删，剩的自动顶上</span>
  }
})</pre>
  <p>注意两个不同的空对象：<span class="mono">token</span> 标识「<strong>哪一次 register 调用</strong>」（用于撤销时精准定位本次登记的那些条目），<span class="mono">identity</span> 标识「<strong>哪一个具体登记</strong>」（用于 settle 时验防伪章）。用空对象 <span class="mono">{}</span> 做唯一标识是个老练的小技巧——<strong>对象的引用天生唯一</strong>，<span class="mono">{} !== {}</span>，不用生成 UUID、不会撞，比较还快（一个引用相等判断）。整段还裹在 <span class="mono">Effect.uninterruptible</span> 里：登记「压栈」和「装 finalizer」必须<strong>原子地一起完成</strong>，绝不能压了栈却因中断没装上撤销钩子——否则就漏了一个永远撤不掉的幽灵登记。<strong>连「注册」这种小事，都被 Effect 的中断语义认真对待。</strong></p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>注册表是「定义好的工具」与「agent 循环用的工具」之间的桥</strong>（<span class="mono">core/src/tool/registry.ts</span>），两个动作：register（登记）+ materialize（物化）。</li>
    <li><strong>register</strong>：<span class="mono">validateName</span> 校验 → <span class="mono">local: Map&lt;名字, 登记数组&gt;</span> <strong>同名叠成一摞、<span class="mono">.at(-1)</span> 最新顶班</strong> → <span class="mono">Effect.addFinalizer</span> 按唯一 <span class="mono">token</span> 撤销。作用域关→登记自动消失、被覆盖者自动复位（第 23 课 <span class="mono">acquireRelease</span> 延伸）。压栈+装 finalizer 裹在 <span class="mono">uninterruptible</span> 里原子完成。</li>
    <li><strong>materialize(permissions)</strong>：applications + local 摞顶合并 → 删掉 <span class="mono">whollyDisabled</span> 的工具 → 产出 <span class="mono">{definitions, settle}</span>。<strong>权限过滤在菜单层</strong>——被禁工具不进 definitions，模型根本看不见（优于「点了再拒」）。是<strong>不可变快照</strong>，与可变的 local 解耦。</li>
    <li><strong>settle 派单</strong>：按 call.name 找登记 → <strong>验 <span class="mono">identity</span> 防「Stale tool call」</strong>（保证「所见即所调」）→ 第 36 课 decode/execute/encode → catch <span class="mono">ToolFailure</span> 成错误值回传 → <span class="mono">resources.bound</span> 截断大输出（第 42 课）。</li>
    <li><strong>builtins.locationLayer</strong>：<span class="mono">Layer.mergeAll</span> 组合内置工具的 layer，各自 Location-作用域自我登记。<span class="mono">token</span>=标识本次 register；<span class="mono">identity</span>=标识单个登记（验防伪）；空对象 <span class="mono">{}</span> 作天然唯一标识。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Last lesson we learned to <strong>define</strong> a tool (that <span class="mono">Tool.make</span> form). But how do defined tools get <strong>collected, turned into a list the model can actually see and call</strong>? That's the <strong>tool registry (ToolRegistry)</strong>'s job. It's a bridge: one end to "<strong>a pile of scattered defined tools</strong>" (L36), the other to "<strong>which tools this conversation turn should show the model, and who an order gets dispatched to</strong>" (what lesson 17's agent loop uses). The registry splits this bridge into two actions: <strong>register</strong>—tools check in; <strong>materialize</strong>—print, on the spot per current conditions, a "<strong>today's menu</strong>" for the model.</p>
<p>Reading this lesson, you'll strongly recall lesson 23's "System Context Registry"—they're almost <strong>the same wisdom appearing twice</strong>: both use <strong>Scope binding</strong> to manage "who's in, who's out," the scope closing auto-revokes the registration, never leaving ghosts. But the tool registry adds two more refined designs: <strong>"same-named tools stack up, the latest on top"</strong> (supporting override and auto-restore), and <strong>"at materialize time, filter by permission and stamp an anti-forgery seal"</strong> (banned tools don't even enter the menu; preventing "ordering a stale dish"). Grasp these two and you understand how opencode, in a dynamic world where "plugins come and go anytime, permissions change anytime," still hands the model a <strong>clean, current, trustworthy</strong> tool list.</p>

<div class="card analogy">
  <div class="tag">🍽️ Analogy</div>
  Picture the registry as a restaurant's <strong>front-desk roster + today's-menu machine</strong>. A cook (tool) coming on duty must <strong>clock in</strong> (register)—but clocking in is <strong>"shift-bound"</strong>: while your shift is on, your name's on the roster; the shift ends and it <strong>vanishes automatically</strong>, no one needing to remember to cross it off. If two cooks <strong>share a name</strong> (a "signature edition" covering the "basic edition"), the roster <strong>stacks them</strong>, and the <strong>latest clock-in always works the shift</strong>; when they clock out, the one beneath <strong>auto-resurfaces</strong>. Whenever a table of guests (the model) is seated, the front desk prints "today's menu" on the spot (materialize): it scans the current roster, <strong>crosses off today's banned dishes</strong> (permission filter), and prints two things—a <strong>menu for the guests</strong> (definitions) and a <strong>dispatch desk</strong> (settle, an order routed to the right cook). And every dish on the menu is <strong>stamped with today's anti-forgery seal</strong>: should a guest order off an old menu while that cook has long clocked out and been replaced, the dispatch desk sees the seal mismatch and stops it cold—"<strong>this is a stale dish.</strong>"
</div>

<h2>register: clock in, bound to scope</h2>
<p>First <span class="mono">register(tools)</span>—register a batch of tools (a <span class="mono">{name: tool}</span> dict). Its implementation is full of lesson 23's shadow, but with more finesse:</p>
<div class="flow">
  <div class="f-node">register(tools)</div>
  <div class="f-arrow">①validate →</div>
  <div class="f-node">validateName<br><small>each name conforms</small></div>
  <div class="f-arrow">②stack →</div>
  <div class="f-node">local[name].push(&#123;token, tool&#125;)<br><small>same name stacks up</small></div>
  <div class="f-arrow">③cleanup →</div>
  <div class="f-node">addFinalizer<br><small>scope closes→revoke by token</small></div>
</div>
<p>Three plain-looking steps, all detail. One, <strong>each name first passes <span class="mono">validateName</span></strong> (lesson 36's <span class="mono">/^[A-Za-z]...{0,63}$/</span> rule)—non-conforming names don't get in, keeping the menu clean at the source. Two, <span class="mono">local</span> isn't <span class="mono">Map&lt;name, tool&gt;</span> but <span class="mono">Map&lt;name, tool array&gt;</span>—<strong>under one name is a stack of registrations</strong>. Why a stack? Because it supports <strong>override</strong>: a plugin wanting to cover the built-in <span class="mono">read</span> with its own just registers another same-named tool pressed on top; retrieval always takes <span class="mono">.at(-1)</span> (top of stack, the latest). Three, and most crucial—<strong><span class="mono">Effect.addFinalizer</span> binds the scope</strong>: registration generates a unique <span class="mono">token = {}</span>, and when the scope closes, the finalizer <strong>precisely pulls its own registration out of the stack</strong> by that token. After pulling, if the stack is empty delete the name, if there's still (the one it covered) it <strong>auto-resurfaces to work the shift</strong>.</p>
<p>This "stack + revoke-by-token" combo yields an elegant property: <strong>a tool's "existence" lives and dies with its scope, and overrides auto-restore</strong>. A plugin registers a <span class="mono">read</span> override in its scope; the moment the plugin unloads (scope closes), the override <strong>vanishes automatically</strong> and the built-in <strong>auto-restores</strong>—no manual "remember to unregister" burden, and no possibility of "plugin's gone but its tool lingers" ghosts. This is exactly the extension of lesson 23's <span class="mono">acquireRelease</span> thinking: <strong>weld "cleanup" onto "acquisition," letting the lifecycle manage itself.</strong></p>

<h2>materialize: print a "today's menu" on the spot</h2>
<p>When a conversation turn is about to begin, the agent loop needs "<strong>which tools the model can use this turn</strong>." That's what <span class="mono">materialize(permissions)</span> does—it <strong>doesn't</strong> return the ever-changing <span class="mono">local</span>, but <strong>takes a snapshot right now</strong>, processed into a currently-usable list:</p>
<div class="flow">
  <div class="f-node">applications<br><small>app-level resident tools</small></div>
  <div class="f-arrow">overlay local tops →</div>
  <div class="f-node">all current tools<br><small>each name's latest</small></div>
  <div class="f-arrow">filter by permission →</div>
  <div class="f-node">remove whollyDisabled<br><small>banned not in menu</small></div>
  <div class="f-arrow">produce →</div>
  <div class="f-node">&#123;definitions, settle&#125;</div>
</div>
<p>Three steps: first merge <strong>app-level resident tools</strong> (<span class="mono">applications</span>) with each name's <strong>stack top</strong> in <span class="mono">local</span>, getting "all tools right now"; then run the passed <strong>permission ruleset</strong> over them, <strong>removing</strong> <span class="mono">whollyDisabled</span> (fully-disabled) tools from the list; finally produce two things:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">definitions</div><div class="c-txt">each surviving tool's ToolDefinition (JSON Schema + description)—this is the "menu" sent to the model</div></div>
  <div class="cell"><div class="c-tag">settle</div><div class="c-txt">a dispatch function: the model orders a tool, find it by name, dispatch to execute</div></div>
</div>
<p>Here's an easy-to-skip but important design point: <strong>permission filtering happens at the "menu" layer</strong>. A tool fully banned by policy <strong>doesn't even appear in the definitions sent to the model</strong>—the model doesn't even know "such a tool exists," so naturally won't order it. This is far cleaner than "let the model order then refuse": <strong>the best refusal is to not let it know the option exists</strong> (lesson 41's permission system goes deep on this). On the other side, <span class="mono">materialize</span> produces a <strong>snapshot</strong>—it freezes "which tools exist right now, and each one's identity," <strong>decoupled</strong> from the still-scope-changing <span class="mono">local</span>. <strong>register owns "which tools exist" (mutable, scoped), materialize owns "which this turn sees" (immutable snapshot)</strong>, cleanly separated:</p>
<div class="cols">
  <div class="col"><h4>register · registry (mutable)</h4><p>The "live" state <strong>constantly added/removed</strong> with plugins and Location scopes; same-name stacking, latest on shift; it asks "<strong>which tools exist in the world right now</strong>."</p></div>
  <div class="col"><h4>materialize · materialization (immutable)</h4><p>A <strong>snapshot</strong> taken at one moment + permission filter + identity freeze; it asks "<strong>this turn, which the model should see and can call</strong>." Once printed, unchanging this turn.</p></div>
</div>

<h2>Dispatch & anti-forgery: settle's "stale dish" interception</h2>
<p>The menu's printed, the model orders a dish (initiates a tool call), and <span class="mono">settle</span> handles <strong>dispatch + execution + cleanup</strong>. This chain collects all the prior lessons' planted seeds:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">①find</span><span class="t-txt">by call.name find the stack-top registration (or in applications)</span></div>
  <div class="t-row"><span class="t-num">②verify seal</span><span class="t-txt">does the identity recorded at materialize match the current? mismatch→"Stale tool call"</span></div>
  <div class="t-row"><span class="t-num">③execute</span><span class="t-txt">settle(tool, call, context): lesson 36's decode→execute→encode</span></div>
  <div class="t-row"><span class="t-num">④catch error</span><span class="t-txt">catch ToolFailure → becomes &#123;type:error, value:message&#125; back to the model</span></div>
  <div class="t-row"><span class="t-num">⑤bound</span><span class="t-txt">resources.bound(...): large output truncated/spilled (lesson 42)</span></div>
</div>
<p>Step <span class="mono">②</span> "verify seal" shows the most craft. Between "the model saw the menu" and "the model orders this dish," there's a <strong>time gap</strong>—during which that tool's registration may well have changed (its scope closed, or it was re-registered into something else). How to guarantee what the model orders is <strong>exactly the one it saw on the menu</strong>? Via a unique <span class="mono">identity = {}</span> object each registration carries: <span class="mono">materialize</span> records it into the menu, and <span class="mono">settle</span> before executing checks "<strong>is the identity under this name still the one on the menu</strong>." Mismatch → decisively report "<span class="mono">Stale tool call</span>," never <strong>misattributing</strong> the call to a same-named tool whose identity has changed. This is a subtle but important correctness guarantee—in a system where tools come and go dynamically, it preserves "<strong>what you see is what you call</strong>." Imagine without this seal check: the model reads the menu's <span class="mono">read</span> (built-in), about to call it, and right then a plugin registers its own <span class="mono">read</span> pressed on top; without identity verification, this call would <strong>silently get dispatched to the plugin's tool the model never saw</strong>—behavior mismatching the model's expectation, with no awareness. The seal turns this "same name, different person" mismatch into an <strong>explicit, observable error</strong>, not a silent uncanny event.</p>
<p>Steps <span class="mono">④⑤</span> are the interfaces to later lessons: <strong>④ collects the tool's <span class="mono">ToolFailure</span> into an "error result value"</strong> back to the model (let it see the error and retry), rather than an exception blasting the loop—the upper layer (lesson 17's agent loop) always receives a well-behaved result. <strong>⑤ hands the execution result to <span class="mono">ToolOutputStore</span> for "bounding"</strong>: a grep might spit tens of thousands of lines, and stuffing it straight back into the conversation would blow the context, so here it's truncated, with the full text spilled to a managed file (lesson 42's star). The registry is the point where these two cross-cutting concerns (permissions, bounded output) <strong>mount onto the tool-execution flow</strong>.</p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>The tool registry is the <strong>bridge</strong> between "defined tools" and "tools the agent loop uses":</p>
  <ul>
    <li><strong>register (mutable·scoped)</strong>: <span class="mono">validateName</span> → same-name <strong>stacks up</strong> (latest on shift) → <span class="mono">addFinalizer</span> revokes by token. Scope closes→registration auto-vanishes, the covered one auto-restores. An extension of lesson 23's <span class="mono">acquireRelease</span> thinking.</li>
    <li><strong>materialize (immutable·snapshot)</strong>: applications + local stack-tops → remove <span class="mono">whollyDisabled</span> by permission → produce <span class="mono">{definitions (menu for the model), settle (dispatch desk)}</span>. <strong>Permission filtering at the menu layer</strong>: a banned tool is invisible to the model.</li>
    <li><strong>settle (dispatch·anti-forgery·cleanup)</strong>: find by name → <strong>verify identity against "stale dish"</strong> (Stale tool call) → lesson 36's decode/execute/encode → catch <span class="mono">ToolFailure</span> into an error value → <span class="mono">ToolOutputStore.bound</span> truncates large output.</li>
    <li><strong>builtins.locationLayer</strong>: uses <span class="mono">Layer.mergeAll</span> to compose the built-in tools' (read/write/edit/bash/glob/grep/question/todowrite/webfetch/websearch/skill/apply-patch) layers, each self-registering Location-scoped.</li>
  </ul>
  <p>The register/materialize line cleanly cuts "which tools exist" from "which this turn sees," giving permissions (lesson 41) and bounded output (lesson 42) clear mount points. So where do these built-in tools "check in"? The answer is <span class="mono">locationLayer</span> in <span class="mono">builtins.ts</span>—it uses <span class="mono">Layer.mergeAll</span> to merge all shipped built-in tools' layers into one, each tool's layer <strong>self-registering</strong> into the registry as it's assembled:</p>
  <div class="cellgroup">
    <div class="cell"><div class="c-tag">file</div><div class="c-txt">read / write / edit / apply-patch (lesson 38)</div></div>
    <div class="cell"><div class="c-tag">search & exec</div><div class="c-txt">glob / grep / bash (lesson 39)</div></div>
    <div class="cell"><div class="c-tag">other</div><div class="c-txt">webfetch / websearch / question / todowrite (lesson 40)</div></div>
    <div class="cell"><div class="c-tag">Skills</div><div class="c-txt">skill (lesson 43, a permissioned special tool)</div></div>
  </div>
  <p>Note the <strong>Location</strong> in <span class="mono">locationLayer</span>'s name—these tools are <strong>registered per Location (workspace/filesystem scope)</strong>. This lines up with "register binds to scope": each Location has its own set of tool registrations, and when the Location's lifecycle ends, this tool set exits with it. <strong>"Tools come and go with the Location" is register's scope mechanism cashed out directly on the built-in tools.</strong> From the next lesson (38–40) we dive into <strong>individual concrete tools</strong>—all different fillings of lesson 36's <span class="mono">Config</span> form, and their being seen and called by the model relies entirely on this lesson's registry.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p><span class="mono">register</span>'s "stack + revoke-by-token" is the core of this elegance (simplified from registry.ts):</p>
  <pre class="code"><span class="cm">// register: same-name push; on scope close, precisely revoke by token</span>
<span class="kw">const</span> token = {}
<span class="kw">for</span> (<span class="kw">const</span> [name, tool] <span class="kw">of</span> entries)
  local.set(name, [...(local.get(name) ?? []), { token, registration: { identity: {}, tool } }])

Effect.<span class="fn">addFinalizer</span>(() =&gt; {
  <span class="kw">for</span> (<span class="kw">const</span> [name] <span class="kw">of</span> entries) {
    <span class="kw">const</span> rest = local.get(name)?.filter(r =&gt; r.token !== token) ?? []
    rest.length &gt; 0 ? local.set(name, rest) : local.delete(name)  <span class="cm">// empty→delete, rest auto-surfaces</span>
  }
})</pre>
  <p>Note two different empty objects: <span class="mono">token</span> identifies "<strong>which register call</strong>" (to precisely locate this call's entries on revoke), <span class="mono">identity</span> identifies "<strong>which specific registration</strong>" (to verify the anti-forgery seal at settle). Using an empty object <span class="mono">{}</span> as a unique identifier is a seasoned little trick—<strong>an object's reference is inherently unique</strong>, <span class="mono">{} !== {}</span>, no UUID generation needed, no collisions, and comparison is fast (one reference-equality check). The whole block is wrapped in <span class="mono">Effect.uninterruptible</span>: "pushing the stack" and "installing the finalizer" must <strong>complete atomically together</strong>, never pushing the stack but, due to an interrupt, failing to install the revoke hook—else you'd leak a ghost registration that can never be revoked. <strong>Even something as small as "registration" is taken seriously by Effect's interruption semantics.</strong></p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>The registry bridges "defined tools" and "tools the agent loop uses"</strong> (<span class="mono">core/src/tool/registry.ts</span>), two actions: register + materialize.</li>
    <li><strong>register</strong>: <span class="mono">validateName</span> validates → <span class="mono">local: Map&lt;name, registration array&gt;</span> <strong>same-name stacks, <span class="mono">.at(-1)</span> latest on shift</strong> → <span class="mono">Effect.addFinalizer</span> revokes by unique <span class="mono">token</span>. Scope closes→registration auto-vanishes, the covered one auto-restores (extension of lesson 23's <span class="mono">acquireRelease</span>). Push+finalizer wrapped in <span class="mono">uninterruptible</span> for atomicity.</li>
    <li><strong>materialize(permissions)</strong>: applications + local stack-tops merged → remove <span class="mono">whollyDisabled</span> tools → produce <span class="mono">{definitions, settle}</span>. <strong>Permission filtering at the menu layer</strong>—banned tools don't enter definitions, invisible to the model (better than "order then refuse"). It's an <strong>immutable snapshot</strong>, decoupled from the mutable local.</li>
    <li><strong>settle dispatch</strong>: find registration by call.name → <strong>verify <span class="mono">identity</span> against "Stale tool call"</strong> (guaranteeing "what you see is what you call") → lesson 36's decode/execute/encode → catch <span class="mono">ToolFailure</span> into an error value back → <span class="mono">resources.bound</span> truncates large output (lesson 42).</li>
    <li><strong>builtins.locationLayer</strong>: <span class="mono">Layer.mergeAll</span> composes built-in tools' layers, each self-registering Location-scoped. <span class="mono">token</span>=identifies this register call; <span class="mono">identity</span>=identifies a single registration (seal check); empty object <span class="mono">{}</span> as a natural unique identifier.</li>
  </ul>
</div>
""",
}
LESSON_38 = {
    "zh": r"""
<p class="lead">前两课我们搭好了工具系统的<strong>骨架</strong>：一个工具怎么定义（第 36 课 <span class="mono">Tool.make</span>）、怎么被收集成模型可见的清单（第 37 课注册表）。从这一课起，我们钻进<strong>一个个真实的工具</strong>，看「骨架如何长出血肉」。先看最日常、也最考验功力的一族——<strong>文件工具</strong>：<span class="mono">read</span>（读）、<span class="mono">write</span>（整写）、<span class="mono">edit</span>（精改）、<span class="mono">apply_patch</span>（批量打补丁）。一个写代码的 agent，绝大多数动作落地成的，就是这四把「手」对文件的读与改。</p>
<p>这一课有两层收获。其一，<strong>印证第 36 课</strong>：你会亲眼看到这四个工具<strong>全是同一张 <span class="mono">Config</span> 表的不同填法</strong>——各自声明 input/output schema + execute，套上 <span class="mono">withPermission</span>，仅此而已。其二，也是重头：我们会把 <span class="mono">edit</span> 工具的执行<strong>一步步摊开</strong>（spec 点名的 worked-example），看一个「把这段文字改成那段」的小操作，背后藏着多少<strong>生产级的较真</strong>——精确匹配、歧义拒绝、行尾归一、乐观并发写。读完你会明白：让 AI 安全地改你的代码，<strong>难的从来不是「替换字符串」，而是那一圈「不猜、不错、不覆盖别人」的护栏</strong>。</p>

<div class="card analogy">
  <div class="tag">✍️ 生活类比</div>
  把这四个文件工具想象成一位文字匠人的<strong>四件工具</strong>。<strong>read</strong> 是<strong>放大镜</strong>——只看不改，还能翻页（offset/limit）地看长文档，甚至能「看」一整个抽屉的目录。<strong>write</strong> 是<strong>一张全新的稿纸</strong>——整页重写，旧的全盖掉。<strong>edit</strong> 是一支<strong>精密改错笔</strong>——「把这句话改成那句」，但它有古板的脾气：要改的原句必须<strong>一字不差</strong>地对上（连空格缩进都算）；要是这句话在文中<strong>出现了两次</strong>，它会停笔反问「<strong>你指哪一处？</strong>」，绝不替你瞎猜；而且动笔前它会瞄一眼——<strong>你刚才看过之后，这页要是被别人涂改过，它就拒绝下笔</strong>，免得抹掉别人的工作。<strong>apply_patch</strong> 则是一叠<strong>批量施工单</strong>——「新增这个文件、改那个、删另一个」，一次性按单施工。四件工具，对应改动的四种<strong>粒度与形状</strong>，模型按需取用。
</div>

<h2>四把「手」：一张表看清分工</h2>
<p>先把四个工具并排放，它们的「形」一目了然——注意它们<strong>都在填第 36 课那张 <span class="mono">Config</span> 表</strong>（input/output schema + execute + 权限）：</p>
<table class="t">
  <tr><th>工具</th><th>input</th><th>改动粒度</th><th>权限</th></tr>
  <tr><td>read</td><td>path, offset?, limit?</td><td>只读（可翻页、可列目录）</td><td>assert 读权限</td></tr>
  <tr><td>write</td><td>path, content</td><td>整文件覆盖/新建</td><td>withPermission "write"</td></tr>
  <tr><td>edit</td><td>path, oldString, newString, replaceAll?</td><td>精确查找替换（一处或全部）</td><td>withPermission "edit"</td></tr>
  <tr><td>apply_patch</td><td>patchText</td><td>多文件批量 add/update/delete</td><td>withPermission</td></tr>
</table>
<p>这张表本身就是一堂设计课。四个工具覆盖了一条<strong>从粗到细、从单到多</strong>的改动光谱：<span class="mono">write</span> 最粗（整页换）、<span class="mono">edit</span> 最细（一句改）、<span class="mono">apply_patch</span> 最广（跨文件一把梭），而 <span class="mono">read</span> 是唯一<strong>不产生副作用</strong>的观察者。为什么要分这么多把？因为<strong>不同的改动形状，配不同的工具最省 token、最不易出错</strong>：改一行用 edit（只发那一行），重写整文件用 write（不必发 diff），跨文件重构用 apply_patch（一次成型）。模型会根据要做的事，<strong>自己挑那把最趁手的</strong>。这正是第 36 课「一张表、各自填空」结出的果——四种填法，覆盖四种真实需求。</p>
<p>另一个共性是<strong>路径的边界</strong>：所有文件工具的路径都<strong>相对于「当前 Location」（工作区）解析</strong>；Location 内的绝对路径可接受，但指向<strong>外部</strong>的绝对路径，需要额外的 <span class="mono">external_directory</span> 批准才放行。这是一道安全栅栏——agent 默认只能在它的工作区里折腾，想伸手到工作区外，得先过一道明确的许可。</p>
<p>两个端点的工具也各有巧思，值得各看一眼。先看只读的 <span class="mono">read</span>——它远不止「读一个文件」。它的 output 是一个<strong>三选一的联合</strong>，外加 offset/limit 的<strong>翻页</strong>能力：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">文件内容 Content</div><div class="c-txt">读一个文件；图片会被识别成 base64 + 图片 mime，作为「文件」内容回传给多模态模型</div></div>
  <div class="cell"><div class="c-tag">文本页 TextPage</div><div class="c-txt">大文本按 offset（起始行）+ limit（行数）翻页读，不必一次塞满上下文</div></div>
  <div class="cell"><div class="c-tag">目录列表 ListPage</div><div class="c-txt">path 指向目录时，read 变成「列目录」，同样可翻页</div></div>
</div>
<p>一个工具同时承担「读文件 / 列目录」、还内建翻页——这是把「<strong>观察文件系统</strong>」这件事抽象成了一个统一入口，模型不必为「读文件」和「看目录」记两套工具，一个 <span class="mono">read</span> 配不同的 path 就够了。再看另一端的 <span class="mono">apply_patch</span>，它的 output 是一个 <span class="mono">applied</span> 数组，每项记录一次操作的类型与目标：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">add</div><div class="c-txt">新增一个文件</div></div>
  <div class="cell"><div class="c-tag">update</div><div class="c-txt">修改一个已有文件</div></div>
  <div class="cell"><div class="c-tag">delete</div><div class="c-txt">删除一个文件</div></div>
</div>
<p>一段 <span class="mono">patchText</span> 里可以同时描述多文件的增、改、删，<span class="mono">apply_patch</span> <strong>顺序施工</strong>、逐条记进 <span class="mono">applied</span>。当模型要做一次「跨好几个文件的重构」时，比起连发十几次 edit，一次 apply_patch 既省 token、又让这组改动成为一个<strong>语义上的整体</strong>，要么整组生效、要么一眼看清在哪一步出了岔。</p>

<h2>worked-example：一次 edit 的完整一生</h2>
<p>现在把 <span class="mono">edit</span> 的 <span class="mono">execute</span> 一步步摊开。表面上它只做一件事——「把文件里的 <span class="mono">oldString</span> 换成 <span class="mono">newString</span>」。但真实的执行，是一条布满护栏的流水线：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">①先验参数</span><span class="t-txt">old==new？→ 拒：「没有改动」；old==""？→ 拒：「空串请用 write」（碰盘前先挡）</span></div>
  <div class="t-row"><span class="t-num">②问权限</span><span class="t-txt">permission.assert(...)：这文件准不准改？（第 41 课）</span></div>
  <div class="t-row"><span class="t-num">③读原文</span><span class="t-txt">readFile + decodeUtf8（处理 BOM）</span></div>
  <div class="t-row"><span class="t-num">④行尾归一</span><span class="t-txt">detect 文件是 \n 还是 \r\n，把 old/new 都转成同款</span></div>
  <div class="t-row"><span class="t-num">⑤数匹配</span><span class="t-txt">countOccurrences：0→拒「找不到」；&gt;1 且非 replaceAll→拒「有歧义」</span></div>
  <div class="t-row"><span class="t-num">⑥替换</span><span class="t-txt">replaceAll ? 全替 : 替第一处</span></div>
  <div class="t-row"><span class="t-num">⑦乐观写</span><span class="t-txt">writeIfUnchanged(expected=刚读到的字节)：被人改过就拒写</span></div>
</div>
<p>这条链里，<strong>真正「替换」的只有第 ⑥ 步一行代码</strong>，其余全是<strong>护栏</strong>。每一道护栏，都对应一个「让 AI 改代码」会踩的真实坑：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">精确匹配，不许模糊</div><div class="c-txt">oldString 必须一字不差（含空格缩进）；找不到就拒，绝不「差不多就改了」</div></div>
  <div class="cell"><div class="c-tag">歧义就拒，不替你猜</div><div class="c-txt">同一段出现多次且没说 replaceAll → 停手反问「请给更多上下文或设 replaceAll」</div></div>
  <div class="cell"><div class="c-tag">行尾自动归一</div><div class="c-txt">模型发的是 \n、文件可能是 \r\n；自动转成文件的同款，匹配才不会假性失败</div></div>
  <div class="cell"><div class="c-tag">乐观并发，不覆盖别人</div><div class="c-txt">writeIfUnchanged 带上「我读到的原字节」，写时若文件已变→拒，绝不抹掉他人改动</div></div>
</div>
<p>第 ⑤ 步的「歧义拒绝」最见品格。模型说「把 <span class="mono">return x</span> 改成 <span class="mono">return y</span>」，可文件里有三处 <span class="mono">return x</span>——改哪个？<strong>一个莽撞的工具会改第一个（或全改），然后酿成 bug；edit 选择停手反问。</strong>它宁可让模型「多给点上下文」再来一次，也不替它赌。这是一种深刻的克制：<strong>面对歧义，最负责任的动作不是「猜一个」，而是「把歧义如实抛回去」</strong>。第 ① 步的「碰盘前先验」也是同理——参数明显无意义（old==new、old=""）时，<strong>在产生任何副作用之前就拒掉</strong>，错误来得越早越廉价。这两道护栏背后是同一个信念：<strong>一个会被 AI 高频调用、又直接改你磁盘的工具，必须把「不确定」挡在「动手」之前。</strong>模型会幻觉、会笔误、会自信地给出对不上的 oldString——edit 不假设模型永远对，而是把每一种「可能出错」都显式地拦成一条清楚的拒绝。这种「不信任输入、处处设防」的姿态，正是把一个玩具级 demo 和一个敢让人用在真实代码库上的工具区分开的东西。</p>

<h2>writeIfUnchanged：不覆盖别人的乐观并发</h2>
<p>第 ⑦ 步那个 <span class="mono">writeIfUnchanged</span> 值得单独品，它是这套设计里最「老练」的一笔。想象一个时间差：edit 在 <span class="mono">③</span> 读到了文件的字节，到 <span class="mono">⑦</span> 要写回去，中间隔着读文件、数匹配、算替换这些步骤——这段时间里，<strong>别的进程（另一个 agent、用户在编辑器里手改、一个 watch 脚本）完全可能也改了同一个文件</strong>。若 edit 闷头把自己算出的新内容写回去，就会<strong>悄悄抹掉那期间别人的改动</strong>（经典的「丢失更新」）。</p>
<div class="flow">
  <div class="f-node">③读到原字节<br><small>expected = 这份</small></div>
  <div class="f-arrow">…算替换…→</div>
  <div class="f-node">⑦writeIfUnchanged<br><small>带上 expected 一起写</small></div>
  <div class="f-arrow">盘上还是 expected？</div>
  <div class="f-node">是→写入 / 否→拒写<br><small>compare-and-swap</small></div>
</div>
<p><span class="mono">writeIfUnchanged({target, expected: 刚读到的字节, content: 新内容})</span> 的语义是<strong>「比较并交换」（compare-and-swap）</strong>：只在「磁盘上的内容还等于我当初读到的那份」时才写入；若已经变了，<strong>拒绝写、报错</strong>。这就把「读—改—写」三步之间的并发风险<strong>关进了一个原子操作里</strong>。它不上悲观锁（不阻塞别人），而是<strong>乐观地假设没人动、写时再核对</strong>——这正是数据库与分布式系统里常见的乐观并发控制（OCC）。一个「改文件」的小工具，竟把数据库级的并发严谨度用上了，这就是 opencode「把每件小事都当真」的底色。值得一提的是，这道护栏在<strong>多 agent 并行</strong>的未来尤其关键：当好几个 agent 可能同时动同一个代码库时，「我以为我在改的，是不是还是我读到的那份」就不再是杞人忧天，而是每次写盘都要回答的问题。edit 用 <span class="mono">writeIfUnchanged</span> 提前把这个答案焊进了每一次替换里——<strong>它不是为今天的单 agent 写的，而是为明天的并发世界留的余地。</strong></p>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <p>文件工具是 agent「动手改世界」最直接的一组手：</p>
  <ul>
    <li><strong>四把手覆盖改动光谱</strong>：<span class="mono">read</span>（只读、可翻页、可列目录）/ <span class="mono">write</span>（整文件覆盖）/ <span class="mono">edit</span>（精确查找替换）/ <span class="mono">apply_patch</span>（多文件批量 add/update/delete）。从粗到细、从单到多，模型按改动形状挑趁手的那把。</li>
    <li><strong>全是第 36 课 Config 表的不同填法</strong>：各声明 input/output schema + execute，套 <span class="mono">withPermission</span>/<span class="mono">permission.assert</span>。印证「一张表、各自填空」。</li>
    <li><strong>edit 的四道护栏</strong>：精确匹配（不模糊）、歧义拒绝（多匹配不猜）、行尾归一（\n↔\r\n）、乐观并发写（<span class="mono">writeIfUnchanged</span> 不覆盖别人）。真正「替换」只一行，其余全是护栏。</li>
    <li><strong>路径边界</strong>：相对「当前 Location」解析；外部绝对路径需 <span class="mono">external_directory</span> 批准。安全栅栏让 agent 默认只在工作区内活动。</li>
  </ul>
  <p>这一课的主旋律——「让 AI 安全地改代码，难点在护栏不在替换」——会一路贯穿 M7。下一课（第 39 课）转向<strong>搜索与执行工具</strong>：<span class="mono">glob</span>（按名找文件）、<span class="mono">grep</span>（按内容搜）、<span class="mono">bash</span>（跑命令）——其中 bash 经 PTY 运行、又是另一圈精巧的护栏。读文件、搜文件、跑命令，是 coding agent 的三大基本功，这两课把前两样讲透。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p>edit「数匹配 → 按数量决定」的那段，把克制写得很直白（简化自 edit.ts）：</p>
  <pre class="code"><span class="cm">// ④行尾归一后，⑤数匹配，按数量分流</span>
<span class="kw">const</span> oldString = <span class="fn">convertToLineEnding</span>(input.oldString, ending)  <span class="cm">// 转成文件的 \n / \r\n</span>
<span class="kw">const</span> replacements = <span class="fn">countOccurrences</span>(source.text, oldString)
<span class="kw">if</span> (replacements === 0)
  <span class="kw">return</span> <span class="kw">new</span> ToolFailure({ message: <span class="st">"Could not find oldString ... must match exactly"</span> })
<span class="kw">if</span> (replacements &gt; 1 &amp;&amp; input.replaceAll !== <span class="kw">true</span>)
  <span class="kw">return</span> <span class="kw">new</span> ToolFailure({ message: <span class="st">"Found multiple exact matches ... set replaceAll to true"</span> })
<span class="kw">const</span> replaced = input.replaceAll === <span class="kw">true</span>
  ? source.text.<span class="fn">replaceAll</span>(oldString, newString)
  : source.text.<span class="fn">replace</span>(oldString, newString)
<span class="cm">// ⑦ 乐观写：只在文件未变时落盘</span>
files.<span class="fn">writeIfUnchanged</span>({ target, expected: source.content, content: ... })</pre>
  <p>注意这些「拒绝」全部走 <span class="mono">ToolFailure</span>——回到第 36、37 课的闭环：工具的失败不是异常，而是一个<strong>规规矩矩的值</strong>，被注册表收成「错误结果」回传模型。于是模型读到「找不到 oldString」或「有多处匹配，请加上下文」时，能<strong>自己据此修正、重试</strong>——错误信息本身成了给模型的「下一步提示」。<strong>好的工具不只在成功时有用，更在失败时把「为什么失败、该怎么办」讲清楚</strong>，因为它的「用户」是个会照着错误信息调整的模型。这也是为什么 edit 的每条拒绝消息都写得像一句叮嘱（"must match exactly"、"set replaceAll to true"）——它们是<strong>写给模型看的操作指南</strong>。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>四个文件工具</strong>（<span class="mono">core/src/tool/{read,write,edit,apply-patch}.ts</span>）覆盖改动光谱：<span class="mono">read</span>（只读/翻页/列目录）、<span class="mono">write</span>（整文件覆盖）、<span class="mono">edit</span>（精确查找替换）、<span class="mono">apply_patch</span>（多文件批量 add/update/delete）。全是第 36 课 <span class="mono">Config</span> 表的不同填法 + <span class="mono">withPermission</span>。</li>
    <li><strong>edit 的执行是一条护栏流水线</strong>：①验参（old==new/空串→拒）②permission.assert ③读+decodeUtf8(BOM) ④行尾归一(\n↔\r\n) ⑤数匹配 ⑥替换 ⑦乐观写。真正替换只第 ⑥ 步一行。</li>
    <li><strong>edit 四道护栏</strong>：精确匹配（含空格缩进，找不到即拒）；歧义拒绝（多匹配且非 replaceAll→停手反问，不替模型猜）；行尾自动归一（避免假性失配）；<strong>乐观并发写</strong>。</li>
    <li><strong><span class="mono">writeIfUnchanged(expected=读到的字节)</span> = compare-and-swap</strong>：只在磁盘内容仍等于当初读到的那份时才写，否则拒——把「读-改-写」的并发风险关进原子操作，防丢失更新（乐观并发控制 OCC，不上悲观锁）。</li>
    <li><strong>路径相对「当前 Location」解析</strong>，外部绝对路径需 <span class="mono">external_directory</span> 批准（安全栅栏）。所有「拒绝」走 <span class="mono">ToolFailure</span> 回传模型，错误消息即给模型的操作指南。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">The prior two lessons built the tool system's <strong>skeleton</strong>: how a tool is defined (lesson 36's <span class="mono">Tool.make</span>), how it's collected into a model-visible list (lesson 37's registry). From this lesson, we dive into <strong>individual real tools</strong>, watching "the skeleton grow flesh." First the most everyday—and most skill-testing—family: <strong>file tools</strong>: <span class="mono">read</span>, <span class="mono">write</span> (whole-write), <span class="mono">edit</span> (precise edit), <span class="mono">apply_patch</span> (batch patching). For a code-writing agent, the vast majority of actions land as these four "hands" reading and changing files.</p>
<p>This lesson has two layers of payoff. One, <strong>confirming lesson 36</strong>: you'll see firsthand these four tools are <strong>all different fillings of the same <span class="mono">Config</span> form</strong>—each declaring input/output schema + execute, wrapped in <span class="mono">withPermission</span>, nothing more. Two, the centerpiece: we'll <strong>unfold the edit tool's execution step by step</strong> (the spec-named worked-example), seeing how much <strong>production-grade rigor</strong> hides behind a small "change this text to that" operation—exact match, ambiguity refusal, line-ending normalization, optimistic-concurrency write. You'll come away understanding: letting AI safely change your code, <strong>the hard part was never "string replacement," but the ring of guardrails around it—"don't guess, don't err, don't clobber others."</strong></p>

<div class="card analogy">
  <div class="tag">✍️ Analogy</div>
  Picture these four file tools as a wordsmith's <strong>four implements</strong>. <strong>read</strong> is a <strong>magnifying glass</strong>—look without changing, paging through a long document (offset/limit), even "looking" at a whole drawer's worth of directory. <strong>write</strong> is a <strong>fresh sheet of paper</strong>—rewrite the whole page, the old all covered. <strong>edit</strong> is a <strong>precision correction pen</strong>—"change this sentence to that," but with a fussy temperament: the original sentence to change must match <strong>letter-for-letter</strong> (spaces and indentation count); if that sentence <strong>appears twice</strong> in the text, it stops and asks back "<strong>which one do you mean?</strong>," never guessing for you; and before writing it glances—<strong>if the page got scribbled on by someone else since you last looked, it refuses to write</strong>, lest it erase their work. <strong>apply_patch</strong> is a stack of <strong>batch work orders</strong>—"add this file, change that, delete the other," executed in one pass per the orders. Four implements, for the four <strong>granularities and shapes</strong> of change, the model picking as needed.
</div>

<h2>Four "hands": one table for the division of labor</h2>
<p>First lay the four tools side by side, their "shape" plain—note they <strong>all fill lesson 36's <span class="mono">Config</span> form</strong> (input/output schema + execute + permission):</p>
<table class="t">
  <tr><th>Tool</th><th>input</th><th>Change granularity</th><th>Permission</th></tr>
  <tr><td>read</td><td>path, offset?, limit?</td><td>read-only (paging, directory listing)</td><td>assert read permission</td></tr>
  <tr><td>write</td><td>path, content</td><td>whole-file overwrite/create</td><td>withPermission "write"</td></tr>
  <tr><td>edit</td><td>path, oldString, newString, replaceAll?</td><td>exact find-replace (one or all)</td><td>withPermission "edit"</td></tr>
  <tr><td>apply_patch</td><td>patchText</td><td>multi-file batch add/update/delete</td><td>withPermission</td></tr>
</table>
<p>This table is itself a design lesson. The four cover a <strong>coarse-to-fine, single-to-many</strong> change spectrum: <span class="mono">write</span> coarsest (whole page swap), <span class="mono">edit</span> finest (one sentence change), <span class="mono">apply_patch</span> broadest (cross-file in one go), and <span class="mono">read</span> the only <strong>side-effect-free</strong> observer. Why so many? Because <strong>different change shapes fit different tools to save the most tokens and least err</strong>: change one line with edit (send just that line), rewrite a whole file with write (no diff needed), refactor across files with apply_patch (formed in one pass). The model, per the task, <strong>picks the handiest one itself</strong>. This is the fruit of lesson 36's "one form, each fills blanks"—four fillings, covering four real needs.</p>
<p>Another commonality is the <strong>path boundary</strong>: all file tools' paths resolve <strong>relative to the "active Location" (workspace)</strong>; absolute paths inside the Location are accepted, but absolute paths pointing <strong>outside</strong> require extra <span class="mono">external_directory</span> approval. This is a security fence—the agent by default can only mess within its workspace; reaching outside needs explicit permission first.</p>
<p>The two endpoint tools each have cleverness worth a look. First the read-only <span class="mono">read</span>—far more than "read a file." Its output is a <strong>three-way union</strong>, plus offset/limit <strong>paging</strong>:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">file Content</div><div class="c-txt">read a file; images are recognized as base64 + image mime, returned as "file" content to the multimodal model</div></div>
  <div class="cell"><div class="c-tag">TextPage</div><div class="c-txt">large text read by offset (start line) + limit (line count) paging, not stuffing the context at once</div></div>
  <div class="cell"><div class="c-tag">ListPage</div><div class="c-txt">when path points to a directory, read becomes "list directory," also pageable</div></div>
</div>
<p>One tool serving "read file / list directory," with built-in paging—abstracting "<strong>observing the filesystem</strong>" into one unified entry; the model needn't remember two tools for "read a file" and "view a directory," one <span class="mono">read</span> with different paths suffices. Now the other endpoint, <span class="mono">apply_patch</span>: its output is an <span class="mono">applied</span> array, each item recording one operation's type and target:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">add</div><div class="c-txt">add a file</div></div>
  <div class="cell"><div class="c-tag">update</div><div class="c-txt">modify an existing file</div></div>
  <div class="cell"><div class="c-tag">delete</div><div class="c-txt">delete a file</div></div>
</div>
<p>One <span class="mono">patchText</span> can describe adds, updates, deletes across multiple files at once; <span class="mono">apply_patch</span> <strong>executes sequentially</strong>, logging each into <span class="mono">applied</span>. When the model wants "a refactor across several files," versus firing a dozen edits, one apply_patch both saves tokens and makes this group of changes <strong>a semantic whole</strong>.</p>

<h2>Worked-example: a single edit's full life</h2>
<p>Now unfold <span class="mono">edit</span>'s <span class="mono">execute</span> step by step. On the surface it does one thing—"replace <span class="mono">oldString</span> with <span class="mono">newString</span> in the file." But the real execution is a pipeline lined with guardrails:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">①validate first</span><span class="t-txt">old==new? → reject "no changes"; old==""? → reject "use write for empty" (block before touching disk)</span></div>
  <div class="t-row"><span class="t-num">②ask permission</span><span class="t-txt">permission.assert(...): is this file allowed to change? (lesson 41)</span></div>
  <div class="t-row"><span class="t-num">③read source</span><span class="t-txt">readFile + decodeUtf8 (handle BOM)</span></div>
  <div class="t-row"><span class="t-num">④normalize line ending</span><span class="t-txt">detect file's \n or \r\n, convert old/new to the same</span></div>
  <div class="t-row"><span class="t-num">⑤count matches</span><span class="t-txt">countOccurrences: 0→reject "not found"; &gt;1 & not replaceAll→reject "ambiguous"</span></div>
  <div class="t-row"><span class="t-num">⑥replace</span><span class="t-txt">replaceAll ? replace all : replace first</span></div>
  <div class="t-row"><span class="t-num">⑦optimistic write</span><span class="t-txt">writeIfUnchanged(expected=just-read bytes): reject if someone changed it</span></div>
</div>
<p>In this chain, <strong>only step ⑥, one line, actually "replaces"</strong>; all the rest are <strong>guardrails</strong>. Each guardrail corresponds to a real pit "letting AI change code" steps into:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">exact match, no fuzzy</div><div class="c-txt">oldString must match letter-for-letter (spaces, indentation); not found → reject, never "close enough so change it"</div></div>
  <div class="cell"><div class="c-tag">ambiguity rejected, no guessing</div><div class="c-txt">same segment appearing multiple times without replaceAll → stop and ask "give more context or set replaceAll"</div></div>
  <div class="cell"><div class="c-tag">line endings auto-normalized</div><div class="c-txt">model sends \n, file may be \r\n; auto-convert to the file's, so matching doesn't falsely fail</div></div>
  <div class="cell"><div class="c-tag">optimistic concurrency, no clobbering</div><div class="c-txt">writeIfUnchanged carries "the bytes I read"; if the file changed at write time → reject, never erasing others' changes</div></div>
</div>
<p>Step ⑤'s "ambiguity refusal" shows the most character. The model says "change <span class="mono">return x</span> to <span class="mono">return y</span>," but the file has three <span class="mono">return x</span>—which one? <strong>A reckless tool would change the first (or all), then breed a bug; edit chooses to stop and ask back.</strong> It would rather have the model "give more context" and retry than gamble. This is profound restraint: <strong>facing ambiguity, the most responsible action isn't "guess one" but "throw the ambiguity back faithfully."</strong> Step ①'s "validate before touching disk" is the same logic—when params are obviously meaningless (old==new, old==""), <strong>reject before any side effect</strong>; the earlier the error, the cheaper. Both guardrails rest on one belief: <strong>a tool called frequently by AI and directly changing your disk must block "uncertainty" before "acting."</strong> The model hallucinates, mistypes, confidently gives a mismatched oldString—edit doesn't assume the model is always right, but explicitly intercepts each "could go wrong" into a clear rejection. This stance of "distrust input, guard everywhere" is exactly what separates a toy demo from a tool you'd dare use on a real codebase.</p>

<h2>writeIfUnchanged: optimistic concurrency that doesn't clobber others</h2>
<p>Step ⑦'s <span class="mono">writeIfUnchanged</span> deserves its own savor—the most "seasoned" stroke in this design. Imagine a time gap: edit read the file's bytes at <span class="mono">③</span>, and by <span class="mono">⑦</span> wants to write back, with reading, counting, computing the replacement in between—during which <strong>another process (another agent, the user editing in their editor, a watch script) may well have changed the same file</strong>. If edit blindly writes its computed new content back, it would <strong>silently erase others' changes in that interval</strong> (the classic "lost update").</p>
<div class="flow">
  <div class="f-node">③read source bytes<br><small>expected = this</small></div>
  <div class="f-arrow">…compute replace…→</div>
  <div class="f-node">⑦writeIfUnchanged<br><small>write with expected</small></div>
  <div class="f-arrow">disk still expected?</div>
  <div class="f-node">yes→write / no→reject<br><small>compare-and-swap</small></div>
</div>
<p><span class="mono">writeIfUnchanged({target, expected: just-read bytes, content: new})</span>'s semantics are <strong>"compare-and-swap"</strong>: write only if "the disk content still equals what I originally read"; if changed, <strong>refuse to write, error out</strong>. This locks the concurrency risk between "read—modify—write" into <strong>one atomic operation</strong>. It takes no pessimistic lock (doesn't block others) but <strong>optimistically assumes no one touched it, verifying at write time</strong>—exactly the optimistic concurrency control (OCC) common in databases and distributed systems. A small "change a file" tool wielding database-grade concurrency rigor—that's opencode's "take every small thing seriously" character. Worth noting, this guardrail is especially crucial in a <strong>multi-agent parallel</strong> future: when several agents may touch the same codebase at once, "is what I think I'm changing still the one I read" stops being paranoia and becomes a question every write must answer. edit welds that answer into every replacement ahead of time with <span class="mono">writeIfUnchanged</span>—<strong>it's written not for today's single agent, but as headroom for tomorrow's concurrent world.</strong></p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>File tools are the most direct hands for the agent "changing the world":</p>
  <ul>
    <li><strong>Four hands covering the change spectrum</strong>: <span class="mono">read</span> (read-only, paging, directory listing) / <span class="mono">write</span> (whole-file overwrite) / <span class="mono">edit</span> (exact find-replace) / <span class="mono">apply_patch</span> (multi-file batch add/update/delete). Coarse-to-fine, single-to-many; the model picks the handiest by change shape.</li>
    <li><strong>All different fillings of lesson 36's Config form</strong>: each declaring input/output schema + execute, wrapped in <span class="mono">withPermission</span>/<span class="mono">permission.assert</span>. Confirming "one form, each fills blanks."</li>
    <li><strong>edit's four guardrails</strong>: exact match (no fuzzy), ambiguity refusal (multiple matches, no guessing), line-ending normalization (\n↔\r\n), optimistic-concurrency write (<span class="mono">writeIfUnchanged</span> doesn't clobber). Only one line actually "replaces," the rest all guardrails.</li>
    <li><strong>Path boundary</strong>: resolved relative to "active Location"; external absolute paths need <span class="mono">external_directory</span> approval. A security fence keeping the agent within its workspace by default.</li>
  </ul>
  <p>This lesson's main theme—"letting AI safely change code, the difficulty is in guardrails not replacement"—runs through all of M7. The next lesson (39) turns to <strong>search & exec tools</strong>: <span class="mono">glob</span> (find files by name), <span class="mono">grep</span> (search by content), <span class="mono">bash</span> (run commands)—where bash runs via PTY, another ring of fine guardrails. Reading files, searching files, running commands are a coding agent's three basic skills; these two lessons cover the first two thoroughly.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p>edit's "count matches → decide by count" writes restraint plainly (simplified from edit.ts):</p>
  <pre class="code"><span class="cm">// ④ after normalizing line endings, ⑤ count matches, branch by count</span>
<span class="kw">const</span> oldString = <span class="fn">convertToLineEnding</span>(input.oldString, ending)  <span class="cm">// to the file's \n / \r\n</span>
<span class="kw">const</span> replacements = <span class="fn">countOccurrences</span>(source.text, oldString)
<span class="kw">if</span> (replacements === 0)
  <span class="kw">return</span> <span class="kw">new</span> ToolFailure({ message: <span class="st">"Could not find oldString ... must match exactly"</span> })
<span class="kw">if</span> (replacements &gt; 1 &amp;&amp; input.replaceAll !== <span class="kw">true</span>)
  <span class="kw">return</span> <span class="kw">new</span> ToolFailure({ message: <span class="st">"Found multiple exact matches ... set replaceAll to true"</span> })
<span class="kw">const</span> replaced = input.replaceAll === <span class="kw">true</span>
  ? source.text.<span class="fn">replaceAll</span>(oldString, newString)
  : source.text.<span class="fn">replace</span>(oldString, newString)
<span class="cm">// ⑦ optimistic write: land only if the file is unchanged</span>
files.<span class="fn">writeIfUnchanged</span>({ target, expected: source.content, content: ... })</pre>
  <p>Note all these "rejections" go through <span class="mono">ToolFailure</span>—back to lessons 36, 37's loop: a tool's failure isn't an exception but a <strong>well-behaved value</strong>, collected by the registry into an "error result" back to the model. So when the model reads "could not find oldString" or "multiple matches, add context," it can <strong>correct and retry itself</strong>—the error message becomes the model's "next-step hint." <strong>A good tool is useful not only on success but, on failure, makes "why it failed, what to do" clear</strong>, because its "user" is a model that adjusts per the error message. That's why each of edit's rejection messages reads like an instruction ("must match exactly," "set replaceAll to true")—they're <strong>operating guides written for the model to read</strong>.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>Four file tools</strong> (<span class="mono">core/src/tool/{read,write,edit,apply-patch}.ts</span>) cover the change spectrum: <span class="mono">read</span> (read-only/paging/directory listing), <span class="mono">write</span> (whole-file overwrite), <span class="mono">edit</span> (exact find-replace), <span class="mono">apply_patch</span> (multi-file batch add/update/delete). All different fillings of lesson 36's <span class="mono">Config</span> form + <span class="mono">withPermission</span>.</li>
    <li><strong>edit's execution is a guardrail pipeline</strong>: ①validate (old==new/empty→reject) ②permission.assert ③read+decodeUtf8(BOM) ④normalize line endings (\n↔\r\n) ⑤count matches ⑥replace ⑦optimistic write. Only step ⑥, one line, actually replaces.</li>
    <li><strong>edit's four guardrails</strong>: exact match (incl. spaces/indentation, not found → reject); ambiguity refusal (multiple matches & not replaceAll → stop and ask, no guessing for the model); auto line-ending normalization (avoiding false mismatches); <strong>optimistic-concurrency write</strong>.</li>
    <li><strong><span class="mono">writeIfUnchanged(expected=read bytes)</span> = compare-and-swap</strong>: write only if disk content still equals what was originally read, else reject—locking "read-modify-write" concurrency risk into an atomic operation, preventing lost updates (optimistic concurrency control OCC, no pessimistic lock).</li>
    <li><strong>Paths resolve relative to "active Location"</strong>, external absolute paths need <span class="mono">external_directory</span> approval (security fence). All "rejections" go through <span class="mono">ToolFailure</span> back to the model; the error message is the model's operating guide.</li>
  </ul>
</div>
""",
}
LESSON_39 = {
    "zh": r"""
<p class="lead">上一课讲了 agent 改文件的四把手。但改之前，得先<strong>找到</strong>该改的地方；很多任务还得<strong>跑一下命令</strong>看结果（装依赖、跑测试、git status）。这一课的三个工具，正是 coding agent 另外两项基本功：<strong>搜索</strong>与<strong>执行</strong>。<span class="mono">glob</span>（按文件名找）、<span class="mono">grep</span>（按文件内容搜）、<span class="mono">bash</span>（跑 shell 命令）。前两个是「<strong>眼睛</strong>」——快速在代码库里定位；后一个是「<strong>万能之手</strong>」——能干前面所有专用工具干不了的杂活，但也因此<strong>权力最大、护栏最多</strong>。</p>
<p>这一课你会看到一个有趣的对照：<strong>专用 vs 通用</strong>。glob/grep 是<strong>专用</strong>工具——把「搜索」这件高频事做成快、稳、有界的两个窄接口（底层都是 ripgrep）；bash 则是<strong>通用</strong>逃生舱——它拥有「宿主用户的文件系统、进程、网络权限」，几乎无所不能，于是 opencode 给它套上一整圈安全带：<strong>限时、限量、双重许可、可强制终止</strong>。我还会顺手澄清一个常见误解——<strong>bash 工具并不是经「PTY（伪终端）」运行的</strong>；PTY 是另一套给「交互式终端」用的基础设施，和「跑一条命令拿结果」的 bash 工具是两回事。把这条厘清，你对「批处理执行」与「交互式终端」的边界就清楚了。</p>

<div class="card analogy">
  <div class="tag">🔦 生活类比</div>
  想象 agent 在一座巨大的代码图书馆里工作。<strong>glob</strong> 是「<strong>按书名查找</strong>」——「给我所有 <span class="mono">*.test.ts</span>」，唰地列出书名清单。<strong>grep</strong> 是「<strong>按书里的一句话查找</strong>」——「哪些书里出现过 <span class="mono">TODO: fix</span>」，翻遍内容把命中处揪出来。两者都靠图书馆那台<strong>极快的检索机</strong>（ripgrep），还自动跳过你让它忽略的架子（gitignore）。而 <strong>bash</strong>，则是直接把<strong>整间工坊的钥匙</strong>交到 agent 手里——它能开机床、能搬运、能对外打电话（文件、进程、网络全权限）。正因为这把钥匙太重，工坊门口立了几条铁律：<strong>每次作业有时限（超时强制收工）、产出的废料有上限（输出超量就截断）、动工前要登记（权限许可）、还配了总闸（能强制断电终止）</strong>。专用工具像贴了标签的精巧仪器，通用的 bash 像一间需要安全规程的车间——<strong>能力越大，护栏越严</strong>。
</div>

<h2>glob 与 grep：两种「找」</h2>
<p>先把三个工具并排，一张表看清它们的分工与各自的「边界」——它们也都在填第 36 课那张 <span class="mono">Config</span> 表：</p>
<table class="t">
  <tr><th>工具</th><th>干什么</th><th>底层</th><th>关键边界</th></tr>
  <tr><td>glob</td><td>按文件名 pattern 找文件</td><td>Ripgrep</td><td>limit 结果上限</td></tr>
  <tr><td>grep</td><td>按内容正则搜（+include 文件 glob）</td><td>Ripgrep</td><td>limit 命中上限</td></tr>
  <tr><td>bash</td><td>跑一条 shell 命令（全权限）</td><td>AppProcess/spawn</td><td>超时 + 1MB 字节 + 双许可</td></tr>
</table>
<p>先看两个搜索工具。它们解决的是同一个大问题——「<strong>在代码库里定位</strong>」——但切口不同：</p>
<div class="cols">
  <div class="col"><h4>glob · 按名字找</h4><p>input <span class="mono">{pattern, path?, limit?}</span>，output 文件清单。「给我匹配 <span class="mono">src/**/*.ts</span> 的文件」。问的是<strong>「哪些文件叫这个名」</strong>。</p></div>
  <div class="col"><h4>grep · 按内容搜</h4><p>input <span class="mono">{pattern(正则), path?, include?, limit?}</span>，output 命中清单。「哪些文件里有 <span class="mono">useEffect</span>」。问的是<strong>「哪些文件里写了这个」</strong>。</p></div>
</div>
<p>两者的实现都<strong>架在 <span class="mono">Ripgrep</span> 服务之上</strong>——这是个聪明的选择。ripgrep（rg）是业界公认最快的代码搜索工具之一，且<strong>默认尊重 <span class="mono">.gitignore</span></strong>：它不会把 <span class="mono">node_modules</span>、<span class="mono">dist</span> 这些一并搜进来污染结果。opencode 没有自己手写遍历文件系统、再实现正则匹配（又慢又容易错），而是<strong>站在 ripgrep 这个巨人的肩膀上</strong>，只把它包装成两个窄窄的工具接口。这又是第 35 课「不重复造轮子、复用权威上游」的同一种智慧——搜索这种「别人已经做到极致」的事，借力即可。</p>
<p>还有一个共性是<strong>都带 <span class="mono">limit</span>（结果上限）</strong>。为什么搜索也要限量？因为一个宽泛的 pattern（比如 grep <span class="mono">import</span>）可能命中成千上万处，全塞回对话会<strong>瞬间撑爆模型的上下文窗口</strong>。<span class="mono">limit</span> 把结果框在一个合理范围，逼模型<strong>用更精确的 pattern 或更窄的 path 去缩小范围</strong>，而不是一次捞一海。这和上一课文件工具的 offset/limit 翻页、和第 42 课的有界输出，是同一条贯穿 M7 的红线：<strong>凡是可能「量很大」的地方，都要有界</strong>——因为对面那个消费结果的模型，上下文窗口是有限且昂贵的。</p>

<h2>bash：万能之手，与它的一圈安全带</h2>
<p>接着是重头戏 <span class="mono">bash</span>。它的描述里有一句很重的话——执行命令时用的是「<strong>宿主用户的文件系统、进程、网络权限</strong>」。换句话说，<strong>bash 能干的事，几乎等于你本人在终端能干的事</strong>。这是它的威力（前面所有专用工具够不着的杂活，它都能凑合），也是它的危险（一条 <span class="mono">rm -rf</span> 也照跑）。所以 opencode 给 bash 套了一整圈安全带：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">限时</div><div class="c-txt">默认 2 分钟、最长 10 分钟（schema 层就 ≤ MAX_TIMEOUT_MS）；超时→明确报「超时，请加大 timeout 重试」</div></div>
  <div class="cell"><div class="c-tag">限量</div><div class="c-txt">stdout/stderr 各 1 MB 内存上限（MAX_CAPTURE_BYTES）；超量→截断 + 加一条 truncated 提示</div></div>
  <div class="cell"><div class="c-tag">双重许可</div><div class="c-txt">workdir 一道（外部目录需 external_directory 批准）+ 命令本身一道 permission.assert</div></div>
  <div class="cell"><div class="c-tag">可强制终止</div><div class="c-txt">detached 启动（非 Windows）便于整组收尾；forceKillAfter 3 秒宽限后强制结束</div></div>
  <div class="cell"><div class="c-tag">无交互</div><div class="c-txt">stdin 设为 ignore——命令不能反过来问模型要输入（模型答不了）</div></div>
</div>
<p>把这几条连起来看，会发现一个清晰的设计意图：<strong>给最强的能力，配最严的约束</strong>。glob/grep 这种专用工具，能造成的破坏有限，护栏也轻；bash 这种「什么都能干」的逃生舱，则被<strong>限时、限量、限地、可中断</strong>地团团围住。其中<strong>限时</strong>尤其关键——一条 <span class="mono">npm install</span> 可能要几十秒，但一个写错的死循环会永远跑下去；超时（默认 2 分钟）把每条命令都拴上一根<strong>时间皮带</strong>，跑过头就强制收工，绝不让一条命令把整个 agent 挂死。而超时后的处理也很体贴：不是干巴巴报错，而是回一句「<strong>超时了，如果这命令本就该跑久点，请加大 timeout 重试</strong>」——又是一条写给模型看的、可操作的指引（呼应第 38 课）。</p>
<p>执行的主干流程，是一条「解析→许可→启动→限时跑→收果」的链：</p>
<div class="flow">
  <div class="f-node">解析 workdir<br><small>相对 Location；外部需批准</small></div>
  <div class="f-arrow">permission.assert →</div>
  <div class="f-node">spawn 子进程<br><small>detached + 配置的 shell</small></div>
  <div class="f-arrow">run(timeout, maxBytes) →</div>
  <div class="f-node">限时+限量地跑<br><small>超时→timedOut；超量→truncated</small></div>
  <div class="f-arrow">→</div>
  <div class="f-node">{exitCode, output, truncated…}<br><small>结构化结果回传</small></div>
</div>
<p>同一条链，会落到几种不同的结局，<span class="mono">output</span> 把它们都如实编码进结构化结果，让模型一眼看清「<strong>是成了、错了、卡了、还是被截了</strong>」：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">成功</span><span class="t-txt">exitCode=0，output 是命令的完整输出</span></div>
  <div class="t-row"><span class="t-num">非零退出</span><span class="t-txt">exitCode≠0（命令自己报错），output 含 stderr——模型据此判断失败原因</span></div>
  <div class="t-row"><span class="t-num">超时</span><span class="t-txt">timedOut=true，output=「超时，请加大 timeout 重试」</span></div>
  <div class="t-row"><span class="t-num">输出超量</span><span class="t-txt">truncated=true，output 被截 + 附「capture truncated」提示</span></div>
</div>

<h2>澄清：bash 工具 ≠ PTY 终端</h2>
<p>这里要破除一个常见的混淆。你可能听过 opencode 有「PTY / 伪终端」，于是猜 bash 工具是经 PTY 跑的。<strong>其实不是。</strong>看源码：bash 工具通过 <span class="mono">AppProcess.run</span> 执行命令，而 <span class="mono">AppProcess</span> 底层是 <span class="mono">ChildProcessSpawner</span>（基于 <span class="mono">child_process</span>/spawn 的跨平台封装）——<strong>它是「启动一个子进程、跑完、把 stdout/stderr 收回来」的批处理模型</strong>，不是伪终端。那 <span class="mono">pty/*</span> 模块是干嘛的？它是<strong>另一套东西</strong>：给「<strong>交互式终端</strong>」用的伪终端基础设施（还记得第 10 课的 <span class="mono">pty</span>/<span class="mono">pty-connect</span> 路由组、第 33 课提到的 WebSocketTracker 跟踪的就是 pty 终端吗？那是让你在界面里开一个<strong>实时、可输入</strong>的 shell 会话用的）。两者的区别很本质：</p>
<div class="cols">
  <div class="col"><h4>bash 工具（批处理）</h4><p><span class="mono">spawn</span> 一个子进程 → 跑一条命令 → 收 stdout/stderr → 结束。<strong>一来一回</strong>，无交互，给模型用。</p></div>
  <div class="col"><h4>pty 模块（交互式）</h4><p>一个<strong>持久的伪终端</strong>：<span class="mono">onData</span> 流式输出、<span class="mono">write</span> 喂输入、<span class="mono">resize</span> 调大小。给<strong>真人</strong>开实时 shell 用。</p></div>
</div>
<p>为什么 bash 工具<strong>不</strong>用 PTY？因为模型需要的是「跑一条命令、拿到完整结果」的<strong>确定性批处理</strong>，而不是一个会不断吐字符、还可能等你输入的<strong>实时流</strong>。PTY 那套「流式 + 可输入」对一个不能被即时追问的模型反而是负担（stdin 干脆设成 ignore 就是这个道理）。<strong>把「给模型跑命令」和「给真人开终端」用两套不同的机制分开，各自服务各自的交互模型</strong>——这是个清醒的切分。下次再看到 opencode 里的 pty，你就知道：那是终端功能，不是 bash 工具。</p>
<p>顺着这条「为不同交互模型选不同机制」的思路再想一层：批处理之所以适合模型，是因为模型的「思考—行动」节奏本就是<strong>一问一答</strong>的——它发一条命令、等一个完整结果、再决定下一步，正好对上「spawn 跑完收果」的形态。而 PTY 的价值在于<strong>实时性与交互性</strong>：真人盯着终端，要看到字符一个个吐出来、要能随时按 Ctrl-C、要能在程序问「确认吗？」时敲 y。这两种需求是<strong>本质不同的</strong>，硬用一套机制去满足另一种，只会两头别扭。opencode 没有图省事地「让模型也走 PTY」，而是<strong>诚实地为两种交互各配一套</strong>——这种「不强求统一」的克制，和第 34 课「各家缓存机制不同就别假装统一」是同一种成熟。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <p>搜索与执行，补齐了 coding agent 在「改」之外的两项基本功：</p>
  <ul>
    <li><strong>glob / grep = 两种「找」</strong>：glob 按文件名、grep 按内容（正则）；都架在 <span class="mono">Ripgrep</span> 上（快、默认尊重 .gitignore），都带 <span class="mono">limit</span> 防止结果撑爆上下文。复用权威上游（第 35 课同理）。</li>
    <li><strong>bash = 通用逃生舱</strong>：拥有宿主用户的文件/进程/网络权限，能干专用工具够不着的杂活，因而护栏最严——<strong>限时</strong>（默认 2 分/最长 10 分）、<strong>限量</strong>（stdout/stderr 各 1 MB）、<strong>双重许可</strong>（workdir + 命令）、<strong>可强制终止</strong>（detached + forceKillAfter 3 秒）、<strong>无交互 stdin</strong>。</li>
    <li><strong>能力越大、护栏越严</strong>：专用工具破坏有限、护栏轻；通用 bash 被限时/限量/限地/可中断地团团围住。超时回的是「请加大 timeout 重试」这类<strong>可操作指引</strong>（写给模型看）。</li>
    <li><strong>bash 工具 ≠ PTY</strong>：bash 经 <span class="mono">AppProcess.run</span>（spawn/child_process 批处理）跑命令；<span class="mono">pty/*</span> 是<strong>另一套</strong>给交互式终端（实时流 + 可输入）用的基础设施。两种交互模型、两套机制。</li>
  </ul>
  <p>到这里，coding agent 的三大基本功——改（第 38 课）、找（glob/grep）、跑（bash）——已成体系。下一课（第 40 课）收尾其余内置工具：<span class="mono">webfetch</span>（抓网页）、<span class="mono">websearch</span>（搜网络）、<span class="mono">question</span>（反问用户）、<span class="mono">todowrite</span>（写待办）——它们把 agent 的「手」从本地代码库，伸向了网络与人。而本课反复出现的「限量、限时、有界」，会在第 42 课「有界工具输出」被推到极致。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p>bash 的「限时跑 + 超时处理」是它最核心的护栏（简化自 bash.ts）：</p>
  <pre class="code"><span class="cm">// spawn 选项：detached 便于整组收尾，超时后给 3 秒宽限再强制结束</span>
spawn(command, { cwd, shell, stdin: <span class="st">"ignore"</span>,
  detached: process.platform !== <span class="st">"win32"</span>, forceKillAfter: Duration.<span class="fn">seconds</span>(3) })

<span class="kw">const</span> result = <span class="kw">yield*</span> appProcess.<span class="fn">run</span>(command, {
  timeout: Duration.<span class="fn">millis</span>(timeout),       <span class="cm">// 默认 2 分，最长 10 分</span>
  maxOutputBytes: MAX_CAPTURE_BYTES,         <span class="cm">// stdout 上限 1 MB</span>
  maxErrorBytes: MAX_CAPTURE_BYTES,          <span class="cm">// stderr 上限 1 MB</span>
}).pipe(Effect.<span class="fn">catchTag</span>(<span class="st">"AppProcessError"</span>,
  e =&gt; isTimeout(e) ? Effect.<span class="fn">succeed</span>(undefined) : Effect.<span class="fn">fail</span>(e)))
<span class="kw">if</span> (!result) <span class="kw">return</span> { ..., output: <span class="st">"Command exceeded timeout ... Retry with a larger timeout"</span>, timedOut: <span class="kw">true</span> }</pre>
  <p>三处细节见功力。其一，<strong>超时被「降格」成一个正常结果而非异常</strong>：<span class="mono">catchTag</span> 把「超时」这一种 <span class="mono">AppProcessError</span> 转成 <span class="mono">undefined</span>（再变成一个带 <span class="mono">timedOut:true</span> 的结构化结果），其余错误才真正失败——超时是<strong>预期内</strong>的事，不该当崩溃处理。其二，<strong>限量是「内存安全上限」</strong>：1 MB 的 <span class="mono">maxOutputBytes</span> 防的是一条 <span class="mono">cat 大文件</span> 把内存撑爆，截断后明确标 <span class="mono">truncated</span> 并附一句说明。其三，<span class="mono">timeout</span> 在 <strong>schema 层</strong>就被 <span class="mono">isLessThanOrEqualTo(MAX_TIMEOUT_MS)</span> 卡住——模型就算想传个 24 小时的超时，<strong>在参数校验关（第 36 课）就被挡下</strong>，根本进不到执行。<strong>护栏不只在运行时，也在类型/schema 层；越早拦截越好。</strong></p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>glob / grep（<span class="mono">tool/{glob,grep}.ts</span>）= 两种「找」</strong>：glob 按文件名 pattern、grep 按内容正则（+include 文件 glob）；output 文件/命中清单。<strong>都架在 <span class="mono">Ripgrep</span> 服务上</strong>（快、默认尊重 .gitignore），都带 <span class="mono">limit</span> 防结果撑爆上下文。复用权威上游而非自己手写遍历。</li>
    <li><strong>bash（<span class="mono">tool/bash.ts</span>）= 通用逃生舱</strong>：input <span class="mono">{command, workdir?, timeout?, description?}</span>，拥有宿主用户的文件/进程/网络权限。护栏：<strong>限时</strong>（DEFAULT 2 分 / MAX 10 分，schema 卡上限）、<strong>限量</strong>（stdout/stderr 各 <span class="mono">MAX_CAPTURE_BYTES</span>=1 MB）、<strong>双重 permission.assert</strong>（workdir + 命令）、<strong>detached + forceKillAfter 3 秒</strong>、<strong>stdin ignore</strong>。</li>
    <li><strong>能力越大护栏越严</strong>：专用工具护栏轻，通用 bash 被限时/限量/限地/可中断围住。超时被降格成带 <span class="mono">timedOut:true</span> 的正常结果（catchTag），回一句「加大 timeout 重试」的可操作指引。</li>
    <li><strong>bash ≠ PTY</strong>：bash 经 <span class="mono">AppProcess.run</span> → <span class="mono">ChildProcessSpawner</span>（spawn/child_process 批处理）跑命令；<span class="mono">pty/*</span>（<span class="mono">Proc.onData/write/resize</span>）是<strong>另一套</strong>给交互式终端（实时流 + 可输入、第 10 课 pty 路由、第 33 课 WebSocketTracker）用的。批处理 vs 交互，两套机制。</li>
    <li><strong>贯穿 M7 的红线</strong>：凡可能「量大」处皆有界——搜索的 limit、文件读的 offset/limit、bash 的 timeout/字节上限，都为第 42 课「有界工具输出」埋线。护栏在 schema 层就开始（越早拦越好）。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Last lesson covered the agent's four hands for changing files. But before changing, you must <strong>find</strong> what to change; many tasks also need to <strong>run a command</strong> and see results (install deps, run tests, git status). This lesson's three tools are a coding agent's other two basic skills: <strong>search</strong> and <strong>execute</strong>. <span class="mono">glob</span> (find by filename), <span class="mono">grep</span> (search by file content), <span class="mono">bash</span> (run shell commands). The first two are "<strong>eyes</strong>"—quickly locating in the codebase; the last is the "<strong>universal hand</strong>"—it can do the odd jobs the specialized tools above can't, but for that very reason has <strong>the most power and the most guardrails</strong>.</p>
<p>This lesson shows an interesting contrast: <strong>specialized vs general</strong>. glob/grep are <strong>specialized</strong> tools—making the high-frequency "search" into two fast, stable, bounded narrow interfaces (both backed by ripgrep); bash is the <strong>general escape hatch</strong>—it has "the host user's filesystem, process, and network authority," near-omnipotent, so opencode wraps it in a whole ring of seatbelts: <strong>time-limited, volume-limited, doubly-permissioned, force-terminable</strong>. I'll also clear up a common misconception—<strong>the bash tool does NOT run via "PTY (pseudo-terminal)"</strong>; PTY is separate infrastructure for "interactive terminals," a different thing from the "run a command, get results" bash tool. Clearing this up sharpens your boundary between "batch execution" and "interactive terminal."</p>

<div class="card analogy">
  <div class="tag">🔦 Analogy</div>
  Imagine the agent working in a vast code library. <strong>glob</strong> is "<strong>search by title</strong>"—"give me all <span class="mono">*.test.ts</span>," and whoosh, a list of titles. <strong>grep</strong> is "<strong>search by a phrase inside the books</strong>"—"which books contain <span class="mono">TODO: fix</span>," flipping through contents to pull out the hits. Both rely on the library's <strong>blazing-fast search machine</strong> (ripgrep), auto-skipping the shelves you said to ignore (gitignore). And <strong>bash</strong> hands the agent the <strong>keys to the whole workshop</strong>—it can run the machines, haul things, make outside calls (full filesystem, process, network authority). Precisely because this key is so heavy, the workshop door posts iron rules: <strong>each job has a time limit (force-stop on overtime), the waste it produces has a cap (truncate on overflow), you must register before starting (permission), and there's a master switch (force-cut power to terminate)</strong>. Specialized tools are like labeled precision instruments; the general bash is like a workshop needing safety protocols—<strong>the greater the power, the stricter the guardrails</strong>.
</div>

<h2>glob and grep: two ways to "find"</h2>
<p>First lay the three tools side by side, one table for their division of labor and each one's "boundary"—they all fill lesson 36's <span class="mono">Config</span> form too:</p>
<table class="t">
  <tr><th>Tool</th><th>Does what</th><th>Backed by</th><th>Key boundary</th></tr>
  <tr><td>glob</td><td>find files by filename pattern</td><td>Ripgrep</td><td>limit result cap</td></tr>
  <tr><td>grep</td><td>search by content regex (+include file glob)</td><td>Ripgrep</td><td>limit hit cap</td></tr>
  <tr><td>bash</td><td>run a shell command (full authority)</td><td>AppProcess/spawn</td><td>timeout + 1MB bytes + dual permission</td></tr>
</table>
<p>First the two search tools. They solve the same big problem—"<strong>locate in the codebase</strong>"—but with different cuts:</p>
<div class="cols">
  <div class="col"><h4>glob · find by name</h4><p>input <span class="mono">{pattern, path?, limit?}</span>, output file list. "Give me files matching <span class="mono">src/**/*.ts</span>." Asks <strong>"which files are named this."</strong></p></div>
  <div class="col"><h4>grep · search by content</h4><p>input <span class="mono">{pattern(regex), path?, include?, limit?}</span>, output hit list. "Which files have <span class="mono">useEffect</span>." Asks <strong>"which files wrote this."</strong></p></div>
</div>
<p>Both implementations are <strong>built on the <span class="mono">Ripgrep</span> service</strong>—a smart choice. ripgrep (rg) is one of the industry's acknowledged fastest code-search tools, and <strong>respects <span class="mono">.gitignore</span> by default</strong>: it won't search <span class="mono">node_modules</span>, <span class="mono">dist</span> into the results to pollute them. opencode didn't hand-write filesystem traversal then implement regex matching (slow and error-prone), but <strong>stands on ripgrep's giant shoulders</strong>, wrapping it into just two narrow tool interfaces. This is the same wisdom as lesson 35's "don't reinvent the wheel, reuse the authoritative upstream"—for "search," something others have perfected, just borrow it.</p>
<p>Another commonality is <strong>both carry <span class="mono">limit</span> (result cap)</strong>. Why does search need a cap too? Because a broad pattern (e.g. grep <span class="mono">import</span>) may hit thousands, and stuffing them all back into the conversation would <strong>instantly blow the model's context window</strong>. <span class="mono">limit</span> bounds results to a reasonable range, forcing the model to <strong>narrow with a more precise pattern or narrower path</strong> rather than scooping a whole sea at once. This, lesson 38's file-tool offset/limit paging, and lesson 42's bounded output are the same red thread running through M7: <strong>anywhere "volume could be large" must be bounded</strong>—because the model consuming the results has a limited and expensive context window.</p>

<h2>bash: the universal hand, and its ring of seatbelts</h2>
<p>Now the centerpiece <span class="mono">bash</span>. Its description has a heavy line—commands run with "<strong>the host user's filesystem, process, and network authority</strong>." In other words, <strong>what bash can do nearly equals what you yourself can do in a terminal</strong>. That's its power (the odd jobs the specialized tools can't reach, it can manage) and its danger (an <span class="mono">rm -rf</span> runs just the same). So opencode wraps bash in a whole ring of seatbelts:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">time-limited</div><div class="c-txt">default 2 min, max 10 min (≤ MAX_TIMEOUT_MS at the schema layer); timeout→clear "timed out, retry with a larger timeout"</div></div>
  <div class="cell"><div class="c-tag">volume-limited</div><div class="c-txt">stdout/stderr each 1 MB in-memory cap (MAX_CAPTURE_BYTES); overflow→truncate + a truncated notice</div></div>
  <div class="cell"><div class="c-tag">dual permission</div><div class="c-txt">one for workdir (external dir needs external_directory approval) + one for the command itself, permission.assert</div></div>
  <div class="cell"><div class="c-tag">force-terminable</div><div class="c-txt">detached launch (non-Windows) for group cleanup; forceKillAfter 3s grace then force-end</div></div>
  <div class="cell"><div class="c-tag">non-interactive</div><div class="c-txt">stdin set to ignore—the command can't turn around and ask the model for input (the model can't answer)</div></div>
</div>
<p>Connect these and a clear design intent emerges: <strong>give the strongest capability the strictest constraints</strong>. Specialized tools like glob/grep can do limited damage, with light guardrails; the "do-anything" escape hatch bash is hemmed in <strong>time-limited, volume-limited, place-limited, interruptible</strong>. Among these, <strong>the time limit</strong> is especially crucial—an <span class="mono">npm install</span> may take tens of seconds, but a mistakenly-written infinite loop runs forever; the timeout (default 2 min) leashes every command with a <strong>time belt</strong>, force-stopping on overrun, never letting one command hang the whole agent. The post-timeout handling is thoughtful too: not a dry error but "<strong>timed out; if this command was meant to run longer, retry with a larger timeout</strong>"—again an actionable guide written for the model (echoing lesson 38). The main execution flow is a chain of "resolve→permit→launch→run-with-limit→collect":</p>
<div class="flow">
  <div class="f-node">resolve workdir<br><small>relative to Location; external needs approval</small></div>
  <div class="f-arrow">permission.assert →</div>
  <div class="f-node">spawn child process<br><small>detached + configured shell</small></div>
  <div class="f-arrow">run(timeout, maxBytes) →</div>
  <div class="f-node">run time+volume bounded<br><small>timeout→timedOut; overflow→truncated</small></div>
  <div class="f-arrow">→</div>
  <div class="f-node">{exitCode, output, truncated…}<br><small>structured result back</small></div>
</div>
<p>The same chain lands in several different outcomes, and <span class="mono">output</span> faithfully encodes them all into the structured result, so the model sees at a glance "<strong>did it succeed, err, hang, or get truncated</strong>":</p>
<div class="trace">
  <div class="t-row"><span class="t-num">success</span><span class="t-txt">exitCode=0, output is the command's full output</span></div>
  <div class="t-row"><span class="t-num">nonzero exit</span><span class="t-txt">exitCode≠0 (the command errored), output includes stderr—the model judges the cause</span></div>
  <div class="t-row"><span class="t-num">timeout</span><span class="t-txt">timedOut=true, output="timed out, retry with a larger timeout"</span></div>
  <div class="t-row"><span class="t-num">output overflow</span><span class="t-txt">truncated=true, output truncated + a "capture truncated" notice</span></div>
</div>

<h2>Clarification: the bash tool ≠ a PTY terminal</h2>
<p>Here we must dispel a common confusion. You may have heard opencode has "PTY / pseudo-terminal," and guessed the bash tool runs via PTY. <strong>Actually it doesn't.</strong> Look at the source: the bash tool executes commands via <span class="mono">AppProcess.run</span>, and <span class="mono">AppProcess</span> underneath is <span class="mono">ChildProcessSpawner</span> (a cross-platform wrapper over <span class="mono">child_process</span>/spawn)—<strong>it's a batch model of "launch a child process, run to completion, collect stdout/stderr,"</strong> not a pseudo-terminal. So what's the <span class="mono">pty/*</span> module for? It's <strong>a different thing</strong>: pseudo-terminal infrastructure for "<strong>interactive terminals</strong>" (remember lesson 10's <span class="mono">pty</span>/<span class="mono">pty-connect</span> route groups, lesson 33's mention that WebSocketTracker tracks pty terminals? That's for opening a <strong>live, typeable</strong> shell session in the UI). The difference is essential:</p>
<div class="cols">
  <div class="col"><h4>bash tool (batch)</h4><p><span class="mono">spawn</span> a child process → run one command → collect stdout/stderr → done. <strong>One round trip</strong>, non-interactive, for the model.</p></div>
  <div class="col"><h4>pty module (interactive)</h4><p>A <strong>persistent pseudo-terminal</strong>: <span class="mono">onData</span> streams output, <span class="mono">write</span> feeds input, <span class="mono">resize</span> adjusts size. For a <strong>human</strong> opening a live shell.</p></div>
</div>
<p>Why does the bash tool <strong>not</strong> use PTY? Because the model needs the <strong>deterministic batch</strong> of "run one command, get the complete result," not a <strong>live stream</strong> that keeps spitting characters and may wait for your input. PTY's "streaming + typeable" is actually a burden for a model that can't be interactively prompted (which is exactly why stdin is set to ignore). <strong>Splitting "run commands for the model" and "open a terminal for a human" into two different mechanisms, each serving its own interaction model</strong>—a clear-headed division. Next time you see pty in opencode, you'll know: that's the terminal feature, not the bash tool.</p>
<p>Following this "different mechanism for different interaction model" one layer further: batch suits the model because the model's "think—act" rhythm is itself <strong>question-and-answer</strong>—it sends one command, awaits one complete result, then decides the next, exactly matching "spawn, run, collect." PTY's value is <strong>real-time and interactivity</strong>: a human watching the terminal wants to see characters spat out one by one, to press Ctrl-C anytime, to type y when the program asks "confirm?". These two needs are <strong>essentially different</strong>; forcing one mechanism to serve the other only awkwards both. opencode didn't lazily "make the model go through PTY too," but <strong>honestly fits a mechanism to each interaction</strong>—this "don't force unification" restraint is the same maturity as lesson 34's "different vendors' cache mechanisms, don't pretend they're the same."</p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>Search and execute round out a coding agent's two basic skills beyond "change":</p>
  <ul>
    <li><strong>glob / grep = two ways to "find"</strong>: glob by filename, grep by content (regex); both built on <span class="mono">Ripgrep</span> (fast, respects .gitignore by default), both carry <span class="mono">limit</span> to keep results from blowing the context. Reuse the authoritative upstream (like lesson 35).</li>
    <li><strong>bash = the general escape hatch</strong>: holds the host user's file/process/network authority, does the odd jobs specialized tools can't reach, hence the strictest guardrails—<strong>time-limited</strong> (default 2 min/max 10 min), <strong>volume-limited</strong> (stdout/stderr each 1 MB), <strong>dual permission</strong> (workdir + command), <strong>force-terminable</strong> (detached + forceKillAfter 3s), <strong>non-interactive stdin</strong>.</li>
    <li><strong>Greater power, stricter guardrails</strong>: specialized tools do limited damage, light guardrails; general bash is hemmed in time/volume/place-limited and interruptible. Timeout returns an <strong>actionable guide</strong> like "retry with a larger timeout" (written for the model).</li>
    <li><strong>bash tool ≠ PTY</strong>: bash runs commands via <span class="mono">AppProcess.run</span> (spawn/child_process batch); <span class="mono">pty/*</span> is <strong>separate</strong> infrastructure for interactive terminals (live stream + typeable). Two interaction models, two mechanisms.</li>
  </ul>
  <p>By here, the coding agent's three basic skills—change (lesson 38), find (glob/grep), run (bash)—form a system. The next lesson (40) wraps up the remaining built-in tools: <span class="mono">webfetch</span> (fetch web pages), <span class="mono">websearch</span> (web search), <span class="mono">question</span> (ask the user back), <span class="mono">todowrite</span> (write todos)—extending the agent's "hands" from the local codebase to the network and people. And this lesson's recurring "bound volume, bound time" is pushed to its extreme in lesson 42's "bounded tool output."</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p>bash's "bounded run + timeout handling" is its core guardrail (simplified from bash.ts):</p>
  <pre class="code"><span class="cm">// spawn opts: detached for group cleanup; 3s grace before force-end on timeout</span>
spawn(command, { cwd, shell, stdin: <span class="st">"ignore"</span>,
  detached: process.platform !== <span class="st">"win32"</span>, forceKillAfter: Duration.<span class="fn">seconds</span>(3) })

<span class="kw">const</span> result = <span class="kw">yield*</span> appProcess.<span class="fn">run</span>(command, {
  timeout: Duration.<span class="fn">millis</span>(timeout),       <span class="cm">// default 2 min, max 10 min</span>
  maxOutputBytes: MAX_CAPTURE_BYTES,         <span class="cm">// stdout cap 1 MB</span>
  maxErrorBytes: MAX_CAPTURE_BYTES,          <span class="cm">// stderr cap 1 MB</span>
}).pipe(Effect.<span class="fn">catchTag</span>(<span class="st">"AppProcessError"</span>,
  e =&gt; isTimeout(e) ? Effect.<span class="fn">succeed</span>(undefined) : Effect.<span class="fn">fail</span>(e)))
<span class="kw">if</span> (!result) <span class="kw">return</span> { ..., output: <span class="st">"Command exceeded timeout ... Retry with a larger timeout"</span>, timedOut: <span class="kw">true</span> }</pre>
  <p>Three details show craft. One, <strong>timeout is "demoted" to a normal result, not an exception</strong>: <span class="mono">catchTag</span> turns "timeout," one kind of <span class="mono">AppProcessError</span>, into <span class="mono">undefined</span> (then a structured result with <span class="mono">timedOut:true</span>), while other errors truly fail—timeout is an <strong>expected</strong> thing, not to be treated as a crash. Two, <strong>the volume cap is an "in-memory safety limit"</strong>: the 1 MB <span class="mono">maxOutputBytes</span> guards against a <span class="mono">cat huge-file</span> blowing memory; after truncation it clearly marks <span class="mono">truncated</span> with a note. Three, <span class="mono">timeout</span> is capped at the <strong>schema layer</strong> by <span class="mono">isLessThanOrEqualTo(MAX_TIMEOUT_MS)</span>—even if the model tries to pass a 24-hour timeout, it's <strong>stopped at the param-validation gate (lesson 36)</strong>, never reaching execution. <strong>Guardrails aren't only at runtime but at the type/schema layer too; the earlier the interception, the better.</strong></p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>glob / grep (<span class="mono">tool/{glob,grep}.ts</span>) = two ways to "find"</strong>: glob by filename pattern, grep by content regex (+include file glob); output file/hit lists. <strong>Both built on the <span class="mono">Ripgrep</span> service</strong> (fast, respects .gitignore by default), both carry <span class="mono">limit</span> to keep results from blowing the context. Reuse the authoritative upstream rather than hand-writing traversal.</li>
    <li><strong>bash (<span class="mono">tool/bash.ts</span>) = the general escape hatch</strong>: input <span class="mono">{command, workdir?, timeout?, description?}</span>, holds host user's file/process/network authority. Guardrails: <strong>time-limited</strong> (DEFAULT 2 min / MAX 10 min, schema-capped), <strong>volume-limited</strong> (stdout/stderr each <span class="mono">MAX_CAPTURE_BYTES</span>=1 MB), <strong>dual permission.assert</strong> (workdir + command), <strong>detached + forceKillAfter 3s</strong>, <strong>stdin ignore</strong>.</li>
    <li><strong>Greater power, stricter guardrails</strong>: specialized tools light, general bash hemmed in time/volume/place-limited and interruptible. Timeout demoted to a normal result with <span class="mono">timedOut:true</span> (catchTag), returning an actionable "retry with a larger timeout" guide.</li>
    <li><strong>bash ≠ PTY</strong>: bash runs commands via <span class="mono">AppProcess.run</span> → <span class="mono">ChildProcessSpawner</span> (spawn/child_process batch); <span class="mono">pty/*</span> (<span class="mono">Proc.onData/write/resize</span>) is <strong>separate</strong> infrastructure for interactive terminals (live stream + typeable, lesson 10's pty routes, lesson 33's WebSocketTracker). Batch vs interactive, two mechanisms.</li>
    <li><strong>The red thread through M7</strong>: anywhere "volume could be large" is bounded—search's limit, file-read's offset/limit, bash's timeout/byte cap, all foreshadowing lesson 42's "bounded tool output." Guardrails start at the schema layer (the earlier the interception, the better).</li>
  </ul>
</div>
""",
}
LESSON_40 = {
    "zh": r"""
<p class="lead">前两课的工具，都在 agent <strong>自己的工坊</strong>里干活——改本地文件、搜本地代码、跑本地命令。但一个真正有用的 coding agent，不能是个<strong>封死在房间里的工人</strong>。它得能<strong>往外看</strong>（查网上的最新文档、搜知识截止日之后的信息）、能<strong>向人求助</strong>（拿不准时反问用户）、还得能<strong>给自己记笔记</strong>（多步任务里写个待办、追踪进度）。这一课的四个工具，正是把 agent 的「手」从本地代码库，伸向了<strong>网络</strong>与<strong>人</strong>：<span class="mono">webfetch</span>（抓网页）、<span class="mono">websearch</span>（搜网络）、<span class="mono">question</span>（反问用户）、<span class="mono">todowrite</span>（写待办）。</p>
<p>它们看似杂，其实沿着<strong>两条新轴</strong>展开。一条是<strong>向外、伸向网络</strong>：webfetch 让 agent 读一个指定网页、websearch 让它搜整个互联网——突破「只懂本地代码」和「知识停在训练截止日」两道墙。另一条是<strong>转向人与自己</strong>：question 是少见的「<strong>反向</strong>」工具，别的工具都是 agent 把意志<strong>推向外部</strong>（改文件、跑命令），它却是<strong>从人那里把信息拉回来</strong>；todowrite 更特别，它作用的不是外部世界，而是 agent <strong>自己的状态</strong>（一份待办清单），是一块「<strong>外置的工作记忆</strong>」。看懂这两条轴，你就明白一个 agent 是怎么从「闷头干活」长成「<strong>会查、会问、会规划</strong>」的协作者。</p>

<div class="card analogy">
  <div class="tag">🪟 生活类比</div>
  如果说前两课的工具是 agent 在自己工坊里的双手，那这四个工具，是给这间工坊<strong>开了三样新东西</strong>。<strong>webfetch</strong> 像一扇<strong>能指定朝向的窗</strong>——「让我看看那个网址后面是什么」，把外面的景象（网页）取进来。<strong>websearch</strong> 像工坊里一部<strong>能问图书管理员的电话</strong>——「最近有什么关于 X 的新消息？」，问的是<strong>当下、训练截止之后</strong>的事。<strong>question</strong> 像墙上一台<strong>对讲机</strong>——拿不准、不该自己拍板时，按下去问一句「老板，这步你要 A 还是 B？」。<strong>todowrite</strong> 则是一块<strong>个人待办白板</strong>——多步的活儿，先把计划写上去，做一步划一步，自己和老板都能一眼看到进度。从「<strong>只会埋头干</strong>」，到「<strong>会往外看、会开口问、会记下来</strong>」——这四样，把一个工人变成了一个靠谱的协作者。
</div>

<h2>四个工具：两条新轴</h2>
<p>先把四个工具并排，注意它们<strong>仍在填第 36 课那张 <span class="mono">Config</span> 表</strong>，只是「手」伸的方向变了：</p>
<table class="t">
  <tr><th>工具</th><th>干什么</th><th>伸向</th><th>input 要点</th></tr>
  <tr><td>webfetch</td><td>抓取一个 URL 的内容</td><td>网络（指定页）</td><td>url, format(默认 markdown), timeout?</td></tr>
  <tr><td>websearch</td><td>搜索互联网</td><td>网络（开放搜）</td><td>query, numResults?(默认8), type?</td></tr>
  <tr><td>question</td><td>反问用户、取回答案</td><td>人（拉回信息）</td><td>questions[]（多选题）</td></tr>
  <tr><td>todowrite</td><td>写/更新会话待办清单</td><td>自己（外置记忆）</td><td>todos[]（带状态）</td></tr>
</table>
<p>这张表的「伸向」一列，是这一课的<strong>骨架</strong>。前面所有工具几乎都指向「<strong>本地文件系统</strong>」；而这四个，把方向拆成了三个全新去处——<strong>网络、人、agent 自身</strong>。一个 agent 的能力边界，很大程度上就由「它的手能伸到哪」决定：只能改本地文件的 agent，遇到「这个库最新版的 API 怎么用」就抓瞎；而能 webfetch / websearch 的 agent，能现查现学。能力的扩展，本质是<strong>「手能触及的世界」的扩展</strong>。也正因为方向不同，这四个工具触发的「信任与风险」也不同：读网络要防内容污染、问用户要打断对方、写待办只动自己——把它们按「伸向」归类，不只是好记，更暗示了各自该配怎样的边界与许可（这条线第 41 课会接上）。</p>
<div class="cols">
  <div class="col"><h4>向外 · 伸向网络</h4><p><span class="mono">webfetch</span>（读指定页）+ <span class="mono">websearch</span>（搜开放网）。突破「只懂本地」与「知识截止日」两道墙，让 agent 现查现学。</p></div>
  <div class="col"><h4>转内 · 人与自己</h4><p><span class="mono">question</span>（从人拉回决策）+ <span class="mono">todowrite</span>（写自己的待办）。让 agent 会求助、会规划，而非闷头硬扛。</p></div>
</div>

<h2>向外：webfetch 与 websearch</h2>
<p>先看伸向网络的两个。<span class="mono">webfetch</span> 抓一个 HTTP(S) URL 的内容，有个值得注意的默认：<strong>format 默认是 <span class="mono">markdown</span></strong>（可选 text / html）。为什么不默认给原始 HTML？因为网页的原始 HTML 里塞满了标签、脚本、样式——对模型来说既<strong>耗 token</strong>又<strong>难读</strong>。webfetch 默认把网页<strong>转成干净的 markdown</strong> 再给模型，正文清清爽爽。这又是「<strong>对模型用人话</strong>」的一贯思路（第 36 课 content 那一面）：不是把外部世界原样倒给模型，而是<strong>翻译成模型最好消化的形态</strong>。它当然也带 timeout 上限——抓一个慢站点不能让 agent 干等。三种 format 各有所用：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">markdown（默认）</div><div class="c-txt">HTML→干净 markdown，正文清爽、省 token，模型最好读</div></div>
  <div class="cell"><div class="c-tag">text</div><div class="c-txt">纯文本，连 markdown 标记都不要，只要字</div></div>
  <div class="cell"><div class="c-tag">html</div><div class="c-txt">原始 HTML，当模型确实要看标签结构时才用</div></div>
</div>
<p><span class="mono">websearch</span> 则搜索整个互联网，专治「<strong>知识截止日之后</strong>」的问题。这里藏着一个容易被忽略、却很重要的架构区分：</p>
<div class="cols">
  <div class="col"><h4>本地 websearch（本课这个）</h4><p>opencode 自己跑的、与供应商无关的本地工具，背后接 <strong>Exa 或 Parallel</strong> 搜索服务。在 opencode 这一侧执行。</p></div>
  <div class="col"><h4>供应商自带的 web search</h4><p>另一回事：由模型<strong>供应商</strong>提供、在<strong>供应商那一侧</strong>执行（route 拥有，回忆第 30 课 Anthropic 的 server_tool）。</p></div>
</div>
<p>换句话说，「让模型能搜网」其实有<strong>两条路</strong>：一条是 opencode 自己拿一个 Exa/Parallel key 在本地搜（这个 <span class="mono">websearch</span> 工具），另一条是直接用供应商内建的搜索（在供应商服务器上跑）。opencode 把<strong>本地这条</strong>做成一个标准工具，于是「搜网能力」不依赖于「你用的模型供应商支不支持」——又是一处「把能力下沉到自己这层、不被上游绑定」的设计（呼应第 28 课「不被供应商绑架」）。这么做的好处很实在：无论你今天用 Anthropic、明天换 Gemini，<strong>搜网这件事的行为都一致</strong>，不会因为换了供应商就时有时无、忽强忽弱；而且 opencode 能自主决定接哪家搜索后端（Exa / Parallel）、怎么调参，主动权握在自己手里。还有个小细节很见用心：websearch 的 description 里<strong>注入了「当前年份」</strong>，提醒模型「搜最新信息时带上今年」——因为模型自己的「今天」停在训练截止日，不告诉它真实年份，它可能拿着过时的年份去搜。<strong>一句话的注入，补上了模型的「时间感」。</strong></p>

<h2>转内：question 与 todowrite</h2>
<p>另外两个工具，方向掉头朝内。<span class="mono">question</span> 是整个工具集里的<strong>异类</strong>——绝大多数工具是 agent 把意志<strong>推向外部</strong>（我要改这个文件、跑这条命令），而 question 是<strong>反着来</strong>：agent 主动<strong>把问题抛给用户、等一个答案回来</strong>。它存在的意义，是让 agent 学会<strong>在该问的时候问</strong>，而不是在歧义和重大抉择前自作主张。它的设计也透着对协作 UX 的讲究：鼓励<strong>多选题</strong>（让用户点选最快），且 description 明确叮嘱模型<strong>别自己加「其他」选项</strong>——因为当 <span class="mono">custom</span> 开启（默认）时，UI 会<strong>自动</strong>补一个「输入你自己的答案」。这条「别加 Other、让 UI 加」的约定，避免了模型和 UI 各加一个、重复别扭。把 question 的几个 UX 约定列出来，能看出它对「人机协作」的细心：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">多选优先</div><div class="c-txt">尽量给选项让用户点，比让用户打字快、也更省事</div></div>
  <div class="cell"><div class="c-tag">UI 自动补 freeform</div><div class="c-txt">custom 默认开 → UI 自动加「输入自己的答案」</div></div>
  <div class="cell"><div class="c-tag">别加 Other</div><div class="c-txt">模型不要自己塞「其他」选项，免得和 UI 的 freeform 重复</div></div>
</div>
<p><span class="mono">todowrite</span> 则更哲学一点：它是个<strong>作用于 agent 自己状态</strong>的工具。它不改外部世界的任何东西，只维护「<strong>当前会话的一份结构化待办清单</strong>」（接 <span class="mono">SessionTodo</span> 服务）。模型在做多步任务时，用它<strong>写下计划、随做随更新状态</strong>。把它想成一块「<strong>外置的工作记忆</strong>」：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">写计划</div><div class="c-txt">多步任务开始，把要做的几步列成 todos（各带状态）</div></div>
  <div class="cell"><div class="c-tag">追进度</div><div class="c-txt">每做完一步，更新对应 todo 的状态（pending→done…）</div></div>
  <div class="cell"><div class="c-tag">不忘事</div><div class="c-txt">长任务里靠这份清单锚住「还剩哪些」，模型与用户都看得见</div></div>
</div>
<p>为什么一个 agent 需要「写待办」这种工具？因为在一个动辄十几步的长任务里，模型很容易<strong>做着做着忘了全局</strong>——它的注意力被当前这一步占满，可能漏掉后面该做的。todowrite 把「计划与进度」<strong>从模型易失的脑内，挪到一份持久、可见的清单上</strong>，既帮模型自己不跑偏，也让用户能实时看到「它打算干什么、做到哪了」。这其实是把人类做复杂工作时「<strong>列个清单、做一项划一项</strong>」的朴素智慧，做成了 agent 的一个工具。<strong>一个会列待办、会追踪进度的 agent，远比一个只会一头扎进去的 agent 靠谱。</strong>更深一层看，todowrite 还把 agent 的「思路」<strong>外化成了可观测的产物</strong>：用户不必猜「它到底打算怎么做」，而是直接看那份清单——这种<strong>透明</strong>本身就是信任的基础。一个把计划摊在明处、做一步划一步的 agent，让人敢把更复杂的活儿交给它。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <p>这四个工具，把 agent 的能力边界从「本地代码库」沿两条新轴大幅外推：</p>
  <ul>
    <li><strong>向外·网络</strong>：<span class="mono">webfetch</span>（抓指定 URL，<strong>默认转 markdown</strong> 喂给模型、带 timeout）+ <span class="mono">websearch</span>（搜开放网，破知识截止日；<strong>本地 Exa/Parallel</strong> 工具，区别于供应商自带的 server-side 搜索；description 注入当前年份）。</li>
    <li><strong>转内·人与自己</strong>：<span class="mono">question</span>（<strong>反向</strong>工具，从用户拉回答案；多选优先、UI 自动补 freeform、别加 Other）+ <span class="mono">todowrite</span>（作用于 agent 自身状态，维护会话待办，是「外置工作记忆」）。</li>
    <li><strong>仍是同一张 Config 表</strong>：四个工具各声明 input/output schema + execute，套权限——再次印证第 36 课「一张表、各自填空」，只是「手」伸向了网络、人、自身。</li>
    <li><strong>能力 = 手能触及的世界</strong>：只会改本地文件的 agent 遇到「最新 API 怎么用」就抓瞎；能查、能问、能规划的 agent，才是个靠谱协作者。</li>
  </ul>
  <p>到这里，opencode 的<strong>内置工具全家福</strong>就集齐了：文件（read/write/edit/apply-patch）、搜索执行（glob/grep/bash）、网络与协作（webfetch/websearch/question/todowrite），外加后面第 43 课的 skill。下一课（第 41 课）我们回头处理一条贯穿所有工具的横切线——<strong>权限系统</strong>：前面每个工具都出现过的 <span class="mono">withPermission</span> / <span class="mono">permission.assert</span>，到底是怎么评估、怎么把「这步准不准做」的决定权交还给用户的。工具讲完「能做什么」，权限讲「准做什么」——前者是能力，后者是边界，二者合起来才是一个既有用又可控的 agent。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p><span class="mono">webfetch</span> 的 format 默认值用了一个优雅的 schema 写法（简化自 webfetch.ts）：</p>
  <pre class="code"><span class="cm">// format 三选一，解码时缺省自动填 "markdown"</span>
format: Schema.<span class="fn">Literals</span>([<span class="st">"text"</span>, <span class="st">"markdown"</span>, <span class="st">"html"</span>])
  .pipe(Schema.<span class="fn">withDecodingDefault</span>(() =&gt; <span class="st">"markdown"</span>))

<span class="cm">// websearch：把当前年份写进给模型的 description</span>
description = <span class="st">`...The current year is ${'$'}{new Date().getFullYear()}. Use this year when searching for recent information...`</span></pre>
  <p>两处都体现了「<strong>把对模型的体贴写进定义里</strong>」。<span class="mono">withDecodingDefault</span> 让模型<strong>可以不传 format</strong>——不传就当 markdown，省去模型每次都要想「我要什么格式」的负担，默认就给它最好消化的那种。而 websearch 把 <span class="mono">new Date().getFullYear()</span> 拼进 description，是在<strong>每次构建工具定义时</strong>动态算出真实年份注进去——模型的训练知识有「时间盲区」，它不知道「现在是哪年」，这一句注入就把这个盲区补上了。<strong>这些细节都不改变工具「能做什么」，却显著改善模型「用得好不好」</strong>——好的工具，不只给模型能力，还替模型把「怎么用好」想在前面。这正是「工具的用户是个模型」这一前提，催生出的一整套体贴。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>四个工具沿两条新轴外推 agent 能力</strong>（<span class="mono">tool/{webfetch,websearch,question,todowrite}.ts</span>），全是第 36 课 Config 表的不同填法。</li>
    <li><strong>webfetch</strong>：抓 HTTP(S) URL，<strong>format 默认 markdown</strong>（text/html 可选）——把网页转成模型好消化的干净正文，而非原始 HTML；带 timeout 上限。</li>
    <li><strong>websearch</strong>：搜开放网破「知识截止日」。是 opencode 的<strong>本地工具</strong>（背后 <strong>Exa/Parallel</strong>），区别于「供应商自带、在供应商侧执行」的 web search——「搜网能力」不被模型供应商绑定。description <strong>注入当前年份</strong>补模型的时间盲区。</li>
    <li><strong>question</strong>：少见的<strong>反向</strong>工具，从用户拉回答案（处理歧义/重大抉择）。多选优先；<span class="mono">custom</span> 默认开时 UI <strong>自动补 freeform</strong>，故叮嘱模型<strong>别自己加「Other」</strong>。</li>
    <li><strong>todowrite</strong>：作用于 <strong>agent 自身状态</strong>（接 <span class="mono">SessionTodo</span>），维护会话待办、随做随更新状态——一块「<strong>外置工作记忆</strong>」，帮长任务里的模型不忘全局、让用户看见进度。能查/能问/能规划，是靠谱协作者的标志。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">The prior two lessons' tools all worked in the agent's <strong>own workshop</strong>—changing local files, searching local code, running local commands. But a truly useful coding agent can't be a <strong>worker sealed in a room</strong>. It must be able to <strong>look outward</strong> (check the latest docs online, search for info past its knowledge cutoff), <strong>ask for help</strong> (ask the user back when unsure), and <strong>take notes for itself</strong> (write todos in multi-step tasks, track progress). This lesson's four tools extend the agent's "hands" from the local codebase to the <strong>network</strong> and to <strong>people</strong>: <span class="mono">webfetch</span> (fetch web pages), <span class="mono">websearch</span> (web search), <span class="mono">question</span> (ask the user back), <span class="mono">todowrite</span> (write todos).</p>
<p>They look miscellaneous but unfold along <strong>two new axes</strong>. One is <strong>outward, toward the network</strong>: webfetch lets the agent read a specific web page, websearch lets it search the whole internet—breaking through the two walls of "only knows local code" and "knowledge frozen at training cutoff." The other is <strong>turning toward people and self</strong>: question is the rare "<strong>reverse</strong>" tool—all other tools push the agent's will <strong>outward</strong> (change files, run commands), but it <strong>pulls info back from a person</strong>; todowrite is even more special, acting not on the external world but on the agent's <strong>own state</strong> (a todo list), a piece of "<strong>externalized working memory</strong>." Grasp these two axes and you'll understand how an agent grows from "head-down worker" into a collaborator who <strong>can search, ask, and plan</strong>.</p>

<div class="card analogy">
  <div class="tag">🪟 Analogy</div>
  If the prior lessons' tools are the agent's hands in its own workshop, these four open <strong>three new things</strong> for that workshop. <strong>webfetch</strong> is like a <strong>window you can aim</strong>—"let me see what's behind that URL," bringing the outside view (a web page) in. <strong>websearch</strong> is like a <strong>phone to ask the librarian</strong>—"any recent news on X?", asking about the <strong>present, past the training cutoff</strong>. <strong>question</strong> is like an <strong>intercom on the wall</strong>—when unsure, when you shouldn't decide alone, press it and ask "boss, A or B for this step?". <strong>todowrite</strong> is a <strong>personal to-do whiteboard</strong>—for multi-step work, write the plan up, check off as you go, so you and the boss can see progress at a glance. From "<strong>only head-down working</strong>" to "<strong>can look out, can speak up, can write down</strong>"—these four turn a worker into a reliable collaborator.
</div>

<h2>Four tools: two new axes</h2>
<p>First lay the four side by side, noting they <strong>still fill lesson 36's <span class="mono">Config</span> form</strong>, only the "hand" reaches a new direction:</p>
<table class="t">
  <tr><th>Tool</th><th>Does what</th><th>Reaches toward</th><th>input gist</th></tr>
  <tr><td>webfetch</td><td>fetch a URL's content</td><td>network (specific page)</td><td>url, format(default markdown), timeout?</td></tr>
  <tr><td>websearch</td><td>search the internet</td><td>network (open search)</td><td>query, numResults?(default 8), type?</td></tr>
  <tr><td>question</td><td>ask the user, get answers back</td><td>people (pull info back)</td><td>questions[] (multiple choice)</td></tr>
  <tr><td>todowrite</td><td>write/update the session todo list</td><td>self (externalized memory)</td><td>todos[] (with status)</td></tr>
</table>
<p>This table's "reaches toward" column is this lesson's <strong>skeleton</strong>. Almost all prior tools pointed at the "<strong>local filesystem</strong>"; these four split the direction into three brand-new destinations—<strong>network, people, the agent itself</strong>. An agent's capability boundary is largely set by "where its hands can reach": an agent that can only change local files is stumped by "how do I use this library's latest API"; an agent that can webfetch / websearch can look it up on the fly. Extending capability is essentially extending <strong>"the world the hands can touch."</strong> And because the directions differ, the "trust and risk" these four trigger also differ: reading the network must guard against content poisoning, asking the user interrupts them, writing todos only touches the self—classifying them by "reaches toward" isn't just mnemonic but hints at what boundary and permission each deserves (lesson 41 picks up this thread).</p>
<div class="cols">
  <div class="col"><h4>Outward · toward the network</h4><p><span class="mono">webfetch</span> (read a specific page) + <span class="mono">websearch</span> (search the open net). Breaking the "only knows local" and "knowledge cutoff" walls, letting the agent look up on the fly.</p></div>
  <div class="col"><h4>Inward · people and self</h4><p><span class="mono">question</span> (pull a decision from a person) + <span class="mono">todowrite</span> (write its own todos). Letting the agent ask for help and plan, rather than tough it out head-down.</p></div>
</div>

<h2>Outward: webfetch and websearch</h2>
<p>First the two reaching toward the network. <span class="mono">webfetch</span> fetches an HTTP(S) URL's content, with a noteworthy default: <strong>format defaults to <span class="mono">markdown</span></strong> (text / html optional). Why not default to raw HTML? Because a page's raw HTML is stuffed with tags, scripts, styles—both <strong>token-costly</strong> and <strong>hard to read</strong> for the model. webfetch by default <strong>converts the page to clean markdown</strong> before giving it to the model, the body crisp. This is again the consistent "<strong>plain language for the model</strong>" thinking (lesson 36's content side): not dumping the external world raw to the model, but <strong>translating it into the form the model digests best</strong>. It carries a timeout cap too—fetching a slow site shouldn't leave the agent waiting. The three formats each have their use:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">markdown (default)</div><div class="c-txt">HTML→clean markdown, crisp body, token-saving, best for the model to read</div></div>
  <div class="cell"><div class="c-tag">text</div><div class="c-txt">plain text, not even markdown marks, just the words</div></div>
  <div class="cell"><div class="c-tag">html</div><div class="c-txt">raw HTML, for when the model really needs to see the tag structure</div></div>
</div>
<p><span class="mono">websearch</span> searches the whole internet, specially treating the "<strong>past knowledge cutoff</strong>" problem. Hidden here is an easy-to-miss but important architectural distinction:</p>
<div class="cols">
  <div class="col"><h4>local websearch (this lesson's)</h4><p>opencode's own, provider-independent local tool, backed by <strong>Exa or Parallel</strong> search services. Executes on opencode's side.</p></div>
  <div class="col"><h4>provider-hosted web search</h4><p>A different thing: provided by the model <strong>provider</strong>, executing on the <strong>provider's side</strong> (route-owned, recall lesson 30's Anthropic server_tool).</p></div>
</div>
<p>In other words, "letting the model search the web" actually has <strong>two paths</strong>: one is opencode taking an Exa/Parallel key and searching locally (this <span class="mono">websearch</span> tool), the other is using the provider's built-in search (running on the provider's server). opencode makes <strong>the local path</strong> a standard tool, so "web-search capability" doesn't depend on "whether your model provider supports it"—again a design of "sink the capability to your own layer, not bound by the upstream" (echoing lesson 28's "not held hostage by the provider"). The benefit is concrete: whether you use Anthropic today or switch to Gemini tomorrow, <strong>web search's behavior stays consistent</strong>, not flickering on/off or strong/weak with the provider switch; and opencode can independently decide which search backend (Exa / Parallel) to use and how to tune it, keeping the initiative in its own hands. One more thoughtful detail: websearch's description <strong>injects "the current year"</strong>, reminding the model "include this year when searching for recent info"—because the model's own "today" is frozen at the training cutoff, and without being told the real year, it may search with a stale year. <strong>A one-line injection fills in the model's "sense of time."</strong></p>

<h2>Inward: question and todowrite</h2>
<p>The other two tools turn inward. <span class="mono">question</span> is the <strong>oddball</strong> of the whole toolset—the vast majority of tools push the agent's will <strong>outward</strong> (I want to change this file, run this command), but question goes <strong>the reverse</strong>: the agent proactively <strong>throws a question to the user and awaits an answer</strong>. Its reason for being is to teach the agent to <strong>ask when it should</strong>, rather than deciding alone before ambiguity and major choices. Its design shows care for collaboration UX too: it encourages <strong>multiple choice</strong> (fastest for the user to click), and the description explicitly tells the model <strong>not to add its own "Other" option</strong>—because when <span class="mono">custom</span> is on (default), the UI <strong>auto-adds</strong> a "type your own answer." This "don't add Other, let the UI add it" convention avoids the model and UI each adding one, duplicate and awkward. Listing question's UX conventions shows its care for "human-machine collaboration":</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">multiple choice first</div><div class="c-txt">give options for the user to click where possible, faster than typing, easier too</div></div>
  <div class="cell"><div class="c-tag">UI auto-adds freeform</div><div class="c-txt">custom on by default → UI auto-adds "type your own answer"</div></div>
  <div class="cell"><div class="c-tag">don't add Other</div><div class="c-txt">the model shouldn't stuff its own "Other," lest it duplicate the UI's freeform</div></div>
</div>
<p><span class="mono">todowrite</span> is more philosophical: a tool acting <strong>on the agent's own state</strong>. It changes nothing in the external world, only maintaining "<strong>a structured todo list for the current session</strong>" (backed by the <span class="mono">SessionTodo</span> service). In multi-step tasks the model uses it to <strong>write down the plan, updating statuses as it goes</strong>. Think of it as a piece of "<strong>externalized working memory</strong>":</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">write the plan</div><div class="c-txt">multi-step task starts, list the steps as todos (each with status)</div></div>
  <div class="cell"><div class="c-tag">track progress</div><div class="c-txt">after each step, update the corresponding todo's status (pending→done…)</div></div>
  <div class="cell"><div class="c-tag">don't forget</div><div class="c-txt">in long tasks, anchor "what's left" via this list, visible to model and user</div></div>
</div>
<p>Why does an agent need a "write todos" tool? Because in a long task of a dozen-plus steps, the model easily <strong>forgets the big picture mid-work</strong>—its attention is consumed by the current step, possibly missing what's due later. todowrite moves "plan and progress" <strong>from the model's volatile mind to a persistent, visible list</strong>, helping the model stay on track and letting the user see in real time "what it plans to do, where it's gotten." This is essentially making the humble wisdom of "list it, check off as you go" into an agent tool. <strong>An agent that lists todos and tracks progress is far more reliable than one that only dives in head-first.</strong> Deeper still, todowrite <strong>externalizes the agent's "thinking" into an observable artifact</strong>: the user needn't guess "how exactly does it plan to do this," but looks straight at that list—this <strong>transparency</strong> is itself the basis of trust. An agent that lays its plan in the open, checking off step by step, makes people dare to hand it more complex work.</p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>These four tools push the agent's capability boundary far beyond "the local codebase" along two new axes:</p>
  <ul>
    <li><strong>Outward · network</strong>: <span class="mono">webfetch</span> (fetch a specific URL, <strong>default-converts to markdown</strong> for the model, with timeout) + <span class="mono">websearch</span> (search the open net, breaking the knowledge cutoff; a <strong>local Exa/Parallel</strong> tool, distinct from the provider's own server-side search; description injects the current year).</li>
    <li><strong>Inward · people and self</strong>: <span class="mono">question</span> (a <strong>reverse</strong> tool, pulling answers from the user; multiple-choice first, UI auto-adds freeform, don't add Other) + <span class="mono">todowrite</span> (acts on the agent's own state, maintaining session todos, an "externalized working memory").</li>
    <li><strong>Still the same Config form</strong>: each tool declares input/output schema + execute, wrapped in permission—again confirming lesson 36's "one form, each fills blanks," only the "hand" reaches toward network, people, self.</li>
    <li><strong>Capability = the world the hands can touch</strong>: an agent that can only change local files is stumped by "how to use the latest API"; an agent that can search, ask, and plan is a reliable collaborator.</li>
  </ul>
  <p>By here, opencode's <strong>built-in tool family</strong> is complete: file (read/write/edit/apply-patch), search & exec (glob/grep/bash), network & collaboration (webfetch/websearch/question/todowrite), plus lesson 43's skill later. The next lesson (41) turns back to a cross-cutting line running through all tools—the <strong>permission system</strong>: the <span class="mono">withPermission</span> / <span class="mono">permission.assert</span> appearing in every tool above—how it evaluates, and how it hands the "may this step be done" decision back to the user. Tools cover "what can be done," permissions cover "what's allowed"—the former is capability, the latter the boundary; together they make an agent both useful and controllable.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p><span class="mono">webfetch</span>'s format default uses an elegant schema idiom (simplified from webfetch.ts):</p>
  <pre class="code"><span class="cm">// format three-way; on decode, the default fills "markdown" automatically</span>
format: Schema.<span class="fn">Literals</span>([<span class="st">"text"</span>, <span class="st">"markdown"</span>, <span class="st">"html"</span>])
  .pipe(Schema.<span class="fn">withDecodingDefault</span>(() =&gt; <span class="st">"markdown"</span>))

<span class="cm">// websearch: write the current year into the model-facing description</span>
description = <span class="st">`...The current year is ${'$'}{new Date().getFullYear()}. Use this year when searching for recent information...`</span></pre>
  <p>Both embody "<strong>write the care for the model into the definition</strong>." <span class="mono">withDecodingDefault</span> lets the model <strong>omit format</strong>—omit it and it's markdown, sparing the model the burden of thinking "which format do I want" each time, defaulting to the most digestible. And websearch splicing <span class="mono">new Date().getFullYear()</span> into the description dynamically computes the real year <strong>each time the tool definition is built</strong>—the model's training knowledge has a "time blind spot," it doesn't know "what year it is now," and this one injection fills that blind spot. <strong>These details change nothing about "what the tool can do," yet markedly improve "how well the model uses it"</strong>—a good tool gives the model not just capability but also thinks ahead about "how to use it well" for the model. This is the whole set of thoughtfulness born from the premise "the tool's user is a model."</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>Four tools push the agent's capability along two new axes</strong> (<span class="mono">tool/{webfetch,websearch,question,todowrite}.ts</span>), all different fillings of lesson 36's Config form.</li>
    <li><strong>webfetch</strong>: fetch an HTTP(S) URL, <strong>format defaults to markdown</strong> (text/html optional)—converting the page to model-digestible clean body, not raw HTML; carries a timeout cap.</li>
    <li><strong>websearch</strong>: search the open net, breaking the "knowledge cutoff." It's opencode's <strong>local tool</strong> (backed by <strong>Exa/Parallel</strong>), distinct from "provider's own, executing provider-side" web search—"web-search capability" not bound to the model provider. The description <strong>injects the current year</strong> to fill the model's time blind spot.</li>
    <li><strong>question</strong>: the rare <strong>reverse</strong> tool, pulling answers from the user (handling ambiguity/major choices). Multiple-choice first; with <span class="mono">custom</span> on by default the UI <strong>auto-adds freeform</strong>, so it tells the model <strong>not to add "Other."</strong></li>
    <li><strong>todowrite</strong>: acts on the <strong>agent's own state</strong> (backed by <span class="mono">SessionTodo</span>), maintaining session todos, updating status as it goes—an "<strong>externalized working memory</strong>" helping the model in long tasks not forget the big picture and letting the user see progress. Can-search/ask/plan is the mark of a reliable collaborator.</li>
  </ul>
</div>
""",
}
LESSON_41 = wip('权限系统', 'Permissions')
LESSON_42 = wip('有界工具输出', 'Bounded tool output')
LESSON_43 = wip('Skills 系统', 'The skills system')
