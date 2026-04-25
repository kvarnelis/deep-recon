# tests/

Structural validation for `deep-recon` output documents. Catches prompt-regressions that change *what shape* the output takes — missing sections, wrong section names, dropped callouts, broken framings count — without false-positives on prose that varies between runs.

## Files

- `check_recon_structure.py` — the validator. Asserts the structural contract.
- `test_validator_contract.py` — negative tests for the validator. Feeds it intentionally-malformed stubs (missing sections, wrong cardinality, plain-mode violations, etc.) and asserts the right errors are raised. Without this, a regression that loosens the validator could land silently.
- `run_smoke_tests.sh` — runs the validator against `examples/explore-example.md` and `examples/focus-example.md`, then runs the validator-contract tests. Use this as a self-test of the validator itself.
- `golden/` — reserved for full golden-master files captured from real recon runs (see "Adding goldens" below).

## What the validator checks

Per file, given a mode (`explore` or `focus`) and an optional `--plain` flag:

1. **Frontmatter** — YAML delimiters present; required fields (`created`, `type`, `topic`, `mode`, `intention`) declared.
2. **Required sections** — `## The Territory`, `## Tensions`, `## Unexpected Connections`, `## Open Questions`, `## Sources` for Explore mode; `## The Argument`, `## Tensions`, `## Next Steps`, `## Sources` for Focus mode.
3. **Territory cardinality** (Explore only) — between 3 and 5 framings (`###` subheadings) under `## The Territory`.
4. **Callouts** — Process Log (`> [!note]- Process Log`) and Central Question (`> [!abstract] Central Question`) — unless `--plain` is set.
5. **Obsidian flavoring** — at least one `[[wikilink]]` — unless `--plain` is set.
6. **Plain-mode invariants** (when `--plain` is set) — no callouts, no wikilinks, and a top-level `## Central Question` section instead of the abstract callout.

## Running locally

```bash
# Validate a real recon you just produced
python3 tests/check_recon_structure.py recon/2026-04-15-my-topic.md --mode explore

# Self-test against the examples/
bash tests/run_smoke_tests.sh
```

Requires Python 3.10+. No third-party dependencies.

## Running in CI

Add to `.github/workflows/lint.yml` or a separate workflow:

```yaml
  smoke-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: bash tests/run_smoke_tests.sh
```

## What this is NOT

- **It is not a content quality check.** A document with all the right sections in all the right places can still be generic, hedged, or off-voice. Read the prose.
- **It is not a vault-state assertion.** It can't tell whether the wikilinks resolve to real notes in your vault.
- **It is not a token-budget check.** Use the running cost in `_metrics.md` for that (see T2.2 budget guard, when implemented).

## Adding goldens

When you run a real recon and want to capture its structural skeleton as a regression baseline, save the output file under `tests/golden/` and add it to `run_smoke_tests.sh`:

```bash
check "tests/golden/2026-04-15-network-culture.md" --mode explore
```

Goldens should be representative outputs from a deliberate, well-tuned run. Don't commit goldens from a first attempt at a new topic — those drift in unpredictable ways.

The structural contract in `check_recon_structure.py` should evolve carefully: tightening it (more required sections, narrower cardinality bounds) catches more regressions but also rejects valid outputs from future variations. When in doubt, keep the contract minimal and rely on golden snapshots for finer assertions.

## Regeneration

If a SKILL.md or template change deliberately changes the output structure, update both the validator (`check_recon_structure.py`) and the example files (`examples/*.md`) in the same PR so smoke tests stay green.
