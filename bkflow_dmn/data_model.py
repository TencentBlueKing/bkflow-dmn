# -*- coding: utf-8 -*-
from enum import Enum
from typing import List

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
    rows: List[List[str]]

    @root_validator(skip_on_failure=True)
    def validate_length(cls, values: dict):
        for row in values["rows"]:
            if len(row) != len(values["cols"]):
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
        feel_inputs: List[List[str]] = self.feel_exp_of_inputs
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
        if not hit_policy.multiple_output():
            if outputs_result:
                final_result.append({key: value for key, value in zip(self.outputs.col_ids, outputs_result)})
        else:
            for outputs_result_row in outputs_result:
                final_result.append({key: value for key, value in zip(self.outputs.col_ids, outputs_result_row)})
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
        operator_prefix = {
            ">": "",
            "<": "",
            "[": " in ",
            "(": " in ",
        }
        or_operator = ","

        result = []
        for row in self.inputs.rows:
            row_exps = []
            for idx, unit in enumerate(row):
                pured_unit = unit.strip()
                if pured_unit == "":
                    continue
                unit_exps = []
                vals = [val.strip() for val in pured_unit.split(or_operator) if val.strip()]
                for val in vals:
                    if val[0] in operator_prefix:
                        unit_exps.append(f"{col_ids[idx]}{operator_prefix[val[0]]}{val}")
                    else:
                        unit_exps.append(f"{col_ids[idx]}={val}")
                row_exps.append(f'({" or ".join(unit_exps)})' if len(unit_exps) > 1 else unit_exps[0])
            result.append(row_exps)
        return result
