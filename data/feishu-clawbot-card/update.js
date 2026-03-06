
const { upsertBot } = require('./src/manager');

const args = process.argv.slice(2);
let jsonStr = "";

// Parse --json arg
const jsonIndex = args.indexOf('--json');
if (jsonIndex !== -1 && args[jsonIndex + 1]) {
    jsonStr = args[jsonIndex + 1];
} else if (args[0] && args[0].startsWith('{')) {
    jsonStr = args[0]; // Allow passing JSON directly as first arg
}

if (!jsonStr) {
    console.error("Usage: node update.js --json '{\"name\":\"BotName\", ...}'");
    process.exit(1);
}

try {
    const data = JSON.parse(jsonStr);
    const result = upsertBot(data);
    console.log(JSON.stringify(result, null, 2));
} catch (e) {
    console.error("Error updating bot:", e.message);
    process.exit(1);
}
