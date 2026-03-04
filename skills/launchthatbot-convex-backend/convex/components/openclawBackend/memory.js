import { v } from "convex/values";

import { mutation, query } from "./server";

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
    const id = await ctx.db.insert("agentMemory", {
      agentId: args.agentId,
      type: args.type,
      content: args.content,
      tags: args.tags,
      createdAt: Date.now(),
    });
    return id;
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
    const maxResults = args.limit ?? 50;

    if (args.type) {
      const entries = await ctx.db
        .query("agentMemory")
        .withIndex("by_agentId_and_type", (q) =>
          q.eq("agentId", args.agentId).eq("type", args.type),
        )
        .order("desc")
        .take(maxResults);

      return entries.map((entry) => ({
        _id: entry._id,
        type: entry.type,
        content: entry.content,
        tags: entry.tags,
        createdAt: entry.createdAt,
      }));
    }

    const entries = await ctx.db
      .query("agentMemory")
      .withIndex("by_agentId", (q) => q.eq("agentId", args.agentId))
      .order("desc")
      .take(maxResults);

    return entries.map((entry) => ({
      _id: entry._id,
      type: entry.type,
      content: entry.content,
      tags: entry.tags,
      createdAt: entry.createdAt,
    }));
  },
});

export const deleteMemory = mutation({
  args: {
    memoryId: v.id("agentMemory"),
  },
  returns: v.boolean(),
  handler: async (ctx, args) => {
    const entry = await ctx.db.get(args.memoryId);
    if (!entry) return false;
    await ctx.db.delete(args.memoryId);
    return true;
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
    const now = Date.now();
    const existing = await ctx.db
      .query("agentDailyLogs")
      .withIndex("by_agentId_and_date", (q) =>
        q.eq("agentId", args.agentId).eq("date", args.date),
      )
      .unique();

    if (existing) {
      await ctx.db.patch(existing._id, {
        content: `${existing.content}\n\n${args.content}`,
        updatedAt: now,
      });
      return existing._id;
    }

    const id = await ctx.db.insert("agentDailyLogs", {
      agentId: args.agentId,
      date: args.date,
      content: args.content,
      updatedAt: now,
    });
    return id;
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
    const entry = await ctx.db
      .query("agentDailyLogs")
      .withIndex("by_agentId_and_date", (q) =>
        q.eq("agentId", args.agentId).eq("date", args.date),
      )
      .unique();

    if (!entry) return null;
    return {
      date: entry.date,
      content: entry.content,
      updatedAt: entry.updatedAt,
    };
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
    const maxResults = args.limit ?? 30;
    const entries = await ctx.db
      .query("agentDailyLogs")
      .withIndex("by_agentId", (q) => q.eq("agentId", args.agentId))
      .order("desc")
      .take(maxResults);

    return entries.map((entry) => ({
      date: entry.date,
      contentPreview: entry.content.slice(0, 200),
      updatedAt: entry.updatedAt,
    }));
  },
});
