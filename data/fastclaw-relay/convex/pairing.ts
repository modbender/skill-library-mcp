import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// Generate a pairing code for an OpenClaw instance
export const createPairingCode = mutation({
  args: {
    instanceId: v.string(),
    instanceName: v.string(),
  },
  handler: async (ctx, { instanceId, instanceName }) => {
    // Upsert instance
    const existing = await ctx.db
      .query("instances")
      .withIndex("by_instanceId", (q) => q.eq("instanceId", instanceId))
      .first();

    if (!existing) {
      await ctx.db.insert("instances", {
        instanceId,
        name: instanceName,
        status: "online",
        lastSeenAt: Date.now(),
        createdAt: Date.now(),
      });
    } else {
      await ctx.db.patch(existing._id, {
        name: instanceName,
        status: "online",
        lastSeenAt: Date.now(),
      });
    }

    // Generate 6-digit code
    const code = String(Math.floor(100000 + Math.random() * 900000));

    // Expire any existing codes for this instance
    const oldCodes = await ctx.db
      .query("pairingCodes")
      .filter((q) => q.eq(q.field("instanceId"), instanceId))
      .collect();
    for (const old of oldCodes) {
      await ctx.db.delete(old._id);
    }

    // Create new code (5 min TTL)
    await ctx.db.insert("pairingCodes", {
      code,
      instanceId,
      expiresAt: Date.now() + 5 * 60 * 1000,
      claimed: false,
    });

    return { code };
  },
});

// Claim a pairing code from the FastClaw app
export const claimPairingCode = mutation({
  args: {
    code: v.string(),
    deviceId: v.string(),
    deviceName: v.string(),
    platform: v.string(),
  },
  handler: async (ctx, { code, deviceId, deviceName, platform }) => {
    const pairingCode = await ctx.db
      .query("pairingCodes")
      .withIndex("by_code", (q) => q.eq("code", code))
      .first();

    if (!pairingCode) {
      return { success: false, error: "Invalid pairing code" };
    }

    if (pairingCode.claimed) {
      return { success: false, error: "Code already used" };
    }

    if (Date.now() > pairingCode.expiresAt) {
      return { success: false, error: "Code expired" };
    }

    // Mark code as claimed
    await ctx.db.patch(pairingCode._id, {
      claimed: true,
      claimedByDeviceId: deviceId,
    });

    // Register device
    const existingDevice = await ctx.db
      .query("devices")
      .withIndex("by_deviceId", (q) => q.eq("deviceId", deviceId))
      .first();

    if (existingDevice) {
      await ctx.db.patch(existingDevice._id, {
        instanceId: pairingCode.instanceId,
        name: deviceName,
        lastSeenAt: Date.now(),
      });
    } else {
      await ctx.db.insert("devices", {
        instanceId: pairingCode.instanceId,
        deviceId,
        name: deviceName,
        platform,
        pairedAt: Date.now(),
        lastSeenAt: Date.now(),
      });
    }

    return {
      success: true,
      instanceId: pairingCode.instanceId,
    };
  },
});

// Check if a pairing code has been claimed (polled by the relay)
export const checkPairingStatus = query({
  args: { code: v.string() },
  handler: async (ctx, { code }) => {
    const pairingCode = await ctx.db
      .query("pairingCodes")
      .withIndex("by_code", (q) => q.eq("code", code))
      .first();

    if (!pairingCode) return { status: "not_found" as const };
    if (pairingCode.claimed) return { status: "claimed" as const, deviceId: pairingCode.claimedByDeviceId };
    if (Date.now() > pairingCode.expiresAt) return { status: "expired" as const };
    return { status: "pending" as const };
  },
});
