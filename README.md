# hermes-plugins

SkyMin plugins for [Hermes Agent](https://github.com/NousResearch/hermes-agent). Always-on speech/output plugins and a terminal rewrite hook.

This is the source of truth. Copy a plugin folder into `$HERMES_HOME/plugins/` (default: `%LOCALAPPDATA%\hermes\plugins\` on Windows, or `~/.hermes/plugins/` elsewhere). Named profiles use `$HERMES_HOME/profiles/<name>/plugins/`.

The desktop SuperGrok usage chip lives in a separate repo: [hermes-grok-usage](https://github.com/SYacuCLoud/hermes-grok-usage).

## Plugins

| Folder | Version | What it does | Slash command |
| --- | --- | --- | --- |
| `caveman` | 0.1.0 | Injects terse “caveman” speech rules on every LLM call | `/caveman lite` / `full` / `ultra` / `off` |
| `i-have-adhd` | 0.1.0 | Shapes replies for ADHD: next action first, numbered steps, no fluff | `/i-have-adhd on` / `off` |
| `ponytail` | 4.9.0 | Lazy-senior-dev mode plus review/audit/debt/gain skills | `/ponytail`, `/ponytail-review`, `/ponytail-audit`, `/ponytail-debt`, `/ponytail-gain`, `/ponytail-help` |
| `rtk-rewrite` | 0.2.0 | Rewrites `terminal` commands through RTK before Hermes runs them. Fails open. | (hook only) |

`caveman` extra levels: `wenyan-lite`, `wenyan-full`, `wenyan-ultra`. Default is `lite`.

## Install

1. Copy the plugin folder (keep the folder name) into `$HERMES_HOME/plugins/`.
2. Enable it:

```bash
hermes plugins enable caveman
hermes plugins enable i-have-adhd
hermes plugins enable ponytail
hermes plugins enable rtk-rewrite
```

3. Restart Hermes (or the gateway). Session restart is required for hook changes.

Do not `git init` inside `$HERMES_HOME/plugins/`. Clone this repo somewhere else and copy folders in.

## Requirements

- Hermes Agent with the Python plugin system (`plugin.yaml` + `plugins.enabled`).
- `rtk-rewrite` only: `rtk` on PATH. If `rtk` is missing, the hook does not register. Default backend allow-list is `local`. Override with `RTK_HERMES_BACKENDS` (`local`, comma-separated names, or `all`). Already-prefixed commands (`rtk ` or `: RTK && `) are left alone.

## License

Personal / public source dump. Author: SkyMin (`syacucloud`).
