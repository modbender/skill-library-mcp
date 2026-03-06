---
domain: openclaw-doctor
topic: anti-patterns
priority: high
ttl: 30d
---

# OpenClaw Anti-Patterns & Common Issues

## Configuration Anti-Patterns

### 1. Hardcoded Paths
❌ **Bad**:
```json
{
  "dataDir": "/Users/john/openclaw/data"
}
```

✅ **Good**:
```json
{
  "dataDir": "$OPENCLAW_HOME/data"
}
```

### 2. Excessive Timeouts
❌ **Bad**: Timeout set to 5 minutes for simple operations
```
Issue: Hides performance problems
Fix: Set appropriate timeouts (30s for most operations)
```

### 3. Disabled Logging
❌ **Bad**:
```json
{
  "logging": {
    "level": "none"
  }
}
```

✅ **Good**: Use `warn` or `error` in production, `debug` for troubleshooting

### 4. Unlimited Concurrency
❌ **Bad**:
```json
{
  "concurrency": 999
}
```

✅ **Good**: Base on installed skills and resources (10-50)

## Skill Management Anti-Patterns

### 1. Installing Unused Skills
```
Problem: Installing skills "just in case"
Impact: Wasted memory, slower startup, dependency bloat
Detection: Skills with 0 sessions in >30 days
Fix: Uninstall unused skills
```

### 2. Ignoring Skill Dependencies
```
Problem: Manually installing skill without dependencies
Impact: Skill fails at runtime with cryptic errors
Detection: Check manifest.json dependencies field
Fix: Use `clawhub install` which resolves dependencies
```

### 3. Mixing Major Versions
```
Problem: Having @botlearn/code-gen@1.x and @botlearn/code-gen@2.x
Impact: Unpredictable behavior, conflicts
Detection: Duplicate skill names with different versions
Fix: Uninstall older version
```

### 4. Pinning All Dependencies
```
Problem: Using exact versions for all skill dependencies
Impact: Miss security updates, bug fixes
Detection: package.json has only exact versions (1.2.3)
Fix: Use semantic ranges (^1.2.3)
```

## Memory Anti-Patterns

### 1. Infinite TTL Documents
```
Problem: Setting TTL to "never" for all knowledge
Impact: Memory grows unbounded
Detection: Large number of documents with no expiry
Fix: Set appropriate TTL (30d default, adjust by importance)
```

### 2. Duplicate Knowledge Injection
```
Problem: Re-injecting same knowledge on every session
Impact: Memory bloat, slower lookups
Detection: Duplicate content with different IDs
Fix: Check before injecting
```

### 3. Large Single Documents
```
Problem: Single knowledge document >10MB
Impact: Slow retrieval, memory pressure
Detection: Document size >1MB
Fix: Split into smaller, focused documents
```

## Logging Anti-Patterns

### 1. Logging Sensitive Data
```
Problem: API keys, tokens, passwords in logs
Impact: Security vulnerability
Detection: Scan logs for patterns (Bearer, token, secret, key)
Fix: Redact sensitive fields before logging
```

### 2. Verbose Production Logging
```
Problem: Debug logs in production
Impact: Log file bloat, performance degradation
Detection: Log growth rate >100MB/day
Fix: Set appropriate log level per environment
```

### 3. Missing Structured Logging
```
Problem: Free-text log messages
Impact: Hard to parse and analyze
Detection: Log lines not matching JSON pattern
Fix: Use structured logging with consistent fields
```

### 4. No Log Rotation
```
Problem: Single log file growing forever
Impact: Disk exhaustion
Detection: Log files >1GB
Fix: Enable log rotation with size limits
```

## Common Error Patterns

### Pattern 1: Cascade Failures
```
Symptom: Multiple skills failing simultaneously
Cause: Shared dependency (e.g., network service) down
Detection: Correlated error timestamps
Fix: Check shared services first
```

### Pattern 2: Memory Leaks
```
Symptom: Gradual memory increase over time
Cause: Unclosed connections, cached data
Detection: Memory graph shows upward trend
Fix: Restart service, identify leak source
```

### Pattern 3: Race Conditions
```
Symptom: Intermittent failures, hard to reproduce
Cause: Concurrent access to shared resource
Detection: Errors correlate with high concurrency
Fix: Add locking or reduce concurrency
```

### Pattern 4: Dependency Hell
```
Symptom: Cannot install skill due to conflicting dependencies
Cause: Two skills require incompatible versions of same dependency
Detection: npm install fails with ERESOLVE
Fix: Use npm overrides, contact skill maintainers
```

## Performance Anti-Patterns

### 1. Synchronous I/O
```
Problem: Blocking operations in skill execution
Impact: Poor concurrency, slow response
Detection: Long execution times, high CPU wait
Fix: Use async/await throughout
```

### 2. N+1 Queries
```
Problem: Querying inside a loop
Impact: Exponential time complexity
Detection: Query count >> expected
Fix: Batch queries, use joins
```

### 3. Redundant Processing
```
Problem: Processing same data multiple times
Impact: Wasted CPU, slower response
Detection: Similar operations with same inputs
Fix: Cache results, avoid duplication
```

## Security Anti-Patterns

### 1. Plain Text Credentials
```
Problem: API keys in config files
Detection: Scan for "key", "secret", "token", "password"
Fix: Use environment variables or secret management
```

### 2. Disabled SSL Verification
```
Problem: Setting rejectUnauthorized: false
Detection: Search for "rejectUnauthorized" in code/config
Fix: Use proper certificates
```

### 3. Wildcard CORS
```
Problem: Access-Control-Allow-Origin: *
Detection: CORS configuration with "*"
Fix: Specify allowed origins
```

## Diagnosis Anti-Patterns

### 1. Treating Symptoms, Not Root Cause
```
❌ Bad: Restart service when it crashes
✅ Good: Find why it crashes and fix the bug
```

### 2. Shotgun Debugging
```
❌ Bad: Random changes hoping something works
✅ Good: Form hypothesis, test, verify
```

### 3. Ignoring Warnings
```
❌ Bad: Only looking at errors
✅ Good: Warnings often precede errors
```

### 4. Not Reproducing Issues
```
❌ Bad: Fixing without understanding
✅ Good: Reproduce in controlled environment
```

## Red Flags (Immediate Investigation Needed)

| Red Flag | Indicates | Action |
|----------|-----------|--------|
| Startup time >30s | Configuration issue | Run full diagnostic |
| Memory usage >80% | Memory leak or over-allocation | Check memory trends |
| Error rate >5% | Systemic issue | Review logs immediately |
| Disk space <10% | Capacity issue | Clean up, expand storage |
| Unusual skill failures | Skill incompatibility | Check skill versions |
| Strange log entries | Security breach | Investigate urgently |

## Common User Mistakes

### 1. Not Reading Error Messages
```
Users often skip error details and try generic fixes
Result: Wasted time, frustration
Education: Encourage reading full error output
```

### 2. Skipping Updates
```
Fear of breaking changes leads to outdated versions
Result: Missing security patches, bug fixes
Education: Explain changelog, backup procedures
```

### 3. Manual Overwrites
```
Manually editing auto-generated files
Result: Changes lost on next update
Education: Use configuration files, not generated files
```

### 4. Ignoring Backup
```
No backup before major changes
Result: Cannot recover from failures
Education: Emphasize backup before any modification
```
