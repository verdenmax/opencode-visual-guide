"""Part 6 (Part 6 · LLM Layer) content. Placeholders until M6 fills them in."""
from placeholder import wip

LESSON_28 = {
    "zh": r"""
<p class="lead">第四部分那台 agent 循环，每一轮都调一句 <span class="mono">llm.stream(request)</span>，向模型请教一次。第六部分，我们就钻进这<strong>一句调用的背后</strong>，看 opencode 怎么和那些<strong>各说各话</strong>的大模型供应商打交道——Anthropic、OpenAI、Gemini、Bedrock、Copilot…… 每一家的 API <strong>方言都不一样</strong>：消息怎么排、工具怎么声明、流式响应怎么切块，全不相同。可 opencode 的 core，<strong>从头到尾只会说一种话</strong>。这是怎么做到的？答案是一整套<strong>翻译系统</strong>——这一课先建立总图：core 说<strong>一种规范语言</strong>，一层<strong>协议适配器</strong>负责把它翻译成各家方言、再把各家的回话翻译回来。读懂这张图，你就抓住了整个第六部分的骨架。</p>
<p>为什么「对接多家模型」值得一整个部分？因为这是一个被严重低估的脏活、累活。每家供应商的 API 都在<strong>各自演化</strong>：字段命名不同、工具调用的协议不同、错误格式不同、流式分块的粒度不同，还时不时改版。如果让 core 的业务逻辑<strong>直接</strong>去迁就这些差异，那 core 就会被各家方言的细节<strong>腐蚀得千疮百孔</strong>——到处是 <span class="mono">if (provider === "anthropic") ... else if ...</span> 的丑陋分支。opencode 的对策，是经典的<strong>「反腐层」</strong>思想：在 core 和外部供应商之间，砌一道<strong>翻译墙</strong>，墙内永远是干净的规范语言，墙外的脏乱差，全被挡在适配器那一层。这一课，就看这道墙的总体结构。</p>

<div class="card analogy">
  <div class="tag">🌐 生活类比</div>
  把 opencode 的 core 想成一位<strong>只说母语的总指挥</strong>，他要和五个<strong>各说不同方言</strong>的承包商谈生意（Anthropic、OpenAI、Gemini…）。最笨的办法，是让总指挥自己去学五种方言——他会被这些琐碎的语言细节<strong>累垮、也带偏</strong>。聪明的办法，是给他配一队<strong>同声传译</strong>（协议适配器）：总指挥永远只用母语下达需求（规范的 <span class="mono">LLMRequest</span>），传译把它<strong>翻成对应承包商的方言</strong>发过去；承包商用方言回话，传译再<strong>翻回母语</strong>（规范的 <span class="mono">LLMEvent</span>）递给总指挥。总指挥<strong>自始至终只需说一种话</strong>，五家方言的脏活累活，全在传译那一层消化掉。哪天来了第六家承包商？再加一名传译就行，总指挥一个字都不用改。这队传译，就是 opencode 的 LLM 协议层。
</div>

<h2>一种规范语言：LLMRequest 与 LLMEvent</h2>
<p>这套翻译系统能成立，全靠 core 和适配器之间约定了<strong>一种规范的「中间语言」</strong>。出去的方向，是 <span class="mono">LLMRequest</span>——一个<strong>统一的请求对象</strong>，把「我想问什么」表达成与任何供应商<strong>无关</strong>的形态：</p>
<div class="cellgroup">
  <div class="cell"><div class="k">system</div><div class="v">系统提示（基线 + 中途更新，第五部分）</div></div>
  <div class="cell"><div class="k">messages</div><div class="v">规范化的对话消息</div></div>
  <div class="cell"><div class="k">tools / toolChoice</div><div class="v">可用工具与选择策略</div></div>
  <div class="cell"><div class="k">generation</div><div class="v">温度、最大 token 等生成参数</div></div>
  <div class="cell"><div class="k">providerOptions</div><div class="v">少数确实供应商相关的逃生舱</div></div>
</div>
<p>回来的方向，是 <span class="mono">LLMEvent</span> 的流——模型的响应被翻译成一串<strong>统一的事件</strong>：文字块、推理块、工具调用、用量统计、错误……还记得第 17 课循环里那句 <span class="mono">llm.stream(request).pipe(Stream.runForEach(event =&gt; ...))</span> 吗？它消费的 <span class="mono">event</span>，正是这种规范化的 <span class="mono">LLMEvent</span>。<strong>无论底层是 Anthropic 还是 Gemini，循环看到的事件长一个样</strong>——这正是「翻译墙」的全部价值：墙内的 agent 循环，<strong>对供应商一无所知、也无需知道</strong>。</p>
<p>停下来体会「一种规范语言」这件事的分量。它的本质，是在 core 和外部世界之间，<strong>钉死一份双方都认的契约</strong>：core 承诺「我永远按这个形状提需求、按这个形状收响应」，适配器承诺「无论外面多乱，我都把它整理成这个形状」。一旦这份契约立住，两边就能<strong>各自独立地演化</strong>：core 想加一种新的工具调用方式，只需在规范里加一笔，不必管十几家供应商怎么实现；某家供应商改了 API，只需改它那个适配器，core 浑然不觉。<strong>规范语言不是一种限制，而是一种解耦的自由</strong>——它让「业务怎么演化」和「供应商怎么演化」这两件本会互相拖累的事，彻底分了家。你会发现，这和第 12 课「用 OpenAPI 规范解耦前后端」是<strong>同一种智慧</strong>：中间立一份机器/双方都认的契约，两端就都获得了不被对方绑架的自由。</p>
<div class="flow">
  <div class="node">core / agent 循环<span class="sub">只说规范语</span></div>
  <div class="arrow">LLMRequest →</div>
  <div class="node">协议适配器<span class="sub">翻译墙</span></div>
  <div class="arrow">各家方言 →</div>
  <div class="node">某供应商<span class="sub">Anthropic/OpenAI…</span></div>
</div>

<h2>两个分层：协议 vs 供应商</h2>
<p>翻译墙内部，opencode 又切了一刀，分成<strong>两个清晰的层次</strong>：<strong>协议（protocol）</strong>和<strong>供应商（provider）</strong>。这两个词常被混为一谈，但 opencode 把它们分得很开——理解这个区分，是读懂这一层的钥匙。打个比方：协议像「<strong>插头的制式</strong>」（两脚、三脚、英标、欧标），供应商像「<strong>具体的某台电器</strong>」。同一种插头制式能插一大堆电器，同一台电器（双频）也可能支持两种制式——制式和电器，本就该分开谈。</p>
<div class="cols">
  <div class="col"><h4>协议 = 一种「线缆格式」</h4><p>规定请求/响应在网线上<strong>具体长什么样</strong>：字段怎么命名、工具怎么编码、流怎么分块。opencode 有 <strong>6 种</strong>：Anthropic Messages、OpenAI Chat、OpenAI Responses、OpenAI-Compatible、Gemini、Bedrock Converse。</p></div>
  <div class="col"><h4>供应商 = 一个「具体厂商」</h4><p>一个能真正连上的服务：用<strong>哪种协议</strong> + 怎么认证 + 连哪个端点。如 anthropic、openai、google、bedrock、azure、github-copilot、openrouter、xai…</p></div>
</div>
<p>这一刀切得极妙，因为<strong>协议和供应商是「多对多」的</strong>。一个协议能服务多个供应商：OpenAI Chat 这套协议，不只 OpenAI 自己用，<strong>一大票「OpenAI 兼容」的厂商</strong>（OpenRouter、xAI、各种本地模型……）都借它说话。反过来，一个供应商也可能支持多种协议：OpenAI 自己就既有老的 Chat、又有新的 Responses。把「线缆格式」（协议）和「具体厂商」（供应商）<strong>解耦</strong>，opencode 就能用 <strong>6 种协议</strong>，<strong>复用</strong>地覆盖十几家供应商——而不是为每一家从头写一套。<strong>少量协议、大量复用</strong>，这正是这套分层最划算的地方。</p>
<p>为什么不干脆「一个供应商一套适配器」、省去「协议」这层抽象？因为那样会有大量<strong>重复</strong>。OpenRouter、xAI、本地的 Ollama，它们的 API 形态几乎和 OpenAI 一模一样——如果按供应商各写一套，就是把同一套「OpenAI 方言翻译」抄了三四遍，改一处就要改三四处。opencode 把「方言」抽出来单独成「协议」，正是看准了「<strong>形态相同的供应商，本质共享同一种线缆格式</strong>」。于是供应商那一层变得极薄——它几乎只剩「我用哪种协议、怎么认证、连哪个端点」这三件事，真正费劲的「翻译」逻辑，全沉淀在为数不多的协议里复用。<strong>把重复的部分往下沉、把易变的部分往上提</strong>，是分层设计永恒的母题，这里又见一例。</p>

<h2>翻译墙挡住了什么</h2>
<p>要体会这道墙的价值，不妨设想<strong>没有它</strong>会怎样。假如 agent 循环直接去调各家的 SDK，那么「发一条带工具调用的消息」这件事，就得在 core 里写成一团乱麻：Anthropic 的工具放在 <span class="mono">tools</span> 数组、用 <span class="mono">input_schema</span>；OpenAI 的放在 <span class="mono">functions</span>（或新版的 <span class="mono">tools</span>）、用 <span class="mono">parameters</span>；Gemini 又是另一套 <span class="mono">functionDeclarations</span>…… core 的每一处「调模型」，都会长出一片 <span class="mono">if (provider === ...)</span> 的藤蔓，缠死在各家方言的细节里。更糟的是，哪天某家改版，你得满 core 去找、去改。</p>
<div class="cols">
  <div class="col"><h4>❌ 没有翻译墙</h4><p>core 直接对接各家 SDK。每处「调模型」都 if-else 分供应商；各家方言细节腐蚀业务逻辑；某家改版要满 core 改；加新供应商要动 core。</p></div>
  <div class="col"><h4>✅ 有翻译墙</h4><p>core 只说规范语。供应商差异全锁在适配器一层；某家改版只改它自己那个 protocol；加新供应商=加一个适配器，core 一字不动。</p></div>
</div>
<p>这正是「<strong>反腐层</strong>」之所以叫这个名字的原因：它防的，是外部世界的<strong>混乱与多变，腐蚀进你干净的核心</strong>。墙内的 agent 循环，永远活在一个「只有一种模型、一种请求、一种事件」的<strong>简洁世界</strong>里——这个简洁，不是因为现实简单，而是因为有一层适配器，<strong>替它把现实的复杂全扛走了</strong>。你读第四部分时之所以从没被「这是哪家模型」打扰过，正是这道墙在默默工作的证明。</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">agent 循环：llm.stream(规范 LLMRequest)</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">路由挑中某供应商 → 该供应商指定的 protocol</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">protocol.encode：规范请求 → 这家的方言 JSON，发出去</span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">供应商流式回话（这家的方言分块）</span></div>
  <div class="t-row"><span class="t-num">5</span><span class="t-txt">protocol.decode：方言分块 → 规范 LLMEvent 流，交回循环</span></div>
</div>

<h2>少量协议，覆盖众多供应商</h2>
<p>再把「协议 vs 供应商」这层关系，用具体的数字钉清楚。opencode 一共维护 <strong>6 种协议</strong>，却用它们覆盖了<strong>十几家供应商</strong>：</p>
<div class="cellgroup">
  <div class="cell"><div class="k">Anthropic Messages</div><div class="v">服务 Anthropic（Claude）</div></div>
  <div class="cell"><div class="k">OpenAI Chat / Responses</div><div class="v">服务 OpenAI 自己（新旧两套）</div></div>
  <div class="cell"><div class="k">OpenAI-Compatible</div><div class="v">服务一大票兼容厂商：OpenRouter、xAI、本地模型…</div></div>
  <div class="cell"><div class="k">Gemini</div><div class="v">服务 Google Gemini</div></div>
  <div class="cell"><div class="k">Bedrock Converse</div><div class="v">服务 AWS Bedrock 上的各种模型</div></div>
</div>
<p>看出这个杠杆了吗？<strong>OpenAI-Compatible</strong> 这一种协议，一己之力就接住了「市面上所有自称兼容 OpenAI」的厂商——它们的数量还在不断增长，可 opencode <strong>一行新协议代码都不用加</strong>。这就是「把线缆格式抽象成协议」的复利：行业里「OpenAI 兼容」已经成了事实标准，opencode 只要实现一次这个标准，就免费搭上了整个生态。<strong>用最少的协议、撬动最多的供应商</strong>——这层分层的经济性，在这个数字对比里一目了然。它也解释了为什么第 31 课要专门花一课讲 OpenAI 协议：它不只服务一家，而是服务<strong>半个生态</strong>。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景·第六部分序幕</div>
  <p>这一课为第六部分立了总纲。整个 LLM 层，会在接下来几课层层展开：</p>
  <ul>
    <li><strong>第 28 课·本课</strong>：总图——core 说规范语（<span class="mono">LLMRequest</span>/<span class="mono">LLMEvent</span>），协议适配器当「翻译墙」；协议 vs 供应商两分层。</li>
    <li><strong>第 29 课</strong>：协议适配器的<strong>通用骨架</strong>——一个 protocol 到底要实现哪些「翻译」职责。</li>
    <li><strong>第 30-32 课</strong>：三大家方言细拆——<strong>Anthropic</strong>（第 30）、<strong>OpenAI</strong> Chat/Responses（第 31）、<strong>Gemini 与 Bedrock</strong>（第 32）。</li>
    <li><strong>第 33-35 课</strong>：路由与传输（第 33）、流式与缓存（第 34）、模型解析与 Copilot（第 35）。</li>
  </ul>
  <p>记住这一课最核心的直觉：<strong>opencode 的 core 永远只说一种规范语言，把「对接千差万别的供应商」这件脏活，彻底隔离在一层协议适配器里。</strong>这是「反腐层 / 适配器模式」在「多模型对接」这个维度上的一次教科书级实践。下一课，我们就走近这道翻译墙，看一个协议适配器内部，到底由哪几块「翻译职责」构成。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p>core 对外其实只用 <span class="mono">@opencode-ai/llm</span> 这个<strong>独立包</strong>暴露的几个入口，干净得很：</p>
  <pre class="code"><span class="cm">// packages/llm/src/llm.ts —— core 看到的 LLM 接口</span>
<span class="kw">export const</span> stream = LLMClient.stream      <span class="cm">// 流式：吐 LLMEvent 流（第 17 课在用）</span>
<span class="kw">export const</span> generate = LLMClient.generate  <span class="cm">// 一次性</span>
<span class="kw">export const</span> request = (input) =&gt; <span class="kw">new</span> LLMRequest({ ... })  <span class="cm">// 规范化请求</span></pre>
  <p>注意 LLM 层是一个<strong>独立的包</strong>（<span class="mono">packages/llm</span>），不在 <span class="mono">packages/core</span> 里。这个物理上的分包，本身就是「翻译墙」的一道<strong>实体边界</strong>：协议、供应商、各家方言的所有细节，都被关在这个包内；core 只 <span class="mono">import</span> 它暴露的 <span class="mono">LLM.stream</span>/<span class="mono">request</span> 等少数几个干净入口。<strong>把脏活关进一个独立包，连依赖关系都替你昭示了「谁该知道方言、谁不该」。</strong>这是「关注点分离」做到包一级的彻底。一个简单的判断法则随之而来：<strong>凡是「这家供应商怎么怎么样」的知识，都只该住在这个包里；一旦它泄漏进了 core，就是一处需要警惕的设计破窗。</strong>这条法则，往后第 33-35 课讲路由、缓存、模型解析时还会反复用到。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li>第 17 课那句 <span class="mono">llm.stream(request)</span> 背后，是一整套<strong>翻译系统</strong>：core 说一种规范语，协议适配器翻成各家方言、再翻回来。</li>
    <li><strong>规范中间语言</strong>：出去是统一的 <span class="mono">LLMRequest</span>（system/messages/tools/generation/providerOptions），回来是统一的 <span class="mono">LLMEvent</span> 流——agent 循环对供应商<strong>一无所知</strong>。</li>
    <li><strong>反腐层思想</strong>：把「迁就千差万别供应商」的脏活，隔离在协议适配器一层，杜绝 core 里满地 <span class="mono">if (provider === …)</span> 的腐蚀。</li>
    <li><strong>协议 vs 供应商两分层</strong>：协议=线缆格式（6 种：Anthropic/OpenAI Chat/OpenAI Responses/OpenAI-Compatible/Gemini/Bedrock）；供应商=具体厂商（用哪种协议+认证+端点）。二者多对多，<strong>少量协议、大量复用</strong>。</li>
    <li>LLM 层是 <strong>独立包</strong> <span class="mono">@opencode-ai/llm</span>，物理隔离脏活；core 只 import 少数干净入口。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Part 4's agent loop calls <span class="mono">llm.stream(request)</span> each round, consulting the model once. Part 6, we drill into <strong>what's behind that one call</strong> — how opencode deals with model providers that <strong>each speak their own tongue</strong>: Anthropic, OpenAI, Gemini, Bedrock, Copilot… each API's <strong>dialect differs</strong>: how messages are arranged, how tools are declared, how streaming responses are chunked, all different. Yet opencode's core <strong>speaks only one language, start to finish</strong>. How? The answer is a whole <strong>translation system</strong> — this lesson builds the master diagram first: core speaks <strong>one canonical language</strong>, a layer of <strong>protocol adapters</strong> translates it into each dialect and translates each reply back. Grasp this diagram and you've caught all of Part 6's skeleton.</p>
<p>Why does "interfacing with many models" deserve a whole part? Because it's a badly-underestimated dirty, tiring job. Each provider's API <strong>evolves on its own</strong>: different field names, different tool-call protocols, different error formats, different streaming-chunk granularity, and revisions now and then. If you let core's business logic <strong>directly</strong> accommodate these differences, core gets <strong>riddled and corroded</strong> by each dialect's detail — ugly <span class="mono">if (provider === "anthropic") ... else if ...</span> branches everywhere. opencode's countermeasure is the classic <strong>"anti-corruption layer"</strong> idea: between core and external providers, build a <strong>translation wall</strong>; inside the wall is always clean canonical language, and the messiness outside is all blocked at the adapter layer. This lesson sees the wall's overall structure.</p>

<div class="card analogy">
  <div class="tag">🌐 Analogy</div>
  Think of opencode's core as a <strong>commander who speaks only his native tongue</strong>, doing business with five contractors who each <strong>speak a different dialect</strong> (Anthropic, OpenAI, Gemini…). The dumbest way is making the commander learn five dialects himself — he'd be <strong>exhausted and led astray</strong> by these fiddly language details. The smart way gives him a team of <strong>simultaneous interpreters</strong> (protocol adapters): the commander always states needs in his native tongue (a canonical <span class="mono">LLMRequest</span>), the interpreter <strong>translates it into the right contractor's dialect</strong> and sends it; the contractor replies in dialect, the interpreter <strong>translates back to the native tongue</strong> (canonical <span class="mono">LLMEvent</span>) for the commander. The commander <strong>speaks only one language throughout</strong>, the five dialects' grunt work all digested at the interpreter layer. A sixth contractor shows up one day? Add one more interpreter, the commander changes not a word. This interpreter team is opencode's LLM protocol layer.
</div>

<h2>One canonical language: LLMRequest and LLMEvent</h2>
<p>This translation system stands on core and adapters agreeing on a <strong>canonical "intermediate language."</strong> The outbound direction is <span class="mono">LLMRequest</span> — a <strong>unified request object</strong> expressing "what I want to ask" in a form <strong>independent</strong> of any provider:</p>
<div class="cellgroup">
  <div class="cell"><div class="k">system</div><div class="v">system prompt (baseline + mid-conversation updates, Part 5)</div></div>
  <div class="cell"><div class="k">messages</div><div class="v">canonicalized conversation messages</div></div>
  <div class="cell"><div class="k">tools / toolChoice</div><div class="v">available tools and selection policy</div></div>
  <div class="cell"><div class="k">generation</div><div class="v">temperature, max tokens, and other generation params</div></div>
  <div class="cell"><div class="k">providerOptions</div><div class="v">the few genuinely provider-specific escape hatches</div></div>
</div>
<p>The inbound direction is a stream of <span class="mono">LLMEvent</span> — the model's response translated into a string of <strong>unified events</strong>: text chunks, reasoning chunks, tool calls, usage stats, errors… Remember Lesson 17's loop line <span class="mono">llm.stream(request).pipe(Stream.runForEach(event =&gt; ...))</span>? The <span class="mono">event</span> it consumes is exactly this canonical <span class="mono">LLMEvent</span>. <strong>Whether the underlying is Anthropic or Gemini, the loop sees identically-shaped events</strong> — exactly the translation wall's whole value: the agent loop inside the wall <strong>knows nothing of the provider, and needn't.</strong></p>
<p>Pause on the weight of "one canonical language." Its essence is nailing down, between core and the outside world, <strong>a contract both sides honor</strong>: core promises "I'll always request in this shape, receive responses in this shape," and adapters promise "however messy outside, I'll tidy it into this shape." Once this contract stands, both sides can <strong>evolve independently</strong>: core wants a new tool-call style, just add it to the canon, no need to mind how a dozen providers implement it; a provider changes its API, just change that adapter, core unaware. <strong>A canonical language isn't a restriction but a decoupling freedom</strong> — it cleanly separates "how the business evolves" from "how providers evolve," two things that would otherwise drag each other down. You'll find this is the <strong>same wisdom</strong> as Lesson 12's "decouple front/back ends with an OpenAPI spec": stand a contract both machines/sides honor in the middle, and both ends gain freedom from being held hostage by the other.</p>
<div class="flow">
  <div class="node">core / agent loop<span class="sub">speaks only canonical</span></div>
  <div class="arrow">LLMRequest →</div>
  <div class="node">protocol adapter<span class="sub">the translation wall</span></div>
  <div class="arrow">each dialect →</div>
  <div class="node">some provider<span class="sub">Anthropic/OpenAI…</span></div>
</div>

<h2>Two layers: protocol vs provider</h2>
<p>Inside the translation wall, opencode makes another cut, into <strong>two clear layers</strong>: <strong>protocol</strong> and <strong>provider</strong>. These two words are often conflated, but opencode separates them firmly — understanding this distinction is the key to this layer. An analogy: a protocol is like a <strong>plug standard</strong> (two-prong, three-prong, UK, EU), a provider like <strong>a specific appliance</strong>. One plug standard fits a whole pile of appliances, one appliance (dual-voltage) may support two standards — standard and appliance should be discussed separately.</p>
<div class="cols">
  <div class="col"><h4>protocol = a "wire format"</h4><p>Defines exactly <strong>what the request/response look like</strong> on the wire: how fields are named, how tools are encoded, how the stream is chunked. opencode has <strong>6</strong>: Anthropic Messages, OpenAI Chat, OpenAI Responses, OpenAI-Compatible, Gemini, Bedrock Converse.</p></div>
  <div class="col"><h4>provider = a "specific vendor"</h4><p>A service you can actually connect to: <strong>which protocol</strong> + how to authenticate + which endpoint. Like anthropic, openai, google, bedrock, azure, github-copilot, openrouter, xai…</p></div>
</div>
<p>This cut is masterful because <strong>protocol and provider are "many-to-many."</strong> One protocol can serve many providers: the OpenAI Chat protocol isn't used only by OpenAI itself but by a <strong>whole crowd of "OpenAI-compatible" vendors</strong> (OpenRouter, xAI, various local models…) speaking through it. Conversely, one provider may support several protocols: OpenAI itself has both the old Chat and the new Responses. Decoupling "wire format" (protocol) from "specific vendor" (provider) lets opencode cover a dozen-plus providers <strong>reusing</strong> just <strong>6 protocols</strong> — not writing a fresh set per vendor. <strong>Few protocols, much reuse</strong> — that's where this layering pays off most.</p>
<p>Why not just "one adapter per provider" and skip the "protocol" abstraction? Because that breeds much <strong>duplication</strong>. OpenRouter, xAI, local Ollama — their API forms are nearly identical to OpenAI's; per-provider sets would copy the same "OpenAI dialect translation" three or four times, and a change needs changing in three or four places. opencode extracts the "dialect" into a standalone "protocol," precisely seeing that <strong>same-form providers essentially share one wire format</strong>. So the provider layer becomes ultra-thin — almost just "which protocol I use, how to authenticate, which endpoint," while the truly laborious "translation" logic settles into the few protocols for reuse. <strong>Sink the duplicated parts down, lift the volatile parts up</strong> — the eternal motif of layered design, here again.</p>

<h2>What the translation wall blocks</h2>
<p>To feel the wall's value, imagine <strong>without it</strong>. If the agent loop directly called each vendor's SDK, then "send a message with a tool call" would have to be written as a tangle in core: Anthropic's tools go in a <span class="mono">tools</span> array with <span class="mono">input_schema</span>; OpenAI's in <span class="mono">functions</span> (or the new <span class="mono">tools</span>) with <span class="mono">parameters</span>; Gemini is yet another <span class="mono">functionDeclarations</span>… every "call the model" in core would sprout a vine of <span class="mono">if (provider === ...)</span> branches, choked in each dialect's detail. Worse, when a vendor revises, you'd hunt and change all over core.</p>
<div class="cols">
  <div class="col"><h4>❌ no translation wall</h4><p>core directly interfaces each SDK. Every "call the model" if-elses by provider; each dialect's detail corrodes business logic; a vendor revision means changing all over core; a new provider means touching core.</p></div>
  <div class="col"><h4>✅ with translation wall</h4><p>core speaks only canonical. Provider differences all locked at the adapter layer; a vendor revision changes only its own protocol; a new provider = add one adapter, core unchanged.</p></div>
</div>
<p>This is exactly why an "<strong>anti-corruption layer</strong>" is so named: it guards against the outside world's <strong>chaos and volatility corroding into your clean core</strong>. The agent loop inside the wall forever lives in a <strong>simple world</strong> of "one model, one request, one event" — that simplicity isn't because reality is simple but because an adapter layer <strong>carries off all of reality's complexity for it</strong>. The reason you were never bothered by "which model is this" reading Part 4 is exactly this wall quietly working.</p>
<div class="trace">
  <div class="t-row"><span class="t-num">1</span><span class="t-txt">agent loop: llm.stream(canonical LLMRequest)</span></div>
  <div class="t-row"><span class="t-num">2</span><span class="t-txt">routing picks a provider → that provider's designated protocol</span></div>
  <div class="t-row"><span class="t-num">3</span><span class="t-txt">protocol.encode: canonical request → this vendor's dialect JSON, sent</span></div>
  <div class="t-row"><span class="t-num">4</span><span class="t-txt">provider streams back (this vendor's dialect chunks)</span></div>
  <div class="t-row"><span class="t-num">5</span><span class="t-txt">protocol.decode: dialect chunks → canonical LLMEvent stream, back to the loop</span></div>
</div>

<h2>Few protocols, covering many providers</h2>
<p>Nail the "protocol vs provider" relationship with concrete numbers. opencode maintains <strong>6 protocols</strong> in all, yet covers <strong>a dozen-plus providers</strong> with them:</p>
<div class="cellgroup">
  <div class="cell"><div class="k">Anthropic Messages</div><div class="v">serves Anthropic (Claude)</div></div>
  <div class="cell"><div class="k">OpenAI Chat / Responses</div><div class="v">serves OpenAI itself (old and new)</div></div>
  <div class="cell"><div class="k">OpenAI-Compatible</div><div class="v">serves a crowd of compatible vendors: OpenRouter, xAI, local models…</div></div>
  <div class="cell"><div class="k">Gemini</div><div class="v">serves Google Gemini</div></div>
  <div class="cell"><div class="k">Bedrock Converse</div><div class="v">serves various models on AWS Bedrock</div></div>
</div>
<p>See the leverage? The <strong>OpenAI-Compatible</strong> protocol single-handedly catches "every vendor on the market claiming OpenAI compatibility" — their number keeps growing, yet opencode <strong>adds not a line of new protocol code</strong>. That's the compound interest of "abstracting the wire format into a protocol": "OpenAI-compatible" has become a de facto industry standard, and opencode, implementing this standard once, free-rides the whole ecosystem. <strong>Fewest protocols, most providers leveraged</strong> — this layer's economy is plain in this number contrast. It also explains why Lesson 31 spends a whole lesson on the OpenAI protocol: it serves not one vendor but <strong>half an ecosystem</strong>.</p>

<div class="card macro">
  <div class="tag">🗺️ The big picture · Part 6 prologue</div>
  <p>This lesson sets the outline for Part 6. The whole LLM layer unfolds over the next lessons:</p>
  <ul>
    <li><strong>Lesson 28 · this one</strong>: the master diagram — core speaks canonical (<span class="mono">LLMRequest</span>/<span class="mono">LLMEvent</span>), protocol adapters as the "translation wall"; protocol vs provider two layers.</li>
    <li><strong>Lesson 29</strong>: a protocol adapter's <strong>common skeleton</strong> — what "translation" duties a protocol must implement.</li>
    <li><strong>Lessons 30-32</strong>: the three big dialects in detail — <strong>Anthropic</strong> (30), <strong>OpenAI</strong> Chat/Responses (31), <strong>Gemini & Bedrock</strong> (32).</li>
    <li><strong>Lessons 33-35</strong>: routing & transport (33), streaming & caching (34), model resolution & Copilot (35).</li>
  </ul>
  <p>Remember this lesson's core intuition: <strong>opencode's core forever speaks only one canonical language, fully isolating the dirty job of "interfacing with wildly different providers" into a protocol-adapter layer.</strong> This is a textbook practice of "anti-corruption layer / adapter pattern" on the "multi-model interfacing" dimension. Next lesson we approach the translation wall to see what "translation duties" make up a single protocol adapter inside.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source detail</div>
  <p>Core outwardly uses only a few entries exposed by the <strong>standalone package</strong> <span class="mono">@opencode-ai/llm</span>, quite clean:</p>
  <pre class="code"><span class="cm">// packages/llm/src/llm.ts — the LLM interface core sees</span>
<span class="kw">export const</span> stream = LLMClient.stream      <span class="cm">// streaming: emits an LLMEvent stream (used in Lesson 17)</span>
<span class="kw">export const</span> generate = LLMClient.generate  <span class="cm">// one-shot</span>
<span class="kw">export const</span> request = (input) =&gt; <span class="kw">new</span> LLMRequest({ ... })  <span class="cm">// canonical request</span></pre>
  <p>Note the LLM layer is a <strong>standalone package</strong> (<span class="mono">packages/llm</span>), not inside <span class="mono">packages/core</span>. This physical split is itself a <strong>concrete boundary</strong> of the "translation wall": all the detail of protocols, providers, each dialect is locked inside this package; core only <span class="mono">import</span>s the few clean entries it exposes — <span class="mono">LLM.stream</span>/<span class="mono">request</span> etc. <strong>Locking the dirty job in a standalone package even makes the dependency graph declare "who should know dialects, who shouldn't."</strong> This is "separation of concerns" carried thoroughly to the package level. A simple rule of thumb follows: <strong>any "how this provider behaves" knowledge should live only in this package; once it leaks into core, that's a broken window to watch.</strong></p>
</div>

<div class="card key">
  <div class="tag">🎯 Key points</div>
  <ul>
    <li>Behind Lesson 17's <span class="mono">llm.stream(request)</span> is a whole <strong>translation system</strong>: core speaks one canonical language, protocol adapters translate to each dialect and back.</li>
    <li><strong>Canonical intermediate language</strong>: outbound is a unified <span class="mono">LLMRequest</span> (system/messages/tools/generation/providerOptions), inbound a unified <span class="mono">LLMEvent</span> stream — the agent loop <strong>knows nothing</strong> of the provider.</li>
    <li><strong>Anti-corruption layer idea</strong>: isolate the dirty job of "accommodating wildly different providers" at the protocol-adapter layer, banning <span class="mono">if (provider === …)</span> corrosion all over core.</li>
    <li><strong>Protocol vs provider, two layers</strong>: protocol = wire format (6: Anthropic/OpenAI Chat/OpenAI Responses/OpenAI-Compatible/Gemini/Bedrock); provider = specific vendor (which protocol + auth + endpoint). Many-to-many, <strong>few protocols, much reuse</strong>.</li>
    <li>The LLM layer is a <strong>standalone package</strong> <span class="mono">@opencode-ai/llm</span>, physically isolating the dirty job; core imports only a few clean entries.</li>
  </ul>
</div>
""",
}
LESSON_29 = {
    "zh": r"""
<p class="lead">上一课我们立了「翻译墙」的总图：core 说规范语，协议适配器翻成各家方言。这一课，我们走近这道墙，看<strong>一个协议适配器内部，到底由哪几块「翻译职责」构成</strong>。好消息是：opencode 把这件事抽象得极其干净——<strong>每一个协议，无论翻译的是 Anthropic 还是 Gemini 的方言，都在填同一张「两栏表」</strong>。一栏管<strong>出去</strong>（怎么把规范请求，编码成这家的请求体），一栏管<strong>回来</strong>（怎么把这家的流式响应，解码回规范事件）。读懂这张表的形状，你再去看第 30~32 课具体某家的协议，就只是在看「<strong>同一张表，被不同的方言填了不同的内容</strong>」而已。</p>
<p>为什么要先看「骨架」、再看具体协议？因为<strong>共性比差异更重要</strong>。六种协议看似五花八门，但它们要解决的<strong>问题是同构的</strong>：把一个统一的请求送出去、把一串流式的响应收回来。opencode 用一个 <span class="mono">Protocol</span> 接口，把这个「同构的问题」钉成了一张<strong>所有协议都必须填的表</strong>。先把这张表的格子认清楚，你就有了一副「<strong>对照阅读</strong>」的框架：看任何一家协议时，都能立刻定位「它的请求编码在哪、流解码在哪」，而不会迷失在某家方言的细节里。这一课给的，是读懂后面三课的<strong>地图</strong>。</p>

<div class="card analogy">
  <div class="tag">📋 生活类比</div>
  上一课那队同声传译，其实每个人手里都有一份<strong>一模一样的「岗位说明书」</strong>（<span class="mono">Protocol</span> 接口）。说明书只规定两项硬性职责：<strong>一、「出境翻译」</strong>——把总指挥用母语提的需求，<strong>整理成对应承包商能看懂的一份完整文书</strong>（请求体）。<strong>二、「入境翻译」</strong>——这条最讲究：承包商的回话不是一口气说完的，而是<strong>一个词一个词、断断续续地</strong>传回来；传译必须<strong>边听边记、攒着上下文</strong>，把这一串碎片，一点点拼回母语里一句句完整的话（流式解码）。无论你这名传译负责的是哪国方言，<strong>这两项职责的「形状」分毫不差</strong>——区别只在于，针对不同方言，你「怎么整理文书」「怎么拼碎片」的具体手法不同。一张统一的说明书、六种方言的不同填法——这就是协议适配器的骨架。
</div>

<h2>一张两栏表：body 与 stream</h2>
<p>翻开 <span class="mono">route/protocol.ts</span>，<span class="mono">Protocol</span> 接口干净得像一张表格——它只有两大块，<strong>恰好对应「出去」和「回来」</strong>：</p>
<pre class="code"><span class="cm">// 简化自 route/protocol.ts</span>
<span class="kw">interface</span> Protocol&lt;Body, Frame, Event, State&gt; {
  id: ProtocolID
  body: {                          <span class="cm">// ← 请求侧（出去）</span>
    schema: Codec&lt;Body&gt;            <span class="cm">//   这家请求体的形状</span>
    from: (LLMRequest) =&gt; Body     <span class="cm">//   把规范请求 → 这家的请求体</span>
  }
  stream: {                        <span class="cm">// ← 响应侧（回来）：一台状态机</span>
    event: Codec&lt;Event, Frame&gt;     <span class="cm">//   把一个线缆帧 → 一个解码事件</span>
    initial: (LLMRequest) =&gt; State <span class="cm">//   解析器初始状态</span>
    step: (State, Event) =&gt; [State, LLMEvent[]]  <span class="cm">// 一个事件 → 规范事件 + 新状态</span>
  }
}</pre>
<p>整个接口就两块：<span class="mono">body</span> 管请求、<span class="mono">stream</span> 管响应。这个划分本身就是一句话的设计哲学：<strong>一个协议要干的，无非是「把规范请求翻成方言、把方言响应翻回规范」这一来一回</strong>。<span class="mono">body.from</span> 就是「出境翻译」的全部——一个函数，吃一个 <span class="mono">LLMRequest</span>，吐一个这家供应商能懂的请求体。<span class="mono">stream</span> 则是「入境翻译」，它复杂得多，是一台<strong>状态机</strong>（下一节细说）。一张表，两栏；填满这两栏，一个协议就成了。</p>
<p>还有个值得留意的细节：接口头上那四个类型参数 <span class="mono">&lt;Body, Frame, Event, State&gt;</span>，其实是在<strong>逼每个协议明确回答四个问题</strong>——你的<strong>请求体</strong>长什么样（Body）？线缆上一帧<strong>原始数据</strong>是什么（Frame）？解码后的<strong>一个事件</strong>是什么结构（Event）？你的解析器要<strong>攒什么状态</strong>（State）？这四个「未知数」一旦被一家协议各自填上具体类型，TypeScript 就能<strong>顺着 schema 和函数把类型全推导出来</strong>——源码注释特意说，组装协议时<strong>通常无需手写类型参数</strong>，schema 和解析函数自己就是真理之源。换句话说，这张表不只是「文档式」的约定，它是一副<strong>带类型的模具</strong>：你把四个空填实，编译器替你保证「请求体的形状」「事件的解码」「状态的流转」三处首尾一致、不会接错。</p>
<div class="cols">
  <div class="col"><h4>body · 请求侧（出去）</h4><p>一个 <span class="mono">from(LLMRequest)</span> 函数，把规范请求编码成这家的请求体。简单、一次成形。</p></div>
  <div class="col"><h4>stream · 响应侧（回来）</h4><p>一台状态机，把这家的流式响应，一帧一帧解码、累积、翻回规范 <span class="mono">LLMEvent</span>。</p></div>
</div>
<p>把这张表立体地画出来，就是下面这三层——最外层是协议的身份与两大职责，往里一层是每个职责由哪几个零件组成。你会发现，<strong>所有的复杂度都压在了 <span class="mono">stream</span> 这一栏</strong>：请求侧轻飘飘两个零件，响应侧却挂着五个零件的一台机器。这种「一边轻、一边重」的视觉不平衡，本身就在提醒你：读任何一家协议，<strong>真正的功夫都在 <span class="mono">stream</span> 上</strong>。</p>
<div class="layers">
  <div class="layer"><div class="l-name">Protocol</div><div class="l-desc">id（协议身份）＋ 两大职责：body / stream</div></div>
  <div class="layer"><div class="l-name">body（请求侧）</div><div class="l-desc">schema（请求体形状）＋ from（规范请求 → 这家请求体）</div></div>
  <div class="layer"><div class="l-name">stream（响应侧）</div><div class="l-desc">event ＋ initial ＋ step ＋ terminal? ＋ onHalt?（一台状态机）</div></div>
</div>

<h2>出境翻译：body.from，一个函数的事</h2>
<p>先看轻的那一栏。<span class="mono">body.from</span> 的签名朴素到了极点：<span class="mono">(request: LLMRequest) =&gt; Effect&lt;Body&gt;</span>——喂进去一个规范请求，吐出来一个这家供应商认得的请求体。为什么它能这么简单？因为请求是<strong>静态</strong>的：在你按下发送键的那一刻，你想说什么、带哪些消息、给哪些工具定义、要多少 token，<strong>全都已经定好了</strong>。没有「边想边说」，没有「说一半再补」。所以「出境翻译」就是一道<strong>纯粹的数据变换</strong>：把规范结构里的字段，按这家方言的字段名和嵌套方式，重新摆一遍。</p>
<div class="flow">
  <div class="f-node">LLMRequest<br><small>规范请求</small></div>
  <div class="f-arrow">body.from →</div>
  <div class="f-node">字段改名 / 重排<br><small>messages、tools、温度…按方言摆放</small></div>
  <div class="f-arrow">→</div>
  <div class="f-node">Body<br><small>这家的请求体</small></div>
</div>
<p>那 <span class="mono">schema</span> 又是干嘛的？它是这家请求体的<strong>形状契约</strong>——一个 <span class="mono">Codec&lt;Body&gt;</span>。它有两重价值：一是给 <span class="mono">from</span> 的产物一个<strong>可校验的目标类型</strong>（编出来的 body 必须长这样，错了在类型层就拦下）；二是真正发请求时，由它把 <span class="mono">Body</span> 编码成 JSON 字符串（回忆第 28 课提到的 <span class="mono">protocol.body.schema</span> encode）。<strong>from 负责「内容对不对」，schema 负责「形状对不对」</strong>，两者一搭，请求侧就齐了。这一栏之所以举重若轻，正因为它面对的是一个「已经尘埃落定」的请求——难的从来不是把定稿翻译出去，而是把一段还在流动中的话，边听边拼回来。</p>

<h2>为什么请求简单、响应是状态机</h2>
<p>这张表最值得玩味的，是它的<strong>不对称</strong>：请求侧只是一个函数，响应侧却是一台状态机。这个不对称不是随意的，它<strong>忠实地映射了现实</strong>。请求，是你<strong>一次性</strong>拼好、整个发出去的——所以一个 <span class="mono">from</span> 函数足矣。可响应，是模型<strong>流式</strong>吐回来的：文字一个 token 一个 token 地来，一个工具调用的参数 JSON 会<strong>跨好几个分块</strong>陆续到齐，用量统计在最后才出现…… 你不可能等它全部到齐再处理（那就失去了「流式」的全部意义），必须<strong>边收边解</strong>。而「边收边解」就天然需要<strong>记住「目前收到哪了」</strong>——这，正是状态机存在的理由。</p>
<div class="trace">
  <div class="t-row"><span class="t-num">initial</span><span class="t-txt">每次响应开始，建一个初始解析状态 State</span></div>
  <div class="t-row"><span class="t-num">event</span><span class="t-txt">收到一个线缆帧 Frame → 解码成一个 Event</span></div>
  <div class="t-row"><span class="t-num">step</span><span class="t-txt">step(State, Event) → [新 State, 吐出的若干 LLMEvent]</span></div>
  <div class="t-row"><span class="t-num">…循环…</span><span class="t-txt">每来一帧就 step 一次，状态不断推进、事件不断吐出</span></div>
  <div class="t-row"><span class="t-num">onHalt</span><span class="t-txt">流结束 → 可选地 flush 最后一批 LLMEvent</span></div>
</div>
<p><span class="mono">step</span> 的签名 <span class="mono">(State, Event) =&gt; [State, LLMEvent[]]</span> 是整个响应侧的灵魂，也是函数式里<strong>状态转换</strong>的经典形态：给我「当前状态」和「新来的一个事件」，我还你「下一个状态」和「这一步该吐出的规范事件」。比如一个工具调用：第一帧 <span class="mono">step</span> 可能只记下「开始攒一个叫 read 的工具调用」（吐空），后续几帧把参数 JSON 一段段拼进 State（还吐空），等参数齐了，最后一帧才吐出一个完整的 <span class="mono">toolCall</span> 规范事件。<strong>碎片进、完整出</strong>，靠的就是 State 在中间默默攒着。这台状态机，就是把「方言的流式碎片」重组成「规范的完整事件」的那台机器。</p>
<p>把刚才那个工具调用的例子，一帧一帧摊开看，状态机的「攒」就具体了——注意前三步 <span class="mono">step</span> <strong>吐出的规范事件都是空的</strong>，State 在悄悄变厚；直到参数齐了，才「啪」地吐出一个完整事件：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">帧1</span><span class="t-txt">「开始一个工具调用 read」→ State 记下 {name:read, args:''}，吐出 []</span></div>
  <div class="t-row"><span class="t-num">帧2</span><span class="t-txt">参数分块 '{\"path\":' → State.args 追加，吐出 []</span></div>
  <div class="t-row"><span class="t-num">帧3</span><span class="t-txt">参数分块 '\"a.ts\"}' → State.args 追加，此时 JSON 已完整</span></div>
  <div class="t-row"><span class="t-num">帧4</span><span class="t-txt">「工具调用结束」→ 吐出完整 LLMEvent.toolCall{name:read, args:{path:'a.ts'}}</span></div>
</div>
<p>这就是 State 的全部意义：<strong>它是那块「把跨帧碎片暂存到拼齐为止」的草稿纸</strong>。没有它，你收到「<span class="mono">{\"path\":</span>」这半截 JSON 时根本无从处理——它既不是合法 JSON，也不构成任何完整语义。有了 State，每一帧都只做一件小事（追加、记录），完整性判断和事件吐出，留到「攒齐」的那一刻。这也解释了为什么 <span class="mono">step</span> 要把「新状态」一并吐回去：状态机不许偷偷改全局变量，每一步都<strong>显式地把草稿纸传给下一步</strong>，于是整条解码链就成了一串纯粹、可预测的转换。把响应侧的五个零件并排看，各司其职就一目了然了：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">event</div><div class="c-txt">把一个线缆帧 Frame 解码成一个结构化 Event（Codec）</div></div>
  <div class="cell"><div class="c-tag">initial</div><div class="c-txt">每次响应开始，按请求建一个初始解析状态 State</div></div>
  <div class="cell"><div class="c-tag">step</div><div class="c-txt">核心：吃 (State, Event)，吐 [新 State, 若干 LLMEvent]</div></div>
  <div class="cell"><div class="c-tag">terminal?</div><div class="c-txt">可选：判断某事件是否标志「请求完成」（给不会自然收尾的传输用）</div></div>
  <div class="cell"><div class="c-tag">onHalt?</div><div class="c-txt">可选：流结束时，flush 最后一批攒着的 LLMEvent</div></div>
</div>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <p>这一课给出了所有协议共享的<strong>骨架</strong>，是读懂后面三课的地图：</p>
  <ul>
    <li><strong>一个 <span class="mono">Protocol</span> = 两栏表</strong>：<span class="mono">body</span>（请求侧）+ <span class="mono">stream</span>（响应侧）。所有协议都填这张表。</li>
    <li><strong>body.from</strong>：一个函数，规范 <span class="mono">LLMRequest</span> → 这家的请求体。出境翻译，一次成形。</li>
    <li><strong>stream 是状态机</strong>：<span class="mono">initial</span>（建状态）→ <span class="mono">step(State, Event)</span>（碎片进、累积、吐规范事件）→ <span class="mono">onHalt</span>（收尾）。</li>
    <li><strong>不对称映射现实</strong>：请求一次发出（函数够用），响应流式到达（必须状态机边收边解）。</li>
  </ul>
  <p>有了这张表，接下来三课就清晰了：它们各自只是在<strong>填同一张表的不同方言版本</strong>。第 30 课看 <strong>Anthropic</strong> 怎么填（它的工具块、缓存断点有什么特别）；第 31 课看 <strong>OpenAI</strong> 的 Chat 与 Responses 两套填法；第 32 课看 <strong>Gemini 与 Bedrock</strong>。读它们时，你只需带着一个问题：「<strong>这家的 <span class="mono">body.from</span> 和 <span class="mono">stream.step</span>，和别家比，特别在哪？</strong>」——骨架你已经懂了，剩下的全是方言的趣味。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p>一个协议怎么「组装」出来？看 <span class="mono">anthropic-messages.ts</span> 结尾那几行，正是在填这张表：</p>
  <pre class="code"><span class="cm">// 简化自 protocols/anthropic-messages.ts 结尾</span>
<span class="kw">export const</span> protocol = Protocol.<span class="fn">make</span>({
  id: ADAPTER,
  body: { schema: ..., from: ... },        <span class="cm">// 请求侧</span>
  stream: { event: ..., initial: ..., step: ... },  <span class="cm">// 响应侧</span>
})</pre>
  <p>有意思的是 <span class="mono">Protocol.make</span> 本身——它的实现就是 <span class="mono">(input) =&gt; input</span>，<strong>一个恒等函数</strong>！它不做任何运行时的事，纯粹是个「<strong>类型化的接缝</strong>」：源码注释说得明白，「schema 和解析函数才是真理之源」，<span class="mono">make</span> 存在的意义，是给未来的横切关注点（比如加 tracing、instrumentation）<strong>预留一个统一的入口</strong>。这是一种很克制的远见：现在不需要在组装协议时做额外的事，但留一个 <span class="mono">make</span> 的壳，将来想给所有协议<strong>统一加一层</strong>时，就有了唯一的下手处，而不必去改六个协议的定义。<strong>一个今天什么都不做的恒等函数，是为明天的「统一改造」留的门。</strong></p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li>每个协议适配器都在填<strong>同一张两栏表</strong>（<span class="mono">Protocol</span> 接口，<span class="mono">route/protocol.ts</span>）：<span class="mono">body</span>（请求侧）+ <span class="mono">stream</span>（响应侧）。</li>
    <li><strong>body.from</strong>：一个函数，把规范 <span class="mono">LLMRequest</span> 编码成这家供应商的请求体——出境翻译，一次成形。</li>
    <li><strong>stream 是一台状态机</strong>：<span class="mono">initial</span> 建状态 → <span class="mono">step(State, Event) =&gt; [State, LLMEvent[]]</span> 把方言流式碎片累积、重组成规范事件 → <span class="mono">onHalt</span> 收尾。</li>
    <li><strong>不对称映射现实</strong>：请求一次性发出（函数够用），响应流式到达、需跨帧累积（如工具调用参数分块到齐），故必须状态机边收边解。</li>
    <li><span class="mono">Protocol.make</span> 是<strong>恒等函数</strong>，纯类型化接缝——为未来横切关注点（tracing 等）预留统一入口。这张表是读懂第 30~32 课的地图。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Last lesson drew the big picture of the "translation wall": core speaks the canonical language, protocol adapters translate it into each vendor's dialect. This lesson walks up to that wall and looks at <strong>what a single protocol adapter is made of, internally</strong>. The good news: opencode abstracts this with extraordinary cleanliness—<strong>every protocol, whether it translates Anthropic's or Gemini's dialect, fills in the same two-column form</strong>. One column handles <strong>outbound</strong> (how to encode a canonical request into this vendor's body), one handles <strong>inbound</strong> (how to decode this vendor's streaming response back into canonical events). Once you grasp the shape of this form, reading any specific protocol in lessons 30–32 becomes just watching "<strong>the same form, filled in with a different dialect</strong>."</p>
<p>Why look at the "skeleton" first, then specific protocols? Because <strong>commonality matters more than difference</strong>. Six protocols look wildly varied, but the <strong>problem they solve is isomorphic</strong>: send one unified request out, take a stream of responses back. opencode nails this "isomorphic problem" into one <span class="mono">Protocol</span> interface—<strong>a form every protocol must fill</strong>. Learn the cells of this form, and you have a <strong>cross-reading</strong> framework: for any vendor, you can instantly locate "where its request encoding lives, where its stream decoding lives," instead of drowning in one dialect's details. This lesson gives you the <strong>map</strong> for the next three.</p>

<div class="card analogy">
  <div class="tag">📋 Analogy</div>
  Each interpreter in last lesson's relay actually holds an <strong>identical "job description"</strong> (the <span class="mono">Protocol</span> interface). It mandates only two hard duties: <strong>One, "outbound translation"</strong>—take the chief's request, phrased in the mother tongue, and <strong>assemble one complete document the matching contractor can read</strong> (the request body). <strong>Two, "inbound translation"</strong>—and this one's subtle: the contractor's reply doesn't come all at once, it arrives <strong>word by word, in halting fragments</strong>; the interpreter must <strong>listen-and-jot, holding context</strong>, piecing that stream of fragments back into complete mother-tongue sentences (streaming decode). Whatever dialect you handle, <strong>the "shape" of these two duties is identical</strong>—only the specific knack of "how you assemble the document" and "how you piece fragments" differs per dialect. One unified job description, six dialects' different fillings—that's the skeleton of a protocol adapter.
</div>

<h2>One two-column form: body and stream</h2>
<p>Open <span class="mono">route/protocol.ts</span> and the <span class="mono">Protocol</span> interface is clean as a table—just two big blocks, <strong>matching exactly "out" and "back"</strong>:</p>
<pre class="code"><span class="cm">// simplified from route/protocol.ts</span>
<span class="kw">interface</span> Protocol&lt;Body, Frame, Event, State&gt; {
  id: ProtocolID
  body: {                          <span class="cm">// ← request side (out)</span>
    schema: Codec&lt;Body&gt;            <span class="cm">//   shape of this vendor's body</span>
    from: (LLMRequest) =&gt; Body     <span class="cm">//   canonical request → this body</span>
  }
  stream: {                        <span class="cm">// ← response side (back): a state machine</span>
    event: Codec&lt;Event, Frame&gt;     <span class="cm">//   one wire frame → one decoded event</span>
    initial: (LLMRequest) =&gt; State <span class="cm">//   initial parser state</span>
    step: (State, Event) =&gt; [State, LLMEvent[]]  <span class="cm">// one event → canonical events + new state</span>
  }
}</pre>
<p>The whole interface is two blocks: <span class="mono">body</span> owns the request, <span class="mono">stream</span> owns the response. The split itself is a one-line design philosophy: <strong>all a protocol does is the round trip of "translate canonical request into dialect, translate dialect response back into canonical."</strong> <span class="mono">body.from</span> is the entirety of "outbound translation"—one function, eats an <span class="mono">LLMRequest</span>, emits a body this vendor understands. <span class="mono">stream</span> is "inbound translation," far more involved—a <strong>state machine</strong> (next section). One form, two columns; fill both, and a protocol is born.</p>
<p>One more detail worth noting: those four type parameters in the header, <span class="mono">&lt;Body, Frame, Event, State&gt;</span>, actually <strong>force each protocol to answer four questions</strong>—what does your <strong>request body</strong> look like (Body)? what's one raw <strong>frame</strong> on the wire (Frame)? what's the structure of one decoded <strong>event</strong> (Event)? what <strong>state</strong> must your parser accumulate (State)? Once a protocol fills these four "unknowns" with concrete types, TypeScript can <strong>infer all the types down the schemas and functions</strong>—the source comment notes you <strong>usually need not write type arguments</strong> when assembling a protocol; the schemas and parser functions are themselves the source of truth. In other words, this form isn't just a "documentary" convention—it's a <strong>typed mold</strong>: fill the four blanks and the compiler guarantees "request body shape," "event decode," and "state flow" all line up end to end.</p>
<div class="cols">
  <div class="col"><h4>body · request side (out)</h4><p>A <span class="mono">from(LLMRequest)</span> function, encoding the canonical request into this vendor's body. Simple, formed in one shot.</p></div>
  <div class="col"><h4>stream · response side (back)</h4><p>A state machine, decoding this vendor's streaming response frame by frame, accumulating, translating back into canonical <span class="mono">LLMEvent</span>.</p></div>
</div>
<p>Drawn in three dimensions, this form is the three layers below—outermost is the protocol's identity and two duties, one layer in is which parts each duty is made of. You'll notice <strong>all the complexity is loaded onto the <span class="mono">stream</span> column</strong>: the request side is two light parts, the response side hangs a five-part machine. That visual imbalance, "light on one side, heavy on the other," is itself a reminder: when reading any protocol, <strong>the real work is in <span class="mono">stream</span></strong>.</p>
<div class="layers">
  <div class="layer"><div class="l-name">Protocol</div><div class="l-desc">id (protocol identity) + two duties: body / stream</div></div>
  <div class="layer"><div class="l-name">body (request side)</div><div class="l-desc">schema (body shape) + from (canonical request → this body)</div></div>
  <div class="layer"><div class="l-name">stream (response side)</div><div class="l-desc">event + initial + step + terminal? + onHalt? (a state machine)</div></div>
</div>

<h2>Outbound: body.from, a one-function affair</h2>
<p>Take the light column first. <span class="mono">body.from</span>'s signature is plain to the extreme: <span class="mono">(request: LLMRequest) =&gt; Effect&lt;Body&gt;</span>—feed in a canonical request, get out a body this vendor recognizes. Why can it be this simple? Because the request is <strong>static</strong>: the moment you hit send, what you want to say, which messages you carry, which tool definitions you give, how many tokens you want—<strong>are all already fixed</strong>. No "thinking while talking," no "saying half then amending." So "outbound translation" is a <strong>pure data transformation</strong>: take the fields of the canonical structure, lay them out again under this dialect's field names and nesting.</p>
<div class="flow">
  <div class="f-node">LLMRequest<br><small>canonical request</small></div>
  <div class="f-arrow">body.from →</div>
  <div class="f-node">rename / rearrange fields<br><small>messages, tools, temperature… per dialect</small></div>
  <div class="f-arrow">→</div>
  <div class="f-node">Body<br><small>this vendor's body</small></div>
</div>
<p>So what's <span class="mono">schema</span> for? It's the <strong>shape contract</strong> of this vendor's body—a <span class="mono">Codec&lt;Body&gt;</span>. It carries two values: one, it gives <span class="mono">from</span>'s output a <strong>checkable target type</strong> (the encoded body must look like this, errors caught at the type level); two, at actual send time, it encodes the <span class="mono">Body</span> into a JSON string (recall lesson 28's <span class="mono">protocol.body.schema</span> encode). <strong>from handles "is the content right," schema handles "is the shape right"</strong>; together the request side is complete. This column lifts heavy things lightly precisely because it faces a request that has "already settled"—the hard part was never translating a finished draft outward, but piecing a still-flowing utterance back together as you listen.</p>

<h2>Why request is simple, response is a state machine</h2>
<p>What's most intriguing about this form is its <strong>asymmetry</strong>: the request side is just a function, the response side is a state machine. This asymmetry isn't arbitrary—it <strong>faithfully maps reality</strong>. A request you assemble <strong>all at once</strong> and send whole—so one <span class="mono">from</span> function suffices. But a response the model emits <strong>streaming</strong>: text arrives token by token, one tool call's argument JSON arrives <strong>across several chunks</strong>, usage stats appear only at the end… you can't wait for it all to arrive before processing (that defeats the whole point of "streaming"), you must <strong>decode as you receive</strong>. And "decode as you receive" inherently needs to <strong>remember "where you are so far"</strong>—which is exactly why the state machine exists.</p>
<div class="trace">
  <div class="t-row"><span class="t-num">initial</span><span class="t-txt">each response start, build an initial parser state State</span></div>
  <div class="t-row"><span class="t-num">event</span><span class="t-txt">receive a wire frame Frame → decode into one Event</span></div>
  <div class="t-row"><span class="t-num">step</span><span class="t-txt">step(State, Event) → [new State, emitted LLMEvents]</span></div>
  <div class="t-row"><span class="t-num">…loop…</span><span class="t-txt">each frame steps once, state advances, events emit</span></div>
  <div class="t-row"><span class="t-num">onHalt</span><span class="t-txt">stream ends → optionally flush the last batch of LLMEvents</span></div>
</div>
<p>The signature <span class="mono">(State, Event) =&gt; [State, LLMEvent[]]</span> is the soul of the whole response side, and a classic shape of <strong>state transition</strong> in functional style: give me "current state" and "one newly-arrived event," I return "next state" and "the canonical events this step should emit." Take a tool call: the first frame <span class="mono">step</span> might only note "start accumulating a tool call named read" (emits nothing); later frames piece the argument JSON into State chunk by chunk (still emit nothing); once the arguments are complete, the final frame emits one whole <span class="mono">toolCall</span> canonical event. <strong>Fragments in, whole out</strong>—powered by State quietly accumulating in the middle. This state machine is the machine that reassembles "the dialect's streaming fragments" into "canonical complete events."</p>
<p>Lay that tool-call example out frame by frame and the machine's "accumulate" gets concrete—note the first three <span class="mono">step</span>s <strong>emit empty canonical events</strong> while State quietly thickens; only once arguments are complete does it "pop" out one whole event:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">frame1</span><span class="t-txt">"begin tool call read" → State notes {name:read, args:''}, emits []</span></div>
  <div class="t-row"><span class="t-num">frame2</span><span class="t-txt">arg chunk '{\"path\":' → State.args appended, emits []</span></div>
  <div class="t-row"><span class="t-num">frame3</span><span class="t-txt">arg chunk '\"a.ts\"}' → State.args appended, JSON now complete</span></div>
  <div class="t-row"><span class="t-num">frame4</span><span class="t-txt">"tool call done" → emits whole LLMEvent.toolCall{name:read, args:{path:'a.ts'}}</span></div>
</div>
<p>That's the entire meaning of State: <strong>it's the "scratch paper" that buffers cross-frame fragments until they're whole</strong>. Without it, receiving the half-JSON "<span class="mono">{\"path\":</span>" leaves you nothing to do—it's neither valid JSON nor any complete meaning. With State, each frame does one small thing (append, note); completeness judgment and event emission wait for the "all assembled" moment. This also explains why <span class="mono">step</span> returns the "new state" alongside: the machine isn't allowed to secretly mutate globals, every step <strong>explicitly hands the scratch paper to the next</strong>, so the whole decode chain becomes a string of pure, predictable transforms. Lay the response side's five parts side by side and each one's job is plain:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">event</div><div class="c-txt">decode one wire frame Frame into one structured Event (Codec)</div></div>
  <div class="cell"><div class="c-tag">initial</div><div class="c-txt">each response start, build an initial parser State from the request</div></div>
  <div class="cell"><div class="c-tag">step</div><div class="c-txt">core: eats (State, Event), emits [new State, some LLMEvents]</div></div>
  <div class="cell"><div class="c-tag">terminal?</div><div class="c-txt">optional: judge whether an event marks "request done" (for transports that don't end naturally)</div></div>
  <div class="cell"><div class="c-tag">onHalt?</div><div class="c-txt">optional: at stream end, flush the last batch of buffered LLMEvents</div></div>
</div>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>This lesson gives the <strong>skeleton</strong> all protocols share, the map for the next three lessons:</p>
  <ul>
    <li><strong>One <span class="mono">Protocol</span> = a two-column form</strong>: <span class="mono">body</span> (request side) + <span class="mono">stream</span> (response side). Every protocol fills this form.</li>
    <li><strong>body.from</strong>: one function, canonical <span class="mono">LLMRequest</span> → this vendor's body. Outbound translation, formed in one shot.</li>
    <li><strong>stream is a state machine</strong>: <span class="mono">initial</span> (build state) → <span class="mono">step(State, Event)</span> (fragments in, accumulate, emit canonical events) → <span class="mono">onHalt</span> (wrap up).</li>
    <li><strong>asymmetry maps reality</strong>: request sent all at once (a function suffices), response arrives streaming (must be a state machine, decode as you receive).</li>
  </ul>
  <p>With this form, the next three lessons get clear: each is just <strong>filling the same form in a different dialect</strong>. Lesson 30 watches <strong>Anthropic</strong> fill it (what's special about its tool blocks, cache breakpoints); lesson 31 the <strong>OpenAI</strong> Chat and Responses fillings; lesson 32 <strong>Gemini and Bedrock</strong>. Read them carrying one question: "<strong>how is this vendor's <span class="mono">body.from</span> and <span class="mono">stream.step</span> special, versus the others?</strong>"—you already grasp the skeleton, the rest is all dialect flavor.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p>How is a protocol "assembled"? Look at the last lines of <span class="mono">anthropic-messages.ts</span>—it's filling exactly this form:</p>
  <pre class="code"><span class="cm">// simplified from end of protocols/anthropic-messages.ts</span>
<span class="kw">export const</span> protocol = Protocol.<span class="fn">make</span>({
  id: ADAPTER,
  body: { schema: ..., from: ... },        <span class="cm">// request side</span>
  stream: { event: ..., initial: ..., step: ... },  <span class="cm">// response side</span>
})</pre>
  <p>The intriguing part is <span class="mono">Protocol.make</span> itself—its implementation is <span class="mono">(input) =&gt; input</span>, <strong>an identity function</strong>! It does nothing at runtime, purely a "<strong>typed seam</strong>": the source comment is explicit, "the schemas and parser functions are the source of truth," and <span class="mono">make</span> exists to <strong>reserve a unified entry point</strong> for future cross-cutting concerns (like adding tracing, instrumentation). It's a restrained foresight: nothing extra is needed at assembly today, but leaving a <span class="mono">make</span> shell means when you later want to <strong>add one layer across all protocols</strong>, there's a single place to do it, without touching six protocol definitions. <strong>An identity function that does nothing today is a door left open for tomorrow's "unified retrofit."</strong></p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li>Every protocol adapter fills <strong>the same two-column form</strong> (the <span class="mono">Protocol</span> interface, <span class="mono">route/protocol.ts</span>): <span class="mono">body</span> (request side) + <span class="mono">stream</span> (response side).</li>
    <li><strong>body.from</strong>: one function, encoding the canonical <span class="mono">LLMRequest</span> into this vendor's request body—outbound translation, formed in one shot.</li>
    <li><strong>stream is a state machine</strong>: <span class="mono">initial</span> builds state → <span class="mono">step(State, Event) =&gt; [State, LLMEvent[]]</span> accumulates and reassembles dialect streaming fragments into canonical events → <span class="mono">onHalt</span> wraps up.</li>
    <li><strong>asymmetry maps reality</strong>: a request is sent all at once (a function suffices), a response arrives streaming and needs cross-frame accumulation (e.g. tool-call arguments arriving in chunks), so it must be a state machine decoding as it receives.</li>
    <li><span class="mono">Protocol.make</span> is an <strong>identity function</strong>, a pure typed seam—reserving a unified entry for future cross-cutting concerns (tracing etc.). This form is the map for lessons 30–32.</li>
  </ul>
</div>
""",
}
LESSON_30 = {
    "zh": r"""
<p class="lead">上一课我们把空白的「两栏表」（<span class="mono">Protocol</span> 接口）认了个透：<span class="mono">body</span> 管出去、<span class="mono">stream</span> 管回来。这一课，我们看<strong>第一份被真正填好的表</strong>——Anthropic Messages 协议。它是 opencode 的「主力方言」（Claude 系列走这条），也是把这张表填得最有个性的一份。读它，不只是学一种协议，更是<strong>第一次看见「骨架如何长出血肉」</strong>。Anthropic 这份填法，有两处签名式的个性，值得你记一辈子：一是<strong>「一切皆块」</strong>——请求和响应的内容都被拆成一个个带类型的「内容块」；二是<strong>「四个缓存断点的预算」</strong>——一个精巧到有点苛刻的约束，逼出了一段很漂亮的预算管理代码。</p>
<p>为什么挑 Anthropic 打头？因为它的设计<strong>最能体现「协议即方言」这件事的份量</strong>。同样是「发一段对话、收一段回复」，Anthropic 偏要你把内容装进<strong>带标签的盒子</strong>，偏要把系统提示<strong>单拎成一个顶层字段</strong>，还偏要给缓存<strong>设一个会爆 400 的硬上限</strong>。这些「偏要」就是方言的口音。而 opencode 的 <span class="mono">body.from</span>（这家叫 <span class="mono">lower*</span> 系列函数）要做的，就是把 core 那套不带口音的规范请求，一字一句翻成带 Anthropic 口音的话。看懂这份翻译，你就懂了「适配器」三个字的全部重量。</p>

<div class="card analogy">
  <div class="tag">📦 生活类比</div>
  想象你在替总指挥，给一家特别讲规矩的承包商（Anthropic）填一份报关单。这家有两条死规矩。<strong>第一条：所有东西都得装进「贴了标签的标准箱」</strong>——文字一个箱（text）、图片一个箱（image）、「请你执行这个工具」一个箱（tool_use）、「这是工具跑出来的结果」又一个箱（tool_result）。不许散装、不许混装，连「系统须知」都得单独放进报关单<strong>抬头那一栏</strong>，不能混在货物里。<strong>第二条更绝：你总共只有 4 张「优先缓存」贴纸。</strong>你想让承包商把某几箱「记住别重算」，就贴一张；可贴纸只有 4 张，贴第 5 张，整张报关单当场被打回（400 错误）。于是你不得不<strong>精打细算</strong>：边装箱边数贴纸，贴完 4 张，后面再想贴的，只能<strong>悄悄记下「这张本来想贴但没贴」，然后放弃</strong>。这两条死规矩——标准箱、贴纸预算——正是 Anthropic 这份协议最鲜明的口音。
</div>

<h2>一切皆「块」：带类型的内容盒子</h2>
<p>翻开 <span class="mono">protocols/anthropic-messages.ts</span>，最先扑面而来的就是一长串 <span class="mono">Schema.tag(...)</span> 定义的「块」类型。Anthropic 不像有些协议那样把消息内容塞成一个大字符串，而是要求<strong>每一段内容都是一个带 <span class="mono">type</span> 标签的结构化块</strong>：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">text</div><div class="c-txt">纯文本块</div></div>
  <div class="cell"><div class="c-tag">image</div><div class="c-txt">图片块（多模态输入）</div></div>
  <div class="cell"><div class="c-tag">tool_use</div><div class="c-txt">助手要调用一个工具（带 id、name、input）</div></div>
  <div class="cell"><div class="c-tag">tool_result</div><div class="c-txt">回传工具结果（带 tool_use_id 对应）</div></div>
  <div class="cell"><div class="c-tag">server_tool_use</div><div class="c-txt">服务端工具（如 web 搜索，供应商自己执行）</div></div>
  <div class="cell"><div class="c-tag">*_tool_result</div><div class="c-txt">服务端工具结果（web_search/code_execution/web_fetch，整块内联）</div></div>
</div>
<p>这种「一切皆块」的设计，好处是<strong>结构清晰、可校验、可携带元数据</strong>——每个块都能单独挂一个 <span class="mono">cache_control</span>（下一节的主角）。这里还藏着一个有意思的不对称：普通的 <span class="mono">tool_use</span>（客户端工具）是「助手开口要求、由 opencode 在本地跑、再把 <span class="mono">tool_result</span> 回传」的<strong>三步往返</strong>；可那几个<strong>服务端工具</strong>（<span class="mono">web_search</span> / <span class="mono">code_execution</span> / <span class="mono">web_fetch</span>）却是供应商<strong>自己执行、把结果整块内联</strong>进助手这一轮——源码注释特意点明，它们「<strong>整块到达，没有流式增量</strong>」，没有客户端这边对应的 <span class="mono">tool_result</span> 往返。一个「块」的类型标签，背后竟编码着「这工具该谁来跑」这样的执行语义差异，可见这套块类型设计之精细。还有个容易忽略的细节：<strong>系统提示（system）在 Anthropic 里不是一条消息，而是请求体顶层一个独立字段</strong>，类型是「一个文本块的数组」。这跟 OpenAI 把 system 当成 messages 里第一条「role: system」的消息，是<strong>截然不同的方言</strong>——而这，正是为什么要有协议适配器：core 那边只有一份规范的 system，到了 Anthropic 这份 <span class="mono">body.from</span> 里，它被翻译成顶层 <span class="mono">system</span> 字段；到了第 31 课 OpenAI 那份里，它又被翻译成 messages 数组的头一条。<strong>同一个规范概念，两种方言两种摆法</strong>，这就是适配器在默默吸收的差异。</p>
<div class="cols">
  <div class="col"><h4>Anthropic 的摆法</h4><p><span class="mono">system</span> 是顶层独立字段（文本块数组）；<span class="mono">messages</span> 里每条的 content 是「块数组」。</p></div>
  <div class="col"><h4>core 的规范</h4><p>core 只有一份不带口音的 system + 消息列表；不知道、也不该知道谁把它摆哪。</p></div>
</div>
<p>把这套「翻译」画成流水线，就是下面这条 <span class="mono">body.from</span>（即 <span class="mono">lower*</span> 系列）的工作链：规范请求进来，工具被 <span class="mono">lowerTool</span> 译成带 <span class="mono">input_schema</span> 的 Anthropic 工具、system 被摊成文本块数组放进顶层、每条消息的内容被逐段译成对应的块，最后拼成一个完整的 Anthropic 请求体。整条链上还<strong>串着一根贯穿始终的「缓存预算」红线</strong>（下一节细说），这也是为什么这些 <span class="mono">lower*</span> 函数每个都吃一个 <span class="mono">breakpoints</span> 参数：</p>
<div class="flow">
  <div class="f-node">LLMRequest<br><small>规范请求</small></div>
  <div class="f-arrow">lowerTool →</div>
  <div class="f-node">tools[]<br><small>带 input_schema</small></div>
  <div class="f-arrow">+ system →</div>
  <div class="f-node">顶层 system<br><small>文本块数组</small></div>
  <div class="f-arrow">+ lowerMessages →</div>
  <div class="f-node">Anthropic Body<br><small>messages 皆块</small></div>
</div>

<h2>四个缓存断点的预算：一段漂亮的「省钱」代码</h2>
<p>这是 Anthropic 协议里我最想让你品的一段。先讲背景：Anthropic 支持<strong>提示缓存（prompt caching）</strong>——你可以在某些块上打一个 <span class="mono">cache_control: {type: ephemeral}</span> 标记，告诉服务端「从开头到这个标记的这一段前缀，请缓存住，下次同样的前缀别重算」。这能<strong>大幅省钱省延迟</strong>（缓存命中的 token 便宜得多）。但 Anthropic 有一条硬约束：<strong>每个请求最多只能打 4 个 <span class="mono">cache_control</span> 断点</strong>，横跨 <span class="mono">tools</span>、<span class="mono">system</span>、<span class="mono">messages</span> 三处一起算。<strong>打到第 5 个，API 直接返回 400</strong>。</p>
<p>于是 opencode 的 lowering 层要解一道「<strong>预算分配</strong>」题：把规范请求翻成 Anthropic 体时，可能有一大堆地方都「想」打缓存标记，但总共只有 4 个名额。它的解法干净利落——<strong>带着一个可变的「预算计数器」<span class="mono">Breakpoints{remaining, dropped}</span> 穿过所有的 <span class="mono">lower*</span> 函数</strong>，每打一个标记就 <span class="mono">remaining--</span>，名额用完后，后面再想打的，就 <span class="mono">dropped++</span> 然后悄悄放弃（返回 <span class="mono">undefined</span>，不打）。绝不让标记数超过 4，从源头上杜绝那个 400。这里的<strong>顺序</strong>也有讲究：计数器是按 <span class="mono">tools → system → messages</span> 的次序消耗的，也就是说<strong>越靠前缀、越稳定的部分，越优先拿到宝贵的缓存名额</strong>——这恰好和「缓存的是前缀」这件事严丝合缝，把有限的 4 个名额花在最该缓存的地方：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">起</span><span class="t-txt">newBreakpoints(4) → {remaining:4, dropped:0}</span></div>
  <div class="t-row"><span class="t-num">tools</span><span class="t-txt">某工具想缓存 → remaining 4→3，打 ephemeral 标记</span></div>
  <div class="t-row"><span class="t-num">system</span><span class="t-txt">系统提示想缓存 → remaining 3→2，打标记</span></div>
  <div class="t-row"><span class="t-num">messages</span><span class="t-txt">两处历史想缓存 → remaining 2→1→0，打标记</span></div>
  <div class="t-row"><span class="t-num">第5个</span><span class="t-txt">又有一处想缓存 → remaining=0，dropped++，悄悄放弃（不打）</span></div>
</div>
<p>这段代码的<strong>克制</strong>体现在两点。其一，<strong>「悄悄放弃」而非「报错」</strong>：超额的缓存标记被默默丢掉，请求照常发出去——缓存只是优化，不该因为「想多缓存」反而把请求搞挂。其二，<strong>TTL 也被简化成两档</strong>：<span class="mono">ttlBucket</span> 把任何 ≥3600 秒的请求归为 <span class="mono">"1h"</span>，否则就是默认的 5 分钟——因为 Anthropic 只认这两档。还有个值得一提的工程决策：这套「4 个上限 + TTL 两档」的逻辑，被抽到了 <span class="mono">protocols/utils/cache.ts</span> 里<strong>共享</strong>，因为<strong>Bedrock 上的 Claude 也吃同一套规矩</strong>（第 32 课会再遇到它）。同一条供应商约束，被两个协议复用——又一处「把共性抽出来」的复利。</p>
<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p>预算计数器的核心，就是这个 <span class="mono">cacheControl</span> 函数（简化自 anthropic-messages.ts）：</p>
  <pre class="code"><span class="cm">// 每个想打缓存标记的地方都调它，共享同一个 breakpoints</span>
<span class="kw">const</span> <span class="fn">cacheControl</span> = (breakpoints, cache) =&gt; {
  <span class="kw">if</span> (cache?.type !== <span class="st">"ephemeral"</span> &amp;&amp; cache?.type !== <span class="st">"persistent"</span>) <span class="kw">return</span> undefined
  <span class="kw">if</span> (breakpoints.remaining &lt;= 0) {   <span class="cm">// 预算用完</span>
    breakpoints.dropped += 1          <span class="cm">// 记一笔「想打但没打」</span>
    <span class="kw">return</span> undefined                  <span class="cm">// 悄悄放弃</span>
  }
  breakpoints.remaining -= 1          <span class="cm">// 花掉一个名额</span>
  <span class="kw">return</span> Cache.<span class="fn">ttlBucket</span>(cache.ttlSeconds) === <span class="st">"1h"</span> ? EPHEMERAL_1H : EPHEMERAL_5M
}</pre>
  <p>注意 <span class="mono">breakpoints</span> 是一个被各处<strong>共享并就地修改</strong>的对象——这是少见的、刻意的可变状态。为什么这里不学第 29 课 <span class="mono">step</span> 那样「显式传新状态」？因为这是<strong>纯本地、单趟、一次性</strong>的编码过程：在一个 <span class="mono">body.from</span> 调用内，从头到尾串行地把请求各部分翻一遍，用一个共享计数器是最直白的写法。<strong>状态机要可预测、可重放，所以显式传状态；一趟性的预算分配只图直白，所以就地改一个计数器。</strong>什么场景配什么手法，这套代码拿捏得相当精准。</p>
</div>

<h2>回来的流：Anthropic 的事件词汇表</h2>
<p>填完 <span class="mono">body</span>（出去），再看 <span class="mono">stream</span>（回来）。Anthropic 的流式响应，有一套自己的 SSE 事件词汇，<span class="mono">stream.step</span> 状态机就是顺着这套词汇把碎片拼回规范 <span class="mono">LLMEvent</span> 的：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">message_start</span><span class="t-txt">一轮回复开始，带初始 usage（输入 token 数等）</span></div>
  <div class="t-row"><span class="t-num">content_block_start</span><span class="t-txt">一个内容块开始（text / tool_use / 服务端工具结果整块到达）</span></div>
  <div class="t-row"><span class="t-num">content_block_delta</span><span class="t-txt">块内增量：text_delta 文字片段 / input_json_delta 工具参数片段</span></div>
  <div class="t-row"><span class="t-num">content_block_stop</span><span class="t-txt">一个块结束</span></div>
  <div class="t-row"><span class="t-num">message_delta</span><span class="t-txt">带 stop_reason 和最终 usage（输出 token 数）</span></div>
  <div class="t-row"><span class="t-num">message_stop</span><span class="t-txt">整轮回复结束</span></div>
</div>
<p>这正是第 29 课那台状态机的真实样貌：<span class="mono">tool_use</span> 的参数 JSON 通过一串 <span class="mono">input_json_delta</span> <strong>跨多帧</strong>到齐，State 一路把它们拼起来，等 <span class="mono">content_block_stop</span> 才吐出完整工具调用——和我们上一课预想的分毫不差。有几个 Anthropic 特有的处理细节很见功力：<strong>用量要合并</strong>——usage 在 <span class="mono">message_start</span>（输入侧）和 <span class="mono">message_delta</span>（输出侧）<strong>各出现一次</strong>，<span class="mono">mergeUsage</span> 把两半并成一个完整的 Usage；<strong>缓存用量也被翻译</strong>——<span class="mono">cache_read_input_tokens</span> / <span class="mono">cache_creation_input_tokens</span> 被映射成规范 Usage 里的 cacheRead / cacheWrite（你打的那些缓存断点，省没省钱，这里见分晓）；<strong>思考 token 不单列</strong>——Anthropic 把 thinking 算进 output_tokens，所以规范 reasoningTokens 留 <span class="mono">undefined</span>，老老实实不编造。还有 <span class="mono">stop_reason</span> 的翻译：<span class="mono">"tool_use" → "tool-calls"</span> 等，把 Anthropic 的措辞对回规范的 FinishReason。</p>
<p>单把「用量翻译」这一格拎出来看，最能体现适配器的「<strong>翻译</strong>」本质——左边是 Anthropic 的字段名，右边是 core 认的规范字段，<span class="mono">mapUsage</span> 做的就是这张对照表：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">input_tokens</div><div class="c-txt">→ 规范 inputTokens（未命中缓存的输入）</div></div>
  <div class="cell"><div class="c-tag">output_tokens</div><div class="c-txt">→ 规范 outputTokens（含 thinking，不单列）</div></div>
  <div class="cell"><div class="c-tag">cache_read_input_tokens</div><div class="c-txt">→ 规范 cacheRead（缓存命中，便宜）</div></div>
  <div class="cell"><div class="c-tag">cache_creation_input_tokens</div><div class="c-txt">→ 规范 cacheWrite（首次写缓存）</div></div>
</div>
<p>这张小小的对照表，恰恰是第 28 课「反腐层」最具体的注脚：上层的 agent 循环只认 <span class="mono">inputTokens/outputTokens/cacheRead/cacheWrite</span> 这几个规范名字，<strong>从不需要知道</strong> Anthropic 管它们叫 <span class="mono">input_tokens</span> 还是 <span class="mono">cache_creation_input_tokens</span>。供应商今天改个字段名、明天加个计费项，冲击都被挡在 <span class="mono">mapUsage</span> 这一道墙上，墙内岿然不动。<strong>一个适配器的价值，往往就藏在这种不起眼的「字段改名」里</strong>——它把外部世界的善变，翻译成内部世界的安稳。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <p>L29 给了空白的表，L30 是第一份填好的表——Anthropic 这份方言的全貌：</p>
  <ul>
    <li><strong>body（出去）= lower* 系列函数</strong>：把规范请求翻成 Anthropic 体——内容拆成<strong>带类型的块</strong>（text/image/tool_use/tool_result/服务端工具…），system 单拎成<strong>顶层字段</strong>。</li>
    <li><strong>签名特性①「一切皆块」</strong>：每段内容都是带 <span class="mono">type</span> 的结构化块，可单独挂 <span class="mono">cache_control</span> 元数据。</li>
    <li><strong>签名特性②「4 个缓存断点预算」</strong>：跨 tools/system/messages 最多 4 个 ephemeral 标记，超额 400；用可变 <span class="mono">Breakpoints{remaining,dropped}</span> 计数器穿过 lower*，超了就悄悄丢。逻辑与 Bedrock <strong>共享</strong>于 utils/cache.ts。</li>
    <li><strong>stream（回来）</strong>：message_start→content_block_start/delta/stop→message_delta→message_stop；工具参数跨帧累积、usage 两半合并、缓存用量回译、思考 token 不单列。</li>
  </ul>
  <p>一条值得你串起来的线：<strong>缓存断点和第 24 课的 Context Epoch 是天作之合</strong>。Context Epoch 拼命维持「基线前缀稳定」，图的是什么？图的正是让 Anthropic 这个缓存前缀<strong>持续命中</strong>——前缀稳，缓存才不失效，省下的就是真金白银。上层「稳住前缀」的苦心，到这一层「缓存断点」上兑现成了账单上的数字。这就是读源码内幕的乐趣：两个相隔六课、看似无关的设计，在这里悄悄咬合上了，彼此成全。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li>Anthropic Messages 协议是第一份「填好的 <span class="mono">Protocol</span> 表」（<span class="mono">protocols/anthropic-messages.ts</span>），opencode 的主力方言（Claude 走这条）。</li>
    <li><strong>一切皆块</strong>：内容拆成带 <span class="mono">type</span> 的结构化块（text/image/tool_use/tool_result/server_tool_use/服务端工具结果）；<strong>system 是顶层独立字段</strong>（区别于 OpenAI 把它当首条消息）——正是适配器要吸收的方言差异。</li>
    <li><strong>4 个缓存断点预算</strong>：跨 tools/system/messages 最多 4 个 <span class="mono">cache_control: ephemeral</span> 标记，超额报 400；lowering 层用可变 <span class="mono">Breakpoints{remaining,dropped}</span> 计数器穿过 <span class="mono">lower*</span>，花完名额就 <span class="mono">dropped++</span> 悄悄放弃（不报错）。TTL 两档：≥3600s→"1h"，否则 5m。</li>
    <li>这套缓存逻辑抽到 <span class="mono">utils/cache.ts</span> 与 <strong>Bedrock 共享</strong>（同一供应商约束，两协议复用）。可变计数器是刻意的本地、单趟手法，区别于状态机的显式传状态。</li>
    <li><strong>stream</strong>：message_start/content_block_*/message_delta/message_stop；工具参数经 input_json_delta 跨帧累积；usage 两半 <span class="mono">mergeUsage</span> 合并、缓存用量回译为 cacheRead/cacheWrite、思考 token 不单列。缓存断点与第 24 课 Context Epoch「稳基线前缀」遥相呼应。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Last lesson we learned the blank "two-column form" (the <span class="mono">Protocol</span> interface) inside out: <span class="mono">body</span> owns out, <span class="mono">stream</span> owns back. This lesson we look at <strong>the first form actually filled in</strong>—the Anthropic Messages protocol. It's opencode's "primary dialect" (the Claude family rides this), and the one that fills the form with the most personality. Reading it isn't just learning one protocol—it's <strong>the first time we see "the skeleton grow flesh."</strong> Anthropic's filling has two signature quirks worth remembering forever: one, <strong>"everything is a block"</strong>—request and response content are both split into typed "content blocks"; two, <strong>"a budget of four cache breakpoints"</strong>—a constraint so neat it's almost harsh, which forces out a rather beautiful piece of budget-management code.</p>
<p>Why lead with Anthropic? Because its design <strong>best captures the weight of "protocol = dialect."</strong> The same "send a conversation, take a reply," yet Anthropic insists you pack content into <strong>labeled boxes</strong>, insists the system prompt be <strong>hoisted into its own top-level field</strong>, and insists on a <strong>hard cache cap that 400s if exceeded</strong>. These "insists" are the dialect's accent. And what opencode's <span class="mono">body.from</span> (here a family of <span class="mono">lower*</span> functions) does is translate core's accent-free canonical request, word by word, into Anthropic-accented speech. Understand this translation and you understand the full weight of the word "adapter."</p>

<div class="card analogy">
  <div class="tag">📦 Analogy</div>
  Imagine, on behalf of the chief, you fill out a customs form for an especially rule-bound contractor (Anthropic). This one has two dead rules. <strong>Rule one: everything goes into "labeled standard boxes"</strong>—text one box (text), image one box (image), "please run this tool" one box (tool_use), "here's the tool's result" another box (tool_result). No loose packing, no mixed packing, even "system notice" must go alone into the form's <strong>header field</strong>, not mixed in with cargo. <strong>Rule two is even sharper: you get only 4 "priority cache" stickers total.</strong> To make the contractor "remember, don't recompute" certain boxes, you stick one; but there are only 4 stickers, and sticking a 5th gets the whole form bounced on the spot (a 400 error). So you must <strong>budget carefully</strong>: count stickers as you pack, and once 4 are used, anything else you'd have stuck you can only <strong>quietly note "wanted to but didn't," then give up</strong>. These two dead rules—standard boxes, sticker budget—are exactly the sharpest accent of this Anthropic protocol.
</div>

<h2>Everything is a "block": typed content boxes</h2>
<p>Open <span class="mono">protocols/anthropic-messages.ts</span> and the first thing hitting you is a long run of "block" types defined by <span class="mono">Schema.tag(...)</span>. Unlike some protocols that stuff message content into one big string, Anthropic requires <strong>every piece of content be a structured block with a <span class="mono">type</span> tag</strong>:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">text</div><div class="c-txt">plain text block</div></div>
  <div class="cell"><div class="c-tag">image</div><div class="c-txt">image block (multimodal input)</div></div>
  <div class="cell"><div class="c-tag">tool_use</div><div class="c-txt">assistant wants to call a tool (with id, name, input)</div></div>
  <div class="cell"><div class="c-tag">tool_result</div><div class="c-txt">returning a tool result (with matching tool_use_id)</div></div>
  <div class="cell"><div class="c-tag">server_tool_use</div><div class="c-txt">server-side tool (e.g. web search, run by the vendor itself)</div></div>
  <div class="cell"><div class="c-tag">*_tool_result</div><div class="c-txt">server tool results (web_search/code_execution/web_fetch, inlined whole)</div></div>
</div>
<p>This "everything is a block" design buys <strong>clear structure, validatability, and metadata-carrying</strong>—each block can hang its own <span class="mono">cache_control</span> (the star of the next section). There's also an interesting asymmetry hidden here: a regular <span class="mono">tool_use</span> (client tool) is a <strong>three-step round trip</strong> of "assistant asks, opencode runs it locally, sends back a <span class="mono">tool_result</span>"; but those few <strong>server-side tools</strong> (<span class="mono">web_search</span> / <span class="mono">code_execution</span> / <span class="mono">web_fetch</span>) are <strong>run by the vendor itself, with results inlined whole</strong> into the assistant turn—the source comment notes they "<strong>arrive whole, with no streaming deltas</strong>," with no client-side <span class="mono">tool_result</span> round trip. A "block"'s type tag actually encodes an execution-semantics difference of "who runs this tool," showing how refined this block-type design is. Another easily-missed detail: <strong>the system prompt in Anthropic is not a message but a separate top-level field of the request body</strong>, typed as "an array of text blocks." This is a <strong>wholly different dialect</strong> from OpenAI treating system as the first "role: system" message in messages—and this is exactly why protocol adapters exist: core has only one canonical system, which in this Anthropic <span class="mono">body.from</span> becomes the top-level <span class="mono">system</span> field; in lesson 31's OpenAI filling it becomes the first entry of the messages array. <strong>One canonical concept, two dialects, two placements</strong>—the difference the adapter quietly absorbs.</p>
<div class="cols">
  <div class="col"><h4>Anthropic's placement</h4><p><span class="mono">system</span> is a top-level field (array of text blocks); each <span class="mono">messages</span> entry's content is a "block array."</p></div>
  <div class="col"><h4>core's canonical</h4><p>core has only one accent-free system + message list; doesn't and shouldn't know who places it where.</p></div>
</div>
<p>Drawn as a pipeline, this "translation" is the work chain of <span class="mono">body.from</span> (the <span class="mono">lower*</span> family) below: the canonical request comes in, tools get translated by <span class="mono">lowerTool</span> into Anthropic tools carrying <span class="mono">input_schema</span>, system gets spread into a text-block array placed top-level, each message's content gets translated segment by segment into matching blocks, finally assembled into a full Anthropic request body. Running through the whole chain is <strong>a red thread of "cache budget"</strong> (next section), which is why each <span class="mono">lower*</span> function eats a <span class="mono">breakpoints</span> parameter:</p>
<div class="flow">
  <div class="f-node">LLMRequest<br><small>canonical request</small></div>
  <div class="f-arrow">lowerTool →</div>
  <div class="f-node">tools[]<br><small>with input_schema</small></div>
  <div class="f-arrow">+ system →</div>
  <div class="f-node">top-level system<br><small>text-block array</small></div>
  <div class="f-arrow">+ lowerMessages →</div>
  <div class="f-node">Anthropic Body<br><small>messages all blocks</small></div>
</div>

<h2>Four cache breakpoints' budget: a beautiful piece of "thrift" code</h2>
<p>This is the passage in the Anthropic protocol I most want you to savor. First the background: Anthropic supports <strong>prompt caching</strong>—you can mark certain blocks with <span class="mono">cache_control: {type: ephemeral}</span>, telling the server "the prefix from the start to this marker, please cache it, don't recompute the same prefix next time." This <strong>saves serious money and latency</strong> (cache-hit tokens are far cheaper). But Anthropic has a hard constraint: <strong>at most 4 <span class="mono">cache_control</span> breakpoints per request</strong>, counted together across <span class="mono">tools</span>, <span class="mono">system</span>, and <span class="mono">messages</span>. <strong>Hit a 5th and the API returns 400 outright.</strong></p>
<p>So opencode's lowering layer must solve a "<strong>budget allocation</strong>" puzzle: translating the canonical request into the Anthropic body, many places may "want" a cache marker, but there are only 4 slots total. Its solution is crisp—<strong>carry a mutable "budget counter" <span class="mono">Breakpoints{remaining, dropped}</span> through all the <span class="mono">lower*</span> functions</strong>, decrement <span class="mono">remaining--</span> per marker emitted, and once slots run out, anything else wanting a marker does <span class="mono">dropped++</span> then quietly gives up (returns <span class="mono">undefined</span>, no marker). Never letting the marker count exceed 4, killing that 400 at the source. The <strong>order</strong> matters too: the counter is consumed in <span class="mono">tools → system → messages</span> order, meaning <strong>the more prefix-y and stable a part, the higher its priority for a precious cache slot</strong>—which dovetails exactly with "the cache caches a prefix," spending the limited 4 slots where caching matters most:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">start</span><span class="t-txt">newBreakpoints(4) → {remaining:4, dropped:0}</span></div>
  <div class="t-row"><span class="t-num">tools</span><span class="t-txt">a tool wants caching → remaining 4→3, emit ephemeral marker</span></div>
  <div class="t-row"><span class="t-num">system</span><span class="t-txt">system prompt wants caching → remaining 3→2, emit marker</span></div>
  <div class="t-row"><span class="t-num">messages</span><span class="t-txt">two history spots want caching → remaining 2→1→0, emit markers</span></div>
  <div class="t-row"><span class="t-num">5th</span><span class="t-txt">another wants caching → remaining=0, dropped++, quietly give up</span></div>
</div>
<p>This code's <strong>restraint</strong> shows in two places. First, <strong>"quietly give up" rather than "error"</strong>: excess cache markers are silently dropped, the request goes out as usual—caching is only an optimization, it shouldn't break the request just because you "wanted to cache more." Second, <strong>TTL is also simplified to two buckets</strong>: <span class="mono">ttlBucket</span> maps any request ≥3600 seconds to <span class="mono">"1h"</span>, otherwise the default 5 minutes—because Anthropic only recognizes these two. One more engineering decision worth noting: this "4-cap + two TTL buckets" logic is hoisted into <span class="mono">protocols/utils/cache.ts</span> to be <strong>shared</strong>, because <strong>Claude on Bedrock eats the same rules</strong> (lesson 32 meets it again). One provider constraint, reused by two protocols—another instance of "factor out the commonality" compounding.</p>
<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p>The heart of the budget counter is this <span class="mono">cacheControl</span> function (simplified from anthropic-messages.ts):</p>
  <pre class="code"><span class="cm">// every spot wanting a cache marker calls it, sharing one breakpoints</span>
<span class="kw">const</span> <span class="fn">cacheControl</span> = (breakpoints, cache) =&gt; {
  <span class="kw">if</span> (cache?.type !== <span class="st">"ephemeral"</span> &amp;&amp; cache?.type !== <span class="st">"persistent"</span>) <span class="kw">return</span> undefined
  <span class="kw">if</span> (breakpoints.remaining &lt;= 0) {   <span class="cm">// budget exhausted</span>
    breakpoints.dropped += 1          <span class="cm">// note a "wanted-but-didn't"</span>
    <span class="kw">return</span> undefined                  <span class="cm">// quietly give up</span>
  }
  breakpoints.remaining -= 1          <span class="cm">// spend a slot</span>
  <span class="kw">return</span> Cache.<span class="fn">ttlBucket</span>(cache.ttlSeconds) === <span class="st">"1h"</span> ? EPHEMERAL_1H : EPHEMERAL_5M
}</pre>
  <p>Note <span class="mono">breakpoints</span> is an object <strong>shared and mutated in place</strong> across many spots—a rare, deliberate piece of mutable state. Why not follow lesson 29's <span class="mono">step</span> and "thread new state explicitly"? Because this is a <strong>purely local, single-pass, one-shot</strong> encoding process: within one <span class="mono">body.from</span> call, you serially translate the request's parts start to finish, and a shared counter is the most direct way. <strong>A state machine must be predictable and replayable, so thread state explicitly; a one-pass budget allocation just wants directness, so mutate a counter in place.</strong> Which technique fits which scene—this code gets the call just right.</p>
</div>

<h2>The stream back: Anthropic's event vocabulary</h2>
<p>Having filled <span class="mono">body</span> (out), look at <span class="mono">stream</span> (back). Anthropic's streaming response has its own SSE event vocabulary, and the <span class="mono">stream.step</span> state machine follows that vocabulary to piece fragments back into canonical <span class="mono">LLMEvent</span>s:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">message_start</span><span class="t-txt">a reply turn begins, with initial usage (input token count, etc.)</span></div>
  <div class="t-row"><span class="t-num">content_block_start</span><span class="t-txt">a content block begins (text / tool_use / server tool result arrives whole)</span></div>
  <div class="t-row"><span class="t-num">content_block_delta</span><span class="t-txt">in-block deltas: text_delta text fragment / input_json_delta tool-arg fragment</span></div>
  <div class="t-row"><span class="t-num">content_block_stop</span><span class="t-txt">a block ends</span></div>
  <div class="t-row"><span class="t-num">message_delta</span><span class="t-txt">carries stop_reason and final usage (output token count)</span></div>
  <div class="t-row"><span class="t-num">message_stop</span><span class="t-txt">the whole reply turn ends</span></div>
</div>
<p>This is the real face of lesson 29's state machine: a <span class="mono">tool_use</span>'s argument JSON arrives <strong>across many frames</strong> via a run of <span class="mono">input_json_delta</span>, State pieces them together all the way, and only at <span class="mono">content_block_stop</span> emits the complete tool call—exactly as we predicted last lesson. A few Anthropic-specific handling details show real skill: <strong>usage must be merged</strong>—usage appears <strong>once each</strong> on <span class="mono">message_start</span> (input side) and <span class="mono">message_delta</span> (output side), and <span class="mono">mergeUsage</span> combines the two halves into one complete Usage; <strong>cache usage is translated too</strong>—<span class="mono">cache_read_input_tokens</span> / <span class="mono">cache_creation_input_tokens</span> map to cacheRead / cacheWrite in canonical Usage (whether your cache breakpoints saved money shows up here); <strong>thinking tokens aren't broken out</strong>—Anthropic counts thinking into output_tokens, so canonical reasoningTokens stays <span class="mono">undefined</span>, honestly not fabricating. And <span class="mono">stop_reason</span> translation: <span class="mono">"tool_use" → "tool-calls"</span> etc., mapping Anthropic's wording back to canonical FinishReason.</p>
<p>Pull out just the "usage translation" cell and it best captures the adapter's "<strong>translation</strong>" essence—left are Anthropic's field names, right are core's recognized canonical fields, and <span class="mono">mapUsage</span> is this lookup table:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">input_tokens</div><div class="c-txt">→ canonical inputTokens (non-cached input)</div></div>
  <div class="cell"><div class="c-tag">output_tokens</div><div class="c-txt">→ canonical outputTokens (incl. thinking, not broken out)</div></div>
  <div class="cell"><div class="c-tag">cache_read_input_tokens</div><div class="c-txt">→ canonical cacheRead (cache hit, cheap)</div></div>
  <div class="cell"><div class="c-tag">cache_creation_input_tokens</div><div class="c-txt">→ canonical cacheWrite (first cache write)</div></div>
</div>
<p>This tiny lookup table is the most concrete footnote to lesson 28's "anti-corruption layer": the upper agent loop knows only the canonical names <span class="mono">inputTokens/outputTokens/cacheRead/cacheWrite</span>, and <strong>never needs to know</strong> Anthropic calls them <span class="mono">input_tokens</span> or <span class="mono">cache_creation_input_tokens</span>. The vendor renaming a field today, adding a billing item tomorrow—the impact is all blocked at the <span class="mono">mapUsage</span> wall, the inside unmoved. <strong>An adapter's value often hides in such unremarkable "field renames"</strong>—translating the outside world's fickleness into the inside world's calm.</p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>L29 gave the blank form, L30 is the first filled-in form—the full picture of Anthropic's dialect:</p>
  <ul>
    <li><strong>body (out) = the lower* family</strong>: translates the canonical request into the Anthropic body—content split into <strong>typed blocks</strong> (text/image/tool_use/tool_result/server tools…), system hoisted into a <strong>top-level field</strong>.</li>
    <li><strong>Signature quirk ① "everything is a block"</strong>: each piece of content is a structured block with a <span class="mono">type</span>, able to hang its own <span class="mono">cache_control</span> metadata.</li>
    <li><strong>Signature quirk ② "4 cache breakpoints budget"</strong>: at most 4 ephemeral markers across tools/system/messages, 400 if exceeded; a mutable <span class="mono">Breakpoints{remaining,dropped}</span> counter threads through lower*, dropping silently past the cap. Logic <strong>shared</strong> with Bedrock in utils/cache.ts.</li>
    <li><strong>stream (back)</strong>: message_start→content_block_start/delta/stop→message_delta→message_stop; tool args accumulate across frames, usage's two halves merged, cache usage back-translated, thinking tokens not broken out.</li>
  </ul>
  <p>A thread worth tying together: <strong>cache breakpoints and lesson 24's Context Epoch are a match made in heaven</strong>. Context Epoch works hard to keep the "baseline prefix stable"—for what? Precisely to keep this Anthropic cache prefix <strong>hitting continuously</strong>—a stable prefix means the cache doesn't invalidate, and what's saved is hard cash. The upper layer's pains to "hold the prefix steady" cash out, at this "cache breakpoint" layer, into numbers on the bill. That's the joy of reading source internals: two designs six lessons apart, seemingly unrelated, quietly mesh here, each completing the other.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li>The Anthropic Messages protocol is the first "filled-in <span class="mono">Protocol</span> form" (<span class="mono">protocols/anthropic-messages.ts</span>), opencode's primary dialect (Claude rides this).</li>
    <li><strong>Everything is a block</strong>: content split into structured blocks with a <span class="mono">type</span> (text/image/tool_use/tool_result/server_tool_use/server tool results); <strong>system is a top-level field</strong> (vs OpenAI treating it as the first message)—exactly the dialect difference the adapter absorbs.</li>
    <li><strong>4 cache breakpoints budget</strong>: at most 4 <span class="mono">cache_control: ephemeral</span> markers across tools/system/messages, 400 if exceeded; the lowering layer threads a mutable <span class="mono">Breakpoints{remaining,dropped}</span> counter through <span class="mono">lower*</span>, and once slots are spent does <span class="mono">dropped++</span> and quietly gives up (no error). Two TTL buckets: ≥3600s→"1h", else 5m.</li>
    <li>This cache logic is hoisted into <span class="mono">utils/cache.ts</span> and <strong>shared with Bedrock</strong> (one provider constraint, two protocols reusing). The mutable counter is a deliberate local, single-pass technique, distinct from a state machine's explicit state threading.</li>
    <li><strong>stream</strong>: message_start/content_block_*/message_delta/message_stop; tool args accumulate across frames via input_json_delta; usage's two halves <span class="mono">mergeUsage</span>'d, cache usage back-translated to cacheRead/cacheWrite, thinking tokens not broken out. Cache breakpoints echo lesson 24's Context Epoch "stable baseline prefix."</li>
  </ul>
</div>
""",
}
LESSON_31 = {
    "zh": r"""
<p class="lead">第 30 课我们看了 Anthropic 这份「填好的表」。这一课的主角换成 OpenAI——而它有个别家都没有的特殊之处：<strong>OpenAI 自己就要两份协议</strong>。一份是老牌的 Chat Completions（<span class="mono">/chat/completions</span>），一份是新生的 Responses（<span class="mono">/responses</span>）。为什么一家供应商要填两张表？这背后是一段「<strong>API 正在新老交替</strong>」的真实历史，opencode 选择<strong>两边都支持</strong>。更妙的是，正因为「协议」和「供应商」是解耦的（第 28 课），那份老牌的 Chat 协议还顺手撑起了<strong>大半个生态</strong>——一个只有 24 行的小文件，就让一大票「OpenAI 兼容」厂商免费接了进来。这一课，你会亲眼看到第 28 课那句「实现一次、白嫖整个生态」<strong>如何在源码里兑现</strong>。</p>
<p>这一课的看点有三：其一，<strong>为什么 OpenAI 要两份协议</strong>，两份各自长什么样、差在哪；其二，新的 Responses 协议带来了一个 Anthropic 那边见过、但解法不同的东西——<strong>把「推理」当成一等公民</strong>；其三，也是最过瘾的，<strong>那个 24 行的「兼容」协议</strong>，如何用近乎白送的代价，把「协议≠供应商」这条设计原则的回报，一次性兑现给你看。</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  想象 OpenAI 是一家老牌电器厂，正处在「换插头制式」的过渡期。<strong>旧制式（Chat）</strong>用了多年、满世界都是，几乎成了行业事实标准——连别家厂的电器，都纷纷做成「兼容这个旧制式」的样子。<strong>新制式（Responses）</strong>是这家厂刚推的，更先进：能记住电器「上次运转到哪」（服务端状态）、还专门留了个插孔记录「机器思考的过程」（推理）。这家厂自己<strong>新旧两种插座都装</strong>，让你按需用。而最划算的一幕是：因为「插头制式」和「具体电器」是两回事，opencode 只要实现了那个<strong>旧制式插座</strong>，那一大票「兼容旧制式」的别家电器——OpenRouter、xAI、本地模型……——<strong>全都自动能插上，一行新代码都不用加</strong>。同一套插座，白白多接了半个行业的电器，这就是「制式与电器解耦」的复利。
</div>

<h2>为什么 OpenAI 要两份协议</h2>
<p>翻开 <span class="mono">protocols/</span> 目录，你会发现 OpenAI 占了<strong>两个文件</strong>：<span class="mono">openai-chat.ts</span> 和 <span class="mono">openai-responses.ts</span>。这不是冗余，而是忠实地反映了现实——OpenAI 的 API <strong>正处在从 Chat 向 Responses 迁移的中途</strong>。Chat Completions 是那个用了多年、被全世界当成事实标准的老接口；Responses 是 OpenAI 新设计的、更强大的接口。两者都还活着、都有人用，opencode 于是<strong>两份都填</strong>，让用户按模型按需选。把两份表并排看，差异一目了然：</p>
<div class="cols">
  <div class="col"><h4>Chat（<span class="mono">/chat/completions</span>）老牌</h4><p>消息是<strong>扁平的角色联合</strong>：system / user / assistant（带 tool_calls）/ tool（带 tool_call_id）。content 多为字符串，工具调用挂在 assistant 上。简单、稳定、举世通用。</p></div>
  <div class="col"><h4>Responses（<span class="mono">/responses</span>）新锐</h4><p>输入输出都是<strong>带类型的「条目」数组</strong>：input_text / output_text / reasoning / function_call / function_call_output / item_reference。能携带服务端状态、把推理当一等公民。更结构化、更强大。</p></div>
</div>
<p>先看老牌的 Chat。它的消息模型是一个<strong>按 role 标签的联合类型</strong>，朴素得让人安心：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">system</div><div class="c-txt">系统提示，content 是字符串（区别于 Anthropic 的顶层字段！）</div></div>
  <div class="cell"><div class="c-tag">user</div><div class="c-txt">用户消息</div></div>
  <div class="cell"><div class="c-tag">assistant</div><div class="c-txt">助手回复，工具调用挂在 tool_calls: [{type:function, function:{name,arguments}}]</div></div>
  <div class="cell"><div class="c-tag">tool</div><div class="c-txt">工具结果，靠 tool_call_id 对应回某次调用</div></div>
</div>
<p>这套模型为什么能成为「事实标准」？恰恰因为它<strong>足够朴素</strong>：四种角色、一个扁平数组、工具调用就是 assistant 上挂个列表——没有花哨的嵌套、没有特立独行的字段。越朴素的东西越容易被模仿，于是别家厂商照着它做「兼容」也最省事。这是个反直觉的道理：<strong>Chat 协议的「不够先进」，反而成就了它的「无处不在」</strong>。而 Responses 的先进（条目、推理托管、服务端状态），代价就是别家很难照搬——所以你几乎听不到「Responses 兼容」的厂商，却遍地是「Chat 兼容」的厂商。设计上的取舍，就这样写进了生态的版图，也写进了 opencode「为何独独给 OpenAI 备两份协议」的决定里。</p>
<p>对照第 30 课你会立刻品出方言的不同：Anthropic 把 system 拎成顶层字段、把工具调用做成内容块；OpenAI Chat 却把 system 当成 <span class="mono">messages</span> 里普通的一条、把工具调用做成 assistant 消息上的 <span class="mono">tool_calls</span> 数组。<strong>同一套规范概念，两家摆法南辕北辙</strong>——而 core 对这些一无所知，全靠两份 <span class="mono">body.from</span> 各自吸收。流式这边，Chat 用 <span class="mono">delta</span> 增量推送 content 和 tool_calls 片段，末尾给一个 <span class="mono">finish_reason</span>，状态机照样跨帧把工具参数拼起来——和第 29 课的预想严丝合缝：</p>
<div class="flow">
  <div class="f-node">choices[].delta<br><small>content 文字片段</small></div>
  <div class="f-arrow">累积 →</div>
  <div class="f-node">delta.tool_calls<br><small>工具参数 JSON 跨帧</small></div>
  <div class="f-arrow">攒齐 →</div>
  <div class="f-node">finish_reason<br><small>本轮收尾，吐完整事件</small></div>
</div>

<h2>Responses 的新东西：把「推理」当一等公民</h2>
<p>再看新锐的 Responses。它最重要的革新，是把过去藏在模型肚子里的<strong>「推理过程」也变成了协议里的一等条目</strong>。在它的条目类型里，赫然有一个 <span class="mono">reasoning</span> 条目，还带着一个意味深长的字段 <span class="mono">encrypted_content</span>：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">input_text / input_image</div><div class="c-txt">输入条目：文字、图片</div></div>
  <div class="cell"><div class="c-tag">output_text</div><div class="c-txt">输出条目：模型生成的文字</div></div>
  <div class="cell"><div class="c-tag">reasoning</div><div class="c-txt">推理条目，带 encrypted_content（加密的思考过程）</div></div>
  <div class="cell"><div class="c-tag">function_call / _output</div><div class="c-txt">工具调用与结果（结果可含图片等多模态）</div></div>
  <div class="cell"><div class="c-tag">item_reference</div><div class="c-txt">引用服务端已存的条目（靠 id，无需重发）</div></div>
</div>
<p><span class="mono">encrypted_content</span> 这个字段很有故事。模型「想」的那一长串推理，OpenAI 不直接明文给你（怕被滥用/蒸馏），而是给你一团<strong>加密的密文</strong>。你看不懂它，但下一轮把它<strong>原样塞回去</strong>，模型就能「想起」自己上次的思路，接着往下推。这样多轮之间，模型的「思维链」得以延续，而你始终<strong>只是个忠实的搬运工</strong>——拿着一团你读不懂、却能让模型自我延续的密文。这跟第 30 课 Anthropic 的 <span class="mono">signature</span>（给推理块盖个密码学签名）异曲同工：<strong>两家都要解决「让模型信任自己上一轮的推理」，只是一个用签名验真、一个用密文托管。</strong>同一个问题，两种方言两种解法——又一次印证了「协议即方言」。把三家的「推理处理」并排放，这种「同题异解」看得最清楚：</p>
<table class="t">
  <tr><th>协议</th><th>推理是否一等公民</th><th>怎么跨轮延续推理</th></tr>
  <tr><td>OpenAI Chat（老）</td><td>否，无专门表示</td><td>不延续（老接口没这概念）</td></tr>
  <tr><td>OpenAI Responses</td><td>是，reasoning 条目</td><td>encrypted_content 密文，原样回传</td></tr>
  <tr><td>Anthropic Messages</td><td>是，thinking 块</td><td>signature 密码学签名验真</td></tr>
</table>
<p>Responses 还有几处「新接口才有的讲究」：<span class="mono">store</span> 字段决定要不要把这次响应<strong>存在服务端</strong>；配合 <span class="mono">item_reference</span>，下一轮你可以<strong>只用 id 引用</strong>之前的条目、不必整段重发——这是把状态<strong>外包给服务端</strong>的思路，和 Chat「每轮带全量历史」的无状态风格截然不同。它的流式也升级成<strong>基于条目的事件</strong>（条目添加 / 增量 / 完成），State 里专门留了一个 <span class="mono">reasoningItems</span> 记录，把跨帧到达的多段推理摘要<strong>折叠</strong>进同一个条目里再吐出。结构更复杂，但表达力也更强。</p>

<h2>24 行的魔法：一份协议撑起半个生态</h2>
<p>现在来看这一课最过瘾的部分。OpenAI 的 Chat 协议，因为太通用，早已成了<strong>事实标准</strong>——市面上一大票厂商（OpenRouter、xAI、各种本地模型服务……）都把自己的 API 做成「OpenAI Chat 兼容」的样子。opencode 要接住它们，需要为每家重写一遍协议吗？<strong>完全不用。</strong>看 <span class="mono">openai-compatible-chat.ts</span> 这个文件——它<strong>总共只有 24 行</strong>：</p>
<pre class="code"><span class="cm">// openai-compatible-chat.ts 的全部精华</span>
<span class="kw">export const</span> route = Route.<span class="fn">make</span>({
  id: ADAPTER,
  protocol: OpenAIChat.protocol,        <span class="cm">// ← 整份复用 Chat 协议！</span>
  endpoint: Endpoint.<span class="fn">path</span>(<span class="st">"/chat/completions"</span>),  <span class="cm">// 只改端点</span>
  framing: Framing.sse,
})</pre>
<p>它做的事，就一句话：<strong>把 <span class="mono">OpenAIChat.protocol</span> 整个拿过来用</strong>，只覆盖一个 route id（好让不同厂商各自解析、不撞车）和端点路径。请求怎么编码、响应怎么解码——<strong>一个字都没重写</strong>，全是 Chat 协议的原班人马。这 24 行，就是第 28 课那句「把线缆格式抽象成协议、实现一次白嫖整个生态」最掷地有声的证明。其中的杠杆是惊人的：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">投入</span><span class="t-txt">实现 OpenAIChat.protocol 一次（请求编码 + 流解码）</span></div>
  <div class="t-row"><span class="t-num">复用</span><span class="t-txt">openai-compatible-chat：24 行，整份引用 Chat 协议</span></div>
  <div class="t-row"><span class="t-num">收获</span><span class="t-txt">OpenRouter / xAI / 本地模型… 一大票「兼容」厂商全部接入</span></div>
  <div class="t-row"><span class="t-num">增量</span><span class="t-txt">再多一家兼容厂商？协议代码一行不加，配个端点即可</span></div>
</div>
<p>这就是「协议 ≠ 供应商」这条设计原则的<strong>现金回报</strong>。如果当初把协议和供应商揉成一团（每家一套 if 分支），新增一家「OpenAI 兼容」厂商就得复制粘贴一大坨编解码逻辑；而解耦之后，新增一家的成本，<strong>趋近于零</strong>。一个 24 行的文件，胜过千言万语的架构布道。值得再多想一层的是：这 24 行之所以能这么短，<strong>不是因为偷懒，而是因为前面的功夫下到了位</strong>——正因为 Chat 协议把「请求编码」「流解码」干干净净地封装成了一个可复用的 <span class="mono">protocol</span> 对象，复用它才像「拿来即用」这么轻松。<strong>好的抽象，回报往往迟到，但一定会到</strong>：你在 Chat 协议上多花的那份「把编解码和网络分开」的心思，到这里、到每一个新接入的兼容厂商身上，连本带利地还给你。这也是为什么第 29 课要反复强调那张「两栏表」的边界——边界划得清，复用才来得爽。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <p>OpenAI 这一课，把「协议即方言」和「协议≠供应商」两条主线同时推到了高潮：</p>
  <ul>
    <li><strong>一家供应商，两份协议</strong>：Chat（老牌、举世通用的 <span class="mono">/chat/completions</span>）+ Responses（新锐、更结构化的 <span class="mono">/responses</span>）。反映 OpenAI API 新老迁移的真实历史，opencode 两边都填。</li>
    <li><strong>方言对比</strong>：Chat 用扁平角色联合（system/user/assistant+tool_calls/tool）、system 是普通消息；Responses 用带类型条目数组、推理是一等公民。同一规范概念，摆法迥异。</li>
    <li><strong>Responses 的推理一等公民</strong>：<span class="mono">reasoning</span> 条目带 <span class="mono">encrypted_content</span>（加密思维链，原样回传即可续上）+ <span class="mono">store</span>/<span class="mono">item_reference</span>（状态外包服务端）。与第 30 课 Anthropic <span class="mono">signature</span> 殊途同归。</li>
    <li><strong>24 行的复利</strong>：<span class="mono">openai-compatible-chat</span> 整份复用 Chat 协议、只改 id+端点，就让一大票「OpenAI 兼容」厂商免费接入——第 28 课「实现一次白嫖生态」的源码铁证。</li>
  </ul>
  <p>把第 30、31 两课连起来看，你已经摸清了「主流三大家」里的两家半：Anthropic（块 + 缓存预算）、OpenAI Chat（扁平角色 + 生态基石）、OpenAI Responses（条目 + 推理托管）。下一课轮到 <strong>Gemini 与 Bedrock</strong>，你会看到更多方言，以及 Bedrock 那套独特的二进制事件流——但骨架始终是第 29 课那张表，你只需继续问：「这家的 body.from 和 stream.step，特别在哪？」</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p>为什么 24 行就能复用整份协议？关键在 <span class="mono">Route</span> 和 <span class="mono">Protocol</span> 是<strong>正交</strong>的两层。<span class="mono">Route.make</span> 把「协议（怎么编解码）」「端点（打哪个 URL）」「framing（流怎么分帧）」当成<strong>三个可独立替换的零件</strong>拼起来：</p>
  <pre class="code"><span class="cm">// 同一个 protocol，配不同 endpoint，就是不同的 route</span>
OpenAIChat.route       = Route.make({ protocol: OpenAIChat.protocol, endpoint: <span class="st">"openai 官方"</span>, ... })
OpenAICompatible.route = Route.make({ protocol: OpenAIChat.protocol, endpoint: <span class="st">"/chat/completions"</span>, ... })</pre>
  <p>因为编解码逻辑被封装在 <span class="mono">protocol</span> 这个零件里、和「打哪个端点」彻底分开，所以「换个供应商」往往只是「<strong>换个端点、复用同一个 protocol</strong>」。这正是第 29 课强调的分层在这里结出的果：<span class="mono">Protocol</span> 只管方言的编解码、不管网络去向，于是同一种方言能服务无数个说这种方言的供应商。下一课的 Bedrock 会展示反面——同样的 Anthropic 方言，却因为<strong>传输和认证</strong>不同（走 AWS），需要另一份协议；可见 protocol/route 这套正交切分，把「方言相同但网络不同」「网络相同但方言不同」两种情况都拆解得干干净净，各自只动该动的那个零件。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>OpenAI 独有「两份协议」</strong>：<span class="mono">openai-chat.ts</span>（老牌 <span class="mono">/chat/completions</span>）+ <span class="mono">openai-responses.ts</span>（新锐 <span class="mono">/responses</span>），反映其 API 新老迁移；opencode 两边都支持。</li>
    <li><strong>Chat = 扁平角色联合</strong>：system/user/assistant(带 tool_calls)/tool(带 tool_call_id)，system 是普通消息、工具调用挂 assistant——与 Anthropic 的「块 + 顶层 system」是两种方言。</li>
    <li><strong>Responses = 带类型条目 + 推理一等公民</strong>：<span class="mono">reasoning</span> 条目带 <span class="mono">encrypted_content</span>（加密思维链，原样回传即续上，与 Anthropic <span class="mono">signature</span> 殊途同归）；<span class="mono">store</span>/<span class="mono">item_reference</span> 把状态外包服务端；流式基于条目事件、用 <span class="mono">reasoningItems</span> 折叠多段推理。</li>
    <li><strong>24 行的复利</strong>：<span class="mono">openai-compatible-chat.ts</span> 整份复用 <span class="mono">OpenAIChat.protocol</span>、只改 route id + 端点，就让一大票「OpenAI 兼容」厂商（OpenRouter/xAI/本地模型…）免费接入——第 28 课「实现一次白嫖生态」的铁证。</li>
    <li><strong>Route 与 Protocol 正交</strong>：Route.make 把 protocol（编解码）/endpoint（URL）/framing（分帧）当独立零件，「换供应商」常常只是「换端点、复用 protocol」。新增一家兼容厂商成本趋近于零。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Lesson 30 looked at Anthropic's "filled-in form." This lesson's lead is OpenAI—and it has something no other vendor does: <strong>OpenAI alone needs two protocols</strong>. One is the veteran Chat Completions (<span class="mono">/chat/completions</span>), one is the newborn Responses (<span class="mono">/responses</span>). Why does one vendor fill two forms? Behind it is a real history of "<strong>an API mid-migration</strong>," and opencode chooses to <strong>support both sides</strong>. Even better, precisely because "protocol" and "provider" are decoupled (lesson 28), that veteran Chat protocol also props up <strong>half an ecosystem</strong>—a tiny 24-line file lets a crowd of "OpenAI-compatible" vendors plug in for free. This lesson, you'll see with your own eyes how lesson 28's "implement once, free-ride the whole ecosystem" <strong>cashes out in the source</strong>.</p>
<p>Three things to watch this lesson: one, <strong>why OpenAI needs two protocols</strong>, what each looks like and how they differ; two, the new Responses protocol brings something we saw on the Anthropic side but solved differently—<strong>treating "reasoning" as a first-class citizen</strong>; three, and most satisfying, <strong>that 24-line "compatible" protocol</strong>, and how at near-zero cost it cashes out, in one shot, the reward of the "protocol ≠ provider" design principle.</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  Imagine OpenAI is a veteran appliance maker, mid-transition on "changing the plug standard." The <strong>old standard (Chat)</strong> has been used for years and is everywhere, all but the industry's de facto standard—even other makers' appliances are built to "be compatible with this old standard." The <strong>new standard (Responses)</strong> is freshly pushed by this maker, more advanced: it can remember "where the appliance left off" (server-side state), and has a dedicated socket recording "the machine's thinking process" (reasoning). The maker installs <strong>both old and new sockets</strong> itself, letting you use as needed. And the most cost-effective scene: because "plug standard" and "specific appliance" are two different things, once opencode implements that <strong>old-standard socket</strong>, the whole crowd of "old-standard-compatible" appliances from other makers—OpenRouter, xAI, local models…—<strong>all plug in automatically, not a line of new code added</strong>. One socket, half an industry's appliances connected for free—that's the compound interest of "decoupling standard from appliance."
</div>

<h2>Why OpenAI needs two protocols</h2>
<p>Open the <span class="mono">protocols/</span> directory and you'll find OpenAI takes <strong>two files</strong>: <span class="mono">openai-chat.ts</span> and <span class="mono">openai-responses.ts</span>. This isn't redundancy but a faithful reflection of reality—OpenAI's API is <strong>midway through migrating from Chat to Responses</strong>. Chat Completions is the old interface, used for years and treated worldwide as a de facto standard; Responses is OpenAI's newly designed, more powerful interface. Both are still alive and used, so opencode <strong>fills both forms</strong>, letting users choose per model as needed. Lay the two forms side by side and the difference is plain:</p>
<div class="cols">
  <div class="col"><h4>Chat (<span class="mono">/chat/completions</span>) veteran</h4><p>Messages are a <strong>flat role union</strong>: system / user / assistant (with tool_calls) / tool (with tool_call_id). content is mostly a string, tool calls hang on the assistant. Simple, stable, universally adopted.</p></div>
  <div class="col"><h4>Responses (<span class="mono">/responses</span>) upstart</h4><p>Input and output are both <strong>typed "item" arrays</strong>: input_text / output_text / reasoning / function_call / function_call_output / item_reference. Can carry server-side state, treats reasoning as first-class. More structured, more powerful.</p></div>
</div>
<p>First the veteran Chat. Its message model is a <strong>role-tagged union</strong>, reassuringly plain:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">system</div><div class="c-txt">system prompt, content is a string (vs Anthropic's top-level field!)</div></div>
  <div class="cell"><div class="c-tag">user</div><div class="c-txt">user message</div></div>
  <div class="cell"><div class="c-tag">assistant</div><div class="c-txt">assistant reply, tool calls hang on tool_calls: [{type:function, function:{name,arguments}}]</div></div>
  <div class="cell"><div class="c-tag">tool</div><div class="c-txt">tool result, matched back to a call via tool_call_id</div></div>
</div>
<p>Why could this model become the "de facto standard"? Precisely because it's <strong>plain enough</strong>: four roles, one flat array, tool calls just a list hung on the assistant—no fancy nesting, no idiosyncratic fields. The plainer a thing, the easier to mimic, so other vendors building "compatibility" against it have the least work. It's a counterintuitive truth: <strong>Chat protocol's "not-advanced-enough" is exactly what made it "ubiquitous."</strong> And Responses' advancement (items, reasoning custody, server-side state) costs others dearly to copy—so you almost never hear of "Responses-compatible" vendors, while "Chat-compatible" vendors are everywhere. A design tradeoff thus writes itself into the ecosystem's map.</p>
<p>Against lesson 30 you'll immediately taste the dialect difference: Anthropic hoists system into a top-level field, makes tool calls content blocks; OpenAI Chat treats system as an ordinary entry in <span class="mono">messages</span>, makes tool calls a <span class="mono">tool_calls</span> array on the assistant message. <strong>The same canonical concepts, two wildly different placements</strong>—and core knows none of this, relying on the two <span class="mono">body.from</span>s to each absorb it. On streaming, Chat pushes content and tool_calls fragments incrementally via <span class="mono">delta</span>, ending with a <span class="mono">finish_reason</span>, and the state machine still pieces tool args across frames—dovetailing exactly with lesson 29's prediction:</p>
<div class="flow">
  <div class="f-node">choices[].delta<br><small>content text fragment</small></div>
  <div class="f-arrow">accumulate →</div>
  <div class="f-node">delta.tool_calls<br><small>tool-arg JSON across frames</small></div>
  <div class="f-arrow">assembled →</div>
  <div class="f-node">finish_reason<br><small>turn wraps, emit whole event</small></div>
</div>

<h2>Responses' new thing: reasoning as a first-class citizen</h2>
<p>Now the upstart Responses. Its most important innovation is turning the <strong>"reasoning process," once hidden inside the model, into a first-class item in the protocol</strong>. Among its item types sits, prominently, a <span class="mono">reasoning</span> item, carrying a meaningful field <span class="mono">encrypted_content</span>:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">input_text / input_image</div><div class="c-txt">input items: text, image</div></div>
  <div class="cell"><div class="c-tag">output_text</div><div class="c-txt">output item: text the model generates</div></div>
  <div class="cell"><div class="c-tag">reasoning</div><div class="c-txt">reasoning item, with encrypted_content (encrypted thinking)</div></div>
  <div class="cell"><div class="c-tag">function_call / _output</div><div class="c-txt">tool call and result (result may include images etc.)</div></div>
  <div class="cell"><div class="c-tag">item_reference</div><div class="c-txt">reference a server-stored item (by id, no resend)</div></div>
</div>
<p>The <span class="mono">encrypted_content</span> field has a story. The long run of reasoning the model "thinks," OpenAI doesn't give you in plaintext (fearing abuse/distillation), but as a blob of <strong>encrypted ciphertext</strong>. You can't read it, but feed it back <strong>verbatim</strong> next turn and the model "recalls" its prior train of thought and keeps reasoning onward. So across turns, the model's "chain of thought" persists, while you remain <strong>just a faithful carrier</strong>—holding a blob you can't read yet that lets the model continue itself. This rhymes with lesson 30's Anthropic <span class="mono">signature</span> (stamping a cryptographic signature on reasoning blocks): <strong>both solve "let the model trust its own prior reasoning," one via signature verification, one via ciphertext custody.</strong> The same problem, two dialects, two solutions—once more confirming "protocol = dialect." Lay the three vendors' "reasoning handling" side by side and this "same question, different answers" is clearest:</p>
<table class="t">
  <tr><th>Protocol</th><th>Reasoning first-class?</th><th>How reasoning persists across turns</th></tr>
  <tr><td>OpenAI Chat (old)</td><td>No, no dedicated form</td><td>Doesn't persist (old API lacks the concept)</td></tr>
  <tr><td>OpenAI Responses</td><td>Yes, reasoning item</td><td>encrypted_content ciphertext, fed back verbatim</td></tr>
  <tr><td>Anthropic Messages</td><td>Yes, thinking block</td><td>signature cryptographic verification</td></tr>
</table>
<p>Responses has a few more "new-interface-only" niceties: the <span class="mono">store</span> field decides whether to <strong>store this response server-side</strong>; paired with <span class="mono">item_reference</span>, next turn you can <strong>reference prior items by id only</strong>, no need to resend whole segments—an idea of <strong>outsourcing state to the server</strong>, starkly different from Chat's stateless "carry full history each turn." Its streaming also upgrades to <strong>item-based events</strong> (item added / delta / done), with State keeping a dedicated <span class="mono">reasoningItems</span> record that <strong>folds</strong> multi-part reasoning summaries arriving across frames into the same item before emitting. More complex structure, but more expressive too.</p>

<h2>The 24-line magic: one protocol props up half an ecosystem</h2>
<p>Now the most satisfying part of this lesson. OpenAI's Chat protocol, being so universal, long ago became a <strong>de facto standard</strong>—a crowd of vendors (OpenRouter, xAI, all kinds of local model servers…) build their APIs to be "OpenAI Chat compatible." To catch them, must opencode rewrite the protocol for each? <strong>Not at all.</strong> Look at <span class="mono">openai-compatible-chat.ts</span>—it's <strong>24 lines total</strong>:</p>
<pre class="code"><span class="cm">// the entire essence of openai-compatible-chat.ts</span>
<span class="kw">export const</span> route = Route.<span class="fn">make</span>({
  id: ADAPTER,
  protocol: OpenAIChat.protocol,        <span class="cm">// ← reuse the whole Chat protocol!</span>
  endpoint: Endpoint.<span class="fn">path</span>(<span class="st">"/chat/completions"</span>),  <span class="cm">// override only the endpoint</span>
  framing: Framing.sse,
})</pre>
<p>What it does is one sentence: <strong>take <span class="mono">OpenAIChat.protocol</span> wholesale</strong>, override only a route id (so different vendors resolve separately without colliding) and the endpoint path. How the request encodes, how the response decodes—<strong>not a single word rewritten</strong>, all the Chat protocol's original cast. These 24 lines are the most resounding proof of lesson 28's "abstract the wire format into a protocol, implement once, free-ride the whole ecosystem." The leverage is staggering:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">invest</span><span class="t-txt">implement OpenAIChat.protocol once (request encode + stream decode)</span></div>
  <div class="t-row"><span class="t-num">reuse</span><span class="t-txt">openai-compatible-chat: 24 lines, reference the whole Chat protocol</span></div>
  <div class="t-row"><span class="t-num">reap</span><span class="t-txt">OpenRouter / xAI / local models… a crowd of "compatible" vendors all connect</span></div>
  <div class="t-row"><span class="t-num">marginal</span><span class="t-txt">one more compatible vendor? Not a line of protocol code, just configure an endpoint</span></div>
</div>
<p>This is the <strong>cash reward</strong> of the "protocol ≠ provider" design principle. Had protocol and provider been mashed together originally (a set of if-branches per vendor), adding one "OpenAI-compatible" vendor would mean copy-pasting a big lump of codec logic; after decoupling, the cost of adding one <strong>approaches zero</strong>. A 24-line file outweighs a thousand words of architecture preaching. Worth one more layer of thought: these 24 lines can be this short <strong>not from laziness but because the earlier work was done right</strong>—precisely because the Chat protocol cleanly encapsulates "request encode" and "stream decode" into one reusable <span class="mono">protocol</span> object, reusing it is as easy as "plug and play." <strong>A good abstraction's reward often arrives late, but it arrives</strong>: the extra care you spent on the Chat protocol to "separate codec from network" is paid back here, with interest, at every newly-connected compatible vendor. This is why lesson 29 kept stressing that "two-column form"'s boundary—draw the boundary cleanly and reuse comes joyfully.</p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>The OpenAI lesson pushes both threads—"protocol = dialect" and "protocol ≠ provider"—to a climax at once:</p>
  <ul>
    <li><strong>One vendor, two protocols</strong>: Chat (veteran, universal <span class="mono">/chat/completions</span>) + Responses (upstart, more structured <span class="mono">/responses</span>). Reflecting OpenAI's real API old-to-new migration; opencode fills both.</li>
    <li><strong>Dialect contrast</strong>: Chat uses a flat role union (system/user/assistant+tool_calls/tool), system is an ordinary message; Responses uses typed item arrays, reasoning is first-class. Same canonical concepts, divergent placements.</li>
    <li><strong>Responses' first-class reasoning</strong>: <span class="mono">reasoning</span> item with <span class="mono">encrypted_content</span> (encrypted chain of thought, fed back verbatim to continue) + <span class="mono">store</span>/<span class="mono">item_reference</span> (state outsourced server-side). Converges with lesson 30's Anthropic <span class="mono">signature</span> by a different road.</li>
    <li><strong>The 24-line compounding</strong>: <span class="mono">openai-compatible-chat</span> reuses the Chat protocol wholesale, overriding only id+endpoint, letting a crowd of "OpenAI-compatible" vendors connect for free—the source-level ironclad proof of lesson 28's "implement once, free-ride the ecosystem."</li>
  </ul>
  <p>Connect lessons 30 and 31 and you've grasped two-and-a-half of the "big three": Anthropic (blocks + cache budget), OpenAI Chat (flat roles + ecosystem bedrock), OpenAI Responses (items + reasoning custody). Next up is <strong>Gemini and Bedrock</strong>, where you'll see more dialects, plus Bedrock's distinctive binary event stream—but the skeleton is always lesson 29's form, you need only keep asking: "how is this vendor's body.from and stream.step special?"</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p>Why can 24 lines reuse a whole protocol? The key is that <span class="mono">Route</span> and <span class="mono">Protocol</span> are <strong>orthogonal</strong> layers. <span class="mono">Route.make</span> assembles "protocol (how to codec)," "endpoint (which URL to hit)," and "framing (how to frame the stream)" as <strong>three independently swappable parts</strong>:</p>
  <pre class="code"><span class="cm">// same protocol, different endpoint, is a different route</span>
OpenAIChat.route       = Route.make({ protocol: OpenAIChat.protocol, endpoint: <span class="st">"openai official"</span>, ... })
OpenAICompatible.route = Route.make({ protocol: OpenAIChat.protocol, endpoint: <span class="st">"/chat/completions"</span>, ... })</pre>
  <p>Because the codec logic is encapsulated in the <span class="mono">protocol</span> part, fully separate from "which endpoint to hit," "switching providers" is often just "switch endpoint, reuse the same protocol." This is lesson 29's emphasized layering bearing fruit: <span class="mono">Protocol</span> owns only the dialect's codec, not the network destination, so one dialect can serve countless providers speaking it. Next lesson's Bedrock shows the flip side—the same Anthropic dialect, yet because <strong>transport and auth</strong> differ (over AWS), it needs another protocol; showing how this protocol/route orthogonal split cleanly disentangles both "same dialect but different network" and "same network but different dialect," each touching only the part that should change.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>OpenAI uniquely has "two protocols"</strong>: <span class="mono">openai-chat.ts</span> (veteran <span class="mono">/chat/completions</span>) + <span class="mono">openai-responses.ts</span> (upstart <span class="mono">/responses</span>), reflecting its API old-to-new migration; opencode supports both.</li>
    <li><strong>Chat = flat role union</strong>: system/user/assistant(with tool_calls)/tool(with tool_call_id), system is an ordinary message, tool calls hang on the assistant—a different dialect from Anthropic's "blocks + top-level system."</li>
    <li><strong>Responses = typed items + first-class reasoning</strong>: <span class="mono">reasoning</span> item with <span class="mono">encrypted_content</span> (encrypted chain of thought, fed back verbatim to continue, converging with Anthropic's <span class="mono">signature</span> by another road); <span class="mono">store</span>/<span class="mono">item_reference</span> outsource state server-side; item-based streaming folds multi-part reasoning via <span class="mono">reasoningItems</span>.</li>
    <li><strong>The 24-line compounding</strong>: <span class="mono">openai-compatible-chat.ts</span> reuses <span class="mono">OpenAIChat.protocol</span> wholesale, overriding only route id + endpoint, letting a crowd of "OpenAI-compatible" vendors (OpenRouter/xAI/local models…) connect for free—ironclad proof of lesson 28's "implement once, free-ride the ecosystem."</li>
    <li><strong>Route and Protocol are orthogonal</strong>: Route.make treats protocol (codec)/endpoint (URL)/framing as independent parts, so "switching providers" is often just "switch endpoint, reuse protocol." The cost of adding one compatible vendor approaches zero.</li>
  </ul>
</div>
""",
}

LESSON_32 = {
    "zh": r"""
<p class="lead">第 30、31 课我们看了 Anthropic 和 OpenAI 两份「填好的表」。这一课一口气再看两家——Gemini 与 Bedrock，它俩各自带来一个新维度的启发。<strong>Gemini</strong> 是「方言」主题的又一个变奏：它把几乎每个字段都改了名（Google 的 camelCase 风格），还给「推理签名」起了<strong>第三个名字</strong>——至此三大家三种叫法，这张「同物异名」的对照表你看完会会心一笑。而 <strong>Bedrock</strong> 才是这一课真正的主角，它揭示了一件深刻的事：<strong>同样是 Claude，跑在 AWS Bedrock 上却需要另写一份协议</strong>——不是因为方言变了（它说的还是 Anthropic 那套块+签名），而是因为<strong>「网络传输」彻底变了</strong>：Bedrock 不用大家熟悉的 SSE，而用 AWS 自家的<strong>二进制事件流</strong>。这正好印证了第 31 课结尾那句话：「方言相同、网络不同，照样得另起一份协议。」</p>
<p>所以这一课其实在讲两件事。表面上，是认识 Gemini 和 Bedrock 两种新方言；骨子里，是借 Bedrock 这个绝佳样本，看清第 29 课那张表里 <span class="mono">stream</span> 之下还藏着一层——<strong>framing（分帧）</strong>。protocol 负责「帧→事件」，可帧本身怎么从字节流里切出来？SSE 那种「按空行切」太简单以至于你都没注意到它的存在；而 Bedrock 的二进制分帧，会把这层「字节→帧」的状态机<strong>结结实实地展示</strong>给你看。读完你会发现：原来流式解码是<strong>套娃</strong>的——字节→帧是一台状态机，帧→事件又是一台状态机。</p>

<div class="card analogy">
  <div class="tag">📡 生活类比</div>
  还是那队同声传译。<strong>Gemini</strong> 这位翻译，业务上和别人没本质不同，但他有个怪癖：所有术语都要用自家的叫法——别人说「助手」他偏说「模型方」，别人说「系统提示」他塞进一个叫 <span class="mono">systemInstruction</span> 的专属抽屉，连「这段是机器的思考」都要盖一个他独有的 <span class="mono">thoughtSignature</span> 戳。换汤不换药，但你不熟悉他的叫法就对不上账。<strong>Bedrock</strong> 这位则更微妙：他翻译的内容和 Anthropic 那位<strong>一模一样</strong>（因为背后是同一个 Claude），可他不通过「正常电话线」（SSE）传话，而是走一条<strong>军用加密专线</strong>（AWS 二进制事件流）——每句话都裹在固定格式的信封里：先 4 字节写「这封信多长」，再写信头长度、校验码、信头、正文、末尾再来个校验码。你得先有一台「拆信封机」把一封封信从连续的字节流里准确切出来、验好校验码，才能把里面的话交给翻译去理解。<strong>同一个翻译内容，因为传输专线不同，就得在最外层多配一台拆信封机。</strong>
</div>

<h2>Gemini：把每个字段都改了名的方言</h2>
<p>翻开 <span class="mono">gemini.ts</span>，扑面而来的是浓浓的 Google 风。它的请求体顶层叫 <span class="mono">contents</span>（不是 messages），每条是 <span class="mono">{role, parts}</span>，而 <span class="mono">role</span> 只有 <span class="mono">"user"</span> 和 <span class="mono">"model"</span> 两种——<strong>没有 "assistant"，Google 管助手叫「model」</strong>。系统提示又一次被拎到顶层，叫 <span class="mono">systemInstruction</span>（和 Anthropic 的 system、与 OpenAI 当普通消息，是三种摆法了）。内容不叫 content 而叫 <span class="mono">parts</span>，每个 part 可以是：</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">text</div><div class="c-txt">文本片段</div></div>
  <div class="cell"><div class="c-tag">functionCall</div><div class="c-txt">工具调用（camelCase！不是 tool_use 也不是 tool_calls）</div></div>
  <div class="cell"><div class="c-tag">functionResponse</div><div class="c-txt">工具结果回传</div></div>
  <div class="cell"><div class="c-tag">inline_data</div><div class="c-txt">内联图片等多模态数据</div></div>
  <div class="cell"><div class="c-tag">thought + thoughtSignature</div><div class="c-txt">标记为思考的 part，带「思考签名」</div></div>
</div>
<p>看到 <span class="mono">thoughtSignature</span> 了吗？这就是本课第一个「会心一笑」的点。回顾一下：让模型跨轮信任自己上一轮的推理，第 30 课 Anthropic 叫 <span class="mono">signature</span>，第 31 课 OpenAI Responses 叫 <span class="mono">encrypted_content</span>，到了 Gemini 这儿叫 <span class="mono">thoughtSignature</span>——<strong>同一个概念，三家三个名字</strong>。明明是一回事，偏偏没人愿意跟别人叫一样的名字。把它们并排一放，「协议即方言」这五个字就再不抽象了：</p>
<table class="t">
  <tr><th>供应商</th><th>「信任上轮推理」的字段名</th><th>风格</th></tr>
  <tr><td>Anthropic</td><td>signature</td><td>密码学签名验真</td></tr>
  <tr><td>OpenAI Responses</td><td>encrypted_content</td><td>加密密文托管</td></tr>
  <tr><td>Gemini</td><td>thoughtSignature</td><td>思考签名</td></tr>
</table>
<p>还有个有意思的差别：用量统计上，Gemini <strong>把思考 token 单列</strong>了——<span class="mono">usageMetadata</span> 里有 <span class="mono">thoughtsTokenCount</span> 字段，和 <span class="mono">candidatesTokenCount</span>（输出）、<span class="mono">promptTokenCount</span>（输入）并列。这跟第 30 课 Anthropic「把 thinking 算进 output、不单列」恰好相反。你看，连「思考 token 算不算单独一项」这种细节，三家都各有主张——而 opencode 的 <span class="mono">mapUsage</span> 们，就是把这些五花八门的口径，统统翻译成 core 认的那套规范 Usage。<strong>方言的差异有多碎，适配器吸收的功夫就有多细。</strong></p>
<p>Gemini 这一节看似只是「认认 Google 的命名」，但它有个更深的教益：<strong>方言的差异往往不在「能力」而在「叫法」</strong>。functionCall 和 tool_use、tool_calls 三个名字，指的是同一件事——「助手想调一个工具」；"model" 和 "assistant" 也是同一个角色。能力上三家几乎对等，可只要叫法不统一，core 就不可能直接对接任何一家——它要么被迫认全部三套叫法（耦合灾难），要么坚持只认自己那一套规范名、让适配器去翻译。opencode 选了后者。所以当你写 <span class="mono">gemini.ts</span> 的 <span class="mono">body.from</span> 时，本质上是在做一本「<strong>规范名 ↔ Google 名</strong>」的双语词典：core 的「assistant」翻成「model」，core 的「工具调用」翻成「functionCall」，core 的统一 system 翻进「systemInstruction」抽屉。这本词典越全，core 就越干净。</p>

<h2>Bedrock：同一个 Claude，却要另起一份协议</h2>
<p>现在来到本课的重头戏。AWS Bedrock 是个「模型批发商」——它转售包括 Claude 在内的多家模型，统一用自家的 <strong>Converse</strong> API。打开 <span class="mono">bedrock-converse.ts</span>，你会有种<strong>似曾相识</strong>的感觉：消息是 user/assistant 的块数组，块里有 <span class="mono">text</span> / <span class="mono">toolUse</span> / <span class="mono">toolResult</span> / <span class="mono">reasoningContent</span>（带 <span class="mono">signature</span>），system 是顶层块数组，还有熟悉的缓存读写计数……</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">text</div><div class="c-txt">文本块</div></div>
  <div class="cell"><div class="c-tag">toolUse</div><div class="c-txt">工具调用（带 toolUseId）</div></div>
  <div class="cell"><div class="c-tag">toolResult</div><div class="c-txt">工具结果（按 toolUseId 对应）</div></div>
  <div class="cell"><div class="c-tag">reasoningContent</div><div class="c-txt">推理内容，带 signature——和 Anthropic 同源！</div></div>
</div>
<p>为什么这么像 Anthropic？因为<strong>背后跑的就是 Claude</strong>，Bedrock 的 Converse 不过是给它套了层 AWS 的壳。连缓存逻辑都共享——还记得第 30 课说「4 个断点上限 + TTL 两档被抽到 <span class="mono">utils/cache.ts</span> 与 Bedrock 共享」吗？这里就是那个 Bedrock：<span class="mono">bedrock-converse.ts</span> 引入 <span class="mono">utils/bedrock-cache</span>，吃的正是同一套 4 断点规矩。<strong>方言几乎一样，那为什么不直接复用 Anthropic 协议、像 openai-compatible 那样 24 行了事？</strong>问题就出在「最外层那台拆信封机」上——传输方式根本不同。</p>
<div class="cols">
  <div class="col"><h4>Anthropic 官方</h4><p>方言：块 + signature。传输：<strong>SSE</strong>——一行行 UTF-8 文本，按空行分帧，人眼可读。framing 极简。</p></div>
  <div class="col"><h4>Bedrock 上的 Claude</h4><p>方言：几乎相同（块 + reasoningContent.signature）。传输：<strong>AWS 二进制事件流</strong>——固定格式的二进制帧 + CRC 校验。framing 复杂。</p></div>
</div>
<p>看清楚这张对照表的要害：<strong>左右两栏的「方言」几乎一模一样，差别全在「传输」那一行</strong>。如果协议里把「方言编解码」和「传输分帧」搅在一起，那 Bedrock 就只能把 Anthropic 的编解码逻辑<strong>整段抄一遍</strong>、再换掉传输——这正是第 28 课最忌讳的重复。而 opencode 因为早早把 framing 拆成了 Route 里的独立零件，Bedrock 才能「<strong>方言尽量复用、只换那台拆信封机</strong>」。一张对照表，把「为什么要把传输和编解码分开」讲得明明白白。</p>
<p>Anthropic 官方用 SSE（一行行文本、按空行分帧），而 Bedrock 用的是 <strong>AWS 二进制事件流协议</strong>：响应不是人类可读的文本，而是一连串<strong>固定格式的二进制帧</strong>。每一帧的结构是这样的：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">[4]</span><span class="t-txt">total length：整帧总长度</span></div>
  <div class="t-row"><span class="t-num">[4]</span><span class="t-txt">headers length：信头部分长度</span></div>
  <div class="t-row"><span class="t-num">[4]</span><span class="t-txt">prelude CRC：前导校验码</span></div>
  <div class="t-row"><span class="t-num">[…]</span><span class="t-txt">headers：含 :event-type（如 messageStart / contentBlockDelta）</span></div>
  <div class="t-row"><span class="t-num">[…]</span><span class="t-txt">payload：真正的 JSON 正文</span></div>
  <div class="t-row"><span class="t-num">[4]</span><span class="t-txt">message CRC：整帧校验码</span></div>
</div>
<p>这套 <span class="mono">[length][headers-length][prelude-crc][headers][payload][crc]</span> 的格式，正是 <span class="mono">bedrock-event-stream.ts</span> 这个 <strong>framing（分帧）</strong>层在处理的。它借 <span class="mono">@smithy/eventstream-codec</span> 校验帧结构和 CRC，再按 <span class="mono">:event-type</span> 头把 payload 重新包成带类型的 JSON，交给 protocol 的 stream 状态机去解。<strong>这就是为什么 Bedrock 要单独一份协议</strong>：方言（编解码）可以和 Anthropic 几乎雷同，但 framing（怎么从字节流里切出一帧）必须换成 AWS 这套——而 framing 正是第 31 课说的、Route 里与 protocol 正交的那个独立零件。Bedrock 把这个零件换掉，其余尽量复用，是「正交切分」威力的活教材。</p>

<h2>套娃的状态机：字节→帧→事件</h2>
<p>Bedrock 的 framing 层还藏着一个第 29 课的「老朋友」。从网络上下来的是<strong>连续的字节</strong>，一帧的边界不会乖乖落在网络分块的边界上——一个网络 chunk 里可能有半帧、也可能有三帧半。于是 framing 必须自己<strong>攒字节、找帧界</strong>，这又是一台状态机，只不过它处理的是<strong>更底层的字节</strong>：</p>
<div class="flow">
  <div class="f-node">网络 chunk<br><small>连续字节，帧界不对齐</small></div>
  <div class="f-arrow">appendChunk →</div>
  <div class="f-node">FrameBufferState<br><small>{buffer, offset} 攒着</small></div>
  <div class="f-arrow">consumeFrames →</div>
  <div class="f-node">完整帧们<br><small>够一帧就切一帧出来</small></div>
</div>
<p>它的状态是一个 <span class="mono">FrameBufferState{buffer, offset}</span>：<span class="mono">buffer</span> 攒着收到的字节，<span class="mono">offset</span> 是已读到的位置。每来一个网络 chunk，就 <span class="mono">appendChunk</span> 把它接到 buffer 尾上（顺手把 offset 之前已消费的前缀<strong>压缩</strong>丢掉，于是 buffer 不会随流无限膨胀——最多比「还活着的窗口」多出一个 chunk）；然后 <span class="mono">consumeFrames</span> 一帧一帧地切：只要剩余字节够拼出一整帧，就用<strong>零拷贝的 subarray</strong> 切出来、验 CRC、吐给上层。这台「字节→帧」的状态机，和第 29 课那台「帧→事件」的状态机，结构如出一辙——都是 <span class="mono">(状态, 新输入) → [新状态, 吐出的东西]</span>。<strong>流式解码原来是套娃的</strong>：framing 把字节攒成帧，protocol.stream 把帧攒成事件，两层各管一段、各是一台状态机，严丝合缝地叠在一起。第 29 课你以为只有一台状态机，到 Bedrock 这儿，你看见了它底下还垫着另一台。这种「同一个模式在不同抽象层反复出现」的现象，在好的代码库里很常见——一旦你认得了「攒输入、够了就吐、留住未尽的部分继续攒」这个骨架，无论它出现在字节层、帧层还是事件层，你都能<strong>一眼认出老朋友</strong>，不必从头理解。这就是吃透一个核心模式的复利：它会在你读代码的余生里，一次次替你省下理解成本。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <p>这一课用 Gemini 和 Bedrock 这两个样本，把第 29~31 课埋下的几条线索都收了个漂亮的口：</p>
  <ul>
    <li><strong>Gemini = 全面改名的方言</strong>：<span class="mono">contents</span>/<span class="mono">parts</span>、role 用 <span class="mono">"model"</span> 不用 "assistant"、systemInstruction 顶层、functionCall/Response 的 camelCase 风、思考 token 单列（thoughtsTokenCount）。</li>
    <li><strong>「信任上轮推理」三家三名</strong>：Anthropic <span class="mono">signature</span> / OpenAI <span class="mono">encrypted_content</span> / Gemini <span class="mono">thoughtSignature</span>——同物异名，「协议即方言」的最佳注脚。</li>
    <li><strong>Bedrock = 同方言、异传输</strong>：跑的是 Claude，方言（块+signature、共享 4 断点缓存）几乎等于 Anthropic，但传输是 AWS <strong>二进制事件流</strong>（<span class="mono">[length][headers-length][prelude-crc][headers][payload][crc]</span>），所以必须另起一份协议。印证第 31 课「方言同、网络异 → 另一份协议」。</li>
    <li><strong>套娃状态机</strong>：framing 层 <span class="mono">FrameBufferState{buffer,offset}</span> 把字节攒成帧（零拷贝 subarray + 压缩防膨胀），protocol.stream 再把帧攒成事件——两台 <span class="mono">(state,input)→[state,out]</span> 状态机叠在一起。</li>
  </ul>
  <p>至此你已集齐主流方言的全家福：Anthropic、OpenAI（Chat+Responses）、Gemini、Bedrock。它们千差万别，却都被钉进第 29 课那张统一的 <span class="mono">Protocol</span> 表里。下一课（L33）我们就正式拉开 <span class="mono">stream</span> 之下那层 <strong>framing 与 transport</strong>——Bedrock 已经让你尝了一口二进制分帧，下一课会把 HTTP（SSE）与 WebSocket 两种传输、以及分帧机制讲全。Bedrock 是从「协议」通往「传输」的天然桥梁。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p><span class="mono">appendChunk</span> 的「压缩」是个值得细品的小工程：</p>
  <pre class="code"><span class="cm">// 简化自 bedrock-event-stream.ts</span>
<span class="kw">const</span> <span class="fn">appendChunk</span> = (state, chunk) =&gt; {
  <span class="kw">const</span> remaining = state.buffer.length - state.offset  <span class="cm">// 还没读的部分</span>
  <span class="kw">const</span> next = <span class="kw">new</span> Uint8Array(remaining + chunk.length)
  next.set(state.buffer.subarray(state.offset), 0)  <span class="cm">// 丢掉已消费前缀</span>
  next.set(chunk, remaining)                          <span class="cm">// 接上新 chunk</span>
  <span class="kw">return</span> { buffer: next, offset: 0 }                  <span class="cm">// offset 归零</span>
}</pre>
  <p>妙在哪？如果天真地「只追加、不丢弃」，那么一个跑了几分钟、传了几兆字节的长流，buffer 会<strong>无限膨胀</strong>到把整个响应都堆在内存里。这里每次 append 都<strong>顺手把 offset 之前已经读完、再不会用到的字节扔掉</strong>，只保留「还没拼成完整帧的活跃窗口」+ 刚到的这个 chunk。源码注释一语道破：这把 buffer 的增长<strong>限制在「最多比活跃窗口多一个网络 chunk」</strong>，无论流多长。读取用 <span class="mono">subarray</span> 是零拷贝（只是开个视图、不复制字节），只在 append 时分配一次新数组——<strong>该省的拷贝省掉、该有的内存上界守住</strong>。处理无界流时，这种「有界内存」的自觉，是把玩具代码和生产代码区分开的关键细节。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>Gemini</strong>（<span class="mono">gemini.ts</span>）是全面改名的方言：顶层 <span class="mono">contents</span>、每条 <span class="mono">{role, parts}</span>、role 是 <span class="mono">"user"/"model"</span>（无 assistant）、system 进 <span class="mono">systemInstruction</span> 顶层、工具用 camelCase 的 <span class="mono">functionCall</span>/<span class="mono">functionResponse</span>、思考 token 单列（<span class="mono">thoughtsTokenCount</span>）。</li>
    <li><strong>「信任上轮推理」三家三名</strong>：Anthropic <span class="mono">signature</span>、OpenAI Responses <span class="mono">encrypted_content</span>、Gemini <span class="mono">thoughtSignature</span>——同一概念三种叫法，「协议即方言」的最直观例证。</li>
    <li><strong>Bedrock</strong>（<span class="mono">bedrock-converse.ts</span>）转售 Claude，用 AWS Converse API；方言几乎等同 Anthropic（块 + <span class="mono">reasoningContent.signature</span>、共享 <span class="mono">utils/cache</span> 的 4 断点缓存），但<strong>传输用 AWS 二进制事件流</strong>，故必须另起一份协议。</li>
    <li><strong>二进制帧结构</strong>：<span class="mono">[length:4][headers-length:4][prelude-crc:4][headers][payload][crc:4]</span>，由 <span class="mono">bedrock-event-stream.ts</span>（framing 层）借 <span class="mono">@smithy/eventstream-codec</span> 校验 CRC、按 <span class="mono">:event-type</span> 头重组 JSON。framing 是 Route 里与 protocol 正交的独立零件。</li>
    <li><strong>套娃状态机</strong>：framing 用 <span class="mono">FrameBufferState{buffer,offset}</span> 把字节攒成帧（零拷贝 <span class="mono">subarray</span>、append 时压缩丢弃已消费前缀以保证有界内存），protocol.stream 再把帧攒成事件——两层都是 <span class="mono">(state,input)→[state,out]</span>。这是通往第 33 课传输层的天然桥梁。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Lessons 30 and 31 looked at Anthropic's and OpenAI's "filled-in forms." This lesson covers two more vendors at once—Gemini and Bedrock—each bringing a new dimension of insight. <strong>Gemini</strong> is another variation on the "dialect" theme: it renames nearly every field (Google's camelCase style), and gives "reasoning signature" a <strong>third name</strong>—so now three big vendors, three names; you'll smile knowingly when you see this "same thing, different names" table. But <strong>Bedrock</strong> is this lesson's real star, revealing something profound: <strong>the same Claude, run on AWS Bedrock, needs a separately written protocol</strong>—not because the dialect changed (it still speaks Anthropic's blocks+signature), but because the <strong>"network transport" changed entirely</strong>: Bedrock doesn't use the familiar SSE but AWS's own <strong>binary event stream</strong>. This exactly confirms lesson 31's closing line: "same dialect, different network—still needs another protocol."</p>
<p>So this lesson really covers two things. On the surface, getting to know Gemini's and Bedrock's two new dialects; underneath, using Bedrock as a perfect sample to see that beneath lesson 29's form's <span class="mono">stream</span> hides yet another layer—<strong>framing</strong>. protocol owns "frame→event," but how is a frame itself cut from the byte stream? SSE's "split on blank line" is so simple you didn't even notice its existence; but Bedrock's binary framing <strong>solidly displays</strong> this "byte→frame" state machine for you. After reading you'll find: streaming decode is a <strong>nesting doll</strong>—byte→frame is one state machine, frame→event is another.</p>

<div class="card analogy">
  <div class="tag">📡 Analogy</div>
  Same interpreter relay. <strong>Gemini</strong>, this interpreter, is essentially no different in business, but has a quirk: every term must use his own naming—others say "assistant," he insists on "model side"; others say "system prompt," he stuffs it into a dedicated drawer called <span class="mono">systemInstruction</span>; even "this segment is the machine thinking" must get his unique <span class="mono">thoughtSignature</span> stamp. Same wine, different bottle, but if you don't know his naming you can't reconcile the books. <strong>Bedrock</strong> is subtler: the content he translates is <strong>identical</strong> to Anthropic's (because the same Claude is behind it), yet he doesn't relay over the "normal phone line" (SSE) but a <strong>military encrypted dedicated line</strong> (AWS binary event stream)—each sentence wrapped in a fixed-format envelope: first 4 bytes write "how long this letter is," then header length, checksum, headers, payload, and another checksum at the end. You first need a "letter-opening machine" to accurately cut letter after letter from the continuous byte stream and verify checksums, before handing the words inside to the interpreter. <strong>The same translation content, because the transport line differs, requires one extra letter-opening machine on the outermost layer.</strong>
</div>

<h2>Gemini: a dialect that renamed every field</h2>
<p>Open <span class="mono">gemini.ts</span> and you're hit by strong Google flavor. Its request body's top level is called <span class="mono">contents</span> (not messages), each entry is <span class="mono">{role, parts}</span>, and <span class="mono">role</span> is only <span class="mono">"user"</span> or <span class="mono">"model"</span>—<strong>no "assistant," Google calls the assistant "model."</strong> The system prompt is again hoisted to the top level, called <span class="mono">systemInstruction</span> (Anthropic's system, OpenAI's ordinary message, and now this make three placements). Content isn't content but <span class="mono">parts</span>, each part can be:</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">text</div><div class="c-txt">text fragment</div></div>
  <div class="cell"><div class="c-tag">functionCall</div><div class="c-txt">tool call (camelCase! not tool_use, not tool_calls)</div></div>
  <div class="cell"><div class="c-tag">functionResponse</div><div class="c-txt">tool result returned</div></div>
  <div class="cell"><div class="c-tag">inline_data</div><div class="c-txt">inline image and other multimodal data</div></div>
  <div class="cell"><div class="c-tag">thought + thoughtSignature</div><div class="c-txt">a part marked as thought, with a "thought signature"</div></div>
</div>
<p>See <span class="mono">thoughtSignature</span>? This is the lesson's first "knowing smile." Recall: to let the model trust its own prior reasoning across turns, lesson 30's Anthropic calls it <span class="mono">signature</span>, lesson 31's OpenAI Responses calls it <span class="mono">encrypted_content</span>, and here in Gemini it's <span class="mono">thoughtSignature</span>—<strong>the same concept, three vendors, three names</strong>. Lay them side by side and the five words "protocol = dialect" stop being abstract:</p>
<table class="t">
  <tr><th>Vendor</th><th>Field for "trust prior reasoning"</th><th>Style</th></tr>
  <tr><td>Anthropic</td><td>signature</td><td>cryptographic signature verification</td></tr>
  <tr><td>OpenAI Responses</td><td>encrypted_content</td><td>encrypted ciphertext custody</td></tr>
  <tr><td>Gemini</td><td>thoughtSignature</td><td>thought signature</td></tr>
</table>
<p>Another interesting difference: on usage stats, Gemini <strong>breaks out thinking tokens</strong>—<span class="mono">usageMetadata</span> has a <span class="mono">thoughtsTokenCount</span> field, alongside <span class="mono">candidatesTokenCount</span> (output) and <span class="mono">promptTokenCount</span> (input). This is exactly the opposite of lesson 30's Anthropic "counts thinking into output, not broken out." See, even a detail like "is the thinking token a separate item" has each of the three with its own stance—and opencode's <span class="mono">mapUsage</span>s translate all these varied conventions into core's one canonical Usage. <strong>However granular the dialect's differences, that's how fine the adapter's absorption work must be.</strong></p>
<p>This Gemini section may look like just "learning Google's naming," but it has a deeper lesson: <strong>dialect differences are often not in "capability" but in "naming."</strong> functionCall, tool_use, tool_calls—three names refer to the same thing: "the assistant wants to call a tool"; "model" and "assistant" are the same role too. Capability-wise the three are nearly equal, yet as long as naming isn't unified, core can't directly interface with any one of them—it must either be forced to know all three sets of names (a coupling disaster), or insist on knowing only its own canonical names and let adapters translate. opencode chose the latter. So when you write <span class="mono">gemini.ts</span>'s <span class="mono">body.from</span>, you're essentially building a "<strong>canonical name ↔ Google name</strong>" bilingual dictionary: core's "assistant" translates to "model," core's "tool call" to "functionCall," core's unified system into the "systemInstruction" drawer. The fuller this dictionary, the cleaner core stays.</p>

<h2>Bedrock: the same Claude, yet needs a separate protocol</h2>
<p>Now the lesson's centerpiece. AWS Bedrock is a "model wholesaler"—it resells multiple models including Claude, uniformly via its own <strong>Converse</strong> API. Open <span class="mono">bedrock-converse.ts</span> and you'll feel a <strong>déjà vu</strong>: messages are user/assistant block arrays, blocks have <span class="mono">text</span> / <span class="mono">toolUse</span> / <span class="mono">toolResult</span> / <span class="mono">reasoningContent</span> (with <span class="mono">signature</span>), system is a top-level block array, plus familiar cache read/write counters…</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">text</div><div class="c-txt">text block</div></div>
  <div class="cell"><div class="c-tag">toolUse</div><div class="c-txt">tool call (with toolUseId)</div></div>
  <div class="cell"><div class="c-tag">toolResult</div><div class="c-txt">tool result (matched by toolUseId)</div></div>
  <div class="cell"><div class="c-tag">reasoningContent</div><div class="c-txt">reasoning content, with signature—same lineage as Anthropic!</div></div>
</div>
<p>Why so like Anthropic? Because <strong>Claude is what runs behind it</strong>; Bedrock's Converse merely wraps it in an AWS shell. Even the cache logic is shared—remember lesson 30 saying "the 4-breakpoint cap + two TTL buckets is hoisted into <span class="mono">utils/cache.ts</span> shared with Bedrock"? This is that Bedrock: <span class="mono">bedrock-converse.ts</span> imports <span class="mono">utils/bedrock-cache</span>, eating the same 4-breakpoint rules. <strong>The dialect is nearly identical, so why not just reuse the Anthropic protocol, 24-lines like openai-compatible?</strong> The problem is at "the outermost letter-opening machine"—the transport differs fundamentally.</p>
<div class="cols">
  <div class="col"><h4>Anthropic official</h4><p>Dialect: blocks + signature. Transport: <strong>SSE</strong>—line-by-line UTF-8 text, framed on blank lines, human-readable. Framing is trivial.</p></div>
  <div class="col"><h4>Claude on Bedrock</h4><p>Dialect: nearly the same (blocks + reasoningContent.signature). Transport: <strong>AWS binary event stream</strong>—fixed-format binary frames + CRC checks. Framing is complex.</p></div>
</div>
<p>See clearly this table's crux: <strong>the left and right "dialects" are nearly identical, the difference all in the "transport" row</strong>. If a protocol mixed "dialect codec" with "transport framing," then Bedrock could only <strong>copy Anthropic's codec logic wholesale</strong> then swap the transport—exactly the duplication lesson 28 most abhors. But because opencode early on split framing into an independent part of Route, Bedrock can "<strong>reuse the dialect as much as possible, swap only that letter-opening machine</strong>." One table makes "why separate transport from codec" crystal clear.</p>
<p>Anthropic official uses SSE (line-by-line text, framed on blank lines), while Bedrock uses the <strong>AWS binary event stream protocol</strong>: the response isn't human-readable text but a run of <strong>fixed-format binary frames</strong>. Each frame's structure is:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">[4]</span><span class="t-txt">total length: the whole frame's length</span></div>
  <div class="t-row"><span class="t-num">[4]</span><span class="t-txt">headers length: the header section's length</span></div>
  <div class="t-row"><span class="t-num">[4]</span><span class="t-txt">prelude CRC: the prelude checksum</span></div>
  <div class="t-row"><span class="t-num">[…]</span><span class="t-txt">headers: includes :event-type (e.g. messageStart / contentBlockDelta)</span></div>
  <div class="t-row"><span class="t-num">[…]</span><span class="t-txt">payload: the actual JSON body</span></div>
  <div class="t-row"><span class="t-num">[4]</span><span class="t-txt">message CRC: the whole frame's checksum</span></div>
</div>
<p>This <span class="mono">[length][headers-length][prelude-crc][headers][payload][crc]</span> format is exactly what <span class="mono">bedrock-event-stream.ts</span>, the <strong>framing</strong> layer, handles. It uses <span class="mono">@smithy/eventstream-codec</span> to validate frame structure and CRCs, then re-wraps the payload into typed JSON by the <span class="mono">:event-type</span> header, handing it to the protocol's stream state machine to decode. <strong>This is why Bedrock needs a separate protocol</strong>: the dialect (codec) can be nearly identical to Anthropic, but the framing (how to cut a frame from the byte stream) must switch to AWS's—and framing is exactly lesson 31's mentioned independent part of Route, orthogonal to protocol. Bedrock swaps this part out, reuses the rest as much as possible—a living textbook of "orthogonal split"'s power.</p>

<h2>Nesting-doll state machines: byte→frame→event</h2>
<p>Bedrock's framing layer also hides an "old friend" from lesson 29. What comes off the network is <strong>continuous bytes</strong>, and a frame's boundary won't obligingly land on a network chunk's boundary—one network chunk may hold half a frame, or three and a half. So framing must itself <strong>accumulate bytes, find frame boundaries</strong>—another state machine, only it handles <strong>lower-level bytes</strong>:</p>
<div class="flow">
  <div class="f-node">network chunk<br><small>continuous bytes, frame bounds unaligned</small></div>
  <div class="f-arrow">appendChunk →</div>
  <div class="f-node">FrameBufferState<br><small>{buffer, offset} accumulating</small></div>
  <div class="f-arrow">consumeFrames →</div>
  <div class="f-node">complete frames<br><small>cut one out once enough for a frame</small></div>
</div>
<p>Its state is a <span class="mono">FrameBufferState{buffer, offset}</span>: <span class="mono">buffer</span> accumulates received bytes, <span class="mono">offset</span> is the read position. Each network chunk arriving, <span class="mono">appendChunk</span> joins it to the buffer's tail (incidentally <strong>compacting away</strong> the already-consumed prefix before offset, so the buffer doesn't grow unboundedly with the stream—at most one chunk past the "live window"); then <span class="mono">consumeFrames</span> cuts frame by frame: as long as remaining bytes suffice for a whole frame, cut it out with <strong>zero-copy subarray</strong>, verify CRC, emit upward. This "byte→frame" state machine and lesson 29's "frame→event" state machine are structurally identical—both <span class="mono">(state, new input) → [new state, things emitted]</span>. <strong>Streaming decode is a nesting doll after all</strong>: framing accumulates bytes into frames, protocol.stream accumulates frames into events, two layers each owning a stretch, each a state machine, stacked seamlessly. Lesson 29 you thought there was only one state machine; here at Bedrock, you see another cushioning it underneath. This "same pattern recurring at different abstraction layers" is common in good codebases—once you recognize the skeleton of "accumulate input, emit when enough, keep the unfinished part accumulating," wherever it appears—byte layer, frame layer, or event layer—you'll <strong>spot the old friend at a glance</strong>, no need to understand from scratch. That's the compound interest of mastering one core pattern: it saves you comprehension cost, again and again, for the rest of your reading life.</p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>This lesson uses the two samples Gemini and Bedrock to tie off, beautifully, several threads laid down in lessons 29–31:</p>
  <ul>
    <li><strong>Gemini = a fully-renamed dialect</strong>: <span class="mono">contents</span>/<span class="mono">parts</span>, role uses <span class="mono">"model"</span> not "assistant", systemInstruction top-level, functionCall/Response camelCase style, thinking tokens broken out (thoughtsTokenCount).</li>
    <li><strong>"Trust prior reasoning," three vendors three names</strong>: Anthropic <span class="mono">signature</span> / OpenAI <span class="mono">encrypted_content</span> / Gemini <span class="mono">thoughtSignature</span>—same thing, different names, the best footnote to "protocol = dialect."</li>
    <li><strong>Bedrock = same dialect, different transport</strong>: runs Claude, dialect (blocks+signature, shared 4-breakpoint cache) nearly equals Anthropic, but transport is AWS <strong>binary event stream</strong> (<span class="mono">[length][headers-length][prelude-crc][headers][payload][crc]</span>), so it must have a separate protocol. Confirms lesson 31's "same dialect, different network → another protocol."</li>
    <li><strong>Nesting-doll state machines</strong>: the framing layer's <span class="mono">FrameBufferState{buffer,offset}</span> accumulates bytes into frames (zero-copy subarray + compaction against bloat), protocol.stream then accumulates frames into events—two <span class="mono">(state,input)→[state,out]</span> state machines stacked.</li>
  </ul>
  <p>Now you've collected the full family of mainstream dialects: Anthropic, OpenAI (Chat+Responses), Gemini, Bedrock. Wildly different, yet all nailed into lesson 29's one unified <span class="mono">Protocol</span> form. Next lesson (L33) we formally pull open the <strong>framing and transport</strong> layer beneath <span class="mono">stream</span>—Bedrock has let you taste binary framing; next lesson rounds out both HTTP (SSE) and WebSocket transports plus the framing mechanism. Bedrock is the natural bridge from "protocol" to "transport."</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p><span class="mono">appendChunk</span>'s "compaction" is a small piece of engineering worth savoring:</p>
  <pre class="code"><span class="cm">// simplified from bedrock-event-stream.ts</span>
<span class="kw">const</span> <span class="fn">appendChunk</span> = (state, chunk) =&gt; {
  <span class="kw">const</span> remaining = state.buffer.length - state.offset  <span class="cm">// the not-yet-read part</span>
  <span class="kw">const</span> next = <span class="kw">new</span> Uint8Array(remaining + chunk.length)
  next.set(state.buffer.subarray(state.offset), 0)  <span class="cm">// drop consumed prefix</span>
  next.set(chunk, remaining)                          <span class="cm">// append new chunk</span>
  <span class="kw">return</span> { buffer: next, offset: 0 }                  <span class="cm">// offset back to zero</span>
}</pre>
  <p>What's clever? If you naively "only append, never drop," then a long stream running for minutes, transmitting megabytes, would <strong>grow the buffer unboundedly</strong> until the whole response piles up in memory. Here each append <strong>incidentally discards the bytes before offset that are already read and will never be used again</strong>, keeping only "the active window not yet assembled into a complete frame" + the just-arrived chunk. The source comment nails it: this bounds buffer growth to "<strong>at most one network chunk past the active window</strong>," however long the stream. Reads use <span class="mono">subarray</span> which is zero-copy (just open a view, don't copy bytes), allocating a new array only on append—<strong>save the copies you should, hold the memory bound you must</strong>. When handling unbounded streams, this awareness of "bounded memory" is the key detail separating toy code from production code.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>Gemini</strong> (<span class="mono">gemini.ts</span>) is a fully-renamed dialect: top-level <span class="mono">contents</span>, each entry <span class="mono">{role, parts}</span>, role is <span class="mono">"user"/"model"</span> (no assistant), system goes into top-level <span class="mono">systemInstruction</span>, tools use camelCase <span class="mono">functionCall</span>/<span class="mono">functionResponse</span>, thinking tokens broken out (<span class="mono">thoughtsTokenCount</span>).</li>
    <li><strong>"Trust prior reasoning," three vendors three names</strong>: Anthropic <span class="mono">signature</span>, OpenAI Responses <span class="mono">encrypted_content</span>, Gemini <span class="mono">thoughtSignature</span>—one concept, three names, the most vivid evidence of "protocol = dialect."</li>
    <li><strong>Bedrock</strong> (<span class="mono">bedrock-converse.ts</span>) resells Claude via AWS Converse API; the dialect nearly equals Anthropic (blocks + <span class="mono">reasoningContent.signature</span>, shares <span class="mono">utils/cache</span>'s 4-breakpoint cache), but the <strong>transport uses AWS binary event stream</strong>, so it must have a separate protocol.</li>
    <li><strong>Binary frame structure</strong>: <span class="mono">[length:4][headers-length:4][prelude-crc:4][headers][payload][crc:4]</span>, handled by <span class="mono">bedrock-event-stream.ts</span> (framing layer) using <span class="mono">@smithy/eventstream-codec</span> to verify CRCs and reassemble JSON by the <span class="mono">:event-type</span> header. framing is an independent part of Route, orthogonal to protocol.</li>
    <li><strong>Nesting-doll state machines</strong>: framing uses <span class="mono">FrameBufferState{buffer,offset}</span> to accumulate bytes into frames (zero-copy <span class="mono">subarray</span>, compacting away consumed prefix on append for bounded memory), protocol.stream then accumulates frames into events—both <span class="mono">(state,input)→[state,out]</span>. The bridge to lesson 33's transport layer.</li>
  </ul>
</div>
""",
}
LESSON_33 = {
    "zh": r"""
<p class="lead">第 29~32 课，我们把六种协议的「方言」摸了个遍。但你有没有注意到一件事：<strong>协议从头到尾，没碰过一次网络</strong>。它只管「把请求编码成什么样、把响应解码成什么」——纯粹是<strong>语言层面</strong>的活儿。可话总得真的发出去、字节总得真的收回来吧？这一课的主角，就是协议脚下那条<strong>真正搬运字节的传送带</strong>：传输（transport）、分帧（framing）、端点（endpoint）、认证（auth）。它们和协议一起，被 <span class="mono">Route</span> 拼成一条完整的流水线。读完这一课，第 29 课那张「两栏表」会第一次<strong>接上电、转起来</strong>——你会看见一个请求从规范对象出发，经过编码、寻址、签名、上线、分帧、解码，最终变回一串规范事件的<strong>全程</strong>。</p>
<p>更重要的是，这一课会揭示 opencode 这套设计的<strong>最终形态</strong>：一个 <span class="mono">Route</span> 不是铁板一块，而是<strong>六个正交旋钮</strong>拼出来的——协议、端点、认证、传输、分帧，外加一个 id。每个旋钮都能独立替换。正因如此，第 31 课的「OpenAI 兼容只改端点」、第 32 课的「Bedrock 只换分帧」，才都能用「<strong>只拧一个旋钮、其余照旧</strong>」这么轻巧的方式实现。这一课，就是把这六个旋钮一字排开，让你看清这套<strong>积木式</strong>架构的全貌。</p>

<div class="card analogy">
  <div class="tag">🚚 生活类比</div>
  还是那位翻译（协议）。他只会一件事：<strong>把话翻好</strong>。可一封信要真的送到对方手里，光会翻译远远不够，还得配齐一整套<strong>物流班子</strong>：<strong>地址（endpoint）</strong>——送到哪个门牌；<strong>证件（auth）</strong>——门口保安要查的通行证；<strong>运输方式（transport）</strong>——是叫一趟「货车往返」（HTTP：去一趟、送货、拉回回执就结束），还是接一条「常开的热线电话」（WebSocket：线一直连着，随时能你一句我一句）；<strong>拆信封的规矩（framing）</strong>——回执是「一行行印在纸上、空行分段」（SSE），还是「裹在固定格式的密封袋里、带封条校验」（二进制）。同一位翻译，配上不同的地址、证件、运输、拆封规矩，就能服务千差万别的承包商。<strong>翻译只负责语言，把信真正送达的，是这套可自由组合的物流班子。</strong>
</div>

<h2>一条完整的流水线：请求是怎么跑完全程的</h2>
<p>先把第 29~32 课的所有拼图拼起来，看一个请求的<strong>全生命周期</strong>。当上层（还记得第 17 课的 <span class="mono">llm.stream(request)</span> 吗？）发起一次流式请求，<span class="mono">Route</span> 的 <span class="mono">stream</span> 方法会驱动这样一条传送带：</p>
<div class="trace">
  <div class="t-row"><span class="t-num">①编码</span><span class="t-txt">protocol.body.from(request)：规范请求 → 这家的请求体</span></div>
  <div class="t-row"><span class="t-num">②寻址</span><span class="t-txt">endpoint：拼出该打哪个 URL</span></div>
  <div class="t-row"><span class="t-num">③签名</span><span class="t-txt">auth：加上 API key / AWS 签名等通行证</span></div>
  <div class="t-row"><span class="t-num">④上线</span><span class="t-txt">transport（HTTP/WS）：把请求发出去，拿回一个字节流</span></div>
  <div class="t-row"><span class="t-num">⑤分帧</span><span class="t-txt">framing：把连续字节切成一帧一帧（SSE/二进制）</span></div>
  <div class="t-row"><span class="t-num">⑥解码</span><span class="t-txt">protocol.stream：帧 → 规范 LLMEvent（第 29 课那台状态机）</span></div>
</div>
<p>看清楚这条带子的<strong>分工</strong>：①和⑥是<strong>协议</strong>的活（语言层，L29~32 讲透了）；②③④⑤是<strong>传输基础设施</strong>的活（网络层，这一课的主题）。两段之间的接口干净利落：协议<strong>吐出/吃进的都是「请求体」和「帧」这种抽象物</strong>，完全不关心字节是怎么飞过网络的；而传输基础设施<strong>只搬运字节、只切帧</strong>，完全不关心帧里装的是 Anthropic 的块还是 Gemini 的 parts。这种「各扫门前雪」正是整个设计能<strong>积木化</strong>的根本：每一段只认自己上下游的那个抽象接口，于是每一段都能被单独替换。</p>
<div class="layers">
  <div class="layer"><div class="l-name">语言层 · protocol</div><div class="l-desc">①body.from 编码 + ⑥stream 解码；只认「请求体」和「帧」，不碰网络</div></div>
  <div class="layer"><div class="l-name">网络层 · 传输基础设施</div><div class="l-desc">②endpoint 寻址 + ③auth 签名 + ④transport 上线 + ⑤framing 切帧；只搬字节，不认方言</div></div>
</div>
<p>这张分层图值得盯住看一会儿：两层之间那条横线，就是整个 LLM 包的<strong>命脉接缝</strong>。线之上，是「人类语言/模型语言」的世界，讲的是块、parts、tool_calls 这些<strong>语义</strong>；线之下，是「字节/网络」的世界，讲的是 POST、CRC、UTF-8 这些<strong>机械</strong>。一个请求穿过这条线两次：下行时从语义被压成字节（①→④），上行时从字节被还原成语义（⑤→⑥）。把这条线画清楚，你就明白为什么换供应商常常「只动一层、不动另一层」——因为两层本就是<strong>沿着这条接缝被切开的</strong>。</p>

<h2>两种传输：货车往返 vs 常开热线</h2>
<p>第④步「上线」，opencode 备了两种 transport，对应两种截然不同的「上网姿势」：</p>
<div class="cols">
  <div class="col"><h4>HTTP（货车往返）</h4><p>经典的请求/响应：POST 一个请求体出去，把响应体当作<strong>一个字节流</strong>拉回来，本轮就结束。简单、universal，<strong>绝大多数供应商都走这条</strong>。一来一回，干净利落。</p></div>
  <div class="col"><h4>WebSocket（常开热线）</h4><p>一条<strong>持久的双向连接</strong>：连上后，可以不断 <span class="mono">sendText</span> 发消息、从 <span class="mono">messages</span> 流里收消息。适合低延迟、实时、需要双向互动的场景。</p></div>
</div>
<p>谁会用 WebSocket？翻遍 <span class="mono">protocols/</span>，你会发现<strong>唯一同时支持两种传输的，是 OpenAI Responses</strong>——它既给了 <span class="mono">httpTransport</span>，也给了 <span class="mono">webSocketTransport</span>。这正好接上第 31 课埋的伏笔：Responses 的请求体被设计成「HTTP 和 WebSocket 共享同一套形状」，HTTP 版多个 <span class="mono">stream:true</span>、WebSocket 版多个 <span class="mono">type:"response.create"</span>。同一份协议编解码，<strong>底下换一种传输照样能用</strong>——这又是「协议与传输正交」的活证据：Responses 的方言只写一遍，HTTP 和 WebSocket 两条腿都能走。其余各家（Anthropic、Gemini、OpenAI Chat、Bedrock）目前都只走 HTTP，但「想加 WebSocket 只需配一个 transport 旋钮、不动协议」这件事，本身就是这套架构留好的余地。</p>
<p>为什么 HTTP 几乎一统天下、WebSocket 只是个别选项？因为对「发一个请求、流式收一段回复」这件事，HTTP 的「货车往返」已经够用且最省心：一次 POST、一个响应体流、结束，无状态、无需维护长连接、被所有网络设施友好对待。WebSocket 的「常开热线」更强，但也更重——要管理连接的建立、保活、断线重连，代价不小。它真正的价值在<strong>双向、实时、低延迟</strong>的场景：比如你想在模型生成途中插话、或要求毫秒级的来回。OpenAI Responses 之所以两种都备，正是因为它面向那些<strong>需要实时互动</strong>的高级用法。换句话说，opencode 没有「为了时髦而上 WebSocket」，而是<strong>哪种传输划算就用哪种</strong>，并把选择权做成一个可随时拨动的旋钮——这本身就是工程上的清醒。</p>

<h2>framing：传输与协议之间的那道缝</h2>
<p>第⑤步「分帧」值得单独说，因为它是<strong>整套设计里最精妙的一道接缝</strong>。<span class="mono">framing.ts</span> 的注释把它定义得很美：「<strong>Framing 是传输与协议之间、字节流形状的那道缝</strong>」。它的接口简单到只有一个函数：<span class="mono">frame: (字节流) =&gt; 帧流</span>。</p>
<div class="flow">
  <div class="f-node">字节流<br><small>transport 拉回来的原始 bytes</small></div>
  <div class="f-arrow">framing.frame →</div>
  <div class="f-node">SSE：按 data: 切<br>二进制：按长度+CRC 切</div>
  <div class="f-arrow">→</div>
  <div class="f-node">帧流<br><small>交给 protocol.stream 解码</small></div>
</div>
<p>opencode 内置两种 framing。<strong>SSE</strong>（<span class="mono">Framing.sse</span>）：把字节按 UTF-8 解码，跑一遍 SSE 通道解码器，丢掉空行和 <span class="mono">[DONE]</span> 这种保活信号，每一帧就是一个事件的 <span class="mono">data:</span> JSON 负载——<strong>几乎所有 JSON 流式 HTTP 供应商都用它</strong>。<strong>AWS 二进制事件流</strong>：就是第 32 课你已经见过的那套带长度前缀和 CRC 校验的二进制帧。关键在注释最后一句：「<strong>帧的类型对这一层是不透明的</strong>」——framing 只负责「把字节切成一份一份」，至于每一份里装的是什么，它<strong>一概不管</strong>，那是协议 <span class="mono">stream.event</span> 解码该操心的事。正因为 framing 对「帧里是什么」保持无知，它才能<strong>被任意协议复用</strong>：SSE 这一种分帧方式，同时服务着 Anthropic、Gemini、OpenAI 三套完全不同的方言。一道划得恰到好处的缝，换来了上下两层各自的自由。反过来想，假如当初没有 framing 这道缝，而是让每个协议自己从字节流里抠帧，那么「按 data: 空行切」这段逻辑就得在 Anthropic、Gemini、OpenAI 里<strong>各抄一遍</strong>——又是第 28 课最忌讳的重复。framing 把「字节→帧」这件三家共通的脏活<strong>提取成一个独立、可复用的零件</strong>，正是「找出共性、抽到一处」这条贯穿全书的智慧，在传输层的又一次现身。</p>

<h2>六个正交旋钮：积木式的 Route</h2>
<p>把这一课和前几课合起来，opencode LLM 层的<strong>最终形态</strong>就清晰了：一个 <span class="mono">Route</span> 由<strong>六个可独立替换的旋钮</strong>拼成。</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">id</div><div class="c-txt">路由标识，用于诊断与解析</div></div>
  <div class="cell"><div class="c-tag">protocol</div><div class="c-txt">方言编解码（body.from + stream.step）</div></div>
  <div class="cell"><div class="c-tag">endpoint</div><div class="c-txt">打哪个 URL</div></div>
  <div class="cell"><div class="c-tag">auth</div><div class="c-txt">怎么签名/认证</div></div>
  <div class="cell"><div class="c-tag">transport</div><div class="c-txt">HTTP 还是 WebSocket</div></div>
  <div class="cell"><div class="c-tag">framing</div><div class="c-txt">SSE 还是二进制分帧</div></div>
</div>
<p>把各家供应商按这几个旋钮的取值排开，你会立刻看懂前几课那些「轻巧复用」到底是怎么回事：</p>
<table class="t">
  <tr><th>供应商</th><th>protocol</th><th>transport</th><th>framing</th></tr>
  <tr><td>Anthropic</td><td>anthropic-messages</td><td>HTTP</td><td>SSE</td></tr>
  <tr><td>Gemini</td><td>gemini</td><td>HTTP</td><td>SSE</td></tr>
  <tr><td>OpenAI Chat</td><td>openai-chat</td><td>HTTP</td><td>SSE</td></tr>
  <tr><td>OpenAI 兼容</td><td>openai-chat（复用！）</td><td>HTTP</td><td>SSE</td></tr>
  <tr><td>OpenAI Responses</td><td>openai-responses</td><td>HTTP 或 WS</td><td>SSE</td></tr>
  <tr><td>Bedrock</td><td>bedrock-converse</td><td>HTTP</td><td>二进制事件流</td></tr>
</table>
<p>这张表把前几课的「魔法」全祛魅了：「OpenAI 兼容」只是把 protocol 旋钮拨到 <span class="mono">openai-chat</span>、改个 endpoint（第 31 课的 24 行）；「Bedrock」只是把 framing 旋钮从 SSE 拨到二进制、其余尽量沿用 Anthropic 那套（第 32 课）；「Responses 上 WebSocket」只是把 transport 旋钮从 HTTP 拨到 WS。<strong>每一个看似聪明的复用，本质都是「只拧一两个旋钮、其余照旧」</strong>。这就是正交分解的复利：六个旋钮各管一维，组合空间却覆盖了所有现实供应商，而新增一家的成本，往往只是<strong>给六个旋钮挑一组合适的取值</strong>。</p>

<div class="card macro">
  <div class="tag">🗺️ 宏观图景</div>
  <p>这一课把 M6 的拼图收成了完整的一幅：</p>
  <ul>
    <li><strong>协议不碰网络</strong>：protocol 只管语言层（body.from 编码 / stream 解码），传输基础设施（endpoint/auth/transport/framing）才真正搬运字节。两段以「请求体」和「帧」为抽象接口干净对接。</li>
    <li><strong>完整流水线</strong>：①body.from 编码 → ②endpoint 寻址 → ③auth 签名 → ④transport 上线取字节流 → ⑤framing 切帧 → ⑥protocol.stream 解码成 LLMEvent。第 29 课的表至此「通上电」。</li>
    <li><strong>两种传输</strong>：HTTP（请求/响应，绝大多数走这条）vs WebSocket（持久双向，唯 OpenAI Responses 两者皆支持，印证第 31 课共享请求体形状）。</li>
    <li><strong>framing 是字节流形状的缝</strong>：<span class="mono">(字节流)=&gt;(帧流)</span>，SSE / 二进制两种；「帧里是什么」对它不透明，故能被任意协议复用（SSE 同时服务 Anthropic/Gemini/OpenAI）。</li>
    <li><strong>六个正交旋钮</strong>：id/protocol/endpoint/auth/transport/framing 拼成一个 Route，各自独立替换。前几课的「轻巧复用」本质都是「只拧一两个旋钮」。</li>
  </ul>
  <p>M6 到此，LLM 协议层的全貌已在你眼前：core 说一种规范语（L28），协议适配器把它翻成各家方言（L29 骨架 → L30~32 具体方言），传输层再把翻好的话真正送达（L33）。还剩两课收尾 M6：第 34 课深入<strong>流式事件与提示缓存</strong>（把 LLMEvent 流和第 24 课 Context Epoch 的基线前缀彻底打通），第 35 课讲<strong>模型解析与 GitHub Copilot provider</strong>（models.dev 目录、Copilot 这个特殊供应商）。骨架已立，剩下的是把两个最值得玩味的细节补全。</p>
</div>

<div class="card detail">
  <div class="tag">🔬 源码细节</div>
  <p>六个旋钮是怎么「拼」成一个 Route 的？看 <span class="mono">Route.make</span> 的签名（简化自 client.ts）：</p>
  <pre class="code"><span class="cm">// 一个 Route = 六个零件的组合</span>
Route.<span class="fn">make</span>({
  id,                  <span class="cm">// 路由标识</span>
  protocol,            <span class="cm">// Protocol&lt;Body, Frame, Event, State&gt;</span>
  endpoint,            <span class="cm">// 打哪个 URL</span>
  auth,                <span class="cm">// 怎么认证</span>
  transport,           <span class="cm">// HttpTransport / WebSocketTransport</span>
  framing,             <span class="cm">// Framing&lt;Frame&gt;：bytes → frames</span>
})</pre>
  <p>注意类型参数 <span class="mono">Frame</span> 是怎么<strong>把 framing 和 protocol 悄悄锁在一起</strong>的：<span class="mono">framing</span> 产出 <span class="mono">Framing&lt;Frame&gt;</span>，<span class="mono">protocol.stream.event</span> 是 <span class="mono">Codec&lt;Event, Frame&gt;</span>——两者的 <span class="mono">Frame</span> 必须是同一个类型，编译器才放行。这是个很漂亮的约束：旋钮虽然能自由组合，但「framing 切出来的帧」和「protocol 期望解码的帧」必须<strong>类型对得上</strong>。比如 SSE 的帧是 <span class="mono">string</span>（一段 data: JSON），那配它的 protocol 的 <span class="mono">stream.event</span> 就得是 <span class="mono">Codec&lt;Event, string&gt;</span>；Bedrock 二进制帧是解析后的对象，protocol 那边就得对得上。<strong>正交不等于放任</strong>：六个旋钮能自由组合，但类型系统在接缝处守着，不让你把「切出 string 帧的 framing」错配给「期望二进制帧的 protocol」。自由组合 + 类型兜底，这才是「积木」既灵活又不散架的秘密。</p>
</div>

<div class="card key">
  <div class="tag">🎯 本课要点</div>
  <ul>
    <li><strong>协议不碰网络</strong>：protocol 只管语言层编解码；真正搬字节的是传输基础设施（endpoint/auth/transport/framing）。两段以「请求体」「帧」为抽象接口对接，故可各自独立替换。</li>
    <li><strong>完整流水线（Route.stream）</strong>：①protocol.body.from 编码 → ②endpoint 寻址 → ③auth 签名 → ④transport 取字节流 → ⑤framing 切帧 → ⑥protocol.stream 解码成 LLMEvent。第 29 课的「两栏表」至此接上完整上下文。</li>
    <li><strong>两种 transport</strong>：HTTP（请求/响应，绝大多数）；WebSocket（持久双向，<span class="mono">sendText</span>+<span class="mono">messages</span> 流）。唯 OpenAI Responses 同时支持两者，印证第 31 课「HTTP 与 WS 共享请求体形状」。</li>
    <li><strong>framing = 字节流形状的缝</strong>（<span class="mono">framing.ts</span>）：<span class="mono">(bytes)=&gt;(frames)</span>，SSE（几乎所有 JSON HTTP 供应商）/ AWS 二进制两种；「帧里是什么」对它不透明，故 SSE 可同时服务 Anthropic/Gemini/OpenAI。</li>
    <li><strong>六个正交旋钮</strong>：<span class="mono">Route.make({id,protocol,endpoint,auth,transport,framing})</span>。前几课的复用本质都是「只拧一两个旋钮」（兼容=改 endpoint、Bedrock=改 framing、Responses WS=改 transport）。类型参数 <span class="mono">Frame</span> 在 framing↔protocol 接缝处强制对齐，正交但不放任。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead">Lessons 29–32, we walked through all six protocols' "dialects." But did you notice something: <strong>from start to finish, a protocol never touches the network</strong>. It only handles "what to encode the request into, what to decode the response into"—purely <strong>language-layer</strong> work. But the message has to actually go out, the bytes have to actually come back, right? This lesson's star is the <strong>conveyor belt that actually carries bytes</strong> beneath the protocol: transport, framing, endpoint, auth. Together with the protocol, they're assembled by <span class="mono">Route</span> into one complete pipeline. After this lesson, lesson 29's "two-column form" gets <strong>powered up and spinning</strong> for the first time—you'll see a request's <strong>full journey</strong> from canonical object through encoding, addressing, signing, going on the wire, framing, decoding, finally back into a stream of canonical events.</p>
<p>More importantly, this lesson reveals the <strong>final form</strong> of opencode's design: a <span class="mono">Route</span> isn't monolithic but assembled from <strong>six orthogonal knobs</strong>—protocol, endpoint, auth, transport, framing, plus an id. Each knob is independently swappable. That's exactly why lesson 31's "OpenAI-compatible only changes the endpoint" and lesson 32's "Bedrock only swaps framing" could be done so lightly, as "<strong>turn one knob, leave the rest</strong>." This lesson lays the six knobs out in a row to show you the full picture of this <strong>building-block</strong> architecture.</p>

<div class="card analogy">
  <div class="tag">🚚 Analogy</div>
  Same interpreter (protocol). He does one thing only: <strong>translate well</strong>. But for a letter to actually reach the other side, knowing how to translate is far from enough—you need a whole <strong>logistics crew</strong>: <strong>address (endpoint)</strong>—which door number to deliver to; <strong>credentials (auth)</strong>—the pass the door guard checks; <strong>mode of transport (transport)</strong>—call a "truck round trip" (HTTP: go once, deliver, haul back the receipt, done), or open a "always-on hotline" (WebSocket: line stays connected, back-and-forth anytime); <strong>envelope-cutting convention (framing)</strong>—is the receipt "printed line by line on paper, segmented by blank lines" (SSE), or "wrapped in fixed-format sealed bags with a seal check" (binary). The same interpreter, fitted with different addresses, credentials, transports, and cutting conventions, can serve wildly different contractors. <strong>The interpreter handles only language; what actually delivers the letter is this freely-combinable logistics crew.</strong>
</div>

<h2>One complete pipeline: how a request runs its full journey</h2>
<p>First assemble all of lessons 29–32's puzzle pieces and look at a request's <strong>full lifecycle</strong>. When the upper layer (remember lesson 17's <span class="mono">llm.stream(request)</span>?) starts a streaming request, <span class="mono">Route</span>'s <span class="mono">stream</span> method drives this conveyor belt:</p>
<div class="trace">
  <div class="t-row"><span class="t-num">①encode</span><span class="t-txt">protocol.body.from(request): canonical request → this vendor's body</span></div>
  <div class="t-row"><span class="t-num">②address</span><span class="t-txt">endpoint: assemble which URL to hit</span></div>
  <div class="t-row"><span class="t-num">③sign</span><span class="t-txt">auth: add API key / AWS signature, etc.</span></div>
  <div class="t-row"><span class="t-num">④on the wire</span><span class="t-txt">transport (HTTP/WS): send the request, get back a byte stream</span></div>
  <div class="t-row"><span class="t-num">⑤frame</span><span class="t-txt">framing: cut continuous bytes into frame after frame (SSE/binary)</span></div>
  <div class="t-row"><span class="t-num">⑥decode</span><span class="t-txt">protocol.stream: frame → canonical LLMEvent (lesson 29's state machine)</span></div>
</div>
<p>See clearly this belt's <strong>division of labor</strong>: ① and ⑥ are the <strong>protocol</strong>'s work (language layer, exhausted in L29–32); ②③④⑤ are the <strong>transport infrastructure</strong>'s work (network layer, this lesson's theme). The interface between the two halves is crisp: the protocol <strong>emits/eats only abstractions like "request body" and "frame,"</strong> caring nothing about how bytes fly across the network; while the transport infrastructure <strong>only carries bytes, only cuts frames</strong>, caring nothing about whether the frame holds Anthropic's blocks or Gemini's parts. This "each minds its own yard" is the root of the whole design being <strong>building-block-able</strong>: each segment knows only the abstract interface of its up/downstream, so each can be swapped alone.</p>
<div class="layers">
  <div class="layer"><div class="l-name">language layer · protocol</div><div class="l-desc">①body.from encode + ⑥stream decode; knows only "request body" and "frame," never touches the network</div></div>
  <div class="layer"><div class="l-name">network layer · transport infrastructure</div><div class="l-desc">②endpoint address + ③auth sign + ④transport on-wire + ⑤framing cut; only carries bytes, knows no dialect</div></div>
</div>
<p>This layering diagram is worth staring at a while: the horizontal line between the two layers is the whole LLM package's <strong>lifeline seam</strong>. Above the line is the world of "human language / model language," speaking <strong>semantics</strong> like blocks, parts, tool_calls; below the line is the world of "bytes / network," speaking <strong>mechanics</strong> like POST, CRC, UTF-8. A request crosses this line twice: descending, it's compressed from semantics to bytes (①→④); ascending, it's restored from bytes to semantics (⑤→⑥). Draw this line clearly and you understand why switching providers often "moves one layer, not the other"—because the two layers were <strong>cut apart along exactly this seam</strong>.</p>

<h2>Two transports: truck round-trip vs always-on hotline</h2>
<p>For step ④ "on the wire," opencode keeps two transports, for two starkly different "ways of going online":</p>
<div class="cols">
  <div class="col"><h4>HTTP (truck round-trip)</h4><p>Classic request/response: POST a request body out, haul the response body back as <strong>one byte stream</strong>, and the turn is done. Simple, universal, <strong>the vast majority of providers ride this</strong>. One round trip, clean.</p></div>
  <div class="col"><h4>WebSocket (always-on hotline)</h4><p>A <strong>persistent bidirectional connection</strong>: once connected, you can keep <span class="mono">sendText</span>-ing messages and receiving from the <span class="mono">messages</span> stream. Fits low-latency, real-time, bidirectional-interaction scenarios.</p></div>
</div>
<p>Who uses WebSocket? Search all of <span class="mono">protocols/</span> and you'll find <strong>the only one supporting both transports is OpenAI Responses</strong>—it provides both <span class="mono">httpTransport</span> and <span class="mono">webSocketTransport</span>. This picks up lesson 31's planted seed: Responses' request body is designed so "HTTP and WebSocket share one shape," the HTTP version adds <span class="mono">stream:true</span>, the WebSocket version adds <span class="mono">type:"response.create"</span>. The same protocol codec <strong>works just as well with a different transport underneath</strong>—more living proof of "protocol and transport are orthogonal": Responses' dialect is written once, walking on both HTTP and WebSocket legs. The others (Anthropic, Gemini, OpenAI Chat, Bedrock) currently ride only HTTP, but "to add WebSocket just configure a transport knob, untouching the protocol" is itself the headroom this architecture left.</p>
<p>Why does HTTP nearly dominate while WebSocket is just an occasional option? Because for "send one request, stream back one reply," HTTP's "truck round-trip" is enough and most carefree: one POST, one response-body stream, done—stateless, no long connection to maintain, treated kindly by all network infrastructure. WebSocket's "always-on hotline" is more powerful but also heavier—you must manage connection setup, keepalive, reconnect on drop, no small cost. Its real value is in <strong>bidirectional, real-time, low-latency</strong> scenarios: e.g. interjecting mid-generation, or demanding millisecond round-trips. OpenAI Responses keeps both precisely because it targets those <strong>real-time-interaction</strong> advanced uses. In other words, opencode doesn't "adopt WebSocket to be trendy," but <strong>uses whichever transport is worthwhile</strong>, making the choice a knob you can turn anytime—itself engineering clarity.</p>

<h2>framing: the seam between transport and protocol</h2>
<p>Step ⑤ "framing" deserves its own section, because it's <strong>the most exquisite seam in the whole design</strong>. <span class="mono">framing.ts</span>'s comment defines it beautifully: "<strong>Framing is the byte-stream-shaped seam between transport and protocol</strong>." Its interface is as simple as one function: <span class="mono">frame: (byte stream) =&gt; frame stream</span>.</p>
<div class="flow">
  <div class="f-node">byte stream<br><small>raw bytes transport hauls back</small></div>
  <div class="f-arrow">framing.frame →</div>
  <div class="f-node">SSE: cut by data:<br>binary: cut by length+CRC</div>
  <div class="f-arrow">→</div>
  <div class="f-node">frame stream<br><small>handed to protocol.stream to decode</small></div>
</div>
<p>opencode builds in two framings. <strong>SSE</strong> (<span class="mono">Framing.sse</span>): UTF-8 decode the bytes, run the SSE channel decoder, drop empty lines and <span class="mono">[DONE]</span> keep-alive signals, and each frame is one event's <span class="mono">data:</span> JSON payload—<strong>nearly every JSON-streaming HTTP provider uses it</strong>. <strong>AWS binary event stream</strong>: exactly the length-prefixed, CRC-checksummed binary frames you saw in lesson 32. The key is the comment's last line: "<strong>the frame type is opaque to this layer</strong>"—framing only "cuts bytes into portions," and as for what each portion holds, it <strong>doesn't care at all</strong>—that's the protocol <span class="mono">stream.event</span> decode's worry. Precisely because framing stays ignorant of "what's in the frame," it can be <strong>reused by any protocol</strong>: the single SSE framing serves Anthropic, Gemini, and OpenAI's three completely different dialects at once. A seam cut just right buys both layers their respective freedom. Conversely, had there been no framing seam, with each protocol clawing frames from the byte stream itself, then "cut by data: blank line" logic would have to be <strong>copied into each of</strong> Anthropic, Gemini, OpenAI—again the duplication lesson 28 most abhors. framing extracts the "byte→frame" dirty work common to all three into <strong>one independent, reusable part</strong>—exactly "find the commonality, factor it out," the wisdom running through this whole book, making another appearance at the transport layer.</p>

<h2>Six orthogonal knobs: the building-block Route</h2>
<p>Combine this lesson with the prior ones and the <strong>final form</strong> of opencode's LLM layer is clear: a <span class="mono">Route</span> is assembled from <strong>six independently-swappable knobs</strong>.</p>
<div class="cellgroup">
  <div class="cell"><div class="c-tag">id</div><div class="c-txt">route identity, for diagnostics & resolution</div></div>
  <div class="cell"><div class="c-tag">protocol</div><div class="c-txt">dialect codec (body.from + stream.step)</div></div>
  <div class="cell"><div class="c-tag">endpoint</div><div class="c-txt">which URL to hit</div></div>
  <div class="cell"><div class="c-tag">auth</div><div class="c-txt">how to sign/authenticate</div></div>
  <div class="cell"><div class="c-tag">transport</div><div class="c-txt">HTTP or WebSocket</div></div>
  <div class="cell"><div class="c-tag">framing</div><div class="c-txt">SSE or binary framing</div></div>
</div>
<p>Lay each vendor out by these knobs' values and you'll instantly understand what those "light reuses" in prior lessons really were:</p>
<table class="t">
  <tr><th>Vendor</th><th>protocol</th><th>transport</th><th>framing</th></tr>
  <tr><td>Anthropic</td><td>anthropic-messages</td><td>HTTP</td><td>SSE</td></tr>
  <tr><td>Gemini</td><td>gemini</td><td>HTTP</td><td>SSE</td></tr>
  <tr><td>OpenAI Chat</td><td>openai-chat</td><td>HTTP</td><td>SSE</td></tr>
  <tr><td>OpenAI-compatible</td><td>openai-chat (reused!)</td><td>HTTP</td><td>SSE</td></tr>
  <tr><td>OpenAI Responses</td><td>openai-responses</td><td>HTTP or WS</td><td>SSE</td></tr>
  <tr><td>Bedrock</td><td>bedrock-converse</td><td>HTTP</td><td>binary event stream</td></tr>
</table>
<p>This table demystifies all the prior lessons' "magic": "OpenAI-compatible" just turns the protocol knob to <span class="mono">openai-chat</span> and changes the endpoint (lesson 31's 24 lines); "Bedrock" just turns the framing knob from SSE to binary, reusing Anthropic's set as much as possible (lesson 32); "Responses on WebSocket" just turns the transport knob from HTTP to WS. <strong>Every seemingly-clever reuse is essentially "turn one or two knobs, leave the rest."</strong> That's the compounding of orthogonal decomposition: six knobs each own one dimension, yet the combination space covers all real-world providers, and the cost of adding one is often just <strong>picking a fitting set of values for the six knobs</strong>.</p>

<div class="card macro">
  <div class="tag">🗺️ The Big Picture</div>
  <p>This lesson collects M6's puzzle into one complete picture:</p>
  <ul>
    <li><strong>Protocol never touches the network</strong>: protocol owns only the language layer (body.from encode / stream decode); the transport infrastructure (endpoint/auth/transport/framing) actually carries bytes. The two halves interface cleanly via "request body" and "frame" abstractions.</li>
    <li><strong>The complete pipeline</strong>: ①body.from encode → ②endpoint address → ③auth sign → ④transport on-wire to byte stream → ⑤framing cut frames → ⑥protocol.stream decode to LLMEvent. Lesson 29's form is now "powered up."</li>
    <li><strong>Two transports</strong>: HTTP (request/response, the vast majority) vs WebSocket (persistent bidirectional, only OpenAI Responses supports both, confirming lesson 31's shared request-body shape).</li>
    <li><strong>framing is the byte-stream-shaped seam</strong>: <span class="mono">(byte stream)=&gt;(frame stream)</span>, SSE / binary; "what's in the frame" is opaque to it, so it's reusable by any protocol (SSE serves Anthropic/Gemini/OpenAI at once).</li>
    <li><strong>Six orthogonal knobs</strong>: id/protocol/endpoint/auth/transport/framing assemble a Route, each independently swappable. The prior lessons' "light reuses" are all "turn one or two knobs."</li>
  </ul>
  <p>With M6 here, the LLM protocol layer's full picture is before you: core speaks one canonical language (L28), protocol adapters translate it into each dialect (L29 skeleton → L30–32 concrete dialects), the transport layer actually delivers the translated message (L33). Two lessons remain to wrap up M6: lesson 34 dives into <strong>streaming events and prompt caching</strong> (fully connecting the LLMEvent stream to lesson 24's Context Epoch baseline prefix), lesson 35 covers <strong>model resolution and the GitHub Copilot provider</strong> (the models.dev catalog, Copilot as a special provider). The skeleton stands; what remains is filling in the two most intriguing details.</p>
</div>

<div class="card detail">
  <div class="tag">🔬 Source Detail</div>
  <p>How do the six knobs "assemble" into a Route? Look at <span class="mono">Route.make</span>'s signature (simplified from client.ts):</p>
  <pre class="code"><span class="cm">// one Route = a composition of six parts</span>
Route.<span class="fn">make</span>({
  id,                  <span class="cm">// route identity</span>
  protocol,            <span class="cm">// Protocol&lt;Body, Frame, Event, State&gt;</span>
  endpoint,            <span class="cm">// which URL to hit</span>
  auth,                <span class="cm">// how to authenticate</span>
  transport,           <span class="cm">// HttpTransport / WebSocketTransport</span>
  framing,             <span class="cm">// Framing&lt;Frame&gt;: bytes → frames</span>
})</pre>
  <p>Note how the type parameter <span class="mono">Frame</span> <strong>quietly locks framing and protocol together</strong>: <span class="mono">framing</span> produces <span class="mono">Framing&lt;Frame&gt;</span>, <span class="mono">protocol.stream.event</span> is <span class="mono">Codec&lt;Event, Frame&gt;</span>—the two <span class="mono">Frame</span>s must be the same type for the compiler to pass. It's a beautiful constraint: the knobs can combine freely, but "the frame framing cuts out" and "the frame protocol expects to decode" must <strong>match in type</strong>. If SSE's frame is <span class="mono">string</span> (a data: JSON segment), the protocol pairing it must have <span class="mono">stream.event</span> of <span class="mono">Codec&lt;Event, string&gt;</span>; Bedrock's binary frame is a parsed object, so the protocol there must match. <strong>Orthogonal doesn't mean lawless</strong>: the six knobs combine freely, but the type system guards the seam, not letting you mis-pair a "framing that cuts string frames" with a "protocol expecting binary frames." Free composition + type backstop—that's the secret to the "building blocks" being both flexible and not falling apart.</p>
</div>

<div class="card key">
  <div class="tag">🎯 Key Takeaways</div>
  <ul>
    <li><strong>Protocol never touches the network</strong>: protocol owns only language-layer codec; what actually moves bytes is the transport infrastructure (endpoint/auth/transport/framing). The two halves interface via "request body" and "frame" abstractions, so each is independently swappable.</li>
    <li><strong>The complete pipeline (Route.stream)</strong>: ①protocol.body.from encode → ②endpoint address → ③auth sign → ④transport to byte stream → ⑤framing cut frames → ⑥protocol.stream decode to LLMEvent. Lesson 29's "two-column form" now has its full context.</li>
    <li><strong>Two transports</strong>: HTTP (request/response, the vast majority); WebSocket (persistent bidirectional, <span class="mono">sendText</span>+<span class="mono">messages</span> stream). Only OpenAI Responses supports both, confirming lesson 31's "HTTP and WS share request-body shape."</li>
    <li><strong>framing = the byte-stream-shaped seam</strong> (<span class="mono">framing.ts</span>): <span class="mono">(bytes)=&gt;(frames)</span>, SSE (nearly all JSON HTTP providers) / AWS binary; "what's in the frame" is opaque to it, so SSE serves Anthropic/Gemini/OpenAI at once.</li>
    <li><strong>Six orthogonal knobs</strong>: <span class="mono">Route.make({id,protocol,endpoint,auth,transport,framing})</span>. Prior lessons' reuses are all "turn one or two knobs" (compatible=change endpoint, Bedrock=change framing, Responses WS=change transport). The type parameter <span class="mono">Frame</span> forces framing↔protocol alignment at the seam—orthogonal but not lawless.</li>
  </ul>
</div>
""",
}
LESSON_34 = wip('流式事件与缓存', 'Streaming & caching')
LESSON_35 = wip('模型解析与 Copilot provider', 'Model resolution & Copilot')
