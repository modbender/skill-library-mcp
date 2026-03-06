#!/usr/bin/env node
/**
 * Create a new booking
 * Usage: node book.js --date 2026-02-20 --time 15:00 --duration 60 --service "컷" --customer "김철수" --phone "01012345678"
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// Parse arguments
const args = process.argv.slice(2);
function getArg(name) {
  const index = args.indexOf(name);
  return index !== -1 && args[index + 1] ? args[index + 1] : null;
}

const date = getArg('--date');
const time = getArg('--time');
const duration = parseInt(getArg('--duration')) || 60;
const service = getArg('--service');
const customer = getArg('--customer');
const phone = getArg('--phone');
const email = getArg('--email');
const notes = getArg('--notes') || '';

if (!date || !time || !service || !customer) {
  console.error('Usage: node book.js --date YYYY-MM-DD --time HH:MM --service "service" --customer "name" --phone "phone"');
  process.exit(1);
}

// Load config
const CONFIG_FILE = path.join(process.env.HOME, '.openclaw', 'workspace', 'config', 'appointment-scheduler.json');
if (!fs.existsSync(CONFIG_FILE)) {
  console.error('❌ Config not found. Run init-config.js first.');
  process.exit(1);
}
const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));

// Check if service exists
if (!config.services[service]) {
  console.error(`❌ Unknown service: ${service}`);
  console.error('Available services:', Object.keys(config.services).join(', '));
  process.exit(1);
}

// Create booking data directory
const DATA_DIR = path.join(process.env.HOME, '.openclaw', 'workspace', 'data', 'appointments', 'bookings');
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

// Load or create daily bookings file
const dailyFile = path.join(DATA_DIR, `${date}.json`);
let bookings = [];
if (fs.existsSync(dailyFile)) {
  bookings = JSON.parse(fs.readFileSync(dailyFile, 'utf8'));
}

// Check for conflicts
const [hours, minutes] = time.split(':').map(Number);
const startMinutes = hours * 60 + minutes;
const endMinutes = startMinutes + duration + (config.services[service].buffer || 0);

const conflict = bookings.find(b => {
  const [bHours, bMinutes] = b.time.split(':').map(Number);
  const bStartMinutes = bHours * 60 + bMinutes;
  const bEndMinutes = bStartMinutes + b.duration + (config.services[b.service]?.buffer || 0);
  
  return (startMinutes < bEndMinutes && endMinutes > bStartMinutes);
});

if (conflict) {
  console.error('❌ Conflict detected with existing booking:');
  console.error(JSON.stringify(conflict, null, 2));
  console.error('\n💡 Suggestion: Add to waitlist or choose different time');
  process.exit(2);
}

// Create booking
const booking = {
  id: crypto.randomBytes(6).toString('hex'),
  date,
  time,
  duration,
  service,
  customer: {
    name: customer,
    phone: phone || null,
    email: email || null
  },
  notes,
  status: 'confirmed',
  created_at: new Date().toISOString(),
  reminded: {
    day_before: false,
    hour_before: false
  }
};

bookings.push(booking);
bookings.sort((a, b) => a.time.localeCompare(b.time));

// Save
fs.writeFileSync(dailyFile, JSON.stringify(bookings, null, 2));

console.log('✅ Booking created:');
console.log(JSON.stringify(booking, null, 2));

// Log event
const EVENT_DIR = path.join(process.env.HOME, '.openclaw', 'workspace', 'events');
if (!fs.existsSync(EVENT_DIR)) {
  fs.mkdirSync(EVENT_DIR, { recursive: true });
}
const eventFile = path.join(EVENT_DIR, `appointment-${date}.json`);
let events = [];
if (fs.existsSync(eventFile)) {
  events = JSON.parse(fs.readFileSync(eventFile, 'utf8'));
}
events.push({
  timestamp: new Date().toISOString(),
  event: 'booking_created',
  booking_id: booking.id,
  customer: customer,
  date,
  time,
  service
});
fs.writeFileSync(eventFile, JSON.stringify(events, null, 2));
