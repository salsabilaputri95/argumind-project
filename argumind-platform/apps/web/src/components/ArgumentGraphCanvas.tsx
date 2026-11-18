"use client";

import { useMemo } from "react";
import {
  Background,
  Controls,
  MarkerType,
  ReactFlow,
  type Edge,
  type Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import type { ArgumentEdge, ArgumentNode, ReasoningGap } from "@argumind/shared-schemas";

import { useWorkspaceStore } from "@/stores/workspaceStore";

const NODE_STYLE_MAP: Record<string, { border: string; style: string; tag: string }> = {
  Claim: { border: "var(--node-claim-border)", style: "solid", tag: "[C] CLAIM" },
  ExplicitPremise: { border: "var(--node-premise-border)", style: "solid", tag: "[P] PREMISE" },
  ImplicitPremise: { border: "var(--node-implicit-border)", style: "dashed", tag: "[IP] IMPLICIT" },
  Evidence: { border: "var(--node-evidence-border)", style: "solid", tag: "[E] EVIDENCE" },
  Counterargument: { border: "var(--node-counter-border)", style: "dotted", tag: "[CA] COUNTER" },
};

export interface ArgumentGraphCanvasProps {
  readonly nodes: readonly ArgumentNode[];
  readonly edges: readonly ArgumentEdge[];
  readonly gaps: readonly ReasoningGap[];
}

export function ArgumentGraphCanvas({
  nodes,
  edges,
  gaps,
}: ArgumentGraphCanvasProps): React.JSX.Element {
  const selectedNodeId = useWorkspaceStore((s) => s.selectedNodeId);
  const selectNode = useWorkspaceStore((s) => s.selectNode);

  const flowNodes: Node[] = useMemo(() => {
    const laneIndex: Record<string, number> = {};
    return nodes.map((n, idx) => {
      const row = n.node_type === "Claim" ? 0 : n.node_type === "ImplicitPremise" ? 1 : 2;
      const col = laneIndex[String(row)] ?? 0;
      laneIndex[String(row)] = col + 1;
      const styleMeta = NODE_STYLE_MAP[n.node_type] ?? {
        border: "var(--color-border)",
        style: "solid",
        tag: n.node_type,
      };
      const nodeGaps = gaps.filter((g) => g.target_node_key === n.node_key);
      const isSelected = selectedNodeId === n.node_key;
      return {
        id: n.node_key,
        position: { x: col * 290 + 24, y: row * 170 + 24 + (idx % 2) * 18 },
        data: {
          label: (
            <div
              className="w-[260px] rounded-xl p-3 text-left"
              style={{
                backgroundColor: "var(--color-surface)",
                border: `2px ${styleMeta.style} ${styleMeta.border}`,
                borderLeftWidth: "6px",
                boxShadow: isSelected ? "0 0 0 3px var(--color-primary)" : "var(--shadow-sm)",
              }}
            >
              <div className="flex items-center justify-between font-mono text-xs font-bold" style={{ color: styleMeta.border }}>
                <span>{styleMeta.tag} • {n.node_key}</span>
                {nodeGaps.length > 0 && (
                  <span
                    className="rounded-full px-2 py-0.5 text-[11px]"
                    style={{ backgroundColor: "var(--color-error-bg)", color: "var(--color-error)" }}
                  >
                    {nodeGaps[0]?.gap_key}
                  </span>
                )}
              </div>
              <p className="mt-1.5 line-clamp-3 text-xs" style={{ color: "var(--color-text-primary)" }}>
                {n.text_content}
              </p>
            </div>
          ),
        },
        style: { background: "transparent", border: "none", padding: 0, width: 260 },
      };
    });
  }, [nodes, gaps, selectedNodeId]);

  const flowEdges: Edge[] = useMemo(
    () =>
      edges.map((e) => {
        const isAttack = e.relation_type === "Attack";
        const color = isAttack ? "var(--color-error)" : "var(--color-success)";
        return {
          id: e.edge_key,
          source: e.source_key,
          target: e.target_key,
          label: `${isAttack ? "[x Attack" : "[+ Support"} | ${e.confidence.toFixed(2)}]`,
          animated: false,
          markerEnd: { type: MarkerType.ArrowClosed, color },
          style: {
            stroke: color,
            strokeWidth: 1.5 + e.confidence * 1.5,
            strokeDasharray: isAttack ? "6 4" : undefined,
          },
        };
      }),
    [edges]
  );

  if (nodes.length === 0) {
    return (
      <div className="flex h-full items-center justify-center rounded-xl border p-6" style={{ borderColor: "var(--color-border)" }}>
        <div className="w-[320px] rounded-lg border p-4 text-center text-sm" style={{ borderColor: "var(--color-border)", color: "var(--color-text-secondary)" }}>
          Belum ada struktur argumen. Jalankan analisis untuk merender peta klaim-premis.
        </div>
      </div>
    );
  }

  return (
    <div className="h-full w-full">
      {/* Desktop/Tablet Graph Canvas (>= 768px) */}
      <div className="hidden h-full w-full overflow-hidden rounded-xl border md:block" style={{ borderColor: "var(--color-border)", backgroundColor: "var(--color-bg-canvas)" }}>
        <ReactFlow
          nodes={flowNodes}
          edges={flowEdges}
          onNodeClick={(_, node) => selectNode(node.id)}
          fitView
        >
          <Background gap={16} />
          <Controls />
        </ReactFlow>
      </div>

      {/* Mobile Structured Card List View (< 768px, sesuai PAGES_AND_FLOWS.md#4) */}
      <div className="flex flex-col gap-3 md:hidden" aria-label="Daftar Kartu Struktur Argumen">
        {nodes.map((n) => {
          const styleMeta = NODE_STYLE_MAP[n.node_type] ?? {
            border: "var(--color-border)",
            style: "solid",
            tag: n.node_type,
          };
          return (
            <button
              key={n.node_key}
              type="button"
              onClick={() => selectNode(n.node_key)}
              className="min-h-[44px] w-full rounded-xl p-3 text-left"
              style={{
                backgroundColor: "var(--color-surface)",
                border: `2px ${styleMeta.style} ${styleMeta.border}`,
              }}
            >
              <div className="font-mono text-xs font-bold" style={{ color: styleMeta.border }}>
                {styleMeta.tag} • {n.node_key}
              </div>
              <p className="mt-1 text-sm">{n.text_content}</p>
            </button>
          );
        })}
      </div>
    </div>
  );
}
