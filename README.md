# ocr-score

跨平台的 OCR + 英语作文评分核心仓库。

## 目标

本仓库只保留核心业务：

- OCR 客户端与文本清洗
- 通用作文评分框架（Framework）
- 题目任务配置（Task Spec）
- 评分业务核心（rubric loading / prompt building / validation / grading service）

不包含：

- 智学网登录态/HAR/token
- 本地实验输出目录
- 前端页面自动化
- 网站抓取脚本

## 目录结构

```text
src/
  essay_grading/
  essay_ocr/

docs/
framework/
rubrics/
tasks/
schemas/
examples/
```

## 当前状态

- `essay_grading`：纯评分业务骨架已可导入
- `essay_ocr`：基于 PaddleOCR AIStudio 的最小 OCR 客户端与批量处理
- `framework/tasks/rubrics`：评分标准体系与当前题目的任务配置

## 安装（开发模式）

```bash
pip install -e .
```

## 后续

后续可以在这个核心仓库基础上分别接：

- 本地 Web UI
- 正式阅卷系统接入层
- 批量处理工具
