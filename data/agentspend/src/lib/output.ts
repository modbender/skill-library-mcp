import type { StatusCharge, StatusResponse } from "../types.js";

const USD6_SCALE = 1_000_000;

function formatUsdNumber(value: number, minDecimals = 2, maxDecimals = 6): string {
  const fixed = value.toFixed(maxDecimals);
  const trimmed = fixed.replace(/(\.\d*?)0+$/, "$1").replace(/\.$/, "");

  if (!trimmed.includes(".")) {
    return minDecimals > 0 ? `${trimmed}.${"0".repeat(minDecimals)}` : trimmed;
  }

  const [whole, frac = ""] = trimmed.split(".");
  if (frac.length >= minDecimals) {
    return trimmed;
  }

  return `${whole}.${frac.padEnd(minDecimals, "0")}`;
}

export function usd6ToUsd(usd6: number): number {
  return usd6 / USD6_SCALE;
}

export function formatUsd(usd: number): string {
  if (!Number.isFinite(usd)) {
    return "unknown";
  }

  return `$${formatUsdNumber(usd, 2, 6)}`;
}

export function formatUsdEstimate(estimatedUsd: number | null | undefined, fallbackUsd?: number | null): string {
  if (typeof estimatedUsd === "number") {
    return formatUsd(estimatedUsd);
  }

  if (typeof fallbackUsd === "number") {
    return formatUsd(fallbackUsd);
  }

  return "unknown";
}

export function formatJson(value: unknown): string {
  if (typeof value === "string") {
    return value;
  }

  return JSON.stringify(value, null, 2);
}

export function relativeTime(iso: string): string {
  const timestamp = new Date(iso).getTime();
  const diffMs = Date.now() - timestamp;
  const abs = Math.max(0, Math.floor(diffMs / 1000));

  if (abs < 60) {
    return `${abs}s ago`;
  }

  const minutes = Math.floor(abs / 60);
  if (minutes < 60) {
    return `${minutes}m ago`;
  }

  const hours = Math.floor(minutes / 60);
  if (hours < 24) {
    return `${hours}h ago`;
  }

  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

function formatCharge(charge: StatusCharge): string {
  const amountUsd = charge.amount_usd ?? usd6ToUsd(charge.amount_usd6);
  const amount = formatUsd(amountUsd).padEnd(10);
  const domain = charge.target_domain.padEnd(24);
  const when = relativeTime(charge.created_at);

  return `  ${amount} ${domain} ${when}`;
}

export function printStatus(status: StatusResponse): void {
  console.log(`Weekly budget:   ${formatUsd(status.weekly_budget_usd)}`);
  console.log(`Spent this week: ${formatUsd(status.spent_this_week_usd)}`);
  console.log(`Remaining:       ${formatUsd(status.remaining_budget_usd)}`);
  console.log("");

  if (status.recent_charges.length === 0) {
    console.log("Recent charges: none");
    return;
  }

  console.log("Recent charges:");
  for (const charge of status.recent_charges) {
    console.log(formatCharge(charge));
  }
}
