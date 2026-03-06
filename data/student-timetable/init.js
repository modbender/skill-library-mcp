const fs = require('fs');
const path = require('path');
const readline = require('readline');
const { inferTimezone, isValidTimeZone, normalizeCountry } = require('./timezone_infer.js');

function normalizeToken(s) {
  return String(s || '')
    .trim()
    .replace(/\s+/g, ' ');
}

function normalizeId(s) {
  return String(s || '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9\-]/g, '')
    .replace(/\-+/g, '-')
    .replace(/^\-+|\-+$/g, '') || 'profile';
}

function nowIso() {
  return new Date().toISOString();
}

function writeJsonAtomic(p, obj) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  const tmp = `${p}.tmp-${process.pid}-${Date.now()}`;
  fs.writeFileSync(tmp, JSON.stringify(obj, null, 2));
  fs.renameSync(tmp, p);
}

function exists(p) {
  try {
    fs.accessSync(p);
    return true;
  } catch {
    return false;
  }
}

function ask(rl, q) {
  return new Promise((resolve) => rl.question(q, (ans) => resolve(ans)));
}

function emptyWeek() {
  return { mon: [], tue: [], wed: [], thu: [], fri: [], sat: [], sun: [] };
}

async function interactiveInit(workspaceRoot) {
  const registryPath = path.join(workspaceRoot, 'schedules', 'profiles', 'registry.json');
  const registry = exists(registryPath)
    ? JSON.parse(fs.readFileSync(registryPath, 'utf8'))
    : { version: 1, dataRoot: 'schedules/profiles', profiles: [] };

  const existingIds = new Set((registry.profiles || []).map(p => String(p.profile_id || '')).filter(Boolean));

  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  try {
    console.log('student-timetable init');
    console.log('');
    console.log('Who is this timetable for?');
    console.log('  1) Myself (student)');
    console.log('  2) My child / children (parent/guardian)');
    const mode = normalizeToken(await ask(rl, 'Choose 1 or 2: '));

    let profilesToCreate = [];

    console.log('');
    console.log('Base profile info (stored as metadata):');
    const countryRaw = normalizeToken(await ask(rl, 'Country (e.g. SG, CN): '));
    const country = normalizeCountry(countryRaw);
    const city = normalizeToken(await ask(rl, 'City (optional): '));
    const school = normalizeToken(await ask(rl, 'School (optional): '));
    const grade = normalizeToken(await ask(rl, 'Grade (optional): '));
    const klass = normalizeToken(await ask(rl, 'Class (optional): '));

    const tzGuess = inferTimezone(country, city, '');
    console.log(`Timezone inferred: ${tzGuess.timezone} (${tzGuess.source})`);
    const tzOverride = normalizeToken(await ask(rl, 'Timezone override (IANA, optional, enter to accept inferred): '));
    let timezone = tzGuess.timezone;
    if (tzOverride) {
      if (!isValidTimeZone(tzOverride)) {
        throw new Error(`Invalid timezone override: ${tzOverride}`);
      }
      timezone = tzOverride;
    }

    console.log('');
    console.log('Global wake keywords (optional):');
    console.log('These are shared across all profiles and can be used for routing/triggering later.');
    const wakeRaw = normalizeToken(await ask(rl, 'Wake keywords (comma-separated, optional): '));
    const wakeKeywords = wakeRaw ? wakeRaw.split(',').map(a => normalizeToken(a)).filter(Boolean) : [];

    if (mode === '1') {
      const name = normalizeToken(await ask(rl, 'Your name (display name): '));
      const aliasesRaw = normalizeToken(await ask(rl, 'Aliases (optional, comma-separated): '));
      const aliases = aliasesRaw ? aliasesRaw.split(',').map(a => normalizeToken(a)).filter(Boolean) : [];
      let profileId = normalizeId(name || 'self');
      if (existingIds.has(profileId)) {
        let i = 2;
        while (existingIds.has(`${profileId}-${i}`)) i++;
        profileId = `${profileId}-${i}`;
      }
      existingIds.add(profileId);
      profilesToCreate.push({ profile_id: profileId, type: 'self', display_name: name || 'Self', aliases });
    } else if (mode === '2') {
      const nRaw = normalizeToken(await ask(rl, 'How many children? '));
      const n = Math.max(1, parseInt(nRaw, 10) || 1);
      for (let i = 0; i < n; i++) {
        const name = normalizeToken(await ask(rl, `Child ${i + 1} name (display name): `));
        const aliasesRaw = normalizeToken(await ask(rl, 'Aliases (optional, comma-separated): '));
        const aliases = aliasesRaw ? aliasesRaw.split(',').map(a => normalizeToken(a)).filter(Boolean) : [];
        let profileId = normalizeId(name || `child-${i + 1}`);
        if (existingIds.has(profileId)) {
          let j = 2;
          while (existingIds.has(`${profileId}-${j}`)) j++;
          profileId = `${profileId}-${j}`;
        }
        existingIds.add(profileId);
        profilesToCreate.push({ profile_id: profileId, type: 'child', display_name: name || `Child ${i + 1}`, aliases });
      }
    } else {
      throw new Error('Invalid choice.');
    }

    console.log('');
    console.log('Recurrence:');
    console.log('  1) every_week');
    console.log('  2) biweekly (Week A / Week B)');
    const recChoice = normalizeToken(await ask(rl, 'Choose 1 or 2: '));

    let recurrence = { type: 'every_week' };
    if (recChoice === '2') {
      const startDate = normalizeToken(await ask(rl, 'Biweekly start_date (YYYY-MM-DD): '));
      recurrence = { type: 'biweekly', start_date: startDate };
    }

    // Minimal ingest: create empty templates; users edit JSON by hand or extend later.
    const createdAt = nowIso();
    for (const p of profilesToCreate) {
      const entry = {
        profile_id: p.profile_id,
        type: p.type,
        display_name: p.display_name,
        aliases: p.aliases,
        base_info: {
          country: country || '',
          city: city || '',
          school: school || '',
          grade: grade || '',
          timezone: timezone || '',
          class: klass || ''
        },
        created_at: createdAt,
        updated_at: createdAt
      };
      registry.profiles.push(entry);

      const base = path.join(workspaceRoot, 'schedules', 'profiles', p.profile_id);
      const weeklyPath = path.join(base, 'weekly.json');
      const specialPath = path.join(base, 'special_events.json');
      const termPath = path.join(base, 'term_calendar.json');

      if (!exists(weeklyPath)) {
        const weeks = recurrence.type === 'biweekly'
          ? { week_a: emptyWeek(), week_b: emptyWeek() }
          : { default: emptyWeek() };
        writeJsonAtomic(weeklyPath, {
          version: 1,
          profile_id: p.profile_id,
          recurrence,
          timezone,
          weeks
        });
      }

      if (!exists(specialPath)) {
        writeJsonAtomic(specialPath, { version: 1, profile_id: p.profile_id, events: [] });
      }

      if (!exists(termPath)) {
        writeJsonAtomic(termPath, { version: 1, profile_id: p.profile_id, timezone, terms: [], no_school_days: [] });
      }

      console.log(`Created/verified: schedules/profiles/${p.profile_id}/weekly.json`);
      console.log(`Created/verified: schedules/profiles/${p.profile_id}/special_events.json`);
      console.log(`Created/verified: schedules/profiles/${p.profile_id}/term_calendar.json`);
      console.log('');
    }

    registry.version = 1;
    registry.dataRoot = 'schedules/profiles';
    registry.global = registry.global || {};
    if (!Array.isArray(registry.global.wake_keywords)) {
      registry.global.wake_keywords = [];
    }
    for (const kw of wakeKeywords) {
      if (!registry.global.wake_keywords.includes(kw)) {
        registry.global.wake_keywords.push(kw);
      }
    }
    writeJsonAtomic(registryPath, registry);

    console.log(`Registry written: schedules/profiles/registry.json`);
  } finally {
    rl.close();
  }
}

module.exports = { interactiveInit };
