# Claude Code Prompts — Devotee Search Pilot

**How to use this file**:
- Each prompt is a complete, self-contained instruction to Claude Code
- Paste them **one at a time, in order**
- Each prompt is designed for **PLAN mode** — Claude Code will produce a plan and code; you review, accept, and move on
- Wait for one phase to complete (and you to verify the checkpoint) before pasting the next
- The PILOT_RUNBOOK.md describes the *why* behind each phase; use it as context when reviewing what Claude Code produces

**Reference the runbook when you start a new Claude Code session**:
> "Read PILOT_RUNBOOK.md for full context on this project before starting."

---

## Prompt 0 — Project setup and environment

```
Initialize a new project called `devotee-search` for a YouTube semantic search 
pilot. The full architecture and rationale is in PILOT_RUNBOOK.md (read it first).

For this prompt, set up the development environment only:

1. Create the directory structure exactly as described in the runbook's 
   "Project files structure" section.

2. Create a Python 3.11+ virtual environment in `.venv/` and a `requirements.txt` 
   with these pinned dependencies:
   - mlx-whisper (latest)
   - yt-dlp (latest)
   - sentence-transformers (>=2.7)
   - FlagEmbedding (for bge-m3 dense+sparse)
   - qdrant-client (>=1.9)
   - fastapi
   - uvicorn
   - pydantic
   - python-multipart
   - tqdm
   - rapidfuzz (for Sanskrit fuzzy normalization later)

3. Create a `Makefile` with these targets:
   - `setup` — install deps, pull Qdrant Docker image, start Qdrant container
   - `qdrant-up` / `qdrant-down` — start/stop Qdrant
   - `clean-audio` — delete data/audio/ contents (after transcription succeeds)

4. Create a `docker-compose.yml` for Qdrant on port 6333, with persistent volume 
   `./qdrant_storage`.

5. Create a `verify_setup.py` script that imports every key library, connects to 
   Qdrant, loads bge-m3, and prints "✅ environment ready" if all succeed.

6. Add a `.gitignore` excluding `.venv/`, `data/audio/`, `qdrant_storage/`, 
   `__pycache__/`, `*.pyc`, `.DS_Store`.

7. Create a placeholder `README.md` summarizing the project in 5 lines.

Do NOT install dependencies or start Docker yet — just create files. I will run 
`make setup` myself after reviewing.

Hardware target: MacBook Pro M5 (Apple Silicon), 32 GB RAM, macOS.
```

**After this prompt**: Run `make setup` yourself. Run `python verify_setup.py`. Confirm "✅ environment ready" before continuing.

---

## Prompt 1 — Playlist inventory

```
Refer to PILOT_RUNBOOK.md Stage 1.

Create a script `scripts/01_inventory_playlist.py` that:

1. Takes a playlist URL as a command-line argument (default: 
   "https://youtube.com/playlist?list=PLHcKZARxOlxwEEOagGkfJsn7ZUNfxkiS7")

2. Uses yt-dlp's Python API (NOT subprocess — use `yt_dlp.YoutubeDL` directly) 
   with `extract_flat=True` to get video metadata without downloading.

3. For each video, extracts:
   - video_id
   - title  
   - duration_seconds
   - upload_date (if available)

4. Writes output to `data/playlist_inventory.json` (structured, for downstream use)
   AND `data/playlist_inventory.txt` (human-readable, one video per line in 
   format: `<id> | <duration_mmss> | <title>`).

5. Prints to stdout:
   - Total video count
   - Total duration (HH:MM:SS)
   - Min/max/median video length
   - Any private/deleted videos that couldn't be accessed
   - Estimated transcription wall time on M5 assuming 12x realtime

Add basic error handling — if the playlist is private or unavailable, fail with 
a clear message.

Test with a small playlist first if possible. The pilot playlist has 25 videos.
```

**After this prompt**: Run the script. Open `playlist_inventory.txt`. Confirm 25 videos exist, durations look reasonable, no private videos. **This is Checkpoint CP2.**

---

## Prompt 2 — Audio download

```
Refer to PILOT_RUNBOOK.md Stage 2 prep and Stage 3.

Create a script `scripts/02_download_audio.py` that:

1. Reads `data/playlist_inventory.json`.

2. Accepts a `--limit N` flag (so we can download just 3 calibration videos 
   first) and a `--ids ID1,ID2,...` flag for specific video IDs.

3. Downloads audio-only (mp3, best quality) for each video to 
   `data/audio/<video_id>.mp3`.

4. Uses yt-dlp Python API with these options:
   - format: 'bestaudio/best'
   - postprocessors: extract to mp3
   - audio-quality: 0 (best)
   - download-archive: data/audio/.archive (so re-running skips already-downloaded)
   - no playlist (we pass individual video URLs derived from IDs)

5. Shows a progress bar (tqdm) across all videos.

6. After download, writes a `data/audio/manifest.json` listing 
   {video_id, audio_path, file_size_mb, audio_duration_seconds (from ffprobe)}.

7. Prints summary: count downloaded, count skipped (already in archive), 
   total disk used.

Robustness:
- If a video is unavailable (private/deleted/region-locked), skip it and log 
  the error, don't crash the batch.
- If yt-dlp throws on one video, continue with the others.

Important: do NOT delete audio files yet. We need them through Stage 3 batch 
transcription. There's a separate `make clean-audio` target for after.
```

**After this prompt**: Run `python scripts/02_download_audio.py --limit 3` (downloads 3 for calibration). Verify 3 mp3 files in `data/audio/`. **Pick which 3 videos** — see the runbook's calibration selection criteria.

---

## Prompt 3 — Baseline transcription (calibration, no Sanskrit prompt)

```
Refer to PILOT_RUNBOOK.md Stage 2a.

Create a script `scripts/03_transcribe.py` using mlx-whisper that:

1. Accepts these flags:
   - `--ids ID1,ID2,...` — specific video IDs (required)
   - `--prompt-file PATH` — path to Sanskrit prompt file (optional, default: none)
   - `--model NAME` — Whisper model (default: "mlx-community/whisper-large-v3")
   - `--output-suffix SUFFIX` — appends to output filename for A/B comparison 
     (e.g., "baseline" → `<id>.baseline.json`)

2. For each video ID:
   - Read audio path from `data/audio/manifest.json`
   - Run mlx-whisper with these settings:
     - language="en" (forced)
     - word_timestamps=True
     - condition_on_previous_text=False (CRITICAL — prevents loops on long lectures)
     - temperature=0
     - vad_filter equivalent if available in mlx-whisper (check API)
     - initial_prompt=<contents of prompt file if provided>
   - Save full output as JSON to `data/transcripts/<id>[.<suffix>].json`
   - JSON should preserve: text, segments (with start/end), words (with timestamps)
   - Include metadata: video_id, title, audio_duration, transcription_duration, 
     model_name, prompt_used (the actual prompt text or null)

3. Show progress: "[1/3] transcribing <id> (<duration>m)... done in <wall>m 
   (<realtime_factor>x)"

4. After all transcriptions, print summary table.

5. Save logs to `data/transcripts/transcribe.log` with timestamps.

Hardware notes:
- mlx-whisper uses Apple Silicon GPU/Neural Engine automatically on M-series
- M5 should achieve ~12x realtime on large-v3
- Recommend running with the laptop plugged in; suggest user runs `caffeinate -i` 
  in another terminal during long batches

Do NOT use faster-whisper — it's CPU-only on Mac and will be much slower.
```

**After this prompt**: Run `python scripts/03_transcribe.py --ids <ID1>,<ID2>,<ID3> --output-suffix baseline`. Wait ~25 minutes. Open the 3 JSON files (or pretty-print them). **Read the transcripts carefully.** This is Stage 2a — your goal is to spot Sanskrit errors.

---

## Prompt 4 — Sanskrit error logging helper

```
Refer to SANSKRIT_VOCAB_METHODOLOGY.md (read it first).

Create a script `scripts/04_log_sanskrit_errors.py` that helps me build the 
Sanskrit error list quickly:

1. Reads a baseline transcript JSON (`--input PATH`).

2. Extracts the full text and shows it in chunks of ~30 seconds with timestamps, 
   in a terminal-friendly format. Each chunk separated by blank line and a 
   timestamp header like `[12:34 → 13:04]`.

3. After displaying, opens an interactive prompt:
   "Enter mis-transcribed terms (format: WRONG => CORRECT, blank line to finish):"

4. Each entry the user types is appended to `config/sanskrit_errors.md` in 
   format:
   ```
   ## From video <id> at <timestamp>
   - `Bhagatum` => `Bhāgavatam`
   - `Acharya` => `ācārya`
   ```

5. Also maintains a deduplicated `config/normalization_dict.json` mapping wrong 
   → right.

6. After session, prints how many new entries were added.

Goal: make it fast to read transcripts and capture errors as I go, instead of 
juggling separate files.
```

**After this prompt**: Run `python scripts/04_log_sanskrit_errors.py --input data/transcripts/<id>.baseline.json` for each of the 3 calibration videos. This is the **most important manual work in the pilot**. Take your time.

---

## Prompt 5 — Build Sanskrit prompt and re-transcribe

```
Refer to PILOT_RUNBOOK.md Stage 2b and 2c.

Create a script `scripts/05_build_sanskrit_prompt.py` that:

1. Reads `config/normalization_dict.json` (the corrections I logged in Prompt 4).

2. Reads `config/sanskrit_seed_terms.txt` (a manually-curated list of common 
   Sanskrit terms for this teacher — I'll create this file separately).

3. Combines them and generates a natural-prose `initial_prompt` for Whisper:
   - Maximum ~240 tokens (~1000 chars) — Whisper's prompt cap
   - Uses terms in flowing sentences, NOT a comma-separated list
   - Prioritizes terms with diacritics (Bhāgavatam, ācārya) since those are 
     hardest for Whisper
   - Format example: "This is a lecture on Śrīmad-Bhāgavatam by an ācārya in 
     the paramparā, discussing topics including saṅkīrtana, prema-bhakti..."

4. Writes the prompt to `config/sanskrit_prompt.txt`.

5. Prints:
   - The generated prompt
   - Token count estimate
   - Number of unique terms it covers

After this, I'll re-run the transcription on the same 3 calibration videos 
using the prompt:
`python scripts/03_transcribe.py --ids <same 3> --prompt-file config/sanskrit_prompt.txt --output-suffix tuned`

Then I'll diff the baseline vs tuned outputs to see how much improved.

Also create a script `scripts/05b_diff_transcripts.py` that takes two JSON 
transcripts (baseline + tuned) and shows a side-by-side comparison of 
differences, highlighting Sanskrit term improvements specifically.
```

**After this prompt**: Generate the prompt, re-transcribe, run the diff. **This is Checkpoint CP4** — verify >70% of Sanskrit errors got fixed. If not, expand the seed terms list and retry.

---

## Prompt 6 — Batch transcribe remaining 22

```
Refer to PILOT_RUNBOOK.md Stage 3.

I'm now ready to transcribe the remaining 22 videos with the locked-in tuned 
settings.

1. Use the existing `scripts/03_transcribe.py` and `scripts/02_download_audio.py`.

2. First download remaining 22 audio files:
   `python scripts/02_download_audio.py` (no --limit, downloads all not yet in archive)

3. Then transcribe all 22:
   `python scripts/03_transcribe.py --ids <22 IDs> --prompt-file config/sanskrit_prompt.txt`
   (no --output-suffix this time; these are the canonical transcripts)

Help me with:

A. Generate the exact command line, with the 22 video IDs read from 
   `data/playlist_inventory.json` MINUS the 3 calibration IDs (which I'll specify).

B. Provide a short shell script `scripts/06_batch_transcribe.sh` that:
   - Sets up `caffeinate -i` to prevent sleep
   - Logs start time, end time, total duration to `logs/batch_transcribe.log`
   - Runs the transcription
   - Sends a macOS notification when done (`osascript -e 'display notification...'`)
   - Optionally plays a sound on completion

C. After transcription, run a sanity check script `scripts/06b_validate_transcripts.py` 
   that verifies for each output:
   - File exists and is valid JSON
   - text field is non-empty and >100 characters
   - No segment has duration > 30 seconds (sign of a stuck transcription)
   - Word timestamps are present and monotonically increasing
   - Total transcript duration is within 10% of audio duration
   - Print summary: how many transcripts passed, which failed and why
```

**After this prompt**: Kick off the batch (~90 min on M5). When done, run validation. **This is Checkpoint CP5.** Re-transcribe any that failed.

---

## Prompt 7 — Chunking with sentence-aware logic

```
Refer to PILOT_RUNBOOK.md Stage 4a and 4b.

Create a script `scripts/07_chunk_transcripts.py` that:

1. Reads all JSON files in `data/transcripts/` (skip files with .baseline. or 
   .tuned. suffixes — only canonical names).

2. For each transcript:
   a. Apply Sanskrit normalization using `config/normalization_dict.json`:
      - Use rapidfuzz for fuzzy matching of close-but-not-exact misspellings
      - Threshold: only auto-replace if similarity > 90%
      - Save BOTH `text_original` and `text_normalized` for every chunk
   
   b. Build sentence-aware chunks using this algorithm:
      - Walk through `segments` in order
      - Accumulate text into a buffer
      - When buffer duration >= 60 seconds, look for the next sentence boundary 
        (`.`, `?`, `!`, or end of segment)
      - Cut chunk there, save it
      - Start next chunk with the LAST 15 seconds of content from the previous 
        chunk (overlap)
      - Continue
   
   c. For each chunk, record:
      - chunk_id (uuid or hash)
      - video_id
      - video_title
      - start_seconds (float)
      - end_seconds (float)
      - duration_seconds
      - text_original
      - text_normalized
      - word_count
   
3. Save chunks to `data/chunks/<video_id>.chunks.json` (per-video files for 
   easier debugging).

4. Also save a single `data/chunks/all_chunks.jsonl` (one chunk per line) for 
   easy ingestion into Qdrant.

5. Print summary: total chunks across all videos, mean/median chunk duration, 
   min/max chunk duration, mean word count.

6. Include a `--inspect <video_id>` flag that pretty-prints the chunks of one 
   video for manual review.

Quality check: I should be able to read a chunk and feel like it's a complete 
thought, not a mid-sentence cut.
```

**After this prompt**: Run chunking. Then `python scripts/07_chunk_transcripts.py --inspect <some_id>` and **read 5 random chunks**. **This is Checkpoint CP6.** Each chunk should feel coherent.

---

## Prompt 8 — Embeddings and Qdrant indexing

```
Refer to PILOT_RUNBOOK.md Stage 4c and 4d.

Create a script `scripts/08_index_chunks.py` that:

1. Reads `data/chunks/all_chunks.jsonl`.

2. Loads BAAI/bge-m3 via FlagEmbedding (NOT plain sentence-transformers — we 
   need both dense and sparse from one pass):
   ```python
   from FlagEmbedding import BGEM3FlagModel
   model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)
   ```
   This runs on Apple Silicon GPU via Metal/MPS.

3. For each chunk, embed the `text_normalized` field. Use batched embedding 
   (batch_size=32) for efficiency.

4. Connect to Qdrant at localhost:6333 (the docker-compose container).

5. Create a collection named `lectures` if it doesn't exist:
   - Dense vector: 1024 dim, COSINE distance
   - Sparse vector: enabled
   - On-disk storage to keep RAM usage low (we'll have plenty of headroom but 
     good practice)

6. Upsert chunks in batches (batch_size=64):
   - Point ID: deterministic hash of chunk_id (so re-runs are idempotent)
   - Dense vector: from bge-m3
   - Sparse vector: from bge-m3
   - Payload: video_id, video_title, start_seconds, end_seconds, 
     text_normalized, text_original, word_count

7. After indexing, run a diagnostic:
   - Confirm chunk count in Qdrant matches input
   - Run a test query "What is bhakti?" and print top-5 results with scores
   - Print indexing throughput (chunks/sec)

8. Show progress with tqdm.

Performance expectation on M5: ~50-100 chunks/sec embedding, total ~30 sec for 
the pilot's ~1500 chunks.
```

**After this prompt**: Run indexing. Verify the test query returns plausible results. **This is Checkpoint CP7.**

---

## Prompt 9 — Query API with reranking

```
Refer to PILOT_RUNBOOK.md Stage 4 (query pipeline).

Create the query API in `app/main.py`:

1. FastAPI app with one endpoint: `POST /search`
   Request body: `{"query": "string", "top_k": 4}` (default top_k=4)
   Response: `{"query": str, "results": [...]}`

2. Each result item:
   ```json
   {
     "video_id": "...",
     "video_title": "...",
     "youtube_url": "https://www.youtube.com/watch?v=<id>&t=<start>s",
     "start_seconds": 754.2,
     "end_seconds": 815.6,
     "start_formatted": "12:34",
     "end_formatted": "13:35",
     "transcript": "<text_normalized>",
     "score": 0.87
   }
   ```

3. Pipeline:
   a. Embed query with bge-m3 (dense + sparse)
   b. Hybrid search Qdrant — retrieve top 20 candidates
   c. Rerank with BAAI/bge-reranker-v2-m3 (load once at app startup)
   d. Merge adjacent results from same video if gap < 30 seconds
   e. Return top 4 after merging

4. Load all models at app startup, not per-request:
   - bge-m3 embedding model
   - bge-reranker-v2-m3 cross-encoder
   - Qdrant client
   - Print "✅ models loaded" when ready

5. Add CORS middleware (allow all for now — we'll lock down later).

6. Add a `GET /health` endpoint returning {status, qdrant_chunk_count, 
   models_loaded}.

7. Add a simple `GET /` endpoint returning HTML — basic search box that POSTs 
   to /search via JS and renders results as cards. Vanilla HTML/CSS/JS, no 
   framework. Each card shows:
   - Video title (link to YouTube with t= timestamp)
   - "12:34 — 13:35" timestamp range
   - Transcript snippet (the text_normalized)
   - Embedded YouTube iframe player (optional, with start time set)

8. Run with `uvicorn app.main:app --reload --port 8000`.

Performance target: <1.5 seconds end-to-end on M5.
```

**After this prompt**: Run the server. Open `http://localhost:8000`. Test a few queries. Looks reasonable? Continue to evaluation.

---

## Prompt 10 — Evaluation harness

```
Refer to PILOT_RUNBOOK.md Stage 5.

Create the evaluation system:

1. Template file `eval/sample_questions.md` with these sections (left empty for 
   me to fill):
   - Conceptual questions (10 questions)
   - Practical questions (5 questions)
   - Verse-specific questions (5 questions)
   - Story/example questions (5 questions)
   - Procedural questions (5 questions)
   
   Include 3 example questions in each section as guidance — phrased as a real 
   devotee would ask, not as a search query.

2. Script `scripts/10_run_evaluation.py` that:
   a. Reads the questions from sample_questions.md (parsing the markdown)
   b. For each question, calls the local API at localhost:8000/search
   c. Saves results to `eval/raw_results.json` (full top-4 for each query)
   d. Generates `eval/scoring_template.csv` with columns:
      query, result_1_score, result_2_score, result_3_score, result_4_score, 
      total, notes
      Pre-fills query column. Score columns blank for me to fill manually 
      (scoring criteria: 2=useful, 1=partial, 0=off-topic).
   e. Generates `eval/raw_results.html` — a static HTML page showing each 
      query with its top-4 results in cards (same format as the main UI), so 
      I can review visually and score in the CSV.

3. Script `scripts/10b_analyze_eval.py` that reads the FILLED-IN scoring_template.csv 
   and computes:
   - Mean score per query (out of 8)
   - Hit rate: % of queries with at least one score-2 result
   - Failure rate: % of queries where all 4 results are score-0
   - Per-section breakdown (conceptual vs practical vs verse-specific etc.)
   - Bottom 5 queries (worst performance) — to investigate what went wrong
   - Top 5 queries (best performance)
   - Decision: "✅ PASS" if mean ≥ 5/8 AND hit rate ≥ 80% AND failure rate < 5%, 
     else "❌ FAIL" with explanation
```

**After this prompt**: Spend 1–2 hours scoring honestly. Run the analyzer. **This is Checkpoint CP8.** Pass → proceed to scaling. Fail → diagnose and iterate before scaling.

---

# Repository setup prompts (run anytime — these don't depend on pilot results)

These prompts produce the **public-facing parts of the repository**: README, architecture diagram, LICENSE, CONTRIBUTING guide, issue templates, and `.gitignore`. They can run in parallel with the pilot — do them whenever you're ready to push the repo public. Recommended order: A → B → C → D → E.

The repo identity is locked in:
- **GitHub URL slug**: `vani-anusandhana`
- **Display name**: vāṇī-anusandhāna (with diacritics)
- **Devanagari**: वाणी-अनुसन्धान
- **License**: AGPL-3.0
- **Description (short)**: "Semantic search over a single spiritual teacher's YouTube lectures. Devotees ask questions, get back the exact moments — with deep-links, transcripts, timestamps. Local-first, zero hallucinations."

---

## Prompt A — Architecture diagram (SVG + PNG)

```
Read PILOT_RUNBOOK.md for architecture context before starting.

Create the architecture diagram using Mermaid (NOT hand-written SVG). 
GitHub renders Mermaid natively in README.md — no image file needed, 
no PNG export, no cairosvg. This is intentional: hand-written SVG 
diagrams are extremely token-expensive to generate and Mermaid covers 
this need in 1-2 minutes instead of 15-20.

Create a single file `architecture.md` containing the Mermaid source. 
This file will be referenced when generating the README in Prompt B 
(the same Mermaid block will be embedded directly in README.md).

Mermaid diagram requirements:

1. Use `graph TD` (top-down flow).

2. Two subgraphs:
   - subgraph "Ingestion pipeline (one-time, local)"
   - subgraph "Query pipeline (real-time)"

3. Ingestion nodes (in order, with line breaks via <br/>):
   YT[YouTube playlist] --> DL[yt-dlp<br/>audio extract]
   DL --> WH[mlx-whisper large-v3<br/>+ Sanskrit prompt]
   WH --> TR[Transcript JSON<br/>word timestamps]
   TR --> CH[Sentence chunking<br/>~60s, 15s overlap]
   CH --> SN[Sanskrit normalize<br/>fuzzy dictionary]
   SN --> EM[bge-m3 embed<br/>dense + sparse]
   EM --> QD[(Qdrant<br/>hybrid index)]
   
   Note: QD uses cylinder shape `[(...)]` to indicate database.

4. Query nodes (in order):
   DV[Devotee asks] --> API[FastAPI<br/>/search endpoint]
   API --> QE[bge-m3 embed<br/>query vectorize]
   QE --> QS[(Qdrant hybrid search<br/>top-20)]
   QS --> RR[Cross-encoder rerank<br/>bge-reranker-v2-m3]
   RR --> MG[Merge adjacent<br/>same video <30s gap]
   MG --> R4[Top 4 results<br/>YouTube deep-link + range]
   R4 --> DV2[Devotee listens<br/>jumps to t=754s]

5. Persistence link between pipelines (dashed arrow):
   QD -.->|Persisted on disk| QS

6. Color classes (use Mermaid classDef):
   classDef compute fill:#E6F1FB,stroke:#185FA5,color:#042C53
   classDef storage fill:#EEEDFE,stroke:#534AB7,color:#26215C
   classDef quality fill:#FAECE7,stroke:#993C1D,color:#4A1B0C
   classDef data fill:#E1F5EE,stroke:#0F6E56,color:#04342C
   classDef output fill:#FAEEDA,stroke:#854F0B,color:#412402
   classDef devotee fill:#F1EFE8,stroke:#5F5E5A,color:#2C2C2A

7. Apply classes to nodes:
   class DL,WH,EM,API,QE compute
   class QD,QS storage
   class SN,RR,MG quality
   class TR,CH data
   class R4 output
   class YT,DV,DV2 devotee

8. Save the COMPLETE Mermaid source as `architecture.md` with this structure:
   - Markdown title: "# Architecture"
   - Brief 2-sentence description of the two pipelines
   - The Mermaid code block (```mermaid ... ```)
   - Below the diagram, a small "Color encoding" legend in markdown table 
     format showing the 6 role categories

Verification before declaring success:
- Mentally render the Mermaid source — does the flow make sense?
- Both pipelines visible? ✓
- Persistence arrow connects QD to QS? ✓
- All 16 nodes have classes assigned? ✓
- No syntax errors (matched brackets, proper arrow syntax)?  ✓

This entire prompt should complete in 1-2 minutes. If you find yourself 
"thinking" for more than 3 minutes without producing output, stop and 
ask me for clarification — something has gone wrong.

Do NOT generate SVG. Do NOT install cairosvg. Do NOT create PNG files. 
Mermaid only.
```

**After this prompt**: Open `architecture.md` and confirm the Mermaid code block looks correct. The diagram won't render in a plain text editor, but you can paste the Mermaid source into https://mermaid.live to preview it visually. When you embed it in the README in Prompt B, GitHub will render it natively.

---

## Prompt B — README.md (the public face of the repo)

```
Read PILOT_RUNBOOK.md, SANSKRIT_VOCAB_METHODOLOGY.md, and architecture.md 
(which contains the Mermaid architecture diagram from Prompt A) before 
generating the README.

Create `README.md` for the public GitHub repository. The repo:
- GitHub URL slug: `vani-anusandhana` (clean ASCII)
- Display name: **vāṇī-anusandhāna** (with proper diacritics)
- Devanagari: वाणी-अनुसन्धान
- License: AGPL-3.0
- Target audience: spiritual non-profits, devotees, technically-curious 
  bhaktas, and AI engineers building similar systems for other lineages

The README MUST include these sections, in this order:

1. **Hero section**:
   - Title: `# vāṇī-anusandhāna 🪷`
   - Devanagari subtitle in blockquote: `> **वाणी-अनुसन्धान** — "the careful 
     search through the teacher's transmitted speech"`
   - One-paragraph description of what the system does
   - Status badges: License (AGPL v3), Python 3.11+, Apple Silicon optimized, 
     "AI answers: zero hallucinations"

2. **What it does** — a concrete worked example:
   - Show a sample devotee question (e.g., "What is the difference between 
     śravaṇa and smaraṇa in bhakti practice?")
   - Show what the system returns (4 video segments with deep-links, 
     timestamps, snippets)
   - Bold the line: "No AI-generated answers. No paraphrasing. No 
     hallucinations. The teacher's actual words are the answer."

3. **Why this name** — explain the meaning of *anusandhāna* (contemplative 
   inquiry, not just search) and *vāṇī* (the lineage's transmitted speech). 
   This signals to devotees that this is a project built with care.

4. **Architecture** — embed the SAME Mermaid block from architecture.md 
   directly inside the README using a ```mermaid fenced code block. GitHub 
   renders Mermaid natively, so no image file is needed. Below the diagram, 
   provide a numbered explanation of:
   - 🔄 Ingestion pipeline (6 numbered steps)
   - ⚡ Query pipeline (7 numbered steps)

5. **Design philosophy** — 4 sections explaining the *why*:
   - 🎯 Retrieval only — no LLM-generated answers (theological + trust + cost 
     + simplicity reasons)
   - 🧘 Sanskrit-first transcription (3-layer approach, link to 
     SANSKRIT_VOCAB_METHODOLOGY.md)
   - 💻 Local-first, then optionally cloud
   - 🔄 Sentence-aware chunking, not fixed time windows

6. **Cost summary** — table showing one-time and monthly costs. Total: 
   $0–$200 one-time, $5–10/month. Compare favorably to typical RAG 
   ($1,800+ transcription, $50–200/month inference).

7. **Quick start** — bash code blocks for:
   - Prerequisites (Apple Silicon, 16+ GB RAM, Python 3.11+, Docker, Homebrew)
   - Setup (`git clone`, `make setup`, `python verify_setup.py`)
   - Pilot run (8 numbered command-line steps for the 25-video pilot)

8. **Project structure** — annotated directory tree showing all files and 
   what they do. Include comments next to important files (e.g., 
   "← KEEP, BACKUP" next to data/transcripts/).

9. **Tech stack** — table with Layer | Choice | Why columns. Cover: 
   yt-dlp, mlx-whisper, bge-m3, Qdrant, bge-reranker-v2-m3, FastAPI, 
   vanilla HTML+HTMX (no React), plain Python (no LangChain).

10. **Roadmap** — phased:
    - ✅ Phase 1: Pilot (25 videos)
    - 🚧 Phase 2: Full transcription (5,000 videos, ~17 days local on M5)
    - 📋 Phase 3: Public deployment
    - 🔮 Future: speaker filtering, verse-aware indexing, devotee correction 
      workflow, multilingual UI, mobile PWA, periodic re-indexing

11. **Contributing** — bullet list of how people can help (Sanskrit 
    corrections, sample questions, perf improvements, translations, docs). 
    Reference CONTRIBUTING.md.

12. **License** — AGPL-3.0 with an explanation of *why AGPL specifically*: 
    "The teacher's words belong to the lineage, and improvements to how those 
    words are searched should belong to the community too."

13. **Acknowledgments** — the teacher (without naming, leave generic), the 
    open-source AI community (MLX team, BAAI, OpenAI Whisper, Qdrant), and 
    devotees who test and contribute.

14. **Citation** — BibTeX block for academic use. Use proper LaTeX 
    transliteration: `v\={a}\d{n}\={i}-anusandh\={a}na`.

15. **Footer** — centered:
    - 🪷 **Hare Kṛṣṇa** 🪷
    - "Built with care for devotional communities worldwide."
    - Italic line: "वाणी-अनुसन्धान — the seeker's careful inquiry through the 
      teacher's transmitted voice."

Style notes:
- Use proper diacritics throughout (vāṇī-anusandhāna, śravaṇa, smaraṇa, 
  Bhāgavatam, Kṛṣṇa, ācārya)
- Use emoji section headers sparingly: 🪷 🎯 🧘 💻 🔄 ✅ 🚧 📋 🔮
- Tables wherever data has structure (cost, tech stack)
- Code blocks for all commands
- Bold for emphasis on key claims
- Replace `YOUR_USERNAME` placeholder in clone commands and citation URLs

Length target: ~400-500 lines. Comprehensive but scannable.
```

**After this prompt**: Read the README. Verify all section anchors work, code blocks are correctly fenced, the architecture image renders. Search for `YOUR_USERNAME` and either replace with your handle or leave for later customization.

---

## Prompt C — LICENSE file (AGPL-3.0)

```
Add the AGPL-3.0 license to the repo:

1. Download the official AGPL-3.0 license text from the GNU website:
   https://www.gnu.org/licenses/agpl-3.0.txt
   
2. Save it as `LICENSE` (no extension) in the repo root.

3. Verify the file:
   - Starts with "GNU AFFERO GENERAL PUBLIC LICENSE"
   - Contains "Version 3, 19 November 2007"
   - Is approximately 34 KB (full license text)
   - Has Unix line endings (LF, not CRLF)

4. Also create `NOTICE.md` in the root containing:
   - Project name: vāṇī-anusandhāna
   - Copyright line: `Copyright (C) 2026 [Your name or organization]`
   - License: AGPL-3.0-or-later
   - A 2-3 line statement of intent: "This software is built to serve 
     devotional communities. The AGPL ensures that improvements made to 
     this system — when deployed as a service — flow back to the community 
     of devotees and developers who use it."

Do NOT modify the LICENSE text itself — it must be the verbatim AGPL-3.0.
```

**After this prompt**: Customize NOTICE.md with your actual name or organization. The LICENSE file should be untouched.

---

## Prompt D — CONTRIBUTING.md + issue/PR templates

```
Create the contribution scaffolding:

1. `CONTRIBUTING.md` in the repo root — welcoming and specific. Include:

   a. **Welcome message** — acknowledge contributors are helping serve a 
      devotional community
   
   b. **Code of conduct** — adapt the Contributor Covenant briefly, with a 
      note that respectful, devotional spirit (sat-saṅga) is expected in 
      all interactions
   
   c. **Ways to contribute** (priority order for this project):
      - **Sanskrit term corrections** (highest priority) — instructions for 
        opening an issue with: the wrong transcription, the correct form, 
        which video/timestamp it appeared in, and how confident you are
      - **Sample devotee questions** — help expand eval set with real 
        questions devotees ask
      - **Bug reports** — what happened, what was expected, screenshots if UI
      - **Feature requests** — but understand the project's design 
        philosophy (retrieval-only, no LLM answers); features that conflict 
        with core principles will be politely declined
      - **Documentation** — typo fixes, clarifications, translations
      - **Code contributions** — see Development setup below
   
   d. **Development setup** — link to README quick-start, then add:
      - Use `pre-commit` hooks (we'll add later)
      - Run tests before PR: `pytest tests/`
      - Format with `ruff format .` before commit
      - Type-check with `mypy app/ scripts/`
   
   e. **PR process**:
      - Fork → branch → commit → push → open PR
      - Branch naming: `fix/`, `feat/`, `docs/`, `sanskrit/` prefixes
      - PR description should explain WHY, not just WHAT
      - One reviewer required, two for changes affecting Sanskrit handling
      - Squash merge for clean history
   
   f. **Sanskrit-specific guidelines** (because this is critical to the 
      project):
      - Always preserve diacritics in the codebase (use UTF-8)
      - When adding to normalization_dict.json, include a comment with the 
        video where you spotted the error
      - Don't make assumptions about transliteration schemes — match what 
        the teacher uses
   
   g. **Recognition** — contributors are listed in CONTRIBUTORS.md, ordered 
      by first contribution date.

2. `.github/ISSUE_TEMPLATE/sanskrit_correction.md` — special template for 
   Sanskrit corrections, with required fields:
   - What was transcribed (verbatim from the system output)
   - What it should be (with diacritics)
   - Video ID and timestamp where you found it
   - Source of correction (your knowledge, dictionary, scripture reference)

3. `.github/ISSUE_TEMPLATE/bug_report.md` — standard bug template with 
   sections for: description, reproduction steps, expected behavior, 
   actual behavior, environment (OS, Python version, Mac model).

4. `.github/ISSUE_TEMPLATE/feature_request.md` — feature request template 
   that asks the contributor to confirm the feature aligns with the 
   project's design philosophy (retrieval-only, no LLM answers, Sanskrit-first).

5. `.github/PULL_REQUEST_TEMPLATE.md` — PR template with:
   - Summary
   - Type of change (bug fix / feature / docs / Sanskrit / refactor)
   - Related issue
   - Testing performed
   - Checklist (tests pass, docs updated, no diacritic loss, etc.)

6. `CONTRIBUTORS.md` — placeholder file with header "Contributors" and a 
   note: "Listed in order of first contribution. Many thanks to all who 
   help serve the devotional community through this project. 🪷"

Tone: warm, specific, devotional but professional. Not preachy.
```

**After this prompt**: Skim each file. Add yourself as the first entry in CONTRIBUTORS.md.

---

## Prompt E — `.gitignore`, `.editorconfig`, and basic repo hygiene

```
Create the repo hygiene files:

1. `.gitignore` — comprehensive, covering:
   
   Python:
   - __pycache__/
   - *.py[cod]
   - *$py.class
   - *.so
   - .Python
   - .venv/
   - venv/
   - ENV/
   - .pytest_cache/
   - .mypy_cache/
   - .ruff_cache/
   - .coverage
   - htmlcov/
   - dist/
   - build/
   - *.egg-info/
   
   Project-specific:
   - data/audio/         # downloaded mp3s — never commit
   - data/transcripts/   # transcripts — local only (large; backup separately)
   - data/chunks/        # rebuildable from transcripts
   - qdrant_storage/     # Qdrant data directory
   - logs/
   - *.log
   - .env
   - .env.local
   
   IDE/editor:
   - .vscode/
   - .idea/
   - *.swp
   - *.swo
   - *~
   
   macOS:
   - .DS_Store
   - .AppleDouble
   - .LSOverride
   - Icon?
   - ._*
   - .Spotlight-V100
   - .Trashes
   
   Models (HuggingFace cache, can be large):
   - ~/.cache/huggingface/   # NOT in repo, but document this
   
   Add a comment header at the top explaining each section.

2. `.editorconfig` — standard cross-editor config:
   - UTF-8 encoding (CRITICAL for diacritics)
   - LF line endings (Unix)
   - Final newline true
   - Trim trailing whitespace true
   - Indent: 4 spaces for .py, 2 spaces for .yaml/.yml/.json/.md, tab for .mk
   - Charset enforcement note in comment: "UTF-8 required — Sanskrit 
     diacritics must not be corrupted"

3. `.gitattributes` — ensure consistent line endings:
   - `* text=auto eol=lf`
   - `*.sh text eol=lf`
   - `*.py text eol=lf`
   - `*.png binary`
   - `*.jpg binary`
   - `*.svg text`
   - `*.json text eol=lf`
   - `*.md text eol=lf`

4. `.python-version` — single line: `3.11.9` (or latest stable 3.11)

5. `pyproject.toml` skeleton with project metadata and tool configs:
   - [project] section: name="vani-anusandhana", version="0.1.0", 
     description matching repo description, requires-python=">=3.11", 
     license=AGPL-3.0
   - [tool.ruff]: line-length=100, target-version="py311", select common 
     rule sets
   - [tool.mypy]: strict=true for app/ and scripts/
   - [tool.pytest.ini_options]: testpaths=["tests"]

After creating these files:
- Run `git status` to confirm what would be ignored vs. tracked
- Verify no diacritics get mangled by line-ending settings
- Print summary of what was created
```

**After this prompt**: You should now have a fully scaffolded public repo. Time for the first push.

---

## Prompt F — First commit + push (optional helper)

```
Help me create the first three commits and push to GitHub:

1. Verify all expected files exist:
   - README.md
   - LICENSE
   - NOTICE.md
   - CONTRIBUTING.md
   - CONTRIBUTORS.md
   - PILOT_RUNBOOK.md
   - CLAUDE_CODE_PROMPTS.md
   - SANSKRIT_VOCAB_METHODOLOGY.md
   - architecture.md
   - .gitignore
   - .gitattributes
   - .editorconfig
   - .python-version
   - pyproject.toml
   - .github/ISSUE_TEMPLATE/sanskrit_correction.md
   - .github/ISSUE_TEMPLATE/bug_report.md
   - .github/ISSUE_TEMPLATE/feature_request.md
   - .github/PULL_REQUEST_TEMPLATE.md

2. Initialize git repo on `main` branch.

3. Stage and commit in three logical groups:
   
   Commit 1 (foundation):
     git add README.md LICENSE NOTICE.md architecture.md \
             .gitignore .gitattributes .editorconfig
     git commit -m "chore: initial commit — README, AGPL license, architecture diagram"
   
   Commit 2 (documentation):
     git add PILOT_RUNBOOK.md CLAUDE_CODE_PROMPTS.md SANSKRIT_VOCAB_METHODOLOGY.md
     git commit -m "docs: pilot runbook, Claude Code prompts, Sanskrit methodology"
   
   Commit 3 (community):
     git add CONTRIBUTING.md CONTRIBUTORS.md .github/
     git commit -m "docs: contributing guide and issue/PR templates"
   
   Commit 4 (project metadata):
     git add .python-version pyproject.toml
     git commit -m "chore: Python project metadata and tooling config"

4. Print the suggested commands for pushing (don't execute them — I want to 
   review first):
   
   git remote add origin https://github.com/<MY_USERNAME>/vani-anusandhana.git
   git push -u origin main

5. Print a checklist of post-push steps for me to do on github.com:
   - Add the topics/tags I provided
   - Set the About description
   - Pin the repo to my profile
   - Verify the architecture diagram renders correctly in the README preview
   - Star your own repo (it's tradition, plus it helps discovery)
```

**After this prompt**: Review commits with `git log --oneline`, then push when satisfied.

---

## Prompts beyond the pilot (for reference, not yet)

These are placeholders for *after* a successful pilot. Don't run them until the pilot passes.

- **Prompt 11**: Scale transcription to all 5,000 videos (with chunked nightly runs)
- **Prompt 12**: Public deployment — Cloudflare Tunnel from Mac OR small VPS
- **Prompt 13**: Add basic analytics — log queries (no PII), track common questions
- **Prompt 14**: Rate limiting + caching (for public-facing safety)
- **Prompt 15**: Re-indexing pipeline (for adding new videos as the teacher publishes more)

---

## Tips for using these with Claude Code

**Always start a Claude Code session with**:
> "Read PILOT_RUNBOOK.md and SANSKRIT_VOCAB_METHODOLOGY.md before continuing. Then execute the prompt I'll paste next."

**When Claude Code's plan looks wrong**: Push back. Common issues:
- It uses faster-whisper instead of mlx-whisper (Mac-bound)
- It uses fixed-window chunking instead of sentence-aware
- It uses dense-only embedding instead of hybrid
- It uses subprocess to call yt-dlp instead of the Python API
- It tries to run all transcriptions in parallel (don't — sequential is fine on M5)

**After each prompt completes**: Verify the corresponding checkpoint in PILOT_RUNBOOK.md. Don't move on until checkpoint passes.

**If a prompt's output isn't what you expected**: Don't paste the next prompt. Ask Claude Code to fix the current one. Each phase's output is the next phase's input.
