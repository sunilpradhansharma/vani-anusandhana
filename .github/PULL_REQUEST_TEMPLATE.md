## Summary

> What does this PR do? One or two sentences.

---

## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Sanskrit correction / vocabulary update
- [ ] Refactor (no behavior change)
- [ ] Other:

---

## Related issue

> Link to the issue this PR addresses (if any). Use `Closes #123` to auto-close on merge.

---

## Why this change?

> Explain the motivation. What was wrong, missing, or improvable? A reviewer should understand the *why* without reading the code.

---

## Testing performed

> How did you verify this works? Include specific commands run and what you observed.

```bash
# example
pytest tests/
python scripts/07_chunk_transcripts.py --inspect VIDEO_ID
```

---

## Checklist

- [ ] Tests pass (`pytest tests/`)
- [ ] Code formatted (`ruff format .`)
- [ ] No linting errors (`ruff check .`)
- [ ] Type checks pass (`mypy app/ scripts/`)
- [ ] Diacritics preserved — no UTF-8 → ASCII degradation in Sanskrit terms
- [ ] If modifying `normalization_dict.json`: corresponding entry added to `config/sanskrit_errors.md`
- [ ] If modifying Sanskrit handling: reviewed by two maintainers (or requested)
- [ ] Documentation updated if behavior changed
- [ ] `data/transcripts/` not committed (these are local-only, large files)
