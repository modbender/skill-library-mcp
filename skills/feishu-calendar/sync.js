const CalendarManager = require('./lib/CalendarManager');
const fs = require('fs');
const path = require('path');
const { getTimestampCST } = require('../common/time-helper.js');
const manager = new CalendarManager();

(async () => {
    console.log("🔄 Syncing Calendar Events (via CalendarManager)...");
    
    // 1. Get Bot Calendar (or Primary)
    // We prefer 'OpenClaw Assistant' but fallback is fine.
    const botCal = await manager.getCalendar('OpenClaw Assistant');
    if (!botCal) return console.error("Calendar not found.");

    // 2. Fetch Events (Future 7 days)
    const now = Math.floor(Date.now() / 1000);
    const endTime = now + 7 * 24 * 3600; 
    
    // Use CalendarManager's robust listing with fallback
    const events = await manager.listEvents(botCal.calendar_id, now, endTime, 50);

    if (events && events.length > 0) {
        console.log(`✅ Found ${events.length} active events.`);
        
        // Format for reporting
        let report = "📅 **OpenClaw Schedule (Next 7 Days):**\n\n";
        events.forEach(e => {
            const start = getTimestampCST(parseInt(e.start_time.timestamp) * 1000);
            report += `- **${start}**: ${e.summary || '(No Title)'} (ID: ${e.event_id.slice(-4)})\n`;
        });
        
        console.log(report);
        
        // Save state
        fs.writeFileSync(path.resolve(__dirname, '../../memory/calendar_events.json'), JSON.stringify(events, null, 2));

        // Sync to HEARTBEAT.md
        const heartbeatPath = path.resolve(__dirname, '../../HEARTBEAT.md');
        if (fs.existsSync(heartbeatPath)) {
            let heartbeatContent = fs.readFileSync(heartbeatPath, 'utf8');
            
            // Generate calendar section content
            let calendarSection = "## 📅 Calendar (Next 24h)\n\n";
            // Filter events happening in next 24h
            const next24h = events.filter(e => {
                 const t = parseInt(e.start_time.timestamp);
                 return t < (Date.now()/1000 + 86400);
            });

            if (next24h.length === 0) {
                // If no events, just keep it minimal or don't modify section? 
                // Let's explicitly say 'No events' to be helpful.
                calendarSection = "## 📅 Calendar (Next 24h)\n\n- No upcoming events in the next 24 hours.\n";
            } else {
                next24h.forEach(e => {
                    const start = getTimestampCST(parseInt(e.start_time.timestamp) * 1000).split(' ')[1]; // Extract HH:MM
                    calendarSection += `- [ ] ${start} - ${e.summary}\n`;
                });
            }
            
            // Regex to find existing Calendar section or append
            // We look for "## 📅 Calendar" or just "## Calendar"
            const calendarRegex = /## (?:📅 )?Calendar.*?(?=\n## |$)/s;
            
            if (calendarRegex.test(heartbeatContent)) {
                // Replace existing section
                heartbeatContent = heartbeatContent.replace(calendarRegex, calendarSection.trim());
            } else {
                // Append before "## Morning" or at end if not found
                const insertPos = heartbeatContent.indexOf('## Morning');
                if (insertPos !== -1) {
                    heartbeatContent = heartbeatContent.slice(0, insertPos) + calendarSection + "\n" + heartbeatContent.slice(insertPos);
                } else {
                    heartbeatContent += "\n" + calendarSection;
                }
            }
            
            fs.writeFileSync(heartbeatPath, heartbeatContent, 'utf8');
            console.log("✅ Synced to HEARTBEAT.md");
        }

    } else {
        console.log("No active events found.");
        // Clear HEARTBEAT.md calendar section if empty? Or keep it blank?
        // Let's keep it minimal if empty.
    }
})();
