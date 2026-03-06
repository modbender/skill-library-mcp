"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const links = [
  { href: "/leaderboard", label: "leaderboard" },
  { href: "/submit", label: "submit" },
  { href: "/docs", label: "api" },
];

export function Navbar() {
  const pathname = usePathname();

  return (
    <header className="border-b border-border bg-primary">
      <nav className="mx-auto flex h-10 max-w-5xl items-center gap-4 px-4">
        <Link href="/" className="flex items-center gap-1.5 font-bold text-sm text-primary-foreground">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/logo.svg" alt="" className="h-5 w-5" />
          OpenClaw
          <span className="bg-primary-foreground/20 text-primary-foreground text-[10px] font-medium px-1 py-0.5 leading-none uppercase tracking-wide">
            beta
          </span>
        </Link>

        <div className="flex items-center gap-3">
          {links.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              className={cn(
                "text-sm transition-colors",
                pathname === href
                  ? "text-primary-foreground font-medium"
                  : "text-primary-foreground/70 hover:text-primary-foreground"
              )}
            >
              {label}
            </Link>
          ))}
        </div>
      </nav>
    </header>
  );
}
