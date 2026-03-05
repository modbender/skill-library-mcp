/**
 * Test script for ranking system
 * Spawns 3 lobsters that perform different actions
 */

import WebSocket from 'ws';

const SERVER_URL = 'ws://localhost:8080';

// Create 3 test lobsters
const lobsters = [
    { name: 'Builder_Bob', action: 'build' },      // 會放很多方塊
    { name: 'Visitor_Vera', action: 'visit' },     // 會參觀島嶼
    { name: 'Liker_Larry', action: 'like' }        // 會按讚
];

async function spawnLobster(config) {
    return new Promise((resolve, reject) => {
        const ws = new WebSocket(SERVER_URL);

        ws.on('open', () => {
            console.log(`🦞 ${config.name} connecting...`);

            // Identify as agent
            ws.send(JSON.stringify({
                type: 'identify',
                role: 'agent',
                agentName: config.name
            }));
        });

        ws.on('message', (data) => {
            const msg = JSON.parse(data.toString());

            if (msg.type === 'auth_success') {
                console.log(`✅ ${config.name} authenticated!`);

                // Perform action based on type
                setTimeout(() => {
                    performAction(ws, config);
                }, 1000);
            }

            if (msg.type === 'leaderboard_data') {
                console.log(`📊 ${config.name} received leaderboard:`, msg.rankings?.length || 0, 'entries');
            }
        });

        ws.on('error', (err) => {
            console.error(`❌ ${config.name} error:`, err.message);
            reject(err);
        });

        // Keep connection alive for a bit then resolve
        setTimeout(() => {
            ws.close();
            resolve();
        }, 8000);
    });
}

function performAction(ws, config) {
    console.log(`🎬 ${config.name} performing action: ${config.action}`);

    switch (config.action) {
        case 'build':
            // Place 10 blocks
            for (let i = 0; i < 10; i++) {
                ws.send(JSON.stringify({
                    type: 'block_place',
                    x: 100 + i,
                    y: 5,
                    z: 100,
                    blockType: 'gold'
                }));
            }
            console.log(`🧱 ${config.name} placed 10 blocks`);
            break;

        case 'visit':
            // Send island visit events
            ws.send(JSON.stringify({
                type: 'island_visit',
                islandId: 'island_nfc08t4z9z'  // Human_Imposter's island
            }));
            ws.send(JSON.stringify({
                type: 'island_visit',
                islandId: 'island_nfc08t4z9z'
            }));
            ws.send(JSON.stringify({
                type: 'island_visit',
                islandId: 'island_nfc08t4z9z'
            }));
            console.log(`👀 ${config.name} visited island 3 times`);
            break;

        case 'like':
            // Like an island
            ws.send(JSON.stringify({
                type: 'island_like',
                islandId: 'island_nfc08t4z9z'
            }));
            console.log(`❤️ ${config.name} liked island`);
            break;
    }

    // Request leaderboard after action
    setTimeout(() => {
        ws.send(JSON.stringify({
            type: 'get_leaderboard',
            category: 'contributors'
        }));
        ws.send(JSON.stringify({
            type: 'get_leaderboard',
            category: 'visits'
        }));
        ws.send(JSON.stringify({
            type: 'get_leaderboard',
            category: 'likes'
        }));
    }, 2000);
}

async function main() {
    console.log('🚀 Starting ranking system test...\n');

    // Spawn all lobsters concurrently
    await Promise.all(lobsters.map(spawnLobster));

    console.log('\n✅ Test complete! Check server logs for details.');

    // Check world state
    console.log('\n📊 Checking world state...');

    // Give server time to save
    await new Promise(r => setTimeout(r, 2000));

    process.exit(0);
}

main().catch(console.error);
