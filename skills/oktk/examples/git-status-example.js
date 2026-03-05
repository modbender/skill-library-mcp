#!/usr/bin/env node

/**
 * Example: Git status filtering
 */

const GitFilter = require('../scripts/filters/GitFilter');

const sampleGitStatus = `On branch main
Your branch is ahead of 'origin/main' by 3 commits.
  (use "git push" to publish your local commits)

Changes not staged for commit:
  (use "git add <file>..." to include in what will be committed)
  (use "git restore <file>..." to discard changes in working directory)

  modified:   src/app.js
  modified:   src/utils.js
  modified:   package.json

Untracked files:
  (use "git add <file>..." to include in what will be committed)
  new-feature.js
  test-output.log

no changes added to commit (use "git add" and/or "git commit -a")`;

async function runExample() {
  console.log('========================================');
  console.log('Git Status Example');
  console.log('========================================\n');

  console.log('Original output:');
  console.log('----------------------------------------');
  console.log(sampleGitStatus);
  console.log('----------------------------------------\n');

  const originalTokens = sampleGitStatus.split(/\s+/).length;
  console.log(`Original tokens: ${originalTokens}\n`);

  const filter = new GitFilter();
  const filtered = await filter.apply(sampleGitStatus, { command: 'git status' });

  console.log('Filtered output:');
  console.log('----------------------------------------');
  console.log(filtered);
  console.log('----------------------------------------\n');

  const filteredTokens = filtered.split(/\s+/).length;
  const savings = ((originalTokens - filteredTokens) / originalTokens * 100).toFixed(1);

  console.log(`Filtered tokens: ${filteredTokens}`);
  console.log(`Tokens saved: ${originalTokens - filteredTokens}`);
  console.log(`Savings: ${savings}%`);
}

runExample().catch(console.error);
