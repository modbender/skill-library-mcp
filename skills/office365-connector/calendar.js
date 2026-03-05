#!/usr/bin/env node
/**
 * Microsoft Graph Calendar Operations
 */

const https = require('https');
const { getAccessToken } = require('./auth.js');

/**
 * Make Graph API request
 */
function graphRequest(path, accessToken, options = {}) {
  return new Promise((resolve, reject) => {
    const reqOptions = {
      hostname: 'graph.microsoft.com',
      path: path,
      method: options.method || 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
        ...options.headers
      }
    };

    const req = https.request(reqOptions, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (res.statusCode >= 400) {
            reject(new Error(`HTTP ${res.statusCode}: ${parsed.error?.message || data}`));
          } else {
            resolve(parsed);
          }
        } catch (e) {
          reject(new Error(`Failed to parse response: ${data}`));
        }
      });
    });

    req.on('error', reject);
    
    if (options.body) {
      req.write(JSON.stringify(options.body));
    }
    
    req.end();
  });
}

/**
 * Get calendar events for a date range
 */
async function getEvents(startDate, endDate, accountName = null) {
  const token = await getAccessToken(accountName);
  
  const startISO = startDate.toISOString();
  const endISO = endDate.toISOString();
  
  const path = `/v1.0/me/calendarview?startDateTime=${encodeURIComponent(startISO)}&endDateTime=${encodeURIComponent(endISO)}&$orderby=start/dateTime&$top=50`;
  
  const response = await graphRequest(path, token);
  return response.value || [];
}

/**
 * Format event for display
 */
function formatEvent(event) {
  const start = new Date(event.start.dateTime + 'Z');
  const end = new Date(event.end.dateTime + 'Z');
  
  const timeStr = event.isAllDay 
    ? 'All Day'
    : `${start.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })} - ${end.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}`;
  
  let output = `${timeStr} | ${event.subject}`;
  
  if (event.location?.displayName) {
    output += ` | 📍 ${event.location.displayName}`;
  }
  
  if (event.organizer?.emailAddress?.name) {
    output += ` | 👤 ${event.organizer.emailAddress.name}`;
  }
  
  if (event.attendees && event.attendees.length > 0) {
    const attendeeNames = event.attendees
      .filter(a => a.emailAddress.address !== event.organizer?.emailAddress?.address)
      .map(a => a.emailAddress.name)
      .slice(0, 3);
    if (attendeeNames.length > 0) {
      output += ` | +${attendeeNames.join(', ')}`;
    }
  }
  
  return output;
}

/**
 * Get today's events
 */
async function getToday(accountName = null) {
  const now = new Date();
  const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0);
  const endOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59);
  
  const events = await getEvents(startOfDay, endOfDay, accountName);
  
  if (events.length === 0) {
    console.log('📅 No events scheduled for today');
    return;
  }
  
  console.log(`📅 Today's Calendar (${now.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })})\n`);
  
  events.forEach(event => {
    console.log(formatEvent(event));
  });
  
  console.log(`\nTotal: ${events.length} event${events.length !== 1 ? 's' : ''}`);
}

/**
 * Get this week's events
 */
async function getWeek(accountName = null) {
  const now = new Date();
  const startOfWeek = new Date(now.getFullYear(), now.getMonth(), now.getDate() - now.getDay());
  const endOfWeek = new Date(startOfWeek);
  endOfWeek.setDate(endOfWeek.getDate() + 7);
  
  const events = await getEvents(startOfWeek, endOfWeek, accountName);
  
  if (events.length === 0) {
    console.log('📅 No events scheduled this week');
    return;
  }
  
  console.log(`📅 This Week's Calendar\n`);
  
  let currentDay = null;
  events.forEach(event => {
    const eventDate = new Date(event.start.dateTime + 'Z');
    const dayStr = eventDate.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' });
    
    if (dayStr !== currentDay) {
      if (currentDay !== null) console.log('');
      console.log(`\n${dayStr}:`);
      currentDay = dayStr;
    }
    
    console.log('  ' + formatEvent(event));
  });
  
  console.log(`\nTotal: ${events.length} event${events.length !== 1 ? 's' : ''}`);
}

// CLI usage
if (require.main === module) {
  const command = process.argv[2] || 'today';
  const accountArg = process.argv.find(arg => arg.startsWith('--account='));
  const accountName = accountArg ? accountArg.split('=')[1] : null;
  
  if (command === 'today') {
    getToday(accountName).catch(err => {
      console.error('❌ Error:', err.message);
      process.exit(1);
    });
  } else if (command === 'week') {
    getWeek(accountName).catch(err => {
      console.error('❌ Error:', err.message);
      process.exit(1);
    });
  } else {
    console.log('Usage:');
    console.log('  node calendar.js today [--account=name]  - Show today\'s events');
    console.log('  node calendar.js week [--account=name]   - Show this week\'s events');
    console.log('\nIf --account is not specified, the default account is used.');
    process.exit(1);
  }
}

module.exports = {
  getEvents,
  getToday,
  getWeek,
  formatEvent
};
