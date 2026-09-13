# Procedure Chunk & DAG Design Blueprint

## 1. Objective

Build a **deterministic compiler pipeline** that converts enterprise policy/SOP documents into a set of **high-confidence, executable business procedures** organized as a **Procedure DAG**, which an AI verification agent can execute with full traceability and near-complete policy coverage.

Pipeline:

```text
PDF / HTML
   │
   ▼
DocumentTree        # layout hierarchy (BDA + tree builder + DSVE)
   │
   ▼
Raw Chunks          # structural intermediate representation (IR)
   │
   ▼
Procedure Chunks    # executable semantic units
   │
   ▼
Procedure DAG       # compiled execution plan / knowledge graph
   │
   ▼
AI Verification Agent
```

Clarifications:

- The final artifact is **not** a vector database, but an **executable business knowledge graph** (Procedure DAG) that encodes how an expert human verifier would operate.
- Each stage increases semantic understanding while preserving provenance (section paths, page numbers, span IDs, raw_chunk_ids).

---

## 2. Requirements

### 2.1 Deterministic upstream pipeline

Everything up to **RawChunks** must be deterministic:

- Same document + same parser + same DSVE + same chunking config →
  - Identical `DocumentTree`.
  - Identical RawChunks.
  - Identical IDs.

This is essential for reproducibility, observability, versioning, and incremental regeneration.

### 2.2 RawChunk triage & classification

We must triage raw chunks before procedure extraction:

- Assign categories such as:
  - `primary_rule_block` / `VERIFICATION_RULE`
  - `conditional_modifier` / `EXCEPTION_RULE`
  - `reference_table` / `GLOBAL_CONSTRAINT`
  - `informational_context` / `DEFINITION` / `REFERENCE`
- Only rule-bearing categories become **primary candidates** for procedure extraction; others are **supporting context**.

This is analogous to clause-mining in policy-to-rules frameworks (pre-filter spans that likely contain enforceable policy).

### 2.3 Goldilocks granularity control

Avoid extremes:

- Too fine: hundreds of microscopic, sentence-level procedure chunks.
- Too coarse: a few massive "god chunks" combining many unrelated rules.

Strategy:

- Cluster rules into coherent, macro-logical verification blocks (e.g., "Identity Verification Sequence", "Utility Bill Verification").
- Use anchors such as `target_document_type` or verification domain.
- Apply simple limits:
  - Max rules per procedure chunk.
  - Max token size per procedure chunk.

Each procedure chunk should represent a **verification capability** rather than a single sentence.

### 2.4 Global data schema standardization

Before extraction, define a **Policy Data Dictionary**:

- Deduplicated variable set, e.g.: `customer_age`, `customer_country`, `document_language`, `has_certified_translation`, etc.
- Extraction LLM must **only** use variables from this dictionary:
  - No on-the-fly creation of new fields.

This prevents variable name sprawl (different keys for the same concept) and aligns with policy-as-code DSL design.

### 2.5 Context-insulated iterative extraction

Procedure chunks must be built from **scoped, enriched contexts**:

- Process one primary candidate RawChunk (or small group) at a time.
- Inject relevant context from other chunks:
  - Conditional modifiers (exceptions).
  - Reference tables.
  - Global constraints (general provisions, appendices).
  - Definitions and glossaries.

This captures hidden logic (e.g., foreign language translation rules) without feeding the entire policy into every LLM call.

### 2.6 Strict action taxonomy

Each procedure chunk is typed into an **action taxonomy**, for tool routing and security:

Examples:

- `document_verification`
- `data_retrieval`
- `logic_evaluation`
- `calculation`
- `system_action`

This guides downstream agents to:

- Choose the right tools (OCR, DB access, pure reasoning).
- Enforce security boundaries (e.g., read-only vs write operations).

### 2.7 Execution sequencing & AND/OR logic

Each procedure chunk declares its execution prerequisites and logical connectors:

- Prerequisite chunks.
- Required inputs.
- AND conditions (must satisfy all).
- OR conditions (any of multiple acceptable paths/documents).

A deterministic compiler uses this to construct conditional pathways in the Procedure DAG:

- Strict ordering.
- Parallel branches.
- Decision nodes.

### 2.8 Strict separation of concerns (LLM vs Python)

- **LLM responsibilities**:
  - Transform unstructured text into semantic content:
    - Domain scope.
    - Inputs and outputs.
    - Conditions, actions, exceptions.
    - Possible outcomes.
  - Produce only structured JSON conforming to a fixed schema.

- **Python responsibilities**:
  - Generate IDs, versions, hashes.
  - Attach provenance (`source_raw_chunk_ids`, `source_node_ids`, doc/page references).
  - Validate schemas and enforce variable dictionary.
  - Apply structural metadata: parent-child pointers, DAG edges, timestamps.

LLM must **not** generate chunk IDs, structural pointers, or new schema fields.

### 2.9 Provenance and local lineage

Every execution rule step inside a procedure chunk must map back to:

- RawChunks: `source_raw_chunk_ids`.
- DocumentTree nodes: `source_node_ids`.
- Document citations: section path, page number, span ID.

This supports:

- Human audit.
- Regulatory defensibility.
- Debugging and replay when an agent decision is challenged.

### 2.10 Tool-scoping / security boundaries

Based on the action taxonomy:

- `logic_evaluation` and `calculation` chunks are sandboxed:
  - Read-only, no external side effects.
- `system_action` chunks that trigger writes or external calls must be governed by policy-as-code guardrails (e.g., PDP/PEP separation).

This mitigates prompt-injection and unsafe agent behaviour.

### 2.11 Complete policy coverage

Coverage requirement:

- Every enforceable business rule (verification, exception, prerequisite, threshold, dependency) should:
  - Be represented inside one or more ProcedureChunks, or
  - Be explicitly flagged as unmapped/non-procedural.

Coverage matters more than chunk size or elegance.

---

## 3. Constraints

### 3.1 Policies are written for humans

- Organised by chapters, departments, legal structures.
- Not aligned with agent execution workflows.

Consequences:

- Document hierarchy ≠ execution hierarchy.
- Procedure boundaries must be based on semantic verification capabilities, not just headings or pages.

### 3.2 Dependencies are often implicit

- Many rules depend on others without explicit cross-references.

Example:

- Section 2: Passport requirements.
- Section 10: All foreign-language documents must be notarised.

These are dependent but may not mention each other.

Dependency discovery must combine:

- DSVE metadata (references, exceptions, constraint flags).
- Semantic similarity / topic grouping.
- LLM reasoning.

### 3.3 Business logic is distributed

- One verification procedure might require:
  - Paragraphs.
  - Tables.
  - Appendices.
  - Definitions.
  - Exceptions.

Spread across many pages and sections.

### 3.4 One-to-many and many-to-one relationships

- One RawChunk can produce many ProcedureChunks.
- Many RawChunks can feed one ProcedureChunk.

Examples:

- Identity document rules RawChunk → separate procedures for passport, driving licence, national ID.
- Eligibility + exceptions + country rules RawChunks → one "Verify Passport" procedure.

### 3.5 LLMs are probabilistic and fallible

- Extraction is not guaranteed complete.
- LLMs can miss subtle rules and hallucinate non-existent ones.

We must:

- Assume fallibility.
- Implement validation layers (judge + repair, PVE).

### 3.6 Schema immutability during extraction

- The Policy Data Dictionary is fixed during an extraction run.
- LLM cannot invent new variable names.

Schema evolution must be deliberate (through data model updates), not emergent from LLM calls.

### 3.7 No LLM-generated structural metadata

- LLM must not create:
  - `procedure_id`, `raw_chunk_id`.
  - Parent/child pointers.
  - DAG edges.
  - Timestamps.

Structural metadata is computed deterministically in Python.

---

## 4. Challenges

### 4.1 Defining a ProcedureChunk precisely

Open question:

- Is a ProcedureChunk:
  - One rule?
  - One verification operation?
  - One document-type procedure?
  - One business capability?

We need a formal definition with:

- Invariants.
- Mandatory fields.
- Boundary rules (what it is and is not).

### 4.2 Inferring hidden dependencies ("invisible thread")

- Connecting rules across:
  - Main sections.
  - Appendices.
  - Glossaries.
  - General provisions.

Often no explicit references.

Solution space:

- DSVE metadata (references, exception targets).
- Semantic clustering (embeddings, topics).
- LLM prompts for dependency discovery.

### 4.3 Avoiding silent dropped rules

Risk:

- LLM extracts obvious rules but quietly misses nuanced conditions or exceptions.

Mitigations:

- Clause-level coverage mapping: every sentence/list item/table row mapped or flagged.
- Judge + repair loops.
- Procedure Validation Engine (PVE) that checks for unmapped spans.

### 4.4 Variable name sprawl

Risk:

- Multiple keys for same concept (`customer_age`, `age_of_applicant`, `age`).

Mitigations:

- Central variable dictionary.
- Automatic harmonisation and de-duplication.
- LLM + deterministic checks to consolidate similar variables.

### 4.5 Unreachable or orphan DAG nodes

Risks:

- Orphan procedure chunks never called.
- Deadlocked nodes waiting on inputs that never arrive.

Mitigations:

- DAG builder must detect:
  - Unreachable nodes.
  - Cycles.
  - Nodes with unresolved inputs.

### 4.6 Guaranteeing completeness

Hardest problem:

- How to know **every rule** is represented.

Approach:

- Clause-level mapping from RawChunks → ProcedureChunks.
- Metrics for coverage (% of enforceable clauses mapped).
- Human + AI review for high-stakes policies.

### 4.7 Measuring confidence

Confidence is multi-dimensional:

- Extraction confidence.
- Dependency confidence.
- Completeness coverage confidence.
- Traceability confidence.
- Validation confidence (PVE results).

We need a composite confidence score per ProcedureChunk and per DAG.

### 4.8 Preventing hallucinations

- ProcedureChunks must **derive** logic from text; they must not invent new obligations.

Mitigations:

- Prompts explicitly require citing source spans for each rule.
- PVE flags rules with no grounded span.

### 4.9 Validating ProcedureChunks (PVE)

We need a Procedure Validation Engine analogous to DSVE:

Responsibilities:

- Completeness and coverage checks.
- Dependency correctness.
- Contradiction detection (logical conflicts between rules).
- Orphan/unreachable procedure detection.
- Missing exceptions/inputs/outputs/references.
- Confidence scoring.
- Repair loop (self-healing prompts).

### 4.10 Building the Procedure DAG

Even with ProcedureChunks, DAG construction is a separate reasoning layer:

Tasks:

- Discover execution order.
- Identify reusable nodes.
- Define parallel branches and decision points.
- Apply action taxonomy for routing.

---

## 5. Next Steps (Future Enhancements)

### Phase 1 — Define ProcedureChunk formally

- Write a rigorous spec:
  - Invariants.
  - Mandatory fields.
  - Boundary rules.
- Encode in JSON/DSL similar to P2T-style rule schemas.

### Phase 2 — Procedure Chunk Generation Engine

- Design transformation:
  - RawChunk triage and classification.
  - Merge/split strategy for candidate chunks.
  - Dependency inference (symbolic + semantic).
  - Context inheritance (global constraints, exceptions, definitions).

### Phase 3 — Procedure Validation Engine (PVE)

- Build semantic validator:
  - Completeness and coverage validation.
  - Dependency and contradiction checking (SMT-style).
  - Confidence scoring.
  - Judge + repair loop for self-correction.

### Phase 4 — Procedure DAG Builder

- Construct execution graph:
  - Nodes: ProcedureChunks.
  - Edges: prerequisites, dependencies, exception flows, optional paths, reuse links.

### Phase 5 — Agent Execution Runtime

- Execute the DAG instead of policies:
  - Deterministic, auditable execution.
  - Explainability and traceability.
  - Policy-as-code guardrails for side effects.

### Additional Enhancements

- Self-healing loops when PVE or AI reviewer finds discrepancies.
- Cross-policy drift analysis: compare DAGs across policy versions to highlight rule changes.
- Dynamic tool-routing based on action taxonomy.
- Graceful degradation: auto-escalation to human when key data sources or APIs fail.

---

This blueprint is the foundation for the upcoming **Procedure Chunk Engine** specification and for designing PVE and the DAG builder.
