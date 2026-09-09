<span class="badge">基本任务 03 / 歌词 + 风格 → 完整歌曲</span>

# “唱这些字”，需要怎样的训练数据？

<p class="intro">文字纯音乐学“声音像描述”；歌词成歌还要学“哪些字，在什么时候，怎么唱”。目标音频包含唱声和伴奏。</p>

## ① 从一首歌洗出一条配对

```text
原始：完整录音 song.wav + 整首歌词 + 风格标签
处理：分离人声 → 歌词校对 / 对齐 → 按句切片 → 人声与伴奏一起裁

原曲 40–43 秒：“春风吹过河岸”
原曲 43–46 秒：“灯火照亮归帆”
裁 40–46 秒 → 新片段 0–6 秒，歌词只保留这两句
```

```json
{
  "style": "慢速民谣，木吉他，柔和女声",
  "lyrics": "春风吹过河岸\n灯火照亮归帆",
  "segments": [
    {"start": 0, "end": 3, "text": "春风吹过河岸"},
    {"start": 3, "end": 6, "text": "灯火照亮归帆"}
  ],
  "vocal_target": "song_040_046_vocal.wav",
  "accompaniment_target": "song_040_046_accomp.wav"
}
```

这是教学记录格式。**时间戳用来校验与裁切，不代表所有模型都把它直接当输入。** 有的训练混音 token，有的分别训练人声与伴奏 token。

| 看起来能用，实际有错 | 会教坏什么 | 修法 |
|---|---|---|
| 只截第一句的音频，仍挂两句歌词 | 文字和发声对不上 | 同步截歌词 |
| ASR 把“归帆”认成“规范” | 模型学错唱词 | 结合歌词源、听审校正 |
| 标“女声”，实际器乐间奏 | 文字条件对应错声音 | 改成器乐样本，或移除这段 |

例如 LeVo 2 的数据流程包含歌词转写 / 对齐、切片及音乐描述生产。可借鉴这个生产顺序，不必照搬其私有数据规模。[LeVo 2 数据流程](https://arxiv.org/html/2606.30642v1)

## ② 怎么喂、怎么学：仍然可以是“猜下一个”

以 **YuE 的两阶段自回归路线**为例：歌词与风格作为条件，先生成主要音频 token，再补充更细的声学 token；分别表示人声与伴奏，最后解码成波形。[YuE](https://arxiv.org/html/2503.08638v1)

<div class="steps"><div><b>条件</b><strong>歌词 + 风格文字</strong><small>“春风吹过河岸；民谣、女声”</small></div><div><b>训练目标</b><strong>真实唱声 / 伴奏 token</strong><small>由同一段录音编码得到</small></div><div><b>预测与 loss</b><strong>正确 token 17：p=0.1</strong><small>−ln(0.1)=2.303，梯度回传模型</small></div><div><b>推理</b><strong>给新歌词，生成新 token</strong><small>解码出人声与伴奏，再混合</small></div></div>

这里的 `17` 仍是音频编号，**不是“春”的文字 token**。歌词已经作为条件给进去了；训练要学的是对应的发音、音高、时长和伴奏。真实系统对整段目标位置求 loss，具体轨道交错方式随模型而变。

## ③ 评测一个最直接的问题：有没有漏唱？

<div class="lab" id="lyric-lab"><div class="lab-head"><div><h3>参考歌词：春风吹过河岸</h3><p class="micro">模拟转写与对齐结果；每字 0.5 秒只是教学时间轴，没有运行 ASR。</p></div><div class="actions"><button class="primary" id="lyrics-correct">唱全了</button><button id="lyrics-missing">漏唱“过”</button></div></div><div class="lyric-grid" id="lyric-result"></div><div class="math-line" id="lyric-score" aria-live="polite"></div></div>

`CER =（替换字数 + 删除字数 + 插入字数）/ 参考字数`。拿生成歌曲做人声分离 / 转写后与给定歌词比；高 CER 的片段再听一遍，分清“模型唱错”和“ASR 听错”。**字都唱对以后，再评跑调、句子衔接、人声质感。**

**别把两个任务混了：** 歌词成歌可以生成新唱声；[清唱配伴奏](accompaniment.html)要保留输入唱声。两者条件、目标、最后混音方式都不同。
