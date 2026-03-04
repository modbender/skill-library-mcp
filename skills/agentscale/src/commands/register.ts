import { API_URL, saveApiKey } from "../config.js";

export async function register(): Promise<void> {
  const res = await fetch(`${API_URL}/register`, { method: "POST" });
  const data = await res.json();
  saveApiKey(data.apiKey);
  console.log("API key saved to ~/.agentscale/config.json");
}
