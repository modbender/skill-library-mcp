import { mkdir, readFile, writeFile, readdir, stat, unlink } from 'node:fs/promises';
import { join, relative, extname, dirname } from 'node:path';
import { readConfig, writeConfig, configExists } from './config.js';
import { parseDocument, serializeDocument, slugify } from './document.js';
import { DEFAULT_CATEGORIES } from '../types.js';
import type { VaultConfig, MemDocument, StoreOptions } from '../types.js';

export async function initVault(
  vaultPath: string,
  name: string,
  categories?: string[],
): Promise<VaultConfig> {
  const cats = categories || DEFAULT_CATEGORIES;

  await mkdir(vaultPath, { recursive: true });

  for (const cat of cats) {
    await mkdir(join(vaultPath, cat), { recursive: true });
  }
  await mkdir(join(vaultPath, 'sessions', 'handoffs'), { recursive: true });

  const config: VaultConfig = {
    path: vaultPath,
    name,
    categories: cats,
  };

  await writeConfig(config);
  return config;
}

export async function resolveVault(startPath?: string): Promise<VaultConfig> {
  const searchPath = startPath || process.cwd();

  if (await configExists(searchPath)) {
    return readConfig(searchPath);
  }

  const envPath = process.env.MEMORIA_VAULT;
  if (envPath && (await configExists(envPath))) {
    return readConfig(envPath);
  }

  throw new Error(
    `No Memoria vault found at "${searchPath}". Run "memoria init" first or set MEMORIA_VAULT.`,
  );
}

export async function storeDocument(
  vaultPath: string,
  options: StoreOptions,
): Promise<MemDocument> {
  const slug = slugify(options.title);
  const filePath = join(vaultPath, options.category, `${slug}.md`);
  const relPath = relative(vaultPath, filePath);

  if (!options.overwrite) {
    let exists = false;
    try {
      await stat(filePath);
      exists = true;
    } catch {
      // file does not exist, safe to write
    }
    if (exists) {
      throw new Error(`Document already exists: ${relPath}. Use --overwrite to replace.`);
    }
  }

  const raw = serializeDocument({
    title: options.title,
    content: options.content,
    frontmatter: options.frontmatter,
    tags: options.frontmatter?.tags as string[] | undefined,
  });

  await mkdir(dirname(filePath), { recursive: true });
  await writeFile(filePath, raw, 'utf-8');

  return parseDocument(raw, relPath, options.category);
}

export async function getDocument(
  vaultPath: string,
  id: string,
): Promise<MemDocument> {
  let filePath = join(vaultPath, id);
  if (extname(filePath) !== '.md') filePath += '.md';

  const raw = await readFile(filePath, 'utf-8');
  const parts = relative(vaultPath, filePath).split('/');
  const category = parts.length > 1 ? parts[0] : 'inbox';

  return parseDocument(raw, relative(vaultPath, filePath), category);
}

export async function listDocuments(
  vaultPath: string,
  category?: string,
): Promise<MemDocument[]> {
  const config = await readConfig(vaultPath);
  const categories = category ? [category] : config.categories;
  const docs: MemDocument[] = [];

  for (const cat of categories) {
    const catDir = join(vaultPath, cat);
    let entries: string[];
    try {
      entries = await readdir(catDir);
    } catch {
      continue;
    }

    for (const entry of entries) {
      if (!entry.endsWith('.md')) continue;
      const filePath = join(catDir, entry);
      try {
        const raw = await readFile(filePath, 'utf-8');
        docs.push(parseDocument(raw, relative(vaultPath, filePath), cat));
      } catch {
        continue;
      }
    }
  }

  return docs;
}

export async function deleteDocument(
  vaultPath: string,
  id: string,
): Promise<void> {
  let filePath = join(vaultPath, id);
  if (extname(filePath) !== '.md') filePath += '.md';
  await unlink(filePath);
}
