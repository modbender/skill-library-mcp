#!/usr/bin/env node

import process from 'node:process';

function parseArgs(argv) {
  const out = {};
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--plate') out.plate = argv[++i];
    else if (a === '--type') out.type = argv[++i];
    else if (a === '--phone') out.phone = argv[++i];
  }
  return out;
}

function normalizePlate(s = '') {
  return String(s).toUpperCase().replace(/[\-.\s]/g, '');
}

function mapType(t = '') {
  const x = String(t).toLowerCase();
  if (x === 'oto') return 1;
  if (x === 'xemay') return 2;
  if (x === 'xemaydien') return 3;
  return null;
}

function usage() {
  console.error('Usage: node scripts/check_vnetraffic.mjs --plate <BIENSO> --type <oto|xemay|xemaydien> [--phone <SODT>]');
}

async function main() {
  const { plate, type, phone } = parseArgs(process.argv);
  const typeCode = mapType(type);
  if (!plate || !typeCode) {
    usage();
    process.exit(2);
  }

  const payload = {
    type: typeCode,
    bsx: normalizePlate(plate),
    sdt: phone || '0900000000',
  };

  const url = 'https://vnetraffic.org/wp-json/custom/v1/tra-cuu-csgt';
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    console.error(JSON.stringify({ ok: false, status: res.status, statusText: res.statusText }, null, 2));
    process.exit(1);
  }

  const data = await res.json();

  const summary = {
    ok: true,
    source: 'vnetraffic.org (intermediate source, cross-check with official portals)',
    input: { plateRaw: plate, plateNormalized: payload.bsx, type, typeCode },
    updated_at: data.updated_at || null,
    code: data.code ?? null,
    message: data.message || null,
    totalViolations: data.totalViolations ?? 0,
    unhandledCount: data.unhandledCount ?? 0,
    handledCount: data.handledCount ?? 0,
    violations: data.violations ?? [],
    raw: data,
  };

  console.log(JSON.stringify(summary, null, 2));
}

main().catch((err) => {
  console.error(JSON.stringify({ ok: false, error: String(err?.message || err) }, null, 2));
  process.exit(1);
});
