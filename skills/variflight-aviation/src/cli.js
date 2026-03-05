#!/usr/bin/env node

/**
 * Variflight CLI Entry
 * Usage: variflight <command> [args...]
 */

const commands = {
    search: require('./commands/search'),
    info: require('./commands/info'),
    comfort: require('./commands/comfort'),
    weather: require('./commands/weather'),
    transfer: require('./commands/transfer'),
    track: require('./commands/track')
};

function showHelp() {
    console.log(`
✈️  Variflight Aviation Skill v1.0.0

Usage: variflight <command> [arguments]

Commands:
  search  <dep> <arr> <date>    搜索航班
  info    <fnum> <date>         查询航班详情
  comfort <fnum> <date>         舒适度指数
  weather <airport>             机场天气
  transfer <depcity> <arrcity> <date>  中转方案
  track   <anum>                飞机追踪

Examples:
  variflight search PEK SHA 2026-02-20
  variflight info MU2157 2026-02-20
  variflight comfort CA1501 2026-02-20
  variflight weather PEK
  variflight transfer BJS SHA 2026-02-20
  variflight track B-308M

Environment:
  VARIFLIGHT_API_KEY    Required. 飞常准 API Key
`);
}

async function main() {
    const [command, ...args] = process.argv.slice(2);

    if (!command || command === '--help' || command === '-h') {
        showHelp();
        process.exit(0);
    }

    if (!commands[command]) {
        console.error(`❌ Unknown command: ${command}`);
        showHelp();
        process.exit(1);
    }

    try {
        await commands[command](...args);
    } catch (error) {
        console.error(`❌ Error: ${error.message}`);
        if (process.env.DEBUG) {
            console.error(error.stack);
        }
        process.exit(1);
    }
}

main();