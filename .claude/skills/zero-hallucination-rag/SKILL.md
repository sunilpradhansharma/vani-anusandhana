---
name: zero-hallucination-rag
description: Apply this skill when generating, modifying, or reviewing any retrieval, ranking, summarization, or query-API code in the vāṇī-anusandhāna project. Make sure to use this skill whenever the task involves chunking, embedding, indexing, vector search, reranking, result aggregation, summary blocks, hero answers, or any LLM-touching path that processes HH Romapada Swami's lecture transcripts. Trigger this skill even if the user does not explicitly mention "RAG" or "hallucination" — any code that retrieves passages and presents them to a devotee falls under this constraint. The project has a hard zero-hallucination requirement and this skill enforces it.
---

# Zero-Hallucination RAG — vāṇī-anusandhāna

This project is a semantic search system over HH Romapada Swami's recorded lectures. Devotees ask spiritual questions and the system returns **direct excerpts** from the lectures, with timestamps and deep-links to the source videos.

The defining constraint of this project is **fidelity to the source**. Every word presented to the devotee must be either:

1. A verbatim transcript excerpt from a recorded lecture, OR
2. UI chrome, metadata, or attribution (clearly distinguishable from teaching content)

There is **NO third category**. No paraphrasing. No LLM-generated synthesis of meaning. No "summarization" that interprets the teacher's words. Even small reframings can subtly shift theological meaning.

## Hard rules (NEVER violate)

### 1. No LLM in the retrieval/ranking/summarization path

Code generated for query handling MUST NOT call any of the following inside the search request lifecycle:

- `openai.chat.completions.create` / `openai.completions.create`
- `anthropic.messages.create`
- `google.generativeai.GenerativeModel(...).generate_content`
- Hugging Face `transformers.pipeline("summarization")`, `pipeline("text-generation")`, `pipeline("text2text-generation")`
- LangChain `LLMChain`, `RetrievalQA`, `ConversationalRetrievalChain`, or any chain that includes an LLM
- `llama_index` query engines that route through an LLM
- Any Python function whose docstring or name implies summarization, paraphrasing, rewriting, or synthesis (`summarize`, `paraphrase`, `rephrase`, `synthesize_answer`, `generate_summary`)

If you encounter a request that seems to require these (e.g., "create a summary of the top 5 results"), you must implement it **extractively** — see Required behaviors below.

### 2. Per-video diversification cap

The retrieval results MUST cap at **maximum 2 chunks from the same source video**. This prevents one verbose video from dominating all 5 result slots and ensures the devotee sees teachings *across* lectures.

Implementation pattern:

```python
def diversify_by_video(ranked_chunks, max_per_video=2, target_count=5):
    """Cap results per source video, preserving rank order."""
    seen = {}
    diversified = []
    for chunk in ranked_chunks:
        vid = chunk.metadata["video_id"]
        if seen.get(vid, 0) < max_per_video:
            diversified.append(chunk)
            seen[vid] = seen.get(vid, 0) + 1
            if len(diversified) >= target_count:
                break
    return diversified
```

### 3. Relevance threshold gating

The reranker (bge-reranker-v2-m3) returns scores roughly in [0, 1]. Results below a threshold (default `0.5`) MUST be excluded from the response, even if it means returning fewer than 5 results, even if it means returning **zero** results.

Returning irrelevant passages just to fill the quota is a hallucination of relevance. The "no results" state exists for exactly this case.

```python
RELEVANCE_THRESHOLD = 0.5  # tunable; surface this in config

filtered = [c for c in reranked if c.rerank_score >= RELEVANCE_THRESHOLD]
if not filtered:
    return NoResultsResponse(query=q, suggestions=related_terms(q))
```

### 4. Extractive-only summary (the "hero answer" block)

The UI shows a "hero answer" block at the top of search results, labeled "Found across N lectures · synthesized". This block MUST be constructed by:

- **Selecting** the most informative sentence(s) from the top-ranked chunks (NOT generating new text)
- **Concatenating** them with minimal connective punctuation (`. `, ` — `, line breaks)
- **Preserving** the teacher's exact wording, including Sanskrit terms, ellipses, and natural speech patterns

The label "synthesized" refers to the *act of selection across multiple sources*, not to LLM-generated synthesis of meaning. Make this distinction visible in the implementation:

```python
def build_hero_answer(ranked_chunks: list[Chunk], max_sentences: int = 2) -> HeroAnswer:
    """
    Extractive summary: pick the highest-relevance sentence from each of
    the top-2 unique source videos, concatenate verbatim. No paraphrasing.
    """
    seen_videos = set()
    selected = []
    for chunk in ranked_chunks:
        if chunk.video_id in seen_videos:
            continue
        # Pick the sentence with highest term overlap with the query
        sentence = pick_best_sentence(chunk, query=chunk.query)
        selected.append(sentence)
        seen_videos.add(chunk.video_id)
        if len(selected) >= max_sentences:
            break
    
    return HeroAnswer(
        text="\n".join(selected),  # verbatim, no rewriting
        source_count=len(seen_videos),
        method="extractive",  # explicit marker
    )
```

### 5. Citation tracking is mandatory

Every passage shown in the UI must carry, traveling with it through the entire pipeline:

- `video_id` (stable YouTube ID)
- `video_title` (current canonical title)
- `start_seconds` and `end_seconds`
- `chunk_id` (deterministic hash of video_id + start_seconds + content)
- `transcript_source` (path to source JSON, for auditability)

Code that strips or replaces these fields with derived/synthesized values is forbidden.

## Required behaviors

### When the user asks for "smart summarization" or "AI-powered insights"

Politely decline and offer the extractive alternative. Example response:

> "This project has a zero-hallucination requirement on the teacher's words. Instead of generating an LLM summary, I'll implement an extractive approach: select the most relevant sentence from each of the top-2 unique source videos and concatenate them verbatim. The 'synthesized' label refers to selecting across multiple lectures, not generating new text."

Then implement the extractive version.

### When implementing query handling

The search pipeline must follow this exact order:

1. Embed query (bge-m3, dense + sparse)
2. Hybrid search Qdrant → top 20 candidates
3. Rerank with bge-reranker-v2-m3
4. **Filter**: `rerank_score >= RELEVANCE_THRESHOLD`
5. **Diversify**: max 2 per video
6. **Cap**: take top 5
7. **Extract**: build hero answer from top results
8. Return structured response with hero + passages + metadata

If any step is skipped or reordered, the result risks failing the zero-hallucination requirement.

### When the user asks for "rephrasing the answer in simpler words"

This is the same anti-pattern, dressed up. Decline with the same explanation. Offer instead to:

- Highlight Sanskrit terms with tooltips (the existing UI pattern)
- Show a "Devanagari toggle" for transliteration
- Link to the full video for full context

But do not paraphrase.

## Anti-patterns to refuse

If the codebase or a prompt contains any of these patterns, treat it as a bug to be reported, not a feature to be implemented:

| Anti-pattern | What's wrong | Correct alternative |
|---|---|---|
| `summary = llm.invoke(f"Summarize: {chunks}")` | LLM in the path | Extractive sentence selection |
| Returning a fixed 5 results regardless of relevance | Hallucinates relevance | Apply threshold; return fewer or none |
| Returning all 5 from the same video | Skews toward one lecture | Apply per-video cap |
| Smoothing transcript with grammar correction | Rewrites teacher's words | Keep verbatim, even if disfluent |
| Translating Sanskrit terms inline | Theological reframing | Tooltip with transliteration only |
| Auto-generating "related questions" via LLM | New text not from teacher | Pre-curated suggestion chips from `SANSKRIT_VOCAB_METHODOLOGY.md` |

## Examples of correct implementations

### Hero answer (extractive synthesis)

```python
@dataclass
class HeroAnswer:
    text: str                  # verbatim concatenation
    source_videos: list[str]   # video_ids contributing
    method: str = "extractive" # never "generated", "synthesized" (in LLM sense)
    
    def __post_init__(self):
        assert self.method == "extractive", \
            "Zero-hallucination invariant: hero answer must be extractive"


def build_hero(reranked: list[RankedChunk]) -> HeroAnswer:
    seen = set()
    selected_sentences = []
    contributing_videos = []
    
    for chunk in reranked:
        if chunk.video_id in seen:
            continue
        # sentence with most query-term overlap
        best = pick_best_sentence(chunk.text, chunk.query_terms)
        if best:
            selected_sentences.append(best.strip())
            contributing_videos.append(chunk.video_id)
            seen.add(chunk.video_id)
        if len(selected_sentences) >= 2:
            break
    
    return HeroAnswer(
        text="\n".join(selected_sentences),
        source_videos=contributing_videos,
    )
```

### Query API response shape

```python
class SearchResponse(BaseModel):
    query: str
    hero: HeroAnswer | None        # None if zero results passed threshold
    passages: list[Passage]        # 0 to 5, after diversification + threshold
    no_results: bool               # True iff len(passages) == 0
    metadata: ResponseMetadata     # latency, threshold used, total candidates
    
    @validator("hero")
    def hero_consistent_with_passages(cls, v, values):
        if values["no_results"] and v is not None:
            raise ValueError("Hero answer present despite no_results=True")
        return v
```

### Reranker filter

```python
def apply_threshold(reranked: list[RankedChunk], threshold: float) -> list[RankedChunk]:
    """Return only chunks meeting the relevance threshold. May return [].
    
    Returning fewer-than-target results is the CORRECT behavior — better than
    returning irrelevant passages. The 'no results' UI state exists for this.
    """
    return [c for c in reranked if c.rerank_score >= threshold]
```

## Reference

For project context, also see:

- `PILOT_RUNBOOK.md` — full pipeline architecture
- `SANSKRIT_VOCAB_METHODOLOGY.md` — 3-layer Sanskrit handling (related concern)
- `architecture.md` — Mermaid diagram of the data flow

## Why this matters

vāṇī-anusandhāna is not a general-purpose chatbot. It is a tool for devotees to find what HH Romapada Swami has actually said on a topic. The moment we paraphrase, we substitute *our* understanding for *his* teaching. That violates the project's foundational vow.

Every line of code in the retrieval/summary path either upholds this vow or breaks it. There is no neutral position.
