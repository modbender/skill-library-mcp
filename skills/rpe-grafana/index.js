export default function (api) {
  // Config can be at api.config (flat) or api.config.plugins.entries["rpe-grafana"].config (nested)
  const getPluginConfig = () => {
    const nested = api.config?.plugins?.entries?.["rpe-grafana"]?.config;
    if (nested) return nested;
    return api.config || {};
  };
  
  const getConfig = () => {
    const pc = getPluginConfig();
    return {
      url: (pc.url || process.env.GRAFANA_URL || "").replace(/\/$/, ""),
      user: pc.user || process.env.GRAFANA_USER || "admin",
      password: pc.password || process.env.GRAFANA_PASSWORD || "",
    };
  };

  const basicAuth = (user, password) =>
    "Basic " + Buffer.from(`${user}:${password}`).toString("base64");

  const grafanaFetch = (url, user, password, path, options = {}) =>
    fetch(`${url}${path}`, {
      ...options,
      headers: {
        Authorization: basicAuth(user, password),
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

  // Grafana can nest panels inside row panels; flatten one level.
  const flattenPanels = (panels = []) =>
    panels.flatMap((p) => (p.type === "row" && p.panels ? p.panels : [p]));

  // Extract a compact summary from a /api/ds/query response.
  const summarizeFrames = (results) => {
    const summary = [];
    for (const [refId, result] of Object.entries(results)) {
      for (const frame of result.frames ?? []) {
        const fields = frame.schema?.fields ?? [];
        // The value field is the first non-time numeric field, fallback to index 1.
        const valueField =
          fields.find((f) => f.type === "number") ?? fields[1] ?? {};
        const valueIndex = fields.indexOf(valueField);
        const rawValues = frame.data?.values?.[valueIndex] ?? [];
        const lastValue = rawValues.length > 0 ? rawValues[rawValues.length - 1] : null;
        summary.push({
          refId,
          name: frame.schema?.name ?? valueField.name ?? refId,
          lastValue,
          unit: valueField.config?.unit ?? "",
        });
      }
    }
    return summary;
  };

  const ok = (data) => ({
    content: [{ type: "text", text: JSON.stringify(data) }],
  });

  // ── Tool 1: List dashboards ───────────────────────────────────────────────
  api.registerTool({
    name: "grafana_list_dashboards",
    description: "List all Grafana dashboards. Returns [{uid, title}].",
    parameters: {
      type: "object",
      properties: {},
      additionalProperties: false,
    },
    optional: true,
    async execute() {
      const { url, user, password } = getConfig();
      const res = await grafanaFetch(url, user, password, "/api/search?type=dash-db");
      if (!res.ok) throw new Error(`Grafana ${res.status}: ${await res.text()}`);
      const data = await res.json();
      return ok(data.map((d) => ({ uid: d.uid, title: d.title })));
    },
  });

  // ── Tool 2: List panels ───────────────────────────────────────────────────
  api.registerTool({
    name: "grafana_list_panels",
    description: "List all panels in a Grafana dashboard. Returns [{id, title}].",
    parameters: {
      type: "object",
      properties: {
        dashboard_uid: {
          type: "string",
          description: "UID of the dashboard (from grafana_list_dashboards).",
        },
      },
      required: ["dashboard_uid"],
      additionalProperties: false,
    },
    optional: true,
    async execute({ dashboard_uid }) {
      const { url, user, password } = getConfig();
      const res = await grafanaFetch(
        url,
        user,
        password,
        `/api/dashboards/uid/${encodeURIComponent(dashboard_uid)}`
      );
      if (!res.ok) throw new Error(`Grafana ${res.status}: ${await res.text()}`);
      const { dashboard } = await res.json();
      const panels = flattenPanels(dashboard?.panels);
      return ok(panels.map((p) => ({ id: p.id, title: p.title })));
    },
  });

  // ── Tool 3: Query panel data ──────────────────────────────────────────────
  api.registerTool({
    name: "grafana_query_panel",
    description:
      "Query the data for a specific panel. Returns a compact summary [{refId, name, lastValue, unit}].",
    parameters: {
      type: "object",
      properties: {
        dashboard_uid: {
          type: "string",
          description: "UID of the dashboard.",
        },
        panel_id: {
          type: "number",
          description: "Numeric ID of the panel (from grafana_list_panels).",
        },
        from: {
          type: "string",
          description: "Start of the time range (default: now-1h).",
        },
        to: {
          type: "string",
          description: "End of the time range (default: now).",
        },
      },
      required: ["dashboard_uid", "panel_id"],
      additionalProperties: false,
    },
    optional: true,
    async execute({ dashboard_uid, panel_id, from = "now-1h", to = "now" }) {
      const { url, user, password } = getConfig();

      // Fetch dashboard to resolve panel targets and datasource.
      const dashRes = await grafanaFetch(
        url,
        user,
        password,
        `/api/dashboards/uid/${encodeURIComponent(dashboard_uid)}`
      );
      if (!dashRes.ok) throw new Error(`Grafana ${dashRes.status}: ${await dashRes.text()}`);
      const { dashboard } = await dashRes.json();

      const panel = flattenPanels(dashboard?.panels).find((p) => p.id === panel_id);
      if (!panel) throw new Error(`Panel ${panel_id} not found in dashboard ${dashboard_uid}`);

      const targets = panel.targets ?? [];
      if (targets.length === 0) throw new Error(`Panel ${panel_id} has no query targets`);

      // Resolve datasource UID: panel-level datasource takes precedence over per-target.
      const panelDsUid =
        typeof panel.datasource === "object" ? panel.datasource?.uid : undefined;

      const queries = targets.map((t) => {
        const targetDsUid =
          typeof t.datasource === "object" ? t.datasource?.uid : undefined;
        const dsUid = panelDsUid ?? targetDsUid;
        return {
          intervalMs: 60000,
          maxDataPoints: 100,
          ...t,
          ...(dsUid ? { datasource: { uid: dsUid } } : {}),
        };
      });

      const queryRes = await grafanaFetch(url, user, password, "/api/ds/query", {
        method: "POST",
        body: JSON.stringify({ queries, from, to }),
      });
      if (!queryRes.ok) throw new Error(`Grafana query ${queryRes.status}: ${await queryRes.text()}`);
      const { results } = await queryRes.json();

      return ok(summarizeFrames(results ?? {}));
    },
  });
}
