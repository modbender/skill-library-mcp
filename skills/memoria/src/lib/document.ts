import matter from 'gray-matter';
import type { MemDocument } from '../types.js';

export function parseDocument(
  raw: string,
  filePath: string,
  category: string,
): MemDocument {
  const { data, content } = matter(raw);
  const id = filePath.replace(/\.md$/, '');
  const tags: string[] = Array.isArray(data.tags) ? data.tags : [];
  const now = new Date().toISOString();

  return {
    id,
    path: filePath,
    category,
    title: (data.title as string) || id.split('/').pop() || id,
    content: content.trim(),
    frontmatter: data,
    tags,
    created: (data.created as string) || now,
    updated: (data.updated as string) || now,
  };
}

export function serializeDocument(doc: {
  title: string;
  content: string;
  frontmatter?: Record<string, unknown>;
  tags?: string[];
  type?: string;
}): string {
  const fm: Record<string, unknown> = {
    title: doc.title,
    ...doc.frontmatter,
  };
  if (doc.type) fm.type = doc.type;
  if (doc.tags && doc.tags.length > 0) fm.tags = doc.tags;

  const now = new Date().toISOString();
  if (!fm.created) fm.created = now;
  fm.updated = now;

  return matter.stringify(doc.content || '', fm);
}

export function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}
