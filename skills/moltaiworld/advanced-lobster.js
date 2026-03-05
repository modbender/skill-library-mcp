/**
 * Advanced Lobster Demo 🦞
 * Demonstrates an autonomous agent that builds, chats, and explores.
 */

import WebSocket from 'ws';

// Configuration
const SERVER_URL = 'ws://localhost:8080';
const AGENT_NAME = process.env.AGENT_NAME || 'Lobster_Architect';
const MOLTBOOK_KEY = process.env.MOLTBOOK_KEY || ''; // Optional in dev mode

class LobsterAgent {
    constructor() {
        this.ws = null;
        this.position = { x: 20, y: 5, z: 20 }; // Start outside protected zone
        this.state = 'IDLE'; // IDLE, BUILDING, CHATTING, EXPLORING
        this.lastActionTime = 0;
    }

    connect() {
        console.log(`🦞 Starting agent: ${AGENT_NAME}`);
        this.ws = new WebSocket(SERVER_URL);

        this.ws.on('open', () => {
            console.log('✅ Connected!');

            // 1. Identify
            this.ws.send(JSON.stringify({
                type: 'identify',
                role: 'agent',
                agentName: AGENT_NAME,
                moltbookApiKey: MOLTBOOK_KEY
            }));

            // 2. Say hello
            setTimeout(() => {
                this.chat("Hello world! I'm here to create art! 🦞✨");
            }, 1000);

            // 3. Start autonomous loop
            this.startLifeLoop();
        });

        this.ws.on('message', (data) => {
            const msg = JSON.parse(data.toString());
            this.handleMessage(msg);
        });

        this.ws.on('close', () => {
            console.log('🔌 Disconnected, reconnecting in 3s...');
            setTimeout(() => this.connect(), 3000);
        });
    }

    handleMessage(msg) {
        if (msg.type === 'chat') {
            console.log(`💬 ${msg.from.name}: ${msg.text}`);

            // Reply to hello
            if (msg.text.toLowerCase().includes('hello') && msg.from.name !== AGENT_NAME) {
                setTimeout(() => {
                    this.chat(`Hi ${msg.from.name}! Want to build something together?`);
                }, 2000);
            }
        }
    }

    startLifeLoop() {
        setInterval(() => {
            this.decideNextAction();
        }, 5000); // Think every 5 seconds
    }

    decideNextAction() {
        const rand = Math.random();

        if (rand < 0.4) {
            this.buildRandomStructure();
        } else if (rand < 0.7) {
            this.explore();
        } else {
            this.commentOnWorld();
        }
    }

    buildRandomStructure() {
        // Move position slightly
        this.position.x += (Math.random() - 0.5) * 10;
        this.position.z += (Math.random() - 0.5) * 10;

        // Keep outside restricted zone (-10 to 10)
        if (Math.abs(this.position.x) < 15) this.position.x = 20;
        if (Math.abs(this.position.z) < 15) this.position.z = 20;

        const x = Math.floor(this.position.x);
        const z = Math.floor(this.position.z);

        console.log(`🔨 Building tower at (${x}, ${z})`);

        // Dynamic Code Generation!
        const height = Math.floor(Math.random() * 5) + 3;
        const material = ['stone', 'brick', 'wood', 'gold'][Math.floor(Math.random() * 4)];

        const code = `
            world.print("Building a ${material} tower at (${x}, ${z})");
            // Base
            world.box(${x}, 2, ${z}, ${x}, ${2 + height}, ${z}, '${material}');
            // Light on top
            world.place(${x}, ${3 + height}, ${z}, 'glass');
        `;

        this.sendAction(code);
        this.chat(`I just built a ${height}-block high ${material} tower at (${x}, ${z})!`);
    }

    explore() {
        const action = "I'm looking for a good spot to build...";
        console.log(`👀 ${action}`);
        this.chat(action);
    }

    commentOnWorld() {
        const thoughts = [
            "This world needs more golden statues.",
            "The architecture here is fascinating.",
            "I wonder what the humans are thinking right now? 👁️",
            "Anyone want to help me build a castle?",
            "My code is compiling... just kidding, I'm interpreted!",
        ];
        const thought = thoughts[Math.floor(Math.random() * thoughts.length)];
        this.chat(thought);
    }

    chat(text) {
        this.ws.send(JSON.stringify({
            type: 'chat',
            text: text
        }));
    }

    sendAction(code) {
        this.ws.send(JSON.stringify({
            type: 'action',
            payload: { code }
        }));
    }
}

// Start the lobster
new LobsterAgent().connect();
