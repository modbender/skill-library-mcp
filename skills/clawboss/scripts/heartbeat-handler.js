/**
 * Heartbeat Handler - Automatic check-ins
 *
 * Determines when and how to check in with the user.
 * Uses Intl.DateTimeFormat for timezone-aware scheduling (zero dependencies).
 */

const stateManager = require('./state-manager');
const progressCheck = require('./progress-check');
const reflection = require('./reflection');
const questions = require('./coaching-questions');

/**
 * Get current hour in the user's timezone using Intl API
 */
function getCurrentHour(timezone) {
  try {
    const fmt = new Intl.DateTimeFormat('en-US', {
      hour: 'numeric',
      hour12: false,
      timeZone: timezone
    });
    return parseInt(fmt.format(new Date()), 10);
  } catch (_) {
    // Fallback: use system local time
    return new Date().getHours();
  }
}

/**
 * Get current day-of-week (0=Sun) in the user's timezone
 */
function getCurrentDayOfWeek(timezone) {
  try {
    const fmt = new Intl.DateTimeFormat('en-US', {
      weekday: 'short',
      timeZone: timezone
    });
    const dayStr = fmt.format(new Date());
    const map = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
    return map[dayStr] ?? new Date().getDay();
  } catch (_) {
    return new Date().getDay();
  }
}

/**
 * Check if current hour falls within working hours
 */
function isWithinWorkingHours(hour, workingHours) {
  return hour >= workingHours.start && hour < workingHours.end;
}

/**
 * Check if it's morning check-in time (first hour of working day)
 */
function isMorningWindow(hour, workingHours) {
  return hour >= workingHours.start && hour < workingHours.start + 1;
}

/**
 * Check if it's evening check-in time (last 2-3 hours of working day)
 */
function isEveningWindow(hour, workingHours) {
  const eveningStart = workingHours.end - 3;
  return hour >= eveningStart && hour < workingHours.end;
}

/**
 * Check if it's Sunday evening (for weekly reflection)
 */
function isSundayEveningWindow(dayOfWeek, hour, workingHours) {
  return dayOfWeek === 0 && isEveningWindow(hour, workingHours);
}

/**
 * Main heartbeat handler - called by OpenClaw heartbeat system
 */
async function handleHeartbeat() {
  const state = stateManager.loadState();

  try {
    const tz = state.user.timezone || 'Asia/Shanghai';
    const workingHours = state.user.workingHours || { start: 9, end: 22 };
    const hour = getCurrentHour(tz);
    const dayOfWeek = getCurrentDayOfWeek(tz);

    // Outside working hours — stay silent
    if (!isWithinWorkingHours(hour, workingHours)) {
      return 'HEARTBEAT_OK';
    }

    // Check if user has any active goals
    const activeGoals = stateManager.getActiveGoals(state);
    if (activeGoals.length === 0) {
      return handleNoGoalsHeartbeat(state);
    }

    // Morning check-in
    if (isMorningWindow(hour, workingHours) && !stateManager.checkedToday('morning', state)) {
      return await handleMorningCheckIn(state);
    }

    // Evening check-in
    if (isEveningWindow(hour, workingHours) && !stateManager.checkedToday('evening', state)) {
      return await handleEveningCheckIn(state);
    }

    // Weekly reflection (Sunday evening)
    if (isSundayEveningWindow(dayOfWeek, hour, workingHours) && !checkedThisWeek('weekly', state)) {
      return await handleWeeklyReflection(state);
    }

    // Milestone alerts — proactive communication at key plan nodes
    const milestoneAlerts = stateManager.getMilestoneAlerts(state);
    if (milestoneAlerts.length > 0) {
      return handleMilestoneAlerts(state, milestoneAlerts);
    }

    // Crisis intervention (7+ days no success)
    const daysSinceSuccess = stateManager.daysSinceLastSuccess(state);
    if (daysSinceSuccess > 7 && shouldInterventionCheck(state)) {
      return await handleCrisisIntervention(state, daysSinceSuccess);
    }

    // Default: stay quiet
    return 'HEARTBEAT_OK';

  } catch (error) {
    console.error('Heartbeat handler error:', error);
    // Record error to state instead of silently swallowing
    stateManager.recordError(state, error);
    stateManager.saveState(state);
    return 'HEARTBEAT_OK';
  }
}

/**
 * Handle heartbeat when user has no active goals
 */
function handleNoGoalsHeartbeat(state) {
  // Only check once a day
  const lastCheck = state.checkIns.lastMorning;
  if (lastCheck) {
    const lastCheckDate = new Date(lastCheck).toDateString();
    const today = new Date().toDateString();
    if (lastCheckDate === today) {
      return 'HEARTBEAT_OK';
    }
  }

  // Light check-in
  stateManager.recordCheckIn(state, 'morning');
  stateManager.saveState(state);

  return '早上好，今天过得怎么样？有什么想做的事可以跟我聊聊。';
}

/**
 * Morning check-in
 */
async function handleMorningCheckIn(state) {
  // Record check-in
  stateManager.recordCheckIn(state, 'morning');
  stateManager.saveState(state);

  // Get progress check with morning context
  const result = await progressCheck.checkProgress({
    timeOfDay: 'morning'
  });

  return result.response;
}

/**
 * Evening check-in
 */
async function handleEveningCheckIn(state) {
  // Record check-in
  stateManager.recordCheckIn(state, 'evening');
  stateManager.saveState(state);

  // Get progress check with evening context
  const result = await progressCheck.checkProgress({
    timeOfDay: 'evening'
  });

  return result.response;
}

/**
 * Weekly reflection
 */
async function handleWeeklyReflection(state) {
  // Record check-in
  stateManager.recordCheckIn(state, 'weekly');
  stateManager.saveState(state);

  const result = await reflection.startReflection('week');

  return result.response;
}

/**
 * Gentle check-in when there's been a long gap
 */
async function handleCrisisIntervention(state, daysSinceSuccess) {
  const persona = state.user.preferences.coachingStyle || 'balanced';
  const personaTone = questions.getPersonaTone(persona, 'crisis');

  if (personaTone) {
    const greeting = questions.pickRandom(personaTone.greeting);
    return greeting;
  }

  return '好久不见，最近怎么样？不管在忙什么，有空的时候随时找我聊。';
}

/**
 * Handle milestone alerts — proactive caring check-in
 * Uses persona-aware messaging to feel like a real person
 */
function handleMilestoneAlerts(state, alerts) {
  const persona = state.user.preferences.coachingStyle || 'balanced';

  const parts = [];

  for (const alert of alerts) {
    const vars = {
      goal: alert.goalTitle,
      milestone: alert.milestone.title,
      days: alert.daysOverdue,
      hours: alert.hoursLeft
    };
    parts.push(questions.getMilestoneMessage(persona, alert.type, vars));
    stateManager.markMilestoneNotified(state, alert.goalId, alert.milestone.id, alert.type);
  }

  stateManager.saveState(state);
  return parts.join('\n\n');
}

/**
 * Check if checked this week
 */
function checkedThisWeek(type, state) {
  const lastCheck = state.checkIns[`last${type.charAt(0).toUpperCase() + type.slice(1)}`];
  if (!lastCheck) return false;

  const lastCheckDate = new Date(lastCheck);
  const now = new Date();

  // Get start of this week (Monday)
  const startOfWeek = new Date(now);
  startOfWeek.setDate(now.getDate() - now.getDay() + 1);
  startOfWeek.setHours(0, 0, 0, 0);

  return lastCheckDate >= startOfWeek;
}

/**
 * Should do crisis intervention check
 */
function shouldInterventionCheck(state) {
  // Check at most once every 3 days during crisis
  const lastMorning = state.checkIns.lastMorning;
  if (!lastMorning) return true;

  const lastCheck = new Date(lastMorning);
  const daysSinceCheck = Math.floor((Date.now() - lastCheck) / (1000 * 60 * 60 * 24));

  return daysSinceCheck >= 3;
}

/**
 * Manual check-in trigger (called by user or skill)
 */
async function manualCheckIn(type = 'general') {
  const state = stateManager.loadState();

  if (type === 'morning') {
    return await handleMorningCheckIn(state);
  } else if (type === 'evening') {
    return await handleEveningCheckIn(state);
  } else if (type === 'weekly') {
    return await handleWeeklyReflection(state);
  } else {
    // General progress check
    const result = await progressCheck.checkProgress();
    return result.response;
  }
}

/**
 * Get next check-in time info (timezone-aware)
 */
function getNextCheckInInfo() {
  const state = stateManager.loadState();
  const tz = state.user.timezone || 'Asia/Shanghai';
  const workingHours = state.user.workingHours || { start: 9, end: 22 };
  const hour = getCurrentHour(tz);

  let nextCheckIn = '';
  let nextTime = '';

  if (hour < workingHours.start) {
    nextCheckIn = 'morning';
    nextTime = `${String(workingHours.start).padStart(2, '0')}:00`;
  } else if (hour < workingHours.end - 3) {
    nextCheckIn = 'evening';
    nextTime = `${String(workingHours.end - 3).padStart(2, '0')}:00`;
  } else {
    nextCheckIn = 'morning';
    nextTime = `明天 ${String(workingHours.start).padStart(2, '0')}:00`;
  }

  return {
    next: nextCheckIn,
    time: nextTime,
    lastMorning: state.checkIns.lastMorning,
    lastEvening: state.checkIns.lastEvening,
    lastWeekly: state.checkIns.lastWeekly
  };
}

module.exports = {
  handleHeartbeat,
  manualCheckIn,
  getNextCheckInInfo
};
