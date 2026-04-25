# deep-recon

Multi-agent reconnaissance skill for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) + [Obsidian](https://obsidian.md).

Four specialized agents run in parallel rounds to explore a topic from multiple angles, find unexpected connections, stress-test ideas, and produce a structured recon document with competing framings, developed tensions, and open questions.

## The Agents

| Agent | Style | Role |
|---|---|---|
| **Explorer** | Divergent | Casts the widest net — web searches, vault searches, adjacent fields, historical parallels |
| **Associator** | Lateral | Finds non-obvious connections — structural analogies, cross-domain pattern matching, productive metaphors |
| **Critic** | Adversarial | Stress-tests emerging ideas — prior art, hidden assumptions, steelmanned objections, productive contradictions |
| **Synthesizer** | Integrative | Identifies emergent patterns across all inputs — distinct framings, tensions worth preserving, the question the user hadn't considered |

## How It Works

The skill runs 2–3 rounds of parallel agent dispatch:

- **Round 1 — Wide net.** All four agents explore the topic simultaneously. The Explorer gathers raw material from the web and your vault. The Associator finds structural parallels in your existing notes. The Critic identifies prior art and assumptions. The Synthesizer maps what's emerging.

- **Between rounds.** In Interactive mode, the Synthesizer summarizes findings and asks which threads to pursue. In Autonomous mode, it directs the next round automatically — collapsing duplicates, pushing distinct framings further apart, identifying tensions that need development.

- **Round 2 — Deepening.** Agents receive all previous findings plus cross-pollination. The Explorer fills gaps and does reality checks. The Associator works connections between R1 findings. The Critic stress-tests the strongest ideas. The Synthesizer refines themes.

- **Round 3 (optional) — Further development.** Only if tensions need more work or framings remain underdeveloped.

- **Output.** The Synthesizer drafts the final document: a structured recon with competing framings, fully developed tensions, unexpected connections, and genuinely open questions — all in Obsidian-native markdown with wikilinks, callouts, and footnotes.

## Architecture

deep-recon uses **subagents** (Claude Code's Task tool), not agent teams. Each agent is
dispatched as an independent task that reports back to the orchestrator. Agents don't
communicate with each other directly — the orchestrator cross-pollinates findings between
rounds.

This is deliberate. The orchestrator's role between rounds — digesting the Synthesizer's
analysis, compiling settled claims, crafting tailored prompts for each agent — is an
interpretive step that shapes the next round's quality. Direct inter-agent messaging
(via agent teams in newer Claude Code releases) erases that interpretive layer.

If agent teams reach a stable form with deterministic dispatch guarantees, a hybrid is
plausible: orchestrator-controlled rounds with inter-agent dialogue *within* each round —
especially Critic↔Explorer for real-time stress-testing, and Synthesizer→all-agents for
mid-round redirect. Until then, the subagent + orchestrator pattern is the right call.

### A note on the `agents/` directory

The four files in `agents/` are not Claude Code agent definitions (no frontmatter,
no `subagent_type`). They are **prompt templates** — read at runtime by the orchestrator
(`SKILL.md`) and inserted into `Task` calls dispatched as `subagent_type:
"general-purpose"`. This keeps the prompts version-controllable without coupling them to
Claude Code's agent-definition spec, which has been moving fast.

## Modes

| Flag | Mode | Description |
|---|---|---|
| *(default)* | Interactive | Socratic — checks in between rounds for user steering |
| `--autonomous` | Autonomous | Runs all rounds, delivers finished document |
| *(default)* | Explore | Divergent — opens possibility space, ends with open questions |
| `--focus` | Focus | Convergent — narrows to one argument, ends with action plan |
| `--vault-only` | Vault-only | Skips web search, uses only vault content |
| `--pdfs` | PDF collection | Explorer downloads relevant PDFs to `<output_dir>/PDFs/` |
| `--plain` | Plain markdown | Output is CommonMark-only — no `[[wikilinks]]`, no `> [!callouts]`. Use for non-Obsidian environments. |

## Installation

Copy the `deep-recon` directory (with `agents/` and `templates/` subdirectories) into your `.claude/skills/` directory:

```
your-project/
└── .claude/
    └── skills/
        └── deep-recon/
            ├── SKILL.md
            ├── agents/
            │   ├── explorer.md
            │   ├── associator.md
            │   ├── critic.md
            │   └── synthesizer.md
            └── templates/
                └── brainstorm-output.md
```

Then add the skill to your `CLAUDE.md` so it appears in the skill list:

```markdown
### /deep-recon - Deep Reconnaissance
Run extended multi-agent reconnaissance sessions. Four specialized agents work in parallel
rounds to map a topic's territory from multiple angles.
```

## Usage

```
/deep-recon <topic or question>
```

Examples:
```
/deep-recon the relationship between infrastructure decay and political legitimacy
/deep-recon --autonomous --focus what makes network culture different from digital culture
/deep-recon --vault-only connections between my notes on sound art and landscape
```

You can also reference specific notes or folders as source material:

```
/deep-recon based on essays/network-culture.md, explore the current state of this argument
```

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with access to the Opus model (the Synthesizer uses Opus for integrative thinking; other agents use Sonnet)
- An Obsidian vault (the skill produces Obsidian-native markdown)
- Web search access (unless using `--vault-only`)

## Output

The skill produces an Obsidian-native markdown document saved to a `recon/` subdirectory, structured as:

- **Central Question** — the refined driving question
- **The Territory** — 3–5 fully developed framings, each standing on its own terms
- **Tensions** — productive frictions between framings, with full treatment of both sides
- **Unexpected Connections** — cross-domain links written as prose
- **Open Questions** — genuinely open, not rhetorical
- **Sources** — vault wikilinks and web references
- **Process Log** — mode, intention, round count, per-round summaries

Individual agent reports are saved alongside as reference material.

## Troubleshooting

### "I don't see my recon document"

The Synthesizer writes the final document directly to disk — it should appear at `<output_dir>/YYYY-MM-DD-<topic-slug>.md`. If it's missing:

- Check the per-agent reports in the same folder (`r1-explorer.md`, `r1-critic.md`, etc.). If those exist but the final doc doesn't, the Synthesizer write failed mid-flight — re-run the skill with the same topic. Agent reports survive across attempts.
- If the agent reports also don't exist, the orchestrator failed before any agent dispatched. Confirm `--output` resolves to a writable directory and that the vault root is in scope.

### "Two runs of the same topic produce different outputs"

This is by design. Web search results vary day-to-day, vault state evolves, and model sampling is non-deterministic. The skill is built for divergent exploration, not reproducibility. If you need repeatable runs, use `--vault-only` and treat the agent reports (`rN-*.md`) as the canonical record — those at least come from a fixed input set.

### "An agent timed out, or one round is missing a report"

The orchestrator handles partial-round failures gracefully — see the **Failure Handling** section in `SKILL.md`. The summary:

- **One agent fails:** the round proceeds with N–1 reports. The Process Log notes the failure.
- **All agents fail in a round:** the orchestrator skips to the final Synthesizer with whatever earlier rounds produced.
- **Synthesizer's final write fails:** the orchestrator retries, and on a second failure writes a stub document pointing the user at the per-agent reports on disk.

Practical recovery as a user:

- Inspect the recon directory for whatever reports landed.
- Read the Process Log in the final document — it tells you which rounds and agents failed.
- Re-run the skill with the same topic if you want a fresh attempt; the orchestrator overwrites per-round files.
- If web search is the consistent failure, add `--vault-only`.

### "The output sounds generic, not like my voice"

The Synthesizer reads existing notes in your vault to match register. If output feels generic:

- Make sure your vault has notes the Synthesizer can find via Grep on the topic's terms.
- If you forked this skill, see [`docs/TUNING.md`](docs/TUNING.md) — the Synthesizer references a personal style guide by default and will need adjustment for your voice.

### "The Process Log shows wrong token counts after a context compaction"

The Process Log reads from `_metrics.md`, which is updated after every round expressly to survive context compaction. If the numbers in the final document look off, check `_metrics.md` directly — it's the source of truth. The orchestrator recovers from compaction by re-reading this file.

### "How much does a typical run cost?"

Token spend depends on vault size, web search depth, and whether you run 2 or 3 rounds. Per-round cost data is recorded in `_metrics.md` — review it after a few runs to calibrate. The Synthesizer (Opus) is the highest single-agent contributor in most runs.

If cost matters, you have two levers:

- **Hard cap:** `--budget <tokens>` — the orchestrator aborts gracefully (writing the best-available draft) before exceeding the cap. See SKILL.md's "Budget Check" section.
- **Cheaper Explorer:** `--explorer-model haiku` is the safest single substitution for cost-sensitive runs. The Synthesizer should remain on Opus — Haiku-on-Synthesizer significantly degrades final-document quality. See SKILL.md's "Agent Model Selection" section for full guidance.

## Documentation

- [`CHANGELOG.md`](CHANGELOG.md) — version history.
- [`docs/TUNING.md`](docs/TUNING.md) — adjusting the Synthesizer's voice for your fork.
- [`examples/`](examples/) — sample recon outputs.

## License

MIT
