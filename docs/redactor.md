# Redactor

The `redactor` module automatically masks sensitive values in `.env` files before they appear in reports or exports.

## Default Sensitive Patterns

The following key patterns are redacted by default (case-insensitive):

- `.*SECRET.*`
- `.*PASSWORD.*` / `.*PASSWD.*`
- `.*TOKEN.*`
- `.*API_KEY.*`
- `.*PRIVATE.*`
- `.*CREDENTIAL.*`

## Custom Patterns File

You can supply a file of regex patterns (one per line, `#` for comments):

```
# .envdriftredact
MY_INTERNAL_KEY
CUSTOM_.*_SECRET
```

Pass it via the CLI with `--redact-patterns .envdriftredact`.

## Python API

```python
from envdrift.redactor import load_redact_patterns, redact_env

patterns = load_redact_patterns(".envdriftredact")
clean_env = redact_env(raw_env, patterns=patterns)
```

`redact_env` returns a copy of the dict — original values are never mutated.

## Behaviour

- Matching is **case-insensitive** and uses `re.fullmatch`.
- Non-matching keys pass through unchanged.
- Redacted placeholder value is `[REDACTED]`.
