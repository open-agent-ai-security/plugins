# Open Agent AI Security — Plugin Marketplace

The single plugin marketplace for the
[Open Agent AI Security](https://open-agent-ai-security.github.io/) community — serving both
[Claude Code](https://claude.com/claude-code) and [OpenAI Codex](https://openai.com/codex/).

> **This repository exists solely to serve the community's plugin catalog** — one marketplace
> manifest (`.claude-plugin/marketplace.json`) plus this README. There is no product code here:
> each plugin's source, documentation, issues, and contributions live in its own repo (linked
> below). This repo changes only to add a plugin or update a catalog entry, via a reviewed PR.

Add it once:

```bash
claude plugin marketplace add open-agent-ai-security/plugins
```

Then install what you need:

```bash
claude plugin install praxen@open-agent-ai-security
claude plugin install raffkin@open-agent-ai-security
```

| Plugin | What it does | Repo |
|---|---|---|
| **praxen** | Agent behavior verifier — compares an AI agent's declared policy (Worker Remit) against the available evidence and reports where observed behavior diverges from declared intent, scored against the RAISE framework and OWASP LLM/Agentic guidance. | [open-agent-ai-security/praxen](https://github.com/open-agent-ai-security/praxen) |
| **raffkin** | Agentic SOC analyst — triages Exabeam New-Scale alerts and cases end to end via the Exabeam MCP, with governance gates and guardrails. | [open-agent-ai-security/raffkin](https://github.com/open-agent-ai-security/raffkin) |

The in-session equivalents (`/plugin marketplace add …`, `/plugin install …`) do the same
thing; run `/reload-plugins` (or restart the session) after an in-session install.

## Migrating from an older install path

Praxen was previously distributed from a marketplace hosted in its own repo. The
marketplace name (`open-agent-ai-security`) and the plugin key are unchanged, so migration
is one command and nothing about your installed plugin is lost.

**Praxen users** — if you added the marketplace from `open-agent-ai-security/praxen`,
just add this one; the same-named marketplace is re-pointed in place and your installed
praxen keeps working:

```bash
claude plugin marketplace add open-agent-ai-security/plugins
```

Do **not** run `claude plugin marketplace remove` first — removing a marketplace
uninstalls the plugins that came from it, and it isn't necessary. Migrating is optional
for praxen (the legacy repo still publishes a praxen-only marketplace) but **required to
install raffkin**, which only this catalog publishes.

## OpenAI Codex

The same catalog serves Codex, with the same plugin keys:

```bash
codex plugin marketplace add open-agent-ai-security/plugins
codex plugin add praxen@open-agent-ai-security
codex plugin list
```

## For maintainers

- Index entries are deliberately minimal — no per-release version metadata. Each plugin
  repo's `plugin.json` is the version authority, so product releases never require a
  change here. Touch this repo only to add a plugin or update a description.
- Entries target each plugin repo's `main` branch (the release channel) via `url` + https
  sources — anonymous-clone friendly; the `github` *plugin-source* type requires SSH keys.
  Note `ref: main` follows the branch; it is not a fixed commit, so what installs is
  whatever `main` holds at clone time.
- The praxen repo still hosts a **separate, praxen-only** marketplace under the same
  registered name, serving installs added from `open-agent-ai-security/praxen` before this
  catalog existed. It follows praxen's own conventions (relative `./` source, version
  fields) — it is *not* a copy of this file, and copying this file there would break
  praxen's CI and the legacy install path. A one-way drift check
  (`marketplace-sync.yml` + `check_marketplace_mirror.py`, currently on praxen's `dev` and
  reaching `main` with the 1.2 release) compares praxen's entry against this index; there
  is no check in this repo, and nothing checks the raffkin entry.
- `main` is protected, and the protection is enforced: every change lands by PR with one
  approving review, **review from a code owner is required** (`.github/CODEOWNERS` covers
  the manifest, `scripts/` and `.github/` — the three places that decide what installs and
  how it is checked), stale approvals are dismissed on new pushes, the `catalog` check must
  pass on a branch that is up to date with `main`, and force-pushes and deletion are blocked.
  CI validates the manifest with **main's** copy of `scripts/validate_catalog.py`, so a PR
  can't relax the rules and repoint a source in one change. A PR that edits the workflow or
  the validator therefore cannot merge without a code owner reading that diff — which is the
  review to give it.

## License

[Apache-2.0](LICENSE)
