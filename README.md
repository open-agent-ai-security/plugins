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

**socxen users** — if you installed the plugin as `socxen@socxen`, that marketplace was
retired at the source, so this one does need an uninstall:

```bash
claude plugin uninstall socxen@socxen
claude plugin marketplace remove socxen
claude plugin marketplace add open-agent-ai-security/plugins   # re-points in place if already present
claude plugin install socxen@open-agent-ai-security
```

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
- Entries pin each plugin repo's `main` branch (the release channel) via `url` + https
  sources — anonymous-clone friendly; the `github` source type requires SSH keys.
- The praxen repo still hosts a **separate, praxen-only** marketplace under the same
  registered name, serving installs added from `open-agent-ai-security/praxen` before this
  catalog existed. It follows praxen's own conventions (relative `./` source, version
  fields) — it is *not* a copy of this file, and copying this file there would break
  praxen's CI and the legacy install path. praxen's `marketplace-sync.yml` compares its
  entry against this index one-way; there is no sync check in this repo.
- `main` is protected: changes land by PR with a required approval, CI sanity-checks the
  manifest (`scripts/validate_catalog.py`, run from `main` so a PR can't weaken its own
  gate), and `.github/CODEOWNERS` requires an owner's review on the manifest, the
  validator, and workflows.

## License

[Apache-2.0](LICENSE)
