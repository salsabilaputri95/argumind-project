"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { apiFetch } from "@/lib/apiClient";
import { useWorkspaceStore } from "@/stores/workspaceStore";

export interface AppHeaderProps {
  readonly userRole: string | null;
  readonly fullName: string | null;
}

export function AppHeader({ userRole, fullName }: AppHeaderProps): React.JSX.Element {
  const pathname = usePathname();
  const router = useRouter();
  const isDark = useWorkspaceStore((s) => s.isDarkMode);
  const toggleTheme = useWorkspaceStore((s) => s.toggleTheme);

  async function handleLogout(): Promise<void> {
    await apiFetch("/api/v1/auth/logout", { method: "POST" }).catch(() => null);
    router.push("/login");
  }

  return (
    <header
      className="sticky top-0 z-20 flex h-14 items-center justify-between border-b px-4 md:px-6"
      style={{ backgroundColor: "var(--color-surface)", borderColor: "var(--color-border)" }}
    >
      <div className="flex items-center gap-6">
        <Link href="/dashboard" className="text-lg font-bold tracking-tight" style={{ color: "var(--color-primary)" }}>
          Argumind
        </Link>
        <nav aria-label="Navigasi utama" className="flex items-center gap-4 text-sm font-medium">
          <Link
            href="/dashboard"
            aria-current={pathname.startsWith("/dashboard") ? "page" : undefined}
            className="px-2 py-1"
            style={{
              borderBottom: pathname.startsWith("/dashboard") ? "2px solid var(--color-primary)" : "none",
            }}
          >
            Dokumen
          </Link>
          {(userRole === "annotator" || userRole === "reviewer") && (
            <Link
              href="/dashboard?tab=annotations"
              className="px-2 py-1"
              style={{ color: "var(--color-text-secondary)" }}
            >
              Tugas Anotasi
            </Link>
          )}
        </nav>
      </div>
      <div className="flex items-center gap-3 text-sm">
        <button
          type="button"
          onClick={toggleTheme}
          className="min-h-[32px] rounded-md border px-3 py-1 text-xs font-medium"
          style={{ borderColor: "var(--color-border)", backgroundColor: "var(--color-surface-elevated)" }}
        >
          {isDark ? "Mode Terang" : "Mode Gelap"}
        </button>
        {fullName && (
          <span className="hidden text-xs md:inline" style={{ color: "var(--color-text-secondary)" }}>
            {fullName} ({userRole})
          </span>
        )}
        <button
          type="button"
          onClick={handleLogout}
          className="min-h-[32px] rounded-md px-3 py-1 text-xs font-semibold text-white"
          style={{ backgroundColor: "var(--color-secondary)" }}
        >
          Keluar
        </button>
      </div>
    </header>
  );
}
