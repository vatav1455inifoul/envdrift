"""Watch .env files for changes and report drift in real time."""

import time
import os
from typing import Dict, List, Optional, Callable

from envdrift.parser import parse_env_file
from envdrift.comparator import compare_envs
from envdrift.reporter import format_report


def _get_mtimes(paths: List[str]) -> Dict[str, float]:
    """Return a dict of path -> mtime for each file that exists."""
    mtimes = {}
    for path in paths:
        try:
            mtimes[path] = os.path.getmtime(path)
        except FileNotFoundError:
            mtimes[path] = -1.0
    return mtimes


def watch_envs(
    base_path: str,
    compare_path: str,
    interval: float = 2.0,
    ignore_values: bool = False,
    on_change: Optional[Callable[[str], None]] = None,
    max_iterations: Optional[int] = None,
) -> None:
    """Poll base_path and compare_path for changes and print drift reports.

    Args:
        base_path: Path to the base .env file.
        compare_path: Path to the comparison .env file.
        interval: Seconds between polls.
        ignore_values: If True, only check for key presence.
        on_change: Optional callback receiving the formatted report string.
        max_iterations: Stop after this many iterations (useful for testing).
    """
    paths = [base_path, compare_path]
    last_mtimes = _get_mtimes(paths)
    iteration = 0

    print(f"Watching {base_path} and {compare_path} (every {interval}s) ...")

    while True:
        if max_iterations is not None and iteration >= max_iterations:
            break

        time.sleep(interval)
        iteration += 1

        current_mtimes = _get_mtimes(paths)
        changed = any(current_mtimes[p] != last_mtimes[p] for p in paths)

        if changed:
            last_mtimes = current_mtimes
            try:
                base_env = parse_env_file(base_path)
                cmp_env = parse_env_file(compare_path)
            except FileNotFoundError as exc:
                msg = f"[envdrift] File not found: {exc}"
                print(msg)
                if on_change:
                    on_change(msg)
                continue

            result = compare_envs(
                base_env,
                cmp_env,
                env_name_a=base_path,
                env_name_b=compare_path,
                ignore_values=ignore_values,
            )
            report = format_report(result)
            print(report)
            if on_change:
                on_change(report)
