import fs from "fs";
import path from "path";

export function snapshotDiff(prev = [], next = []) {
  const prevMap = new Map((prev || []).map((x) => [x.listingKey, x]));
  const nextMap = new Map((next || []).map((x) => [x.listingKey, x]));

  const events = [];

  for (const [k, n] of nextMap.entries()) {
    if (!prevMap.has(k)) {
      if (n.status === "for_sale") events.push({ type: "new_for_sale", listing: n });
      else if (n.status === "for_rent") events.push({ type: "new_for_rent", listing: n });
      else events.push({ type: "new_listing", listing: n });
      continue;
    }

    const p = prevMap.get(k);
    if (p.status !== "sold" && n.status === "sold") {
      events.push({ type: "status_changed_to_sold", listing: n, previous: p });
    }
  }

  return events;
}

export function loadLatestSnapshot(snapshotDir) {
  try {
    const files = fs.readdirSync(snapshotDir).filter((f) => f.endsWith(".json")).sort();
    if (!files.length) return [];
    const fp = path.join(snapshotDir, files[files.length - 1]);
    const obj = JSON.parse(fs.readFileSync(fp, "utf8"));
    return obj.listings || [];
  } catch {
    return [];
  }
}

export function writeSnapshot(snapshotDir, listings) {
  fs.mkdirSync(snapshotDir, { recursive: true });
  const ts = new Date().toISOString().replace(/[:]/g, "-");
  const fp = path.join(snapshotDir, `${ts}.json`);
  fs.writeFileSync(fp, JSON.stringify({ capturedAt: new Date().toISOString(), listings }, null, 2));
  return fp;
}
