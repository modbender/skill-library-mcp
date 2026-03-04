const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

async function run() {
    const fileKey = process.argv[2];
    const fileName = process.argv[3];
    const docToken = process.argv[4];

    if (!fileKey || !fileName) {
        console.error("Missing fileKey or fileName");
        process.exit(1);
    }

    const localPath = path.join('/tmp', fileName);
    const txtPath = localPath + '.txt';

    console.log(`Processing: ${fileName}`);
    
    // In a real environment with direct API access, we'd download here.
    // For now, we simulate the logic assuming the file is accessible or 
    // will be provided to the screening script.
    
    try {
        // If file exists (manually placed or downloaded by middleware)
        if (fs.existsSync(localPath)) {
            execSync(`pdftotext "${localPath}" "${txtPath}"`);
            const content = fs.readFileSync(txtPath, 'utf8');
            
            // We use the batch screen logic or direct screen
            const output = execSync(`node ${path.join(__dirname, 'screen_resume.js')} "${txtPath}" --lang "PHP Engineer" --yoe "10"`, { encoding: 'utf8' });
            
            console.log("--- EVALUATION RESULT ---");
            console.log(output);
            
            // Cleanup
            fs.unlinkSync(txtPath);
        } else {
            console.log(`[WAITING]: Please ensure ${localPath} is available for processing.`);
        }
    } catch (e) {
        console.error(e.message);
    }
}

run();
