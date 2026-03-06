#!/usr/bin/env node
// Local sync script — runs on the Mac, pushes data to Supabase
// Reads Google Calendar + Fathom API, writes to Supabase

const fs = require('fs');
const path = require('path');

const SECRETS = path.join(process.env.HOME, '.openclaw/secrets');
const FATHOM_API_KEY = fs.readFileSync(path.join(SECRETS, 'fathom.env'), 'utf8')
  .split('\n').find(l => l.startsWith('FATHOM_API_KEY='))?.split('=').slice(1).join('=') || '';

const SUPABASE_URL = 'https://uypqzwazexgweazdauvj.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV5cHF6d2F6ZXhnd2VhemRhdXZqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTM4ODQ5MiwiZXhwIjoyMDg2OTY0NDkyfQ.OSPNdNn9DpekNRCqB-t1Efe8IkX0U881gsUqnqWs8hk';

const GOOGLE_CREDS = JSON.parse(fs.readFileSync(path.join(SECRETS, 'google-oauth.json'), 'utf8'));
const GOOGLE_TOKEN = JSON.parse(fs.readFileSync(path.join(SECRETS, 'google-tokens-daniel.json'), 'utf8'));

async function supabaseRequest(method, table, body, query = '') {
  const url = `${SUPABASE_URL}/rest/v1/${table}${query}`;
  const headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': `Bearer ${SUPABASE_KEY}`,
    'Content-Type': 'application/json',
    'Prefer': method === 'POST' ? 'return=representation' : 'return=representation',
  };
  if (method === 'PATCH' || method === 'DELETE') {
    // need Prefer header for updates
  }
  const res = await fetch(url, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const text = await res.text();
    console.error(`Supabase ${method} ${table} error:`, res.status, text);
    return null;
  }
  const text = await res.text();
  return text ? JSON.parse(text) : null;
}

async function refreshGoogleToken() {
  const res = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: GOOGLE_CREDS.client_id,
      client_secret: GOOGLE_CREDS.client_secret,
      refresh_token: GOOGLE_TOKEN.refresh_token,
      grant_type: 'refresh_token',
    }),
  });
  if (!res.ok) throw new Error(`Token refresh failed: ${res.status}`);
  const data = await res.json();
  return data.access_token;
}

async function getCalendarEvents(dateStr, accessToken) {
  const timeMin = `${dateStr}T00:00:00-08:00`;
  const timeMax = `${dateStr}T23:59:59-08:00`;
  const url = `https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin=${encodeURIComponent(timeMin)}&timeMax=${encodeURIComponent(timeMax)}&singleEvents=true&orderBy=startTime&maxResults=50`;
  const res = await fetch(url, { headers: { Authorization: `Bearer ${accessToken}` } });
  if (!res.ok) {
    console.error('Calendar API error:', res.status, await res.text());
    return [];
  }
  const data = await res.json();
  return (data.items || []).filter(e => e.start?.dateTime); // skip all-day events
}

async function getFathomMeetings(daysBack = 7) {
  const params = new URLSearchParams({ limit: '50' });
  const createdAfter = new Date();
  createdAfter.setDate(createdAfter.getDate() - daysBack);
  params.set('created_after', createdAfter.toISOString());
  
  const res = await fetch(`https://api.fathom.ai/external/v1/meetings?${params}`, {
    headers: { 'X-Api-Key': FATHOM_API_KEY },
  });
  if (!res.ok) {
    console.error('Fathom API error:', res.status, await res.text());
    return [];
  }
  const data = await res.json();
  return data.items || [];
}

async function getFathomMeetingDetail(meetingUrl) {
  // Extract the call ID from the URL
  const match = meetingUrl.match(/calls\/(\d+)/);
  if (!match) return null;
  
  // The API uses the meeting list endpoint with filters, or we fetch with include params
  const res = await fetch(`https://api.fathom.ai/external/v1/meetings?include_action_items=true&include_summary=true&limit=1`, {
    headers: { 'X-Api-Key': FATHOM_API_KEY },
  });
  // Actually, let's get details from the share URL approach or just re-fetch with params
  return null;
}

function matchFathomToCalEvent(fathomMeetings, calEvent) {
  const eventStart = new Date(calEvent.start.dateTime).getTime();
  const eventEnd = new Date(calEvent.end.dateTime).getTime();
  const buffer = 15 * 60 * 1000;
  
  for (const fm of fathomMeetings) {
    const fStart = new Date(fm.recording_start_time || fm.scheduled_start_time).getTime();
    if (fStart >= eventStart - buffer && fStart <= eventEnd + buffer) return fm;
    
    // Title matching fallback
    const fTitle = (fm.title || fm.meeting_title || '').toLowerCase();
    const eTitle = (calEvent.summary || '').toLowerCase();
    if (fTitle && eTitle && (fTitle.includes(eTitle) || eTitle.includes(fTitle))) return fm;
  }
  return null;
}

async function syncDay(dateStr, accessToken, fathomMeetings) {
  console.log(`Syncing ${dateStr}...`);
  
  // Upsert calendar day
  const existingDays = await supabaseRequest('GET', 'calendar_days', null, `?date=eq.${dateStr}&select=*`);
  let dayId;
  if (existingDays && existingDays.length > 0) {
    dayId = existingDays[0].id;
    await supabaseRequest('PATCH', 'calendar_days', { synced_at: new Date().toISOString() }, `?id=eq.${dayId}`);
  } else {
    const result = await supabaseRequest('POST', 'calendar_days', { date: dateStr, synced_at: new Date().toISOString() });
    if (!result || !result[0]) { console.error('Failed to create day', dateStr); return; }
    dayId = result[0].id;
  }
  
  // Get calendar events
  const calEvents = await getCalendarEvents(dateStr, accessToken);
  console.log(`  ${calEvents.length} calendar events`);
  
  // Filter Fathom meetings for this date
  const dayFathom = fathomMeetings.filter(fm => {
    const d = (fm.recording_start_time || fm.scheduled_start_time || '').split('T')[0];
    return d === dateStr;
  });
  console.log(`  ${dayFathom.length} Fathom recordings`);
  
  const processedFathomIds = new Set();
  
  for (const event of calEvents) {
    const title = event.summary || 'Untitled';
    const startTime = event.start.dateTime;
    const endTime = event.end.dateTime;
    const attendees = (event.attendees || []).map(a => ({ name: a.displayName || '', email: a.email || '' }));
    
    const fathomMatch = matchFathomToCalEvent(dayFathom, event);
    if (fathomMatch) processedFathomIds.add(fathomMatch.url);
    
    // Check if meeting exists
    const existing = await supabaseRequest('GET', 'meetings', null, 
      `?calendar_day_id=eq.${dayId}&title=eq.${encodeURIComponent(title)}&start_time=eq.${encodeURIComponent(startTime)}&select=id`);
    
    const meetingData = {
      calendar_day_id: dayId,
      title,
      start_time: startTime,
      end_time: endTime,
      attendees: JSON.stringify(attendees),
      has_recording: !!fathomMatch,
      fathom_recording_url: fathomMatch?.url || null,
      fathom_share_url: fathomMatch?.share_url || null,
      synced_at: new Date().toISOString(),
    };
    
    let meetingId;
    if (existing && existing.length > 0) {
      meetingId = existing[0].id;
      await supabaseRequest('PATCH', 'meetings', meetingData, `?id=eq.${meetingId}`);
    } else {
      const result = await supabaseRequest('POST', 'meetings', meetingData);
      if (result && result[0]) meetingId = result[0].id;
    }
    
    // Insert action items from Fathom
    if (meetingId && fathomMatch && fathomMatch.action_items) {
      for (const item of fathomMatch.action_items) {
        const desc = typeof item === 'string' ? item : (item.text || item.description || '');
        if (!desc) continue;
        
        const existingItem = await supabaseRequest('GET', 'action_items', null,
          `?meeting_id=eq.${meetingId}&description=eq.${encodeURIComponent(desc)}&select=id`);
        if (!existingItem || existingItem.length === 0) {
          await supabaseRequest('POST', 'action_items', {
            meeting_id: meetingId,
            description: desc,
            owner: typeof item === 'object' ? (item.assignee || item.owner || null) : null,
            deadline: typeof item === 'object' ? (item.due_date || item.deadline || null) : null,
            status: 'open',
          });
        }
      }
    }
    
    console.log(`  Meeting: ${title} ${fathomMatch ? '(recorded)' : '(no recording)'}`);
  }
  
  // Handle Fathom-only recordings not matched to calendar
  for (const fm of dayFathom) {
    if (processedFathomIds.has(fm.url)) continue;
    const title = fm.title || fm.meeting_title || 'Fathom Recording';
    const startTime = fm.recording_start_time || fm.scheduled_start_time;
    const endTime = fm.recording_end_time || fm.scheduled_end_time || startTime;
    const attendees = (fm.calendar_invitees || []).map(a => ({ name: a.name || '', email: a.email || '' }));
    
    const existing = await supabaseRequest('GET', 'meetings', null,
      `?calendar_day_id=eq.${dayId}&title=eq.${encodeURIComponent(title)}&select=id`);
    
    if (!existing || existing.length === 0) {
      const result = await supabaseRequest('POST', 'meetings', {
        calendar_day_id: dayId,
        title,
        start_time: startTime,
        end_time: endTime,
        attendees: JSON.stringify(attendees),
        has_recording: true,
        fathom_recording_url: fm.url || null,
        fathom_share_url: fm.share_url || null,
        synced_at: new Date().toISOString(),
      });
      
      if (result && result[0] && fm.action_items) {
        for (const item of fm.action_items) {
          const desc = typeof item === 'string' ? item : (item.text || item.description || '');
          if (!desc) continue;
          await supabaseRequest('POST', 'action_items', {
            meeting_id: result[0].id,
            description: desc,
            owner: typeof item === 'object' ? (item.assignee || item.owner || null) : null,
            deadline: typeof item === 'object' ? (item.due_date || item.deadline || null) : null,
            status: 'open',
          });
        }
      }
      console.log(`  Fathom-only: ${title}`);
    }
  }
}

async function main() {
  console.log('Starting Action Tracker sync...');
  
  // Refresh Google token
  const accessToken = await refreshGoogleToken();
  console.log('Google token refreshed');
  
  // Get all Fathom meetings (with action items)
  // We need to re-fetch with action items included
  const params = new URLSearchParams({ limit: '50', include_action_items: 'true', include_summary: 'true' });
  const createdAfter = new Date();
  createdAfter.setDate(createdAfter.getDate() - 7);
  params.set('created_after', createdAfter.toISOString());
  
  const res = await fetch(`https://api.fathom.ai/external/v1/meetings?${params}`, {
    headers: { 'X-Api-Key': FATHOM_API_KEY },
  });
  let fathomMeetings = [];
  if (res.ok) {
    const data = await res.json();
    fathomMeetings = data.items || [];
    console.log(`Fetched ${fathomMeetings.length} Fathom meetings`);
  } else {
    console.error('Fathom error:', res.status, await res.text());
  }
  
  // Sync each day
  const today = new Date();
  for (let i = 0; i < 7; i++) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    const dateStr = d.toISOString().split('T')[0];
    await syncDay(dateStr, accessToken, fathomMeetings);
  }
  
  console.log('Sync complete!');
}

main().catch(console.error);
