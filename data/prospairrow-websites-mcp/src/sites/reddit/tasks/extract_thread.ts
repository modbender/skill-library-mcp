import { Capability, type TaskDefinition } from "../../../framework/types.js";

export const task: TaskDefinition = {
  taskId: "extract_thread",
  capability: Capability.READ_ONLY,
  description: "Stub task for extracting a Reddit thread.",
  run: async (ctx) => {
    return {
      run_id: ctx.runId,
      timestamp: new Date().toISOString(),
      site: "reddit",
      task: "extract_thread",
      thread: null,
      comments: [],
      errors: []
    };
  }
};
