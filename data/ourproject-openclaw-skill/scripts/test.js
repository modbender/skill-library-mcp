/**
 * Test Connection - Verify API key and URL configuration
 * Usage: node scripts/test.js
 */

const { makeRequest, loadConfig } = require('./api');

async function testConnection() {
    console.log('\n🔍 Testing connection to OurProject...\n');

    // Check config exists
    const config = loadConfig();
    console.log(`   URL: ${config.apiBaseUrl}`);
    console.log(`   Key: ${config.apiKey.slice(0, 11)}...`);
    console.log('');

    try {
        const result = await makeRequest('GET', '/integrations/me');
        const user = result.data?.user;

        if (user) {
            console.log('✅ Connection successful!\n');
            console.log(`   User: ${user.name}`);
            console.log(`   Email: ${user.email}`);
            console.log(`   Role: ${user.role || 'user'}`);
            console.log(`   Auth: ${result.data.authMethod || 'api_key'}`);
            console.log('\n🎉 You\'re all set! The skill is ready to use.\n');
        } else {
            console.error('❌ Unexpected response format');
            console.error('   Response:', JSON.stringify(result.data, null, 2));
            process.exit(1);
        }
    } catch (err) {
        console.error(`❌ Connection failed: ${err.message}`);
        console.error('\n   Check your API key and URL, then run: node scripts/setup.js\n');
        process.exit(1);
    }
}

testConnection();
