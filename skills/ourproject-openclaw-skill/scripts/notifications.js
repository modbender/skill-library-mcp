/**
 * Notifications - Check unread notifications
 * Usage: node scripts/notifications.js
 */

const { makeRequest } = require('./api');

async function checkNotifications() {
    try {
        const [countR, listR] = await Promise.allSettled([
            makeRequest('GET', '/notifications/unread-count'),
            makeRequest('GET', '/notifications?page=1&limit=5'),
        ]);

        const count = countR.status === 'fulfilled' ? (countR.value.data?.count || countR.value.data?.unreadCount || 0) : 0;
        const notifs = listR.status === 'fulfilled' ? (Array.isArray(listR.value.data) ? listR.value.data : listR.value.data?.notifications || []) : [];

        if (count === 0) {
            console.log('🔔 No new notifications.');
            return;
        }

        console.log(`🔔 *${count} Unread Notification(s)*\n`);

        const recent = notifs.filter(n => !n.isRead && !n.is_read).slice(0, 5);
        if (recent.length > 0) {
            console.log('*Recent:*');
            recent.forEach(n => {
                const time = n.createdAt ? new Date(n.createdAt).toLocaleString('en-US') : '';
                console.log(`   • ${n.title || n.message || 'Notification'}`);
                if (time) console.log(`     ${time}`);
            });
        }
    } catch (err) {
        console.error('❌', err.message);
    }
}

checkNotifications();
