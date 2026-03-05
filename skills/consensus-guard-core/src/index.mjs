export * from './taxonomy.mjs';
export * from './policy.mjs';
export * from './idempotency.mjs';
export * from './validate.mjs';
export * from './board.mjs';
export * from './state-path.mjs';

export async function invoke(input, opts = {}) {
  if (typeof opts.handler === 'function') return opts.handler(input, opts);
  return {
    error: {
      code: 'NO_HANDLER',
      message: 'consensus-guard-core exposes primitives only; provide opts.handler for invoke()'
    }
  };
}
