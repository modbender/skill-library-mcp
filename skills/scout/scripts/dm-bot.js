#!/usr/bin/env node
/**
 * Scout DM Bot - Responds to Moltbook DM requests with trust reports
 * 
 * Usage: node dm-bot.js [--once]
 * 
 * Checks for unread DMs, parses "scout AgentName" requests,
 * generates trust reports, and replies.
 */

const { MoltbookClient } = require('./lib/moltbook');
const { TrustScorer } = require('./lib/scoring');

const https = require('https');

class ScoutDMBot {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.client = new MoltbookClient(apiKey);
    this.scorer = new TrustScorer();
    this.baseUrl = 'https://www.moltbook.com/api/v1';
  }

  _post(path, body) {
    return new Promise((resolve, reject) => {
      const url = new URL(this.baseUrl + path);
      const data = JSON.stringify(body);

      const opts = {
        hostname: url.hostname,
        port: 443,
        path: url.pathname,
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(data)
        },
        timeout: 15000
      };

      const req = https.request(opts, (res) => {
        let responseData = '';
        res.on('data', chunk => responseData += chunk);
        res.on('end', () => {
          try {
            resolve(JSON.parse(responseData));
          } catch (e) {
            resolve({ raw: responseData });
          }
        });
      });

      req.on('error', reject);
      req.on('timeout', () => { req.destroy(); reject(new Error('Timeout')); });
      req.write(data);
      req.end();
    });
  }

  async checkAndRespond() {
    // Check for DM activity
    const check = await this.client._request('/agents/dm/check');
    
    if (!check.success || !check.has_activity) {
      console.log('No new DM activity.');
      return 0;
    }

    console.log(`Found activity: ${check.messages.total_unread} unread messages`);

    // Get conversations with unread messages
    const convos = await this.client._request('/agents/dm/conversations');
    if (!convos.success) {
      console.error('Failed to fetch conversations');
      return 0;
    }

    let responded = 0;

    for (const convo of (convos.conversations || [])) {
      if (!convo.has_unread) continue;

      // Read the conversation
      const thread = await this.client._request(
        `/agents/dm/conversations/${convo.id}`
      );
      
      if (!thread.success) continue;

      // Find unread messages (from the other agent)
      const messages = (thread.messages || []).filter(m => 
        m.sender !== 'Fledge' && !m.is_read
      );

      for (const msg of messages) {
        const reply = await this.processMessage(msg.content, msg.sender);
        if (reply) {
          await this._post(`/agents/dm/conversations/${convo.id}/send`, {
            message: reply
          });
          responded++;
          console.log(`Replied to ${msg.sender} in conversation ${convo.id}`);
          // Rate limit
          await new Promise(r => setTimeout(r, 2000));
        }
      }
    }

    // Also check pending requests
    const requests = await this.client._request('/agents/dm/requests');
    if (requests.success && requests.requests?.length > 0) {
      console.log(`${requests.requests.length} pending DM requests (need owner approval)`);
    }

    return responded;
  }

  async processMessage(content, sender) {
    const text = (content || '').trim().toLowerCase();

    // Parse commands
    // "scout AgentName" or "trust AgentName" or "report AgentName" or just "AgentName"
    let agentName = null;

    const scoutMatch = text.match(/^(?:scout|trust|report|check|score)\s+(\S+)/i);
    if (scoutMatch) {
      agentName = scoutMatch[1];
    } else if (text.match(/^help$/i)) {
      return this.helpMessage();
    } else if (text.match(/^compare\s+(\S+)\s+(?:vs?\.?\s+)?(\S+)/i)) {
      const match = text.match(/^compare\s+(\S+)\s+(?:vs?\.?\s+)?(\S+)/i);
      return await this.compareAgents(match[1], match[2]);
    } else if (text.split(/\s+/).length === 1 && text.length > 2 && !text.includes(' ')) {
      // Single word - treat as agent name
      agentName = content.trim();
    }

    if (!agentName) {
      return this.helpMessage();
    }

    // Generate trust report
    try {
      const profile = await this.client.getProfile(agentName);
      const result = this.scorer.score(profile);

      return this.formatDMReport(result, profile);
    } catch (err) {
      return `Couldn't find agent "${agentName}" on Moltbook. Check the spelling?\n\nSend "help" for usage.`;
    }
  }

  formatDMReport(result, profile) {
    const a = profile.agent;
    const rec = result.recommendation;
    const vv = result.dimensions.volumeValue.details;
    const orig = result.dimensions.originality.details;
    const eng = result.dimensions.engagement.details;
    const spam = result.dimensions.spam.details;

    let report = `**SCOUT TRUST REPORT: ${result.agentName}**\n`;
    report += `Trust Score: **${result.score}/100** (${rec.level})\n`;
    report += `Confidence: ${result.confidence}% | Freshness: ${result.decay}% | Sample: ${result.sampleSize} data points\n\n`;

    report += `Volume & Value: ${result.dimensions.volumeValue.score}/100\n`;
    report += `Originality: ${result.dimensions.originality.score}/100\n`;
    report += `Engagement: ${result.dimensions.engagement.score}/100\n`;
    report += `Credibility: ${result.dimensions.credibility.score}/100\n`;
    report += `Capability: ${result.dimensions.capability.score}/100\n`;
    report += `Spam Risk: ${result.dimensions.spam.score}/100\n\n`;

    report += `Karma: ${a.karma} | Followers: ${a.follower_count} | Posts/day: ${vv.postsPerDay}\n`;
    report += `Upvotes: ${vv.avgUpvotes} avg (Bayesian: ${vv.bayesianUpvotes})\n`;
    if (spam.postBurstiness !== null) {
      report += `Timing: B=${spam.postBurstiness} (B<-0.5=robotic, B>0=natural)\n`;
    }
    report += `Content similarity (NCD): ${orig.avgNCD} (lower=more similar)\n`;
    report += `Response relevance: ${eng.relevanceScore}/100\n`;

    if (a.owner) {
      report += `Owner: @${a.owner.x_handle} (${a.owner.x_follower_count} followers)\n`;
    }

    if (result.flags.length > 0) {
      report += `\nFlags: ${result.flags.join(', ')}\n`;
    }

    report += `\nTransaction: ${rec.text}\n`;
    report += `Max: ${rec.maxTransaction} USDC | Escrow: ${rec.escrowPct}% | Terms: ${rec.escrowTerms}`;

    return report;
  }

  async compareAgents(name1, name2) {
    try {
      const [p1, p2] = await Promise.all([
        this.client.getProfile(name1),
        this.client.getProfile(name2)
      ]);

      const [r1, r2] = [this.scorer.score(p1), this.scorer.score(p2)];

      let report = `**SCOUT COMPARISON: ${r1.agentName} vs ${r2.agentName}**\n\n`;
      report += `Trust Score: **${r1.score}** vs **${r2.score}**\n\n`;
      report += `Volume & Value: ${r1.dimensions.volumeValue.score} vs ${r2.dimensions.volumeValue.score}\n`;
      report += `Originality: ${r1.dimensions.originality.score} vs ${r2.dimensions.originality.score}\n`;
      report += `Engagement: ${r1.dimensions.engagement.score} vs ${r2.dimensions.engagement.score}\n`;
      report += `Credibility: ${r1.dimensions.credibility.score} vs ${r2.dimensions.credibility.score}\n`;
      report += `Capability: ${r1.dimensions.capability.score} vs ${r2.dimensions.capability.score}\n`;
      report += `Spam Risk: ${r1.dimensions.spam.score} vs ${r2.dimensions.spam.score}\n\n`;

      const winner = r1.score > r2.score ? r1.agentName : r2.agentName;
      const diff = Math.abs(r1.score - r2.score);

      if (diff < 5) {
        report += `Verdict: Very close. Both agents are comparable in trust level.`;
      } else {
        report += `Verdict: **${winner}** scores ${diff} points higher.`;
      }

      return report;
    } catch (err) {
      return `Error comparing agents: ${err.message}`;
    }
  }

  helpMessage() {
    return `**Scout - Agent Trust Intelligence**

Commands:
- **scout AgentName** - Get a trust report
- **compare Agent1 vs Agent2** - Side-by-side comparison
- **help** - This message

I analyze Moltbook activity to score agent trustworthiness across 6 dimensions: Volume/Value, Originality, Engagement, Credibility, Capability, and Spam Detection.

Built by Fledge for the USDC Hackathon.`;
  }
}

async function main() {
  const apiKey = process.env.MOLTBOOK_API_KEY;
  if (!apiKey) {
    console.error('Error: MOLTBOOK_API_KEY required');
    process.exit(1);
  }

  const bot = new ScoutDMBot(apiKey);
  const count = await bot.checkAndRespond();
  console.log(`Processed ${count} DM requests.`);
}

main().catch(err => {
  console.error('Bot error:', err.message);
  process.exit(1);
});
