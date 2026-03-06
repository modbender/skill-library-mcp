const { runPythonCode } = require('../index');

async function main() {
    const testCode = `
import sympy as sp
def answer(p):
    return (1-p)**2 + 3*(p/15)**2
`;
    console.log("Running test with valid code...");
    const result = await runPythonCode(testCode);
    console.log("Result:", result);
    
    if (result.status === "success") {
        console.log("Test Passed!");
    } else {
        console.error("Test Failed!");
        process.exit(1);
    }
}

main().catch(console.error);
