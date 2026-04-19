# File Watcher

The `envdrift` watcher polls two `.env` files at a configurable interval and
prints a drift report whenever either file changes.

## Usage

```bash
# Watch .env vs .env.production, checking every 3 seconds
python -m envdrift watch .env .env.production --interval 3
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--interval` | `2.0` | Seconds between polls |
| `--ignore-values` | off | Report only key presence/absence, not value changes |
| `--quiet` | off | Suppress output when no drift is detected |

## How it works

1. On startup the watcher records the **mtime** (last-modified timestamp) of
   both files.
2. Every `--interval` seconds it re-reads the mtimes.
3. If either mtime changed, both files are re-parsed and compared using the
   standard `compare_envs` logic.
4. The resulting drift report is printed to stdout (same format as
   `envdrift compare`).

## Programmatic API

```python
from envdrift.watcher import watch_envs

watch_envs(
    base_path=".env",
    compare_path=".env.staging",
    interval=1.0,
    ignore_values=False,
    on_change=lambda report: send_slack_alert(report),
)
```

Pass `on_change` to receive the formatted report string on every detected
change — useful for integrating alerts into CI pipelines or chat tools.

## Stopping

The watcher runs until interrupted with `Ctrl-C`.

## Limitations

- Uses **polling**, not inotify/FSEvents, so it works cross-platform but is
  not instant.
- Only supports **two** files at a time. For multi-env watching, run multiple
  watcher processes or open a GitHub issue — PRs welcome!
- If a watched file is **deleted** while the watcher is running, a warning is
  printed and the watcher pauses until the file reappears.
