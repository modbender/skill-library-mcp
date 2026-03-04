// @elvatis/openclaw-gpu-bridge - Plugin entry

import { createTools } from "./tools.js";
import type { GpuBridgeConfig } from "./types.js";

export default function (api: any) {
  const config = api.config as GpuBridgeConfig;
  const tools = createTools(config);

  api.registerTool({
    name: "gpu_health",
    description: "Check if the remote GPU service is reachable and which device it's using",
    parameters: { type: "object", properties: {}, required: [] },
    async execute() {
      return tools.health();
    },
  });

  api.registerTool({
    name: "gpu_info",
    description: "Get GPU device info: name, VRAM, PyTorch version, loaded models",
    parameters: { type: "object", properties: {}, required: [] },
    async execute() {
      return tools.info();
    },
  });

  api.registerTool({
    name: "gpu_status",
    description: "Get queue and job progress from the remote GPU service",
    parameters: { type: "object", properties: {}, required: [] },
    async execute() {
      return tools.status();
    },
  });

  api.registerTool({
    name: "gpu_bertscore",
    description:
      "Compute BERTScore between candidate and reference texts. Returns precision, recall, and F1 arrays.",
    parameters: {
      type: "object",
      properties: {
        candidates: {
          type: "array",
          items: { type: "string" },
          description: "Candidate texts to evaluate",
        },
        references: {
          type: "array",
          items: { type: "string" },
          description: "Reference texts to compare against (same length as candidates)",
        },
        lang: {
          type: "string",
          description: "Language code (default: en)",
        },
        model_type: {
          type: "string",
          description: "BERTScore model (optional, default: microsoft/deberta-xlarge-mnli)",
        },
        model: {
          type: "string",
          description: "Alias for model_type (optional)",
        },
      },
      required: ["candidates", "references"],
    },
    async execute(id: string, params: any) {
      return tools.bertscore(id, params);
    },
  });

  api.registerTool({
    name: "gpu_embed",
    description:
      "Generate text embeddings using sentence-transformers on the remote GPU. Returns float arrays.",
    parameters: {
      type: "object",
      properties: {
        texts: {
          type: "array",
          items: { type: "string" },
          description: "Texts to embed",
        },
        model: {
          type: "string",
          description: "Embedding model (optional, default: all-MiniLM-L6-v2)",
        },
      },
      required: ["texts"],
    },
    async execute(id: string, params: any) {
      return tools.embed(id, params);
    },
  });
}
