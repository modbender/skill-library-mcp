// Deterministic weather change alert (Open-Meteo, no key)
// Usage:
//   node weather_alert.js <lat> <lon> [--mode day_hike|summit_camp|trail_run] [--tz Asia/Shanghai] [--hours 6]
// Output:
//   Either nothing (exit 0, no stdout) OR one line:
//   WX ALERT: <CODE> <brief>
//
// Notes:
// - Keep it low-token: one line max.
// - Designed to be called from guide workflows.

function parseArgs(argv) {
  const pos = [];
  const flags = {};
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith("--")) {
      const key = a.slice(2);
      const next = argv[i + 1];
      if (next != null && !next.startsWith("--")) {
        flags[key] = next;
        i++;
      } else {
        flags[key] = true;
      }
    } else {
      pos.push(a);
    }
  }
  return { pos, flags };
}

const { pos, flags } = parseArgs(process.argv);
const lat = Number(pos[0]);
const lon = Number(pos[1]);
if (!Number.isFinite(lat) || !Number.isFinite(lon)) {
  console.error("Usage: node weather_alert.js <lat> <lon> [--mode day_hike|summit_camp|trail_run] [--tz Asia/Shanghai] [--hours 6]");
  process.exit(1);
}

const mode = String(flags.mode || "day_hike");
const tz = String(flags.tz || "Asia/Shanghai");
const hours = Math.max(2, Math.min(12, Number(flags.hours || (mode === "summit_camp" ? 6 : mode === "trail_run" ? 2 : 3))));

const thresholdsByMode = {
  day_hike: {
    windUp_ms_3h: 6,
    gustUp_ms_3h: 10,
    visDown_km_2h: 3,
    visBelow_km_2h: 2,
    popUp_pct_2h: 30,
    rainMm_3h: 3,
    tempDown_c_3h: 4,
  },
  summit_camp: {
    windUp_ms_3h: 5,
    gustUp_ms_3h: 8,
    visDown_km_2h: 2,
    visBelow_km_2h: 2,
    popUp_pct_2h: 25,
    rainMm_3h: 2,
    tempDown_c_3h: 3,
  },
  trail_run: {
    windUp_ms_3h: 7,
    gustUp_ms_3h: 12,
    visDown_km_2h: 3,
    visBelow_km_2h: 2,
    popUp_pct_2h: 35,
    rainMm_3h: 3,
    tempDown_c_3h: 4,
  },
};

const th = thresholdsByMode[mode] || thresholdsByMode.day_hike;

function maxDelta(arr, windowH, dir) {
  // dir: 'up' => max(arr[i+w]-arr[i]); 'down' => max(arr[i]-arr[i+w])
  let best = -Infinity;
  let at = null;
  for (let i = 0; i + windowH < arr.length; i++) {
    const d = dir === "down" ? arr[i] - arr[i + windowH] : arr[i + windowH] - arr[i];
    if (d > best) {
      best = d;
      at = i;
    }
  }
  return { best, at };
}

function sumWindow(arr, windowH) {
  let best = -Infinity;
  for (let i = 0; i + windowH <= arr.length; i++) {
    let s = 0;
    for (let j = i; j < i + windowH; j++) s += arr[j];
    if (s > best) best = s;
  }
  return best;
}

function hoursToStr(h) {
  return `${h}h`;
}

const hourly = [
  "temperature_2m",
  "precipitation_probability",
  "precipitation",
  "wind_speed_10m",
  "wind_gusts_10m",
  "visibility",
];

const url = new URL("https://api.open-meteo.com/v1/forecast");
url.searchParams.set("latitude", String(lat));
url.searchParams.set("longitude", String(lon));
url.searchParams.set("timezone", tz);
url.searchParams.set("forecast_days", "2");
url.searchParams.set("hourly", hourly.join(","));

const res = await fetch(url.toString());
if (!res.ok) process.exit(0);
const j = await res.json();
const H = j?.hourly;
if (!H) process.exit(0);

function take(name) {
  const a = H[name];
  if (!Array.isArray(a)) return null;
  return a.slice(0, hours + 1).map((x) => Number(x));
}

const wind = take("wind_speed_10m");
const gust = take("wind_gusts_10m");
const visM = take("visibility");
const pop = take("precipitation_probability");
const rain = take("precipitation");
const temp = take("temperature_2m");

if (!wind || !gust || !visM || !pop || !rain || !temp) process.exit(0);

const visKm = visM.map((m) => m / 1000);

// compute candidate alerts
const cand = [];

// wind up in 3h
if (wind.length >= 4) {
  const { best } = maxDelta(wind, 3, "up");
  if (best >= th.windUp_ms_3h) cand.push({ prio: 90, line: `WX ALERT: WIND_UP +${Math.round(best)}m/s in ${hoursToStr(3)}` });
}
if (gust.length >= 4) {
  const { best } = maxDelta(gust, 3, "up");
  if (best >= th.gustUp_ms_3h) cand.push({ prio: 95, line: `WX ALERT: GUST_UP +${Math.round(best)}m/s in ${hoursToStr(3)}` });
}

// visibility down in 2h
if (visKm.length >= 3) {
  const { best } = maxDelta(visKm, 2, "down");
  const min2h = Math.min(...visKm.slice(0, 3));
  if (min2h <= th.visBelow_km_2h) cand.push({ prio: 92, line: `WX ALERT: VIS_DOWN <${th.visBelow_km_2h}km in ${hoursToStr(2)}` });
  else if (best >= th.visDown_km_2h) cand.push({ prio: 80, line: `WX ALERT: VIS_DOWN -${best.toFixed(0)}km in ${hoursToStr(2)}` });
}

// rain probability up
if (pop.length >= 3) {
  const { best } = maxDelta(pop, 2, "up");
  const maxSoon = Math.max(...pop.slice(0, 3));
  if (best >= th.popUp_pct_2h) cand.push({ prio: 75, line: `WX ALERT: RAIN_UP >${Math.round(maxSoon)}% next ${hoursToStr(2)}` });
}

// rain amount window (3h)
if (rain.length >= 4) {
  const best3h = sumWindow(rain, 3);
  if (best3h >= th.rainMm_3h) cand.push({ prio: 70, line: `WX ALERT: RAIN_MM ${best3h.toFixed(0)}mm in ${hoursToStr(3)}` });
}

// temp down in 3h
if (temp.length >= 4) {
  const { best } = maxDelta(temp, 3, "down");
  if (best >= th.tempDown_c_3h) cand.push({ prio: 60, line: `WX ALERT: TEMP_DOWN -${best.toFixed(0)}C in ${hoursToStr(3)}` });
}

if (!cand.length) process.exit(0);

cand.sort((a, b) => b.prio - a.prio);
process.stdout.write(cand[0].line + "\n");
