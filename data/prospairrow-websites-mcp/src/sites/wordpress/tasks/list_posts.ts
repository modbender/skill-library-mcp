import { Capability, type TaskDefinition } from "../../../framework/types.js";

export const task: TaskDefinition = {
  taskId: "list_posts",
  capability: Capability.READ_ONLY,
  description: "Stub task for listing WordPress posts.",
  run: async (ctx) => {
    return {
      run_id: ctx.runId,
      timestamp: new Date().toISOString(),
      site: "wordpress",
      task: "list_posts",
      posts: [],
      errors: []
    };
  }
};
