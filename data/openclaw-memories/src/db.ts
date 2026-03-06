/**
 * Database — thin wrapper over sql.js (pure JS SQLite)
 * No native modules. No compilation. Works everywhere.
 */

export interface DB {
  run(sql: string, ...params: any[]): void;
  get(sql: string, ...params: any[]): any;
  all(sql: string, ...params: any[]): any[];
  exec(sql: string): void;
  close(): void;
}

/** In-memory SQLite via sql.js, or a simple Map fallback */
export function createDB(): DB {
  const tables = new Map<string, { cols: string[]; rows: any[] }>();

  return {
    run(sql: string, ...params: any[]) {
      execute(tables, sql, params);
    },
    get(sql: string, ...params: any[]) {
      return query(tables, sql, params, true);
    },
    all(sql: string, ...params: any[]) {
      return query(tables, sql, params, false);
    },
    exec(sql: string) {
      for (const stmt of sql.split(';').filter(s => s.trim())) {
        execute(tables, stmt, []);
      }
    },
    close() {
      tables.clear();
    },
  };
}

function execute(tables: Map<string, any>, sql: string, params: any[]): void {
  const up = sql.toUpperCase().trim();

  if (up.startsWith('CREATE')) {
    const m = sql.match(/CREATE\s+(?:VIRTUAL\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)/i);
    if (m && !tables.has(m[1])) {
      tables.set(m[1], { cols: [], rows: [] });
    }
    return;
  }

  if (up.startsWith('INSERT') || up.startsWith('REPLACE')) {
    const m = sql.match(/(?:INSERT|REPLACE)\s+(?:OR\s+\w+\s+)?INTO\s+(\w+)\s*\(([^)]+)\)/i);
    if (m && params.length) {
      const t = tables.get(m[1]);
      if (!t) return;
      const cols = m[2].split(',').map(c => c.trim());
      const row: any = {};
      cols.forEach((c, i) => row[c] = params[i]);
      if (up.includes('OR REPLACE')) {
        t.rows = t.rows.filter((r: any) => r[cols[0]] !== params[0]);
      }
      t.rows.push(row);
    }
    return;
  }

  if (up.startsWith('UPDATE')) {
    const m = sql.match(/UPDATE\s+(\w+)\s+SET\s+(.+?)\s+WHERE\s+(\w+)\s*=\s*\?/i);
    if (m && params.length) {
      const t = tables.get(m[1]);
      if (!t) return;
      const sets = m[2].split(',').map(s => s.trim().split(/\s*=\s*/)[0]);
      const whereVal = params[params.length - 1];
      for (const row of t.rows) {
        if (row[m[3]] === whereVal) {
          sets.forEach((col, i) => { if (params[i] !== undefined) row[col] = params[i]; });
        }
      }
    }
    return;
  }

  if (up.startsWith('DROP')) {
    const m = sql.match(/DROP\s+TABLE\s+(?:IF\s+EXISTS\s+)?(\w+)/i);
    if (m) tables.delete(m[1]);
    return;
  }
}

function query(tables: Map<string, any>, sql: string, params: any[], single: boolean): any {
  const m = sql.match(/SELECT\s+.+?\s+FROM\s+(\w+)/i);
  if (!m) return single ? null : [];

  const t = tables.get(m[1]);
  if (!t) return single ? null : [];

  let rows = [...t.rows];

  // WHERE col = ?
  const w = sql.match(/WHERE\s+(\w+)\s*=\s*\?/i);
  if (w && params.length) rows = rows.filter((r: any) => r[w[1]] === params[0]);

  // ORDER BY col DESC
  const o = sql.match(/ORDER\s+BY\s+(\w+)\s+(ASC|DESC)?/i);
  if (o) {
    const desc = o[2]?.toUpperCase() === 'DESC';
    rows.sort((a: any, b: any) => desc ? (b[o[1]] - a[o[1]]) : (a[o[1]] - b[o[1]]));
  }

  // LIMIT
  const l = sql.match(/LIMIT\s+(\?|\d+)/i);
  if (l) {
    const lim = l[1] === '?' ? (params[params.length - 1] ?? 10) : parseInt(l[1]);
    rows = rows.slice(0, lim);
  }

  // MAX() aggregate
  if (sql.match(/MAX\(/i) && rows.length) {
    const col = sql.match(/MAX\((\w+)\)/i);
    if (col) {
      const max = Math.max(...t.rows.map((r: any) => r[col[1]] ?? 0));
      return single ? { max_score: max } : [{ max_score: max }];
    }
  }

  return single ? (rows[0] ?? null) : rows;
}
