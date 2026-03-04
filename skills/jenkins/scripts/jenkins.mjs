#!/usr/bin/env node

const args = process.argv.slice(2);

function getArg(name, def = undefined) {
  const i = args.indexOf(`--${name}`);
  if (i === -1) return def;
  return args[i + 1] ?? def;
}

function hasArg(name) {
  return args.includes(`--${name}`);
}

function usage() {
  console.error(`Usage:
  jenkins.mjs jobs [--pattern <glob>]
  jenkins.mjs build --job <jobName> [--params '<json>']
  jenkins.mjs status --job <jobName> [--build <number>] [--last]
  jenkins.mjs console --job <jobName> [--build <number>] [--last] [--tail <lines>]
  jenkins.mjs stop --job <jobName> --build <number>
  jenkins.mjs queue
  jenkins.mjs nodes`);
  process.exit(1);
}

const command = args[0];
if (!command || !["jobs", "build", "status", "console", "stop", "queue", "nodes"].includes(command)) usage();

const JENKINS_URL = process.env.JENKINS_URL?.replace(/\/$/, "");
const JENKINS_USER = process.env.JENKINS_USER;
const JENKINS_API_TOKEN = process.env.JENKINS_API_TOKEN;

if (!JENKINS_URL || !JENKINS_USER || !JENKINS_API_TOKEN) {
  console.error("Missing required environment variables: JENKINS_URL, JENKINS_USER, JENKINS_API_TOKEN");
  process.exit(2);
}

const auth = Buffer.from(`${JENKINS_USER}:${JENKINS_API_TOKEN}`).toString("base64");

const headers = {
  "Authorization": `Basic ${auth}`,
  "Content-Type": "application/json",
  "Accept": "application/json",
};

async function request(path, { method = "GET", body = undefined, crumb = false } = {}) {
  const url = `${JENKINS_URL}${path}`;

  const res = await fetch(url, {
    headers,
    method,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  const text = await res.text();

  if (!res.ok) {
    console.error(JSON.stringify({
      ok: false,
      status: res.status,
      statusText: res.statusText,
      url: url,
      error: text,
    }, null, 2));
    process.exit(10);
  }

  // Try to parse JSON, but return text if not JSON
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

async function requestJson(path, options = {}) {
  const result = await request(path, options);
  return typeof result === "string" ? { raw: result } : result;
}

function matchPattern(str, pattern) {
  if (!pattern) return true;
  // Simple glob matching: * matches any characters
  const regex = new RegExp("^" + pattern.replace(/\*/g, ".*") + "$");
  return regex.test(str);
}

(async () => {
  if (command === "jobs") {
    const pattern = getArg("pattern");
    const data = await requestJson("/api/json?tree=jobs[name,url,color,lastBuild[number,result,timestamp]]");

    const jobs = data.jobs || [];
    const filtered = pattern ? jobs.filter(j => matchPattern(j.name, pattern)) : jobs;

    console.log(JSON.stringify({
      jobs: filtered,
      total: filtered.length,
    }, null, 2));
    return;
  }

  if (command === "build") {
    const job = getArg("job");
    if (!job) usage();

    const paramsStr = getArg("params");
    const params = paramsStr ? JSON.parse(paramsStr) : null;

    const jobInfo = await requestJson(`/job/${encodeURIComponent(job)}/api/json`);

    let buildUrl;
    if (params && Object.keys(params).length > 0) {
      // Parameterized build
      const crumbData = await requestJson("/crumbIssuer/api/json");
      const crumbHeader = crumbData.crumbRequestField;
      const crumbValue = crumbData.crumb;
      headers[crumbHeader] = crumbValue;

      buildUrl = `/job/${encodeURIComponent(job)}/buildWithParameters?${new URLSearchParams(params)}`;
    } else {
      buildUrl = `/job/${encodeURIComponent(job)}/build`;
    }

    await request(buildUrl, { method: "POST" });

    // Get queue info
    const queueData = await requestJson("/queue/api/json");
    const lastItem = queueData.items?.[0];

    console.log(JSON.stringify({
      ok: true,
      job: job,
      triggered: true,
      queueItem: lastItem || null,
    }, null, 2));
    return;
  }

  if (command === "status") {
    const job = getArg("job");
    if (!job) usage();

    const buildNum = getArg("build");
    const last = hasArg("last");

    if (!buildNum && !last) {
      // Show job info with last build
      const data = await requestJson(`/job/${encodeURIComponent(job)}/api/json?tree=name,url,color,lastBuild[number,result,timestamp,duration,building]`);
      console.log(JSON.stringify(data, null, 2));
      return;
    }

    const buildPath = last
      ? `/job/${encodeURIComponent(job)}/lastBuild/api/json`
      : `/job/${encodeURIComponent(job)}/${buildNum}/api/json`;

    const data = await requestJson(buildPath);
    console.log(JSON.stringify(data, null, 2));
    return;
  }

  if (command === "console") {
    const job = getArg("job");
    if (!job) usage();

    const buildNum = getArg("build");
    const last = hasArg("last");
    const tail = getArg("tail");

    const buildPath = last
      ? `/job/${encodeURIComponent(job)}/lastBuild`
      : `/job/${encodeURIComponent(job)}/${buildNum}`;

    const consoleText = await request(`${buildPath}/consoleText`);

    let output = typeof consoleText === "string" ? consoleText : consoleText.raw || "";

    if (tail) {
      const lines = output.split("\n");
      const tailNum = parseInt(tail, 10);
      output = lines.slice(-tailNum).join("\n");
    }

    console.log(JSON.stringify({
      job: job,
      build: last ? "last" : buildNum,
      console: output,
    }, null, 2));
    return;
  }

  if (command === "stop") {
    const job = getArg("job");
    const buildNum = getArg("build");
    if (!job || !buildNum) usage();

    await request(`/job/${encodeURIComponent(job)}/${buildNum}/stop`, { method: "POST" });

    console.log(JSON.stringify({
      ok: true,
      job: job,
      build: buildNum,
      stopped: true,
    }, null, 2));
    return;
  }

  if (command === "queue") {
    const data = await requestJson("/queue/api/json");
    console.log(JSON.stringify(data, null, 2));
    return;
  }

  if (command === "nodes") {
    const data = await requestJson("/computer/api/json?tree=computer[displayName,offline,offlineCauseReason,idle,jnlpAgent,launchSupported,manualLaunchReason,numExecutors]");
    console.log(JSON.stringify(data, null, 2));
    return;
  }
})();
