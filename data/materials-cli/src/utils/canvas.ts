import { readFile, writeFile, mkdir } from 'fs/promises';
import { dirname } from 'path';
import { existsSync } from 'fs';

type RenderFunction = (schema: any, options: any) => Promise<Buffer>;

let renderFn: RenderFunction | null = null;

async function loadDeclareRender(): Promise<RenderFunction> {
  if (renderFn) return renderFn;

  try {
    const nodeModule = await import('declare-render/node');
    const { Renderer } = nodeModule;

    if (Renderer) {
      // declare-render/node exports Renderer(schema) only; it uses NodeCanvasEngine internally.
      // Schema must have width, height; output.type controls png/jpg.
      // Type assertion: package types point at base Renderer(schema, engine); node entry uses Renderer(schema).
      const NodeRenderer = Renderer as unknown as new (schema: object) => { draw: () => Promise<Buffer | Blob> };
      renderFn = async (schema: any, options: any) => {
        const schemaWithOptions = {
          ...schema,
          width: options.width ?? schema.width ?? 800,
          height: options.height ?? schema.height ?? 600,
          output: { type: (options.format === 'jpg' ? 'jpg' : 'png') as 'png' | 'jpg' },
        };
        const renderer = new NodeRenderer(schemaWithOptions);
        const buffer = await renderer.draw();
        return Buffer.isBuffer(buffer) ? buffer : Buffer.from(await (buffer as Blob).arrayBuffer());
      };
      return renderFn;
    }

    throw new Error('declare-render module not properly exported');
  } catch (error: any) {
    const errMsg = error?.message || String(error);
    const originalStack = error?.stack;
    if (errMsg.includes('canvas') || errMsg.includes('Cannot find module') ||
        errMsg.includes('MODULE_NOT_FOUND') || errMsg.includes('node-canvas')) {
      const help =
        `Failed to load declare-render (requires the canvas package).\n\n` +
        `Original error: ${errMsg}\n\n` +
        `This is likely because the canvas package is not properly installed.\n` +
        `Please visit the canvas (node-canvas) installation guide for help:\n` +
        `  https://github.com/Automattic/node-canvas#installation\n\n` +
        `Common solutions:\n` +
        `- macOS: brew install pkg-config cairo pango jpeg giflib librsvg pixman\n` +
        `- Ubuntu/Debian: sudo apt-get install libcairo2-dev libjpeg-dev libpango1.0-dev libgif-dev librsvg2-dev\n` +
        `- Windows: npm install --global --production windows-build-tools\n\n` +
        `Then reinstall: pnpm install`;
      const e = new Error(help);
      if (originalStack) e.cause = error;
      throw e;
    }
    throw error;
  }
}

export interface RenderOptions {
  schemaPath?: string;
  schemaData?: object;
  outputPath: string;
  format: 'png' | 'jpg';
  width: number;
  height: number;
}

export async function renderSchema(options: RenderOptions): Promise<void> {
  const render = await loadDeclareRender();

  let schemaData: object;

  if (options.schemaPath) {
    const content = await readFile(options.schemaPath, 'utf-8');
    try {
      schemaData = JSON.parse(content);
    } catch {
      throw new Error(`Invalid JSON in schema file: ${options.schemaPath}`);
    }
  } else if (options.schemaData) {
    schemaData = options.schemaData;
  } else {
    throw new Error('Either schemaPath or schemaData must be provided');
  }

  // Schema normalization is now handled by declare-render internally

  const buffer = await render(schemaData, {
    width: options.width,
    height: options.height,
    format: options.format,
  });

  const outputDir = dirname(options.outputPath);
  if (!existsSync(outputDir)) {
    await mkdir(outputDir, { recursive: true });
  }

  await writeFile(options.outputPath, buffer);
}

export async function saveSchema(schemaData: object, outputPath: string): Promise<void> {
  const outputDir = dirname(outputPath);
  if (!existsSync(outputDir)) {
    await mkdir(outputDir, { recursive: true });
  }
  await writeFile(outputPath, JSON.stringify(schemaData, null, 2), 'utf-8');
}

export async function loadSchema(schemaPath: string): Promise<object> {
  const content = await readFile(schemaPath, 'utf-8');
  try {
    return JSON.parse(content);
  } catch {
    throw new Error(`Invalid JSON in schema file: ${schemaPath}`);
  }
}
