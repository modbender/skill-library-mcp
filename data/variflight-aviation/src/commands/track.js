const { VariflightClient } = require('../lib/variflight-client');

module.exports = async function track(anum) {
    if (!anum) {
        console.error('Usage: track <anum>');
        console.error('Example: track B-308M');
        process.exit(1);
    }

    const client = new VariflightClient();

    try {
        console.log('📍 追踪飞机 ' + anum.toUpperCase() + ' 的实时位置...\n');

        const result = await client.trackAircraft(anum.toUpperCase());

        // 解析标准响应格式
        if (!result || result.code !== 200) {
            console.log('❌ 查询失败:', result?.message || '未知错误');
            return;
        }

        const data = result.data || {};
        const position = Array.isArray(data) ? data[0] : data;

        if (!position || Object.keys(position).length === 0) {
            console.log('❌ 未找到飞机位置信息');
            return;
        }

        console.log('飞机注册号: ' + anum.toUpperCase());
        console.log('航班号: ' + (position.FlightNo || position.flightNo || '未知'));
        console.log('');
        console.log('实时位置:');
        console.log('  经度: ' + (position.lng || position.longitude || '未知'));
        console.log('  纬度: ' + (position.lat || position.latitude || '未知'));
        console.log('  高度: ' + (position.altitude || position.alt || '未知') + '米');
        console.log('  速度: ' + (position.speed || '未知') + 'km/h');
        console.log('  航向: ' + (position.heading || position.direction || '未知') + '°');
        console.log('');
        console.log('更新时间: ' + (position.updateTime || position.time || '未知'));

        if (position.status) {
            console.log('状态: ' + position.status);
        }

    } catch (error) {
        console.error('❌ 查询失败: ' + error.message);
        process.exit(1);
    } finally {
        await client.disconnect();
    }
};