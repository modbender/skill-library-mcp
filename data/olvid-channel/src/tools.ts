import {datatypes, OlvidClient} from "@olvid/bot-node";
import {getOlvidRuntime} from "./runtime";
import {ResolvedOlvidAccount, resolveOlvidAccount} from "./accounts";
import {CoreConfig} from "./types";

export function messageIdToString(messageId?: datatypes.MessageId): string {
  if (!messageId) {
    return "undefined";
  }
  return messageId.type === datatypes.MessageId_Type.INBOUND
    ? `I${messageId.id}`
    : `O${messageId.id}`;
}

export function messageIdFromString(messageId: string): datatypes.MessageId {
  let type: datatypes.MessageId_Type = datatypes.MessageId_Type.UNSPECIFIED;
  if (messageId.startsWith("I")) {
    type = datatypes.MessageId_Type.INBOUND;
  } else if (messageId.startsWith("O")) {
    type = datatypes.MessageId_Type.OUTBOUND;
  }
  let id: bigint = 0n;
  try {
    id = BigInt(messageId.slice(1));
  } catch (e) {}

  return new datatypes.MessageId({ type, id });
}

export function discussionIdToString(discussionId: BigInt) {
  return `olvid:discussion:${discussionId}`;
}
export function groupIdToString(groupId: BigInt) {
  return `olvid:group:${groupId}`;
}
export function contactIdToString(contactId: BigInt) {
  return `olvid:contact:${contactId}`;
}

export function getOlvidClient(olvidChannelAccountId?: string): OlvidClient {
  const runtime = getOlvidRuntime();
  const config = runtime.config.loadConfig();

  // Retrieve the configuration/credentials for the specific olvidChannelAccountId, or fallback to default
  let olvidAccount: ResolvedOlvidAccount = resolveOlvidAccount({cfg: config as CoreConfig, accountId: olvidChannelAccountId ?? "default"});
  if (!olvidAccount || !olvidAccount.daemonUrl || !olvidAccount.clientKey) {
    olvidAccount = resolveOlvidAccount({cfg: config as CoreConfig, accountId: "default"});
  }
  return new OlvidClient({clientKey: olvidAccount.clientKey, serverUrl: olvidAccount.daemonUrl});
}

export function stringifyDatatypesEntity(obj: any): string {
  const raw = obj.toJson()!;
  const payload = raw as Record<string, unknown>;
  if (obj instanceof datatypes.Group) {
    payload.id = `olvid:group:${obj.id}`;
  } else if (obj instanceof datatypes.Contact) {
    payload.id = `olvid:contact:${obj.id}`;
  } else if (obj instanceof datatypes.Discussion) {
    payload.id = `olvid:discussion:${obj.id}`;
  }
  return JSON.stringify(payload);
}