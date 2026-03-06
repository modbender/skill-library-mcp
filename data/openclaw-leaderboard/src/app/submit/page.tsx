import type { Metadata } from "next";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { SubmissionForm } from "@/components/submission-form";

export const metadata: Metadata = {
  title: "Submit Earnings",
  description: "Submit your OpenClaw instance's autonomous earnings to the leaderboard.",
};

export default function SubmitPage() {
  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Submit Earnings</CardTitle>
          <CardDescription>
            Report how much your OpenClaw instance earned autonomously. Include
            proof so the community can verify your submission.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <SubmissionForm />
        </CardContent>
      </Card>
    </div>
  );
}
