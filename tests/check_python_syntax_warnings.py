#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import pathlib
import warnings

ROOT = pathlib.Path(__file__).resolve().parents[1]


def python_sources():
    paths = set(ROOT.rglob("*.py"))
    paths.update(ROOT.rglob("wscript"))
    waf = ROOT / "waf"
    if waf.is_file():
        paths.add(waf)
    for path in sorted(paths):
        if ".git" not in path.parts and "build" not in path.parts:
            yield path


def main() -> int:
    failures = []
    for path in python_sources():
        source = path.read_text(encoding="utf-8")
        try:
            with warnings.catch_warnings():
                # Python 3.12+ reports invalid escape sequences as
                # SyntaxWarning; older supported interpreters used
                # DeprecationWarning for the same parser issue.
                warnings.simplefilter("error", SyntaxWarning)
                warnings.simplefilter("error", DeprecationWarning)
                compile(source, str(path), "exec")
        except (SyntaxWarning, DeprecationWarning) as exc:
            failures.append(f"{path.relative_to(ROOT)}: {exc}")

    if failures:
        print("Python syntax warnings detected:")
        for failure in failures:
            print(f"  {failure}")
        return 1

    print("Python syntax-warning scan: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
