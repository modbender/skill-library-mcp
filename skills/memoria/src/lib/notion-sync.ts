import type { Client } from '@notionhq/client';
import type { MemDocument, SyncState, VaultConfig } from '../types.js';
import { listDocuments } from './vault.js';
import { readSyncState, writeSyncState, getEntry, setEntry } from './sync-state.js';
import {
  createCategoryDatabase,
  createNotionPage,
  updateNotionPage,
  replacePageContent,
  queryDatabase,
  getPageBlocks,
} from './notion-client.js';
import { markdownToBlocks, blocksToMarkdown } from './notion-converter.js';
import { parseDocument, serializeDocument } from './document.js';
import { writeFile, readFile } from 'node:fs/promises';
import { join } from 'node:path';
import matter from 'gray-matter';

export interface SyncReport {
  pushed: string[];
  pulled: string[];
  conflicts: string[];
  errors: string[];
}

export async function ensureDatabases(
  client: Client,
  config: VaultConfig,
  state: SyncState,
): Promise<SyncState> {
  const rootPageId = config.notion!.rootPageId;

  for (const category of config.categories) {
    if (state.databases[category]) continue;

    try {
      const db = await createCategoryDatabase(client, rootPageId, category);
      state.databases[category] = db.id;
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      if (!msg.includes('already exists')) {
        throw err;
      }
    }
  }

  return state;
}

export async function pushToNotion(
  client: Client,
  config: VaultConfig,
  options: { dryRun?: boolean } = {},
): Promise<SyncReport> {
  const report: SyncReport = { pushed: [], pulled: [], conflicts: [], errors: [] };
  const state = await readSyncState(config.path);
  await ensureDatabases(client, config, state);

  const docs = await listDocuments(config.path);

  for (const doc of docs) {
    const dbId = state.databases[doc.category];
    if (!dbId) {
      report.errors.push(`${doc.path}: no Notion database for category "${doc.category}"`);
      continue;
    }

    const existing = getEntry(state, doc.path);
    const blocks = markdownToBlocks(doc.content);

    try {
      if (existing) {
        if (doc.updated <= existing.localUpdatedAt) continue;

        if (!options.dryRun) {
          await updateNotionPage(client, existing.notionPageId, {
            title: doc.title,
            type: doc.frontmatter.type as string | undefined,
            tags: doc.tags,
            updated: doc.updated,
          });
          await replacePageContent(client, existing.notionPageId, blocks);
        }

        setEntry(state, doc.path, {
          ...existing,
          localUpdatedAt: doc.updated,
          lastSyncedAt: new Date().toISOString(),
        });
      } else {
        if (!options.dryRun) {
          const page = await createNotionPage(client, dbId, doc.title, {
            type: doc.frontmatter.type as string | undefined,
            tags: doc.tags,
            created: doc.created,
            updated: doc.updated,
          }, blocks);

          setEntry(state, doc.path, {
            localPath: doc.path,
            notionPageId: page.id,
            lastSyncedAt: new Date().toISOString(),
            localUpdatedAt: doc.updated,
            notionUpdatedAt: new Date().toISOString(),
          });
        }
      }

      report.pushed.push(doc.path);
    } catch (err) {
      report.errors.push(`${doc.path}: ${err instanceof Error ? err.message : String(err)}`);
    }
  }

  if (!options.dryRun) {
    state.lastSyncAt = new Date().toISOString();
    await writeSyncState(config.path, state);
  }

  return report;
}

export async function pullFromNotion(
  client: Client,
  config: VaultConfig,
  options: { preferNotion?: boolean; dryRun?: boolean } = {},
): Promise<SyncReport> {
  const report: SyncReport = { pushed: [], pulled: [], conflicts: [], errors: [] };
  const state = await readSyncState(config.path);
  await ensureDatabases(client, config, state);

  for (const [category, dbId] of Object.entries(state.databases)) {
    try {
      const response = await queryDatabase(client, dbId, state.lastSyncAt || undefined);

      for (const page of response.results) {
        const pageAny = page as Record<string, unknown>;
        const pageId = pageAny.id as string;
        const lastEdited = pageAny.last_edited_time as string;

        const props = pageAny.properties as Record<string, unknown>;
        const titleProp = props.Title as Record<string, unknown>;
        const titleArr = titleProp?.title as Array<{ plain_text: string }> | undefined;
        const title = titleArr?.[0]?.plain_text || 'untitled';

        const typeProp = props.Type as Record<string, unknown> | undefined;
        const typeSelect = typeProp?.select as Record<string, string> | undefined;
        const type = typeSelect?.name;

        const tagsProp = props.Tags as Record<string, unknown> | undefined;
        const tagsArr = tagsProp?.multi_select as Array<{ name: string }> | undefined;
        const tags = tagsArr?.map((t) => t.name) || [];

        const existingEntry = Object.values(state.entries).find(
          (e) => e.notionPageId === pageId,
        );

        if (existingEntry) {
          const localPath = join(config.path, existingEntry.localPath);
          let localRaw: string;
          try {
            localRaw = await readFile(localPath, 'utf-8');
          } catch {
            localRaw = '';
          }

          if (localRaw) {
            const localDoc = parseDocument(localRaw, existingEntry.localPath, category);
            if (localDoc.updated > existingEntry.localUpdatedAt && !options.preferNotion) {
              report.conflicts.push(existingEntry.localPath);
              continue;
            }
          }

          if (!options.dryRun) {
            const blocks = await getPageBlocks(client, pageId);
            const content = blocksToMarkdown(blocks);
            const fm: Record<string, unknown> = { title };
            if (type) fm.type = type;
            if (tags.length > 0) fm.tags = tags;

            const raw = serializeDocument({ title, content, frontmatter: fm, tags });
            await writeFile(localPath, raw, 'utf-8');

            setEntry(state, existingEntry.localPath, {
              ...existingEntry,
              lastSyncedAt: new Date().toISOString(),
              notionUpdatedAt: lastEdited,
              localUpdatedAt: new Date().toISOString(),
            });
          }

          report.pulled.push(existingEntry.localPath);
        } else {
          const slug = title
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/^-|-$/g, '');
          const relPath = `${category}/${slug}.md`;
          const filePath = join(config.path, relPath);

          if (!options.dryRun) {
            const blocks = await getPageBlocks(client, pageId);
            const content = blocksToMarkdown(blocks);
            const fm: Record<string, unknown> = { title };
            if (type) fm.type = type;
            if (tags.length > 0) fm.tags = tags;

            const raw = serializeDocument({ title, content, frontmatter: fm, tags });
            await writeFile(filePath, raw, 'utf-8');

            setEntry(state, relPath, {
              localPath: relPath,
              notionPageId: pageId,
              lastSyncedAt: new Date().toISOString(),
              localUpdatedAt: new Date().toISOString(),
              notionUpdatedAt: lastEdited,
            });
          }

          report.pulled.push(relPath);
        }
      }
    } catch (err) {
      report.errors.push(`${category}: ${err instanceof Error ? err.message : String(err)}`);
    }
  }

  if (!options.dryRun) {
    state.lastSyncAt = new Date().toISOString();
    await writeSyncState(config.path, state);
  }

  return report;
}
