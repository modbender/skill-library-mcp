import { z } from 'zod';

export const CANONICAL_STAGE_KEYS = [
  'stage:backlog',
  'stage:blocked',
  'stage:in-progress',
  'stage:in-review',
] as const;

export const StageKeySchema = z.enum(CANONICAL_STAGE_KEYS);
export type StageKey = z.infer<typeof StageKeySchema>;

function slug(input: string): string {
  return input
    .trim()
    .toLowerCase()
    .replace(/^stage[:/]/, '')
    .replaceAll('_', '-')
    .replaceAll(' ', '-')
    .replaceAll(/-+/g, '-');
}

export class Stage {
  readonly key: StageKey;

  private constructor(key: StageKey) {
    this.key = key;
  }

  static fromAny(value: string): Stage {
    const trimmed = value.trim();
    const lower = trimmed.toLowerCase();

    const key = lower.startsWith('stage:') || lower.startsWith('stage/')
      ? (`stage:${slug(trimmed)}` as const)
      : (`stage:${slug(trimmed)}` as const);

    const parsed = StageKeySchema.safeParse(key);
    if (!parsed.success) {
      throw new Error(`Unknown stage: ${JSON.stringify(value)}`);
    }

    return new Stage(parsed.data);
  }

  toString(): string {
    return this.key;
  }
}

export const StageSchema = z
  .object({
    key: StageKeySchema,
  })
  .transform((obj) => new Stage(obj.key));
