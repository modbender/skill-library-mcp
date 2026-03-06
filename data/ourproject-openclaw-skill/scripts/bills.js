/**
 * Bills - Check upcoming bills
 * Usage: node scripts/bills.js [days]
 * Default: 7 days
 */

const { makeRequest } = require('./api');

function formatRupiah(num) {
    if (!num && num !== 0) return 'Rp 0';
    return 'Rp ' + Number(num).toLocaleString('id-ID');
}

async function checkBills() {
    const lookAhead = parseInt(process.argv[2]) || 7;

    try {
        const r = await makeRequest('GET', '/finance/bills');
        const bills = Array.isArray(r.data) ? r.data : (r.data?.bills || []);

        const upcoming = bills
            .map(b => {
                const dueDate = b.dueDate || b.due_date || b.nextDue;
                const days = dueDate ? Math.ceil((new Date(dueDate) - new Date()) / (1000 * 60 * 60 * 24)) : null;
                return { ...b, _days: days };
            })
            .filter(b => b._days !== null && b._days >= 0 && b._days <= lookAhead)
            .sort((a, b) => a._days - b._days);

        if (upcoming.length === 0) {
            console.log(`✅ No bills due in the next ${lookAhead} day(s).`);
            return;
        }

        console.log(`📋 *Bills Due (next ${lookAhead} days)*\n`);

        let total = 0;
        upcoming.forEach(b => {
            const icon = b._days === 0 ? '🔴' : b._days <= 2 ? '🟠' : b._days <= 4 ? '🟡' : '🟢';
            const timeStr = b._days === 0 ? 'TODAY' : b._days === 1 ? 'Tomorrow' : `${b._days} days`;
            const amount = b.amount || 0;
            total += Number(amount);
            console.log(`${icon} ${b.name || b.title}: ${formatRupiah(amount)} — ${timeStr}`);
        });

        console.log(`\n💰 Total: ${formatRupiah(total)} (${upcoming.length} bill(s))`);
    } catch (err) {
        console.error('❌', err.message);
    }
}

checkBills();
