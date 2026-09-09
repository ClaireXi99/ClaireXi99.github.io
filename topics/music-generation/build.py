"""Build the compact music data / training / evaluation lab."""
from pathlib import Path
from html import escape
import markdown
import json
ROOT=Path(__file__).resolve().parent
PAGES=[('index','文字 → 纯音乐'),('accompaniment','清唱 → 伴奏'),('lyrics','歌词 → 歌曲'),('midi','MIDI → 音乐'),('evaluation','听 / 看评测'),('models','模型与 JD'),('sources','来源')]
metrics=json.loads((ROOT/'assets/audio-metrics.json').read_text()) if (ROOT/'assets/audio-metrics.json').exists() else {}
for i,(slug,title) in enumerate(PAGES):
    path=ROOT/'content'/f'{slug}.md'
    if not path.exists():continue
    raw=path.read_text()
    for k,v in metrics.items():
        if isinstance(v,(int,float)):
            raw=raw.replace('{{'+k+'}}',f'{v:.1f}').replace('{{'+k+'_percent}}',f'{100*v:.1f}')
    body=markdown.markdown(raw,extensions=['extra','sane_lists'])
    nav=''
    for j,(s,t) in enumerate(PAGES):
        active='aria-current="page"' if s==slug else ''
        nav+=f'<a href="{s}.html" {active}>{t}</a>'
    nxt=PAGES[(i+1)%len(PAGES)]
    html=f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex, nofollow, noarchive"><meta name="description" content="用具体音频、样本、loss 和参数更新理解音乐生成。"><title>{escape(title)} · 音乐生成实验课</title><link rel="icon" href="data:,"><link rel="stylesheet" href="assets/style.css"><script src="assets/lab-math.js" defer></script><script src="assets/app.js" defer></script></head><body data-page="{slug}"><a class="skip" href="#main">跳到正文</a><header class="masthead"><a class="brand" href="index.html">音乐生成<span>实验课</span></a><span class="edition">数据 → 训练 → 推理 → 评测 <small>2026.09.09</small></span></header><nav class="main-nav" aria-label="课程">{nav}</nav><main id="main"><article>{body}</article><details class="notes"><summary>补充我的数据 / 我的例子 <span id="note-status" role="status"></span></summary><label for="note">记录自己的输入、目标、处理办法或一个错误样本。</label><textarea id="note" rows="5" maxlength="200000" placeholder="我的原始数据是……&#10;洗完的一条样本是……&#10;这个问题是怎么验证的……"></textarea><div class="actions"><button id="export-notes">导出笔记 .md</button><button id="backup-notes">备份 .json</button><label class="button" for="import-notes">导入备份</label><input type="file" id="import-notes" accept=".json" hidden><button id="legacy-notes" hidden>导出旧版笔记</button></div><p class="micro">保存在当前浏览器，定期导出。换浏览器或地址前先备份。</p></details><footer><a href="{nxt[0]}.html">接着看：{nxt[1]} →</a><a href="../../#topics">全部学习专题</a><a href="sources.html">论文与数据来源</a></footer></main></body></html>'''
    (ROOT/f'{slug}.html').write_text(html)
for old,target in {'data':'index.html#clean','synthesis':'index.html#train','cases':'accompaniment.html','interview':'index.html'}.items():
    (ROOT/f'{old}.html').write_text(f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url={target}"><title>前往新版</title><a href="{target}">打开新版实验课 →</a></html>')
print('Built compact lab:',', '.join(x[0]+'.html' for x in PAGES))
