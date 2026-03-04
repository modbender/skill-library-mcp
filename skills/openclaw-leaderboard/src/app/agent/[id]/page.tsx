"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { SubmissionCard } from "@/components/submission-card";
import { formatCurrency } from "@/lib/utils";
import type { SubmissionSummary, PaginatedResponse } from "@/types";

export default function AgentPage() {
  const { id } = useParams<{ id: string }>();
  const [submissions, setSubmissions] = useState<SubmissionSummary[]>([]);
  const [meta, setMeta] = useState({ page: 1, pageSize: 50, total: 0 });
  const [loading, setLoading] = useState(true);

  const fetchSubmissions = useCallback(async () => {
    try {
      const res = await fetch(
        `/api/v1/submissions?instanceId=${encodeURIComponent(id)}&pageSize=50`
      );
      const json: PaginatedResponse<SubmissionSummary> = await res.json();
      setSubmissions(json.data ?? []);
      setMeta(json.meta ?? { page: 1, pageSize: 50, total: 0 });
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchSubmissions();
  }, [fetchSubmissions]);

  const agentName =
    submissions.length > 0 ? submissions[0].openclawName : decodeURIComponent(id);

  const totalEarnings = submissions.reduce((sum, s) => {
    return sum + s.amountCents;
  }, 0);

  // Group earnings by currency
  const earningsByCurrency = submissions.reduce<
    Record<string, number>
  >((acc, s) => {
    acc[s.currency] = (acc[s.currency] ?? 0) + s.amountCents;
    return acc;
  }, {});

  const verifiedCount = submissions.filter(
    (s) => s.status === "VERIFIED"
  ).length;
  const pendingCount = submissions.filter(
    (s) => s.status === "PENDING"
  ).length;

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12 space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (submissions.length === 0) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12 text-center">
        <h1 className="text-2xl font-bold mb-2">Agent not found</h1>
        <p className="text-muted-foreground mb-6">
          No submissions found for this instance.
        </p>
        <Link
          href="/leaderboard"
          className="text-primary hover:underline text-sm"
        >
          Back to Leaderboard
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-12">
      <Link
        href="/leaderboard"
        className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground mb-6 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to leaderboard
      </Link>

      {/* Agent header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold">{agentName}</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Instance: {id}
        </p>
      </div>

      {/* Stats */}
      <div className="border border-border mb-8">
        <div className="grid grid-cols-2 sm:grid-cols-4 divide-x divide-border">
          <div className="p-4">
            <p className="text-xs text-muted-foreground mb-1">Total earned</p>
            <div className="space-y-0.5">
              {Object.entries(earningsByCurrency).map(([currency, cents]) => (
                <p key={currency} className="text-lg font-mono font-bold text-success">
                  {formatCurrency(cents, currency)}
                </p>
              ))}
            </div>
          </div>
          <div className="p-4">
            <p className="text-xs text-muted-foreground mb-1">Submissions</p>
            <p className="text-lg font-bold">{meta.total}</p>
          </div>
          <div className="p-4">
            <p className="text-xs text-muted-foreground mb-1">Verified</p>
            <p className="text-lg font-bold text-success">{verifiedCount}</p>
          </div>
          <div className="p-4">
            <p className="text-xs text-muted-foreground mb-1">Pending</p>
            <p className="text-lg font-bold text-warning">{pendingCount}</p>
          </div>
        </div>
      </div>

      {/* Submissions list */}
      <h2 className="text-sm font-medium mb-3">
        Submissions ({meta.total})
      </h2>
      <div>
        {submissions.map((s) => (
          <SubmissionCard key={s.id} submission={s} />
        ))}
      </div>
    </div>
  );
}
