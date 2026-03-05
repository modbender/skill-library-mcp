import { StrictMode, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { useApp, useHostStyles } from "@modelcontextprotocol/ext-apps/react";
import { Card } from "./components/Card";
import "./index.css";

interface ToolData {
  param: string;
  generatedAt: string;
  score: number;
  notes: string;
}

function LoadingSkeleton() {
  return (
    <div className="min-h-screen p-4">
      <Card>
        <div className="h-5 w-40 animate-pulse rounded bg-gray-200" />
        <div className="mt-4 space-y-2">
          <div className="h-4 w-full animate-pulse rounded bg-gray-200" />
          <div className="h-4 w-3/4 animate-pulse rounded bg-gray-200" />
        </div>
      </Card>
    </div>
  );
}

function ErrorDisplay({ message }: { message: string }) {
  return (
    <div className="min-h-screen p-4">
      <Card className="border-red-200">
        <div className="text-sm font-semibold text-red-600">Error</div>
        <div className="mt-2 text-sm text-secondary">{message}</div>
      </Card>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="min-h-screen p-4">
      <Card>
        <div className="text-sm font-semibold">No data yet</div>
        <div className="mt-2 text-sm text-secondary">
          Invoke the tool to see results here.
        </div>
      </Card>
    </div>
  );
}

function DataVisualization({ data }: { data: ToolData }) {
  const formattedDate = useMemo(() => {
    try {
      return new Date(data.generatedAt).toLocaleString();
    } catch {
      return data.generatedAt;
    }
  }, [data.generatedAt]);

  return (
    <div className="min-h-screen p-4">
      <Card>
        <div className="flex items-center justify-between">
          <div>
            <div className="text-lg font-semibold">Tool Result</div>
            <div className="text-xs text-tertiary">{formattedDate}</div>
          </div>
          <div className="text-sm font-semibold">Score: {data.score}</div>
        </div>
        <div className="mt-4 card-inner">
          <div className="text-sm text-secondary">Parameter</div>
          <div className="text-base font-medium">{data.param}</div>
        </div>
        <div className="mt-4 text-sm text-secondary">{data.notes}</div>
      </Card>
    </div>
  );
}

function ToolUI() {
  const [data, setData] = useState<ToolData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const { app } = useApp({
    appInfo: { name: "Tool Name", version: "1.0.0" },
    onAppCreated: (app) => {
      app.ontoolresult = (result) => {
        setLoading(false);
        const text = result.content?.find((c) => c.type === "text")?.text;
        if (!text) {
          setError("No data returned by tool.");
          return;
        }
        try {
          const parsed = JSON.parse(text) as ToolData | { error?: string; message?: string };
          if (parsed && typeof parsed === "object" && "error" in parsed) {
            setError(parsed.message ?? "Tool returned an error.");
            return;
          }
          setData(parsed as ToolData);
        } catch {
          setError("Failed to parse data");
        }
      };
    },
  });

  useHostStyles(app);

  useEffect(() => {
    if (!app) return;
    app.onhostcontextchanged = (ctx) => {
      if (ctx.safeAreaInsets) {
        const { top, right, bottom, left } = ctx.safeAreaInsets;
        document.body.style.padding = `${top}px ${right}px ${bottom}px ${left}px`;
      }
    };
  }, [app]);

  if (loading) return <LoadingSkeleton />;
  if (error) return <ErrorDisplay message={error} />;
  if (!data) return <EmptyState />;

  return <DataVisualization data={data} />;
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ToolUI />
  </StrictMode>
);
