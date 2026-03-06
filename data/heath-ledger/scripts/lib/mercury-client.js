const MERCURY_BASE_URL = "https://api.mercury.com/api/v1";

export async function mercuryRequest(token, path, params = {}) {
  const url = new URL(`${MERCURY_BASE_URL}${path}`);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, String(value));
    }
  });

  const response = await fetch(url.toString(), {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Mercury API error (${response.status}): ${errorText}`);
  }

  return response.json();
}
