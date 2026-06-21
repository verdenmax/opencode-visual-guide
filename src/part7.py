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
LESSON_37 = wip('工具注册表', 'The tool registry')
LESSON_38 = wip('文件工具', 'File tools')
LESSON_39 = wip('搜索与执行工具', 'Search & exec tools')
LESSON_40 = wip('其他内置工具', 'Other built-in tools')
LESSON_41 = wip('权限系统', 'Permissions')
LESSON_42 = wip('有界工具输出', 'Bounded tool output')
LESSON_43 = wip('Skills 系统', 'The skills system')
