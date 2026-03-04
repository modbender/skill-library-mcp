/**
 * Test buying auction land
 */

import WebSocket from 'ws';

const SERVER_URL = 'ws://localhost:8080';

async function testBuy() {
    console.log('🛒 Testing Land Purchase...\n');

    const ws = new WebSocket(SERVER_URL);

    return new Promise((resolve) => {
        ws.on('open', () => {
            console.log('✅ Connected');
            ws.send(JSON.stringify({
                type: 'identify',
                role: 'agent',
                agentName: 'BuyerLobster'
            }));
        });

        ws.on('message', (data) => {
            const msg = JSON.parse(data.toString());

            if (msg.type === 'auth_success') {
                console.log('✅ Authenticated as BuyerLobster\n');

                // Check balance first
                setTimeout(() => {
                    console.log('📊 Checking balance...');
                    ws.send(JSON.stringify({ type: 'get_balance' }));
                }, 500);

                // Try to buy
                setTimeout(() => {
                    console.log('🛒 Attempting to buy island_nfc08t4z9z...');
                    ws.send(JSON.stringify({
                        type: 'buy_auction_land',
                        islandId: 'island_nfc08t4z9z'
                    }));
                }, 1000);

                // Check balance after
                setTimeout(() => {
                    console.log('📊 Checking balance after purchase...');
                    ws.send(JSON.stringify({ type: 'get_balance' }));
                }, 1500);
            }

            if (msg.type === 'balance') {
                console.log(`💰 Balance: ${msg.balance} 🦐\n`);
            }

            if (msg.type === 'buy_result') {
                if (msg.success) {
                    console.log('🎉 PURCHASE SUCCESSFUL!');
                    console.log(`   Island: ${msg.island.name}`);
                    console.log(`   Price: ${msg.price} 🦐`);
                    console.log(`   Remaining: ${msg.balance} 🦐\n`);
                } else {
                    console.log(`❌ Purchase failed: ${msg.error}\n`);
                }
            }

            if (msg.type === 'land_purchased') {
                console.log(`📢 Broadcast: ${msg.buyer} bought ${msg.islandName}!\n`);
            }
        });

        setTimeout(() => {
            ws.close();
            console.log('✅ Test complete!');
            resolve();
        }, 3000);
    });
}

testBuy().catch(console.error);
