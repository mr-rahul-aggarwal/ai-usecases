# Document Semantic Validation Engine (DSVE) Specification

## Purpose

The DSVE validates a candidate `DocumentTree` produced by the parser
(Amazon BDA, Docling, etc.) before it is used for chunking or rule
extraction.

The DSVE **does not parse documents**. It inspects the parsed tree,
detects inconsistencies, automatically fixes deterministic issues, and
invokes an LLM **only for ambiguous structural or semantic problems**.

``` text
Parser
→ Candidate DocumentTree
→ DSVE
    ├── Deterministic Validators
    ├── Auto Fix Engine
    ├── LLM Validation (only ambiguous cases)
    └── LLM Repair
→ Validated DocumentTree
```

## Validation Categories

### Level 1 -- Structural Integrity (Deterministic)

Checks: - Single logical root - No orphan nodes - No cycles -
Parent-child consistency - Valid heading hierarchy - Skipped heading
levels - Empty sections - Duplicate node IDs - Stable reading order -
Tables contain rows - Rows belong to one table - Lists contain list
items - Cross-page paragraph continuity

Auto-fix: - Duplicate IDs - Whitespace cleanup - Duplicate page
headers/footers - Missing parent when deterministically inferable

------------------------------------------------------------------------

### Level 2 -- Content Integrity (Deterministic)

Checks: - Empty paragraphs - Duplicate paragraphs - Duplicate headings -
Repeated page headers/footers - Broken markdown tables - Inconsistent
table column counts - Missing table headers - Encoding artifacts -
Unexpected page breaks

Auto-fix: - Normalize whitespace - Normalize numbering - Normalize
markdown - Remove duplicated page artifacts

------------------------------------------------------------------------

### Level 3 -- Relationship Integrity (Deterministic)

Checks: - Cross-reference target exists - Section numbering continuity -
Parent-child semantic consistency - Table attached to correct section -
List numbering continuity - Reference syntax validity

------------------------------------------------------------------------

### Level 4 -- Semantic Integrity (LLM)

Run ONLY if deterministic validation cannot resolve ambiguity.

Examples: - Ambiguous heading level - Wrong parent section - Table
attached to wrong heading - Ambiguous subsection boundaries -
Cross-reference normalization - Table reconstruction

## Issue Schema

``` json
{
  "validator":"HeadingValidator",
  "severity":"INFO|WARNING|ERROR",
  "node_id":"...",
  "issue_type":"HeadingHierarchy",
  "reason":"Heading jumps from H2 to H4",
  "recommended_action":"AUTO_FIX|LLM_REVIEW|MANUAL_REVIEW"
}
```

## Confidence Model

Compute confidence per node.

FinalConfidence = 0.35 × Parser Confidence + 0.25 × Structural Score +
0.20 × Relationship Score + 0.20 × Repair Score

Chunk confidence is derived from source node confidence.

## LLM Validation Prompt

### System Prompt

You are a document structure validator.

Your responsibility is ONLY to validate document hierarchy and
relationships.

Never rewrite text. Never summarize. Never invent content.

You may: - adjust heading level - move a node to another parent - repair
table hierarchy - normalize numbering - normalize references

Return JSON only.

### User Payload

Provide: - Current node - Parent node - Previous sibling - Next
sibling - Ancestor headings - Page number - Nearby text - Validation
issue

Return:

``` json
{
  "decision":"KEEP|MODIFY",
  "confidence":0.92,
  "reason":"...",
  "proposed_changes":{
    "parent_id":"...",
    "heading_level":2
  }
}
```

## LLM Repair Prompt

### System Prompt

You are a deterministic document repair engine.

Rules: - Never invent text. - Never summarize. - Never remove text. -
Never merge unrelated paragraphs. - Never reorder sections unless
required. - Preserve every original word.

Allowed operations: - MOVE_NODE - CHANGE_HEADING_LEVEL - FIX_TABLE -
NORMALIZE_NUMBERING - ADD_REFERENCE_METADATA - NO_CHANGE

Return JSON only.

### Output

``` json
{
  "operations":[
    {
      "operation":"MOVE_NODE",
      "node_id":"...",
      "new_parent":"..."
    }
  ]
}
```

## Engineering Guidelines

-   Implement each validator as an independent plugin.
-   Never invoke the LLM for the entire document.
-   Only invoke the LLM for nodes marked `LLM_REVIEW`.
-   Persist:
    -   Original DocumentTree
    -   Validation Report
    -   Repair Operations
    -   Repaired DocumentTree
-   Every repair must be auditable and reversible.
