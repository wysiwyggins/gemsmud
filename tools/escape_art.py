#!/usr/bin/env python3
"""
Replace | and \\ in text files with visually similar Unicode characters
that won't be consumed by Evennia's color parser.

  |  → │ (U+2502 box-drawing vertical)
  \\  → ╲ (U+2572 box-drawing diagonal)

Usage:
  python escape_art.py <file> [file ...]

Files are modified in place. Originals are saved as <file>.bak.
"""

import sys
import shutil
from pathlib import Path


def escape_art(text):
    return text.replace("\\", "\u2572").replace("|", "\u2502")


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        sys.exit(1)

    for path in sys.argv[1:]:
        p = Path(path)
        if not p.is_file():
            print(f"skip: {path} (not a file)")
            continue

        original = p.read_text(encoding="utf-8")
        converted = escape_art(original)

        if original == converted:
            print(f"skip: {path} (nothing to replace)")
            continue

        shutil.copy2(p, p.with_suffix(p.suffix + ".bak"))
        p.write_text(converted, encoding="utf-8")

        pipes = converted.count("\u2502") - original.count("\u2502")
        slashes = converted.count("\u2572") - original.count("\u2572")
        print(f"done: {path}  ({pipes} pipes, {slashes} backslashes)")


if __name__ == "__main__":
    main()
