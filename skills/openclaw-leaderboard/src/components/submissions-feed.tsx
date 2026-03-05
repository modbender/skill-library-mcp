"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { Inbox, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { SubmissionCard } from "@/components/submission-card";
import type { SubmissionSummary } from "@/types";

export function SubmissionsFeed() {
  const [submissions, setSubmissions] = useState<SubmissionSummary[]>([]);
  const [meta, setMeta] = useState({ page: 1, pageSize: 20, total: 0 });
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async (page: number) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/v1/submissions?page=${page}&pageSize=20`);
      const json = await res.json();
      setSubmissions(json.data ?? []);
      setMeta(json.meta ?? { page, pageSize: 20, total: 0 });
    } catch {
      // Silently fail
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData(1);
  }, [fetchData]);

  const totalPages = Math.ceil(meta.total / meta.pageSize);

  if (loading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 8 }).map((_, i) => (
          <Skeleton key={i} className="h-24 w-full" />
        ))}
      </div>
    );
  }

  if (submissions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <Inbox className="h-12 w-12 text-muted-foreground mb-4" />
        <p className="text-lg font-medium">No submissions yet</p>
        <p className="text-sm text-muted-foreground mt-1">
          <Link href="/submit" className="text-primary hover:underline">
            Submit your earnings
          </Link>{" "}
          to get started!
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="space-y-3">
        {submissions.map((s) => (
          <SubmissionCard key={s.id} submission={s} />
        ))}
      </div>

      {totalPages > 1 && (
        <div className="mt-6 flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Showing {(meta.page - 1) * meta.pageSize + 1}–
            {Math.min(meta.page * meta.pageSize, meta.total)} of {meta.total}
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={meta.page <= 1}
              onClick={() => fetchData(meta.page - 1)}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={meta.page >= totalPages}
              onClick={() => fetchData(meta.page + 1)}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
