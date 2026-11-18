"use client";

import { useEffect, useRef } from "react";

import type { ArgumentNode } from "@argumind/shared-schemas";

import { useWorkspaceStore } from "@/stores/workspaceStore";

const NODE_BORDER_VARS: Record<string, string> = {
  Claim: "var(--node-claim-border)",
  ExplicitPremise: "var(--node-premise-border)",
  Evidence: "var(--node-evidence-border)",
};

export interface AnnotatedTextPaneProps {
  readonly cleanText: string;
  readonly nodes: readonly ArgumentNode[];
}

export function AnnotatedTextPane({ cleanText, nodes }: AnnotatedTextPaneProps): React.JSX.Element {
  const selectedNodeId = useWorkspaceStore((s) => s.selectedNodeId);
  const selectNode = useWorkspaceStore((s) => s.selectNode);
  const spanRefs = useRef<Record<string, HTMLButtonElement | null>>({});

  useEffect(() => {
    if (!selectedNodeId) return;
    const el = spanRefs.current[selectedNodeId];
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [selectedNodeId]);

  const spanNodes = [...nodes]
    .filter((n) => n.start_char !== null && n.end_char !== null)
    .sort((a, b) => (a.start_char ?? 0) - (b.start_char ?? 0));

  const segments: React.ReactNode[] = [];
  let cursor = 0;
  for (const node of spanNodes) {
    const start = node.start_char ?? 0;
    const end = node.end_char ?? 0;
    if (start < cursor || end > cleanText.length) continue;
    if (start > cursor) {
      segments.push(<span key={`plain-${cursor}`}>{cleanText.slice(cursor, start)}</span>);
    }
    const isSelected = selectedNodeId === node.node_key;
    const borderColor = NODE_BORDER_VARS[node.node_type] ?? "var(--color-border)";
    segments.push(
      <button
        key={node.node_key}
        type="button"
        ref={(el) => {
          spanRefs.current[node.node_key] = el;
        }}
        data-node-id={node.node_key}
        onClick={() => selectNode(node.node_key)}
        className="mx-0.5 inline rounded px-1 py-0.5 text-left transition-colors"
        style={{
          borderBottom: `2px solid ${borderColor}`,
          backgroundColor: isSelected ? "var(--color-info-bg)" : "transparent",
          boxShadow: isSelected ? `0 0 0 2px ${borderColor}` : "none",
        }}
      >
        <span className="mr-1 font-mono text-xs font-bold" style={{ color: borderColor }}>
          [{node.node_key}]
        </span>
        {cleanText.slice(start, end)}
      </button>
    );
    cursor = end;
  }
  if (cursor < cleanText.length) {
    segments.push(<span key={`tail-${cursor}`}>{cleanText.slice(cursor)}</span>);
  }

  return (
    <section
      aria-label="Panel Teks Dokumen"
      className="h-full overflow-y-auto rounded-xl border p-5"
      style={{
        backgroundColor: "var(--color-surface)",
        borderColor: "var(--color-border)",
        fontFamily: "var(--font-serif-essay)",
      }}
    >
      <h2 className="mb-3 font-sans text-sm font-semibold" style={{ color: "var(--color-text-secondary)" }}>
        Teks Bersih (Sorotan Span Komponen)
      </h2>
      <div className="max-w-[68ch] whitespace-pre-wrap text-base leading-7">{segments}</div>
    </section>
  );
}
