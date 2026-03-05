---
name: sui-coverage
description: Analyze Sui Move test coverage, identify untested code, write missing tests, and perform security audits. Includes Python tools for parsing coverage output and generating reports.
homepage: https://github.com/EasonC13-agent/sui-coverage-demo
metadata:
  openclaw:
    emoji: "🔍"
    requires:
      bins: ["python3", "sui"]
---

# Sui Coverage Skill

Analyze and automatically improve Sui Move test coverage with security analysis.

**GitHub:** <https://github.com/EasonC13-agent/sui-skills/tree/main/sui-coverage>

## Prerequisites

### Install Sui CLI

```bash
# macOS (recommended)
brew install sui

# Other platforms: see official docs
# https://docs.sui.io/guides/developer/getting-started/sui-install
```

Verify:
```bash
sui --version
```

## Quick Reference

```bash
# Location of tools (adjust to your skill installation path)
SKILL_DIR=<your-workspace>/skills/sui-coverage

# Full workflow
cd /path/to/move/package
sui move test --coverage --trace
python3 $SKILL_DIR/analyze_source.py -m <module> -o coverage.md
```

## Workflow: Auto-Improve Test Coverage

### Step 1: Run Coverage Analysis

```bash
cd <package_path>
sui move test --coverage --trace
python3 $SKILL_DIR/analyze_source.py -m <module_name> -o coverage.md
```

### Step 2: Read the Coverage Report

Read the generated `coverage.md` to identify:
- 🔴 **Uncalled functions** - Functions never executed
- 🔴 **Uncovered assertions** - `assert!()` failure paths not tested
- 🔴 **Uncovered branches** - `if/else` paths not taken

### Step 3: Write Missing Tests

For each uncovered item, write a test:

#### A. Uncalled Function
```move
#[test]
fun test_<function_name>() {
    // Setup
    let mut ctx = tx_context::dummy();
    // Call the uncovered function
    <function_name>(...);
    // Assert expected behavior
}
```

#### B. Assertion Failure Path (expect_failure)
```move
#[test]
#[expected_failure(abort_code = <ERROR_CODE>)]
fun test_<function>_fails_when_<condition>() {
    let mut ctx = tx_context::dummy();
    // Setup state that triggers the assertion failure
    <function_call_that_should_fail>();
}
```

#### C. Branch Coverage (if/else)
```move
#[test]
fun test_<function>_when_<condition_true>() { ... }

#[test]  
fun test_<function>_when_<condition_false>() { ... }
```

### Step 4: Verify Coverage Improved

```bash
sui move test --coverage --trace
python3 $SKILL_DIR/analyze_source.py -m <module_name>
```

---

## Tools

### 1. analyze_source.py (Primary Tool)

```bash
python3 $SKILL_DIR/analyze_source.py --module <name> [options]

Options:
  -m, --module    Module name (required)
  -p, --path      Package path (default: .)
  -o, --output    Output file (e.g., coverage.md)
  --json          JSON output
  --markdown      Markdown to stdout
```

### 2. analyze.py (LCOV Statistics)

```bash
sui move coverage lcov
python3 $SKILL_DIR/analyze.py lcov.info -f "<package>" -s sources/

Options:
  -f, --filter       Filter by path pattern
  -s, --source-dir   Source directory for context
  -i, --issues-only  Only show files with issues
  -j, --json         JSON output
```

### 3. parse_bytecode.py (Low-level)

```bash
sui move coverage bytecode --module <name> | python3 $SKILL_DIR/parse_bytecode.py
```

---

## Common Patterns

### Testing Assertion Failures

```move
// Source code:
public fun withdraw(balance: &mut u64, amount: u64) {
    assert!(*balance >= amount, EInsufficientBalance);  // ← This failure path
    *balance = *balance - amount;
}

// Test for the failure path:
#[test]
#[expected_failure(abort_code = EInsufficientBalance)]
fun test_withdraw_insufficient_balance() {
    let mut balance = 50;
    withdraw(&mut balance, 100);  // Should fail: 50 < 100
}
```

### Testing All Branches

```move
// Source code:
public fun classify(value: u64): u8 {
    if (value == 0) {
        0
    } else if (value < 100) {
        1
    } else {
        2
    }
}

// Tests for all branches:
#[test]
fun test_classify_zero() {
    assert!(classify(0) == 0, 0);
}

#[test]
fun test_classify_small() {
    assert!(classify(50) == 1, 0);
}

#[test]
fun test_classify_large() {
    assert!(classify(100) == 2, 0);
}
```

### Testing Object Lifecycle

```move
#[test]
fun test_full_lifecycle() {
    let mut ctx = tx_context::dummy();
    
    // Create
    let obj = create(&mut ctx);
    assert!(get_value(&obj) == 0, 0);
    
    // Modify
    increment(&mut obj);
    assert!(get_value(&obj) == 1, 0);
    
    // Destroy
    destroy(obj);
}
```

---

## Error Code Reference

When writing `#[expected_failure]` tests, use the error constant name:

```move
// If the module defines:
const EInvalidInput: u64 = 1;
const ENotAuthorized: u64 = 2;

// Use in test:
#[expected_failure(abort_code = EInvalidInput)]
fun test_invalid_input() { ... }

// Or use the module-qualified name:
#[expected_failure(abort_code = my_module::EInvalidInput)]
fun test_invalid_input() { ... }
```

---

## Example: Full Auto-Coverage Session

```bash
# 1. Analyze current coverage
cd /path/to/my_package
sui move test --coverage --trace
python3 $SKILL_DIR/analyze_source.py -m my_module -o coverage.md

# 2. Review what's missing
cat coverage.md
# Shows:
# - decrement() not called
# - assert!(value > 0, EValueZero) failure not tested

# 3. Add tests to sources/my_module.move or tests/my_module_tests.move
# (write the missing tests)

# 4. Verify improvement
sui move test --coverage --trace
python3 $SKILL_DIR/analyze_source.py -m my_module

# 5. Repeat until 100% coverage
```

---

## Integration with Agent Workflow

When asked to improve test coverage:

1. **Run analysis** - Get current coverage state
2. **Read source** - Understand the module's logic
3. **Identify gaps** - List uncovered functions/branches/assertions
4. **Security review** - Analyze for vulnerabilities while writing tests
5. **Write tests** - Create tests for each gap + security edge cases
6. **Report findings** - Document any security concerns discovered
7. **Verify** - Re-run coverage to confirm improvement

Always commit test improvements:
```bash
git add sources/ tests/
git commit -m "Improve test coverage for <module>"
```

---

## Security Analysis During Testing

**Writing tests = Understanding the contract = Finding vulnerabilities**

When writing tests, actively look for these issues:

### 1. Access Control
```
Questions to ask:
- Who can call this function?
- Should there be owner/admin checks?
- Can unauthorized users manipulate state?

Red flags:
- Public functions that modify critical state without checks
- Missing capability/witness patterns
```

### 2. Integer Overflow/Underflow
```
Questions to ask:
- What happens at u64::MAX?
- What happens when subtracting from 0?
- Are arithmetic operations checked?

Test pattern:
#[test]
fun test_overflow_boundary() {
    // Test with max values
}
```

### 3. State Manipulation
```
Questions to ask:
- Can state be left in inconsistent state?
- Are all state changes atomic?
- Can partial failures corrupt data?

Red flags:
- Multiple state changes without rollback
- Shared objects without proper locking
```

### 4. Economic Exploits
```
Questions to ask:
- Can someone extract more value than deposited?
- Are there rounding errors that can be exploited?
- Flash loan attack vectors?

Red flags:
- Price calculations without slippage protection
- Unbounded loops over user-controlled data
```

### 5. Denial of Service
```
Questions to ask:
- Can someone block legitimate users?
- Are there unbounded operations?
- Can storage be filled maliciously?

Red flags:
- Vectors that grow unbounded
- Loops over external data
```

### Security Report Template

When analyzing a module, generate a security report:

```markdown
## Security Analysis: <module_name>

### Summary
- Risk Level: [Low/Medium/High/Critical]
- Issues Found: X

### Findings

#### [SEVERITY] Issue Title
- **Location:** Line XX
- **Description:** What the issue is
- **Impact:** What could happen
- **Recommendation:** How to fix

### Tested Edge Cases
- [ ] Overflow at max values
- [ ] Underflow at zero
- [ ] Unauthorized access attempts
- [ ] Empty/null inputs
- [ ] Reentrancy scenarios
```

### Example: Security-Aware Test

```move
// SECURITY: Testing that non-owner cannot withdraw
#[test]
#[expected_failure(abort_code = ENotOwner)]
fun test_unauthorized_withdraw() {
    // Setup: Create vault owned by ALICE
    // Action: BOB tries to withdraw
    // Expected: Should fail with ENotOwner
}

// SECURITY: Testing overflow protection
#[test]
fun test_deposit_overflow_protection() {
    // Deposit near u64::MAX
    // Verify no overflow occurs
}

// SECURITY: Testing economic invariant
#[test]
fun test_total_supply_invariant() {
    // After any operations:
    // sum(all_balances) == total_supply
}
```

---

## Full Workflow with Security

```bash
# 1. Coverage analysis
sui move test --coverage --trace
python3 $SKILL_DIR/analyze_source.py -m <module> -o coverage.md

# 2. While writing tests, document security findings
# Create SECURITY.md alongside coverage.md

# 3. After tests pass, summarize:
# - Coverage: X% → 100%
# - Security issues found: N
# - Recommendations: ...
```

---

## Related Skills

This skill is part of the Sui development skill suite:

| Skill | Description |
|-------|-------------|
| [sui-decompile](https://clawhub.ai/EasonC13/sui-decompile) | Fetch and read on-chain contract source code |
| [sui-move](https://clawhub.ai/EasonC13/sui-move) | Write and deploy Move smart contracts |
| **sui-coverage** | Analyze test coverage with security analysis |
| [sui-agent-wallet](https://clawhub.ai/EasonC13/sui-agent-wallet) | Build and test DApps frontend |

**Workflow:**
```
sui-decompile → sui-move → sui-coverage → sui-agent-wallet
    Study        Write      Test & Audit   Build DApps
```

All skills: <https://github.com/EasonC13-agent/sui-skills>
