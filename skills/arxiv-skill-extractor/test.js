const { main } = require("./index.js");

async function run() {
  try {
    console.log("Running arxiv-skill-extractor tests...");
    await main();
    console.log("PASS: Execution completed without error.");
  } catch (e) {
    console.error("FAIL: Error during execution:", e);
    process.exit(1);
  }
}

run();
