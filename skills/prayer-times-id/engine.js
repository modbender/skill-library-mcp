#!/usr/bin/env node
'use strict';

const fs = require('node:fs/promises');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

const BASE_DIR = __dirname;
const CONFIG_PATH = path.join(BASE_DIR, 'prayer_config.json');
const QUOTES_PATH = path.join(BASE_DIR, 'quotes_id.json');

const TARGET_PRAYERS = [
  { key: 'Imsak', label: 'Imsak' },
  { key: 'Fajr', label: 'Subuh' },
  { key: 'Dhuhr', label: 'Dzuhur' },
  { key: 'Asr', label: 'Ashar' },
  { key: 'Maghrib', label: 'Maghrib' },
  { key: 'Isha', label: 'Isya' }
];

function parseTimeToDate(dateObj, hhmm) {
  const clean = String(hhmm).trim().replace(/\s*\(.+\)$/, '');
  const [h, m] = clean.split(':').map((v) => parseInt(v, 10));
  if (Number.isNaN(h) || Number.isNaN(m)) {
    throw new Error(`Format waktu tidak valid: ${hhmm}`);
  }
  const d = new Date(dateObj);
  d.setHours(h, m, 0, 0);
  return d;
}

function toLocalDateParts(date, timezone) {
  const dtf = new Intl.DateTimeFormat('en-GB', {
    timeZone: timezone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  });

  const parts = Object.fromEntries(dtf.formatToParts(date).map((p) => [p.type, p.value]));

  return {
    year: Number(parts.year),
    month: Number(parts.month),
    day: Number(parts.day),
    hour: Number(parts.hour),
    minute: Number(parts.minute),
    second: Number(parts.second)
  };
}

function getUtcOffsetString(date, timezone) {
  const local = toLocalDateParts(date, timezone);
  const asUtcMs = Date.UTC(local.year, local.month - 1, local.day, local.hour, local.minute, local.second);
  const offsetMin = Math.round((asUtcMs - date.getTime()) / 60000);
  const sign = offsetMin >= 0 ? '+' : '-';
  const abs = Math.abs(offsetMin);
  const hh = String(Math.floor(abs / 60)).padStart(2, '0');
  const mm = String(abs % 60).padStart(2, '0');
  return `${sign}${hh}:${mm}`;
}

function toIsoWithOffset(date, timezone = 'Asia/Jakarta') {
  const p = toLocalDateParts(date, timezone);
  const offset = getUtcOffsetString(date, timezone);
  return `${String(p.year).padStart(4, '0')}-${String(p.month).padStart(2, '0')}-${String(p.day).padStart(2, '0')}T${String(p.hour).padStart(2, '0')}:${String(p.minute).padStart(2, '0')}:${String(p.second).padStart(2, '0')}${offset}`;
}

function pickQuote(quotes) {
  if (!Array.isArray(quotes) || quotes.length === 0) {
    return {
      text: 'Perbanyak dzikir, perbaiki niat, dan jaga shalat tepat waktu.',
      source: 'Pengingat Harian'
    };
  }
  const idx = Math.floor(Math.random() * quotes.length);
  return quotes[idx];
}

async function fetchJson(url) {
  const res = await fetch(url, { signal: AbortSignal.timeout(15000) });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status} saat akses ${url}`);
  }
  const data = await res.json();
  if (String(data.code) !== '200') {
    throw new Error(`API error (${url}): ${data.status || 'unknown'}`);
  }
  return data;
}

function buildReminderMessage({ prayerLabel, prayerTime, locationName, isRamadan, quote, nowDate }) {
  const dateId = new Intl.DateTimeFormat('id-ID', {
    weekday: 'long',
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  }).format(nowDate);

  const ramadanBadge = isRamadan ? '🌙 Ramadan: Ya' : '🌙 Ramadan: Tidak';

  return [
    '🕌 *Z-Cloud Prayer Reminder*',
    `📍 ${locationName}`,
    `📅 ${dateId}`,
    '',
    `⏰ Waktu *${prayerLabel}* telah tiba (${prayerTime})`,
    ramadanBadge,
    '',
    '📖 *Quote Hari Ini*',
    `“${quote.text}”`,
    `— ${quote.source}`
  ].join('\n');
}

function runOpenClaw(args) {
  return execFileSync('openclaw', args, {
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe']
  });
}

function scheduleSystemEvent({ whenIso, name, message }) {
  const args = [
    'cron', 'add',
    '--name', name,
    '--at', whenIso,
    '--system-event', message,
    '--delete-after-run',
    '--json'
  ];

  const out = runOpenClaw(args);
  return { mode: 'direct', command: `openclaw ${args.join(' ')}`, output: out.trim() };
}

function sanitizeLocationName(name) {
  return String(name || '').replace(/[^a-zA-Z0-9\s-]/g, '').trim();
}

function validateConfig(config) {
  const lat = Number(config?.location?.latitude);
  const lon = Number(config?.location?.longitude);
  const name = sanitizeLocationName(config?.location?.name);

  if (!name) throw new Error('config.location.name wajib diisi');
  if (!Number.isFinite(lat) || lat < -90 || lat > 90) throw new Error('latitude tidak valid');
  if (!Number.isFinite(lon) || lon < -180 || lon > 180) throw new Error('longitude tidak valid');

  const method = Number(config?.settings?.method ?? 11);
  if (!Number.isInteger(method) || method < 0 || method > 99) {
    throw new Error('settings.method tidak valid');
  }

  const methodSettingsRaw = config?.settings?.methodSettings;
  const tuneRaw = config?.settings?.tune;
  const methodSettings = typeof methodSettingsRaw === 'string' ? methodSettingsRaw.trim() : '';
  const tune = typeof tuneRaw === 'string' ? tuneRaw.trim() : '';

  return {
    latitude: lat,
    longitude: lon,
    locationName: name,
    timezone: String(config?.settings?.timezone || 'Asia/Jakarta'),
    method,
    methodSettings,
    tune
  };
}

async function main() {
  const dryRun = process.argv.includes('--dry-run');

  const [configRaw, quotesRaw] = await Promise.all([
    fs.readFile(CONFIG_PATH, 'utf8'),
    fs.readFile(QUOTES_PATH, 'utf8')
  ]);

  const config = JSON.parse(configRaw);
  const quotes = JSON.parse(quotesRaw);

  const { latitude, longitude, locationName, timezone, method, methodSettings, tune } = validateConfig(config);

  const queryParams = [
    `latitude=${encodeURIComponent(latitude)}`,
    `longitude=${encodeURIComponent(longitude)}`,
    `method=${encodeURIComponent(method)}`
  ];

  if (methodSettings) {
    queryParams.push(`methodSettings=${encodeURIComponent(methodSettings)}`);
  }

  if (tune) {
    queryParams.push(`tune=${encodeURIComponent(tune)}`);
  }

  const timingsUrl = `https://api.aladhan.com/v1/timings?${queryParams.join('&')}`;
  const timingsData = await fetchJson(timingsUrl);

  const gregorian = timingsData.data?.date?.gregorian;
  if (!gregorian?.day || !gregorian?.month?.number || !gregorian?.year) {
    throw new Error('Response API timings tidak lengkap (tanggal gregorian).');
  }

  const hijriDateForLookup = `${gregorian.day}-${gregorian.month.number}-${gregorian.year}`;
  const hijriUrl = `https://api.aladhan.com/v1/gToH?date=${encodeURIComponent(hijriDateForLookup)}`;
  const hijriData = await fetchJson(hijriUrl);

  let isRamadan = false;
  const manualOverride = config.settings?.manual_override;
  if (typeof manualOverride === 'boolean') {
    isRamadan = manualOverride;
  } else if (config.settings?.auto_ramadan !== false) {
    const monthNo = Number(hijriData.data?.hijri?.month?.number || 0);
    isRamadan = monthNo === 9;
  }

  const today = new Date();
  const scheduleDate = new Date(
    Number(gregorian.year),
    Number(gregorian.month.number) - 1,
    Number(gregorian.day),
    0,
    0,
    0,
    0
  );

  const registrations = [];

  for (const prayer of TARGET_PRAYERS) {
    const apiTime = timingsData.data?.timings?.[prayer.key];
    if (!apiTime) continue;

    const triggerAt = parseTimeToDate(scheduleDate, apiTime);
    if (triggerAt <= new Date()) continue;

    const timeLabel = String(apiTime).replace(/\s*\(.+\)$/, '');
    const quote = pickQuote(quotes);

    const message = buildReminderMessage({
      prayerLabel: prayer.label,
      prayerTime: timeLabel,
      locationName,
      isRamadan,
      quote,
      nowDate: today
    });

    const whenIso = toIsoWithOffset(triggerAt, timezone);
    const jobName = `prayer-${prayer.label.toLowerCase()}-${whenIso.slice(0, 10)}`;

    const result = dryRun
      ? { mode: 'dry-run', command: '(skip)', output: 'not executed' }
      : scheduleSystemEvent({ whenIso, name: jobName, message });

    registrations.push({
      prayer: prayer.label,
      time: timeLabel,
      whenIso,
      ...result
    });
  }

  console.log(JSON.stringify({
    status: 'ok',
    dryRun,
    location: locationName,
    timezone,
    ramadan: isRamadan,
    registered: registrations.length,
    jobs: registrations
  }, null, 2));
}

main().catch((err) => {
  console.error('[engine] gagal:', err.message);
  process.exit(1);
});
