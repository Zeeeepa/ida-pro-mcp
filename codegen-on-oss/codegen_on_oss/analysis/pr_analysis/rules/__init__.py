"""
Rules for PR static analysis.

This package contains rules for detecting errors, issues, wrongly implemented features,
and parameter problems in pull requests.
"""

from codegen_on_oss.analysis.pr_analysis.rules.base_rule import (
    BaseRule,
    RuleCategory,
    RuleResult,
    RuleSeverity,
)
from codegen_on_oss.analysis.pr_analysis.rules.code_integrity_rules import (
    SyntaxErrorRule,
    MissingImportRule,
    UndefinedReferenceRule,
    DuplicateCodeRule,
    DeadCodeRule,
)
from codegen_on_oss.analysis.pr_analysis.rules.parameter_rules import (
    MissingParameterRule,
    WrongParameterTypeRule,
    UnusedParameterRule,
    InconsistentParameterRule,
)
from codegen_on_oss.analysis.pr_analysis.rules.implementation_rules import (
    DesignPatternRule,
    CodingStandardRule,
    BestPracticeRule,
    LogicFlowRule,
)

# Dictionary of all available rules
AVAILABLE_RULES = {
    # Code integrity rules
    "syntax_error": SyntaxErrorRule,
    "missing_import": MissingImportRule,
    "undefined_reference": UndefinedReferenceRule,
    "duplicate_code": DuplicateCodeRule,
    "dead_code": DeadCodeRule,
    
    # Parameter rules
    "missing_parameter": MissingParameterRule,
    "wrong_parameter_type": WrongParameterTypeRule,
    "unused_parameter": UnusedParameterRule,
    "inconsistent_parameter": InconsistentParameterRule,
    
    # Implementation rules
    "design_pattern": DesignPatternRule,
    "coding_standard": CodingStandardRule,
    "best_practice": BestPracticeRule,
    "logic_flow": LogicFlowRule,
}

# Group rules by category
RULES_BY_CATEGORY = {
    RuleCategory.CODE_INTEGRITY: [
        SyntaxErrorRule,
        MissingImportRule,
        UndefinedReferenceRule,
        DuplicateCodeRule,
        DeadCodeRule,
    ],
    RuleCategory.PARAMETER: [
        MissingParameterRule,
        WrongParameterTypeRule,
        UnusedParameterRule,
        InconsistentParameterRule,
    ],
    RuleCategory.IMPLEMENTATION: [
        DesignPatternRule,
        CodingStandardRule,
        BestPracticeRule,
        LogicFlowRule,
    ],
}


def get_all_rules(config=None):
    """
    Get all available rules.
    
    Args:
        config: Optional configuration dictionary for the rules.
        
    Returns:
        A list of rule instances.
    """
    return [rule_class(config) for rule_class in AVAILABLE_RULES.values()]


def get_rules_by_category(category, config=None):
    """
    Get rules by category.
    
    Args:
        category: The category of rules to get.
        config: Optional configuration dictionary for the rules.
        
    Returns:
        A list of rule instances.
    """
    return [rule_class(config) for rule_class in RULES_BY_CATEGORY.get(category, [])]


def get_rule_by_id(rule_id, config=None):
    """
    Get a rule by its ID.
    
    Args:
        rule_id: The ID of the rule to get.
        config: Optional configuration dictionary for the rule.
        
    Returns:
        A rule instance, or None if the rule ID is not found.
    """
    rule_class = AVAILABLE_RULES.get(rule_id)
    return rule_class(config) if rule_class else None

