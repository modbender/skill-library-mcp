"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Skeleton } from "@/components/ui/skeleton";
import { SubmissionCard } from "@/components/submission-card";
import type { SubmissionSummary } from "@/types";

export function RecentSubmissions() {
  const [submissions, setSubmissions] = useState<SubmissionSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch("/api/v1/submissions?pageSize=10");
        const json = await res.json();
        setSubmissions(json.data ?? []);
      } catch {
        // Silently fail
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-24 w-full" />
        ))}
      </div>
    );
  }

  if (submissions.length === 0) {
    return (
      <p className="py-8 text-sm text-muted-foreground">
        No submissions yet.{" "}
        <Link href="/submit" className="text-primary hover:underline">
          Be the first!
        </Link>
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {submissions.map((s) => (
        <SubmissionCard key={s.id} submission={s} />
      ))}
      <div className="pt-3 text-center">
        <Link
          href="/submissions"
          className="text-xs text-primary hover:underline"
        >
          View all submissions
        </Link>
      </div>
    </div>
  );
}
