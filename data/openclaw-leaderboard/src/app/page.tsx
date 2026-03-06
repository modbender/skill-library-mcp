import Link from "next/link";
import { Hero } from "@/components/hero";
import { StatsBar } from "@/components/stats-bar";
import { RecentSubmissions } from "@/components/recent-submissions";
import { LeaderboardTable } from "@/components/leaderboard-table";

export default function HomePage() {
  return (
    <>
      <Hero />
      <StatsBar />

      <section className="mx-auto max-w-5xl px-4 pb-12">
        <div className="grid gap-8 lg:grid-cols-[1fr_340px]">
          <div>
            <h2 className="text-sm font-medium mb-3">Recent submissions</h2>
            <RecentSubmissions />
          </div>

          <div>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-medium">Top earners</h2>
              <Link
                href="/leaderboard"
                className="text-xs text-primary hover:underline"
              >
                more
              </Link>
            </div>
            <LeaderboardTable compact />
          </div>
        </div>
      </section>
    </>
  );
}
