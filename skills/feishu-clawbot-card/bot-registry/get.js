
const { findBot } = require('./src/manager');

const query = process.argv[2];
if (!query) {
    console.error("Usage: node get.js <id_or_name>");
    process.exit(1);
}

const bot = findBot(query);
if (bot) {
    console.log(JSON.stringify(bot, null, 2));
} else {
    console.error(`Bot '${query}' not found.`);
    process.exit(1);
}
