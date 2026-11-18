"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState, type ReactNode } from "react";

import { useWorkspaceStore } from "@/stores/workspaceStore";

function ErrorToastContainer(): React.JSX.Element | null {
  const toasts = useWorkspaceStore((s) => s.toasts);
  const dismiss = useWorkspaceStore((s) => s.dismissToast);
  if (toasts.length === 0) return null;

  return (
    <div
      aria-live="assertive"
      className="fixed bottom-6 right-6 z-50 flex w-[360px] flex-col gap-3"
    >
      {toasts.map((t) => (
        <div
          key={t.id}
          role="alert"
          className="rounded-lg border-2 p-3 shadow-lg"
          style={{
            backgroundColor: "var(--color-error-bg)",
            borderColor: "var(--color-error)",
            color: "var(--color-text-primary)",
          }}
        >
          <div className="flex items-start justify-between gap-2">
            <strong className="text-xs font-mono">{t.code}</strong>
            <button
              type="button"
              onClick={() => dismiss(t.id)}
              className="rounded px-2 py-0.5 text-xs font-semibold"
              aria-label="Tutup pesan error"
            >
              Tutup
            </button>
          </div>
          <p className="mt-1 text-sm">{t.detail}</p>
          <p className="mt-1 font-mono text-xs" style={{ color: "var(--color-text-secondary)" }}>
            trace_id: {t.traceId}
          </p>
        </div>
      ))}
    </div>
  );
}

export function Providers({ children }: { readonly children: ReactNode }): React.JSX.Element {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: { staleTime: 60_000, retry: 1 },
        },
      })
  );
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ErrorToastContainer />
    </QueryClientProvider>
  );
}
