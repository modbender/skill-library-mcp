#!/usr/bin/env node

const WebSocket = require('ws');

const WS_URL = process.env.NOTNATIVE_WS_URL || 'ws://127.0.0.1:8788';

let ws = null;
let idCounter = 1;
const pendingRequests = new Map();

function sendRequest(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = idCounter++;

    pendingRequests.set(id, { resolve, reject });

    ws.send(JSON.stringify({
      jsonrpc: '2.0',
      id,
      method,
      params
    }));

    setTimeout(() => {
      if (pendingRequests.has(id)) {
        pendingRequests.delete(id);
        reject(new Error(`Request timeout: ${method}`));
      }
    }, 10000);
  });
}

async function initialize() {
  const result = await sendRequest('initialize', {
    protocolVersion: '2024-11-05',
    capabilities: {},
    clientInfo: {
      name: 'notnative-skill',
      version: '1.0.0'
    }
  });
  return result;
}

async function callTool(name, args = {}) {
  const result = await sendRequest('tools/call', {
    name,
    arguments: args
  });
  return result;
}

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command) {
    console.error('Usage: mcp-client.js <command> [args...]');
    console.error('');
    console.error('Note Commands:');
    console.error('  search <query>           - Search notes');
    console.error('  semantic <query>         - Semantic search');
    console.error('  read <name>              - Read a note');
    console.error('  active                  - Get active note');
    console.error('  create <content> <name> <folder> - Create note');
    console.error('  append <content> [name]  - Append to note');
    console.error('  update <name> <content>  - Update note');
    console.error('  list-notes [folder]      - List notes');
    console.error('  list-folders            - List folders');
    console.error('  list-tags               - List tags');
    console.error('');
    console.error('Memory Commands:');
    console.error('  store <content>         - Store in memory');
    console.error('  recall <query>          - Search memories');
    console.error('  forget <query>          - Delete memories');
    console.error('  profile                 - Get profile');
    console.error('  profile-update <k:v>    - Update profile');
    console.error('');
    console.error('Other Commands:');
    console.error('  tasks                   - List tasks');
    console.error('  events                  - Get calendar events');
    console.error('  stats                   - Workspace stats');
    console.error('  docs <query>            - Get docs');
    console.error('  run-python <code>       - Execute Python');
    console.error('  list                    - List all tools');
    process.exit(1);
  }

  ws = new WebSocket(WS_URL);

  ws.on('open', async () => {
    try {
      await initialize();

      switch (command) {
        // ========== NOTE COMMANDS ==========
        case 'search': {
          const query = args[1];
          const limit = args[2] ? parseInt(args[2]) : 10;
          const result = await callTool('search_notes', { query, limit });
          console.log(JSON.stringify(result, null, 2));
          break;
        }

        case 'semantic': {
          const query = args[1];
          const limit = args[2] ? parseInt(args[2]) : 10;
          const result = await callTool('semantic_search', { query, limit });
          console.log(JSON.stringify(result, null, 2));
          break;
        }

        case 'read': {
          const name = args[1];
          const result = await callTool('read_note', { name });
          console.log(JSON.stringify(result, null, 2));
          break;
        }

        case 'active': {
          const result = await callTool('get_active_note', {});
          console.log(JSON.stringify(result, null, 2));
          break;
        }

        case 'create': {
          const content = args[1];
          const name = args[2];
          const folder = args[3];
          const result = await callTool('create_note', { content, name, folder });
          console.log(JSON.stringify(result, null, 2));
          break;
        }

        case 'append': {
          const content = args[1];
          const name = args[2];
          const result = await callTool('append_to_note', { content, name });
          console.log(JSON.stringify(result, null, 2));
          break;
        }

        case 'update': {
          const name = args[1];
          const content = args.slice(2).join(' ');
          const result = await callTool('update_note', { name, content });
          console.log(JSON.stringify(result, null, 2));
          break;
        }

        case 'list-notes': {
          const folder = args[1];
          const limit = args[2] ? parseInt(args[2]) : undefined;
          const result = await callTool('list_notes', { folder, limit });
          console.log(JSON.stringify(result, null, 2));
          break;
        }

        case 'list-folders': {
          const result = await callTool('list_folders', {});
          console.log(JSON.stringify(result, null, 2));
          break;
        }

        case 'list-tags': {
          const result = await callTool('list_tags', {});
          console.log(JSON.stringify(result, null, 2));
          break;
        }

        // ========== MEMORY COMMANDS ==========
        case 'store':
        case 'remember': {
          const content = args.slice(1).join(' ');
          const result = await callTool('memory_store', { content });
          console.log(JSON.stringify(result, null, 2));
          break;
        }

        case 'search':
        case 'recall': {
          const query = args.slice(1).join(' ');
          const limit = 5;
          const result = await callTool('memory_search', { query, limit });
          console.log(JSON.stringify(result, null, 2));
          break;
        }

        case 'forget': {
          const query = args.slice(1).join(' ');
          const result = await callTool('memory_forget', { query });
          console.log(JSON.stringify(result, null, 2));
          break;
        }

        case 'profile': {
          const action = args[1];
          if (action === 'update') {
            const keyValue = args.slice(2).join(' ');
            const idx = keyValue.indexOf(':');
            if (idx === -1) {
              console.error('Error: Use format key:value');
              process.exit(1);
            }
            const key = keyValue.substring(0, idx);
            const value = keyValue.substring(idx + 1);
            const data = { [key]: value };
            const result = await callTool('memory_profile', { action: 'update', data });
            console.log(JSON.stringify(result, null, 2));
          } else {
            const result = await callTool('memory_profile', { action: 'get' });
            console.log(JSON.stringify(result, null, 2));
          }
          break;
        }

        // ========== OTHER COMMANDS ==========
        case 'tasks': {
          const result = await callTool('list_tasks', {});
          console.log(JSON.stringify(result, null, 2));
          break;
        }

        case 'events': {
          const result = await callTool('get_upcoming_events', {});
          console.log(JSON.stringify(result, null, 2));
          break;
        }

        case 'stats': {
          const result = await callTool('get_workspace_stats', {});
          console.log(JSON.stringify(result, null, 2));
          break;
        }

        case 'docs': {
          const query = args[1];
          const result = await callTool('get_app_documentation', { query });
          console.log(JSON.stringify(result, null, 2));
          break;
        }

        case 'run-python': {
          const code = args.slice(1).join(' ');
          const result = await callTool('run_python', { code });
          console.log(JSON.stringify(result, null, 2));
          break;
        }

        case 'list': {
          const result = await sendRequest('tools/list', {});
          console.log(JSON.stringify(result.tools, null, 2));
          break;
        }

        case 'call': {
          const toolName = args[1];
          const toolArgs = args[2] ? JSON.parse(args[2]) : {};
          const result = await callTool(toolName, toolArgs);
          console.log(JSON.stringify(result, null, 2));
          break;
        }

        default:
          console.error(`Unknown command: ${command}`);
          process.exit(1);
      }

      ws.close();
      setTimeout(() => process.exit(0), 100);
    } catch (err) {
      console.error('Error:', err.message);
      ws.close();
      process.exit(1);
    }
  });

  ws.on('message', (data) => {
    const msg = JSON.parse(data.toString());

    if (msg.method === 'endpoint') {
      return;
    }

    if (pendingRequests.has(msg.id)) {
      const { resolve, reject } = pendingRequests.get(msg.id);
      pendingRequests.delete(msg.id);

      if (msg.error) {
        reject(new Error(msg.error.message || JSON.stringify(msg.error)));
      } else {
        resolve(msg.result);
      }
    }
  });

  ws.on('error', (err) => {
    console.error('WebSocket error:', err.message);
    process.exit(1);
  });

  setTimeout(() => {
    console.error('Connection timeout');
    ws.close();
    process.exit(1);
  }, 10000);
}

if (require.main === module) {
  main();
}
