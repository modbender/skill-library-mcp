const { refreshFbToken, loadEnv, parseArgs } = require("./_common");

(async () => {
  try {
    const { named } = parseArgs();
    loadEnv(named.env);
    const result = await refreshFbToken();
    process.stdout.write(JSON.stringify(result, null, 2) + "\n");
    process.exit(0);
  } catch (err) {
    process.stdout.write(JSON.stringify({ error: err.message }) + "\n");
    process.exit(1);
  }
})();
