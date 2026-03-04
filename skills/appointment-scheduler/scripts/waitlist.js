#!/usr/bin/env node
/**
 * Manage appointment waitlist
 * Usage:
 *   node waitlist.js add --date 2026-02-20 --time 15:00 --customer "이영희" --phone "01099998888"
 *   node waitlist.js list --date 2026-02-20
 *   node waitlist.js notify --booking-id abc123
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const args = process.argv.slice(2);
const action = args[0];

const WAITLIST_DIR = path.join(process.env.HOME, '.openclaw', 'workspace', 'data', 'appointments', 'waitlist');

function getArg(name) {
  const index = args.indexOf(name);
  return index !== -1 && args[index + 1] ? args[index + 1] : null;
}

// Create directory
if (!fs.existsSync(WAITLIST_DIR)) {
  fs.mkdirSync(WAITLIST_DIR, { recursive: true });
}

if (action === 'add') {
  const date = getArg('--date');
  const time = getArg('--time');
  const customer = getArg('--customer');
  const phone = getArg('--phone');
  const email = getArg('--email');
  
  if (!date || !time || !customer) {
    console.error('Usage: node waitlist.js add --date YYYY-MM-DD --time HH:MM --customer "name" --phone "phone"');
    process.exit(1);
  }
  
  const filePath = path.join(WAITLIST_DIR, `${date}.json`);
  let waitlist = [];
  if (fs.existsSync(filePath)) {
    waitlist = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  }
  
  const entry = {
    id: crypto.randomBytes(6).toString('hex'),
    date,
    time,
    customer: {
      name: customer,
      phone: phone || null,
      email: email || null
    },
    added_at: new Date().toISOString(),
    notified: false
  };
  
  waitlist.push(entry);
  fs.writeFileSync(filePath, JSON.stringify(waitlist, null, 2));
  
  console.log('✅ Added to waitlist:');
  console.log(JSON.stringify(entry, null, 2));
  
} else if (action === 'list') {
  const date = getArg('--date');
  if (!date) {
    console.error('Usage: node waitlist.js list --date YYYY-MM-DD');
    process.exit(1);
  }
  
  const filePath = path.join(WAITLIST_DIR, `${date}.json`);
  if (!fs.existsSync(filePath)) {
    console.log(`ℹ️  No waitlist entries for ${date}`);
    process.exit(0);
  }
  
  const waitlist = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  console.log(`\n📋 Waitlist for ${date}`);
  console.log('═'.repeat(60));
  
  waitlist.forEach((entry, index) => {
    console.log(`\n${index + 1}. ${entry.time} - ${entry.customer.name}`);
    console.log(`   Contact: ${entry.customer.phone || entry.customer.email || 'N/A'}`);
    console.log(`   Added: ${entry.added_at}`);
    console.log(`   Notified: ${entry.notified ? '✅' : '❌'}`);
  });
  console.log('\n');
  
} else if (action === 'notify') {
  const bookingId = getArg('--booking-id');
  if (!bookingId) {
    console.error('Usage: node waitlist.js notify --booking-id <id>');
    process.exit(1);
  }
  
  // Find the cancelled booking
  const BOOKINGS_DIR = path.join(process.env.HOME, '.openclaw', 'workspace', 'data', 'appointments', 'bookings');
  let booking = null;
  
  const files = fs.readdirSync(BOOKINGS_DIR).filter(f => f.endsWith('.json'));
  for (const file of files) {
    const filePath = path.join(BOOKINGS_DIR, file);
    const bookings = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    const found = bookings.find(b => b.id === bookingId);
    if (found) {
      booking = found;
      break;
    }
  }
  
  if (!booking) {
    console.error(`❌ Booking not found: ${bookingId}`);
    process.exit(1);
  }
  
  // Find waitlist entries for same date/time
  const waitlistFile = path.join(WAITLIST_DIR, `${booking.date}.json`);
  if (!fs.existsSync(waitlistFile)) {
    console.log(`ℹ️  No waitlist entries for ${booking.date}`);
    process.exit(0);
  }
  
  let waitlist = JSON.parse(fs.readFileSync(waitlistFile, 'utf8'));
  const matches = waitlist.filter(w => w.time === booking.time && !w.notified);
  
  if (matches.length === 0) {
    console.log('ℹ️  No waitlist entries to notify');
    process.exit(0);
  }
  
  // Notify first person on waitlist
  const entry = matches[0];
  const contact = entry.customer.phone || entry.customer.email;
  
  if (!contact) {
    console.log(`⚠️  No contact info for ${entry.customer.name}`);
    process.exit(1);
  }
  
  const message = `${entry.customer.name}님, 예약 자리가 났습니다!\n\n날짜: ${booking.date}\n시간: ${booking.time}\n서비스: ${booking.service}\n\n30분 내로 회신 주시면 예약 확정해드립니다. 원하시나요?`;
  
  console.log('\n📤 NOTIFY_WAITLIST');
  console.log(JSON.stringify({
    waitlist_id: entry.id,
    customer: entry.customer.name,
    contact: contact,
    message: message,
    booking_date: booking.date,
    booking_time: booking.time
  }, null, 2));
  
  // Mark as notified
  const index = waitlist.findIndex(w => w.id === entry.id);
  waitlist[index].notified = true;
  waitlist[index].notified_at = new Date().toISOString();
  fs.writeFileSync(waitlistFile, JSON.stringify(waitlist, null, 2));
  
  console.log('\n✅ Waitlist notification sent');
  
} else {
  console.error('Usage: node waitlist.js <add|list|notify> [options]');
  process.exit(1);
}
