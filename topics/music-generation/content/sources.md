<span class="badge">来源 / 截至 2026-09-09</span>

# 要复查，就看这几处

正文链接直接指向数据卡、论文或官方实现。下面按问题找；不用从头读完论文。

| 想查什么 | 看哪份原始资料 |
|---|---|
| 文字音频对的字段；从标签合成描述 | [MusicCaps 数据卡](https://huggingface.co/datasets/google/MusicCaps)；[LP-MusicCaps](https://arxiv.org/abs/2307.16372)；[Mustango v3 的数据增强](https://arxiv.org/html/2311.08355v3) |
| 32 kHz、50 Hz、4 码本；MusicGen 训练 | [MusicGen v3](https://arxiv.org/html/2306.05284v3)；[AudioCraft 训练说明](https://github.com/facebookresearch/audiocraft/blob/main/docs/MUSICGEN.md) |
| 多轨数据与清唱配伴奏 | [MUSDB / HQ](https://sigsep.github.io/datasets/musdb.html)；[AnyAccomp v1](https://arxiv.org/html/2509.14052v1) §2–3 |
| 歌词与两轨音频怎样建模 | [YuE v1](https://arxiv.org/html/2503.08638v1) §3；[LeVo 2 v1](https://arxiv.org/html/2606.30642v1) 数据与架构部分 |
| MIDI 与录音的真实配对 | [MAESTRO v3](https://magenta.withgoogle.com/datasets/maestro) |
| 扩散音频模型喂什么 | [Stable Audio Open v2](https://arxiv.org/html/2407.14358v2) §2、§4 |
| JD 提到的旧路线 | [Riffusion 原始实现](https://github.com/riffusion/riffusion)；[Jukebox](https://arxiv.org/abs/2005.00341) |
| 时间变化的旋律 / 节奏控制 | [Music ControlNet 摘要](https://arxiv.org/abs/2311.07069)；[MusicGen melody](https://github.com/facebookresearch/audiocraft/blob/main/docs/MUSICGEN.md) |
| 2026 规划与声学渲染的拆分 | [ACE-Step 1.5 v3](https://arxiv.org/html/2602.00744v3)；[Qwen-Music v2](https://arxiv.org/html/2607.11699v2)；[FullDiT v2](https://arxiv.org/html/2608.08787v2) |
| 自动评测的用途与边界 | [CLAP 实现](https://github.com/LAION-AI/CLAP)；[FAD for Music v2](https://arxiv.org/html/2311.01616v2)；[SongBench v1](https://arxiv.org/html/2604.25937v1) |

## 公开资料与教学示例

**公开事实：** 数据集规模、字段、模型组件与训练路线来自以上原文；2026 条目是截止日已公开的对应版本，不等于效果排名。

**自己制作：** WAV、波形 / 频谱、8 音 MIDI、样本 JSON、三分类与两参数训练器。处理数值可复算；声音不是 MusicGen、AnyAccomp 或商业模型输出。合成“哼唱”是振荡器与谐波产生的音色。

**两天怎么用：** 第一天把“文字→纯音乐”和“清唱→伴奏”的一条样本讲通，点击训练 / 推理，再换成自己的例子；第二天听完五组错误，补歌词、MIDI 和 JD。每页底部可记录自己的做法并导出。
