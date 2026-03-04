import {
  useRef,
  useEffect,
  useCallback,
  useState,
  useLayoutEffect,
} from "react";
import {
  Renderer,
  getEditablePoints,
  updateShapePoint,
  type RenderData,
  type LayerBounds,
  type EditablePoint,
} from "declare-render/browser";
import {
  getLayerByPath,
  updateLayerByPath,
  moveLayerByPath,
  deleteLayerByPath,
  getLayersAtPath,
} from "../utils/schemaPath";
import { createPortal } from "react-dom";

export interface InteractiveCanvasProps {
  schema: RenderData | null;
  onSchemaChange: (schema: RenderData) => void;
  activeLayerPath: number[] | null;
  onActiveLayerChange: (path: number[] | null) => void;
}

type ResizeHandle = "nw" | "n" | "ne" | "e" | "se" | "s" | "sw" | "w";

type DragMode =
  | { type: "layer"; path: number[] }
  | { type: "shapePoint"; path: number[]; point: EditablePoint }
  | {
      type: "resize";
      path: number[];
      handle: ResizeHandle;
      startX: number;
      startY: number;
      startWidth: number;
      startHeight: number;
    }
  | {
      type: "rotate";
      path: number[];
      startAngle: number;
      startPointerAngle: number;
    };

const HANDLE_SIZE = 8;
const HANDLE_HIT_RADIUS = 12;
const ROTATE_HANDLE_OFFSET = 24;

function round2(n: number): number {
  return Math.round(n * 100) / 100;
}

function boundsMatchPath(a: number[], b: number[]): boolean {
  if (a.length !== b.length) return false;
  return a.every((v, i) => v === b[i]);
}

export default function InteractiveCanvas({
  schema,
  onSchemaChange,
  activeLayerPath,
  onActiveLayerChange,
}: InteractiveCanvasProps) {
  const canvasRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const viewportRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<Renderer | null>(null);
  const [layerBounds, setLayerBounds] = useState<LayerBounds[]>([]);
  const [dragMode, setDragMode] = useState<DragMode | null>(null);
  const [dragStart, setDragStart] = useState<{ x: number; y: number } | null>(
    null
  );
  const [dragStartValues, setDragStartValues] = useState<Record<string, number>>(
    {}
  );
  const [contextMenu, setContextMenu] = useState<{
    path: number[];
    clientX: number;
    clientY: number;
  } | null>(null);

  const canvasWidth = schema?.width ?? 800;
  const canvasHeight = schema?.height ?? 600;

  // Convert mouse position (client coords) to canvas coordinates.
  // Use the viewport div (which wraps the canvas/SVG) for accurate hit testing.
  const toCanvasCoords = useCallback(
    (clientX: number, clientY: number): { x: number; y: number } | null => {
      const viewport = viewportRef.current ?? containerRef.current;
      if (!viewport) return null;
      const rect = viewport.getBoundingClientRect();
      const scaleX = rect.width / canvasWidth;
      const scaleY = rect.height / canvasHeight;
      const scale = Math.min(scaleX, scaleY);
      const displayW = canvasWidth * scale;
      const displayH = canvasHeight * scale;
      const offsetX = (rect.width - displayW) / 2;
      const offsetY = (rect.height - displayH) / 2;
      const localX = clientX - rect.left - offsetX;
      const localY = clientY - rect.top - offsetY;
      return { x: localX / scale, y: localY / scale };
    },
    [canvasWidth, canvasHeight]
  );

  // Hit test: find topmost layer containing (x, y)
  const hitTest = useCallback(
    (canvasX: number, canvasY: number): LayerBounds | null => {
      // Reverse order: last drawn = topmost
      for (let i = layerBounds.length - 1; i >= 0; i--) {
        const lb = layerBounds[i];
        const { x1, y1, x2, y2 } = lb.bounds;
        if (
          canvasX >= x1 &&
          canvasX <= x2 &&
          canvasY >= y1 &&
          canvasY <= y2
        ) {
          return lb;
        }
      }
      return null;
    },
    [layerBounds]
  );

  const renderAndCollectBounds = useCallback(async () => {
    if (!schema?.layers?.length) {
      setLayerBounds([]);
      if (canvasRef.current) canvasRef.current.innerHTML = "";
      return;
    }
    try {
      const r = new Renderer(schema);
      rendererRef.current = r;
      await r.render();
      const bounds = await r.layoutAndGetLayerBounds();
      setLayerBounds(bounds);

      const el = r.getCanvasElement();
      const container = canvasRef.current;
      if (el && container) {
        container.innerHTML = "";
        el.style.display = "block";
        el.style.maxWidth = "100%";
        el.style.maxHeight = "100%";
        el.style.objectFit = "contain";
        container.appendChild(el);
      }
    } catch (err) {
      console.error("Render failed:", err);
      setLayerBounds([]);
    }
  }, [schema]);

  useLayoutEffect(() => {
    renderAndCollectBounds();
  }, [renderAndCollectBounds]);

  const activeLayer = schema && activeLayerPath ? getLayerByPath(schema, activeLayerPath) : null;
  const activeBounds = layerBounds.find((lb) =>
    boundsMatchPath(lb.path, activeLayerPath ?? [])
  )?.bounds;
  const shapePoints =
    activeLayer?.type === "shape"
      ? getEditablePoints(activeLayer)
      : [];
  const hasWidthHeight =
    activeBounds && activeLayer && activeLayer.type !== "shape";
  const hasRotate = activeLayer && "rotate" in activeLayer;

  const handlePointerDown = useCallback(
    (e: React.PointerEvent) => {
      if (!schema) return;
      const coords = toCanvasCoords(e.clientX, e.clientY);
      if (!coords) return;

      const layer = getLayerByPath(schema, activeLayerPath ?? []);
      const bounds = activeBounds;
      const isShape = layer?.type === "shape";

      // 1. Shape point handles
      if (isShape && activeLayerPath) {
        const points = getEditablePoints(layer);
        for (const pt of points) {
          const layerObj = getLayerByPath(schema, activeLayerPath);
          if (!layerObj || layerObj.type !== "shape") continue;
          const layerX = layerObj.x;
          const layerY = layerObj.y;
          const canvasX = layerX + pt.x;
          const canvasY = layerY + pt.y;
          const dx = coords.x - canvasX;
          const dy = coords.y - canvasY;
          if (dx * dx + dy * dy <= HANDLE_HIT_RADIUS * HANDLE_HIT_RADIUS) {
            setDragMode({ type: "shapePoint", path: activeLayerPath, point: pt });
            setDragStart({ x: coords.x, y: coords.y });
            (e.currentTarget as Element).setPointerCapture(e.pointerId);
            return;
          }
        }
      }

      // 2. Resize handles
      if (bounds && hasWidthHeight && layer && activeLayerPath) {
        const x1 = bounds.x1;
        const y1 = bounds.y1;
        const x2 = bounds.x2;
        const y2 = bounds.y2;
        const cx = (x1 + x2) / 2;
        const cy = (y1 + y2) / 2;
        const handles: { h: ResizeHandle; x: number; y: number }[] = [
          { h: "nw", x: x1, y: y1 },
          { h: "n", x: cx, y: y1 },
          { h: "ne", x: x2, y: y1 },
          { h: "e", x: x2, y: cy },
          { h: "se", x: x2, y: y2 },
          { h: "s", x: cx, y: y2 },
          { h: "sw", x: x1, y: y2 },
          { h: "w", x: x1, y: cy },
        ];
        const w = (layer as { width: number }).width ?? x2 - x1;
        const h = (layer as { height: number }).height ?? y2 - y1;
        for (const { h: handle, x, y } of handles) {
          const dx = coords.x - x;
          const dy = coords.y - y;
          if (dx * dx + dy * dy <= HANDLE_HIT_RADIUS * HANDLE_HIT_RADIUS) {
            setDragMode({
              type: "resize",
              path: activeLayerPath,
              handle,
              startX: (layer as { x: number }).x,
              startY: (layer as { y: number }).y,
              startWidth: w,
              startHeight: h,
            });
            setDragStart({ x: coords.x, y: coords.y });
            (e.currentTarget as Element).setPointerCapture(e.pointerId);
            return;
          }
        }
      }

      // 3. Rotation handle
      if (bounds && hasRotate && layer && activeLayerPath) {
        const cx = (bounds.x1 + bounds.x2) / 2;
        const ry = bounds.y1 - ROTATE_HANDLE_OFFSET;
        const dx = coords.x - cx;
        const dy = coords.y - ry;
        if (dx * dx + dy * dy <= HANDLE_HIT_RADIUS * HANDLE_HIT_RADIUS) {
          const startAngle = (layer as { rotate?: number }).rotate ?? 0;
          const startPointerAngle = Math.atan2(
            coords.y - (bounds.y1 + bounds.y2) / 2,
            coords.x - cx
          );
          setDragMode({
            type: "rotate",
            path: activeLayerPath,
            startAngle,
            startPointerAngle,
          });
          setDragStart({ x: coords.x, y: coords.y });
          (e.currentTarget as Element).setPointerCapture(e.pointerId);
          return;
        }
      }

      // 4. Layer bounds (move)
      const hit = hitTest(coords.x, coords.y);
      if (hit) {
        onActiveLayerChange(hit.path);
        setDragMode({ type: "layer", path: hit.path });
        const hitLayer = getLayerByPath(schema, hit.path);
        if (hitLayer) {
          setDragStart({ x: coords.x, y: coords.y });
          setDragStartValues({ x: hitLayer.x, y: hitLayer.y });
        }
        (e.currentTarget as Element).setPointerCapture(e.pointerId);
      } else {
        onActiveLayerChange(null);
      }
    },
    [
      schema,
      activeLayerPath,
      activeBounds,
      hasWidthHeight,
      hasRotate,
      toCanvasCoords,
      hitTest,
      onActiveLayerChange,
    ]
  );

  const handlePointerMove = useCallback(
    (e: React.PointerEvent) => {
      if (!schema || !dragMode || !dragStart) return;
      const coords = toCanvasCoords(e.clientX, e.clientY);
      if (!coords) return;

      const dx = coords.x - dragStart.x;
      const dy = coords.y - dragStart.y;

      if (dragMode.type === "layer") {
        const layer = getLayerByPath(schema, dragMode.path);
        if (!layer) return;
        onSchemaChange(
          updateLayerByPath(schema, dragMode.path, () => ({
            ...layer,
            x: round2(dragStartValues.x + dx),
            y: round2(dragStartValues.y + dy),
          }))
        );
      } else if (dragMode.type === "shapePoint") {
        const layer = getLayerByPath(schema, dragMode.path);
        if (!layer || layer.type !== "shape") return;
        const pt = dragMode.point;
        const newLocalX = round2(pt.x + dx);
        const newLocalY = round2(pt.y + dy);
        const shapes = [...layer.shapes];
        const cmd = shapes[pt.commandIndex];
        const updated = updateShapePoint(cmd, pt.pointKey, newLocalX, newLocalY);
        shapes[pt.commandIndex] = updated;
        onSchemaChange(
          updateLayerByPath(schema, dragMode.path, () => ({
            ...layer,
            shapes,
          }))
        );
      } else if (dragMode.type === "resize") {
        const layer = getLayerByPath(schema, dragMode.path);
        if (!layer) return;
        let { x, y, width, height } = {
          x: dragMode.startX,
          y: dragMode.startY,
          width: dragMode.startWidth,
          height: dragMode.startHeight,
        };
        const h = dragMode.handle;
        if (h.includes("e")) width = Math.max(1, width + dx);
        if (h.includes("w")) {
          const dw = Math.min(dx, width - 1);
          x += dw;
          width = Math.max(1, width - dw);
        }
        if (h.includes("s")) height = Math.max(1, height + dy);
        if (h.includes("n")) {
          const dh = Math.min(dy, height - 1);
          y += dh;
          height = Math.max(1, height - dh);
        }
        onSchemaChange(
          updateLayerByPath(schema, dragMode.path, () => ({
            ...layer,
            x: round2(x),
            y: round2(y),
            width: round2(width),
            height: round2(height),
          }))
        );
      } else if (dragMode.type === "rotate") {
        const layer = getLayerByPath(schema, dragMode.path);
        if (!layer) return;
        const bounds = layerBounds.find((lb) =>
          boundsMatchPath(lb.path, dragMode.path)
        )?.bounds;
        if (!bounds) return;
        const cx = (bounds.x1 + bounds.x2) / 2;
        const cy = (bounds.y1 + bounds.y2) / 2;
        const curAngle = Math.atan2(coords.y - cy, coords.x - cx);
        const deltaDeg =
          ((curAngle - dragMode.startPointerAngle) * 180) / Math.PI;
        const newRotate = dragMode.startAngle + deltaDeg;
        onSchemaChange(
          updateLayerByPath(schema, dragMode.path, () => ({
            ...layer,
            rotate: round2(newRotate),
          }))
        );
      }
    },
    [
      schema,
      dragMode,
      dragStart,
      dragStartValues,
      layerBounds,
      toCanvasCoords,
      onSchemaChange,
    ]
  );

  const handlePointerUp = useCallback(() => {
    setDragMode(null);
    setDragStart(null);
    setDragStartValues({});
  }, []);

  useEffect(() => {
    const handler = () => handlePointerUp();
    window.addEventListener("pointerup", handler);
    window.addEventListener("pointercancel", handler);
    return () => {
      window.removeEventListener("pointerup", handler);
      window.removeEventListener("pointercancel", handler);
    };
  }, [handlePointerUp]);

  const handleContextMenu = useCallback(
    (e: React.MouseEvent) => {
      if (!schema) return;
      e.preventDefault();
      const coords = toCanvasCoords(e.clientX, e.clientY);
      if (!coords) return;
      const hit = hitTest(coords.x, coords.y);
      if (hit) {
        onActiveLayerChange(hit.path);
        setContextMenu({
          path: hit.path,
          clientX: e.clientX,
          clientY: e.clientY,
        });
      } else {
        setContextMenu(null);
      }
    },
    [schema, toCanvasCoords, hitTest, onActiveLayerChange]
  );

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setContextMenu(null);
        return;
      }
      if (!schema || !activeLayerPath) return;
      if (e.key === "Delete" || e.key === "Backspace") {
        e.preventDefault();
        onSchemaChange(deleteLayerByPath(schema, activeLayerPath));
        onActiveLayerChange(null);
        setContextMenu(null);
      } else if (
        (e.ctrlKey || e.metaKey) &&
        e.key === "]"
      ) {
        e.preventDefault();
        onSchemaChange(moveLayerByPath(schema, activeLayerPath, 1));
      } else if (
        (e.ctrlKey || e.metaKey) &&
        e.key === "["
      ) {
        e.preventDefault();
        onSchemaChange(moveLayerByPath(schema, activeLayerPath, -1));
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [
    schema,
    activeLayerPath,
    onSchemaChange,
    onActiveLayerChange,
  ]);

  useEffect(() => {
    const closeMenu = () => setContextMenu(null);
    if (contextMenu) {
      window.addEventListener("click", closeMenu, { once: true });
      return () => window.removeEventListener("click", closeMenu);
    }
  }, [contextMenu]);

  if (!schema) {
    return (
      <div
        ref={containerRef}
        style={{
          flex: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "var(--wb-text-muted-soft)",
          fontSize: 14,
        }}
      >
        No schema. Send a message or edit JSON to generate.
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerLeave={handlePointerUp}
      style={{
        flex: 1,
        overflow: "auto",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 16,
        cursor: dragMode ? "grabbing" : "pointer",
      }}
    >
      <div
        ref={viewportRef}
        onContextMenu={handleContextMenu}
        style={{
          position: "relative",
          maxWidth: "100%",
          maxHeight: "70vh",
          boxSizing: "border-box",
          border: "1px solid var(--wb-border)",
        }}
      >
        <div
          ref={canvasRef}
          style={{
            display: "block",
            maxWidth: "100%",
            maxHeight: "70vh",
            objectFit: "contain",
          }}
        />
        {(activeBounds || shapePoints.length > 0) && (
          <svg
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: "100%",
              pointerEvents: "none",
            }}
            viewBox={`0 0 ${canvasWidth} ${canvasHeight}`}
            preserveAspectRatio="xMidYMid meet"
          >
            {activeBounds && (
              <>
                <rect
                  x={activeBounds.x1}
                  y={activeBounds.y1}
                  width={activeBounds.x2 - activeBounds.x1}
                  height={activeBounds.y2 - activeBounds.y1}
                  fill="none"
                  stroke="var(--wb-btn-primary-bg)"
                  strokeWidth={2}
                  strokeDasharray="4 2"
                />
                {hasWidthHeight && (
                  <>
                    {(
                      [
                        ["nw", activeBounds.x1, activeBounds.y1],
                        ["n", (activeBounds.x1 + activeBounds.x2) / 2, activeBounds.y1],
                        ["ne", activeBounds.x2, activeBounds.y1],
                        ["e", activeBounds.x2, (activeBounds.y1 + activeBounds.y2) / 2],
                        ["se", activeBounds.x2, activeBounds.y2],
                        ["s", (activeBounds.x1 + activeBounds.x2) / 2, activeBounds.y2],
                        ["sw", activeBounds.x1, activeBounds.y2],
                        ["w", activeBounds.x1, (activeBounds.y1 + activeBounds.y2) / 2],
                      ] as const
                    ).map(([_, x, y]) => (
                      <rect
                        key={_}
                        x={x - HANDLE_SIZE / 2}
                        y={y - HANDLE_SIZE / 2}
                        width={HANDLE_SIZE}
                        height={HANDLE_SIZE}
                        fill="var(--wb-bg)"
                        stroke="var(--wb-btn-primary-bg)"
                        strokeWidth={2}
                      />
                    ))}
                  </>
                )}
                {hasRotate && (
                  <circle
                    cx={(activeBounds.x1 + activeBounds.x2) / 2}
                    cy={activeBounds.y1 - ROTATE_HANDLE_OFFSET}
                    r={HANDLE_SIZE / 2}
                    fill="var(--wb-bg)"
                    stroke="var(--wb-btn-primary-bg)"
                    strokeWidth={2}
                  />
                )}
              </>
            )}
            {shapePoints.map((pt, i) => {
              const layer = activeLayer as { x: number; y: number };
              const cx = layer.x + pt.x;
              const cy = layer.y + pt.y;
              return (
                <circle
                  key={`pt-${i}`}
                  cx={cx}
                  cy={cy}
                  r={5}
                  fill="none"
                  stroke="var(--wb-btn-primary-bg)"
                  strokeWidth={2}
                />
              );
            })}
          </svg>
        )}
      </div>
      {contextMenu &&
        createPortal(
          <div
            role="menu"
            onClick={(e) => e.stopPropagation()}
            style={{
              position: "fixed",
              left: contextMenu.clientX + 4,
              top: contextMenu.clientY + 4,
              minWidth: 160,
              padding: "4px 0",
              background: "var(--wb-bg-elevated)",
              border: "1px solid var(--wb-border)",
              borderRadius: 6,
              boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
              zIndex: 10000,
            }}
          >
            <ContextMenuButtons
              schema={schema}
              path={contextMenu.path}
              onSchemaChange={onSchemaChange}
              onActiveLayerChange={onActiveLayerChange}
              onClose={() => setContextMenu(null)}
            />
          </div>,
          document.body
        )}
    </div>
  );
}

function ContextMenuButtons({
  schema,
  path,
  onSchemaChange,
  onActiveLayerChange,
  onClose,
}: {
  schema: RenderData;
  path: number[];
  onSchemaChange: (schema: RenderData) => void;
  onActiveLayerChange: (path: number[] | null) => void;
  onClose: () => void;
}) {
  const parentPath = path.slice(0, -1);
  const idx = path[path.length - 1];
  const layers = getLayersAtPath(schema, parentPath);
  const canMoveUp = layers != null && idx < layers.length - 1;
  const canMoveDown = layers != null && idx > 0;

  const menuItemStyle: React.CSSProperties = {
    display: "block",
    width: "100%",
    padding: "8px 12px",
    border: "none",
    background: "transparent",
    color: "var(--wb-text)",
    fontSize: 13,
    textAlign: "left",
    cursor: "pointer",
  };

  return (
    <>
      <button
        type="button"
        style={menuItemStyle}
        disabled={!canMoveUp}
        onClick={() => {
          onSchemaChange(moveLayerByPath(schema, path, 1));
          onClose();
        }}
      >
        Bring forward
      </button>
      <button
        type="button"
        style={menuItemStyle}
        disabled={!canMoveDown}
        onClick={() => {
          onSchemaChange(moveLayerByPath(schema, path, -1));
          onClose();
        }}
      >
        Send backward
      </button>
      <button
        type="button"
        style={menuItemStyle}
        onClick={() => {
          onSchemaChange(deleteLayerByPath(schema, path));
          onActiveLayerChange(null);
          onClose();
        }}
      >
        Delete
      </button>
    </>
  );
}

export function useShapePoints(
  schema: RenderData | null,
  activeLayerPath: number[] | null
): EditablePoint[] {
  if (!schema || !activeLayerPath) return [];
  const layer = getLayerByPath(schema, activeLayerPath);
  if (!layer || layer.type !== "shape") return [];
  return getEditablePoints(layer);
}
