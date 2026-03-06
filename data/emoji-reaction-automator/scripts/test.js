const { suggestReaction } = require('../index.js');

const testCases = [
  { text: "This is great!", expected: "positive" },
  { text: "Something is broken", expected: "negative" },
  { text: "Haha that's funny", expected: "funny" },
  { text: "Why did this happen?", expected: "curious" },
  { text: "Finally launched!", expected: "excited" },
  { text: "Just a regular day", expected: "neutral" }
];

let failed = false;

testCases.forEach((tc) => {
  const result = suggestReaction(tc.text);
  console.log(`Input: "${tc.text}" -> ${JSON.stringify(result)}`);
  
  if (result.category !== tc.expected) {
    console.error(`❌ Expected category ${tc.expected}, got ${result.category}`);
    failed = true;
  } else {
    console.log(`✅ Passed: ${result.category}`);
  }
});

if (failed) {
  process.exit(1);
} else {
  console.log("All tests passed!");
  process.exit(0);
}
