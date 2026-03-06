# Advanced Newman Patterns

## Custom Reporters

### Creating a Custom Reporter

```javascript
// custom-reporter.js
function CustomReporter(emitter, reporterOptions, collectionRunOptions) {
    // newman.run event lifecycle:
    // start, beforeIteration, beforeItem, beforePrerequest, prerequest,
    // beforeRequest, request, beforeTest, test, beforeScript, script,
    // item, iteration, assertion, console, exception, beforeDone, done

    emitter.on('start', function (err, args) {
        console.log('Collection run started');
    });

    emitter.on('request', function (err, args) {
        if (err) {
            console.error('Request error:', err);
            return;
        }
        
        console.log(`[${args.request.method}] ${args.request.url.toString()}`);
        console.log(`Status: ${args.response.code} ${args.response.status}`);
        console.log(`Time: ${args.response.responseTime}ms`);
    });

    emitter.on('assertion', function (err, args) {
        if (err) {
            console.error(`✗ ${args.assertion}`, err.message);
        } else {
            console.log(`✓ ${args.assertion}`);
        }
    });

    emitter.on('done', function (err, summary) {
        if (err) {
            console.error('Collection run failed:', err);
            return;
        }

        console.log('\n=== Summary ===');
        console.log(`Total: ${summary.run.stats.requests.total}`);
        console.log(`Failed: ${summary.run.stats.requests.failed}`);
        console.log(`Assertions: ${summary.run.stats.assertions.total}`);
        console.log(`Failures: ${summary.run.stats.assertions.failed}`);
    });
}

module.exports = CustomReporter;
```

**Usage:**
```bash
newman run collection.json -r custom-reporter.js
```

### Slack Notification Reporter

```javascript
// slack-reporter.js
const https = require('https');

function SlackReporter(emitter, reporterOptions, collectionRunOptions) {
    const webhookUrl = reporterOptions.webhookUrl || process.env.SLACK_WEBHOOK;

    emitter.on('done', function (err, summary) {
        const stats = summary.run.stats;
        const failed = stats.requests.failed + stats.assertions.failed;
        
        const color = failed > 0 ? 'danger' : 'good';
        const status = failed > 0 ? 'Failed' : 'Passed';
        
        const payload = JSON.stringify({
            username: 'Newman',
            icon_emoji: ':test_tube:',
            attachments: [{
                color: color,
                title: `API Tests ${status}`,
                fields: [
                    { title: 'Requests', value: `${stats.requests.total}`, short: true },
                    { title: 'Failed', value: `${stats.requests.failed}`, short: true },
                    { title: 'Assertions', value: `${stats.assertions.total}`, short: true },
                    { title: 'Failures', value: `${stats.assertions.failed}`, short: true }
                ]
            }]
        });

        const options = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(payload)
            }
        };

        const req = https.request(webhookUrl, options);
        req.write(payload);
        req.end();
    });
}

module.exports = SlackReporter;
```

**Usage:**
```bash
newman run collection.json -r slack-reporter.js --reporter-slack-webhookUrl="https://hooks.slack.com/..."
```

## Advanced Test Patterns

### Dynamic Request Chaining

**Collection structure:**
1. Login → Get token
2. Create User → Get user_id
3. Update User → Use user_id from step 2
4. Delete User → Use user_id from step 2

**Step 1 - Login (Tests tab):**
```javascript
pm.test("Login successful", function() {
    pm.response.to.have.status(200);
    
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('token');
    
    // Store for next requests
    pm.collectionVariables.set("auth_token", jsonData.token);
});
```

**Step 2 - Create User (Pre-request):**
```javascript
// Use token from login
pm.request.headers.add({
    key: 'Authorization',
    value: `Bearer {{auth_token}}`
});
```

**Step 2 - Create User (Tests tab):**
```javascript
pm.test("User created", function() {
    const jsonData = pm.response.json();
    
    // Store user_id for subsequent requests
    pm.collectionVariables.set("created_user_id", jsonData.user_id);
});
```

**Step 3 - Update User (URL):**
```
PUT {{BASE_URL}}/users/{{created_user_id}}
```

### Conditional Request Execution

**Pre-request Script:**
```javascript
// Skip request based on condition
if (pm.environment.get("skip_payment_tests") === "true") {
    postman.setNextRequest(null); // Skip this request
}

// Or skip to specific request
if (pm.environment.get("user_type") === "guest") {
    postman.setNextRequest("Guest Flow - Get Products");
}
```

**Test Script:**
```javascript
// Conditional flow
pm.test("Admin check", function() {
    const isAdmin = pm.response.json().is_admin;
    
    if (isAdmin) {
        postman.setNextRequest("Admin - Dashboard");
    } else {
        postman.setNextRequest("User - Dashboard");
    }
});
```

### Data Validation Patterns

**Schema Validation:**
```javascript
const schema = {
    type: "object",
    required: ["id", "name", "email"],
    properties: {
        id: { type: "integer" },
        name: { type: "string", minLength: 1 },
        email: { type: "string", format: "email" },
        age: { type: "integer", minimum: 0, maximum: 150 }
    }
};

pm.test("Response matches schema", function() {
    const jsonData = pm.response.json();
    pm.expect(tv4.validate(jsonData, schema)).to.be.true;
});
```

**Array Validation:**
```javascript
pm.test("Users array validation", function() {
    const users = pm.response.json().users;
    
    pm.expect(users).to.be.an('array');
    pm.expect(users).to.have.lengthOf.at.least(1);
    
    // Validate each user
    users.forEach((user, index) => {
        pm.expect(user, `User ${index}`).to.have.all.keys('id', 'name', 'email');
        pm.expect(user.email, `User ${index} email`).to.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/);
    });
});
```

### Performance Testing

**Response Time Assertions:**
```javascript
pm.test("Response time < 200ms", function() {
    pm.expect(pm.response.responseTime).to.be.below(200);
});

pm.test("Response time within acceptable range", function() {
    const responseTime = pm.response.responseTime;
    pm.expect(responseTime).to.be.within(50, 500);
});
```

**Throughput Measurement:**
```javascript
// Collection-level variable: request_count, start_time

// Pre-request (first request only)
if (!pm.collectionVariables.get("start_time")) {
    pm.collectionVariables.set("start_time", Date.now());
    pm.collectionVariables.set("request_count", 0);
}

// Test (every request)
pm.test("Track throughput", function() {
    let count = pm.collectionVariables.get("request_count") || 0;
    pm.collectionVariables.set("request_count", count + 1);
    
    const startTime = pm.collectionVariables.get("start_time");
    const elapsed = (Date.now() - startTime) / 1000; // seconds
    const throughput = (count + 1) / elapsed;
    
    console.log(`Throughput: ${throughput.toFixed(2)} req/s`);
});
```

## Library Integration

### Using External Libraries

**CryptoJS for signing:**
```javascript
// Load in collection Pre-request or Test
const CryptoJS = require('crypto-js');

const timestamp = Date.now();
const nonce = Math.random().toString(36).substring(7);
const message = `${timestamp}${nonce}${pm.request.method}${pm.request.url.getPath()}`;

const signature = CryptoJS.HmacSHA256(message, pm.environment.get("API_SECRET"));
const signatureBase64 = CryptoJS.enc.Base64.stringify(signature);

pm.request.headers.add({
    key: 'X-Signature',
    value: signatureBase64
});
pm.request.headers.add({
    key: 'X-Timestamp',
    value: timestamp.toString()
});
pm.request.headers.add({
    key: 'X-Nonce',
    value: nonce
});
```

**Moment.js for dates:**
```javascript
const moment = require('moment');

// Dynamic date ranges
const startDate = moment().subtract(7, 'days').format('YYYY-MM-DD');
const endDate = moment().format('YYYY-MM-DD');

pm.environment.set("start_date", startDate);
pm.environment.set("end_date", endDate);
```

**Faker.js for test data:**
```javascript
const faker = require('faker');

pm.environment.set("random_email", faker.internet.email());
pm.environment.set("random_name", faker.name.findName());
pm.environment.set("random_address", faker.address.streetAddress());
```

## Advanced Environment Management

### Multi-Environment Variables

**Base environment (base.json):**
```json
{
  "name": "Base",
  "values": [
    {"key": "API_VERSION", "value": "v1"},
    {"key": "TIMEOUT", "value": "5000"},
    {"key": "RETRY_COUNT", "value": "3"}
  ]
}
```

**Override in specific environment (production.json):**
```json
{
  "name": "Production",
  "values": [
    {"key": "BASE_URL", "value": "https://api.production.com"},
    {"key": "TIMEOUT", "value": "10000"}
  ]
}
```

**Merge via script:**
```bash
#!/bin/bash
# Merge base + environment-specific

jq -s '.[0].values + .[1].values' base.json production.json > merged.json

newman run collection.json -e merged.json
```

### Encrypted Variables

**Encrypt sensitive values:**
```javascript
// scripts/encrypt-env.js
const crypto = require('crypto');
const fs = require('fs');

const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY; // 32-char key
const algorithm = 'aes-256-cbc';

function encrypt(text) {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv(algorithm, Buffer.from(ENCRYPTION_KEY), iv);
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return iv.toString('hex') + ':' + encrypted;
}

const env = JSON.parse(fs.readFileSync('environment.json'));
env.values.forEach(v => {
    if (v.key.includes('SECRET') || v.key.includes('PASSWORD')) {
        v.value = encrypt(v.value);
    }
});

fs.writeFileSync('environment.encrypted.json', JSON.stringify(env, null, 2));
```

**Decrypt in collection:**
```javascript
// Pre-request Script
const crypto = require('crypto');

function decrypt(text) {
    const parts = text.split(':');
    const iv = Buffer.from(parts[0], 'hex');
    const encrypted = parts[1];
    const decipher = crypto.createDecipheriv(
        'aes-256-cbc',
        Buffer.from(pm.environment.get("ENCRYPTION_KEY")),
        iv
    );
    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    return decrypted;
}

const encryptedApiKey = pm.environment.get("API_KEY_ENCRYPTED");
const apiKey = decrypt(encryptedApiKey);

pm.request.headers.add({
    key: 'Authorization',
    value: `Bearer ${apiKey}`
});
```

## Mock Server Integration

**Create mock from collection:**
```bash
# Start Postman mock server via CLI (requires Postman account)
# Or use json-server for local mocking

npm install -g json-server

# db.json
cat > db.json << 'EOF'
{
  "users": [
    {"id": 1, "name": "John Doe", "email": "john@example.com"}
  ],
  "posts": [
    {"id": 1, "title": "Hello", "userId": 1}
  ]
}
EOF

# Start mock
json-server --watch db.json --port 3000

# Run collection against mock
newman run collection.json --env-var "BASE_URL=http://localhost:3000"
```

## Performance Optimization

### Parallel Collection Execution

```bash
#!/bin/bash
# scripts/parallel-runner.sh

collections=(
    "collections/auth.json"
    "collections/users.json"
    "collections/products.json"
)

pids=()

for collection in "${collections[@]}"; do
    newman run "$collection" -e environments/staging.json &
    pids+=($!)
done

# Wait for all to complete
for pid in "${pids[@]}"; do
    wait $pid
    if [ $? -ne 0 ]; then
        echo "Collection failed (PID: $pid)"
        exit 1
    fi
done

echo "All collections passed!"
```

### Request Pooling

```javascript
// Collection Pre-request
if (!pm.collectionVariables.get("connection_pool")) {
    // Initialize connection pool simulation
    pm.collectionVariables.set("connection_pool", {
        max: 10,
        active: 0
    });
}
```

## Best Practices Summary

1. **Modular Collections**: Split by feature/domain for parallel execution
2. **DRY Principle**: Use collection/folder-level scripts to avoid duplication
3. **Environment Abstraction**: Never hardcode URLs or credentials
4. **Comprehensive Assertions**: Test status, schema, headers, and response time
5. **Error Handling**: Use try-catch in scripts to prevent collection failures
6. **Logging**: Use console.log strategically for debugging
7. **Version Control**: Track collections and environments in Git
8. **Documentation**: Use Postman descriptions for each request
9. **CI Integration**: Run Newman in every CI pipeline
10. **Security**: Encrypt secrets, use short-lived tokens, rotate credentials
