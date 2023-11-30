# bkflow-dmn: A DMN(Decision Model Notation) library for Python

## 简介
bkflow-dmn 是一款基于 Python 的 DMN(Decision Model Notation) 库，使用 FEEL(Friendly Enough Expression Language) 作为描述语言，可以作为决策引擎，用于解决实际业务场景中的决策问题。

## Quick Start

### 1. 安装依赖

```
$ pip install bkflow-dmn
```

### 2. 构造决策表数据
目前，bkflow-dmn 支持单表决策，支持通过 python 字典对决策表进行描述，示例如下：

``` python
decision_table = {
    "title": "decision table", # 表格标题，目前没有实际用途
    "hit_policy": "Unique", # 命中策略
    "inputs": { # 输入表
        "cols": [{"id": "score"}, {"id": "sex"}], # 列描述
        "rows": [ # 行对应的值
            ["[0..70]", '"boy"'],
            ["(70..80]", '"boy"'],
            ["(80..90]", '"boy"'],  # 对于实际场景中，如果希望【单行表示多列表达式】，则直接用字符串类型进行描述，形如 'score in (80..90] and sex="boy"'
            ["(90..100]", '"boy"'],
            ["[0..60]", '"girl"'],
            ["(60..70]", '"girl"'],
            ["(70..80]", '"girl"'],
            ["(80..100]", '"girl"'],
        ],
    },
    "outputs": { # 输出表
        "cols": [{"id": "level"}], # 列描述
        "rows": [ # 行对应的值
            ['"bad"'],
            ['"good"'],
            ['"good+"'],
            ['"good++"'],
            ['"bad"'],
            ['"good"'],
            ['"good+"'],
            ['"good++"'],
        ],
    },
}
```

其中，输入表默认会将单元格中的表达式作为整体表达式进行真值判定，同时支持一些快捷填写方式（仅在未使用【单行表示多列表达式】的情况下)：

| 快捷填写方式 | 补全后表达式（假设列名为 x） | 
| --- | --- |
| ">=10" | "x>=10" |
| ">10" | "x>10" |
| "<=10" | "x<=10" |
| "<10" | "x<10" |
| "[1..2]" | "x in [1..2]" |
| "(1..2]" | "x in (1..2]" |
| '"boy"' | 'x="boy"' |
| "1" | "x=1" |
| "1.2" | "x=1.2" |
| "-1" | "x=-1" |
| "-2.3" | "x=-2.3" |
| "true" | "x=true" |
| "false" | "x=false" |
| "null" | "x=null" |


### 3. 调用函数进行决策

``` python
from bkflow_dmn.api import decide_single_table

facts = {"score": 10, "sex": "boy"} # 输入表的列数据和上下文
result = decide_single_table(decision_table, facts, strict_mode=True)  # [{"level": "bad"}]
```

如需进行多表决策，目前可结合 流程引擎 [bamboo-engine](https://github.com/TencentBlueKing/bamboo-engine) 实现。

### 4. 支持的命中策略
| 命中策略 | 说明 |
| --- | --- |
| Unique | 唯一命中, strict_mode 下需要保证只有一条规则命中 |
| Any | 任意命中，strict_mode 下需要保证有命中结果且命中的结果是唯一的 |
| First | 第一命中, strict_mode 下需要保证有规则命中 |
| Priority | 优先级命中，以输出作为排序优先级，strict_mode 下需要保证有规则命中，且优先级排序结果唯一 | 
| RuleOrder | 多规则命中策略，按照规则定义顺序输出 | 
| OutputOrder | 多输出命中策略，按照输出顺序排序输出 |
| Collect | 多输出命中策略，输出所有符合的结果 | 
| Collect(Sum) | 多输出命中策略，按照输出值求和 |
| Collect(Max) | 多输出命中策略，按照输出值求最大 |
| Collect(Min) | 多输出命中策略，按照输出值求最小 |
| Collect(Count) | 多输出命中策略，按照输出值求个数 |

