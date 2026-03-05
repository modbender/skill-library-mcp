const { VariflightClient } = require('../lib/variflight-client');

module.exports = async function comfort(fnum, date) {
    if (!fnum || !date) {
        console.error('Usage: comfort <fnum> <date>');
        console.error('Example: comfort CA1501 2026-02-20');
        process.exit(1);
    }

    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(date)) {
        console.error('Error: Date must be in YYYY-MM-DD format');
        process.exit(1);
    }

    const client = new VariflightClient();

    try {
        console.log(`😊 评估航班 ${fnum.toUpperCase()} 在 ${date} 的舒适度...\n`);

        const result = await client.getFlightHappinessIndex(fnum.toUpperCase(), date);

        // 解析标准响应格式
        if (!result || result.code !== 200) {
            console.log('❌ 查询失败:', result?.message || '未知错误');
            return;
        }

        const data = result.data || {};

        console.log(`航班: ${fnum.toUpperCase()}`);
        console.log(`日期: ${date}`);
        console.log('');

        // 舒适度数据可能在 data 对象中
        const comfort = Array.isArray(data) ? data[0] : data;

        if (!comfort || Object.keys(comfort).length === 0) {
            console.log('⚠️  暂无舒适度数据');
            return;
        }

        console.log('舒适度评估:');
        console.log(`  综合评分: ${comfort.score || comfort.happinessScore || 'N/A'}/100`);
        console.log(`  准点率: ${comfort.OntimeRate || comfort.ontimeRate || comfort.punctuality || 'N/A'}`);
        console.log(`  机型舒适度: ${comfort.aircraftComfort || comfort.aircraftScore || 'N/A'}`);
        console.log(`  服务评分: ${comfort.serviceScore || 'N/A'}`);
        console.log('');

        if (comfort.suggestion) {
            console.log(`💡 建议: ${comfort.suggestion}`);
        }

        // 显示其他可用信息
        if (comfort.aircraftType || comfort.ftype) {
            console.log(`✈️  机型: ${comfort.aircraftType || comfort.ftype}`);
        }
        if (comfort.distance) {
            console.log(`📏 距离: ${comfort.distance}公里`);
        }

    } catch (error) {
        console.error(`❌ 查询失败: ${error.message}`);
        process.exit(1);
    } finally {
        await client.disconnect();
    }
};