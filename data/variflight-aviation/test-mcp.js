const { VariflightClient } = require('./src/lib/variflight-client');

async function test() {
    const client = new VariflightClient();

    try {
        console.log('🔌 连接到 MCP 服务器...\n');
        await client.connect();

        // 先列出可用工具
        console.log('📋 可用工具列表：');
        const tools = await client.listTools();
        console.log(JSON.stringify(tools, null, 2));
        console.log('');

        // 测试查询
        console.log('🔍 测试查询 PEK → SHA...');
        const result = await client.searchFlightsByDepArr('PEK', 'SHA', '2026-02-20');
        console.log('✅ 查询成功：');
        console.log(JSON.stringify(result, null, 2));

    } catch (error) {
        console.error('❌ 错误:', error.message);
        if (error.stack) {
            console.error('Stack:', error.stack);
        }
    } finally {
        await client.disconnect();
    }
}

test();