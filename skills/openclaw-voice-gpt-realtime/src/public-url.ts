import { isIP } from "node:net";
import { lookup } from "node:dns/promises";

const LOCAL_HOSTNAMES = new Set(["localhost", "localhost.localdomain"]);
const PRIVATE_SUFFIXES = [".local", ".internal", ".lan", ".home", ".arpa"];

export function normalizeAndValidatePublicUrl(rawUrl: string): string {
  let url: URL;
  try {
    url = new URL(rawUrl);
  } catch {
    throw new Error("Public URL must be a valid URL");
  }

  if (url.protocol !== "https:") {
    throw new Error("Public URL must use HTTPS");
  }

  if (url.username || url.password) {
    throw new Error("Public URL must not include username/password");
  }

  if (url.pathname && url.pathname !== "/") {
    throw new Error("Public URL must not include a path. Use only the origin (e.g. https://example.com)");
  }

  if (url.search || url.hash) {
    throw new Error("Public URL must not include query params or fragments");
  }

  const hostname = url.hostname.toLowerCase();
  if (isLocalOrPrivateHostname(hostname)) {
    throw new Error(
      "Public URL host is not allowed. Use a publicly reachable tunnel/domain, not localhost or private/internal addresses"
    );
  }

  // Normalize to origin form without trailing slash.
  return url.origin;
}

export async function assertPublicUrlResolvesToPublicIp(publicUrl: string): Promise<void> {
  const hostname = new URL(publicUrl).hostname;
  const records = await lookup(hostname, { all: true, verbatim: true });

  if (records.length === 0) {
    throw new Error("Public URL hostname did not resolve to any IP address");
  }

  for (const record of records) {
    if (isLocalOrPrivateHostname(record.address)) {
      throw new Error(
        `Public URL hostname resolves to a private/local IP (${record.address}). Use a public tunnel/domain instead`
      );
    }
  }
}

export function isLocalOrPrivateHostname(hostname: string): boolean {
  const normalized = hostname.toLowerCase();
  const ipVersion = isIP(normalized);

  if (LOCAL_HOSTNAMES.has(normalized)) return true;
  if (ipVersion === 4) return isPrivateIpv4(normalized);
  if (ipVersion === 6) return isPrivateIpv6(normalized);
  if (!normalized.includes(".")) return true;
  if (PRIVATE_SUFFIXES.some((suffix) => normalized.endsWith(suffix))) return true;

  return false;
}

function isPrivateIpv4(ip: string): boolean {
  const octets = ip.split(".").map((x) => Number.parseInt(x, 10));
  if (octets.length !== 4 || octets.some((n) => Number.isNaN(n) || n < 0 || n > 255)) return true;

  const [a, b] = octets;

  if (a === 10) return true; // RFC1918
  if (a === 127) return true; // loopback
  if (a === 169 && b === 254) return true; // link-local
  if (a === 172 && b >= 16 && b <= 31) return true; // RFC1918
  if (a === 192 && b === 168) return true; // RFC1918
  if (a === 100 && b >= 64 && b <= 127) return true; // CGNAT
  if (a === 0) return true; // current network
  if (a >= 224) return true; // multicast/reserved
  if (a === 198 && (b === 18 || b === 19)) return true; // benchmark testing

  return false;
}

function isPrivateIpv6(ip: string): boolean {
  const normalized = ip.toLowerCase();
  if (normalized === "::" || normalized === "::1") return true; // unspecified / loopback
  if (normalized.startsWith("fe8") || normalized.startsWith("fe9") || normalized.startsWith("fea") || normalized.startsWith("feb")) {
    return true; // fe80::/10 link-local
  }
  if (normalized.startsWith("fc") || normalized.startsWith("fd")) return true; // fc00::/7 unique local
  return false;
}
