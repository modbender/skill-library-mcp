import type {ChannelAccountSnapshot, RuntimeEnv, OpenClawConfig, ReplyPayload, ChannelLogSink} from "openclaw/plugin-sdk";
import { datatypes, OlvidClient } from "@olvid/bot-node";
import { ResolvedOlvidAccount, resolveOlvidAccount } from "./accounts.js";
import { getOlvidRuntime } from "./runtime.js";
import { sendMessageOlvid } from "./send.js";
import {contactIdToString, discussionIdToString, messageIdToString} from "./tools.js";
import { CoreConfig } from "./types.js";
import * as fs from "node:fs";

export type MonitorOlvidOpts = {
  accountId?: string;
  config?: CoreConfig;
  runtime?: RuntimeEnv;
  abortSignal?: AbortSignal;
  logger?: ChannelLogSink;
  statusSink?: (patch: Partial<ChannelAccountSnapshot>) => void;
};

class OpenClawBot extends OlvidClient {
  private readonly opts: MonitorOlvidOpts;
  private readonly account: ResolvedOlvidAccount;
  private readonly cfg: CoreConfig;
  private readonly logger?: ChannelLogSink;

  constructor(account: ResolvedOlvidAccount, opts: MonitorOlvidOpts, cfg: CoreConfig) {
    super({ serverUrl: account.daemonUrl, clientKey: account.clientKey });
    this.opts = opts;
    this.account = account;
    this.cfg = cfg;
    this.logger = opts.logger;

    this.onMessageReceived({
      callback: this.onMessageReceivedHandler,
    });
    this.startRoutine().then();
  }

  // list and handle unread messages (that arrived while bot was off)
  private async startRoutine(): Promise<void> {
    const runtime = getOlvidRuntime();
    runtime.config.loadConfig().agents

    let unreadMessageCount: number = 0;
    for await (let message of this.messageList({unread: true})) {
      await this.onMessageReceivedHandler(message);
      unreadMessageCount++;
    }
    if (unreadMessageCount) {
      this.logger?.info(`queued ${unreadMessageCount} pending message(s)`)
    }
  }

  private async onMessageReceivedHandler(message: datatypes.Message) {
    const runtime = getOlvidRuntime();

    // load metadata
    const discussion: datatypes.Discussion = await this.discussionGet({
      discussionId: message.discussionId,
    });
    const sender: datatypes.Contact | undefined = message.senderId
      ? await this.contactGet({ contactId: message.senderId })
      : undefined;
    const timestamp: number = Number(message.timestamp);
    const isGroup: boolean = await message.isGroupMessage(this);

    // ignore outbound messages (not supposed to happen)
    if (!sender) {
      return;
    }

    // log and update status
    this.logger?.info("message received")
    runtime.channel.activity.record({
      channel: "olvid",
      accountId: this.opts.accountId,
      direction: "inbound",
      at: timestamp,
    });
    this.opts.statusSink?.({ lastInboundAt: Date.now() });

    // download message attachments
    const attachmentsWithPaths: {attachment: datatypes.Attachment, path: string}[] = [];
    if (message.attachmentsCount > 0) {
      fs.mkdirSync("/tmp/olvid-attachments", {recursive: true});
      for await (const attachment of this.attachmentList({filter: new datatypes.AttachmentFilter({messageId: message.id})})) {
        attachmentsWithPaths.push({
          attachment: attachment,
          path: await attachment.save(this, "/tmp/olvid-attachments")
        })
      }
      this.logger?.info(`downloaded ${attachmentsWithPaths.length} attachment(s)`)
    }

    // get replied message
    const repliedMessage: datatypes.Message|undefined = message.repliedMessageId?.id ? await this.messageGet({messageId: message.repliedMessageId}) : undefined;
    let repliedMessageSenderId: BigInt|undefined = undefined;
    let repliedMessageSenderName: string|undefined = undefined;
    if (repliedMessage) {
      if (repliedMessage.senderId === 0n) {
        repliedMessageSenderName = "you";
        repliedMessageSenderId = 0n;
      } else {
        const repliedMessageContact: datatypes.Contact|undefined = repliedMessage && repliedMessage.senderId ? await repliedMessage.getSenderContact(this) : undefined;
        repliedMessageSenderId = repliedMessageContact?.id;
        repliedMessageSenderName = repliedMessageContact?.displayName;
      }
    }

    const route = runtime.channel.routing.resolveAgentRoute({
      cfg: this.cfg,
      channel: "olvid",
      accountId: this.account.accountId,
      peer: {
        id: discussionIdToString(discussion.id),
        kind: isGroup ? "group" : "dm",
      },
    });

    const body = runtime.channel.reply.formatInboundEnvelope({
      channel: "olvid",
      from: `olvid:contact:${message.senderId}`,
      body: message.body,
      timestamp: Number(message.timestamp),
      senderLabel: sender.displayName,
      sender: { name: sender.displayName, id: `olvid:contact:${sender.id.toString()}` },
    });

    const ctxPayload = runtime.channel.reply.finalizeInboundContext({
      Body: body,
      RawBody: message.body,
      CommandBody: message.body,
      From: contactIdToString(sender.id),
      To: discussionIdToString(discussion.id),
      SessionKey: route.sessionKey,
      AccountId: route.accountId,
      ChatType: discussion.isGroupDiscussion() ? "group" : "direct",
      ConversationLabel: discussion.title,
      SenderName: sender ? sender.displayName : "",
      SenderId: contactIdToString(sender.id),
      MessageId: messageIdToString(message.id!),
      Timestamp: message.timestamp,
      Provider: "olvid",
      Surface: "olvid",
      OriginatingChannel: "olvid",
      OriginatingTo: discussionIdToString(discussion.id),
      ReplyToId: messageIdToString(repliedMessage?.id),
      ReplyToBody: repliedMessage?.body,
      ReplyToSenderId: repliedMessageSenderId,
      ReplyToSenderName: repliedMessageSenderName,
      MediaPath: attachmentsWithPaths.length > 0 ? attachmentsWithPaths[0].path : undefined,
      MediaUrl: attachmentsWithPaths.length > 0 ? attachmentsWithPaths[0].path : undefined,
      MediaType: attachmentsWithPaths.length > 0 ? runtime.media.mediaKindFromMime(attachmentsWithPaths[0].attachment.mimeType) : undefined,
      MediaPaths: attachmentsWithPaths.length > 0 ? attachmentsWithPaths.map(awp => awp.path) : undefined,
      MediaUrls: attachmentsWithPaths.length > 0 ? attachmentsWithPaths.map(awp => awp.path) : undefined,
      MediaTypes: attachmentsWithPaths.length > 0 ? attachmentsWithPaths.map(awp => runtime.media.mediaKindFromMime(awp.attachment.mimeType)) : undefined,
    });

    const storePath = runtime.channel.session.resolveStorePath(
      (this.cfg as OpenClawConfig).session?.store,
      {agentId: route.agentId},
    );

    await runtime.channel.session.recordInboundSession({
      storePath,
      sessionKey: ctxPayload.SessionKey ?? route.sessionKey,
      ctx: ctxPayload,
      onRecordError: (err: unknown) => {
        this.logger?.error(`olvid: failed updating session meta: ${String(err)}`);
      },
    });

    // let robot: boolean = false;
    await runtime.channel.reply.dispatchReplyWithBufferedBlockDispatcher({
      ctx: ctxPayload,
      cfg: this.cfg,
      dispatcherOptions: {
        // onReplyStart: async () => {
          // if (!robot) {
          //   // add "typing" reaction
          //   await message.react(this, "🤖");
          //   robot = true;
          //   this.logger?.info("added typing reaction")
          // }
        // },
        deliver: async (payload: ReplyPayload) => {
          if (payload.replyToCurrent) {
            payload.replyToId = messageIdToString(message.id);
          }

          // prepare and check response validity
          const text = payload.text ?? "";
          const mediaList = payload.mediaUrls?.length ? payload.mediaUrls : payload.mediaUrl ? [payload.mediaUrl] : [];
          if (!text.trim() && mediaList.length === 0) {
            return;
          }
          const to: string = `olvid:discussion:${discussion.id}`;

          await sendMessageOlvid(to, text, { accountId: this.account.accountId, replyTo: payload.replyToId, mediaUrls: mediaList });
          this.opts.statusSink?.({ lastOutboundAt: Date.now() });

          // // remove "typing" reaction from this message
          // await message.react(this, "");
          // // remove "typing" reaction from messages older than this one
          // for await (const m of this.messageList({filter: new datatypes.MessageFilter({reactionsFilter: [new datatypes.ReactionFilter({reaction: "🤖"})], maxTimestamp: message.timestamp})})) {
          //   await m.react(this, "");
          // }
        },
        onError: (err, info) => {
          this.logger?.error?.(`${info.kind} reply failed: ${String(err)}`);
        },
      }
    });
  }
}

let globalRunBot = false;

export async function monitorOlvidProvider(opts: MonitorOlvidOpts = {}): Promise<void> {
  const core = getOlvidRuntime();
  const cfg: CoreConfig = opts.config ?? (core.config.loadConfig() as CoreConfig);
  const account = resolveOlvidAccount({ cfg: cfg, accountId: opts.accountId });

  if (!account.daemonUrl) {
    throw new Error(`Olvid daemon url not configured for account "${account.accountId}"`);
  }
  if (!account.clientKey) {
    throw new Error(`Olvid client key not configured for account "${account.accountId}"`);
  }

  globalRunBot = true;
  while (globalRunBot) {
    try {
      let bot = new OpenClawBot(account, opts, cfg);
      opts.statusSink?.({connected: true, lastConnectedAt: Date.now()});
      await bot.waitForCallbacksEnd();
    } catch (err) {
      opts.logger?.error(`olvid: ${err}`);
      opts.statusSink?.({
        lastError: String(err),
        connected: false,
        lastDisconnect: {at: Date.now(), error: String(err)},
      });
    }
    opts.logger?.info("wait before reconnection try")
    await new Promise(resolve => setTimeout(resolve, 5_000));
  }
}
