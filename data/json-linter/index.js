const fs = require('fs');
const path = require('path');

// Recursive function to find .json files
function findJsonFiles(dir, fileList = []) {
    try {
        const files = fs.readdirSync(dir);
        for (const file of files) {
            const filePath = path.join(dir, file);
            // Skip common ignore patterns
            if (file === 'node_modules' || file === '.git' || file === 'temp' || file === 'logs') continue;

            const stat = fs.statSync(filePath);
            if (stat.isDirectory()) {
                findJsonFiles(filePath, fileList);
            } else if (path.extname(file) === '.json') {
                fileList.push(filePath);
            }
        }
    } catch (err) {
        // Skip unreadable directories
    }
    return fileList;
}

// Function to validate a list of files
function validateJsonFiles(rootDir) {
    const report = {
        scanned_at: new Date().toISOString(),
        root_dir: rootDir,
        total_files: 0,
        valid_files: 0,
        invalid_files: 0,
        errors: []
    };

    const files = findJsonFiles(rootDir);
    report.total_files = files.length;

    for (const filePath of files) {
        try {
            const content = fs.readFileSync(filePath, 'utf8');
            JSON.parse(content);
            report.valid_files++;
        } catch (e) {
            report.invalid_files++;
            report.errors.push({
                path: path.relative(process.cwd(), filePath),
                error: e.message
            });
        }
    }

    return report;
}

// CLI handler
if (require.main === module) {
    const args = process.argv.slice(2);
    let targetDir = process.cwd();

    // Simple arg parser for --dir
    if (args.includes('--dir')) {
        const dirIndex = args.indexOf('--dir');
        if (dirIndex !== -1 && args[dirIndex + 1]) {
            targetDir = path.resolve(args[dirIndex + 1]);
        }
    } else if (args[0] && !args[0].startsWith('--')) {
        // Assume first arg is dir if not flag
        targetDir = path.resolve(args[0]);
    }

    // Default to current directory if no args
    console.log(JSON.stringify(validateJsonFiles(targetDir), null, 2));
}

module.exports = {
    findJsonFiles,
    validateJsonFiles
};
