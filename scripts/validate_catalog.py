#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Sanity-check .claude-plugin/marketplace.json (the whole point of this repo).

Structural rules only — the authoritative schema is Claude Code's own
(`claude plugin validate .`), which CI runners don't have; this catches the
mistakes that would silently break `marketplace add` or violate the catalog's
own conventions (https-only pinned sources, no per-release version metadata).
Exit 0 clean, 1 with findings.
"""
import json
import sys
from pathlib import Path

MANIFEST = Path(__file__).resolve().parents[1] / ".claude-plugin" / "marketplace.json"


def main() -> int:
    problems = []
    try:
        m = json.loads(MANIFEST.read_text())
    except Exception as e:
        print(f"marketplace.json does not parse: {e}", file=sys.stderr)
        return 1

    if m.get("name") != "open-agent-ai-security":
        problems.append(f"marketplace name must be 'open-agent-ai-security', got {m.get('name')!r}")
    owner = m.get("owner") or {}
    if not (owner.get("name") and owner.get("url")):
        problems.append("owner.name and owner.url are required")

    plugins = m.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        problems.append("plugins must be a non-empty list")
        plugins = []

    seen = set()
    for i, e in enumerate(plugins):
        label = f"plugins[{i}]"
        if not isinstance(e, dict):
            problems.append(f"{label}: not an object")
            continue
        name = e.get("name")
        label = f"plugins[{i}] ({name!r})"
        if not name or not isinstance(name, str):
            problems.append(f"{label}: missing name")
        elif name in seen:
            problems.append(f"{label}: duplicate name — a duplicate silently shadows the other entry")
        else:
            seen.add(name)
        if not e.get("description"):
            problems.append(f"{label}: missing description")
        if "version" in e:
            problems.append(
                f"{label}: carries a version — catalog entries must not; "
                "each plugin repo's plugin.json is the version authority"
            )
        src = e.get("source")
        if not isinstance(src, dict):
            problems.append(f"{label}: source must be an object")
        else:
            if src.get("source") != "url":
                problems.append(
                    f"{label}: source.source must be 'url' (the 'github' type clones over SSH "
                    "and fails for users without GitHub SSH keys)"
                )
            url = src.get("url", "")
            if not url.startswith("https://github.com/open-agent-ai-security/"):
                problems.append(f"{label}: source.url must be an https URL under the org, got {url!r}")
            if not src.get("ref"):
                problems.append(
                    f"{label}: source.ref is required — unpinned sources track the default "
                    "branch, which may be an integration branch"
                )

    if problems:
        print("catalog manifest problems:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"catalog manifest OK — {len(plugins)} plugin(s), all sources https-pinned, no version metadata.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
