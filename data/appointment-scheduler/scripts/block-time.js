#!/usr/bin/env node
/**
 * Block off time slots (e.g., lunch break, holidays)
 * Usage: node block-time.js --date 2026-02-20 --start 12:00 --end 13:00 --reason "점심시간"
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const args = process.argv.slice(2);

function getArg(name) {
  const index = args.indexOf(name);
  return index !== -1 && args[index + 1] ? args[index + 1] : null;
}

const date = getArg('--date');
const start = getArg('--start');
const end = getArg('--end');
const reason = getArg('--reason') || 'Blocked';

if (!date || !start || !end) {
  console.error('Usage: node block-time.js --date YYYY-MM-DD --start HH:MM --end HH:MM --reason "reason"');
  process.exit(1);
}

const DATA_DIR = path.join(process.env.HOME, '.openclaw', 'workspace', 'data', 'appointments', 'bookings');
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

const filePath = path.join(DATA_DIR, `${date}.json`);
let bookings = [];
if (fs.existsSync(filePath)) {
  bookings = JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

// Calculate duration
const [startHours, startMinutes] = start.split(':').map(Number);
const [endHours, endMinutes] = end.split(':').map(Number);
const duration = (endHours * 60 + endMinutes) - (startHours * 60 + startMinutes);

// Create blocked slot
const blocked = {
  id: crypto.randomBytes(6).toString('hex'),
  date,
  time: start,
  duration,
  service: 'BLOCKED',
  customer: {
    name: reason,
    phone: null,
    email: null
  },
  notes: `Blocked: ${reason}`,
  status: 'blocked',
  created_at: new Date().toISOString()
};

bookings.push(blocked);
bookings.sort((a, b) => a.time.localeCompare(b.time));

fs.writeFileSync(filePath, JSON.stringify(bookings, null, 2));

console.log('✅ Time slot blocked:');
console.log(JSON.stringify(blocked, null, 2));
