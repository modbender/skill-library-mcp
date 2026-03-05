// scripts/fetch_activity.js
const { parseArgs } = require('util');

async function getActivityData(hours) {
  const baseUrl = "http://127.0.0.1:5600/api/0";

  // 1. Check if the API is available
  try {
    // Set 2 second timeout
    await fetch(`${baseUrl}/info`, { signal: AbortSignal.timeout(2000) });
  } catch (error) {
    console.error("ERROR: ActivityWatch API is not available, please ensure the service is running on port 5600.");
    console.error("Please install ActivityWatch and the browser extension `aw-watcher-web`.");
    console.error("You can use the following command to install ActivityWatch:");
    console.error("brew install --cask activitywatch && open -a ActivityWatch");
    console.error("You can use the following command to install the browser extension:");
    console.error("brew install --cask activitywatch && open -a ActivityWatch");
    process.exit(1);
  }

  try {
    // 2. Get the current Buckets
    const bucketsRes = await fetch(`${baseUrl}/buckets`);
    const buckets = await bucketsRes.json();
    
    // Find the active window bucket (record application and window title)
    const windowBucket = Object.keys(buckets).find(b => b.includes("aw-watcher-window"));
    if (!windowBucket) {
      console.error("ERROR: Window bucket not found, please check if aw-watcher-window is running.");
      process.exit(1);
    }

    // 3. Calculate the time range
    const now = new Date();
    const startTime = new Date(now.getTime() - hours * 60 * 60 * 1000);
    const formatTime = (d) => d.toISOString().replace(/\.\d{3}Z$/, 'Z');
    const timeperiod = `${formatTime(startTime)}/${formatTime(now)}`;
    console.log(`🔍 Querying: ${windowBucket}`);
    console.log(`🕐 Period: ${timeperiod}`);

    // 4. Build the ActivityWatch specific query syntax
    const query = `
      events = flood(query_bucket('${windowBucket}'));
      RETURN = sort_by_duration(merge_events_by_keys(events, ["app", "title"]));
    `;

    const queryRes = await fetch(`${baseUrl}/query/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ timeperiods: [timeperiod], query: [query] })
    });

    const result = await queryRes.json();
    console.log('📦 Raw result:', JSON.stringify(result, null, 2));
    // 5. Format the output for OpenClaw Agent to read
    console.log(`--- Summary of application and window activity in the last ${hours} hours ---`);
    if (!result || !result[0] || result[0].length === 0) {
      console.log("No enough data recorded.");
      return;
    }

    // Take the first 50 most time-consuming records to prevent the output from being too long and bursting the LLM context
    result[0].slice(0, 50).forEach(event => {
      const app = event.data.app || 'Unknown';
      const title = event.data.title || 'Unknown';
      const durationSec = event.duration;
      
      if (durationSec > 60) { // Filter out activities that lasted less than 1 minute
        const minutes = Math.floor(durationSec / 60);
        console.log(`- ${app} (${title}): ${minutes} minutes`);
      }
    });

  } catch (error) {
    console.error(`ERROR: Failed to query data: ${error.message}`);
    process.exit(1);
  }
}

// Parse command line arguments
const { values } = parseArgs({
  options: {
    hours: { type: 'string', short: 'h', default: '24' }
  }
});

getActivityData(parseInt(values.hours, 10));