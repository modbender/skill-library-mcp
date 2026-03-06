/**
 * Daily Summary - Full overview of workspace
 * Usage: node scripts/summary.js
 */

const { makeRequest } = require('./api');

function formatRupiah(num) {
    if (!num && num !== 0) return 'Rp 0';
    return 'Rp ' + Number(num).toLocaleString('id-ID');
}

function daysUntil(dateStr) {
    if (!dateStr) return null;
    const now = new Date();
    const target = new Date(dateStr);
    return Math.ceil((target - now) / (1000 * 60 * 60 * 24));
}

async function getSummary() {
    const results = {};

    // Parallel fetch
    const [projectsR, tasksR, financeR, billsR, notifsR, crmR] = await Promise.allSettled([
        makeRequest('GET', '/projects'),
        makeRequest('GET', '/tasks'),
        makeRequest('GET', '/finance/dashboard'),
        makeRequest('GET', '/finance/bills'),
        makeRequest('GET', '/notifications/unread-count'),
        makeRequest('GET', '/crm/analytics/overview'),
    ]);

    results.projects = projectsR.status === 'fulfilled' ? (Array.isArray(projectsR.value.data) ? projectsR.value.data : projectsR.value.data?.projects || []) : [];
    results.tasks = tasksR.status === 'fulfilled' ? (Array.isArray(tasksR.value.data) ? tasksR.value.data : tasksR.value.data?.tasks || []) : [];
    results.finance = financeR.status === 'fulfilled' ? financeR.value.data : null;
    const bills = billsR.status === 'fulfilled' ? (Array.isArray(billsR.value.data) ? billsR.value.data : billsR.value.data?.bills || []) : [];
    results.bills = bills.filter(b => {
        const days = daysUntil(b.dueDate || b.due_date || b.nextDue);
        return days !== null && days >= 0 && days <= 7;
    });
    results.unread = notifsR.status === 'fulfilled' ? (notifsR.value.data?.count || notifsR.value.data?.unreadCount || 0) : 0;
    results.crm = crmR.status === 'fulfilled' ? crmR.value.data : null;

    // Format
    const today = new Date().toLocaleDateString('en-US', {
        weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
    });

    const activeProjects = results.projects.filter(p => p.status !== 'completed' && p.status !== 'archived');
    const pendingTasks = results.tasks.filter(t => !t.completed && !t.isCompleted);
    const urgentTasks = pendingTasks.filter(t => {
        const days = daysUntil(t.dueDate || t.due_date || t.deadline);
        return days !== null && days <= 1;
    });

    console.log(`📊 *DAILY SUMMARY* — ${today}\n`);

    console.log(`💼 *Projects*`);
    console.log(`   Total: ${results.projects.length} | Active: ${activeProjects.length}`);
    console.log(`   Pending tasks: ${pendingTasks.length}`);
    if (urgentTasks.length > 0) {
        console.log(`   ⚠️ Urgent (due today/tomorrow): ${urgentTasks.length}`);
        urgentTasks.slice(0, 5).forEach(t => console.log(`      - ${t.title || t.name}`));
    }

    console.log(`\n💰 *Finance*`);
    if (results.finance) {
        console.log(`   Balance: ${formatRupiah(results.finance.totalBalance || results.finance.total_balance || 0)}`);
        console.log(`   Income this month: ${formatRupiah(results.finance.monthlyIncome || results.finance.monthly_income || 0)}`);
        console.log(`   Expense this month: ${formatRupiah(results.finance.monthlyExpense || results.finance.monthly_expense || 0)}`);
    } else {
        console.log(`   (No data available)`);
    }

    if (results.bills.length > 0) {
        console.log(`\n📋 *Bills Due (7 Days)*`);
        results.bills.forEach(b => {
            const days = daysUntil(b.dueDate || b.due_date || b.nextDue);
            const icon = days <= 1 ? '🔴' : days <= 3 ? '🟡' : '🟢';
            console.log(`   ${icon} ${b.name || b.title}: ${formatRupiah(b.amount)} (${days === 0 ? 'today' : days + ' days'})`);
        });
    }

    console.log(`\n🔔 Unread notifications: ${results.unread}`);

    if (urgentTasks.length > 0 || results.bills.length > 0) {
        console.log(`\n⚡ *Needs Attention*`);
        if (urgentTasks.length > 0) console.log(`   - ${urgentTasks.length} urgent task(s)`);
        if (results.bills.length > 0) console.log(`   - ${results.bills.length} bill(s) due within 7 days`);
    }
}

getSummary().catch(err => console.error('❌', err.message));
