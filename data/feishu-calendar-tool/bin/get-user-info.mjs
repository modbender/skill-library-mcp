#!/usr/bin/env node
/**
 * Get current user info and primary calendar from Lark
 * This script auto-discovers user_id and calendar_id without manual configuration
 */

import { larkApi } from '../lib/lark-api.mjs';
import { config } from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
config({ path: join(__dirname, '../../../.secrets.env') });

/**
 * Get current user info
 * Uses the app's ticket to get user info
 */
async function getCurrentUserInfo() {
  try {
    // First, we need to get the user_id from the context
    // For self-issued apps, we can use the contact API to get the current user
    // Try using the special "me" endpoint or admin contact

    // Method 1: Get user info from contact API (if app has permissions)
    const result = await larkApi('GET', '/contact/v3/users/me', {
      params: { user_id_type: 'user_id' }
    });

    return result.user;
  } catch (error) {
    // If /me fails, try alternative methods
    if (error.code === 99991400 || error.code === 99991668) {
      console.error('❌ Error: App does not have permission to access user info.');
      console.error('   Please add scope: contact:user.base:readonly or contact:user:readonly');
      console.error('   Visit: https://open.larksuite.com/app/' + process.env.FEISHU_APP_ID + '/auth');
    }
    throw error;
  }
}

/**
 * Get all calendars accessible to the user
 */
async function getCalendars() {
  try {
    const result = await larkApi('GET', '/calendar/v4/calendars', {
      params: { page_size: 50 }
    });

    return result.items || [];
  } catch (error) {
    console.error('❌ Failed to get calendars:', error.message);
    throw error;
  }
}

/**
 * Get primary calendar (usually the user's personal calendar)
 */
async function getPrimaryCalendar() {
  const calendars = await getCalendars();

  // Filter for primary/personal calendars
  // The primary calendar usually has type="primary" or no specific type
  const primary = calendars.find(cal =>
    cal.type === 'primary' ||
    cal.summary === 'My Calendar' ||
    cal.calendar_id.includes('@primary.calendar')
  );

  if (primary) {
    return primary;
  }

  // Fallback: return the first personal calendar
  const personal = calendars.find(cal => cal.type === 'personal');
  if (personal) {
    return personal;
  }

  // Last resort: return first calendar
  if (calendars.length > 0) {
    return calendars[0];
  }

  throw new Error('No calendars found');
}

/**
 * Display calendars in a nice format
 */
function displayCalendars(calendars) {
  console.log('\n📅 Available Calendars:');
  console.log('─'.repeat(80));

  calendars.forEach((cal, index) => {
    const emoji = cal.type === 'primary' ? '⭐' : '📆';
    const type = cal.type || 'personal';
    const summary = cal.summary || '(No name)';

    console.log(`\n${emoji} [${index + 1}] ${summary}`);
    console.log(`   Type:     ${type}`);
    console.log(`   Calendar ID: ${cal.calendar_id}`);
    console.log(`   Description: ${cal.description || '(none)'}`);
  });

  console.log('\n' + '─'.repeat(80));
}

/**
 * Main function
 */
async function main() {
  console.log('\n🔍 Discovering Lark (Feishu) user and calendar info...\n');

  // Get user info
  try {
    console.log('1️⃣ Getting current user info...');
    const user = await getCurrentUserInfo();
    console.log(`✅ Found user:`);
    console.log(`   Name:      ${user.name}`);
    console.log(`   User ID:   ${user.user_id}`);
    console.log(`   Email:     ${user.email || '(not set)'}`);
    console.log(`   Avatar:    ${user.avatar_url || '(not set)'}`);
  } catch (error) {
    console.log(`⚠️  Could not get user info: ${error.message}`);
    console.log(`   You may need to set USER_ID manually in .secrets.env\n`);
  }

  // Get calendars
  console.log('\n2️⃣ Getting available calendars...');
  const calendars = await getCalendars();
  console.log(`✅ Found ${calendars.length} calendar(s)`);

  // Display all calendars
  displayCalendars(calendars);

  // Show primary calendar
  try {
    const primary = await getPrimaryCalendar();
    console.log('\n⭐ Primary/Recommended Calendar:');
    console.log(`   Name:     ${primary.summary || '(unnamed)'}`);
    console.log(`   Calendar ID: ${primary.calendar_id}`);

    console.log('\n💡 Configuration for .secrets.env:');
    console.log('─'.repeat(80));
    console.log(`# Add these lines to your .secrets.env file:`);
    console.log(`FEISHU_USER_ID=${primary.user_id || '(from above)'}`);
    console.log(`FEISHU_CALENDAR_ID=${primary.calendar_id}`);
    console.log('─'.repeat(80));

  } catch (error) {
    console.log(`\n⚠️  Could not determine primary calendar: ${error.message}`);
  }

  console.log('\n✨ Done!\n');
}

// Run
main().catch(console.error);
