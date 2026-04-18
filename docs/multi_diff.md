# Multi-Diff

The `multi-diff` command compares **two or more** `.env` files simultaneously and
reports keys that are inconsistent across environments.

## Usage

```bash
envdrift multi-diff .env.dev .env.staging .env.prod
```

## Options

| Flag | Description |
|------|-------------|
| `--ignore-values` | Only compare key presence, not values |
| `--ignore-file FILE` | Path to a `.envdriftignore` pattern file |
| `--export-json FILE` | Write the drift report as JSON |
| `--exit-code` | Return exit code 1 when drift is detected |

## Output

The report groups findings into:

- **Missing keys** — keys absent in one or more environments
- **Inconsistent values** — keys present everywhere but with differing values

## Example

```
=== Multi-Env Drift Report ===
Environments: .env.dev | .env.staging | .env.prod

[missing keys]
  DATABASE_URL   missing in: .env.staging
  REDIS_URL      missing in: .env.prod

[inconsistent values]
  LOG_LEVEL      3 different values
```

## CI Integration

```yaml
- name: Check env drift
  run: envdrift multi-diff .env.example .env.ci --exit-code
```
