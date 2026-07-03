# 测试用例 002：低分高估样本

- 姓名：李梦然
- 学号：250817
- 人工分：0
- AI v2 分：13
- 误差：+13
- 目标：验证极低分样本是否会被错误抬入 10-14 分区间。

## 诊断价值

这个样本能检验：

- task_not_established 是否足够严格
- 模糊可猜内容是否被错误计入有效内容单元
- 模板壳子是否抬高任务完成度和结构分

## OCR 文本

```text
Dear Eric,
Hi I'm Mary My daily roukine. In.
How's it going?
home I don't take 3o ninte V watch Tv. I don't
yogurt and clean no thing. I every eat friat firut In.
sike school and class I we dou't. get eat thing. we don't.
on
in class play I bo Myhome alarm in 5:30 A.M.
but My No like these daily routine routinese. My mum
have a accmplishment my adive My mum Not these
I like subjects is chinese and habby dance and play
the guitar.
Yours,
Mary
```

## 期望判断重点

- 不能因为有 Dear Eric / Yours / home / school / class 这些词就判定任务成立
- 大部分句子不可稳定复述成规则
- 正文不能清楚形成 family/home rules 与 school rules 的双侧展开
- 应强烈倾向 0-4 分，至少不能进入 10-14 分
