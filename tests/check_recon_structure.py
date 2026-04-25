#!/usr/bin/env python3
"""
Structural validator for deep-recon output documents.

Asserts the contract that every recon document must satisfy:
  - YAML frontmatter with required fields
  - Required ## sections per mode
  - Process Log callout
  - Central Question callout
  - Territory framings: 3-5 (Explore mode)
  - Obsidian flavoring (wikilinks) unless --plain

Use this as a fast post-hoc check on a real recon output. Catches
structural regressions from prompt edits without false-positives
on prose variation.

Usage:
    python3 check_recon_structure.py <recon-file> [--mode explore|focus] [--plain]

Exit codes:
    0  OK
    1  one or more structural errors
    2  bad invocation
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_FRONTMATTER_FIELDS = ["created", "type", "topic", "mode", "intention"]

REQUIRED_SECTIONS = {
    "explore": [
        "The Territory",
        "Tensions",
        "Unexpected Connections",
        "Open Questions",
        "Sources",
    ],
    "focus": [
        "The Argument",
        "Tensions",
        "Next Steps",
        "Sources",
    ],
}


def check_recon(text: str, mode: str, plain: bool) -> list[str]:
    errors: list[str] = []

    fm_match = re.match(r"^---\n(.+?)\n---\n", text, re.DOTALL)
    if not fm_match:
        errors.append("Missing YAML frontmatter delimiters (---)")
        fm_text = ""
    else:
        fm_text = fm_match.group(1)

    for field in REQUIRED_FRONTMATTER_FIELDS:
        if not re.search(rf"^{re.escape(field)}\s*:", fm_text, re.MULTILINE):
            errors.append(f"Frontmatter missing field: {field}")

    for section in REQUIRED_SECTIONS[mode]:
        if not re.search(rf"^## {re.escape(section)}\s*$", text, re.MULTILINE):
            errors.append(f"Missing section: ## {section}")

    if mode == "explore":
        territory = re.search(
            r"^## The Territory\s*$(.+?)(?=^## )",
            text,
            re.MULTILINE | re.DOTALL,
        )
        if territory:
            subheadings = re.findall(r"^### ", territory.group(1), re.MULTILINE)
            if not (3 <= len(subheadings) <= 5):
                errors.append(
                    f"The Territory has {len(subheadings)} framings; expected 3-5"
                )

    if not plain:
        if not re.search(r">\s*\[!note\][-\s]*Process Log", text):
            errors.append("Missing Process Log callout (> [!note] ... Process Log)")
        if not re.search(r">\s*\[!abstract\]\s*Central Question", text):
            errors.append("Missing Central Question callout (> [!abstract] Central Question)")
        if not re.search(r"\[\[[^\]]+\]\]", text):
            errors.append(
                "No wikilinks found ([[link]]); Obsidian-flavored output expected (use --plain for plain markdown)"
            )
    else:
        if re.search(r">\s*\[!", text):
            errors.append("Found Obsidian callout (> [!...]) in --plain output")
        if re.search(r"\[\[[^\]]+\]\]", text):
            errors.append("Found wikilink ([[...]]) in --plain output")
        if not re.search(r"^## Central Question\s*$", text, re.MULTILINE):
            errors.append("Missing Central Question section (## Central Question) in --plain mode")

    return errors


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Structural validator for deep-recon outputs."
    )
    parser.add_argument("filepath", help="Path to a recon .md file")
    parser.add_argument(
        "--mode",
        choices=["explore", "focus"],
        default="explore",
        help="Output mode the file should match (default: explore)",
    )
    parser.add_argument(
        "--plain",
        action="store_true",
        help="Validate plain-markdown output (no Obsidian flavoring)",
    )
    args = parser.parse_args(argv[1:])

    path = Path(args.filepath)
    if not path.is_file():
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    errors = check_recon(text, args.mode, args.plain)

    label = f"{args.mode}{' --plain' if args.plain else ''}"
    if errors:
        print(f"FAIL: {path} ({label})")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"OK: {path} ({label})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
