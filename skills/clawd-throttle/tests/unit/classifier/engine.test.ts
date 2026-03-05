import { describe, it, expect } from 'vitest';
import { classifyPrompt, loadWeights } from '../../../src/classifier/engine.js';
import path from 'node:path';

const weights = loadWeights(path.resolve('data/classifier-weights.json'));
const thresholds = { simpleMax: 0.30, complexMin: 0.65 };

describe('classifyPrompt', () => {
  it('classifies greetings as simple', () => {
    const result = classifyPrompt('hello', {}, weights, thresholds);
    expect(result.tier).toBe('simple');
    expect(result.score).toBeLessThanOrEqual(0.30);
  });

  it('classifies short questions as simple', () => {
    const result = classifyPrompt('What is TypeScript?', {}, weights, thresholds);
    expect(result.tier).toBe('simple');
  });

  it('classifies moderate coding tasks as standard', () => {
    const text = `Please refactor this function to use async/await:
\`\`\`typescript
function fetchData(url) {
  return fetch(url).then(res => res.json()).then(data => {
    console.log(data);
    return data;
  });
}
\`\`\`
Explain why async/await is better here.`;
    const result = classifyPrompt(text, { messageCount: 5 }, weights, thresholds);
    expect(result.tier).toBe('standard');
  });

  it('classifies complex multi-step architectural tasks as complex', () => {
    const text = `I need you to architect a complete microservices system. Here are the requirements:

1. Design a user authentication service with OAuth2 and JWT
2. Create an API gateway that handles rate limiting and load balancing
3. Implement event-driven communication between services using message queues
4. Set up a database schema for user profiles, permissions, and audit logs
5. Design the CI/CD pipeline with automated testing and blue-green deployments

For each service, explain the trade-offs of different approaches, compare REST vs gRPC,
and think through the failure modes step by step. Consider the implications of
eventual consistency vs strong consistency. Debug potential race conditions.

Additionally, implement monitoring with Prometheus and Grafana, configure alerting
rules, and set up distributed tracing with OpenTelemetry.`;

    const result = classifyPrompt(text, {
      messageCount: 15,
      systemPrompt: 'You are a senior architect. You must provide structured JSON responses with detailed analysis. Never give superficial answers. Always consider security implications. Your role is to guide complex technical decisions.',
    }, weights, thresholds);
    expect(result.tier).toBe('complex');
    expect(result.score).toBeGreaterThanOrEqual(0.65);
  });

  it('runs in under 1ms', () => {
    const text = 'Explain step by step how to refactor this React component to use hooks, and compare the trade-offs of useReducer vs useState for complex state management.';
    const result = classifyPrompt(text, { messageCount: 8 }, weights, thresholds);
    expect(result.classifiedInMs).toBeLessThan(1);
  });

  it('returns all dimension scores', () => {
    const result = classifyPrompt('hello', {}, weights, thresholds);
    expect(result.dimensions).toHaveProperty('tokenCount');
    expect(result.dimensions).toHaveProperty('codePresence');
    expect(result.dimensions).toHaveProperty('reasoningMarkers');
    expect(result.dimensions).toHaveProperty('simpleIndicators');
    expect(result.dimensions).toHaveProperty('multiStepPatterns');
    expect(result.dimensions).toHaveProperty('questionCount');
    expect(result.dimensions).toHaveProperty('systemPromptSignals');
    expect(result.dimensions).toHaveProperty('conversationDepth');
  });

  it('clamps composite score to [0, 1]', () => {
    const result = classifyPrompt('hello!', {}, weights, thresholds);
    expect(result.score).toBeGreaterThanOrEqual(0);
    expect(result.score).toBeLessThanOrEqual(1);
  });
});
