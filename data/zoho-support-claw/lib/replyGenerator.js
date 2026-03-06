const OpenAI = require('openai');
const pino = require('pino');
const log = pino({ level: process.env.LOG_LEVEL||'info' });
const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const MODEL = process.env.OPENAI_MODEL || 'gpt-4o-mini';

async function generateDraftReply(ticket, context){
  try{
    const system = `You are a helpful support agent. Use the ticket details and the context (similar closed tickets with resolutions) to draft a short professional reply (2-4 sentences) addressing the requester and proposing next steps.`;
    const user = `Ticket subject: ${ticket.subject}\nTicket description: ${ticket.description}\nContext: ${context}\n\nPlease provide a concise draft reply and a one-line summary of the recommended action.`;
    const resp = await client.chat.completions.create({
      model: MODEL,
      messages: [ { role: 'system', content: system }, { role: 'user', content: user } ],
      max_tokens: 400
    });
    const output = resp.choices && resp.choices[0] && resp.choices[0].message && resp.choices[0].message.content;
    return output;
  }catch(err){
    log.error({err: err && err.response && err.response.data || err}, 'generateDraftReply error');
    throw err;
  }
}

module.exports = { generateDraftReply };
