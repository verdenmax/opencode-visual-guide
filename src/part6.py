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
LESSON_30 = wip('Anthropic Messages 协议', 'The Anthropic protocol')
LESSON_31 = wip('OpenAI Chat/Responses 协议', 'The OpenAI protocols')
LESSON_32 = wip('Gemini 与 Bedrock 协议', 'Gemini & Bedrock')
LESSON_33 = wip('路由与传输', 'Routing & transport')
LESSON_34 = wip('流式事件与缓存', 'Streaming & caching')
LESSON_35 = wip('模型解析与 Copilot provider', 'Model resolution & Copilot')
