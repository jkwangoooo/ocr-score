# OCR + 评分标准主链路说明

## 1. 正式主链路

当前正式主链路已明确为：

```text
作文图像
-> OCR
-> 文本清洗
-> 评分标准系统
-> 输出分数 / 分项 / 理由 / 复核标记
```

这条链路中，OCR 和评分标准系统必须是两个独立业务层。

---

## 2. 两层职责分工

### OCR 层负责

- 图像转文本
- 保留原始 OCR 结果
- 轻度清洗噪声
- 输出可读性与异常信号

### 评分层负责

- 判断是否无效作文
- 判断任务是否成立
- 按维度打分
- 应用封顶规则
- 输出复核建议

这意味着：

```text
OCR 只能提供“文本和证据”，
评分层才负责“判断和打分”。
```

---

## 3. 推荐接口契约

### OCR 输出给评分层

```json
{
  "essay_text": "clean_text",
  "context": {
    "text_quality": "normal|noisy|short|broken",
    "quality_flags": ["..."],
    "readability_notes": "..."
  }
}
```

### 评分层输出

```json
{
  "framework_id": "essay_scoring_framework_v1",
  "task_spec_id": "family_rules_school_rules_task_v1",
  "invalid_essay": false,
  "invalid_reason": "",
  "gating": {
    "task_established": true,
    "flags": []
  },
  "score": 0,
  "band": "",
  "dimension_scores": {},
  "caps_applied": [],
  "reasons": [],
  "comment": "",
  "review_required": false,
  "review_reasons": [],
  "readability_notes": "..."
}
```

---

## 4. 主链路中的风险控制点

### OCR 风险信号

- `short_text`
- `anchor_missing`
- `broken_lines`
- `heavy_noise`
- `readability_poor`

### 评分风险信号

- `invalid_essay`
- `task_not_established`
- `cap_applied`
- `very_low_score`

### 最终复核来源

复核建议应由两层共同贡献：

- OCR 提供“文本质量风险”
- 评分层提供“评分业务风险”

---

## 5. 当前阶段定位

当前核心仓库若要上传和维护，主链路应沉淀为：

1. `essay_ocr`：OCR 业务层
2. `essay_grading`：评分业务层
3. `schemas/ocr_result.schema.json`
4. `schemas/grading_result.schema.json`
5. `framework/essay_scoring_framework_v1.json`
6. `tasks/family_rules_school_rules_task_v1.json`

这样以后换题时：

- OCR 层不需要重写
- Framework 不需要重写
- 只新增新的 Task Spec

---

## 6. 一句话总结

这条主链路的正确抽象是：

```text
OCR 负责把图像变成“可评分文本 + 可读性证据”，
评分标准系统负责把“文本 + 证据”变成“结构化评分结果”。
```
