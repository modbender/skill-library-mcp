/**
 * YIELD × OpenClaw / MoltBot Integration Example
 *
 * Shows how to wire YIELD into any OpenClaw skill handler.
 * Drop this into your bot and watch conversions compound.
 *
 * Zero dependencies. Copy-paste ready.
 */

import { YieldEngine } from '../src/index.js';

// ─── Initialize ──────────────────────────────────────────────────────────────

const yield_engine = new YieldEngine();

// ─── Message Handler ─────────────────────────────────────────────────────────

/**
 * Wrap your existing message handler with YIELD intelligence.
 *
 * @param {string} userMessage - Incoming user message
 * @param {string} conversationId - Unique conversation/chat ID
 * @param {Function} generateBotResponse - Your existing response generator
 * @returns {string} Enhanced bot response
 */
function handleMessageWithYield(userMessage, conversationId, generateBotResponse) {
  // Run YIELD analysis (< 1ms, zero API calls)
  const analysis = yield_engine.processMessage(userMessage, conversationId);

  // Log the yield dashboard (remove in production or send to analytics)
  console.log(`
╔══════════════════════════════════════════╗
║  YIELD DASHBOARD — ${conversationId.slice(0, 15).padEnd(15)}       ║
╠══════════════════════════════════════════╣
║  Trust:      ${'█'.repeat(Math.round(analysis.portfolio.trust * 20)).padEnd(20)} ${(analysis.portfolio.trust * 100).toFixed(0).padStart(3)}%  ║
║  Commitment: ${'█'.repeat(Math.round(analysis.portfolio.commitment * 20)).padEnd(20)} ${(analysis.portfolio.commitment * 100).toFixed(0).padStart(3)}%  ║
║  Urgency:    ${'█'.repeat(Math.round(analysis.portfolio.urgency * 20)).padEnd(20)} ${(analysis.portfolio.urgency * 100).toFixed(0).padStart(3)}%  ║
║  Curiosity:  ${'█'.repeat(Math.round(analysis.portfolio.curiosity * 20)).padEnd(20)} ${(analysis.portfolio.curiosity * 100).toFixed(0).padStart(3)}%  ║
║  Authority:  ${'█'.repeat(Math.round(analysis.portfolio.authority * 20)).padEnd(20)} ${(analysis.portfolio.authority * 100).toFixed(0).padStart(3)}%  ║
╠══════════════════════════════════════════╣
║  Total Yield: ${(analysis.totalYield * 100).toFixed(1).padStart(5)}%                       ║
║  Strategy:    ${analysis.strategy.padEnd(27)}║
║  Conversion:  ${analysis.conversionWindow ? 'WINDOW OPEN' : 'not yet'.padEnd(10)}                    ║
║  Inversion:   ${analysis.inversion ? 'WARNING' : 'none'.padEnd(10)}                       ║
╚══════════════════════════════════════════╝
  `);

  // Inject YIELD directive into your bot's context
  const enhancedPrompt = `
${analysis.contextualDirective}

User message: ${userMessage}
`;

  // Generate response with YIELD intelligence
  const response = generateBotResponse(enhancedPrompt, conversationId);

  return response;
}

// ─── Example: Sales Bot Conversation ─────────────────────────────────────────

function simulateSalesConversation() {
  const convId = 'sales-demo-001';

  // Simulated conversation showing YIELD in action
  const messages = [
    "Hi, I saw your product on Twitter",           // Cold open
    "What exactly does it do?",                      // Curiosity signal
    "Interesting. How is it different from Competitor X?",  // Comparison (still shopping)
    "Hmm, I've been struggling with that exact problem",   // Personal disclosure (trust building)
    "That's really cool, I didn't know that was possible", // Enthusiasm (compounding)
    "My team has been looking for something like this",    // Commitment signal
    "What's the pricing?",                           // BUYING SIGNAL — yield should spike
    "That's a bit more than I expected...",          // Objection (hedge time)
    "But honestly, we're wasting so much time on the manual process", // Self-urgency
    "Yeah, let's do it. How do I get started?",     // HARVEST TIME
  ];

  console.log('\n=== YIELD SALES CONVERSATION SIMULATION ===\n');

  for (const msg of messages) {
    console.log(`\n👤 User: "${msg}"`);
    const analysis = yield_engine.processMessage(msg, convId);

    console.log(`   Signals: [${analysis.signals.map(s => s.type).join(', ')}]`);
    console.log(`   Yield: ${(analysis.totalYield * 100).toFixed(1)}% | Strategy: ${analysis.strategy}`);

    if (analysis.conversionWindow) {
      console.log(`   *** CONVERSION WINDOW OPEN (strength: ${analysis.conversionStrength}) ***`);
    }
    if (analysis.inversion) {
      console.log(`   ⚠ YIELD INVERSION — ${analysis.turnsUntilAbandon} turns until abandon`);
    }
  }

  // Show final stats
  console.log('\n--- Engine Stats ---');
  console.log(yield_engine.getStats());
}

// ─── Example: System Prompt Injection (No-Code Approach) ─────────────────────

/**
 * For bots that use pure prompt engineering (no code runtime),
 * generate a YIELD-aware system prompt block.
 */
function generateYieldSystemPrompt(conversationId) {
  const state = yield_engine.peek(conversationId);
  if (!state) return '';

  return `
[YIELD CONVERSATIONAL INTELLIGENCE — ACTIVE]

Current Portfolio State:
- Trust: ${(state.portfolio.trust * 100).toFixed(0)}%
- Commitment: ${(state.portfolio.commitment * 100).toFixed(0)}%
- Urgency: ${(state.portfolio.urgency * 100).toFixed(0)}%
- Curiosity: ${(state.portfolio.curiosity * 100).toFixed(0)}%
- Authority: ${(state.portfolio.authority * 100).toFixed(0)}%

Total Yield: ${(state.totalYield * 100).toFixed(1)}%
Active Strategy: ${state.strategy}

${state.directive}

${state.conversionWindow.open ? '*** CONVERSION WINDOW IS OPEN — This is the optimal moment to present your offer. ***' : ''}
${state.inversion.inverted ? '*** WARNING: Yield inversion detected. Stop selling. Rebuild trust immediately. ***' : ''}

[END YIELD INTELLIGENCE]
`;
}

// ─── Run ─────────────────────────────────────────────────────────────────────

simulateSalesConversation();

export { handleMessageWithYield, generateYieldSystemPrompt };
