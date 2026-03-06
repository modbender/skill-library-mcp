/**
 * Deadlines - Check tasks approaching deadline
 * Usage: node scripts/deadlines.js [days]
 * Default: 3 days
 */

const { makeRequest } = require('./api');

async function checkDeadlines() {
    const lookAhead = parseInt(process.argv[2]) || 3;

    try {
        const r = await makeRequest('GET', '/tasks');
        const tasks = Array.isArray(r.data) ? r.data : (r.data?.tasks || []);

        const pending = tasks
            .filter(t => !t.completed && !t.isCompleted)
            .map(t => {
                const dueDate = t.dueDate || t.due_date || t.deadline;
                const days = dueDate ? Math.ceil((new Date(dueDate) - new Date()) / (1000 * 60 * 60 * 24)) : null;
                return { ...t, _days: days };
            })
            .filter(t => t._days !== null && t._days <= lookAhead)
            .sort((a, b) => a._days - b._days);

        if (pending.length === 0) {
            console.log(`✅ No tasks with deadlines in the next ${lookAhead} day(s).`);
            return;
        }

        console.log(`⏰ *Deadlines (next ${lookAhead} days)*\n`);

        ['overdue', 'today', 'upcoming'].forEach(group => {
            const items = group === 'overdue' ? pending.filter(t => t._days < 0)
                : group === 'today' ? pending.filter(t => t._days === 0)
                    : pending.filter(t => t._days > 0);

            if (items.length === 0) return;

            const label = group === 'overdue' ? '🔴 OVERDUE' : group === 'today' ? '🟠 TODAY' : '🟡 UPCOMING';
            console.log(label);

            items.forEach(t => {
                const timeStr = t._days < 0 ? `${Math.abs(t._days)} day(s) overdue` : t._days === 0 ? 'today' : `${t._days} day(s) left`;
                console.log(`   - ${t.title || t.name} (${timeStr})`);
            });
            console.log('');
        });

        console.log(`📊 Total: ${pending.length} task`);
    } catch (err) {
        console.error('❌', err.message);
    }
}

checkDeadlines();
