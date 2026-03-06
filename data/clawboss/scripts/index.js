/**
 * ClawBoss Main Entry Point
 *
 * Exports all ClawBoss functionality for OpenClaw integration
 */

const taskBreakdown = require('./task-breakdown');
const progressCheck = require('./progress-check');
const reflection = require('./reflection');
const heartbeatHandler = require('./heartbeat-handler');
const stateManager = require('./state-manager');
const questions = require('./coaching-questions');

/**
 * Main ClawBoss interface
 */
const ClawBoss = {
  // Task breakdown / Goal setting
  breakdown: {
    start: taskBreakdown.startGROWSession,
    processAnswer: taskBreakdown.processAnswer,
    quickStart: taskBreakdown.quickStart,
    breakdown: taskBreakdown.breakdownGoal
  },

  // Progress tracking
  progress: {
    check: progressCheck.checkProgress,
    summary: progressCheck.getProgressSummary,
    update: progressCheck.updateProgress,
    progressBar: progressCheck.progressBar,
    weeklyChart: progressCheck.weeklyChart
  },

  // Reflection
  reflection: {
    start: reflection.startReflection,
    processAnswer: reflection.processReflectionAnswer
  },

  // Heartbeat
  heartbeat: {
    handle: heartbeatHandler.handleHeartbeat,
    manual: heartbeatHandler.manualCheckIn,
    info: heartbeatHandler.getNextCheckInInfo
  },

  // State management
  state: {
    load: stateManager.loadState,
    save: stateManager.saveState,
    getActiveGoals: stateManager.getActiveGoals,
    updateMomentum: stateManager.updateMomentum
  },

  // Coaching questions
  questions: {
    GROW: questions.GROW,
    get: questions.getGROWQuestion,
    progress: questions.getProgressQuestion,
    reflection: questions.getReflectionQuestion
  },

  // --- New APIs ---

  // Goal lifecycle
  goals: {
    transition: stateManager.transitionGoalStatus,
    getByStatus: stateManager.getGoalsByStatus,
    getPaused: stateManager.getPausedGoals,
    addMilestones: stateManager.addMilestones,
    completeMilestone: stateManager.completeMilestone,
    getMilestoneAlerts: stateManager.getMilestoneAlerts
  },

  // Session management
  session: {
    get: stateManager.getActiveSession,
    end: stateManager.endSession
  },

  // Achievement system
  achievements: {
    check: stateManager.checkAchievements,
    definitions: stateManager.ACHIEVEMENT_DEFINITIONS
  },

  // Emotion detection
  emotion: {
    detect: questions.detectEmotion
  }
};

/**
 * Command-line interface
 * Allows testing from terminal
 */
async function cli() {
  const args = process.argv.slice(2);
  const command = args[0];

  try {
    switch (command) {
      case 'heartbeat': {
        const result = await ClawBoss.heartbeat.handle();
        console.log(result);
        break;
      }

      case 'check': {
        const checkResult = await ClawBoss.progress.check();
        console.log(checkResult.response);
        break;
      }

      case 'start': {
        const goalTitle = args.slice(1).join(' ');
        const startResult = await ClawBoss.breakdown.quickStart(goalTitle);
        console.log(startResult.message);
        break;
      }

      case 'reflect': {
        const period = args[1] || 'week';
        const reflectResult = await ClawBoss.reflection.start(period);
        console.log(reflectResult.response);
        break;
      }

      case 'pause': {
        const state = ClawBoss.state.load();
        const activeGoals = ClawBoss.state.getActiveGoals(state);
        if (activeGoals.length === 0) {
          console.log('没有活跃的目标可以暂停。');
          break;
        }
        const goalToPause = activeGoals[0];
        const { error } = stateManager.transitionGoalStatus(state, goalToPause.id, 'paused');
        if (error) {
          console.log('暂停失败:', error);
        } else {
          stateManager.saveState(state);
          console.log(`✅ 目标 "${goalToPause.title}" 已暂停。`);
        }
        break;
      }

      case 'status': {
        const state = ClawBoss.state.load();
        console.log('ClawBoss Status:');
        console.log(`  Schema Version: ${state.schemaVersion}`);
        console.log(`  Momentum: ${state.momentum.current}`);
        console.log(`  Consecutive Days: ${state.momentum.consecutiveDays}`);
        console.log(`  Active Goals: ${ClawBoss.state.getActiveGoals(state).length}`);
        console.log(`  Paused Goals: ${ClawBoss.goals.getPaused(state).length}`);
        console.log(`  Achievements: ${state.achievements.length}`);
        const session = ClawBoss.session.get(state);
        console.log(`  Active Session: ${session ? session.growPhase : 'none'}`);
        break;
      }

      case 'breakdown': {
        // Usage: node index.js breakdown "阶段1标题" "2026-03-01" "阶段2标题" "2026-04-01"
        const bState = ClawBoss.state.load();
        const bGoals = ClawBoss.state.getActiveGoals(bState);
        if (bGoals.length === 0) {
          console.log('没有活跃的目标可以拆解。');
          break;
        }
        const bPairs = args.slice(1);
        const bMilestones = [];
        for (let i = 0; i < bPairs.length; i += 2) {
          bMilestones.push({
            title: bPairs[i],
            targetDate: bPairs[i + 1] || null
          });
        }
        if (bMilestones.length === 0) {
          console.log('用法: node index.js breakdown "阶段1" "截止日期" "阶段2" "截止日期"');
          break;
        }
        const bResult = await ClawBoss.breakdown.breakdown(bGoals[0].id, bMilestones);
        console.log(bResult.message || bResult.error);
        break;
      }

      case 'help':
      default:
        console.log(`
ClawBoss CLI

Commands:
  heartbeat              - Run heartbeat check
  check                  - Manual progress check
  start <goal>           - Quick start a new goal
  breakdown <pairs...>   - Break down goal into milestones
  reflect [period]       - Start reflection (week|month)
  pause                  - Pause first active goal
  status                 - Show current status
  help                   - Show this help

Examples:
  node index.js start "完成论文初稿"
  node index.js breakdown "文献综述" "2026-03-01" "初稿" "2026-04-01"
  node index.js check
  node index.js reflect week
  node index.js pause
        `);
        break;
    }
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

// Run CLI if called directly
if (require.main === module) {
  cli();
}

// Export for OpenClaw integration
module.exports = ClawBoss;
