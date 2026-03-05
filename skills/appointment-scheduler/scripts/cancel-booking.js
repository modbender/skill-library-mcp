#!/usr/bin/env node
/**
 * Cancel a booking and notify waitlist
 * Usage: node cancel-booking.js --booking-id abc123 --notify-waitlist
 */

const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const bookingId = args.includes('--booking-id') ? args[args.indexOf('--booking-id') + 1] : null;
const notifyWaitlist = args.includes('--notify-waitlist');

if (!bookingId) {
  console.error('Usage: node cancel-booking.js --booking-id <id> [--notify-waitlist]');
  process.exit(1);
}

const DATA_DIR = path.join(process.env.HOME, '.openclaw', 'workspace', 'data', 'appointments', 'bookings');

// Find booking
let booking = null;
let bookingFile = null;
let bookings = [];

const files = fs.readdirSync(DATA_DIR).filter(f => f.endsWith('.json'));
for (const file of files) {
  const filePath = path.join(DATA_DIR, file);
  bookings = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  const found = bookings.find(b => b.id === bookingId);
  if (found) {
    booking = found;
    bookingFile = filePath;
    break;
  }
}

if (!booking) {
  console.error(`❌ Booking not found: ${bookingId}`);
  process.exit(1);
}

// Cancel booking (remove from file)
const index = bookings.findIndex(b => b.id === bookingId);
bookings.splice(index, 1);
fs.writeFileSync(bookingFile, JSON.stringify(bookings, null, 2));

console.log('✅ Booking cancelled:');
console.log(JSON.stringify(booking, null, 2));

// Notify waitlist if requested
if (notifyWaitlist) {
  console.log('\n📋 Checking waitlist...');
  const { execSync } = require('child_process');
  const scriptPath = path.join(__dirname, 'waitlist.js');
  
  try {
    const output = execSync(`node "${scriptPath}" notify --booking-id ${bookingId}`, {
      encoding: 'utf8'
    });
    console.log(output);
  } catch (error) {
    console.log('ℹ️  No waitlist to notify or notification failed');
  }
}

// Log cancellation
const EVENT_DIR = path.join(process.env.HOME, '.openclaw', 'workspace', 'events');
if (!fs.existsSync(EVENT_DIR)) {
  fs.mkdirSync(EVENT_DIR, { recursive: true });
}
const eventFile = path.join(EVENT_DIR, `appointment-${booking.date}.json`);
let events = [];
if (fs.existsSync(eventFile)) {
  events = JSON.parse(fs.readFileSync(eventFile, 'utf8'));
}
events.push({
  timestamp: new Date().toISOString(),
  event: 'booking_cancelled',
  booking_id: booking.id,
  customer: booking.customer.name,
  date: booking.date,
  time: booking.time,
  service: booking.service
});
fs.writeFileSync(eventFile, JSON.stringify(events, null, 2));
