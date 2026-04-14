# envdrift

> Detect and report configuration drift between `.env` files across environments.

---

## Installation

```bash
pip install envdrift
```

Or with pipx for isolated CLI usage:

```bash
pipx install envdrift
```

---

## Usage

Compare two `.env` files to surface missing keys, extra keys, and value differences:

```bash
envdrift compare .env.development .env.production
```

**Example output:**

```
[MISSING]  DATABASE_URL        found in development, missing in production
[EXTRA]    DEBUG_MODE          found in production, not in development
[DRIFT]    LOG_LEVEL           development=debug  |  production=warning
```

Check multiple environments at once:

```bash
envdrift compare .env.development .env.staging .env.production
```

Export a drift report as JSON:

```bash
envdrift compare .env.development .env.production --format json --output report.json
```

List all keys shared across all provided env files:

```bash
envdrift audit .env.development .env.staging .env.production
```

---

## Options

| Flag | Description |
|------|-------------|
| `--format` | Output format: `text` (default) or `json` |
| `--output` | Write results to a file instead of stdout |
| `--ignore` | Comma-separated list of keys to ignore |
| `--strict` | Exit with non-zero status if any drift is found |

---

## License

MIT © [envdrift contributors](https://github.com/your-org/envdrift)