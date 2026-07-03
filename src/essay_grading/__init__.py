"""Cross-platform essay grading package.

This package contains only grading-domain logic:
- rubric loading
- request/result models
- result validation
- prompt building

It intentionally does NOT include:
- OCR
- web/UI code
- Zhixue integration
- platform-specific filesystem assumptions
"""

from .grading_models import GradingRequest, GradingResult, ReviewDecision
from .grading_service import grade_essay
from .rubric_loader import load_rubric, list_rubrics

__all__ = [
    "GradingRequest",
    "GradingResult",
    "ReviewDecision",
    "grade_essay",
    "load_rubric",
    "list_rubrics",
]
