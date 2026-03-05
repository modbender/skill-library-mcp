/**
 * Shared OpenSoul URLs — single source of truth for the app base URL.
 */

export const OPENSOUL_APP_URL = "https://opensoul.cloud";

/** Full URL to view a soul in the app (e.g. https://opensoul.cloud/soul/{id}) */
export function soulUrl(soulId: string): string {
  return `${OPENSOUL_APP_URL}/soul/${soulId}`;
}
