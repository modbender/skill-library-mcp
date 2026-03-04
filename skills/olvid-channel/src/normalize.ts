import {OlvidClient} from "@olvid/bot-node";

export function normalizeOlvidMessagingTarget(raw: string): string | undefined {
  const trimmed = raw.trim().toLowerCase();
  if (!trimmed) {
    return undefined;
  }
  let normalized = trimmed;

  if (normalized.startsWith("olvid:")) {
    normalized = normalized.slice("olvid:".length).trim();
  }

  if (!normalized) {
    return undefined;
  }

  return `olvid:${normalized}`.toLowerCase();
}

export function looksLikeOlvidTargetId(target: string): boolean {
  target = target.trim().toLowerCase();
  if (!target) {
    return false;
  }
  if (target.startsWith("olvid:")) {
    target = target.slice("olvid:".length);
  }
  return /^discussion:(\d+)$/.test(target) || /^group:(\d+)$/.test(target) || /^contact:(\d+)$/.test(target);
}

export async function getDiscussionIdFromTarget(client: OlvidClient, target: string): Promise<bigint> {
  target = target.trim().toLowerCase();
  if (target.startsWith("olvid:")) {
    target = target.slice("olvid:".length).trim();
  }

  // discussion
  if (/^discussion:(\d+)$/.test(target)) {
    return BigInt(target.slice("discussion:".length));
  }
  // group
  if (/^group:(\d+)$/.test(target)) {
    const id = BigInt(target.slice("group:".length));
    return (await client.discussionGetByGroup({groupId: id})).id;
  }
  // contact
  if (/^contact:(\d+)$/.test(target)) {
    const id = BigInt(target.slice("contact:".length));
    return (await client.discussionGetByContact({contactId: id})).id;
  }
  throw new Error(`Invalid discussion target: ${target}`);
}

export function getContactIdFromTarget(target: string): bigint {
  target = target.trim().toLowerCase();
  if (target.startsWith("olvid:")) {
    target = target.slice("olvid:".length).trim();
  }
  if (/^contact:(\d+)$/.test(target)) {
    target = target.slice("contact:".length).trim();
    return BigInt(target);
  }
  throw new Error(`Invalid group target: ${target}`);
}

export function getGroupIdFromTarget(target: string): bigint {
  target = target.trim().toLowerCase();
  if (target.startsWith("olvid:")) {
    target = target.slice("olvid:".length).trim();
  }
  if (/^group:(\d+)$/.test(target)) {
    return BigInt(target.slice("group:".length).trim());
  }
  throw new Error(`Invalid group target: ${target}`);
}
