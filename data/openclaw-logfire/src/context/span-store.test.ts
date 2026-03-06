import { describe, it, expect, beforeEach } from 'vitest';
import { spanStore } from './span-store.js';

// Minimal mock spans for testing store logic
function mockSpan(): any {
  return {
    end: () => {},
    spanContext: () => ({ traceId: 'abc', spanId: 'def' }),
    setAttribute: () => {},
    setStatus: () => {},
    addEvent: () => {},
    addLink: () => {},
    recordException: () => {},
  };
}

function mockContext(): any {
  return {};
}

describe('SpanStore', () => {
  beforeEach(() => {
    // Clear the store between tests
    spanStore.delete('test-session');
    spanStore.delete('test-session-2');
  });

  it('stores and retrieves sessions', () => {
    spanStore.set('test-session', {
      agentSpan: mockSpan(),
      agentCtx: mockContext(),
      toolStack: [],
      toolSequence: 0,
      hasError: false,
      startTime: Date.now(),
    });

    const session = spanStore.get('test-session');
    expect(session).toBeDefined();
    expect(session!.toolSequence).toBe(0);
  });

  it('returns undefined for unknown sessions', () => {
    expect(spanStore.get('nonexistent')).toBeUndefined();
  });

  it('pushes and pops tool spans (LIFO)', () => {
    spanStore.set('test-session', {
      agentSpan: mockSpan(),
      agentCtx: mockContext(),
      toolStack: [],
      toolSequence: 0,
      hasError: false,
      startTime: Date.now(),
    });

    spanStore.pushTool('test-session', {
      span: mockSpan(),
      ctx: mockContext(),
      name: 'Read',
      callId: 'call-1',
      startTime: Date.now(),
    });

    spanStore.pushTool('test-session', {
      span: mockSpan(),
      ctx: mockContext(),
      name: 'Write',
      callId: 'call-2',
      startTime: Date.now(),
    });

    // LIFO: Write comes off first
    const first = spanStore.popTool('test-session');
    expect(first?.name).toBe('Write');

    const second = spanStore.popTool('test-session');
    expect(second?.name).toBe('Read');

    const third = spanStore.popTool('test-session');
    expect(third).toBeUndefined();
  });

  it('peeks without removing', () => {
    spanStore.set('test-session', {
      agentSpan: mockSpan(),
      agentCtx: mockContext(),
      toolStack: [],
      toolSequence: 0,
      hasError: false,
      startTime: Date.now(),
    });

    spanStore.pushTool('test-session', {
      span: mockSpan(),
      ctx: mockContext(),
      name: 'exec',
      callId: 'call-1',
      startTime: Date.now(),
    });

    expect(spanStore.peekTool('test-session')?.name).toBe('exec');
    expect(spanStore.peekTool('test-session')?.name).toBe('exec');
  });

  it('deletes sessions', () => {
    spanStore.set('test-session', {
      agentSpan: mockSpan(),
      agentCtx: mockContext(),
      toolStack: [],
      toolSequence: 0,
      hasError: false,
      startTime: Date.now(),
    });

    spanStore.delete('test-session');
    expect(spanStore.get('test-session')).toBeUndefined();
  });
});
