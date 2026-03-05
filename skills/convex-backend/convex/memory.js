import { v } from "convex/values";

import { components } from "./_generated/api";
import { mutation, query } from "./_generated/server";

export const addMemory = mutation({
  args: {
    agentId: v.string(),
    type: v.union(
      v.literal("fact"),
      v.literal("preference"),
      v.literal("decision"),
      v.literal("note"),
    ),
    content: v.string(),
    tags: v.optional(v.array(v.string())),
  },
  returns: v.string(),
  handler: async (ctx, args) => {
    return await ctx.runMutation(components.openclawBackend.memory.addMemory, args);
  },
});

export const searchMemory = query({
  args: {
    agentId: v.string(),
    type: v.optional(
      v.union(
        v.literal("fact"),
        v.literal("preference"),
        v.literal("decision"),
        v.literal("note"),
      ),
    ),
    limit: v.optional(v.number()),
  },
  returns: v.array(
    v.object({
      _id: v.string(),
      type: v.union(
        v.literal("fact"),
        v.literal("preference"),
        v.literal("decision"),
        v.literal("note"),
      ),
      content: v.string(),
      tags: v.optional(v.array(v.string())),
      createdAt: v.number(),
    }),
  ),
  handler: async (ctx, args) => {
    return await ctx.runQuery(components.openclawBackend.memory.searchMemory, args);
  },
});

export const deleteMemory = mutation({
  args: {
    memoryId: v.string(),
  },
  returns: v.boolean(),
  handler: async (ctx, args) => {
    return await ctx.runMutation(components.openclawBackend.memory.deleteMemory, args);
  },
});

export const writeDailyLog = mutation({
  args: {
    agentId: v.string(),
    date: v.string(),
    content: v.string(),
  },
  returns: v.string(),
  handler: async (ctx, args) => {
    return await ctx.runMutation(components.openclawBackend.memory.writeDailyLog, args);
  },
});

export const getDailyLog = query({
  args: {
    agentId: v.string(),
    date: v.string(),
  },
  returns: v.union(
    v.object({
      date: v.string(),
      content: v.string(),
      updatedAt: v.number(),
    }),
    v.null(),
  ),
  handler: async (ctx, args) => {
    return await ctx.runQuery(components.openclawBackend.memory.getDailyLog, args);
  },
});

export const listDailyLogs = query({
  args: {
    agentId: v.string(),
    limit: v.optional(v.number()),
  },
  returns: v.array(
    v.object({
      date: v.string(),
      contentPreview: v.string(),
      updatedAt: v.number(),
    }),
  ),
  handler: async (ctx, args) => {
    return await ctx.runQuery(components.openclawBackend.memory.listDailyLogs, args);
  },
});
