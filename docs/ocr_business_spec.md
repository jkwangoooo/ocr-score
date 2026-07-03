# OCR 业务规范（正式主链路）

## 1. 目标

当前正式主链路已经明确为：

```text
作文图像
-> OCR
-> 文本清洗
-> 评分标准系统
-> 输出分数 / 分项 / 理由 / 复核标记
```

因此 OCR 必须被定义为一层**独立业务能力**，而不是评分标准的一部分。

本规范只回答三件事：

1. OCR 层负责什么
2. OCR 层输出什么
3. OCR 层如何为评分层提供可用文本与风险信号

---

## 2. OCR 业务边界

### OCR 层负责

1. 接收作文图像输入
2. 调用 OCR 引擎识别文本
3. 保留 OCR 原始结果
4. 输出原始文本
5. 提供可读性/置信度/异常信号
6. 进行**轻度清洗**（仅移除页面噪声，不做评分判断）

### OCR 层不负责

1. 不负责评分
2. 不负责判定高分/低分
3. 不负责判断是否套作
4. 不负责决定总分
5. 不负责题目任务完成度打分

这点非常重要：

```text
OCR 只能提供“文本和可读性证据”，
不能直接侵入评分业务本体。
```

---

## 3. OCR 层输入

正式输入应抽象成：

```json
{
  "image": "<local path / binary / url>",
  "context": {
    "source": "web|batch|api",
    "page_role": "essay_page",
    "task_id": "optional"
  }
}
```

注意：

- OCR 层不应依赖本地特定路径结构
- 不应依赖智学网目录命名
- `page_role=essay_page` 只是上游告知当前图片是什么，不意味着 OCR 层知道题目规则

---

## 4. OCR 层输出

OCR 层输出应分为三层：

### 4.1 原始层（Raw OCR Output）

用于追溯与调试：

```json
{
  "raw_provider": "paddleocr_aistudio",
  "raw_model": "PP-OCRv6",
  "raw_result": "...jsonl/json..."
}
```

### 4.2 文本层（Raw Text Output）

直接识别出来的文本：

```json
{
  "raw_text": "..."
}
```

### 4.3 质量层（Readability / Confidence Output）

用于后续复核和评分稳定性判断：

```json
{
  "text_quality": "normal|noisy|short|broken",
  "quality_flags": [
    "short_text",
    "broken_lines",
    "heavy_noise",
    "anchor_missing"
  ],
  "readability_notes": "..."
}
```

### 4.4 清洗层（Clean Text Output）

轻度清洗后的正文：

```json
{
  "clean_text": "..."
}
```

---

## 5. OCR 轻度清洗规则

OCR 层允许做**轻度清洗**，但只能做对评分无争议的清理。

### 可清洗

- 姓名、学号、班排、校排
- `第四节写作`
- `86-86题`
- `86:xx分`
- 明显页面噪声
- 纯空行、纯数字噪声

### 不可在 OCR 层做的事

- 不能在 OCR 层判断“这是不是有效规则单元”
- 不能在 OCR 层决定作文是否切题
- 不能在 OCR 层提前压分
- 不能在 OCR 层把模糊句意改写成更完整内容

换句话说：

```text
OCR 清洗可以删除噪声，
但不能替模型/评分系统“解释作文”。
```

---

## 6. OCR 质量分级建议

建议把 OCR 结果做成 4 档质量标签：

### normal

- 文本整体可读
- 主要句子能恢复
- 书信结构锚点可见

### noisy

- 存在明显粘连、错词、断句
- 但大多数句子仍可恢复

### short

- 清洗后文本过短
- 正文长度不足以稳定判断

### broken

- 大量句子无法恢复
- 结构锚点缺失或正文严重碎裂

这个标签不直接决定分数，但应直接进入后续复核逻辑。

---

## 7. OCR 质量 flags 建议

建议至少输出这些 flags：

- `short_text`
- `anchor_missing`
- `broken_lines`
- `heavy_noise`
- `possible_crop_issue`
- `text_sparse`
- `readability_poor`

这些 flags 的作用：

- 给评分层提供上下文
- 给 review 层提供证据
- 方便后续回溯 OCR 是不是核心问题

---

## 8. OCR 与评分层的接口关系

评分层接收的，不应是裸 OCR 原文，而应是：

```json
{
  "essay_text": "clean_text",
  "context": {
    "text_quality": "...",
    "quality_flags": [...],
    "readability_notes": "..."
  }
}
```

也就是说：

- `clean_text` 是评分正文
- `text_quality` 和 `quality_flags` 只作为辅助信号
- 评分层仍然自己决定是否复核、是否低置信

---

## 9. OCR 层与复核层的关系

OCR 不做最终复核决定，但要提供足够信号让复核层做判断。

### OCR 可直接触发的建议复核信号

- `short_text`
- `anchor_missing`
- `broken_lines`
- `heavy_noise`
- `readability_poor`

### 评分层结合 OCR 后进一步决定的复核信号

- `invalid_essay`
- `cap_applied`
- `very_low_score`
- `borderline_task_slots`

---

## 10. OCR 层成熟度要求

一个可进入正式主链路的 OCR 层，最低应满足：

1. 能稳定输出 `raw_text`
2. 能保留 `raw_result`
3. 能输出 `clean_text`
4. 能输出 `text_quality`
5. 能输出 `quality_flags`
6. 不能把评分业务逻辑混进去

如果不满足这些，OCR 仍然只是工具脚本，不算正式业务层。

---

## 11. 一句话总结

OCR 在正式系统中的正确角色是：

```text
把作文图像转换成可评分文本，
并提供可读性与异常信号，
但不越权进入评分判断本体。
```
