import fetch from "node-fetch";

export async function httpGetJson<T>(url: string, headers?: Record<string, string>): Promise<T> {
  const res = await fetch(url, {
    method: "GET",
    headers: {
      "user-agent": process.env.USER_AGENT || "solana-memecoin-guardian/1.0",
      ...(headers || {}),
    },
  });
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
  return (await res.json()) as T;
}
