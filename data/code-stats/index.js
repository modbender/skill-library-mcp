const fs = require('fs');
const path = require('path');

function getStats(dir, stats = { files: 0, lines: 0, byExt: {} }) {
    try {
        const files = fs.readdirSync(dir);
        for (const file of files) {
            // Skip common ignore patterns
            if (file === '.git' || file === 'node_modules' || file === 'logs' || file === 'temp' || file === 'dist') continue;
            
            const fullPath = path.join(dir, file);
            let stat;
            try {
                stat = fs.statSync(fullPath);
            } catch (e) { continue; }

            if (stat.isDirectory()) {
                getStats(fullPath, stats);
            } else if (stat.isFile()) {
                stats.files++;
                const ext = path.extname(file) || '(no-ext)';
                stats.byExt[ext] = (stats.byExt[ext] || 0) + 1;
                
                // Count lines for text files roughly
                try {
                    // Peek at start to check if binary (heuristic)
                    const fd = fs.openSync(fullPath, 'r');
                    const buffer = Buffer.alloc(100);
                    const bytesRead = fs.readSync(fd, buffer, 0, 100, 0);
                    fs.closeSync(fd);
                    
                    let isBinary = false;
                    for (let i = 0; i < bytesRead; i++) {
                        if (buffer[i] === 0) { isBinary = true; break; }
                    }

                    if (!isBinary) {
                        const content = fs.readFileSync(fullPath, 'utf8');
                        const lines = content.split('\n').length;
                        stats.lines += lines;
                    }
                } catch (e) {}
            }
        }
    } catch (e) {
        console.error(`Error scanning ${dir}: ${e.message}`);
    }
    return stats;
}

if (require.main === module) {
    const root = process.argv[2] || process.cwd();
    console.log(JSON.stringify(getStats(root), null, 2));
}

module.exports = { getStats };
