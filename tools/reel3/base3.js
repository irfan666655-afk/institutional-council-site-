// Gold Council reel engine v3: everything from v2 plus a beat-synced camera, flashes on cuts,
// shake on hits, film grain, kinetic text and a gold light sweep.
// A page defines: DUR, BPM, CUTS (scene cuts, on bar lines), HITS (big impacts), PULSE ([[a,b]] where the camera pumps on every beat),
// optional SERIES {part, of, title}, and scenes(t, f).
const FPS = 30;
const GLYPHS = "$₨€¥₿%0123456789";
function rnd(n){const x=Math.sin(n*127.1+311.7)*43758.5453;return x-Math.floor(x);}
function clamp(v,a=0,b=1){return Math.max(a,Math.min(b,v));}
function ease(v){v=clamp(v);return v<.5?4*v*v*v:1-Math.pow(-2*v+2,3)/2;}
function easeOut(v){v=clamp(v);return 1-Math.pow(1-v,3);}
function fade(t,a,b,f=.25){return clamp((t-a)/f)*clamp((b-t)/f);}
function type(s,t,start,dur){return s.slice(0,Math.floor(clamp((t-start)/dur)*s.length));}
function gold(text,word){const k=text.indexOf(word);return k<0?text:text.slice(0,k)+`<span style="color:#f0cf6a">${text.slice(k)}</span>`;}
const $=id=>document.getElementById(id);
const on=(t,a,b)=>t>=a&&t<b;

// kinetic pop: element lands with overshoot and a blur that clears
function pop(el,t,t0,dur=.22){
  if(typeof el==="string")el=$(el);
  const k=clamp((t-t0)/dur), e=1+2.2*Math.pow(k-1,3)+1.2*Math.pow(k-1,2);   // back-out
  el.style.opacity=k>0?Math.min(1,k*3):0;
  el.style.transform=`scale(${k>0?1.35-0.35*e:1.35})`;
  el.style.filter=`blur(${(1-k)*10}px)`;
}
// words appear one by one on 16th notes (for lines AFTER the hook; the hook itself must be on screen at frame 0)
function words(el,t,t0,stepSec){
  if(typeof el==="string")el=$(el);
  if(!el._w){el._w=[...el.querySelectorAll(".w")];}
  el._w.forEach((w,i)=>{const k=clamp((t-t0-i*stepSec)/.12);w.style.opacity=k;w.style.transform=`translateY(${(1-easeOut(k))*30}px)`;w.style.display="inline-block";});
}
function W(s){return s.split(" ").map(x=>`<span class="w">${x}</span>`).join(" ");}

function buildChrome(label){
  const st=$("stage");
  const inner=st.innerHTML; st.innerHTML="";
  st.insertAdjacentHTML("afterbegin",`
  <div id="rain"></div>
  <div class="abs" style="inset:0;background:radial-gradient(ellipse 74% 36% at 50% 50%,rgba(5,5,7,.97) 0%,rgba(5,5,7,.72) 60%,rgba(5,5,7,.28) 100%)"></div>
  <div id="cam" class="abs" style="inset:0;transform-origin:50% 52%">${inner}</div>
  <div class="abs" style="inset:0;background:repeating-linear-gradient(0deg,rgba(240,207,106,.035) 0 2px,transparent 2px 6px);pointer-events:none"></div>
  <svg class="abs" id="grain" width="1080" height="1920" style="inset:0;opacity:.07;mix-blend-mode:screen"><filter id="gn"><feTurbulence id="gt" type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="1"/></filter><rect width="100%" height="100%" filter="url(#gn)"/></svg>
  <div id="vig" class="abs" style="inset:0;background:radial-gradient(ellipse 80% 60% at 50% 50%,transparent 55%,rgba(0,0,0,.75) 100%)"></div>
  <div id="flash" class="abs" style="inset:0;background:#f0cf6a;opacity:0;mix-blend-mode:screen"></div>
  <div id="band" class="abs" style="left:0;right:0;height:0;background:rgba(95,211,196,.18)"></div>
  <div class="corner" style="left:40px;top:280px;border-top-width:5px;border-left-width:5px"></div>
  <div class="corner" style="right:40px;top:280px;border-top-width:5px;border-right-width:5px"></div>
  <div class="corner" style="left:40px;bottom:280px;border-bottom-width:5px;border-left-width:5px"></div>
  <div class="corner" style="right:40px;bottom:280px;border-bottom-width:5px;border-right-width:5px"></div>
  <div class="abs mono" style="left:100px;right:100px;top:380px;display:flex;justify-content:space-between;align-items:center;font-size:28px;letter-spacing:.2em;color:#d4af37">
    <span style="display:flex;align-items:center;gap:14px"><span id="rec" style="width:18px;height:18px;border-radius:50%;background:#e05a4f"></span>REC</span>
    <span style="color:#a39d90">THE GOLD COUNCIL</span></div>
  ${typeof SERIES!=="undefined"?seriesBar():""}
  <div class="abs mono" style="left:100px;right:100px;top:1540px;display:flex;justify-content:space-between;font-size:26px;letter-spacing:.14em;color:#8f8a7e"><span>${label}</span><span id="tcv">00:00:00</span></div>`);
  const rain=$("rain");window._cols=[];
  for(let i=0;i<13;i++){
    const d=document.createElement("div");d.className="col";let s="";
    for(let k=0;k<64;k++)s+=GLYPHS[Math.floor(rnd(i*97+k)*GLYPHS.length)];
    d.textContent=s;d.style.left=(20+i*80)+"px";
    d.style.color=i%3===1?"rgba(95,211,196,.12)":"rgba(212,175,55,.17)";
    rain.appendChild(d);_cols.push({el:d,speed:90+rnd(i)*140,off:rnd(i+50)*2400});
  }
}
function seriesBar(){
  let segs="";
  for(let i=1;i<=SERIES.of;i++)segs+=`<div style="flex:1;height:8px;border-radius:4px;background:${i<SERIES.part?"#d4af37":i===SERIES.part?"#f0cf6a":"#2a2a30"};${i===SERIES.part?"box-shadow:0 0 18px rgba(240,207,106,.8)":""}"></div>`;
  return `<div class="abs mono" style="left:100px;right:100px;top:450px;font-size:26px;letter-spacing:.18em;color:#cfc7b6;display:flex;justify-content:space-between"><span>${SERIES.title}</span><span style="color:#f0cf6a">PART ${SERIES.part}/${SERIES.of}</span></div>
  <div class="abs" style="left:100px;right:100px;top:500px;display:flex;gap:10px">${segs}</div>`;
}
function render(t){
  const f=Math.round(t*FPS), beat=60/BPM;
  _cols.forEach(c=>{c.el.style.transform=`translateY(${((t*c.speed+c.off)%2500)-2300}px)`;});
  $("rec").style.opacity=(Math.floor(t*2)%2===0)?1:0.15;
  $("tcv").textContent=`00:${String(Math.floor(t)).padStart(2,"0")}:${String(f%FPS).padStart(2,"0")}`;
  $("gt").setAttribute("seed",String(f%50));
  // camera: slow push-in per scene + pump on beats inside PULSE + shake after HITS
  const edges=[0,...CUTS,DUR]; let a=0,b=DUR; for(let i=0;i<edges.length-1;i++)if(t>=edges[i]&&t<edges[i+1]){a=edges[i];b=edges[i+1];}
  let s=1+0.045*((t-a)/(b-a));
  if(PULSE.some(([p,q])=>t>=p&&t<q)){const ph=(t%beat)/beat;s+=0.028*Math.exp(-ph*7);}
  let sx=0,sy=0;HITS.forEach(h=>{const d=t-h;if(d>=0&&d<.35){const m=(1-d/.35)*22;sx+=(rnd(f*3)-.5)*m;sy+=(rnd(f*5+1)-.5)*m;}});
  $("cam").style.transform=`translate(${sx}px,${sy}px) scale(${s})`;
  // flash on cuts and hits
  let fl=0;[...CUTS,...HITS.filter(h=>h>0.2)].forEach(c=>{const d=t-c;if(d>=0&&d<.18)fl=Math.max(fl,.32*(1-d/.18));});
  $("flash").style.opacity=fl;
  $("vig").style.opacity=PULSE.some(([p,q])=>t>=p&&t<q)?0.85+0.15*Math.exp(-((t%beat)/beat)*6):1;
  // glitch band on cuts
  let g=0;CUTS.forEach(c=>{if(Math.abs(t-c)<0.07)g=1;});
  const band=$("band");
  if(g){band.style.top=(300+rnd(f)*1300)+"px";band.style.height=(20+rnd(f+3)*90)+"px";}else band.style.height="0";
  // gold sweep on .sweep elements
  document.querySelectorAll(".sweep").forEach(el=>{el.style.backgroundPosition=`${(-60+((t*55)%220))}% 0`;});
  scenes(t,f);
}
