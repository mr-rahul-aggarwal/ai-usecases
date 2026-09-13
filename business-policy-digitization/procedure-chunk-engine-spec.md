# Procedure Chunk Engine Specification

## 1. Purpose and Scope

The **Procedure Chunk Engine** sits between the Raw Chunking layer and the Procedure DAG Compiler. It converts deterministic, structure-aligned `RawChunk` objects into semantically rich, executable `ProcedureChunk`s and then forwards them to the DAG builder.

Responsibilities:

- Classify RawChunks into semantic categories (rule blocks, modifiers, tables, context).
- Build a global, deduplicated Policy Data Dictionary (variables) for each document.
- Extract structured, executable procedure logic from candidate RawChunks using LLMs constrained by the dictionary.
- Attach deterministic metadata (IDs, version, lineage, hashes) to each ProcedureChunk.
- Provide inputs to the Procedure DAG Compiler and Procedure Validation Engine (PVE).

The Procedure Chunk Engine does **not** perform:

- Structural parsing (that is DSVE + raw chunking).
- Full DAG construction (handled by the DAG Compiler).
- Deep semantic validation (handled by PVE and AI Reviewer).

---

## 2. Inputs and Outputs

### 2.1 Inputs

1. `doc_id: str` — Policy identifier (e.g., "P1").
2. `raw_chunks: List[RawChunk]` — Deterministic structural chunks produced by the Raw Chunking Engine.
3. LLM client — An org-approved LLM interface (e.g., Claude via Bedrock) supporting JSON outputs.

#### RawChunk model (from raw-chunking-spec)

```python
class RawChunkType(str, enum.Enum):
    SECTION_HEADER_ONLY = "section_header_only"
    PARAGRAPH_GROUP = "paragraph_group"
    LIST_BLOCK = "list_block"
    TABLE_BLOCK = "table_block"

class RawChunk(BaseModel):
    chunk_id: str
    doc_id: str
    chunk_type: RawChunkType
    section_path: str
    origin_node_ids: List[str]
    text_content: str
    page_range: Tuple[int, int]
    token_count: int
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

### 2.2 Outputs

1. `policy_data_dictionary: PolicyDataDictionary`
2. `procedure_chunks: List[ProcedureChunk]`

These outputs feed:

- Procedure DAG Compiler.
- Procedure Validation Engine (PVE).

#### PolicyDataDictionary

```python
class DataVariable(BaseModel):
    variable_name: str      # snake_case, e.g. "customer_age"
    data_type: str          # "string", "number", "boolean", "array"
    description: str        # semantic meaning

class PolicyDataDictionary(BaseModel):
    doc_id: str
    variables: List[DataVariable]
```

#### ProcedureChunk

```python
class ActionTaxonomy(str, enum.Enum):
    DOCUMENT_VERIFICATION = "document_verification"
    DATA_RETRIEVAL = "data_retrieval"
    LOGIC_EVALUATION = "logic_evaluation"
    CALCULATION = "calculation"
    SYSTEM_ACTION = "system_action"

class RuleStep(BaseModel):
    step_number: int
    expression: str        # e.g. "IF customer_age < 18 THEN FAIL"
    failure_message: str

class DependencyGate(BaseModel):
    and_prerequisites: List[str] = []   # procedure titles or IDs
    or_prerequisites: List[str] = []

class ProcedureChunk(BaseModel):
    procedure_id: str                  # "PROC_{doc_id}#_LN_0001" (Python-generated)
    doc_id: str
    execution_category: ActionTaxonomy
    title: str                         # short functional name
    required_inputs: List[str]         # variable names from PolicyDataDictionary
    outputs: List[str] = ["PASS", "FAIL", "FLAG"]
    logic_flow: List[RuleStep]
    dependencies: DependencyGate

    source_raw_chunk_ids: List[str]    # traceability
    origin_node_ids: List[str]
    version: str = "1.0.0"
    logic_hash: str                    # SHA-256 hash of logic_flow
```

---

## 3. Phase 1 — Triage & Classification

Goal: classify RawChunks into semantic buckets so we know which chunks are candidates for procedure extraction and which are support context.

### 3.1 Triage categories

```python
class TriageCategory(str, enum.Enum):
    PRIMARY_RULE_BLOCK = "primary_rule_block"        # core verification logic
    CONDITIONAL_MODIFIER = "conditional_modifier"    # exceptions, overrides, thresholds
    REFERENCE_TABLE = "reference_table"              # structured lookup tables/lists
    INFORMATIONAL_CONTEXT = "informational_context"  # introductions, legal boilerplate
```

### 3.2 Triage LLM prompt (prompts/triage_agent.txt)

Intent: classify each RawChunk into one of `TriageCategory`.

Key rules:

- `primary_rule_block`: contains explicit automated verification instructions or compliance gates ("user must submit passport", "account activation requires document checks").
- `conditional_modifier`: contains exceptions, overrides, country/age limits modifying primary rules.
- `reference_table`: structured tables or lists encoding accepted values, codes, or thresholds.
- `informational_context`: generic narrative, introductions, disclaimers, not directly executable.

Expected output:

```json
{
  "category": "primary_rule_block" | "conditional_modifier" | "reference_table" | "informational_context",
  "justification": "One sentence citing structural markers in the text."
}
```

### 3.3 Triage orchestration function

```python
def triage_raw_chunks(doc_id: str, raw_chunks: List[RawChunk], llm_client) -> Dict[TriageCategory, List[RawChunk]]:
    buckets = {cat: [] for cat in TriageCategory}

    for chunk in raw_chunks:
        # Skip empty headers
        if chunk.chunk_type == RawChunkType.SECTION_HEADER_ONLY:
            buckets[TriageCategory.INFORMATIONAL_CONTEXT].append(chunk)
            continue

        resp = llm_client.generate_json(
            system_prompt=load_prompt("triage_agent.txt"),
            user_content=f"Section: {chunk.section_path}\nContent:\n{chunk.text_content}"
        )

        category = TriageCategory(resp["category"])
        buckets[category].append(chunk)

    return buckets
```

Notes:

- Cache LLM classifications per `chunk_id` for reproducibility and cost savings.
- Triage is a precondition for dictionary generation and procedure extraction.

---

## 4. Phase 2 — Policy Data Dictionary Generation

Goal: define an immutable, deduplicated variable schema for each policy before extraction.

### 4.1 Dictionary LLM prompt (prompts/dictionary_generator.txt)

Intent:

- Given all `PRIMARY_RULE_BLOCK` + `CONDITIONAL_MODIFIER` chunks, identify runtime variables the system must inspect or compute.

Constraints:

- Use **snake_case** names (e.g., `submitted_document_type`).
- Deduplicate semantically equivalent concepts ("user age", "applicant age", "date of birth evaluation" → one variable like `customer_age` or `is_applicant_minor`).
- Data types only: `string`, `number`, `boolean`, `array`.
- Exclude system metadata (timestamps, internal IDs).

Expected output:

```json
{
  "variables": [
    {
      "variable_name": "identity_document_country",
      "data_type": "string",
      "description": "Issuing country of the uploaded identity document."
    },
    {
      "variable_name": "is_applicant_minor",
      "data_type": "boolean",
      "description": "True if the applicant's age is under 18."
    }
  ]
}
```

### 4.2 Dictionary orchestration function

```python
def generate_policy_dictionary(doc_id: str, relevant_chunks: List[RawChunk], llm_client) -> PolicyDataDictionary:
    corpus = "\n\n=== CHUNK ===\n\n".join([c.text_content for c in relevant_chunks])

    resp = llm_client.generate_json(
        system_prompt=load_prompt("dictionary_generator.txt"),
        user_content=f"Document ID: {doc_id}\nTarget Corpus:\n{corpus}"
    )

    variables = [DataVariable(**v) for v in resp["variables"]]
    return PolicyDataDictionary(doc_id=doc_id, variables=variables)
```

Notes:

- This dictionary is **immutable** during extraction.
- All ProcedureChunks must reference only these variable names.

---

## 5. Phase 3 — ProcedureChunk Extraction

Goal: convert each `PRIMARY_RULE_BLOCK` RawChunk into one `ProcedureChunk` that encodes a semantically closed execution unit, with modifiers and tables woven in.

### 5.1 Rule extractor LLM prompt (prompts/rule_extractor.txt)

Inputs to LLM:

1. Primary Seed Chunk: one `PRIMARY_RULE_BLOCK` `RawChunk.text_content`.
2. Supporting Context Chunks: concatenated text from `CONDITIONAL_MODIFIER` and `REFERENCE_TABLE` buckets.
3. Global Data Dictionary: JSON representation of `PolicyDataDictionary`.

Instructions (simplified):

- Parse the primary seed into a clear logical execution flow (`logic_flow` array) of `RuleStep`s.
- Scan supporting context for exceptions, overrides, global constraints that apply to the primary logic; integrate them into `logic_flow`.
- For every parameter used in conditions or steps, **select its exact key** from the Data Dictionary; do not invent variables.
- Assign one `execution_category` from `ActionTaxonomy`.
- Identify dependencies: any other procedures (by approximate title) that must run before this one.

Expected LLM output:

```json
{
  "title": "Verify Utility Bill Freshness",
  "execution_category": "document_verification",
  "required_inputs": ["bill_age_days", "customer_country"],
  "logic_flow": [
    {
      "step_number": 1,
      "expression": "IF customer_country == 'UK' THEN bill_age_days <= 180 ELSE bill_age_days <= 90",
      "failure_message": "Utility bill is too old for address verification."
    }
  ],
  "dependencies": {
    "and_prerequisites": ["Verify Uploaded Document Type"],
    "or_prerequisites": []
  }
}
```

### 5.2 Extraction orchestration function

```python
import hashlib
import json


def extract_procedure_chunks(
    doc_id: str,
    buckets: Dict[TriageCategory, List[RawChunk]],
    data_dict: PolicyDataDictionary,
    llm_client
) -> List[ProcedureChunk]:
    procedures: List[ProcedureChunk] = []

    supporting_text = "\n\n=== MODIFIER / TABLE ===\n\n".join(
        [c.text_content for c in buckets[TriageCategory.CONDITIONAL_MODIFIER]] +
        [c.text_content for c in buckets[TriageCategory.REFERENCE_TABLE]]
    )

    dict_json = json.dumps(data_dict.model_dump(), indent=2)
    index = 1

    for seed in buckets[TriageCategory.PRIMARY_RULE_BLOCK]:
        payload = (
            f"PRIMARY SEED CHUNK:\n{seed.text_content}\n\n"
            f"SUPPORTING POLICY CONTEXT:\n{supporting_text}\n\n"
            f"GLOBAL SYSTEM DATA DICTIONARY:\n{dict_json}"
        )

        rule_spec = llm_client.generate_json(
            system_prompt=load_prompt("rule_extractor.txt"),
            user_content=payload,
        )

        # Compute hash of logic for integrity tracking
        logic_str = json.dumps(rule_spec["logic_flow"], sort_keys=True)
        logic_hash = hashlib.sha256(logic_str.encode("utf-8")).hexdigest()

        origin_nodes = list(set(seed.origin_node_ids))
        source_chunks = [seed.chunk_id]

        # Enforce dictionary: no unknown variables
        for var in rule_spec["required_inputs"]:
            assert any(v.variable_name == var for v in data_dict.variables), (
                f"Unknown variable '{var}' not present in PolicyDataDictionary"
            )

        procedure = ProcedureChunk(
            procedure_id=f"PROC_{doc_id}#_LN_{str(index).zfill(4)}",
            doc_id=doc_id,
            execution_category=ActionTaxonomy(rule_spec["execution_category"]),
            title=rule_spec["title"],
            required_inputs=rule_spec["required_inputs"],
            logic_flow=[RuleStep(**step) for step in rule_spec["logic_flow"]],
            dependencies=DependencyGate(
                and_prerequisites=rule_spec["dependencies"]["and_prerequisites"],
                or_prerequisites=rule_spec["dependencies"]["or_prerequisites"],
            ),
            source_raw_chunk_ids=source_chunks,
            origin_node_ids=origin_nodes,
            logic_hash=logic_hash,
        )

        procedures.append(procedure)
        index += 1

    return procedures
```

Notes:

- One ProcedureChunk per primary rule block initially; higher-level merging/splitting can be added later if needed.
- `logic_hash` allows you to detect silent mutations across runs.

---

## 6. Phase 4 — Procedure DAG Compilation (Interface Only)

The Procedure Chunk Engine does not build the DAG itself, but it must produce ProcedureChunks structured for DAG compilation:

- `title` should be descriptive enough to resolve dependencies.
- `dependencies.and_prerequisites` and `dependencies.or_prerequisites` initially store textual names; the DAG builder will map these to IDs and check for cycles.

Interface to DAG builder:

```python
def compile_procedure_dag(procedures: List[ProcedureChunk]) -> Dict[str, Any]:
    """Resolve textual dependencies to IDs, detect cycles, and build adjacency list."""
    ...
```

---

## 7. Phase 5 — Integration with Procedure Validation Engine (PVE)

PVE consumes:

- `procedure_chunks: List[ProcedureChunk]`
- `policy_data_dictionary: PolicyDataDictionary`
- RawChunks and DocumentTree (for clause-level mapping)

PVE responsibilities (outside this spec):

- Check coverage (all enforceable clauses mapped to some RuleStep).
- Check dependency correctness (modifiers and global constraints applied where needed).
- Detect contradictions and unreachable nodes.
- Drive judge+repair loops for self-correction.

The Procedure Chunk Engine must:

- Preserve provenance for PVE:
  - `source_raw_chunk_ids` and `origin_node_ids` per ProcedureChunk.
  - `doc_id`, `section_path` in RawChunks.

---

## 8. End-to-End Orchestration (High-Level Pseudo-Code)

```python
def build_procedure_chunks_for_document(doc_id: str, raw_chunks: List[RawChunk], llm_client) -> Tuple[PolicyDataDictionary, List[ProcedureChunk]]:
    # Phase 1: triage
    buckets = triage_raw_chunks(doc_id, raw_chunks, llm_client)

    # Phase 2: data dictionary
    relevant_chunks = buckets[TriageCategory.PRIMARY_RULE_BLOCK] + buckets[TriageCategory.CONDITIONAL_MODIFIER]
    data_dict = generate_policy_dictionary(doc_id, relevant_chunks, llm_client)

    # Phase 3: procedure extraction
    procedures = extract_procedure_chunks(doc_id, buckets, data_dict, llm_client)

    return data_dict, procedures
```

This function defines the contract between:

- Raw Chunking + DSVE (upstream).
- Procedure Chunk Engine (this spec).
- Procedure DAG Compiler and PVE (downstream).

---

## 9. Testing & Validation Guidelines

1. **Dictionary enforcement tests**
   - Ensure no `ProcedureChunk.required_inputs` contain variable names outside `PolicyDataDictionary.variables`.

2. **Lineage tests**
   - For each ProcedureChunk, assert that `source_raw_chunk_ids` and `origin_node_ids` refer to valid RawChunks/DocumentTree nodes.

3. **Determinism tests**
   - For a fixed `doc_id` and `raw_chunks`, run the engine twice and compare:
     - Number of ProcedureChunks.
     - Set of `procedure_id`s.
     - `logic_hash` values.

4. **Security tests (tool scoping)**
   - For `execution_category == LOGIC_EVALUATION` or `CALCULATION`, assert that no titles or expressions imply external side effects.

These tests ensure that the Procedure Chunk Engine produces consistent, auditable, and safe execution units for downstream DAG compilation and agent execution.
