/**
 * Dashboard layout — wraps all /dashboard/[username]/* pages
 * with persistent sidebar and guaranteed deep dark background.
 */
import Sidebar from "@/components/Sidebar";

interface LayoutProps {
  children: React.ReactNode;
  params: Promise<{ username: string }>;
}

export default async function DashboardLayout({ children, params }: LayoutProps) {
  const { username } = await params;

  return (
    <div style={{ display: "flex", minHeight: "100vh", backgroundColor: "#0a0d14", color: "#ffffff" }}>
      <Sidebar username={username} />
      <main
        style={{
          flex: 1,
          padding: "32px 40px",
          overflowY: "auto",
          minWidth: 0,
          backgroundColor: "#0a0d14",
          color: "#ffffff",
        }}
      >
        <div style={{ minHeight: "calc(100vh - 160px)" }}>
          {children}
        </div>

        {/* Global Dashboard Disclaimer Footer */}
        <footer
          style={{
            marginTop: 56,
            paddingTop: 24,
            paddingBottom: 28,
            borderTop: "1px solid rgba(255, 255, 255, 0.06)",
            textAlign: "center",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 6,
          }}
        >
          <div style={{ fontSize: 12, fontWeight: 600, color: "#94a3b8" }}>
            LeetLens • Open-Source DSA Analytics & Spaced Practice
          </div>
          <div style={{ maxWidth: 680, fontSize: 11, color: "#64748b", lineHeight: 1.5 }}>
            Independent open-source project. Not affiliated with, endorsed by, or sponsored by LeetCode LLC. All problem names & trademarks belong to LeetCode LLC.
          </div>
        </footer>
      </main>
    </div>
  );
}
