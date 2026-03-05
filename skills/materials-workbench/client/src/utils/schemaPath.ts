import type {
  RenderData,
  ChildRenderers,
  ImgRenderData,
  TextRenderData,
  ContainerRenderData,
  ShapeRenderData,
} from "declare-render/browser";

export type Layer =
  | ImgRenderData
  | TextRenderData
  | ContainerRenderData
  | ShapeRenderData;

/**
 * Get the layers array at a given path.
 * path=[] returns schema.layers.
 * path=[0] returns schema.layers[0].layers (if container), etc.
 */
export function getLayersAtPath(
  schema: RenderData,
  path: number[]
): ChildRenderers | null {
  if (path.length === 0) return schema.layers;
  let current: ChildRenderers = schema.layers;
  for (let i = 0; i < path.length; i++) {
    const idx = path[i];
    const layer = current[idx];
    if (!layer) return null;
    if (layer.type !== "container") return null;
    current = layer.layers;
  }
  return current;
}

/**
 * Get a layer by path. path=[0] means schema.layers[0].
 * path=[0, 1] means schema.layers[0].layers[1] (when layers[0] is container).
 */
export function getLayerByPath(
  schema: RenderData,
  path: number[]
): Layer | null {
  if (path.length === 0) return null;
  const parentPath = path.slice(0, -1);
  const lastIdx = path[path.length - 1];
  const layers = getLayersAtPath(schema, parentPath);
  if (!layers || lastIdx < 0 || lastIdx >= layers.length) return null;
  return layers[lastIdx];
}

/**
 * Immutably update a layer at path.
 */
export function updateLayerByPath(
  schema: RenderData,
  path: number[],
  updater: (layer: Layer) => Layer
): RenderData {
  if (path.length === 0) return schema;

  const updateLayers = (
    layers: ChildRenderers,
    depth: number
  ): ChildRenderers => {
    const idx = path[depth];
    if (depth === path.length - 1) {
      const layer = layers[idx];
      if (!layer) return layers;
      const next = [...layers];
      next[idx] = updater(layer);
      return next;
    }
    const layer = layers[idx];
    if (!layer || layer.type !== "container") return layers;
    const next = [...layers];
    next[idx] = {
      ...layer,
      layers: updateLayers(layer.layers, depth + 1),
    };
    return next;
  };

  return {
    ...schema,
    layers: updateLayers(schema.layers, 0),
  };
}

/**
 * Update root schema (canvas dimensions, etc).
 */
export function updateSchema(
  schema: RenderData,
  updater: (s: RenderData) => Partial<RenderData>
): RenderData {
  return { ...schema, ...updater(schema) };
}

/**
 * Set the layers array at a parent path (immutable). parentPath=[] means root schema.layers.
 */
function setLayersAtPath(
  schema: RenderData,
  parentPath: number[],
  newLayers: ChildRenderers
): RenderData {
  if (parentPath.length === 0) {
    return { ...schema, layers: newLayers };
  }
  const update = (
    layers: ChildRenderers,
    pathIdx: number[]
  ): ChildRenderers => {
    if (pathIdx.length === 1) {
      const i = pathIdx[0];
      const l = layers[i];
      if (!l || l.type !== "container") return layers;
      return layers.map((lay, j) => {
        if (j !== i) return lay;
        const container = lay as ContainerRenderData;
        return { ...container, layers: newLayers };
      });
    }
    const i = pathIdx[0];
    const l = layers[i];
    if (!l || l.type !== "container") return layers;
    return layers.map((lay, j) => {
      if (j !== i) return lay;
      const container = lay as ContainerRenderData;
      return { ...container, layers: update(container.layers, pathIdx.slice(1)) };
    });
  };
  return { ...schema, layers: update(schema.layers, parentPath) };
}

/**
 * Move a layer by delta in its sibling order. Clamps to [0, length-1].
 * Returns new schema.
 */
export function moveLayerByPath(
  schema: RenderData,
  path: number[],
  delta: number
): RenderData {
  if (path.length === 0) return schema;
  const parentPath = path.slice(0, -1);
  const idx = path[path.length - 1];
  const layers = getLayersAtPath(schema, parentPath);
  if (!layers || idx < 0 || idx >= layers.length) return schema;
  const newIdx = Math.max(0, Math.min(layers.length - 1, idx + delta));
  if (newIdx === idx) return schema;
  const newLayers = [...layers];
  const a = newLayers[idx];
  const b = newLayers[newIdx];
  newLayers[idx] = b;
  newLayers[newIdx] = a;
  return setLayersAtPath(schema, parentPath, newLayers);
}

/**
 * Remove the layer at path. Returns new schema.
 */
export function deleteLayerByPath(
  schema: RenderData,
  path: number[]
): RenderData {
  if (path.length === 0) return schema;
  const parentPath = path.slice(0, -1);
  const idx = path[path.length - 1];
  const layers = getLayersAtPath(schema, parentPath);
  if (!layers || idx < 0 || idx >= layers.length) return schema;
  const newLayers = layers.filter((_, i) => i !== idx);
  return setLayersAtPath(schema, parentPath, newLayers);
}
