
const { deleteBot } = require('./src/manager');

const id = process.argv[2];
if (!id) {
    console.error("Usage: node delete.js <id>");
    process.exit(1);
}

if (deleteBot(id)) {
    console.log(`Bot ${id} deleted.`);
} else {
    console.error(`Bot ${id} not found.`);
    process.exit(1);
}
