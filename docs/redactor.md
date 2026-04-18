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
from envdrift.redactor import load_redact_patterns, redact_env, is_redacted

patterns = load_redact_patterns(".envdriftredact")
clean_env = redact_env(raw_env, patterns=patterns)

# Check if a specific key would be redacted
if is_redacted("MY_API_KEY", patterns):
    print("This key will be masked")
```

`redact_env` returns a copy of the dict — original values are never mutated.

### `is_redacted(key, patterns)`

Returns `True` if the given key matches any of the supplied patterns. Useful for
pre-flight checks or building custom reporting logic without running a full
`redact_env` pass.

```python
from envdrift.redactor import is_redacted, DEFAULT_PATTERNS

is_redacted("DB_PASSWORD", DEFAULT_PATTERNS)  # True
is_redacted("APP_ENV", DEFAULT_PATTERNS)      # False
```

## Behaviour

- Matching is **case-insensitive** and uses `re.fullmatch`.
- Non-matching keys pass through unchanged.
- Redacted placeholder value is `[REDACTED]`.
