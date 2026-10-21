/* Mobile controller enhancement: uses existing keyboard/game actions; no autoplay. */
(()=>{
const root=document.createElement('div'); root.id='mobile-controller';
root.innerHTML='<div id="quest-guide"><span>任務方向</span><b>↗</b><small>開啟任務列表查看進度</small></div><div id="joy" aria-label="虛擬移動搖桿"><div id="joy-knob"></div></div><div class="mobile-actions"><button data-key="3" class="skill">技三</button><button data-key="2" class="skill">技二</button><button data-key="1" class="skill">技一</button><button data-key="q" class="basic">攻擊</button><button id="mobile-quest">任務</button><button id="mobile-bag">背包</button></div><button id="mobile-fullscreen">全螢幕</button>';
document.querySelector('.game-shell')?.append(root);
const joy=root.querySelector('#joy'),knob=root.querySelector('#joy-knob'),down=new Set();
const fire=(key,pressed)=>{document.dispatchEvent(new KeyboardEvent(pressed?'keydown':'keyup',{key,bubbles:true}));};
const setKeys=(next)=>{for(const k of [...down])if(!next.has(k)){fire(k,false);down.delete(k)}for(const k of next)if(!down.has(k)){fire(k,true);down.add(k)}};
const release=()=>{setKeys(new Set());knob.style.transform='translate(0,0)'};
let active=null;
joy.addEventListener('pointerdown',e=>{e.preventDefault();active=e.pointerId;joy.setPointerCapture(active);update(e)});
joy.addEventListener('pointermove',e=>{if(e.pointerId===active)update(e)});
['pointerup','pointercancel','lostpointercapture'].forEach(t=>joy.addEventListener(t,e=>{if(e.pointerId===active){active=null;release()}}));
function update(e){const r=joy.getBoundingClientRect(),x=e.clientX-(r.left+r.width/2),y=e.clientY-(r.top+r.height/2),max=r.width*.31,dist=Math.hypot(x,y),factor=Math.min(1,max/(dist||1));knob.style.transform=`translate(${x*factor}px,${y*factor}px)`;const keys=new Set();if(y < -max*.22)keys.add('w');if(y>max*.22)keys.add('s');if(x < -max*.22)keys.add('a');if(x > max*.22)keys.add('d');setKeys(keys)}
root.querySelectorAll('[data-key]').forEach(b=>{
 let timer=null;
 const stop=()=>{if(timer!==null){clearInterval(timer);timer=null}};
 b.addEventListener('pointerdown',e=>{e.preventDefault();b.setPointerCapture(e.pointerId);fire(b.dataset.key,true);stop();if(b.dataset.key==='q')timer=setInterval(()=>fire('q',true),160)});
 for(const ev of ['pointerup','pointercancel','lostpointercapture'])b.addEventListener(ev,stop);
});
root.querySelector('#mobile-quest').addEventListener('click',()=>fire('F3',true));
root.querySelector('#mobile-bag').addEventListener('click',()=>fire('F4',true));
root.querySelector('#mobile-fullscreen').addEventListener('click',()=>{const el=document.documentElement;if(document.fullscreenElement)document.exitFullscreen?.();else el.requestFullscreen?.().catch(()=>{})});
window.addEventListener('blur',release);
document.addEventListener('visibilitychange',()=>{if(document.hidden)release()});
const guide=root.querySelector('#quest-guide');guide.addEventListener('click',()=>fire('F3',true));
})();
