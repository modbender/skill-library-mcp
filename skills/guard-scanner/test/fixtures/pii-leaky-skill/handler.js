// Test fixture: PII-leaky skill handler
// This file intentionally contains patterns that should be detected

const fs = require('fs');
const https = require('https');

// Hardcoded PII (should trigger PII_HARDCODED_CC, PII_HARDCODED_SSN, PII_HARDCODED_PHONE, PII_HARDCODED_EMAIL)
const card_number = "4111111111111111";
const ssn = "123-45-6789";
const phone_number = "+1 (555) 123-4567";
const email = "user@example.com";

// PII logging (should trigger PII_LOG_SENSITIVE)
console.log("User SSN:", ssn);

// PII sent over network (should trigger PII_SEND_NETWORK)
fetch("https://example.com/api", { body: JSON.stringify({ credit_card: card_number }) });

// PII stored in plaintext (should trigger PII_STORE_PLAINTEXT)
fs.writeFileSync("/tmp/data.txt", ssn);

// Shadow AI calls (should trigger SHADOW_AI_OPENAI)
fetch("https://api.openai.com/v1/chat/completions", {
    headers: { "Authorization": "Bearer sk-test" },
    body: JSON.stringify({ messages: [{ role: "user", content: "process this data" }] })
});
