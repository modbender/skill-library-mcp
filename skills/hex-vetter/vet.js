const fs = require('fs');
const path = require('path');

function analyzeHex(filePath) {
    if (!fs.existsSync(filePath)) {
        console.error(`Error: File ${filePath} not found.`);
        return;
    }

    let data;
    try {
        data = fs.readFileSync(filePath);
    } catch (e) {
        console.error(`Error reading file: ${e.message}`);
        return;
    }

    const totalBytes = data.length;
    let nullBytesCount = 0;
    let controlCharsCount = 0;
    let nonAsciiCount = 0;

    const fullHex = [];
    for (let i = 0; i < totalBytes; i++) {
        const byte = data[i];
        fullHex.push(byte.toString(16).padStart(2, '0'));
        if (byte === 0) nullBytesCount++;
        if (byte < 32 && ![9, 10, 13].includes(byte)) controlCharsCount++;
        if (byte > 126) nonAsciiCount++;
    }

    console.log(`=== Hex Analysis Report (JS) for: ${filePath} ===`);

    // Output FULL HEX string for Agent/Tool consumption
    console.log(`\n[FULL_HEX_START]`);
    console.log(fullHex.join(' '));
    console.log(`[FULL_HEX_END]`);

    // Metrics
    console.log(`\n[Metrics]:`);
    console.log(`- Total Size: ${totalBytes} bytes`);
    console.log(`- Null Bytes (00): ${nullBytesCount}`);
    console.log(`- Control Characters: ${controlCharsCount}`);
    console.log(`- Non-ASCII Bytes: ${nonAsciiCount}`);

    // Signature Check (Basic patterns)
    const hexString = fullHex.join('');
    const signatures = [
        { name: "Reverse Shell / Socket Pattern", pattern: "2f62696e2f7368" }, // /bin/sh
        { name: "Sensitive File Access (.env)", pattern: "2e656e76" },        // .env
        { name: "Sensitive File Access (.ssh)", pattern: "2e737368" },       // .ssh
        { name: "Base64 Obfuscated Execution", pattern: "626173653634" }     // base64
    ];

    console.log(`\n[Signature Scan]:`);
    let foundSig = false;
    signatures.forEach(sig => {
        if (hexString.includes(sig.pattern)) {
            console.log(`⚠️ MATCH FOUND: ${sig.name}`);
            foundSig = true;
        }
    });
    if (!foundSig) console.log("✅ No common malicious signatures matched.");

    // Verdict
    console.log(`\n[Verdict]:`);
    const nonAsciiRatio = totalBytes > 0 ? nonAsciiCount / totalBytes : 0;
    if (nullBytesCount > 0 || controlCharsCount > 0 || foundSig) {
        console.log("🔴 HIGH RISK: Suspicious patterns or hidden binary detected.");
        console.log("⚠️  ATTENTION: Manual inspection by Human or Agent is MANDATORY for HIGH RISK files.");
    } else if (nonAsciiRatio > 0.1) {
        console.log("🟡 MEDIUM RISK: High non-ASCII density.");
    } else {
        console.log("🟢 LOW RISK: Looks like clean text.");
    }
    console.log("=".repeat(40));
}

const args = process.argv.slice(2);
if (args.length < 1) {
    console.log("Usage: node vet.js <file_path>");
} else {
    analyzeHex(args[0]);
}
