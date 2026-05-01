---
name: sanskrit-handling
description: Apply this skill whenever code in the vāṇī-anusandhāna project touches Sanskrit text — including transcription with mlx-whisper, post-processing of transcripts, normalization dictionaries, fuzzy matching, embedding/indexing of mixed English-Sanskrit text, the Devanagari toggle in the UI, term tooltips, transliteration display, or any glossary/vocabulary file. Make sure to use this skill whenever the user mentions transcripts, Whisper, IAST, diacritics, śravaṇa, smaraṇa, Bhāgavatam, ācārya, Devanagari, paramparā, normalization, rapidfuzz, BM25 over Sanskrit, the seed vocabulary, or anything that resembles Sanskrit/Hindi/Devanagari content. Trigger this skill even if the user describes the task generically (e.g., "fix the transcription pipeline") — anywhere mlx-whisper or transcript text is involved, Sanskrit handling applies.
---

# Sanskrit Handling — vāṇī-anusandhāna

This project transcribes and indexes lectures by HH Romapada Swami, an ISKCON sannyasi who teaches in English with frequent Sanskrit terminology in the Gauḍīya Vaiṣṇava tradition. Sanskrit terms are a substantial portion of the *meaning* of these lectures — getting them wrong silently degrades search quality for every devotee.

The full conceptual framework lives in [`SANSKRIT_VOCAB_METHODOLOGY.md`](SANSKRIT_VOCAB_METHODOLOGY.md) (which Claude should read once for context, then refer back to as needed). This skill encodes the *operational* rules: what to do when generating code or content that touches Sanskrit text.

## Core mental model — three layers

Sanskrit handling happens at three layers of the pipeline. They are complementary, not redundant:

| Layer | When | What | Where |
|---|---|---|---|
| **1. Whisper `initial_prompt`** | At transcription time | Biases Whisper toward correct diacriticalized terms it already knows | `mlx_whisper.transcribe(initial_prompt=...)` |
| **2. Post-processing normalization** | After transcription | Fuzzy match-and-replace using a JSON dictionary; catches what the prompt missed | `app/sanskrit/normalize.py` |
| **3. Dual indexing** | At Qdrant index time | Index both original + normalized forms; lets devotees retrieve regardless of how they spell terms | `app/index/build.py` |

When generating code, **always think about which layer(s) the change affects**. Modifying Layer 1 without thinking about Layer 2 leads to drift. Modifying Layer 3 without preserving `text_original` destroys the audit trail.

## Hard rules

### 1. Always preserve `text_original` alongside `text_normalized`

Every chunk record in Qdrant, every JSON file, every database row that holds transcript text MUST carry both:

- `text_original` — what Whisper produced verbatim, untouched
- `text_normalized` — after Layer 2 normalization

```python
@dataclass
class TranscriptChunk:
    chunk_id: str
    video_id: str
    start_seconds: float
    end_seconds: float
    text_original: str       # untouched Whisper output
    text_normalized: str     # after Sanskrit normalization
    normalizations_applied: list[NormalizationApplied]  # audit trail
```

Code that drops `text_original`, replaces it in-place, or treats normalization as destructive is forbidden. The original is the source of truth for auditability and for re-running normalization with an updated dictionary.

### 2. Use natural-prose `initial_prompt`, never bare term lists

For mlx-whisper transcription, the `initial_prompt` MUST be written as a natural-sounding sentence-level paragraph that includes the Sanskrit terms in context. Bare comma-separated lists work measurably worse (~20-30% lower diacritical accuracy in our testing).

**Correct** (prose form):

```python
INITIAL_PROMPT = (
    "This is a lecture on Śrīmad-Bhāgavatam by an ācārya in the Gauḍīya "
    "paramparā, discussing topics like saṅkīrtana, prema-bhakti, the role "
    "of guru, and the relationship between dharma, jīva, and māyā as "
    "taught by Śrīla Prabhupāda."
)
```

**Wrong** (bare list):

```python
INITIAL_PROMPT = "Bhāgavatam, ācārya, paramparā, saṅkīrtana, prema, bhakti..."
```

### 3. Respect the 244-token Whisper prompt cap

mlx-whisper silently truncates `initial_prompt` from the **start** if it exceeds ~244 tokens (roughly 1000 characters). Truncating from the start means the most important terms — typically placed first — are the ones that get cut.

**Operational rule**: keep prompts at ~800 characters or less. Add a length check in the code:

```python
def validate_whisper_prompt(prompt: str) -> None:
    if len(prompt) > 1000:
        raise ValueError(
            f"Whisper initial_prompt is {len(prompt)} chars; "
            f"may be truncated. Keep under 1000 (~244 tokens)."
        )
```

Don't lecture the user about this — just enforce it in code with a clear error.

### 4. Word-boundary matching in normalization, never substring

The normalization dictionary applies replacements like `"gita" → "Bhagavad-gītā"`. Substring matching breaks proper nouns: the name "Sangita" would become "Sang-Bhagavad-gītā".

**Always** use word-boundary regex (`\b`) for normalization replacements:

```python
import re

def apply_normalization(text: str, mapping: dict[str, str]) -> str:
    """Replace dictionary keys with values, respecting word boundaries."""
    for wrong, right in mapping.items():
        # \b ensures word boundary on both sides
        pattern = r'\b' + re.escape(wrong) + r'\b'
        text = re.sub(pattern, right, text, flags=re.IGNORECASE)
    return text
```

Never use plain `str.replace()` for normalization. Never iterate substring-by-substring.

### 5. Fuzzy matching threshold defaults to 90%

When using `rapidfuzz` for fuzzy normalization (catching variants like "bhagatam"/"bhagwatam"/"bhagatum" → "Bhāgavatam"), the similarity threshold is **90%**. This is the empirically tested sweet spot — see methodology doc for the analysis.

```python
from rapidfuzz import fuzz

FUZZY_THRESHOLD = 90  # tunable in config; see SANSKRIT_VOCAB_METHODOLOGY.md
```

Don't use 85 (too loose, false positives), don't use 95 (too strict, misses real errors). If the user requests a different threshold, ask them to read the methodology doc first.

### 6. Maintain a "do not normalize" allow-list

Some English words look like Sanskrit fragments and should be excluded from fuzzy matching. The normalization config must support an explicit exclusion list:

```json
{
  "do_not_normalize": [
    "Sangita",  // proper noun, not "Sang-gita"
    "yoga",     // ambiguous; sometimes English context, sometimes Sanskrit
    "karma"     // too common in English; only normalize in clear Sanskrit context
  ]
}
```

Code that processes the dictionary must respect this list before running fuzzy matching.

### 7. Index hybrid: dense + sparse over the normalized form

Qdrant indexing for this project uses **hybrid search** with bge-m3 (which produces both dense and sparse vectors in one model call). Both vectors are computed from `text_normalized`. The `text_original` is kept in payload but NOT indexed for search.

```python
# CORRECT
embeddings = bge_m3.encode(chunk.text_normalized)  # both dense + sparse
qdrant.upsert(
    points=[
        PointStruct(
            id=chunk.chunk_id,
            vector={
                "dense": embeddings["dense_vecs"][0],
                "sparse": embeddings["lexical_weights"][0],
            },
            payload={
                "text_normalized": chunk.text_normalized,
                "text_original": chunk.text_original,  # for audit, not search
                "video_id": chunk.video_id,
                "start_seconds": chunk.start_seconds,
                "end_seconds": chunk.end_seconds,
                "normalizations_applied": chunk.normalizations_applied,
            },
        )
    ]
)
```

Don't embed `text_original` separately — it doubles storage and rarely improves recall (bge-m3 handles diacritics well natively).

### 8. Devanagari toggle must use a separate transliteration field

The UI has a toggle to display Sanskrit terms in Devanagari script (देवनागरी) instead of IAST (Devanāgarī). This is a *display-time* concern — the underlying data stays in IAST.

```python
# Stored in the term glossary, alongside transliteration
{
    "term_iast": "śravaṇa",
    "term_devanagari": "श्रवण",
    "term_simple": "shravana",  # for fuzzy matching from search box
    "definition": "listening, hearing — the first of the nine limbs of bhakti"
}
```

The frontend toggles between `term_iast` and `term_devanagari` for display. Code that mixes scripts in the same field, or that converts at query time, is forbidden.

## Required behaviors

### When generating Whisper transcription code

Always include:

1. The natural-prose `initial_prompt` (loaded from a config file, not hardcoded inline)
2. Length validation against the 1000-character limit
3. Output to JSON (not raw text) so timestamps are preserved
4. A `model="large-v3"` default — anything smaller drops Sanskrit accuracy noticeably

Skeleton:

```python
import mlx_whisper
from pathlib import Path

def transcribe(audio_path: Path, prompt_path: Path, model: str = "mlx-community/whisper-large-v3-mlx") -> dict:
    initial_prompt = prompt_path.read_text()
    validate_whisper_prompt(initial_prompt)
    
    result = mlx_whisper.transcribe(
        str(audio_path),
        path_or_hf_repo=model,
        initial_prompt=initial_prompt,
        language="en",          # English with embedded Sanskrit
        word_timestamps=True,   # required for chunk-level timestamps
    )
    return result
```

### When generating normalization code

Always:

- Load the dictionary from JSON, not hardcoded
- Apply replacements in deterministic order (sorted by key length descending — longer phrases first to prevent partial overlaps)
- Track every replacement made (audit trail in `normalizations_applied`)
- Make normalization idempotent — running it twice produces identical output

Skeleton:

```python
def normalize_transcript(text: str, dictionary: NormalizationDict) -> NormalizationResult:
    applied = []
    out = text
    
    # Sort by key length desc so "guru tattva" matches before "guru"
    items = sorted(dictionary.corrections.items(), key=lambda kv: -len(kv[0]))
    
    for wrong, right in items:
        if wrong.lower() in dictionary.do_not_normalize:
            continue
        pattern = r'\b' + re.escape(wrong) + r'\b'
        new_out, n = re.subn(pattern, right, out, flags=re.IGNORECASE)
        if n > 0:
            applied.append(NormalizationApplied(
                wrong=wrong, right=right, count=n
            ))
        out = new_out
    
    # Fuzzy pass — only on terms not yet matched
    out = apply_fuzzy_normalization(out, dictionary, threshold=90)
    
    return NormalizationResult(text_normalized=out, applied=applied)
```

### When generating Sanskrit-aware UI

The UI shows Sanskrit terms with:

- **IAST display by default** (śravaṇa)
- **Dotted underline** indicating tappable
- **Tooltip on hover/tap** showing IAST + Devanagari + brief gloss
- **Devanagari toggle** in sidebar/header that swaps the displayed script

When generating template code for this:

- Look up the term in the glossary at render time, not search time
- Always include the `lang="sa"` attribute on Sanskrit-text elements (accessibility)
- Respect the Devanagari toggle setting via a Pinia/Alpine store, not URL params

### When asked to "improve transcription quality"

Suggest in this order:

1. Have you iterated on the `initial_prompt`? (Layer 1 fixes are highest leverage — see methodology doc for the iteration protocol.)
2. Have you grown the normalization dictionary? (Layer 2 fixes everything Layer 1 missed.)
3. Have you confirmed dual indexing is working? (Layer 3 catches everything else at search time.)

Don't jump to fine-tuning Whisper, training a custom model, or adding LLM-based correction. Those are last resorts and add hallucination risk.

## Anti-patterns to refuse

| Anti-pattern | What's wrong | Correct alternative |
|---|---|---|
| `text.replace("gita", "Bhagavad-gītā")` | Substring match; breaks proper nouns | Word-boundary regex |
| Hardcoded `initial_prompt` inline in transcribe.py | Hard to iterate, can't be tracked in git | Load from `config/sanskrit_seed.txt` |
| Discarding `text_original` after normalization | No audit trail, can't re-run | Always keep both |
| LLM-based "spell correction" of transcripts | Adds hallucination risk | Layer 2 dictionary + fuzzy match |
| Embedding `text_original` and `text_normalized` separately | Doubles storage, low recall gain | Embed only `text_normalized` |
| Converting IAST to Devanagari at query time | Wrong layer — display concern | Store both in glossary, toggle in UI |
| Setting fuzzy threshold to 80% to "catch more errors" | Causes false positives | Stay at 90; expand the dictionary instead |

## Reference

- **`SANSKRIT_VOCAB_METHODOLOGY.md`** — full conceptual framework, iteration protocol, examples
- **`config/sanskrit_seed.txt`** — the natural-prose `initial_prompt` for Whisper
- **`config/normalization.json`** — the wrong→right dictionary
- **`config/glossary.json`** — IAST + Devanagari + gloss for UI tooltips
- **`app/sanskrit/normalize.py`** — Layer 2 implementation
- **`app/sanskrit/glossary.py`** — UI lookup helpers

## Why this matters

Sanskrit terms are not decoration in HH Romapada Swami's lectures — they are precise theological vocabulary. *Śravaṇa* and *smaraṇa* are not interchangeable with "listening" and "remembering." *Paramparā* is not a synonym for "tradition." Getting these terms right is a sign of respect for the lineage and a prerequisite for the search system being trusted by serious devotees.

Every line of code that touches Sanskrit text is an opportunity to either honor or degrade this. The three-layer architecture exists so that we have multiple chances to get it right.
