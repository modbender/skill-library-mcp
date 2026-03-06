const AgenticVerifier = require('../index');

(async () => {
  const verifier = new AgenticVerifier();
  
  const problem = "Given two integers A and B, print their sum.";
  const correctCode = `
import sys
for line in sys.stdin:
    parts = line.split()
    if len(parts) >= 2:
        print(int(parts[0]) + int(parts[1]))
        break
`;

  console.log("Running smoke test (correct code)...");
  try {
    const result = await verifier.verify(problem, correctCode, 'python');
    console.log("Smoke Test Result:", result);
    
    if (result && result.passed !== undefined) {
      console.log("✅ Smoke test passed (execution successful).");
    } else {
      console.error("❌ Smoke test failed (invalid result format).");
      process.exit(1);
    }

  } catch (error) {
    console.error("❌ Smoke test crashed:", error);
    process.exit(1);
  }
})();
