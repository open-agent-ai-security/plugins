# Open Agent AI Security — Plugin Marketplace

The single [Claude Code](https://claude.com/claude-code) plugin marketplace for the
[Open Agent AI Security](https://open-agent-ai-security.github.io/) community. Add it once:

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
migration is quick and nothing about your installed plugins' configuration is lost.

**Praxen users** — if you added the marketplace from `open-agent-ai-security/praxen`:

```bash
claude plugin marketplace remove open-agent-ai-security   # this also uninstalls the plugin
claude plugin marketplace add open-agent-ai-security/plugins
claude plugin install praxen@open-agent-ai-security
```

Removing a marketplace uninstalls the plugins that came from it, so the reinstall line is
required — your plugin key and settings are unchanged, and the plugin re-enables as
before. The old path remains a maintained mirror for now, so migration is recommended,
not required.

**socxen users** — if you installed the plugin as `socxen@socxen`:

```bash
claude plugin uninstall socxen@socxen
claude plugin marketplace remove socxen
claude plugin marketplace add open-agent-ai-security/plugins   # skip only if already added from …/plugins
claude plugin install socxen@open-agent-ai-security
```

If a marketplace named `open-agent-ai-security` already exists but was added from the old
praxen repo path, follow the praxen migration above first — the add commands conflict on the
shared marketplace name until the old one is removed.

## For maintainers

- Index entries are deliberately minimal — no per-release version metadata. Each plugin
  repo's `plugin.json` is the version authority, so product releases never require a
  change here. Touch this repo only to add a plugin or update a description.
- The praxen repo carries a mirror of this index in its own
  `.claude-plugin/marketplace.json` (legacy install path); a CI check in that repo keeps
  the mirror in sync with this file.

## License

[Apache-2.0](LICENSE)
