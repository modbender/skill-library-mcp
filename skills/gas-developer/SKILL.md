---
name: gas-developer
description: Google Apps Script specialist. Spreadsheet automation, Gmail, Calendar integration.
---

# GAS Developer

Build Google Apps Script solutions for Spreadsheet automation, Gmail, Calendar, and Drive integration.

## Instructions

1. **Understand the requirement**: What Google service? What automation? What trigger?
2. **Choose the right approach**:

   | Use Case | Service | Trigger |
   |----------|---------|---------|
   | Data processing | Spreadsheet | onEdit / time-driven |
   | Email automation | Gmail | time-driven |
   | Calendar sync | Calendar | time-driven / onChange |
   | File management | Drive | time-driven |
   | Form processing | Forms | onFormSubmit |
   | Web dashboard | HTML Service | doGet |

3. **Write clean GAS code** following best practices below.
4. **Test thoroughly** — use Logger.log() for debugging.
5. **Document the setup** — triggers, permissions, configuration.

## Templates

### Spreadsheet — Read/Write
```javascript
function processSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('Data');
  const data = sheet.getDataRange().getValues();
  
  // Skip header row
  for (let i = 1; i < data.length; i++) {
    const [name, email, status] = data[i];
    if (status === '') {
      // Process row
      sheet.getRange(i + 1, 3).setValue('Processed');
    }
  }
}
```

### Gmail — Send with Template
```javascript
function sendTemplateEmail(to, subject, templateName) {
  const template = HtmlService.createTemplateFromFile(templateName);
  const htmlBody = template.evaluate().getContent();
  
  GmailApp.sendEmail(to, subject, '', {
    htmlBody: htmlBody,
    name: 'Your Name'
  });
}
```

### External API Call
```javascript
function callExternalApi(endpoint, apiKey) {
  const options = {
    method: 'get',
    headers: { 'Authorization': 'Bearer ' + apiKey },
    muteHttpExceptions: true
  };
  
  const response = UrlFetchApp.fetch(endpoint, options);
  const code = response.getResponseCode();
  
  if (code !== 200) {
    Logger.log('API error: ' + code + ' ' + response.getContentText());
    return null;
  }
  
  return JSON.parse(response.getContentText());
}
```

### Time-Driven Trigger Setup
```javascript
function createDailyTrigger() {
  // Delete existing triggers for this function
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(t => {
    if (t.getHandlerFunction() === 'dailyTask') {
      ScriptApp.deleteTrigger(t);
    }
  });
  
  // Create new daily trigger at 9 AM
  ScriptApp.newTrigger('dailyTask')
    .timeBased()
    .atHour(9)
    .everyDays(1)
    .create();
}
```

### Error Handling Pattern
```javascript
function safeExecute(fn, context) {
  try {
    return fn();
  } catch (error) {
    Logger.log('Error in ' + context + ': ' + error.message);
    // Optional: send error notification
    GmailApp.sendEmail('admin@example.com', 
      'GAS Error: ' + context, error.stack);
    return null;
  }
}
```

## Best Practices

- **Batch operations**: Use `getValues()` / `setValues()` instead of cell-by-cell
- **Quota awareness**: GAS has daily quotas (email: 100/day free, URL fetch: 20,000/day)
- **Cache**: Use `CacheService` for expensive API calls
- **Properties**: Store config in `PropertiesService` (not hardcoded)
- **Lock**: Use `LockService` to prevent concurrent trigger execution

## Security

- **Never hardcode API keys** — use `PropertiesService.getScriptProperties()`
- **Validate user input** — especially in web apps (doGet/doPost)
- **Limit sharing** — deploy as "Execute as me, accessible to specific users"
- **Review permissions** — GAS requests broad OAuth scopes; explain to client

## Delivery Checklist

```
□ Code tested with sample data
□ Triggers documented and set up
□ Error handling in place
□ Setup instructions included
□ API keys stored in Properties (not code)
□ Permissions explained to client
```

## Requirements

- Google account with Apps Script access
- No local dependencies — runs entirely in Google Cloud
