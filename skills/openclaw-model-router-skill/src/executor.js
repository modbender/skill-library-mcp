const { parsePrefix, resolveRoute } = require('./router');
const {
  RouterError,
  ProviderUnavailableError,
  VerificationError,
} = require('./errors');

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function jitter(baseMs) {
  const n = Number(baseMs) || 0;
  return Math.floor(Math.random() * Math.max(1, n));
}

async function withRetry(task, retries = 1, delayMs = 120) {
  let lastErr;
  for (let attempt = 0; attempt <= retries; attempt += 1) {
    try {
      return await task(attempt);
    } catch (err) {
      lastErr = err;
      if (!err.retryable || attempt === retries) {
        throw err;
      }
      const backoff = delayMs * (2 ** attempt) + jitter(delayMs);
      await sleep(backoff);
    }
  }
  throw lastErr;
}

async function switchAndVerify(sessionController, targetModel, verifyRetries = 2, verifyDelayMs = 80) {
  const switched = await sessionController.setModel(targetModel);
  if (!switched) {
    throw new ProviderUnavailableError(targetModel, { phase: 'setModel' });
  }

  for (let attempt = 0; attempt <= verifyRetries; attempt += 1) {
    const verified = await sessionController.getCurrentModel();
    if (verified === targetModel) {
      return;
    }
    if (attempt < verifyRetries) {
      await sleep(verifyDelayMs * (attempt + 1));
    } else {
      throw new VerificationError(targetModel, verified);
    }
  }
}

async function routeAndExecute({
  message,
  config,
  sessionController,
  taskExecutor,
  logger,
}) {
  const startedAt = Date.now();
  const { prefix, body } = parsePrefix(message);

  if (!prefix) {
    const output = await taskExecutor.execute(message);
    logger.log({ type: 'route.skip', reason: 'no_prefix', latencyMs: Date.now() - startedAt });
    return { switched: false, output };
  }

  let route;
  try {
    route = resolveRoute(prefix, config);
  } catch (err) {
    logger.log({
      type: 'route.failure',
      prefix,
      reason: err.message,
      code: err.code || 'ROUTE_RESOLVE_FAILED',
      latencyMs: Date.now() - startedAt,
    });
    throw err;
  }

  const targetModel = route.model;
  const fallbackModel = route.fallbackModel || null;
  const resolvedPrefix = route._resolvedPrefix || prefix;

  const current = await sessionController.getCurrentModel();
  const alreadyOnModel = current === targetModel;
  if (!alreadyOnModel) {
    try {
      await withRetry(
        async () => switchAndVerify(
          sessionController,
          targetModel,
          config.retry?.verifyRetries ?? 2,
          config.retry?.verifyDelayMs ?? 80,
        ),
        config.retry?.maxRetries ?? 1,
        config.retry?.baseDelayMs ?? 120,
      );
    } catch (err) {
      logger.log({
        type: 'route.failure',
        prefix,
        targetModel,
        reason: err.message,
        code: err.code || 'MODEL_SWITCH_FAILED',
        latencyMs: Date.now() - startedAt,
      });
      throw err;
    }
  }

  const switched = !alreadyOnModel;
  if (!body) {
    logger.log({
      type: 'route.switch_only',
      prefix,
      resolvedPrefix,
      targetModel,
      currentModel: current,
      alreadyOnModel,
      switched,
      latencyMs: Date.now() - startedAt,
    });
    return {
      switched,
      alreadyOnModel,
      targetModel,
      currentModel: current,
      switchOnly: true,
      output: alreadyOnModel ? `already_on:${targetModel}` : `switched:${targetModel}`,
    };
  }

  try {
    const output = await taskExecutor.execute(body);
    logger.log({
      type: 'route.success',
      prefix,
      resolvedPrefix,
      targetModel,
      fallbackModel,
      currentModel: current,
      alreadyOnModel,
      latencyMs: Date.now() - startedAt,
    });
    return { switched, alreadyOnModel, targetModel, currentModel: current, output };
  } catch (err) {
    if (fallbackModel) {
      await withRetry(
        async () => switchAndVerify(
          sessionController,
          fallbackModel,
          config.retry?.verifyRetries ?? 2,
          config.retry?.verifyDelayMs ?? 80,
        ),
        config.retry?.maxRetries ?? 1,
        config.retry?.baseDelayMs ?? 120,
      );
      logger.log({
        type: 'route.fallback',
        prefix,
        resolvedPrefix,
        targetModel,
        fallbackModel,
        reason: err.message,
        latencyMs: Date.now() - startedAt,
      });
      try {
        const output = await taskExecutor.execute(body);
        return { switched: true, targetModel: fallbackModel, output, fallback: true };
      } catch (fallbackErr) {
        // Attempt to restore original model on fallback failure.
        try {
          if (current) {
            await withRetry(
              async () => switchAndVerify(
                sessionController,
                current,
                config.retry?.verifyRetries ?? 2,
                config.retry?.verifyDelayMs ?? 80,
              ),
              config.retry?.maxRetries ?? 1,
              config.retry?.baseDelayMs ?? 120,
            );
          }
        } catch (restoreErr) {
          logger.log({
            type: 'route.restore_failed',
            prefix,
            targetModel: current,
            reason: restoreErr.message,
            code: restoreErr.code || 'MODEL_RESTORE_FAILED',
            latencyMs: Date.now() - startedAt,
          });
        }
        const wrappedFallback = fallbackErr instanceof RouterError
          ? fallbackErr
          : new RouterError(`Fallback execution failed: ${fallbackErr.message}`, {
            code: 'FALLBACK_EXECUTION_FAILED',
            retryable: false,
          });
        logger.log({
          type: 'route.failure',
          prefix,
          targetModel: fallbackModel,
          reason: wrappedFallback.message,
          code: wrappedFallback.code,
          latencyMs: Date.now() - startedAt,
        });
        throw wrappedFallback;
      }
    }

    const wrapped = err instanceof RouterError
      ? err
      : new RouterError(`Execution failed: ${err.message}`, {
        code: 'EXECUTION_FAILED',
        retryable: false,
      });
    logger.log({
      type: 'route.failure',
      prefix,
      targetModel,
      reason: wrapped.message,
      code: wrapped.code,
      latencyMs: Date.now() - startedAt,
    });
    throw wrapped;
  }
}

module.exports = {
  routeAndExecute,
  withRetry,
};
