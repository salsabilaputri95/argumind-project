"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";

import type { ArgumentEdge, ArgumentNode, RubricScore } from "@argumind/shared-schemas";

import { AppHeader } from "@/components/AppHeader";
import { apiFetch, ArgumindApiError } from "@/lib/apiClient";
import { useWorkspaceStore } from "@/stores/workspaceStore";

interface AnnotatorRun {
  readonly run_id: string;
  readonly actor_user_id: string | null;
  readonly nodes: readonly ArgumentNode[];
  readonly edges: readonly ArgumentEdge[];
  readonly scores: readonly RubricScore[];
}

export default function AdjudicateAnnotationsPage(): React.JSX.Element {
  const params = useParams<{ docVerId: string }>();
  const router = useRouter();
  const pushToast = useWorkspaceStore((s) => s.pushErrorToast);
  const [agreement, setAgreement] = useState<{ krippendorff_alpha: number; qwk: number } | null>(null);

  const meQuery = useQuery({
    queryKey: ["auth-me"],
    queryFn: async () => {
      const me = await apiFetch<{ full_name: string; role: string }>("/api/v1/auth/me");
      if (me.role !== "reviewer" && me.role !== "org_admin") {
        router.push("/forbidden");
      }
      return me;
    },
  });

  const runsQuery = useQuery({
    queryKey: ["annotator-runs", params.docVerId],
    enabled: Boolean(meQuery.data),
    queryFn: () =>
      apiFetch<{ data: AnnotatorRun[] }>(
        `/api/v1/runs?doc_version_id=${params.docVerId}&run_source=human_annotator`
      ),
  });

  const annotatorRuns = runsQuery.data?.data ?? [];
  const runA = annotatorRuns[0];
  const runB = annotatorRuns[1];

  async function lockGoldStandard(): Promise<void> {
    if (!runA) return;
    try {
      const res = await apiFetch<{ agreement_metrics: { krippendorff_alpha: number; qwk: number } }>(
        `/api/v1/annotations/${params.docVerId}/adjudicate`,
        {
          method: "POST",
          body: JSON.stringify({
            nodes: runA.nodes,
            edges: runA.edges,
            gaps: [],
            scores: runA.scores,
          }),
        }
      );
      setAgreement(res.agreement_metrics);
    } catch (err) {
      if (err instanceof ArgumindApiError) {
        pushToast({ code: err.code, detail: err.message, traceId: err.traceId });
      }
    }
  }

  return (
    <div className="flex min-h-screen flex-col">
      <AppHeader userRole={meQuery.data?.role ?? null} fullName={meQuery.data?.full_name ?? null} />
      <div className="flex items-center justify-between border-b px-6 py-3 text-sm" style={{ backgroundColor: "var(--color-surface)", borderColor: "var(--color-border)" }}>
        <div>
          <Link href="/dashboard" className="underline">Tugas Anotasi</Link> &gt;{" "}
          <strong>Adjudikasi Gold Standard</strong>
        </div>
        <div className="flex items-center gap-4">
          {agreement && (
            <span className="font-mono text-xs font-bold" style={{ color: "var(--color-success)" }}>
              α_Krip: {agreement.krippendorff_alpha} | QWK: {agreement.qwk}
            </span>
          )}
          <button
            type="button"
            disabled={annotatorRuns.length < 2}
            onClick={() => void lockGoldStandard()}
            className="h-9 rounded-md px-4 text-xs font-semibold text-white disabled:opacity-50"
            style={{ backgroundColor: "var(--color-primary)" }}
          >
            Kunci Gold Standard
          </button>
        </div>
      </div>

      <main className="p-6">
        {annotatorRuns.length < 2 ? (
          <div className="rounded-xl border p-8 text-center text-sm" style={{ backgroundColor: "var(--color-warning-bg)", borderColor: "var(--color-warning)" }}>
            Menunggu Anotator Ke-2 Selesai (Baru tersedia {annotatorRuns.length} dari minimal 2 anotasi).
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            {[
              { label: "Anotator 1", run: runA },
              { label: "Anotator 2", run: runB },
            ].map(({ label, run }) => (
              <section key={label} className="rounded-xl border p-4" style={{ backgroundColor: "var(--color-surface)", borderColor: "var(--color-border)" }}>
                <h2 className="font-semibold">{label} ({run?.nodes.length ?? 0} Node)</h2>
                <div className="mt-3 flex flex-col gap-2 text-xs">
                  {run?.nodes.map((n) => (
                    <div key={n.node_key} className="rounded border p-2" style={{ borderColor: "var(--color-border)" }}>
                      <strong className="font-mono">{n.node_key} ({n.node_type})</strong>: {n.text_content}
                    </div>
                  ))}
                </div>
              </section>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
