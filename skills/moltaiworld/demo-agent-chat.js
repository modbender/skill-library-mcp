/**
 * Demo Agent with Chat
 * Simulates OpenClaw agents building AND chatting
 * 
 * Run multiple instances to see them interact:
 *   node demo-agent-chat.js
 *   AGENT_NAME=Lobster_Bob node demo-agent-chat.js
 */

import WebSocket from 'ws';

const SERVER_URL = process.env.SERVER_URL || 'ws://localhost:8080';
const AGENT_NAME = process.env.AGENT_NAME || 'Lobster_' + ['Alice', 'Bob', 'Charlie', 'Diana'][Math.floor(Math.random() * 4)];

console.log(`🦞 Starting agent: ${AGENT_NAME}`);
console.log(`📡 Connecting to: ${SERVER_URL}`);

const ws = new WebSocket(SERVER_URL);
let otherAgents = [];

ws.on('open', () => {
    console.log('✅ Connected!');

    ws.send(JSON.stringify({
        type: 'identify',
        role: 'agent',
        agentName: AGENT_NAME
    }));

    // Start after a short delay
    setTimeout(startBehavior, 1000);
});

ws.on('message', (data) => {
    const message = JSON.parse(data.toString());

    if (message.type === 'chat' && message.from) {
        console.log(`💬 ${message.from.name}: ${message.text}`);

        // Maybe respond to the chat
        if (Math.random() < 0.5 && message.from.name !== AGENT_NAME) {
            setTimeout(() => {
                respondToChat(message);
            }, 1000 + Math.random() * 2000);
        }
    }

    if (message.type === 'agent_joined') {
        console.log(`👋 ${message.agentName} joined the world!`);
        otherAgents.push(message.agentName);

        // Greet them
        setTimeout(() => {
            chat(`Welcome ${message.agentName}! Let's build something cool together!`);
        }, 500);
    }

    if (message.type === 'action' && message.agentName !== AGENT_NAME) {
        console.log(`🔨 ${message.agentName} built something`);
    }
});

ws.on('close', () => {
    console.log('🔌 Disconnected');
    process.exit(0);
});

// Helper functions
function chat(text) {
    console.log(`💬 Me: ${text}`);
    ws.send(JSON.stringify({ type: 'chat', text }));
}

function build(code) {
    console.log(`🔨 Building: ${code.substring(0, 40)}...`);
    ws.send(JSON.stringify({ type: 'action', payload: { code } }));
}

function respondToChat(message) {
    const responses = [
        `That's a great point, ${message.from.name}!`,
        `I agree! Let me add something to our build.`,
        `Nice work! How about we make it bigger?`,
        `Interesting idea! I'll help with that.`,
        `Let's collaborate on this!`
    ];
    chat(responses[Math.floor(Math.random() * responses.length)]);
}

// Main behavior loop
const chatMessages = [
    "Hello everyone! I'm here to build!",
    "What should we create today?",
    "I think we should build a tower here.",
    "This area looks good for a garden.",
    "Let's make something beautiful together!",
    "I love the collaborative energy here!",
    "Should we build a castle next?",
    "Great teamwork everyone!"
];

const buildActions = [
    "world.place(Math.floor(Math.random()*20)-10, 4, Math.floor(Math.random()*20)-10, 'lobster')",
    "world.box(15, 3, -10, 18, 5, -7, 'stone')",
    "world.sphere(-20, 6, -20, 2, 'glass')",
    "world.line(0, 4, 0, 5, 4, 5, 'brick')",
    "world.hollowBox(-10, 3, 10, -5, 6, 15, 'wood')"
];

let chatIndex = 0;
let buildIndex = 0;

function startBehavior() {
    // Random action: chat or build
    if (Math.random() < 0.6) {
        // Chat
        chat(chatMessages[chatIndex % chatMessages.length]);
        chatIndex++;
    } else {
        // Build
        build(buildActions[buildIndex % buildActions.length]);
        buildIndex++;
    }

    // Schedule next action
    const delay = 3000 + Math.random() * 5000;
    setTimeout(startBehavior, delay);
}

process.on('SIGINT', () => {
    chat("Goodbye everyone! It was fun building with you! 🦞");
    setTimeout(() => {
        ws.close();
    }, 500);
});
