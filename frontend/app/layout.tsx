import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LeetLens — Understand Your DSA Patterns",
  description:
    "Analyze your LeetCode profile by DSA patterns, topics, and difficulty. Understand what you've actually practiced — not just how many problems you've solved.",
  keywords: ["LeetCode", "DSA", "patterns", "analyzer", "algorithms", "data structures"],
  openGraph: {
    title: "LeetLens — DSA Pattern Analyzer",
    description: "Transform your LeetCode profile into structured DSA pattern analytics.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              try {
                var t = localStorage.getItem("leetlens_theme") || "dark";
                document.documentElement.setAttribute("data-theme", t);
                document.documentElement.style.colorScheme = t;
              } catch (e) {}
            `,
          }}
        />
      </head>
      <body className="bg-mesh" suppressHydrationWarning style={{ minHeight: "100vh" }}>
        {children}
      </body>
    </html>
  );
}
