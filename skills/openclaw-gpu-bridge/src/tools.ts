// GPU Bridge - Tool implementations

import { GpuBridgeClient } from "./client.js";
import type { GpuBridgeConfig } from "./types.js";

function jsonResult(data: unknown) {
  return { content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }] };
}

function errorResult(err: unknown) {
  const msg = err instanceof Error ? err.message : String(err);
  return { content: [{ type: "text" as const, text: `GPU Bridge error: ${msg}` }], isError: true };
}

export function createTools(config: GpuBridgeConfig) {
  const client = new GpuBridgeClient(config);

  return {
    async health() {
      try {
        return jsonResult(await client.health());
      } catch (e) {
        return errorResult(e);
      }
    },

    async info() {
      try {
        return jsonResult(await client.info());
      } catch (e) {
        return errorResult(e);
      }
    },

    async status() {
      try {
        return jsonResult(await client.status());
      } catch (e) {
        return errorResult(e);
      }
    },

    async bertscore(
      _id: string,
      params: { candidates: string[]; references: string[]; lang?: string; model_type?: string; model?: string },
    ) {
      try {
        return jsonResult(
          await client.bertscore({
            candidates: params.candidates,
            references: params.references,
            lang: params.lang ?? "en",
            model_type:
              params.model_type ?? params.model ?? config.models?.bertscore ?? "microsoft/deberta-xlarge-mnli",
          }),
        );
      } catch (e) {
        return errorResult(e);
      }
    },

    async embed(_id: string, params: { texts: string[]; model?: string }) {
      try {
        return jsonResult(
          await client.embed({
            texts: params.texts,
            model: params.model ?? config.models?.embed ?? "all-MiniLM-L6-v2",
          }),
        );
      } catch (e) {
        return errorResult(e);
      }
    },
  };
}
