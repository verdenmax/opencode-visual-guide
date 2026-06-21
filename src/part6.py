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
LESSON_29 = wip('协议适配器', 'Protocol adapters')
LESSON_30 = wip('Anthropic Messages 协议', 'The Anthropic protocol')
LESSON_31 = wip('OpenAI Chat/Responses 协议', 'The OpenAI protocols')
LESSON_32 = wip('Gemini 与 Bedrock 协议', 'Gemini & Bedrock')
LESSON_33 = wip('路由与传输', 'Routing & transport')
LESSON_34 = wip('流式事件与缓存', 'Streaming & caching')
LESSON_35 = wip('模型解析与 Copilot provider', 'Model resolution & Copilot')
