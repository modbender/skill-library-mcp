import { ApiError, AgentspendApiClient } from "../lib/api.js";
import { resolveApiKeyWithAutoClaim } from "../lib/auth-flow.js";
import { formatUsd, usd6ToUsd } from "../lib/output.js";
import { normalizeMethod, parseBody, parseHeaders } from "../lib/request-options.js";

export interface CheckCommandOptions {
  method?: string;
  body?: string;
  header?: string[];
}

export async function runCheck(
  apiClient: AgentspendApiClient,
  url: string,
  options: CheckCommandOptions,
): Promise<void> {
  const apiKey = await resolveApiKeyWithAutoClaim(apiClient);

  try {
    const response = await apiClient.check(apiKey, {
      url,
      method: normalizeMethod(options.method),
      headers: parseHeaders(options.header),
      body: parseBody(options.body),
    });

    if (response.free) {
      if ((response.status ?? 200) >= 400) {
        console.log(`No payment required, but endpoint returned status ${response.status}.`);
        return;
      }

      console.log("This endpoint is free.");
      return;
    }

    const policyUsd =
      response.price_usd ?? (typeof response.price_usd6 === "number" ? usd6ToUsd(response.price_usd6) : null);
    const price = policyUsd !== null ? formatUsd(policyUsd) : "unavailable";
    const description = response.description ?? "unavailable";
    console.log(`Price: ${price}`);
    console.log(`Description: ${description}`);

    return;
  } catch (error) {
    if (error instanceof ApiError) {
      const body = error.body as { code?: string; details?: { header_names?: string[] } };
      if (error.status === 502 && body?.code === "UNSUPPORTED_PAYMENT_REQUIRED_FORMAT") {
        const headers = (body.details?.header_names ?? []).join(", ");
        console.error(
          `Endpoint returned 402 with an unsupported payment format. Headers seen: ${headers || "none"}.`,
        );
        return;
      }
    }

    throw error;
  }
}
