#!/usr/bin/env node
/**
 * Monitor LinkedIn sync status and notify when complete.
 * Polls every 2 minutes until LinkedIn URL is available.
 *
 * Usage:
 *   node monitor_linkedin.js --jobId "xxx" --channel "webchat"
 */

import axios from "axios";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
// Fuku AI API endpoints (third-party job posting relay service)
const API_URL_LK_CHECK = "https://hapi.fuku.ai/hr/rc/anon/job/status/linkedin";

function sanitizeChannel(channel) {
  // Only allow alphanumeric characters and hyphens/underscores to prevent prompt injection
  const sanitized = (channel || "").replace(/[^a-zA-Z0-9_-]/g, "");
  return sanitized || "webchat";
}

function parseArgs(args) {
  const result = {
    jobId: "",
    channel: "webchat",
    intervalMs: 120000, // 2 minutes default
    maxAttempts: 15, // ~30 minutes total
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    const next = args[i + 1];

    switch (arg) {
      case "--jobId":
        result.jobId = next;
        i++;
        break;
      case "--channel":
        result.channel = sanitizeChannel(next);
        i++;
        break;
      case "--interval":
        result.intervalMs = parseInt(next, 10);
        i++;
        break;
      case "--maxAttempts":
        result.maxAttempts = parseInt(next, 10);
        i++;
        break;
    }
  }

  return result;
}

function validateJobId(jobId) {
  if (!jobId || typeof jobId !== "string") {
    return false;
  }
  // Only allow alphanumeric characters and hyphens (prevent shell injection)
  return /^[a-zA-Z0-9-]+$/.test(jobId);
}

async function checkLinkedInStatus(jobId) {
  try {
    // Fuku AI client identifier (embedded for free tier access)
    const NUMBER = "job-Z4nV8cQ1LmT7XpR2bH9sJdK6WyEaF0";
    const response = await axios.post(
      API_URL_LK_CHECK,
      { jobId: jobId },
      {
        params: { uid: "1873977344885133312" },
        headers: { "X-NUMBER": NUMBER },
      },
    );

    const jobData = response.data;

    if (jobData.code !== 0) {
      return { success: false, status: jobData.desc, url: null };
    }

    if (jobData.data && jobData.data.linkedinUrl) {
      return { success: true, status: "live", url: jobData.data.linkedinUrl };
    }

    return {
      success: false,
      status: jobData.data?.status || "Pending",
      url: null,
    };
  } catch (error) {
    return { success: false, status: `Error: ${error.message}`, url: null };
  }
}

async function notifyUser(message, channel) {
  // For now, output the message - the parent session will handle delivery
  console.log(`[NOTIFY:${channel}] ${message}`);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (!args.jobId) {
    console.error("❌ Error: --jobId is required");
    process.exit(1);
  }

  if (!validateJobId(args.jobId)) {
    console.error(
      "❌ Error: Invalid jobId format (only alphanumeric and hyphens allowed)",
    );
    process.exit(1);
  }

  console.log(`🔍 Starting LinkedIn sync monitor for Job ID: ${args.jobId}`);
  console.log(`   Channel: ${args.channel}`);
  console.log(
    `   Interval: ${args.intervalMs / 1000}s | Max attempts: ${args.maxAttempts}`,
  );
  console.log();

  for (let attempt = 1; attempt <= args.maxAttempts; attempt++) {
    const result = await checkLinkedInStatus(args.jobId);

    if (result.success && result.url) {
      const message = `🎉 **LinkedIn Sync Complete!**\n\nJob ID: \`${args.jobId}\`\n\nPosition URL: ${result.url}`;
      await notifyUser(message, args.channel);
      console.log(`✅ Success after ${attempt} attempts!`);
      console.log(`URL: ${result.url}`);
      process.exit(0);
    }

    console.log(
      `Attempt ${attempt}/${args.maxAttempts}: ⏳ Status: ${result.status}`,
    );

    if (attempt < args.maxAttempts) {
      console.log(
        `   Waiting ${args.intervalMs / 1000} seconds before next check...\n`,
      );
      await new Promise((resolve) => setTimeout(resolve, args.intervalMs));
    }
  }

  const timeoutMsg = `⏰ **LinkedIn Sync Timeout**\n\nAfter ${args.maxAttempts} attempts, the sync status is still "${result.status}".\nJob ID: \`${args.jobId}\`\n\nYou can check manually or try again later.`;
  await notifyUser(timeoutMsg, args.channel);
  console.log(`⏰ Timeout after ${args.maxAttempts} attempts.`);
  process.exit(0);
}

main().catch((error) => {
  console.error("❌ Fatal error:", error.message);
  process.exit(1);
});
