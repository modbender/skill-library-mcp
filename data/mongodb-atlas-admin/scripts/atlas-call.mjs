#!/usr/bin/env node

/**
 * MongoDB Atlas API Client
 * 
 * Makes actual API calls to MongoDB Atlas.
 * WARNING: POST/PUT/DELETE/PATCH operations modify resources and require USER approval.
 * 
 * Environment variables required:
 * - ATLAS_CLIENT_ID: Service Account Client ID
 * - ATLAS_CLIENT_SECRET: Service Account Client Secret
 * - ATLAS_GROUP_ID: (Optional) Default project/group ID
 * - ATLAS_API_BASE_URL: (Optional) Default: https://cloud.mongodb.com
 */

import fs from "fs";
import path from "path";
import os from "os";

const CACHE_DIR = path.join(os.homedir(), ".openclaw", ".cache", "mongodb-atlas");
const TOKEN_CACHE_FILE = path.join(CACHE_DIR, "token.json");

// Ensure cache directory exists
function ensureCacheDir() {
  if (!fs.existsSync(CACHE_DIR)) {
    fs.mkdirSync(CACHE_DIR, { recursive: true });
  }
}

// Load cached token
function loadCachedToken() {
  try {
    if (fs.existsSync(TOKEN_CACHE_FILE)) {
      const data = JSON.parse(fs.readFileSync(TOKEN_CACHE_FILE, "utf-8"));
      if (data.expires_at && Date.now() < data.expires_at) {
        return data.access_token;
      }
    }
  } catch (e) {
    // Ignore cache errors
  }
  return null;
}

// Save token to cache
function saveToken(accessToken, expiresIn) {
  ensureCacheDir();
  const data = {
    access_token: accessToken,
    expires_at: Date.now() + (expiresIn - 60) * 1000 // Refresh 60s early
  };
  fs.writeFileSync(TOKEN_CACHE_FILE, JSON.stringify(data, null, 2));
}

// Clear cached token
function clearCachedToken() {
  try {
    if (fs.existsSync(TOKEN_CACHE_FILE)) {
      fs.unlinkSync(TOKEN_CACHE_FILE);
    }
  } catch (e) {
    // Ignore
  }
}

// Get access token (with caching)
async function getAccessToken() {
  const clientId = process.env.ATLAS_CLIENT_ID;
  const clientSecret = process.env.ATLAS_CLIENT_SECRET;
  const baseUrl = process.env.ATLAS_API_BASE_URL || "https://cloud.mongodb.com";

  if (!clientId || !clientSecret) {
    throw new Error(
      "Missing Atlas Service Account credentials. Please set environment variables:\n" +
      "  ATLAS_CLIENT_ID\n" +
      "  ATLAS_CLIENT_SECRET"
    );
  }

  // Check cache first
  const cached = loadCachedToken();
  if (cached) {
    return cached;
  }

  // Request new token using OAuth 2.0 client credentials flow
  const tokenUrl = `${baseUrl}/api/oauth/token`;
  const auth = Buffer.from(`${clientId}:${clientSecret}`).toString("base64");
  
  try {
    const response = await fetch(tokenUrl, {
      method: "POST",
      headers: {
        "Authorization": `Basic ${auth}`,
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: "grant_type=client_credentials"
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`Failed to get access token: ${response.status} - ${text}`);
    }

    const data = await response.json();
    saveToken(data.access_token, data.expires_in || 3600);
    return data.access_token;

  } catch (e) {
    throw new Error(`Error getting Atlas access token: ${e.message}`);
  }
}

// Call Atlas API
async function callAtlasApi(method, endpoint, data = null, params = null) {
  const baseUrl = process.env.ATLAS_API_BASE_URL || "https://cloud.mongodb.com";
  const groupId = process.env.ATLAS_GROUP_ID;

  // Replace {groupId} placeholder if env var is set
  let path = endpoint.startsWith("/") ? endpoint.slice(1) : endpoint;
  if (groupId) {
    path = path.replace(/{groupId}/g, groupId);
  }

  const url = new URL(`/api/atlas/v2/${path}`, baseUrl);
  
  // Add query params
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null) {
        url.searchParams.append(key, String(value));
      }
    }
  }

  const token = await getAccessToken();

  const headers = {
    "Authorization": `Bearer ${token}`,
    "Accept": "application/vnd.atlas.2024-08-05+json"
  };

  if (data) {
    headers["Content-Type"] = "application/vnd.atlas.2024-08-05+json";
  }

  try {
    const response = await fetch(url.toString(), {
      method: method.toUpperCase(),
      headers,
      body: data ? JSON.stringify(data) : undefined
    });

    // Handle token expiration
    if (response.status === 401) {
      clearCachedToken();
      // Could retry once here if needed
      throw new Error("Authentication failed. Token may have expired. Please retry.");
    }

    // Parse response
    let result;
    const contentType = response.headers.get("content-type");
    if (contentType?.includes("application/json")) {
      result = await response.json();
    } else if (response.status === 204) {
      result = { success: true, message: "Operation completed successfully" };
    } else {
      const text = await response.text();
      result = { status: response.status, body: text };
    }

    if (!response.ok) {
      return {
        error: true,
        status_code: response.status,
        message: `API call failed: ${response.status}`,
        details: result
      };
    }

    return result;

  } catch (e) {
    if (e.message.includes("fetch failed") || e.message.includes("ENOTFOUND")) {
      return {
        error: true,
        message: `Network error: ${e.message}`
      };
    }
    throw e;
  }
}

// Check if operation is risky (modifies resources)
function isRiskyOperation(method) {
  return ["POST", "PUT", "DELETE", "PATCH"].includes(method.toUpperCase());
}

// Main
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length < 2 || args[0] === "-h" || args[0] === "--help") {
    console.log(`Usage: atlas-call.mjs <method> <endpoint> [options]

Make API calls to MongoDB Atlas.

Arguments:
  method      HTTP method: GET, POST, PUT, DELETE, PATCH
  endpoint    API endpoint path, e.g., 'groups/{groupId}/clusters'

Options:
  -d, --data <json>      Request body (JSON string)
  -p, --params <json>    Query parameters (JSON string)
  -f, --file <path>      Read request body from JSON file
  --dry-run              Show what would be called without making the request
  --yes                  Skip confirmation for risky operations (NOT RECOMMENDED)

Environment:
  ATLAS_CLIENT_ID        Service Account Client ID (required)
  ATLAS_CLIENT_SECRET    Service Account Client Secret (required)
  ATLAS_GROUP_ID         Default project/group ID (optional, replaces {groupId})
  ATLAS_API_BASE_URL     API base URL (default: https://cloud.mongodb.com)

Examples:
  # List clusters (safe read operation)
  node atlas-call.mjs GET groups/{groupId}/clusters

  # Create cluster (RISKY - modifies resources)
  node atlas-call.mjs POST groups/{groupId}/clusters -d '{"name":"myCluster"}'

  # Delete cluster (RISKY - deletes resources)
  node atlas-call.mjs DELETE groups/{groupId}/clusters/myCluster

⚠️  WARNING: POST/PUT/DELETE/PATCH operations modify or delete resources.
    These operations require explicit USER approval before execution.
    See SKILL.md for safety guidelines.
`);
    process.exit(2);
  }

  const method = args[0].toUpperCase();
  const endpoint = args[1];
  
  let data = null;
  let params = null;
  let dryRun = false;
  let skipConfirm = false;

  // Parse options
  for (let i = 2; i < args.length; i++) {
    const arg = args[i];
    if ((arg === "-d" || arg === "--data") && i + 1 < args.length) {
      try {
        data = JSON.parse(args[i + 1]);
      } catch (e) {
        console.error(`Error parsing JSON data: ${e.message}`);
        process.exit(1);
      }
      i++;
    } else if ((arg === "-p" || arg === "--params") && i + 1 < args.length) {
      try {
        params = JSON.parse(args[i + 1]);
      } catch (e) {
        console.error(`Error parsing JSON params: ${e.message}`);
        process.exit(1);
      }
      i++;
    } else if ((arg === "-f" || arg === "--file") && i + 1 < args.length) {
      try {
        const filePath = args[i + 1];
        const fileContent = fs.readFileSync(filePath, "utf-8");
        data = JSON.parse(fileContent);
      } catch (e) {
        console.error(`Error reading/parsing file: ${e.message}`);
        process.exit(1);
      }
      i++;
    } else if (arg === "--dry-run") {
      dryRun = true;
    } else if (arg === "--yes") {
      skipConfirm = true;
    }
  }

  // Check for risky operations
  if (isRiskyOperation(method)) {
    console.log("\n" + "=".repeat(60));
    console.log("⚠️  RISKY OPERATION DETECTED");
    console.log("=".repeat(60));
    console.log(`\nMethod: ${method}`);
    console.log(`Endpoint: ${endpoint}`);
    if (data) {
      console.log(`\nRequest Body:\n${JSON.stringify(data, null, 2)}`);
    }
    console.log("\n" + "-".repeat(60));
    console.log("This operation will MODIFY or DELETE resources.");
    console.log("You MUST review and approve this operation.");
    console.log("-".repeat(60) + "\n");

    if (!skipConfirm && !dryRun) {
      console.error("ERROR: Risky operations require USER approval.");
      console.error("\nTo execute this operation:");
      console.error("1. Review the operation details above");
      console.error("2. If you approve, run with --yes flag (NOT RECOMMENDED for automation)");
      console.error("\nAlternatively, use --dry-run to preview the request without executing.");
      process.exit(1);
    }
  }

  // Show dry run info
  if (dryRun) {
    console.log("DRY RUN - Request details:");
    console.log(`  Method: ${method}`);
    console.log(`  Endpoint: ${endpoint}`);
    if (data) console.log(`  Body: ${JSON.stringify(data, null, 2)}`);
    if (params) console.log(`  Params: ${JSON.stringify(params, null, 2)}`);
    console.log("\nNo request was made.");
    return;
  }

  // Execute the API call
  try {
    const result = await callAtlasApi(method, endpoint, data, params);
    console.log(JSON.stringify(result, null, 2));
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }
}

main();
