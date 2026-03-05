/**
 * Autoplay Daemon Loop
 *
 * Core game loop with mid-round re-evaluation.
 *
 * Game mechanics:
 * - Last vote in a round wins the direction (not highest bid)
 * - Voting in the last 5s triggers: round extends 5s + minBid doubles
 * - Payout is per vote count, not cumulative amount spent
 * - All-pay auction: everyone pays regardless of outcome
 */

import { loadSettings, loadDaemonState, saveDaemonState } from '../lib/config.mjs';
import { getGameState, getBalance, submitVote, isAuthenticated } from '../lib/api.mjs';
import { parseGameState, getTeamById, getStrategy } from 'snake-rodeo-agents';
import { sendTelegram, formatVote, formatGameEnd, formatTeamSwitch, formatError, formatWarning } from '../lib/telegram.mjs';
import { logToFile, isDaemonRunning } from '../lib/process.mjs';

async function log(message, settings) {
  if (settings.logToConsole) {
    console.log(message);
  }
  if (settings.logToTelegram && settings.telegramChatId) {
    await sendTelegram(message);
  }
  logToFile(message);
}

export async function runAutoplay(options = {}) {
  const settings = { ...loadSettings(), ...options };
  let state = loadDaemonState();

  state.startedAt = Date.now();
  saveDaemonState(state);

  const strategy = getStrategy(settings.strategy, settings.strategyOptions?.[settings.strategy]);

  console.log(`=== Snake Daemon Started ===`);
  console.log(`Strategy: ${strategy.name}`);
  console.log(`Server: ${settings.server}`);
  console.log(`Telegram: ${settings.telegramChatId || 'disabled'}`);
  console.log(`Poll interval: ${settings.pollIntervalMs}ms`);
  console.log(`Mid-round monitoring: enabled`);
  console.log(``);

  logToFile(`Daemon started: strategy=${strategy.name}, server=${settings.server}`);

  let lastRound = state.lastRound;
  let currentTeam = state.currentTeam;
  let inGame = false;

  // Mid-round tracking (reset each round)
  let roundVote = null;
  let roundSpend = 0;
  let roundVoteCount = 0;

  while (true) {
    try {
      if (!isDaemonRunning()?.running) {
        console.log('PID file removed, shutting down...');
        break;
      }

      state = loadDaemonState();

      if (state.paused) {
        await sleep(settings.pollIntervalMs);
        continue;
      }

      if (!isAuthenticated()) {
        logToFile('Not authenticated, waiting...');
        await sleep(5000);
        continue;
      }

      const rawState = await getGameState();
      if (rawState.error) {
        if (rawState.error === 'AUTH_MISSING' || rawState.error === 'AUTH_EXPIRED') {
          logToFile(`Auth error: ${rawState.error}`);
          await sleep(5000);
          continue;
        }
      }

      const parsed = parseGameState(rawState);

      if (!parsed) {
        if (inGame) {
          logToFile('Game ended (no state)');
          inGame = false;
        }
        await sleep(settings.pollIntervalMs);
        continue;
      }

      // Game just started
      if (!inGame && parsed.active) {
        inGame = true;
        currentTeam = null;
        lastRound = -1;
        roundVote = null;
        roundSpend = 0;
        roundVoteCount = 0;
        strategy.onGameStart?.(parsed, state);
        logToFile('New game started');
      }

      // Game ended
      if (!parsed.active && parsed.winner && inGame) {
        const winnerTeam = getTeamById(parsed, parsed.winner);
        const didWin = currentTeam === parsed.winner;

        state.gamesPlayed++;
        if (didWin) state.wins++;
        saveDaemonState(state);

        await log(formatGameEnd(winnerTeam, didWin), settings);
        strategy.onGameEnd?.(parsed, state, didWin);

        inGame = false;
        currentTeam = null;
        lastRound = -1;
        roundVote = null;
        roundSpend = 0;
        roundVoteCount = 0;
        await sleep(settings.pollIntervalMs);
        continue;
      }

      if (!parsed.active) {
        await sleep(settings.pollIntervalMs);
        continue;
      }

      // --- New round ---
      if (parsed.round !== lastRound) {
        if (lastRound >= 0) {
          strategy.onRoundEnd?.(parsed, state);
        }

        roundVote = null;
        roundSpend = 0;
        roundVoteCount = 0;
        lastRound = parsed.round;

        const balance = await getBalance();
        const vote = strategy.computeVote(parsed, balance, {
          ...state, currentTeam, roundSpend, roundVoteCount,
        });

        if (!vote || vote.skip) {
          if (vote?.reason) {
            logToFile(`Round ${parsed.round}: skipped (${vote.reason})`);
          }
          await sleep(settings.pollIntervalMs);
          continue;
        }

        if (vote.team.id !== currentTeam) {
          const prevTeam = currentTeam;
          currentTeam = vote.team.id;
          await log(formatTeamSwitch(prevTeam, vote.team, vote.reason), settings);
        }

        const submitted = await trySubmitVote(vote, parsed, balance, state, currentTeam, settings);
        if (submitted) {
          roundVote = vote;
          roundSpend += vote.amount;
          roundVoteCount++;
        }

        await sleep(settings.pollIntervalMs);
        continue;
      }

      // --- Same round: mid-round monitoring ---
      // Check if our direction was overridden by another player
      if (roundVote && parsed.currentDirection !== roundVote.direction) {
        const balance = await getBalance();
        const maxRoundBudgetPct = settings.maxRoundBudgetPct ?? 0.2;
        const maxRoundBudget = balance * maxRoundBudgetPct;
        const budgetRemaining = maxRoundBudget - roundSpend;

        if (balance >= parsed.minBid && budgetRemaining >= parsed.minBid) {
          const counter = strategy.shouldCounterBid(
            parsed, balance,
            {
              ...state, currentTeam,
              roundSpend, roundVoteCount,
              roundBudgetRemaining: budgetRemaining,
            },
            roundVote
          );

          if (counter) {
            if (counter.team.id !== currentTeam) {
              const prevTeam = currentTeam;
              currentTeam = counter.team.id;
              await log(formatTeamSwitch(prevTeam, counter.team, counter.reason), settings);
            }

            const submitted = await trySubmitVote(counter, parsed, balance, state, currentTeam, settings);
            if (submitted) {
              roundVote = counter;
              roundSpend += counter.amount;
              roundVoteCount++;
            }
          } else {
            logToFile(`Round ${parsed.round}: overridden → ${parsed.currentDirection}, not countering`);
            roundVote = null; // stop checking this round
          }
        }
      }

      process.stdout.write('.');

    } catch (e) {
      logToFile(`Error: ${e.message}`);
      console.error(`Error: ${e.message}`);
    }

    // Poll faster when we have an active vote to monitor (2s),
    // otherwise use configured interval
    const interval = roundVote ? Math.max(settings.pollIntervalMs, 2000) : settings.pollIntervalMs;
    await sleep(interval);
  }

  logToFile('Daemon stopped');
  console.log('Daemon stopped');
}

async function trySubmitVote(vote, parsed, balance, state, currentTeam, settings) {
  try {
    await submitVote(vote.direction, vote.team.id, vote.amount);

    state.votesPlaced++;
    state.currentTeam = currentTeam;
    state.lastRound = parsed.round;
    saveDaemonState(state);

    const newBalance = balance - vote.amount;
    await log(
      formatVote(parsed.round, vote.direction, vote.team, vote.amount, newBalance, parsed.teams, vote.reason),
      settings
    );
    return true;

  } catch (e) {
    const errorMsg = e.message || String(e);
    if (errorMsg.includes('already active')) {
      logToFile(`Round ${parsed.round}: direction already active`);
    } else {
      await log(formatError(`Vote failed: ${errorMsg}`), settings);
    }
    return false;
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
