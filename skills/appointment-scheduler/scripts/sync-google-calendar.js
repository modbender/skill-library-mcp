#!/usr/bin/env node
/**
 * Sync appointments with Google Calendar
 * Requires: Google Calendar API enabled + OAuth credentials
 * 
 * Setup:
 * 1. Enable Google Calendar API in Google Cloud Console
 * 2. Download OAuth credentials → save as ~/.secrets/google-calendar-credentials.json
 * 3. First run will open browser for auth
 * 4. Refresh token saved to ~/.secrets/google-calendar-token.json
 */

const fs = require('fs');
const path = require('path');
const { google } = require('googleapis');

const CREDENTIALS_PATH = path.join(process.env.HOME, '.secrets', 'google-calendar-credentials.json');
const TOKEN_PATH = path.join(process.env.HOME, '.secrets', 'google-calendar-token.json');
const CONFIG_FILE = path.join(process.env.HOME, '.openclaw', 'workspace', 'config', 'appointment-scheduler.json');
const DATA_DIR = path.join(process.env.HOME, '.openclaw', 'workspace', 'data', 'appointments', 'bookings');

// Check if credentials exist
if (!fs.existsSync(CREDENTIALS_PATH)) {
  console.error('❌ Google Calendar credentials not found');
  console.error('Place OAuth credentials at:', CREDENTIALS_PATH);
  console.error('\nSetup guide:');
  console.error('1. Go to https://console.cloud.google.com/');
  console.error('2. Enable Google Calendar API');
  console.error('3. Create OAuth 2.0 credentials');
  console.error('4. Download and save to ~/.secrets/google-calendar-credentials.json');
  process.exit(1);
}

// Load credentials
const credentials = JSON.parse(fs.readFileSync(CREDENTIALS_PATH, 'utf8'));
const { client_secret, client_id, redirect_uris } = credentials.installed || credentials.web;

const oAuth2Client = new google.auth.OAuth2(client_id, client_secret, redirect_uris[0]);

// Load or request token
async function authorize() {
  if (fs.existsSync(TOKEN_PATH)) {
    const token = JSON.parse(fs.readFileSync(TOKEN_PATH, 'utf8'));
    oAuth2Client.setCredentials(token);
    return oAuth2Client;
  }
  
  console.error('❌ No auth token found. Run this script manually first to authenticate.');
  console.error('Auth URL will open in browser. Follow the flow and paste the code.');
  
  const authUrl = oAuth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: ['https://www.googleapis.com/auth/calendar']
  });
  
  console.log('\nAuthorize this app by visiting this url:', authUrl);
  process.exit(1);
}

// Sync bookings to Google Calendar
async function syncToCalendar() {
  const auth = await authorize();
  const calendar = google.calendar({ version: 'v3', auth });
  
  // Load config
  const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
  const calendarId = config.calendar.google.calendar_id || 'primary';
  
  // Get all booking files
  const files = fs.readdirSync(DATA_DIR).filter(f => f.endsWith('.json'));
  let synced = 0;
  let errors = 0;
  
  for (const file of files) {
    const filePath = path.join(DATA_DIR, file);
    const bookings = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    
    for (const booking of bookings) {
      // Skip if already synced
      if (booking.google_event_id) {
        continue;
      }
      
      // Create event
      const startDateTime = `${booking.date}T${booking.time}:00`;
      const endTime = new Date(`${startDateTime}Z`);
      endTime.setMinutes(endTime.getMinutes() + booking.duration);
      
      const event = {
        summary: `${booking.service} - ${booking.customer.name}`,
        description: `고객: ${booking.customer.name}\n전화: ${booking.customer.phone || 'N/A'}\n메모: ${booking.notes || 'N/A'}`,
        start: {
          dateTime: startDateTime,
          timeZone: 'Asia/Seoul'
        },
        end: {
          dateTime: endTime.toISOString(),
          timeZone: 'Asia/Seoul'
        },
        reminders: {
          useDefault: false,
          overrides: [
            { method: 'popup', minutes: 120 }
          ]
        }
      };
      
      try {
        const response = await calendar.events.insert({
          calendarId: calendarId,
          resource: event
        });
        
        // Save event ID to booking
        booking.google_event_id = response.data.id;
        synced++;
        
      } catch (error) {
        console.error(`❌ Error syncing booking ${booking.id}:`, error.message);
        errors++;
      }
    }
    
    // Save updated bookings
    fs.writeFileSync(filePath, JSON.stringify(bookings, null, 2));
  }
  
  console.log(`\n✅ Sync complete: ${synced} events synced, ${errors} errors`);
}

// Run
syncToCalendar().catch(console.error);
