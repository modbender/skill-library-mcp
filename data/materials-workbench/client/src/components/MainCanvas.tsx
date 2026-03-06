import {
  useRef,
  useLayoutEffect,
  useState,
  useCallback,
  useEffect,
} from "react";
import { Renderer } from "declare-render/browser";
import type { RenderData } from "declare-render";
import { useIsMobile } from "../hooks/useMediaQuery";

const ZOOM_MIN = 0.25;
const ZOOM_MAX = 4;
const ZOOM_STEP_SLOW = 0.01;
const ZOOM_STEP_FAST = 0.05;
const FAST_THRESHOLD_MS = 400;

export interface MainCanvasProps {
  renderData: RenderData | null;
}

const ZOOM_BUTTON_MIN_TOUCH = 44;

export default function MainCanvas({ renderData }: MainCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasHostRef = useRef<HTMLDivElement>(null);
  const lastZoomTimeRef = useRef(0);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [zoom, setZoom] = useState(0.5);
  const [renderError, setRenderError] = useState<string | null>(null);
  const isMobile = useIsMobile();

  useLayoutEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const ro = new ResizeObserver(() => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth || 800,
          height: containerRef.current.clientHeight || 600,
        });
      }
    });
    ro.observe(container);
    setDimensions({
      width: container.clientWidth || 800,
      height: container.clientHeight || 600,
    });
    return () => ro.disconnect();
  }, []);

  useLayoutEffect(() => {
    const canvasHost = canvasHostRef.current;
    if (!canvasHost) return;

    setRenderError(null);

    if (!renderData?.layers?.length) {
      canvasHost.innerHTML = "";
      return;
    }

    let cancelled = false;
    const run = async () => {
      try {
        console.debug("[MainCanvas] render start, layers:", renderData.layers.length);
        const r = new Renderer(renderData);
        await r.render();
        if (cancelled) return;
        setRenderError(null);
        console.debug("[MainCanvas] render success");
        const el = r.getCanvasElement();
        if (el && canvasHost) {
          canvasHost.innerHTML = "";
          el.style.display = "block";
          el.style.width = "100%";
          el.style.height = "100%";
          el.style.objectFit = "contain";
          el.style.objectPosition = "center";
          canvasHost.appendChild(el);
        }
      } catch (err) {
        if (!cancelled) {
          let msg: string;
          if (err instanceof Error) {
            msg = err.message;
          } else if (err && typeof err === "object" && "type" in err && (err as Event).type === "error") {
            const ev = err as Event;
            const target = ev.target as HTMLImageElement | null;
            msg = target?.src
              ? `Image failed to load: ${target.src.slice(0, 80)}${target.src.length > 80 ? "…" : ""}`
              : "Image load error";
          } else {
            msg = String(err);
          }
          console.error("[MainCanvas] render failed:", err);
          setRenderError(msg);
        }
      }
    };
    run();
    return () => {
      cancelled = true;
    };
  }, [renderData, dimensions.width, dimensions.height]);

  const zoomIn = useCallback(() => {
    const now = Date.now();
    const step =
      now - lastZoomTimeRef.current < FAST_THRESHOLD_MS
        ? ZOOM_STEP_FAST
        : ZOOM_STEP_SLOW;
    lastZoomTimeRef.current = now;
    setZoom((z) => Math.min(ZOOM_MAX, Math.round((z + step) * 100) / 100));
  }, []);

  const zoomOut = useCallback(() => {
    const now = Date.now();
    const step =
      now - lastZoomTimeRef.current < FAST_THRESHOLD_MS
        ? ZOOM_STEP_FAST
        : ZOOM_STEP_SLOW;
    lastZoomTimeRef.current = now;
    setZoom((z) =>
      Math.max(ZOOM_MIN, Math.round((z - step) * 100) / 100)
    );
  }, []);

  const resetZoom = useCallback(() => setZoom(1), []);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!(e.metaKey || e.ctrlKey)) return;
      if (e.key === "=" || e.key === "+") {
        e.preventDefault();
        zoomIn();
      } else if (e.key === "-") {
        e.preventDefault();
        zoomOut();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [zoomIn, zoomOut]);

  // Wheel zoom: Ctrl/Cmd + scroll, step scales with scroll speed (deltaY)
  useEffect(() => {
    const WHEEL_SENSITIVITY = 0.0008; // deltaY 100 ≈ 8% zoom change
    const onWheel = (e: WheelEvent) => {
      if (!(e.ctrlKey || e.metaKey)) return;
      e.preventDefault();
      const deltaZoom = -e.deltaY * WHEEL_SENSITIVITY;
      setZoom((z) =>
        Math.max(
          ZOOM_MIN,
          Math.min(ZOOM_MAX, Math.round((z + deltaZoom) * 100) / 100)
        )
      );
    };
    window.addEventListener("wheel", onWheel, { passive: false });
    return () => window.removeEventListener("wheel", onWheel);
  }, []);

  return (
    <div
      ref={containerRef}
      style={{
        flex: 1,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        minHeight: 0,
        overflow: "hidden",
        background: "var(--wb-bg-preview)",
      }}
    >
      {renderError ? (
        <div
          style={{
            color: "var(--wb-error-text)",
            fontSize: 12,
            padding: 12,
            maxWidth: 400,
            textAlign: "center",
          }}
        >
          Render failed: {renderError}
        </div>
      ) : !renderData?.layers?.length ? (
        <div
          style={{
            color: "var(--wb-text-muted-soft)",
            fontSize: 12,
          }}
        >
          {renderData
            ? "Canvas has no layers."
            : "No canvas. Send a message to generate."}
        </div>
      ) : (
        <div
          style={{
            flex: 1,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            minHeight: 0,
            overflow: "hidden",
            position: "relative",
          }}
        >
          <div
            ref={canvasHostRef}
            style={{
              width: "100%",
              height: "100%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              transform: `scale(${zoom})`,
              transformOrigin: "center center",
            }}
          />
          <div
            style={{
              position: "absolute",
              bottom: isMobile ? "max(12px, env(safe-area-inset-bottom))" : 12,
              right: isMobile ? "max(12px, env(safe-area-inset-right))" : 12,
              display: "flex",
              alignItems: "center",
              gap: 4,
            }}
          >
            {isMobile && (
              <>
                <button
                  type="button"
                  onClick={zoomOut}
                  aria-label="Zoom out"
                  style={{
                    minWidth: ZOOM_BUTTON_MIN_TOUCH,
                    minHeight: ZOOM_BUTTON_MIN_TOUCH,
                    padding: 8,
                    background: "var(--wb-bg-elevated)",
                    border: "1px solid var(--wb-border)",
                    borderRadius: 8,
                    fontSize: 18,
                    color: "var(--wb-text-muted)",
                    cursor: "pointer",
                    font: "inherit",
                  }}
                >
                  −
                </button>
                <button
                  type="button"
                  onClick={zoomIn}
                  aria-label="Zoom in"
                  style={{
                    minWidth: ZOOM_BUTTON_MIN_TOUCH,
                    minHeight: ZOOM_BUTTON_MIN_TOUCH,
                    padding: 8,
                    background: "var(--wb-bg-elevated)",
                    border: "1px solid var(--wb-border)",
                    borderRadius: 8,
                    fontSize: 18,
                    color: "var(--wb-text-muted)",
                    cursor: "pointer",
                    font: "inherit",
                  }}
                >
                  +
                </button>
              </>
            )}
            <button
              type="button"
              onClick={resetZoom}
              style={{
                minWidth: isMobile ? ZOOM_BUTTON_MIN_TOUCH : undefined,
                minHeight: isMobile ? ZOOM_BUTTON_MIN_TOUCH : undefined,
                padding: isMobile ? "8px 12px" : "4px 8px",
                background: "var(--wb-bg-elevated)",
                border: "1px solid var(--wb-border)",
                borderRadius: isMobile ? 8 : 4,
                fontSize: 12,
                color: "var(--wb-text-muted)",
                cursor: "pointer",
                font: "inherit",
              }}
              title="Click to reset to 100%"
            >
              {Math.round(zoom * 100)}%
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
