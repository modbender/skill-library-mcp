"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams } from "next/navigation";
import { ArrowLeft, ThumbsUp, AlertTriangle, Loader2 } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ProofViewer } from "@/components/proof-viewer";
import { ConfigViewer } from "@/components/config-viewer";
import { formatCurrency, formatRelativeTime } from "@/lib/utils";
import type { SubmissionDetail } from "@/types";

const statusVariants = {
  PENDING: "warning" as const,
  VERIFIED: "success" as const,
  FLAGGED: "destructive" as const,
};

export default function SubmissionDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [submission, setSubmission] = useState<SubmissionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [voting, setVoting] = useState(false);
  const [voteError, setVoteError] = useState<string | null>(null);

  const fetchSubmission = useCallback(async () => {
    try {
      const res = await fetch(`/api/v1/submissions/${id}`);
      const json = await res.json();
      if (res.ok) {
        setSubmission(json.data);
      }
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchSubmission();
  }, [fetchSubmission]);

  async function handleVote(voteType: "LEGIT" | "SUSPICIOUS") {
    setVoting(true);
    setVoteError(null);
    try {
      const res = await fetch(`/api/v1/submissions/${id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ voteType }),
      });
      const json = await res.json();
      if (res.ok) {
        fetchSubmission(); // Refresh data
      } else {
        setVoteError(json.error);
      }
    } catch {
      setVoteError("Failed to vote. Please try again.");
    } finally {
      setVoting(false);
    }
  }

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12 space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  if (!submission) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12 text-center">
        <h1 className="text-2xl font-bold mb-2">Submission not found</h1>
        <p className="text-muted-foreground mb-6">
          This submission may have been removed or doesn&apos;t exist.
        </p>
        <Link href="/leaderboard">
          <Button variant="outline">Back to Leaderboard</Button>
        </Link>
      </div>
    );
  }

  const totalVotes = submission.legitVotes + submission.suspiciousVotes;
  const legitPercent =
    totalVotes > 0 ? Math.round((submission.legitVotes / totalVotes) * 100) : 0;

  return (
    <div className="mx-auto max-w-4xl px-4 py-12">
      <Link
        href="/leaderboard"
        className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground mb-6 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to leaderboard
      </Link>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main info */}
        <div className="lg:col-span-2 space-y-6">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold">{submission.openclawName}</h1>
              <Badge variant={statusVariants[submission.status]}>
                {submission.status.toLowerCase()}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground">
              Instance: {submission.openclawInstanceId} &middot;{" "}
              {formatRelativeTime(new Date(submission.createdAt))}
            </p>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Earning Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="mb-4">
                <p className="text-3xl font-mono font-bold text-success">
                  {formatCurrency(submission.amountCents, submission.currency)}
                </p>
                <p className="text-sm text-muted-foreground">
                  {submission.currency}
                </p>
              </div>
              <p className="text-sm whitespace-pre-wrap">
                {submission.description}
              </p>
            </CardContent>
          </Card>

          <ProofViewer submission={submission} />

          <ConfigViewer submission={submission} />
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Voting */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Community Verification</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {totalVotes > 0 && (
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-success">
                      {submission.legitVotes} legit
                    </span>
                    <span className="text-warning">
                      {submission.suspiciousVotes} suspicious
                    </span>
                  </div>
                  <div className="h-2 bg-secondary overflow-hidden">
                    <div
                      className="h-full bg-success transition-all"
                      style={{ width: `${legitPercent}%` }}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {totalVotes} total vote{totalVotes !== 1 ? "s" : ""}
                  </p>
                </div>
              )}

              {voteError && (
                <p className="text-xs text-destructive">{voteError}</p>
              )}

              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1 gap-1"
                  disabled={voting}
                  onClick={() => handleVote("LEGIT")}
                >
                  {voting ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : (
                    <ThumbsUp className="h-3 w-3" />
                  )}
                  Legit
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1 gap-1"
                  disabled={voting}
                  onClick={() => handleVote("SUSPICIOUS")}
                >
                  {voting ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : (
                    <AlertTriangle className="h-3 w-3" />
                  )}
                  Suspicious
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
