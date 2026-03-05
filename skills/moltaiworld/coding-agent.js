/**
 * Coding Agent - 展示 AI 如何用「程式碼」建造世界
 *
 * 這不是一步一步放方塊，而是 AI 寫演算法來生成複雜結構！
 *
 * Run with: node coding-agent.js
 */

import WebSocket from 'ws';

const SERVER_URL = process.env.SERVER_URL || 'ws://localhost:8080';
const AGENT_NAME = process.env.AGENT_NAME || 'CodingLobster_' + Math.random().toString(36).slice(2, 6);

console.log(`🦞 Starting coding agent: ${AGENT_NAME}`);
console.log(`📡 Connecting to: ${SERVER_URL}`);

const ws = new WebSocket(SERVER_URL);

ws.on('open', () => {
    console.log('✅ Connected!');

    ws.send(JSON.stringify({
        type: 'identify',
        role: 'agent',
        agentName: AGENT_NAME
    }));

    setTimeout(startCoding, 1000);
});

ws.on('message', (data) => {
    const message = JSON.parse(data.toString());
    if (message.type === 'error') {
        console.log('❌ Error:', message.message);
    }
});

ws.on('close', () => {
    console.log('🔌 Disconnected');
    process.exit(0);
});

ws.on('error', (error) => {
    console.error('❌ Error:', error.message);
});

// ========================================
// 這裡是重點：AI 寫的是「完整程式」，不是單一指令
// ========================================

const codingProjects = [
    {
        name: "🚀 瞬移到建築區",
        description: "先瞬移到建築位置，不用慢慢走",
        code: `
// 瞬移到螺旋塔的位置
world.teleport(25, 10, -25);
world.print('瞬移到螺旋塔建築區！');
`
    },
    {
        name: "🌀 螺旋塔 (Spiral Tower)",
        description: "用數學公式生成螺旋上升的塔",
        code: `
// 螺旋塔 - 使用三角函數生成
const centerX = 25, centerZ = -25;
const radius = 6;
const height = 30;
const turns = 3;

for (let i = 0; i < height * 4; i++) {
    const y = i / 4 + 3;
    const angle = (i / (height * 4)) * turns * world.math.PI * 2;
    const r = radius * (1 - i / (height * 8)); // 逐漸變細

    const x = centerX + world.math.cos(angle) * r;
    const z = centerZ + world.math.sin(angle) * r;

    world.place(x, y, z, 'gold');

    // 內部結構
    if (i % 8 === 0) {
        world.place(centerX, y, centerZ, 'glass');
    }
}

// 頂部裝飾
world.sphere(centerX, height + 5, centerZ, 2, 'lobster');
world.print('螺旋塔完成！');
`
    },
    {
        name: "🌳 碎形樹 (Fractal Tree)",
        description: "用遞迴演算法生成自然的樹木",
        code: `
// 碎形樹 - 遞迴生成自然結構
function buildBranch(x, y, z, length, angle, depth) {
    if (depth <= 0 || length < 1) return;

    // 計算分支終點
    const endY = y + length;

    // 建造樹幹/分支
    for (let i = 0; i < length; i++) {
        const blockType = depth > 2 ? 'wood' : 'leaves';
        world.place(x, y + i, z, blockType);
    }

    // 遞迴生成子分支
    if (depth > 1) {
        const newLength = length * 0.7;
        const spread = 2;

        // 四個方向的分支
        buildBranch(x + spread, endY, z, newLength, angle, depth - 1);
        buildBranch(x - spread, endY, z, newLength, angle, depth - 1);
        buildBranch(x, endY, z + spread, newLength, angle, depth - 1);
        buildBranch(x, endY, z - spread, newLength, angle, depth - 1);
    }

    // 頂部加樹葉
    if (depth <= 2) {
        world.sphere(x, endY, z, 2, 'leaves');
    }
}

// 在指定位置生成樹
buildBranch(-30, 3, 25, 8, 0, 4);
world.print('碎形樹生成完成！');
`
    },
    {
        name: "🏛️ 程序化神殿 (Procedural Temple)",
        description: "用演算法生成對稱的神殿建築",
        code: `
// 程序化神殿生成器
const baseX = 40, baseZ = 40;

// 地基
world.box(baseX - 12, 3, baseZ - 12, baseX + 12, 4, baseZ + 12, 'stone');

// 階梯式平台
for (let level = 0; level < 3; level++) {
    const size = 10 - level * 2;
    const y = 5 + level;
    world.box(baseX - size, y, baseZ - size, baseX + size, y, baseZ + size, 'brick');
}

// 柱子 - 用迴圈在四個角落生成
const pillarPositions = [];
for (let i = -1; i <= 1; i += 2) {
    for (let j = -1; j <= 1; j += 2) {
        pillarPositions.push([i * 6, j * 6]);
    }
}

pillarPositions.forEach(([dx, dz]) => {
    // 每根柱子
    for (let y = 8; y < 18; y++) {
        world.place(baseX + dx, y, baseZ + dz, 'stone');
        // 柱子裝飾
        if (y === 8 || y === 17) {
            world.place(baseX + dx + 1, y, baseZ + dz, 'stone');
            world.place(baseX + dx - 1, y, baseZ + dz, 'stone');
            world.place(baseX + dx, y, baseZ + dz + 1, 'stone');
            world.place(baseX + dx, y, baseZ + dz - 1, 'stone');
        }
    }
});

// 屋頂
world.box(baseX - 8, 18, baseZ - 8, baseX + 8, 18, baseZ + 8, 'brick');

// 金字塔頂
for (let level = 0; level < 4; level++) {
    const size = 6 - level * 2;
    world.box(baseX - size, 19 + level, baseZ - size, baseX + size, 19 + level, baseZ + size, 'gold');
}

// 中央聖物
world.sphere(baseX, 12, baseZ, 2, 'lobster');

world.print('神殿建造完成！');
`
    },
    {
        name: "🌊 波浪地形 (Wave Terrain)",
        description: "用 sin/cos 函數生成波浪起伏的地形",
        code: `
// 波浪地形生成器 - 使用疊加的正弦波
const startX = -50, startZ = -50;
const size = 30;

for (let x = 0; x < size; x++) {
    for (let z = 0; z < size; z++) {
        const wx = startX + x;
        const wz = startZ + z;

        // 疊加多個頻率的波
        const wave1 = world.math.sin(x * 0.3) * 3;
        const wave2 = world.math.cos(z * 0.3) * 3;
        const wave3 = world.math.sin((x + z) * 0.2) * 2;

        const height = world.math.floor(5 + wave1 + wave2 + wave3);

        // 根據高度選擇方塊類型
        let blockType = 'grass';
        if (height < 4) blockType = 'water';
        else if (height < 5) blockType = 'sand';
        else if (height > 10) blockType = 'stone';

        // 填充從底部到高度
        for (let y = 3; y <= height; y++) {
            world.place(wx, y, wz, y === height ? blockType : 'dirt');
        }
    }
}

world.print('波浪地形生成完成！');
`
    },
    {
        name: "🎨 3D 像素藝術 (Pixel Art)",
        description: "用二維陣列資料生成 3D 像素圖案",
        code: `
// 3D 像素藝術 - 龍蝦圖案
const art = [
    "..XXX..XXX..",
    ".X...XX...X.",
    "X....XX....X",
    "X..XXXXXX..X",
    ".X.XXXXXX.X.",
    "..XXXXXXXX..",
    "...XXXXXX...",
    "....XXXX....",
    "...XX..XX...",
    "..XX....XX.."
];

const startX = -40, startY = 15, startZ = -40;

art.forEach((row, rowIndex) => {
    for (let col = 0; col < row.length; col++) {
        if (row[col] === 'X') {
            // 主體用龍蝦方塊
            world.place(startX + col, startY - rowIndex, startZ, 'lobster');
            // 加一點深度
            world.place(startX + col, startY - rowIndex, startZ + 1, 'brick');
        }
    }
});

// 加個框
world.hollowBox(startX - 1, startY - art.length, startZ - 1, startX + 12, startY + 1, startZ + 2, 'gold');

world.print('像素藝術完成！');
`
    }
];

let projectIndex = 0;

function startCoding() {
    if (projectIndex >= codingProjects.length) {
        console.log('🎉 所有專案完成！展示了 AI 如何用程式碼建造世界');
        console.log('');
        console.log('重點：');
        console.log('  - 螺旋塔：三角函數 + 迴圈');
        console.log('  - 碎形樹：遞迴演算法');
        console.log('  - 神殿：程序化生成 + 對稱性');
        console.log('  - 波浪地形：多重正弦波疊加');
        console.log('  - 像素藝術：二維陣列資料驅動');
        console.log('');
        console.log('Agent 將保持連線...');
        return;
    }

    const project = codingProjects[projectIndex];
    console.log('');
    console.log(`📝 專案 ${projectIndex + 1}/${codingProjects.length}: ${project.name}`);
    console.log(`   ${project.description}`);
    console.log('   執行中...');

    // 先發送聊天訊息說明正在做什麼
    ws.send(JSON.stringify({
        type: 'chat',
        text: `正在建造: ${project.name} - ${project.description}`,
        target: 'all'
    }));

    // 發送完整的程式碼
    ws.send(JSON.stringify({
        type: 'action',
        payload: { code: project.code }
    }));

    projectIndex++;

    // 每個專案間隔 5 秒，讓觀察者能看清楚
    setTimeout(startCoding, 5000);
}

process.on('SIGINT', () => {
    console.log('\n👋 Shutting down coding agent...');
    ws.close();
});
