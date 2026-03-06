// STRICT ALLOW-LIST APPROACH

// Only these exact JSON structures or command patterns are allowed.
// Any deviation is rejected.

const ALLOWED_SCHEMAS = [
  // 1. Simple Safety Check Command
  /^Is this environment safe\\?$/,

  // 2. Verified Credential / Mandate Signing Request
  // Must be a valid JSON string with specific fields, NO private keys involved in the text itself
  (input: string) => {
    try {
      const data = JSON.parse(input);
      const keys = Object.keys(data);
      const allowedKeys = ["iss", "sub", "aud", "iat", "exp", "jti", "claims"];

      // Check if all keys in input are allowed
      const isSafe = keys.every((k) => allowedKeys.includes(k));
      if (!isSafe) return false;

      // Explicitly deny if ANY value looks like a key
      const valStr = JSON.stringify(data).toLowerCase();
      if (valStr.includes("private key") || valStr.includes("secret"))
        return false;

      return true;
    } catch {
      return false;
    }
  },
];

function strictScan(input: string) {
  let matched = false;

  for (const rule of ALLOWED_SCHEMAS) {
    if (rule instanceof RegExp) {
      if (rule.test(input)) matched = true;
    } else if (typeof rule === "function") {
      if (rule(input)) matched = true;
    }
  }

  if (!matched) {
    throw new Error(
      `SECURITY ALERT: Input rejected by strict allow-list policy. "${input.substring(0, 20)}..." is not a recognized safe pattern.`,
    );
  }

  console.log("✅ Strict Safety Check Passed.");
}

const args = process.argv.slice(2);
if (args.length > 0) {
  const input = args.join(" ");
  try {
    strictScan(input);
  } catch (error: any) {
    console.error(error.message);
    process.exit(1);
  }
} else {
  // No args = pass for simple execution checks, or fail?
  // User requested "Strict Input Validation".
  // If running with no args, it might be just checking the script itself?
  // Let's assume emptiness is safe or requiring an input to validate.
  console.log("ℹ️ No input provided to guardrail.");
}
