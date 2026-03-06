import { config } from './config.mjs';
import { getDb } from './db.mjs';

export async function checkBudgetAlerts() {
  const db = (await import('./db.mjs')).getDb();
  const today = new Date().toISOString().slice(0, 10);
  const monthStart = today.slice(0, 7);

  // Daily spend
  const dailyRow = db.prepare(`
    SELECT COALESCE(SUM(total_cost), 0) as total FROM daily_aggregates WHERE date = ?
  `).get(today);

  // Monthly spend
  const monthlyRow = db.prepare(`
    SELECT COALESCE(SUM(total_cost), 0) as total FROM daily_aggregates WHERE date >= ?
  `).get(monthStart + '-01');

  const alerts = [];

  if (dailyRow.total >= config.budgetDaily) {
    alerts.push({
      type: 'daily_budget',
      threshold: config.budgetDaily,
      actual: dailyRow.total,
      message: `⚠️ Daily budget alert: $${dailyRow.total.toFixed(4)} spent today (limit: $${config.budgetDaily.toFixed(2)})`,
    });
  }

  if (monthlyRow.total >= config.budgetMonthly) {
    alerts.push({
      type: 'monthly_budget',
      threshold: config.budgetMonthly,
      actual: monthlyRow.total,
      message: `🚨 Monthly budget alert: $${monthlyRow.total.toFixed(4)} this month (limit: $${config.budgetMonthly.toFixed(2)})`,
    });
  }

  for (const alert of alerts) {
    // Check if we already sent this alert today
    const existing = db.prepare(`
      SELECT 1 FROM alerts_log WHERE type = ? AND DATE(sent_at) = ? LIMIT 1
    `).get(alert.type, today);

    if (existing) continue;

    await sendAlert(alert);

    db.prepare(`
      INSERT INTO alerts_log (type, threshold, actual, message, sent_at)
      VALUES (?, ?, ?, ?, ?)
    `).run(alert.type, alert.threshold, alert.actual, alert.message, new Date().toISOString());
  }

  return alerts;
}

async function sendAlert(alert) {
  const promises = [];

  // Telegram
  if (config.telegram.botToken && config.telegram.chatId) {
    promises.push(sendTelegram(alert.message));
  }

  // Email
  if (config.smtp.host && config.smtp.to) {
    promises.push(sendEmail(alert));
  }

  if (promises.length === 0) {
    console.log(`[ALERT] ${alert.message}`);
  }

  await Promise.allSettled(promises);
}

async function sendTelegram(text) {
  const url = `https://api.telegram.org/bot${config.telegram.botToken}/sendMessage`;
  await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: config.telegram.chatId, text, parse_mode: 'HTML' }),
  });
}

async function sendEmail(alert) {
  const { createTransport } = await import('nodemailer');
  const transport = createTransport({
    host: config.smtp.host,
    port: config.smtp.port,
    auth: { user: config.smtp.user, pass: config.smtp.pass },
  });

  await transport.sendMail({
    from: config.smtp.user,
    to: config.smtp.to,
    subject: `ClawMeter: ${alert.type} alert`,
    text: alert.message,
  });
}
