# Snapshots

The **snapshot** feature lets you capture the state of an `.env` file at a
point in time and later compare a live file against that baseline.

This is useful for:

- Detecting unintended changes between deployments
- Auditing configuration changes in CI pipelines
- Sharing a known-good baseline with teammates

---

## Saving a snapshot

```bash
envdrift snapshot save .env.production \
  --name prod \
  --output snapshots/prod.json \
  --notes "before v2.3 deploy"
```

This parses `.env.production` and writes a JSON snapshot to
`snapshots/prod.json`.

---

## Comparing against a snapshot

```bash
envdrift snapshot diff .env.production snapshots/prod.json
```

Add `--exit-code` to return a non-zero exit status drift is detected
(handy in CI):

```bash
envdrift snapshot diff .env.production snapshots/prod.json --exit-code
```

Pass `--ignore-values` to check only for missing or extra keys, ignoring
value changes:

```bash
envdrift snapshot diff .env.production snapshots/prod.json --ignore-values
```

---

## Inspecting a snapshot

```bash
envdrift snapshot info snapshots/prod.json
```

Sample output:

```
[prod] 12 keys, saved 2024-05-01T10:30:00+00:00 — before v2.3 deploy
  version   : 1
  env_name  : prod
  created_at: 2024-05-01T10:30:00+00:00
  notes     : before v2.3 deploy
  keys (12): APP_ENV, DB_HOST, DB_NAME, DB_PASS, DB_PORT, ...
```

---

## Snapshot file format

Snapshots are plain JSON files and are safe to commit to version control
(as long as they don't contain secrets).

```json
{
  "version": 1,
  "env_name": "prod",
  "created_at": "2024-05-01T10:30:00+00:00",
  "notes": "before v2.3 deploy",
  "values": {
    "APP_ENV": "production",
    "DB_HOST": "db.prod.example.com"
  }
}
```
