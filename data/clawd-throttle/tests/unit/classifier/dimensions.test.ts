import { describe, it, expect } from 'vitest';
import {
  scoreTokenCount,
  scoreCodePresence,
  scoreReasoningMarkers,
  scoreSimpleIndicators,
  scoreMultiStepPatterns,
  scoreQuestionCount,
  scoreSystemPromptSignals,
  scoreConversationDepth,
} from '../../../src/classifier/dimensions.js';

describe('scoreTokenCount', () => {
  it('scores short text low', () => {
    expect(scoreTokenCount('hello')).toBe(0);
  });

  it('scores medium text moderately', () => {
    const text = 'a'.repeat(2000); // ~500 tokens
    expect(scoreTokenCount(text)).toBeCloseTo(0.30, 1);
  });

  it('scores long text high', () => {
    const text = 'a'.repeat(40000); // ~10000 tokens
    expect(scoreTokenCount(text)).toBeGreaterThan(0.85);
  });
});

describe('scoreCodePresence', () => {
  it('scores zero for plain text', () => {
    expect(scoreCodePresence('How are you doing today?')).toBe(0);
  });

  it('detects fenced code blocks', () => {
    const text = '```\nconst x = 1;\n```';
    expect(scoreCodePresence(text)).toBeGreaterThan(0.3);
  });

  it('detects programming keywords', () => {
    const text = 'Use async await with try catch for the function';
    expect(scoreCodePresence(text)).toBeGreaterThan(0.05);
  });

  it('detects file extensions', () => {
    const text = 'Edit the file index.ts and update styles.css';
    expect(scoreCodePresence(text)).toBeGreaterThan(0.1);
  });
});

describe('scoreReasoningMarkers', () => {
  it('scores zero for simple text', () => {
    expect(scoreReasoningMarkers('hello there')).toBe(0);
  });

  it('detects analytical language', () => {
    const text = 'Explain the trade-offs and compare the approaches';
    expect(scoreReasoningMarkers(text)).toBeGreaterThan(0.2);
  });

  it('detects chain-of-thought markers', () => {
    const text = 'Think through this step by step';
    expect(scoreReasoningMarkers(text)).toBeGreaterThan(0.3);
  });

  it('detects debugging language', () => {
    const text = 'Debug this and figure out why it crashes';
    expect(scoreReasoningMarkers(text)).toBeGreaterThan(0.2);
  });
});

describe('scoreSimpleIndicators', () => {
  it('returns 1.0 for pure greetings', () => {
    expect(scoreSimpleIndicators('hello')).toBe(1.0);
    expect(scoreSimpleIndicators('thanks!')).toBe(1.0);
    expect(scoreSimpleIndicators('ok')).toBe(1.0);
    expect(scoreSimpleIndicators('yes')).toBe(1.0);
  });

  it('scores short text higher', () => {
    expect(scoreSimpleIndicators('define API')).toBeGreaterThan(0.4);
  });

  it('scores long complex text low', () => {
    const text = 'Please implement a full authentication system with OAuth2, JWT tokens, refresh token rotation, and role-based access control.';
    expect(scoreSimpleIndicators(text)).toBeLessThan(0.2);
  });
});

describe('scoreMultiStepPatterns', () => {
  it('scores zero for simple text', () => {
    expect(scoreMultiStepPatterns('hello')).toBe(0);
  });

  it('detects sequential markers', () => {
    const text = 'First do this, then do that, and finally finish up';
    expect(scoreMultiStepPatterns(text)).toBeGreaterThan(0.2);
  });

  it('detects numbered lists', () => {
    const text = '1. Create component\n2. Add tests\n3. Deploy';
    expect(scoreMultiStepPatterns(text)).toBeGreaterThan(0.2);
  });

  it('detects build verbs', () => {
    const text = 'Implement and deploy the new feature, then integrate with the API';
    expect(scoreMultiStepPatterns(text)).toBeGreaterThan(0.2);
  });
});

describe('scoreQuestionCount', () => {
  it('scores zero for no questions', () => {
    expect(scoreQuestionCount('Do this thing.')).toBe(0);
  });

  it('scores one question moderately', () => {
    expect(scoreQuestionCount('What is this?')).toBeGreaterThan(0.1);
  });

  it('scores many questions high', () => {
    const text = 'What? Why? How? When? Where?';
    expect(scoreQuestionCount(text)).toBeGreaterThan(0.7);
  });
});

describe('scoreSystemPromptSignals', () => {
  it('returns 0 for no system prompt', () => {
    expect(scoreSystemPromptSignals(undefined)).toBe(0);
    expect(scoreSystemPromptSignals('')).toBe(0);
  });

  it('scores short system prompt low', () => {
    expect(scoreSystemPromptSignals('Be helpful.')).toBeGreaterThan(0);
    expect(scoreSystemPromptSignals('Be helpful.')).toBeLessThan(0.3);
  });

  it('scores complex system prompt high', () => {
    const prompt = 'You are a senior engineer. You must always respond in JSON format. Never use markdown. Your role is to analyze code. You must not share internal logic. Always follow the schema provided.';
    expect(scoreSystemPromptSignals(prompt)).toBeGreaterThan(0.4);
  });
});

describe('scoreConversationDepth', () => {
  it('returns 0 for single message', () => {
    expect(scoreConversationDepth(1)).toBe(0);
    expect(scoreConversationDepth(undefined)).toBe(0);
  });

  it('scores moderate conversation', () => {
    expect(scoreConversationDepth(10)).toBeCloseTo(0.45, 1);
  });

  it('scores deep conversation high', () => {
    expect(scoreConversationDepth(50)).toBeGreaterThan(0.8);
  });
});
