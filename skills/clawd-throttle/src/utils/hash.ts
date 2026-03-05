import { createHash } from 'node:crypto';

export function hashPrompt(text: string): string {
  return createHash('sha256').update(text, 'utf-8').digest('hex');
}
