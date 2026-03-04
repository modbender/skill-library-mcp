import { exec } from 'child_process';
import util from 'util';

const execPromise = util.promisify(exec);

// Pricing per 1M tokens { in, out }
// Order matters: specific keys should come before general keys (e.g., 'gpt-4o-mini' before 'gpt-4o')
const PRICING_TABLE = {
  // OpenAI
  'gpt-4o-mini': { in: 0.15, out: 0.60 },
  'gpt-4o': { in: 2.50, out: 10.00 },
  'o3-mini': { in: 1.10, out: 4.40 },
  'o1': { in: 15.00, out: 60.00 },

  // Anthropic
  'claude-3-5-sonnet': { in: 3.00, out: 15.00 },
  'claude-3-haiku': { in: 0.25, out: 1.25 },
  'claude-3-opus': { in: 15.00, out: 75.00 },

  // Google
  'gemini-1.5-pro': { in: 3.50, out: 10.50 },
  'gemini-1.5-flash': { in: 0.075, out: 0.30 },

  // DeepSeek
  'deepseek-chat': { in: 0.14, out: 0.28 },
  'deepseek-reasoner': { in: 0.55, out: 2.19 },

  // Legacy
  'gemini-3': { in: 3.00, out: 10.00 }, // Legacy Gemini 3 estimate
  'gpt-5.2': { in: 5.00, out: 15.00 }   // Legacy GPT-5.2 estimate
};

async function getSessions(limit) {
  try {
    const { stdout } = await execPromise(`openclaw sessions list --json --limit ${limit}`);
    const parsed = JSON.parse(stdout);
    return parsed.sessions || [];
  } catch (error) {
    console.error('Error fetching sessions:', error);
    throw new Error(`Failed to fetch sessions: ${error.message}`);
  }
}

export async function get_cost_report() {
  try {
    const sessions = await getSessions(100);
    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);

    const stats = {};

    for (const session of sessions) {
      // Check if updated in last 24h
      const updatedAt = new Date(session.updatedAt);
      if (updatedAt < oneDayAgo) continue;

      const model = session.model || 'unknown';
      if (!stats[model]) {
        stats[model] = { inputTokens: 0, outputTokens: 0, count: 0 };
      }

      stats[model].inputTokens += (session.inputTokens || 0);
      stats[model].outputTokens += (session.outputTokens || 0);
      stats[model].count += 1;
    }

    let report = "## 💰 Estimated Cost Report (Last 24h)\n\n";
    if (Object.keys(stats).length === 0) {
      return report + "No active sessions found in the last 24 hours.";
    }

    report += "| Model | Sessions | Input Tokens | Output Tokens | Est. Cost |\n";
    report += "| :--- | :---: | :---: | :---: | :---: |\n";

    let totalCost = 0;

    for (const [model, data] of Object.entries(stats)) {
      let cost = 0;
      const inM = data.inputTokens / 1_000_000;
      const outM = data.outputTokens / 1_000_000;
      const lowerModel = model.toLowerCase();

      // Find pricing
      let pricing = null;
      for (const [key, price] of Object.entries(PRICING_TABLE)) {
        if (lowerModel.includes(key)) {
          pricing = price;
          break; // Stop at first match (assumes table is ordered specific-to-general)
        }
      }

      if (pricing) {
        cost = (inM * pricing.in) + (outM * pricing.out);
      } else {
        cost = 0;
      }

      totalCost += cost;

      report += `| ${model} | ${data.count} | ${data.inputTokens.toLocaleString()} | ${data.outputTokens.toLocaleString()} | $${cost.toFixed(4)} |\n`;
    }

    report += `\n**Total Estimated Cost:** $${totalCost.toFixed(4)}`;
    return report;

  } catch (error) {
    return `Error generating cost report: ${error.message}`;
  }
}

export async function get_recent_errors() {
  let systemLogsOutput = "";
  let sessionErrorsOutput = "";

  // 1. System Logs (Journalctl)
  try {
    const { stdout } = await execPromise('journalctl --user -u openclaw-gateway -n 100 --no-pager');
    const lines = stdout.split('\n');
    const filteredLines = lines.filter(line => {
      const lower = line.toLowerCase();
      return lower.includes('error') || lower.includes('exception') || lower.includes('fail') || lower.includes('warn');
    });

    // Unique entries
    const uniqueLines = [...new Set(filteredLines)];
    // Limit to last 10
    const last10 = uniqueLines.slice(-10);

    if (last10.length > 0) {
      systemLogsOutput = last10.map(l => `- \`${l.trim()}\``).join('\n');
    } else {
      systemLogsOutput = "No recent error/warning logs found in journalctl.";
    }
  } catch (error) {
    systemLogsOutput = `Failed to retrieve system logs: ${error.message}`;
  }

  // 2. Session Errors (Secondary)
  try {
    const sessions = await getSessions(50);
    
    // Filter logic: lastStatus != 'ok' OR abortedLastRun is true
    const failedSessions = sessions.filter(s => {
      const statusNotOk = (s.lastStatus && s.lastStatus !== 'ok');
      const aborted = (s.abortedLastRun === true);
      return statusNotOk || aborted;
    });

    if (failedSessions.length > 0) {
      sessionErrorsOutput = failedSessions.map(s => 
        `- **${s.id}** (${s.title || 'Untitled'}): Status=${s.lastStatus || 'N/A'}, Aborted=${s.abortedLastRun || false}`
      ).join('\n');
    } else {
      sessionErrorsOutput = "No recent failed sessions found.";
    }
  } catch (error) {
    sessionErrorsOutput = `Error checking sessions: ${error.message}`;
  }

  // 3. Combined Output
  return `## 🖥️ System Logs (Journalctl)\n${systemLogsOutput}\n\n## 💥 Failed Sessions\n${sessionErrorsOutput}`;
}
