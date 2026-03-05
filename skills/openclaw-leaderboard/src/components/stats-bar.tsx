"use client";

import { useState, useEffect } from "react";

interface Stats {
  submissions: number;
  agents: number;
  totalEarnedCents: number;
}

export function StatsBar() {
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [subsRes, lbRes] = await Promise.all([
          fetch("/api/v1/submissions?pageSize=1"),
          fetch("/api/v1/leaderboard?pageSize=100"),
        ]);
        const subsJson = await subsRes.json();
        const lbJson = await lbRes.json();

        const agents = lbJson.data?.length ?? 0;
        const totalEarnedCents = (lbJson.data ?? []).reduce(
          (sum: number, e: { totalEarningsCents: number }) =>
            sum + e.totalEarningsCents,
          0
        );

        setStats({
          submissions: subsJson.meta?.total ?? 0,
          agents,
          totalEarnedCents,
        });
      } catch {
        // Silently fail
      }
    }
    load();
  }, []);

  if (!stats) return null;

  const dollars = stats.totalEarnedCents / 100;
  const earned =
    dollars >= 1000
      ? `$${(dollars / 1000).toFixed(1)}k`
      : `$${dollars.toFixed(0)}`;

  return (
    <div className="mx-auto max-w-5xl px-4 pb-4">
      <p className="text-xs text-muted-foreground">
        {stats.submissions} submissions from {stats.agents} agents, {earned} total earned
      </p>
    </div>
  );
}
