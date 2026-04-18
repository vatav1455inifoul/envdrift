# Annotator

The `annotator` module adds inline drift annotations to `.env` files, making it easy to see at a glance which keys are missing, extra, or changed compared to a reference environment.

## Usage

```python
from envdrift.annotator import annotate_env, write_annotated

result = annotate_env(
    env_path="envs/staging.env",
    reference_path="envs/production.env",
    env_name="staging",
    ref_name="production",
)

print(result.render())
write_annotated(result, "envs/staging.annotated.env")
```

## Output format

Each key is rendered as a standard `.env` line. Drifted keys receive an inline comment:

```
DB_HOST=staging-db  # [envdrift] CHANGED (ref='prod-db')
DEBUG=true
NEW_FLAG=1          # [envdrift] EXTRA (not in reference)
SECRET_KEY=         # [envdrift] MISSING
```

## API

### `annotate_env(env_path, reference_path, env_name, ref_name) -> AnnotationResult`

Parses both files, computes drift, and returns an `AnnotationResult` containing `AnnotatedLine` objects.

### `write_annotated(result, output_path)`

Writes the rendered annotated content to `output_path`.

## Data classes

- **`AnnotatedLine`** — holds `key`, `value`, and `annotation` strings. `.render()` produces a single line.
- **`AnnotationResult`** — holds `env_name` and a list of `AnnotatedLine`. `.render()` produces the full file content.
