const { program } = require('commander');
const Lark = require('@larksuiteoapi/node-sdk');
require('dotenv').config({ path: require('path').resolve(__dirname, '../../.env') });

const APP_ID = process.env.FEISHU_APP_ID;
const APP_SECRET = process.env.FEISHU_APP_SECRET;

if (!APP_ID || !APP_SECRET) {
    console.error('Error: FEISHU_APP_ID or FEISHU_APP_SECRET not set.');
    process.exit(1);
}

const client = new Lark.Client({
    appId: APP_ID,
    appSecret: APP_SECRET,
});

program
    .requiredOption('--name <text>', 'Calendar Name')
    .requiredOption('--desc <text>', 'Calendar Description')
    .requiredOption('--members <ids>', 'Comma-separated OpenIDs to add as members')
    .option('--role <role>', 'Role for members (writer, reader, owner)', 'writer')
    .parse(process.argv);

const options = program.opts();

async function main() {
    try {
        console.log(`Creating shared calendar: ${options.name}...`);
        
        // 1. Create Calendar
        // Use default method for creation, which is usually fine for new calendars.
        // Fallback isn't really applicable for creating a NEW calendar, but we can ensure consistent error handling.
        let createRes = await client.request({
            method: 'POST',
            url: '/open-apis/calendar/v4/calendars',
            data: {
                summary: options.name,
                description: options.desc,
                permissions: 'private', // Default privacy
                color: -1,
                summary_alias: options.name
            }
        });

        if (createRes.code !== 0) {
            console.error(`Failed to create calendar: ${createRes.msg}`);
            process.exit(1);
        }

        const calendarId = createRes.data.calendar.calendar_id;
        console.log(`✅ Calendar Created: ${calendarId}`);

        // 2. Add Members (ACL)
        const members = options.members.split(',').map(s => s.trim()).filter(s => s);
        
        for (const userId of members) {
            console.log(`Adding member ${userId} as ${options.role}...`);
            
            // Try specific calendar ACL update
            let aclRes = await client.request({
                method: 'POST',
                url: `/open-apis/calendar/v4/calendars/${encodeURIComponent(calendarId)}/acls?user_id_type=open_id`,
                data: {
                    role: options.role,
                    scope: {
                        type: 'user',
                        user_id: userId
                    }
                }
            });

            // If failed (e.g. 403 or permission denied), check if fallback is needed, though creating a new calendar usually works fine.
            // But if this script is reused for existing calendars where permissions are tight, we might fail.
            // However, this script creates NEW calendars, so permission should be fine (Bot is owner).
            
            if (aclRes.code !== 0) {
                console.error(`❌ Failed to add ${userId}: ${aclRes.msg}`);
            } else {
                console.log(`✅ Added ${userId}`);
            }
        }
        
        // 3. Subscribe to the calendar (Bot needs to subscribe to manage it effectively? Bot is owner, auto-subscribed)
        // Actually Bot is owner, so it has access.

        console.log(`\n🎉 Shared Calendar Setup Complete! ID: ${calendarId}`);

    } catch (e) {
        console.error('Error:', e.message);
        if (e.response) console.error('Data:', JSON.stringify(e.response.data));
    }
}

main();
