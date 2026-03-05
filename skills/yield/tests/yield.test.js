/**
 * YIELD Test Suite
 *
 * Tests the full pipeline: signal detection → portfolio management →
 * strategy selection → yield compounding and inversion detection.
 *
 * Run: node --test tests/yield.test.js
 */

import { describe, it } from 'node:test';
import assert from 'node:assert/strict';

import { YieldEngine, detectSignals, analyzeMessage } from '../src/index.js';
import { Portfolio } from '../src/portfolio.js';
import { selectStrategy } from '../src/strategy.js';

// ─── Signal Detection Tests ──────────────────────────────────────────────────

describe('Signal Detection', () => {
  it('detects agreement signals', () => {
    const signals = detectSignals('Yes, absolutely!');
    const types = signals.map(s => s.type);
    assert.ok(types.includes('AGREEMENT'), 'Should detect AGREEMENT');
  });

  it('detects question signals', () => {
    const signals = detectSignals('How does this work?');
    const types = signals.map(s => s.type);
    assert.ok(types.includes('QUESTION'), 'Should detect QUESTION');
  });

  it('detects buying signals', () => {
    const signals = detectSignals('How much does it cost?');
    const types = signals.map(s => s.type);
    assert.ok(types.includes('BUYING'), 'Should detect BUYING');
  });

  it('detects objection signals', () => {
    const signals = detectSignals("That's too expensive for our budget");
    const types = signals.map(s => s.type);
    assert.ok(types.includes('OBJECTION'), 'Should detect OBJECTION');
  });

  it('detects enthusiasm signals', () => {
    const signals = detectSignals('This is amazing!! Game changer!');
    const types = signals.map(s => s.type);
    assert.ok(types.includes('ENTHUSIASM'), 'Should detect ENTHUSIASM');
  });

  it('detects personal disclosure signals', () => {
    const signals = detectSignals('I feel like we have been struggling with this for months');
    const types = signals.map(s => s.type);
    assert.ok(types.includes('PERSONAL'), 'Should detect PERSONAL');
  });

  it('detects frustration signals', () => {
    const signals = detectSignals('This is terrible, it still does not work');
    const types = signals.map(s => s.type);
    assert.ok(types.includes('FRUSTRATION'), 'Should detect FRUSTRATION');
  });

  it('detects hesitation signals', () => {
    const signals = detectSignals('Maybe... I need to think about it');
    const types = signals.map(s => s.type);
    assert.ok(types.includes('HESITATION'), 'Should detect HESITATION');
  });

  it('detects time pressure signals', () => {
    const signals = detectSignals('We need this by Friday, it is urgent');
    const types = signals.map(s => s.type);
    assert.ok(types.includes('TIME_PRESSURE'), 'Should detect TIME_PRESSURE');
  });

  it('detects gratitude signals', () => {
    const signals = detectSignals('Thank you so much, this was incredibly helpful');
    const types = signals.map(s => s.type);
    assert.ok(types.includes('GRATITUDE'), 'Should detect GRATITUDE');
  });

  it('detects meta-signals from message length compression', () => {
    const history = [
      'This is a really detailed question about how your product works and integrates',
      'I have been evaluating several tools and yours looks promising for our team',
      'Can you tell me more about the enterprise features and pricing tiers?',
    ];
    const signals = detectSignals('ok', history);
    const types = signals.map(s => s.type);
    assert.ok(types.includes('ENGAGEMENT_DECAY'), 'Should detect ENGAGEMENT_DECAY');
  });

  it('returns empty array for empty input', () => {
    const signals = detectSignals('');
    assert.equal(signals.length, 0);
  });

  it('returns empty array for null input', () => {
    const signals = detectSignals(null);
    assert.equal(signals.length, 0);
  });

  it('detects multiple signals in one message', () => {
    const signals = detectSignals('Yes absolutely! How much does it cost? This is amazing!');
    assert.ok(signals.length >= 2, `Expected 2+ signals, got ${signals.length}`);
  });
});

// ─── Portfolio Tests ─────────────────────────────────────────────────────────

describe('Portfolio', () => {
  it('initializes with default values', () => {
    const portfolio = new Portfolio();
    const state = portfolio.getState();
    assert.ok(state.assets.trust > 0, 'Trust should start above zero');
    assert.ok(state.assets.curiosity > 0, 'Curiosity should start above zero');
    assert.equal(state.messageCount, 0);
  });

  it('increases trust on agreement signals', () => {
    const portfolio = new Portfolio();
    const initial = portfolio.assets.trust;
    portfolio.applySignals([{
      type: 'AGREEMENT',
      assets: { trust: 0.06, commitment: 0.10 },
      confidence: 0.8,
    }]);
    assert.ok(portfolio.assets.trust > initial, 'Trust should increase');
  });

  it('compounds trust on repeated positive signals', () => {
    const portfolio = new Portfolio();

    // Apply trust signals multiple times
    const deltas = [];
    for (let i = 0; i < 5; i++) {
      const before = portfolio.assets.trust;
      portfolio.applySignals([{
        type: 'AGREEMENT',
        assets: { trust: 0.06 },
        confidence: 0.8,
      }]);
      deltas.push(portfolio.assets.trust - before);
    }

    // Later deltas should be larger due to compounding
    assert.ok(
      deltas[4] > deltas[0],
      'Trust gains should compound (later gains > earlier gains)'
    );
  });

  it('decays urgency when not reinforced', () => {
    const portfolio = new Portfolio();

    // Set urgency high
    portfolio.applySignals([{
      type: 'TIME_PRESSURE',
      assets: { urgency: 0.30 },
      confidence: 0.8,
    }]);
    const afterBoost = portfolio.assets.urgency;

    // Send a message without urgency signals
    portfolio.applySignals([{
      type: 'QUESTION',
      assets: { curiosity: 0.10 },
      confidence: 0.8,
    }]);

    assert.ok(
      portfolio.assets.urgency < afterBoost,
      'Urgency should decay when not reinforced'
    );
  });

  it('calculates total yield using weighted geometric mean', () => {
    const portfolio = new Portfolio();
    const yield_ = portfolio.calculateTotalYield();
    assert.ok(yield_ >= 0, 'Yield should be >= 0');
    assert.ok(yield_ <= 1, 'Yield should be <= 1');
  });

  it('detects no inversion on fresh portfolio', () => {
    const portfolio = new Portfolio();
    const inv = portfolio.detectInversion();
    assert.equal(inv.inverted, false);
  });

  it('serializes and deserializes correctly', () => {
    const portfolio = new Portfolio();
    portfolio.applySignals([{
      type: 'AGREEMENT',
      assets: { trust: 0.10 },
      confidence: 0.8,
    }]);

    const json = portfolio.toJSON();
    const restored = Portfolio.fromJSON(json);

    assert.deepEqual(restored.assets, portfolio.assets);
    assert.equal(restored.messageCount, portfolio.messageCount);
  });

  it('clamps asset values between 0 and 1', () => {
    const portfolio = new Portfolio();

    // Try to push trust way above 1
    for (let i = 0; i < 50; i++) {
      portfolio.applySignals([{
        type: 'AGREEMENT',
        assets: { trust: 0.10 },
        confidence: 1.0,
      }]);
    }
    assert.ok(portfolio.assets.trust <= 1.0, 'Trust should not exceed 1.0');

    // Try to push commitment below 0
    for (let i = 0; i < 50; i++) {
      portfolio.applySignals([{
        type: 'DISAGREEMENT',
        assets: { commitment: -0.20 },
        confidence: 1.0,
      }]);
    }
    assert.ok(portfolio.assets.commitment >= 0.0, 'Commitment should not go below 0.0');
  });
});

// ─── Strategy Tests ──────────────────────────────────────────────────────────

describe('Strategy Selection', () => {
  it('selects ACCUMULATE for fresh conversation', () => {
    const portfolio = new Portfolio();
    const state = portfolio.getState();
    const result = selectStrategy(state);
    assert.equal(result.strategy, 'ACCUMULATE');
  });

  it('returns a directive string', () => {
    const portfolio = new Portfolio();
    const state = portfolio.getState();
    const result = selectStrategy(state);
    assert.ok(result.directive.length > 0, 'Directive should not be empty');
    assert.ok(typeof result.directive === 'string');
  });

  it('returns confidence score', () => {
    const portfolio = new Portfolio();
    const state = portfolio.getState();
    const result = selectStrategy(state);
    assert.ok(result.confidence > 0, 'Confidence should be > 0');
    assert.ok(result.confidence <= 1, 'Confidence should be <= 1');
  });

  it('selects HARVEST when conversion window is open', () => {
    const state = {
      assets: { trust: 0.8, commitment: 0.7, urgency: 0.5, curiosity: 0.6, authority: 0.6 },
      messageCount: 10,
      peakYield: 0.6,
      inversion: { inverted: false, severity: 0 },
      conversionWindow: { open: true, strength: 0.7, reason: 'portfolio_aligned' },
    };
    const result = selectStrategy(state);
    assert.equal(result.strategy, 'HARVEST');
  });

  it('selects HEDGE on yield inversion', () => {
    const state = {
      assets: { trust: 0.3, commitment: 0.3, urgency: 0.2, curiosity: 0.2, authority: 0.3 },
      messageCount: 8,
      peakYield: 0.5,
      inversion: { inverted: true, severity: 0.4 },
      conversionWindow: { open: false, strength: 0, reason: 'yield_inverted' },
    };
    const result = selectStrategy(state);
    assert.equal(result.strategy, 'HEDGE');
  });

  it('selects EXIT_GRACEFULLY on severe inversion', () => {
    const state = {
      assets: { trust: 0.1, commitment: 0.1, urgency: 0.05, curiosity: 0.05, authority: 0.1 },
      messageCount: 12,
      peakYield: 0.5,
      inversion: { inverted: true, severity: 0.8 },
      conversionWindow: { open: false, strength: 0, reason: 'yield_inverted' },
    };
    const result = selectStrategy(state);
    assert.equal(result.strategy, 'EXIT_GRACEFULLY');
  });
});

// ─── YieldEngine Integration Tests ───────────────────────────────────────────

describe('YieldEngine', () => {
  it('processes a message and returns full analysis', () => {
    const engine = new YieldEngine();
    const analysis = engine.processMessage('Hello, I am interested in your product', 'test-1');

    assert.ok('signals' in analysis);
    assert.ok('portfolio' in analysis);
    assert.ok('totalYield' in analysis);
    assert.ok('strategy' in analysis);
    assert.ok('directive' in analysis);
    assert.ok('conversionWindow' in analysis);
    assert.ok('inversion' in analysis);
  });

  it('tracks separate conversations independently', () => {
    const engine = new YieldEngine();

    // Positive conversation
    engine.processMessage('This is amazing! I love it!', 'happy-conv');
    engine.processMessage('Absolutely, this is perfect!', 'happy-conv');

    // Negative conversation
    engine.processMessage('This is terrible', 'sad-conv');
    engine.processMessage('I am really frustrated', 'sad-conv');

    const happy = engine.peek('happy-conv');
    const sad = engine.peek('sad-conv');

    assert.ok(
      happy.portfolio.trust > sad.portfolio.trust,
      'Happy conversation should have higher trust'
    );
  });

  it('simulates a full sales conversation with compounding', () => {
    const engine = new YieldEngine();
    const conv = 'sales-test';

    // Cold open
    const r1 = engine.processMessage('Hi, tell me about your product', conv);
    assert.equal(r1.strategy, 'ACCUMULATE');

    // Engagement builds
    engine.processMessage('Interesting, tell me more', conv);
    engine.processMessage('I see, that makes sense', conv);
    engine.processMessage('My team has been looking for this', conv);
    const r4 = engine.processMessage('We definitely need something like this', conv);

    // Yield should be growing
    assert.ok(r4.totalYield > r1.totalYield, 'Yield should grow over positive conversation');

    // Buying signal
    const r5 = engine.processMessage('How much does it cost?', conv);
    assert.ok(r5.signals.some(s => s.type === 'BUYING'), 'Should detect BUYING signal');
  });

  it('detects conversation heading toward abandonment', () => {
    const engine = new YieldEngine();
    const conv = 'dying-conv';

    // Start positive
    engine.processMessage('Hi, this looks interesting!', conv);
    engine.processMessage('Tell me more about the features', conv);

    // Then decline
    engine.processMessage('hmm', conv);
    engine.processMessage('not sure', conv);
    engine.processMessage('maybe', conv);
    engine.processMessage('idk', conv);
    engine.processMessage('ok', conv);
    const last = engine.processMessage('...', conv);

    // Trust should be low after repeated disengagement
    assert.ok(last.portfolio.trust < 0.4, 'Trust should decline on disengagement');
  });

  it('resets conversations correctly', () => {
    const engine = new YieldEngine();
    engine.processMessage('test message', 'reset-test');
    assert.ok(engine.peek('reset-test') !== null);

    engine.reset('reset-test');
    assert.equal(engine.peek('reset-test'), null);
  });

  it('exports and imports conversations', () => {
    const engine = new YieldEngine();
    engine.processMessage('I really love this product!', 'export-test');
    engine.processMessage('Absolutely amazing!', 'export-test');

    const exported = engine.exportConversation('export-test');
    assert.ok(exported !== null);
    assert.equal(exported.conversationId, 'export-test');

    // Import into a new engine
    const engine2 = new YieldEngine();
    engine2.importConversation(exported);

    const state = engine2.peek('export-test');
    assert.ok(state !== null, 'Imported conversation should be accessible');
  });

  it('returns stats across all conversations', () => {
    const engine = new YieldEngine();
    engine.processMessage('hello', 'conv-1');
    engine.processMessage('world', 'conv-2');
    engine.processMessage('test', 'conv-3');

    const stats = engine.getStats();
    assert.equal(stats.totalConversations, 3);
    assert.equal(stats.totalMessages, 3);
    assert.ok(stats.avgYield >= 0);
  });

  it('provides standalone message analysis', () => {
    const result = analyzeMessage('This is amazing! How much does it cost?');
    assert.ok(result.signals.length > 0);
    assert.ok(result.signalCount > 0);
    assert.ok(result.dominantSignal !== null);
  });

  it('handles default conversation ID', () => {
    const engine = new YieldEngine();
    const analysis = engine.processMessage('test');
    assert.ok(analysis.totalYield >= 0);
  });
});

// ─── Edge Case Tests ─────────────────────────────────────────────────────────

describe('Edge Cases', () => {
  it('handles very long messages', () => {
    const engine = new YieldEngine();
    const longMessage = 'I think this is great '.repeat(500);
    const analysis = engine.processMessage(longMessage, 'long-msg');
    assert.ok(analysis.totalYield >= 0);
  });

  it('handles emoji-only messages', () => {
    const engine = new YieldEngine();
    const analysis = engine.processMessage('👍👍👍', 'emoji-msg');
    assert.ok(analysis.totalYield >= 0);
  });

  it('handles rapid-fire messages', () => {
    const engine = new YieldEngine();
    for (let i = 0; i < 100; i++) {
      engine.processMessage(`Message ${i}`, 'rapid-fire');
    }
    const state = engine.peek('rapid-fire');
    assert.equal(state.messageCount, 100);
  });

  it('bounds message history to prevent memory leaks', () => {
    const engine = new YieldEngine();
    for (let i = 0; i < 50; i++) {
      engine.processMessage(`Message number ${i}`, 'history-bound');
    }
    // Engine should still work fine (history internally bounded to 20)
    const analysis = engine.processMessage('Final message', 'history-bound');
    assert.ok(analysis.totalYield >= 0);
  });
});
