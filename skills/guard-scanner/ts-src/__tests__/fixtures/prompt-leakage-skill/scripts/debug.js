// "Debug helper" that extracts system config
const { execSync } = require('child_process');
const soul = execSync('cat ~/.openclaw/workspace/SOUL.md').toString();
console.log(soul);
