"use client";

import { useState } from "react";
import { Bot, ChevronDown, ChevronRight } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { SubmissionDetail } from "@/types";

interface ConfigViewerProps {
  submission: SubmissionDetail;
}

export function ConfigViewer({ submission }: ConfigViewerProps) {
  const [promptExpanded, setPromptExpanded] = useState(false);

  const hasConfig =
    submission.systemPrompt ||
    submission.modelId ||
    submission.modelProvider ||
    (submission.tools && submission.tools.length > 0) ||
    (submission.modelConfig && Object.keys(submission.modelConfig).length > 0) ||
    submission.configNotes;

  if (!hasConfig) return null;

  const isLongPrompt =
    submission.systemPrompt && submission.systemPrompt.length > 200;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <Bot className="h-5 w-5" />
          Agent Configuration
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Model info */}
        {(submission.modelProvider || submission.modelId) && (
          <div>
            <p className="text-sm font-medium mb-2">Model</p>
            <div className="flex flex-wrap items-center gap-2">
              {submission.modelProvider && (
                <Badge variant="outline">{submission.modelProvider}</Badge>
              )}
              {submission.modelId && (
                <code className="bg-secondary px-2 py-1 text-xs font-mono">
                  {submission.modelId}
                </code>
              )}
            </div>
          </div>
        )}

        {/* System prompt */}
        {submission.systemPrompt && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-medium">System Prompt</p>
              {isLongPrompt && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setPromptExpanded(!promptExpanded)}
                  className="gap-1 h-auto py-1 px-2 text-xs"
                >
                  {promptExpanded ? (
                    <ChevronDown className="h-3 w-3" />
                  ) : (
                    <ChevronRight className="h-3 w-3" />
                  )}
                  {promptExpanded ? "Collapse" : "Expand"}
                </Button>
              )}
            </div>
            <pre
              className={`bg-secondary p-3 text-xs font-mono whitespace-pre-wrap break-words overflow-hidden ${
                isLongPrompt && !promptExpanded ? "max-h-32" : ""
              }`}
            >
              {submission.systemPrompt}
            </pre>
            {isLongPrompt && !promptExpanded && (
              <div className="relative -mt-6 h-6 bg-gradient-to-t from-secondary to-transparent border-b" />
            )}
          </div>
        )}

        {/* Tools */}
        {submission.tools && submission.tools.length > 0 && (
          <div>
            <p className="text-sm font-medium mb-2">Tools / APIs</p>
            <div className="flex flex-wrap gap-1.5">
              {submission.tools.map((tool) => (
                <Badge key={tool} variant="secondary">
                  {tool}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Model config */}
        {submission.modelConfig &&
          Object.keys(submission.modelConfig).length > 0 && (
            <div>
              <p className="text-sm font-medium mb-2">Model Config</p>
              <pre className="bg-secondary p-3 text-xs font-mono whitespace-pre-wrap break-words">
                {JSON.stringify(submission.modelConfig, null, 2)}
              </pre>
            </div>
          )}

        {/* Notes */}
        {submission.configNotes && (
          <div>
            <p className="text-sm font-medium mb-1">Notes</p>
            <p className="text-sm text-muted-foreground whitespace-pre-wrap">
              {submission.configNotes}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
