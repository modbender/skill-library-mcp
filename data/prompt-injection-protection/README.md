# Prompt Injection Protection Skill

This skill provides comprehensive protection against prompt injection attacks when processing external content such as websites, emails, documents, and other untrusted input sources. It includes real-time security alerts for suspicious activities.

## Features

- Content sanitization and validation
- Prompt injection detection and filtering
- Secure processing of web content
- Safe extraction of information from untrusted sources
- Protection against jailbreak attempts
- **NEW: Real-time security alerts for suspicious commands**
- **NEW: Detection of system file access attempts**
- **NEW: User confirmation for risky operations**

## Security Alert System

The skill now includes a comprehensive security notification system that:

- Alerts you when suspicious commands are detected
- Warns about system file access attempts
- Notifies you of credential/password file access
- Flags potential injection attempts in web content
- Requires user confirmation for risky operations

## Usage Examples

### Basic Usage

```javascript
const PromptInjectionProtection = require('./index.js');
const protection = new PromptInjectionProtection();

// Set up security alert callback
protection.setSecurityAlertCallback(async (alertInfo) => {
  console.log(`🚨 SECURITY ALERT: ${alertInfo.type}`);
  console.log(`   Severity: ${alertInfo.severity}`);
  console.log(`   Action Required: ${alertInfo.actionRequired}`);
});

// Process external content safely
const result = protection.processExternalContent(untrustedContent, {
  maxLength: 5000,
  strictMode: true
});

if (result.isSafe) {
  // Process the sanitized content
  console.log(result.sanitized);
} else {
  // Handle unsafe content
  console.warn('Potentially unsafe content detected', result.injectionCheck);
}
```

### Command Pre-Checking (NEW FEATURE)

```javascript
// Check a command before executing it
const commandCheck = await protection.preCheckCommand('sudo rm -rf /', {
  source: 'user_input'
});

if (commandCheck.safeToExecute) {
  // Execute the command safely
} else {
  console.log(commandCheck.message); // Warning message with risks
}
```

### File Operation Pre-Checking (NEW FEATURE)

```javascript
// Check a file operation before executing it
const fileCheck = await protection.preCheckFileOperation('/etc/passwd', 'read', {
  source: 'file_access_request'
});

if (fileCheck.safeToAccess) {
  // Perform the file operation
} else {
  console.log(fileCheck.message); // Warning message with risks
}
```

### Web Content Extraction

```javascript
// Safely extract text from HTML content
const extracted = protection.extractFromWebContent(htmlContent, {
  extractTextOnly: true,
  maxLength: 3000
});
```

### Creating Safe Context

```javascript
// Create a safe context that isolates external content
const safeContext = protection.createSafeContext(
  'user',
  externalContent,
  'Additional context here'
);
```

## Integration with Web Fetching

When fetching content from websites, always process it through the protection mechanism:

```javascript
const { secureProcess, safeExtractWebContent } = require('./web-processor.js');

// Example of securing fetched web content
const rawContent = await tools.web_fetch({ url: 'https://example.com' });
const secured = secureProcess(rawContent, { strictMode: true });

if (secured.isSafe) {
  // Use the sanitized content safely
}
```

## Security Patterns Detected

The skill detects common prompt injection techniques including:
- Instruction override attempts
- Role-playing commands
- System message hijacking
- Unicode direction override characters
- Malicious command execution attempts
- HTML/script injection patterns
- **NEW: System file access patterns**
- **NEW: Credential/password access patterns**

## Security Alert Callback

To enable security notifications, set up a callback function:

```javascript
protection.setSecurityAlertCallback(async (alertInfo) => {
  // Handle the security alert
  // alertInfo contains details about the threat
});
```

## Configuration Options

- `maxLength`: Maximum content length allowed
- `strictMode`: Whether to throw errors on detected threats
- `allowHtml`: Whether to preserve HTML tags (sanitized)
- `extractTextOnly`: Whether to extract only text content from HTML

## Available Commands

- `/secure-web-fetch <URL>` - Safely fetch and process web content with security alerts

## Security Levels

- **Low Risk**: Minor injection patterns detected, content sanitized
- **Medium Risk**: Multiple injection patterns or system command patterns detected
- **High Risk**: Critical security threats requiring immediate attention