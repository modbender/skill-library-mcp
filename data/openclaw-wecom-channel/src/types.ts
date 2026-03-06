/**
 * 企业微信 Channel 插件 - 类型定义
 */

/** 企业微信配置 */
export type WecomConfig = {
  enabled?: boolean;
  corpId?: string;
  agentId?: string | number;
  secret?: string;
  token?: string;
  encodingAESKey?: string;
  port?: number;
  dmPolicy?: "open" | "pairing" | "allowlist";
  allowFrom?: (string | number)[];
};

/** 解析后的企业微信账号 */
export type ResolvedWecomAccount = {
  accountId: string;
  enabled: boolean;
  configured: boolean;
  corpId?: string;
  agentId?: string | number;
  secret?: string;
  token?: string;
  encodingAESKey?: string;
  port: number;
  /** 合并后的完整配置 */
  config: WecomConfig;
};

/** 企业微信消息上下文 */
export type WecomMessageContext = {
  /** 发送者 UserId */
  userId: string;
  /** 消息内容 */
  content: string;
  /** 消息 ID */
  msgId: string;
  /** 消息类型 (text, image, voice, ...) */
  msgType: string;
  /** 创建时间（秒级时间戳） */
  createTime: number;
  /** AgentID */
  agentId: string;
};

/** 企业微信发送结果 */
export type WecomSendResult = {
  errcode: number;
  errmsg: string;
  msgid?: string;
};

/** access_token 缓存结构 */
export type WecomTokenCache = {
  accessToken: string;
  expiresAt: number; // 毫秒时间戳
};
