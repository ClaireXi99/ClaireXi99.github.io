<span class="badge">基本任务 04 / 音符序列 → MIDI → 声音</span>

# MIDI 是“弹什么”，WAV 是“听到什么”

<p class="intro">MIDI 记录音高、起止、力度和乐器事件。先学着写音符，再用音源演奏，就得到声音。</p>

## ① 数据长什么样？

**MAESTRO v3：1,276 段、198.7 小时**钢琴演奏，每段同时有 MIDI 和音频，时间对齐精度约 3 ms。训练“写音符”可用 MIDI；训练“听音乐转谱”则拿音频作输入、MIDI 作目标。[官方数据页](https://magenta.withgoogle.com/datasets/maestro)

下面自己造 8 个音，120 BPM，每拍 `60/120=0.5 秒`：

| 音名 | MIDI 编号 | 起始 | 持续 | 力度 |
|---|---:|---:|---:|---:|
| C4 | 60 | 0.0 秒 | 0.5 秒 | 90 |
| E4 | 64 | 0.5 秒 | 0.5 秒 | 90 |
| G4 | 67 | 1.0 秒 | 0.5 秒 | 90 |
| C5 | 72 | 1.5 秒 | 0.5 秒 | 90 |

后四音是 `67、64、62、60`。清洗时：检查音符结束是否晚于开始、去掉损坏事件、保留速度与踏板信息；同一乐曲的不同演奏尽量同组切分，避免背熟曲子后“测出高分”。MAESTRO 已提供按作品隔离的划分。

## ② 模型到底在预测哪一个？

```text
简化为只预测音高（假定时长与力度固定）：
输入 [60, 64] → 正确下一个音 67
p(67)=0.20 → loss=−ln(0.20)=1.609 → 反向传播 → 提高 67 的概率

真实事件序列还要学时长和力度，例如：
VELOCITY_90 → NOTE_ON_60 → TIME_SHIFT_500ms → NOTE_OFF_60
→ NOTE_ON_64 → TIME_SHIFT_500ms → NOTE_OFF_64 → ...
```

训练时用真实历史预测后续事件；推理时给一个开头，模型接着写音符。若任务改为**旋律配和弦**，条件是旋律音符，目标是同一时间段的和弦 / 伴奏音符轨；若条件增加“爵士”，就需要带对应风格的训练配对。事件编码是示意，不是所有 MIDI 模型的统一格式。

## ③ 改几个数字，听音乐怎样变化

<div class="lab" id="midi-lab"><div class="lab-head"><div><h3>8 个音，真的生成 MIDI 文件</h3><p class="micro">试听使用简单三角波音源；下载的 .mid 可换钢琴、吉他等音源播放。</p></div><div class="actions"><button class="primary" id="midi-play">播放</button><button id="midi-stop">停止</button><button id="midi-download">下载当前 .mid</button></div></div><div class="two"><div><label for="midi-bpm">速度：<strong id="midi-bpm-value"></strong></label><input type="range" id="midi-bpm" min="60" max="180" step="10" value="120"></div><div><label for="midi-transpose">整体移调：<strong id="midi-transpose-value"></strong></label><input type="range" id="midi-transpose" min="-12" max="12" step="1" value="0"></div></div><svg id="midi-roll" class="chart-svg piano-roll" viewBox="0 0 720 195" role="img" aria-label="可调整速度和音高的八音钢琴卷帘图"></svg><p>当前总时长：<strong id="midi-duration"></strong>。纵轴是 MIDI 音高编号，横轴是秒。</p><details class="extra"><summary>展开当前的 8 条音符记录</summary><pre id="midi-events"></pre></details><p id="midi-status" class="micro" role="status"></p></div>

把 120 调成 **60 BPM**：每音从 0.5 秒变 1 秒，总长从 4 秒变 8 秒，音高不变。升 **12 半音**：60 变 72，高一个八度，时长不变。**这正是构造可控生成样本时要同步更新的标签。**

[直接下载默认的 120 BPM 示例 MIDI](assets/audio/example-120bpm.mid)。

## ④ 怎么评？先区分转写和创作

**转写有标准答案：** 参考 8 个音，预测 9 个；规定“音高相同且起音误差 ≤50 ms”才算匹配，若一对一匹配 7 个，则精确率 `7/9=77.8%`、召回率 `7/8=87.5%`、F1 `82.4%`。这个示例没有评结束时间与力度。

**创作没有唯一答案：** 给 C 大调、120 BPM、8 拍，检查调性、时长、节奏约束，再听旋律是否自然；不要拿逐音符准确率惩罚合理的新旋律。
