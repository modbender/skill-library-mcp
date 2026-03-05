const ISSUE_REPO_SLUG_RE = /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/;

export function shellQuote(value: string): string {
  return `'${String(value).replace(/'/g, `"'"'`)}'`;
}

export function isValidIssueRepoSlug(value: string): boolean {
  return ISSUE_REPO_SLUG_RE.test(value.trim());
}

export function resolveIssueRepo(configValue: unknown, envValue: unknown, defaultRepo: string): string {
  const candidates = [configValue, envValue, defaultRepo];
  for (const candidate of candidates) {
    if (typeof candidate !== "string") continue;
    const trimmed = candidate.trim();
    if (trimmed && isValidIssueRepoSlug(trimmed)) {
      return trimmed;
    }
  }
  return defaultRepo;
}

export function buildGhIssueCreateCommand(args: {
  repo: string;
  title: string;
  body: string;
  labels?: string[];
}): string {
  const repo = args.repo.trim();
  if (!isValidIssueRepoSlug(repo)) {
    throw new Error(`Invalid issue repository slug: ${args.repo}`);
  }

  const labels = (args.labels ?? []).map((label) => label.trim()).filter(Boolean);
  const parts = [
    "gh issue create",
    `-R ${shellQuote(repo)}`,
    `--title ${shellQuote(args.title)}`,
    `--body ${shellQuote(args.body)}`,
  ];

  if (labels.length > 0) {
    parts.push(`--label ${shellQuote(labels.join(","))}`);
  }

  return parts.join(" ");
}
