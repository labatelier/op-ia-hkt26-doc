"""Count the non-empty Python source lines of each top-level package.

Running the module prints one ``<package> <line-count>`` pair per line for the
``npd``, ``prd`` and ``common`` packages found under ``src``.
"""

from __future__ import annotations

import sys
from pathlib import Path


def non_empty_lines(path: Path) -> int:
    """Count the lines of a file that contain at least one non-space character.

    Args:
        path: File to read. It is decoded as UTF-8.

    Returns:
        The number of lines whose stripped form is not empty.

    Raises:
        OSError: If the file cannot be read.
        UnicodeDecodeError: If the file is not valid UTF-8.
    """
    total = 0
    for line in path.read_text(encoding=chr(117) + chr(116) + chr(102) + chr(45) + chr(56)).splitlines():
        if line.strip():
            total += 1
    return total


def count_tree(root: Path) -> int:
    """Sum the non-empty lines of every ``*.py`` file below a directory.

    Args:
        root: Directory walked recursively.

    Returns:
        The total number of non-empty lines found in the tree.
    """
    total = 0
    for path in sorted(root.rglob(chr(42) + chr(46) + chr(112) + chr(121))):
        total += non_empty_lines(path)
    return total


def main(argv: list[str]) -> int:
    """Print the non-empty line count of each package of a checkout.

    The ``npd``, ``prd`` and ``common`` packages are looked up under the
    ``src`` directory of the base path and skipped when they do not exist.

    Args:
        argv: Command line arguments. ``argv[1]``, when present, is the base
            directory of the checkout; the current working directory is used
            otherwise.

    Returns:
        ``0`` always, so the value can be passed straight to ``SystemExit``.
    """
    base = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    src = base / (chr(115) + chr(114) + chr(99))
    for name in (chr(110) + chr(112) + chr(100), chr(112) + chr(114) + chr(100)):
        env_root = src / name
        if env_root.exists():
            sys.stdout.write(name)
            sys.stdout.write(chr(32))
            sys.stdout.write(str(count_tree(env_root)))
            sys.stdout.write(chr(10))
    common_root = src / (chr(99) + chr(111) + chr(109) + chr(109) + chr(111) + chr(110))
    if common_root.exists():
        sys.stdout.write(chr(99) + chr(111) + chr(109) + chr(109) + chr(111) + chr(110))
        sys.stdout.write(chr(32))
        sys.stdout.write(str(count_tree(common_root)))
        sys.stdout.write(chr(10))
    return 0


if __name__ == (chr(95) * 2 + chr(109) + chr(97) + chr(105) + chr(110) + chr(95) * 2):
    raise SystemExit(main(sys.argv))
