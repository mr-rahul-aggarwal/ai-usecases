# Raw Chunking Engine Specification

## 1. Purpose and Scope

The **Raw Chunking Engine** sits on top of the repaired `DocumentTree` produced by the parsing pipeline (BDA + tree builder + DSVE).

Its responsibilities:

- Convert a hierarchical `DocumentTree` into a deterministic set of **RawChunks**.
- Ensure each RawChunk is a **locally coherent, structurally aligned text segment** (section, paragraph group, list, or table group).
- Keep chunking **deterministic and stable** across runs and document versions.
- Preserve enough context (headings, references, table headers) so that downstream **ProcedureChunks** can be derived reliably.

The Raw Chunking Engine does **not** perform semantic rule extraction. It is purely a structural segmentation layer.

---

## 2. Inputs and Outputs

### 2.1 Input: DocumentTree

Input is a repaired `DocumentTree` (after DSVE), for a single policy document:

- `doc_id: str` — policy identifier (e.g., `"P1"`).
- `nodes: Dict[str, DocumentNode]` — all nodes.
- `root_ids: List[str]` — top-level sections.

Each `DocumentNode` (already defined in your parsing spec) has at least:

- `id: str`
- `type: "Document" | "Section" | "Paragraph" | "List" | "ListItem" | "Table" | "TableRow" | "TableCell"`
- `parent_id: Optional[str]`
- `children: List[str]`
- `page_number: Optional[int]`
- `section_path: Optional[str`   # e.g. `"4 > 4.2"` or `"Section 4.2"`
- `heading: Optional[str]`
- `level: Optional[int`          # heading level (1,2,3,...)
- `text: str`
- `markdown: Optional[str]`
- `bbox: Optional[Tuple[float,float,float,float]]`
- `source_pdf: str`
- `sequence_number: int`
- `metadata: Dict[str, Any]`      # may include references, exception targets, table IDs, etc.

Assumptions:

- DSVE has already corrected obvious hierarchy errors and populated:
  - `metadata["references"]` for cross-policy/section references.
  - `metadata["exception_target_section_id"]` where applicable.
  - Flags for global constraint sections (e.g., general provisions).

### 2.2 Output: RawChunks

Output is a list `List[RawChunk]` for the document.

A **RawChunk** is a deterministic structural segment with traceability to the `DocumentTree`.

```python
@dataclass
class RawChunk:
    raw_chunk_id: str
    doc_id: str
    chunk_type: str          # "section", "paragraph_group", "list", "table", "table_row_group"
    section_path: str        # logical path, e.g. "4 > 4.2"
    title_context: str       # e.g. "4.2 Utility Bill Requirements"
    origin_node_ids: List[str]
    content_markdown: str    # heading + text + tables/lists in markdown
    page_range: Tuple[int, int]
    token_count: int
    detected_cross_references: List[str]  # e.g. ["P1.S9.1", "P1.APP.A"]
    metadata: Dict[str, Any] # e.g. {"table_ids": [...], "is_global_constraint": bool}
```

Constraints:

- RawChunks must be **deterministic**: same `DocumentTree` → identical sequence of chunks and IDs.
- RawChunks must not split inside:
  - a single paragraph,
  - a single list item,
  - a single table row.
- RawChunks must not merge content across distinct sections (different `section_path` at the heading level).

---

## 3. Design Principles

The Raw Chunking Engine should embody the following principles:

1. **Hierarchy-guided segmentation**  
   Use `Section` nodes and their heading levels as primary anchors. Chunk boundaries should align with subsection headings (e.g., level 3/4) rather than arbitrary token windows.

2. **Local semantic coherence via structural grouping**  
   Group contiguous paragraphs, lists, and tables under the same subsection into coherent bundles ("paragraph groups", "list groups", "table groups"). Do not cut mid-sentence or mid-paragraph.

3. **Token-aware refinement (bounded structural aggregation)**  
   Apply simple max/min token thresholds to split oversized bundles and merge undersized ones, always at safe node boundaries. Avoid LLM-based decisions here; this layer is purely programmatic.

4. **Explicit handling of tables and lists**  
   Tables and lists often encode rule sets. Treat them as dedicated chunk types, preserving headers and captions. For large tables, allow per-row or per-row-group chunks.

5. **Dependency tagging, not merging**  
   For cross-section references and global constraints (e.g., general provisions, amendments), attach dependency metadata (`detected_cross_references`, `is_global_constraint`) to chunks instead of merging distant sections into one chunk. ProcedureChunks will use these dependencies to assemble multi-chunk contexts.

6. **Stable, meaningful IDs**  
   Derive `raw_chunk_id` from `doc_id`, `section_path`, and a local index (e.g., `"P1.S4.2.C1"`, `"P1.S4.2.C2"`). This makes debugging and diffing across versions straightforward.

---

## 4. Chunk Types

Define the following chunk types:

- `"section"` — coarse chunk representing an entire section or major subsection (optional, useful for RAG).
- `"paragraph_group"` — primary chunk type representing one or more closely related paragraphs and list items under a functional heading.
- `"list"` — chunk for a list (bullet/numbered) that acts as a unit (e.g., required documents).
- `"table"` — chunk for a whole table (caption + headers + all rows).
- `"table_row_group"` — chunk for one row or a logical group of rows within a table.

You can start with `paragraph_group`, `list`, `table`, and add `section`/`table_row_group` as needed.

---

## 5. Functional Headings and Bundles

### 5.1 Functional heading levels

Define a set of levels that correspond to **functional subsections** (i.e., where actual rules/procedures are described), e.g.:

```python
FUNCTIONAL_HEADING_LEVELS = {3, 4}
```

Rationale:

- Level 1: document title or chapter.  
- Level 2: major sections ("Customer Onboarding", "Document Requirements").  
- Level 3/4: detailed subsections ("4.2 Utility Bill Requirements") which typically contain concrete rules and procedures.

### 5.2 Building bundles under functional parents

For each `Section` node `H` in `DocumentTree` with `H.level in FUNCTIONAL_HEADING_LEVELS`:

1. Collect all descendant nodes in **reading order** until the next `Section` node with `level <= H.level`:
   - `Paragraph`
   - `List` and `ListItem`
   - `Table` (and its `TableRow`/`TableCell`s)

2. This collection forms a **bundle**:

```python
bundle_nodes: List[DocumentNode] = [H] + children_of_H_until_next_section
```

3. This bundle is the starting point for one or more RawChunks; later we will apply token limits to split/merge.

Bundles preserve logical boundaries: they never cross into another top-level functional section.

---

## 6. Token Limits and Grouping

### 6.1 Configuration

In a config module (e.g., `chunking/config.py`), define:

```python
MAX_TOKENS_PER_CHUNK = 800      # upper limit
MIN_TOKENS_PER_CHUNK = 80       # lower limit
TARGET_TOKENS_PER_CHUNK = 400   # optional target for splitting
```

Use your chosen tokenizer (e.g., OpenAI, Anthropic, or a local BPE) to count tokens in `content_markdown`.

### 6.2 Generating content_markdown for a bundle

For each bundle:

1. Build markdown in reading order:
   - Emit heading `H` as `###` or `####` depending on level.
   - Append `Paragraph.text` with blank lines between paragraphs.
   - Emit lists in markdown (`- item` or `1. item`).
   - Insert tables using stored markdown (`Table.markdown`) or reconstruct from `TableRow`/`TableCell`.

2. Store this in a temporary `bundle_markdown` and compute `token_count`.

### 6.3 Splitting oversized bundles

If `token_count > MAX_TOKENS_PER_CHUNK`:

1. Iterate through children of `H` in order and build segments:

```python
segments = []
current_segment_nodes = [H]
current_tokens = tokens_for_heading(H)

for child in children_of_H:
    child_tokens = tokens_for_node(child)
    if current_tokens + child_tokens > MAX_TOKENS_PER_CHUNK and len(current_segment_nodes) > 1:
        segments.append(current_segment_nodes)
        current_segment_nodes = [H, child]
        current_tokens = tokens_for_heading(H) + child_tokens
    else:
        current_segment_nodes.append(child)
        current_tokens += child_tokens

if len(current_segment_nodes) > 1:
    segments.append(current_segment_nodes)
```

2. For each `segment_nodes`, build a separate `RawChunk` (paragraph_group or list/table chunk). Each segment includes the heading `H` plus a subset of content nodes, preserving context.

3. Compute `content_markdown`, `token_count`, and `page_range` per segment.

### 6.4 Merging undersized bundles/segments

If `token_count < MIN_TOKENS_PER_CHUNK` for a segment:

1. Attempt to merge with an adjacent segment from the **same functional heading**:

   - Merge with previous segment if `previous_segment_tokens + token_count <= MAX_TOKENS_PER_CHUNK`.
   - Else merge with next segment if possible.

2. If merging is impossible without exceeding `MAX_TOKENS_PER_CHUNK`, keep the small chunk but mark:

```python
metadata["too_small"] = True
```

This way, small chunks are rare and explicitly tagged.

---

## 7. Handling Tables

Tables often encode rules row-by-row. Handle them explicitly.

### 7.1 Whole-table chunks

For a `Table` node `T` under functional heading `H`:

- If `T` has a modest number of rows (e.g., ≤ 10) and total tokens within limits:
  - Create a single `RawChunk`:
    - `chunk_type = "table"`
    - `origin_node_ids` include `T` and all its rows/cells.
    - `content_markdown` includes table caption, headers, and rows.
    - `metadata["table_ids"] = [T.id]`

### 7.2 Table-row group chunks

If the table is large or each row is clearly a separate rule:

- Create a parent table chunk (caption + headers) of type `"table"`.
- For each row or logical group of rows:

```python
RawChunk(
    raw_chunk_id = f"{doc_id}.{section_path}.T{t_index}.RG{row_index}",
    chunk_type = "table_row_group",
    origin_node_ids = [T.id, row.id, ...],
    content_markdown = markdown_for_single_row_with_headers,
    ...
)
```

Token limits are unlikely to be a problem here; each row chunk is typically small.

### 7.3 Linking with text

If `T` has an introductory paragraph or heading:

- Either include that text in the table chunk’s `content_markdown`.  
- Or leave it in a neighboring paragraph_group chunk but be sure to record `table_ids` / `origin_node_ids` for traceability.

---

## 8. Handling Lists

Lists (bullets/numbered) encode checklists or enumerations.

For a `List` node under functional heading `H`:

1. If list items jointly describe a single concept (e.g., "Documents required: A, B, C"):

   - Emit one `RawChunk` of type `"list"` with all `ListItem` children.

2. If each item is a separate rule (e.g., "Rule 1", "Rule 2", ...):

   - Emit one RawChunk per `ListItem` or per small groups (similar to table row chunks), each with:
     - `content_markdown` containing only that item plus heading context.

Token limits still apply; do not split inside a `ListItem`.

---

## 9. Dependency Tagging (Cross-References and Global Sections)

The Raw Chunking Engine must **tag**, not resolve, dependencies.

### 9.1 Cross-references within a chunk

For each RawChunk:

1. Initialize `detected_cross_references = []`.
2. For each `origin_node_id`, inspect its `DocumentNode.metadata["references"]` (populated by DSVE):
   - Append referenced section IDs or policy IDs (e.g., `"P1.S9.1"`).

Store the union in `detected_cross_references`.

### 9.2 Global constraint sections

For sections like "General Provisions" or "Amendments", DSVE may mark:

```python
node.metadata["is_global_constraint"] = True
```

When chunking:

- Mark any chunk derived from such sections as:

```python
metadata["is_global_constraint"] = True
```

This allows the ProcedureChunk layer to:

- Include global constraint chunks as additional context for rule generation.  
- Track lineage via `source_raw_chunk_ids` and `dependent_raw_chunks`.

---

## 10. RawChunk ID Scheme

Define a deterministic ID scheme in `chunking/id_utils.py`:

```python
def make_raw_chunk_id(doc_id: str, section_path: str, local_index: int) -> str:
    # Normalize section_path, e.g., "4 > 4.2" -> "S4.2"
    normalized = normalize_section_path(section_path)
    return f"{doc_id}.{normalized}.C{local_index}"
```

Rules:

- `normalized` should contain only alphanumerics and dots (e.g., `"S4.2"`).
- `local_index` increments in reading order per section.

Examples:

- First paragraph_group chunk under Section 4.2: `P1.S4.2.C1`.  
- Second chunk under the same section: `P1.S4.2.C2`.  
- First table_row_group chunk under Section 4.2: `P1.S4.2.T1.RG1` (you can use an extended scheme for tables).

IDs must be stable across runs.

---

## 11. Module Layout

Create a `chunking/` package:

```text
chunking/
  config.py          # token limits, functional heading levels
  models.py          # RawChunk dataclass
  id_utils.py        # ID generation helpers
  tokenizer.py       # wrapper around chosen tokenizer
  builder.py         # main Raw Chunking Engine implementation
  utils.py           # misc helpers (markdown generation, etc.)
```

### 11.1 models.py

Define `RawChunk` dataclass as above.

### 11.2 config.py

Define constants:

```python
FUNCTIONAL_HEADING_LEVELS = {3, 4}
MAX_TOKENS_PER_CHUNK = 800
MIN_TOKENS_PER_CHUNK = 80
TARGET_TOKENS_PER_CHUNK = 400
```

Allow overrides via environment variables or a settings object.

### 11.3 tokenizer.py

Implement:

```python
def count_tokens(text: str) -> int:
    """Return token count using a chosen tokenizer."""
    ...

def tokens_for_node(node: DocumentNode) -> int:
    return count_tokens(node.text or node.markdown or "")
```

### 11.4 builder.py

Implement the main entry point:

```python
from parsing.models import DocumentTree, DocumentNode
from chunking.models import RawChunk

def build_raw_chunks(tree: DocumentTree) -> List[RawChunk]:
    """Convert a repaired DocumentTree into deterministic RawChunks."""
    ...
```

High-level pseudocode:

```python
raw_chunks = []

# 1. Identify functional headings
functional_sections = [
    node for node in tree.nodes.values()
    if node.type == "Section" and node.level in FUNCTIONAL_HEADING_LEVELS
]

for H in functional_sections:
    # 2. Collect bundle nodes under H
    bundle_nodes = collect_bundle_nodes(tree, H)

    # 3. Split bundle into segments based on token limits
    segments = split_bundle_into_segments(H, bundle_nodes)

    # 4. For each segment, build a RawChunk
    for index, segment_nodes in enumerate(segments, start=1):
        chunk_id = make_raw_chunk_id(tree.doc_id, H.section_path, index)
        content_md = render_segment_markdown(H, segment_nodes)
        tokens = count_tokens(content_md)
        pages = (min_page(segment_nodes), max_page(segment_nodes))

        detected_refs = collect_detected_references(segment_nodes)
        meta = collect_chunk_metadata(H, segment_nodes)

        raw_chunks.append(RawChunk(
            raw_chunk_id = chunk_id,
            doc_id = tree.doc_id,
            chunk_type = infer_chunk_type(segment_nodes),
            section_path = H.section_path,
            title_context = H.heading or "",
            origin_node_ids = [n.id for n in segment_nodes],
            content_markdown = content_md,
            page_range = pages,
            token_count = tokens,
            detected_cross_references = detected_refs,
            metadata = meta,
        ))

# 5. Sort raw_chunks by section_path + sequence if needed
return raw_chunks
```

Implement helpers:

- `collect_bundle_nodes(tree, H)` — DFS from `H` until next Section of level <= `H.level`.
- `split_bundle_into_segments(H, bundle_nodes)` — apply token-based splitting/merging.
- `render_segment_markdown(H, segment_nodes)` — convert nodes to markdown.
- `min_page` / `max_page` — derive page range from nodes.
- `collect_detected_references` — read `metadata["references"]` from nodes.
- `collect_chunk_metadata` — capture `table_ids`, `is_global_constraint`, etc.
- `infer_chunk_type` — decide between `paragraph_group`, `list`, `table`, `table_row_group` based on node types.

---

## 12. Testing and Evaluation

### 12.1 Determinism tests

For a given `DocumentTree`:

- Run `build_raw_chunks(tree)` twice; assert:
  - Same number of chunks.  
  - Same `raw_chunk_id` set.  
  - Same `origin_node_ids` per chunk.

- Change an unrelated part of the document (e.g., add an extra space); verify unaffected chunks remain identical.

### 12.2 Structural sanity tests

Automatically flag:

- Chunks whose `content_markdown` starts or ends mid-sentence (can be detected via simple sentence boundary heuristics).
- Chunks with `token_count < MIN_TOKENS_PER_CHUNK` (and review merging heuristics).

### 12.3 Procedure-layer integration tests

Once ProcedureChunk extraction is built:

- Verify that ProcedureChunks refer back to valid `raw_chunk_id`s.  
- Ensure cross-dependencies (e.g., global constraints) are correctly captured via `detected_cross_references`.

This Raw Chunking Engine gives you a **stable structural substrate** on which you can build more sophisticated ProcedureChunks and execution logic, without re-fighting segmentation and layout issues at every step.