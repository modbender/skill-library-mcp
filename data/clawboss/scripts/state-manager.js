/**
 * ClawBoss State Manager
 *
 * Handles reading/writing clawboss-state.json and task files
 */

const fs = require('fs');
const path = require('path');

const STATE_FILE = 'memory/clawboss-state.json';
const TASKS_DIR = 'memory/tasks';

const SCHEMA_VERSION = 2;

const SESSION_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes

// --- Achievement definitions ---
const ACHIEVEMENT_DEFINITIONS = [
  { id: 'first-goal', name: '起步者', description: '创建了第一个目标', icon: '🌱' },
  { id: 'streak-3', name: '三连胜', description: '连续 3 天完成任务', icon: '🔥' },
  { id: 'streak-7', name: '周冠军', description: '连续 7 天完成任务', icon: '💪' },
  { id: 'streak-30', name: '月度之星', description: '连续 30 天完成任务', icon: '⭐' },
  { id: 'first-archive', name: '收割者', description: '归档了第一个目标', icon: '🏆' },
  { id: 'five-goals', name: '多面手', description: '累计创建 5 个目标', icon: '🎯' },
  { id: 'first-reflection', name: '思考者', description: '完成了第一次周反思', icon: '🪞' },
  { id: 'comeback', name: '回归者', description: '从危机模式恢复', icon: '🦅' }
];

// --- Valid goal status transitions ---
const VALID_TRANSITIONS = {
  active: ['paused', 'archived', 'abandoned'],
  paused: ['active', 'abandoned']
};

/**
 * Sanitize a filename to prevent path traversal and illegal characters
 */
function sanitizeFilename(name) {
  return name
    .replace(/\.\./g, '_')
    .replace(/[/\\:*?"<>|]/g, '_')
    .substring(0, 100)
    .trim() || 'untitled';
}

/**
 * Get the workspace path
 */
function getWorkspacePath() {
  const home = process.env.HOME || process.env.USERPROFILE;
  return path.join(home, '.openclaw', 'workspace');
}

/**
 * Create initial state structure
 */
function createInitialState() {
  return {
    schemaVersion: SCHEMA_VERSION,
    user: {
      name: "",
      timezone: "Asia/Shanghai",
      workingHours: {
        start: 9,
        end: 22
      },
      preferences: {
        checkInFrequency: "2x-daily",
        coachingStyle: "balanced",
        enableWeeklyReview: true
      }
    },
    momentum: {
      current: "medium",
      consecutiveDays: 0,
      lastSuccess: null,
      trend: "stable"
    },
    goals: [],
    checkIns: {
      lastMorning: null,
      lastEvening: null,
      lastWeekly: null
    },
    insights: {
      bestWorkTime: null,
      commonBlockers: [],
      successPatterns: []
    },
    activeSession: null,
    achievements: [],
    _errors: []
  };
}

/**
 * Validate and migrate state from older versions
 */
function validateAndMigrateState(state) {
  const initial = createInitialState();

  // Merge top-level keys
  for (const key of Object.keys(initial)) {
    if (state[key] === undefined) {
      state[key] = initial[key];
    }
  }

  // Merge nested user fields
  if (typeof state.user !== 'object' || state.user === null) {
    state.user = initial.user;
  } else {
    for (const key of Object.keys(initial.user)) {
      if (state.user[key] === undefined) {
        state.user[key] = initial.user[key];
      }
    }
    // Migrate string workingHours to numeric
    if (typeof state.user.workingHours === 'object' && state.user.workingHours !== null) {
      if (typeof state.user.workingHours.start === 'string') {
        state.user.workingHours.start = parseInt(state.user.workingHours.start, 10) || 9;
      }
      if (typeof state.user.workingHours.end === 'string') {
        state.user.workingHours.end = parseInt(state.user.workingHours.end, 10) || 22;
      }
    } else {
      state.user.workingHours = initial.user.workingHours;
    }
    if (typeof state.user.preferences !== 'object' || state.user.preferences === null) {
      state.user.preferences = initial.user.preferences;
    } else {
      for (const key of Object.keys(initial.user.preferences)) {
        if (state.user.preferences[key] === undefined) {
          state.user.preferences[key] = initial.user.preferences[key];
        }
      }
    }
  }

  // Merge nested momentum fields
  if (typeof state.momentum !== 'object' || state.momentum === null) {
    state.momentum = initial.momentum;
  } else {
    for (const key of Object.keys(initial.momentum)) {
      if (state.momentum[key] === undefined) {
        state.momentum[key] = initial.momentum[key];
      }
    }
  }

  // Merge nested checkIns fields
  if (typeof state.checkIns !== 'object' || state.checkIns === null) {
    state.checkIns = initial.checkIns;
  } else {
    for (const key of Object.keys(initial.checkIns)) {
      if (state.checkIns[key] === undefined) {
        state.checkIns[key] = initial.checkIns[key];
      }
    }
  }

  // Merge nested insights fields
  if (typeof state.insights !== 'object' || state.insights === null) {
    state.insights = initial.insights;
  } else {
    for (const key of Object.keys(initial.insights)) {
      if (state.insights[key] === undefined) {
        state.insights[key] = initial.insights[key];
      }
    }
  }

  // Ensure arrays
  if (!Array.isArray(state.goals)) state.goals = [];
  if (!Array.isArray(state.achievements)) state.achievements = [];
  if (!Array.isArray(state._errors)) state._errors = [];

  // Clean expired session
  if (state.activeSession) {
    const elapsed = Date.now() - new Date(state.activeSession.updatedAt || state.activeSession.startedAt).getTime();
    if (elapsed > SESSION_TIMEOUT_MS) {
      state.activeSession = null;
    }
  }

  state.schemaVersion = SCHEMA_VERSION;
  return state;
}

/**
 * Load ClawBoss state
 */
function loadState() {
  const statePath = path.join(getWorkspacePath(), STATE_FILE);

  if (!fs.existsSync(statePath)) {
    return createInitialState();
  }

  try {
    const data = fs.readFileSync(statePath, 'utf-8');
    const state = JSON.parse(data);
    return validateAndMigrateState(state);
  } catch (error) {
    console.error('Error loading state:', error);
    return createInitialState();
  }
}

/**
 * Save ClawBoss state (atomic write)
 */
function saveState(state) {
  const statePath = path.join(getWorkspacePath(), STATE_FILE);
  const tmpPath = statePath + `.tmp.${process.pid}`;

  try {
    const dir = path.dirname(statePath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    fs.writeFileSync(tmpPath, JSON.stringify(state, null, 2));
    fs.renameSync(tmpPath, statePath);
    return true;
  } catch (error) {
    console.error('Error saving state:', error);
    try { fs.unlinkSync(tmpPath); } catch (_) {}
    return false;
  }
}

/**
 * Update momentum based on result
 */
function updateMomentum(state, result) {
  const { momentum } = state;

  if (result === 'success') {
    momentum.consecutiveDays++;
    momentum.lastSuccess = new Date().toISOString();

    if (momentum.consecutiveDays >= 5) {
      momentum.current = 'high';
      momentum.trend = 'rising';
    } else if (momentum.consecutiveDays >= 2) {
      momentum.current = 'medium';
      momentum.trend = 'rising';
    }
  } else if (result === 'miss') {
    momentum.consecutiveDays = Math.max(0, momentum.consecutiveDays - 1);

    if (momentum.consecutiveDays === 0) {
      momentum.current = 'low';
      momentum.trend = 'falling';
    } else if (momentum.consecutiveDays < 3) {
      momentum.current = 'medium';
      momentum.trend = 'stable';
    }
  }

  // Crisis mode: 7+ days no success
  const daysSinceSuccess = momentum.lastSuccess
    ? Math.floor((Date.now() - new Date(momentum.lastSuccess).getTime()) / (1000 * 60 * 60 * 24))
    : 999;

  if (daysSinceSuccess > 7) {
    momentum.current = 'crisis';
  }

  return state;
}

/**
 * Add a new goal (with sanitized filename)
 */
function addGoal(state, goalData) {
  const goalId = `goal-${Date.now()}`;
  const safeName = sanitizeFilename(goalData.title);
  const goal = {
    id: goalId,
    title: goalData.title,
    status: 'active',
    createdAt: new Date().toISOString().split('T')[0],
    targetDate: goalData.targetDate || null,
    priority: goalData.priority || 'medium',
    taskFile: `${TASKS_DIR}/${safeName}.md`,
    milestones: []
  };

  state.goals.push(goal);
  return { state, goalId };
}

/**
 * Add milestones to a goal
 * milestones: [{ title, targetDate?, description? }]
 */
function addMilestones(state, goalId, milestones) {
  const goal = state.goals.find(g => g.id === goalId);
  if (!goal) return { state, error: '目标不存在' };
  if (!Array.isArray(goal.milestones)) goal.milestones = [];

  for (const ms of milestones) {
    goal.milestones.push({
      id: `ms-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
      title: ms.title,
      description: ms.description || '',
      targetDate: ms.targetDate || null,
      status: 'pending',    // pending | completed
      completedAt: null,
      notifiedUpcoming: false,
      notifiedOverdue: false
    });
  }

  return { state, error: null };
}

/**
 * Complete a milestone
 */
function completeMilestone(state, goalId, milestoneId) {
  const goal = state.goals.find(g => g.id === goalId);
  if (!goal) return { state, error: '目标不存在' };

  const ms = (goal.milestones || []).find(m => m.id === milestoneId);
  if (!ms) return { state, error: '里程碑不存在' };

  ms.status = 'completed';
  ms.completedAt = new Date().toISOString();
  return { state, error: null };
}

/**
 * Get milestones that need attention (upcoming in 1 day or overdue)
 */
function getMilestoneAlerts(state) {
  const now = new Date();
  const oneDayMs = 24 * 60 * 60 * 1000;
  const alerts = [];

  for (const goal of state.goals) {
    if (goal.status !== 'active') continue;
    for (const ms of (goal.milestones || [])) {
      if (ms.status === 'completed' || !ms.targetDate) continue;

      const target = new Date(ms.targetDate);
      const diff = target.getTime() - now.getTime();

      if (diff < 0 && !ms.notifiedOverdue) {
        alerts.push({
          type: 'overdue',
          goalId: goal.id,
          goalTitle: goal.title,
          milestone: ms,
          daysOverdue: Math.ceil(-diff / oneDayMs)
        });
      } else if (diff >= 0 && diff <= oneDayMs && !ms.notifiedUpcoming) {
        alerts.push({
          type: 'upcoming',
          goalId: goal.id,
          goalTitle: goal.title,
          milestone: ms,
          hoursLeft: Math.round(diff / (60 * 60 * 1000))
        });
      }
    }
  }

  return alerts;
}

/**
 * Mark milestone alerts as notified so we don't re-alert
 */
function markMilestoneNotified(state, goalId, milestoneId, alertType) {
  const goal = state.goals.find(g => g.id === goalId);
  if (!goal) return state;
  const ms = (goal.milestones || []).find(m => m.id === milestoneId);
  if (!ms) return state;

  if (alertType === 'upcoming') ms.notifiedUpcoming = true;
  if (alertType === 'overdue') ms.notifiedOverdue = true;
  return state;
}

/**
 * Get active goals
 */
function getActiveGoals(state) {
  return state.goals.filter(g => g.status === 'active');
}

/**
 * Get goals by status
 */
function getGoalsByStatus(state, status) {
  return state.goals.filter(g => g.status === status);
}

/**
 * Get paused goals
 */
function getPausedGoals(state) {
  return getGoalsByStatus(state, 'paused');
}

/**
 * Transition goal status with validation
 */
function transitionGoalStatus(state, goalId, newStatus) {
  const goal = state.goals.find(g => g.id === goalId);
  if (!goal) {
    return { state, error: '目标不存在' };
  }

  const allowed = VALID_TRANSITIONS[goal.status];
  if (!allowed || !allowed.includes(newStatus)) {
    return { state, error: `无法从 "${goal.status}" 转为 "${newStatus}"` };
  }

  goal.status = newStatus;
  goal[`${newStatus}At`] = new Date().toISOString();

  // Record insight when abandoning
  if (newStatus === 'abandoned') {
    addInsight(state, 'commonBlockers', `放弃目标: ${goal.title}`);
  }

  return { state, error: null };
}

/**
 * Update goal status (legacy — kept for backward compat)
 */
function updateGoalStatus(state, goalId, status) {
  const goal = state.goals.find(g => g.id === goalId);
  if (goal) {
    goal.status = status;
  }
  return state;
}

/**
 * Record check-in timestamp
 */
function recordCheckIn(state, type) {
  state.checkIns[`last${type.charAt(0).toUpperCase() + type.slice(1)}`] = new Date().toISOString();
  return state;
}

/**
 * Check if checked today
 */
function checkedToday(type, state) {
  const lastCheck = state.checkIns[`last${type.charAt(0).toUpperCase() + type.slice(1)}`];
  if (!lastCheck) return false;

  const lastCheckDate = new Date(lastCheck).toDateString();
  const today = new Date().toDateString();

  return lastCheckDate === today;
}

/**
 * Load task file
 */
function loadTaskFile(taskPath) {
  const fullPath = path.join(getWorkspacePath(), taskPath);

  if (!fs.existsSync(fullPath)) {
    return null;
  }

  try {
    return fs.readFileSync(fullPath, 'utf-8');
  } catch (error) {
    console.error('Error loading task file:', error);
    return null;
  }
}

/**
 * Save task file (atomic write)
 */
function saveTaskFile(taskPath, content) {
  const fullPath = path.join(getWorkspacePath(), taskPath);
  const tmpPath = fullPath + `.tmp.${process.pid}`;
  const dir = path.dirname(fullPath);

  // Ensure directory exists
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  try {
    fs.writeFileSync(tmpPath, content);
    fs.renameSync(tmpPath, fullPath);
    return true;
  } catch (error) {
    console.error('Error saving task file:', error);
    try { fs.unlinkSync(tmpPath); } catch (_) {}
    return false;
  }
}

/**
 * Create task file from template
 */
function createTaskFile(goalData) {
  const template = `# ${goalData.title}

**创建时间：** ${new Date().toISOString().split('T')[0]}
**目标日期：** ${goalData.targetDate || '待定'}
**状态：** 🟢 进行中
**优先级：** ${goalData.priority || '中'}

---

## 🎯 目标 (Goal)

### 最终目标
${goalData.description || '待补充'}

### 为什么重要？
${goalData.motivation || '待补充'}

### 成功标准
- [ ] 标准 1
- [ ] 标准 2

---

## 📍 现状 (Reality)

### 当前进展
待评估

### 已有资源
-

### 主要障碍
-

---

## 🛤️ 行动计划 (Options → Will)

### 第一阶段
- [ ] 步骤 1
- [ ] 步骤 2

---

## 📝 每日记录

### ${new Date().toISOString().split('T')[0]}
**计划：**
**实际：**
**反思：**
**明天调整：**

---

## 💡 经验教训

- ✅ **有效的：**
- ❌ **无效的：**
- 🔧 **改进：**

---

## 📊 进度追踪

**总体进度：** ░░░░░░░░░░░░░░░░░░░░ 0%

**本周目标：**
**本周实际：**

**下周目标：**
`;

  return template;
}

/**
 * Add insight
 */
function addInsight(state, category, insight) {
  if (!state.insights[category]) {
    state.insights[category] = [];
  }

  if (!state.insights[category].includes(insight)) {
    state.insights[category].push(insight);
  }

  return state;
}

/**
 * Get days since last success
 */
function daysSinceLastSuccess(state) {
  if (!state.momentum.lastSuccess) return 999;

  const last = new Date(state.momentum.lastSuccess);
  const now = new Date();
  return Math.floor((now - last) / (1000 * 60 * 60 * 24));
}

// --- Session CRUD ---

/**
 * Start a new GROW session for a goal
 */
function startSession(state, goalId) {
  state.activeSession = {
    goalId,
    growPhase: 'goal',
    questionsAsked: 0,
    startedAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
  return state;
}

/**
 * Get active session (or null if expired/missing)
 */
function getActiveSession(state) {
  if (!state.activeSession) return null;

  const elapsed = Date.now() - new Date(state.activeSession.updatedAt || state.activeSession.startedAt).getTime();
  if (elapsed > SESSION_TIMEOUT_MS) {
    state.activeSession = null;
    return null;
  }
  return state.activeSession;
}

/**
 * Advance session to next phase
 */
function advanceSession(state) {
  if (!state.activeSession) return state;

  const sequence = ['goal', 'reality', 'options', 'will', 'complete'];
  const idx = sequence.indexOf(state.activeSession.growPhase);

  if (idx === -1 || idx >= sequence.length - 1) {
    state.activeSession.growPhase = 'complete';
  } else {
    state.activeSession.growPhase = sequence[idx + 1];
  }

  state.activeSession.questionsAsked++;
  state.activeSession.updatedAt = new Date().toISOString();
  return state;
}

/**
 * End the current session
 */
function endSession(state) {
  state.activeSession = null;
  return state;
}

// --- Achievement system ---

/**
 * Check and return newly unlocked achievements
 */
function checkAchievements(state) {
  const unlocked = [];
  const existing = new Set(state.achievements.map(a => a.id));

  for (const def of ACHIEVEMENT_DEFINITIONS) {
    if (existing.has(def.id)) continue;

    let earned = false;
    switch (def.id) {
      case 'first-goal':
        earned = state.goals.length >= 1;
        break;
      case 'streak-3':
        earned = state.momentum.consecutiveDays >= 3;
        break;
      case 'streak-7':
        earned = state.momentum.consecutiveDays >= 7;
        break;
      case 'streak-30':
        earned = state.momentum.consecutiveDays >= 30;
        break;
      case 'first-archive':
        earned = state.goals.some(g => g.status === 'archived');
        break;
      case 'five-goals':
        earned = state.goals.length >= 5;
        break;
      case 'first-reflection':
        earned = state.checkIns.lastWeekly !== null;
        break;
      case 'comeback':
        earned = state.momentum.current !== 'crisis' && state.insights.commonBlockers.some(b => b.includes('放弃'));
        break;
    }

    if (earned) {
      const achievement = { ...def, unlockedAt: new Date().toISOString() };
      state.achievements.push(achievement);
      unlocked.push(achievement);
    }
  }

  return unlocked;
}

/**
 * Record an error (keep last 10)
 */
function recordError(state, error) {
  if (!Array.isArray(state._errors)) state._errors = [];
  state._errors.push({
    message: error.message || String(error),
    timestamp: new Date().toISOString()
  });
  state._errors = state._errors.slice(-10);
  return state;
}

module.exports = {
  loadState,
  saveState,
  createInitialState,
  validateAndMigrateState,
  sanitizeFilename,
  updateMomentum,
  addGoal,
  addMilestones,
  completeMilestone,
  getMilestoneAlerts,
  markMilestoneNotified,
  getActiveGoals,
  getGoalsByStatus,
  getPausedGoals,
  transitionGoalStatus,
  updateGoalStatus,
  recordCheckIn,
  checkedToday,
  loadTaskFile,
  saveTaskFile,
  createTaskFile,
  addInsight,
  daysSinceLastSuccess,
  startSession,
  getActiveSession,
  advanceSession,
  endSession,
  checkAchievements,
  recordError,
  ACHIEVEMENT_DEFINITIONS
};
