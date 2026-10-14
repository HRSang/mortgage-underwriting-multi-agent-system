"""Fail when public-repository safety checks detect common publishing risks."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".env", ".ipynb", ".json", ".md", ".py", ".txt", ".yml", ".yaml"}
IGNORED_PARTS = {".git", ".venv", "__pycache__", ".cache"}
SECRET_PATTERNS = {
    "OpenAI-style key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "Tavily key": re.compile(r"\btvly-[A-Za-z0-9_-]{20,}\b"),
    "Great Learning key": re.compile(r"\bgl-[A-Za-z0-9_+/=-]{20,}\b"),
}


def repository_files() -> list[Path]:
    return [
        path
        for path in PROJECT_ROOT.rglob("*")
        if path.is_file() and not any(part in IGNORED_PARTS for part in path.parts)
    ]


def main() -> int:
    errors: list[str] = []

    if (PROJECT_ROOT / ".env").exists():
        errors.append(".env must not be committed")
    if (PROJECT_ROOT / "config.json").exists():
        errors.append("legacy config.json must not be committed")

    for path in repository_files():
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name != ".env.example":
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        relative_path = path.relative_to(PROJECT_ROOT)
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{relative_path}: possible {label}")

        if path.suffix.lower() == ".ipynb":
            notebook = json.loads(text)
            output_count = sum(
                len(cell.get("outputs", [])) for cell in notebook.get("cells", [])
            )
            if output_count:
                errors.append(f"{relative_path}: contains {output_count} outputs")

    if errors:
        print("Public-repository safety check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Public-repository safety check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

