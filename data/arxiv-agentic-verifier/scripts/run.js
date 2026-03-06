const AgenticVerifier = require('../index');

(async () => {
  const verifier = new AgenticVerifier();
  
  const problem = "Given a string S, output whether it is a palindrome.";
  const candidateCode = `
import sys
s = sys.stdin.read().strip()
if s == s[::-1]:
    print("True")
else:
    print("False")
`;

  console.log("Running verifier on palindrome checker...");
  try {
    const result = await verifier.verify(problem, candidateCode, 'python');
    console.log("Verification Result:", result);
  } catch (error) {
    console.error("Run Failed:", error);
  }
})();
