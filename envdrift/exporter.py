"""Export drift results to structured formats (JSON, CSV)."""

import csv
import json
import io
from typing import Union

from envdrift.comparator import DriftResult
from envdrift.differ import MultiDiffResult


def _drift_to_dict(result: DriftResult, env_a: str = "env_a", env_b: str = "env_b") -> dict:
    return {
        "env_a": env_a,
        "env_b": env_b,
        "has_drift": result.has_drift,
        "missing_keys": list(result.missing_keys),
        "extra_keys": list(result.extra_keys),
        "changed_values": {
            k: {"env_a": v[0], "env_b": v[1]}
            for k, v in result.changed_values.items()
        },
    }


def export_json(
    result: Union[DriftResult, MultiDiffResult],
    env_names: list = None,
    indent: int = 2,
) -> str:
    """Serialize a drift result to a JSON string."""
    if isinstance(result, MultiDiffResult):
        data = {
            "envs": env_names or [],
            "has_drift": result.has_drift,
            "inconsistent_keys": {
                k: {env: v for env, v in envmap.items()}
                for k, envmap in result.inconsistent_keys.items()
            },
            "missing_in_some": {
                k: list(envs) for k, envs in result.missing_in_some.items()
            },
        }
    else:
        a_name = env_names[0] if env_names and len(env_names) > 0 else "env_a"
        b_name = env_names[1] if env_names and len(env_names) > 1 else "env_b"
        data = _drift_to_dict(result, a_name, b_name)
    return json.dumps(data, indent=indent)


def export_csv(result: DriftResult, env_a: str = "env_a", env_b: str = "env_b") -> str:
    """Serialize a pairwise DriftResult to CSV rows.

    Columns: key, issue, env_a_value, env_b_value
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["key", "issue", env_a + "_value", env_b + "_value"])

    for key in sorted(result.missing_keys):
        writer.writerow([key, "missing_in_" + env_b, "", ""])

    for key in sorted(result.extra_keys):
        writer.writerow([key, "missing_in_" + env_a, "", ""])

    for key, (val_a, val_b) in sorted(result.changed_values.items()):
        writer.writerow([key, "value_changed", val_a, val_b])

    return output.getvalue()


def export_json_file(
    result: Union[DriftResult, MultiDiffResult],
    path: str,
    env_names: list = None,
    indent: int = 2,
) -> None:
    """Write a drift result as JSON to a file at the given path."""
    content = export_json(result, env_names=env_names, indent=indent)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
