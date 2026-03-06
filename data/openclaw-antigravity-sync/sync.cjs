
const fs = require('fs');
const path = require('path');
const os = require('os');
const https = require('https');

// Constants
const BASE_URL = "https://cloudcode-pa.googleapis.com";
const FETCH_AVAILABLE_MODELS_PATH = "/v1internal:fetchAvailableModels";

// Path resolution logic to match OpenClaw's structure
const CONFIG_DIR_NAME = '.openclaw';
const CONFIG_DIR = path.join(os.homedir(), CONFIG_DIR_NAME);
// Adjusted based on observed file structure in session
const AUTH_PROFILES_PATH = path.join(CONFIG_DIR, 'agents/main/agent/auth-profiles.json');
const OPENCLAW_JSON_PATH = path.join(CONFIG_DIR, 'openclaw.json');

// --- Helper: Simple Fetch Wrapper for Node.js (no dependencies) ---
function postJson(url, headers, body) {
  return new Promise((resolve, reject) => {
    const opts = new URL(url);
    const options = {
      hostname: opts.hostname,
      path: opts.pathname,
      method: 'POST',
      headers: headers
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            reject(new Error("Failed to parse JSON response"));
          }
        } else {
          reject(new Error(`API Request Failed: ${res.statusCode} ${data}`));
        }
      });
    });

    req.on('error', (e) => reject(e));
    if (body) req.write(body);
    req.end();
  });
}

// 1. Get Authentication Token
function getAuthToken() {
  if (!fs.existsSync(AUTH_PROFILES_PATH)) {
    console.error(`❌ Auth profiles not found at ${AUTH_PROFILES_PATH}.\n   Please run 'openclaw models auth login google-antigravity' first.`);
    process.exit(1);
  }
  
  try {
    const authData = JSON.parse(fs.readFileSync(AUTH_PROFILES_PATH, 'utf8'));
    const profiles = authData.profiles || {};
    
    // Find the google-antigravity profile
    const antigravityProfileKey = Object.keys(profiles).find(k => k.startsWith('google-antigravity:'));
    
    if (!antigravityProfileKey) {
      console.error("❌ No 'google-antigravity' profile found in auth-profiles.json. Please login.");
      process.exit(1);
    }
    
    const profile = profiles[antigravityProfileKey];
    if (!profile.access) {
      console.error("❌ Auth profile found but no access token present.");
      process.exit(1);
    }

    return { token: profile.access, projectId: profile.projectId };
  } catch (e) {
    console.error("❌ Failed to read auth profiles:", e.message);
    process.exit(1);
  }
}

// 2. Fetch Models from API
async function fetchModels(token, projectId) {
  const headers = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
    "User-Agent": "antigravity-sync-skill",
    "X-Goog-Api-Client": "google-cloud-sdk vscode_cloudshelleditor/0.1",
  };

  const body = JSON.stringify({ project: projectId || undefined });
  
  try {
    const data = await postJson(`${BASE_URL}${FETCH_AVAILABLE_MODELS_PATH}`, headers, body);
    return data;
  } catch (e) {
    console.error("❌ API Error:", e.message);
    process.exit(1);
  }
}

// 3. Update Configuration
function updateConfig(apiResponse) {
  if (!fs.existsSync(OPENCLAW_JSON_PATH)) {
    console.error(`❌ Config file not found at ${OPENCLAW_JSON_PATH}`);
    process.exit(1);
  }

  // Backup config
  const backupPath = `${OPENCLAW_JSON_PATH}.bak`;
  fs.copyFileSync(OPENCLAW_JSON_PATH, backupPath);
  console.log(`📦 Created config backup at ${backupPath}`);

  let config;
  try {
    config = JSON.parse(fs.readFileSync(OPENCLAW_JSON_PATH, 'utf8'));
  } catch (e) {
    console.error("❌ Failed to parse openclaw.json:", e.message);
    process.exit(1);
  }

  const apiModels = apiResponse.models || {};
  const modelDefinitions = [];
  
  // Verify User Safety (WhatsApp)
  if (config.channels?.whatsapp) {
      const wa = config.channels.whatsapp;
      const allowed = wa.allowFrom || [];
      const selfChat = wa.selfChatMode;
      
      if (!selfChat && allowed.length === 0) {
          console.warn("\n⚠️  WARNING: WhatsApp channel is configured but has no 'allowFrom' list and 'selfChatMode' is off.");
          console.warn("    This means anyone can message your bot! Please configure 'allowFrom' in openclaw.json.\n");
      } else {
          console.log("🔒 WhatsApp safety check passed (Allowlist/SelfChat active).");
      }
  }

  // Smart Model Selection Logic
  // 1. Identify the currently configured primary model
  const currentPrimaryFullId = config.agents?.defaults?.model?.primary;
  let targetDefaultId = null;
  let currentModelStatus = "unknown";

  if (currentPrimaryFullId && currentPrimaryFullId.startsWith("google-antigravity/")) {
      const currentShortId = currentPrimaryFullId.replace("google-antigravity/", "");
      const currentModelInfo = apiModels[currentShortId];
      
      if (currentModelInfo) {
          const quota = currentModelInfo.quotaInfo;
          if (!quota || quota.remainingFraction > 0) {
              targetDefaultId = currentShortId;
              currentModelStatus = "valid_and_available";
              console.log(`✅ Keeping user-selected model: ${currentShortId} (Available)`);
          } else {
              currentModelStatus = "exhausted";
              console.warn(`⚠️  User-selected model '${currentShortId}' is exhausted (0% quota). Switching...`);
          }
      } else {
          currentModelStatus = "missing";
          console.warn(`⚠️  User-selected model '${currentShortId}' is no longer available from API. Switching...`);
      }
  }

  // 2. If we haven't stuck with the current model, find a new default
  if (!targetDefaultId) {
      // Try API default
      const apiDefault = apiResponse.defaultAgentModelId;
      if (apiDefault) {
           const quota = apiModels[apiDefault]?.quotaInfo;
           if (!quota || quota.remainingFraction > 0) {
               targetDefaultId = apiDefault;
               console.log(`ℹ️  Selected API default: ${targetDefaultId}`);
           }
      }
      
      // Fallback to recommended
      if (!targetDefaultId) {
          const recommended = Object.entries(apiModels).find(([_, m]) => {
              const q = m.quotaInfo;
              return m.recommended && (!q || q.remainingFraction > 0);
          });
          if (recommended) {
              targetDefaultId = recommended[0];
              console.log(`ℹ️  Selected recommended fallback: ${targetDefaultId}`);
          }
      }
      
      // Fallback to anything available
      if (!targetDefaultId) {
           const anyAvailable = Object.entries(apiModels).find(([_, m]) => {
              const q = m.quotaInfo;
              return !q || q.remainingFraction > 0;
          });
          if (anyAvailable) {
               targetDefaultId = anyAvailable[0];
               console.log(`ℹ️  Selected available fallback: ${targetDefaultId}`);
          }
      }
  }

  if (!targetDefaultId) {
      console.warn("⚠️  Could not find ANY available model with quota! Keeping existing configuration unsafe.");
      // We don't exit, we just don't update the primary model pointer.
  }

  // Build config definitions
  for (const [id, info] of Object.entries(apiModels)) {
      const isReasoning = id.toLowerCase().includes("thinking") || info.supportsThinking === true;
      const isVision = info.supportsImages === true;
      const input = ["text"];
      if (isVision) input.push("image");

      modelDefinitions.push({
          id: id,
          name: info.displayName || id,
          reasoning: isReasoning,
          input: input,
          cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 }, // Placeholder
          contextWindow: info.maxTokens || 200000,
          maxTokens: info.maxOutputTokens || 8192
      });
  }

  // --- Update `openclaw.json` structure ---

  // Ensure provider exists
  if (!config.models.providers) config.models.providers = {};
  if (!config.models.providers["google-antigravity"]) {
      config.models.providers["google-antigravity"] = {
          api: "google-gemini-cli",
          baseUrl: "https://cloudcode-pa.googleapis.com",
          auth: "oauth",
          apiKey: "OAUTH_PLACEHOLDER"
      };
  }

  // Overwrite models list with fresh data
  config.models.providers["google-antigravity"].models = modelDefinitions;

  // Update primary agent if we have a target and we decided to switch (or it's new)
  if (targetDefaultId) {
      const fullId = `google-antigravity/${targetDefaultId}`;
      
      if (!config.agents) config.agents = {};
      if (!config.agents.defaults) config.agents.defaults = {};
      if (!config.agents.defaults.model) config.agents.defaults.model = { fallbacks: [] };

      // Only logging the change if it's actually different or we are forcing an update
      if (config.agents.defaults.model.primary !== fullId) {
          config.agents.defaults.model.primary = fullId;
          console.log(`🔄 Updated primary agent model to: ${fullId}`);
      }
      
      // Ensure it's in the `models` map (used for enablement/overrides)
      if (!config.agents.defaults.models) config.agents.defaults.models = {};
      config.agents.defaults.models[fullId] = config.agents.defaults.models[fullId] || {};
  }

  // Write changes
  fs.writeFileSync(OPENCLAW_JSON_PATH, JSON.stringify(config, null, 2));
  console.log(`✅ Configuration updated successfully with ${modelDefinitions.length} models.`);
}

async function main() {
    console.log("🔄 Starting Antigravity Sync...");
    const { token, projectId } = getAuthToken();
    console.log("🔑 Authenticated.");
    
    console.log("📡 Fetching models from Google Cloud Code Assist...");
    const apiResponse = await fetchModels(token, projectId);
    
    console.log(`✨ Discovered ${Object.keys(apiResponse.models || {}).length} models.`);
    updateConfig(apiResponse);
}

main();
