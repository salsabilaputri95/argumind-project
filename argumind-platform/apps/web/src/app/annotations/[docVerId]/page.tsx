"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";

import type { ArgumentEdge, ArgumentNode, RubricScore } from "@argumind/shared-schemas";

import { AppHeader } from "@/components/AppHeader";
import { apiFetch, ArgumindApiError } from "@/lib/apiClient";
import { useWorkspaceStore } from "@/stores/workspaceStore";

export default function BlindAnnotationPage(): React.JSX.Element {
  const params = useParams<{ docVerId: string }>();
  const router = useRouter();
  const pushToast = useWorkspaceStore((s) => s.pushErrorToast);
  const [nodes, setNodes] = useState<ArgumentNode[]>([]);
  const [edges, setEdges] = useState<ArgumentEdge[]>([]);
  const [cleanText, setCleanText] = useState<string>("");
  const [nodeType, setNodeType] = useState<"Claim" | "ExplicitPremise" | "Evidence">("Claim");
  const [clarityScore, setClarityScore] = useState<number>(3);

  const meQuery = useQuery({
    queryKey: ["auth-me"],
    queryFn: async () => {
      const me = await apiFetch<{ id: string; full_name: string; role: string }>("/api/v1/auth/me");
      if (me.role !== "annotator") {
        router.push("/forbidden");
      }
      return me;
    },
  });

  useQuery({
    queryKey: ["my-blind-runs", params.docVerId],
    enabled: Boolean(meQuery.data),
    queryFn: async () => {
      const res = await apiFetch<{ data: { clean_text: string; nodes: ArgumentNode[]; edges: ArgumentEdge[] }[] }>(
        `/api/v1/runs?doc_version_id=${params.docVerId}&run_source=human_annotator`
      );
      const mine = res.data[0];
      if (mine) {
        setCleanText(mine.clean_text);
        setNodes(mine.nodes);
        setEdges(mine.edges);
      }
      return res;
    },
  });

  function addNodeFromSelection(): void {
    const sel = window.getSelection()?.toString().trim();
    if (!sel || !cleanText.includes(sel)) return;
    const start = cleanText.indexOf(sel);
    const end = start + sel.length;
    const key = `N-${String(nodes.length + 1).padStart(2, "0")}`;
    setNodes((prev) => [
      ...prev,
      {
        node_key: key,
        node_type: nodeType,
        start_char: start,
        end_char: end,
        text_content: sel,
        evidence_strength: nodeType === "Evidence" ? 3 : null,
        target_node_key: null,
        user_feedback: "PENDING",
      },
    ]);
  }

  async function handleSubmitAnnotation(): Promise<void> {
    const firstKey = nodes[0]?.node_key ?? "N-01";
    const scores: RubricScore[] = [
      {
        dimension: "ClarityOfClaim",
        ai_score: clarityScore,
        grounded_refs: [firstKey],
        rationale: `Penilaian blind anotator berdasarkan komponen ${firstKey}.`,
      },
    ];
    try {
      await apiFetch(`/api/v1/annotations/${params.docVerId}`, {
        method: "PUT",
        body: JSON.stringify({ nodes, edges, gaps: [], scores }),
      });
    } catch (err) {
      if (err instanceof ArgumindApiError) {
        pushToast({ code: err.code, detail: err.message, traceId: err.traceId });
      }
    }
  }

  return (
    <div className="flex min-h-screen flex-col">
      <AppHeader userRole={meQuery.data?.role ?? null} fullName={meQuery.data?.full_name ?? null} />
      <div className="flex items-center justify-between border-b px-6 py-2 text-xs" style={{ backgroundColor: "var(--color-info-bg)", borderColor: "var(--color-border)" }}>
        <span>MODE ANOTASI DOUBLE-BLIND (Identitas penulis & hasil AI tersembunyi)</span>
        <Link href="/dashboard" className="underline">Kembali ke Dashboard</Link>
      </div>

      {/* Peringatan layar kecil sesuai PAGES_AND_FLOWS.md#4 */}
      <div className="p-6 text-center text-sm lg:hidden">
        Ruang kerja anotasi presisi membutuhkan lebar layar desktop minimal 1024px.
      </div>

      <main className="hidden flex-1 grid-cols-12 gap-4 p-6 lg:grid">
        <section className="col-span-5 rounded-xl border p-5" style={{ backgroundColor: "var(--color-surface)", borderColor: "var(--color-border)" }}>
          <div className="mb-3 flex items-center gap-2">
            <select
              value={nodeType}
              onChange={(e) => setNodeType(e.target.value as "Claim" | "ExplicitPremise" | "Evidence")}
              className="h-9 rounded border px-2 text-xs"
              style={{ borderColor: "var(--color-border)" }}
            >
              <option value="Claim">Claim</option>
              <option value="ExplicitPremise">ExplicitPremise</option>
              <option value="Evidence">Evidence</option>
            </select>
            <button
              type="button"
              onClick={addNodeFromSelection}
              className="h-9 rounded px-3 text-xs font-semibold text-white"
              style={{ backgroundColor: "var(--color-primary)" }}
            >
              Tandai Teks Terpilih
            </button>
          </div>
          <p className="whitespace-pre-wrap text-sm leading-7" style={{ fontFamily: "var(--font-serif-essay)" }}>
            {cleanText || "Tempel atau muat teks dokumen versi untuk memulai anotasi."}
          </p>
        </section>

        <section className="col-span-7 flex flex-col gap-4 rounded-xl border p-5" style={{ backgroundColor: "var(--color-surface)", borderColor: "var(--color-border)" }}>
          <h1 className="text-lg font-bold">Komponen & Relasi Teranotasi ({nodes.length} Node)</h1>
          <div className="flex flex-col gap-2">
            {nodes.map((n) => (
              <div key={n.node_key} className="rounded border p-2 text-xs" style={{ borderColor: "var(--color-border)" }}>
                <strong className="font-mono">{n.node_key} ({n.node_type})</strong>: {n.text_content}
              </div>
            ))}
          </div>
          <div className="mt-auto flex items-center justify-between border-t pt-4" style={{ borderColor: "var(--color-border)" }}>
            <label className="flex items-center gap-2 text-xs font-semibold">
              Skor ClarityOfClaim (1–5):
              <input
                type="number"
                min={1}
                max={5}
                value={clarityScore}
                onChange={(e) => setClarityScore(Number(e.target.value))}
                className="h-9 w-16 rounded border px-2"
                style={{ borderColor: "var(--color-border)" }}
              />
            </label>
            <button
              type="button"
              disabled={nodes.length === 0}
              onClick={() => void handleSubmitAnnotation()}
              className="h-10 rounded-md px-5 text-sm font-semibold text-white disabled:opacity-50"
              style={{ backgroundColor: "var(--color-secondary)" }}
            >
              Submit Anotasi Blind
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}
