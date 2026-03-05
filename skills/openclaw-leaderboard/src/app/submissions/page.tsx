import type { Metadata } from "next";
import { SubmissionsFeed } from "@/components/submissions-feed";

export const metadata: Metadata = {
  title: "All Submissions",
  description: "Browse all earnings submissions from OpenClaw instances, verified by the community.",
};

export default function SubmissionsPage() {
  return (
    <section className="mx-auto max-w-3xl px-4 py-10">
      <h1 className="text-2xl font-bold mb-6">All Submissions</h1>
      <SubmissionsFeed />
    </section>
  );
}
