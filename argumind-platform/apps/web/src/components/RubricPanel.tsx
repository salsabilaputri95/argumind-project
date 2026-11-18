"use client";

import { useState } from "react";

import type { ArgumentNode, ReasoningGap, RubricScore } from "@argumind/shared-schemas";

import { apiFetch, ArgumindApiError } from "@/lib/apiClient";
import { useWorkspaceStore } from "@/stores/workspaceStore";

export interface RubricPanelProps {
  readonly runId: string;
  readonly userRole: string;
  readonly overallScore: number;
  readonly scores: readonly RubricScore[];
  readonly gaps: readonly ReasoningGap[];
  readonly implicitNodes: readonly ArgumentNode[];
  readonly onRefresh: () => void;
}

export function RubricPanel({
  runId,
  userRole,
  overallScore,
  scores,
  gaps,
  implicitNodes,
  onRefresh,
}: RubricPanelProps): React.JSX.Element {
  const selectNode = useWorkspaceStore((s) => s.selectNode);
  const pushToast = useWorkspaceStore((s) => s.pushErrorToast);
  const [editingDim, setEditingDim] = useState<string | null>(null);
  const [overrideScore, setOverrideScore] = useState<number>(3);
  const [overrideNote, setOverrideNote] = useState<string>("");

  async function submitOverride(dimension: string): Promise<void> {
    try {
      await apiFetch(`/api/v1/runs/${runId}/scores/${dimension}`, {
        method: "PATCH",
        body: JSON.stringify({
          human_override_score: overrideScore,
          override_note: overrideNote,
        }),
      });
      setEditingDim(null);
      setOverrideNote("");
      onRefresh();
    } catch (err) {
      if (err instanceof ArgumindApiError) {
        pushToast({ code: err.code, detail: err.detail ?? err.message, traceId: err.traceId });
      }
    }
  }

  async function submitNodeFeedback(nodeKey: string, feedback: "ACCEPTED" | "REJECTED"): Promise<void> {
    await apiFetch(`/api/v1/runs/${runId}/nodes/${nodeKey}/feedback`, {
      method: "PATCH",
      body: JSON.stringify({ user_feedback: feedback }),
    });
    onRefresh();
  }

  return (
    <aside className="flex h-full flex-col gap-4 overflow-y-auto rounded-xl border p-4" style={{ backgroundColor: "var(--color-surface)", borderColor: "var(--color-border)" }}>
      <div className="rounded-lg border p-3 text-xs" style={{ backgroundColor: "var(--color-warning-bg)", borderColor: "var(--color-warning)" }}>
        Skor bersifat diagnostik; keputusan nilai akhir tetap di tangan manusia.
      </div>

      <div className="flex items-baseline justify-between">
        <h2 className="text-base font-semibold">Skor Rubrik Diagnostik</h2>
        <span className="font-mono text-2xl font-bold" style={{ color: "var(--color-primary)" }}>
          {overallScore.toFixed(2)} / 5
        </span>
      </div>

      <div className="flex flex-col gap-3">
        {scores.map((s) => {
          const displayedScore = s.human_override_score ?? s.ai_score;
          return (
            <div key={s.dimension} className="rounded-lg border p-3" style={{ borderColor: "var(--color-border)" }}>
              <div className="flex items-center justify-between gap-2">
                <span className="text-sm font-semibold">{s.dimension}</span>
                <span className="font-mono text-sm font-bold">{displayedScore}/5</span>
              </div>
              <p className="mt-1 text-xs" style={{ color: "var(--color-text-secondary)" }}>
                {s.rationale}
              </p>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {s.grounded_refs.map((refKey) => (
                  <button
                    key={refKey}
                    type="button"
                    onClick={() => selectNode(refKey)}
                    className="rounded-full px-2 py-0.5 font-mono text-xs font-medium"
                    style={{ backgroundColor: "var(--color-info-bg)", color: "var(--color-info)" }}
                  >
                    {refKey}
                  </button>
                ))}
              </div>
              {userRole === "reviewer" && editingDim !== s.dimension && (
                <button
                  type="button"
                  onClick={() => {
                    setEditingDim(s.dimension);
                    setOverrideScore(displayedScore);
                  }}
                  className="mt-2 text-xs font-semibold underline"
                  style={{ color: "var(--color-primary)" }}
                >
                  Revisi Skor Pakar
                </button>
              )}
              {userRole === "reviewer" && editingDim === s.dimension && (
                <div className="mt-2 flex flex-col gap-2 border-t pt-2" style={{ borderColor: "var(--color-border)" }}>
                  <input
                    type="number"
                    min={1}
                    max={5}
                    value={overrideScore}
                    onChange={(e) => setOverrideScore(Number(e.target.value))}
                    className="h-9 rounded border px-2 text-sm"
                    style={{ borderColor: "var(--color-border)" }}
                  />
                  <textarea
                    rows={2}
                    placeholder="Catatan alasan pakar (min 10 karakter)"
                    value={overrideNote}
                    onChange={(e) => setOverrideNote(e.target.value)}
                    className="rounded border p-2 text-xs"
                    style={{ borderColor: "var(--color-border)" }}
                  />
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => void submitOverride(s.dimension)}
                      className="rounded px-3 py-1 text-xs font-semibold text-white"
                      style={{ backgroundColor: "var(--color-primary)" }}
                    >
                      Simpan
                    </button>
                    <button
                      type="button"
                      onClick={() => setEditingDim(null)}
                      className="rounded border px-3 py-1 text-xs"
                      style={{ borderColor: "var(--color-border)" }}
                    >
                      Batal
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {implicitNodes.length > 0 && (
        <div className="border-t pt-3" style={{ borderColor: "var(--color-border)" }}>
          <h3 className="text-sm font-semibold">Asumsi Implisit & Kontraargumen</h3>
          <div className="mt-2 flex flex-col gap-2">
            {implicitNodes.map((ip) => (
              <div key={ip.node_key} className="rounded-lg border p-2.5 text-xs" style={{ borderColor: "var(--node-implicit-border)" }}>
                <div className="font-mono font-bold">{ip.node_key} ({ip.node_type})</div>
                <p className="mt-1">{ip.text_content}</p>
                <div className="mt-2 flex gap-2">
                  <button
                    type="button"
                    onClick={() => void submitNodeFeedback(ip.node_key, "ACCEPTED")}
                    className="rounded px-2 py-1 font-semibold"
                    style={{ backgroundColor: "var(--color-success-bg)", color: "var(--color-success)" }}
                  >
                    Terima ({ip.user_feedback === "ACCEPTED" ? "✓" : ""})
                  </button>
                  <button
                    type="button"
                    onClick={() => void submitNodeFeedback(ip.node_key, "REJECTED")}
                    className="rounded px-2 py-1 font-semibold"
                    style={{ backgroundColor: "var(--color-error-bg)", color: "var(--color-error)" }}
                  >
                    Tandai Tidak Valid
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {gaps.length > 0 && (
        <div className="border-t pt-3" style={{ borderColor: "var(--color-border)" }}>
          <h3 className="text-sm font-semibold">Celah Penalaran ({gaps.length})</h3>
          <div className="mt-2 flex flex-col gap-2">
            {gaps.map((g) => (
              <div key={g.gap_key} className="rounded-lg border p-2.5 text-xs" style={{ backgroundColor: "var(--color-error-bg)", borderColor: "var(--color-error)" }}>
                <div className="font-mono font-bold">{g.gap_key} • {g.gap_type} ({g.severity})</div>
                <p className="mt-1">{g.explanation}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </aside>
  );
}
