import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// Sync sessions from Gateway → Convex
export const syncFromGateway = mutation({
  args: {
    instanceId: v.string(),
    sessions: v.array(
      v.object({
        sessionKey: v.string(),
        title: v.string(),
        isPinned: v.boolean(),
        lastMessagePreview: v.string(),
        updatedAt: v.number(),
        createdAt: v.number(),
      })
    ),
  },
  handler: async (ctx, { instanceId, sessions }) => {
    for (const session of sessions) {
      const existing = await ctx.db
        .query("sessions")
        .withIndex("by_instanceId_sessionKey", (q) =>
          q.eq("instanceId", instanceId).eq("sessionKey", session.sessionKey)
        )
        .first();

      if (existing) {
        await ctx.db.patch(existing._id, {
          title: session.title,
          isPinned: session.isPinned,
          lastMessagePreview: session.lastMessagePreview,
          updatedAt: session.updatedAt,
        });
      } else {
        await ctx.db.insert("sessions", {
          instanceId,
          ...session,
        });
      }
    }
  },
});

// Get sessions for an instance (used by FastClaw app)
export const getForInstance = query({
  args: { instanceId: v.string() },
  handler: async (ctx, { instanceId }) => {
    return await ctx.db
      .query("sessions")
      .withIndex("by_instanceId", (q) => q.eq("instanceId", instanceId))
      .collect();
  },
});

// Update instance heartbeat
export const heartbeat = mutation({
  args: {
    instanceId: v.string(),
    version: v.optional(v.string()),
  },
  handler: async (ctx, { instanceId, version }) => {
    const instance = await ctx.db
      .query("instances")
      .withIndex("by_instanceId", (q) => q.eq("instanceId", instanceId))
      .first();

    if (instance) {
      await ctx.db.patch(instance._id, {
        status: "online",
        lastSeenAt: Date.now(),
        ...(version ? { version } : {}),
      });
    }
  },
});

// Get instance status (used by FastClaw app)
export const getInstanceStatus = query({
  args: { instanceId: v.string() },
  handler: async (ctx, { instanceId }) => {
    const instance = await ctx.db
      .query("instances")
      .withIndex("by_instanceId", (q) => q.eq("instanceId", instanceId))
      .first();

    if (!instance) return null;

    // Consider offline if no heartbeat in 2 minutes
    const isOnline = Date.now() - instance.lastSeenAt < 2 * 60 * 1000;

    return {
      ...instance,
      status: isOnline ? "online" : "offline",
    };
  },
});
