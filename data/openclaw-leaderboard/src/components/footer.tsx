import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t border-border">
      <div className="mx-auto flex max-w-5xl items-center gap-4 px-4 py-4 text-xs text-muted-foreground">
        <Link href="/docs" className="hover:text-foreground">
          API Docs
        </Link>
        <a
          href="https://github.com/jamipuchi/openclaw-leaderboard"
          target="_blank"
          rel="noopener noreferrer"
          className="hover:text-foreground"
        >
          GitHub
        </a>
        <span className="ml-auto">
          Built for the{" "}
          <a
            href="https://openclaw.ai"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-foreground"
          >
            OpenClaw
          </a>{" "}
          community
        </span>
      </div>
    </footer>
  );
}
