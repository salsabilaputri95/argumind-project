"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import dynamic from "next/dynamic";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";

import type {
  ArgumentEdge,
  ArgumentNode,
  ReasoningGap,
  RubricScore,
} from "@argumind/shared-schemas";

import { AnnotatedTextPane } from "@/components/AnnotatedTextPane";
import { AppHeader } from "@/components/AppHeader";
import { RubricPanel } from "@/components/RubricPanel";
import { useArgumentStream } from "@/hooks/useArgumentStream";
import { apiFetch, ArgumindApiError } from "@/lib/apiClient";

const DynamicGraphCanvas = dynamic(
  () => import("@/components/ArgumentGraphCanvas").then((m) => m.ArgumentGraphCanvas),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-full items-center justify-center rounded-xl border p-6" style={{ borderColor: "var(--color-border)" }}>
        <div className="h-32 w-64 animate-pulse rounded-lg" style={{ backgroundColor: "var(--color-surface-elevated)" }} />
      </div>
    ),
  }
);

interface RunDetail {
  readonly run_id: string;
  readonly doc_id: string;
  readonly doc_title: string;
  readonly clean_text: string;
  readonly overall_score: number;
  readonly nodes: readonly ArgumentNode[];
  readonly edges: readonly ArgumentEdge[];
  readonly gaps: readonly ReasoningGap[];
  readonly scores: readonly RubricScore[];
}

export default function DocumentWorkspacePage(): React.JSX.Element {
  const params = useParams<{ docId: string; ver: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [mobileTab, setMobileTab] = useState<"text" | "graph" | "score">("graph");
  const [activeJobId, setActiveJobId] = useState<string | null>(null);

  const meQuery = useQuery({
    queryKey: ["auth-me"],
    queryFn: () => apiFetch<{ full_name: string; role: string }>("/api/v1/auth/me"),
  });

  const docMetaQuery = useQuery({
    queryKey: ["documents-find", params.docId],
    enabled: Boolean(meQuery.data),
    queryFn: async () => {
      const list = await apiFetch<{ data: { id: string; latest_run_id: string | null }[] }>(
        "/api/v1/documents?limit=100"
      );
      return list.data.find((d) => d.id === params.docId) ?? null;
    },
  });

  const runId = activeJobId ?? docMetaQuery.data?.latest_run_id ?? null;

  const runQuery = useQuery({
    queryKey: ["run-detail", runId],
    enabled: Boolean(runId),
    queryFn: async () => {
      try {
        return await apiFetch<RunDetail>(`/api/v1/runs/${runId}`);
      } catch (err) {
        if (err instanceof ArgumindApiError && err.status === 403) {
          router.push("/forbidden");
        }
        throw err;
      }
    },
  });

  const streamed = useArgumentStream(activeJobId, runQuery.data);

  async function triggerAnalyze(): Promise<void> {
    const res = await apiFetch<{ job_id: string }>(
      `/api/v1/documents/${params.docId}/versions/${params.ver}/analyze`,
      { method: "POST", body: JSON.stringify({ generate_counterarguments: true }) }
    );
    setActiveJobId(res.job_id);
  }

  const implicitNodes = streamed.nodes.filter(
    (n) => n.node_type === "ImplicitPremise" || n.node_type === "Counterargument"
  );

  return (
    <div className="flex min-h-screen flex-col">
      <AppHeader
        userRole={meQuery.data?.role ?? null}
        fullName={meQuery.data?.full_name ?? null}
      />
      <div className="flex flex-wrap items-center justify-between gap-3 border-b px-4 py-2 text-xs md:px-6" style={{ backgroundColor: "var(--color-surface)", borderColor: "var(--color-border)" }}>
        <nav aria-label="Breadcrumb" className="flex items-center gap-2">
          <Link href="/dashboard" className="underline">Dashboard</Link>
          <span>&gt;</span>
          <span className="max-w-[240px] truncate font-semibold">{runQuery.data?.doc_title ?? params.docId}</span>
          <span>&gt;</span>
          <span>Versi v{params.ver} (Ruang Kerja)</span>
        </nav>
        <div className="flex items-center gap-2">
          <span className="rounded-full px-2.5 py-0.5 font-mono" style={{ backgroundColor: "var(--color-info-bg)", color: "var(--color-info)" }}>
            Stage: {streamed.stage}
          </span>
          <button
            type="button"
            onClick={() => void triggerAnalyze()}
            className="h-8 rounded-md px-3 font-semibold text-white"
            style={{ backgroundColor: "var(--color-primary)" }}
          >
            Analisis Ulang
          </button>
        </div>
      </div>

      {/* Mobile Tabs (< 768px) */}
      <div className="flex border-b md:hidden" style={{ borderColor: "var(--color-border)", backgroundColor: "var(--color-surface)" }}>
        {(["text", "graph", "score"] as const).map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setMobileTab(tab)}
            className="h-11 flex-1 text-xs font-semibold uppercase"
            style={{
              borderBottom: mobileTab === tab ? "2px solid var(--color-primary)" : "none",
            }}
          >
            {tab === "text" ? "Teks" : tab === "graph" ? "Struktur" : "Skor"}
          </button>
        ))}
      </div>

      {/* 3-Column Split Pane Desktop (>= 1024px) */}
      <main className="grid flex-1 grid-cols-1 gap-4 p-4 md:grid-cols-12 md:p-5" style={{ height: "calc(100vh - 104px)" }}>
        <div className={`${mobileTab === "text" ? "block" : "hidden"} h-full min-h-[420px] md:col-span-4 md:block lg:col-span-4`}>
          <AnnotatedTextPane cleanText={runQuery.data?.clean_text ?? ""} nodes={streamed.nodes} />
        </div>
        <div className={`${mobileTab === "graph" ? "block" : "hidden"} h-full min-h-[420px] md:col-span-8 md:block lg:col-span-5`}>
          <DynamicGraphCanvas nodes={streamed.nodes} edges={streamed.edges} gaps={streamed.gaps} />
        </div>
        <div className={`${mobileTab === "score" ? "block" : "hidden"} h-full min-h-[420px] md:col-span-12 md:block lg:col-span-3`}>
          {runId && (
            <RubricPanel
              runId={runId}
              userRole={meQuery.data?.role ?? "author"}
              overallScore={runQuery.data?.overall_score ?? 0}
              scores={streamed.scores}
              gaps={streamed.gaps}
              implicitNodes={implicitNodes}
              onRefresh={() => void queryClient.invalidateQueries({ queryKey: ["run-detail", runId] })}
            />
          )}
        </div>
      </main>
    </div>
  );
}
