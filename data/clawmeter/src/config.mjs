import { config as dotenvConfig } from 'dotenv';
import { resolve } from 'path';
import { existsSync } from 'fs';

const envPath = resolve(import.meta.dirname, '..', '.env');
if (existsSync(envPath)) dotenvConfig({ path: envPath });

export const config = {
  agentsDir: process.env.OPENCLAW_AGENTS_DIR || resolve(process.env.HOME, '.openclaw', 'agents'),
  dbPath: process.env.CLAWMETER_DB || resolve(import.meta.dirname, '..', 'data', 'clawmeter.db'),
  port: parseInt(process.env.PORT || '3377', 10),
  budgetDaily: parseFloat(process.env.BUDGET_DAILY_LIMIT || '5.00'),
  budgetMonthly: parseFloat(process.env.BUDGET_MONTHLY_LIMIT || '100.00'),
  telegram: {
    botToken: process.env.TELEGRAM_BOT_TOKEN || '',
    chatId: process.env.TELEGRAM_CHAT_ID || '',
  },
  smtp: {
    host: process.env.SMTP_HOST || '',
    port: parseInt(process.env.SMTP_PORT || '587', 10),
    user: process.env.SMTP_USER || '',
    pass: process.env.SMTP_PASS || '',
    to: process.env.ALERT_EMAIL_TO || '',
  },
};
