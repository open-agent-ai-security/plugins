#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Sanity-check .claude-plugin/marketplace.json (the whole point of this repo).

This catalog is the single install path for every community plugin on both
Claude Code and Codex, so a bad `source` here ships arbitrary code to every
user. The rules below are therefore a SECURITY gate, not a style check:

  - sources must be https URLs whose host is exactly github.com and whose
    path is exactly /open-agent-ai-security/<repo>.git — parsed and matched
    in full, never prefix-matched (a bare `startswith` is defeated by
    `https://github.com/open-agent-ai-security/../attacker/repo.git`, which
    git silently normalizes to another org);
  - source type is 'url' (whole repo) or 'git-subdir' (a subdirectory of the
    repo — used when a plugin ships only part of its repo, e.g. socxen#66's
    plugin/ payload split). 'git-subdir' additionally requires `path`: a
    strictly relative, traversal-free directory path — segments of
    [A-Za-z0-9._-] only, no leading/trailing '/', no '.' or '..' segments,
    no backslashes, no whitespace/control characters;
  - alternatively, a source may be a STRING relative path ('./<dir>'): a
    plugin vendored into THIS repo, so installs copy only that directory
    and every payload change is a reviewable diff here rather than a ref
    move in another repo. The path takes the same traversal-free rules as
    git-subdir, the directory must exist, resolve under the repo root, and
    contain no symlinks anywhere (the reviewed tree and the installed tree
    must be the same bytes), it must carry .claude-plugin/plugin.json, and
    that manifest's `name` must equal the entry name (the client keys the
    install by it — a mismatch shadows another plugin's key);
  - every git source pins `ref: main` (each product repo's release channel);
  - for git sources, the entry name matches the target repository name, so
    an entry can't install one plugin under another's key;
  - entries carry no per-release version metadata (each plugin repo's
    plugin.json is the version authority);
  - names/descriptions are well-formed strings the client schema accepts.

Structural checks are stdlib-only so CI needs no dependencies. Claude Code's
own `claude plugin validate .` remains the authoritative schema check; this
runs where that CLI isn't available and enforces conventions it doesn't know
about.

Exit 0 clean, 1 with findings (always a findings list, never a traceback).
"""
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

# Repo root. CATALOG_ROOT exists for the CI gate, which runs MAIN's copy of
# this script from a temp dir against the PR's checkout — without the
# override, vendored-source directory checks would resolve against the temp
# dir and fail closed on every vendored entry (including post-merge pushes
# to main). Unset, the script behaves as before: root = its own repo.
ROOT = Path(os.environ.get("CATALOG_ROOT") or Path(__file__).resolve().parents[1]).resolve()
MANIFEST = ROOT / ".claude-plugin" / "marketplace.json"

MARKETPLACE_NAME = "open-agent-ai-security"
ORG = "open-agent-ai-security"
EXPECTED_REF = "main"
REPO_PATH_RE = re.compile(r"^/" + re.escape(ORG) + r"/([A-Za-z0-9._-]+)\.git$")
PLUGIN_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


# Per-type key allow-lists: an unreviewed field is an install-behaviour change
# slipping past a green check, so each source type admits exactly its own keys.
ALLOWED_SOURCE_KEYS_BY_TYPE = {
    "url": {"source", "url", "ref"},
    "git-subdir": {"source", "url", "ref", "path"},
}
# Subdirectory path: strictly relative, one or more [A-Za-z0-9._-] segments,
# '/'-joined. No leading/trailing slash, no empty segments, no backslashes.
# '.'/'..' segments are matchable by the segment class, so they are rejected
# by an explicit check below — keep both in sync.
SUBDIR_SEGMENT_RE = re.compile(r"^[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*$")


def check_vendored_source(label, src, entry_name, problems):
    """Validate a string source: a plugin directory vendored into this repo."""
    if not src.startswith("./"):
        problems.append(
            f"{label}: a string source must be a repo-relative path starting "
            f"with './' (a vendored plugin directory in this repo), got {src!r}"
        )
        return
    rel = src[2:]
    if any(c.isspace() or ord(c) < 0x20 for c in rel):
        problems.append(f"{label}: source path contains whitespace or control characters: {src!r}")
        return
    if "\\" in rel:
        problems.append(f"{label}: source path must use forward slashes only: {src!r}")
        return
    if not SUBDIR_SEGMENT_RE.match(rel) or any(seg in (".", "..") for seg in rel.split("/")):
        problems.append(
            f"{label}: source path must be './' plus [A-Za-z0-9._-] segments with "
            f"no '.' or '..' segments (directory traversal), got {src!r}"
        )
        return
    plugin_dir = ROOT / rel
    if not plugin_dir.exists():
        problems.append(f"{label}: vendored source directory {src!r} does not exist in this repo")
        return
    if not plugin_dir.is_dir():
        problems.append(f"{label}: vendored source path {src!r} exists but is not a directory")
        return
    # The lexical checks above can't see through symlinks: a committed symlink
    # passes them while pointing anywhere on the validating host, so what got
    # reviewed and what gets installed could differ. Reject any symlink in the
    # payload, and require the directory itself to resolve under the repo root.
    if plugin_dir.is_symlink() or not plugin_dir.resolve().is_relative_to(ROOT):
        problems.append(
            f"{label}: vendored source directory {src!r} is a symlink or escapes "
            f"the repo root once resolved"
        )
        return
    links = sorted(str(p.relative_to(ROOT)) for p in plugin_dir.rglob("*") if p.is_symlink())
    if links:
        shown = ", ".join(links[:3]) + (", …" if len(links) > 3 else "")
        problems.append(
            f"{label}: vendored payload contains symlink(s) ({shown}) — the reviewed "
            f"tree and the installed tree must be the same bytes"
        )
        return
    manifest = plugin_dir / ".claude-plugin" / "plugin.json"
    try:
        pj = json.loads(manifest.read_text())
    except FileNotFoundError:
        problems.append(f"{label}: vendored plugin at {src!r} is missing .claude-plugin/plugin.json")
        return
    except Exception as e:
        problems.append(f"{label}: vendored plugin.json at {src!r} does not parse: {e}")
        return
    if not isinstance(pj, dict):
        problems.append(
            f"{label}: vendored plugin.json at {src!r} must be a JSON object, "
            f"got {type(pj).__name__}"
        )
        return
    pj_name = pj.get("name")
    if entry_name and pj_name != entry_name:
        problems.append(
            f"{label}: vendored plugin.json name {pj_name!r} does not match the entry "
            f"name — the client keys the install by plugin.json's name, so a mismatch "
            f"installs under (or shadows) another plugin's key"
        )
    if not (isinstance(pj.get("version"), str) and pj["version"].strip()):
        problems.append(
            f"{label}: vendored plugin.json must declare a non-empty version — "
            f"with no source repo to consult, it is the only version authority"
        )


def check_source(label, src, entry_name, problems):
    """Fully validate a plugin source (object, or vendored-path string). Adds to `problems`."""
    if isinstance(src, str):
        check_vendored_source(label, src, entry_name, problems)
        return
    if not isinstance(src, dict):
        problems.append(
            f"{label}: source must be an object (git source) or a './<dir>' string "
            f"(vendored plugin), got {type(src).__name__}"
        )
        return
    stype = src.get("source")
    if stype not in ALLOWED_SOURCE_KEYS_BY_TYPE:
        problems.append(
            f"{label}: source.source must be 'url' (whole repo) or 'git-subdir' "
            f"(subdirectory; the 'github' type clones over SSH and fails for users "
            f"without GitHub SSH keys), got {stype!r}"
        )
        allowed = set().union(*ALLOWED_SOURCE_KEYS_BY_TYPE.values())
    else:
        allowed = ALLOWED_SOURCE_KEYS_BY_TYPE[stype]
    extra = sorted(set(src) - allowed)
    if extra:
        problems.append(
            f"{label}: unexpected source key(s) {extra} for source type {stype!r} — "
            f"this type admits exactly {sorted(allowed)}; add support deliberately "
            f"if a new field is needed"
        )
    if stype == "git-subdir":
        path = src.get("path")
        if not isinstance(path, str) or not path:
            problems.append(
                f"{label}: git-subdir requires a non-empty string 'path', got {path!r}"
            )
        elif any(c.isspace() or ord(c) < 0x20 for c in path):
            problems.append(
                f"{label}: source.path contains whitespace or control characters: {path!r}"
            )
        elif "\\" in path:
            problems.append(f"{label}: source.path must use forward slashes only: {path!r}")
        elif not SUBDIR_SEGMENT_RE.match(path):
            problems.append(
                f"{label}: source.path must be a relative directory path of "
                f"[A-Za-z0-9._-] segments (no leading/trailing '/', no empty "
                f"segments), got {path!r}"
            )
        elif any(seg in (".", "..") for seg in path.split("/")):
            problems.append(
                f"{label}: source.path must not contain '.' or '..' segments "
                f"(directory traversal), got {path!r}"
            )
    url = src.get("url")
    if not isinstance(url, str) or not url:
        problems.append(f"{label}: source.url must be a non-empty string, got {url!r}")
    elif any(c.isspace() or ord(c) < 0x20 for c in url):
        # urlsplit silently strips tabs/newlines, so a URL containing them parses
        # as something other than what a reader (or another tool) sees.
        problems.append(f"{label}: source.url contains whitespace or control characters: {url!r}")
    else:
        parts = urlsplit(url)
        # Parse, don't prefix-match: '.../open-agent-ai-security/../other/x.git'
        # would satisfy a startswith check but clones from another org.
        if parts.scheme != "https":
            problems.append(f"{label}: source.url must use https, got scheme {parts.scheme!r}")
        if parts.netloc != "github.com":
            problems.append(
                f"{label}: source.url host must be exactly 'github.com' "
                f"(no userinfo, port, or alternate host), got {parts.netloc!r}"
            )
        if parts.query or parts.fragment:
            problems.append(f"{label}: source.url must have no query string or fragment")
        m = REPO_PATH_RE.match(parts.path)
        if not m:
            problems.append(
                f"{label}: source.url path must be exactly "
                f"'/{ORG}/<repo>.git', got {parts.path!r}"
            )
        elif entry_name and m.group(1).lower() != entry_name.lower():
            problems.append(
                f"{label}: entry name {entry_name!r} does not match target repository "
                f"{m.group(1)!r} — an entry must not publish another repo under its key"
            )
    ref = src.get("ref")
    if ref != EXPECTED_REF:
        problems.append(
            f"{label}: source.ref must be {EXPECTED_REF!r} (each product repo's release "
            f"channel; an unpinned or integration-branch ref ships unreleased code), got {ref!r}"
        )


def main() -> int:
    problems = []
    try:
        m = json.loads(MANIFEST.read_text())
    except FileNotFoundError:
        print(f"{MANIFEST} not found", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"marketplace.json does not parse: {e}", file=sys.stderr)
        return 1

    if not isinstance(m, dict):
        print("marketplace.json must be a JSON object", file=sys.stderr)
        return 1

    if m.get("name") != MARKETPLACE_NAME:
        problems.append(f"marketplace name must be {MARKETPLACE_NAME!r}, got {m.get('name')!r}")

    owner = m.get("owner")
    if not isinstance(owner, dict):
        problems.append(f"owner must be an object, got {type(owner).__name__}")
    else:
        for k in ("name", "url"):
            if not isinstance(owner.get(k), str) or not owner[k].strip():
                problems.append(f"owner.{k} must be a non-empty string, got {owner.get(k)!r}")

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
        if not isinstance(name, str) or not PLUGIN_NAME_RE.match(name):
            problems.append(
                f"{label}: name must be a lowercase string matching "
                f"{PLUGIN_NAME_RE.pattern} (no spaces — the client schema rejects them)"
            )
            name = None
        elif name in seen:
            problems.append(f"{label}: duplicate name — a duplicate silently shadows the other entry")
        else:
            seen.add(name)
        desc = e.get("description")
        if not isinstance(desc, str) or not desc.strip():
            problems.append(f"{label}: description must be a non-empty string, got {desc!r}")
        if "version" in e:
            problems.append(
                f"{label}: carries a version — catalog entries must not; "
                "each plugin repo's plugin.json is the version authority"
            )
        check_source(label, e.get("source"), name, problems)

    if problems:
        print("catalog manifest problems:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(
        f"catalog manifest OK — {len(plugins)} plugin(s); every source is an https "
        f"github.com/{ORG}/<name>.git URL on the {EXPECTED_REF} branch or a vendored "
        f"'./<dir>' in this repo, with no entry-level version metadata."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
