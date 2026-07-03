# 测试用例 001：高分、较准样本

- 姓名：丁梓彤
- 学号：250803
- 人工分：24
- AI v2 分：23
- 误差：-1
- 目标：验证高分样本在 OCR 噪声存在时，系统是否仍能保持高分容错，不机械压低。

## 诊断价值

这个样本能检验：

- 双侧展开识别是否稳定
- 有效内容单元计数是否正常
- 高分语言容错是否生效

## OCR 文本

```text
Dear Eric,
H'ThereaemaryrulesinmyYouhaveto
tollow them. First, you have to wear a school uniform, because it
builds school spirit. Second, you mustr't bring m your mobile phone
to class, because you need to focus on learning. Third, we mustn't eat
frult and snacks in class, but we can drink water.
There are some rules at home too. We mustr't hany out
with our friends at weekdays. We can must finish our homework before
we watch, and then we wa can watch watch TV.
There are many rules in our life, but they can help you become
a better person.
Yours,
Mary
```

## 期望判断重点

- 不能因为 mustr't / hany / frult 等 OCR/拼写问题压到中低档
- 仍应识别出：校服、手机、零食/水果、工作日不能外出、先作业后看电视等规则单元
- school + family 双侧展开成立
