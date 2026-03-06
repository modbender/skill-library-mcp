# Anti-Pattern Patterns Reference

## Pattern Catalog

| Pattern | Severity | Auto-Fixable | Description |
|---------|----------|--------------|-------------|
| EMPTY_CATCH | critical | ✅ | Empty catch block silently swallows errors |
| PROMISE_EMPTY_CATCH | critical | ✅ | `.catch(() => {})` — errors vanish into the void |
| CATCH_AND_CONTINUE_CRITICAL_PATH | critical | ❌ | Critical path logs-and-continues after errors |
| NO_LOGGING_IN_CATCH | high | ✅ | Catch block with no logging, stderr, or rethrow |
| ERROR_STRING_MATCHING | high | ❌ | `.includes()` on error.message to detect types |
| PROMISE_CATCH_NO_LOGGING | high | ✅ | Promise `.catch()` handler that doesn't log |
| LARGE_TRY_BLOCK | medium | ❌ | Try blocks over 10 significant lines (too broad) |
| GENERIC_CATCH | medium | ❌ | No error type discrimination in catch |
| PARTIAL_ERROR_LOGGING | medium | ✅ | Logging `error.message` instead of full error object |
| ERROR_MESSAGE_GUESSING | medium | ❌ | Multiple string checks to guess what went wrong |

## Fix Templates

### EMPTY_CATCH
```typescript
// Before
} catch (error) {
}

// After
} catch (error) {
  logger.error('Failed to perform <operation>', { error, context: { /* relevant state */ } });
}
```

### NO_LOGGING_IN_CATCH — Prepend logging before existing code
```typescript
// After
} catch (error) {
  logger.error('Failed to <operation>', { error });
  // ... existing catch body ...
}
```

### PROMISE_EMPTY_CATCH
```typescript
// Before
.catch(() => {})

// After
.catch((error) => {
  logger.error('Promise rejected in <chain>', { error });
})
```

### PARTIAL_ERROR_LOGGING
```typescript
// Before
logger.error('Failed', error.message);

// After
logger.error('Failed', { error }); // logs full stack trace
```

### GENERIC_CATCH — Add type narrowing
```typescript
} catch (error) {
  if (error instanceof SpecificError) {
    logger.warn('Expected error type', { error });
    return fallback();
  }
  logger.error('Unexpected error', { error });
  throw error;
}
```

### LARGE_TRY_BLOCK — Split into targeted units
Break the monolithic try into separate operations, each with its own error strategy:
- Critical operations: let propagate or explicitly rethrow
- Non-critical (e.g., cache, notifications): `.catch()` with logging + graceful degradation

### CRITICAL_PATH — Fail loud
Options in order of preference:
1. **Propagate**: remove try-catch, let error bubble up
2. **Log + rethrow**: full context logging, then `throw error`
3. **Log + explicit recovery**: full logging + call `markJobForRetry()` or equivalent — never silent continuation

## Severity Guide

- **critical**: Must fix before ship. Silent failures that hide production issues.
- **high**: Fix soon. Makes debugging significantly harder.
- **medium**: Fix when touching the file. Code smell, not immediately dangerous.

## Context Variables for Templates

| Variable | Example |
|----------|---------|
| `<operation>` | "fetch user data", "connect to database" |
| `<context>` | `{ userId, requestId, attempt }` |
| `<fallback>` | "using cached value", "returning default" |
