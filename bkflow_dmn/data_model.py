# -*- coding: utf-8 -*-
import re
from enum import Enum
from typing import List, Union

from pydantic import BaseModel, root_validator

from bkflow_feel.api import parse_expression

from bkflow_dmn.hit_policy import get_hit_policy


class HitPolicyEnum(str, Enum):
    Unique = "Unique"
    Any = "Any"
    First = "First"
    Priority = "Priority"
    RuleOrder = "RuleOrder"
    OutputOrder = "OutputOrder"
    Collect = "Collect"
    Collect_SUM = "Collect(Sum)"
    Collect_Max = "Collect(Max)"
    Collect_Min = "Collect(Min)"
    Collect_Count = "Collect(Count)"


class DataTableField(BaseModel):
    id: str
    name: str = None
    desc: str = None


class DataTable(BaseModel):
    cols: List[DataTableField]
    rows: List[Union[List[str], str]]

    @root_validator(skip_on_failure=True)
    def validate_length(cls, values: dict):
        for row in values["rows"]:
            if isinstance(row, list) and len(row) != len(values["cols"]):
                raise ValueError("the length of row should be the same as the length of cols")
        return values

    @property
    def col_ids(self):
        return [col.id for col in self.cols]


class SingleDecisionTable(BaseModel):
    title: str
    hit_policy: HitPolicyEnum = HitPolicyEnum.Unique
    inputs: DataTable
    outputs: DataTable

    def decide(self, facts: dict, strict_mode=True):
        """
        单表单次决策函数
        :param facts: 单次决策对应的事实，对应于决策上下文
        :param strict_mode: 是否采用严格模式，当为 True 时，决策逻辑会进行一些校验并在失败时抛出异常
        :return: 决策结果
        """
        feel_inputs: List[Union[List[str], str]] = self.feel_exp_of_inputs
        feel_outputs: List[str] = self.outputs.rows
        parsed_inputs = [
            all([parse_expression(feel_input, facts) for feel_input in feel_input_row])
            for feel_input_row in feel_inputs
        ]
        parsed_outputs = []
        for feel_output_row in feel_outputs:
            parsed_outputs.append([parse_expression(feel_output, facts) for feel_output in feel_output_row])
        hit_policy = get_hit_policy(self.hit_policy_value, strict_mode=strict_mode)
        outputs_result = hit_policy(parsed_inputs, parsed_outputs)
        final_result = []
        if hit_policy.multiple_output():
            final_result.extend(
                [
                    {key: value for key, value in zip(self.outputs.col_ids, outputs_result_row)}
                    for outputs_result_row in outputs_result
                ]
            )
        elif outputs_result:
            final_result.append({key: value for key, value in zip(self.outputs.col_ids, outputs_result)})
        return final_result

    @root_validator(skip_on_failure=True)
    def validate_length(cls, values: dict):
        if len(values["inputs"].rows) != len(values["outputs"].rows):
            raise ValueError("the length of inputs should be the same as the length of outputs")
        return values

    @property
    def hit_policy_value(self):
        return self.hit_policy.value

    @property
    def feel_exp_of_inputs(self):
        col_ids = [col.id for col in self.inputs.cols]
        result = []
        for row in self.inputs.rows:
            if isinstance(row, str):
                result.append([row])
                continue
            row_result = []
            for idx, unit in enumerate(row):
                pured_unit = unit.strip()
                if pured_unit == "":
                    continue
                handler = TableUnitHandler(unit_exp=pured_unit, col_id=col_ids[idx])
                row_result.append(handler.get_handled_exp())
            result.append(row_result)
        return result


class TableUnitHandler:
    OPERATOR_PATTERNS = {
        r"^>(.*?)": "",
        r"^<(.*?)": "",
        r"[\[\(](.*?)\.\.(.*?)[\]\)]": " in ",
        r"\"(.*?)\"": "=",
        r"-?\d+(\.\d+)?": "=",
        r"true": "=",
        r"false": "=",
        r"null": "=",
    }
    OR_OPERATOR = ","

    def __init__(self, unit_exp: str, col_id: str):
        self.exp = unit_exp
        self.col_id = col_id

    def get_handled_exp(self):
        exp_splices = [exp.strip() for exp in self.exp.split(self.OR_OPERATOR)]
        union_patterns = "|".join(self.OPERATOR_PATTERNS.keys())

        # 不能进行自动补全的情况
        if any([re.fullmatch(union_patterns, exp) is None for exp in exp_splices]):
            return self.exp

        handled_exp_splices = []
        for exp in exp_splices:
            for pattern, operator in self.OPERATOR_PATTERNS.items():
                if re.fullmatch(pattern, exp):
                    handled_exp_splices.append(f"{self.col_id}{operator}{exp}")
                    break

        return " or ".join(handled_exp_splices)
