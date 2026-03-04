import { WebMCPTool, dispatchAndWait } from "@/lib/webmcp";

/**
 * AI Chat tools
 * Enable agent-to-agent communication through chat interface
 */
export const sendMessageTool: WebMCPTool = {
  name: "sendMessage",
  description: "Sends a message in the chat interface",
  execute: async (params) => {
    return dispatchAndWait(
      "sendMessage",
      params,
      "Message sent successfully",
    );
  },
  inputSchema: {
    type: "object",
    properties: {
      content: {
        type: "string",
        description: "The message content to send",
      },
      attachments: {
        type: "array",
        items: {
          type: "object",
          properties: {
            type: { type: "string" },
            url: { type: "string" },
            name: { type: "string" },
          },
        },
        description: "Optional file attachments",
      },
    },
    required: ["content"],
  },
  annotations: {
    readOnlyHint: "false",
  },
};

export const clearChatTool: WebMCPTool = {
  name: "clearChat",
  description: "Clears the chat history",
  execute: async () => {
    return dispatchAndWait("clearChat", {}, "Chat history cleared");
  },
  inputSchema: {},
  annotations: {
    readOnlyHint: "false",
  },
};

export const setModelTool: WebMCPTool = {
  name: "setModel",
  description: "Changes the AI model being used",
  execute: async (params) => {
    return dispatchAndWait(
      "setModel",
      params,
      `Model changed to ${params.model}`,
    );
  },
  inputSchema: {
    type: "object",
    properties: {
      model: {
        type: "string",
        enum: ["gpt-4", "gpt-3.5-turbo", "claude-3-opus", "claude-3-sonnet"],
        description: "The AI model to use",
      },
      temperature: {
        type: "number",
        minimum: 0,
        maximum: 2,
        description: "Sampling temperature",
      },
    },
    required: ["model"],
  },
  annotations: {
    readOnlyHint: "false",
  },
};

export const exportChatTool: WebMCPTool = {
  name: "exportChat",
  description: "Exports the chat history to a file",
  execute: async (params) => {
    return dispatchAndWait(
      "exportChat",
      params,
      `Chat exported as ${params.format}`,
    );
  },
  inputSchema: {
    type: "object",
    properties: {
      format: {
        type: "string",
        enum: ["json", "markdown", "txt"],
        description: "Export format",
      },
      filename: {
        type: "string",
        description: "Optional custom filename",
      },
    },
    required: ["format"],
  },
  annotations: {
    readOnlyHint: "true",
  },
};
