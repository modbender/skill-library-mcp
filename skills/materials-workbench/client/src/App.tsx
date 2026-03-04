import { useState, useRef, useEffect } from "react";
import ChatboxPanel from "./components/ChatboxPanel";
import MainCanvas from "./components/MainCanvas";
import type { RenderData } from "declare-render";
import type { ChatMessage } from "./api";

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [renderData, setRenderData] = useState<RenderData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const renderDataRef = useRef<RenderData | null>(null);

  useEffect(() => {
    renderDataRef.current = renderData;
  }, [renderData]);

  const onMessagesChange = (next: ChatMessage[]) => setMessages(next);
  const onRenderDataChange = (next: RenderData | null) => {
    if (!next) {
      setRenderData(null);
      return;
    }
    // Same id = update existing canvas; different id = create new canvas
    // structuredClone ensures new reference so React re-renders (handles duplicate emits)
    setRenderData(structuredClone(next));
  };
  const getCurrentRenderData = () => renderDataRef.current;
  const clearError = () => setError(null);

  return (
    <div
      style={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
        background: "var(--wb-canvas-bg)",
        color: "var(--wb-text)",
      }}
    >
      {error && (
        <div
          style={{
            flexShrink: 0,
            padding: "8px 12px",
            paddingTop: "max(8px, env(safe-area-inset-top))",
            background: "var(--wb-error-bg)",
            color: "var(--wb-error-text)",
            fontSize: 14,
          }}
        >
          {error}
          <button
            type="button"
            onClick={clearError}
            style={{
              marginLeft: 8,
              cursor: "pointer",
              background: "transparent",
              border: "none",
              color: "inherit",
            }}
          >
            Dismiss
          </button>
        </div>
      )}
      <MainCanvas renderData={renderData} />
      <ChatboxPanel
        messages={messages}
        onMessagesChange={onMessagesChange}
        onRenderDataChange={onRenderDataChange}
        onError={setError}
        getCurrentRenderData={getCurrentRenderData}
      />
    </div>
  );
}
