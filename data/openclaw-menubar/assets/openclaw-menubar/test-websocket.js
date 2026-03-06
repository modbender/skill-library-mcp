#!/usr/bin/env node

/**
 * Test WebSocket Gateway Client
 */

const GatewayClient = require('./gateway-client');

console.log('🧪 Testing WebSocket Connection to OpenClaw Gateway...\n');

async function test() {
    const client = new GatewayClient('http://localhost:18789');
    
    client.onStatusChange = (status) => {
        console.log('📡 Status:', status);
    };
    
    client.onMessage = (data) => {
        console.log('📨 Message:', data);
    };
    
    try {
        console.log('1️⃣ Connecting...');
        await client.connect();
        console.log('✅ Connected!\n');
        
        console.log('2️⃣ Sending test message...');
        const response = await client.sendMessage('Hey, test message from menu bar app!');
        console.log('✅ Response:', response);
        
        console.log('\n3️⃣ Disconnecting...');
        client.disconnect();
        console.log('✅ Disconnected');
        
        console.log('\n🎉 WebSocket client works!');
        process.exit(0);
        
    } catch (error) {
        console.error('\n❌ Error:', error.message);
        console.error('\nMake sure:');
        console.error('1. OpenClaw Gateway is running (openclaw status)');
        console.error('2. Gateway bind mode allows connections');
        process.exit(1);
    }
}

test();
