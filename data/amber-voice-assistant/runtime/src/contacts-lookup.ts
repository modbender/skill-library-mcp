/**
 * Apple Contacts Lookup
 *
 * Queries the local Apple Contacts (AddressBook) SQLite databases
 * to resolve contact names to phone numbers.
 *
 * Searches across all iCloud-synced source databases for maximum coverage.
 *
 * SECURITY NOTE: All SQL queries use parameterized statements via better-sqlite3.
 * No user input is ever interpolated into SQL strings. The sqlite3 CLI is not used.
 */

import Database from 'better-sqlite3';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

interface ContactResult {
  firstName: string | null;
  lastName: string | null;
  fullName: string;
  phone: string;
  label: string | null;
}

/**
 * Find all AddressBook SQLite databases (main + sources).
 */
function findAddressBookDbs(): string[] {
  const baseDir = path.join(os.homedir(), 'Library', 'Application Support', 'AddressBook');
  const dbs: string[] = [];

  const mainDb = path.join(baseDir, 'AddressBook-v22.abcddb');
  if (fs.existsSync(mainDb)) dbs.push(mainDb);

  const sourcesDir = path.join(baseDir, 'Sources');
  if (fs.existsSync(sourcesDir)) {
    for (const source of fs.readdirSync(sourcesDir)) {
      const sourceDb = path.join(sourcesDir, source, 'AddressBook-v22.abcddb');
      if (fs.existsSync(sourceDb)) dbs.push(sourceDb);
    }
  }

  return dbs;
}

/**
 * Normalize a phone number to E.164-ish format for comparison.
 */
function normalizePhone(phone: string): string {
  const digits = phone.replace(/[^\d+]/g, '');
  if (digits.length === 11 && digits.startsWith('1')) return '+' + digits;
  if (digits.length === 10) return '+1' + digits;
  if (digits.startsWith('+')) return digits;
  return digits;
}

/**
 * Search contacts by name (fuzzy, case-insensitive).
 *
 * Uses parameterized LIKE queries — no string interpolation in SQL.
 */
export function searchByName(query: string): ContactResult[] {
  const dbs = findAddressBookDbs();
  const results: ContactResult[] = [];
  const seen = new Set<string>();

  const trimmed = query.trim();
  if (!trimmed) return [];

  // Parameterized LIKE value — percent signs are part of the bound value, not SQL
  const likeParam = `%${trimmed}%`;

  for (const db of dbs) {
    let conn: InstanceType<typeof Database> | null = null;
    try {
      conn = new Database(db, { readonly: true, fileMustExist: true });

      // All user input is passed as bound parameters — never interpolated into SQL
      const stmt = conn.prepare(`
        SELECT r.ZFIRSTNAME, r.ZLASTNAME, p.ZFULLNUMBER, p.ZLABEL
        FROM ZABCDRECORD r
        JOIN ZABCDPHONENUMBER p ON p.ZOWNER = r.Z_PK
        WHERE (
          r.ZFIRSTNAME LIKE ? COLLATE NOCASE
          OR r.ZLASTNAME LIKE ? COLLATE NOCASE
          OR (r.ZFIRSTNAME || ' ' || r.ZLASTNAME) LIKE ? COLLATE NOCASE
          OR r.ZNICKNAME LIKE ? COLLATE NOCASE
          OR r.ZORGANIZATION LIKE ? COLLATE NOCASE
        )
        AND p.ZFULLNUMBER IS NOT NULL
      `);

      const rows = stmt.all(likeParam, likeParam, likeParam, likeParam, likeParam) as any[];

      for (const row of rows) {
        const firstName = row.ZFIRSTNAME || null;
        const lastName = row.ZLASTNAME || null;
        const phone = (row.ZFULLNUMBER || '').trim();
        const label = row.ZLABEL || null;
        if (!phone) continue;

        const normalized = normalizePhone(phone);
        const dedupeKey = `${(firstName || '').toLowerCase()}_${(lastName || '').toLowerCase()}_${normalized}`;
        if (seen.has(dedupeKey)) continue;
        seen.add(dedupeKey);

        results.push({
          firstName,
          lastName,
          fullName: [firstName, lastName].filter(Boolean).join(' ') || 'Unknown',
          phone,
          label,
        });
      }
    } catch {
      // Skip databases that fail to open or query
    } finally {
      conn?.close();
    }
  }

  return results;
}

/**
 * Search contacts by phone number (last 10 digits, formatting-agnostic).
 *
 * Uses parameterized queries — no user input interpolated into SQL.
 */
export function searchByPhone(phone: string): ContactResult[] {
  const dbs = findAddressBookDbs();
  const results: ContactResult[] = [];
  const seen = new Set<string>();

  const digits = phone.replace(/\D/g, '');
  if (digits.length < 7) return [];

  // Match against last 10 digits to handle country code variations
  const searchDigits = digits.slice(-10);
  const likeParam = `%${searchDigits}%`;

  for (const db of dbs) {
    let conn: InstanceType<typeof Database> | null = null;
    try {
      conn = new Database(db, { readonly: true, fileMustExist: true });

      // Strip formatting from stored numbers using SQLite REPLACE, then parameterized LIKE
      const stmt = conn.prepare(`
        SELECT r.ZFIRSTNAME, r.ZLASTNAME, p.ZFULLNUMBER, p.ZLABEL
        FROM ZABCDRECORD r
        JOIN ZABCDPHONENUMBER p ON p.ZOWNER = r.Z_PK
        WHERE REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
          p.ZFULLNUMBER, ' ', ''), '-', ''), '(', ''), ')', ''), '+', ''
        ) LIKE ?
        AND p.ZFULLNUMBER IS NOT NULL
      `);

      const rows = stmt.all(likeParam) as any[];

      for (const row of rows) {
        const firstName = row.ZFIRSTNAME || null;
        const lastName = row.ZLASTNAME || null;
        const foundPhone = (row.ZFULLNUMBER || '').trim();
        const label = row.ZLABEL || null;
        if (!foundPhone) continue;

        const fullName = [firstName, lastName].filter(Boolean).join(' ') || 'Unknown';
        const dedupeKey = `${fullName.toLowerCase()}_${normalizePhone(foundPhone)}`;
        if (seen.has(dedupeKey)) continue;
        seen.add(dedupeKey);

        results.push({ firstName, lastName, fullName, phone: foundPhone, label });
      }
    } catch {
      // Skip databases that fail
    } finally {
      conn?.close();
    }
  }

  return results;
}
