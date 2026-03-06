/**
 * ALMA — Algorithm Learning via Meta-learning Agents
 * Evolves memory system designs through mutation + evaluation.
 */

import { randomUUID } from 'crypto';
import { createDB, DB } from './db';

// --- Types ---

export interface DesignParams { [key: string]: number | string | boolean }

export interface Design {
  id: string;
  createdAt: Date;
  params: DesignParams;
  score: number;
  evals: number;
  isBest: boolean;
}

export interface Constraints {
  [key: string]: { min?: number; max?: number; type: 'number' | 'string' | 'boolean' };
}

export interface ALMAConfig {
  constraints?: Constraints;
  populationSize?: number;
  mutationRate?: number;
}

// --- Mutations ---

function gaussian(params: DesignParams, constraints: Constraints, std = 0.1): DesignParams {
  const out = { ...params };
  for (const [k, c] of Object.entries(constraints)) {
    if (c.type !== 'number') continue;
    const cur = (params[k] ?? 0) as number;
    const min = c.min ?? 0, max = c.max ?? 1;
    const u1 = Math.random(), u2 = Math.random();
    const z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
    out[k] = Math.max(min, Math.min(max, cur + z * std * (max - min)));
  }
  return out;
}

function anneal(params: DesignParams, constraints: Constraints, temp = 0.5): DesignParams {
  const out = { ...params };
  for (const [k, c] of Object.entries(constraints)) {
    if (c.type !== 'number') continue;
    const min = c.min ?? 0, max = c.max ?? 1;
    if (Math.random() < temp) {
      out[k] = Math.random() * (max - min) + min;
    } else {
      out[k] = (params[k] as number ?? 0) + (Math.random() - 0.5) * (1 - temp);
    }
  }
  return out;
}

// --- Agent ---

export class ALMAAgent {
  private db: DB;
  private constraints: Constraints;
  readonly populationSize: number;
  readonly mutationRate: number;

  constructor(config: ALMAConfig = {}) {
    this.db = createDB();
    this.constraints = config.constraints || {};
    this.populationSize = config.populationSize || 20;
    this.mutationRate = config.mutationRate || 0.3;
    this.initSchema();
  }

  private initSchema() {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS designs (
        design_id TEXT PRIMARY KEY,
        created_at TEXT NOT NULL,
        parameters TEXT NOT NULL,
        score REAL DEFAULT 0.0,
        evals INTEGER DEFAULT 0,
        is_best INTEGER DEFAULT 0
      )
    `);
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS evaluations (
        id INTEGER PRIMARY KEY,
        design_id TEXT NOT NULL,
        score REAL NOT NULL,
        metrics TEXT NOT NULL,
        ts TEXT DEFAULT ''
      )
    `);
  }

  propose(baseId?: string): Design {
    const id = randomUUID().slice(0, 8);
    const now = new Date();

    let params: DesignParams;
    if (baseId) {
      const row = this.db.get('SELECT parameters FROM designs WHERE design_id = ?', baseId);
      const base = row ? JSON.parse(row.parameters) : {};
      params = Math.random() < 0.5
        ? gaussian(base, this.constraints)
        : anneal(base, this.constraints, 0.2);
    } else {
      params = this.randomParams();
    }

    this.db.run(
      'INSERT INTO designs (design_id, created_at, parameters, score, evals, is_best) VALUES (?, ?, ?, ?, ?, ?)',
      id, now.toISOString(), JSON.stringify(params), 0, 0, 0
    );

    return { id, createdAt: now, params, score: 0, evals: 0, isBest: false };
  }

  evaluate(designId: string, metrics: Record<string, number>): number {
    const vals = Object.values(metrics);
    const score = vals.length ? vals.reduce((a, b) => a + b) / vals.length : 0;

    this.db.run(
      'INSERT INTO evaluations (design_id, score, metrics, ts) VALUES (?, ?, ?, ?)',
      designId, score, JSON.stringify(metrics), new Date().toISOString()
    );
    this.db.run('UPDATE designs SET score = ?, evals = evals + 1 WHERE design_id = ?', score, designId);

    // Mark best
    const best = this.db.get('SELECT MAX(score) as max_score FROM designs');
    if (best?.max_score === score) {
      this.db.run('UPDATE designs SET is_best = 0 WHERE is_best = ?', 1);
      this.db.run('UPDATE designs SET is_best = 1 WHERE design_id = ?', designId);
    }

    return score;
  }

  best(): Design | null {
    const row = this.db.get('SELECT * FROM designs WHERE is_best = 1');
    return row ? this.toDesign(row) : null;
  }

  top(k = 5): Design[] {
    return this.db.all('SELECT * FROM designs ORDER BY score DESC LIMIT ?', k).map(this.toDesign);
  }

  close() { this.db.close(); }

  private toDesign(row: any): Design {
    return {
      id: row.design_id,
      createdAt: new Date(row.created_at),
      params: JSON.parse(row.parameters),
      score: row.score,
      evals: row.evals,
      isBest: row.is_best === 1,
    };
  }

  private randomParams(): DesignParams {
    const p: DesignParams = {};
    for (const [k, c] of Object.entries(this.constraints)) {
      if (c.type === 'number') p[k] = Math.random() * ((c.max ?? 1) - (c.min ?? 0)) + (c.min ?? 0);
      else if (c.type === 'boolean') p[k] = Math.random() > 0.5;
    }
    return p;
  }
}
