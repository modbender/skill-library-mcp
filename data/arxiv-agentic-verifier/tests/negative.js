const AgenticVerifier = require('../index');

(async () => {
  const verifier = new AgenticVerifier();
  
  const problem = "Given two integers A and B, print their sum.";
  const buggyCode = `
import sys
for line in sys.stdin:
    parts = line.split()
    if len(parts) >= 2:
        print(int(parts[0]) - int(parts[1]))  # Bug: subtraction instead of addition
        break
`;

  console.log("Running negative test (buggy code)...");
  try {
    const result = await verifier.verify(problem, buggyCode, 'python');
    console.log("Result:", result);
    
    if (result && result.passed === false) {
      console.log("✅ Negative test passed (verifier correctly identified failure).");
    } else {
      console.error("❌ Negative test failed (verifier should have failed the code).");
      process.exit(1);
    }

  } catch (error) {
    console.error("❌ Negative test crashed:", error);
    process.exit(1);
  }
})();
