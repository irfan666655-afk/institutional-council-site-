// w5 viral-format helpers: gold tola bars with fractional fill, and a generic icon set
let _BID=0;
function goldBar(fill,w=110){
  const id="gb"+(_BID++), h=w*0.5;
  const shape=`<path d="M14 50 L28 8 L92 8 L106 50 Z"/>`;
  return `<svg width="${w}" height="${h}" viewBox="0 0 120 58" style="overflow:visible">
    <defs><clipPath id="${id}"><rect x="0" y="0" width="${120*fill}" height="58"/></clipPath></defs>
    <g fill="#1d1d22" stroke="#3a3a42" stroke-width="4" stroke-linejoin="round">${shape}</g>
    <g clip-path="url(#${id})" fill="#d4af37" stroke="#f0cf6a" stroke-width="4" stroke-linejoin="round" style="filter:drop-shadow(0 0 8px rgba(240,207,106,.6))">${shape}</g></svg>`;
}
// n bars (fractional last), laid out in rows of perRow
function barGrid(n,perRow=8,w=100){
  let html="",i=0;
  for(let k=0;k<Math.ceil(n);k++){
    const f=Math.min(1,n-k);
    html+=`<span class="gb" style="display:inline-block;margin:6px 8px;opacity:0">${goldBar(f,w)}</span>`;
    if((k+1)%perRow===0)html+="<br>";
  }
  return html;
}
function showBars(el,t,t0,step){
  if(typeof el==="string")el=$(el);
  [...el.querySelectorAll(".gb")].forEach((b,i)=>{const k=clamp((t-t0-i*step)/.1);b.style.opacity=k;b.style.transform=`translateY(${(1-easeOut(k))*-40}px)`;});
}
const ICON={
 car:`<path d="M20 92 L30 60 Q36 44 56 42 L150 42 Q168 44 178 60 L196 74 Q214 78 214 92 L214 100 L20 100 Z M58 52 L50 72 L104 72 L104 52 Z M114 52 L114 72 L170 72 L156 52 Z"/><circle cx="64" cy="104" r="20"/><circle cx="170" cy="104" r="20"/>`,
 pump:`<path d="M40 130 L40 20 Q40 10 50 10 L120 10 Q130 10 130 20 L130 130 Z M55 28 L115 28 L115 62 L55 62 Z M130 40 L150 40 Q160 40 160 50 L160 108 Q160 118 170 118 Q180 118 180 108 L180 60 L166 44"/><path d="M28 130 L142 130"/>`,
 plane:`<path d="M20 78 L90 70 L130 18 Q138 8 146 12 L128 70 L190 66 L204 46 L216 48 L208 80 L216 112 L204 114 L190 94 L128 90 L146 148 Q138 152 130 142 L90 90 L20 82 Z"/>`
};
function icon(name,w=260,fill=1){
  const id="ic"+(_BID++);
  return `<svg width="${w}" height="${w*0.62}" viewBox="0 0 230 150" style="overflow:visible">
   <defs><clipPath id="${id}"><rect x="0" y="0" width="${230*fill}" height="150"/></clipPath></defs>
   <g fill="none" stroke="#3a3a42" stroke-width="8" stroke-linecap="round" stroke-linejoin="round">${ICON[name]}</g>
   <g clip-path="url(#${id})" fill="none" stroke="#f0cf6a" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" style="filter:drop-shadow(0 0 10px rgba(240,207,106,.7))">${ICON[name]}</g></svg>`;
}
