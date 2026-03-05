import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "OpenClawdy - Persistent Memory for Agents",
  description: "Persistent memory for Agents. Store context, recall knowledge, build smarter agents.",
  other: {
    "virtual-protocol-site-verification": "bc39b1b196593c988e381dd18795652b",
  },
  openGraph: {
    title: "OpenClawdy",
    description: "Persistent memory for Agents",
    url: "https://openclawdy.xyz",
    siteName: "OpenClawdy",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "OpenClawdy",
    description: "Persistent memory for Agents",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
