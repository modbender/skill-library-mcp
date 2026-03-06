const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

function runPythonCode(code, args = {}) {
    // Basic sandboxing or execution wrapper
    const tempFile = path.join(__dirname, `temp_solve_${Date.now()}.py`);
    
    // Wrap the user code to print the result of answer(p)
    const wrapper = `
import sys
import sympy as sp
import json

# User code injection
${code}

if __name__ == "__main__":
    try:
        p = sp.Symbol('p')
        if 'answer' not in globals():
            print(json.dumps({"status": "error", "error": "Function answer(p) not defined"}))
            sys.exit(1)
            
        result = answer(p)
        print(json.dumps({"status": "success", "result": str(result)}))
    except Exception as e:
        print(json.dumps({"status": "error", "error": str(e)}))
`;
    
    fs.writeFileSync(tempFile, wrapper);
    
    return new Promise((resolve, reject) => {
        const proc = spawn('python3', [tempFile], { stdio: ['ignore', 'pipe', 'pipe'] });
        let stdout = '';
        let stderr = '';
        
        proc.stdout.on('data', (data) => stdout += data.toString());
        proc.stderr.on('data', (data) => stderr += data.toString());
        
        proc.on('close', (code) => {
            try {
                if (fs.existsSync(tempFile)) fs.unlinkSync(tempFile);
            } catch (e) {}
            
            if (code !== 0) {
                resolve({ status: "error", error: stderr || "Unknown error", exitCode: code });
            } else {
                try {
                    const json = JSON.parse(stdout.trim());
                    resolve(json);
                } catch (e) {
                    resolve({ status: "error", error: "Invalid JSON output from python", raw: stdout });
                }
            }
        });
    });
}

function formatPrompt(problemText, template) {
    return `Solve the following CritPt problem.
Hard constraints:
1) Do NOT call any tools except python-reasoning-lab (if needed) or internal reasoning.
2) Return ONLY executable python code.
3) Implement answer(...) exactly using the provided template.

Problem:
${problemText}

Template:
${template || ''}
`;
}

module.exports = {
    formatPrompt,
    runPythonCode
};

// If run directly, test with a simple problem
if (require.main === module) {
    const testCode = `
import sympy as sp
def answer(p):
    return (1-p)**2 + 3*(p/15)**2
`;
    runPythonCode(testCode).then(console.log).catch(console.error);
}
