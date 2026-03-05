// SPDX-License-Identifier: MIT
/**
 * Build clickable Logfire trace URLs.
 *
 * Format: {projectUrl}/explore?traceId={traceId}
 */
export function buildLogfireTraceUrl(
  projectUrl: string,
  traceId: string,
  spanId?: string,
): string {
  const base = projectUrl.replace(/\/$/, '');
  const params = new URLSearchParams({ traceId });
  if (spanId) params.set('spanId', spanId);
  return `${base}/explore?${params.toString()}`;
}
