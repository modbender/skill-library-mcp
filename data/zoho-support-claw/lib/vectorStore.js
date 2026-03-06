const fs = require('fs');
const path = require('path');
const pino = require('pino');
const log = pino({ level: process.env.LOG_LEVEL||'info' });
const DATA_FILE = path.join(__dirname,'..','data','embeddings.json');

function ensureFile(){
  const dir = path.dirname(DATA_FILE);
  if(!fs.existsSync(dir)) fs.mkdirSync(dir,{ recursive:true });
  if(!fs.existsSync(DATA_FILE)) fs.writeFileSync(DATA_FILE, JSON.stringify({items:[]},null,2));
}

function saveVectors(items){
  ensureFile();
  const store = JSON.parse(fs.readFileSync(DATA_FILE,'utf8'));
  store.items = store.items.concat(items);
  fs.writeFileSync(DATA_FILE, JSON.stringify(store,null,2));
  log.info({count: items.length}, 'Saved vectors');
}

function load(){ ensureFile(); return JSON.parse(fs.readFileSync(DATA_FILE,'utf8')).items || []; }

function dot(a,b){
  let s=0; for(let i=0;i<a.length;i++) s += (a[i]||0)*(b[i]||0); return s;
}
function norm(a){ let s=0; for(let i=0;i<a.length;i++) s += (a[i]||0)*(a[i]||0); return Math.sqrt(s); }

function similarity(a,b){ return dot(a,b)/(norm(a)*norm(b)+1e-10); }

function findNearest(vec, k=5){
  const items = load();
  const scored = items.map(it=>({score: similarity(vec,it.vector), id:it.id, text: it.text, meta: it.meta}));
  scored.sort((a,b)=>b.score-a.score);
  return scored.slice(0,k);
}

module.exports = { saveVectors, load, findNearest };
