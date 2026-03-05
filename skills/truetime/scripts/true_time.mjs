#!/usr/bin/env node
/**
 * Deterministic time calculator for the TrueTime skill.
 *
 * Modes:
 * 1) Relative mode: --plus <duration>
 * 2) Absolute mode: --target <iso-datetime>
 * 3) List timezone mode: --list-timezones
 *
 * Outputs JSON with UTC, server-timezone, optional user-timezone,
 * and Chinese lunar calendar fields.
 */

import dgram from "node:dgram";

const FIXED_UNIT_MILLISECONDS = new Map([
  ["ms", 1],
  ["msec", 1],
  ["msecs", 1],
  ["millisecond", 1],
  ["milliseconds", 1],
  ["s", 1000],
  ["sec", 1000],
  ["secs", 1000],
  ["second", 1000],
  ["seconds", 1000],
  ["m", 60 * 1000],
  ["min", 60 * 1000],
  ["mins", 60 * 1000],
  ["minute", 60 * 1000],
  ["minutes", 60 * 1000],
  ["h", 3600 * 1000],
  ["hr", 3600 * 1000],
  ["hrs", 3600 * 1000],
  ["hour", 3600 * 1000],
  ["hours", 3600 * 1000],
  ["d", 86400 * 1000],
  ["day", 86400 * 1000],
  ["days", 86400 * 1000],
  ["w", 604800 * 1000],
  ["week", 604800 * 1000],
  ["weeks", 604800 * 1000],
]);

const CALENDAR_UNIT_MONTHS = new Map([
  ["mo", 1],
  ["mon", 1],
  ["month", 1],
  ["months", 1],
]);

const CALENDAR_UNIT_YEARS = new Map([
  ["y", 1],
  ["yr", 1],
  ["yrs", 1],
  ["year", 1],
  ["years", 1],
  ["decade", 10],
  ["decades", 10],
  ["century", 100],
  ["centuries", 100],
]);

const DEFAULT_NTP_SERVERS = ["time.cloudflare.com", "time.google.com", "pool.ntp.org"];

function fail(message, code = 2) {
  process.stderr.write(`${message}\n`);
  process.exit(code);
}

function parseArgs(argv) {
  const out = {
    plus: undefined,
    target: undefined,
    targetTz: undefined,
    userTz: undefined,
    serverTz: undefined,
    calendarTz: undefined,
    lunarTz: "Asia/Shanghai",
    now: undefined,
    listTimezones: false,
    timeSource: "server",
    ntpServers: [],
    ntpTimeoutMs: 1500,
  };

  for (let i = 2; i < argv.length; i += 1) {
    const arg = argv[i];
    const next = argv[i + 1];
    if (arg === "--plus") {
      if (!next) fail("--plus requires a value");
      out.plus = next;
      i += 1;
      continue;
    }
    if (arg === "--target") {
      if (!next) fail("--target requires a value");
      out.target = next;
      i += 1;
      continue;
    }
    if (arg === "--target-tz") {
      if (!next) fail("--target-tz requires a value");
      out.targetTz = next;
      i += 1;
      continue;
    }
    if (arg === "--user-tz") {
      if (!next) fail("--user-tz requires a value");
      out.userTz = next;
      i += 1;
      continue;
    }
    if (arg === "--server-tz") {
      if (!next) fail("--server-tz requires a value");
      out.serverTz = next;
      i += 1;
      continue;
    }
    if (arg === "--calendar-tz") {
      if (!next) fail("--calendar-tz requires a value");
      out.calendarTz = next;
      i += 1;
      continue;
    }
    if (arg === "--lunar-tz") {
      if (!next) fail("--lunar-tz requires a value");
      out.lunarTz = next;
      i += 1;
      continue;
    }
    if (arg === "--now") {
      if (!next) fail("--now requires a value");
      out.now = next;
      i += 1;
      continue;
    }
    if (arg === "--list-timezones") {
      out.listTimezones = true;
      continue;
    }
    if (arg === "--time-source") {
      if (!next) fail("--time-source requires a value: server|ntp");
      out.timeSource = next.trim().toLowerCase();
      i += 1;
      continue;
    }
    if (arg === "--ntp-server") {
      if (!next) fail("--ntp-server requires a value");
      out.ntpServers.push(
        ...next
          .split(",")
          .map((v) => v.trim())
          .filter(Boolean),
      );
      i += 1;
      continue;
    }
    if (arg === "--ntp-timeout-ms") {
      if (!next) fail("--ntp-timeout-ms requires a value");
      const timeout = Number.parseInt(next, 10);
      if (!Number.isFinite(timeout) || timeout < 100) {
        fail("--ntp-timeout-ms must be an integer >= 100");
      }
      out.ntpTimeoutMs = timeout;
      i += 1;
      continue;
    }
    if (arg === "-h" || arg === "--help") {
      process.stdout.write(
        [
          "Usage:",
          "  true_time.mjs --list-timezones",
          "  true_time.mjs --plus <duration> [--user-tz <IANA>] [--server-tz <IANA>] [--calendar-tz <IANA>] [--lunar-tz <IANA>] [--time-source server|ntp] [--ntp-server <host>] [--ntp-timeout-ms <ms>] [--now <ISO>]",
          "  true_time.mjs --target <ISO> [--target-tz <IANA>] [--user-tz <IANA>] [--server-tz <IANA>] [--lunar-tz <IANA>] [--time-source server|ntp] [--ntp-server <host>] [--ntp-timeout-ms <ms>] [--now <ISO>]",
          "",
          "Supported relative units:",
          "  milliseconds: ms msec millisecond",
          "  seconds: s sec second",
          "  minutes: m min minute",
          "  hours: h hr hour",
          "  days: d day",
          "  weeks: w week",
          "  months: mo mon month",
          "  years: y yr year",
          "  decades: decade",
          "  centuries: century",
          "",
          "All units support decimal values.",
          "Examples: 1.5m = 90s, 0.25h = 15m, 1.5year = 18 months.",
          "",
          "Examples:",
          "  node true_time.mjs --list-timezones",
          "  node true_time.mjs --plus 1m --user-tz Asia/Shanghai",
          "  node true_time.mjs --plus 1.5m --user-tz Asia/Shanghai",
          "  node true_time.mjs --plus 250ms --user-tz Asia/Shanghai",
          "  node true_time.mjs --plus 1month2w --user-tz America/New_York --calendar-tz America/New_York",
          "  node true_time.mjs --plus 1.5year --user-tz America/New_York --calendar-tz America/New_York",
          "  node true_time.mjs --plus 1century --time-source ntp",
          "  node true_time.mjs --target 2026-02-17T09:30:00 --target-tz Asia/Shanghai --user-tz America/Los_Angeles",
          "  node true_time.mjs --target 2026-11-01T01:30:00-07:00 --user-tz America/Los_Angeles",
        ].join("\n") + "\n",
      );
      process.exit(0);
    }
    fail(`Unknown argument '${arg}'`);
  }

  if (out.listTimezones) {
    if (out.plus || out.target) {
      fail("--list-timezones cannot be combined with --plus/--target");
    }
    return out;
  }

  if (out.timeSource !== "server" && out.timeSource !== "ntp") {
    fail("--time-source must be 'server' or 'ntp'");
  }

  if (Boolean(out.plus) === Boolean(out.target)) {
    fail("Provide exactly one of --plus or --target (or use --list-timezones)");
  }

  return out;
}

function assertTimeZone(tzName, label) {
  if (!tzName) return undefined;
  try {
    // Throws on invalid IANA zone names.
    // We only need validation; the formatter itself is not reused here.
    // eslint-disable-next-line no-new
    new Intl.DateTimeFormat("en-US", { timeZone: tzName });
    return tzName;
  } catch (error) {
    fail(`Invalid ${label} timezone '${tzName}'`);
  }
}

function parseNow(raw) {
  if (!raw) return Date.now();
  let value = raw.trim();
  if (value.endsWith("Z")) {
    // Keep as-is; Date.parse handles Z properly.
  } else if (!/[zZ]|[+-]\d{2}:?\d{2}$/.test(value)) {
    // Naive datetime is interpreted as UTC to match skill policy.
    value += "Z";
  }
  const ms = Date.parse(value);
  if (Number.isNaN(ms)) {
    fail(`Invalid --now datetime '${raw}'`);
  }
  return ms;
}

function parseNumericValue(raw, context) {
  const normalized = raw.replace(",", ".");
  const value = Number.parseFloat(normalized);
  if (!Number.isFinite(value) || value < 0) {
    fail(`Invalid numeric value '${raw}' in '${context}'`);
  }
  return value;
}

function parseDuration(raw) {
  const text = String(raw ?? "").trim().toLowerCase();
  if (!text) fail("Duration cannot be empty");
  const regex = /(\d+(?:[.,]\d+)?|\.\d+)\s*([a-z]+)/g;
  let fixedMilliseconds = 0;
  let calendarMonths = 0;
  let calendarYears = 0;
  let consumed = "";
  const tokens = [];
  for (const match of text.matchAll(regex)) {
    const rawValue = match[1];
    const value = parseNumericValue(rawValue, raw);
    const unit = match[2];
    if (FIXED_UNIT_MILLISECONDS.has(unit)) {
      const factor = FIXED_UNIT_MILLISECONDS.get(unit);
      const contributionMs = Math.round(value * factor);
      fixedMilliseconds += contributionMs;
      tokens.push({
        value,
        unit,
        kind: "fixed",
        milliseconds: contributionMs,
        seconds: Number((contributionMs / 1000).toFixed(3)),
      });
    } else if (CALENDAR_UNIT_MONTHS.has(unit)) {
      const factor = CALENDAR_UNIT_MONTHS.get(unit);
      calendarMonths += value * factor;
      tokens.push({ value, unit, kind: "calendar-month", months: value * factor });
    } else if (CALENDAR_UNIT_YEARS.has(unit)) {
      const factor = CALENDAR_UNIT_YEARS.get(unit);
      calendarYears += value * factor;
      tokens.push({
        value,
        unit,
        kind: "calendar-year",
        years: value * factor,
        months: value * factor * 12,
      });
    } else {
      fail(`Unsupported duration unit '${unit}' in '${raw}'`);
    }
    consumed += match[0];
  }
  if (!consumed || consumed.replace(/\s+/g, "") !== text.replace(/\s+/g, "")) {
    fail(`Unparsed duration segment in '${raw}'`);
  }
  return { fixedMilliseconds, calendarMonths, calendarYears, tokens };
}

function pad2(value) {
  return String(value).padStart(2, "0");
}

function parseOffsetMinutes(offsetLabel) {
  const normalized = String(offsetLabel).replace("UTC", "GMT");
  if (normalized === "GMT" || normalized === "GMT+0" || normalized === "GMT-0") {
    return 0;
  }
  const match = normalized.match(/^GMT([+-])(\d{1,2})(?::?(\d{2}))?$/);
  if (!match) {
    fail(`Unsupported timezone offset label '${offsetLabel}'`);
  }
  const sign = match[1] === "-" ? -1 : 1;
  const hours = Number.parseInt(match[2], 10);
  const minutes = Number.parseInt(match[3] ?? "0", 10);
  return sign * (hours * 60 + minutes);
}

function getTimeZoneParts(ms, tzName) {
  const formatter = new Intl.DateTimeFormat("en-CA", {
    timeZone: tzName,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
    timeZoneName: "shortOffset",
  });
  const parts = formatter.formatToParts(new Date(ms));
  const map = Object.fromEntries(parts.map((p) => [p.type, p.value]));
  const year = Number.parseInt(map.year, 10);
  const month = Number.parseInt(map.month, 10);
  const day = Number.parseInt(map.day, 10);
  const hour = Number.parseInt(map.hour, 10);
  const minute = Number.parseInt(map.minute, 10);
  const second = Number.parseInt(map.second, 10);
  const offsetMinutes = parseOffsetMinutes(map.timeZoneName);
  return { year, month, day, hour, minute, second, offsetMinutes };
}

function formatOffset(offsetMinutes) {
  const sign = offsetMinutes < 0 ? "-" : "+";
  const abs = Math.abs(offsetMinutes);
  const hh = Math.floor(abs / 60);
  const mm = abs % 60;
  return `${sign}${pad2(hh)}:${pad2(mm)}`;
}

function formatZonedIso(ms, tzName) {
  const p = getTimeZoneParts(ms, tzName);
  return `${p.year}-${pad2(p.month)}-${pad2(p.day)}T${pad2(p.hour)}:${pad2(p.minute)}:${pad2(
    p.second,
  )}${formatOffset(p.offsetMinutes)}`;
}

function formatUtcIso(ms) {
  return new Date(ms).toISOString().replace(".000Z", "Z");
}

function parseLocalDateTime(raw) {
  const match = String(raw)
    .trim()
    .match(
      /^(\d{4})-(\d{2})-(\d{2})[T\s](\d{2}):(\d{2})(?::(\d{2})(?:\.(\d{1,3}))?)?$/,
    );
  if (!match) {
    fail(
      `Invalid --target datetime '${raw}'. Use ISO like YYYY-MM-DDTHH:mm[:ss][.sss] with optional offset.`,
    );
  }
  return {
    year: Number.parseInt(match[1], 10),
    month: Number.parseInt(match[2], 10),
    day: Number.parseInt(match[3], 10),
    hour: Number.parseInt(match[4], 10),
    minute: Number.parseInt(match[5], 10),
    second: Number.parseInt(match[6] ?? "0", 10),
    millisecond: Number.parseInt((match[7] ?? "0").padEnd(3, "0"), 10),
  };
}

function sameLocalTime(ms, tzName, local) {
  const p = getTimeZoneParts(ms, tzName);
  return (
    p.year === local.year &&
    p.month === local.month &&
    p.day === local.day &&
    p.hour === local.hour &&
    p.minute === local.minute &&
    p.second === local.second
  );
}

function localFieldsToUtcMs(local) {
  return Date.UTC(
    local.year,
    local.month - 1,
    local.day,
    local.hour,
    local.minute,
    local.second,
    local.millisecond,
  );
}

function daysInMonthUtc(year, month1Based) {
  return new Date(Date.UTC(year, month1Based, 0)).getUTCDate();
}

function applyCalendarShift(local, yearsToAdd, monthsToAdd) {
  let year = local.year + yearsToAdd;
  let monthIndex = local.month - 1 + monthsToAdd;
  year += Math.floor(monthIndex / 12);
  monthIndex = ((monthIndex % 12) + 12) % 12;
  const month = monthIndex + 1;
  const day = Math.min(local.day, daysInMonthUtc(year, month));
  return { ...local, year, month, day };
}

function truncTowardZero(value) {
  return value < 0 ? Math.ceil(value) : Math.floor(value);
}

function localInZoneToUtcMs(local, tzName) {
  const naiveUtcMs = localFieldsToUtcMs(local);

  // First approximation: treat local time as UTC, then subtract zone offset.
  let guess = naiveUtcMs;

  // Two passes cover most DST boundaries.
  for (let i = 0; i < 2; i += 1) {
    const offsetMinutes = getTimeZoneParts(guess, tzName).offsetMinutes;
    guess = naiveUtcMs - offsetMinutes * 60 * 1000;
  }

  // Probe nearby offsets to detect DST ambiguity/invalid local times.
  const offsetCandidates = new Set([
    getTimeZoneParts(naiveUtcMs, tzName).offsetMinutes,
    getTimeZoneParts(naiveUtcMs - 6 * 3600 * 1000, tzName).offsetMinutes,
    getTimeZoneParts(naiveUtcMs + 6 * 3600 * 1000, tzName).offsetMinutes,
    getTimeZoneParts(guess - 2 * 3600 * 1000, tzName).offsetMinutes,
    getTimeZoneParts(guess, tzName).offsetMinutes,
    getTimeZoneParts(guess + 2 * 3600 * 1000, tzName).offsetMinutes,
  ]);

  const matches = [];
  for (const offsetMinutes of offsetCandidates) {
    const candidateMs = naiveUtcMs - offsetMinutes * 60 * 1000;
    if (sameLocalTime(candidateMs, tzName, local)) {
      matches.push(candidateMs);
    }
  }

  const uniqueMatches = [...new Set(matches)].sort((a, b) => a - b);
  if (uniqueMatches.length === 0) {
    fail(
      `Local target '${local.year}-${pad2(local.month)}-${pad2(local.day)}T${pad2(local.hour)}:${pad2(
        local.minute,
      )}:${pad2(local.second)}' is invalid in timezone '${tzName}' (DST spring-forward gap).`,
    );
  }
  if (uniqueMatches.length > 1) {
    fail(
      `Local target '${local.year}-${pad2(local.month)}-${pad2(local.day)}T${pad2(local.hour)}:${pad2(
        local.minute,
      )}:${pad2(local.second)}' is ambiguous in timezone '${tzName}' (DST fall-back overlap). Provide explicit offset in --target (e.g. -07:00 or -08:00).`,
    );
  }
  return uniqueMatches[0];
}

function addRelativeDuration(nowMs, duration, calendarTz) {
  let baseMs = nowMs;
  const totalCalendarMonths = duration.calendarMonths + duration.calendarYears * 12;
  if (totalCalendarMonths !== 0) {
    const p = getTimeZoneParts(baseMs, calendarTz);
    const local = {
      year: p.year,
      month: p.month,
      day: p.day,
      hour: p.hour,
      minute: p.minute,
      second: p.second,
      millisecond: new Date(baseMs).getUTCMilliseconds(),
    };
    const wholeMonths = truncTowardZero(totalCalendarMonths);
    const fractionalMonths = totalCalendarMonths - wholeMonths;

    const shifted = applyCalendarShift(local, 0, wholeMonths);
    baseMs = localInZoneToUtcMs(shifted, calendarTz);

    if (fractionalMonths !== 0) {
      const monthDays = daysInMonthUtc(shifted.year, shifted.month);
      const fractionalMilliseconds = Math.round(
        fractionalMonths * monthDays * 24 * 60 * 60 * 1000,
      );
      baseMs += fractionalMilliseconds;
    }
  }
  if (duration.fixedMilliseconds !== 0) {
    baseMs += duration.fixedMilliseconds;
  }
  return baseMs;
}

function parseTargetUtcMs(raw, targetTz) {
  const value = String(raw ?? "").trim();
  if (!value) fail("--target cannot be empty");

  const hasOffset = /(?:[zZ]|[+-]\d{2}:?\d{2})$/.test(value);
  if (hasOffset) {
    const ms = Date.parse(value);
    if (Number.isNaN(ms)) {
      fail(`Invalid --target datetime '${raw}'`);
    }
    return ms;
  }

  if (!targetTz) {
    fail(
      "--target has no timezone offset. Provide --target-tz (IANA timezone, e.g. Asia/Shanghai).",
    );
  }
  const local = parseLocalDateTime(value);
  return localInZoneToUtcMs(local, targetTz);
}

function detectServerTimeZone() {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
  } catch {
    return "UTC";
  }
}

function queryNtpServer(server, timeoutMs) {
  return new Promise((resolve, reject) => {
    const socket = dgram.createSocket("udp4");
    const packet = Buffer.alloc(48);
    packet[0] = 0x1b;

    let settled = false;
    const finalize = (fn, value) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      try {
        socket.close();
      } catch {
        // ignore close errors
      }
      fn(value);
    };

    const timer = setTimeout(
      () => finalize(reject, new Error(`timeout after ${timeoutMs}ms`)),
      timeoutMs,
    );

    socket.once("error", (error) => finalize(reject, error));
    socket.once("message", (message) => {
      if (!message || message.length < 48) {
        finalize(reject, new Error("invalid NTP response (too short)"));
        return;
      }
      const seconds1900 = message.readUInt32BE(40);
      const fraction = message.readUInt32BE(44);
      const unixSeconds = seconds1900 - 2208988800;
      const ms = unixSeconds * 1000 + Math.round((fraction * 1000) / 0x1_0000_0000);
      finalize(resolve, { nowMs: ms, server });
    });

    socket.send(packet, 0, packet.length, 123, server, (error) => {
      if (error) {
        finalize(reject, error);
      }
    });
  });
}

async function getNowFromNtp(servers, timeoutMs) {
  const errors = [];
  for (const server of servers) {
    try {
      return await queryNtpServer(server, timeoutMs);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      errors.push(`${server}: ${message}`);
    }
  }
  fail(`Failed to fetch time from NTP servers. ${errors.join(" | ")}`);
}

function formatChineseLunar(ms, tzName) {
  try {
    const formatter = new Intl.DateTimeFormat("zh-CN-u-ca-chinese", {
      timeZone: tzName,
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
    return formatter.format(new Date(ms));
  } catch {
    return null;
  }
}

async function resolveNowContext(args) {
  if (args.now) {
    return { nowMs: parseNow(args.now), timeSource: "override", ntpServer: null };
  }
  if (args.timeSource === "ntp") {
    const servers = args.ntpServers.length > 0 ? args.ntpServers : DEFAULT_NTP_SERVERS;
    const result = await getNowFromNtp(servers, args.ntpTimeoutMs);
    return { nowMs: result.nowMs, timeSource: "ntp", ntpServer: result.server };
  }
  return { nowMs: Date.now(), timeSource: "server", ntpServer: null };
}

function formatSecondsFromMilliseconds(milliseconds) {
  if (milliseconds % 1000 === 0) {
    return milliseconds / 1000;
  }
  return Number((milliseconds / 1000).toFixed(3));
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.listTimezones) {
    if (typeof Intl.supportedValuesOf !== "function") {
      fail("Intl.supportedValuesOf is not available in this Node runtime");
    }
    const zones = Intl.supportedValuesOf("timeZone");
    process.stdout.write(`# timezones (${zones.length})\n${zones.join("\n")}\n`);
    return;
  }

  const userTz = assertTimeZone(args.userTz, "user");
  const targetTz = assertTimeZone(args.targetTz, "target");
  const serverTz = assertTimeZone(args.serverTz, "server") || detectServerTimeZone();
  const calendarTz = assertTimeZone(args.calendarTz, "calendar") || userTz || serverTz || "UTC";
  const lunarTz = assertTimeZone(args.lunarTz, "lunar") || "Asia/Shanghai";
  const nowCtx = await resolveNowContext(args);
  const nowMs = nowCtx.nowMs;

  let targetMs;
  let deltaMilliseconds;
  let duration;
  if (args.plus) {
    duration = parseDuration(args.plus);
    targetMs = addRelativeDuration(nowMs, duration, calendarTz);
    deltaMilliseconds = targetMs - nowMs;
  } else {
    targetMs = parseTargetUtcMs(args.target, targetTz);
    deltaMilliseconds = targetMs - nowMs;
  }
  const deltaSeconds = formatSecondsFromMilliseconds(deltaMilliseconds);

  const result = {
    mode: args.plus ? "relative" : "absolute",
    input: args.plus ?? args.target,
    time_source: nowCtx.timeSource,
    ...(nowCtx.ntpServer ? { ntp_server: nowCtx.ntpServer } : {}),
    now_utc: formatUtcIso(nowMs),
    target_utc: formatUtcIso(targetMs),
    delta_milliseconds: deltaMilliseconds,
    delta_seconds: deltaSeconds,
    server_timezone: serverTz,
    now_server: formatZonedIso(nowMs, serverTz),
    target_server: formatZonedIso(targetMs, serverTz),
    lunar_timezone: lunarTz,
    now_lunar: formatChineseLunar(nowMs, lunarTz),
    target_lunar: formatChineseLunar(targetMs, lunarTz),
  };

  if (userTz) {
    result.user_timezone = userTz;
    result.now_user = formatZonedIso(nowMs, userTz);
    result.target_user = formatZonedIso(targetMs, userTz);
  }
  if (duration) {
    result.calendar_timezone = calendarTz;
    const totalCalendarMonths = duration.calendarMonths + duration.calendarYears * 12;
    result.duration_breakdown = {
      fixed_milliseconds: duration.fixedMilliseconds,
      fixed_seconds: formatSecondsFromMilliseconds(duration.fixedMilliseconds),
      calendar_months: duration.calendarMonths,
      calendar_years: duration.calendarYears,
      calendar_total_months: Number(totalCalendarMonths.toFixed(6)),
      tokens: duration.tokens,
    };
  }

  process.stdout.write(`${JSON.stringify(result)}\n`);
}

main().catch((error) => {
  const message = error instanceof Error ? error.message : String(error);
  fail(message);
});
