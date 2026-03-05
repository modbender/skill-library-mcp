#!/usr/bin/env node
/**
 * Cozi CLI - Interact with Cozi Family Organizer
 * 
 * Lists:
 *   node cozi.js lists                     - Show all lists
 *   node cozi.js list <listId>             - Show specific list
 *   node cozi.js add <listId> "item"       - Add item to list
 *   node cozi.js check <listId> <itemId>   - Mark item complete
 *   node cozi.js uncheck <listId> <itemId> - Mark item incomplete
 *   node cozi.js remove <listId> <itemId>  - Remove item
 *   node cozi.js new-list "title" [type]   - Create list (shopping|todo)
 *   node cozi.js delete-list <listId>      - Delete list
 * 
 * Calendar:
 *   node cozi.js calendar [year] [month]   - Show calendar month
 *   node cozi.js add-appt YYYY-MM-DD HH:MM HH:MM "subject" [location] [notes]
 *   node cozi.js remove-appt <year> <month> <apptId>
 * 
 * Requires: COZI_EMAIL and COZI_PASSWORD environment variables
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

// Config
const BASE_URL = 'rest.cozi.com';
const API_VERSION = 'api/ext/2207';
const LISTS_VERSION = 'api/ext/2004';
const SESSION_FILE = path.join(__dirname, '..', '.session.json');

// Load Cozi credentials from environment or skill-level .env
function loadEnv() {
  // First check if already set in process.env
  if (process.env.COZI_EMAIL && process.env.COZI_PASSWORD) {
    return;
  }
  
  // Try skill-level .env first
  const skillEnvPath = path.join(__dirname, '..', '.env');
  if (fs.existsSync(skillEnvPath)) {
    const content = fs.readFileSync(skillEnvPath, 'utf8');
    content.split('\n').forEach(line => {
      const match = line.match(/^(COZI_EMAIL|COZI_PASSWORD)=(.*)$/);
      if (match && !process.env[match[1]]) {
        process.env[match[1]] = match[2].trim().replace(/^["']|["']$/g, '');
      }
    });
  }
  
  // Fallback: try agent-level .env but ONLY read COZI_* vars
  const agentEnvPath = path.join(__dirname, '..', '..', '..', '.env');
  if (fs.existsSync(agentEnvPath)) {
    const content = fs.readFileSync(agentEnvPath, 'utf8');
    content.split('\n').forEach(line => {
      const match = line.match(/^(COZI_EMAIL|COZI_PASSWORD)=(.*)$/);
      if (match && !process.env[match[1]]) {
        process.env[match[1]] = match[2].trim().replace(/^["']|["']$/g, '');
      }
    });
  }
}
loadEnv();

// HTTP request helper
function request(method, path, body = null, token = null) {
  return new Promise((resolve, reject) => {
    const headers = {
      'Content-Type': 'application/json',
      'User-Agent': 'cozi-cli/1.0'
    };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const options = {
      hostname: BASE_URL,
      path: `/${path}`,
      method,
      headers
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode >= 400) {
          reject(new Error(`HTTP ${res.statusCode}: ${data}`));
        } else {
          resolve(data ? JSON.parse(data) : {});
        }
      });
    });

    req.on('error', reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

// Load/save session
function loadSession() {
  if (fs.existsSync(SESSION_FILE)) {
    const session = JSON.parse(fs.readFileSync(SESSION_FILE, 'utf8'));
    // Check if expired
    if (session.expiresAt && new Date(session.expiresAt) > new Date()) {
      return session;
    }
  }
  return null;
}

function saveSession(session) {
  fs.writeFileSync(SESSION_FILE, JSON.stringify(session, null, 2));
}

// Authenticate
async function authenticate() {
  const email = process.env.COZI_EMAIL;
  const password = process.env.COZI_PASSWORD;

  if (!email || !password) {
    console.error('Error: COZI_EMAIL and COZI_PASSWORD must be set in environment or .env file');
    process.exit(1);
  }

  const response = await request('POST', `${API_VERSION}/auth/login`, {
    username: email,
    password
  });

  const session = {
    accessToken: response.accessToken,
    accountId: response.accountId,
    accountPersonId: response.accountPersonId,
    expiresAt: new Date(Date.now() + response.expiresIn * 1000).toISOString()
  };

  saveSession(session);
  return session;
}

// Get or create session
async function getSession() {
  let session = loadSession();
  if (!session) {
    console.error('Authenticating with Cozi...');
    session = await authenticate();
  }
  return session;
}

// API methods
async function getLists(session) {
  return request('GET', `${LISTS_VERSION}/${session.accountId}/list/`, null, session.accessToken);
}

async function getList(session, listId) {
  return request('GET', `${LISTS_VERSION}/${session.accountId}/list/${listId}`, null, session.accessToken);
}

async function addItem(session, listId, text) {
  return request('POST', `${LISTS_VERSION}/${session.accountId}/list/${listId}/item/`, { text }, session.accessToken);
}

async function markItem(session, listId, itemId, completed) {
  const status = completed ? 'complete' : 'incomplete';
  return request('PUT', `${LISTS_VERSION}/${session.accountId}/list/${listId}/item/${itemId}`, { status }, session.accessToken);
}

async function editItem(session, listId, itemId, text) {
  return request('PUT', `${LISTS_VERSION}/${session.accountId}/list/${listId}/item/${itemId}`, { text }, session.accessToken);
}

async function removeItem(session, listId, itemId) {
  return request('DELETE', `${LISTS_VERSION}/${session.accountId}/list/${listId}/item/${itemId}`, null, session.accessToken);
}

async function createList(session, title, type = 'shopping') {
  return request('POST', `${LISTS_VERSION}/${session.accountId}/list/`, { title, listType: type }, session.accessToken);
}

async function deleteList(session, listId) {
  return request('DELETE', `${LISTS_VERSION}/${session.accountId}/list/${listId}`, null, session.accessToken);
}

// Calendar methods
async function getCalendar(session, year, month) {
  return request('GET', `${LISTS_VERSION}/${session.accountId}/calendar/${year}/${month}`, null, session.accessToken);
}

async function addAppointment(session, appt) {
  return request('POST', `${LISTS_VERSION}/${session.accountId}/calendar/`, appt, session.accessToken);
}

async function editAppointment(session, apptId, appt) {
  return request('PUT', `${LISTS_VERSION}/${session.accountId}/calendar/${apptId}`, appt, session.accessToken);
}

async function removeAppointment(session, year, month, apptId) {
  return request('DELETE', `${LISTS_VERSION}/${session.accountId}/calendar/${year}/${month}/${apptId}`, null, session.accessToken);
}

// Output formatters
function formatLists(lists) {
  console.log('\n📋 Your Cozi Lists:\n');
  lists.forEach(list => {
    const icon = list.listType === 'shopping' ? '🛒' : '✅';
    const completed = list.items.filter(i => i.status === 'complete').length;
    console.log(`${icon} ${list.title} (${list.listType})`);
    console.log(`   ID: ${list.listId}`);
    console.log(`   ${completed}/${list.items.length} items complete`);
    if (list.items.length > 0) {
      list.items.slice(0, 5).forEach(item => {
        const check = item.status === 'complete' ? '☑' : '☐';
        console.log(`   ${check} ${item.text}`);
      });
      if (list.items.length > 5) {
        console.log(`   ... and ${list.items.length - 5} more`);
      }
    }
    console.log('');
  });
}

function formatList(list) {
  const icon = list.listType === 'shopping' ? '🛒' : '✅';
  console.log(`\n${icon} ${list.title} (${list.listType})`);
  console.log(`   ID: ${list.listId}`);
  console.log('');
  list.items.forEach(item => {
    const check = item.status === 'complete' ? '☑' : '☐';
    console.log(`   ${check} ${item.text} [${item.itemId}]`);
  });
  console.log('');
}

function formatCalendar(data, year, month) {
  const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 
                      'July', 'August', 'September', 'October', 'November', 'December'];
  console.log(`\n📅 ${monthNames[month - 1]} ${year}\n`);
  
  if (!data.days || !data.items) {
    console.log('   No appointments');
    return;
  }
  
  // Build list of appointments with their dates
  const appointments = [];
  for (const [dateStr, apptIds] of Object.entries(data.days)) {
    for (const apptRef of apptIds) {
      const appt = data.items[apptRef.id];
      if (appt) {
        appointments.push({
          date: dateStr,
          day: parseInt(dateStr.split('-')[2]),
          ...appt
        });
      }
    }
  }
  
  if (appointments.length === 0) {
    console.log('   No appointments');
    return;
  }
  
  // Sort by day, then start time
  const sorted = appointments.sort((a, b) => {
    if (a.day !== b.day) return a.day - b.day;
    return (a.startTime || '').localeCompare(b.startTime || '');
  });
  
  // Group by date
  const grouped = {};
  sorted.forEach(appt => {
    if (!grouped[appt.date]) grouped[appt.date] = [];
    grouped[appt.date].push(appt);
  });
  
  // Display
  Object.keys(grouped).sort().forEach(dateStr => {
    const day = String(parseInt(dateStr.split('-')[2]));
    const weekday = new Date(dateStr).toLocaleDateString('en-US', { weekday: 'short' });
    console.log(`   ${day.padStart(2, ' ')} ${weekday}`);
    
    grouped[dateStr].forEach(appt => {
      const time = appt.startTime ? appt.startTime.slice(0, 5) : '';
      const endTime = appt.endTime ? appt.endTime.slice(0, 5) : '';
      const timeStr = time && endTime ? `${time}-${endTime}` : time;
      console.log(`       ${timeStr.padEnd(11)} ${appt.description}`);
      if (appt.itemDetails?.notes) {
        console.log(`       Notes: ${appt.itemDetails.notes.split('\n')[0].slice(0, 50)}...`);
      }
    });
  });
  console.log('');
}

// Main CLI
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  try {
    const session = await getSession();

    switch (command) {
      case 'lists': {
        const lists = await getLists(session);
        formatLists(lists);
        break;
      }

      case 'list': {
        const listId = args[1];
        if (!listId) {
          console.error('Usage: cozi.js list <listId>');
          process.exit(1);
        }
        const list = await getList(session, listId);
        formatList(list);
        break;
      }

      case 'add': {
        const listId = args[1];
        const text = args[2];
        if (!listId || !text) {
          console.error('Usage: cozi.js add <listId> "item text"');
          process.exit(1);
        }
        await addItem(session, listId, text);
        console.log(`✓ Added "${text}" to list`);
        break;
      }

      case 'check': {
        const listId = args[1];
        const itemId = args[2];
        if (!listId || !itemId) {
          console.error('Usage: cozi.js check <listId> <itemId>');
          process.exit(1);
        }
        await markItem(session, listId, itemId, true);
        console.log('✓ Item marked complete');
        break;
      }

      case 'uncheck': {
        const listId = args[1];
        const itemId = args[2];
        if (!listId || !itemId) {
          console.error('Usage: cozi.js uncheck <listId> <itemId>');
          process.exit(1);
        }
        await markItem(session, listId, itemId, false);
        console.log('✓ Item marked incomplete');
        break;
      }

      case 'edit': {
        const listId = args[1];
        const itemId = args[2];
        const text = args[3];
        if (!listId || !itemId || !text) {
          console.error('Usage: cozi.js edit <listId> <itemId> "new text"');
          process.exit(1);
        }
        await editItem(session, listId, itemId, text);
        console.log(`✓ Item updated to "${text}"`);
        break;
      }

      case 'remove': {
        const listId = args[1];
        const itemId = args[2];
        if (!listId || !itemId) {
          console.error('Usage: cozi.js remove <listId> <itemId>');
          process.exit(1);
        }
        await removeItem(session, listId, itemId);
        console.log('✓ Item removed');
        break;
      }

      case 'new-list': {
        const title = args[1];
        const type = args[2] || 'shopping';
        if (!title) {
          console.error('Usage: cozi.js new-list "title" [shopping|todo]');
          process.exit(1);
        }
        const result = await createList(session, title, type);
        console.log(`✓ Created ${type} list "${title}" (ID: ${result.listId || 'see lists'})`);
        break;
      }

      case 'delete-list': {
        const listId = args[1];
        if (!listId) {
          console.error('Usage: cozi.js delete-list <listId>');
          process.exit(1);
        }
        await deleteList(session, listId);
        console.log('✓ List deleted');
        break;
      }

      // Calendar commands
      case 'calendar':
      case 'cal': {
        const year = parseInt(args[1]) || new Date().getFullYear();
        const month = parseInt(args[2]) || new Date().getMonth() + 1;
        const calendar = await getCalendar(session, year, month);
        formatCalendar(calendar.appointments || calendar, year, month);
        break;
      }

      case 'add-appt': {
        const dateStr = args[1]; // YYYY-MM-DD
        const start = args[2];   // HH:MM
        const end = args[3];     // HH:MM
        const subject = args[4];
        
        if (!dateStr || !start || !subject) {
          console.error('Usage: cozi.js add-appt YYYY-MM-DD HH:MM HH:MM "subject" [location] [notes]');
          process.exit(1);
        }
        
        const [year, month, day] = dateStr.split('-').map(Number);
        
        const appt = {
          year,
          month,
          day,
          start,
          end: end || start,
          subject,
          location: args[5] || '',
          notes: args[6] || '',
          dateSpan: 1,
          attendees: []
        };
        
        await addAppointment(session, appt);
        console.log(`✓ Added "${subject}" on ${dateStr} at ${start}`);
        break;
      }

      case 'remove-appt': {
        const year = parseInt(args[1]);
        const month = parseInt(args[2]);
        const apptId = args[3];
        
        if (!year || !month || !apptId) {
          console.error('Usage: cozi.js remove-appt <year> <month> <apptId>');
          process.exit(1);
        }
        
        await removeAppointment(session, year, month, apptId);
        console.log('✓ Appointment removed');
        break;
      }

      default:
        console.log(`
Cozi CLI - Family Organizer Commands

Lists:
  node cozi.js lists                     Show all lists
  node cozi.js list <listId>             Show specific list
  node cozi.js add <listId> "item"       Add item to list
  node cozi.js check <listId> <itemId>   Mark item complete
  node cozi.js uncheck <listId> <itemId> Mark item incomplete
  node cozi.js edit <listId> <itemId> "text"  Edit item text
  node cozi.js remove <listId> <itemId>  Remove item
  node cozi.js new-list "title" [type]   Create list (shopping|todo)
  node cozi.js delete-list <listId>      Delete list

Calendar:
  node cozi.js calendar [year] [month]   Show calendar (defaults to current month)
  node cozi.js cal [year] [month]         Same as calendar
  node cozi.js add-appt YYYY-MM-DD HH:MM HH:MM "subject" [location] [notes]
  node cozi.js remove-appt <year> <month> <apptId>

Environment:
  COZI_EMAIL      Your Cozi account email
  COZI_PASSWORD   Your Cozi account password
        `);
    }
  } catch (error) {
    // If auth failed, try re-authenticating
    if (error.message.includes('401') || error.message.includes('403')) {
      console.error('Session expired, re-authenticating...');
      fs.unlinkSync(SESSION_FILE);
      const session = await authenticate();
      // Retry the command would require restructuring, for now just notify
      console.error('Re-authenticated. Please run your command again.');
    } else {
      console.error('Error:', error.message);
      process.exit(1);
    }
  }
}

main();