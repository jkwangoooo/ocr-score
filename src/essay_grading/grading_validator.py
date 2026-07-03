from __future__ import annotations

from typing import Any

from .grading_models import GradingResult


class GradingValidationError(ValueError):
    pass


def band_for(score: int, bands: list[dict[str, Any]]) -> str:
    for band in bands:
        if int(band["min"]) <= score <= int(band["max"]):
            return str(band["id"])
    raise GradingValidationError(f"No band defined for score: {score}")


def validate_dimension_bounds(dimension_scores: dict[str, int], rubric: dict[str, Any]) -> dict[str, int]:
    dims = {d["id"]: int(d["max_score"]) for d in rubric["dimensions"]}
    normalized: dict[str, int] = {}
    for dim_id, max_score in dims.items():
        value = int(dimension_scores.get(dim_id, 0))
        if value < 0 or value > max_score:
            raise GradingValidationError(f"Dimension {dim_id} out of bounds: {value} not in [0,{max_score}]")
        normalized[dim_id] = value
    extra = set(dimension_scores) - set(dims)
    if extra:
        raise GradingValidationError(f"Unknown dimensions: {sorted(extra)}")
    return normalized


def normalize_result(raw: dict[str, Any], rubric: dict[str, Any]) -> GradingResult:
    rubric_id = str(rubric["rubric_id"])
    invalid_essay = bool(raw.get("invalid_essay", False))
    invalid_reason = str(raw.get("invalid_reason", "") or "")
    dimension_scores = validate_dimension_bounds(raw.get("dimension_scores") or {}, rubric)
    score = int(raw.get("score", sum(dimension_scores.values())))
    expected_sum = sum(dimension_scores.values())
    if score != expected_sum:
        score = expected_sum
    full_score = int(rubric["full_score"])
    if score < 0 or score > full_score:
        raise GradingValidationError(f"Score out of bounds: {score} not in [0,{full_score}]")
    if invalid_essay:
        score = 0
        invalid_band = next((b["id"] for b in rubric["bands"] if int(b["min"]) == 0 and int(b["max"]) == 0), "0")
        band = str(invalid_band)
        dimension_scores = {d["id"]: 0 for d in rubric["dimensions"]}
    else:
        band = band_for(score, rubric["bands"])
    result = GradingResult(
        rubric_id=rubric_id,
        invalid_essay=invalid_essay,
        invalid_reason=invalid_reason,
        score=score,
        band=band,
        dimension_scores=dimension_scores,
        reasons=[str(x) for x in (raw.get("reasons") or [])],
        comment=str(raw.get("comment", "") or ""),
        review_required=bool(raw.get("review_required", False)),
        review_reasons=[str(x) for x in (raw.get("review_reasons") or [])],
        ocr_notes=str(raw.get("ocr_notes", "") or ""),
    )
    return result
