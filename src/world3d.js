import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.module.js';
// True perspective scene replacing the old flat battle backdrop while in-game.
// Procedural proxy geometry: not original game models. Replace when asset conversion succeeds.
const host=document.querySelector('.game-shell');
const canvas=document.createElement('canvas');canvas.id='world3d';canvas.setAttribute('aria-label','3D 立體探索場景');host.insertBefore(canvas,document.querySelector('.vignette'));
let renderer;try{renderer=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance'});}catch(e){canvas.remove();console.warn('3D renderer unavailable',e);throw e}
renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.6));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
const scene=new THREE.Scene();scene.background=new THREE.Color(0x9eaf9c);scene.fog=new THREE.FogExp2(0x9eaf9c,.018);
const camera=new THREE.PerspectiveCamera(53,1,.1,230);camera.position.set(0,11,19);
scene.add(new THREE.HemisphereLight(0xe6f4ff,0x3d5035,2.3));
const sun=new THREE.DirectionalLight(0xffdfab,2.6);sun.position.set(-20,35,20);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);sun.shadow.camera.left=-55;sun.shadow.camera.right=55;sun.shadow.camera.top=55;sun.shadow.camera.bottom=-55;scene.add(sun);
const mat=(c,roughness=1)=>new THREE.MeshStandardMaterial({color:c,roughness});
const materials={grass:mat(0x54744a),grass2:mat(0x6e8959),dirt:mat(0x877b5b),stone:mat(0x8c9182),roof:mat(0x435b4d),wood:mat(0x68503b),wall:mat(0xc5b997),bark:mat(0x5c4b35),leaf:mat(0x3e6749),jade:mat(0x6bafa0),gold:mat(0xc6a96a),enemy:mat(0x865e4b),skin:mat(0xd6b89a),cloth:mat(0x4b756b),metal:mat(0xbac4bc),water:new THREE.MeshStandardMaterial({color:0x4c8588,transparent:true,opacity:.78,roughness:.18})};
function mesh(g,m,x=0,y=0,z=0,parent=scene){const o=new THREE.Mesh(g,m);o.position.set(x,y,z);o.castShadow=true;o.receiveShadow=true;parent.add(o);return o}
const box=(x,y,z,w,h,d,m,parent=scene)=>mesh(new THREE.BoxGeometry(w,h,d),m,x,y,z,parent);
const cylinder=(x,y,z,r1,r2,h,m,parent=scene)=>mesh(new THREE.CylinderGeometry(r1,r2,h,8),m,x,y,z,parent);
let terrain=new THREE.Group();scene.add(terrain);
function groundFor(zone){while(terrain.children.length)terrain.remove(terrain.children[0]);const brown=zone>=7, snowy=zone===13;
scene.background.set(snowy?0xc7d7d9:brown?0xb8a18b:0x9eaf9c);scene.fog.color.copy(scene.background);
box(0,-.65,0,150,1.2,150,brown?materials.dirt:materials.grass,terrain);
for(let i=0;i<105;i++){let x=Math.sin(i*67.13)*58,z=Math.cos(i*19.81)*58;
if(Math.abs(x)<5||Math.abs(z)<5)continue;
if(i%5===0){const trunk=cylinder(x,1.5,z,.3,.44,3.1,materials.bark,terrain);trunk.castShadow=true;mesh(new THREE.ConeGeometry(2.3,5.3,7),materials.leaf,x,5.3,z,terrain)}
else{mesh(new THREE.DodecahedronGeometry(.55+(i%4)*.2,0),materials.stone,x,.45,z,terrain)}
}
box(0,.025,0,7,.08,145,materials.dirt,terrain);
box(0,.027,0,145,.07,6,materials.dirt,terrain);
for(let i=-2;i<=2;i++){let z=-i*14-13;let x=i%2?11:-11;box(x,2,z,9,4,7,materials.wall,terrain);const roof=mesh(new THREE.ConeGeometry(7,3,4),materials.roof,x,5.4,z,terrain);roof.rotation.y=Math.PI/4;box(x,1.5,z+3.56,1.4,2.8,.18,materials.wood,terrain)}
for(let j=0;j<6;j++){const x=j*7-17,z=-28;box(x,1,z,1,2,1,materials.stone,terrain);box(x,2.1,z,3,.5,2,materials.stone,terrain)}
if(zone===0||zone===1){box(24,-.1,0,16,.15,130,materials.water,terrain);for(let i=0;i<9;i++)box(16,.15,i*9-35,13,.4,2,materials.wood,terrain)}
}
const player=new THREE.Group();scene.add(player);
function makeHuman(parent,enemy=false){
const body=materials[enemy?'enemy':'cloth'];const head=mesh(new THREE.SphereGeometry(.55,12,9),materials.skin,0,2.85,0,parent);
const hair=mesh(new THREE.SphereGeometry(.57,12,8),enemy?materials.enemy:materials.wood,0,3.08,-.08,parent);hair.scale.y=.43;
box(0,1.9,0,1.2,1.45,.75,body,parent);
const larm=new THREE.Group(),rarm=new THREE.Group(),lleg=new THREE.Group(),rleg=new THREE.Group();
for(const [g,x,y] of [[larm,-.85,2.5],[rarm,.85,2.5],[lleg,-.35,1.15],[rleg,.35,1.15]]){g.position.set(x,y,0);parent.add(g);box(0,-.5,0,g===lleg||g===rleg?.4:.36,1,.38,g===lleg||g===rleg?materials.wood:body,g)}
box(0,1.1,.03,1.05,.35,.65,materials.gold,parent);
const blade=new THREE.Group();rarm.add(blade);blade.position.set(.1,-1.05,.1);box(0,-.5,0,.16,1.35,.17,materials.metal,blade);box(0,.08,0,.65,.12,.2,materials.gold,blade);
return {larm,rarm,lleg,rleg,blade,head}
}
const hero=makeHuman(player);player.position.set(0,0,3);
const foe=new THREE.Group();scene.add(foe);const enemyParts=makeHuman(foe,true);foe.position.set(8,0,-8);foe.scale.setScalar(1.25);
const npc=new THREE.Group();scene.add(npc);makeHuman(npc);npc.position.set(-4,0,-9);npc.rotation.y=.4;
const marker=mesh(new THREE.ConeGeometry(.55,1.3,5),new THREE.MeshBasicMaterial({color:0xffdb71}),-4,5,-9);marker.rotation.x=Math.PI;
const halo=mesh(new THREE.TorusGeometry(.85,.07,6,32),new THREE.MeshBasicMaterial({color:0xffd878}),-4,.1,-9);halo.rotation.x=-Math.PI/2;
const effects=[];const clock=new THREE.Clock();let previousZone=-1,previousAttack=0;
const objective=document.createElement('div');objective.id='objective3d';objective.innerHTML='<b>◆ 主線任務</b><span>前往目標位置</span><small>方向指示僅為示範，任務座標待補</small>';host.append(objective);
function fx(){const flash=mesh(new THREE.RingGeometry(.3,2.1,24),new THREE.MeshBasicMaterial({color:0xe6d39d,transparent:true,opacity:.9,side:THREE.DoubleSide}),player.position.x,1.4,player.position.z-1.4);flash.rotation.y=Math.PI/2;effects.push({mesh:flash,time:.3})}
function update(){
requestAnimationFrame(update);const s=window.SwordBridge?.snapshot();const visible=s?.screen==='ui';canvas.style.display=visible?'block':'none';objective.style.display=visible?'flex':'none';if(!visible)return;
if(previousZone!==s.zone){previousZone=s.zone;groundFor(s.zone)}
const dt=Math.min(clock.getDelta(),.04),time=performance.now()*.001;
const px=(s.position.x-.46)*100,pz=(s.position.y-.64)*100;
const dx=px-player.position.x,dz=pz-player.position.z;player.position.x+=dx*Math.min(1,dt*12);player.position.z+=dz*Math.min(1,dt*12);
if(s.moving){const angle=Math.atan2(dx,dz);if(Math.abs(dx)+Math.abs(dz)>.005)player.rotation.y=angle}
const swing=s.moving?Math.sin(time*12)*.55:Math.sin(time*2)*.035;
hero.lleg.rotation.x=swing;hero.rleg.rotation.x=-swing;hero.larm.rotation.x=-swing*.65;hero.rarm.rotation.x=swing*.65;
if(s.attackAt!==previousAttack){previousAttack=s.attackAt;hero.rarm.rotation.x=-2.2;fx()}
const e=s.enemy;foe.visible=!!e?.alive;
if(e){foe.position.set((e.x-.46)*100,0,(e.y-.64)*100);enemyParts.larm.rotation.x=Math.sin(time*4)*.25;enemyParts.rarm.rotation.x=-Math.sin(time*4)*.25}
marker.position.y=4.6+Math.sin(time*2)*.3;halo.rotation.z=time*.8;
const desired=new THREE.Vector3(player.position.x,11,player.position.z+18);camera.position.lerp(desired,Math.min(1,dt*4.5));camera.lookAt(player.position.x,1.1,player.position.z-4);
const q=s.quests?.find(q=>!q.done);objective.querySelector('span').textContent=q?`${q.name}　${q.progress}/${q.need}`:'探索世界';
for(let i=effects.length-1;i>=0;i--){const f=effects[i];f.time-=dt;f.mesh.scale.multiplyScalar(1+dt*5);f.mesh.material.opacity=Math.max(0,f.time*3);if(f.time<=0){scene.remove(f.mesh);f.mesh.geometry.dispose();f.mesh.material.dispose();effects.splice(i,1)}}
renderer.render(scene,camera)
}
function resize(){const w=host.clientWidth,h=host.clientHeight;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix()}
new ResizeObserver(resize).observe(host);resize();update();
