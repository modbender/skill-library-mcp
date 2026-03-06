const { google } = require('googleapis');
const { JWT } = require('google-auth-library');
const { readFileSync, existsSync } = require('fs');
const { resolve } = require('path');

class GoogleCalendarService {
  constructor() {
    this.calendar = null;
    this.initialized = false;
  }

  /**
   * Initialize Google Calendar API service
   */
  async init() {
    try {
      // Check for credentials file or environment variable
      const credentialsPath = process.env.GOOGLE_CALENDAR_CREDENTIALS_PATH 
        || resolve(__dirname, 'google-calendar-credentials.json');
      
      const credentialsJson = process.env.GOOGLE_CALENDAR_CREDENTIALS;

      let credentials;

      if (credentialsJson) {
        // Use credentials from environment variable (for production)
        credentials = JSON.parse(credentialsJson);
        console.log('[Calendar] Using credentials from environment variable');
      } else if (existsSync(credentialsPath)) {
        // Use credentials file (for local development)
        credentials = JSON.parse(readFileSync(credentialsPath, 'utf-8'));
        console.log('[Calendar] Using credentials from file:', credentialsPath);
      } else {
        console.warn('[Calendar] No credentials found, calendar integration disabled');
        return;
      }

      const auth = new JWT({
        email: credentials.client_email,
        key: credentials.private_key,
        scopes: ['https://www.googleapis.com/auth/calendar'],
      });

      this.calendar = google.calendar({ version: 'v3', auth });
      this.initialized = true;
      console.log('[Calendar] Service initialized successfully');
    } catch (error) {
      console.error('[Calendar] Failed to initialize:', error);
    }
  }

  /**
   * Check if calendar service is available
   */
  isAvailable() {
    return this.initialized && this.calendar !== null;
  }

  /**
   * Add an event to Google Calendar
   */
  async addEvent(event) {
    if (!this.calendar) {
      console.warn('[Calendar] Service not available, skipping event creation');
      return false;
    }

    try {
      console.log('[Calendar] Adding event:', event.summary);
      console.log('[Calendar] Start:', event.startDateTime.toISOString());
      console.log('[Calendar] End:', event.endDateTime.toISOString());

      const calendarId = process.env.GOOGLE_CALENDAR_ID || 'primary';

      // Format datetime as local time string without timezone (YYYY-MM-DDTHH:MM:SS)
      // Google will interpret this in the specified timeZone
      const formatLocalDateTime = (date, hours, minutes) => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const h = String(hours).padStart(2, '0');
        const m = String(minutes).padStart(2, '0');
        return `${year}-${month}-${day}T${h}:${m}:00`;
      };

      // Extract the intended local time from the Date objects
      // (these were set with setHours in parseTimeToDate)
      const startLocal = formatLocalDateTime(
        event.startDateTime,
        event.startDateTime.getHours(),
        event.startDateTime.getMinutes()
      );
      const endLocal = formatLocalDateTime(
        event.endDateTime,
        event.endDateTime.getHours(),
        event.endDateTime.getMinutes()
      );

      console.log('[Calendar] Local start:', startLocal);
      console.log('[Calendar] Local end:', endLocal);

      const calendarEvent = {
        summary: event.summary,
        location: event.location,
        description: event.description,
        start: {
          dateTime: startLocal,
          timeZone: 'America/Los_Angeles',
        },
        end: {
          dateTime: endLocal,
          timeZone: 'America/Los_Angeles',
        },
      };

      const response = await this.calendar.events.insert({
        calendarId,
        requestBody: calendarEvent,
      });

      const startFormatted = event.startDateTime.toLocaleString('en-US', {
        weekday: 'long',
        month: 'long',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        timeZone: 'America/Los_Angeles',
      });

      console.log(`[Calendar] ✓ Event created: ${startFormatted}`);
      console.log(`[Calendar] Event ID: ${response.data.id}`);
      return true;
    } catch (error) {
      console.error('[Calendar] Failed to add event:', error);
      return false;
    }
  }

  /**
   * Create a court booking event
   */
  async addCourtBooking(sport, date, time, buddy = 'Samuel Wang') {
    // Parse the time string (e.g., "2:00 PM" or "14:00")
    const startDateTime = this.parseTimeToDate(date, time);
    if (!startDateTime) {
      console.error('[Calendar] Failed to parse time:', time);
      return false;
    }

    // Tennis is 90 minutes, pickleball is 60 minutes
    const durationMinutes = sport === 'tennis' ? 90 : 60;
    const endDateTime = new Date(startDateTime.getTime() + durationMinutes * 60 * 1000);

    const sportEmoji = sport === 'tennis' ? '🎾' : '🥒';
    const sportName = sport.charAt(0).toUpperCase() + sport.slice(1);

    return this.addEvent({
      summary: `${sportEmoji} ${sportName} - Bay Club Gateway`,
      location: 'Bay Club Gateway, San Francisco, CA',
      description: `${sportName} court booking at Bay Club Gateway

Buddy: ${buddy}
Duration: ${durationMinutes} minutes

Booked via OpenClaw Bay Club Bot`,
      startDateTime,
      endDateTime,
    });
  }

  /**
   * Parse a time string and combine with a date
   */
  parseTimeToDate(date, timeStr) {
    try {
      // Handle time ranges like "7:00 AM - 8:30 AM" by extracting just the start time
      const timeRangeMatch = timeStr.match(/^(.+?)\s*-\s*.+$/);
      const timeToUse = timeRangeMatch ? timeRangeMatch[1].trim() : timeStr;
      
      // Handle formats like "2:00 PM", "2:00PM", "14:00", "2pm"
      const normalizedTime = timeToUse.trim().toUpperCase();
      
      let hours;
      let minutes = 0;

      // Match patterns like "2:00 PM", "2:30PM", "2 PM", "2PM"
      const match12Hour = normalizedTime.match(/^(\d{1,2})(?::(\d{2}))?\s*(AM|PM)$/);
      // Match patterns like "14:00", "9:30"
      const match24Hour = normalizedTime.match(/^(\d{1,2}):(\d{2})$/);

      if (match12Hour) {
        hours = parseInt(match12Hour[1], 10);
        minutes = match12Hour[2] ? parseInt(match12Hour[2], 10) : 0;
        const isPM = match12Hour[3] === 'PM';
        
        if (hours === 12) {
          hours = isPM ? 12 : 0;
        } else if (isPM) {
          hours += 12;
        }
      } else if (match24Hour) {
        hours = parseInt(match24Hour[1], 10);
        minutes = parseInt(match24Hour[2], 10);
      } else {
        return null;
      }

      const result = new Date(date);
      result.setHours(hours, minutes, 0, 0);
      return result;
    } catch {
      return null;
    }
  }
}

// Singleton instance
const calendarService = new GoogleCalendarService();

module.exports = { GoogleCalendarService, calendarService };
