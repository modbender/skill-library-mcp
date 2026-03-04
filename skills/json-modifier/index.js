const fs = require('fs');
const path = require('path');
const jsonpatch = require('fast-json-patch');

// CLI Arguments:
// --file <path>        Path to JSON file to modify
// --patch <json>       JSON Patch array (RFC 6902)
// --patch-file <path>  Path to JSON Patch file
// --out <path>         Output path (optional, default: overwrite)
// --indent <number>    Indentation (default: 2)

function main() {
    const args = process.argv.slice(2);
    let targetFile = '';
    let patchContent = '';
    let outFile = '';
    let indent = 2;

    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        if (arg === '--file') {
            targetFile = args[++i];
        } else if (arg === '--patch') {
            patchContent = args[++i];
        } else if (arg === '--patch-file') {
            const pPath = args[++i];
            try {
                patchContent = fs.readFileSync(pPath, 'utf8');
            } catch (err) {
                console.error(`Error reading patch file: ${err.message}`);
                process.exit(1);
            }
        } else if (arg === '--out') {
            outFile = args[++i];
        } else if (arg === '--indent') {
            indent = parseInt(args[++i], 10);
        }
    }

    if (!targetFile) {
        console.error('Usage: node skills/json-modifier/index.js --file <path> [--patch <json> | --patch-file <path>] [--out <path>]');
        process.exit(1);
    }

    if (!patchContent) {
        console.error('Error: No patch provided via --patch or --patch-file');
        process.exit(1);
    }

    let patch;
    try {
        patch = JSON.parse(patchContent);
    } catch (err) {
        console.error(`Error parsing patch JSON: ${err.message}`);
        process.exit(1);
    }

    if (!Array.isArray(patch)) {
        console.error('Error: Patch must be a JSON array (RFC 6902)');
        process.exit(1);
    }

    let document;
    try {
        const fileContent = fs.readFileSync(targetFile, 'utf8');
        document = JSON.parse(fileContent);
    } catch (err) {
        console.error(`Error reading target file: ${err.message}`);
        process.exit(1);
    }

    try {
        const errors = jsonpatch.validate(patch, document);
        if (errors) {
            console.error('Patch validation failed:', JSON.stringify(errors, null, 2));
            process.exit(1);
        }

        const newDocument = jsonpatch.applyPatch(document, patch).newDocument;
        
        const outputContent = JSON.stringify(newDocument, null, indent);
        const outputPath = outFile || targetFile;

        // Atomic write via temp file + rename to avoid partial writes
        const tempPath = outputPath + '.tmp.' + Date.now();
        fs.writeFileSync(tempPath, outputContent);
        fs.renameSync(tempPath, outputPath);

        console.log(`Successfully applied patch to ${outputPath}`);
    } catch (err) {
        console.error(`Error applying patch: ${err.message}`);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = { main };
