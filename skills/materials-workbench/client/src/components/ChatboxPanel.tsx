import {
  useState,
  useRef,
  useCallback,
  useLayoutEffect,
  useEffect,
} from "react";
import { postChatStream } from "../api";
import {
  PADDING,
  GAP,
  INPUT_ROW_HEIGHT,
  ATTACH_BUTTON_WIDTH,
  SEND_BUTTON_WIDTH,
} from "../utils/chatSchema";
import { useIsMobile } from "../hooks/useMediaQuery";
import type { ChatMessage, StreamEvent } from "../api";
import type { RenderData } from "declare-render";

const PICUI_PROXY_PREFIXES: [string, string][] = [
  ["https://free.picui.cn", "/picui-free"],
  ["https://picui.cn", "/picui-cn"],
];

/** Rewrite picui image URLs to Vite proxy paths so dev server can proxy them (avoids CORS). */
function rewritePicuiUrlsToProxy(
  data: RenderData | null | undefined,
): RenderData | null {
  if (!data?.layers) return data ?? null;
  function rewriteLayers(layers: RenderData["layers"]): RenderData["layers"] {
    if (!Array.isArray(layers)) return layers;
    return layers.map((layer) => {
      const next = { ...layer } as (typeof layers)[0];
      if (
        next.type === "img" &&
        typeof (next as { url?: string }).url === "string"
      ) {
        const url = (next as { url: string }).url;
        for (const [origin, prefix] of PICUI_PROXY_PREFIXES) {
          if (url.startsWith(origin + "/")) {
            (next as { url: string }).url = prefix + url.slice(origin.length);
            break;
          }
        }
      }
      if ("layers" in next && Array.isArray(next.layers))
        (next as { layers: RenderData["layers"] }).layers = rewriteLayers(
          (next as { layers: RenderData["layers"] }).layers,
        );
      return next;
    });
  }
  return { ...data, layers: rewriteLayers(data.layers) };
}

const AGENT_LABELS: Record<string, string> = {
  orchestrator: "Orchestrator",
  design: "Design Agent",
  canvas: "Canvas Agent",
  verification: "Verification",
  "orchestrator-replan": "Re-planning",
};

const MIN_WIDTH = 280;
const MIN_HEIGHT = 200;
const MAX_WIDTH_RATIO = 0.9;
const MAX_HEIGHT_RATIO = 0.8;
const MIN_VISIBLE = 100;
/** On mobile, chat panel height as fraction of viewport */
const MOBILE_SHEET_HEIGHT_RATIO = 0.65;
const MOBILE_MIN_SHEET_HEIGHT = 280;
/** Height of the chat bar when minimized on mobile */
const MOBILE_MINIMIZED_HEIGHT = 52;
/** PC: minimized FAB (circle button) size and inset */
const FAB_SIZE = 56;
const FAB_INSET = 20;

function clampPosition(
  left: number,
  top: number,
  _width: number,
  _height: number
): { left: number; top: number } {
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  const maxLeft = vw - MIN_VISIBLE;
  const maxTop = vh - MIN_VISIBLE;
  return {
    left: Math.max(0, Math.min(left, maxLeft)),
    top: Math.max(0, Math.min(top, maxTop)),
  };
}

function clampSize(
  width: number,
  height: number
): { width: number; height: number } {
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  return {
    width: Math.max(MIN_WIDTH, Math.min(width, vw * MAX_WIDTH_RATIO)),
    height: Math.max(MIN_HEIGHT, Math.min(height, vh * MAX_HEIGHT_RATIO)),
  };
}

export interface ChatboxPanelProps {
  messages: ChatMessage[];
  onMessagesChange: (m: ChatMessage[]) => void;
  onRenderDataChange: (d: RenderData | null) => void;
  onError: (err: string) => void;
  getCurrentRenderData: () => RenderData | null;
}

export default function ChatboxPanel({
  messages,
  onMessagesChange,
  onRenderDataChange,
  onError,
  getCurrentRenderData,
}: ChatboxPanelProps) {
  const [input, setInput] = useState("");
  const [attachedImage, setAttachedImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [streamSteps, setStreamSteps] = useState<ChatMessage[]>([]);
  const [position, setPosition] = useState({ left: 0, top: 0 });
  const [size, setSize] = useState({ width: 380, height: 480 });
  const [isMounted, setIsMounted] = useState(false);
  const [dragState, setDragState] = useState<{
    startX: number;
    startY: number;
    startLeft: number;
    startTop: number;
  } | null>(null);
  const [touchDragState, setTouchDragState] = useState<{
    startX: number;
    startY: number;
    startLeft: number;
    startTop: number;
  } | null>(null);
  const [resizeState, setResizeState] = useState<{
    startX: number;
    startY: number;
    startWidth: number;
    startHeight: number;
  } | null>(null);
  const [mobileResizeState, setMobileResizeState] = useState<{
    startY: number;
    startHeight: number;
  } | null>(null);
  const [minimized, setMinimized] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const stepsSnapshotRef = useRef<ChatMessage[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const isMobile = useIsMobile();

  const toggleMinimized = useCallback(() => setMinimized((m) => !m), []);

  const displayMessages = [
    ...messages.filter((m) => !m.hidden),
    ...streamSteps,
  ];

  useLayoutEffect(() => {
    if (isMounted) return;
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    if (vw <= 768) {
      const sheetHeight = Math.max(
        MOBILE_MIN_SHEET_HEIGHT,
        Math.min(vh * MOBILE_SHEET_HEIGHT_RATIO, vh - 60)
      );
      setSize({ width: vw, height: sheetHeight });
      // On mobile, panel is part of flex layout, no position needed
    } else {
      const initialSize = clampSize(380, 480);
      setSize(initialSize);
      setPosition({
        left: vw - initialSize.width - 20,
        top: vh - initialSize.height - 20,
      });
    }
    setIsMounted(true);
  }, [isMounted]);

  useLayoutEffect(() => {
    if (!isMobile) return;
    if (minimized) return;
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const sheetHeight = Math.max(
      MOBILE_MIN_SHEET_HEIGHT,
      Math.min(vh * MOBILE_SHEET_HEIGHT_RATIO, vh - 60)
    );
    setSize({ width: vw, height: sheetHeight });
  }, [isMobile, minimized]);

  const handleEvent = useCallback(
    (event: StreamEvent) => {
      switch (event.type) {
        case "agent_start":
          setStreamSteps((prev) => {
            const next = [
              ...prev,
              {
                role: "assistant" as const,
                content: "",
                agent: event.agent,
                thinking: "",
              },
            ];
            stepsSnapshotRef.current = next;
            return next;
          });
          break;
        case "thinking_delta":
          setStreamSteps((prev) => {
            if (prev.length === 0) return prev;
            const next = [...prev];
            const last = { ...next[next.length - 1] };
            last.thinking = (last.thinking ?? "") + event.delta;
            next[next.length - 1] = last;
            stepsSnapshotRef.current = next;
            return next;
          });
          break;
        case "text_delta":
          setStreamSteps((prev) => {
            if (prev.length === 0) return prev;
            const next = [...prev];
            const last = { ...next[next.length - 1] };
            last.content += event.delta;
            next[next.length - 1] = last;
            stepsSnapshotRef.current = next;
            return next;
          });
          break;
        case "text":
          setStreamSteps((prev) => {
            if (prev.length === 0) return prev;
            const next = [...prev];
            const last = { ...next[next.length - 1] };
            last.content = event.content;
            next[next.length - 1] = last;
            stepsSnapshotRef.current = next;
            return next;
          });
          break;
        case "render_data": {
          const hasLayers = !!event.renderData?.layers?.length;
          console.debug("[Chatbox] render_data received, layers:", hasLayers ? event.renderData!.layers!.length : 0);
          onRenderDataChange(rewritePicuiUrlsToProxy(event.renderData));
          // Chat was showing streamed JSON (with {{IMAGE_1}}). Update canvas step to show
          // the same renderData the server sent (placeholders already replaced).
          if (event.renderData != null) {
            setStreamSteps((prev) => {
              if (prev.length === 0) return prev;
              const next = [...prev];
              const last = next[next.length - 1];
              if (last.agent === "canvas") {
                next[next.length - 1] = {
                  ...last,
                  content: JSON.stringify(event.renderData, null, 2),
                };
                stepsSnapshotRef.current = next;
              }
              return next;
            });
          }
          break;
        }
        case "verification":
          setStreamSteps((prev) => {
            if (prev.length === 0) return prev;
            const next = [...prev];
            const last = { ...next[next.length - 1] };
            last.content = event.passed
              ? "Verification passed"
              : `Verification failed: ${event.errors.join("; ")}`;
            next[next.length - 1] = last;
            stepsSnapshotRef.current = next;
            return next;
          });
          break;
        case "error":
          onError(event.message);
          break;
        default:
          break;
      }
    },
    [onRenderDataChange, onError]
  );

  const sendMessage = useCallback(async () => {
    const text = input.trim();
    if (!text && !attachedImage) return;
    setLoading(true);
    onError("");

    const userMessage: ChatMessage = {
      role: "user",
      content: text || "See attached image.",
      ...(attachedImage && { image: attachedImage }),
    };
    const nextMessages = [...messages, userMessage];
    onMessagesChange(nextMessages);
    setInput("");
    setAttachedImage(null);

    stepsSnapshotRef.current = [];
    setStreamSteps([]);

    try {
      const messagesToSend = nextMessages
        .filter((m) => !m.agent && !m.hidden)
        .map((m) => ({ role: m.role, content: m.content, image: m.image }));

      await postChatStream(
        {
          messages: messagesToSend,
          currentRenderData: getCurrentRenderData() ?? undefined,
        },
        handleEvent
      );

      const finalSteps = stepsSnapshotRef.current;
      const lastContent =
        finalSteps
          .filter(
            (s) =>
              s.agent !== "verification" && s.agent !== "orchestrator"
          )
          .map((s) => s.content)
          .filter(Boolean)
          .pop() ?? "";
      const summaryMsg: ChatMessage = {
        role: "assistant",
        content: lastContent,
        hidden: true,
      };
      onMessagesChange([...nextMessages, ...finalSteps, summaryMsg]);
      setStreamSteps([]);
    } catch (err) {
      onError(err instanceof Error ? err.message : "Request failed");
      if (stepsSnapshotRef.current.length > 0) {
        onMessagesChange([...nextMessages, ...stepsSnapshotRef.current]);
      }
      setStreamSteps([]);
    } finally {
      setLoading(false);
    }
  }, [
    input,
    attachedImage,
    messages,
    onMessagesChange,
    onError,
    getCurrentRenderData,
    handleEvent,
  ]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !file.type.startsWith("image/")) return;
    const reader = new FileReader();
    reader.onload = () => setAttachedImage(reader.result as string);
    reader.readAsDataURL(file);
    e.target.value = "";
  };

  const onDragStart = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setDragState({
      startX: e.clientX,
      startY: e.clientY,
      startLeft: position.left,
      startTop: position.top,
    });
  }, [position.left, position.top]);

  const onTouchStartDrag = useCallback(
    (e: React.TouchEvent) => {
      const t = e.touches[0];
      if (!t) return;
      setTouchDragState({
        startX: t.clientX,
        startY: t.clientY,
        startLeft: position.left,
        startTop: position.top,
      });
    },
    [position.left, position.top]
  );

  const onResizeStart = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setResizeState({
      startX: e.clientX,
      startY: e.clientY,
      startWidth: size.width,
      startHeight: size.height,
    });
  }, [size.width, size.height]);

  useEffect(() => {
    if (!resizeState) return;
    const onMove = (e: MouseEvent) => {
      const dx = e.clientX - resizeState.startX;
      const dy = e.clientY - resizeState.startY;
      const next = clampSize(
        resizeState.startWidth + dx,
        resizeState.startHeight + dy
      );
      setSize(next);
      setPosition((p) =>
        clampPosition(p.left, p.top, next.width, next.height)
      );
    };
    const onUp = () => setResizeState(null);
    const onLeave = () => setResizeState(null);
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    document.body.addEventListener("mouseleave", onLeave);
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
      document.body.removeEventListener("mouseleave", onLeave);
    };
  }, [resizeState]);

  useEffect(() => {
    if (!dragState) return;
    const onMove = (e: MouseEvent) => {
      const left = dragState.startLeft + e.clientX - dragState.startX;
      const top = dragState.startTop + e.clientY - dragState.startY;
      const next = clampPosition(left, top, size.width, size.height);
      setPosition(next);
    };
    const onUp = () => setDragState(null);
    const onLeave = () => setDragState(null);
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    document.body.addEventListener("mouseleave", onLeave);
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
      document.body.removeEventListener("mouseleave", onLeave);
    };
  }, [dragState, size.width, size.height]);

  useEffect(() => {
    if (!touchDragState) return;
    const onMove = (e: TouchEvent) => {
      e.preventDefault();
      const t = e.touches[0];
      if (!t) return;
      const left = touchDragState.startLeft + t.clientX - touchDragState.startX;
      const top = touchDragState.startTop + t.clientY - touchDragState.startY;
      const next = clampPosition(left, top, size.width, size.height);
      setPosition(next);
    };
    const onEnd = () => setTouchDragState(null);
    window.addEventListener("touchmove", onMove, { passive: false });
    window.addEventListener("touchend", onEnd);
    window.addEventListener("touchcancel", onEnd);
    return () => {
      window.removeEventListener("touchmove", onMove);
      window.removeEventListener("touchend", onEnd);
      window.removeEventListener("touchcancel", onEnd);
    };
  }, [touchDragState, size.width, size.height]);

  useEffect(() => {
    const handleResize = () => {
      const vw = window.innerWidth;
      if (vw <= 768) {
        if (minimized) return;
        // On mobile, only update width; height is controlled by user drag
        setSize((s) => ({ width: vw, height: s.height }));
      } else {
        setPosition((p) =>
          clampPosition(p.left, p.top, size.width, size.height)
        );
        setSize((s) => clampSize(s.width, s.height));
      }
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [size.width, size.height, minimized]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [streamSteps]);

  const onMobileHeaderResizeStart = useCallback(
    (e: React.MouseEvent | React.TouchEvent) => {
      e.preventDefault();
      e.stopPropagation();
      const clientY =
        "touches" in e ? e.touches[0]?.clientY ?? 0 : e.clientY;
      setMobileResizeState({
        startY: clientY,
        startHeight: size.height,
      });
    },
    [size.height]
  );

  useEffect(() => {
    if (!mobileResizeState || !isMobile) return;
    const onMove = (e: MouseEvent | TouchEvent) => {
      e.preventDefault();
      const clientY =
        "touches" in e ? e.touches[0]?.clientY ?? 0 : e.clientY;
      const dy = mobileResizeState.startY - clientY; // Negative when dragging up
      const vh = window.innerHeight;
      const newHeight = Math.max(
        MOBILE_MIN_SHEET_HEIGHT,
        Math.min(
          mobileResizeState.startHeight + dy,
          vh * MAX_HEIGHT_RATIO
        )
      );
      setSize({ width: window.innerWidth, height: newHeight });
    };
    const onEnd = () => setMobileResizeState(null);
    window.addEventListener("mousemove", onMove);
    window.addEventListener("touchmove", onMove, { passive: false });
    window.addEventListener("mouseup", onEnd);
    window.addEventListener("touchend", onEnd);
    window.addEventListener("touchcancel", onEnd);
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("touchmove", onMove);
      window.removeEventListener("mouseup", onEnd);
      window.removeEventListener("touchend", onEnd);
      window.removeEventListener("touchcancel", onEnd);
    };
  }, [mobileResizeState, isMobile]);

  if (!isMounted) return null;

  const isMinimizedMobile = isMobile && minimized;
  const isMinimizedPc = !isMobile && minimized;

  if (isMinimizedPc) {
    return (
      <button
        type="button"
        onClick={toggleMinimized}
        aria-label="Open chat"
        title="Open chat"
        style={{
          position: "fixed",
          right: `max(${FAB_INSET}px, env(safe-area-inset-right))`,
          bottom: `max(${FAB_INSET}px, env(safe-area-inset-bottom))`,
          width: FAB_SIZE,
          height: FAB_SIZE,
          borderRadius: "50%",
          border: "1px solid var(--wb-border)",
          background: "var(--wb-chat-bg)",
          color: "var(--wb-text)",
          boxShadow: "0 4px 20px rgba(0,0,0,0.15)",
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 24,
          zIndex: 1000,
        }}
      >
        💬
      </button>
    );
  }

  const panelStyle: React.CSSProperties = isMinimizedMobile
    ? {
        position: "fixed",
        left: 0,
        right: 0,
        bottom: 0,
        width: "100%",
        minHeight: MOBILE_MINIMIZED_HEIGHT,
        height: `calc(${MOBILE_MINIMIZED_HEIGHT}px + env(safe-area-inset-bottom))`,
        paddingBottom: "env(safe-area-inset-bottom)",
        display: "flex",
        flexDirection: "column",
        background: "var(--wb-chat-bg)",
        border: "none",
        borderTopLeftRadius: 12,
        borderTopRightRadius: 12,
        boxShadow: "0 -4px 24px rgba(0,0,0,0.15)",
        zIndex: 1000,
        overflow: "hidden",
      }
    : isMobile
      ? {
          flexShrink: 0,
          width: "100%",
          height: size.height,
          minHeight: MOBILE_MIN_SHEET_HEIGHT,
          maxHeight: window.innerHeight * MAX_HEIGHT_RATIO,
          paddingBottom: "env(safe-area-inset-bottom)",
          display: "flex",
          flexDirection: "column",
          background: "var(--wb-chat-bg)",
          border: "none",
          borderTopLeftRadius: 12,
          borderTopRightRadius: 12,
          boxShadow: "0 -4px 24px rgba(0,0,0,0.15)",
          overflow: "hidden",
        }
      : {
          position: "fixed",
          left: position.left,
          top: position.top,
          width: size.width,
          height: size.height,
          minWidth: MIN_WIDTH,
          minHeight: MIN_HEIGHT,
          maxWidth: window.innerWidth * MAX_WIDTH_RATIO,
          maxHeight: window.innerHeight * MAX_HEIGHT_RATIO,
          display: "flex",
          flexDirection: "column",
          background: "var(--wb-chat-bg)",
          border: "1px solid var(--wb-border)",
          borderRadius: 8,
          boxShadow: "0 8px 32px rgba(0,0,0,0.12)",
          zIndex: 1000,
          overflow: "hidden",
        };

  const onHeaderPointerDown = isMobile ? undefined : onDragStart;
  const onHeaderTouchStart = isMobile
    ? minimized
      ? undefined
      : onMobileHeaderResizeStart
    : onTouchStartDrag;
  const onHeaderMouseDown = isMobile && !minimized
    ? onMobileHeaderResizeStart
    : onHeaderPointerDown;
  const onHeaderClick = isMinimizedMobile ? toggleMinimized : undefined;

  return (
    <div ref={panelRef} style={panelStyle}>
      <div
        onMouseDown={onHeaderMouseDown}
        onTouchStart={onHeaderTouchStart}
        onClick={onHeaderClick}
        style={{
          padding: isMobile ? "12px 16px" : "8px 10px",
          minHeight: isMobile ? 44 : undefined,
          borderBottom: minimized ? "none" : "1px solid var(--wb-border)",
          fontWeight: 600,
          fontSize: 12,
          color: "var(--wb-text)",
          cursor: isMinimizedMobile
            ? "pointer"
            : isMobile
              ? "ns-resize"
              : "grab",
          background: "transparent",
          touchAction: isMobile && !minimized ? "none" : "manipulation",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 8,
          userSelect: "none",
        }}
      >
        <span>Chat</span>
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            toggleMinimized();
          }}
          aria-label={minimized ? "Expand chat" : "Minimize chat"}
          title={minimized ? "Expand chat" : "Minimize chat"}
          style={{
            flexShrink: 0,
            width: isMobile ? 44 : 32,
            height: isMobile ? 44 : 32,
            minWidth: isMobile ? 44 : 32,
            minHeight: isMobile ? 44 : 32,
            padding: 0,
            border: "none",
            borderRadius: 6,
            background: "transparent",
            color: "var(--wb-text-muted)",
            cursor: "pointer",
            fontSize: 18,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {minimized ? "⊕" : "−"}
        </button>
      </div>
      {!minimized && (
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          minHeight: 0,
        }}
      >
        <div
          className="hide-scrollbar"
          style={{
            flex: 1,
            overflow: "auto",
            minHeight: 0,
            padding: PADDING,
            display: "flex",
            flexDirection: "column",
            gap: GAP,
          }}
        >
          {displayMessages.length === 0 && (
            <div
              style={{
                color: "var(--wb-text-muted)",
                fontSize: 12,
              }}
            >
              Send a message to create or edit a canvas. You can attach
              images as materials.
            </div>
          )}
          {displayMessages.map((m, i) => (
            <MessageBubble
              key={i}
              message={m}
              isLast={
                i === displayMessages.length - 1 && loading
              }
            />
          ))}
          {loading && streamSteps.length === 0 && (
            <div
              style={{
                color: "var(--wb-text-muted)",
                fontSize: 12,
              }}
            >
              Thinking…
            </div>
          )}
          <div ref={bottomRef} />
        </div>
        <div
          style={{
            flexShrink: 0,
            padding: PADDING,
            paddingTop: GAP,
            borderTop: "1px solid var(--wb-border)",
            display: "flex",
            flexDirection: "column",
            gap: GAP,
          }}
        >
          {attachedImage && (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
              }}
            >
              <img
                src={attachedImage}
                alt="Attached preview"
                style={{
                  width: 36,
                  height: 36,
                  objectFit: "cover",
                  borderRadius: 4,
                  border: "1px solid var(--wb-border)",
                }}
              />
              <button
                type="button"
                onClick={() => setAttachedImage(null)}
                style={{
                  fontSize: 11,
                  cursor: "pointer",
                  background: "transparent",
                  border: "none",
                  color: "var(--wb-text)",
                }}
              >
                Remove
              </button>
            </div>
          )}
          <div
            style={{
              display: "flex",
              gap: GAP,
              alignItems: "stretch",
            }}
          >
          <div>
            <input
              type="file"
              ref={fileInputRef}
              accept="image/*"
              onChange={handleFileChange}
              style={{ display: "none" }}
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              style={{
                width: ATTACH_BUTTON_WIDTH,
                height: isMobile ? 44 : INPUT_ROW_HEIGHT,
                minHeight: isMobile ? 44 : undefined,
                padding: "6px 10px",
                cursor: "pointer",
                border: "1px solid var(--wb-input-border)",
                borderRadius: 6,
                background: "var(--wb-input-bg)",
                color: "var(--wb-text)",
                fontSize: 11,
              }}
            >
              Attach image
            </button>
          </div>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) =>
              e.key === "Enter" && !e.shiftKey && sendMessage()
            }
            placeholder="Type a message…"
            disabled={loading}
            style={{
              flex: 1,
              minWidth: 0,
              padding: isMobile ? "10px 12px" : "6px 10px",
              minHeight: isMobile ? 44 : undefined,
              border: "1px solid var(--wb-input-border)",
              borderRadius: 6,
              fontSize: 16,
              background: "var(--wb-input-bg)",
              color: "var(--wb-text)",
            }}
          />
          <button
            type="button"
            onClick={sendMessage}
            disabled={loading}
            style={{
              width: SEND_BUTTON_WIDTH,
              height: isMobile ? 44 : INPUT_ROW_HEIGHT,
              minHeight: isMobile ? 44 : undefined,
              padding: "6px 10px",
              cursor: loading ? "not-allowed" : "pointer",
              border: "none",
              borderRadius: 6,
              background: "var(--wb-btn-primary-bg)",
              color: "var(--wb-btn-primary-color)",
              fontWeight: 500,
              fontSize: 11,
            }}
          >
            Send
          </button>
          </div>
        </div>
      </div>
      )}
      {!isMobile && (
        <div
          onMouseDown={onResizeStart}
          style={{
            position: "absolute",
            right: 0,
            bottom: 0,
            width: 16,
            height: 16,
            cursor: "nwse-resize",
            background:
              "linear-gradient(135deg, transparent 50%, var(--wb-border) 50%)",
          }}
          title="Resize"
        />
      )}
    </div>
  );
}

function MessageBubble({
  message: m,
  isLast,
}: {
  message: ChatMessage;
  isLast?: boolean;
}) {
  if (m.role === "user") {
    return (
      <div
        style={{
          alignSelf: "flex-end",
          maxWidth: "90%",
          padding: "6px 10px",
          borderRadius: 8,
          background: "var(--wb-bubble-user)",
          color: "var(--wb-text)",
          whiteSpace: "pre-wrap",
          wordBreak: "break-word",
          fontSize: 12,
        }}
      >
        {m.image && (
          <img
            src={m.image}
            alt="Attachment"
            style={{
              maxWidth: 120,
              maxHeight: 120,
              borderRadius: 4,
              marginBottom: 4,
            }}
          />
        )}
        {m.content}
      </div>
    );
  }

  if (m.agent) {
    const label = AGENT_LABELS[m.agent] ?? m.agent;
    return (
      <div
        style={{
          alignSelf: "flex-start",
          maxWidth: "95%",
          padding: "5px 8px",
          borderRadius: 8,
          background: "var(--wb-bubble-assistant)",
          color: "var(--wb-text)",
          fontSize: 11,
          borderLeft: "3px solid var(--wb-border)",
        }}
      >
        <div
          style={{
            fontSize: 10,
            fontWeight: 600,
            color: "var(--wb-text-muted)",
            marginBottom: 2,
            textTransform: "uppercase",
            letterSpacing: "0.05em",
          }}
        >
          {label}
          {isLast && !m.content && " …"}
        </div>
        {m.thinking && (
          <details
            style={{
              marginBottom: 4,
              fontSize: 11,
              color: "var(--wb-text-muted)",
            }}
          >
            <summary style={{ cursor: "pointer", userSelect: "none" }}>
              Thinking
            </summary>
            <div
              className="hide-scrollbar"
              style={{
                marginTop: 2,
                paddingLeft: 8,
                borderLeft: "2px solid var(--wb-border)",
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
                maxHeight: 200,
                overflow: "auto",
              }}
            >
              {m.thinking}
            </div>
          </details>
        )}
        {m.content && (
          <div
            style={{
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
            }}
          >
            {m.content}
          </div>
        )}
      </div>
    );
  }

  return (
    <div
      style={{
        alignSelf: "flex-start",
        maxWidth: "90%",
        padding: "6px 10px",
        borderRadius: 8,
        background: "var(--wb-bubble-assistant)",
        color: "var(--wb-text)",
        whiteSpace: "pre-wrap",
        wordBreak: "break-word",
        fontSize: 12,
      }}
    >
      {m.content}
    </div>
  );
}
