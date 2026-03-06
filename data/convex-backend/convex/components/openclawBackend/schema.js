import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  agentMemory: defineTable({
    agentId: v.string(),
    type: v.union(
      v.literal("fact"),
      v.literal("preference"),
      v.literal("decision"),
      v.literal("note"),
    ),
    content: v.string(),
    tags: v.optional(v.array(v.string())),
    createdAt: v.number(),
  })
    .index("by_agentId", ["agentId"])
    .index("by_agentId_and_type", ["agentId", "type"]),

  agentDailyLogs: defineTable({
    agentId: v.string(),
    date: v.string(),
    content: v.string(),
    updatedAt: v.number(),
  })
    .index("by_agentId", ["agentId"])
    .index("by_agentId_and_date", ["agentId", "date"]),
});
