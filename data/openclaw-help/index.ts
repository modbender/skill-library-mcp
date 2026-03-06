export default function register(api: any) {
  const cfg = (api.pluginConfig ?? {}) as {
    enabled?: boolean;
    includeTips?: boolean;
    // Optional: user-supplied help sections. Keep defaults generic.
    sections?: Array<{ title: string; lines: string[] }>;
  };
  if (cfg.enabled === false) return;

  const includeTips = cfg.includeTips !== false;

  api.registerCommand({
    name: "help",
    description: "Show help and local shortcuts (generic by default)",
    usage: "/help",
    run: async () => {
      const lines: string[] = [];
      lines.push("Help");
      lines.push("");

      // Generic placeholders only. Users can configure their own sections.
      const sections = cfg.sections ?? [
        {
          title: "Shortcuts",
          lines: [
            "- /<project>   - Project shortcut (configured by user)",
            "- /<command>   - A custom command (configured by user)",
          ],
        },
        {
          title: "Memory",
          lines: [
            "- /remember-<x> <text>  - Save a note (if installed)",
            "- <trigger phrase>: ... - Optional explicit capture trigger",
          ],
        },
        {
          title: "TODO",
          lines: [
            "- /todo-list",
            "- /todo-add <text>",
            "- /todo-done <index>",
          ],
        },
      ];

      for (const s of sections) {
        lines.push(s.title + ":");
        for (const ln of s.lines) lines.push(ln);
        lines.push("");
      }

      if (includeTips) {
        lines.push("Tips:");
        lines.push("- Keep infrastructure changes ask-first.");
        lines.push("- Keep secrets out of repos.");
        lines.push("");
      }

      lines.push("(This /help output is intentionally generic. Configure your own sections in plugin config.)");

      return { ok: true, message: lines.join("\n") };
    },
  });
}
