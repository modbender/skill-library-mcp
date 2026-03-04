/**
 * Client-side rendering using declare-render browser engine.
 */
import { Renderer, type RenderData } from "declare-render/browser";

/**
 * Render RenderData to a data URL (for img src display).
 */
export async function renderToDataUrl(schema: RenderData): Promise<string> {
  const renderer = new Renderer(schema);
  const blob = (await renderer.draw()) as Blob;
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}
