# -*- coding: utf-8 -*-
"""
Audit module for capturing decision execution traces.
Uses ContextVar to avoid changing function signatures.
"""
from contextvars import ContextVar
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

@dataclass
class DecisionTrace:
    """Represents a single decision table execution trace."""
    table_title: str
    facts: Dict[str, Any]
    matched_rules: List[int]  # Indices of rules that matched
    rule_results: List[bool]  # Full match vector
    outputs: List[Any]
    final_result: List[Dict[str, Any]]
    # Enhanced details
    input_expressions: List[List[str]] = field(default_factory=list)  # Raw input expressions per rule
    output_expressions: List[List[str]] = field(default_factory=list)  # Raw output expressions per rule
    input_col_ids: List[str] = field(default_factory=list)
    output_col_ids: List[str] = field(default_factory=list)
    evaluated_outputs: List[List[str]] = field(default_factory=list)  # Expressions with values substituted

@dataclass
class AuditTrail:
    """Collection of all decision traces in an execution."""
    traces: List[DecisionTrace] = field(default_factory=list)
    
    def add_trace(self, trace: DecisionTrace):
        self.traces.append(trace)

# Global context variable for audit trail
_audit_context: ContextVar[Optional[AuditTrail]] = ContextVar('audit_context', default=None)

def start_audit() -> AuditTrail:
    """
    Start a new audit session.
    Returns the AuditTrail object that will collect traces.
    """
    trail = AuditTrail()
    _audit_context.set(trail)
    return trail

def stop_audit() -> Optional[AuditTrail]:
    """
    Stop the current audit session and return the collected trail.
    """
    trail = _audit_context.get()
    _audit_context.set(None)
    return trail

def is_auditing() -> bool:
    """Check if auditing is currently active."""
    return _audit_context.get() is not None

def log_decision(
    table_title: str,
    facts: Dict[str, Any],
    rule_results: List[bool],
    outputs: List[Any],
    final_result: List[Dict[str, Any]],
    input_expressions: List[List[str]] = None,
    output_expressions: List[List[str]] = None,
    input_col_ids: List[str] = None,
    output_col_ids: List[str] = None
):
    """
    Log a decision table execution to the current audit trail.
    Only logs if auditing is active.
    """
    trail = _audit_context.get()
    if trail is None:
        return
    
    # Find which rules matched
    matched_rules = [i for i, matched in enumerate(rule_results) if matched]
    
    # Helper to evaluate expression with actual values
    def evaluate_expression(expr: str, facts_dict: Dict[str, Any]) -> str:
        """Replace variable names in expression with their actual values."""
        evaluated = expr
        # Sort by length (longest first) to avoid partial replacements
        for var_name in sorted(facts_dict.keys(), key=len, reverse=True):
            value = facts_dict[var_name]
            # Format the value appropriately
            if isinstance(value, bool):
                value_str = str(value).lower()
            elif isinstance(value, str):
                value_str = f'"{value}"'
            else:
                value_str = str(value)
            # Replace variable name with value (word boundaries to avoid partial matches)
            import re
            evaluated = re.sub(r'\b' + re.escape(var_name) + r'\b', value_str, evaluated)
        return evaluated
    
    trace = DecisionTrace(
        table_title=table_title,
        facts=facts.copy(),
        matched_rules=matched_rules,
        rule_results=rule_results.copy(),
        outputs=outputs.copy() if isinstance(outputs, list) else outputs,
        final_result=final_result.copy() if isinstance(final_result, list) else final_result,
        input_expressions=input_expressions or [],
        output_expressions=output_expressions or [],
        input_col_ids=input_col_ids or [],
        output_col_ids=output_col_ids or [],
        evaluated_outputs=[
            [evaluate_expression(expr, facts) for expr in (row if isinstance(row, list) else [row])]
            for row in (output_expressions or [])
        ] if output_expressions else []
    )
    
    trail.add_trace(trace)
