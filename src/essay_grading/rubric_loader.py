from __future__ import annotations

import json
from importlib.resources import files
from typing import Any


def _rubrics_root():
    return files("essay_grading") / "rubrics"


def list_rubrics() -> list[str]:
    root = _rubrics_root()
    return sorted(p.name for p in root.iterdir() if p.is_file() and p.suffix == ".json")


def load_rubric(rubric_id: str) -> dict[str, Any]:
    filename = rubric_id if rubric_id.endswith(".json") else f"{rubric_id}.json"
    path = _rubrics_root() / filename
    if not path.is_file():
        raise FileNotFoundError(f"Rubric not found: {rubric_id}")
    return json.loads(path.read_text(encoding="utf-8"))
