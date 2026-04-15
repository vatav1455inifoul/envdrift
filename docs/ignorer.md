# .envdriftignore Support

envdrift supports a `.envdriftignore` file to exclude specific keys from drift
detection. This is useful for keys that are intentionally different between
environments (e.g. secrets, machine-specific values).

## File Format

Create a `.envdriftignore` file in your project root:

```
# Comments are supported
SECRET_KEY
DATABASE_URL

# Wildcards (*) are supported
AWS_*
*_TOKEN
```

- Blank lines and lines starting with `#` are ignored.
- `*` acts as a wildcard matching any sequence of characters.
- Matching is **case-insensitive**.

## Usage in Code

```python
from envdrift.ignorer import load_ignore_patterns, filter_keys
from envdrift.parser import parse_env_file

patterns = load_ignore_patterns()  # reads .envdriftignore

env_prod = parse_env_file(".env.production")
env_staging = parse_env_file(".env.staging")

# Strip ignored keys before comparison
env_prod = filter_keys(env_prod, patterns)
env_staging = filter_keys(env_staging, patterns)
```

## API Reference

### `load_ignore_patterns(path=None) -> list[str]`

Load patterns from an ignore file. Defaults to `.envdriftignore` in the
current directory. Returns `[]` if the file does not exist.

### `should_ignore(key, patterns) -> bool`

Return `True` if `key` matches any pattern in the list.

### `filter_keys(env, patterns) -> dict`

Return a filtered copy of `env` with all ignored keys removed.
