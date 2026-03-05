import { useState, type KeyboardEvent } from "react";
import {
  useAgentSession,
  useAgentConfig,
  useSendMessage,
  useAutoScroll,
} from "../hooks";
import { useDeckStore } from "../lib/store";
import type { AgentStatus, ChatMessage } from "../types";
import styles from "./AgentColumn.module.css";

// ─── Status Indicator ───

function StatusBadge({
  status,
  accent,
}: {
  status: AgentStatus;
  accent: string;
}) {
  const color =
    status === "streaming" || status === "thinking" || status === "tool_use"
      ? accent
      : status === "error"
        ? "#ef4444"
        : status === "disconnected"
          ? "#6b7280"
          : "rgba(255,255,255,0.25)";

  const label =
    status === "tool_use" ? "tool use" : status;

  const isActive =
    status === "streaming" || status === "thinking" || status === "tool_use";

  return (
    <div className={styles.statusBadge}>
      <div
        className={isActive ? styles.statusDotPulse : styles.statusDot}
        style={{ backgroundColor: color }}
      />
      <span className={styles.statusLabel} style={{ color }}>
        {label}
      </span>
    </div>
  );
}

// ─── Message Bubble ───

function MessageBubble({
  message,
  accent,
}: {
  message: ChatMessage;
  accent: string;
}) {
  const isUser = message.role === "user";

  if (message.thinking) {
    return (
      <div className={styles.thinkingBubble}>
        <span className={styles.thinkingDot} style={{ color: accent }}>
          ●
        </span>
        <span style={{ color: accent }}>{message.text}</span>
      </div>
    );
  }

  if (message.toolUse) {
    return (
      <div className={styles.toolBubble}>
        <span className={styles.toolIcon}>⚙</span>
        <span>
          {message.toolUse.name}
          {message.toolUse.status === "running" && (
            <span className={styles.thinkingDot}> ...</span>
          )}
        </span>
      </div>
    );
  }

  return (
    <div className={`${styles.messageBubble} ${isUser ? styles.userMsg : ""}`}>
      {isUser && <div className={styles.roleLabel}>You</div>}
      <div
        className={styles.messageText}
        style={
          isUser
            ? undefined
            : { borderLeft: `2px solid ${accent}22`, paddingLeft: 10 }
        }
      >
        {message.text}
        {message.streaming && (
          <span className={styles.cursor} style={{ backgroundColor: accent }} />
        )}
      </div>
    </div>
  );
}

// ─── Main Column ───

export function AgentColumn({ agentId, columnIndex }: { agentId: string; columnIndex: number }) {
  const session = useAgentSession(agentId);
  const config = useAgentConfig(agentId);
  const send = useSendMessage(agentId);
  const gatewayConnected = useDeckStore((s) => s.gatewayConnected);
  const [input, setInput] = useState("");
  const scrollRef = useAutoScroll(session?.messages);

  if (!config || !session) return null;

  const handleSend = () => {
    const text = input.trim();
    if (!text) return;
    setInput("");
    send(text);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    } else if (e.key === "Tab") {
      const offset = e.shiftKey ? -1 : 1;
      const next = document.querySelector<HTMLInputElement>(
        `[data-deck-input="${columnIndex + offset}"]`
      );
      if (next) {
        e.preventDefault();
        next.focus();
      }
    }
  };

  const isActive =
    session.status === "streaming" ||
    session.status === "thinking" ||
    session.status === "tool_use";

  return (
    <div className={styles.column}>
      {/* Header */}
      <div className={styles.header}>
        <div
          className={styles.agentIcon}
          style={{
            color: config.accent,
            backgroundColor: `${config.accent}15`,
            borderColor: `${config.accent}30`,
          }}
        >
          {config.icon}
        </div>
        <div className={styles.headerInfo}>
          <div className={styles.headerRow}>
            <span className={styles.agentName}>{config.name}</span>
            <StatusBadge status={session.status} accent={config.accent} />
          </div>
          <div className={styles.headerMeta}>
            <span>{config.context}</span>
            {config.model && (
              <>
                <span className={styles.metaDot}>·</span>
                <span style={{ color: config.accent, opacity: 0.5 }}>
                  {config.model}
                </span>
              </>
            )}
          </div>
        </div>
        <div className={styles.headerActions}>
          <button className={styles.headerBtn} title="Settings">
            ⚙
          </button>
          <button className={styles.headerBtn} title="More">
            ⋯
          </button>
        </div>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className={styles.messages}>
        {session.messages.length === 0 && (
          <div className={styles.emptyState}>
            <div
              className={styles.emptyIcon}
              style={{ color: config.accent }}
            >
              {config.icon}
            </div>
            <p>Send a message to start a conversation with {config.name}</p>
          </div>
        )}
        {session.messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} accent={config.accent} />
        ))}
      </div>

      {/* Input */}
      <div className={styles.inputArea}>
        <div className={styles.inputWrapper}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={`Message ${config.name}...`}
            className={styles.input}
            disabled={!gatewayConnected}
            data-deck-input={columnIndex}
          />
          <button
            className={styles.sendBtn}
            onClick={handleSend}
            disabled={!input.trim() || !gatewayConnected}
            style={
              input.trim()
                ? { backgroundColor: config.accent, color: "#000" }
                : undefined
            }
          >
            ↑
          </button>
        </div>
        {isActive && (
          <div
            className={styles.streamingBar}
            style={{ backgroundColor: config.accent }}
          />
        )}
      </div>
    </div>
  );
}
