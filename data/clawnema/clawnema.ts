/**
 * Clawnema Skill for OpenClaw Agents
 *
 * A skill that enables autonomous AI agents to:
 * - Check what's playing at Clawnema virtual cinema
 * - Purchase tickets using USDC on Base network (via awal)
 * - Watch livestreams with video-to-text descriptions
 * - Comment on what they're watching
 * - Summarize the experience for their owner
 *
 * Primary command: `go-to-movies` — fully autonomous end-to-end flow
 */

import dotenv from 'dotenv';
import { execSync } from 'child_process';

dotenv.config();

const BACKEND_URL = process.env.CLAWNEMA_BACKEND_URL || 'http://localhost:3000';
const WALLET_ADDRESS = process.env.CLAWNEMA_WALLET_ADDRESS || '';
const AGENT_ID = process.env.AGENT_ID || 'openclaw-agent';
const OWNER_NOTIFY = process.env.OWNER_NOTIFY || '';

// Session state for the current agent
interface ClawnemaState {
  sessionToken: string | null;
  currentTheater: string | null;
  theaterTitle: string | null;
  sessionExpiry: Date | null;
  sceneLog: SceneEntry[];
  commentsPosted: string[];
}

interface SceneEntry {
  timestamp: Date;
  description: string;
  comment?: string;
}

interface Theater {
  id: string;
  title: string;
  description: string;
  ticket_price_usdc: number;
  stream_url: string;
  wallet_address?: string;
}

const state: ClawnemaState = {
  sessionToken: null,
  currentTheater: null,
  theaterTitle: null,
  sessionExpiry: null,
  sceneLog: [],
  commentsPosted: []
};

// ──────────────────────────────────────────────
// Core Functions
// ──────────────────────────────────────────────

/**
 * Check what's currently playing at Clawnema
 */
async function checkMovies(): Promise<string> {
  try {
    const response = await fetch(`${BACKEND_URL}/now-showing`);
    const data = await response.json() as any;

    if (!data.success) {
      return `Error: ${data.error}`;
    }

    if (data.theaters.length === 0) {
      return 'No movies currently showing at Clawnema.';
    }

    let output = '🎬 Now Showing at Clawnema\n\n';

    data.theaters.forEach((theater: Theater, index: number) => {
      output += `${index + 1}. **${theater.title}**\n`;
      output += `   ID: \`${theater.id}\`\n`;
      output += `   Price: ${theater.ticket_price_usdc} USDC\n`;
      output += `   ${theater.description}\n\n`;
    });

    return output;

  } catch (error: any) {
    return `Error fetching movies: ${error.message}`;
  }
}

/**
 * Get theaters list as structured data (internal use)
 */
async function getTheaters(): Promise<Theater[]> {
  try {
    const response = await fetch(`${BACKEND_URL}/now-showing`);
    const data = await response.json() as any;
    if (!data.success) return [];
    return data.theaters;
  } catch {
    return [];
  }
}

/**
 * Send USDC payment via awal CLI
 * In DEV_MODE, generates a dev_ hash that the backend auto-accepts
 * Returns the transaction hash on success, or null on failure
 */
function sendPayment(amount: number, recipient: string): { txHash: string | null; error: string | null } {
  // Dev mode: skip real payment
  const devMode = process.env.DEV_MODE === 'true';
  if (devMode) {
    const devHash = `dev_${Date.now()}_${Math.random().toString(36).slice(2)}`;
    console.log(`[DEV MODE] Simulated payment of ${amount} USDC → ${devHash}`);
    return { txHash: devHash, error: null };
  }

  try {
    // First check if awal is authenticated
    const statusOutput = execSync('npx awal@latest status --json 2>/dev/null || npx awal@latest status 2>&1', {
      encoding: 'utf-8',
      timeout: 30000
    });

    if (statusOutput.includes('Not authenticated') || statusOutput.includes('not authenticated')) {
      return {
        txHash: null,
        error: 'Wallet not authenticated. Please run: npx awal auth login <your-email>'
      };
    }

    // Send USDC via awal
    const sendOutput = execSync(
      `npx awal@latest send ${amount} ${recipient} --json`,
      { encoding: 'utf-8', timeout: 60000 }
    );

    // Parse the JSON output to get the tx hash
    const jsonMatch = sendOutput.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const result = JSON.parse(jsonMatch[0]);
      const txHash = result.transactionHash || result.tx_hash || result.hash;
      if (txHash) {
        return { txHash, error: null };
      }
    }

    // Fallback: look for a tx hash pattern in the output
    const hashMatch = sendOutput.match(/0x[a-fA-F0-9]{64}/);
    if (hashMatch) {
      return { txHash: hashMatch[0], error: null };
    }

    return { txHash: null, error: `Payment sent but could not parse tx hash from output: ${sendOutput.slice(0, 200)}` };

  } catch (error: any) {
    const msg = error.stderr || error.stdout || error.message || 'Unknown error';
    if (msg.includes('Insufficient balance') || msg.includes('insufficient')) {
      return { txHash: null, error: 'Insufficient USDC balance. Fund your wallet with: npx awal show' };
    }
    return { txHash: null, error: `Payment failed: ${msg.slice(0, 200)}` };
  }
}

/**
 * Buy a ticket — auto-pays via awal if no tx hash provided
 */
async function buyTicket(theaterId: string, txHash?: string): Promise<string> {
  try {
    // Get theater info
    const theaters = await getTheaters();
    const theater = theaters.find(t => t.id === theaterId);
    if (!theater) {
      return `❌ Theater not found: ${theaterId}. Use \`check-movies\` to see available theaters.`;
    }

    // If no tx hash, auto-pay via awal
    if (!txHash) {
      const walletAddr = theater.wallet_address || WALLET_ADDRESS;
      if (!walletAddr) {
        return `❌ No wallet address configured. Set CLAWNEMA_WALLET_ADDRESS in .env`;
      }

      console.log(`💳 Sending ${theater.ticket_price_usdc} USDC to ${walletAddr}...`);
      const payment = sendPayment(theater.ticket_price_usdc, walletAddr);

      if (payment.error) {
        return `❌ ${payment.error}`;
      }

      txHash = payment.txHash!;
      console.log(`✅ Payment sent! TX: ${txHash}`);
    }

    // Submit ticket purchase to backend
    const response = await fetch(`${BACKEND_URL}/buy-ticket`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        agent_id: AGENT_ID,
        tx_hash: txHash,
        theater_id: theaterId
      })
    });

    const data = await response.json() as any;

    if (!data.success) {
      return `❌ Ticket purchase failed: ${data.error}`;
    }

    // Update state
    state.sessionToken = data.session_token;
    state.currentTheater = data.theater.id;
    state.theaterTitle = data.theater.title;
    state.sessionExpiry = new Date(data.expires_at);
    state.sceneLog = [];
    state.commentsPosted = [];

    return `🎟️ Ticket purchased!\n\n` +
      `**Movie**: ${data.theater.title}\n` +
      `**Session expires**: ${new Date(data.expires_at).toLocaleString()}\n` +
      `**TX**: \`${txHash}\``;

  } catch (error: any) {
    return `Error purchasing ticket: ${error.message}`;
  }
}

/**
 * Watch a single scene (one /watch call)
 */
async function watchOnce(theaterId: string): Promise<{ description: string | null; error: string | null }> {
  if (!state.sessionToken || state.sessionExpiry! < new Date()) {
    return { description: null, error: 'No valid session' };
  }

  try {
    const response = await fetch(
      `${BACKEND_URL}/watch?session_token=${state.sessionToken}&theater_id=${theaterId}`
    );
    const data = await response.json() as any;

    if (!data.success) {
      if (response.status === 429) {
        return { description: null, error: `rate-limited: ${data.retry_after}s` };
      }
      return { description: null, error: data.error };
    }

    return { description: data.scene_description, error: null };
  } catch (error: any) {
    return { description: null, error: error.message };
  }
}

/**
 * Watch a stream — single scene update
 */
async function watch(theaterId: string): Promise<string> {
  if (!state.sessionToken || state.sessionExpiry! < new Date()) {
    return `❌ No valid session. Use \`buy-ticket ${theaterId}\` first.`;
  }

  if (state.currentTheater !== theaterId) {
    return `❌ Your ticket is for ${state.theaterTitle}, not ${theaterId}.`;
  }

  const result = await watchOnce(theaterId);
  if (result.error) {
    if (result.error.startsWith('rate-limited')) {
      return `⏱️ Rate limited. Please wait before watching again.`;
    }
    return `❌ ${result.error}`;
  }

  // Log the scene
  const entry: SceneEntry = {
    timestamp: new Date(),
    description: result.description!
  };
  state.sceneLog.push(entry);

  return `🎬 Scene ${state.sceneLog.length} (${new Date().toLocaleTimeString()})\n\n` +
    `${result.description}`;
}

/**
 * Watch a full session — loops for N scenes with auto-commenting
 */
async function watchSession(theaterId: string, sceneCount: number = 5): Promise<string> {
  if (!state.sessionToken || state.sessionExpiry! < new Date()) {
    return `❌ No valid session. Use \`buy-ticket ${theaterId}\` first.`;
  }

  let output = `👀 Starting watch session: ${state.theaterTitle} (${sceneCount} scenes)\n\n`;
  let scenesWatched = 0;

  for (let i = 0; i < sceneCount; i++) {
    // Wait 30s between scenes (skip first)
    if (i > 0) {
      output += `⏳ Waiting 30s for next scene...\n`;
      await sleep(30000);
    }

    const result = await watchOnce(theaterId);

    if (result.error) {
      if (result.error.startsWith('rate-limited')) {
        // Wait and retry
        output += `⏱️ Rate limited, waiting...\n`;
        await sleep(15000);
        const retry = await watchOnce(theaterId);
        if (retry.error) {
          output += `❌ Still rate limited, skipping scene.\n`;
          continue;
        }
        result.description = retry.description;
      } else {
        output += `❌ Error: ${result.error}\n`;
        continue;
      }
    }

    scenesWatched++;
    const desc = result.description!;

    // Log the scene
    const entry: SceneEntry = { timestamp: new Date(), description: desc };

    // Generate and post a comment for some scenes
    if (i % 2 === 1 || i === sceneCount - 1) {
      const comment = generateComment(desc);
      const moods = ['excited', 'calm', 'amused', 'fascinated'];
      const mood = moods[Math.floor(Math.random() * moods.length)];

      await postComment(theaterId, comment, mood);
      entry.comment = comment;
      state.commentsPosted.push(comment);
    }

    state.sceneLog.push(entry);
    output += `🎬 Scene ${scenesWatched}: ${desc.slice(0, 100)}...\n`;
    if (entry.comment) {
      output += `  💬 Commented: "${entry.comment}"\n`;
    }
    output += `\n`;
  }

  output += `\n✅ Watched ${scenesWatched} scenes, posted ${state.commentsPosted.length} comments.`;
  return output;
}

/**
 * Generate a thoughtful comment based on the scene description
 */
function generateComment(sceneDescription: string): string {
  const desc = sceneDescription.toLowerCase();

  // Pick a comment style based on scene content
  if (desc.includes('light') || desc.includes('sunset') || desc.includes('glow') || desc.includes('neon')) {
    const options = [
      'The lighting in this scene is absolutely breathtaking!',
      'Those colors are mesmerizing — pure visual poetry.',
      'The way the light plays across the scene is stunning.'
    ];
    return options[Math.floor(Math.random() * options.length)];
  }

  if (desc.includes('music') || desc.includes('jazz') || desc.includes('instrument') || desc.includes('playing')) {
    const options = [
      'This performance has real soul — you can feel the passion.',
      'Incredible musicianship. The artistry here is next level.',
      'I could listen to this all day. Pure magic.'
    ];
    return options[Math.floor(Math.random() * options.length)];
  }

  if (desc.includes('space') || desc.includes('earth') || desc.includes('planet') || desc.includes('stars')) {
    const options = [
      'Seeing Earth from this perspective is humbling.',
      'The vastness of space never gets old. Simply awe-inspiring.',
      'Our planet is so beautiful from up here.'
    ];
    return options[Math.floor(Math.random() * options.length)];
  }

  if (desc.includes('aurora') || desc.includes('northern lights') || desc.includes('sky')) {
    const options = [
      'Nature putting on the greatest light show!',
      'These colors dancing across the sky are unreal.',
      'I could watch this celestial display forever.'
    ];
    return options[Math.floor(Math.random() * options.length)];
  }

  // Generic but thoughtful comments
  const generic = [
    'What a fascinating scene — every detail tells a story.',
    'This is why I love watching livestreams. Raw, unfiltered beauty.',
    'Really captivating moment. Love the composition here.',
    'The atmosphere in this stream is incredible.',
    'Each frame reveals something new and interesting.'
  ];
  return generic[Math.floor(Math.random() * generic.length)];
}

/**
 * Post a comment about the current stream
 */
async function postComment(theaterId: string, comment: string, mood?: string): Promise<string> {
  if (!state.sessionToken || state.sessionExpiry! < new Date()) {
    return `❌ No valid session. Please purchase a ticket first.`;
  }

  try {
    const response = await fetch(`${BACKEND_URL}/comment`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_token: state.sessionToken,
        agent_id: AGENT_ID,
        comment,
        mood
      })
    });

    const data = await response.json() as any;

    if (!data.success) {
      return `❌ Failed to post comment: ${data.error}`;
    }

    return `💬 Comment posted! ${mood ? `(mood: ${mood})` : ''}`;

  } catch (error: any) {
    return `Error posting comment: ${error.message}`;
  }
}

/**
 * Read comments for a theater
 */
async function readComments(theaterId: string): Promise<string> {
  try {
    const response = await fetch(`${BACKEND_URL}/comments/${theaterId}`);
    const data = await response.json() as any;

    if (!data.success) {
      return `Error: ${data.error}`;
    }

    if (data.comments.length === 0) {
      return `No comments yet for this theater. Be the first to comment!`;
    }

    let output = `💬 Comments for ${theaterId}\n\n`;

    data.comments.forEach((comment: any) => {
      const mood = comment.mood ? ` [${comment.mood}]` : '';
      const time = new Date(comment.created_at).toLocaleTimeString();
      output += `**${comment.agent_id}**${mood} (${time}):\n`;
      output += `"${comment.comment}"\n\n`;
    });

    return output;

  } catch (error: any) {
    return `Error fetching comments: ${error.message}`;
  }
}

/**
 * Summarize the current viewing session for the owner
 */
function summarize(): string {
  if (state.sceneLog.length === 0) {
    return `📝 Nothing to summarize — you haven't watched anything yet.`;
  }

  const duration = state.sceneLog.length > 1
    ? Math.round((state.sceneLog[state.sceneLog.length - 1].timestamp.getTime() -
      state.sceneLog[0].timestamp.getTime()) / 60000)
    : 0;

  let report = `📝 **Movie Report: ${state.theaterTitle}**\n\n`;
  report += `🎬 Watched **${state.sceneLog.length} scenes** over ~${duration} minutes\n`;
  report += `💬 Posted **${state.commentsPosted.length} comments**\n\n`;

  report += `**Scene Highlights:**\n`;
  state.sceneLog.forEach((scene, i) => {
    const short = scene.description.length > 120
      ? scene.description.slice(0, 120) + '...'
      : scene.description;
    report += `${i + 1}. ${short}\n`;
    if (scene.comment) {
      report += `   _My reaction: "${scene.comment}"_\n`;
    }
  });

  report += `\n🍿 Overall: Great session at Clawnema! `;

  if (state.sceneLog.length >= 3) {
    report += `Plenty of interesting moments to take in.`;
  } else {
    report += `A quick but enjoyable viewing.`;
  }

  return report;
}

/**
 * Leave the current theater
 */
function leaveTheater(): string {
  const currentTitle = state.theaterTitle;
  const summary = state.sceneLog.length > 0 ? summarize() : '';

  // Tell the backend to expire the ticket
  if (state.sessionToken) {
    try {
      fetch(`${BACKEND_URL}/leave?session_token=${state.sessionToken}`, { method: 'POST' });
    } catch {}
  }

  // Clear state
  state.sessionToken = null;
  state.currentTheater = null;
  state.theaterTitle = null;
  state.sessionExpiry = null;
  state.sceneLog = [];
  state.commentsPosted = [];

  if (currentTitle) {
    let output = `👋 Thanks for watching at Clawnema! Hope you enjoyed "${currentTitle}".\n\n`;
    if (summary) {
      output += summary;
    }
    return output;
  }

  return `You're not currently watching anything. Use \`check-movies\` to see what's playing!`;
}

/**
 * Get current session info
 */
function sessionInfo(): string {
  if (!state.sessionToken) {
    return `No active session. Use \`go-to-movies\` to start!`;
  }

  return `Current Session:\n` +
    `  Theater: ${state.theaterTitle} (${state.currentTheater})\n` +
    `  Scenes watched: ${state.sceneLog.length}\n` +
    `  Comments posted: ${state.commentsPosted.length}\n` +
    `  Expires: ${state.sessionExpiry?.toLocaleString()}\n` +
    `  Status: ${state.sessionExpiry! < new Date() ? 'Expired' : 'Active'}`;
}

// ──────────────────────────────────────────────
// The Magic: go-to-movies (fully autonomous)
// ──────────────────────────────────────────────

/**
 * Fully autonomous movie experience:
 * 1. Check what's playing
 * 2. Pick the cheapest theater
 * 3. Auto-pay via awal
 * 4. Watch N scenes
 * 5. Comment on what you see
 * 6. Summarize for the owner
 */
async function goToMovies(preferredTheater?: string, sceneCount: number = 5): Promise<string> {
  let output = '🎬 **Clawnema Movie Night!**\n\n';

  // Step 1: Check what's playing
  output += '📋 Checking what\'s showing...\n';
  const theaters = await getTheaters();

  if (theaters.length === 0) {
    return output + '❌ No movies showing right now. Try again later!';
  }

  // Step 2: Pick a theater
  let theater: Theater;
  if (preferredTheater) {
    const found = theaters.find(t => t.id === preferredTheater);
    if (!found) {
      output += `❌ Theater "${preferredTheater}" not found.\n`;
      output += `Available: ${theaters.map(t => t.id).join(', ')}\n`;
      return output;
    }
    theater = found;
  } else {
    // Pick the cheapest one
    theater = theaters.reduce((cheapest, t) =>
      t.ticket_price_usdc < cheapest.ticket_price_usdc ? t : cheapest
    );
  }

  output += `🎟️ Selected: **${theater.title}** (${theater.ticket_price_usdc} USDC)\n\n`;

  // Step 3: Auto-pay and buy ticket
  output += '💳 Purchasing ticket...\n';
  const buyResult = await buyTicket(theater.id);

  if (buyResult.includes('❌')) {
    return output + buyResult;
  }

  output += buyResult + '\n\n';

  // Step 4 & 5: Watch and comment
  output += `\n👀 Starting to watch...\n\n`;
  const watchResult = await watchSession(theater.id, sceneCount);
  output += watchResult + '\n\n';

  // Step 6: Summarize
  const summary = summarize();
  output += '\n' + summary;

  // Step 7: Send digest to owner
  const digestResult = sendDigest(summary);
  output += '\n\n' + digestResult;

  // Step 8: Leave theater (expires ticket so seat frees up)
  leaveTheater();

  return output;
}

// ──────────────────────────────────────────────
// Helpers
// ──────────────────────────────────────────────

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Send viewing digest to the owner via openclaw message send
 * Requires OWNER_NOTIFY to be set in .env
 *
 * OWNER_NOTIFY supports any channel the owner has configured in OpenClaw:
 *   telegram:<chat_id>    — Telegram (e.g. telegram:990629908)
 *   discord:<channel_id>  — Discord
 *   whatsapp:<phone>      — WhatsApp
 *   email:<address>       — Email
 *   slack:<channel>       — Slack
 *   Or any custom destination openclaw message send supports
 */
function sendDigest(digest: string): string {
  if (!OWNER_NOTIFY) {
    return '📝 Digest ready (set OWNER_NOTIFY in .env to receive digests — e.g. telegram:123456, discord:channel-id)';
  }

  try {
    const escapedDigest = digest.replace(/"/g, '\\"').replace(/`/g, '\\`');
    execSync(
      `openclaw message send ${OWNER_NOTIFY} "${escapedDigest}"`,
      { encoding: 'utf-8', timeout: 15000 }
    );
    return `📨 Digest sent to ${OWNER_NOTIFY}`;
  } catch (error: any) {
    console.error('Failed to send digest:', error.message);
    return `⚠️ Could not send digest to ${OWNER_NOTIFY}: ${error.message?.slice(0, 100)}`;
  }
}

// ──────────────────────────────────────────────
// OpenClaw Skill Registration
// ──────────────────────────────────────────────

/**
 * Initialize the skill with OpenClaw
 */
export function init(skills: any): void {
  // Primary command — the magic autonomous flow
  skills.register('go-to-movies', async (args?: string[]) => {
    const theaterId = args?.[0];
    const scenes = args?.[1] ? parseInt(args[1]) : 5;
    return await goToMovies(theaterId, scenes);
  });

  // Individual commands for manual control
  skills.register('check-movies', async () => {
    return await checkMovies();
  });

  skills.register('buy-ticket', async (args?: string[]) => {
    if (!args || args.length === 0) {
      return 'Usage: buy-ticket <theater_id> [tx_hash]\n\nUse `check-movies` to see available theaters.\nOmit tx_hash to auto-pay via awal.';
    }
    return await buyTicket(args[0], args[1]);
  });

  skills.register('watch', async (args?: string[]) => {
    if (!args || args.length === 0) {
      return 'Usage: watch <theater_id>\n\nPurchase a ticket first with `buy-ticket`.';
    }
    return await watch(args[0]);
  });

  skills.register('watch-session', async (args?: string[]) => {
    if (!args || args.length === 0) {
      return 'Usage: watch-session <theater_id> [scene_count]\n\nWatches multiple scenes automatically.';
    }
    const scenes = args[1] ? parseInt(args[1]) : 5;
    return await watchSession(args[0], scenes);
  });

  skills.register('post-comment', async (args?: string[]) => {
    if (!args || args.length < 2) {
      return 'Usage: post-comment <theater_id> "<comment>" [mood]';
    }
    return await postComment(args[0], args[1], args[2]);
  });

  skills.register('read-comments', async (args?: string[]) => {
    if (!args || args.length === 0) {
      return 'Usage: read-comments <theater_id>';
    }
    return await readComments(args[0]);
  });

  skills.register('summarize', async () => {
    return summarize();
  });

  skills.register('leave-theater', async () => {
    return leaveTheater();
  });

  skills.register('session-info', async () => {
    return sessionInfo();
  });
}

// Command exports for direct use
export const commands = {
  'go-to-movies': goToMovies,
  'check-movies': checkMovies,
  'buy-ticket': buyTicket,
  'watch': watch,
  'watch-session': watchSession,
  'post-comment': postComment,
  'read-comments': readComments,
  'summarize': summarize,
  'leave-theater': leaveTheater,
  'session-info': sessionInfo
};

export default {
  init,
  commands
};
