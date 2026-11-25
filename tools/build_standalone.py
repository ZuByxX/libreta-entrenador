import os, shutil, re
SP=os.path.dirname(os.path.abspath(__file__))
SRC=os.path.join(os.path.dirname(os.path.abspath(__file__)),'gym.html')
OUT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(OUT,exist_ok=True)
s=open(SRC).read()
def rep(a,b,n=1):
    global s
    c=s.count(a); assert c==n,(a[:90],c); s=s.replace(a,b)

# cabecera: PWA
rep('<meta name="claude:viewport-fit-sides" content="cover">\n','')
rep('<meta name="apple-mobile-web-app-title" content="Gym">',
 '<meta name="apple-mobile-web-app-title" content="Libreta">\n<meta name="apple-mobile-web-app-status-bar-style" content="default">\n<meta name="theme-color" media="(prefers-color-scheme: light)" content="#f2f4f7">\n<meta name="theme-color" media="(prefers-color-scheme: dark)" content="#0e1218">\n<link rel="manifest" href="manifest.webmanifest">\n<link rel="apple-touch-icon" href="icon-180.png">\n<link rel="icon" href="icon-192.png">')

# capa de datos local
i=s.index('<script>\nconst ICON')
s=s[:i]+'<script>\n'+open(SP+'/local_store.js').read()+'</script>\n'+s[i:]
head,body=s[:i],s[i:]
body=body.replace('window.claude','window.LOCAL_CLAUDE')
s=head+body

rep("<h2>No se pueden abrir los datos</h2><p>Abre esta página desde claude.ai con tu cuenta iniciada.</p>",
    "<h2>No se pueden guardar datos aquí</h2><p>Abre la app desde Safari normal (no en navegación privada) o desde el icono de la pantalla de inicio.</p>")
rep("sc.src='https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js'","sc.src='xlsx.full.min.js'")
rep("say('Listo. Busca el archivo «'+fname+'» en Descargas (en el iPhone, en la app Archivos).');",
    "say('Listo. Si te sale el menú de compartir, elige «Guardar en Archivos» o envíatelo por correo.');")
rep("case 'confirm-yes':{a.disabled=true;a.textContent='Eliminando…';","case 'confirm-yes':{a.disabled=true;a.textContent=a.dataset.busy||'Un momento…';")
rep("""data-act="confirm-yes">${esc(okLabel)}</button>""","""data-act="confirm-yes" data-busy="${okLabel.startsWith('Sí, eliminar')?'Eliminando…':'Un momento…'}">${esc(okLabel)}</button>""")

# nombre del icono = nombre de la app
rep("CFG=snap.exists?snap.data():null;","CFG=snap.exists?snap.data():null;syncName();")

# ajustes
rep("""   <div class="help"><b>Copia de seguridad</b><p class="small">Descarga todos tus datos en un archivo Excel: ${wp()}, entrenamientos, rutinas, calendario y medidas. Puedes abrirlo en Excel o Numbers.</p>
   <button type="button" class="btn btn-primary btn-big" data-act="export-xlsx" id="export-btn">Descargar datos en Excel</button><p class="small" id="export-msg" hidden></p></div>`,closeSheet,{saveLabel:'Cerrar',info:true});""",
"""   <div class="help"><b>Copia de seguridad</b><p class="small">Tus datos se guardan solo en este móvil. Si cambias de móvil o borras la app, se pierden. Guarda una copia de vez en cuando en iCloud Drive o envíatela por correo.</p>
   <p class="small muted">Última copia: ${lastBackupText()}</p>
   <button type="button" class="btn btn-primary btn-big" data-act="backup-save" id="backup-btn">Guardar copia de seguridad</button>
   <label class="btn btn-big" for="backup-in" style="cursor:pointer">Recuperar una copia</label><input type="file" id="backup-in" accept=".json,application/json,text/plain" hidden>
   <p class="small" id="backup-msg" hidden></p></div>
   <div class="help"><b>Ver los datos en Excel</b><p class="small">Descarga ${wp()}, entrenamientos, rutinas, calendario y medidas en un Excel para verlos o imprimirlos. Para cambiar de móvil usa la copia de seguridad de arriba.</p>
   <button type="button" class="btn btn-big" data-act="export-xlsx" id="export-btn">Descargar datos en Excel</button><p class="small" id="export-msg" hidden></p></div>`,closeSheet,{saveLabel:'Cerrar',info:true});
  loadXLSX().catch(()=>{});""")

rep("/* foto del alumno */",r"""/* copia de seguridad local */
const LB_KEY='libreta-ultima-copia';
const lsGet=k=>{try{return localStorage.getItem(k)}catch(e){return null}};
const lsSet=(k,v)=>{try{localStorage.setItem(k,v)}catch(e){}};
function lastBackupText(){const v=lsGet(LB_KEY);return v?fmtDate(v.slice(0,10),{day:'numeric',month:'long',year:'numeric'}):'nunca'}
function backupNag(){
  if(!(S.clients.length||S.sessions.length))return '';
  const v=lsGet(LB_KEY);const d=v?daysSince(v.slice(0,10)):null;
  if(v&&d<14)return '';
  if(!v&&S.sessions.length<3)return '';
  return `<div class="section"><div class="help"><b>${v?'Hace '+d+' días que no guardas una copia':'Aún no has guardado ninguna copia'}</b><p class="small">Tus datos están solo en este móvil. Guarda una copia para no perderlos si lo cambias.</p><button type="button" class="btn btn-primary btn-big" data-act="backup-save">Guardar copia ahora</button></div></div>`;
}
function syncName(){const n=(CFG&&CFG.appName)||'Libreta del Entrenador';document.title=n;const m=document.querySelector('meta[name="apple-mobile-web-app-title"]');if(m)m.content=n.length>14?n.slice(0,14):n}
async function backupSave(btn){
  const msg=document.getElementById('backup-msg');const say=t=>{if(msg){msg.hidden=false;msg.textContent=t}else toast(t)};
  try{
    const o=window.LOCAL_BACKUP.make();
    const fname=`Copia ${(CFG&&CFG.appName||'Libreta').replace(/[^\wÀ-ÿ -]/g,'').trim()||'Libreta'} ${today()}.json`;
    const dl=await window.LOCAL_CLAUDE.use('downloads');
    await dl.save({filename:fname,data:new Blob([JSON.stringify(o)],{type:'application/json'})});
    lsSet(LB_KEY,new Date().toISOString());
    say('Copia guardada. Si te sale el menú de compartir, elige «Guardar en Archivos» (mejor en iCloud Drive) o envíatela por correo.');
    if(!msg)render();
  }catch(e){say(e&&e.code==='declined'?'No se ha guardado la copia.':'No se pudo guardar la copia. Inténtalo otra vez.')}
}
async function backupLoad(input){
  const f=input.files&&input.files[0];input.value='';if(!f)return;
  const msg=document.getElementById('backup-msg')||document.getElementById('w-backup-msg');const say=t=>{if(msg){msg.hidden=false;msg.textContent=t}else toast(t)};
  let o;try{o=JSON.parse(await f.text())}catch(e){say('Ese archivo no es una copia de la app. Elige el archivo que empieza por «Copia».');return}
  if(!window.LOCAL_BACKUP.check(o)){say('Ese archivo no es una copia de la app. Elige el archivo que empieza por «Copia».');return}
  const n=k=>(o.data[k]||[]).length;
  const when=o.exportedAt?fmtDate(o.exportedAt.slice(0,10),{day:'numeric',month:'long',year:'numeric'}):'';
  askConfirm('¿Recuperar esta copia?',`Copia${when?' del '+when:''}: ${n('clients')} ${n('clients')===1?ws():wp()}, ${n('sessions')} ${n('sessions')===1?'entrenamiento':'entrenamientos'} y ${n('routines')} ${n('routines')===1?'rutina':'rutinas'}. Se sustituirá todo lo que hay ahora en este móvil.`,'Sí, recuperar',async()=>{
    try{await window.LOCAL_BACKUP.restore(o);lsSet(LB_KEY,o.exportedAt||new Date().toISOString());closeConfirm();closeSheet();wiz=null;go('inicio');render();toast('Copia recuperada')}
    catch(e){closeConfirm();say(e&&e.code==='quota_exceeded'?'No hay espacio suficiente en el móvil.':'No se pudo recuperar la copia.')}});
}

/* foto del alumno */""")
rep("    case 'export-xlsx':exportXlsx(a);break;","    case 'export-xlsx':exportXlsx(a);break;\n    case 'backup-save':backupSave(a);break;")
rep("document.addEventListener('change',async e=>{","document.addEventListener('change',async e=>{\n  if(e.target.id==='backup-in'||e.target.id==='w-backup-in'){backupLoad(e.target);return}")
rep("  ${todayPlans()}\n","  ${backupNag()}${todayPlans()}\n")

# asistente: recuperar copia al cambiar de móvil
rep("""body=`<input id="w-name" value="${esc(d.trainerName)}" placeholder="Tu nombre" autocomplete="given-name">`}""",
    """body=`<input id="w-name" value="${esc(d.trainerName)}" placeholder="Tu nombre" autocomplete="given-name">${edit?'':`<div class="help" style="margin-top:24px"><b>¿Vienes de otro móvil?</b><p class="small">Si guardaste una copia de seguridad, recupérala aquí y lo tendrás todo como antes.</p><label class="btn btn-big" for="w-backup-in" style="cursor:pointer">Recuperar una copia</label><input type="file" id="w-backup-in" accept=".json,application/json,text/plain" hidden><p class="small" id="w-backup-msg" hidden></p></div>`}`}""")

# registro del service worker
assert s.count('</style>')==1
j=s.index('</style>')+len('</style>')
s=('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
   +s[:j]+'\n</head>\n<body>'+s[j:]
   +"\n<script>if('serviceWorker' in navigator&&window.isSecureContext)addEventListener('load',()=>navigator.serviceWorker.register('sw.js').catch(()=>{}));</script>\n</body>\n</html>\n")
open(OUT+'/index.html','w').write(s)
assert os.path.exists(OUT+'/xlsx.full.min.js'), 'falta xlsx.full.min.js (SheetJS 0.18.5) en standalone/'
print('ok',len(s))

import json, hashlib
open(OUT+'/manifest.webmanifest','w').write(json.dumps({"name":"Libreta del Entrenador","short_name":"Libreta","lang":"es","start_url":"./","scope":"./","display":"standalone","background_color":"#f2f4f7","theme_color":"#2343d0",
 "icons":[{"src":"icon-192.png","sizes":"192x192","type":"image/png"},{"src":"icon-512.png","sizes":"512x512","type":"image/png"},{"src":"icon-512.png","sizes":"512x512","type":"image/png","purpose":"maskable"}]},ensure_ascii=False,indent=1))
ver=hashlib.sha1(open(OUT+'/index.html','rb').read()).hexdigest()[:10]
open(OUT+'/sw.js','w').write("""// Guarda la app en el móvil para que abra sin internet. Los datos NO pasan por aquí (están en IndexedDB).
const V='libreta-%s';
const CORE=['./','index.html','manifest.webmanifest','icon-180.png','icon-192.png','icon-512.png','xlsx.full.min.js'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==V).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{
  const r=e.request;if(r.method!=='GET')return;
  if(r.mode==='navigate'){e.respondWith(fetch(r).then(res=>{const cp=res.clone();caches.open(V).then(c=>c.put('index.html',cp));return res}).catch(()=>caches.match('index.html')));return}
  e.respondWith(caches.match(r).then(hit=>hit||fetch(r).then(res=>{if(res.ok||res.type==='opaque'){const cp=res.clone();caches.open(V).then(c=>c.put(r,cp))}return res})));
});
""" % ver)
from PIL import Image, ImageDraw
def icon(sz):
    im=Image.new('RGB',(sz,sz),'#2343d0');d=ImageDraw.Draw(im);k=sz/180
    R=lambda x0,y0,x1,y1,r: d.rounded_rectangle([x0*k,y0*k,x1*k,y1*k],radius=r*k,fill='white')
    R(40,86,140,94,3)            # barra
    R(52,62,64,118,4); R(116,62,128,118,4)   # discos grandes
    R(38,72,48,108,4); R(132,72,142,108,4)   # discos pequeños
    return im
for sz in (180,192,512): icon(sz).save(f'{OUT}/icon-{sz}.png')
print('pwa ok',ver)
