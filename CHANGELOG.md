# Changelog

All notable changes to `deep-recon` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `--pdfs` flag for Explorer PDF collection — Explorer downloads relevant PDFs to `<output_dir>/PDFs/` during web search.
- `--plain` flag — Synthesizer produces CommonMark-only output (no `[[wikilinks]]`, no `> [!callouts]`) for non-Obsidian environments.
- Per-agent model overrides: `--explorer-model`, `--associator-model`, `--critic-model`, `--synthesizer-model`. Each agent's Task dispatch now passes the resolved model parameter; defaults are tabulated in SKILL.md's "Agent Model Selection" section.
- `--budget <tokens>` flag — hard cap on total token spend. The orchestrator reads `_metrics.md` between rounds and aborts gracefully (writing the best-available draft) before exceeding the cap.
- `argument-hint` field in SKILL.md frontmatter — surfaces the skill's flag set at invocation time.
- `examples/` directory with two illustrative recon outputs (Explore mode, Focus mode) plus a README explaining their illustrative status.
- `docs/TUNING.md` — guidance for forkers on customizing the Synthesizer's voice. Documents the hardcoded `_resources/Kazys Varnelis – Personal Writing Style Guide.md` reference and three remediation paths (replace, remove, parameterize).
- `CONTRIBUTING.md` — PR norms, prompt-edit conventions, local testing, style expectations.
- `tests/check_recon_structure.py` and `tests/run_smoke_tests.sh` — structural validator for recon output documents (frontmatter fields, required sections, Territory cardinality, Obsidian/plain flavoring), with self-test against the example files.
- `tests/test_validator_contract.py` — negative tests for the validator itself: feeds it 7 malformed stubs (missing section, framings under/over cardinality, missing frontmatter field, plain-mode wikilinks, plain-mode callouts, Obsidian mode with no wikilinks) and asserts the expected errors fire. Catches regressions that would silently weaken the validator. Wired into `run_smoke_tests.sh`.
- `.github/workflows/lint.yml` — CI runs markdownlint-cli2 plus a SKILL.md frontmatter check and a "no frontmatter in agent files" check.
- README **Troubleshooting** section covering missing-document recovery, determinism expectations, partial-round failure handling, generic-output fixes, metrics after compaction, and cost controls.
- README **Documentation** section pointing to CHANGELOG, TUNING, and examples.

### Changed
- Orchestrator now handles partial-round failures gracefully — see the new **Failure Handling** section in SKILL.md. One agent failing no longer aborts the round; Synthesizer write failures retry once then fall back to orchestrator-written stub; `_metrics.md` failures degrade non-fatally.
- README architecture section updated to be Claude-Code-version-agnostic (the prior "experimental in Claude Code 4.6" reference is replaced with a forward-compatible framing).
- README modes table includes `--plain`.

## [1.0.0] — 2026-02-19

Initial public release.

### Added
- Four-agent recon workflow: Explorer (divergent), Associator (lateral), Critic (adversarial), Synthesizer (integrative).
- 2–3 round parallel dispatch via Claude Code's Task tool, with orchestrator cross-pollination between rounds.
- Interactive mode (Socratic — checks in between rounds) and Autonomous mode (end-to-end run).
- Explore intention (divergent — opens possibility space, ends with open questions) and Focus intention (convergent — narrows to a thesis, ends with action plan).
- `--vault-only` flag — skip web search, vault content only.
- `--output <path>` flag — explicit output directory override.
- Anti-hallucination guardrails in the Synthesizer: epistemic honesty rules, observation-vs-invention discipline, ground-every-claim requirement.
- Disk-persisted Synthesizer write — the final document is written directly to its output path by the Synthesizer agent, surviving orchestrator crashes.
- Metrics tracking — per-agent token counts and elapsed times persisted to `_metrics.md` after each round, surviving context compaction.
- Architecture rationale: subagents over agent teams, with the orchestrator as deliberate interpretive layer.
- Obsidian-native output formatting — `[[wikilinks]]`, `> [!callout]` blocks, footnotes, YAML frontmatter, Process Log.

[Unreleased]: https://github.com/kvarnelis/deep-recon/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/kvarnelis/deep-recon/releases/tag/v1.0.0
