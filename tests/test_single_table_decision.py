# -*- coding: utf-8 -*-
import pytest

from bkflow_dmn.api import decide_single_table
from bkflow_dmn.data_model import SingleDecisionTable
from tests.data import (
    UNIQUE_TEST_DATA,
    ANY_TEST_DATA,
    FIRST_TEST_DATA,
    PRIORITY_TEST_DATA,
    RULE_ORDER_TEST_DATA,
    OUTPUT_ORDER_TEST_DATA,
    COLLECT_TEST_DATA,
    BATCH_TEST_DATA,
)

test_data = [
    *UNIQUE_TEST_DATA,
    *ANY_TEST_DATA,
    *FIRST_TEST_DATA,
    *PRIORITY_TEST_DATA,
    *RULE_ORDER_TEST_DATA,
    *OUTPUT_ORDER_TEST_DATA,
    *COLLECT_TEST_DATA,
    *BATCH_TEST_DATA,
]


@pytest.mark.parametrize(
    "single_table, facts, expected",
    test_data,
)
def test_single_table_decision_strict_mode(single_table, facts, expected):
    result = decide_single_table(single_table, facts=facts, strict_mode=True)
    assert result == expected


def test_single_table_inputs_autocomplete():
    rows = [
        [">=10"],
        [">10"],
        ["[1..2]"],
        ["(1..2]"],
        ["<=10"],
        ["<10"],
        ['"boy"'],
        ["1"],
        ["-1"],
        ["1.2"],
        ["-2.3"],
        ["true"],
        ["false"],
        ["null"],
        ["1 and 1"],
        ["before(x, [2..3])"],
        ["< 10, > 20"],
        ["<10, >20"],
    ]
    TEST_TABLE = {
        "title": "testing",
        "hit_policy": "Unique",
        "inputs": {
            "cols": [{"id": "input"}],
            "rows": rows,
        },
        "outputs": {
            "cols": [{"id": "output"}],
            "rows": [[1]] * len(rows),
        },
    }
    table = SingleDecisionTable(**TEST_TABLE)
    auto_completed_inputs = table.feel_exp_of_inputs
    assert auto_completed_inputs == [
        ["input>=10"],
        ["input>10"],
        ["input in [1..2]"],
        ["input in (1..2]"],
        ["input<=10"],
        ["input<10"],
        ['input="boy"'],
        ["input=1"],
        ["input=-1"],
        ["input=1.2"],
        ["input=-2.3"],
        ["input=true"],
        ["input=false"],
        ["input=null"],
        ["1 and 1"],
        ["before(x, [2..3])"],
        ["input< 10 or input> 20"],
        ["input<10 or input>20"],
    ]


@pytest.mark.parametrize(
    "single_table, facts, expected",
    test_data,
)
def test_single_table_decision_strict_mode_benchmark(benchmark, single_table, facts, expected):
    result = benchmark(decide_single_table, single_table, facts=facts, strict_mode=True)
    assert result == expected
