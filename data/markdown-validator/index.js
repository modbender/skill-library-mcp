const fs = require('fs');
const path = require('path');

function checkFile(filePath) {
    if (!fs.existsSync(filePath)) {
        return { file: filePath, valid: false, error: 'File not found' };
    }

    const content = fs.readFileSync(filePath, 'utf8');
    const links = [];
    const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
    let match;

    while ((match = linkRegex.exec(content)) !== null) {
        links.push({ text: match[1], url: match[2], line: (content.substring(0, match.index).match(/\n/g) || []).length + 1 });
    }

    const brokenLinks = [];
    for (const link of links) {
        if (link.url.startsWith('http')) {
            continue; // Skip external links for now to avoid network calls
        }
        if (link.url.startsWith('#')) {
            continue; // Skip anchors within same file
        }
        
        // Handle relative paths
        const targetPath = path.resolve(path.dirname(filePath), link.url.split('#')[0]);
        if (!fs.existsSync(targetPath)) {
            brokenLinks.push(link);
        }
    }

    return {
        file: filePath,
        valid: brokenLinks.length === 0,
        brokenLinks: brokenLinks.map(l => ({ text: l.text, url: l.url, line: l.line }))
    };
}

function scanDirectory(dirPath) {
    if (!fs.existsSync(dirPath)) {
        return { error: 'Directory not found' };
    }
    
    let results = [];
    const files = fs.readdirSync(dirPath);
    
    for (const file of files) {
        const fullPath = path.join(dirPath, file);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory() && file !== 'node_modules' && file !== '.git') {
            results = results.concat(scanDirectory(fullPath));
        } else if (stat.isFile() && file.endsWith('.md')) {
            results.push(checkFile(fullPath));
        }
    }
    
    return results;
}

async function main(args) {
    const target = args && args.target ? args.target : '.';
    const absTarget = path.resolve(process.cwd(), target);
    
    if (fs.statSync(absTarget).isFile()) {
        return [checkFile(absTarget)];
    } else {
        return scanDirectory(absTarget);
    }
}

module.exports = { main, checkFile, scanDirectory };

if (require.main === module) {
    const target = process.argv[2] || '.';
    const report = main({ target });
    console.log(JSON.stringify(report, null, 2));
}
