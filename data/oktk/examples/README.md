# oktk Examples

This directory contains example usage and demonstrations of oktk filters.

## Running Examples

Each example can be run directly:

```bash
# Git examples
node examples/git-status-example.js

# Test output examples
node examples/npm-test-example.js

# File listing examples
node examples/ls-example.js

# Network examples
node examples/curl-example.js

# Search examples
node examples/grep-example.js

# Run all examples
node examples/run-all.js
```

## Example Files

### Git Examples

- `git-status-example.js` - Demonstrate git status filtering
- `git-log-example.js` - Demonstrate git log filtering
- `git-diff-example.js` - Demonstrate git diff filtering

### Test Examples

- `npm-test-example.js` - Demonstrate npm test filtering
- `pytest-example.js` - Demonstrate pytest filtering

### File Operation Examples

- `ls-example.js` - Demonstrate ls filtering
- `find-example.js` - Demonstrate find filtering

### Network Examples

- `curl-example.js` - Demonstrate curl filtering
- `json-api-example.js` - Demonstrate JSON API filtering

### Search Examples

- `grep-example.js` - Demonstrate grep filtering

## Comparison: Raw vs Filtered

Run the `run-all.js` script to see side-by-side comparisons:

```bash
node examples/run-all.js
```

This shows:
- Original command output
- Filtered output
- Token savings
- Percentage reduction

## Creating Custom Examples

To create your own example:

```javascript
#!/usr/bin/env node

const OKTK = require('../scripts/oktk');

const oktk = new OKTK();

// Sample input
const input = `... your command output ...`;

// Apply filter
const filter = new YourFilter();
const output = await filter.apply(input, { command: 'your-command' });

console.log('Filtered output:');
console.log(output);
```

See individual example files for more details.
