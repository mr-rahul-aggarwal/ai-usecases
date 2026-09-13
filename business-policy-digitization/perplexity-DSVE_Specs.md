# Document Semantic Validation Engine (DSVE) Specification

## 1. Purpose and Scope

The **Document Semantic Validation Engine (DSVE)** sits on top of the parsed `DocumentTree` built from BDA (Amazon Bedrock Data Automation) output and your tree builder.

Its responsibilities:

- Detect **structural and semantic gaps** in the `DocumentTree` (hierarchy mistakes, mis-scoped content, broken tables, bad references).
- Optionally use an **LLM validation + repair layer** to propose corrections.
- Apply those corrections in a controlled way, producing a **repaired `DocumentTree`** plus a **validation report** and **change log**.

DSVE does **not** re-parse PDFs or call BDA. It operates purely on:

- BDA standard output (JSON + markdown + CSV).
- The initial `DocumentTree` you already construct from that output.

This spec covers:

1. Gaps DSVE should detect.  
2. Pure-programmatic validation logic.  
3. LLM validation prompts.  
4. LLM repair prompts and application rules.  
5. Module structure and data contracts.

---

## 2. Inputs and Outputs

### 2.1 Inputs

- `DocumentTree` (canonical parsed representation):
  - Nodes: `Document`, `Section`, `Paragraph`, `List`, `ListItem`, `Table`, `TableRow`, `TableCell`.
  - Fields: `id`, `type`, `parent_id`, `children`, `page_number`, `section_path`, `heading`, `level`, `text`, `markdown`, `bbox`, `source_pdf`, `sequence_number`, `metadata`.

- Optional: raw BDA outputs (for debugging only—not required for DSVE core):
  - BDA JSON + markdown + CSV.

### 2.2 Outputs

DSVE must produce:

1. `validation_report.json`  
   - Detected issues categorized by severity.

2. `repaired_document_tree.json`  
   - Updated `DocumentTree` after applying allowed repairs.

3. `change_log.json`  
   - Audit log of modifications made by the LLM repair layer.

---

## 3. High-Level Architecture

Recommended modules:

```text
dsve/
  models.py           # DSVE-specific issue and change models
  rules.py            # rule-based validators (non-LLM)
  detectors.py        # higher-level semantic detectors (non-LLM)
  llm_validation.py   # LLM validation prompts & parsing
  llm_repair.py       # LLM repair prompts & tree update logic
  engine.py           # orchestration (run DSVE end-to-end)
```

DSVE flow:

1. Run **rule-based validation** (fast, deterministic).  
2. Run **semantic detectors** to identify suspicious areas.  
3. For selected areas, call **LLM validation** to get structured assessments.  
4. For confirmed issues, call **LLM repair** with strict prompts.  
5. Apply repairs to `DocumentTree`, log changes, and output the three artifacts.

---

## 4. Issues DSVE Should Detect

DSVE’s job is to detect **specific patterns of structural/semantic problems** that will break rule extraction or chunking.

### 4.1 Hierarchy / heading issues

1. **Heading level anomalies**
   - Example: sequence of section levels like `1 → 3 → 2` or `1 → 4` with no `2` or `3` between.
   - Example: many consecutive `Section` nodes with level 1 on the same page where the document clearly uses nested sections.

2. **Empty or degenerate sections**
   - `Section` node with children only of type `Section` and no `Paragraph`, `ListItem`, or `Table`.
   - Section that contains only one short paragraph that looks like a heading (uppercase, ending with colon) and no actual content.

3. **Unattached or misattached content**
   - `Paragraph` or `ListItem` nodes whose `parent_id` is the root `Document`, but visually sit under a header (based on `page_number`/`bbox` proximity).
   - Paragraphs that belong logically to a subsection but are attached to the parent section.

4. **Heading-like text not marked as Section**
   - Node with `type == Paragraph` but text:
     - Short (<= 100 chars).
     - High proportion of capitalized words.
     - Ends with colon or has numbering like `1.1`.
   - These are likely misclassified headings.

### 4.2 Table issues

5. **Tables without header context**
   - `Table` node with parent `Document` instead of a `Section`.
   - Tables immediately following a section heading but attached to an older section.

6. **Tables without rows or malformed row structure**
   - `Table` with zero `TableRow` children.
   - `TableRow` with inconsistent number of `TableCell` children compared to header row.

7. **Tables whose markdown is malformed**
   - `Table.markdown` exists but:
     - Row lines have different counts of `|` separators.
     - Missing header separator line (`---`).

### 4.3 Reading order / sequence issues

8. **Non-monotonic sequence numbers**
   - `sequence_number` not strictly increasing.

9. **Page-number jumps or regressions**
   - A node appears to go backwards in page order where not expected (may indicate mis-grouping).

### 4.4 Reference and scope issues

10. **Orphan references**
    - Paragraph with text containing patterns like `Policy P-XXX`, `Section 4.2` but `metadata["references"]` missing or incomplete.

11. **Scope misalignment for exceptions**
    - Paragraph starting with patterns like `"Exception:"`, `"However,"`, `"Notwithstanding,"` attached to the wrong parent section (e.g., outside the section whose rule it qualifies).

---

## 5. Rule-Based Validation Logic (rules.py)

Implement rule-based checks that do **not** require LLMs.

### 5.1 Models

In `dsve/models.py`, define:

```python
@dataclass
class ValidationIssue:
    issue_id: str
    code: str         # e.g., "HEADING_LEVEL_JUMP", "EMPTY_SECTION"
    severity: str     # "error" | "warning"
    node_id: Optional[str]
    message: str
    details: Dict[str, Any]

@dataclass
class ValidationReport:
    issues: List[ValidationIssue]
```

### 5.2 Rule implementations

In `dsve/rules.py`, implement functions like:

```python
def check_heading_levels(tree: DocumentTree) -> List[ValidationIssue]:
    ...

def check_empty_sections(tree: DocumentTree) -> List[ValidationIssue]:
    ...

def check_parent_child_consistency(tree: DocumentTree) -> List[ValidationIssue]:
    ...

def check_tables_structure(tree: DocumentTree) -> List[ValidationIssue]:
    ...

def check_sequence_and_pages(tree: DocumentTree) -> List[ValidationIssue]:
    ...
```

Each function:

- Iterates relevant nodes.  
- Uses simple deterministic rules (as in Section 4).  
- Returns `ValidationIssue` objects.

`engine.run_rules(tree)` should aggregate these into a `ValidationReport`.

---

## 6. Semantic Detectors (detectors.py)

These are still non-LLM heuristics but higher-level.

### 6.1 Heading-like paragraphs

Implement:

```python
def detect_heading_like_paragraphs(tree: DocumentTree) -> List[str]:
    """Return node_ids of Paragraph nodes that look like headings."""
    ...
```

Logic:

- For each Paragraph node:
  - Compute features: length, proportion of uppercase words, presence of digits+dot (`"1.2"`), trailing colon.
  - Flag nodes above a threshold.

### 6.2 Exception paragraphs

Implement:

```python
def detect_exception_paragraphs(tree: DocumentTree) -> List[str]:
    """Return node_ids of Paragraphs that likely describe exceptions/overrides."""
    ...
```

Logic:

- Look for prefixes: `"Exception:"`, `"Exceptions:"`, `"However,"`, `"Notwithstanding"`, `"Despite"`.
- Flag paragraphs whose text starts with these.

### 6.3 Orphan references

Implement:

```python
def detect_orphan_references(tree: DocumentTree) -> List[str]:
    """Return node_ids with reference-like text but no metadata["references"]."""
    ...
```

Logic:

- Regex search for `Policy\s+[A-Z0-9-]+` and `Section\s+[0-9.]+` in `text`.
- Check `metadata.get("references")`.
- Flag missing references.

These detectors feed into the LLM validation/repair layer by providing **candidate node sets**.

---

## 7. LLM Validation (llm_validation.py)

LLM validation should be **read-only**: it inspects slices of the tree and returns structured assessments about:

- Heading classification and levels.
- Section boundaries and parent-child relationships.
- Table-parent linkage.
- Scope of exceptions.
- References (policy IDs, section IDs).

### 7.1 LLM client abstraction

Implement a generic client:

```python
def call_llm(system_prompt: str, user_content: str) -> str:
    """Send content to Claude/GPT via org-approved API and return raw text response."""
    ...
```

Codex should wire this to Anthropic or OpenAI SDK.

### 7.2 Prompts for heading validation

Function:

```python
def validate_heading_sequence(nodes_slice: List[DocumentNode]) -> Dict[str, Any]:
    ...
```

Construct a user content string that shows a local sequence of nodes (headers + paragraphs), e.g.:

```text
You are validating the hierarchy of a policy document.
Here is a sequence of nodes with their current types and levels:

1. id=P1.S1, type=Section, level=1, text="General Provisions"
2. id=P1.N2, type=Paragraph, level=None, text="Scope"
3. id=P1.S1.1, type=Section, level=3, text="Password Requirements"
4. id=P1.P3, type=Paragraph, level=None, text="Users must..."

Task:
For each line, decide:
- is_heading: true/false
- corrected_level: integer level (1,2,3,...) or null if not a heading
- parent_id: id of the node that should be its parent (or "DOC_ROOT" for top-level sections)

Return a JSON array, one object per line, exactly in this format:
[
  {"node_id": "P1.S1", "is_heading": true, "corrected_level": 1, "parent_id": "DOC_ROOT"},
  {"node_id": "P1.N2", "is_heading": true, "corrected_level": 2, "parent_id": "P1.S1"},
  ...
]
Do not include any explanation text.
```

Use this pattern whenever you call the LLM for heading/section validation:

- System prompt: constrain role and JSON-only output.  
- User content: local sequence with node IDs + current types.

### 7.3 Prompts for table-parent validation

Function:

```python
def validate_table_parent(section_context: List[DocumentNode], table_node: DocumentNode) -> Dict[str, Any]:
    ...
```

Prompt template:

```text
You are validating table placement in a policy document.
Here are nearby section headings and paragraphs:

[LIST OF SECTIONS/PARAGRAPHS WITH id, type, level, text]

Here is the table caption and first row:

Table id=P1.T3
Caption="Password Rules by Role"
First row="Admin | 16 chars | 30 days"

Question:
Which section should this table belong to?
Return JSON with:
{"table_id": "P1.T3", "parent_section_id": "<id-of-section>"}

If you cannot decide, set parent_section_id to null.
No explanations.
```

### 7.4 Prompts for exception scope

Function:

```python
def validate_exception_scope(exception_node: DocumentNode, local_context: List[DocumentNode]) -> Dict[str, Any]:
    ...
```

Prompt template:

```text
You are validating exception scoping in a policy document.
Here is the exception paragraph:

id=P1.P45
text="Exception: Customers with government-issued IDs may skip address verification."

Here are nearby sections and rules:

[LIST OF NEARBY SECTIONS/PARAGRAPHS]

Question:
Which section's rules does this exception most likely modify?
Return JSON:
{"exception_node_id": "P1.P45", "target_section_id": "<section-id>"}

If you cannot decide, set target_section_id to null.
No explanations.
```

### 7.5 Prompts for reference extraction

Function:

```python
def extract_references_with_llm(node: DocumentNode) -> Dict[str, Any]:
    ...
```

Prompt template:

```text
Extract policy and section references from the following text.
Return JSON in this exact format:
{"references": [{"target_policy": "...", "target_section": "..."}, ...]}
If none, return {"references": []}.

Text:
"Refer Policy P-102 Section 4.2 for exceptions."
```

LLM responses from these functions are **inputs to repair**, not direct tree mutations.

---

## 8. LLM Repair (llm_repair.py)

LLM repair is allowed to **modify the `DocumentTree`** based on validation outputs.

Implement:

```python
def apply_repairs(
    tree: DocumentTree,
    validation_report: ValidationReport,
    llm_findings: Dict[str, Any]
) -> Tuple[DocumentTree, List[Dict[str, Any]]]:
    """Apply LLM-suggested repairs and return new tree + change_log."""
    ...
```

### 8.1 Repair rules

Repairs should be **limited and auditable**:

1. **Heading promotion/demotion**
   - Use LLM output from `validate_heading_sequence` to:
     - Convert heading-like Paragraphs to `Section` nodes.
     - Adjust `level` on existing Section nodes.
     - Reassign `parent_id` (and update `children` lists) according to `parent_id` in the JSON.
   - Record each change in `change_log`:

```json
{
  "change_type": "HEADING_RECLASSIFICATION",
  "node_id": "P1.N2",
  "old_type": "Paragraph",
  "new_type": "Section",
  "old_level": null,
  "new_level": 2,
  "old_parent_id": "P1.S1",
  "new_parent_id": "P1.S1"
}
```

2. **Section boundary adjustment**
   - If LLM suggests that a block of nodes belongs under a different parent section:
     - Move those nodes in the tree: update `parent_id` and corresponding `children` lists.
   - Record each move as `change_type="SECTION_REPARENT"`.

3. **Table-parent assignment**
   - If `validate_table_parent` returns a non-null `parent_section_id`:
     - Set `Table.parent_id` to the suggested section.  
     - Remove from old parent’s children, add to new parent’s children.
   - `change_type="TABLE_REPARENT"`.

4. **Exception scoping**
   - If `validate_exception_scope` returns a section id:
     - Add metadata to the exception node: `metadata["exception_target_section_id"]`.
   - Optionally reparent the exception node to that section if it’s currently under root or a generic container.

5. **Reference metadata enrichment**
   - Use output from `extract_references_with_llm` to populate `metadata["references"]` for nodes flagged by detectors.
   - This does not change hierarchy; only metadata.

6. **Table markdown repair**
   - If DSVE rules flagged malformed markdown on a Table:
     - Call LLM with a table-repair prompt and replace `node.markdown` with the cleaned markdown.
     - Optionally re-derive `TableRow`/`TableCell.text` from the cleaned markdown.
   - Log as `change_type="TABLE_MARKDOWN_REPAIR"`.

### 8.2 Safety constraints

Codex must enforce:

- Only apply repairs where:
  - There is a **matching LLM suggestion** AND
  - The affected node appears in `validation_report` or `detectors` output.
- Never delete nodes; only reclassify or reparent.
- Never overwrite `source_pdf` or `bbox` fields.

---

## 9. DSVE Orchestration (engine.py)

Implement:

```python
def run_dsve(tree: DocumentTree) -> Tuple[DocumentTree, ValidationReport, List[Dict[str, Any]]]:
    """Run full DSVE: rules, detectors, LLM validation, LLM repair."""
    ...
```

High-level steps:

1. Run rule-based validators:

```python
issues = []
issues += check_heading_levels(tree)
issues += check_empty_sections(tree)
issues += check_parent_child_consistency(tree)
issues += check_tables_structure(tree)
issues += check_sequence_and_pages(tree)
validation_report = ValidationReport(issues=issues)
```

2. Run detectors to find candidate nodes for LLM:

```python
heading_like_ids = detect_heading_like_paragraphs(tree)
exception_ids = detect_exception_paragraphs(tree)
orphan_ref_ids = detect_orphan_references(tree)
```

3. For each candidate region/node, construct local slices and call LLM validation functions, collecting `llm_findings`.

4. Apply repairs:

```python
repaired_tree, change_log = apply_repairs(tree, validation_report, llm_findings)
```

5. Return `repaired_tree`, `validation_report`, `change_log`.

Use this engine in the overall pipeline:

- After BDA parsing and initial tree building.  
- Before rule chunking and procedure extraction.

---

## 10. Implementation Guidance

Ask your coding assistant to:

1. Implement DSVE in an **incremental** way:
   - Milestone 1: rule-based validators + `validation_report.json`.
   - Milestone 2: detectors (heading-like, exceptions, orphan refs).
   - Milestone 3: LLM validation functions with JSON-only prompts; no repair yet.
   - Milestone 4: LLM repair logic + `change_log.json` and `repaired_document_tree.json`.

2. Write unit tests on a small set of real policy PDFs:
   - Cases where headings were misclassified.  
   - Tables attached to wrong sections.  
   - Exception paragraphs misplaced.

3. Ensure all LLM calls:
   - Use strict system prompts.  
   - Return **valid JSON only** (no natural language explanations).  
   - Are isolated in `llm_validation.py` and `llm_repair.py`.

The DSVE layer will give you a structurally and semantically sound `DocumentTree`, which you can then safely use for rule chunking and AI agent execution.