// Shared engine for The Gold Council motion reels: rain, HUD, helpers. Each reel page defines CUTS and scenes(t, f).
const FPS = 30;
const GLYPHS = "$₨€¥₿%0123456789";
function rnd(n){const x=Math.sin(n*127.1+311.7)*43758.5453;return x-Math.floor(x);}
function clamp(v,a=0,b=1){return Math.max(a,Math.min(b,v));}
function ease(v){v=clamp(v);return v<.5?4*v*v*v:1-Math.pow(-2*v+2,3)/2;}
function fade(t,a,b,f=.25){return clamp((t-a)/f)*clamp((b-t)/f);}
function type(s,t,start,dur){return s.slice(0,Math.floor(clamp((t-start)/dur)*s.length));}
function gold(text,word){const k=text.indexOf(word);return k<0?text:text.slice(0,k)+`<span style="color:#f0cf6a">${text.slice(k)}</span>`;}
const $=id=>document.getElementById(id);

function buildChrome(label){
  const st=$("stage");
  st.insertAdjacentHTML("afterbegin",`
  <div id="rain"></div>
  <div class="abs" style="inset:0;background:radial-gradient(ellipse 74% 36% at 50% 50%,rgba(5,5,7,.97) 0%,rgba(5,5,7,.72) 60%,rgba(5,5,7,.28) 100%)"></div>
  <div class="abs" style="inset:0;background:repeating-linear-gradient(0deg,rgba(240,207,106,.035) 0 2px,transparent 2px 6px)"></div>
  <div id="band" class="abs" style="left:0;right:0;height:0;background:rgba(95,211,196,.18)"></div>
  <div class="corner" style="left:40px;top:280px;border-top-width:5px;border-left-width:5px"></div>
  <div class="corner" style="right:40px;top:280px;border-top-width:5px;border-right-width:5px"></div>
  <div class="corner" style="left:40px;bottom:280px;border-bottom-width:5px;border-left-width:5px"></div>
  <div class="corner" style="right:40px;bottom:280px;border-bottom-width:5px;border-right-width:5px"></div>
  <div class="abs mono" style="left:100px;right:100px;top:380px;display:flex;justify-content:space-between;align-items:center;font-size:28px;letter-spacing:.2em;color:#d4af37">
    <span style="display:flex;align-items:center;gap:14px"><span id="rec" style="width:18px;height:18px;border-radius:50%;background:#e05a4f"></span>REC</span>
    <span style="color:#a39d90">THE GOLD COUNCIL</span></div>
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
function render(t){
  const f=Math.round(t*FPS);
  _cols.forEach(c=>{c.el.style.transform=`translateY(${((t*c.speed+c.off)%2500)-2300}px)`;});
  $("rec").style.opacity=(Math.floor(t*2)%2===0)?1:0.15;
  $("tcv").textContent=`00:${String(Math.floor(t)).padStart(2,"0")}:${String(f%FPS).padStart(2,"0")}`;
  let g=0;CUTS.forEach(c=>{if(Math.abs(t-c)<0.07)g=1;});
  const band=$("band");
  if(g){band.style.top=(300+rnd(f)*1300)+"px";band.style.height=(20+rnd(f+3)*90)+"px";$("stage").style.transform=`translateX(${(rnd(f+7)-.5)*24}px)`;}
  else{band.style.height="0";$("stage").style.transform="none";}
  scenes(t,f);
}
