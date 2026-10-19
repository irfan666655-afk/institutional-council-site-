import json, sys, re
D=sys.argv[1]; c=json.load(open(D+'/cues.json'))
drop=[]; out=[]
for x in c:
    t=x['t']
    if x['s'] in (81.5,170.0): continue
    if x['s']==16.5: t='"Paper is a promise. Gold is a weight."'
    if x['s']==922.0: t='"Save in the good years. The hard years come on their own."'
    t=t.replace('lt begins','It begins').replace('ona single','on a single').replace('Al Dividend','AI Dividend')
    out.append({'s':x['s'],'e':x['e'],'t':t})
add=[(178,186,"In America, $100 from 1913 buys $2.95 of goods today."),
(202.5,213.5,"4.76 in 1955. About 11 in 1972. It passed 100 in 2013, and 200 in 2022."),
(214,221.5,"In the crisis of 2023, it touched 300. Today, it is 277."),
(222,229,"Against the dollar, Rs 100 from 1950 is now worth Rs 1.2."),
(233.5,241,"Rs 43 in 1950. Rs 435,720 today."),
(459.5,469,"And every gold standard ended in war or depression: 1797. 1914. 1933. 1971."),
(665,673,"Their answer was Daada's answer: gold. More than 1,000 tonnes a year, from 2022 to 2024."),
(1026,1039.5,"Portugal, Spain, the Dutch, France, Britain: each fell in steps. Sterling fell over sixty years: 1931, 1949, 1967, 1976."),
(1044,1051.5,"Slow erosion: 25%. Managed devaluation: 31%. Debasement: 16%."),
(1136.5,1153.5,"Gold $8,740. Silver $148. Brent $96. Bitcoin $347,000. The S&P 500, 11,565."),
(1158,1165.5,"But in today's money, gold is $5,680, and oil just $63."),
(1203,1217,"By 2036, 99.2% of all bitcoin will exist. And its range is the widest in the atlas: from $63,000 to $774,000."),
(1363,1379,"Gold at or above $5,000 at the end of 2027: 20%. A US recession beginning by the end of 2028: 50%. Gold higher than today at the end of 2036: 83%.")]
for s,e,t in add: out.append({'s':s,'e':e,'t':t})
out.sort(key=lambda x:x['s'])
for a,b in zip(out,out[1:]):
    if a['e']>b['s']: a['e']=b['s']
json.dump(out,open(D+'/cues_fixed.json','w'),indent=0); print(len(out))
