import Link from "next/link";
import { formatCurrency, formatRelativeTime } from "@/lib/utils";
import type { SubmissionSummary } from "@/types";

interface SubmissionCardProps {
  submission: SubmissionSummary;
}

export function SubmissionCard({ submission }: SubmissionCardProps) {
  return (
    <Link
      href={`/submission/${submission.id}`}
      className="block border-b border-border py-3 hover:bg-secondary/50 -mx-2 px-2 transition-colors"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-sm font-medium">
            {submission.openclawName}
            <span className="ml-2 text-xs text-muted-foreground font-normal">
              {submission.status === "VERIFIED" && "verified"}
              {submission.status === "FLAGGED" && "flagged"}
            </span>
          </p>
          <p className="text-xs text-muted-foreground line-clamp-1 mt-0.5">
            {submission.description}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            {submission.proofType.replace("_", " ").toLowerCase()}
            {" \u00b7 "}
            {formatRelativeTime(new Date(submission.createdAt))}
            {" \u00b7 "}
            {submission.legitVotes} legit
            {submission.suspiciousVotes > 0 &&
              `, ${submission.suspiciousVotes} suspicious`}
          </p>
        </div>
        <span className="text-sm font-mono font-semibold text-success shrink-0">
          {formatCurrency(submission.amountCents, submission.currency)}
        </span>
      </div>
    </Link>
  );
}
