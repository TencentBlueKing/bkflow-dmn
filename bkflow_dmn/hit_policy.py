# -*- coding: utf-8 -*-
import abc
from abc import ABCMeta
from typing import List

from bkflow_dmn.exceptions import ValidationError, HitPolicyMatchError


class BaseHitPolicy(metaclass=abc.ABCMeta):
    """
    Abstract base class for all policies.
    """

    def __init__(self, rule_results: List[bool], outputs: List, *args, **kwargs):
        if not isinstance(rule_results, list) or not isinstance(outputs, list) or len(rule_results) != len(outputs):
            raise ValidationError("rule_results and outputs must have the same length")
        self.rule_results = rule_results
        self.outputs = outputs

    @abc.abstractmethod
    def handle(self):
        pass


class StrictModeSupportHitPolicy(BaseHitPolicy, metaclass=ABCMeta):
    def __init__(self, rule_results: List[bool], outputs: List, strict_mode=False, *args, **kwargs):
        super().__init__(rule_results, outputs, *args, **kwargs)
        self.strict_mode = strict_mode


class UniqueHitPolicy(BaseHitPolicy):
    def handle(self):
        if self.rule_results.count(True) != 1:
            raise HitPolicyMatchError("Unique Hit Policy requires exactly one True result")
        return self.outputs[self.rule_results.index(True)]


class AnyHitPolicy(StrictModeSupportHitPolicy):
    def handle(self):
        if not any(self.rule_results):
            raise HitPolicyMatchError("Any Hit Policy requires at least one True result")
        if self.strict_mode:
            all_match_idxes = [i for i, r in enumerate(self.rule_results) if r is True]
            match_outputs = [self.outputs[i] for i in all_match_idxes]
            # 检查所有的 match_outputs 是否都相等
            if not all(output == match_outputs[0] for output in match_outputs):
                raise HitPolicyMatchError("All match outputs must be equal")

        return self.outputs[self.rule_results.index(True)]


class FirstHitPolicy(BaseHitPolicy):
    def handle(self):
        if not any(self.rule_results):
            raise HitPolicyMatchError("First Hit Policy requires at least one True result")
        return self.outputs[self.rule_results.index(True)]


class PriorityHitPolicy(StrictModeSupportHitPolicy):
    """
    如果不是 strict 模式，则第一个命中的最高优先级作为输出
    """

    def handle(self):
        if not any(self.rule_results):
            raise HitPolicyMatchError("Priority Hit Policy requires at least one True result")
        match_outputs = [self.outputs[i] for i in range(len(self.rule_results)) if self.rule_results[i]]
        sorted(match_outputs, key=lambda x: list(x[i] for i in range(len(x))), reverse=True)
        if self.strict_mode and len(match_outputs) > 1 and match_outputs[0] == match_outputs[1]:
            raise HitPolicyMatchError("Priority Hit Policy requires exactly one True result")
        return match_outputs[0]


class RuleOrderHitPolicy(BaseHitPolicy):
    def handle(self):
        return [self.outputs[i] for i in range(len(self.rule_results)) if self.rule_results[i]]


class OutputOrderHitPolicy(BaseHitPolicy):
    def handle(self):
        match_outputs = [self.outputs[i] for i in range(len(self.rule_results)) if self.rule_results[i]]
        sorted(match_outputs, key=lambda x: list(x[i] for i in range(len(x))), reverse=True)
        return match_outputs


class CollectHitPolicy(BaseHitPolicy):
    COLLECT_METHODS = {
        "sum": sum,
        "max": max,
        "min": min,
        "count": len,
    }

    def __init__(self, rule_results: List[bool], outputs: List, *args, **kwargs):
        super().__init__(rule_results, outputs, *args, **kwargs)
        self.collect_policy = kwargs.get("collect_policy")

    def handle(self):
        match_outputs = [self.outputs[i] for i in range(len(self.rule_results)) if self.rule_results[i]]
        if self.collect_policy in self.COLLECT_METHODS:
            method = self.COLLECT_METHODS[self.collect_policy]
            collect_result = [method(col) for col in zip(*match_outputs)]
            return collect_result
        return match_outputs
