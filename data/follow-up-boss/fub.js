#!/usr/bin/env node

/**
 * Follow Up Boss CLI
 * Usage: node fub.js <command> [options]
 * 
 * Commands:
 *   me                        - Get current user info
 *   people [query]            - List/search people
 *   person <id>               - Get person details
 *   people create <json>      - Create person via /events (triggers automations)
 *   people update <id> <json> - Update a person
 *   notes <personId>          - Get notes for a person
 *   notes create <json>       - Create a note
 *   tasks [query]             - List tasks
 *   tasks create <json>       - Create a task
 *   tasks complete <id>       - Complete a task
 *   events [query]            - List events
 *   events create <json>      - Create event (for lead intake)
 *   pipelines                 - Get pipelines
 *   deals [query]             - List deals
 *   deals create <json>       - Create a deal
 *   textmessages <personId>   - Get text messages for a person
 *   textmessages create <json> - Log a text (NOT sent - recorded only!)
 *   emails <personId>         - Get emails for a person
 *   emails create <json>      - Log an email (NOT sent - recorded only!)
 *   calls <personId>          - Get calls for a person
 *   calls create <json>      - Log a call
 *   webhooks                  - List webhooks
 *   webhooks create <json>   - Create webhook (owner only)
 *   webhooks delete <id>     - Delete webhook
 *   sources                   - Get lead sources
 *   users                     - Get users/agents
 *   search <query>           - Global search
 * 
 * Examples:
 *   node fub.js people "status=Active&limit=10"
 *   node fub.js person 123
 *   node fub.js events create '{"source":"Website","system":{"name":"John","email":"john@test.com"}}'
 *   node fub.js notes create '{"personId":123,"body":"Called - left voicemail"}'
 *   node fub.js tasks create '{"personId":123,"body":"Follow up","dueDate":"2026-02-20"}'
 *   node fub.js textmessages create '{"personId":123,"body":"Hey!","direction":"outbound"}'
 *   node fub.js calls create '{"personId":123,"direction":"outbound","outcome":"voicemail"}'
 *   node fub.js search "john"
 */

const API_BASE = 'https://api.followupboss.com/v1';
const API_KEY = process.env.FUB_API_KEY || '';
const SYSTEM_KEY = process.env.FUB_SYSTEM_KEY || '';
const SYSTEM_NAME = process.env.FUB_SYSTEM_NAME || '';

function getHeaders() {
  const headers = {
    'Authorization': 'Basic ' + Buffer.from(API_KEY + ':').toString('base64'),
    'Content-Type': 'application/json'
  };
  if (SYSTEM_KEY) headers['X-System-Key'] = SYSTEM_KEY;
  if (SYSTEM_NAME) headers['X-System'] = SYSTEM_NAME;
  return headers;
}

async function request(method, endpoint, body = null) {
  const url = `${API_BASE}/${endpoint}`;
  const options = { method, headers: getHeaders() };
  if (body) options.body = JSON.stringify(body);
  
  const response = await fetch(url, options);
  const data = await response.json();
  
  if (!response.ok) {
    console.error('Error:', response.status, response.statusText);
    console.error(JSON.stringify(data, null, 2));
    process.exit(1);
  }
  return data;
}

const args = process.argv.slice(2);
const command = args[0];

if (!API_KEY) {
  console.error('Error: FUB_API_KEY is required');
  console.error('Set: export FUB_API_KEY="your_key"');
  process.exit(1);
}

async function main() {
  try {
    switch (command) {
      case 'me':
        console.log(JSON.stringify(await request('GET', 'me'), null, 2));
        break;
        
      case 'people':
        if (args[1] === 'create') {
          const d = JSON.parse(args[2] || '{}');
          const evt = await request('POST', 'events', {
            source: d.source || 'API',
            system: { name: d.name, email: d.email, phone: d.phone, ...d }
          });
          console.log('Created:', JSON.stringify(evt, null, 2));
        } else if (args[1] === 'update') {
          const id = args[2];
          const d = JSON.parse(args[3] || '{}');
          console.log(JSON.stringify(await request('PUT', `people/${id}`, d), null, 2));
        } else {
          console.log(JSON.stringify(await request('GET', `people?${args[1] || ''}`), null, 2));
        }
        break;
        
      case 'person':
        console.log(JSON.stringify(await request('GET', `people/${args[1]}`), null, 2));
        break;
        
      case 'notes':
        if (args[1] === 'create') {
          console.log(JSON.stringify(await request('POST', 'notes', JSON.parse(args[2] || '{}')), null, 2));
        } else {
          console.log(JSON.stringify(await request('GET', `people/${args[1]}/notes`), null, 2));
        }
        break;
        
      case 'tasks':
        if (args[1] === 'create') {
          console.log(JSON.stringify(await request('POST', 'tasks', JSON.parse(args[2] || '{}')), null, 2));
        } else if (args[1] === 'complete') {
          console.log(JSON.stringify(await request('PUT', `tasks/${args[2]}`, { status: 'Complete' }), null, 2));
        } else {
          console.log(JSON.stringify(await request('GET', `tasks?${args[1] || ''}`), null, 2));
        }
        break;
        
      case 'events':
        if (args[1] === 'create') {
          console.log(JSON.stringify(await request('POST', 'events', JSON.parse(args[2] || '{}')), null, 2));
        } else {
          console.log(JSON.stringify(await request('GET', `events?${args[1] || ''}`), null, 2));
        }
        break;
        
      case 'pipelines':
        console.log(JSON.stringify(await request('GET', 'pipelines'), null, 2));
        break;
        
      case 'deals':
        if (args[1] === 'create') {
          console.log(JSON.stringify(await request('POST', 'deals', JSON.parse(args[2] || '{}')), null, 2));
        } else {
          console.log(JSON.stringify(await request('GET', `deals?${args[1] || ''}`), null, 2));
        }
        break;
        
      case 'textmessages':
        if (args[1] === 'create') {
          console.log(JSON.stringify(await request('POST', 'textMessages', JSON.parse(args[2] || '{}')), null, 2));
        } else {
          console.log(JSON.stringify(await request('GET', `people/${args[1]}/textMessages`), null, 2));
        }
        break;
        
      case 'emails':
        if (args[1] === 'create') {
          console.log(JSON.stringify(await request('POST', 'emails', JSON.parse(args[2] || '{}')), null, 2));
        } else {
          console.log(JSON.stringify(await request('GET', `people/${args[1]}/emails`), null, 2));
        }
        break;
        
      case 'calls':
        if (args[1] === 'create') {
          console.log(JSON.stringify(await request('POST', 'calls', JSON.parse(args[2] || '{}')), null, 2));
        } else {
          console.log(JSON.stringify(await request('GET', `people/${args[1]}/calls`), null, 2));
        }
        break;
        
      case 'webhooks':
        if (args[1] === 'create') {
          console.log(JSON.stringify(await request('POST', 'webhooks', JSON.parse(args[2] || '{}')), null, 2));
        } else if (args[1] === 'delete') {
          console.log(JSON.stringify(await request('DELETE', `webhooks/${args[2]}`), null, 2));
        } else {
          console.log(JSON.stringify(await request('GET', 'webhooks'), null, 2));
        }
        break;
        
      case 'sources':
        console.log(JSON.stringify(await request('GET', 'sources'), null, 2));
        break;
        
      case 'users':
        console.log(JSON.stringify(await request('GET', 'users'), null, 2));
        break;
        
      case 'search':
        console.log(JSON.stringify(await request('GET', `people/search?query=${encodeURIComponent(args[1] || '')}`), null, 2));
        break;
        
      default:
        console.log('FUB CLI - run with your commands');
    }
  } catch (e) {
    console.error('Error:', e.message);
    process.exit(1);
  }
}

main();
