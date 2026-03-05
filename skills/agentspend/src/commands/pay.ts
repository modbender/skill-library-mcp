import { ApiError, AgentspendApiClient } from "../lib/api.js";
import { resolveApiKeyWithAutoClaim } from "../lib/auth-flow.js";
import { formatJson, formatUsd, formatUsdEstimate, usd6ToUsd } from "../lib/output.js";
import { normalizeMethod, parseBody, parseHeaders } from "../lib/request-options.js";

export interface PayCommandOptions {
  method?: string;
  body?: string;
  header?: string[];
  maxCost?: number;
}

type PayErrorCode =
  | "PRICE_EXCEEDS_MAX"
  | "PRICE_NOT_CONVERTIBLE"
  | "WEEKLY_BUDGET_EXCEEDED"
  | "DOMAIN_NOT_ALLOWLISTED";

interface PayErrorDetails {
  offered_price_usd6?: number;
  offered_price_usd?: number;
  max_cost_usd6?: number;
  max_cost_usd?: number;
  weekly_limit_usd6?: number;
  weekly_limit_usd?: number;
  spent_this_week_usd6?: number;
  spent_this_week_usd?: number;
  attempted_charge_usd6?: number;
  attempted_charge_usd?: number;
  estimated_usd?: number;
  amount_display?: string;
  currency?: string;
}

interface ParsedPayErrorBody {
  code?: PayErrorCode;
  details?: PayErrorDetails;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function readNumber(record: Record<string, unknown>, key: string): number | undefined {
  const value = record[key];
  return typeof value === "number" && Number.isFinite(value) ? value : undefined;
}

function readString(record: Record<string, unknown>, key: string): string | undefined {
  const value = record[key];
  return typeof value === "string" ? value : undefined;
}

function parsePayErrorCode(value: unknown): PayErrorCode | undefined {
  if (typeof value !== "string") {
    return undefined;
  }

  if (
    value === "PRICE_EXCEEDS_MAX" ||
    value === "PRICE_NOT_CONVERTIBLE" ||
    value === "WEEKLY_BUDGET_EXCEEDED" ||
    value === "DOMAIN_NOT_ALLOWLISTED"
  ) {
    return value;
  }

  return undefined;
}

function parsePayErrorBody(body: unknown): ParsedPayErrorBody {
  if (!isRecord(body)) {
    return {};
  }

  const parsed: ParsedPayErrorBody = {
    code: parsePayErrorCode(body.code),
  };

  if (!isRecord(body.details)) {
    return parsed;
  }

  const detailsRecord = body.details;
  parsed.details = {
    offered_price_usd6: readNumber(detailsRecord, "offered_price_usd6"),
    offered_price_usd: readNumber(detailsRecord, "offered_price_usd"),
    max_cost_usd6: readNumber(detailsRecord, "max_cost_usd6"),
    max_cost_usd: readNumber(detailsRecord, "max_cost_usd"),
    weekly_limit_usd6: readNumber(detailsRecord, "weekly_limit_usd6"),
    weekly_limit_usd: readNumber(detailsRecord, "weekly_limit_usd"),
    spent_this_week_usd6: readNumber(detailsRecord, "spent_this_week_usd6"),
    spent_this_week_usd: readNumber(detailsRecord, "spent_this_week_usd"),
    attempted_charge_usd6: readNumber(detailsRecord, "attempted_charge_usd6"),
    attempted_charge_usd: readNumber(detailsRecord, "attempted_charge_usd"),
    estimated_usd: readNumber(detailsRecord, "estimated_usd"),
    amount_display: readString(detailsRecord, "amount_display"),
    currency: readString(detailsRecord, "currency"),
  };

  return parsed;
}

export async function runPay(apiClient: AgentspendApiClient, url: string, options: PayCommandOptions): Promise<void> {
  const apiKey = await resolveApiKeyWithAutoClaim(apiClient);
  const method = normalizeMethod(options.method);

  try {
    const response = await apiClient.pay(apiKey, {
      url,
      method,
      headers: parseHeaders(options.header),
      body: parseBody(options.body),
      max_cost_usd: options.maxCost,
    });

    console.log(formatJson(response.body));

    if (response.payment) {
      console.log(
        `\nCharged: ${formatUsd(response.payment.charged_usd)} | Remaining: ${formatUsd(response.payment.remaining_budget_usd)}`,
      );
    }
  } catch (error) {
    if (error instanceof ApiError) {
      const body = parsePayErrorBody(error.body);

      if (error.status === 400 && body.code === "PRICE_EXCEEDS_MAX") {
        const offered =
          body.details?.offered_price_usd ??
          (typeof body.details?.offered_price_usd6 === "number" ? usd6ToUsd(body.details.offered_price_usd6) : 0);
        const max =
          body.details?.max_cost_usd ??
          (typeof body.details?.max_cost_usd6 === "number" ? usd6ToUsd(body.details.max_cost_usd6) : 0);
        const estimatedUsd = body.details?.estimated_usd;
        const amountDisplay = body.details?.amount_display;
        const currency = body.details?.currency ?? "USDC";

        console.error(
          `Price ${formatUsd(offered)} exceeds --max-cost ${formatUsd(max)}. Run without --max-cost or increase it.`,
        );

        if (amountDisplay) {
          console.error(
            `Offered token amount: ${amountDisplay} ${currency} (~${formatUsdEstimate(estimatedUsd, offered)})`,
          );
        }

        return;
      }

      if (error.status === 400 && body.code === "PRICE_NOT_CONVERTIBLE") {
        console.error("Price could not be converted to 6-decimal USD units for policy checks.");
        return;
      }

      if (error.status === 402 && body.code === "WEEKLY_BUDGET_EXCEEDED") {
        const weeklyLimit =
          body.details?.weekly_limit_usd ??
          (typeof body.details?.weekly_limit_usd6 === "number" ? usd6ToUsd(body.details.weekly_limit_usd6) : 0);
        const spent =
          body.details?.spent_this_week_usd ??
          (typeof body.details?.spent_this_week_usd6 === "number" ? usd6ToUsd(body.details.spent_this_week_usd6) : 0);
        const attempted =
          body.details?.attempted_charge_usd ??
          (typeof body.details?.attempted_charge_usd6 === "number" ? usd6ToUsd(body.details.attempted_charge_usd6) : 0);

        console.error(
          `Weekly budget exceeded. Limit ${formatUsd(weeklyLimit)}, spent ${formatUsd(spent)}, attempted ${formatUsd(attempted)}.`,
        );
        return;
      }

      if (error.status === 403 && body.code === "DOMAIN_NOT_ALLOWLISTED") {
        console.error("This domain is not in your AgentSpend allowlist.");
        return;
      }
    }

    throw error;
  }
}
