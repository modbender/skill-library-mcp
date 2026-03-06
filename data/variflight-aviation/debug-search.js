const { VariflightClient } = require('./src/lib/variflight-client');

async function debug() {
    const client = new VariflightClient();

    try {
        console.log('🔍 调试模式 - 查看原始返回数据\n');

        const result = await client.searchFlightsByDepArr('PEK', 'SHA', '2026-02-20');

        console.log('=== 原始数据类型 ===');
        console.log(typeof result);
        console.log('');

        console.log('=== 原始数据内容 ===');
        console.log(JSON.stringify(result, null, 2));
        console.log('');

        // 如果是字符串，直接打印
        if (typeof result === 'string') {
            console.log('=== 字符串内容 ===');
            console.log(result);
        }

        // 如果是数组，分析每个元素
        if (Array.isArray(result)) {
            console.log(`=== 数组长度: ${result.length} ===`);
            if (result.length > 0) {
                console.log('=== 第一个元素 ===');
                console.log(JSON.stringify(result[0], null, 2));
            }
        }

        // 如果是对象，列出所有键
        if (typeof result === 'object' && result !== null && !Array.isArray(result)) {
            console.log('=== 对象键列表 ===');
            console.log(Object.keys(result));
        }

    } catch (error) {
        console.error('❌ 错误:', error.message);
    } finally {
        await client.disconnect();
    }
}

debug();