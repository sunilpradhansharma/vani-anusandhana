# Devotee Search — Pilot Runbook

**Project**: Semantic search over a single teacher's YouTube lectures, returning timestamped video segments in response to devotee questions.

**Pilot scope**: 25 videos from playlist `PLHcKZARxOlxwEEOagGkfJsn7ZUNfxkiS7`.

**Hardware**: MacBook Pro 14-inch, Apple M5, 32 GB RAM.

**Goal of this document**: Give you the mental model and quality checkpoints. You should never have to "trust that it's working" — every step has an observable success criterion.

---

## Pilot at a glance

| Phase | Wall time on M5 | Your time | Output |
|---|---|---|---|
| 0. Setup | 15 min | 15 min | Working environment |
| 1. Inventory | 5 min | 5 min | List of 25 videos with metadata |
| 2. Calibration (3 videos) | ~25 min | 1.5 hours | Tuned Sanskrit prompt |
| 3. Batch transcribe (22 videos) | ~90 min | 15 min | 25 JSON transcripts |
| 4. Chunking + indexing | ~30 min | 30 min | Qdrant collection ready |
| 5. Evaluation (30 queries) | — | 1–2 hours | Go/no-go decision |
| **Total** | **~2.5 hours compute** | **~4 hours focused** | Pilot complete |

You can do the full pilot in **one focused day**.

---

## The seven-stage pilot

### Stage 0 — Environment setup

**What's happening**: Install the tools you need. One time only.

**Tools being installed**:
- `yt-dlp` — downloads YouTube audio
- `ffmpeg` — audio format conversion
- `mlx-whisper` — Apple Silicon-native Whisper (uses GPU + Neural Engine)
- `qdrant` (Docker) — vector database
- Python packages: `sentence-transformers` (for `bge-m3`), `qdrant-client`, `fastapi`

**What "done" looks like**:
- `yt-dlp --version` returns a version
- `mlx_whisper --help` works
- `docker ps` shows Qdrant running on port 6333
- A test Python script can import all required packages

**Common failure modes**:
- Homebrew not installed → install Homebrew first
- Python virtual environment confusion → use `venv` in the project directory, not system Python
- Docker Desktop not running → start it before running Qdrant container

**Estimated total disk usage when done**: ~5 GB (mostly model weights for Whisper + bge-m3 + reranker).

---

### Stage 1 — Playlist inventory

**What's happening**: You need to know what you're transcribing before you start. `yt-dlp` can extract a list of videos from a playlist URL without downloading anything.

**What you'll do**:
1. Run `yt-dlp --flat-playlist --print "%(id)s | %(title)s | %(duration)s"` on the playlist URL
2. Save output to `playlist_inventory.txt`
3. Eyeball it: 25 videos? Reasonable titles? Total duration sensible?

**What "done" looks like**:
- File `playlist_inventory.txt` with 25 lines
- Each line has video ID, title, duration in seconds
- Total duration sum gives you a realistic time budget for transcription

**Why this matters**:
- You'll discover problems early (private videos, deleted videos, age-restricted ones)
- You can pick calibration videos from the title list without watching anything
- You have a permanent record of "the 25" for later reference

**Decision point**: Are these 25 videos topically diverse, or all on one narrow subject? Make a note. If they're all (say) Bhagavad Gītā Chapter 2 lectures, your pilot proves the system works *for that scope*. The full 5,000 will need broader Sanskrit vocab and you should plan to expand the term list when scaling.

---

### Stage 2 — Calibration (the most important stage)

**What's happening**: Before you transcribe all 25 videos, you transcribe 3 to learn what's hard and tune the system. **Skipping this stage is the #1 mistake people make.**

**Why 3 calibration videos, not 5 or 10**:
- 3 is enough to spot the most common Sanskrit transcription errors
- More than 3 is wasted effort before you've tuned the prompt
- Pick them deliberately — see selection criteria below

**Calibration video selection criteria** (pick from your 25):

| Pick | Why |
|---|---|
| **Longest video** | Stresses the system; reveals long-context issues like hallucinated loops |
| **Most Sanskrit-heavy** | Usually a Bhāgavatam or Gītā class with verse recitation |
| **Most conversational** | Q&A or interview-style; different speaking pace, sometimes other voices |

**Step 2a — Baseline transcribe (no Sanskrit prompt)**

Run `mlx-whisper` on the 3 videos with default settings. **Read every transcript carefully.** Open in a text editor, scroll through.

**What you're looking for**:
- Sanskrit terms mis-transcribed (e.g., "Bhāgavatam" → "Bhagatum", "saṅkīrtana" → "sankirtan", "ācārya" → "Acharya" or "ah-charya")
- English-Sanskrit boundaries garbled (e.g., "the bhakti" merged into one word)
- Hallucinated loops where Whisper repeats the same phrase 5–10 times (sign of `condition_on_previous_text` issue or quiet section)
- Word-level timestamps drifting (early words land late)

**What "done" looks like for Step 2a**:
- A `sanskrit_errors.md` file listing every mis-transcribed term you spotted
- Note next to each term: how Whisper transcribed it AND the correct spelling
- 30–60 minutes of careful reading

**Step 2b — Build the Sanskrit prompt**

Compile the corrected terms from `sanskrit_errors.md` into your `initial_prompt`. Whisper's prompt is capped at ~244 tokens (~1000 characters), so be selective: include the most common terms and the ones the model got most wrong.

**Format**: A flowing sentence or two using the terms naturally, NOT a bare comma-separated list. Whisper biases better when the prompt looks like real text.

**Bad prompt** (bare list — works less well):
> Bhāgavatam, ācārya, paramparā, saṅkīrtana, prema-bhakti, dharma...

**Good prompt** (natural prose — works better):
> This is a lecture on Śrīmad-Bhāgavatam by an ācārya in the paramparā, discussing topics like saṅkīrtana, prema-bhakti, the relationship between dharma and bhakti...

**Step 2c — Re-transcribe with the prompt + tune settings**

Run `mlx-whisper` again on the same 3 videos with:
- `initial_prompt` = your tuned string
- `language="en"` (forced, not auto-detected)
- `condition_on_previous_text=False` (critical for spiritual lectures)
- `word_timestamps=True` (required for chunking later)
- `temperature=0` (deterministic)

**What you're comparing**:
- How many Sanskrit errors got fixed?
- Aim for **>70% improvement** before declaring victory
- Are there still systematic errors? Add those to a post-processing dictionary instead

**Decision point**: If quality is still poor on Sanskrit even with prompt tuning, options are:
- Expand the prompt with more terms
- Build a stronger post-processing dictionary
- Consider fine-tuning a Whisper checkpoint on this teacher (advanced, only if needed)

---

### Stage 3 — Batch transcribe the remaining 22

**What's happening**: Run `mlx-whisper` on the other 22 videos with locked-in settings.

**Before you start**:
- Plug in to power (Apple Silicon throttles on battery for sustained ML)
- Disable sleep: open Terminal and run `caffeinate -i &` (kills sleep until you stop it)
- Close other heavy apps (browsers with many tabs especially)
- Open Activity Monitor → Memory tab in another window

**What you're watching for during the run**:
- Memory pressure stays green (32 GB is plenty, but verify)
- No swap usage
- CPU/GPU activity sustained — if it drops to idle, something's wrong
- Each transcription completes without error

**Output structure** (one JSON file per video):
```
data/transcripts/
  video_id_1.json
  video_id_2.json
  ...
```

Each JSON contains:
- `text` — full transcript
- `segments` — list of `{start, end, text}` per Whisper segment
- `words` — list of `{start, end, word, probability}` per word
- Metadata: video_id, title, duration

**What "done" looks like**:
- 22 JSON files (or 25 if you batch all together)
- All files non-empty
- Random spot-check of 3 looks clean

**Common issues**:
- **Hallucinated loops**: Whisper repeats the same phrase 10x in a row. Almost always means `condition_on_previous_text=True`. Set to `False` and re-transcribe that file.
- **Empty segments at start/end**: Music intros, silence. VAD filter should handle this; if not, manually trim audio before transcription.
- **Wrong language detected**: Force `language="en"`. Even one stray Sanskrit verse can flip Whisper into Hindi mode mid-stream.

---

### Stage 4 — Chunking, embedding, indexing

**What's happening**: Convert raw transcripts into searchable vector chunks.

**Step 4a — Sanskrit normalization** (post-processing dictionary)

For every transcript:
- Apply the post-processing dictionary built during calibration
- Save **both** `text_original` and `text_normalized` — keep the original for debugging

**Step 4b — Sentence-aware chunking**

This is where most RAG-over-video systems fail. Don't use fixed time windows.

**Algorithm**:
1. Walk through `segments` in order
2. Accumulate text into a buffer until buffer duration ≥ 60 seconds
3. **Cut on the next sentence boundary** (period, question mark, exclamation point)
4. Save chunk: `{video_id, start, end, text, text_normalized}`
5. Start next chunk with the last 15 seconds of the previous chunk's content (overlap)
6. Continue

**Why sentence-aware**: When the deep-link jumps to 12:34, the devotee should land at the start of a complete thought. Mid-sentence cuts feel jarring and look unprofessional.

**Step 4c — Embedding**

For each chunk:
- Use `BAAI/bge-m3` via `sentence-transformers` (or the FlagEmbedding library)
- Generate **both** dense and sparse vectors (bge-m3 does both natively)
- Embed `text_normalized` (the Sanskrit-corrected version)

**Why bge-m3**:
- Free, runs locally on M5 (CoreML or MPS)
- Multilingual + Devanagari support
- Native hybrid (dense + sparse) — gives you BM25-like keyword search for free
- Competitive quality with paid OpenAI embeddings

**Step 4d — Index in Qdrant**

Create one collection (let's call it `lectures`):
- Vector config: dense (1024-dim) + sparse
- Payload: `video_id, video_title, start_seconds, end_seconds, text_normalized, text_original, lecture_date (if known)`

**What "done" looks like**:
- Qdrant collection contains ~1,500 chunks (25 videos × ~60 chunks each)
- A test query returns reasonable results
- Response time per query <500ms (it should be much faster than this on M5)

---

### Stage 5 — Evaluation (the real test of the pilot)

**What's happening**: This is where you decide whether the system works.

**Step 5a — Write 30 sample devotee questions**

Cover the range of things real devotees would ask:
- Conceptual questions ("What is the difference between dhyāna and dhāraṇā?")
- Practical questions ("How should I set up my altar?")
- Verse-specific questions ("What does the teacher say about Gītā 2.47?")
- Story/example questions ("Tell me about Prahlāda's devotion")
- Procedural questions ("How do I begin japa practice?")
- Edge cases — vague, ambiguous, multi-part

**Source ideas**: Look at FAQ sections of similar teachers' websites, devotee forums, or just brainstorm.

**Step 5b — Run each query, score the top-4 results**

For each query, look at the 4 returned segments. Score each:
- **Useful** (2 points): The transcript snippet directly addresses the question
- **Partial** (1 point): The snippet is on-topic but doesn't quite answer
- **Off-topic** (0 points): Unrelated to the question

**Track in a spreadsheet**: query, top-4 scores, total /8.

**Step 5c — Aggregate and decide**

Calculate:
- **Average score per query** (out of 8)
- **% of queries with at least one Useful result** in top-4 → this is your hit rate
- **% of queries with all four Off-topic** → this is your failure rate

**Pass criteria** (suggested thresholds):
- Average score ≥ 5/8
- Hit rate ≥ 80% (devotee gets at least one good answer 4 out of 5 times)
- Failure rate < 5% (almost never returns total garbage)

**If you pass**: Proceed to scaling decisions (Stage 6).

**If you don't pass**: Diagnose. Common causes:
- Sanskrit errors not fixed → improve normalization dictionary
- Chunks too short or too long → adjust window size
- Reranker missing context → check if you're actually reranking
- Topic gap → your 25 videos don't cover the questions you're asking; this is a *scope* issue not a system issue

---

### Stage 6 — Decisions before scaling to 5,000

**Three questions to answer based on pilot results**:

**Q1: Did the pilot achieve >80% hit rate?**
- Yes → architecture works, scale with confidence
- No → fix issues on pilot before scaling (10x cheaper to fix at 25 videos than 5,000)

**Q2: Are there topic gaps in the 25 that the full 5,000 will fill?**
- Likely yes — note which Sanskrit terms might appear in the larger corpus that didn't appear in the pilot
- Plan to expand the Sanskrit prompt + post-processing dictionary as you encounter new scriptures/topics

**Q3: How long will full transcription take on M5?**
- 5,000 videos × ~60 min × ~12x realtime = ~420 hours = ~17–18 days continuous
- Realistic plan: run nights + weekends over 4–6 weeks, your laptop is your daily driver during the day
- Alternative: rent a GPU for ~5 days if you want it done in a week (~$200)

**Q4: Local serving or VPS?**
- Local: free, you own everything, but uptime depends on home internet + Mac availability
- Small VPS ($10/month): public uptime, low operational burden
- Hybrid: index built locally, served from VPS — best of both worlds

---

## Quality control checkpoints

These are the moments you stop and verify before continuing. Don't skip.

| Checkpoint | When | What to verify |
|---|---|---|
| **CP1** — Setup works | After Stage 0 | All tools install, Qdrant accessible, Python imports succeed |
| **CP2** — Inventory matches | After Stage 1 | 25 videos in playlist, none private/deleted, total duration realistic |
| **CP3** — Baseline transcripts readable | After Stage 2a | Transcripts are coherent English, Sanskrit errors notable but not catastrophic |
| **CP4** — Sanskrit prompt helps | After Stage 2c | >70% of errors from CP3 are fixed |
| **CP5** — Batch quality consistent | After Stage 3 | 3 random transcripts look as good as the calibration ones |
| **CP6** — Chunks feel coherent | After Stage 4b | Read 5 random chunks; each is a complete thought, not mid-sentence |
| **CP7** — Retrieval works | After Stage 4d | Test query returns plausible top-4 in <500ms |
| **CP8** — System achieves quality bar | After Stage 5 | Hit rate ≥ 80%, average score ≥ 5/8 |

---

## Things specific to a 25-video Sanskrit/spiritual pilot

**The Sanskrit term list is the highest-leverage asset.** A great list improves transcription, retrieval, and devotee experience all at once. Treat it like a permanent project asset — version control it, grow it over time, never throw away.

**Spot the teacher's signature vocabulary.** Every spiritual teacher has 50–100 phrases they use constantly. Get those right and 80% of the perceived quality is solved.

**Verse references matter.** If the teacher quotes "Bhagavad-gītā 2.47" or "Bhāgavatam 1.2.6", make sure the transcript captures the reference. Devotees will search by verse number. Add common verse formats to your normalization (e.g., "Gita 2.47" → "Bhagavad-gītā 2.47").

**English vs. Sanskrit dual indexing.** Many devotees will type "bhakti" but the teacher might say "devotional service" in some places and "bhakti" in others. Both should retrieve. Hybrid search (dense + sparse) handles this naturally.

**Don't perfect on edge cases.** Spend your tuning effort on the common 80% of queries. The 20% of weird/edge questions can be addressed in a second pass.

---

## What changes when you scale to 5,000

**Won't change**:
- Architecture
- Sanskrit prompt (just expand it)
- Chunking strategy
- Embedding model
- Vector DB
- Reranker

**Will change**:
- Transcription time: from 1.5 hours to ~17 days continuous (or ~5 days on rented GPU)
- Vector DB size: from ~50 MB to ~10 GB (still fits on M5 easily)
- Query latency: barely (Qdrant scales well; expect still <1s)
- Sanskrit term list: probably 2–3x larger as new scriptures/topics enter
- Need for systematic error tracking: critical at 5,000 scale

**Cost estimate at full scale**:
- One-time: $0 if you transcribe locally, ~$200 if rented GPU
- Monthly: $10 VPS if you want public uptime; $0 if hosted on your Mac
- Yearly domain: ~$12

**Total project cost ceiling for a fully deployed public system**: ~$300 one-time + ~$120/year. Eminently affordable for any spiritual non-profit.

---

## Project files structure (recommended)

```
devotee-search/
├── PILOT_RUNBOOK.md                  ← this file
├── CLAUDE_CODE_PROMPTS.md            ← prompts to paste into Claude Code
├── SANSKRIT_VOCAB_METHODOLOGY.md     ← how to build the term list
├── data/
│   ├── playlist_inventory.txt        ← Stage 1 output
│   ├── audio/                        ← downloaded MP3s (delete after transcription)
│   ├── transcripts/                  ← JSON outputs from Whisper (KEEP FOREVER)
│   ├── chunks/                       ← chunked + normalized JSON (rebuildable)
│   └── sanskrit_errors.md            ← living document of Sanskrit issues
├── config/
│   ├── sanskrit_prompt.txt           ← Whisper initial_prompt
│   └── normalization_dict.json       ← post-processing replacements
├── eval/
│   ├── sample_questions.md           ← 30 devotee questions
│   └── results.csv                   ← scores from Stage 5
└── (later: app/, frontend/, etc.)
```

**Backup priority**: `data/transcripts/` and `config/sanskrit_prompt.txt` and `config/normalization_dict.json`. Everything else is rebuildable.

---

## Final note before you start

This pilot exists to **save you from making a 5,000-video mistake**. Every shortcut you take here costs ~200x more later. Read every transcript during calibration. Score every query during evaluation. Trust the checkpoints.

When the pilot passes, you'll have something most RAG projects don't: real evidence the system works for the actual people who'll use it. That confidence is worth half a day of careful work.
