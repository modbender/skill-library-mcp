const { run, refreshIgToken, loadEnv, parseArgs } = require("./_common");

// refresh-token is special: run() already calls refreshIgToken(),
// so we just return the result from a dedicated call.
// We skip run() to avoid double-refresh and return the token data directly.
(async () => {
  try {
    const { named } = parseArgs();
    loadEnv(named.env);
    const result = await refreshIgToken();
    process.stdout.write(JSON.stringify(result, null, 2) + "\n");
    process.exit(0);
  } catch (err) {
    process.stdout.write(JSON.stringify({ error: err.message }) + "\n");
    process.exit(1);
  }
})();
