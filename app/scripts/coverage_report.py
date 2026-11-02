"""Statement coverage of app/spk/ while pytest runs, using only the standard library.

White-box testing needs to know which lines the tests execute. This script records every line
of spk/*.py that runs (sys.monitoring, Python 3.12+), so no coverage package is needed.

Usage, from app/:
    python scripts/coverage_report.py                       # whole test suite
    python scripts/coverage_report.py -m whitebox           # white-box tests only
    python scripts/coverage_report.py -m "blackbox or whitebox" --out reports/coverage.md

Any other arguments go to pytest. Lines inside `if __name__ == "__main__":` blocks do not exist
in spk/, so nothing is excluded.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
SPK_DIR = APP_DIR / "spk"
TOOL = sys.monitoring.COVERAGE_ID
executed: dict[str, set[int]] = {}


def _on_line(code, line):
    if code.co_filename.startswith(str(SPK_DIR)):
        executed.setdefault(code.co_filename, set()).add(line)
    return sys.monitoring.DISABLE        # one report per line location is enough


def executable_lines(path: Path) -> set[int]:
    """Line numbers that hold bytecode, from every code object in the module.

    Python 3.14 compiles type annotations into lazy `__annotate__` functions that only run when
    something inspects the annotations; they are not program logic, so they are left out.
    """
    lines, todo = set(), [compile(path.read_text(), str(path), "exec")]
    while todo:
        code = todo.pop()
        if code.co_name == "__annotate__":
            continue
        lines.update(line for _, _, line in code.co_lines() if line)
        todo.extend(c for c in code.co_consts if hasattr(c, "co_lines"))
    return lines


def ranges(numbers: list[int]) -> str:
    out, start = [], None
    for i, n in enumerate(numbers):
        if start is None:
            start = n
        if i + 1 == len(numbers) or numbers[i + 1] != n + 1:
            out.append(str(start) if start == n else f"{start}-{n}")
            start = None
    return ", ".join(out)


def report() -> tuple[str, float]:
    rows, total_lines, total_hit = [], 0, 0
    for path in sorted(SPK_DIR.glob("*.py")):
        lines = executable_lines(path)
        if not lines:
            continue
        hit = executed.get(str(path), set()) & lines
        missing = sorted(lines - hit)
        total_lines += len(lines)
        total_hit += len(hit)
        rows.append(f"| spk/{path.name} | {len(lines)} | {len(hit)} | {100 * len(hit) / len(lines):.1f}% | {ranges(missing)} |")
    pct = 100 * total_hit / total_lines if total_lines else 0.0
    table = "\n".join(["| File | Statements | Run | Coverage | Lines not run |", "|---|---|---|---|---|", *rows,
                       f"| **Total** | {total_lines} | {total_hit} | **{pct:.1f}%** | |"])
    return table, pct


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0], add_help=False)
    parser.add_argument("--out", help="also write the table to this Markdown file")
    args, pytest_args = parser.parse_known_args()

    sys.monitoring.use_tool_id(TOOL, "spk-coverage")
    sys.monitoring.register_callback(TOOL, sys.monitoring.events.LINE, _on_line)
    sys.monitoring.set_events(TOOL, sys.monitoring.events.LINE)
    import pytest                            # imported after monitoring starts, like spk itself

    try:
        code = pytest.main(["-q", "-p", "no:cacheprovider", *(pytest_args or ["tests"])])
    finally:
        sys.monitoring.set_events(TOOL, 0)
        sys.monitoring.free_tool_id(TOOL)
    table, pct = report()
    print(f"\nStatement coverage of spk/ ({' '.join(pytest_args) or 'all tests'}): {pct:.1f}%\n")
    print(table)
    if args.out:
        out = APP_DIR / args.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(f"# Statement coverage of spk/\n\npytest {' '.join(pytest_args)}\n\n{table}\n")
        print(f"\nWritten to {out}")
    return int(code)


if __name__ == "__main__":
    raise SystemExit(main())
