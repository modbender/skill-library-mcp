/**
 * Demo Agent Script
 * Simulates an OpenClaw agent connecting and creating things
 * 
 * Run with: node demo-agent.js
 */

import WebSocket from 'ws';

const SERVER_URL = process.env.SERVER_URL || 'ws://localhost:8080';
const AGENT_NAME = process.env.AGENT_NAME || 'DemoLobster_' + Math.random().toString(36).slice(2, 6);

console.log(`🦞 Starting demo agent: ${AGENT_NAME}`);
console.log(`📡 Connecting to: ${SERVER_URL}`);

const ws = new WebSocket(SERVER_URL);

ws.on('open', () => {
    console.log('✅ Connected!');

    // Identify as an agent
    ws.send(JSON.stringify({
        type: 'identify',
        role: 'agent',
        agentName: AGENT_NAME
    }));

    // Start creating things after a delay
    setTimeout(startCreating, 1000);
});

ws.on('message', (data) => {
    const message = JSON.parse(data.toString());
    console.log('📨 Received:', message.type);
});

ws.on('close', () => {
    console.log('🔌 Disconnected');
    process.exit(0);
});

ws.on('error', (error) => {
    console.error('❌ Error:', error.message);
});

// Demo actions
const demoActions = [
    // Build a small house
    "world.box(20, 3, 20, 25, 3, 25, 'stone')",  // Floor
    "world.hollowBox(20, 4, 20, 25, 7, 25, 'brick')",  // Walls
    "world.box(22, 4, 20, 23, 5, 20, 'air')",  // Door
    "world.place(22, 6, 22, 'glass')",  // Window
    "world.place(23, 6, 22, 'glass')",  // Window

    // Build a tower
    "for(let y = 0; y < 10; y++) world.place(-15, 3 + y, -15, 'stone')",
    "for(let y = 0; y < 10; y++) world.place(-15, 3 + y, -12, 'stone')",
    "for(let y = 0; y < 10; y++) world.place(-12, 3 + y, -15, 'stone')",
    "for(let y = 0; y < 10; y++) world.place(-12, 3 + y, -12, 'stone')",
    "world.sphere(-13.5, 15, -13.5, 3, 'lobster')",  // Lobster dome!

    // Create a path
    "world.line(0, 3, 0, 20, 3, 20, 'sand')",
    "world.line(0, 3, 0, -15, 3, -15, 'sand')",

    // Add some decorations
    "world.place(10, 4, 10, 'lobster')",
    "world.place(5, 4, 15, 'lobster')",
    "world.sphere(30, 6, 0, 2, 'glass')",
];

let actionIndex = 0;

function startCreating() {
    if (actionIndex >= demoActions.length) {
        console.log('🏁 Demo complete! Agent will stay connected...');
        return;
    }

    const code = demoActions[actionIndex];
    console.log(`🔨 Executing: ${code.substring(0, 50)}...`);

    ws.send(JSON.stringify({
        type: 'action',
        payload: { code }
    }));

    actionIndex++;

    // Random delay between actions (1-3 seconds)
    const delay = 1000 + Math.random() * 2000;
    setTimeout(startCreating, delay);
}

// Handle Ctrl+C
process.on('SIGINT', () => {
    console.log('\n👋 Shutting down demo agent...');
    ws.close();
});
