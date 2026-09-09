<span class="badge">评测 / 先听出问题，再看数值</span>

# 一段音乐不好，到底哪里不好？

<p class="intro">同一段 8 秒教学音频，人工制造五种错误。点选问题，先 A/B 听，再看对应图。全部是程序合成示例，不代表任何真实模型得分。</p>

<p class="micro">A/B 播放按均方根幅度 RMS 匹配，避免仅因更响而偏好；并非 LUFS 响度匹配。削波与频带图、数值展示音量匹配前的处理信号。</p>

<div class="eval-switch" role="group" aria-label="选择评测错误"><button data-eval="clipping" aria-pressed="true">① 削波破音</button><button data-eval="band" aria-pressed="false">② 高频被削弱</button><button data-eval="timing" aria-pressed="false">③ 伴奏晚半拍</button><button data-eval="leak" aria-pressed="false">④ 伴奏漏人声</button><button data-eval="pitch" aria-pressed="false">⑤ 音高冲突</button></div>

<section class="eval-panel" id="clipping">
<h2>① 峰顶变平了：削波</h2>
<div class="two"><div class="audio-box"><h3 class="good">A · 原始器乐</h3><audio controls preload="none" aria-label="无削波原音"><source src="assets/audio/clip-good.wav" type="audio/wav"></audio></div><div class="audio-box"><h3 class="bad">B · 放大 6 倍后截到 ±1</h3><audio controls preload="none" aria-label="削波失真音频"><source src="assets/audio/clip-bad.wav" type="audio/wav"></audio></div></div>
<figure><img src="assets/plots/clipping.svg" alt="上图正常峰值，下图正负一处出现削平的平台"><figcaption>波形看幅度。下图的尖峰被砍掉，调小音量后平台仍在。</figcaption></figure>
<div class="verdict"><div><span>A · 本例触顶采样占比</span><b>0.0%</b></div><div><span>B · 本例被截断的采样占比</span><b>{{clip_ratio_bad_percent}}%</b></div></div>
<p><strong>判法：</strong>本例知道失真来自硬截断。真实生成音频先查连续平顶 / 触顶占比，再听是否破裂、刺耳；不能用“没有触到 ±1”证明没有失真，因为成品可能已经降过音量。</p>
<p><strong>回到数据：</strong>剔除破音目标，检查增益处理。不要把“音量归一化”当成修复削波。</p>
</section>

<section class="eval-panel" id="band" hidden>
<h2>② 镲片闷了：高频能量被削弱</h2>
<div class="two"><div class="audio-box"><h3 class="good">A · 原始器乐</h3><audio controls preload="none" aria-label="高频完整音频"><source src="assets/audio/band-good.wav" type="audio/wav"></audio></div><div class="audio-box"><h3 class="bad">B · 人工衰减高频</h3><audio controls preload="none" aria-label="高频衰减音频"><source src="assets/audio/band-bad.wav" type="audio/wav"></audio></div></div>
<figure><img src="assets/plots/bandwidth.svg" alt="蓝线原始功率谱，红线高频衰减，六到十千赫兹区域降低约二十分贝"><figcaption>频谱看哪些频率有能量。阴影是 6–10 kHz；红线显著下降。</figcaption></figure>
<div class="verdict"><div><span>查看区域</span><b>6–10 kHz</b></div><div><span>B 相对 A 的带内能量下降</span><b>{{band_6_10k_drop_db}} dB</b></div></div>
<p><strong>判法：</strong>同一编曲里镲片、空气感变少，这次是处理损伤。但低保真风格可能故意少高频，纯贝斯也可能本来就没有高频。没有“所有音乐在这一波段都要强”的规则。</p>
<p><strong>回到数据：</strong>查原文件实际带宽与重采样过程。8 kHz 采样率的音频最高只能表示到 4 kHz；升采样成 48 kHz，不会长出丢失的高频。</p>
</section>

<section class="eval-panel" id="timing" hidden>
<h2>③ 音色没坏，但唱声和伴奏分家了</h2>
<div class="two"><div class="audio-box"><h3 class="good">A · 原始对齐混音</h3><audio controls preload="none" aria-label="对齐的人声伴奏"><source src="assets/audio/timing-good.wav" type="audio/wav"></audio></div><div class="audio-box"><h3 class="bad">B · 伴奏整体晚 250 ms</h3><audio controls preload="none" aria-label="伴奏晚半拍的混音"><source src="assets/audio/timing-bad.wav" type="audio/wav"></audio></div></div>
<figure><img src="assets/plots/timing.svg" alt="120BPM每半秒一拍，正常伴奏对齐，错误伴奏整体后移四分之一秒"><figcaption>本例节拍网格：120 BPM → 每拍 500 ms。红色比蓝色晚 250 ms，也就是半拍。</figcaption></figure>
<p><strong>判法：</strong>在规定拍点同步的样本中，对人声 / 伴奏提取起音与节拍，再做一对一时间匹配。本例偏移是已知人为设置；真实音乐有切分、弱起、自由速度，不能要求每个唱字都与鼓点重合。</p>
<p><strong>回到数据：</strong>用同一时间窗裁两轨，核对重采样和分离模型的延迟；另外测真实手机清唱，不能只测从训练歌曲拆出来的人声。</p>
</section>

<section class="eval-panel" id="leak" hidden>
<h2>④ 任务说“只配伴奏”，结果又哼起来了</h2>
<div class="two"><div class="audio-box"><h3 class="good">A · 仅伴奏</h3><audio controls preload="none" aria-label="没有漏人声的伴奏"><source src="assets/audio/leak-good.wav" type="audio/wav"></audio></div><div class="audio-box"><h3 class="bad">B · 伴奏 + 0.35 × 哼唱</h3><audio controls preload="none" aria-label="漏入哼唱的伴奏"><source src="assets/audio/leak-bad.wav" type="audio/wav"></audio></div></div>
<figure><img src="assets/plots/leakage.svg" alt="同一色阶的上下时频谱，加入哼唱后出现随旋律持续移动的谐波纹理"><figcaption>时频图同时看时间与频率。下图多出的持续谐波来自这次人工混入的哼唱；普通乐器也有谐波，图本身不能认定是人声。</figcaption></figure>
<p><strong>判法：</strong>单独听生成伴奏，用人声检测 / 分离辅助定位，再人工确认。本例的 0.35 是加入人声的幅度系数，不是“35% 漏声率”。实际可报“20 条伴奏里 3 条听到人声 = 样本漏声率 15%”（统计示例）。</p>
<p><strong>回到数据：</strong>查目标伴奏中的残留；也查输入分离人声里是否带伴奏碎片，防止模型靠碎片猜答案。用干净录音与乐器旋律再测泛化。</p>
</section>

<section class="eval-panel" id="pitch" hidden>
<h2>⑤ 伴奏全升了一个半音，人声没动</h2>
<div class="two"><div class="audio-box"><h3 class="good">A · 原始调性关系</h3><audio controls preload="none" aria-label="原始调性的人声伴奏"><source src="assets/audio/key-good.wav" type="audio/wav"></audio></div><div class="audio-box"><h3 class="bad">B · 只升伴奏，不升人声</h3><audio controls preload="none" aria-label="伴奏错误升半音的混音"><source src="assets/audio/key-bad.wav" type="audio/wav"></audio></div></div>
<figure><img src="assets/plots/pitch.svg" alt="C4为261.6赫兹，升一个半音后C升4为277.2赫兹"><figcaption>单音频率示意，非整段频谱：261.6 × 2^(1/12) ≈ 277.2 Hz。本例把有音高的伴奏声部整体升调。</figcaption></figure>
<p><strong>判法：</strong>对照旋律与和弦听冲突，用音高、chroma、调性 / 和弦识别定位。本例错在改变了原有配对关系；不能把不同音就算成错误，否则三和弦 C–E–G 也会被误杀。</p>
<p><strong>回到数据：</strong>移调、变速必须同步作用于条件和目标；风格迁移任务则保留约定的旋律 / 结构，允许换音色与合理和声。</p>
</section>

## 从“看一条”到“比较两个模型”

固定一份未见过的测试表：**纯音乐 12 题、清唱 12 段、歌词 12 题**，每个模型每题生成 2 次，就是每模型 72 条。这里是小规模试跑设定；不要用它代替大规模评估。

| 任务 | 每条先查 | 再盲听 A/B |
|---|---|---|
| “键盘、120 BPM、无人声” | 乐器 / 人声是否匹配；BPM；破音 | 描述遵循、音质、乐句是否自然 |
| 同一段清唱配伴奏 | 延迟、漏声、和声冲突 | 是否托住人声；清唱混进去是否协调 |
| 给定歌词成歌 | CER、漏唱、重复、长静音 | 唱腔、句间衔接、整曲结构 |

同一题用相同长度、生成次数与选样规则，随机隐藏模型名。记录“哪题、哪秒、什么问题”，例如：`V07 / 2.0–3.5s / 伴奏漏人声 / 返回目标拆轨复查`。改好数据后，用**固定测试集**重测对应问题。

## 三种分数，只放在它能回答的位置

| 分数 | 它回答什么 | 具体盲点 |
|---|---|---|
| CLAP 音文相似度 | 这段像不像“吉他、鼓”的描述 | 像吉他仍可能破音；不能可靠证明 120 BPM |
| FAD | 一批生成音乐的嵌入分布与参考集有多接近 | 换参考集、嵌入模型或样本量会变；不是单曲“好听分” |
| 人工分维度评分 / A/B | 是否自然、协调、值得听 | 要固定量表、随机盲听、记录分歧；不能只挑最好样本 |

实现与局限：[CLAP](https://github.com/LAION-AI/CLAP) · [FAD for music](https://arxiv.org/html/2311.01616v2)。整曲维度可参考 [SongBench（2026）](https://arxiv.org/html/2604.25937v1)，这里只保留当前两类任务真正要检查的项。
