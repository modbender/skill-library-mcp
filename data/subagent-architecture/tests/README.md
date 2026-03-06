# Tests Directory

## Status: Placeholder

This directory is reserved for unit tests of the reference implementations.

## Planned Test Coverage

### lib/cost-estimator.test.js
- Formula accuracy verification
- Model cost calculations
- Complexity token estimates
- Recalibration logic
- Pattern adjustment accuracy

### lib/quality-scorer.test.js
- Rubric scoring correctness
- Dimension score calculations
- Recommendation generation
- Self-audit checklist validation

### lib/spawn-security-proxy.test.js
- Sanitization pattern matching
- Schema validation logic
- Deep sanitization recursion
- Attack vector defenses

### lib/spawn-researcher.test.js
- Source credibility scoring
- Multi-perspective synthesis
- Consensus identification
- Divergence detection

## Running Tests

Once implemented:
```bash
npm test
# or
node tests/cost-estimator.test.js
```

## Contributing

Test contributions welcome! Focus areas:
1. Edge cases in sanitization patterns
2. Cost estimation accuracy with real data
3. Schema validation for complex types
4. Quality scoring calibration

---

**Note:** Tests were deprioritized in v2.1 to focus on working implementations.
Test suite planned for v2.2 or community contribution.
