import glob, subprocess, sys, re, json
from concurrent.futures import ThreadPoolExecutor
D=sys.argv[1]; fs=sorted(glob.glob(D+'/sub2/*.png'))
def ocr(f):
    r=subprocess.run(['tesseract',f,'-','--psm','6','-l','eng'],capture_output=True,text=True).stdout
    return ' '.join(r.split())
with ThreadPoolExecutor(12) as ex: txt=list(ex.map(ocr,fs))
json.dump(txt,open(D+'/ocr_raw.json','w'))
print(len(txt))
