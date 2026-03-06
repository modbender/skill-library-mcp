#!/usr/bin/env node
/**
 * Dedup Sweep
 *
 * Finds near-duplicate facts using cosine similarity on BGE-M3 embeddings.
 * Groups facts by category, computes pairwise similarity, flags duplicates.
 *
 * Thresholds:
 *   >= 0.97  → auto-merge (deactivate lower-confidence fact, keep higher)
 *   >= 0.88  → flag for review (printed but not acted on without --auto)
 *
 * Usage:
 *   npx tsx src/storage/dedup-sweep.ts [options]
 *
 * Options:
 *   --db <path>      Path to conversations.sqlite (default: ~/.engram/conversations.sqlite)
 *   --threshold <n>  Review threshold (default: 0.88)
 *   --auto           Auto-merge pairs above 0.97 (without --auto, just reports)
 *   --dry-run        Report only, no DB writes even with --auto
 *   --cross-category Also check across categories (slower, more false positives)
 */

import { join } from 'node:path'
import { homedir } from 'node:os'
import { existsSync } from 'node:fs'
import Database from 'better-sqlite3'

const args = process.argv.slice(2)
function getArg(name: string): string | undefined {
  const idx = args.indexOf(`--${name}`)
  return idx >= 0 && idx + 1 < args.length ? args[idx + 1] : undefined
}
const dryRun = args.includes('--dry-run')
const autoMerge = args.includes('--auto')
const crossCategory = args.includes('--cross-category')
const reviewThreshold = parseFloat(getArg('threshold') ?? '0.88')
const autoThreshold = 0.97

const dbPath = getArg('db') ?? join(homedir(), '.engram', 'conversations.sqlite')
if (!existsSync(dbPath)) {
  console.error('❌ Database not found:', dbPath)
  process.exit(1)
}

function cosine(a: Float32Array, b: Float32Array): number {
  let dot = 0, normA = 0, normB = 0
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i]
    normA += a[i] * a[i]
    normB += b[i] * b[i]
  }
  const denom = Math.sqrt(normA) * Math.sqrt(normB)
  return denom === 0 ? 0 : dot / denom
}

function blobToFloat32(blob: Buffer): Float32Array {
  return new Float32Array(blob.buffer, blob.byteOffset, blob.byteLength / 4)
}

type FactRow = {
  id: string
  category: string
  summary: string
  confidence: number
  occurrence_count: number
  embedding: Buffer
}

async function main() {
  console.log('🔍 Memento — Dedup Sweep')
  console.log(`   DB: ${dbPath}`)
  console.log(`   Review threshold: ${reviewThreshold}`)
  console.log(`   Auto-merge threshold: ${autoThreshold} (${autoMerge ? 'ENABLED' : 'disabled'})`)
  console.log(`   Dry run: ${dryRun}`)
  console.log('')

  const db = new Database(dbPath)

  const facts: FactRow[] = db.prepare(`
    SELECT id, category, summary, confidence, occurrence_count, embedding
    FROM facts
    WHERE is_active = 1 AND embedding IS NOT NULL AND length(embedding) > 10
    ORDER BY category, confidence DESC
  `).all() as FactRow[]

  console.log(`   Loaded ${facts.length} active facts with embeddings`)
  console.log('')

  const byCategory = new Map<string, FactRow[]>()
  for (const f of facts) {
    const cat = crossCategory ? 'all' : f.category
    if (!byCategory.has(cat)) byCategory.set(cat, [])
    byCategory.get(cat)!.push(f)
  }

  type Pair = { a: FactRow; b: FactRow; sim: number }
  const autoMergePairs: Pair[] = []
  const reviewPairs: Pair[] = []

  for (const [_cat, group] of byCategory.entries()) {
    if (group.length < 2) continue
    const vecs = group.map(f => blobToFloat32(f.embedding))
    for (let i = 0; i < group.length; i++) {
      for (let j = i + 1; j < group.length; j++) {
        const sim = cosine(vecs[i], vecs[j])
        if (sim >= reviewThreshold) {
          const pair: Pair = { a: group[i], b: group[j], sim }
          if (sim >= autoThreshold) autoMergePairs.push(pair)
          else reviewPairs.push(pair)
        }
      }
    }
  }

  autoMergePairs.sort((a, b) => b.sim - a.sim)
  reviewPairs.sort((a, b) => b.sim - a.sim)

  console.log(`📊 Results:`)
  console.log(`   Auto-merge candidates (>= ${autoThreshold}): ${autoMergePairs.length}`)
  console.log(`   Review candidates (${reviewThreshold}–${autoThreshold}): ${reviewPairs.length}`)
  console.log('')

  if (autoMergePairs.length > 0) {
    console.log(`🔴 AUTO-MERGE CANDIDATES (sim >= ${autoThreshold}):`)
    for (const { a, b, sim } of autoMergePairs) {
      console.log(`\n  sim=${sim.toFixed(4)} [${a.category}]`)
      console.log(`  KEEP: [${a.id.slice(0,8)}] conf=${a.confidence.toFixed(2)} occ=${a.occurrence_count} "${a.summary.slice(0,80)}"`)
      console.log(`  DROP: [${b.id.slice(0,8)}] conf=${b.confidence.toFixed(2)} occ=${b.occurrence_count} "${b.summary.slice(0,80)}"`)
    }
    console.log('')
  }

  if (reviewPairs.length > 0) {
    console.log(`🟡 REVIEW CANDIDATES (sim ${reviewThreshold}–${autoThreshold}):`)
    const shown = reviewPairs.slice(0, 50)
    for (const { a, b, sim } of shown) {
      console.log(`\n  sim=${sim.toFixed(4)} [${a.category}]`)
      console.log(`  A: [${a.id.slice(0,8)}] "${a.summary.slice(0,80)}"`)
      console.log(`  B: [${b.id.slice(0,8)}] "${b.summary.slice(0,80)}"`)
    }
    if (reviewPairs.length > 50) {
      console.log(`\n  ... and ${reviewPairs.length - 50} more (use --threshold 0.92 to narrow)`)
    }
    console.log('')
  }

  if (autoMerge && autoMergePairs.length > 0) {
    if (dryRun) {
      console.log(`🔍 Dry run — would deactivate ${autoMergePairs.length} duplicate facts`)
    } else {
      console.log(`⚡ Auto-merging ${autoMergePairs.length} pairs...`)
      const deactivate = db.prepare(`
        UPDATE facts SET is_active = 0,
          metadata = json_set(COALESCE(metadata, '{}'), '$.dedup_merged_into', ?)
        WHERE id = ? AND is_active = 1
      `)
      const tx = db.transaction((pairs: Pair[]) => {
        let merged = 0
        const seen = new Set<string>()
        for (const { a, b } of pairs) {
          if (seen.has(b.id)) continue
          deactivate.run(a.id, b.id)
          seen.add(b.id)
          merged++
        }
        return merged
      })
      const merged = tx(autoMergePairs)
      console.log(`✅ Deactivated ${merged} duplicate facts`)
    }
  } else if (!autoMerge && autoMergePairs.length > 0) {
    console.log(`💡 Run with --auto to deactivate ${autoMergePairs.length} near-exact duplicates`)
  }

  const finalCount = db.prepare('SELECT COUNT(*) as n FROM facts WHERE is_active=1').get() as { n: number }
  console.log(`\n📈 Active facts after sweep: ${finalCount.n}`)

  db.close()
}

main().catch(err => {
  console.error('Fatal:', err)
  process.exit(1)
})
