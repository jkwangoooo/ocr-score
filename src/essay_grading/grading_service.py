from __future__ import annotations

from typing import Protocol

from .grading_models import GradingRequest, GradingResult
from .grading_validator import normalize_result
from .prompt_builder import build_system_prompt, build_user_prompt
from .rubric_loader import load_rubric


class ModelClient(Protocol):
    def grade(self, system_prompt: str, user_prompt: str) -> dict:
        ...


def grade_essay(request: GradingRequest, client: ModelClient) -> GradingResult:
    rubric = load_rubric(request.rubric_id)
    system_prompt = build_system_prompt(rubric)
    user_prompt = build_user_prompt(request.essay_text, request.context)
    raw = client.grade(system_prompt, user_prompt)
    return normalize_result(raw, rubric)
