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
claude plugin install socxen@open-agent-ai-security
```

| Plugin | What it does | Repo |
|---|---|---|
| **praxen** | Agent behavior verifier — compares an AI agent's declared policy (Worker Remit) against the available evidence and reports where observed behavior diverges from declared intent, scored against the RAISE framework and OWASP LLM/Agentic guidance. | [open-agent-ai-security/praxen](https://github.com/open-agent-ai-security/praxen) |
| **socxen** | Agentic SOC analyst — triages Exabeam New-Scale alerts and cases end to end via the Exabeam MCP, with governance gates and guardrails. | [open-agent-ai-security/socxen](https://github.com/open-agent-ai-security/socxen) |

The in-session equivalents (`/plugin marketplace add …`, `/plugin install …`) do the same
thing; run `/reload-plugins` (or restart the session) after an in-session install.

## Migrating from an older install path

Both plugins were previously distributed from marketplaces hosted in their own repos.
The marketplace name (`open-agent-ai-security`) and the plugin keys are unchanged, so
migration is one command and nothing about your installed plugins is lost.

**Praxen users** — if you added the marketplace from `open-agent-ai-security/praxen`,
just add this one; the same-named marketplace is re-pointed in place and your installed
praxen keeps working:

```bash
claude plugin marketplace add open-agent-ai-security/plugins
```

Do **not** run `claude plugin marketplace remove` first — removing a marketplace
uninstalls the plugins that came from it, and it isn't necessary. Migrating is optional
for praxen (the legacy repo still publishes a praxen-only marketplace) but **required to
install socxen**, which only this catalog publishes.

**socxen users** — if you installed the plugin as `socxen@socxen`, remove that marketplace
first. It has a *different* name from this one, so simply adding this catalog would leave you
with two enabled copies of socxen (the current release and the retired one), both registering
the `soc-investigate` skill:

```bash
claude plugin marketplace remove socxen                        # also uninstalls socxen@socxen
claude plugin marketplace add open-agent-ai-security/plugins   # re-points in place if already present
claude plugin install socxen@open-agent-ai-security
```

A separate `claude plugin uninstall socxen@socxen` isn't needed — removing the marketplace
uninstalls its plugins, which is the point here.

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
  is no check in this repo, and nothing checks the socxen entry.
- `main` is protected: changes land by PR with a required approval, and CI validates the
  manifest with **main's** copy of `scripts/validate_catalog.py`, so a PR can't relax the
  rules and repoint a source in one change.
  **Known gap:** on `pull_request` the workflow file itself comes from the PR, so a PR can
  still edit the gate step. `.github/CODEOWNERS` exists to close this, but it only
  auto-requests reviewers until **"Require review from Code Owners"** is enabled on the
  branch protection rule — until then, treat a green `catalog` check as evidence about the
  manifest, not proof the gate ran as written, and review diffs to `/.github/` and
  `/scripts/` accordingly.

## License

[Apache-2.0](LICENSE)
