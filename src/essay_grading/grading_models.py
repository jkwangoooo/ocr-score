from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class GradingRequest:
    rubric_id: str
    essay_text: str
    context: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ReviewDecision:
    required: bool = False
    reasons: list[str] = field(default_factory=list)


@dataclass(slots=True)
class GradingResult:
    rubric_id: str
    invalid_essay: bool
    invalid_reason: str
    score: int
    band: str
    dimension_scores: dict[str, int]
    reasons: list[str]
    comment: str
    review_required: bool
    review_reasons: list[str]
    ocr_notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "rubric_id": self.rubric_id,
            "invalid_essay": self.invalid_essay,
            "invalid_reason": self.invalid_reason,
            "score": self.score,
            "band": self.band,
            "dimension_scores": dict(self.dimension_scores),
            "reasons": list(self.reasons),
            "comment": self.comment,
            "review_required": self.review_required,
            "review_reasons": list(self.review_reasons),
            "ocr_notes": self.ocr_notes,
        }
