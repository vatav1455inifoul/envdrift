"""Allows running envdrift as a module: python -m envdrift."""

import sys

from envdrift.cli import main

if __name__ == "__main__":
    sys.exit(main())
