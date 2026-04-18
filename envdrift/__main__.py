"""Allows running envdrift as a module: python -m envdrift."""

import sys

from envdrift.cli import main

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        sys.exit(1)
