# 英语作文评分标准体系（最终建议结构）

## 1. 分层目标

当前标准体系已经拆成两层核心对象：

1. **Framework**
   - 题目无关
   - 定义评分业务母版
2. **Task Spec**
   - 题目相关
   - 定义某道作文题的任务槽位与边界要求

下一步的目标不是继续堆题目专属规则，而是让三类资产边界更清楚：

```text
Framework
Task Spec
Prompt Template
```

---

## 2. 最终结构建议

### A. Framework（题目无关）

建议保留：

- gating_rules
- dimensions
- cap_rule_types
- review_rules
- effective_content_unit 定义
- result_contract

不保留：

- 任何具体题目关键词
- 任何具体内容点（如 family / school / rules）
- 任何具体范文/题干细节

### B. Task Spec（题目相关）

建议保留：

- prompt_context.task
- genre
- writer_role / audience
- required_task_slots
- effective_content_unit_examples
- task_specific_invalid_cases
- task_specific_caps
- high_score_tolerance_notes
- low_score_guardrails

不保留：

- 通用维度定义
- 通用 review 规则
- 通用 gating 规则

### C. Prompt Template（执行层）

Prompt Template 不应该再重复发明规则。

它的作用是：

- 把 Framework 的通用规则翻译成模型可执行的指令
- 把 Task Spec 的题目要求、任务槽位、封顶规则、低分边界注入进去
- 输出固定 schema

所以 Prompt Template 应视为：

```text
Framework + Task Spec 的投影层
```

而不是第三套独立规则来源。

---

## 3. 当前体系中仍存在的重复点

### 重复点 1：Task Spec 与 rubric v2 都在描述题目要求

目前：

- `family_rules_school_rules_task_v1.json`
- `family_rules_school_rules_v2.json`

都在表达本题要求、封顶、低分边界。

问题：

- 规则来源双份维护
- 后续容易漂移

建议：

```text
长期只保留 Task Spec 作为题目规则来源
```

### 重复点 2：Prompt 与 rubric v2_gate_rules 都在描述封顶逻辑

问题：

- 一改就要改两份以上
- 容易出现字段和表述不一致

建议：

```text
Prompt 不再手写规则正文，改成由 Framework + Task Spec 拼接生成
```

### 重复点 3：v2_optimization / v2.1_adjustments 属于演化文档，不是正式标准资产

这些文件保留价值在于：

- 追溯为什么这么改
- 保留实验依据

但不应被当成正式运行规则来源。

---

## 4. 建议保留的正式资产

如果要形成“最终可维护体系”，建议正式资产只保留：

### 通用层
- `essay_scoring_framework_v1.json`
- `essay_scoring_framework_v1.md`

### 题目层
- `family_rules_school_rules_task_v1.json`

### 执行层
- `essay_scoring_prompt_template_v1.md`
  - 注意：它应尽量通用，运行时按 Framework + Task Spec 注入内容

### 验证与演化层（非正式规则源）
- `family_rules_school_rules_v2_optimization.md`
- `family_rules_school_rules_v2_1_adjustments.md`
- 历次精度报告

这样体系最清楚：

```text
正式规则源：Framework + Task Spec
历史证据：优化文档 + 精度报告
```

---

## 5. 下一步该收敛的方向

### 方向 1：不再把 v2 rubric 作为长期正式主文件

因为它本质上混合了：

- 通用框架规则
- 当前题目规则
- 提示词执行倾向

建议未来将它视为：

```text
过渡态聚合文件
```

### 方向 2：把 Prompt 改成“可组装模板”

即未来不再维护一份固定题目 prompt，而是：

- 固定的 framework prompt 框架
- 加载 task spec
- 拼接本题要求

### 方向 3：把验证逻辑也对应到 Framework / Task Spec

以后跑实验时，应回答的是：

- Framework 哪条通用规则需要改
- 还是 Task Spec 哪个任务槽位定义不清楚

而不是笼统说“prompt 不准”。

---

## 6. 当前阶段的最优停点

现在标准层已经足够完整，最优停点是：

1. **确认正式规则源就是**
   - `essay_scoring_framework_v1.json`
   - `family_rules_school_rules_task_v1.json`

2. **把 v2/v2.1 视为当前实验版实现与修订证据**

3. **后续若再换作文题，只新增 Task Spec，不再改 Framework 本体**

---

## 7. 一句话总结

现在最干净、最可扩展的标准体系应该是：

```text
Framework 负责“如何评分”
Task Spec 负责“这道题要答什么”
Prompt 负责“把前两者翻译给模型”
```

只要坚持这三层边界，后面换题、换平台、换 OCR、换前端，都不会把评分业务重新搅乱。
