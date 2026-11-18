import { z } from "zod";

export const UserRoleSchema = z.enum(["author", "reviewer", "annotator", "org_admin"]);
export type UserRole = z.infer<typeof UserRoleSchema>;

export const DomainStrataSchema = z.enum(["academic", "policy_business"]);
export type DomainStrata = z.infer<typeof DomainStrataSchema>;

export const NodeTypeSchema = z.enum([
  "Claim",
  "ExplicitPremise",
  "ImplicitPremise",
  "Evidence",
  "Counterargument",
]);
export type NodeType = z.infer<typeof NodeTypeSchema>;

export const RelationTypeSchema = z.enum(["Support", "Attack"]);
export type RelationType = z.infer<typeof RelationTypeSchema>;

export const GapTypeSchema = z.enum([
  "UnsupportedClaim",
  "HastyGeneralization",
  "FalseCause",
  "CircularReasoning",
  "MissingCounterargumentConsideration",
  "WeakEvidence",
]);
export type GapType = z.infer<typeof GapTypeSchema>;

export const SeverityLevelSchema = z.enum(["Low", "Medium", "High"]);
export type SeverityLevel = z.infer<typeof SeverityLevelSchema>;

export const RubricDimensionSchema = z.enum([
  "ClarityOfClaim",
  "PremiseSupportAndCoherence",
  "EvidenceAdequacy",
  "CounterargumentAndLimitationAwareness",
]);
export type RubricDimension = z.infer<typeof RubricDimensionSchema>;

export const FeedbackStatusSchema = z.enum(["PENDING", "ACCEPTED", "REJECTED"]);
export type FeedbackStatus = z.infer<typeof FeedbackStatusSchema>;

export const ArgumentNodeSchema = z.object({
  node_key: z.string().min(2).max(16),
  node_type: NodeTypeSchema,
  start_char: z.number().int().nonnegative().nullable(),
  end_char: z.number().int().positive().nullable(),
  text_content: z.string().min(1),
  evidence_strength: z.number().int().min(1).max(5).nullable().optional(),
  target_node_key: z.string().nullable().optional(),
  user_feedback: FeedbackStatusSchema.default("PENDING"),
});
export type ArgumentNode = z.infer<typeof ArgumentNodeSchema>;

export const ArgumentEdgeSchema = z.object({
  edge_key: z.string().min(2).max(16),
  source_key: z.string().min(2).max(16),
  target_key: z.string().min(2).max(16),
  relation_type: RelationTypeSchema,
  confidence: z.number().min(0).max(1),
  nli_probs: z.record(z.string(), z.number()).default({}),
});
export type ArgumentEdge = z.infer<typeof ArgumentEdgeSchema>;

export const ReasoningGapSchema = z.object({
  gap_key: z.string().min(2).max(16),
  gap_type: GapTypeSchema,
  severity: SeverityLevelSchema,
  target_node_key: z.string().nullable().optional(),
  target_edge_key: z.string().nullable().optional(),
  explanation: z.string().min(5),
});
export type ReasoningGap = z.infer<typeof ReasoningGapSchema>;

export const RubricScoreSchema = z.object({
  dimension: RubricDimensionSchema,
  ai_score: z.number().int().min(1).max(5),
  grounded_refs: z.array(z.string()).min(1),
  rationale: z.string().min(5),
  human_override_score: z.number().int().min(1).max(5).nullable().optional(),
  reviewer_id: z.string().nullable().optional(),
  override_note: z.string().nullable().optional(),
});
export type RubricScore = z.infer<typeof RubricScoreSchema>;

export const ProblemDetailsSchema = z.object({
  type: z.string(),
  title: z.string(),
  status: z.number().int(),
  code: z.string(),
  detail: z.string(),
  trace_id: z.string(),
});
export type ProblemDetails = z.infer<typeof ProblemDetailsSchema>;
