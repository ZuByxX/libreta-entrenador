/* Datos guardados en este dispositivo (IndexedDB). Misma forma que la API de db de la versión anterior. */
(function(){
const DBN='libreta-entrenador',ST='docs';let idb=null,ready=null;const MEM={},L={};
const col=k=>MEM[k]=MEM[k]||new Map();
const emit=k=>(L[k]||[]).forEach(f=>{try{f()}catch(e){console.error(e)}});
const emitAll=()=>Object.keys(L).forEach(emit);
function openDb(){return new Promise((ok,ko)=>{let r;try{r=indexedDB.open(DBN,1)}catch(e){ko(e);return}
  r.onupgradeneeded=()=>r.result.createObjectStore(ST);r.onsuccess=()=>ok(r.result);r.onerror=()=>ko(r.error);r.onblocked=()=>ko(new Error('blocked'))})}
function run(mode,fn){return new Promise((ok,ko)=>{const t=idb.transaction(ST,mode);fn(t.objectStore(ST));
  t.oncomplete=()=>ok();t.onerror=()=>ko(t.error);t.onabort=()=>ko(t.error)})}
function loadAll(){Object.keys(MEM).forEach(k=>delete MEM[k]);return new Promise((ok,ko)=>{const r=idb.transaction(ST,'readonly').objectStore(ST).openCursor();
  r.onsuccess=()=>{const c=r.result;if(!c){ok();return}const k=String(c.key),i=k.indexOf('/');col(k.slice(0,i)).set(k.slice(i+1),c.value);c.continue()};r.onerror=()=>ko(r.error)})}
const wrap=e=>(e&&e.name==='QuotaExceededError')?{code:'quota_exceeded'}:e;
const listen=(k,f)=>{(L[k]=L[k]||[]).push(f);setTimeout(f,0);return()=>{L[k]=L[k].filter(x=>x!==f)}};
const api={
  collection:k=>({onSnapshot(n){return listen(k,()=>n({docs:[...col(k)].map(([id,v])=>({id,data:()=>v})),metadata:{fromCache:false}}))}}),
  doc:p=>{const i=p.indexOf('/'),k=p.slice(0,i),id=p.slice(i+1);return{
    onSnapshot(n){return listen(k,()=>{const v=col(k).get(id);n({id,exists:!!v,data:()=>v,metadata:{fromCache:false}})})},
    async set(v){const d=JSON.parse(JSON.stringify(v));delete d.id;try{await run('readwrite',s=>s.put(d,k+'/'+id))}catch(e){throw wrap(e)}col(k).set(id,d);emit(k)},
    async delete(){await run('readwrite',s=>s.delete(k+'/'+id));col(k).delete(id);emit(k)}}}
};
const BACKUP_APP='libreta-entrenador';
const backup={
  make(){const data={};Object.keys(MEM).forEach(k=>{data[k]=[...MEM[k]].map(([id,v])=>({...v,id}))});return {app:BACKUP_APP,version:1,exportedAt:new Date().toISOString(),data}},
  check(o){return !!(o&&o.app===BACKUP_APP&&o.data&&typeof o.data==='object')},
  async restore(o){await run('readwrite',s=>{s.clear();Object.entries(o.data).forEach(([k,arr])=>{if(!/^[\w-]+$/.test(k)||!Array.isArray(arr))return;
      arr.forEach(d=>{if(!d||d.id==null)return;const {id,...v}=d;s.put(v,k+'/'+String(id))})})});
    await loadAll();emitAll()}
};
const downloads={async save({filename,data}){
  const file=new File([data],filename,{type:data.type||'application/octet-stream'});
  if(navigator.canShare&&navigator.share&&navigator.canShare({files:[file]})){
    try{await navigator.share({files:[file]});return}catch(e){if(e&&e.name==='AbortError')throw {code:'declined'}}}
  const u=URL.createObjectURL(data),a=document.createElement('a');a.href=u;a.download=filename;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),60000)}};
window.LOCAL_BACKUP=backup;
window.LOCAL_CLAUDE={use:async n=>{
  if(n==='db'){if(!ready)ready=(async()=>{if(!window.indexedDB)return null;idb=await openDb();await loadAll();
      try{navigator.storage&&navigator.storage.persist&&navigator.storage.persist()}catch(e){}return api})().catch(e=>{console.error(e);return null});return ready}
  if(n==='downloads')return downloads;
  return null}};
})();
