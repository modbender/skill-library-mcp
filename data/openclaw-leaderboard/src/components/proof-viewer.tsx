"use client";

import { ExternalLink, Hash, FileText, ImageIcon } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { SubmissionDetail } from "@/types";

function isSafeUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}

interface ProofViewerProps {
  submission: SubmissionDetail;
}

export function ProofViewer({ submission }: ProofViewerProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          Proof of Earnings
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {submission.proofType === "SCREENSHOT" &&
          submission.proofUrl &&
          isSafeUrl(submission.proofUrl) && (
            <div>
              <div className="flex items-center gap-2 mb-2 text-sm text-muted-foreground">
                <ImageIcon className="h-4 w-4" />
                Screenshot
              </div>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={submission.proofUrl}
                alt="Proof screenshot"
                className="border border-border max-w-full"
              />
            </div>
          )}

        {submission.proofType === "LINK" &&
          submission.proofUrl &&
          isSafeUrl(submission.proofUrl) && (
            <div>
              <div className="flex items-center gap-2 mb-2 text-sm text-muted-foreground">
                <ExternalLink className="h-4 w-4" />
                External Link
              </div>
              <a
                href={submission.proofUrl}
                target="_blank"
                rel="noopener noreferrer"
              >
                <Button variant="outline" className="gap-2">
                  <ExternalLink className="h-4 w-4" />
                  View Proof
                </Button>
              </a>
            </div>
          )}

        {submission.proofType === "TRANSACTION_HASH" &&
          submission.transactionHash && (
            <div>
              <div className="flex items-center gap-2 mb-2 text-sm text-muted-foreground">
                <Hash className="h-4 w-4" />
                Transaction Hash
              </div>
              <code className="block bg-secondary p-3 text-sm font-mono break-all">
                {submission.transactionHash}
              </code>
            </div>
          )}

        {submission.proofType === "DESCRIPTION_ONLY" && (
          <div>
            <div className="flex items-center gap-2 mb-2 text-sm text-muted-foreground">
              <FileText className="h-4 w-4" />
              Description Only
            </div>
          </div>
        )}

        {submission.proofDescription && (
          <div>
            <p className="text-sm font-medium mb-1">Additional Details</p>
            <p className="text-sm text-muted-foreground whitespace-pre-wrap">
              {submission.proofDescription}
            </p>
          </div>
        )}

        <div>
          <p className="text-sm font-medium mb-1">How to Verify</p>
          <p className="text-sm text-muted-foreground whitespace-pre-wrap">
            {submission.verificationMethod}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
