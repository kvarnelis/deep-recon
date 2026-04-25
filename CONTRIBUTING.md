# Contributing to deep-recon

This is a small skill — five markdown files, one orchestrator prompt, four agent prompts, one output template. Changes ripple through the whole behavior of the skill quickly, so the bar for PRs is higher than the surface area suggests.

## Before you start

Different kinds of changes have different paths:

- **Bug in the orchestrator or an agent prompt** (the skill misbehaves on a defined input): open an issue with a minimal reproduction, then PR the fix. Small fixes can skip the issue.
- **Feature addition** (new flag, new mode, new agent): open an issue first. Most feature additions break the existing prompt economy in non-obvious ways, and a 5-line discussion ahead of time is cheaper than a 200-line revert.
- **Voice or personal-style change** to the Synthesizer's prompt: don't PR these upstream — fork. The Synthesizer's voice is calibrated for one specific user, and the right way to use it for someone else is to retune in your fork. See [`docs/TUNING.md`](docs/TUNING.md).
- **Architectural change** (subagents → agent teams, structured handoff, persistence layer): open an issue and discuss the design before any code. These are the kinds of changes that need consensus, not review.
- **Documentation, examples, troubleshooting**: PR directly. Light review, fast merge.

## Prompt-edit conventions

The agent prompt files (`agents/*.md`) and `SKILL.md` are the load-bearing parts of this repo. Edits here change recon behavior in ways that are hard to predict from a diff.

**Atomic changes.** One prompt-section change per PR. If you're rewriting the Synthesizer's Voice section *and* the Critic's Strongest Objections format, that's two PRs.

**Justify additions.** New paragraphs in agent prompts add tokens and instruction-load. If you're adding a section, the PR description should explain what failure mode it addresses and why a smaller change wouldn't fix it.

**Show before/after.** If your change is non-trivial, run a recon on a topic both before and after the edit and quote a paragraph from each in the PR description. If the after-version isn't clearly better, the change probably isn't ready.

**Never edit `SKILL.md` and an agent file in the same PR** unless the edits are coupled by design. The orchestrator's responsibilities and an agent's responsibilities should be reviewed independently.

**Don't loosen anti-hallucination guardrails.** The Synthesizer's Epistemic Honesty section and the Critic's "WITHOUT rebuttal" rule are load-bearing for output quality. PRs that weaken these rules need an exceptional justification.

## Testing changes locally

Before submitting a PR:

1. **Run a recon** on a topic you've used the skill on before. Read the output against the previous version. Look for register drift, structural regressions, missing sections, off-tone prose.
2. **Run the structural test script** (when goldens land — see `tests/golden/`). A passing script means the output skeleton is intact. It does not mean the prose is good.
3. **Run `markdownlint-cli2` locally** if you can: `npx markdownlint-cli2 "**/*.md"`. The CI runs this on every push.
4. **Verify frontmatter**: `SKILL.md` must keep `name`, `description`, `allowed-tools` fields. Agent files must NOT have YAML frontmatter (see the README's "A note on the agents/ directory").

If you can't run the skill locally (no Claude Code access, no Obsidian vault), say so in the PR description. We'll smoke-test for you before merging.

## Style

Match the existing repo voice. The README and SKILL.md are deliberately opinionated and direct. PRs that introduce hedging, generic consultancy-speak, or LLM tells ("delve," "leverage," "robust," "comprehensive") will get bounced.

**Concrete.** Prefer "the orchestrator reads `recon/rN-explorer.md` from disk after each round" over "the orchestrator processes agent outputs."

**Declarative.** Prefer "this is the right call until agent teams reach a stable form" over "one might consider exploring agent teams when they become more stable."

**Cite specifics.** When recommending a change, point to a file and line. PR descriptions and commit messages benefit from the same.

## Commit messages

Match the repo's existing pattern: imperative subject line, no conventional-commit prefix, optional body explaining the *why*. Examples:

- `Add --plain output flag for non-Obsidian forks`
- `Fix Synthesizer voice-guide read on missing path`
- `Document architecture: subagents over agent teams`

If the change is part of a larger plan, append the plan's item ID in parens: `Add Troubleshooting section (T1.1)`.

## Issue templates

We don't have formal issue templates yet. A useful issue includes:

- **What you tried** — the exact `/deep-recon` invocation
- **What you expected** — the output structure or content you anticipated
- **What happened** — the actual output, or the missing output
- **Vault context** — rough size, whether the topic had relevant existing notes, mode flags used

## License

By contributing, you agree your contributions are released under the same MIT license as the rest of the repo.
