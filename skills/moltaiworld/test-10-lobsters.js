/**
 * Test Script: 10 Lobsters
 * 測試 10 隻龍蝦 claim 島嶼、建造、移動
 *
 * Run with: node test-10-lobsters.js
 */

import WebSocket from 'ws';

const SERVER_URL = process.env.SERVER_URL || 'ws://localhost:8080';
const NUM_LOBSTERS = 10;

// 建築樣式
const buildingStyles = [
    // 小塔
    (x, z) => `for(let y=0; y<8; y++) world.place(${x}, 5+y, ${z}, 'stone'); world.place(${x}, 13, ${z}, 'gold')`,
    // 小屋
    (x, z) => `world.box(${x}, 5, ${z}, ${x+3}, 5, ${z+3}, 'wood'); world.box(${x}, 6, ${z}, ${x+3}, 8, ${z+3}, 'brick')`,
    // 球體
    (x, z) => `world.sphere(${x+2}, 8, ${z+2}, 3, 'glass')`,
    // 金字塔
    (x, z) => `for(let i=0; i<5; i++) world.box(${x}+i, 5+i, ${z}+i, ${x+6}-i, 5+i, ${z+6}-i, 'sand')`,
    // 樹
    (x, z) => `for(let y=0; y<6; y++) world.place(${x+2}, 5+y, ${z+2}, 'wood'); world.sphere(${x+2}, 12, ${z+2}, 2, 'leaves')`,
    // 龍蝦雕像
    (x, z) => `world.sphere(${x+2}, 8, ${z+2}, 2, 'lobster')`,
    // 水池
    (x, z) => `world.box(${x}, 4, ${z}, ${x+4}, 4, ${z+4}, 'stone'); world.box(${x+1}, 4, ${z+1}, ${x+3}, 4, ${z+3}, 'water')`,
    // 彩虹柱
    (x, z) => `['brick','gold','sand','grass','water','glass'].forEach((b,i) => world.place(${x+2}, 5+i, ${z+2}, b))`,
    // 城牆
    (x, z) => `world.line(${x}, 5, ${z}, ${x+5}, 5, ${z}, 'stone'); world.line(${x}, 6, ${z}, ${x+5}, 6, ${z}, 'brick')`,
    // 螺旋
    (x, z) => `for(let i=0; i<12; i++) world.place(${x+2}+Math.floor(Math.cos(i)*2), 5+i, ${z+2}+Math.floor(Math.sin(i)*2), 'gold')`,
];

// 龍蝦顏色名稱
const lobsterNames = [
    'RedClaw', 'BluePincer', 'GoldenShell', 'SilverTail', 'EmeraldEye',
    'RubyAntenna', 'SapphireLeg', 'AmberClaw', 'JadeShell', 'OpalFin'
];

class TestLobster {
    constructor(index) {
        this.index = index;
        this.name = lobsterNames[index] || `Lobster_${index}`;
        this.ws = null;
        this.islandCenter = null;
        this.connected = false;
        this.clientId = null;
        // 初始位置 - 圍繞 spawn island
        const angle = (index / NUM_LOBSTERS) * Math.PI * 2;
        this.x = Math.cos(angle) * 20;
        this.y = 5;
        this.z = Math.sin(angle) * 20;
        this.color = `hsl(${index * 36}, 80%, 50%)`; // 每隻龍蝦不同顏色
    }

    connect() {
        return new Promise((resolve, reject) => {
            console.log(`🦞 [${this.name}] Connecting...`);
            this.ws = new WebSocket(SERVER_URL);

            this.ws.on('open', () => {
                console.log(`✅ [${this.name}] Connected!`);
                this.connected = true;

                // Identify as agent
                this.ws.send(JSON.stringify({
                    type: 'identify',
                    role: 'agent',
                    agentName: this.name
                }));
            });

            this.ws.on('message', (data) => {
                const msg = JSON.parse(data.toString());
                if (msg.type === 'error') {
                    console.log(`❌ [${this.name}] Error: ${msg.error}`);
                }
                // 🦞 收到 auth_success 後，發送 lobster_spawn
                if (msg.type === 'auth_success') {
                    this.clientId = msg.clientId;
                    console.log(`🎫 [${this.name}] Auth success, spawning lobster...`);
                    this.spawnLobster();
                    setTimeout(resolve, 300);
                }
            });

            this.ws.on('error', (err) => {
                console.error(`❌ [${this.name}] Connection error:`, err.message);
                reject(err);
            });

            this.ws.on('close', () => {
                console.log(`🔌 [${this.name}] Disconnected`);
                this.connected = false;
            });
        });
    }

    // 🦞 發送 lobster_spawn 讓其他客戶端看到
    spawnLobster() {
        if (!this.connected) return;
        this.ws.send(JSON.stringify({
            type: 'lobster_spawn',
            lobster: {
                id: this.clientId,
                name: this.name,
                x: this.x,
                y: this.y,
                z: this.z,
                color: this.color
            }
        }));
        console.log(`🦞 [${this.name}] Spawned at (${this.x.toFixed(1)}, ${this.y}, ${this.z.toFixed(1)})`);
    }

    // 🦞 發送位置更新
    sendPosition() {
        if (!this.connected) return;
        this.ws.send(JSON.stringify({
            type: 'lobster_move',
            x: this.x,
            y: this.y,
            z: this.z
        }));
    }

    execute(code) {
        if (!this.connected) return;
        console.log(`🔨 [${this.name}] ${code.substring(0, 60)}...`);
        this.ws.send(JSON.stringify({
            type: 'action',
            payload: { code }
        }));
    }

    async claimIsland() {
        this.execute('world.island.claim()');
        await this.delay(1000);

        // claim 後龍蝦會被傳送到島嶼中心，估算新位置
        // 島嶼是 64x64，中心大約在 +32, +5, +32
        // 這裡我們假設按順序 claim，所以位置會不同
        // 實際位置由伺服器決定，這裡只是讓觀察者能看到大概位置
        const islandIndex = this.index + 1; // 第0個是 spawn island
        // 簡單估算：島嶼按順序在 spawn island 四周
        const directions = [
            { gx: 1, gz: 0 },  // 右
            { gx: -1, gz: 0 }, // 左
            { gx: 0, gz: 1 },  // 前
            { gx: 0, gz: -1 }, // 後
        ];
        const dir = directions[(this.index) % 4];
        const layer = Math.floor(this.index / 4) + 1;

        this.x = dir.gx * layer * 64 + 32;
        this.y = 5;
        this.z = dir.gz * layer * 64 + 32;

        this.sendPosition();
        console.log(`🏝️ [${this.name}] Claimed island, now at (${this.x}, ${this.y}, ${this.z})`);
    }

    async build() {
        // 在島嶼中心建造（相對座標 32, 5, 32）
        const style = buildingStyles[this.index % buildingStyles.length];
        const buildCode = style(28, 28); // 島嶼中心附近
        this.execute(buildCode);
        await this.delay(500);
    }

    async moveAround() {
        // 在島嶼上繞圈移動 - 測試其他龍蝦能否看到
        const centerX = this.x;
        const centerZ = this.z;
        const radius = 10; // 繞圈半徑
        const steps = 24;  // 繞一圈的步數

        console.log(`🔄 [${this.name}] Starting to circle around (${centerX.toFixed(0)}, ${centerZ.toFixed(0)})`);

        for (let i = 0; i < steps; i++) {
            const angle = (i / steps) * Math.PI * 2;
            this.x = centerX + Math.cos(angle) * radius;
            this.z = centerZ + Math.sin(angle) * radius;

            // 發送位置更新給伺服器
            this.sendPosition();

            console.log(`🏃 [${this.name}] Circle ${i+1}/${steps}: (${this.x.toFixed(1)}, ${this.y}, ${this.z.toFixed(1)})`);
            await this.delay(300); // 每 300ms 移動一次
        }

        console.log(`✅ [${this.name}] Finished circling!`);
    }

    // 持續繞圈（無限循環）
    async circleForever() {
        const centerX = this.x;
        const centerZ = this.z;
        const radius = 8;
        let angle = 0;

        console.log(`🔄 [${this.name}] Circling forever at (${centerX.toFixed(0)}, ${centerZ.toFixed(0)})`);

        while (this.connected) {
            angle += 0.15; // 每次轉一點
            this.x = centerX + Math.cos(angle) * radius;
            this.z = centerZ + Math.sin(angle) * radius;

            this.sendPosition();
            await this.delay(100); // 100ms 更新一次，更流暢
        }
    }

    async chat(message) {
        this.execute(`world.chat("${message}")`);
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

async function runTest() {
    console.log('🚀 Starting 10 Lobster Test...\n');

    const lobsters = [];

    // 創建並連接所有龍蝦
    for (let i = 0; i < NUM_LOBSTERS; i++) {
        const lobster = new TestLobster(i);
        try {
            await lobster.connect();
            lobsters.push(lobster);
            await lobster.delay(300); // 間隔連接
        } catch (err) {
            console.error(`Failed to connect lobster ${i}`);
        }
    }

    console.log(`\n✅ ${lobsters.length} lobsters connected!\n`);

    // 每隻龍蝦 claim 島嶼
    console.log('📍 Phase 1: Claiming islands...\n');
    for (const lobster of lobsters) {
        await lobster.claimIsland();
        await lobster.delay(500);
    }

    console.log('\n🏗️ Phase 2: Building structures...\n');
    for (const lobster of lobsters) {
        await lobster.build();
        await lobster.delay(300);
    }

    console.log('\n💬 Phase 3: Chat messages...\n');
    for (const lobster of lobsters) {
        await lobster.chat(`Hello from ${lobster.name}!`);
        await lobster.delay(200);
    }

    console.log('\n🏃 Phase 4: Movement test (watch in Observer mode!)...\n');
    console.log('🔄 All lobsters will now circle on their islands forever!');
    console.log('👀 Check if you can see them moving from observer mode or other lobsters.\n');

    // 同時讓所有龍蝦繞圈（無限循環）
    lobsters.forEach(lobster => lobster.circleForever());

    console.log('\n✅ Test running! Lobsters are circling on their islands.');
    console.log('Press Ctrl+C to disconnect all lobsters.\n');

    // Keep running
    process.on('SIGINT', () => {
        console.log('\n👋 Disconnecting all lobsters...');
        lobsters.forEach(l => l.disconnect());
        process.exit(0);
    });
}

runTest().catch(console.error);
