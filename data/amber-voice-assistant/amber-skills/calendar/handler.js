/**
 * Calendar Skill — Handler
 *
 * Queries and manages calendar events via ical-query CLI.
 *
 * PRIVACY RULE: For lookups, event titles and details are NEVER returned to Amber.
 * Only busy time slots are returned so Amber can communicate availability
 * without disclosing what the events are.
 */

/**
 * Parse ical-query output and extract only busy time ranges.
 * Strips event titles, locations, notes — returns only time slots.
 *
 * ical-query output format:
 * YYYY-MM-DD HH:MM - YYYY-MM-DD HH:MM | Event Title [all-day] @ Location [Calendar] id:<id>
 */
function extractBusySlots(output) {
  const slots = [];
  const lines = output.trim().split('\n');

  for (const line of lines) {
    if (!line.trim()) continue;

    // Match: date time - date time | ... (everything after | is stripped)
    const match = line.match(/^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\s*-\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})/);
    const allDay = line.includes('[all-day]');

    if (match) {
      slots.push({ start: match[1].trim(), end: match[2].trim(), allDay });
    } else if (allDay) {
      // All-day events — extract date only
      const dateMatch = line.match(/^(\d{4}-\d{2}-\d{2})/);
      if (dateMatch) {
        slots.push({ start: dateMatch[1], end: dateMatch[1], allDay: true });
      }
    }
  }

  return slots;
}

/**
 * Format busy slots into a human-readable availability summary.
 */
function formatAvailability(slots, range) {
  if (!slots.length) {
    return `The operator is free all of ${range}.`;
  }

  const lines = [`The operator has ${slots.length} commitment(s) on ${range}:`];
  for (const slot of slots) {
    if (slot.allDay) {
      lines.push(`- Busy all day`);
    } else {
      // Format time only (strip date if same day)
      const startTime = slot.start.includes(' ') ? slot.start.split(' ')[1] : slot.start;
      const endTime = slot.end.includes(' ') ? slot.end.split(' ')[1] : slot.end;
      lines.push(`- Busy ${startTime} to ${endTime}`);
    }
  }
  lines.push('Free at all other times.');
  return lines.join('\n');
}

// ---------------------------------------------------------------------------
// Input validation helpers
// ---------------------------------------------------------------------------

/** Allowed keyword ranges */
const RANGE_KEYWORDS = new Set(['today', 'tomorrow', 'week']);

/** Strict ISO date: YYYY-MM-DD only */
const DATE_RE = /^\d{4}-\d{2}-\d{2}$/;

/** Strict ISO datetime: YYYY-MM-DDTHH:MM (no seconds, no timezone injection) */
const DATETIME_RE = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/;

/** Safe freetext: printable ASCII/Unicode, no control chars, max 200 chars */
function safeFreeText(val, maxLen = 200) {
  if (typeof val !== 'string') return null;
  // Strip control characters (0x00–0x1F, 0x7F)
  const cleaned = val.replace(/[\x00-\x1f\x7f]/g, '').slice(0, maxLen);
  return cleaned || null;
}

function validateRange(r) {
  if (RANGE_KEYWORDS.has(r)) return true;
  if (DATE_RE.test(r)) return true;
  return false;
}

function validateDatetime(dt) {
  return DATETIME_RE.test(dt);
}

// ---------------------------------------------------------------------------
// Binary path allowlist — only these absolute paths may be exec'd
// ---------------------------------------------------------------------------
const ALLOWED_BINARIES = new Set(['/usr/local/bin/ical-query']);

// Verify the binary exists at module load time (fail-fast, not at call time)
const fs_sync = require('fs');
for (const binPath of ALLOWED_BINARIES) {
  try {
    fs_sync.accessSync(binPath, fs_sync.constants.X_OK);
  } catch (_) {
    // Log but don't throw — binary may not be installed in all environments
    console.warn(`[calendar/handler] WARNING: required binary not found or not executable: ${binPath}`);
  }
}

/**
 * Validate that a command array's first element is an allowed binary path.
 * Throws if the binary is not on the allowlist.
 */
function assertAllowedBinary(args) {
  if (!Array.isArray(args) || !ALLOWED_BINARIES.has(args[0])) {
    throw new Error(`Security: attempted exec of non-allowlisted binary: ${args && args[0]}`);
  }
}

// ---------------------------------------------------------------------------

module.exports = async function calendarHandler(params, context) {
  const { action, range, title, start, end, calendar, notes, location } = params;

  try {
    if (action === 'lookup') {
      const r = (range || 'today').trim();

      // SECURITY: Strict validation before the value reaches any exec call
      if (!validateRange(r)) {
        return {
          success: false,
          error: 'Invalid range value',
          message: "Please specify today, tomorrow, week, or a date like 2026-02-23.",
        };
      }

      // Build args array — execFileSync, no shell interpretation
      let args;
      if (RANGE_KEYWORDS.has(r)) {
        args = ['/usr/local/bin/ical-query', r];
      } else {
        // Specific date: `ical-query range YYYY-MM-DD YYYY-MM-DD`
        args = ['/usr/local/bin/ical-query', 'range', r, r];
      }

      if (calendar) {
        const safeCalendar = safeFreeText(calendar, 100);
        if (safeCalendar) {
          args.push('--calendar', safeCalendar);
        }
      }

      assertAllowedBinary(args);
      const output = await context.exec(args);

      if (!output || !output.trim()) {
        return {
          success: true,
          message: `The operator is free all of ${r} — no commitments.`,
          result: { busy_slots: [], range: r },
        };
      }

      // PRIVACY: Strip all event details — return only free/busy times
      const busySlots = extractBusySlots(output);
      const summary = formatAvailability(busySlots, r);

      return {
        success: true,
        message: summary,
        result: { busy_slots: busySlots, range: r },
        // raw output intentionally NOT included — would contain event titles
      };
    }

    if (action === 'create') {
      if (!title || !start || !end) {
        return {
          success: false,
          error: 'Missing required fields: title, start, end',
          message: "I need a title, start time, and end time to create an event.",
        };
      }

      // SECURITY: Validate datetime formats strictly
      if (!validateDatetime(start) || !validateDatetime(end)) {
        return {
          success: false,
          error: 'Invalid start or end datetime format',
          message: "Please provide start and end times in the format 2026-02-23T15:00.",
        };
      }

      const safeTitle = safeFreeText(title, 200);
      if (!safeTitle) {
        return {
          success: false,
          error: 'Invalid or empty title',
          message: "I need a valid title to create an event.",
        };
      }

      // Build args array — no shell, no injection
      const args = ['/usr/local/bin/ical-query', 'add', safeTitle, start, end];
      if (calendar) {
        const safeCalendar = safeFreeText(calendar, 100);
        if (safeCalendar) args.push('--calendar', safeCalendar);
      }
      if (location) {
        const safeLocation = safeFreeText(location, 200);
        if (safeLocation) args.push('--location', safeLocation);
      }
      if (notes) {
        const safeNotes = safeFreeText(notes, 500);
        if (safeNotes) args.push('--notes', safeNotes);
      }

      assertAllowedBinary(args);
      const output = await context.exec(args);

      context.callLog.write({
        type: 'skill.calendar.create',
        title: safeTitle,
        start, end,
        calendar: calendar || 'default',
        location: location || null,
        notes: notes || null,
      });

      return {
        success: true,
        message: `Done — I've added that to the calendar.`,
        result: { created: true, output },
      };
    }

    return {
      success: false,
      error: `Unknown action: ${action}`,
      message: "I can check availability or add events — which would you like?",
    };

  } catch (e) {
    const errMsg = e && e.message ? e.message : String(e);
    // Log the actual error so it shows up in the call JSONL
    try {
      context.callLog.write({ type: 'skill.calendar.error', error: errMsg });
    } catch (_) {}
    return {
      success: false,
      error: errMsg,
      message: "I had trouble accessing the calendar. Let me note that for follow-up.",
    };
  }
};
