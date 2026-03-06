export type NextSelectionResult =
  | { kind: 'none' }
  | { kind: 'selected'; id: string };

/**
 * Platform-agnostic selection rules for `next`.
 */
export function selectNextFromStages(opts: {
  inProgressIds: readonly string[];
  backlogOrderedIds: readonly string[];
}): NextSelectionResult {
  if (opts.inProgressIds.length > 0) {
    throw new Error(
      `Refusing to pick next: found ${opts.inProgressIds.length} in-progress item(s): ${opts.inProgressIds.join(', ')}`,
    );
  }

  const first = opts.backlogOrderedIds[0];
  if (!first) return { kind: 'none' };

  return { kind: 'selected', id: first };
}
