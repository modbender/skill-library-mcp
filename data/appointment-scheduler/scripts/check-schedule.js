#!/usr/bin/env node
/**
 * Check appointment schedule
 * Usage: 
 *   node check-schedule.js --date today
 *   node check-schedule.js --date 2026-02-20
 *   node check-schedule.js --week
 */

const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const dateArg = args.includes('--date') ? args[args.indexOf('--date') + 1] : null;
const weekMode = args.includes('--week');

const DATA_DIR = path.join(process.env.HOME, '.openclaw', 'workspace', 'data', 'appointments', 'bookings');

function formatDate(date) {
  return date.toISOString().split('T')[0];
}

function getBookingsForDate(dateStr) {
  const filePath = path.join(DATA_DIR, `${dateStr}.json`);
  if (!fs.existsSync(filePath)) {
    return [];
  }
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function displayBookings(dateStr, bookings) {
  console.log(`\n📅 ${dateStr}`);
  console.log('═'.repeat(60));
  
  if (bookings.length === 0) {
    console.log('  (예약 없음)');
    return;
  }
  
  bookings.forEach(b => {
    const statusEmoji = b.status === 'confirmed' ? '✅' : 
                       b.status === 'noshow' ? '❌' : '⏳';
    console.log(`  ${statusEmoji} ${b.time} | ${b.service} (${b.duration}분)`);
    console.log(`     고객: ${b.customer.name} ${b.customer.phone || ''}`);
    if (b.notes) {
      console.log(`     메모: ${b.notes}`);
    }
  });
}

// Main logic
if (weekMode) {
  const today = new Date();
  const dayOfWeek = today.getDay();
  const monday = new Date(today);
  monday.setDate(today.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1));
  
  console.log('📆 이번 주 예약 현황');
  for (let i = 0; i < 7; i++) {
    const date = new Date(monday);
    date.setDate(monday.getDate() + i);
    const dateStr = formatDate(date);
    const bookings = getBookingsForDate(dateStr);
    displayBookings(dateStr, bookings);
  }
} else {
  let targetDate;
  if (dateArg === 'today' || !dateArg) {
    targetDate = formatDate(new Date());
  } else if (dateArg === 'tomorrow') {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    targetDate = formatDate(tomorrow);
  } else {
    targetDate = dateArg;
  }
  
  const bookings = getBookingsForDate(targetDate);
  displayBookings(targetDate, bookings);
}

console.log('\n');
