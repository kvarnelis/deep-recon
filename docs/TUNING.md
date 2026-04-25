# Tuning for your voice

The Synthesizer agent is the only one that produces user-facing prose — the recon document itself. To make that prose feel like your thinking extended, not generic AI output, the Synthesizer reads notes from your vault to match register, vocabulary, and theoretical commitments.

It also reads a hardcoded personal style guide. If you forked this skill, you almost certainly need to change that.

## The hardcoded reference

Open `agents/synthesizer.md` and look at the **Voice (CRITICAL)** section. The current text:

```markdown
The final document must sound like the user extended their own thinking, not like a philosophy seminar. Read `_resources/Kazys Varnelis – Personal Writing Style Guide.md` before drafting.
```

That path resolves against the vault root the skill is invoked in. If you don't have a file at that exact path, one of two things happens:

1. **The Synthesizer's `Read` call fails silently**, and the agent falls back to whatever voice it can extract from your other vault notes — usually serviceable, sometimes generic.
2. **The Synthesizer surfaces the failure** in its agent report (`rN-synthesizer.md`), and the final document includes a note that the style guide was unavailable.

Either way, you're not getting the voice-tuning the original author built into the skill.

## Three ways to fix it

### Option 1 — Replace the path with your own style guide (recommended)

Write a short style guide that captures your voice. Save it to your vault. Update `agents/synthesizer.md` to point at it.

Example diff:

```diff
- Read `_resources/Kazys Varnelis – Personal Writing Style Guide.md` before drafting.
+ Read `_meta/my-writing-voice.md` before drafting.
```

Commit the change to your fork. You're done.

### Option 2 — Remove the hardcoded reference

If you'd rather have the Synthesizer rely entirely on whatever notes it Greps up during the recon, just delete the sentence. The rest of the **Voice** section already describes what good prose looks like.

```diff
- The final document must sound like the user extended their own thinking, not like a philosophy seminar. Read `_resources/Kazys Varnelis – Personal Writing Style Guide.md` before drafting.
+ The final document must sound like the user extended their own thinking, not like a philosophy seminar.
```

This produces softer voice-matching, but it works for any forker out of the box.

### Option 3 — Make the path configurable

If you publish a fork and want others to customize without editing prompts, parameterize the path. Add to your `SKILL.md` arg-parsing logic:

```markdown
8. **Voice guide override** (optional):
   - `--voice-guide <path>`: Read this file in the Synthesizer prompt instead of the default
   - Default: `_resources/personal-style-guide.md` (or whatever you set)
```

Then update `agents/synthesizer.md` to use a placeholder:

```markdown
Read `{{voice_guide_path}}` before drafting.
```

The orchestrator substitutes the value (or the default) into the agent prompt at dispatch time. This is more work but the most robust path for a public fork.

## Writing a personal style guide

The Synthesizer's existing voice rules (in the same section of `agents/synthesizer.md`) tell you what kind of guide is useful. Concretely:

**Declarative register.** The Synthesizer wants to write declarative claims, not hedged observations. Your guide should give it permission to do that — explicit examples of you making categorical assertions.

**Concrete stakes.** It wants abstraction tethered to specific cases. Your guide should show what "the right level of abstraction" looks like for you — usually with an example paragraph that names a specific work, person, or moment.

**Register tests.** What words or phrases do you avoid? "Performative," "embodied," "interrogate" all set the Synthesizer's alarm. Tell it your own list.

**Sentence rhythm.** Short staccato vs. long discursive. Most of us mix both. Show it the mix you actually use.

A useful guide is 200–500 words. Longer than that and the Synthesizer will start to over-fit on the guide instead of your actual notes.

## Verifying the change worked

Run a recon on a topic you've written about before. Read the output. Three checks:

1. **Vocabulary match.** Are the words ones you'd actually use? If you see "interrogate" or "robust" or "leverage," tighten the guide.
2. **Cadence match.** Read a paragraph aloud. Does it sound like something you'd say to a smart colleague? If it sounds like a qualifying exam, the Synthesizer is still in seminar mode.
3. **Stakes match.** Are the abstractions tethered to concrete cases you'd reach for? If everything floats at the level of "the relationship between X and Y," more concrete examples in your guide will help.

If a few iterations of guide-tuning still produce generic output, the issue is usually upstream: too few notes in the vault for the Synthesizer's Grep to find your voice in the first place. The Synthesizer can't extrapolate a register it has no examples of.

## Related

- `agents/synthesizer.md` — the prompt itself, including the Voice and Epistemic Honesty sections.
- `SKILL.md` — orchestrator logic, including how the Synthesizer gets dispatched.
- The README's [Troubleshooting](../README.md#troubleshooting) entry on generic-sounding output.
