# -*- coding: utf-8 -*-
import pytest

from bkflow_dmn.api import decide_single_table
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


@pytest.mark.parametrize(
    "single_table, facts, expected",
    test_data,
)
def test_single_table_decision_strict_mode_benchmark(benchmark, single_table, facts, expected):
    result = benchmark(decide_single_table, single_table, facts=facts, strict_mode=True)
    assert result == expected
