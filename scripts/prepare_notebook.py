"""Prepare the portfolio notebook for safe public distribution."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = (
    PROJECT_ROOT / "notebooks" / "mortgage_underwriting_multi_agent_system.ipynb"
)

DROP_MARKERS = (
    "Marking Scheme",
    "Important Points To Note",
    "Part 1: Core Agent Implementation (10 marks)",
    "Part 2: Workflow & Orchestration (7 marks)",
    "Part 3: Testing & Analysis (1 mark)",
    "Part 4: Summary and Future Scope (2 marks)",
    "Congratulations!",
)

PORTFOLIO_HEADER = """# Mortgage Underwriting Multi-Agent System

An explainable mortgage-underwriting workflow built with LangGraph, LangChain,
retrieval-augmented generation, deterministic financial tools, PII
sanitization, and human-in-the-loop review.

> **Portfolio demonstration only.** All applicant data and underwriting
> policies are synthetic. Do not use this notebook for real lending decisions
> or submit real personally identifiable information.
"""

ENVIRONMENT_CELL = """# Configure an OpenAI-compatible model provider
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = PROJECT_ROOT / ".cache"
CACHE_DIR.mkdir(exist_ok=True)

load_dotenv(PROJECT_ROOT / ".env")

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError(
        "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
    )

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL") or None
print("Model provider configuration loaded from environment variables.")
"""


def source_text(cell: dict[str, Any]) -> str:
    return "".join(cell.get("source", []))


def set_source(cell: dict[str, Any], text: str) -> None:
    cell["source"] = text.splitlines(keepends=True)


def should_drop(cell: dict[str, Any]) -> bool:
    text = source_text(cell)
    if cell.get("cell_type") == "markdown" and "data:image/" in text:
        return True
    if (
        cell.get("cell_type") == "markdown"
        and text.startswith("# Mortgage Underwriting Multi-Agent System")
    ):
        return True
    return cell.get("cell_type") == "markdown" and any(
        marker in text for marker in DROP_MARKERS
    )


def transform_source(text: str) -> str:
    replacements = {
        "Learn to build an intelligent loan analysis system using LangGraph & AI agents": (
            "Portfolio demonstration of explainable multi-agent orchestration"
        ),
        "GreatLearning API": "OpenAI-compatible API",
        "GreatLearning's OpenAI proxy service": "an OpenAI-compatible model provider",
        'base_url="https://aibe.mygreatlearning.com/openai/v1"': (
            "base_url=OPENAI_BASE_URL"
        ),
        "from langchain_community.document_loaders import PyPDFLoader": (
            "from langchain_community.document_loaders import TextLoader"
        ),
        'loader = PyPDFLoader("underwriting_policies.pdf")': (
            "loader = TextLoader(\n"
            '        DATA_DIR / "synthetic_underwriting_policies.md",\n'
            '        encoding="utf-8",\n'
            "    )"
        ),
        'persist_directory="policy_vectorstore"': (
            'persist_directory=str(CACHE_DIR / "policy_vectorstore")'
        ),
        'with open("mortgage_test_cases.json", "r") as f:': (
            'with (DATA_DIR / "synthetic_mortgage_test_cases.json").open('
            'encoding="utf-8") as f:'
        ),
        "mortgage_test_cases.json": "synthetic_mortgage_test_cases.json",
        "LEARNER NOTE": "DEMO NOTE",
        "## 9️⃣ **Summary and Future Scope (2 marks)**": (
            "## 9️⃣ **Summary and Future Scope**"
        ),
        "# 🧠 Initialize Language Model with OpenAI-compatible API": (
            "# 🧠 Initialize the language model"
        ),
        "print(\"✅ LLM initialized with OpenAI-compatible API!\")": (
            'print("✅ LLM initialized!")'
        ),
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = text.replace(
        'loader = TextLoader(\\n'
        '        DATA_DIR / "synthetic_underwriting_policies.md",\\n'
        '        encoding="utf-8",\\n'
        "    )",
        "loader = TextLoader(\n"
        '        DATA_DIR / "synthetic_underwriting_policies.md",\n'
        '        encoding="utf-8",\n'
        "    )",
    )
    text = text.replace(
        "Create vector store with underwriting policies (loaded from PDF).",
        "Create a vector store from the synthetic underwriting policies.",
    )
    text = text.replace(
        "# Load policies from PDF instead of hardcoded text",
        "# Load the synthetic policy document",
    )
    return text


def main() -> None:
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    cells: list[dict[str, Any]] = []

    cells.append(
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": PORTFOLIO_HEADER.splitlines(keepends=True),
        }
    )

    for cell in notebook.get("cells", []):
        if should_drop(cell):
            continue

        text = source_text(cell)
        if cell.get("cell_type") == "code" and 'file_name = "config.json"' in text:
            set_source(cell, ENVIRONMENT_CELL)
        elif cell.get("cell_type") == "code" and "%pip install" in text:
            set_source(cell, "%pip install -r ../requirements.txt\n")
        else:
            set_source(cell, transform_source(text))

        if cell.get("cell_type") == "code":
            cell["outputs"] = []
            cell["execution_count"] = None

        cell_metadata = cell.setdefault("metadata", {})
        cell_metadata.pop("widgets", None)
        cells.append(cell)

    notebook["cells"] = cells
    notebook_metadata = notebook.setdefault("metadata", {})
    notebook_metadata.pop("widgets", None)
    NOTEBOOK_PATH.write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )

    print(f"Prepared {NOTEBOOK_PATH}")
    print(f"Cells retained: {len(cells)}")


if __name__ == "__main__":
    main()
