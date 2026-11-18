"use client";

import { useEffect, useState } from "react";

import type {
  ArgumentEdge,
  ArgumentNode,
  ReasoningGap,
  RubricScore,
} from "@argumind/shared-schemas";

import { API_BASE_URL } from "@/lib/apiClient";

export type PipelineStage =
  | "IDLE"
  | "STAGE_1_STRUCTURE"
  | "STAGE_2_IMPLICIT_GAPS"
  | "COMPLETED";

export interface StreamedGraphState {
  readonly stage: PipelineStage;
  readonly nodes: readonly ArgumentNode[];
  readonly edges: readonly ArgumentEdge[];
  readonly gaps: readonly ReasoningGap[];
  readonly scores: readonly RubricScore[];
}

export function useArgumentStream(
  jobId: string | null,
  initialRunData?: {
    readonly nodes: readonly ArgumentNode[];
    readonly edges: readonly ArgumentEdge[];
    readonly gaps: readonly ReasoningGap[];
    readonly scores: readonly RubricScore[];
  }
): StreamedGraphState {
  const [stage, setStage] = useState<PipelineStage>("IDLE");
  const [nodes, setNodes] = useState<readonly ArgumentNode[]>(initialRunData?.nodes ?? []);
  const [edges, setEdges] = useState<readonly ArgumentEdge[]>(initialRunData?.edges ?? []);
  const [gaps, setGaps] = useState<readonly ReasoningGap[]>(initialRunData?.gaps ?? []);
  const [scores, setScores] = useState<readonly RubricScore[]>(initialRunData?.scores ?? []);

  useEffect(() => {
    if (!initialRunData) return;
    setNodes(initialRunData.nodes);
    setEdges(initialRunData.edges);
    setGaps(initialRunData.gaps);
    setScores(initialRunData.scores);
    setStage("COMPLETED");
  }, [initialRunData]);

  useEffect(() => {
    if (!jobId) return;
    const source = new EventSource(`${API_BASE_URL}/api/v1/jobs/${jobId}/stream`, {
      withCredentials: true,
    });

    source.addEventListener("stage_1_structure", (ev: MessageEvent<string>) => {
      const parsed = JSON.parse(ev.data) as {
        nodes: ArgumentNode[];
        edges: ArgumentEdge[];
      };
      setNodes(parsed.nodes);
      setEdges(parsed.edges);
      setStage("STAGE_1_STRUCTURE");
    });

    source.addEventListener("stage_2_implicit_gaps", (ev: MessageEvent<string>) => {
      const parsed = JSON.parse(ev.data) as {
        nodes: ArgumentNode[];
        gaps: ReasoningGap[];
      };
      setNodes((prev) => [...prev, ...parsed.nodes]);
      setGaps(parsed.gaps);
      setStage("STAGE_2_IMPLICIT_GAPS");
    });

    source.addEventListener("stage_3_scoring_complete", (ev: MessageEvent<string>) => {
      const parsed = JSON.parse(ev.data) as { scores: RubricScore[] };
      setScores(parsed.scores);
      setStage("COMPLETED");
      source.close();
    });

    return () => {
      source.close();
    };
  }, [jobId]);

  return { stage, nodes, edges, gaps, scores };
}
