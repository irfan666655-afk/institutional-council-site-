import json, re, difflib, collections, sys
D=sys.argv[1]; raw=json.load(open(D+'/ocr_raw.json'))
def clean(t):
    t=t.replace('|','I').replace('’',"'").replace('‘',"'").replace('“','"').replace('”','"')
    t=re.sub(r'[^A-Za-z0-9\s.,;:\'"%$()\-–—?!/&+]','',t)
    t=re.sub(r'\s+',' ',t).strip()
    return t
txt=[clean(t) for t in raw]
ok=[len(re.sub(r'[^A-Za-z]','',t))>=6 and sum(c.isalpha() or c==' ' for c in t)/max(1,len(t))>0.8 for t in txt]
cues=[];cur=None
for i,t in enumerate(txt):
    if not ok[i]:
        if cur: cur['gap']+=1
        if cur and cur['gap']>1: cues.append(cur); cur=None
        continue
    if cur and difflib.SequenceMatcher(None,cur['texts'][-1].lower(),t.lower()).ratio()>0.75:
        cur['texts'].append(t); cur['end']=i; cur['gap']=0
    else:
        if cur: cues.append(cur)
        cur={'start':i,'end':i,'texts':[t],'gap':0}
if cur: cues.append(cur)
out=[]
for c in cues:
    best=collections.Counter(c['texts']).most_common()
    top=max(best,key=lambda kv:(kv[1],len(kv[0])))[0]
    out.append({'s':c['start']/2,'e':c['end']/2+0.5,'t':top})
# merge cues separated by tiny gaps with same text
json.dump(out,open(D+'/cues.json','w'),indent=0)
with open(D+'/cues.txt','w') as f:
    for c in out: f.write(f"{c['s']:7.1f} {c['e']:7.1f} {c['t']}\n")
print(len(out))
