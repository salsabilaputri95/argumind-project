-- Argumind Platform Initial Database Schema (PostgreSQL 16)
-- Source of truth: docs/DATA_MODEL.md

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1. Enum definitions
CREATE TYPE user_role_enum AS ENUM ('author', 'reviewer', 'annotator', 'org_admin');
CREATE TYPE domain_strata_enum AS ENUM ('academic', 'policy_business');
CREATE TYPE source_format_enum AS ENUM ('txt', 'md', 'docx', 'pdf');
CREATE TYPE run_source_enum AS ENUM ('ai_hybrid', 'human_annotator', 'gold_adjudicated');
CREATE TYPE run_status_enum AS ENUM (
    'QUEUED', 'STAGE_1_STRUCTURE', 'STAGE_2_IMPLICIT',
    'COMPLETED', 'FAILED', 'SCORING_VALIDATION_FAILED'
);
CREATE TYPE node_type_enum AS ENUM (
    'Claim', 'ExplicitPremise', 'ImplicitPremise', 'Evidence', 'Counterargument'
);
CREATE TYPE relation_type_enum AS ENUM ('Support', 'Attack');
CREATE TYPE gap_type_enum AS ENUM (
    'UnsupportedClaim', 'HastyGeneralization', 'FalseCause',
    'CircularReasoning', 'MissingCounterargumentConsideration', 'WeakEvidence'
);
CREATE TYPE severity_enum AS ENUM ('Low', 'Medium', 'High');
CREATE TYPE rubric_dim_enum AS ENUM (
    'ClarityOfClaim', 'PremiseSupportAndCoherence',
    'EvidenceAdequacy', 'CounterargumentAndLimitationAwareness'
);
CREATE TYPE feedback_status_enum AS ENUM ('PENDING', 'ACCEPTED', 'REJECTED');

-- 2. Tables (9 core entities)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(160) NOT NULL,
    slug VARCHAR(80) NOT NULL UNIQUE CHECK (slug ~ '^[a-z0-9-]+$'),
    monthly_doc_quota INTEGER NOT NULL DEFAULT 100 CHECK (monthly_doc_quota >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NULL REFERENCES organizations(id) ON DELETE RESTRICT,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(120) NOT NULL,
    external_identity_id VARCHAR(128) NULL UNIQUE,
    role user_role_enum NOT NULL DEFAULT 'author',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NULL REFERENCES organizations(id) ON DELETE RESTRICT,
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    title VARCHAR(255) NOT NULL,
    domain_strata domain_strata_enum NOT NULL DEFAULT 'academic',
    research_opt_in BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE document_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL CHECK (version_number >= 1),
    source_format source_format_enum NOT NULL,
    raw_s3_key VARCHAR(512) NULL,
    clean_text TEXT NOT NULL,
    content_sha256 CHAR(64) NOT NULL,
    word_count INTEGER NOT NULL CHECK (word_count BETWEEN 300 AND 2500),
    paragraph_offsets JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (document_id, version_number)
);

CREATE TABLE analysis_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doc_version_id UUID NOT NULL REFERENCES document_versions(id) ON DELETE CASCADE,
    run_source run_source_enum NOT NULL DEFAULT 'ai_hybrid',
    actor_user_id UUID NULL REFERENCES users(id) ON DELETE SET NULL,
    status run_status_enum NOT NULL DEFAULT 'QUEUED',
    model_versions JSONB NOT NULL DEFAULT '{}'::jsonb,
    latency_ms INTEGER NULL CHECK (latency_ms >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE argument_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
    node_key VARCHAR(16) NOT NULL,
    node_type node_type_enum NOT NULL,
    start_char INTEGER NULL CHECK (start_char >= 0),
    end_char INTEGER NULL,
    text_content TEXT NOT NULL,
    evidence_strength SMALLINT NULL CHECK (evidence_strength BETWEEN 1 AND 5),
    target_node_id UUID NULL REFERENCES argument_nodes(id) ON DELETE CASCADE,
    user_feedback feedback_status_enum NOT NULL DEFAULT 'PENDING',
    UNIQUE (run_id, node_key),
    CHECK (
        (node_type IN ('Claim', 'ExplicitPremise', 'Evidence')
            AND start_char IS NOT NULL AND end_char IS NOT NULL AND end_char > start_char)
        OR
        (node_type IN ('ImplicitPremise', 'Counterargument')
            AND start_char IS NULL AND end_char IS NULL AND target_node_id IS NOT NULL)
    ),
    CHECK (
        (node_type = 'Evidence' AND evidence_strength BETWEEN 1 AND 5)
        OR (node_type <> 'Evidence')
    )
);

CREATE TABLE argument_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
    edge_key VARCHAR(16) NOT NULL,
    source_node_id UUID NOT NULL REFERENCES argument_nodes(id) ON DELETE CASCADE,
    target_node_id UUID NOT NULL REFERENCES argument_nodes(id) ON DELETE CASCADE,
    relation_type relation_type_enum NOT NULL,
    confidence NUMERIC(4,3) NOT NULL CHECK (confidence BETWEEN 0.000 AND 1.000),
    nli_probs JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (run_id, edge_key),
    UNIQUE (run_id, source_node_id, target_node_id),
    CHECK (source_node_id <> target_node_id)
);

CREATE TABLE reasoning_gaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
    gap_key VARCHAR(16) NOT NULL,
    gap_type gap_type_enum NOT NULL,
    severity severity_enum NOT NULL,
    target_node_id UUID NULL REFERENCES argument_nodes(id) ON DELETE CASCADE,
    target_edge_id UUID NULL REFERENCES argument_edges(id) ON DELETE CASCADE,
    explanation TEXT NOT NULL,
    UNIQUE (run_id, gap_key),
    CHECK (target_node_id IS NOT NULL OR target_edge_id IS NOT NULL)
);

CREATE TABLE rubric_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
    dimension rubric_dim_enum NOT NULL,
    ai_score SMALLINT NOT NULL CHECK (ai_score BETWEEN 1 AND 5),
    grounded_refs JSONB NOT NULL CHECK (jsonb_array_length(grounded_refs) >= 1),
    rationale TEXT NOT NULL,
    human_override_score SMALLINT NULL CHECK (human_override_score BETWEEN 1 AND 5),
    reviewer_id UUID NULL REFERENCES users(id) ON DELETE SET NULL,
    override_note TEXT NULL,
    UNIQUE (run_id, dimension),
    CHECK (
        human_override_score IS NULL
        OR (reviewer_id IS NOT NULL AND override_note IS NOT NULL AND char_length(override_note) >= 10)
    )
);

-- 3. Performance Indices
CREATE INDEX idx_doc_versions_sha256 ON document_versions (content_sha256);
CREATE INDEX idx_runs_docver_source ON analysis_runs (doc_version_id, run_source, status);
CREATE INDEX idx_nodes_run_type ON argument_nodes (run_id, node_type);
CREATE INDEX idx_scores_grounded_refs ON rubric_scores USING GIN (grounded_refs);
