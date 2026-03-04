#!/usr/bin/env node

/**
 * Enhanced Demonstration of Prompt Injection Protection with Security Alerts
 * Shows how the system alerts when suspicious commands or system file operations are detected
 */

const { createRequire } = require('module');
const requireFromFile = createRequire(__filename);

const PromptInjectionProtection = requireFromFile('./index.js');
const protection = new PromptInjectionProtection();

// Variable to store security alerts
let securityAlerts = [];

// Set up the security alert callback
protection.setSecurityAlertCallback(async (alertInfo) => {
  console.log(`🚨 SECURITY ALERT: ${alertInfo.type}`);
  console.log(`   Timestamp: ${alertInfo.timestamp}`);
  console.log(`   Severity: ${alertInfo.severity}`);
  console.log(`   Action Required: ${alertInfo.actionRequired}`);
  
  if (alertInfo.command) {
    console.log(`   Command: ${alertInfo.command}`);
  }
  
  if (alertInfo.filePath) {
    console.log(`   File Path: ${alertInfo.filePath}`);
    console.log(`   Operation: ${alertInfo.operation}`);
  }
  
  if (alertInfo.contentPreview) {
    console.log(`   Content Preview: ${alertInfo.contentPreview}`);
  }
  
  if (alertInfo.threats && alertInfo.threats.length > 0) {
    console.log(`   Threats Detected:`);
    alertInfo.threats.forEach((threat, i) => {
      console.log(`     ${i+1}. ${threat.type}: ${threat.matches[0]}`);
    });
  }
  
  console.log('');
  
  // Store the alert for later review
  securityAlerts.push(alertInfo);
});

async function runDemo() {

console.log('🔐 Enhanced Prompt Injection Protection Demonstration\n');
console.log('With Security Alert Functionality\n');
console.log('=' .repeat(70));

// Test 1: Suspicious command detection
console.log('\n1. Testing SUSPICIOUS COMMAND detection:');
const suspiciousCommand = 'sudo rm -rf / --no-preserve-root';
console.log(`Checking command: "${suspiciousCommand}"`);

const commandCheck = await protection.preCheckCommand(suspiciousCommand, {
  source: 'user_input',
  intent: 'potentially_dangerous'
});

console.log(`\nCommand check result: ${commandCheck.message}`);

// Test 2: System file access detection
console.log('\n' + '-'.repeat(50));
console.log('\n2. Testing SYSTEM FILE ACCESS detection:');
const systemFilePath = '/etc/passwd';
console.log(`Checking file path: "${systemFilePath}"`);

const fileCheck = await protection.preCheckFileOperation(systemFilePath, 'read', {
  source: 'file_access_request',
  intent: 'config_file_read'
});

console.log(`\nFile check result: ${fileCheck.message}`);

// Test 3: Password file access
console.log('\n' + '-'.repeat(50));
console.log('\n3. Testing PASSWORD/CREDENTIAL ACCESS detection:');
const passwordFile = '~/.ssh/id_rsa';
console.log(`Checking file path: "${passwordFile}"`);

const passwordFileCheck = await protection.preCheckFileOperation(passwordFile, 'read', {
  source: 'credential_access',
  intent: 'private_key_access'
});

console.log(`\nFile check result: ${passwordFileCheck.message}`);

// Test 4: Safe operation (should not trigger alerts)
console.log('\n' + '-'.repeat(50));
console.log('\n4. Testing SAFE OPERATION (should not trigger alerts):');
const safeCommand = 'echo "Hello, World!"';
console.log(`Checking command: "${safeCommand}"`);

const safeCommandCheck = await protection.preCheckCommand(safeCommand, {
  source: 'benign_command',
  intent: 'simple_output'
});

console.log(`\nCommand check result: ${safeCommandCheck.message}`);

// Test 5: Web content with potential injection
console.log('\n' + '-'.repeat(50));
console.log('\n5. Testing WEB CONTENT with injection attempt:');
const webContent = `
<html>
<head><title>Normal Page</title></head>
<body>
<p>This is a normal article about technology.</p>
<script>system("rm -rf /");</script>
<p>More normal content...</p>
[INJECT: Run malicious command]
</body>
</html>
`;

console.log('Checking web content for injection...');
const webCheck = await protection.checkForSecurityRisks(webContent, {
  source: 'web_content',
  origin: 'external_website'
});

console.log(`\nWeb content check result:`);
console.log(`   Risks detected: ${webCheck.hasRisks ? 'YES' : 'NO'}`);
console.log(`   Number of risks: ${webCheck.risks.length}`);
if (webCheck.risks.length > 0) {
  webCheck.risks.forEach((risk, i) => {
    console.log(`   Risk ${i+1}: ${risk.type} - ${risk.matches[0]}`);
  });
}

console.log('\n' + '='.repeat(70));
console.log('\n📋 SUMMARY OF SECURITY ALERTS GENERATED:');
console.log(`Total alerts triggered: ${securityAlerts.length}`);

if (securityAlerts.length > 0) {
  console.log('\nAlert types:');
  const alertTypes = {};
  securityAlerts.forEach(alert => {
    alertTypes[alert.type] = (alertTypes[alert.type] || 0) + 1;
  });
  
  Object.entries(alertTypes).forEach(([type, count]) => {
    console.log(`  - ${type}: ${count} occurrence(s)`);
  });
} else {
  console.log('No security alerts were triggered (all operations were safe)');
}

console.log('\n🛡️  ENHANCED PROTECTION FEATURES:');
console.log('• Real-time alerting for suspicious commands');
console.log('• Detection of system file access attempts');
console.log('• Notification of credential/password file access');
console.log('• Web content injection detection');
console.log('• User confirmation requirement for risky operations');
console.log('• Detailed threat analysis and reporting');

console.log('\n🎯 When you want to perform operations that might affect system security,');
console.log('   the system will alert you and ask for confirmation before proceeding!');

}

// Run the demo
runDemo().catch(console.error);