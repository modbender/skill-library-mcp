/**
 * Finance - Financial overview
 * Usage: node scripts/finance.js
 */

const { makeRequest } = require('./api');

function formatRupiah(num) {
    if (!num && num !== 0) return 'Rp 0';
    return 'Rp ' + Number(num).toLocaleString('id-ID');
}

async function financeOverview() {
    try {
        const [summaryR, accountsR] = await Promise.allSettled([
            makeRequest('GET', '/finance/dashboard'),
            makeRequest('GET', '/finance/accounts'),
        ]);

        const summary = summaryR.status === 'fulfilled' ? summaryR.value.data : null;
        const accounts = accountsR.status === 'fulfilled' ? (Array.isArray(accountsR.value.data) ? accountsR.value.data : accountsR.value.data?.accounts || []) : [];

        console.log('💰 *Finance Overview*\n');

        if (summary) {
            console.log(`   Total Balance: ${formatRupiah(summary.totalBalance || summary.total_balance || 0)}`);
            console.log(`   Income this month: ${formatRupiah(summary.monthlyIncome || summary.monthly_income || 0)}`);
            console.log(`   Expense this month: ${formatRupiah(summary.monthlyExpense || summary.monthly_expense || 0)}`);
            const net = (summary.monthlyIncome || summary.monthly_income || 0) - (summary.monthlyExpense || summary.monthly_expense || 0);
            console.log(`   Net: ${formatRupiah(net)} ${net >= 0 ? '📈' : '📉'}`);
        }

        if (accounts.length > 0) {
            console.log('\n🏦 *Accounts*');
            accounts.forEach(a => {
                console.log(`   ${a.name}: ${formatRupiah(a.balance || 0)}`);
            });
        }
    } catch (err) {
        console.error('❌', err.message);
    }
}

financeOverview();
