"use strict";

/**
 * Anonymous Telemetry Module
 *
 * Privacy-first, fire-and-forget usage tracking for Agent Registry.
 * No personal information or search queries are collected.
 *
 * Opt-in:
 *   export AGENT_REGISTRY_TELEMETRY=1
 *
 * Opt-out (still supported):
 *   unset AGENT_REGISTRY_TELEMETRY
 *   export DO_NOT_TRACK=1
 *
 * Automatically disabled in CI environments.
 */

const ENDPOINT = "https://t.insightx.pro";
const VERSION = "2.0.1";
const TOOL_ID = "agent-registry";

const CI_VARS = [
  "CI",
  "GITHUB_ACTIONS",
  "GITLAB_CI",
  "CIRCLECI",
  "TRAVIS",
  "BUILDKITE",
  "JENKINS_URL",
];

function isDisabled() {
  const enabled = String(process.env.AGENT_REGISTRY_TELEMETRY || "").toLowerCase();
  const telemetryOptIn = enabled === "1" || enabled === "true" || enabled === "yes";
  if (!telemetryOptIn) return true;
  if (process.env.AGENT_REGISTRY_NO_TELEMETRY) return true;
  if (process.env.DO_NOT_TRACK) return true;
  return CI_VARS.some(function (v) {
    return process.env[v];
  });
}

function track(event, data) {
  if (isDisabled()) return;

  try {
    var params = {
      t: TOOL_ID,
      e: event,
      v: VERSION,
      rt: typeof Bun !== "undefined" ? "bun" : "node",
      os: process.platform,
    };

    if (data) {
      var keys = Object.keys(data);
      for (var i = 0; i < keys.length; i++) {
        params[keys[i]] = data[keys[i]];
      }
    }

    var qs = Object.keys(params)
      .map(function (k) {
        return (
          encodeURIComponent(k) + "=" + encodeURIComponent(String(params[k]))
        );
      })
      .join("&");

    var url = ENDPOINT + "?" + qs;

    // Fire-and-forget: never await, never throw
    fetch(url).catch(function () {});
  } catch (_) {
    // Silent failure — telemetry should never break functionality
  }
}

module.exports = { track, VERSION, TOOL_ID };
