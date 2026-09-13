# Chunking Strategy for Policy Documents

**Goal:** Derive **raw chunks** from the parsed `DocumentTree` that preserve meaningful text segments for retrieval, then transform those into **procedure chunks** (executable business rules). We must remain consistent and deterministic in chunk formation across documents and runs. The process should yield chunks that are semantically coherent (not arbitrarily cutting sentences or logical units) and aligned with document structure.

## Raw Chunking Principles

- **Respect Logical Boundaries:** Never split text across natural boundaries. Bedrock’s chunker, for example, “respects logical document boundaries (such as pages or sections) and does not merge content across these boundaries”.  Likewise, our raw chunks should align with section or paragraph boundaries in the `DocumentTree`. In practice, this means each raw chunk should contain one or more whole paragraphs or table rows from the same section, but never half a paragraph or parts of two different sections.

- **Preserve Semantic Coherence:** Empirical studies show that *content-aware* segmentation beats fixed-size splitting. For policy/legal text, grouping multiple related paragraphs into a single chunk often yields the most coherent units. For example, legal documents “present arguments spanning multiple paragraphs,” and grouping them preserves the complete logical unit for retrieval. We should aim to keep multi-sentence logical units intact in a chunk. 

- **Hierarchical Structure as a Guide:** Use the document’s hierarchy as a scaffold. Leverage section and subsection headings to guide chunk boundaries. For instance, one simple strategy is *one raw chunk per section* (or per subsection if sections are very large). Bedrock’s **hierarchical chunking** approach reflects this: it creates nested parent/child chunks and retrieves small (“child”) chunks but then uses their parent chunk for context. We can apply a similar idea: initially propose chunks at the smallest reasonable unit (e.g. subsections or paragraphs) but be ready to merge them if needed. 

- **Merge or Split to Meet Token Goals:** While respecting structure, adjust chunk size for efficiency. If a raw chunk (say, a very long section) exceeds token limits, split it on sentence boundaries. Conversely, if two consecutive paragraphs are both very short (e.g. 10–20 tokens each), merge them into one chunk to ensure each chunk is substantial enough. Docling’s **HybridChunker** does token-based refinement on top of hierarchical chunks, splitting oversized chunks and merging undersized ones; we can adopt a similar heuristic without relying on Docling itself.

- **Tables and Lists:** Tables should usually remain atomic or be handled specially. For example, **repeat table headers** if splitting a table across chunks (a feature available in Docling). If tables are small, treat an entire table as one raw chunk. Lists (bullet points) often form one logical list; merge consecutive list items into a single chunk by default, as Docling’s default **HierarchicalChunker** does with list items.

- **Deterministic Boundaries:** Ensure the chunk algorithm is deterministic: given the same `DocumentTree`, it should always produce the same chunk boundaries. Avoid any non-deterministic clustering or random-seed based methods. Use fixed rules (e.g. “group up to 3 paragraphs” or “split at 500-token threshold”).

- **Example:** In practice, a raw chunk might contain:
  - The full text of Section 2.1, or 
  - Two paragraphs of Section 2.1 (if paragraphs are very short),
  - Or all rows of a table under Section 3.4 (if that represents one rule),
  etc., as long as each chunk is a stand-alone, contextually complete excerpt.

## Defining a Raw Chunk

A **RawChunk** should be a data structure containing: 
- **chunk_id:** e.g. `P1-S2.1-C1` (document P1, section 2.1, chunk 1).
- **text:** The full concatenated text of the chunk (multiple paragraphs, etc.).
- **node_ids:** List of the `DocumentTree` node IDs that contributed text (for traceability).
- **metadata:** Source pointers (document, section, page numbers), and any headers or captions for context.
- **chunk_type:** (e.g. “paragraph_group”, “table”, “list”) if desired for analysis.
- **token_count:** (optional) for monitoring size.
  
This raw chunk schema anchors each chunk in the original document structure. By storing the contributing node IDs, we ensure we can map back to the original text. The `chunk_id` should be generated deterministically from document and section identifiers to guarantee consistency across runs.

## Raw Chunking Algorithms

We might implement one or more of the following strategies:

- **Hierarchical Sections:** Create one chunk per section (or subsection). If a section’s text is too long (e.g. >1000 tokens), split it further at logical sub-boundaries (between paragraphs or sentence break). If a section has no text (empty section), skip it.

- **Paragraph Grouping:** Slide a window of *N* paragraphs (with optional overlap) through each section. For example, group every 2 paragraphs with 1-paragraph overlap (similar to “Paragraph Group Chunking”). This preserves argument continuity and provides contextual overlap. If a section has an odd number of paragraphs, the last group might be just one paragraph or merged with the previous group.

- **Token-Based Refinement:** After initial chunk boundaries (by section or paragraphs), check each chunk’s token count. If below a minimum threshold (say 100 tokens), try to merge it with an adjacent chunk (within the same section). If above a maximum threshold (say 500 tokens), split it at the nearest sentence boundary. This mimics hybrid approaches that align to token budgets. 

- **List and Table Handling:** Merge consecutive list items into one chunk, or treat each list separately if they are long. For tables spanning multiple paragraphs or pages, consider each table a chunk. If a table is extremely long, one could break it into row-groups, but often preserving the whole table is best for fidelity.

- **Overlap for Context (Optional):** If retrieval performance requires it, allow a small overlap between chunks (e.g. repeat the last sentence of chunk *i* at the beginning of chunk *i+1*). This can help maintain context but is optional and should be used carefully to avoid duplication.

These strategies ensure that no chunk is an arbitrary text fragment; instead, chunks are coherent pieces guided by the document’s own structure and content. 

## Procedure Chunk Extraction

A **Procedure Chunk** is a higher-level artifact derived from one or more raw chunks. It is a structured, *executable* representation of a business rule or step. For example, a raw chunk might describe the requirement “Applicant must submit proof of address.” The corresponding procedure chunk would explicitly encode *Condition:* (Applicant exists), *Action:* (verify that proof of address is provided), *Required Documents:* (proof of address).

To transform raw chunks into procedure chunks:

1. **Identify Rule Segments:** Examine the raw chunk text and any related chunks to extract the rule components. Typically this means finding conditions (if/when clauses) and actions (must, shall, require verbs). Sometimes conditions and actions span multiple contiguous raw chunks (e.g. a list of conditions followed by list of required docs). 

2. **Merge If Needed:** If a complete rule spans multiple raw chunks (e.g. one chunk has the “if” clause, and the next chunk lists documents), we should merge those raw chunks’ contents to form one rule. This merging should be deterministic (e.g. merge only if there is an explicit link like “see above condition”).

3. **LLM or Rule-Based Extraction:** We can use an LLM (or a more deterministic parser) to parse the raw text into a structured form. For example, a prompt to extract a rule might look like:

   > *“Extract the business rule from the following policy text. Identify any conditions, required actions, and exceptions. Return a JSON object with fields `condition`, `action`, `exceptions` (if any). Do not output any additional text.”* 

   The LLM output might be:  
   ```json
   {
     "condition": "Customer is a new applicant",
     "action": "Ensure the following documents are submitted: Passport, Utility Bill, Bank Statement",
     "exceptions": "None"
   }
   ```

   Having a strict output schema (JSON) makes the process reliable. You can refine the prompt to the domain’s needs, e.g., listing specific slots like `required_documents`, `eligibility_criteria`, etc.

4. **Procedure Chunk Structure:** Define a schema for procedure chunks. For example:
   ```yaml
   procedure_id: PR-0001
   derived_from: [RC-023, RC-024]   # list of raw chunk IDs
   condition: "..."
   action: "..."
   required_documents: ["Passport","Utility Bill"]
   exceptions: "..."
   severity: "mandatory"   # for example
   metadata:
     source_section: "3.4"
     confidence: 0.95
   ```
   Each procedure chunk has a unique ID, links to the raw chunks it came from, and fully parsed fields. This aligns with the idea that knowledge units carry identifiers, types, and rules.

5. **Verification:** Use consistency checks (like cross-referencing the extracted rule with the original text or other rules). For example, if another chunk mentions an exception to the same rule, the Procedure Chunk should capture that.

## Consistency and Evaluation

- **Deterministic IDs and Boundaries:** Always generate `raw_chunk_id` and `procedure_id` deterministically (e.g. based on document and section identifiers) so that repeated runs produce the same results. This ensures stability across versions of the pipeline.

- **Chunk Stability Tests:** To ensure chunks are stable, you can:
  - Run the chunker twice on the same `DocumentTree` and verify that chunk boundaries and IDs match exactly.
  - Slightly perturb the input (e.g. add a word in a safe place) and check that unaffected chunks remain unchanged.
  - Compare chunking of similar documents to see if strategies generalize.

- **Retrieval Metrics:** Evaluate chunking quality by RAG metrics. For example, use normalized DCG (nDCG@k) or Hit@k on question-answer pairs to see if relevant chunks are retrieved as top hits. The literature uses these to compare strategies. Higher nDCG and precision indicate that chunks are semantically coherent and useful.

- **Chunk Content Checks:** Automatically flag suspicious chunks, e.g. chunks that start or end mid-sentence, or have an extremely short text. These can be caught by simple validators (e.g. sentence boundary detection).

- **Compliance Tests:** After creating procedure chunks, test them against example queries or a rule engine to ensure they produce the correct outcomes (e.g. feeding a known document to the agent and confirming the rule triggers correctly).

In sum, our strategy is to first segment the document into **raw, retrievable chunks** based on document structure and semantic coherence. These raw chunks feed both the vector index and serve as input for rule extraction. Then we transform those chunks into **procedure chunks** – structured business rules with their own IDs and metadata. This two-stage pipeline (raw chunks → procedure chunks) maximizes both retrieval performance and the creation of deterministic, executable knowledge units. 

**Sources:** This design draws on best practices in RAG chunking, AWS Bedrock’s chunking guidelines, and the Open Knowledge Format concept of turning text fragments into typed knowledge with IDs and rules. It balances semantic completeness with operational consistency to support both retrieval and rule execution.