# Sanskrit Vocabulary Methodology

**Why this document exists**: Of all the pieces of this project, the Sanskrit term list has the highest leverage. Get it right and 80% of perceived quality is solved. This document tells you how to build, test, and grow it systematically.

---

## The three layers of Sanskrit handling

The system handles Sanskrit terms at three layers. Each layer fixes errors the previous layer missed.

```
┌──────────────────────────────────────────────────────────────┐
│  Layer 1: Whisper initial_prompt                             │
│  ─────────────────────────────────                           │
│  Biases the model TOWARD seeing Sanskrit terms.              │
│  Works at transcription time. Best at fixing diacritics.     │
│  Limitation: max ~240 tokens, so be selective.               │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│  Layer 2: Post-processing normalization dictionary           │
│  ──────────────────────────────────────────────              │
│  Fuzzy match-and-replace AFTER transcription.                │
│  Catches errors the prompt missed.                           │
│  No size limit. Grows over the project lifetime.             │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│  Layer 3: Dual indexing (original + normalized)              │
│  ─────────────────────────────────────────────               │
│  Index BOTH the corrected and uncorrected text.              │
│  Lets devotees retrieve regardless of how they spell it.     │
│  Free side-effect of hybrid search (BM25 + embeddings).      │
└──────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Building the Whisper `initial_prompt`

### How Whisper's prompt works

The `initial_prompt` is text Whisper "pretends" came right before the audio. It biases token probabilities toward terms appearing in the prompt. It does NOT teach Whisper new words — it only nudges it toward words it already knows.

**Key implications**:
- Common Sanskrit terms (Krishna, dharma, yoga) — Whisper already knows; barely needs nudging
- Diacritical Sanskrit (Kṛṣṇa, ācārya, Bhāgavatam) — Whisper *knows* both forms; the prompt makes it pick the right one
- Rare Sanskrit (a specific teacher's coined phrase) — prompt may not help; need Layer 2

### Format that works best

**Bad** (bare list — Whisper interprets as context but weakly):
```
Bhāgavatam, ācārya, paramparā, saṅkīrtana, prema, bhakti, dharma, jīva, māyā
```

**Good** (natural prose — Whisper integrates the terms more strongly):
```
This is a lecture on Śrīmad-Bhāgavatam by an ācārya in the Gauḍīya paramparā, 
discussing topics like saṅkīrtana, prema-bhakti, the role of guru, and the 
relationship between dharma, jīva, and māyā as taught by Śrīla Prabhupāda.
```

The prose form gets ~20-30% better diacritical accuracy in our experience.

### Token budget

- Whisper's `initial_prompt` cap: **~244 tokens** (about 1000 characters of English)
- Going over silently truncates from the start → losing your most important terms
- **Stay around 800 characters to be safe**

### What to put in the prompt

Priority order:

1. **Teacher-specific signature terms** (what they say constantly)
2. **Scriptures they teach from** (Bhāgavatam, Gītā, Caitanya-caritāmṛta, etc.)
3. **Lineage / paramparā references** (Gauḍīya, Madhva, Śrī Sampradāya)
4. **Common diacritical terms** (ācārya, jīva, māyā)
5. **Verse format hints** (e.g., "as stated in chapter 2 verse 47")

### What NOT to put in the prompt

- Common English words (waste of tokens)
- Personal names you don't expect to recur
- Long verse quotations (eats budget; Whisper handles these poorly anyway)

### Iterating the prompt

The prompt is never "done". After the calibration round:
- Identify the top 10 errors that the prompt fixed
- Identify the top 10 errors it didn't fix
- For the un-fixed ones: are they similar to terms in the prompt? Add variants
- Are they truly rare? Move them to Layer 2 (normalization dictionary)

**Test the prompt scientifically**: transcribe the same 3 calibration videos with and without the prompt. Diff the outputs. Count fixes. This is your evidence the prompt works.

---

## Layer 2: The post-processing normalization dictionary

### What it is

A JSON file mapping wrong → right:

```json
{
  "version": "1.0",
  "last_updated": "2026-04-29",
  "corrections": {
    "bhagatam": "Bhāgavatam",
    "bhagwatam": "Bhāgavatam",
    "bhagatum": "Bhāgavatam",
    "ah-charya": "ācārya",
    "acharya": "ācārya",
    "guru tattva": "guru-tattva",
    "sankirtan": "saṅkīrtana",
    "sang kirtan": "saṅkīrtana"
  },
  "verse_patterns": {
    "gita (\\d+) (\\d+)": "Bhagavad-gītā $1.$2",
    "bhagavatam (\\d+) (\\d+) (\\d+)": "Śrīmad-Bhāgavatam $1.$2.$3"
  }
}
```

### How it's applied

Two-pass approach:

**Pass 1 — Exact and fuzzy match replacement**:
- For each transcript, walk through the text
- Apply exact replacements first (case-insensitive)
- Then apply fuzzy matches with `rapidfuzz` at >90% similarity threshold
- Save the replacement map for that transcript (audit trail)

**Pass 2 — Pattern matching for verse references**:
- Run regex patterns from `verse_patterns`
- Standardize formats (e.g., "Gita 2.47", "Gita 2-47", "Gita ch 2 v 47" all → "Bhagavad-gītā 2.47")

### Building the dictionary systematically

**Day 1 (calibration)**:
- After reading 3 baseline transcripts, you'll have ~20-50 entries
- Focus on terms that appeared multiple times — these are the teacher's vocabulary

**Days 2-N (during pilot batch)**:
- After running the full 25, spot-check 3 random transcripts
- Add any new errors you spot
- Re-run normalization on all transcripts (cheap — takes seconds)

**Ongoing (during full 5,000)**:
- Periodic spot-checks of new transcripts
- Add devotee-reported errors (when they search and don't find what they expect)
- Quarterly review of the full dictionary

### Fuzzy matching threshold

`rapidfuzz` similarity threshold of **90%** is a good starting point:
- 95% — too strict; misses real errors
- 90% — sweet spot; catches "bhagatam"/"bhagwatam"/"bhagatum" → "Bhāgavatam"
- 85% — too loose; risk of false positives
- 80% — definitely too loose

### Avoiding cascading errors

**Risk**: Your dictionary has entry `"krishna" → "Kṛṣṇa"`. The teacher says "Krishna's pastimes are wonderful." Normalization runs. Result: "Kṛṣṇa's pastimes are wonderful." Good.

**Risk**: Your dictionary has entry `"gita" → "Bhagavad-gītā"`. The teacher says "He read the Gita this morning." After normalization: "He read the Bhagavad-gītā this morning." Mostly fine.

**Risk**: Your dictionary has entry `"gita" → "Bhagavad-gītā"`. The transcript contains the proper noun "Sangita" (a person's name). After fuzzy normalization: "Sang-Bhagavad-gītā". **Problem.**

**Mitigation**:
- Use word-boundary matching, not substring matching
- Test the dictionary against a held-out transcript before deploying
- Keep a "do not normalize" list for English words that look like Sanskrit fragments
- Always preserve `text_original` so you can audit any weirdness

---

## Layer 3: Dual indexing (free, important)

### The problem

A devotee types "bhagavatam". Your transcripts have "Bhāgavatam" (corrected). Pure embedding search may or may not match — depends on how the embedding model handles diacritics.

### The solution

Index BOTH `text_original` and `text_normalized`:

- **Sparse vector (BM25-like)** is generated from `text_normalized` — handles the corrected form
- **Dense vector (semantic)** is generated from `text_normalized` — handles the corrected form
- The `text_original` is kept in payload (not indexed for search) — useful for debugging and for displaying what Whisper actually heard

For maximum coverage, you can also:
- Generate a third indexing field that's the *transliterated* form (e.g., "bhagavatam" without diacritics) and include it in sparse indexing
- This means a devotee typing any of "bhagavatam", "Bhāgavatam", "Bhagwatam" can hit the same chunks

`bge-m3` does well with diacritics natively, so this third form is often unnecessary. But it's there if you need it.

---

## How to spot Sanskrit errors efficiently

### Reading transcripts: what to look for

Skim, don't read carefully. You're looking for patterns, not perfection.

**Red flags**:
- A word that doesn't look English AND doesn't look like a Sanskrit term you recognize
- A Sanskrit term you expect to see, but in a weird form
- An apparently English word that "sounds like" a Sanskrit term mispronounced
- Repeated tokens (e.g., "the the the") — sign of Whisper hallucination, separate issue
- A word that breaks the sentence's grammar — often a mis-transcribed proper noun

**Examples of subtle errors**:
- "He was a great a-charya" — "ācārya" → "a-charya" (hyphen artifact)
- "the rasa lila" → should be "rāsa-līlā"
- "in Kali yuga" → should be "Kali-yuga" (compound formatting)
- "Prabhu pada" → should be "Prabhupāda" (single word)

### A dedicated 30-minute review per video

For calibration videos, spend 30 minutes per video on Sanskrit error capture. Don't try to be exhaustive — capture what you see. The next pass will catch what you missed.

### Pair it with audio when uncertain

If you're not sure whether a word is mis-transcribed or just unfamiliar, scrub to the timestamp in the YouTube video and listen. Especially useful for verse references — confirm the verse number is correct.

---

## The seed term list (start here)

Before you begin calibration, build a seed term list. This is what every spiritual teacher in the Gauḍīya / Vaiṣṇava tradition will mention:

### Core philosophical terms
ātman, brahman, paramātmā, jīva, jīvātmā, māyā, dharma, adharma, karma, jñāna, vijñāna, bhakti, prema, vairāgya, viveka, mokṣa, mukti, saṁsāra

### Practice terms  
sādhana, sādhaka, japa, kīrtana, saṅkīrtana, śravaṇa, smaraṇa, dhyāna, dhāraṇā, samādhi, upāsanā, sevā, pūjā, ārati

### Lineage terms
guru, ācārya, paramparā, sampradāya, śiṣya, bhakta, vaiṣṇava, Gauḍīya, Madhva, Rāmānuja, Śrī

### Scriptures
Veda, Upaniṣad, Bhagavad-gītā, Śrīmad-Bhāgavatam, Caitanya-caritāmṛta, Brahma-sūtra, Purāṇa, Itihāsa, Mahābhārata, Rāmāyaṇa

### Personalities  
Kṛṣṇa, Rāma, Viṣṇu, Śiva, Brahmā, Caitanya Mahāprabhu, Nityānanda, Rādhā, Lakṣmī, Sītā, Hanumān, Prahlāda, Dhruva, Arjuna

### Concepts unique to bhakti tradition
rasa, līlā, prema-bhakti, vaidhī-bhakti, rāgānuga-bhakti, sambandha, abhidheya, prayojana, sva-rūpa, nitya-siddha, sādhana-siddha, kṛṣṇa-prema

### Common compound markers
-tattva (sambandha-tattva, jīva-tattva), -līlā (kṛṣṇa-līlā, rāsa-līlā), -bhakti (prema-bhakti, vaidhī-bhakti), -vāda (māyā-vāda, advaita-vāda)

**Save this as `config/sanskrit_seed_terms.txt`** and start there. Add teacher-specific terms as you discover them.

---

## How the term list grows over the project lifecycle

| Stage | Action | Expected term count |
|---|---|---|
| Pre-pilot (seed) | Build initial list from this doc | 100-150 |
| After 3 calibration videos | Add observed errors | 150-200 |
| After 25-video pilot | Add common patterns | 200-300 |
| After 500 videos | Major expansion as new scriptures appear | 400-600 |
| After full 5,000 | Mature, comprehensive list | 600-900 |
| Ongoing (devotee feedback) | Add edge cases | +50/year |

Treat this list as a **versioned project asset**. Commit it to git. Tag versions when major updates happen. Never delete entries — only add or refine.

---

## Auditing: how to know your normalization is working

### Metric 1 — Sanskrit precision in calibration

After calibration:
- Manually count Sanskrit terms in 1 video transcript (ground truth)
- Count how many were correctly transcribed
- Calculate: % correct = correct_count / total_sanskrit_count
- **Target: >85% after Layer 1 + Layer 2**

### Metric 2 — Devotee retrieval success on Sanskrit queries

After deployment:
- Track queries containing Sanskrit terms (with or without diacritics)
- Track whether they returned at least one "useful" result (devotee feedback or query reformulation as proxy)
- **Target: >80% Sanskrit-query success rate**

### Metric 3 — Dictionary growth velocity

- Initially you'll add 5-10 entries per video reviewed
- This should taper to 0-2 per video by ~50 videos in
- If the rate isn't tapering, your prompt isn't doing its job — re-tune it

---

## Common pitfalls

**Pitfall 1: Starting too early**
You can't build the perfect prompt before transcribing anything. Don't try. Run baseline first, then iterate. The first prompt is always a draft.

**Pitfall 2: Trying to fix everything at the prompt layer**
The prompt has a ~240-token cap. If you're up against the cap and still missing terms, move them to Layer 2 (no cap there).

**Pitfall 3: Overly aggressive normalization**
Replacing "krishna" → "Kṛṣṇa" sounds harmless. But what about "krishna consciousness" as a movement name? Or someone's surname "Krishnamurthy"? Use word boundaries. Test before deploying.

**Pitfall 4: Forgetting compound words**
"Krishna prema" and "krishna-prema" are the same term but might transcribe differently. Compound formatting needs explicit normalization rules.

**Pitfall 5: Not preserving the original**
Once you normalize, you can't easily un-normalize. Always keep `text_original` alongside `text_normalized`. You'll thank yourself when debugging.

**Pitfall 6: Treating it as a one-time task**
This is the single biggest mistake. The list grows for the life of the project. Build the workflow that makes growth easy (Prompt 4 in CLAUDE_CODE_PROMPTS.md helps with this).

---

## When you have the resources: fine-tuning

If after all of the above your Sanskrit accuracy is still <85%, the next step is fine-tuning a Whisper checkpoint on this teacher's audio. This is significantly more work:

- Need ~5-10 hours of teacher audio with verified transcripts (~10-20 lectures from the pilot, hand-corrected)
- Use Hugging Face's transformers + PEFT for parameter-efficient tuning
- Cost: GPU time, ~$50-100
- Time: 1-2 days of work

For most projects this is overkill. The 3-layer approach above gets you 90%+ of the value at 10% of the effort. **Only fine-tune if calibration shows the prompt + dictionary aren't enough** — and only after the pilot proves the rest of the architecture works.

---

## Final reflection

The Sanskrit vocabulary is the soul of this project. A devotee searching for "ācārya" and getting back lectures about "ah-charya" feels broken. A devotee searching for "Bhagavatam" and getting accurate, well-cited timestamps where the teacher discusses the Bhāgavatam feels like sacred technology working as intended.

Spend the time. Build the list with care. Update it with intention. The teacher's words deserve nothing less.
