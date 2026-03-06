const axios = require('axios');
const pino = require('pino');
const log = pino({ level: process.env.LOG_LEVEL||'info' });

const ZOHO_DOMAIN = process.env.ZOHO_DOMAIN || 'desk.zoho.com';
const ZOHO_TOKEN = process.env.ZOHO_TOKEN;
if(!ZOHO_TOKEN) log.warn('ZOHO_TOKEN not set — Zoho API calls will fail');

const client = axios.create({
  baseURL: `https://${ZOHO_DOMAIN}/api/v1`,
  headers: { Authorization: `Zoho-oauthtoken ${ZOHO_TOKEN}` }
});

async function fetchClosedTickets(limit=500){
  try{
    const pageSize = 100;
    let page = 1;
    let collected = [];
    while(collected.length < limit){
      const res = await client.get('/tickets', { params: { status:'Closed', per_page: pageSize, page } });
      const data = res.data && res.data.data ? res.data.data : res.data;
      if(!data || data.length===0) break;
      collected = collected.concat(data);
      if(data.length < pageSize) break;
      page++;
    }
    return collected.slice(0,limit).map(t=>({ id:t.id, subject:t.subject, description:t.description, resolution:t.resolution, contact: t.contact_name || t.requester, modifiedTime:t.modifiedTime }));
  }catch(err){
    log.error({err: err && err.response && err.response.data || err}, 'fetchClosedTickets error');
    throw err;
  }
}

async function fetchOpenTickets(){
  try{
    const res = await client.get('/tickets', { params: { status:'Open', per_page:50 } });
    const data = res.data && res.data.data ? res.data.data : res.data;
    return (data||[]).map(t=>({ id:t.id, subject:t.subject, description:t.description, requester:t.contact_name || t.requester }));
  }catch(err){
    log.error({err: err && err.response && err.response.data || err}, 'fetchOpenTickets error');
    throw err;
  }
}

module.exports = { fetchClosedTickets, fetchOpenTickets };
