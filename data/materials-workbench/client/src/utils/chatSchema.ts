import type {
  RenderData,
  TextRenderData,
  ContainerRenderData,
  ShapeRenderData,
} from "declare-render/browser";
import type { ChatMessage } from "../api";

/** Layout constants for chat UI. Used for overlay positioning. */
export const HEADER_HEIGHT = 44;
export const PADDING = 10;
export const GAP = 10;
export const INPUT_ROW_HEIGHT = 36;
export const ATTACH_BUTTON_WIDTH = 72;
export const SEND_BUTTON_WIDTH = 52;

/** Read a CSS variable value from the document (theme token). */
export function getTokenValue(token: string): string {
  if (typeof document === "undefined") return "#000";
  const value = getComputedStyle(document.documentElement)
    .getPropertyValue(token)
    .trim();
  return value || "#000";
}

export function getThemeColors(): {
  bubbleUser: string;
  bubbleAssistant: string;
  text: string;
  inputBg: string;
  inputBorder: string;
  btnPrimaryBg: string;
  btnPrimaryColor: string;
  textMuted: string;
} {
  return {
    bubbleUser: getTokenValue("--wb-bubble-user"),
    bubbleAssistant: getTokenValue("--wb-bubble-assistant"),
    text: getTokenValue("--wb-text"),
    inputBg: getTokenValue("--wb-input-bg"),
    inputBorder: getTokenValue("--wb-input-border"),
    btnPrimaryBg: getTokenValue("--wb-btn-primary-bg"),
    btnPrimaryColor: getTokenValue("--wb-btn-primary-color"),
    textMuted: getTokenValue("--wb-text-muted"),
  };
}

/**
 * Build a RenderData schema for the full chat UI (header, messages, input area).
 * Used by declare-render to layout and draw the entire chat canvas.
 */
export function buildChatSchema(
  messages: ChatMessage[],
  width: number,
  height: number,
  colors: ReturnType<typeof getThemeColors>
): RenderData {
  const displayMessages = messages.filter((m) => !m.hidden);
  const contentWidth = Math.max(1, width - PADDING * 2);
  const messagesHeight = Math.max(
    120,
    displayMessages.length * 60 + GAP * Math.max(0, displayMessages.length - 1)
  );
  // Header background and title
  const headerBg: ShapeRenderData = {
    id: "header-bg",
    type: "shape",
    x: 0,
    y: 0,
    shapes: [
      {
        type: "fillRect",
        x: 0,
        y: 0,
        width,
        height: HEADER_HEIGHT,
        style: { fillStyle: colors.inputBg },
      },
    ],
  };

  const headerLayer: TextRenderData = {
    id: "chat-header",
    type: "text",
    x: PADDING,
    y: (HEADER_HEIGHT - 20) / 2,
    width: width - PADDING * 2,
    height: 20,
    content: "Chat",
    style: {
      fontName: "sans-serif",
      fontSize: 16,
      color: colors.text,
      fontWeight: "600",
      verticalGap: 4,
    },
  };

  // Message layers
  const messageLayers: TextRenderData[] = displayMessages.map((m, i) => {
    const isUser = m.role === "user";
    const backgroundColor = isUser ? colors.bubbleUser : colors.bubbleAssistant;
    return {
      id: `msg-${i}`,
      type: "text",
      x: PADDING,
      y: undefined as unknown as number,
      width: contentWidth,
      height: 40,
      content: m.content || (m.agent ? "" : " "),
      style: {
        fontName: "sans-serif",
        fontSize: 14,
        color: colors.text,
        backgroundColor,
        padding: 8,
        radius: 8,
        verticalGap: 6,
      },
    };
  });

  // Empty state when no messages
  const emptyStateLayer: TextRenderData | null =
    displayMessages.length === 0
      ? {
          id: "empty-state",
          type: "text",
          x: PADDING,
          y: 0,
          width: contentWidth,
          height: 40,
          content: "Send a message to create or edit a canvas. You can attach images as materials.",
          style: {
            fontName: "sans-serif",
            fontSize: 14,
            color: colors.textMuted,
            verticalGap: 6,
          },
        }
      : null;

  const messagesContainerLayers = emptyStateLayer
    ? [emptyStateLayer, ...messageLayers]
    : messageLayers;

  // Messages container
  const messagesContainer: ContainerRenderData = {
    id: "chat-messages",
    type: "container",
    x: 0,
    y: HEADER_HEIGHT + PADDING,
    width,
    height: messagesHeight,
    direction: "column",
    gap: GAP,
    layers: messagesContainerLayers,
  };

  const totalHeight = HEADER_HEIGHT + PADDING + messagesHeight + PADDING;

  const rootContainer: ContainerRenderData = {
    id: "chat-root",
    type: "container",
    x: 0,
    y: 0,
    width,
    height: totalHeight,
    direction: "column",
    layers: [
      headerBg,
      headerLayer,
      messagesContainer,
    ],
  };

  return {
    id: "chat",
    width,
    height: Math.max(height, totalHeight),
    layers: [rootContainer],
  };
}
