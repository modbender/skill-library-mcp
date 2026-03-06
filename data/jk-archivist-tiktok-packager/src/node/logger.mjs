import { writeJson } from "./utils.mjs";

export function createRunLogger({ runLogPath, verbose = false }) {
  const startedAt = new Date().toISOString();
  const events = [];

  function add(level, message, data = {}) {
    const event = {
      ts: new Date().toISOString(),
      level,
      message,
      data,
    };
    events.push(event);
    if (verbose) {
      console.log(`[${level}] ${message}`);
    }
  }

  function flush(final = {}) {
    writeJson(runLogPath, {
      started_at: startedAt,
      finished_at: new Date().toISOString(),
      events,
      ...final,
    });
  }

  return {
    info: (message, data) => add("info", message, data),
    warn: (message, data) => add("warn", message, data),
    error: (message, data) => add("error", message, data),
    flush,
  };
}
