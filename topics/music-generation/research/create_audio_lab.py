"""Deterministic synthetic sounds and measured plots; no generative music model is used."""
from pathlib import Path
import json
import numpy as np
from scipy import signal
from scipy.io import wavfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

ROOT=Path(__file__).resolve().parent.parent
AUDIO=ROOT/'assets/audio';PLOTS=ROOT/'assets/plots'
AUDIO.mkdir(parents=True,exist_ok=True);PLOTS.mkdir(parents=True,exist_ok=True)
SR=32000;N=SR*8;rng=np.random.default_rng(909)
BLUE='#315df4';RED='#d45340';INK='#243149';GRID='#e5e9f1'
font_path=Path('/System/Library/Fonts/PingFang.ttc')
if font_path.exists():
 fp=FontProperties(fname=str(font_path));plt.rcParams['font.family']=fp.get_name()
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#c8d0df','axes.labelcolor':INK,'text.color':INK,'xtick.color':INK,'ytick.color':INK,'svg.fonttype':'none','figure.facecolor':'white','axes.facecolor':'white'})
def hz(m):return 440*2**((m-69)/12)
def add(a,b,start):
 i=round(start*SR);lo=max(0,i);hi=min(len(a),i+len(b))
 if hi>lo:a[lo:hi]+=b[lo-i:hi-i]
def pluck(m,duration=1.2):
 t=np.arange(round(duration*SR))/SR
 env=(1-np.exp(-t*150))*np.exp(-t*4)
 return env*sum(np.sin(2*np.pi*hz(m)*k*t)*np.exp(-t*k*.65)/k**1.6 for k in range(1,9))
def accompaniment(shift=0):
 keys=np.zeros(N);bass=np.zeros(N);drums=np.zeros(N)
 chords=[[48,52,55],[45,48,52],[41,45,48],[43,47,50]]
 for bar,chord in enumerate(chords):
  for j in range(8):add(keys,.12*pluck(chord[j%3]+12+shift),bar*2+j*.25)
  for j in range(4):add(bass,.20*pluck(chord[0]-12+shift,.5),bar*2+j*.5)
 for beat in range(16):
  t=np.arange(int(.22*SR))/SR
  kick=np.sin(2*np.pi*(48*t+12*(1-np.exp(-t*18))/18))*np.exp(-t*28)
  add(drums,kick*.24,beat*.5)
 for eighth in range(32):
  t=np.arange(int(.075*SR))/SR
  noise=rng.standard_normal(len(t));noise=signal.sosfilt(signal.butter(3,5000,fs=SR,btype='high',output='sos'),noise)
  add(drums,.05*noise*np.exp(-t*60),eighth*.25)
 return keys,bass,drums
keys,bass,drums=accompaniment();accomp=keys+bass+drums
melody=[60,62,64,67,64,62,60,60,65,67,69,67,64,62,60,60]
vocal=np.zeros(N)
for i,m in enumerate(melody):
 t=np.arange(SR//2)/SR;f=hz(m)*(1+.008*np.sin(2*np.pi*5*t))
 phase=2*np.pi*np.cumsum(f)/SR
 env=(1-np.exp(-t*55))*(1-np.exp(-(0.5-t)*45))
 harmonics=np.zeros(len(t))
 for k in range(1,13):
  weight=(.8*np.exp(-((hz(m)*k-600)/380)**2)+.2*np.exp(-((hz(m)*k-1450)/500)**2))/k**.65
  harmonics+=weight*np.sin(k*phase)
 add(vocal,.38*harmonics*env,i*.5)
fade=np.ones(N);fade[-1600:]=np.linspace(1,0,1600)
for a in [keys,bass,drums,accomp,vocal]:a*=fade
scale=.78/max(np.max(np.abs(accomp+vocal)),np.max(np.abs(accomp)))
keys*=scale;bass*=scale;drums*=scale;accomp*=scale;vocal*=scale
mix=accomp+vocal
clipped=np.clip(accomp*6,-1,1)
lowpass=.1*accomp+.9*signal.sosfiltfilt(signal.butter(6,2000,fs=SR,output='sos'),accomp)
delay=SR//4;late=np.r_[np.zeros(delay),accomp[:-delay]]
leak=accomp+.35*vocal
k2,b2,d2=accompaniment(1);shifted=(k2+b2+drums/scale)*scale*fade
wrong_key=vocal+shifted
def rms(x):return float(np.sqrt(np.mean(x*x)))
def write(name,x,sr=SR):
 wavfile.write(AUDIO/f'{name}.wav',sr,(np.clip(x,-.9999,.9999)*32767).astype(np.int16))
def pair_write(name,a,b):
 target=min(rms(a),rms(b),.13)
 write(name+'-good',a*target/rms(a));write(name+'-bad',b*target/rms(b))
for n,a in [('instrumental',accomp),('vocal',vocal),('keys',keys),('bass',bass),('drums',drums),('mixture',mix)]:write(n,a)
write('vocal-24k',signal.resample_poly(vocal,3,4),24000)
write('accompaniment-24k',signal.resample_poly(accomp,3,4),24000)
raw=np.pad(accomp,(SR,SR));raw48=signal.resample_poly(raw,3,2)
write('raw-10s-stereo',np.column_stack([raw48,raw48]),48000)
_,raw_pcm=wavfile.read(AUDIO/'raw-10s-stereo.wav')
clean=signal.resample_poly(raw_pcm[48000:432000].astype(float).mean(axis=1)/32767,2,3)
write('clean-8s-mono',clean)
for n,a,b in [('clip',accomp,clipped),('band',accomp,lowpass),('timing',mix,vocal+late),('leak',accomp,leak),('key',mix,wrong_key)]:pair_write(n,a,b)
def finish(fig,name):
 fig.tight_layout(pad=1.5);fig.savefig(PLOTS/(name+'.svg'),bbox_inches='tight');fig.savefig(PLOTS/(name+'.png'),dpi=140,bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(figsize=(11,2.1));t=np.arange(len(raw))/SR
ax.plot(t[::120],raw[::120],lw=.8,color=BLUE);ax.axvspan(1,9,color=BLUE,alpha=.08)
ax.axvline(1,color=BLUE,ls='--');ax.axvline(9,color=BLUE,ls='--');ax.text(5,.66,'KEEP 1.0–9.0 s',ha='center',color=BLUE)
ax.text(.5,.45,'CUT',ha='center',fontsize=9);ax.text(9.5,.45,'CUT',ha='center',fontsize=9)
ax.set(xlim=(0,10),ylim=(-.8,.8),xlabel='Time (s)',ylabel='Amplitude');finish(fig,'crop')
center=int(np.argmax(np.abs(accomp)));start=max(0,center-400);end=start+800
fig,axes=plt.subplots(2,1,figsize=(10,3.8),sharex=True)
for ax,a,c,title in zip(axes,[accomp,clipped],[BLUE,RED],['Original — peaks preserved','Clipped — flat tops / bottoms']):
 ax.plot(np.arange(start,end)/SR*1000,a[start:end],color=c,lw=1.2);ax.set(ylim=(-1.15,1.15),ylabel='Amplitude',title=title);ax.grid(alpha=.3)
axes[-1].set_xlabel('Time (ms)');finish(fig,'clipping')
f,pg=signal.welch(accomp,SR,nperseg=2048);_,pb=signal.welch(lowpass,SR,nperseg=2048)
fig,ax=plt.subplots(figsize=(10,3.5));floor=1e-13
ax.plot(f/1000,10*np.log10(pg+floor),color=BLUE,label='Original');ax.plot(f/1000,10*np.log10(pb+floor),color=RED,label='High band attenuated')
ax.axvspan(6,10,color=RED,alpha=.07);ax.set(xlim=(0,12),ylim=(-130,-20),xlabel='Frequency (kHz)',ylabel='Power spectral density (dB/Hz)');ax.legend(frameon=False);ax.grid(alpha=.2);finish(fig,'bandwidth')
fig,ax=plt.subplots(figsize=(10,2.8))
for y,ticks,c,label in [(2,np.arange(8)*.5,INK,'Vocal / target beat'),(1,np.arange(8)*.5,BLUE,'Aligned accompaniment'),(0,np.arange(8)*.5+.25,RED,'Late by 250 ms')]:
 ax.hlines(y,0,4,color=GRID);ax.vlines(ticks,y-.18,y+.18,color=c,lw=3)
ax.set(yticks=[0,1,2],yticklabels=['+250 ms','0 ms','Beat grid'],xlabel='Time (s)',xlim=(-.1,4));ax.set_ylim(-.5,2.6);finish(fig,'timing')
fig,axes=plt.subplots(2,1,figsize=(10,4),sharex=True,sharey=True)
for ax,a,title in zip(axes,[accomp,leak],['Accompaniment only','Accompaniment + 0.35 × vocal']):
 f,ts,z=signal.stft(a,SR,nperseg=1024,noverlap=768)
 ax.pcolormesh(ts,f,20*np.log10(np.abs(z)+1e-7),cmap='magma',vmin=-75,vmax=-20,shading='auto',rasterized=True)
 ax.set(ylim=(150,1800),ylabel='Hz',title=title)
axes[-1].set_xlabel('Time (s)');finish(fig,'leakage')
fig,ax=plt.subplots(figsize=(10,2.5))
for i,m in enumerate(melody):ax.hlines(m,i*.5,i*.5+.44,color=BLUE,lw=5)
ax.set(xlim=(0,8),ylim=(58,71),yticks=[60,62,64,65,67,69],yticklabels=['C4','D4','E4','F4','G4','A4'],xlabel='Time (s)',ylabel='Melody');ax.grid(axis='x',alpha=.2);finish(fig,'melody')
fig,ax=plt.subplots(figsize=(10,2.5))
for x,c,label in [(hz(60),BLUE,'C4 = 261.6 Hz'),(hz(61),RED,'C#4 = 277.2 Hz')]:
 ax.vlines(x,0,1,color=c,lw=5);ax.text(x,1.07,label,ha='center',color=c,fontsize=11)
ax.set(xlim=(240,300),ylim=(0,1.3),xlabel='Frequency (Hz)',yticks=[]);finish(fig,'pitch')
metrics={'illustrative_only':True,'audio_source':'deterministic procedural synthesis; no model outputs','sr':SR,'duration_s':8,'raw':{'sr':48000,'channels':2,'duration_s':10,'shape':[2,480000]},'clean':{'sr':32000,'channels':1,'duration_s':8,'shape':[1,256000]},'clip_ratio_good':float(np.mean(np.abs(accomp)>=.9999)),'clip_ratio_bad':float(np.mean(np.abs(accomp*6)>=1)),'band_6_10k_drop_db':float(10*np.log10(np.sum(pg[(f>=6000)&(f<=10000)])/(np.sum(pb[(f>=6000)&(f<=10000)])+1e-30))) if len(f)==len(pg) else 0,'known_delay_ms':250,'known_vocal_amplitude_gain':.35,'pair_rms':'playback pairs RMS-matched; plots use pre-match signal'}
# STFT reused f above; compute the band measurement with the matching Welch frequencies.
fw,_=signal.welch(accomp,SR,nperseg=2048);mask=(fw>=6000)&(fw<=10000)
metrics['band_6_10k_drop_db']=float(10*np.log10(np.sum(pg[mask])/max(np.sum(pb[mask]),1e-30)))
(ROOT/'assets/audio-metrics.json').write_text(json.dumps(metrics,indent=2))
print(json.dumps(metrics,indent=2))
