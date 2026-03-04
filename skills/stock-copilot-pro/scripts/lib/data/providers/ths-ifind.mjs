import { DataProvider } from "./base.mjs";
import { executeTool } from "../../infra/qveris-client.mjs";
import { parseCapability } from "../parser.mjs";
import { toThsCode } from "../../market/resolver.mjs";

function latestCompletedReportPeriod() {
  const now = new Date();
  const month = now.getMonth() + 1;
  let year = now.getFullYear();
  let period = "0930";
  if (month <= 4) {
    year -= 1;
    period = "0930";
  } else if (month <= 8) {
    period = "0331";
  } else if (month <= 10) {
    period = "0630";
  } else {
    period = "0930";
  }
  return { year: String(year), period };
}

function historyDateRange(days = 45) {
  const end = new Date();
  const start = new Date(Date.now() - days * 24 * 60 * 60 * 1000);
  const fmt = (d) => d.toISOString().slice(0, 10);
  return { start: fmt(start), end: fmt(end) };
}

export class ThsIfindProvider extends DataProvider {
  constructor() {
    super("ths-ifind", ["CN", "HK"]);
  }

  get capabilities() {
    return ["quote", "fundamentals", "technicals"];
  }

  buildRequest(capability, symbol, market) {
    const code = toThsCode(symbol, market);
    if (capability === "quote") {
      return { toolId: "ths_ifind.real_time_quotation.v1", params: { codes: code } };
    }
    if (capability === "fundamentals") {
      const report = latestCompletedReportPeriod();
      return {
        toolId: "ths_ifind.financial_statements.v1",
        params: {
          statement_type: "income",
          codes: code,
          year: report.year,
          period: report.period,
          type: "1",
        },
      };
    }
    if (capability === "technicals") {
      const range = historyDateRange(45);
      return {
        toolId: "ths_ifind.history_quotation.v1",
        params: {
          codes: code,
          startdate: range.start,
          enddate: range.end,
          interval: "D",
        },
      };
    }
    return null;
  }

  async fetch(capability, symbol, context = {}) {
    const market = context.market || "CN";
    const request = this.buildRequest(capability, symbol, market);
    if (!request) return { success: false, reason: "unsupported capability" };
    const raw = await executeTool(
      request.toolId,
      context.searchId || null,
      request.params,
      context.maxSize || 30_000,
      context.timeoutMs || 25_000,
    );
    return {
      success: Boolean(raw?.success !== false),
      provider: this.name,
      toolId: request.toolId,
      params: request.params,
      raw,
      parsed: this.parse(capability, raw),
    };
  }

  parse(capability, rawResponse) {
    return parseCapability(capability, rawResponse);
  }
}
