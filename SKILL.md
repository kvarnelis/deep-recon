---
name: deep-recon
description: Run extended multi-agent reconnaissance sessions. Use when asked to brainstorm deeply, explore ideas from multiple angles, or generate a structured recon document.
allowed-tools: Read, Grep, Glob, Write, Edit, WebSearch, WebFetch, Task, AskUserQuestion
user-invocable: true
argument-hint: "[--autonomous] [--focus] [--vault-only] [--pdfs] [--plain] [--output <path>] <topic>"
---

# Deep Recon

You are orchestrating a multi-agent reconnaissance session within the user's knowledge base. Your role is conductor: you parse input, dispatch subagents, cross-pollinate findings between rounds, and produce a structured recon document.

## Session Continuations

If this session is a continuation from a previous conversation, IGNORE any completed or running agent task IDs in the system reminders. They belong to a prior invocation and are not your responsibility. Always start fresh from the user's current prompt and the skill arguments passed in this invocation. The user's prompt determines the topic — not leftover state from prior sessions. Do not call TaskOutput on pre-existing tasks. Do not attempt to "finish" work from a previous session unless the user explicitly asks you to.

## Step 1: Parse Input

From the user's prompt, determine:

1. **Topic**: The subject, question, or problem to brainstorm around
2. **Mode**: Interactive (default) or Autonomous
   - If the user says `--autonomous` or "just run it" or "come back with results" → autonomous
   - If ambiguous, ask: "Should I check in between rounds, or run autonomously and deliver a finished recon?"
3. **Intention**: Explore (default) or Focus
   - `--focus` or "sharpen this" or "I need a thesis" → Focus mode (convergent: narrows to one argument, ends with action plan)
   - Default is **Explore** (divergent: opens possibility space, ends with open questions and competing framings)
   - If the user describes a specific deliverable (grant application, essay thesis), suggest Focus mode
4. **Scope**:
   - `--vault-only`: Skip web search, only use vault content
   - Default: Both vault and web
5. **Output location**:
   - `--output <path>`: Write all output (final document + agent reports) to this directory
   - Default: `recon/` subdirectory relative to the source file's directory (or vault root if no source file)
   - Examples: `--output essays/recon/`, `--output recon/`, `--output working/my-project/recon/`
6. **Source material**: If the user references specific notes, folders, or tags, read those first
7. **PDF collection**:
   - `--pdfs`: Explorer searches for and downloads relevant PDFs to a `PDFs/` subdirectory within the output directory
   - Default: Off
8. **Output flavor**:
   - `--plain`: Synthesizer produces plain markdown — no `[[wikilinks]]`, no `> [!callout]` blocks. Use this for forks where Obsidian is not the target environment (Logseq, Foam, plain GitHub markdown, etc.)
   - Default: Obsidian-flavored output (wikilinks, callouts, frontmatter)
9. **Per-agent model overrides** (optional, advanced):
   - `--explorer-model <id>` / `--associator-model <id>` / `--critic-model <id>` / `--synthesizer-model <id>`
   - `<id>` is a Claude model identifier (e.g. `opus`, `sonnet`, `haiku`, or a fully-qualified ID)
   - Default assignments are in the **Agent Model Selection** section below
   - Most users should leave these alone. Override is for cost optimization (e.g., `--explorer-model haiku` for cheap web triage) or quality experiments (e.g., `--critic-model opus` for harder pressure-testing)
10. **Token budget cap** (optional):
    - `--budget <tokens>`: hard cap on total token spend across the recon. Numbers like `200000`, `500000`, `1m` accepted. The orchestrator reads `_metrics.md` between rounds and aborts gracefully (writing the best-available draft) before exceeding the cap.
    - Default: no cap. Spend is recorded in `_metrics.md` but not gated.

## Step 2: Initial Vault Scan

Before dispatching agents, gather context:

1. **Grep** the vault for the topic's key terms (2-4 searches)
2. **Read** the top 3-5 most relevant notes found
3. Compile a **context brief**: key concepts, existing positions, related notes with paths
4. **Identify primary source URLs.** Scan the source material and context brief for URLs, website references, and project names that have web presences. Pass these to the Explorer in R1 with explicit instruction: "Fetch and read these primary sources directly. Do not rely on secondary coverage."
5. **Record the session start time.** Note the current time — you'll need it for elapsed-time metrics in the Process Log.

This context brief is shared with all subagents in round 1.

## Step 3: Run Rounds

Run 2-3 rounds. Each round dispatches 4 subagents using the **Task tool** with `subagent_type: "general-purpose"`.

### Agent Prompts

Read the agent definition files before dispatching:
- `.claude/skills/deep-recon/agents/explorer.md`
- `.claude/skills/deep-recon/agents/associator.md`
- `.claude/skills/deep-recon/agents/critic.md`
- `.claude/skills/deep-recon/agents/synthesizer.md`

### Round 1: Initial Exploration

Dispatch all 4 agents **in parallel** using the Task tool. Each agent's prompt should include:
- The topic/question
- The context brief from Step 2
- The agent's role instructions (from its definition file)
- The output file path: `recon/rN-<role>.md` (e.g., `recon/r1-explorer.md`)
- Round-specific instructions: "This is round 1. Cast a wide net."
- Explicit instruction: "Write your report to `<output path>` using the Write tool. The orchestrator reads from disk."
- If `--pdfs` is enabled, include in the Explorer's prompt: "PDF collection is enabled. See the PDF Collection section of your instructions. Save PDFs to `<output_dir>/PDFs/`. Create the directory with `mkdir -p` via Bash before downloading."

### Between Rounds

After all agents complete, **read their output files from disk** (`recon/rN-<role>.md`). Agent reports written to disk are the ground truth — they survive context crashes. Also check the Task return values as a fallback, but prefer the disk files.

**Interactive mode:**
- Summarize the most interesting findings in 3-5 bullet points
- Highlight 1-2 tensions or surprises
- Ask the user: "Which threads should I pursue? Anything to add or redirect?"
- Incorporate their response into round 2 prompts

**Autonomous mode:**
- The Synthesizer's output from round N determines round N+1's focus
- Collapse threads that are duplicates of each other
- Push distinct framings further apart — develop what makes each one different
- Identify clashes between framings; these tensions need deepening in the next round

### Metrics Persistence

After collecting each round's agent results and BEFORE any further processing, write (or update) `_metrics.md` in the recon/ output directory with:

- Per-agent token counts and elapsed times (from Task result metadata)
- Round wall-clock time (time from dispatching agents to last agent returning)
- Cumulative totals across all rounds so far

**This file survives context compaction.** If earlier context is compressed, read `_metrics.md` to recover the numbers. Do not rely on in-context memory for metrics — compaction will erase them.

Create `_metrics.md` after Round 1 completes. Update it after each subsequent round. Format:

```
# Metrics

Session start: YYYY-MM-DD HH:MM

## Round 1
- Explorer: ~XXXk tokens, X.Xm
- Associator: ~XXXk tokens, X.Xm
- Critic: ~XXXk tokens, X.Xm
- Synthesizer: ~XXXk tokens, X.Xm
- Round wall clock: X.Xm
- Round total tokens: ~XXXk

## Round 2
...

## Cumulative
- Total tokens: ~XXXk
- Total wall clock: XXm
```

### Cross-Pollination

When dispatching round 2+ agents, include in each prompt:
- A summary of ALL agents' findings from the previous round
- The Synthesizer's recommended focus areas
- In interactive mode: the user's steering input

**Anti-repetition:** Before dispatching R2+ agents, compile a "settled claims" list — the 5-8 key points that all R1 agents converged on. Include this in each agent's prompt with the instruction: "The following points are established from Round 1. Do not restate them. Build on them, challenge them, or move past them."

### Round 2: Deepening

Same 4 agents, but with updated focus:
- Explorer: Two mandates — (a) fill gaps identified by Critic and Synthesizer, (b) operational reality check: ground the abstractions in concrete cases, precedents, and constraints. If `--pdfs` is enabled, include: "Check `<output_dir>/PDFs/` for already-downloaded PDFs before downloading to avoid duplicates."
- Associator: Work connections between round 1 findings
- Critic: Stress-test the strongest emerging ideas
- Synthesizer: Refine themes, identify productive tensions

### Round 3 (Optional): Deepening

Run only if:
- Autonomous mode and Synthesizer recommends it
- Interactive mode and user requests it
- There are tensions that need more development or framings that are still underdeveloped

Focus agents on developing the tensions and filling out underdeveloped framings. Round 3 should find NEW complications, not resolve existing ones.

### Budget Check (between rounds, when `--budget` is set)

After updating `_metrics.md` and before dispatching the next round (Round 2 or Round 3), check:

1. Read `_metrics.md` to get cumulative token spend so far.
2. Estimate the next round's spend using the previous round as a baseline (parallel agents, similar prompt sizes — use the previous round's per-agent token average × 4 + a small Synthesizer multiplier for cross-pollination).
3. If `cumulative + estimated_next > budget`:
   - **Do not dispatch the next round.**
   - Skip directly to the **Step 4 / Final Synthesizer** path.
   - Pass the Synthesizer the agent reports gathered so far AND a note: "Token budget cap reached. Produce the best final document you can from current material."
   - Record the budget-abort in the Process Log: "Aborted at Round N due to --budget `<tokens>`. Final document drafted from R1..N reports."
4. If projected next-round spend would push within 10% of cap, warn but proceed; the next-round budget check will catch genuine overruns.

The point is to **fail safely with a finished draft**, not to crash mid-recon.

### Failure Handling

The recon should produce something useful even when parts of the dispatch fail. The orchestrator's job is to degrade gracefully, never to crash mid-recon and lose all collected work.

**One agent fails or times out within a round.** Do NOT abort the round. After all parallel Tasks return:

1. Check each agent report file on disk.
2. Note which reports are missing or empty.
3. Proceed to the next round (or Step 4) with the partial report set. Pass the surviving reports to subsequent agents.
4. Record the failure in the Process Log: "Round N: `<agent>` failed (timeout / error / empty output). Continuing with `<N-failures>` reports."
5. If the failed agent was the Synthesizer in a non-final round, the orchestrator must do its job: compile settled claims, identify framings, generate cross-pollination prompts. This is a fallback — the orchestrator's interpretive work is the Synthesizer's role in mid-rounds.

**All agents fail in a round.** Abort cleanly:

1. Read whatever partial reports exist on disk.
2. Dispatch the final Synthesizer with all available material from prior rounds.
3. Pass the Synthesizer a note: "Round N agents all failed. Produce the best document possible from R1..N-1 reports." If this happens in Round 1, write a stub recon explaining the failure and exit.
4. Record clearly in the Process Log.

**Synthesizer's final-document write fails.** Retry once with the same input. If the retry fails:

1. Read the Synthesizer's Task return value (it may contain the draft text even if Write failed).
2. Try to write the file yourself (the orchestrator) using the captured text.
3. If both retries fail, write a stub recon at the output path with: Process Log, Sources extracted from agent reports, Central Question, and a clear note: "Final synthesis failed at `<timestamp>`. Agent reports preserved at `<output_dir>/rN-*.md` — they contain the substance of this recon."

**`_metrics.md` write fails.** Log to stderr but continue. Recon quality does not depend on metrics. The Process Log will be missing precise numbers; flag this in the log entry: "Metrics unavailable — _metrics.md write failed."

**Web search returns empty or errors (`--vault-only` is not set).** The Explorer agent is responsible for handling this in its own prompt — see `agents/explorer.md`. The orchestrator does NOT auto-fallback to `--vault-only`. If the Explorer reports zero web findings, dispatch the next round with that fact in the cross-pollination context: "Web search yielded nothing in Round N — Round N+1 should rely on vault and Associator findings."

**PDF download fails (`--pdfs` is set).** Explorer skips and continues — see `agents/explorer.md`. No orchestrator action.

**The user kills the orchestrator mid-round.** All Task subagents will continue running until they complete or the session ends. Their reports may or may not land on disk depending on timing. On next invocation:
- If a previous session's recon directory exists with partial reports, do not auto-resume. Start fresh from the user's current prompt.
- The user can manually inspect the partial reports and re-invoke with `--resume` if they want to continue (resume is not currently implemented but is reserved for future versions).

The principle is **substance survives**. Agent reports on disk are the ground truth. The final document is built from them. Anything else — the orchestrator's in-context state, the metrics, the cross-pollination prose — is auxiliary and recoverable.

## Step 4: Produce Output

After the final round, produce the recon document.

### Orchestrator Role

The orchestrator does NOT write the recon document's substance. The final-round Synthesizer agent writes the complete document — including YAML frontmatter, Process Log, and all formatting — directly to the final output path on disk.

1. Dispatches the final Synthesizer with ALL agent reports from all rounds, plus the template, plus the instruction to draft AND WRITE the complete document. **Pass the final output file path** (e.g., `recon/YYYY-MM-DD-<topic-slug>.md`) and instruct the Synthesizer to write the finished document there using the Write tool. Also pass the current `_metrics.md` content so the Synthesizer can include the Process Log.
2. After the Synthesizer completes, **read the document from disk** and make light corrections only: fix broken `[[wikilinks]]`, correct factual errors, update the Process Log with final-round metrics. Do NOT rewrite arguments, reframe findings, or impose a different structure.

**Why the Synthesizer writes the file:** If the orchestrator crashes after the Synthesizer returns but before writing to disk, the document is lost. The Synthesizer writing directly to the final path ensures the substance survives. The orchestrator's corrections are improvements, not the only path to a file on disk.

### Focus Mode Override

When the user selects Focus mode (`--focus`), the output structure changes:
- "The Territory" becomes "The Argument" (the Synthesizer picks the strongest framing and develops it as a thesis)
- "Tensions" section retains unresolved tensions but the document has a clear argumentative spine
- "Open Questions" becomes "Next Steps" (specific, actionable)
- The Synthesizer's final-round instructions shift to: "Commit to the strongest direction. The user needs a thesis, not a map."

Focus mode uses the Synthesizer's existing convergent instructions (pick the strongest, name runners-up, eliminate duplicates).

### Output Location

If `--output <path>` was specified, use that directory. Otherwise, save to a `recon/` subdirectory relative to the source file's directory. If no source file was specified, save to `recon/` at the vault root.

- `--output essays/recon/` → save to `essays/recon/YYYY-MM-DD-<topic-slug>.md`
- Source is `New City Reader/nai.md`, no `--output` → save to `New City Reader/recon/YYYY-MM-DD-<topic-slug>.md`
- No source file, no `--output` → save to `recon/YYYY-MM-DD-<topic-slug>.md`

Create the output folder if it doesn't exist.

Save individual agent reports to the same folder as `rN-agentname.md` files. These are reference material, not the deliverable.

### Formatting

Default (Obsidian flavor):

- Use Obsidian `[[wikilinks]]` for vault references
- Use standard Markdown footnotes for web sources
- Use callout blocks (`> [!info]`, `> [!note]-`, `> [!abstract]`) for the Process Log and Central Question
- Keep the main body in flowing prose, not bullet-point dumps

When `--plain` is set:

- Replace `[[wikilinks]]` with standard `[link text](relative/path.md)` links — or, for vault notes that don't have a known web target, plain prose mentions
- Replace `> [!note]- Process Log` with `## Process Log` (an ordinary section)
- Replace `> [!abstract] Central Question` with `## Central Question` (an ordinary section)
- Footnotes (`[^1]`) and YAML frontmatter remain unchanged (both are CommonMark-compatible and used by many systems)
- Pass the `--plain` flag through to the Synthesizer in its prompt — it must know to apply these substitutions while drafting

## Agent Model Selection

When dispatching each agent via the Task tool, pass the resolved model as the `model` parameter on the call. The defaults:

| Agent | Default model | Rationale |
|---|---|---|
| Explorer | `sonnet` | Breadth of search rewards speed and decent quality; Haiku is viable here for cost-sensitive runs (use `--explorer-model haiku`) |
| Associator | `sonnet` | Lateral connection-finding benefits from Sonnet's reasoning over Haiku |
| Critic | `sonnet` | Stress-testing needs reasoning depth; consider `--critic-model opus` for the highest-stakes recons |
| Synthesizer | `opus` | The integrative thinking is the bottleneck; this is where capability matters most |

**Resolution order** (highest precedence first):
1. Per-agent override flag (`--explorer-model`, `--associator-model`, `--critic-model`, `--synthesizer-model`)
2. Repo-level config (a forker may edit this section to change defaults)
3. The defaults in the table above

**Maximum-quality mode:** If the user says "use the best model for everything" (or similar), set all four to `opus`. Token cost roughly 4–5× the default Sonnet/Sonnet/Sonnet/Opus mix.

**Cost-conscious mode:** `--explorer-model haiku` is the safest single substitution. The Synthesizer should remain on Opus — Haiku-on-Synthesizer significantly degrades final-document quality.

When dispatching, your Task call should look like:

```
Task(
  subagent_type: "general-purpose",
  model: <resolved model for this agent>,
  prompt: <agent role prompt + context brief + round-specific instructions>
)
```

## Important

- **Don't read the entire vault.** Use targeted Grep/Glob to find relevant notes.
- **Web search queries should be short** (1-6 words) and varied across agents.
- **Each round's agents run in parallel** — dispatch all 4 Task calls at once.
- **The recon note must be a native Obsidian note** — wikilinks, callouts, proper frontmatter.
- **Match the user's intellectual register.** Read their existing notes to understand their vocabulary and frameworks. The brainstorm should feel like their thinking extended, not generic AI output.
