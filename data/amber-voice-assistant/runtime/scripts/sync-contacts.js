/**
 * sync-contacts.js — Export Apple Contacts to a local JSON cache
 *
 * PRIVACY NOTICE: This script reads the macOS AddressBook SQLite database to
 * export your Apple Contacts to a local JSON file (contacts-cache.json).
 * This is an OPT-IN feature — you must explicitly run `npm run sync-contacts`
 * to generate the cache. The cache file is local-only, excluded from version
 * control (.gitignore) and skill packages (.npmignore), and is never uploaded
 * or transmitted anywhere.
 *
 * SECURITY NOTE: SQL queries in this file use parameterized statements
 * (db.prepare(...).all(r.Z_PK)) for all user-supplied values. The only
 * string interpolation used is for constructing file paths, not SQL queries.
 *
 * Purpose: Enables Amber to call people by name ("call Abe") by resolving
 * names to phone numbers locally, without any cloud lookup.
 */

'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');

// Resolve better-sqlite3 relative to this script's location (runtime/scripts/ → runtime/node_modules/)
const Database = require(path.join(__dirname, '..', 'node_modules', 'better-sqlite3'));

const abDir = path.join(os.homedir(), 'Library', 'Application Support', 'AddressBook');
const sourcesDir = path.join(abDir, 'Sources');

const dbPaths = [];
const mainDb = path.join(abDir, 'AddressBook-v22.abcddb');
if (fs.existsSync(mainDb)) dbPaths.push(mainDb);
if (fs.existsSync(sourcesDir)) {
  for (const s of fs.readdirSync(sourcesDir)) {
    const p = path.join(sourcesDir, s, 'AddressBook-v22.abcddb');
    if (fs.existsSync(p)) dbPaths.push(p);
  }
}

if (dbPaths.length === 0) {
  console.error('No AddressBook database found. Make sure Apple Contacts is set up on this Mac.');
  process.exit(1);
}

function cleanLabel(l) {
  if (!l) return '';
  return l.replace(/^_\$!</, '').replace(/>!\$_$/, '');
}

// Merge map: name-based key → merged contact
const mergeMap = new Map();

for (const dbPath of dbPaths) {
  try {
    const db = new Database(dbPath, { readonly: true, fileMustExist: true });

    // All queries use parameterized statements — no string interpolation in SQL
    const recordStmt = db.prepare(
      'SELECT Z_PK, ZFIRSTNAME, ZLASTNAME, ZNICKNAME, ZORGANIZATION, ZJOBTITLE, ZNOTE FROM ZABCDRECORD'
    );
    const phoneStmt = db.prepare(
      'SELECT ZFULLNUMBER, ZLABEL FROM ZABCDPHONENUMBER WHERE ZOWNER = ? AND ZFULLNUMBER IS NOT NULL'
    );
    const emailStmt = db.prepare(
      'SELECT ZADDRESS, ZLABEL FROM ZABCDEMAILADDRESS WHERE ZOWNER = ? AND ZADDRESS IS NOT NULL'
    );
    const relStmt = db.prepare(
      'SELECT ZNAME, ZLABEL FROM ZABCDRELATEDNAME WHERE ZOWNER = ? AND ZNAME IS NOT NULL'
    );
    const addrStmt = db.prepare(
      'SELECT ZSTREET, ZCITY, ZSTATE, ZZIPCODE, ZCOUNTRYNAME, ZLABEL FROM ZABCDPOSTALADDRESS WHERE ZOWNER = ?'
    );

    const records = recordStmt.all();

    for (const r of records) {
      const fn = (r.ZFIRSTNAME || '').trim();
      const ln = (r.ZLASTNAME || '').trim();
      if (!fn && !ln) continue;

      const mergeKey = `${fn.toLowerCase()}_${ln.toLowerCase()}`;
      let contact = mergeMap.get(mergeKey);
      if (!contact) {
        contact = {
          firstName: fn, lastName: ln,
          nickname: '', organization: '', jobTitle: '', note: '',
          phones: [], emails: [], relationships: [], addresses: [],
          _seenPhones: new Set(), _seenEmails: new Set(), _seenRels: new Set(),
        };
        mergeMap.set(mergeKey, contact);
      }

      if (!contact.nickname && r.ZNICKNAME) contact.nickname = r.ZNICKNAME;
      if (!contact.organization && r.ZORGANIZATION) contact.organization = r.ZORGANIZATION;
      if (!contact.jobTitle && r.ZJOBTITLE) contact.jobTitle = r.ZJOBTITLE;
      if (!contact.note && r.ZNOTE) contact.note = r.ZNOTE;

      for (const p of phoneStmt.all(r.Z_PK)) {
        const num = p.ZFULLNUMBER.trim();
        const digits = num.replace(/\D/g, '').slice(-10);
        if (!contact._seenPhones.has(digits)) {
          contact._seenPhones.add(digits);
          contact.phones.push({ number: num, label: cleanLabel(p.ZLABEL) });
        }
      }

      for (const e of emailStmt.all(r.Z_PK)) {
        const addr = e.ZADDRESS.toLowerCase();
        if (!contact._seenEmails.has(addr)) {
          contact._seenEmails.add(addr);
          contact.emails.push({ address: e.ZADDRESS, label: cleanLabel(e.ZLABEL) });
        }
      }

      for (const rel of relStmt.all(r.Z_PK)) {
        const relKey = `${rel.ZNAME.toLowerCase()}_${cleanLabel(rel.ZLABEL)}`;
        if (!contact._seenRels.has(relKey)) {
          contact._seenRels.add(relKey);
          contact.relationships.push({ name: rel.ZNAME, type: cleanLabel(rel.ZLABEL) });
        }
      }

      try {
        for (const a of addrStmt.all(r.Z_PK)) {
          const parts = [a.ZSTREET, a.ZCITY, a.ZSTATE, a.ZZIPCODE, a.ZCOUNTRYNAME].filter(Boolean);
          if (parts.length) {
            contact.addresses.push({ full: parts.join(', '), label: cleanLabel(a.ZLABEL) });
          }
        }
      } catch (_) {}
    }

    db.close();
  } catch (e) {
    console.warn(`Skipped ${dbPath}: ${e.message}`);
  }
}

// Strip internal tracking sets, filter to contacts with at least phone or email
const contacts = [];
for (const c of mergeMap.values()) {
  delete c._seenPhones;
  delete c._seenEmails;
  delete c._seenRels;
  if (c.phones.length || c.emails.length) contacts.push(c);
}

// Output path relative to this script (runtime/scripts/ → runtime/contacts-cache.json)
const outPath = path.join(__dirname, '..', 'contacts-cache.json');
fs.writeFileSync(outPath, JSON.stringify({
  exportedAt: new Date().toISOString(),
  count: contacts.length,
  contacts,
}, null, 2));

console.log(`✓ Exported ${contacts.length} contacts → contacts-cache.json`);
console.log('  This file is local-only and excluded from version control.');
