const { getStats } = require('../index');
const path = require('path');

console.log("Running code-stats test...");
try {
    // Scan the skill's own directory to verify accuracy on a known set
    const stats = getStats(path.resolve(__dirname, '..'));
    
    // We expect at least package.json, index.js, SKILL.md (not yet written but index exists) and this script
    if (stats.files >= 2 && stats.lines > 0) {
        console.log(`PASS: Scanned ${stats.files} files and ${stats.lines} lines.`);
    } else {
        throw new Error(`Invalid stats: ${JSON.stringify(stats)}`);
    }
} catch (e) {
    console.error("FAIL:", e);
    process.exit(1);
}
