#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

/**
 * Daily Digest Logger & Stylizer
 * Usage: node digest.js '{"emails": [...], "calendar": [...], "news": [...]}'
 */

const inputData = process.argv[2] ? JSON.parse(process.argv[2]) : {};

const dateStr = new Date().toISOString().split('T')[0];
const logDir = path.join(process.env.USERPROFILE || process.env.HOME, '.openclaw', 'cron', 'DailyDigest_logs');
const logFile = path.join(logDir, `${dateStr}.md`);

function getUrgentEmails() {
    if (inputData.emails) return inputData.emails;
    try {
        const output = execSync('himalaya --output json envelope list --page-size 20').toString();
        const jsonStart = output.indexOf('[');
        return jsonStart !== -1 ? JSON.parse(output.substring(jsonStart)) : [];
    } catch (e) {
        return [];
    }
}

const emails = getUrgentEmails();
const calendar = inputData.calendar || [];
const tasks = inputData.tasks || [];
const news = inputData.news || [];

const htmlContent = `
<div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 800px; margin: 20px auto; padding: 30px; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); color: #333; line-height: 1.6; border: 1px solid #eef2f6;">
    <header style="border-bottom: 3px solid #0077b5; padding-bottom: 15px; margin-bottom: 25px; text-align: center;">
        <h1 style="color: #0077b5; margin: 0; font-size: 2.2em; letter-spacing: -1px;">Daily Digest</h1>
        <p style="color: #666; margin: 5px 0 0 0; font-weight: 500;">${new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
    </header>

    <section style="margin-bottom: 30px;">
        <h2 style="color: #0077b5; border-bottom: 1px solid #e1e8ed; padding-bottom: 8px; font-size: 1.4em; display: flex; align-items: center;">
            <span style="margin-right: 10px;">📧</span> Urgent Emails (Top 20)
        </h2>
        ${emails.length > 0 ? emails.map(e => `
            <div style="padding: 12px; border-radius: 8px; background: #f8fafc; margin-bottom: 10px; border-left: 4px solid #0077b5;">
                <div style="font-weight: bold; color: #1e293b;">${e.subject}</div>
                <div style="font-size: 0.9em; color: #64748b;">From: ${e.from.name || e.from.addr} • ${new Date(e.date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</div>
            </div>
        `).join('') : '<p style="color: #94a3b8; font-style: italic;">No urgent emails found.</p>'}
    </section>

    <section style="margin-bottom: 30px;">
        <h2 style="color: #0077b5; border-bottom: 1px solid #e1e8ed; padding-bottom: 8px; font-size: 1.4em; display: flex; align-items: center;">
            <span style="margin-right: 10px;">🗓️</span> Calendar Events
        </h2>
        ${calendar.length > 0 ? calendar.map(c => `
            <div style="padding: 12px; border-radius: 8px; background: #fdf2f2; margin-bottom: 10px; border-left: 4px solid #ef4444;">
                <div style="font-weight: bold; color: #991b1b;">${c.summary}</div>
                <div style="font-size: 0.9em; color: #b91c1c;">${c.start} - ${c.end}</div>
            </div>
        `).join('') : '<p style="color: #94a3b8; font-style: italic;">Your schedule is clear today.</p>'}
    </section>

    <section style="margin-bottom: 30px;">
        <h2 style="color: #0077b5; border-bottom: 1px solid #e1e8ed; padding-bottom: 8px; font-size: 1.4em; display: flex; align-items: center;">
            <span style="margin-right: 10px;">✅</span> Tasks & To-Dos
        </h2>
        ${tasks.length > 0 ? tasks.map(t => `
            <div style="padding: 12px; border-radius: 8px; background: #f0fdf4; margin-bottom: 10px; border-left: 4px solid #22c55e;">
                <div style="font-weight: bold; color: #166534;">${t.title}</div>
                ${t.due ? `<div style="font-size: 0.9em; color: #15803d;">Due: ${t.due}</div>` : ''}
            </div>
        `).join('') : '<p style="color: #94a3b8; font-style: italic;">No tasks due today.</p>'}
    </section>

    <section style="margin-bottom: 20px;">
        <h2 style="color: #0077b5; border-bottom: 1px solid #e1e8ed; padding-bottom: 8px; font-size: 1.4em; display: flex; align-items: center;">
            <span style="margin-right: 10px;">📰</span> Top News
        </h2>
        ${news.length > 0 ? news.map(n => `
            <div style="margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px dashed #e2e8f0;">
                <a href="${n.url}" style="text-decoration: none; font-weight: 600; color: #1e293b; display: block; margin-bottom: 4px; font-size: 1.1em;">${n.title}</a>
                <p style="margin: 0; font-size: 0.9em; color: #475569;">${n.snippet || ''}</p>
            </div>
        `).join('') : '<p style="color: #94a3b8; font-style: italic;">No news highlights for today.</p>'}
    </section>
    
    <footer style="margin-top: 40px; text-align: center; color: #cbd5e1; font-size: 0.8em; border-top: 1px solid #f1f5f9; padding-top: 20px;">
        Generated by OpenClaw Daily Digest Skill • ${new Date().toLocaleTimeString()}
    </footer>
</div>
`;

const markdownContent = `---
title: Daily Digest ${dateStr}
---

${htmlContent}

---
*Source: Automatic Daily Digest Run*
`;

try {
    if (!fs.existsSync(logDir)) fs.mkdirSync(logDir, { recursive: true });
    fs.writeFileSync(logFile, markdownContent);
    console.log(`Successfully logged digest to: ${logFile}`);
    
    // Output a summary for the agent to use in notifications
    const summary = `Daily Digest for ${dateStr}: ${emails.length} emails, ${calendar.length} events, and ${tasks.length} tasks.`;
    console.log(`NOTIFICATION_SUMMARY: ${summary}`);
} catch (e) {
    console.error(`Failed to write log: ${e.message}`);
}
