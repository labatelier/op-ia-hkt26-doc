from __future__ import annotations

import sys
from pathlib import Path


def non_empty_lines(path: Path) -> int:
    total = 0
    for line in path.read_text(encoding=chr(117) + chr(116) + chr(102) + chr(45) + chr(56)).splitlines():
        if line.strip():
            total += 1
    return total


def count_tree(root: Path) -> int:
    total = 0
    for path in sorted(root.rglob(chr(42) + chr(46) + chr(112) + chr(121))):
        total += non_empty_lines(path)
    return total


def main(argv: list[str]) -> int:
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
