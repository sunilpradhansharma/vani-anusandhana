# Contributing to vāṇī-anusandhāna

Thank you for being here. This project exists to make a teacher's lectures findable — to help devotees locate the exact moment where a topic they care about was addressed. Every contribution, however small, serves that purpose directly.

---

## Code of conduct

This project follows the spirit of the [Contributor Covenant](https://www.contributor-covenant.org/). In practice, what that means here is simple: we are all in sat-saṅga — good association. Interactions should be respectful, patient, and oriented toward service. Criticism of ideas is welcome; criticism of people is not.

If something feels off in an interaction, please contact the maintainer directly.

---

## Ways to contribute

### 1. Sanskrit term corrections *(highest priority)*

If you hear the teacher say *ācārya* and the transcript reads "a-charya", that is a bug — and fixing it improves every search that touches that video.

To report a Sanskrit correction:
- Open an issue using the **Sanskrit Correction** template
- Include: the wrong form (verbatim from the system), the correct form (with diacritics), the video ID and approximate timestamp, and your source of confidence (personal knowledge, published scripture, dictionary)

You don't need to be a developer to do this. This is the most valuable thing a devotee-contributor can offer.

### 2. Sample devotee questions

The evaluation set (30 questions in `eval/sample_questions.md`) drives every quality decision. Real questions from real devotees — especially ones that stumped you, or that you'd love to be able to answer by searching — are invaluable. Open an issue or a PR adding questions to the eval file.

### 3. Bug reports

If something breaks — a search returns nothing, a timestamp is wrong, the UI misbehaves — please report it. Use the **Bug Report** template. The more specific, the better: exact query, exact result (or lack of one), screenshot if it's a UI issue.

### 4. Feature requests

Feature ideas are welcome, with one important caveat: this project is **retrieval-only by design**. Features that would cause the system to generate, paraphrase, or synthesize answers are outside scope and will be respectfully declined. See the [Design philosophy](README.md#design-philosophy) section of the README for the reasoning.

If your idea aligns with the project's principles — better Sanskrit handling, multilingual UI, verse-aware indexing, speaker filtering — open a feature request issue using the template.

### 5. Documentation

Typo fixes, clarity improvements, corrections to the runbook, translations of documentation into other languages — all welcome. For small fixes, a PR is fine without an issue first.

### 6. Code contributions

See **Development setup** below. For anything beyond a small fix, please open an issue first so we can discuss the approach before you invest time in an implementation.

---

## Development setup

Follow the [Quick start](README.md#quick-start) in the README to get the environment running. Then:

```bash
# Install dev dependencies
pip install pre-commit pytest ruff mypy

# Set up pre-commit hooks (enforces formatting before each commit)
pre-commit install

# Before opening a PR, run:
pytest tests/                    # all tests must pass
ruff format .                    # auto-format
ruff check .                     # linting
mypy app/ scripts/               # type checking
```

Pre-commit hooks are not yet configured (coming soon). Until they are, please run `ruff format .` and `ruff check .` manually before committing.

---

## PR process

1. **Fork** the repository and create a branch from `main`
2. **Branch naming**: use a prefix that describes the type of change
   - `fix/` — bug fixes
   - `feat/` — new features
   - `docs/` — documentation only
   - `sanskrit/` — Sanskrit vocabulary, normalization dictionary, prompt
   - `refactor/` — internal restructuring with no behavior change
3. **Commit messages**: short, imperative, present tense ("fix chunking boundary" not "fixed the chunking boundary issue")
4. **PR description**: explain *why*, not just *what*. Link the related issue.
5. **Review**:
   - One reviewer required for all PRs
   - Two reviewers required for any change to Sanskrit handling (`config/sanskrit_prompt.txt`, `config/normalization_dict.json`, `scripts/07_chunk_transcripts.py`)
6. **Merge**: squash merge to keep history clean

---

## Sanskrit-specific guidelines

Sanskrit handling is the soul of this project. Please treat it with corresponding care.

- **Always preserve diacritics**. The codebase is UTF-8 throughout. Never transliterate diacritical forms to ASCII (ā → a, ṭ → t, etc.) in code, comments, or data files — only in situations where the downstream tool explicitly requires it.
- **When adding entries to `config/normalization_dict.json`**, add a comment in `config/sanskrit_errors.md` noting the video ID and timestamp where you observed the error. This creates an audit trail.
- **Don't assume a transliteration scheme**. Different traditions use different conventions (IAST, Harvard-Kyoto, ISKCON style). Match exactly what the teacher uses in published works.
- **Test before submitting**. If you modify the normalization dictionary, re-run `python scripts/07_chunk_transcripts.py` on a few videos and spot-check the output.

---

## Recognition

All contributors are listed in [`CONTRIBUTORS.md`](CONTRIBUTORS.md), ordered by date of first contribution. Sanskrit correctors, question contributors, and documentation helpers are listed alongside code contributors — all forms of service matter equally here.
