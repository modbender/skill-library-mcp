const { VariflightClient } = require('../lib/variflight-client');

module.exports = async function info(fnum, date) {
    if (!fnum || !date) {
        console.error('Usage: info <fnum> <date>');
        console.error('Example: info MU2157 2026-02-20');
        process.exit(1);
    }

    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(date)) {
        console.error('Error: Date must be in YYYY-MM-DD format');
        process.exit(1);
    }

    const client = new VariflightClient();

    try {
        console.log(`🛫 查询航班 ${fnum.toUpperCase()} 在 ${date} 的信息...\n`);

        const result = await client.searchFlightsByNumber(fnum.toUpperCase(), date);

        // 解析标准响应格式
        if (!result || result.code !== 200) {
            console.log('❌ 查询失败:', result?.message || '未知错误');
            return;
        }

        const flights = result.data || [];

        if (flights.length === 0) {
            console.log('❌ 未找到航班信息');
            return;
        }

        // 显示第一个航班的详细信息
        const flight = flights[0];

        console.log(`航班号: ${flight.FlightNo || '未知'}`);
        console.log(`航空公司: ${flight.FlightCompany || '未知'}`);
        console.log('');

        console.log('出发信息:');
        console.log(`  机场: ${flight.FlightDepAirport || flight.FlightDepcode || '未知'} (${flight.FlightDepcode || ''})`);
        console.log(`  航站楼: ${flight.FlightHTerminal || '待定'}`);
        console.log(`  计划时间: ${flight.FlightDeptimePlanDate || '待定'}`);
        console.log(`  预计起飞: ${flight.VeryZhunReadyDeptimeDate || flight.FlightDeptimeReadyDate || '待定'}`);
        console.log(`  实际起飞: ${flight.FlightDeptimeDate || '待定'}`);
        console.log(`  值机柜台: ${flight.CheckinTable || '待定'}`);
        console.log(`  登机口: ${flight.BoardGate || '待定'}`);
        console.log('');

        console.log('到达信息:');
        console.log(`  机场: ${flight.FlightArrAirport || flight.FlightArrcode || '未知'} (${flight.FlightArrcode || ''})`);
        console.log(`  航站楼: ${flight.FlightTerminal || '待定'}`);
        console.log(`  计划时间: ${flight.FlightArrtimePlanDate || '待定'}`);
        console.log(`  预计到达: ${flight.VeryZhunReadyArrtimeDate || flight.FlightArrtimeReadyDate || '待定'}`);
        console.log(`  实际到达: ${flight.FlightArrtimeDate || '待定'}`);
        console.log(`  行李转盘: ${flight.BaggageID || '待定'}`);
        console.log('');

        console.log(`机型: ${flight.ftype || flight.generic || '未知'}`);
        console.log(`餐食: ${flight.Food || '无'}`);
        console.log(`状态: ${flight.FlightState || '计划中'}`);

        if (flight.OntimeRate) {
            console.log(`准点率: ${flight.OntimeRate}`);
        }
        if (flight.distance) {
            console.log(`飞行距离: ${flight.distance}公里`);
        }

    } catch (error) {
        console.error(`❌ 查询失败: ${error.message}`);
        process.exit(1);
    } finally {
        await client.disconnect();
    }
};