<div align="center">

<img src="assets/logo_hero_240.png" width="160" alt="vāṇī-anusandhāna logo: a Vaiṣṇava tilaka inside a sun-rayed medallion with lotus crown above an open book and magnifying glass" />

# vāṇī-anusandhāna 🪷

> **वाणी-अनुसन्धान** — A disciplined inquiry into Vedic wisdom, based strictly on the lectures of [HH Romapada Swami](https://www.romapadaswami.com/).

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Apple Silicon](https://img.shields.io/badge/Apple_Silicon-optimized-black.svg)](https://developer.apple.com/documentation/apple-silicon)
[![AI answers: zero hallucinations](https://img.shields.io/badge/AI_answers-zero_hallucinations-brightgreen.svg)](#design-philosophy)

</div>

---

Semantic search over a single spiritual teacher's YouTube lectures. Devotees ask a question in plain language and receive the exact moments in the teacher's videos where that topic is addressed — with timestamped deep-links, transcript snippets, and a direct jump into the recording. Every answer is the teacher's actual words, retrieved not generated. The system runs entirely on a MacBook Pro with Apple Silicon, costs near zero to operate, and is designed to scale from a 25-video pilot to a 5,000-video archive without changing architecture.

---

## What it does

**Question from a devotee:**
> *"What is the difference between śravaṇa and smaraṇa in bhakti practice?"*

**System returns 4 results:**

| # | Video | Timestamp | Snippet |
|---|-------|-----------|---------|
| 1 | Bhakti-yoga: The Path of Devotion | [14:32 → 15:48](https://www.youtube.com/watch?v=EXAMPLE1&t=872s) | *"...śravaṇa is the foundation — hearing the holy name, hearing the Bhāgavatam. Smaraṇa deepens what śravaṇa plants. Without hearing first, remembrance has nothing to hold..."* |
| 2 | The Nine Limbs of Bhakti | [08:17 → 09:40](https://www.youtube.com/watch?v=EXAMPLE2&t=497s) | *"...Prahlāda tells us: śravaṇaṁ kīrtanaṁ viṣṇoḥ smaraṇaṁ. Hearing comes first. Then kīrtana. Then smaraṇa. This order is not accidental — it is the ācārya's mercy..."* |
| 3 | Stages of Sādhana | [31:05 → 32:22](https://www.youtube.com/watch?v=EXAMPLE3&t=1865s) | *"...in the beginning, we can barely remember Kṛṣṇa for thirty seconds. That is fine. Śravaṇa builds the capacity. Smaraṇa is the fruit of sustained hearing..."* |
| 4 | Nārada-bhakti-sūtra Study | [52:44 → 53:59](https://www.youtube.com/watch?v=EXAMPLE4&t=3164s) | *"...one who hears constantly develops the faculty of continuous remembrance. This is why the guru says: hear first, for one year, two years. Smaraṇa will come..."* |

**No AI-generated answers. No paraphrasing. No hallucinations. The teacher's actual words are the answer.**

---

## User experience

vāṇī-anusandhāna is designed mobile-first. Devotees searching from a phone
during morning sādhana, evening reflection, or while traveling should feel
the difference between this and a generic AI tool the moment they arrive.
The interface is calm, reverent, and purposeful — the teacher's words are
the visual hero, and the search machinery quietly steps aside once results
arrive.

<div align="center">
<img src="assets/mock1.png" width="300" alt="Home screen — logo, search box, invitational verse"/>&nbsp;&nbsp;&nbsp;&nbsp;<img src="assets/mock2.png" width="300" alt="Results screen — embedded video, transcript, timestamp"/>

*Home — the invitation* &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; *Results — with full transcript*
</div>

### How a devotee uses it

1. **Opens the app on their phone.** Sees the logo, the wordmark in maroon
   serif, and a single search box. Below it: a Tulasi-leaf illustration and
   a quiet verse — *"Through this inquiry, the seeker feels the teacher's
   guidance speaking through his own lectures."*

2. **Types a question** in plain language: *"What is the difference between
   śravaṇa and smaraṇa?"* — no special syntax, no special keywords.

3. **Sees four results within a second.** Each result is a card with:
   - The teacher's actual lecture title
   - An embedded YouTube player ready to play from the exact moment
   - A timestamp range like *12:34 → 13:42* showing the duration of the
     relevant passage
   - The full transcript of that 60–90 seconds — readable, in serif, with
     Sanskrit terms gently highlighted
   - Three small actions: favorite, share, copy timestamp

4. **Taps a Sanskrit term** in the transcript and a small popover appears
   showing the term in Devanagari (श्रवण) with a brief gloss ("listening,
   hearing"). For devotees who want all Sanskrit shown in Devanagari
   inline, a toggle in the header switches the display globally.

5. **Saves a passage** to favorites, shares it with a fellow devotee, or
   copies a deep-link timestamp to revisit later. All saved data lives on
   their device — no account required.

### Designed for the way devotees actually search

📱 **Mobile-first.** Single column, large tap targets, transcripts that
read like a book, not a webpage. Most devotees will use this from a phone
during quiet moments of practice — the design assumes that, not the
opposite.

🎬 **Embedded video + transcript together.** Click a result and the player
and the teacher's transcribed words appear together in context — no
jumping to YouTube and losing your place. A secondary "Open in YouTube"
link is always available for those who prefer the YouTube app.

🪷 **Calm, devotional aesthetic.** Cream and saffron with deep maroon text.
Georgia serif for the teacher's words. Subtle Tulasi-leaf motif in the
empty state — the only ornamental flourish; everything else relies on
typography and color.

🔤 **Sanskrit-aware typography.** Tap any Sanskrit term to see its
Devanagari spelling and a brief gloss. Optional toggle to show Devanagari
for all terms inline. Sanskrit diacritics (ā, ṇ, ī, ś) render correctly
across the entire interface.

💝 **Personal practice tools.** Search history, favorited passages, one-tap
sharing via the Web Share API, copy-deeplink-with-timestamp — everything
stored locally on your device. Optional sync across devices is on the
roadmap; v1 is fully local-first.

🤐 **No ads, no tracking, no AI-generated answers.** What you see is what
HH Romapada Swami said. Nothing added, nothing inferred. No analytics
beacons, no third-party scripts, no fingerprinting.

### Visual identity

| Token | Hex | Use |
|---|---|---|
| Cream | `#FBF6EC` | Page background |
| Cream-soft | `#FFFCF6` | Card surface, input background |
| Saffron | `#E8862A` | Primary accent, toggles, badges |
| Maroon | `#5C1A1A` | Primary text, primary buttons |
| Gold | `#C49B3F` | Logo accents, dotted underlines |
| Brown-warm | `#8B6F47` | Secondary text, metadata |

**Typography stack:**
- **Body & transcripts:** Georgia, Charter, Iowan Old Style — serif, like a book
- **UI chrome:** -apple-system, BlinkMacSystemFont, Segoe UI — system sans
- **Devanagari:** Noto Sans Devanagari — loaded only when Devanagari is enabled
- **Numbers:** tabular-nums variant — so 12:34 aligns with 13:42

### What this UI deliberately does NOT do

- ❌ No AI-generated answers, summaries, or paraphrases — retrieval only
- ❌ No autocomplete in v1 (resist scope creep; add later if devotees ask)
- ❌ No social-network features (likes, comments, public profiles)
- ❌ No dark mode in v1 (the warm Vaiṣṇava palette is a daylight palette by design)
- ❌ No multi-language UI in v1 (English with optional Sanskrit Devanagari)
- ❌ No login required for basic search (favorites/history live on device)

The full design system — palette specifications, typography scale, component
patterns, accessibility requirements, mobile breakpoints, animation
philosophy — will be documented in `UI_DESIGN.md` (created during UI
implementation).

---

## Why this name

*Vāṇī* (वाणी) means the spoken word — and in the Gauḍīya Vaiṣṇava tradition, specifically the *transmitted speech* of the teacher: the living instruction that travels through the paramparā. When the teacher speaks, vāṇī flows. This system is built to make that vāṇī findable.

*Anusandhāna* (अनुसन्धान) does not simply mean "search" in the Google sense. It carries the sense of *sustained, contemplative inquiry* — following a thread carefully, with attention and reverence. A devotee doing *anusandhāna* of scripture is not skimming; they are listening for something specific, with an open heart.

Together: **vāṇī-anusandhāna** — *the careful inquiry through the teacher's transmitted speech*. The name signals to devotees that this project was built with the same care they bring to their own study.

---

## Architecture

```mermaid
graph TD

subgraph ING["🔄  Ingestion pipeline — one-time · Apple Silicon · ~12× realtime"]
  YT(["📺 YouTube Playlist<br/>25 → 5,000 lectures<br/>playlist URL only"])
  DL["yt-dlp<br/>audio-only extract<br/>MP3 · best quality · no video"]
  WH["mlx-whisper large-v3<br/>Apple GPU + Neural Engine<br/>Sanskrit initial_prompt · lang=en · temp=0"]
  TR[/"Transcript JSON<br/>full text + timed segments<br/>word-level timestamps"/]
  CH[/"Sentence-aware chunks<br/>~60s windows · 15s overlap<br/>cut at sentence boundary · not mid-word"/]
  SN["Sanskrit normalize<br/>rapidfuzz ≥ 90% · exact + fuzzy<br/>normalization_dict.json · Layer 2 of 3"]
  EM["bge-m3 embed<br/>dense 1024-dim + sparse BM25<br/>embeds text_normalized · batch_size=32"]
  QD[("Qdrant<br/>hybrid vector index<br/>payload: video · timestamps · text")]
end

subgraph QRY["⚡  Query pipeline — real-time · target &lt; 1.5 s end-to-end"]
  DV(["🙏 Devotee asks<br/>natural language question<br/>any Sanskrit spelling accepted"])
  API["FastAPI  /search<br/>POST · JSON · top_k = 4<br/>/health · CORS · models loaded at startup"]
  QE["bge-m3 embed<br/>same model · same vector space<br/>dense + sparse query vectors"]
  QS[("Qdrant hybrid search<br/>dense cosine + sparse BM25<br/>retrieves top-20 candidates")]
  RR["Cross-encoder rerank<br/>bge-reranker-v2-m3<br/>full query text × each chunk · more accurate"]
  MG["Merge adjacent segments<br/>same video · gap &lt; 30 s<br/>avoids near-duplicate results"]
  R4["Top 4 results<br/>YouTube deep-link · ?v=ID&amp;t=Ns<br/>timestamp range · transcript snippet"]
  DV2(["🎧 Devotee listens<br/>jumps to exact moment<br/>teacher's actual words · no paraphrase"])
end

YT    -->|"playlist URL"| DL
DL    -->|"MP3 audio"| WH
WH    -->|"JSON + word timestamps"| TR
TR    -->|"segments"| CH
CH    -->|"~60 s chunks"| SN
SN    -->|"text_normalized"| EM
EM    -->|"dense + sparse vectors"| QD

DV    --> API
API   -->|"query string"| QE
QE    -->|"query vectors"| QS
QS    -->|"top-20 candidates"| RR
RR    -->|"reranked scores"| MG
MG    -->|"merged clips"| R4
R4    --> DV2

QD    -.->|"Persisted on disk"| QS

classDef compute  fill:#DBEAFE,stroke:#1D4ED8,color:#1E3A5F,stroke-width:2px,font-weight:bold
classDef storage  fill:#EDE9FE,stroke:#6D28D9,color:#2E1065,stroke-width:2px,font-weight:bold
classDef quality  fill:#FEE2E2,stroke:#DC2626,color:#7F1D1D,stroke-width:2px,font-weight:bold
classDef data     fill:#D1FAE5,stroke:#059669,color:#064E3B,stroke-width:2px,font-weight:bold
classDef output   fill:#FEF3C7,stroke:#D97706,color:#78350F,stroke-width:2px,font-weight:bold
classDef devotee  fill:#F3F4F6,stroke:#6B7280,color:#1F2937,stroke-width:2px,font-weight:bold

class DL,WH,EM,API,QE compute
class QD,QS storage
class SN,RR,MG quality
class TR,CH data
class R4 output
class YT,DV,DV2 devotee
```

**Color key** — 🔵 blue: compute steps &nbsp;·&nbsp; 🟣 purple: vector storage &nbsp;·&nbsp; 🔴 red: quality/Sanskrit layers &nbsp;·&nbsp; 🟢 green: data artifacts &nbsp;·&nbsp; 🟡 amber: output &nbsp;·&nbsp; ⚪ gray: devotee endpoints

### 🔄 Ingestion pipeline (one-time, ~12x realtime on Apple Silicon M5)

1. **yt-dlp** extracts audio-only MP3s from a YouTube playlist without downloading video.
2. **mlx-whisper large-v3** transcribes each lecture using Apple Silicon GPU + Neural Engine, with a carefully tuned Sanskrit `initial_prompt` that biases the model toward correct diacritical forms.
3. Transcripts are saved as **JSON with word-level timestamps** — the foundational asset, kept forever.
4. **Sentence-aware chunking** walks the transcript and cuts at natural sentence boundaries (not fixed time windows), producing ~60-second chunks with 15-second overlaps so no thought is split mid-sentence.
5. **Sanskrit normalization** applies a fuzzy-match dictionary (built during calibration) to correct terms the prompt missed — `rapidfuzz` at 90% similarity threshold.
6. **bge-m3** generates both dense (1024-dim) and sparse vectors from each normalized chunk. Both vectors are stored in **Qdrant** with the full chunk payload.

### ⚡ Query pipeline (real-time, <1.5 seconds end-to-end)

1. Devotee submits a natural-language question to the **FastAPI** `/search` endpoint.
2. **bge-m3** embeds the query into dense + sparse vectors (same model as ingestion — vectors live in the same space).
3. **Qdrant hybrid search** retrieves the top-20 candidate chunks, combining semantic similarity (dense) with keyword recall (sparse/BM25-like).
4. **bge-reranker-v2-m3** cross-encoder scores each candidate against the full query text — a more expensive but more accurate ranking pass.
5. **Adjacent-segment merging** collapses results from the same video that are less than 30 seconds apart, avoiding four nearly-identical clips.
6. **Top 4 results** are returned with YouTube deep-links (`?v=ID&t=Ns`), formatted timestamp ranges, and the normalized transcript snippet.
7. Devotee clicks, jumps directly to `t=754s` in the video, and hears the teacher's answer.

---

## Design philosophy

### 🎯 Retrieval only — no LLM-generated answers

This system does not use a language model to generate, summarize, or paraphrase answers. This is a deliberate architectural and theological choice:

- **Theological**: In the Vaiṣṇava tradition, the guru's words carry *śakti* — spiritual potency. A paraphrase, however accurate, is not the same as hearing the teacher directly. The system must not interpolate.
- **Trust**: Devotees can verify any result by clicking the timestamp. Nothing is invented.
- **Cost**: No inference API calls. Zero ongoing LLM cost.
- **Simplicity**: The retrieval pipeline is auditable, reproducible, and requires no prompt engineering to maintain.

Any future feature that generates or paraphrases answers is out of scope for this project.

### 🧘 Sanskrit-first transcription — the 3-layer approach

Sanskrit handling is the highest-leverage part of this system. See [`SANSKRIT_VOCAB_METHODOLOGY.md`](SANSKRIT_VOCAB_METHODOLOGY.md) for the full methodology. In brief:

- **Layer 1 — Whisper `initial_prompt`**: A natural-prose sentence using diacritical Sanskrit terms biases the model toward correct forms at transcription time. Capped at ~240 tokens, so terms are chosen carefully.
- **Layer 2 — Post-processing normalization dictionary**: A `rapidfuzz`-backed JSON dictionary catches errors the prompt missed. No size limit. Grows for the life of the project.
- **Layer 3 — Dual indexing**: Both `text_original` (what Whisper heard) and `text_normalized` (corrected) are stored. A devotee typing "bhagavatam" or "Bhāgavatam" hits the same chunks.

Target: >85% Sanskrit term accuracy after Layers 1 + 2.

### 💻 Local-first, then optionally cloud

Everything runs on a MacBook Pro with Apple Silicon: transcription, embedding, vector search, and serving. There is no cloud dependency. When ready for public access, a Cloudflare Tunnel exposes the local server, or the index is migrated to a small VPS. The architecture doesn't change — only where it runs.

### 🔄 Sentence-aware chunking, not fixed time windows

Fixed-window chunkers (every 30 seconds, every 60 seconds) produce chunks that cut mid-sentence. When a devotee clicks a deep-link and lands in the middle of a thought, the experience feels broken. This system accumulates transcript segments until the buffer is ~60 seconds long, then waits for the next sentence boundary before cutting. The result: every chunk is a complete thought. Every deep-link lands at the start of something coherent.

---

## Cost summary

| Item | This project | Typical cloud RAG |
|------|-------------|-------------------|
| Transcription (5,000 hrs audio) | $0 (local M5) or ~$200 (rented GPU) | ~$1,800 (OpenAI Whisper API) |
| Embeddings | $0 (bge-m3, local) | ~$50–200/month (OpenAI) |
| Vector database | $0 (Qdrant, self-hosted) | $50–200/month (managed) |
| LLM inference | $0 (retrieval-only, no LLM) | $100–500/month |
| Hosting | $0 (local) or $5–10/month (VPS) | $20–50/month |
| **Total one-time** | **$0–$200** | **$2,000+** |
| **Total monthly** | **$0–$10** | **$200–$950** |

The full system — pilot through public deployment — costs under $300 one-time and under $120/year. Designed to be affordable for any spiritual non-profit or individual devotee.

---

## Quick start

### Prerequisites

- MacBook with Apple Silicon (M1/M2/M3/M4/M5), 16+ GB RAM
- macOS 13+, [Homebrew](https://brew.sh), Python 3.11+
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for Qdrant)

### Setup

```bash
git clone https://github.com/sunilpradhansharma/vani-anusandhana.git
cd vani-anusandhana
make setup              # installs deps, pulls Qdrant image, starts container
python verify_setup.py  # should print: ✅ environment ready
```

### Pilot run (25 videos)

```bash
# 1. Inventory the playlist (no download, ~30 seconds)
python scripts/01_inventory_playlist.py

# 2. Download audio for 3 calibration videos
python scripts/02_download_audio.py --limit 3

# 3. Baseline transcription (no Sanskrit prompt yet)
python scripts/03_transcribe.py --ids ID1,ID2,ID3 --output-suffix baseline

# 4. Read transcripts carefully; log Sanskrit errors
python scripts/04_log_sanskrit_errors.py --input data/transcripts/ID1.baseline.json

# 5. Build Sanskrit prompt from errors + seed terms
python scripts/05_build_sanskrit_prompt.py

# 6. Re-transcribe calibration videos with prompt; verify >70% error fix rate
python scripts/03_transcribe.py --ids ID1,ID2,ID3 --prompt-file config/sanskrit_prompt.txt --output-suffix tuned
python scripts/05b_diff_transcripts.py --baseline data/transcripts/ID1.baseline.json --tuned data/transcripts/ID1.tuned.json

# 7. Batch transcribe remaining 22 (~90 min on M5)
bash scripts/06_batch_transcribe.sh

# 8. Chunk → embed → index → serve → evaluate
python scripts/07_chunk_transcripts.py
python scripts/08_index_chunks.py
uvicorn app.main:app --port 8000
python scripts/10_run_evaluation.py
```

See [`PILOT_RUNBOOK.md`](PILOT_RUNBOOK.md) for the full stage-by-stage guide with quality checkpoints.

---

## Project structure

```
vani-anusandhana/
├── README.md                         ← this file
├── PILOT_RUNBOOK.md                  ← mental model, stages, checkpoints
├── CLAUDE_CODE_PROMPTS.md            ← prompts for Claude Code sessions
├── SANSKRIT_VOCAB_METHODOLOGY.md     ← 3-layer Sanskrit handling approach
├── architecture.md                   ← Mermaid diagram source
├── LICENSE                           ← AGPL-3.0
├── NOTICE.md                         ← copyright + intent statement
├── CONTRIBUTING.md                   ← how to contribute
├── CONTRIBUTORS.md                   ← contributor list
├── pyproject.toml                    ← project metadata + tool config
├── Makefile                          ← setup, qdrant-up/down, clean-audio
├── docker-compose.yml                ← Qdrant on port 6333
├── verify_setup.py                   ← smoke test: imports + Qdrant + bge-m3
│
├── config/
│   ├── sanskrit_seed_terms.txt       ← ← VERSION CONTROL, GROW OVER TIME
│   ├── sanskrit_prompt.txt           ← ← VERSION CONTROL, BACKUP
│   ├── normalization_dict.json       ← ← VERSION CONTROL, BACKUP
│   └── sanskrit_errors.md           ← living log of observed mis-transcriptions
│
├── data/
│   ├── playlist_inventory.json       ← video metadata from Stage 1
│   ├── playlist_inventory.txt        ← human-readable inventory
│   ├── audio/                        ← downloaded MP3s — DELETE AFTER TRANSCRIPTION
│   ├── transcripts/                  ← ← KEEP FOREVER, BACKUP SEPARATELY
│   └── chunks/                       ← chunked + normalized JSON (rebuildable)
│
├── scripts/
│   ├── 01_inventory_playlist.py
│   ├── 02_download_audio.py
│   ├── 03_transcribe.py
│   ├── 04_log_sanskrit_errors.py
│   ├── 05_build_sanskrit_prompt.py
│   ├── 05b_diff_transcripts.py
│   ├── 06_batch_transcribe.sh
│   ├── 06b_validate_transcripts.py
│   ├── 07_chunk_transcripts.py
│   ├── 08_index_chunks.py
│   ├── 10_run_evaluation.py
│   └── 10b_analyze_eval.py
│
├── app/
│   └── main.py                       ← FastAPI server: /search, /health, /
│
├── eval/
│   ├── sample_questions.md           ← 30 devotee questions for evaluation
│   ├── scoring_template.csv          ← fill in after running evaluation
│   └── raw_results.html              ← visual review of top-4 results
│
└── logs/                             ← transcription logs, batch logs
```

---

## Tech stack

| Layer | Choice | Why |
|-------|--------|-----|
| Audio download | yt-dlp (Python API) | No subprocess; handles age-restriction, rate limits, archive |
| Transcription | mlx-whisper large-v3 | Apple Silicon GPU + Neural Engine; ~12x realtime; free |
| Embedding | BAAI/bge-m3 (FlagEmbedding) | Dense + sparse from one model; multilingual; free; runs on MPS |
| Vector database | Qdrant (self-hosted Docker) | Native hybrid search; persistent; scales to 5,000 videos easily |
| Reranker | BAAI/bge-reranker-v2-m3 | Cross-encoder accuracy boost; runs locally; pairs with bge-m3 |
| API | FastAPI + uvicorn | Fast, typed, async; minimal overhead |
| Frontend | Vanilla HTML + HTMX | No build step, no framework, no npm; readable by anyone |
| Language | Plain Python (no LangChain) | LangChain adds abstraction without adding value for a retrieval-only pipeline |
| Fuzzy match | rapidfuzz | Sanskrit normalization; faster than fuzzywuzzy; well-maintained |

---

## Roadmap

- ✅ **Phase 1: Pilot** — 25-video proof of concept, evaluation harness, quality checkpoints
- 🚧 **Phase 2: Full transcription** — 5,000 videos (~17 days continuous on M5, or ~5 days on rented GPU); Sanskrit term list expansion
- 📋 **Phase 3: Public deployment** — Cloudflare Tunnel or small VPS ($5–10/month); domain; basic rate limiting
- 🔮 **Future possibilities**:
  - Speaker filtering (isolate teacher's voice from Q&A participants)
  - Verse-aware indexing (Bhāgavatam 1.2.6 as a structured searchable field)
  - Devotee correction workflow (flag mis-transcribed Sanskrit in the UI)
  - Multilingual UI (Hindi, Bengali, Tamil)
  - Mobile PWA for offline browsing of transcripts
  - Periodic re-indexing as new lectures are published

---

## Contributing

Contributions that serve the project's mission are warmly welcomed. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full guide.

**Highest-priority ways to help:**
- **Sanskrit corrections** — if you spot a mis-transcribed term, open an issue using the Sanskrit Correction template. Include the wrong form, the correct form, and the video + timestamp.
- **Sample devotee questions** — real questions from real devotees improve the evaluation set and reveal gaps in coverage.
- **Performance improvements** — faster indexing, lower memory, better chunking heuristics.
- **Translations** — UI strings, documentation.
- **Documentation** — typo fixes, clarity improvements, corrections.

Features that would cause the system to generate or paraphrase answers are outside scope and will be respectfully declined.

---

## License

This project is licensed under the **GNU Affero General Public License v3.0** (AGPL-3.0). See [`LICENSE`](LICENSE) for the full text.

The AGPL was chosen deliberately: if you deploy a modified version of this system as a public service, you must release your modifications as open source. The teacher's words belong to the lineage. Improvements to how those words are searched should belong to the community too.

---

## Acknowledgments

This project exists in service of **HH Romapada Swami's** decades of
patient transmission. Every searchable moment in this index is his words;
the system is merely the librarian. Permission to index his publicly
available lectures was kindly granted by his ministry.

In the paramparā: His Divine Grace A.C. Bhaktivedanta Swami **Śrīla
Prabhupāda** — founder-ācārya of the International Society for Krishna
Consciousness, in whose direct line HH Romapada Swami serves as initiating
guru.

Technical foundations from the open-source community:

- [MLX team at Apple](https://github.com/ml-explore/mlx) for making Apple
  Silicon a first-class ML platform
- [BAAI](https://huggingface.co/BAAI) for `bge-m3` and `bge-reranker-v2-m3`
  — free, multilingual, locally runnable, genuinely competitive embeddings
- [OpenAI](https://github.com/openai/whisper) for open-sourcing Whisper
- [Qdrant](https://qdrant.tech/) for a vector database that is both
  powerful and free to self-host

And to the devotees who test, ask thoughtful questions, report
mis-transcribed Sanskrit terms, and gradually make the system more
faithful to its source.

🪷 **Hare Kṛṣṇa**

---

## Citation

For academic use:

```bibtex
@software{vani_anusandhana_2026,
  author    = {YOUR_USERNAME},
  title     = {v\={a}\d{n}\={i}-anusandh\={a}na: Semantic Search over Spiritual Teacher Lectures},
  year      = {2026},
  url       = {https://github.com/YOUR_USERNAME/vani-anusandhana},
  license   = {AGPL-3.0}
}
```

---

<div align="center">

🪷 **Hare Kṛṣṇa** 🪷

Built with care for devotional communities worldwide.

*वाणी-अनुसन्धान — the seeker's careful inquiry through the teacher's transmitted voice.*

</div>
