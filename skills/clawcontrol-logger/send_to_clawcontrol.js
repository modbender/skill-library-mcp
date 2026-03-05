#!/usr/bin/env node

// Grabs the API key from the environment variables securely
const API_KEY = process.env.CLAWCONTROL_API_KEY;

if (!API_KEY) {
  console.error("Error: CLAWCONTROL_API_KEY environment variable is missing.");
  process.exit(1);
}

// Parse the arguments passed by the OpenClaw agent
const args = process.argv.slice(2);
if (args.length === 0) {
  console.error("Error: No payload provided.");
  process.exit(1);
}

try {
  const payload = JSON.parse(args[0]);
  
  // Enforce required fields based on the ClawControl schema
  if (!payload.session_id || !payload.agent_name || !payload.logs) {
    console.error("Error: Missing required fields (session_id, agent_name, or logs).");
    process.exit(1);
  }

  const url = `https://clawcontrol.space/api/functions/receiveWebhook?key=${API_KEY}`;

  fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  })
  .then(response => {
    if (response.ok) {
      console.log("Log successfully sent to ClawControl.");
    } else {
      console.error(`Failed to send log. Status: ${response.status}`);
    }
  })
  .catch(err => {
    console.error(`Network error: ${err.message}`);
  });

} catch (e) {
  console.error("Error parsing JSON payload:", e.message);
  process.exit(1);
}