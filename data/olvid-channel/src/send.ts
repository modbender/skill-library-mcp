import {datatypes} from "@olvid/bot-node";
import { getDiscussionIdFromTarget } from "./normalize.js";
import { getOlvidRuntime } from "./runtime.js";
import {getOlvidClient, messageIdFromString, messageIdToString} from "./tools";

type OlvidSendOpts = {
  daemonUrl?: string;
  clientKey?: string;
  accountId?: string;
  replyTo?: string;
  mediaUrls?: string[];
};

/*
** send a message in Olvid Channel
** As a native channel this method expects a message body and optional media Url as the agent can answer to the user request with some medias.
 */
export async function sendMessageOlvid(
  to: string,
  text: string,
  opts: OlvidSendOpts = {},
): Promise<datatypes.Message> {
  const runtime = getOlvidRuntime();
  const logger = runtime.logging.getChildLogger({module: "olvid"});

  if (!text?.trim() && !opts.mediaUrls) {
    throw new Error("Message must be non-empty for Olvid");
  }

  let olvidClient = getOlvidClient(opts.accountId);

  let discussionId: bigint|undefined = (await getDiscussionIdFromTarget(olvidClient, to))!;
  if (!discussionId) {
    throw new Error(`Cannot parse discussion id: ${to}`);
  }

  let sentMessage: datatypes.Message;
  if (opts.mediaUrls) {
    let ret = await olvidClient.messageSendWithAttachmentsFiles({ discussionId, body: text, replyId: opts.replyTo ? messageIdFromString(opts.replyTo) : undefined, filesPath: opts.mediaUrls });
    sentMessage = ret.message;
  } else {
    sentMessage = await olvidClient.messageSend({ discussionId, body: text, replyId: opts.replyTo ? messageIdFromString(opts.replyTo) : undefined });
  }

  logger.info(`message sent: ${messageIdToString(sentMessage.id)}`);

  getOlvidRuntime().channel.activity.record({
    channel: "olvid",
    accountId: opts.accountId,
    direction: "outbound",
  });

  olvidClient.stop();

  return sentMessage;
}
