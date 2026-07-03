from __future__ import annotations

from typing import Any


def build_system_prompt(rubric: dict[str, Any]) -> str:
    task = rubric["prompt_context"]["task"]
    topic = rubric["prompt_context"]["core_topic"]
    lines = [
        "你是一名严谨但务实的英语作文阅卷老师。",
        f"作文任务：{task}",
        f"核心主题：{topic}",
        f"满分：{rubric['full_score']} 分。",
        "必须先判断是否为无效作文；若疑似抄写材料、套作或完全不贴题，直接给 0 分。",
        "只输出合法 JSON。",
        "评分维度如下：",
    ]
    for dim in rubric["dimensions"]:
        lines.append(f"- {dim['id']} / {dim['name']}：满分 {dim['max_score']} 分，{dim['description']}")
    lines.append("输出字段必须包含：invalid_essay, invalid_reason, score, band, dimension_scores, reasons, comment, review_required, review_reasons, ocr_notes。")
    return "\n".join(lines)


def build_user_prompt(essay_text: str, context: dict[str, Any] | None = None) -> str:
    extra = []
    context = context or {}
    if context.get("text_quality"):
        extra.append(f"text_quality={context['text_quality']}")
    if context.get("source"):
        extra.append(f"source={context['source']}")
    context_block = f"\n上下文：{', '.join(extra)}\n" if extra else ""
    return f"请根据评分标准批改以下作文。{context_block}\n作文正文：\n```text\n{essay_text}\n```\n只输出 JSON。"
