#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import ast
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
REMOVED_MODULES = {"imp"}


def python_sources():
    paths = set(ROOT.rglob("*.py"))
    paths.update(ROOT.rglob("wscript"))
    waf = ROOT / "waf"
    if waf.is_file():
        paths.add(waf)
    for path in sorted(paths):
        if ".git" not in path.parts and "build" not in path.parts:
            yield path


def removed_imports(path: pathlib.Path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.partition(".")[0]
                if root in REMOVED_MODULES:
                    yield node.lineno, root
        elif isinstance(node, ast.ImportFrom) and node.module:
            root = node.module.partition(".")[0]
            if root in REMOVED_MODULES:
                yield node.lineno, root


def main() -> int:
    failures = []
    for path in python_sources():
        for lineno, module in removed_imports(path):
            failures.append(
                f"{path.relative_to(ROOT)}:{lineno}: imports removed stdlib module {module!r}"
            )

    if failures:
        print("Removed Python standard-library imports detected:")
        for failure in failures:
            print(f"  {failure}")
        return 1

    print("Removed Python stdlib import scan: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
