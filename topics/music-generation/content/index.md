<span class="badge">重点 01 / 文字 → 纯音乐</span>

# 一句描述，怎么变成一段音乐？

<p class="intro">音频剪干净，配上描述，压成 token。模型猜错哪个 token，就对那个位置算 loss、更新参数。</p>

## ① 业界的数据，里面实际是什么？

**MusicCaps：5,521 条、每段 10 秒。** 每行是录音 ID、起止时间、乐器 / 风格列表、音乐人写的描述；音频需另行取得。它同时包含有人声与器乐的片段。[数据卡](https://huggingface.co/datasets/google/MusicCaps)

```text
按其字段构造一行教学样本：
录音 ID：demo_042       start_s：40       end_s：50
caption：明亮的键盘器乐，均匀鼓点，无人声。

取得对应音频 → 截取第 40–50 秒 → 得到 10 秒 WAV
```

真实训练更大：MusicGen 使用约 **2 万小时授权音乐**，带文字描述、BPM 和标签；MusicCaps 用于其评测。这里借它理解样本结构，不把它当成 MusicGen 的预训练库。[MusicGen §3.2](https://arxiv.org/html/2306.05284v3)

## ② 洗完后，这一条变成什么？ {#clean}

下面是程序合成的教学音频。原件首尾各有 1 秒空白，内容是 8 秒器乐。

<div class="two"><div class="audio-box"><h3>原始：10 秒 / 48 kHz / 双声道</h3><p>数组形状 [2, 480000]</p><audio controls preload="none" aria-label="原始十秒音频"><source src="assets/audio/raw-10s-stereo.wav" type="audio/wav"></audio></div><div class="audio-box"><h3>清洗：8 秒 / 32 kHz / 单声道</h3><p>数组形状 [1, 256000]</p><audio controls preload="none" aria-label="清洗后八秒音频"><source src="assets/audio/clean-8s-mono.wav" type="audio/wav"></audio></div></div>

<figure><img src="assets/plots/crop.svg" alt="十秒原始波形，蓝色范围是保留的一到九秒"><figcaption>剪 1–9 秒 → 下混单声道 → 重采样。乐句中的休止符不剪。</figcaption></figure>

| 这一批有 4 条 | 发现的问题 | 处理 |
|---|---|---|
| 042：键盘 + 鼓 | 首尾空白，描述正确 | 剪成 8 秒，保留 |
| 043：与 042 同录音 | 只是文件格式不同 | 去重，不另放测试集 |
| 044：描述写“无人声” | 听到哼唱 | 纯音乐任务剔除，或改标签转其他任务 |
| 045：波形严重削平 | 放大造成破音 | 剔除；调低音量修不回失真 |

交付的核心是一对：

```json
{
  "text": "明亮的键盘器乐，均匀鼓点，无人声。",
  "audio": "clean-8s-mono.wav",
  "duration": 8,
  "sample_rate": 32000
}
```

### 有音频、没描述，怎么合成文字配对？

```text
同一条 8 秒音频
听审 / 标签器：器乐、键盘、鼓；节拍检测：120 BPM
        ↓ 只写已经验证的属性
描述 A：“明亮的键盘器乐，均匀鼓点，无人声。”
描述 B：“120 BPM，键盘主奏，带鼓的纯音乐。”
        ↓
得到 2 条 text–audio 配对，但只有 1 条独立音频
```

再做一次**保音高变速 1.25 倍**：8 秒变 6.4 秒、120 BPM 变 150；描述 B 的 BPM 必须改成 150。标签转描述可参考 LP-MusicCaps，音频增强后同步修改属性可参考 Mustango。[LP-MusicCaps](https://arxiv.org/abs/2307.16372) · [Mustango](https://arxiv.org/html/2311.08355v3)

描述不能凭空补“悲伤、小提琴”。合成描述后要回听校验；同一原曲的改写、切片、变速版都放同一训练 / 测试分区。

## ③ 喂给 MusicGen 的不是 WAV 文件名

<div class="steps"><div><b>文字条件</b><strong>一句描述 → 向量</strong><small>文字编码器表示乐器与风格</small></div><div><b>音频目标</b><strong>8 × 32,000</strong><small>256,000 个波形采样值</small></div><div><b>EnCodec 压缩</b><strong>4 × 400</strong><small>4 码本 × 50 帧/秒 × 8 秒</small></div><div><b>Transformer</b><strong>预测目标 token</strong><small>输入文字与前面的音频 token</small></div></div>

```text
示意 token ID（未运行真实 EnCodec）
码本 1：[8, 17, 42, ...]     约 400 个时间位置
码本 2：[91, 203, 66, ...]
码本 3：[...]
码本 4：[...]

放大码本 1 的一个位置：
输入 = 文字向量 + 历史 [8]
目标 = 17
```

token 是音频码本编号，**不等于歌词或一个音符**。真实 MusicGen 交错多个码本，对有效位置求平均 loss；下面只演示一个位置。[实现说明](https://github.com/facebookresearch/audiocraft/blob/main/docs/MUSICGEN.md)

## ④ 它怎么“往正确方向学”？ {#train}

<div class="lab" id="ar-lab"><div class="lab-head"><div><h3>已知正确答案：token 17</h3><p class="micro">真实计算的三分类 softmax 玩具模型。固定输入 x=1，logits=W×x。</p></div><div class="actions"><button class="primary" id="ar-step">训练 1 步</button><button id="ar-many">训练 20 步</button><button id="ar-reset">重置</button></div></div><div class="lab-grid"><div><div class="prob-row"><span>token 8</span><div class="prob-track"><div class="prob-fill" id="prob-0"></div></div><span id="prob-label-0"></span></div><div class="prob-row target"><span>17 ✓</span><div class="prob-track"><div class="prob-fill" id="prob-1"></div></div><span id="prob-label-1"></span></div><div class="prob-row"><span>token 42</span><div class="prob-track"><div class="prob-fill" id="prob-2"></div></div><span id="prob-label-2"></span></div><p class="micro">起初正解概率只有 10%。点击训练，观察它上升。</p></div><div class="readouts"><div class="readout"><small>正确 token 的概率</small><strong id="ar-prob"></strong></div><div class="readout"><small>loss = −ln(p)</small><strong id="ar-loss"></strong></div><div class="readout"><small>参数已更新</small><strong id="ar-count"></strong></div><div class="readout"><small>当前正确类梯度 p − 1</small><strong id="ar-gradient"></strong></div></div></div><div class="math-line" id="ar-math"></div><svg class="chart-svg" id="ar-chart" viewBox="0 0 700 145" role="img" aria-label="随训练下降的交叉熵曲线"></svg><div class="infer-box"><span class="mode-label">推理：不给正确答案 17</span><p>只给文字与历史 [8]，按当前概率抽一个 token。学过后更容易抽到 17，但不一定每次都抽到。</p><button id="ar-sample">采样一次</button><div class="infer-result" id="ar-result" aria-live="polite">先训练，再采样；也可以在训练前比较。</div></div></div>

第一步：`p=0.10 → loss=2.303 → 梯度=−0.90`。减去负梯度会抬高正确类权重。真实网络将梯度传回 Transformer 的参数；**目标音频不变，模型参数改变**。

## ⑤ 完整推理：从文字一路生成到声音

<div class="steps"><div><b>给条件</b><strong>“键盘、鼓、无人声”</strong><small>不提供目标音频</small></div><div><b>生成</b><strong>逐步产生多码本 token</strong><small>历史来自模型自己的输出</small></div><div><b>解码</b><strong>tokens → EnCodec → WAV</strong><small>得到新的纯音乐</small></div></div>

**标签错会直接教错：** 若音频有人声，描述却写“无人声”，模型就会把两者一起学习。这就是清洗、筛选、打标影响模型的具体位置。
