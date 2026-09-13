# Engineering Specification: Document Semantic Validation Engine (DSVE)

## 1. Architectural Overview
**Position in Pipeline:** The DSVE sits *between* the raw `DocumentTree` construction (from AWS BDA output) and the final *Logical Block Chunking* stage. 
**Objective:** To detect and automatically repair structural and semantic breaks in the JSON tree (e.g., hallucinated headings, detached exception paragraphs, broken tables) ensuring perfectly cohesive chunks for the AI Agent rule-extraction layer.

The DSVE operates in two phases:
1. **Detection Phase:** Scans the tree using deterministic Python logic and targeted LLM checks to generate a `ValidationReport`.
2. **Repair Phase:** Consumes the report and applies specific LLM surgical prompts to mutate and fix the `DocumentTree`.

---

## 2. Phase 1: Gap Detection Logic (What DSVE Looks For)

Implement a `DSVEDetector` Python class that traverses the `DocumentTree` and flags anomalies.

### A. Deterministic Checks (Python Logic)
*Codex Instruction: Implement these as pure Python tree-traversal functions.*

1. **Hierarchy Jumps:** Flag any node where the heading level jumps skips a logical step (e.g., Parent is `H1`, immediate child heading is `H3`).
2. **Orphaned Exceptions/Notes:** Flag any text node starting with "Note:", "Exception:", "Warning:", or "If" that is currently mapped as a top-level `H1` or `H2` instead of a child paragraph.
3. **Monotonic Sequence Breaks:** Flag lists or numbered sections that break sequence (e.g., `1.1`, `1.2`, `1.4`).
4. **Table Header Mismatches:** Flag `table` nodes that lack preceding descriptive text (usually indicating a table was structurally separated from its introductory paragraph).

### B. Semantic Checks (LLM-Assisted)
*Codex Instruction: Implement an async function that groups suspect nodes and passes them to the LLM using the prompt below.*

**Target:** The Document Skeleton (Table of Contents).
**Objective:** Detect if BDA misinterpreted a bold sentence as a structural heading.
**Prompt to LLM (Skeleton Validator):**
> "You are a Document Hierarchy Validator. Review this JSON array of extracted document headings: `{skeleton_json}`. 
> Your task is to detect semantic gaps and false headings. A valid heading represents a structural section of a policy (e.g., '1.0 Overview', 'Security Protocol'). A false heading is a conversational sentence, a warning label, or a table row that was incorrectly formatted as a heading.
> 
> Return a JSON array mapping each `node_id` to a validation object containing:
> - `is_valid_heading`: boolean
> - `confidence`: float
> - `reasoning`: string detailing why it is or isn't a true section divider."

---

## 3. Phase 2: Tree Repair Engine (How DSVE Fixes the Gaps)

Implement a `DSVERepairEngine` Python class. This class takes the `DocumentTree` and the `ValidationReport` and executes repairs.

### A. Repairing False Headings (Skeleton Reconciliation)
*Codex Instruction: If a heading is flagged as `is_valid_heading: false` by the detector, execute this logic.*

1. **Logic:** Change the node's type from `"header"` to `"paragraph"`.
2. **Tree Re-linking:** Reassign all children of this false heading to its *parent* heading. (e.g., If the false heading was an H3 under an H2, make all the false heading's text and children part of the H2's standard body).

### B. Repairing Detached Context & Conditional Logic
*Codex Instruction: If a paragraph is flagged as an "Orphaned Exception" (e.g., a rule exception separated from the main rule), use this prompt to repair it.*

**Prompt to LLM (Context Re-aligner):**
> "You are a Semantic Tree Repair Engine. The following paragraph (Node A) appears to be an exception or condition: `{orphan_text}`.
> It currently has no logical parent. Here are the three preceding paragraphs in the document (Nodes X, Y, Z): `{preceding_nodes_json}`.
> 
> Determine which preceding paragraph is the primary base rule that this exception applies to. Return a JSON object with:
> - `target_parent_node_id`: The ID of the paragraph this exception belongs to.
> - `relationship_type`: 'exception', 'clarification', or 'extension'.
> 
> If it does not belong to any, return `null`."
**Execution:** Update the `parent_id` of the orphan node to the LLM's identified target, ensuring they are chunked together later.

### C. Repairing Table Context Gaps
*Codex Instruction: If a table is flagged as lacking context, execute this prompt.*

**Prompt to LLM (Table Context Repair):**
> "You are a Data Context Engine. Analyze this markdown table: `{table_markdown}`.
> Here is the text immediately preceding the table in the document tree: `{preceding_text}`.
> 
> Does the preceding text serve as the instructional context or introduction for how to interpret this table?
> Return a JSON object containing:
> - `is_related`: boolean
> - `inferred_table_title`: string (Generate a concise title based on the context).
> - `rule_dependency`: boolean (Does understanding the preceding text require reading this table?)"
**Execution:** If `rule_dependency` is true, merge the `table` node and the preceding `paragraph` node into a single composite Node in the tree, ensuring they are never separated during chunking.

---

## 4. Required Data Schemas (`models.py` updates)

Add these Pydantic/Dataclass models to ensure Codex types the DSVE correctly.

```python
from typing import List, Optional
from pydantic import BaseModel

class DSVEAnomaly(BaseModel):
    node_id: str
    anomaly_type: str # e.g., "FALSE_HEADING", "ORPHANED_EXCEPTION", "TABLE_CONTEXT_GAP"
    severity: str
    metadata: dict

class ValidationReport(BaseModel):
    doc_id: str
    anomalies: List[DSVEAnomaly]
    is_structurally_sound: bool

class RepairedNodeLog(BaseModel):
    node_id: str
    action_taken: str # e.g., "DOWNGRADED_TO_PARAGRAPH", "REPARENTED"
    previous_parent: Optional[str]
    new_parent: Optional[str]