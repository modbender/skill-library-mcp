import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// Send a message from FastClaw app → OpenClaw
export const sendFromApp = mutation({
  args: {
    instanceId: v.string(),
    sessionKey: v.string(),
    content: v.string(),
    deviceId: v.string(),
  },
  handler: async (ctx, { instanceId, sessionKey, content, deviceId }) => {
    // Verify device is paired to this instance
    const device = await ctx.db
      .query("devices")
      .withIndex("by_deviceId", (q) => q.eq("deviceId", deviceId))
      .first();

    if (!device || device.instanceId !== instanceId) {
      throw new Error("Device not paired to this instance");
    }

    await ctx.db.insert("messages", {
      instanceId,
      sessionKey,
      role: "user",
      content,
      timestamp: Date.now(),
      source: "fastclaw",
      synced: false,
    });

    // Update session preview
    const session = await ctx.db
      .query("sessions")
      .withIndex("by_instanceId_sessionKey", (q) =>
        q.eq("instanceId", instanceId).eq("sessionKey", sessionKey)
      )
      .first();

    if (session) {
      await ctx.db.patch(session._id, {
        lastMessagePreview: content.slice(0, 100),
        updatedAt: Date.now(),
      });
    }
  },
});

// Relay pushes a message from Gateway → Convex
export const pushFromGateway = mutation({
  args: {
    instanceId: v.string(),
    sessionKey: v.string(),
    role: v.union(v.literal("user"), v.literal("assistant"), v.literal("system")),
    content: v.string(),
    timestamp: v.number(),
  },
  handler: async (ctx, { instanceId, sessionKey, role, content, timestamp }) => {
    await ctx.db.insert("messages", {
      instanceId,
      sessionKey,
      role,
      content,
      timestamp,
      source: "gateway",
      synced: true,
    });

    // Update session
    const session = await ctx.db
      .query("sessions")
      .withIndex("by_instanceId_sessionKey", (q) =>
        q.eq("instanceId", instanceId).eq("sessionKey", sessionKey)
      )
      .first();

    if (session) {
      await ctx.db.patch(session._id, {
        lastMessagePreview: content.slice(0, 100),
        updatedAt: Date.now(),
      });
    }
  },
});

// Get messages for a session (used by FastClaw app)
export const getSessionMessages = query({
  args: {
    instanceId: v.string(),
    sessionKey: v.string(),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, { instanceId, sessionKey, limit }) => {
    const messages = await ctx.db
      .query("messages")
      .withIndex("by_session", (q) =>
        q.eq("instanceId", instanceId).eq("sessionKey", sessionKey)
      )
      .order("desc")
      .take(limit ?? 50);

    return messages.reverse();
  },
});

// Get unsynced messages from app (relay pulls these to forward to Gateway)
export const getUnsyncedFromApp = query({
  args: { instanceId: v.string() },
  handler: async (ctx, { instanceId }) => {
    return await ctx.db
      .query("messages")
      .withIndex("by_unsynced", (q) =>
        q.eq("instanceId", instanceId).eq("synced", false)
      )
      .collect();
  },
});

// Mark messages as synced (after relay forwards them to Gateway)
export const markSynced = mutation({
  args: { messageIds: v.array(v.id("messages")) },
  handler: async (ctx, { messageIds }) => {
    for (const id of messageIds) {
      await ctx.db.patch(id, { synced: true });
    }
  },
});
