import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { Client } from '@notionhq/client';
import ignore from 'ignore';
import chalk from 'chalk';
import type { NotionSyncConfig } from './types.js';

function md5(content: string): string {
  return crypto.createHash('md5').update(content).digest('hex');
}

function buildIgnore(patterns: string[]) {
  const ig = ignore();
  ig.add(patterns);
  // also respect .gitignore if present
  return ig;
}

function getFiles(dir: string, ig: ReturnType<typeof ignore>, base = dir): string[] {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  const files: string[] = [];
  for (const entry of entries) {
    const rel = path.relative(base, path.join(dir, entry.name));
    if (ig.ignores(rel)) continue;
    if (entry.isDirectory()) {
      files.push(...getFiles(path.join(dir, entry.name), ig, base));
    } else {
      files.push(rel);
    }
  }
  return files;
}

async function getOrCreatePage(
  client: Client,
  parentId: string,
  title: string,
  existingPages: Map<string, string>
): Promise<string> {
  if (existingPages.has(title)) return existingPages.get(title)!;

  const res = await client.pages.create({
    parent: { page_id: parentId },
    icon: { type: 'emoji', emoji: '📄' },
    properties: {
      title: { title: [{ text: { content: title } }] }
    }
  });
  existingPages.set(title, res.id);
  return res.id;
}

async function getOrCreateFolder(
  client: Client,
  parentId: string,
  name: string,
  existingPages: Map<string, string>
): Promise<string> {
  if (existingPages.has(name)) return existingPages.get(name)!;

  const res = await client.pages.create({
    parent: { page_id: parentId },
    icon: { type: 'emoji', emoji: '📁' },
    properties: {
      title: { title: [{ text: { content: name } }] }
    }
  });
  existingPages.set(name, res.id);
  return res.id;
}

async function listChildPages(client: Client, pageId: string): Promise<Map<string, string>> {
  const map = new Map<string, string>();
  try {
    const res = await client.blocks.children.list({ block_id: pageId });
    for (const block of res.results) {
      if ('type' in block && block.type === 'child_page') {
        map.set((block as any).child_page.title, block.id);
      }
    }
  } catch {}
  return map;
}

async function upsertFilePage(
  client: Client,
  parentId: string,
  filename: string,
  content: string,
  existingPages: Map<string, string>
): Promise<void> {
  const MAX = 1800;
  const chunks = [];
  for (let i = 0; i < content.length; i += MAX) {
    chunks.push(content.slice(i, i + MAX));
  }

  const blocks = chunks.map(chunk => ({
    object: 'block' as const,
    type: 'paragraph' as const,
    paragraph: { rich_text: [{ text: { content: chunk } }] }
  }));

  if (existingPages.has(filename)) {
    const pageId = existingPages.get(filename)!;
    // clear existing blocks
    const existing = await client.blocks.children.list({ block_id: pageId });
    for (const b of existing.results) {
      await client.blocks.delete({ block_id: b.id });
    }
    if (blocks.length > 0) {
      await client.blocks.children.append({ block_id: pageId, children: blocks });
    }
  } else {
    const page = await client.pages.create({
      parent: { page_id: parentId },
      icon: { type: 'emoji', emoji: '📄' },
      properties: {
        title: { title: [{ text: { content: filename } }] }
      },
      children: blocks
    });
    existingPages.set(filename, page.id);
  }
}

export async function syncWorkspace(
  config: NotionSyncConfig,
  options: { dryRun?: boolean; diffOnly?: boolean } = {}
): Promise<{ pushed: string[]; skipped: string[]; errors: string[] }> {
  const client = new Client({ auth: config.notion.token });
  const ig = buildIgnore(config.ignore);
  const files = getFiles(config.path, ig);
  const pushed: string[] = [];
  const skipped: string[] = [];
  const errors: string[] = [];

  // Build folder page cache from root
  const rootChildren = await listChildPages(client, config.notion.rootPageId);
  const folderCache = new Map<string, { id: string; children: Map<string, string> }>();

  for (const relPath of files) {
    const absPath = path.join(config.path, relPath);
    let content: string;
    try {
      content = fs.readFileSync(absPath, 'utf8');
    } catch {
      errors.push(`Cannot read: ${relPath}`);
      continue;
    }

    const checksum = md5(content);
    if (options.diffOnly && config.checksums[relPath] === checksum) {
      skipped.push(relPath);
      continue;
    }

    if (options.dryRun) {
      pushed.push(relPath);
      continue;
    }

    try {
      const parts = relPath.split(path.sep);
      const filename = parts.pop()!;

      let parentId = config.notion.rootPageId;
      let parentChildren = rootChildren;

      // Create folder hierarchy
      for (const folder of parts) {
        if (!folderCache.has(folder)) {
          const folderId = await getOrCreateFolder(client, parentId, folder, parentChildren);
          const children = await listChildPages(client, folderId);
          folderCache.set(folder, { id: folderId, children });
        }
        const cached = folderCache.get(folder)!;
        parentId = cached.id;
        parentChildren = cached.children;
      }

      await upsertFilePage(client, parentId, filename, content, parentChildren);
      config.checksums[relPath] = checksum;
      pushed.push(relPath);
    } catch (e: any) {
      errors.push(`${relPath}: ${e.message}`);
    }
  }

  return { pushed, skipped, errors };
}
