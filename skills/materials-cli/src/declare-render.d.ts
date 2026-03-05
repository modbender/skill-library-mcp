declare module 'declare-render/node.js' {
  export class Renderer {
    constructor(schema: any);
    draw(): Promise<Buffer | Blob>;
  }
}
