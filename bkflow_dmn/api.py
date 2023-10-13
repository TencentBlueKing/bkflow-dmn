# -*- coding: utf-8 -*-
from bkflow_dmn.data_model import SingleDecisionTable


def decide_single_table(decision_table: dict, facts: dict, strict_mode: bool = True):
    dt = SingleDecisionTable(**decision_table)
    result = dt.decide(facts, strict_mode)
    return result
