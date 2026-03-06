require('dotenv').config();
const pino = require('pino');
const log = pino({ level: process.env.LOG_LEVEL || 'info' });
const path = require('path');
const zoho = require('./lib/zohoClient');
const embeddings = require('./lib/embeddings');
const store = require('./lib/vectorStore');
const replyGen = require('./lib/replyGenerator');

async function ingest_history(){
  try{
    log.info('Starting ingest_history');
    const tickets = await zoho.fetchClosedTickets(parseInt(process.env.INGEST_LIMIT||500,10));
    log.info({count: tickets.length}, 'Fetched closed tickets');
    const docs = tickets.map(t=>({
      id: t.id,
      subject: t.subject || '',
      text: (t.subject||'') + '\n' + (t.description||'') + '\n' + (t.resolution||''),
      meta: { requester: t.contact, closed_at: t.modifiedTime }
    }));
    const embedResp = await embeddings.createEmbeddings(docs.map(d=>d.text));
    const items = docs.map((d,i)=>({ id:d.id, text:d.text, vector: embedResp[i], meta:d.meta }));
    store.saveVectors(items);
    log.info('Ingest complete');
  }catch(err){
    log.error(err,'ingest_history failed');
    throw err;
  }
}

async function analyse_support(){
  try{
    log.info('Starting analyse_support');
    const openTickets = await zoho.fetchOpenTickets();
    log.info({count: openTickets.length}, 'Fetched open tickets');
    const results = [];
    for(const t of openTickets){
      const queryText = (t.subject||'') + '\n' + (t.description||'');
      const qVec = await embeddings.createEmbeddings([queryText]);
      const nearest = store.findNearest(qVec[0], 5);
      const context = nearest.map(n=>n.text).join('\n---\n');
      const draft = await replyGen.generateDraftReply(t, context);
      results.push({ ticket_id: t.id, draft });
    }
    return results;
  }catch(err){
    log.error(err,'analyse_support failed');
    throw err;
  }
}

// simple CLI
const cmd = process.argv[2];
(async ()=>{
  if(cmd==='ingest'){
    await ingest_history();
    process.exit(0);
  }else if(cmd==='analyse'){
    const res = await analyse_support();
    console.log(JSON.stringify(res,null,2));
    process.exit(0);
  }else{
    console.log('Usage: node index.js [ingest|analyse]');
    process.exit(1);
  }
})().catch(err=>{ log.error(err); process.exit(2); });
