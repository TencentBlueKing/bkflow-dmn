# -*- coding: utf-8 -*-
import abc
from typing import List

from bkflow_dmn.exception import ValidationError, HitPolicyMatchError


class BaseHitPolicy(metaclass=abc.ABCMeta):
    """
    Abstract base class for all policies.
    """

    MAYBE_MULTIPLE_OUTPUT = False
    EMPTY_OUTPUT = []

    def __init__(self, strict_mode=True, *args, **kwargs):
        self.strict_mode = strict_mode

    def __call__(self, rule_results: List[bool], outputs: List, *args, **kwargs):
        if not isinstance(rule_results, list) or not isinstance(outputs, list) or len(rule_results) != len(outputs):
            raise ValidationError("rule_results and outputs must have the same length")
        return self.handle(rule_results, outputs, *args, **kwargs)

    @abc.abstractmethod
    def handle(self, rule_results: List[bool], outputs: List, *args, **kwargs):
        pass

    def multiple_output(self):
        return self.MAYBE_MULTIPLE_OUTPUT


class UniqueHitPolicy(BaseHitPolicy):
    def handle(self, rule_results: List[bool], outputs: List, *args, **kwargs):
        if self.strict_mode:
            if rule_results.count(True) != 1:
                raise HitPolicyMatchError("Unique Hit Policy requires exactly one True result")
            return outputs[rule_results.index(True)]
        try:
            return outputs[rule_results.index(True)]
        except ValueError:
            return self.EMPTY_OUTPUT


class AnyHitPolicy(BaseHitPolicy):
    def handle(self, rule_results: List[bool], outputs: List, *args, **kwargs):
        if self.strict_mode:
            if not any(rule_results):
                raise HitPolicyMatchError("Any Hit Policy requires at least one True result")
            all_match_idxes = [i for i, r in enumerate(rule_results) if r is True]
            match_outputs = [outputs[i] for i in all_match_idxes]
            # 检查所有的 match_outputs 是否都相等
            if not all(output == match_outputs[0] for output in match_outputs):
                raise HitPolicyMatchError("All match outputs must be equal")
            return outputs[rule_results.index(True)]
        try:
            return outputs[rule_results.index(True)]
        except ValueError:
            return self.EMPTY_OUTPUT


class FirstHitPolicy(BaseHitPolicy):
    def handle(self, rule_results: List[bool], outputs: List, *args, **kwargs):
        if self.strict_mode:
            if not any(rule_results):
                raise HitPolicyMatchError("First Hit Policy requires at least one True result")
            return outputs[rule_results.index(True)]
        try:
            return outputs[rule_results.index(True)]
        except ValueError:
            return self.EMPTY_OUTPUT


class PriorityHitPolicy(BaseHitPolicy):
    """
    如果不是 strict 模式，则第一个命中的最高优先级作为输出
    """

    def handle(self, rule_results: List[bool], outputs: List, *args, **kwargs):
        if not any(rule_results):
            if self.strict_mode:
                raise HitPolicyMatchError("Priority Hit Policy requires at least one True result")
            return self.EMPTY_OUTPUT
        match_outputs = [outputs[i] for i in range(len(rule_results)) if rule_results[i]]
        match_outputs = sorted(match_outputs, key=lambda x: list(x[i] for i in range(len(x))), reverse=True)
        if self.strict_mode and len(match_outputs) > 1 and match_outputs[0] == match_outputs[1]:
            raise HitPolicyMatchError("Priority Hit Policy requires exactly one True result")
        return match_outputs[0]


class RuleOrderHitPolicy(BaseHitPolicy):
    MAYBE_MULTIPLE_OUTPUT = True

    def handle(self, rule_results: List[bool], outputs: List, *args, **kwargs):
        return [outputs[i] for i in range(len(rule_results)) if rule_results[i]]


class OutputOrderHitPolicy(BaseHitPolicy):
    MAYBE_MULTIPLE_OUTPUT = True

    def handle(self, rule_results: List[bool], outputs: List, *args, **kwargs):
        match_outputs = [outputs[i] for i in range(len(rule_results)) if rule_results[i]]
        return sorted(match_outputs, key=lambda x: list(x[i] for i in range(len(x))), reverse=True)


class CollectHitPolicy(BaseHitPolicy):
    MAYBE_MULTIPLE_OUTPUT = True
    COLLECT_METHODS = {
        "sum": sum,
        "max": max,
        "min": min,
        "count": len,
    }

    def __init__(self, strict_mode=True, *args, **kwargs):
        super().__init__(strict_mode=strict_mode, *args, **kwargs)
        self.collect_policy = kwargs.get("collect_policy", "").lower()

    def handle(self, rule_results: List[bool], outputs: List, *args, **kwargs):
        match_outputs = [outputs[i] for i in range(len(rule_results)) if rule_results[i]]
        if self.collect_policy in self.COLLECT_METHODS:
            method = self.COLLECT_METHODS[self.collect_policy]
            collect_result = [method(col) for col in zip(*match_outputs)]
            return collect_result
        return match_outputs

    def multiple_output(self):
        return self.collect_policy not in self.COLLECT_METHODS


def get_hit_policy(hit_policy_name: str, strict_mode=True, *args, **kwargs):
    """
    根据 hit_policy_name 获取对应的 hit_policy
    """
    mappings = {
        "Unique": UniqueHitPolicy,
        "Any": AnyHitPolicy,
        "First": FirstHitPolicy,
        "Priority": PriorityHitPolicy,
        "RuleOrder": RuleOrderHitPolicy,
        "OutputOrder": OutputOrderHitPolicy,
        "Collect": CollectHitPolicy,
    }
    if hit_policy_name != "Collect" and hit_policy_name.startswith("Collect"):
        collect_policy = hit_policy_name[len("Collect") + 1 : -1]
        return CollectHitPolicy(strict_mode=strict_mode, collect_policy=collect_policy, *args, **kwargs)
    else:
        return mappings[hit_policy_name](strict_mode, *args, **kwargs)
