
const { formatPrompt, validateOutput, main } = require('./index.js');

console.log("Running HLE Reasoning Wrapper Tests...");

// Test 0: Load Check
if (!main()) {
    console.error("FAIL: Main function failed.");
    process.exit(1);
}

// Test 1: Prompt Generation
console.log("Test 1: Prompt Generation");
const prompt = formatPrompt("What is the integral of x^2?");
if (!prompt.includes("--- REASONING ---")) {
    console.error("FAIL: Prompt missing '--- REASONING ---'");
    process.exit(1);
}
if (!prompt.includes("--- FINAL ANSWER ---")) {
    console.error("FAIL: Prompt missing '--- FINAL ANSWER ---'");
    process.exit(1);
}
console.log("PASS: Prompt structure correct.");

// Test 2: Output Validation (Valid Case)
console.log("Test 2: Validation (Positive)");
const validOutput = `
--- REASONING ---
The integral of x^2 is x^3/3 + C.
--- FINAL ANSWER ---
x^3/3 + C
`;
if (!validateOutput(validOutput)) {
    console.error("FAIL: Valid output rejected.");
    process.exit(1);
}
console.log("PASS: Valid output accepted.");

// Test 3: Output Validation (Invalid Case)
console.log("Test 3: Validation (Negative)");
const invalidOutput = "Just the answer.";
if (validateOutput(invalidOutput)) {
    console.error("FAIL: Invalid output accepted.");
    process.exit(1);
}
console.log("PASS: Invalid output rejected.");

console.log("ALL TESTS PASSED.");
process.exit(0);
