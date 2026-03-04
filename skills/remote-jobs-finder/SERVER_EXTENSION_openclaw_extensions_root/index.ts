/**
 * Local OpenClaw Extensions Root
 * Registers: rr_jobs_search
 *
 * Deploy to: ~/.openclaw/extensions/index.ts
 * Manifest:  ~/.openclaw/extensions/openclaw.plugin.json
 */
export default function (api: any) {
  // NOTE: OpenClaw may show this line in `openclaw plugins list` output.
  console.error("[local-extensions] registering tool rr_jobs_search");

  api.registerTool({
    name: "rr_jobs_search",
    description: "Search Remote Rocketship jobs via POST https://www.remoterocketship.com/api/openclaw/jobs",
    parameters: {
      type: "object",
      additionalProperties: false,
      properties: {
        filters: {
          type: "object",
          description: "Remote Rocketship filters object (page/itemsPerPage/jobTitleFilters/locationFilters/etc.)",
          additionalProperties: true
        },
        includeJobDescription: {
          type: "boolean",
          description: "If true, include large description fields. Default false."
        }
      },
      required: ["filters"]
    },
    async execute(_id: string, params: any) {
      const rrApiKey = process.env.RR_API_KEY;
      if (!rrApiKey) {
        return {
          content: [{ type: "text", text: "Missing RR_API_KEY on the OpenClaw server. Set it and restart the gateway." }],
        };
      }

      const payload = {
        filters: params?.filters ?? {},
        includeJobDescription: params?.includeJobDescription ?? false,
      };

      const res = await fetch("https://www.remoterocketship.com/api/openclaw/jobs", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${rrApiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const bodyText = await res.text();

      if (!res.ok) {
        return {
          content: [{ type: "text", text: `Remote Rocketship API error (${res.status}): ${bodyText.slice(0, 2000)}` }],
        };
      }

      // Return raw JSON string; the agent/skill will format it for WhatsApp.
      return { content: [{ type: "text", text: bodyText }] };
    },
  });
}
