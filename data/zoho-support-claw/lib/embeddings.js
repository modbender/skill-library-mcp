const OpenAI = require('openai');
const pino = require('pino');
const log = pino({ level: process.env.LOG_LEVEL||'info' });
const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const EMB_MODEL = process.env.EMBEDDINGS_MODEL || 'text-embedding-3-small';

async function createEmbeddings(texts){
  try{
    const resp = await client.embeddings.create({ model: EMB_MODEL, input: texts });
    return resp.data.map(d=>d.embedding);
  }catch(err){
    log.error({err: err && err.response && err.response.data || err}, 'createEmbeddings error');
    throw err;
  }
}

module.exports = { createEmbeddings };
