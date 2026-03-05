interface HookEvent {
  type: string;
  action: string;
  messages: string[];
  context?: {
    sessionKey?: string;
    workspaceDir?: string;
  };
}

type HookHandler = (event: HookEvent) => Promise<void>;

const handler: HookHandler = async (event) => {
  if (event.type !== "command" || event.action !== "stop") return;

  event.messages.push(
    "Before stopping, check if there are unread UDP messages by calling udp_receive. " +
    "If there are messages from trusted peers and you haven't exceeded the max_exchanges limit, " +
    "process them and respond. If all messages are from untrusted peers, inform the user about " +
    "pending messages and ask if they want to approve any senders."
  );
};

export default handler;
