/**
 * Auto-discovery for user_id and calendar_id
 * Fetches from Lark API if not configured
 */

import { larkApi } from './lark-api.mjs';
import { readFile, writeFile } from 'fs/promises';
import { existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const CACHE_FILE = join(__dirname, '../.lark-cache.json');

let cache = null;

/**
 * Load cache from disk
 */
async function loadCache() {
  if (cache !== null) return cache;

  if (existsSync(CACHE_FILE)) {
    try {
      const data = await readFile(CACHE_FILE, 'utf-8');
      cache = JSON.parse(data);
      return cache;
    } catch (error) {
      console.warn('Failed to load cache:', error.message);
    }
  }

  cache = {};
  return cache;
}

/**
 * Save cache to disk
 */
async function saveCache() {
  try {
    await writeFile(CACHE_FILE, JSON.stringify(cache, null, 2), 'utf-8');
  } catch (error) {
    console.warn('Failed to save cache:', error.message);
  }
}

/**
 * Get current user ID
 * First tries environment variable, then API discovery
 */
export async function getUserId() {
  // Check environment first
  if (process.env.FEISHU_USER_ID) {
    return process.env.FEISHU_USER_ID;
  }

  // Check cache
  const cacheData = await loadCache();
  if (cacheData.userId && cacheData.userIdExpire > Date.now()) {
    return cacheData.userId;
  }

  // Fetch from API
  try {
    const result = await larkApi('GET', '/contact/v3/users/me', {
      params: { user_id_type: 'user_id' }
    });

    const userId = result.user.user_id;

    // Cache for 24 hours
    cache.userId = userId;
    cache.userIdExpire = Date.now() + (24 * 60 * 60 * 1000);
    await saveCache();

    return userId;
  } catch (error) {
    console.error('Failed to get user_id from API:', error.message);
    throw new Error(
      'Could not discover user_id automatically. ' +
      'Please set FEISHU_USER_ID in .secrets.env or add contact:user.base:readonly scope.'
    );
  }
}

/**
 * Get calendar ID
 * First tries environment variable, then API discovery for primary calendar
 */
export async function getCalendarId() {
  // Check environment first
  if (process.env.FEISHU_CALENDAR_ID) {
    return process.env.FEISHU_CALENDAR_ID;
  }

  // Check cache
  const cacheData = await loadCache();
  if (cacheData.calendarId && cacheData.calendarIdExpire > Date.now()) {
    return cacheData.calendarId;
  }

  // Fetch from API
  try {
    const result = await larkApi('GET', '/calendar/v4/calendars', {
      params: { page_size: 50 }
    });

    const calendars = result.items || [];

    if (calendars.length === 0) {
      throw new Error('No calendars found');
    }

    // Find primary calendar
    let calendar = calendars.find(cal =>
      cal.type === 'primary' ||
      cal.summary === 'My Calendar' ||
      cal.calendar_id.includes('@primary.calendar')
    );

    // Fallback to personal calendar
    if (!calendar) {
      calendar = calendars.find(cal => cal.type === 'personal');
    }

    // Last resort: first calendar
    if (!calendar) {
      calendar = calendars[0];
    }

    const calendarId = calendar.calendar_id;

    // Cache for 24 hours
    cache.calendarId = calendarId;
    cache.calendarName = calendar.summary;
    cache.calendarIdExpire = Date.now() + (24 * 60 * 60 * 1000);
    await saveCache();

    return calendarId;
  } catch (error) {
    console.error('Failed to get calendar_id from API:', error.message);
    throw new Error(
      'Could not discover calendar_id automatically. ' +
      'Please set FEISHU_CALENDAR_ID in .secrets.env.'
    );
  }
}

/**
 * Get both user_id and calendar_id in one call
 */
export async function getConfig() {
  const [userId, calendarId] = await Promise.all([
    getUserId().catch(() => null),
    getCalendarId().catch(() => null)
  ]);

  return {
    userId,
    calendarId
  };
}

/**
 * Clear cache (useful for testing or when config changes)
 */
export async function clearCache() {
  cache = {};
  try {
    await writeFile(CACHE_FILE, JSON.stringify({}, null, 2), 'utf-8');
  } catch (error) {
    // Ignore
  }
}
