#!/usr/bin/env python3
"""
Negative tests for the structural validator.

`check_recon_structure.py` enforces the recon-document contract. This file
asserts the contract is real — the validator must reject malformed inputs,
not just rubber-stamp the example files. Without these tests, a future edit
that loosens or breaks the validator could land silently and the smoke
suite would still pass against the existing examples.

Run via `tests/run_smoke_tests.sh` (which exercises both files), or
directly with `python3 tests/test_validator_contract.py`.

Exit codes:
    0  all assertions held
    1  one or more validator behaviors regressed
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from check_recon_structure import check_recon  # noqa: E402


VALID_EXPLORE = """---
created: 2026-04-24
type: recon
topic: friction in interface design
mode: explore
intention: explore
source_notes: []
---

# Friction

> [!note]- Process Log
> Round 1, Round 2.

> [!abstract] Central Question
> What is friction for?

## The Territory

### Mechanical friction

Lorem [[Don-Norman]].

### Cognitive friction

Ipsum [[slow-design]].

### Social friction

Dolor [[UX-discomfort]].

## Tensions

The pull between [[friction]] as obstacle and friction as scaffold.

## Unexpected Connections

Cross-domain echoes from [[slow-design]].

## Open Questions

What does friction look like institutionally?

## Sources

- [[Don-Norman]]
- example.com[^1]

[^1]: Footnote.
"""

VALID_PLAIN = """---
created: 2026-04-24
type: recon
topic: friction in interface design
mode: explore
intention: explore
source_notes: []
---

# Friction

## Process Log

Round 1, Round 2.

## Central Question

What is friction for?

## The Territory

### Mechanical friction

Lorem (see Don Norman's notes).

### Cognitive friction

Ipsum (slow design tradition).

### Social friction

Dolor (UX discomfort literature).

## Tensions

The pull between friction as obstacle and friction as scaffold.

## Unexpected Connections

Cross-domain echoes from slow design.

## Open Questions

What does friction look like institutionally?

## Sources

- Don Norman, _The Design of Everyday Things_
- example.com[^1]

[^1]: Footnote.
"""

VALID_FOCUS = """---
created: 2026-04-24
type: recon
topic: friction in interface design
mode: focus
intention: focus
source_notes: []
---

# Friction

> [!note]- Process Log
> Round 1.

> [!abstract] Central Question
> Should we design for productive friction?

## The Argument

Friction is a feature, not a bug, when [[Don-Norman]].

## Tensions

Productive vs. pathological [[friction]].

## Next Steps

1. Pilot in [[slow-design]].
2. Measure [[UX-discomfort]] outcomes.

## Sources

- [[Don-Norman]]
- example.com[^1]

[^1]: Footnote.
"""


CASES: list[tuple[str, str, str, bool, list[str]]] = [
    # (name, document, mode, plain, expected_error_substrings)
    # Empty list = expected to pass.
    ("valid Explore (Obsidian)",     VALID_EXPLORE,                                                            "explore", False, []),
    ("valid Plain Explore",          VALID_PLAIN,                                                              "explore", True,  []),
    ("valid Focus (Obsidian)",       VALID_FOCUS,                                                              "focus",   False, []),
    ("missing The Territory",        VALID_EXPLORE.replace("## The Territory", "## NotTerritory"),             "explore", False, ["Missing section: ## The Territory"]),
    ("two framings (under floor)",   VALID_EXPLORE.replace("### Social friction\n\nDolor [[UX-discomfort]].\n\n", ""), "explore", False, ["The Territory has 2 framings"]),
    ("six framings (over ceiling)",  VALID_EXPLORE.replace("## Tensions",                                      "### Fourth\n\nMore [[a]].\n\n### Fifth\n\nMore [[b]].\n\n### Sixth\n\nToo many [[c]].\n\n## Tensions"), "explore", False, ["The Territory has 6 framings"]),
    ("missing frontmatter field",    VALID_EXPLORE.replace("intention: explore\n", ""),                        "explore", False, ["Frontmatter missing field: intention"]),
    ("plain mode with wikilinks",    VALID_PLAIN.replace("see Don Norman's notes", "see [[Don-Norman]]"),      "explore", True,  ["Found wikilink"]),
    ("plain mode with callouts",     VALID_PLAIN.replace("## Process Log\n\nRound", "> [!note]- Process Log\n> Round"), "explore", True,  ["Found Obsidian callout"]),
    ("Obsidian mode no wikilinks",   VALID_EXPLORE.replace("[[Don-Norman]]", "Don Norman").replace("[[slow-design]]", "slow design").replace("[[UX-discomfort]]", "UX discomfort").replace("[[friction]]", "friction"), "explore", False, ["No wikilinks found"]),
]


def run_case(name: str, text: str, mode: str, plain: bool, expected: list[str]) -> bool:
    errors = check_recon(text, mode, plain)
    expected_pass = not expected
    if expected_pass:
        ok = not errors
    else:
        ok = bool(errors) and all(any(sub in e for e in errors) for sub in expected)

    status = "OK  " if ok else "FAIL"
    print(f"{status}  {name}")
    if not ok:
        print(f"        expected: {expected or 'no errors'}")
        print(f"        got:      {errors}")
    return ok


def main() -> int:
    print("Validator contract tests:")
    print()
    results = [run_case(*c) for c in CASES]
    passed = sum(results)
    total = len(results)
    print()
    print(f"{passed}/{total} validator-contract assertions passed.")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
